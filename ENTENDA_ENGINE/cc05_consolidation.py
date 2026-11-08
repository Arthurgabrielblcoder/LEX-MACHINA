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


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def active(path: Path) -> dict[str, dict]:
    return {r["target_id"]: r for r in load_jsonl(path) if r["status"] == "ACTIVE"}


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def content_hash(content: dict) -> str:
    raw = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


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


def main(check: bool) -> None:
    value = build_registry()
    raw = encoded(value)
    if check:
        if not REGISTRY.is_file() or REGISTRY.read_bytes() != raw:
            raise SystemExit("CC05_HUMAN_APPROVAL_REGISTRY_NOT_REPRODUCIBLE")
    else:
        REGISTRY.write_bytes(raw)
    print(json.dumps({
        "human_approved_texts_integrated": value["record_count"],
        "formal_status_promoted": value["formal_status_promoted"],
        "check": check,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    main(args.check)
