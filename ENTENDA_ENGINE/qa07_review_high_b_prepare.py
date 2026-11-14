"""Persist the independent legal review of QA-07 editor module HIGH_B."""
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "derived/qa07_high_findings_resolution"
PROPOSAL = OUT / "QA07_EDITOR_HIGH_B.json"
REVIEW = OUT / "QA07_REVIEW_HIGH_B.json"
EXPECTED = "f831b49744570d1ed79bd11c18c9c614abe4e4d33ac01a244c43a6c60a6c342e"
SOURCE = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sha(PROPOSAL) != EXPECTED:
        raise RuntimeError("editor HIGH_B proposal hash mismatch")
    proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    analyses = {
        "CC2002:ART.1353": ("ACEITA", "A proposta explicita corretamente os limites de 60 dias para a sessão em seguimento e de 90 dias para a conclusão integral, preservando convocação, ata parcial, continuidade e alteração de voto até o desfecho."),
        "CC2002:ART.1354-A": ("ACEITA", "O texto limita corretamente a exoneração a equipamentos, conexão e circunstâncias fora do controle da administração, sem afastar os deveres procedimentais que permanecem sob seu domínio."),
        "CC2002:ART.1358-J": ("REJEITADA", "A correção cobre desocupação, sanção progressiva e rateio de reparos, mas a frase de atenção afirma genericamente que multas e sanções devem estar previstas na convenção. O inciso VIII submete a multa diária ao instrumento pertinente, que pode ser o instrumento de instituição ou a convenção; somente as sanções do § 1º têm previsão obrigatória na convenção."),
        "CC2002:ART.1358-P": ("ACEITA", "A regra supletiva foi corretamente apresentada: o rateio proporcional à fração de tempo cede diante de disciplina válida diversa no instrumento de instituição ou na convenção de multipropriedade."),
        "CC2002:ART.1358-S": ("REJEITADA", "A proposta usa apenas a expressão indefinida 'sistema único de locação'. O parágrafo único exige empreendimento em que titulares possam ou sejam obrigados a locar suas frações exclusivamente por administração única, com repartição de receitas independentemente da ocupação efetiva. Sem explicitar esse conjunto, a explicação pode estender proibição de uso e retenção de receitas a empreendimento não abrangido."),
        "CC2002:ART.1361": ("ACEITA", "A eficácia retroativa ao arquivamento, condicionada à aquisição superveniente da propriedade pelo devedor, foi incorporada sem afastar contrato, identificação, registro e regimes especiais."),
        "CC2002:ART.1389": ("ACEITA", "O prazo de dez anos contínuos de não uso foi incluído corretamente e distinguido de uso esporádico ou interrupção breve."),
        "CC2002:ART.1404": ("ACEITA", "O critério legal de despesa superior a dois terços do rendimento líquido anual foi traduzido corretamente, inclusive no exemplo numérico, sem confundi-lo com a natureza extraordinária da reparação."),
        "CC2002:ART.1487-A": ("ACEITA", "A legitimidade exclusiva do credor do crédito prioritário para executar, ressalvada convenção diversa de todos os credores, foi corretamente integrada com limites, averbação e prioridades da extensão."),
        "CC2002:ART.1488": ("ACEITA", "A proposta atribui corretamente despesas ao requerente salvo convenção em contrário e preserva a responsabilidade do devedor originário referida no art. 1.430 salvo anuência do credor."),
        "CC2002:ART.1523": ("ACEITA", "O período de dez meses e a prova especial de nascimento ou inexistência de gravidez foram corretamente separados das provas de ausência de prejuízo dos incisos I, III e IV."),
        "CC2002:ART.1541": ("ACEITA", "A via de ratificação após convalescença foi corretamente distinguida da confirmação judicial por testemunhas e exige presença da autoridade competente e do oficial do registro."),
        "CC2002:ART.1735": ("ACEITA", "O rol do inciso IV e a permanência do impedimento após o cumprimento da pena foram fielmente expostos. A ressalva terminológica evita converter automaticamente a expressão histórica 'contra os costumes' em tipos penais atuais sem análise concreta."),
        "CC2002:ART.1800": ("ACEITA", "A aplicação, no que couber, das regras da curatela dos incapazes aos poderes, deveres e responsabilidades do curador foi explicada sem atribuir-lhe propriedade dos bens."),
        "CC2002:ART.1817": ("ACEITA", "A restituição de frutos e rendimentos e o direito à indenização por despesas de conservação foram corretamente conciliados com a proteção anterior dos terceiros de boa-fé."),
    }
    records = []
    for row in proposal["records"]:
        decision, analysis = analyses[row["target_id"]]
        objections = []
        if row["target_id"] == "CC2002:ART.1358-J":
            objections.append({
                "code": "DAILY_FINE_SOURCE_OVERGENERALIZED",
                "required_revision": "Distinguir a multa diária do inciso VIII, conforme o instrumento pertinente, das sanções do § 1º, cuja previsão deve constar da convenção.",
            })
        if row["target_id"] == "CC2002:ART.1358-S":
            objections.append({
                "code": "SPECIAL_RENTAL_SYSTEM_GATE_INCOMPLETE",
                "required_revision": "Explicitar cumulativamente locação exclusiva por administração única e partilha de receitas independentemente da ocupação efetiva, sem generalizar o regime a qualquer locação centralizada.",
            })
        records.append({
            "target_id": row["target_id"], "finding_ids": row["finding_ids"],
            "subdivision_ids": row["subdivision_ids"], "decision": decision,
            "legal_analysis": analysis, "objections": objections,
            "five_fields_reviewed": True,
            "affected_subdivisions_covered": decision == "ACEITA",
            "new_legal_error_detected": bool(objections),
            "legislation_special_check": "Verificada quando pertinente; nenhuma fonte especial altera o comando literal auditado.",
            "binding_precedent_check": "Nenhum precedente vinculante necessário para alterar o comando legal literal examinado.",
            "source": SOURCE, "source_cutoff": "2026-11-14",
        })
    doc = {
        "schema_version": 1, "mission": "QA-07", "role": "INDEPENDENT_LEGAL_REVIEWER",
        "assignment": "HIGH_FINDINGS_22_41", "as_of": "2026-11-14",
        "status": "COMPLETE_WITH_OBJECTIONS", "proposal_file": PROPOSAL.name,
        "proposal_sha256": EXPECTED, "finding_total": sum(len(r["finding_ids"]) for r in records),
        "target_total": len(records), "decision_counts": {
            "ACEITA": sum(r["decision"] == "ACEITA" for r in records),
            "REJEITADA": sum(r["decision"] == "REJEITADA" for r in records),
        },
        "sources": [
            {"authority": "Câmara dos Deputados", "url": SOURCE, "checked_on": "2026-11-14"},
            {"authority": "Câmara dos Deputados", "url": "https://www2.camara.leg.br/legin/fed/lei/2018/lei-13777-20-dezembro-2018-787502-publicacaooriginal-157049-pl.html", "scope": "multipropriedade"},
            {"authority": "Câmara dos Deputados", "url": "https://www2.camara.leg.br/legin/fed/lei/2023/lei-14711-30-outubro-2023-794873-publicacaooriginal-169906-pl.html", "scope": "extensão hipotecária"},
        ],
        "records": records, "corpus_modified": False,
        "proposal_modified": False, "human_approval_claimed": False,
    }
    REVIEW.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"targets": len(records), "findings": doc["finding_total"],
                      "decisions": doc["decision_counts"], "sha256": sha(REVIEW)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
