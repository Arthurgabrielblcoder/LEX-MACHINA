"""Evaluation-only reader. Refuses to open labels until proof freeze matches."""
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "05_COMPILADOR"))
from proof_compiler_r1 import load, digest, serialized, file_hash


def compare():
    proof = load(ROOT / "06_BENCHMARKS/PROVAS_PILOTO_V2_R1.json")
    freeze = load(ROOT / "00_CHECKPOINTS/PILOTO_R1_PROOFS_FREEZE.json")
    assert digest(proof) == freeze["proofs_hash"]
    assert file_hash(ROOT / "05_COMPILADOR/proof_compiler_r1.py") == freeze["compiler_sha256"]
    wanted = {(r["device_id"], r["work_id"]) for r in proof["pairs"]}
    labels = defaultdict(list)
    for file in ["LEX_MACHINA_REFERENCIAS_BENCHMARK_69_HUMANO_V1/BENCHMARK_HUMANO_134.json",
                 "LEX_MACHINA_REFERENCIAS_VALIDACAO_V14_ALPHA3/RESULTADO_EXTERNO_ALPHA3.json"]:
        for r in load(REPO / file)["casos"]:
            key = (r["dispositivo_id"], r["obra_id"])
            if key in wanted:
                labels[key].append({"decision": r["decisao_humana"], "file": file,
                                    "source_id": r.get("benchmark_id", r.get("id")), "source_hash": file_hash(REPO / file)})
    file = "LEX_MACHINA_REFERENCIAS_AUDITORIA_ASTRA_V1/TAXONOMIA_ERROS_589.json"
    recent = load(REPO / file)["resultados_humanos_80"]
    for group in ["amostra_sobreviventes", "amostra_rejeitados"]:
        for r in recent[group]:
            key = (r["dispositivo_id"], r["obra_id"])
            if key in wanted:
                labels[key].append({"decision": r["decisao_humana_informada"], "file": file,
                                    "source_id": group + "/" + str(r["numero"]), "source_hash": file_hash(REPO / file)})
    cases = []
    for row in proof["pairs"]:
        key = (row["device_id"], row["work_id"])
        provenance = labels.get(key, [])
        values = {r["decision"] for r in provenance}
        label = next(iter(values)) if len(values) == 1 else ("CONFLITO" if values else "SEM_ROTULO_ENCONTRADO")
        predicted = row["state"] == "ADMISSIVEL"
        metric = ("TP" if predicted else "FN") if label == "APROVAR" else (("FP" if predicted else "TN_NAO_PUBLICADO") if label == "REJEITAR" else "NAO_AVALIAVEL")
        cases.append({"pilot_id": row["pilot_id"], "device_id": key[0], "work_id": key[1],
                      "human_label": label, "v2_state": row["state"], "metric": metric, "provenance": provenance})
    result = {"schema": "PILOT_EVALUATION_V2", "proofs_hash": freeze["proofs_hash"],
              "evaluation_after_freeze": True, "known_pairs": sum(bool(c["provenance"]) for c in cases),
              "counts": dict(Counter(c["metric"] for c in cases)), "cases": cases,
              "warning": "TN_NAO_PUBLICADO agrega abstenção e incompatibilidade; não é medição de rejeição semântica. Piloto conhecido não mede precisão global."}
    return {"06_BENCHMARKS/COMPARACAO_PILOTO_V2_R1.json": serialized(result)}


if __name__ == "__main__": print(json.dumps({"files": compare()}, ensure_ascii=False))
