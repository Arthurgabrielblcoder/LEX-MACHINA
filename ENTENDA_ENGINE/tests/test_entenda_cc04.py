import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ENTENDA_ENGINE"))
import entenda_engine as E  # noqa: E402

BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"


def load(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class CC04DelegatedReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = {r["target_id"]: r for r in load(BATCH / "CC2002_CC03B_BASELINE.entenda.jsonl") if r["status"] == "ACTIVE"}
        cls.corpus = load(BATCH / "CC2002_CC02.entenda.jsonl")
        cls.active = {r["target_id"]: r for r in cls.corpus if r["status"] == "ACTIVE"}
        cls.matrix = json.loads((BATCH / "CC04_DELEGATED_REVIEW_MATRIX.json").read_text(encoding="utf-8"))

    def test_coverage_classification_and_release(self):
        self.assertEqual(110, self.matrix["reviewed_records"])
        self.assertEqual({"A": 89, "B": 19, "C": 2, "D": 0}, self.matrix["classification_counts"])
        self.assertEqual(108, self.matrix["delegated_editorial_release_count"])
        self.assertEqual(2, self.matrix["pending_count"])
        self.assertEqual(110, len({r["target_id"] for r in self.matrix["records"]}))
        self.assertTrue(all(r["evidence"] and r["source_snapshot_sha256"] for r in self.matrix["records"]))

    def test_excluded_six_are_byte_semantically_unchanged(self):
        for number in (2, 4, 15, 20, 50, 113):
            tid = f"CC2002:ART.{number}"
            self.assertEqual(self.base[tid]["explanation_id"], self.active[tid]["explanation_id"])
            self.assertEqual(self.base[tid]["content"], self.active[tid]["content"])
            self.assertEqual(self.base[tid]["source"], self.active[tid]["source"])

    def test_versions_and_formal_status(self):
        changed = [tid for tid in self.active if self.active[tid]["content"] != self.base[tid]["content"]]
        self.assertEqual(19, len(changed))
        self.assertEqual(269, len(self.corpus))
        self.assertEqual({"PENDING_HUMAN_REVIEW"}, {r["review_status"] for r in self.active.values()})
        self.assertFalse(self.matrix["human_approval_claimed"])
        E.validate_corpus(self.corpus, E.NormContext("CC2002"))

    def test_five_checkpoints_and_priority_review(self):
        points = sorted((BATCH / "checkpoints_cc04").glob("CC04_*.json"))
        self.assertEqual(5, len(points))
        self.assertEqual(110, sum(json.loads(p.read_text(encoding="utf-8"))["reviewed_count"] for p in points))
        priority = json.loads((BATCH / "CC04_PRIORITY_SECOND_REVIEW.json").read_text(encoding="utf-8"))
        self.assertEqual(23, priority["count"])
        self.assertTrue(all(r["result"] for r in priority["records"]))

    def test_no_generic_filler_and_subdivision_evidence(self):
        banned = ("A explicação cobre o artigo", "O dispositivo deve ser lido", "O exemplo é apenas didático")
        text = json.dumps([r["content"] for r in self.active.values()], ensure_ascii=False)
        self.assertFalse(any(x in text for x in banned))
        self.assertTrue(all(r["subdivision_evidence_scope"] in {"SUBTREE", "SUBTREE+COVERED"} for r in self.matrix["records"]))


if __name__ == "__main__":
    unittest.main()
