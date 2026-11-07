import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ENTENDA_ENGINE"))
import entenda_engine as E  # noqa: E402

BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"


class CC02CandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext("CC2002")
        cls.corpus = E.load_corpus(BATCH / "CC2002_CC02.entenda.jsonl")

    def test_contract_and_coverage(self):
        E.validate_corpus(self.corpus, self.ctx)
        active = [r for r in self.corpus if r["status"] == "ACTIVE"]
        ids = {r["target_id"] for r in active}
        self.assertEqual(116, len(active))
        self.assertTrue({f"CC2002:ART.{n}" for n in range(1, 115)} <= ids)
        self.assertTrue({"CC2002:ART.48-A", "CC2002:ART.49-A"} <= ids)
        self.assertNotIn("CC2002:ART.69-A", ids)
        self.assertEqual({"PENDING_HUMAN_REVIEW"}, {r["review_status"] for r in active})

    def test_pinned_source_and_structure(self):
        raw = (BATCH / "SOURCE_CC2002_ARTS_001_114.txt").read_bytes()
        self.assertEqual("0c927ce1d9817c5db5b3a1c563d8320eb334431495afeb3745a0fc8bc399e385", hashlib.sha256(raw).hexdigest())
        idx = json.loads((BATCH / "CC2002_TARGET_INDEX.json").read_text(encoding="utf-8"))
        self.assertEqual(378, idx["total_targets"])
        self.assertEqual(0, idx["target_id_duplicates"])
        self.assertEqual([], idx["anomalies"])
        self.assertEqual("REVOKED", self.ctx.effective_status("CC2002:ART.69-A"))
        self.assertEqual("REVOKED", self.ctx.effective_status("CC2002:ART.62:PAR.UNICO:INC.X"))
        self.assertEqual("CURRENT", self.ctx.effective_status("CC2002:ART.62"))

    def test_candidate_is_not_production_approved(self):
        review = json.loads((BATCH / "CC02_LEGAL_REVIEW.json").read_text(encoding="utf-8"))
        self.assertFalse(review["human_approval_claimed"])
        self.assertEqual(0, review["counts"]["approved_for_production"])
        self.assertEqual(1, review["counts"]["blocked"])


if __name__ == "__main__":
    unittest.main()
