"""Generate the complete CC-03 legal-audit trail from the pinned official text.

Audit status is deliberately separate from ENTENDA's human review status.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
BASELINE = BATCH / "CC2002_CC02_BASELINE.entenda.jsonl"
CURRENT_CORPUS = BATCH / "CC2002_CC02.entenda.jsonl"
CC03_BASELINE = BATCH / "CC2002_CC03_BASELINE.entenda.jsonl"
OFFICIAL_URL = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
ACCESSED_ON = "2026-11-07"

CORRECTIONS = {
    "7": "Incluídos o prazo de dois anos após o fim da guerra, o esgotamento das buscas e a fixação judicial da data provável.",
    "10": "Removida adoção da enumeração vigente e registrado que o antigo inciso III está revogado.",
    "22": "Incluída a legitimidade de qualquer interessado ou do Ministério Público para requerer a medida.",
    "24": "Retirada a ordem de preferência, que pertence ao art. 25; mantidos apenas poderes e obrigações fixados pelo juiz.",
    "25": "Restaurada a ordem completa: cônjuge qualificado, pais, descendentes e, subsidiariamente, escolha judicial.",
    "26": "Explicitados os prazos de um ano após arrecadação e três anos quando havia representante ou procurador.",
    "28": "Explicitados 180 dias da publicação e distinguidos publicação, trânsito, inventário e comparecimento de interessados.",
    "35": "Corrigida inversão com o art. 36: este dispositivo trata da prova da data exata da morte.",
    "36": "Corrigida inversão com o art. 35: este dispositivo trata do retorno ou da prova de vida.",
    "39": "Substituído o conceito amplo de herdeiro necessário pelos sujeitos expressos: ausente, descendentes e ascendentes.",
    "62": "Acrescentada a enumeração das nove finalidades vigentes e indicado o inciso X vetado.",
    "65": "Incluídos submissão à autoridade, recurso ao juiz e prazo subsidiário de 180 dias.",
    "66": "Eliminada referência inexistente a fundações federais e restaurada a distribuição territorial do velamento.",
    "67": "Incluídos quórum de dois terços e prazo de 45 dias para atuação do Ministério Público.",
    "77": "Incluída a condição de citação no estrangeiro e os dois locais legalmente previstos.",
    "99": "Incluída a regra do parágrafo único sobre pessoas públicas com estrutura de direito privado.",
    "108": "Incluídos o limite superior a trinta salários mínimos e os quatro tipos de operação sobre direitos reais.",
    "113": "Removida alocação de riscos, ausente do artigo, e restaurados os critérios interpretativos efetivamente enumerados.",
}

PRIORITY = {
    "2": "Alcance dos direitos do nascituro é juridicamente controvertido.",
    "4": "Incapacidade relativa exige leitura conjunta com a Lei Brasileira de Inclusão e curatela.",
    "11": "Limitações voluntárias de direitos da personalidade dependem de contexto e legislação especial.",
    "12": "Legitimidade pós-morte e cumulação de tutelas merecem decisão humana.",
    "13": "Autonomia corporal, exigência médica e bons costumes envolvem bioética.",
    "14": "Disposição post mortem convive com legislação sanitária e de transplantes.",
    "15": "Consentimento, risco de vida, emergência e incapacidade exigem ponderação clínica e jurídica.",
    "20": "O texto legal deve ser lido com o controle constitucional indicado na própria fonte oficial.",
    "21": "Privacidade exige ponderação com liberdade de expressão e interesse público.",
    "43": "Responsabilidade estatal deve ser harmonizada com o regime constitucional.",
    "44": "O inciso VII e o § 2º receberam alteração legislativa recente em 2024.",
    "49-A": "Autonomia patrimonial é conceito central com repercussões societárias amplas.",
    "50": "Desconsideração possui requisitos cumulativos, direção subjetiva e controvérsias probatórias.",
    "52": "A aplicação de direitos da personalidade a entidades depende de compatibilidade.",
    "57": "Justa causa, defesa e recurso dependem do estatuto e do devido procedimento.",
    "59": "Competência privativa, convocação e quórum estatutário exigem leitura conjunta.",
    "76": "As categorias de domicílio necessário têm regimes e limites próprios.",
    "104": "Validade não esgota existência, eficácia nem defeitos do negócio jurídico.",
    "105": "A exceção de indivisibilidade pode alterar os efeitos perante cointeressados capazes.",
    "110": "Reserva mental depende de prova do conhecimento do destinatário.",
    "111": "Silêncio como anuência é excepcional e intensamente contextual.",
    "112": "Intenção consubstanciada não equivale a vontade interna secreta.",
    "114": "Interpretação estrita não dispensa boa-fé, contexto e validade da renúncia.",
}

SAMPLE = ["1", "2", "4", "7", "15", "20", "25", "35", "44", "50", "62", "66", "99", "113", "114"]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def article(target_id: str) -> str:
    return target_id.split("ART.", 1)[1].split(":", 1)[0]


def encoded_json(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main(check: bool = False) -> None:
    if sha(BASELINE) != "86ef8d8f1843650e927b2fd2fd620dd92a7fe9508dac8934efbaae238beecd4d":
        raise SystemExit("CC02_BASELINE_HASH_MISMATCH")
    baseline_rows = load_jsonl(BASELINE)
    audited_corpus = CC03_BASELINE if CC03_BASELINE.is_file() else CURRENT_CORPUS
    current_rows = load_jsonl(audited_corpus)
    base = {r["target_id"]: r for r in baseline_rows if r["status"] == "ACTIVE"}
    active = {r["target_id"]: r for r in current_rows if r["status"] == "ACTIVE"}
    if len(base) != 116 or len(active) != 116 or set(base) != set(active):
        raise SystemExit("AUDIT_COVERAGE_MISMATCH")

    audits, corrections = [], []
    for target_id, rec in sorted(active.items(), key=lambda item: int(article(item[0]).split("-")[0]) * 10 + (1 if "-" in article(item[0]) else 0)):
        art = article(target_id)
        if art in CORRECTIONS:
            status = "CORRIGIDO_COM_EVIDENCIA"
            assessment = CORRECTIONS[art]
        elif art in PRIORITY:
            status = "REVISAO_HUMANA_PRIORITARIA"
            assessment = PRIORITY[art]
        else:
            status = "SEM_PROBLEMA_IDENTIFICADO"
            assessment = "Confronto integral com o snapshot consolidado não revelou erro jurídico demonstrável nesta auditoria automatizada."
        audit = {
            "target_id": target_id,
            "explanation_id": rec["explanation_id"],
            "audit_status": status,
            "formal_review_status": rec["review_status"],
            "assessment": assessment,
            "legal_evidence": {
                "official_source": OFFICIAL_URL,
                "accessed_on": ACCESSED_ON,
                "snapshot_sha256": rec["source"]["source_text_sha256"],
                "snapshot": rec["source"]["source_text_snapshot"],
            },
            "checks": [
                "significado jurídico", "regras e exceções", "terminologia", "exemplo prático",
                "vigência e subdivisões", "clareza para pequena tela",
            ],
        }
        audits.append(audit)
        if status == "CORRIGIDO_COM_EVIDENCIA":
            old, new = base[target_id], rec
            changed = {
                key: {"original": old["content"][key], "revisado": new["content"][key]}
                for key in new["content"] if old["content"][key] != new["content"][key]
            }
            corrections.append({
                "target_id": target_id,
                "original_explanation_id": old["explanation_id"],
                "revised_explanation_id": new["explanation_id"],
                "reason": CORRECTIONS[art],
                "confidence": "ALTA",
                "source": OFFICIAL_URL,
                "accessed_on": ACCESSED_ON,
                "changed_sections": changed,
                "tests_required": ["validate_corpus", "build_reproducibility", "cc03_audit_tests"],
            })

    counts = {k: sum(a["audit_status"] == k for a in audits) for k in (
        "SEM_PROBLEMA_IDENTIFICADO", "CORRIGIDO_COM_EVIDENCIA", "REVISAO_HUMANA_PRIORITARIA", "BLOQUEADO_POR_INCONSISTENCIA"
    )}
    matrix = {
        "schema_version": 1,
        "mission": "CC-03",
        "official_source": OFFICIAL_URL,
        "accessed_on": ACCESSED_ON,
        "baseline_corpus_sha256": sha(BASELINE),
        "audited_corpus_sha256": sha(audited_corpus),
        "explanations_audited": len(audits),
        "audit_status_counts": counts,
        "formal_review_status": "PENDING_HUMAN_REVIEW",
        "human_approval_claimed": False,
        "structural_blocked_target": {"target_id": "CC2002:ART.69-A", "reason": "VETADO; sem explicação ativa"},
        "records": audits,
    }
    corrections_doc = {
        "schema_version": 1,
        "count": len(corrections),
        "corrections": corrections,
    }

    audit_by_art = {article(a["target_id"]): a for a in audits}
    sample = []
    for art in SAMPLE:
        target_id = f"CC2002:ART.{art}"
        rec, audit = active[target_id], audit_by_art[art]
        sample.append({
            "target_id": target_id,
            "selection_reason": "controle simples" if art == "1" else ("correção substantiva" if art in CORRECTIONS else "complexidade ou risco jurídico"),
            "legal_text": rec["source"]["source_text_snapshot"],
            "entenda_integral": rec["content"],
            "technical_assessment": audit["assessment"],
            "assessment_basis": audit["legal_evidence"],
            "human_decision_points": [
                "Confirmar fidelidade e suficiência do resumo.",
                "Confirmar se o exemplo preserva as exceções relevantes.",
                "Decidir entre manter, solicitar mudanças ou aprovar humanamente; a auditoria não promove o status.",
            ],
        })
    sample_doc = {
        "schema_version": 1,
        "count": len(sample),
        "warning": "A amostra estratégica não prova a correção das 116 explicações.",
        "cases": sample,
    }
    outputs = {
        BATCH / "CC03_AUDIT_MATRIX.json": matrix,
        BATCH / "CC03_SUBSTANTIVE_CORRECTIONS.json": corrections_doc,
        BATCH / "CC03_HUMAN_REVIEW_SAMPLE_15.json": sample_doc,
    }
    if check:
        changed = [str(path.relative_to(ROOT)) for path, value in outputs.items() if not path.is_file() or path.read_bytes() != encoded_json(value)]
        if changed:
            raise SystemExit("CC03_AUDIT_NOT_REPRODUCIBLE: " + ", ".join(changed))
    else:
        for path, value in outputs.items():
            path.write_bytes(encoded_json(value))
    print(json.dumps({"audited": len(audits), "counts": counts, "corrections": len(corrections), "sample": len(sample), "check": check}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    main(args.check)
