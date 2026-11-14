"""Persist QA-07 editorial proposals for high findings 22-41."""
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
QA06 = HERE / "derived/qa06_subdivision_material_audit"
CORPUS = HERE / "derived/candidate_qa06_cc_001_2046/CC2002_QA06.entenda.jsonl"
OUT = HERE / "derived/qa07_high_findings_resolution/QA07_EDITOR_HIGH_B.json"
SOURCE_URL = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
AS_OF = "2026-11-13"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(o_que_diz, o_que_significa, exemplo_pratico, atencao, termos):
    return {
        "o_que_diz": o_que_diz,
        "o_que_significa": o_que_significa,
        "exemplo_pratico": exemplo_pratico,
        "atencao": atencao,
        "palavras_dificeis": [{"termo": termo, "explicacao": explicacao}
                              for termo, explicacao in termos],
    }


PROPOSALS = {
    "CC2002:ART.1353": {
        "analysis": "A síntese anterior mencionava prazos e requisitos genericamente, mas não informava os marcos de 60 dias para a sessão seguinte e 90 dias para a conclusão total. Ambos condicionam a validade operacional da sessão permanente.",
        "risk": "Não confundir o intervalo máximo até a sessão seguinte (60 dias) com o prazo total contado da abertura inicial (90 dias).",
        "content": content(
            "Em segunda convocação, a assembleia decide pela maioria dos presentes, salvo quórum especial. Se esse quórum não for alcançado, a maioria presente pode autorizar sessão permanente: devem ser definidos data, hora e deliberações da continuação, marcada para até 60 dias; presentes e ausentes devem ser convocados; a ata parcial deve registrar os argumentos e ser enviada aos ausentes; e a ata final deve consolidar as deliberações. A sessão pode ser prorrogada, mas a assembleia inteira deve terminar em até 90 dias da abertura inicial.",
            "A reunião pode ser suspensa e retomada para completar um quórum especial, sem começar outra assembleia, desde que preserve convocação, informação, pauta, votos e documentação dentro dos dois limites de tempo.",
            "Sem quórum especial em 10 de março, a assembleia fixa a continuação para 20 de abril, identifica a pauta, convoca as unidades ausentes e envia a ata parcial. Outras retomadas são possíveis, mas a conclusão não pode ultrapassar 90 dias contados de 10 de março.",
            "Os requisitos são cumulativos. Os votos da primeira sessão permanecem registrados; quem comparecer à continuação pode alterá-los até o encerramento da deliberação.",
            [("Sessão permanente", "continuação da mesma assembleia, suspensa e retomada para concluir deliberação que exige quórum especial"), ("Quórum especial", "quantidade qualificada de votos exigida por lei ou convenção")],
        ),
    },
    "CC2002:ART.1354-A": {
        "analysis": "A redação anterior sugeria dever amplo de tratar problemas técnicos, mas não explicitava a exoneração legal por equipamentos, conexão ou outras circunstâncias fora do controle da administração.",
        "risk": "A exoneração não cobre falha da própria administração nem autoriza restringir voz, debate ou voto.",
        "content": content(
            "Assembleias condominiais podem ser eletrônicas ou híbridas se a convenção não proibir e se preservarem voz, debate e voto. A convocação deve explicar acesso, manifestação e coleta de votos. A administração não responde por falhas nos equipamentos ou na internet dos condôminos ou representantes, nem por outras situações fora de seu controle.",
            "A reunião digital é válida com participação e procedimento adequados, mas cada participante assume os problemas de sua própria estrutura tecnológica que a administração não controla.",
            "O condomínio fornece corretamente a plataforma e as instruções, mas a conexão particular de um condômino cai. Essa falha externa, por si só, não torna a administração responsável.",
            "A exclusão de responsabilidade alcança apenas situações fora do controle da administração. A ata só é lavrada após a soma e divulgação dos votos, e o edital deve disciplinar instalação, funcionamento e encerramento.",
            [("Assembleia híbrida", "assembleia com participação física e virtual simultânea"), ("Fora do controle", "circunstância que a administração não tem poder efetivo de prevenir ou corrigir")],
        ),
    },
    "CC2002:ART.1358-J": {
        "analysis": "Três comandos autônomos estavam apenas insinuados: desocupação pontual sob multa diária; sanção progressiva e perda temporária por reiteração; e distribuição das despesas de reparo conforme uso normal ou anormal.",
        "risk": "A perda temporária depende de descumprimento reiterado e de previsão na convenção; não é consequência de qualquer infração isolada.",
        "content": content(
            "O multiproprietário deve pagar contribuições mesmo sem usar, conservar e usar o imóvel conforme sua finalidade, comunicar danos, permitir reparos urgentes e responder pelos danos causados por si ou por quem autorizar. Deve desocupar até o dia e a hora convencionados, sob multa diária. A convenção deve prever multa por descumprimento e, se houver reiteração, multa progressiva e perda temporária do uso de sua fração. Reparos por uso normal e desgaste natural são custeados por todos; os causados por uso anormal cabem exclusivamente ao responsável, sem prejuízo de multa.",
            "Cada titular entrega o imóvel no horário e no estado necessários ao próximo período. O custo coletivo cobre desgaste normal; dano decorrente de uso anormal e sanções recaem sobre quem o causou, nos termos da convenção.",
            "Um titular permanece após o horário fixado e entrega o imóvel danificado por uso anormal. Pode sofrer a multa diária pela demora e arcar sozinho com o reparo; se reiterar infrações, a convenção pode aplicar multa progressiva e suspender temporariamente seu período de uso.",
            "A perda de uso é temporária e exige descumprimento reiterado. Multas e sanções devem estar previstas na convenção de multipropriedade; desgaste natural não pode ser cobrado exclusivamente de um titular.",
            [("Multa progressiva", "sanção cujo valor aumenta diante da repetição do descumprimento"), ("Uso anormal", "utilização incompatível com a finalidade ou os cuidados ordinários do imóvel")],
        ),
    },
    "CC2002:ART.1358-P": {
        "analysis": "A regra supletiva do rateio estava diluída em referência genérica a custeio proporcional, sem esclarecer que a proporção segue a fração de tempo apenas na falta de disciplina diversa.",
        "risk": "Não apresentar a proporcionalidade temporal como regra inderrogável: o instrumento de instituição ou a convenção de multipropriedade pode estabelecer forma diversa.",
        "content": content(
            "A convenção do condomínio edilício que contenha multipropriedade deve identificar unidades e períodos, disciplinar despesas, administração, sanções e quóruns, e definir como os titulares da mesma unidade rateiam as contribuições. Se o instrumento de instituição ou a convenção de multipropriedade não estabelecer outro critério, o rateio será proporcional à fração de tempo de cada titular.",
            "Os custos da unidade precisam ter regra expressa. Na ausência de escolha válida diferente, quem possui período maior suporta parcela proporcionalmente maior das contribuições.",
            "Dois titulares têm, respectivamente, uma e três semanas na mesma unidade. Sem regra diferente no instrumento ou na convenção, o segundo participa do rateio em proporção três vezes maior.",
            "A proporcionalidade à fração de tempo é regra supletiva, não obrigatória quando o instrumento de instituição ou a convenção de multipropriedade disciplina validamente outro rateio.",
            [("Rateio", "divisão de uma despesa entre os responsáveis por seu pagamento"), ("Regra supletiva", "regra aplicada quando os instrumentos permitidos não estabelecem solução diferente")],
        ),
    },
    "CC2002:ART.1358-S": {
        "analysis": "A versão anterior falava apenas em direcionamento genérico de receitas, omitindo proibição de uso até quitação e o dever automático da administradora de aplicar integralmente valores líquidos e devolver eventual saldo.",
        "risk": "As medidas do parágrafo único dependem do tipo específico de empreendimento com sistema único de locação e de previsão na convenção.",
        "content": content(
            "O inadimplemento de despesas ordinárias ou extraordinárias pode levar, pelo procedimento civil, à adjudicação da fração de tempo ao condomínio edilício. Em empreendimento com sistema único de locação, a convenção pode ainda proibir o inadimplente de usar o imóvel até quitar integralmente a dívida, inserir sua fração no conjunto administrado e atribuir à administradora poderes e dever de aplicar todos os valores líquidos devidos ao titular na amortização das dívidas dos condomínios edilício e de multipropriedade; eventual saldo deve ser repassado imediatamente ao titular.",
            "Além da possível transferência judicial da fração, certos empreendimentos de locação compartilhada podem usar o próprio período e sua renda para pagar a dívida, mas somente nas condições previstas pela lei e pela convenção.",
            "A convenção de empreendimento com locação centralizada prevê que a semana do inadimplente entre no sistema de locação. A administradora usa toda a receita líquida para quitar os débitos condominiais e transfere imediatamente ao titular o que sobrar.",
            "Proibição de uso, inclusão no sistema de locação e retenção de receitas não são automáticas para toda multipropriedade: exigem o empreendimento descrito no parágrafo único e disciplina na convenção.",
            [("Adjudicação", "transferência da fração ao credor por meio do procedimento legal para satisfação da dívida"), ("Valores líquidos", "receitas restantes após as deduções legítimas do sistema de locação")],
        ),
    },
    "CC2002:ART.1361": {
        "analysis": "Faltava a eficácia atribuída à aquisição posterior da propriedade pelo devedor, relevante quando ele ainda não era proprietário ao celebrar e arquivar a garantia fiduciária.",
        "risk": "A regra não dispensa arquivamento: a propriedade superveniente torna eficaz a transferência desde esse arquivamento.",
        "content": content(
            "Propriedade fiduciária é a propriedade resolúvel de coisa móvel infungível transferida pelo devedor ao credor para garantir dívida. Constitui-se com o registro do contrato no órgão competente e desdobra a posse, ficando o devedor como possuidor direto. Se o devedor adquirir posteriormente a propriedade do bem, essa aquisição superveniente torna eficaz a transferência fiduciária desde o arquivamento.",
            "O credor recebe titularidade limitada à garantia por meio do registro. Mesmo que a propriedade do devedor seja adquirida depois, a lei aproveita o arquivamento já realizado para dar eficácia à transferência.",
            "O devedor arquiva contrato fiduciário e depois adquire a propriedade do bem descrito. Com essa aquisição posterior, a garantia transferida ao credor torna-se eficaz desde o arquivamento.",
            "A regra trata da propriedade superveniente e não elimina os requisitos do contrato, da identificação do bem e do registro competente. Leis especiais podem reger determinadas operações.",
            [("Propriedade superveniente", "propriedade adquirida pelo devedor depois do ato ou contrato"), ("Propriedade resolúvel", "titularidade que se extingue quando ocorre a condição prevista, como a quitação")],
        ),
    },
    "CC2002:ART.1389": {
        "analysis": "A explicação reconhecia desuso prolongado, porém omitia o prazo material exato de dez anos contínuos para essa causa de extinção.",
        "risk": "Uso apenas reduzido ou interrupções inferiores ao período legal não equivalem automaticamente ao não uso contínuo por dez anos.",
        "content": content(
            "A servidão também se extingue, permitindo ao dono do imóvel serviente pedir seu cancelamento mediante prova, quando os imóveis dominante e serviente passam ao mesmo proprietário, quando as obras correspondentes são suprimidas por contrato ou outro título expresso, ou quando a servidão não é usada por dez anos contínuos.",
            "Esses fatos eliminam a utilidade ou a base jurídica da servidão, mas o cancelamento exige demonstração da causa de extinção.",
            "Uma passagem gravada como servidão deixa de ser utilizada por dez anos sem interrupção. Com a prova desse período, o dono do imóvel onerado pode requerer o cancelamento.",
            "Mero uso pouco frequente ou interrupção breve não satisfaz a hipótese de não uso por dez anos contínuos.",
            [("Imóvel serviente", "imóvel onerado pela servidão"), ("Não uso contínuo", "ausência ininterrupta de exercício da servidão durante todo o prazo legal")],
        ),
    },
    "CC2002:ART.1404": {
        "analysis": "A explicação remetia genericamente ao conceito de despesa módica, mas não apresentava o critério quantitativo legal de dois terços do rendimento líquido anual.",
        "risk": "O parâmetro compara a despesa ao rendimento líquido de um ano; não é percentual do valor do bem.",
        "content": content(
            "O proprietário suporta as reparações extraordinárias e as que não sejam de custo módico; o usufrutuário paga juros sobre o capital gasto nas obras necessárias à conservação ou que aumentem o rendimento. Não são módicas as despesas superiores a dois terços do rendimento líquido de um ano. Se o dono não fizer reparo indispensável a seu cargo, o usufrutuário pode realizá-lo e cobrar o valor gasto.",
            "A lei divide reparos de maior peso com base no custo e no benefício econômico. Uma despesa que ultrapasse dois terços do rendimento líquido anual não pode ser tratada como pequena para transferi-la ao usufrutuário.",
            "Se o imóvel rende R$ 30 mil líquidos no ano, despesa superior a R$ 20 mil não é módica. Sendo reparo extraordinário a cargo do dono e indispensável, o usufrutuário pode fazê-lo diante da omissão e exigir reembolso.",
            "O limite de dois terços qualifica a despesa como não módica; ainda é preciso considerar a natureza da reparação e as demais regras do artigo.",
            [("Rendimento líquido", "rendimento depois das despesas necessárias para sua obtenção"), ("Custo módico", "custo que não ultrapassa o limite legal de dois terços do rendimento líquido anual")],
        ),
    },
    "CC2002:ART.1487-A": {
        "analysis": "A prioridade da extensão estava coberta, mas faltava a regra de legitimidade para executar quando surgem vários credores garantidos pela mesma hipoteca estendida.",
        "risk": "A exceção exige convenção diversa de todos os credores, não apenas acordo entre alguns deles.",
        "content": content(
            "O proprietário pode estender hipoteca para novas obrigações com o mesmo credor, mantendo registro e publicidade originais, dentro do prazo e valor máximos e sem prejudicar direitos contraditórios já inscritos. A extensão deve ser averbada e respeita a preferência da obrigação inicial e, entre extensões, da obrigação mais antiga. Se depois houver vários credores garantidos pela mesma hipoteca estendida, somente o titular do crédito mais prioritário pode executar judicial ou extrajudicialmente a garantia, salvo convenção diferente de todos os credores.",
            "A hipoteca pode garantir novas dívidas sem perder sua organização registral, mas a prioridade define quem conduz a execução quando existem vários credores.",
            "Após cessão de créditos garantidos pela hipoteca estendida, três credores passam a compartilhar a garantia. Sem acordo unânime em sentido diferente, apenas o credor do crédito prioritário promove a execução.",
            "A extensão não ultrapassa o prazo nem o valor máximo da garantia original e não desloca direitos contraditórios que entraram antes na matrícula.",
            [("Averbação", "anotação posterior feita na matrícula do imóvel"), ("Crédito prioritário", "crédito que ocupa a posição preferencial segundo as regras legais e registrais")],
        ),
    },
    "CC2002:ART.1488": {
        "analysis": "A divisão do gravame estava explicada, mas faltavam duas consequências: despesas por conta do requerente, salvo ajuste, e manutenção da responsabilidade do devedor originário, salvo anuência do credor.",
        "risk": "O desmembramento distribui a garantia entre unidades, mas não libera automaticamente o devedor da responsabilidade pelo saldo referida no art. 1.430.",
        "content": content(
            "Se imóvel hipotecado for loteado ou convertido em condomínio edilício, credor, devedor ou proprietários podem pedir ao juiz a divisão da hipoteca entre lotes ou unidades, proporcionalmente a seus valores e ao crédito. O credor só se opõe provando redução da garantia. Salvo acordo diferente, quem requer o desmembramento paga as despesas judiciais e extrajudiciais. A divisão do ônus não exonera o devedor originário da responsabilidade pelo restante da dívida prevista no art. 1.430, a menos que o credor concorde.",
            "A hipoteca pode ser repartida para acompanhar as novas unidades, mas isso não transfere automaticamente os custos do procedimento nem libera o devedor original.",
            "O proprietário pede a divisão da hipoteca entre apartamentos e, sem convenção diferente, paga as despesas do procedimento. Mesmo após a divisão, o devedor original continua responsável pelo saldo não coberto, salvo anuência do credor.",
            "Desmembrar o gravame não significa perdoar dívida ou substituir devedor. A exoneração depende da anuência do credor.",
            [("Desmembramento do ônus", "divisão da hipoteca entre os lotes ou unidades resultantes"), ("Anuência", "concordância expressa da pessoa cujo direito é afetado")],
        ),
    },
    "CC2002:ART.1523": {
        "analysis": "A finalidade geral das causas suspensivas estava indicada, mas faltava o período específico de dez meses aplicável à viúva ou à mulher cujo casamento foi nulo ou anulado.",
        "risk": "O prazo é causa suspensiva, não impedimento absoluto; no inciso II, pode ser afastado com prova de nascimento de filho ou de inexistência de gravidez durante o prazo.",
        "content": content(
            "A lei recomenda adiar o casamento em quatro situações destinadas a proteger partilha, herdeiros, tutelados e segurança sobre filiação. Entre elas, a viúva ou a mulher cujo casamento foi declarado nulo ou anulado não deve casar até dez meses após o início da viuvez ou a dissolução da sociedade conjugal. O juiz pode afastar as causas dos incisos I, III e IV com prova de ausência do prejuízo indicado; na hipótese do inciso II, a nubente deve provar nascimento de filho ou inexistência de gravidez durante o prazo.",
            "São causas suspensivas: não tornam a pessoa incapaz de casar, mas recomendam espera e podem produzir consequência patrimonial se desrespeitadas. O prazo de dez meses busca esclarecer eventual filiação concebida na relação anterior.",
            "Mulher viúva há quatro meses pretende casar e comprova judicialmente que não está grávida. Essa prova pode permitir o afastamento da causa suspensiva do inciso II.",
            "O Código usa formulação ligada ao casamento da mulher. A dispensa do inciso II exige a prova específica prevista no parágrafo único, diferente da prova de ausência de prejuízo exigida nas demais hipóteses.",
            [("Causa suspensiva", "situação que recomenda adiar o casamento, sem constituir impedimento matrimonial absoluto"), ("Nubente", "pessoa que pretende se casar")],
        ),
    },
    "CC2002:ART.1541": {
        "analysis": "A versão anterior descrevia apenas a confirmação judicial ordinária e omitia a via alternativa quando o enfermo recupera a saúde e pode ratificar o casamento.",
        "risk": "A dispensa depende de ratificação perante, conjuntamente, a autoridade competente e o oficial do registro.",
        "content": content(
            "No casamento celebrado em perigo de vida sem a autoridade, as testemunhas devem procurar o juiz em dez dias e declarar convocação, lucidez, perigo e consentimento; seguem diligências, decisão e registro, cujos efeitos sobre o estado dos cônjuges retroagem à celebração. Essas formalidades e as do artigo anterior são dispensadas se o enfermo convalescer e puder ratificar o casamento na presença da autoridade competente e do oficial do registro.",
            "A lei oferece duas formas de confirmação: procedimento judicial apoiado nas testemunhas ou, havendo recuperação, ratificação pessoal e formal do casamento pelo próprio enfermo.",
            "Após casamento emergencial, o enfermo se recupera antes da confirmação judicial. Ele comparece perante a autoridade competente e o oficial do registro e ratifica o casamento, dispensando as formalidades emergenciais indicadas.",
            "Convalescer não basta sozinho: é necessário que o enfermo possa ratificar o casamento perante as duas autoridades mencionadas pela lei.",
            [("Convalescer", "recuperar-se da enfermidade ou do perigo de vida"), ("Ratificar", "confirmar formalmente um ato anteriormente praticado")],
        ),
    },
    "CC2002:ART.1735": {
        "analysis": "A referência genérica a condenação relevante não informava o rol legal nem que o impedimento permanece mesmo após o cumprimento da pena.",
        "risk": "Preservar a expressão legal histórica 'crimes contra os costumes' sem transformá-la em afirmação sobre a classificação penal atual; a incidência concreta pode exigir enquadramento jurídico.",
        "content": content(
            "Não podem exercer tutela — e devem ser exonerados se já a exercem — quem não administra livremente seus bens, tem conflito relevante com o menor, é inimigo dele ou de seus pais, foi excluído por estes, apresenta conduta ou probidade incompatível, abusou de tutela anterior ou exerce função pública incompatível. Também são impedidos os condenados por furto, roubo, estelionato, falsidade, crime contra a família ou pelos crimes designados no Código Civil como 'contra os costumes', tenham ou não cumprido a pena.",
            "A tutela exige capacidade, ausência de conflito e idoneidade. Nas condenações expressamente listadas, terminar de cumprir a pena não remove, por si só, o impedimento civil para ser tutor.",
            "Pessoa condenada por estelionato não pode assumir tutela mesmo depois de cumprir integralmente a pena, pois o artigo mantém o impedimento nessa situação.",
            "A expressão 'crimes contra os costumes' é a terminologia literal e histórica do Código Civil; a correspondência com tipos penais atuais deve ser examinada juridicamente no caso concreto.",
            [("Exoneração", "retirada da pessoa do encargo que já exercia"), ("Probidade", "honestidade e correção necessárias ao exercício da tutela")],
        ),
    },
    "CC2002:ART.1800": {
        "analysis": "A existência de curador estava coberta, porém faltava o regime jurídico que define seus poderes, deveres e responsabilidades.",
        "risk": "As regras da curatela dos incapazes aplicam-se somente no que forem compatíveis com esta curadoria sucessória.",
        "content": content(
            "Quando o testamento beneficia filho ainda não concebido de pessoa indicada, os bens, depois da liquidação ou partilha, ficam com curador nomeado pelo juiz. Salvo disposição diferente, a curatela cabe primeiro à pessoa cujo filho era esperado. Os poderes, deveres e responsabilidades desse curador seguem, no que forem compatíveis, as regras da curatela dos incapazes. Se o herdeiro nascer com vida, recebe a sucessão e os frutos desde a morte do testador; se não for concebido em dois anos, os bens passam aos herdeiros legítimos, salvo disposição testamentária em contrário.",
            "O curador apenas conserva e administra os bens durante a espera, submetido a deveres e responsabilidades equivalentes aos da curatela de incapaz quando compatíveis; não se torna proprietário do patrimônio.",
            "O juiz entrega ao curador os bens reservados ao futuro filho de determinada pessoa. O curador deve administrá-los e responder por sua gestão segundo as regras compatíveis da curatela dos incapazes.",
            "A aplicação das regras de curatela é adaptada pela expressão 'no que couber'. O nascimento com vida ou o fim do prazo legal altera a destinação dos bens.",
            [("Prole eventual", "filho que a pessoa indicada poderá conceber no futuro"), ("No que couber", "somente na medida em que a regra seja compatível com a situação")],
        ),
    },
    "CC2002:ART.1817": {
        "analysis": "A versão anterior protegia terceiros e mencionava indenização aos herdeiros, mas omitia a prestação de contas econômica específica imposta ao excluído.",
        "risk": "Distinguir restituição de frutos e rendimentos, obrigatória, do direito do excluído ao reembolso das despesas de conservação.",
        "content": content(
            "Alienações onerosas a terceiros de boa-fé e atos de administração legal praticados antes da sentença de exclusão permanecem válidos, sem impedir perdas e danos aos herdeiros prejudicados. O excluído deve restituir os frutos e rendimentos que recebeu dos bens hereditários, mas tem direito à indenização pelas despesas feitas para conservá-los.",
            "A lei protege terceiros de boa-fé e, ao mesmo tempo, recompõe o patrimônio sucessório: o excluído devolve os ganhos obtidos, mas não suporta gratuitamente os gastos necessários de conservação.",
            "Antes da exclusão, o herdeiro recebe aluguéis do imóvel da herança e paga reparo indispensável. Depois da sentença, restitui os aluguéis, mas pode exigir indenização pela despesa de conservação.",
            "A proteção do negócio exige terceiro de boa-fé e alienação onerosa. A restituição dos rendimentos não elimina o direito de reembolso das despesas conservatórias.",
            [("Frutos e rendimentos", "utilidades econômicas produzidas pelo bem, como aluguéis"), ("Despesa de conservação", "gasto necessário para preservar o bem e evitar sua deterioração")],
        ),
    },
}


def main():
    queue_path = QA06 / "QA06_B_DEFINITIVE_CORRECTION_QUEUE.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    high = [row for row in queue["findings"] if row["final_severity"] == "ALTO"][21:]
    rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines()]
    active = {row["target_id"]: row for row in rows if row["status"] == "ACTIVE"}
    grouped = {}
    for finding in high:
        grouped.setdefault(finding["target_id"], []).append(finding)
    if set(grouped) != set(PROPOSALS) or len(high) != 20:
        raise RuntimeError("assigned finding scope changed")
    records = []
    for target_id, findings in grouped.items():
        proposal = PROPOSALS[target_id]
        records.append({
            "target_id": target_id,
            "finding_ids": [row["finding_id"] for row in findings],
            "subdivision_ids": [row["subdivision_id"] for row in findings],
            "decision": "CORRECAO_NECESSARIA",
            "analysis": proposal["analysis"],
            "risk": proposal["risk"],
            "previous_explanation_id": active[target_id]["explanation_id"],
            "previous_content": active[target_id]["content"],
            "proposed_content": proposal["content"],
            "source": {"url": SOURCE_URL, "as_of": AS_OF,
                       "inventory_sha256": "7fe41b6b6e7755e17174551b56ea684fbbd8a399e95641f7f47e729f55ef5c82",
                       "legal_text_sha256": [hashlib.sha256(row["finding"]["legal_text"].encode("utf-8")).hexdigest()
                                             for row in findings]},
            "human_approval_claimed": False,
            "independent_revalidation_status": "PENDING",
        })
    doc = {
        "schema_version": 1, "mission": "QA-07", "role": "EDITOR",
        "assignment": "HIGH_FINDINGS_22_41", "as_of": AS_OF,
        "source_queue": queue_path.name, "source_queue_sha256": sha(queue_path),
        "baseline_corpus_sha256": sha(CORPUS),
        "finding_total": len(high), "target_total": len(records),
        "decision_counts": {"CORRECAO_NECESSARIA": len(high)},
        "records": records, "human_approval_claimed": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"file": str(OUT), "findings": len(high), "targets": len(records),
                      "sha256": sha(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
