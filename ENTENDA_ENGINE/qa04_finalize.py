"""Persist deterministic QA-04 final evidence and correction queue."""
import json
from collections import Counter

import qa04_prepare as prep


CANDIDATE_DIR = prep.HERE / "derived/candidate_qa04_cc_001_2046"
CANDIDATE = CANDIDATE_DIR / "CC2002_QA04.entenda.jsonl"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")
    resolution = load(prep.OUT / "QA04_CORRECTION_RESOLUTION_4.json")
    audit = load(prep.OUT / "QA04_B_AUDIT_1000.json")
    summary = load(prep.OUT / "QA04_B_CONSOLIDATION.json")
    findings = load(prep.OUT / "QA04_B_NEW_FINDINGS.json")["findings"]
    manifest = load(CANDIDATE_DIR / "QA04_CANDIDATE_MANIFEST.json")
    if (resolution["corrected"], resolution["revalidated"], resolution["pending"]) != (4, 4, 0):
        raise RuntimeError("front A incomplete")
    if audit["audited_total"] != 1000 or len(audit["records"]) != 1000:
        raise RuntimeError("front B incomplete")
    if len(findings) != 50 or Counter(row["severity"] for row in findings) != Counter({"CRÍTICO": 2, "ALTO": 31, "MÉDIO": 17}):
        raise RuntimeError("unexpected finding queue")

    correction_queue = {
        "schema_version": 1, "mission": "QA-04", "as_of": prep.AS_OF,
        "status": "PENDING_EDITORIAL_CORRECTION_AND_INDEPENDENT_REVALIDATION",
        "source": "QA04_B_NEW_FINDINGS.json",
        "source_sha256": prep.sha256(prep.OUT / "QA04_B_NEW_FINDINGS.json"),
        "total": 50,
        "severity_counts": dict(sorted(Counter(row["severity"] for row in findings).items())),
        "critical_targets": [row["target_id"] for row in findings if row["severity"] == "CRÍTICO"],
        "findings": findings,
    }
    prep.write_json(prep.OUT / "QA04_CORRECTION_QUEUE_50.json", correction_queue)

    tests = {
        "schema_version": 1, "mission": "QA-04", "as_of": prep.AS_OF, "status": "PASS",
        "directed_regression": {"scope": "CC-02 through CC-13 plus QA-02 through QA-04",
                                "executed": 159, "passed": 159, "failed": 0, "errors": 0},
        "global_suite": {"executed": 454, "passed": 452, "skipped": 2,
                         "failed": 0, "errors": 0, "elapsed_seconds": 133.656},
        "determinism": {"status": "PASS", "comparison": "byte-identical queue, candidate, indexes, checkpoints and consolidation",
                        "rebuilders": ["qa04_prepare.py", "qa04_editorial_prepare.py",
                                       "qa04_correction_build.py", "qa04_audit_build.py --through-checkpoint 20"]},
        "temporary_directory": ".tmp_qa04 within worktree",
    }
    prep.write_json(prep.OUT / "QA04_TEST_EVIDENCE.json", tests)

    final = {
        "schema_version": 1, "mission": "QA-04", "as_of": prep.AS_OF,
        "status": "FULL_CORPUS_AUDIT_COMPLETE", "full_corpus_audit_complete": True,
        "full_corpus_legally_approved": False,
        "front_a": {"source_findings": 4, "confirmed": 4, "corrected": 4,
                    "independently_revalidated": 4, "pending": 0,
                    "severity_counts": resolution["severity_counts"],
                    "targets": [row["target_id"] for row in resolution["records"]],
                    "formal_review_status": "PENDING_HUMAN_REVIEW", "human_approval_claimed": False},
        "front_b": {"new_unique_audits": 1000, "prior_unique_audits": 1017,
                    "unique_audits_accumulated": 2017, "still_unaudited": 0,
                    "coverage_by_book": summary["coverage"]["by_book_qa04"],
                    "new_findings": 50,
                    "new_findings_by_severity": correction_queue["severity_counts"],
                    "critical_targets": correction_queue["critical_targets"]},
        "candidate": {"path": "ENTENDA_ENGINE/derived/candidate_qa04_cc_001_2046/CC2002_QA04.entenda.jsonl",
                      "versions": 2262, "active": 2017, "historical": 245, "versioned_targets": 4,
                      "corpus_sha256": prep.sha256(CANDIDATE),
                      "lookup_sha256": prep.sha256(CANDIDATE_DIR / "candidate_index/ENTENDA_LOOKUP.IDX"),
                      "payload_sha256": prep.sha256(CANDIDATE_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT"),
                      "build_manifest_sha256": prep.sha256(CANDIDATE_DIR / "candidate_index/ENTENDA_BUILD_MANIFEST.json"),
                      "candidate_only": True},
        "protected": {"preserved": True, "sha256": prep.PROTECTED,
                      "qa03_versions": 2258, "qa03_active": 2017, "qa03_historical": 241},
        "checkpoints": {"front_a_total": 3,
                        "front_a_sha256": {f"A-CP{n:02d}": prep.sha256(prep.OUT / f"QA04_A_CHECKPOINT_{n:02d}.json") for n in range(1, 4)},
                        "front_b_total": 20,
                        "front_b_sha256": {f"B-CP{n:02d}": prep.sha256(prep.OUT / f"QA04_B_CHECKPOINT_{n:02d}.json") for n in range(1, 21)}},
        "evidence": {"audit_1000_sha256": prep.sha256(prep.OUT / "QA04_B_AUDIT_1000.json"),
                     "new_findings_sha256": prep.sha256(prep.OUT / "QA04_B_NEW_FINDINGS.json"),
                     "correction_queue_sha256": prep.sha256(prep.OUT / "QA04_CORRECTION_QUEUE_50.json"),
                     "test_evidence_sha256": prep.sha256(prep.OUT / "QA04_TEST_EVIDENCE.json")},
        "deployment": {"performed": False, "production_indexes_modified": False,
                       "firmware_accessed": False, "microsd_accessed": False, "esp32_accessed": False},
        "limitations": [
            "FULL_CORPUS_AUDIT_COMPLETE does not mean FULL_CORPUS_LEGALLY_APPROVED.",
            "Fifty findings remain pending correction and human review, including two critical findings.",
            "Article-level audit does not replace a future subdivision-specific coverage audit.",
        ],
        "recommended_next_mission": "Correct and independently revalidate QA04_CORRECTION_QUEUE_50.json, prioritizing arts. 1.102 and 1.103.",
    }
    prep.write_json(prep.OUT / "QA04_FINAL_CONSOLIDATION.json", final)
    print(json.dumps({"audited": 1000, "accumulated": 2017, "unaudited": 0,
                      "findings": 50, "candidate_sha256": final["candidate"]["corpus_sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
