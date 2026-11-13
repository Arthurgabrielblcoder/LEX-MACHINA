import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
OUT = HERE / "derived/qa02_independent_legal_audit"
CORPUS = HERE / "derived/candidate_cc_001_2046/CC2002_CC13.entenda.jsonl"
SOURCE = OUT / "QA02_PENDING_PRIORITY_WAVE_04.json"
PRIOR = OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_03.json"
AUDIT = OUT / "QA02_AUDIT_WAVE_04.json"
FINDINGS = OUT / "QA02_WAVE04_FINDINGS.json"
CORRECTIONS = OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_04.json"
PENDING = OUT / "QA02_PENDING_PRIORITY_AFTER_WAVE_04.json"
CONSOLIDATION = OUT / "QA02_CONSOLIDATION_WAVE_04.json"
REVIEWS = (
    OUT / "QA02_WAVE04_REVIEW_201_325.json",
    OUT / "QA02_WAVE04_REVIEW_326_450.json",
    OUT / "QA02_WAVE04_REVIEW_451_577.json",
)
PROTECTED = {
    "corpus": "b9fa2d39b6b4292fe2be466427871e75e14b2a327fb0c35ae190d5443cfd5c8c",
    "lookup": "60f1de336f2f9ecbc5e671d0a6a9223cf20e47ab5826a5501b53f9a67551866e",
    "payload": "9fb3f3a1b6f1c1926eda0818fc753f2d0348194cf25b0a333fc6fa18c48222cb",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA02Wave04Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.findings = json.loads(FINDINGS.read_text(encoding="utf-8"))["findings"]
        cls.corrections = json.loads(CORRECTIONS.read_text(encoding="utf-8"))
        cls.pending = json.loads(PENDING.read_text(encoding="utf-8"))
        cls.consolidation = json.loads(CONSOLIDATION.read_text(encoding="utf-8"))
        cls.checkpoints = [json.loads((OUT / f"QA02_CHECKPOINT_{number:02d}.json").read_text(encoding="utf-8"))
                           for number in range(18, 34)]

    def test_baseline_queue_prior_queue_and_protected_hashes(self):
        self.assertEqual(sha(SOURCE), "0933db90fea763f457c91b5ea30f1f39a688e6ba3e094f9479cb0bac541828b9")
        self.assertEqual(sha(PRIOR), "f56e044382fad87c7d2779cc19d310c65eb8a3adfa8201769fa9dd97f33f8164")
        self.assertEqual(sha(CORPUS), PROTECTED["corpus"])
        self.assertEqual(sha(HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_LOOKUP.IDX"), PROTECTED["lookup"])
        self.assertEqual(sha(HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_PAYLOAD.DAT"), PROTECTED["payload"])

    def test_delegated_modules_cover_exact_queue_once(self):
        reviews = [record for path in REVIEWS for record in json.loads(path.read_text(encoding="utf-8"))["records"]]
        self.assertEqual(len(reviews), 377)
        self.assertEqual([record["target_id"] for record in reviews],
                         [record["target_id"] for record in self.source["records"]])
        self.assertEqual([record["source_queue_position"] for record in reviews], list(range(201, 578)))
        self.assertEqual(len({record["target_id"] for record in reviews}), 377)

    def test_sixteen_checkpoints_follow_exact_positions(self):
        records = [record for checkpoint in self.checkpoints for record in checkpoint["records"]]
        self.assertEqual([record["target_id"] for record in records],
                         [record["target_id"] for record in self.source["records"]])
        self.assertEqual([record["queue_position"] for record in records], list(range(201, 578)))
        self.assertEqual([checkpoint["examined"] for checkpoint in self.checkpoints], [25] * 15 + [2])

    def test_no_overlap_with_prior_waves_and_unique(self):
        prior_ids = {record["target_id"] for wave in (1, 2, 3)
                     for record in json.loads((OUT / f"QA02_AUDIT_WAVE_{wave:02d}.json").read_text(encoding="utf-8"))["records"]}
        current = [record["target_id"] for record in self.audit["records"]]
        self.assertEqual(len(current), len(set(current)))
        self.assertFalse(prior_ids & set(current))

    def test_individual_evidence_is_complete_and_specific(self):
        comparisons = set()
        for record in self.audit["records"]:
            self.assertTrue(record["sources"] and record["current_law_snapshot"] and record["legal_segments_checked"])
            self.assertEqual(len(record["checks"]["field_sha256"]), 5)
            self.assertTrue(all(record["checks"][key] for key in ("requirements", "exceptions", "consequences")))
            self.assertIn(record["result"], ("ACHADO", "SEM_ACHADO_NO_ESCOPO_VERIFICADO"))
            self.assertGreater(len(record["comparison"]), 40)
            comparisons.add(record["comparison"])
        self.assertGreater(len(comparisons), 350)

    def test_new_findings_are_exact_unique_and_traceable(self):
        actual = [record["finding"] for record in self.audit["records"] if record["finding"]]
        self.assertEqual(actual, self.findings)
        self.assertEqual(len(actual), len({finding["target_id"] for finding in actual}))
        for finding in actual:
            for key in ("problematic_field", "problematic_excerpt", "legal_basis", "source_url", "nature", "severity",
                        "legal_or_pedagogical_consequence", "correction_direction", "confidence",
                        "human_review_required"):
                self.assertIn(key, finding)

    def test_prior_findings_and_critical_1258_are_preserved(self):
        prior = json.loads(PRIOR.read_text(encoding="utf-8"))
        for wave in (1, 2, 3):
            self.assertEqual(self.corrections[f"wave_{wave:02d}_findings"], prior[f"wave_{wave:02d}_findings"])
        critical = [item for wave in range(1, 5) for item in self.corrections[f"wave_{wave:02d}_findings"]
                    if item["target_id"] == "CC2002:ART.1258"]
        self.assertEqual(len(critical), 1)
        self.assertEqual(critical[0]["severity"], "CRÍTICO")

    def test_priority_queue_is_complete_but_full_corpus_is_not(self):
        self.assertEqual(self.audit["status"], "PRIORITY_AUDIT_COMPLETE")
        self.assertEqual((self.pending["total"], self.pending["records"], self.pending["next_source_position"]),
                         (0, [], None))
        self.assertEqual(self.consolidation["status"], "PRIORITY_AUDIT_COMPLETE")
        self.assertFalse(self.consolidation["full_corpus_audit_complete"])

    def test_consolidation_counts_and_artifact_hashes(self):
        coverage = self.consolidation["coverage"]
        self.assertEqual((coverage["wave_04_priority_audited"], coverage["priority_audited_accumulated"],
                          coverage["priority_pending"], coverage["unique_audited_accumulated"]),
                         (377, 599, 0, 629))
        self.assertEqual(sum(coverage["by_book_accumulated"].values()), 629)
        self.assertEqual(coverage["nonpriority_unaudited"], 1388)
        self.assertEqual(self.consolidation["protected_sha256"], PROTECTED)
        for name, expected in self.consolidation["artifact_sha256"].items():
            self.assertEqual(sha(OUT / name), expected, name)

    def test_deterministic_rebuild(self):
        paths = [AUDIT, FINDINGS, CORRECTIONS, PENDING, CONSOLIDATION,
                 *[OUT / f"QA02_CHECKPOINT_{number:02d}.json" for number in range(18, 34)]]
        before = [path.read_bytes() for path in paths]
        subprocess.run([sys.executable, str(HERE / "qa02_wave04_build.py"), "--through-checkpoint", "33"],
                       cwd=ROOT, check=True, capture_output=True)
        self.assertEqual([path.read_bytes() for path in paths], before)


if __name__ == "__main__":
    unittest.main()
