import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
OUT = HERE / "derived/qa03_corrections_and_audit"
BASE_DIR = HERE / "derived/candidate_cc_001_2046"
BASE = BASE_DIR / "CC2002_CC13.entenda.jsonl"
CANDIDATE_DIR = HERE / "derived/candidate_qa03_cc_001_2046"
CANDIDATE = CANDIDATE_DIR / "CC2002_QA03.entenda.jsonl"
PROTECTED = {
    "corpus": "b9fa2d39b6b4292fe2be466427871e75e14b2a327fb0c35ae190d5443cfd5c8c",
    "lookup": "60f1de336f2f9ecbc5e671d0a6a9223cf20e47ab5826a5501b53f9a67551866e",
    "payload": "9fb3f3a1b6f1c1926eda0818fc753f2d0348194cf25b0a333fc6fa18c48222cb",
    "qa02_corrections": "0d8cce6b3b9c335e7f71502b88c81488ae53732a7927708f2f83701504896e6b",
}
CRITICAL = {"CC2002:ART.1258", "CC2002:ART.1276", "CC2002:ART.1641", "CC2002:ART.2016"}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA03CorrectionsAndAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = load_json(OUT / "QA03_UNAUDITED_FULL_QUEUE.json")
        cls.selected = load_json(OUT / "QA03_AUDIT_388_QUEUE.json")
        cls.remaining = load_json(OUT / "QA03_UNAUDITED_REMAINING_1000.json")
        cls.audit = load_json(OUT / "QA03_B_AUDIT_388.json")
        cls.findings = load_json(OUT / "QA03_B_NEW_FINDINGS.json")["findings"]
        cls.b_consolidation = load_json(OUT / "QA03_B_CONSOLIDATION.json")
        cls.editorial = load_json(OUT / "QA03_EDITORIAL_CORRECTIONS_78.json")
        cls.revalidation = load_json(OUT / "QA03_EDITORIAL_REVALIDATION_78.json")
        cls.resolution = load_json(OUT / "QA03_CORRECTION_RESOLUTION_78.json")
        cls.base = load_jsonl(BASE)
        cls.candidate = load_jsonl(CANDIDATE)

    def test_protected_cc13_and_qa02_artifacts_are_immutable(self):
        self.assertEqual(sha(BASE), PROTECTED["corpus"])
        self.assertEqual(sha(BASE_DIR / "candidate_index/ENTENDA_LOOKUP.IDX"), PROTECTED["lookup"])
        self.assertEqual(sha(BASE_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT"), PROTECTED["payload"])
        self.assertEqual(sha(HERE / "derived/qa02_independent_legal_audit/QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_04.json"),
                         PROTECTED["qa02_corrections"])

    def test_queues_partition_exactly_1388_into_388_and_1000(self):
        full_ids = [row["target_id"] for row in self.full["records"]]
        selected_ids = [row["target_id"] for row in self.selected["records"]]
        remaining_ids = [row["target_id"] for row in self.remaining["records"]]
        self.assertEqual((self.full["total"], self.selected["total"], self.remaining["total"]), (1388, 388, 1000))
        self.assertEqual(full_ids, selected_ids + remaining_ids)
        self.assertEqual(len(full_ids), len(set(full_ids)))
        self.assertEqual((selected_ids[0], selected_ids[-1], remaining_ids[0]),
                         ("CC2002:ART.115", "CC2002:ART.517", "CC2002:ART.518"))

    def test_sixteen_front_b_checkpoints_cover_each_selected_record_once(self):
        checkpoints = [load_json(OUT / f"QA03_B_CHECKPOINT_{number:02d}.json") for number in range(1, 17)]
        records = [row for checkpoint in checkpoints for row in checkpoint["records"]]
        self.assertEqual([checkpoint["examined"] for checkpoint in checkpoints], [25] * 15 + [13])
        self.assertEqual([row["target_id"] for row in records],
                         [row["target_id"] for row in self.selected["records"]])
        self.assertEqual([row["queue_position"] for row in records], list(range(1, 389)))

    def test_388_individual_audits_have_complete_evidence(self):
        records = self.audit["records"]
        self.assertEqual((self.audit["status"], self.audit["audited_total"], len(records)),
                         ("COMPLETE_388", 388, 388))
        self.assertEqual(len({row["target_id"] for row in records}), 388)
        for row in records:
            self.assertTrue(row["sources"] and row["current_law_snapshot"] and row["legal_segments_checked"])
            self.assertEqual(len(row["checks"]["field_sha256"]), 5)
            self.assertTrue(all(row["checks"][key] for key in ("requirements", "exceptions", "consequences")))
            self.assertIn(row["result"], ("ACHADO", "SEM_ACHADO_NO_ESCOPO_VERIFICADO"))
            self.assertGreater(len(row["comparison"]), 40)

    def test_four_preliminary_findings_are_exact_and_traceable(self):
        self.assertEqual([row["target_id"] for row in self.findings],
                         ["CC2002:ART.228", "CC2002:ART.288", "CC2002:ART.371", "CC2002:ART.500"])
        self.assertEqual(Counter(row["severity"] for row in self.findings), Counter({"ALTO": 3, "MÉDIO": 1}))
        self.assertEqual([row["finding"] for row in self.audit["records"] if row["finding"]], self.findings)
        for finding in self.findings:
            for key in ("problematic_field", "problematic_excerpt", "legal_basis", "source_url", "nature",
                        "severity", "legal_or_pedagogical_consequence", "correction_direction", "confidence"):
                self.assertTrue(finding.get(key), (finding["target_id"], key))

    def test_front_b_accumulated_coverage_and_residual_are_exact(self):
        coverage = self.b_consolidation["coverage"]
        self.assertEqual((coverage["qa02_unique_audited"], coverage["qa03_new_unique_audited"],
                          coverage["unique_audited_accumulated"], coverage["still_unaudited"]),
                         (629, 388, 1017, 1000))
        self.assertFalse(self.b_consolidation["full_corpus_audit_complete"])
        self.assertEqual(self.b_consolidation["continuation"]["queue_sha256"], sha(OUT / "QA03_UNAUDITED_REMAINING_1000.json"))

    def test_all_78_corrections_were_independently_revalidated(self):
        self.assertEqual((self.editorial["total"], self.revalidation["total"], self.resolution["total"]), (78, 78, 78))
        self.assertEqual(self.revalidation["decision_counts"], {"CONFIRMED_CORRECTED": 78})
        self.assertEqual(self.resolution["severity_counts"], {"ALTO": 51, "CRÍTICO": 4, "MÉDIO": 23})
        self.assertEqual(set(self.resolution["critical_status"]), CRITICAL)
        self.assertTrue(all(value == "CORRECTED_AND_INDEPENDENTLY_REVALIDATED"
                            for value in self.resolution["critical_status"].values()))
        self.assertEqual((self.resolution["corrected"], self.resolution["revalidated"], self.resolution["pending"]),
                         (78, 78, 0))

    def test_candidate_versions_corrections_without_mutating_old_content(self):
        self.assertEqual((len(self.base), len(self.candidate)), (2180, 2258))
        self.assertEqual(sum(row["status"] == "ACTIVE" for row in self.candidate), 2017)
        self.assertEqual(sum(row["status"] != "ACTIVE" for row in self.candidate), 241)
        active = [row for row in self.candidate if row["status"] == "ACTIVE"]
        self.assertEqual(len({row["target_id"] for row in active}), 2017)
        base_active = {row["target_id"]: row for row in self.base if row["status"] == "ACTIVE"}
        candidate_active = {row["target_id"]: row for row in active}
        proposals = {row["target_id"]: row for row in self.editorial["records"]}
        candidate_by_id = {row["explanation_id"]: row for row in self.candidate}
        for target, proposal in proposals.items():
            old = base_active[target]
            new = candidate_active[target]
            retired = candidate_by_id[old["explanation_id"]]
            self.assertEqual(new["editorial_version"], old["editorial_version"] + 1)
            self.assertEqual(new["content"], proposal["proposed_content"])
            self.assertEqual(new["review_status"], "PENDING_HUMAN_REVIEW")
            self.assertFalse(new["qa03_correction"]["human_approval_claimed"])
            self.assertEqual(retired["content"], old["content"])
            self.assertEqual(retired["source"], old["source"])
            self.assertEqual(retired["superseded_by"], new["explanation_id"])

    def test_candidate_manifest_and_indexes_match_files(self):
        manifest = load_json(CANDIDATE_DIR / "QA03_CANDIDATE_MANIFEST.json")
        self.assertEqual((manifest["records"], manifest["active"], manifest["historical"], manifest["versioned_targets"]),
                         (2258, 2017, 241, 78))
        self.assertTrue(manifest["candidate_only"])
        self.assertFalse(manifest["deployed"] or manifest["production_index_modified"])
        self.assertEqual(manifest["corpus_sha256"], sha(CANDIDATE))
        for name, metadata in manifest["candidate_index"].items():
            self.assertEqual(metadata["sha256"], sha(CANDIDATE_DIR / "candidate_index" / name), name)

    def test_all_builds_are_deterministic(self):
        paths = [
            OUT / "QA03_UNAUDITED_FULL_QUEUE.json", OUT / "QA03_AUDIT_388_QUEUE.json",
            OUT / "QA03_UNAUDITED_REMAINING_1000.json", OUT / "QA03_EDITORIAL_REVALIDATION_78.json",
            OUT / "QA03_B_AUDIT_388.json", OUT / "QA03_B_NEW_FINDINGS.json", OUT / "QA03_B_CONSOLIDATION.json",
            OUT / "QA03_CORRECTION_RESOLUTION_78.json", CANDIDATE,
            CANDIDATE_DIR / "candidate_index/ENTENDA_LOOKUP.IDX",
            CANDIDATE_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT",
            CANDIDATE_DIR / "QA03_CANDIDATE_MANIFEST.json",
        ]
        before = {path: path.read_bytes() for path in paths}
        commands = [
            [sys.executable, str(HERE / "qa03_prepare.py")],
            [sys.executable, str(HERE / "qa03_revalidate_corrections.py")],
            [sys.executable, str(HERE / "qa03_audit_build.py"), "--through-checkpoint", "16"],
            [sys.executable, str(HERE / "qa03_correction_build.py")],
        ]
        for command in commands:
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        self.assertEqual({path: path.read_bytes() for path in paths}, before)


if __name__ == "__main__":
    unittest.main()
