"""Build the CC-02 ENTENDA candidate for Civil Code arts. 1-114.

The bootstrap option is intentionally one-shot: it pins an excerpt of the exact
operational source audited in CC-01. Normal and CI builds use only the committed
excerpt and never depend on the backup path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ENTENDA_ENGINE"))
sys.path.insert(0, str(ROOT / "LEGAL_TARGET_ID"))

import entenda_engine as E  # noqa: E402
import build_target_index as BT  # noqa: E402
from cc02_editorial import CC05_HUMAN_APPROVED_TARGETS, render_drafts  # noqa: E402

BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
SOURCE = BATCH / "SOURCE_CC2002_ARTS_001_114.txt"
SOURCE_META = BATCH / "SOURCE_PROVENANCE.json"
TARGET_INDEX = BATCH / "CC2002_TARGET_INDEX.json"
DRAFTS = BATCH / "CC02_DRAFTS.json"
CORPUS = BATCH / "CC2002_CC02.entenda.jsonl"
BASELINE_CORPUS = BATCH / "CC2002_CC02_BASELINE.entenda.jsonl"
CC03_BASELINE_CORPUS = BATCH / "CC2002_CC03_BASELINE.entenda.jsonl"
CC03B_BASELINE_CORPUS = BATCH / "CC2002_CC03B_BASELINE.entenda.jsonl"
CC04_BASELINE_CORPUS = BATCH / "CC2002_CC04_BASELINE.entenda.jsonl"
INDEX_DIR = BATCH / "index"
EXPECTED_FULL_SHA256 = "ad5ba178613b6181e2d8a61919eda0c6223c68feb6e47bef4ea65bc45c13e6ae"
EXPECTED_CC02_CORPUS_SHA256 = "86ef8d8f1843650e927b2fd2fd620dd92a7fe9508dac8934efbaae238beecd4d"
EXPECTED_CC03_CORPUS_SHA256 = "f4f44ab5334f9adc5aa7c88015762028b2a5d1381b2cfd0e0d9959799191407e"
EXPECTED_CC03B_CORPUS_SHA256 = "be75e9bdb93e9c28f76dd0577957d128471f159e8fe931e72276d7456dbbc1d2"
EXPECTED_CC04_CORPUS_SHA256 = "1311c107504697a13a9a4b99d13af5b8c47d9e210edc2b446f761c1407b73bcf"
EXPECTED_PRODUCTION_INDEX_SHA256 = {
    "ENTENDA_LOOKUP.IDX": "38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82",
    "ENTENDA_PAYLOAD.DAT": "6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638",
    "ENTENDA_BUILD_MANIFEST.json": "213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760",
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def bootstrap(full_source: Path) -> None:
    raw = full_source.read_bytes()
    if _sha(raw) != EXPECTED_FULL_SHA256:
        raise SystemExit("BOOTSTRAP_SOURCE_HASH_MISMATCH")
    text = raw.decode("utf-8-sig")
    start = re.search(r"(?m)^Art\. 1(?:º|o)\s", text)
    end = re.search(r"(?m)^Art\. 115\.\s", text)
    if not start or not end or end.start() <= start.start():
        raise SystemExit("BOOTSTRAP_ARTICLE_BOUNDARY_NOT_FOUND")
    excerpt = text[start.start():end.start()].encode("utf-8")
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    SOURCE.write_bytes(excerpt)
    _write_json(SOURCE_META, {
        "schema_version": 1,
        "norma_id": "CC2002",
        "scope": "Código Civil, arts. 1 a 114, incluindo artigos alfanuméricos vigentes no intervalo",
        "operational_full_source_sha256": EXPECTED_FULL_SHA256,
        "operational_full_source_bytes": len(raw),
        "excerpt_sha256": _sha(excerpt),
        "excerpt_bytes": len(excerpt),
        "bootstrap_source_repository_location": "DEVICE_INTEGRATION/backups/sd_20260929T163407Z/data/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt",
        "official_confrontation": {
            "checked_on": "2026-11-07",
            "norm_page": "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-norma-pl.html",
            "consolidated_text": "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
        }
    })


def build_target_index() -> dict:
    if not SOURCE.is_file():
        raise SystemExit("PINNED_SOURCE_MISSING: use --bootstrap-source once")
    idx = BT.build("CC2002", SOURCE)
    idx["source"]["path"] = str(SOURCE.relative_to(ROOT)).replace("\\", "/")
    if idx["target_id_duplicates"]:
        raise SystemExit("TARGET_ID_DUPLICATES")
    _write_json(TARGET_INDEX, idx)
    return idx


def build(out_dir: Path | None = None) -> dict:
    idx = build_target_index()
    rendered_drafts = render_drafts()
    if out_dir is None:
        _write_json(DRAFTS, rendered_drafts)
    ctx = E.NormContext("CC2002")
    drafts = rendered_drafts
    prior_corpus = CC04_BASELINE_CORPUS if CC04_BASELINE_CORPUS.is_file() else (CC03B_BASELINE_CORPUS if CC03B_BASELINE_CORPUS.is_file() else (CC03_BASELINE_CORPUS if CC03_BASELINE_CORPUS.is_file() else BASELINE_CORPUS))
    existing = E.load_corpus(prior_corpus) if prior_corpus.is_file() else []
    existing_by_id = {r["explanation_id"]: r for r in existing}
    existing_ids = {r["explanation_id"] for r in existing}
    records = E.stamp(drafts, ctx, existing=existing)
    records = [
        dict(existing_by_id[rec["explanation_id"]])
        if rec["explanation_id"] in existing_by_id
        and rec["status"] == "ACTIVE"
        and existing_by_id[rec["explanation_id"]]["status"] == "ACTIVE"
        else rec
        for rec in records
    ]
    for rec in records:
        if CC04_BASELINE_CORPUS.is_file() and rec["status"] == "ACTIVE" and rec["explanation_id"] not in existing_ids:
            rec["prompt_version"] = "CC05-CONSOLIDATION-V1"
            article = rec["target_id"].split("ART.", 1)[1].split(":", 1)[0]
            if article in CC05_HUMAN_APPROVED_TARGETS:
                rec["authoring"] = {
                    "method": "OWNER_APPROVED_EXTERNAL_TEXT_TRANSCRIPTION",
                    "mission": "CC-05",
                    "generated_on": "2026-11-07",
                    "human_approval_claimed": True,
                    "formal_status_promoted": False,
                }
                rec["external_human_approval"] = {
                    "origin": "Transcrição integral fornecida pelo proprietário no prompt da missão CC-05",
                    "approval_date": "2026-11-07",
                    "electronic_signature_verified": False,
                    "exact_text_integrity_verified": True,
                    "formal_status": "PENDING_HUMAN_REVIEW",
                }
            else:
                rec["authoring"] = {
                    "method": "TARGETED_LEGAL_RESOLUTION_WITH_OFFICIAL_SOURCES",
                    "mission": "CC-05",
                    "generated_on": "2026-11-07",
                    "human_approval_claimed": False,
                }
        elif not CC04_BASELINE_CORPUS.is_file() and CC03B_BASELINE_CORPUS.is_file() and rec["status"] == "ACTIVE" and rec["explanation_id"] not in existing_ids:
            rec["prompt_version"] = "CC04-DELEGATED-LEGAL-REVIEW-V1"
            rec["authoring"] = {
                "method": "DELEGATED_AI_LEGAL_REVIEW_WITH_OFFICIAL_SOURCE",
                "mission": "CC-04",
                "generated_on": "2026-11-07",
                "human_approval_claimed": False,
            }
        elif not CC04_BASELINE_CORPUS.is_file() and CC03_BASELINE_CORPUS.is_file() and rec["status"] == "ACTIVE":
            rec["prompt_version"] = "CC03B-PEDAGOGICAL-REFINEMENT-V1"
            rec["authoring"] = {
                "method": "ARTICLE_SPECIFIC_PEDAGOGICAL_REWRITE_AFTER_LEGAL_AUDIT",
                "mission": "CC-03B",
                "generated_on": "2026-11-07",
                "human_approval_claimed": False,
            }
        elif not CC04_BASELINE_CORPUS.is_file() and rec["editorial_version"] == 2:
            rec["prompt_version"] = "CC03-LEGAL-AUDIT-V1"
            rec["authoring"] = {
                "method": "INDEPENDENT_AUTOMATED_LEGAL_AUDIT_WITH_OFFICIAL_SOURCE",
                "mission": "CC-03",
                "generated_on": "2026-11-07",
                "human_approval_claimed": False,
            }
    E.validate_corpus(records, ctx)
    corpus_path = CORPUS if out_dir is None else out_dir / CORPUS.name
    # CC-04 is an editorial-review candidate only. Its index may be built in a
    # disposable directory for compatibility validation, but the production
    # index committed by the preceding mission must not be modified.
    preserve_production_index = out_dir is None and CC03B_BASELINE_CORPUS.is_file()
    transient_index = None
    if preserve_production_index:
        transient_index = tempfile.TemporaryDirectory(prefix=".cc04-index-check-", dir=BATCH)
        index_path = Path(transient_index.name) / "index"
    else:
        index_path = INDEX_DIR if out_dir is None else out_dir / "index"
    E.write_corpus(records, corpus_path, ctx)
    manifest = E.build_entenda_index(ctx, records, index_path)
    active = [r for r in records if r["status"] == "ACTIVE"]
    summary = {
        "target_count": idx["total_targets"],
        "explanation_count": len(active),
        "review_status_counts": {"PENDING_HUMAN_REVIEW": sum(r["review_status"] == "PENDING_HUMAN_REVIEW" for r in active)},
        "source_sha256": _sha(SOURCE.read_bytes()),
        "corpus_sha256": _sha(corpus_path.read_bytes()),
        "lookup_sha256": _sha((index_path / "ENTENDA_LOOKUP.IDX").read_bytes()),
        "payload_sha256": _sha((index_path / "ENTENDA_PAYLOAD.DAT").read_bytes()),
        "build_manifest": manifest,
        "production_index_modified": False if CC03B_BASELINE_CORPUS.is_file() else None,
    }
    if transient_index is not None:
        transient_index.cleanup()
    if out_dir is None:
        audit_mode = any(r["editorial_version"] > 1 for r in active)
        prefix = "CC05" if CC04_BASELINE_CORPUS.is_file() else ("CC04" if CC03B_BASELINE_CORPUS.is_file() else ("CC03B" if CC03_BASELINE_CORPUS.is_file() else ("CC03" if audit_mode else "CC02")))
        _write_json(BATCH / f"{prefix}_MANIFEST.json", summary)
        checkpoint_dir = BATCH / ("checkpoints_cc05" if prefix == "CC05" else ("checkpoints_cc04" if prefix == "CC04" else ("checkpoints_cc03b" if prefix == "CC03B" else ("checkpoints_cc03" if audit_mode else "checkpoints"))))
        for start, end in ((1, 25), (26, 50), (51, 75), (76, 100), (101, 114)):
            block = [r for r in active if start <= int(re.search(r"ART\.(\d+)", r["target_id"]).group(1)) <= end]
            encoded = json.dumps(block, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            _write_json(checkpoint_dir / f"{prefix}_{start:03d}_{end:03d}.json", {
                "range": [start, end],
                "explanation_count": len(block),
                "review_status": "PENDING_HUMAN_REVIEW",
                "target_ids": [r["target_id"] for r in block],
                "records_sha256": _sha(encoded),
            })
        _write_json(BATCH / f"{prefix}_COVERAGE.json", {
            "base_numbered_articles_expected": 114,
            "base_numbered_articles_explained": 114,
            "inserted_current_articles_explained": ["CC2002:ART.48-A", "CC2002:ART.49-A"],
            "blocked_targets": [{"target_id": "CC2002:ART.69-A", "reason": "VETADO na fonte consolidada; explicação ativa proibida"}],
            "active_explanations": len(active),
            "article_targets_in_source": sum(t["kind"] == "ARTIGO" for t in idx["targets"]),
            "subdivision_targets_covered_by_article_snapshots": sum(t["kind"] not in ("NORMA", "ARTIGO") for t in idx["targets"] if t["target_id"] != "CC2002:ART.69-A:CAPUT"),
            "all_active_review_status": "PENDING_HUMAN_REVIEW",
        })
    return summary


def check() -> dict:
    if CC03B_BASELINE_CORPUS.is_file():
        changed_index = [
            name for name, expected in EXPECTED_PRODUCTION_INDEX_SHA256.items()
            if not (INDEX_DIR / name).is_file() or _sha((INDEX_DIR / name).read_bytes()) != expected
        ]
        if changed_index:
            raise SystemExit("CC04_PRODUCTION_INDEX_MODIFIED: " + ", ".join(changed_index))
    with tempfile.TemporaryDirectory(prefix=".cc02-check-", dir=BATCH) as td:
        tmp = Path(td)
        summary = build(tmp)
        pairs = [(tmp / CORPUS.name, CORPUS)]
        if not CC03B_BASELINE_CORPUS.is_file():
            pairs.extend([
                (tmp / "index" / "ENTENDA_LOOKUP.IDX", INDEX_DIR / "ENTENDA_LOOKUP.IDX"),
                (tmp / "index" / "ENTENDA_PAYLOAD.DAT", INDEX_DIR / "ENTENDA_PAYLOAD.DAT"),
                (tmp / "index" / "ENTENDA_BUILD_MANIFEST.json", INDEX_DIR / "ENTENDA_BUILD_MANIFEST.json"),
            ])
        changed = [str(dst.relative_to(ROOT)) for src, dst in pairs if not dst.is_file() or src.read_bytes() != dst.read_bytes()]
        if changed:
            raise SystemExit("NON_REPRODUCIBLE_OR_UNBUILT: " + ", ".join(changed))
        return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bootstrap-source", type=Path)
    ap.add_argument("--bootstrap-only", action="store_true")
    ap.add_argument("--snapshot-cc02-baseline", action="store_true")
    ap.add_argument("--snapshot-cc03-baseline", action="store_true")
    ap.add_argument("--snapshot-cc03b-baseline", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.bootstrap_source:
        bootstrap(args.bootstrap_source)
    if args.snapshot_cc02_baseline:
        raw = CORPUS.read_bytes()
        if _sha(raw) != EXPECTED_CC02_CORPUS_SHA256:
            raise SystemExit("CC02_BASELINE_CORPUS_HASH_MISMATCH")
        BASELINE_CORPUS.write_bytes(raw)
        print(json.dumps({"baseline_corpus": str(BASELINE_CORPUS.relative_to(ROOT)), "sha256": _sha(raw)}, indent=2))
        return
    if args.snapshot_cc03_baseline:
        raw = CORPUS.read_bytes()
        if _sha(raw) != EXPECTED_CC03_CORPUS_SHA256:
            raise SystemExit("CC03_BASELINE_CORPUS_HASH_MISMATCH")
        CC03_BASELINE_CORPUS.write_bytes(raw)
        print(json.dumps({"baseline_corpus": str(CC03_BASELINE_CORPUS.relative_to(ROOT)), "sha256": _sha(raw)}, indent=2))
        return
    if args.snapshot_cc03b_baseline:
        raw = CORPUS.read_bytes()
        if _sha(raw) != EXPECTED_CC03B_CORPUS_SHA256:
            raise SystemExit("CC03B_BASELINE_CORPUS_HASH_MISMATCH")
        CC03B_BASELINE_CORPUS.write_bytes(raw)
        print(json.dumps({"baseline_corpus": str(CC03B_BASELINE_CORPUS.relative_to(ROOT)), "sha256": _sha(raw)}, indent=2))
        return
    if args.bootstrap_only:
        print(json.dumps(json.loads(SOURCE_META.read_text(encoding="utf-8")), ensure_ascii=False, indent=2))
        return
    result = check() if args.check else build()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
