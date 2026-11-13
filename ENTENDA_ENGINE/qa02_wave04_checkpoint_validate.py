"""Validate one persisted QA-02 wave-four checkpoint and cumulative state."""
import argparse
import json
import sys

import qa02_wave02_build as base
import qa02_wave04_build as wave4


def main(checkpoint):
    if checkpoint not in wave4.CHECKPOINTS:
        raise SystemExit("--checkpoint must be between 18 and 33")
    start, end = wave4.CHECKPOINTS[checkpoint]
    queue = json.loads(wave4.SOURCE_QUEUE.read_text(encoding="utf-8"))["records"]
    expected = [item for item in queue if start <= item["source_queue_position"] <= end]
    document = json.loads((wave4.OUT / f"QA02_CHECKPOINT_{checkpoint:02d}.json").read_text(encoding="utf-8"))
    records = document["records"]
    if document["source_queue_positions"] != [start, end] or document["examined"] != len(expected):
        raise RuntimeError("checkpoint range/count mismatch")
    if [record["target_id"] for record in records] != [item["target_id"] for item in expected]:
        raise RuntimeError("checkpoint target order mismatch")
    if [record["queue_position"] for record in records] != list(range(start, end + 1)):
        raise RuntimeError("checkpoint position mismatch")
    if len({record["target_id"] for record in records}) != len(records):
        raise RuntimeError("duplicate target in checkpoint")
    for record in records:
        if not record["sources"] or not record["current_law_snapshot"] or not record["legal_segments_checked"]:
            raise RuntimeError(f"incomplete legal evidence for {record['target_id']}")
        if len(record["checks"]["field_sha256"]) != 5 or len(record["comparison"]) <= 40:
            raise RuntimeError(f"incomplete field comparison for {record['target_id']}")

    audit = json.loads((wave4.OUT / "QA02_AUDIT_WAVE_04.json").read_text(encoding="utf-8"))
    expected_total = end - 200
    if audit["audited_total"] != expected_total or audit["completed_through_checkpoint"] != checkpoint:
        raise RuntimeError("cumulative audit mismatch")
    if len({record["target_id"] for record in audit["records"]}) != expected_total:
        raise RuntimeError("duplicate target in cumulative audit")

    prior = json.loads(wave4.PRIOR_QUEUE.read_text(encoding="utf-8"))
    corrections = json.loads((wave4.OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_04.json").read_text(encoding="utf-8"))
    for number in (1, 2, 3):
        key = f"wave_{number:02d}_findings"
        if corrections[key] != prior[key]:
            raise RuntimeError(f"prior findings changed: {key}")
    current_findings = [record["finding"] for record in audit["records"] if record["finding"]]
    if corrections["wave_04_findings"] != current_findings:
        raise RuntimeError("wave-four correction queue mismatch")

    pending = json.loads((wave4.OUT / "QA02_PENDING_PRIORITY_AFTER_WAVE_04.json").read_text(encoding="utf-8"))
    expected_pending = [item for item in queue if item["source_queue_position"] > end]
    if pending["records"] != expected_pending or pending["total"] != len(expected_pending):
        raise RuntimeError("pending queue mismatch")
    if base.current_hashes() != base.PROTECTED:
        raise RuntimeError("protected artifact hash mismatch")
    print(json.dumps({
        "checkpoint": checkpoint,
        "positions": [start, end],
        "examined": len(records),
        "cumulative": expected_total,
        "findings": document["findings"],
        "pending": len(expected_pending),
        "sha256": base.sha256(wave4.OUT / f"QA02_CHECKPOINT_{checkpoint:02d}.json"),
        "status": "OK",
    }, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=int, required=True)
    args = parser.parse_args()
    try:
        main(args.checkpoint)
    except Exception as error:
        print(f"checkpoint validation failed: {error}", file=sys.stderr)
        raise
