"""Build the isolated QA-03 candidate with 78 independently revalidated corrections."""
import json
from collections import Counter
from pathlib import Path

import entenda_engine as E
import qa03_prepare as prep

EDITORIAL = prep.OUT / "QA03_EDITORIAL_CORRECTIONS_78.json"
REVALIDATION = prep.OUT / "QA03_EDITORIAL_REVALIDATION_78.json"
CANDIDATE = prep.HERE / "derived/candidate_qa03_cc_001_2046"
CORPUS = CANDIDATE / "CC2002_QA03.entenda.jsonl"
INDEX = CANDIDATE / "candidate_index"
CONFIG = prep.HERE / "derived/candidate_cc_001_2046/CC13_ENTENDA_CONFIG.json"
CRITICAL = ("CC2002:ART.1258", "CC2002:ART.1276", "CC2002:ART.1641", "CC2002:ART.2016")
EXTERNAL_NOTES = {
    "CC2002:ART.1829": ["STF, Tema 809: o regime sucessório do art. 1.829 aplica-se também à união estável."],
    "CC2002:ART.1641": ["STF, Tema 1.236: a separação do inciso II pode ser afastada por manifestação expressa em escritura pública."],
    "CC2002:ART.1824": ["STJ, Tema Repetitivo 1.200: o prazo da petição de herança começa na abertura da sucessão."],
}


def write(path, value):
    prep.write_json(path, value)


def build():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")
    editorial_doc = json.loads(EDITORIAL.read_text(encoding="utf-8"))
    reviews_doc = json.loads(REVALIDATION.read_text(encoding="utf-8"))
    proposals = editorial_doc["records"]
    reviews = {item["target_id"]: item for item in reviews_doc["records"]}
    if len(proposals) != 78 or len(reviews) != 78:
        raise RuntimeError("correction/revalidation cardinality mismatch")
    if any(reviews[item["target_id"]]["decision"] != "CONFIRMED_CORRECTED" for item in proposals):
        raise RuntimeError("a correction lacks independent confirmation")

    ctx = E.NormContext("CC2002", config_path=CONFIG)
    existing = E.load_corpus(prep.CORPUS)
    active = {row["target_id"]: row for row in existing if row["status"] == "ACTIVE"}
    explanations = []
    for item in proposals:
        old = active[item["target_id"]]
        explanations.append({
            "target_id": item["target_id"],
            "role": old["granularity"]["role"],
            "semantic_autonomy": old["granularity"]["semantic_autonomy"],
            "editorial_reason": (
                "Correção jurídica versionada da QA-03, baseada em achado independente QA-02 e "
                "revalidada separadamente contra fontes oficiais."
            ),
            "content": item["proposed_content"],
            "external_layer_notes": list(old["external_layer_notes"]) + EXTERNAL_NOTES.get(item["target_id"], []),
            "review_status": "PENDING_HUMAN_REVIEW",
            "editorial_version": old["editorial_version"] + 1,
        })
    drafts = {
        "schema_version": 1,
        "norma_id": "CC2002",
        "template_version": "ENTENDA-T1",
        "prompt_version": "QA03-CORRECTION-AND-INDEPENDENT-REVALIDATION-V1",
        "review_status": "PENDING_HUMAN_REVIEW",
        "authoring": {
            "method": "QA02_FINDING_CORRECTION_WITH_SEPARATE_INDEPENDENT_LEGAL_REVALIDATION",
            "mission": "QA-03",
            "generated_on": prep.AS_OF,
            "human_approval_claimed": False,
        },
        "explanations": explanations,
    }
    records = E.stamp(drafts, ctx, existing=existing)
    review_by_target = reviews
    proposal_by_target = {item["target_id"]: item for item in proposals}
    for record in records:
        target = record["target_id"]
        if record["status"] == "ACTIVE" and target in proposal_by_target:
            proposal = proposal_by_target[target]
            review = review_by_target[target]
            record["qa03_correction"] = {
                "source_inventory": "QA03_CORRECTION_INVENTORY.json",
                "source_wave": proposal["source_wave"],
                "severity": proposal["severity"],
                "source_finding_sha256": prep.json_sha(proposal["source_finding"]),
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
    retired_current = [row for row in records if row["status"] == "RETIRED" and row["target_id"] in proposal_by_target]
    if len(new_active) != 78 or len(records) != 2258 or sum(row["status"] == "ACTIVE" for row in records) != 2017:
        raise RuntimeError("candidate version cardinality mismatch")
    for row in new_active:
        old = active[row["target_id"]]
        if row["editorial_version"] != old["editorial_version"] + 1:
            raise RuntimeError(f"editorial version did not advance for {row['target_id']}")
        previous = next(item for item in retired_current if item["explanation_id"] == old["explanation_id"])
        if previous["superseded_by"] != row["explanation_id"] or previous["content"] != old["content"]:
            raise RuntimeError(f"historical preservation mismatch for {row['target_id']}")

    severity_order = {"CRÍTICO": 0, "ALTO": 1, "MÉDIO": 2}
    ordered = sorted(proposals, key=lambda item: (severity_order[item["severity"]], item["target_id"]))
    critical = [item for item in ordered if item["severity"] == "CRÍTICO"]
    high = [item for item in ordered if item["severity"] == "ALTO"]
    medium = [item for item in ordered if item["severity"] == "MÉDIO"]
    groups = {
        2: critical,
        3: high[:11], 4: high[11:21], 5: high[21:31], 6: high[31:41], 7: high[41:],
        8: medium[:8], 9: medium[8:16], 10: medium[16:],
    }
    for number, group in groups.items():
        document = {
            "schema_version": 1, "mission": "QA-03-FRONT-A", "checkpoint": f"A-CP{number:02d}",
            "as_of": prep.AS_OF, "status": "COMPLETE_REVALIDATED",
            "severity": group[0]["severity"], "total": len(group),
            "target_ids": [item["target_id"] for item in group],
            "records": [{
                "target_id": item["target_id"], "severity": item["severity"],
                "changed_fields": item["changed_fields"],
                "proposal_sha256": prep.json_sha(item["proposed_content"]),
                "revalidation_decision": reviews[item["target_id"]]["decision"],
                "revalidation_sha256": prep.json_sha(reviews[item["target_id"]]),
                "new_explanation_id": next(row["explanation_id"] for row in new_active if row["target_id"] == item["target_id"]),
            } for item in group],
        }
        write(prep.OUT / f"QA03_A_CP{number:02d}.json", document)

    cp11 = {
        "schema_version": 1, "mission": "QA-03-FRONT-A", "checkpoint": "A-CP11",
        "as_of": prep.AS_OF, "status": "COMPLETE",
        "source": REVALIDATION.name, "source_sha256": prep.sha256(REVALIDATION),
        "revalidated": 78, "decision_counts": reviews_doc["decision_counts"],
        "critical_targets": list(CRITICAL),
    }
    write(prep.OUT / "QA03_A_CP11.json", cp11)

    resolution = {
        "schema_version": 1, "mission": "QA-03-FRONT-A", "as_of": prep.AS_OF,
        "status": "78_KNOWN_FINDINGS_CORRECTED_AND_INDEPENDENTLY_REVALIDATED",
        "source_inventory": "QA03_CORRECTION_INVENTORY.json",
        "editorial_source": EDITORIAL.name, "editorial_source_sha256": prep.sha256(EDITORIAL),
        "revalidation_source": REVALIDATION.name, "revalidation_source_sha256": prep.sha256(REVALIDATION),
        "total": 78, "corrected": 78, "revalidated": 78, "pending": 0,
        "severity_counts": dict(sorted(Counter(item["severity"] for item in proposals).items())),
        "critical_status": {target: "CORRECTED_AND_INDEPENDENTLY_REVALIDATED" for target in CRITICAL},
        "records": [{
            "target_id": item["target_id"], "severity": item["severity"],
            "old_explanation_id": item["baseline_explanation_id"],
            "new_explanation_id": next(row["explanation_id"] for row in new_active if row["target_id"] == item["target_id"]),
            "changed_fields": item["changed_fields"], "decision": reviews[item["target_id"]]["decision"],
        } for item in proposals],
    }
    write(prep.OUT / "QA03_CORRECTION_RESOLUTION_78.json", resolution)
    manifest = {
        "schema_version": 1, "mission": "QA-03-FRONT-A", "checkpoint": "A-CP12",
        "as_of": prep.AS_OF, "status": "CANDIDATE_COMPLETE", "candidate_only": True,
        "deployed": False, "production_index_modified": False,
        "baseline": str(prep.CORPUS.relative_to(prep.HERE)).replace("\\", "/"),
        "baseline_sha256": prep.PROTECTED["corpus"],
        "records": len(records), "active": 2017, "historical": len(records) - 2017,
        "versioned_targets": 78,
        "corpus_sha256": prep.sha256(CORPUS), "candidate_index": index_manifest,
        "correction_resolution_sha256": prep.sha256(prep.OUT / "QA03_CORRECTION_RESOLUTION_78.json"),
    }
    write(CANDIDATE / "QA03_CANDIDATE_MANIFEST.json", manifest)
    cp12 = {
        "schema_version": 1, "mission": "QA-03-FRONT-A", "checkpoint": "A-CP12",
        "as_of": prep.AS_OF, "status": "COMPLETE", "manifest": "QA03_CANDIDATE_MANIFEST.json",
        "manifest_sha256": prep.sha256(CANDIDATE / "QA03_CANDIDATE_MANIFEST.json"),
        "corpus_sha256": manifest["corpus_sha256"],
        "lookup_sha256": prep.sha256(INDEX / "ENTENDA_LOOKUP.IDX"),
        "payload_sha256": prep.sha256(INDEX / "ENTENDA_PAYLOAD.DAT"),
        "production_index_modified": False, "deployed": False,
    }
    write(prep.OUT / "QA03_A_CP12.json", cp12)
    print(json.dumps({"corrected": 78, "revalidated": 78, "records": len(records),
                      "active": 2017, "historical": len(records) - 2017,
                      "corpus_sha256": manifest["corpus_sha256"]}, ensure_ascii=False))
    return manifest


if __name__ == "__main__":
    build()
