"""Create a deterministic stratified QA sample of non-high QA-06 findings."""
import hashlib
import json

import qa06_prepare as prep


MODULES = (
    ("0001_0672", "QA06_B_FINDINGS_V2_0001_0672.json"),
    ("0673_1344", "QA06_B_FINDINGS_V2_0673_1344.json"),
    ("1345_2017", "QA06_B_FINDINGS_V2_1345_2017.json"),
)


def stable_key(finding):
    return hashlib.sha256(finding["subdivision_id"].encode("utf-8")).hexdigest()


def main():
    records = []
    source_counts = {}
    for module, filename in MODULES:
        path = prep.OUT / filename
        document = json.loads(path.read_text(encoding="utf-8"))
        source_counts[module] = {"file": filename, "sha256": prep.sha256(path), "total": len(document["findings"])}
        for finding in document["findings"]:
            records.append({"module": module, "source_file": filename, **finding})
    non_high = [item for item in records if item["severity"] != "ALTO"]
    selected = {}

    def add(item, reason):
        selected.setdefault(item["subdivision_id"], {"finding": item, "sample_reasons": []})["sample_reasons"].append(reason)

    for item in non_high:
        if item["classification"] == "INDETERMINADA":
            add(item, "ALL_INDETERMINADA_INDIVIDUAL_REVIEW")
        if item["severity"] == "BAIXO":
            add(item, "ALL_BAIXO_INDIVIDUAL_REVIEW")

    for module, _filename in MODULES:
        pool = [item for item in non_high if item["module"] == module and item["subdivision_id"] not in selected]
        module_selected = []
        for classification in ("AUSENTE", "PARCIAL", "INCORRETA"):
            group = sorted((item for item in pool if item["classification"] == classification), key=stable_key)
            take = min(10, len(group))
            for item in group[:take]:
                add(item, f"STRATIFIED_{classification}_MODULE_{module}")
                module_selected.append(item["subdivision_id"])
        remaining = sorted((item for item in pool if item["subdivision_id"] not in selected), key=stable_key)
        for item in remaining[:max(0, 30 - len(module_selected))]:
            add(item, f"HASH_DETERMINISTIC_FILL_MODULE_{module}")

    sample = []
    for position, entry in enumerate(sorted(selected.values(), key=lambda value: value["finding"]["audit_position"]), 1):
        finding = entry["finding"]
        sample.append({
            "sample_position": position,
            "module": finding.pop("module"),
            "source_file": finding.pop("source_file"),
            "sample_reasons": sorted(entry["sample_reasons"]),
            "finding": finding,
            "source_finding_sha256": prep.json_sha(finding),
        })
    document = {
        "schema_version": 1, "mission": "QA-06-FINDINGS-QA", "as_of": prep.AS_OF,
        "status": "DETERMINISTIC_STRATIFIED_SAMPLE_SELECTED",
        "source_modules": source_counts,
        "population": {
            "source_findings": len(records), "high_reviewed_separately": sum(item["severity"] == "ALTO" for item in records),
            "non_high": len(non_high), "low_all_selected": sum(item["severity"] == "BAIXO" for item in non_high),
            "indeterminate_all_selected": sum(item["classification"] == "INDETERMINADA" for item in non_high),
        },
        "sample_total": len(sample),
        "sample_by_module": {module: sum(item["module"] == module for item in sample) for module, _ in MODULES},
        "sample_by_severity": dict(sorted(__import__("collections").Counter(item["finding"]["severity"] for item in sample).items())),
        "sample_by_classification": dict(sorted(__import__("collections").Counter(item["finding"]["classification"] for item in sample).items())),
        "selection_policy": {
            "all_indeterminate": True, "all_low": True,
            "additional_per_module": 30,
            "strata_priority": ["AUSENTE", "PARCIAL", "INCORRETA"],
            "selection_order": "sha256(subdivision_id)",
        },
        "records": sample,
    }
    path = prep.OUT / "QA06_B_NON_HIGH_STRATIFIED_SAMPLE.json"
    prep.write_json(path, document)
    print(json.dumps({"sample_total": len(sample), "by_module": document["sample_by_module"],
                      "by_severity": document["sample_by_severity"],
                      "by_classification": document["sample_by_classification"],
                      "sha256": prep.sha256(path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
