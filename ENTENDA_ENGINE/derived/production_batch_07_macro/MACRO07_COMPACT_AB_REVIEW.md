# MACRO07 — REVISÃO COMPACTA (filas A e B)

Lote `ENTENDA_CF_MACRO_BATCH_07` · 2026-10-05 · 71 itens pendentes; aprovação só por revisão humana (AUTO_APPROVE_LOW/MEDIUM = OFF). Revisão humana obrigatória em formato compacto; T1 completo só sob pedido. Risco = LEGAL_RISK; complexidade = VERIFICATION_COMPLEXITY.

## A — CLEAN_LOW (71)

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
- Interpretação principal: O artigo prevê uma contribuição própria para custear, expandir e melhorar o serviço de iluminação pública.
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
- ATENÇÃO: Há tributos que não seguem a alínea b, a alínea c ou ambas: parte das exceções está no § 1º, com explicação própria, e outras aparecem em dispositivos como os arts. 195, § 6º, 177, § 4º, I, b, e 155,…
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
- Interpretação principal: Os combustíveis e lubrificantes definidos em lei complementar têm um regime especial: o imposto é cobrado uma única vez na cadeia.
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
- Warnings: NEAR_COPY_MICROFIX(o_que_significa: orçamentos fiscal e da seguridade social da união)
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
- Ponto jurídico: O § 3º limita a aprovação de emendas ao projeto de lei do orçamento anual, ou aos que o modifiquem, às hipóteses dos incisos I a III.
- Interpretação principal: O parlamentar pode mudar o orçamento, mas não pode criar despesa do nada.
- ATENÇÃO: Os incisos do texto estão ligados pela conjunção ou; a leitura de quais requisitos são cumulativos deve considerar a redação dos incisos I e II e a camada JURISPRUDÊNCIA.
- Dependência externa: nenhuma
- Warnings: NEAR_COPY_MICROFIX(o_que_diz: ao projeto de lei do orçamento anual ou), lint JURISPRUDENCE_WORDING_IN_BODY
- Motivo da fila: LOW sem alerta
- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D

### `CF88:ART.167:INC.IV` — Art. 167, inciso IV — Não vinculação da receita de impostos

- Risco: LOW · complexidade: STRUCTURED
- Ponto jurídico: O inciso IV proíbe vincular a receita de impostos a órgão, fundo ou despesa.
- Interpretação principal: A regra é a não vinculação da receita de impostos.
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

## B — CLEAN_MEDIUM (0)

- nenhum item nesta fila

