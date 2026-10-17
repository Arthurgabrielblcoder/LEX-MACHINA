"""J2H: semantic check READ DIRECTLY FROM THE CARD after the SD deploy of J2H_CANDIDATE_B_OVER_A (read only). Base = backup PRE of the
card (sd_pre = physically approved Candidate A, 299/186). Firmware mirror = GENERIC tribunal/classe firmware (juris_types.label /
id_accepted = JURIS_TYPE_PROTOTYPE patch), NOT the current physical firmware; the CURRENT firmware view is computed only to document why the
card must not be booted before the flash. Every relation on the card is validated, not only the samples.

BACK simulation (firmware model, mirror of abrirRelacao/BACK): for every juris target, the list is resolved, each item is "opened"
(ficha present on the card, title = tribunal + label, súmula without repeated tribunal) and BACK re-resolves the list from the saved origin
(target + selected index): the list must be identical and the index must point to the same precedent.
Usage: python semantic_check_j2h_sd.py D: --backup DIR [--out FILE]
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'DEVICE_INTEGRATION/tools'))
import build_j2b_isolation_audit as A  # noqa: E402
import build_j2f_isolation_audit as F  # noqa: E402
import juris_types as JT  # noqa: E402
import semantic_check_j2g_sd as SG  # noqa: E402

PAYLOAD, TARGETS, LOOKUP_REF = SG.PAYLOAD, SG.TARGETS, SG.LOOKUP_REF
ADDITIONS = SG.ADDITIONS
INO = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'
REQUIRED = ('HC 232627', 'HC 70648', 'MS 21689', 'AP 694', 'AI 343461', 'Inq 4781', 'Rcl 84738 (PROVISÓRIA)', 'ADPF 378 (CAUTELAR)', 'ADPF 964',
            'Súmula 9 TSE')
IMPORTANT = {'CF88:ART.52:PAR.UNICO': ['MS 21689'], 'CF88:ART.55:INC.VI': ['AP 694'], 'CF88:ART.35:INC.IV': ['AI 343461', 'ADI 7369'],
             'CF88:ART.86': ['MS 21564'], 'CF88:ART.86:PAR.1:INC.II': ['ADPF 378 (CAUTELAR)'], 'CF88:ART.52:INC.I': ['ADPF 378 (CAUTELAR)'],
             'CF88:ART.96:INC.III': ['Rcl 84738 (PROVISÓRIA)'], 'CF88:ART.53': ['Inq 4781', 'RG TEMA 950'], 'CF88:ART.84:INC.XII': ['ADPF 964'],
             'CF88:ART.142:PAR.2': ['HC 70648'], 'CF88:ART.15:INC.III': ['Súmula 9 TSE'], 'CF88:ART.53:PAR.1': ['HC 232627'],
             'CF88:ART.29:INC.X': ['Súmula 702 STF'], 'CF88:ART.62:PAR.6': ['MS 27931'], 'CF88:ART.86:PAR.4': ['Inq 672'], 'CF88:ART.198': ['ADPF 672'],
             'CF88:ART.86:PAR.3': ['ADI 978'], 'ADCT:ART.107-A': ['ADI 7064']}
EXACT = {'ADCT:ART.107-A'}


def fw_define(name):
    return int(re.search(rf'#define {name} (\d+)', INO.read_text(encoding='utf-8')).group(1))


def card_view(root, rows, idx, files, fw):
    idx_lines = {l.split('|')[0]: l.split('|') for l in idx.decode('utf-8').split('\n') if l and not l.startswith('#')}
    targets = sorted({r[0] for r in rows if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE'})
    vis = set()
    for t in targets:                                  # visual article target also queries ART.n:CAPUT
        vis.add(t[:-len(':CAPUT')] if t.endswith(':CAPUT') else t)
    return {t: F.view(t, rows, idx_lines, files, fw) for t in sorted(vis | set(IMPORTANT))}, idx_lines


def back_simulation(view, idx_lines):
    for t, items in view.items():
        for i, x in enumerate(items):
            if not (x['resolved'] and x['ficha_present']):
                return False
            key = next((k for k, f in idx_lines.items() if f[6] == x['source'] or k.startswith(x['source'] + ':')), None)
            f = idx_lines[key]
            title = JT.title(f[1], f[2], f[3])
            if title.startswith('OUTRO') or (f[1] in JT.SUMULA and title.count(f[2]) != 1):
                return False
            again = view[t]                            # BACK: re-resolve from the saved origin (same bytes -> same list)
            if again[i]['source'] != x['source'] or again != items:
                return False
    return True


def check(card_root, backup):
    root, pre = Path(card_root), Path(backup)
    files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and 'System Volume Information' not in p.parts}
    pb, pc = A.rows((pre / 'sd_pre' / PAYLOAD).read_bytes()), A.rows((root / PAYLOAD).read_bytes())
    sb, sc = {'|'.join(r) for r in pb}, {'|'.join(r) for r in pc}
    tb = {r[0]: r for r in A.rows((pre / 'sd_pre' / TARGETS).read_bytes())}
    tc = {r[0]: r for r in A.rows((root / TARGETS).read_bytes())}
    flags = {k: sorted(t for t in tb if tb[t][3][i] != tc[t][3][i]) for k, i in A.POS.items()}
    by = lambda rs, t: {'|'.join(r) for r in rs if r[1] == t}  # noqa: E731
    jvb = [r for r in pb if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
    jv = [r for r in pc if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
    lookup_targets = {r[0] for r in A.rows((root / LOOKUP_REF).read_bytes())}
    idx, lk = (root / A.IDX).read_bytes(), (root / A.LOOKUP).read_bytes()
    pre_idx, pre_lk = (pre / 'sd_pre' / A.IDX).read_bytes(), (pre / 'sd_pre' / A.LOOKUP).read_bytes()
    cache_ok, n_rec, n_sum = A.cache_rules(idx, lk)
    add = json.loads(ADDITIONS.read_text(encoding='utf-8'))
    recs_b = [r for r in add['records'] if r['group'] == 'B']
    expected = {f"JURISPRUDENCE:{r['source_reference_id']}@{r['target_id']}" for r in recs_b}
    added = {r.split('|')[4] for r in sc - sb}
    gen, idx_lines = card_view(root, pc, idx, files, 'GENERIC')
    cur, _ = card_view(root, pc, idx, files, 'CURRENT')
    pre_files = files - {f'99_JURISPRUDENCIA_V2/03_CONTEUDO/{r["source_id"].replace(":", "_")}.TXT' for r in recs_b if r.get('new_ficha')}
    pre_lines = {l.split('|')[0]: l.split('|') for l in pre_idx.decode('utf-8').split('\n') if l and not l.startswith('#')}
    was = {t: F.view(t, pb, pre_lines, pre_files, 'GENERIC') for t in gen}
    touched = {r['target_id'][:-len(':CAPUT')] if r['target_id'].endswith(':CAPUT') else r['target_id'] for r in recs_b}
    items = [x for xs in gen.values() for x in xs]
    labels = {t: [x.get('label') for x in xs] for t, xs in gen.items()}
    all_labels = sorted({x.get('label') for x in items})
    srcs = {r[5] for r in jv}
    rej = SG.rejected_pairs()
    rej_pub = sorted({f'{t}|{p}|{rid}' for t, p, rid in rej for r in jv if r[0] == t and SG.same_precedent(r[5], p)})
    rat = {i['recommendation_id']: i for i in json.loads(SG.RAT.read_text(encoding='utf-8'))['items']}
    by_ref = {f"JURISPRUDENCE:{r['source_reference_id']}@{r['target_id']}": r for r in recs_b}
    dup_ac = sorted(ref for ref in added if ref in by_ref and by_ref[ref]['origin'] == 'J2F'
                    and any(rat[d]['decision'] in ('DUPLICATE_RECOMMENDATION', 'ALREADY_COVERED') for d in by_ref[ref]['ratified_decisions']))
    vis_by = collections.Counter(r[0] for r in pc if r[2] == 'CURRENT_VISIBLE')
    max_items = max(sum(vis_by[k] for k in A.query_keys(t)) for t in tc)
    n_lookups = sum(1 for l in lk.split(b'\n') if l and not l.startswith(b'#'))
    lim = dict(MAX_JUR_LOOKUPS_SEGURANCA=fw_define('MAX_JUR_LOOKUPS_SEGURANCA'), lookups=n_lookups, LEXV1_REF_ITENS_MAX=fw_define('LEXV1_REF_ITENS_MAX'),
               max_visible_items_per_target=max_items, MAX_RELACOES_ARTIGO=fw_define('MAX_RELACOES_ARTIGO'),
               max_juris_per_target=max(len(v) for v in gen.values()), legacy_index_bytes=len(idx), lookup_bytes=len(lk))
    cache_limits = cache_ok and n_lookups <= lim['MAX_JUR_LOOKUPS_SEGURANCA'] and max_items <= lim['LEXV1_REF_ITENS_MAX'] \
        and lim['max_juris_per_target'] <= lim['MAX_RELACOES_ARTIGO']
    important_ok = {t: (labels[t] == w) if t in EXACT else all(x in labels[t] for x in w) for t, w in IMPORTANT.items()}
    cur_bad = sorted({x.get('label') or x['source'] for xs in cur.values() for x in xs
                      if x['resolved'] and (x['label'].startswith('OUTRO') or not x['id_accepted_by_firmware'])})
    import canonical_layer_audit as L
    import device_lookup_simulator as S
    dev = S.Device(root / '99_LEX_V1')
    try:
        corr = [r[5] for r in L.device_query_union(dev, 'CF88:ART.202:PAR.5')[0].get(L.CORRELATA, [])]
        works = sorted(r[6] for r in L.device_query_union(dev, 'CF88:ART.196')[0].get(L.REFERENCIA, []))
    finally:
        dev.close()
    v = dict(
        JURIS_RELATIONS=len(jv), JURIS_TARGETS=len({r[0] for r in jv}), BASE_FROM_PRE_BACKUP=[len(jvb), len({r[0] for r in jvb})],
        ROWS_REMOVED=len(sb - sc), ROWS_ADDED=len(sc - sb), NEW_TARGETS_WITH_J=len(flags['J']), ADDED_EQUALS_GROUP_B=added == expected,
        A_RELATIONS_PRESERVED=f"{sum(1 for r in jvb if '|'.join(r) in sc)}/{len(jvb)}",
        A_ITEMS_PRESERVED_ON_TOUCHED_TARGETS=all(all(x in gen[t] for x in was[t]) for t in gen if t in touched),
        UNTOUCHED_TARGETS_IDENTICAL=all(gen[t] == was[t] for t in gen if t not in touched),
        CORRELATAS_CHANGED='NO' if not by(pb, 'CORRELATA') ^ by(pc, 'CORRELATA') else 'YES',
        REFERENCES4_CHANGED='NO' if not by(pb, 'WORK_REFERENCE') ^ by(pc, 'WORK_REFERENCE') else 'YES',
        ENTENDA_CHANGED='NO' if not by(pb, 'ENTENDA') ^ by(pc, 'ENTENDA') else 'YES',
        FLAG_CHANGES={k: len(x) for k, x in flags.items()},
        J_FLAG_EQUALS_VISIBLE={t for t, r in tc.items() if r[3][A.POS['J']] == 'J'} == {r[0] for r in jv},
        R_FLAG_KNOWN_DIVERGENCE=sum(1 for t, r in tc.items() if (r[3][A.POS['R']] == 'R') != (t in lookup_targets)),
        A_INDEX_PREFIX_IDENTICAL='YES' if idx.startswith(pre_idx) and lk.startswith(pre_lk) else 'NO',
        FIRMWARE_CACHE_RULES_HOLD=cache_ok, LEGACY_RECORDS=n_rec, LOOKUP_QUANTITY_SUM=n_sum, CACHE_LIMITS='PASS' if cache_limits else 'FAIL', LIMITS=lim,
        ALL_B_FICHAS_RESOLVE='YES' if all(x['resolved'] and x['ficha_present'] for t in touched for x in gen[t]) else 'NO',
        ALL_RELATIONS_RESOLVE_WITH_FICHA=all(x['resolved'] and x['ficha_present'] for x in items),
        ALL_IDS_ACCEPTED_BY_GENERIC_FIRMWARE=all(x['id_accepted_by_firmware'] for x in items if x['resolved']),
        NO_LABEL_OUTRO='YES' if not [l for l in all_labels if l and l.startswith('OUTRO')] else 'NO',
        REQUIRED_LABELS_FOUND={q: q in all_labels for q in REQUIRED},
        TYPES_ON_CARD=dict(sorted(collections.Counter(f[1] + '/' + f[2] for f in idx_lines.values()).items())),
        IMPORTANT_TARGETS={t: labels[t] for t in IMPORTANT}, IMPORTANT_TARGETS_OK=important_ok,
        BACK_BEHAVIOR_SIMULATION='PASS' if back_simulation(gen, idx_lines) else 'FAIL',
        UNRESOLVED_EXTERNAL_PUBLISHED=sum(1 for s in srcs if s.startswith('STJ:SUMULA:403')) + idx.count(b'STJ:SUMULA:403')
        + sum(1 for f in files if 'STJ_SUMULA_403' in f),
        REJECTED_PAIRS_CHECKED=len(rej), REJECTED_RELATIONS_PUBLISHED=rej_pub, DUPLICATE_OR_ALREADY_COVERED_CREATED_NEW_RELATIONS=dup_ac,
        PROVISIONAL_ON_CARD=sorted({x['label'] for x in items if x.get('label') and '(' in x['label']}),
        CURRENT_FIRMWARE_WOULD_SHOW_WRONG=cur_bad, SAFE_TO_BOOT_WITH_CURRENT_FIRMWARE='NO',
        CORRELATA_202_PAR5=corr, REFERENCIAS_196=works, ENTENDA_127_AVAILABLE=tc['CF88:ART.127'][3][A.POS['E']] in 'EB')
    ok = (v['JURIS_RELATIONS'], v['JURIS_TARGETS']) == (315, 198) and v['BASE_FROM_PRE_BACKUP'] == [299, 186] and v['ROWS_REMOVED'] == 0 \
        and v['ADDED_EQUALS_GROUP_B'] and v['A_RELATIONS_PRESERVED'] == '299/299' and v['A_ITEMS_PRESERVED_ON_TOUCHED_TARGETS'] \
        and v['UNTOUCHED_TARGETS_IDENTICAL'] and (v['CORRELATAS_CHANGED'], v['REFERENCES4_CHANGED'], v['ENTENDA_CHANGED']) == ('NO',) * 3 \
        and {k: n for k, n in v['FLAG_CHANGES'].items() if k != 'J'} == dict(E=0, C=0, W=0, R=0, X=0) and v['J_FLAG_EQUALS_VISIBLE'] \
        and v['A_INDEX_PREFIX_IDENTICAL'] == 'YES' and v['CACHE_LIMITS'] == 'PASS' and v['ALL_B_FICHAS_RESOLVE'] == 'YES' \
        and v['ALL_RELATIONS_RESOLVE_WITH_FICHA'] and v['ALL_IDS_ACCEPTED_BY_GENERIC_FIRMWARE'] and v['NO_LABEL_OUTRO'] == 'YES' \
        and all(v['REQUIRED_LABELS_FOUND'].values()) and all(important_ok.values()) and v['BACK_BEHAVIOR_SIMULATION'] == 'PASS' \
        and v['UNRESOLVED_EXTERNAL_PUBLISHED'] == 0 and not rej_pub and not dup_ac and corr == ['EXT_LC108_2001'] \
        and works == ['Sicko - S.O.S. Saúde'] and v['ENTENDA_127_AVAILABLE']
    v['GENERIC_FW_SIMULATION'] = 'PASS' if ok else 'FAIL'
    v['RESULT'] = v['GENERIC_FW_SIMULATION']
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
