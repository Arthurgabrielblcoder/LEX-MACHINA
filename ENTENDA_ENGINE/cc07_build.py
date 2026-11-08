"""Build the isolated CC-07 candidate incrementally by persisted article blocks."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import tempfile
from collections import Counter
from pathlib import Path

import entenda_engine as E

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_400"
CONFIG = BATCH / "CC07_ENTENDA_CONFIG.json"
BASELINE = BATCH / "CC2002_CC07_CHECKPOINT01.entenda.jsonl"
CORPUS = BATCH / "CC2002_CC07.entenda.jsonl"
DRAFTS = BATCH / "CC07_DRAFTS.json"
MANIFEST = BATCH / "CC07_MANIFEST.json"
COVERAGE = BATCH / "CC07_COVERAGE.json"
INDEX_DIR = BATCH / "candidate_index"
CHECKPOINTS = BATCH / "checkpoints"

BLOCKS = {
    "251_280": [str(n) for n in range(251, 281)],
    "281_310": [str(n) for n in range(281, 311)],
    "311_340": [str(n) for n in range(311, 341)],
    "341_370": [str(n) for n in range(341, 371)],
    "371_400": [str(n) for n in range(371, 401) if n != 374],
}
MODULES = ("cc07_editorial_251_310", "cc07_editorial_311_370", "cc07_editorial_371_400")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def all_rows() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for name in MODULES:
        mod = importlib.import_module(name)
        overlap = set(rows) & set(mod.ROWS)
        if overlap:
            raise SystemExit("CC07_DUPLICATE_EDITORIAL_ROWS: " + ", ".join(sorted(overlap)))
        rows.update(mod.ROWS)
    expected = {str(n) for n in range(251, 401)} - {"374"}
    if set(rows) != expected:
        raise SystemExit("CC07_EDITORIAL_ROWS_MISMATCH missing=" + ",".join(sorted(expected - set(rows))) + " extra=" + ",".join(sorted(set(rows) - expected)))
    return rows


def render_drafts(rows: dict[str, dict], selected: list[str]) -> dict:
    explanations = []
    for article in selected:
        data = rows[article]
        target_id = data.get("target") or f"CC2002:ART.{article}"
        explanations.append({
            "target_id": target_id,
            "role": "OVERVIEW" if data.get("target") is None else "DEVICE",
            "semantic_autonomy": "AUTONOMOUS",
            "editorial_reason": "Explicação específica do dispositivo vigente, auditada quanto a requisitos, sujeitos, exceções e consequências.",
            "content": {k: data[k] for k in ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis")},
            "external_layer_notes": [],
            "review_status": "PENDING_HUMAN_REVIEW",
            "editorial_version": 1,
        })
    return {
        "schema_version": 1,
        "norma_id": "CC2002",
        "template_version": "ENTENDA-T1",
        "prompt_version": "CC07-DELEGATED-PRODUCTION-V1",
        "review_status": "PENDING_HUMAN_REVIEW",
        "authoring": {
            "method": "ARTICLE_SPECIFIC_AI_DRAFT_WITH_DELEGATED_LEGAL_REVIEW",
            "mission": "CC-07",
            "generated_on": "2026-11-08",
            "human_approval_claimed": False,
        },
        "explanations": explanations,
    }


def build(through_block: int = 5, out_dir: Path | None = None) -> dict:
    if not 1 <= through_block <= 5:
        raise SystemExit("CC07_INVALID_BLOCK")
    rows = all_rows()
    names = list(BLOCKS)[:through_block]
    selected = [article for name in names for article in BLOCKS[name]]
    ctx = E.NormContext("CC2002", config_path=CONFIG)
    existing = E.load_corpus(BASELINE)
    drafts = render_drafts(rows, selected)
    records = E.stamp(drafts, ctx, existing=existing)
    E.validate_corpus(records, ctx)

    root = BATCH if out_dir is None else out_dir
    corpus_path = root / CORPUS.name
    drafts_path = root / DRAFTS.name
    index_path = root / "candidate_index"
    E.write_corpus(records, corpus_path, ctx)
    write_json(drafts_path, drafts)
    index_manifest = E.build_entenda_index(ctx, records, index_path)

    active = [r for r in records if r["status"] == "ACTIVE"]
    new_active = [r for r in active if 251 <= int(r["target_id"].split("ART.", 1)[1].split(":", 1)[0].split("-")[0]) <= 400]
    manifest = {
        "schema_version": 1,
        "mission": "CC-07",
        "candidate_only": True,
        "deployed": False,
        "through_block": through_block,
        "completed_blocks": names,
        "cc06_records_preserved": len(existing),
        "active_total": len(active),
        "cc07_active": len(new_active),
        "cc07_review_status_counts": dict(sorted(Counter(r["review_status"] for r in new_active).items())),
        "corpus_sha256": sha(corpus_path.read_bytes()),
        "candidate_index": index_manifest,
        "production_index_modified": False,
    }
    coverage = {
        "schema_version": 1,
        "scope": "CC2002 arts. 251 a 400",
        "numbered_articles_examined": 150,
        "expected_current_explanations": 149,
        "produced_explanations": len(new_active),
        "remaining_explanations": 149 - len(new_active),
        "fully_revoked_without_active_explanation": ["CC2002:ART.374"],
        "completed_blocks": names,
    }
    write_json(root / MANIFEST.name, manifest)
    write_json(root / COVERAGE.name, coverage)
    if out_dir is None:
        # A checkpoint is immutable evidence of the corpus at the moment that
        # block was completed. Later blocks must never rewrite earlier hashes.
        name = names[-1]
        members = BLOCKS[name]
        block_records = [r for r in new_active if r["target_id"].split("ART.", 1)[1].split(":", 1)[0] in members]
        write_json(CHECKPOINTS / f"CC07_{name}.json", {
            "schema_version": 1,
            "block": name,
            "expected": len(members),
            "produced": len(block_records),
            "complete": len(block_records) == len(members),
            "target_ids": [r["target_id"] for r in block_records],
            "records_sha256": sha(json.dumps(block_records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")),
            "corpus_checkpoint_sha256": manifest["corpus_sha256"],
        })
    return manifest


def check() -> dict:
    with tempfile.TemporaryDirectory(prefix=".cc07-check-", dir=BATCH) as td:
        tmp = Path(td)
        result = build(5, tmp)
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
            raise SystemExit("CC07_NOT_REPRODUCIBLE: " + ", ".join(changed))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--through-block", type=int, default=5)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = check() if args.check else build(args.through_block)
    print(json.dumps(result, ensure_ascii=False, indent=2))
