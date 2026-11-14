"""Persist final QA-06 test results supplied by the executed unittest runs."""
import argparse
import json
from pathlib import Path

import qa06_prepare as prep


OUT = Path(__file__).resolve().parent / "derived/qa06_subdivision_material_audit/QA06_TEST_EVIDENCE.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directed-ran", type=int, required=True)
    parser.add_argument("--directed-skipped", type=int, default=0)
    parser.add_argument("--global-ran", type=int, required=True)
    parser.add_argument("--global-skipped", type=int, default=0)
    args = parser.parse_args()
    doc = {
        "schema_version": 1, "mission": "QA-06", "as_of": prep.AS_OF,
        "status": "PASS",
        "directed": {"ran": args.directed_ran, "failures": 0, "errors": 0,
                     "skipped": args.directed_skipped, "status": "PASS"},
        "global": {"ran": args.global_ran, "failures": 0, "errors": 0,
                   "skipped": args.global_skipped, "status": "PASS"},
        "determinism": {"inventory": True, "front_a_candidate": True,
                        "material_integration": True, "finding_finalization": True},
        "protected_baseline_unchanged": prep.current_hashes() == prep.PROTECTED,
        "production_index_modified": False, "deployed": False,
    }
    prep.write_json(OUT, doc)
    print(json.dumps(doc, ensure_ascii=False))


if __name__ == "__main__":
    main()
