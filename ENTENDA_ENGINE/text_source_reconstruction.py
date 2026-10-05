"""Byte-exact reconstruction of git-ignored text sources from versioned content (editorial/TEXT_SOURCE_RECONSTRUCTION.json).

Used by entenda_engine.NormContext only when a configured text source file is absent (clean clone, cloud). Fail closed: the result
must hash to the registered sha256, otherwise ReconstructionError. Never edits law text.
Usage: python text_source_reconstruction.py [--materialize]   (verifies; --materialize also writes absent files at their configured path)
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RECIPES = HERE / 'editorial/TEXT_SOURCE_RECONSTRUCTION.json'


class ReconstructionError(RuntimeError):
    pass


def recipes(path=RECIPES):
    return json.loads(Path(path).read_text(encoding='utf-8'))['sources'] if Path(path).is_file() else {}


def reconstruct(rel_path, base=REPO):
    r = recipes().get(rel_path)
    if r is None:
        raise ReconstructionError(f'NO_RECIPE {rel_path}')
    body = (Path(base) / r['body']).read_bytes()
    if hashlib.sha256(body).hexdigest() != r['body_sha256']:
        raise ReconstructionError(f"BODY_SHA256_MISMATCH {r['body']}")
    data = r['header'].encode('utf-8') + body + r['suffix'].encode('utf-8')
    if hashlib.sha256(data).hexdigest() != r['sha256'] or len(data) != r['bytes']:
        raise ReconstructionError(f'RECONSTRUCTED_SHA256_MISMATCH {rel_path}')
    return data


def main(argv):
    out = {}
    for rel, r in recipes().items():
        p = REPO / rel
        data = reconstruct(rel)
        if p.is_file():
            out[rel] = 'PRESENT_IDENTICAL' if p.read_bytes() == data else 'PRESENT_DIFFERENT (arquivo local difere da receita; nada alterado)'
        elif '--materialize' in argv:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
            out[rel] = 'MATERIALIZED'
        else:
            out[rel] = 'ABSENT_RECONSTRUCTIBLE'
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(sys.argv[1:])
