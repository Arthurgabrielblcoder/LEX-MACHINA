"""Validate and freeze the protected QA-05 correction baseline."""
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "derived/qa05_final_corrections"
QA04_OUT = HERE / "derived/qa04_final_audit"
QA04_DIR = HERE / "derived/candidate_qa04_cc_001_2046"
CORPUS = QA04_DIR / "CC2002_QA04.entenda.jsonl"
LOOKUP = QA04_DIR / "candidate_index/ENTENDA_LOOKUP.IDX"
PAYLOAD = QA04_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT"
QUEUE = QA04_OUT / "QA04_CORRECTION_QUEUE_50.json"
QA03_CORPUS = HERE / "derived/candidate_qa03_cc_001_2046/CC2002_QA03.entenda.jsonl"
CC13_CORPUS = HERE / "derived/candidate_cc_001_2046/CC2002_CC13.entenda.jsonl"
AS_OF = "2026-11-13"
FIELDS = ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis")
PROTECTED = {
    "qa04_corpus": "70a6232437f77e2a0d48e39f1a00dd5ec7e753b39a6d1663c9e34b0742e5e524",
    "qa04_lookup": "b677aa36772dc6d32662a00e26587d517f916bd428e70f3526eb083c29d0b17f",
    "qa04_payload": "756ce344c834730b3e0f2696ef5ce3823d484a7c8ce20254b779cb9a2febde59",
    "qa04_queue": "cceac77f6357ca81dae1653a2812dfc8d607dc8e3833ffecd6ae9955f3759310",
    "qa03_corpus": "dad0a9414fd42b4e5c348ab7e87b90b99501ae4b77c950c5cbfd7dbaef58a496",
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
    return {"qa04_corpus": sha256(CORPUS), "qa04_lookup": sha256(LOOKUP),
            "qa04_payload": sha256(PAYLOAD), "qa04_queue": sha256(QUEUE),
            "qa03_corpus": sha256(QA03_CORPUS), "cc13_corpus": sha256(CC13_CORPUS)}


def main():
    if current_hashes() != PROTECTED:
        raise RuntimeError("protected QA-04/QA-03/CC-13 hash mismatch")
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    findings = queue["findings"]
    if queue["total"] != 50 or len(findings) != 50 or len({row["target_id"] for row in findings}) != 50:
        raise RuntimeError("unexpected correction queue cardinality")
    if Counter(row["severity"] for row in findings) != Counter({"CRÍTICO": 2, "ALTO": 31, "MÉDIO": 17}):
        raise RuntimeError("unexpected severity counts")
    corpus = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line]
    active = {row["target_id"]: row for row in corpus if row["status"] == "ACTIVE"}
    if (len(corpus), len(active)) != (2262, 2017):
        raise RuntimeError("unexpected QA-04 corpus cardinality")
    records = []
    for position, finding in enumerate(findings, 1):
        old = active[finding["target_id"]]
        records.append({
            "correction_position": position,
            "target_id": finding["target_id"],
            "severity": finding["severity"],
            "finding": finding,
            "finding_sha256": json_sha(finding),
            "baseline_explanation_id": old["explanation_id"],
            "baseline_editorial_version": old["editorial_version"],
            "baseline_content_sha256": json_sha(old["content"]),
            "baseline_source_snapshot_sha256": old["source"]["source_text_sha256"],
        })
    inventory = {
        "schema_version": 1, "mission": "QA-05", "as_of": AS_OF,
        "status": "PENDING_EDITORIAL_CORRECTION_AND_INDEPENDENT_REVALIDATION",
        "source": QUEUE.name, "source_sha256": PROTECTED["qa04_queue"],
        "total": 50, "severity_counts": dict(sorted(Counter(row["severity"] for row in findings).items())),
        "records": records,
    }
    write_json(OUT / "QA05_CORRECTION_INVENTORY_50.json", inventory)
    checkpoint = {
        "schema_version": 1, "mission": "QA-05", "checkpoint": "CP01", "as_of": AS_OF,
        "status": "COMPLETE", "protected_sha256": PROTECTED,
        "counts": {"versions": 2262, "active": 2017, "historical": 245,
                   "previous_corrections_revalidated": 82, "pending_findings": 50},
        "artifact_sha256": {"QA05_CORRECTION_INVENTORY_50.json": sha256(OUT / "QA05_CORRECTION_INVENTORY_50.json")},
    }
    write_json(OUT / "QA05_CHECKPOINT_01.json", checkpoint)
    print(json.dumps({"total": 50, "severity": inventory["severity_counts"],
                      "critical": [row["target_id"] for row in findings if row["severity"] == "CRÍTICO"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
