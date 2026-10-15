"""REFERÊNCIAS Nº 4 R1: isolation audit C3B.2 (physically approved) x RUN5 candidate. Read-only; deterministic.

Compares, per reference type, the REF_PAYLOAD rows (semantic: TARGET, TYPE, VISIBILITY, STATUS, REFERENCE_ID, SOURCE_ID, LABEL), the
REF_LOOKUP counts, the CORRELATA files (RELACOES/REL_LOOKUP/EXT_ARTIGOS) and every flag position of CF88_TARGETS.IDX; checks the detail
header (old entries byte-identical, sorted for the firmware binary search) and the firmware limits of the layer-4 path.
Output: REFERENCE_COVERAGE_AUDIT/REFERENCES_4_R1_ISOLATION_AUDIT.json.   Usage: python build_references4_r1_isolation_audit.py [--check]
"""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / 'CORRELATA_COVERAGE_AUDIT/C3B2_PHYSICAL_TEST_PACKAGE/candidate/SD'
RUN5 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate'
CAND = RUN5 / 'device_ready'
ADDS_R1 = ROOT / 'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS_R1.json'
HDR_BASE = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h'
HDR_CAND = RUN5 / 'device_candidate/lex_ref_detail_data.RUN5_CANDIDATE.h'
FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
OUT = HERE / 'REFERENCES_4_R1_ISOLATION_AUDIT.json'
FLAG_NAMES = ('E', 'C', 'J', 'W', 'R', 'X')
FILES = dict(TARGETS=('99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX', 'CF88_TARGETS.IDX'), REF_LOOKUP=('99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX', 'REF_LOOKUP.IDX'),
             REF_PAYLOAD=('99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX', 'REF_PAYLOAD.IDX'),
             RELACOES=('99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX', 'RELACOES.IDX'),
             REL_LOOKUP=('99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX', 'REL_LOOKUP.IDX'),
             EXT_ARTIGOS=('99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX', 'EXT_ARTIGOS.IDX'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rows(b):
    return [l.split('|') for l in b.decode('utf-8').split('\n') if l and not l.startswith('#')]


def pair(name):
    a, c = FILES[name]
    return (BASE / a).read_bytes(), (CAND / c).read_bytes()


def fw_define(name):
    for p in sorted(FW.glob('*.h')) + sorted(FW.glob('*.ino')):
        m = re.search(rf'#define {name} (\d+)', lf(p.read_bytes()).decode('utf-8', errors='replace'))
        if m:
            return int(m.group(1))
    raise SystemExit(f'DEFINE_NOT_FOUND {name}')


def lf(b):
    return b.replace(b'\r\n', b'\n')                  # committed (LF) form; a checkout with core.autocrlf may give CRLF


def header_entries(p):
    txt = lf(Path(p).read_bytes()).decode('utf-8')
    body = txt[txt.index('LEXV1_REF_DETALHES[LEXV1_REF_DETAIL_COUNT] = {'):]
    ents = re.findall(r'\n  \{"((?:[^"\\]|\\.)*)", .*?\},(?=\n  \{|\n\};)', body, re.S)
    blocks = re.findall(r'\n  (\{"(?:[^"\\]|\\.)*", .*?\},)(?=\n  \{|\n\};)', body, re.S)
    return dict(zip(ents, blocks)), int(re.search(r'#define LEXV1_REF_DETAIL_COUNT (\d+)', txt).group(1))


def audit():
    out = dict(artifact='REFERENCES_4_R1_ISOLATION_AUDIT', base='C3B.2 physically approved (CORRELATA_COVERAGE_AUDIT/C3B2_PHYSICAL_TEST_PACKAGE/candidate)',
               candidate=CAND.relative_to(ROOT).as_posix())
    out['files'] = {k: dict(base_sha256=sha(pair(k)[0]), candidate_sha256=sha(pair(k)[1]), identical=pair(k)[0] == pair(k)[1]) for k in FILES}
    # ---- REF_PAYLOAD by type
    pb, pc = (rows(b) for b in pair('REF_PAYLOAD'))
    by = lambda rs, t: {tuple(r) for r in rs if r[1] == t}  # noqa: E731
    types = sorted({r[1] for r in pb + pc})
    per = {}
    for t in types:
        b, c = by(pb, t), by(pc, t)
        per[t] = dict(base=len(b), candidate=len(c), removed=sorted('|'.join(x) for x in b - c), added=sorted('|'.join(x) for x in c - b))
    out['ref_payload_by_type'] = per
    cor_b, cor_c = by(pb, 'CORRELATA'), by(pc, 'CORRELATA')
    rel_b, rel_c = rows(pair('RELACOES')[0]), rows(pair('RELACOES')[1])
    out['correlata'] = dict(
        CORRELATA_RELATION_SET_CHANGED=len(cor_b ^ cor_c),
        CORRELATA_REFERENCE_IDS_CHANGED=len({r[4] for r in cor_b} ^ {r[4] for r in cor_c}),
        CORRELATA_DESTINATIONS_CHANGED=len({(r[0], r[4], r[5]) for r in cor_b} ^ {(r[0], r[4], r[5]) for r in cor_c}),
        CORRELATA_ROUTES_CHANGED=sum(1 for x, y in zip(rel_b, rel_c) if x != y) + abs(len(rel_b) - len(rel_c)),
        device_ready_visible=sum(r[2] == 'CURRENT_VISIBLE' for r in cor_c), hidden_historical=sum(r[2] != 'CURRENT_VISIBLE' for r in cor_c),
        reference_id_to_relacoes_1to1=all(sum(1 for x in rel_c if x[5] == r[4].split(':', 1)[1].split('@')[0]) == 1 for r in cor_c
                                         if r[2] == 'CURRENT_VISIBLE'),
        relacoes_rows=len(rel_c))
    # ---- WORK_REFERENCE
    wb, wc = by(pb, 'WORK_REFERENCE'), by(pc, 'WORK_REFERENCE')
    adds = json.loads(ADDS_R1.read_text(encoding='utf-8'))['records']
    expected_new = {f"WORK_REFERENCE:{a['work_id']}@{a['target_id']}" for a in adds}
    out['work_reference'] = dict(
        OLD_WORK_REFERENCE_SET_PRESERVED=wb <= wc, removed=len(wb - wc), added=sorted(r[4] for r in wc - wb),
        added_equals_approved_overlay={r[4] for r in wc - wb} == expected_new,
        relations_before=len(wb), relations_after=len(wc), works_used_before=len({r[5] for r in wb}), works_used_after=len({r[5] for r in wc}),
        targets_before=len({r[0] for r in wb}), targets_after=len({r[0] for r in wc}),
        new_targets_had_work_before=sorted(t for t in {r[0] for r in wc - wb} if t in {r[0] for r in wb}),
        repeated_works=sum(1 for v in collections.Counter(r[5] for r in wc).values() if v > 1))
    # ---- REF_LOOKUP: only the lookup rows of the new targets are new; every other target keeps its count
    lb = {r[0]: int(r[2]) for r in rows(pair('REF_LOOKUP')[0])}
    lc = {r[0]: int(r[2]) for r in rows(pair('REF_LOOKUP')[1])}
    out['ref_lookup'] = dict(rows_before=len(lb), rows_after=len(lc), removed=sorted(set(lb) - set(lc)), added=sorted(set(lc) - set(lb)),
                             count_changed=sorted(t for t in set(lb) & set(lc) if lb[t] != lc[t]))
    # ---- TARGETS flags per position
    tb, tc = {r[0]: r for r in rows(pair('TARGETS')[0])}, {r[0]: r for r in rows(pair('TARGETS')[1])}
    changes = collections.defaultdict(list)
    for tid in tb:
        if tb[tid][:3] != tc[tid][:3]:
            changes['NON_FLAG_FIELDS'].append(tid)
        for i, n in enumerate(FLAG_NAMES):
            if tb[tid][3][i] != tc[tid][3][i]:
                changes[n].append(dict(target_id=tid, before=tb[tid][3], after=tc[tid][3]))
    w_targets = {r[0] for r in wc if r[2] == 'CURRENT_VISIBLE'}
    out['targets'] = dict(
        rows_base=len(tb), rows_candidate=len(tc), same_target_set=set(tb) == set(tc),
        flag_changes={n: len(changes.get(n, [])) for n in FLAG_NAMES}, non_flag_field_changes=len(changes.get('NON_FLAG_FIELDS', [])),
        w_changes=changes.get('W', []),
        W_FLAGS_DERIVED_ONLY_FROM_NEW_APPROVED_WORK_REFERENCES=(
            {c['target_id'] for c in changes.get('W', [])} == {r[0] for r in wc - wb} - {r[0] for r in wb}
            and all(c['after'][3] == 'W' for c in changes.get('W', []))),
        w_flag_equals_visible_work_targets={t for t, r in tc.items() if r[3][3] == 'W'} == w_targets,
        c_flag_equals_visible_correlata_targets={t for t, r in tc.items() if r[3][1] == 'C'} == {r[0] for r in cor_c if r[2] == 'CURRENT_VISIBLE'},
        w_targets_before=sum(r[3][3] == 'W' for r in tb.values()), w_targets_after=sum(r[3][3] == 'W' for r in tc.values()),
        r_flag_note='R ([4], não lido pelo firmware) mantido como aprovado no C3B.2; os 2 novos targets passam a ter linha no REF_LOOKUP com R=-, '
                    'como os 23 já divergentes do gerador no C3B.2.')
    # ---- detail header
    eb, nb = header_entries(HDR_BASE)
    ec, nc = header_entries(HDR_CAND)
    keys = list(ec)
    out['detail_header'] = dict(
        base_count=nb, candidate_count=nc, old_entries_byte_identical=all(ec.get(k) == v for k, v in eb.items()),
        new_keys=sorted(set(ec) - set(eb)), removed_keys=sorted(set(eb) - set(ec)), unique_keys=len(keys) == len(set(keys)),
        sorted_for_strcmp=keys == sorted(keys, key=lambda k: k.encode('utf-8')),
        every_visible_work_link_has_detail={f'{r[0]}|{r[5]}' for r in wc if r[2] == 'CURRENT_VISIBLE'} == set(ec),
        candidate_sha256=sha(lf(HDR_CAND.read_bytes())), base_sha256=sha(lf(HDR_BASE.read_bytes())))
    # ---- firmware limits of the layer-4 path (registered, not optimized)
    key_max, line_max, itens_max = fw_define('LEXV1_KEY_MAX'), fw_define('LEXV1_LINE_MAX'), fw_define('LEXV1_REF_ITENS_MAX')
    per_article = collections.Counter()
    for r in pc:
        if r[1] == 'WORK_REFERENCE' and r[2] == 'CURRENT_VISIBLE':
            t = r[0]
            per_article[t[:-len(':CAPUT')] if t.endswith(':CAPUT') else t] += 1
    payload_lines = [l for l in pair('REF_PAYLOAD')[1].decode('utf-8').split('\n') if l]
    out['firmware_limits'] = dict(
        LEXV1_KEY_MAX=key_max, max_target_id_len=max(len(t) for t in tc), LEXV1_LINE_MAX=line_max,
        max_payload_line_bytes=max(len(l.encode('utf-8')) for l in payload_lines),
        LEXV1_REF_ITENS_MAX=itens_max, max_work_items_per_query=max(per_article.values()),
        RefItem_fonte_cap=47, max_work_id_len=max(len(r[5].encode('utf-8')) for r in wc),
        RefItem_rotulo_cap=119, max_work_label_bytes=max(len(r[6].encode('utf-8')) for r in wc),
        Reg_id_cap=95, max_reference_id_len=max(len(r[4]) for r in pc),
        detail_key_cap=key_max + 55, max_detail_key_len=max(len(k.encode('utf-8')) for k in keys),
        detail_count=nc)
    fl = out['firmware_limits']
    out['firmware_limits']['all_within_limits'] = (fl['max_target_id_len'] < key_max and fl['max_payload_line_bytes'] < line_max
                                                   and fl['max_work_items_per_query'] <= itens_max and fl['max_work_id_len'] <= 47
                                                   and fl['max_work_label_bytes'] <= 119 and fl['max_reference_id_len'] <= 95
                                                   and fl['max_detail_key_len'] < key_max + 56)
    c, t, w = out['correlata'], out['targets'], out['work_reference']
    out['verdict'] = dict(
        CORRELATA_RELATION_SET_CHANGED=c['CORRELATA_RELATION_SET_CHANGED'], CORRELATA_REFERENCE_IDS_CHANGED=c['CORRELATA_REFERENCE_IDS_CHANGED'],
        CORRELATA_ROUTES_CHANGED=c['CORRELATA_ROUTES_CHANGED'], CORRELATA_DESTINATIONS_CHANGED=c['CORRELATA_DESTINATIONS_CHANGED'],
        C_FLAGS_CHANGED=t['flag_changes']['C'], E_FLAGS_CHANGED=t['flag_changes']['E'], J_FLAGS_CHANGED=t['flag_changes']['J'],
        R_FLAGS_CHANGED=t['flag_changes']['R'], X_FLAGS_CHANGED=t['flag_changes']['X'],
        NON_W_TARGET_FLAGS_CHANGED=sum(v for k, v in t['flag_changes'].items() if k != 'W') + t['non_flag_field_changes'],
        W_FLAGS_CHANGED=('DERIVED_ONLY_FROM_NEW_APPROVED_WORK_REFERENCES' if t['W_FLAGS_DERIVED_ONLY_FROM_NEW_APPROVED_WORK_REFERENCES'] else 'FAIL'),
        OLD_WORK_REFERENCE_SET_PRESERVED='PASS' if w['OLD_WORK_REFERENCE_SET_PRESERVED'] and not w['removed'] else 'FAIL',
        JURISPRUDENCE_UNCHANGED=not (per['JURISPRUDENCE']['added'] or per['JURISPRUDENCE']['removed']),
        CORRELATA_FILES_BYTE_IDENTICAL=all(out['files'][k]['identical'] for k in ('RELACOES', 'REL_LOOKUP', 'EXT_ARTIGOS')),
        FIRMWARE_LIMITS='PASS' if out['firmware_limits']['all_within_limits'] else 'FAIL')
    return out


def render():
    return (json.dumps(audit(), ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = render()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes() == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    print(json.dumps(json.loads(b)['verdict'], indent=1))
