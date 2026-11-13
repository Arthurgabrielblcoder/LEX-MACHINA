"""Integrate the three non-overlapping QA-05 editorial modules into checkpoints."""
import json

import qa05_prepare as prep


MODULES = (
    prep.OUT / "QA05_EDITORIAL_A_CRITICAL_HIGH_12.json",
    prep.OUT / "QA05_EDITORIAL_B_HIGH_MEDIUM_17.json",
    prep.OUT / "QA05_EDITORIAL_C_HIGH_MEDIUM_21.json",
)
CROSS_AUDIT = prep.OUT / "QA05_CROSS_AUDIT_1101_1105.json"
CONSOLIDATED = prep.OUT / "QA05_EDITORIAL_CORRECTIONS_50.json"


def main():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")
    inventory = json.loads((prep.OUT / "QA05_CORRECTION_INVENTORY_50.json").read_text(encoding="utf-8"))
    baseline = [json.loads(line) for line in prep.CORPUS.read_text(encoding="utf-8").splitlines() if line]
    active = {row["target_id"]: row for row in baseline if row["status"] == "ACTIVE"}
    records = []
    for module in MODULES:
        records.extend(json.loads(module.read_text(encoding="utf-8"))["records"])
    by_target = {row["target_id"]: row for row in records}
    expected = [row["target_id"] for row in inventory["records"]]
    if len(records) != 50 or len(by_target) != 50 or set(by_target) != set(expected):
        raise RuntimeError("editorial modules do not cover exactly 50 unique targets")
    ordered = []
    inventory_by_target = {row["target_id"]: row for row in inventory["records"]}
    for target in expected:
        proposal = by_target[target]
        meta = inventory_by_target[target]
        old = active[target]
        if proposal["severity"] != meta["severity"] or proposal["baseline_explanation_id"] != old["explanation_id"]:
            raise RuntimeError(f"identity/severity mismatch: {target}")
        if proposal["baseline_content_sha256"] != prep.json_sha(old["content"]):
            raise RuntimeError(f"baseline content mismatch: {target}")
        if set(proposal["proposed_content"]) != set(prep.FIELDS):
            raise RuntimeError(f"five-field contract mismatch: {target}")
        actual_changed = [field for field in prep.FIELDS if proposal["proposed_content"][field] != old["content"][field]]
        if proposal["changed_fields"] != actual_changed or not actual_changed:
            raise RuntimeError(f"changed field mismatch: {target}")
        proposal["source_finding_sha256"] = meta["finding_sha256"]
        proposal["correction_position"] = meta["correction_position"]
        proposal["independent_approval_claimed"] = False
        ordered.append(proposal)
    document = {
        "schema_version": 1, "mission": "QA-05", "as_of": prep.AS_OF,
        "status": "PROPOSED_PENDING_INDEPENDENT_REVALIDATION", "total": 50,
        "source_inventory": "QA05_CORRECTION_INVENTORY_50.json",
        "source_modules": [{"name": path.name, "sha256": prep.sha256(path)} for path in MODULES],
        "records": ordered,
    }
    prep.write_json(CONSOLIDATED, document)

    critical = [row for row in ordered if row["severity"] == "CRÍTICO"]
    high = [row for row in ordered if row["severity"] == "ALTO"]
    medium = [row for row in ordered if row["severity"] == "MÉDIO"]
    groups = {2: critical, 4: high[:8], 5: high[8:16], 6: high[16:24], 7: high[24:],
              8: medium[:6], 9: medium[6:12], 10: medium[12:]}
    for number, group in groups.items():
        checkpoint = {
            "schema_version": 1, "mission": "QA-05", "checkpoint": f"CP{number:02d}",
            "as_of": prep.AS_OF, "status": "EDITORIAL_COMPLETE_PENDING_INDEPENDENT_REVALIDATION",
            "severity": group[0]["severity"], "total": len(group),
            "target_ids": [row["target_id"] for row in group],
            "records": [{"target_id": row["target_id"], "severity": row["severity"],
                         "changed_fields": row["changed_fields"],
                         "proposal_sha256": prep.json_sha(row["proposed_content"]),
                         "editor_identifier": row["editor_identifier"]} for row in group],
        }
        prep.write_json(prep.OUT / f"QA05_CHECKPOINT_{number:02d}.json", checkpoint)
    cross = json.loads(CROSS_AUDIT.read_text(encoding="utf-8"))
    text = json.dumps(cross, ensure_ascii=False)
    for number in range(1101, 1106):
        if str(number) not in text:
            raise RuntimeError(f"cross-audit lacks art. {number}")
    prep.write_json(prep.OUT / "QA05_CHECKPOINT_03.json", {
        "schema_version": 1, "mission": "QA-05", "checkpoint": "CP03", "as_of": prep.AS_OF,
        "status": "CROSS_AUDIT_COMPLETE", "scope": ["CC2002:ART.1101", "CC2002:ART.1102",
        "CC2002:ART.1103", "CC2002:ART.1104", "CC2002:ART.1105"],
        "source": CROSS_AUDIT.name, "source_sha256": prep.sha256(CROSS_AUDIT),
        "neighbor_content_modified": False,
    })
    print(json.dumps({"integrated": 50, "critical": len(critical), "high": len(high),
                      "medium": len(medium)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
