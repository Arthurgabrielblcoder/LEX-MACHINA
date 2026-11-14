import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

import ENTENDA_ENGINE.entenda_engine as E


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
OUT = HERE / "derived/qa07_high_findings_resolution"
BASE = HERE / "derived/candidate_qa06_cc_001_2046/CC2002_QA06.entenda.jsonl"
CANDIDATE = HERE / "derived/candidate_qa07_cc_001_2046"
CORPUS = CANDIDATE / "CC2002_QA07.entenda.jsonl"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA07ResolutionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cp6 = load_json(OUT / "QA07_CP06.json")
        cls.cp7 = load_json(OUT / "QA07_CP07.json")
        cls.final = load_json(OUT / "QA07_ACCEPTED_CONTENT_FINAL.json")
        cls.manifest = load_json(CANDIDATE / "QA07_CANDIDATE_MANIFEST.json")
        cls.base = E.load_corpus(BASE)
        cls.candidate = E.load_corpus(CORPUS)

    def test_all_priority_findings_have_independent_resolution(self):
        self.assertEqual((self.cp6["high_findings_resolved"], self.cp6["pending_high"]), (41, 0))
        self.assertEqual((self.cp6["indeterminate_reviewed"], self.cp6["pending_indeterminate"]), (10, 0))
        self.assertEqual((self.cp6["indeterminate_confirmed_for_correction"],
                          self.cp6["indeterminate_materially_sufficient"]), (8, 2))
        self.assertEqual((self.final["target_total"], self.final["resolved_finding_total"]), (31, 49))
        ids = [fid for row in self.final["records"] for fid in row["finding_ids"]]
        self.assertEqual((len(ids), len(set(ids))), (49, 49))

    def test_rejections_and_microrevision_are_preserved_in_review_chain(self):
        negative = load_json(OUT / "QA07_REVIEW_HIGH_B.json")
        self.assertEqual(negative["decision_counts"], {"ACEITA": 13, "REJEITADA": 2})
        revised = load_json(OUT / "QA07_REVIEW_HIGH_B_REVISION_2.json")
        self.assertTrue(revised["all_prior_objections_resolved"])
        self.assertEqual(revised["decision_counts"], {"ACEITA": 2, "REJEITADA": 0})
        micro = load_json(OUT / "QA07_REVIEW_MICROREVISION_1541.json")
        self.assertEqual(micro["records"][0]["decision"], "ACEITA")
        self.assertTrue(micro["records"][0]["official_text_copy_guard_resolved"])

    def test_candidate_cardinality_versioning_and_unique_active_targets(self):
        active = [r for r in self.candidate if r["status"] == "ACTIVE"]
        historical = [r for r in self.candidate if r["status"] != "ACTIVE"]
        self.assertEqual((len(self.candidate), len(active), len(historical)), (2344, 2017, 327))
        self.assertEqual(len({r["target_id"] for r in active}), 2017)
        self.assertEqual(len({r["explanation_id"] for r in self.candidate}), 2344)
        base_active = {r["target_id"]: r for r in self.base if r["status"] == "ACTIVE"}
        new_active = {r["target_id"]: r for r in active}
        changed = {tid for tid in base_active if base_active[tid]["explanation_id"] != new_active[tid]["explanation_id"]}
        self.assertEqual(changed, {r["target_id"] for r in self.final["records"]})
        self.assertEqual(len(changed), 31)
        for tid in set(base_active) - changed:
            self.assertEqual(base_active[tid], new_active[tid])

    def test_qa06_and_medium_queue_are_byte_preserved(self):
        self.assertEqual(sha(BASE), "4f7481e5ec697eddc26e5e412ff9f5394c983fcfbd5cff6b678bdb7d9811aaf5")
        queue = HERE / "derived/qa06_subdivision_material_audit/QA06_B_DEFINITIVE_CORRECTION_QUEUE.json"
        self.assertEqual(sha(queue), "d981890d1fecca4fe0e76eeefb1d6d5d398a336be065ebf7c4998ec2641668f9")
        medium = load_json(OUT / "QA07_MEDIUM_420_PRESERVATION_MANIFEST.json")
        self.assertEqual(len(medium["findings"]), 420)
        self.assertTrue(all(r["final_severity"] == "MÉDIO" for r in medium["findings"]))
        self.assertFalse(medium["editorial_changes_authorized"])

    def test_candidate_contract_hashes_and_no_deployment_claim(self):
        self.assertEqual(self.manifest["corpus_sha256"], sha(CORPUS))
        self.assertEqual(self.cp7["lookup_sha256"], sha(CANDIDATE / "candidate_index/ENTENDA_LOOKUP.IDX"))
        self.assertEqual(self.cp7["payload_sha256"], sha(CANDIDATE / "candidate_index/ENTENDA_PAYLOAD.DAT"))
        self.assertFalse(self.manifest["production_index_modified"])
        self.assertFalse(self.manifest["human_approved"])
        self.assertFalse(self.manifest["deployed"])
        self.assertTrue(all(r["review_status"] == "PENDING_HUMAN_REVIEW"
                            for r in self.candidate if r["status"] == "ACTIVE" and "qa07_resolution" in r))

    def test_finalization_and_candidate_are_byte_deterministic(self):
        paths = [OUT / "QA07_ACCEPTED_CONTENT_FINAL.json", OUT / "QA07_CP06.json",
                 CORPUS, CANDIDATE / "candidate_index/ENTENDA_LOOKUP.IDX",
                 CANDIDATE / "candidate_index/ENTENDA_PAYLOAD.DAT", OUT / "QA07_CP07.json"]
        before = [sha(p) for p in paths]
        subprocess.run([sys.executable, "-X", "utf8", str(HERE / "qa07_finalize_revalidation.py")],
                       cwd=ROOT, check=True, capture_output=True)
        subprocess.run([sys.executable, "-X", "utf8", str(HERE / "qa07_build_candidate.py")],
                       cwd=ROOT, check=True, capture_output=True)
        self.assertEqual(before, [sha(p) for p in paths])


if __name__ == "__main__":
    unittest.main()
