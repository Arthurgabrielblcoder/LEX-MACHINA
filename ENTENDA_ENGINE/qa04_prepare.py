"""Validate and freeze the protected QA-04 baseline and exact work queues."""
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "derived/qa04_final_audit"
QA03_OUT = HERE / "derived/qa03_corrections_and_audit"
QA03_DIR = HERE / "derived/candidate_qa03_cc_001_2046"
CORPUS = QA03_DIR / "CC2002_QA03.entenda.jsonl"
LOOKUP = QA03_DIR / "candidate_index/ENTENDA_LOOKUP.IDX"
PAYLOAD = QA03_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT"
FINDINGS = QA03_OUT / "QA03_B_NEW_FINDINGS.json"
QUEUE = QA03_OUT / "QA03_UNAUDITED_REMAINING_1000.json"
CC13 = HERE / "derived/candidate_cc_001_2046/CC2002_CC13.entenda.jsonl"
AS_OF = "2026-11-13"
FIELDS = ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis")
PROTECTED = {
    "qa03_corpus": "dad0a9414fd42b4e5c348ab7e87b90b99501ae4b77c950c5cbfd7dbaef58a496",
    "qa03_lookup": "9cda2855e4534b7a7cefc833f2e2498a91cf81666395cf83a064d3d69705eeba",
    "qa03_payload": "6a5ea56bffc14c06df9ac1f16c145b02e2115bacbfce1d87858ba342e77d6268",
    "qa03_findings": "4fd7700b9c66c370405a8ce7d9004222a9af2202efa4cabf4c0a2ff581062ba1",
    "qa03_remaining_queue": "8c798f79745f4d878b882e582bbfa71effbcb6c99c7763bf77cfc51e2b5151df",
    "cc13_corpus": "b9fa2d39b6b4292fe2be466427871e75e14b2a327fb0c35ae190d5443cfd5c8c",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_sha(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def current_hashes():
    return {
        "qa03_corpus": sha256(CORPUS),
        "qa03_lookup": sha256(LOOKUP),
        "qa03_payload": sha256(PAYLOAD),
        "qa03_findings": sha256(FINDINGS),
        "qa03_remaining_queue": sha256(QUEUE),
        "cc13_corpus": sha256(CC13),
    }


def main():
    if current_hashes() != PROTECTED:
        raise RuntimeError("protected QA-03/CC-13 hash mismatch")
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    findings = json.loads(FINDINGS.read_text(encoding="utf-8"))["findings"]
    corpus = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line]
    active = {row["target_id"]: row for row in corpus if row["status"] == "ACTIVE"}
    if (len(corpus), len(active)) != (2258, 2017):
        raise RuntimeError("unexpected QA-03 corpus cardinality")
    records = queue["records"]
    if len(records) != 1000 or len({row["target_id"] for row in records}) != 1000:
        raise RuntimeError("residual queue cardinality mismatch")
    if (records[0]["queue_position"], records[0]["target_id"]) != (389, "CC2002:ART.518"):
        raise RuntimeError("unexpected first residual record")
    if (records[-1]["queue_position"], records[-1]["target_id"]) != (1388, "CC2002:ART.2025"):
        raise RuntimeError("unexpected last residual record")
    for record in records:
        row = active[record["target_id"]]
        actual = {field: json_sha(row["content"][field]) for field in FIELDS}
        if actual != record["baseline_field_sha256"]:
            raise RuntimeError(f"field hash mismatch: {record['target_id']}")
    expected_findings = {
        "CC2002:ART.228": "ALTO", "CC2002:ART.288": "MÉDIO",
        "CC2002:ART.371": "ALTO", "CC2002:ART.500": "ALTO",
    }
    if {row["target_id"]: row["severity"] for row in findings} != expected_findings:
        raise RuntimeError("unexpected QA-03 pending findings")

    correction_inventory = {
        "schema_version": 1, "mission": "QA-04-FRONT-A", "as_of": AS_OF,
        "status": "PENDING_EDITORIAL_CORRECTION_AND_INDEPENDENT_REVALIDATION",
        "source": "QA03_B_NEW_FINDINGS.json", "source_sha256": PROTECTED["qa03_findings"],
        "total": 4, "findings": findings,
    }
    write_json(OUT / "QA04_CORRECTION_INVENTORY_4.json", correction_inventory)
    audit_queue = {
        "schema_version": 1, "mission": "QA-04-FRONT-B", "as_of": AS_OF,
        "status": "FROZEN_EXACT_RESIDUAL_QUEUE", "source": "QA03_UNAUDITED_REMAINING_1000.json",
        "source_sha256": PROTECTED["qa03_remaining_queue"], "total": 1000,
        "residual_positions": [1, 1000], "original_queue_positions": [389, 1388],
        "records": records,
    }
    write_json(OUT / "QA04_AUDIT_1000_QUEUE.json", audit_queue)
    inventory = {
        "schema_version": 1, "mission": "QA-04", "checkpoint": "PREP-CP01", "as_of": AS_OF,
        "status": "COMPLETE", "protected_sha256": PROTECTED,
        "counts": {"versions": 2258, "active": 2017, "historical": 241,
                   "previously_audited": 1017, "selected": 1000, "pending_findings": 4},
        "artifact_sha256": {
            "QA04_CORRECTION_INVENTORY_4.json": sha256(OUT / "QA04_CORRECTION_INVENTORY_4.json"),
            "QA04_AUDIT_1000_QUEUE.json": sha256(OUT / "QA04_AUDIT_1000_QUEUE.json"),
        },
    }
    write_json(OUT / "QA04_PREPARATION_CHECKPOINT.json", inventory)
    print(json.dumps({"findings": 4, "queue": 1000, "first": records[0]["target_id"],
                      "last": records[-1]["target_id"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
