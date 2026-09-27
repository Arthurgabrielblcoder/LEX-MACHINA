"""Emit proof artifacts without reading labels. No filesystem mutation."""
import json
from collections import Counter
from pathlib import Path
from proof_compiler import load, CanonicalInput, run_pairs, run_exhaustive, digest, serialized, file_hash

ROOT = Path(__file__).resolve().parents[1]


def run():
    inp = CanonicalInput(load(ROOT / "01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_PILOTO.json"))
    freeze = load(ROOT / "00_CHECKPOINTS/PILOTO_REPRESENTATIONS_FREEZE.json")
    assert inp.hash == freeze["input_hash"]
    pairs = load(ROOT / "06_BENCHMARKS/PARES_PILOTO_V2.json")["pairs"]
    proof = run_pairs(inp, pairs)
    for p, r in zip(pairs, proof): r["pilot_id"] = p["pilot_id"]
    full_a, full_b = run_exhaustive(inp), run_exhaustive(inp)
    assert digest(full_a) == digest(full_b)
    result = {"scope": "36 pares dirigidos; não execução completa 69x3461", "input_hash": inp.hash,
              "counts": dict(sorted(Counter(r["state"] for r in proof).items())), "pairs": proof}
    manifest = {"logical_timestamp": "V2-P01-PROOFS-0003", "labels_loaded_for_pilot": False,
                "input_hash": inp.hash, "proofs_hash": digest(result),
                "compiler_sha256": file_hash(ROOT / "05_COMPILADOR/proof_compiler.py"),
                "pilot_cross_product": len(full_a), "deterministic_cross_product_sha256": digest(full_a),
                "run_twice_identical": True}
    return {"06_BENCHMARKS/PROVAS_PILOTO_V2.json": serialized(result),
            "00_CHECKPOINTS/PILOTO_PROOFS_FREEZE.json": serialized(manifest)}


if __name__ == "__main__": print(json.dumps({"files": run()}, ensure_ascii=False))
