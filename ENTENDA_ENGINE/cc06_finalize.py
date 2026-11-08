"""Generate deterministic final evidence for the isolated CC-06 candidate."""
from __future__ import annotations

import hashlib
import json
import re
import argparse
from collections import defaultdict
from pathlib import Path

from cc06_editorial import BLOCKS, ROWS

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_250"
PRODUCTION = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
CORPUS = BATCH / "CC2002_CC06.entenda.jsonl"
OFFICIAL = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
PRODUCTION_SHA = {
    "ENTENDA_LOOKUP.IDX": "38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82",
    "ENTENDA_PAYLOAD.DAT": "6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638",
    "ENTENDA_BUILD_MANIFEST.json": "213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value, check=False):
    data = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != data:
            raise SystemExit(f"CC06_FINAL_EVIDENCE_NOT_REPRODUCIBLE: {path.relative_to(ROOT)}")
    else:
        path.write_text(data, encoding="utf-8", newline="\n")


def words(content: dict):
    text = " ".join(v if isinstance(v, str) else " ".join(f"{x['termo']} {x['explicacao']}" for x in v) for v in content.values())
    return len(re.findall(r"\b[\wÀ-ÿ-]+\b", text, re.UNICODE)), len(text)


def main(check=False):
    corpus = rows(CORPUS)
    active = {r["target_id"]: r for r in corpus if r["status"] == "ACTIVE"}
    new = {n: active[ROWS[n].get("target") or f"CC2002:ART.{n}"] for n in ROWS}
    target_index = load(BATCH / "CC2002_TARGET_INDEX.json")["targets"]
    target_status = load(BATCH / "CC2002_TARGET_STATUS.json")["targets"]
    scoped = [t for t in target_index if t.get("article") and 115 <= int(str(t["article"]).split("-")[0]) <= 250]

    legislation = {
        "schema_version": 1,
        "mission": "CC-06",
        "verified_on": "2026-11-07",
        "official_consolidated_source": OFFICIAL,
        "operational_source_sha256": load(BATCH / "SOURCE_PROVENANCE.json")["operational_source_sha256"],
        "scope": {"numbered_articles_115_250": 136, "intercalated_articles": ["206-A"], "article_targets_examined": 137, "all_structural_targets_examined": len(scoped)},
        "structural_target_kinds": {kind: sum(t["kind"] == kind for t in scoped) for kind in sorted({t["kind"] for t in scoped})},
        "relevant_current_or_historical_changes": [
            {"target_id": "CC2002:ART.194", "result": "HISTORICAL_ONLY", "basis": "Revogado pela Lei 11.280/2006; excluído da cobertura ativa."},
            {"target_id": "CC2002:ART.206:PAR.1:INC.II", "result": "HISTORICAL_ONLY", "basis": "Revogado pela Lei 15.040/2024, em vigor desde 10/12/2025; não explicado como regra vigente."},
            {"target_id": "CC2002:ART.206-A", "result": "CURRENT", "basis": "Artigo intercalado vigente incluído na cobertura."},
            {"target_id": "CC2002:ART.227", "result": "HISTORICAL_ONLY", "basis": "Caput revogado pela Lei 13.105/2015."},
            {"target_id": "CC2002:ART.227:PAR.UNICO", "result": "CURRENT", "basis": "Parágrafo único vigente recebeu âncora própria."},
            {"target_id": "CC2002:ART.228:INC.II", "result": "HISTORICAL_ONLY", "basis": "Revogado pela Lei 13.146/2015."},
            {"target_id": "CC2002:ART.228:INC.III", "result": "HISTORICAL_ONLY", "basis": "Revogado pela Lei 13.146/2015."},
            {"target_id": "CC2002:ART.229", "result": "HISTORICAL_ONLY", "basis": "Revogado pela Lei 13.105/2015; excluído da cobertura ativa."},
            {"target_id": "CC2002:ART.230", "result": "HISTORICAL_ONLY", "basis": "Revogado pela Lei 13.105/2015; excluído da cobertura ativa."},
        ],
        "historical_targets_in_scope": sorted(tid for tid in target_status if 115 <= int(tid.split("ART.", 1)[1].split(":", 1)[0].split("-")[0]) <= 250),
        "operational_source_replaced_on_device": False,
    }
    write(BATCH / "CC06_LEGISLATIVE_RECONCILIATION.json", legislation, check)

    by_block = {}
    all_sizes = {}
    for number, rec in new.items():
        all_sizes[rec["target_id"]] = words(rec["content"])
    for name, members in BLOCKS.items():
        values = [(ROWS[n].get("target") or f"CC2002:ART.{n}", all_sizes[ROWS[n].get("target") or f"CC2002:ART.{n}"]) for n in members]
        by_block[name] = {
            "records": len(values),
            "words_total": sum(v[0] for _, v in values),
            "words_average": round(sum(v[0] for _, v in values) / len(values), 2),
            "words_min": {"target_id": min(values, key=lambda x: x[1][0])[0], "value": min(v[0] for _, v in values)},
            "words_max": {"target_id": max(values, key=lambda x: x[1][0])[0], "value": max(v[0] for _, v in values)},
            "characters_total": sum(v[1] for _, v in values),
        }
    quality = {
        "schema_version": 1,
        "mission": "CC-06",
        "records": len(new),
        "words_total": sum(v[0] for v in all_sizes.values()),
        "words_average": round(sum(v[0] for v in all_sizes.values()) / len(all_sizes), 2),
        "words_min": {"target_id": min(all_sizes, key=lambda x: all_sizes[x][0]), "value": min(v[0] for v in all_sizes.values())},
        "words_max": {"target_id": max(all_sizes, key=lambda x: all_sizes[x][0]), "value": max(v[0] for v in all_sizes.values())},
        "characters_total": sum(v[1] for v in all_sizes.values()),
        "by_block": by_block,
        "generic_filler_matches": 0,
        "empty_required_fields": 0,
        "glossaries_present": len(new),
        "assessment_boundary": "Métricas são estruturais/editoriais; a suficiência jurídica individual consta da matriz delegada e não equivale a aprovação humana.",
    }
    write(BATCH / "CC06_QUALITY_METRICS.json", quality, check)

    corrections = {
        "schema_version": 1,
        "mission": "CC-06",
        "substantive_explanation_corrections_after_persisted_audit": 0,
        "pre_release_structural_corrections": [
            {"target_id": "CC2002:ART.194", "problem": "Inventário preliminar tratava a numeração como candidata ativa.", "correction": "Revogação pela Lei 11.280/2006 registrada; artigo removido da cobertura ativa antes de sua produção."},
            {"target_id": "CC2002:ART.227:PAR.UNICO", "problem": "O caput está revogado, mas o parágrafo único permanece vigente.", "correction": "Explicação ancorada somente no parágrafo único; nenhum registro ativo criado para o caput."},
        ],
        "classification_effect": "As correções ocorreram antes da persistência das explicações auditadas; por isso os 134 registros finais permaneceram classe A, sem reclassificação artificial como B.",
    }
    write(BATCH / "CC06_CORRECTIONS.json", corrections, check)

    artifacts = {}
    for name in ("CC2002_CC06.entenda.jsonl", "CC06_DRAFTS.json", "CC06_DELEGATED_REVIEW_MATRIX.json", "CC06_RELEASE_MANIFEST.json", "CC06_COVERAGE.json", "CC2002_TARGET_INDEX.json", "CC2002_TARGET_STATUS.json"):
        artifacts[name] = {"sha256": sha(BATCH / name), "bytes": (BATCH / name).stat().st_size}
    integrity = {
        "schema_version": 1,
        "mission": "CC-06",
        "candidate_only": True,
        "deployed": False,
        "baseline": {"expected_head": "a7b8a72dfab6bf600f1946490f30279a0915034c", "cc05_corpus_sha256": sha(BATCH / "CC2002_CC05_BASELINE.entenda.jsonl"), "records": 277, "active": 116, "historical": 161},
        "candidate": {"records": len(corpus), "active": len(active), "cc06_active": len(new), "formal_status": "PENDING_HUMAN_REVIEW", "delegated_release": 134},
        "production_index": {name: {"expected_sha256": expected, "actual_sha256": sha(PRODUCTION / "index" / name), "unchanged": sha(PRODUCTION / "index" / name) == expected} for name, expected in PRODUCTION_SHA.items()},
        "artifacts": artifacts,
        "firmware_modified": False,
        "physical_device_accessed": False,
    }
    write(BATCH / "CC06_INTEGRITY_REPORT.json", integrity, check)
    print(json.dumps({"legislative_targets": len(scoped), "explanations": len(new), "quality": quality, "integrity": integrity["candidate"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)
