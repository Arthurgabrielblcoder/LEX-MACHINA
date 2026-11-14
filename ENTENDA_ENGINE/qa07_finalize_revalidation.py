"""Close CP06 while preserving the full proposal/rejection/revision chain."""
import hashlib
import json

import qa07_prepare as prep


OUT = prep.OUT


def sha(name):
    return hashlib.sha256((OUT / name).read_bytes()).hexdigest()


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def build():
    draft = load("QA07_ACCEPTED_CONTENT_DRAFT.json")
    content_review = load("QA07_REVIEW_ACCEPTED_CONTENT.json")
    micro = load("QA07_EDITOR_MICROREVISION_1541.json")
    micro_review = load("QA07_REVIEW_MICROREVISION_1541.json")
    if content_review["draft_sha256"] != sha("QA07_ACCEPTED_CONTENT_DRAFT.json"):
        raise RuntimeError("accepted draft review mismatch")
    if not content_review["all_integrated_targets_accepted"]:
        raise RuntimeError("integrated overlap review not accepted")
    if micro["accepted_content_sha256"] != sha("QA07_ACCEPTED_CONTENT_DRAFT.json"):
        raise RuntimeError("microrevision base mismatch")
    if micro_review["proposal_sha256"] != sha("QA07_EDITOR_MICROREVISION_1541.json"):
        raise RuntimeError("microrevision review mismatch")
    if micro_review["records"][0]["decision"] != "ACEITA":
        raise RuntimeError("microrevision rejected")
    records = json.loads(json.dumps(draft["records"], ensure_ascii=False))
    art1541 = next(r for r in records if r["target_id"] == "CC2002:ART.1541")
    art1541["proposed_content"] = micro["records"][0]["proposed_content"]
    art1541["origins"].append("MICROREVISION_1541_ACCEPTED")
    art1541["integration_kind"] = "DIRECT_ACCEPTED_PROPOSAL_WITH_ACCEPTED_TECHNICAL_MICROREVISION"
    final = {
        "schema_version": 1, "mission": "QA-07", "as_of": prep.AS_OF,
        "status": "INDEPENDENTLY_REVALIDATED_CONTENT_READY_FOR_CANDIDATE",
        "target_total": 31, "resolved_finding_total": 49,
        "high_findings_resolved": 41, "indeterminate_review_complete": 10,
        "indeterminate_confirmed_for_correction": 8,
        "indeterminate_materially_sufficient": 2,
        "source_draft_sha256": sha("QA07_ACCEPTED_CONTENT_DRAFT.json"),
        "review_chain_sha256": {
            "accepted_content_review": sha("QA07_REVIEW_ACCEPTED_CONTENT.json"),
            "microrevision_1541": sha("QA07_EDITOR_MICROREVISION_1541.json"),
            "microrevision_1541_review": sha("QA07_REVIEW_MICROREVISION_1541.json"),
        },
        "records": records, "corpus_modified": False, "human_approval_claimed": False,
    }
    final_path = OUT / "QA07_ACCEPTED_CONTENT_FINAL.json"
    prep.write(final_path, final)
    chain = {
        "high_a_review": sha("QA07_REVIEW_HIGH_A.json"),
        "high_b_negative_review": sha("QA07_REVIEW_HIGH_B.json"),
        "high_b_revision_2": sha("QA07_EDITOR_HIGH_B_REVISION_2.json"),
        "high_b_revision_2_review": sha("QA07_REVIEW_HIGH_B_REVISION_2.json"),
        "indeterminate_review": sha("QA07_REVIEW_INDETERMINATE.json"),
        "accepted_content_review": sha("QA07_REVIEW_ACCEPTED_CONTENT.json"),
        "microrevision_1541": sha("QA07_EDITOR_MICROREVISION_1541.json"),
        "microrevision_1541_review": sha("QA07_REVIEW_MICROREVISION_1541.json"),
    }
    prep.write(OUT / "QA07_CP06.json", {
        "schema_version": 1, "mission": "QA-07", "checkpoint": "CP06", "as_of": prep.AS_OF,
        "status": "INDEPENDENT_REVALIDATION_COMPLETE", "high_findings_resolved": 41,
        "high_targets": 25, "initial_rejections": 2, "revised_and_accepted": 2,
        "indeterminate_reviewed": 10, "indeterminate_confirmed_for_correction": 8,
        "indeterminate_materially_sufficient": 2, "targets_ready_for_versioning": 31,
        "findings_ready_for_correction": 49, "review_chain_sha256": chain,
        "accepted_content_final_sha256": hashlib.sha256(final_path.read_bytes()).hexdigest(),
        "pending_high": 0, "pending_indeterminate": 0, "human_approval_claimed": False,
    })
    print(json.dumps({"high_resolved": 41, "indeterminate_reviewed": 10,
                      "targets": 31, "final_sha256": hashlib.sha256(final_path.read_bytes()).hexdigest()},
                     ensure_ascii=False))


if __name__ == "__main__":
    build()
