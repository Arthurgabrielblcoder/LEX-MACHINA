import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ENTENDA_ENGINE"))
import entenda_engine as E  # noqa: E402

BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class CC03AuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_jsonl(BATCH / "CC2002_CC02_BASELINE.entenda.jsonl")
        corpus_path = BATCH / "CC2002_CC03_BASELINE.entenda.jsonl"
        cls.corpus = load_jsonl(corpus_path if corpus_path.is_file() else BATCH / "CC2002_CC02.entenda.jsonl")
        cls.matrix = json.loads((BATCH / "CC03_AUDIT_MATRIX.json").read_text(encoding="utf-8"))

    def test_versions_and_human_status_are_preserved(self):
        active = [r for r in self.corpus if r["status"] == "ACTIVE"]
        retired = [r for r in self.corpus if r["status"] == "RETIRED"]
        self.assertEqual((116, 18, 134), (len(active), len(retired), len(self.corpus)))
        self.assertEqual(18, sum(r["editorial_version"] == 2 for r in active))
        self.assertEqual({"PENDING_HUMAN_REVIEW"}, {r["review_status"] for r in active})
        self.assertEqual({"CHANGES_REQUESTED"}, {r["review_status"] for r in retired})
        self.assertFalse(any(r["review_status"] in {"HUMAN_APPROVED_T1", "APPROVED"} for r in self.corpus))

    def test_original_content_and_provenance_remain_available(self):
        current = {r["explanation_id"]: r for r in self.corpus}
        for original in self.baseline:
            kept = current[original["explanation_id"]]
            self.assertEqual(original["content"], kept["content"])
            self.assertEqual(original["source"], kept["source"])
        raw = (BATCH / "CC2002_CC02_BASELINE.entenda.jsonl").read_bytes()
        self.assertEqual("86ef8d8f1843650e927b2fd2fd620dd92a7fe9508dac8934efbaae238beecd4d", hashlib.sha256(raw).hexdigest())

    def test_complete_audit_matrix(self):
        counts = self.matrix["audit_status_counts"]
        self.assertEqual(116, self.matrix["explanations_audited"])
        self.assertEqual(116, sum(counts.values()))
        self.assertEqual(18, counts["CORRIGIDO_COM_EVIDENCIA"])
        self.assertEqual(23, counts["REVISAO_HUMANA_PRIORITARIA"])
        self.assertEqual(0, counts["BLOQUEADO_POR_INCONSISTENCIA"])
        self.assertEqual(116, len({r["target_id"] for r in self.matrix["records"]}))
        self.assertTrue(all(r["formal_review_status"] == "PENDING_HUMAN_REVIEW" for r in self.matrix["records"]))

    def test_corrections_and_sample_are_complete(self):
        changes = json.loads((BATCH / "CC03_SUBSTANTIVE_CORRECTIONS.json").read_text(encoding="utf-8"))
        sample = json.loads((BATCH / "CC03_HUMAN_REVIEW_SAMPLE_15.json").read_text(encoding="utf-8"))
        self.assertEqual(18, changes["count"])
        self.assertTrue(all(c["changed_sections"] and c["original_explanation_id"].endswith("/1") and c["revised_explanation_id"].endswith("/2") for c in changes["corrections"]))
        self.assertEqual(15, sample["count"])
        self.assertEqual(15, len({c["target_id"] for c in sample["cases"]}))
        self.assertTrue(all(c["legal_text"] and c["entenda_integral"] and c["human_decision_points"] for c in sample["cases"]))

    def test_utf8_schema_and_engine_contract(self):
        E.validate_corpus(self.corpus, E.NormContext("CC2002"))
        for path in BATCH.glob("CC03*.json"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("\ufffd", text)
            json.loads(text)


if __name__ == "__main__":
    unittest.main()
