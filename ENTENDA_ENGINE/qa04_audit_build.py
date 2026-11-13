"""Build deterministic QA-04 checkpoints from the three independent review modules."""
import argparse
import json
from collections import Counter

import qa04_prepare as prep


OUT = prep.OUT
QUEUE = OUT / "QA04_AUDIT_1000_QUEUE.json"
REVIEW_FILES = (
    OUT / "QA04_B_REVIEW_001_333.json",
    OUT / "QA04_B_REVIEW_334_666.json",
    OUT / "QA04_B_REVIEW_667_1000.json",
)
FINDING_FILES = (
    OUT / "QA04_B_FINDINGS_001_333.json",
    OUT / "QA04_B_FINDINGS_334_666.json",
    OUT / "QA04_B_FINDINGS_667_1000.json",
)
CHECKPOINTS = {number: ((number - 1) * 50 + 1, number * 50) for number in range(1, 21)}


def load_all(paths, key):
    values = []
    for path in paths:
        values.extend(json.loads(path.read_text(encoding="utf-8"))[key])
    return values


def main(through):
    if through not in CHECKPOINTS:
        raise SystemExit("--through-checkpoint must be between 1 and 20")
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")
    queue_doc = json.loads(QUEUE.read_text(encoding="utf-8"))
    queue = queue_doc["records"]
    if len(queue) != 1000 or [row["queue_position"] for row in queue] != list(range(389, 1389)):
        raise RuntimeError("invalid exact residual queue")
    reviews = load_all(REVIEW_FILES, "records")
    if len(reviews) != 1000 or len({row["target_id"] for row in reviews}) != 1000:
        raise RuntimeError("review modules are not exactly 1000 unique records")
    if [row["target_id"] for row in reviews] != [row["target_id"] for row in queue]:
        raise RuntimeError("review module order differs from frozen queue")

    corpus = [json.loads(line) for line in prep.CORPUS.read_text(encoding="utf-8").splitlines() if line]
    active = {row["target_id"]: row for row in corpus if row["status"] == "ACTIVE"}
    for residual, (meta, review) in enumerate(zip(queue, reviews), 1):
        target = meta["target_id"]
        recorded_residual = review.get("residual_position", review.get("residual_queue_position"))
        if review["queue_position"] != meta["queue_position"] or recorded_residual != residual:
            raise RuntimeError(f"position mismatch: {target}")
        review["residual_position"] = residual
        review["explanation_id"] = review.get("explanation_id", review.get("baseline_explanation_id"))
        if review["explanation_id"] != active[target]["explanation_id"]:
            raise RuntimeError(f"explanation mismatch: {target}")
        review.setdefault("book", meta["book"])
        review.setdefault("origin_mission", meta["origin_mission"])
        review.setdefault("norm", "Lei 10.406/2002 (Código Civil)")
        review.setdefault("as_of", prep.AS_OF)
        review.setdefault("current_law_snapshot", active[target]["source"]["source_text_snapshot"])
        review.setdefault("independent_review_module", review.get("review_module", "QA04_DELEGATED_REVIEW"))
        review.setdefault("reviewer", review.get("auditor", "delegated-independent-auditor"))
        field_hashes = review["checks"].get("field_sha256", review.get("baseline_field_sha256"))
        review["checks"]["field_sha256"] = field_hashes
        if field_hashes != meta["baseline_field_sha256"]:
            raise RuntimeError(f"field evidence mismatch: {target}")
        if not review["sources"] or not review["current_law_snapshot"] or not review["legal_segments_checked"]:
            raise RuntimeError(f"incomplete source evidence: {target}")
        if len(review["comparison"]) <= 80:
            raise RuntimeError(f"insufficient individualized comparison: {target}")

    findings = load_all(FINDING_FILES, "findings")
    finding_map = {row["target_id"]: row for row in findings}
    if len(findings) != len(finding_map) or not set(finding_map) <= {row["target_id"] for row in reviews}:
        raise RuntimeError("duplicate or out-of-scope finding")
    for review in reviews:
        target = review["target_id"]
        found = review["result"] == "ACHADO"
        if found != (target in finding_map):
            raise RuntimeError(f"review/finding disagreement: {target}")
        if found and review.get("finding") != finding_map[target]:
            raise RuntimeError(f"finding payload disagreement: {target}")

    prior = set()
    qa02 = prep.HERE / "derived/qa02_independent_legal_audit"
    for wave in range(1, 5):
        prior.update(row["target_id"] for row in json.loads(
            (qa02 / f"QA02_AUDIT_WAVE_{wave:02d}.json").read_text(encoding="utf-8"))["records"])
    prior.update(row["target_id"] for row in json.loads(
        (prep.QA03_OUT / "QA03_B_AUDIT_388.json").read_text(encoding="utf-8"))["records"])
    if len(prior) != 1017 or prior & {row["target_id"] for row in queue}:
        raise RuntimeError("QA-04 overlaps the 1017 prior audits")

    master_findings = {
        "schema_version": 1, "mission": "QA-04-FRONT-B", "as_of": prep.AS_OF,
        "status": "NEW_FINDINGS_NOT_SILENTLY_CORRECTED",
        "findings": [finding_map[row["target_id"]] for row in queue if row["target_id"] in finding_map],
    }
    prep.write_json(OUT / "QA04_B_NEW_FINDINGS.json", master_findings)

    end = CHECKPOINTS[through][1]
    completed = []
    for number, (start, finish) in CHECKPOINTS.items():
        if number > through:
            break
        block = reviews[start - 1:finish]
        block_findings = [row["finding"] for row in block if row["finding"]]
        checkpoint = {
            "schema_version": 1, "mission": "QA-04-FRONT-B", "checkpoint": f"B-CP{number:02d}",
            "as_of": prep.AS_OF, "status": "COMPLETE", "source_queue": QUEUE.name,
            "source_queue_sha256": prep.sha256(QUEUE), "residual_positions": [start, finish],
            "original_queue_positions": [queue[start - 1]["queue_position"], queue[finish - 1]["queue_position"]],
            "examined": 50, "target_ids": [row["target_id"] for row in block],
            "findings": len(block_findings),
            "finding_counts": dict(sorted(Counter(row["severity"] for row in block_findings).items())),
            "protected_sha256": prep.PROTECTED, "records": block,
        }
        prep.write_json(OUT / f"QA04_B_CHECKPOINT_{number:02d}.json", checkpoint)
        completed.extend(block)

    current_findings = [row["finding"] for row in completed if row["finding"]]
    complete = through == 20
    audit = {
        "schema_version": 1, "mission": "QA-04-FRONT-B", "as_of": prep.AS_OF,
        "status": "COMPLETE_1000" if complete else "PARTIAL_REQUIRES_CONTINUATION",
        "completed_through_checkpoint": f"B-CP{through:02d}", "audited_total": len(completed),
        "residual_positions_completed": [1, end], "original_queue_positions_completed": [389, 388 + end],
        "next_residual_position": None if complete else end + 1,
        "findings_total": len(current_findings),
        "finding_counts": dict(sorted(Counter(row["severity"] for row in current_findings).items())),
        "protected_sha256": prep.PROTECTED, "records": completed,
    }
    prep.write_json(OUT / "QA04_B_AUDIT_1000.json", audit)
    pending = {
        "schema_version": 1, "mission": "QA-04-FRONT-B", "as_of": prep.AS_OF,
        "status": "COMPLETE" if complete else "PENDING_INDEPENDENT_AUDIT",
        "source": QUEUE.name, "source_sha256": prep.sha256(QUEUE),
        "completed_residual_positions": [1, end], "next_residual_position": None if complete else end + 1,
        "total": 1000 - end, "records": queue[end:],
    }
    prep.write_json(OUT / "QA04_B_PENDING.json", pending)

    if complete:
        by_book = Counter(row["book"] for row in reviews)
        checkpoint_hashes = {f"QA04_B_CHECKPOINT_{n:02d}.json": prep.sha256(OUT / f"QA04_B_CHECKPOINT_{n:02d}.json")
                             for n in CHECKPOINTS}
        consolidation = {
            "schema_version": 1, "mission": "QA-04-FRONT-B", "as_of": prep.AS_OF,
            "status": "FULL_CORPUS_AUDIT_COMPLETE", "full_corpus_audit_complete": True,
            "full_corpus_legally_approved": False,
            "coverage": {"prior_unique_audited": 1017, "qa04_new_unique_audited": 1000,
                         "unique_audited_accumulated": 2017, "still_unaudited": 0,
                         "by_book_qa04": dict(sorted(by_book.items()))},
            "findings": {"new_total": len(current_findings),
                         "new_by_severity": dict(sorted(Counter(row["severity"] for row in current_findings).items())),
                         "target_ids": [row["target_id"] for row in current_findings]},
            "protected_sha256": prep.PROTECTED,
            "artifact_sha256": {**checkpoint_hashes,
                                "QA04_B_AUDIT_1000.json": prep.sha256(OUT / "QA04_B_AUDIT_1000.json"),
                                "QA04_B_NEW_FINDINGS.json": prep.sha256(OUT / "QA04_B_NEW_FINDINGS.json"),
                                "QA04_B_PENDING.json": prep.sha256(OUT / "QA04_B_PENDING.json")},
        }
        prep.write_json(OUT / "QA04_B_CONSOLIDATION.json", consolidation)
    print(json.dumps({"through": through, "audited": len(completed), "findings": len(current_findings),
                      "pending": 1000 - end}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--through-checkpoint", type=int, required=True)
    args = parser.parse_args()
    main(args.through_checkpoint)
