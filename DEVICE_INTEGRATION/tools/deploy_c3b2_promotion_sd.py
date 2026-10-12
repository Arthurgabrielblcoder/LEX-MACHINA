"""Physical microSD deploy for the C3B.2 CORRELATA promotion (SD only; never flashes firmware). Same flow as deploy_full_entenda_810_sd.py.

Usage:
  python deploy_c3b2_promotion_sd.py pre D: [--backup-root DIR]
  python deploy_c3b2_promotion_sd.py copy D: [--backup-root DIR]
  python deploy_c3b2_promotion_sd.py verify D: [--backup-root DIR]

The allowed physical changes are DERIVED from the promotion host manifest (staging_sd_v1_c3b2_promotion_candidate/_host/
STAGING_FILE_MANIFEST.json): the 5 /99_LEX_V1 files that differ from the physically approved FULL_CF_ENTENDA_810 package plus the 3
99_RELATIONS_V2 indices. Before any write the whole card must be byte-identical to the last approved physical manifest
(<backup-root>/full_entenda_810_physical_deploy/sd_manifest_post_full.json). Every other file must stay byte-identical.
Backups (gitignored) go to <backup-root>/c3b2_correlata_physical_deploy/; its sd_manifest_post_full.json is the next approved baseline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
STAGING = DI / "staging_sd_v1_c3b2_promotion_candidate"
HOST_MANIFEST = STAGING / "_host" / "STAGING_FILE_MANIFEST.json"
IGNORED_ROOTS = {"System Volume Information"}
CHUNK = 1 << 20
# write order: relation indices first, then the reference pair, the availability flags, the manifest and LEXV1.VER last
ORDER = ("99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX", "99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX",
         "99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX", "99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX", "99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX",
         "99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX", "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json", "99_LEX_V1/00_SYS/LEXV1.VER")
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


def root_for(drive: str) -> Path:
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
    host = json.loads(HOST_MANIFEST.read_text(encoding="utf-8"))
    if host.get("promotion") != "C3B2_CORRELATA" or not host.get("byte_identical_rebuild") or not all(host["promotion_bytes_match_physical_test"].values()):
        stop("manifesto do candidato não é a promoção C3B2 determinística com bytes testados")
    rows, keep = {}, {}
    for f in host["files"]:
        rel = f["path"].lstrip("/")
        got = file_record(STAGING / "SD" / rel)
        if got != {"bytes": f["bytes"], "sha256": f["sha256"]}:
            stop("staging diverge do manifesto do candidato: " + rel)
        if f["same_as_physical_baseline"]:
            keep[rel] = f["sha256"]
        else:
            rows[rel] = {"after": got, "before_sha256": f["baseline_sha256"]}
    if set(rows) != set(ORDER):
        stop("conjunto de substituições inesperado: " + json.dumps(sorted(rows)))
    return {"replace": rows, "keep": keep, "host": {k: host[k] for k in ("build_id", "git_commit", "reference_engine")}}


def pre(drive: str):
    if (DIRS["out"] / "sd_manifest_pre_full.json").exists():
        stop("diretório de auditoria já existe: " + str(DIRS["out"]))
    root, ver = root_for(drive)
    if not all(x in ver for x in ("BUILD_ID|de963699728cb66e", "GIT_COMMIT|fa9719a6bd335275252473a5f154e4e11f5532f4",
                                  "REFERENCE_ENGINE|cf-reference-engine-run3")):
        stop("LEXV1.VER não é o baseline FULL_CF_ENTENDA_810")
    p = plan()
    full = manifest(root, skip_system=True)
    baseline = json.loads(DIRS["baseline"].read_text(encoding="utf-8"))["entries"]
    d_base = diff(baseline, full)
    if d_base != {"added": [], "removed": [], "changed": []}:
        stop("cartão diverge do último manifesto físico aprovado (FULL_CF_ENTENDA_810): " + json.dumps(d_base, ensure_ascii=False)[:2000])
    for rel, r in p["replace"].items():
        if full.get(rel, {}).get("sha256") != r["before_sha256"]:
            stop("arquivo a substituir não está no baseline aprovado: " + rel)
    for rel, h in p["keep"].items():
        if full.get(rel, {}).get("sha256") != h:
            stop("arquivo KEEP diverge do pacote aprovado: " + rel)
    dump("sd_manifest_pre_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                       "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "file_count": len(full), "entries": full})
    rows = {}
    for rel in ORDER:
        target = DIRS["out"] / "sd_pre" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, target)
        got = file_record(target)
        if got != full[rel]:
            stop("backup não confere: " + rel)
        rows[rel] = {"backup_path": str(target), **got}
    dump("sd_pre_backup_manifest.json", {"source": str(root), "backup": str(DIRS["out"] / "sd_pre"), "file_count": len(rows), "entries": rows})
    result = {"result": "PRE_OK", "drive": drive, "full_files": len(full), "baseline_diff": d_base, "replace": list(ORDER),
              "keep_in_package": len(p["keep"]), "candidate": p["host"], "backup": rows}
    dump("physical_pre.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "backup"}, ensure_ascii=False))


def write_one(root: Path, rel: str, r: dict):
    source, target = STAGING / "SD" / rel, root / rel
    temporary = target.with_name(target.name + ".LEX_NEW")
    if temporary.exists():
        stop("temporário já existe: " + rel)
    if sha(target) != r["before_sha256"]:
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


def copy(drive: str):
    root, _ = root_for(drive)
    p = plan()
    if manifest(root, skip_system=True) != load("sd_manifest_pre_full.json")["entries"]:
        stop("cartão mudou desde o manifesto pré")
    for rel in ORDER:
        write_one(root, rel, p["replace"][rel])
    print("COPY_OK", len(ORDER))


def verify(drive: str):
    root, _ = root_for(drive)
    p = plan()
    pre_full = load("sd_manifest_pre_full.json")["entries"]
    post_full = manifest(root, skip_system=True)
    readback = {rel: post_full.get(rel) for rel in ORDER}
    mismatch = sorted(rel for rel in ORDER if readback[rel] != p["replace"][rel]["after"])
    d_full = diff(pre_full, post_full)
    dev = json.loads((root / "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json").read_text(encoding="utf-8"))
    man_vs_card = {k: post_full.get(k, {}).get("sha256") == v["sha256"] for k, v in dev["files"].items() if k != "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json"}
    ok = (not mismatch and d_full == {"added": [], "removed": [], "changed": sorted(ORDER)} and all(man_vs_card.values())
          and all(post_full.get(rel, {}).get("sha256") == h for rel, h in p["keep"].items()))
    dump("sd_manifest_post_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "file_count": len(post_full), "entries": post_full})
    result = {"result": "SD_VALIDATED" if ok else "SD_NOT_VALIDATED", "readback": readback, "mismatch": mismatch, "diff_full": d_full,
              "manifest_vs_card": "PASS" if all(man_vs_card.values()) else "FAIL", "manifest_entries_checked": len(man_vs_card),
              "other_files_untouched": all(post_full.get(k) == v for k, v in pre_full.items() if k not in ORDER),
              "file_count_pre": len(pre_full), "file_count_post": len(post_full), "candidate": p["host"]}
    dump("physical_validation.json", result)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if ok else 3)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("pre", "copy", "verify"))
    ap.add_argument("drive")
    ap.add_argument("--backup-root", default=str(DI / "backups"))
    a = ap.parse_args()
    br = Path(a.backup_root)
    DIRS.update(out=br / "c3b2_correlata_physical_deploy", baseline=br / "full_entenda_810_physical_deploy" / "sd_manifest_post_full.json")
    {"pre": pre, "copy": copy, "verify": verify}[a.step](a.drive.rstrip("\\/"))
