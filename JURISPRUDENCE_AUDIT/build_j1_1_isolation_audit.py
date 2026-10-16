"""J1.1 — isolation audit: physically approved baseline (REFERENCES 4, 2026-10-16) x RUN6 candidate. Read-only; deterministic.

Proves that the only semantic change is the removal of the 20 ratified jurisprudence links: CORRELATA and WORK_REFERENCE rows identical,
no JURISPRUDENCE row added or altered, CF88_TARGETS changes only in flag position [2] (J) exactly on the targets that lost their last visible
jurisprudence link, CORRELATA files byte-identical, ENTENDA flags (E/B, X) and W untouched.
Output: JURISPRUDENCE_AUDIT/J1_1_ISOLATION_AUDIT.json.   Usage: python build_j1_1_isolation_audit.py [--check]
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / 'REFERENCE_COVERAGE_AUDIT/REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1'
BASE_REL = ROOT / 'CORRELATA_COVERAGE_AUDIT/C3B2_PHYSICAL_TEST_PACKAGE/candidate/SD/99_RELATIONS_V2/05_INDICES_ESP32_V2'
CAND = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run6_juris_j1_candidate/device_ready'
EXCL = ROOT / 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J1.json'
OUT = HERE / 'J1_1_ISOLATION_AUDIT.json'
FLAGS = ('E', 'C', 'J', 'W', 'R', 'X')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rows(b):
    return [l.split('|') for l in b.decode('utf-8').split('\n') if l and not l.startswith('#')]


def audit():
    pb, pc = (rows(p.read_bytes()) for p in (BASE / '20_REFERENCES/REF_PAYLOAD.IDX', CAND / 'REF_PAYLOAD.IDX'))
    tb, tc = ({r[0]: r for r in rows(p.read_bytes())} for p in (BASE / '10_TARGETS/CF88_TARGETS.IDX', CAND / 'CF88_TARGETS.IDX'))
    lb, lc = ({r[0]: int(r[2]) for r in rows(p.read_bytes())} for p in (BASE / '20_REFERENCES/REF_LOOKUP.IDX', CAND / 'REF_LOOKUP.IDX'))
    excl = json.loads(EXCL.read_text(encoding='utf-8'))['records']
    want = {r['reference_id'] for r in excl}
    by = lambda rs, t: {tuple(r) for r in rs if r[1] == t}  # noqa: E731
    per = {t: dict(base=len(by(pb, t)), candidate=len(by(pc, t)), removed=sorted(r[4] for r in by(pb, t) - by(pc, t)),
                   added=sorted(r[4] for r in by(pc, t) - by(pb, t))) for t in ('CORRELATA', 'JURISPRUDENCE', 'WORK_REFERENCE')}
    jb, jc = by(pb, 'JURISPRUDENCE'), by(pc, 'JURISPRUDENCE')
    vis_j = {r[0] for r in jc if r[2] == 'CURRENT_VISIBLE'}
    changes = collections.defaultdict(list)
    for t in tb:
        if tb[t][:3] != tc[t][:3]:
            changes['FIELDS'].append(t)
        for i, n in enumerate(FLAGS):
            if tb[t][3][i] != tc[t][3][i]:
                changes[n].append(dict(target_id=t, before=tb[t][3], after=tc[t][3]))
    lost_last = sorted({r[0] for r in jb - jc} - vis_j)
    rel = {n: sha((BASE_REL / n).read_bytes()) == sha((CAND / n).read_bytes()) for n in ('RELACOES.IDX', 'REL_LOOKUP.IDX', 'EXT_ARTIGOS.IDX')}
    lookup_removed = sorted(set(lb) - set(lc))
    v = dict(
        CORRELATA_RELATION_SET_CHANGED=len(by(pb, 'CORRELATA') ^ by(pc, 'CORRELATA')),
        WORK_REFERENCE_SET_CHANGED=len(by(pb, 'WORK_REFERENCE') ^ by(pc, 'WORK_REFERENCE')),
        JURIS_REMOVED=len(jb - jc), JURIS_ADDED_OR_ALTERED=len(jc - jb),
        JURIS_REMOVED_EQUALS_RATIFIED_20={r[4] for r in jb - jc} == want and len(want) == 20,
        J_FLAGS_CHANGED=len(changes['J']), J_FLAG_CHANGES_ONLY_LOST_LAST_LINK={c['target_id'] for c in changes['J']} == set(lost_last)
        and all(c['after'][2] == '-' for c in changes['J']),
        C_FLAGS_CHANGED=len(changes['C']), E_FLAGS_CHANGED=len(changes['E']), W_FLAGS_CHANGED=len(changes['W']),
        R_FLAGS_CHANGED=len(changes['R']), X_FLAGS_CHANGED=len(changes['X']), NON_FLAG_FIELDS_CHANGED=len(changes['FIELDS']),
        NON_J_TARGET_FLAGS_CHANGED=sum(len(changes[n]) for n in FLAGS if n != 'J') + len(changes['FIELDS']),
        J_FLAG_EQUALS_VISIBLE_JURIS={t for t, r in tc.items() if r[3][2] == 'J'} == vis_j,
        CORRELATA_FILES_BYTE_IDENTICAL=all(rel.values()),
        HISTORICAL_HIDDEN_JURIS_UNCHANGED={r for r in jb if r[2] != 'CURRENT_VISIBLE'} == {r for r in jc if r[2] != 'CURRENT_VISIBLE'})
    return dict(artifact='J1_1_ISOLATION_AUDIT', base='pacote físico aprovado lex-device-v1-references4-physical-approved-2026-10-16',
                candidate=CAND.relative_to(ROOT).as_posix(), ref_payload_by_type=per,
                targets=dict(rows=len(tc), same_target_set=set(tb) == set(tc), j_before=sum(r[3][2] == 'J' for r in tb.values()),
                             j_after=sum(r[3][2] == 'J' for r in tc.values()), j_changes=changes['J'], targets_lost_last_juris=lost_last),
                ref_lookup=dict(rows_before=len(lb), rows_after=len(lc), removed_rows=lookup_removed,
                                count_changed=sorted(t for t in set(lb) & set(lc) if lb[t] != lc[t])),
                r_flag_note=f'R ([4], não lido pelo firmware) mantido como aprovado: {len(lookup_removed)} targets deixam de ter linha no REF_LOOKUP '
                            'e continuam com R (mesma política de C3B.2 e R1; dívida conhecida).',
                verdict=v)


def render():
    return (json.dumps(audit(), ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = render()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    print(json.dumps(json.loads(b)['verdict'], indent=1))
