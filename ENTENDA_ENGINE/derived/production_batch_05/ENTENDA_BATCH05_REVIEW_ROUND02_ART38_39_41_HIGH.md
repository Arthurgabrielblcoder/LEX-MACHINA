# ENTENDA BATCH05 — RODADA 02 DE REVISÃO EDITORIAL ASSISTIDA — ARTS. 38, 39 e 41 (itens HIGH)

- Lote: `ENTENDA_CF_PRODUCTION_BATCH_05` · data de referência 2026-10-04 · escopo proposto `CF88_ARTS_38_39_41_HIGH_ROUND_2`
- Base textual: `CF88_RUNTIME` aprovado (texto por target idêntico ao runtime). A Lei Seca abaixo é o texto oficial vigente de cada target, sem alteração.
- Status de todas as explicações desta rodada: `PENDING_HUMAN_REVIEW` (editorial: `READY_FOR_EDITORIAL_REVIEW`). Nenhuma foi aprovada.
- Este pacote só reproduz o que já existe no projeto (drafts, checagens, notas de vigência, texto do runtime dos dispositivos citados pelo draft). Não contém sugestões novas.
- Já aprovados (não revisar aqui): Rodada 01 (art. 37, HIGH: XI, XVI, §§ 4º, 5º, 9º, 14 e 15) e os pilotos art. 37, § 6º e § 10.
- Restante HIGH após esta rodada: art. 40 (22 itens), proposto para a Rodada 03.
- Lembretes do padrão T1 (regras bloqueantes): no corpo não pode haver sigla de tribunal (ex.: "STF") nem número de processo/tema; no máximo 10 palavras seguidas iguais à Lei Seca; no máximo 5 PALAVRAS DIFÍCEIS; 80–400 palavras (visão geral: 120–560).

## Como responder

Para cada item: **APROVAR**, **AJUSTAR** (indicar seção e trecho, com o motivo) ou **REJEITAR** (motivo).
Verificar especialmente: fidelidade à Lei Seca, extrapolação, exceção inventada, simplificação que altere o sentido, regra permanente × transição, exemplo compatível.

## Itens (9)

1. `CF88:ART.38:INC.V` — Art. 38, inciso V — Previdência do servidor no mandato (ITEM)
2. `CF88:ART.39` — Art. 39 — Política de pessoal e remuneração dos servidores (OVERVIEW)
3. `CF88:ART.39:PAR.4` — Art. 39, §§ 4º e 8º — Subsídio em parcela única (BLOCK)
4. `CF88:ART.39:PAR.9` — Art. 39, § 9º — Proibição de incorporar vantagens temporárias (DEVICE)
5. `CF88:ART.41` — Art. 41 — Estabilidade do servidor público (OVERVIEW)
6. `CF88:ART.41:PAR.1` — Art. 41, § 1º — Hipóteses de perda do cargo do servidor estável (BLOCK)
7. `CF88:ART.41:PAR.2` — Art. 41, § 2º — Reintegração e recondução (DEVICE)
8. `CF88:ART.41:PAR.3` — Art. 41, § 3º — Disponibilidade do servidor estável (DEVICE)
9. `CF88:ART.41:PAR.4` — Art. 41, § 4º — Avaliação especial de desempenho (DEVICE)

---

## 1. Art. 38, inciso V — Previdência do servidor no mandato

- **target_id:** `CF88:ART.38:INC.V`
- **explanation_id:** `ENTENDA/CF88:ART.38:INC.V/BASE/1`
- **tipo:** ITEM (INCISO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.38`, `CF88:ART.38:CAPUT`
- **risco:** HIGH — previdencia: filiacao ao regime proprio do ente de origem
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.38:INC.V`: na hipótese de ser segurado de regime próprio de previdência social, permanecerá filiado a esse regime, no ente federativo de origem.

### Dispositivos citados pelo draft (texto do runtime, para conferência)

- `CF88:ART.40:PAR.13`: Aplica-se ao agente público ocupante, exclusivamente, de cargo em comissão declarado em lei de livre nomeação e exoneração, de outro cargo temporário, inclusive mandato eletivo, ou de emprego público, o Regime Geral de Previdência Social.

### Draft T1

**O QUE DIZ**

No art. 38, este inciso trata do servidor segurado de regime próprio de previdência que exerce mandato: ele continua filiado a esse regime, no ente federativo de origem.

**O QUE SIGNIFICA**

O servidor titular de cargo efetivo contribui para o regime próprio do seu ente, por exemplo o do Estado. Ao assumir um mandato, ele não passa a contribuir para outro regime em razão do mandato: continua vinculado ao regime próprio de onde veio.

A regra dá continuidade à vida previdenciária do servidor e evita a fragmentação do seu tempo de contribuição entre regimes diferentes.

**EXEMPLO PRÁTICO**

Um auditor fiscal do Estado, segurado do regime próprio estadual, é eleito deputado federal. Durante o mandato, ele continua filiado ao regime próprio do Estado, que é o seu ente de origem.

**ATENÇÃO**

O inciso vale para quem já é segurado de regime próprio. Detentores de mandato eletivo que não são servidores efetivos seguem, em regra, o Regime Geral, conforme o art. 40, § 13.

**PALAVRAS DIFÍCEIS**

- *Segurado*: pessoa vinculada a um regime de previdência, com direito aos seus benefícios.
- *Ente de origem*: União, Estado, Distrito Federal ou Município ao qual pertence o cargo efetivo do servidor.
- *Filiação*: vínculo jurídico da pessoa com um regime de previdência.

**CAMADA EXTERNA (external_layer_notes)**

—

### Avisos (editorial_checks e lint do motor)

- lint · NEAR_COPY_OF_OFFICIAL_TEXT (o_que_diz: a esse regime no ente federativo de origem)

### Vigência / redação (registro existente no projeto)

- nenhuma observação específica registrada

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 2. Art. 39 — Política de pessoal e remuneração dos servidores

- **target_id:** `CF88:ART.39`
- **explanation_id:** `ENTENDA/CF88:ART.39/BASE/1`
- **tipo:** OVERVIEW (ARTIGO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** —
- **risco:** HIGH — regime constitucional complexo: historico da redacao do caput (Vide ADI 2.135 na fonte canonica); nao resolvido no corpo
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.39:CAPUT`: A União, os Estados, o Distrito Federal e os Municípios instituirão conselho de política de administração e remuneração de pessoal, integrado por servidores designados pelos respectivos Poderes.
- `CF88:ART.39:PAR.1`: A fixação dos padrões de vencimento e dos demais componentes do sistema remuneratório observará:
- `CF88:ART.39:PAR.1:INC.I`: a natureza, o grau de responsabilidade e a complexidade dos cargos componentes de cada carreira;
- `CF88:ART.39:PAR.1:INC.II`: os requisitos para a investidura;
- `CF88:ART.39:PAR.1:INC.III`: as peculiaridades dos cargos.
- `CF88:ART.39:PAR.2`: A União, os Estados e o Distrito Federal manterão escolas de governo para a formação e o aperfeiçoamento dos servidores públicos, constituindo-se a participação nos cursos um dos requisitos para a promoção na carreira, facultada, para isso, a celebração de convênios ou contratos entre os entes federados.
- `CF88:ART.39:PAR.3`: Aplica-se aos servidores ocupantes de cargo público o disposto no art. 7º, IV, VII, VIII, IX, XII, XIII, XV, XVI, XVII, XVIII, XIX, XX, XXII e XXX, podendo a lei estabelecer requisitos diferenciados de admissão quando a natureza do cargo o exigir.
- `CF88:ART.39:PAR.4`: O membro de Poder, o detentor de mandato eletivo, os Ministros de Estado e os Secretários Estaduais e Municipais serão remunerados exclusivamente por subsídio fixado em parcela única, vedado o acréscimo de qualquer gratificação, adicional, abono, prêmio, verba de representação ou outra espécie remuneratória, obedecido, em qualquer caso, o disposto no art. 37, X e XI.
- `CF88:ART.39:PAR.5`: Lei da União, dos Estados, do Distrito Federal e dos Municípios poderá estabelecer a relação entre a maior e a menor remuneração dos servidores públicos, obedecido, em qualquer caso, o disposto no art. 37, XI.
- `CF88:ART.39:PAR.6`: Os Poderes Executivo, Legislativo e Judiciário publicarão anualmente os valores do subsídio e da remuneração dos cargos e empregos públicos.
- `CF88:ART.39:PAR.7`: Lei da União, dos Estados, do Distrito Federal e dos Municípios disciplinará a aplicação de recursos orçamentários provenientes da economia com despesas correntes em cada órgão, autarquia e fundação, para aplicação no desenvolvimento de programas de qualidade e produtividade, treinamento e desenvolvimento, modernização, reaparelhamento e racionalização do serviço público, inclusive sob a forma de adicional ou prêmio de produtividade.
- `CF88:ART.39:PAR.8`: A remuneração dos servidores públicos organizados em carreira poderá ser fixada nos termos do § 4º.
- `CF88:ART.39:PAR.9`: É vedada a incorporação de vantagens de caráter temporário ou vinculadas ao exercício de função de confiança ou de cargo em comissão à remuneração do cargo efetivo.

### Draft T1

**O QUE DIZ**

O art. 39 organiza a política de pessoal dos servidores. O caput manda cada ente instituir um conselho de política de administração e remuneração de pessoal, formado por servidores indicados pelos Poderes. Os parágrafos tratam dos critérios da remuneração, das escolas de governo, dos direitos sociais aplicáveis, do subsídio, dos limites internos da remuneração, da publicação dos valores, do uso da economia de despesas e da proibição de incorporar vantagens.

**O QUE SIGNIFICA**

Enquanto o art. 37 traz princípios e regras gerais da administração, o art. 39 se concentra em como os servidores são remunerados, formados e organizados em carreira.

O conselho do caput é um órgão de apoio: reúne servidores designados pelos Poderes para pensar a política de administração e de remuneração de pessoal, de modo coordenado. O texto não define as suas competências nem a sua composição numérica, que ficam a cargo de cada ente.

Os parágrafos podem ser lidos em grupos: como fixar a remuneração (§§ 1º, 4º, 5º e 8º), como formar e valorizar o servidor (§§ 2º e 7º), quais direitos trabalhistas se estendem a ele (§ 3º), a transparência dos valores (§ 6º) e a vedação de incorporar vantagens temporárias (§ 9º).

Todos os entes se submetem a essas regras, respeitada a autonomia de cada um para editar as suas leis de pessoal.

**EXEMPLO PRÁTICO**

Um Município cria, por lei, o seu conselho de política de administração e remuneração, com servidores indicados pelo Executivo e pela Câmara. Ao reestruturar a carreira de fiscal, o Município considera a complexidade do cargo e os requisitos de ingresso, publica anualmente os valores da remuneração e não permite que a gratificação de chefia seja incorporada ao cargo efetivo.

**ATENÇÃO**

O art. 39 convive com o art. 37: teto, irredutibilidade e exigência de lei para fixar remuneração estão no art. 37 e continuam valendo. A redação do caput tem histórico constitucional complexo, ligado ao regime jurídico dos servidores; qual redação produz efeitos deve ser conferido na camada externa, e não deduzido só da leitura deste texto.

**PALAVRAS DIFÍCEIS**

- *Política remuneratória*: conjunto de critérios e decisões sobre como os servidores são pagos.
- *Carreira*: conjunto de cargos organizados em níveis, pelos quais o servidor avança.
- *Designação*: indicação formal de alguém para exercer uma função.
- *Subsídio*: remuneração fixada em parcela única, sem acréscimos de outras espécies remuneratórias (art. 39, § 4º).

**CAMADA EXTERNA (external_layer_notes)**

- A fonte estrutural canônica do projeto registra, junto ao caput, a remissão "Vide ADI nº 2.135" e a redação original sobre regime jurídico único e planos de carreira. A eficácia de cada redação do caput é tema da camada JURISPRUDÊNCIA.

### Avisos (editorial_checks e lint do motor)

- lint · NEAR_COPY_OF_OFFICIAL_TEXT (o_que_diz: conselho de política de administração e remuneração de)

### Vigência / redação (registro existente no projeto)

- redacao da EC 19/1998 com "Vide ADI nº 2.135" e redacao original sobre regime juridico unico na fonte canonica: nao resolvido no corpo (ATENCAO + camada JURISPRUDENCIA)

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 3. Art. 39, §§ 4º e 8º — Subsídio em parcela única

- **target_id:** `CF88:ART.39:PAR.4`
- **explanation_id:** `ENTENDA/CF88:ART.39:PAR.4/BASE/1`
- **tipo:** BLOCK (PARAGRAFO)
- **targets cobertos:** `CF88:ART.39:PAR.8`
- **contexto estrutural:** `CF88:ART.39`
- **risco:** HIGH — subsidio em parcela unica e teto (art. 37, X e XI); parcelas indenizatorias fora do texto
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.39:PAR.4`: O membro de Poder, o detentor de mandato eletivo, os Ministros de Estado e os Secretários Estaduais e Municipais serão remunerados exclusivamente por subsídio fixado em parcela única, vedado o acréscimo de qualquer gratificação, adicional, abono, prêmio, verba de representação ou outra espécie remuneratória, obedecido, em qualquer caso, o disposto no art. 37, X e XI.
- `CF88:ART.39:PAR.8`: A remuneração dos servidores públicos organizados em carreira poderá ser fixada nos termos do § 4º.

### Dispositivos citados pelo draft (texto do runtime, para conferência)

- `CF88:ART.37:INC.X`: a remuneração dos servidores públicos e o subsídio de que trata o § 4º do art. 39 somente poderão ser fixados ou alterados por lei específica, observada a iniciativa privativa em cada caso, assegurada revisão geral anual, sempre na mesma data e sem distinção de índices;
- `CF88:ART.37:INC.XI`: a remuneração e o subsídio dos ocupantes de cargos, funções e empregos públicos da administração direta, autárquica e fundacional, dos membros de qualquer dos Poderes da União, dos Estados, do Distrito Federal e dos Municípios, dos detentores de mandato eletivo e dos demais agentes políticos e os proventos, pensões ou outra espécie remuneratória, percebidos cumulativamente ou não, incluídas as vantagens pessoais ou de qualquer outra natureza, não poderão exceder o subsídio mensal, em espécie, dos Ministros do Supremo Tribunal Federal, aplicando-se como limite, nos Municípios, o subsídio do Prefeito, e nos Estados e no Distrito Federal, o subsídio mensal do Governador no âmbito do Poder Executivo, o subsídio dos Deputados Estaduais e Distritais no âmbito do Poder Legislativo e o subsídio dos Desembargadores do Tribunal de Justiça, limitado a noventa inteiros e vinte e cinco centésimos por cento do subsídio mensal, em espécie, dos Ministros do Supremo Tribunal Federal, no âmbito do Poder Judiciário, aplicável este limite aos membros do Ministério Público, aos Procuradores e aos Defensores Públicos;
- `CF88:ART.37:PAR.11`: Não serão computadas, para efeito dos limites remuneratórios de que trata o inciso XI do caput deste artigo, as parcelas de caráter indenizatório expressamente previstas em lei ordinária, aprovada pelo Congresso Nacional, de caráter nacional, aplicada a todos os Poderes e órgãos constitucionalmente autônomos. ( Vide o art. 3º da Emenda Constitucional nº 135/2024 )

### Draft T1

**O QUE DIZ**

O § 4º manda remunerar por subsídio, em parcela única, os membros de Poder, os detentores de mandato eletivo, os Ministros de Estado e os Secretários dos Estados e dos Municípios, proibindo acréscimos como gratificações, adicionais, abonos e prêmios, e mandando observar o art. 37, X e XI. O § 8º permite que servidores organizados em carreira também sejam remunerados assim.

**O QUE SIGNIFICA**

Subsídio é uma forma de remuneração em valor único. O objetivo é transparência: em vez de um vencimento básico somado a muitas parcelas, há um valor só, fácil de conhecer e de comparar com o teto.

Para as autoridades listadas no § 4º, o subsídio é obrigatório. Membros de Poder são, por exemplo, parlamentares, chefes do Executivo e magistrados.

Para servidores organizados em carreira, o § 8º torna o subsídio uma opção do legislador.

O subsídio também depende de lei específica e se sujeita ao teto, por força da remissão ao art. 37, X e XI.

**EXEMPLO PRÁTICO**

Um deputado estadual recebe subsídio fixado em parcela única e não pode receber, além dele, uma gratificação por presidir uma comissão. Já uma lei pode organizar a carreira de procurador do Estado em subsídio, com base no § 8º.

**ATENÇÃO**

A proibição atinge parcelas de natureza remuneratória. O texto não trata de parcelas que apenas indenizam despesas; o tratamento delas depende de interpretação e das regras do teto (art. 37, § 11).

**PALAVRAS DIFÍCEIS**

- *Subsídio*: remuneração fixada em parcela única, sem acréscimos de outras espécies remuneratórias.
- *Membro de Poder*: agente que integra a cúpula de um Poder, como parlamentares, chefes do Executivo e magistrados.
- *Verba de representação*: parcela paga em razão do cargo para custear atividades de representação.

**CAMADA EXTERNA (external_layer_notes)**

- Quais parcelas podem ser pagas junto com o subsídio (por exemplo, décimo terceiro e terço de férias) é tema da camada JURISPRUDÊNCIA.

### Avisos (editorial_checks e lint do motor)

- lint · NEAR_COPY_OF_OFFICIAL_TEXT (o_que_diz: de mandato eletivo os ministros de estado e)

### Vigência / redação (registro existente no projeto)

- nenhuma observação específica registrada

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 4. Art. 39, § 9º — Proibição de incorporar vantagens temporárias

- **target_id:** `CF88:ART.39:PAR.9`
- **explanation_id:** `ENTENDA/CF88:ART.39:PAR.9/BASE/1`
- **tipo:** DEVICE (PARAGRAFO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.39`
- **risco:** HIGH — vedacao de incorporacao (EC 103/2019); transicao fora do texto
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.39:PAR.9`: É vedada a incorporação de vantagens de caráter temporário ou vinculadas ao exercício de função de confiança ou de cargo em comissão à remuneração do cargo efetivo.

### Draft T1

**O QUE DIZ**

O parágrafo proíbe incorporar à remuneração do cargo efetivo as vantagens temporárias e as que decorrem do exercício de função de confiança ou de cargo em comissão.

**O QUE SIGNIFICA**

Incorporar significa transformar uma vantagem passageira em parte permanente da remuneração. Por exemplo, depois de alguns anos recebendo gratificação de chefia, o servidor passaria a recebê-la de forma permanente, mesmo sem continuar chefiando.

O parágrafo proíbe isso. A gratificação de função ou de cargo em comissão é paga enquanto o servidor exerce a função; quando ela termina, a parcela deixa de ser paga.

A regra evita que a remuneração cresça de forma permanente por atividades exercidas apenas por um tempo.

**EXEMPLO PRÁTICO**

Uma servidora ocupou por seis anos a função de diretora de um departamento, com gratificação. Ao deixar a função, volta a receber apenas a remuneração do seu cargo efetivo, sem incorporar a gratificação.

**ATENÇÃO**

O parágrafo foi incluído pela reforma da previdência de 2019. Incorporações ocorridas antes dela dependem das regras de transição da emenda, que não estão neste parágrafo.

**PALAVRAS DIFÍCEIS**

- *Incorporação*: transformação de uma vantagem temporária em parte permanente da remuneração.
- *Vantagem de caráter temporário*: parcela paga apenas enquanto existe certa situação ou atividade.

**CAMADA EXTERNA (external_layer_notes)**

- As regras de transição da Emenda Constitucional nº 103/2019 sobre incorporações anteriores devem ser consultadas na própria emenda.

### Avisos (editorial_checks e lint do motor)

- lint · NEAR_COPY_OF_OFFICIAL_TEXT (o_que_diz: de função de confiança ou de cargo em)

### Vigência / redação (registro existente no projeto)

- Incluido pela EC 103/2019

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 5. Art. 41 — Estabilidade do servidor público

- **target_id:** `CF88:ART.41`
- **explanation_id:** `ENTENDA/CF88:ART.41/BASE/1`
- **tipo:** OVERVIEW (ARTIGO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** —
- **risco:** HIGH — estabilidade, perda do cargo e seus efeitos (redacao da EC 19/1998); hipotese do art. 169, § 4º, fora do art. 41
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.41:CAPUT`: São estáveis após três anos de efetivo exercício os servidores nomeados para cargo de provimento efetivo em virtude de concurso público.
- `CF88:ART.41:PAR.1`: O servidor público estável só perderá o cargo:
- `CF88:ART.41:PAR.2`: Invalidada por sentença judicial a demissão do servidor estável, será ele reintegrado, e o eventual ocupante da vaga, se estável, reconduzido ao cargo de origem, sem direito a indenização, aproveitado em outro cargo ou posto em disponibilidade com remuneração proporcional ao tempo de serviço.
- `CF88:ART.41:PAR.3`: Extinto o cargo ou declarada a sua desnecessidade, o servidor estável ficará em disponibilidade, com remuneração proporcional ao tempo de serviço, até seu adequado aproveitamento em outro cargo.
- `CF88:ART.41:PAR.1:INC.I`: em virtude de sentença judicial transitada em julgado;
- `CF88:ART.41:PAR.1:INC.II`: mediante processo administrativo em que lhe seja assegurada ampla defesa;
- `CF88:ART.41:PAR.1:INC.III`: mediante procedimento de avaliação periódica de desempenho, na forma de lei complementar, assegurada ampla defesa.
- `CF88:ART.41:PAR.4`: Como condição para a aquisição da estabilidade, é obrigatória a avaliação especial de desempenho por comissão instituída para essa finalidade.

### Dispositivos citados pelo draft (texto do runtime, para conferência)

- `CF88:ART.169:PAR.4`: Se as medidas adotadas com base no parágrafo anterior não forem suficientes para assegurar o cumprimento da determinação da lei complementar referida neste artigo, o servidor estável poderá perder o cargo, desde que ato normativo motivado de cada um dos Poderes especifique a atividade funcional, o órgão ou unidade administrativa objeto da redução de pessoal.

### Draft T1

**O QUE DIZ**

O art. 41 trata da estabilidade do servidor público. O caput garante estabilidade, após três anos de efetivo exercício, aos servidores nomeados por concurso para cargo de provimento efetivo. Os parágrafos tratam das hipóteses de perda do cargo, da reintegração após demissão invalidada, da disponibilidade e da avaliação especial de desempenho.

**O QUE SIGNIFICA**

Estabilidade é a garantia de permanência no serviço público. O servidor estável só pode perder o cargo nas hipóteses que a Constituição admite. Ela protege o servidor contra demissões arbitrárias e, com isso, protege também a impessoalidade e a continuidade da administração.

O caput traz três condições cumulativas: cargo de provimento efetivo, nomeação em virtude de concurso público e três anos de efetivo exercício. A essas condições, o § 4º acrescenta a aprovação em avaliação especial de desempenho.

Estabilidade é diferente de efetividade. Efetividade é a característica do cargo, ocupado de forma permanente. Estabilidade é a garantia que o servidor adquire depois do período e da avaliação.

O período antes da estabilidade é conhecido como estágio probatório.

**EXEMPLO PRÁTICO**

Uma analista toma posse em cargo efetivo depois de aprovada em concurso. Durante os três primeiros anos, ela é acompanhada e avaliada. Aprovada na avaliação especial e completado o período, torna-se estável e só pode perder o cargo nas hipóteses do § 1º.

**ATENÇÃO**

A estabilidade não alcança ocupantes só de cargo em comissão nem contratados temporários. A Constituição também prevê, no art. 169, § 4º, perda do cargo do servidor estável por excesso de despesa com pessoal, hipótese que está fora do art. 41.

**PALAVRAS DIFÍCEIS**

- *Estabilidade*: garantia de permanência no serviço público, com perda do cargo só nas hipóteses constitucionais.
- *Cargo de provimento efetivo*: cargo ocupado de forma permanente, após concurso.
- *Estágio probatório*: período inicial em que o servidor é avaliado antes de adquirir estabilidade.
- *Disponibilidade*: situação do servidor estável que fica sem exercer o cargo, mas vinculado e remunerado proporcionalmente.
- *Reintegração*: retorno do servidor ao cargo após a anulação da sua demissão.

**CAMADA EXTERNA (external_layer_notes)**

- A relação entre o prazo do estágio probatório e o prazo da estabilidade é tema da camada JURISPRUDÊNCIA.

### Avisos (editorial_checks e lint do motor)

- editorial_checks · LAW_DEPENDENCY_OMITTED (body: de lei) → resolução registrada: a lei complementar da avaliacao periodica (§ 1º, III) e explicada no bloco CF88:ART.41:PAR.1; a visao geral situa as hipoteses.

### Vigência / redação (registro existente no projeto)

- redacao da EC 19/1998 (tres anos, § 1º I-III, § 4º)

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 6. Art. 41, § 1º — Hipóteses de perda do cargo do servidor estável

- **target_id:** `CF88:ART.41:PAR.1`
- **explanation_id:** `ENTENDA/CF88:ART.41:PAR.1/BASE/1`
- **tipo:** BLOCK (PARAGRAFO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.41`
- **risco:** HIGH — estabilidade, perda do cargo e seus efeitos (redacao da EC 19/1998); hipotese do art. 169, § 4º, fora do art. 41
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.41:PAR.1`: O servidor público estável só perderá o cargo:
- `CF88:ART.41:PAR.1:INC.I`: em virtude de sentença judicial transitada em julgado;
- `CF88:ART.41:PAR.1:INC.II`: mediante processo administrativo em que lhe seja assegurada ampla defesa;
- `CF88:ART.41:PAR.1:INC.III`: mediante procedimento de avaliação periódica de desempenho, na forma de lei complementar, assegurada ampla defesa.

### Dispositivos citados pelo draft (texto do runtime, para conferência)

- `CF88:ART.247:CAPUT`: As leis previstas no inciso III do § 1º do art. 41 e no § 7º do art. 169 estabelecerão critérios e garantias especiais para a perda do cargo pelo servidor público estável que, em decorrência das atribuições de seu cargo efetivo, desenvolva atividades exclusivas de Estado.
- `CF88:ART.169:PAR.4`: Se as medidas adotadas com base no parágrafo anterior não forem suficientes para assegurar o cumprimento da determinação da lei complementar referida neste artigo, o servidor estável poderá perder o cargo, desde que ato normativo motivado de cada um dos Poderes especifique a atividade funcional, o órgão ou unidade administrativa objeto da redução de pessoal.

### Draft T1

**O QUE DIZ**

O parágrafo lista as formas pelas quais o servidor estável pode perder o cargo: por sentença judicial transitada em julgado; por processo administrativo com ampla defesa; e por avaliação periódica de desempenho, na forma de lei complementar, também com ampla defesa.

**O QUE SIGNIFICA**

As três hipóteses têm em comum a garantia de defesa.

Na primeira, a perda decorre de decisão judicial definitiva, contra a qual não cabe mais recurso, como uma condenação que determina a perda do cargo.

Na segunda, a administração apura uma falta grave em processo próprio, com direito a contraditório e ampla defesa, e aplica a demissão.

Na terceira, a perda resulta de desempenho insuficiente apurado em avaliações periódicas. Essa hipótese depende de lei complementar e também assegura ampla defesa.

**EXEMPLO PRÁTICO**

Um servidor estável é flagrado recebendo vantagem indevida. A administração instaura processo administrativo disciplinar, garante a sua defesa e, comprovada a falta, aplica a demissão. Se outro servidor tiver desempenho insuficiente, a perda do cargo por esse motivo só pode ocorrer nos termos da lei complementar que regula a avaliação periódica.

**ATENÇÃO**

O art. 247 manda que a lei preveja critérios e garantias especiais para a perda do cargo por desempenho de servidores que exercem atividades exclusivas de Estado. Fora do art. 41, o art. 169, § 4º, prevê outra hipótese: excesso de despesa com pessoal.

**PALAVRAS DIFÍCEIS**

- *Transitada em julgado*: diz-se da decisão judicial que se tornou definitiva, sem possibilidade de recurso.
- *Ampla defesa*: direito de usar todos os meios legítimos para se defender.
- *Processo administrativo disciplinar*: procedimento da administração para apurar faltas de servidores.

**CAMADA EXTERNA (external_layer_notes)**

- A situação da lei complementar sobre avaliação periódica de desempenho deve ser verificada na camada de leis correlatas.

### Avisos (editorial_checks e lint do motor)

- lint · NEAR_COPY_OF_OFFICIAL_TEXT (o_que_diz: avaliação periódica de desempenho na forma de lei)

### Vigência / redação (registro existente no projeto)

- redacao da EC 19/1998 (tres anos, § 1º I-III, § 4º)

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 7. Art. 41, § 2º — Reintegração e recondução

- **target_id:** `CF88:ART.41:PAR.2`
- **explanation_id:** `ENTENDA/CF88:ART.41:PAR.2/BASE/1`
- **tipo:** DEVICE (PARAGRAFO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.41`
- **risco:** HIGH — estabilidade, perda do cargo e seus efeitos (redacao da EC 19/1998); hipotese do art. 169, § 4º, fora do art. 41
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.41:PAR.2`: Invalidada por sentença judicial a demissão do servidor estável, será ele reintegrado, e o eventual ocupante da vaga, se estável, reconduzido ao cargo de origem, sem direito a indenização, aproveitado em outro cargo ou posto em disponibilidade com remuneração proporcional ao tempo de serviço.

### Draft T1

**O QUE DIZ**

O parágrafo trata da demissão de servidor estável invalidada por sentença judicial. O servidor é reintegrado. Quem ocupava a vaga, se for estável, volta ao cargo de origem sem indenização, é aproveitado em outro cargo ou fica em disponibilidade, com remuneração proporcional ao tempo de serviço.

**O QUE SIGNIFICA**

Reintegração é a volta do servidor ao cargo de que foi ilegalmente demitido. Como a demissão foi anulada, ele retorna como se não tivesse saído.

O problema prático é a vaga, que pode ter sido ocupada por outra pessoa. O parágrafo resolve a situação do ocupante estável em três alternativas: recondução ao cargo de origem, aproveitamento em outro cargo ou disponibilidade com remuneração proporcional.

O ocupante reconduzido não tem direito a indenização, porque apenas volta à situação anterior.

**EXEMPLO PRÁTICO**

Um fiscal estável é demitido e, anos depois, a Justiça anula a demissão. Ele é reintegrado ao cargo. A servidora estável que havia sido promovida para essa vaga volta ao seu cargo anterior, sem indenização.

**ATENÇÃO**

As três alternativas do parágrafo se referem ao ocupante estável da vaga. Os efeitos financeiros da reintegração para o servidor demitido não estão detalhados neste texto.

**PALAVRAS DIFÍCEIS**

- *Reintegração*: retorno do servidor ao cargo após a anulação da sua demissão.
- *Recondução*: retorno do servidor estável ao cargo que ocupava antes.
- *Aproveitamento*: aproveitamento do servidor em disponibilidade em outro cargo compatível.
- *Disponibilidade*: situação do servidor estável que fica sem exercer o cargo, mas vinculado e remunerado proporcionalmente.

**CAMADA EXTERNA (external_layer_notes)**

—

### Avisos (editorial_checks e lint do motor)

- lint · NEAR_COPY_OF_OFFICIAL_TEXT (o_que_diz: disponibilidade com remuneração proporcional ao tempo de serviço)

### Vigência / redação (registro existente no projeto)

- redacao da EC 19/1998 (tres anos, § 1º I-III, § 4º)

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 8. Art. 41, § 3º — Disponibilidade do servidor estável

- **target_id:** `CF88:ART.41:PAR.3`
- **explanation_id:** `ENTENDA/CF88:ART.41:PAR.3/BASE/1`
- **tipo:** DEVICE (PARAGRAFO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.41`
- **risco:** HIGH — estabilidade, perda do cargo e seus efeitos (redacao da EC 19/1998); hipotese do art. 169, § 4º, fora do art. 41
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.41:PAR.3`: Extinto o cargo ou declarada a sua desnecessidade, o servidor estável ficará em disponibilidade, com remuneração proporcional ao tempo de serviço, até seu adequado aproveitamento em outro cargo.

### Draft T1

**O QUE DIZ**

O parágrafo prevê que, quando o cargo é extinto ou declarado desnecessário, o servidor estável passa à disponibilidade, recebendo de forma proporcional ao seu tempo de serviço, até ser aproveitado de modo adequado em outro cargo.

**O QUE SIGNIFICA**

A estabilidade protege o servidor, mas não o cargo. A administração pode extinguir cargos ou declará-los desnecessários, por exemplo em uma reorganização.

Nesse caso, o servidor estável não é demitido. Ele fica em disponibilidade: deixa de trabalhar, mas continua vinculado e recebe remuneração proporcional ao seu tempo de serviço.

A disponibilidade é provisória: dura até o aproveitamento em outro cargo adequado.

**EXEMPLO PRÁTICO**

Um Município extingue o cargo de datilógrafo, que se tornou desnecessário. O servidor estável que o ocupava fica em disponibilidade, recebendo proporcionalmente ao seu tempo de serviço, até ser aproveitado em um cargo administrativo compatível.

**ATENÇÃO**

A remuneração na disponibilidade é proporcional ao tempo de serviço, e não necessariamente integral. A garantia vale para o servidor estável.

**PALAVRAS DIFÍCEIS**

- *Disponibilidade*: situação do servidor estável que fica sem exercer o cargo, mas vinculado e remunerado proporcionalmente.
- *Desnecessidade*: declaração de que o cargo deixou de ser útil à administração.

**CAMADA EXTERNA (external_layer_notes)**

—

### Avisos (editorial_checks e lint do motor)

- editorial_checks · FACT_INCONSISTENCY (DISPONIBILIDADE_PROPORCIONAL: A remuneração na disponibilidade é proporcional ao tempo de serviço, e não necessariamente) → resolução registrada: falso positivo da regra: a frase afirma a proporcionalidade do texto e nega a integralidade, exatamente o que a regra protege.

### Vigência / redação (registro existente no projeto)

- redacao da EC 19/1998 (tres anos, § 1º I-III, § 4º)

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 9. Art. 41, § 4º — Avaliação especial de desempenho

- **target_id:** `CF88:ART.41:PAR.4`
- **explanation_id:** `ENTENDA/CF88:ART.41:PAR.4/BASE/1`
- **tipo:** DEVICE (PARAGRAFO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.41`
- **risco:** HIGH — estabilidade, perda do cargo e seus efeitos (redacao da EC 19/1998); hipotese do art. 169, § 4º, fora do art. 41
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.41:PAR.4`: Como condição para a aquisição da estabilidade, é obrigatória a avaliação especial de desempenho por comissão instituída para essa finalidade.

### Draft T1

**O QUE DIZ**

O parágrafo torna obrigatória, como condição para adquirir estabilidade, uma avaliação especial de desempenho feita por comissão criada para essa finalidade.

**O QUE SIGNIFICA**

O tempo de exercício, sozinho, não basta. Além dos três anos do caput, o servidor precisa ser aprovado em uma avaliação especial.

A avaliação é feita por uma comissão instituída para isso, e não apenas pela chefia imediata. Ela verifica se o servidor demonstrou aptidão para o cargo durante o período inicial.

Esta avaliação é diferente da avaliação periódica do § 1º, III. A especial acontece antes da estabilidade e é condição para adquiri-la; a periódica acontece depois e pode levar à perda do cargo.

**EXEMPLO PRÁTICO**

Ao fim do período inicial, uma comissão analisa assiduidade, produtividade e responsabilidade de um servidor. Aprovado, ele adquire estabilidade. Reprovado, não se torna estável e pode ser exonerado conforme a lei.

**ATENÇÃO**

Não confundir a avaliação especial (condição para adquirir estabilidade) com a avaliação periódica de desempenho (hipótese de perda do cargo de quem já é estável). Os critérios da avaliação especial estão na legislação de cada ente.

**PALAVRAS DIFÍCEIS**

- *Avaliação especial de desempenho*: avaliação obrigatória para que o servidor adquira estabilidade.
- *Comissão*: grupo de pessoas designado para uma tarefa específica, aqui a avaliação do servidor.
- *Exoneração*: desligamento do servidor que não tem caráter de punição.

**CAMADA EXTERNA (external_layer_notes)**

—

### Avisos (editorial_checks e lint do motor)

- nenhum

### Vigência / redação (registro existente no projeto)

- redacao da EC 19/1998 (tres anos, § 1º I-III, § 4º)

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

