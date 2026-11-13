import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "derived/qa06_subdivision_material_audit"
BASELINE = HERE / "derived/candidate_qa05_cc_001_2046/CC2002_QA05.entenda.jsonl"
CANDIDATE = HERE / "derived/candidate_qa06_cc_001_2046"
CORPUS = CANDIDATE / "CC2002_QA06.entenda.jsonl"
TARGET = "CC2002:ART.1104"
EXPECTED = {
    "corpus": "4f7481e5ec697eddc26e5e412ff9f5394c983fcfbd5cff6b678bdb7d9811aaf5",
    "lookup": "95fb9a2c076ce0b124b26ae96cb9ff15ac5ed9b5ee2dad6eab8c718299e57e08",
    "payload": "091f05cdd991771d3366996528a89385735e7c813e14745e54c5db4714a2e26d",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class QA06FrontATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_jsonl(BASELINE)
        cls.candidate = load_jsonl(CORPUS)
        cls.baseline_active = {row["target_id"]: row for row in cls.baseline if row["status"] == "ACTIVE"}
        cls.candidate_active = {row["target_id"]: row for row in cls.candidate if row["status"] == "ACTIVE"}
        cls.review = load(OUT / "QA06_A_INDEPENDENT_REVALIDATION_1104_V2.json")
        cls.resolution = load(OUT / "QA06_A_CORRECTION_RESOLUTION_1104.json")

    def test_candidate_cardinality_and_versioning(self):
        self.assertEqual((len(self.baseline), len(self.baseline_active)), (2312, 2017))
        self.assertEqual((len(self.candidate), len(self.candidate_active)), (2313, 2017))
        self.assertEqual(sum(row["status"] != "ACTIVE" for row in self.candidate), 296)
        old = self.baseline_active[TARGET]
        new = self.candidate_active[TARGET]
        self.assertEqual((old["editorial_version"], new["editorial_version"]), (2, 3))
        self.assertEqual(new["explanation_id"], "ENTENDA/CC2002:ART.1104/BASE/3")
        retired = next(row for row in self.candidate if row["explanation_id"] == old["explanation_id"])
        self.assertEqual((retired["content"], retired["source"]), (old["content"], old["source"]))
        self.assertEqual(retired["superseded_by"], new["explanation_id"])

    def test_only_art_1104_active_explanation_changed(self):
        self.assertEqual(set(self.baseline_active), set(self.candidate_active))
        changed = []
        for target in self.baseline_active:
            before, after = self.baseline_active[target], self.candidate_active[target]
            if before["content"] != after["content"] or before["explanation_id"] != after["explanation_id"]:
                changed.append(target)
            if target != TARGET:
                self.assertEqual((before["content"], before["source"], before["explanation_id"]),
                                 (after["content"], after["source"], after["explanation_id"]))
        self.assertEqual(changed, [TARGET])

    def test_final_independent_review_is_objection_free(self):
        record = self.review["records"][0]
        self.assertEqual(record["decision"], "CONFIRMED_CORRECTED")
        self.assertEqual(record["objections"], [])
        self.assertEqual(record["prior_objection_resolution"]["status"], "RESOLVED")
        self.assertFalse(record["independence_declaration"]["reviewer_was_editor"])
        self.assertFalse(record["human_approval_claimed"])
        self.assertEqual({value["status"] for value in record["field_assessments"].values()}, {"CONFIRMED"})

    def test_art_1104_content_has_correct_legal_boundary(self):
        content = self.candidate_active[TARGET]["content"]
        joined = json.dumps(content, ensure_ascii=False).casefold()
        self.assertNotIn("no que couber", content["o_que_diz"].casefold())
        self.assertNotIn("balanço anual", joined)
        self.assertNotIn("registra nomeação", joined)
        self.assertIn("art. 1.103", content["atencao"])
        self.assertIn("art. 1.105", content["atencao"])
        self.assertIn("administradores", content["o_que_significa"])
        self.assertEqual(content["palavras_dificeis"][0]["termo"], "Sociedade liquidanda")

    def test_candidate_hashes_and_production_safety(self):
        self.assertEqual(sha(CORPUS), EXPECTED["corpus"])
        self.assertEqual(sha(CANDIDATE / "candidate_index/ENTENDA_LOOKUP.IDX"), EXPECTED["lookup"])
        self.assertEqual(sha(CANDIDATE / "candidate_index/ENTENDA_PAYLOAD.DAT"), EXPECTED["payload"])
        manifest = load(CANDIDATE / "QA06_CANDIDATE_MANIFEST.json")
        self.assertTrue(manifest["candidate_only"])
        self.assertFalse(manifest["deployed"])
        self.assertFalse(manifest["production_index_modified"])
        self.assertEqual(self.resolution["status"], "ART_1104_CORRECTED_AND_INDEPENDENTLY_REVALIDATED")

    def test_build_is_deterministic(self):
        before = {"corpus": sha(CORPUS),
                  "lookup": sha(CANDIDATE / "candidate_index/ENTENDA_LOOKUP.IDX"),
                  "payload": sha(CANDIDATE / "candidate_index/ENTENDA_PAYLOAD.DAT")}
        subprocess.run([sys.executable, str(HERE / "qa06_correction_build.py")],
                       cwd=HERE.parent, check=True, capture_output=True, text=True, encoding="utf-8")
        after = {"corpus": sha(CORPUS),
                 "lookup": sha(CANDIDATE / "candidate_index/ENTENDA_LOOKUP.IDX"),
                 "payload": sha(CANDIDATE / "candidate_index/ENTENDA_PAYLOAD.DAT")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
