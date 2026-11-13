import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "derived/qa06_subdivision_material_audit"
INVENTORY = OUT / "QA06_SUBDIVISION_INVENTORY_V2_CORRECTED.json"
QUEUE = OUT / "QA06_AUDIT_QUEUE_2017_V2_CORRECTED.json"
POINTER = OUT / "QA06_AUTHORIZED_INVENTORY_POINTER.json"
REPORT = OUT / "QA06_INVENTORY_RECOVERY_REPORT.json"
QA05 = HERE / "derived/candidate_qa05_cc_001_2046/CC2002_QA05.entenda.jsonl"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA06InventoryRecoveryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = load(INVENTORY)
        cls.queue = load(QUEUE)
        cls.pointer = load(POINTER)
        cls.report = load(REPORT)
        cls.by_target = {record["target_id"]: record for record in cls.inventory["records"]}

    def test_qa05_baseline_and_corrected_artifact_hashes(self):
        self.assertEqual(sha(QA05), "2bf21e8333b584130a3159a240a96d5225958a53821971a184285ecc222a082f")
        self.assertEqual(sha(INVENTORY), "7fe41b6b6e7755e17174551b56ea684fbbd8a399e95641f7f47e729f55ef5c82")
        self.assertEqual(self.pointer["authorized_inventory_sha256"], sha(INVENTORY))
        self.assertEqual(self.pointer["authorized_queue_sha256"], sha(QUEUE))

    def test_preliminary_and_intermediate_inventories_are_invalidated(self):
        self.assertEqual(self.report["invalid_preliminary"]["sha256"],
                         "cc61bba3ba073b28308634bc3096ffb82e6da1270147a654951693ee757e5238")
        self.assertEqual(self.report["invalid_preliminary"]["validity"], "INVALID_FOR_LEGAL_AUDIT")
        self.assertEqual(self.report["intermediate_parser_fix"]["sha256"],
                         "277f54308399d7a6310ffeea80b079e51f9fbe20e24f05e25561e5346430cf7e")
        self.assertEqual(self.report["intermediate_parser_fix"]["validity"],
                         "SUPERSEDED_BY_SOURCE_LINE_EXTRACTION")

    def test_exact_target_and_subdivision_cardinality(self):
        records = self.inventory["records"]
        segments = [segment for record in records for segment in record["subdivisions"]]
        self.assertEqual((len(records), len({record["target_id"] for record in records})), (2017, 2017))
        self.assertEqual((len(segments), len({segment["subdivision_id"] for segment in segments})), (3790, 3790))
        self.assertEqual(sum(segment["material_audit_required"] for segment in segments), 3752)
        self.assertEqual(Counter(segment["status"] for segment in segments),
                         Counter({"ACTIVE": 3752, "EXCLUDED_REVOKED_OR_VETOED": 38}))
        self.assertEqual([record["audit_position"] for record in records], list(range(1, 2018)))
        self.assertEqual([record["target_id"] for record in self.queue["records"]],
                         [record["target_id"] for record in records])

    def test_internal_title_remissions_are_never_headings(self):
        art1367 = self.by_target["CC2002:ART.1367"]["subdivisions"][0]["text"]
        self.assertIn("Capítulo I do Título X do Livro III", art1367)
        self.assertIn("art. 1.231", art1367)
        art1358a = self.by_target["CC2002:ART.1358-A"]["subdivisions"]
        inciso_ii = next(item["text"] for item in art1358a if item["subdivision_id"].endswith("PAR.2:INC.II"))
        self.assertIn("Capítulo I do Título II da Lei nº 4.591", inciso_ii)

    def test_structural_headings_are_not_absorbed_as_legal_text(self):
        art1358a = self.by_target["CC2002:ART.1358-A"]["subdivisions"]
        paragraph_three = next(item["text"] for item in art1358a if item["subdivision_id"].endswith("PAR.3"))
        self.assertNotIn("Disposições Gerais", paragraph_three)
        self.assertTrue(paragraph_three.endswith("ficará a cargo do empreendedor."))

    def test_known_source_anomalies_are_complete(self):
        art96 = self.by_target["CC2002:ART.96"]["subdivisions"]
        paragraph_three = next(item["text"] for item in art96 if item["subdivision_id"].endswith("PAR.3"))
        self.assertEqual(paragraph_three,
                         "São necessárias as que têm por fim conservar o bem ou evitar que se deteriore.")
        self.assertIn("O pai ou a mãe", self.by_target["CC2002:ART.1636"]["subdivisions"][0]["text"])

    def test_no_agent_evidence_was_mixed_across_inventories(self):
        recovery = self.report["agent_recovery"]
        self.assertEqual((recovery["final_artifacts_found"], recovery["reused"], recovery["quarantined"]),
                         (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
