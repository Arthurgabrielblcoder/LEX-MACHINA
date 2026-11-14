"""Independent legal review of the ten QA-07 indeterminate decisions."""
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "derived/qa07_high_findings_resolution"
SOURCE = OUT / "QA07_INDETERMINATE_DECISIONS.json"
DEST = OUT / "QA07_REVIEW_INDETERMINATE.json"
EXPECTED = "1af16bece49b103723ad81b98be93049923619d2cd140c0890e6d0837acf588b"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


REVIEWS = {
    "QA06-FINAL-0092": {
        "norm_check": "O art. 964, IV, vincula a preferência ao imóvel, fábrica, oficina ou construção que recebeu materiais, dinheiro ou serviços para edificação, reconstrução ou melhoramento.",
        "assessment": "A versão anterior enunciava construção apenas como categoria e omitia a contribuição protegida e o bem sobre o qual recai a preferência. A proposta inclui ambos sem transformar o campo em transcrição.",
    },
    "QA06-FINAL-0095": {
        "norm_check": "O art. 968, II, separa a firma da assinatura autógrafa, admite substituição por assinatura autenticada com certificação digital ou meio equivalente e ressalva a LC 123/2006.",
        "assessment": "A proposta desfaz a expressão imprecisa 'firma autenticada', explica a alternativa eletrônica e preserva o regime simplificado da lei complementar sem ampliar dispensa específica.",
    },
    "QA06-FINAL-0148": {
        "norm_check": "O art. 1.071, VIII, ainda diz 'pedido de concordata'. A Lei 11.101/2005 disciplina recuperação e falência e, no art. 192, conserva o regime anterior apenas para processos já ajuizados, admitindo a transição ali prevista.",
        "assessment": "A referência pedagógica a recuperação exprime o instituto atual submetido à deliberação societária e não afirma identidade técnico-processual com a antiga concordata. A palavra histórica isolada reduziria a utilidade atual. Mantém-se a ressalva de que se trata de equivalência funcional e intertemporal, não lexical.",
    },
    "QA06-FINAL-0154": {
        "norm_check": "O caput do art. 1.076 é introdutório e só se completa pelos incisos, além de ressalvar o art. 1.061. O inciso I está revogado e os quóruns vigentes decorrem da Lei 14.451/2022.",
        "assessment": "Os cinco campos já registram a ressalva e os dois regimes de quórum vigentes. A indicação de cobertura suficiente corrige adequadamente o falso positivo causado pela segmentação do caput.",
    },
    "QA06-FINAL-0158": {
        "norm_check": "O art. 1.078, § 2º, exige leitura, discussão e votação dos documentos e impede administradores e membros do conselho fiscal de participar dessa votação.",
        "assessment": "A proposta incorpora a sequência deliberativa e o impedimento de voto, com exemplo correto e sem estender a vedação a outras deliberações.",
    },
    "QA06-FINAL-0181": {
        "norm_check": "O art. 1.134, § 1º, III, exige relação de membros de todos os órgãos da administração, dados pessoais e valor da participação, exceto quanto a ações ao portador.",
        "assessment": "A proposta cobre integralmente os requisitos e limita corretamente a exceção ao valor da participação. A nota sobre ações ao portador evita apresentar a terminologia histórica como prática societária atual.",
    },
    "QA06-FINAL-0278": {
        "norm_check": "O art. 1.301 fixa 1,5 m no caput e 75 cm, no § 1º, para janelas sem visão incidente sobre a linha divisória e para as perpendiculares.",
        "assessment": "A proposta distingue os limites e preserva a exceção das pequenas aberturas do § 2º. O exemplo não converte o limite de 75 cm em autorização incondicionada para qualquer janela.",
    },
    "QA06-FINAL-0304": {
        "norm_check": "O art. 1.334, § 2º, equipara promitentes compradores e cessionários de direitos aos proprietários somente para os fins do artigo e salvo disposição em contrário.",
        "assessment": "A proposta contém os dois limitadores e não generaliza a equiparação para aquisição da propriedade ou outros efeitos jurídicos.",
    },
    "QA06-FINAL-0336": {
        "norm_check": "O art. 1.358-G, V, exige que a convenção trate da perda ou destruição parcial ou total, inclusive risco, seguro, indenização e parte restante.",
        "assessment": "A proposta cobre todos os efeitos patrimoniais essenciais e os distingue da disciplina ordinária de manutenção e danos de uso.",
    },
    "QA06-FINAL-0362": {
        "norm_check": "O art. 1.358-P, VI, exige indicação do sistema de intercâmbio, quando existente, e limita responsabilidade e obrigações da companhia ao documento contratual. O art. 23, § 2º, da Lei 11.771/2008 define a administração de intercâmbio.",
        "assessment": "A proposta preserva a condicionalidade, admite troca de período ou local e não atribui à companhia obrigações além da contratação.",
    },
}


def build():
    if sha(SOURCE) != EXPECTED:
        raise RuntimeError("indeterminate decision module hash mismatch")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(source["records"]) != 10 or set(REVIEWS) != {r["finding_id"] for r in source["records"]}:
        raise RuntimeError("indeterminate review scope mismatch")
    common_sources = [
        {"authority": "Câmara dos Deputados", "url": "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html", "use": "Código Civil vigente"},
        {"authority": "Planalto", "url": "https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2005/lei/l11101.htm", "use": "regime recuperacional e transição da concordata"},
        {"authority": "Planalto", "url": "https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11771compilado.htm", "use": "administração de intercâmbio"},
        {"authority": "Planalto", "url": "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm", "use": "simplificação registral"},
    ]
    records = []
    for row in source["records"]:
        review = REVIEWS[row["finding_id"]]
        proposed = row.get("proposed_content")
        records.append({
            "finding_id": row["finding_id"], "target_id": row["target_id"],
            "subdivision_id": row["subdivision_id"], "reviewed_decision": row["decision"],
            "review_decision": "ACEITA", "norm_check": review["norm_check"],
            "independent_assessment": review["assessment"],
            "five_fields_reviewed": True,
            "proposal_assessment": "ACCEPTED_NO_NEW_LEGAL_ERROR" if proposed else "NOT_APPLICABLE_COVERAGE_SUFFICIENT",
            "finding_resolved_by_decision": True, "objections": [],
        })
    document = {
        "schema_version": 1, "mission": "QA-07", "role": "INDEPENDENT_LEGAL_REVIEWER",
        "as_of": "2026-11-14", "status": "INDETERMINATE_DECISIONS_INDEPENDENTLY_REVALIDATED",
        "source_module": SOURCE.name, "source_module_sha256": EXPECTED,
        "source_date_cut": "2026-11-14", "total": 10,
        "review_decision_counts": {"ACEITA": 10, "REJEITADA": 0},
        "reviewed_result_counts": {"CONFIRMADO_PARA_CORRECAO": 8, "COBERTURA_MATERIAL_SUFICIENTE": 2},
        "sources": common_sources, "records": records,
        "corpus_modified": False, "human_approval_claimed": False,
    }
    DEST.write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8", newline="\n")
    print(json.dumps({"total": 10, "accepted": 10, "rejected": 0, "sha256": sha(DEST)}, ensure_ascii=False))


if __name__ == "__main__":
    build()
