"""J2E — isolation audit of the BATCH02 candidates (A: current firmware; B: + HC) against the J2C physical card. Read-only, deterministic.

Firmware mirror (from build_j2b_isolation_audit): query keys -> REF_PAYLOAD -> key in JURISPRUDENCIA.IDX -> label -> ficha, PSRAM cache rules.
The label is computed for two firmwares: CURRENT (rotuloTipoJurisprudencia today: "hc" -> "OUTRO <n>") and HC_CANDIDATE (adds "HC <n>").
Writes JURISPRUDENCE_AUDIT/J2_HIGH_BACKLOG/J2E_ISOLATION_AUDIT.json.   Usage: python build_j2e_isolation_audit.py [--check]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_j2b_isolation_audit as A  # noqa: E402

CARD_PKG = HERE / 'J2B_1_CANDIDATE_HOST_ONLY/candidate/SD'
PHYSICAL = HERE / 'J2C_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
PKG_ROOT = HERE / 'J2_HIGH_BACKLOG/J2E_BATCH02_CANDIDATE_HOST_ONLY'
ADDITIONS = HERE.parent / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2E.json'
OUT = HERE / 'J2_HIGH_BACKLOG/J2E_ISOLATION_AUDIT.json'
VARIANTS = {'A': ('VARIANT_A_CURRENT_FIRMWARE', ('A',)), 'B': ('VARIANT_B_REQUIRES_HC_FIRMWARE', ('A', 'B'))}
PAYLOAD, TARGETS, LOOKUP_REF = '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX', '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX', '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX'
SIM = ('ADCT:ART.101:PAR.5', 'ADCT:ART.107-A', 'CF88:ART.100:PAR.11', 'CF88:ART.100:PAR.9', 'CF88:ART.23:INC.II', 'CF88:ART.22:INC.I',
       'CF88:ART.85:PAR.UNICO', 'CF88:ART.53', 'CF88:ART.53:PAR.1', 'CF88:ART.29-A:PAR.2', 'CF88:ART.36:INC.I')
REGRESSION = ('CF88:ART.100:PAR.5', 'CF88:ART.40', 'CF88:ART.16', 'CF88:ART.37:INC.XI', 'CF88:ART.100', 'CF88:ART.100:PAR.12',
              'CF88:ART.166:PAR.9', 'CF88:ART.166:PAR.11', 'CF88:ART.166-A')
FW_LABEL = dict(CURRENT=dict(A.LABEL), HC_CANDIDATE=dict(A.LABEL, hc='HC'))


def label(row_type, numero, fw):
    return f"{FW_LABEL[fw].get(row_type.lower(), 'OUTRO')} {numero}"


def view(t, rows, idx, files, fw):
    out = []
    for x in A.resolve(t, rows, idx, files, set()):
        if x['resolved']:
            line = next(l for l in idx.decode('utf-8').split('\n') if l.split('|')[0] and l.split('|')[6] and l.startswith(
                next(r[4] for r in rows if r[5] == x['source'] and r[0] in A.query_keys(t)).split(':', 1)[1].rsplit('@', 1)[0] + '|'))
            f = line.split('|')
            x = dict(x, list_label=label(f[1], f[3], fw))
        out.append(x)
    return out


def build():
    card = {k: v['sha256'] for k, v in json.loads(PHYSICAL.read_text(encoding='utf-8'))['entries'].items()}
    add = json.loads(ADDITIONS.read_text(encoding='utf-8'))
    base_rows = A.rows((CARD_PKG / PAYLOAD).read_bytes())
    base_idx = (CARD_PKG / A.IDX).read_bytes()
    tb = {r[0]: r for r in A.rows((CARD_PKG / TARGETS).read_bytes())}
    jv = lambda rs: [r for r in rs if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']  # noqa: E731
    by = lambda rs, t: {'|'.join(r) for r in rs if r[1] == t}  # noqa: E731
    res = {}
    for v, (pkgname, inc) in VARIANTS.items():
        pkg = PKG_ROOT / pkgname
        m = json.loads((pkg / 'J2E_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
        rd = lambda rel: (pkg / 'candidate/SD' / rel).read_bytes()  # noqa: E731
        rows, idx, lk = A.rows(rd(PAYLOAD)), rd(A.IDX), rd(A.LOOKUP)
        tc = {r[0]: r for r in A.rows(rd(TARGETS))}
        flags = {k: sorted(t for t in tb if tb[t][3][i] != tc[t][3][i]) for k, i in A.POS.items()}
        sb, sc = {'|'.join(r) for r in base_rows}, {'|'.join(r) for r in rows}
        expected = {f"JURISPRUDENCE:{r['source_reference_id']}@{r['target_id']}" for r in add['records'] if r['variant'] in inc}
        files = set(card) | {a['path'].lstrip('/') for a in m['file_additions']}
        cache_ok, n_rec, n_sum = A.cache_rules(idx, lk)
        lookup_targets = {r[0] for r in A.rows(rd(LOOKUP_REF))}
        sim = {fw: {t: view(t, rows, idx, files, fw) for t in SIM} for fw in FW_LABEL}
        reg_now = {t: A.resolve(t, rows, idx, files, set()) for t in REGRESSION}
        reg_card = {t: A.resolve(t, base_rows, base_idx, set(card), set()) for t in REGRESSION}
        lbl = lambda fw, t: [x.get('list_label') for x in sim[fw][t]]  # noqa: E731
        verdict = dict(
            INSTALLED_261_BYTE_IDENTICAL=all('|'.join(r) in sc for r in jv(base_rows)) and len(jv(base_rows)) == 261,
            ROWS_REMOVED=len(sb - sc), ROWS_ADDED=len(sc - sb),
            ONLY_APPROVED_RELATIONS_ADDED={r.split('|')[4] for r in sc - sb} == expected,
            JURIS_RELATIONS=len(jv(rows)), JURIS_TARGETS=len({r[0] for r in jv(rows)}),
            CORRELATA_RELATION_SET_CHANGED=len(by(base_rows, 'CORRELATA') ^ by(rows, 'CORRELATA')),
            WORK_REFERENCE_SET_CHANGED=len(by(base_rows, 'WORK_REFERENCE') ^ by(rows, 'WORK_REFERENCE')),
            **{f'{k}_FLAGS_CHANGED': len(x) for k, x in flags.items()}, NEW_TARGETS_WITH_J=flags['J'],
            J_FLAG_EQUALS_VISIBLE_JURIS={t for t, r in tc.items() if r[3][A.POS['J']] == 'J'} == {r[0] for r in jv(rows)},
            R_FLAG_KNOWN_DIVERGENCE=sum(1 for t, r in tc.items() if (r[3][A.POS['R']] == 'R') != (t in lookup_targets)),
            LEGACY_PREFIX_IDENTICAL=idx.startswith(base_idx) and lk.startswith((CARD_PKG / A.LOOKUP).read_bytes()),
            FIRMWARE_CACHE_RULES_HOLD=cache_ok, LEGACY_RECORDS=n_rec, LOOKUP_QUANTITY_SUM=n_sum,
            ALL_SIMULATED_RESOLVE_WITH_FICHA=all(x['resolved'] and x['ficha_present'] for xs in sim['CURRENT'].values() for x in xs),
            ADCT_107A_LABEL_IS_ADI_7064_ONLY=lbl('CURRENT', 'ADCT:ART.107-A') == ['ADI 7064'],
            ADCT_101_PAR5_LABEL_IS_JOINT=lbl('CURRENT', 'ADCT:ART.101:PAR.5') == ['ADI 7047/7064'],
            PAR11_LABEL_IS_JOINT=lbl('CURRENT', 'CF88:ART.100:PAR.11') == ['ADI 7047/7064'],
            SV46_SAME_FICHA_TWO_TARGETS=[x['ficha'] for x in sim['CURRENT']['CF88:ART.85:PAR.UNICO']] ==
            [x['ficha'] for x in sim['CURRENT']['CF88:ART.22:INC.I'] if x['source'] == 'STF:SV:46'] == ['99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_SV_46.TXT'],
            REJECTED_NOT_LINKED=not sim['CURRENT']['CF88:ART.36:INC.I'] and 'STF:SV:46' not in [x['source'] for x in sim['CURRENT']['CF88:ART.29-A:PAR.2']],
            HC_LABEL_CURRENT_FIRMWARE=lbl('CURRENT', 'CF88:ART.53:PAR.1'), HC_LABEL_HC_FIRMWARE=lbl('HC_CANDIDATE', 'CF88:ART.53:PAR.1'),
            REGRESSION_TARGETS_UNCHANGED=reg_now == reg_card,
            FILES_CHANGED=len(m['changed_vs_physical']), FILES_ADDED=len(m['added_vs_physical']), NEW_FICHAS=[a['path'] for a in m['file_additions']])
        res[v] = dict(package=pkgname, build_id=m['build_id'], verdict=verdict,
                      device_simulation={fw: {t: [x.get('list_label') for x in xs] for t, xs in s.items()} for fw, s in sim.items()})
    return dict(artifact='J2E_ISOLATION_AUDIT', base='J2C card (261/160)', variants=res)


if __name__ == '__main__':
    b = (json.dumps(build(), ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    d = json.loads(b)
    for v, r in d['variants'].items():
        print(v, json.dumps(r['verdict'], ensure_ascii=False))
        print('  ', json.dumps(r['device_simulation']['CURRENT'], ensure_ascii=False))
