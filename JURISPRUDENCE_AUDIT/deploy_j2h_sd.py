"""JURISPRUDÊNCIA J2H: physical microSD deploy of J2H_CANDIDATE_B_OVER_A (Candidate B data over the physically approved Candidate A).
SD ONLY: the firmware is NOT flashed. After this deploy the card REQUIRES the generic firmware: SAFE_TO_BOOT_WITH_CURRENT_FIRMWARE = NO.
Same write path as deploy_j2g_sd.py / deploy_j2c_sd.py (temporary .LEX_NEW, fsync, os.replace, readback, sha256; created files are deleted
on rollback). Rollback restores Candidate A (299/186), NOT J2C.

Usage:
  python deploy_j2h_sd.py pre D: [--backup-root DIR]
  python deploy_j2h_sd.py copy D: [--backup-root DIR]
  python deploy_j2h_sd.py verify D: [--backup-root DIR]

Before any write: Candidate A physically approved (J2G 21/21); the WHOLE card byte-identical to the J2G post-deploy manifest
(<backup-root>/juris_j2g_physical_deploy/sd_manifest_post_full.json == committed J2G_PHYSICAL_DEPLOY copy); 299/186 recounted from the
card bytes; consolidated provisional gate PASS with the REAL date; firmware source gate PASS (FIRMWARE_BASELINE_REPRODUCIBILITY.json and
JURIS_TYPE_PROTOTYPE_BUILD.json recomputed in this mission). Backups (gitignored): <backup-root>/juris_j2h_physical_deploy/.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import deploy_j2g_sd as G  # noqa: E402  (manifest, diff, root_for, write_one, create_one, provisional_gate)
import build_j2b_isolation_audit as A  # noqa: E402

PKG = HERE / "J2H_CANDIDATE_B_OVER_A"
PKG_MANIFEST = PKG / "J2H_PACKAGE_MANIFEST.json"
A_VALIDATION = HERE / "J2G_PHYSICAL_DEPLOY" / "J2G_PHYSICAL_VALIDATION.json"
COMMITTED_BASELINE = HERE / "J2G_PHYSICAL_DEPLOY" / "sd_manifest_post_full.json"
FW_BASE = HERE / "FIRMWARE_REPRODUCIBILITY" / "FIRMWARE_BASELINE_REPRODUCIBILITY.json"
FW_PROTO = HERE / "JURIS_TYPE_PROTOTYPE" / "JURIS_TYPE_PROTOTYPE_BUILD.json"
BASE_VER = ("BUILD_ID|7fa6c609d2aadbc7", "GIT_COMMIT|64564d6d667440208a7f71dbf1150c262524e017")      # Candidate A (J2G)
ORDER = G.ORDER
LEGACY_IDX = G.LEGACY_IDX
PROTECTED = G.PROTECTED + tuple(G.CONTENT + n for n in ("STF_ADI_5017.TXT", "STF_RG_935.TXT", "STF_SV_46.TXT", "STF_ADI_7064.TXT"))
DIRS = G.DIRS
G.PKG = PKG                                      # write_one / create_one copy from THIS package


def stop(m):
    G.stop(m)


def plan() -> dict:
    m = json.loads(PKG_MANIFEST.read_text(encoding="utf-8"))
    if (m.get("package"), m.get("status")) != ("J2H_CANDIDATE_B_OVER_A", "HOST_ONLY_CANDIDATE") or (m["juris_relations"], m["juris_targets"]) != (315, 198) \
            or m["legacy"]["A_INDEX_PREFIX_IDENTICAL"] != "YES" or not (m["legacy"]["same_rows_as_j2f_b"] and m["legacy"]["same_lookup_tuples_as_j2f_b"]):
        stop("manifesto não é o pacote J2H (B sobre A, 315/198)")
    rows = {}
    for d in m["file_diff"]:
        rel = d["path"].lstrip("/")
        after, before = G.file_record(PKG / "candidate/SD" / rel), G.file_record(PKG / "rollback/SD" / rel)
        if after != {"bytes": d["after_bytes"], "sha256": d["after_sha256"]} or before != {"bytes": d["before_bytes"], "sha256": d["before_sha256"]}:
            stop("pacote diverge do manifesto: " + rel)
        rows[rel] = {"after": after, "before": before}
    if set(rows) != set(ORDER):
        stop("conjunto de substituições inesperado")
    creates = {}
    for d in m["file_additions"]:
        rel = d["path"].lstrip("/")
        after = G.file_record(PKG / "candidate/SD" / rel)
        if after != {"bytes": d["after_bytes"], "sha256": d["after_sha256"]} or d.get("rollback") != "DELETE" or not rel.startswith(G.CONTENT):
            stop("pacote diverge do manifesto (arquivo novo): " + rel)
        creates[rel] = {"after": after}
    if set(creates) & set(PROTECTED):
        stop("pacote recria ficha protegida")
    legacy = {}
    for rel in LEGACY_IDX:
        old, new = (PKG / "rollback/SD" / rel).read_bytes(), (PKG / "candidate/SD" / rel).read_bytes()
        if not new.startswith(old) or not old.endswith(b"\n"):
            stop("índice legado não preserva o prefixo do Candidato A: " + rel)
        legacy[rel] = {"A_INDEX_PREFIX_IDENTICAL": "YES", "OLD_OFFSETS_PRESERVED": "YES", "old_bytes": len(old), "appended_bytes": len(new) - len(old),
                       "old_lines": old.count(b"\n"), "appended_lines": new.count(b"\n") - old.count(b"\n")}
    tree = {f["path"].lstrip("/"): f["sha256"] for f in m["files"]}
    return {"replace": rows, "create": creates, "create_order": sorted(creates), "legacy": legacy, "tree": tree,
            "host": {k: m[k] for k in ("package", "build_id", "git_commit")}}


def gates() -> dict:
    v = json.loads(A_VALIDATION.read_text(encoding="utf-8"))
    if (v["J2G_PHYSICAL_VALIDATION"], v["CANDIDATE_A_PHYSICAL_APPROVED"], v["PHYSICAL_BASELINE_RELATIONS"], v["PHYSICAL_BASELINE_TARGETS"]) != \
            ("21/21 PASS", "YES", 299, 186):
        stop("Candidato A não está registrado como fisicamente aprovado (21/21, 299/186)")
    fb, fp = json.loads(FW_BASE.read_text(encoding="utf-8")), json.loads(FW_PROTO.read_text(encoding="utf-8"))
    fw = {"FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE": fb["FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE"],
          "GENERIC_FIRMWARE_PROTOTYPE": "PASS" if fp["base"]["vs_approved_metadata_only"] and fp["patch"]["firmware_tables_equal_host"]
          and fp["patch"]["other_files_identical"] and not fp["flashed"] else "FAIL",
          "PROGRAM_DELTA": fp["delta_vs_base"]["program_bytes"], "STATIC_RAM_DELTA": fp["delta_vs_base"]["static_ram_bytes"],
          "generic_app_sha256": fp["types_build"]["app_sha256"], "generic_app_bytes": fp["types_build"]["app_bin_bytes"]}
    if fw["FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE"] != "PASS" or fw["GENERIC_FIRMWARE_PROTOTYPE"] != "PASS":
        stop("gate de firmware não passou: " + json.dumps(fw))
    return {"A_physical_validation": v["J2G_PHYSICAL_VALIDATION"], "firmware": fw, "provisional_gate": G.provisional_gate()}


def recount(root: Path) -> tuple:
    rows = A.rows((root / "99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX").read_bytes())
    jv = [r for r in rows if r[1] == "JURISPRUDENCE" and r[2] == "CURRENT_VISIBLE"]
    return len(jv), len({r[0] for r in jv})


def baseline() -> dict:
    b = DIRS["baseline"].read_bytes()
    if b != COMMITTED_BASELINE.read_bytes():
        stop("manifesto físico J2G de backup diverge da cópia versionada")
    return json.loads(b.decode("utf-8"))["entries"]


def pre(drive: str):
    if (DIRS["out"] / "sd_manifest_pre_full.json").exists():
        stop("diretório de auditoria já existe: " + str(DIRS["out"]))
    root, ver = G.root_for(drive)
    if not all(x in ver for x in BASE_VER):
        stop("LEXV1.VER não é o Candidato A instalado")
    g = gates()
    p = plan()
    full = G.manifest(root, skip_system=True)
    d_base = G.diff(baseline(), full)
    if d_base != {"added": [], "removed": [], "changed": []}:
        stop("cartão diverge do manifesto físico do Candidato A: " + json.dumps(d_base, ensure_ascii=False)[:2000])
    count = recount(root)
    if count != (299, 186):
        stop(f"recontagem do cartão não é 299/186: {count}")
    for rel, r in p["replace"].items():
        if full.get(rel) != r["before"]:
            stop("arquivo a substituir não é o do Candidato A: " + rel)
    for rel in p["create_order"]:
        if rel in full or (root / rel).exists() or (root / rel).with_name(Path(rel).name + ".LEX_NEW").exists():
            stop("arquivo novo já existe no cartão: " + rel)
    G.dump("sd_manifest_pre_full.json", {"drive": drive, "excluded_os_metadata": sorted(G.IGNORED_ROOTS),
                                         "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "file_count": len(full), "entries": full})
    rows = {}
    for rel in ORDER:
        target = DIRS["out"] / "sd_pre" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, target)
        got = G.file_record(target)
        if got != full[rel] or got != p["replace"][rel]["before"]:
            stop("backup não confere: " + rel)
        rows[rel] = {"backup_path": str(target), **got}
    G.dump("sd_pre_backup_manifest.json", {"source": str(root), "backup": str(DIRS["out"] / "sd_pre"), "file_count": len(rows), "entries": rows,
                                           "ROLLBACK_TARGET": "Candidato A 299/186 (NÃO J2C)", "ROLLBACK_DELETE_FILES": p["create_order"],
                                           "ROLLBACK_TO_A_READY": "YES",
                                           "rollback_procedure": "1) apagar cada arquivo de ROLLBACK_DELETE_FILES; 2) restaurar os 7 arquivos de sd_pre "
                                                                 "(cópia PRE real do cartão com o Candidato A); 3) conferir o cartão com "
                                                                 "J2G_PHYSICAL_DEPLOY/sd_manifest_post_full.json (299/186)"})
    result = {"result": "PRE_OK", "drive": drive, "PREDEPLOY_SD_BASELINE": "299/186", "CANDIDATE_A_HASHES": "ALL_EXACT",
              "CARD_FILESET_MATCHES_A": "YES", "full_files": len(full), "baseline_diff": d_base, "recount_from_card": list(count),
              "PROVISIONAL_GATE": "PASS", "gates": g, "replace": list(ORDER), "create": p["create_order"], "legacy": p["legacy"],
              "candidate": p["host"], "ROLLBACK_TO_A_READY": "YES", "ROLLBACK_DELETE_FILES": len(p["create_order"]), "backup": rows}
    G.dump("physical_pre.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("backup", "gates", "create")}, ensure_ascii=False))
    print(json.dumps(g["firmware"]), [(x["source_id"], x["result"]) for x in g["provisional_gate"]["items"]], g["provisional_gate"]["as_of"])


def copy(drive: str):
    root, _ = G.root_for(drive)
    p = plan()
    if G.load("physical_pre.json").get("result") != "PRE_OK":
        stop("PRE não concluído")
    if G.manifest(root, skip_system=True) != G.load("sd_manifest_pre_full.json")["entries"]:
        stop("cartão mudou desde o manifesto pré")
    for rel in p["create_order"]:
        G.create_one(root, rel, p["create"][rel])
    for rel in ORDER:
        G.write_one(root, rel, p["replace"][rel])
    print("COPY_OK", "replaced", len(ORDER), "created", len(p["create_order"]))


def verify(drive: str):
    root, _ = G.root_for(drive)
    p = plan()
    pre_full = G.load("sd_manifest_pre_full.json")["entries"]
    post_full = G.manifest(root, skip_system=True)
    names = list(ORDER) + p["create_order"]
    readback = {rel: post_full.get(rel) for rel in names}
    expected = {**{rel: p["replace"][rel]["after"] for rel in ORDER}, **{rel: p["create"][rel]["after"] for rel in p["create_order"]}}
    mismatch = sorted(rel for rel in expected if readback[rel] != expected[rel])
    d_full = G.diff(pre_full, post_full)
    dev = json.loads((root / "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json").read_text(encoding="utf-8"))
    man_vs_card = {k: post_full.get(k, {}).get("sha256") == v["sha256"] for k, v in dev["files"].items() if k != "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json"}
    frozen = {rel: post_full.get(rel) == pre_full.get(rel) for rel in G.CORRELATA_FILES + G.ENTENDA_FILES + PROTECTED}
    legacy_prefix = {rel: (root / rel).read_bytes().startswith((DIRS["out"] / "sd_pre" / rel).read_bytes()) for rel in LEGACY_IDX}
    fileset = {k: post_full.get(k, {}).get("sha256") == h for k, h in p["tree"].items()}
    exact_fileset = set(post_full) == set(p["tree"])
    unexpected = len(set(d_full["changed"]) - set(ORDER)) + len(set(d_full["added"]) - set(p["create_order"])) + len(d_full["removed"])
    count = recount(root)
    ok = (not mismatch and d_full == {"added": p["create_order"], "removed": [], "changed": sorted(ORDER)} and all(man_vs_card.values())
          and all(frozen.values()) and all(legacy_prefix.values()) and all(fileset.values()) and exact_fileset and unexpected == 0 and count == (315, 198))
    G.dump("sd_manifest_post_full.json", {"drive": drive, "excluded_os_metadata": sorted(G.IGNORED_ROOTS),
                                          "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "file_count": len(post_full), "entries": post_full})
    result = {"result": "SD_VALIDATED" if ok else "SD_NOT_VALIDATED", "SD_HASHES": "PASS" if not mismatch else "FAIL",
              "MANIFEST_VS_SD": "PASS" if all(man_vs_card.values()) else "FAIL",
              "CARD_FILESET_MATCHES_B": "YES" if all(fileset.values()) and exact_fileset else "NO", "UNEXPECTED_SD_CHANGES": unexpected,
              "JURIS_RELATIONS": count[0], "JURIS_TARGETS": count[1], "readback": readback, "mismatch": mismatch, "diff_full": d_full,
              "files_replaced": len(d_full["changed"]), "files_created": len(d_full["added"]), "files_deleted": len(d_full["removed"]),
              "legacy_index_prefix_identical": legacy_prefix, "frozen_and_protected_files_unchanged": frozen,
              "rollback": {"target": "Candidato A 299/186", "restore_from": str(DIRS["out"] / "sd_pre"), "ROLLBACK_DELETE_FILES": p["create_order"]},
              "manifest_entries_checked": len(man_vs_card), "candidate_files_checked": len(fileset),
              "file_count_pre": len(pre_full), "file_count_post": len(post_full), "candidate": p["host"], "FIRMWARE_FLASHED": "NO",
              "SAFE_TO_BOOT_WITH_CURRENT_FIRMWARE": "NO"}
    G.dump("physical_validation.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("readback", "frozen_and_protected_files_unchanged", "diff_full")}, ensure_ascii=False))
    raise SystemExit(0 if ok else 3)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("pre", "copy", "verify"))
    ap.add_argument("drive")
    ap.add_argument("--backup-root", default=str(G.DI / "backups"))
    a = ap.parse_args()
    br = Path(a.backup_root)
    DIRS.update(out=br / "juris_j2h_physical_deploy", baseline=br / "juris_j2g_physical_deploy" / "sd_manifest_post_full.json")
    {"pre": pre, "copy": copy, "verify": verify}[a.step](a.drive.rstrip("\\/"))
