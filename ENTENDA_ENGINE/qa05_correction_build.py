"""Build the isolated QA-05 candidate with 50 independently revalidated corrections."""
import json
from collections import Counter

import entenda_engine as E
import qa05_prepare as prep


EDITORIAL = prep.OUT / "QA05_EDITORIAL_CORRECTIONS_50.json"
REVALIDATION = prep.OUT / "QA05_REVALIDATION_50.json"
CROSS_AUDIT = prep.OUT / "QA05_CROSS_AUDIT_1101_1105.json"
CANDIDATE = prep.HERE / "derived/candidate_qa05_cc_001_2046"
CORPUS = CANDIDATE / "CC2002_QA05.entenda.jsonl"
INDEX = CANDIDATE / "candidate_index"
CONFIG = prep.HERE / "derived/candidate_cc_001_2046/CC13_ENTENDA_CONFIG.json"


def build():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")
    proposals = json.loads(EDITORIAL.read_text(encoding="utf-8"))["records"]
    review_doc = json.loads(REVALIDATION.read_text(encoding="utf-8"))
    reviews = {row["target_id"]: row for row in review_doc["records"]}
    if len(proposals) != 50 or len(reviews) != 50:
        raise RuntimeError("correction/revalidation cardinality mismatch")
    if any(reviews[row["target_id"]]["decision"] != "CONFIRMED_CORRECTED" for row in proposals):
        raise RuntimeError("a correction lacks independent confirmation")

    ctx = E.NormContext("CC2002", config_path=CONFIG)
    existing = E.load_corpus(prep.CORPUS)
    active = {row["target_id"]: row for row in existing if row["status"] == "ACTIVE"}
    drafts = {
        "schema_version": 1, "norma_id": "CC2002", "template_version": "ENTENDA-T1",
        "prompt_version": "QA05-FINAL-50-CORRECTIONS-INDEPENDENT-REVALIDATION-V1",
        "review_status": "PENDING_HUMAN_REVIEW",
        "authoring": {"method": "QA04_FINDING_CORRECTION_WITH_CROSS_AGENT_INDEPENDENT_REVALIDATION",
                      "mission": "QA-05", "generated_on": prep.AS_OF, "human_approval_claimed": False},
        "explanations": [{
            "target_id": item["target_id"],
            "role": active[item["target_id"]]["granularity"]["role"],
            "semantic_autonomy": active[item["target_id"]]["granularity"]["semantic_autonomy"],
            "editorial_reason": "Correção jurídica QA-05 de achado QA-04, revalidada por agente independente do editor.",
            "content": item["proposed_content"],
            "external_layer_notes": active[item["target_id"]]["external_layer_notes"],
            "review_status": "PENDING_HUMAN_REVIEW",
            "editorial_version": active[item["target_id"]]["editorial_version"] + 1,
        } for item in proposals],
    }
    records = E.stamp(drafts, ctx, existing=existing)
    proposal_by_target = {row["target_id"]: row for row in proposals}
    for row in records:
        target = row["target_id"]
        if row["status"] == "ACTIVE" and target in proposal_by_target:
            proposal = proposal_by_target[target]
            review = reviews[target]
            row["qa05_correction"] = {
                "source_inventory": "QA05_CORRECTION_INVENTORY_50.json",
                "severity": proposal["severity"],
                "source_finding_sha256": proposal["source_finding_sha256"],
                "changed_fields": proposal["changed_fields"],
                "editorial_proposal_sha256": prep.json_sha(proposal["proposed_content"]),
                "independent_revalidation_decision": review["decision"],
                "independent_revalidation_sha256": prep.json_sha(review),
                "human_approval_claimed": False,
            }
    E.validate_corpus(records, ctx)
    E.write_corpus(records, CORPUS, ctx)
    index_manifest = E.build_entenda_index(ctx, records, INDEX)

    new_active = [row for row in records if row["status"] == "ACTIVE" and row["target_id"] in proposal_by_target]
    by_id = {row["explanation_id"]: row for row in records}
    if len(records) != 2312 or len(new_active) != 50 or sum(row["status"] == "ACTIVE" for row in records) != 2017:
        raise RuntimeError("candidate cardinality mismatch")
    for row in new_active:
        old = active[row["target_id"]]
        retired = by_id[old["explanation_id"]]
        if row["editorial_version"] != old["editorial_version"] + 1:
            raise RuntimeError(f"version did not advance: {row['target_id']}")
        if retired["content"] != old["content"] or retired["source"] != old["source"]:
            raise RuntimeError(f"historical version changed: {row['target_id']}")
        if retired["superseded_by"] != row["explanation_id"]:
            raise RuntimeError(f"supersession mismatch: {row['target_id']}")

    resolution = {
        "schema_version": 1, "mission": "QA-05", "as_of": prep.AS_OF,
        "status": "KNOWN_FINDINGS_RESOLVED", "known_findings_resolved": True,
        "full_corpus_legally_approved": False,
        "total": 50, "confirmed": 50, "corrected": 50, "revalidated": 50, "pending": 0,
        "severity_counts": dict(sorted(Counter(row["severity"] for row in proposals).items())),
        "critical_status": {target: "CORRIGIDO_E_REVALIDADO" for target in ("CC2002:ART.1102", "CC2002:ART.1103")},
        "records": [{"target_id": item["target_id"], "severity": item["severity"],
                     "old_explanation_id": item["baseline_explanation_id"],
                     "new_explanation_id": next(row["explanation_id"] for row in new_active if row["target_id"] == item["target_id"]),
                     "changed_fields": item["changed_fields"], "independent_decision": reviews[item["target_id"]]["decision"],
                     "status": "CORRIGIDO_E_REVALIDADO", "pending": []} for item in proposals],
    }
    prep.write_json(prep.OUT / "QA05_CORRECTION_RESOLUTION_50.json", resolution)
    cross = json.loads(CROSS_AUDIT.read_text(encoding="utf-8"))
    new_findings = cross.get("new_findings", [])
    prep.write_json(prep.OUT / "QA05_NEW_FINDINGS_CROSS_AUDIT.json", {
        "schema_version": 1, "mission": "QA-05", "as_of": prep.AS_OF,
        "status": "NEW_FINDINGS_OUTSIDE_ORIGINAL_CORRECTION_SCOPE", "total": len(new_findings),
        "findings": new_findings,
    })
    manifest = {
        "schema_version": 1, "mission": "QA-05", "checkpoint": "CP12", "as_of": prep.AS_OF,
        "status": "CANDIDATE_COMPLETE", "candidate_only": True, "deployed": False,
        "production_index_modified": False,
        "baseline": "derived/candidate_qa04_cc_001_2046/CC2002_QA04.entenda.jsonl",
        "baseline_sha256": prep.PROTECTED["qa04_corpus"], "records": 2312,
        "active": 2017, "historical": 295, "versioned_targets": 50,
        "corpus_sha256": prep.sha256(CORPUS), "candidate_index": index_manifest,
        "correction_resolution_sha256": prep.sha256(prep.OUT / "QA05_CORRECTION_RESOLUTION_50.json"),
        "new_findings_outside_scope": len(new_findings),
    }
    prep.write_json(CANDIDATE / "QA05_CANDIDATE_MANIFEST.json", manifest)
    prep.write_json(prep.OUT / "QA05_CHECKPOINT_12.json", {
        "schema_version": 1, "mission": "QA-05", "checkpoint": "CP12", "as_of": prep.AS_OF,
        "status": "COMPLETE", "manifest": "QA05_CANDIDATE_MANIFEST.json",
        "manifest_sha256": prep.sha256(CANDIDATE / "QA05_CANDIDATE_MANIFEST.json"),
        "corpus_sha256": manifest["corpus_sha256"],
        "lookup_sha256": prep.sha256(INDEX / "ENTENDA_LOOKUP.IDX"),
        "payload_sha256": prep.sha256(INDEX / "ENTENDA_PAYLOAD.DAT"),
        "production_index_modified": False, "deployed": False,
    })
    print(json.dumps({"corrected": 50, "revalidated": 50, "records": 2312,
                      "active": 2017, "historical": 295,
                      "corpus_sha256": manifest["corpus_sha256"],
                      "new_findings_outside_scope": len(new_findings)}, ensure_ascii=False))
    return manifest


if __name__ == "__main__":
    build()
