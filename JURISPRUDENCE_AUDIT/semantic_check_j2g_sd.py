"""J2G: semantic check READ DIRECTLY FROM THE CARD after the deploy of J2F Candidate A (read only). Base = backup PRE of the card (sd_pre,
J2C state) + the committed J2C card package bytes. Firmware mirror = CURRENT firmware (build_j2b_isolation_audit labels: adi / repercussao_geral
/ sumula_vinculante; everything else "OUTRO"; only "STF:" ids accepted). Layer regressions with the DEVICE_INTEGRATION simulator on the card bytes.
Every relation of the candidate is validated, not only the samples.
Usage: python semantic_check_j2g_sd.py D: --backup DIR [--out FILE]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'DEVICE_INTEGRATION/tools'))
import build_j2b_isolation_audit as A  # noqa: E402
import build_j2_batch as G  # noqa: E402

PAYLOAD = '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'
TARGETS = '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX'
LOOKUP_REF = '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX'
CARD_PKG = HERE / 'J2B_1_CANDIDATE_HOST_ONLY/candidate/SD'
ADDITIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2F.json'
RAT = HERE / 'J2_RATIFICATION_RECORD_03_09.json'
SAMPLES = {   # target -> labels that MUST be listed (CURRENT firmware); EXACT = the list must be exactly this
    'CF88:ART.23:INC.II': ['RG TEMA 793'], 'CF88:ART.22:INC.I': ['SV 46'], 'CF88:ART.85:PAR.UNICO': ['SV 46'],
    'ADCT:ART.101:PAR.5': ['ADI 7047/7064'], 'ADCT:ART.107-A': ['ADI 7064'], 'CF88:ART.100:PAR.11': ['ADI 7047/7064'],
    'CF88:ART.103:PAR.3': ['ADI 1616', 'ADI 1254'], 'ADCT:ART.27:PAR.11': ['ADI 5017 (CAUTELAR)'], 'CF88:ART.31:PAR.2': ['RG TEMA 157', 'RG TEMA 835'],
    'CF88:ART.5:INC.LV': ['SV 5'], 'CF88:ART.7:INC.XXVI': ['RG TEMA 1046', 'RG TEMA 935'], 'CF88:ART.5:INC.XXXVIII': ['RG TEMA 1068'],
    'CF88:ART.5:INC.LXVII': ['SV 25'], 'CF88:ART.14:PAR.5': ['RG TEMA 1229'], 'CF88:ART.142': ['ADI 6457'],
    'CF88:ART.150:PAR.7': ['RG TEMA 201', 'ADI 2777'], 'CF88:ART.155:PAR.2:INC.VII': ['RG TEMA 1093'],
    'CF88:ART.166-A': ['ADI 7697 (CAUTELAR)'], 'CF88:ART.100': ['RG TEMA 558']}
EXACT = {'ADCT:ART.107-A', 'CF88:ART.166-A'}
MUST_BE_ABSENT = ('STF:HC:232627', 'STF:HC:70648', 'STF:MS:21689', 'STF:MS:21564', 'STF:MS:27931', 'STF:AP:694', 'STF:AI:343461', 'STF:INQ:4781',
                  'STF:INQ:672', 'STF:RCL:84738', 'STF:ADPF:378', 'STF:ADPF:964', 'STF:ADPF:672', 'TSE:SUMULA:9', 'STJ:SUMULA:403', 'STF:SUMULA:702')


def rejected_pairs():
    out = []
    for f in (HERE / 'J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json', HERE / 'J2_HIGH_BACKLOG/J2D_BATCH02_DECISIONS.json'):
        for x in json.loads(f.read_text(encoding='utf-8'))['decisions']:
            if 'REJECT' in x['decision']:
                ids = [p['id'] for p in x.get('precedents', [])] or [x['precedent']]
                out += [(x.get('target_id') or x['recommended_by_backlog'], i, x['recommendation_id']) for i in ids]
    for n in (3, 4, 6, 7, 8, 9):
        for x in json.loads(G.batch_file(n).read_text(encoding='utf-8'))['decisions']:
            if 'REJECT' in x['decision']:
                out += [(x['recommended_by_backlog'], p['id'], x['recommendation_id']) for p in x['precedents']]
    return out


def same_precedent(source_id, pid):
    """True if source_id is pid itself or a joint record containing pid (STF:ADI:3423-3392-3432-3520 contains STF:ADI:3392)."""
    s, p = source_id.split(':'), pid.split(':')
    return s[:2] == p[:2] and p[2] in s[2].split('-')


def check(card_root, backup):
    root, pre = Path(card_root), Path(backup)
    files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and 'System Volume Information' not in p.parts}
    pb, pc = A.rows((pre / 'sd_pre' / PAYLOAD).read_bytes()), A.rows((root / PAYLOAD).read_bytes())
    if (pre / 'sd_pre' / PAYLOAD).read_bytes() != (CARD_PKG / PAYLOAD).read_bytes():
        raise SystemExit('PRE_BACKUP_IS_NOT_J2C')
    sb, sc = {'|'.join(r) for r in pb}, {'|'.join(r) for r in pc}
    tb = {r[0]: r for r in A.rows((pre / 'sd_pre' / TARGETS).read_bytes())}
    tc = {r[0]: r for r in A.rows((root / TARGETS).read_bytes())}
    flags = {k: sorted(t for t in tb if tb[t][3][i] != tc[t][3][i]) for k, i in A.POS.items()}
    by = lambda rs, t: {'|'.join(r) for r in rs if r[1] == t}  # noqa: E731
    jvb = [r for r in pb if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
    jv = [r for r in pc if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
    lookup_targets = {r[0] for r in A.rows((root / LOOKUP_REF).read_bytes())}
    idx, lk = (root / A.IDX).read_bytes(), (root / A.LOOKUP).read_bytes()
    pre_idx = (pre / 'sd_pre' / A.IDX).read_bytes()
    cache_ok, n_rec, n_sum = A.cache_rules(idx, lk)
    add = json.loads(ADDITIONS.read_text(encoding='utf-8'))
    recs_a = [r for r in add['records'] if r['group'] == 'A']
    expected = {f"JURISPRUDENCE:{r['source_reference_id']}@{r['target_id']}" for r in recs_a}
    added = {r.split('|')[4] for r in sc - sb}
    juris_targets = sorted({r[0] for r in jv} | {r[0] for r in jvb})
    now = {t: A.resolve(t, pc, idx, files, set()) for t in sorted(set(juris_targets) | set(SAMPLES))}
    base_files = files - {k for k in files if k.startswith('99_JURISPRUDENCIA_V2/03_CONTEUDO/') and k.rsplit('/', 1)[1] in
                          {r['new_ficha'].replace(':', '_').replace('/', '_') + '.TXT' for r in recs_a if r.get('new_ficha')}}
    was = {t: A.resolve(t, pb, pre_idx, base_files, set()) for t in now}
    touched = {r['target_id'] for r in recs_a}
    all_items = [x for xs in now.values() for x in xs]
    labels = {t: [x.get('list_label') for x in xs] for t, xs in now.items()}
    srcs = {r[5] for r in jv}
    rej = rejected_pairs()
    rej_published = sorted({f'{t}|{p}|{rid}' for t, p, rid in rej for r in jv if r[0] == t and same_precedent(r[5], p)})
    rat = {i['recommendation_id']: i for i in json.loads(RAT.read_text(encoding='utf-8'))['items']}
    by_ref = {f"JURISPRUDENCE:{r['source_reference_id']}@{r['target_id']}": r for r in recs_a}
    non_linking_created = sorted(ref for ref in added if ref in by_ref and by_ref[ref]['origin'] == 'J2F'
                                 and any(rat[d]['decision'] in ('DUPLICATE_RECOMMENDATION', 'ALREADY_COVERED') for d in by_ref[ref]['ratified_decisions']))
    sample_ok = {t: (labels[t] == want) if t in EXACT else all(w in labels[t] for w in want) for t, want in SAMPLES.items()}
    import canonical_layer_audit as L
    import device_lookup_simulator as S
    dev = S.Device(root / '99_LEX_V1')
    try:
        corr = [r[5] for r in L.device_query_union(dev, 'CF88:ART.202:PAR.5')[0].get(L.CORRELATA, [])]
        works = sorted(r[6] for r in L.device_query_union(dev, 'CF88:ART.196')[0].get(L.REFERENCIA, []))
    finally:
        dev.close()
    v = dict(
        JURIS_RELATIONS=len(jv), JURIS_TARGETS=len({r[0] for r in jv}), BASE_FROM_PRE_BACKUP=(len(jvb), len({r[0] for r in jvb})),
        ROWS_REMOVED=len(sb - sc), ROWS_ADDED=len(sc - sb), ADDED_EQUALS_CANDIDATE_A=added == expected,
        LEGACY_261_RELATIONS_PRESERVED=f"{sum(1 for r in jvb if '|'.join(r) in sc)}/{len(jvb)}",
        OLD_ITEMS_PRESERVED_ON_TOUCHED_TARGETS=all(all(x in now[t] for x in was[t]) for t in now if t in touched),
        UNTOUCHED_TARGETS_IDENTICAL=all(now[t] == was[t] for t in now if t not in touched),
        CORRELATAS_CHANGED='NO' if not by(pb, 'CORRELATA') ^ by(pc, 'CORRELATA') else 'YES',
        WORK_REFERENCES_CHANGED='NO' if not by(pb, 'WORK_REFERENCE') ^ by(pc, 'WORK_REFERENCE') else 'YES',
        ENTENDA_CHANGED='NO' if not by(pb, 'ENTENDA') ^ by(pc, 'ENTENDA') else 'YES',
        FLAG_CHANGES={k: len(x) for k, x in flags.items()}, NEW_TARGETS_WITH_J=len(flags['J']),
        J_FLAG_EQUALS_VISIBLE={t for t, r in tc.items() if r[3][A.POS['J']] == 'J'} == {r[0] for r in jv},
        R_FLAG_KNOWN_DIVERGENCE=sum(1 for t, r in tc.items() if (r[3][A.POS['R']] == 'R') != (t in lookup_targets)),
        LEGACY_PREFIX_IDENTICAL='YES' if idx.startswith(pre_idx) and lk.startswith((pre / 'sd_pre' / A.LOOKUP).read_bytes()) else 'NO',
        FIRMWARE_CACHE_RULES_HOLD=cache_ok, LEGACY_RECORDS=n_rec, LOOKUP_QUANTITY_SUM=n_sum,
        ALL_RELATIONS_RESOLVE_WITH_FICHA=all(x['resolved'] and x['ficha_present'] for x in all_items),
        NO_LABEL_OUTRO='YES' if not [x for x in all_items if x.get('list_label', '').startswith('OUTRO')] else 'NO',
        ALL_IDS_STF_PREFIX=all(r[5].startswith('STF:') for r in jv),
        TYPES_ON_CARD=dict(sorted(collections.Counter(l.split('|')[1] for l in idx.decode('utf-8').split('\n')[1:] if l).items())),
        GENERIC_FW_ONLY_RELATIONS_PUBLISHED=sorted(s for s in srcs if any(same_precedent(s, m) for m in MUST_BE_ABSENT)),
        REJECTED_PAIRS_CHECKED=len(rej), REJECTED_RELATIONS_PUBLISHED=rej_published,
        DUPLICATE_OR_ALREADY_COVERED_CREATED_NEW_RELATIONS=non_linking_created,
        PROVISIONAL_ON_CARD=sorted({x['list_label'] for x in all_items if '(' in x.get('list_label', '')}),
        SAMPLES={t: labels[t] for t in SAMPLES}, SAMPLES_OK=sample_ok,
        TEMA_558_ART100=labels['CF88:ART.100'], ART16_367_387=labels.get('CF88:ART.16'),
        CORRELATA_202_PAR5=corr, REFERENCIAS_196=works, ENTENDA_127_AVAILABLE=tc['CF88:ART.127'][3][A.POS['E']] in 'EB')
    ok = (v['JURIS_RELATIONS'], v['JURIS_TARGETS']) == (299, 186) and v['BASE_FROM_PRE_BACKUP'] == (261, 160) and v['ROWS_REMOVED'] == 0 \
        and v['ADDED_EQUALS_CANDIDATE_A'] and v['LEGACY_261_RELATIONS_PRESERVED'] == '261/261' and v['OLD_ITEMS_PRESERVED_ON_TOUCHED_TARGETS'] \
        and v['UNTOUCHED_TARGETS_IDENTICAL'] and (v['CORRELATAS_CHANGED'], v['WORK_REFERENCES_CHANGED'], v['ENTENDA_CHANGED']) == ('NO',) * 3 \
        and {k: n for k, n in v['FLAG_CHANGES'].items() if k != 'J'} == dict(E=0, C=0, W=0, R=0, X=0) and v['J_FLAG_EQUALS_VISIBLE'] \
        and v['LEGACY_PREFIX_IDENTICAL'] == 'YES' and v['FIRMWARE_CACHE_RULES_HOLD'] and v['ALL_RELATIONS_RESOLVE_WITH_FICHA'] \
        and v['NO_LABEL_OUTRO'] == 'YES' and v['ALL_IDS_STF_PREFIX'] and not v['GENERIC_FW_ONLY_RELATIONS_PUBLISHED'] \
        and not v['REJECTED_RELATIONS_PUBLISHED'] and not v['DUPLICATE_OR_ALREADY_COVERED_CREATED_NEW_RELATIONS'] and all(sample_ok.values()) \
        and {'RG TEMA 367', 'RG TEMA 387'} <= set(v['ART16_367_387'] or []) and corr == ['EXT_LC108_2001'] and works == ['Sicko - S.O.S. Saúde'] \
        and v['ENTENDA_127_AVAILABLE']
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
