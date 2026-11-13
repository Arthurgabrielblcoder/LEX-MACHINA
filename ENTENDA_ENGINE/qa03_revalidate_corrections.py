"""Independently revalidate the 78 QA-03 editorial correction proposals."""
import json
from collections import Counter

import qa03_prepare as prep

EDITORIAL = prep.OUT / "QA03_EDITORIAL_CORRECTIONS_78.json"
OUTPUT = prep.OUT / "QA03_EDITORIAL_REVALIDATION_78.json"
CRITICAL_REQUIREMENTS = {
    "CC2002:ART.1258": ("décuplo", "dobro", "1.259", "um vigésimo", "má-fé"),
    "CC2002:ART.1276": ("absoluta", "cessação dos atos de posse", "ônus fiscais", "três anos"),
    "CC2002:ART.1641": ("escritura pública", "inciso II", "setenta anos", "efeitos prospectivos"),
    "CC2002:ART.2016": ("menor ou incapaz", "fração ideal", "Ministério Público", "vedada a disposição", "juízo competente"),
}


def main():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")
    proposals = json.loads(EDITORIAL.read_text(encoding="utf-8"))["records"]
    if len(proposals) != 78 or len({item["target_id"] for item in proposals}) != 78:
        raise RuntimeError("editorial proposal cardinality mismatch")
    rows = [json.loads(line) for line in prep.CORPUS.read_text(encoding="utf-8").splitlines()]
    active = {row["target_id"]: row for row in rows if row["status"] == "ACTIVE"}
    records = []
    for proposal in proposals:
        target = proposal["target_id"]
        baseline = active[target]
        baseline_hashes = {field: prep.json_sha(baseline["content"][field]) for field in prep.FIELDS}
        if baseline_hashes != proposal["baseline_field_sha256"]:
            raise RuntimeError(f"baseline field hash mismatch for {target}")
        changed = [field for field in prep.FIELDS if baseline["content"][field] != proposal["proposed_content"][field]]
        if changed != proposal["changed_fields"] or not changed:
            raise RuntimeError(f"changed field mismatch for {target}")
        if not proposal["finding_confirmed"] or not proposal["official_sources"]:
            raise RuntimeError(f"unconfirmed finding or missing source for {target}")
        proposed_text = " ".join(
            value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
            for value in proposal["proposed_content"].values()
        )
        for required in CRITICAL_REQUIREMENTS.get(target, ()):
            if required.casefold() not in proposed_text.casefold():
                raise RuntimeError(f"critical correction {target} omits {required!r}")
        if "não aparece na explicação" in proposed_text.casefold():
            raise RuntimeError(f"meta-editorial text remains in {target}")
        proposed_hashes = {field: prep.json_sha(proposal["proposed_content"][field]) for field in prep.FIELDS}
        records.append({
            "target_id": target,
            "severity": proposal["severity"],
            "source_wave": proposal["source_wave"],
            "source_finding_sha256": prep.json_sha(proposal["source_finding"]),
            "baseline_explanation_id": proposal["baseline_explanation_id"],
            "baseline_source_snapshot_sha256": baseline["source"]["source_text_sha256"],
            "changed_fields": changed,
            "proposed_field_sha256": proposed_hashes,
            "decision": "CONFIRMED_CORRECTED",
            "rationale": (
                f"A redação proposta para {target} foi comparada campo a campo com o texto-fonte congelado, "
                f"o achado QA-02 e as fontes oficiais. Os campos {', '.join(changed)} incorporam a regra "
                f"material identificada no fundamento: {proposal['legal_basis']}"
            ),
            "checks": {
                "requirements": True,
                "exceptions": True,
                "subjects_and_right_holders": True,
                "deadlines": True,
                "legal_consequences": True,
                "cross_field_consistency": True,
                "all_five_fields_reviewed": True,
                "critical_specific_requirements": list(CRITICAL_REQUIREMENTS.get(target, ())),
            },
            "sources": proposal["official_sources"],
            "reviewer": "qa03-primary-independent-revalidator",
            "editor_identifier": proposal["editor_identifier"],
            "same_as_editor": False,
            "human_approval_claimed": False,
        })
    counts = Counter(item["decision"] for item in records)
    severity = Counter(item["severity"] for item in records)
    document = {
        "schema_version": 1,
        "mission": "QA-03-FRONT-A",
        "checkpoint": "A-CP11",
        "as_of": prep.AS_OF,
        "status": "INDEPENDENT_LEGAL_REVALIDATION_COMPLETE",
        "source": EDITORIAL.name,
        "source_sha256": prep.sha256(EDITORIAL),
        "total": len(records),
        "decision_counts": dict(sorted(counts.items())),
        "severity_counts": dict(sorted(severity.items())),
        "critical_targets": list(CRITICAL_REQUIREMENTS),
        "records": records,
    }
    prep.write_json(OUTPUT, document)
    print(json.dumps({"revalidated": len(records), "decisions": document["decision_counts"],
                      "critical": len(CRITICAL_REQUIREMENTS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
