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
INVENTORY = OUT / "QA06_SUBDIVISION_INVENTORY_V2_CORRECTED.json"
QA05 = HERE / "derived/candidate_qa05_cc_001_2046/CC2002_QA05.entenda.jsonl"
MODULE_STEMS = ("0001_0672", "0673_1344", "1345_2017")
EXPECTED_MODULE_HASHES = {
    "QA06_B_REVIEW_V2_0001_0672.json": "c52d2b3ea62f46f8839ae410414513282445baa380fc1f5decbda9c0a06f6b42",
    "QA06_B_FINDINGS_V2_0001_0672.json": "892a7afb7f10254f8ed3c935c17a948c0cba0d11342571b9c3572373040f31d2",
    "QA06_B_REVIEW_V2_0673_1344.json": "98315d056aa63ab3fcc37fdbb261816c24317115a4fd22f8433524d9465ccc8e",
    "QA06_B_FINDINGS_V2_0673_1344.json": "0eb3dd26d7d04ef5b0c6cc849e25dfe36760aaf6b723f5bdc12f8cb3f4aeda7b",
    "QA06_B_REVIEW_V2_1345_2017.json": "4db30ba7d40333703350dc81215c28e0c2c9c05faf8c2c34ccb3a235e785c62e",
    "QA06_B_FINDINGS_V2_1345_2017.json": "187e3ac2c140ff4eefa8abf6c1a8d34d7b0e14e6877746fc536f93f7d33c4f9e",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def status(assessment):
    return assessment.get("status") or assessment.get("classification")


def evidence_text(assessment):
    evidence = assessment["evidence"]
    return evidence.get("legal_text") or evidence.get("legal_excerpt")


class QA06MaterialAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = load(INVENTORY)
        cls.inventory_segments = {segment["subdivision_id"]: segment
                                  for record in cls.inventory["records"] for segment in record["subdivisions"]}
        cls.modules = [load(OUT / f"QA06_B_REVIEW_V2_{stem}.json") for stem in MODULE_STEMS]
        cls.finding_modules = [load(OUT / f"QA06_B_FINDINGS_V2_{stem}.json") for stem in MODULE_STEMS]
        cls.records = [record for module in cls.modules for record in module["records"]]
        cls.assessments = [item for record in cls.records for item in record["subdivision_assessments"]]
        cls.source_findings = [item for module in cls.finding_modules for item in module["findings"]]
        cls.consolidation = load(OUT / "QA06_B_MATERIAL_AUDIT_CONSOLIDATION.json")
        cls.queue = load(OUT / "QA06_B_CORRECTION_QUEUE.json")

    def test_modules_are_bound_to_corrected_inventory_and_qa05(self):
        self.assertEqual(sha(INVENTORY), "7fe41b6b6e7755e17174551b56ea684fbbd8a399e95641f7f47e729f55ef5c82")
        self.assertEqual(sha(QA05), "2bf21e8333b584130a3159a240a96d5225958a53821971a184285ecc222a082f")
        for name, expected in EXPECTED_MODULE_HASHES.items():
            self.assertEqual(sha(OUT / name), expected)

    def test_exact_target_and_subdivision_coverage_once(self):
        self.assertEqual([record["audit_position"] for record in self.records], list(range(1, 2018)))
        self.assertEqual([record["target_id"] for record in self.records],
                         [record["target_id"] for record in self.inventory["records"]])
        ids = [item["subdivision_id"] for item in self.assessments]
        self.assertEqual((len(ids), len(set(ids)), set(ids)), (3790, 3790, set(self.inventory_segments)))
        self.assertEqual(Counter(status(item) for item in self.assessments), Counter({
            "COBERTA": 2714, "PARCIAL": 861, "AUSENTE": 123, "INDETERMINADA": 53,
            "NAO_APLICAVEL": 38, "INCORRETA": 1,
        }))

    def test_every_assessment_has_exact_individual_evidence(self):
        rationales = []
        for assessment in self.assessments:
            subdivision = self.inventory_segments[assessment["subdivision_id"]]
            self.assertEqual(assessment["kind"], subdivision["kind"])
            self.assertTrue(assessment["rationale"].strip())
            self.assertIsInstance(assessment["material_elements"], dict)
            if status(assessment) == "NAO_APLICAVEL":
                self.assertFalse(subdivision["material_audit_required"])
            else:
                self.assertEqual(evidence_text(assessment), subdivision["text"])
            rationales.append(assessment["rationale"])
        self.assertEqual(len(rationales), len(set(rationales)))

    def test_findings_trace_exact_problematic_assessments(self):
        problematic = {item["subdivision_id"] for item in self.assessments
                       if status(item) in {"PARCIAL", "INCORRETA", "AUSENTE", "INDETERMINADA"}}
        finding_ids = [item["subdivision_id"] for item in self.source_findings]
        self.assertEqual((len(finding_ids), len(set(finding_ids)), set(finding_ids)),
                         (1038, 1038, problematic))
        for finding in self.source_findings:
            self.assertEqual(finding["legal_text"], self.inventory_segments[finding["subdivision_id"]]["text"])
            self.assertTrue(finding["human_review_required"])

    def test_all_high_findings_received_independent_cross_review(self):
        middle = load(OUT / "QA06_B_HIGH_FINDINGS_CROSS_REVIEW_0673_1344.json")
        outer = load(OUT / "QA06_B_HIGH_FINDINGS_CROSS_REVIEW_OUTER.json")
        records = middle["records"] + outer["records"]
        high_ids = {item["subdivision_id"] for item in self.source_findings if item["severity"] == "ALTO"}
        self.assertEqual((len(records), len({item["subdivision_id"] for item in records}),
                          {item["subdivision_id"] for item in records}), (154, 154, high_ids))
        self.assertEqual(Counter(item["decision"] for item in records), Counter({
            "REJECTED_FALSE_POSITIVE": 92, "DOWNGRADE_MEDIO": 37, "CONFIRMED_FINDING": 25,
        }))

    def test_correction_queue_preserves_front_a_and_future_scope(self):
        self.assertEqual((self.queue["source_findings_before_high_cross_review"],
                          self.queue["rejected_false_positives_by_high_cross_review"],
                          self.queue["total_findings_retained"], self.queue["resolved_in_front_a"],
                          self.queue["pending_future_mission"]), (1038, 91, 947, 1, 946))
        self.assertEqual(self.queue["severity_counts_pending"], {"ALTO": 25, "BAIXO": 20, "MÉDIO": 901})
        art1104 = [item for item in self.queue["findings"] if item["target_id"] == "CC2002:ART.1104"]
        self.assertEqual(len(art1104), 1)
        self.assertEqual(art1104[0]["resolution_status"], "RESOLVED_IN_QA06_FRONT_A")
        self.assertEqual(art1104[0]["cross_review_decision"],
                         "CENTRAL_OVERRIDE_CONFIRMED_BY_FRONT_A_REVALIDATION")
        self.assertFalse(self.queue["corpus_modified_for_front_b"])
        self.assertFalse(self.queue["human_approval_claimed"])

    def test_forty_one_checkpoints_are_exact_and_nonoverlapping(self):
        positions = []
        for number in range(1, 42):
            checkpoint = load(OUT / f"QA06_B_CHECKPOINT_{number:02d}.json")
            expected_start = 1 + (number - 1) * 50
            expected_end = min(expected_start + 49, 2017)
            self.assertEqual((checkpoint["audit_position_start"], checkpoint["audit_position_end"]),
                             (expected_start, expected_end))
            self.assertEqual(checkpoint["target_total"], expected_end - expected_start + 1)
            positions.extend(range(expected_start, expected_end + 1))
        self.assertEqual(positions, list(range(1, 2018)))

    def test_consolidation_states_are_precise(self):
        self.assertEqual(self.consolidation["status"], "SUBDIVISION_AUDIT_COMPLETE")
        self.assertFalse(self.consolidation["subdivision_findings_resolved"])
        self.assertFalse(self.consolidation["full_corpus_legally_approved"])
        self.assertFalse(self.consolidation["human_approved"])
        self.assertEqual((self.consolidation["active_targets_examined"],
                          self.consolidation["subdivisions_identified"],
                          self.consolidation["subdivisions_effectively_audited"]), (2017, 3790, 3752))
        self.assertEqual(self.consolidation["pending_future_corrections"], 946)
        self.assertEqual(self.consolidation["critical_and_high_findings"] and
                         Counter(item["severity"] for item in self.consolidation["critical_and_high_findings"]),
                         Counter({"ALTO": 26}))
        self.assertFalse(self.consolidation["production_index_modified"])
        self.assertFalse(self.consolidation["deployed"])

    def test_integration_is_byte_deterministic(self):
        paths = [OUT / f"QA06_B_CHECKPOINT_{number:02d}.json" for number in range(1, 42)]
        paths += [OUT / "QA06_B_CORRECTION_QUEUE.json", OUT / "QA06_B_MATERIAL_AUDIT_CONSOLIDATION.json"]
        before = {path.name: sha(path) for path in paths}
        subprocess.run([sys.executable, "-X", "utf8", str(HERE / "qa06_material_integrate.py")], cwd=ROOT,
                       check=True, capture_output=True)
        after = {path.name: sha(path) for path in paths}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
