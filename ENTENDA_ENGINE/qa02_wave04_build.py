"""Build resumable QA-02 wave-four checkpoints for source positions 201-577."""
import argparse
import json
from collections import Counter

import qa02_wave02_build as base

HERE = base.HERE
OUT = base.OUT
CORPUS = base.CORPUS
SOURCE_QUEUE = OUT / "QA02_PENDING_PRIORITY_WAVE_04.json"
PRIOR_QUEUE = OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_03.json"
PRIOR_CONSOLIDATION = OUT / "QA02_CONSOLIDATION_WAVE_03.json"
REVIEW_FILES = (
    OUT / "QA02_WAVE04_REVIEW_201_325.json",
    OUT / "QA02_WAVE04_REVIEW_326_450.json",
    OUT / "QA02_WAVE04_REVIEW_451_577.json",
)
FINDING_FILES = (
    OUT / "QA02_WAVE04_FINDINGS_201_325.json",
    OUT / "QA02_WAVE04_FINDINGS_326_450.json",
    OUT / "QA02_WAVE04_FINDINGS_451_577.json",
)
EXPECTED_QUEUE_SHA256 = "0933db90fea763f457c91b5ea30f1f39a688e6ba3e094f9479cb0bac541828b9"
EXPECTED_PRIOR_QUEUE_SHA256 = "f56e044382fad87c7d2779cc19d310c65eb8a3adfa8201769fa9dd97f33f8164"
CHECKPOINTS = {
    18: (201, 225), 19: (226, 250), 20: (251, 275), 21: (276, 300),
    22: (301, 325), 23: (326, 350), 24: (351, 375), 25: (376, 400),
    26: (401, 425), 27: (426, 450), 28: (451, 475), 29: (476, 500),
    30: (501, 525), 31: (526, 550), 32: (551, 575), 33: (576, 577),
}


def load_modules(paths, key):
    values = []
    for path in paths:
        doc = json.loads(path.read_text(encoding="utf-8"))
        values.extend(doc[key])
    return values


def main(through):
    if through not in CHECKPOINTS:
        raise SystemExit("--through-checkpoint must be between 18 and 33")
    if base.sha256(SOURCE_QUEUE) != EXPECTED_QUEUE_SHA256:
        raise RuntimeError("wave-four source queue hash mismatch")
    if base.sha256(PRIOR_QUEUE) != EXPECTED_PRIOR_QUEUE_SHA256:
        raise RuntimeError("prior correction queue hash mismatch")
    if base.current_hashes() != base.PROTECTED:
        raise RuntimeError("protected artifact hash mismatch")

    queue = json.loads(SOURCE_QUEUE.read_text(encoding="utf-8"))
    queued = queue["records"]
    queue_ids = [item["target_id"] for item in queued]
    if len(queued) != 377 or len(queue_ids) != len(set(queue_ids)):
        raise RuntimeError("wave-four queue is not exactly 377 unique records")
    if [item["source_queue_position"] for item in queued] != list(range(201, 578)):
        raise RuntimeError("wave-four source positions are not contiguous 201-577")

    reviews = load_modules(REVIEW_FILES, "records")
    review_map = {item["target_id"]: item for item in reviews}
    if len(reviews) != 377 or len(review_map) != 377 or set(review_map) != set(queue_ids):
        raise RuntimeError("review modules do not cover the exact wave-four queue")
    for meta in queued:
        review = review_map[meta["target_id"]]
        if review["source_queue_position"] != meta["source_queue_position"]:
            raise RuntimeError(f"review position mismatch for {meta['target_id']}")

    module_findings = load_modules(FINDING_FILES, "findings")
    findings = {item["target_id"]: item for item in module_findings}
    if len(module_findings) != len(findings) or not set(findings) <= set(queue_ids):
        raise RuntimeError("finding modules contain duplicate or out-of-queue targets")
    for target, review in review_map.items():
        expected = review["result"] == "ACHADO"
        if expected != (target in findings):
            raise RuntimeError(f"review/finding disagreement for {target}")
        if expected and review.get("finding") != findings[target]:
            raise RuntimeError(f"finding payload disagreement for {target}")

    master_findings = {
        "schema_version": 1,
        "mission": "QA-02-WAVE-04",
        "as_of": base.AS_OF,
        "findings": [findings[target] for target in queue_ids if target in findings],
    }
    base.write_json(OUT / "QA02_WAVE04_FINDINGS.json", master_findings)

    rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines()]
    active = {row["target_id"]: row for row in rows if row["status"] == "ACTIVE"}
    if not set(queue_ids) <= set(active):
        raise RuntimeError("queue includes a target without an active explanation")
    prior_ids = {
        record["target_id"]
        for wave in (1, 2, 3)
        for record in json.loads((OUT / f"QA02_AUDIT_WAVE_{wave:02d}.json").read_text(encoding="utf-8"))["records"]
    }
    if prior_ids & set(queue_ids):
        raise RuntimeError("wave-four target repeats a prior audit")

    end_position = CHECKPOINTS[through][1]
    selected = [item for item in queued if item["source_queue_position"] <= end_position]
    all_records = []
    for checkpoint, (start, end) in CHECKPOINTS.items():
        if checkpoint > through:
            break
        block = [item for item in queued if start <= item["source_queue_position"] <= end]
        records = []
        for meta in block:
            target = meta["target_id"]
            review = review_map[target]
            record = base.build_record(target, meta["source_queue_position"], active[target], meta, findings.get(target))
            record["comparison"] = review["comparison"]
            known_urls = {source["url"] for source in record["sources"]}
            record["sources"].extend(source for source in review.get("sources", []) if source["url"] not in known_urls)
            record["independent_review_module"] = review.get("review_module", "QA02_WAVE04_DELEGATED_REVIEW")
            record["reviewer"] = review.get("reviewer", "delegated-independent-auditor")
            records.append(record)
        block_findings = [record["finding"] for record in records if record["finding"]]
        checkpoint_doc = {
            "schema_version": 1,
            "mission": "QA-02-WAVE-04",
            "checkpoint": checkpoint,
            "as_of": base.AS_OF,
            "source_queue": SOURCE_QUEUE.name,
            "source_queue_sha256": EXPECTED_QUEUE_SHA256,
            "source_queue_positions": [start, end],
            "examined": len(records),
            "target_ids": [record["target_id"] for record in records],
            "findings": len(block_findings),
            "finding_counts": dict(sorted(Counter(item["severity"] for item in block_findings).items())),
            "protected_sha256": base.PROTECTED,
            "records": records,
        }
        base.write_json(OUT / f"QA02_CHECKPOINT_{checkpoint:02d}.json", checkpoint_doc)
        all_records.extend(records)

    new_findings = [record["finding"] for record in all_records if record["finding"]]
    completed = through == 33
    audit = {
        "schema_version": 1,
        "mission": "QA-02-WAVE-04",
        "as_of": base.AS_OF,
        "completed_through_checkpoint": through,
        "status": "PRIORITY_AUDIT_COMPLETE" if completed else "PARTIAL_REQUIRES_CONTINUATION",
        "audited_total": len(all_records),
        "source_queue_positions_completed": [201, end_position],
        "next_source_queue_position": None if completed else end_position + 1,
        "findings_total": len(new_findings),
        "finding_counts": dict(sorted(Counter(item["severity"] for item in new_findings).items())),
        "protected_sha256": base.PROTECTED,
        "records": all_records,
    }
    base.write_json(OUT / "QA02_AUDIT_WAVE_04.json", audit)

    prior = json.loads(PRIOR_QUEUE.read_text(encoding="utf-8"))
    consolidated = {
        "schema_version": 1,
        "mission": "QA-02",
        "as_of": base.AS_OF,
        "status": "VERSIONED_CONSOLIDATED_CORRECTION_QUEUE",
        "prior_source": PRIOR_QUEUE.name,
        "prior_sha256": EXPECTED_PRIOR_QUEUE_SHA256,
        "wave_01_findings": prior["wave_01_findings"],
        "wave_02_findings": prior["wave_02_findings"],
        "wave_03_findings": prior["wave_03_findings"],
        "wave_04_findings": new_findings,
        "total": prior["total"] + len(new_findings),
    }
    base.write_json(OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_04.json", consolidated)

    remaining = [item for item in queued if item["source_queue_position"] > end_position]
    continuation = {
        "schema_version": 1,
        "mission": "QA-02",
        "as_of": base.AS_OF,
        "status": "PRIORITY_AUDIT_COMPLETE" if completed else "PENDING_INDEPENDENT_LEGAL_AUDIT",
        "source": SOURCE_QUEUE.name,
        "source_sha256": EXPECTED_QUEUE_SHA256,
        "completed_source_positions": [201, end_position],
        "next_source_position": None if completed else remaining[0]["source_queue_position"],
        "total": len(remaining),
        "records": remaining,
    }
    base.write_json(OUT / "QA02_PENDING_PRIORITY_AFTER_WAVE_04.json", continuation)

    if completed:
        prior_consolidation = json.loads(PRIOR_CONSOLIDATION.read_text(encoding="utf-8"))
        by_book = Counter(prior_consolidation["coverage"]["by_book_accumulated"])
        by_book.update(record["book"] for record in all_records)
        prior_findings = prior["wave_01_findings"] + prior["wave_02_findings"] + prior["wave_03_findings"]
        accumulated = prior_findings + new_findings
        checkpoint_hashes = {
            f"QA02_CHECKPOINT_{number:02d}.json": base.sha256(OUT / f"QA02_CHECKPOINT_{number:02d}.json")
            for number in CHECKPOINTS
        }
        consolidation = {
            "schema_version": 1,
            "mission": "QA-02-WAVE-04",
            "as_of": base.AS_OF,
            "status": "PRIORITY_AUDIT_COMPLETE",
            "full_corpus_audit_complete": False,
            "completed_checkpoints": list(CHECKPOINTS),
            "coverage": {
                "active_explanations": 2017,
                "versions": 2180,
                "historical_versions": 163,
                "priority_total": 599,
                "wave_04_priority_audited": len(all_records),
                "priority_audited_accumulated": 222 + len(all_records),
                "priority_pending": len(remaining),
                "unique_audited_accumulated": 252 + len(all_records),
                "nonpriority_unaudited": 1388,
                "by_book_accumulated": dict(sorted(by_book.items())),
            },
            "findings": {
                "wave_04_total": len(new_findings),
                "wave_04_by_severity": dict(sorted(Counter(item["severity"] for item in new_findings).items())),
                "accumulated_total": len(accumulated),
                "accumulated_by_severity": dict(sorted(Counter(item["severity"] for item in accumulated).items())),
                "wave_04_target_ids": [item["target_id"] for item in new_findings],
                "blocking_target_ids": [item["target_id"] for item in accumulated if item["severity"] == "CRÍTICO"],
            },
            "protected_sha256": base.PROTECTED,
            "immutability": {
                "editorial_corpus_changed": False,
                "candidate_indexes_changed": False,
                "production_indexes_changed": False,
                "deploy_performed": False,
            },
            "continuation": {
                "priority_queue_complete": True,
                "pending_priority_queue": "QA02_PENDING_PRIORITY_AFTER_WAVE_04.json",
                "pending_priority_queue_sha256": base.sha256(OUT / "QA02_PENDING_PRIORITY_AFTER_WAVE_04.json"),
                "recommended_next_scope": "Independent individual audit of the 1,388 nonpriority explanations",
            },
            "artifact_sha256": {
                **checkpoint_hashes,
                "QA02_AUDIT_WAVE_04.json": base.sha256(OUT / "QA02_AUDIT_WAVE_04.json"),
                "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_04.json": base.sha256(OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_04.json"),
                "QA02_PENDING_PRIORITY_AFTER_WAVE_04.json": base.sha256(OUT / "QA02_PENDING_PRIORITY_AFTER_WAVE_04.json"),
                "QA02_WAVE04_FINDINGS.json": base.sha256(OUT / "QA02_WAVE04_FINDINGS.json"),
            },
        }
        base.write_json(OUT / "QA02_CONSOLIDATION_WAVE_04.json", consolidation)
    print(json.dumps({"through": through, "audited": len(all_records), "findings": len(new_findings),
                      "remaining": len(remaining)}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--through-checkpoint", type=int, required=True)
    args = parser.parse_args()
    main(args.through_checkpoint)
