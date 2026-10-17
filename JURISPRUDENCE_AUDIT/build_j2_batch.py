"""J2 — generic, reusable batch builder for Batches 03+ (HIGH, then MEDIUM, then LOW). Host-only, read-only, deterministic, no network.

State model (never mixed):
  PHYSICALLY_INSTALLED              J2C card: J2B_1_CANDIDATE_HOST_ONLY REF_PAYLOAD (261/160)
  EDITORIALLY_APPROVED_HOST_ONLY    ratified decisions not installed: Batch02 relations (CF88_JURIS_ADDITIONS_J2E.json, variants A+B)
  UNAPPROVED_RESEARCH_PROPOSAL      Batch03+ decisions (AWAITING_USER_RATIFICATION) — excluded from re-selection, never treated as links
Queue = J0 categories (re-run over the installed 261) − recommendations decided in any batch (ratified or not) − recommendations whose
(target, identifier) is already covered by a ratified decision or an editorially approved relation. Priority = the J0 rule, unchanged
(named identifier, recurrence, article without jurisprudence, reference described; HIGH >= 3), with article coverage = installed +
editorially approved relations (documented choice: an approved-but-not-installed link still answers the "article gap" question).
Selection = J2D order. Level: --level HIGH|MEDIUM|LOW; only that level is selected (no padding with a lower level).
Writes <dir>/J2_BATCH<NN>_DECISIONS.json, merging the review module <dir>/j2_batch<NN>_review.py when it exists.
Usage: python build_j2_batch.py --batch N --level HIGH [--check] [--selection-only]
"""
import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_j2a_batch01 as B  # noqa: E402
import build_j2d_batch02 as D2  # noqa: E402
import build_j0_diagnostic_audit as J0  # noqa: E402

HIGH_DIR = HERE / 'J2_HIGH_BACKLOG'
LEVEL_DIR = {'HIGH': HIGH_DIR, 'MEDIUM': HERE / 'J2_MEDIUM_BACKLOG', 'LOW': HERE / 'J2_LOW_BACKLOG'}
J2E = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2E.json'
RATIFIED = {1: HIGH_DIR / 'J2A_BATCH01_DECISIONS.json', 2: HIGH_DIR / 'J2D_BATCH02_DECISIONS.json'}
BATCH_SIZE = 10


def batch_file(n):
    if n in RATIFIED:
        return RATIFIED[n]
    for d in LEVEL_DIR.values():
        p = d / f'J2_BATCH{n:02d}_DECISIONS.json'
        if p.is_file():
            return p
    return None


def previous_batches(n):
    out = {}
    for k in range(1, n):
        p = batch_file(k)
        if p is None:
            raise SystemExit(f'MISSING_PREVIOUS_BATCH {k}')
        out[k] = json.loads(p.read_text(encoding='utf-8'))
    return out


def _num(s):
    m = re.search(r'(\d[\d-]*)$', s.split(':')[-1] if ':' in s else s)
    return m.group(1).split('-') if m else []


def reconstruct(n):
    original = B.current_baseline
    B.current_baseline = D2.current_baseline                    # installed 261 (J2C)
    try:
        items, _, j0 = B.reconstruct()
    finally:
        B.current_baseline = original
    installed = D2.current_baseline()
    approved = json.loads(J2E.read_text(encoding='utf-8'))['records']
    prev = previous_batches(n)
    analyzed = {d['recommendation_id']: k for k, doc in prev.items() for d in doc['decisions']}
    ratified_pairs = set()
    for k in (1, 2):
        for d in prev[k]['decisions']:
            for t in [d['recommended_by_backlog'], d.get('recommended_target')] + list(d.get('additional_targets') or []):
                if t:
                    ratified_pairs.add((t, d['precedent']))
    ratified_pairs |= {(r['target_id'], r['source_id']) for r in approved}
    vis_targets = {r[0] for r in installed} | {r['target_id'] for r in approved}
    art_with = {':'.join(t.split(':')[:2]) for t in vis_targets}
    pending, covered = [], {}
    for b in items:
        if b['category'] != 'NEEDS_EXTERNAL_INGESTION' or b['recommendation_id'] in analyzed:
            continue
        ids = B.ids_in(f"{b['desired_reference']} {b['recommendation_text']}")
        nums = {x.replace('.', '') for i in ids for x in re.findall(r'\d[\d.]*', i)}
        ov = sorted(f'{t}|{p}' for t, p in ratified_pairs if t == b['target_id'] and set(_num(p)) & nums)
        done = {x for t, p in ratified_pairs if t == b['target_id'] for x in _num(p)}
        if ov and nums <= done:                          # covered only if EVERY identifier already has a ratified decision there
            covered[b['recommendation_id']] = dict(target=b['target_id'], covered_by=ov)
            continue
        pending.append(b)
    dup_desired = collections.Counter(J0.norm(b['desired_reference']) for b in pending)
    id_count = collections.Counter(i for b in pending for i in B.ids_in(f"{b['desired_reference']} {b['recommendation_text']}"))
    for b in pending:
        text = f"{b['desired_reference']} {b['recommendation_text'][:300]}"
        named = sorted({m.group(0).strip() for m in D2.J0_IDENT.finditer(text)})
        art_has = ':'.join(b['target_id'].split(':')[:2]) in art_with
        tgt_has = any(k in vis_targets for k in (b['target_id'], b['target_id'] + ':CAPUT', b['target_id'].removesuffix(':CAPUT')))
        recurrent = b['occurrences'] > 1 or dup_desired[J0.norm(b['desired_reference'])] > 1
        described = bool(b['desired_reference'] and b['desired_reference'] != 'IDENTIFICACAO_PENDENTE')
        score = (1 if named else 0) + (1 if recurrent else 0) + (0 if art_has else 1) + (1 if described else 0)
        b['priority'] = 'HIGH' if score >= 3 else 'MEDIUM' if score == 2 else 'LOW'
        b['priority_reason'] = dict(named_identifier=bool(named), recurrent=recurrent, article_without_juris=not art_has, reference_described=described)
        ref_ids = B.ids_in(b['desired_reference'] if described else '')
        all_ids = B.ids_in(f"{b['desired_reference']} {b['recommendation_text']}")
        b['suggested_identifiers'] = all_ids
        b['current_baseline_equivalent'] = dict(target_has_juris=tgt_has, article_has_juris=art_has,
                                                target_juris_installed=sorted(r[5] for r in installed if r[0] == b['target_id']),
                                                target_juris_approved_not_installed=sorted(r['source_id'] for r in approved if r['target_id'] == b['target_id']))
        b['selection_scores'] = {
            '1_explicit_identifier': 2 if len(ref_ids) == 1 else 1 if all_ids else 0,
            '2_direct_constitutional_weight': 2 if all_ids and all(B.GENERAL_EFFECT.match(i) for i in (ref_ids or all_ids)) else 1 if all_ids else 0,
            '3_target_without_juris': 0 if tgt_has else 1,
            '4_recurrence': 1 if b['occurrences'] > 1 or any(id_count[i] > 1 for i in all_ids) else 0,
            '5_practical_relevance': 0 if art_has else 1,
            '6_low_ambiguity': 1 if len(all_ids) == 1 and described else 0}
    return items, pending, analyzed, covered, prev


def build(n, level, selection_only=False):
    items, pending, analyzed, covered, prev = reconstruct(n)
    key = lambda b: tuple(-b['selection_scores'][k] for k in sorted(b['selection_scores'])) + (b['recommendation_id'],)  # noqa: E731
    lvl = sorted([b for b in pending if b['priority'] == level], key=key)
    chosen = [b['recommendation_id'] for b in lvl[:BATCH_SIZE]]
    cnt = collections.Counter(b['priority'] for b in pending)
    status = {k: ('RATIFIED' if k in (1, 2) else 'AWAITING_USER_RATIFICATION') for k in prev}
    last = prev[max(prev)]
    prev_level = {q['recommendation_id'] for q in last.get('queue') or last.get('high_queue') or []
                  if q['recommendation_id'] not in set(last['selected'])}
    now = {b['recommendation_id']: b for b in pending}
    transitions = {r: (dict(now='COVERED_BY_RATIFIED') if r in covered else
                       dict(now=now[r]['priority'], reason=now[r]['priority_reason'],
                            approved_links_on_article=now[r]['current_baseline_equivalent']['article_has_juris']))
                   for r in sorted(prev_level) if r not in now or now[r]['priority'] != level}
    doc = dict(schema_version=1, round='J2', batch=f'BATCH{n:02d}', level=level, mode='HOST_ONLY_DECISIONS_NO_MATERIALIZATION',
               status='AWAITING_USER_RATIFICATION',
               state_model=dict(PHYSICALLY_INSTALLED='J2C 261/160 (J2B_1 REF_PAYLOAD)',
                                EDITORIALLY_APPROVED_HOST_ONLY=f'Batch02 J2E: {len(json.loads(J2E.read_text(encoding="utf-8"))["records"])} relações (A+B)',
                                UNAPPROVED_RESEARCH_PROPOSAL=[f'BATCH{k:02d}' for k, s in status.items() if s != 'RATIFIED']),
               previous_batches=status,
               inputs={p.relative_to(ROOT).as_posix(): B.sha_lf(p) for p in [batch_file(k) for k in prev] + [J2E, B.J0_AUDIT]},
               reconstruction=dict(ANALYZED_IN_PREVIOUS_BATCHES=len(analyzed), COVERED_BY_RATIFIED=covered, BACKLOG_PENDING_CURRENT=len(pending),
                                   HIGH_CURRENT=cnt['HIGH'], MEDIUM_CURRENT=cnt['MEDIUM'], LOW_CURRENT=cnt['LOW'],
                                   WITHOUT_IDENTIFIER=sum(1 for b in pending if not b['suggested_identifiers']),
                                   LEFT_LEVEL_SINCE_PREVIOUS_BATCH=transitions),
               queue=[{k: b[k] for k in ('recommendation_id', 'target_id', 'desired_reference', 'origin', 'suggested_identifiers', 'priority_reason',
                                         'current_baseline_equivalent', 'selection_scores')} | dict(rank=i + 1, recommendation_text=b['recommendation_text'][:400])
                      for i, b in enumerate(lvl)],
               selected=chosen, LEVEL_REMAINING_AFTER_BATCH=len(lvl) - len(chosen))
    review = LEVEL_DIR[level] / f'j2_batch{n:02d}_review.py'
    if not selection_only and review.is_file():
        sys.path.insert(0, str(LEVEL_DIR[level]))
        R = __import__(f'j2_batch{n:02d}_review')
        decisions = R.decisions(doc)
        doc.update(sources=R.SOURCES, decisions=decisions, totals=dict(sorted(collections.Counter(d['decision'] for d in decisions).items())))
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', type=int, required=True)
    ap.add_argument('--level', choices=('HIGH', 'MEDIUM', 'LOW'), required=True)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--selection-only', action='store_true')
    a = ap.parse_args()
    b = build(a.batch, a.level, a.selection_only)
    out = LEVEL_DIR[a.level] / f'J2_BATCH{a.batch:02d}_DECISIONS.json'
    if a.selection_only:
        d = json.loads(b)
        print(json.dumps(dict(reconstruction={k: v for k, v in d['reconstruction'].items()}, selected=d['selected'],
                              remaining=d['LEVEL_REMAINING_AFTER_BATCH']), ensure_ascii=False, indent=1))
        for q in d['queue']:
            print(q['rank'], q['recommendation_id'], q['target_id'], q['suggested_identifiers'], list(q['selection_scores'].values()),
                  q['current_baseline_equivalent']['target_juris_installed'])
        return
    if a.check:
        ok = out.is_file() and out.read_bytes() == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(b)
    print(out.name, hashlib.sha256(b).hexdigest())


if __name__ == '__main__':
    main()
