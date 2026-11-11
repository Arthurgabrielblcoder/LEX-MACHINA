"""Build the isolated ten-checkpoint CC-10 candidate through Civil Code art. 1,040."""
from __future__ import annotations
import argparse, hashlib, importlib, json, tempfile
from collections import Counter
from pathlib import Path
import entenda_engine as E

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_1040"
CONFIG = BATCH / "CC10_ENTENDA_CONFIG.json"
BASELINE = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_700" / "CC2002_CC09.entenda.jsonl"
CORPUS = BATCH / "CC2002_CC10.entenda.jsonl"
DRAFTS = BATCH / "CC10_DRAFTS.json"
MANIFEST = BATCH / "CC10_MANIFEST.json"
COVERAGE = BATCH / "CC10_COVERAGE.json"
INDEX = BATCH / "candidate_index"
CHECKPOINTS = BATCH / "checkpoints"
EXPECTED = "372e427d6268e38685b78dfba18ba5e87c3c7d95ca997c4356e77128e1a03eec"

BLOCKS = {
    "701_734": [str(n) for n in range(701, 735)],
    "735_768": [str(n) for n in range(735, 757)],
    "769_802": [],
    "803_836": [str(n) for n in range(803, 837)],
    "837_870": [str(n) for n in range(837, 871)] + ["853-A"],
    "871_904": [str(n) for n in range(871, 905)],
    "905_938": [str(n) for n in range(905, 939)],
    "939_972": [str(n) for n in range(939, 973)],
    "973_1006": [str(n) for n in range(973, 1007)],
    "1007_1040": [str(n) for n in range(1007, 1041)],
}
HISTORICAL = {
    "735_768": [str(n) for n in range(757, 769)],
    "769_802": [str(n) for n in range(769, 803)],
    "803_836": ["819-A"],
    "973_1006": ["980-A"],
}
MODULES = (
    "cc10_editorial_701_756", "cc10_editorial_803_826", "cc10_editorial_827_850",
    "cc10_editorial_851_904", "cc10_editorial_905_972", "cc10_editorial_973_1040",
)

def sha(b): return hashlib.sha256(b).hexdigest()
def write(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(v, ensure_ascii=False, indent=2) + "\n").encode())

def all_rows():
    rows = {}
    for name in MODULES:
        mod = importlib.import_module(name)
        overlap = set(rows) & set(mod.ROWS)
        if overlap: raise SystemExit("CC10_EDITORIAL_DUPLICATE_ROWS: " + ", ".join(sorted(overlap)))
        rows.update(mod.ROWS)
    expected = {n for values in BLOCKS.values() for n in values}
    if set(rows) != expected:
        raise SystemExit("CC10_EDITORIAL_ROWS_MISMATCH missing=%s extra=%s" % (sorted(expected-set(rows)), sorted(set(rows)-expected)))
    return rows

def draft(rows, selected):
    return {"schema_version": 1, "norma_id": "CC2002", "template_version": "ENTENDA-T1",
        "prompt_version": "CC10-AMPLIADA-DELEGATED-PRODUCTION-V1", "review_status": "PENDING_HUMAN_REVIEW",
        "authoring": {"method": "ARTICLE_SPECIFIC_AI_DRAFT_WITH_DELEGATED_LEGAL_REVIEW", "mission": "CC-10",
            "generated_on": "2026-11-11", "human_approval_claimed": False},
        "explanations": [{"target_id": f"CC2002:ART.{n}", "role": "OVERVIEW", "semantic_autonomy": "AUTONOMOUS",
            "editorial_reason": "Explicação específica do dispositivo vigente, auditada quanto a requisitos, sujeitos, exceções e consequências.",
            "content": {k: rows[n][k] for k in ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis")},
            "external_layer_notes": [], "review_status": "PENDING_HUMAN_REVIEW", "editorial_version": 1} for n in selected]}

def build(through=10, out=None):
    if sha(BASELINE.read_bytes()) != EXPECTED: raise SystemExit("CC10_BASELINE_MISMATCH")
    names = list(BLOCKS)[:through]
    selected = [n for name in names for n in BLOCKS[name]]
    ctx = E.NormContext("CC2002", config_path=CONFIG)
    existing = E.load_corpus(BASELINE)
    drafts = draft(all_rows(), selected)
    records = E.stamp(drafts, ctx, existing=existing)
    E.validate_corpus(records, ctx)
    root = BATCH if out is None else out
    cp = root / CORPUS.name
    E.write_corpus(records, cp, ctx)
    write(root / DRAFTS.name, drafts)
    im = E.build_entenda_index(ctx, records, root / "candidate_index")
    active = [r for r in records if r["status"] == "ACTIVE"]
    new = [r for r in active if 701 <= int(r["target_id"].split("ART.", 1)[1].split(":", 1)[0].split("-")[0]) <= 1040]
    man = {"schema_version": 1, "mission": "CC-10", "candidate_only": True, "deployed": False,
        "through_block": through, "completed_blocks": names, "cc09_records_preserved": len(existing),
        "active_total": len(active), "cc10_active": len(new),
        "cc10_review_status_counts": dict(sorted(Counter(r["review_status"] for r in new).items())),
        "corpus_sha256": sha(cp.read_bytes()), "candidate_index": im, "production_index_modified": False}
    cov = {"schema_version": 1, "scope": "CC2002 arts. 701 a 1.040", "numbered_positions_examined": 340,
        "article_targets_examined": 343, "expected_current_explanations": 295, "produced_explanations": len(new),
        "remaining_explanations": 295-len(new), "revoked_historical_articles": [f"CC2002:ART.{n}" for n in range(757,803)] + ["CC2002:ART.980-A"],
        "vetoed_without_active_explanation": ["CC2002:ART.819-A"], "active_intercalated": ["CC2002:ART.853-A"],
        "completed_blocks": names}
    write(root / MANIFEST.name, man); write(root / COVERAGE.name, cov)
    if out is None:
        name = names[-1]; expected = BLOCKS[name]
        produced = [r for r in new if r["target_id"].split("ART.",1)[1].split(":",1)[0] in expected]
        hist = [f"CC2002:ART.{n}" for n in HISTORICAL.get(name, [])]
        write(CHECKPOINTS / f"CC10_{name}.json", {"schema_version": 1, "block": name,
            "kind": "HISTORICAL_RECONCILIATION" if not expected else "MIXED" if hist else "ACTIVE_PRODUCTION",
            "expected_active": len(expected), "produced": len(produced), "complete": len(produced)==len(expected),
            "target_ids": [r["target_id"] for r in produced], "historical_targets": hist,
            "corpus_checkpoint_sha256": man["corpus_sha256"]})
    return man

def check():
    with tempfile.TemporaryDirectory(prefix=".cc10-check-", dir=BATCH) as td:
        tmp = Path(td); result = build(10, tmp)
        pairs = [(tmp/CORPUS.name,CORPUS),(tmp/DRAFTS.name,DRAFTS),(tmp/MANIFEST.name,MANIFEST),(tmp/COVERAGE.name,COVERAGE)]
        pairs += [(tmp/"candidate_index"/n, INDEX/n) for n in ("ENTENDA_LOOKUP.IDX","ENTENDA_PAYLOAD.DAT","ENTENDA_BUILD_MANIFEST.json")]
        bad = [str(d.relative_to(ROOT)) for s,d in pairs if not d.is_file() or s.read_bytes()!=d.read_bytes()]
        if bad: raise SystemExit("CC10_NOT_REPRODUCIBLE: " + ", ".join(bad))
        return result

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--through-block",type=int,default=10); p.add_argument("--check",action="store_true")
    a=p.parse_args(); print(json.dumps(check() if a.check else build(a.through_block),ensure_ascii=False,indent=2))
