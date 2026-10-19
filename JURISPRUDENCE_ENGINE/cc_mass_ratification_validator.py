"""Valida decisões humanas da ratificação massiva sem materializar relações."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import build_cc_mass_ratification as B


GROUP_DECISIONS = {
    "PENDING",
    "APPROVE_GROUP",
    "REJECT_GROUP",
    "HOLD_GROUP",
    "APPROVE_GROUP_WITH_EXCEPTIONS",
}
ID_ACTIONS = {"APPROVE_IDS", "REJECT_IDS", "HOLD_IDS"}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(groups_doc: dict, decision_doc: dict, groups_bytes: bytes | None = None) -> list[str]:
    errors: list[str] = []
    if groups_doc.get("baseline") != B.BASELINE or decision_doc.get("baseline") != B.BASELINE:
        errors.append("baseline divergente")
    if groups_doc.get("audit_commit") != B.AUDIT_COMMIT or decision_doc.get("audit_commit") != B.AUDIT_COMMIT:
        errors.append("audit commit divergente")
    if groups_doc.get("group_hash_required") is not True:
        errors.append("GROUP_HASH_REQUIRED deve ser true")

    if groups_bytes is not None and decision_doc.get("groups_manifest_sha256") != _sha(groups_bytes):
        errors.append("hash do manifesto de grupos divergente")

    expected_groups = {}
    all_ids: set[str] = set()
    all_pairs: set[tuple[str, str]] = set()
    for group in groups_doc.get("groups", []):
        group_id = group.get("group_id")
        ids = group.get("relation_ids", [])
        expected_hash = B.group_hash(group_id, ids, group.get("version", ""))
        if group.get("sha256") != expected_hash:
            errors.append(f"hash de composição inválido: {group_id}")
        if group.get("relation_count") != len(ids) or len(ids) != len(set(ids)):
            errors.append(f"contagem/IDs duplicados no grupo: {group_id}")
        item_ids = [item.get("id") for item in group.get("items", [])]
        if item_ids != ids:
            errors.append(f"relation_ids e items divergem: {group_id}")
        if group.get("target_count") != len({item.get("target") for item in group.get("items", [])}):
            errors.append(f"target_count divergente: {group_id}")
        for item in group.get("items", []):
            item_id = item.get("id")
            if item_id in all_ids:
                errors.append(f"ID em mais de um grupo: {item_id}")
            all_ids.add(item_id)
            pair = (item.get("target"), item.get("precedent"))
            if pair in all_pairs:
                errors.append(f"par target/precedente duplicado: {pair}")
            all_pairs.add(pair)
            if item.get("current_human_decision") != "PENDING":
                errors.append(f"artefato-base não está PENDING: {item_id}")
            if item.get("authority_class") == "TURMA_ACORDAO" and item.get("classe") in {"REPETITIVO", "IAC", "SUMULA"}:
                errors.append(f"Turma promovida indevidamente a autoridade qualificada: {item_id}")
        expected_groups[group_id] = group

    if len(all_ids) != 681:
        errors.append(f"total de relações deve ser 681, obtido {len(all_ids)}")
    if set(expected_groups) != set(B.GROUP_META):
        errors.append("conjunto de grupos divergente")

    seen_decisions: set[str] = set()
    for entry in decision_doc.get("groups", []):
        group_id = entry.get("group_id")
        if group_id in seen_decisions:
            errors.append(f"decisão de grupo duplicada: {group_id}")
            continue
        seen_decisions.add(group_id)
        group = expected_groups.get(group_id)
        if not group:
            errors.append(f"grupo desconhecido: {group_id}")
            continue
        if entry.get("group_sha256") != group["sha256"]:
            errors.append(f"hash de decisão divergente: {group_id}")
        decision = entry.get("decision")
        if decision not in GROUP_DECISIONS:
            errors.append(f"decisão inválida: {group_id}: {decision}")
        exceptions = entry.get("exceptions", [])
        if len(exceptions) != len(set(exceptions)):
            errors.append(f"exceções duplicadas: {group_id}")
        unknown = sorted(set(exceptions) - set(group["relation_ids"]))
        if unknown:
            errors.append(f"exceções fora do grupo {group_id}: {unknown}")
        if decision == "APPROVE_GROUP_WITH_EXCEPTIONS" and not exceptions:
            errors.append(f"aprovação com exceções sem IDs: {group_id}")
        if decision != "APPROVE_GROUP_WITH_EXCEPTIONS" and exceptions:
            errors.append(f"exceções só são aceitas em APPROVE_GROUP_WITH_EXCEPTIONS: {group_id}")
    if seen_decisions != set(expected_groups):
        errors.append("template não contém exatamente uma decisão para cada grupo")

    acted_ids: set[str] = set()
    for action in decision_doc.get("id_actions", []):
        kind = action.get("action")
        ids = action.get("ids", [])
        if kind not in ID_ACTIONS:
            errors.append(f"ação por IDs inválida: {kind}")
        if not ids:
            errors.append(f"ação por IDs vazia: {kind}")
        unknown = sorted(set(ids) - all_ids)
        if unknown:
            errors.append(f"IDs desconhecidos em {kind}: {unknown}")
        repeated = sorted(set(ids) & acted_ids)
        if repeated:
            errors.append(f"IDs com decisões conflitantes: {repeated}")
        if len(ids) != len(set(ids)):
            errors.append(f"IDs duplicados em {kind}")
        acted_ids.update(ids)
    return errors


def validate_files(groups_path: Path, decision_path: Path) -> list[str]:
    raw = groups_path.read_bytes()
    return validate(json.loads(raw.decode("utf-8")), load(decision_path), raw)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision", nargs="?", type=Path, default=B.OUT / "CC_MASS_RATIFICATION_DECISION_TEMPLATE.json")
    parser.add_argument("--groups", type=Path, default=B.OUT / "CC_MASS_RATIFICATION_GROUPS.json")
    args = parser.parse_args()
    errors = validate_files(args.groups, args.decision)
    if errors:
        print("VALIDATION: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALIDATION: PASS")
    print("MATERIALIZATION: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
