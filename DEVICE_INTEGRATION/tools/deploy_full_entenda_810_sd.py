"""Physical microSD deploy for FULL_CF_ENTENDA_810 (SD only; never flashes firmware).

Usage:
  python deploy_full_entenda_810_sd.py pre D:
  python deploy_full_entenda_810_sd.py copy D:
  python deploy_full_entenda_810_sd.py verify D:

The allowed physical changes are DERIVED from the candidate host manifest (staging_sd_v1_full_entenda_810_candidate/_host/
STAGING_FILE_MANIFEST.json): every /99_LEX_V1 file whose sha256 differs from the physically approved BATCH04_RUN3 package (expected: 5
REPLACE). Before any write the whole card must be byte-identical to the last approved physical manifest (MARIA2006 deploy, 2026-10-04),
and each file to replace must still hold its approved BATCH04_RUN3 bytes. Every other file (Lei Seca, legacy layers, the 72 article
indexes, RUN3, runtime, TEXT_MAP) must stay byte-identical. After `copy`, run `Write-VolumeCache <letter>` before `verify`.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
STAGING = DI / "staging_sd_v1_full_entenda_810_candidate"
HOST_MANIFEST = STAGING / "_host" / "STAGING_FILE_MANIFEST.json"
BASELINE = DI / "backups" / "maria2006_physical_deploy_20261004" / "sd_manifest_post_full.json"
OUT = DI / "backups" / "full_entenda_810_physical_deploy"
BACKUP = OUT / "sd_pre"
IGNORED_ROOTS = {"System Volume Information"}
CHUNK = 1 << 20
EXPECTED_REPLACE = 5
# write order: payload and lookup first, LEXV1.VER last (the device never sees a half-written card, but the order keeps any
# interrupted copy fail-closed: the old VER is read until the very last step)
ORDER = ("30_ENTENDA/ENTENDA_PAYLOAD.DAT", "30_ENTENDA/ENTENDA_LOOKUP.IDX", "10_TARGETS/CF88_TARGETS.IDX",
         "00_SYS/LEX_DEVICE_MANIFEST.json", "00_SYS/LEXV1.VER")


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
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def load(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def diff(before: dict, after: dict) -> dict:
    return {"added": sorted(set(after) - set(before)), "removed": sorted(set(before) - set(after)),
            "changed": sorted(k for k in set(before) & set(after) if before[k] != after[k])}


def root_for(drive: str) -> Path:
    root = Path(drive.rstrip("\\/") + os.sep)
    required = [root / "99_LEX_V1" / d for d in ("00_SYS", "05_TEXT", "10_TARGETS", "20_REFERENCES", "30_ENTENDA")]
    if not all(p.is_dir() for p in required):
        stop("assinatura /99_LEX_V1 incompleta em " + str(root))
    if not any(p.is_dir() and p.name.startswith("1- CONSTITUI") for p in root.iterdir()):
        stop("assinatura do acervo jurídico ausente")
    return root


def plan() -> dict:
    """rel (under 99_LEX_V1) -> {before, after}; derived from the candidate host manifest and re-checked against the staging bytes."""
    host = json.loads(HOST_MANIFEST.read_text(encoding="utf-8"))
    if host.get("profile") != "FULL_CF_ENTENDA_810" or not host.get("byte_identical_rebuild"):
        stop("manifesto do candidato não é FULL_CF_ENTENDA_810 determinístico")
    rows = {}
    for f in host["files"]:
        rel = f["path"][len("/99_LEX_V1/"):]
        got = file_record(STAGING / "SD" / "99_LEX_V1" / rel)
        if got != {"bytes": f["bytes"], "sha256": f["sha256"]}:
            stop("staging diverge do manifesto do candidato: " + rel)
        if not f["same_as_physical_baseline"]:
            rows[rel] = {"after": got, "before_sha256": f["baseline_sha256"]}
    if len(rows) != EXPECTED_REPLACE or set(rows) != set(ORDER):
        stop("conjunto de substituições inesperado: " + json.dumps(sorted(rows)))
    return {"replace": rows, "keep": {f["path"][len("/99_LEX_V1/"):]: f["sha256"] for f in host["files"] if f["same_as_physical_baseline"]},
            "host": {k: host[k] for k in ("build_id", "git_commit", "entenda_explanations", "entenda_lookup_rows", "entenda_scope")}}


def pre(drive: str):
    if (OUT / "sd_manifest_pre_full.json").exists():
        stop("diretório de auditoria já existe: " + str(OUT))
    root = root_for(drive)
    p = plan()
    started = time.time()
    full = manifest(root, skip_system=True)
    lex = manifest(root / "99_LEX_V1")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))["entries"]
    d_base = diff(baseline, full)
    if d_base != {"added": [], "removed": [], "changed": []}:
        stop("cartão diverge do último manifesto físico aprovado (MARIA2006): " + json.dumps(d_base, ensure_ascii=False)[:2000])
    for rel, r in p["replace"].items():
        if full.get("99_LEX_V1/" + rel, {}).get("sha256") != r["before_sha256"]:
            stop("arquivo a substituir não está no estado aprovado BATCH04_RUN3: " + rel)
    for rel, h in p["keep"].items():
        if full.get("99_LEX_V1/" + rel, {}).get("sha256") != h:
            stop("arquivo KEEP diverge do pacote aprovado: " + rel)
    dump("sd_manifest_pre_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                       "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "file_count": len(full), "entries": full})
    dump("sd_manifest_pre_99_lex_v1.json", {"drive": drive, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                            "file_count": len(lex), "entries": lex})
    rows = {}
    for rel in ORDER:
        target = BACKUP / "99_LEX_V1" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / "99_LEX_V1" / rel, target)
        got = file_record(target)
        if got != full["99_LEX_V1/" + rel]:
            stop("backup não confere: " + rel)
        rows[rel] = {"backup_path": str(target), **got}
    dump("sd_pre_backup_manifest.json", {"source": str(root), "backup": str(BACKUP), "file_count": len(rows), "entries": rows})
    result = {"result": "PRE_OK", "drive": drive, "full_files": len(full), "lex_files": len(lex), "baseline_diff": d_base,
              "replace": sorted(p["replace"]), "keep_in_package": len(p["keep"]), "candidate": p["host"], "backup": rows,
              "elapsed_s": round(time.time() - started, 1)}
    dump("physical_pre.json", result)
    print(json.dumps(result, ensure_ascii=False))


def write_one(root: Path, rel: str, r: dict):
    source = STAGING / "SD" / "99_LEX_V1" / rel
    target = root / "99_LEX_V1" / rel
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
    root = root_for(drive)
    p = plan()
    if manifest(root, skip_system=True) != load("sd_manifest_pre_full.json")["entries"]:
        stop("cartão mudou desde o manifesto pré")
    for rel in ORDER:
        write_one(root, rel, p["replace"][rel])
    print("COPY_OK", len(ORDER))


def verify(drive: str):
    root = root_for(drive)
    p = plan()
    pre_full = load("sd_manifest_pre_full.json")["entries"]
    post_full = manifest(root, skip_system=True)
    post_lex = manifest(root / "99_LEX_V1")
    readback = {rel: post_full.get("99_LEX_V1/" + rel) for rel in ORDER}
    mismatch = sorted(rel for rel in ORDER if readback[rel] != p["replace"][rel]["after"])
    d_full = diff(pre_full, post_full)
    ok = (not mismatch and d_full == {"added": [], "removed": [], "changed": sorted("99_LEX_V1/" + r for r in ORDER)}
          and all(post_full.get("99_LEX_V1/" + rel, {}).get("sha256") == h for rel, h in p["keep"].items()))
    dump("sd_manifest_post_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "file_count": len(post_full), "entries": post_full})
    dump("sd_manifest_post_99_lex_v1.json", {"drive": drive, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                             "file_count": len(post_lex), "entries": post_lex})
    result = {"result": "SD_VALIDATED" if ok else "SD_NOT_VALIDATED", "readback": readback, "mismatch": mismatch, "diff_full": d_full,
              "other_files_untouched": all(post_full.get(k) == v for k, v in pre_full.items() if k[len("99_LEX_V1/"):] not in ORDER),
              "file_count_pre": len(pre_full), "file_count_post": len(post_full), "candidate": p["host"]}
    dump("physical_validation.json", result)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if ok else 3)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in {"pre", "copy", "verify"}:
        raise SystemExit("usage: deploy_full_entenda_810_sd.py pre|copy|verify DRIVE")
    {"pre": pre, "copy": copy, "verify": verify}[sys.argv[1]](sys.argv[2].rstrip("\\/"))
