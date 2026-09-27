import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "05_COMPILADOR"))
from proof_compiler_r1 import (CanonicalInput, ContractError, load, digest, source_hash,
                            evaluate_pair, run_pairs, run_exhaustive, attach_historical_scores,
                            lexical_phrase, serialized)


class PilotR1ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load(ROOT / "01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_PILOTO_R1.json")
        cls.inp = CanonicalInput(cls.raw)
        cls.pairs = load(ROOT / "06_BENCHMARKS/PARES_PILOTO_V2.json")["pairs"]

    def altered(self, work_id, fn):
        data = copy.deepcopy(self.raw)
        work = next(w for w in data["works"] if w["work_id"] == work_id)
        fn(work)
        return CanonicalInput(data)

    def test_01_counts(self):
        self.assertEqual((25, 21, 36), (len(self.inp.devices), len(self.inp.works), len(self.pairs)))

    def test_02_all_spans(self):
        for d in self.inp.devices.values():
            for n in d["nuclei"]:
                for s in n["source_spans"]:
                    self.assertEqual(s["text"], d["text"][s["start"]:s["end"]])

    def test_03_representation_freeze(self):
        f = load(ROOT / "00_CHECKPOINTS/PILOTO_R1_REPRESENTATIONS_FREEZE.json")
        self.assertEqual(f["input_hash"], self.inp.hash)

    def test_04_six_non_equivalences(self):
        for a, b in self.raw["ontology"]["non_equivalences"]:
            with self.subTest(pair=(a, b)):
                self.assertFalse(self.inp.same_concept(a, b))

    def test_05_intra_word_substring(self):
        self.assertFalse(lexical_phrase("raça", "reparação administração separação"))

    def test_06_curated_synonym(self):
        self.assertTrue(self.inp.same_concept("SIGILO_COMUNICACOES", "COMUNICACAO_PRIVADA"))

    def test_07_ancestry_never_identity(self):
        for edge in self.raw["ontology"]["hierarchy"]:
            self.assertFalse(self.inp.same_concept(edge["parent"], edge["child"]))

    def test_08_negative_not_positive(self):
        inp = self.altered("REF-LIV-0001", lambda w: w["evidences"][0].update(polarity="NEGADA"))
        self.assertNotEqual("ADMISSIVEL", evaluate_pair(inp, "CF88:ART.5:INC.XII", "REF-LIV-0001")["state"])

    def test_09_warning_not_evidence(self):
        inp = self.altered("REF-LIV-0001", lambda w: w["evidences"][0].update(content_type="WARNING_EDITORIAL"))
        self.assertEqual("EVIDENCIA_INSUFICIENTE", evaluate_pair(inp, "CF88:ART.5:INC.XII", "REF-LIV-0001")["state"])

    def test_10_trace_not_evidence(self):
        inp = self.altered("REF-LIV-0001", lambda w: w["evidences"][0].update(content_type="RASTREAMENTO"))
        self.assertFalse(evaluate_pair(inp, "CF88:ART.5:INC.XII", "REF-LIV-0001")["proofs"])

    def test_11_theme_not_evidence(self):
        inp = self.altered("REF-LIV-0001", lambda w: w["evidences"][0].update(content_type="TEMA"))
        self.assertFalse(evaluate_pair(inp, "CF88:ART.5:INC.XII", "REF-LIV-0001")["proofs"])

    def test_12_url_alone_rejected(self):
        with self.assertRaises(ContractError):
            self.altered("REF-LIV-0001", lambda w: w["evidences"][0]["source"].update(paraphrase=""))

    def test_13_source_hash_tamper(self):
        with self.assertRaises(ContractError):
            self.altered("REF-LIV-0001", lambda w: w["evidences"][0]["source"].update(paraphrase="Outra afirmação"))

    def test_14_score_cannot_repair(self):
        row = evaluate_pair(self.inp, "CF88:ART.205", "REF-FIL-0004")
        scored = attach_historical_scores([row], {(row["device_id"], row["work_id"]): 10})[0]
        self.assertEqual("EVIDENCIA_INSUFICIENTE", scored["state"])
        self.assertIsNone(scored["editorial_score"])

    def test_15_one_autonomous_nucleus_suffices(self):
        r = evaluate_pair(self.inp, "CF88:ART.225", "REF-FIL-0007")
        self.assertEqual("ADMISSIVEL", r["state"])
        self.assertEqual(1, len(r["proofs"]))

    def test_16_dependent_requires_anchor(self):
        data = copy.deepcopy(self.raw)
        d = next(d for d in data["devices"] if d["device_id"] == "CF88:ART.225")
        d["nuclei"][0].update(role="DEPENDENTE", depends_on=[d["nuclei"][1]["nucleus_id"]])
        r = evaluate_pair(CanonicalInput(data), d["device_id"], "REF-FIL-0007")
        self.assertEqual("EVIDENCIA_INSUFICIENTE", r["state"])

    def test_17_subject_is_mandatory(self):
        inp = self.altered("REF-LIV-0004", lambda w: w["evidences"][0]["claim"].update(participants=[{"concept": "MAE", "role": "AFFECTED"}]))
        self.assertEqual("EVIDENCIA_INSUFICIENTE", evaluate_pair(inp, "CF88:ART.227", "REF-LIV-0004")["state"])

    def test_18_benchmark_exhaustive_parity(self):
        full = {(r["device_id"], r["work_id"]): r for r in run_exhaustive(self.inp)}
        for row in run_pairs(self.inp, self.pairs):
            self.assertEqual(row, full[row["device_id"], row["work_id"]])

    def test_19_determinism(self):
        self.assertEqual(serialized(run_exhaustive(self.inp)), serialized(run_exhaustive(self.inp)))

    def test_20_duplicate_device(self):
        data = copy.deepcopy(self.raw); data["devices"].append(data["devices"][0])
        with self.assertRaises(ContractError): CanonicalInput(data)

    def test_21_cycle_rejected(self):
        data = copy.deepcopy(self.raw); n = data["devices"][0]["nuclei"][0]
        n["depends_on"] = [n["nucleus_id"]]
        with self.assertRaises(ContractError): CanonicalInput(data)

    def test_22_unknown_concept(self):
        with self.assertRaises(ContractError):
            self.altered("REF-LIV-0001", lambda w: w["evidences"][0]["claim"].update(objects=["inventado"]))

    def test_23_mutated_input(self):
        inp = CanonicalInput(self.raw); inp.data["scope"] = "modified"
        with self.assertRaises(ContractError): run_pairs(inp, self.pairs)

    def test_24_labels_never_features(self):
        data = copy.deepcopy(self.raw); data["works"][0]["rotulo_humano"] = "APROVAR"
        with self.assertRaises(ContractError): CanonicalInput(data)

    def test_25_synthetic_features_rejected(self):
        data = copy.deepcopy(self.raw); data["features_simulacao"] = {"mecanismo": True}
        with self.assertRaises(ContractError): CanonicalInput(data)

    def test_26_absence_is_not_incompatible(self):
        inp = self.altered("REF-LIV-0001", lambda w: w.update(evidences=[]))
        self.assertEqual("EVIDENCIA_INSUFICIENTE", evaluate_pair(inp, "CF88:ART.5:INC.XII", "REF-LIV-0001")["state"])

    def test_27_source_review_blocks(self):
        data = copy.deepcopy(self.raw)
        next(d for d in data["devices"] if d["device_id"] == "CF88:ART.225")["text_identity_status"] = "FONTE_EM_REVISAO"
        self.assertEqual("FONTE_EM_REVISAO", evaluate_pair(CanonicalInput(data), "CF88:ART.225", "REF-FIL-0007")["state"])

    def test_28_proposed_blocks(self):
        inp = self.altered("REF-LIV-0001", lambda w: w["evidences"][0].update(state="PROPOSTA"))
        self.assertEqual("EVIDENCIA_INSUFICIENTE", evaluate_pair(inp, "CF88:ART.5:INC.XII", "REF-LIV-0001")["state"])

    def test_29_scores_only_after_admissibility(self):
        r = evaluate_pair(self.inp, "CF88:ART.225", "REF-FIL-0007")
        self.assertIsNone(r["editorial_score"])
        scored = attach_historical_scores([r], {(r["device_id"], r["work_id"]): 8.5})[0]
        self.assertEqual(8.5, scored["editorial_score"])

    def test_30_no_title_or_address_exceptions(self):
        text = (ROOT / "05_COMPILADOR/proof_compiler_r1.py").read_text(encoding="utf-8")
        self.assertNotIn("CF88:ART.", text)
        for w in self.raw["works"]: self.assertNotIn(w["nome"], text)

    def test_31_partial_scope(self):
        r = evaluate_pair(self.inp, "CF88:ART.41:PAR.1:INC.III", "REF-LIV-0002")
        self.assertEqual("ADMISSIVEL", r["state"])
        self.assertEqual("GARANTIA", r["proofs"][0]["object_reached"])
        self.assertTrue(r["proofs"][0]["not_affirmed"])

    def test_32_source_card_hashes(self):
        for w in self.inp.works.values():
            for e in w["evidences"]: self.assertEqual(source_hash(e["source"]), e["source"]["hash"])


class ParticipantAndProjectionTests(unittest.TestCase):
    def setUp(self):
        self.data = load(ROOT / "01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_PILOTO_R1.json")
        self.inp = CanonicalInput(self.data)

    def test_context_child_is_not_affected(self):
        row = evaluate_pair(self.inp, "CF88:ART.227", "EXP-FIL-006")
        self.assertEqual("EVIDENCIA_INSUFICIENTE", row["state"])
        work = self.inp.works["EXP-FIL-006"]
        self.assertTrue(any(p == {"concept": "CRIANCA", "role": "CONTEXT"} for e in work["evidences"] for p in e["claim"]["participants"]))

    def test_explicit_child_affliction_can_support(self):
        self.assertEqual("ADMISSIVEL", evaluate_pair(self.inp, "CF88:ART.227", "REF-LIV-0004")["state"])

    def test_projection_does_not_claim_legislative_power(self):
        row = evaluate_pair(self.inp, "CF88:ART.24:INC.XII", "EXP-FIL-006")
        self.assertTrue(row["proofs"])
        self.assertTrue(all(p["object_reached"] == "VALOR_DIREITO" for p in row["proofs"]))

    def test_housing_problem_not_program(self):
        self.assertEqual("EVIDENCIA_INSUFICIENTE", evaluate_pair(self.inp, "CF88:ART.23:INC.IX", "REF-LIV-0004")["state"])

    def test_salary_not_health(self):
        self.assertEqual("EVIDENCIA_INSUFICIENTE", evaluate_pair(self.inp, "CF88:ART.198:PAR.7", "EXP-FIL-006")["state"])

    def test_all_roles_required(self):
        del self.data["works"][0]["evidences"][0]["claim"]["participants"]
        with self.assertRaises(ContractError): CanonicalInput(self.data)

if __name__ == "__main__": unittest.main(verbosity=2)
