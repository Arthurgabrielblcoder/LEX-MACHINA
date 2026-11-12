import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import qa02_build_inventory as Q  # noqa: E402

OUT = HERE / "derived/qa02_independent_legal_audit"
INVENTORY = OUT / "QA02_RISK_INVENTORY.json"
AUDIT = OUT / "QA02_AUDIT_WAVE_01.json"
QUEUE = OUT / "QA02_CORRECTION_QUEUE.json"
PENDING = OUT / "QA02_PENDING_PRIORITY_WAVE_02.json"
CONSOLIDATION = OUT / "QA02_CONSOLIDATION.json"
PROTECTED = {
    "ENTENDA_ENGINE/derived/candidate_cc_001_2046/CC2002_CC13.entenda.jsonl": "b9fa2d39b6b4292fe2be466427871e75e14b2a327fb0c35ae190d5443cfd5c8c",
    "ENTENDA_ENGINE/derived/candidate_cc_001_2046/candidate_index/ENTENDA_LOOKUP.IDX": "60f1de336f2f9ecbc5e671d0a6a9223cf20e47ab5826a5501b53f9a67551866e",
    "ENTENDA_ENGINE/derived/candidate_cc_001_2046/candidate_index/ENTENDA_PAYLOAD.DAT": "9fb3f3a1b6f1c1926eda0818fc753f2d0348194cf25b0a333fc6fa18c48222cb",
}


class QA02InventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(INVENTORY.read_text(encoding="utf-8"))

    def test_protected_hashes(self):
        for rel, expected in PROTECTED.items():
            self.assertEqual(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest(), expected, rel)

    def test_priority_and_sample_are_unique_and_active(self):
        active = {json.loads(x)["target_id"] for x in (ROOT / next(iter(PROTECTED))).read_text(encoding="utf-8").splitlines()
                  if json.loads(x)["status"] == "ACTIVE"}
        priority = [r["target_id"] for r in self.doc["priority_b_or_substantive_correction"]["records"]]
        sample = [r["target_id"] for r in self.doc["stratified_a_sample"]["records"]]
        self.assertEqual(len(priority), len(set(priority)))
        self.assertEqual(len(sample), len(set(sample)))
        self.assertFalse(set(priority) & set(sample))
        self.assertTrue(set(priority + sample + self.doc["mandatory_sentinels"]) <= active)

    def test_no_active_insurance_targets_757_802(self):
        self.assertEqual(self.doc["insurance_757_802"], dict(active_count=0, active_target_ids=[],
                         expectation="zero active explanations after Lei 15.040/2024"))

    def test_selection_is_deterministic(self):
        before = INVENTORY.read_bytes()
        subprocess.run([sys.executable, str(HERE / "qa02_build_inventory.py")], cwd=ROOT, check=True, capture_output=True)
        self.assertEqual(INVENTORY.read_bytes(), before)

    def test_manifest_paths_are_posix(self):
        self.assertNotIn("\\", INVENTORY.read_text(encoding="utf-8"))


class QA02AuditWaveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.queue = json.loads(QUEUE.read_text(encoding="utf-8"))

    def test_promised_wave_has_individual_evidence(self):
        inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
        promised = set(inv["first_b_audit_wave"]["target_ids"]) | set(inv["mandatory_sentinels"]) | \
                   {r["target_id"] for r in inv["stratified_a_sample"]["records"]}
        actual = {r["target_id"] for r in self.audit["records"]}
        self.assertEqual(actual, promised)
        self.assertEqual(len(actual), len(self.audit["records"]))
        for r in self.audit["records"]:
            self.assertTrue(r["current_law_snapshot"] and r["independent_rule_summary"] and r["sources"], r["target_id"])
            self.assertTrue(all(r["checks"][k] for k in ("requirements", "exceptions", "consequences")), r["target_id"])
            self.assertEqual(len(r["checks"]["fields"]), 5)

    def test_findings_are_unique_traceable_and_queued(self):
        findings = [r["finding"] for r in self.audit["records"] if r["finding"]]
        ids = [f["target_id"] for f in findings]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(self.queue["findings"], sorted(findings, key=lambda f: ({"CRÍTICO": 0, "ALTO": 1, "MÉDIO": 2, "BAIXO": 3}[f["severity"]], f["target_id"])))
        for f in findings:
            for k in ("problematic_field", "problematic_excerpt", "legal_basis", "nature", "severity",
                      "legal_or_pedagogical_consequence", "correction_direction", "confidence"):
                self.assertTrue(f[k], (f["target_id"], k))

    def test_wave_render_is_deterministic(self):
        paths = [AUDIT, QUEUE] + [OUT / f"QA02_CHECKPOINT_{n:02d}.json" for n in range(2, 7)]
        before = [p.read_bytes() for p in paths]
        subprocess.run([sys.executable, str(HERE / "qa02_build_audit_wave01.py")], cwd=ROOT, check=True, capture_output=True)
        self.assertEqual([p.read_bytes() for p in paths], before)

    def test_checkpoint_coverage_is_exact_and_disjoint(self):
        cps = [json.loads((OUT / f"QA02_CHECKPOINT_{n:02d}.json").read_text(encoding="utf-8")) for n in range(2, 7)]
        ids = [t for cp in cps for t in cp["target_ids"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {r["target_id"] for r in self.audit["records"]})
        self.assertEqual(sum(cp["findings"] for cp in cps), self.audit["findings_total"])
        for cp in cps:
            self.assertEqual(cp["examined"], len(cp["records"]))
            self.assertEqual(cp["protected_sha256"], {"corpus": PROTECTED[next(iter(PROTECTED))],
                "lookup": PROTECTED["ENTENDA_ENGINE/derived/candidate_cc_001_2046/candidate_index/ENTENDA_LOOKUP.IDX"],
                "payload": PROTECTED["ENTENDA_ENGINE/derived/candidate_cc_001_2046/candidate_index/ENTENDA_PAYLOAD.DAT"]})


class QA02ConsolidationTest(unittest.TestCase):
    def test_pending_queue_is_exact(self):
        inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        pending = json.loads(PENDING.read_text(encoding="utf-8"))
        audited_priority = {r["target_id"] for r in audit["records"] if "B_OR_CORRECTION_WAVE" in r["audit_groups"]}
        expected = [r for r in inv["priority_b_or_substantive_correction"]["records"] if r["target_id"] not in audited_priority]
        self.assertEqual(pending["records"], expected)
        self.assertEqual(pending["total"], 577)

    def test_partial_status_and_immutability_are_explicit(self):
        doc = json.loads(CONSOLIDATION.read_text(encoding="utf-8"))
        self.assertEqual(doc["status"], "PARTIAL_REQUIRES_CONTINUATION")
        self.assertEqual({k: doc["coverage"][k] for k in ("priority_total", "priority_audited", "priority_pending",
            "a_universe", "a_sample_audited", "unique_targets_audited")},
            {"priority_total": 599, "priority_audited": 22, "priority_pending": 577,
             "a_universe": 1416, "a_sample_audited": 28, "unique_targets_audited": 52})
        self.assertEqual(sum(doc["coverage"]["audited_by_book"].values()), 52)
        self.assertEqual(doc["coverage"]["audited_by_group"], {"A_STRATIFIED_SAMPLE": 28,
            "B_OR_CORRECTION_WAVE": 22, "MANDATORY_SENTINEL": 6})
        self.assertEqual(sum(doc["coverage"]["audited_by_thematic_checkpoint"].values()), 52)
        self.assertEqual(doc["findings"]["by_severity"], {"ALTO": 5, "MÉDIO": 2})
        self.assertEqual(doc["immutability"], {"editorial_corpus_changed": False,
            "production_indexes_changed": False, "deploy_performed": False})
        self.assertEqual(doc["protected_sha256"], {"corpus": PROTECTED[next(iter(PROTECTED))],
            "lookup": PROTECTED["ENTENDA_ENGINE/derived/candidate_cc_001_2046/candidate_index/ENTENDA_LOOKUP.IDX"],
            "payload": PROTECTED["ENTENDA_ENGINE/derived/candidate_cc_001_2046/candidate_index/ENTENDA_PAYLOAD.DAT"]})

    def test_consolidation_render_is_deterministic(self):
        paths = [PENDING, CONSOLIDATION]
        before = [p.read_bytes() for p in paths]
        subprocess.run([sys.executable, str(HERE / "qa02_build_consolidation.py")], cwd=ROOT, check=True, capture_output=True)
        self.assertEqual([p.read_bytes() for p in paths], before)


if __name__ == "__main__":
    unittest.main()
