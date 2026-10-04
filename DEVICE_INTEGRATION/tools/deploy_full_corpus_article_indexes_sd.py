"""Physical microSD deploy for FULL_CORPUS ARTICLE_SEARCH indexes (SD only; never flashes firmware).

Usage:
  python deploy_full_corpus_article_indexes_sd.py pre D:
  python deploy_full_corpus_article_indexes_sd.py copy D:
  python deploy_full_corpus_article_indexes_sd.py verify D:

The copy phase is allowed to add exactly 69 new *_ARTICLE_SEARCH.IDX files plus
ARTICLE_SEARCH_CATALOG.IDX under /99_LEX_V1/10_TARGETS. Existing files are never
overwritten. CF88/CC2002 are mandatory byte-identical KEEP files. MARIA2006 is
mandatory absent.
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
STAGING = DI / "staging_article_indexes_full_corpus_candidate" / "SD" / "99_LEX_V1" / "10_TARGETS"
OUT = DI / "backups" / "full_corpus_physical_deploy_20261003"
BACKUP = OUT / "sd_pre" / "99_LEX_V1"
PREFIX = "99_LEX_V1/10_TARGETS/"
EXPECTED_CF = "56e437a0c9cebb113c47f6a7b100ee64363c63207a647eca0456e86d6db27fae"
EXPECTED_CC = "674c9971925c29aaca9685fb2d0b9515fe87e4072d644858ea27495c327d3a68"
KEEP = {"CF88_ARTICLE_SEARCH.IDX": EXPECTED_CF, "CC2002_ARTICLE_SEARCH.IDX": EXPECTED_CC}
IGNORED_ROOTS = {"System Volume Information"}
CHUNK = 1 << 20


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
            rel = path.relative_to(root).as_posix()
            entries[rel] = file_record(path)
    return dict(sorted(entries.items()))


def dump(name: str, value: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def load(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def candidate() -> dict:
    files = {p.name: file_record(p) for p in sorted(STAGING.iterdir()) if p.is_file()}
    if len(files) != 72 or sum(v["bytes"] for v in files.values()) != 166760:
        stop("staging não é 72 arquivos / 166760 B")
    article = [n for n in files if n.endswith("_ARTICLE_SEARCH.IDX")]
    if len(article) != 71 or "ARTICLE_SEARCH_CATALOG.IDX" not in files:
        stop("staging não é 71 ARTICLE_SEARCH.IDX + catálogo")
    if "MARIA2006_ARTICLE_SEARCH.IDX" in files:
        stop("staging contém índice proibido de MARIA2006")
    for name, expected in KEEP.items():
        if files.get(name, {}).get("sha256") != expected:
            stop("KEEP do staging diverge: " + name)
    return files


def root_for(drive: str) -> Path:
    root = Path(drive.rstrip("\\/" ) + os.sep)
    required = [root / "99_LEX_V1" / "00_SYS", root / "99_LEX_V1" / "05_TEXT",
                root / "99_LEX_V1" / "10_TARGETS", root / "99_LEX_V1" / "20_REFERENCES",
                root / "99_LEX_V1" / "30_ENTENDA"]
    if not all(p.is_dir() for p in required):
        stop("assinatura /99_LEX_V1 incompleta em " + str(root))
    if not any(p.is_dir() and p.name.startswith("1- CONSTITUI") for p in root.iterdir()):
        stop("assinatura do acervo jurídico ausente")
    return root


def diff(before: dict, after: dict) -> dict:
    return {
        "added": sorted(set(after) - set(before)),
        "removed": sorted(set(before) - set(after)),
        "changed": sorted(k for k in set(before) & set(after) if before[k] != after[k]),
    }


def pre(drive: str):
    if OUT.exists():
        stop("diretório de auditoria já existe: " + str(OUT))
    root = root_for(drive)
    stage = candidate()
    targets = root / "99_LEX_V1" / "10_TARGETS"
    current_targets = manifest(targets)
    actions = {}
    for name, rec in stage.items():
        if name not in current_targets:
            actions[name] = "ADD"
        elif current_targets[name] == rec:
            actions[name] = "KEEP"
        else:
            actions[name] = "CONFLICT"
    counts = {kind: sum(v == kind for v in actions.values()) for kind in ("KEEP", "ADD", "CONFLICT")}
    if counts != {"KEEP": 2, "ADD": 70, "CONFLICT": 0} or {n for n, a in actions.items() if a == "KEEP"} != set(KEEP):
        stop("diff materialmente diferente do plano: " + repr(counts))
    for name, expected in KEEP.items():
        if current_targets.get(name, {}).get("sha256") != expected:
            stop("hash físico aprovado diverge: " + name)

    started = time.time()
    full = manifest(root, skip_system=True)
    lex = manifest(root / "99_LEX_V1")
    dump("sd_manifest_pre_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                       "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                       "file_count": len(full), "entries": full})
    dump("sd_manifest_pre_99_lex_v1.json", {"drive": drive, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                            "file_count": len(lex), "entries": lex})
    dump("staging_deploy_manifest.json", {"file_count": len(stage), "bytes": sum(v["bytes"] for v in stage.values()),
                                           "entries": stage})
    dump("physical_diff_pre.json", {"counts": counts, "actions": dict(sorted(actions.items()))})

    backup_rows = {}
    for rel, rec in lex.items():
        source = root / "99_LEX_V1" / Path(rel)
        target = BACKUP / Path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        got = file_record(target)
        if got != rec:
            stop("backup não confere: " + rel)
        backup_rows[rel] = got
    dump("sd_pre_backup_manifest.json", {"source": str(root / "99_LEX_V1"), "backup": str(BACKUP),
                                          "file_count": len(backup_rows), "entries": backup_rows})
    print(json.dumps({"result": "PRE_OK", "drive": drive, "full_files": len(full), "lex_files": len(lex),
                      "backup_files": len(backup_rows), "diff": counts,
                      "elapsed_s": round(time.time() - started, 1)}, ensure_ascii=False))


def copy(drive: str):
    root = root_for(drive)
    stage = candidate()
    pre_lex = load("sd_manifest_pre_99_lex_v1.json")["entries"]
    if manifest(root / "99_LEX_V1") != pre_lex:
        stop("/99_LEX_V1 mudou desde o manifesto pré")
    actions = load("physical_diff_pre.json")["actions"]
    additions = [n for n, action in actions.items() if action == "ADD"]
    if len(additions) != 70:
        stop("lista de ADD não contém 70 arquivos")
    targets = root / "99_LEX_V1" / "10_TARGETS"
    for name in additions:
        source = STAGING / name
        target = targets / name
        temporary = targets / (name + ".LEX_NEW")
        if target.exists() or temporary.exists():
            stop("destino novo/temporário já existe: " + name)
        with source.open("rb") as fi, temporary.open("xb") as fo:
            for block in iter(lambda: fi.read(CHUNK), b""):
                fo.write(block)
            fo.flush()
            os.fsync(fo.fileno())
        if file_record(temporary) != stage[name]:
            stop("readback temporário diverge: " + name)
        os.replace(temporary, target)
        if file_record(target) != stage[name]:
            stop("readback final diverge: " + name)
        print("ADD", name)
    print("COPY_OK", len(additions))


def verify(drive: str):
    root = root_for(drive)
    stage = candidate()
    pre_full = load("sd_manifest_pre_full.json")["entries"]
    pre_lex = load("sd_manifest_pre_99_lex_v1.json")["entries"]
    post_full = manifest(root, skip_system=True)
    post_lex = manifest(root / "99_LEX_V1")
    deploy = {name: post_lex.get("10_TARGETS/" + name) for name in stage}
    mismatch = sorted(name for name, rec in stage.items() if deploy.get(name) != rec)
    d_full = diff(pre_full, post_full)
    d_lex = diff(pre_lex, post_lex)
    expected_add = sorted(PREFIX + name for name in stage if name not in KEEP)
    ok = (not mismatch and d_full == {"added": expected_add, "removed": [], "changed": []}
          and d_lex == {"added": sorted("10_TARGETS/" + name for name in stage if name not in KEEP),
                        "removed": [], "changed": []}
          and "10_TARGETS/MARIA2006_ARTICLE_SEARCH.IDX" not in post_lex
          and all(post_lex["10_TARGETS/" + name]["sha256"] == expected for name, expected in KEEP.items()))
    dump("sd_manifest_post_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                        "file_count": len(post_full), "entries": post_full})
    dump("sd_manifest_post_99_lex_v1.json", {"drive": drive, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                             "file_count": len(post_lex), "entries": post_lex})
    result = {"result": "SD_VALIDATED" if ok else "SD_NOT_VALIDATED", "deploy_match": len(stage) - len(mismatch),
              "deploy_total": len(stage), "mismatch": mismatch, "diff_full": d_full, "diff_99_lex_v1": d_lex,
              "cf_sha256": post_lex.get("10_TARGETS/CF88_ARTICLE_SEARCH.IDX", {}).get("sha256"),
              "cc_sha256": post_lex.get("10_TARGETS/CC2002_ARTICLE_SEARCH.IDX", {}).get("sha256"),
              "maria_index_absent": "10_TARGETS/MARIA2006_ARTICLE_SEARCH.IDX" not in post_lex,
              "legacy_untouched": all(post_full.get(k) == v for k, v in pre_full.items() if not k.startswith("99_LEX_V1/"))}
    dump("physical_validation.json", result)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if ok else 3)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in {"pre", "copy", "verify"}:
        raise SystemExit("usage: deploy_full_corpus_article_indexes_sd.py pre|copy|verify DRIVE")
    {"pre": pre, "copy": copy, "verify": verify}[sys.argv[1]](sys.argv[2].rstrip("\\/"))
