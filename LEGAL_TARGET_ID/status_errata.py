"""CF88 target status errata: corrected status rows layered over the frozen derived/CF88_TARGET_STATUS.json.

The frozen status file is a pinned input of already produced artifacts (DEVICE exports run1/run2/run3, editorial batch manifests), so it is
never rewritten. Corrections found later go to derived/CF88_TARGET_STATUS_ERRATA.json, which is fully reproducible from Git:

  frozen   = reference_canonicalization.build_status(errata=False)   (must reproduce the frozen file, fail closed)
  corrected = reference_canonicalization.build_status(errata=True)   (approved source corrections + renumbered-label comparison fix)
  errata   = every target whose status/reason differs between the two, with both rows and the cause.

Consumers that want the corrected status load the frozen file and apply the errata with `overlay()`, which checks the frozen file sha256.
The operational text (git-ignored) must be present: materialize it first with the text source reconstruction tool (byte-exact recipe).

Usage: python status_errata.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference_canonicalization as RC  # noqa: E402
import source_corrections as SC  # noqa: E402

FROZEN = HERE / 'derived/CF88_TARGET_STATUS.json'
ERRATA = HERE / 'derived/CF88_TARGET_STATUS_ERRATA.json'
OPERATIONAL_REL = RC.OPERATIONAL.relative_to(RC.REPO).as_posix()   # recorded path (the bytes may come from a byte-exact reconstruction)


class StatusErrataError(RuntimeError):
    pass


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _cause(tid, old, new, corrections):
    for c in corrections:
        if c.get('target_hint') and (tid == c['target_hint'] or tid.startswith(c['target_hint'] + ':')):
            return dict(kind='SOURCE_TEXT_CORRECTION', correction_id=c['correction_id'])
    if new['status'] == 'HISTORICAL_ONLY' and new['reason'].startswith('rotulo renumerado'):
        return dict(kind='RENUMBERED_LABEL_FINAL_PUNCTUATION',
                    note='mesmo texto sob outro rotulo vigente; a pontuacao final nao faz parte da redacao')
    raise StatusErrataError(f'ERRATA_WITHOUT_CAUSE {tid}: {old} -> {new}')


def build():
    if not RC.OPERATIONAL.is_file():
        raise StatusErrataError(f'OPERATIONAL_TEXT_ABSENT {OPERATIONAL_REL}: materialize-o pela receita de reconstrucao')
    frozen_bytes = FROZEN.read_bytes()
    frozen = json.loads(frozen_bytes)['targets']
    _, tg, text = RC.load_targets()
    legacy = RC.build_status(tg, text, errata=False)
    if legacy != frozen:
        raise StatusErrataError('FROZEN_STATUS_NOT_REPRODUCED: o build legado nao reproduz derived/CF88_TARGET_STATUS.json')
    fixed = RC.build_status(tg, text, errata=True)
    corrections = [c for c in SC.load() if c.get('norm_id') == 'CF88' and c.get('status') == 'APPROVED']
    rows = {}
    for tid in sorted(set(frozen) | set(fixed)):
        old, new = frozen.get(tid), fixed.get(tid)
        if old != new:
            rows[tid] = dict(frozen=old, corrected=new, cause=_cause(tid, old, new, corrections))
    op = RC.OPERATIONAL.read_bytes()
    return dict(schema_version=1, norma_id='CF88', base_status_file=FROZEN.relative_to(RC.REPO).as_posix(),
                base_status_sha256=_sha(frozen_bytes), operational_source=OPERATIONAL_REL,
                operational_sha256=_sha(op), source_corrections=SC.REGISTRY.relative_to(RC.REPO).as_posix(),
                source_corrections_sha256=_sha(SC.REGISTRY.read_bytes()), count=len(rows), targets=rows)


def dumps(doc):
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def overlay(status_targets, base_bytes, errata_path=ERRATA):
    """Returns a copy of the frozen status rows with the errata applied. Fail closed if the errata was built on another base."""
    if not Path(errata_path).is_file():
        return dict(status_targets), {}
    doc = json.loads(Path(errata_path).read_text(encoding='utf-8'))
    if doc['base_status_sha256'] != _sha(base_bytes):
        raise StatusErrataError('ERRATA_BASE_MISMATCH: errata construida sobre outro CF88_TARGET_STATUS.json')
    out = dict(status_targets)
    for tid, row in doc['targets'].items():
        if out.get(tid) != row['frozen']:
            raise StatusErrataError(f'ERRATA_ROW_MISMATCH {tid}')
        out[tid] = row['corrected']
    return out, doc['targets']


def main(argv):
    data = dumps(build())
    if '--check' in argv:
        ok = ERRATA.is_file() and ERRATA.read_bytes() == data
        print('ERRATA_UP_TO_DATE' if ok else 'ERRATA_STALE')
        return 0 if ok else 1
    ERRATA.write_bytes(data)
    print(f'{ERRATA.relative_to(RC.REPO).as_posix()}: {json.loads(data)["count"]} correcoes')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
