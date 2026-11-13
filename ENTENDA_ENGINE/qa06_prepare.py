"""Build the deterministic QA-06 active-target and subdivision inventory."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import qa03_prepare as old_prep


HERE = Path(__file__).resolve().parent
OUT = HERE / "derived/qa06_subdivision_material_audit"
QA05_OUT = HERE / "derived/qa05_final_corrections"
QA05_DIR = HERE / "derived/candidate_qa05_cc_001_2046"
CORPUS = QA05_DIR / "CC2002_QA05.entenda.jsonl"
LOOKUP = QA05_DIR / "candidate_index/ENTENDA_LOOKUP.IDX"
PAYLOAD = QA05_DIR / "candidate_index/ENTENDA_PAYLOAD.DAT"
FINDING = QA05_OUT / "QA05_NEW_FINDINGS_CROSS_AUDIT.json"
QA04_CORPUS = HERE / "derived/candidate_qa04_cc_001_2046/CC2002_QA04.entenda.jsonl"
QA03_CORPUS = HERE / "derived/candidate_qa03_cc_001_2046/CC2002_QA03.entenda.jsonl"
CC13_CORPUS = HERE / "derived/candidate_cc_001_2046/CC2002_CC13.entenda.jsonl"
AS_OF = "2026-11-13"
FIELDS = ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis")
PROTECTED = {
    "qa05_corpus": "2bf21e8333b584130a3159a240a96d5225958a53821971a184285ecc222a082f",
    "qa05_lookup": "0bf8c5ce3da6fa8b7065f4c05f34bfa3350b29d77d026c6c628a9b6757dd700c",
    "qa05_payload": "fdae31938907a93807cbadaa5667cd0131ededc484132db62173afbb663e13ce",
    "qa05_finding": "bb40c4ab9910ffa6d32616d9e723fd0bd3dd0c1b574d089e9364f5c4577c8ec6",
    "qa04_corpus": "70a6232437f77e2a0d48e39f1a00dd5ec7e753b39a6d1663c9e34b0742e5e524",
    "qa03_corpus": "dad0a9414fd42b4e5c348ab7e87b90b99501ae4b77c950c5cbfd7dbaef58a496",
    "cc13_corpus": "b9fa2d39b6b4292fe2be466427871e75e14b2a327fb0c35ae190d5443cfd5c8c",
}
# The source snapshots sometimes append an all-uppercase structural heading to
# the final segment of the preceding article.  Keep this match case-sensitive:
# title-case occurrences (for example, "Título X do Livro III") are legal
# remissions inside the provision and must never be stripped as headings.
HEADING_RE = re.compile(r"\s+(?P<kind>SUBT[IÍ]TULO|T[IÍ]TULO)\s+(?P<number>[IVXLCDM]+)\s+(?P<name>[^\n]+)$")
REMISSION_RE = re.compile(r"\b(?:art(?:igo)?s?\.?|§)\s*[\d.]+(?:-[A-Z]+)?(?:\s*,?\s*(?:§|inciso)\s*[\wº°.-]+)?", re.I)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_sha(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def current_hashes():
    return {"qa05_corpus": sha256(CORPUS), "qa05_lookup": sha256(LOOKUP),
            "qa05_payload": sha256(PAYLOAD), "qa05_finding": sha256(FINDING),
            "qa04_corpus": sha256(QA04_CORPUS), "qa03_corpus": sha256(QA03_CORPUS),
            "cc13_corpus": sha256(CC13_CORPUS)}


def segment_kind(segment_id):
    tail = segment_id.split(":")[-1]
    if tail == "CAPUT":
        return "CAPUT"
    if tail.startswith("PAR."):
        return "PARAGRAFO"
    if tail.startswith("INC."):
        return "INCISO"
    if tail.startswith("AL."):
        return "ALINEA"
    if tail.startswith("ITEM."):
        return "ITEM"
    return "OUTRO"


def main():
    if current_hashes() != PROTECTED:
        raise RuntimeError("protected QA-05 and historical baseline hash mismatch")
    rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line]
    active = sorted((row for row in rows if row["status"] == "ACTIVE"),
                    key=lambda row: old_prep.article_key(row["target_id"]))
    if len(rows) != 2312 or len(active) != 2017:
        raise RuntimeError("unexpected QA-05 corpus cardinality")

    current_title = "TÍTULO I — DAS PESSOAS NATURAIS"
    records = []
    segment_status = Counter()
    kind_counts = Counter()
    for position, row in enumerate(active, 1):
        title = current_title
        raw_segments = []
        next_title = None
        for line in row["source"]["source_text_snapshot"].splitlines():
            if "\t" not in line:
                continue
            segment_id, text = line.split("\t", 1)
            heading = HEADING_RE.search(text)
            if heading:
                next_title = f"{heading.group('kind').upper()} {heading.group('number')} — {heading.group('name').strip()}"
                text = text[:heading.start()].rstrip()
            lowered = text.casefold()
            status = "EXCLUDED_REVOKED_OR_VETOED" if ("revogad" in lowered or "vetado" in lowered) else "ACTIVE"
            material = status == "ACTIVE" and bool(text.strip())
            kind = segment_kind(segment_id)
            raw_segments.append({
                "subdivision_id": segment_id,
                "kind": kind,
                "text": text,
                "status": status,
                "material_audit_required": material,
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "express_remissions": sorted(set(REMISSION_RE.findall(text))),
            })
            segment_status[status] += 1
            kind_counts[kind] += 1
        if not raw_segments:
            raise RuntimeError(f"no structural segments: {row['target_id']}")
        records.append({
            "audit_position": position,
            "target_id": row["target_id"],
            "explanation_id": row["explanation_id"],
            "article": row["target_id"].split(":")[1],
            "book": old_prep.book_for(row["target_id"]),
            "title": title,
            "validity": row["validity"]["target_status"],
            "source_text_sha256": row["source"]["source_text_sha256"],
            "content_sha256": json_sha(row["content"]),
            "subdivision_total": len(raw_segments),
            "subdivision_auditable": sum(segment["material_audit_required"] for segment in raw_segments),
            "subdivisions": raw_segments,
        })
        if next_title:
            current_title = next_title

    inventory = {
        "schema_version": 1, "mission": "QA-06-FRONT-B", "as_of": AS_OF,
        "status": "FROZEN_ACTIVE_SUBDIVISION_INVENTORY", "source": str(CORPUS.relative_to(HERE)).replace("\\", "/"),
        "source_sha256": PROTECTED["qa05_corpus"], "active_targets": 2017,
        "subdivisions_total": sum(row["subdivision_total"] for row in records),
        "subdivisions_auditable": sum(row["subdivision_auditable"] for row in records),
        "subdivision_status_counts": dict(sorted(segment_status.items())),
        "subdivision_kind_counts": dict(sorted(kind_counts.items())),
        "ordering": "canonical numeric article order, base before intercalated suffix, then granular suffix",
        "records": records,
    }
    write_json(OUT / "QA06_SUBDIVISION_INVENTORY.json", inventory)
    queue = {
        "schema_version": 1, "mission": "QA-06-FRONT-B", "as_of": AS_OF,
        "status": "SELECTED_ALL_ACTIVE_TARGETS", "source": "QA06_SUBDIVISION_INVENTORY.json",
        "source_sha256": sha256(OUT / "QA06_SUBDIVISION_INVENTORY.json"),
        "total": 2017, "checkpoint_size": 50, "checkpoint_total": 41, "records": records,
    }
    write_json(OUT / "QA06_AUDIT_QUEUE_2017.json", queue)
    checkpoint = {
        "schema_version": 1, "mission": "QA-06", "checkpoint": "PREP-CP01", "as_of": AS_OF,
        "status": "COMPLETE", "protected_sha256": PROTECTED,
        "counts": {"versions": 2312, "active": 2017, "historical": 295,
                   "subdivisions_total": inventory["subdivisions_total"],
                   "subdivisions_auditable": inventory["subdivisions_auditable"],
                   "material_checkpoints": 41},
        "artifact_sha256": {"QA06_SUBDIVISION_INVENTORY.json": sha256(OUT / "QA06_SUBDIVISION_INVENTORY.json"),
                            "QA06_AUDIT_QUEUE_2017.json": sha256(OUT / "QA06_AUDIT_QUEUE_2017.json")},
    }
    write_json(OUT / "QA06_PREPARATION_CHECKPOINT.json", checkpoint)
    print(json.dumps({"targets": 2017, "subdivisions_total": inventory["subdivisions_total"],
                      "subdivisions_auditable": inventory["subdivisions_auditable"],
                      "excluded": segment_status["EXCLUDED_REVOKED_OR_VETOED"], "checkpoints": 41}, ensure_ascii=False))


if __name__ == "__main__":
    main()
