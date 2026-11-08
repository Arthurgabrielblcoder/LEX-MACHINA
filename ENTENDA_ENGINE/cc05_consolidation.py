"""Validate and consolidate the CC-05 candidate without touching production indexes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from cc02_editorial import CC05_HUMAN_APPROVED_TARGETS, CC05_OVERRIDES

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
CORPUS = BATCH / "CC2002_CC02.entenda.jsonl"
BASELINE = BATCH / "CC2002_CC04_BASELINE.entenda.jsonl"
REGISTRY = BATCH / "CC05_HUMAN_APPROVAL_REGISTRY.json"
CC04_MATRIX = BATCH / "CC04_DELEGATED_REVIEW_MATRIX.json"
LEGAL_RESOLUTION = BATCH / "CC05_LEGAL_RESOLUTION_14_21.json"
MATRIX = BATCH / "CC05_CONSOLIDATED_MATRIX.json"
RELEASE = BATCH / "CC05_RELEASE_MANIFEST.json"
INTEGRITY = BATCH / "CC05_INTEGRITY_REPORT.json"
LEGAL_RESOLVED = {"14", "21"}
PRODUCTION_INDEX_SHA256 = {
    "ENTENDA_LOOKUP.IDX": "38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82",
    "ENTENDA_PAYLOAD.DAT": "6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638",
    "ENTENDA_BUILD_MANIFEST.json": "213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760",
}
CC_OFFICIAL = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
APPROVAL_VALIDATION_SOURCES = {
    "2": [{"title": "Código Civil consolidado", "url": CC_OFFICIAL}],
    "4": [
        {"title": "Código Civil consolidado", "url": CC_OFFICIAL},
        {"title": "Lei Brasileira de Inclusão", "url": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm"},
    ],
    "15": [
        {"title": "Código Civil consolidado", "url": CC_OFFICIAL},
        {"title": "STF — Tema 952", "url": "https://portal.stf.jus.br/jurisprudenciaRepercussao/verAndamentoProcesso.asp?classeProcesso=RE&incidente=5006128&numeroProcesso=979742&numeroTema=952"},
        {"title": "STF — Tema 1069", "url": "https://portal.stf.jus.br/jurisprudenciaRepercussao/verAndamentoProcesso.asp?classeProcesso=RE&incidente=5703626&numeroProcesso=1212272&numeroTema=1069"},
    ],
    "20": [
        {"title": "Código Civil consolidado", "url": CC_OFFICIAL},
        {"title": "STF — ADI 4.815", "url": "https://portal.stf.jus.br/peticaoInicial/verPeticaoInicial.asp?base=ADI&numProcesso=4815"},
        {"title": "STJ — Súmula 403", "url": "https://scon.stj.jus.br/SCON/sumstj/doc.jsp?b=SUMU&i=1&l=10&livre=%22403%22+INPATH%28NUM%29&operador=AND&ordenacao=-%40NUM&p=false"},
    ],
    "50": [{"title": "Código Civil consolidado", "url": CC_OFFICIAL}],
    "113": [{"title": "Código Civil consolidado", "url": CC_OFFICIAL}],
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def active(path: Path) -> dict[str, dict]:
    return {r["target_id"]: r for r in load_jsonl(path) if r["status"] == "ACTIVE"}


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def content_hash(content: dict) -> str:
    raw = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def article(target_id: str) -> str:
    return target_id.split("ART.", 1)[1].split(":", 1)[0]


def build_registry() -> dict:
    current = active(CORPUS)
    baseline = active(BASELINE)
    records = []
    for article in sorted(CC05_HUMAN_APPROVED_TARGETS, key=int):
        target_id = f"CC2002:ART.{article}"
        record = current[target_id]
        prior = baseline[target_id]
        if record["content"] != CC05_OVERRIDES[article]:
            raise SystemExit("CC05_APPROVED_TEXT_NOT_EXACT: " + target_id)
        if record["review_status"] != "PENDING_HUMAN_REVIEW":
            raise SystemExit("CC05_UNVERIFIED_FORMAL_PROMOTION: " + target_id)
        if record["editorial_version"] != prior["editorial_version"] + 1:
            raise SystemExit("CC05_APPROVED_VERSION_NOT_INCREMENTED: " + target_id)
        approval = record.get("external_human_approval", {})
        if approval.get("electronic_signature_verified") is not False or approval.get("exact_text_integrity_verified") is not True:
            raise SystemExit("CC05_APPROVAL_PROVENANCE_INVALID: " + target_id)
        records.append({
            "target_id": target_id,
            "prior_explanation_id": prior["explanation_id"],
            "approved_explanation_id": record["explanation_id"],
            "approved_text": record["content"],
            "origin_declared": approval["origin"],
            "approval_date": approval["approval_date"],
            "content_sha256": content_hash(record["content"]),
            "editorial_version": record["editorial_version"],
            "formal_review_status": record["review_status"],
            "electronic_signature_verified": approval["electronic_signature_verified"],
            "exact_text_integrity_verified": approval["exact_text_integrity_verified"],
            "legal_validation_sources": APPROVAL_VALIDATION_SOURCES[article],
            "formal_promotion_block": "Aprovação externa expressa, mas sem assinatura eletrônica verificável; preservado PENDING_HUMAN_REVIEW.",
        })
    claimed = {
        r["target_id"] for r in current.values()
        if r.get("authoring", {}).get("human_approval_claimed") is True
    }
    expected = {f"CC2002:ART.{article}" for article in CC05_HUMAN_APPROVED_TARGETS}
    if claimed != expected:
        raise SystemExit("CC05_HUMAN_APPROVAL_SCOPE_MISMATCH")
    return {
        "schema_version": 1,
        "mission": "CC-05",
        "origin": "Transcrição de aprovação externa fornecida pelo proprietário no prompt da missão",
        "approval_date": "2026-11-07",
        "electronic_signature_verified": False,
        "formal_status_promoted": False,
        "record_count": len(records),
        "records": records,
    }


def build_consolidation(registry: dict) -> dict[Path, dict]:
    current_rows = load_jsonl(CORPUS)
    baseline_rows = load_jsonl(BASELINE)
    current = {r["target_id"]: r for r in current_rows if r["status"] == "ACTIVE"}
    baseline = {r["target_id"]: r for r in baseline_rows if r["status"] == "ACTIVE"}
    if len(current) != 116 or len(set(current)) != 116 or "CC2002:ART.69-A" in current:
        raise SystemExit("CC05_ACTIVE_COVERAGE_INVALID")
    if {r["review_status"] for r in current.values()} != {"PENDING_HUMAN_REVIEW"}:
        raise SystemExit("CC05_FORMAL_STATUS_INVALID")

    changed_targets = {f"CC2002:ART.{n}" for n in CC05_HUMAN_APPROVED_TARGETS | LEGAL_RESOLVED}
    preserved = [tid for tid in baseline if tid not in changed_targets]
    different = [tid for tid in preserved if current[tid] != baseline[tid]]
    if len(preserved) != 108 or different:
        raise SystemExit("CC05_DELEGATED_108_NOT_PRESERVED: " + ", ".join(different))

    current_by_id = {r["explanation_id"]: r for r in current_rows}
    lost_history = [r["explanation_id"] for r in baseline_rows if r["explanation_id"] not in current_by_id]
    altered_history = [
        r["explanation_id"] for r in baseline_rows
        if r["explanation_id"] in current_by_id
        and (r["content"] != current_by_id[r["explanation_id"]]["content"] or r["source"] != current_by_id[r["explanation_id"]]["source"])
    ]
    if lost_history or altered_history:
        raise SystemExit("CC05_HISTORY_NOT_PRESERVED")

    index_actual = {name: file_hash(BATCH / "index" / name) for name in PRODUCTION_INDEX_SHA256}
    if index_actual != PRODUCTION_INDEX_SHA256:
        raise SystemExit("CC05_PRODUCTION_INDEX_MODIFIED")

    cc04 = json.loads(CC04_MATRIX.read_text(encoding="utf-8"))
    cc04_by_target = {r["target_id"]: r for r in cc04["records"]}
    legal = json.loads(LEGAL_RESOLUTION.read_text(encoding="utf-8"))
    legal_by_target = {r["target_id"]: r for r in legal["records"]}
    registry_by_target = {r["target_id"]: r for r in registry["records"]}
    rows = []
    for record in (r for r in current_rows if r["status"] == "ACTIVE"):
        tid = record["target_id"]
        number = article(tid)
        if number in CC05_HUMAN_APPROVED_TARGETS:
            route = "OWNER_APPROVED_EXTERNAL_TEXT_INTEGRATED"
            delegated_classification = None
            evidence = {
                "registry": str(REGISTRY.relative_to(ROOT)).replace("\\", "/"),
                "content_sha256": registry_by_target[tid]["content_sha256"],
            }
        elif number in LEGAL_RESOLVED:
            route = "CC05_DELEGATED_LEGAL_RESOLUTION"
            delegated_classification = "A"
            evidence = {
                "resolution": str(LEGAL_RESOLUTION.relative_to(ROOT)).replace("\\", "/"),
                "official_sources": legal_by_target[tid]["official_sources"],
            }
        else:
            route = "CC04_DELEGATED_RELEASE_PRESERVED"
            delegated_classification = cc04_by_target[tid]["classification"]
            evidence = {
                "cc04_matrix": str(CC04_MATRIX.relative_to(ROOT)).replace("\\", "/"),
                "reasoning": cc04_by_target[tid]["reasoning"],
                "official_source": cc04_by_target[tid]["official_source"],
            }
        rows.append({
            "target_id": tid,
            "explanation_id": record["explanation_id"],
            "editorial_version": record["editorial_version"],
            "consolidation_route": route,
            "delegated_classification": delegated_classification,
            "formal_review_status": record["review_status"],
            "human_approval_claimed": record.get("authoring", {}).get("human_approval_claimed", False),
            "content_sha256": content_hash(record["content"]),
            "evidence": evidence,
        })

    matrix = {
        "schema_version": 1,
        "mission": "CC-05",
        "active_records": 116,
        "delegated_release_preserved": 108,
        "delegated_release_new": 2,
        "delegated_release_total": 110,
        "owner_approved_external_texts_integrated": 6,
        "formal_human_approval_promotions": 0,
        "legal_pending": 0,
        "formal_pending_human_review": 116,
        "records": rows,
    }
    release = {
        "schema_version": 1,
        "mission": "CC-05",
        "candidate_only": True,
        "deployed": False,
        "active_records": 116,
        "corpus_records": len(current_rows),
        "retired_records": sum(r["status"] == "RETIRED" for r in current_rows),
        "delegated_editorial_release": {"preserved_from_cc04": 108, "resolved_in_cc05": 2, "total": 110},
        "external_human_approval": {"texts_integrated": 6, "formal_status_promoted": 0, "electronic_signature_verified": False},
        "pending": {"legal": 0, "formal_human_review": 116},
        "corpus_sha256": file_hash(CORPUS),
        "matrix_sha256": hashlib.sha256(encoded(matrix)).hexdigest(),
        "production_index_modified": False,
    }
    integrity = {
        "schema_version": 1,
        "mission": "CC-05",
        "checks": {
            "active_unique_116": True,
            "arts_1_to_114_plus_48_a_49_a_covered": True,
            "art_69_a_active": False,
            "baseline_history_records_preserved": len(baseline_rows),
            "baseline_history_lost": lost_history,
            "baseline_content_or_source_altered": altered_history,
            "delegated_records_preserved_exactly": len(preserved),
            "owner_approved_texts_exact": 6,
            "legal_pending": 0,
            "production_index_sha256": index_actual,
            "production_index_modified": False,
        },
        "corpus": {"total": len(current_rows), "active": len(current), "retired": sum(r["status"] == "RETIRED" for r in current_rows)},
    }
    return {MATRIX: matrix, RELEASE: release, INTEGRITY: integrity}


def main(check: bool) -> None:
    value = build_registry()
    outputs = {REGISTRY: value, **build_consolidation(value)}
    if check:
        changed = [str(path.relative_to(ROOT)) for path, doc in outputs.items() if not path.is_file() or path.read_bytes() != encoded(doc)]
        if changed:
            raise SystemExit("CC05_CONSOLIDATION_NOT_REPRODUCIBLE: " + ", ".join(changed))
    else:
        for path, doc in outputs.items():
            path.write_bytes(encoded(doc))
    print(json.dumps({
        "human_approved_texts_integrated": value["record_count"],
        "formal_status_promoted": value["formal_status_promoted"],
        "delegated_release": 110,
        "legal_pending": 0,
        "check": check,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    main(args.check)
