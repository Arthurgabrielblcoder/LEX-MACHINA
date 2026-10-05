# ENTENDA BATCH05 — RODADA 03B — DIFF EDITORIAL (art. 40, 2ª metade, HIGH)

- Revisão: `ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW` · escopo `CF88_ART40_HIGH_ROUND_3B` · 2026-10-04
- Resultado: 11 revisados · 1 APROVADO sem alteração · 10 AJUSTAR · 0 REJEITADOS
- `ROUND03B_ART40_HIGH_HUMAN_APPROVED`: 11 de 11 · `BATCH05_HIGH_REVIEW_COMPLETE`: 38 de 38 HIGH aprovados.
- `CF88:ART.40:PAR.8` → `HUMAN_APPROVED_T1` (v1, conteúdo inalterado; nenhum microajuste necessário).
- 10 itens AJUSTAR → `editorial_version` 2 → `HUMAN_APPROVED_T1` direto, pela **política de microajustes T1** da Rodada 03A (válida nesta rodada). As v1 permanecem como `RETIRED` / `CHANGES_REQUESTED`.
- Drafts anteriores em `BATCH_05_DRAFTS_PRE_ROUND3B.json`. Targets, papel e cobertura de BLOCK inalterados. Rodadas 01, 02 e 03A, pilotos e itens MEDIUM/LOW inalterados.
- Texto quebrado em linhas convertido pela mesma regra da 03A, acrescida de: linha que começa com "* " é item de lista (linha própria). O teste confere a conversão.

## Desvios T1 (1) — política pré-autorizada

| Target | Seção | Texto do revisor | Texto aplicado | Item da política | Motivo |
|---|---|---|---|---|---|
| `CF88:ART.40:PAR.7` | o_que_diz | quando decorrente de agressão sofrida | quando decorrente da agressão sofrida | 2 (trocar artigo, preposicao, ordem sintatica ou sinonimo exclusivamente para evitar NEAR_COPY_OF_OFFICIAL_TEXT) | ENTENDA_COPIES_OFFICIAL_TEXT: 11 palavras seguidas do § 7º oficial; preposicao "de" -> "da" |

Prova automática (`test_round3b_pre_authorized_t1_policy`): conteúdo = texto do revisor + desvio registrado; nenhum número alterado; só palavras funcionais diferem.

## Estrutura dos 3 BLOCKs

- §§ 9º/10: `covered_targets` = `CF88:ART.40:PAR.10` (irmão).
- §§ 14–16: `covered_targets` = `CF88:ART.40:PAR.15`, `CF88:ART.40:PAR.16` (irmãos).
- § 22 + incisos I–X: **confirmado BLOCK**. Os incisos são subdivisões do próprio § 22 e ficam cobertos como `BLOCK_SUBDIVISION` (mesmo mecanismo do art. 41, § 1º, incisos I–III). `covered_targets` é reservado a irmãos estruturais: o motor rejeita filhos nesse campo (`ENTENDA_COVERED_INVALID`), por isso não foram listados ali. O teste confere os 10 incisos como `BLOCK_SUBDIVISION`.

## Camada externa e proveniência

- Notas existentes mantidas: §§ 7º ("Manter"), 9º/10, 12, 13, 19 e 20 (sem instrução de alteração).
- § 11: nota antiga substituída pelas notas dos Temas 377/384 e do Tema 359.
- §§ 14–16: nota existente mantida + nota sobre o marco de instituição do regime complementar e o § 16.
- § 18: nota substituída por "Art. 149, § 1º-A." (mesmo critério da Rodada 02 para notas fornecidas literalmente).
- § 22: nota antiga ("a lei complementar … está na camada de leis correlatas") removida; nova nota: art. 9º da EC 103/2019, Lei nº 9.717/1998 e regras do próprio art. 9º, sem apresentar a lei complementar como editada.
- Proveniência `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`: § 11 (Temas 377/384 e 359), §§ 14–16 (nota do marco), § 18 (parâmetro ordinário × base do art. 149, § 1º-A), § 22 (art. 9º da EC 103/2019, Lei nº 9.717/1998).
- Observação: a lista com "* " no O QUE SIGNIFICA do § 22 é a primeira lista em itens do corpus ENTENDA; o validador aceita e o texto foi mantido literalmente.

## editorial_checks

- 5 alertas novos gerados pelo texto do revisor, resolvidos sem alterar texto: "automaticamente" em negação (§§ 14 e 19), remissão a lei complementar e "autarquia" (§ 20), ano 2019 (§ 22). Resultado: 0 sem resolução.

## Aprovado sem alteração

- `CF88:ART.40:PAR.7` — O draft afirmava que, com outra renda formal, a pensao "pode ficar abaixo do salario minimo"; nao transformar a ausencia da garantia em autorizacao generica para qualquer valor.
- `CF88:ART.40:PAR.8` — Distingue preservacao do valor real; indice e periodicidade remetidos a lei; inexistencia, no § 8º atual, de garantia geral de paridade com servidores ativos; eventual paridade oriunda de regras de transicao externas.
- `CF88:ART.40:PAR.9` — Evitar a ideia de que a mudanca de ente transfere automaticamente o tempo sem observar a contagem reciproca; explicacao de tempo ficticio mais precisa.
- `CF88:ART.40:PAR.11` — O nucleo afirmava como regra universal que o teto vale "sobre a soma" e que o total de duas aposentadorias licitamente acumuladas se sujeita ao teto; a jurisprudencia constitucional distingue hipoteses de acumulacao.
- `CF88:ART.40:PAR.12` — O draft definia a regra como puramente "subsidiaria", aplicavel so na omissao do art. 40 ou da lei do ente; essa condicao de omissao nao esta no § 12.
- `CF88:ART.40:PAR.13` — Evitar a generalizacao "o regime proprio e para quem ocupa cargo efetivo; os demais contribuem para o Regime Geral" (nem todo ente possui RPPS); "exclusivamente" e essencial.
- `CF88:ART.40:PAR.14` — Evitar "o regime proprio paga ate o teto do Regime Geral" como afirmacao absoluta (depende da instituicao do regime complementar e da situacao do servidor); nao afirmar genericamente que quem ingressou antes "continua com as regras anteriores".
- `CF88:ART.40:PAR.18` — Retirado "a leitura usual e"; regra ordinaria explicada objetivamente e coordenada com o art. 149, § 1º-A.
- `CF88:ART.40:PAR.19` — Retirada a finalidade especulativa ("incentivo para o servidor experiente"; "adia a necessidade de substitui-lo").
- `CF88:ART.40:PAR.20` — "Cada ente tem um unico regime proprio e uma unica gestora" qualificado (so o ente que possui RPPS); nao dizer que Poderes nao podem manter "fundos" separados; retirada a justificativa teleologica sobre reducao de custos.
- `CF88:ART.40:PAR.22` — A camada externa sugeria que a lei complementar federal especifica do § 22 ja foi editada; as fontes oficiais a tratam como pendente (art. 9º da EC 103/2019: Lei nº 9.717/1998 e regras transitorias). T1 revisado.

## `CF88:ART.40:PAR.7` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.7/BASE/1 → ENTENDA/CF88:ART.40:PAR.7/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: O draft afirmava que, com outra renda formal, a pensao "pode ficar abaixo do salario minimo"; nao transformar a ausencia da garantia em autorizacao generica para qualquer valor.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

O parágrafo remete à lei de cada ente a concessão da pensão por morte no regime próprio. Garante o piso do art. 201, § 2º, quando a pensão for a única fonte de renda formal do dependente, e manda a lei dar tratamento diferenciado à morte de agentes do § 4º-B por agressão sofrida no exercício ou em razão da função.

**Depois (v2):**

O § 7º deixa à lei do respectivo ente federativo a disciplina da pensão por morte no regime próprio.

Quando a pensão constituir a única fonte de renda formal auferida pelo dependente, deve ser observado o piso constitucional relacionado ao art. 201, § 2º.

A lei também deve dar tratamento diferenciado à morte dos servidores abrangidos pelo § 4º-B quando decorrente da agressão sofrida no exercício ou em razão da função.

### O QUE SIGNIFICA

**Antes (v1):**

A pensão por morte é o benefício pago aos dependentes do servidor que falece. A Constituição deixou para a lei de cada ente as regras de concessão e de valor.

Há duas garantias no próprio texto. A primeira é o piso: se a pensão é a única renda formal do dependente, ela não pode ser menor que o salário mínimo. A segunda é o tratamento diferenciado para a família do policial ou agente penitenciário ou socioeducativo que morre em razão de agressão sofrida no trabalho.

**Depois (v2):**

A pensão por morte é o benefício previdenciário destinado aos dependentes do servidor falecido.

A Constituição não define neste parágrafo toda a fórmula de cálculo nem todas as condições do benefício. Esses pontos dependem da legislação do respectivo ente.

Há, porém, uma proteção expressa: quando a pensão é a única fonte de renda formal do dependente, aplica-se a garantia constitucional do valor mínimo mencionada pelo dispositivo.

Também deve existir tratamento diferenciado para a pensão decorrente da morte, em determinadas circunstâncias, dos agentes indicados no § 4º-B.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um policial civil é morto durante uma operação. A lei do Estado deve prever tratamento diferenciado para a pensão dos seus dependentes. Já a pensão de um dependente que tem outra renda formal pode ficar abaixo do salário mínimo, se a lei do ente assim previr.

**Depois (v2):**

Um policial civil morre em decorrência de agressão sofrida durante o exercício de sua função.

A legislação previdenciária do Estado deverá tratar essa situação de forma diferenciada, conforme exige o § 7º.

### ATENÇÃO

**Antes (v1):**

O piso de um salário mínimo vale quando a pensão é a única fonte de renda formal do dependente. Os incisos antigos deste parágrafo, com as regras anteriores de cálculo, são históricos.

**Depois (v2):**

Se o dependente possuir outra fonte de renda formal, a garantia específica do piso prevista neste parágrafo não incide da mesma forma.

Isso não significa que o § 7º, isoladamente, determine qual será o valor da pensão nessa situação: o cálculo deve ser verificado na legislação aplicável.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Pensão por morte**: benefício pago aos dependentes de quem faleceu.
- **Dependente**: pessoa que a lei reconhece como beneficiária da pensão, como cônjuge e filhos.
- **Renda formal**: rendimento registrado, como salário, aposentadoria ou outro benefício.

**Depois (v2):**

- **Pensão por morte**: benefício previdenciário destinado aos dependentes do segurado falecido.
- **Dependente**: pessoa reconhecida pela legislação como beneficiária da pensão.
- **Renda formal**: renda considerada formalmente para fins da regra previdenciária aplicável.

## `CF88:ART.40:PAR.9` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.9/BASE/1 → ENTENDA/CF88:ART.40:PAR.9/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Evitar a ideia de que a mudanca de ente transfere automaticamente o tempo sem observar a contagem reciproca; explicacao de tempo ficticio mais precisa.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

O § 9º determina que o tempo de contribuição em qualquer esfera de governo seja contado para aposentadoria, observadas as regras de contagem recíproca do art. 201, §§ 9º e 9º-A, e que o tempo de serviço correspondente seja contado para disponibilidade. O § 10 proíbe a lei de criar tempo de contribuição fictício.

**Depois (v2):**

O § 9º assegura o aproveitamento do tempo de contribuição federal, estadual, distrital ou municipal para fins de aposentadoria, observadas as regras de contagem recíproca do art. 201.

O tempo de serviço correspondente é contado para fins de disponibilidade.

O § 10 impede que a lei crie formas de contagem de tempo de contribuição fictício.

### O QUE SIGNIFICA

**Antes (v1):**

O servidor que muda de ente, por exemplo de um Município para a União, não perde o tempo já contribuído: ele é levado em conta na nova aposentadoria. Os regimes acertam as contas entre si pela compensação financeira prevista no art. 201.

O § 10 completa a lógica contributiva do regime. Tempo fictício é aquele contado sem que tenha havido contribuição correspondente, como contar em dobro períodos de licença não gozada. A lei não pode criar esse tipo de contagem.

**Depois (v2):**

O tempo de contribuição realizado em determinado regime pode ser aproveitado em outro, dentro do sistema de contagem recíproca.

Esse aproveitamento deve observar as regras previdenciárias aplicáveis, inclusive a compensação financeira entre os regimes e a proibição de utilizar o mesmo período mais de uma vez.

O § 10 impede que a legislação acrescente artificialmente tempo previdenciário sem fundamento em período efetivamente reconhecido pelo sistema.

### EXEMPLO PRÁTICO

**Antes (v1):**

Uma servidora trabalhou dez anos como professora municipal e depois foi aprovada em concurso federal. Os dez anos de contribuição ao regime do Município contam para a sua aposentadoria pelo regime federal. Uma lei que mandasse contar em dobro, para aposentadoria, o tempo de licença não usufruída criaria tempo fictício.

**Depois (v2):**

Uma servidora contribuiu durante dez anos para um regime municipal e depois ingressou em cargo federal.

Esse período pode ser aproveitado para aposentadoria no novo regime por meio da contagem recíproca, observadas as regras legais correspondentes.

Já uma lei nova não pode simplesmente determinar que um ano sem efetiva correspondência previdenciária passe a valer como dois anos de contribuição.

### ATENÇÃO

**Antes (v1):**

O tempo de serviço contado para disponibilidade não se confunde com tempo de contribuição para aposentadoria. A situação de períodos fictícios reconhecidos antes da vedação depende de regras de transição.

**Depois (v2):**

Tempo de contribuição para aposentadoria e tempo de serviço para disponibilidade possuem finalidades diferentes.

Além disso, situações reconhecidas por regras antigas ou de transição devem ser examinadas segundo a legislação correspondente.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Contagem recíproca**: aproveitamento, em um regime previdenciário, do tempo de contribuição feito em outro.
- **Compensação financeira**: acerto de valores entre regimes previdenciários pelo tempo aproveitado.
- **Tempo fictício**: período contado para aposentadoria sem contribuição correspondente.
- **Disponibilidade**: situação do servidor estável que fica sem exercer o cargo, mas vinculado e remunerado proporcionalmente.

**Depois (v2):**

- **Contagem recíproca**: aproveitamento, em um regime previdenciário, de tempo reconhecido em outro regime.
- **Compensação financeira**: acerto entre regimes em razão do tempo previdenciário aproveitado.
- **Tempo fictício**: período artificialmente acrescentado ao tempo previdenciário sem correspondência admitida pelo ordenamento.
- **Disponibilidade**: situação constitucional do servidor estável afastado do exercício nas hipóteses previstas.

## `CF88:ART.40:PAR.11` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.11/BASE/1 → ENTENDA/CF88:ART.40:PAR.11/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: O nucleo afirmava como regra universal que o teto vale "sobre a soma" e que o total de duas aposentadorias licitamente acumuladas se sujeita ao teto; a jurisprudencia constitucional distingue hipoteses de acumulacao.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: LAW_DEPENDENCY_OMITTED (em lei) → falso positivo: "em lei" integra a expressao "cargo em comissao declarado em lei de livre nomeacao", nao remete a regulamentacao.

### O QUE DIZ

**Antes (v1):**

O parágrafo submete ao teto do art. 37, XI, a soma de todos os proventos de inatividade, inclusive os vindos de acumulação de cargos ou de outras atividades que contribuem para o Regime Geral. Também o aplica à soma de proventos com a remuneração de cargo acumulável, cargo em comissão ou cargo eletivo.

**Depois (v2):**

O texto do § 11 determina a aplicação do teto previsto no art. 37, XI, às combinações de proventos e remunerações que ele enumera.

O dispositivo menciona a soma de proventos de inatividade e também situações em que proventos são recebidos juntamente com remuneração decorrente de determinados vínculos.

### O QUE SIGNIFICA

**Antes (v1):**

O teto remuneratório também vale para aposentados, e vale sobre a soma.

Se o servidor tem duas aposentadorias públicas licitamente acumuladas, o total delas se sujeita ao teto. O mesmo acontece quando ele soma proventos a uma remuneração permitida, por exemplo de cargo em comissão ou de mandato eletivo.

O parágrafo fecha o caminho de quem tentaria contornar o teto somando vínculos diferentes.

**Depois (v2):**

O § 11 conecta os benefícios de inatividade ao teto constitucional do art. 37, XI.

Entretanto, a aplicação prática dessa regra não pode ser explicada apenas pela palavra “soma”.

A jurisprudência constitucional distingue diferentes tipos de acumulação.

Nas acumulações de vínculos constitucionalmente permitidas, há situações em que o teto é considerado separadamente em cada vínculo.

Já outras combinações, como determinadas acumulações de pensão com remuneração ou proventos, recebem tratamento diferente.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um professor aposentado por um Estado é nomeado para cargo em comissão de secretário municipal. Pelo texto do parágrafo, a soma dos proventos e da remuneração do cargo em comissão se submete ao teto.

**Depois (v2):**

Uma pessoa recebe simultaneamente valores decorrentes de mais de um vínculo público constitucionalmente admitido.

Não basta simplesmente somar todos os valores e aplicar o teto de forma automática.

É necessário identificar a natureza de cada vínculo e a jurisprudência aplicável àquela combinação.

### ATENÇÃO

**Antes (v1):**

O parágrafo fala em soma total. A forma de aplicar o teto em cada hipótese concreta de acumulação lícita é tema de interpretação, tratado na camada externa.

**Depois (v2):**

O § 11 possui redação ampla, mas sua aplicação foi interpretada pelo Supremo Tribunal Federal.

Por isso, o ENTENDA não deve transformar a expressão “soma total” em regra universal para toda acumulação constitucionalmente lícita.

A camada JURISPRUDÊNCIA deve apresentar as distinções.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Proventos de inatividade**: valores recebidos pelo servidor aposentado.
- **Cargo acumulável**: cargo que pode ser exercido junto com outro nas hipóteses admitidas pela Constituição.

**Depois (v2):**

- **Proventos de inatividade**: valores recebidos em razão da aposentadoria.
- **Teto remuneratório**: limite constitucional previsto no art. 37, XI.
- **Acumulação**: recebimento simultâneo de valores decorrentes de mais de um vínculo ou benefício.

### CAMADA EXTERNA

**Antes (v1):**

- Se o teto incide sobre a soma ou sobre cada vínculo acumulado licitamente é tema da camada JURISPRUDÊNCIA.

**Depois (v2):**

- Temas 377 e 384: nas acumulações constitucionalmente autorizadas de cargos, empregos e funções, o teto do art. 37, XI, é considerado em relação a cada vínculo, e não sobre o somatório.
- Tema 359: na hipótese abrangida pela tese, ocorrida a morte do instituidor da pensão após a EC 19/1998, o teto incide sobre o somatório de remuneração ou provento e pensão percebidos pelo servidor.

## `CF88:ART.40:PAR.12` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.12/BASE/1 → ENTENDA/CF88:ART.40:PAR.12/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: O draft definia a regra como puramente "subsidiaria", aplicavel so na omissao do art. 40 ou da lei do ente; essa condicao de omissao nao esta no § 12.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

O parágrafo determina que o regime próprio, além de seguir o art. 40, aplique no que couber os requisitos e critérios que valem para o Regime Geral de Previdência Social.

**Depois (v2):**

O § 12 determina que, além das regras próprias do art. 40, o regime próprio observe, no que couber, requisitos e critérios previstos para o Regime Geral de Previdência Social.

### O QUE SIGNIFICA

**Antes (v1):**

As regras do Regime Geral funcionam como complemento. Quando o art. 40 e a lei do ente não tratam de um ponto, e a regra do Regime Geral for compatível, ela pode ser usada no regime próprio.

A expressão "no que couber" é o filtro: só se aplica aquilo que for compatível com as características do regime dos servidores.

**Depois (v2):**

O regime próprio possui disciplina constitucional própria, mas não funciona de maneira completamente isolada do Regime Geral.

A Constituição determina que requisitos e critérios do RGPS também sejam observados quando forem compatíveis com o regime dos servidores.

A expressão decisiva é “no que couber”.

Ela exige verificar se determinada regra do Regime Geral pode ser aplicada à situação do regime próprio sem contrariar as normas específicas deste.

### EXEMPLO PRÁTICO

**Antes (v1):**

A lei de um regime próprio não define certo critério de comprovação de dependência para a pensão. Se o Regime Geral tem critério compatível sobre o tema, ele pode ser aplicado ao regime próprio, no que couber.

**Depois (v2):**

Ao analisar determinada exigência previdenciária de um regime próprio, pode ser necessário verificar também o critério correspondente utilizado no Regime Geral.

Esse critério somente será aplicado na medida em que seja compatível com a disciplina constitucional e legal do RPPS.

### ATENÇÃO

**Antes (v1):**

A aplicação é subsidiária e condicionada à compatibilidade. Ela não substitui as regras próprias do art. 40 nem as da lei do ente.

**Depois (v2):**

O § 12 não diz que as regras do RGPS somente podem ser utilizadas quando existir uma lacuna.

Ele determina sua observância “no que couber”, isto é, conforme a compatibilidade com o regime próprio.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Aplicação subsidiária**: uso de uma regra para completar outra quando esta é omissa.
- **No que couber**: na medida em que for compatível com a situação regulada.

**Depois (v2):**

- **Regime Geral de Previdência Social**: regime previdenciário geral previsto no art. 201 da Constituição.
- **No que couber**: na medida em que determinada regra seja compatível com a situação regulada.

## `CF88:ART.40:PAR.13` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.13/BASE/1 → ENTENDA/CF88:ART.40:PAR.13/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Evitar a generalizacao "o regime proprio e para quem ocupa cargo efetivo; os demais contribuem para o Regime Geral" (nem todo ente possui RPPS); "exclusivamente" e essencial.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: LAW_DEPENDENCY_OMITTED (em lei) → falso positivo: "em lei" integra a expressao "cargo em comissao declarado em lei de livre nomeacao", nao remete a regulamentacao.

### O QUE DIZ

**Antes (v1):**

O parágrafo vincula ao Regime Geral o agente público que ocupa só cargo em comissão de livre nomeação e exoneração, outro cargo temporário, inclusive mandato eletivo, ou emprego público.

**Depois (v2):**

O § 13 determina a aplicação do Regime Geral de Previdência Social ao agente público cujo vínculo seja exclusivamente cargo em comissão de livre nomeação e exoneração, outro cargo temporário, inclusive mandato eletivo, ou emprego público.

### O QUE SIGNIFICA

**Antes (v1):**

O regime próprio é para quem ocupa cargo efetivo. Os demais agentes públicos contribuem para o Regime Geral, o mesmo dos trabalhadores da iniciativa privada.

A palavra "exclusivamente" é decisiva. Se a pessoa ocupa apenas um cargo em comissão, sem vínculo efetivo, vai para o Regime Geral. Se é servidora efetiva e exerce um cargo em comissão, continua no regime próprio pelo seu cargo efetivo.

O mesmo vale para mandato eletivo, contratação temporária e emprego público.

**Depois (v2):**

O dispositivo separa essas espécies de vínculo do regime próprio disciplinado pelo art. 40.

Quem possui apenas um dos vínculos indicados no § 13 fica submetido ao Regime Geral.

A palavra “exclusivamente” é importante porque a situação de quem também possui cargo efetivo e vínculo previdenciário próprio deve ser analisada de acordo com esse outro vínculo e com as demais regras constitucionais.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um advogado sem vínculo com a administração é nomeado assessor em cargo em comissão de um Estado: ele contribui para o Regime Geral. Já uma auditora efetiva do mesmo Estado, nomeada para o mesmo tipo de cargo, continua vinculada ao regime próprio estadual.

**Depois (v2):**

Uma pessoa sem cargo efetivo é nomeada exclusivamente para cargo em comissão em um Estado.

Seu vínculo previdenciário decorrente daquele cargo é com o Regime Geral.

Já a situação de um servidor efetivo que assume função ou mandato adicional não deve ser resolvida ignorando o vínculo efetivo que ele já possui.

### ATENÇÃO

**Antes (v1):**

O servidor efetivo que exerce mandato eletivo segue a regra do art. 38, V: permanece no regime próprio do ente de origem.

**Depois (v2):**

O art. 38, V, contém regra específica para o servidor segurado de regime próprio que exerce mandato eletivo: ele permanece filiado ao regime próprio do ente de origem.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Cargo temporário**: cargo exercido por prazo determinado, sem vínculo efetivo.
- **Emprego público**: vínculo de trabalho com a administração regido pela legislação trabalhista.

**Depois (v2):**

- **Cargo em comissão**: cargo de livre nomeação e exoneração, nas hipóteses constitucionais.
- **Emprego público**: vínculo de trabalho com entidade pública submetido ao regime trabalhista.
- **Vínculo previdenciário**: relação da pessoa com determinado regime de previdência.

## `CF88:ART.40:PAR.14` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.14/BASE/1 → ENTENDA/CF88:ART.40:PAR.14/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Evitar "o regime proprio paga ate o teto do Regime Geral" como afirmacao absoluta (depende da instituicao do regime complementar e da situacao do servidor); nao afirmar genericamente que quem ingressou antes "continua com as regras anteriores".
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: ABSOLUTE_CLAIM (automaticamente) → negacao ("nao significa que a previdencia complementar pagara automaticamente a diferenca"): afasta leitura indevida.

### O QUE DIZ

**Antes (v1):**

O § 14 obriga todos os entes a instituir, por lei de iniciativa do Executivo, previdência complementar para os servidores efetivos, limitando os benefícios do regime próprio ao teto do Regime Geral, ressalvado o § 16. O § 15 exige plano na modalidade contribuição definida, por entidade fechada ou aberta. O § 16 só aplica essas regras a quem ingressou antes da instituição se houver opção prévia e expressa.

**Depois (v2):**

O § 14 determina que os entes instituam regime de previdência complementar para os servidores ocupantes de cargo efetivo.

Com a aplicação desse regime, o valor das aposentadorias e pensões do RPPS observa o limite máximo dos benefícios do Regime Geral, ressalvada a situação prevista no § 16.

O § 15 determina que o plano complementar utilize a modalidade de contribuição definida e seja administrado pelas entidades admitidas constitucionalmente.

O § 16 protege quem ingressou no serviço público antes da instituição do correspondente regime complementar: a aplicação dos §§ 14 e 15 a esse servidor depende de opção prévia e expressa.

### O QUE SIGNIFICA

**Antes (v1):**

O regime próprio paga até o teto do Regime Geral. Acima disso, o servidor pode formar uma reserva na previdência complementar, baseada em contribuições.

Na contribuição definida, sabe-se quanto se contribui, mas o valor do benefício depende do que for acumulado e rendido. É diferente do benefício definido, em que o valor é prometido de antemão.

O § 16 protege quem já era servidor quando o regime complementar foi criado: ele só passa a ter o benefício limitado ao teto se optar por isso, de forma prévia e expressa.

**Depois (v2):**

A previdência complementar cria uma separação entre o benefício básico pago pelo RPPS, dentro dos limites constitucionais aplicáveis, e o benefício adicional que pode resultar do plano complementar.

Na modalidade de contribuição definida, são conhecidas as contribuições feitas para o plano, enquanto o benefício futuro depende do saldo formado e das regras do plano.

Para quem já estava no serviço público antes da instituição do regime complementar correspondente, a Constituição exige opção prévia e expressa para aplicar as regras dos §§ 14 e 15.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um servidor que tomou posse depois da criação da previdência complementar federal terá aposentadoria do regime próprio limitada ao teto do Regime Geral e pode aderir ao plano complementar. Um colega que ingressou antes continua com as regras anteriores, a menos que opte pela migração.

**Depois (v2):**

Um servidor ingressa depois da instituição do regime de previdência complementar do seu ente.

A limitação constitucional do benefício do RPPS ao teto do Regime Geral incide segundo esse regime, independentemente de o servidor decidir realizar contribuições adicionais a um plano complementar.

Já para servidor que ingressou antes do marco de instituição, a aplicação dos §§ 14 e 15 depende da opção prevista no § 16.

### ATENÇÃO

**Antes (v1):**

A instituição da previdência complementar é obrigatória para os entes, nos termos do § 14. As condições específicas de adesão e de migração estão nas leis de cada ente e nas regras de transição.

**Depois (v2):**

A limitação do benefício do RPPS ao teto do Regime Geral não significa que a previdência complementar pagará automaticamente a diferença entre a remuneração do servidor e esse teto.

O valor de eventual benefício complementar depende das contribuições, do saldo acumulado e das regras do plano.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Contribuição definida**: modalidade em que o benefício depende do saldo acumulado com as contribuições e os rendimentos.
- **Entidade fechada de previdência complementar**: entidade sem fins lucrativos que administra planos para grupos determinados.
- **Opção prévia e expressa**: escolha formal do servidor, manifestada antes de as regras serem aplicadas a ele.

**Depois (v2):**

- **Previdência complementar**: regime previdenciário adicional ao regime básico.
- **Contribuição definida**: modalidade em que as contribuições são definidas e o benefício depende do saldo acumulado.
- **Opção prévia e expressa**: manifestação formal necessária antes da aplicação da regra ao servidor abrangido pelo § 16.

### CAMADA EXTERNA

**Antes (v1):**

- Regras de transição para quem já era servidor antes da Emenda Constitucional nº 103/2019, e a situação de Estados, Distrito Federal e Municípios que ainda não adaptaram as suas normas, estão na própria emenda e na legislação de cada ente (camada externa); não estão escritas no art. 40.

**Depois (v2):**

- Regras de transição para quem já era servidor antes da Emenda Constitucional nº 103/2019, e a situação de Estados, Distrito Federal e Municípios que ainda não adaptaram as suas normas, estão na própria emenda e na legislação de cada ente (camada externa); não estão escritas no art. 40.
- A aplicação concreta do teto do Regime Geral depende do marco de instituição do regime de previdência complementar de cada ente e da situação do servidor perante o § 16.

## `CF88:ART.40:PAR.18` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.18/BASE/1 → ENTENDA/CF88:ART.40:PAR.18/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Retirado "a leitura usual e"; regra ordinaria explicada objetivamente e coordenada com o art. 149, § 1º-A.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

O parágrafo prevê contribuição sobre as aposentadorias e pensões do regime próprio na parte que superar o teto de benefícios do Regime Geral, com o mesmo percentual cobrado dos servidores efetivos em atividade.

**Depois (v2):**

O § 18 prevê contribuição previdenciária sobre aposentadorias e pensões do regime próprio que ultrapassem o limite máximo dos benefícios do Regime Geral.

A contribuição segue o percentual previsto para os servidores titulares de cargos efetivos, conforme o regime aplicável.

### O QUE SIGNIFICA

**Antes (v1):**

Aposentados e pensionistas também contribuem, o que expressa o caráter solidário do caput. Este parágrafo usa como referência o teto do Regime Geral: a contribuição alcança os benefícios que o superam, e a leitura usual é que ela recai sobre a parte excedente.

O percentual é o mesmo exigido dos servidores ativos.

Outro dispositivo da Constituição, o art. 149, § 1º-A, permite que, havendo déficit atuarial, a contribuição de aposentados e pensionistas incida sobre o valor que supere o salário mínimo.

**Depois (v2):**

Na situação ordinária prevista pelo § 18, a contribuição do aposentado ou pensionista incide sobre a parcela do benefício que ultrapassa o teto do Regime Geral.

Assim, não se trata de contribuição calculada necessariamente sobre o valor inteiro da aposentadoria ou pensão.

A Constituição, porém, contém outra regra relevante no art. 149, § 1º-A.

Quando houver déficit atuarial, esse dispositivo permite que a contribuição ordinária dos aposentados e pensionistas alcance a parcela que exceder o salário mínimo, conforme a disciplina legal aplicável.

### EXEMPLO PRÁTICO

**Antes (v1):**

Uma aposentada recebe proventos acima do teto do Regime Geral. Pela regra deste parágrafo, a contribuição recai sobre o valor que excede esse teto, com o mesmo percentual aplicado aos servidores em atividade do seu ente.

**Depois (v2):**

Se um aposentado recebe benefício acima do teto do Regime Geral e não existe hipótese constitucional de ampliação da base, a contribuição ordinária incide sobre a parcela que ultrapassa aquele teto.

Se existir déficit atuarial e forem preenchidos os requisitos do art. 149, § 1º-A, a legislação pode estabelecer a base ampliada admitida pela Constituição.

### ATENÇÃO

**Antes (v1):**

O parágrafo não é a única regra sobre a contribuição de inativos: a base ampliada em caso de déficit está no art. 149, § 1º-A, e as alíquotas dependem da lei de cada ente.

**Depois (v2):**

O § 18 não deve ser lido isoladamente.

O art. 149, § 1º-A, contém regra excepcional relacionada a déficit atuarial que pode alterar a faixa sobre a qual a contribuição de aposentados e pensionistas incide.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Base de contribuição**: parcela do valor recebido sobre a qual a contribuição é calculada.
- **Alíquota**: percentual aplicado sobre a base para calcular a contribuição.
- **Déficit atuarial**: diferença projetada entre os benefícios futuros e os recursos para pagá-los.
- **Pensionista**: dependente que recebe pensão por morte do servidor.

**Depois (v2):**

- **Base de contribuição**: valor sobre o qual a contribuição previdenciária é calculada.
- **Alíquota**: percentual utilizado para calcular a contribuição.
- **Déficit atuarial**: insuficiência projetada de recursos para cobrir as obrigações futuras do regime.
- **Pensionista**: beneficiário de pensão previdenciária.

### CAMADA EXTERNA

**Antes (v1):**

- Regras de transição para quem já era servidor antes da Emenda Constitucional nº 103/2019, e a situação de Estados, Distrito Federal e Municípios que ainda não adaptaram as suas normas, estão na própria emenda e na legislação de cada ente (camada externa); não estão escritas no art. 40.

**Depois (v2):**

- Art. 149, § 1º-A.

## `CF88:ART.40:PAR.19` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.19/BASE/1 → ENTENDA/CF88:ART.40:PAR.19/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Retirada a finalidade especulativa ("incentivo para o servidor experiente"; "adia a necessidade de substitui-lo").
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: ABSOLUTE_CLAIM (automaticamente) → negacao ("nao permite concluir que todo servidor ... recebera automaticamente"): afasta leitura indevida.

### O QUE DIZ

**Antes (v1):**

O parágrafo permite que o servidor efetivo que já cumpriu as exigências da aposentadoria voluntária e decide continuar trabalhando receba um abono de permanência. O abono pode chegar, no máximo, ao valor da sua contribuição previdenciária e vai até a idade da compulsória, segundo critérios da lei do ente.

**Depois (v2):**

O § 19 permite que o servidor titular de cargo efetivo que já cumpriu as exigências para aposentadoria voluntária e opta por permanecer em atividade possa receber abono de permanência.

Os critérios são definidos em lei do respectivo ente e o valor não pode superar o montante da contribuição previdenciária do servidor.

### O QUE SIGNIFICA

**Antes (v1):**

O abono é um incentivo para o servidor experiente continuar em atividade, em vez de se aposentar. Para a administração, isso adia a necessidade de substituí-lo.

O valor máximo é o da contribuição previdenciária do servidor; o texto usa "no máximo", o que permite valores menores conforme a lei. O pagamento termina quando o servidor atinge a idade da aposentadoria compulsória.

O texto atual usa "poderá fazer jus" e remete à lei do ente os critérios.

**Depois (v2):**

O servidor que já possui os requisitos para pedir aposentadoria voluntária pode escolher continuar em atividade.

Nessa situação, a legislação do ente pode prever o abono de permanência.

A Constituição não fixa um valor obrigatório igual à contribuição previdenciária: ela estabelece essa contribuição como limite máximo do abono.

O benefício pode ser pago até a idade da aposentadoria compulsória, conforme as regras aplicáveis.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um servidor federal cumpre os requisitos da aposentadoria voluntária, mas decide continuar trabalhando. Conforme a lei aplicável, ele passa a receber o abono de permanência, de valor equivalente, no máximo, à sua contribuição, até atingir a idade da compulsória.

**Depois (v2):**

Uma servidora cumpre os requisitos para aposentadoria voluntária, mas prefere continuar exercendo seu cargo.

Se preencher os critérios estabelecidos pela lei do ente, poderá receber abono de permanência dentro do limite constitucional.

### ATENÇÃO

**Antes (v1):**

O abono depende dos critérios da lei de cada ente. O texto não garante que o valor seja igual à contribuição: ela é o limite máximo.

**Depois (v2):**

A expressão “poderá fazer jus” e a remissão à lei do ente são importantes.

O § 19 não permite concluir que todo servidor que permanece em atividade receberá automaticamente valor idêntico à sua contribuição previdenciária.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Abono de permanência**: valor pago ao servidor que já pode se aposentar e continua trabalhando.
- **Fazer jus**: ter direito a receber algo, por cumprir as condições exigidas.
- **Aposentadoria compulsória**: aposentadoria obrigatória ao atingir a idade-limite fixada pela Constituição e pela lei.

**Depois (v2):**

- **Abono de permanência**: valor que pode ser devido ao servidor que já cumpriu os requisitos para aposentadoria voluntária e permanece em atividade.
- **Aposentadoria compulsória**: aposentadoria obrigatória ao atingir a idade-limite aplicável.

## `CF88:ART.40:PAR.20` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.20/BASE/1 → ENTENDA/CF88:ART.40:PAR.20/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: "Cada ente tem um unico regime proprio e uma unica gestora" qualificado (so o ente que possui RPPS); nao dizer que Poderes nao podem manter "fundos" separados; retirada a justificativa teleologica sobre reducao de custos.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: LAW_DEPENDENCY_OMITTED (lei complementar) → o corpo remete a "legislacao aplicavel"; a lei complementar do § 22, a que o § 20 se refere, e explicada no BLOCK CF88:ART.40:PAR.22.; TECHNICAL_TERM_UNDEFINED (autarquia) → termo do proprio texto oficial do § 20; definido em CF88:ART.37:INC.XIX.

### O QUE DIZ

**Antes (v1):**

O parágrafo proíbe que um ente federativo tenha mais de um regime próprio de previdência ou mais de um órgão ou entidade gestora desse regime. Todos os Poderes, órgãos, autarquias e fundações ficam no mesmo regime e respondem pelo seu financiamento, conforme a lei complementar do § 22.

**Depois (v2):**

O § 20 impede que um mesmo ente federativo mantenha mais de um regime próprio de previdência social ou mais de um órgão ou entidade responsável por sua gestão.

O regime existente deve abranger os Poderes, órgãos, autarquias e fundações alcançados pelo dispositivo, que participam de seu financiamento.

### O QUE SIGNIFICA

**Antes (v1):**

Cada ente tem um único regime próprio e uma única gestora. Assim, o Judiciário, o Legislativo e o Executivo de um Estado não podem manter fundos ou institutos previdenciários separados.

A unicidade facilita o controle, reduz custos administrativos e dá transparência ao equilíbrio do regime. Ao mesmo tempo, cada Poder e entidade continua responsável por financiar a parte do regime que lhe corresponde.

**Depois (v2):**

Se União, Estado, Distrito Federal ou Município possui RPPS, não pode fragmentá-lo em vários regimes previdenciários independentes para cada Poder ou órgão.

Também deve existir uma única estrutura gestora do regime, nos termos das normas constitucionais e da legislação aplicável.

Isso não significa que toda organização financeira interna do RPPS seja proibida: a vedação constitucional é à existência de vários regimes próprios ou de várias entidades gestoras para o mesmo ente.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um Estado mantinha um instituto de previdência para o Executivo e outro para o Tribunal de Justiça. Pelo parágrafo, os servidores dos dois Poderes devem integrar um único regime, administrado por uma só entidade gestora.

**Depois (v2):**

Um Estado não pode manter um RPPS independente para o Executivo e outro RPPS separado para os servidores do Judiciário.

Os servidores abrangidos integram o regime próprio único do Estado, sujeito à estrutura de gestão prevista pela legislação.

### ATENÇÃO

**Antes (v1):**

A unicidade é de regime e de gestora, não de orçamento: cada Poder e entidade responde pelo financiamento, nos termos da lei complementar federal do § 22.

**Depois (v2):**

A unicidade prevista no § 20 refere-se ao regime próprio e ao órgão ou entidade gestora.

Os Poderes, órgãos e entidades abrangidos continuam responsáveis pelo financiamento do sistema nas condições previstas constitucional e legalmente.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Entidade gestora**: órgão ou entidade que administra o regime próprio de previdência do ente.
- **Financiamento**: aporte dos recursos necessários para pagar os benefícios do regime.
- **Autarquia**: entidade de direito público criada por lei para executar atividade típica do Estado.

**Depois (v2):**

- **Entidade gestora**: estrutura responsável pela administração do regime próprio.
- **Financiamento**: conjunto dos recursos destinados ao custeio do sistema previdenciário.
- **Regime próprio**: regime previdenciário dos servidores titulares de cargos efetivos abrangidos por ele.

## `CF88:ART.40:PAR.22` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.22/BASE/1 → ENTENDA/CF88:ART.40:PAR.22/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: A camada externa sugeria que a lei complementar federal especifica do § 22 ja foi editada; as fontes oficiais a tratam como pendente (art. 9º da EC 103/2019: Lei nº 9.717/1998 e regras transitorias). T1 revisado.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: EXTRAPOLATION_NUMBER (2019) → ano da EC 103/2019, que incluiu o § 22 (registro de vigencia ART40 da fonte estrutural canonica); a disciplina transitoria do art. 9º tem proveniencia HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE.

### O QUE DIZ

**Antes (v1):**

O parágrafo proíbe criar novos regimes próprios de previdência. Para os que já existem, manda uma lei complementar federal fixar normas gerais de organização, funcionamento e responsabilidade da gestão. Os incisos listam temas dessa lei, como extinção e migração para o Regime Geral, uso dos recursos, fiscalização, equilíbrio atuarial, déficit, governança e alíquotas.

**Depois (v2):**

O § 22 proíbe a instituição de novos regimes próprios de previdência social.

Para os RPPS já existentes, determina que lei complementar federal estabeleça normas gerais sobre organização, funcionamento e responsabilidade na gestão.

Os incisos I a X indicam matérias que essa disciplina deve abranger.

### O QUE SIGNIFICA

**Antes (v1):**

Com a vedação, o ente que não tem regime próprio não pode criá-lo, e os seus servidores efetivos ficam no Regime Geral.

Os regimes que já existem continuam, mas sob normas gerais nacionais. A lei complementar federal define regras comuns de boa gestão, controle e responsabilidade.

Os incisos mostram as preocupações centrais: permitir a extinção do regime e a migração ordenada dos servidores para o Regime Geral; organizar a arrecadação e o uso dos recursos; garantir fiscalização da União e controle externo e social; definir equilíbrio atuarial e formas de equacionar o déficit; estruturar a gestora com governança e transparência; responsabilizar gestores; permitir consórcios; e fixar parâmetros de base de cálculo e alíquotas, inclusive extraordinárias.

**Depois (v2):**

Depois da reforma previdenciária de 2019, um ente que não possuía regime próprio não pode criar um novo RPPS.

Os regimes que já existiam podem continuar funcionando, mas estão submetidos às normas constitucionais e às normas gerais federais aplicáveis.

Os incisos mostram os principais assuntos que a disciplina nacional deve tratar, entre eles:

* extinção do RPPS e migração para o Regime Geral;

* arrecadação e utilização dos recursos;

* fiscalização e controle;

* equilíbrio financeiro e atuarial;

* mecanismos para enfrentar déficit;

* estrutura e governança da entidade gestora;

* responsabilização de gestores;

* consórcios públicos;

* parâmetros para contribuições ordinárias e extraordinárias.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um Município sem regime próprio pretende criar um para os seus servidores efetivos. A vedação do parágrafo impede isso, e os servidores continuam no Regime Geral. Um Município que já tem regime próprio deve seguir as normas gerais da lei complementar federal sobre gestão e equilíbrio.

**Depois (v2):**

Um Município que não possuía RPPS quando entrou em vigor a vedação constitucional não pode instituir um novo regime próprio para seus servidores.

Já um Município que mantém RPPS anterior à reforma continua submetido às normas constitucionais e às normas gerais federais aplicáveis à gestão desse regime.

### ATENÇÃO

**Antes (v1):**

O parágrafo trata de normas gerais nacionais; cada ente continua a editar a sua própria legislação dentro desses limites. A lista dos incisos é exemplificativa: o texto diz "entre outros aspectos".

**Depois (v2):**

A lista dos incisos não é exaustiva: o próprio § 22 utiliza a expressão “entre outros aspectos”.

A lei complementar federal específica prevista pelo § 22 deve ser acompanhada na camada de legislação correlata.

Enquanto essa regulamentação específica não entra em vigor, a EC 103/2019 contém disciplina transitória para os regimes próprios existentes.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Normas gerais**: regras nacionais que estabelecem bases comuns, deixando aos entes o detalhamento.
- **Déficit atuarial**: diferença projetada entre os benefícios futuros e os recursos para pagá-los.
- **Consórcio público**: associação entre entes federativos para gerir em conjunto uma atividade.

**Depois (v2):**

- **Normas gerais**: regras nacionais que estabelecem parâmetros comuns para os regimes próprios.
- **Déficit atuarial**: insuficiência projetada de recursos para cobrir obrigações previdenciárias futuras.
- **Governança**: conjunto de mecanismos de direção, controle e responsabilização da gestão.
- **Consórcio público**: forma de cooperação entre entes federativos para executar atividades de interesse comum.

### CAMADA EXTERNA

**Antes (v1):**

- A lei complementar federal de normas gerais dos regimes próprios está na camada de leis correlatas.

**Depois (v2):**

- EC 103/2019, art. 9º: enquanto não entrar em vigor a lei complementar que discipline o § 22, aplicam-se aos regimes próprios a Lei nº 9.717/1998 e as regras previstas no próprio art. 9º da EC 103/2019.

