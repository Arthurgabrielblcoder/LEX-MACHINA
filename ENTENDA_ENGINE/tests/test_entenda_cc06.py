import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ENTENDA_ENGINE"))

import entenda_engine as E  # noqa: E402
from cc06_editorial import BLOCKS, ROWS  # noqa: E402

BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_250"
PRODUCTION = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
CORPUS = BATCH / "CC2002_CC06.entenda.jsonl"
BASELINE = BATCH / "CC2002_CC05_BASELINE.entenda.jsonl"
PRODUCTION_INDEX_SHA = {
    "ENTENDA_LOOKUP.IDX": "38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82",
    "ENTENDA_PAYLOAD.DAT": "6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638",
    "ENTENDA_BUILD_MANIFEST.json": "213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CC06CandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = E.load_corpus(CORPUS)
        cls.base = E.load_corpus(BASELINE)
        cls.active = {r["target_id"]: r for r in cls.rows if r["status"] == "ACTIVE"}
        cls.matrix = json.loads((BATCH / "CC06_DELEGATED_REVIEW_MATRIX.json").read_text(encoding="utf-8"))
        cls.coverage = json.loads((BATCH / "CC06_COVERAGE.json").read_text(encoding="utf-8"))

    def test_complete_current_scope_and_counts(self):
        expected = {f"CC2002:ART.{n}" for n in range(115, 251) if n not in {194, 227, 229, 230}}
        expected |= {"CC2002:ART.206-A", "CC2002:ART.227:PAR.UNICO"}
        produced = {tid for tid in self.active if tid.split("ART.", 1)[1].split(":", 1)[0] in ROWS}
        self.assertEqual(produced, expected)
        self.assertEqual((len(self.rows), len(self.active), len(produced)), (411, 250, 134))
        self.assertEqual(sum(r["status"] == "RETIRED" for r in self.rows), 161)

    def test_revoked_targets_are_fail_closed(self):
        for tid in ("CC2002:ART.194", "CC2002:ART.227", "CC2002:ART.229", "CC2002:ART.230"):
            self.assertNotIn(tid, self.active)
        status = json.loads((BATCH / "CC2002_TARGET_STATUS.json").read_text(encoding="utf-8"))
        historical = {tid for tid, data in status["targets"].items() if data["status"] == "HISTORICAL_ONLY"}
        self.assertTrue({"CC2002:ART.194", "CC2002:ART.227", "CC2002:ART.229", "CC2002:ART.230"} <= historical)

    def test_cc05_corpus_is_byte_and_record_exact(self):
        self.assertEqual(sha(BASELINE), "c6a37520b7ed357645f722bde451204832657185ffa85e89cdbff69e2b56b8d2")
        self.assertEqual(BASELINE.read_bytes(), (PRODUCTION / "CC2002_CC02.entenda.jsonl").read_bytes())
        self.assertEqual(self.rows[: len(self.base)], self.base)
        self.assertEqual((len(self.base), sum(r["status"] == "ACTIVE" for r in self.base)), (277, 116))

    def test_delegated_review_is_individual_and_not_human_approval(self):
        records = self.matrix["records"]
        self.assertEqual((len(records), len({r["target_id"] for r in records})), (134, 134))
        self.assertEqual(self.matrix["classification_counts"], {"A": 134, "B": 0, "C": 0, "D": 0})
        self.assertEqual(self.matrix["delegated_editorial_release_count"], 134)
        self.assertFalse(self.matrix["human_approval_claimed"])
        self.assertTrue(all(r["formal_review_status"] == "PENDING_HUMAN_REVIEW" for r in records))
        self.assertFalse(any(r["human_approval_claimed"] for r in records))
        self.assertFalse(any(r["review_status"] == "HUMAN_APPROVED_T1" for r in self.active.values()))

    def test_five_persistent_blocks_are_complete(self):
        expected = {"115_140": 26, "141_165": 25, "166_190": 25, "191_220": 30, "221_250": 28}
        for name, count in expected.items():
            checkpoint = json.loads((BATCH / "checkpoints" / f"CC06_{name}.json").read_text(encoding="utf-8"))
            audit = json.loads((BATCH / "audit_blocks" / f"CC06_AUDIT_{name}.json").read_text(encoding="utf-8"))
            self.assertEqual((checkpoint["expected"], checkpoint["produced"], checkpoint["complete"]), (count, count, True))
            self.assertEqual((audit["expected"], audit["reviewed"], audit["complete"]), (count, count, True))

    def test_content_contract_glossaries_and_specificity(self):
        forbidden = ("este dispositivo trata", "consulte um profissional", "depende do caso concreto")
        new = [self.active[ROWS[n].get("target") or f"CC2002:ART.{n}"] for n in ROWS]
        for rec in new:
            self.assertEqual(set(rec["content"]), {"o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis"})
            self.assertTrue(all(rec["content"][k].strip() for k in ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao")))
            self.assertTrue(rec["content"]["palavras_dificeis"])
            text = " ".join(str(v) for v in rec["content"].values()).lower()
            self.assertFalse(any(phrase in text for phrase in forbidden), rec["target_id"])

    def test_unique_ids_utf8_and_engine_validation(self):
        self.assertEqual(len({r["explanation_id"] for r in self.rows}), len(self.rows))
        self.assertNotIn(b"\xef\xbf\xbd", CORPUS.read_bytes())
        E.validate_corpus(self.rows, E.NormContext("CC2002"))

    def test_candidate_only_and_production_index_immutable(self):
        release = json.loads((BATCH / "CC06_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertTrue(release["candidate_only"])
        self.assertFalse(release["deployed"])
        self.assertFalse(release["production_index_modified"])
        for name, expected in PRODUCTION_INDEX_SHA.items():
            self.assertEqual(sha(PRODUCTION / "index" / name), expected)
            self.assertTrue((BATCH / "candidate_index" / name).is_file())

    def test_coverage_manifest_documents_legislative_edges(self):
        self.assertEqual(self.coverage["produced_explanations"], 134)
        self.assertEqual(self.coverage["remaining_explanations"], 0)
        self.assertEqual(self.coverage["inserted_current_articles"], ["CC2002:ART.206-A"])
        self.assertEqual(set(self.coverage["fully_revoked_without_active_explanation"]), {"CC2002:ART.194", "CC2002:ART.229", "CC2002:ART.230"})
        self.assertIn("CC2002:ART.227:PAR.UNICO", self.coverage["special_anchor"])


if __name__ == "__main__":
    unittest.main()
