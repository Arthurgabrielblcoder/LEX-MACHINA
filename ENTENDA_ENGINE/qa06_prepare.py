"""Build the deterministic QA-06 active-target and subdivision inventory."""
import hashlib
import json
import re
import subprocess
import unicodedata
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
CC13_DIR = HERE / "derived/candidate_cc_001_2046"
SOURCE_TEXT = CC13_DIR / "SOURCE_CC2002_ARTS_001_2046.txt"
TARGET_INDEX = CC13_DIR / "CC2002_TARGET_INDEX.json"
TARGET_STATUS = CC13_DIR / "CC2002_TARGET_STATUS.json"
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
SOURCE_NOTE_RE = re.compile(
    r"\s+\((?:[“\"]?(?:artigo|caput|redação|parágrafo|inciso|alínea)|incluíd[oa]s?|acrescid[oa]s?|revogad[oa]s?|vetad[oa]s?|vide\b).*$",
    re.I,
)
STRUCTURAL_HEADING_RE = re.compile(r"^(?P<kind>PARTE|LIVRO|SUBTÍTULO|TÍTULO|TITULO)\s+(?P<number>[IVXLCDM]+|GERAL|ESPECIAL)$")
LABEL_RE = {
    "CAPUT": re.compile(r"^Art\.?\s*[\d.]+(?:-[A-Z]+)?[.º°]?\s*", re.I),
    "PARAGRAFO": re.compile(r"^§\s*\d+\s*[ºo°]?\s*", re.I),
    "PARAGRAFO_UNICO": re.compile(r"^Parágrafo\s+único\.\s*", re.I),
    "INCISO": re.compile(r"^[IVXLCDM]+\s*[-–—]\s*"),
    "ALINEA": re.compile(r"^[a-z]\)\s*", re.I),
}
INVALID_COMMIT = "75cb468"
INTERMEDIATE_COMMIT = "7e5d287"
INVENTORY_REL = "ENTENDA_ENGINE/derived/qa06_subdivision_material_audit/QA06_SUBDIVISION_INVENTORY.json"


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


def normalized(value):
    return unicodedata.normalize("NFC", " ".join(value.split()))


def source_segment_text(segment_id, target, source_lines, target_lines):
    """Extract one device from its indexed source line, never from a heading buffer."""
    kind = target["kind"]
    if kind not in LABEL_RE:
        raise RuntimeError(f"unsupported source target kind: {segment_id} {kind}")
    line_index = target["line_start"] - 1
    raw = source_lines[line_index].strip()
    text, substitutions = LABEL_RE[kind].subn("", raw, count=1)
    if substitutions != 1:
        raise RuntimeError(f"source label mismatch: {segment_id}: {raw!r}")
    # Official amendment/revocation notes immediately following a device belong
    # to that device.  A blank line, another target, or a structural heading is
    # a hard boundary; this prevents headings from being absorbed into the law.
    cursor = line_index + 1
    while cursor < len(source_lines):
        following = source_lines[cursor].strip()
        if not following or cursor + 1 in target_lines:
            break
        if (STRUCTURAL_HEADING_RE.fullmatch(following) or
                following.startswith(("CAPÍTULO ", "Seção ", "SEÇÃO "))):
            break
        if following.startswith("("):
            break
        if following == "º" and raw.startswith("§"):
            # Source typo in art. 96, § 3º: the ordinal marker was duplicated
            # on its own physical line before the actual provision text.
            cursor += 1
            continue
        text += " " + following
        cursor += 1
    text = re.sub(r"^\.\s+", "", text)
    return normalized(SOURCE_NOTE_RE.sub("", text))


def heading_context(source_lines):
    """Map each source line to its enclosing official book/title/subtitle."""
    current_book = "PARTE GERAL / LIVRO I"
    current_title = "TÍTULO I — DAS PESSOAS NATURAIS"
    current_subtitle = None
    context = {}
    for index, raw in enumerate(source_lines):
        stripped = raw.strip()
        match = STRUCTURAL_HEADING_RE.fullmatch(stripped)
        if match:
            name = None
            for candidate in source_lines[index + 1:index + 6]:
                candidate = candidate.strip()
                if not candidate or candidate.startswith("("):
                    continue
                if STRUCTURAL_HEADING_RE.fullmatch(candidate) or candidate.startswith(("CAPÍTULO ", "Seção ")):
                    break
                name = candidate
                break
            full = stripped + (f" — {name}" if name else "")
            if match.group("kind") == "LIVRO":
                current_book = full
            elif match.group("kind") in ("TÍTULO", "TITULO"):
                current_title, current_subtitle = full, None
            elif match.group("kind") == "SUBTÍTULO":
                current_subtitle = full
        context[index + 1] = (current_book, current_title, current_subtitle)
    return context


def committed_inventory(commit):
    raw = subprocess.check_output(["git", "show", f"{commit}:{INVENTORY_REL}"])
    return hashlib.sha256(raw).hexdigest(), json.loads(raw.decode("utf-8"))


def comparable_legal_text(value):
    value = normalized(value or "")
    value = re.sub(r"^(?:o|º)\s+(?:\.\s*)?", "", value)
    value = SOURCE_NOTE_RE.sub("", " " + value).strip()
    return value


def inventory_differences(old, new):
    old_by = {record["target_id"]: record for record in old["records"]}
    new_by = {record["target_id"]: record for record in new["records"]}
    changed = []
    for target_id in sorted(new_by, key=old_prep.article_key):
        old_segments = {item["subdivision_id"]: item for item in old_by[target_id]["subdivisions"]}
        new_segments = {item["subdivision_id"]: item for item in new_by[target_id]["subdivisions"]}
        differences = []
        for segment_id in sorted(set(old_segments) | set(new_segments)):
            before, after = old_segments.get(segment_id), new_segments.get(segment_id)
            if before != after:
                differences.append({
                    "subdivision_id": segment_id,
                    "before_text": before and before["text"],
                    "after_text": after and after["text"],
                    "before_status": before and before["status"],
                    "after_status": after and after["status"],
                    "difference_class": (
                        "SOURCE_NOTE_OR_LABEL_NORMALIZATION"
                        if comparable_legal_text(before and before["text"]) == comparable_legal_text(after and after["text"])
                        else "LEGAL_TEXT_BOUNDARY_CORRECTION"
                    ),
                })
        heading_changed = any(old_by[target_id].get(key) != new_by[target_id].get(key)
                              for key in ("book", "title", "subtitle"))
        if differences or heading_changed:
            changed.append({"target_id": target_id, "segment_changes": differences,
                            "heading_context_changed": heading_changed})
    return changed


def main():
    if current_hashes() != PROTECTED:
        raise RuntimeError("protected QA-05 and historical baseline hash mismatch")
    rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line]
    active = sorted((row for row in rows if row["status"] == "ACTIVE"),
                    key=lambda row: old_prep.article_key(row["target_id"]))
    if len(rows) != 2312 or len(active) != 2017:
        raise RuntimeError("unexpected QA-05 corpus cardinality")

    index_document = json.loads(TARGET_INDEX.read_text(encoding="utf-8"))
    target_map = {target["target_id"]: target for target in index_document["targets"]}
    target_lines = {target["line_start"] for target in index_document["targets"] if target.get("line_start")}
    status_map = json.loads(TARGET_STATUS.read_text(encoding="utf-8"))["targets"]
    source_lines = SOURCE_TEXT.read_text(encoding="utf-8-sig").splitlines()
    contexts = heading_context(source_lines)
    records = []
    segment_status = Counter()
    kind_counts = Counter()
    for position, row in enumerate(active, 1):
        raw_segments = []
        for line in row["source"]["source_text_snapshot"].splitlines():
            if "\t" not in line:
                continue
            segment_id, _snapshot_text = line.split("\t", 1)
            if segment_id not in target_map:
                raise RuntimeError(f"segment absent from frozen target index: {segment_id}")
            target = target_map[segment_id]
            text = source_segment_text(segment_id, target, source_lines, target_lines)
            target_state = status_map.get(segment_id, {})
            lowered = text.casefold()
            excluded = (target_state.get("revoked_marker") or
                        target_state.get("status") in ("REVOKED", "HISTORICAL_ONLY") or
                        "revogad" in lowered or "vetado" in lowered)
            status = "EXCLUDED_REVOKED_OR_VETOED" if excluded else "ACTIVE"
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
        first_line = min(target_map[item["subdivision_id"]]["line_start"] for item in raw_segments)
        book, title, subtitle = contexts[first_line]
        records.append({
            "audit_position": position,
            "target_id": row["target_id"],
            "explanation_id": row["explanation_id"],
            "article": row["target_id"].split(":")[1],
            "book": book,
            "title": title,
            "subtitle": subtitle,
            "validity": row["validity"]["target_status"],
            "source_text_sha256": row["source"]["source_text_sha256"],
            "content_sha256": json_sha(row["content"]),
            "subdivision_total": len(raw_segments),
            "subdivision_auditable": sum(segment["material_audit_required"] for segment in raw_segments),
            "subdivisions": raw_segments,
        })

    inventory = {
        "schema_version": 1, "mission": "QA-06-FRONT-B", "as_of": AS_OF,
        "status": "FROZEN_ACTIVE_SUBDIVISION_INVENTORY_V2_CORRECTED", "source": str(CORPUS.relative_to(HERE)).replace("\\", "/"),
        "source_sha256": PROTECTED["qa05_corpus"], "active_targets": 2017,
        "legal_text_source": str(SOURCE_TEXT.relative_to(HERE)).replace("\\", "/"),
        "legal_text_source_sha256": sha256(SOURCE_TEXT),
        "target_index_sha256": sha256(TARGET_INDEX),
        "target_status_sha256": sha256(TARGET_STATUS),
        "subdivisions_total": sum(row["subdivision_total"] for row in records),
        "subdivisions_auditable": sum(row["subdivision_auditable"] for row in records),
        "subdivision_status_counts": dict(sorted(segment_status.items())),
        "subdivision_kind_counts": dict(sorted(kind_counts.items())),
        "ordering": "canonical numeric article order, base before intercalated suffix, then granular suffix",
        "records": records,
    }
    inventory_path = OUT / "QA06_SUBDIVISION_INVENTORY_V2_CORRECTED.json"
    write_json(inventory_path, inventory)
    queue = {
        "schema_version": 1, "mission": "QA-06-FRONT-B", "as_of": AS_OF,
        "status": "SELECTED_ALL_ACTIVE_TARGETS_FROM_CORRECTED_INVENTORY", "source": inventory_path.name,
        "source_sha256": sha256(inventory_path),
        "total": 2017, "checkpoint_size": 50, "checkpoint_total": 41, "records": records,
    }
    queue_path = OUT / "QA06_AUDIT_QUEUE_2017_V2_CORRECTED.json"
    write_json(queue_path, queue)
    invalid_hash, invalid_inventory = committed_inventory(INVALID_COMMIT)
    intermediate_hash, intermediate_inventory = committed_inventory(INTERMEDIATE_COMMIT)
    invalid_changes = inventory_differences(invalid_inventory, inventory)
    intermediate_changes = inventory_differences(intermediate_inventory, inventory)
    invalid_segment_changes = [change for item in invalid_changes for change in item["segment_changes"]]
    intermediate_segment_changes = [change for item in intermediate_changes for change in item["segment_changes"]]
    report = {
        "schema_version": 1, "mission": "QA-06-RECOVERY", "as_of": AS_OF,
        "status": "CORRECTED_INVENTORY_AUTHORIZED_FOR_AUDIT",
        "invalid_preliminary": {"commit": INVALID_COMMIT, "sha256": invalid_hash,
                                "validity": "INVALID_FOR_LEGAL_AUDIT"},
        "intermediate_parser_fix": {"commit": INTERMEDIATE_COMMIT, "sha256": intermediate_hash,
                                    "validity": "SUPERSEDED_BY_SOURCE_LINE_EXTRACTION"},
        "corrected": {"file": inventory_path.name, "sha256": sha256(inventory_path),
                      "queue_file": queue_path.name, "queue_sha256": sha256(queue_path),
                      "validity": "AUTHORIZED_FOR_LEGAL_AUDIT"},
        "cause": "case-insensitive heading regex matched title-case internal legal remissions; snapshot buffering could also absorb later headings",
        "correction": "device text extracted from each target's indexed official source line; only contiguous parenthetical amendment notes are attached; blank lines and structural headings are hard boundaries",
        "differences_from_invalid": {
            "affected_targets_any_field": len(invalid_changes),
            "affected_targets_legal_segments": sum(bool(item["segment_changes"]) for item in invalid_changes),
            "affected_subdivisions": sum(len(item["segment_changes"]) for item in invalid_changes),
            "difference_classes": dict(sorted(Counter(item["difference_class"] for item in invalid_segment_changes).items())),
            "records": invalid_changes,
        },
        "differences_from_intermediate": {
            "affected_targets_any_field": len(intermediate_changes),
            "affected_targets_legal_segments": sum(bool(item["segment_changes"]) for item in intermediate_changes),
            "affected_subdivisions": sum(len(item["segment_changes"]) for item in intermediate_changes),
            "difference_classes": dict(sorted(Counter(item["difference_class"] for item in intermediate_segment_changes).items())),
            "records": intermediate_changes,
        },
        "definitive_counts": {"active_targets": 2017, "subdivisions_total": inventory["subdivisions_total"],
                              "subdivisions_auditable": inventory["subdivisions_auditable"],
                              "excluded_revoked_or_vetoed": segment_status["EXCLUDED_REVOKED_OR_VETOED"]},
        "agent_recovery": {"final_artifacts_found": 0, "reused": 0, "quarantined": 0,
                           "status": "ALL_THREE_AGENTS_STOPPED_BEFORE_FINAL_ARTIFACTS_DUE_TO_USAGE_LIMIT"},
    }
    report_path = OUT / "QA06_INVENTORY_RECOVERY_REPORT.json"
    write_json(report_path, report)
    all_segments = [segment for record in records for segment in record["subdivisions"]]
    boundary_corrections = [
        {"target_id": item["target_id"], **change}
        for item in invalid_changes for change in item["segment_changes"]
        if change["difference_class"] == "LEGAL_TEXT_BOUNDARY_CORRECTION"
    ]
    intercalated = [record["target_id"] for record in records
                    if re.search(r"ART\.\d+(?:\.\d+)?-[A-Z]+", record["target_id"])]
    integrity = {
        "schema_version": 1, "mission": "QA-06-RECOVERY", "as_of": AS_OF,
        "status": "PASS_CORRECTED_EXTRACTION_RELEASED_FOR_AUDIT",
        "authorized_inventory_sha256": sha256(inventory_path),
        "checks": {
            "active_target_count_2017": len(records) == 2017,
            "active_target_ids_unique": len({record["target_id"] for record in records}) == 2017,
            "audit_positions_contiguous": [record["audit_position"] for record in records] == list(range(1, 2018)),
            "subdivision_count_matches": len(all_segments) == inventory["subdivisions_total"],
            "subdivision_ids_unique": len({segment["subdivision_id"] for segment in all_segments}) == len(all_segments),
            "all_auditable_segments_nonempty": all(segment["text"] for segment in all_segments
                                                    if segment["material_audit_required"]),
            "all_segment_hashes_match_text": all(
                hashlib.sha256(segment["text"].encode("utf-8")).hexdigest() == segment["text_sha256"]
                for segment in all_segments),
            "revoked_or_vetoed_preserved_not_auditable": all(
                not segment["material_audit_required"] for segment in all_segments
                if segment["status"] == "EXCLUDED_REVOKED_OR_VETOED"),
            "art_1358_a_internal_title_complete": "Título II da Lei nº 4.591" in next(
                segment["text"] for segment in all_segments
                if segment["subdivision_id"] == "CC2002:ART.1358-A:PAR.2:INC.II"),
            "art_1367_internal_title_complete": "Título X do Livro III" in next(
                segment["text"] for segment in all_segments
                if segment["subdivision_id"] == "CC2002:ART.1367:CAPUT"),
            "art_96_split_source_line_repaired": next(
                segment["text"] for segment in all_segments
                if segment["subdivision_id"] == "CC2002:ART.96:PAR.3").startswith("São necessárias"),
            "art_1636_anomalous_label_supported": next(
                segment["text"] for segment in all_segments
                if segment["subdivision_id"] == "CC2002:ART.1636:CAPUT").startswith("O pai ou a mãe"),
        },
        "counts": {
            "active_targets": len(records), "subdivisions_total": len(all_segments),
            "subdivisions_auditable": sum(segment["material_audit_required"] for segment in all_segments),
            "excluded_revoked_or_vetoed": sum(segment["status"] == "EXCLUDED_REVOKED_OR_VETOED"
                                                for segment in all_segments),
            "intercalated_active_targets": len(intercalated),
            "preliminary_legal_boundary_corrections": len(boundary_corrections),
        },
        "intercalated_active_target_ids": intercalated,
        "preliminary_legal_boundary_corrections": boundary_corrections,
        "protected_source_sha256": {
            "qa05_corpus": sha256(CORPUS), "official_frozen_text": sha256(SOURCE_TEXT),
            "target_index": sha256(TARGET_INDEX), "target_status": sha256(TARGET_STATUS),
        },
    }
    if not all(integrity["checks"].values()):
        raise RuntimeError("corrected extraction integrity check failed")
    integrity_path = OUT / "QA06_EXTRACTION_INTEGRITY_EVIDENCE.json"
    write_json(integrity_path, integrity)
    pointer = {
        "schema_version": 1, "mission": "QA-06", "as_of": AS_OF,
        "authorized_inventory": inventory_path.name, "authorized_inventory_sha256": sha256(inventory_path),
        "authorized_queue": queue_path.name, "authorized_queue_sha256": sha256(queue_path),
        "recovery_report": report_path.name, "recovery_report_sha256": sha256(report_path),
        "extraction_integrity": integrity_path.name,
        "extraction_integrity_sha256": sha256(integrity_path),
        "preliminary_inventory_status": "INVALID_PRESERVED_IN_GIT_COMMIT_75cb468",
    }
    write_json(OUT / "QA06_AUTHORIZED_INVENTORY_POINTER.json", pointer)
    checkpoint = {
        "schema_version": 1, "mission": "QA-06", "checkpoint": "PREP-CP02-RECOVERY", "as_of": AS_OF,
        "status": "COMPLETE_CORRECTED_INVENTORY_AUTHORIZED", "protected_sha256": PROTECTED,
        "counts": {"versions": 2312, "active": 2017, "historical": 295,
                   "subdivisions_total": inventory["subdivisions_total"],
                   "subdivisions_auditable": inventory["subdivisions_auditable"],
                   "material_checkpoints": 41},
        "artifact_sha256": {inventory_path.name: sha256(inventory_path), queue_path.name: sha256(queue_path),
                            report_path.name: sha256(report_path), integrity_path.name: sha256(integrity_path)},
    }
    write_json(OUT / "QA06_PREPARATION_CHECKPOINT_V2_CORRECTED.json", checkpoint)
    print(json.dumps({"targets": 2017, "subdivisions_total": inventory["subdivisions_total"],
                      "subdivisions_auditable": inventory["subdivisions_auditable"],
                      "excluded": segment_status["EXCLUDED_REVOKED_OR_VETOED"], "checkpoints": 41}, ensure_ascii=False))


if __name__ == "__main__":
    main()
