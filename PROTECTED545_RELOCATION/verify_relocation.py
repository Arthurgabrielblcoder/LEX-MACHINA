"""Derived protected545 verifier: ORIGINAL PROOF + RELOCATION LEDGER + current filesystem.

Never modifies the original proof. For each of the proof's occurrences it reports one status:
  ORIGINAL_PATH_PRESENT  file at the original path, sha256/size equal to the proof, no active relocation
  VALID_RELOCATION       original path absent, unambiguous ledger lineage, file at final location with equal sha256/size
  MISSING                expected file absent (original without ledger, or relocation destination)
  HASH_MISMATCH          file present but sha256 or size differs from the proof
  AMBIGUOUS_RELOCATION   branching lineage, or more than one physical copy claims the occurrence
  INVALID_LINEAGE        broken chain for this occurrence (wrong from, cycle, bad rollback, wrong occurrence, unsafe path)
The overall result is PASS only if the ledger is intact and every occurrence is ORIGINAL_PATH_PRESENT or VALID_RELOCATION.
Fail-closed: any ledger corruption makes the whole result FAIL.
"""
import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import relocation_ledger as rl  # noqa: E402

OK = ('ORIGINAL_PATH_PRESENT', 'VALID_RELOCATION')


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_bytes().decode('utf-8-sig'))


def check_ledger(ledger, proof_rel, proof_sha, expected_head):
    """Return list of ledger-level errors (hash chain, head, seq, header binding)."""
    errors = []
    for key in ('header', 'events', 'head'):
        if key not in ledger:
            return ['LEDGER_CORRUPT:missing_' + key]
    header = ledger['header']
    if header.get('schema_version') != rl.SCHEMA_VERSION:
        errors.append('LEDGER_CORRUPT:schema_version')
    op = header.get('original_proof', {})
    if op.get('relative_path') != proof_rel or op.get('sha256') != proof_sha or op.get('root_id') != rl.PROOF_ROOT_ID:
        errors.append('LEDGER_CORRUPT:original_proof_binding')
    prev = rl.sha256_bytes(rl.canonical(header))
    for i, ev in enumerate(ledger['events'], 1):
        if ev.get('seq') != i:
            errors.append(f'LEDGER_CORRUPT:seq_at_{i}')
        if ev.get('prev_event_hash') != prev:
            errors.append(f'LEDGER_CORRUPT:prev_hash_at_{i}')
        if rl.event_hash(ev) != ev.get('event_hash'):
            errors.append(f'LEDGER_CORRUPT:event_hash_at_{i}')
        prev = ev.get('event_hash')
    head = ledger['head']
    if head.get('count') != len(ledger['events']) or head.get('event_hash') != prev:
        errors.append('LEDGER_TRUNCATED_OR_CORRUPT:head_mismatch')
    if expected_head and (head.get('event_hash') != expected_head):
        errors.append('LEDGER_TRUNCATED_OR_CORRUPT:anchor_mismatch')
    return errors


def physical(bindings, loc):
    return Path(bindings[loc['root_id']]).joinpath(*loc['relative_path'].split('/'))


def verify(proof_path, bindings, ledger=None, expected_proof_sha256=None, expected_head=None):
    repo = Path(bindings[rl.PROOF_ROOT_ID])
    proof_file = repo / proof_path
    proof_sha = file_sha256(proof_file)
    result = dict(original_proof=dict(relative_path=proof_path, sha256=proof_sha), ledger_errors=[], occurrences=[])
    if expected_proof_sha256 and proof_sha != expected_proof_sha256:
        result['ledger_errors'].append('ORIGINAL_PROOF_HASH_MISMATCH')
    entries = load_json(proof_file)['files']
    by_id = {}
    for e in entries:
        by_id[rl.occurrence_id(e)] = e
    events = []
    if ledger is not None:
        result['ledger_errors'] += check_ledger(ledger, proof_path, proof_sha, expected_head)
        result['ledger_head'] = ledger.get('head')
        events = ledger.get('events', [])
        declared_roots = set(ledger.get('header', {}).get('roots', [])) | {rl.PROOF_ROOT_ID}
    per_occ = {}
    for ev in events:
        per_occ.setdefault(ev.get('occurrence_id'), []).append(ev)
    for oid in per_occ:
        if oid not in by_id:
            result['ledger_errors'].append('UNKNOWN_OCCURRENCE:' + str(oid))
    final_locations = {}
    for oid, entry in by_id.items():
        orig = dict(root_id=rl.PROOF_ROOT_ID, relative_path=entry['path'])
        rec = dict(occurrence_id=oid, original_path=entry['path'], original_sha256=entry['sha256'], original_size=entry['bytes'],
                   lineage=[], problems=[])
        stack = [orig]
        visited_left = set()
        for ev in per_occ.get(oid, []):
            f, t = ev.get('from_location') or {}, ev.get('to_location') or {}
            rec['lineage'].append(dict(seq=ev.get('seq'), event_type=ev.get('event_type'), from_location=f, to_location=t,
                                       event_hash=ev.get('event_hash')))
            o = ev.get('original') or {}
            if (o.get('relative_path'), o.get('sha256'), o.get('size')) != (entry['path'], entry['sha256'], entry['bytes']) \
                    or ev.get('post_move_sha256') != entry['sha256'] or ev.get('post_move_size') != entry['bytes']:
                rec['problems'].append('WRONG_OCCURRENCE')
            for loc in (f, t):
                err = rl.check_relative_path(loc.get('relative_path'))
                if err:
                    rec['problems'].append('UNSAFE_PATH:' + err)
                if loc.get('root_id') not in declared_roots or loc.get('root_id') not in bindings:
                    rec['problems'].append('UNKNOWN_ROOT:' + str(loc.get('root_id')))
            if rec['problems']:
                break
            cur = stack[-1]
            if ev.get('event_type') == 'RELOCATE':
                if rl.location_key(f) != rl.location_key(cur):
                    code = 'AMBIGUOUS_BRANCH' if rl.location_key(f) in visited_left else 'BROKEN_LINEAGE'
                    rec['problems'].append(code)
                    break
                if rl.location_key(t) in {rl.location_key(x) for x in stack}:
                    rec['problems'].append('CYCLE')
                    break
                visited_left.add(rl.location_key(cur))
                stack.append(t)
            elif ev.get('event_type') == 'ROLLBACK':
                if len(stack) < 2 or rl.location_key(f) != rl.location_key(cur) or rl.location_key(t) != rl.location_key(stack[-2]):
                    rec['problems'].append('INVALID_ROLLBACK')
                    break
                stack.pop()
            else:
                rec['problems'].append('UNKNOWN_EVENT_TYPE')
                break
        final = stack[-1]
        rec['current_location'] = final
        if rec['problems']:
            rec['status'] = 'AMBIGUOUS_RELOCATION' if 'AMBIGUOUS_BRANCH' in rec['problems'] else 'INVALID_LINEAGE'
        else:
            p = physical(bindings, final)
            if not p.is_file():
                rec['status'] = 'MISSING'
            else:
                size, digest = p.stat().st_size, file_sha256(p)
                if size != entry['bytes']:
                    rec['status'], rec['problems'] = 'HASH_MISMATCH', ['SIZE_MISMATCH']
                elif digest != entry['sha256']:
                    rec['status'], rec['problems'] = 'HASH_MISMATCH', ['SHA256_MISMATCH']
                else:
                    rec['status'] = 'ORIGINAL_PATH_PRESENT' if len(stack) == 1 else 'VALID_RELOCATION'
            if len(stack) > 1:
                others = [x for x in stack[:-1] if physical(bindings, x).exists()]
                if others and rec['status'] in OK:
                    rec['status'], rec['problems'] = 'AMBIGUOUS_RELOCATION', ['STALE_COPY_AT:' + rl.location_key(others[0])]
        key = unicodedata.normalize('NFC', rl.location_key(final)).casefold()
        final_locations.setdefault(key, []).append(oid)
        result['occurrences'].append(rec)
    collisions = {k: v for k, v in final_locations.items() if len(v) > 1}
    for rec in result['occurrences']:
        key = unicodedata.normalize('NFC', rl.location_key(rec['current_location'])).casefold()
        if key in collisions:
            rec['status'] = 'AMBIGUOUS_RELOCATION'
            rec['problems'].append('LOCATION_COLLISION_CASEFOLD_NFC')
    counts = {}
    for rec in result['occurrences']:
        counts[rec['status']] = counts.get(rec['status'], 0) + 1
    result['counts'] = dict(sorted(counts.items()))
    result['total'] = len(result['occurrences'])
    result['result'] = 'PASS' if not result['ledger_errors'] and all(r['status'] in OK for r in result['occurrences']) else 'FAIL'
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--proof', default='LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/INTEGRITY_BEFORE.json')
    ap.add_argument('--expected-proof-sha256')
    ap.add_argument('--ledger', type=Path)
    ap.add_argument('--expected-ledger-head')
    ap.add_argument('--bind', action='append', default=[], help='ROOT_ID=absolute_path (REPO_ROOT required)')
    ap.add_argument('--output', type=Path)
    a = ap.parse_args()
    bindings = dict(b.split('=', 1) for b in a.bind)
    if rl.PROOF_ROOT_ID not in bindings:
        ap.error('--bind REPO_ROOT=<path> is required')
    ledger = load_json(a.ledger) if a.ledger else None
    res = verify(a.proof, bindings, ledger, a.expected_proof_sha256, a.expected_ledger_head)
    if a.output:
        a.output.write_bytes(json.dumps(res, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')
    print(json.dumps(dict(result=res['result'], total=res['total'], counts=res['counts'], ledger_errors=res['ledger_errors'][:10],
                          original_proof_sha256=res['original_proof']['sha256']), ensure_ascii=False, indent=1))
    return 0 if res['result'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
