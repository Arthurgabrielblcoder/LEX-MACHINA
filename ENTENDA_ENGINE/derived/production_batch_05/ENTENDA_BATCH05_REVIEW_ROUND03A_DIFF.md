# ENTENDA BATCH05 — RODADA 03A — DIFF EDITORIAL (art. 40, 1ª metade, HIGH)

- Revisão: `ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW` · escopo `CF88_ART40_HIGH_ROUND_3A` · 2026-10-04
- Resultado: 11 revisados · 3 APROVADOS sem alteração · 8 AJUSTAR · 0 REJEITADOS
- `ROUND03A_ART40_HIGH_HUMAN_APPROVED`: 11 de 11.
- `CF88:ART.40:PAR.3` (BLOCK §§ 3º/17), `CF88:ART.40:PAR.1:INC.III` e `CF88:ART.40:PAR.4-A` (BLOCK §§ 4º-A–4º-C) → `HUMAN_APPROVED_T1` (v1, conteúdo inalterado; nenhum microajuste foi necessário).
- 8 itens AJUSTAR → `editorial_version` 2 → `HUMAN_APPROVED_T1` direto, conforme a **política de microajustes T1 pré-autorizada** nesta rodada (só houve desvios dessa política). As v1 permanecem como `RETIRED` / `CHANGES_REQUESTED`.
- Drafts anteriores em `BATCH_05_DRAFTS_PRE_ROUND3A.json`. Targets, papel e cobertura de BLOCK inalterados. Rodadas 01–02, pilotos e itens da 03B inalterados.
- O texto da revisão chegou quebrado em linhas de ~60 colunas. Foi guardado como recebido (`raw_wrapped`) e convertido por regra determinística: quebras unidas por espaço, exceto após ". : ;" seguido de início de frase (novo parágrafo). O teste confere a conversão.

## Desvios T1 (2) — política pré-autorizada

| Target | Seção | Texto do revisor | Texto aplicado | Item da política | Motivo |
|---|---|---|---|---|---|
| `CF88:ART.40` | o_que_diz | regime próprio de previdência social dos servidores titulares | regime próprio de previdência social para os servidores titulares | 2 (trocar artigo, preposicao, ordem sintatica ou sinonimo exclusivamente para evitar NEAR_COPY_OF_OFFICIAL_TEXT) | ENTENDA_COPIES_OFFICIAL_TEXT: 11 palavras seguidas do caput oficial; preposicao "dos" -> "para os" |
| `CF88:ART.40:PAR.5` | o_que_diz | tempo de efetivo exercício das funções de | tempo de efetivo exercício nas funções de | 2 (trocar artigo, preposicao, ordem sintatica ou sinonimo exclusivamente para evitar NEAR_COPY_OF_OFFICIAL_TEXT) | ENTENDA_COPIES_OFFICIAL_TEXT: 12 palavras seguidas do § 5º oficial; preposicao "das" -> "nas" |

Prova automática (`test_round3a_pre_authorized_t1_policy`): conteúdo = texto do revisor + desvios registrados; nenhum número alterado; nos desvios do item 2 só diferem palavras funcionais (artigos/preposições).

## Camada externa e proveniência

- `CF88:ART.40`, caput, §§ 2º e 4º, § 1º I: notas existentes mantidas ("Manter" / sem instrução de alteração).
- `CF88:ART.40:PAR.5`: nota antiga substituída por: Tema 965 e ADI 3.772 do Supremo Tribunal Federal (direção, coordenação e assessoramento pedagógico por professores de carreira na educação básica, nas condições da jurisprudência).
- `CF88:ART.40:PAR.1:INC.II`: nota substituída por "Lei Complementar nº 152/2015."
- `CF88:ART.40:PAR.6`: nota existente mantida e acrescentada a nota sobre os Temas 377 e 384 (teto em acumulações), sem reproduzir no núcleo T1.
- Proveniência `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`: art. 40 ("nem todo ente possui RPPS"), § 5º (Tema 965/ADI 3.772), § 1º II (LC 152/2015, também no corpo), § 6º (Temas 377/384).

## editorial_checks

- 8 alertas novos gerados pelo texto do revisor, resolvidos sem alterar texto: "pensionista" (caput), "automaticamente" em negação (§ 2º), frase longa e idades 65/60 (§ 5º), "proventos" (§ 1º I), ano 2015 (§ 1º II). Resultado: 0 sem resolução.

## Aprovados sem alteração

- `CF88:ART.40` — Nao afirmar que todos os servidores efetivos necessariamente se aposentam por RPPS: o art. 40 disciplina os regimes proprios existentes; nem todo ente possui RPPS e o § 22 veda a instituicao de novos regimes proprios.
- `CF88:ART.40:CAPUT` — "Contributivo" nao deve ser explicado apenas como "o direito ao beneficio depende de contribuicao"; nao afirmar que todos os aposentados e pensionistas contribuem da mesma maneira (incidencia concreta tratada por outras normas).
- `CF88:ART.40:PAR.1:INC.I` — Nao exigir incapacidade para "qualquer atividade compativel com a formacao" (a Constituicao fala em incapacidade permanente no cargo e impossibilidade de readaptacao); nao afirmar automaticamente a consequencia de eventual melhora nas avaliacoes.
- `CF88:ART.40:PAR.1:INC.II` — O texto constitucional fala em 70 ou 75 anos na forma de lei complementar, mas a legislacao complementar atual ja regulamentou a hipotese.
- `CF88:ART.40:PAR.1:INC.III` — Distingue corretamente idade constitucional da Uniao, idade definida pelos demais entes, necessidade de outros requisitos, regras de transicao externas ao inciso e reducao especifica dos professores.
- `CF88:ART.40:PAR.2` — Retirada a ideia de que quem ultrapassa o teto do RGPS simplesmente "busca a diferenca" na previdencia complementar: a existencia e o valor de eventual beneficio complementar dependem do regime e do plano aplicavel.
- `CF88:ART.40:PAR.3` — BLOCK §§ 3º e 17 aprovado sem alteracao juridica.
- `CF88:ART.40:PAR.4` — Evitar dizer que "todos os servidores se aposentam pelas mesmas regras gerais", porque regras concretas podem variar entre entes e beneficios.
- `CF88:ART.40:PAR.4-A` — Preserva tres grupos constitucionais, necessidade de lei complementar, avaliacao biopsicossocial no § 4º-A, grupos do § 4º-B, exposicao efetiva no § 4º-C e impossibilidade de reconhecimento apenas pela categoria profissional.
- `CF88:ART.40:PAR.5` — Nao definir "magisterio" simplesmente como atividade em sala de aula.
- `CF88:ART.40:PAR.6` — Retirada a afirmacao categorica "Todas as somas se sujeitam ao teto (§ 11)": a relacao entre teto e acumulacoes constitucionalmente admitidas possui tratamento jurisprudencial.

## `CF88:ART.40` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40/BASE/1 → ENTENDA/CF88:ART.40/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Nao afirmar que todos os servidores efetivos necessariamente se aposentam por RPPS: o art. 40 disciplina os regimes proprios existentes; nem todo ente possui RPPS e o § 22 veda a instituicao de novos regimes proprios.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: EXTRAPOLATION_NUMBER (2019) → ano da Emenda Constitucional nº 103/2019, origem confirmada na fonte estrutural canonica do projeto (anotacoes "Redacao dada pela EC 103/2019").

### O QUE DIZ

**Antes (v1):**

O art. 40 disciplina o regime próprio de previdência social dos servidores titulares de cargo efetivo. O caput define o caráter do regime. Os parágrafos tratam das hipóteses de aposentadoria, do valor e do cálculo dos proventos, das aposentadorias com critérios diferenciados, da pensão por morte, da contagem de tempo, das vedações de acumulação, da previdência complementar e da organização dos regimes próprios.

**Depois (v2):**

O art. 40 disciplina o regime próprio de previdência social para os servidores titulares de cargos efetivos abrangidos por esse regime.

O artigo trata do financiamento do regime, das modalidades de aposentadoria, do cálculo e dos limites dos benefícios, das hipóteses com critérios diferenciados, da pensão por morte, da acumulação de benefícios, da previdência complementar e da organização dos regimes próprios.

### O QUE SIGNIFICA

**Antes (v1):**

Os servidores efetivos não se aposentam pelo INSS, mas por um regime próprio, organizado por cada ente: União, Estados, Distrito Federal e Municípios que tenham esse regime.

O texto atual do artigo resulta, em grande parte, da reforma da previdência de 2019. O desenho é este. O caput fixa os fundamentos: contribuição, solidariedade e equilíbrio entre receitas e despesas. O § 1º lista as hipóteses de aposentadoria. Os §§ 2º, 3º, 8º e 17 tratam do valor, do cálculo e da atualização dos benefícios. O § 4º proíbe critérios diferenciados, com as exceções dos §§ 4º-A a 5º. Os §§ 6º, 7º, 9º a 13, 18 e 19 tratam de acumulação, pensão, tempo de contribuição, teto, regras subsidiárias, contribuição de inativos e abono de permanência. Os §§ 14 a 16 criam a previdência complementar, e os §§ 20 e 22 organizam os regimes próprios.

Muitas regras dependem de lei do respectivo ente federativo, o que faz o regime variar entre a União, os Estados e os Municípios.

**Depois (v2):**

O regime próprio de previdência social, ou RPPS, é o sistema previdenciário mantido por determinado ente federativo para os servidores titulares de cargos efetivos que estejam abrangidos por esse regime.

O art. 40 estabelece a estrutura constitucional permanente dos RPPS.

O caput trata do financiamento e do equilíbrio do sistema.

O § 1º apresenta as modalidades de aposentadoria. Outros parágrafos disciplinam cálculo, limites, critérios diferenciados, pensão, acumulação, previdência complementar e organização do regime.

Nem todo ente federativo possui RPPS. Além disso, o § 22 veda a instituição de novos regimes próprios e determina que lei complementar federal estabeleça normas gerais para os que já existam.

### EXEMPLO PRÁTICO

**Antes (v1):**

Uma servidora efetiva de um Estado contribui mensalmente para o regime próprio estadual. Ao preencher os requisitos fixados pela Constituição e pela lei do Estado, ela se aposenta por esse regime, e o valor dos seus proventos segue as regras de cálculo da lei estadual. Se o Estado já tiver previdência complementar, o valor pago pelo regime próprio pode ficar limitado ao teto do Regime Geral.

**Depois (v2):**

Uma servidora titular de cargo efetivo de um Estado que possui regime próprio contribui para esse sistema.

Quando preencher os requisitos aplicáveis, sua aposentadoria será concedida pelo RPPS estadual, segundo a Constituição, as normas gerais e a legislação daquele regime.

### ATENÇÃO

**Antes (v1):**

O art. 40 contém a regra permanente. Regras de transição para quem já era servidor antes da Emenda Constitucional nº 103/2019, e a situação de Estados, Distrito Federal e Municípios que ainda não adaptaram as suas normas, estão na própria emenda e na legislação de cada ente (camada externa); não estão escritas no art. 40. Os incisos e alíneas do texto original do caput e de alguns parágrafos são históricos e não fazem parte do texto vigente.

**Depois (v2):**

O texto permanente do art. 40 não deve ser confundido com as diversas regras de transição criadas pela EC 103/2019.

Para servidores que já estavam no serviço público quando ocorreram as reformas previdenciárias, pode ser necessário consultar a própria emenda e a legislação aplicável ao ente.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Regime próprio de previdência social**: sistema previdenciário dos servidores titulares de cargo efetivo de cada ente.
- **Proventos**: valor pago ao servidor aposentado.
- **Previdência complementar**: sistema adicional e baseado em contribuições, que complementa o benefício do regime básico.

**Depois (v2):**

- **Regime próprio de previdência social**: regime previdenciário destinado aos servidores titulares de cargos efetivos abrangidos por ele.
- **Proventos**: valor recebido em razão da aposentadoria.
- **Previdência complementar**: regime previdenciário adicional, disciplinado por regras próprias.

## `CF88:ART.40:CAPUT` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:CAPUT/BASE/1 → ENTENDA/CF88:ART.40:CAPUT/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: "Contributivo" nao deve ser explicado apenas como "o direito ao beneficio depende de contribuicao"; nao afirmar que todos os aposentados e pensionistas contribuem da mesma maneira (incidencia concreta tratada por outras normas).
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: TECHNICAL_TERM_UNDEFINED (pensionista) → termo do proprio texto oficial do caput ("de aposentados e de pensionistas"), de uso comum; glossario do revisor dedicado aos conceitos centrais (carater contributivo/solidario, equilibrios).

### O QUE DIZ

**Antes (v1):**

O caput define o regime próprio dos servidores efetivos como contributivo e solidário. Contribuem o ente federativo, os servidores ativos, os aposentados e os pensionistas, e o regime deve observar critérios que preservem o seu equilíbrio financeiro e atuarial.

**Depois (v2):**

O caput estabelece que o regime próprio possui caráter contributivo e solidário.

Seu financiamento envolve o ente federativo, servidores ativos, aposentados e pensionistas, observadas as regras aplicáveis, e o sistema deve preservar equilíbrio financeiro e atuarial.

### O QUE SIGNIFICA

**Antes (v1):**

Caráter contributivo significa que o direito ao benefício depende de contribuição: não basta o tempo no cargo.

Caráter solidário significa que todos financiam o sistema em conjunto. Por isso o texto inclui como contribuintes não só os ativos e o ente, mas também aposentados e pensionistas.

O equilíbrio tem duas dimensões. O financeiro olha para o presente: as receitas do ano devem cobrir as despesas do ano. O atuarial olha para o futuro: projeta por décadas, com base em dados como idade e expectativa de vida, se as contribuições serão suficientes para pagar os benefícios prometidos.

**Depois (v2):**

Caráter contributivo significa que o RPPS é financiado por contribuições e funciona dentro de um sistema previdenciário baseado nesse custeio.

Caráter solidário significa que o financiamento não fica ligado apenas à contribuição individual de cada servidor: os recursos integram um sistema coletivo destinado ao pagamento dos benefícios previstos pelo regime.

A Constituição também exige equilíbrio financeiro e atuarial.

O equilíbrio financeiro considera a capacidade de pagar as obrigações correntes.

O equilíbrio atuarial considera também o longo prazo, projetando contribuições, benefícios e demais fatores que influenciam a sustentabilidade futura do regime.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um Município verifica, em estudo técnico, que as contribuições atuais não bastarão para pagar as aposentadorias daqui a vinte anos. Esse desequilíbrio atuarial obriga o Município a adotar medidas, como ajustar alíquotas ou aportar recursos, na forma da lei, para preservar o equilíbrio que o caput exige.

**Depois (v2):**

Se estudos do regime indicarem que, no longo prazo, os recursos projetados serão insuficientes para cumprir suas obrigações previdenciárias, o ente deverá enfrentar o desequilíbrio segundo as medidas permitidas pela Constituição e pela legislação aplicável.

### ATENÇÃO

**Antes (v1):**

A contribuição de aposentados e pensionistas tem regra específica sobre a parcela que incide (§ 18). O caput abrange os servidores titulares de cargo efetivo; ocupantes só de cargo em comissão e outros agentes temporários seguem o Regime Geral (§ 13).

**Depois (v2):**

O caput identifica as categorias que participam do financiamento do sistema, mas não define sozinho a base, o valor ou todas as condições de cada contribuição.

A contribuição incidente sobre aposentadorias e pensões possui disciplina constitucional e legal própria.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Caráter contributivo**: exigência de contribuição para que haja direito ao benefício.
- **Caráter solidário**: financiamento conjunto do regime por todos os participantes, inclusive aposentados e pensionistas.
- **Equilíbrio atuarial**: compatibilidade, projetada no longo prazo, entre as contribuições e os benefícios futuros.
- **Pensionista**: dependente que recebe pensão por morte do servidor.

**Depois (v2):**

- **Caráter contributivo**: característica de um sistema financiado mediante contribuições previdenciárias.
- **Caráter solidário**: financiamento coletivo do regime, segundo as regras constitucionais e legais.
- **Equilíbrio financeiro**: capacidade de compatibilizar receitas e despesas do regime.
- **Equilíbrio atuarial**: equilíbrio projetado no longo prazo entre recursos e obrigações previdenciárias.

## `CF88:ART.40:PAR.1:INC.I` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.1:INC.I/BASE/1 → ENTENDA/CF88:ART.40:PAR.1:INC.I/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Nao exigir incapacidade para "qualquer atividade compativel com a formacao" (a Constituicao fala em incapacidade permanente no cargo e impossibilidade de readaptacao); nao afirmar automaticamente a consequencia de eventual melhora nas avaliacoes.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: TECHNICAL_TERM_UNDEFINED (proventos) → definido no glossario da visao geral CF88:ART.40 ("Proventos"); aqui apenas mencionado ("o calculo dos proventos tambem nao e definido aqui").

### O QUE DIZ

**Antes (v1):**

Este inciso, uma das hipóteses de aposentadoria do § 1º, trata da incapacidade permanente para o trabalho no cargo, quando não for possível readaptar o servidor. Nesse caso, são obrigatórias avaliações periódicas para verificar se as condições que levaram à aposentadoria continuam, na forma de lei do ente.

**Depois (v2):**

O inciso prevê aposentadoria quando o servidor apresenta incapacidade permanente para o trabalho no cargo em que está investido e não é possível sua readaptação.

Depois da concessão, avaliações periódicas devem verificar se continuam presentes as condições que justificaram a aposentadoria, conforme a lei do ente.

### O QUE SIGNIFICA

**Antes (v1):**

A aposentadoria por incapacidade permanente ocorre quando o servidor não consegue mais exercer o seu cargo de forma definitiva. O texto traz duas condições ligadas entre si: a incapacidade deve ser permanente para o cargo ocupado, e o servidor não pode ser aproveitado por readaptação.

A readaptação, prevista no art. 37, § 13, vem antes: se o servidor pode exercer outro cargo compatível com a sua limitação, a solução é readaptá-lo, e não aposentá-lo.

Depois de aposentado, o servidor passa por reavaliações periódicas. Se as condições mudarem, a aposentadoria pode ser revista, conforme a lei do ente.

**Depois (v2):**

A incapacidade considerada pelo inciso está ligada ao cargo ocupado pelo servidor.

Antes da aposentadoria, deve ser considerada a possibilidade de readaptação prevista no art. 37, § 13.

Se for possível exercer outro cargo compatível com a limitação, observados os requisitos constitucionais da readaptação, a aposentadoria por incapacidade não é a solução prevista para aquela situação.

Se a incapacidade for permanente para o cargo e a readaptação não for possível, pode ocorrer a aposentadoria.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um servidor sofre uma doença grave que o impede de forma definitiva de exercer qualquer atividade compatível com a sua formação, e não há cargo para readaptação. Ele é aposentado por incapacidade permanente e passa por avaliações periódicas definidas na lei do ente.

**Depois (v2):**

Um servidor adquire limitação permanente que o impede de exercer as atribuições de seu cargo.

Depois da análise da possibilidade de readaptação, conclui-se que ela não é possível nas condições constitucionais.

Nessa hipótese, poderá ser aposentado por incapacidade permanente, conforme o regime aplicável.

### ATENÇÃO

**Antes (v1):**

O cálculo do valor dessa aposentadoria não está neste inciso: cabe à lei do ente (§ 3º). A expressão antiga "aposentadoria por invalidez" deu lugar a "incapacidade permanente para o trabalho".

**Depois (v2):**

A Constituição exige avaliações periódicas mesmo após a concessão, para verificar a continuidade das condições que a justificaram.

Os efeitos de eventual mudança dessas condições dependem da legislação aplicável e não devem ser deduzidos apenas deste inciso.

O cálculo dos proventos também não é definido aqui.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Incapacidade permanente**: impossibilidade definitiva de exercer o trabalho no cargo ocupado.
- **Readaptação**: transferência do servidor para cargo compatível com a limitação sofrida (art. 37, § 13).
- **Avaliação periódica**: reexame feito de tempos em tempos para verificar se a incapacidade continua.

**Depois (v2):**

- **Incapacidade permanente**: limitação duradoura que impede o exercício do trabalho no cargo.
- **Readaptação**: passagem para cargo compatível com a limitação, nas condições do art. 37, § 13.
- **Avaliação periódica**: reavaliação realizada em intervalos para verificar a continuidade das condições consideradas.

## `CF88:ART.40:PAR.1:INC.II` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.1:INC.II/BASE/1 → ENTENDA/CF88:ART.40:PAR.1:INC.II/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: O texto constitucional fala em 70 ou 75 anos na forma de lei complementar, mas a legislacao complementar atual ja regulamentou a hipotese.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: EXTRAPOLATION_NUMBER (2015) → ano da Lei Complementar nº 152/2015 (texto do revisor), com proveniencia HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE.; EXAMPLE_NUMBER (2015) → ano da Lei Complementar nº 152/2015 (texto do revisor), com proveniencia HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE.

### O QUE DIZ

**Antes (v1):**

Dentro das hipóteses do § 1º, este inciso prevê a aposentadoria compulsória aos 70 anos de idade, ou aos 75 anos na forma de lei complementar, com proventos proporcionais ao tempo de contribuição.

**Depois (v2):**

O inciso trata da aposentadoria compulsória.

A Constituição prevê aposentadoria obrigatória aos 70 anos ou aos 75 anos, na forma de lei complementar, com proventos proporcionais ao tempo de contribuição.

### O QUE SIGNIFICA

**Antes (v1):**

Compulsória quer dizer obrigatória. Ao atingir a idade-limite, o servidor é aposentado mesmo que queira continuar trabalhando e esteja apto.

O texto traz duas idades: 70 anos, como regra, e 75 anos, quando prevista em lei complementar. Assim, a idade efetivamente aplicável depende do que a lei complementar dispuser.

Os proventos são proporcionais ao tempo de contribuição: quem contribuiu por menos tempo recebe valor proporcionalmente menor.

**Depois (v2):**

Compulsória significa que a aposentadoria ocorre obrigatoriamente quando a pessoa alcança a idade-limite aplicável, independentemente de pedido do servidor.

A Constituição deixou à lei complementar a aplicação do limite de 75 anos.

Na legislação atualmente vigente, a Lei Complementar nº 152/2015 fixa 75 anos para os servidores e demais agentes abrangidos por ela.

### EXEMPLO PRÁTICO

**Antes (v1):**

Uma servidora completa a idade-limite prevista para o seu caso e continua em plena atividade. Ainda assim, é aposentada compulsoriamente, e os seus proventos são calculados de forma proporcional ao seu tempo de contribuição.

**Depois (v2):**

Um servidor titular de cargo efetivo abrangido pela Lei Complementar nº 152/2015 completa 75 anos.

Mesmo que queira permanecer trabalhando, alcançou a idade de aposentadoria compulsória.

### ATENÇÃO

**Antes (v1):**

O inciso não fixa sozinho qual das duas idades vale para cada servidor: isso depende da lei complementar. A aposentadoria compulsória é diferente da voluntária, tratada no inciso III.

**Depois (v2):**

O inciso constitucional deve ser lido junto com a lei complementar que o regulamenta.

O valor dos proventos é proporcional ao tempo de contribuição, mas a fórmula concreta de cálculo depende das demais regras previdenciárias aplicáveis.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Aposentadoria compulsória**: aposentadoria obrigatória ao atingir a idade-limite fixada pela Constituição e pela lei.
- **Proventos proporcionais**: valor de aposentadoria calculado em proporção ao tempo de contribuição.
- **Lei complementar**: lei que exige aprovação por maioria absoluta e trata de temas indicados pela Constituição.

**Depois (v2):**

- **Aposentadoria compulsória**: aposentadoria obrigatória ao atingir a idade-limite.
- **Proventos proporcionais**: proventos cujo cálculo considera a proporcionalidade prevista pelo regime em relação ao tempo de contribuição.
- **Lei complementar**: espécie legislativa exigida pela Constituição para determinadas matérias.

### CAMADA EXTERNA

**Antes (v1):**

- A lei complementar que fixou a idade de 75 anos e o seu alcance estão na camada de leis correlatas.

**Depois (v2):**

- Lei Complementar nº 152/2015.

## `CF88:ART.40:PAR.2` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.2/BASE/1 → ENTENDA/CF88:ART.40:PAR.2/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Retirada a ideia de que quem ultrapassa o teto do RGPS simplesmente "busca a diferenca" na previdencia complementar: a existencia e o valor de eventual beneficio complementar dependem do regime e do plano aplicavel.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: ABSOLUTE_CLAIM (automaticamente) → negacao ("nao significa, por si so, que o servidor recebera automaticamente"): afasta leitura indevida; nao e afirmacao absoluta.

### O QUE DIZ

**Antes (v1):**

O parágrafo fixa limites para os proventos de aposentadoria do regime próprio. Eles não podem ser menores que o valor mínimo do art. 201, § 2º, nem maiores que o limite máximo do Regime Geral, observados os §§ 14 a 16.

**Depois (v2):**

O § 2º estabelece limites mínimo e máximo para os proventos de aposentadoria concedidos pelo regime próprio, fazendo remissão ao art. 201, § 2º, ao limite máximo dos benefícios do Regime Geral e às regras dos §§ 14 a 16.

### O QUE SIGNIFICA

**Antes (v1):**

O piso remete ao art. 201, § 2º, que impede benefício substitutivo da renda inferior ao salário mínimo. Assim, nenhuma aposentadoria do regime próprio fica abaixo desse valor.

O teto é o limite máximo de benefícios do Regime Geral. A remissão aos §§ 14 a 16 é essencial: ela liga esse teto à previdência complementar. Quem recebe acima do teto do Regime Geral deve buscar a diferença na previdência complementar.

Para quem ingressou antes da instituição da previdência complementar do seu ente, o § 16 exige opção prévia e expressa para que essas regras se apliquem.

**Depois (v2):**

O limite mínimo remete ao art. 201, § 2º, que protege o valor mínimo dos benefícios que substituem a renda do trabalho.

No limite superior, o dispositivo relaciona o valor das aposentadorias do regime próprio ao teto do Regime Geral, mas exige que sejam observados os §§ 14 a 16, que tratam da previdência complementar.

Por isso, o teto não deve ser analisado isoladamente: é necessário considerar a instituição do regime complementar e a situação do servidor perante esse regime.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um servidor municipal de baixa remuneração se aposenta por incapacidade permanente com tempo de contribuição curto. Mesmo que o cálculo da lei municipal resulte em valor menor, os proventos não podem ficar abaixo do piso a que o § 2º remete, ligado ao salário mínimo.

**Depois (v2):**

Se o cálculo de uma aposentadoria resultar em valor inferior ao piso constitucional aplicável, o benefício não poderá ser concedido abaixo daquele limite.

Já a aplicação do teto do Regime Geral deve ser analisada junto com as regras constitucionais da previdência complementar.

### ATENÇÃO

**Antes (v1):**

O parágrafo não diz que todo servidor tem a aposentadoria limitada ao teto do Regime Geral. A aplicação do teto depende da previdência complementar e da data de ingresso, nos termos dos §§ 14 a 16.

**Depois (v2):**

O § 16 protege a situação de quem ingressou no serviço público antes da instituição do correspondente regime de previdência complementar, exigindo opção prévia e expressa para a aplicação das regras ali indicadas.

A existência de previdência complementar não significa, por si só, que o servidor receberá automaticamente a diferença entre o teto do Regime Geral e sua remuneração.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Piso**: valor mínimo que um benefício pode ter.
- **Teto do Regime Geral**: valor máximo dos benefícios pagos pelo Regime Geral de Previdência Social.
- **Proventos**: valor pago ao servidor aposentado.

**Depois (v2):**

- **Piso**: valor mínimo aplicável ao benefício.
- **Teto do Regime Geral**: limite máximo dos benefícios previdenciários do RGPS.
- **Proventos**: valor recebido em razão da aposentadoria.
- **Previdência complementar**: regime adicional de previdência, sujeito às regras de seu plano.

## `CF88:ART.40:PAR.4` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.4/BASE/1 → ENTENDA/CF88:ART.40:PAR.4/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Evitar dizer que "todos os servidores se aposentam pelas mesmas regras gerais", porque regras concretas podem variar entre entes e beneficios.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

O parágrafo proíbe adotar requisitos ou critérios diferenciados para conceder benefícios no regime próprio. As únicas ressalvas são as dos §§ 4º-A, 4º-B, 4º-C e 5º.

**Depois (v2):**

O § 4º estabelece como regra a proibição de requisitos ou critérios diferenciados para concessão de benefícios no regime próprio.

As exceções estão indicadas nos §§ 4º-A, 4º-B, 4º-C e 5º.

### O QUE SIGNIFICA

**Antes (v1):**

A regra é a igualdade: todos os servidores do regime próprio se aposentam pelas mesmas regras gerais.

Quando há motivo constitucional para tratar alguns grupos de forma diferente, a própria Constituição indica quais são: servidores com deficiência (§ 4º-A), certos agentes de segurança pública e do sistema prisional e socioeducativo (§ 4º-B), servidores expostos a agentes nocivos à saúde (§ 4º-C) e professores (§ 5º).

Fora dessas hipóteses, a lei não pode criar aposentadorias especiais com requisitos mais brandos.

**Depois (v2):**

A Constituição impede que sejam criados livremente regimes mais favoráveis de aposentadoria para determinadas categorias de servidores.

Os tratamentos diferenciados dependem das hipóteses que a própria Constituição ressalva.

Essas hipóteses envolvem servidores com deficiência, determinados agentes das áreas indicadas no § 4º-B, atividades com exposição efetiva a agentes prejudiciais à saúde e professores nas condições do § 5º.

### EXEMPLO PRÁTICO

**Antes (v1):**

Uma lei municipal reduz a idade mínima de aposentadoria para os fiscais de tributos, alegando desgaste da função. Como essa categoria não está entre as ressalvas do parágrafo, a lei contraria a vedação.

**Depois (v2):**

Uma lei não pode reduzir a idade de aposentadoria de uma categoria apenas porque considera sua atividade desgastante, se a situação não estiver enquadrada em uma das hipóteses constitucionais de tratamento diferenciado.

### ATENÇÃO

**Antes (v1):**

A lista de ressalvas é fechada. As próprias ressalvas dependem de lei complementar de cada ente para serem aplicadas.

**Depois (v2):**

As exceções não significam que todos os detalhes já estejam prontos no texto constitucional.

Os §§ 4º-A, 4º-B e 4º-C remetem a lei complementar do respectivo ente.

O § 5º possui regra constitucional própria para professores e também remete à lei complementar quanto ao tempo de efetivo exercício das funções de magistério.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Critério diferenciado**: regra de aposentadoria mais favorável aplicada a um grupo específico.
- **Ressalva**: exceção prevista no próprio texto da norma.

**Depois (v2):**

- **Critério diferenciado**: requisito previdenciário diferente daquele aplicado pela regra geral.
- **Ressalva**: exceção prevista pelo próprio texto constitucional.

## `CF88:ART.40:PAR.5` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.5/BASE/1 → ENTENDA/CF88:ART.40:PAR.5/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Nao definir "magisterio" simplesmente como atividade em sala de aula.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: LONG_SENTENCE (O § 5º reduz em cinco anos a idade mínim) → frase do revisor que acompanha a estrutura do § 5º (reducao, condicao de tempo e lei complementar); dividi-la iria alem da politica de microajustes; legibilidade aceita pelo revisor.; EXTRAPOLATION_NUMBER (65) → idade do § 1º, III (Uniao, homem), base da reducao; dispositivo citado e conferido no runtime.; EXTRAPOLATION_NUMBER (57) → calculo direto do proprio texto: 62 anos (§ 1º, III, Uniao, mulher) menos 5 anos (§ 5º).; EXTRAPOLATION_NUMBER (60) → calculo direto do proprio texto: 65 anos (§ 1º, III, Uniao, homem) menos 5 anos (§ 5º).

### O QUE DIZ

**Antes (v1):**

O parágrafo reduz em cinco anos a idade mínima de aposentadoria voluntária do professor, em relação às idades do § 1º, III. Para isso, ele precisa comprovar o tempo de efetivo exercício no magistério da educação infantil e dos ensinos fundamental e médio, fixado em lei complementar do ente.

**Depois (v2):**

O § 5º reduz em cinco anos a idade mínima aplicável ao professor em relação à regra do § 1º, III, desde que seja cumprido o tempo de efetivo exercício nas funções de magistério na educação infantil e nos ensinos fundamental e médio, conforme lei complementar do respectivo ente.

### O QUE SIGNIFICA

**Antes (v1):**

É a exceção dos professores à regra de igualdade do § 4º.

A redução vale para a idade mínima: se, na União, a idade da mulher é 62 anos, a professora que cumpre o requisito pode se aposentar aos 57.

O requisito é o efetivo exercício de funções de magistério na educação básica: infantil, fundamental e média. O tempo exigido é definido pela lei complementar de cada ente.

**Depois (v2):**

O dispositivo cria tratamento previdenciário específico para professores da educação básica.

Na União, a referência constitucional de 62 anos para mulher e 65 anos para homem corresponde, com a redução de cinco anos, a 57 e 60 anos respectivamente, sem afastar os demais requisitos aplicáveis.

A redução exige o tempo de efetivo exercício das funções de magistério fixado na legislação correspondente.

### EXEMPLO PRÁTICO

**Antes (v1):**

Uma professora federal da educação básica comprova o tempo de magistério exigido pela lei complementar. Ela pode se aposentar com idade cinco anos menor do que a exigida das demais servidoras federais.

**Depois (v2):**

Uma professora abrangida pelo RPPS e que preencha o tempo de funções de magistério exigido pela legislação aplicável poderá utilizar a redução constitucional de cinco anos na idade mínima, desde que satisfaça também os demais requisitos previdenciários pertinentes.

### ATENÇÃO

**Antes (v1):**

A redução não alcança o magistério no ensino superior, que não aparece no texto. O tempo exigido é o de efetivo exercício de funções de magistério; funções que se enquadram nesse conceito são definidas fora deste parágrafo.

**Depois (v2):**

O dispositivo é dirigido à educação infantil e aos ensinos fundamental e médio; não inclui o magistério de ensino superior.

O conceito de funções de magistério não se limita, necessariamente, ao tempo dentro da sala de aula.

O alcance de atividades como direção de unidade escolar, coordenação e assessoramento pedagógico é tratado pela jurisprudência.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Magistério**: exercício da função de professor.
- **Educação básica**: etapas da educação formadas pela educação infantil e pelos ensinos fundamental e médio.

**Depois (v2):**

- **Funções de magistério**: atividades da carreira do magistério consideradas para essa regra, cujo alcance também é interpretado pela legislação e jurisprudência.
- **Educação básica**: educação infantil e ensinos fundamental e médio.

### CAMADA EXTERNA

**Antes (v1):**

- Quais funções além da sala de aula contam como magistério é tema da camada JURISPRUDÊNCIA.

**Depois (v2):**

- Tema 965 e ADI 3.772 do Supremo Tribunal Federal: nas condições fixadas pela jurisprudência, também podem ser computadas atividades de direção de unidade escolar, coordenação e assessoramento pedagógico exercidas por professores de carreira em estabelecimentos de educação básica.

## `CF88:ART.40:PAR.6` — AJUSTAR → HUMAN_APPROVED_T1

- ENTENDA/CF88:ART.40:PAR.6/BASE/1 → ENTENDA/CF88:ART.40:PAR.6/BASE/2 · HUMAN_APPROVED_T1 (politica de microajustes T1 pre-autorizada; editorial_version 2)
- Motivo: Retirada a afirmacao categorica "Todas as somas se sujeitam ao teto (§ 11)": a relacao entre teto e acumulacoes constitucionalmente admitidas possui tratamento jurisprudencial.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

O parágrafo proíbe receber mais de uma aposentadoria do regime próprio, salvo as decorrentes de cargos que a Constituição permite acumular. Também manda aplicar outras vedações e condições de acumulação de benefícios previstas no Regime Geral.

**Depois (v2):**

O § 6º proíbe, como regra, a percepção de mais de uma aposentadoria custeada por regime próprio.

A Constituição ressalva as aposentadorias decorrentes de cargos que poderiam ser acumulados constitucionalmente.

O dispositivo também determina a aplicação de outras vedações, condições e regras de acumulação de benefícios previstas para o Regime Geral.

### O QUE SIGNIFICA

**Antes (v1):**

Em regra, cada servidor recebe uma só aposentadoria do regime próprio. A exceção acompanha o art. 37, XVI: quem acumulou licitamente dois cargos, como dois de professor, pode se aposentar nos dois.

A parte final importa as regras de acumulação de benefícios do Regime Geral. Elas podem limitar a soma de benefícios diferentes, como aposentadoria e pensão.

**Depois (v2):**

A regra geral é impedir que uma pessoa receba múltiplas aposentadorias de RPPS sem fundamento constitucional.

A exceção acompanha as hipóteses em que a própria Constituição permite acumular cargos.

Assim, se dois cargos puderam ser exercidos licitamente de forma acumulada, as aposentadorias correspondentes podem se enquadrar na ressalva do § 6º.

A parte final do dispositivo também conecta a acumulação de benefícios às demais regras previdenciárias aplicáveis ao Regime Geral.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um médico que ocupou licitamente dois cargos públicos de médico pode receber duas aposentadorias do regime próprio. Um servidor com um único cargo não pode obter uma segunda aposentadoria nesse regime.

**Depois (v2):**

Um médico que tenha exercido licitamente dois cargos públicos acumuláveis pode preencher os requisitos para aposentadoria decorrente de cada vínculo.

Já o exercício de um único cargo não permite criar uma segunda aposentadoria de RPPS sem outra hipótese constitucional que a autorize.

### ATENÇÃO

**Antes (v1):**

O parágrafo trata de aposentadorias do regime próprio. Os limites concretos para acumular aposentadoria com pensão vêm das regras do Regime Geral a que o texto remete, e não estão detalhados aqui. Todas as somas se sujeitam ao teto (§ 11).

**Depois (v2):**

O § 6º não detalha todas as combinações possíveis entre aposentadorias, pensões e outros benefícios.

Também não deve ser usado isoladamente para definir como o teto remuneratório incide em situações de acumulação.

O § 11 e a jurisprudência constitucional devem ser consultados para essas questões.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Cargos acumuláveis**: cargos que a Constituição permite exercer ao mesmo tempo, como dois de professor.
- **Acumulação de benefícios**: recebimento simultâneo de mais de um benefício previdenciário.

**Depois (v2):**

- **Cargos acumuláveis**: cargos cujo exercício simultâneo é admitido pela Constituição.
- **Acumulação de benefícios**: recebimento simultâneo de mais de um benefício previdenciário.

### CAMADA EXTERNA

**Antes (v1):**

- As regras de acumulação de benefícios aplicáveis e as reduções de valor previstas estão na Emenda Constitucional nº 103/2019 e na legislação do Regime Geral (camada externa).

**Depois (v2):**

- As regras de acumulação de benefícios aplicáveis e as reduções de valor previstas estão na Emenda Constitucional nº 103/2019 e na legislação do Regime Geral (camada externa).
- A incidência do teto em acumulações constitucionalmente admitidas possui jurisprudência própria, inclusive os Temas 377 e 384 do Supremo Tribunal Federal, já catalogados na revisão do art. 37.

