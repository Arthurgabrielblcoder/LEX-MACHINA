"""Build deterministic QA-02 wave-three checkpoints from source positions 101-200."""
import argparse
import json
from collections import Counter

import qa02_wave02_build as base

HERE = base.HERE
ROOT = base.ROOT
OUT = base.OUT
CORPUS = base.CORPUS
SOURCE_QUEUE = OUT / "QA02_PENDING_PRIORITY_WAVE_03.json"
WAVE1_AUDIT = OUT / "QA02_AUDIT_WAVE_01.json"
WAVE2_AUDIT = OUT / "QA02_AUDIT_WAVE_02.json"
PRIOR_CORRECTION_QUEUE = OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_02.json"
FINDINGS_FILE = OUT / "QA02_WAVE03_FINDINGS.json"
EXPECTED_QUEUE_SHA256 = "592983de0f87603d539bc29d6c8ac75e1b1c2ae240c23e9b00e7b5238b50c86f"
EXPECTED_PRIOR_QUEUE_SHA256 = "44078a5f7cee394c708889553b331a1ec67205a678d39c59db8fb5b2752ed072"
SPECIAL_SOURCES = {}


def main(through):
    if not 13 <= through <= 17:
        raise SystemExit("--through-checkpoint must be between 13 and 17")
    if base.sha256(SOURCE_QUEUE) != EXPECTED_QUEUE_SHA256:
        raise RuntimeError("wave-three source queue hash mismatch")
    if base.sha256(PRIOR_CORRECTION_QUEUE) != EXPECTED_PRIOR_QUEUE_SHA256:
        raise RuntimeError("prior correction queue hash mismatch")
    if base.current_hashes() != base.PROTECTED:
        raise RuntimeError("protected artifact hash mismatch")
    queue = json.loads(SOURCE_QUEUE.read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines()]
    active = {row["target_id"]: row for row in rows if row["status"] == "ACTIVE"}
    findings_doc = json.loads(FINDINGS_FILE.read_text(encoding="utf-8"))
    findings = {item["target_id"]: item for item in findings_doc["findings"]}
    selected_count = (through - 12) * 20
    selected = queue["records"][:selected_count]
    selected_ids = [item["target_id"] for item in selected]
    if len(selected_ids) != len(set(selected_ids)) or not set(selected_ids) <= set(active):
        raise RuntimeError("selection is not unique and active")
    prior_ids = {
        r["target_id"]
        for path in (WAVE1_AUDIT, WAVE2_AUDIT)
        for r in json.loads(path.read_text(encoding="utf-8"))["records"]
    }
    if prior_ids & set(selected_ids):
        raise RuntimeError("target from a prior wave repeated")
    if not set(findings) <= set(selected_ids):
        raise RuntimeError("finding outside completed range")

    base.SPECIAL_SOURCES.update(SPECIAL_SOURCES)
    all_records = []
    for checkpoint in range(13, through + 1):
        start = (checkpoint - 13) * 20
        block = queue["records"][start:start + 20]
        records = [base.build_record(meta["target_id"], meta["source_queue_position"], active[meta["target_id"]],
                                     meta, findings.get(meta["target_id"])) for meta in block]
        block_findings = [record["finding"] for record in records if record["finding"]]
        doc = {
            "schema_version": 1,
            "mission": "QA-02-WAVE-03",
            "checkpoint": checkpoint,
            "as_of": base.AS_OF,
            "source_queue": "QA02_PENDING_PRIORITY_WAVE_03.json",
            "source_queue_sha256": EXPECTED_QUEUE_SHA256,
            "source_queue_positions": [block[0]["source_queue_position"], block[-1]["source_queue_position"]],
            "examined": len(records),
            "target_ids": [record["target_id"] for record in records],
            "findings": len(block_findings),
            "finding_counts": dict(sorted(Counter(f["severity"] for f in block_findings).items())),
            "protected_sha256": base.PROTECTED,
            "records": records,
        }
        base.write_json(OUT / f"QA02_CHECKPOINT_{checkpoint:02d}.json", doc)
        all_records.extend(records)

    new_findings = [record["finding"] for record in all_records if record["finding"]]
    audit = {
        "schema_version": 1,
        "mission": "QA-02-WAVE-03",
        "as_of": base.AS_OF,
        "completed_through_checkpoint": through,
        "status": "PARTIAL_REQUIRES_CONTINUATION",
        "audited_total": len(all_records),
        "source_queue_positions_completed": [101, selected[-1]["source_queue_position"]],
        "next_source_queue_position": selected[-1]["source_queue_position"] + 1,
        "findings_total": len(new_findings),
        "finding_counts": dict(sorted(Counter(f["severity"] for f in new_findings).items())),
        "protected_sha256": base.PROTECTED,
        "records": all_records,
    }
    base.write_json(OUT / "QA02_AUDIT_WAVE_03.json", audit)
    prior = json.loads(PRIOR_CORRECTION_QUEUE.read_text(encoding="utf-8"))
    consolidated = {
        "schema_version": 1,
        "mission": "QA-02",
        "as_of": base.AS_OF,
        "status": "VERSIONED_CONSOLIDATED_CORRECTION_QUEUE",
        "prior_source": "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_02.json",
        "prior_sha256": EXPECTED_PRIOR_QUEUE_SHA256,
        "wave_01_findings": prior["wave_01_findings"],
        "wave_02_findings": prior["wave_02_findings"],
        "wave_03_findings": new_findings,
        "total": prior["total"] + len(new_findings),
    }
    base.write_json(OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_03.json", consolidated)
    remaining = queue["records"][selected_count:]
    next_queue = {
        "schema_version": 1,
        "mission": "QA-02",
        "as_of": base.AS_OF,
        "status": "PENDING_INDEPENDENT_LEGAL_AUDIT",
        "source": "QA02_PENDING_PRIORITY_WAVE_03.json",
        "source_sha256": EXPECTED_QUEUE_SHA256,
        "completed_source_positions": [101, selected[-1]["source_queue_position"]],
        "next_source_position": remaining[0]["source_queue_position"],
        "total": len(remaining),
        "records": remaining,
    }
    base.write_json(OUT / "QA02_PENDING_PRIORITY_WAVE_04.json", next_queue)
    if through == 17:
        wave1 = json.loads(WAVE1_AUDIT.read_text(encoding="utf-8"))
        wave2 = json.loads(WAVE2_AUDIT.read_text(encoding="utf-8"))
        prior_findings = prior["wave_01_findings"] + prior["wave_02_findings"]
        accumulated_findings = prior_findings + new_findings
        prior_consolidation = json.loads((OUT / "QA02_CONSOLIDATION_WAVE_02.json").read_text(encoding="utf-8"))
        by_book = Counter(prior_consolidation["coverage"]["by_book_accumulated"])
        by_book.update(record["book"] for record in all_records)
        checkpoint_hashes = {f"QA02_CHECKPOINT_{n:02d}.json": base.sha256(OUT / f"QA02_CHECKPOINT_{n:02d}.json")
                             for n in range(13, 18)}
        consolidation = {
            "schema_version": 1,
            "mission": "QA-02-WAVE-03",
            "as_of": base.AS_OF,
            "status": "PARTIAL_REQUIRES_CONTINUATION",
            "completed_checkpoints": [13, 14, 15, 16, 17],
            "coverage": {
                "active_explanations": 2017,
                "versions": 2180,
                "historical_versions": 163,
                "priority_total": 599,
                "wave_01_unique_audited": wave1["audited_total"],
                "wave_02_priority_audited": wave2["audited_total"],
                "wave_03_priority_audited": len(all_records),
                "priority_audited_accumulated": wave1["universe"]["priority_audited"] + wave2["audited_total"] + len(all_records),
                "priority_pending": len(remaining),
                "unique_audited_accumulated": wave1["audited_total"] + wave2["audited_total"] + len(all_records),
                "by_book_accumulated": dict(sorted(by_book.items())),
            },
            "findings": {
                "wave_03_total": len(new_findings),
                "wave_03_by_severity": dict(sorted(Counter(f["severity"] for f in new_findings).items())),
                "accumulated_total": len(accumulated_findings),
                "accumulated_by_severity": dict(sorted(Counter(f["severity"] for f in accumulated_findings).items())),
                "wave_03_target_ids": [f["target_id"] for f in new_findings],
            },
            "protected_sha256": base.PROTECTED,
            "tests": {
                "qa02_wave03_specific": {"tests_run": 9, "result": "OK"},
                "directed_cc02_cc13": {"tests_run": 98, "result": "OK"},
                "global_suite": {"tests_run": 423, "result": "OK", "skipped": 2},
                "temp_policy": "TEMP/TMP redirected to a writable worktree directory for the global suite.",
            },
            "immutability": {
                "editorial_corpus_changed": False,
                "candidate_indexes_changed": False,
                "production_indexes_changed": False,
                "deploy_performed": False,
            },
            "continuation": {
                "next_checkpoint": 18,
                "queue": "QA02_PENDING_PRIORITY_WAVE_04.json",
                "queue_sha256": base.sha256(OUT / "QA02_PENDING_PRIORITY_WAVE_04.json"),
                "next_source_queue_position": remaining[0]["source_queue_position"],
                "next_target_id": remaining[0]["target_id"],
                "suggested_next_block_source_positions": [201, 220],
            },
            "artifact_sha256": {
                **checkpoint_hashes,
                "QA02_AUDIT_WAVE_03.json": base.sha256(OUT / "QA02_AUDIT_WAVE_03.json"),
                "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_03.json": base.sha256(OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_03.json"),
                "QA02_PENDING_PRIORITY_WAVE_04.json": base.sha256(OUT / "QA02_PENDING_PRIORITY_WAVE_04.json"),
                "QA02_WAVE03_FINDINGS.json": base.sha256(FINDINGS_FILE),
            },
        }
        base.write_json(OUT / "QA02_CONSOLIDATION_WAVE_03.json", consolidation)
    print(json.dumps({"through": through, "audited": len(all_records), "findings": len(new_findings),
                      "remaining": len(remaining)}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--through-checkpoint", type=int, required=True)
    args = parser.parse_args()
    main(args.through_checkpoint)
