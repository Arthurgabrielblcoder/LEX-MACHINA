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

OUT = AUDIT / 'C3B1_PHYSICAL_TEST_PACKAGE'      # C3B.1 (the first C3B package, which failed physically, stays frozen as evidence)
PREFIX = 'C3B1'
TARGETS_PATH = '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX'   # allowed to change ONLY in the C availability position
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
    src = (R4.RUN3 / name) if path.startswith('99_LEX_V1/20_REFERENCES/') else (R4.CARD_TARGETS if path == TARGETS_PATH else R4.CARD / name)
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
    elif name == 'CF88_TARGETS.IDX':
        r['why'] = 'C3B.1: somente a posição C (disponibilidade de 1 CORR.) recalculada a partir do REF_PAYLOAD DEVICE_READY'
    elif name == 'EXT_ARTIGOS.IDX':
        r['why'] = 'C3A.1: entradas de artigos ausentes do índice do cartão (offsets dos bytes do texto); predecessor encurtado'
    else:
        r['why'] = 'arquivo da camada CORRELATA'
    return r


def isolation(changed, base, cand):
    """Only CORRELATA-layer files change, and inside REF_* only CORRELATA content changes (resolved per target, firmware-style)."""
    out = dict(changed_paths_only_in=list(CORRELATA_LAYER_DIRS) + [TARGETS_PATH], forbidden_dirs_unchanged=list(FORBIDDEN_DIRS))
    for p in changed:
        if p == TARGETS_PATH:
            out['targets_flags'] = targets_c_only(base[p], cand[p])
        elif not p.startswith(CORRELATA_LAYER_DIRS) or p.startswith(FORBIDDEN_DIRS):
            raise SystemExit(f'ISOLATION_FAIL non-CORRELATA file {p}')
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


def targets_c_only(base, cand):
    """CF88_TARGETS.IDX: same header, same targets/kind/status/order; per target only flags[1] (C) may differ."""
    b, c = lines(base), lines(cand)
    if len(b) != len(c):
        raise SystemExit('ISOLATION_FAIL TARGETS line count')
    keys = ('ENTENDA_FLAGS_CHANGED', 'CORRELATA_FLAGS_CHANGED', 'JURIS_FLAGS_CHANGED', 'WORK_REFERENCE_FLAGS_CHANGED', 'R_FLAGS_CHANGED', 'X_FLAGS_CHANGED')
    n = dict({k: 0 for k in keys}, OTHER_FIELDS_CHANGED=0)
    for x, y in zip(b, c):
        if x == y:
            continue
        if x.startswith('#') or y.startswith('#'):
            raise SystemExit('ISOLATION_FAIL TARGETS header changed')
        fx, fy = x.split('|'), y.split('|')
        n['OTHER_FIELDS_CHANGED'] += fx[:3] != fy[:3]
        for i, k in enumerate(keys):
            n[k] += fx[3][i] != fy[3][i]
    if any(v for k, v in n.items() if k != 'CORRELATA_FLAGS_CHANGED'):
        raise SystemExit(f'ISOLATION_FAIL TARGETS non-C change {n}')
    return dict(n, verdict='CORRELATA_FLAG_CHANGES_ONLY')


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
    common = dict(schema_version=1, status='C3B1_CANDIDATE_HOST_ONLY', engine_status=R4.STATUS, physical_approved=False, card_touched=False, as_of=R4.AS_OF)
    dump(out / f'{PREFIX}_FILE_DIFF.json', dict(common, artifact=f'{PREFIX}_FILE_DIFF', files=diff, compared_unchanged=unchanged, host_only_not_on_card=host_only,
                                          isolation=iso, firmware_cache=cap))
    dump(out / f'{PREFIX}_ROLLBACK_MANIFEST.json', dict(common, artifact=f'{PREFIX}_ROLLBACK_MANIFEST', device_identity=DEVICE_ID,
                                                  files=[dict(path=p, sha256=sha(base[p]), bytes=len(base[p]), rollback_copy=f'rollback/SD/{p}',
                                                              physical_manifest_sha256=phys[p]['sha256']) for p in changed]))
    (out / f'{PREFIX}_PHYSICAL_TEST_PLAN.md').write_bytes(plan(diff, legal, cap, summary).encode('utf-8'))
    files = sorted(p for p in out.rglob('*') if p.is_file())
    dump(out / f'{PREFIX}_PACKAGE_MANIFEST.json', dict(common, artifact=f'{PREFIX}_PACKAGE_MANIFEST', files_changed=len(changed),
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
    a('# C3B.1 — plano do segundo teste físico (preparado, NÃO executado)')
    a('')
    a('**Candidato `C3B1_CANDIDATE_HOST_ONLY`.** Não é baseline nem aprovado. Nada foi copiado para nenhum cartão. Arthur executa; o Claude não toca no cartão.')
    a('')
    a('- **Origem:** corrige as duas causas raiz do primeiro teste C3B (`C3B_PHYSICAL_TEST_FAILURE_REPORT.md`).')
    a('  - Flags C antigas no `CF88_TARGETS.IDX`.')
    a('  - ID de relação compartilhado por várias linhas do `RELACOES.IDX`.')
    a('')
    a('## Arquivos do pacote (somente os que mudam)')
    a('')
    a('| Caminho no cartão | SHA256 baseline | SHA256 candidato | Bytes (baseline → candidato) |')
    a('|---|---|---|---|')
    for d in diff:
        a(f"| `{d['path']}` | `{d['baseline_sha256']}` | `{d['candidate_sha256']}` | {d['baseline_bytes']} → {d['candidate_bytes']} |")
    a('')
    a(f"- **Cache do firmware:** REL_LOOKUP {cap['used']['lookup_rows']}/64 linhas; {cap['used']['norms']}/32 normas.")
    a('- **`CF88_TARGETS.IDX`:** muda só na posição C (disponibilidade de `1 CORR.`).')
    a('  - Não mudam ENTENDA (E/B), JURIS (J), obras (W), R, X, status, IDs nem a ordem.')
    a('- **Não mudam:** Lei Seca (05_TEXT), ENTENDA (30_ENTENDA), 00_SYS, textos das normas externas, EXT_NORMAS.IDX e firmware.')
    a('- **Aviso:** o `00_SYS/LEX_DEVICE_MANIFEST.json` registra o SHA dos REF_* e do TARGETS e ficará desatualizado durante o teste.')
    a('  - O firmware não lê esse arquivo; o rollback restaura a coerência.')
    a('')
    a('## Procedimento')
    a('')
    a('1. **Backup.** Com o aparelho desligado, retire o microSD e copie o cartão inteiro para uma pasta nova no PC. Confira que a cópia tem o mesmo número de arquivos.')
    a('2. **Identificar o cartão.** Confirme que `99_LEX_V1/00_SYS/LEXV1.VER` contém:')
    a(f"   - `BUILD_ID|{DEVICE_ID['lexv1_ver_build_id']}`;")
    a(f"   - `GIT_COMMIT|{DEVICE_ID['lexv1_ver_git_commit']}`;")
    a(f"   - `REFERENCE_ENGINE|{DEVICE_ID['reference_engine']}`.")
    a('   - Confira que o SHA256 de cada arquivo da tabela no cartão é o **baseline**. Se divergir, PARE.')
    a('3. **Copiar, nesta ordem**, de `candidate/SD/` para a raiz do cartão (cópia binária):')
    for i, d in enumerate(sorted(diff, key=lambda d: (not d['path'].startswith('99_RELATIONS_V2'), d['path'].endswith('CF88_TARGETS.IDX'), d['path'])), 1):
        a(f"   {i}. `{d['path']}`")
    a('   - Os índices de relação vêm primeiro, depois os REF_* e por último o `CF88_TARGETS.IDX`.')
    a('   - Assim o `1 CORR.` só passa a ser anunciado quando as listas já estão no lugar.')
    a('4. **Conferir** cada SHA256 contra a coluna **candidato**.')
    a('5. **Ejetar**, reinserir no aparelho desligado e **ligar**. Esperado: boot normal.')
    a('6. **Executar os testes abaixo** e anotar OK/FALHA.')
    a('7. **Rollback** (qualquer falha ou dúvida): copiar de `rollback/SD/` TODOS os arquivos da tabela e conferir a coluna **baseline** (`C3B1_ROLLBACK_MANIFEST.json`).')
    a('')
    a('## Testes manuais')
    a('')
    t = [
        ('KEEP legado', 'CF art. 5º, XLIII', '`1 CORR.` aparece; a Lei 13.260/2016 abre no art. 1º'),
        ('ROUTE_FIX (reteste do teste 2)', 'CF art. 202, § 5º', 'a LC 108/2001 abre DIRETO no art. 26, e não no art. 1º'),
        ('Mesma relação nos §§ 4º e 6º', 'CF art. 202, § 4º e § 6º', 'o § 4º abre o art. 1º; o § 6º lista a LC 108 nos arts. 11 e 20'),
        ('RETARGET (reteste do teste 3)', 'CF art. 158, § 1º, I e § 1º, II', 'no inciso I aparece `1 CORR.` com a LC 63 (art. 3º); no inciso II `1 CORR.` NÃO aparece'),
        ('REPLACE', 'CF art. 161, I, II e III', 'I: LC 63 (art. 3º); II e III: LC 62 (art. 1º)'),
        ('Novo HIGH (reteste do teste 5)', 'CF art. 202, § 1º', '`1 CORR.` aparece; a LC 109/2001 abre no art. 3º (o caput continua com a LC 109 no art. 1º)'),
        ('PNE (reteste do teste 6)', 'CF art. 214 (artigo/caput) e incisos I a VI', 'no artigo, `1 CORR.` com a Lei 15.388/2026; nos incisos I a VI, `1 CORR.` NÃO aparece'),
        ('Salto LC 87', 'CF art. 150, § 7º', 'abre no "Art. 10. É assegurado ao contribuinte substituído..."'),
        ('Salto Lei 7.998 (reteste do teste 8)', 'CF art. 239, § 3º', '`1 CORR.` aparece; abre no "Art. 9º É assegurado o recebimento de abono salarial..."'),
        ('HOLD (reteste do teste 9, obrigatório)', 'CF art. 37, § 3º, III',
         '`1 CORR.` AUSENTE; pressionar `1` não abre nada nem mostra lista; ENTENDA/JURIS/REFERÊNCIAS do dispositivo iguais ao baseline'),
        ('Vacatio (reteste do teste 10)', 'CF art. 37, II; art. 131, § 2º; art. 132',
         'a Lei 14.965/2024 não aparece; no art. 37, II, `1 CORR.` AUSENTE (ENTENDA e JURIS continuam)'),
        ('Outras camadas (teste 11)', 'CF art. 5º (caput), um dispositivo com ENTENDA e Lei Seca de qualquer norma',
         'jurisprudência, obras, ENTENDA e texto iguais ao estado anterior; nenhuma tela de erro'),
    ]
    a('| # | Cobre | Onde | Esperado |')
    a('|---|---|---|---|')
    for i, (c, w, x) in enumerate(t, 1):
        a(f'| {i} | {c} | {w} | {x} |')
    a('')
    a(f"Visíveis DEVICE_READY no candidato: {summary['device_ready']['correlata_visible']} vínculos CORRELATA. Fora do pacote:")
    a('- MAIN_CORPUS, ingestão e ADCT (bloqueados por ingestão);')
    a('- supressões temporais (Lei 14.965);')
    a('- HOLD.')
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
    if a.check:
        ok = Path(a.out).exists() and tree(a.out) == trees[0]
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    t = build(a.out)
    print(json.dumps(dict(files=len(t), reproducible=t == trees[0]), indent=1))


if __name__ == '__main__':
    main()
