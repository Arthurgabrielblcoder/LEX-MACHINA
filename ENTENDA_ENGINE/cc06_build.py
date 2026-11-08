"""Build the isolated CC-06 candidate while preserving the CC-05 corpus exactly."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path

import entenda_engine as E
from cc06_editorial import BLOCKS, ROWS, render_drafts

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_250"
CC05_CORPUS = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114" / "CC2002_CC02.entenda.jsonl"
BASELINE = BATCH / "CC2002_CC05_BASELINE.entenda.jsonl"
CORPUS = BATCH / "CC2002_CC06.entenda.jsonl"
DRAFTS = BATCH / "CC06_DRAFTS.json"
INDEX_DIR = BATCH / "candidate_index"
MANIFEST = BATCH / "CC06_MANIFEST.json"
COVERAGE = BATCH / "CC06_COVERAGE.json"
CHECKPOINTS = BATCH / "checkpoints"
EXPECTED_CC05_SHA256 = "c6a37520b7ed357645f722bde451204832657185ffa85e89cdbff69e2b56b8d2"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def ensure_baseline() -> None:
    raw = CC05_CORPUS.read_bytes()
    if sha(raw) != EXPECTED_CC05_SHA256:
        raise SystemExit("CC06_CC05_BASELINE_HASH_MISMATCH")
    if BASELINE.is_file() and BASELINE.read_bytes() != raw:
        raise SystemExit("CC06_SNAPSHOT_MISMATCH")
    if not BASELINE.is_file():
        BASELINE.write_bytes(raw)


def build(out_dir: Path | None = None) -> dict:
    ensure_baseline()
    ctx = E.NormContext("CC2002")
    drafts = render_drafts()
    existing = E.load_corpus(BASELINE)
    records = E.stamp(drafts, ctx, existing=existing)
    E.validate_corpus(records, ctx)

    root = BATCH if out_dir is None else out_dir
    corpus_path = root / CORPUS.name
    drafts_path = root / DRAFTS.name
    index_path = root / "candidate_index"
    write_json(drafts_path, drafts)
    E.write_corpus(records, corpus_path, ctx)
    index_manifest = E.build_entenda_index(ctx, records, index_path)

    active = [r for r in records if r["status"] == "ACTIVE"]
    new_active = [r for r in active if r["target_id"].split("ART.", 1)[1].split(":", 1)[0] in ROWS]
    completed_blocks = [name for name, members in BLOCKS.items() if set(members) <= set(ROWS)]
    manifest = {
        "schema_version": 1,
        "mission": "CC-06",
        "candidate_only": True,
        "deployed": False,
        "cc05_records_preserved": len(existing),
        "active_total": len(active),
        "cc06_active": len(new_active),
        "cc06_review_status_counts": dict(sorted(Counter(r["review_status"] for r in new_active).items())),
        "completed_blocks": completed_blocks,
        "corpus_sha256": sha(corpus_path.read_bytes()),
        "candidate_index": index_manifest,
        "production_index_modified": False,
    }
    coverage = {
        "schema_version": 1,
        "scope": "CC2002 arts. 115 a 250",
        "expected_current_explanations": 134,
        "produced_explanations": len(new_active),
        "remaining_explanations": 134 - len(new_active),
        "inserted_current_articles": ["CC2002:ART.206-A"],
        "fully_revoked_without_active_explanation": ["CC2002:ART.194", "CC2002:ART.229", "CC2002:ART.230"],
        "special_anchor": {"CC2002:ART.227:PAR.UNICO": "caput revogado; parágrafo único vigente"},
        "completed_blocks": completed_blocks,
    }
    write_json(root / MANIFEST.name, manifest)
    write_json(root / COVERAGE.name, coverage)

    if out_dir is None:
        for name, members in BLOCKS.items():
            present = [a for a in members if a in ROWS]
            if not present:
                continue
            block_records = [r for r in new_active if r["target_id"].split("ART.", 1)[1].split(":", 1)[0] in present]
            write_json(CHECKPOINTS / f"CC06_{name}.json", {
                "schema_version": 1,
                "block": name,
                "expected": len(members),
                "produced": len(block_records),
                "complete": set(members) <= set(ROWS),
                "target_ids": [r["target_id"] for r in block_records],
                "records_sha256": hashlib.sha256(json.dumps(block_records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
            })
    return manifest


def check() -> dict:
    with tempfile.TemporaryDirectory(prefix=".cc06-check-", dir=BATCH) as td:
        tmp = Path(td)
        result = build(tmp)
        pairs = [
            (tmp / CORPUS.name, CORPUS),
            (tmp / DRAFTS.name, DRAFTS),
            (tmp / MANIFEST.name, MANIFEST),
            (tmp / COVERAGE.name, COVERAGE),
            (tmp / "candidate_index" / "ENTENDA_LOOKUP.IDX", INDEX_DIR / "ENTENDA_LOOKUP.IDX"),
            (tmp / "candidate_index" / "ENTENDA_PAYLOAD.DAT", INDEX_DIR / "ENTENDA_PAYLOAD.DAT"),
            (tmp / "candidate_index" / "ENTENDA_BUILD_MANIFEST.json", INDEX_DIR / "ENTENDA_BUILD_MANIFEST.json"),
        ]
        changed = [str(dst.relative_to(ROOT)) for src, dst in pairs if not dst.is_file() or src.read_bytes() != dst.read_bytes()]
        if changed:
            raise SystemExit("CC06_NOT_REPRODUCIBLE: " + ", ".join(changed))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = check() if args.check else build()
    print(json.dumps(result, ensure_ascii=False, indent=2))
