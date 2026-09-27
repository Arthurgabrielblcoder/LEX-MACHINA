#!/usr/bin/env python3
"""Read-only verifier for the D05 historical-parity shadow Dataset Lock."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


LOCK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = LOCK_ROOT.parent.resolve()
DEFAULT_LOCK = LOCK_ROOT / "d05-historical-parity-v1.lock.json"
SCHEMA_PATH = LOCK_ROOT / "schemas" / "dataset-lock.schema.json"
INDEX_PATH = REPO_ROOT / "ARTIFACT_REGISTRY" / "index.json"
FRAGMENT_PATH = REPO_ROOT / "ARTIFACT_REGISTRY" / "datasets" / "d05.catalogo-expansao-200.json"
GOLDEN_PATH = REPO_ROOT / "CLEANUP_AUDIT" / "D05_GOLDEN_REFERENCE.json"
CANONICALIZATION = "json-utf8-lf-sorted-keys-indent-2-final-lf-v1"
RESTRICTED_LOCAL = {
    "D05_MANAGED_ROOT:03_FONTES/BUSCA_118.json",
    "D05_MANAGED_ROOT:06_RELATORIOS/CONSULTA_CP11.txt",
    "D05_MANAGED_ROOT:06_RELATORIOS/CONSULTA_CP12.txt",
}


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


def load_json(path: Path, canonical: bool = False) -> Any:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise VerificationError(f"JSON com BOM: {path}")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"JSON inválido em {path}: {exc}") from exc
    if canonical and raw != canonical_bytes(value):
        raise VerificationError(f"serialização não canônica: {path}")
    return value


def validate_schema(value: Any, schema: dict[str, Any], root: dict[str, Any], where: str) -> None:
    if "$ref" in schema:
        node: Any = root
        for part in schema["$ref"][2:].split("/"):
            node = node[part.replace("~1", "/").replace("~0", "~")]
        validate_schema(value, node, root, where)
        return
    expected = schema.get("type")
    if expected:
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
            raise VerificationError(f"schema {where}: tipo inválido")
    if "const" in schema and value != schema["const"]:
        raise VerificationError(f"schema {where}: valor constante inválido")
    if "enum" in schema and value not in schema["enum"]:
        raise VerificationError(f"schema {where}: valor fora do enum")
    if isinstance(value, dict):
        missing = sorted(set(schema.get("required", [])) - set(value))
        if missing:
            raise VerificationError(f"schema {where}: campos ausentes {missing}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                raise VerificationError(f"schema {where}: campos extras {extra}")
        for key, child in properties.items():
            if key in value:
                validate_schema(value[key], child, root, f"{where}.{key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise VerificationError(f"schema {where}: poucos itens")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            raise VerificationError(f"schema {where}: itens duplicados")
        if "items" in schema:
            for index, child in enumerate(value):
                validate_schema(child, schema["items"], root, f"{where}[{index}]")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise VerificationError(f"schema {where}: string vazia")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            raise VerificationError(f"schema {where}: padrão inválido")
    if isinstance(value, int) and not isinstance(value, bool) and value < schema.get("minimum", value):
        raise VerificationError(f"schema {where}: abaixo do mínimo")


def artifact_ref(artifact: dict[str, Any], ordinal: int | None = None,
                 member_ref: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "logical_id": artifact["logical_id"],
        "occurrence_id": artifact["occurrence_id"],
        "version": artifact["version"],
    }
    if member_ref is not None:
        result["member_ref"] = member_ref
    if ordinal is not None:
        result["ordinal"] = ordinal
    return result


def registry_context(fragment: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str], dict[str, Any]], dict[str, Path]]:
    by_occurrence = {a["occurrence_id"]: a for a in fragment["artifacts"]}
    if len(by_occurrence) != len(fragment["artifacts"]):
        raise VerificationError("occurrence_id duplicado no Registry")
    by_location = {(a["storage_root_id"], a["relative_path"]): a for a in fragment["artifacts"]}
    roots = {
        root["storage_root_id"]: (REPO_ROOT / root["relative_path"]).resolve()
        for root in fragment["storage_roots"]
    }
    return by_occurrence, by_location, roots


def expected_sets(golden: dict[str, Any], by_location: dict[tuple[str, str], dict[str, Any]],
                  by_occurrence: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = {x["set_id"]: x["items"] for x in golden["ordered_sets"] if x["items"] is not None}
    metadata = {
        "triage_batch_paths": ("TRIAGE_BATCH_INPUTS", "PIPELINE_INPUT", "ARTIFACT_OCCURRENCE"),
        "triage_candidate_numbers": ("TRIAGE_MEMBER_ORDER", "HISTORICAL_ORDER_ASSERTION", "MEMBER_WITHIN_ARTIFACT"),
        "base_catalog_work_ids": ("USABLE_DOSSIER_INPUTS", "PIPELINE_INPUT", "ARTIFACT_OCCURRENCE_WITH_MEMBER_ID"),
        "catalog_69_ids": ("EXTERNAL_CATALOG_MEMBER_ORDER", "PIPELINE_INPUT", "MEMBER_WITHIN_ARTIFACT"),
        "enrichment_queue_work_ids": ("ENRICHMENT_QUEUE_ORDER", "PIPELINE_INPUT", "MEMBER_WITHIN_ARTIFACT"),
        "enrichment_checkpoints": ("CHECKPOINT_SEQUENCE", "PROVENANCE_INPUT", "ARTIFACT_OCCURRENCE_WITH_ORDERED_MEMBERS"),
        "enrichment_capture_paths_lexical": ("ENRICHMENT_SOURCE_CAPTURE_SEQUENCE", "PROVENANCE_INPUT", "ARTIFACT_OCCURRENCE"),
        "enrichment_overlay_paths_build_order": ("ENRICHMENT_OVERLAY_INPUTS", "PIPELINE_INPUT", "ARTIFACT_OCCURRENCE"),
        "enriched_payload_paths": ("ENRICHED_PACKAGE_PAYLOADS", "OUTPUT_REFERENCE", "ARTIFACT_OCCURRENCE"),
        "outer_manifest_member_paths": ("FINAL_HISTORICAL_SNAPSHOT_MEMBERS", "AUDIT_CLOSURE", "ARTIFACT_OCCURRENCE"),
    }

    def at(root_id: str, relative: str) -> dict[str, Any]:
        try:
            return by_location[(root_id, relative)]
        except KeyError as exc:
            raise VerificationError(f"Golden não resolve no Registry: {root_id}:{relative}") from exc

    sets: list[dict[str, Any]] = []
    for set_id, source in ordered.items():
        items: list[dict[str, Any]] = []
        for ordinal, raw in enumerate(source, 1):
            member: dict[str, Any] | None = None
            if set_id == "triage_batch_paths":
                artifact = at("D05_MANAGED_ROOT", raw)
            elif set_id == "triage_candidate_numbers":
                batch = ((int(raw) - 1) // 25) + 1
                artifact = at("D05_MANAGED_ROOT", f"02_TRIAGEM/LOTE_{batch:02d}.json")
                member = {"kind": "candidate_number", "value": int(raw)}
            elif set_id == "base_catalog_work_ids":
                artifact = at("D05_MANAGED_ROOT", f"04_DOSSIERS/{raw}.json")
                member = {"kind": "work_id", "value": raw}
            elif set_id == "catalog_69_ids":
                artifact = by_occurrence["CATALOG_69_ROOT:CATALOGO_69_CANONICO.json"]
                member = {"kind": "catalog_69_id", "value": raw}
            elif set_id == "enrichment_queue_work_ids":
                artifact = by_occurrence["D05_MANAGED_ROOT:06_RELATORIOS/CHECKPOINT_ENRIQUECIMENTO.json"]
                member = {"kind": "work_id", "value": raw}
            elif set_id == "enrichment_checkpoints":
                number = int(raw["checkpoint_number"])
                artifact = at("D05_MANAGED_ROOT", f"06_RELATORIOS/CHECKPOINTS_ENRIQUECIMENTO/CP_{number:02d}.json")
                member = {"kind": "checkpoint", "value": raw}
            elif set_id == "enrichment_capture_paths_lexical":
                artifact = at("D05_MANAGED_ROOT", raw)
            elif set_id == "enrichment_overlay_paths_build_order":
                artifact = at("D05_MANAGED_ROOT", raw)
            elif set_id == "enriched_payload_paths":
                artifact = at("D05_MANAGED_ROOT", f"07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/{raw}")
            elif set_id == "outer_manifest_member_paths":
                artifact = at("D05_MANAGED_ROOT", raw)
            else:
                raise VerificationError(f"conjunto Golden inesperado: {set_id}")
            items.append(artifact_ref(artifact, ordinal, member))
        semantic_role, consumption_class, item_kind = metadata[set_id]
        sets.append({
            "consumption_class": consumption_class,
            "expected_count": len(items),
            "expected_items_sha256": hashlib.sha256(canonical_bytes(source)).hexdigest(),
            "item_kind": item_kind,
            "items": items,
            "ordered": True,
            "ordering_rule_id": f"golden:{set_id}",
            "semantic_role": semantic_role,
            "set_id": set_id,
        })

    revisions = sorted(x["evidence_id"] for x in golden["decisions"]["post_codex_revisions"])
    ledger = by_occurrence["D05_MANAGED_ROOT:06_RELATORIOS/REVISOES_ENRIQUECIMENTO_V1.json"]
    sets.append({
        "consumption_class": "PIPELINE_INPUT",
        "expected_count": len(revisions),
        "expected_items_sha256": hashlib.sha256(canonical_bytes(revisions)).hexdigest(),
        "item_kind": "MEMBER_WITHIN_ARTIFACT",
        "items": [artifact_ref(ledger, member_ref={"kind": "evidence_id", "value": evidence_id}) for evidence_id in revisions],
        "ordered": False,
        "ordering_rule_id": None,
        "semantic_role": "POST_CODEX_REVISION_PATCHES",
        "set_id": "post_codex_revision_members",
    })
    return sets


def expected_absences(golden: dict[str, Any]) -> list[dict[str, Any]]:
    by_kind = {x["absence_kind"]: x for x in golden["semantic_absences"]}
    result: list[dict[str, Any]] = []
    for work_id in by_kind["NO_ENRICHMENT_OVERLAY_BY_DESIGN"]["work_ids"]:
        result.append({"absence_kind": "NO_ENRICHMENT_OVERLAY_BY_DESIGN", "category": "LOCK_OPERATIONAL", "member_ref": {"kind": "work_id", "value": work_id}})
    result.append({"absence_kind": "CANDIDATE_EXCLUDED_FROM_USABLE_CATALOG", "category": "LOCK_OPERATIONAL", "member_ref": {"kind": "candidate", "value": {"candidate_number": 92, "work_id": "EXP2-SER-002"}}})
    for decision in golden["decisions"]["enrichment_overlays"]:
        if decision["cards_added"] == 0:
            result.append({"absence_kind": "NO_ADDITIONAL_CARD_AFTER_EXAMINATION", "category": "HISTORICAL_EVIDENCE", "member_ref": {"kind": "work_id", "value": decision["work_id"]}})
    for evidence_id in by_kind["WEB_SOURCE_WITHOUT_COMPLETE_LOCAL_RECEIPT"]["evidence_ids"]:
        result.append({"absence_kind": "WEB_SOURCE_WITHOUT_COMPLETE_LOCAL_RECEIPT", "category": "HISTORICAL_EVIDENCE", "member_ref": {"kind": "evidence_id", "value": evidence_id}})
    for path in by_kind["REMOTE_FETCH_FAILED_WITH_METADATA_PRESERVED"]["paths"]:
        result.append({"absence_kind": "REMOTE_FETCH_FAILED_WITH_METADATA_PRESERVED", "category": "HISTORICAL_EVIDENCE", "member_ref": {"kind": "capture_path", "value": path}})
    return result


def expected_dependencies(by_occurrence: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    definitions = [
        ("catalog_69", "CATALOG_69_ROOT:CATALOGO_69_CANONICO.json"),
        ("base_catalog", "D05_MANAGED_ROOT:07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json"),
        ("enrichment_checkpoint_state", "D05_MANAGED_ROOT:06_RELATORIOS/CHECKPOINT_ENRIQUECIMENTO.json"),
        ("enrichment_revision_layer", "D05_MANAGED_ROOT:06_RELATORIOS/REVISOES_ENRIQUECIMENTO_V1.json"),
    ]
    return [dict(artifact_ref(by_occurrence[occurrence_id]), dependency_id=dependency_id, required=True)
            for dependency_id, occurrence_id in definitions]


def artifact_path(artifact: dict[str, Any], roots: dict[str, Path]) -> Path:
    root = roots[artifact["storage_root_id"]]
    target = (root / artifact["relative_path"]).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise VerificationError(f"path escapa da storage root: {artifact['occurrence_id']}") from exc
    return target


def validate_member(item: dict[str, Any], artifact: dict[str, Any], roots: dict[str, Path], set_id: str) -> None:
    member = item.get("member_ref")
    if member is None:
        return
    data = load_json(artifact_path(artifact, roots))
    kind, value = member["kind"], member["value"]
    valid = False
    if kind == "candidate_number":
        valid = isinstance(data, list) and sum(x.get("number") == value for x in data) == 1
    elif kind == "work_id" and set_id == "base_catalog_work_ids":
        valid = isinstance(data, dict) and data.get("work_id") == value
    elif kind == "work_id" and set_id == "enrichment_queue_work_ids":
        valid = isinstance(data, dict) and sum(x.get("work_id") == value for x in data.get("fila", [])) == 1
    elif kind == "catalog_69_id":
        valid = isinstance(data, dict) and sum(x.get("id") == value for x in data.get("obras", [])) == 1
    elif kind == "checkpoint":
        valid = (isinstance(data, dict) and data.get("numero") == value.get("checkpoint_number")
                 and data.get("obras_examinadas") == value.get("candidate_numbers"))
    elif kind == "evidence_id":
        valid = isinstance(data, dict) and sum(x.get("evidence_id") == value for x in data.get("revisoes", [])) == 1
    if not valid:
        raise VerificationError(f"member_ref não resolve univocamente em {set_id}: {member!r}")


def assert_no_implicit_selection(value: Any, where: str = "lock") -> None:
    forbidden_keys = {"glob", "rglob", "wildcard", "regex", "latest", "fallback", "discover", "scan"}
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() in forbidden_keys:
                raise VerificationError(f"seleção implícita proibida em {where}.{key}")
            assert_no_implicit_selection(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_implicit_selection(child, f"{where}[{index}]")
    elif isinstance(value, str):
        lowered = value.casefold()
        if "*" in value or "?" in value or re.search(r"\b(latest|glob|rglob|wildcard)\b", lowered):
            raise VerificationError(f"valor de seleção implícita proibido em {where}: {value!r}")


def verify(lock_path: Path, simulated_missing: set[str] | None = None) -> dict[str, Any]:
    simulated_missing = simulated_missing or set()
    schema = load_json(SCHEMA_PATH, canonical=True)
    lock = load_json(lock_path, canonical=True)
    validate_schema(lock, schema, schema, "lock")
    assert_no_implicit_selection(lock)
    if lock["canonicalization"] != CANONICALIZATION:
        raise VerificationError("canonicalização desconhecida")
    if sha256(INDEX_PATH) != lock["registry_index_sha256"]:
        raise VerificationError("hash do Registry index diverge")
    if sha256(FRAGMENT_PATH) != lock["registry_fragments"][0]["sha256"]:
        raise VerificationError("hash do fragmento D05 diverge")
    if sha256(GOLDEN_PATH) != lock["golden_reference"]["sha256"]:
        raise VerificationError("hash da Golden Reference diverge")

    index = load_json(INDEX_PATH, canonical=True)
    fragment = load_json(FRAGMENT_PATH, canonical=True)
    golden = load_json(GOLDEN_PATH, canonical=True)
    if index["registry_id"] != lock["registry_id"]:
        raise VerificationError("registry_id diverge")
    if golden["golden_reference_version"] != lock["golden_reference"]["version"]:
        raise VerificationError("versão da Golden Reference diverge")
    by_occurrence, by_location, roots = registry_context(fragment)

    expected_selection_sets = expected_sets(golden, by_location, by_occurrence)
    if sum(x["expected_count"] for x in lock["selection_sets"]) != 1699:
        raise VerificationError("total semântico diverge de 1699")

    for selection_set in lock["selection_sets"]:
        items = selection_set["items"]
        if len(items) != selection_set["expected_count"]:
            raise VerificationError(f"cardinalidade divergente: {selection_set['set_id']}")
        ordinals = [x.get("ordinal") for x in items]
        if selection_set["ordered"]:
            if ordinals != list(range(1, len(items) + 1)):
                raise VerificationError(f"ordinais inválidos: {selection_set['set_id']}")
        elif any(x is not None for x in ordinals):
            raise VerificationError(f"conjunto não ordenado possui ordinal: {selection_set['set_id']}")
        identities = []
        for item in items:
            occurrence_id = item["occurrence_id"]
            artifact = by_occurrence.get(occurrence_id)
            if artifact is None:
                raise VerificationError(f"occurrence_id inexistente: {occurrence_id}")
            if item["logical_id"] != artifact["logical_id"] or item["version"] != artifact["version"]:
                raise VerificationError(f"identidade divergente: {occurrence_id}")
            identity = (occurrence_id, json.dumps(item.get("member_ref"), ensure_ascii=False, sort_keys=True))
            identities.append(identity)
            path = artifact_path(artifact, roots)
            if occurrence_id in simulated_missing or not path.is_file():
                raise VerificationError(f"ocorrência selecionada ausente: {occurrence_id}")
            if sha256(path) != artifact["sha256"]:
                raise VerificationError(f"bytes divergentes: {occurrence_id}")
            validate_member(item, artifact, roots, selection_set["set_id"])
        if len(identities) != len(set(identities)):
            raise VerificationError(f"multiplicidade ambígua: {selection_set['set_id']}")

    if lock["selection_sets"] != expected_selection_sets:
        raise VerificationError("selection_sets divergem da Golden Reference")

    expected_abs = expected_absences(golden)
    if lock["explicit_absences"] != expected_abs:
        raise VerificationError("ausências explícitas divergem da Golden Reference")
    expected_deps = expected_dependencies(by_occurrence)
    if lock["dependencies"] != expected_deps:
        raise VerificationError("dependências divergem do perfil A4A")
    for dependency in lock["dependencies"]:
        artifact = by_occurrence[dependency["occurrence_id"]]
        path = artifact_path(artifact, roots)
        if dependency["occurrence_id"] in simulated_missing or not path.is_file() or sha256(path) != artifact["sha256"]:
            raise VerificationError(f"dependência ausente ou divergente: {dependency['dependency_id']}")
    if set(lock["constraints"]["restricted_local_occurrence_ids"]) != RESTRICTED_LOCAL:
        raise VerificationError("lista restricted_local diverge")
    for occurrence_id in RESTRICTED_LOCAL:
        artifact = by_occurrence[occurrence_id]
        path = artifact_path(artifact, roots)
        if occurrence_id in simulated_missing or not path.is_file() or sha256(path) != artifact["sha256"]:
            raise VerificationError(f"restricted_local ausente ou divergente: {occurrence_id}")
    if not all(lock["constraints"][key] is False for key in (
        "allow_glob", "allow_implicit_resolution", "allow_latest", "allow_regex_discovery", "allow_wildcard"
    )) or not lock["constraints"]["fail_closed"] or lock["mode"] != "SHADOW":
        raise VerificationError("constraints não preservam modo sombra fail-closed")

    absence_counts = Counter(x["absence_kind"] for x in lock["explicit_absences"])
    return {
        "ABSENCE_MATCH": True,
        "DEPENDENCY_MATCH": True,
        "EXTRA_ITEMS": 0,
        "MEMBER_MATCH": True,
        "MULTIPLICITY_MATCH": True,
        "ORDER_MATCH": True,
        "absence_counts": dict(sorted(absence_counts.items())),
        "dependencies": len(lock["dependencies"]),
        "lock_id": lock["lock_id"],
        "ordered_sets": sum(x["ordered"] for x in lock["selection_sets"]),
        "registry_entries": len(fragment["artifacts"]),
        "restricted_local": len(RESTRICTED_LOCAL),
        "result": "PASS",
        "selection_sets": len(lock["selection_sets"]),
        "semantic_items": sum(x["expected_count"] for x in lock["selection_sets"]),
        "unordered_sets": sum(not x["ordered"] for x in lock["selection_sets"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--simulate-missing", action="append", default=[])
    args = parser.parse_args()
    try:
        result = verify(args.lock.resolve(), set(args.simulate_missing))
    except (OSError, KeyError, TypeError, ValueError, VerificationError) as exc:
        print(json.dumps({"errors": [str(exc)], "result": "FAIL"}, ensure_ascii=False, sort_keys=True, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
