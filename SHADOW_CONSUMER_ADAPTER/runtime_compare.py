"""Independent, non-authoritative runtime comparison for the D05 adapter."""

from __future__ import annotations

from collections import Counter
from typing import Any


STATUSES = {
    "MATCH",
    "MATCH_CARDINALITY_ONLY",
    "NOT_OBSERVABLE",
    "LEGACY_ONLY",
    "SHADOW_ONLY",
    "ORDER_MISMATCH",
    "MULTIPLICITY_MISMATCH",
    "BYTE_MISMATCH",
    "SHADOW_RESOLUTION_FAILURE",
    "ADAPTER_INTERNAL_FAILURE",
}

P1_RUNTIME_SETS = {
    "triage_batch_paths",
    "base_catalog_work_ids",
    "triage_candidate_numbers",
    "catalog_69_ids",
}


def shadow_runtime_summary(resolved: dict[str, Any]) -> dict[str, Any]:
    """Project resolver output without promoting non-observable Legacy dimensions."""
    sets: dict[str, Any] = {}
    for group in resolved.get("selection_sets", []):
        set_id = group["set_id"]
        if set_id not in P1_RUNTIME_SETS:
            continue
        members = []
        for item in group.get("items", []):
            member_ref = item.get("member_ref")
            if isinstance(member_ref, dict) and "value" in member_ref:
                members.append(member_ref["value"])
            else:
                members.append(item.get("relative_path", item.get("occurrence_id")))
        sets[set_id] = {
            "observability": "MEMBER_LEVEL",
            "members": members,
            "ordered": bool(group.get("ordered")),
            "byte_hashes": {
                str(member): item.get("sha256")
                for member, item in zip(members, group.get("items", []))
                if item.get("sha256")
            },
        }
    return {
        "authority": resolved.get("authority", "NON_AUTHORITATIVE"),
        "sets": sets,
        "dependencies": [
            "CATALOG_69_EMBEDDED"
            for item in resolved.get("dependencies", [])
            if item.get("dependency_id") == "catalog_69"
        ],
        "absences": resolved.get("explicit_absences", []),
        "resolution_summary": resolved.get("resolution_summary", {}),
    }


def _result(set_id: str, dimension: str, status: str, **evidence: Any) -> dict[str, Any]:
    assert status in STATUSES
    return {"set_id": set_id, "dimension": dimension, "status": status, "evidence": evidence}


def compare_runtime(
    legacy: dict[str, Any],
    shadow: dict[str, Any],
    *,
    shadow_status: str = "SHADOW_OK",
) -> dict[str, Any]:
    if shadow_status == "SHADOW_FAIL_CLOSED":
        item = _result("__shadow__", "RESOLUTION", "SHADOW_RESOLUTION_FAILURE")
        return {"status": "SHADOW_RESOLUTION_FAILURE", "dimensions": [item], "mismatches": [item]}
    if shadow_status == "SHADOW_INTERNAL_ERROR":
        item = _result("__adapter__", "INTERNAL", "ADAPTER_INTERNAL_FAILURE")
        return {"status": "ADAPTER_INTERNAL_FAILURE", "dimensions": [item], "mismatches": [item]}

    dimensions: list[dict[str, Any]] = []
    legacy_sets = legacy.get("sets", {})
    shadow_sets = shadow.get("sets", {})
    for set_id in sorted(set(legacy_sets) | set(shadow_sets)):
        left = legacy_sets.get(set_id)
        right = shadow_sets.get(set_id)
        if left is None:
            dimensions.append(_result(set_id, "MEMBERSHIP", "SHADOW_ONLY"))
            continue
        if right is None:
            dimensions.append(_result(set_id, "MEMBERSHIP", "LEGACY_ONLY"))
            continue
        observability = left.get("observability", "MEMBER_LEVEL")
        if observability == "NOT_OBSERVABLE":
            dimensions.append(_result(set_id, "MEMBERSHIP", "NOT_OBSERVABLE"))
            continue
        left_members = list(left.get("members", []))
        right_members = list(right.get("members", []))
        if observability == "CARDINALITY_ONLY":
            status = "MATCH_CARDINALITY_ONLY" if len(left_members) == len(right_members) else "MULTIPLICITY_MISMATCH"
            dimensions.append(_result(set_id, "MEMBERSHIP", status, legacy_count=len(left_members), shadow_count=len(right_members)))
            continue

        left_counter, right_counter = Counter(map(str, left_members)), Counter(map(str, right_members))
        if set(left_counter) == set(right_counter):
            dimensions.append(_result(set_id, "MEMBERSHIP", "MATCH", count=len(left_counter)))
        else:
            if set(left_counter) - set(right_counter):
                dimensions.append(_result(set_id, "MEMBERSHIP", "LEGACY_ONLY", members=sorted(set(left_counter) - set(right_counter))))
            if set(right_counter) - set(left_counter):
                dimensions.append(_result(set_id, "MEMBERSHIP", "SHADOW_ONLY", members=sorted(set(right_counter) - set(left_counter))))
        mult_status = "MATCH" if left_counter == right_counter else "MULTIPLICITY_MISMATCH"
        dimensions.append(_result(set_id, "MULTIPLICITY", mult_status, legacy=dict(left_counter), shadow=dict(right_counter)))
        if left.get("ordered"):
            order_status = "MATCH" if list(map(str, left_members)) == list(map(str, right_members)) else "ORDER_MISMATCH"
            dimensions.append(_result(set_id, "ORDER", order_status))
        left_hashes, right_hashes = left.get("byte_hashes", {}), right.get("byte_hashes", {})
        if left_hashes and right_hashes:
            byte_status = "MATCH" if left_hashes == right_hashes else "BYTE_MISMATCH"
            dimensions.append(_result(set_id, "BYTE_IDENTITY", byte_status))

    for dimension, key in (("DEPENDENCIES", "dependencies"), ("ABSENCES", "absences")):
        left_values, right_values = legacy.get(key), shadow.get(key)
        if left_values is None:
            dimensions.append(_result(f"__{key}__", dimension, "NOT_OBSERVABLE"))
        else:
            status = "MATCH" if Counter(map(str, left_values)) == Counter(map(str, right_values or [])) else "MULTIPLICITY_MISMATCH"
            dimensions.append(_result(f"__{key}__", dimension, status))

    benign = {"MATCH", "MATCH_CARDINALITY_ONLY", "NOT_OBSERVABLE"}
    mismatches = [item for item in dimensions if item["status"] not in benign]
    has_not_observable = any(item["status"] == "NOT_OBSERVABLE" for item in dimensions)
    overall = "PASS_WITH_NOT_OBSERVABLE_DIMENSIONS" if not mismatches and has_not_observable else ("MATCH" if not mismatches else "MISMATCH")
    return {"status": overall, "dimensions": dimensions, "mismatches": mismatches}
