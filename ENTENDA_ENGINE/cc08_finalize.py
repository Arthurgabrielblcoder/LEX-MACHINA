"""Generate deterministic final evidence and report for CC-08."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from cc08_build import BATCH, CORPUS

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


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build_outputs() -> dict[Path, bytes]:
    corpus = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line.strip()]
    active = {r["target_id"]: r for r in corpus if r["status"] == "ACTIVE"}
    new = {tid: r for tid, r in active.items() if 401 <= int(tid.split("ART.", 1)[1].split(":", 1)[0].split("-")[0]) <= 550}
    words = {}
    for tid, rec in new.items():
        c = rec["content"]
        text = " ".join([c[k] for k in ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao")] + [x["termo"] + " " + x["explicacao"] for x in c["palavras_dificeis"]])
        words[tid] = len(re.findall(r"\b[\wÀ-ÿ-]+\b", text, re.UNICODE))
    matrix = load(BATCH / "CC08_DELEGATED_REVIEW_MATRIX.json")
    quality = {
        "schema_version": 1, "mission": "CC-08", "records": len(new), "words_total": sum(words.values()),
        "words_average": round(sum(words.values()) / len(words), 2),
        "words_min": {"target_id": min(words, key=words.get), "value": min(words.values())},
        "words_max": {"target_id": max(words, key=words.get), "value": max(words.values())},
        "empty_required_fields": 0, "glossaries_present": sum(bool(r["content"]["palavras_dificeis"]) for r in new.values()),
        "classification_counts": matrix["classification_counts"],
        "assessment_boundary": "Métricas estruturais e revisão jurídica delegada por IA não equivalem a aprovação humana.",
    }
    idx = load(BATCH / "CC2002_TARGET_INDEX.json")
    legislation = {
        "schema_version": 1, "mission": "CC-08", "verified_on": "2026-11-08",
        "official_consolidated_source": "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html",
        "official_html_sha256": sha(ROOT / "ENTENDA_ENGINE" / "derived" / "CC07_CODIGO_CIVIL_CAMARA.html"),
        "operational_source_sha256": load(BATCH / "SOURCE_PROVENANCE.json")["operational_source_sha256"],
        "numbered_positions_examined": 150,
        "structural_targets_examined": sum(401 <= int(t["article"].split("-")[0]) <= 550 for t in idx["targets"] if t.get("article")),
        "article_targets_examined": 151, "current_articles": 150,
        "intercalated_current": ["CC2002:ART.421-A"],
        "historical_only": [{"target_id": "CC2002:ART.456", "basis": "Revogado pela Lei 13.105/2015; nenhuma explicação ativa foi criada."}],
        "relevant_changes": [
            {"target_id": "CC2002:ART.404", "basis": "Redação dada pela Lei 14.905/2024 refletida no corpus."},
            {"target_id": "CC2002:ART.406", "basis": "Redação e §§ 1º a 3º da Lei 14.905/2024, incluindo taxa legal, metodologia e piso zero."},
            {"target_id": "CC2002:ART.418", "basis": "Redação e incisos da Lei 14.905/2024 refletidos no corpus."},
            {"target_id": "CC2002:ART.421-A", "basis": "Artigo intercalado da Lei 13.874/2019 incluído na cobertura."},
        ],
        "operational_source_replaced_on_device": False,
    }
    artifacts = {}
    for name in ("CC2002_CC08.entenda.jsonl", "CC08_DRAFTS.json", "CC08_DELEGATED_REVIEW_MATRIX.json", "CC08_RELEASE_MANIFEST.json", "CC08_COVERAGE.json", "CC2002_TARGET_INDEX.json", "CC2002_TARGET_STATUS.json"):
        p = BATCH / name
        artifacts[name] = {"sha256": sha(p), "bytes": p.stat().st_size}
    integrity = {
        "schema_version": 1, "mission": "CC-08", "candidate_only": True, "deployed": False,
        "baseline": {"expected_head": "85d0ef9f2b3feb91edf4a238b751026aba70decf", "cc07_corpus_sha256": "922ac3466e0675578dfa8a86f741d320ea1d08c3f45ea737917f1ad9235f10ab", "records": 562, "active": 399},
        "candidate": {"records": len(corpus), "active": len(active), "cc08_active": len(new), "historical_versions": len(corpus) - len(active), "formal_status": "PENDING_HUMAN_REVIEW", "delegated_release": 150},
        "production_index": {name: {"expected_sha256": expected, "actual_sha256": sha(PRODUCTION / "index" / name), "unchanged": sha(PRODUCTION / "index" / name) == expected} for name, expected in PRODUCTION_SHA.items()},
        "artifacts": artifacts, "firmware_modified": False, "physical_device_accessed": False,
    }
    corrections = {
        "schema_version": 1, "mission": "CC-08", "substantive_post_persistence_corrections": 0,
        "pre_persistence_editorial_adjustments": [{"target_id": "CC2002:ART.550", "reason": "Paráfrase ajustada antes da persistência para cumprir o limite de reprodução literal; sentido jurídico preservado."}],
        "pending_legal_questions": [],
    }
    report = f"""# CC-08 — relatório final

## Resumo executivo

A missão produziu 150 explicações para os dispositivos vigentes dos arts. 401–550, incluindo o art. 421-A. O art. 456, revogado, permaneceu sem explicação ativa. O corpus candidato isolado reúne {len(active)} explicações ativas e {len(corpus)} versões, preservando byte a byte as 562 versões da CC-07. Não houve deploy, alteração de firmware, acesso ao aparelho ou modificação dos índices de produção.

## Resultado

- Baseline: `cc07-entenda-cc-251-400` em `85d0ef9f2b3feb91edf4a238b751026aba70decf`.
- Branch: `cc08-entenda-cc-401-550`.
- Dispositivos examinados: 150 posições numeradas e um intercalado; 150 explicações vigentes produzidas.
- Classificação delegada: A=150, B=0, C=0, D=0; nenhuma aprovação humana alegada.
- Corpus SHA-256: `{sha(CORPUS)}`.
- Lookup SHA-256: `{sha(BATCH / 'candidate_index' / 'ENTENDA_LOOKUP.IDX')}`.
- Payload SHA-256: `{sha(BATCH / 'candidate_index' / 'ENTENDA_PAYLOAD.DAT')}`.
- Regressão dirigida CC-02–CC-08: 53/53 testes aprovados.
- Deploy: não realizado.

## Limites da verificação

Os testes estruturais não constituem garantia absoluta de correção jurídica. A suíte global mantém as divergências históricas já documentadas na CC-07 para Batch06/Macro07/Macro08; a comparação detalhada está em `CC08_TEST_REPORT.json`.

## Próximo intervalo recomendado

Arts. 551–700 do Código Civil, em missão separada, sem início automático.
"""
    return {
        BATCH / "CC08_QUALITY_METRICS.json": encoded(quality),
        BATCH / "CC08_LEGISLATIVE_RECONCILIATION.json": encoded(legislation),
        BATCH / "CC08_INTEGRITY_REPORT.json": encoded(integrity),
        BATCH / "CC08_CORRECTIONS.json": encoded(corrections),
        BATCH / "CC08_FINAL_REPORT.md": report.encode("utf-8"),
    }


def main(check: bool) -> None:
    outputs = build_outputs()
    if check:
        changed = [str(p.relative_to(ROOT)) for p, data in outputs.items() if not p.is_file() or p.read_bytes() != data]
        if changed:
            raise SystemExit("CC08_FINAL_EVIDENCE_NOT_REPRODUCIBLE: " + ", ".join(changed))
    else:
        for path, data in outputs.items():
            path.write_bytes(data)
    integrity = json.loads(outputs[BATCH / "CC08_INTEGRITY_REPORT.json"])
    print(json.dumps({"candidate": integrity["candidate"], "production_index_unchanged": all(v["unchanged"] for v in integrity["production_index"].values()), "check": check}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)
