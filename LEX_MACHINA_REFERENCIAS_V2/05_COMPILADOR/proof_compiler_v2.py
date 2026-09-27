"""Expanded runner reuses the frozen R1 proof interpreter, not alpha gates."""
import copy
from collections import defaultdict
from proof_compiler_r1 import evaluate_pair as interpret_proof, attach_historical_scores

VERSION='REFERENCE_PROOF_COMPILER_V2_EXPERIMENTAL_1'


def evaluate_pair(inp, device_id, work_id):
    row=interpret_proof(inp,device_id,work_id)
    row['compiler_version']=VERSION
    row['annotation_status']=inp.devices[device_id].get('annotation_status','PILOT')
    row['evidence_availability']={
        'validated_claims':sum(e['state']=='VALIDADA' for e in inp.works[work_id]['evidences']),
        'proven_claims':len({eid for p in row['proofs'] for eid in p['evidence_ids']})}
    return row


def run_pairs(inp,pairs):
    inp.assert_unchanged()
    rows=[evaluate_pair(inp,p['device_id'],p['work_id']) for p in pairs]
    inp.assert_unchanged()
    return rows


def iter_exhaustive(inp):
    inp.assert_unchanged()
    for did in sorted(inp.devices):
        for wid in sorted(inp.works):
            yield evaluate_pair(inp,did,wid)
    inp.assert_unchanged()


def rank_select(inp, rows, scores, per_device=3):
    """Never rescues inadmissible links. Missing historical score stays null.

    Media diversity is a deterministic tie-break after a first ranked candidate;
    no work/title/constitutional-address preference is permitted.
    """
    rows=attach_historical_scores(rows,scores)
    groups=defaultdict(list)
    for row in rows:
        if row['state']=='ADMISSIVEL' and row['editorial_score'] is not None and row['editorial_score']>=6:
            groups[row['device_id']].append(row)
    for group in groups.values():
        used=set()
        remaining=list(group)
        for _ in range(min(per_device,len(remaining))):
            remaining.sort(key=lambda r:(inp.works[r['work_id']]['tipo'] in used, -r['editorial_score'],r['work_id']))
            chosen=remaining.pop(0); chosen['selected']=True
            used.add(inp.works[chosen['work_id']]['tipo'])
    return rows
