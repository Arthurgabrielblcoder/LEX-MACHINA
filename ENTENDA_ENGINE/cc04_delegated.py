"""Consolidate the delegated CC-04 review without claiming human approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
PROPOSALS = BATCH / "cc04_delegated"
BASELINE = BATCH / "CC2002_CC03B_BASELINE.entenda.jsonl"
CORPUS = BATCH / "CC2002_CC02.entenda.jsonl"
OFFICIAL = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
EXCLUDED = {"2", "4", "15", "20", "50", "113"}
PRIORITY = {"2", "4", "11", "12", "13", "14", "15", "20", "21", "43", "44", "49-A", "50", "52", "57", "59", "76", "104", "105", "110", "111", "112", "114"}
EXPECTED_B = {"5", "9", "11", "29", "30", "45", "46", "48", "61", "64", "68", "69", "75", "76", "83", "96", "103", "105", "110"}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def active(path: Path) -> dict[str, dict]:
    return {r["target_id"]: r for r in load_jsonl(path) if r["status"] == "ACTIVE"}


def article(target_id: str) -> str:
    return target_id.split("ART.", 1)[1].split(":", 1)[0]


def class_letter(value: str) -> str:
    m = re.match(r"[ABCD]", value or "")
    if not m:
        raise ValueError("invalid classification: " + repr(value))
    return m.group(0)


def encoded(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main(check: bool = False) -> None:
    base, current = active(BASELINE), active(CORPUS)
    proposal_files = sorted(PROPOSALS.glob("block_*_proposal.json"))
    if len(proposal_files) != 3:
        raise SystemExit("CC04_PROPOSAL_FILE_COUNT")
    proposed = []
    for path in proposal_files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        proposed.extend(doc["records"])
    by_tid = {r["target_id"]: r for r in proposed}
    expected = {tid for tid in current if article(tid) not in EXCLUDED}
    if len(proposed) != 110 or len(by_tid) != 110 or set(by_tid) != expected:
        raise SystemExit("CC04_REVIEW_COVERAGE_MISMATCH")

    records, corrections = [], []
    for tid in sorted(expected, key=lambda t: (int(article(t).split("-")[0]), "-" not in article(t), article(t))):
        source = by_tid[tid]
        cls = class_letter(source["classification"])
        number = article(tid)
        changed = current[tid]["content"] != base[tid]["content"]
        if (cls == "B") != changed:
            raise SystemExit(f"CC04_CLASS_VERSION_MISMATCH: {tid} {cls} changed={changed}")
        if cls == "B":
            section_changes = {
                k: {"before": base[tid]["content"][k], "after": current[tid]["content"][k]}
                for k in current[tid]["content"] if current[tid]["content"][k] != base[tid]["content"][k]
            }
            corrections.append({
                "target_id": tid,
                "before_explanation_id": base[tid]["explanation_id"],
                "after_explanation_id": current[tid]["explanation_id"],
                "evidence": source.get("evidence"),
                "reasoning": source.get("reasoning"),
                "official_source": OFFICIAL,
                "changed_sections": section_changes,
            })
        records.append({
            "target_id": tid,
            "explanation_id": current[tid]["explanation_id"],
            "classification": cls,
            "classification_label": {
                "A": "REVISAO_DELEGADA_SATISFATORIA",
                "B": "REVISAO_DELEGADA_SATISFATORIA_APOS_CORRECAO",
                "C": "REVISAO_PENDENTE",
                "D": "BLOQUEADO",
            }[cls],
            "delegated_editorial_release": cls in {"A", "B"},
            "formal_review_status": current[tid]["review_status"],
            "human_approval_claimed": False,
            "evidence": source.get("evidence"),
            "reasoning": source.get("reasoning"),
            "remaining_risk": source.get("remaining_risk"),
            "official_source": OFFICIAL,
            "source_snapshot_sha256": current[tid]["source"]["source_text_sha256"],
            "subdivision_evidence_scope": current[tid]["source"]["snapshot_scope"],
        })

    counts = {letter: sum(r["classification"] == letter for r in records) for letter in "ABCD"}
    if counts != {"A": 89, "B": 19, "C": 2, "D": 0} or {article(r["target_id"]) for r in records if r["classification"] == "B"} != EXPECTED_B:
        raise SystemExit("CC04_UNEXPECTED_CLASSIFICATION_COUNTS")
    excluded = []
    for number in sorted(EXCLUDED, key=int):
        tid = f"CC2002:ART.{number}"
        if current[tid]["explanation_id"] != base[tid]["explanation_id"] or current[tid]["content"] != base[tid]["content"] or current[tid]["source"] != base[tid]["source"]:
            raise SystemExit("CC04_EXCLUDED_CHANGED: " + tid)
        excluded.append({
            "target_id": tid,
            "explanation_id": current[tid]["explanation_id"],
            "content_sha256": hashlib.sha256(json.dumps(current[tid]["content"], ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
            "treatment": "EXCLUIDO: aprovação humana externa sem texto final incorporado; não modificado nem classificado nesta missão",
        })

    matrix = {
        "schema_version": 1,
        "mission": "CC-04",
        "method": "DELEGATED_AI_LEGAL_REVIEW",
        "official_source": OFFICIAL,
        "accessed_on": "2026-11-07",
        "reviewed_records": 110,
        "classification_counts": counts,
        "delegated_editorial_release_count": counts["A"] + counts["B"],
        "pending_count": counts["C"] + counts["D"],
        "formal_status_changed": False,
        "human_approval_claimed": False,
        "records": records,
        "excluded_external_human_review": excluded,
    }
    priority = []
    matrix_by_tid = {r["target_id"]: r for r in records}
    for number in sorted(PRIORITY, key=lambda x: (int(x.split("-")[0]), x)):
        tid = f"CC2002:ART.{number}"
        priority.append({
            "target_id": tid,
            "result": "EXCLUIDO_APROVACAO_HUMANA_EXTERNA_NAO_INCORPORADA" if number in EXCLUDED else matrix_by_tid[tid]["classification_label"],
            "evidence": None if number in EXCLUDED else matrix_by_tid[tid]["evidence"],
            "remaining_risk": "Texto humano final ausente do repositório" if number in EXCLUDED else matrix_by_tid[tid]["remaining_risk"],
        })

    checkpoints = {}
    for start, end in ((1, 25), (26, 50), (51, 75), (76, 100), (101, 114)):
        block = [r for r in records if start <= int(article(r["target_id"]).split("-")[0]) <= end]
        value = {
            "schema_version": 1,
            "range": [start, end],
            "reviewed_count": len(block),
            "counts": {letter: sum(r["classification"] == letter for r in block) for letter in "ABCD"},
            "records": block,
            "records_sha256": hashlib.sha256(json.dumps(block, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        }
        checkpoints[BATCH / "checkpoints_cc04" / f"CC04_{start:03d}_{end:03d}.json"] = value

    quality = json.loads((BATCH / "CC03B_REPETITION_METRICS.json").read_text(encoding="utf-8"))["cc03b_after"]
    outputs = {
        BATCH / "CC04_DELEGATED_REVIEW_MATRIX.json": matrix,
        BATCH / "CC04_CORRECTIONS.json": {"schema_version": 1, "count": len(corrections), "corrections": corrections},
        BATCH / "CC04_PRIORITY_SECOND_REVIEW.json": {"schema_version": 1, "count": len(priority), "records": priority},
        BATCH / "CC04_RELEASE_MANIFEST.json": {
            "schema_version": 1,
            "method": "DELEGATED_AI_LEGAL_REVIEW",
            "release_is_human_approval": False,
            "eligible_for_delegated_editorial_release": counts["A"] + counts["B"],
            "pending": counts["C"] + counts["D"],
            "excluded_external_human_review": len(EXCLUDED),
            "formal_review_status": "PENDING_HUMAN_REVIEW",
            "corpus_sha256": hashlib.sha256(CORPUS.read_bytes()).hexdigest(),
            "quality_metrics": quality,
        },
        **checkpoints,
    }
    if check:
        changed = [str(path.relative_to(ROOT)) for path, value in outputs.items() if not path.is_file() or path.read_bytes() != encoded(value)]
        if changed:
            raise SystemExit("CC04_NOT_REPRODUCIBLE: " + ", ".join(changed))
    else:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded(value))
    print(json.dumps({"reviewed": 110, "counts": counts, "released": counts["A"] + counts["B"], "pending": counts["C"] + counts["D"], "corrections": len(corrections), "check": check}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    main(args.check)
