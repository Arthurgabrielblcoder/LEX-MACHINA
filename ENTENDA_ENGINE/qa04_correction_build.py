"""Build an isolated QA-04 candidate from four independently revalidated corrections."""
import json
from collections import Counter

import entenda_engine as E
import qa04_prepare as prep


EDITORIAL = prep.OUT / "QA04_EDITORIAL_CORRECTIONS_4.json"
REVALIDATION = prep.OUT / "QA04_EDITORIAL_REVALIDATION_4.json"
CANDIDATE = prep.HERE / "derived/candidate_qa04_cc_001_2046"
CORPUS = CANDIDATE / "CC2002_QA04.entenda.jsonl"
INDEX = CANDIDATE / "candidate_index"
CONFIG = prep.HERE / "derived/candidate_cc_001_2046/CC13_ENTENDA_CONFIG.json"
TARGETS = ("CC2002:ART.228", "CC2002:ART.288", "CC2002:ART.371", "CC2002:ART.500")


def build():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected QA-03/CC-13 hash mismatch")
    editorial_doc = json.loads(EDITORIAL.read_text(encoding="utf-8"))
    review_doc = json.loads(REVALIDATION.read_text(encoding="utf-8"))
    proposals = editorial_doc["records"]
    reviews = {row["target_id"]: row for row in review_doc["records"]}
    if tuple(row["target_id"] for row in proposals) != TARGETS or set(reviews) != set(TARGETS):
        raise RuntimeError("correction/revalidation scope mismatch")
    if any(reviews[target]["decision"] != "CONFIRMED_CORRECTED" for target in TARGETS):
        raise RuntimeError("one or more corrections lack independent confirmation")

    ctx = E.NormContext("CC2002", config_path=CONFIG)
    existing = E.load_corpus(prep.CORPUS)
    active = {row["target_id"]: row for row in existing if row["status"] == "ACTIVE"}
    drafts = {
        "schema_version": 1, "norma_id": "CC2002", "template_version": "ENTENDA-T1",
        "prompt_version": "QA04-FOUR-CORRECTIONS-INDEPENDENT-REVALIDATION-V1",
        "review_status": "PENDING_HUMAN_REVIEW",
        "authoring": {"method": "QA03_FINDING_CORRECTION_WITH_SEPARATE_INDEPENDENT_REVALIDATION",
                      "mission": "QA-04", "generated_on": prep.AS_OF, "human_approval_claimed": False},
        "explanations": [{
            "target_id": item["target_id"],
            "role": active[item["target_id"]]["granularity"]["role"],
            "semantic_autonomy": active[item["target_id"]]["granularity"]["semantic_autonomy"],
            "editorial_reason": "Correção jurídica QA-04 de achado QA-03, revalidada independentemente contra fonte oficial.",
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
            row["qa04_correction"] = {
                "source_inventory": "QA04_CORRECTION_INVENTORY_4.json",
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

    new_active = [row for row in records if row["status"] == "ACTIVE" and row["target_id"] in TARGETS]
    by_id = {row["explanation_id"]: row for row in records}
    if len(records) != 2262 or len(new_active) != 4 or sum(row["status"] == "ACTIVE" for row in records) != 2017:
        raise RuntimeError("candidate cardinality mismatch")
    for row in new_active:
        old = active[row["target_id"]]
        retired = by_id[old["explanation_id"]]
        if row["editorial_version"] != old["editorial_version"] + 1:
            raise RuntimeError(f"version did not advance: {row['target_id']}")
        if retired["content"] != old["content"] or retired["source"] != old["source"]:
            raise RuntimeError(f"historical content/source changed: {row['target_id']}")
        if retired["superseded_by"] != row["explanation_id"]:
            raise RuntimeError(f"supersession mismatch: {row['target_id']}")

    resolution = {
        "schema_version": 1, "mission": "QA-04-FRONT-A", "as_of": prep.AS_OF,
        "status": "FOUR_FINDINGS_CORRECTED_AND_INDEPENDENTLY_REVALIDATED",
        "total": 4, "corrected": 4, "revalidated": 4, "pending": 0,
        "severity_counts": dict(sorted(Counter(row["severity"] for row in proposals).items())),
        "records": [{
            "target_id": item["target_id"], "severity": item["severity"],
            "old_explanation_id": item["baseline_explanation_id"],
            "new_explanation_id": next(row["explanation_id"] for row in new_active if row["target_id"] == item["target_id"]),
            "changed_fields": item["changed_fields"], "decision": reviews[item["target_id"]]["decision"],
        } for item in proposals],
    }
    prep.write_json(prep.OUT / "QA04_CORRECTION_RESOLUTION_4.json", resolution)
    manifest = {
        "schema_version": 1, "mission": "QA-04-FRONT-A", "checkpoint": "A-CP03",
        "as_of": prep.AS_OF, "status": "CANDIDATE_COMPLETE", "candidate_only": True,
        "deployed": False, "production_index_modified": False,
        "baseline": "derived/candidate_qa03_cc_001_2046/CC2002_QA03.entenda.jsonl",
        "baseline_sha256": prep.PROTECTED["qa03_corpus"], "records": 2262,
        "active": 2017, "historical": 245, "versioned_targets": 4,
        "corpus_sha256": prep.sha256(CORPUS), "candidate_index": index_manifest,
        "correction_resolution_sha256": prep.sha256(prep.OUT / "QA04_CORRECTION_RESOLUTION_4.json"),
    }
    prep.write_json(CANDIDATE / "QA04_CANDIDATE_MANIFEST.json", manifest)
    checkpoints = {
        1: {"status": "EDITORIAL_COMPLETE", "source": EDITORIAL.name, "source_sha256": prep.sha256(EDITORIAL), "total": 4},
        2: {"status": "INDEPENDENT_REVALIDATION_COMPLETE", "source": REVALIDATION.name, "source_sha256": prep.sha256(REVALIDATION), "total": 4},
        3: {"status": "CANDIDATE_COMPLETE", "manifest": "QA04_CANDIDATE_MANIFEST.json",
            "manifest_sha256": prep.sha256(CANDIDATE / "QA04_CANDIDATE_MANIFEST.json"),
            "corpus_sha256": manifest["corpus_sha256"],
            "lookup_sha256": prep.sha256(INDEX / "ENTENDA_LOOKUP.IDX"),
            "payload_sha256": prep.sha256(INDEX / "ENTENDA_PAYLOAD.DAT")},
    }
    for number, data in checkpoints.items():
        prep.write_json(prep.OUT / f"QA04_A_CHECKPOINT_{number:02d}.json", {
            "schema_version": 1, "mission": "QA-04-FRONT-A", "checkpoint": f"A-CP{number:02d}",
            "as_of": prep.AS_OF, **data,
        })
    print(json.dumps({"corrected": 4, "records": 2262, "active": 2017, "historical": 245,
                      "corpus_sha256": manifest["corpus_sha256"]}, ensure_ascii=False))
    return manifest


if __name__ == "__main__":
    build()
