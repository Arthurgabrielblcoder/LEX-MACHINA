import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ENTENDA_ENGINE"))

import entenda_engine as E  # noqa: E402
from cc02_editorial import CC05_HUMAN_APPROVED_TARGETS, CC05_OVERRIDES  # noqa: E402

BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
CORPUS = BATCH / "CC2002_CC02.entenda.jsonl"
BASELINE = BATCH / "CC2002_CC04_BASELINE.entenda.jsonl"
INDEX_SHA = {
    "ENTENDA_LOOKUP.IDX": "38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82",
    "ENTENDA_PAYLOAD.DAT": "6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638",
    "ENTENDA_BUILD_MANIFEST.json": "213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760",
}


def active(rows):
    return {r["target_id"]: r for r in rows if r["status"] == "ACTIVE"}


def content_hash(content):
    raw = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class CC05ConsolidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = E.load_corpus(CORPUS)
        cls.base_rows = E.load_corpus(BASELINE)
        cls.current = active(cls.rows)
        cls.baseline = active(cls.base_rows)
        cls.registry = json.loads((BATCH / "CC05_HUMAN_APPROVAL_REGISTRY.json").read_text(encoding="utf-8"))
        cls.matrix = json.loads((BATCH / "CC05_CONSOLIDATED_MATRIX.json").read_text(encoding="utf-8"))
        cls.release = json.loads((BATCH / "CC05_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))

    def test_active_coverage_history_and_formal_status(self):
        expected = {f"CC2002:ART.{n}" for n in range(1, 115)} | {"CC2002:ART.48-A", "CC2002:ART.49-A"}
        self.assertEqual(set(self.current), expected)
        self.assertEqual((len(self.rows), len(self.current)), (277, 116))
        self.assertEqual(sum(r["status"] == "RETIRED" for r in self.rows), 161)
        self.assertNotIn("CC2002:ART.69-A", self.current)
        self.assertEqual({r["review_status"] for r in self.current.values()}, {"PENDING_HUMAN_REVIEW"})
        ids = {r["explanation_id"] for r in self.rows}
        self.assertTrue(all(r["explanation_id"] in ids for r in self.base_rows))

    def test_six_owner_approved_texts_are_exact_and_versioned(self):
        reg = {r["target_id"]: r for r in self.registry["records"]}
        self.assertEqual(self.registry["record_count"], 6)
        self.assertFalse(self.registry["formal_status_promoted"])
        for number in CC05_HUMAN_APPROVED_TARGETS:
            tid = f"CC2002:ART.{number}"
            rec = self.current[tid]
            self.assertEqual(rec["content"], CC05_OVERRIDES[number])
            self.assertEqual(rec["editorial_version"], self.baseline[tid]["editorial_version"] + 1)
            self.assertEqual(reg[tid]["content_sha256"], content_hash(rec["content"]))
            self.assertTrue(rec["external_human_approval"]["exact_text_integrity_verified"])
            self.assertFalse(rec["external_human_approval"]["electronic_signature_verified"])

    def test_human_approval_scope_is_exactly_six(self):
        claimed = {
            tid for tid, rec in self.current.items()
            if rec.get("authoring", {}).get("human_approval_claimed") is True
        }
        self.assertEqual(claimed, {f"CC2002:ART.{n}" for n in CC05_HUMAN_APPROVED_TARGETS})
        self.assertFalse(any(r["review_status"] == "HUMAN_APPROVED_T1" for r in self.current.values()))

    def test_108_delegated_records_are_exactly_preserved(self):
        changed = {f"CC2002:ART.{n}" for n in CC05_HUMAN_APPROVED_TARGETS | {"14", "21"}}
        preserved = [tid for tid in self.baseline if tid not in changed]
        self.assertEqual(len(preserved), 108)
        self.assertTrue(all(self.current[tid] == self.baseline[tid] for tid in preserved))

    def test_arts_14_and_21_are_resolved_with_evidence(self):
        resolution = json.loads((BATCH / "CC05_LEGAL_RESOLUTION_14_21.json").read_text(encoding="utf-8"))
        by_target = {r["target_id"]: r for r in resolution["records"]}
        self.assertEqual(set(by_target), {"CC2002:ART.14", "CC2002:ART.21"})
        self.assertEqual(resolution["result"]["remaining_legal_pending"], 0)
        for tid in by_target:
            self.assertEqual(by_target[tid]["delegated_classification"], "A")
            self.assertEqual(by_target[tid]["content_sha256"], content_hash(self.current[tid]["content"]))
            self.assertTrue(by_target[tid]["official_sources"])

    def test_external_case_exception_is_narrow_and_fail_closed(self):
        ctx = E.NormContext("CC2002")
        approved = self.current["CC2002:ART.20"]
        self.assertTrue(E.validate_explanation(approved, ctx))
        ordinary = copy.deepcopy(approved)
        ordinary.pop("external_human_approval")
        ordinary["authoring"] = dict(ordinary["authoring"], method="AUTONOMOUS_DRAFT")
        with self.assertRaisesRegex(E.EntendaError, "ENTENDA_EXTERNAL_CASE_CONTENT"):
            E.validate_explanation(ordinary, ctx)
        invalid = copy.deepcopy(approved)
        invalid["external_human_approval"]["electronic_signature_verified"] = True
        with self.assertRaisesRegex(E.EntendaError, "ENTENDA_EXTERNAL_HUMAN_APPROVAL_INVALID"):
            E.validate_explanation(invalid, ctx)

    def test_release_matrix_and_production_index(self):
        self.assertEqual((self.matrix["active_records"], len(self.matrix["records"])), (116, 116))
        self.assertEqual(self.matrix["delegated_release_total"], 110)
        self.assertEqual(self.matrix["owner_approved_external_texts_integrated"], 6)
        self.assertEqual(self.matrix["legal_pending"], 0)
        self.assertEqual(self.release["pending"], {"legal": 0, "formal_human_review": 116})
        self.assertFalse(self.release["deployed"])
        for name, expected in INDEX_SHA.items():
            self.assertEqual(hashlib.sha256((BATCH / "index" / name).read_bytes()).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
