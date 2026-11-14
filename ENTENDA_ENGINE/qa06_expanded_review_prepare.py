"""Expand QA-06 non-high review to the full population after sample failure."""
import hashlib
import json

import qa06_prepare as prep


SOURCE_FILES = (
    ("0001_0672", "QA06_B_FINDINGS_V2_0001_0672.json"),
    ("0673_1344", "QA06_B_FINDINGS_V2_0673_1344.json"),
    ("1345_2017", "QA06_B_FINDINGS_V2_1345_2017.json"),
)
SAMPLE = prep.OUT / "QA06_B_NON_HIGH_STRATIFIED_SAMPLE.json"


def main():
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    sampled = {record["finding"]["subdivision_id"] for record in sample["records"]}
    remaining = []
    sources = {}
    for module, filename in SOURCE_FILES:
        path = prep.OUT / filename
        document = json.loads(path.read_text(encoding="utf-8"))
        sources[module] = {"file": filename, "sha256": prep.sha256(path)}
        for finding in document["findings"]:
            if finding["severity"] != "ALTO" and finding["subdivision_id"] not in sampled:
                remaining.append({"module": module, "source_file": filename, "finding": finding,
                                  "source_finding_sha256": prep.json_sha(finding)})
    middle = sorted((item for item in remaining if item["module"] == "0673_1344"),
                    key=lambda item: item["finding"]["audit_position"])
    last = sorted((item for item in remaining if item["module"] == "1345_2017"),
                  key=lambda item: hashlib.sha256(item["finding"]["subdivision_id"].encode("utf-8")).hexdigest())
    first = [item for item in remaining if item["module"] == "0001_0672"]
    if first or len(middle) != 173 or len(last) != 591 or len(remaining) != 764:
        raise RuntimeError(f"unexpected expanded-review cardinality: {len(first)}, {len(middle)}, {len(last)}")
    tasks = {
        "0673_1344_REMAINING": middle,
        "1345_2017_REMAINING_A": last[:296],
        "1345_2017_REMAINING_B": last[296:],
    }
    document = {
        "schema_version": 1, "mission": "QA-06-FINDINGS-QA-EXPANDED", "as_of": prep.AS_OF,
        "status": "FULL_NON_HIGH_REVIEW_REQUIRED_AFTER_RELEVANT_FALSE_POSITIVE_RATE",
        "trigger_sample": SAMPLE.name, "trigger_sample_sha256": prep.sha256(SAMPLE),
        "sample_result": {"reviewed": 120, "not_confirmed": 64,
                          "false_positive_rate": 0.5333333333,
                          "decision": "EXPAND_TO_ALL_REMAINING_NON_HIGH_FINDINGS"},
        "source_modules": sources,
        "population": {"source_findings": 1038, "high_reviewed_separately": 154,
                       "non_high_total": 884, "sampled_non_high": 120,
                       "remaining_non_high": 764},
        "tasks": {name: {"total": len(records), "records": records} for name, records in tasks.items()},
    }
    path = prep.OUT / "QA06_B_NON_HIGH_EXPANDED_REVIEW_PLAN.json"
    prep.write_json(path, document)
    print(json.dumps({"tasks": {name: len(records) for name, records in tasks.items()},
                      "total": len(remaining), "sha256": prep.sha256(path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
