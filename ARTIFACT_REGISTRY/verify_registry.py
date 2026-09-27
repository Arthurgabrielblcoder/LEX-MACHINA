#!/usr/bin/env python3
"""Read-only verifier for the shadow Artifact Registry.

The verifier never writes registry or functional data. It validates the small
JSON-Schema subset used by this pilot, canonical JSON bytes, fragment hashes,
identities, locations, file bytes and closed managed-root membership.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


REGISTRY_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = REGISTRY_ROOT.parent.resolve()
CANONICALIZATION = "json-utf8-lf-sorted-keys-indent-2-final-lf-v1"
FORBIDDEN_SELECTION_KEYS = {"active", "enabled", "selected_for_consumption"}


class VerificationError(Exception):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_canonical_json(path: Path) -> Any:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise VerificationError(f"JSON com BOM: {path}")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"JSON inválido em {path}: {exc}") from exc
    if raw != canonical_bytes(value):
        raise VerificationError(f"serialização não canônica: {path}")
    return value


def resolve_ref(schema_root: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise VerificationError(f"$ref externo não suportado: {reference}")
    node: Any = schema_root
    for part in reference[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def validate_schema(value: Any, schema: dict[str, Any], schema_root: dict[str, Any], where: str) -> None:
    if "$ref" in schema:
        validate_schema(value, resolve_ref(schema_root, schema["$ref"]), schema_root, where)
        return
    if "const" in schema and value != schema["const"]:
        raise VerificationError(f"schema {where}: esperado {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise VerificationError(f"schema {where}: valor fora do enum")
    expected = schema.get("type")
    if expected is not None:
        names = expected if isinstance(expected, list) else [expected]
        checks = {
            "array": lambda x: isinstance(x, list),
            "boolean": lambda x: isinstance(x, bool),
            "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
            "null": lambda x: x is None,
            "object": lambda x: isinstance(x, dict),
            "string": lambda x: isinstance(x, str),
        }
        if not any(checks[name](value) for name in names):
            raise VerificationError(f"schema {where}: tipo inválido")
    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            raise VerificationError(f"schema {where}: campos ausentes {missing}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                raise VerificationError(f"schema {where}: campos extras {extra}")
        for key, child in properties.items():
            if key in value:
                validate_schema(value[key], child, schema_root, f"{where}.{key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise VerificationError(f"schema {where}: poucos itens")
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise VerificationError(f"schema {where}: itens duplicados")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema(item, schema["items"], schema_root, f"{where}[{index}]")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise VerificationError(f"schema {where}: string curta")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            raise VerificationError(f"schema {where}: padrão inválido")
    if isinstance(value, int) and not isinstance(value, bool) and value < schema.get("minimum", value):
        raise VerificationError(f"schema {where}: abaixo do mínimo")


def reject_selection_keys(value: Any, where: str = "root") -> None:
    if isinstance(value, dict):
        bad = sorted(FORBIDDEN_SELECTION_KEYS.intersection(value))
        if bad:
            raise VerificationError(f"campos operacionais proibidos em {where}: {bad}")
        for key, child in value.items():
            reject_selection_keys(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_selection_keys(child, f"{where}[{index}]")


def safe_relative(value: str, where: str) -> PurePosixPath:
    if "\\" in value or unicodedata.normalize("NFC", value) != value:
        raise VerificationError(f"path não canônico em {where}: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise VerificationError(f"path inseguro em {where}: {value!r}")
    if re.match(r"^[A-Za-z]:", value) or value.startswith("//"):
        raise VerificationError(f"path absoluto em {where}: {value!r}")
    return path


def resolve_inside(base: Path, relative: str, where: str) -> Path:
    rel = safe_relative(relative, where)
    target = base.joinpath(*rel.parts).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise VerificationError(f"path escapa da raiz em {where}: {relative!r}") from exc
    return target


def main() -> int:
    errors: list[str] = []
    conflicts: list[str] = []
    orphans: list[str] = []
    missing: list[str] = []
    role_counts: Counter[str] = Counter()
    entries = 0
    external_entries = 0
    total_bytes = 0
    try:
        index_schema = load_canonical_json(REGISTRY_ROOT / "schemas" / "registry-index.schema.json")
        fragment_schema = load_canonical_json(REGISTRY_ROOT / "schemas" / "registry-fragment.schema.json")
        index = load_canonical_json(REGISTRY_ROOT / "index.json")
        validate_schema(index, index_schema, index_schema, "index")
        reject_selection_keys(index, "index")
        if index["canonicalization"] != CANONICALIZATION:
            raise VerificationError("canonicalização desconhecida no índice")
        fragment_ids: set[str] = set()
        fragment_paths: set[str] = set()
        for descriptor in index["fragments"]:
            if descriptor["dataset_id"] in fragment_ids:
                conflicts.append(f"dataset_id duplicado: {descriptor['dataset_id']}")
            fragment_ids.add(descriptor["dataset_id"])
            fragment_rel = safe_relative(descriptor["path"], "index.fragments.path").as_posix()
            folded = unicodedata.normalize("NFC", fragment_rel).casefold()
            if folded in fragment_paths:
                conflicts.append(f"fragment path colide por NFC/casefold: {fragment_rel}")
            fragment_paths.add(folded)
            fragment_path = resolve_inside(REGISTRY_ROOT, fragment_rel, "index.fragments.path")
            if not fragment_path.is_file():
                missing.append(fragment_rel)
                continue
            if fragment_path.stat().st_size != descriptor["size"]:
                errors.append(f"tamanho do fragmento diverge: {fragment_rel}")
            if sha256(fragment_path) != descriptor["sha256"]:
                errors.append(f"SHA-256 do fragmento diverge: {fragment_rel}")
            fragment = load_canonical_json(fragment_path)
            validate_schema(fragment, fragment_schema, fragment_schema, fragment_rel)
            reject_selection_keys(fragment, fragment_rel)
            if fragment["dataset_id"] != descriptor["dataset_id"]:
                errors.append(f"dataset_id diverge entre índice e fragmento: {fragment_rel}")
            roots: dict[str, tuple[Path, bool]] = {}
            root_folded: set[str] = set()
            for root in fragment["storage_roots"]:
                root_id = root["storage_root_id"]
                if root_id in roots:
                    conflicts.append(f"storage_root_id duplicado: {root_id}")
                    continue
                physical = resolve_inside(REPOSITORY_ROOT, root["relative_path"], f"storage_root {root_id}")
                folded_root = unicodedata.normalize("NFC", str(physical)).casefold()
                if folded_root in root_folded:
                    conflicts.append(f"storage roots colidem: {root_id}")
                root_folded.add(folded_root)
                roots[root_id] = (physical, root["managed"])
            managed_ids = fragment["managed_roots"]
            if len(set(managed_ids)) != len(managed_ids):
                conflicts.append("managed_roots contém duplicatas")
            for root_id in managed_ids:
                if root_id not in roots or not roots[root_id][1]:
                    errors.append(f"managed root inválida: {root_id}")
            logical: dict[tuple[str, str], tuple[str, int]] = {}
            occurrences: dict[str, tuple[str, int]] = {}
            locations: dict[tuple[str, str], str] = {}
            folded_locations: dict[tuple[str, str], str] = {}
            registered_by_root: dict[str, set[str]] = {root_id: set() for root_id in managed_ids}
            for artifact in fragment["artifacts"]:
                entries += 1
                role_counts[artifact["artifact_role"]] += 1
                total_bytes += artifact["size"]
                root_id = artifact["storage_root_id"]
                if root_id not in roots:
                    errors.append(f"root desconhecida: {root_id}")
                    continue
                rel = safe_relative(artifact["relative_path"], artifact["occurrence_id"]).as_posix()
                byte_id = (artifact["sha256"], artifact["size"])
                logical_id = (artifact["logical_id"], artifact["version"])
                if logical_id in logical and logical[logical_id] != byte_id:
                    conflicts.append(f"logical_id/version com bytes divergentes: {logical_id}")
                logical.setdefault(logical_id, byte_id)
                occurrence_id = artifact["occurrence_id"]
                if occurrence_id in occurrences:
                    if occurrences[occurrence_id] != byte_id:
                        conflicts.append(f"occurrence_id com bytes divergentes: {occurrence_id}")
                    else:
                        conflicts.append(f"occurrence_id duplicada: {occurrence_id}")
                occurrences.setdefault(occurrence_id, byte_id)
                location = (root_id, rel)
                if location in locations:
                    conflicts.append(f"localização literal duplicada: {root_id}:{rel}")
                locations[location] = occurrence_id
                folded = (root_id, unicodedata.normalize("NFC", rel).casefold())
                if folded in folded_locations:
                    conflicts.append(f"localização colide por NFC/casefold: {root_id}:{rel}")
                folded_locations[folded] = occurrence_id
                physical = resolve_inside(roots[root_id][0], rel, occurrence_id)
                if not physical.is_file():
                    missing.append(f"{root_id}:{rel}")
                else:
                    if physical.stat().st_size != artifact["size"]:
                        errors.append(f"tamanho diverge: {root_id}:{rel}")
                    if sha256(physical) != artifact["sha256"]:
                        errors.append(f"SHA-256 diverge: {root_id}:{rel}")
                if root_id in registered_by_root:
                    registered_by_root[root_id].add(rel)
                else:
                    external_entries += 1
            for root_id in managed_ids:
                physical_root = roots[root_id][0]
                if not physical_root.is_dir():
                    missing.append(f"managed root {root_id}")
                    continue
                actual = {
                    path.relative_to(physical_root).as_posix()
                    for path in physical_root.rglob("*")
                    if path.is_file()
                }
                expected = registered_by_root[root_id]
                orphans.extend(f"{root_id}:{path}" for path in sorted(actual - expected))
                missing.extend(f"{root_id}:{path}" for path in sorted(expected - actual))
        if conflicts or errors or orphans or missing:
            raise VerificationError("verificação fail-closed encontrou divergências")
    except (OSError, KeyError, TypeError, VerificationError) as exc:
        errors.append(str(exc))
    result = {
        "conflicts": sorted(set(conflicts)),
        "entries": entries,
        "errors": sorted(set(errors)),
        "external_entries": external_entries,
        "managed_roots": ["D05_MANAGED_ROOT"] if entries else [],
        "missing": sorted(set(missing)),
        "orphans": sorted(set(orphans)),
        "result": "PASS" if not (conflicts or errors or orphans or missing) else "FAIL",
        "role_counts": dict(sorted(role_counts.items())),
        "total_bytes": total_bytes,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
