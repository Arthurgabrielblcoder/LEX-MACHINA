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
SOURCE_QUEUE = OUT / "QA02_PENDING_PRIORITY_WAVE_03.json"
PRIOR_QUEUE = OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_02.json"
PENDING = OUT / "QA02_PENDING_PRIORITY_WAVE_04.json"
AUDIT = OUT / "QA02_AUDIT_WAVE_03.json"
FINDINGS = OUT / "QA02_WAVE03_FINDINGS.json"
CONSOLIDATION = OUT / "QA02_CONSOLIDATION_WAVE_03.json"
PROTECTED = {
    "corpus": "b9fa2d39b6b4292fe2be466427871e75e14b2a327fb0c35ae190d5443cfd5c8c",
    "lookup": "60f1de336f2f9ecbc5e671d0a6a9223cf20e47ab5826a5501b53f9a67551866e",
    "payload": "9fb3f3a1b6f1c1926eda0818fc753f2d0348194cf25b0a333fc6fa18c48222cb",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA02Wave03Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE_QUEUE.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.pending = json.loads(PENDING.read_text(encoding="utf-8"))
        cls.consolidation = json.loads(CONSOLIDATION.read_text(encoding="utf-8"))
        cls.checkpoints = [json.loads((OUT / f"QA02_CHECKPOINT_{n:02d}.json").read_text(encoding="utf-8"))
                           for n in range(13, 18)]

    def test_baseline_queue_and_protected_hashes(self):
        self.assertEqual(sha(SOURCE_QUEUE), "592983de0f87603d539bc29d6c8ac75e1b1c2ae240c23e9b00e7b5238b50c86f")
        self.assertEqual(sha(PRIOR_QUEUE), "44078a5f7cee394c708889553b331a1ec67205a678d39c59db8fb5b2752ed072")
        self.assertEqual(sha(CORPUS), PROTECTED["corpus"])
        self.assertEqual(sha(HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_LOOKUP.IDX"), PROTECTED["lookup"])
        self.assertEqual(sha(HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_PAYLOAD.DAT"), PROTECTED["payload"])

    def test_checkpoints_follow_source_positions_101_200(self):
        records = [record for checkpoint in self.checkpoints for record in checkpoint["records"]]
        self.assertEqual([r["target_id"] for r in records], [r["target_id"] for r in self.source["records"][:100]])
        self.assertEqual([r["queue_position"] for r in records], list(range(101, 201)))
        self.assertTrue(all(cp["examined"] == 20 for cp in self.checkpoints))

    def test_no_prior_wave_overlap_and_unique(self):
        prior_ids = {r["target_id"] for name in ("QA02_AUDIT_WAVE_01.json", "QA02_AUDIT_WAVE_02.json")
                     for r in json.loads((OUT / name).read_text(encoding="utf-8"))["records"]}
        current = [r["target_id"] for r in self.audit["records"]]
        self.assertEqual(len(current), len(set(current)))
        self.assertFalse(prior_ids & set(current))

    def test_individual_evidence_complete(self):
        for record in self.audit["records"]:
            self.assertTrue(record["sources"] and record["current_law_snapshot"] and record["legal_segments_checked"])
            self.assertTrue(record["independent_rule_summary"])
            self.assertEqual(len(record["checks"]["field_sha256"]), 5)
            self.assertTrue(all(record["checks"][key] for key in ("requirements", "exceptions", "consequences")))

    def test_new_findings_are_exact_unique_and_traceable(self):
        expected = json.loads(FINDINGS.read_text(encoding="utf-8"))["findings"]
        actual = [r["finding"] for r in self.audit["records"] if r["finding"]]
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), len({f["target_id"] for f in actual}))
        for finding in actual:
            for key in ("problematic_field", "problematic_excerpt", "legal_basis", "source_url", "severity",
                        "legal_or_pedagogical_consequence", "correction_direction", "confidence"):
                self.assertTrue(finding[key], (finding["target_id"], key))

    def test_prior_findings_preserved_in_consolidated_queue(self):
        prior = json.loads(PRIOR_QUEUE.read_text(encoding="utf-8"))
        current = json.loads((OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_03.json").read_text(encoding="utf-8"))
        self.assertEqual(current["prior_sha256"], sha(PRIOR_QUEUE))
        self.assertEqual(current["wave_01_findings"], prior["wave_01_findings"])
        self.assertEqual(current["wave_02_findings"], prior["wave_02_findings"])
        self.assertEqual(current["total"], 32)

    def test_remaining_queue_is_exact(self):
        self.assertEqual(self.pending["records"], self.source["records"][100:])
        self.assertEqual((self.pending["total"], self.pending["next_source_position"]), (377, 201))
        self.assertEqual(self.pending["records"][0]["target_id"], "CC2002:ART.1273")

    def test_deterministic_rebuild(self):
        paths = [AUDIT, PENDING, CONSOLIDATION, OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_03.json",
                 *[OUT / f"QA02_CHECKPOINT_{n:02d}.json" for n in range(13, 18)]]
        before = [path.read_bytes() for path in paths]
        subprocess.run([sys.executable, str(HERE / "qa02_wave03_build.py"), "--through-checkpoint", "17"],
                       cwd=ROOT, check=True, capture_output=True)
        self.assertEqual([path.read_bytes() for path in paths], before)

    def test_consolidation_counts_severity_and_paths(self):
        coverage = self.consolidation["coverage"]
        self.assertEqual((coverage["priority_audited_accumulated"], coverage["priority_pending"],
                          coverage["unique_audited_accumulated"]), (222, 377, 252))
        self.assertEqual(self.consolidation["findings"]["wave_03_by_severity"],
                         {"ALTO": 11, "CRÍTICO": 1, "MÉDIO": 6})
        self.assertEqual(self.consolidation["findings"]["accumulated_by_severity"],
                         {"ALTO": 21, "CRÍTICO": 1, "MÉDIO": 10})
        self.assertEqual(self.consolidation["protected_sha256"], PROTECTED)
        self.assertNotIn("\\", CONSOLIDATION.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
