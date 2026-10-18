"""Host model of the multinorm jurisprudence path of the firmware prototype (multinorm.patch). It mirrors, function by function, the C code:
normaJurisAtual, carregarCacheJurisCF (validation), normaTemJurisLookup, buscarMelhorLookupJurisCF (+ the 4 fallback attempts),
adicionarLinhaJurisCF (tribunal whitelist), rotuloOrigemRelationsV2, rotuloTipoJurisprudencia (juris_types), arquivoDetalheJurisCF and the
list -> ficha -> BACK flow. `legacy=True` reproduces the J2I firmware (CF only, literal "CF88") for equivalence checks. Pure, no I/O
besides reading the package files given to it.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import juris_types as JT  # noqa: E402
from build_multinorm_prototype import catalog_table  # noqa: E402

CF_FOLDERS = ('/1- CONSTITUIÇÃO FEDERAL/', '/1-CONSTITUIÇÃO FEDERAL/')
CF_RUNTIME = '/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt'
NORMA_FIELD = 16          # LookupJurisCFCache.norma (multinorm); the J2I firmware had 8
MAX_RELACOES_ARTIGO = 32
TABLE = catalog_table()


def norma_juris_atual(path, in_adct=False, legacy=False):
    cf = path.startswith(CF_FOLDERS) or (path == CF_RUNTIME and not in_adct)
    if cf:
        return 'CF88'
    if legacy:
        return ''
    if path == CF_RUNTIME:
        return 'ADCT'
    for pasta, arquivo, nid in TABLE:
        pref = f'/{pasta}/'
        if path.startswith(pref) and (not arquivo or path[len(pref):] == arquivo):
            return nid
    return ''


class Package:
    """JUR_LOOKUP.IDX + JURISPRUDENCIA.IDX + fichas, validated like carregarCacheJurisCF (fail closed)."""

    def __init__(self, lookup_bytes, records_bytes, fichas, norma_field=NORMA_FIELD):
        self.records = records_bytes
        self.fichas = set(fichas)
        self.lookups = []
        for line in lookup_bytes.decode('utf-8').split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            f = line.split('|')
            norma, art, off, q = f[0], f[1], int(f[5]), int(f[6])
            if not norma or not art or q <= 0 or q > 255:
                raise ValueError('linha de lookup corrompida')
            self.lookups.append((norma[:norma_field - 1], art, f[2], f[3], f[4], off, q))
        total = 0
        for *_, off, q in self.lookups:
            if off >= len(records_bytes) or (off > 0 and records_bytes[off - 1:off] != b'\n'):
                raise ValueError('offset fora do indice ou desalinhado')
            total += q
        if total != records_bytes.count(b'\n') - 1:
            raise ValueError('quantidade total inconsistente')

    def has_norm(self, norma):
        return bool(norma) and any(l[0] == norma for l in self.lookups)

    def exact(self, norma, art, par, inc, ali):
        for n, a, p, i, al, off, q in self.lookups:
            if (n, a, p, i, al) == (norma, art, par, inc, ali):
                return off, q
        return None

    def rows(self, off, q):
        out, cur = [], off
        for _ in range(q):
            end = self.records.index(b'\n', cur)
            out.append(self.records[cur:end].decode('utf-8').replace('\r', ''))
            cur = end + 1
        return out


def rotulo_origem(norma, art, par, inc, ali):
    r = ('CF ART. ' if norma == 'CF88' else 'ART. ') + art
    if par:
        r += ', PAR. UNICO' if par == 'unico' else f', § {par}º'
    if inc:
        r += ', ' + inc
    if ali:
        r += ', ' + ali + ')'
    return r


def relation(line, rotulo):
    f = line.split('|')
    rid, tipo, trib, num, status, ident = f[0], f[1], f[2], f[3], f[4], f[6]
    if not JT.id_accepted(rid, trib) or not tipo or not ident:
        return None
    arquivo = ident.replace(':', '_').replace('/', '_') + '.TXT'
    return dict(referencia=rotulo, tribunal=trib, tipo=tipo, numero=num, status=status, label=JT.label(tipo, trib, num),
                title=JT.title(tipo, trib, num), arquivo=arquivo, caminho='/99_JURISPRUDENCIA_V2/03_CONTEUDO/' + arquivo)


def carregar(pkg, path, art, par='', inc='', ali='', in_adct=False, legacy=False):
    """carregarRelacoesDoArtigo (juris part). Returns dict(norma, branch, relations)."""
    norma = norma_juris_atual(path, in_adct, legacy)
    if norma == 'CF88':
        branch = 'CF'
    elif norma and not legacy and pkg.has_norm(norma):
        branch = 'MULTINORMA'
    else:
        return dict(norma=norma, branch='PREVIOUS_FLOW', relations=[])
    tries = ([(par, inc, ali)] if ali else []) + ([(par, inc, '')] if inc else []) + ([(par, '', '')] if par else []) + [('', '', '')]
    for p, i, a in tries:
        hit = pkg.exact(norma, art, p, i, a)
        if hit:
            rot = rotulo_origem(norma, art, p, i, a)
            rels = [r for r in (relation(l, rot) for l in pkg.rows(*hit)) if r][:MAX_RELACOES_ARTIGO]
            return dict(norma=norma, branch=branch, used=(p, i, a), relations=rels)
    return dict(norma=norma, branch=branch, relations=[])


def open_and_back(pkg, state, index):
    """Open item `index` of the list (ficha must exist), then BACK: the list is re-resolved from the saved origin and must be identical."""
    r = state['relations'][index]
    if r['arquivo'] not in pkg.fichas or r['label'].startswith('OUTRO'):
        return dict(opened=False)
    return dict(opened=True, title=r['title'], ficha=r['caminho'])
