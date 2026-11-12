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
SOURCE_QUEUE = OUT / "QA02_PENDING_PRIORITY_WAVE_02.json"
PENDING = OUT / "QA02_PENDING_PRIORITY_WAVE_03.json"
AUDIT = OUT / "QA02_AUDIT_WAVE_02.json"
FINDINGS = OUT / "QA02_WAVE02_FINDINGS.json"
CONSOLIDATION = OUT / "QA02_CONSOLIDATION_WAVE_02.json"
PROTECTED = {
    "corpus": "b9fa2d39b6b4292fe2be466427871e75e14b2a327fb0c35ae190d5443cfd5c8c",
    "lookup": "60f1de336f2f9ecbc5e671d0a6a9223cf20e47ab5826a5501b53f9a67551866e",
    "payload": "9fb3f3a1b6f1c1926eda0818fc753f2d0348194cf25b0a333fc6fa18c48222cb",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA02Wave02Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE_QUEUE.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.pending = json.loads(PENDING.read_text(encoding="utf-8"))
        cls.consolidation = json.loads(CONSOLIDATION.read_text(encoding="utf-8"))
        cls.checkpoints = [json.loads((OUT / f"QA02_CHECKPOINT_{n:02d}.json").read_text(encoding="utf-8"))
                           for n in range(8, 13)]

    def test_baseline_and_queue_hashes(self):
        self.assertEqual(sha(SOURCE_QUEUE), "881adcca7df7a6dd91f4f69b77f3f88dc38c9d89c2bf9859612a316717cde496")
        self.assertEqual(sha(CORPUS), PROTECTED["corpus"])
        self.assertEqual(sha(HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_LOOKUP.IDX"), PROTECTED["lookup"])
        self.assertEqual(sha(HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_PAYLOAD.DAT"), PROTECTED["payload"])

    def test_checkpoints_follow_exact_queue_order(self):
        records = [record for checkpoint in self.checkpoints for record in checkpoint["records"]]
        self.assertEqual([r["target_id"] for r in records], [r["target_id"] for r in self.source["records"][:100]])
        self.assertEqual([r["queue_position"] for r in records], list(range(1, 101)))
        self.assertTrue(all(cp["examined"] == 20 for cp in self.checkpoints))

    def test_no_wave1_overlap_and_unique(self):
        wave1 = json.loads((OUT / "QA02_AUDIT_WAVE_01.json").read_text(encoding="utf-8"))
        wave1_ids = {r["target_id"] for r in wave1["records"]}
        wave2_ids = [r["target_id"] for r in self.audit["records"]]
        self.assertEqual(len(wave2_ids), len(set(wave2_ids)))
        self.assertFalse(wave1_ids & set(wave2_ids))

    def test_individual_evidence_complete(self):
        for record in self.audit["records"]:
            self.assertTrue(record["sources"] and record["current_law_snapshot"] and record["legal_segments_checked"])
            self.assertTrue(record["independent_rule_summary"])
            self.assertEqual(set(record["checks"]["field_sha256"]),
                             {"o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis"})
            self.assertTrue(all(record["checks"][k] for k in ("requirements", "exceptions", "consequences")))

    def test_findings_traceable_and_unique(self):
        expected = json.loads(FINDINGS.read_text(encoding="utf-8"))["findings"]
        actual = [r["finding"] for r in self.audit["records"] if r["finding"]]
        self.assertEqual(actual, expected)
        self.assertEqual(len({f["target_id"] for f in actual}), len(actual))
        for finding in actual:
            for key in ("problematic_field", "problematic_excerpt", "legal_basis", "source_url", "severity",
                        "legal_or_pedagogical_consequence", "correction_direction", "confidence"):
                self.assertTrue(finding[key], (finding["target_id"], key))

    def test_prior_correction_queue_preserved(self):
        old_path = OUT / "QA02_CORRECTION_QUEUE.json"
        old = json.loads(old_path.read_text(encoding="utf-8"))
        new = json.loads((OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_02.json").read_text(encoding="utf-8"))
        self.assertEqual(new["wave_01_sha256"], sha(old_path))
        self.assertEqual(new["wave_01_findings"], old["findings"])
        self.assertEqual(new["total"], 14)

    def test_remaining_queue_exact(self):
        self.assertEqual(self.pending["records"],
                         [{"source_queue_position": i, **r} for i, r in enumerate(self.source["records"][100:], 101)])
        self.assertEqual((self.pending["total"], self.pending["next_source_position"]), (477, 101))
        self.assertEqual(self.pending["records"][0]["target_id"], "CC2002:ART.101")

    def test_deterministic_rebuild(self):
        paths = [AUDIT, PENDING, CONSOLIDATION, OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_02.json",
                 *[OUT / f"QA02_CHECKPOINT_{n:02d}.json" for n in range(8, 13)]]
        before = [path.read_bytes() for path in paths]
        subprocess.run([sys.executable, str(HERE / "qa02_wave02_build.py"), "--through-checkpoint", "12"],
                       cwd=ROOT, check=True, capture_output=True)
        self.assertEqual([path.read_bytes() for path in paths], before)

    def test_consolidation_counts_hashes_and_paths(self):
        coverage = self.consolidation["coverage"]
        self.assertEqual((coverage["priority_audited_accumulated"], coverage["priority_pending"],
                          coverage["unique_audited_accumulated"]), (122, 477, 152))
        self.assertEqual(self.consolidation["findings"]["wave_02_by_severity"], {"ALTO": 5, "MÉDIO": 2})
        self.assertEqual(self.consolidation["findings"]["accumulated_by_severity"], {"ALTO": 10, "MÉDIO": 4})
        self.assertEqual(self.consolidation["protected_sha256"], PROTECTED)
        self.assertNotIn("\\", CONSOLIDATION.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
