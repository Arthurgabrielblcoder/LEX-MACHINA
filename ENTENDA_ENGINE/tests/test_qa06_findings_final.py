import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
OUT = HERE / "derived/qa06_subdivision_material_audit"
CONSOLIDATION = OUT / "QA06_B_FINDINGS_FINAL_CONSOLIDATION.json"
QUEUE = OUT / "QA06_B_DEFINITIVE_CORRECTION_QUEUE.json"
INDETERMINATE = OUT / "QA06_B_INDETERMINATE_REVIEW_QUEUE.json"
REJECTED = OUT / "QA06_B_REJECTED_FINDINGS_EVIDENCE.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA06FinalFindingsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.consolidation = load(CONSOLIDATION)
        cls.queue = load(QUEUE)
        cls.indeterminate = load(INDETERMINATE)
        cls.rejected = load(REJECTED)

    def test_every_preliminary_finding_has_one_quality_decision(self):
        records = self.consolidation["records"]
        ids = [record["subdivision_id"] for record in records]
        self.assertEqual((len(records), len(set(ids))), (1038, 1038))
        self.assertEqual(self.consolidation["review_decision_counts"], {
            "CONFIRMADO": 344, "INDETERMINADO": 1, "NAO_CONFIRMADO": 563, "RECLASSIFICADO": 130,
        })
        for record in records:
            self.assertTrue(record["review_justification"].strip())
            self.assertTrue(record["review_file"].endswith(".json"))
            self.assertEqual(len(record["review_record_sha256"]), 64)

    def test_final_dispositions_partition_without_silent_deletion(self):
        self.assertEqual(self.consolidation["final_disposition_counts"], {
            "INDETERMINADO": 10, "JA_CORRIGIDO": 1, "NAO_CONFIRMADO": 566, "PENDENTE_CORRECAO": 461,
        })
        self.assertEqual(sum(self.consolidation["final_disposition_counts"].values()), 1038)
        self.assertEqual((self.queue["total"], self.indeterminate["total"], self.rejected["total"]),
                         (461, 10, 566))
        self.assertEqual(self.queue["severity_counts"], {"ALTO": 41, "MÉDIO": 420})
        self.assertEqual(len(self.queue["findings"]), 461)
        self.assertEqual(len(self.indeterminate["findings"]), 10)
        self.assertEqual(len(self.rejected["findings"]), 566)

    def test_art_1104_is_corrected_not_pending(self):
        art1104 = [record for record in self.consolidation["records"] if record["target_id"] == "CC2002:ART.1104"]
        self.assertEqual(len(art1104), 1)
        self.assertEqual(art1104[0]["final_disposition"], "JA_CORRIGIDO")
        self.assertTrue(art1104[0]["central_override"])
        self.assertNotIn("CC2002:ART.1104", {record["target_id"] for record in self.queue["findings"]})

    def test_non_high_sample_failure_triggered_full_expansion(self):
        quality = self.consolidation["non_high_quality_control"]
        self.assertEqual(quality, {
            "population": 884, "stratified_sample": 120, "sample_not_confirmed": 64,
            "sample_false_positive_rate": 0.5333333333,
            "expanded_remainder_review": 764, "full_non_high_review_complete": True,
        })
        review_total = sum(artifact["total"] for artifact in self.consolidation["review_artifacts"]
                           if artifact["scope"] in ("STRATIFIED_SAMPLE", "EXPANDED_REMAINDER"))
        self.assertEqual(review_total, 884)

    def test_definitive_queue_contains_only_confirmed_or_reclassified_findings(self):
        for record in self.queue["findings"]:
            self.assertIn(record["review_decision"], {"CONFIRMADO", "RECLASSIFICADO"})
            self.assertIn(record["final_severity"], {"CRÍTICO", "ALTO", "MÉDIO", "BAIXO"})
            self.assertEqual(record["final_disposition"], "PENDENTE_CORRECAO")
        for record in self.indeterminate["findings"]:
            self.assertEqual(record["final_disposition"], "INDETERMINADO")
        for record in self.rejected["findings"]:
            self.assertIn(record["final_disposition"], {"NAO_CONFIRMADO", "DUPLICADO"})

    def test_no_front_b_corpus_mutation_or_human_approval_claim(self):
        self.assertFalse(self.queue["corpus_modified"])
        self.assertFalse(self.queue["human_approval_claimed"])
        self.assertFalse(self.indeterminate["corpus_modified"])
        self.assertFalse(self.indeterminate["human_approval_claimed"])
        self.assertFalse(self.consolidation["subdivision_findings_resolved"])
        self.assertFalse(self.consolidation["full_corpus_legally_approved"])
        self.assertFalse(self.consolidation["human_approved"])

    def test_finalization_is_byte_deterministic(self):
        paths = (CONSOLIDATION, QUEUE, INDETERMINATE, REJECTED)
        before = {path.name: sha(path) for path in paths}
        subprocess.run([sys.executable, "-X", "utf8", str(HERE / "qa06_findings_finalize.py")],
                       cwd=ROOT, check=True, capture_output=True)
        after = {path.name: sha(path) for path in paths}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
