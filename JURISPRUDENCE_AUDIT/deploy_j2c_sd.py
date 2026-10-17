"""JURISPRUDÊNCIA J2C: physical microSD deploy of the J2B.1 host-only candidate (ADIs of BATCH01 + Tema 558 temporal fix; SD ONLY, the
firmware is NOT touched). Same flow and safeguards as deploy_j1_4_sd.py (J1.5), plus CREATION of new files (the 3 ADI fichas):
the target must not exist, temporary .LEX_NEW, fsync, os.replace, readback, sha256; rollback of a created file = DELETE.
PRE also requires the ADI 7697 revalidation gate (check_j2b_provisional.py --as-of today) to PASS.

Usage:
  python deploy_j2c_sd.py pre D: [--backup-root DIR]
  python deploy_j2c_sd.py copy D: [--backup-root DIR]
  python deploy_j2c_sd.py verify D: [--backup-root DIR]

The allowed physical changes are DERIVED from J2B_1_CANDIDATE_HOST_ONLY/J2B_1_PACKAGE_MANIFEST.json (file_diff = replaced, file_additions =
created). Before any write the WHOLE card must be byte-identical to the last physical manifest
(<backup-root>/juris_j1_4_physical_deploy/sd_manifest_post_full.json, equal to the committed JURISPRUDENCE_AUDIT/J1_5_PHYSICAL_DEPLOY/
sd_manifest_post_full.json) and the legacy indexes of the candidate must be APPEND-ONLY over the card bytes. Every other file must stay
byte-identical. Backups (gitignored) go to <backup-root>/juris_j2c_physical_deploy/ (never overwritten).
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
ROOT = HERE.parent
DI = ROOT / "DEVICE_INTEGRATION"
PKG = HERE / "J2B_1_CANDIDATE_HOST_ONLY"
PKG_MANIFEST = PKG / "J2B_1_PACKAGE_MANIFEST.json"
COMMITTED_BASELINE = HERE / "J1_5_PHYSICAL_DEPLOY" / "sd_manifest_post_full.json"
SUPERSEDED = HERE / "J2B_CANDIDATE_HOST_ONLY"
LEGACY_IDX = ("99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX", "99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX")
IGNORED_ROOTS = {"System Volume Information"}
CHUNK = 1 << 20
# write order: new fichas first (unreferenced until the indexes change), legacy IDX before JUR_LOOKUP, then the reference pair, the
# availability flags, the manifest and LEXV1.VER last (same tail order as the C3B.2 promotion)
CREATE = ("99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_4425.TXT", "99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7047-7064.TXT",
          "99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7697.TXT")
ORDER = LEGACY_IDX + ("99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX", "99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX", "99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX",
                      "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json", "99_LEX_V1/00_SYS/LEXV1.VER")
TEMA558_FICHA = "99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_558.TXT"
CORRELATA_FILES = ("99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX", "99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX",
                   "99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX")
BASE_VER = ("BUILD_ID|cbed709a40356681", "GIT_COMMIT|7786bbc50a5f33fcf7eec01ce0de170b2d02a4f6", "REFERENCE_ENGINE|cf-reference-engine-run7-juris-j1-4")
ENTENDA_FILES = ("99_LEX_V1/30_ENTENDA/ENTENDA_LOOKUP.IDX", "99_LEX_V1/30_ENTENDA/ENTENDA_PAYLOAD.DAT")
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
    if (m.get("status"), m.get("package")) != ("HOST_ONLY_CANDIDATE", "JURIS_J2B_1") or not (
            m.get("physical_baseline_reproduced") and m.get("byte_identical_rebuild") and m.get("device_manifest_matches_package")):
        stop("manifesto do pacote não é o candidato J2B.1 determinístico")
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
    creates = {}
    for d in m["file_additions"]:
        rel = d["path"].lstrip("/")
        after = file_record(PKG / "candidate/SD" / rel)
        if after != {"bytes": d["after_bytes"], "sha256": d["after_sha256"]} or d.get("rollback") != "DELETE":
            stop("pacote diverge do manifesto (arquivo novo): " + rel)
        creates[rel] = {"after": after}
    if set(creates) != set(CREATE):
        stop("conjunto de arquivos novos inesperado: " + json.dumps(sorted(creates)))
    legacy = {}
    for rel in LEGACY_IDX:                                   # append-only: card bytes are an exact prefix; old offsets preserved
        old, new = (PKG / "rollback/SD" / rel).read_bytes(), (PKG / "candidate/SD" / rel).read_bytes()
        if not new.startswith(old) or not old.endswith(b"\n"):
            stop("índice legado não é append-only: " + rel)
        legacy[rel] = {"prefix_identical": True, "old_bytes": len(old), "appended_bytes": len(new) - len(old),
                       "old_lines": old.count(b"\n"), "appended_lines": new.count(b"\n") - old.count(b"\n")}
    keep = {f["path"].lstrip("/"): f["sha256"] for f in m["files"] if f["same_as_physical"]}
    return {"replace": rows, "create": creates, "keep": keep, "legacy": legacy,
            "host": {k: m[k] for k in ("build_id", "git_commit", "reference_engine")}}


def provisional_gate() -> list:
    import datetime as dt
    import check_j2b_provisional as G
    res = G.check(dt.date.today())
    if not all(r["result"] == "PASS" for r in res):
        stop("gate de revalidação da ADI 7697 não passou: " + json.dumps(res, ensure_ascii=False))
    return res


def baseline() -> dict:
    b = DIRS["baseline"].read_bytes()
    if b != COMMITTED_BASELINE.read_bytes():
        stop("manifesto físico pós-J1.5 de backup diverge da cópia versionada")
    return json.loads(b.decode("utf-8"))["entries"]


def pre(drive: str):
    if (DIRS["out"] / "sd_manifest_pre_full.json").exists():
        stop("diretório de auditoria já existe: " + str(DIRS["out"]))
    root, ver = root_for(drive)
    if not all(x in ver for x in BASE_VER):
        stop("LEXV1.VER não é o candidato J1.4 instalado na J1.5")
    if SUPERSEDED == PKG:
        stop("pacote J2B superado não pode ser usado")
    gate = provisional_gate()
    p = plan()
    full = manifest(root, skip_system=True)
    d_base = diff(baseline(), full)
    if d_base != {"added": [], "removed": [], "changed": []}:
        stop("cartão diverge do último manifesto físico (pós-J1.5): " + json.dumps(d_base, ensure_ascii=False)[:2000])
    for rel, r in p["replace"].items():
        if full.get(rel) != r["before"]:
            stop("arquivo a substituir não está no baseline aprovado: " + rel)
    for rel, h in p["keep"].items():
        if full.get(rel, {}).get("sha256") != h:
            stop("arquivo KEEP diverge do pacote: " + rel)
    for rel in CREATE:
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
        if got != full[rel]:
            stop("backup não confere: " + rel)
        rows[rel] = {"backup_path": str(target), **got}
    dump("sd_pre_backup_manifest.json", {"source": str(root), "backup": str(DIRS["out"] / "sd_pre"), "file_count": len(rows), "entries": rows,
                                         "rollback_delete_new_files": list(CREATE), "DELETE_NEW_ADI_FILES": "YES"})
    result = {"result": "PRE_OK", "drive": drive, "full_files": len(full), "baseline_diff": d_base, "replace": list(ORDER), "create": list(CREATE),
              "create_targets_absent": True, "legacy_append_only": p["legacy"], "provisional_gate": gate,
              "tema558_ficha_sha256": full[TEMA558_FICHA]["sha256"], "keep_in_package": len(p["keep"]), "candidate": p["host"], "backup": rows}
    dump("physical_pre.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "backup"}, ensure_ascii=False))


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
    if manifest(root, skip_system=True) != load("sd_manifest_pre_full.json")["entries"]:
        stop("cartão mudou desde o manifesto pré")
    for rel in CREATE:
        create_one(root, rel, p["create"][rel])
    for rel in ORDER:
        write_one(root, rel, p["replace"][rel])
    print("COPY_OK", "replaced", len(ORDER), "created", len(CREATE))


def verify(drive: str):
    root, _ = root_for(drive)
    p = plan()
    pre_full = load("sd_manifest_pre_full.json")["entries"]
    post_full = manifest(root, skip_system=True)
    readback = {rel: post_full.get(rel) for rel in ORDER + CREATE}
    expected = {**{rel: p["replace"][rel]["after"] for rel in ORDER}, **{rel: p["create"][rel]["after"] for rel in CREATE}}
    mismatch = sorted(rel for rel in expected if readback[rel] != expected[rel])
    d_full = diff(pre_full, post_full)
    dev = json.loads((root / "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json").read_text(encoding="utf-8"))
    man_vs_card = {k: post_full.get(k, {}).get("sha256") == v["sha256"] for k, v in dev["files"].items() if k != "99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json"}
    correlata = {rel: post_full.get(rel) == pre_full.get(rel) for rel in CORRELATA_FILES + ENTENDA_FILES}
    legacy_prefix = {rel: (root / rel).read_bytes().startswith((PKG / "rollback/SD" / rel).read_bytes()) for rel in LEGACY_IDX}
    tema558 = post_full.get(TEMA558_FICHA) == pre_full.get(TEMA558_FICHA)
    ok = (not mismatch and d_full == {"added": sorted(CREATE), "removed": [], "changed": sorted(ORDER)} and all(man_vs_card.values())
          and all(correlata.values()) and all(legacy_prefix.values()) and tema558
          and all(post_full.get(rel, {}).get("sha256") == h for rel, h in p["keep"].items()))
    dump("sd_manifest_post_full.json", {"drive": drive, "excluded_os_metadata": sorted(IGNORED_ROOTS),
                                        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "file_count": len(post_full), "entries": post_full})
    result = {"result": "SD_VALIDATED" if ok else "SD_NOT_VALIDATED", "readback": readback, "mismatch": mismatch, "diff_full": d_full,
              "files_modified": len(d_full["changed"]), "files_created": len(d_full["added"]), "files_deleted": len(d_full["removed"]),
              "legacy_index_prefix_identical": legacy_prefix, "tema558_ficha_changed": not tema558,
              "rollback": {"restore_from": str(DIRS["out"] / "sd_pre"), "delete": list(CREATE)},
              "manifest_vs_card": "PASS" if all(man_vs_card.values()) else "FAIL", "manifest_entries_checked": len(man_vs_card),
              "correlata_files_unchanged": correlata,
              "other_files_untouched": all(post_full.get(k) == v for k, v in pre_full.items() if k not in ORDER),
              "unexpected_sd_changes": len(set(d_full["changed"]) - set(ORDER)) + len(set(d_full["added"]) - set(CREATE)) + len(d_full["removed"]),
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
    DIRS.update(out=br / "juris_j2c_physical_deploy", baseline=br / "juris_j1_4_physical_deploy" / "sd_manifest_post_full.json")
    {"pre": pre, "copy": copy, "verify": verify}[a.step](a.drive.rstrip("\\/"))
