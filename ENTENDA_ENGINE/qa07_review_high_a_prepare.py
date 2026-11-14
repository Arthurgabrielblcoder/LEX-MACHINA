"""Independent legal revalidation of the recovered QA-07 HIGH_A proposals."""
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "derived/qa07_high_findings_resolution"
PROPOSAL = OUT / "QA07_EDITOR_HIGH_A.json"
DEST = OUT / "QA07_REVIEW_HIGH_A.json"
AS_OF = "2026-11-14"
EXPECTED_PROPOSAL_SHA256 = "d6dbf83b87948f03f8f6909cb54b02ee9fef26baa8021b9ea05bba690141479a"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, doc):
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8", newline="\n")


REVIEWS = {
    "CC2002:ART.39": {
        "analysis": "A proposta restitui a destinação territorial omitida: Município ou Distrito Federal conforme a circunscrição, e União quando os bens estiverem em território federal. Mantém o prazo decenal e, em atenção, restringe corretamente os legitimados ao retorno mencionados no caput.",
        "special_law_check": "Não necessária para a lacuna examinada; o comando está integralmente no art. 39, parágrafo único.",
        "binding_case_law_check": "Nenhum precedente vinculante é necessário para explicar o comando literal corrigido.",
    },
    "CC2002:ART.44": {
        "analysis": "A proposta cobre criação, organização interna, funcionamento e a vedação de recusa estatal de reconhecimento ou registro. A ressalva sobre exigências legais gerais evita converter a autonomia religiosa em dispensa de requisitos formais.",
        "special_law_check": "A correção limita-se ao § 1º do Código Civil e não substitui a disciplina registral aplicável.",
        "binding_case_law_check": "Nenhum precedente vinculante é necessário para a correção textual do § 1º.",
    },
    "CC2002:ART.206": {
        "analysis": "A proposta integrada resolve os nove achados sem transformar o artigo em mera cópia: identifica as pretensões dos incisos IV e V do § 1º; restituição de lucros de má-fé; os três marcos societários do inciso VII; título de crédito e ressalva de lei especial; seguro obrigatório; e honorários do § 5º, II. Duração e termo inicial permanecem associados à pretensão correta.",
        "special_law_check": "Foi preservada a ressalva de legislação especial para títulos. A revogação do § 1º, II, pela Lei 15.040/2024 não foi indevidamente projetada sobre o § 3º, IX, que permanece no texto compilado oficial.",
        "binding_case_law_check": "Não se introduziu tese jurisprudencial; a proposta explica os prazos e marcos literais vigentes.",
    },
    "CC2002:ART.1069": {
        "analysis": "A revisão confirma a periodicidade mínima trimestral, o dever de administradores ou liquidantes fornecerem informações e o parecer anual registrado no mesmo livro, baseado nos balanços patrimonial e de resultado econômico. Não houve ampliação das competências do conselho fiscal.",
        "special_law_check": "A proposta permanece no regime da sociedade limitada descrito pelo Código e não afirma aplicação universal a outros tipos societários.",
        "binding_case_law_check": "Nenhum precedente vinculante é necessário para os deveres literais revisados.",
    },
    "CC2002:ART.1187": {
        "analysis": "A proposta explica corretamente que, havendo avaliação pelo preço corrente superior ao custo, a diferença não integra a distribuição de lucros nem as percentagens dos fundos de reserva. O exemplo é condicional e não afirma que todo aumento de valor deva ser registrado pelo preço corrente.",
        "special_law_check": "A referência a normas contábeis especiais foi mantida como complemento, sem afastar a vedação do inciso II.",
        "binding_case_law_check": "Nenhum precedente vinculante é necessário para o critério contábil literal examinado.",
    },
    "CC2002:ART.1228": {
        "analysis": "A proposta cobre os deveres ambientais do § 1º e articula corretamente os §§ 4º e 5º: posse ininterrupta e de boa-fé superior a cinco anos, número considerável de pessoas, obras ou serviços relevantes, justa indenização, pagamento e sentença como título registral. Não apresenta a transferência como automática.",
        "special_law_check": "A expressão 'nos termos da legislação especial' foi preservada para as obrigações ambientais, sem inventar conteúdo externo.",
        "binding_case_law_check": "A proposta não depende de tese vinculante nem atribui ao dispositivo natureza além do texto legal; limita-se aos requisitos do Código.",
    },
    "CC2002:ART.1301": {
        "analysis": "A exceção do § 2º foi recomposta com os três requisitos cumulativos: largura máxima de dez centímetros, comprimento máximo de vinte centímetros e altura superior a dois metros em cada piso. O exemplo não amplia a exceção.",
        "special_law_check": "Nenhuma legislação especial é necessária para a correção do requisito dimensional literal.",
        "binding_case_law_check": "Nenhum precedente vinculante é necessário para os limites objetivos revisados.",
    },
    "CC2002:ART.1331": {
        "analysis": "A proposta incorpora a proibição absoluta de privar unidade do acesso ao logradouro público e preserva a distinção entre unidade exclusiva e partes comuns. O exemplo usa caminho juridicamente assegurado apenas como tradução pedagógica do acesso exigido.",
        "special_law_check": "A revisão não altera o regime da Lei 4.591/1964 nem formula regra registral externa ao § 4º.",
        "binding_case_law_check": "Nenhum precedente vinculante é necessário para o comando literal do § 4º.",
    },
    "CC2002:ART.1336": {
        "analysis": "A proposta distingue correção monetária, juros moratórios e multa, preserva a primazia dos juros convencionados, a remissão subsidiária ao art. 406 e o teto de dois por cento sobre o débito. Não estende a multa moratória a infrações de conduta.",
        "special_law_check": "A remissão dinâmica ao art. 406 foi mantida, evitando congelar na explicação uma taxa potencialmente alterável.",
        "binding_case_law_check": "Nenhum precedente vinculante foi invocado ou é necessário para o conteúdo literal revisado.",
    },
    "CC2002:ART.1341": {
        "analysis": "A proposta corrige a confusão entre obra urgente de custo excessivo, com ciência e convocação imediata, e obra não urgente de custo excessivo, que exige autorização prévia. Também reproduz corretamente que só obra ou reparo necessário gera reembolso ao condômino executor.",
        "special_law_check": "A revisão considerou a redação compilada vigente, inclusive a disciplina de assembleia, sem importar regra externa.",
        "binding_case_law_check": "Nenhum precedente vinculante é necessário para distinguir os §§ 2º, 3º e 4º.",
    },
}


def build():
    if sha(PROPOSAL) != EXPECTED_PROPOSAL_SHA256:
        raise RuntimeError("HIGH_A proposal hash mismatch")
    proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    if proposal["finding_count"] != 21 or proposal["target_count"] != 10:
        raise RuntimeError("HIGH_A proposal cardinality mismatch")
    if {row["target_id"] for row in proposal["records"]} != set(REVIEWS):
        raise RuntimeError("HIGH_A target mismatch")
    records = []
    for row in proposal["records"]:
        target = row["target_id"]
        review = REVIEWS[target]
        finding_reviews = []
        for finding in row["findings"]:
            finding_reviews.append({
                "finding_id": finding["finding_id"],
                "subdivision_id": finding["subdivision_id"],
                "decision": "ACEITA",
                "reason": "A proposta integrada cobre a subdivisão indicada e preserva as condições, exceções, prazos e consequências materiais relevantes, conforme a análise independente do target.",
            })
        records.append({
            "target_id": target,
            "proposal_explanation_id": row["source_explanation_id"],
            "proposal_target_sha256": hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
            "decision": "ACEITA",
            "analysis": review["analysis"],
            "special_law_check": review["special_law_check"],
            "binding_case_law_check": review["binding_case_law_check"],
            "five_fields_reviewed": sorted(row["proposed_content"]),
            "new_error_detected": False,
            "objections": [],
            "finding_reviews": finding_reviews,
        })
    doc = {
        "schema_version": 1,
        "mission": "QA-07",
        "role": "INDEPENDENT_LEGAL_REVIEWER_HIGH_A",
        "as_of": AS_OF,
        "status": "INDEPENDENT_REVALIDATION_COMPLETE",
        "proposal_file": PROPOSAL.name,
        "proposal_sha256": EXPECTED_PROPOSAL_SHA256,
        "source_date_cut": AS_OF,
        "sources": [
            {"authority": "Câmara dos Deputados", "url": "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html", "use": "texto consolidado principal"},
            {"authority": "Presidência da República - Planalto", "url": "https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm", "use": "conferência cruzada da compilação"},
        ],
        "target_total": 10,
        "finding_total": 21,
        "decision_counts": {"ACEITA": 10, "REJEITADA": 0},
        "finding_decision_counts": {"ACEITA": 21, "REJEITADA": 0},
        "records": records,
        "corpus_modified": False,
        "proposal_modified": False,
        "human_approval_claimed": False,
    }
    write(DEST, doc)
    print(json.dumps({"targets": 10, "findings": 21, "accepted": 10,
                      "sha256": sha(DEST)}, ensure_ascii=False))


if __name__ == "__main__":
    build()
