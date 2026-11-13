"""Validate a QA-04 Front-B checkpoint and cumulative state."""
import argparse
import json

import qa04_audit_build as build
import qa04_prepare as prep


def main(number):
    if number not in build.CHECKPOINTS:
        raise SystemExit("--checkpoint must be between 1 and 20")
    start, end = build.CHECKPOINTS[number]
    queue = json.loads(build.QUEUE.read_text(encoding="utf-8"))["records"]
    checkpoint = json.loads((build.OUT / f"QA04_B_CHECKPOINT_{number:02d}.json").read_text(encoding="utf-8"))
    records = checkpoint["records"]
    expected = queue[start - 1:end]
    if checkpoint["residual_positions"] != [start, end] or checkpoint["examined"] != 50:
        raise RuntimeError("checkpoint range/count mismatch")
    if [row["target_id"] for row in records] != [row["target_id"] for row in expected]:
        raise RuntimeError("checkpoint order mismatch")
    if [row["residual_position"] for row in records] != list(range(start, end + 1)):
        raise RuntimeError("residual position mismatch")
    if [row["queue_position"] for row in records] != list(range(388 + start, 389 + end)):
        raise RuntimeError("original queue position mismatch")
    audit = json.loads((build.OUT / "QA04_B_AUDIT_1000.json").read_text(encoding="utf-8"))
    if audit["audited_total"] != end or audit["completed_through_checkpoint"] != f"B-CP{number:02d}":
        raise RuntimeError("cumulative audit mismatch")
    if len({row["target_id"] for row in audit["records"]}) != end:
        raise RuntimeError("cumulative duplicate")
    pending = json.loads((build.OUT / "QA04_B_PENDING.json").read_text(encoding="utf-8"))
    if pending["total"] != 1000 - end or pending["records"] != queue[end:]:
        raise RuntimeError("pending queue mismatch")
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline changed")
    print(json.dumps({"checkpoint": f"B-CP{number:02d}", "residual_positions": [start, end],
                      "original_positions": [388 + start, 388 + end], "examined": 50,
                      "cumulative": end, "findings": checkpoint["findings"], "pending": 1000 - end,
                      "sha256": prep.sha256(build.OUT / f"QA04_B_CHECKPOINT_{number:02d}.json"),
                      "status": "OK"}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=int, required=True)
    args = parser.parse_args()
    main(args.checkpoint)
