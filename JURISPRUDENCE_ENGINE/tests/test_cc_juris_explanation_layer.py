import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(HERE), str(HERE / "firmware_multinorm")]
import build_cc_juris_explanation_layer as X
import generic_packager as P
import juris_content_quality as Q
import multinorm_sim as S


def docs():
    outputs, metrics = X.build()
    summaries = json.loads(outputs[X.SUMMARIES])["summaries"]
    relations = json.loads(outputs[X.RELATIONS])["relations"]
    return outputs, metrics, summaries, relations


def test_exact_cardinality_and_identity_layers():
    _, metrics, summaries, relations = docs()
    assert (len(summaries), len(relations)) == (574, 653)
    assert len({x["precedent_id"] for x in summaries}) == 574
    assert len({x["relation_id"] for x in relations}) == 653
    assert all(x["human_status"] == "HUMAN_APPROVED" for x in relations)
    assert metrics["group_f_included"] == 0


def test_provenance_and_no_summary_conflict():
    _, metrics, summaries, relations = docs()
    assert metrics["precedent_summary_conflicts"] == 0
    assert metrics["generic_summary_errors"] == 0
    assert all(x["evidence_locator"] and x["evidence_kind"] for x in summaries)
    assert all(x["evidence_locator"] and x["evidence_source"] for x in relations)


def test_all_six_golden_are_ready_and_substantive():
    _, metrics, summaries, relations = docs()
    sm = {x["precedent_id"]: x for x in summaries}
    rx = {x["relation_id"]: x for x in relations}
    assert metrics["fixture_6_content_ready"] == 6
    for rid in X.FIXTURE_IDS:
        assert rx[rid]["content_status"] == "CONTENT_READY"
        assert len(rx[rid]["relation_explanation"]) >= 100
        assert len(sm[rx[rid]["precedent_id"]]["generated_summary"]) >= 100


def test_art_1_fixture_has_verified_boundary_text():
    _, _, _, relations = docs()
    row = next(x for x in relations if x["relation_id"] == "CCMD-006371F260")
    assert row["target_id"] == "CC2002:ART.1"
    assert "personalidade civil" in row["relation_explanation"]
    assert "presunção de capacidade para testar" in row["relation_explanation"]


def test_relation_ficha_schema_is_optional_and_legacy_safe():
    precedent = {"STJ:RESP:1": {"tipo": "acordao", "tribunal": "STJ", "numero": "1", "status": "x", "titulo": "x", "fonte": "x"}}
    legacy = [{"norm": "CC2002", "target_id": "CC2002:ART.1", "precedent_id": "STJ:RESP:1"}]
    old = P.package(legacy, precedent, {"STJ_RESP_1.TXT"}, known_targets={"CC2002:ART.1"})
    state = S.carregar(S.Package(old[f"{P.LAYER}/JUR_LOOKUP.IDX"], old[f"{P.LAYER}/JURISPRUDENCIA.IDX"], {"STJ_RESP_1.TXT"}),
                       "/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt", "1")
    assert state["relations"][0]["arquivo"] == "STJ_RESP_1.TXT"
    new_rel = [dict(legacy[0], relation_ficha="CCMD_TESTE.TXT")]
    new = P.package(new_rel, precedent, set(), new_fichas={"CCMD_TESTE.TXT": "x"}, known_targets={"CC2002:ART.1"})
    state = S.carregar(S.Package(new[f"{P.LAYER}/JUR_LOOKUP.IDX"], new[f"{P.LAYER}/JURISPRUDENCIA.IDX"], {"CCMD_TESTE.TXT"}),
                       "/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt", "1")
    assert state["relations"][0]["arquivo"] == "CCMD_TESTE.TXT"


def test_fixture_and_mass_keep_relation_and_target_counts():
    _, metrics, _, _ = docs()
    assert metrics["fixture"]["post_CC"] == "55/45"
    assert metrics["mass"]["post_CC"] == "702/636"
    assert metrics["fixture"]["distinct_targets_added"] == 6
    assert metrics["mass"]["distinct_targets_added"] == 597


def test_device_projection_has_all_sections_without_target_leakage():
    outputs, metrics, _, _ = docs()
    assert metrics["target_leakage_errors"] == 0
    files = [data.decode("utf-8") for path, data in outputs.items()
             if path.is_relative_to(X.FIXTURE_OUT / "candidate/SD" / P.CONTENT)]
    assert len(files) == 6
    assert all(all(title in text for title in ("O QUE DECIDIU", "POR QUE ESTÁ AQUI", "AUTORIDADE", "FONTE OFICIAL")) for text in files)


def test_build_is_byte_deterministic_in_process():
    a, _ = X.build()
    b, _ = X.build()
    assert a.keys() == b.keys()
    assert all(a[k] == b[k] for k in a)


def test_quality_gate_detects_real_leading_fragments():
    for value in (
        "rato bancário com intuito de novar afasta a discussão.",
        "ase em dados comprobatórios hábeis a tal mister.",
        "º, do CPC. Litigância de má-fé não configurada.",
        "6, e em cinco anos prescreve a pretensão.",
    ):
        flags = Q.quality_flags(value)
        assert "LEADING_FRAGMENT" in flags


def test_quality_gate_detects_truncated_word_and_sentence():
    assert "ABRUPT_END" in Q.quality_flags("A regra disciplina a regulação dos direitos su")
    assert "TRAILING_FRAGMENT" in Q.quality_flags("As pessoas sempre serão cons")
    assert "INCOMPLETE_SENTENCE" in Q.quality_flags("A indenização depende de")


def test_quality_gate_detects_quotes_parentheses_and_enumeration():
    assert "UNBALANCED_QUOTES" in Q.quality_flags('A Corte decidiu que "a dívida não é exigível.')
    assert "UNBALANCED_PARENTHESES" in Q.quality_flags("A regra incide (salvo prova em contrário.")
    assert "BROKEN_ENUMERATION" in Q.quality_flags("1. Aplica-se o prazo trienal.")


def test_quality_gate_detects_raw_excerpt_and_mechanical_why_here():
    assert "RAW_EXCERPT_NOT_SUMMARY" in Q.quality_flags("EMENTA. RECURSO ESPECIAL. PROCESSUAL CIVIL. PRELIMINAR AFASTADA.")
    flags = Q.quality_flags("O vínculo com o art. 682 decorre deste fundamento do acórdão: aplica-se a regra legal.", relation=True)
    assert "TEMPLATE_LIKE_EXPLANATION" in flags


def test_reaudited_corpus_has_no_unresolved_quality_flags():
    _, metrics, summaries, relations = docs()
    assert metrics["unresolved_truncations"] == 0
    assert metrics["unresolved_raw_fragments"] == 0
    assert metrics["template_like_explanations_after"] == 0
    assert all(not x["review_flags"] for x in summaries)
    assert all(not x["review_flags"] for x in relations)


def test_repeated_clause_is_collapsed_without_cutting_the_first_sentence():
    text = (
        "A consignação em pagamento somente libera o devedor quando for integral e tempestiva "
        "A consignação em pagamento somente libera o devedor quando for integral e tempestiva."
    )
    assert Q.collapse_duplicated_clause(text) == (
        "A consignação em pagamento somente libera o devedor quando for integral e tempestiva."
    )


def test_multitarget_precedents_keep_one_summary_and_distinct_explanations():
    _, metrics, summaries, relations = docs()
    assert metrics["multitarget_precedents_audited"] == 67
    assert metrics["target_leakage_errors"] == 0
    by_precedent = {}
    for relation in relations:
        by_precedent.setdefault(relation["precedent_id"], []).append(relation)
    for group in by_precedent.values():
        targets = {x["target_id"] for x in group}
        if len(targets) > 1:
            assert len({x["relation_explanation"] for x in group}) == len(targets)
    assert len({x["precedent_id"] for x in summaries}) == len(summaries)


class TestCcJurisExplanationLayer(unittest.TestCase):
    def test_cardinality(self): test_exact_cardinality_and_identity_layers()
    def test_provenance(self): test_provenance_and_no_summary_conflict()
    def test_golden(self): test_all_six_golden_are_ready_and_substantive()
    def test_art1(self): test_art_1_fixture_has_verified_boundary_text()
    def test_schema(self): test_relation_ficha_schema_is_optional_and_legacy_safe()
    def test_counts(self): test_fixture_and_mass_keep_relation_and_target_counts()
    def test_projection(self): test_device_projection_has_all_sections_without_target_leakage()
    def test_determinism(self): test_build_is_byte_deterministic_in_process()
    def test_leading_fragments(self): test_quality_gate_detects_real_leading_fragments()
    def test_trailing_fragments(self): test_quality_gate_detects_truncated_word_and_sentence()
    def test_balance_and_enumeration(self): test_quality_gate_detects_quotes_parentheses_and_enumeration()
    def test_raw_and_template(self): test_quality_gate_detects_raw_excerpt_and_mechanical_why_here()
    def test_corpus_quality(self): test_reaudited_corpus_has_no_unresolved_quality_flags()
    def test_duplicated_clause(self): test_repeated_clause_is_collapsed_without_cutting_the_first_sentence()
    def test_multitarget_quality(self): test_multitarget_precedents_keep_one_summary_and_distinct_explanations()
