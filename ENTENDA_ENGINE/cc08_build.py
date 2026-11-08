"""Build the isolated CC-08 candidate incrementally by persisted article blocks."""
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
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_550"
CONFIG = BATCH / "CC08_ENTENDA_CONFIG.json"
BASELINE = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_400" / "CC2002_CC07.entenda.jsonl"
CORPUS = BATCH / "CC2002_CC08.entenda.jsonl"
DRAFTS = BATCH / "CC08_DRAFTS.json"
MANIFEST = BATCH / "CC08_MANIFEST.json"
COVERAGE = BATCH / "CC08_COVERAGE.json"
INDEX_DIR = BATCH / "candidate_index"
CHECKPOINTS = BATCH / "checkpoints"
EXPECTED_BASELINE_SHA256 = "922ac3466e0675578dfa8a86f741d320ea1d08c3f45ea737917f1ad9235f10ab"

BLOCKS = {
    "401_430": [str(n) for n in range(401, 431)] + ["421-A"],
    "431_460": [str(n) for n in range(431, 461) if n != 456],
    "461_490": [str(n) for n in range(461, 491)],
    "491_520": [str(n) for n in range(491, 521)],
    "521_550": [str(n) for n in range(521, 551)],
}
MODULES = ("cc08_editorial_401_460", "cc08_editorial_461_520", "cc08_editorial_521_550")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def all_rows() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for name in MODULES:
        mod = importlib.import_module(name)
        overlap = set(rows) & set(mod.ROWS)
        if overlap:
            raise SystemExit("CC08_DUPLICATE_EDITORIAL_ROWS: " + ", ".join(sorted(overlap)))
        rows.update(mod.ROWS)
    expected = ({str(n) for n in range(401, 551)} - {"456"}) | {"421-A"}
    if set(rows) != expected:
        raise SystemExit("CC08_EDITORIAL_ROWS_MISMATCH missing=" + ",".join(sorted(expected - set(rows))) + " extra=" + ",".join(sorted(set(rows) - expected)))
    return rows


def render_drafts(rows: dict[str, dict], selected: list[str]) -> dict:
    return {
        "schema_version": 1,
        "norma_id": "CC2002",
        "template_version": "ENTENDA-T1",
        "prompt_version": "CC08-DELEGATED-PRODUCTION-V1",
        "review_status": "PENDING_HUMAN_REVIEW",
        "authoring": {"method": "ARTICLE_SPECIFIC_AI_DRAFT_WITH_DELEGATED_LEGAL_REVIEW", "mission": "CC-08", "generated_on": "2026-11-08", "human_approval_claimed": False},
        "explanations": [{
            "target_id": rows[n].get("target") or f"CC2002:ART.{n}",
            "role": "OVERVIEW" if rows[n].get("target") is None else "DEVICE",
            "semantic_autonomy": "AUTONOMOUS",
            "editorial_reason": "Explicação específica do dispositivo vigente, auditada quanto a requisitos, sujeitos, exceções e consequências.",
            "content": {k: rows[n][k] for k in ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis")},
            "external_layer_notes": [],
            "review_status": "PENDING_HUMAN_REVIEW",
            "editorial_version": 1,
        } for n in selected],
    }


def build(through_block: int = 5, out_dir: Path | None = None) -> dict:
    if sha(BASELINE.read_bytes()) != EXPECTED_BASELINE_SHA256:
        raise SystemExit("CC08_CC07_BASELINE_HASH_MISMATCH")
    if not 1 <= through_block <= 5:
        raise SystemExit("CC08_INVALID_BLOCK")
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
    E.write_corpus(records, corpus_path, ctx)
    write_json(root / DRAFTS.name, drafts)
    index_manifest = E.build_entenda_index(ctx, records, root / "candidate_index")
    active = [r for r in records if r["status"] == "ACTIVE"]
    new_active = [r for r in active if 401 <= int(r["target_id"].split("ART.", 1)[1].split(":", 1)[0].split("-")[0]) <= 550]
    manifest = {
        "schema_version": 1, "mission": "CC-08", "candidate_only": True, "deployed": False,
        "through_block": through_block, "completed_blocks": names, "cc07_records_preserved": len(existing),
        "active_total": len(active), "cc08_active": len(new_active),
        "cc08_review_status_counts": dict(sorted(Counter(r["review_status"] for r in new_active).items())),
        "corpus_sha256": sha(corpus_path.read_bytes()), "candidate_index": index_manifest, "production_index_modified": False,
    }
    coverage = {
        "schema_version": 1, "scope": "CC2002 arts. 401 a 550", "numbered_positions_examined": 150,
        "article_targets_examined": 151, "expected_current_explanations": 150, "produced_explanations": len(new_active),
        "remaining_explanations": 150 - len(new_active), "intercalated_current_articles": ["CC2002:ART.421-A"],
        "fully_revoked_without_active_explanation": ["CC2002:ART.456"], "completed_blocks": names,
    }
    write_json(root / MANIFEST.name, manifest)
    write_json(root / COVERAGE.name, coverage)
    if out_dir is None:
        name = names[-1]
        members = BLOCKS[name]
        block_records = [r for r in new_active if r["target_id"].split("ART.", 1)[1].split(":", 1)[0] in members]
        write_json(CHECKPOINTS / f"CC08_{name}.json", {
            "schema_version": 1, "block": name, "expected": len(members), "produced": len(block_records),
            "complete": len(block_records) == len(members), "target_ids": [r["target_id"] for r in block_records],
            "records_sha256": sha(json.dumps(block_records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")),
            "corpus_checkpoint_sha256": manifest["corpus_sha256"],
        })
    return manifest


def check() -> dict:
    with tempfile.TemporaryDirectory(prefix=".cc08-check-", dir=BATCH) as td:
        tmp = Path(td)
        result = build(5, tmp)
        pairs = [(tmp / CORPUS.name, CORPUS), (tmp / DRAFTS.name, DRAFTS), (tmp / MANIFEST.name, MANIFEST), (tmp / COVERAGE.name, COVERAGE)]
        for name in ("ENTENDA_LOOKUP.IDX", "ENTENDA_PAYLOAD.DAT", "ENTENDA_BUILD_MANIFEST.json"):
            pairs.append((tmp / "candidate_index" / name, INDEX_DIR / name))
        changed = [str(dst.relative_to(ROOT)) for src, dst in pairs if not dst.is_file() or src.read_bytes() != dst.read_bytes()]
        if changed:
            raise SystemExit("CC08_NOT_REPRODUCIBLE: " + ", ".join(changed))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--through-block", type=int, default=5)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    print(json.dumps(check() if args.check else build(args.through_block), ensure_ascii=False, indent=2))
