import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ENTENDA_ENGINE"))
import entenda_engine as E  # noqa: E402
from cc08_build import BASELINE, BATCH, BLOCKS, CONFIG, CORPUS  # noqa: E402

PRODUCTION = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
PRODUCTION_INDEX_SHA = {
    "ENTENDA_LOOKUP.IDX": "38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82",
    "ENTENDA_PAYLOAD.DAT": "6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638",
    "ENTENDA_BUILD_MANIFEST.json": "213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CC08CandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = E.load_corpus(CORPUS)
        cls.base = E.load_corpus(BASELINE)
        cls.active = {r["target_id"]: r for r in cls.rows if r["status"] == "ACTIVE"}
        cls.by_id = {r["explanation_id"]: r for r in cls.rows}
        cls.matrix = json.loads((BATCH / "CC08_DELEGATED_REVIEW_MATRIX.json").read_text(encoding="utf-8"))
        cls.coverage = json.loads((BATCH / "CC08_COVERAGE.json").read_text(encoding="utf-8"))
        cls.ctx = E.NormContext("CC2002", config_path=CONFIG)

    def test_complete_current_scope_and_counts(self):
        expected = ({f"CC2002:ART.{n}" for n in range(401, 551)} - {"CC2002:ART.456"}) | {"CC2002:ART.421-A"}
        produced = {tid for tid in self.active if tid in expected}
        self.assertEqual(produced, expected)
        self.assertEqual((len(self.rows), len(self.active), len(produced)), (712, 549, 150))
        self.assertEqual(sum(r["status"] == "RETIRED" for r in self.rows), 163)

    def test_intercalated_and_revoked_status(self):
        self.assertIn("CC2002:ART.421-A", self.active)
        self.assertNotIn("CC2002:ART.456", self.active)
        self.assertEqual(self.ctx.effective_status("CC2002:ART.456"), "REVOKED")

    def test_cc07_is_preserved_byte_and_record_exact(self):
        self.assertEqual(sha(BASELINE), "922ac3466e0675578dfa8a86f741d320ea1d08c3f45ea737917f1ad9235f10ab")
        final_by_id = {r["explanation_id"]: r for r in self.rows}
        for record in self.base:
            self.assertEqual(final_by_id[record["explanation_id"]], record)
        self.assertEqual((len(self.base), sum(r["status"] == "ACTIVE" for r in self.base)), (562, 399))

    def test_corrections_and_owner_approved_texts_remain(self):
        self.assertEqual(self.active["CC2002:ART.157"]["editorial_version"], 2)
        self.assertEqual(self.active["CC2002:ART.202"]["editorial_version"], 2)
        owner = [r for r in self.rows if r.get("external_human_approval")]
        self.assertEqual(len(owner), 6)

    def test_five_persistent_blocks_and_audits(self):
        for name, members in BLOCKS.items():
            cp = json.loads((BATCH / "checkpoints" / f"CC08_{name}.json").read_text(encoding="utf-8"))
            audit = json.loads((BATCH / "audit_blocks" / f"CC08_AUDIT_{name}.json").read_text(encoding="utf-8"))
            self.assertEqual((cp["expected"], cp["produced"], cp["complete"]), (len(members), len(members), True))
            self.assertEqual((audit["expected"], audit["reviewed"], audit["complete"]), (len(members), len(members), True))

    def test_individual_delegated_review_without_human_claim(self):
        records = self.matrix["records"]
        self.assertEqual((len(records), len({r["target_id"] for r in records})), (150, 150))
        self.assertEqual(self.matrix["classification_counts"], {"A": 150, "B": 0, "C": 0, "D": 0})
        self.assertFalse(self.matrix["human_approval_claimed"])
        self.assertTrue(all(r["formal_review_status"] == "PENDING_HUMAN_REVIEW" for r in records))

    def test_content_contract_utf8_unique_ids_and_payload(self):
        expected = ({f"CC2002:ART.{n}" for n in range(401, 551)} - {"CC2002:ART.456"}) | {"CC2002:ART.421-A"}
        for tid in expected:
            content = self.active[tid]["content"]
            self.assertEqual(set(content), {"o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis"})
            self.assertTrue(all(content[k].strip() for k in ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao")))
            self.assertTrue(content["palavras_dificeis"])
        self.assertEqual(len({r["explanation_id"] for r in self.rows}), len(self.rows))
        self.assertNotIn(b"\xef\xbf\xbd", CORPUS.read_bytes())
        E.validate_corpus(self.rows, self.ctx)

    def test_sensitive_recent_rules_are_covered(self):
        a406 = " ".join(str(v) for v in self.active["CC2002:ART.406"]["content"].values()).lower()
        for fragment in ("selic", "atualização", "zero"):
            self.assertIn(fragment, a406)
        a418 = " ".join(str(v) for v in self.active["CC2002:ART.418"]["content"].values()).lower()
        self.assertIn("arras", a418)
        a421a = " ".join(str(v) for v in self.active["CC2002:ART.421-A"]["content"].values()).lower()
        for fragment in ("paritários", "riscos", "excepcional"):
            self.assertIn(fragment, a421a)

    def test_coverage_and_production_immutability(self):
        self.assertEqual((self.coverage["article_targets_examined"], self.coverage["produced_explanations"], self.coverage["remaining_explanations"]), (151, 150, 0))
        self.assertEqual(self.coverage["intercalated_current_articles"], ["CC2002:ART.421-A"])
        self.assertEqual(self.coverage["fully_revoked_without_active_explanation"], ["CC2002:ART.456"])
        release = json.loads((BATCH / "CC08_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertTrue(release["candidate_only"])
        self.assertFalse(release["deployed"])
        for name, expected in PRODUCTION_INDEX_SHA.items():
            self.assertEqual(sha(PRODUCTION / "index" / name), expected)


if __name__ == "__main__":
    unittest.main()
