#!/usr/bin/env python3
"""Independently reread and verify a D05 shadow resolved selection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from resolve_selection import (
    ResolutionError,
    build_resolved_selection,
    digest_bytes,
    load_json,
    parse_bindings_file,
    parse_inline_bindings,
    validate_schema,
)


def assert_no_absolute_paths(value: Any, where: str = "resolved") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"absolute_path", "cwd", "hostname", "username", "timestamp"}:
                raise ResolutionError("NONCANONICAL_OUTPUT", f"machine-specific field in canonical output: {where}.{key}")
            assert_no_absolute_paths(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_absolute_paths(child, f"{where}[{index}]")


def verify_output(registry: Path, lock: Path, expected_lock_sha256: str,
                  raw_bindings: dict[str, str], resolved_path: Path) -> dict[str, Any]:
    actual, raw = load_json(resolved_path)
    schema_path = Path(__file__).resolve().parent / "schemas" / "resolved-selection.schema.json"
    schema, _ = load_json(schema_path)
    validate_schema(actual, schema, schema, "resolved")
    assert_no_absolute_paths(actual)
    if actual.get("artifact_class") != "DERIVED" or actual.get("mode") != "SHADOW" or actual.get("authority") != "NON_AUTHORITATIVE":
        raise ResolutionError("AUTHORITY_MISMATCH", "resolved output authority labels are invalid")

    # Reconstruct from Registry, Lock, bindings and physical bytes. The candidate
    # output is never used as an input to resolution.
    expected, _ = build_resolved_selection(registry, lock, expected_lock_sha256, raw_bindings)
    if actual != expected:
        raise ResolutionError("RESOLVED_SELECTION_MISMATCH", "resolved output differs from independent reconstruction")

    sets = actual["selection_sets"]
    items = [item for group in sets for item in group["items"]]
    if len(items) != actual["resolution_summary"]["semantic_items"]:
        raise ResolutionError("MULTIPLICITY_CHANGED", "resolved item count differs from summary")
    if len(actual["explicit_absences"]) != actual["resolution_summary"]["explicit_absences"]:
        raise ResolutionError("MULTIPLICITY_CHANGED", "resolved absence count differs from summary")
    if len(actual["dependencies"]) != actual["resolution_summary"]["dependencies"]:
        raise ResolutionError("DEPENDENCY_UNRESOLVED", "resolved dependency count differs from summary")
    for group in sets:
        ordinals = [item.get("ordinal") for item in group["items"]]
        if group["ordered"] and ordinals != list(range(1, len(group["items"]) + 1)):
            raise ResolutionError("ORDINAL_INVALID", f"output ordinal sequence invalid: {group['set_id']}")
        if not group["ordered"] and any(value is not None for value in ordinals):
            raise ResolutionError("ORDINAL_INVALID", f"unordered output has ordinal: {group['set_id']}")
    return {
        "dependencies": len(actual["dependencies"]),
        "explicit_absences": len(actual["explicit_absences"]),
        "output_sha256": digest_bytes(raw),
        "restricted_local": actual["resolution_summary"]["restricted_local"],
        "result": "PASS",
        "selection_sets": len(sets),
        "semantic_items": len(items),
        "zero_extra_items": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--expected-lock-sha256", "--lock-sha256", dest="lock_sha256", required=True)
    binding_group = parser.add_mutually_exclusive_group(required=True)
    binding_group.add_argument("--root-bindings", "--bindings", dest="bindings_file", type=Path)
    binding_group.add_argument("--bind", action="append", default=[])
    parser.add_argument("--resolved", type=Path, required=True)
    args = parser.parse_args()
    try:
        raw_bindings = parse_bindings_file(args.bindings_file) if args.bindings_file else parse_inline_bindings(args.bind)
        result = verify_output(args.registry, args.lock, args.lock_sha256, raw_bindings, args.resolved)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except (OSError, KeyError, TypeError, ValueError, ResolutionError) as exc:
        code = exc.code if isinstance(exc, ResolutionError) else "UNEXPECTED_INPUT_ERROR"
        message = exc.message if isinstance(exc, ResolutionError) else str(exc)
        print(json.dumps({"error_code": code, "errors": [message], "result": "FAIL"}, ensure_ascii=False, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
