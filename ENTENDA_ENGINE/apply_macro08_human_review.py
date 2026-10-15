#!/usr/bin/env python3
"""
Apply the human-approved Macro08 patch set to the authoring drafts only.

Safety properties:
- expects exactly 31 decisions: 20 A + 7 B + 4 C
- applies only content fields explicitly present in the decision file
- leaves all non-target explanations untouched
- handles the ADCT:ART.101 provenance-only decision in a sidecar metadata file
- fails closed on missing/duplicate targets or glossary terms
- does NOT promote review status
- does NOT edit derived corpus/index/hash evidence directly

After this script succeeds, rerun the canonical Macro08 builder and test suite.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

EXPECTED_PATCH_COUNT = 31
EXPECTED_QUEUE_COUNTS = {"A": 20, "B": 7, "C": 4}
DRAFT_GLOB = "MACRO08_?_DRAFTS.json"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    # Matches the formatting style currently used by Macro08 draft artifacts.
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def find_target(files_data: dict[Path, dict], target_id: str):
    hits = []
    for path, data in files_data.items():
        for idx, exp in enumerate(data.get("explanations", [])):
            if exp.get("target_id") == target_id:
                hits.append((path, idx, exp))
    if len(hits) != 1:
        raise RuntimeError(
            f"{target_id}: expected exactly 1 authoring record, found {len(hits)}"
        )
    return hits[0]


def apply_content_set(exp: dict, patch_set: dict, target_id: str):
    content = exp.setdefault("content", {})
    changed_fields = []

    for key, value in patch_set.items():
        if key == "palavras_dificeis_replace":
            words = content.get("palavras_dificeis")
            if not isinstance(words, list):
                raise RuntimeError(f"{target_id}: palavras_dificeis is not a list")
            for repl in value:
                match_term = repl["match_term"]
                matches = [i for i, item in enumerate(words) if item.get("termo") == match_term]
                if len(matches) != 1:
                    raise RuntimeError(
                        f"{target_id}: glossary term {match_term!r} expected once, found {len(matches)}"
                    )
                words[matches[0]] = repl["replacement"]
                changed_fields.append(f"palavras_dificeis[{match_term}]")

        elif key == "external_layer_notes_append":
            notes = exp.setdefault("external_layer_notes", [])
            if not isinstance(notes, list):
                raise RuntimeError(f"{target_id}: external_layer_notes is not a list")
            for note in value:
                if note not in notes:
                    notes.append(note)
            changed_fields.append("external_layer_notes")

        else:
            if key not in content:
                raise RuntimeError(
                    f"{target_id}: content field {key!r} does not exist; refusing implicit schema change"
                )
            content[key] = value
            changed_fields.append(key)

    return changed_fields


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        default=".",
        help="repository root (default: current directory)",
    )
    ap.add_argument(
        "--decisions",
        default="ENTENDA_ENGINE/derived/production_batch_08_macro/MACRO08_HUMAN_REVIEW_DECISIONS.json",
        help="path to the human decision JSON, relative to root unless absolute",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    decisions_path = Path(args.decisions)
    if not decisions_path.is_absolute():
        decisions_path = root / decisions_path
    decisions_path = decisions_path.resolve()

    macro_dir = root / "ENTENDA_ENGINE" / "derived" / "production_batch_08_macro"
    drafts_dir = macro_dir / "drafts"

    if not decisions_path.exists():
        raise SystemExit(f"Decision file not found: {decisions_path}")
    if not drafts_dir.is_dir():
        raise SystemExit(f"Drafts directory not found: {drafts_dir}")

    decisions = load_json(decisions_path)
    patches = decisions.get("patches", [])
    if len(patches) != EXPECTED_PATCH_COUNT:
        raise SystemExit(
            f"Expected {EXPECTED_PATCH_COUNT} patches, found {len(patches)}"
        )

    queue_counts = {}
    target_ids = []
    for p in patches:
        queue_counts[p["queue"]] = queue_counts.get(p["queue"], 0) + 1
        target_ids.append(p["target_id"])
    if queue_counts != EXPECTED_QUEUE_COUNTS:
        raise SystemExit(f"Unexpected queue counts: {queue_counts}")
    if len(target_ids) != len(set(target_ids)):
        raise SystemExit("Duplicate target_id in human decision file")

    draft_paths = sorted(drafts_dir.glob(DRAFT_GLOB))
    expected_names = {f"MACRO08_{x}_DRAFTS.json" for x in "ABCDEFGH"}
    if {p.name for p in draft_paths} != expected_names:
        raise SystemExit(
            "Expected exactly MACRO08_A_DRAFTS.json ... MACRO08_H_DRAFTS.json; "
            f"found {[p.name for p in draft_paths]}"
        )

    files_data = {p: load_json(p) for p in draft_paths}
    before_hash = {p: sha256_path(p) for p in draft_paths}
    before_explanations = {
        exp["target_id"]: copy.deepcopy(exp)
        for data in files_data.values()
        for exp in data.get("explanations", [])
    }

    metadata_records = []
    touched_targets = []
    touched_files = set()
    audit = []

    for patch in patches:
        tid = patch["target_id"]

        # Provenance-only decision: keep T1 text unchanged and persist separately.
        if "set_metadata" in patch and not patch.get("set"):
            # Still ensure the target exists exactly once in authoring sources.
            path, idx, exp = find_target(files_data, tid)
            metadata_records.append(
                {
                    "target_id": tid,
                    "decision": patch["decision"],
                    "reason_code": patch["reason_code"],
                    **patch["set_metadata"],
                }
            )
            audit.append(
                {
                    "target_id": tid,
                    "file": str(path.relative_to(root)),
                    "changed_fields": [],
                    "metadata_only": True,
                }
            )
            continue

        path, idx, exp = find_target(files_data, tid)
        changed = apply_content_set(exp, patch.get("set", {}), tid)
        touched_targets.append(tid)
        touched_files.add(path)
        audit.append(
            {
                "target_id": tid,
                "file": str(path.relative_to(root)),
                "changed_fields": changed,
                "metadata_only": False,
            }
        )

    # Strong guard: explanations outside patched content targets must be object-identical.
    after_explanations = {
        exp["target_id"]: exp
        for data in files_data.values()
        for exp in data.get("explanations", [])
    }
    content_target_set = set(touched_targets)

    unexpected = []
    for tid, before in before_explanations.items():
        if tid not in content_target_set and after_explanations.get(tid) != before:
            unexpected.append(tid)
    if unexpected:
        raise RuntimeError(
            "Non-target explanations changed in memory: " + ", ".join(unexpected)
        )

    # Persist only files that actually contain content patches.
    for path in sorted(touched_files):
        write_json(path, files_data[path])

    metadata_path = macro_dir / "MACRO08_HUMAN_REVIEW_METADATA.json"
    write_json(
        metadata_path,
        {
            "schema_version": 1,
            "batch_id": decisions.get("batch_id"),
            "review_date": decisions.get("review_date"),
            "base_commit": decisions.get("base_commit"),
            "records": metadata_records,
        },
    )

    after_hash = {p: sha256_path(p) for p in draft_paths}
    changed_files = [
        str(p.relative_to(root))
        for p in draft_paths
        if before_hash[p] != after_hash[p]
    ]

    expected_touched_file_names = {p.name for p in touched_files}
    actual_changed_file_names = {
        Path(x).name for x in changed_files
    }
    if actual_changed_file_names != expected_touched_file_names:
        raise RuntimeError(
            f"Changed-file mismatch. expected={sorted(expected_touched_file_names)} "
            f"actual={sorted(actual_changed_file_names)}"
        )

    audit_path = macro_dir / "MACRO08_HUMAN_REVIEW_APPLY_AUDIT.json"
    write_json(
        audit_path,
        {
            "schema_version": 1,
            "decision_sha256": sha256_path(decisions_path),
            "content_patches_applied": len(touched_targets),
            "metadata_only_patches": len(metadata_records),
            "total_decisions": len(patches),
            "changed_authoring_files": changed_files,
            "unchanged_authoring_files": [
                str(p.relative_to(root))
                for p in draft_paths
                if before_hash[p] == after_hash[p]
            ],
            "before_sha256": {
                str(p.relative_to(root)): before_hash[p] for p in draft_paths
            },
            "after_sha256": {
                str(p.relative_to(root)): after_hash[p] for p in draft_paths
            },
            "patch_audit": audit,
            "status_promotion_performed": False,
            "derived_rebuild_performed": False,
        },
    )

    print("PASS: human review patch applied to authoring drafts")
    print(f"  content patches: {len(touched_targets)}")
    print(f"  metadata-only:   {len(metadata_records)}")
    print(f"  total decisions: {len(patches)}")
    print("  changed authoring files:")
    for x in changed_files:
        print(f"    - {x}")
    print(f"  metadata sidecar: {metadata_path.relative_to(root)}")
    print(f"  audit:            {audit_path.relative_to(root)}")
    print()
    print("NEXT (do not skip):")
    print(
        "  python ENTENDA_ENGINE/build_entenda_macro_segment.py "
        "ENTENDA_ENGINE/derived/production_batch_08_macro --determinism 3"
    )
    print("  then run the Macro08 and full ENTENDA test suites.")
    print("  Do not promote HUMAN_APPROVED_T1 until rebuild/tests pass.")


if __name__ == "__main__":
    main()
