import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
OUT = HERE / "derived/qa05_final_corrections"
QA04_DIR = HERE / "derived/candidate_qa04_cc_001_2046"
QA04 = QA04_DIR / "CC2002_QA04.entenda.jsonl"
QA05_DIR = HERE / "derived/candidate_qa05_cc_001_2046"
QA05 = QA05_DIR / "CC2002_QA05.entenda.jsonl"
PROTECTED = {
    "qa04_corpus": "70a6232437f77e2a0d48e39f1a00dd5ec7e753b39a6d1663c9e34b0742e5e524",
    "qa04_lookup": "b677aa36772dc6d32662a00e26587d517f916bd428e70f3526eb083c29d0b17f",
    "qa04_payload": "756ce344c834730b3e0f2696ef5ce3823d484a7c8ce20254b779cb9a2febde59",
    "qa04_queue": "cceac77f6357ca81dae1653a2812dfc8d607dc8e3833ffecd6ae9955f3759310",
    "qa03_corpus": "dad0a9414fd42b4e5c348ab7e87b90b99501ae4b77c950c5cbfd7dbaef58a496",
    "cc13_corpus": "b9fa2d39b6b4292fe2be466427871e75e14b2a327fb0c35ae190d5443cfd5c8c",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA05FinalCorrectionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = load(OUT / "QA05_CORRECTION_INVENTORY_50.json")
        cls.editorial = load(OUT / "QA05_EDITORIAL_CORRECTIONS_50.json")
        cls.revalidation = load(OUT / "QA05_REVALIDATION_50.json")
        cls.resolution = load(OUT / "QA05_CORRECTION_RESOLUTION_50.json")
        cls.cross = load(OUT / "QA05_CROSS_AUDIT_1101_1105.json")
        cls.qa04 = load_jsonl(QA04)
        cls.qa05 = load_jsonl(QA05)

    def test_all_protected_baselines_and_queue_are_immutable(self):
        self.assertEqual(sha(QA04), PROTECTED["qa04_corpus"])
        self.assertEqual(sha(QA04_DIR / "candidate_index/ENTENDA_LOOKUP.IDX"), PROTECTED["qa04_lookup"])
        self.assertEqual(sha(QA04_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT"), PROTECTED["qa04_payload"])
        self.assertEqual(sha(HERE / "derived/qa04_final_audit/QA04_CORRECTION_QUEUE_50.json"), PROTECTED["qa04_queue"])
        self.assertEqual(sha(HERE / "derived/candidate_qa03_cc_001_2046/CC2002_QA03.entenda.jsonl"),
                         PROTECTED["qa03_corpus"])
        self.assertEqual(sha(HERE / "derived/candidate_cc_001_2046/CC2002_CC13.entenda.jsonl"),
                         PROTECTED["cc13_corpus"])

    def test_inventory_and_editorial_cover_exactly_fifty_findings(self):
        inventory_ids = [row["target_id"] for row in self.inventory["records"]]
        editorial_ids = [row["target_id"] for row in self.editorial["records"]]
        self.assertEqual((self.inventory["total"], self.editorial["total"]), (50, 50))
        self.assertEqual(inventory_ids, editorial_ids)
        self.assertEqual(len(set(editorial_ids)), 50)
        self.assertEqual(Counter(row["severity"] for row in self.editorial["records"]),
                         Counter({"CRÍTICO": 2, "ALTO": 31, "MÉDIO": 17}))
        for row in self.editorial["records"]:
            self.assertEqual(set(row["proposed_content"]),
                             {"o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis"})
            self.assertTrue(row["changed_fields"])
            self.assertFalse(row["independent_approval_claimed"])

    def test_cross_agent_revalidation_confirms_all_fifty(self):
        self.assertEqual((self.revalidation["total"], self.revalidation["decision_counts"]),
                         (50, {"CONFIRMED_CORRECTED": 50}))
        editorial = {row["target_id"]: row for row in self.editorial["records"]}
        for review in self.revalidation["records"]:
            self.assertEqual(review["decision"], "CONFIRMED_CORRECTED")
            self.assertTrue(review["independence_confirmed"])
            self.assertNotIn(editorial[review["target_id"]]["editor_identifier"], review["reviewer"])
            self.assertEqual(review["proposed_content_sha256"],
                             hashlib.sha256(json.dumps(editorial[review["target_id"]]["proposed_content"],
                             ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest())

    def test_critical_1102_and_1103_are_rebuilt_with_correct_rules(self):
        proposals = {row["target_id"]: row["proposed_content"] for row in self.editorial["records"]}
        art1102 = " ".join(str(value) for value in proposals["CC2002:ART.1102"].values()).lower()
        art1103 = " ".join(str(value) for value in proposals["CC2002:ART.1103"].values()).lower()
        for token in ("liquidação", "ato constitutivo", "averbação", "liquidante"):
            self.assertIn(token, art1102)
        for token in ("quinze dias", "semestral", "quotistas", "insolvente", "em liquidação"):
            self.assertIn(token, art1103)
        self.assertEqual(self.resolution["critical_status"],
                         {"CC2002:ART.1102": "CORRIGIDO_E_REVALIDADO",
                          "CC2002:ART.1103": "CORRIGIDO_E_REVALIDADO"})

    def test_directed_neighbor_audit_records_one_out_of_scope_finding(self):
        self.assertEqual(self.cross["new_findings_total"], 1)
        self.assertEqual(self.cross["new_findings"][0]["target_id"], "CC2002:ART.1104")
        queue = load(OUT / "QA05_NEW_FINDINGS_CROSS_AUDIT.json")
        self.assertEqual((queue["total"], queue["findings"][0]["severity"]), (1, "ALTO"))
        old = next(row for row in self.qa04 if row["status"] == "ACTIVE" and row["target_id"] == "CC2002:ART.1104")
        new = next(row for row in self.qa05 if row["status"] == "ACTIVE" and row["target_id"] == "CC2002:ART.1104")
        self.assertEqual(new, old)

    def test_twelve_prebuild_checkpoints_are_complete_and_exact(self):
        for number in range(1, 13):
            checkpoint = load(OUT / f"QA05_CHECKPOINT_{number:02d}.json")
            self.assertEqual(checkpoint["checkpoint"], f"CP{number:02d}")
        sizes = [load(OUT / f"QA05_CHECKPOINT_{number:02d}.json")["total"] for number in range(4, 11)]
        self.assertEqual(sizes, [8, 8, 8, 7, 6, 6, 5])

    def test_resolution_has_fifty_resolved_and_no_original_pending(self):
        self.assertTrue(self.resolution["known_findings_resolved"])
        self.assertFalse(self.resolution["full_corpus_legally_approved"])
        self.assertEqual((self.resolution["confirmed"], self.resolution["corrected"],
                          self.resolution["revalidated"], self.resolution["pending"]), (50, 50, 50, 0))
        self.assertTrue(all(row["status"] == "CORRIGIDO_E_REVALIDADO" for row in self.resolution["records"]))

    def test_candidate_cardinality_active_uniqueness_and_history(self):
        self.assertEqual((len(self.qa04), len(self.qa05)), (2262, 2312))
        active = [row for row in self.qa05 if row["status"] == "ACTIVE"]
        self.assertEqual((len(active), len(self.qa05) - len(active)), (2017, 295))
        self.assertEqual(len({row["target_id"] for row in active}), 2017)

    def test_only_fifty_targets_are_versioned_and_old_content_is_preserved(self):
        old_active = {row["target_id"]: row for row in self.qa04 if row["status"] == "ACTIVE"}
        new_active = {row["target_id"]: row for row in self.qa05 if row["status"] == "ACTIVE"}
        by_id = {row["explanation_id"]: row for row in self.qa05}
        proposals = {row["target_id"]: row for row in self.editorial["records"]}
        self.assertEqual({target for target in old_active if old_active[target] != new_active[target]}, set(proposals))
        for target, proposal in proposals.items():
            old = old_active[target]
            new = new_active[target]
            retired = by_id[old["explanation_id"]]
            self.assertEqual(new["editorial_version"], old["editorial_version"] + 1)
            self.assertEqual(new["content"], proposal["proposed_content"])
            self.assertEqual(new["review_status"], "PENDING_HUMAN_REVIEW")
            self.assertFalse(new["qa05_correction"]["human_approval_claimed"])
            self.assertEqual(retired["content"], old["content"])
            self.assertEqual(retired["source"], old["source"])
            self.assertEqual(retired["superseded_by"], new["explanation_id"])

    def test_candidate_manifest_and_indexes_match_files(self):
        manifest = load(QA05_DIR / "QA05_CANDIDATE_MANIFEST.json")
        self.assertEqual((manifest["records"], manifest["active"], manifest["historical"], manifest["versioned_targets"]),
                         (2312, 2017, 295, 50))
        self.assertEqual(manifest["corpus_sha256"], sha(QA05))
        self.assertEqual(manifest["new_findings_outside_scope"], 1)
        self.assertFalse(manifest["deployed"] or manifest["production_index_modified"])
        for name, metadata in manifest["candidate_index"].items():
            self.assertEqual(metadata["sha256"], sha(QA05_DIR / "candidate_index" / name), name)

    def test_rebuild_is_byte_deterministic(self):
        paths = [OUT / "QA05_CORRECTION_INVENTORY_50.json", OUT / "QA05_EDITORIAL_CORRECTIONS_50.json",
                 OUT / "QA05_REVALIDATION_50.json", OUT / "QA05_CORRECTION_RESOLUTION_50.json",
                 OUT / "QA05_NEW_FINDINGS_CROSS_AUDIT.json", QA05,
                 QA05_DIR / "candidate_index/ENTENDA_LOOKUP.IDX",
                 QA05_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT", QA05_DIR / "QA05_CANDIDATE_MANIFEST.json"]
        before = {path: path.read_bytes() for path in paths}
        for command in ([sys.executable, str(HERE / "qa05_prepare.py")],
                        [sys.executable, str(HERE / "qa05_editorial_integrate.py")],
                        [sys.executable, str(HERE / "qa05_revalidation_integrate.py")],
                        [sys.executable, str(HERE / "qa05_correction_build.py")]):
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        self.assertEqual({path: path.read_bytes() for path in paths}, before)


if __name__ == "__main__":
    unittest.main()
