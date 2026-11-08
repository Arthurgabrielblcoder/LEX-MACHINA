"""Persist the individual delegated legal/editorial audit for CC-06."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from cc06_editorial import BLOCKS, ROWS

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_250"
CORPUS = BATCH / "CC2002_CC06.entenda.jsonl"
MATRIX = BATCH / "CC06_DELEGATED_REVIEW_MATRIX.json"
RELEASE = BATCH / "CC06_RELEASE_MANIFEST.json"
AUDIT_DIR = BATCH / "audit_blocks"
OFFICIAL = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"

# Populated only when a persisted earlier version was corrected after audit.
CORRECTIONS: dict[str, dict] = {}
PENDING: dict[str, str] = {}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def article(target_id: str) -> str:
    return target_id.split("ART.", 1)[1].split(":", 1)[0]


def build_outputs() -> dict[Path, dict]:
    rows = load_jsonl(CORPUS)
    active = {r["target_id"]: r for r in rows if r["status"] == "ACTIVE"}
    reviewed = []
    for number in sorted(ROWS, key=lambda x: (int(x.split("-")[0]), x)):
        target = ROWS[number].get("target") or f"CC2002:ART.{number}"
        rec = active[target]
        if number in PENDING:
            classification = "C"
        elif number in CORRECTIONS:
            classification = "B"
        else:
            classification = "A"
        reviewed.append({
            "target_id": target,
            "explanation_id": rec["explanation_id"],
            "classification": classification,
            "classification_label": {
                "A": "SATISFATORIA_SEM_CORRECAO_SUBSTANCIAL",
                "B": "SATISFATORIA_APOS_CORRECAO_FUNDAMENTADA",
                "C": "PENDENTE_CONTROVERSIA_OU_EVIDENCIA_INSUFICIENTE",
            }[classification],
            "delegated_editorial_release": classification in {"A", "B"},
            "formal_review_status": rec["review_status"],
            "human_approval_claimed": False,
            "source_snapshot_sha256": rec["source"]["source_text_sha256"],
            "source_snapshot_scope": rec["source"]["snapshot_scope"],
            "official_source": OFFICIAL,
            "evidence": "Texto e subdivisões do dispositivo confrontados com a fonte consolidada; requisitos, exceções e consequência foram verificados individualmente.",
            "reasoning": rec["content"]["o_que_diz"] + " " + rec["content"]["atencao"],
            "remaining_risk": PENDING.get(number, rec["content"]["atencao"]),
            **({"correction": CORRECTIONS[number]} if number in CORRECTIONS else {}),
        })
    counts = dict(sorted(Counter(r["classification"] for r in reviewed).items()))
    for key in "ABCD":
        counts.setdefault(key, 0)
    counts = {key: counts[key] for key in "ABCD"}
    complete_blocks = [name for name, members in BLOCKS.items() if set(members) <= set(ROWS)]
    matrix = {
        "schema_version": 1,
        "mission": "CC-06",
        "method": "INDIVIDUAL_DELEGATED_AI_LEGAL_AND_EDITORIAL_REVIEW",
        "official_source": OFFICIAL,
        "reviewed_records": len(reviewed),
        "classification_counts": counts,
        "delegated_editorial_release_count": sum(r["delegated_editorial_release"] for r in reviewed),
        "pending_count": counts["C"] + counts["D"],
        "human_approval_claimed": False,
        "completed_blocks": complete_blocks,
        "records": reviewed,
    }
    release = {
        "schema_version": 1,
        "mission": "CC-06",
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
    outputs = {MATRIX: matrix, RELEASE: release}
    by_number = {article(r["target_id"]): r for r in reviewed}
    for name, members in BLOCKS.items():
        present = [by_number[n] for n in members if n in by_number]
        if present:
            outputs[AUDIT_DIR / f"CC06_AUDIT_{name}.json"] = {
                "schema_version": 1,
                "block": name,
                "expected": len(members),
                "reviewed": len(present),
                "complete": set(members) <= set(ROWS),
                "classification_counts": {k: sum(r["classification"] == k for r in present) for k in "ABCD"},
                "records": present,
            }
    return outputs


def main(check: bool) -> None:
    outputs = build_outputs()
    if check:
        changed = [str(path.relative_to(ROOT)) for path, value in outputs.items() if not path.is_file() or path.read_bytes() != encoded(value)]
        if changed:
            raise SystemExit("CC06_AUDIT_NOT_REPRODUCIBLE: " + ", ".join(changed))
    else:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded(value))
    matrix = outputs[MATRIX]
    print(json.dumps({
        "reviewed": matrix["reviewed_records"],
        "counts": matrix["classification_counts"],
        "released": matrix["delegated_editorial_release_count"],
        "pending": matrix["pending_count"],
        "check": check,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    main(args.check)
