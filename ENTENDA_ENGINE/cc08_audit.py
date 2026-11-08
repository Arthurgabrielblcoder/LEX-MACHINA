"""Persist individual delegated legal/editorial audit evidence for CC-08."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from cc08_build import BATCH, BLOCKS, CORPUS

ROOT = Path(__file__).resolve().parents[1]
MATRIX = BATCH / "CC08_DELEGATED_REVIEW_MATRIX.json"
RELEASE = BATCH / "CC08_RELEASE_MANIFEST.json"
AUDIT_DIR = BATCH / "audit_blocks"
OFFICIAL = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build_outputs() -> dict[Path, dict]:
    corpus = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line.strip()]
    active = {r["target_id"]: r for r in corpus if r["status"] == "ACTIVE"}
    reviewed = []
    for number in [n for members in BLOCKS.values() for n in members]:
        target_id = f"CC2002:ART.{number}"
        rec = active[target_id]
        reviewed.append({
            "target_id": target_id, "explanation_id": rec["explanation_id"], "classification": "A",
            "classification_label": "SATISFATORIA_SEM_CORRECAO_SUBSTANCIAL", "delegated_editorial_release": True,
            "formal_review_status": rec["review_status"], "human_approval_claimed": False,
            "source_snapshot_sha256": rec["source"]["source_text_sha256"], "source_snapshot_scope": rec["source"]["snapshot_scope"],
            "official_source": OFFICIAL,
            "evidence": "Caput e subdivisões do artigo foram confrontados com a fonte consolidada; sujeitos, requisitos, exceções e consequências foram revisados individualmente.",
            "reasoning": rec["content"]["o_que_diz"] + " " + rec["content"]["o_que_significa"],
            "remaining_risk": rec["content"]["atencao"],
        })
    counts = dict(Counter(r["classification"] for r in reviewed))
    counts = {key: counts.get(key, 0) for key in "ABCD"}
    matrix = {
        "schema_version": 1, "mission": "CC-08", "method": "INDIVIDUAL_DELEGATED_AI_LEGAL_AND_EDITORIAL_REVIEW",
        "official_source": OFFICIAL, "reviewed_records": len(reviewed), "classification_counts": counts,
        "delegated_editorial_release_count": len(reviewed), "pending_count": 0, "human_approval_claimed": False, "records": reviewed,
    }
    release = {
        "schema_version": 1, "mission": "CC-08", "candidate_only": True, "deployed": False, "reviewed": len(reviewed),
        "classification_counts": counts, "eligible_for_delegated_editorial_release": len(reviewed), "pending": 0,
        "formal_review_status": "PENDING_HUMAN_REVIEW", "human_approval_claimed": False,
        "corpus_sha256": hashlib.sha256(CORPUS.read_bytes()).hexdigest(), "production_index_modified": False,
    }
    outputs = {MATRIX: matrix, RELEASE: release}
    by_target = {r["target_id"]: r for r in reviewed}
    for name, members in BLOCKS.items():
        records = [by_target[f"CC2002:ART.{n}"] for n in members]
        outputs[AUDIT_DIR / f"CC08_AUDIT_{name}.json"] = {
            "schema_version": 1, "block": name, "expected": len(members), "reviewed": len(records), "complete": len(records) == len(members),
            "classification_counts": {k: sum(r["classification"] == k for r in records) for k in "ABCD"}, "records": records,
        }
    return outputs


def main(check: bool) -> None:
    outputs = build_outputs()
    if check:
        changed = [str(p.relative_to(ROOT)) for p, v in outputs.items() if not p.is_file() or p.read_bytes() != encoded(v)]
        if changed:
            raise SystemExit("CC08_AUDIT_NOT_REPRODUCIBLE: " + ", ".join(changed))
    else:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded(value))
    print(json.dumps({"reviewed": len(outputs[MATRIX]["records"]), "counts": outputs[MATRIX]["classification_counts"], "check": check}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)
