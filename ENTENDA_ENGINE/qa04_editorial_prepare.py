"""Prepare the four QA-04 editorial corrections without claiming independent approval."""
import json

import qa04_prepare as prep


PROPOSALS = {
    "CC2002:ART.228": {
        "o_que_diz": "Em regra, não são admitidos como testemunhas o menor de dezesseis anos, o interessado no litígio, o amigo íntimo ou inimigo capital e, em relação a qualquer das partes, seu cônjuge, ascendentes, descendentes e parentes colaterais até o terceiro grau, tanto por consanguinidade quanto por afinidade. O juiz pode ouvir essas pessoas sobre fatos conhecidos somente por elas. A pessoa com deficiência testemunha em igualdade de condições e com os recursos assistivos necessários.",
        "o_que_significa": "A regra identifica situações que podem comprometer a independência do depoimento, mas não cria exclusão absoluta: a necessidade da prova pode justificar a oitiva. Os incisos II e III estão revogados, e deficiência não constitui impedimento para testemunhar.",
        "exemplo_pratico": "O cunhado de uma das partes, parente por afinidade, é alcançado pela restrição; se apenas ele presenciou o fato, o juiz pode admitir seu depoimento.",
        "atencao": "É preciso distinguir parentesco por sangue de parentesco por afinidade e observar o limite do terceiro grau para colaterais. A exceção probatória não elimina a avaliação judicial da credibilidade.",
        "palavras_dificeis": [{"termo": "Afinidade", "explicacao": "vínculo familiar formado pelo casamento ou união com os parentes do cônjuge ou companheiro"}],
    },
    "CC2002:ART.288": {
        "o_que_diz": "Para que a cessão de crédito produza efeitos contra terceiros, ela deve constar de instrumento público ou de documento particular com as formalidades remetidas pelo art. 654, § 1º: lugar de celebração, identificação das partes, data, finalidade do ato e indicação do objeto e da extensão dos poderes ou efeitos conferidos.",
        "o_que_significa": "A exigência protege terceiros ao tornar a transmissão documentalmente verificável. A falta dessa forma qualificada impede opor a cessão a terceiros, mas não torna, por si só, inválido o acordo existente entre cedente e cessionário.",
        "exemplo_pratico": "Cedente e cessionário celebram cessão sem documento apto a identificar data, partes e objeto. O ajuste pode vinculá-los, mas não prevalece automaticamente contra terceiro que dispute o mesmo crédito.",
        "atencao": "Eficácia perante terceiros e validade entre as partes são questões diferentes. Além da forma do art. 288, devem ser verificadas as demais regras da cessão e a situação concreta do terceiro.",
        "palavras_dificeis": [{"termo": "Eficácia perante terceiros", "explicacao": "possibilidade de fazer o negócio produzir efeitos contra pessoas que não participaram dele"}],
    },
    "CC2002:ART.371": {
        "o_que_diz": "Em regra, o devedor só pode compensar o que o próprio credor lhe deve. Na fiança há exceção: o fiador cobrado pode usar, para reduzir ou extinguir a dívida garantida, o crédito que o afiançado possui contra esse mesmo credor.",
        "o_que_significa": "A reciprocidade normalmente é examinada entre as mesmas duas pessoas. Para proteger o garante, a lei permite que ele invoque também um crédito pertencente ao devedor principal contra o credor da obrigação garantida.",
        "exemplo_pratico": "Um banco cobra do fiador dívida de uma empresa, mas deve à própria empresa uma quantia líquida e vencida. O fiador pode opor esse crédito da empresa ao banco, observados os demais requisitos da compensação.",
        "atencao": "A exceção não se limita a crédito próprio do fiador: o crédito relevante pode pertencer ao afiançado. A compensação ainda depende dos requisitos legais aplicáveis às dívidas confrontadas.",
        "palavras_dificeis": [{"termo": "Afiançado", "explicacao": "devedor principal cuja obrigação foi garantida pelo fiador"}],
    },
    "CC2002:ART.500": {
        "o_que_diz": "Na venda de imóvel por medida, se faltar área, o comprador deve primeiro pedir o complemento. Apenas quando completar a área for impossível poderá escolher entre desfazer o contrato e obter redução proporcional do preço. Diferença de até um vigésimo presume indicação aproximada, salvo prova do comprador. Se houver área excedente e o vendedor demonstrar motivo justificável para desconhecer a medida exata, o comprador escolhe entre pagar a diferença correspondente ou devolver o excesso. Na venda de coisa certa, com dimensões apenas informativas, não há complemento nem devolução.",
        "o_que_significa": "As soluções não são alternativas livres desde o início. A falta de área dá prioridade ao complemento; resolução ou abatimento são subsidiários. No excesso, a escolha é do comprador e somente surge depois da prova exigida do vendedor.",
        "exemplo_pratico": "Um lote vendido por metro quadrado tem área menor que a contratada. O comprador busca primeiro completar a metragem; se isso for inviável, poderá resolver a compra ou pedir abatimento. Se a área for maior e o vendedor provar desconhecimento justificável, quem escolhe pagar ou devolver o excedente é o comprador.",
        "atencao": "Devem ser apurados o modo da venda, a proporção da divergência, a possibilidade de complemento e, no excesso, a prova do vendedor. A presunção de diferença até cinco por cento admite prova contrária do comprador.",
        "palavras_dificeis": [{"termo": "Venda ad corpus", "explicacao": "venda do imóvel como bem certo, em que a medida indicada tem caráter apenas informativo"}],
    },
}


def main():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")
    inventory = json.loads((prep.OUT / "QA04_CORRECTION_INVENTORY_4.json").read_text(encoding="utf-8"))
    corpus = [json.loads(line) for line in prep.CORPUS.read_text(encoding="utf-8").splitlines() if line]
    active = {row["target_id"]: row for row in corpus if row["status"] == "ACTIVE"}
    records = []
    for finding in inventory["findings"]:
        target = finding["target_id"]
        old = active[target]
        proposed = PROPOSALS[target]
        changed = [field for field in prep.FIELDS if proposed[field] != old["content"][field]]
        records.append({
            "target_id": target,
            "severity": finding["severity"],
            "source_finding": finding,
            "source_finding_sha256": prep.json_sha(finding),
            "finding_confirmed": True,
            "finding_confirmation_rationale": finding["legal_basis"],
            "baseline_explanation_id": old["explanation_id"],
            "baseline_content_sha256": prep.json_sha(old["content"]),
            "proposed_content": proposed,
            "changed_fields": changed,
            "official_sources": [{"url": finding["source_url"], "accessed_on": prep.AS_OF}],
            "correction_status": "PROPOSED_PENDING_INDEPENDENT_REVALIDATION",
            "editor_identifier": "qa04_primary_editor",
            "independent_approval_claimed": False,
        })
    document = {
        "schema_version": 1, "mission": "QA-04-FRONT-A", "as_of": prep.AS_OF,
        "status": "PROPOSED_PENDING_INDEPENDENT_REVALIDATION", "total": 4,
        "source_inventory": "QA04_CORRECTION_INVENTORY_4.json", "records": records,
    }
    prep.write_json(prep.OUT / "QA04_EDITORIAL_CORRECTIONS_4.json", document)
    print(json.dumps({"proposals": 4, "targets": list(PROPOSALS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
