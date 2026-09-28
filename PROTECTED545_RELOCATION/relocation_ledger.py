"""Append-only, hash-chained relocation ledger for protected545 occurrences.

The original proof (LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/INTEGRITY_BEFORE.json) is never modified. This ledger
is a second, derived layer: each event records that one historical occurrence of the original proof moved from one
location to another (RELOCATE) or back (ROLLBACK). Identity of an occurrence is the original proof entry
(original path + sha256 + size), never the hash alone.
"""
import hashlib
import json
import unicodedata

SCHEMA_VERSION = 1
PROOF_ROOT_ID = 'REPO_ROOT'
EVENT_TYPES = ('RELOCATE', 'ROLLBACK')


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def occurrence_id(entry):
    """Deterministic id of one historical occurrence of the original proof."""
    key = 'INTEGRITY_BEFORE\0' + entry['path'] + '\0' + entry['sha256'] + '\0' + str(entry['bytes'])
    return 'p545-' + sha256_bytes(key.encode('utf-8'))[:24]


def check_relative_path(path):
    """Return an error code for an unsafe relative path, or None."""
    if not isinstance(path, str) or not path:
        return 'EMPTY_PATH'
    if '\\' in path or path.startswith('/') or (len(path) > 1 and path[1] == ':'):
        return 'ABSOLUTE_OR_BACKSLASH_PATH'
    if any(part in ('', '.', '..') for part in path.split('/')):
        return 'PATH_TRAVERSAL'
    if unicodedata.normalize('NFC', path) != path:
        return 'NON_NFC_PATH'
    return None


def location_key(location):
    return location['root_id'] + ':' + location['relative_path']


def new_ledger(ledger_id, proof_path, proof_sha256, roots):
    header = dict(schema_version=SCHEMA_VERSION, ledger_id=ledger_id,
                  original_proof=dict(root_id=PROOF_ROOT_ID, relative_path=proof_path, sha256=proof_sha256),
                  roots=sorted(roots))
    genesis = sha256_bytes(canonical(header))
    return dict(header=header, events=[], head=dict(count=0, event_hash=genesis))


def event_hash(event):
    return sha256_bytes(canonical({k: v for k, v in event.items() if k != 'event_hash'}))


def append_event(ledger, event_type, entry, from_loc, to_loc, reason, source_manifest, batch=None):
    """Append one event; never edits previous events."""
    if event_type not in EVENT_TYPES:
        raise ValueError(event_type)
    event = dict(seq=len(ledger['events']) + 1, event_type=event_type, occurrence_id=occurrence_id(entry),
                 original=dict(root_id=PROOF_ROOT_ID, relative_path=entry['path'], sha256=entry['sha256'], size=entry['bytes']),
                 from_location=from_loc, to_location=to_loc, post_move_sha256=entry['sha256'], post_move_size=entry['bytes'],
                 byte_identity_verified=True, reason=reason, source_manifest=source_manifest,
                 batch=batch, prev_event_hash=ledger['head']['event_hash'])
    event['event_hash'] = event_hash(event)
    ledger['events'].append(event)
    ledger['head'] = dict(count=len(ledger['events']), event_hash=event['event_hash'])
    return event


def dump(ledger, path):
    with open(path, 'wb') as fh:
        fh.write(json.dumps(ledger, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8') + b'\n')
