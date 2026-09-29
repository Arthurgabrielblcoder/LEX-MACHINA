"""Apply a human review to a pending ENTENDA batch (editorial tool; the original drafts/corpus are never modified).

Input:  a review spec (JSON) with, per target, the decision and the literal before/after edits, plus new explanations
        created by the review. Output: the reviewed editorial source (HUMAN_APPROVED_T1, adjusted entries bumped to a new
        editorial_version) and HUMAN_REVIEW_DECISIONS.json with the original and final texts of every changed section.
Usage: python apply_batch_review.py <review_spec.json>
"""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEXT = ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao')


def _dump(obj, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes((json.dumps(obj, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))


def apply(spec_path):
    spec = json.loads(Path(spec_path).read_text(encoding='utf-8'))
    base = Path(spec_path).parent
    orig = json.loads((base / spec['original_drafts']).read_text(encoding='utf-8'))
    out = copy.deepcopy(orig)
    by = {e['target_id']: e for e in out['explanations']}
    reviewed = {r['target_id']: r for r in spec['reviews']}
    if sorted(reviewed) != sorted(by):
        raise SystemExit(f'REVIEW_INCOMPLETE: {sorted(set(by) ^ set(reviewed))}')
    decisions = []
    for e in orig['explanations']:
        tid = e['target_id']
        r = reviewed[tid]
        cur = by[tid]
        changes = []
        for ed in r.get('edits', []):
            sec = ed['section']
            if sec in TEXT:
                before = cur['content'][sec]
                if before.count(ed['before']) != 1:
                    raise SystemExit(f'EDIT_NOT_FOUND {tid} {sec}: {ed["before"][:60]}')
                cur['content'][sec] = before.replace(ed['before'], ed['after'])
            elif sec == 'palavras_dificeis':
                terms = cur['content'][sec]
                hit = [t for t in terms if t['termo'] == ed['termo']]
                if ed.get('add'):
                    if hit:
                        raise SystemExit(f'TERM_EXISTS {tid} {ed["termo"]}')
                    terms.append(dict(termo=ed['termo'], explicacao=ed['after']))
                else:
                    if len(hit) != 1 or hit[0]['explicacao'] != ed['before']:
                        raise SystemExit(f'TERM_NOT_FOUND {tid} {ed["termo"]}')
                    hit[0]['explicacao'] = ed['after']
            elif sec == 'external_layer_notes':
                notes = cur.setdefault('external_layer_notes', [])
                if ed.get('before') is None:
                    notes.append(ed['after'])
                elif notes.count(ed['before']) != 1:
                    raise SystemExit(f'NOTE_NOT_FOUND {tid}: {ed["before"][:60]}')
                else:
                    notes[notes.index(ed['before'])] = ed['after']
            elif sec == 'temporal':
                if cur.get('temporal') is not None and ed.get('before') != cur['temporal']:
                    raise SystemExit(f'TEMPORAL_MISMATCH {tid}')
                cur['temporal'] = ed['after']
            else:
                raise SystemExit(f'UNKNOWN_SECTION {sec}')
            changes.append(dict(section=sec, termo=ed.get('termo'), before=ed.get('before'), after=ed['after'], kind=ed.get('kind', 'HUMAN_REQUESTED')))
        if r.get('display_topic'):
            cur['display_topic'] = r['display_topic']
        adjusted = bool(changes)
        if adjusted:
            cur['editorial_version'] = e.get('editorial_version', 1) + 1
        if r['decision'] != ('APPROVED_AFTER_ADJUSTMENT' if adjusted else 'APPROVED'):
            raise SystemExit(f'DECISION_INCONSISTENT {tid}: {r["decision"]} com {len(changes)} edicoes')
        decisions.append(dict(target_id=tid, decision=r['decision'], review_reason=r['review_reason'],
                              changed_sections=sorted({c['section'] for c in changes}),
                              from_explanation_id=f"ENTENDA/{tid}/{e.get('variant', 'BASE')}/{e.get('editorial_version', 1)}",
                              to_explanation_id=f"ENTENDA/{tid}/{e.get('variant', 'BASE')}/{cur.get('editorial_version', 1)}",
                              changes=changes, original_content=e['content'] if adjusted else None,
                              original_external_layer_notes=e.get('external_layer_notes', []) if adjusted else None))
    for n in spec.get('new_explanations', []):
        if n['target_id'] in by:
            raise SystemExit(f'NEW_ALREADY_EXISTS {n["target_id"]}')
        entry = {k: v for k, v in n.items() if k not in ('review_reason',)}
        out['explanations'].append(entry)
        decisions.append(dict(target_id=n['target_id'], decision='APPROVED', review_reason=n['review_reason'], changed_sections=[],
                              from_explanation_id=None, to_explanation_id=f"ENTENDA/{n['target_id']}/BASE/1", origin='CREATED_BY_HUMAN_REVIEW',
                              changes=[], original_content=None, original_external_layer_notes=None))
    out['review_status'] = 'HUMAN_APPROVED_T1'
    out['human_review'] = dict(spec['human_review'])
    out['supersedes_drafts'] = spec['original_drafts']
    counts = {}
    for d in decisions:
        counts[d['decision']] = counts.get(d['decision'], 0) + 1
    doc = dict(schema_version=1, batch_id=spec['batch_id'], review_date=spec['human_review']['reviewed_on'], review_status='HUMAN_REVIEW_COMPLETED',
               original_drafts=spec['original_drafts'], original_drafts_preserved=True, decision_counts=dict(sorted(counts.items())),
               created_by_review=[n['target_id'] for n in spec.get('new_explanations', [])], decisions=decisions)
    if spec.get('decisions_schema', 1) >= 2:  # batch 03+: scope and hashes of the evidence handed to the reviewer
        doc = dict(doc, schema_version=2, review_scope=spec['review_scope'], original_evidence_sha256=spec['evidence_sha256'])
    for p in spec['decisions_out']:
        _dump(doc, base / p)
    _dump(out, base / spec['reviewed_drafts_out'])
    return doc


if __name__ == '__main__':
    d = apply(sys.argv[1])
    print(json.dumps(dict(decisions=len(d['decisions']), counts=d['decision_counts'], created=d['created_by_review']), ensure_ascii=False))
