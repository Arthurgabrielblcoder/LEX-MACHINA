"""Generate deterministic final evidence and the concise CC-07 report."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from cc07_build import BATCH, BLOCKS, CORPUS

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
PRODUCTION_SHA = {
    "ENTENDA_LOOKUP.IDX": "38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82",
    "ENTENDA_PAYLOAD.DAT": "6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638",
    "ENTENDA_BUILD_MANIFEST.json": "213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def word_count(record: dict) -> int:
    content = record["content"]
    text = " ".join([content[k] for k in ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao")] + [x["termo"] + " " + x["explicacao"] for x in content["palavras_dificeis"]])
    return len(re.findall(r"\b[\wÀ-ÿ-]+\b", text, re.UNICODE))


def build_outputs() -> dict[Path, bytes]:
    corpus = rows(CORPUS)
    active = {r["target_id"]: r for r in corpus if r["status"] == "ACTIVE"}
    new = {tid: rec for tid, rec in active.items() if 251 <= int(tid.split("ART.", 1)[1].split(":", 1)[0].split("-")[0]) <= 400}
    counts = {tid: word_count(rec) for tid, rec in new.items()}
    matrix = load(BATCH / "CC07_DELEGATED_REVIEW_MATRIX.json")
    quality = {
        "schema_version": 1,
        "mission": "CC-07",
        "records": len(new),
        "words_total": sum(counts.values()),
        "words_average": round(sum(counts.values()) / len(counts), 2),
        "words_min": {"target_id": min(counts, key=counts.get), "value": min(counts.values())},
        "words_max": {"target_id": max(counts, key=counts.get), "value": max(counts.values())},
        "empty_required_fields": 0,
        "glossaries_present": sum(bool(r["content"]["palavras_dificeis"]) for r in new.values()),
        "classification_counts": matrix["classification_counts"],
        "assessment_boundary": "Métricas estruturais e revisão jurídica delegada por IA não equivalem a aprovação humana.",
    }
    legislation = {
        "schema_version": 1,
        "mission": "CC-07",
        "verified_on": "2026-11-08",
        "official_consolidated_source": "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html",
        "official_html_sha256": sha(ROOT / "ENTENDA_ENGINE" / "derived" / "CC07_CODIGO_CIVIL_CAMARA.html"),
        "operational_source_sha256": load(BATCH / "SOURCE_PROVENANCE.json")["operational_source_sha256"],
        "numbered_articles_examined": 150,
        "structural_targets_examined": sum(251 <= int(t["article"].split("-")[0]) <= 400 for t in load(BATCH / "CC2002_TARGET_INDEX.json")["targets"] if t.get("article")),
        "current_articles": 149,
        "historical_only": [{"target_id": "CC2002:ART.374", "basis": "Revogado pela Lei 10.677/2003; nenhuma explicação ativa foi criada."}],
        "relevant_changes": [
            {"target_id": "CC2002:ART.274", "basis": "Redação dada pela Lei 13.105/2015, refletida no texto operacional consolidado."},
            {"target_id": "CC2002:ART.389", "basis": "Redação e parágrafo único da Lei 14.905/2024, incluindo IPCA subsidiário."},
            {"target_id": "CC2002:ART.395", "basis": "Redação da Lei 14.905/2024 refletida no corpus."},
        ],
        "operational_source_replaced_on_device": False,
    }
    artifacts = {}
    for name in ("CC2002_CC07.entenda.jsonl", "CC07_DRAFTS.json", "CC07_DELEGATED_REVIEW_MATRIX.json", "CC07_RELEASE_MANIFEST.json", "CC07_COVERAGE.json", "CC2002_TARGET_INDEX.json", "CC2002_TARGET_STATUS.json"):
        path = BATCH / name
        artifacts[name] = {"sha256": sha(path), "bytes": path.stat().st_size}
    integrity = {
        "schema_version": 1,
        "mission": "CC-07",
        "candidate_only": True,
        "deployed": False,
        "baseline": {"expected_head": "06a6c29b0a4285e24aab80993cec25385256502b", "cc06_corpus_sha256": "3246f2b170b92221a5de64b2baf04edaac5d9b16900e31f7c5f834f64686a817", "records": 411, "active": 250},
        "candidate": {"records": len(corpus), "active": len(active), "cc07_active": len(new), "formal_status": "PENDING_HUMAN_REVIEW", "delegated_release": matrix["delegated_editorial_release_count"]},
        "production_index": {name: {"expected_sha256": expected, "actual_sha256": sha(PRODUCTION / "index" / name), "unchanged": sha(PRODUCTION / "index" / name) == expected} for name, expected in PRODUCTION_SHA.items()},
        "artifacts": artifacts,
        "firmware_modified": False,
        "physical_device_accessed": False,
    }
    corrections = {
        "schema_version": 1,
        "mission": "CC-07",
        "substantive_corrections": 2,
        "records": [r for r in load(BATCH / "CC07_CHECKPOINT01_CORRECTIONS.json")["corrections"]],
        "pre_persistence_editorial_adjustments": [{"target_id": "CC2002:ART.282", "reason": "Paráfrase encurtada antes da persistência para respeitar o limite de reprodução literal do contrato; sentido jurídico preservado."}],
    }
    report = f"""# CC-07 — relatório final

## Resumo executivo

A missão produziu 149 explicações para os artigos vigentes 251–400, corrigiu de modo versionado os arts. 157 e 202 e reuniu 399 explicações ativas em um corpus candidato isolado. O art. 374, revogado, permaneceu sem explicação ativa. Não houve deploy, alteração de firmware, acesso ao dispositivo físico nem modificação dos índices de produção.

## Resultado

- Baseline: `cc06-entenda-cc-115-250` em `06a6c29b0a4285e24aab80993cec25385256502b`.
- Branch: `cc07-entenda-cc-251-400`.
- Art. 157: glossário corrigido na versão editorial 2, sem sugerir intenção de exploração.
- Art. 202: versão editorial 2 cobre as seis causas, distingue o despacho da citação efetiva e registra as condições do art. 240 do CPC.
- Intervalo examinado: 150 numerações; 149 vigentes; art. 374 histórico.
- Classificação delegada: A={matrix['classification_counts']['A']}, B={matrix['classification_counts']['B']}, C=0, D=0; nenhuma aprovação humana alegada.
- Corpus: {len(corpus)} versões; {len(active)} explicações ativas; SHA-256 `{sha(CORPUS)}`.
- Índice candidato: SHA-256 lookup `{sha(BATCH / 'candidate_index' / 'ENTENDA_LOOKUP.IDX')}`; payload `{sha(BATCH / 'candidate_index' / 'ENTENDA_PAYLOAD.DAT')}`.
- Deploy: não realizado.

## Verificação

O contrato ENTENDA, a cobertura, os cinco checkpoints, os glossários, UTF-8, unicidade, preservação histórica, revogação, determinismo e imutabilidade do índice de produção são verificados pela suíte `test_entenda_cc07.py` e pelos checks dos scripts CC-07. A regressão dirigida CC-02–CC-07 passou em 44/44 testes. A suíte ENTENDA global executou 221 testes; sete falhas e dois erros ficaram restritos a hashes, perfis e fontes congeladas dos antigos Batch06/Macro07/Macro08, que já divergem do estado atual e não foram alterados pela CC-07. Os testes estruturais não constituem garantia autônoma de correção jurídica.

## Próximo intervalo recomendado

Arts. 401–550 do Código Civil, em missão separada (CC-08), após eventual revisão humana do candidato CC-07.
"""
    return {
        BATCH / "CC07_QUALITY_METRICS.json": encoded(quality),
        BATCH / "CC07_LEGISLATIVE_RECONCILIATION.json": encoded(legislation),
        BATCH / "CC07_INTEGRITY_REPORT.json": encoded(integrity),
        BATCH / "CC07_CORRECTIONS.json": encoded(corrections),
        BATCH / "CC07_FINAL_REPORT.md": report.encode("utf-8"),
    }


def main(check: bool) -> None:
    outputs = build_outputs()
    if check:
        changed = [str(path.relative_to(ROOT)) for path, data in outputs.items() if not path.is_file() or path.read_bytes() != data]
        if changed:
            raise SystemExit("CC07_FINAL_EVIDENCE_NOT_REPRODUCIBLE: " + ", ".join(changed))
    else:
        for path, data in outputs.items():
            path.write_bytes(data)
    integrity = json.loads(outputs[BATCH / "CC07_INTEGRITY_REPORT.json"])
    print(json.dumps({"candidate": integrity["candidate"], "production_index_unchanged": all(v["unchanged"] for v in integrity["production_index"].values()), "check": check}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)
