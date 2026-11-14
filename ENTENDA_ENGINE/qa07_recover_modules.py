"""Validate recovered QA-07 modules and persist CP02-CP05 without regenerating them."""
import hashlib
import json
from collections import Counter
from pathlib import Path

import qa07_prepare as prep


OUT = prep.OUT
FIVE = {"o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis"}
MODULES = {
    "A": OUT / "QA07_EDITOR_HIGH_A.json",
    "B": OUT / "QA07_EDITOR_HIGH_B.json",
    "I": OUT / "QA07_INDETERMINATE_DECISIONS.json",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def finding_ids(record, group):
    if group == "A":
        return [item["finding_id"] for item in record["findings"]]
    return list(record["finding_ids"])


def build():
    prep.build()
    scope = load(OUT / "QA07_AUTHORIZED_SCOPE.json")
    docs = {key: load(path) for key, path in MODULES.items()}
    expected_a = [r["finding_id"] for r in scope["high_groups"]["A"]]
    expected_b = [r["finding_id"] for r in scope["high_groups"]["B"]]
    actual_a = [fid for row in docs["A"]["records"] for fid in finding_ids(row, "A")]
    actual_b = [fid for row in docs["B"]["records"] for fid in finding_ids(row, "B")]
    if actual_a != expected_a or actual_b != expected_b:
        raise RuntimeError("recovered high module coverage/order mismatch")
    if (len(docs["A"]["records"]), len(docs["B"]["records"])) != (10, 15):
        raise RuntimeError("recovered high target cardinality mismatch")
    high_targets = [r["target_id"] for r in docs["A"]["records"] + docs["B"]["records"]]
    if len(high_targets) != len(set(high_targets)) or len(high_targets) != 25:
        raise RuntimeError("duplicate or missing high target")
    for row in docs["A"]["records"] + docs["B"]["records"]:
        if set(row["previous_content"]) != FIVE or set(row["proposed_content"]) != FIVE:
            raise RuntimeError(f"five-field contract mismatch: {row['target_id']}")
    expected_i = [r["finding_id"] for r in scope["indeterminate"]]
    actual_i = [r["finding_id"] for r in docs["I"]["records"]]
    if actual_i != expected_i or len(actual_i) != 10:
        raise RuntimeError("indeterminate module coverage/order mismatch")
    allowed = {"CONFIRMADO_PARA_CORRECAO", "COBERTURA_MATERIAL_SUFICIENTE",
               "RECLASSIFICADO_COM_FUNDAMENTO", "INDETERMINADO_REQUER_HUMANO"}
    for row in docs["I"]["records"]:
        if row["decision"] not in allowed:
            raise RuntimeError("invalid indeterminate decision")
        if row["decision"] == "CONFIRMADO_PARA_CORRECAO" and set(row["proposed_content"]) != FIVE:
            raise RuntimeError(f"indeterminate correction lacks five fields: {row['finding_id']}")
    hashes = {key: sha(path) for key, path in MODULES.items()}
    decisions = dict(sorted(Counter(r["decision"] for r in docs["I"]["records"]).items()))
    prep.write(OUT / "QA07_CP02.json", {
        "schema_version": 1, "mission": "QA-07", "checkpoint": "CP02", "as_of": prep.AS_OF,
        "status": "INDETERMINATE_DECISIONS_RECOVERED_PENDING_INDEPENDENT_REVIEW",
        "records": 10, "decision_counts": decisions, "module_sha256": hashes["I"],
        "corpus_modified": False, "human_approval_claimed": False,
    })
    all_high = scope["high_groups"]["A"] + scope["high_groups"]["B"]
    for cp, start, end in ((3, 0, 14), (4, 14, 28), (5, 28, 41)):
        block = all_high[start:end]
        prep.write(OUT / f"QA07_CP{cp:02d}.json", {
            "schema_version": 1, "mission": "QA-07", "checkpoint": f"CP{cp:02d}", "as_of": prep.AS_OF,
            "status": "HIGH_PROPOSALS_RECOVERED_PENDING_INDEPENDENT_REVIEW",
            "finding_start": start + 1, "finding_end": end, "finding_total": len(block),
            "finding_ids": [r["finding_id"] for r in block],
            "target_ids": list(dict.fromkeys(r["target_id"] for r in block)),
            "editor_module_sha256": hashes, "corpus_modified": False,
            "human_approval_claimed": False,
        })
    print(json.dumps({"high": len(actual_a) + len(actual_b), "targets": len(high_targets),
                      "indeterminate": len(actual_i), "indeterminate_decisions": decisions,
                      "hashes": hashes}, ensure_ascii=False))


if __name__ == "__main__":
    build()
