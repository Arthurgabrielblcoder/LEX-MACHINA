#!/usr/bin/env python3
"""Resolve the D05 Dataset Lock in shadow mode without filesystem discovery."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


CANONICALIZATION = "json-utf8-lf-sorted-keys-indent-2-final-lf-v1"
RESOLVER_VERSION = "d05-shadow-resolver/1"
OUTPUT_SCHEMA_VERSION = 1
REQUIRED_COUNTS = {"sets": 11, "items": 1699, "absences": 151, "dependencies": 4}
FORBIDDEN_SELECTION_WORDS = {"glob", "rglob", "wildcard", "latest", "fallback", "discover", "scan"}
WINDOWS_RESERVED = {
    "con", "prn", "aux", "nul", "clock$",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


class ResolutionError(Exception):
    """A fail-closed resolver error with a stable machine-readable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def fail(code: str, message: str) -> None:
    raise ResolutionError(code, message)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest_path(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            while True:
                block = stream.read(1024 * 1024)
                if not block:
                    break
                digest.update(block)
    except OSError as exc:
        fail("FILE_READ_FAILED", f"cannot read {path}: {exc}")
    return digest.hexdigest()


def load_json(path: Path, *, canonical: bool = True) -> tuple[Any, bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        fail("FILE_READ_FAILED", f"cannot read {path}: {exc}")
    if raw.startswith(b"\xef\xbb\xbf"):
        fail("NONCANONICAL_JSON", f"JSON has BOM: {path}")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail("INVALID_JSON", f"invalid JSON in {path}: {exc}")
    if canonical and raw != canonical_bytes(value):
        fail("NONCANONICAL_JSON", f"noncanonical JSON: {path}")
    return value, raw


def _schema_ref(root: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        fail("SCHEMA_INVALID", f"external schema reference is forbidden: {reference}")
    node: Any = root
    try:
        for part in reference[2:].split("/"):
            node = node[part.replace("~1", "/").replace("~0", "~")]
    except (KeyError, TypeError) as exc:
        fail("SCHEMA_INVALID", f"unresolvable schema reference: {reference}")
    return node


def validate_schema(value: Any, schema: dict[str, Any], root: dict[str, Any], where: str) -> None:
    if "$ref" in schema:
        validate_schema(value, _schema_ref(root, schema["$ref"]), root, where)
        return
    if "const" in schema and value != schema["const"]:
        fail("SCHEMA_MISMATCH", f"{where}: constant mismatch")
    if "enum" in schema and value not in schema["enum"]:
        fail("SCHEMA_MISMATCH", f"{where}: value outside enum")
    expected = schema.get("type")
    if expected is not None:
        checks = {
            "array": lambda x: isinstance(x, list),
            "boolean": lambda x: isinstance(x, bool),
            "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
            "null": lambda x: x is None,
            "object": lambda x: isinstance(x, dict),
            "string": lambda x: isinstance(x, str),
        }
        names = expected if isinstance(expected, list) else [expected]
        if not any(checks[name](value) for name in names):
            fail("SCHEMA_MISMATCH", f"{where}: invalid type")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        missing = sorted(set(schema.get("required", [])) - set(value))
        if missing:
            fail("SCHEMA_MISMATCH", f"{where}: missing fields {missing}")
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                fail("SCHEMA_MISMATCH", f"{where}: extra fields {extra}")
        for key, child_schema in properties.items():
            if key in value:
                validate_schema(value[key], child_schema, root, f"{where}.{key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            fail("SCHEMA_MISMATCH", f"{where}: too few items")
        if schema.get("uniqueItems"):
            identities = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value]
            if len(identities) != len(set(identities)):
                fail("SCHEMA_MISMATCH", f"{where}: duplicate items")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema(item, schema["items"], root, f"{where}[{index}]")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            fail("SCHEMA_MISMATCH", f"{where}: string too short")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            fail("SCHEMA_MISMATCH", f"{where}: pattern mismatch")
    if isinstance(value, int) and not isinstance(value, bool) and value < schema.get("minimum", value):
        fail("SCHEMA_MISMATCH", f"{where}: below minimum")


def reject_implicit_selection(value: Any, where: str = "lock") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() in FORBIDDEN_SELECTION_WORDS:
                fail("IMPLICIT_DISCOVERY_REQUESTED", f"forbidden selection key: {where}.{key}")
            reject_implicit_selection(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_implicit_selection(child, f"{where}[{index}]")
    elif isinstance(value, str):
        lowered = value.casefold()
        if "*" in value or "?" in value or any(re.search(rf"\b{word}\b", lowered) for word in FORBIDDEN_SELECTION_WORDS):
            fail("IMPLICIT_DISCOVERY_REQUESTED", f"forbidden selection value at {where}: {value!r}")


def safe_relative(value: str, where: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        fail("UNSAFE_PATH", f"empty path at {where}")
    if unicodedata.normalize("NFC", value) != value or "\\" in value or "\x00" in value:
        fail("UNSAFE_PATH", f"noncanonical path at {where}: {value!r}")
    win = PureWindowsPath(value)
    path = PurePosixPath(value)
    if path.is_absolute() or win.is_absolute() or win.drive or value.startswith("//"):
        fail("UNSAFE_PATH", f"absolute, drive-relative, UNC or device path at {where}: {value!r}")
    if not path.parts or any(part in ("", ".", "..") for part in path.parts):
        fail("UNSAFE_PATH", f"dot or empty component at {where}: {value!r}")
    for part in path.parts:
        if ":" in part or part.endswith((".", " ")):
            fail("UNSAFE_PATH", f"ADS or trailing alias at {where}: {value!r}")
        stem = part.split(".", 1)[0].casefold()
        if stem in WINDOWS_RESERVED:
            fail("UNSAFE_PATH", f"reserved Windows name at {where}: {value!r}")
    if path.as_posix() != value:
        fail("UNSAFE_PATH", f"path is not canonical POSIX syntax at {where}: {value!r}")
    return path


def _is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError as exc:
        fail("FILE_MISSING", f"cannot inspect path component {path}: {exc}")
    attributes = getattr(info, "st_file_attributes", 0)
    return stat.S_ISLNK(info.st_mode) or bool(attributes & 0x400)


def _inspect_no_reparse(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if _is_reparse(current):
            fail("SYMLINK_OR_JUNCTION_ESCAPE", f"reparse point is forbidden: {current}")


def validate_binding(root_id: str, raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        fail("ROOT_BINDING_INVALID", f"binding must be absolute: {root_id}")
    try:
        lexical = Path(os.path.abspath(path))
    except OSError as exc:
        fail("ROOT_BINDING_INVALID", f"invalid binding {root_id}: {exc}")
    _inspect_no_reparse(lexical)
    if not lexical.is_dir():
        fail("ROOT_BINDING_INVALID", f"binding is not an existing directory: {root_id}")
    resolved = lexical.resolve(strict=True)
    if os.path.normcase(str(resolved)) != os.path.normcase(str(lexical)):
        fail("SYMLINK_OR_JUNCTION_ESCAPE", f"binding resolves through an alias: {root_id}")
    return resolved


def resolve_target(root: Path, relative: str, where: str) -> Path:
    rel = safe_relative(relative, where)
    lexical = root.joinpath(*rel.parts)
    _inspect_no_reparse(lexical)
    try:
        resolved = lexical.resolve(strict=True)
    except OSError as exc:
        fail("FILE_MISSING", f"missing selected file at {where}: {exc}")
    try:
        resolved.relative_to(root)
    except ValueError:
        fail("SYMLINK_OR_JUNCTION_ESCAPE", f"selected path escapes root at {where}")
    if not resolved.is_file():
        fail("FILE_MISSING", f"selected path is not a file at {where}")
    return resolved


def verify_bytes(path: Path, artifact: dict[str, Any]) -> None:
    before = path.stat()
    if before.st_size != artifact["size"]:
        fail("SIZE_MISMATCH", f"size mismatch: {artifact['occurrence_id']}")
    actual = digest_path(path)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        fail("FILE_CHANGED_DURING_READ", f"file changed while hashing: {artifact['occurrence_id']}")
    if actual != artifact["sha256"]:
        fail("SHA256_MISMATCH", f"SHA-256 mismatch: {artifact['occurrence_id']}")


def parse_bindings_file(path: Path) -> dict[str, str]:
    value, _ = load_json(path)
    schema_path = Path(__file__).resolve().parent / "schemas" / "root-bindings.schema.json"
    schema, _ = load_json(schema_path)
    validate_schema(value, schema, schema, "root_bindings")
    result: dict[str, str] = {}
    for item in value["bindings"]:
        root_id = item["storage_root_id"]
        if root_id in result:
            fail("ROOT_BINDING_MISSING_OR_DUPLICATE", f"duplicate binding: {root_id}")
        result[root_id] = item["absolute_path"]
    return result


def parse_inline_bindings(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            fail("ROOT_BINDING_INVALID", f"binding must use ID=PATH: {raw!r}")
        root_id, path = raw.split("=", 1)
        if not root_id or not path:
            fail("ROOT_BINDING_INVALID", f"binding must use ID=PATH: {raw!r}")
        if root_id in result:
            fail("ROOT_BINDING_MISSING_OR_DUPLICATE", f"duplicate binding: {root_id}")
        result[root_id] = path
    return result


def _load_schema(path: Path) -> dict[str, Any]:
    value, _ = load_json(path)
    if not isinstance(value, dict):
        fail("SCHEMA_INVALID", f"schema root is not an object: {path}")
    return value


def _fragment_path(registry_path: Path, descriptor: dict[str, Any]) -> Path:
    rel = safe_relative(descriptor["path"], "registry.fragments.path")
    base = registry_path.parent.resolve(strict=True)
    target = base.joinpath(*rel.parts)
    _inspect_no_reparse(target)
    try:
        resolved = target.resolve(strict=True)
        resolved.relative_to(base)
    except (OSError, ValueError):
        fail("UNSAFE_PATH", f"fragment path escapes registry root: {descriptor['path']}")
    return resolved


def load_contracts(registry_path: Path, lock_path: Path, expected_lock_sha256: str) -> tuple[dict[str, Any], dict[str, Any], list[tuple[dict[str, Any], dict[str, Any], str]]]:
    if re.fullmatch(r"[0-9a-f]{64}", expected_lock_sha256) is None:
        fail("LOCK_HASH_MISMATCH", "expected Lock SHA-256 must be 64 lowercase hex")
    index, index_raw = load_json(registry_path)
    lock, lock_raw = load_json(lock_path)
    index_schema = _load_schema(registry_path.parent / "schemas" / "registry-index.schema.json")
    fragment_schema = _load_schema(registry_path.parent / "schemas" / "registry-fragment.schema.json")
    lock_schema = _load_schema(lock_path.parent / "schemas" / "dataset-lock.schema.json")
    validate_schema(index, index_schema, index_schema, "registry")
    validate_schema(lock, lock_schema, lock_schema, "lock")
    reject_implicit_selection(lock)
    if digest_bytes(lock_raw) != expected_lock_sha256:
        fail("LOCK_HASH_MISMATCH", "actual Lock SHA-256 differs from the explicit expected digest")
    index_hash = digest_bytes(index_raw)
    if index_hash != lock["registry_index_sha256"]:
        fail("REGISTRY_HASH_MISMATCH", "Registry index SHA-256 differs from Lock pin")
    if index["registry_id"] != lock["registry_id"]:
        fail("IDENTITY_MISMATCH", "registry_id differs between Registry and Lock")
    if index["canonicalization"] != CANONICALIZATION or lock["canonicalization"] != CANONICALIZATION:
        fail("NONCANONICAL_JSON", "unknown canonicalization")
    lock_pins = {item["dataset_id"]: item["sha256"] for item in lock["registry_fragments"]}
    if len(lock_pins) != len(lock["registry_fragments"]):
        fail("REGISTRY_HASH_MISMATCH", "duplicate fragment pins in Lock")
    fragments: list[tuple[dict[str, Any], dict[str, Any], str]] = []
    seen_dataset_ids: set[str] = set()
    for descriptor in index["fragments"]:
        dataset_id = descriptor["dataset_id"]
        if dataset_id in seen_dataset_ids:
            fail("REGISTRY_HASH_MISMATCH", f"duplicate Registry fragment: {dataset_id}")
        seen_dataset_ids.add(dataset_id)
        path = _fragment_path(registry_path, descriptor)
        fragment, raw = load_json(path)
        validate_schema(fragment, fragment_schema, fragment_schema, f"fragment[{dataset_id}]")
        actual_hash = digest_bytes(raw)
        if len(raw) != descriptor["size"] or actual_hash != descriptor["sha256"]:
            fail("REGISTRY_HASH_MISMATCH", f"Registry descriptor mismatch: {dataset_id}")
        if fragment["dataset_id"] != dataset_id or fragment["mode"] != "SHADOW" or fragment["authority"] != "LEGACY_PIPELINE":
            fail("IDENTITY_MISMATCH", f"fragment identity/authority mismatch: {dataset_id}")
        if lock_pins.get(dataset_id) != actual_hash:
            fail("REGISTRY_HASH_MISMATCH", f"Lock fragment pin mismatch: {dataset_id}")
        fragments.append((descriptor, fragment, actual_hash))
    if set(lock_pins) != seen_dataset_ids:
        fail("REGISTRY_HASH_MISMATCH", "Lock and Registry fragment sets differ")
    return index, lock, fragments


def build_occurrence_index(fragments: list[tuple[dict[str, Any], dict[str, Any], str]]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_occurrence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    storage_roots: dict[str, dict[str, Any]] = {}
    folded_locations: dict[tuple[str, str], str] = {}
    logical_bytes: dict[tuple[str, str], tuple[str, int]] = {}
    for _, fragment, _ in fragments:
        for root in fragment["storage_roots"]:
            root_id = root["storage_root_id"]
            if root_id in storage_roots and storage_roots[root_id] != root:
                fail("ROOT_BINDING_MISSING_OR_DUPLICATE", f"conflicting storage root: {root_id}")
            storage_roots[root_id] = root
        for artifact in fragment["artifacts"]:
            safe_relative(artifact["relative_path"], artifact["occurrence_id"])
            by_occurrence[artifact["occurrence_id"]].append(artifact)
            logical_key = (artifact["logical_id"], artifact["version"])
            byte_identity = (artifact["sha256"], artifact["size"])
            if logical_key in logical_bytes and logical_bytes[logical_key] != byte_identity:
                fail("IDENTITY_MISMATCH", f"logical_id/version has conflicting bytes: {logical_key!r}")
            logical_bytes.setdefault(logical_key, byte_identity)
            key = (artifact["storage_root_id"], unicodedata.normalize("NFC", artifact["relative_path"]).casefold())
            if key in folded_locations:
                fail("PATH_COLLISION", f"NFC/casefold path collision: {artifact['occurrence_id']}")
            folded_locations[key] = artifact["occurrence_id"]
    unique: dict[str, dict[str, Any]] = {}
    for occurrence_id, entries in by_occurrence.items():
        if len(entries) != 1:
            fail("OCCURRENCE_NOT_FOUND_OR_AMBIGUOUS", f"ambiguous occurrence: {occurrence_id}")
        unique[occurrence_id] = entries[0]
    return unique, storage_roots


def _required_root_ids(lock: dict[str, Any], by_occurrence: dict[str, dict[str, Any]]) -> set[str]:
    occurrence_ids = [item["occurrence_id"] for group in lock["selection_sets"] for item in group["items"]]
    occurrence_ids += [item["occurrence_id"] for item in lock["dependencies"]]
    occurrence_ids += list(lock["constraints"]["restricted_local_occurrence_ids"])
    roots: set[str] = set()
    for occurrence_id in occurrence_ids:
        artifact = by_occurrence.get(occurrence_id)
        if artifact is None:
            fail("OCCURRENCE_NOT_FOUND_OR_AMBIGUOUS", f"unknown occurrence: {occurrence_id}")
        roots.add(artifact["storage_root_id"])
    return roots


def bind_roots(raw_bindings: dict[str, str], required_ids: set[str], storage_roots: dict[str, dict[str, Any]]) -> dict[str, Path]:
    supplied = set(raw_bindings)
    missing = sorted(required_ids - supplied)
    unknown = sorted(supplied - required_ids)
    if missing or unknown:
        fail("ROOT_BINDING_MISSING_OR_DUPLICATE", f"binding set mismatch; missing={missing}, unknown={unknown}")
    if not supplied <= set(storage_roots):
        fail("ROOT_BINDING_MISSING_OR_DUPLICATE", "binding references undeclared storage root")
    resolved = {root_id: validate_binding(root_id, raw_bindings[root_id]) for root_id in sorted(required_ids)}
    folded = [unicodedata.normalize("NFC", str(path)).casefold() for path in resolved.values()]
    if len(folded) != len(set(folded)):
        fail("ROOT_BINDING_MISSING_OR_DUPLICATE", "two root IDs resolve to the same directory")
    return resolved


def _artifact_for(item: dict[str, Any], by_occurrence: dict[str, dict[str, Any]]) -> dict[str, Any]:
    artifact = by_occurrence.get(item["occurrence_id"])
    if artifact is None:
        fail("OCCURRENCE_NOT_FOUND_OR_AMBIGUOUS", f"unknown occurrence: {item['occurrence_id']}")
    if item["logical_id"] != artifact["logical_id"] or item["version"] != artifact["version"]:
        fail("IDENTITY_MISMATCH", f"identity mismatch: {item['occurrence_id']}")
    return artifact


def _load_member_document(path: Path) -> Any:
    value, _ = load_json(path, canonical=False)
    return value


def validate_member(item: dict[str, Any], artifact: dict[str, Any], path: Path, set_id: str, cache: dict[Path, Any]) -> None:
    member = item.get("member_ref")
    if member is None:
        return
    if path not in cache:
        cache[path] = _load_member_document(path)
    data = cache[path]
    kind, value = member["kind"], member["value"]
    matches = 0
    if kind == "candidate_number" and set_id == "triage_candidate_numbers" and isinstance(data, list):
        matches = sum(isinstance(row, dict) and row.get("number") == value for row in data)
    elif kind == "work_id" and set_id == "base_catalog_work_ids" and isinstance(data, dict):
        matches = int(data.get("work_id") == value)
    elif kind == "work_id" and set_id == "enrichment_queue_work_ids" and isinstance(data, dict):
        matches = sum(isinstance(row, dict) and row.get("work_id") == value for row in data.get("fila", []))
    elif kind == "catalog_69_id" and set_id == "catalog_69_ids" and isinstance(data, dict):
        matches = sum(isinstance(row, dict) and row.get("id") == value for row in data.get("obras", []))
    elif kind == "checkpoint" and set_id == "enrichment_checkpoints" and isinstance(data, dict) and isinstance(value, dict):
        matches = int(data.get("numero") == value.get("checkpoint_number") and data.get("obras_examinadas") == value.get("candidate_numbers"))
    elif kind == "evidence_id" and set_id == "post_codex_revision_members" and isinstance(data, dict):
        matches = sum(isinstance(row, dict) and row.get("evidence_id") == value for row in data.get("revisoes", []))
    else:
        fail("MEMBER_REF_NOT_UNIQUE", f"unsupported member adapter: {set_id}/{kind}")
    if matches != 1:
        fail("MEMBER_REF_NOT_UNIQUE", f"member_ref resolves {matches} times: {set_id}/{member!r}")


def projection_value(set_id: str, item: dict[str, Any], artifact: dict[str, Any]) -> Any:
    if set_id in {"triage_batch_paths", "enrichment_capture_paths_lexical", "enrichment_overlay_paths_build_order", "outer_manifest_member_paths"}:
        return artifact["relative_path"]
    if set_id == "enriched_payload_paths":
        return PurePosixPath(artifact["relative_path"]).name
    if "member_ref" not in item:
        fail("MEMBER_REF_NOT_UNIQUE", f"projection requires member_ref: {set_id}")
    return item["member_ref"]["value"]


def resolved_item(set_id: str, semantic_role: str, item: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    result = {
        "logical_id": artifact["logical_id"],
        "occurrence_id": artifact["occurrence_id"],
        "relative_path": artifact["relative_path"],
        "resolution_status": "RESOLVED_VERIFIED",
        "semantic_role": semantic_role,
        "set_id": set_id,
        "sha256": artifact["sha256"],
        "size": artifact["size"],
        "storage_root_id": artifact["storage_root_id"],
        "version": artifact["version"],
    }
    if "ordinal" in item:
        result["ordinal"] = item["ordinal"]
    if "member_ref" in item:
        result["member_ref"] = item["member_ref"]
    return result


def _validate_constraints(lock: dict[str, Any]) -> None:
    constraints = lock["constraints"]
    false_keys = ("allow_glob", "allow_implicit_resolution", "allow_latest", "allow_regex_discovery", "allow_wildcard")
    if any(constraints[key] is not False for key in false_keys):
        fail("IMPLICIT_DISCOVERY_REQUESTED", "Lock permits implicit selection")
    if constraints["fail_closed"] is not True or constraints["legacy_pipeline_authoritative"] is not True:
        fail("IDENTITY_MISMATCH", "Lock does not preserve fail-closed legacy authority")
    if constraints["restricted_local_absence_result"] != "FAIL_CLOSED" or lock["mode"] != "SHADOW":
        fail("IDENTITY_MISMATCH", "Lock does not preserve SHADOW fail-closed mode")


def build_resolved_selection(registry_path: Path, lock_path: Path, expected_lock_sha256: str, raw_bindings: dict[str, str]) -> tuple[dict[str, Any], dict[str, str]]:
    registry_path = registry_path.resolve(strict=True)
    lock_path = lock_path.resolve(strict=True)
    index, lock, fragments = load_contracts(registry_path, lock_path, expected_lock_sha256)
    _validate_constraints(lock)
    if lock["dataset_id"] != "d05.catalogo-expansao-200" or lock["profile_id"] != "d05-historical-parity-v1":
        fail("IDENTITY_MISMATCH", "this pilot accepts only D05 historical parity v1")
    by_occurrence, storage_roots = build_occurrence_index(fragments)
    required_roots = _required_root_ids(lock, by_occurrence)
    bindings = bind_roots(raw_bindings, required_roots, storage_roots)
    byte_cache: set[str] = set()
    member_cache: dict[Path, Any] = {}

    def validated_artifact(item: dict[str, Any]) -> tuple[dict[str, Any], Path]:
        artifact = _artifact_for(item, by_occurrence)
        try:
            path = resolve_target(bindings[artifact["storage_root_id"]], artifact["relative_path"], artifact["occurrence_id"])
            if artifact["occurrence_id"] not in byte_cache:
                verify_bytes(path, artifact)
                byte_cache.add(artifact["occurrence_id"])
        except ResolutionError as exc:
            if artifact.get("access_class") == "restricted_local":
                fail("RESTRICTED_LOCAL_MISSING", f"restricted_local validation failed for {artifact['occurrence_id']}: {exc.message}")
            raise
        return artifact, path

    output_sets: list[dict[str, Any]] = []
    total_items = 0
    for group in lock["selection_sets"]:
        items = group["items"]
        if len(items) != group["expected_count"]:
            fail("MULTIPLICITY_CHANGED", f"expected_count mismatch: {group['set_id']}")
        ordinals = [item.get("ordinal") for item in items]
        if group["ordered"]:
            if ordinals != list(range(1, len(items) + 1)):
                fail("ORDINAL_INVALID", f"noncontiguous ordinal sequence: {group['set_id']}")
        elif any(value is not None for value in ordinals):
            fail("ORDINAL_INVALID", f"unordered set has ordinal: {group['set_id']}")
        projected: list[Any] = []
        resolved_items: list[dict[str, Any]] = []
        identities: list[tuple[str, str]] = []
        for item in items:
            artifact, path = validated_artifact(item)
            validate_member(item, artifact, path, group["set_id"], member_cache)
            projected.append(projection_value(group["set_id"], item, artifact))
            identities.append((artifact["occurrence_id"], json.dumps(item.get("member_ref"), ensure_ascii=False, sort_keys=True)))
            resolved_items.append(resolved_item(group["set_id"], group["semantic_role"], item, artifact))
        if len(identities) != len(set(identities)):
            fail("MULTIPLICITY_CHANGED", f"ambiguous duplicate member in set: {group['set_id']}")
        if not group["ordered"]:
            projected = sorted(projected)
        if digest_bytes(canonical_bytes(projected)) != group["expected_items_sha256"]:
            fail("MULTIPLICITY_CHANGED", f"projected item digest mismatch: {group['set_id']}")
        output_sets.append({
            "consumption_class": group["consumption_class"],
            "expected_items_sha256": group["expected_items_sha256"],
            "item_kind": group["item_kind"],
            "items": resolved_items,
            "ordered": group["ordered"],
            "ordering_rule_id": group["ordering_rule_id"],
            "semantic_role": group["semantic_role"],
            "set_id": group["set_id"],
        })
        total_items += len(resolved_items)

    dependencies: list[dict[str, Any]] = []
    dependency_ids: set[str] = set()
    for dependency in lock["dependencies"]:
        if dependency["dependency_id"] in dependency_ids:
            fail("DEPENDENCY_UNRESOLVED", f"duplicate dependency_id: {dependency['dependency_id']}")
        dependency_ids.add(dependency["dependency_id"])
        artifact, _ = validated_artifact(dependency)
        resolved = resolved_item("__dependency__", "LOCK_DEPENDENCY", dependency, artifact)
        resolved.pop("set_id")
        resolved["dependency_id"] = dependency["dependency_id"]
        resolved["required"] = dependency["required"]
        dependencies.append(resolved)

    restricted_ids = lock["constraints"]["restricted_local_occurrence_ids"]
    for occurrence_id in restricted_ids:
        artifact = by_occurrence.get(occurrence_id)
        if artifact is None or artifact.get("access_class") != "restricted_local":
            fail("RESTRICTED_LOCAL_MISSING", f"invalid restricted_local occurrence: {occurrence_id}")
        try:
            validated_artifact({"logical_id": artifact["logical_id"], "occurrence_id": occurrence_id, "version": artifact["version"]})
        except ResolutionError as exc:
            fail("RESTRICTED_LOCAL_MISSING", f"restricted_local validation failed for {occurrence_id}: {exc.message}")

    counts = {
        "dependencies": len(dependencies),
        "explicit_absences": len(lock["explicit_absences"]),
        "restricted_local": len(restricted_ids),
        "selection_sets": len(output_sets),
        "semantic_items": total_items,
    }
    if counts["selection_sets"] != REQUIRED_COUNTS["sets"] or counts["semantic_items"] != REQUIRED_COUNTS["items"]:
        fail("MULTIPLICITY_CHANGED", f"D05 cardinality mismatch: {counts}")
    if counts["explicit_absences"] != REQUIRED_COUNTS["absences"]:
        fail("MULTIPLICITY_CHANGED", f"explicit absence count mismatch: {counts['explicit_absences']}")
    if counts["dependencies"] != REQUIRED_COUNTS["dependencies"]:
        fail("DEPENDENCY_UNRESOLVED", f"dependency count mismatch: {counts['dependencies']}")

    fragment_digests = [
        {"dataset_id": descriptor["dataset_id"], "sha256": fragment_hash}
        for descriptor, _, fragment_hash in fragments
    ]
    result = {
        "artifact_class": "DERIVED",
        "authority": "NON_AUTHORITATIVE",
        "canonicalization": CANONICALIZATION,
        "dataset_id": lock["dataset_id"],
        "dependencies": dependencies,
        "explicit_absences": lock["explicit_absences"],
        "lock_sha256": expected_lock_sha256,
        "mode": "SHADOW",
        "profile_id": lock["profile_id"],
        "registry_fragments": fragment_digests,
        "registry_id": index["registry_id"],
        "registry_index_sha256": lock["registry_index_sha256"],
        "resolution_summary": counts,
        "resolver_version": RESOLVER_VERSION,
        "root_binding_ids": sorted(bindings),
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "selection_sets": output_sets,
    }
    diagnostics = {root_id: str(path) for root_id, path in sorted(bindings.items())}
    return result, diagnostics


def write_canonical(path: Path, value: Any) -> str:
    raw = canonical_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(raw)
    os.replace(temporary, path)
    return digest_bytes(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--expected-lock-sha256", "--lock-sha256", dest="lock_sha256", required=True)
    binding_group = parser.add_mutually_exclusive_group(required=True)
    binding_group.add_argument("--root-bindings", "--bindings", dest="bindings_file", type=Path)
    binding_group.add_argument("--bind", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-report", type=Path)
    args = parser.parse_args()
    try:
        raw_bindings = parse_bindings_file(args.bindings_file) if args.bindings_file else parse_inline_bindings(args.bind)
        result, diagnostics = build_resolved_selection(args.registry, args.lock, args.lock_sha256, raw_bindings)
        output_hash = write_canonical(args.output, result)
        if args.runtime_report:
            write_canonical(args.runtime_report, {
                "canonical_output_sha256": output_hash,
                "root_bindings": diagnostics,
                "runtime_report_class": "NONCANONICAL_DIAGNOSTIC",
            })
        print(json.dumps({**result["resolution_summary"], "output_sha256": output_hash, "result": "PASS"}, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except (OSError, KeyError, TypeError, ValueError, ResolutionError) as exc:
        code = exc.code if isinstance(exc, ResolutionError) else "UNEXPECTED_INPUT_ERROR"
        message = exc.message if isinstance(exc, ResolutionError) else str(exc)
        print(json.dumps({"error_code": code, "errors": [message], "result": "FAIL"}, ensure_ascii=False, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
