"""Consolidate individual QA decisions for all 1,038 preliminary QA-06 findings."""
import json
from collections import Counter

import qa06_prepare as prep


SOURCE_FILES = (
    "QA06_B_FINDINGS_V2_0001_0672.json",
    "QA06_B_FINDINGS_V2_0673_1344.json",
    "QA06_B_FINDINGS_V2_1345_2017.json",
)
HIGH_REVIEWS = (
    "QA06_B_HIGH_FINDINGS_CROSS_REVIEW_0673_1344.json",
    "QA06_B_HIGH_FINDINGS_CROSS_REVIEW_OUTER.json",
)
NON_HIGH_REVIEWS = (
    "QA06_B_NON_HIGH_SAMPLE_REVIEW_0001_0672.json",
    "QA06_B_NON_HIGH_SAMPLE_REVIEW_0673_1344.json",
    "QA06_B_NON_HIGH_SAMPLE_REVIEW_1345_2017.json",
    "QA06_B_NON_HIGH_EXPANDED_REVIEW_0673_1344.json",
    "QA06_B_NON_HIGH_EXPANDED_REVIEW_1345_2017_A.json",
    "QA06_B_NON_HIGH_EXPANDED_REVIEW_1345_2017_B.json",
)
VALID_SEVERITY = {"CRÍTICO", "ALTO", "MÉDIO", "BAIXO"}
HIGH_DECISION = {
    "CONFIRMED_FINDING": "CONFIRMADO",
    "DOWNGRADE_MEDIO": "RECLASSIFICADO",
    "REJECTED_FALSE_POSITIVE": "NAO_CONFIRMADO",
    "INDETERMINADA": "INDETERMINADO",
}


def records(document):
    return document.get("records") or document.get("reviews") or []


def rationale(record):
    return record.get("justification") or record.get("rationale") or ""


def main():
    source = {}
    source_artifacts = []
    for filename in SOURCE_FILES:
        path = prep.OUT / filename
        document = json.loads(path.read_text(encoding="utf-8"))
        source_artifacts.append({"file": filename, "sha256": prep.sha256(path), "total": len(document["findings"])})
        for finding in document["findings"]:
            subdivision_id = finding["subdivision_id"]
            if subdivision_id in source:
                raise RuntimeError(f"duplicate source finding: {subdivision_id}")
            source[subdivision_id] = finding
    if len(source) != 1038:
        raise RuntimeError("unexpected preliminary finding total")

    decisions = {}
    review_artifacts = []
    for filename in HIGH_REVIEWS:
        path = prep.OUT / filename
        document = json.loads(path.read_text(encoding="utf-8"))
        review_artifacts.append({"file": filename, "sha256": prep.sha256(path), "total": len(records(document)),
                                 "scope": "ALL_PRELIMINARY_HIGH"})
        for review in records(document):
            subdivision_id = review["subdivision_id"]
            if subdivision_id in decisions:
                raise RuntimeError(f"duplicate QA decision: {subdivision_id}")
            if source[subdivision_id]["severity"] != "ALTO":
                raise RuntimeError(f"high review contains non-high source: {subdivision_id}")
            if (review.get("source_finding_sha256") is not None and
                    review.get("source_finding_sha256") != prep.json_sha(source[subdivision_id])):
                raise RuntimeError(f"high review source hash mismatch: {subdivision_id}")
            decision = HIGH_DECISION[review["decision"]]
            final_severity = review.get("final_severity")
            if final_severity == "NONE":
                final_severity = "SEM_ACHADO"
            decisions[subdivision_id] = {
                "decision": decision, "original_review_decision": review["decision"],
                "final_classification": review.get("source_classification") or source[subdivision_id]["classification"],
                "final_severity": final_severity, "confidence": review.get("confidence"),
                "justification": rationale(review), "review_file": filename,
                "review_record_sha256": prep.json_sha(review),
            }

    for filename in NON_HIGH_REVIEWS:
        path = prep.OUT / filename
        document = json.loads(path.read_text(encoding="utf-8"))
        review_artifacts.append({"file": filename, "sha256": prep.sha256(path), "total": len(records(document)),
                                 "scope": "STRATIFIED_SAMPLE" if "SAMPLE_REVIEW" in filename else "EXPANDED_REMAINDER"})
        for review in records(document):
            subdivision_id = review["subdivision_id"]
            if subdivision_id in decisions:
                raise RuntimeError(f"duplicate QA decision: {subdivision_id}")
            if source[subdivision_id]["severity"] == "ALTO":
                raise RuntimeError(f"non-high review contains high source: {subdivision_id}")
            if (review.get("source_finding_sha256") is not None and
                    review.get("source_finding_sha256") != prep.json_sha(source[subdivision_id])):
                raise RuntimeError(f"non-high review source hash mismatch: {subdivision_id}")
            final_severity = review.get("final_severity")
            if final_severity in ("NONE", "NAO_APLICAVEL"):
                final_severity = "SEM_ACHADO"
            decisions[subdivision_id] = {
                "decision": review["decision"], "original_review_decision": review["decision"],
                "final_classification": review.get("final_classification"),
                "final_severity": final_severity, "confidence": review.get("confidence"),
                "justification": rationale(review), "review_file": filename,
                "review_record_sha256": prep.json_sha(review),
            }
    if set(decisions) != set(source) or len(decisions) != 1038:
        missing = sorted(set(source) - set(decisions))
        raise RuntimeError(f"QA decision coverage incomplete: {len(decisions)}; missing={missing[:5]}")

    final_records = []
    for position, finding in enumerate(sorted(source.values(), key=lambda item: (item["audit_position"], item["subdivision_id"])), 1):
        subdivision_id = finding["subdivision_id"]
        qa = dict(decisions[subdivision_id])
        if finding["target_id"] == "CC2002:ART.1104":
            qa.update({
                "decision": "CONFIRMADO",
                "final_classification": "INCORRETA",
                "final_severity": "ALTO",
                "central_override": True,
                "override_reason": (
                    "A revisão alta leu apenas excertos de o_que_diz/atencao; a Frente A comprovou o deslocamento "
                    "em o_que_significa/exemplo_pratico, corrigiu-o e obteve revalidação independente sem objeções."
                ),
            })
        decision = qa["decision"]
        if finding["target_id"] == "CC2002:ART.1104":
            disposition = "JA_CORRIGIDO"
        elif decision == "DUPLICADO":
            disposition = "DUPLICADO"
        elif decision == "INDETERMINADO" or qa["final_classification"] == "INDETERMINADA":
            disposition = "INDETERMINADO"
        elif decision == "NAO_CONFIRMADO" or qa["final_severity"] not in VALID_SEVERITY:
            disposition = "NAO_CONFIRMADO"
        else:
            disposition = "PENDENTE_CORRECAO"
        final_records.append({
            "finding_position": position,
            "finding_id": f"QA06-FINAL-{position:04d}",
            "target_id": finding["target_id"], "audit_position": finding["audit_position"],
            "subdivision_id": subdivision_id,
            "initial_classification": finding["classification"],
            "initial_severity": finding["severity"],
            "source_finding_sha256": prep.json_sha(finding),
            "review_decision": decision,
            "original_review_decision": qa["original_review_decision"],
            "final_classification": qa["final_classification"],
            "final_severity": qa["final_severity"],
            "final_disposition": disposition,
            "review_justification": qa["justification"],
            "review_confidence": qa["confidence"],
            "review_file": qa["review_file"],
            "review_record_sha256": qa["review_record_sha256"],
            "central_override": qa.get("central_override", False),
            "override_reason": qa.get("override_reason"),
            "finding": finding,
        })

    disposition_counts = Counter(item["final_disposition"] for item in final_records)
    decision_counts = Counter(item["review_decision"] for item in final_records)
    pending = [item for item in final_records if item["final_disposition"] == "PENDENTE_CORRECAO"]
    indeterminate = [item for item in final_records if item["final_disposition"] == "INDETERMINADO"]
    rejected = [item for item in final_records if item["final_disposition"] in ("NAO_CONFIRMADO", "DUPLICADO")]
    corrected = [item for item in final_records if item["final_disposition"] == "JA_CORRIGIDO"]
    if sum(disposition_counts.values()) != 1038 or len(corrected) != 1:
        raise RuntimeError("final disposition partition mismatch")

    consolidation = {
        "schema_version": 1, "mission": "QA-06-FINDINGS-FINAL-QA", "as_of": prep.AS_OF,
        "status": "ALL_PRELIMINARY_FINDINGS_INDIVIDUALLY_QA_REVIEWED",
        "authorized_inventory_sha256": "7fe41b6b6e7755e17174551b56ea684fbbd8a399e95641f7f47e729f55ef5c82",
        "baseline_qa05_sha256": prep.PROTECTED["qa05_corpus"],
        "initial_findings": 1038,
        "initial_high_findings": 154,
        "high_review": {"reviewed": 154, "art_1104_central_override": 1},
        "non_high_quality_control": {
            "population": 884,
            "stratified_sample": 120,
            "sample_not_confirmed": 64,
            "sample_false_positive_rate": 0.5333333333,
            "expanded_remainder_review": 764,
            "full_non_high_review_complete": True,
        },
        "review_decision_counts": dict(sorted(decision_counts.items())),
        "final_disposition_counts": dict(sorted(disposition_counts.items())),
        "pending_severity_counts": dict(sorted(Counter(item["final_severity"] for item in pending).items())),
        "pending_classification_counts": dict(sorted(Counter(item["final_classification"] for item in pending).items())),
        "source_artifacts": source_artifacts,
        "review_artifacts": review_artifacts,
        "records": final_records,
        "subdivision_findings_resolved": False,
        "full_corpus_legally_approved": False,
        "human_approved": False,
    }
    consolidation_path = prep.OUT / "QA06_B_FINDINGS_FINAL_CONSOLIDATION.json"
    prep.write_json(consolidation_path, consolidation)
    prep.write_json(prep.OUT / "QA06_B_DEFINITIVE_CORRECTION_QUEUE.json", {
        "schema_version": 1, "mission": "QA-06-FUTURE-CORRECTIONS", "as_of": prep.AS_OF,
        "status": "DEFINITIVE_CONFIRMED_AND_RECLASSIFIED_FINDINGS_PENDING_CORRECTION",
        "source": consolidation_path.name, "source_sha256": prep.sha256(consolidation_path),
        "total": len(pending),
        "severity_counts": consolidation["pending_severity_counts"],
        "classification_counts": consolidation["pending_classification_counts"],
        "findings": pending, "corpus_modified": False, "human_approval_claimed": False,
    })
    prep.write_json(prep.OUT / "QA06_B_INDETERMINATE_REVIEW_QUEUE.json", {
        "schema_version": 1, "mission": "QA-06-FUTURE-LEGAL-REVIEW", "as_of": prep.AS_OF,
        "status": "INDETERMINATE_SEPARATE_REVIEW_QUEUE", "total": len(indeterminate),
        "findings": indeterminate, "corpus_modified": False, "human_approval_claimed": False,
    })
    prep.write_json(prep.OUT / "QA06_B_REJECTED_FINDINGS_EVIDENCE.json", {
        "schema_version": 1, "mission": "QA-06-FINDINGS-FINAL-QA", "as_of": prep.AS_OF,
        "status": "REJECTED_OR_DUPLICATE_FINDINGS_PRESERVED_WITH_JUSTIFICATION",
        "total": len(rejected), "findings": rejected,
    })
    print(json.dumps({
        "initial": 1038, "decisions": dict(sorted(decision_counts.items())),
        "dispositions": dict(sorted(disposition_counts.items())),
        "pending": len(pending), "pending_severity": consolidation["pending_severity_counts"],
        "indeterminate": len(indeterminate), "rejected": len(rejected), "corrected": len(corrected),
        "consolidation_sha256": prep.sha256(consolidation_path),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
