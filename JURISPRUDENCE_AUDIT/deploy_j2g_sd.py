"""JURISPRUDÊNCIA J2G: physical microSD deploy of J2F CANDIDATE A (J2_CURRENT_FW_CANDIDATE: J2C + Batch02 J2E-A + group A of the ratified
Batches 03–09; SD ONLY, the firmware is NOT touched). Same flow and safeguards as deploy_j2c_sd.py: new files are CREATED (target must not exist,
temporary .LEX_NEW, fsync, os.replace, readback, sha256; rollback of a created file = DELETE); replaced files are backed up from the real card
first (rollback = restore PRE bytes).

Usage:
  python deploy_j2g_sd.py pre D: [--backup-root DIR]
  python deploy_j2g_sd.py copy D: [--backup-root DIR]
  python deploy_j2g_sd.py verify D: [--backup-root DIR]

The allowed physical changes are DERIVED from J2F_CANDIDATES_HOST_ONLY/J2_CURRENT_FW_CANDIDATE/J2F_PACKAGE_MANIFEST.json (file_diff = replaced,
file_additions = created) and cross-checked with CF88_JURIS_ADDITIONS_J2F.json (group A only). Before any write:
  * 301×261 reconciliation PASS (261/160 physical; 301 = legacy index rows, never a relation count);
  * consolidated provisional gate (ADI 7697, ADI 5017, ADPF 378, Rcl 84738) PASS with the REAL date of the deploy;
  * the WHOLE card byte-identical to the J2C physical manifest (<backup-root>/juris_j2c_physical_deploy/sd_manifest_post_full.json, equal
    to the committed JURISPRUDENCE_AUDIT/J2C_PHYSICAL_DEPLOY/sd_manifest_post_full.json);
  * legacy indexes of the candidate APPEND-ONLY over the card bytes.
Backups (gitignored) go to <backup-root>/juris_j2g_physical_deploy/ (never overwritten).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DI = ROOT / "DEVICE_INTEGRATION"
sys.path.insert(0, str(HERE))
PKG = HERE / "J2F_CANDIDATES_HOST_ONLY" / "J2_CURRENT_FW_CANDIDATE"
PKG_MANIFEST = PKG / "J2F_PACKAGE_MANIFEST.json"
FORBIDDEN_PKG = HERE / "J2F_CANDIDATES_HOST_ONLY" / "J2_GENERIC_FW_CANDIDATE"
ADDITIONS = ROOT / "LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2F.json"
PROV = HERE / "J2_PROVISIONAL_REGISTRY.json"
COMMITTED_BASELINE = HERE / "J2C_PHYSICAL_DEPLOY" / "sd_manifest_post_full.json"
LEGACY_IDX = ("99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX", "99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX")
CONTENT = "99_JURISPRUDENCIA_V2/03_CONTEUDO/"
IGNORED_ROOTS = {"System Volume Information"}
CHUNK = 1 << 20
ORDER = LEGACY_IDX + ("99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX", "99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX", "99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX",
                      "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json", "99_LEX_V1/00_SYS/LEXV1.VER")
PROTECTED = (CONTENT + "STF_RG_558.TXT", CONTENT + "STF_RG_367.TXT", CONTENT + "STF_RG_387.TXT", CONTENT + "STF_ADI_7697.TXT",
             CONTENT + "STF_ADI_4425.TXT", CONTENT + "STF_SV_25.TXT")
CORRELATA_FILES = ("99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX", "99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX",
                   "99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX")
ENTENDA_FILES = ("99_LEX_V1/30_ENTENDA/ENTENDA_LOOKUP.IDX", "99_LEX_V1/30_ENTENDA/ENTENDA_PAYLOAD.DAT")
BASE_VER = ("BUILD_ID|12b9fb5624112d9e", "GIT_COMMIT|de0b1812a9bf0d3c89d3bb094bb7bf0012a36625")     # J2C (installed J2B.1)
DIRS = {}


def stop(message: str):
    raise SystemExit("PARAR: " + message)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def file_record(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": sha(path)}


def manifest(root: Path, skip_system=False) -> dict:
    entries = {}
    for dirpath, dirnames, filenames in os.walk(root):
        if skip_system and Path(dirpath) == root:
            dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_ROOTS)
        else:
            dirnames.sort()
        for name in sorted(filenames):
            path = Path(dirpath) / name
            entries[path.relative_to(root).as_posix()] = file_record(path)
    return dict(sorted(entries.items()))


def dump(name: str, value: dict):
    DIRS["out"].mkdir(parents=True, exist_ok=True)
    (DIRS["out"] / name).write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def load(name: str) -> dict:
    return json.loads((DIRS["out"] / name).read_text(encoding="utf-8"))


def diff(before: dict, after: dict) -> dict:
    return {"added": sorted(set(after) - set(before)), "removed": sorted(set(before) - set(after)),
            "changed": sorted(k for k in set(before) & set(after) if before[k] != after[k])}


def root_for(drive: str) -> tuple[Path, list[str]]:
    root = Path(drive.rstrip("\\/") + os.sep)
    required = [root / "99_LEX_V1" / d for d in ("00_SYS", "05_TEXT", "10_TARGETS", "20_REFERENCES", "30_ENTENDA")]
    required.append(root / "99_RELATIONS_V2" / "05_INDICES_ESP32_V2")
    if not all(p.is_dir() for p in required):
        stop("assinatura /99_LEX_V1 + /99_RELATIONS_V2 incompleta em " + str(root))
    if not any(p.is_dir() and p.name.startswith("1- CONSTITUI") for p in root.iterdir()):
        stop("assinatura do acervo jurídico ausente")
    ver = (root / "99_LEX_V1/00_SYS/LEXV1.VER").read_text(encoding="utf-8").splitlines()
    return root, ver


def plan() -> dict:
    m = json.loads(PKG_MANIFEST.read_text(encoding="utf-8"))
    if (m.get("status"), m.get("package"), m.get("variant")) != ("HOST_ONLY_CANDIDATE", "J2_CURRENT_FW_CANDIDATE", "A") or not (
            m.get("physical_baseline_reproduced") and m.get("byte_identical_rebuild") and m.get("device_manifest_matches_package")
            and m.get("legacy_append_only") and m.get("temas_367_387_fichas_untouched")) or m.get("firmware_files") is not None:
        stop("manifesto do pacote não é o Candidato A determinístico (firmware atual)")
    if PKG == FORBIDDEN_PKG:
        stop("Candidato B não pode ser usado nesta missão")
    rows = {}
    for d in m["file_diff"]:
        rel = d["path"].lstrip("/")
        cand, back = PKG / "candidate/SD" / rel, PKG / "rollback/SD" / rel
        after, before = file_record(cand), file_record(back)
        if after != {"bytes": d["after_bytes"], "sha256": d["after_sha256"]} or before != {"bytes": d["before_bytes"], "sha256": d["before_sha256"]}:
            stop("pacote diverge do manifesto: " + rel)
        rows[rel] = {"after": after, "before": before}
    if set(rows) != set(ORDER):
        stop("conjunto de substituições inesperado: " + json.dumps(sorted(rows)))
    add = json.loads(ADDITIONS.read_text(encoding="utf-8"))
    expected_new = sorted({CONTENT + r["source_id"].replace(":", "_").replace("/", "_") + ".TXT"
                           for r in add["records"] if r["group"] == "A" and r["new_ficha"]})
    creates = {}
    for d in m["file_additions"]:
        rel = d["path"].lstrip("/")
        after = file_record(PKG / "candidate/SD" / rel)
        if after != {"bytes": d["after_bytes"], "sha256": d["after_sha256"]} or d.get("rollback") != "DELETE" or not rel.startswith(CONTENT):
            stop("pacote diverge do manifesto (arquivo novo): " + rel)
        creates[rel] = {"after": after}
    if sorted(creates) != expected_new:
        stop("arquivos novos não batem com as fichas do grupo A: " + json.dumps(sorted(set(creates) ^ set(expected_new))))
    if set(creates) & set(PROTECTED):
        stop("pacote recria ficha protegida")
    legacy = {}
    for rel in LEGACY_IDX:                                   # append-only: card bytes are an exact prefix; old offsets preserved
        old, new = (PKG / "rollback/SD" / rel).read_bytes(), (PKG / "candidate/SD" / rel).read_bytes()
        if not new.startswith(old) or not old.endswith(b"\n"):
            stop("índice legado não é append-only: " + rel)
        legacy[rel] = {"LEGACY_PREFIX_IDENTICAL": "YES", "OLD_OFFSETS_PRESERVED": "YES", "old_bytes": len(old), "appended_bytes": len(new) - len(old),
                       "old_lines": old.count(b"\n"), "appended_lines": new.count(b"\n") - old.count(b"\n")}
    keep = {f["path"].lstrip("/"): f["sha256"] for f in m["files"] if f["same_as_physical"]}
    return {"replace": rows, "create": creates, "create_order": sorted(creates), "keep": keep, "legacy": legacy,
            "host": {k: m[k] for k in ("package", "build_id", "git_commit")}}


def reconciliation() -> dict:
    import build_baseline_reconciliation as R
    d = json.loads(R.build())
    rec = {"PHYSICAL_RELATIONS": d["PHYSICAL_BASELINE_RELATIONS"], "PHYSICAL_TARGETS": d["PHYSICAL_BASELINE_TARGETS"],
           "LEGACY_INDEX_ROWS": d["legacy_index"]["LEGACY_JURIS_RECORDS"], "RECONCILED": d["PHYSICAL_BASELINE_RECONCILED"]}
    rec["301_NOT_EQUAL_PHYSICAL_RELATIONS"] = rec["LEGACY_INDEX_ROWS"] != rec["PHYSICAL_RELATIONS"]
    if (rec["PHYSICAL_RELATIONS"], rec["PHYSICAL_TARGETS"], rec["LEGACY_INDEX_ROWS"], rec["RECONCILED"]) != (261, 160, 301, "PASS") \
            or not rec["301_NOT_EQUAL_PHYSICAL_RELATIONS"]:
        stop("reconciliação 301×261 não passou: " + json.dumps(rec))
    return rec


def provisional_gate() -> dict:
    import check_j2b_provisional as G
    today = dt.date.today()
    res = G.check(today, PROV)
    if not res or not all(r["result"] == "PASS" for r in res):
        stop("gate consolidado de provisórios não passou: " + json.dumps(res, ensure_ascii=False))
    return {"as_of": today.isoformat(), "registry": PROV.name, "items": res}


def baseline() -> dict:
    b = DIRS["baseline"].read_bytes()
    if b != COMMITTED_BASELINE.read_bytes():
        stop("manifesto físico J2C de backup diverge da cópia versionada")
    return json.loads(b.decode("utf-8"))["entries"]


def pre(drive: str):
    if (DIRS["out"] / "sd_manifest_pre_full.json").exists():
        stop("diretório de auditoria já existe: " + str(DIRS["out"]))
    root, ver = root_for(drive)
    if not all(x in ver for x in BASE_VER):
        stop("LEXV1.VER não é o J2C instalado")
    rec = reconciliation()
    gate = provisional_gate()
    p = plan()
    full = manifest(root, skip_system=True)
    d_base = diff(baseline(), full)
    if d_base != {"added": [], "removed": [], "changed": []}:
        stop("cartão diverge do manifesto físico J2C: " + json.dumps(d_base, ensure_ascii=False)[:2000])
    for rel, r in p["replace"].items():
        if full.get(rel) != r["before"]:
            stop("arquivo a substituir não está no baseline aprovado: " + rel)
    for rel, h in p["keep"].items():
        if full.get(rel, {}).get("sha256") != h:
            stop("arquivo KEEP diverge do pacote: " + rel)
    for rel in p["create_order"]:
        if rel in full or (root / rel).exists() or (root / rel).with_name(Path(rel).name + ".LEX_NEW").exists():
            stop("arquivo novo já existe no cartão: " + rel)
    dump("sd_manifest_pre_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                       "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "file_count": len(full), "entries": full})
    rows = {}
    for rel in ORDER:
        target = DIRS["out"] / "sd_pre" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, target)
        got = file_record(target)
        if got != full[rel] or got != p["replace"][rel]["before"]:
            stop("backup não confere: " + rel)
        rows[rel] = {"backup_path": str(target), **got}
    dump("sd_pre_backup_manifest.json", {"source": str(root), "backup": str(DIRS["out"] / "sd_pre"), "file_count": len(rows), "entries": rows,
                                         "ROLLBACK_DELETE_FILES": p["create_order"], "ROLLBACK_READY": "YES",
                                         "rollback_procedure": "1) apagar cada arquivo de ROLLBACK_DELETE_FILES; 2) restaurar os 7 arquivos de sd_pre "
                                                               "(cópia PRE real do cartão); 3) conferir o cartão com o manifesto físico J2C"})
    result = {"result": "PRE_OK", "drive": drive, "PREDEPLOY_SD_BASELINE": "PASS", "full_files": len(full), "baseline_diff": d_base,
              "reconciliation": rec, "PROVISIONAL_GATE": "PASS", "provisional_gate": gate, "replace": list(ORDER), "create": p["create_order"],
              "create_targets_absent": True, "legacy_append_only": p["legacy"], "keep_in_package": len(p["keep"]), "candidate": p["host"],
              "ROLLBACK_READY": "YES", "ROLLBACK_DELETE_FILES": len(p["create_order"]), "backup": rows}
    dump("physical_pre.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("backup", "provisional_gate", "create")}, ensure_ascii=False))


def write_one(root: Path, rel: str, r: dict):
    source, target = PKG / "candidate/SD" / rel, root / rel
    temporary = target.with_name(target.name + ".LEX_NEW")
    if temporary.exists():
        stop("temporário já existe: " + rel)
    if file_record(target) != r["before"]:
        stop("destino mudou: " + rel)
    with source.open("rb") as fi, temporary.open("xb") as fo:
        for block in iter(lambda: fi.read(CHUNK), b""):
            fo.write(block)
        fo.flush()
        os.fsync(fo.fileno())
    if file_record(temporary) != r["after"]:
        stop("readback temporário diverge: " + rel)
    os.replace(temporary, target)
    got = file_record(target)
    if got != r["after"]:
        stop("readback final diverge: " + rel)
    print("REPLACE", rel, got["bytes"], got["sha256"])


def create_one(root: Path, rel: str, r: dict):
    source, target = PKG / "candidate/SD" / rel, root / rel
    temporary = target.with_name(target.name + ".LEX_NEW")
    if target.exists() or temporary.exists():
        stop("arquivo novo ou temporário já existe: " + rel)
    with source.open("rb") as fi, temporary.open("xb") as fo:
        for block in iter(lambda: fi.read(CHUNK), b""):
            fo.write(block)
        fo.flush()
        os.fsync(fo.fileno())
    if file_record(temporary) != r["after"]:
        stop("readback temporário diverge: " + rel)
    if target.exists():
        stop("destino surgiu durante a escrita: " + rel)
    os.replace(temporary, target)
    got = file_record(target)
    if got != r["after"]:
        stop("readback final diverge: " + rel)
    print("CREATE", rel, got["bytes"], got["sha256"])


def copy(drive: str):
    root, _ = root_for(drive)
    p = plan()
    if load("physical_pre.json").get("result") != "PRE_OK":
        stop("PRE não concluído")
    if manifest(root, skip_system=True) != load("sd_manifest_pre_full.json")["entries"]:
        stop("cartão mudou desde o manifesto pré")
    for rel in p["create_order"]:                # new fichas first: unreferenced until the indexes change
        create_one(root, rel, p["create"][rel])
    for rel in ORDER:
        write_one(root, rel, p["replace"][rel])
    print("COPY_OK", "replaced", len(ORDER), "created", len(p["create_order"]))


def verify(drive: str):
    root, _ = root_for(drive)
    p = plan()
    pre_full = load("sd_manifest_pre_full.json")["entries"]
    post_full = manifest(root, skip_system=True)
    names = list(ORDER) + p["create_order"]
    readback = {rel: post_full.get(rel) for rel in names}
    expected = {**{rel: p["replace"][rel]["after"] for rel in ORDER}, **{rel: p["create"][rel]["after"] for rel in p["create_order"]}}
    mismatch = sorted(rel for rel in expected if readback[rel] != expected[rel])
    d_full = diff(pre_full, post_full)
    dev = json.loads((root / "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json").read_text(encoding="utf-8"))
    man_vs_card = {k: post_full.get(k, {}).get("sha256") == v["sha256"] for k, v in dev["files"].items() if k != "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json"}
    frozen = {rel: post_full.get(rel) == pre_full.get(rel) for rel in CORRELATA_FILES + ENTENDA_FILES + PROTECTED}
    legacy_prefix = {rel: (root / rel).read_bytes().startswith((DIRS["out"] / "sd_pre" / rel).read_bytes()) for rel in LEGACY_IDX}
    pkg_tree = {f["path"].lstrip("/"): f["sha256"] for f in json.loads(PKG_MANIFEST.read_text(encoding="utf-8"))["files"]}
    fileset = {k: post_full.get(k, {}).get("sha256") == h for k, h in pkg_tree.items()}
    unexpected = len(set(d_full["changed"]) - set(ORDER)) + len(set(d_full["added"]) - set(p["create_order"])) + len(d_full["removed"])
    ok = (not mismatch and d_full == {"added": p["create_order"], "removed": [], "changed": sorted(ORDER)} and all(man_vs_card.values())
          and all(frozen.values()) and all(legacy_prefix.values()) and all(fileset.values()) and unexpected == 0
          and all(post_full.get(rel, {}).get("sha256") == h for rel, h in p["keep"].items()))
    dump("sd_manifest_post_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "file_count": len(post_full), "entries": post_full})
    result = {"result": "SD_VALIDATED" if ok else "SD_NOT_VALIDATED", "SD_HASHES": "ALL_EXACT" if not mismatch else "MISMATCH",
              "MANIFEST_VS_SD": "PASS" if all(man_vs_card.values()) else "FAIL",
              "CARD_FILESET_MATCHES_CANDIDATE": "YES" if all(fileset.values()) else "NO", "UNEXPECTED_SD_CHANGES": unexpected,
              "readback": readback, "mismatch": mismatch, "diff_full": d_full,
              "files_replaced": len(d_full["changed"]), "files_created": len(d_full["added"]), "files_deleted": len(d_full["removed"]),
              "legacy_index_prefix_identical": legacy_prefix, "frozen_and_protected_files_unchanged": frozen,
              "rollback": {"restore_from": str(DIRS["out"] / "sd_pre"), "ROLLBACK_DELETE_FILES": p["create_order"]},
              "manifest_entries_checked": len(man_vs_card), "candidate_files_checked": len(fileset),
              "other_files_untouched": all(post_full.get(k) == v for k, v in pre_full.items() if k not in ORDER),
              "file_count_pre": len(pre_full), "file_count_post": len(post_full), "candidate": p["host"], "FIRMWARE_FLASHED": "NO"}
    dump("physical_validation.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("readback", "frozen_and_protected_files_unchanged")}, ensure_ascii=False))
    raise SystemExit(0 if ok else 3)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("pre", "copy", "verify"))
    ap.add_argument("drive")
    ap.add_argument("--backup-root", default=str(DI / "backups"))
    a = ap.parse_args()
    br = Path(a.backup_root)
    DIRS.update(out=br / "juris_j2g_physical_deploy", baseline=br / "juris_j2c_physical_deploy" / "sd_manifest_post_full.json")
    {"pre": pre, "copy": copy, "verify": verify}[a.step](a.drive.rstrip("\\/"))
