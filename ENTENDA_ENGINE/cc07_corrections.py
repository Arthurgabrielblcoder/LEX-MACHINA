"""Apply and verify the controlled CC-07 corrections to arts. 157 and 202."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import entenda_engine as E

ROOT = Path(__file__).resolve().parents[1]
CC06 = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_250"
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_400"
BASELINE = CC06 / "CC2002_CC06.entenda.jsonl"
CORPUS = BATCH / "CC2002_CC07_CHECKPOINT01.entenda.jsonl"
EVIDENCE = BATCH / "CC07_CHECKPOINT01_CORRECTIONS.json"
EXPECTED_BASELINE_SHA256 = "3246f2b170b92221a5de64b2baf04edaac5d9b16900e31f7c5f834f64686a817"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def active_by_key(records: list[dict]) -> dict[str, dict]:
    return {r["explanation_key"]: r for r in records if r["status"] == "ACTIVE"}


def drafts(existing: list[dict]) -> dict:
    active = active_by_key(existing)
    art157 = active["ENTENDA/CC2002:ART.157/BASE"]
    art202 = active["ENTENDA/CC2002:ART.202/BASE"]
    content157 = json.loads(json.dumps(art157["content"], ensure_ascii=False))
    content157["palavras_dificeis"] = [{
        "termo": "Lesão",
        "explicacao": "defeito do negócio jurídico caracterizado por prestação manifestamente desproporcional assumida por pessoa em situação de premente necessidade ou inexperiência",
    }]
    content202 = json.loads(json.dumps(art202["content"], ensure_ascii=False))
    content202["o_que_diz"] = (
        "A prescrição pode ser interrompida uma única vez pelas causas legais: despacho judicial que ordena a citação, "
        "observadas as exigências processuais; protesto nas mesmas condições; protesto cambial; apresentação do título de "
        "crédito em inventário ou concurso de credores; ato judicial que constitua o devedor em mora; ou ato inequívoco, "
        "mesmo extrajudicial, pelo qual o devedor reconheça o direito."
    )
    content202["atencao"] = (
        "Não basta qualquer despacho judicial. No caso do inciso I, aplicam-se as regras processuais pertinentes: pelo art. 240 "
        "do CPC, a interrupção operada pelo despacho que ordena a citação retroage à data da propositura da ação, desde que o "
        "autor adote no prazo legal as providências necessárias para viabilizá-la; demora exclusivamente do serviço judiciário "
        "não o prejudica. No regime civil, a interrupção só pode ocorrer uma vez."
    )
    return {
        "schema_version": 1,
        "norma_id": "CC2002",
        "template_version": "ENTENDA-T1",
        "prompt_version": "CC07-CONTROLLED-CORRECTIONS-V1",
        "review_status": "PENDING_HUMAN_REVIEW",
        "authoring": {
            "method": "CONTROLLED_AI_LEGAL_EDITORIAL_CORRECTION",
            "mission": "CC-07",
            "generated_on": "2026-11-08",
            "human_approval_claimed": False,
        },
        "explanations": [
            {
                "target_id": "CC2002:ART.157",
                "role": "OVERVIEW",
                "semantic_autonomy": "AUTONOMOUS",
                "editorial_reason": "Correção controlada do glossário para não sugerir requisito subjetivo de aproveitamento ausente do art. 157.",
                "content": content157,
                "external_layer_notes": [],
                "review_status": "PENDING_HUMAN_REVIEW",
                "editorial_version": 2,
            },
            {
                "target_id": "CC2002:ART.202",
                "role": "OVERVIEW",
                "semantic_autonomy": "AUTONOMOUS",
                "editorial_reason": "Correção controlada para distinguir o despacho que ordena a citação de sua efetivação e explicitar todas as causas legais.",
                "content": content202,
                "external_layer_notes": ["Art. 240 do CPC confrontado na versão consolidada da Câmara dos Deputados em 08/11/2026."],
                "review_status": "PENDING_HUMAN_REVIEW",
                "editorial_version": 2,
            },
        ],
    }


def build(check: bool = False) -> dict:
    if sha(BASELINE.read_bytes()) != EXPECTED_BASELINE_SHA256:
        raise SystemExit("CC07_CC06_BASELINE_HASH_MISMATCH")
    ctx = E.NormContext("CC2002")
    existing = E.load_corpus(BASELINE)
    records = E.stamp(drafts(existing), ctx, existing=existing)
    E.validate_corpus(records, ctx)
    baseline_active = active_by_key(existing)
    corrected_active = active_by_key(records)
    changed = sorted(k for k in baseline_active if baseline_active[k]["content"] != corrected_active[k]["content"] or baseline_active[k].get("external_layer_notes") != corrected_active[k].get("external_layer_notes"))
    if changed != ["ENTENDA/CC2002:ART.157/BASE", "ENTENDA/CC2002:ART.202/BASE"]:
        raise SystemExit("CC07_UNEXPECTED_CORRECTION_SCOPE: " + ", ".join(changed))
    untouched = sum(baseline_active[k] == corrected_active[k] for k in baseline_active if k not in changed)
    if untouched != 248:
        raise SystemExit(f"CC07_UNTOUCHED_ACTIVE_MISMATCH: {untouched}")

    if check:
        if not CORPUS.is_file():
            raise SystemExit("CC07_CHECKPOINT01_MISSING")
        expected = CORPUS.read_bytes()
        import tempfile
        with tempfile.TemporaryDirectory(prefix=".cc07-correction-check-", dir=BATCH) as td:
            tmp = Path(td) / CORPUS.name
            E.write_corpus(records, tmp, ctx)
            if tmp.read_bytes() != expected:
                raise SystemExit("CC07_CHECKPOINT01_NOT_REPRODUCIBLE")
    else:
        E.write_corpus(records, CORPUS, ctx)

    evidence = {
        "schema_version": 1,
        "mission": "CC-07",
        "checkpoint": "01_CORRECTIONS",
        "baseline_branch": "cc06-entenda-cc-115-250",
        "baseline_head": "06a6c29b0a4285e24aab80993cec25385256502b",
        "baseline_corpus_sha256": EXPECTED_BASELINE_SHA256,
        "candidate_corpus_sha256": sha(CORPUS.read_bytes()) if CORPUS.is_file() else None,
        "records": len(records),
        "active": len(corrected_active),
        "historical_versions_preserved": len(records) - len(corrected_active),
        "untouched_active_explanations": untouched,
        "new_editorial_versions": ["ENTENDA/CC2002:ART.157/BASE/2", "ENTENDA/CC2002:ART.202/BASE/2"],
        "corrections": [
            {
                "target_id": "CC2002:ART.157",
                "classification": "B",
                "basis": "O texto legal exige premente necessidade ou inexperiência e desproporção manifesta, sem acrescentar intenção subjetiva de exploração pela contraparte.",
                "preserved_fields": ["o_que_diz", "o_que_significa", "exemplo_pratico", "atencao"],
            },
            {
                "target_id": "CC2002:ART.202",
                "classification": "B",
                "basis": "O inciso I aponta o despacho que ordena a citação, condicionado à observância da lei processual; o art. 240, §§ 1º a 3º, do CPC disciplina retroação, diligência do autor e demora judicial.",
                "all_hypotheses_covered": True,
                "single_interruption_preserved": True,
            },
        ],
        "human_approval_claimed": False,
        "deployed": False,
    }
    encoded = (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if check:
        if not EVIDENCE.is_file() or EVIDENCE.read_bytes() != encoded:
            raise SystemExit("CC07_CORRECTION_EVIDENCE_NOT_REPRODUCIBLE")
    else:
        EVIDENCE.write_bytes(encoded)
    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    print(json.dumps(build(parser.parse_args().check), ensure_ascii=False, indent=2))
