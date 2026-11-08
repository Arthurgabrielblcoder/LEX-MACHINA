import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ENTENDA_ENGINE"))
import entenda_engine as E  # noqa: E402

BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"


def load(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class CC03BRefinementTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = load(BATCH / "CC2002_CC03_BASELINE.entenda.jsonl")
        baseline = BATCH / "CC2002_CC03B_BASELINE.entenda.jsonl"
        cls.current = load(baseline if baseline.is_file() else BATCH / "CC2002_CC02.entenda.jsonl")
        cls.active = {r["target_id"]: r for r in cls.current if r["status"] == "ACTIVE"}

    def test_all_records_refined_and_versions_preserved(self):
        previous = {r["target_id"]: r for r in self.prior if r["status"] == "ACTIVE"}
        self.assertEqual(116, len(self.active))
        self.assertEqual(250, len(self.current))
        self.assertTrue(all(self.active[tid]["content"] != old["content"] for tid, old in previous.items()))
        current_ids = {r["explanation_id"] for r in self.current}
        self.assertTrue(all(r["explanation_id"] in current_ids for r in self.prior))
        self.assertEqual({"PENDING_HUMAN_REVIEW"}, {r["review_status"] for r in self.active.values()})

    def test_no_filler_phrases_remain(self):
        banned = (
            "A explicação cobre o artigo como unidade",
            "O termo técnico central aqui é",
            "O dispositivo deve ser lido dentro do tema",
            "Na aplicação, é preciso relacionar a regra",
            "O exemplo é apenas didático",
            "Antes de decidir ou agir, confirme",
        )
        text = json.dumps([r["content"] for r in self.active.values()], ensure_ascii=False)
        self.assertFalse(any(phrase in text for phrase in banned))

    def test_complex_articles_have_specific_coverage(self):
        expected = {
            "CC2002:ART.4": ("pródigos", "indígenas", "curatela"),
            "CC2002:ART.50": ("desvio", "confusão patrimonial", "grupo econômico"),
            "CC2002:ART.62": ("segurança alimentar", "direitos humanos", "religiosas"),
            "CC2002:ART.113": ("conduta posterior", "práticas de mercado", "não redigiu"),
        }
        for tid, terms in expected.items():
            text = json.dumps(self.active[tid]["content"], ensure_ascii=False).casefold()
            self.assertTrue(all(term.casefold() in text for term in terms), (tid, terms))

    def test_repetition_metrics_improve(self):
        m = json.loads((BATCH / "CC03B_REPETITION_METRICS.json").read_text(encoding="utf-8"))
        before, after = m["cc03_before"], m["cc03b_after"]
        self.assertEqual(696, before["filler_occurrences_total"])
        self.assertEqual(0, after["filler_occurrences_total"])
        self.assertLess(after["repeated_sentence_excess_occurrences"], before["repeated_sentence_excess_occurrences"])
        self.assertLess(after["average_words_per_record"], before["average_words_per_record"])

    def test_sample_and_engine_contract(self):
        sample = json.loads((BATCH / "CC03B_HUMAN_REVIEW_SAMPLE_15.json").read_text(encoding="utf-8"))
        required = {"CC2002:ART.1", "CC2002:ART.2", "CC2002:ART.4", "CC2002:ART.50", "CC2002:ART.62", "CC2002:ART.113"}
        self.assertEqual(15, sample["count"])
        self.assertTrue(required <= {c["target_id"] for c in sample["cases"]})
        E.validate_corpus(self.current, E.NormContext("CC2002"))


if __name__ == "__main__":
    unittest.main()
