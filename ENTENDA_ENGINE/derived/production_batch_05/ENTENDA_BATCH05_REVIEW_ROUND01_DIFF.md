# ENTENDA BATCH05 — RODADA 01 — DIFF EDITORIAL (art. 37, HIGH)

- Revisão: `ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW` · escopo `CF88_ART37_HIGH_ROUND_1` · 2026-10-04
- Resultado: 7 revisados · 1 APROVADO sem alteração · 6 AJUSTAR · 0 REJEITADOS
- `CF88:ART.37:PAR.5` → `HUMAN_APPROVED_T1` (versão 1, conteúdo inalterado).
- 6 itens AJUSTAR → `editorial_version` 2. Após a verificação final (2026-10-04), marcados `HUMAN_APPROVED_T1` na mesma versão 2 (sem v3). A versão 1 de cada um permanece no corpus como `RETIRED` / `CHANGES_REQUESTED`.
- Drafts anteriores preservados em `BATCH_05_DRAFTS_PRE_ROUND1.json`. Targets, papel (ITEM/BLOCK/DEVICE) e cobertura de BLOCK inalterados. Pilotos aprovados inalterados.
- Texto do revisor incorporado literalmente, exceto os **desvios T1** listados (regras bloqueantes do validador). Confirmar os desvios na verificação final.

## Verificação final (2026-10-04) — `ROUND01_ART37_HIGH_HUMAN_APPROVED`: 7 de 7

- "Supremo Tribunal Federal" por extenso nos dois pontos do corpo: **APROVADO** (não é alteração de conteúdo). "STF" permanece só na CAMADA EXTERNA (Temas 377/384).
- Glossário do inciso XI: retirado "Subsídio"; mantidos Teto remuneratório, Subteto, Vantagem pessoal, Proventos, Pensionista: **APROVADO**.
- 5 microalterações contra cópia literal: **APROVADAS** (adaptações editoriais, sem mudança de conteúdo jurídico). Conferido: o conteúdo v2 é exatamente o texto do revisor + os 8 desvios abaixo, sem nenhuma outra alteração.
- Arts. 6º e 7º da EC 103/2019 (§§ 14 e 15), caráter transitório do art. 3º da EC 135/2024 (§ 9º) e Temas 377/384 (XI e XVI): mantidos na ATENÇÃO/CAMADA EXTERNA com proveniência `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE` (`human_review.content_provenance`): não vêm do CF88_RUNTIME e não são Lei Seca do art. 37.
- Status: `CF88:ART.37:PAR.5` HUMAN_APPROVED_T1 v1; `INC.XI`, `INC.XVI`, `PAR.4`, `PAR.9`, `PAR.14`, `PAR.15` HUMAN_APPROVED_T1 v2. Decisões em `ROUND_1_HUMAN_REVIEW_DECISIONS.json` (APPROVED 1, APPROVED_AFTER_ADJUSTMENT 6).

## Desvios T1 (confirmados)

| Target | Seção | Texto do revisor | Texto aplicado | Motivo |
|---|---|---|---|---|
| `CF88:ART.37:INC.XI` | o_que_significa | limitado a 90,25% do subsídio dos Ministros do STF. | limitado a 90,25% do subsídio dos Ministros do Supremo Tribunal Federal. | ENTENDA_EXTERNAL_CASE_CONTENT: sigla de tribunal no corpo e bloqueada; expandida por extenso |
| `CF88:ART.37:INC.XI` | o_que_significa | também é aplicado aos membros do Ministério Público, aos Procuradores e aos Defensores Públicos. | também é aplicado a membros do Ministério Público, Procuradores e Defensores Públicos. | ENTENDA_COPIES_OFFICIAL_TEXT: 11 palavras seguidas do texto oficial; artigos "aos" suprimidos |
| `CF88:ART.37:INC.XI` | palavras_dificeis | Subsídio: remuneração fixada em parcela única, nos termos constitucionais. | (removido) | ENTENDA_TERMS_INVALID: maximo de 5 termos; "Subsídio" ja e definido em CF88:ART.37:INC.X e INC.XV |
| `CF88:ART.37:INC.XVI` | o_que_diz | dois cargos ou empregos privativos de profissionais de saúde com profissões regulamentadas. | dois cargos ou empregos privativos de profissionais da saúde com profissões regulamentadas. | ENTENDA_COPIES_OFFICIAL_TEXT: 11 palavras seguidas do texto oficial; "de" -> "da" |
| `CF88:ART.37:INC.XVI` | o_que_significa | A vedação também alcança empregos e funções e abrange autarquias, | A vedação também alcança empregos e funções, abrangendo autarquias, | ENTENDA_COPIES_OFFICIAL_TEXT: 11 palavras seguidas do texto oficial; "e abrange" -> "abrangendo" |
| `CF88:ART.37:PAR.9` | o_que_significa | respeitado o máximo de 90,25% do subsídio dos Ministros do STF. | respeitado o máximo de 90,25% do subsídio dos Ministros do Supremo Tribunal Federal. | ENTENDA_EXTERNAL_CASE_CONTENT: sigla de tribunal no corpo e bloqueada; expandida por extenso |
| `CF88:ART.37:PAR.14` | o_que_diz | concedida com o uso de tempo de contribuição | concedida com o uso do tempo de contribuição | ENTENDA_COPIES_OFFICIAL_TEXT: 11 palavras seguidas do texto oficial; "de" -> "do" |
| `CF88:ART.37:PAR.15` | o_que_diz | proíbe a complementação de aposentadorias de servidores públicos e de pensões por morte de seus dependentes | proíbe a complementação das aposentadorias de servidores públicos e das pensões por morte de seus dependentes | ENTENDA_COPIES_OFFICIAL_TEXT: 11 palavras seguidas do texto oficial; "de" -> "das" (duas vezes) |

## Aprovado sem alteração

- `CF88:ART.37:PAR.5` — Texto contido a literalidade constitucional; nao afirma imprescritibilidade geral e deixa o alcance da ressalva final para a camada JURISPRUDENCIA. Opcao editorial preservada.

## `CF88:ART.37:INC.XI` — AJUSTAR

- ENTENDA/CF88:ART.37:INC.XI/BASE/1 → ENTENDA/CF88:ART.37:INC.XI/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: Exemplo anterior afirmava a soma das remuneracoes de acumulacao licita para aplicar o teto, em conflito com a jurisprudencia indicada pelo revisor (Temas 377 e 384); T1 substituido.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: EXTRAPOLATION_NUMBER (90,25%) → equivalente numerico de "noventa inteiros e vinte e cinco centesimos por cento" do texto oficial.; TECHNICAL_TERM_UNDEFINED (subsídio) → definido em CF88:ART.37:INC.X e INC.XV; retirado deste glossario pelo limite de 5 termos (desvio T1 listado para a verificacao final).

### O QUE DIZ

**Antes (v1):**

Dentro das regras do art. 37, o inciso XI fixa um teto para tudo o que é pago a agentes públicos: remuneração, subsídio, proventos, pensões e vantagens de qualquer natureza, somados ou não. O teto geral é o subsídio dos Ministros do Supremo Tribunal Federal. Nos Municípios e nos Estados e Distrito Federal há limites próprios, os subtetos.

**Depois (v2):**

O inciso XI estabelece limites para remunerações, subsídios, proventos, pensões e outras parcelas remuneratórias abrangidas pela Constituição, inclusive vantagens pessoais. O teto geral é o subsídio mensal dos Ministros do Supremo Tribunal Federal. Nos Municípios e nos Estados e Distrito Federal existem limites próprios, chamados subtetos.

### O QUE SIGNIFICA

**Antes (v1):**

O teto é o valor máximo que um agente público pode receber dos cofres públicos. Ele alcança servidores da administração direta, autárquica e fundacional, membros dos Poderes, detentores de mandato eletivo, aposentados e pensionistas.

Os subtetos funcionam assim. Nos Municípios, o limite é o subsídio do Prefeito. Nos Estados e no Distrito Federal, o limite varia por Poder: no Executivo, o subsídio do Governador; no Legislativo, o dos Deputados Estaduais e Distritais; no Judiciário, o dos Desembargadores do Tribunal de Justiça. Esse último fica limitado a 90,25% do subsídio dos Ministros do Supremo e também vale para membros do Ministério Público, Procuradores e Defensores Públicos.

O teto alcança também as vantagens pessoais e o total recebido cumulativamente.

**Depois (v2):**

O teto remuneratório é um limite constitucional para os valores de natureza remuneratória abrangidos pelo inciso.

Nos Municípios, o limite é o subsídio do Prefeito.

Nos Estados e no Distrito Federal, o limite varia conforme o Poder: no Executivo, é o subsídio do Governador; no Legislativo, o subsídio dos Deputados Estaduais ou Distritais; e, no Judiciário, o subsídio dos Desembargadores do Tribunal de Justiça, limitado a 90,25% do subsídio dos Ministros do Supremo Tribunal Federal. Esse último limite também é aplicado a membros do Ministério Público, Procuradores e Defensores Públicos.

O inciso também alcança vantagens pessoais, proventos e pensões.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um servidor municipal acumula licitamente dois cargos e, somadas as remunerações, ultrapassaria o subsídio do Prefeito. Pelo texto do inciso, a soma está sujeita ao teto municipal, e o excedente não é pago.

**Depois (v2):**

Um servidor municipal, em um único vínculo, recebe vencimento e uma vantagem pessoal. Se o total das parcelas remuneratórias abrangidas pelo teto ultrapassar o subsídio do Prefeito, incide o limite constitucional, ressalvadas as parcelas que a própria Constituição exclui do cálculo.

### ATENÇÃO

**Antes (v1):**

Algumas regras completam o teto e estão em outros dispositivos: a extensão às estatais que recebem recursos públicos, as parcelas indenizatórias excluídas e o subteto único facultativo dos Estados (§§ 9º, 11 e 12). O teto para a soma de aposentadorias e remunerações também aparece no art. 40, § 11.

**Depois (v2):**

Outros dispositivos completam essa regra, especialmente os §§ 9º, 11 e 12.

Nas acumulações de cargos constitucionalmente permitidas, não se deve concluir apenas pela leitura da expressão “percebidos cumulativamente ou não” que todas as remunerações devem ser somadas para aplicar o teto. A forma de incidência do teto nesses casos é matéria tratada pela jurisprudência.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- *Teto remuneratório*: limite máximo de tudo o que um agente público pode receber dos cofres públicos.
- *Subteto*: limite próprio de um ente ou Poder, abaixo do teto geral.
- *Vantagem pessoal*: parcela paga em razão da situação individual do servidor, como adicionais por tempo de serviço.
- *Subsídio*: remuneração fixada em parcela única, sem acréscimos de outras espécies remuneratórias (art. 39, § 4º).
- *Proventos*: valor pago ao servidor aposentado.

**Depois (v2):**

- *Teto remuneratório*: limite constitucional máximo aplicável às parcelas remuneratórias abrangidas pela regra.
- *Subteto*: limite próprio aplicável dentro de determinado ente ou Poder.
- *Vantagem pessoal*: parcela relacionada à situação individual do servidor.
- *Proventos*: valor recebido em razão da aposentadoria.
- *Pensionista*: pessoa que recebe pensão em razão do falecimento do segurado ou servidor.

### CAMADA EXTERNA

**Antes (v1):**

- A aplicação do teto a cada cargo, em casos de acumulação lícita, e o enquadramento de parcelas específicas são temas da camada JURISPRUDÊNCIA.

**Depois (v2):**

- Segundo os Temas 377 e 384 do STF, nas acumulações constitucionalmente permitidas o teto é considerado separadamente em cada vínculo, e não sobre o somatório.

---

## `CF88:ART.37:INC.XVI` — AJUSTAR

- ENTENDA/CF88:ART.37:INC.XVI/BASE/1 → ENTENDA/CF88:ART.37:INC.XVI/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: Retirada a afirmacao de que a soma das remuneracoes e submetida ao teto e a justificativa especulativa de que a Constituicao quis "aproveitar o profissional".
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: EXTRAPOLATION_NUMBER (2025) → ano da EC 138/2025 (texto do revisor), origem confirmada na fonte estrutural canonica do projeto.; EXTRAPOLATION_NUMBER (2025) → ano da EC 138/2025 (texto do revisor), origem confirmada na fonte estrutural canonica do projeto.; TECHNICAL_TERM_UNDEFINED (autarquia) → lista do texto do revisor (inciso XVII); termo definido em CF88:ART.37:INC.XIX.; TECHNICAL_TERM_UNDEFINED (economia mista) → lista do texto do revisor (inciso XVII); termo definido em CF88:ART.37:INC.XIX.

### O QUE DIZ

**Antes (v1):**

Em regra, é proibido acumular cargos públicos remunerados. As exceções exigem compatibilidade de horários e respeito ao teto, e são três: dois cargos de professor; um de professor com outro de qualquer natureza; dois cargos ou empregos privativos de profissionais de saúde com profissão regulamentada. O inciso XVII estende a proibição a empregos e funções, inclusive na administração indireta.

**Depois (v2):**

Em regra, é proibida a acumulação remunerada de cargos públicos. A Constituição admite três exceções, desde que haja compatibilidade de horários e seja observado o inciso XI: dois cargos de professor; um cargo de professor com outro de qualquer natureza; ou dois cargos ou empregos privativos de profissionais da saúde com profissões regulamentadas.

O inciso XVII estende a proibição também aos empregos e funções públicas e às entidades da administração indireta nele indicadas.

### O QUE SIGNIFICA

**Antes (v1):**

A regra geral é um vínculo público remunerado por pessoa. A acumulação só é permitida nas três hipóteses das alíneas, e mesmo assim com duas condições: os horários precisam ser compatíveis, e a soma das remunerações se submete ao teto do inciso XI.

As hipóteses protegem áreas em que a Constituição quis aproveitar o profissional em mais de um vínculo: o magistério e a saúde.

O inciso XVII amplia o alcance da proibição. Ela não se limita a cargos: vale para empregos e funções e alcança toda a administração indireta, incluídas as estatais, as suas subsidiárias e as sociedades que o poder público controla direta ou indiretamente.

**Depois (v2):**

A regra geral é que uma pessoa não exerça simultaneamente mais de um vínculo público remunerado.

A Constituição, porém, permite três combinações específicas. Mesmo nessas situações, os horários precisam ser realmente compatíveis e deve ser observado o regime constitucional do teto remuneratório.

O inciso XVII impede que a regra seja contornada apenas mudando o tipo de vínculo. A vedação também alcança empregos e funções, abrangendo autarquias, fundações, empresas públicas, sociedades de economia mista, subsidiárias e sociedades controladas pelo poder público.

### EXEMPLO PRÁTICO

**Antes (v1):**

Uma enfermeira concursada de um hospital estadual é aprovada para emprego de enfermeira em empresa pública federal de saúde. Como são duas ocupações privativas de profissional de saúde, a acumulação é possível se os plantões forem compatíveis. Já um técnico administrativo de uma prefeitura não pode assumir, ao mesmo tempo, emprego em sociedade de economia mista estadual, porque a proibição alcança também a administração indireta.

**Depois (v2):**

Uma enfermeira concursada de um hospital estadual é aprovada para outro vínculo de enfermeira em uma empresa pública federal de saúde. Como se trata de dois vínculos privativos de profissional de saúde com profissão regulamentada, a acumulação pode ser admitida se os horários forem compatíveis.

Já um técnico administrativo de uma prefeitura, em regra, não pode manter simultaneamente outro emprego em uma sociedade de economia mista apenas porque o segundo vínculo é chamado de “emprego” e não de “cargo”.

### ATENÇÃO

**Antes (v1):**

A proibição é de acumulação remunerada, e as exceções dependem das duas condições: horários compatíveis e teto. Na alínea "b", a redação vigente, dada pela Emenda Constitucional nº 138, de 2025, admite o cargo de professor com outro de qualquer natureza; materiais mais antigos falam em cargo técnico ou científico. A acumulação de aposentadoria com remuneração tem regra própria no § 10.

**Depois (v2):**

A alínea “b” mudou em 2025. O texto vigente permite um cargo de professor com outro de qualquer natureza. Materiais anteriores à EC 138/2025 ainda podem apresentar a redação antiga, que falava em cargo técnico ou científico.

A forma como o teto remuneratório incide sobre vínculos acumulados licitamente é tratada pela jurisprudência e não deve ser explicada como simples soma das remunerações.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- *Acumulação*: exercício simultâneo de mais de um cargo, emprego ou função pública.
- *Compatibilidade de horários*: possibilidade real de cumprir as jornadas dos dois vínculos sem sobreposição.
- *Profissão regulamentada*: profissão cujo exercício é disciplinado por lei, como medicina e enfermagem.

**Depois (v2):**

- *Acumulação*: exercício simultâneo de mais de um cargo, emprego ou função pública.
- *Compatibilidade de horários*: possibilidade real de cumprir as jornadas dos vínculos sem sobreposição.
- *Profissão regulamentada*: profissão cujo exercício possui disciplina legal específica.

### CAMADA EXTERNA

**Antes (v1):**

- Critérios de compatibilidade de horários são tema da camada JURISPRUDÊNCIA. A redação da alínea "b" (cargo de professor com outro de qualquer natureza) é a do texto operacional vigente, dada pela Emenda Constitucional nº 138/2025 segundo a fonte estrutural canônica do projeto.

**Depois (v2):**

- Temas 377/384 do STF para o teto em acumulações lícitas.

---

## `CF88:ART.37:PAR.4` — AJUSTAR

- ENTENDA/CF88:ART.37:PAR.4/BASE/1 → ENTENDA/CF88:ART.37:PAR.4/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: A definicao anterior de improbidade era ampla demais e podia sugerir que o proprio § 4º define quais condutas sao improbidade.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

O parágrafo prevê as consequências dos atos de improbidade administrativa: suspensão dos direitos políticos, perda da função pública, indisponibilidade dos bens e ressarcimento ao erário. A forma e a gradação dessas medidas ficam para a lei, e a responsabilização não impede a ação penal cabível.

**Depois (v2):**

O § 4º prevê consequências para os atos de improbidade administrativa: suspensão dos direitos políticos, perda da função pública, indisponibilidade dos bens e ressarcimento ao erário. A forma e a gradação dessas consequências são definidas em lei, sem prejuízo da ação penal que também possa ser cabível.

### O QUE SIGNIFICA

**Antes (v1):**

Improbidade é a conduta desonesta ou gravemente desleal de quem exerce função pública, como enriquecer ilicitamente, causar prejuízo aos cofres públicos ou violar deveres de honestidade.

O parágrafo lista medidas de natureza diferente. A suspensão dos direitos políticos e a perda da função são sanções. O ressarcimento repara o dano ao patrimônio público. A indisponibilidade dos bens serve para garantir que haverá patrimônio para ressarcir.

A expressão "sem prejuízo da ação penal" indica que a responsabilização por improbidade é independente da criminal: a mesma conduta pode gerar os dois processos.

**Depois (v2):**

A Constituição não define neste parágrafo quais condutas constituem improbidade administrativa. Essa definição é feita pela legislação.

O § 4º estabelece as consequências constitucionais que podem decorrer desses atos.

A suspensão dos direitos políticos e a perda da função pública possuem caráter sancionatório. O ressarcimento busca recompor o prejuízo causado ao patrimônio público. A indisponibilidade dos bens é uma medida patrimonial disciplinada pela legislação.

A expressão “sem prejuízo da ação penal cabível” significa que, se a mesma conduta também constituir crime, a responsabilização por improbidade não impede a responsabilização penal.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um servidor municipal recebe dinheiro de uma empresa para favorecê-la em contratos. Ele pode responder por improbidade, com perda da função, suspensão dos direitos políticos e ressarcimento, conforme a lei. Ao mesmo tempo, pode ser processado criminalmente pelo crime cometido.

**Depois (v2):**

Um agente público recebe vantagem indevida para favorecer uma empresa em uma contratação pública. Se a conduta preencher os requisitos previstos na legislação de improbidade, ele poderá responder nessa esfera e sofrer as consequências cabíveis. Se o mesmo fato também constituir crime, poderá haver processo criminal.

### ATENÇÃO

**Antes (v1):**

O parágrafo não define quais condutas são improbidade nem fixa prazos ou graduações: tudo isso está na lei. A suspensão dos direitos políticos aqui prevista dialoga com o art. 15, V.

**Depois (v2):**

Nem toda ilegalidade ou irregularidade administrativa é, por si só, ato de improbidade.

O próprio § 4º não define os atos de improbidade, o elemento subjetivo necessário nem a gradação das consequências. Esses pontos dependem da legislação aplicável e, quando necessário, da jurisprudência.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- *Improbidade administrativa*: ato desonesto ou gravemente contrário aos deveres de quem exerce função pública, definido em lei.
- *Erário*: patrimônio financeiro do poder público; os cofres públicos.
- *Indisponibilidade dos bens*: bloqueio que impede vender ou transferir bens, para garantir o ressarcimento.

**Depois (v2):**

- *Improbidade administrativa*: categoria de ilícito contra a Administração Pública cujas condutas e requisitos são definidos em lei.
- *Erário*: patrimônio financeiro do poder público; os cofres públicos.
- *Indisponibilidade dos bens*: medida que restringe a disposição de determinados bens nos termos previstos pela legislação.
- *Ressarcimento*: recomposição do prejuízo causado.

### CAMADA EXTERNA

**Antes (v1):**

- A lei de improbidade, suas sucessivas alterações e a exigência de dolo para a responsabilização são temas da camada de leis correlatas e da camada JURISPRUDÊNCIA.

**Depois (v2):**

- A legislação de improbidade, suas alterações, o requisito de dolo e a jurisprudência correspondente pertencem à camada externa.

---

## `CF88:ART.37:PAR.9` — AJUSTAR

- ENTENDA/CF88:ART.37:PAR.9/BASE/1 → ENTENDA/CF88:ART.37:PAR.9/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: Evitar "estatal dependente" como se fosse expressao do § 9º; nao reduzir o criterio a ideia generica de depender de dinheiro publico; explicitar a regra transitoria da EC 135/2024; reduzir o tamanho.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: TECHNICAL_TERM_UNDEFINED (subsídio) → definido em CF88:ART.37:INC.X e INC.XV.

### O QUE DIZ

**Antes (v1):**

O § 9º aplica o teto às empresas públicas, sociedades de economia mista e subsidiárias que recebem recursos públicos para pagar pessoal ou custeio. O § 11 exclui do teto as parcelas indenizatórias previstas expressamente em lei ordinária nacional, aprovada pelo Congresso. O § 12 permite que Estados e Distrito Federal adotem como limite único o subsídio dos Desembargadores do Tribunal de Justiça.

**Depois (v2):**

O § 9º submete ao teto do inciso XI as empresas públicas, sociedades de economia mista e subsidiárias que recebem recursos públicos destinados ao pagamento de pessoal ou ao custeio em geral.

O § 11 exclui do teto as parcelas indenizatórias que atendam aos requisitos previstos na própria Constituição.

O § 12 permite que os Estados e o Distrito Federal adotem, por alteração de suas normas constitucionais próprias, um limite remuneratório único baseado no subsídio dos Desembargadores do Tribunal de Justiça.

### O QUE SIGNIFICA

**Antes (v1):**

Os três parágrafos ajustam o alcance do teto do inciso XI.

O § 9º trata das estatais. Em regra, elas não estão no texto do inciso XI, que fala da administração direta, autárquica e fundacional. Mas, se dependem de dinheiro público para pagar salários ou despesas correntes, passam a se submeter ao teto.

O § 11 tira do teto as parcelas indenizatórias, que reembolsam gastos e não remuneram o trabalho. A exclusão só vale para as parcelas previstas expressamente em lei ordinária de alcance nacional, válida para todos os Poderes e órgãos autônomos.

O § 12 é uma opção dos Estados e do Distrito Federal: por emenda à Constituição estadual ou à Lei Orgânica, podem adotar um subteto único, limitado a 90,25% do subsídio dos Ministros do Supremo. A opção não alcança Deputados Estaduais e Distritais nem Vereadores.

**Depois (v2):**

O § 9º amplia o alcance do teto para determinadas empresas estatais. O critério é objetivo: receber recursos da União, Estado, Distrito Federal ou Município para despesas de pessoal ou de custeio em geral.

O § 11 trata das parcelas indenizatórias. Para a regra permanente do dispositivo, não entram no teto as parcelas expressamente previstas em lei ordinária nacional aprovada pelo Congresso e aplicável a todos os Poderes e órgãos constitucionalmente autônomos.

O § 12 permite que Estado ou Distrito Federal escolha um subteto único. Esse limite corresponde ao subsídio dos Desembargadores do Tribunal de Justiça, respeitado o máximo de 90,25% do subsídio dos Ministros do Supremo Tribunal Federal. A regra não se aplica aos subsídios dos Deputados Estaduais e Distritais nem dos Vereadores.

### EXEMPLO PRÁTICO

**Antes (v1):**

Uma companhia estadual de transportes que depende de repasses do Estado para pagar a folha passa a observar o teto (§ 9º). Uma diária paga a um servidor para cobrir hospedagem em viagem de trabalho, se prevista na lei nacional exigida pelo § 11, não entra na conta do teto.

**Depois (v2):**

Uma empresa pública estadual recebe recursos do Estado destinados ao pagamento de sua folha de pessoal. Nessa situação, o § 9º determina que o teto constitucional também seja observado.

Em outro caso, um Estado pode alterar sua Constituição para adotar o subteto único permitido pelo § 12, em vez de utilizar subtetos diferentes conforme cada Poder.

### ATENÇÃO

**Antes (v1):**

O texto oficial do § 11 traz remissão ao art. 3º da Emenda Constitucional nº 135/2024, que trata da aplicação dessa regra. O conteúdo dessa disposição está fora do art. 37 e deve ser consultado na emenda. Estatais que não recebem recursos públicos para pessoal ou custeio não estão alcançadas pelo § 9º.

**Depois (v2):**

O próprio texto do § 11 remete ao art. 3º da EC 135/2024. Essa emenda contém uma regra transitória para o período em que ainda não tiver sido editada a lei ordinária nacional exigida pelo § 11.

Como essa regra está fora do art. 37, seu conteúdo e sua vigência devem permanecer identificados como camada externa.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- *Estatal dependente*: empresa do poder público que precisa de repasses do Tesouro para pagar pessoal ou custeio.
- *Parcela indenizatória*: valor pago para reembolsar despesa do servidor, e não para remunerar o seu trabalho.
- *Custeio*: despesas correntes de manutenção, como contas, materiais e serviços.
- *Subsídio*: remuneração fixada em parcela única, sem acréscimos de outras espécies remuneratórias (art. 39, § 4º).
- *Sociedade de economia mista*: empresa com capital público e privado, controlada pelo poder público.

**Depois (v2):**

- *Parcela indenizatória*: valor destinado a compensar ou reembolsar uma despesa, em vez de remunerar o trabalho.
- *Custeio*: despesas correntes necessárias à manutenção das atividades.
- *Subteto único*: opção constitucional de utilizar um mesmo limite remuneratório dentro do Estado ou Distrito Federal, nas condições do § 12.
- *Sociedade de economia mista*: empresa controlada pelo poder público cujo capital também pode ter participação privada.

### CAMADA EXTERNA

**Antes (v1):**

- A situação da lei nacional de parcelas indenizatórias exigida pelo § 11 e as regras do art. 3º da Emenda Constitucional nº 135/2024 devem ser verificadas em fonte oficial atualizada (camada externa).

**Depois (v2):**

- Art. 3º da Emenda Constitucional nº 135/2024: regra transitória vinculada ao § 11.

---

## `CF88:ART.37:PAR.14` — AJUSTAR

- ENTENDA/CF88:ART.37:PAR.14/BASE/1 → ENTENDA/CF88:ART.37:PAR.14/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: Corpo aprovado; T1 substituido para tornar a ATENCAO mais precisa (regra de transicao do art. 6º da EC 103/2019).
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: EXTRAPOLATION_NUMBER (2019) → ano da EC 103/2019, origem confirmada na fonte estrutural canonica; o conteudo do art. 6º da emenda foi informado pela revisao humana (nao consta do runtime).; EXTRAPOLATION_NUMBER (2019) → ano da EC 103/2019, origem confirmada na fonte estrutural canonica; o conteudo do art. 6º da emenda foi informado pela revisao humana (nao consta do runtime).

### O QUE DIZ

**Antes (v1):**

O parágrafo determina que a aposentadoria concedida com o uso de tempo de contribuição de cargo, emprego ou função pública rompe o vínculo que gerou esse tempo, inclusive quando a aposentadoria é do Regime Geral.

**Depois (v2):**

O parágrafo determina que a aposentadoria concedida com o uso do tempo de contribuição decorrente de cargo, emprego ou função pública rompe o vínculo que gerou esse tempo, inclusive quando a aposentadoria é concedida pelo Regime Geral de Previdência Social.

### O QUE SIGNIFICA

**Antes (v1):**

A regra impede que a pessoa se aposente usando o tempo de um vínculo público e continue nesse mesmo vínculo, recebendo ao mesmo tempo a aposentadoria e a remuneração.

O ponto central é a origem do tempo de contribuição. Se a aposentadoria usou o tempo de um cargo, emprego ou função pública, esse vínculo termina. A menção expressa ao Regime Geral alcança, por exemplo, o empregado público que se aposenta pelo regime geral usando o tempo do seu emprego.

**Depois (v2):**

O ponto central é a origem do tempo de contribuição.

Se a aposentadoria utiliza o tempo decorrente de determinado cargo, emprego ou função pública, o vínculo que gerou esse tempo é rompido.

A referência expressa ao Regime Geral alcança, por exemplo, empregados públicos vinculados ao RGPS.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um empregado de uma empresa pública, vinculado ao Regime Geral, se aposenta contando o tempo de contribuição desse emprego. Pelo texto do parágrafo, a aposentadoria rompe o vínculo de emprego com a empresa pública.

**Depois (v2):**

Um empregado de uma empresa pública, vinculado ao Regime Geral, aposenta-se utilizando o tempo de contribuição decorrente desse emprego. Pela regra do § 14, a concessão da aposentadoria acarreta o rompimento daquele vínculo.

### ATENÇÃO

**Antes (v1):**

O parágrafo foi incluído pela reforma da previdência de 2019. A aplicação a aposentadorias concedidas antes da sua vigência depende de regras de transição da própria emenda, que não estão neste parágrafo.

**Depois (v2):**

O § 14 foi introduzido pela EC 103/2019.

A própria emenda contém regra de transição: seu art. 6º estabelece que o § 14 do art. 37 não se aplica às aposentadorias concedidas pelo Regime Geral de Previdência Social até a data de entrada em vigor da EC 103/2019.

Essa regra de transição está fora do art. 37 e deve permanecer identificada como conteúdo externo.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- *Tempo de contribuição*: período em que a pessoa contribuiu para um regime de previdência.
- *Regime Geral de Previdência Social*: sistema previdenciário administrado pelo INSS, que abrange os trabalhadores em geral.
- *Rompimento do vínculo*: término da relação de trabalho do agente com a administração.

**Depois (v2):**

- *Tempo de contribuição*: período considerado para fins previdenciários em razão das contribuições realizadas.
- *Regime Geral de Previdência Social*: regime previdenciário administrado pelo INSS e aplicável aos trabalhadores por ele abrangidos.
- *Rompimento do vínculo*: término da relação funcional ou de trabalho que gerou o tempo utilizado.

### CAMADA EXTERNA

**Antes (v1):**

- As regras de transição da Emenda Constitucional nº 103/2019 sobre este parágrafo devem ser consultadas na própria emenda (camada externa).

**Depois (v2):**

- EC 103/2019, art. 6º.

---

## `CF88:ART.37:PAR.15` — AJUSTAR

- ENTENDA/CF88:ART.37:PAR.15/BASE/1 → ENTENDA/CF88:ART.37:PAR.15/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: A definicao anterior dizia que a complementacao seria necessariamente pagamento extra feito pelo ente publico (mais estreita que o texto); regra transitoria descrita com precisao (art. 7º da EC 103/2019).
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: EXTRAPOLATION_NUMBER (2019) → ano da EC 103/2019, origem confirmada na fonte estrutural canonica; o conteudo do art. 7º da emenda foi informado pela revisao humana (nao consta do runtime).; EXTRAPOLATION_NUMBER (2019) → ano da EC 103/2019, origem confirmada na fonte estrutural canonica; o conteudo do art. 7º da emenda foi informado pela revisao humana (nao consta do runtime).

### O QUE DIZ

**Antes (v1):**

O parágrafo proíbe complementar aposentadorias de servidores públicos e pensões por morte de seus dependentes. Há duas exceções: a complementação que decorre do regime de previdência complementar do art. 40, §§ 14 a 16, e a prevista em lei que extinga regime próprio de previdência.

**Depois (v2):**

O § 15 proíbe a complementação das aposentadorias de servidores públicos e das pensões por morte de seus dependentes fora de duas hipóteses: quando decorrer do regime previsto nos §§ 14 a 16 do art. 40 ou quando estiver prevista em lei que extinga regime próprio de previdência social.

### O QUE SIGNIFICA

**Antes (v1):**

Complementação é um pagamento extra, feito pelo ente público, para aumentar o valor de uma aposentadoria ou pensão. O parágrafo impede que o ente crie esses acréscimos por conta própria.

Ficam permitidas apenas duas formas. A primeira é a previdência complementar dos servidores, organizada nos termos do art. 40, baseada em contribuições. A segunda é a complementação prevista na lei que extingue um regime próprio, caso em que os servidores daquele ente passam para o Regime Geral.

**Depois (v2):**

Complementação é um valor ou benefício destinado a acrescentar prestação à aposentadoria ou à pensão.

A Constituição impede que essas complementações sejam criadas fora das hipóteses que ela própria admite.

A primeira hipótese está ligada ao regime de previdência complementar previsto nos §§ 14 a 16 do art. 40.

A segunda ocorre quando uma lei extingue um regime próprio de previdência social e prevê a complementação correspondente.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um Município aprova lei para pagar, com recursos do Tesouro, um valor adicional às pensões de dependentes de servidores falecidos, fora de qualquer plano de previdência complementar. Essa lei contraria o parágrafo.

**Depois (v2):**

Um Município cria, com recursos públicos, um pagamento adicional às pensões de dependentes de servidores, sem que esse pagamento decorra do regime previsto no art. 40, §§ 14 a 16, nem de lei que extinga o regime próprio.

Essa complementação não se enquadra nas exceções previstas pelo § 15.

### ATENÇÃO

**Antes (v1):**

O parágrafo foi incluído pela reforma da previdência de 2019. A situação das complementações já existentes antes dela depende das regras de transição da emenda, que não estão escritas aqui.

**Depois (v2):**

O § 15 foi introduzido pela EC 103/2019.

O art. 7º da própria emenda determina que essa regra não se aplica às complementações de aposentadorias e pensões concedidas até a data de entrada em vigor da EC 103/2019.

Essa regra transitória está fora do art. 37.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- *Complementação*: pagamento adicional que aumenta o valor de uma aposentadoria ou pensão.
- *Pensão por morte*: benefício pago aos dependentes de quem faleceu.
- *Regime próprio de previdência social*: sistema previdenciário dos servidores titulares de cargo efetivo de cada ente.

**Depois (v2):**

- *Complementação*: valor ou benefício acrescentado à aposentadoria ou à pensão nas hipóteses admitidas pelo ordenamento.
- *Pensão por morte*: benefício destinado aos dependentes em razão do falecimento do segurado.
- *Regime próprio de previdência social*: regime previdenciário destinado aos servidores titulares de cargo efetivo de determinado ente federativo.
- *Previdência complementar*: regime adicional de previdência disciplinado pelas regras constitucionais e legais próprias.

### CAMADA EXTERNA

**Antes (v1):**

- As regras de transição da Emenda Constitucional nº 103/2019 sobre complementações pré-existentes devem ser consultadas na própria emenda.

**Depois (v2):**

- EC 103/2019, art. 7º.

---

