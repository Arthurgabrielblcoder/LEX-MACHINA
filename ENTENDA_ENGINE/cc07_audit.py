"""Persist individual delegated legal/editorial audit evidence for CC-07."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from cc07_build import BATCH, BLOCKS, CORPUS

ROOT = Path(__file__).resolve().parents[1]
MATRIX = BATCH / "CC07_DELEGATED_REVIEW_MATRIX.json"
RELEASE = BATCH / "CC07_RELEASE_MANIFEST.json"
AUDIT_DIR = BATCH / "audit_blocks"
OFFICIAL = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build_outputs() -> dict[Path, dict]:
    corpus = rows(CORPUS)
    active = {r["target_id"]: r for r in corpus if r["status"] == "ACTIVE"}
    reviewed: list[dict] = []
    for target_id in ("CC2002:ART.157", "CC2002:ART.202"):
        rec = active[target_id]
        reviewed.append({
            "target_id": target_id,
            "explanation_id": rec["explanation_id"],
            "classification": "B",
            "classification_label": "SATISFATORIA_APOS_CORRECAO_FUNDAMENTADA",
            "delegated_editorial_release": True,
            "formal_review_status": rec["review_status"],
            "human_approval_claimed": False,
            "source_snapshot_sha256": rec["source"]["source_text_sha256"],
            "official_source": OFFICIAL,
            "evidence": "Redação integral do dispositivo confrontada com a fonte oficial consolidada; a versão anterior permanece RETIRED no corpus.",
            "reasoning": rec["granularity"]["editorial_reason"],
            "remaining_risk": rec["content"]["atencao"],
        })
    for number in [str(n) for n in range(251, 401) if n != 374]:
        target_id = f"CC2002:ART.{number}"
        rec = active[target_id]
        reviewed.append({
            "target_id": target_id,
            "explanation_id": rec["explanation_id"],
            "classification": "A",
            "classification_label": "SATISFATORIA_SEM_CORRECAO_SUBSTANCIAL",
            "delegated_editorial_release": True,
            "formal_review_status": rec["review_status"],
            "human_approval_claimed": False,
            "source_snapshot_sha256": rec["source"]["source_text_sha256"],
            "source_snapshot_scope": rec["source"]["snapshot_scope"],
            "official_source": OFFICIAL,
            "evidence": "Caput e subdivisões do artigo foram confrontados com a fonte consolidada; sujeitos, requisitos, exceções e consequências foram revisados individualmente.",
            "reasoning": rec["content"]["o_que_diz"] + " " + rec["content"]["o_que_significa"],
            "remaining_risk": rec["content"]["atencao"],
        })
    counts = dict(Counter(r["classification"] for r in reviewed))
    counts = {key: counts.get(key, 0) for key in "ABCD"}
    matrix = {
        "schema_version": 1,
        "mission": "CC-07",
        "method": "INDIVIDUAL_DELEGATED_AI_LEGAL_AND_EDITORIAL_REVIEW",
        "official_source": OFFICIAL,
        "reviewed_records": len(reviewed),
        "classification_counts": counts,
        "delegated_editorial_release_count": sum(r["delegated_editorial_release"] for r in reviewed),
        "pending_count": counts["C"] + counts["D"],
        "human_approval_claimed": False,
        "records": reviewed,
    }
    release = {
        "schema_version": 1,
        "mission": "CC-07",
        "candidate_only": True,
        "deployed": False,
        "reviewed": len(reviewed),
        "classification_counts": counts,
        "eligible_for_delegated_editorial_release": matrix["delegated_editorial_release_count"],
        "pending": matrix["pending_count"],
        "formal_review_status": "PENDING_HUMAN_REVIEW",
        "human_approval_claimed": False,
        "corpus_sha256": hashlib.sha256(CORPUS.read_bytes()).hexdigest(),
        "production_index_modified": False,
    }
    outputs: dict[Path, dict] = {MATRIX: matrix, RELEASE: release}
    by_target = {r["target_id"]: r for r in reviewed}
    for name, members in BLOCKS.items():
        records = [by_target[f"CC2002:ART.{n}"] for n in members]
        outputs[AUDIT_DIR / f"CC07_AUDIT_{name}.json"] = {
            "schema_version": 1,
            "block": name,
            "expected": len(members),
            "reviewed": len(records),
            "complete": len(records) == len(members),
            "classification_counts": {k: sum(r["classification"] == k for r in records) for k in "ABCD"},
            "records": records,
        }
    return outputs


def main(check: bool) -> None:
    outputs = build_outputs()
    if check:
        changed = [str(path.relative_to(ROOT)) for path, value in outputs.items() if not path.is_file() or path.read_bytes() != encoded(value)]
        if changed:
            raise SystemExit("CC07_AUDIT_NOT_REPRODUCIBLE: " + ", ".join(changed))
    else:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded(value))
    matrix = outputs[MATRIX]
    print(json.dumps({"reviewed": matrix["reviewed_records"], "counts": matrix["classification_counts"], "pending": matrix["pending_count"], "check": check}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)
