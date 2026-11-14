"""Build the authoritative QA-06 final consolidation from persisted evidence."""
import hashlib
import json
from pathlib import Path

import qa06_prepare as prep


HERE = Path(__file__).resolve().parent
OUT = HERE / "derived/qa06_subdivision_material_audit"
CANDIDATE = HERE / "derived/candidate_qa06_cc_001_2046"
FINAL = OUT / "QA06_FINAL_CONSOLIDATION.json"
TEST_EVIDENCE = OUT / "QA06_TEST_EVIDENCE.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def artifact(name):
    path = OUT / name
    return {"file": name, "sha256": sha(path)}


def build():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected QA-05 baseline hash mismatch")
    inventory = load(OUT / "QA06_SUBDIVISION_INVENTORY_V2_CORRECTED.json")
    material = load(OUT / "QA06_B_MATERIAL_AUDIT_CONSOLIDATION.json")
    findings = load(OUT / "QA06_B_FINDINGS_FINAL_CONSOLIDATION.json")
    candidate = load(CANDIDATE / "QA06_CANDIDATE_MANIFEST.json")
    checkpoints = []
    for number in range(1, 42):
        name = f"QA06_B_CHECKPOINT_{number:02d}.json"
        doc = load(OUT / name)
        checkpoints.append({"checkpoint": doc["checkpoint"], "file": name,
                            "sha256": sha(OUT / name), "targets": doc["target_total"]})
    if sum(item["targets"] for item in checkpoints) != 2017:
        raise RuntimeError("checkpoint target coverage mismatch")
    tests = load(TEST_EVIDENCE) if TEST_EVIDENCE.exists() else {
        "status": "PENDING_FINAL_EXECUTION", "directed": None, "global": None
    }
    final = {
        "schema_version": 1,
        "mission": "QA-06",
        "as_of": prep.AS_OF,
        "status": "AUDIT_COMPLETE_WITH_DEFINITIVE_CORRECTION_QUEUE",
        "authorized_inventory": {
            "targets": inventory["active_targets"],
            "subdivisions": inventory["subdivisions_total"],
            "auditable": inventory["subdivisions_auditable"],
            "excluded": inventory["subdivision_status_counts"]["EXCLUDED_REVOKED_OR_VETOED"],
            "sha256": sha(OUT / "QA06_SUBDIVISION_INVENTORY_V2_CORRECTED.json"),
        },
        "front_a": {
            "corrected_and_independently_revalidated": 1,
            "target_id": "CC2002:ART.1104",
            "records": candidate["records"], "active": candidate["active"],
            "historical": candidate["historical"],
            "corpus_sha256": candidate["corpus_sha256"],
            "lookup_sha256": candidate["candidate_index"]["ENTENDA_LOOKUP.IDX"]["sha256"],
            "payload_sha256": candidate["candidate_index"]["ENTENDA_PAYLOAD.DAT"]["sha256"],
        },
        "front_b": {
            "classification_counts": material["classification_counts"],
            "coverage_by_book": material["coverage_by_book"],
            "initial_findings": findings["initial_findings"],
            "review_decision_counts": findings["review_decision_counts"],
            "final_disposition_counts": findings["final_disposition_counts"],
            "pending_severity_counts": findings["pending_severity_counts"],
            "definitive_correction_queue": artifact("QA06_B_DEFINITIVE_CORRECTION_QUEUE.json"),
            "indeterminate_review_queue": artifact("QA06_B_INDETERMINATE_REVIEW_QUEUE.json"),
            "rejected_findings_evidence": artifact("QA06_B_REJECTED_FINDINGS_EVIDENCE.json"),
        },
        "checkpoints": checkpoints,
        "protected_baseline_sha256": prep.PROTECTED,
        "tests": tests,
        "states": {
            "subdivision_audit_complete": True,
            "subdivision_findings_resolved": False,
            "full_corpus_legally_approved": False,
            "human_approved": False,
            "candidate_only": True,
            "production_index_modified": False,
            "deployed": False,
            "firmware_accessed": False,
            "microsd_accessed": False,
            "esp32_accessed": False,
        },
    }
    prep.write_json(FINAL, final)
    print(json.dumps({"file": FINAL.name, "sha256": sha(FINAL),
                      "pending_corrections": findings["final_disposition_counts"]["PENDENTE_CORRECAO"]},
                     ensure_ascii=False))
    return final


if __name__ == "__main__":
    build()
