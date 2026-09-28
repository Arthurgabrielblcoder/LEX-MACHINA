"""Rebuild the ORIGINAL protected545 layout from ORIGINAL PROOF + RELOCATION LEDGER into a fresh directory (copy only).

Frozen legacy tools (r1d_support.integrity(), consolidate_labels.py, compare_pilot*.py, run_regression*.py, ...) resolve
protected members as ROOT.parent/<original path>. After a relocation they must not be edited (they belong to the frozen
V2 set); instead they run against this reconstructed view, where every occurrence is back at its original relative path.
Refuses to run unless the derived verifier passes; refuses an existing target; re-hashes every copied file.
Usage: python materialize_legacy_view.py --bind REPO_ROOT=<repo> --bind P545_ARCHIVE=<archive> --ledger L.json --target <new dir>
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_relocation as vr  # noqa: E402


def materialize(proof, bindings, ledger, target, expected_head=None):
    target = Path(target)
    if target.exists():
        raise SystemExit('target exists: refusing to overwrite ' + str(target))
    res = vr.verify(proof, bindings, ledger, None, expected_head)
    if res['result'] != 'PASS':
        raise SystemExit('derived verifier FAIL: refusing to materialize ' + str(res['counts']))
    copied = 0
    for rec in res['occurrences']:
        src = vr.physical(bindings, rec['current_location'])
        dst = target / rec['original_path']
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if vr.file_sha256(dst) != rec['original_sha256'] or dst.stat().st_size != rec['original_size']:
            raise SystemExit('copy verification failed: ' + rec['original_path'])
        copied += 1
    pdst = target / proof
    pdst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(bindings['REPO_ROOT']) / proof, pdst)
    return dict(result='PASS', occurrences=copied, target=str(target), relocated=res['counts'].get('VALID_RELOCATION', 0))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--proof', default='LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/INTEGRITY_BEFORE.json')
    ap.add_argument('--bind', action='append', default=[])
    ap.add_argument('--ledger', type=Path, required=True)
    ap.add_argument('--expected-ledger-head')
    ap.add_argument('--target', type=Path, required=True)
    a = ap.parse_args()
    print(materialize(a.proof, dict(b.split('=', 1) for b in a.bind), vr.load_json(a.ledger), a.target, a.expected_ledger_head))


if __name__ == '__main__':
    main()
