"""Physical microSD deploy for MARIA2006_SOURCE_REPAIR (SD only; never flashes firmware).

Usage:
  python deploy_maria2006_source_repair_sd.py pre D:
  python deploy_maria2006_source_repair_sd.py copy D:
  python deploy_maria2006_source_repair_sd.py verify D:

Exactly 3 physical changes are allowed:
  REPLACE /15-LEI MARIA DA PENHA/Lei Maria da Penha.txt
  REPLACE /99_LEX_V1/10_TARGETS/ARTICLE_SEARCH_CATALOG.IDX
  ADD     /99_LEX_V1/10_TARGETS/MARIA2006_ARTICLE_SEARCH.IDX
Every other file must stay byte-identical to the approved full-corpus physical manifest.
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
sys.path.insert(0, str(HERE))
import article_index_corpus as C  # noqa: E402
import article_index_loader_model as L  # noqa: E402

DI = HERE.parent
STAGING = DI / "staging_maria2006_source_repair" / "SD"
BASELINE = DI / "backups" / "full_corpus_physical_deploy_20261003" / "sd_manifest_post_full.json"
OUT = DI / "backups" / "maria2006_physical_deploy_20261004"
BACKUP = OUT / "sd_pre"
IGNORED_ROOTS = {"System Volume Information"}
CHUNK = 1 << 20

TXT = "15-LEI MARIA DA PENHA/Lei Maria da Penha.txt"
CAT = "99_LEX_V1/10_TARGETS/ARTICLE_SEARCH_CATALOG.IDX"
IDX = "99_LEX_V1/10_TARGETS/MARIA2006_ARTICLE_SEARCH.IDX"
BEFORE = {
    TXT: {"bytes": 215426, "sha256": "a560439bfa7bbb6cfa77f42578bf1688183c9047004eb022af0a6444af5e775c"},
    CAT: {"bytes": 4040, "sha256": "efadd17ee2483a325f1451d71ee40e8fedbf3c032ed0127cbdbc61a9c72b2f3b"},
}
AFTER = {
    TXT: {"bytes": 46902, "sha256": "f1d43b76e1ae4013cbf812d5ac2169561e6bc6c4ecfa1e5ab7fbf2721c7d341f"},
    CAT: {"bytes": 4096, "sha256": "8d7d11db81dfa1a07f647260e17a88b197b90a3b912012880a3701e5ca31a4c9"},
    IDX: {"bytes": 796, "sha256": "61e00407355f37f516eede152d0436f8e7e2897ebf4fff81eca2ecf5e86ad2d6"},
}
ACTIONS = {TXT: "REPLACE", CAT: "REPLACE", IDX: "ADD"}
KEEP = {
    "99_LEX_V1/10_TARGETS/CF88_ARTICLE_SEARCH.IDX": "56e437a0c9cebb113c47f6a7b100ee64363c63207a647eca0456e86d6db27fae",
    "99_LEX_V1/10_TARGETS/CC2002_ARTICLE_SEARCH.IDX": "674c9971925c29aaca9685fb2d0b9515fe87e4072d644858ea27495c327d3a68",
}


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
    return {
        "added": sorted(set(after) - set(before)),
        "removed": sorted(set(before) - set(after)),
        "changed": sorted(k for k in set(before) & set(after) if before[k] != after[k]),
    }


def root_for(drive: str) -> Path:
    root = Path(drive.rstrip("\\/") + os.sep)
    required = [root / "99_LEX_V1" / d for d in ("00_SYS", "05_TEXT", "10_TARGETS", "20_REFERENCES", "30_ENTENDA")]
    if not all(p.is_dir() for p in required):
        stop("assinatura /99_LEX_V1 incompleta em " + str(root))
    if not any(p.is_dir() and p.name.startswith("1- CONSTITUI") for p in root.iterdir()):
        stop("assinatura do acervo jurídico ausente")
    if not (root / "15-LEI MARIA DA PENHA").is_dir():
        stop("pasta 15-LEI MARIA DA PENHA ausente")
    return root


def staging() -> dict:
    files = {p.relative_to(STAGING).as_posix(): file_record(p) for p in sorted(STAGING.rglob("*")) if p.is_file()}
    if files != AFTER:
        stop("staging diverge do aprovado: " + json.dumps(files, ensure_ascii=False))
    return files


def catalog_entries(path: Path) -> list:
    return C.read_catalog(path.read_bytes())


def select_maria(root: Path) -> dict:
    tdir = root / "99_LEX_V1" / "10_TARGETS"
    directory = [(n, (tdir / n).read_bytes()) for n in os.listdir(tdir) if (tdir / n).is_file()]
    rec = file_record(root / TXT)
    return L.select(directory, rec["bytes"], rec["sha256"], "CATALOG") | {"text": rec}


def pre(drive: str):
    if OUT.exists() and (OUT / "sd_manifest_pre_full.json").exists():
        stop("diretório de auditoria já existe: " + str(OUT))
    root = root_for(drive)
    staging()
    started = time.time()
    full = manifest(root, skip_system=True)
    lex = manifest(root / "99_LEX_V1")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))["entries"]
    d_base = diff(baseline, full)
    if d_base != {"added": [], "removed": [], "changed": []}:
        stop("cartão diverge do manifesto físico aprovado: " + json.dumps(d_base, ensure_ascii=False))
    for rel, rec in BEFORE.items():
        if full.get(rel) != rec:
            stop("estado 'antes' diverge: " + rel + " " + json.dumps(full.get(rel)))
    if IDX in full:
        stop("MARIA2006_ARTICLE_SEARCH.IDX já presente")
    for rel, expected in KEEP.items():
        if full.get(rel, {}).get("sha256") != expected:
            stop("KEEP diverge: " + rel)
    cat = catalog_entries(root / CAT)
    if len(cat) != 71 or any(e["norma"] == "MARIA2006" for e in cat):
        stop("catálogo atual não é 71 entradas sem MARIA2006")
    idx_count = sum(1 for k in full if k.startswith("99_LEX_V1/10_TARGETS/") and k.endswith("_ARTICLE_SEARCH.IDX"))
    if idx_count != 71:
        stop("número de *_ARTICLE_SEARCH.IDX físico != 71: " + str(idx_count))
    head = (root / TXT).read_bytes()[:4096]
    corrupted_signs = {"bom_mojibake": b"\xc3\xbf\xc3\xbe" in head, "spaced_html": b"<h t m l >" in (root / TXT).read_bytes()}
    if not all(corrupted_signs.values()):
        stop("TXT atual não mostra a assinatura do corrompido conhecido: " + repr(corrupted_signs))

    dump("sd_manifest_pre_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                       "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                       "file_count": len(full), "entries": full})
    dump("sd_manifest_pre_99_lex_v1.json", {"drive": drive, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                            "file_count": len(lex), "entries": lex})
    rows = {}
    for rel in BEFORE:
        target = BACKUP / Path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, target)
        got = file_record(target)
        if got != full[rel]:
            stop("backup não confere: " + rel)
        rows[rel] = {"backup_path": str(target), **got}
    dump("sd_pre_backup_manifest.json", {"source": str(root), "backup": str(BACKUP), "file_count": len(rows), "entries": rows})
    loader = select_maria(root)
    result = {"result": "PRE_OK", "drive": drive, "full_files": len(full), "lex_files": len(lex),
              "baseline_diff": d_base, "before": {k: full[k] for k in BEFORE}, "maria_index_absent": True,
              "catalog_entries": len(cat), "article_indexes": idx_count, "corrupted_signature": corrupted_signs,
              "loader_before": {k: loader[k] for k in ("state", "index")}, "backup": rows,
              "elapsed_s": round(time.time() - started, 1)}
    dump("physical_pre.json", result)
    print(json.dumps(result, ensure_ascii=False))


def write_one(root: Path, rel: str):
    source = STAGING / rel
    target = root / rel
    temporary = target.with_name(target.name + ".LEX_NEW")
    if temporary.exists():
        stop("temporário já existe: " + rel)
    if ACTIONS[rel] == "ADD" and target.exists():
        stop("destino ADD já existe: " + rel)
    if ACTIONS[rel] == "REPLACE" and file_record(target) != BEFORE[rel]:
        stop("destino REPLACE mudou: " + rel)
    with source.open("rb") as fi, temporary.open("xb") as fo:
        for block in iter(lambda: fi.read(CHUNK), b""):
            fo.write(block)
        fo.flush()
        os.fsync(fo.fileno())
    if file_record(temporary) != AFTER[rel]:
        stop("readback temporário diverge: " + rel)
    os.replace(temporary, target)
    got = file_record(target)
    if got != AFTER[rel]:
        stop("readback final diverge: " + rel)
    print(ACTIONS[rel], rel, got["bytes"], got["sha256"])


def copy(drive: str):
    root = root_for(drive)
    staging()
    pre_full = load("sd_manifest_pre_full.json")["entries"]
    if manifest(root, skip_system=True) != pre_full:
        stop("cartão mudou desde o manifesto pré")
    # Index first, then text, then catalog: no intermediate state points the catalog at a missing index.
    for rel in (IDX, TXT, CAT):
        write_one(root, rel)
    print("COPY_OK", len(ACTIONS))


def verify(drive: str):
    root = root_for(drive)
    staging()
    pre_full = load("sd_manifest_pre_full.json")["entries"]
    pre_lex = load("sd_manifest_pre_99_lex_v1.json")["entries"]
    post_full = manifest(root, skip_system=True)
    post_lex = manifest(root / "99_LEX_V1")
    readback = {rel: post_full.get(rel) for rel in AFTER}
    mismatch = sorted(rel for rel, rec in AFTER.items() if readback[rel] != rec)
    d_full = diff(pre_full, post_full)
    d_lex = diff(pre_lex, post_lex)
    cat = catalog_entries(root / CAT)
    idx_count = sum(1 for k in post_full if k.startswith("99_LEX_V1/10_TARGETS/") and k.endswith("_ARTICLE_SEARCH.IDX"))
    maria = [e for e in cat if e["norma"] == "MARIA2006"]
    loader = select_maria(root)
    lex_prefix = "99_LEX_V1/"
    ok = (not mismatch
          and d_full == {"added": [IDX], "removed": [], "changed": sorted([TXT, CAT])}
          and d_lex == {"added": [IDX[len(lex_prefix):]], "removed": [], "changed": [CAT[len(lex_prefix):]]}
          and len(cat) == 72 and idx_count == 72
          and len(maria) == 1 and maria[0]["source_bytes"] == AFTER[TXT]["bytes"] and maria[0]["source_sha256"] == AFTER[TXT]["sha256"]
          and loader["state"] == "LOADED" and loader["index"] == "MARIA2006_ARTICLE_SEARCH.IDX"
          and all(post_full.get(rel, {}).get("sha256") == h for rel, h in KEEP.items()))
    dump("sd_manifest_post_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                        "file_count": len(post_full), "entries": post_full})
    dump("sd_manifest_post_99_lex_v1.json", {"drive": drive, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                             "file_count": len(post_lex), "entries": post_lex})
    result = {"result": "SD_VALIDATED" if ok else "SD_NOT_VALIDATED", "readback": readback, "mismatch": mismatch,
              "diff_full": d_full, "diff_99_lex_v1": d_lex, "catalog_entries": len(cat), "article_indexes": idx_count,
              "catalog_maria": maria, "loader_after": {k: loader[k] for k in ("state", "index", "selection_ms", "load_ms")},
              "cf_idx_sha256": post_full.get(list(KEEP)[0], {}).get("sha256"),
              "cc_idx_sha256": post_full.get(list(KEEP)[1], {}).get("sha256"),
              "other_files_untouched": all(post_full.get(k) == v for k, v in pre_full.items() if k not in AFTER),
              "file_count_pre": len(pre_full), "file_count_post": len(post_full)}
    dump("physical_validation.json", result)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if ok else 3)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in {"pre", "copy", "verify"}:
        raise SystemExit("usage: deploy_maria2006_source_repair_sd.py pre|copy|verify DRIVE")
    {"pre": pre, "copy": copy, "verify": verify}[sys.argv[1]](sys.argv[2].rstrip("\\/"))
