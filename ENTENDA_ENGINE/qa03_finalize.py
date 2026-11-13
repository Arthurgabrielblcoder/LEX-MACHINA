"""Persist deterministic final evidence for QA-03."""
import json
from pathlib import Path

import qa03_prepare as prep


OUT = prep.OUT
CANDIDATE_DIR = prep.HERE / "derived/candidate_qa03_cc_001_2046"
CANDIDATE = CANDIDATE_DIR / "CC2002_QA03.entenda.jsonl"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")

    editorial = load(OUT / "QA03_EDITORIAL_CORRECTIONS_78.json")
    revalidation = load(OUT / "QA03_EDITORIAL_REVALIDATION_78.json")
    resolution = load(OUT / "QA03_CORRECTION_RESOLUTION_78.json")
    audit = load(OUT / "QA03_B_AUDIT_388.json")
    b_summary = load(OUT / "QA03_B_CONSOLIDATION.json")
    candidate_manifest = load(CANDIDATE_DIR / "QA03_CANDIDATE_MANIFEST.json")
    remaining = load(OUT / "QA03_UNAUDITED_REMAINING_1000.json")

    critical = {
        "CC2002:ART.1258", "CC2002:ART.1276", "CC2002:ART.1641", "CC2002:ART.2016"
    }
    if editorial["total"] != 78 or revalidation["decision_counts"] != {"CONFIRMED_CORRECTED": 78}:
        raise RuntimeError("front A is incomplete")
    if set(resolution["critical_status"]) != critical or resolution["pending"] != 0:
        raise RuntimeError("critical or correction resolution mismatch")
    if audit["audited_total"] != 388 or audit["findings_total"] != 4:
        raise RuntimeError("front B is incomplete")
    if b_summary["coverage"]["unique_audited_accumulated"] != 1017 or remaining["total"] != 1000:
        raise RuntimeError("coverage or residual mismatch")

    a_checkpoints = {
        f"A-CP{number:02d}": prep.sha256(
            OUT / ("QA03_A_CP01_INVENTORY.json" if number == 1 else f"QA03_A_CP{number:02d}.json")
        ) for number in range(1, 13)
    }
    b_checkpoints = {
        f"B-CP{number:02d}": prep.sha256(OUT / f"QA03_B_CHECKPOINT_{number:02d}.json")
        for number in range(1, 17)
    }

    tests = {
        "schema_version": 1,
        "mission": "QA-03",
        "as_of": prep.AS_OF,
        "status": "PASS",
        "temporary_directory": ".tmp_qa03 within worktree",
        "directed_regression": {
            "scope": "CC-02 through CC-13 plus QA-02 waves and QA-03",
            "executed": 148,
            "passed": 148,
            "failed": 0,
            "errors": 0,
        },
        "global_suite": {
            "executed": 443,
            "passed": 441,
            "skipped": 2,
            "failed": 0,
            "errors": 0,
            "elapsed_seconds": 132.156,
        },
        "determinism": {
            "status": "PASS",
            "rebuilders": [
                "qa03_prepare.py", "qa03_revalidate_corrections.py",
                "qa03_audit_build.py --through-checkpoint 16", "qa03_correction_build.py",
            ],
            "comparison": "byte-identical queues, evidence, candidate corpus and runtime indexes",
        },
        "git_materialization": {
            "status": "PASS_AFTER_CANDIDATE_COMMIT",
            "note": "The pre-commit run exposed the expected tracked/untracked index-pair difference; the post-commit global run passed.",
        },
    }
    prep.write_json(OUT / "QA03_TEST_EVIDENCE.json", tests)

    final = {
        "schema_version": 1,
        "mission": "QA-03",
        "as_of": prep.AS_OF,
        "status": "COMPLETE_PARTIAL_CORPUS_AUDIT",
        "full_corpus_audit_complete": False,
        "recovery": {
            "editorial_module_records_recovered": 78,
            "audit_module_001_194_records_recovered": 194,
            "audit_module_195_388_records_recovered": 194,
            "modules_regenerated": 0,
            "individual_audits_repeated": 0,
        },
        "front_a": {
            "known_findings_examined": 78,
            "confirmed": 78,
            "corrected": 78,
            "independently_revalidated": 78,
            "pending": 0,
            "severity_counts": resolution["severity_counts"],
            "critical_status": resolution["critical_status"],
            "versioned_targets": candidate_manifest["versioned_targets"],
            "formal_review_status": "PENDING_HUMAN_REVIEW",
            "human_approval_claimed": False,
        },
        "front_b": {
            "new_unique_audits": 388,
            "prior_unique_audits": 629,
            "unique_audits_accumulated": 1017,
            "remaining_queue": 1000,
            "new_findings": b_summary["findings"],
        },
        "candidate": {
            "path": "ENTENDA_ENGINE/derived/candidate_qa03_cc_001_2046/CC2002_QA03.entenda.jsonl",
            "versions": candidate_manifest["records"],
            "active": candidate_manifest["active"],
            "historical": candidate_manifest["historical"],
            "corpus_sha256": prep.sha256(CANDIDATE),
            "lookup_sha256": prep.sha256(CANDIDATE_DIR / "candidate_index/ENTENDA_LOOKUP.IDX"),
            "payload_sha256": prep.sha256(CANDIDATE_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT"),
            "build_manifest_sha256": prep.sha256(CANDIDATE_DIR / "candidate_index/ENTENDA_BUILD_MANIFEST.json"),
            "candidate_only": True,
        },
        "protected_cc13": {
            "preserved": True,
            "sha256": prep.PROTECTED,
            "versions": 2180,
            "active": 2017,
            "historical": 163,
        },
        "checkpoints": {
            "front_a_total": 12,
            "front_a_sha256": a_checkpoints,
            "front_b_total": 16,
            "front_b_sha256": b_checkpoints,
        },
        "queues": {
            "full_unaudited_baseline_sha256": prep.sha256(OUT / "QA03_UNAUDITED_FULL_QUEUE.json"),
            "selected_388_sha256": prep.sha256(OUT / "QA03_AUDIT_388_QUEUE.json"),
            "remaining_1000_sha256": prep.sha256(OUT / "QA03_UNAUDITED_REMAINING_1000.json"),
            "new_findings_sha256": prep.sha256(OUT / "QA03_B_NEW_FINDINGS.json"),
        },
        "evidence": {
            "editorial_sha256": prep.sha256(OUT / "QA03_EDITORIAL_CORRECTIONS_78.json"),
            "revalidation_sha256": prep.sha256(OUT / "QA03_EDITORIAL_REVALIDATION_78.json"),
            "audit_388_sha256": prep.sha256(OUT / "QA03_B_AUDIT_388.json"),
            "test_evidence_sha256": prep.sha256(OUT / "QA03_TEST_EVIDENCE.json"),
        },
        "deployment": {
            "performed": False,
            "production_indexes_modified": False,
            "firmware_accessed": False,
            "microsd_accessed": False,
            "esp32_accessed": False,
        },
    }
    prep.write_json(OUT / "QA03_FINAL_CONSOLIDATION.json", final)
    print(json.dumps({
        "corrected_and_revalidated": 78,
        "audited": 388,
        "accumulated": 1017,
        "remaining": 1000,
        "candidate_sha256": final["candidate"]["corpus_sha256"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
