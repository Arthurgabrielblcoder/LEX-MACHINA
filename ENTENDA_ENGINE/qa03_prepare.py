"""Prepare deterministic QA-03 correction and independent-audit inventories."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "derived/qa03_corrections_and_audit"
QA02 = HERE / "derived/qa02_independent_legal_audit"
CORPUS = HERE / "derived/candidate_cc_001_2046/CC2002_CC13.entenda.jsonl"
LOOKUP = HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_LOOKUP.IDX"
PAYLOAD = HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_PAYLOAD.DAT"
CORRECTIONS = QA02 / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_04.json"
AS_OF = "2026-11-13"
PROTECTED = {
    "corpus": "b9fa2d39b6b4292fe2be466427871e75e14b2a327fb0c35ae190d5443cfd5c8c",
    "lookup": "60f1de336f2f9ecbc5e671d0a6a9223cf20e47ab5826a5501b53f9a67551866e",
    "payload": "9fb3f3a1b6f1c1926eda0818fc753f2d0348194cf25b0a333fc6fa18c48222cb",
    "qa02_corrections": "0d8cce6b3b9c335e7f71502b88c81488ae53732a7927708f2f83701504896e6b",
}
ARTICLE_RE = re.compile(r"^CC2002:ART\.(\d+)(?:-([A-Z]+))?(?::(.+))?$")
FIELDS = ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_sha(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def article_key(target_id):
    match = ARTICLE_RE.fullmatch(target_id)
    if not match:
        raise ValueError(f"unsupported target id: {target_id}")
    number, suffix, subdivision = match.groups()
    return int(number), (0, "") if suffix is None else (1, suffix), subdivision or ""


def book_for(target_id):
    number = article_key(target_id)[0]
    if number <= 232:
        return "PARTE_GERAL"
    if number <= 965:
        return "OBRIGACOES_E_CONTRATOS"
    if number <= 1195:
        return "EMPRESA"
    if number <= 1510:
        return "DIREITOS_REAIS"
    if number <= 1783:
        return "FAMILIA"
    if number <= 2027:
        return "SUCESSOES"
    return "COMPLEMENTARES_E_FINAIS"


def current_hashes():
    return {
        "corpus": sha256(CORPUS),
        "lookup": sha256(LOOKUP),
        "payload": sha256(PAYLOAD),
        "qa02_corrections": sha256(CORRECTIONS),
    }


def main():
    if current_hashes() != PROTECTED:
        raise RuntimeError("protected QA-02 baseline hash mismatch")
    rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines()]
    active = {row["target_id"]: row for row in rows if row["status"] == "ACTIVE"}
    if len(active) != 2017 or len(rows) != 2180:
        raise RuntimeError("unexpected CC-13 corpus cardinality")

    audited = set()
    for wave in range(1, 5):
        audit = json.loads((QA02 / f"QA02_AUDIT_WAVE_{wave:02d}.json").read_text(encoding="utf-8"))
        audited.update(record["target_id"] for record in audit["records"])
    if len(audited) != 629 or not audited <= set(active):
        raise RuntimeError("unexpected QA-02 audited universe")

    remaining_ids = sorted(set(active) - audited, key=article_key)
    if len(remaining_ids) != 1388:
        raise RuntimeError("unexpected unaudited universe")
    records = []
    for position, target in enumerate(remaining_ids, 1):
        row = active[target]
        records.append({
            "queue_position": position,
            "target_id": target,
            "explanation_id": row["explanation_id"],
            "book": book_for(target),
            "origin_mission": row["authoring"]["mission"],
            "baseline_field_sha256": {field: json_sha(row["content"][field]) for field in FIELDS},
        })

    full_queue = {
        "schema_version": 1,
        "mission": "QA-03",
        "as_of": AS_OF,
        "status": "UNAUDITED_ACTIVE_BASELINE_QUEUE",
        "ordering": "numeric article number ascending; base article before alphabetic intercalated suffix; suffix lexicographic",
        "baseline_sha256": PROTECTED,
        "active_total": len(active),
        "previously_audited_unique": len(audited),
        "total": len(records),
        "records": records,
    }
    write_json(OUT / "QA03_UNAUDITED_FULL_QUEUE.json", full_queue)
    full_hash = sha256(OUT / "QA03_UNAUDITED_FULL_QUEUE.json")

    selected = {
        "schema_version": 1,
        "mission": "QA-03-FRONT-B",
        "as_of": AS_OF,
        "status": "SELECTED_FOR_INDEPENDENT_AUDIT",
        "source": "QA03_UNAUDITED_FULL_QUEUE.json",
        "source_sha256": full_hash,
        "selection_rule": "first 388 records in the persisted canonical queue",
        "total": 388,
        "records": records[:388],
    }
    write_json(OUT / "QA03_AUDIT_388_QUEUE.json", selected)
    remaining = {
        "schema_version": 1,
        "mission": "QA-03-FRONT-B",
        "as_of": AS_OF,
        "status": "PENDING_INDEPENDENT_AUDIT_AFTER_QA03",
        "source": "QA03_UNAUDITED_FULL_QUEUE.json",
        "source_sha256": full_hash,
        "completed_queue_positions": [1, 388],
        "next_queue_position": 389,
        "total": 1000,
        "records": records[388:],
    }
    write_json(OUT / "QA03_UNAUDITED_REMAINING_1000.json", remaining)

    prior = json.loads(CORRECTIONS.read_text(encoding="utf-8"))
    findings = []
    for wave in range(1, 5):
        for finding in prior[f"wave_{wave:02d}_findings"]:
            findings.append({"source_wave": wave, **finding})
    if len(findings) != 78 or Counter(item["severity"] for item in findings) != Counter({"ALTO": 51, "MÉDIO": 23, "CRÍTICO": 4}):
        raise RuntimeError("unexpected correction inventory")
    correction_inventory = {
        "schema_version": 1,
        "mission": "QA-03-FRONT-A",
        "as_of": AS_OF,
        "status": "PENDING_EDITORIAL_CORRECTION_AND_INDEPENDENT_REVALIDATION",
        "source": CORRECTIONS.name,
        "source_sha256": PROTECTED["qa02_corrections"],
        "total": len(findings),
        "unique_targets": len({item["target_id"] for item in findings}),
        "severity_counts": dict(sorted(Counter(item["severity"] for item in findings).items())),
        "findings": findings,
    }
    write_json(OUT / "QA03_CORRECTION_INVENTORY.json", correction_inventory)
    inventory = {
        "schema_version": 1,
        "mission": "QA-03",
        "checkpoint": "A-CP01",
        "as_of": AS_OF,
        "status": "COMPLETE",
        "protected_sha256": PROTECTED,
        "counts": {
            "active": len(active), "versions": len(rows), "historical": len(rows) - len(active),
            "qa02_unique_audited": len(audited), "unaudited": len(records),
            "selected_for_qa03": 388, "remaining_after_qa03": 1000,
            "known_findings": len(findings),
        },
        "artifact_sha256": {
            "QA03_UNAUDITED_FULL_QUEUE.json": full_hash,
            "QA03_AUDIT_388_QUEUE.json": sha256(OUT / "QA03_AUDIT_388_QUEUE.json"),
            "QA03_UNAUDITED_REMAINING_1000.json": sha256(OUT / "QA03_UNAUDITED_REMAINING_1000.json"),
            "QA03_CORRECTION_INVENTORY.json": sha256(OUT / "QA03_CORRECTION_INVENTORY.json"),
        },
    }
    write_json(OUT / "QA03_A_CP01_INVENTORY.json", inventory)
    print(json.dumps({
        "known_findings": len(findings), "full_unaudited": len(records), "selected": 388,
        "remaining": 1000, "selected_first": records[0]["target_id"],
        "selected_last": records[387]["target_id"], "remaining_first": records[388]["target_id"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
