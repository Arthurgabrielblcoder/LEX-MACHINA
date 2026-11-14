"""Prepare editor proposals for QA-07 high findings, deterministic group A."""
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
QA06 = HERE / "derived/qa06_subdivision_material_audit"
OUT = HERE / "derived/qa07_high_findings_resolution"
QUEUE = QA06 / "QA06_B_DEFINITIVE_CORRECTION_QUEUE.json"
INVENTORY = QA06 / "QA06_SUBDIVISION_INVENTORY_V2_CORRECTED.json"
CORPUS = HERE / "derived/candidate_qa06_cc_001_2046/CC2002_QA06.entenda.jsonl"
DEST = OUT / "QA07_EDITOR_HIGH_A.json"
AS_OF = "2026-11-13"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


PROPOSALS = {
    "CC2002:ART.39": {
        "o_que_diz": "Quem retorna dentro dos dez anos posteriores à sucessão definitiva recebe os bens ainda existentes, os que os substituíram ou o preço obtido com alienações. Se ninguém regressar nem promover a sucessão definitiva nesse período, os bens arrecadados passam ao Município ou ao Distrito Federal da respectiva localização; se estiverem em território federal, passam à União.",
        "o_que_significa": "O retorno tardio não recompõe todo o patrimônio como antes. Encerrado o prazo sem retorno nem iniciativa sucessória, a localização dos bens define qual ente público os recebe.",
        "exemplo_pratico": "Se o imóvel arrecadado estiver em um município e ninguém regressar ou promover a sucessão definitiva durante os dez anos, ele passa ao domínio municipal; em território federal, o destinatário seria a União.",
        "atencao": "O direito de retorno previsto no caput alcança especificamente o ausente, seus descendentes e seus ascendentes. A destinação pública do parágrafo único não é genérica: depende da circunscrição onde o bem está situado.",
        "palavras_dificeis": [{"termo": "sub-rogação", "explicacao": "substituição de um bem por outro que assume sua posição jurídica"}, {"termo": "circunscrição", "explicacao": "área territorial de atuação do Município ou do Distrito Federal"}],
    },
    "CC2002:ART.44": {
        "o_que_diz": "São pessoas jurídicas privadas as associações, sociedades, fundações, organizações religiosas, partidos políticos e empreendimentos de economia solidária. Organizações religiosas têm liberdade de criação, organização interna e funcionamento, e o poder público não pode negar o reconhecimento nem o registro dos atos necessários à sua constituição e atividade.",
        "o_que_significa": "Cada espécie de entidade possui regime próprio. No caso das organizações religiosas, a autonomia institucional também protege contra recusa estatal indevida de reconhecimento ou registro.",
        "exemplo_pratico": "Uma organização religiosa apresenta seus atos constitutivos regulares ao registro competente; o órgão público não pode recusá-los simplesmente por discordar de sua organização interna ou de sua orientação religiosa.",
        "atencao": "A liberdade não elimina exigências legais gerais aplicáveis ao registro. A proibição é de negar reconhecimento ou registro por motivo incompatível com a autonomia assegurada pelo Código.",
        "palavras_dificeis": [{"termo": "atos constitutivos", "explicacao": "documentos que criam a entidade e definem sua organização básica"}, {"termo": "subsidiariamente", "explicacao": "de forma complementar, quando a disciplina principal não resolve o ponto"}],
    },
    "CC2002:ART.206": {
        "o_que_diz": "O artigo estabelece prazos prescricionais especiais de um, dois, três, quatro e cinco anos e dá marcos iniciais próprios a várias pretensões. Em um ano entram, entre outras, a cobrança contra peritos pela avaliação de bens aportados ao capital de sociedade anônima, desde a publicação da ata que aprovou o laudo, e a pretensão de credores não pagos contra sócios, acionistas e liquidantes, desde a publicação da ata de encerramento da liquidação. Em três anos estão a restituição de lucros ou dividendos recebidos de má-fé, contada da deliberação da distribuição; responsabilidades de fundadores, administradores, fiscais e liquidantes, com os marcos societários indicados no inciso; pagamento de título de crédito desde o vencimento, salvo lei especial; e pretensões do beneficiário contra o segurador e do terceiro prejudicado no seguro obrigatório de responsabilidade civil. Em cinco anos prescrevem os honorários de profissionais liberais, procuradores judiciais, curadores e professores, desde a conclusão do serviço ou a cessação do contrato ou mandato.",
        "o_que_significa": "Não basta saber a duração do prazo: é preciso identificar exatamente a pretensão e o evento que inicia a contagem. Nas responsabilidades societárias trienais, o marco muda conforme o responsável: publicação dos atos constitutivos para fundadores; apresentação do balanço ou reunião que deva conhecer a violação para administradores e fiscais; e primeira assembleia semestral posterior à violação para liquidantes.",
        "exemplo_pratico": "A pretensão para cobrar um título de crédito, quando não houver prazo diferente em lei especial, conta três anos do vencimento. Já os honorários de um procurador seguem prazo de cinco anos contado da conclusão do serviço ou do fim do contrato ou mandato, conforme o caso.",
        "atencao": "Qualificação da pretensão, termo inicial e eventual lei especial devem ser verificados juntos. O antigo inciso de seguro do § 1º foi revogado pela Lei 15.040/2024; isso não elimina a regra trienal do § 3º, IX, para o beneficiário e o terceiro prejudicado em seguro obrigatório de responsabilidade civil.",
        "palavras_dificeis": [{"termo": "prescrição", "explicacao": "perda da possibilidade de exigir judicialmente uma pretensão após o prazo legal"}, {"termo": "termo inicial", "explicacao": "fato ou data a partir do qual o prazo começa a correr"}, {"termo": "liquidante", "explicacao": "responsável por conduzir a liquidação e o encerramento da sociedade"}],
    },
    "CC2002:ART.1069": {
        "o_que_diz": "O conselho fiscal examina, ao menos trimestralmente, livros, documentos, caixa e carteira da sociedade, e administradores ou liquidantes devem fornecer as informações solicitadas. Registra conclusões, denuncia irregularidades, opina sobre demonstrações e operações e apresenta à assembleia anual parecer lançado no mesmo livro, baseado no balanço patrimonial e no balanço de resultado econômico. Também pode convocar assembleia nas hipóteses legais, e suas funções continuam durante a liquidação.",
        "o_que_significa": "A fiscalização é periódica, documentada e informada. O conselho não atua apenas diante de suspeita: deve examinar dados regularmente e prestar contas aos sócios na assembleia anual com base nos dois balanços exigidos.",
        "exemplo_pratico": "A cada trimestre, o conselho consulta livros e caixa e pede documentos aos administradores. Ao final do exercício, registra e apresenta à assembleia anual parecer apoiado nos balanços patrimonial e de resultado econômico.",
        "atencao": "A periodicidade trimestral é mínima. Administradores e liquidantes têm dever de informação, e o parecer anual deve ser registrado no mesmo livro usado para as conclusões do conselho.",
        "palavras_dificeis": [{"termo": "parecer fiscal", "explicacao": "manifestação fundamentada do conselho fiscal sobre negócios, operações e demonstrações da sociedade"}, {"termo": "balanço patrimonial", "explicacao": "demonstração da posição de bens, direitos e obrigações da sociedade"}],
    },
    "CC2002:ART.1187": {
        "o_que_diz": "O balanço deve avaliar bens e direitos por critérios prudentes: bens de exploração pelo custo com depreciação; estoques e itens destinados à alienação pelo custo ou pelo preço corrente quando este for menor; títulos e créditos segundo os critérios legais; e certas despesas por amortização. Se bens forem avaliados pelo preço corrente acima do custo, essa diferença não pode servir para distribuir lucros nem para calcular percentuais de fundos de reserva.",
        "o_que_significa": "Uma valorização ainda não realizada não pode ser tratada como lucro distribuível nem aumentar artificialmente reservas calculadas por percentual. O balanço deve evitar transformar expectativa de ganho em resultado disponível.",
        "exemplo_pratico": "Mercadoria adquirida por cem passa a valer cento e trinta e é registrada pelo preço corrente. A diferença de trinta não pode ser usada para distribuir dividendos nem para calcular a parcela destinada ao fundo de reserva.",
        "atencao": "Leis e normas contábeis especiais podem complementar os critérios, mas não afastam a vedação do inciso quanto à diferença entre preço corrente e custo para esses fins.",
        "palavras_dificeis": [{"termo": "depreciação", "explicacao": "redução contábil do valor de um bem pelo uso, tempo ou obsolescência"}, {"termo": "fundo de reserva", "explicacao": "parcela patrimonial separada para finalidade ou proteção definida em lei ou no regime societário"}],
    },
    "CC2002:ART.1228": {
        "o_que_diz": "O proprietário pode usar, fruir, dispor e reivindicar a coisa, mas deve exercer o domínio conforme suas finalidades econômicas e sociais. Nos termos da legislação especial, deve preservar flora, fauna, belezas naturais, equilíbrio ecológico e patrimônio histórico e artístico, além de evitar poluição do ar e das águas. O abuso é vedado. Em situação de extensa posse coletiva de boa-fé com obras ou serviços de interesse social e econômico relevante, o proprietário pode perder o imóvel mediante justa indenização fixada pelo juiz; pago o preço, a sentença vale como título para registrar o imóvel em nome dos possuidores.",
        "o_que_significa": "A propriedade é ampla, mas não absoluta. Ela se submete a deveres sociais e ambientais e, na hipótese excepcional de posse coletiva qualificada, a transferência só se completa com a indenização e o pagamento que permite o registro em favor dos possuidores.",
        "exemplo_pratico": "Uma extensa área é ocupada de boa-fé por muitas pessoas que realizam obras socialmente relevantes. Reconhecidos os requisitos legais, o juiz fixa indenização justa ao proprietário; somente depois de pago o preço a sentença serve para registrar o imóvel em nome dos possuidores.",
        "atencao": "A hipótese dos §§ 4º e 5º exige conjuntamente posse ininterrupta e de boa-fé por mais de cinco anos, número considerável de pessoas e obras ou serviços de relevante interesse social e econômico. Ela não autoriza transferência sem justa indenização e pagamento.",
        "palavras_dificeis": [{"termo": "função social", "explicacao": "dever de exercer a propriedade de modo compatível com interesses econômicos, sociais e ambientais protegidos"}, {"termo": "título para registro", "explicacao": "documento juridicamente apto a permitir a inscrição da propriedade no registro de imóveis"}],
    },
    "CC2002:ART.1301": {
        "o_que_diz": "Janelas, terraços, varandas e eirados devem respeitar as distâncias legais do imóvel vizinho, com regra própria para visão oblíqua. A restrição não alcança pequenas aberturas exclusivamente para luz ou ventilação quando tiverem, no máximo, dez centímetros de largura por vinte de comprimento e estiverem construídas a mais de dois metros de altura em cada piso.",
        "o_que_significa": "A lei protege a privacidade do vizinho, mas admite uma abertura reduzida e elevada para iluminação ou ventilação. A exceção só vale se todas as medidas forem respeitadas.",
        "exemplo_pratico": "Uma abertura de dez por vinte centímetros instalada acima de dois metros do piso pode servir à ventilação sem se submeter à distância geral das janelas; uma abertura maior não entra nessa exceção.",
        "atencao": "Os limites são cumulativos: largura não superior a dez centímetros, comprimento não superior a vinte centímetros e altura superior a dois metros em relação a cada piso.",
        "palavras_dificeis": [{"termo": "visão oblíqua", "explicacao": "vista lateral ou indireta para o imóvel vizinho"}, {"termo": "eirado", "explicacao": "terraço ou área descoberta elevada de uma edificação"}],
    },
    "CC2002:ART.1331": {
        "o_que_diz": "No condomínio edilício, existem unidades de propriedade exclusiva e partes comuns inseparáveis. Cada unidade se vincula a uma fração ideal do solo e das áreas comuns, e nenhuma unidade pode ficar sem acesso ao logradouro público.",
        "o_que_significa": "O titular dispõe de sua unidade, mas compartilha estruturas essenciais do edifício. A organização do condomínio não pode criar unidade imobiliária isolada da via pública.",
        "exemplo_pratico": "Apartamento é exclusivo e corredores são comuns; a divisão ou alteração do prédio não pode deixar uma das unidades sem caminho juridicamente assegurado até a rua.",
        "atencao": "Abrigos de veículos e partes comuns seguem o título, a convenção e as restrições legais. O acesso ao logradouro público deve ser preservado para todas as unidades.",
        "palavras_dificeis": [{"termo": "fração ideal", "explicacao": "participação indivisa de cada unidade no terreno e nas partes comuns"}, {"termo": "logradouro público", "explicacao": "via ou espaço público de circulação, como rua ou avenida"}],
    },
    "CC2002:ART.1336": {
        "o_que_diz": "O condômino deve contribuir para as despesas, preservar segurança e fachada e respeitar a destinação do edifício. Quem não paga a contribuição fica sujeito à correção monetária, aos juros moratórios convencionados ou, se não houver previsão, aos juros do art. 406, além de multa de até dois por cento sobre o débito. Outras violações podem gerar as multas previstas nos limites legais.",
        "o_que_significa": "O atraso atualiza o valor devido e pode acrescentar juros e multa, mas cada encargo deve seguir sua base legal ou convencional. As sanções de conduta também dependem das regras e do procedimento aplicáveis.",
        "exemplo_pratico": "O condômino atrasa a quota mensal: o débito é corrigido, recebe os juros definidos na convenção — ou os do art. 406 se ela nada disser — e pode sofrer multa de até dois por cento sobre o valor devido.",
        "atencao": "Correção monetária, juros e multa são encargos distintos. A multa moratória do § 1º não pode ultrapassar dois por cento do débito.",
        "palavras_dificeis": [{"termo": "juros moratórios", "explicacao": "juros devidos pelo atraso no pagamento"}, {"termo": "correção monetária", "explicacao": "atualização do valor para recompor a perda do poder de compra da moeda"}],
    },
    "CC2002:ART.1341": {
        "o_que_diz": "Obras voluptuárias exigem voto de dois terços dos condôminos e obras úteis, maioria. Reparos necessários cabem ao síndico e, se ele se omitir ou estiver impedido, podem ser feitos por qualquer condômino. Se forem urgentes e de custo excessivo, a assembleia deve ser imediatamente convocada; se não forem urgentes e tiverem despesa excessiva, só podem começar após autorização de assembleia especialmente convocada. O condômino é reembolsado pelo que gastar em obra ou reparo necessário, mas não pelas obras de outra natureza, ainda que de interesse comum.",
        "o_que_significa": "Urgência, necessidade e custo definem quem pode agir e quando a assembleia precisa autorizar. Gasto alto sem urgência exige autorização prévia; o reembolso individual é reservado às intervenções necessárias.",
        "exemplo_pratico": "Morador contém vazamento urgente e pode cobrar a despesa necessária. Já uma reparação cara, mas sem urgência, deve aguardar autorização da assembleia; uma melhoria apenas útil feita por iniciativa própria não gera automaticamente reembolso.",
        "atencao": "Não confunda convocação posterior à obra urgente de custo excessivo com autorização prévia para obra necessária não urgente de custo excessivo. Também não há restituição pelo simples fato de uma obra não necessária interessar ao condomínio.",
        "palavras_dificeis": [{"termo": "obra necessária", "explicacao": "intervenção destinada a conservar o bem ou evitar sua deterioração"}, {"termo": "obra voluptuária", "explicacao": "melhoria de recreio ou luxo que não aumenta o uso habitual do bem"}],
    },
}


def main():
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    findings = [x for x in queue["findings"] if x["final_severity"] == "ALTO"][:21]
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    subdivision = {s["subdivision_id"]: s for row in inventory["records"] for s in row["subdivisions"]}
    corpus = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines()]
    active = {row["target_id"]: row for row in corpus if row["status"] == "ACTIVE"}
    target_order = []
    by_target = {}
    for finding in findings:
        target = finding["target_id"]
        if target not in by_target:
            target_order.append(target)
            by_target[target] = []
        by_target[target].append({
            "finding_id": finding["finding_id"],
            "subdivision_id": finding["subdivision_id"],
            "historical_severity": finding["final_severity"],
            "historical_classification": finding["final_classification"],
            "qa06_review_justification": finding["review_justification"],
            "official_legal_text": subdivision[finding["subdivision_id"]]["text"],
            "decision": "CORRECAO_NECESSARIA",
            "analysis": "A explicação QA-06 não representa integralmente o comando material indicado; a proposta integrada explicita a regra sem transformar o ENTENDA em transcrição da lei.",
        })
    records = []
    for target in target_order:
        records.append({
            "target_id": target,
            "source_explanation_id": active[target]["explanation_id"],
            "source_editorial_version": active[target]["editorial_version"],
            "findings": by_target[target],
            "decision": "CORRECAO_NECESSARIA",
            "previous_content": active[target]["content"],
            "proposed_content": PROPOSALS[target],
            "editor_risk_check": "Revisor independente deve conferir integralidade, precisão dos marcos/condições e ausência de nova generalização indevida.",
        })
    doc = {
        "schema_version": 1,
        "mission": "QA-07",
        "role": "EDITOR_HIGH_A",
        "as_of": AS_OF,
        "status": "EDITORIAL_PROPOSALS_COMPLETE_PENDING_INDEPENDENT_REVALIDATION",
        "source_queue": QUEUE.name,
        "source_queue_sha256": sha(QUEUE),
        "authorized_inventory": INVENTORY.name,
        "authorized_inventory_sha256": sha(INVENTORY),
        "baseline_corpus_sha256": sha(CORPUS),
        "finding_count": len(findings),
        "target_count": len(records),
        "decision_counts": {"CORRECAO_NECESSARIA": len(findings), "COBERTURA_SUFFICIENTE_COM_FUNDAMENTO": 0},
        "sources": [{
            "authority": "Câmara dos Deputados",
            "url": "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html",
            "cutoff_date": AS_OF,
            "local_official_snapshot_sha256": inventory["legal_text_source_sha256"],
        }],
        "human_approval_claimed": False,
        "corpus_modified": False,
        "records": records,
    }
    if set(PROPOSALS) != set(target_order):
        raise RuntimeError((set(PROPOSALS) - set(target_order), set(target_order) - set(PROPOSALS)))
    OUT.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"findings": len(findings), "targets": len(records), "sha256": sha(DEST)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
