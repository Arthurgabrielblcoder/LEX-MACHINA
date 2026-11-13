"""Validate one QA-03 Front-B checkpoint and cumulative audit state."""
import argparse
import json

import qa03_audit_build as build
import qa03_prepare as prep


def main(number):
    if number not in build.CHECKPOINTS:
        raise SystemExit("--checkpoint must be between 1 and 16")
    start, end = build.CHECKPOINTS[number]
    queue = json.loads(build.QUEUE.read_text(encoding="utf-8"))["records"]
    checkpoint = json.loads((build.OUT / f"QA03_B_CHECKPOINT_{number:02d}.json").read_text(encoding="utf-8"))
    records = checkpoint["records"]
    expected = queue[start - 1:end]
    if checkpoint["queue_positions"] != [start, end] or checkpoint["examined"] != len(expected):
        raise RuntimeError("checkpoint range/count mismatch")
    if [record["target_id"] for record in records] != [item["target_id"] for item in expected]:
        raise RuntimeError("checkpoint target order mismatch")
    if [record["queue_position"] for record in records] != list(range(start, end + 1)):
        raise RuntimeError("checkpoint position mismatch")
    for record in records:
        if not record["sources"] or not record["legal_segments_checked"] or len(record["checks"]["field_sha256"]) != 5:
            raise RuntimeError(f"incomplete evidence for {record['target_id']}")
        if len(record["comparison"]) <= 80:
            raise RuntimeError(f"non-specific comparison for {record['target_id']}")

    audit = json.loads((build.OUT / "QA03_B_AUDIT_388.json").read_text(encoding="utf-8"))
    if audit["audited_total"] != end or audit["completed_through_checkpoint"] != f"B-CP{number:02d}":
        raise RuntimeError("cumulative audit mismatch")
    current_ids = [record["target_id"] for record in audit["records"]]
    if current_ids != [item["target_id"] for item in queue[:end]] or len(current_ids) != len(set(current_ids)):
        raise RuntimeError("cumulative target mismatch or duplicate")
    pending = json.loads((build.OUT / "QA03_B_SELECTED_PENDING.json").read_text(encoding="utf-8"))
    if pending["records"] != queue[end:] or pending["total"] != 388 - end:
        raise RuntimeError("selected pending queue mismatch")
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline changed")
    print(json.dumps({
        "checkpoint": f"B-CP{number:02d}", "positions": [start, end], "examined": len(records),
        "cumulative": end, "findings": checkpoint["findings"], "pending": 388 - end,
        "sha256": prep.sha256(build.OUT / f"QA03_B_CHECKPOINT_{number:02d}.json"), "status": "OK",
    }, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=int, required=True)
    args = parser.parse_args()
    main(args.checkpoint)
