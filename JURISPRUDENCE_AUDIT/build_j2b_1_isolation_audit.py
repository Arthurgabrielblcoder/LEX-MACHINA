"""J2B.1 — isolation audit of the J2B_PREDEPLOY_TEMPORAL_FIX: J2B package (RUN8) × J2B.1 package (RUN9), and installed card × J2B.1.
Read-only, deterministic. Reuses the firmware mirror of build_j2b_isolation_audit (query keys, legacy key resolution, PSRAM cache rules).
Writes JURISPRUDENCE_AUDIT/J2B_1_ISOLATION_AUDIT.json.   Usage: python build_j2b_1_isolation_audit.py [--check]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_j2b_isolation_audit as A  # noqa: E402

J2B = HERE / 'J2B_CANDIDATE_HOST_ONLY'
J2B1 = HERE / 'J2B_1_CANDIDATE_HOST_ONLY'
INSTALLED = HERE / 'J1_4_CANDIDATE_HOST_ONLY/candidate/SD'
OUT = HERE / 'J2B_1_ISOLATION_AUDIT.json'
OLD = 'JURISPRUDENCE:STF:RG:558:CF88:100:-:-:-@CF88:ART.100:PAR.9'
NEW = 'JURISPRUDENCE:STF:RG:558:CF88:100:-:-:-@CF88:ART.100'
FICHA_558 = '99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_558.TXT'
PAYLOAD = '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'
TARGETS = '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX'


def rd(pkg, rel):
    return (pkg / 'candidate/SD' / rel).read_bytes()


def build():
    card = {k: v['sha256'] for k, v in json.loads(A.CARD.read_text(encoding='utf-8'))['entries'].items()}
    m1 = json.loads((J2B / 'J2B_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
    m2 = json.loads((J2B1 / 'J2B_1_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
    r8, r9 = A.rows(rd(J2B, PAYLOAD)), A.rows(rd(J2B1, PAYLOAD))
    ri = A.rows((INSTALLED / PAYLOAD).read_bytes())
    s8, s9, si = ({'|'.join(r) for r in x} for x in (r8, r9, ri))
    removed, added = sorted(s8 - s9), sorted(s9 - s8)
    t8, t9 = ({r[0]: r for r in A.rows(rd(p, TARGETS))} for p in (J2B, J2B1))
    flags = {k: sorted(t for t in t8 if t8[t][3][i] != t9[t][3][i]) for k, i in A.POS.items()}
    by = lambda rs, t: {'|'.join(r) for r in rs if r[1] == t}  # noqa: E731
    jv = lambda rs: [r for r in rs if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']  # noqa: E731
    idx, lk = rd(J2B1, A.IDX), rd(J2B1, A.LOOKUP)
    cache_ok, n_rec, n_sum = A.cache_rules(idx, lk)
    new_files = {a['path'].lstrip('/') for a in m2['file_additions']}
    sim = {t: A.resolve(t, r9, idx, card, new_files) for t in ('CF88:ART.100', 'CF88:ART.100:PAR.9', 'CF88:ART.100:PAR.10', 'CF88:ART.100:PAR.12',
                                                            'CF88:ART.166:PAR.9', 'CF88:ART.166:PAR.11', 'CF88:ART.166-A')}
    sim8 = {t: A.resolve(t, r8, rd(J2B, A.IDX), card, new_files) for t in sim}
    regress = {t: A.resolve(t, r9, idx, card, new_files) for t in ('CF88:ART.100:PAR.5', 'CF88:ART.40', 'CF88:ART.16', 'CF88:ART.37:INC.XI')}
    regress8 = {t: A.resolve(t, r8, rd(J2B, A.IDX), card, new_files) for t in regress}
    src = lambda t, s: [x['source'] for x in s[t]]  # noqa: E731
    installed_j = {'|'.join(r) for r in jv(ri)}
    v = dict(
        OLD_LINK_REMOVED=len(removed), TEMPORAL_REALLOCATION_ADDED=len(added),
        REMOVED_IS_TEMA558_PAR9=[r.split('|')[4] for r in removed] == [OLD], ADDED_IS_TEMA558_ART100=[r.split('|')[4] for r in added] == [NEW],
        JURIS_RELATIONS_J2B=len(jv(r8)), JURIS_RELATIONS_FINAL=len(jv(r9)),
        JURIS_TARGETS_J2B=len({r[0] for r in jv(r8)}), JURIS_TARGETS_FINAL=len({r[0] for r in jv(r9)}),
        **{f'{k}_FLAG_CHANGES_VS_J2B': len(flags[k]) for k in A.POS},
        HISTORICAL_256_INTACT_EXCEPT_AUTHORIZED=sorted(installed_j - s9) == [next(r for r in installed_j if r.split('|')[4] == OLD)]
        and len(installed_j) == 256,
        ADI_BATCH01_ROWS_PRESERVED=sorted(r for r in s8 if ':ADI:' in r) == sorted(r for r in s9 if ':ADI:' in r) and sum(':ADI:' in r for r in s9) == 5,
        CORRELATA_RELATION_SET_CHANGED=len(by(r8, 'CORRELATA') ^ by(r9, 'CORRELATA')),
        WORK_REFERENCE_SET_CHANGED=len(by(r8, 'WORK_REFERENCE') ^ by(r9, 'WORK_REFERENCE')),
        LEGACY_FILES_SAME_AS_J2B=all(rd(J2B, a['path'].lstrip('/')) == rd(J2B1, a['path'].lstrip('/'))
                                     for a in m1['file_additions'] + [dict(path=A.IDX), dict(path=A.LOOKUP)]),
        TEMA558_FICHA_UNTOUCHED=FICHA_558 in card and FICHA_558 not in m2['changed_vs_physical'] + m2['added_vs_physical'],
        CORRELATA_FILES_BYTE_IDENTICAL=not any(k.startswith('99_RELATIONS_V2/') for k in m2['changed_vs_physical'] + m2['added_vs_physical']),
        ENTENDA_FILES_BYTE_IDENTICAL=not any('/30_ENTENDA/' in k for k in m2['changed_vs_physical'] + m2['added_vs_physical']),
        FIRMWARE_CACHE_RULES_HOLD=cache_ok, LEGACY_RECORDS=n_rec, LOOKUP_QUANTITY_SUM=n_sum,
        TEMA558_NOT_ON_PAR9='STF:RG:558' not in src('CF88:ART.100:PAR.9', sim), TEMA558_ON_ART100='STF:RG:558' in src('CF88:ART.100', sim),
        TEMA558_RESOLVES_WITH_FICHA=all(x['resolved'] and x['ficha_present'] for x in sim['CF88:ART.100'] if x['source'] == 'STF:RG:558'),
        ADI_7047_7064_ON_PAR9=src('CF88:ART.100:PAR.9', sim) == ['STF:ADI:7047-7064'],
        ADI_4425_ON_PAR12=src('CF88:ART.100:PAR.12', sim) == ['STF:ADI:4425'],
        ADI_7697_ON_3_TARGETS=all(src(t, sim) == ['STF:ADI:7697'] for t in ('CF88:ART.166:PAR.9', 'CF88:ART.166:PAR.11', 'CF88:ART.166-A')),
        OTHER_SIMULATED_TARGETS_UNCHANGED=all(sim[t] == sim8[t] for t in sim if t not in ('CF88:ART.100', 'CF88:ART.100:PAR.9')),
        REGRESSION_TARGETS_UNCHANGED=regress == regress8,
        FILES_CHANGED=len(m2['changed_vs_physical']), FILES_ADDED=len(m2['added_vs_physical']))
    return dict(artifact='J2B_1_ISOLATION_AUDIT', fix='J2B_PREDEPLOY_TEMPORAL_FIX', before='J2B_CANDIDATE_HOST_ONLY (SUPERSEDED_BEFORE_PHYSICAL_DEPLOY)',
                after='J2B_1_CANDIDATE_HOST_ONLY', package_build_id=m2['build_id'], verdict=v, removed=removed, added=added,
                flag_changes=flags, device_simulation=dict(before=sim8, after=sim), regression_simulation=regress)


if __name__ == '__main__':
    b = (json.dumps(build(), ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    print(json.dumps(json.loads(b)['verdict'], ensure_ascii=False, indent=1))
