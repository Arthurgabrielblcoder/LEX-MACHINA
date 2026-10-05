# MACRO07 — REVISÃO COMPACTA (filas A e B)

Lote `ENTENDA_CF_MACRO_BATCH_07` · 2026-10-05 · nenhum item aprovado (AUTO_APPROVE_LOW/MEDIUM = OFF). Revisão humana obrigatória em formato compacto; T1 completo só sob pedido. Risco = LEGAL_RISK; complexidade = VERIFICATION_COMPLEXITY.

## A — CLEAN_LOW (143)

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
- Interpretação principal: Os três parágrafos completam o regime da autonomia financeira.
- ATENÇÃO: A ressalva do § 5º exige autorização prévia: créditos suplementares ou especiais não podem ser abertos depois que a despesa já foi feita.
- Dependência externa: nenhuma
- Warnings: DUPLICATION(resolvido), DUPLICATION(resolvido), lint PARENT_REPETITION
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
- Warnings: NUMBER_FROM_OTHER_DEVICE(20% )
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.100:PAR.23` — Art. 100, §§ 23 e 24 — Limites anuais de pagamento de Estados, Distrito Federal e Municípios

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O § 23 limita os pagamentos anuais de precatórios dos Estados, do Distrito Federal e dos Municípios a um percentual da receita corrente líquida do exercício anterior.
- Interpretação principal: Em vez de quitar o estoque de uma só vez, esses entes pagam até um teto anual ligado à sua receita.
- ATENÇÃO: As faixas, os percentuais e a data de 2036 constam do texto atual, mas a sistemática foi introduzida recentemente por emenda; a transição entre regimes deve ser consultada na camada externa.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a partir de 1 de janeiro de 2036), NUMBER_FROM_OTHER_DEVICE(30% ), lint EXAMPLE_REQUIREMENT_LANGUAGE
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

### `CF88:ART.126` — Art. 126 — Varas agrárias

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 126 determina que, para resolver conflitos fundiários, o Tribunal de Justiça proponha a criação de varas especializadas que cuidem só de questões agrárias.
- Interpretação principal: O artigo prevê juízes dedicados aos conflitos pela posse e pela propriedade da terra no campo.
- ATENÇÃO: O artigo fala em proposta do Tribunal de Justiça.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.127` — Art. 127 — Ministério Público

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 127 define o Ministério Público como instituição permanente e essencial à função jurisdicional do Estado.
- Interpretação principal: O texto qualifica o Ministério Público como instituição permanente e essencial à função jurisdicional, regulada em capítulo próprio, fora dos três Poderes.
- ATENÇÃO: O texto não inclui o Ministério Público em nenhum dos Poderes, mas a sua organização, a lista de funções e as garantias dos membros estão nos arts. 128 e 129.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.127:PAR.1` — Art. 127, § 1º — Princípios institucionais do Ministério Público

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O § 1º indica três princípios que regem a instituição: unidade, indivisibilidade e independência funcional.
- Interpretação principal: A unidade significa que os membros de um mesmo Ministério Público atuam como uma só instituição, sob a mesma chefia.
- ATENÇÃO: A independência funcional protege a convicção do membro, mas não afasta a organização administrativa da instituição.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.127:PAR.2` — Art. 127, § 2º — Autonomia do Ministério Público

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º assegura ao Ministério Público autonomia funcional e administrativa.
- Interpretação principal: A autonomia funcional garante que o Ministério Público exerça suas funções sem subordinação a outro Poder.
- ATENÇÃO: O texto fala em autonomia funcional e administrativa.
- Dependência externa: nenhuma
- Warnings: lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.127:PAR.3` — Art. 127, §§ 3º, 4º, 5º e 6º — Orçamento do Ministério Público

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 3º manda o Ministério Público elaborar a sua proposta orçamentária nos limites da lei de diretrizes orçamentárias.
- Interpretação principal: Os parágrafos combinam autonomia e controle.
- ATENÇÃO: As regras são semelhantes às do Judiciário (art. 99, §§ 3º a 5º).
- Dependência externa: nenhuma
- Warnings: DUPLICATION(resolvido), DUPLICATION(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.128:PAR.1` — Art. 128, §§ 1º e 2º — Procurador-Geral da República

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º estabelece que o Procurador-Geral da República chefia o Ministério Público da União.
- Interpretação principal: A escolha do Procurador-Geral da República combina três elementos: indicação do Presidente, limitada a membros da carreira, aprovação do Senado e mandato fixo.
- ATENÇÃO: O § 1º permite a recondução sem dizer quantas vezes; o § 3º, para os Estados, permite uma recondução.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: da carreira maiores de trinta e cinco anos), EXAMPLE_NUMBER_NOT_IN_TEXT(50), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.129:INC.I` — Art. 129, inciso I — Ação penal pública

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso I atribui ao Ministério Público, de forma privativa, a promoção da ação penal pública, na forma da lei.
- Interpretação principal: Nos crimes de ação penal pública, quem acusa o réu perante o juiz é o Ministério Público.
- ATENÇÃO: A Constituição admite ação privada nos crimes de ação pública quando o Ministério Público não age no prazo legal (art. 5º, LIX).
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.129:INC.III` — Art. 129, inciso III — Inquérito civil e ação civil pública

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O inciso III atribui ao Ministério Público a promoção do inquérito civil e da ação civil pública para proteger o patrimônio público e social, o meio ambiente e outros interesses difusos e coletivos.
- Interpretação principal: O inciso dá ao Ministério Público dois instrumentos para defender interesses que pertencem a muitas pessoas.
- ATENÇÃO: O Ministério Público não é o único legitimado para a ação civil pública: o § 1º preserva a legitimação de terceiros, nos termos da Constituição e da lei.
- Dependência externa: nenhuma
- Warnings: lint PARENT_REPETITION
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.129:INC.VII` — Art. 129, inciso VII — Controle externo da atividade policial

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso VII atribui ao Ministério Público o controle externo da atividade policial, nos termos da lei complementar prevista no art. 128, § 5º.
- Interpretação principal: A polícia tem seus próprios órgãos internos de controle, como as corregedorias.
- ATENÇÃO: O inciso fala em controle externo da atividade policial, e não em comando da polícia.
- Dependência externa: nenhuma
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.129:INC.IX` — Art. 129, inciso IX — Outras funções e vedação de representação judicial

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O inciso IX admite que o Ministério Público receba outras funções, contanto que sejam compatíveis com a sua finalidade.
- Interpretação principal: A lista de funções não é fechada: a lei pode atribuir novas tarefas ao Ministério Público.
- ATENÇÃO: O inciso condiciona as novas funções à compatibilidade com a finalidade da instituição; quem decide sobre essa compatibilidade não está dito no texto.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a representação judicial e a consultoria jurídica…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.129:PAR.2` — Art. 129, § 2º — Exercício por integrantes da carreira e residência

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º reserva as funções do Ministério Público aos integrantes da carreira.
- Interpretação principal: O parágrafo tem duas regras.
- ATENÇÃO: A residência na comarca é a regra, e a autorização do chefe é a exceção prevista no próprio texto.
- Dependência externa: nenhuma
- Warnings: lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.131` — Art. 131 — Advocacia-Geral da União

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 131 define a Advocacia-Geral da União como a instituição que representa a União judicial e extrajudicialmente, diretamente ou por órgão vinculado.
- Interpretação principal: A Advocacia-Geral da União é o escritório de advocacia do Estado federal.
- ATENÇÃO: O § 2º tem nota de remissão a lei na fonte oficial.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.132` — Art. 132 — Procuradores dos Estados e do Distrito Federal

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 132 atribui a representação judicial e a consultoria jurídica dos Estados e do Distrito Federal aos seus Procuradores.
- Interpretação principal: Os procuradores estaduais têm, nos Estados e no Distrito Federal, o papel que a Advocacia-Geral da União tem na esfera federal: defendem o ente em juízo e lhe dão…
- ATENÇÃO: O artigo fala em Estados e Distrito Federal.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: participação da ordem dos advogados do brasil em), NEAR_COPY_MICROFIX(o_que_significa: da ordem dos advogados do brasil em todas), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.134` — Art. 134 — Defensoria Pública

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 134 define a Defensoria Pública como instituição permanente, essencial à função jurisdicional do Estado.
- Interpretação principal: O texto apresenta a Defensoria como expressão e instrumento do regime democrático, ligada ao direito à assistência jurídica gratuita do art. 5º, LXXIV.
- ATENÇÃO: O texto fala em necessitados, na forma do art. 5º, LXXIV, que exige comprovação de insuficiência de recursos.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: instituição permanente essencial à função…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.134:PAR.2` — Art. 134, §§ 2º e 3º — Autonomia das Defensorias Públicas

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º garante às Defensorias Públicas dos Estados autonomia funcional e administrativa.
- Interpretação principal: A autonomia funcional significa que a Defensoria exerce suas funções sem subordinação ao Executivo.
- ATENÇÃO: A remissão ao art. 99, § 2º, trata do encaminhamento da proposta orçamentária.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: defensorias públicas da união e do distrito…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.135` — Art. 135 — Remuneração das carreiras jurídicas

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 135 determina que os servidores das carreiras disciplinadas nas Seções II e III do Capítulo sejam remunerados na forma do art. 39, § 4º.
- Interpretação principal: O artigo alcança as carreiras disciplinadas nas Seções II e III do Capítulo das funções essenciais à Justiça, como a advocacia pública.
- ATENÇÃO: O artigo remete ao art. 39, § 4º.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: das carreiras disciplinadas nas seções ii e iii), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.136:PAR.1` — Art. 136, § 1º — Medidas do estado de defesa

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O § 1º exige que o decreto do estado de defesa fixe o tempo de duração, especifique as áreas abrangidas e indique, nos termos e limites da lei, as medidas coercitivas que vão vigorar, escolhidas…
- Interpretação principal: O decreto não é um cheque em branco.
- ATENÇÃO: As medidas são aplicadas nos termos e limites da lei.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: nos termos e limites da lei as medidas), NUMBER_FROM_OTHER_DEVICE(15 dias)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.136:PAR.4` — Art. 136, §§ 4º, 5º, 6º e 7º — Controle do estado de defesa pelo Congresso

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 4º determina que o Presidente, em até vinte e quatro horas depois de decretar o estado de defesa ou sua prorrogação, envie o ato e a justificação ao Congresso Nacional, que decide por maioria…
- Interpretação principal: No estado de defesa, o controle do Congresso vem depois do decreto.
- ATENÇÃO: A maioria absoluta do § 4º é exigida para a decisão do Congresso.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.137` — Art. 137 — Estado de sítio

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 137 permite que o Presidente da República, depois de ouvir os Conselhos da República e de Defesa Nacional, peça ao Congresso Nacional autorização para decretar o estado de sítio.
- Interpretação principal: O estado de sítio é mais grave que o estado de defesa, e por isso o controle é mais rigoroso.
- ATENÇÃO: Sem autorização prévia do Congresso, o estado de sítio não pode ser decretado.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: ao congresso nacional autorização para decretar o…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.138` — Art. 138 — Decreto e funcionamento no estado de sítio

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 138 exige que o decreto do estado de sítio indique sua duração, as normas necessárias para a execução e as garantias constitucionais que ficarão suspensas.
- Interpretação principal: Assim como no estado de defesa, o decreto precisa ser claro sobre o que muda.
- ATENÇÃO: A duração tem regras diferentes conforme a hipótese (§ 1º, com explicação própria).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: executor das medidas específicas e as áreas…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.138:PAR.1` — Art. 138, § 1º — Duração do estado de sítio

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º estabelece que, na hipótese do art. 137, I, o estado de sítio não pode ser decretado por mais de trinta dias, nem prorrogado, a cada vez, por prazo maior.
- Interpretação principal: A duração depende da causa.
- ATENÇÃO: Diferentemente do estado de defesa, o texto não limita o número de prorrogações no caso de comoção grave; limita a duração de cada uma.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: decretado por mais de trinta dias nem prorrogado)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.140` — Art. 140 — Comissão de acompanhamento

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 140 determina que a Mesa do Congresso Nacional, depois de ouvir os líderes partidários, forme uma Comissão com cinco parlamentares encarregada de acompanhar e fiscalizar como são executadas as…
- Interpretação principal: Além de autorizar ou aprovar as medidas, o Congresso acompanha de perto a sua execução.
- ATENÇÃO: A comissão acompanha e fiscaliza; o texto não lhe dá poder de suspender sozinha as medidas.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.141` — Art. 141 — Fim dos estados de defesa e de sítio

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 141 estabelece que, terminado o estado de defesa ou o estado de sítio, cessam também os seus efeitos, sem prejuízo da responsabilidade pelos ilícitos cometidos por executores ou agentes.
- Interpretação principal: Quando a medida termina, as restrições também terminam.
- ATENÇÃO: A responsabilidade alcança executores e agentes que cometeram ilícitos.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: com relação nominal dos atingidos e indicação das), lint TERM_LOW_UTILITY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.143` — Art. 143 — Serviço militar

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 143 torna o serviço militar obrigatório, nos termos da lei.
- Interpretação principal: A regra geral é a obrigatoriedade, nos termos da lei.
- ATENÇÃO: A recusa a cumprir também o serviço alternativo tem consequências previstas no art. 5º, VIII, e no art. 15, IV, que tratam da privação ou suspensão de direitos.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a outros encargos que a lei lhes atribuir)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.144` — Art. 144 — Segurança pública

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 144 define a segurança pública como dever do Estado, direito e responsabilidade de todos, exercida para preservar a ordem pública e a incolumidade das pessoas e do patrimônio.
- Interpretação principal: A segurança pública é tarefa do Estado, mas o texto também fala em responsabilidade de todos.
- ATENÇÃO: Os Municípios não estão na lista de órgãos do caput; eles podem criar guardas municipais (§ 8º, com explicação própria).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: dever do estado direito e responsabilidade de…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.144:PAR.1` — Art. 144, § 1º — Polícia federal

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O § 1º descreve a polícia federal como órgão permanente, instituído por lei, organizado e mantido pela União e estruturado em carreira.
- Interpretação principal: A polícia federal investiga os crimes que interessam à União.
- ATENÇÃO: A investigação de crimes com repercussão interestadual depende do que dispuser a lei.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: as funções de polícia marítima aeroportuária e de), NEAR_COPY_MICROFIX(o_que_significa: com exclusividade as funções de polícia…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.144:PAR.4` — Art. 144, § 4º — Polícias civis

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 4º confia às polícias civis, dirigidas por delegados de polícia de carreira, a função de polícia judiciária e a investigação de infrações penais.
- Interpretação principal: A polícia civil é a polícia de investigação dos Estados e do Distrito Federal.
- ATENÇÃO: As duas ressalvas do texto são a competência da União e as infrações militares.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: civis dirigidas por delegados de polícia de…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.144:PAR.5` — Art. 144, §§ 5º e 5º-A — Polícias militares, bombeiros e polícias penais

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 5º atribui às polícias militares a polícia ostensiva e a preservação da ordem pública, e aos corpos de bombeiros militares a execução de atividades de defesa civil, somadas às tarefas que a lei…
- Interpretação principal: Os dois parágrafos tratam das forças que atuam de forma preventiva ou em áreas específicas.
- ATENÇÃO: O § 6º, explicado na visão geral, subordina essas forças aos Governadores e qualifica as polícias militares e os bombeiros como forças auxiliares e reserva do Exército.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a polícia ostensiva e a preservação da ordem)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.145` — Art. 145 — Espécies de tributos e princípios do sistema

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 145 permite que a União, os Estados, o Distrito Federal e os Municípios instituam impostos, taxas e contribuição de melhoria.
- Interpretação principal: O artigo apresenta três espécies de tributos que a União, os Estados, o Distrito Federal e os Municípios podem criar, cada um dentro da sua competência e nos termos da…
- ATENÇÃO: O artigo não esgota as espécies tributárias da Constituição: há também empréstimos compulsórios e contribuições (arts. 148 e 149).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a união os estados o distrito federal e), NEAR_COPY_MICROFIX(o_que_significa: a união os estados o distrito federal e)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.145:PAR.1` — Art. 145, § 1º — Capacidade contributiva

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º determina que os impostos, quando possível, tenham caráter pessoal e sejam graduados conforme a capacidade econômica do contribuinte.
- Interpretação principal: O parágrafo expressa a ideia de que quem tem mais deve contribuir mais.
- ATENÇÃO: O texto fala em impostos.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: o patrimônio os rendimentos e as atividades…), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.146` — Art. 146 — Papel da lei complementar tributária

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 146 atribui à lei complementar três funções em matéria tributária: dispor sobre conflitos de competência entre os entes federativos, regular as limitações constitucionais ao poder de tributar…
- Interpretação principal: A lei complementar funciona como uma ponte entre a Constituição e as leis de cada ente.
- ATENÇÃO: O inciso III e o regime único (§§ 1º a 3º) têm explicações próprias.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: regular as limitações constitucionais ao poder de…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.146:INC.III` — Art. 146, inciso III — Normas gerais de legislação tributária

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso III reserva à lei complementar as normas gerais de legislação tributária, especialmente sobre: definição de tributos e espécies e, quanto aos impostos discriminados na Constituição, seus…
- Interpretação principal: O inciso indica temas que precisam de tratamento uniforme no país.
- ATENÇÃO: As alíneas c e d mencionam também os tributos dos arts. 156-A e 195, V, incluídos por emenda recente, com regras de transição na camada externa.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.146-A` — Art. 146-A — Tributação e concorrência

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 146-A autoriza a lei complementar a criar critérios especiais de tributação para prevenir desequilíbrios na concorrência, sem prejuízo da competência da União para, por lei, editar normas com…
- Interpretação principal: O tributo pode afetar a concorrência entre empresas.
- ATENÇÃO: O artigo é permissivo: a lei complementar pode criar os critérios, mas o texto não diz quais são.
- Dependência externa: nenhuma
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.147` — Art. 147 — Impostos nos Territórios e no Distrito Federal

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 147 atribui à União, nos Territórios Federais, os impostos estaduais e, se o Território não estiver dividido em Municípios, também os impostos municipais.
- Interpretação principal: O artigo resolve quem cobra impostos em situações especiais da Federação.
- ATENÇÃO: A competência do Distrito Federal para os impostos estaduais está em outros dispositivos (art. 155).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: impostos municipais ao distrito federal cabem os…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.148` — Art. 148 — Empréstimos compulsórios

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 148 permite que a União, por lei complementar, institua empréstimos compulsórios em duas hipóteses: para cobrir despesas extraordinárias que decorram de calamidade pública ou de guerra…
- Interpretação principal: O empréstimo compulsório é um tributo que o Estado cobra com a promessa de devolver depois.
- ATENÇÃO: A regra de devolução e suas condições ficam na lei complementar que instituir o empréstimo.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: urgente e de relevante interesse nacional…), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.149` — Art. 149 — Contribuições especiais

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 149 reserva somente à União a criação de três tipos de contribuição: sociais, de intervenção no domínio econômico, e as de interesse de categorias profissionais ou econômicas.
- Interpretação principal: As contribuições são tributos ligados a uma finalidade.
- ATENÇÃO: A contribuição para iluminação pública é municipal e está em outro artigo (art. 149-A).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: arts 146 iii e 150 i e iii), NEAR_COPY_MICROFIX(o_que_significa: a união os estados o distrito federal e)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.149:PAR.1` — Art. 149, §§ 1º, 1º-A, 1º-B e 1º-C — Contribuição previdenciária dos servidores

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O § 1º determina que a União, os Estados, o Distrito Federal e os Municípios instituam, por lei, contribuições para custear o regime próprio de previdência, cobradas dos servidores ativos,…
- Interpretação principal: Os servidores com regime próprio contribuem para sua previdência, inclusive depois de aposentados.
- ATENÇÃO: A contribuição extraordinária do § 1º-B está prevista no âmbito da União.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a união os estados o distrito federal e)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.149:PAR.2` — Art. 149, § 2º — Incidência das contribuições sociais e de intervenção

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º estabelece três regras para as contribuições sociais e de intervenção no domínio econômico do caput.
- Interpretação principal: O parágrafo define três pontos.
- ATENÇÃO: O parágrafo trata das contribuições sociais e de intervenção do caput, e não das contribuições de interesse de categorias.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: as contribuições sociais e de intervenção no…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.149-A` — Art. 149-A — Contribuição de iluminação pública

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 149-A permite que os Municípios e o Distrito Federal instituam, por suas leis, contribuição para custear, expandir e melhorar o serviço de iluminação pública e sistemas de monitoramento para a…
- Interpretação principal: A iluminação pública beneficia todos ao mesmo tempo, e não é possível medir quanto cada pessoa usa.
- ATENÇÃO: A contribuição é municipal e distrital.
- Dependência externa: nenhuma
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.150:INC.I` — Art. 150, inciso I — Legalidade tributária

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O inciso I proíbe exigir ou aumentar tributo sem lei que o estabeleça.
- Interpretação principal: É o princípio da legalidade tributária.
- ATENÇÃO: A própria Constituição admite que o Executivo altere alíquotas de alguns tributos, nas condições e limites da lei (art. 153, § 1º, por exemplo).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: exigir ou aumentar tributo sem lei que o), lint EXAMPLE_REQUIREMENT_LANGUAGE, lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.150:INC.III` — Art. 150, inciso III — Irretroatividade e anterioridade

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso III impede a cobrança de tributos em três situações: sobre fatos geradores anteriores à entrada em vigor da lei que os criou ou aumentou (alínea a); no mesmo exercício financeiro em que essa…
- Interpretação principal: O inciso protege o contribuinte contra surpresas.
- ATENÇÃO: Há tributos que não seguem a alínea b, a alínea c ou ambas: as exceções estão no § 1º, com explicação própria.
- Dependência externa: nenhuma
- Warnings: lint PARENT_REPETITION
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.150:PAR.1` — Art. 150, § 1º — Exceções à anterioridade

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º indica tributos que não seguem as anterioridades.
- Interpretação principal: O parágrafo libera alguns tributos de uma ou de ambas as esperas.
- ATENÇÃO: A leitura do parágrafo depende de cruzar os números com os artigos citados.
- Dependência externa: nenhuma
- Warnings: lint PARENT_REPETITION
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.150:PAR.6` — Art. 150, § 6º — Lei específica para benefícios fiscais

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 6º exige lei específica para conceder subsídio, isenção, redução de base de cálculo, crédito presumido, anistia ou remissão em impostos, taxas ou contribuições.
- Interpretação principal: Benefícios fiscais significam receita que o Estado deixa de arrecadar.
- ATENÇÃO: A exigência alcança impostos, taxas e contribuições.
- Dependência externa: nenhuma
- Warnings: lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.152` — Art. 152 — Vedação de diferença pela origem ou pelo destino

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 152 proíbe os Estados, o Distrito Federal e os Municípios de estabelecer diferença tributária entre bens e serviços, de qualquer natureza, por causa da sua procedência ou do seu destino.
- Interpretação principal: Um Estado não pode cobrar mais imposto sobre um produto só porque ele veio de outro Estado, nem cobrar menos para favorecer o que é produzido dentro do seu território.
- ATENÇÃO: As alíquotas interestaduais do imposto estadual sobre circulação de mercadorias seguem regras próprias da Constituição (art. 155, § 2º), que não se confundem com a diferença proibida por este artigo.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: diferença tributária entre bens e serviços de…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.153:PAR.1` — Art. 153, § 1º — Alteração de alíquotas pelo Executivo

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O § 1º faculta ao Poder Executivo alterar as alíquotas dos impostos dos incisos I, II, IV e V, atendidas as condições e os limites estabelecidos em lei.
- Interpretação principal: Em regra, alterar a alíquota de um tributo exige lei (art. 150, I).
- ATENÇÃO: A faculdade alcança apenas os quatro impostos indicados.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: as condições e os limites estabelecidos em lei), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.153:PAR.4` — Art. 153, § 4º — Imposto territorial rural

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 4º estabelece que o imposto sobre a propriedade territorial rural será progressivo, com alíquotas fixadas para desestimular a manutenção de propriedades improdutivas.
- Interpretação principal: O imposto rural tem uma função ligada ao uso da terra.
- ATENÇÃO: O tamanho da pequena gleba é definido em lei.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: incidirá sobre pequenas glebas rurais definidas…), lint TERM_LOW_UTILITY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.153:PAR.5` — Art. 153, § 5º — Ouro como ativo financeiro

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O § 5º determina que o ouro, quando a lei o definir como ativo financeiro ou instrumento cambial, sofra apenas o imposto do inciso V, devido na operação de origem, com alíquota mínima de um por cento.
- Interpretação principal: O ouro pode ser mercadoria ou ativo financeiro.
- ATENÇÃO: A regra só vale quando a lei define o ouro como ativo financeiro ou instrumento cambial.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.154` — Art. 154 — Competência residual e impostos de guerra

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 154 permite à União criar, por lei complementar, impostos além dos previstos no art. 153.
- Interpretação principal: A lista de impostos federais do art. 153 não é totalmente fechada.
- ATENÇÃO: Os impostos extraordinários de guerra não seguem as regras de anterioridade (art. 150, § 1º).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: extraordinários compreendidos ou não em sua…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.155:PAR.1` — Art. 155, § 1º — Imposto sobre heranças e doações

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º estabelece regras para o imposto sobre transmissão causa mortis e doação.
- Interpretação principal: O parágrafo resolve qual Estado cobra o imposto.
- ATENÇÃO: A progressividade e as novas não incidências foram incluídas por emenda recente; a aplicação no tempo segue as regras da camada externa.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: valor do quinhão do legado ou da doação)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.155:PAR.2:INC.X` — Art. 155, § 2º, inciso X — Não incidências do imposto sobre circulação de mercadorias

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso X afasta o imposto em quatro casos: nas operações que destinem mercadorias ao exterior e nos serviços a destinatários no exterior, mantido e aproveitado o imposto cobrado nas operações e…
- Interpretação principal: O inciso afasta o imposto em quatro situações.
- ATENÇÃO: A alínea b se refere à saída para outros Estados.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.155:PAR.3` — Art. 155, § 3º — Impostos sobre energia, telecomunicações e combustíveis

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 3º limita os impostos sobre certos setores.
- Interpretação principal: O parágrafo limita os impostos que podem recair sobre esses setores.
- ATENÇÃO: A limitação fala em impostos.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: derivados de petróleo combustíveis e minerais do…), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.155:PAR.4` — Art. 155, §§ 4º e 5º — Incidência única sobre combustíveis

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 4º regula a incidência única sobre combustíveis e lubrificantes definida em lei complementar (§ 2º, XII, h).
- Interpretação principal: Os combustíveis têm um regime especial: o imposto é cobrado uma única vez na cadeia.
- ATENÇÃO: O regime depende da lei complementar que define os combustíveis de incidência única.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.156-B:PAR.3` — Art. 156-B, §§ 3º e 4º — Composição e deliberação do Comitê Gestor

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 3º compõe a instância máxima de deliberação do Comitê Gestor com vinte e sete membros, um por Estado e um pelo Distrito Federal, e outros vinte e sete que representam o conjunto dos Municípios e…
- Interpretação principal: A composição é paritária: metade dos membros representa os Estados, metade os Municípios.
- ATENÇÃO: As duas maiorias são cumulativas.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: o conjunto dos municípios e do distrito federal)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.157` — Art. 157 — Receitas tributárias dos Estados vindas da União

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 157 atribui aos Estados e ao Distrito Federal o produto da arrecadação do imposto da União sobre a renda e proventos de qualquer natureza retido na fonte sobre rendimentos que eles, suas…
- Interpretação principal: O artigo inicia a repartição das receitas tributárias, em que parte do que um ente arrecada pertence a outro.
- ATENÇÃO: O texto fala em rendimentos pagos pelo Estado, por suas autarquias e pelas fundações que instituir e mantiver.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: o produto da arrecadação do imposto da união), lint JURISPRUDENCE_WORDING_IN_BODY, lint TERM_NOT_USED
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.159` — Art. 159 — Entregas da União aos Estados e Municípios

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 159 determina que a União entregue parte da arrecadação de impostos e contribuições.
- Interpretação principal: Além das receitas que pertencem diretamente aos Estados e Municípios, a União divide com eles parte do que arrecada.
- ATENÇÃO: O inciso I tem explicação própria.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: do imposto sobre produtos industrializados e do…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.160` — Art. 160 — Vedação de retenção das receitas repartidas

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 160 proíbe a retenção ou qualquer restrição à entrega e ao uso dos recursos que a Seção atribui aos Estados, ao Distrito Federal e aos Municípios, incluídos adicionais e acréscimos relativos a…
- Interpretação principal: As receitas repartidas pertencem aos Estados e aos Municípios.
- ATENÇÃO: As hipóteses de condicionamento estão nos §§ 1º e 2º, com explicação própria.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a retenção ou qualquer restrição à entrega e)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.160:PAR.1` — Art. 160, §§ 1º e 2º — Condicionamento e dedução dos repasses

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º permite que a União e os Estados condicionem a entrega de recursos ao pagamento de seus créditos, inclusive de suas autarquias, e ao cumprimento dos mínimos de aplicação em saúde do art. 198,…
- Interpretação principal: A proibição de retenção do caput tem dois limites.
- ATENÇÃO: As hipóteses são as do texto: créditos do ente que repassa, mínimos de saúde e cláusulas de dedução em ajustes com a União.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: ao pagamento de seus créditos inclusive de suas), lint TERM_LOW_UTILITY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.161` — Art. 161 — Lei complementar da repartição de receitas

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 161 atribui à lei complementar definir valor adicionado para fins do art. 158, § 1º, I; estabelecer normas sobre a entrega dos recursos do art. 159, especialmente os critérios de rateio dos…
- Interpretação principal: A Constituição fixa quanto é repartido, mas deixa para a lei complementar os detalhes de como dividir.
- ATENÇÃO: Os critérios concretos de rateio estão na lei complementar, e não neste artigo.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.162` — Art. 162 — Divulgação da arrecadação e dos repasses

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 162 obriga a União, os Estados, o Distrito Federal e os Municípios a divulgar dados sobre os tributos até o último dia do mês seguinte ao da arrecadação.
- Interpretação principal: O artigo impõe transparência sobre o dinheiro dos tributos e sua divisão entre os entes.
- ATENÇÃO: O dever alcança os quatro níveis da Federação.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a união os estados o distrito federal e)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.163` — Art. 163 — Lei complementar de finanças públicas

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 163 reserva à lei complementar, entre outras, as seguintes matérias: finanças públicas; dívida pública externa e interna, inclusive das entidades controladas pelo poder público; garantias…
- Interpretação principal: O artigo abre o capítulo das finanças públicas indicando os temas que exigem lei complementar, aprovada por maioria absoluta.
- ATENÇÃO: O artigo indica matérias; o conteúdo concreto está nas leis complementares, na camada de legislação correlata.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: compatibilização das funções das instituições…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.163-A` — Art. 163-A — Dados contábeis e fiscais padronizados

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 163-A determina que a União, os Estados, o Distrito Federal e os Municípios disponibilizem suas informações contábeis, orçamentárias e fiscais conforme periodicidade, formato e sistema…
- Interpretação principal: Cada ente produz suas próprias contas, e sem um padrão comum seria difícil compará-las.
- ATENÇÃO: O padrão é definido por órgão da União, mas o dever de disponibilizar os dados é de cada ente.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a união os estados o distrito federal e), EXAMPLE_NUMBER_NOT_IN_TEXT(2)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.164` — Art. 164 — Banco Central e emissão de moeda

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 164 atribui exclusivamente ao Banco Central a competência da União para emitir moeda.
- Interpretação principal: Só o Banco Central emite moeda em nome da União.
- ATENÇÃO: A proibição do § 1º alcança empréstimos diretos e indiretos.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a oferta de moeda ou a taxa de), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.164-A` — Art. 164-A — Sustentabilidade da dívida pública

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 164-A determina que a União, os Estados, o Distrito Federal e os Municípios conduzam suas políticas fiscais de modo que a dívida pública permaneça em níveis sustentáveis, conforme a lei…
- Interpretação principal: O artigo transforma a sustentabilidade da dívida em dever da União, dos Estados, do Distrito Federal e dos Municípios.
- ATENÇÃO: O artigo depende da lei complementar para ter critérios concretos.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a compatibilidade dos indicadores fiscais com a…), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.165` — Art. 165 — Leis orçamentárias

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 165 determina que leis de iniciativa do Poder Executivo estabeleçam o plano plurianual, as diretrizes orçamentárias e os orçamentos anuais.
- Interpretação principal: O orçamento público é organizado em três leis que se encaixam.
- ATENÇÃO: Os §§ 18 a 22 trazem regras ligadas a exercícios específicos e a emendas recentes, com explicação própria.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.165:PAR.2` — Art. 165, § 2º — Lei de diretrizes orçamentárias

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º estabelece que a lei de diretrizes orçamentárias reúne as metas e prioridades da administração pública federal e define as diretrizes de política fiscal e suas metas, de acordo com uma…
- Interpretação principal: A lei de diretrizes orçamentárias funciona como uma ponte entre o planejamento de médio prazo e o orçamento de cada ano.
- ATENÇÃO: A menção à trajetória sustentável da dívida liga este parágrafo ao art. 163, VIII, e ao art. 164-A.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a política de aplicação das agências financeiras…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.165:PAR.5` — Art. 165, § 5º — Os três orçamentos da lei anual

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 5º determina que a lei orçamentária anual compreenda três orçamentos.
- Interpretação principal: A lei orçamentária anual não é um orçamento único, mas reúne três peças.
- ATENÇÃO: O orçamento de investimento trata das empresas em que a União tem maioria do capital votante, direta ou indiretamente.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: e fundações instituídos e mantidos pelo poder…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.165:PAR.8` — Art. 165, § 8º — Exclusividade da lei orçamentária

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 8º proíbe que a lei orçamentária anual traga dispositivo que não trate de prever a receita e fixar a despesa.
- Interpretação principal: A lei do orçamento tem conteúdo próprio: prever receitas e fixar despesas.
- ATENÇÃO: As autorizações admitidas são apenas as do texto e seguem os termos da lei.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.165:PAR.10` — Art. 165, §§ 10 e 11 — Dever de executar o orçamento

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O § 10 impõe à administração o dever de executar as programações do orçamento, com os meios e medidas necessários, tendo como propósito declarado a efetiva entrega de bens e serviços à sociedade.
- Interpretação principal: O orçamento não é apenas uma autorização para gastar: a administração tem o dever de executá-lo.
- ATENÇÃO: Pelo § 13, o dever do § 10 se aplica exclusivamente aos orçamentos fiscal e da seguridade social da União.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a efetiva entrega de bens e serviços à), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.166:PAR.3` — Art. 166, § 3º — Condições para emendar o orçamento

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O § 3º permite aprovar emendas ao projeto de lei do orçamento anual, ou aos que o modifiquem, apenas em três situações.
- Interpretação principal: O parlamentar pode mudar o orçamento, mas não pode criar despesa do nada.
- ATENÇÃO: Os incisos do texto estão ligados pela conjunção ou; a leitura de quais requisitos são cumulativos deve considerar a redação dos incisos I e II e a camada JURISPRUDÊNCIA.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: ao projeto de lei do orçamento anual ou), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167:INC.IV` — Art. 167, inciso IV — Não vinculação da receita de impostos

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso IV proíbe vincular a receita de impostos a órgão, fundo ou despesa.
- Interpretação principal: A receita dos impostos deve ficar livre para que o orçamento decida, a cada ano, onde aplicá-la.
- ATENÇÃO: As exceções são as do texto.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: 158 e 159 a destinação de recursos para), NUMBER_FROM_OTHER_DEVICE(10% )
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167:PAR.3` — Art. 167, § 3º — Crédito extraordinário

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 3º só admite crédito extraordinário para despesas que sejam ao mesmo tempo imprevisíveis e urgentes, a exemplo das causadas por guerra, comoção interna ou calamidade pública, observado o art. 62.
- Interpretação principal: O crédito extraordinário é a forma mais rápida de abrir uma despesa nova, porque pode ser feito por medida provisória, conforme o art. 62.
- ATENÇÃO: A verificação concreta dos requisitos de imprevisibilidade e urgência é tema da camada JURISPRUDÊNCIA.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: guerra comoção interna ou calamidade pública…), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167:PAR.7` — Art. 167, § 7º — Encargo sem fonte de custeio

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 7º proíbe que a lei imponha ou transfira encargo financeiro gerado pela prestação de serviço público, inclusive despesas de pessoal, à União, aos Estados, ao Distrito Federal ou aos Municípios…
- Interpretação principal: Uma lei não pode criar despesa para outro ente sem dizer de onde virá o dinheiro.
- ATENÇÃO: O alcance da regra sobre pisos salariais nacionais e seus efeitos para os entes é tema da camada JURISPRUDÊNCIA.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: prestação de serviço público inclusive despesas…), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167-A` — Art. 167-A — Mecanismo de ajuste fiscal

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 167-A trata da situação em que, a relação entre despesas correntes e receitas correntes, medida em doze meses, passa de 95% nos Estados, no Distrito Federal e nos Municípios.
- Interpretação principal: O artigo cria um freio para os entes cujas despesas correntes se aproximam do total das receitas correntes.
- ATENÇÃO: No caput, a aplicação é facultativa.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a relação entre despesas correntes e receitas…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167-A:PAR.1` — Art. 167-A, §§ 1º, 2º e 3º — Acionamento antecipado pelo Executivo

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º permite que, quando a despesa corrente superar 85% da receita corrente sem passar do percentual do caput, o Chefe do Poder Executivo implemente as medidas, no todo ou em parte, por atos com…
- Interpretação principal: O bloco permite agir antes de atingir o percentual do caput.
- ATENÇÃO: O prazo de cento e oitenta dias conta para a apreciação pelo Legislativo.
- Dependência externa: nenhuma
- Warnings: EXAMPLE_NUMBER_NOT_IN_TEXT(88%)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167-A:PAR.6` — Art. 167-A, § 6º — Restrições ao ente que não adota o ajuste

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 6º estabelece que, ocorrida a hipótese do caput, até que todos os Poderes e órgãos tenham adotado todas as medidas, conforme declaração do Tribunal de Contas, é vedada a concessão de garantias ao…
- Interpretação principal: A adoção das medidas é facultativa, mas quem não as adota sofre consequências.
- ATENÇÃO: A vedação dura até que todos os Poderes e órgãos tenham adotado todas as medidas, segundo declaração do Tribunal de Contas.
- Dependência externa: nenhuma
- Warnings: lint TERM_LOW_UTILITY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167-C` — Art. 167-C — Contratações simplificadas na calamidade

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 167-C trata do Poder Executivo federal durante a calamidade.
- Interpretação principal: Na calamidade, o governo federal pode contratar com mais rapidez.
- ATENÇÃO: A flexibilização tem finalidade exclusiva e prazo: enfrentar a calamidade, durante a sua duração.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167-D` — Art. 167-D — Dispensa de limitações legais na calamidade

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 167-D trata das proposições legislativas e dos atos do Executivo feitos com o único propósito de enfrentar a calamidade e suas consequências, com vigência e efeitos limitados à sua duração.
- Interpretação principal: As limitações legais mencionadas no texto tratam do aumento de despesa e da renúncia de receita.
- ATENÇÃO: A dispensa não alcança despesa obrigatória de caráter continuado.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167-E` — Art. 167-E — Dispensa da regra de ouro na calamidade

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 167-E dispensa a observância do art. 167, III, durante todo o exercício financeiro em que vigorar a calamidade pública de âmbito nacional.
- Interpretação principal: O art. 167, III, proíbe operações de crédito em montante superior às despesas de capital, a chamada regra de ouro.
- ATENÇÃO: A dispensa vale para todo o exercício financeiro em que vigorar a calamidade, e não apenas para o período da calamidade dentro do ano.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167-F` — Art. 167-F — Operações de crédito e superávit na calamidade

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 167-F estabelece que, durante a calamidade pública nacional, ficam dispensados, durante a integralidade do exercício financeiro, os limites, condições e restrições aplicáveis à União para…
- Interpretação principal: Na calamidade, a União pode contratar empréstimos sem os limites e condições comuns.
- ATENÇÃO: A dispensa de limites de crédito é da União.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: financeiro apurado em 31 de dezembro do ano)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167-G` — Art. 167-G — Vedações de ajuste na calamidade

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 167-G aplica à União, até o fim da calamidade nacional, as vedações do art. 167-A.
- Interpretação principal: Em contrapartida às flexibilizações, a União fica sujeita, durante a calamidade, às mesmas vedações de gastos com pessoal e benefícios do mecanismo de ajuste fiscal.
- ATENÇÃO: As exceções do § 1º valem só para medidas cuja vigência e efeitos não ultrapassem a calamidade.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: aos estados ao distrito federal e aos municípios), lint TERM_LOW_UTILITY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.168` — Art. 168 — Repasse em duodécimos

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 168 garante aos órgãos do Legislativo e do Judiciário, ao Ministério Público e à Defensoria Pública a entrega dos recursos de suas dotações orçamentárias, incluídos os créditos suplementares e…
- Interpretação principal: O Executivo arrecada e administra o caixa.
- ATENÇÃO: O repasse é garantido aos órgãos indicados no texto.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.169:PAR.1` — Art. 169, § 1º — Requisitos para aumentar a despesa com pessoal

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º estabelece que vantagens e aumentos de remuneração, criação de cargos, empregos e funções, alteração de carreiras e admissão ou contratação de pessoal, a qualquer título, por órgãos e…
- Interpretação principal: Antes de aumentar gastos com pessoal, o ente precisa cumprir duas condições.
- ATENÇÃO: A ressalva das empresas estatais vale apenas para a autorização na lei de diretrizes orçamentárias.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: admissão ou contratação de pessoal a qualquer…), NEAR_COPY_MICROFIX(o_que_significa: as empresas públicas e as sociedades de economia), lint EXAMPLE_REQUIREMENT_LANGUAGE, lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.170` — Art. 170 — Princípios da ordem econômica

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 170 apoia a ordem econômica em dois fundamentos, a valorização do trabalho humano e a livre iniciativa, com a finalidade de garantir existência digna a todos, segundo a justiça social.
- Interpretação principal: O artigo abre a parte da Constituição sobre a economia e mostra que ela combina valores diferentes.
- ATENÇÃO: Os princípios convivem e, em casos concretos, precisam ser harmonizados.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: de pequeno porte constituídas sob as leis…), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.170:PAR.UNICO` — Art. 170, parágrafo único — Livre exercício de atividade econômica

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O parágrafo único assegura a todos o livre exercício de qualquer atividade econômica, sem necessidade de autorização de órgãos públicos, exceto nos casos que a lei indicar.
- Interpretação principal: A regra é a liberdade: para abrir um negócio ou exercer uma atividade econômica, a pessoa não precisa pedir licença ao Estado.
- ATENÇÃO: A fonte canônica remete a lei sobre liberdade econômica, que detalha o tema.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a todos o livre exercício de qualquer atividade), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.172` — Art. 172 — Capital estrangeiro

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 172 determina que a lei discipline, com base no interesse nacional, os investimentos de capital estrangeiro, incentive os reinvestimentos e regule a remessa de lucros.
- Interpretação principal: O artigo não proíbe nem libera de forma ampla o capital estrangeiro.
- ATENÇÃO: O artigo é uma remissão à lei.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: base no interesse nacional os investimentos de…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.173` — Art. 173 — Exploração de atividade econômica pelo Estado

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 173 só permite que o Estado explore diretamente atividade econômica quando isso for necessário à segurança nacional ou a relevante interesse coletivo, nos termos definidos em lei, ressalvados…
- Interpretação principal: Na ordem econômica brasileira, a atividade econômica cabe em regra aos particulares.
- ATENÇÃO: O estatuto das estatais (§ 1º) tem explicação própria.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: da empresa pública com o estado e a)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.173:PAR.1` — Art. 173, § 1º — Estatuto jurídico das empresas estatais

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O § 1º determina que a lei crie o estatuto jurídico das empresas públicas, das sociedades de economia mista e de suas subsidiárias que exploram atividade econômica, seja produzindo ou comercializando…
- Interpretação principal: As empresas estatais vivem entre dois mundos: são do Estado, mas atuam no mercado.
- ATENÇÃO: O parágrafo trata das estatais que exploram atividade econômica.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: de economia mista e de suas subsidiárias que), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.174` — Art. 174 — Estado como agente normativo e regulador

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 174 estabelece que o Estado, como agente normativo e regulador da atividade econômica, fiscaliza, incentiva e planeja, na forma da lei, e o planejamento é obrigatório para o setor público e…
- Interpretação principal: Além de atuar como empresário em casos excepcionais (art. 173), o Estado regula a economia.
- ATENÇÃO: A fonte canônica remete o caput a lei sobre liberdade econômica, na camada de legislação correlata.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: como agente normativo e regulador da atividade…), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.175` — Art. 175 — Prestação de serviços públicos

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 175 atribui ao poder público, na forma da lei, a prestação de serviços públicos, diretamente ou sob regime de concessão ou permissão; para a concessão e para a permissão, o texto exige…
- Interpretação principal: O serviço público é responsabilidade do Estado, que pode prestá-lo por conta própria ou transferir a execução a empresas privadas, por concessão ou permissão.
- ATENÇÃO: O texto exige licitação para a concessão e a permissão.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: diretamente ou sob regime de concessão ou…), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

## B — CLEAN_MEDIUM (53)

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
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: cidadãos de notável saber jurídico e reputação…), DUPLICATION(resolvido)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.103-B:PAR.4` — Art. 103-B, § 4º — Competências do Conselho Nacional de Justiça

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: Os limites do poder regulamentar do Conselho são tema da…; SENSITIVE_THEME: sanções
- Ponto jurídico: O § 4º dá ao Conselho duas tarefas de controle: a gestão administrativa e financeira dos tribunais e o cumprimento, pelos juízes, dos seus deveres funcionais.
- Interpretação principal: O parágrafo mostra que o Conselho atua em duas frentes.
- ATENÇÃO: As competências são administrativas e disciplinares.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NEAR_COPY_MICROFIX(o_que_significa: da competência do tribunal de contas da união), DUPLICATION(resolvido), DUPLICATION(resolvido)
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

### `CF88:ART.128` — Art. 128 — Estrutura do Ministério Público

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: perder o cargo
- Ponto jurídico: O art. 128 divide o Ministério Público em Ministério Público da União, que compreende o Federal, o do Trabalho, o Militar e o do Distrito Federal e Territórios, e Ministérios Públicos dos Estados.
- Interpretação principal: Não existe um único Ministério Público, mas vários, cada um com sua chefia.
- ATENÇÃO: O Ministério Público do Distrito Federal e Territórios faz parte do Ministério Público da União.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_significa: a organização as atribuições e o estatuto de)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.128:PAR.3` — Art. 128, §§ 3º e 4º — Procuradores-Gerais nos Estados e no Distrito Federal

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: A autoridade que nomeia e o órgão legislativo que destitui o…
- Ponto jurídico: O § 3º prevê que, nos Estados e no Ministério Público do Distrito Federal e Territórios, a própria carreira forme lista tríplice, na forma da lei respectiva.
- Interpretação principal: Nos Estados, a escolha do chefe do Ministério Público começa dentro da própria instituição: a carreira forma uma lista de três nomes, e o chefe do Executivo escolhe um…
- ATENÇÃO: No caso do Ministério Público do Distrito Federal e Territórios, que integra o Ministério Público da União, o texto não identifica qual chefe do Executivo nomeia nem qual Legislativo delibera a…
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.128:PAR.5` — Art. 128, § 5º — Garantias e vedações dos membros do Ministério Público

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: perder o cargo
- Ponto jurídico: O § 5º determina que leis complementares da União e dos Estados, de iniciativa facultada aos Procuradores-Gerais, definam como cada Ministério Público se organiza, suas atribuições e o estatuto dos…
- Interpretação principal: As garantias protegem o membro do Ministério Público para que possa atuar sem medo de retaliação.
- ATENÇÃO: A irredutibilidade tem ressalvas expressas, como o teto remuneratório e as regras tributárias indicadas no texto.
- Dependência externa: nenhuma
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.130` — Art. 130 — Ministério Público junto aos Tribunais de Contas

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: A autonomia do Ministério Público junto aos Tribunais de…
- Ponto jurídico: O art. 130 estende aos membros do Ministério Público que atuam junto aos Tribunais de Contas as disposições desta Seção sobre direitos, vedações e forma de investidura.
- Interpretação principal: Junto aos Tribunais de Contas atua um Ministério Público especial, que fiscaliza a aplicação da lei nos processos de controle das contas públicas.
- ATENÇÃO: O artigo estende direitos, vedações e investidura.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.130-A` — Art. 130-A — Conselho Nacional do Ministério Público

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: sanções
- Ponto jurídico: O art. 130-A estabelece que o Conselho Nacional do Ministério Público tem quatorze membros, nomeados pelo Presidente da República após aprovação da maioria absoluta do Senado, para mandato de dois…
- Interpretação principal: O Conselho tem para o Ministério Público papel semelhante ao do Conselho Nacional de Justiça para o Judiciário: controla a atuação administrativa e financeira e o…
- ATENÇÃO: As competências do Conselho (§ 2º) têm explicação própria.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: cidadãos de notável saber jurídico e reputação…), NEAR_COPY_MICROFIX(o_que_significa: sem prejuízo da competência dos tribunais de…), DUPLICATION(resolvido)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.130-A:PAR.2` — Art. 130-A, § 2º — Competências do Conselho Nacional do Ministério Público

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: sanções
- Ponto jurídico: O § 2º dá ao Conselho duas tarefas de controle: a gestão administrativa e financeira do Ministério Público e o cumprimento, pelos membros, dos seus deveres funcionais.
- Interpretação principal: O parágrafo repete, para o Ministério Público, o modelo de controle do art. 103-B, § 4º.
- ATENÇÃO: As competências são administrativas e disciplinares.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_significa: do ministério público da união e dos estados), DUPLICATION(resolvido), DUPLICATION(resolvido)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.133` — Art. 133 — Advocacia

- Risco: MEDIUM · complexidade: EXTERNAL · SENSITIVE_THEME: invioláv
- Ponto jurídico: O art. 133 declara o advogado indispensável à administração da justiça.
- Interpretação principal: O artigo reconhece a advocacia como parte do funcionamento da Justiça, ao lado do Judiciário, do Ministério Público e da Defensoria.
- ATENÇÃO: O texto não diz que todo processo exige advogado.
- Dependência externa: nenhuma
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.136` — Art. 136 — Estado de defesa

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: prisão
- Ponto jurídico: O art. 136 permite que o Presidente da República, depois de ouvir o Conselho da República e o Conselho de Defesa Nacional, decrete estado de defesa.
- Interpretação principal: O estado de defesa é a primeira e mais leve das medidas excepcionais da Constituição.
- ATENÇÃO: O parecer dos Conselhos é exigido, mas o texto não diz que ele vincula o Presidente.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: conselho da república e o conselho de defesa)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.136:PAR.3` — Art. 136, § 3º — Garantias do preso no estado de defesa

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: prisão
- Ponto jurídico: O § 3º fixa regras para a prisão durante o estado de defesa.
- Interpretação principal: Mesmo em situação excepcional, o preso não fica sem proteção.
- ATENÇÃO: O inciso I trata da prisão por crime contra o Estado; os incisos III e IV valem para a prisão ou detenção de qualquer pessoa durante o estado de defesa.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: estado físico e mental do detido no momento), NEAR_COPY_MICROFIX(o_que_significa: estado físico e mental do detido no momento)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.139` — Art. 139 — Medidas no estado de sítio por comoção grave

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: crimes
- Ponto jurídico: O art. 139 determina que, no estado de sítio decretado com base no art. 137, I, só podem ser tomadas contra as pessoas as medidas da lista.
- Interpretação principal: Na comoção grave, a lista de medidas é fechada.
- ATENÇÃO: A lista vale para o estado de sítio do art. 137, I.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.142:PAR.3` — Art. 142, § 3º — Regime jurídico dos militares

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: prerrogativ
- Ponto jurídico: O § 3º denomina militares os membros das Forças Armadas e lhes aplica, além do que a lei fixar, regras próprias.
- Interpretação principal: O parágrafo cria um regime próprio para os militares, diferente do dos servidores civis.
- ATENÇÃO: A perda do posto depende de decisão de tribunal militar permanente quando o país está em paz, ou de tribunal especial se houver guerra.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.150:INC.VI` — Art. 150, inciso VI — Imunidades tributárias

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: O alcance das imunidades (por exemplo, livros digitais e…
- Ponto jurídico: O inciso VI proíbe instituir impostos sobre: patrimônio, renda ou serviços de um ente federativo cobrados por outro (alínea a); templos de qualquer culto e entidades religiosas, com suas organizações…
- Interpretação principal: As imunidades impedem a cobrança de impostos sobre as pessoas e os bens indicados.
- ATENÇÃO: Os §§ 2º a 4º limitam o alcance das imunidades das alíneas a, b e c às finalidades essenciais das entidades.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: e fonogramas e videofonogramas musicais…), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.150:PAR.2` — Art. 150, §§ 2º e 3º — Alcance da imunidade recíproca

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: A extensão da imunidade recíproca a outras empresas estatais…
- Ponto jurídico: O § 2º estende a imunidade recíproca (inciso VI, a) às autarquias, às fundações criadas e mantidas pelo poder público e à empresa pública que presta o serviço postal.
- Interpretação principal: A imunidade recíproca protege os entes federativos.
- ATENÇÃO: A aplicação da imunidade a empresas estatais além da empresa postal é tema da camada JURISPRUDÊNCIA.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: e mantidas pelo poder público e à empresa), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.151` — Art. 151 — Limitações ao poder de tributar da União

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: A concessão de isenções de tributos locais por tratado…
- Ponto jurídico: O art. 151 proíbe a União de três condutas.
- Interpretação principal: As três vedações limitam o poder tributário da União em relação aos demais entes.
- ATENÇÃO: A vedação do inciso III trata de isenção concedida pela União em lei própria.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.155:PAR.2:INC.VII` — Art. 155, § 2º, incisos VII e VIII — Diferença de alíquotas nas vendas para outro Estado

- Risco: MEDIUM · complexidade: EXTERNAL · JURISPRUDENCE_CONTEXT_ONLY: A exigência de lei complementar para a cobrança do…
- Ponto jurídico: O inciso VII determina que, nas vendas de bens e serviços a consumidor final localizado em outro Estado, contribuinte ou não do imposto, se aplique a alíquota interestadual, cabendo ao Estado do…
- Interpretação principal: A regra divide o imposto entre o Estado de origem e o Estado de destino.
- ATENÇÃO: A cobrança dessa diferença depende de lei complementar sobre o imposto.
- Dependência externa: JURISPRUDENCIA (contexto)
- Warnings: lint JURISPRUDENCE_WORDING_IN_BODY, lint TERM_LOW_UTILITY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (JURISPRUDENCE_CONTEXT_ONLY)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.156:PAR.1` — Art. 156, §§ 1º e 1º-A — Imposto sobre a propriedade urbana

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: imunidade
- Ponto jurídico: O § 1º permite que o imposto sobre a propriedade predial e territorial urbana seja progressivo conforme o valor do imóvel, tenha alíquotas diferentes conforme a localização e o uso e tenha a base de…
- Interpretação principal: O imposto sobre imóveis urbanos pode variar de três formas.
- ATENÇÃO: A atualização da base de cálculo pelo Executivo depende de critérios definidos em lei municipal.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167` — Art. 167 — Vedações orçamentárias

- Risco: MEDIUM · complexidade: EXTERNAL · SENSITIVE_THEME: sob pena
- Ponto jurídico: O art. 167 lista vedações em matéria orçamentária.
- Interpretação principal: O artigo funciona como um conjunto de regras de disciplina do orçamento.
- ATENÇÃO: Os incisos III e IV e os §§ 1º, 3º e 7º têm explicação própria.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167:PAR.1` — Art. 167, § 1º — Investimento plurianual sem previsão

- Risco: MEDIUM · complexidade: SIMPLE · SENSITIVE_THEME: sob pena
- Ponto jurídico: O § 1º proíbe começar investimento que dure mais de um exercício financeiro se ele não tiver sido incluído antes no plano plurianual ou se não houver lei autorizando essa inclusão.
- Interpretação principal: Obras e investimentos que duram mais de um ano precisam estar no planejamento de médio prazo antes de começar.
- ATENÇÃO: O processo e as penas do crime de responsabilidade são definidos em lei especial, na camada de legislação correlata.
- Dependência externa: nenhuma
- Warnings: NUMBER_FROM_OTHER_DEVICE(3 anos)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167-B` — Art. 167-B — Regime extraordinário na calamidade nacional

- Risco: MEDIUM · complexidade: STRUCTURED · SENSITIVE_THEME: incompatív
- Ponto jurídico: O art. 167-B trata da calamidade pública que alcança todo o país, decretada pelo Congresso por iniciativa privativa do Presidente da República.
- Interpretação principal: Em uma calamidade de alcance nacional, as regras fiscais e de contratação comuns podem ser lentas demais.
- ATENÇÃO: O regime é da União e depende de decreto do Congresso.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.169` — Art. 169 — Limites de despesa com pessoal

- Risco: MEDIUM · complexidade: EXTERNAL · SENSITIVE_THEME: perder o cargo
- Ponto jurídico: O art. 169 proíbe que a União, os Estados, o Distrito Federal e os Municípios gastem com pessoal ativo, inativo e pensionistas acima dos limites fixados em lei complementar.
- Interpretação principal: O artigo coloca um teto nos gastos com servidores, aposentados e pensionistas.
- ATENÇÃO: Os §§ 1º e 3º a 7º têm explicação própria.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a união os estados o distrito federal e), NEAR_COPY_MICROFIX(exemplo_pratico: com cargos em comissão e funções de confiança), lint TERM_LOW_UTILITY
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.169:PAR.3` — Art. 169, §§ 3º, 4º, 5º, 6º e 7º — Redução da despesa com pessoal

- Risco: MEDIUM · complexidade: EXTERNAL · SENSITIVE_THEME: perder o cargo
- Ponto jurídico: O § 3º determina que, para cumprir os limites no prazo da lei complementar, os entes reduzam em pelo menos vinte por cento as despesas com cargos em comissão e funções de confiança e exonerem os…
- Interpretação principal: O bloco define uma ordem para reduzir gastos com pessoal.
- ATENÇÃO: A perda do cargo de servidor estável é a última medida e depende de ato motivado.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: cargo emprego ou função com atribuições iguais ou)
- Motivo da fila: sem alerta; LEGAL_RISK MEDIUM (SENSITIVE_THEME)
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

