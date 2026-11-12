"""Build the deterministic QA-02 wave-one consolidation and exact continuation queue."""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "derived/qa02_independent_legal_audit"
INVENTORY = OUT / "QA02_RISK_INVENTORY.json"
AUDIT = OUT / "QA02_AUDIT_WAVE_01.json"
AS_OF = "2026-11-12"
BOOKS = (
    ("PARTE_GERAL", 1, 232), ("OBRIGACOES_E_CONTRATOS", 233, 965),
    ("EMPRESA", 966, 1195), ("DIREITOS_REAIS", 1196, 1510),
    ("FAMILIA", 1511, 1783), ("SUCESSOES", 1784, 2027),
    ("COMPLEMENTARES_E_FINAIS", 2028, 2046),
)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def book(target_id):
    number = int(target_id.split("ART.", 1)[1].split("-", 1)[0])
    return next(name for name, lo, hi in BOOKS if lo <= number <= hi)


def main():
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    audited_priority = {r["target_id"] for r in audit["records"] if "B_OR_CORRECTION_WAVE" in r["audit_groups"]}
    priority_records = inventory["priority_b_or_substantive_correction"]["records"]
    pending_records = [r for r in priority_records if r["target_id"] not in audited_priority]
    pending = {
        "schema_version": 1,
        "mission": "QA-02",
        "as_of": AS_OF,
        "status": "PENDING_INDEPENDENT_LEGAL_AUDIT",
        "selection_rule": "priority_b_or_substantive_correction minus QA02 wave-one priority targets",
        "total": len(pending_records),
        "resume_instruction": "Continue at checkpoint 08 in deterministic batches, preserving this order and recording individual independent legal evidence before any conclusion.",
        "records": pending_records,
    }
    write_json(OUT / "QA02_PENDING_PRIORITY_WAVE_02.json", pending)

    findings = [r["finding"] for r in audit["records"] if r["finding"]]
    sentinel_results = {
        target: next(r["result"] for r in audit["records"] if r["target_id"] == target)
        for target in inventory["mandatory_sentinels"]
    }
    artifacts = [
        "QA02_RISK_INVENTORY.json",
        *[f"QA02_CHECKPOINT_{n:02d}.json" for n in range(2, 7)],
        "QA02_AUDIT_WAVE_01.json",
        "QA02_CORRECTION_QUEUE.json",
        "QA02_PENDING_PRIORITY_WAVE_02.json",
    ]
    corpus = inventory["corpus"]
    consolidation = {
        "schema_version": 1,
        "mission": "QA-02",
        "checkpoint": 7,
        "as_of": AS_OF,
        "status": "PARTIAL_REQUIRES_CONTINUATION",
        "scope_statement": "Wave one is complete and reproducible; QA-02 as a whole is not complete because the full priority universe was not audited.",
        "corpus": corpus,
        "coverage": {
            "priority_total": inventory["priority_b_or_substantive_correction"]["total"],
            "priority_audited": len(audited_priority),
            "priority_pending": len(pending_records),
            "a_universe": inventory["stratified_a_sample"]["universe"],
            "a_sample_audited": len(inventory["stratified_a_sample"]["records"]),
            "unique_targets_audited": audit["audited_total"],
            "audited_by_book": dict(sorted(Counter(book(r["target_id"]) for r in audit["records"]).items())),
            "audited_by_group": dict(sorted(Counter(group for r in audit["records"] for group in r["audit_groups"]).items())),
            "audited_by_thematic_checkpoint": {
                f"QA02_CHECKPOINT_{n:02d}": json.loads((OUT / f"QA02_CHECKPOINT_{n:02d}.json").read_text(encoding="utf-8"))["examined"]
                for n in range(2, 7)
            },
        },
        "findings": {
            "total": len(findings),
            "by_severity": dict(sorted(Counter(f["severity"] for f in findings).items())),
            "target_ids": [f["target_id"] for f in findings],
        },
        "mandatory_sentinels": sentinel_results,
        "insurance_757_802": inventory["insurance_757_802"],
        "tests": {
            "qa02_specific": {"tests_run": 12, "result": "OK"},
            "global_suite": {"tests_run": 405, "result": "OK", "skipped": 2},
            "environment_note": "The first sandboxed global run had 27 temporary-directory permission errors; rerun with TEMP/TMP inside the writable worktree passed without failures.",
        },
        "protected_sha256": {
            "corpus": corpus["sha256"],
            "lookup": "60f1de336f2f9ecbc5e671d0a6a9223cf20e47ab5826a5501b53f9a67551866e",
            "payload": "9fb3f3a1b6f1c1926eda0818fc753f2d0348194cf25b0a333fc6fa18c48222cb",
        },
        "immutability": {
            "editorial_corpus_changed": False,
            "production_indexes_changed": False,
            "deploy_performed": False,
        },
        "continuation": {
            "next_checkpoint": 8,
            "queue": "QA02_PENDING_PRIORITY_WAVE_02.json",
            "queue_sha256": sha256(OUT / "QA02_PENDING_PRIORITY_WAVE_02.json"),
            "instruction": pending["resume_instruction"],
        },
        "artifact_sha256": {name: sha256(OUT / name) for name in artifacts},
    }
    write_json(OUT / "QA02_CONSOLIDATION.json", consolidation)
    print(json.dumps({"audited": audit["audited_total"], "findings": len(findings), "pending": len(pending_records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
