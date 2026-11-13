"""Validate the three QA-06 V2 audit modules and build 41 checkpoints."""
import json
from collections import Counter, defaultdict

import qa06_prepare as prep


INVENTORY = prep.OUT / "QA06_SUBDIVISION_INVENTORY_V2_CORRECTED.json"
MODULES = (
    (1, 672, "QA06_B_REVIEW_V2_0001_0672.json", "QA06_B_FINDINGS_V2_0001_0672.json"),
    (673, 1344, "QA06_B_REVIEW_V2_0673_1344.json", "QA06_B_FINDINGS_V2_0673_1344.json"),
    (1345, 2017, "QA06_B_REVIEW_V2_1345_2017.json", "QA06_B_FINDINGS_V2_1345_2017.json"),
)
ALLOWED = {"COBERTA", "PARCIAL", "INCORRETA", "AUSENTE", "NAO_APLICAVEL", "INDETERMINADA"}
PROBLEM = {"PARCIAL", "INCORRETA", "AUSENTE", "INDETERMINADA"}
SEVERITY = {"CRÍTICO", "ALTO", "MÉDIO", "BAIXO"}
HIGH_CROSS_REVIEWS = (
    prep.OUT / "QA06_B_HIGH_FINDINGS_CROSS_REVIEW_0673_1344.json",
    prep.OUT / "QA06_B_HIGH_FINDINGS_CROSS_REVIEW_OUTER.json",
)


def legal_evidence_text(assessment):
    evidence = assessment.get("evidence") or {}
    return evidence.get("legal_text") or evidence.get("legal_excerpt")


def content_hash(record):
    direct = record.get("baseline_content_sha256") or record.get("content_sha256")
    if direct:
        return direct
    assessments = record.get("subdivision_assessments", [])
    if assessments:
        return (assessments[0].get("evidence") or {}).get("baseline_content_sha256")
    return None


def assessment_status(assessment):
    return assessment.get("status") or assessment.get("classification")


def validate_and_load():
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    expected = {record["audit_position"]: record for record in inventory["records"]}
    modules, records, findings = [], [], []
    seen_subdivisions, seen_findings, rationales = set(), set(), set()
    for start, end, review_name, findings_name in MODULES:
        review_path, findings_path = prep.OUT / review_name, prep.OUT / findings_name
        review = json.loads(review_path.read_text(encoding="utf-8"))
        finding_doc = json.loads(findings_path.read_text(encoding="utf-8"))
        review_inventory_hash = review.get("inventory_sha256") or review.get("authorized_inventory_sha256")
        finding_inventory_hash = finding_doc.get("inventory_sha256") or finding_doc.get("authorized_inventory_sha256")
        if review_inventory_hash != prep.sha256(INVENTORY):
            raise RuntimeError(f"wrong inventory hash: {review_name}")
        review_baseline_hash = review.get("baseline_corpus_sha256") or review.get("baseline_sha256")
        finding_baseline_hash = finding_doc.get("baseline_corpus_sha256") or finding_doc.get("baseline_sha256")
        if review_baseline_hash != prep.PROTECTED["qa05_corpus"]:
            raise RuntimeError(f"wrong baseline hash: {review_name}")
        if finding_inventory_hash != prep.sha256(INVENTORY):
            raise RuntimeError(f"wrong findings inventory hash: {findings_name}")
        if finding_baseline_hash != prep.PROTECTED["qa05_corpus"]:
            raise RuntimeError(f"wrong findings baseline hash: {findings_name}")
        module_records = review["records"]
        if [row["audit_position"] for row in module_records] != list(range(start, end + 1)):
            raise RuntimeError(f"non-contiguous module: {review_name}")
        module_findings = finding_doc["findings"]
        findings_by_segment = {row["subdivision_id"]: row for row in module_findings}
        if len(findings_by_segment) != len(module_findings):
            raise RuntimeError(f"duplicate findings: {findings_name}")
        module_classification = Counter()
        problematic_ids = []
        for row in module_records:
            source = expected[row["audit_position"]]
            if row["target_id"] != source["target_id"] or row["explanation_id"] != source["explanation_id"]:
                raise RuntimeError(f"record identity mismatch: {row['audit_position']}")
            if content_hash(row) != source["content_sha256"]:
                raise RuntimeError(f"content hash mismatch: {row['target_id']}")
            assessments = row["subdivision_assessments"]
            if [item["subdivision_id"] for item in assessments] != [item["subdivision_id"] for item in source["subdivisions"]]:
                raise RuntimeError(f"subdivision order mismatch: {row['target_id']}")
            for assessment, subdivision in zip(assessments, source["subdivisions"]):
                subdivision_id = assessment["subdivision_id"]
                if subdivision_id in seen_subdivisions:
                    raise RuntimeError(f"duplicate assessment: {subdivision_id}")
                seen_subdivisions.add(subdivision_id)
                status = assessment_status(assessment)
                assessment.setdefault("status", status)
                if status not in ALLOWED:
                    raise RuntimeError(f"invalid status: {subdivision_id} {status}")
                if subdivision["material_audit_required"] and status == "NAO_APLICAVEL":
                    raise RuntimeError(f"auditable subdivision marked not applicable: {subdivision_id}")
                if not subdivision["material_audit_required"] and status != "NAO_APLICAVEL":
                    raise RuntimeError(f"excluded subdivision lacks NAO_APLICAVEL: {subdivision_id}")
                if assessment.get("kind") != subdivision["kind"]:
                    raise RuntimeError(f"kind mismatch: {subdivision_id}")
                rationale = assessment.get("rationale", "").strip()
                if len(rationale) < 35 or rationale in rationales:
                    raise RuntimeError(f"missing or repeated individual rationale: {subdivision_id}")
                rationales.add(rationale)
                if not isinstance(assessment.get("material_elements"), dict):
                    raise RuntimeError(f"material elements absent: {subdivision_id}")
                if (subdivision["material_audit_required"] and status not in ("AUSENTE", "INDETERMINADA")
                        and not assessment.get("related_fields")):
                    raise RuntimeError(f"related fields absent: {subdivision_id}")
                evidence_text = legal_evidence_text(assessment)
                evidence_matches = (evidence_text == subdivision["text"] or
                                    (isinstance(evidence_text, str) and evidence_text.endswith("…") and
                                     subdivision["text"].startswith(evidence_text[:-1])))
                if status != "NAO_APLICAVEL" and not evidence_matches:
                    raise RuntimeError(f"legal evidence mismatch: {subdivision_id}")
                module_classification[status] += 1
                if status in PROBLEM:
                    problematic_ids.append(subdivision_id)
        if set(problematic_ids) != set(findings_by_segment):
            raise RuntimeError(f"finding coverage mismatch: {findings_name}")
        for finding in module_findings:
            subdivision_id = finding["subdivision_id"]
            if subdivision_id in seen_findings:
                raise RuntimeError(f"finding repeated across modules: {subdivision_id}")
            seen_findings.add(subdivision_id)
            if finding["classification"] not in PROBLEM or finding["severity"] not in SEVERITY:
                raise RuntimeError(f"invalid finding classification: {subdivision_id}")
            source_subdivision = next(item for item in expected[finding["audit_position"]]["subdivisions"]
                                      if item["subdivision_id"] == subdivision_id)
            if finding["legal_text"] != source_subdivision["text"]:
                raise RuntimeError(f"finding legal text mismatch: {subdivision_id}")
            if not finding.get("human_review_required"):
                raise RuntimeError(f"finding lacks human review flag: {subdivision_id}")
        if module_classification != Counter(review["classification_counts"]):
            raise RuntimeError(f"module classification summary mismatch: {review_name}")
        if len(module_findings) != review.get("finding_total", len(module_findings)) or len(module_findings) != finding_doc["total"]:
            raise RuntimeError(f"module finding total mismatch: {review_name}")
        modules.append({
            "range": [start, end], "review": review_name, "review_sha256": prep.sha256(review_path),
            "findings": findings_name, "findings_sha256": prep.sha256(findings_path),
            "target_total": len(module_records),
            "subdivision_total": sum(len(row["subdivision_assessments"]) for row in module_records),
            "finding_total": len(module_findings),
        })
        records.extend(module_records)
        findings.extend(module_findings)
    if len(records) != 2017 or len(seen_subdivisions) != inventory["subdivisions_total"]:
        raise RuntimeError("full audit coverage incomplete")
    return inventory, modules, records, findings


def build():
    inventory, modules, records, findings = validate_and_load()
    by_position = {record["audit_position"]: record for record in records}
    finding_by_position = defaultdict(list)
    for finding in findings:
        finding_by_position[finding["audit_position"]].append(finding)
    checkpoints = []
    for checkpoint_number, start in enumerate(range(1, 2018, 50), 1):
        end = min(start + 49, 2017)
        block = [by_position[position] for position in range(start, end + 1)]
        block_assessments = [item for record in block for item in record["subdivision_assessments"]]
        block_findings = [item for position in range(start, end + 1) for item in finding_by_position[position]]
        artifact = {
            "schema_version": 1, "mission": "QA-06-FRONT-B",
            "checkpoint": f"B-CP{checkpoint_number:02d}", "as_of": prep.AS_OF,
            "status": "COMPLETE_VALIDATED_AGAINST_V2",
            "authorized_inventory": INVENTORY.name,
            "authorized_inventory_sha256": prep.sha256(INVENTORY),
            "audit_position_start": start, "audit_position_end": end,
            "target_total": len(block), "subdivision_total": len(block_assessments),
            "classification_counts": dict(sorted(Counter(assessment_status(item) for item in block_assessments).items())),
            "finding_total": len(block_findings),
            "severity_counts": dict(sorted(Counter(item["severity"] for item in block_findings).items())),
            "target_ids": [record["target_id"] for record in block],
            "record_evidence": [{
                "audit_position": record["audit_position"], "target_id": record["target_id"],
                "record_sha256": prep.json_sha(record),
                "subdivision_total": len(record["subdivision_assessments"]),
                "finding_sha256": [prep.json_sha(item) for item in finding_by_position[record["audit_position"]]],
            } for record in block],
            "source_modules": [module for module in modules
                               if not (module["range"][1] < start or module["range"][0] > end)],
            "human_approval_claimed": False,
        }
        path = prep.OUT / f"QA06_B_CHECKPOINT_{checkpoint_number:02d}.json"
        prep.write_json(path, artifact)
        checkpoints.append({"checkpoint": artifact["checkpoint"], "file": path.name,
                            "sha256": prep.sha256(path), "range": [start, end],
                            "target_total": len(block), "subdivision_total": len(block_assessments),
                            "finding_total": len(block_findings)})

    assessments = [item for record in records for item in record["subdivision_assessments"]]
    high_reviews = {}
    cross_review_documents = []
    for path in HIGH_CROSS_REVIEWS:
        document = json.loads(path.read_text(encoding="utf-8"))
        cross_review_documents.append({"file": path.name, "sha256": prep.sha256(path),
                                       "reviewed": len(document["records"]),
                                       "decision_counts": document["decision_counts"]})
        for review in document["records"]:
            subdivision_id = review["subdivision_id"]
            if subdivision_id in high_reviews:
                raise RuntimeError(f"duplicate high cross-review: {subdivision_id}")
            high_reviews[subdivision_id] = review
    source_high = {item["subdivision_id"] for item in findings if item["severity"] == "ALTO"}
    if set(high_reviews) != source_high or len(high_reviews) != 154:
        raise RuntimeError("high-finding cross-review coverage mismatch")

    normalized_findings = []
    rejected_findings = []
    for position, finding in enumerate(findings, 1):
        item = {"finding_id": f"QA06-SUBDIVISION-{position:04d}", **finding}
        if finding["severity"] == "ALTO":
            cross = high_reviews[finding["subdivision_id"]]
            decision = cross["decision"]
            if finding["target_id"] == "CC2002:ART.1104":
                # The high cross-review considered only the already-correct o_que_diz
                # excerpt and missed the displaced content in o_que_significa and
                # exemplo_pratico.  Front A independently confirmed and corrected
                # that exact QA-05 finding, so this known case remains substantiated.
                item["cross_review_decision"] = "CENTRAL_OVERRIDE_CONFIRMED_BY_FRONT_A_REVALIDATION"
                item["cross_review_original_decision"] = decision
                item["final_severity"] = "ALTO"
            else:
                item["cross_review_decision"] = decision
                item["final_severity"] = ("MÉDIO" if decision == "DOWNGRADE_MEDIO"
                                          else "ALTO" if decision == "CONFIRMED_FINDING"
                                          else "SEM_ACHADO")
            item["cross_review_sha256"] = prep.json_sha(cross)
            if item["final_severity"] == "SEM_ACHADO":
                item["resolution_status"] = "REJECTED_FALSE_POSITIVE_BY_INDEPENDENT_CROSS_REVIEW"
                rejected_findings.append(item)
                continue
        else:
            item["final_severity"] = finding["severity"]
            item["cross_review_decision"] = "NOT_REQUIRED_BELOW_HIGH"
        item["resolution_status"] = ("RESOLVED_IN_QA06_FRONT_A" if finding["target_id"] == "CC2002:ART.1104"
                                     else "PENDING_FUTURE_CORRECTION_MISSION")
        normalized_findings.append(item)
    pending = [item for item in normalized_findings if item["resolution_status"].startswith("PENDING")]
    queue = {
        "schema_version": 1, "mission": "QA-06-FRONT-B", "as_of": prep.AS_OF,
        "status": "SUBDIVISION_FINDINGS_QUEUED_NOT_SILENTLY_CORRECTED",
        "source_inventory_sha256": prep.sha256(INVENTORY),
        "source_findings_before_high_cross_review": len(findings),
        "rejected_false_positives_by_high_cross_review": len(rejected_findings),
        "total_findings_retained": len(normalized_findings),
        "resolved_in_front_a": len(normalized_findings) - len(pending),
        "pending_future_mission": len(pending),
        "severity_counts_retained": dict(sorted(Counter(item["final_severity"] for item in normalized_findings).items())),
        "severity_counts_pending": dict(sorted(Counter(item["final_severity"] for item in pending).items())),
        "high_findings_cross_review": cross_review_documents,
        "findings": normalized_findings,
        "rejected_findings": rejected_findings,
        "corpus_modified_for_front_b": False, "human_approval_claimed": False,
    }
    queue_path = prep.OUT / "QA06_B_CORRECTION_QUEUE.json"
    prep.write_json(queue_path, queue)

    coverage = defaultdict(lambda: {"targets": 0, "subdivisions": 0, "findings": 0, "classifications": Counter()})
    inventory_by_position = {record["audit_position"]: record for record in inventory["records"]}
    for record in records:
        book = inventory_by_position[record["audit_position"]]["book"]
        entry = coverage[book]
        entry["targets"] += 1
        entry["subdivisions"] += len(record["subdivision_assessments"])
        entry["findings"] += len(finding_by_position[record["audit_position"]])
        entry["classifications"].update(assessment_status(item) for item in record["subdivision_assessments"])
    coverage_by_book = {book: {**{key: value for key, value in entry.items() if key != "classifications"},
                               "classifications": dict(sorted(entry["classifications"].items()))}
                        for book, entry in sorted(coverage.items())}
    consolidation = {
        "schema_version": 1, "mission": "QA-06-FRONT-B", "as_of": prep.AS_OF,
        "status": "SUBDIVISION_AUDIT_COMPLETE",
        "subdivision_findings_resolved": False, "full_corpus_legally_approved": False,
        "human_approved": False, "authorized_inventory_sha256": prep.sha256(INVENTORY),
        "baseline_qa05_sha256": prep.PROTECTED["qa05_corpus"],
        "active_targets_examined": len(records), "subdivisions_identified": len(assessments),
        "subdivisions_effectively_audited": sum(assessment_status(item) != "NAO_APLICAVEL" for item in assessments),
        "classification_counts": dict(sorted(Counter(assessment_status(item) for item in assessments).items())),
        "source_finding_total": len(findings),
        "high_cross_review_rejected_false_positives": len(rejected_findings),
        "finding_total_retained": len(normalized_findings),
        "pending_future_corrections": len(pending),
        "severity_counts_retained": dict(sorted(Counter(item["final_severity"] for item in normalized_findings).items())),
        "severity_counts_pending": dict(sorted(Counter(item["final_severity"] for item in pending).items())),
        "critical_and_high_findings": [{"finding_id": item["finding_id"], "target_id": item["target_id"],
                                        "subdivision_id": item["subdivision_id"], "severity": item["final_severity"],
                                        "classification": item["classification"], "problem": item["problem"]}
                                       for item in normalized_findings if item["final_severity"] in ("CRÍTICO", "ALTO")],
        "coverage_by_book": coverage_by_book,
        "modules": modules, "high_findings_cross_review": cross_review_documents,
        "central_override": {
            "target_id": "CC2002:ART.1104",
            "reason": "cross-review considered incomplete source excerpts; Front A independently confirmed and resolved the displaced-content finding",
            "front_a_resolution": "QA06_A_CORRECTION_RESOLUTION_1104.json",
            "front_a_resolution_sha256": prep.sha256(prep.OUT / "QA06_A_CORRECTION_RESOLUTION_1104.json"),
        },
        "checkpoints": checkpoints,
        "correction_queue": queue_path.name, "correction_queue_sha256": prep.sha256(queue_path),
        "front_a_art_1104": "CORRECTED_AND_INDEPENDENTLY_REVALIDATED_IN_CANDIDATE_QA06",
        "production_index_modified": False, "deployed": False,
    }
    consolidation_path = prep.OUT / "QA06_B_MATERIAL_AUDIT_CONSOLIDATION.json"
    prep.write_json(consolidation_path, consolidation)
    print(json.dumps({
        "targets": len(records), "subdivisions": len(assessments),
        "classifications": consolidation["classification_counts"],
        "source_findings": len(findings), "retained_findings": len(normalized_findings),
        "severity": consolidation["severity_counts_retained"],
        "pending": len(pending), "checkpoints": len(checkpoints),
        "consolidation_sha256": prep.sha256(consolidation_path),
    }, ensure_ascii=False))


if __name__ == "__main__":
    build()
