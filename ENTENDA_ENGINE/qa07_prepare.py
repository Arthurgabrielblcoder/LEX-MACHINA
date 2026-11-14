"""Freeze the authoritative QA-07 scope without reconstructing QA-06 queues."""
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
QA06 = HERE / "derived/qa06_subdivision_material_audit"
OUT = HERE / "derived/qa07_high_findings_resolution"
QUEUE = QA06 / "QA06_B_DEFINITIVE_CORRECTION_QUEUE.json"
INDETERMINATE = QA06 / "QA06_B_INDETERMINATE_REVIEW_QUEUE.json"
INVENTORY = QA06 / "QA06_SUBDIVISION_INVENTORY_V2_CORRECTED.json"
AS_OF = "2026-11-13"

PROTECTED = {
    "qa06_corpus": (HERE / "derived/candidate_qa06_cc_001_2046/CC2002_QA06.entenda.jsonl",
                    "4f7481e5ec697eddc26e5e412ff9f5394c983fcfbd5cff6b678bdb7d9811aaf5"),
    "qa06_lookup": (HERE / "derived/candidate_qa06_cc_001_2046/candidate_index/ENTENDA_LOOKUP.IDX",
                    "95fb9a2c076ce0b124b26ae96cb9ff15ac5ed9b5ee2dad6eab8c718299e57e08"),
    "qa06_payload": (HERE / "derived/candidate_qa06_cc_001_2046/candidate_index/ENTENDA_PAYLOAD.DAT",
                     "091f05cdd991771d3366996528a89385735e7c813e14745e54c5db4714a2e26d"),
    "qa06_queue": (QUEUE, "d981890d1fecca4fe0e76eeefb1d6d5d398a336be065ebf7c4998ec2641668f9"),
    "qa06_indeterminate": (INDETERMINATE, "c29f0ae0c252be9a92bc16df90d1208f30d2bdd2c8a8a8deb23f8876035932ad"),
    "qa06_inventory": (INVENTORY, "7fe41b6b6e7755e17174551b56ea684fbbd8a399e95641f7f47e729f55ef5c82"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8", newline="\n")


def build():
    actual = {name: sha(path) for name, (path, _) in PROTECTED.items()}
    expected = {name: expected for name, (_, expected) in PROTECTED.items()}
    if actual != expected:
        raise RuntimeError({"protected_hash_mismatch": {k: (expected[k], actual[k]) for k in expected if expected[k] != actual[k]}})
    queue = load(QUEUE)
    indeterminate = load(INDETERMINATE)
    high = [row for row in queue["findings"] if row["final_severity"] == "ALTO"]
    medium = [row for row in queue["findings"] if row["final_severity"] == "MÉDIO"]
    if (len(high), len(medium), len(indeterminate["findings"])) != (41, 420, 10):
        raise RuntimeError("QA-07 source cardinality mismatch")
    if len({row["finding_id"] for row in high + medium + indeterminate["findings"]}) != 471:
        raise RuntimeError("duplicate finding id across QA-07 source queues")
    scope = {
        "schema_version": 1, "mission": "QA-07", "as_of": AS_OF,
        "status": "AUTHORITATIVE_SCOPE_FROZEN", "source_queue_sha256": actual["qa06_queue"],
        "source_indeterminate_sha256": actual["qa06_indeterminate"],
        "source_inventory_sha256": actual["qa06_inventory"],
        "high_total": 41, "high_target_total": len({r["target_id"] for r in high}),
        "high_groups": {"A": high[:21], "B": high[21:]},
        "indeterminate_total": 10, "indeterminate": indeterminate["findings"],
        "medium_total_preserved": 420,
    }
    preservation = {
        "schema_version": 1, "mission": "QA-07", "as_of": AS_OF,
        "status": "PRESERVED_PENDING_UNMODIFIED", "total": 420,
        "source_queue": QUEUE.name, "source_queue_sha256": actual["qa06_queue"],
        "finding_ids_sha256": hashlib.sha256("\n".join(r["finding_id"] for r in medium).encode()).hexdigest(),
        "target_total": len({r["target_id"] for r in medium}),
        "classification_counts": dict(sorted(Counter(r["final_classification"] for r in medium).items())),
        "findings": medium, "editorial_changes_authorized": False,
        "corpus_modified": False, "human_approval_claimed": False,
    }
    scope_path = OUT / "QA07_AUTHORIZED_SCOPE.json"
    preservation_path = OUT / "QA07_MEDIUM_420_PRESERVATION_MANIFEST.json"
    write(scope_path, scope)
    write(preservation_path, preservation)
    cp = {
        "schema_version": 1, "mission": "QA-07", "checkpoint": "CP01", "as_of": AS_OF,
        "status": "INVENTORY_AND_INTEGRITY_COMPLETE", "branch_base_head": "74775b2b5db692c2886a6a3d3d6b772bfb89ba14",
        "protected_sha256": actual, "scope_sha256": sha(scope_path),
        "medium_preservation_sha256": sha(preservation_path),
        "high": 41, "high_targets": scope["high_target_total"], "indeterminate": 10, "medium_preserved": 420,
        "production_index_modified": False, "deployed": False,
    }
    write(OUT / "QA07_CP01.json", cp)
    print(json.dumps({"high": 41, "high_targets": scope["high_target_total"],
                      "indeterminate": 10, "medium": 420,
                      "scope_sha256": sha(scope_path)}, ensure_ascii=False))


if __name__ == "__main__":
    build()
