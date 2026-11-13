import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
OUT = HERE / "derived/qa04_final_audit"
QA03_DIR = HERE / "derived/candidate_qa03_cc_001_2046"
QA03 = QA03_DIR / "CC2002_QA03.entenda.jsonl"
QA04_DIR = HERE / "derived/candidate_qa04_cc_001_2046"
QA04 = QA04_DIR / "CC2002_QA04.entenda.jsonl"
PROTECTED = {
    "corpus": "dad0a9414fd42b4e5c348ab7e87b90b99501ae4b77c950c5cbfd7dbaef58a496",
    "lookup": "9cda2855e4534b7a7cefc833f2e2498a91cf81666395cf83a064d3d69705eeba",
    "payload": "6a5ea56bffc14c06df9ac1f16c145b02e2115bacbfce1d87858ba342e77d6268",
    "queue": "8c798f79745f4d878b882e582bbfa71effbcb6c99c7763bf77cfc51e2b5151df",
    "findings": "4fd7700b9c66c370405a8ce7d9004222a9af2202efa4cabf4c0a2ff581062ba1",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA04FinalAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = load(OUT / "QA04_AUDIT_1000_QUEUE.json")
        cls.audit = load(OUT / "QA04_B_AUDIT_1000.json")
        cls.findings = load(OUT / "QA04_B_NEW_FINDINGS.json")["findings"]
        cls.consolidation = load(OUT / "QA04_B_CONSOLIDATION.json")
        cls.editorial = load(OUT / "QA04_EDITORIAL_CORRECTIONS_4.json")
        cls.revalidation = load(OUT / "QA04_EDITORIAL_REVALIDATION_4.json")
        cls.resolution = load(OUT / "QA04_CORRECTION_RESOLUTION_4.json")
        cls.qa03 = load_jsonl(QA03)
        cls.qa04 = load_jsonl(QA04)

    def test_protected_qa03_and_source_queues_are_immutable(self):
        self.assertEqual(sha(QA03), PROTECTED["corpus"])
        self.assertEqual(sha(QA03_DIR / "candidate_index/ENTENDA_LOOKUP.IDX"), PROTECTED["lookup"])
        self.assertEqual(sha(QA03_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT"), PROTECTED["payload"])
        self.assertEqual(sha(HERE / "derived/qa03_corrections_and_audit/QA03_UNAUDITED_REMAINING_1000.json"),
                         PROTECTED["queue"])
        self.assertEqual(sha(HERE / "derived/qa03_corrections_and_audit/QA03_B_NEW_FINDINGS.json"),
                         PROTECTED["findings"])

    def test_exact_frozen_queue_is_unchanged_and_ordered(self):
        records = self.queue["records"]
        self.assertEqual((self.queue["total"], len(records)), (1000, 1000))
        self.assertEqual([row["queue_position"] for row in records], list(range(389, 1389)))
        self.assertEqual((records[0]["target_id"], records[-1]["target_id"]),
                         ("CC2002:ART.518", "CC2002:ART.2025"))
        self.assertEqual(len({row["target_id"] for row in records}), 1000)

    def test_three_independent_modules_cover_queue_once(self):
        files = ("QA04_B_REVIEW_001_333.json", "QA04_B_REVIEW_334_666.json", "QA04_B_REVIEW_667_1000.json")
        records = [row for name in files for row in load(OUT / name)["records"]]
        self.assertEqual([len(load(OUT / name)["records"]) for name in files], [333, 333, 334])
        self.assertEqual([row["target_id"] for row in records],
                         [row["target_id"] for row in self.queue["records"]])
        self.assertEqual(len({row["target_id"] for row in records}), 1000)

    def test_twenty_checkpoints_have_exact_nonoverlapping_blocks(self):
        checkpoints = [load(OUT / f"QA04_B_CHECKPOINT_{number:02d}.json") for number in range(1, 21)]
        records = [row for checkpoint in checkpoints for row in checkpoint["records"]]
        self.assertEqual([checkpoint["examined"] for checkpoint in checkpoints], [50] * 20)
        self.assertEqual([row["residual_position"] for row in records], list(range(1, 1001)))
        self.assertEqual([row["queue_position"] for row in records], list(range(389, 1389)))
        self.assertEqual([row["target_id"] for row in records],
                         [row["target_id"] for row in self.queue["records"]])

    def test_all_1000_records_have_individual_legal_evidence(self):
        records = self.audit["records"]
        self.assertEqual((self.audit["status"], self.audit["audited_total"], len(records)),
                         ("COMPLETE_1000", 1000, 1000))
        comparisons = set()
        for row in records:
            self.assertTrue(row["sources"] and row["current_law_snapshot"] and row["legal_segments_checked"])
            self.assertEqual(len(row["checks"]["field_sha256"]), 5)
            self.assertTrue(all(row["checks"][key] for key in ("requirements", "exceptions", "consequences")))
            self.assertIn(row["result"], ("ACHADO", "SEM_ACHADO_NO_ESCOPO_VERIFICADO"))
            self.assertGreater(len(row["comparison"]), 80)
            comparisons.add(row["comparison"])
        self.assertEqual(len(comparisons), 1000)

    def test_new_findings_are_exact_traceable_and_not_silently_corrected(self):
        actual = [row["finding"] for row in self.audit["records"] if row["finding"]]
        self.assertEqual(actual, self.findings)
        self.assertEqual(len(self.findings), 50)
        self.assertEqual(Counter(row["severity"] for row in self.findings),
                         Counter({"ALTO": 31, "MÉDIO": 17, "CRÍTICO": 2}))
        self.assertEqual({row["target_id"] for row in self.findings if row["severity"] == "CRÍTICO"},
                         {"CC2002:ART.1102", "CC2002:ART.1103"})
        for finding in self.findings:
            for key in ("problematic_field", "problematic_excerpt", "legal_basis", "source_url", "nature",
                        "severity", "legal_or_pedagogical_consequence", "correction_direction", "confidence"):
                self.assertTrue(finding.get(key), (finding["target_id"], key))

    def test_full_audit_complete_is_not_full_legal_approval(self):
        coverage = self.consolidation["coverage"]
        self.assertTrue(self.consolidation["full_corpus_audit_complete"])
        self.assertFalse(self.consolidation["full_corpus_legally_approved"])
        self.assertEqual((coverage["prior_unique_audited"], coverage["qa04_new_unique_audited"],
                          coverage["unique_audited_accumulated"], coverage["still_unaudited"]),
                         (1017, 1000, 2017, 0))
        self.assertEqual(sum(coverage["by_book_qa04"].values()), 1000)
        pending = load(OUT / "QA04_B_PENDING.json")
        self.assertEqual((pending["status"], pending["total"], pending["records"]), ("COMPLETE", 0, []))

    def test_four_prior_findings_are_corrected_and_independently_revalidated(self):
        targets = {"CC2002:ART.228", "CC2002:ART.288", "CC2002:ART.371", "CC2002:ART.500"}
        self.assertEqual({row["target_id"] for row in self.editorial["records"]}, targets)
        self.assertEqual(self.revalidation["decision_counts"], {"CONFIRMED_CORRECTED": 4})
        self.assertFalse(self.revalidation["independence_declaration"]["same_person_or_agent"])
        self.assertEqual((self.resolution["corrected"], self.resolution["revalidated"], self.resolution["pending"]),
                         (4, 4, 0))
        self.assertEqual(self.resolution["severity_counts"], {"ALTO": 3, "MÉDIO": 1})

    def test_candidate_versions_four_targets_and_preserves_history(self):
        self.assertEqual((len(self.qa03), len(self.qa04)), (2258, 2262))
        active = [row for row in self.qa04 if row["status"] == "ACTIVE"]
        self.assertEqual((len(active), len(self.qa04) - len(active)), (2017, 245))
        self.assertEqual(len({row["target_id"] for row in active}), 2017)
        old_active = {row["target_id"]: row for row in self.qa03 if row["status"] == "ACTIVE"}
        new_active = {row["target_id"]: row for row in active}
        by_id = {row["explanation_id"]: row for row in self.qa04}
        proposals = {row["target_id"]: row for row in self.editorial["records"]}
        for target, proposal in proposals.items():
            old = old_active[target]
            new = new_active[target]
            retired = by_id[old["explanation_id"]]
            self.assertEqual(new["editorial_version"], old["editorial_version"] + 1)
            self.assertEqual(new["content"], proposal["proposed_content"])
            self.assertEqual(new["review_status"], "PENDING_HUMAN_REVIEW")
            self.assertFalse(new["qa04_correction"]["human_approval_claimed"])
            self.assertEqual(retired["content"], old["content"])
            self.assertEqual(retired["source"], old["source"])
            self.assertEqual(retired["superseded_by"], new["explanation_id"])

    def test_candidate_manifest_and_indexes_match(self):
        manifest = load(QA04_DIR / "QA04_CANDIDATE_MANIFEST.json")
        self.assertEqual((manifest["records"], manifest["active"], manifest["historical"], manifest["versioned_targets"]),
                         (2262, 2017, 245, 4))
        self.assertEqual(manifest["corpus_sha256"], sha(QA04))
        self.assertFalse(manifest["deployed"] or manifest["production_index_modified"])
        for name, metadata in manifest["candidate_index"].items():
            self.assertEqual(metadata["sha256"], sha(QA04_DIR / "candidate_index" / name), name)

    def test_qa04_rebuild_is_byte_deterministic(self):
        paths = [OUT / "QA04_AUDIT_1000_QUEUE.json", OUT / "QA04_EDITORIAL_CORRECTIONS_4.json",
                 OUT / "QA04_B_AUDIT_1000.json", OUT / "QA04_B_NEW_FINDINGS.json",
                 OUT / "QA04_B_CONSOLIDATION.json", OUT / "QA04_CORRECTION_RESOLUTION_4.json",
                 QA04, QA04_DIR / "candidate_index/ENTENDA_LOOKUP.IDX",
                 QA04_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT", QA04_DIR / "QA04_CANDIDATE_MANIFEST.json"]
        before = {path: path.read_bytes() for path in paths}
        commands = [[sys.executable, str(HERE / "qa04_prepare.py")],
                    [sys.executable, str(HERE / "qa04_editorial_prepare.py")],
                    [sys.executable, str(HERE / "qa04_correction_build.py")],
                    [sys.executable, str(HERE / "qa04_audit_build.py"), "--through-checkpoint", "20"]]
        for command in commands:
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        self.assertEqual({path: path.read_bytes() for path in paths}, before)


if __name__ == "__main__":
    unittest.main()
