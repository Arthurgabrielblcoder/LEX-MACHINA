"""Build the isolated QA-06 candidate after final independent revalidation."""
import json
from pathlib import Path

import entenda_engine as E
import qa06_prepare as prep


PROPOSAL = prep.OUT / "QA06_A_EDITORIAL_PROPOSAL_1104_V2.json"
REVALIDATION = prep.OUT / "QA06_A_INDEPENDENT_REVALIDATION_1104_V2.json"
CANDIDATE = prep.HERE / "derived/candidate_qa06_cc_001_2046"
CORPUS = CANDIDATE / "CC2002_QA06.entenda.jsonl"
INDEX = CANDIDATE / "candidate_index"
CONFIG = prep.HERE / "derived/candidate_cc_001_2046/CC13_ENTENDA_CONFIG.json"
TARGET = "CC2002:ART.1104"


def build():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected QA-05 and historical baseline hash mismatch")
    proposal_doc = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    review_doc = json.loads(REVALIDATION.read_text(encoding="utf-8"))
    if proposal_doc["total"] != 1 or review_doc["total"] != 1:
        raise RuntimeError("unexpected Front A cardinality")
    proposal = proposal_doc["records"][0]
    review = review_doc["records"][0]
    if proposal["target_id"] != TARGET or review["target_id"] != TARGET:
        raise RuntimeError("Front A scope mismatch")
    if review["decision"] != "CONFIRMED_CORRECTED" or review.get("objections"):
        raise RuntimeError("art. 1.104 lacks objection-free independent confirmation")
    if review.get("proposal_sha256") != prep.sha256(PROPOSAL):
        raise RuntimeError("revalidation is not bound to proposal V2")

    ctx = E.NormContext("CC2002", config_path=CONFIG)
    existing = E.load_corpus(prep.CORPUS)
    active = {row["target_id"]: row for row in existing if row["status"] == "ACTIVE"}
    old = active[TARGET]
    drafts = {
        "schema_version": 1, "norma_id": "CC2002", "template_version": "ENTENDA-T1",
        "prompt_version": "QA06-ART1104-CORRECTION-INDEPENDENT-REVALIDATION-V2",
        "review_status": "PENDING_HUMAN_REVIEW",
        "authoring": {
            "method": "QA05_FINDING_CORRECTION_WITH_OBJECTION_AND_FINAL_INDEPENDENT_REVALIDATION",
            "mission": "QA-06", "generated_on": prep.AS_OF, "human_approval_claimed": False,
        },
        "explanations": [{
            "target_id": TARGET,
            "role": old["granularity"]["role"],
            "semantic_autonomy": old["granularity"]["semantic_autonomy"],
            "editorial_reason": (
                "Correção jurídica QA-06 do achado alto QA-05; proposta V2 ajustada após objeção "
                "e confirmada por revalidador independente contra os arts. 1.102 a 1.105."
            ),
            "content": proposal["proposed_content"],
            "external_layer_notes": old["external_layer_notes"],
            "review_status": "PENDING_HUMAN_REVIEW",
            "editorial_version": old["editorial_version"] + 1,
        }],
    }
    records = E.stamp(drafts, ctx, existing=existing)
    for row in records:
        if row["status"] == "ACTIVE" and row["target_id"] == TARGET:
            row["qa06_correction"] = {
                "source_finding": "QA05_NEW_FINDINGS_CROSS_AUDIT.json",
                "source_finding_sha256": proposal["source_finding_sha256"],
                "severity": proposal["severity"],
                "changed_fields": proposal["changed_fields"],
                "editorial_proposal_file": PROPOSAL.name,
                "editorial_proposal_sha256": prep.sha256(PROPOSAL),
                "initial_objection_code": "UNSTATED_LIMITER_NO_QUE_COUBER",
                "initial_objection_resolved": True,
                "independent_revalidation_file": REVALIDATION.name,
                "independent_revalidation_decision": review["decision"],
                "independent_revalidation_sha256": prep.sha256(REVALIDATION),
                "human_approval_claimed": False,
            }
    E.validate_corpus(records, ctx)
    E.write_corpus(records, CORPUS, ctx)
    index_manifest = E.build_entenda_index(ctx, records, INDEX)

    new = next(row for row in records if row["status"] == "ACTIVE" and row["target_id"] == TARGET)
    by_id = {row["explanation_id"]: row for row in records}
    retired = by_id[old["explanation_id"]]
    if (len(records), sum(row["status"] == "ACTIVE" for row in records),
            sum(row["status"] != "ACTIVE" for row in records)) != (2313, 2017, 296):
        raise RuntimeError("QA-06 candidate cardinality mismatch")
    if new["editorial_version"] != 3 or new["explanation_id"] != "ENTENDA/CC2002:ART.1104/BASE/3":
        raise RuntimeError("art. 1.104 version did not advance exactly once")
    if retired["content"] != old["content"] or retired["source"] != old["source"]:
        raise RuntimeError("QA-05 art. 1.104 historical version changed")
    if retired["superseded_by"] != new["explanation_id"]:
        raise RuntimeError("art. 1.104 supersession mismatch")

    resolution = {
        "schema_version": 1, "mission": "QA-06-FRONT-A", "as_of": prep.AS_OF,
        "status": "ART_1104_CORRECTED_AND_INDEPENDENTLY_REVALIDATED",
        "target_id": TARGET, "severity": "ALTO", "corrected": 1, "revalidated": 1, "pending": 0,
        "old_explanation_id": old["explanation_id"], "new_explanation_id": new["explanation_id"],
        "changed_fields": proposal["changed_fields"], "decision": review["decision"],
        "initial_objection_resolved": "UNSTATED_LIMITER_NO_QUE_COUBER",
        "human_approval_claimed": False,
    }
    resolution_path = prep.OUT / "QA06_A_CORRECTION_RESOLUTION_1104.json"
    prep.write_json(resolution_path, resolution)
    manifest = {
        "schema_version": 1, "mission": "QA-06-FRONT-A", "checkpoint": "A-CP03",
        "as_of": prep.AS_OF, "status": "CANDIDATE_COMPLETE", "candidate_only": True,
        "deployed": False, "production_index_modified": False,
        "baseline": str(prep.CORPUS.relative_to(prep.HERE)).replace("\\", "/"),
        "baseline_sha256": prep.PROTECTED["qa05_corpus"],
        "records": 2313, "active": 2017, "historical": 296, "versioned_targets": 1,
        "corpus_sha256": prep.sha256(CORPUS), "candidate_index": index_manifest,
        "correction_resolution_sha256": prep.sha256(resolution_path),
    }
    manifest_path = CANDIDATE / "QA06_CANDIDATE_MANIFEST.json"
    prep.write_json(manifest_path, manifest)
    prep.write_json(prep.OUT / "QA06_A_CP02.json", {
        "schema_version": 1, "mission": "QA-06-FRONT-A", "checkpoint": "A-CP02",
        "as_of": prep.AS_OF, "status": "INDEPENDENT_REVALIDATION_COMPLETE",
        "proposal_sha256": prep.sha256(PROPOSAL), "revalidation_sha256": prep.sha256(REVALIDATION),
        "decision": review["decision"], "initial_objection_resolved": True,
        "human_approval_claimed": False,
    })
    prep.write_json(prep.OUT / "QA06_A_CP03.json", {
        "schema_version": 1, "mission": "QA-06-FRONT-A", "checkpoint": "A-CP03",
        "as_of": prep.AS_OF, "status": "CANDIDATE_COMPLETE",
        "manifest_sha256": prep.sha256(manifest_path), "corpus_sha256": prep.sha256(CORPUS),
        "lookup_sha256": prep.sha256(INDEX / "ENTENDA_LOOKUP.IDX"),
        "payload_sha256": prep.sha256(INDEX / "ENTENDA_PAYLOAD.DAT"),
        "production_index_modified": False, "deployed": False,
    })
    print(json.dumps({"corrected": 1, "revalidated": 1, "records": 2313,
                      "active": 2017, "historical": 296,
                      "corpus_sha256": prep.sha256(CORPUS)}, ensure_ascii=False))
    return manifest


if __name__ == "__main__":
    build()
