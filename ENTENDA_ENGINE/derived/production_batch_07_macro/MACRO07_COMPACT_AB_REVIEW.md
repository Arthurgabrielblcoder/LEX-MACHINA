# MACRO07 — REVISÃO COMPACTA (filas A e B)

Lote `ENTENDA_CF_MACRO_BATCH_07` · 2026-10-05 · nenhum item aprovado (AUTO_APPROVE_LOW/MEDIUM = OFF). Revisão humana obrigatória em formato compacto; T1 completo só sob pedido. Risco = LEGAL_RISK; complexidade = VERIFICATION_COMPLEXITY.

## A — CLEAN_LOW (54)

### `CF88:ART.76` — Art. 76 — Exercício do Poder Executivo

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 76 atribui o exercício do Poder Executivo federal ao Presidente da República, que conta com o auxílio dos Ministros de Estado.
- Interpretação principal: O artigo concentra a chefia do Executivo da União em uma única pessoa: o Presidente da República.
- ATENÇÃO: O artigo trata do Executivo da União.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.77` — Art. 77 — Eleição do Presidente e do Vice-Presidente

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 77 marca a eleição presidencial para outubro do ano anterior ao fim do mandato: primeiro turno no primeiro domingo do mês e, se houver, segundo turno no último domingo.
- Interpretação principal: Presidente e Vice são eleitos na mesma votação.
- ATENÇÃO: A regra do segundo turno vale para Presidente; Governadores e Prefeitos de grandes Municípios seguem regras próprias, por remissão (arts. 28 e 29, II).
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.77:PAR.2` — Art. 77, §§ 2º e 3º — Maioria absoluta e segundo turno

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º considera eleito o candidato, registrado por partido, que obtiver maioria absoluta de votos, sem contar os brancos e os nulos.
- Interpretação principal: No primeiro turno, a conta considera apenas os votos válidos, isto é, os dados a candidatos.
- ATENÇÃO: Maioria absoluta, aqui, é calculada sobre os votos válidos, e não sobre o total de eleitores nem sobre o total de votos depositados.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.78` — Art. 78 — Posse do Presidente e do Vice-Presidente

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 78 determina que o Presidente e o Vice tomem posse em sessão do Congresso Nacional, prestando compromisso de defender e cumprir a Constituição e as leis.
- Interpretação principal: A posse é o ato que transforma o eleito em titular do cargo.
- ATENÇÃO: O prazo de dez dias conta da data fixada para a posse.
- Dependência externa: nenhuma
- Warnings: NUMBER_FROM_OTHER_DEVICE(15 dias), lint TERM_NOT_USED
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.79` — Art. 79 — Substituição e sucessão pelo Vice-Presidente

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 79 determina que o Vice-Presidente substitua o Presidente nos impedimentos e o suceda em caso de vaga.
- Interpretação principal: Substituir e suceder são coisas diferentes.
- ATENÇÃO: Se Presidente e Vice estiverem impedidos ou os dois cargos vagarem, aplicam-se os arts. 80 e 81.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.80` — Art. 80 — Linha de substituição do Presidente

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 80 estabelece quem exerce a Presidência quando Presidente e Vice estão impedidos ou os dois cargos estão vagos: são chamados, nesta ordem, o Presidente da Câmara dos Deputados, o Presidente do…
- Interpretação principal: O artigo cria uma linha de substituição para os casos em que nem o Presidente nem o Vice podem exercer o cargo.
- ATENÇÃO: Exercer a Presidência não é o mesmo que suceder no cargo.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.81` — Art. 81 — Dupla vacância: nova eleição

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 81 determina nova eleição quando vagam os cargos de Presidente e Vice: em regra, noventa dias depois da última vaga.
- Interpretação principal: Quando só o Presidente sai, o Vice o sucede (art. 79).
- ATENÇÃO: Enquanto a nova eleição não acontece, a Presidência é exercida pela linha do art. 80 (Presidente da Câmara, do Senado e do Supremo Tribunal Federal).
- Dependência externa: nenhuma
- Warnings: lint TERM_NOT_USED
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.81:PAR.1` — Art. 81, § 1º — Eleição indireta pelo Congresso Nacional

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º estabelece que, se os cargos de Presidente e Vice vagarem nos dois últimos anos do período presidencial, a eleição para ambos será feita pelo Congresso Nacional, trinta dias após a última…
- Interpretação principal: É a única hipótese em que a Constituição prevê eleição indireta para Presidente da República.
- ATENÇÃO: A eleição indireta depende do momento da segunda vaga, que precisa ocorrer nos dois últimos anos do período presidencial.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: anos do período presidencial a eleição para ambos), lint PARENT_REPETITION
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.84` — Art. 84 — Atribuições do Presidente da República

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 84 enumera as competências privativas do Presidente da República.
- Interpretação principal: As competências podem ser agrupadas pelas duas funções do Presidente.
- ATENÇÃO: O inciso XXVII mostra que a lista não é fechada: outras atribuições do Presidente estão espalhadas pela Constituição.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.84:INC.IV` — Art. 84, inciso IV — Sanção, promulgação e poder regulamentar

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso IV dá ao Presidente a competência para sancionar, promulgar e fazer publicar as leis, e para expedir decretos e regulamentos destinados à fiel execução delas.
- Interpretação principal: O inciso reúne duas funções.
- ATENÇÃO: O decreto de execução do inciso IV é diferente do decreto previsto no inciso VI, que trata de organização da administração e de cargos vagos sem depender de lei específica.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.84:INC.VI` — Art. 84, inciso VI — Decreto sobre organização administrativa

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso VI permite ao Presidente dispor por decreto sobre a organização e o funcionamento da administração federal, sem aumento de despesa e sem criação ou extinção de órgãos públicos (alínea a).
- Interpretação principal: Aqui o decreto não regulamenta uma lei específica: ele trata diretamente da organização interna da administração.
- ATENÇÃO: Criar ou extinguir órgão público e criar cargo continuam exigindo lei.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.84:PAR.UNICO` — Art. 84, parágrafo único — Delegação de atribuições do Presidente

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O parágrafo único permite ao Presidente delegar as atribuições dos incisos VI e XII e a primeira parte do inciso XXV.
- Interpretação principal: Delegar é transferir a outra autoridade o exercício de uma competência.
- ATENÇÃO: A expressão "primeira parte" significa que, no inciso XXV, só o provimento de cargos pode ser delegado; a extinção de cargos públicos não está incluída.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.87` — Art. 87 — Ministros de Estado

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 87 exige que os Ministros de Estado sejam brasileiros maiores de vinte e um anos, em pleno gozo dos direitos políticos.
- Interpretação principal: Os requisitos são poucos: nacionalidade brasileira, idade mínima e gozo dos direitos políticos.
- ATENÇÃO: Para alguns Ministérios a Constituição exige brasileiro nato: é o caso do Ministro de Estado da Defesa (art. 12, § 3º, VII).
- Dependência externa: nenhuma
- Warnings: EXAMPLE_NUMBER_NOT_IN_TEXT(30)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.88` — Art. 88 — Criação e extinção de Ministérios

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 88 determina que cabe à lei tratar da criação e da extinção de Ministérios e de órgãos da administração pública.
- Interpretação principal: O Presidente não cria nem extingue Ministérios sozinho, por decreto.
- ATENÇÃO: Transferir atribuições entre órgãos já existentes, sem criar nem extinguir órgãos e sem aumentar despesas, pode ser feito por decreto (art. 84, VI, a).
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.89` — Art. 89 — Conselho da República: composição

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 89 define o Conselho da República como órgão superior de consulta do Presidente.
- Interpretação principal: O Conselho reúne representantes do governo, do Congresso e da sociedade para aconselhar o Presidente em momentos institucionais delicados.
- ATENÇÃO: O Conselho é consultivo: sua manifestação não obriga o Presidente.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.90` — Art. 90 — Conselho da República: competências

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 90 determina que o Conselho da República se pronuncie sobre intervenção federal, estado de defesa e estado de sítio, e sobre questões relevantes para a estabilidade das instituições…
- Interpretação principal: As matérias do Conselho são as mais sensíveis para a democracia: as medidas excepcionais de defesa do Estado e as crises institucionais.
- ATENÇÃO: Ouvir o Conselho é etapa prevista para a intervenção federal, o estado de defesa e o estado de sítio (arts. 136 e 137), mas a opinião do Conselho não vincula o Presidente.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: federal estado de defesa e estado de sítio)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.91` — Art. 91 — Conselho de Defesa Nacional

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 91 cria o Conselho de Defesa Nacional como órgão de consulta do Presidente em assuntos de soberania nacional e defesa do Estado democrático.
- Interpretação principal: Enquanto o Conselho da República é político e inclui cidadãos, o Conselho de Defesa Nacional é técnico-militar e tem foco em segurança e soberania.
- ATENÇÃO: As hipóteses de estado de defesa, estado de sítio e intervenção federal aparecem nos dois Conselhos: o da República (art. 90) e o de Defesa Nacional (§ 1º, II).
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.93:INC.II` — Art. 93, inciso II — Promoção na magistratura

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso II determina que a promoção de uma entrância para outra se faça alternadamente por antiguidade e por merecimento.
- Interpretação principal: A carreira avança por dois critérios que se revezam.
- ATENÇÃO: A ressalva da alínea b permite promover quem não preenche os requisitos de tempo e posição apenas quando nenhum juiz que os preenche aceita a vaga.
- Dependência externa: nenhuma
- Warnings: lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.93:INC.V` — Art. 93, inciso V — Subsídio dos magistrados

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso V fixa o subsídio dos Ministros dos Tribunais Superiores em noventa e cinco por cento do subsídio dos Ministros do Supremo Tribunal Federal.
- Interpretação principal: A remuneração dos juízes forma uma escada.
- ATENÇÃO: O inciso trata da estrutura do escalonamento; os valores concretos dependem de lei.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.93:INC.VIII` — Art. 93, inciso VIII — Remoção e disponibilidade por interesse público

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso VIII exige que a remoção ou a disponibilidade de um juiz, quando motivada por interesse público, dependa de decisão da maioria absoluta do tribunal ou do Conselho Nacional de Justiça, com…
- Interpretação principal: Em regra, o juiz não pode ser transferido contra a sua vontade: é a garantia da inamovibilidade (art. 95, II).
- ATENÇÃO: Remoção por interesse público é diferente da remoção a pedido do próprio juiz, tratada no inciso VIII-A.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.94` — Art. 94 — Quinto constitucional

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 94 reserva um quinto dos lugares dos Tribunais Regionais Federais e dos tribunais dos Estados, do Distrito Federal e Territórios a membros do Ministério Público e a advogados, todos com mais…
- Interpretação principal: É o chamado quinto constitucional: parte das vagas dos tribunais não é preenchida por juízes de carreira, mas por pessoas vindas do Ministério Público e da advocacia.
- ATENÇÃO: O quinto também aparece, com regras próprias, em outros tribunais, como os do Trabalho (art. 115).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: um quinto dos lugares dos tribunais regionais…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.95:PAR.UNICO` — Art. 95, parágrafo único — Vedações aos juízes

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O parágrafo único proíbe ao juiz: exercer outro cargo ou função, ainda que em disponibilidade, salvo uma de magistério; receber custas ou participação em processo; dedicar-se a atividade…
- Interpretação principal: As vedações procuram manter o juiz dedicado à função e afastado de interesses que possam influenciar suas decisões.
- ATENÇÃO: As exceções do inciso IV dependem de previsão em lei; não basta a vontade do doador ou do juiz.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.98:INC.I` — Art. 98, inciso I — Juizados especiais

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O inciso I prevê juizados especiais, providos por juízes togados ou por togados e leigos, com competência para conciliar, julgar e executar, por procedimentos oral e sumaríssimo, as causas cíveis…
- Interpretação principal: Os juizados foram pensados para causas simples.
- ATENÇÃO: O conceito de causa de menor complexidade e de infração de menor potencial ofensivo depende de lei; o inciso não fixa valores nem penas.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.99` — Art. 99 — Autonomia administrativa e financeira do Judiciário

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 99 assegura ao Poder Judiciário autonomia administrativa e financeira.
- Interpretação principal: A autonomia financeira significa que o próprio Judiciário prepara a sua proposta de orçamento, sem depender do Executivo para isso.
- ATENÇÃO: A proposta do Judiciário integra o projeto de lei orçamentária, que depende de aprovação do Legislativo.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: com os demais poderes na lei de diretrizes), NEAR_COPY_MICROFIX(o_que_significa: do supremo tribunal federal e dos tribunais…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.99:PAR.3` — Art. 99, §§ 3º, 4º e 5º — Proposta orçamentária fora do prazo ou dos limites

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 3º determina que, se a proposta do Judiciário não for enviada no prazo da lei de diretrizes orçamentárias, o Executivo considere os valores da lei orçamentária vigente, ajustados aos limites do §…
- Interpretação principal: Os três parágrafos fecham as brechas da autonomia financeira.
- ATENÇÃO: A ressalva do § 5º exige autorização prévia: créditos suplementares ou especiais não podem ser abertos depois que a despesa já foi feita.
- Dependência externa: nenhuma
- Warnings: lint PARENT_REPETITION
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.100:PAR.3` — Art. 100, §§ 3º e 4º — Obrigações de pequeno valor

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 3º afasta a exigência de precatório para as obrigações definidas em lei como de pequeno valor, devidas pela Fazenda Pública em razão de sentença transitada em julgado.
- Interpretação principal: Dívidas menores não entram na fila do precatório.
- ATENÇÃO: O município não pode fixar limite abaixo do maior benefício do regime geral de previdência social.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: maior benefício do regime geral de previdência…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.100:PAR.11` — Art. 100, § 11 — Uso de créditos de precatório

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 11 permite ao credor, conforme lei do ente devedor e de forma autoaplicável para a União, oferecer créditos líquidos e certos, próprios ou adquiridos de terceiros, reconhecidos pelo ente ou por…
- Interpretação principal: O credor não precisa esperar a fila para usar o crédito em certas operações com o próprio ente devedor.
- ATENÇÃO: As operações valem com o mesmo ente devedor.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: próprios ou adquiridos de terceiros reconhecidos…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.100:PAR.13` — Art. 100, §§ 13 e 14 — Cessão de precatórios

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 13 permite ao credor ceder, total ou parcialmente, seus créditos em precatórios a terceiros, sem precisar da concordância do devedor; ao cessionário não se aplicam as preferências do § 2º nem o…
- Interpretação principal: O credor pode transferir seu precatório, por exemplo a um investidor.
- ATENÇÃO: Enquanto não houver a comunicação por petição ao Tribunal e ao ente devedor, a cessão não produz efeitos.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: ceder total ou parcialmente seus créditos em…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.100:PAR.20` — Art. 100, § 20 — Precatório de valor muito alto

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 20 prevê que, se um precatório tiver valor superior a quinze por cento do total dos precatórios apresentados nos termos do § 5º, quinze por cento do seu valor seja pago até o fim do exercício…
- Interpretação principal: Um único precatório muito grande poderia consumir quase todo o orçamento destinado a precatórios.
- ATENÇÃO: O acordo depende da regulamentação do ente devedor e de não haver recurso ou defesa pendente sobre o crédito.
- Dependência externa: nenhuma
- Warnings: EXAMPLE_NUMBER_NOT_IN_TEXT(20%)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.100:PAR.23` — Art. 100, §§ 23 e 24 — Limites anuais de pagamento de Estados, Distrito Federal e Municípios

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O § 23 limita os pagamentos anuais de precatórios dos Estados, do Distrito Federal e dos Municípios a um percentual da receita corrente líquida do exercício anterior.
- Interpretação principal: Em vez de quitar o estoque de uma só vez, esses entes pagam até um teto anual ligado à sua receita.
- ATENÇÃO: As faixas, os percentuais e a data de 2036 constam do texto atual, mas a sistemática foi introduzida recentemente por emenda; a transição entre regimes deve ser consultada na camada externa.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a partir de 1 de janeiro de 2036), EXAMPLE_NUMBER_NOT_IN_TEXT(30%), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.100:PAR.27` — Art. 100, § 27 — Falta de repasse para precatórios

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 27 prevê que, se os recursos destinados aos precatórios dos Estados, do Distrito Federal e dos Municípios não forem liberados no tempo devido, no todo ou em parte: os limites do § 23 ficam…
- Interpretação principal: O limite anual do § 23 é um benefício para o ente devedor, condicionado ao repasse em dia.
- ATENÇÃO: O inciso III remete à legislação de responsabilidade fiscal e de improbidade: a punição concreta depende dessas leis.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: da legislação de responsabilidade fiscal e de…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.101` — Art. 101 — Composição do Supremo Tribunal Federal

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 101 estabelece que o Supremo Tribunal Federal tem onze Ministros.
- Interpretação principal: O Supremo é o órgão de cúpula do Judiciário, e o artigo define quem pode integrá-lo e como se chega lá.
- ATENÇÃO: O artigo exige apenas cidadania; outra regra da Constituição reserva o cargo de Ministro do Supremo a brasileiros natos (art. 12, § 3º).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: de trinta e cinco e menos de setenta), EXAMPLE_NUMBER_NOT_IN_TEXT(50), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.102:INC.III` — Art. 102, inciso III — Recurso extraordinário

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O inciso III atribui ao Supremo Tribunal Federal o julgamento, por recurso extraordinário, das causas decididas em única ou última instância.
- Interpretação principal: O recurso extraordinário é o caminho para levar ao Supremo uma questão constitucional surgida em qualquer processo.
- ATENÇÃO: Além das alíneas, o recorrente precisa demonstrar a repercussão geral da questão (§ 3º, com explicação própria).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: julgar válida lei ou ato de governo local), DUPLICATION(resolvido), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.102:PAR.3` — Art. 102, § 3º — Repercussão geral no recurso extraordinário

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O § 3º exige que, no recurso extraordinário, o recorrente demonstre a repercussão geral das questões constitucionais discutidas, nos termos da lei.
- Interpretação principal: Não basta que a questão seja constitucional: o recorrente precisa demonstrar a repercussão geral.
- ATENÇÃO: Os critérios do que tem repercussão geral estão na lei processual, e não neste parágrafo.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: lo pela manifestação de dois terços de seus), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.103:PAR.2` — Art. 103, § 2º — Inconstitucionalidade por omissão

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º estabelece que, declarada a inconstitucionalidade por omissão de medida necessária para tornar efetiva uma norma constitucional, o Poder competente recebe ciência para adotar as providências…
- Interpretação principal: Algumas normas da Constituição só funcionam plenamente depois que o legislador ou a administração fazem a sua parte.
- ATENÇÃO: O texto não fixa prazo para o Poder Legislativo.
- Dependência externa: nenhuma
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.104` — Art. 104 — Composição do Superior Tribunal de Justiça

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 104 estabelece que o Superior Tribunal de Justiça tem no mínimo trinta e três Ministros.
- Interpretação principal: O artigo combina dois elementos: um número mínimo de Ministros e uma regra de origem das vagas.
- ATENÇÃO: Diferentemente do art. 101, aqui o texto exige que o escolhido seja brasileiro.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: de trinta e cinco e menos de setenta), NEAR_COPY_MICROFIX(o_que_significa: desembargadores dos tribunais de justiça…), DUPLICATION(resolvido), DUPLICATION(resolvido), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.106` — Art. 106 — Órgãos da Justiça Federal

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 106 indica os órgãos da Justiça Federal: os Tribunais Regionais Federais e os Juízes Federais.
- Interpretação principal: A Justiça Federal tem dois graus.
- ATENÇÃO: O artigo apenas lista os órgãos.
- Dependência externa: nenhuma
- Warnings: DUPLICATION(resolvido), DUPLICATION(resolvido), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.107` — Art. 107 — Composição dos Tribunais Regionais Federais

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 107 estabelece que os Tribunais Regionais Federais têm no mínimo sete juízes, recrutados quando possível na própria região e nomeados pelo Presidente da República entre brasileiros com mais de…
- Interpretação principal: O artigo aplica aos tribunais federais de segundo grau o modelo do quinto constitucional: a maior parte das vagas fica com juízes de carreira, e um quinto com…
- ATENÇÃO: A remoção e a permuta de juízes dos tribunais, assim como a jurisdição e a sede de cada um, são definidas em lei (§ 1º), e não neste artigo.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: brasileiros com mais de trinta e menos de), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.109:PAR.3` — Art. 109, §§ 3º e 4º — Causas previdenciárias na Justiça estadual

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O § 3º permite que a lei leve à Justiça estadual causas federais entre instituição de previdência social e segurado, quando não houver vara federal sediada na comarca onde o segurado mora.
- Interpretação principal: Os parágrafos tratam de uma delegação de competência para facilitar o acesso do segurado.
- ATENÇÃO: O § 3º é permissivo: a lei pode autorizar a delegação e definir suas condições.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.110` — Art. 110 — Seções judiciárias

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 110 determina que cada Estado e o Distrito Federal formem uma seção judiciária, com sede na respectiva capital, e varas localizadas conforme a lei.
- Interpretação principal: A seção judiciária é a unidade territorial da Justiça Federal de primeiro grau.
- ATENÇÃO: A localização das varas é definida em lei.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: nos territórios federais a jurisdição e as…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.111` — Art. 111 — Órgãos da Justiça do Trabalho

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 111 indica os órgãos da Justiça do Trabalho: o Tribunal Superior do Trabalho, os Tribunais Regionais do Trabalho e os Juízes do Trabalho.
- Interpretação principal: A Justiça do Trabalho é um ramo especializado do Judiciário, voltado às relações de trabalho.
- ATENÇÃO: Os parágrafos originais do artigo foram revogados; a composição e o funcionamento dos tribunais estão nos artigos seguintes.
- Dependência externa: nenhuma
- Warnings: DUPLICATION(resolvido), DUPLICATION(resolvido), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.111-A` — Art. 111-A — Tribunal Superior do Trabalho

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 111-A estabelece que o Tribunal Superior do Trabalho tem vinte e sete Ministros, nomeados pelo Presidente da República após aprovação da maioria absoluta do Senado.
- Interpretação principal: Diferentemente do Superior Tribunal de Justiça, o Tribunal Superior do Trabalho tem número fixo de Ministros: vinte e sete.
- ATENÇÃO: A competência do Tribunal Superior do Trabalho é definida em lei (§ 1º).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: de trinta e cinco e menos de setenta), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.112` — Art. 112 — Varas do Trabalho

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 112 determina que a lei crie as varas da Justiça do Trabalho.
- Interpretação principal: As varas do trabalho são a porta de entrada da Justiça do Trabalho, mas não existem em todas as cidades.
- ATENÇÃO: A atribuição ao juiz de direito é uma possibilidade, a ser definida em lei, e vale apenas para comarcas não abrangidas pela jurisdição de vara do trabalho.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: aos juízes de direito com recurso para o)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.113` — Art. 113 — Lei de organização da Justiça do Trabalho

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 113 remete à lei a disciplina dos órgãos da Justiça do Trabalho: como são constituídos, como seus membros são investidos, qual a sua jurisdição e competência, quais as garantias e as condições…
- Interpretação principal: A Constituição traça a estrutura básica da Justiça do Trabalho nos arts. 111 a 116, mas deixa os detalhes para o legislador.
- ATENÇÃO: As garantias da magistratura do trabalho incluem as que a própria Constituição dá a todos os juízes (art. 95).
- Dependência externa: nenhuma
- Warnings: lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.115` — Art. 115 — Tribunais Regionais do Trabalho

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 115 fixa a composição dos Tribunais Regionais do Trabalho: pelo menos sete juízes, nomeados pelo Presidente da República entre brasileiros que tenham mais de trinta e menos de setenta anos,…
- Interpretação principal: O desenho é o mesmo dos Tribunais Regionais Federais (art. 107): número mínimo, quinto constitucional e promoção de juízes de carreira.
- ATENÇÃO: O texto não exige tempo mínimo de exercício para a promoção dos juízes do trabalho, diferentemente do que faz para os Tribunais Regionais Federais (art. 107).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: mais de trinta e menos de setenta anos), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.116` — Art. 116 — Juiz singular nas Varas do Trabalho

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 116 determina que, nas Varas do Trabalho, a jurisdição seja exercida por um juiz singular.
- Interpretação principal: Na primeira instância da Justiça do Trabalho, quem julga é um único juiz, chamado juiz singular.
- ATENÇÃO: O artigo trata apenas da vara do trabalho.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.118` — Art. 118 — Órgãos da Justiça Eleitoral

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 118 indica os órgãos da Justiça Eleitoral: o Tribunal Superior Eleitoral, os Tribunais Regionais Eleitorais, os Juízes Eleitorais e as Juntas Eleitorais.
- Interpretação principal: A Justiça Eleitoral é o ramo do Judiciário que cuida das eleições: do alistamento dos eleitores à diplomação dos eleitos e aos processos sobre o pleito.
- ATENÇÃO: A composição dos tribunais eleitorais está nos arts. 119 e 120.
- Dependência externa: nenhuma
- Warnings: DUPLICATION(resolvido), DUPLICATION(resolvido), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.119` — Art. 119 — Composição do Tribunal Superior Eleitoral

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 119 estabelece que o Tribunal Superior Eleitoral tem no mínimo sete membros.
- Interpretação principal: O Tribunal Superior Eleitoral não tem quadro próprio de juízes de carreira.
- ATENÇÃO: O número sete é mínimo.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: advogados de notável saber jurídico e idoneidade…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.120` — Art. 120 — Tribunais Regionais Eleitorais

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 120 prevê que cada Estado tenha um Tribunal Regional Eleitoral sediado na capital, e que o Distrito Federal também tenha o seu.
- Interpretação principal: O tribunal regional segue o modelo do tribunal superior: não tem juízes próprios de carreira, e sim membros vindos de outros ramos do Judiciário e da advocacia.
- ATENÇÃO: As vagas da advocacia exigem notável saber jurídico e idoneidade moral.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: juízes de direito escolhidos pelo tribunal de…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.121` — Art. 121 — Organização e funcionamento da Justiça Eleitoral

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 121 remete à lei complementar a organização e a competência dos órgãos da Justiça Eleitoral: tribunais, juízes de direito e juntas.
- Interpretação principal: A Justiça Eleitoral depende muito da lei complementar, que define o que cada órgão faz.
- ATENÇÃO: Os §§ 2º, 3º e 4º têm explicações próprias.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.121:PAR.2` — Art. 121, § 2º — Mandato dos juízes eleitorais

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º determina que os juízes dos tribunais eleitorais sirvam por pelo menos dois anos, salvo motivo justificado, e por no máximo dois biênios seguidos.
- Interpretação principal: Os juízes dos tribunais eleitorais não ficam no cargo por tempo indeterminado.
- ATENÇÃO: O limite fala em biênios consecutivos.
- Dependência externa: nenhuma
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY, lint TERM_LOW_UTILITY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.121:PAR.3` — Art. 121, §§ 3º e 4º — Recursos contra decisões eleitorais

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 3º estabelece que não cabe recurso contra as decisões do Tribunal Superior Eleitoral, salvo quando contrariarem a Constituição ou negarem habeas corpus ou mandado de segurança.
- Interpretação principal: Os parágrafos limitam os recursos no processo eleitoral.
- ATENÇÃO: As hipóteses de recurso contra os tribunais regionais formam lista fechada, indicada pela palavra somente.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.122` — Art. 122 — Órgãos da Justiça Militar

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 122 indica os órgãos da Justiça Militar: o Superior Tribunal Militar e os Tribunais e Juízes Militares instituídos por lei.
- Interpretação principal: A Justiça Militar é o ramo especializado do Judiciário que julga crimes militares.
- ATENÇÃO: A organização da primeira instância da Justiça Militar da União é definida em lei, e não neste artigo.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: os tribunais e juízes militares instituídos por…), DUPLICATION(resolvido), DUPLICATION(resolvido), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.123` — Art. 123 — Composição do Superior Tribunal Militar

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 123 estabelece que o Superior Tribunal Militar tem quinze Ministros vitalícios, nomeados pelo Presidente da República depois que o Senado aprova a indicação.
- Interpretação principal: O tribunal tem composição mista: a maioria é de militares de alta patente, e uma parte é de civis.
- ATENÇÃO: Para os Ministros militares, o texto não fixa limite de idade; a faixa de trinta e cinco a setenta anos está no parágrafo único, dirigido aos civis.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: advogados de notório saber jurídico e conduta…), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

## B — CLEAN_MEDIUM (32)

### `CF88:ART.83` — Art. 83 — Ausência do País e perda do cargo

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: sob pena
- Ponto jurídico: O art. 83 proíbe o Presidente e o Vice de se ausentarem do País por mais de quinze dias sem licença do Congresso Nacional, sob pena de perderem o cargo.
- Interpretação principal: Viagens curtas ao exterior não dependem de autorização.
- ATENÇÃO: Ausências de até quinze dias não exigem licença; a exigência começa quando o período fora do País supera esse limite.
- Dependência externa: nenhuma
- Warnings: NUMBER_FROM_OTHER_DEVICE(20 dias), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.84:INC.XII` — Art. 84, inciso XII — Indulto e comutação de penas

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: Os limites do poder presidencial de indultar e a extensão das…
- Ponto jurídico: O inciso XII atribui ao Presidente a concessão de indulto e a comutação de penas, ouvindo, se necessário, os órgãos instituídos em lei.
- Interpretação principal: O indulto extingue a pena de pessoas condenadas que se enquadram nas condições fixadas no decreto presidencial.
- ATENÇÃO: O inciso não fixa os limites do indulto.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.85` — Art. 85 — Crimes de responsabilidade do Presidente

- Risco: MEDIUM · complexidade: EXTERNAL · SENSITIVE_THEME: crimes
- Ponto jurídico: O art. 85 define como crimes de responsabilidade os atos do Presidente que atentem contra a Constituição e, em especial, contra: a existência da União; o livre exercício dos Poderes, do Ministério…
- Interpretação principal: Crime de responsabilidade não é crime comum.
- ATENÇÃO: A definição concreta dos crimes depende da lei especial; o artigo não basta para tipificar uma conduta.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: o cumprimento das leis e das decisões judiciais)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.86` — Art. 86 — Processo e julgamento do Presidente

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crimes
- Ponto jurídico: O art. 86 estabelece que, admitida a acusação por dois terços da Câmara dos Deputados, o Presidente é julgado pelo Supremo Tribunal Federal nas infrações penais comuns ou pelo Senado nos crimes de…
- Interpretação principal: O processo contra o Presidente tem duas etapas.
- ATENÇÃO: Sem a autorização da Câmara por dois terços, o processo não avança, nem no Supremo nem no Senado.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: supremo tribunal federal nas infrações penais…)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.86:PAR.1` — Art. 86, §§ 1º e 2º — Afastamento do Presidente durante o processo

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crime
- Ponto jurídico: O § 1º suspende o Presidente de suas funções nas infrações penais comuns, quando o Supremo Tribunal Federal recebe a denúncia ou queixa-crime, e nos crimes de responsabilidade, quando o Senado…
- Interpretação principal: A autorização da Câmara não afasta o Presidente por si só.
- ATENÇÃO: O fim do afastamento pelo decurso do prazo não encerra o processo nem equivale a absolvição.
- Dependência externa: nenhuma
- Warnings: lint PARENT_REPETITION
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.93` — Art. 93 — Estatuto da Magistratura

- Risco: MEDIUM · complexidade: EXTERNAL · SENSITIVE_THEME: sob pena
- Ponto jurídico: O art. 93 determina que lei complementar, de iniciativa do Supremo Tribunal Federal, disponha sobre o Estatuto da Magistratura, observando uma série de princípios.
- Interpretação principal: O Estatuto da Magistratura é a lei que organiza a carreira dos juízes em todo o país.
- ATENÇÃO: Os princípios do art. 93 valem para toda a magistratura, federal e estadual, inclusive antes de qualquer alteração do Estatuto.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: lei complementar de iniciativa do supremo…)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.93:INC.I` — Art. 93, inciso I — Ingresso na magistratura

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: O conceito de atividade jurídica e o momento de sua…
- Ponto jurídico: O inciso I determina que o ingresso na magistratura se dê no cargo de juiz substituto, por concurso público de provas e títulos, acompanhado pela Ordem dos Advogados do Brasil em cada uma das suas…
- Interpretação principal: Ninguém começa a carreira como juiz titular: o primeiro cargo é o de juiz substituto.
- ATENÇÃO: O que conta como atividade jurídica e o momento de comprová-la não estão definidos no inciso; são tratados em normas do Judiciário e na camada JURISPRUDÊNCIA.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NUMBER_FROM_OTHER_DEVICE(4 anos), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.93:INC.IX` — Art. 93, inciso IX — Publicidade dos julgamentos e fundamentação das decisões

- Risco: MEDIUM · complexidade: SIMPLE · SENSITIVE_THEME: sob pena
- Ponto jurídico: O inciso IX determina que todos os julgamentos do Judiciário sejam públicos e todas as decisões fundamentadas, sob pena de nulidade.
- Interpretação principal: O inciso traz dois deveres.
- ATENÇÃO: A restrição de publicidade depende de previsão em lei e de ponderação entre intimidade e interesse público; já o dever de fundamentar não tem exceção no texto.
- Dependência externa: nenhuma
- Warnings: lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.93:INC.XII` — Art. 93, inciso XII — Atividade jurisdicional ininterrupta

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: A relação entre a vedação de férias coletivas e o recesso…
- Ponto jurídico: O inciso XII determina que a atividade jurisdicional seja ininterrupta.
- Interpretação principal: A Justiça não pode parar.
- ATENÇÃO: A vedação de férias coletivas não se confunde com o recesso de fim de ano previsto em lei para alguns ramos; o tema é tratado em normas infraconstitucionais e na camada JURISPRUDÊNCIA.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: lint EXAMPLE_REQUIREMENT_LANGUAGE, lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.95` — Art. 95 — Garantias e vedações dos juízes

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: perda do cargo
- Ponto jurídico: O art. 95 assegura aos juízes três garantias: vitaliciedade, inamovibilidade, salvo interesse público na forma do art. 93, VIII, e irredutibilidade de subsídio, com as ressalvas que indica.
- Interpretação principal: As garantias protegem a independência do juiz para decidir sem pressões.
- ATENÇÃO: A irredutibilidade não impede o desconto do imposto de renda nem a aplicação do teto remuneratório: essas ressalvas estão no próprio inciso III.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: interesse público na forma do art 93 viii)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.95:INC.I` — Art. 95, inciso I — Vitaliciedade dos juízes

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: perda do cargo
- Ponto jurídico: O inciso I estabelece que a vitaliciedade, no primeiro grau, só é adquirida após dois anos de exercício.
- Interpretação principal: O juiz que acabou de entrar na carreira passa por um período de dois anos de exercício.
- ATENÇÃO: Vitaliciedade não é o mesmo que estabilidade dos servidores (art. 41): o vitalício só perde o cargo por sentença judicial definitiva.
- Dependência externa: nenhuma
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.96` — Art. 96 — Autogoverno dos tribunais

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crimes
- Ponto jurídico: O art. 96 atribui privativamente aos tribunais eleger seus órgãos diretivos e elaborar regimentos, organizar suas secretarias, prover os cargos de juiz e de servidores, salvo os de confiança…
- Interpretação principal: O artigo traduz a ideia de autogoverno do Judiciário.
- ATENÇÃO: A iniciativa reservada aos tribunais impede que outro Poder apresente projeto sobre essas matérias, mas não dispensa a aprovação pelo Legislativo.
- Dependência externa: nenhuma
- Warnings: lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.96:INC.III` — Art. 96, inciso III — Julgamento de juízes e promotores estaduais

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crimes
- Ponto jurídico: O inciso III atribui aos Tribunais de Justiça o julgamento, por crimes comuns e de responsabilidade, dos juízes estaduais, do Distrito Federal e dos Territórios e dos membros do Ministério Público,…
- Interpretação principal: Juízes e membros do Ministério Público que atuam nos Estados não são julgados por um juiz de primeiro grau quando acusados de crime: o processo corre no Tribunal de…
- ATENÇÃO: O inciso trata dos juízes e do Ministério Público ligados aos Estados e ao Distrito Federal; juízes federais e membros do Ministério Público da União seguem outra regra (art. 108, I, a).
- Dependência externa: nenhuma
- Warnings: lint PARENT_REPETITION, lint TERM_NOT_USED
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.97` — Art. 97 — Cláusula de reserva de plenário

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: As hipóteses em que o órgão fracionário pode deixar de…
- Ponto jurídico: O art. 97 exige o voto da maioria absoluta dos membros do tribunal, ou dos membros do seu órgão especial, para que o tribunal reconheça que uma lei ou um ato normativo do poder público é…
- Interpretação principal: É a chamada cláusula de reserva de plenário.
- ATENÇÃO: O artigo se dirige aos tribunais e não trata da decisão do juiz de primeiro grau.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.100:PAR.1` — Art. 100, §§ 1º e 2º — Créditos alimentares e superpreferência

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: A forma de verificação da idade e dos demais requisitos da…
- Ponto jurídico: O § 1º define os débitos de natureza alimentícia: os que decorrem de relação de trabalho ou previdenciária, mesmo de natureza tributária, inclusive a devolução de tributo cobrado indevidamente sobre…
- Interpretação principal: Há três níveis na fila.
- ATENÇÃO: Doença grave e deficiência são definidas na forma da lei.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: portadores de doença grave ou pessoas com…), NUMBER_FROM_OTHER_DEVICE(70 anos), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.100:PAR.6` — Art. 100, §§ 6º e 7º — Sequestro de verbas e responsabilidade do Presidente do Tribunal

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crime
- Ponto jurídico: O § 6º determina que as verbas para precatórios sejam entregues diretamente ao Judiciário e que o Presidente do Tribunal que proferiu a decisão determine o pagamento integral.
- Interpretação principal: O dinheiro dos precatórios não fica com o devedor: é repassado ao Judiciário, que controla os pagamentos.
- ATENÇÃO: Fora das duas hipóteses do § 6º, o sequestro não é autorizado por este parágrafo.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: ou tentar frustrar a liquidação regular de…)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.102:INC.I` — Art. 102, inciso I — Competência originária do Supremo

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: O alcance do foro por prerrogativa de função e o momento em…; SENSITIVE_THEME: crimes
- Ponto jurídico: O inciso I lista as causas que o Supremo Tribunal Federal processa e julga originariamente.
- Interpretação principal: As alíneas podem ser lidas em grupos.
- ATENÇÃO: A ressalva da alínea c remete ao art. 52, I: quando o crime de responsabilidade de Ministro de Estado ou de Comandante militar for conexo com o do Presidente, o julgamento cabe ao Senado.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: ações contra o conselho nacional de justiça e), NEAR_COPY_MICROFIX(o_que_significa: a revisão criminal e a ação rescisória de), lint JURISPRUDENCE_WORDING_IN_BODY, lint LONG_EXPLANATION
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY, SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.103` — Art. 103 — Quem pode propor as ações de controle

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: O requisito de pertinência temática para certos legitimados é…
- Ponto jurídico: O art. 103 indica quem tem legitimidade para a ação direta de inconstitucionalidade e para a declaratória de constitucionalidade: o Presidente da República; a Mesa do Senado Federal; a Mesa da Câmara…
- Interpretação principal: Essas ações não podem ser propostas por qualquer pessoa.
- ATENÇÃO: O texto não diz se todos os legitimados podem questionar qualquer norma.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: confederação sindical ou entidade de classe de…), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.103:PAR.1` — Art. 103, §§ 1º e 3º — Procurador-Geral e Advogado-Geral nas ações de controle

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: O alcance do dever de defesa do Advogado-Geral da União é…
- Ponto jurídico: O § 1º determina que o Procurador-Geral da República seja ouvido antes da decisão nas ações de inconstitucionalidade e, de modo geral, nos processos de competência do Supremo.
- Interpretação principal: Os dois parágrafos colocam duas figuras diferentes no processo de controle.
- ATENÇÃO: O § 3º fala em defesa do ato impugnado.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.103-A:PAR.3` — Art. 103-A, § 3º — Reclamação contra descumprimento do enunciado vinculante

- Risco: MEDIUM · complexidade: EXTERNAL · SENSITIVE_THEME: cassa
- Ponto jurídico: O § 3º prevê reclamação ao Supremo Tribunal Federal contra ato administrativo ou decisão judicial que contrariar o enunciado vinculante aplicável ou que o aplicar indevidamente.
- Interpretação principal: A reclamação é o instrumento que dá força prática ao efeito vinculante.
- ATENÇÃO: A lei pode exigir etapas prévias para a reclamação contra atos da administração.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: outra seja proferida com ou sem a aplicação)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.103-B` — Art. 103-B — Conselho Nacional de Justiça

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: sanções
- Ponto jurídico: O art. 103-B estabelece que o Conselho Nacional de Justiça tem quinze membros, com mandato de dois anos e uma recondução admitida.
- Interpretação principal: O Conselho é um órgão do Judiciário que não julga processos.
- ATENÇÃO: As competências do Conselho (§ 4º) têm explicação própria.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: cidadãos de notável saber jurídico e reputação…)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.103-B:PAR.4` — Art. 103-B, § 4º — Competências do Conselho Nacional de Justiça

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: Os limites do poder regulamentar do Conselho são tema da…; SENSITIVE_THEME: sanções
- Ponto jurídico: O § 4º dá ao Conselho duas tarefas de controle: a gestão administrativa e financeira dos tribunais e o cumprimento, pelos juízes, dos seus deveres funcionais.
- Interpretação principal: O parágrafo mostra que o Conselho atua em duas frentes.
- ATENÇÃO: As competências são administrativas e disciplinares.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NEAR_COPY_MICROFIX(o_que_significa: da competência do tribunal de contas da união)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY, SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.105` — Art. 105 — Competências do Superior Tribunal de Justiça

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crimes
- Ponto jurídico: O art. 105 atribui ao Superior Tribunal de Justiça três tipos de competência.
- Interpretação principal: O artigo reúne as competências do tribunal em três vias.
- ATENÇÃO: O recurso especial e o filtro de relevância (inciso III e §§ 2º e 3º) têm explicação própria.
- Dependência externa: nenhuma
- Warnings: DUPLICATION(resolvido)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.105:INC.III` — Art. 105, inciso III — Recurso especial

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: O cabimento de recurso especial contra decisões de turmas…
- Ponto jurídico: O inciso III atribui ao Superior Tribunal de Justiça o julgamento, por recurso especial, das causas que os Tribunais Regionais Federais e os tribunais dos Estados, do Distrito Federal e dos…
- Interpretação principal: O recurso especial é o caminho para levar ao Superior Tribunal de Justiça uma questão sobre lei federal.
- ATENÇÃO: O recurso especial cuida de lei federal; a questão constitucional vai ao Supremo por recurso extraordinário.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: DUPLICATION(resolvido)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.108` — Art. 108 — Competências dos Tribunais Regionais Federais

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crimes
- Ponto jurídico: O art. 108 atribui aos Tribunais Regionais Federais o julgamento originário, por crimes comuns e de responsabilidade, dos juízes federais da sua área (incluídos os juízes militares e os do trabalho)…
- Interpretação principal: O tribunal regional tem duas funções.
- ATENÇÃO: A competência penal originária tem ressalva expressa: os casos da competência da Justiça Eleitoral ficam fora.
- Dependência externa: nenhuma
- Warnings: DUPLICATION(resolvido)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.109` — Art. 109 — Competências dos juízes federais

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crimes
- Ponto jurídico: O art. 109 lista as causas que os juízes federais processam e julgam.
- Interpretação principal: A lógica do artigo é o interesse federal.
- ATENÇÃO: Os incisos I e IV têm exceções importantes e explicação própria.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a bordo de navios ou aeronaves ressalvada a)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.109:INC.I` — Art. 109, inciso I — Causas cíveis de interesse da União

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: A competência para causas de sociedades de economia mista e…
- Ponto jurídico: O inciso I atribui aos juízes federais as causas de que participem, como autoras, rés, assistentes ou oponentes, a União, uma autarquia federal ou uma empresa pública federal.
- Interpretação principal: O critério é a pessoa que está no processo, e não o assunto.
- ATENÇÃO: A participação da entidade federal precisa ocorrer em uma das posições listadas.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.109:INC.IV` — Art. 109, inciso IV — Crimes de competência federal

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crimes
- Ponto jurídico: O inciso IV atribui aos juízes federais os crimes políticos e as infrações penais praticadas contra bens, serviços ou interesse da União, de suas autarquias ou de suas empresas públicas.
- Interpretação principal: No campo penal, a Justiça Federal julga o que ofende diretamente a União ou suas entidades.
- ATENÇÃO: O texto menciona empresas públicas, e não sociedades de economia mista.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: os crimes políticos e as infrações penais…), lint JURISPRUDENCE_WORDING_IN_BODY, lint PARENT_REPETITION
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.109:PAR.1` — Art. 109, §§ 1º e 2º — Onde propor as ações da União

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: A aplicação do § 2º a autarquias federais é tema da camada…
- Ponto jurídico: O § 1º determina que as causas em que a União for autora sejam propostas na seção judiciária do domicílio da outra parte.
- Interpretação principal: Os dois parágrafos protegem a parte que litiga contra a União.
- ATENÇÃO: No § 2º, a escolha é do autor da ação; no § 1º, o local é fixo.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: as causas em que a união for autora)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.109:PAR.5` — Art. 109, § 5º — Deslocamento de competência por violação de direitos humanos

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: Os requisitos aplicados para deferir o deslocamento de…
- Ponto jurídico: O § 5º permite que, em caso de violação grave de direitos humanos, o Procurador-Geral da República peça ao Superior Tribunal de Justiça, em qualquer fase do inquérito ou do processo, o deslocamento…
- Interpretação principal: O parágrafo cria uma via excepcional para levar à Justiça Federal casos que, pelas regras comuns de competência, não estariam nela.
- ATENÇÃO: O texto exige grave violação de direitos humanos e a finalidade de cumprir obrigações de tratados.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: de direitos humanos o procurador geral da…), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.125` — Art. 125 — Justiça dos Estados

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crimes
- Ponto jurídico: O art. 125 determina que os Estados organizem sua Justiça, observados os princípios da Constituição.
- Interpretação principal: A Justiça estadual é organizada por cada Estado, mas dentro dos limites da Constituição Federal.
- ATENÇÃO: O controle de constitucionalidade estadual (§ 2º) e a Justiça Militar estadual (§§ 3º a 5º) têm explicações próprias.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.125:PAR.3` — Art. 125, §§ 3º, 4º e 5º — Justiça Militar estadual

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: Os crimes abrangidos pela ressalva do júri e a distribuição…; SENSITIVE_THEME: crimes
- Ponto jurídico: O § 3º permite que a lei estadual, por proposta do Tribunal de Justiça, crie a Justiça Militar estadual.
- Interpretação principal: A Justiça Militar estadual julga policiais militares e bombeiros militares dos Estados.
- ATENÇÃO: A ressalva do júri vale quando a vítima é civil; a delimitação dos crimes abrangidos é da lei e da camada JURISPRUDÊNCIA.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NEAR_COPY_MICROFIX(o_que_significa: crimes militares definidos em lei e as ações), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY, SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

