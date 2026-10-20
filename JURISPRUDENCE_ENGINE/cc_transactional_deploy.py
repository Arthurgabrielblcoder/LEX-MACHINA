"""Deploy transacional host-side para os pacotes CC pós-Gate A.

O módulo não procura volumes nem acessa hardware por conta própria. Um destino real
precisa ser informado explicitamente e passar por confirmação, firmware declarado,
filesystem removível e backup externo. Clones de teste usam `.lex_mock_sd.json`.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LAYER = "99_JURISPRUDENCIA_V2/06_NORMALIZADO"
CONTENT = "99_JURISPRUDENCIA_V2/03_CONTEUDO"
AGGREGATES = (
    f"{LAYER}/JURISPRUDENCIA.IDX",
    f"{LAYER}/MULTINORM_MANIFEST.json",
    f"{LAYER}/LAYER.VER",
    f"{LAYER}/JUR_LOOKUP.IDX",  # lookup sempre por último
)
INJECTIONS = {"after_partial_fichas", "before_replace", "after_first_normalized", "before_lookup", "after_lookup"}


class RefuseWrite(RuntimeError):
    pass


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_record(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": sha_bytes(path.read_bytes())}


def atomic_bytes(path: Path, data: bytes, suffix: str = ".lex.tmp") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + suffix)
    if tmp.exists():
        raise RefuseWrite(f"temporário preexistente: {tmp}")
    with tmp.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    if sha_bytes(tmp.read_bytes()) != sha_bytes(data):
        tmp.unlink(missing_ok=True)
        raise IOError(f"readback divergente: {tmp}")
    os.replace(tmp, path)


def load_profile(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema_version") != 1 or tuple(doc.get("aggregate_order", ())) != AGGREGATES:
        raise RefuseWrite("perfil inválido ou ordem transacional divergente")
    return doc


def source_bytes(meta: dict) -> bytes:
    path = ROOT / meta["repository_path"]
    data = path.read_bytes()
    if {"bytes": len(data), "sha256": sha_bytes(data)} != {"bytes": meta["bytes"], "sha256": meta["sha256"]}:
        raise RefuseWrite(f"fonte divergiu: {meta['repository_path']}")
    return data


def is_mock(root: Path) -> bool:
    return (root / ".lex_mock_sd.json").is_file()


def windows_volume(root: Path) -> tuple[bool, str]:
    anchor = root.resolve().anchor
    if os.name != "nt" or not anchor:
        return False, "UNKNOWN"
    drive_type = ctypes.windll.kernel32.GetDriveTypeW(anchor)
    fs_name = ctypes.create_unicode_buffer(32)
    ok = ctypes.windll.kernel32.GetVolumeInformationW(anchor, None, 0, None, None, None, fs_name, len(fs_name))
    return drive_type == 2, fs_name.value.upper() if ok else "UNKNOWN"


def guard_destination(root: Path, *, write: bool, confirm: str | None, firmware: str | None, profile: dict,
                      backup_dir: Path | None) -> bool:
    root = root.resolve()
    mock = is_mock(root)
    if not root.is_dir() or not (root / LAYER).is_dir() or not (root / CONTENT).is_dir():
        raise RefuseWrite("estrutura de SD esperada ausente")
    if mock:
        return True
    removable, filesystem = windows_volume(root)
    if not removable or filesystem not in {"FAT", "FAT32", "EXFAT"}:
        raise RefuseWrite(f"destino real deve ser removível FAT/FAT32/exFAT; detectado {filesystem}")
    if any((root / marker).exists() for marker in ("bootloader.bin", "partitions.bin", "firmware.bin")):
        raise RefuseWrite("destino parece mídia de firmware ESP32")
    if write:
        if confirm != profile["confirmation_token"]:
            raise RefuseWrite("confirmação física explícita ausente")
        if firmware != profile["firmware_requirement"]["sha256"]:
            raise RefuseWrite("firmware Gate A não confirmado")
        if backup_dir is None or backup_dir.resolve().anchor == root.anchor:
            raise RefuseWrite("backup real deve ser informado fora do volume removível")
    return False


def semantic_counts(root: Path) -> dict:
    records = (root / AGGREGATES[0]).read_text(encoding="utf-8").splitlines()
    rows = []
    for line in records:
        if line and not line.startswith("#"):
            fields = line.split("|")
            if len(fields) >= 7:
                target = fields[0][len(fields[6]) + 1:]
                rows.append((target, fields[6]))
    cc = [(target, precedent) for target, precedent in rows if target.startswith("CC2002:")]
    cf = [(target, precedent) for target, precedent in rows if not target.startswith("CC2002:")]
    lookup = [line for line in (root / AGGREGATES[3]).read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]
    return {"cc_relations": len(cc), "cc_targets": len({x[0] for x in cc}),
            "cf_adct_normalized_relations": len(cf), "cf_adct_normalized_targets": len({x[0] for x in cf}),
            "lookup_entries": len(lookup)}


def detect_state(root: Path, profile: dict) -> tuple[str | None, dict]:
    actual = {}
    for rel in AGGREGATES:
        path = root / rel
        actual[rel] = file_record(path) if path.is_file() else None
    expected_record = lambda values: {key: {"bytes": value["bytes"], "sha256": value["sha256"]} for key, value in values.items()}
    for name, state in profile["allowed_pre_states"].items():
        if actual == expected_record(state["aggregates"]):
            return name, actual
    if actual == expected_record(profile["post_state"]["aggregates"]):
        return "POST", actual
    return None, actual


def preflight(root: Path, profile: dict, *, write: bool = False, confirm: str | None = None,
              firmware: str | None = None, backup_dir: Path | None = None) -> dict:
    mock = guard_destination(root, write=write, confirm=confirm, firmware=firmware, profile=profile, backup_dir=backup_dir)
    state, actual = detect_state(root, profile)
    semantic = semantic_counts(root)
    if state is None:
        raise RefuseWrite("hashes dos quatro agregados não correspondem a estado autorizado")
    expected = profile["post_state"] if state == "POST" else profile["allowed_pre_states"][state]
    if semantic != expected["semantic"]:
        raise RefuseWrite(f"recontagem semântica divergente: {semantic}")
    if not mock:
        baseline_doc = json.loads((ROOT / profile["physical_baseline_manifest"]).read_text(encoding="utf-8"))["entries"]
        exempt = set(AGGREGATES) | set(profile["content_files"])
        failures = []
        for rel, meta in baseline_doc.items():
            if rel in exempt:
                continue
            path = root / rel
            if not path.is_file() or file_record(path) != {"bytes": meta["bytes"], "sha256": meta["sha256"]}:
                failures.append(rel)
        physical_files = sum(1 for path in root.rglob("*") if path.is_file())
        if failures or physical_files < len(baseline_doc):
            raise RefuseWrite(f"inventário físico baseline divergente: {len(failures)} hashes; {physical_files}/{len(baseline_doc)} arquivos")
        from deploy_cc_j1_sd import recount_lexv1
        _, cf_relations, cf_targets = recount_lexv1(root)
        if (cf_relations, cf_targets) != (315, 198):
            raise RefuseWrite(f"recontagem CF/ADCT LexV1 divergente: {cf_relations}/{cf_targets}")
    content = {}
    for rel, meta in profile["content_files"].items():
        path = root / rel
        content[rel] = file_record(path) if path.is_file() else None
        if content[rel] is not None and content[rel] != {"bytes": meta["bytes"], "sha256": meta["sha256"]}:
            raise RefuseWrite(f"colisão de ficha: {rel}")
    if state != "POST" and any(content.values()):
        expected_present = set(profile["allowed_pre_states"][state].get("content_present", ()))
        unexpected = sorted(rel for rel, value in content.items() if value and rel not in expected_present)
        if unexpected:
            raise RefuseWrite(f"fixture/conteúdo parcial não autorizado: {unexpected[:3]}")
    return {"result": "PREFLIGHT_OK", "mock": mock, "state": state, "semantic": semantic,
            "CF_ADCT_LEXV1": "NOT_APPLICABLE_SYNTHETIC_MOCK" if mock else "315/198", "aggregates": actual}


def backup(root: Path, profile: dict, backup_dir: Path, pre: dict) -> dict:
    tx = backup_dir / profile["name"]
    if tx.exists():
        shutil.rmtree(tx)
    (tx / "aggregates").mkdir(parents=True)
    items = {}
    for rel in AGGREGATES:
        src = root / rel
        dst = tx / "aggregates" / Path(rel).name
        shutil.copyfile(src, dst)
        items[rel] = {**file_record(dst), "backup_path": str(dst.resolve())}
    manifest = {"schema_version": 1, "profile": profile["name"], "pre_state": pre["state"], "aggregates": items,
                "created_content": [], "result": "BACKUP_READY"}
    atomic_bytes(tx / "transaction.json", (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
    return manifest


def _save_tx(backup_dir: Path, profile: dict, tx_doc: dict) -> None:
    atomic_bytes(backup_dir / profile["name"] / "transaction.json",
                 (json.dumps(tx_doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(), ".update.tmp")


def rollback(root: Path, profile: dict, backup_dir: Path) -> dict:
    tx_path = backup_dir / profile["name"] / "transaction.json"
    if not tx_path.is_file():
        raise RefuseWrite("manifesto transacional de rollback ausente")
    tx = json.loads(tx_path.read_text(encoding="utf-8"))
    if tx.get("profile") != profile["name"]:
        raise RefuseWrite("backup pertence a outro perfil")
    for rel in AGGREGATES:
        meta = tx["aggregates"][rel]
        data = Path(meta["backup_path"]).read_bytes()
        if {"bytes": len(data), "sha256": sha_bytes(data)} != {"bytes": meta["bytes"], "sha256": meta["sha256"]}:
            raise RefuseWrite(f"backup corrompido: {rel}")
        atomic_bytes(root / rel, data, ".restore.tmp")
    for rel in tx.get("created_content", []):
        path = root / rel
        if path.exists():
            expected = profile["content_files"][rel]
            if file_record(path) != {"bytes": expected["bytes"], "sha256": expected["sha256"]}:
                raise RefuseWrite(f"recusa apagar ficha divergente: {rel}")
            path.unlink()
    state, _ = detect_state(root, profile)
    semantic = semantic_counts(root)
    expected = profile["allowed_pre_states"][tx["pre_state"]]
    if state != tx["pre_state"] or semantic != expected["semantic"]:
        raise RefuseWrite("rollback não restaurou estado PRE")
    tx["result"] = "ROLLBACK_PASS"
    _save_tx(backup_dir, profile, tx)
    byte_exact = all(file_record(root / rel) == {"bytes": tx["aggregates"][rel]["bytes"],
                                                "sha256": tx["aggregates"][rel]["sha256"]}
                     for rel in AGGREGATES)
    return {"result": "ROLLBACK_PASS", "restored_state": state, "semantic": semantic, "byte_exact": byte_exact}


def deploy(root: Path, profile: dict, backup_dir: Path, *, confirm: str | None = None, firmware: str | None = None,
           inject: str | None = None) -> dict:
    if inject and inject not in INJECTIONS:
        raise RefuseWrite("ponto de falha desconhecido")
    pre = preflight(root, profile, write=True, confirm=confirm, firmware=firmware, backup_dir=backup_dir)
    if pre["state"] == "POST":
        return {"result": "ALREADY_DEPLOYED_NOOP", "semantic": pre["semantic"]}
    required = sum(meta["bytes"] for rel, meta in profile["content_files"].items() if not (root / rel).exists())
    required += 2 * sum(meta["bytes"] for meta in profile["post_state"]["aggregates"].values())
    if shutil.disk_usage(root).free < required:
        raise RefuseWrite(f"espaço livre insuficiente: requer {required} bytes")
    tx = backup(root, profile, backup_dir, pre)
    try:
        pending = [(rel, meta) for rel, meta in profile["content_files"].items() if not (root / rel).exists()]
        for index, (rel, meta) in enumerate(pending):
            atomic_bytes(root / rel, source_bytes(meta), ".content.tmp")
            tx["created_content"].append(rel)
            _save_tx(backup_dir, profile, tx)
            if inject == "after_partial_fichas" and index >= max(0, len(pending) // 2 - 1):
                raise IOError("INJECTED after_partial_fichas")
        if inject == "before_replace":
            raise IOError("INJECTED before_replace")
        staged = {}
        for rel in AGGREGATES:
            meta = profile["post_state"]["aggregates"][rel]
            data = source_bytes(meta)
            tmp = (root / rel).with_name(Path(rel).name + ".stage.tmp")
            with tmp.open("xb") as handle:
                handle.write(data); handle.flush(); os.fsync(handle.fileno())
            if file_record(tmp) != {"bytes": meta["bytes"], "sha256": meta["sha256"]}:
                raise IOError(f"staging divergente: {rel}")
            staged[rel] = tmp
        for index, rel in enumerate(AGGREGATES):
            if rel.endswith("JUR_LOOKUP.IDX") and inject == "before_lookup":
                raise IOError("INJECTED before_lookup")
            os.replace(staged[rel], root / rel)
            if index == 0 and inject == "after_first_normalized":
                raise IOError("INJECTED after_first_normalized")
            if rel.endswith("JUR_LOOKUP.IDX") and inject == "after_lookup":
                raise IOError("INJECTED after_lookup")
        post = preflight(root, profile)
        if post["state"] != "POST":
            raise IOError("verificação POST falhou")
        tx["result"] = "DEPLOY_PASS"; _save_tx(backup_dir, profile, tx)
        return {"result": "DEPLOY_PASS", "from_state": pre["state"], "semantic": post["semantic"],
                "content_created": len(tx["created_content"])}
    except Exception as exc:
        for rel in AGGREGATES:
            (root / rel).with_name(Path(rel).name + ".stage.tmp").unlink(missing_ok=True)
        restored = rollback(root, profile, backup_dir)
        return {"result": "INJECTED_FAILURE_ROLLED_BACK" if inject else "DEPLOY_FAILURE_ROLLED_BACK",
                "error": str(exc), "rollback": restored}


def verify(root: Path, profile: dict) -> dict:
    result = preflight(root, profile)
    if result["state"] != "POST":
        raise RefuseWrite("estado não é POST")
    missing = [rel for rel, meta in profile["content_files"].items()
               if not (root / rel).is_file() or file_record(root / rel) != {"bytes": meta["bytes"], "sha256": meta["sha256"]}]
    if missing:
        raise RefuseWrite(f"fichas POST ausentes/divergentes: {missing[:3]}")
    return {"result": "VERIFY_PASS", "semantic": result["semantic"], "content": len(profile["content_files"])}


def cli(profile_path: Path, argv: list[str] | None = None, forced_mode: str | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    modes = parser.add_mutually_exclusive_group(required=forced_mode is None)
    modes.add_argument("--preflight", action="store_true"); modes.add_argument("--deploy", action="store_true")
    modes.add_argument("--verify", action="store_true"); modes.add_argument("--rollback", action="store_true")
    modes.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--confirm-physical-deploy")
    parser.add_argument("--firmware-approved")
    parser.add_argument("--inject-failure", choices=sorted(INJECTIONS), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    profile = load_profile(profile_path)
    mode = forced_mode or next(name for name in ("preflight", "deploy", "verify", "rollback", "dry_run") if getattr(args, name))
    root = args.root.resolve()
    backup_dir = (args.backup_dir or (root / "._lex_mock_backups")).resolve()
    try:
        if mode in {"preflight", "dry_run"}:
            result = preflight(root, profile)
            result["result"] = "DRY_RUN_PASS" if mode == "dry_run" else result["result"]
        elif mode == "deploy":
            result = deploy(root, profile, backup_dir, confirm=args.confirm_physical_deploy,
                            firmware=args.firmware_approved, inject=args.inject_failure)
        elif mode == "verify":
            result = verify(root, profile)
        else:
            guard_destination(root, write=True, confirm=args.confirm_physical_deploy, firmware=args.firmware_approved,
                              profile=profile, backup_dir=backup_dir)
            result = rollback(root, profile, backup_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (RefuseWrite, OSError, ValueError) as exc:
        print(json.dumps({"result": "REFUSE_WRITE", "reason": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit("use um wrapper de fixture ou mass deploy")
