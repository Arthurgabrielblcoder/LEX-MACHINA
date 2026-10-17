"""J2C: semantic check READ DIRECTLY FROM THE CARD after the deploy of J2B.1 (read only). Base = backup PRE of the card (sd_pre, J1.5 state).

Firmware mirror (build_j2b_isolation_audit): query keys -> REF_PAYLOAD rows -> key in the card JURISPRUDENCIA.IDX -> list label -> ficha on the
card; PSRAM cache rules on the card indexes. Layer regressions with the DEVICE_INTEGRATION simulator on the card bytes.
Usage: python semantic_check_j2c_sd.py D: --backup DIR [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'DEVICE_INTEGRATION/tools'))
import build_j2b_isolation_audit as A  # noqa: E402

PAYLOAD = '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'
TARGETS = '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX'
LOOKUP_REF = '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX'
OLD558 = 'JURISPRUDENCE:STF:RG:558:CF88:100:-:-:-@CF88:ART.100:PAR.9'
ADDED = {'JURISPRUDENCE:STF:RG:558:CF88:100:-:-:-@CF88:ART.100', 'JURISPRUDENCE:STF:ADI:4425:CF88:100:12:-:-@CF88:ART.100:PAR.12',
         'JURISPRUDENCE:STF:ADI:7047-7064:CF88:100:9:-:-@CF88:ART.100:PAR.9', 'JURISPRUDENCE:STF:ADI:7697:CF88:166:9:-:-@CF88:ART.166:PAR.9',
         'JURISPRUDENCE:STF:ADI:7697:CF88:166:11:-:-@CF88:ART.166:PAR.11', 'JURISPRUDENCE:STF:ADI:7697:CF88:166-A:-:-:-@CF88:ART.166-A'}


def check(card_root, backup):
    root, pre = Path(card_root), Path(backup)
    files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and 'System Volume Information' not in p.parts}
    pb, pc = A.rows((pre / 'sd_pre' / PAYLOAD).read_bytes()), A.rows((root / PAYLOAD).read_bytes())
    sb, sc = {'|'.join(r) for r in pb}, {'|'.join(r) for r in pc}
    tb = {r[0]: r for r in A.rows((pre / 'sd_pre' / TARGETS).read_bytes())}
    tc = {r[0]: r for r in A.rows((root / TARGETS).read_bytes())}
    flags = {k: sorted(t for t in tb if tb[t][3][i] != tc[t][3][i]) for k, i in A.POS.items()}
    by = lambda rs, t: {'|'.join(r) for r in rs if r[1] == t}  # noqa: E731
    jv = [r for r in pc if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
    lookup_targets = {r[0] for r in A.rows((root / LOOKUP_REF).read_bytes())}
    idx, lk = (root / A.IDX).read_bytes(), (root / A.LOOKUP).read_bytes()
    cache_ok, n_rec, n_sum = A.cache_rules(idx, lk)
    res = lambda t: A.resolve(t, pc, idx, files, set())  # noqa: E731
    sim = {t: res(t) for t in ('CF88:ART.100:PAR.9', 'CF88:ART.100', 'CF88:ART.100:PAR.10', 'CF88:ART.100:PAR.12', 'CF88:ART.166:PAR.9',
                               'CF88:ART.166:PAR.11', 'CF88:ART.166-A', 'CF88:ART.166', 'CF88:ART.92', 'CF88:ART.98', 'CF88:ART.16',
                               'CF88:ART.37:INC.XI', 'CF88:ART.100:PAR.5', 'CF88:ART.40')}
    src = lambda t: [x['source'] for x in sim[t]]  # noqa: E731
    lbl = lambda t: [x['list_label'] for x in sim[t]]  # noqa: E731
    import canonical_layer_audit as L
    import device_lookup_simulator as S
    dev = S.Device(root / '99_LEX_V1')
    try:
        corr = [r[5] for r in L.device_query_union(dev, 'CF88:ART.202:PAR.5')[0].get(L.CORRELATA, [])]
        works = sorted(r[6] for r in L.device_query_union(dev, 'CF88:ART.196')[0].get(L.REFERENCIA, []))
    finally:
        dev.close()
    entenda = tc['CF88:ART.127'][3][A.POS['E']] in 'EB'
    v = dict(
        JURIS_RELATIONS_INSTALLED=len(jv), JURIS_TARGETS_INSTALLED=len({r[0] for r in jv}),
        ROWS_REMOVED=sorted(r.split('|')[4] for r in sb - sc), ROWS_ADDED=sorted(r.split('|')[4] for r in sc - sb),
        DELTA_EQUALS_J2B_1=sorted(r.split('|')[4] for r in sb - sc) == [OLD558] and {r.split('|')[4] for r in sc - sb} == ADDED,
        CORRELATA_RELATIONS_CHANGED=len(by(pb, 'CORRELATA') ^ by(pc, 'CORRELATA')),
        WORK_REFERENCE_RELATIONS_CHANGED=len(by(pb, 'WORK_REFERENCE') ^ by(pc, 'WORK_REFERENCE')),
        FLAG_CHANGES={k: len(x) for k, x in flags.items()}, J_FLAG_CHANGED_TARGETS=flags['J'],
        J_FLAG_EQUALS_VISIBLE={t for t, r in tc.items() if r[3][A.POS['J']] == 'J'} == {r[0] for r in jv},
        R_FLAG_KNOWN_DIVERGENCE=sum(1 for t, r in tc.items() if (r[3][A.POS['R']] == 'R') != (t in lookup_targets)),
        LEGACY_INDEX_PREFIX_IDENTICAL=idx.startswith((pre / 'sd_pre' / A.IDX).read_bytes()) and lk.startswith((pre / 'sd_pre' / A.LOOKUP).read_bytes()),
        FIRMWARE_CACHE_RULES_HOLD=cache_ok, LEGACY_RECORDS=n_rec, LOOKUP_QUANTITY_SUM=n_sum,
        PAR9=lbl('CF88:ART.100:PAR.9'), ART100=lbl('CF88:ART.100'), PAR10=lbl('CF88:ART.100:PAR.10'), PAR12=lbl('CF88:ART.100:PAR.12'),
        ART166_PAR9=lbl('CF88:ART.166:PAR.9'), ART166_PAR11=lbl('CF88:ART.166:PAR.11'), ART166A=lbl('CF88:ART.166-A'),
        ART166_CAPUT=lbl('CF88:ART.166'), ART92=lbl('CF88:ART.92'), ART98=lbl('CF88:ART.98'), ART16=lbl('CF88:ART.16'),
        ART37_XI=lbl('CF88:ART.37:INC.XI'), ART100_PAR5=lbl('CF88:ART.100:PAR.5'), ART40=lbl('CF88:ART.40'),
        ALL_ITEMS_RESOLVE_WITH_FICHA=all(x['resolved'] and x['ficha_present'] for xs in sim.values() for x in xs),
        CORRELATA_202_PAR5=corr, REFERENCIAS_196=works, ENTENDA_127_AVAILABLE=entenda)
    ok = (v['JURIS_RELATIONS_INSTALLED'], v['JURIS_TARGETS_INSTALLED']) == (261, 160) and v['DELTA_EQUALS_J2B_1'] \
        and v['CORRELATA_RELATIONS_CHANGED'] == 0 and v['WORK_REFERENCE_RELATIONS_CHANGED'] == 0 \
        and v['FLAG_CHANGES'] == dict(E=0, C=0, J=4, W=0, R=0, X=0) and v['J_FLAG_EQUALS_VISIBLE'] and v['R_FLAG_KNOWN_DIVERGENCE'] == 42 \
        and v['LEGACY_INDEX_PREFIX_IDENTICAL'] and v['FIRMWARE_CACHE_RULES_HOLD'] and v['ALL_ITEMS_RESOLVE_WITH_FICHA'] \
        and src('CF88:ART.100:PAR.9') == ['STF:ADI:7047-7064'] and 'STF:RG:558' in src('CF88:ART.100') \
        and src('CF88:ART.100:PAR.12') == ['STF:ADI:4425'] \
        and all(src(t) == ['STF:ADI:7697'] for t in ('CF88:ART.166:PAR.9', 'CF88:ART.166:PAR.11', 'CF88:ART.166-A')) \
        and v['ART166A'] == ['ADI 7697 (CAUTELAR)'] and not src('CF88:ART.166') and 'STF:ADI:3392' not in src('CF88:ART.92') + src('CF88:ART.98') \
        and {'STF:RG:367', 'STF:RG:387'} <= set(src('CF88:ART.16')) and 'STF:RG:1167' in src('CF88:ART.37:INC.XI') \
        and corr == ['EXT_LC108_2001'] and works == ['Sicko - S.O.S. Saúde'] and entenda
    v['RESULT'] = 'PASS' if ok else 'FAIL'
    return v


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('drive')
    ap.add_argument('--backup', required=True)
    ap.add_argument('--out')
    a = ap.parse_args()
    v = check(a.drive.rstrip('\\/') + '/', a.backup)
    t = json.dumps(v, ensure_ascii=False, indent=1) + '\n'
    if a.out:
        Path(a.out).write_text(t, encoding='utf-8', newline='\n')
    print(t)
    sys.exit(0 if v['RESULT'] == 'PASS' else 3)
