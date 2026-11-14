import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
OUT = HERE / "derived/qa07_high_findings_resolution"


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA07PreparationTest(unittest.TestCase):
    def test_authoritative_scope_and_nonoverlap(self):
        scope = load("QA07_AUTHORIZED_SCOPE.json")
        high = scope["high_groups"]["A"] + scope["high_groups"]["B"]
        indeterminate = scope["indeterminate"]
        self.assertEqual((len(high), len(indeterminate), scope["medium_total_preserved"]), (41, 10, 420))
        self.assertEqual(len({r["finding_id"] for r in high + indeterminate}), 51)
        self.assertEqual((len(scope["high_groups"]["A"]), len(scope["high_groups"]["B"])), (21, 20))

    def test_medium_manifest_is_exact_and_immutable(self):
        manifest = load("QA07_MEDIUM_420_PRESERVATION_MANIFEST.json")
        self.assertEqual(len(manifest["findings"]), 420)
        self.assertEqual(len({r["finding_id"] for r in manifest["findings"]}), 420)
        self.assertTrue(all(r["final_severity"] == "MÉDIO" for r in manifest["findings"]))
        self.assertFalse(manifest["editorial_changes_authorized"])
        self.assertFalse(manifest["corpus_modified"])

    def test_protected_hashes_and_checkpoint(self):
        cp = load("QA07_CP01.json")
        self.assertEqual(cp["status"], "INVENTORY_AND_INTEGRITY_COMPLETE")
        self.assertEqual(cp["protected_sha256"]["qa06_corpus"],
                         "4f7481e5ec697eddc26e5e412ff9f5394c983fcfbd5cff6b678bdb7d9811aaf5")
        self.assertEqual((cp["high"], cp["indeterminate"], cp["medium_preserved"]), (41, 10, 420))

    def test_preparation_is_byte_deterministic(self):
        paths = [OUT / name for name in ("QA07_AUTHORIZED_SCOPE.json",
                                         "QA07_MEDIUM_420_PRESERVATION_MANIFEST.json", "QA07_CP01.json")]
        before = [sha(path) for path in paths]
        subprocess.run([sys.executable, "-X", "utf8", str(HERE / "qa07_prepare.py")],
                       cwd=ROOT, check=True, capture_output=True)
        self.assertEqual(before, [sha(path) for path in paths])


if __name__ == "__main__":
    unittest.main()
