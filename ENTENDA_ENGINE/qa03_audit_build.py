"""Build deterministic QA-03 Front-B checkpoints from delegated independent reviews."""
import argparse
import json
from collections import Counter

import qa02_wave02_build as base
import qa03_prepare as prep

OUT = prep.OUT
QUEUE = OUT / "QA03_AUDIT_388_QUEUE.json"
REMAINING = OUT / "QA03_UNAUDITED_REMAINING_1000.json"
REVIEW_FILES = (OUT / "QA03_B_REVIEW_001_194.json", OUT / "QA03_B_REVIEW_195_388.json")
FINDING_FILES = (OUT / "QA03_B_FINDINGS_001_194.json", OUT / "QA03_B_FINDINGS_195_388.json")
EXPECTED_QUEUE_SHA256 = "b42fdebc0027548ce3458e188ff748c963bf7ff5c6c8d675ddaf2d4a82148e08"
EXPECTED_REMAINING_SHA256 = "8c798f79745f4d878b882e582bbfa71effbcb6c99c7763bf77cfc51e2b5151df"
CHECKPOINTS = {number: ((number - 1) * 25 + 1, min(number * 25, 388)) for number in range(1, 17)}


def load_all(paths, key):
    values = []
    for path in paths:
        values.extend(json.loads(path.read_text(encoding="utf-8"))[key])
    return values


def main(through):
    if through not in CHECKPOINTS:
        raise SystemExit("--through-checkpoint must be between 1 and 16")
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")
    if prep.sha256(QUEUE) != EXPECTED_QUEUE_SHA256 or prep.sha256(REMAINING) != EXPECTED_REMAINING_SHA256:
        raise RuntimeError("persisted QA-03 queue hash mismatch")

    queue = json.loads(QUEUE.read_text(encoding="utf-8"))["records"]
    if len(queue) != 388 or [item["queue_position"] for item in queue] != list(range(1, 389)):
        raise RuntimeError("invalid 388-record queue")
    reviews = load_all(REVIEW_FILES, "records")
    review_map = {item["target_id"]: item for item in reviews}
    if len(reviews) != 388 or len(review_map) != 388:
        raise RuntimeError("review modules are not exactly 388 unique records")
    if [item["target_id"] for item in reviews] != [item["target_id"] for item in queue]:
        raise RuntimeError("review modules do not follow the persisted queue")
    for meta in queue:
        if review_map[meta["target_id"]]["queue_position"] != meta["queue_position"]:
            raise RuntimeError(f"review position mismatch for {meta['target_id']}")

    finding_values = load_all(FINDING_FILES, "findings")
    finding_map = {item["target_id"]: item for item in finding_values}
    if len(finding_values) != len(finding_map) or not set(finding_map) <= set(review_map):
        raise RuntimeError("duplicate or out-of-scope new finding")
    for target, review in review_map.items():
        is_finding = review["result"] == "ACHADO"
        if is_finding != (target in finding_map):
            raise RuntimeError(f"review/finding disagreement for {target}")
        if is_finding and review.get("finding") != finding_map[target]:
            raise RuntimeError(f"finding payload disagreement for {target}")

    master_findings = {
        "schema_version": 1, "mission": "QA-03-FRONT-B", "as_of": prep.AS_OF,
        "status": "NEW_FINDINGS_NOT_SILENTLY_CORRECTED",
        "findings": [finding_map[item["target_id"]] for item in queue if item["target_id"] in finding_map],
    }
    prep.write_json(OUT / "QA03_B_NEW_FINDINGS.json", master_findings)

    rows = [json.loads(line) for line in prep.CORPUS.read_text(encoding="utf-8").splitlines()]
    active = {row["target_id"]: row for row in rows if row["status"] == "ACTIVE"}
    prior_audited = set()
    for wave in range(1, 5):
        prior = json.loads((prep.QA02 / f"QA02_AUDIT_WAVE_{wave:02d}.json").read_text(encoding="utf-8"))
        prior_audited.update(record["target_id"] for record in prior["records"])
    queue_ids = {item["target_id"] for item in queue}
    if prior_audited & queue_ids or not queue_ids <= set(active):
        raise RuntimeError("new audit queue overlaps QA-02 or lacks active explanation")

    end_position = CHECKPOINTS[through][1]
    all_records = []
    for number, (start, end) in CHECKPOINTS.items():
        if number > through:
            break
        block = queue[start - 1:end]
        records = []
        for meta in block:
            target = meta["target_id"]
            review = review_map[target]
            queue_meta = {**meta, "mission": meta["origin_mission"]}
            record = base.build_record(target, meta["queue_position"], active[target], queue_meta, finding_map.get(target))
            record["as_of"] = prep.AS_OF
            record["comparison"] = review["comparison"]
            merged = {source["url"]: {**source, "accessed_on": prep.AS_OF} for source in record["sources"]}
            for source in review.get("sources", []):
                merged[source["url"]] = source
            record["sources"] = list(merged.values())
            record["independent_review_module"] = review.get("review_module", "QA03_FRONT_B_DELEGATED_REVIEW")
            record["reviewer"] = review.get("auditor", "delegated-independent-auditor")
            records.append(record)
        findings = [record["finding"] for record in records if record["finding"]]
        checkpoint = {
            "schema_version": 1, "mission": "QA-03-FRONT-B", "checkpoint": f"B-CP{number:02d}",
            "as_of": prep.AS_OF, "status": "COMPLETE",
            "source_queue": QUEUE.name, "source_queue_sha256": EXPECTED_QUEUE_SHA256,
            "queue_positions": [start, end], "examined": len(records),
            "target_ids": [record["target_id"] for record in records],
            "findings": len(findings),
            "finding_counts": dict(sorted(Counter(item["severity"] for item in findings).items())),
            "protected_sha256": prep.PROTECTED, "records": records,
        }
        prep.write_json(OUT / f"QA03_B_CHECKPOINT_{number:02d}.json", checkpoint)
        all_records.extend(records)

    new_findings = [record["finding"] for record in all_records if record["finding"]]
    complete = through == 16
    audit = {
        "schema_version": 1, "mission": "QA-03-FRONT-B", "as_of": prep.AS_OF,
        "status": "COMPLETE_388" if complete else "PARTIAL_REQUIRES_CONTINUATION",
        "completed_through_checkpoint": f"B-CP{through:02d}",
        "audited_total": len(all_records), "queue_positions_completed": [1, end_position],
        "next_queue_position": None if complete else end_position + 1,
        "findings_total": len(new_findings),
        "finding_counts": dict(sorted(Counter(item["severity"] for item in new_findings).items())),
        "protected_sha256": prep.PROTECTED, "records": all_records,
    }
    prep.write_json(OUT / "QA03_B_AUDIT_388.json", audit)
    pending_selected = {
        "schema_version": 1, "mission": "QA-03-FRONT-B", "as_of": prep.AS_OF,
        "status": "COMPLETE" if complete else "PENDING_INDEPENDENT_AUDIT",
        "source": QUEUE.name, "source_sha256": EXPECTED_QUEUE_SHA256,
        "completed_queue_positions": [1, end_position],
        "next_queue_position": None if complete else end_position + 1,
        "total": 388 - end_position, "records": queue[end_position:],
    }
    prep.write_json(OUT / "QA03_B_SELECTED_PENDING.json", pending_selected)

    if complete:
        checkpoint_hashes = {
            f"QA03_B_CHECKPOINT_{number:02d}.json": prep.sha256(OUT / f"QA03_B_CHECKPOINT_{number:02d}.json")
            for number in CHECKPOINTS
        }
        by_book = Counter(item["book"] for item in queue)
        consolidation = {
            "schema_version": 1, "mission": "QA-03-FRONT-B", "as_of": prep.AS_OF,
            "status": "COMPLETE_388", "full_corpus_audit_complete": False,
            "coverage": {
                "qa02_unique_audited": 629, "qa03_new_unique_audited": 388,
                "unique_audited_accumulated": 1017, "still_unaudited": 1000,
                "by_book_qa03": dict(sorted(by_book.items())),
            },
            "findings": {
                "new_total": len(new_findings),
                "new_by_severity": dict(sorted(Counter(item["severity"] for item in new_findings).items())),
                "target_ids": [item["target_id"] for item in new_findings],
            },
            "protected_sha256": prep.PROTECTED,
            "continuation": {
                "queue": REMAINING.name, "queue_sha256": EXPECTED_REMAINING_SHA256,
                "remaining": 1000,
            },
            "artifact_sha256": {
                **checkpoint_hashes,
                "QA03_B_AUDIT_388.json": prep.sha256(OUT / "QA03_B_AUDIT_388.json"),
                "QA03_B_NEW_FINDINGS.json": prep.sha256(OUT / "QA03_B_NEW_FINDINGS.json"),
                "QA03_B_SELECTED_PENDING.json": prep.sha256(OUT / "QA03_B_SELECTED_PENDING.json"),
            },
        }
        prep.write_json(OUT / "QA03_B_CONSOLIDATION.json", consolidation)
    print(json.dumps({"through": through, "audited": len(all_records), "findings": len(new_findings),
                      "selected_pending": 388 - end_position}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--through-checkpoint", type=int, required=True)
    args = parser.parse_args()
    main(args.through_checkpoint)
