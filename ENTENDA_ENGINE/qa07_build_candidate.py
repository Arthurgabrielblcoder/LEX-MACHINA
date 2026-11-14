"""Build the isolated QA-07 candidate from independently accepted content."""
import hashlib
import json
from pathlib import Path

import entenda_engine as E
import qa07_prepare as prep


HERE = Path(__file__).resolve().parent
OUT = prep.OUT
BASELINE = HERE / "derived/candidate_qa06_cc_001_2046/CC2002_QA06.entenda.jsonl"
CANDIDATE = HERE / "derived/candidate_qa07_cc_001_2046"
CORPUS = CANDIDATE / "CC2002_QA07.entenda.jsonl"
INDEX = CANDIDATE / "candidate_index"
CONFIG = HERE / "derived/candidate_cc_001_2046/CC13_ENTENDA_CONFIG.json"
ACCEPTED = OUT / "QA07_ACCEPTED_CONTENT_FINAL.json"
CP06 = OUT / "QA07_CP06.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build():
    prep.build()
    accepted, cp06 = load(ACCEPTED), load(CP06)
    if accepted["status"] != "INDEPENDENTLY_REVALIDATED_CONTENT_READY_FOR_CANDIDATE":
        raise RuntimeError("accepted content lacks final independent acceptance")
    if cp06["accepted_content_final_sha256"] != sha(ACCEPTED):
        raise RuntimeError("CP06 accepted-content hash mismatch")
    if cp06["pending_high"] or cp06["pending_indeterminate"]:
        raise RuntimeError("CP06 has unresolved priority items")
    existing = E.load_corpus(BASELINE)
    active = {row["target_id"]: row for row in existing if row["status"] == "ACTIVE"}
    if (len(existing), len(active)) != (2313, 2017):
        raise RuntimeError("QA-06 baseline cardinality mismatch")
    ctx = E.NormContext("CC2002", config_path=CONFIG)
    explanations = []
    for record in accepted["records"]:
        old = active[record["target_id"]]
        explanations.append({
            "target_id": record["target_id"], "role": old["granularity"]["role"],
            "semantic_autonomy": old["granularity"]["semantic_autonomy"],
            "editorial_reason": "QA-07: resolução revalidada dos achados materiais prioritários " + ", ".join(record["finding_ids"]),
            "content": record["proposed_content"], "external_layer_notes": old["external_layer_notes"],
            "review_status": "PENDING_HUMAN_REVIEW", "editorial_version": old["editorial_version"] + 1,
        })
    drafts = {
        "schema_version": 1, "norma_id": "CC2002", "template_version": "ENTENDA-T1",
        "prompt_version": "QA07-HIGH-AND-INDETERMINATE-RESOLUTION",
        "review_status": "PENDING_HUMAN_REVIEW",
        "authoring": {"method": "INDEPENDENT_EDITOR_REVIEW_INTEGRATION", "mission": "QA-07",
                      "generated_on": prep.AS_OF, "human_approval_claimed": False},
        "explanations": explanations,
    }
    records = E.stamp(drafts, ctx, existing=existing)
    accepted_by_target = {r["target_id"]: r for r in accepted["records"]}
    for row in records:
        if row["status"] == "ACTIVE" and row["target_id"] in accepted_by_target:
            source = accepted_by_target[row["target_id"]]
            row["qa07_resolution"] = {
                "finding_ids": source["finding_ids"], "subdivision_ids": source["subdivision_ids"],
                "origins": source["origins"], "integration_kind": source["integration_kind"],
                "accepted_content_sha256": sha(ACCEPTED), "independent_review_sha256": sha(CP06),
                "human_approval_claimed": False,
            }
    E.validate_corpus(records, ctx)
    E.write_corpus(records, CORPUS, ctx)
    index_manifest = E.build_entenda_index(ctx, records, INDEX)
    new_active = {row["target_id"]: row for row in records if row["status"] == "ACTIVE"}
    changed = sorted(tid for tid in active if new_active[tid]["explanation_id"] != active[tid]["explanation_id"])
    if changed != sorted(accepted_by_target):
        raise RuntimeError("candidate changed outside authorized targets")
    if (len(records), len(new_active), sum(r["status"] != "ACTIVE" for r in records)) != (2344, 2017, 327):
        raise RuntimeError("QA-07 candidate cardinality mismatch")
    by_id = {r["explanation_id"]: r for r in records}
    for tid in changed:
        old, new = active[tid], new_active[tid]
        retired = by_id[old["explanation_id"]]
        if retired["content"] != old["content"] or retired["source"] != old["source"]:
            raise RuntimeError(f"historical mutation: {tid}")
        if retired["superseded_by"] != new["explanation_id"]:
            raise RuntimeError(f"supersession mismatch: {tid}")
    manifest = {
        "schema_version": 1, "mission": "QA-07", "as_of": prep.AS_OF,
        "status": "CANDIDATE_COMPLETE_PENDING_HUMAN_REVIEW", "candidate_only": True,
        "baseline": str(BASELINE.relative_to(HERE)).replace("\\", "/"),
        "baseline_sha256": sha(BASELINE), "records": 2344, "active": 2017, "historical": 327,
        "versioned_targets": 31, "target_ids": changed, "corpus_sha256": sha(CORPUS),
        "candidate_index": index_manifest, "accepted_content_sha256": sha(ACCEPTED),
        "independent_review_sha256": sha(CP06), "production_index_modified": False,
        "human_approved": False, "deployed": False,
    }
    prep.write(CANDIDATE / "QA07_CANDIDATE_MANIFEST.json", manifest)
    prep.write(OUT / "QA07_CP07.json", {
        "schema_version": 1, "mission": "QA-07", "checkpoint": "CP07", "as_of": prep.AS_OF,
        "status": "CANDIDATE_INTEGRATION_COMPLETE", "versioned_targets": 31,
        "records": 2344, "active": 2017, "historical": 327,
        "corpus_sha256": sha(CORPUS),
        "lookup_sha256": sha(INDEX / "ENTENDA_LOOKUP.IDX"),
        "payload_sha256": sha(INDEX / "ENTENDA_PAYLOAD.DAT"),
        "production_index_modified": False, "human_approved": False, "deployed": False,
    })
    print(json.dumps({"targets": 31, "records": 2344, "active": 2017, "historical": 327,
                      "corpus_sha256": sha(CORPUS)}, ensure_ascii=False))
    return manifest


if __name__ == "__main__":
    build()
