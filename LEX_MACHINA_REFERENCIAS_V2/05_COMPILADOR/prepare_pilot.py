"""Emit deterministic artifacts to stdout; caller persists them with apply_patch.

Reads no human labels, historical decisions, or score fields. The work and device
curation files are independent data inputs, not generated from target outcomes.
"""
import json
from pathlib import Path
from proof_compiler import load, digest, serialized, source_hash, CanonicalInput

ROOT = Path(__file__).resolve().parents[1]


def prepare():
    devices = load(ROOT / "02_DISPOSITIVOS/DISPOSITIVOS_PILOTO_V2.json")["devices"]
    works = load(ROOT / "03_OBRAS/EVIDENCIAS_PILOTO_V2.json")["works"]
    concepts, predicates = set(), set()
    for d in devices:
        for n in d["nuclei"]:
            p = n["proposition"]
            concepts.update(p["sujeitos"] + p["objetos"])
            predicates.add(p["predicado"])
            for c in n["contracts_by_relation"]:
                r = c["requires"]
                concepts.update(r["objects_all"] + r["subjects_any"] + r["context_all"])
                predicates.update(r["predicates"])
    for w in works:
        for e in w["evidences"]:
            e["source"]["hash"] = source_hash(e["source"])
            for k in ("subjects", "objects", "context", "effects"):
                concepts.update(e["claim"][k])
            predicates.add(e["claim"]["predicate"])
    negative_pairs = [("RACA", "REPARACAO"), ("SAUDE", "PROFISSIONAL_SAUDE"),
                      ("SAUDE", "AGENTE_COMUNITARIO_SAUDE"), ("FAMILIA", "SALARIO_FAMILIA"),
                      ("PROPRIEDADE", "PEQUENA_PROPRIEDADE_RURAL"), ("TRABALHO", "JUSTICA_DO_TRABALHO")]
    concepts.update(c for pair in negative_pairs for c in pair)
    ontology = {"version": "CONCEPTS_V2_PILOT_1", "concepts": [
        {"id": c, "label": c.replace("_", " ").lower(), "state": "CURADA_EXPERIMENTAL"} for c in sorted(concepts)],
        "predicates": sorted(predicates),
        "equivalences": {"SIGILO_COMUNICACOES": "COMUNICACAO_PRIVADA"},
        "hierarchy": [{"parent": a, "child": b, "relation": "DOMINIO_NAO_EQUIVALENCIA"} for a, b in negative_pairs[1:]],
        "non_equivalences": negative_pairs,
        "policy": "Hierarquia serve à recuperação; apenas equivalências expressamente curadas entram na prova."}
    data = {"schema_version": "CANONICAL_EVALUATION_INPUT_V2", "scope": "PILOT_25_DEVICES_21_WORKS",
            "devices": devices, "works": works, "ontology": ontology,
            "source_policy": "Curadoria experimental auditável, não revisão humana independente."}
    inp = CanonicalInput(data)
    families = {"version": "TEMPLATES_V2_PILOT_1", "families": sorted({d["family"] for d in devices}),
                "template": {"fields": ["modalidade", "sujeitos", "predicado", "objetos", "condicoes", "excecoes", "finalidades"],
                             "proof": "conjunção de argumentos dentro de uma afirmação; disjunção entre núcleos, preservando âncoras"}}
    return {"04_CONCEITOS/CONCEITOS_PILOTO_V2.json": serialized(ontology),
            "01_SCHEMA/TEMPLATES_PILOTO_V2.json": serialized(families),
            "01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_PILOTO.json": serialized(data),
            "00_CHECKPOINTS/PILOTO_REPRESENTATIONS_FREEZE.json": serialized({
                "logical_timestamp": "V2-P01-REPRESENTATIONS-0002", "input_hash": inp.hash,
                "device_representation_hash": digest(devices), "work_evidence_hash": digest(works),
                "ontology_hash": digest(ontology), "labels_loaded_for_pilot": False,
                "preexposure": "Agente conhecia auditoria e exemplos; isolamento de dados, não cegamento cognitivo.",
                "evidence_validated_meaning": "Paráfrase conferida documentalmente; ainda sujeita a revisão humana semântica."})}


if __name__ == "__main__":
    print(json.dumps({"files": prepare()}, ensure_ascii=False))
