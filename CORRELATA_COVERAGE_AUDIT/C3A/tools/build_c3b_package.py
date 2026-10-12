"""C3B PREP — physical test package of the RUN4_CANDIDATE_HOST_ONLY device-ready view. PREPARES ONLY: never touches a card.

Derives (no file names assumed): every device_ready output that has a counterpart on the physical card (C0 pin physical manifest) is
compared with the physical baseline bytes; ONLY files whose bytes differ enter the package. Baseline bytes come from the repository
(RUN3 export = card REF_*; frozen card relation indices) and are checked against the physical manifest sha256.

Writes CORRELATA_COVERAGE_AUDIT/C3B_PHYSICAL_TEST_PACKAGE/:
  candidate/SD/<card path>     files to copy to the test card          rollback/SD/<card path>   baseline bytes for restoration
  C3B_FILE_DIFF.json  C3B_ROLLBACK_MANIFEST.json  C3B_PACKAGE_MANIFEST.json  C3B_PHYSICAL_TEST_PLAN.md
Fails (SystemExit) when isolation is broken: a non-CORRELATA layer changing, firmware changing, or the firmware cache limits exceeded.
Usage: python build_c3b_package.py [--out DIR] [--check]
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

C3A = Path(__file__).resolve().parents[1]
AUDIT = C3A.parent
ROOT = AUDIT.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_export_run4_candidate as R4  # noqa: E402
import correlata_overlay as O  # noqa: E402

OUT = AUDIT / 'C3B_PHYSICAL_TEST_PACKAGE'
BASELINE_HEAD = '9108d72812802de941e54b7e4e3ec556b7abd019'
CORRELATA_LAYER_DIRS = ('99_RELATIONS_V2/05_INDICES_ESP32_V2/', '99_LEX_V1/20_REFERENCES/')
FORBIDDEN_DIRS = ('99_LEX_V1/05_TEXT/', '99_LEX_V1/10_TARGETS/', '99_LEX_V1/30_ENTENDA/', '99_LEX_V1/00_SYS/', '99_RELATIONS_V2/03_NORMAS_EXTERNAS/')
DEVICE_ID = dict(lexv1_ver_build_id='de963699728cb66e', lexv1_ver_git_commit='fa9719a6bd335275252473a5f154e4e11f5532f4',
                 reference_engine='cf-reference-engine-run3')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def physical():
    return R4.load(R4.PIN)['physical_sd']['files']


def baseline_bytes(path):
    """Baseline bytes of a card file from the repository, verified against the physical manifest (fail closed)."""
    name = path.split('/')[-1]
    src = (R4.RUN3 / name) if path.startswith('99_LEX_V1/20_REFERENCES/') else (R4.CARD / name)
    b = src.read_bytes().replace(b'\r\n', b'\n')
    if sha(b) != physical()[path]['sha256'] or len(b) != physical()[path]['bytes']:
        raise SystemExit(f'BASELINE_NOT_PHYSICAL {path}')
    return b


def card_path(name, phys):
    hits = [k for k in phys if k.split('/')[-1] == name]
    if len(hits) > 1:
        raise SystemExit(f'AMBIGUOUS_CARD_PATH {name}')
    return hits[0] if hits else None


def lines(b):
    return [l for l in b.decode('utf-8').split('\n') if l]


def payload_split(b):
    ls = [l for l in lines(b) if not l.startswith('#')]
    return [l for l in ls if l.split('|')[1] != 'CORRELATA'], [l for l in ls if l.split('|')[1] == 'CORRELATA']


def resolve_all(lookup, payload):
    """Firmware-style resolution of every target: target -> payload lines (offset/count of REF_LOOKUP into REF_PAYLOAD)."""
    out = {}
    for l in lines(lookup):
        if l.startswith('#'):
            continue
        t, off, n = l.split('|')
        out[t] = payload[int(off):].split(b'\n')[:int(n)]
    return out


def reason(path, base, cand):
    bl, cl = set(lines(base)), set(lines(cand))
    r = dict(lines_removed=len(bl - cl), lines_added=len(cl - bl))
    name = path.split('/')[-1]
    if name == 'REF_PAYLOAD.IDX':
        r['why'] = 'linhas CORRELATA: exclusões/supressões do legado saem, adições DEVICE_READY entram; demais tipos idênticos'
    elif name == 'REF_LOOKUP.IDX':
        r['why'] = 'offsets/contagens recalculados porque REF_PAYLOAD mudou (só alvos com CORRELATA mudam de conteúdo)'
    elif name == 'RELACOES.IDX':
        r['why'] = 'linhas de relação: removidas (exclusões/supressões), adicionadas (adições), rota corrigida (ROUTE_FIX)'
    elif name == 'REL_LOOKUP.IDX':
        r['why'] = 'offsets por origem recalculados porque RELACOES.IDX mudou'
    elif name == 'EXT_ARTIGOS.IDX':
        r['why'] = 'C3A.1: entradas de artigos ausentes do índice do cartão (offsets dos bytes do texto); predecessor encurtado'
    else:
        r['why'] = 'arquivo da camada CORRELATA'
    return r


def isolation(changed, base, cand):
    """Only CORRELATA-layer files change, and inside REF_* only CORRELATA content changes (resolved per target, firmware-style)."""
    for p in changed:
        if not p.startswith(CORRELATA_LAYER_DIRS) or p.startswith(FORBIDDEN_DIRS):
            raise SystemExit(f'ISOLATION_FAIL non-CORRELATA file {p}')
    out = dict(changed_paths_only_in=list(CORRELATA_LAYER_DIRS), forbidden_dirs_unchanged=list(FORBIDDEN_DIRS))
    pp, lp = '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX', '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX'
    bp, cp = base.get(pp), cand.get(pp)
    if bp is not None:
        bn, bc = payload_split(bp)
        cn, cc = payload_split(cp)
        if bn != cn:
            raise SystemExit('ISOLATION_FAIL non-CORRELATA payload lines changed')
        rb, rc = resolve_all(base[lp], bp), resolve_all(cand[lp], cp)
        for t in set(rb) | set(rc):
            a = [l for l in rb.get(t, []) if l.split(b'|')[1] != b'CORRELATA']
            b = [l for l in rc.get(t, []) if l.split(b'|')[1] != b'CORRELATA']
            if a != b:
                raise SystemExit(f'ISOLATION_FAIL non-CORRELATA resolution changed at {t}')
        out.update(non_correlata_payload_lines=len(bn), non_correlata_identical=True, correlata_lines_before=len(bc), correlata_lines_after=len(cc),
                   targets_resolved_identically_outside_correlata=len(set(rb) | set(rc)))
    fw = subprocess.run(['git', 'diff', '--name-only', BASELINE_HEAD, '--', 'firmware'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    if fw.strip():
        raise SystemExit('ISOLATION_FAIL firmware changed')
    out['firmware_unchanged_vs'] = BASELINE_HEAD
    return out


def caps(cand):
    rel = [l.split('|') for l in lines(cand['99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX']) if not l.startswith('#')]
    look = [l for l in lines(cand['99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX']) if not l.startswith('#')]
    used = dict(lookup_rows=len(look), norms=len({r[6] for r in rel}))
    for k, lim in O.FIRMWARE_CACHE.items():
        if used[k] > lim:
            raise SystemExit(f'FIRMWARE_CACHE_EXCEEDED {k}')
    return dict(used=used, limit=O.FIRMWARE_CACHE)


def build(out):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    phys = physical()
    with tempfile.TemporaryDirectory() as t:
        summary = R4.build(t)
        dev = Path(t) / 'device_ready'
        mapped, host_only = {}, []
        for f in sorted(dev.iterdir()):
            p = card_path(f.name, phys)
            (mapped.__setitem__(p, f.read_bytes()) if p else host_only.append(f.name))
        legal = R4.load(Path(t) / 'legal_view/CF88_CORRELATA_LEGAL_VIEW.json')
    base = {p: baseline_bytes(p) for p in mapped}
    changed = sorted(p for p in mapped if sha(mapped[p]) != sha(base[p]))
    iso = isolation(changed, base, mapped)
    cap = caps(mapped)
    diff = []
    for p in changed:
        (out / 'candidate/SD' / p).parent.mkdir(parents=True, exist_ok=True)
        (out / 'candidate/SD' / p).write_bytes(mapped[p])
        (out / 'rollback/SD' / p).parent.mkdir(parents=True, exist_ok=True)
        (out / 'rollback/SD' / p).write_bytes(base[p])
        diff.append(dict(path=p, baseline_sha256=sha(base[p]), candidate_sha256=sha(mapped[p]), baseline_bytes=len(base[p]),
                         candidate_bytes=len(mapped[p]), reason=reason(p, base[p], mapped[p])))
    unchanged = sorted(p for p in mapped if p not in changed)
    common = dict(schema_version=1, status=R4.STATUS, physical_approved=False, card_touched=False, as_of=R4.AS_OF)
    dump(out / 'C3B_FILE_DIFF.json', dict(common, artifact='C3B_FILE_DIFF', files=diff, compared_unchanged=unchanged, host_only_not_on_card=host_only,
                                          isolation=iso, firmware_cache=cap))
    dump(out / 'C3B_ROLLBACK_MANIFEST.json', dict(common, artifact='C3B_ROLLBACK_MANIFEST', device_identity=DEVICE_ID,
                                                  files=[dict(path=p, sha256=sha(base[p]), bytes=len(base[p]), rollback_copy=f'rollback/SD/{p}',
                                                              physical_manifest_sha256=phys[p]['sha256']) for p in changed]))
    (out / 'C3B_PHYSICAL_TEST_PLAN.md').write_bytes(plan(diff, legal, cap, summary).encode('utf-8'))
    files = sorted(p for p in out.rglob('*') if p.is_file())
    dump(out / 'C3B_PACKAGE_MANIFEST.json', dict(common, artifact='C3B_PACKAGE_MANIFEST', files_changed=len(changed),
                                                 run4_sha256sums=sha((Path(R4.OUT) / 'SHA256SUMS.txt').read_bytes().replace(b'\r\n', b'\n')),
                                                 package={p.relative_to(out).as_posix(): sha(p.read_bytes()) for p in files}))
    return tree(out)


def tree(d):
    return {p.relative_to(d).as_posix(): sha(p.read_bytes()) for p in sorted(Path(d).rglob('*')) if p.is_file()}


def dump(p, o):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))


def find(legal, **kw):
    return next(e for e in legal['entries'] if all(e.get(k) == v for k, v in kw.items()))


def plan(diff, legal, cap, summary):
    L = []
    a = L.append
    a('# C3B — plano de teste físico (preparado, NÃO executado)')
    a('')
    a('**Candidato `RUN4_CANDIDATE_HOST_ONLY`.** Não é baseline nem aprovado. Nada foi copiado para nenhum cartão. Arthur executa; o Claude não toca no cartão.')
    a('')
    a('## Arquivos do pacote (somente os que mudam)')
    a('')
    a('| Caminho no cartão | SHA256 baseline | SHA256 candidato | Bytes (baseline → candidato) |')
    a('|---|---|---|---|')
    for d in diff:
        a(f"| `{d['path']}` | `{d['baseline_sha256']}` | `{d['candidate_sha256']}` | {d['baseline_bytes']} → {d['candidate_bytes']} |")
    a('')
    a(f"- **Cache do firmware:** REL_LOOKUP {cap['used']['lookup_rows']}/64 linhas; {cap['used']['norms']}/32 normas.")
    a('- **Não mudam:** Lei Seca (05_TEXT), TARGETS, ENTENDA, 00_SYS, textos das normas externas, EXT_NORMAS.IDX e firmware.')
    a('- **Aviso:** o `00_SYS/LEX_DEVICE_MANIFEST.json` do cartão registra o SHA dos REF_* e ficará desatualizado durante o teste.')
    a('  - O firmware não lê esse arquivo (verificado no código-fonte); o rollback restaura a coerência.')
    a('')
    a('## Procedimento')
    a('')
    a('1. **Backup.** Com o aparelho desligado, retire o microSD e copie o cartão inteiro para uma pasta nova no PC (ex.: `D:\\BACKUP_C3B_<data>`). Confira que a cópia tem o mesmo número de arquivos.')
    a('2. **Identificar o cartão.** Confirme que `99_LEX_V1/00_SYS/LEXV1.VER` contém:')
    a(f"   - `BUILD_ID|{DEVICE_ID['lexv1_ver_build_id']}`;")
    a(f"   - `GIT_COMMIT|{DEVICE_ID['lexv1_ver_git_commit']}`;")
    a(f"   - `REFERENCE_ENGINE|{DEVICE_ID['reference_engine']}`.")
    a('   - Confira também que o SHA256 de cada arquivo da tabela acima no cartão é igual ao **baseline**.')
    a('   - Se qualquer um divergir, PARE: não é o cartão esperado.')
    a('3. **Copiar, nesta ordem**, de `candidate/SD/` para a raiz do cartão, substituindo:')
    for i, d in enumerate(sorted(diff, key=lambda d: (not d['path'].startswith('99_RELATIONS_V2'), d['path'])), 1):
        a(f"   {i}. `{d['path']}`")
    a('   - Os índices de relação vêm antes dos REF_*: se a cópia for interrompida, os REF_* antigos continuam coerentes com os vínculos antigos.')
    a('4. **Conferir** o SHA256 de cada arquivo copiado contra a coluna **candidato**. Se divergir, refaça a cópia ou faça o rollback.')
    a('5. **Ejetar** o cartão com segurança e reinseri-lo no aparelho desligado.')
    a('6. **Ligar** o aparelho. Esperado: boot normal, sem erro de diagnóstico.')
    a('7. **Executar os testes abaixo** e anotar OK/FALHA em cada um.')
    a('8. **Rollback (se qualquer teste falhar ou houver dúvida).**')
    a('   - Desligue o aparelho, retire o cartão e copie de `rollback/SD/` os mesmos arquivos.')
    a('   - Confira cada SHA256 contra a coluna **baseline** (`C3B_ROLLBACK_MANIFEST.json`) e repita os testes 10 e 11 no estado antigo.')
    a('   - O backup completo do passo 1 é a última garantia.')
    a('')
    a('## Testes manuais (11)')
    a('')
    t = []
    e = find(legal, kind='LEGACY', target_id='CF88:ART.5:INC.XLIII')
    t.append(('KEEP legado', 'CF art. 5º, XLIII → botão 1 (correlatas)', f"{e['destination_norm_id']} aparece e abre o art. 1º"))
    e = find(legal, kind='LEGACY', target_id='CF88:ART.202:PAR.5')
    t.append(('ROUTE_FIX', 'CF art. 202, § 5º → correlata LC 108/2001', 'abre direto o art. 26 (antes abria o art. 1º)'))
    t.append(('RETARGET', 'CF art. 158, § 1º, I e depois § 1º, II', 'LC 63/1990 aparece no inciso I (abre o art. 3º) e NÃO aparece mais no inciso II'))
    t.append(('REPLACE resolvível', 'CF art. 161, I', 'aparece a LC 63/1990 (abre o art. 3º); a LC 62/1989 não aparece mais no inciso I (continua nos incisos II e III)'))
    t.append(('Novo HIGH', 'CF art. 202, § 1º', 'aparece a LC 109/2001 e abre o art. 3º'))
    t.append(('PNE no caput', 'CF art. 214 (caput) e incisos I a VI', 'Lei 15.388/2026 aparece uma única vez, no artigo/caput; nenhum inciso a mostra'))
    t.append(('Salto LC 87 art. 10', 'CF art. 150, § 7º → LC 87/1996', 'abre exatamente no "Art. 10. É assegurado ao contribuinte substituído..."'))
    t.append(('Salto Lei 7.998 art. 9º', 'CF art. 239, § 3º → Lei 7.998/1990', 'abre exatamente no "Art. 9º É assegurado o recebimento de abono salarial..."'))
    t.append(('HOLD suprimido', 'CF art. 37, § 3º, III', 'nenhuma correlata (a Lei 13.460/2017 não aparece); no § 3º, I ela continua'))
    t.append(('Vacatio suprimida', 'CF art. 37, II; art. 131, § 2º; art. 132', 'a Lei 14.965/2024 não aparece em nenhum dos três'))
    t.append(('Outras camadas', 'CF art. 5º (caput) e um dispositivo com ENTENDA; abrir Lei Seca de qualquer norma',
              'jurisprudência, obras, ENTENDA e texto iguais ao estado anterior; nenhuma tela nova de erro'))
    a('| # | Cobre | Onde | Esperado |')
    a('|---|---|---|---|')
    for i, (c, w, x) in enumerate(t, 1):
        a(f'| {i} | {c} | {w} | {x} |')
    a('')
    a(f"Visíveis DEVICE_READY no candidato: {summary['device_ready']['correlata_visible']} vínculos CORRELATA. Fora do pacote:")
    a('- 21 MAIN_CORPUS;')
    a('- 55 que dependem de ingestão;')
    a('- 2 ADCT (bloqueados por ingestão);')
    a('- 3 supressões temporais (Lei 14.965);')
    a('- 1 HOLD.')
    a('')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(OUT))
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    trees = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as t:
            trees.append(build(Path(t) / 'pkg'))
    if trees[0] != trees[1]:
        raise SystemExit('C3B_PACKAGE_NOT_REPRODUCIBLE')
    report = closure_report(trees[0]).encode('utf-8')
    if a.check:
        ok = Path(a.out).exists() and tree(a.out) == trees[0] and CLOSURE.read_bytes().replace(b'\r\n', b'\n') == report
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    t = build(a.out)
    CLOSURE.write_bytes(report)
    print(json.dumps(dict(files=len(t), reproducible=t == trees[0]), indent=1))


CLOSURE = C3A / 'C3A1_CLOSURE_REPORT.md'


def closure_report(pkg_tree):
    s = R4.load(R4.OUT / 'RUN4_CANDIDATE_SUMMARY.json')
    d = s['device_ready']
    audit = R4.load(AUDIT / 'C3A/inputs/ext_index_audit.json')
    reg = R4.load(R4.REGISTER)['records']
    cls = [r for r in reg if r.get('relation_type_basis')]
    diff = [k for k in pkg_tree if k.startswith('candidate/')]
    L = []
    a = L.append
    a('# C3A.1 — fechamento editorial da C3A e preparação do C3B')
    a('')
    a('**`RUN4_CANDIDATE_HOST_ONLY`.** Nenhum cartão foi tocado, nenhum firmware foi alterado e nada foi promovido a baseline.')
    a('')
    a('## Tipos de relação (decisão humana C3A.1)')
    a('')
    a('| Target | Norma | Tipo | Revalidar em |')
    a('|---|---|---|---|')
    for r in cls:
        a(f"| `{r['target_id']}` | {r['destination_norm_key']} | {r['relation_type']} | {r['revalidate_on'] or '—'} |")
    a('')
    a(f"- **Não classificados restantes:** {d['unclassified_relation_types']}. O marcador `{O.UNCLASSIFIED_RELATION_TYPE}` agora é rejeitado pelo motor.")
    a('- **PNE:** continuam um único vínculo no caput do art. 214 e `NEXT_STEP = ANNEX_ROUTE_SUPPORT`.')
    a('')
    a('## Índice de artigos (EXT_ARTIGOS candidato)')
    a('')
    a(f"- **Auditoria restrita** aos artigos que os vínculos DEVICE_READY abrem ({len(audit['articles'])} artigos): {audit['counts']}.")
    a('- **Reparos** (offsets dos bytes reais do texto congelado; UTF-8 sem BOM, LF; o OFFSET aponta o início de "Art."):')
    for r in d['ext_artigos_index_repairs']:
        a(f"  - {r['norm_id']} art. {r['article']}: offset {r['offset']}, tamanho {r['size']}.")
        a(f"    - O predecessor (art. {r['predecessor']}) foi encurtado de {r['predecessor_size_before']} para {r['predecessor_size_after']}, "
          "para manter as faixas contíguas.")
    a('  - O firmware só usa o OFFSET (busca linear em `buscarOffsetArtigoExternoV2`).')
    a(f"- **Resultado:** lacunas restantes nos vínculos DEVICE_READY: {d['device_article_gaps']}.")
    a(f"  - Resolução por vínculo: {d['device_article_resolution']}.")
    a('  - O único `OPEN_NORM_START_BY_DECISION` é um vínculo legado KEEP cuja rota sempre abriu a norma inteira.')
    a('- **Fallback:** `OPEN_NORM_START` continua no motor para casos sem entrada no índice.')
    a('')
    a('## RUN4 regenerado')
    a('')
    a(f"- **Visíveis DEVICE_READY:** {d['correlata_visible']}, sem mudança: a correção do índice não altera a contagem.")
    a(f"- **Cache do firmware:** REL_LOOKUP {d['firmware_cache']['used']['lookup_rows']}/64 linhas; {d['firmware_cache']['used']['norms']}/32 normas.")
    a('')
    a('## Pacote C3B')
    a('')
    a(f"- `C3B_PHYSICAL_TEST_PACKAGE/` tem {len(diff)} arquivos alterados, com cópia de rollback de cada um.")
    a('- O teste foi preparado e NÃO executado; o plano está em `C3B_PHYSICAL_TEST_PLAN.md`.')
    a('- **`.gitattributes`:** os textos congelados e o pacote ficaram como `-text`, para que o checkout no Windows (`core.autocrlf=true`) não altere bytes.')
    a('')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    main()
