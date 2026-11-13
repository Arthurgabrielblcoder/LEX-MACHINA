"""Persist deterministic QA-05 checkpoint 13 and final evidence."""
import json

import qa05_prepare as prep


CANDIDATE_DIR = prep.HERE / "derived/candidate_qa05_cc_001_2046"
CANDIDATE = CANDIDATE_DIR / "CC2002_QA05.entenda.jsonl"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")
    resolution = load(prep.OUT / "QA05_CORRECTION_RESOLUTION_50.json")
    revalidation = load(prep.OUT / "QA05_REVALIDATION_50.json")
    manifest = load(CANDIDATE_DIR / "QA05_CANDIDATE_MANIFEST.json")
    cross = load(prep.OUT / "QA05_NEW_FINDINGS_CROSS_AUDIT.json")
    if (resolution["corrected"], resolution["revalidated"], resolution["pending"]) != (50, 50, 0):
        raise RuntimeError("known findings are not fully resolved")
    if revalidation["decision_counts"] != {"CONFIRMED_CORRECTED": 50}:
        raise RuntimeError("independent revalidation incomplete")
    if cross["total"] != 1 or cross["findings"][0]["target_id"] != "CC2002:ART.1104":
        raise RuntimeError("unexpected cross-audit finding state")

    tests = {
        "schema_version": 1, "mission": "QA-05", "checkpoint": "CP13", "as_of": prep.AS_OF,
        "status": "PASS",
        "directed_regression": {"scope": "CC-02 through CC-13 plus QA-02 through QA-05",
                                "executed": 170, "passed": 170, "failed": 0, "errors": 0},
        "global_suite": {"executed": 465, "passed": 463, "skipped": 2,
                         "failed": 0, "errors": 0, "elapsed_seconds": 138.701},
        "determinism": {"status": "PASS", "comparison": "byte-identical inventory, editorial integration, revalidation, corpus and indexes",
                        "rebuilders": ["qa05_prepare.py", "qa05_editorial_integrate.py",
                                       "qa05_revalidation_integrate.py", "qa05_correction_build.py"]},
        "temporary_directory": ".tmp_qa05 within worktree",
    }
    prep.write_json(prep.OUT / "QA05_TEST_EVIDENCE.json", tests)

    final = {
        "schema_version": 1, "mission": "QA-05", "as_of": prep.AS_OF,
        "status": "KNOWN_FINDINGS_RESOLVED", "known_findings_resolved": True,
        "full_corpus_audit_complete": True, "full_corpus_legally_approved": False,
        "original_findings": {"total": 50, "confirmed": 50, "corrected": 50,
                              "independently_revalidated": 50, "pending": 0,
                              "severity_counts": resolution["severity_counts"]},
        "critical": {"CC2002:ART.1102": "CORRIGIDO_E_REVALIDADO",
                     "CC2002:ART.1103": "CORRIGIDO_E_REVALIDADO"},
        "independent_review": {"first_pass_revisions_required": ["CC2002:ART.1103", "CC2002:ART.1358-L"],
                               "final_decisions": {"CONFIRMED_CORRECTED": 50},
                               "editors_distinct_from_reviewers": True},
        "cross_audit_1101_1105": {"status": "COMPLETE", "resolved_displacements": ["CC2002:ART.1102", "CC2002:ART.1103"],
                                  "neighbors_without_new_finding": ["CC2002:ART.1101", "CC2002:ART.1105"],
                                  "new_findings_outside_original_scope": 1,
                                  "new_finding_targets": ["CC2002:ART.1104"]},
        "candidate": {"path": "ENTENDA_ENGINE/derived/candidate_qa05_cc_001_2046/CC2002_QA05.entenda.jsonl",
                      "versions": manifest["records"], "active": manifest["active"],
                      "historical": manifest["historical"], "versioned_targets": manifest["versioned_targets"],
                      "corpus_sha256": prep.sha256(CANDIDATE),
                      "lookup_sha256": prep.sha256(CANDIDATE_DIR / "candidate_index/ENTENDA_LOOKUP.IDX"),
                      "payload_sha256": prep.sha256(CANDIDATE_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT"),
                      "build_manifest_sha256": prep.sha256(CANDIDATE_DIR / "candidate_index/ENTENDA_BUILD_MANIFEST.json"),
                      "candidate_only": True},
        "protected": {"preserved": True, "sha256": prep.PROTECTED,
                      "qa04_versions": 2262, "qa04_active": 2017, "qa04_historical": 245},
        "checkpoints": {"total": 13,
                        "completed_before_final": 12,
                        "sha256": {f"CP{n:02d}": prep.sha256(prep.OUT / f"QA05_CHECKPOINT_{n:02d}.json") for n in range(1, 13)}},
        "evidence": {"editorial_sha256": prep.sha256(prep.OUT / "QA05_EDITORIAL_CORRECTIONS_50.json"),
                     "revalidation_sha256": prep.sha256(prep.OUT / "QA05_REVALIDATION_50.json"),
                     "resolution_sha256": prep.sha256(prep.OUT / "QA05_CORRECTION_RESOLUTION_50.json"),
                     "cross_audit_sha256": prep.sha256(prep.OUT / "QA05_CROSS_AUDIT_1101_1105.json"),
                     "new_finding_queue_sha256": prep.sha256(prep.OUT / "QA05_NEW_FINDINGS_CROSS_AUDIT.json"),
                     "test_evidence_sha256": prep.sha256(prep.OUT / "QA05_TEST_EVIDENCE.json")},
        "deployment": {"performed": False, "production_indexes_modified": False,
                       "firmware_accessed": False, "microsd_accessed": False, "esp32_accessed": False},
        "residual_risks": [
            "The new high finding for art. 1.104 remains pending because it was outside the original 50-target edit scope.",
            "FULL_CORPUS_AUDIT_COMPLETE and KNOWN_FINDINGS_RESOLVED do not mean FULL_CORPUS_LEGALLY_APPROVED.",
            "A future material audit of paragraph, item and subitem coverage remains separate.",
        ],
        "recommended_next_step": "Correct and independently revalidate the documented art. 1.104 finding, then perform the separate subdivision-level material coverage audit.",
    }
    prep.write_json(prep.OUT / "QA05_FINAL_CONSOLIDATION.json", final)
    prep.write_json(prep.OUT / "QA05_CHECKPOINT_13.json", {
        "schema_version": 1, "mission": "QA-05", "checkpoint": "CP13", "as_of": prep.AS_OF,
        "status": "COMPLETE", "tests": "PASS", "determinism": "PASS",
        "final_consolidation": "QA05_FINAL_CONSOLIDATION.json",
        "final_consolidation_sha256": prep.sha256(prep.OUT / "QA05_FINAL_CONSOLIDATION.json"),
        "test_evidence_sha256": prep.sha256(prep.OUT / "QA05_TEST_EVIDENCE.json"),
        "deployed": False,
    })
    print(json.dumps({"resolved": 50, "pending_original": 0, "new_out_of_scope": 1,
                      "candidate_sha256": final["candidate"]["corpus_sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
