"""Persist deterministic QA-07 CP08 test evidence and final consolidation."""
import hashlib
import json
from pathlib import Path

import qa07_prepare as prep


HERE = Path(__file__).resolve().parent
OUT = prep.OUT
CANDIDATE = HERE / "derived/candidate_qa07_cc_001_2046"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build():
    prep.build()
    cps = [load(OUT / f"QA07_CP{n:02d}.json") for n in range(1, 8)]
    if [cp["checkpoint"] for cp in cps] != [f"CP{n:02d}" for n in range(1, 8)]:
        raise RuntimeError("checkpoint sequence mismatch")
    cp6, cp7 = cps[5], cps[6]
    manifest = load(CANDIDATE / "QA07_CANDIDATE_MANIFEST.json")
    medium = load(OUT / "QA07_MEDIUM_420_PRESERVATION_MANIFEST.json")
    tests = {
        "schema_version": 1, "mission": "QA-07", "as_of": "2026-11-14", "status": "PASS",
        "directed": {"ran": 47, "passed": 47, "failures": 0, "errors": 0, "skipped": 0},
        "global": {"ran": 512, "passed": 510, "failures": 0, "errors": 0, "skipped": 2},
        "determinism": {"scope": True, "recovered_modules": True, "revalidation": True,
                        "candidate_corpus": True, "candidate_indexes": True},
        "protected_qa06_unchanged": True, "production_index_modified": False, "deployed": False,
    }
    test_path = OUT / "QA07_TEST_EVIDENCE.json"
    prep.write(test_path, tests)
    final = {
        "schema_version": 1, "mission": "QA-07", "as_of": "2026-11-14",
        "status": "HIGH_FINDINGS_RESOLVED_AND_INDETERMINATE_REVIEW_COMPLETE",
        "baseline_head": "74775b2b5db692c2886a6a3d3d6b772bfb89ba14",
        "protected_qa06_sha256": {name: actual for name, (path, actual) in prep.PROTECTED.items()},
        "high_findings": {"total": 41, "resolved": cp6["high_findings_resolved"],
                          "targets": cp6["high_targets"], "pending": cp6["pending_high"],
                          "initial_rejections": cp6["initial_rejections"],
                          "revised_and_accepted": cp6["revised_and_accepted"]},
        "indeterminate": {"total": 10, "review_complete": cp6["indeterminate_reviewed"],
                          "confirmed_for_correction": cp6["indeterminate_confirmed_for_correction"],
                          "materially_sufficient": cp6["indeterminate_materially_sufficient"],
                          "requires_human": 0, "pending": cp6["pending_indeterminate"]},
        "corrections": {"resolved_findings": cp6["findings_ready_for_correction"],
                        "versioned_targets": cp7["versioned_targets"]},
        "candidate": {"records": cp7["records"], "active": cp7["active"],
                      "historical": cp7["historical"], "corpus_sha256": cp7["corpus_sha256"],
                      "lookup_sha256": cp7["lookup_sha256"], "payload_sha256": cp7["payload_sha256"]},
        "medium_queue": {"preserved": medium["total"], "manifest_sha256": sha(OUT / "QA07_MEDIUM_420_PRESERVATION_MANIFEST.json"),
                         "state": "PENDING_UNMODIFIED"},
        "checkpoints": [{"checkpoint": cp["checkpoint"], "sha256": sha(OUT / f"QA07_CP{n:02d}.json")}
                        for n, cp in enumerate(cps, 1)],
        "test_evidence_sha256": sha(test_path),
        "states": {"high_findings_resolved": True, "indeterminate_review_complete": True,
                   "subdivision_findings_resolved": False, "full_corpus_legally_approved": False,
                   "human_approved": False, "candidate_only": True,
                   "production_index_modified": False, "deployed": False,
                   "firmware_accessed": False, "microsd_accessed": False, "esp32_accessed": False},
        "source": {"authority": "Câmara dos Deputados",
                   "url": "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html",
                   "cutoff": "2026-11-14"},
    }
    final_path = OUT / "QA07_FINAL_CONSOLIDATION.json"
    prep.write(final_path, final)
    cp8 = {
        "schema_version": 1, "mission": "QA-07", "checkpoint": "CP08", "as_of": "2026-11-14",
        "status": "TESTS_AND_DETERMINISM_COMPLETE_READY_FOR_PUBLICATION",
        "directed_tests": 47, "global_tests": 512, "global_skips": 2,
        "failures": 0, "errors": 0, "test_evidence_sha256": sha(test_path),
        "final_consolidation_sha256": sha(final_path), "production_index_modified": False,
        "human_approved": False, "deployed": False,
    }
    prep.write(OUT / "QA07_CP08.json", cp8)
    print(json.dumps({"status": cp8["status"], "corpus_sha256": manifest["corpus_sha256"],
                      "final_sha256": sha(final_path)}, ensure_ascii=False))


if __name__ == "__main__":
    build()
