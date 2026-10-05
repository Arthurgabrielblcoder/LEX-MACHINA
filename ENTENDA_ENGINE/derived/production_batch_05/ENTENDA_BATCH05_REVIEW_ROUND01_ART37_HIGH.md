# ENTENDA BATCH05 — RODADA 01 DE REVISÃO EDITORIAL ASSISTIDA — ART. 37 (itens HIGH)

- Lote: `ENTENDA_CF_PRODUCTION_BATCH_05` · data de referência 2026-10-04
- Base textual: `CF88_RUNTIME` aprovado (texto por target idêntico ao runtime). A Lei Seca abaixo é o texto oficial vigente de cada target, sem alteração.
- Status de todas as explicações: `PENDING_HUMAN_REVIEW` (editorial: `READY_FOR_EDITORIAL_REVIEW`). Nenhuma foi aprovada.
- Este pacote só reproduz o que já existe no projeto (drafts, checagens, notas de vigência). Não contém sugestões novas.
- Contexto já aprovado (não revisar aqui): visão geral `CF88:ART.37`, `CF88:ART.37:PAR.6` e `CF88:ART.37:PAR.10` (pilotos `HUMAN_APPROVED_T1`).

## Como responder

Para cada item: **APROVAR**, **AJUSTAR** (indicar seção e trecho, com o motivo) ou **REJEITAR** (motivo).
Verificar especialmente: fidelidade à Lei Seca, extrapolação, exceção inventada, simplificação que altere o sentido, regra permanente × transição, exemplo compatível.

## Itens (7)

1. `CF88:ART.37:INC.XI` — Art. 37, inciso XI — Teto remuneratório e subtetos
2. `CF88:ART.37:INC.XVI` — Art. 37, incisos XVI e XVII — Acumulação de cargos públicos
3. `CF88:ART.37:PAR.4` — Art. 37, § 4º — Improbidade administrativa
4. `CF88:ART.37:PAR.5` — Art. 37, § 5º — Prescrição de ilícitos contra o erário
5. `CF88:ART.37:PAR.9` — Art. 37, §§ 9º, 11 e 12 — Teto: estatais dependentes, parcelas indenizatórias e subteto único
6. `CF88:ART.37:PAR.14` — Art. 37, § 14 — Aposentadoria e rompimento do vínculo
7. `CF88:ART.37:PAR.15` — Art. 37, § 15 — Vedação de complementação de aposentadorias e pensões

---

## 1. Art. 37, inciso XI — Teto remuneratório e subtetos

- **target_id:** `CF88:ART.37:INC.XI`
- **explanation_id:** `ENTENDA/CF88:ART.37:INC.XI/BASE/1`
- **tipo:** ITEM (INCISO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.37`, `CF88:ART.37:CAPUT`
- **risco:** HIGH — teto e subtetos por ente e Poder; percentual de 90,25%; alcance sobre proventos e vantagens pessoais
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.37:INC.XI`: a remuneração e o subsídio dos ocupantes de cargos, funções e empregos públicos da administração direta, autárquica e fundacional, dos membros de qualquer dos Poderes da União, dos Estados, do Distrito Federal e dos Municípios, dos detentores de mandato eletivo e dos demais agentes políticos e os proventos, pensões ou outra espécie remuneratória, percebidos cumulativamente ou não, incluídas as vantagens pessoais ou de qualquer outra natureza, não poderão exceder o subsídio mensal, em espécie, dos Ministros do Supremo Tribunal Federal, aplicando-se como limite, nos Municípios, o subsídio do Prefeito, e nos Estados e no Distrito Federal, o subsídio mensal do Governador no âmbito do Poder Executivo, o subsídio dos Deputados Estaduais e Distritais no âmbito do Poder Legislativo e o subsídio dos Desembargadores do Tribunal de Justiça, limitado a noventa inteiros e vinte e cinco centésimos por cento do subsídio mensal, em espécie, dos Ministros do Supremo Tribunal Federal, no âmbito do Poder Judiciário, aplicável este limite aos membros do Ministério Público, aos Procuradores e aos Defensores Públicos;

### Draft T1

**O QUE DIZ**

Dentro das regras do art. 37, o inciso XI fixa um teto para tudo o que é pago a agentes públicos: remuneração, subsídio, proventos, pensões e vantagens de qualquer natureza, somados ou não. O teto geral é o subsídio dos Ministros do Supremo Tribunal Federal. Nos Municípios e nos Estados e Distrito Federal há limites próprios, os subtetos.

**O QUE SIGNIFICA**

O teto é o valor máximo que um agente público pode receber dos cofres públicos. Ele alcança servidores da administração direta, autárquica e fundacional, membros dos Poderes, detentores de mandato eletivo, aposentados e pensionistas.

Os subtetos funcionam assim. Nos Municípios, o limite é o subsídio do Prefeito. Nos Estados e no Distrito Federal, o limite varia por Poder: no Executivo, o subsídio do Governador; no Legislativo, o dos Deputados Estaduais e Distritais; no Judiciário, o dos Desembargadores do Tribunal de Justiça. Esse último fica limitado a 90,25% do subsídio dos Ministros do Supremo e também vale para membros do Ministério Público, Procuradores e Defensores Públicos.

O teto alcança também as vantagens pessoais e o total recebido cumulativamente.

**EXEMPLO PRÁTICO**

Um servidor municipal acumula licitamente dois cargos e, somadas as remunerações, ultrapassaria o subsídio do Prefeito. Pelo texto do inciso, a soma está sujeita ao teto municipal, e o excedente não é pago.

**ATENÇÃO**

Algumas regras completam o teto e estão em outros dispositivos: a extensão às estatais que recebem recursos públicos, as parcelas indenizatórias excluídas e o subteto único facultativo dos Estados (§§ 9º, 11 e 12). O teto para a soma de aposentadorias e remunerações também aparece no art. 40, § 11.

**PALAVRAS DIFÍCEIS**

- *Teto remuneratório*: limite máximo de tudo o que um agente público pode receber dos cofres públicos.
- *Subteto*: limite próprio de um ente ou Poder, abaixo do teto geral.
- *Vantagem pessoal*: parcela paga em razão da situação individual do servidor, como adicionais por tempo de serviço.
- *Subsídio*: remuneração fixada em parcela única, sem acréscimos de outras espécies remuneratórias (art. 39, § 4º).
- *Proventos*: valor pago ao servidor aposentado.

**CAMADA EXTERNA (external_layer_notes)**

- A aplicação do teto a cada cargo, em casos de acumulação lícita, e o enquadramento de parcelas específicas são temas da camada JURISPRUDÊNCIA.

### Avisos (editorial_checks e lint do motor)

- editorial_checks · EXTRAPOLATION_NUMBER (o_que_significa: 90,25%) → resolução registrada: equivalente numerico de "noventa inteiros e vinte e cinco centesimos por cento" do texto oficial.
- editorial_checks · TECHNICAL_TERM_UNDEFINED (body: pensionista) → resolução registrada: termo de uso comum explicado no contexto (aposentados e pensionistas citados com "pensoes" do texto); glossario ja no limite util de termos centrais.

### Vigência / redação (registro existente no projeto)

- nenhuma observação específica registrada

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 2. Art. 37, incisos XVI e XVII — Acumulação de cargos públicos

- **target_id:** `CF88:ART.37:INC.XVI`
- **explanation_id:** `ENTENDA/CF88:ART.37:INC.XVI/BASE/1`
- **tipo:** BLOCK (INCISO)
- **targets cobertos:** `CF88:ART.37:INC.XVII`
- **contexto estrutural:** `CF88:ART.37`, `CF88:ART.37:CAPUT`
- **risco:** HIGH — acumulacao de cargos; alinea "b" alterada pela EC 138/2025 (redacao recente); compatibilidade e teto
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.37:INC.XVI`: é vedada a acumulação remunerada de cargos públicos, exceto, quando houver compatibilidade de horários, observado em qualquer caso o disposto no inciso XI:
- `CF88:ART.37:INC.XVI:AL.a`: a de dois cargos de professor;
- `CF88:ART.37:INC.XVI:AL.b`: a de um cargo de professor com outro de qualquer natureza;
- `CF88:ART.37:INC.XVI:AL.c`: a de dois cargos ou empregos privativos de profissionais de saúde, com profissões regulamentadas;
- `CF88:ART.37:INC.XVII`: a proibição de acumular estende-se a empregos e funções e abrange autarquias, fundações, empresas públicas, sociedades de economia mista, suas subsidiárias, e sociedades controladas, direta ou indiretamente, pelo poder público;

### Draft T1

**O QUE DIZ**

Em regra, é proibido acumular cargos públicos remunerados. As exceções exigem compatibilidade de horários e respeito ao teto, e são três: dois cargos de professor; um de professor com outro de qualquer natureza; dois cargos ou empregos privativos de profissionais de saúde com profissão regulamentada. O inciso XVII estende a proibição a empregos e funções, inclusive na administração indireta.

**O QUE SIGNIFICA**

A regra geral é um vínculo público remunerado por pessoa. A acumulação só é permitida nas três hipóteses das alíneas, e mesmo assim com duas condições: os horários precisam ser compatíveis, e a soma das remunerações se submete ao teto do inciso XI.

As hipóteses protegem áreas em que a Constituição quis aproveitar o profissional em mais de um vínculo: o magistério e a saúde.

O inciso XVII amplia o alcance da proibição. Ela não se limita a cargos: vale para empregos e funções e alcança toda a administração indireta, incluídas as estatais, as suas subsidiárias e as sociedades que o poder público controla direta ou indiretamente.

**EXEMPLO PRÁTICO**

Uma enfermeira concursada de um hospital estadual é aprovada para emprego de enfermeira em empresa pública federal de saúde. Como são duas ocupações privativas de profissional de saúde, a acumulação é possível se os plantões forem compatíveis. Já um técnico administrativo de uma prefeitura não pode assumir, ao mesmo tempo, emprego em sociedade de economia mista estadual, porque a proibição alcança também a administração indireta.

**ATENÇÃO**

A proibição é de acumulação remunerada, e as exceções dependem das duas condições: horários compatíveis e teto. Na alínea "b", a redação vigente, dada pela Emenda Constitucional nº 138, de 2025, admite o cargo de professor com outro de qualquer natureza; materiais mais antigos falam em cargo técnico ou científico. A acumulação de aposentadoria com remuneração tem regra própria no § 10.

**PALAVRAS DIFÍCEIS**

- *Acumulação*: exercício simultâneo de mais de um cargo, emprego ou função pública.
- *Compatibilidade de horários*: possibilidade real de cumprir as jornadas dos dois vínculos sem sobreposição.
- *Profissão regulamentada*: profissão cujo exercício é disciplinado por lei, como medicina e enfermagem.

**CAMADA EXTERNA (external_layer_notes)**

- Critérios de compatibilidade de horários são tema da camada JURISPRUDÊNCIA. A redação da alínea "b" (cargo de professor com outro de qualquer natureza) é a do texto operacional vigente, dada pela Emenda Constitucional nº 138/2025 segundo a fonte estrutural canônica do projeto.

### Avisos (editorial_checks e lint do motor)

- lint · NEAR_COPY_OF_OFFICIAL_TEXT (o_que_diz: cargos ou empregos privativos de profissionais de saúde)

### Vigência / redação (registro existente no projeto)

- EC 138/2025: "um cargo de professor com outro de qualquer natureza" (antes: tecnico ou cientifico; fonte estrutural canonica)
- EC 34/2001 (profissionais de saude com profissoes regulamentadas)

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 3. Art. 37, § 4º — Improbidade administrativa

- **target_id:** `CF88:ART.37:PAR.4`
- **explanation_id:** `ENTENDA/CF88:ART.37:PAR.4/BASE/1`
- **tipo:** DEVICE (PARAGRAFO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.37`
- **risco:** HIGH — improbidade: sancoes, reserva de lei, independencia da esfera penal
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.37:PAR.4`: Os atos de improbidade administrativa importarão a suspensão dos direitos políticos, a perda da função pública, a indisponibilidade dos bens e o ressarcimento ao erário, na forma e gradação previstas em lei, sem prejuízo da ação penal cabível.

### Draft T1

**O QUE DIZ**

O parágrafo prevê as consequências dos atos de improbidade administrativa: suspensão dos direitos políticos, perda da função pública, indisponibilidade dos bens e ressarcimento ao erário. A forma e a gradação dessas medidas ficam para a lei, e a responsabilização não impede a ação penal cabível.

**O QUE SIGNIFICA**

Improbidade é a conduta desonesta ou gravemente desleal de quem exerce função pública, como enriquecer ilicitamente, causar prejuízo aos cofres públicos ou violar deveres de honestidade.

O parágrafo lista medidas de natureza diferente. A suspensão dos direitos políticos e a perda da função são sanções. O ressarcimento repara o dano ao patrimônio público. A indisponibilidade dos bens serve para garantir que haverá patrimônio para ressarcir.

A expressão "sem prejuízo da ação penal" indica que a responsabilização por improbidade é independente da criminal: a mesma conduta pode gerar os dois processos.

**EXEMPLO PRÁTICO**

Um servidor municipal recebe dinheiro de uma empresa para favorecê-la em contratos. Ele pode responder por improbidade, com perda da função, suspensão dos direitos políticos e ressarcimento, conforme a lei. Ao mesmo tempo, pode ser processado criminalmente pelo crime cometido.

**ATENÇÃO**

O parágrafo não define quais condutas são improbidade nem fixa prazos ou graduações: tudo isso está na lei. A suspensão dos direitos políticos aqui prevista dialoga com o art. 15, V.

**PALAVRAS DIFÍCEIS**

- *Improbidade administrativa*: ato desonesto ou gravemente contrário aos deveres de quem exerce função pública, definido em lei.
- *Erário*: patrimônio financeiro do poder público; os cofres públicos.
- *Indisponibilidade dos bens*: bloqueio que impede vender ou transferir bens, para garantir o ressarcimento.

**CAMADA EXTERNA (external_layer_notes)**

- A lei de improbidade, suas sucessivas alterações e a exigência de dolo para a responsabilização são temas da camada de leis correlatas e da camada JURISPRUDÊNCIA.

### Avisos (editorial_checks e lint do motor)

- nenhum

### Vigência / redação (registro existente no projeto)

- nenhuma observação específica registrada

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 4. Art. 37, § 5º — Prescrição de ilícitos contra o erário

- **target_id:** `CF88:ART.37:PAR.5`
- **explanation_id:** `ENTENDA/CF88:ART.37:PAR.5/BASE/1`
- **tipo:** DEVICE (PARAGRAFO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.37`
- **risco:** HIGH — prescricao e ressalva das acoes de ressarcimento: redacao controvertida; nao afirmar imprescritibilidade geral
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.37:PAR.5`: A lei estabelecerá os prazos de prescrição para ilícitos praticados por qualquer agente, servidor ou não, que causem prejuízos ao erário, ressalvadas as respectivas ações de ressarcimento.

### Draft T1

**O QUE DIZ**

O parágrafo manda a lei fixar os prazos de prescrição para ilícitos que causem prejuízo ao erário, praticados por qualquer agente, servidor ou não. Ao final, ressalva as ações de ressarcimento correspondentes.

**O QUE SIGNIFICA**

Prescrição é a perda, pelo passar do tempo, da possibilidade de punir ou de cobrar. O parágrafo diz que os prazos para punir quem causa prejuízo aos cofres públicos são definidos em lei, e não pela Constituição.

A regra alcança qualquer agente, inclusive particulares que causem dano ao erário, e não só servidores.

A parte final separa a punição do ressarcimento. A punição segue os prazos da lei. Já o alcance exato da ressalva sobre as ações de ressarcimento, isto é, em que casos a cobrança do prejuízo pode ser feita a qualquer tempo, não está detalhado no texto e depende de interpretação.

**EXEMPLO PRÁTICO**

Um servidor desvia recursos de um programa público. Os prazos para aplicar-lhe as sanções estão fixados em lei. A possibilidade de, depois desses prazos, ainda cobrar a devolução do valor desviado é exatamente o ponto que a ressalva final do parágrafo deixa em aberto para a interpretação.

**ATENÇÃO**

Não se deve ler o parágrafo como se tornasse imprescritível toda e qualquer cobrança de dano ao erário. O texto apenas ressalva as ações de ressarcimento; o alcance dessa ressalva é definido fora da letra do parágrafo.

**PALAVRAS DIFÍCEIS**

- *Prescrição*: perda, pelo decurso do tempo, da possibilidade de punir ou de exigir um direito em juízo.
- *Ressarcimento*: devolução do valor do prejuízo causado.
- *Imprescritível*: que pode ser exigido a qualquer tempo, sem prazo final.
- *Erário*: patrimônio financeiro do poder público; os cofres públicos.

**CAMADA EXTERNA (external_layer_notes)**

- Quais ações de ressarcimento ao erário são imprescritíveis é questão definida pela camada JURISPRUDÊNCIA; o parágrafo não a resolve em sua literalidade.

### Avisos (editorial_checks e lint do motor)

- nenhum

### Vigência / redação (registro existente no projeto)

- nenhuma observação específica registrada

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 5. Art. 37, §§ 9º, 11 e 12 — Teto: estatais dependentes, parcelas indenizatórias e subteto único

- **target_id:** `CF88:ART.37:PAR.9`
- **explanation_id:** `ENTENDA/CF88:ART.37:PAR.9/BASE/1`
- **tipo:** BLOCK (PARAGRAFO)
- **targets cobertos:** `CF88:ART.37:PAR.11`, `CF88:ART.37:PAR.12`
- **contexto estrutural:** `CF88:ART.37`
- **risco:** HIGH — teto: estatais dependentes, parcelas indenizatorias (remissao a EC 135/2024) e subteto unico facultativo
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.37:PAR.9`: O disposto no inciso XI aplica-se às empresas públicas e às sociedades de economia mista e suas subsidiárias, que receberem recursos da União, dos Estados, do Distrito Federal ou dos Municípios para pagamento de despesas de pessoal ou de custeio em geral.
- `CF88:ART.37:PAR.11`: Não serão computadas, para efeito dos limites remuneratórios de que trata o inciso XI do caput deste artigo, as parcelas de caráter indenizatório expressamente previstas em lei ordinária, aprovada pelo Congresso Nacional, de caráter nacional, aplicada a todos os Poderes e órgãos constitucionalmente autônomos. ( Vide o art. 3º da Emenda Constitucional nº 135/2024 )
- `CF88:ART.37:PAR.12`: Para os fins do disposto no inciso XI do caput deste artigo, fica facultado aos Estados e ao Distrito Federal fixar, em seu âmbito, mediante emenda às respectivas Constituições e Lei Orgânica, como limite único, o subsídio mensal dos Desembargadores do respectivo Tribunal de Justiça, limitado a noventa inteiros e vinte e cinco centésimos por cento do subsídio mensal dos Ministros do Supremo Tribunal Federal, não se aplicando o disposto neste parágrafo aos subsídios dos Deputados Estaduais e Distritais e dos Vereadores.

### Draft T1

**O QUE DIZ**

O § 9º aplica o teto às empresas públicas, sociedades de economia mista e subsidiárias que recebem recursos públicos para pagar pessoal ou custeio. O § 11 exclui do teto as parcelas indenizatórias previstas expressamente em lei ordinária nacional, aprovada pelo Congresso. O § 12 permite que Estados e Distrito Federal adotem como limite único o subsídio dos Desembargadores do Tribunal de Justiça.

**O QUE SIGNIFICA**

Os três parágrafos ajustam o alcance do teto do inciso XI.

O § 9º trata das estatais. Em regra, elas não estão no texto do inciso XI, que fala da administração direta, autárquica e fundacional. Mas, se dependem de dinheiro público para pagar salários ou despesas correntes, passam a se submeter ao teto.

O § 11 tira do teto as parcelas indenizatórias, que reembolsam gastos e não remuneram o trabalho. A exclusão só vale para as parcelas previstas expressamente em lei ordinária de alcance nacional, válida para todos os Poderes e órgãos autônomos.

O § 12 é uma opção dos Estados e do Distrito Federal: por emenda à Constituição estadual ou à Lei Orgânica, podem adotar um subteto único, limitado a 90,25% do subsídio dos Ministros do Supremo. A opção não alcança Deputados Estaduais e Distritais nem Vereadores.

**EXEMPLO PRÁTICO**

Uma companhia estadual de transportes que depende de repasses do Estado para pagar a folha passa a observar o teto (§ 9º). Uma diária paga a um servidor para cobrir hospedagem em viagem de trabalho, se prevista na lei nacional exigida pelo § 11, não entra na conta do teto.

**ATENÇÃO**

O texto oficial do § 11 traz remissão ao art. 3º da Emenda Constitucional nº 135/2024, que trata da aplicação dessa regra. O conteúdo dessa disposição está fora do art. 37 e deve ser consultado na emenda. Estatais que não recebem recursos públicos para pessoal ou custeio não estão alcançadas pelo § 9º.

**PALAVRAS DIFÍCEIS**

- *Estatal dependente*: empresa do poder público que precisa de repasses do Tesouro para pagar pessoal ou custeio.
- *Parcela indenizatória*: valor pago para reembolsar despesa do servidor, e não para remunerar o seu trabalho.
- *Custeio*: despesas correntes de manutenção, como contas, materiais e serviços.
- *Subsídio*: remuneração fixada em parcela única, sem acréscimos de outras espécies remuneratórias (art. 39, § 4º).
- *Sociedade de economia mista*: empresa com capital público e privado, controlada pelo poder público.

**CAMADA EXTERNA (external_layer_notes)**

- A situação da lei nacional de parcelas indenizatórias exigida pelo § 11 e as regras do art. 3º da Emenda Constitucional nº 135/2024 devem ser verificadas em fonte oficial atualizada (camada externa).

### Avisos (editorial_checks e lint do motor)

- editorial_checks · EXTRAPOLATION_NUMBER (o_que_significa: 90,25%) → resolução registrada: equivalente numerico de "noventa inteiros e vinte e cinco centesimos por cento" do § 12.
- lint · LONG_EXPLANATION (*: 368 palavras (limite 400))

### Vigência / redação (registro existente no projeto)

- texto oficial traz "( Vide o art. 3º da Emenda Constitucional nº 135/2024 )"; conteudo da EC fora do art. 37 (ATENCAO + camada externa)

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 6. Art. 37, § 14 — Aposentadoria e rompimento do vínculo

- **target_id:** `CF88:ART.37:PAR.14`
- **explanation_id:** `ENTENDA/CF88:ART.37:PAR.14/BASE/1`
- **tipo:** DEVICE (PARAGRAFO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.37`
- **risco:** HIGH — previdencia: rompimento do vinculo (EC 103/2019); transicao fora do texto
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.37:PAR.14`: A aposentadoria concedida com a utilização de tempo de contribuição decorrente de cargo, emprego ou função pública, inclusive do Regime Geral de Previdência Social, acarretará o rompimento do vínculo que gerou o referido tempo de contribuição.

### Draft T1

**O QUE DIZ**

O parágrafo determina que a aposentadoria concedida com o uso de tempo de contribuição de cargo, emprego ou função pública rompe o vínculo que gerou esse tempo, inclusive quando a aposentadoria é do Regime Geral.

**O QUE SIGNIFICA**

A regra impede que a pessoa se aposente usando o tempo de um vínculo público e continue nesse mesmo vínculo, recebendo ao mesmo tempo a aposentadoria e a remuneração.

O ponto central é a origem do tempo de contribuição. Se a aposentadoria usou o tempo de um cargo, emprego ou função pública, esse vínculo termina. A menção expressa ao Regime Geral alcança, por exemplo, o empregado público que se aposenta pelo regime geral usando o tempo do seu emprego.

**EXEMPLO PRÁTICO**

Um empregado de uma empresa pública, vinculado ao Regime Geral, se aposenta contando o tempo de contribuição desse emprego. Pelo texto do parágrafo, a aposentadoria rompe o vínculo de emprego com a empresa pública.

**ATENÇÃO**

O parágrafo foi incluído pela reforma da previdência de 2019. A aplicação a aposentadorias concedidas antes da sua vigência depende de regras de transição da própria emenda, que não estão neste parágrafo.

**PALAVRAS DIFÍCEIS**

- *Tempo de contribuição*: período em que a pessoa contribuiu para um regime de previdência.
- *Regime Geral de Previdência Social*: sistema previdenciário administrado pelo INSS, que abrange os trabalhadores em geral.
- *Rompimento do vínculo*: término da relação de trabalho do agente com a administração.

**CAMADA EXTERNA (external_layer_notes)**

- As regras de transição da Emenda Constitucional nº 103/2019 sobre este parágrafo devem ser consultadas na própria emenda (camada externa).

### Avisos (editorial_checks e lint do motor)

- nenhum

### Vigência / redação (registro existente no projeto)

- Incluidos pela EC 103/2019 (fonte estrutural canonica)

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

## 7. Art. 37, § 15 — Vedação de complementação de aposentadorias e pensões

- **target_id:** `CF88:ART.37:PAR.15`
- **explanation_id:** `ENTENDA/CF88:ART.37:PAR.15/BASE/1`
- **tipo:** DEVICE (PARAGRAFO)
- **targets cobertos:** — (sem cobertura de irmãos)
- **contexto estrutural:** `CF88:ART.37`
- **risco:** HIGH — previdencia: vedacao de complementacao com duas excecoes (EC 103/2019)
- **status:** PENDING_HUMAN_REVIEW · READY_FOR_EDITORIAL_REVIEW

### Lei Seca (texto oficial vigente)

- `CF88:ART.37:PAR.15`: É vedada a complementação de aposentadorias de servidores públicos e de pensões por morte a seus dependentes que não seja decorrente do disposto nos §§ 14 a 16 do art. 40 ou que não seja prevista em lei que extinga regime próprio de previdência social.

### Draft T1

**O QUE DIZ**

O parágrafo proíbe complementar aposentadorias de servidores públicos e pensões por morte de seus dependentes. Há duas exceções: a complementação que decorre do regime de previdência complementar do art. 40, §§ 14 a 16, e a prevista em lei que extinga regime próprio de previdência.

**O QUE SIGNIFICA**

Complementação é um pagamento extra, feito pelo ente público, para aumentar o valor de uma aposentadoria ou pensão. O parágrafo impede que o ente crie esses acréscimos por conta própria.

Ficam permitidas apenas duas formas. A primeira é a previdência complementar dos servidores, organizada nos termos do art. 40, baseada em contribuições. A segunda é a complementação prevista na lei que extingue um regime próprio, caso em que os servidores daquele ente passam para o Regime Geral.

**EXEMPLO PRÁTICO**

Um Município aprova lei para pagar, com recursos do Tesouro, um valor adicional às pensões de dependentes de servidores falecidos, fora de qualquer plano de previdência complementar. Essa lei contraria o parágrafo.

**ATENÇÃO**

O parágrafo foi incluído pela reforma da previdência de 2019. A situação das complementações já existentes antes dela depende das regras de transição da emenda, que não estão escritas aqui.

**PALAVRAS DIFÍCEIS**

- *Complementação*: pagamento adicional que aumenta o valor de uma aposentadoria ou pensão.
- *Pensão por morte*: benefício pago aos dependentes de quem faleceu.
- *Regime próprio de previdência social*: sistema previdenciário dos servidores titulares de cargo efetivo de cada ente.

**CAMADA EXTERNA (external_layer_notes)**

- As regras de transição da Emenda Constitucional nº 103/2019 sobre complementações pré-existentes devem ser consultadas na própria emenda.

### Avisos (editorial_checks e lint do motor)

- lint · NEAR_COPY_OF_OFFICIAL_TEXT (o_que_diz: em lei que extinga regime próprio de previdência)

### Vigência / redação (registro existente no projeto)

- Incluidos pela EC 103/2019 (fonte estrutural canonica)

### Decisão

- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR

---

