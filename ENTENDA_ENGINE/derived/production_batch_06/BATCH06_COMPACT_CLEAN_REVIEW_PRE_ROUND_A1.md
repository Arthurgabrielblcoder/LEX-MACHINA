# BATCH06 — REVISÃO COMPACTA (filas A e B)

Lote `ENTENDA_CF_PRODUCTION_BATCH_06` · 2026-10-04 · nenhum item aprovado (AUTO_APPROVE_LOW/MEDIUM = OFF). Revisão humana obrigatória em formato compacto; T1 completo só sob pedido. Risco = LEGAL_RISK; complexidade = VERIFICATION_COMPLEXITY.

## A — CLEAN_LOW (42)

### `CF88:ART.42` — Art. 42 — Militares dos Estados, do Distrito Federal e dos Territórios

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 42 identifica os militares estaduais: os integrantes das Polícias Militares e dos Corpos de Bombeiros Militares, instituições que se organizam pela hierarquia e pela disciplina.
- Interpretação principal: O artigo separa duas categorias de militares.
- ATENÇÃO: Polícia Militar e Corpo de Bombeiros Militar não se confundem com as Forças Armadas, embora algumas regras destas lhes sejam aplicadas por remissão.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.42:PAR.1` — Art. 42, § 1º — Regras aplicáveis aos militares estaduais

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º estende aos militares estaduais, além do que a lei fixar, as regras do art. 14, § 8º (elegibilidade do militar), do art. 40, § 9º (contagem do tempo de contribuição) e do art. 142, §§ 2º e 3º…
- Interpretação principal: O parágrafo funciona por remissão: em vez de repetir regras, aponta para outros artigos.
- ATENÇÃO: Ler este parágrafo exige consultar os dispositivos citados: ele não reproduz o conteúdo do art. 14, § 8º, do art. 40, § 9º, nem do art. 142.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.42:PAR.3` — Art. 42, § 3º — Acumulação de cargos pelo militar estadual

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 3º manda aplicar aos militares dos Estados, do Distrito Federal e dos Territórios a regra do art. 37, XVI, sobre acumulação remunerada de cargos públicos, com prioridade para a atividade militar.
- Interpretação principal: O art. 37, XVI, proíbe em regra acumular cargos públicos remunerados e admite exceções, como a de professor com outro cargo e a de dois cargos de profissionais da saúde,…
- ATENÇÃO: O parágrafo não cria hipóteses novas de acumulação: remete às do art. 37, XVI.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: aos militares dos estados do distrito federal e), HISTORICAL_CLAIM_SUPPORTED(foi incluído pela Emenda Constitucional…), EXCEPTION_NOT_IN_TEXT(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.43:PAR.2` — Art. 43, § 2º — Incentivos regionais

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º lista, sem esgotar, os incentivos regionais, na forma da lei: igualdade de tarifas, fretes, seguros e outros custos de responsabilidade do poder público; juros favorecidos para atividades…
- Interpretação principal: Os incentivos são ferramentas para reduzir desvantagens de regiões menos desenvolvidas.
- ATENÇÃO: Os benefícios tributários do inciso III alcançam tributos federais.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: nas regiões de baixa renda sujeitas a secas), lint ABSOLUTE_CLAIM, lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.44` — Art. 44 — Congresso Nacional e legislatura

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 44 atribui o Poder Legislativo da União ao Congresso Nacional, formado por duas Casas: a Câmara dos Deputados e o Senado Federal.
- Interpretação principal: O Brasil adota, no plano federal, o bicameralismo: as leis em regra passam pelas duas Casas.
- ATENÇÃO: Legislatura (quatro anos) não se confunde com sessão legislativa (o período anual de trabalho) nem com o mandato do senador, que é de oito anos.
- Dependência externa: nenhuma
- Warnings: NUMBER_FROM_OTHER_DEVICE(8 anos), EXAMPLE_NUMBER_NOT_IN_TEXT(2), NUMBER_FROM_OTHER_DEVICE(8 anos)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.45` — Art. 45 — Câmara dos Deputados

- Risco: LOW · complexidade: EXTERNAL
- Ponto jurídico: O art. 45 define a Câmara dos Deputados como a Casa dos representantes do povo, eleitos pelo sistema proporcional em cada Estado, Território e no Distrito Federal.
- Interpretação principal: Os deputados representam a população, e não os entes federativos.
- ATENÇÃO: O sistema proporcional da Câmara é diferente do sistema majoritário do Senado (art. 46).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: do povo eleitos pelo sistema proporcional em cada)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.46` — Art. 46 — Senado Federal

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 46 define o Senado Federal como a Casa dos representantes dos Estados e do Distrito Federal, eleitos pelo princípio majoritário.
- Interpretação principal: No Senado, todos os Estados têm o mesmo peso, independentemente da população.
- ATENÇÃO: Os suplentes são eleitos junto com o senador, na mesma chapa; não há eleição separada para eles.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: representantes dos estados e do distrito federal…), NUMBER_FROM_OTHER_DEVICE(fracao 1/3 , fracao 2/3 )
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.47` — Art. 47 — Quórum das deliberações

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 47 estabelece a regra geral de votação no Congresso: ressalvadas as exceções previstas na própria Constituição, cada Casa e cada comissão decidem por maioria dos votos, desde que esteja…
- Interpretação principal: A regra tem duas exigências diferentes.
- ATENÇÃO: Maioria simples (dos votos dos presentes) é diferente de maioria absoluta (mais da metade de todos os membros da Casa).
- Dependência externa: nenhuma
- Warnings: EXAMPLE_NUMBER_NOT_IN_TEXT(21, 40), EXAMPLE_NUMBER_NOT_IN_TEXT(16), TRANSITION_IN_CORE(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.49` — Art. 49 — Competência exclusiva do Congresso

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 49 enumera as competências exclusivas do Congresso Nacional.
- Interpretação principal: Competência exclusiva é aquela que o Congresso exerce sozinho, sem sanção ou veto do Presidente.
- ATENÇÃO: O art. 49 trata da competência do Congresso como um todo.
- Dependência externa: nenhuma
- Warnings: HISTORICAL_CLAIM_SUPPORTED(foi incluído pela Emenda Constitucional…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.49:INC.V` — Art. 49, inciso V — Sustação de atos normativos do Executivo

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso V autoriza o Congresso a sustar os atos normativos do Poder Executivo que ultrapassem o poder regulamentar ou os limites de uma delegação legislativa.
- Interpretação principal: O Executivo pode editar regulamentos para executar as leis (art. 84, IV) e leis delegadas nos limites da resolução de delegação (art. 68).
- ATENÇÃO: Sustar não é o mesmo que revogar nem que declarar inconstitucional: o Congresso suspende a eficácia do ato que exorbitou.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: sustar os atos normativos do poder executivo que)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.49:INC.IX` — Art. 49, inciso IX — Julgamento das contas do Presidente

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O inciso IX encarrega o Congresso de julgar a cada ano as contas do Presidente da República e de examinar os relatórios de execução dos planos de governo.
- Interpretação principal: O Presidente presta contas anualmente ao Congresso (art. 84, XXIV).
- ATENÇÃO: Se o Presidente não apresentar as contas no prazo, cabe à Câmara proceder à tomada de contas (art. 51, II).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_significa: os relatórios sobre a execução dos planos de)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.51` — Art. 51 — Competências privativas da Câmara

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 51 lista as competências privativas da Câmara dos Deputados: autorizar a instauração de processo contra o Presidente, o Vice-Presidente e os Ministros de Estado; tomar as contas do Presidente…
- Interpretação principal: Competência privativa é aquela exercida só pela Câmara, sem participação do Senado nem sanção do Presidente.
- ATENÇÃO: A Câmara autoriza o processo contra o Presidente, mas não o julga: o julgamento por crime de responsabilidade cabe ao Senado (art. 52, I).
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.52:INC.III` — Art. 52, inciso III — Aprovação prévia de autoridades pelo Senado

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso III exige aprovação prévia do Senado, por voto secreto e após arguição pública, para a escolha de certas autoridades.
- Interpretação principal: É um mecanismo de controle mútuo entre os Poderes.
- ATENÇÃO: A sabatina é pública, mas o voto é secreto.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: do tribunal de contas da união indicados pelo)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.53:PAR.6` — Art. 53, § 6º — Dispensa de testemunhar sobre informações do mandato

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 6º dispensa deputados e senadores de testemunhar sobre informações recebidas ou prestadas por causa do mandato e sobre as pessoas que lhes passaram ou delas receberam informações.
- Interpretação principal: A regra protege a relação de confiança entre o parlamentar e quem leva a ele denúncias e dados, por exemplo para uma investigação parlamentar.
- ATENÇÃO: O parágrafo trata de uma dispensa: não proíbe o parlamentar de testemunhar se quiser.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.54` — Art. 54 — Incompatibilidades dos parlamentares

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 54 lista o que deputados e senadores não podem fazer.
- Interpretação principal: As incompatibilidades evitam conflito de interesses: quem vota leis e fiscaliza o governo não deve manter vínculos que o tornem dependente do próprio poder público.
- ATENÇÃO: Incompatibilidade não se confunde com inelegibilidade: a primeira impede certas atividades durante o mandato; a segunda impede a própria candidatura.
- Dependência externa: nenhuma
- Warnings: lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.54:INC.II` — Art. 54, inciso II — Vedações desde a posse

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso II proíbe ao parlamentar, desde a posse: ser dono, controlador ou diretor de empresa beneficiada por favor que resulte de contrato com o poder público, ou exercer nela função remunerada;…
- Interpretação principal: Com a posse, as restrições ficam mais rigorosas.
- ATENÇÃO: A proibição da alínea a fala em empresa que goze de favor decorrente de contrato público: não é qualquer empresa da qual o parlamentar seja sócio.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: de mais de um cargo ou mandato público)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.56:PAR.1` — Art. 56, §§ 1º e 2º — Suplente e eleição para preencher a vaga

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 1º manda convocar o suplente em caso de vaga, de investidura nos cargos do art. 56 ou de licença superior a cento e vinte dias.
- Interpretação principal: Os parágrafos garantem que a cadeira não fique vazia por muito tempo.
- ATENÇÃO: A licença de até cento e vinte dias não gera convocação de suplente pelo § 1º.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: de licença superior a cento e vinte dias)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.57:PAR.2` — Art. 57, § 2º — Recesso condicionado à aprovação da LDO

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O § 2º impede que a sessão legislativa seja interrompida sem que o projeto da lei de diretrizes orçamentárias esteja aprovado.
- Interpretação principal: A lei de diretrizes orçamentárias orienta a elaboração do orçamento do ano seguinte.
- ATENÇÃO: O parágrafo fala em aprovação do projeto, e não em sanção da lei.
- Dependência externa: nenhuma
- Warnings: EXAMPLE_NUMBER(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.57:PAR.7` — Art. 57, §§ 7º e 8º — Pauta da sessão extraordinária

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 7º limita a sessão legislativa extraordinária à matéria para a qual o Congresso foi convocado, ressalvadas as medidas provisórias do § 8º, e proíbe pagamento de parcela indenizatória pela…
- Interpretação principal: Na convocação extraordinária, o Congresso não tem pauta livre: só delibera sobre o que motivou a convocação.
- ATENÇÃO: A vedação de parcela indenizatória pela convocação tem a redação dada pela Emenda Constitucional nº 50, de 2006.
- Dependência externa: nenhuma
- Warnings: ABSOLUTE_CLAIM(resolvido), lint ABSOLUTE_CLAIM
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.58` — Art. 58 — Comissões do Congresso e de suas Casas

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 58 prevê comissões permanentes e temporárias no Congresso e em cada Casa, formadas conforme o regimento ou o ato de criação.
- Interpretação principal: Grande parte do trabalho legislativo ocorre nas comissões, que examinam projetos por tema antes do plenário.
- ATENÇÃO: A expressão "tanto quanto possível" indica que a proporcionalidade é um objetivo a ser buscado, não uma divisão matemática exata em todos os casos.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: tanto quanto possível a representação…), LAW_DEPENDENCY_OMITTED(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.58:PAR.2` — Art. 58, § 2º — O que as comissões podem fazer

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º atribui às comissões, conforme a matéria de sua competência: discutir e votar projetos que dispensem o plenário, na forma do regimento, salvo recurso de um décimo dos membros da Casa; realizar…
- Interpretação principal: O inciso I traz o chamado poder conclusivo: certos projetos podem ser aprovados pela própria comissão, sem passar pelo plenário.
- ATENÇÃO: Quais projetos podem ser votados de forma conclusiva é definido pelo regimento de cada Casa.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: recurso de um décimo dos membros da casa), LAW_DEPENDENCY_OMITTED(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.59` — Art. 59 — Espécies do processo legislativo

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 59 enumera o que o processo legislativo produz: emendas à Constituição, leis complementares, leis ordinárias, leis delegadas, medidas provisórias, decretos legislativos e resoluções.
- Interpretação principal: Cada espécie tem procedimento e função próprios, detalhados nos artigos seguintes.
- ATENÇÃO: A lista não estabelece hierarquia simples entre as espécies: lei complementar e lei ordinária, por exemplo, diferem sobretudo pela matéria e pelo quórum.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.61:PAR.2` — Art. 61, § 2º — Iniciativa popular de lei

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º permite a iniciativa popular por meio de projeto de lei apresentado à Câmara dos Deputados, assinado por pelo menos um por cento do eleitorado nacional, espalhado por no mínimo cinco Estados,…
- Interpretação principal: A iniciativa popular é uma forma de participação direta: os próprios cidadãos propõem a lei.
- ATENÇÃO: A iniciativa popular prevista aqui é para leis, e não para emendas à Constituição.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: décimos por cento dos eleitores de cada um), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.62:PAR.2` — Art. 62, § 2º — Medida provisória sobre impostos

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º determina que a medida provisória que crie ou aumente impostos só produza efeitos no exercício financeiro seguinte se for convertida em lei até o último dia do ano em que foi editada, com…
- Interpretação principal: A regra combina a medida provisória com a anterioridade tributária.
- ATENÇÃO: A regra se soma às demais limitações ao poder de tributar, como os prazos de anterioridade do art. 150, III.
- Dependência externa: nenhuma
- Warnings: lint TERM_LOW_UTILITY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.62:PAR.3` — Art. 62, §§ 3º, 4º e 7º — Prazo de vigência da medida provisória

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 3º estabelece que a medida provisória perde a eficácia desde a edição se não for convertida em lei em sessenta dias, prorrogáveis uma vez por igual período, ressalvados os §§ 11 e 12, cabendo ao…
- Interpretação principal: A medida provisória tem vida limitada: sessenta dias, mais sessenta se a votação não for concluída, totalizando até cento e vinte dias, sem contar o recesso.
- ATENÇÃO: O prazo fica suspenso durante o recesso parlamentar.
- Dependência externa: nenhuma
- Warnings: NUMBER_FROM_OTHER_DEVICE(120 dias)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.62:PAR.10` — Art. 62, § 10 — Proibição de reeditar medida provisória

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 10 proíbe reeditar, na mesma sessão legislativa, medida provisória rejeitada ou que tenha perdido a eficácia por decurso de prazo.
- Interpretação principal: Antes de 2001, medidas provisórias não votadas eram reeditadas repetidamente, e algumas vigoravam por anos sem decisão do Congresso.
- ATENÇÃO: A vedação alcança a reedição da mesma medida.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.62:PAR.11` — Art. 62, §§ 11 e 12 — Efeitos depois da rejeição ou da aprovação com alterações

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 11 determina que, se o decreto legislativo do § 3º não for editado em até sessenta dias após a rejeição ou a perda de eficácia da medida provisória, as relações jurídicas formadas durante a sua…
- Interpretação principal: O § 11 dá segurança a quem agiu com base na medida enquanto ela valia: se o Congresso não regular a situação em sessenta dias, esses atos continuam regidos pela medida,…
- ATENÇÃO: O § 11 só alcança relações constituídas e atos praticados durante a vigência; não permite novos atos com base na medida rejeitada.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.64` — Art. 64 — Início na Câmara e urgência constitucional

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 64 determina que os projetos de lei apresentados pelo Presidente da República, pelo Supremo Tribunal Federal ou pelos Tribunais Superiores comecem a ser discutidos e votados na Câmara dos…
- Interpretação principal: Projetos que vêm de fora do Congresso entram pela Câmara, a Casa de representação do povo.
- ATENÇÃO: A urgência do § 1º só pode ser pedida para projetos de iniciativa do próprio Presidente.
- Dependência externa: nenhuma
- Warnings: lint TERM_NOT_USED
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.64:PAR.2` — Art. 64, §§ 2º, 3º e 4º — Prazos da urgência pedida pelo Presidente

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º determina que, pedida a urgência, se a Câmara e o Senado não se manifestarem, cada qual sucessivamente, em até quarenta e cinco dias, as demais deliberações legislativas da Casa fiquem…
- Interpretação principal: Cada Casa tem quarenta e cinco dias para se manifestar, uma depois da outra.
- ATENÇÃO: O sobrestamento não alcança as deliberações que tenham prazo constitucional determinado: o § 2º as exclui expressamente.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: cada qual sucessivamente em até quarenta e cinco), EXCEPTION_NOT_IN_TEXT(resolvido)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.66:PAR.7` — Art. 66, § 7º — Quem promulga a lei

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 7º trata da promulgação nos casos de sanção tácita e de veto derrubado.
- Interpretação principal: A regra impede que a lei deixe de existir formalmente por omissão do Presidente.
- ATENÇÃO: O parágrafo trata da promulgação nos casos dos §§ 3º e 5º.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.67` — Art. 67 — Reapresentação de projeto rejeitado

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 67 determina que a matéria de projeto de lei rejeitado só possa ser objeto de novo projeto, na mesma sessão legislativa, se houver proposta da maioria absoluta dos membros de uma das Casas do…
- Interpretação principal: É o chamado princípio da irrepetibilidade.
- ATENÇÃO: A regra para projeto de lei é mais flexível que a da emenda constitucional: a proposta de emenda rejeitada não pode ser reapresentada na mesma sessão legislativa em hipótese alguma (art. 60, § 5º).
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: objeto de novo projeto na mesma sessão legislativa)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.68` — Art. 68 — Leis delegadas

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 68 estabelece que as leis delegadas são elaboradas pelo Presidente da República, que precisa pedir a delegação ao Congresso Nacional.
- Interpretação principal: Na lei delegada, o Congresso transfere ao Presidente, por tempo e conteúdo definidos, o poder de legislar sobre um tema.
- ATENÇÃO: Lei delegada não se confunde com medida provisória: depende de autorização prévia do Congresso e não tem prazo de conversão.
- Dependência externa: nenhuma
- Warnings: lint TERM_NOT_USED
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.68:PAR.1` — Art. 68, § 1º — Matérias que não podem ser delegadas

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: Pelo § 1º, ficam fora da delegação três grupos.
- Interpretação principal: Algumas matérias são vedadas por pertencerem ao núcleo das funções do próprio Legislativo, como as competências exclusivas e privativas, exercidas por decreto…
- ATENÇÃO: A lista de vedações é parecida, mas não idêntica, à das medidas provisórias (art. 62, § 1º).
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.68:PAR.2` — Art. 68, §§ 2º e 3º — Forma da delegação e apreciação pelo Congresso

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º determina que a delegação ao Presidente seja feita por resolução do Congresso, que especifica o seu conteúdo e os termos de seu exercício.
- Interpretação principal: A resolução de delegação funciona como um mandato com limites: indica o tema, o alcance e as condições da lei a ser editada.
- ATENÇÃO: A proibição de emendas vale para a apreciação prevista no § 3º, e não para a votação da própria resolução de delegação.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a resolução determinar a apreciação do projeto…), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.70` — Art. 70 — Fiscalização da União: controle externo e interno

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 70 trata da fiscalização das contas da União e das entidades da sua administração, nos aspectos contábil, financeiro, orçamentário, operacional e patrimonial.
- Interpretação principal: O artigo abre a seção sobre o controle do dinheiro público federal.
- ATENÇÃO: O artigo trata da União.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.70:PAR.UNICO` — Art. 70, parágrafo único — Quem deve prestar contas

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O parágrafo único obriga a prestar contas toda pessoa, física ou jurídica, pública ou privada, que use, arrecade, guarde, gerencie ou administre dinheiro, bens ou valores públicos, ou pelos quais a…
- Interpretação principal: O dever de prestar contas não depende de quem a pessoa é, mas do que ela faz com recursos públicos.
- ATENÇÃO: O dever alcança a parcela de recursos públicos administrada, e não toda a atividade da entidade privada.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: pessoa física ou jurídica pública ou privada que), lint EXAMPLE_REQUIREMENT_LANGUAGE
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.71:INC.I` — Art. 71, inciso I — Parecer prévio sobre as contas do Presidente

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso I dá ao Tribunal a tarefa de examinar as contas apresentadas a cada ano pelo Presidente da República e de emitir sobre elas parecer prévio no prazo de sessenta dias, contado do recebimento.
- Interpretação principal: Nas contas do Presidente, o Tribunal não julga: emite parecer técnico, que orienta a decisão.
- ATENÇÃO: Não confundir com o inciso II: as contas dos demais administradores são julgadas pelo próprio Tribunal.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.71:INC.II` — Art. 71, inciso II — Julgamento das contas de administradores

- Risco: LOW · complexidade: SIMPLE
- Ponto jurídico: O inciso II atribui ao Tribunal julgar as contas de quem administra ou responde por dinheiro, bens e valores públicos da administração direta e indireta, inclusive fundações e sociedades criadas e…
- Interpretação principal: Aqui o Tribunal julga de fato: decide se as contas são regulares ou irregulares.
- ATENÇÃO: Embora se fale em julgamento, o Tribunal não é órgão do Judiciário.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: bens e valores públicos da administração direta e)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.71:INC.IX` — Art. 71, incisos IX e X — Prazo para correção e sustação de atos

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: Os incisos IX e X tratam da reação do Tribunal diante de ilegalidade.
- Interpretação principal: Há uma sequência.
- ATENÇÃO: A sustação direta pelo Tribunal vale para atos, e não para contratos.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: a execução do ato impugnado comunicando a decisão), NUMBER_FROM_OTHER_DEVICE(30 dias)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.72` — Art. 72 — Despesas não autorizadas: atuação da comissão mista

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O art. 72 permite que a comissão mista permanente de orçamento (art. 166, § 1º), diante de indícios de despesas não autorizadas, peça explicações à autoridade responsável em cinco dias.
- Interpretação principal: O artigo cria um procedimento rápido para gastos feitos sem autorização orçamentária, inclusive disfarçados de investimentos não programados ou subsídios não aprovados.
- ATENÇÃO: A proposta de sustação depende de dois requisitos: a irregularidade apontada pelo Tribunal e o risco de dano irreparável ou grave lesão à economia pública.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: 1 diante de indícios de despesas não autorizadas)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.73:PAR.2` — Art. 73, § 2º — Escolha dos Ministros do Tribunal de Contas da União

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º divide a escolha dos Ministros: um terço pelo Presidente da República, com aprovação do Senado, sendo duas dessas vagas preenchidas, alternadamente, por auditores e por membros do Ministério…
- Interpretação principal: Com nove Ministros, o Presidente escolhe três e o Congresso, seis.
- ATENÇÃO: O Ministério Público junto ao Tribunal de Contas é um órgão próprio, distinto do Ministério Público da União.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: pelo presidente da república com aprovação do…)
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.74:PAR.2` — Art. 74, § 2º — Denúncia de irregularidades ao Tribunal

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O § 2º reconhece a qualquer cidadão, partido político, associação ou sindicato legitimidade para levar ao Tribunal de Contas da União, na forma da lei, denúncia sobre irregularidades ou ilegalidades.
- Interpretação principal: O parágrafo abre o controle das contas públicas à participação social.
- ATENÇÃO: A denúncia não é uma ação judicial: leva os fatos ao Tribunal, que decide se e como apurar.
- Dependência externa: nenhuma
- Warnings: nenhum
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

## B — CLEAN_MEDIUM (0)

- nenhum item nesta fila

