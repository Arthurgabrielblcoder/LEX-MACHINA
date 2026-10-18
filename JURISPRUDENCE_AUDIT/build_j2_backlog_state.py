"""J2 — current backlog state of the CF/ADCT jurisprudence audit, recomputed from the batch files (never from historical counts).
Queue rule = build_j2_batch.reconstruct (J0 categories + the batch priority rule, coverage over J2I_FROZEN_315_198 for Batch10+).
Host-only, deterministic, read-only over its inputs.
Usage: python build_j2_backlog_state.py [--check]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_j2_batch as G  # noqa: E402

OUT = HERE / 'J2_BACKLOG_STATE.json'


def last_batch():
    n = 1
    while G.batch_file(n + 1) is not None:
        n += 1
    return n


def build():
    n = last_batch()
    items, pending, analyzed, covered, prev = G.reconstruct(n + 1)
    rat = G.ratified_03_09()
    rat_ids = {x['recommendation_id'] for x in rat['items'] if x['human_approved']}
    by_rec = {}
    for k, doc in sorted(prev.items()):
        for d in doc['decisions']:
            by_rec[d['recommendation_id']] = (k, d['decision'])
    human = {r for r, (k, _) in by_rec.items() if k in (1, 2) or r in rat_ids}
    awaiting = sorted(r for r, (k, _) in by_rec.items() if r not in human and r not in rat['ratification']['exceptions'])
    unresolved = collections.defaultdict(list)
    for r, (k, dec) in sorted(by_rec.items()):
        if dec.startswith('UNRESOLVED'):
            unresolved[dec].append(dict(recommendation_id=r, batch=f'BATCH{k:02d}', human_ratified_as_unresolved=r in rat['ratification']['exceptions']))
    cats = collections.Counter(b['category'] for b in items)
    pr = collections.Counter(b['priority'] for b in pending)
    doc = dict(schema_version=1, round='J2', kind='BACKLOG_STATE', physical_baseline='J2I_FROZEN_315_198', after_batch=f'BATCH{n:02d}',
               J0_CATEGORIES=dict(sorted(cats.items())),
               ALREADY_REVIEWED=len(by_rec), HUMAN_APPROVED=len(human), AWAITING_USER_RATIFICATION=len(awaiting),
               AWAITING_IDS=awaiting, COVERED_BY_RATIFIED_OR_INSTALLED=len(covered),
               UNRESOLVED=dict(sorted(unresolved.items())),
               UNRESOLVED_EXTERNAL=len(unresolved['UNRESOLVED_EXTERNAL']), UNRESOLVED_IDENTIFICATION=len(unresolved['UNRESOLVED_IDENTIFICATION']),
               PENDING_NOT_RESEARCHED=len(pending), HIGH_REMAINING=pr['HIGH'], MEDIUM_REMAINING=pr['MEDIUM'], LOW_REMAINING=pr['LOW'],
               WITHOUT_IDENTIFIER=sum(1 for b in pending if not b['suggested_identifiers']),
               decisions_by_type=dict(sorted(collections.Counter(d for _, d in by_rec.values()).items())),
               inputs={G.batch_file(k).relative_to(G.ROOT).as_posix(): G.B.sha_lf(G.batch_file(k)) for k in prev}
               | {G.RATIFICATION_03_09.relative_to(G.ROOT).as_posix(): G.B.sha_lf(G.RATIFICATION_03_09)})
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    b = build()
    if ap.parse_args().check:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    d = json.loads(b)
    print({k: v for k, v in d.items() if isinstance(v, int)})


if __name__ == '__main__':
    main()
