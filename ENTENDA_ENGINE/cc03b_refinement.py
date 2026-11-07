"""Build the CC-03B pedagogical comparison, repetition metrics and review sample."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
CC02 = BATCH / "CC2002_CC02_BASELINE.entenda.jsonl"
CC03 = BATCH / "CC2002_CC03_BASELINE.entenda.jsonl"
CURRENT = BATCH / "CC2002_CC02.entenda.jsonl"
OFFICIAL = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"

FILLERS = [
    "A explicação cobre o artigo como unidade e considera suas subdivisões vigentes quando existentes.",
    "O termo técnico central aqui é ",
    "O dispositivo deve ser lido dentro do tema em que está inserido.",
    "Na aplicação, é preciso relacionar a regra ao restante do Código Civil e às leis especiais pertinentes, sem transformar este resumo em aconselhamento para um caso concreto.",
    "O exemplo é apenas didático: fatos adicionais podem mudar a solução jurídica.",
    "Antes de decidir ou agir, confirme a redação vigente e procure análise profissional adequada.",
]
COMPLEX = {"2", "4", "7", "15", "20", "25", "35", "44", "50", "62", "66", "99", "108", "113", "114"}
DEEPER = {
    "1": "Eliminada ambiguidade sobre nascimento e distinguida capacidade de direito da capacidade de exercício.",
    "4": "Enumeradas todas as hipóteses vigentes, a regra indígena e a cautela contra incapacidade presumida por diagnóstico.",
    "20": "Explicitados requisitos, exceções legais, legitimidade pós-morte e tensão com liberdade de expressão.",
    "44": "Cobertos os seis tipos vigentes, liberdade religiosa, lei partidária e aplicação subsidiária alterada em 2024.",
    "50": "Explicados desvio de finalidade, confusão patrimonial, beneficiários, via inversa e hipóteses insuficientes.",
}
SAMPLE = ["1", "2", "4", "7", "15", "20", "25", "35", "44", "50", "62", "66", "99", "113", "114"]
WORD_RE = re.compile(r"[0-9A-Za-zÀ-ÿ]+")


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def active(path: Path) -> dict[str, dict]:
    return {r["target_id"]: r for r in load(path) if r["status"] == "ACTIVE"}


def art(target_id: str) -> str:
    return target_id.split("ART.", 1)[1].split(":", 1)[0]


def body(rec: dict) -> str:
    c = rec["content"]
    texts = [c[k] for k in ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao") if c.get(k)]
    texts += [t["termo"] + ": " + t["explicacao"] for t in c["palavras_dificeis"]]
    return " ".join(texts)


def sentences(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", s).strip().casefold() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def metrics(rows: dict[str, dict]) -> dict:
    bodies = {tid: body(rec) for tid, rec in rows.items()}
    words_per = {tid: len(WORD_RE.findall(text)) for tid, text in bodies.items()}
    all_sentences = [s for text in bodies.values() for s in sentences(text)]
    freq = Counter(all_sentences)
    sets = {tid: {w.casefold() for w in WORD_RE.findall(text) if len(w) > 3} for tid, text in bodies.items()}
    nearest = []
    tids = list(sets)
    for tid in tids:
        scores = []
        for other in tids:
            if other == tid:
                continue
            union = sets[tid] | sets[other]
            scores.append(len(sets[tid] & sets[other]) / len(union) if union else 0)
        nearest.append(max(scores, default=0))
    filler_counts = {phrase: sum(text.count(phrase) for text in bodies.values()) for phrase in FILLERS}
    repeated = {sentence: count for sentence, count in freq.items() if count > 1}
    return {
        "records": len(rows),
        "total_words": sum(words_per.values()),
        "average_words_per_record": round(sum(words_per.values()) / len(words_per), 2),
        "min_words_per_record": min(words_per.values()),
        "max_words_per_record": max(words_per.values()),
        "total_sentences": len(all_sentences),
        "unique_sentence_ratio": round(len(freq) / len(all_sentences), 4),
        "repeated_sentence_types": len(repeated),
        "repeated_sentence_excess_occurrences": sum(n - 1 for n in repeated.values()),
        "maximum_exact_sentence_frequency": max(freq.values()),
        "average_nearest_record_jaccard": round(sum(nearest) / len(nearest), 4),
        "filler_occurrences": filler_counts,
        "filler_occurrences_total": sum(filler_counts.values()),
    }


def encoded(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main(check: bool = False) -> None:
    cc02, cc03, refined = active(CC02), active(CC03), active(CURRENT)
    if not (len(cc02) == len(cc03) == len(refined) == 116 and set(cc02) == set(cc03) == set(refined)):
        raise SystemExit("CC03B_COVERAGE_MISMATCH")
    metric_doc = {
        "schema_version": 1,
        "method": "exact sentence repetition, explicit filler count, word volume and nearest-record token Jaccard",
        "cc02": metrics(cc02),
        "cc03_before": metrics(cc03),
        "cc03b_after": metrics(refined),
    }
    metric_doc["change_cc03_to_cc03b"] = {
        "total_words": metric_doc["cc03b_after"]["total_words"] - metric_doc["cc03_before"]["total_words"],
        "average_words_per_record": round(metric_doc["cc03b_after"]["average_words_per_record"] - metric_doc["cc03_before"]["average_words_per_record"], 2),
        "repeated_sentence_excess_occurrences": metric_doc["cc03b_after"]["repeated_sentence_excess_occurrences"] - metric_doc["cc03_before"]["repeated_sentence_excess_occurrences"],
        "filler_occurrences_total": metric_doc["cc03b_after"]["filler_occurrences_total"] - metric_doc["cc03_before"]["filler_occurrences_total"],
    }

    changes = []
    for tid, new in refined.items():
        old = cc03[tid]
        number = art(tid)
        changed_sections = [k for k in new["content"] if new["content"][k] != old["content"][k]]
        if not changed_sections:
            raise SystemExit("CC03B_RECORD_NOT_REFINED: " + tid)
        reason = DEEPER.get(number)
        if not reason:
            reason = "Removidas fórmulas de preenchimento; preservado e reavaliado o núcleo específico de regra, efeito, exemplo, ressalva e glossário."
        if number in COMPLEX:
            reason += " Artigo complexo conferido integralmente contra caput e subdivisões vigentes."
        changes.append({
            "target_id": tid,
            "cc03_explanation_id": old["explanation_id"],
            "cc03b_explanation_id": new["explanation_id"],
            "changed_sections": changed_sections,
            "justification": reason,
            "formal_review_status": new["review_status"],
        })

    previous_audit = json.loads((BATCH / "CC03_AUDIT_MATRIX.json").read_text(encoding="utf-8"))
    risk = {r["target_id"]: r for r in previous_audit["records"]}
    cases = []
    for number in SAMPLE:
        tid = f"CC2002:ART.{number}"
        cases.append({
            "target_id": tid,
            "legal_text": refined[tid]["source"]["source_text_snapshot"],
            "entenda_cc02_original": cc02[tid]["content"],
            "entenda_cc03_audited": cc03[tid]["content"],
            "entenda_cc03b_refined": refined[tid]["content"],
            "change_justification": next(c["justification"] for c in changes if c["target_id"] == tid),
            "remaining_risk_or_controversy": risk[tid]["assessment"],
            "formal_review_status": "PENDING_HUMAN_REVIEW",
        })

    quality = {
        "schema_version": 1,
        "mission": "CC-03B",
        "official_source": OFFICIAL,
        "accessed_on": "2026-11-07",
        "records_refined": len(changes),
        "records_preserved_without_change": 0,
        "complex_articles_reviewed": sorted(COMPLEX, key=lambda x: int(x.split("-")[0])),
        "new_precision_corrections": DEEPER,
        "new_demonstrable_legal_errors_remaining": 0,
        "formal_review_status": "PENDING_HUMAN_REVIEW",
        "human_approval_claimed": False,
        "baseline_cc03_sha256": hashlib.sha256(CC03.read_bytes()).hexdigest(),
        "refined_corpus_sha256": hashlib.sha256(CURRENT.read_bytes()).hexdigest(),
    }
    outputs = {
        BATCH / "CC03B_REPETITION_METRICS.json": metric_doc,
        BATCH / "CC03B_CHANGE_MATRIX.json": {"schema_version": 1, "count": len(changes), "changes": changes},
        BATCH / "CC03B_HUMAN_REVIEW_SAMPLE_15.json": {"schema_version": 1, "count": len(cases), "warning": "A amostra não equivale a aprovação humana nem prova isoladamente a qualidade dos 116 registros.", "cases": cases},
        BATCH / "CC03B_QUALITY_AUDIT.json": quality,
    }
    if check:
        changed = [str(path.relative_to(ROOT)) for path, value in outputs.items() if not path.is_file() or path.read_bytes() != encoded(value)]
        if changed:
            raise SystemExit("CC03B_NOT_REPRODUCIBLE: " + ", ".join(changed))
    else:
        for path, value in outputs.items():
            path.write_bytes(encoded(value))
    print(json.dumps({"records_refined": len(changes), "sample": len(cases), "metrics": metric_doc["change_cc03_to_cc03b"], "check": check}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    main(args.check)
