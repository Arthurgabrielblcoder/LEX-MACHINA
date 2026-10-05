# ENTENDA BATCH05 — RODADA 02 — DIFF EDITORIAL (arts. 38, 39 e 41, HIGH)

- Revisão: `ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW` · escopo `CF88_ART38_39_41_HIGH_ROUND_2` · 2026-10-04
- Resultado: 9 revisados · 2 APROVADOS sem alteração · 7 AJUSTAR · 0 REJEITADOS
- `CF88:ART.41:PAR.1` (BLOCK, incisos I–III) e `CF88:ART.41:PAR.3` → `HUMAN_APPROVED_T1` (versão 1, conteúdo inalterado).
- 7 itens AJUSTAR → `editorial_version` 2, **ainda `PENDING_HUMAN_REVIEW`** (não marcados como aprovados antes da verificação rápida dos desvios). A versão 1 de cada um permanece no corpus como `RETIRED` / `CHANGES_REQUESTED`.
- Drafts anteriores preservados em `BATCH_05_DRAFTS_PRE_ROUND2.json`. Targets, papel e cobertura de BLOCK inalterados (`ART.39:PAR.4` cobre `PAR.8`; `ART.41:PAR.1` explica os incisos I–III). Pilotos e Rodada 01 inalterados.
- Texto do revisor incorporado literalmente, exceto o **desvio T1** listado abaixo.

## Verificação final (2026-10-04) — `ROUND02_ART38_39_41_HIGH_HUMAN_APPROVED`: 9 de 9

- Desvio T1 do art. 39 ("integrado" → "composto"): **APROVADO** (adaptação editorial, sem alteração do sentido jurídico).
- Camada externa do art. 39 em duas notas sobre a ADI nº 2.135: **APROVADA**; a nota antiga, que tratava a eficácia do caput como questão aberta, foi removida. Proveniência `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`.
- Camada externa do art. 39 § 9º = "EC 103/2019, art. 13.": **APROVADA**; proveniência externa mantida.
- Art. 39 § 4º e art. 41: notas existentes mantidas, sem duplicação. Itens com "—": camada externa vazia.
- **Edição da verificação final (art. 39, ATENÇÃO):** "…pela EC 19/1998, que é a utilizada atualmente no CF88_RUNTIME." → "…pela EC 19/1998, que corresponde ao texto constitucional vigente utilizado neste aplicativo." (texto do revisor; o identificador interno não aparece mais ao leitor).
- **Versionamento:** uma `editorial_version` carimbada é imutável no motor (`ENTENDA_CONTENT_CHANGED_WITHOUT_VERSION_BUMP`), então o art. 39 passou a **v3**; a v2 (texto do revisor + desvio) ficou `RETIRED` / `CHANGES_REQUESTED`. Pela regra do motor, `superseded_by` aponta para a versão vigente: v1 e v2 → v3. Os outros 6 foram aprovados na v2, sem v3.
- Conferido antes de marcar: as v2 eram exatamente o texto do revisor + o desvio aprovado.
- Status: `ART.41:PAR.1` e `ART.41:PAR.3` HUMAN_APPROVED_T1 v1; `ART.38:INC.V`, `ART.39:PAR.4`, `ART.39:PAR.9`, `ART.41`, `ART.41:PAR.2`, `ART.41:PAR.4` HUMAN_APPROVED_T1 v2; `ART.39` HUMAN_APPROVED_T1 v3. Decisões em `ROUND_2_HUMAN_REVIEW_DECISIONS.json` (APPROVED 2, APPROVED_AFTER_ADJUSTMENT 7).
- As seções por item abaixo mostram v1 → texto do revisor; para o art. 39, o texto final é o da v3 (com a edição acima).

## Para a verificação rápida

### Desvios T1 (1)

| Target | Seção | Texto do revisor | Texto aplicado | Motivo |
|---|---|---|---|---|
| `CF88:ART.39` | o_que_diz | remuneração de pessoal, integrado por servidores designados | remuneração de pessoal, composto por servidores designados | ENTENDA_COPIES_OFFICIAL_TEXT: 16 palavras seguidas do caput oficial; "integrado" -> "composto" |

### Pontos de implementação a confirmar (nenhum altera o texto do revisor)

1. **CAMADA EXTERNA do art. 39:** os itens de "Registrar" foram organizados em duas notas (`external_layer_notes`): "ADI nº 2.135: o julgamento definitivo declarou constitucional a alteração promovida pela EC 19/1998 no caput do art. 39." e "ADI nº 2.135: eficácia ex nunc; inexistência de transmudação automática do regime dos atuais servidores; embargos rejeitados em 2025." A nota antiga ("a eficácia de cada redação do caput é tema da camada JURISPRUDÊNCIA") foi substituída. O número da ADI fica só na camada externa (regra T1 do corpo).
2. **CAMADA EXTERNA do § 9º do art. 39:** a nota antiga foi substituída pelo texto do revisor, "EC 103/2019, art. 13."
3. **CAMADAS EXTERNAS mantidas:** art. 39 § 4º ("Manter na camada JURISPRUDÊNCIA…") e art. 41 ("permanece matéria adequada à camada JURISPRUDÊNCIA") já tinham nota equivalente; ficaram inalteradas. Inciso V do art. 38, § 2º e § 4º do art. 41: "—" (sem nota, como antes).
4. **Observação, não alterada:** a ATENÇÃO do art. 39 cita "CF88_RUNTIME", nome interno do projeto, que aparecerá ao leitor no dispositivo. Não é regra bloqueante do T1, então o texto foi mantido literalmente. Se preferir, uma redação como "que é a utilizada atualmente neste aplicativo" resolveria.
5. **Proveniência** (`content_provenance`, `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`; não altera o payload):
   - art. 39 (ATENÇÃO/CAMADA EXTERNA): ADI nº 2.135 — julgamento definitivo, constitucionalidade da redação da EC 19/1998, eficácia ex nunc, não transmudação automática, embargos rejeitados em 2025. O runtime e a fonte estrutural canônica contêm apenas a remissão "Vide ADI nº 2.135"; esses fatos vêm da revisão humana e não foram verificados por pesquisa automática (proibida nesta missão).
   - art. 39 § 9º (ATENÇÃO/CAMADA EXTERNA): art. 13 da EC 103/2019, regra transitória. A origem do § 9º na EC 103/2019 consta da fonte estrutural canônica.
6. **editorial_checks:** 6 achados automáticos novos, gerados pelo texto do revisor, resolvidos com justificativa e sem alterar texto: EC 19/1998 e EC 103/2019 (anos), "incorporação" na visão geral do art. 39 (definida no § 9º), remissão a lei na visão geral do art. 39 (tratada nos §§ 3º, 5º e 7º), "provimento" no art. 41 (explicado pelo termo "Cargo efetivo"). Resultado: 0 sem resolução.

## Aprovados sem alteração

- `CF88:ART.41:PAR.1` — Distingue corretamente as tres hipoteses; preserva o transito em julgado no inciso I e a ampla defesa nos incisos II e III; nao apresenta a avaliacao periodica como autoaplicavel; identifica a dependencia de lei complementar; registra separadamente a hipotese do art. 169, § 4º; situa o art. 247 como protecao especial para atividades exclusivas de Estado.
- `CF88:ART.41:PAR.3` — Preserva extincao ou declaracao de desnecessidade do cargo, protecao dirigida ao servidor estavel, disponibilidade, remuneracao proporcional ao tempo de servico e carater temporario ate o adequado aproveitamento. O alerta automatico FACT_INCONSISTENCY permanece corretamente classificado como falso positivo.

## `CF88:ART.38:INC.V` — AJUSTAR

- ENTENDA/CF88:ART.38:INC.V/BASE/1 → ENTENDA/CF88:ART.38:INC.V/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: "Nao passa a contribuir para outro regime" descrevia mecanismo contributivo que o inciso nao detalha; retirada a justificativa teleologica sobre "evitar fragmentacao".
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

No art. 38, este inciso trata do servidor segurado de regime próprio de previdência que exerce mandato: ele continua filiado a esse regime, no ente federativo de origem.

**Depois (v2):**

O inciso V estabelece que o servidor que já é segurado de regime próprio de previdência social e passa a exercer mandato eletivo permanece filiado ao regime próprio do ente federativo de origem.

### O QUE SIGNIFICA

**Antes (v1):**

O servidor titular de cargo efetivo contribui para o regime próprio do seu ente, por exemplo o do Estado. Ao assumir um mandato, ele não passa a contribuir para outro regime em razão do mandato: continua vinculado ao regime próprio de onde veio.

A regra dá continuidade à vida previdenciária do servidor e evita a fragmentação do seu tempo de contribuição entre regimes diferentes.

**Depois (v2):**

O exercício do mandato não rompe, por si só, o vínculo previdenciário que o servidor efetivo já possuía com o regime próprio de seu ente.

Assim, se um servidor estadual vinculado ao regime próprio do Estado assume mandato eletivo, continua filiado àquele regime durante a situação prevista pelo art. 38.

A regra trata da filiação previdenciária do servidor que já possuía vínculo com regime próprio antes do mandato.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um auditor fiscal do Estado, segurado do regime próprio estadual, é eleito deputado federal. Durante o mandato, ele continua filiado ao regime próprio do Estado, que é o seu ente de origem.

**Depois (v2):**

Um auditor fiscal estadual, titular de cargo efetivo e segurado do regime próprio do Estado, é eleito deputado federal. Durante o mandato, permanece filiado ao regime próprio do ente estadual de origem.

### ATENÇÃO

**Antes (v1):**

O inciso vale para quem já é segurado de regime próprio. Detentores de mandato eletivo que não são servidores efetivos seguem, em regra, o Regime Geral, conforme o art. 40, § 13.

**Depois (v2):**

A regra pressupõe que a pessoa já seja segurada de regime próprio.

Para quem ocupa exclusivamente mandato eletivo, sem essa condição de servidor segurado de regime próprio, o art. 40, § 13, prevê a aplicação do Regime Geral de Previdência Social.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Segurado**: pessoa vinculada a um regime de previdência, com direito aos seus benefícios.
- **Ente de origem**: União, Estado, Distrito Federal ou Município ao qual pertence o cargo efetivo do servidor.
- **Filiação**: vínculo jurídico da pessoa com um regime de previdência.

**Depois (v2):**

- **Segurado**: pessoa vinculada a determinado regime de previdência.
- **Ente de origem**: União, Estado, Distrito Federal ou Município ao qual pertence o vínculo efetivo do servidor.
- **Filiação**: vínculo jurídico da pessoa com determinado regime previdenciário.

## `CF88:ART.39` — AJUSTAR

- ENTENDA/CF88:ART.39/BASE/1 → ENTENDA/CF88:ART.39/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: A ATENCAO tratava a eficacia do caput como controversia pendente ("qual redacao produz efeitos"); informacao desatualizada segundo o revisor: o julgamento definitivo declarou constitucional a redacao da EC 19/1998 (eficacia prospectiva, sem transmudacao automatica do regime dos atuais servidores). T1 revisado.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: EXTRAPOLATION_NUMBER (1998) → ano da EC 19/1998 (texto do revisor), redacao do caput confirmada na fonte estrutural canonica; o resultado do julgamento e conteudo externo com proveniencia HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE.; LAW_DEPENDENCY_OMITTED (a lei) → a remissao a lei vem do § 3º (requisitos diferenciados de admissao) e dos §§ 5º e 7º, explicados em CF88:ART.39:PAR.3, PAR.5 e PAR.7; a visao geral apenas situa os temas.; TECHNICAL_TERM_UNDEFINED (incorporação) → citada apenas como tema dos paragrafos; definida no glossario de CF88:ART.39:PAR.9.

### O QUE DIZ

**Antes (v1):**

O art. 39 organiza a política de pessoal dos servidores. O caput manda cada ente instituir um conselho de política de administração e remuneração de pessoal, formado por servidores indicados pelos Poderes. Os parágrafos tratam dos critérios da remuneração, das escolas de governo, dos direitos sociais aplicáveis, do subsídio, dos limites internos da remuneração, da publicação dos valores, do uso da economia de despesas e da proibição de incorporar vantagens.

**Depois (v2):**

O art. 39 reúne regras sobre administração e remuneração de pessoal no serviço público.

O caput determina que União, Estados, Distrito Federal e Municípios instituam conselho de política de administração e remuneração de pessoal, composto por servidores designados pelos respectivos Poderes.

Os parágrafos tratam, entre outros pontos, dos critérios para estruturar a remuneração, da formação dos servidores, de direitos sociais aplicáveis, do subsídio, da publicidade dos valores pagos e da proibição de incorporar determinadas vantagens temporárias.

### O QUE SIGNIFICA

**Antes (v1):**

Enquanto o art. 37 traz princípios e regras gerais da administração, o art. 39 se concentra em como os servidores são remunerados, formados e organizados em carreira.

O conselho do caput é um órgão de apoio: reúne servidores designados pelos Poderes para pensar a política de administração e de remuneração de pessoal, de modo coordenado. O texto não define as suas competências nem a sua composição numérica, que ficam a cargo de cada ente.

Os parágrafos podem ser lidos em grupos: como fixar a remuneração (§§ 1º, 4º, 5º e 8º), como formar e valorizar o servidor (§§ 2º e 7º), quais direitos trabalhistas se estendem a ele (§ 3º), a transparência dos valores (§ 6º) e a vedação de incorporar vantagens temporárias (§ 9º).

Todos os entes se submetem a essas regras, respeitada a autonomia de cada um para editar as suas leis de pessoal.

**Depois (v2):**

Enquanto o art. 37 contém princípios e regras gerais da Administração Pública, o art. 39 concentra diversas normas relacionadas à organização, formação e remuneração dos servidores.

O conselho previsto no caput deve ser integrado por servidores designados pelos respectivos Poderes. A Constituição não define, nesse dispositivo, quantos membros ele terá nem detalha todas as suas competências.

O § 1º indica fatores que devem ser considerados na estrutura remuneratória, como responsabilidade, complexidade, requisitos de ingresso e peculiaridades dos cargos.

Os demais parágrafos tratam de temas específicos que recebem explicação própria quando necessário, como subsídio e incorporação de vantagens.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um Município cria, por lei, o seu conselho de política de administração e remuneração, com servidores indicados pelo Executivo e pela Câmara. Ao reestruturar a carreira de fiscal, o Município considera a complexidade do cargo e os requisitos de ingresso, publica anualmente os valores da remuneração e não permite que a gratificação de chefia seja incorporada ao cargo efetivo.

**Depois (v2):**

Ao estruturar a carreira de fiscais, um Estado deve considerar fatores como a complexidade das atribuições, a responsabilidade do cargo e os requisitos exigidos para ingresso.

Além disso, deve observar as demais regras constitucionais do artigo relacionadas à política de pessoal e remuneração.

### ATENÇÃO

**Antes (v1):**

O art. 39 convive com o art. 37: teto, irredutibilidade e exigência de lei para fixar remuneração estão no art. 37 e continuam valendo. A redação do caput tem histórico constitucional complexo, ligado ao regime jurídico dos servidores; qual redação produz efeitos deve ser conferido na camada externa, e não deduzido só da leitura deste texto.

**Depois (v2):**

O caput do art. 39 teve uma longa controvérsia constitucional.

Materiais produzidos durante o período da medida cautelar podem apresentar como vigente a redação original sobre regime jurídico único.

O julgamento definitivo declarou constitucional a redação dada pela EC 19/1998, que é a utilizada atualmente no CF88_RUNTIME.

Os efeitos temporais e a preservação das situações anteriores pertencem à camada JURISPRUDÊNCIA.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Política remuneratória**: conjunto de critérios e decisões sobre como os servidores são pagos.
- **Carreira**: conjunto de cargos organizados em níveis, pelos quais o servidor avança.
- **Designação**: indicação formal de alguém para exercer uma função.
- **Subsídio**: remuneração fixada em parcela única, sem acréscimos de outras espécies remuneratórias (art. 39, § 4º).

**Depois (v2):**

- **Política remuneratória**: conjunto de regras e critérios relacionados à remuneração dos servidores.
- **Carreira**: organização de cargos ou posições funcionais segundo a estrutura prevista em lei.
- **Designação**: indicação formal de alguém para determinada função.
- **Subsídio**: forma constitucional de remuneração em parcela única.

### CAMADA EXTERNA

**Antes (v1):**

- A fonte estrutural canônica do projeto registra, junto ao caput, a remissão "Vide ADI nº 2.135" e a redação original sobre regime jurídico único e planos de carreira. A eficácia de cada redação do caput é tema da camada JURISPRUDÊNCIA.

**Depois (v2):**

- ADI nº 2.135: o julgamento definitivo declarou constitucional a alteração promovida pela EC 19/1998 no caput do art. 39.
- ADI nº 2.135: eficácia ex nunc; inexistência de transmudação automática do regime dos atuais servidores; embargos rejeitados em 2025.

## `CF88:ART.39:PAR.4` — AJUSTAR

- ENTENDA/CF88:ART.39:PAR.4/BASE/1 → ENTENDA/CF88:ART.39:PAR.4/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: Retirada a afirmacao teleologica de que o "objetivo e transparencia"; "membro de Poder" nao e mais definido com categorias que o proprio § 4º enumera separadamente; exemplo menos sujeito a excecoes tratadas fora do dispositivo.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

O § 4º manda remunerar por subsídio, em parcela única, os membros de Poder, os detentores de mandato eletivo, os Ministros de Estado e os Secretários dos Estados e dos Municípios, proibindo acréscimos como gratificações, adicionais, abonos e prêmios, e mandando observar o art. 37, X e XI. O § 8º permite que servidores organizados em carreira também sejam remunerados assim.

**Depois (v2):**

O § 4º determina a remuneração por subsídio em parcela única para as categorias nele indicadas, como membros de Poder, detentores de mandato eletivo, Ministros de Estado e Secretários estaduais e municipais.

O dispositivo veda o acréscimo das espécies remuneratórias que enumera e manda observar as regras do art. 37, X e XI.

O § 8º permite aplicar essa mesma forma de remuneração aos servidores públicos organizados em carreira.

### O QUE SIGNIFICA

**Antes (v1):**

Subsídio é uma forma de remuneração em valor único. O objetivo é transparência: em vez de um vencimento básico somado a muitas parcelas, há um valor só, fácil de conhecer e de comparar com o teto.

Para as autoridades listadas no § 4º, o subsídio é obrigatório. Membros de Poder são, por exemplo, parlamentares, chefes do Executivo e magistrados.

Para servidores organizados em carreira, o § 8º torna o subsídio uma opção do legislador.

O subsídio também depende de lei específica e se sujeita ao teto, por força da remissão ao art. 37, X e XI.

**Depois (v2):**

Subsídio é uma forma constitucional de remuneração fixada em parcela única.

Para as categorias listadas no § 4º, essa forma de pagamento é obrigatória.

Já para servidores organizados em carreira, o § 8º permite que o legislador também adote o sistema de subsídio.

Como o § 4º remete ao art. 37, X e XI, o subsídio está sujeito às regras constitucionais de fixação ou alteração por lei específica e aos limites remuneratórios aplicáveis.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um deputado estadual recebe subsídio fixado em parcela única e não pode receber, além dele, uma gratificação por presidir uma comissão. Já uma lei pode organizar a carreira de procurador do Estado em subsídio, com base no § 8º.

**Depois (v2):**

A remuneração ordinária de um Secretário municipal é fixada em subsídio. Não se pode simplesmente acrescentar ao subsídio uma gratificação remuneratória pelo próprio exercício normal daquele cargo, contrariando a regra da parcela única.

### ATENÇÃO

**Antes (v1):**

A proibição atinge parcelas de natureza remuneratória. O texto não trata de parcelas que apenas indenizam despesas; o tratamento delas depende de interpretação e das regras do teto (art. 37, § 11).

**Depois (v2):**

“Parcela única” não significa, por si só, que qualquer pagamento de natureza diversa seja constitucionalmente proibido.

O tratamento de parcelas indenizatórias, décimo terceiro, férias e outras situações específicas depende das demais normas constitucionais e da jurisprudência.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Subsídio**: remuneração fixada em parcela única, sem acréscimos de outras espécies remuneratórias.
- **Membro de Poder**: agente que integra a cúpula de um Poder, como parlamentares, chefes do Executivo e magistrados.
- **Verba de representação**: parcela paga em razão do cargo para custear atividades de representação.

**Depois (v2):**

- **Subsídio**: forma de remuneração constitucionalmente fixada em parcela única.
- **Parcela remuneratória**: valor pago como contraprestação pelo exercício do cargo ou função.
- **Verba indenizatória**: valor destinado a compensar ou reembolsar determinada despesa, conforme o regime jurídico aplicável.

## `CF88:ART.39:PAR.9` — AJUSTAR

- ENTENDA/CF88:ART.39:PAR.9/BASE/1 → ENTENDA/CF88:ART.39:PAR.9/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: Nucleo correto; substituida a justificativa generica ("evita que a remuneracao cresca") e a transicao tornada precisa (art. 13 da EC 103/2019, conteudo externo).
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS, CAMADA EXTERNA
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: EXTRAPOLATION_NUMBER (2019) → ano da EC 103/2019 (texto do revisor), origem do § 9º confirmada na fonte estrutural canonica; o conteudo do art. 13 da emenda tem proveniencia HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE.; EXTRAPOLATION_NUMBER (2019) → ano da EC 103/2019 (texto do revisor), origem do § 9º confirmada na fonte estrutural canonica; o conteudo do art. 13 da emenda tem proveniencia HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE.

### O QUE DIZ

**Antes (v1):**

O parágrafo proíbe incorporar à remuneração do cargo efetivo as vantagens temporárias e as que decorrem do exercício de função de confiança ou de cargo em comissão.

**Depois (v2):**

O § 9º impede que vantagens temporárias ou relacionadas ao exercício de função de confiança ou cargo em comissão sejam incorporadas à remuneração permanente do cargo efetivo.

### O QUE SIGNIFICA

**Antes (v1):**

Incorporar significa transformar uma vantagem passageira em parte permanente da remuneração. Por exemplo, depois de alguns anos recebendo gratificação de chefia, o servidor passaria a recebê-la de forma permanente, mesmo sem continuar chefiando.

O parágrafo proíbe isso. A gratificação de função ou de cargo em comissão é paga enquanto o servidor exerce a função; quando ela termina, a parcela deixa de ser paga.

A regra evita que a remuneração cresça de forma permanente por atividades exercidas apenas por um tempo.

**Depois (v2):**

Incorporação ocorre quando determinada parcela que era paga apenas em razão de uma situação temporária passa a integrar de forma permanente a remuneração do servidor.

O § 9º proíbe essa transformação para as vantagens abrangidas pelo dispositivo.

Assim, uma parcela ligada ao exercício temporário de função de confiança ou cargo em comissão não se torna, apenas pelo decurso do tempo, parte permanente da remuneração do cargo efetivo.

### EXEMPLO PRÁTICO

**Antes (v1):**

Uma servidora ocupou por seis anos a função de diretora de um departamento, com gratificação. Ao deixar a função, volta a receber apenas a remuneração do seu cargo efetivo, sem incorporar a gratificação.

**Depois (v2):**

Uma servidora ocupa durante alguns anos uma função de direção e recebe a vantagem correspondente enquanto exerce essa função.

Depois de deixar a direção, essa vantagem não pode ser incorporada à remuneração permanente do seu cargo efetivo com fundamento apenas no período em que exerceu a função.

### ATENÇÃO

**Antes (v1):**

O parágrafo foi incluído pela reforma da previdência de 2019. Incorporações ocorridas antes dela dependem das regras de transição da emenda, que não estão neste parágrafo.

**Depois (v2):**

O § 9º foi introduzido pela EC 103/2019.

A própria emenda contém regra de transição: seu art. 13 determina que o § 9º não se aplica às incorporações abrangidas por ele que tenham sido efetivadas até a entrada em vigor da EC 103/2019.

Essa regra está fora do art. 39 e deve permanecer identificada como conteúdo externo.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Incorporação**: transformação de uma vantagem temporária em parte permanente da remuneração.
- **Vantagem de caráter temporário**: parcela paga apenas enquanto existe certa situação ou atividade.

**Depois (v2):**

- **Incorporação**: transformação de determinada vantagem em parcela permanente da remuneração.
- **Vantagem temporária**: parcela ligada a uma situação que não possui caráter permanente.
- **Função de confiança**: função atribuída a servidor efetivo para atividades de direção, chefia ou assessoramento, conforme o regime aplicável.

### CAMADA EXTERNA

**Antes (v1):**

- As regras de transição da Emenda Constitucional nº 103/2019 sobre incorporações anteriores devem ser consultadas na própria emenda.

**Depois (v2):**

- EC 103/2019, art. 13.

## `CF88:ART.41` — AJUSTAR

- ENTENDA/CF88:ART.41/BASE/1 → ENTENDA/CF88:ART.41/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: O exemplo dizia que, apos adquirir estabilidade, o servidor "so pode perder o cargo nas hipoteses do § 1º", o que e incompleto diante do art. 169, § 4º.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: LAW_DEPENDENCY_OMITTED (de lei) → a lei complementar da avaliacao periodica (§ 1º, III) e explicada no bloco CF88:ART.41:PAR.1; a visao geral situa as hipoteses.; TECHNICAL_TERM_UNDEFINED (provimento) → expressao "cargo de provimento efetivo" do texto oficial; explicada pelo termo "Cargo efetivo" do glossario do revisor (glossario no limite de 5 termos).

### O QUE DIZ

**Antes (v1):**

O art. 41 trata da estabilidade do servidor público. O caput garante estabilidade, após três anos de efetivo exercício, aos servidores nomeados por concurso para cargo de provimento efetivo. Os parágrafos tratam das hipóteses de perda do cargo, da reintegração após demissão invalidada, da disponibilidade e da avaliação especial de desempenho.

**Depois (v2):**

O art. 41 disciplina a estabilidade do servidor nomeado para cargo efetivo após concurso público.

O caput estabelece o período de três anos de efetivo exercício. Os parágrafos tratam das hipóteses de perda do cargo, da reintegração, da disponibilidade e da avaliação especial necessária à aquisição da estabilidade.

### O QUE SIGNIFICA

**Antes (v1):**

Estabilidade é a garantia de permanência no serviço público. O servidor estável só pode perder o cargo nas hipóteses que a Constituição admite. Ela protege o servidor contra demissões arbitrárias e, com isso, protege também a impessoalidade e a continuidade da administração.

O caput traz três condições cumulativas: cargo de provimento efetivo, nomeação em virtude de concurso público e três anos de efetivo exercício. A essas condições, o § 4º acrescenta a aprovação em avaliação especial de desempenho.

Estabilidade é diferente de efetividade. Efetividade é a característica do cargo, ocupado de forma permanente. Estabilidade é a garantia que o servidor adquire depois do período e da avaliação.

O período antes da estabilidade é conhecido como estágio probatório.

**Depois (v2):**

Estabilidade é uma garantia constitucional relacionada à permanência do servidor no serviço público depois do cumprimento dos requisitos constitucionais.

O caput exige cargo de provimento efetivo, ingresso mediante concurso público e três anos de efetivo exercício.

Além disso, o § 4º exige avaliação especial de desempenho realizada por comissão instituída para essa finalidade.

Efetividade e estabilidade não são a mesma coisa. O servidor ocupa cargo efetivo desde o ingresso nessa espécie de cargo; a estabilidade é adquirida depois do preenchimento das condições constitucionais.

### EXEMPLO PRÁTICO

**Antes (v1):**

Uma analista toma posse em cargo efetivo depois de aprovada em concurso. Durante os três primeiros anos, ela é acompanhada e avaliada. Aprovada na avaliação especial e completado o período, torna-se estável e só pode perder o cargo nas hipóteses do § 1º.

**Depois (v2):**

Uma analista ingressa por concurso em cargo efetivo.

Depois de completar o período constitucional e preencher a condição da avaliação especial de desempenho, adquire estabilidade.

A partir daí, a perda do cargo depende das hipóteses admitidas pela Constituição.

### ATENÇÃO

**Antes (v1):**

A estabilidade não alcança ocupantes só de cargo em comissão nem contratados temporários. A Constituição também prevê, no art. 169, § 4º, perda do cargo do servidor estável por excesso de despesa com pessoal, hipótese que está fora do art. 41.

**Depois (v2):**

A estabilidade não se aplica apenas porque alguém ingressou por processo seletivo ou trabalha de forma permanente para o poder público: o caput refere-se ao servidor nomeado para cargo de provimento efetivo em virtude de concurso público.

Além das hipóteses do § 1º, a Constituição prevê no art. 169, § 4º, outra possibilidade de perda do cargo do servidor estável, ligada à redução de despesas com pessoal e sujeita às condições daquele artigo.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Estabilidade**: garantia de permanência no serviço público, com perda do cargo só nas hipóteses constitucionais.
- **Cargo de provimento efetivo**: cargo ocupado de forma permanente, após concurso.
- **Estágio probatório**: período inicial em que o servidor é avaliado antes de adquirir estabilidade.
- **Disponibilidade**: situação do servidor estável que fica sem exercer o cargo, mas vinculado e remunerado proporcionalmente.
- **Reintegração**: retorno do servidor ao cargo após a anulação da sua demissão.

**Depois (v2):**

- **Estabilidade**: garantia constitucional adquirida após o preenchimento das condições do art. 41.
- **Cargo efetivo**: cargo público cujo provimento definitivo depende de concurso.
- **Avaliação especial de desempenho**: avaliação obrigatória prevista como condição para aquisição da estabilidade.
- **Disponibilidade**: situação constitucional prevista para determinados servidores estáveis afastados do exercício do cargo.
- **Reintegração**: retorno do servidor estável após invalidação judicial de sua demissão.

## `CF88:ART.41:PAR.2` — AJUSTAR

- ENTENDA/CF88:ART.41:PAR.2/BASE/1 → ENTENDA/CF88:ART.41:PAR.2/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: Retirado "retorna como se nao tivesse saido" (sugeria efeitos financeiros que o paragrafo nao detalha); substituido o exemplo de "promocao para a vaga"; melhorada a definicao de aproveitamento.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

O parágrafo trata da demissão de servidor estável invalidada por sentença judicial. O servidor é reintegrado. Quem ocupava a vaga, se for estável, volta ao cargo de origem sem indenização, é aproveitado em outro cargo ou fica em disponibilidade, com remuneração proporcional ao tempo de serviço.

**Depois (v2):**

Se a demissão de um servidor estável for invalidada por sentença judicial, ele será reintegrado.

Se a vaga estiver ocupada por outro servidor estável, a Constituição prevê para esse ocupante a recondução ao cargo de origem, sem indenização, o aproveitamento em outro cargo ou a disponibilidade com remuneração proporcional ao tempo de serviço.

### O QUE SIGNIFICA

**Antes (v1):**

Reintegração é a volta do servidor ao cargo de que foi ilegalmente demitido. Como a demissão foi anulada, ele retorna como se não tivesse saído.

O problema prático é a vaga, que pode ter sido ocupada por outra pessoa. O parágrafo resolve a situação do ocupante estável em três alternativas: recondução ao cargo de origem, aproveitamento em outro cargo ou disponibilidade com remuneração proporcional.

O ocupante reconduzido não tem direito a indenização, porque apenas volta à situação anterior.

**Depois (v2):**

Reintegração é o retorno do servidor estável ao cargo após a invalidação judicial de sua demissão.

A Constituição também precisa resolver a situação da pessoa que passou a ocupar aquela vaga.

Se esse ocupante também for estável, poderá retornar ao cargo de origem, ser aproveitado em outro cargo ou ficar em disponibilidade, conforme a situação aplicável.

A regra de ausência de indenização mencionada pelo parágrafo refere-se ao ocupante estável reconduzido.

### EXEMPLO PRÁTICO

**Antes (v1):**

Um fiscal estável é demitido e, anos depois, a Justiça anula a demissão. Ele é reintegrado ao cargo. A servidora estável que havia sido promovida para essa vaga volta ao seu cargo anterior, sem indenização.

**Depois (v2):**

Um fiscal estável é demitido. Posteriormente, uma sentença judicial invalida a demissão e ele deve ser reintegrado.

Se outro servidor estável estiver ocupando aquela vaga, poderá ser reconduzido ao seu cargo de origem, nas condições previstas pelo § 2º.

### ATENÇÃO

**Antes (v1):**

As três alternativas do parágrafo se referem ao ocupante estável da vaga. Os efeitos financeiros da reintegração para o servidor demitido não estão detalhados neste texto.

**Depois (v2):**

O § 2º não detalha os efeitos financeiros da reintegração do servidor cuja demissão foi invalidada.

Também não se deve confundir a indenização mencionada no dispositivo com eventuais efeitos financeiros relativos ao servidor reintegrado.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Reintegração**: retorno do servidor ao cargo após a anulação da sua demissão.
- **Recondução**: retorno do servidor estável ao cargo que ocupava antes.
- **Aproveitamento**: aproveitamento do servidor em disponibilidade em outro cargo compatível.
- **Disponibilidade**: situação do servidor estável que fica sem exercer o cargo, mas vinculado e remunerado proporcionalmente.

**Depois (v2):**

- **Reintegração**: retorno do servidor estável ao cargo após a invalidação judicial de sua demissão.
- **Recondução**: retorno do servidor estável ao cargo de origem na situação prevista pelo dispositivo.
- **Aproveitamento**: colocação do servidor em outro cargo adequado, conforme o regime jurídico aplicável.
- **Disponibilidade**: situação em que o servidor permanece vinculado à Administração sem exercer o cargo, nas condições constitucionais.

## `CF88:ART.41:PAR.4` — AJUSTAR

- ENTENDA/CF88:ART.41:PAR.4/BASE/1 → ENTENDA/CF88:ART.41:PAR.4/BASE/2 · PENDING_HUMAN_REVIEW (aguarda verificacao rapida final)
- Motivo: Retirados criterios inventados no exemplo (assiduidade, produtividade, responsabilidade); diferenca entre avaliacao especial e periodica explicitada; afastada a sugestao de exoneracao automatica.
- Seções alteradas: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS
- editorial_checks após a rodada: READY_FOR_EDITORIAL_REVIEW; achados: nenhum

### O QUE DIZ

**Antes (v1):**

O parágrafo torna obrigatória, como condição para adquirir estabilidade, uma avaliação especial de desempenho feita por comissão criada para essa finalidade.

**Depois (v2):**

O § 4º estabelece uma condição adicional para a aquisição da estabilidade: o servidor deve passar por avaliação especial de desempenho realizada por comissão criada para essa finalidade.

### O QUE SIGNIFICA

**Antes (v1):**

O tempo de exercício, sozinho, não basta. Além dos três anos do caput, o servidor precisa ser aprovado em uma avaliação especial.

A avaliação é feita por uma comissão instituída para isso, e não apenas pela chefia imediata. Ela verifica se o servidor demonstrou aptidão para o cargo durante o período inicial.

Esta avaliação é diferente da avaliação periódica do § 1º, III. A especial acontece antes da estabilidade e é condição para adquiri-la; a periódica acontece depois e pode levar à perda do cargo.

**Depois (v2):**

Completar três anos de efetivo exercício não é, isoladamente, suficiente para adquirir estabilidade.

A Constituição também exige a avaliação especial de desempenho.

Essa avaliação deve ser realizada por uma comissão instituída especificamente para essa finalidade, conforme a disciplina jurídica aplicável.

Ela não se confunde com a avaliação periódica mencionada no § 1º, III. A avaliação especial está ligada à aquisição da estabilidade; a periódica é prevista como possível fundamento para perda do cargo de servidor já estável e depende de lei complementar.

### EXEMPLO PRÁTICO

**Antes (v1):**

Ao fim do período inicial, uma comissão analisa assiduidade, produtividade e responsabilidade de um servidor. Aprovado, ele adquire estabilidade. Reprovado, não se torna estável e pode ser exonerado conforme a lei.

**Depois (v2):**

Uma servidora ingressa por concurso em cargo efetivo e completa o período de três anos.

Antes de adquirir estabilidade, deve ser submetida à avaliação especial realizada pela comissão competente, segundo os critérios definidos pelo regime jurídico aplicável.

### ATENÇÃO

**Antes (v1):**

Não confundir a avaliação especial (condição para adquirir estabilidade) com a avaliação periódica de desempenho (hipótese de perda do cargo de quem já é estável). Os critérios da avaliação especial estão na legislação de cada ente.

**Depois (v2):**

O § 4º não enumera os critérios concretos que a comissão deve utilizar.

Esses critérios e o procedimento da avaliação são disciplinados pela legislação aplicável.

Também não se deve tratar a avaliação especial e a avaliação periódica do § 1º, III, como se fossem o mesmo procedimento.

### PALAVRAS DIFÍCEIS

**Antes (v1):**

- **Avaliação especial de desempenho**: avaliação obrigatória para que o servidor adquira estabilidade.
- **Comissão**: grupo de pessoas designado para uma tarefa específica, aqui a avaliação do servidor.
- **Exoneração**: desligamento do servidor que não tem caráter de punição.

**Depois (v2):**

- **Avaliação especial de desempenho**: avaliação constitucionalmente exigida para aquisição da estabilidade.
- **Comissão**: grupo formalmente instituído para desempenhar determinada função.
- **Avaliação periódica de desempenho**: mecanismo distinto, previsto no § 1º, III, relacionado à possível perda do cargo do servidor estável.

