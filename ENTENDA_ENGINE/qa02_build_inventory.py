"""QA-02: deterministic risk inventory and stratified sampling (no editorial writes)."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "derived/qa02_independent_legal_audit"
CORPUS = HERE / "derived/candidate_cc_001_2046/CC2002_CC13.entenda.jsonl"
SEED = "LEX-MACHINA-QA02-A-SAMPLE-v1"
SENTINELS = {f"CC2002:ART.{n}" for n in (157, 202, 406, "421-A", 1790, 1829)}

MATRICES = (
    ("CC03", "derived/production_cc_001_114/CC03_AUDIT_MATRIX.json"),
    ("CC04", "derived/production_cc_001_114/CC04_DELEGATED_REVIEW_MATRIX.json"),
    ("CC05", "derived/production_cc_001_114/CC05_CONSOLIDATED_MATRIX.json"),
    ("CC06", "derived/candidate_cc_001_250/CC06_DELEGATED_REVIEW_MATRIX.json"),
    ("CC07", "derived/candidate_cc_001_400/CC07_DELEGATED_REVIEW_MATRIX.json"),
    ("CC08", "derived/candidate_cc_001_550/CC08_DELEGATED_REVIEW_MATRIX.json"),
    ("CC09", "derived/candidate_cc_001_700/CC09_DELEGATED_REVIEW_MATRIX.json"),
    ("CC10", "derived/candidate_cc_001_1040/CC10_DELEGATED_REVIEW_MATRIX.json"),
    ("CC11", "derived/candidate_cc_001_1380/CC11_DELEGATED_REVIEW_MATRIX.json"),
    ("CC12", "derived/candidate_cc_001_1720/CC12_DELEGATED_REVIEW_MATRIX.json"),
    ("CC13", "derived/candidate_cc_001_2046/CC13_DELEGATED_REVIEW_MATRIX.json"),
)

BOOKS = (
    ("PARTE_GERAL", 1, 232),
    ("OBRIGACOES_E_CONTRATOS", 233, 965),
    ("EMPRESA", 966, 1195),
    ("DIREITOS_REAIS", 1196, 1510),
    ("FAMILIA", 1511, 1783),
    ("SUCESSOES", 1784, 2027),
    ("COMPLEMENTARES_E_FINAIS", 2028, 2046),
)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def records(doc):
    for key in ("records", "rows", "explanations"):
        if isinstance(doc.get(key), list):
            return doc[key]
    return []


def article_number(target_id):
    raw = target_id.split("ART.", 1)[1].split(":", 1)[0]
    return int(raw.split("-", 1)[0])


def book(target_id):
    n = article_number(target_id)
    return next(name for name, lo, hi in BOOKS if lo <= n <= hi)


def score(target_id):
    return hashlib.sha256(f"{SEED}|{target_id}".encode("ascii")).hexdigest()


def mission_for(target_id):
    n = article_number(target_id)
    for mission, lo, hi in (("CC02-CC05", 1, 114), ("CC06", 115, 250), ("CC07", 251, 400),
                            ("CC08", 401, 550), ("CC09", 551, 700), ("CC10", 701, 1040),
                            ("CC11", 1041, 1380), ("CC12", 1381, 1720), ("CC13", 1721, 2046)):
        if lo <= n <= hi:
            return mission
    raise ValueError(target_id)


def main():
    rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line.strip()]
    active = {r["target_id"]: r for r in rows if r["status"] == "ACTIVE"}
    retired_targets = {r["target_id"] for r in rows if r["status"] == "RETIRED"}
    origins = defaultdict(list)
    matrix_counts = {}
    for mission, rel in MATRICES:
        path = HERE / rel
        doc = load_json(path)
        matrix_counts[mission] = len(records(doc))
        for r in records(doc):
            target = r.get("target_id")
            if target not in active:
                continue
            classification = r.get("classification")
            status = r.get("audit_status")
            label = r.get("classification_label", "")
            if classification == "B" or status == "CORRIGIDO_COM_EVIDENCIA" or "APOS_CORRECAO" in label:
                origins[target].append(dict(mission=mission, matrix=rel, classification=classification,
                                            audit_status=status, classification_label=label or None))
    for target in retired_targets & active.keys():
        origins[target].append(dict(mission=mission_for(target), matrix="corpus_history",
                                    classification=None, audit_status="ACTIVE_WITH_RETIRED_VERSION",
                                    classification_label=None))

    priority = sorted(origins, key=lambda t: (article_number(t), t))
    priority_rows = [dict(target_id=t, explanation_id=active[t]["explanation_id"], book=book(t),
                          mission=mission_for(t), origins=origins[t]) for t in priority]

    # A sample excludes every target with a B/correction trajectory and every mandatory sentinel.
    eligible_a = [t for t in active if t not in origins and t not in SENTINELS]
    strata = defaultdict(list)
    for t in eligible_a:
        strata[(book(t), mission_for(t))].append(t)
    sample = []
    for (book_name, mission), targets in sorted(strata.items()):
        for t in sorted(targets, key=lambda x: (score(x), x))[:2]:
            sample.append(dict(target_id=t, explanation_id=active[t]["explanation_id"], book=book_name,
                               mission=mission, deterministic_score=score(t)))

    # First auditable B wave: deterministic breadth, at most two per represented book/mission stratum, plus B sentinels.
    b_strata = defaultdict(list)
    for t in priority:
        b_strata[(book(t), mission_for(t))].append(t)
    b_wave = set(SENTINELS & set(priority))
    for targets in b_strata.values():
        b_wave.update(sorted(targets, key=lambda x: (score(x), x))[:2])

    insurance_active = sorted(t for t in active if 757 <= article_number(t) <= 802)
    corpus_hash = hashlib.sha256(CORPUS.read_bytes()).hexdigest()
    doc = dict(
        schema_version=1,
        mission="QA-02",
        generated_by="ENTENDA_ENGINE/qa02_build_inventory.py",
        selection_seed=SEED,
        corpus=dict(path=CORPUS.relative_to(ROOT).as_posix(), sha256=corpus_hash, versions=len(rows),
                    active=len(active), retired=sum(r["status"] == "RETIRED" for r in rows)),
        matrix_counts=matrix_counts,
        priority_b_or_substantive_correction=dict(total=len(priority_rows), by_book=dict(sorted(Counter(r["book"] for r in priority_rows).items())),
                                                  by_mission=dict(sorted(Counter(r["mission"] for r in priority_rows).items())), records=priority_rows),
        first_b_audit_wave=dict(total=len(b_wave), target_ids=sorted(b_wave, key=lambda t: (article_number(t), t))),
        stratified_a_sample=dict(universe=len(eligible_a), total=len(sample), strata=len(strata), per_stratum=2,
                                 criterion="two lowest SHA-256 scores of seed|target_id per (book, origin mission)", records=sample),
        mandatory_sentinels=sorted(SENTINELS, key=lambda t: (article_number(t), t)),
        insurance_757_802=dict(active_count=len(insurance_active), active_target_ids=insurance_active,
                               expectation="zero active explanations after Lei 15.040/2024"),
        limitations=["Matrizes anteriores identify priority/history only and are not evidence of current legal correctness.",
                     "Selection does not imply that any record has been legally audited."],
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "QA02_RISK_INVENTORY.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(dict(priority=len(priority_rows), b_wave=len(b_wave), a_universe=len(eligible_a), a_sample=len(sample),
                          a_strata=len(strata), insurance_active=len(insurance_active)), ensure_ascii=False))


if __name__ == "__main__":
    main()
