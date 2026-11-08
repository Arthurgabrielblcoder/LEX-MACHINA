import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ENTENDA_ENGINE"))

import entenda_engine as E  # noqa: E402
from cc07_build import BLOCKS, CONFIG  # noqa: E402

BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_400"
CC06 = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_250"
PRODUCTION = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
CORPUS = BATCH / "CC2002_CC07.entenda.jsonl"
CHECKPOINT01 = BATCH / "CC2002_CC07_CHECKPOINT01.entenda.jsonl"
PRODUCTION_INDEX_SHA = {
    "ENTENDA_LOOKUP.IDX": "38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82",
    "ENTENDA_PAYLOAD.DAT": "6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638",
    "ENTENDA_BUILD_MANIFEST.json": "213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CC07CandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = E.load_corpus(CORPUS)
        cls.prior = E.load_corpus(CHECKPOINT01)
        cls.active = {r["target_id"]: r for r in cls.rows if r["status"] == "ACTIVE"}
        cls.by_id = {r["explanation_id"]: r for r in cls.rows}
        cls.matrix = json.loads((BATCH / "CC07_DELEGATED_REVIEW_MATRIX.json").read_text(encoding="utf-8"))
        cls.coverage = json.loads((BATCH / "CC07_COVERAGE.json").read_text(encoding="utf-8"))
        cls.ctx = E.NormContext("CC2002", config_path=CONFIG)

    def test_complete_current_scope_and_counts(self):
        expected = {f"CC2002:ART.{n}" for n in range(251, 401) if n != 374}
        produced = {tid for tid in self.active if tid in expected}
        self.assertEqual(produced, expected)
        self.assertEqual((len(self.rows), len(self.active), len(produced)), (562, 399, 149))
        self.assertEqual(sum(r["status"] == "RETIRED" for r in self.rows), 163)

    def test_article_374_is_historical_and_has_no_active_explanation(self):
        self.assertNotIn("CC2002:ART.374", self.active)
        status = json.loads((BATCH / "CC2002_TARGET_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["targets"]["CC2002:ART.374"]["status"], "HISTORICAL_ONLY")
        self.assertEqual(self.ctx.effective_status("CC2002:ART.374"), "REVOKED")

    def test_corrections_are_versioned_and_previous_versions_preserved(self):
        for article in (157, 202):
            old = self.by_id[f"ENTENDA/CC2002:ART.{article}/BASE/1"]
            new = self.by_id[f"ENTENDA/CC2002:ART.{article}/BASE/2"]
            self.assertEqual((old["status"], old["superseded_by"]), ("RETIRED", new["explanation_id"]))
            self.assertEqual(new["status"], "ACTIVE")
        glossary = self.active["CC2002:ART.157"]["content"]["palavras_dificeis"][0]["explicacao"]
        self.assertIn("premente necessidade ou inexperiência", glossary)
        self.assertNotIn("aproveitada", glossary)
        art202 = " ".join(self.active["CC2002:ART.202"]["content"].values() if False else [self.active["CC2002:ART.202"]["content"]["o_que_diz"], self.active["CC2002:ART.202"]["content"]["atencao"]])
        for fragment in ("despacho judicial", "protesto cambial", "inventário", "ato judicial", "ato inequívoco", "art. 240", "uma vez"):
            self.assertIn(fragment, art202)

    def test_checkpoint01_preserves_other_248_active_records(self):
        cc06 = {r["explanation_key"]: r for r in E.load_corpus(CC06 / "CC2002_CC06.entenda.jsonl") if r["status"] == "ACTIVE"}
        checkpoint = {r["explanation_key"]: r for r in self.prior if r["status"] == "ACTIVE"}
        changed = {key for key in cc06 if cc06[key] != checkpoint[key]}
        self.assertEqual(changed, {"ENTENDA/CC2002:ART.157/BASE", "ENTENDA/CC2002:ART.202/BASE"})
        self.assertEqual(sum(cc06[key] == checkpoint[key] for key in cc06 if key not in changed), 248)

    def test_all_prior_versions_are_preserved_exactly(self):
        final_by_id = {r["explanation_id"]: r for r in self.rows}
        for record in self.prior:
            self.assertEqual(final_by_id[record["explanation_id"]], record)

    def test_five_persistent_blocks_and_audits_are_complete(self):
        for name, members in BLOCKS.items():
            checkpoint = json.loads((BATCH / "checkpoints" / f"CC07_{name}.json").read_text(encoding="utf-8"))
            audit = json.loads((BATCH / "audit_blocks" / f"CC07_AUDIT_{name}.json").read_text(encoding="utf-8"))
            self.assertEqual((checkpoint["expected"], checkpoint["produced"], checkpoint["complete"]), (len(members), len(members), True))
            self.assertEqual((audit["expected"], audit["reviewed"], audit["complete"]), (len(members), len(members), True))

    def test_delegated_review_is_individual_and_not_human_approval(self):
        records = self.matrix["records"]
        self.assertEqual((len(records), len({r["target_id"] for r in records})), (151, 151))
        self.assertEqual(self.matrix["classification_counts"], {"A": 149, "B": 2, "C": 0, "D": 0})
        self.assertEqual(self.matrix["delegated_editorial_release_count"], 151)
        self.assertFalse(self.matrix["human_approval_claimed"])
        self.assertTrue(all(r["formal_review_status"] == "PENDING_HUMAN_REVIEW" for r in records))
        self.assertFalse(any(r["human_approval_claimed"] for r in records))

    def test_content_contract_glossaries_utf8_and_unique_ids(self):
        expected = {f"CC2002:ART.{n}" for n in range(251, 401) if n != 374}
        for target_id in expected:
            content = self.active[target_id]["content"]
            self.assertEqual(set(content), {"o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis"})
            self.assertTrue(all(content[k].strip() for k in ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao")))
            self.assertTrue(content["palavras_dificeis"])
        self.assertEqual(len({r["explanation_id"] for r in self.rows}), len(self.rows))
        self.assertNotIn(b"\xef\xbf\xbd", CORPUS.read_bytes())

    def test_engine_contract_and_coverage(self):
        E.validate_corpus(self.rows, self.ctx)
        self.assertEqual(self.coverage["numbered_articles_examined"], 150)
        self.assertEqual(self.coverage["produced_explanations"], 149)
        self.assertEqual(self.coverage["remaining_explanations"], 0)
        self.assertEqual(self.coverage["fully_revoked_without_active_explanation"], ["CC2002:ART.374"])

    def test_candidate_only_and_production_index_immutable(self):
        release = json.loads((BATCH / "CC07_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertTrue(release["candidate_only"])
        self.assertFalse(release["deployed"])
        self.assertFalse(release["production_index_modified"])
        for name, expected in PRODUCTION_INDEX_SHA.items():
            self.assertEqual(sha(PRODUCTION / "index" / name), expected)
            self.assertTrue((BATCH / "candidate_index" / name).is_file())


if __name__ == "__main__":
    unittest.main()
