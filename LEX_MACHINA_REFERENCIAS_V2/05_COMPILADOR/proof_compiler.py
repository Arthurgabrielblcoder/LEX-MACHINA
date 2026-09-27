"""Offline proof interpreter. No title/address gates, historical engine, or labels.

All callers use CanonicalInput and evaluate_pair. Retrieval is deliberately exhaustive
within the supplied scope. Closed concept IDs, typed predicates and same-claim
arguments validate proofs; raw prose and lexical retrieval never do.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

VERSION = "REFERENCE_PROOF_COMPILER_V2_PILOT_1"
RELATIONS = {"REPRESENTACAO", "ILUSTRACAO_DE_VIOLACAO", "ILUSTRACAO_DE_CONSEQUENCIA", "CONTEXTUALIZACAO_HISTORICA", "ANALOGIA_CONTROLADA"}
OBJECTS = {"VALOR_DIREITO", "PROBLEMA_SOCIAL", "GARANTIA", "INSTITUTO", "COMPETENCIA_POLITICA", "MECANISMO_PROCEDIMENTO"}
STATES = {"ADMISSIVEL", "INCOMPATIVEL", "EVIDENCIA_INSUFICIENTE", "FONTE_EM_REVISAO", "REVISAO_EDITORIAL"}
POSITIVE_CONTENT = {"EVENTO_NARRATIVO", "EVENTO_AUTOBIOGRAFICO", "ARGUMENTO_ACADEMICO", "ARGUMENTO_DOCUMENTAL", "PRATICA_INSTITUCIONAL", "MECANICA_JOGO"}


def serialized(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def digest(value):
    return hashlib.sha256(serialized(value).encode("utf-8")).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def source_hash(source):
    return digest({k: source[k] for k in ("identifier", "locator", "paraphrase")})


def lexical_tokens(text):
    """Retrieval only. Not called by proof evaluation."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.findall(r"[a-z0-9]+", text)


def lexical_phrase(phrase, text):
    p, t = lexical_tokens(phrase), lexical_tokens(text)
    return bool(p) and any(t[i:i + len(p)] == p for i in range(len(t) - len(p) + 1))


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


class CanonicalInput:
    """One immutable-by-hash data contract, reused by every runner."""
    def __init__(self, data):
        self.data = json.loads(json.dumps(data))
        self.hash = digest(self.data)
        require(data["schema_version"] == "CANONICAL_EVALUATION_INPUT_V2", "input version")
        self.devices = {d["device_id"]: d for d in self.data["devices"]}
        self.works = {w["work_id"]: w for w in self.data["works"]}
        self.concepts = {c["id"]: c for c in self.data["ontology"]["concepts"]}
        self.predicates = set(self.data["ontology"]["predicates"])
        require(len(self.devices) == len(data["devices"]), "duplicate device")
        require(len(self.works) == len(data["works"]), "duplicate work")
        require(len(self.concepts) == len(data["ontology"]["concepts"]), "duplicate concept")
        self.synonyms = self.data["ontology"].get("equivalences", {})
        require(all(x in self.concepts for x in self.synonyms.values()), "synonym target")
        self._validate()

    def concept(self, value):
        # Only explicitly curated equivalence, never parent/child propagation.
        return self.synonyms.get(value, value)

    def same_concept(self, a, b):
        return self.concept(a) in self.concepts and self.concept(a) == self.concept(b)

    def _concepts(self, values):
        require(isinstance(values, list), "concept array required")
        require(all(self.concept(c) in self.concepts for c in values), "unknown concept ID")

    def _validate(self):
        evidence_ids = set()
        for d in self.devices.values():
            require(all(k in d for k in ("device_id", "source_version", "source_hash", "text_identity_status", "hierarchical_context", "nuclei", "text")), "device fields")
            require(re.fullmatch(r"[a-f0-9]{64}", d["source_hash"]) is not None, "source hash")
            ns = {n["nucleus_id"]: n for n in d["nuclei"]}
            require(len(ns) == len(d["nuclei"]), "duplicate nucleus")
            for n in ns.values():
                require(all(k in n for k in ("source_spans", "template", "proposition", "role", "depends_on", "contracts_by_relation", "state", "provenance")), "nucleus fields")
                require(n["role"] in {"AUTONOMO", "DEPENDENTE", "GARANTIA_TRANSVERSAL"}, "nucleus role")
                require(n["role"] != "DEPENDENTE" or n["depends_on"], "unanchored dependent")
                require(set(n["depends_on"]) <= ns.keys(), "missing anchor")
                require(n["source_spans"], "missing spans")
                for s in n["source_spans"]:
                    require(s["device_id"] == d["device_id"] and 0 <= s["start"] < s["end"] <= len(d["text"]), "invalid span")
                    require(d["text"][s["start"]:s["end"]] == s["text"], "span text mismatch")
                p = n["proposition"]
                require(all(k in p for k in ("modalidade", "sujeitos", "predicado", "objetos", "condicoes", "excecoes", "finalidades")), "proposition fields")
                for k in ("sujeitos", "objetos"):
                    self._concepts(p[k])
                require(p["predicado"] in self.predicates, "unknown legal predicate")
                for c in n["contracts_by_relation"]:
                    require(c["relation"] in RELATIONS and c["object_reached"] in OBJECTS, "relation axes")
                    r = c["requires"]
                    require(r["predicates"] and set(r["predicates"]) <= self.predicates, "predicate requirement")
                    require(r["objects_all"], "empty object requirement")
                    for k in ("objects_all", "subjects_any", "context_all"):
                        self._concepts(r[k])
            def visit(nid, trail):
                require(nid not in trail, "dependency cycle")
                for dep in ns[nid]["depends_on"]:
                    visit(dep, trail | {nid})
            for nid in ns:
                visit(nid, set())
        for w in self.works.values():
            require("evidences" in w, "missing evidence dossier")
            for e in w["evidences"]:
                require(e["evidence_id"] not in evidence_ids, "duplicate evidence")
                evidence_ids.add(e["evidence_id"])
                require(e["work_id"] == w["work_id"], "cross-work evidence")
                require(e["state"] in {"VALIDADA", "PROPOSTA", "INSUFICIENTE", "CONTRADITA"}, "evidence state")
                require(e["polarity"] in {"AFIRMADA", "NEGADA", "LIMITACAO"}, "polarity")
                claim = e["claim"]
                require(claim["predicate"] in self.predicates, "unknown claim predicate")
                for k in ("subjects", "objects", "context", "effects"):
                    self._concepts(claim[k])
                if e["state"] == "VALIDADA":
                    s = e["source"]
                    require(all(isinstance(s.get(k), str) and s[k].strip() for k in ("identifier", "locator", "paraphrase")), "source is not evidence")
                    require(s["hash"] == source_hash(s), "evidence source card hash mismatch")
                    require(bool(e["transposition_limits"]), "missing scope limits")
        # Labels may only exist in independent evaluation output, not nested features.
        def check_keys(v):
            if isinstance(v, dict):
                require(not ({"rotulo_humano", "decisao_humana", "features_simulacao", "expected_label"} & v.keys()), "human label/synthetic feature in input")
                for x in v.values():
                    check_keys(x)
            elif isinstance(v, list):
                for x in v:
                    check_keys(x)
        check_keys(self.data)

    def assert_unchanged(self):
        require(digest(self.data) == self.hash, "canonical input mutated")


def match_claim(inp, claim, requirements):
    """All mandatory arguments must be in the same documented assertion."""
    canonical = lambda xs: {inp.concept(x) for x in xs}
    return (claim["predicate"] in requirements["predicates"]
            and canonical(requirements["objects_all"]) <= canonical(claim["objects"])
            and canonical(requirements["context_all"]) <= canonical(claim["context"])
            and (not requirements["subjects_any"]
                 or bool(canonical(requirements["subjects_any"]) & canonical(claim["subjects"]))))


def evaluate_pair(inp, device_id, work_id):
    require(device_id in inp.devices and work_id in inp.works, "pair outside canonical input")
    d, w = inp.devices[device_id], inp.works[work_id]
    result = {"device_id": device_id, "work_id": work_id, "input_hash": inp.hash,
              "compiler_version": VERSION, "retrieved": True, "retrieval": "EXHAUSTIVE_WITHIN_DECLARED_SCOPE",
              "state": "EVIDENCIA_INSUFICIENTE", "proofs": [], "unmet_contracts": [],
              "editorial_score": None, "selected": False}
    if d["text_identity_status"] == "FONTE_EM_REVISAO":
        result.update(state="FONTE_EM_REVISAO", reason="Identidade textual/contextual sob revisão.")
        return result
    positive, negative = {}, {}
    for n in d["nuclei"]:
        nid = n["nucleus_id"]
        positive[nid], negative[nid] = [], []
        for index, c in enumerate(n["contracts_by_relation"]):
            hits, contrary = [], []
            for e in w["evidences"]:
                if e["state"] != "VALIDADA" or e["content_type"] not in POSITIVE_CONTENT:
                    continue
                if match_claim(inp, e["claim"], c["requires"]):
                    if e["polarity"] == "AFIRMADA":
                        hits.append(e)
                    elif e["polarity"] == "NEGADA":
                        contrary.append(e)
            if hits:
                positive[nid].append({"nucleus_id": nid, "contract_index": index,
                    "relation": c["relation"], "object_reached": c["object_reached"],
                    "evidence_ids": sorted(e["evidence_id"] for e in hits),
                    "source_hashes": sorted({e["source"]["hash"] for e in hits}),
                    "legal_proposition": n["proposition"],
                    "affirmed_scope": {"relation": c["relation"], "object_reached": c["object_reached"], "matched_requirements": c["requires"]},
                    "scope_policy": c["scope_policy"],
                    "not_affirmed": sorted({s for e in hits for s in e["transposition_limits"]} | {"Não afirma cobertura integral das condições, exceções, sujeitos ou finalidades do dispositivo."}),
                    "requires_editorial_review": bool(c["editorial_review"] or contrary or n["state"] != "CURADA_EXPERIMENTAL")})
            else:
                result["unmet_contracts"].append({"nucleus_id": nid, "contract_index": index,
                    "requires": c["requires"], "reason": "Sem afirmação validada que satisfaça conjuntamente os papéis exigidos."})
            if contrary:
                negative[nid].append(index)
    proven = set()
    while True:
        updated = proven | {n["nucleus_id"] for n in d["nuclei"]
                            if positive[n["nucleus_id"]] and set(n["depends_on"]) <= proven}
        if updated == proven:
            break
        proven = updated
    for n in d["nuclei"]:
        if n["nucleus_id"] in proven:
            for p in positive[n["nucleus_id"]]:
                p["anchors"] = n["depends_on"]
                result["proofs"].append(p)
    result["proofs"].sort(key=lambda p: (p["nucleus_id"], p["contract_index"]))
    if result["proofs"]:
        result["state"] = "ADMISSIVEL" if any(not p["requires_editorial_review"] for p in result["proofs"]) else "REVISAO_EDITORIAL"
        result["reason"] = "Há prova de ao menos um núcleo com suas dependências; alcance parcial explícito."
    elif d["nuclei"] and all(n["contracts_by_relation"] and len(negative[n["nucleus_id"]]) == len(n["contracts_by_relation"]) for n in d["nuclei"]):
        result.update(state="INCOMPATIVEL", reason="Todas as rotas contratuais possuem evidência negativa explícita; não mera ausência.")
    else:
        result["reason"] = "Ausência de prova completa não é incompatibilidade; adquirir evidência/representação."
    return result


def run_pairs(inp, pairs):
    inp.assert_unchanged()
    out = [evaluate_pair(inp, p["device_id"], p["work_id"]) for p in pairs]
    inp.assert_unchanged()
    return out


def run_exhaustive(inp):
    return run_pairs(inp, ({"device_id": d, "work_id": w}
                          for d in sorted(inp.devices) for w in sorted(inp.works)))


def attach_historical_scores(results, scores):
    """Score is read from frozen historical output only AFTER the proof decision."""
    out = json.loads(json.dumps(results))
    for row in out:
        if row["state"] == "ADMISSIVEL":
            row["editorial_score"] = scores.get((row["device_id"], row["work_id"]))
            row["score_provenance"] = "Frozen historical artifact; not a proof and not recalibrated."
    return out
