# T1 — CALIBRAÇÃO HUMANA DA TRIAGEM (Batch05, 31 pendentes)

`T1_VALIDATOR_V2 (A6, 2026-10-04)` · 2026-10-04 · nada alterado: textos, status e versões intactos; autoaprovação OFF (LOW e MEDIUM). Objetivo: decidir se o roteamento A/B/C/D está correto. Não é aprovação.

**Como responder:** por item, `CONFIRMAR` a fila ou `RECLASSIFICAR → <fila>` (com motivo curto). Na fila D, só confirmar se o roteamento está certo; a correção virá depois.

**Classificação do validador na fila C** (regras determinísticas, a calibrar com a sua resposta):
- PROVÁVEL FALSO POSITIVO: o mesmo termo já está justificado no editorial_checks, ou o quantificador está num exemplo que reproduz a Lei Seca;
- PROVÁVEL PROBLEMA: mesmo padrão já corrigido nas rodadas (finalidade, consequência automática, condição inexistente, permissão sobre garantia);
- INDETERMINADO: o restante.

## A — CLEAN_LOW (5)

### `CF88:ART.37:INC.VIII` — Art. 37, inciso VIII — Reserva de vagas para pessoas com deficiência

- risco LOW · ITEM · seleção: Acao afirmativa com comando proprio ao legislador (percentual e criterios de admissao).
- **O QUE DIZ:** No conjunto de regras do art. 37, este inciso manda a lei reservar uma parte dos cargos e empregos públicos para pessoas com deficiência e definir os critérios de admissão desses candidatos.
- **O QUE SIGNIFICA:** É uma ação afirmativa: uma medida que busca igualdade real, compensando barreiras enfrentadas por um grupo. A Constituição não fixa o percentual; ela obriga o legislador a fixá-lo e a definir como esses candidatos serão admitidos. / A reserva não dispensa o concurso. O candidato com deficiência participa do concurso e concorre às vagas reservadas, segundo os critérios previstos em lei e no edital. A deficiência deve ser compatível com as atribuições do cargo. / O texto oficial usa a expressão "pessoas portadoras de deficiência", da época da redação. Hoje se usa a expressão "pessoa com deficiência".
- **EXEMPLO:** Um concurso estadual oferece 100 vagas e, conforme a lei estadual, reserva parte delas a candidatos com deficiência. Uma candidata cega concorre nessas vagas para um cargo administrativo e realiza a prova com os recursos de acessibilidade previstos no edital.
- **ATENÇÃO:** O inciso não fixa número nem percentual: isso cabe à lei de cada ente. A reserva convive com o concurso e não o substitui.
- **Camada externa:** Percentuais e critérios de admissão vigentes estão na legislação infraconstitucional (camada de leis correlatas).
- **Checks:** nenhum · **v2:** sem HARD_FAIL/REVIEW (INFO: —)
- **Por que A:** LOW, nenhum alerta jurídico/editorial pendente. [ ] CONFIRMAR   [ ] RECLASSIFICAR → ____

### `CF88:ART.37:PAR.1` — Art. 37, § 1º — Publicidade institucional sem promoção pessoal

- risco LOW · DEVICE · seleção: Paragrafo autonomo de alta utilidade pratica: finalidade da publicidade oficial e vedacao de promocao pessoal.
- **O QUE DIZ:** O parágrafo define a finalidade da publicidade dos órgãos públicos: ela deve educar, informar ou orientar a sociedade. Proíbe que essa publicidade traga nomes, símbolos ou imagens que funcionem como propaganda pessoal de autoridades ou de servidores.
- **O QUE SIGNIFICA:** A comunicação oficial, chamada publicidade institucional, pertence à instituição, não ao governante. Ela é paga com recursos públicos e deve servir ao cidadão: informar um serviço, explicar uma política, orientar sobre saúde ou segurança. / O parágrafo concretiza a impessoalidade. Ele proíbe usar a publicidade para construir a imagem pessoal de quem está no poder. A proibição alcança nomes, fotografias e também símbolos, slogans ou marcas que identifiquem a pessoa da autoridade e não o órgão.
- **EXEMPLO:** Uma campanha estadual de vacinação informa datas, locais e públicos-alvo. Essa é publicidade informativa e de orientação social. Se a mesma campanha estampar a foto do governador e o slogan pessoal da sua gestão, passa a caracterizar promoção pessoal, vedada pelo parágrafo.
- **ATENÇÃO:** O parágrafo não proíbe informar quais órgãos realizaram uma obra ou serviço. O que ele veda é a personalização: elementos que promovam a autoridade ou o servidor.
- **Camada externa:** As consequências do uso indevido de publicidade oficial (por exemplo, na esfera eleitoral ou de improbidade) estão em leis correlatas e na camada JURISPRUDÊNCIA.
- **Checks:** nenhum · **v2:** sem HARD_FAIL/REVIEW (INFO: —)
- **Por que A:** LOW, nenhum alerta jurídico/editorial pendente. [ ] CONFIRMAR   [ ] RECLASSIFICAR → ____

### `CF88:ART.37:PAR.16` — Art. 37, § 16 — Avaliação de políticas públicas

- risco LOW · DEVICE · seleção: Dever autonomo de avaliacao de politicas publicas com transparencia (objeto e resultados).
- **O QUE DIZ:** O parágrafo determina que órgãos e entidades da administração, sozinhos ou em conjunto, avaliem as políticas públicas, divulgando o que será avaliado e os resultados obtidos, na forma da lei.
- **O QUE SIGNIFICA:** Uma política pública é um conjunto de ações do governo para enfrentar um problema coletivo, como um programa de alfabetização ou de vacinação. Avaliá-la é verificar se ela funciona: se alcança os objetivos, a que custo e com quais efeitos. / O parágrafo liga a avaliação à transparência: a sociedade deve saber o que está sendo avaliado e quais foram os resultados. Isso concretiza a eficiência e a publicidade do caput e ajuda a decidir se uma política deve continuar, mudar ou terminar.
- **EXEMPLO:** Um Estado mantém um programa de transferência de renda para estudantes. Os órgãos responsáveis avaliam se o programa reduziu a evasão escolar e publicam o objeto da avaliação e os resultados, para que a população e o Legislativo acompanhem.
- **ATENÇÃO:** A forma da avaliação depende de lei. O parágrafo admite avaliação individual ou conjunta entre órgãos e entidades.
- **Camada externa:** —
- **Checks:** nenhum · **v2:** sem HARD_FAIL/REVIEW (INFO: —)
- **Por que A:** LOW, nenhum alerta jurídico/editorial pendente. [ ] CONFIRMAR   [ ] RECLASSIFICAR → ____

### `CF88:ART.37:PAR.3` — Art. 37, § 3º — Participação do usuário de serviço público

- risco LOW · BLOCK · seleção: Paragrafo-bloco com enunciado e tres incisos sobre participacao do usuario: reclamacoes, acesso a informacoes e representacao.
- **O QUE DIZ:** O parágrafo manda a lei disciplinar como o usuário participa da administração pública direta e indireta. Destaca três temas: reclamações sobre os serviços, com atendimento ao usuário e avaliação periódica; acesso a registros administrativos e informações sobre atos de governo; e representação contra quem exerce cargo, emprego ou função com negligência ou abuso.
- **O QUE SIGNIFICA:** O usuário não é só destinatário do serviço público: ele também ajuda a controlá-lo. O parágrafo cria três canais. / O primeiro é a reclamação, com serviços de atendimento e avaliação da qualidade, feita de dentro e de fora da administração. / O segundo é o acesso a informações e registros. Ele observa a proteção da intimidade e as hipóteses de sigilo previstas no art. 5º, X e XXXIII. / O terceiro é a representação: o usuário pode comunicar formalmente condutas negligentes ou abusivas de agentes públicos, para que sejam apuradas.
- **EXEMPLO:** Um cidadão registra na ouvidoria de uma autarquia uma reclamação sobre a demora no atendimento, pede cópia de documentos sobre um programa de governo e, depois, apresenta representação contra um servidor que o tratou com abuso. Os três canais estão previstos neste parágrafo e na lei que o regula.
- **ATENÇÃO:** O parágrafo depende de lei para ser aplicado. O acesso a informações não é ilimitado: o próprio texto ressalva a intimidade e o sigilo necessário à segurança da sociedade e do Estado.
- **Camada externa:** As leis de defesa do usuário de serviços públicos e de acesso à informação estão na camada de leis correlatas.
- **Checks:** nenhum · **v2:** sem HARD_FAIL/REVIEW (INFO: —)
- **Por que A:** LOW, nenhum alerta jurídico/editorial pendente. [ ] CONFIRMAR   [ ] RECLASSIFICAR → ____

### `CF88:ART.37:PAR.8` — Art. 37, § 8º — Contrato de desempenho e autonomia ampliada

- risco LOW · BLOCK · seleção: Paragrafo-bloco com enunciado (ampliacao de autonomia por contrato com metas) e tres incisos sobre o conteudo da lei.
- **O QUE DIZ:** O parágrafo permite ampliar a autonomia gerencial, orçamentária e financeira de órgãos e entidades por meio de contrato com o poder público, que fixa metas de desempenho. A lei deve tratar do prazo do contrato, dos controles e critérios de avaliação, dos direitos e responsabilidades dos dirigentes e da remuneração do pessoal.
- **O QUE SIGNIFICA:** É um instrumento ligado ao princípio da eficiência. O órgão ou entidade assume metas e, em troca, ganha mais liberdade para administrar pessoal, orçamento e finanças. / O contrato é firmado entre os administradores do órgão ou entidade e o poder público. Por isso ele costuma ser chamado de contrato de gestão ou contrato de desempenho. / Os incisos indicam o que a lei deve regular: quanto tempo dura o contrato, como o desempenho será medido e controlado, quais os deveres e responsabilidades dos dirigentes e como fica a remuneração dos servidores envolvidos.
- **EXEMPLO:** Um hospital público estadual assina com a Secretaria de Saúde um contrato com metas de redução das filas de cirurgia. Em troca, ganha mais flexibilidade para gerir seus recursos, dentro do que a lei permitir. Se não cumprir as metas, os dirigentes respondem conforme as regras de responsabilidade previstas.
- **ATENÇÃO:** A ampliação da autonomia depende do contrato e da lei; ela não acontece por decisão unilateral do órgão. O parágrafo usa "poderá": é uma possibilidade, não uma obrigação.
- **Camada externa:** —
- **Checks:** MODALITY_SHIFT(resolvido) · **v2:** sem HARD_FAIL/REVIEW (INFO: EDITORIAL_CHECK_RESOLVED)
- **Por que A:** LOW, nenhum alerta jurídico/editorial pendente. [ ] CONFIRMAR   [ ] RECLASSIFICAR → ____

## B — CLEAN_MEDIUM (15)

**`CF88:ART.37:INC.I` — Art. 37, inciso I — Acesso a cargos, empregos e funções**

- Ponto central: Este inciso, uma das regras que o caput do art. 37 anuncia, abre o acesso aos cargos, empregos e funções públicas aos brasileiros que cumpram os requisitos fixados em…
- Interpretação: O ponto de partida é a ampla acessibilidade: o serviço público não é reservado a grupos fechados.
- Exemplo: Uma lei estadual exige diploma de engenharia para o cargo de engenheiro do Estado. · ATENÇÃO: Os requisitos para o cargo devem estar previstos em lei.
- Dep. externa: NO · checks: ABSOLUTE_CLAIM, EXAMPLE_REQUIREMENT_LANGUAGE×2, ABSOLUTE_CLAIM(resolvido) · v2: limpo
- Parágrafo(s) com termo sensível:
  - ATENÇÃO [está no]: "Os requisitos para o cargo devem estar previstos em lei. Um edital, sozinho, não pode criar exigências que a lei não prevê. O inciso trata de quem pode ter acesso; a forma de entrar, em regra por concurso, está no inciso II."
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.III` — Art. 37, incisos III e IV — Validade do concurso e prioridade do aprovado**

- Ponto central: O inciso III fixa a validade do concurso em até dois anos, prorrogável uma única vez por igual período.
- Interpretação: Os dois incisos tratam do tempo em que o resultado do concurso pode ser aproveitado.
- Exemplo: Um edital fixa a validade do concurso em um ano. · ATENÇÃO: A prorrogação não pode ser maior que o prazo inicial, nem acontecer duas vezes.
- Dep. externa: NO · checks: EXAMPLE_REQUIREMENT_LANGUAGE · v2: limpo
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.IX` — Art. 37, inciso IX — Contratação por tempo determinado**

- Ponto central: Dentro das regras do art. 37, este inciso atribui à lei a definição dos casos em que a administração pode contratar pessoal por tempo determinado.
- Interpretação: É uma forma de contratação sem concurso, admitida apenas em situações passageiras e excepcionais.
- Exemplo: Durante uma epidemia, um município contrata, por seis meses, profissionais de saúde para reforçar o… · ATENÇÃO: Contratações temporárias renovadas por anos seguidos para atividades permanentes desvirtuam o inciso e…
- Dep. externa: NO · checks: nenhum · v2: limpo
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.V` — Art. 37, inciso V — Funções de confiança e cargos em comissão**

- Ponto central: Entre as regras do art. 37, este inciso diferencia funções de confiança e cargos em comissão.
- Interpretação: A função de confiança é um conjunto de atribuições extras dado a um servidor efetivo, que continua no seu cargo e recebe uma gratificação pela…
- Exemplo: Um analista efetivo de um tribunal é designado chefe de seção e passa a receber uma gratificação: é… · ATENÇÃO: Função de confiança é exclusiva de servidor efetivo; cargo em comissão admite pessoa sem vínculo, respeitado…
- Dep. externa: NO · checks: nenhum · v2: limpo
- Parágrafo(s) com termo sensível:
  - EXEMPLO [tribunal]: "Um analista efetivo de um tribunal é designado chefe de seção e passa a receber uma gratificação: é uma função de confiança. Já o assessor jurídico de um secretário, nomeado sem concurso, ocupa cargo em comissão. Uma lei que criasse cargos em comissão de digitador seria incompatível com o inciso, porque essa atividade não é de direção, chefia ou assessoramento."
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.VI` — Art. 37, incisos VI e VII — Sindicalização e greve do servidor civil**

- Ponto central: O inciso VI assegura ao servidor público civil o direito de se associar livremente a sindicatos.
- Interpretação: Os dois incisos tratam dos direitos coletivos do servidor civil.
- Exemplo: Servidores de uma agência estadual fundam um sindicato e decidem, em assembleia, paralisar as… · ATENÇÃO: Direito de greve não é direito sem limites: o próprio inciso VII manda observar os limites da lei.
- Dep. externa: NO · checks: EXAMPLE_REQUIREMENT_LANGUAGE · v2: limpo
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.XIX` — Art. 37, incisos XIX e XX — Criação de entidades da administração indireta**

- Ponto central: O inciso XIX exige lei específica para criar autarquia e para autorizar a instituição de empresa pública, sociedade de economia mista e fundação; para as fundações, lei…
- Interpretação: Há uma diferença importante de verbos.
- Exemplo: Um Estado quer criar uma companhia de saneamento como sociedade de economia mista. · ATENÇÃO: O inciso XX fala em autorização legislativa "em cada caso".
- Dep. externa: NO · checks: EXAMPLE_REQUIREMENT_LANGUAGE · v2: limpo
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.XV` — Art. 37, inciso XV — Irredutibilidade de subsídio e vencimentos**

- Ponto central: Entre as regras do art. 37, este inciso torna irredutíveis o subsídio e os vencimentos de quem ocupa cargo ou emprego público.
- Interpretação: Irredutibilidade significa que o valor nominal pago pelo cargo não pode ser diminuído por ato do poder público.
- Exemplo: Uma lei estadual reduz em 10% o vencimento básico de um cargo, sem relação com o teto. · ATENÇÃO: A garantia protege o valor nominal.
- Dep. externa: NO · checks: EXAMPLE_NUMBER(resolvido) · v2: limpo
- Parágrafo(s) com termo sensível:
  - O QUE DIZ [teto]: "Entre as regras do art. 37, este inciso torna irredutíveis o subsídio e os vencimentos de quem ocupa cargo ou emprego público. A garantia tem ressalvas expressas: o teto (inciso XI), a vedação do efeito cascata (inciso XIV), o subsídio em parcela única (art. 39, § 4º) e regras tributárias, como o imposto de renda."
  - O QUE SIGNIFICA [teto]: "Mas ela não é ilimitada. Os valores que ultrapassam o teto podem ser cortados; acréscimos calculados em cascata podem ser ajustados; e a incidência de tributos, como o imposto de renda, não é tratada como redução proibida. As remissões aos arts. 150, II, e 153 confirmam que o servidor paga impostos como os demais contribuintes."
  - EXEMPLO [teto]: "Uma lei estadual reduz em 10% o vencimento básico de um cargo, sem relação com o teto. Essa redução contraria o inciso XV. Já o corte da parte da remuneração que excede o teto do inciso XI não viola a irredutibilidade, porque é uma das ressalvas do próprio texto."
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.XXI` — Art. 37, inciso XXI — Licitação**

- Ponto central: No conjunto do art. 37, este inciso exige licitação pública para contratar obras, serviços, compras e alienações, salvo nos casos previstos na legislação.
- Interpretação: Licitação é o procedimento para escolher, com igualdade e transparência, quem vai contratar com a administração.
- Exemplo: Um município vai comprar merenda escolar e faz licitação. · ATENÇÃO: A regra é licitar; as exceções dependem de previsão legal e não da conveniência do administrador.
- Dep. externa: NO · checks: EXAMPLE_REQUIREMENT_LANGUAGE · v2: limpo
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:PAR.2` — Art. 37, § 2º — Nulidade por desrespeito ao concurso**

- Ponto central: O parágrafo fixa as consequências de desrespeitar os incisos II e III, isto é, a exigência de concurso e o prazo de validade do concurso: o ato é nulo e a autoridade…
- Interpretação: São duas consequências diferentes.
- Exemplo: Um prefeito contrata dezenas de pessoas para cargos efetivos sem concurso. · ATENÇÃO: O parágrafo remete à lei a forma de punição.
- Dep. externa: NO · checks: nenhum · v2: limpo
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.38` — Art. 38 — Servidor público no exercício de mandato eletivo**

- Ponto central: O art. 38 regula o que acontece com o servidor público da administração direta, autárquica e fundacional quando ele assume um mandato eletivo.
- Interpretação: O artigo resolve um conflito prático: a mesma pessoa passa a ter dois vínculos com o poder público, o cargo de servidor e o mandato.
- Exemplo: Uma professora efetiva da rede estadual é eleita deputada estadual. · ATENÇÃO: O art. 38 não trata de quem pode se candidatar nem de prazos de desincompatibilização antes da eleição.
- Dep. externa: NO · checks: NEAR_COPY_OF_OFFICIAL_TEXT, TECHNICAL_TERM_UNDEFINED(resolvido) · v2: limpo
- Microajuste proposto (não aplicado): o_que_diz: "ce com o servidor público da administração direta, aut" → "ce com o servidor público de administração direta, aut"
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.38:INC.I` — Art. 38, inciso I — Mandato federal, estadual ou distrital**

- Ponto central: Para o servidor que assume mandato federal, estadual ou distrital, este inciso do art. 38 determina o afastamento do cargo, emprego ou função durante o mandato.
- Interpretação: Mandatos federais são os de Deputado Federal e Senador.
- Exemplo: Um analista do Tesouro Nacional é eleito deputado federal. · ATENÇÃO: A possibilidade de optar pela remuneração do cargo existe para o Prefeito e, em certos casos, para o Vereador.
- Dep. externa: NO · checks: nenhum · v2: limpo
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.38:INC.IV` — Art. 38, inciso IV — Tempo de serviço durante o mandato**

- Ponto central: Dentro do art. 38, este inciso determina que, nos casos em que o mandato exige afastamento, o tempo de serviço do servidor afastado é contado para todos os efeitos…
- Interpretação: O servidor afastado para exercer mandato não perde tempo de carreira.
- Exemplo: Um servidor fica oito anos afastado como deputado estadual. · ATENÇÃO: O inciso trata do tempo de serviço.
- Dep. externa: NO · checks: nenhum · v2: limpo
- Parágrafo(s) com termo sensível:
  - ATENÇÃO [está no]: "O inciso trata do tempo de serviço. A situação previdenciária do servidor afastado está no inciso V, e a contagem para aposentadoria depende das regras previdenciárias."
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.39:PAR.1` — Art. 39, § 1º — Critérios do sistema remuneratório**

- Ponto central: O parágrafo fixa três critérios para estabelecer os padrões de vencimento e os demais componentes da remuneração: a natureza, a responsabilidade e a complexidade dos…
- Interpretação: A remuneração não deve ser fixada de forma arbitrária.
- Exemplo: Ao reorganizar as carreiras da saúde, um Estado fixa remuneração maior para médicos do que para… · ATENÇÃO: Os critérios orientam a lei; o parágrafo não fixa valores nem garante equiparação entre cargos parecidos, que…
- Dep. externa: NO · checks: nenhum · v2: limpo
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.39:PAR.3` — Art. 39, § 3º — Direitos sociais aplicáveis aos servidores**

- Ponto central: O parágrafo estende aos servidores ocupantes de cargo público uma lista de direitos sociais do art. 7º, previstos para os trabalhadores.
- Interpretação: Os direitos estendidos são: salário mínimo e garantia de salário não inferior ao mínimo para quem tem remuneração variável; décimo terceiro;…
- Exemplo: Uma servidora estadual tem direito a férias com acréscimo de um terço e à licença à gestante,… · ATENÇÃO: A lista é fechada: só os incisos indicados do art. 7º se aplicam diretamente.
- Dep. externa: NO · checks: nenhum · v2: limpo
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

**`CF88:ART.39:PAR.5` — Art. 39, §§ 5º e 6º — Relação entre remunerações e publicação anual**

- Ponto central: O § 5º permite que lei de cada ente fixe a proporção entre a remuneração mais alta e a mais baixa dos seus servidores, respeitado o teto do art. 37, XI.
- Interpretação: O § 5º trata da diferença entre o topo e a base da folha.
- Exemplo: Uma lei municipal estabelece que a maior remuneração do quadro de servidores não pode exceder dez… · ATENÇÃO: O § 5º usa "poderá": cada ente decide se fixa essa relação.
- Dep. externa: NO · checks: MODALITY_SHIFT(resolvido) · v2: limpo
- Parágrafo(s) com termo sensível:
  - O QUE DIZ [teto]: "O § 5º permite que lei de cada ente fixe a proporção entre a remuneração mais alta e a mais baixa dos seus servidores, respeitado o teto do art. 37, XI. O § 6º obriga os três Poderes a publicar todo ano quanto pagam, como subsídio ou remuneração, em cada cargo e emprego público."
  - ATENÇÃO [teto]: "O § 5º usa "poderá": cada ente decide se fixa essa relação. O § 6º, ao contrário, é um dever de todos os Poderes. Os dois parágrafos não alteram o teto, que continua valendo."
- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____

## C — QUICK_REVIEW (9)

Reclassificar para A/B se o alerta for falso positivo; para D se houver problema jurídico.

**`CF88:ART.37:CAPUT` — Art. 37, caput — Princípios da administração pública · MEDIUM**

- **UNIVERSAL_CLAIM** (o_que_significa, gatilho "só pode"): "**o administrador público só pode agir com base em autorização da lei.**"
  - antes: …Legalidade administrativa é diferente da legalidade do particular. · depois: Impessoalidade tem duas faces: a administração não pode favorecer nem perseguir pessoas,…
  - validador: **INDETERMINADO** — quantificador/expressão no núcleo; depende da leitura do dispositivo · ação: restringir o quantificador ao alcance da Lei Seca (ou confirmar que o…
- Dep. externa: nenhuma · [ ] CONFIRMAR C   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.II` — Art. 37, inciso II — Concurso público · MEDIUM**

- **UNIVERSAL_CLAIM** (exemplo_pratico, gatilho "todos os"): "**Ela abre concurso de provas, com regras iguais para todos os candidatos.**"
  - antes: …Uma prefeitura precisa de novos agentes administrativos para cargos efetivos. · depois: Se, em vez disso, o prefeito nomeasse parentes para esses cargos efetivos sem concurso,…
  - validador: **PROVÁVEL FALSO POSITIVO** — quantificador dentro de exemplo que reproduz situação prevista na Lei Seca
- Dep. externa: nenhuma · [ ] CONFIRMAR C   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.X` — Art. 37, inciso X — Remuneração por lei e revisão geral anual · MEDIUM**

- **UNIVERSAL_CLAIM** (o_que_significa, gatilho "todos os"): "**Ela busca recompor o valor da remuneração de todos os servidores do ente, de uma só vez, na mesma data e pelo mesmo índice.**"
  - antes: …A revisão geral anual é diferente de um aumento para uma categoria. · depois: Por isso não pode haver índices diferentes para categorias diferentes nessa revisão.
  - validador: **INDETERMINADO** — quantificador/expressão no núcleo; depende da leitura do dispositivo · ação: restringir o quantificador ao alcance da Lei Seca (ou confirmar que o…
- Dep. externa: nenhuma · [ ] CONFIRMAR C   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.XII` — Art. 37, incisos XII, XIII e XIV — Limites e vedações na política remuneratória · MEDIUM**

- **UNIVERSAL_CLAIM** (exemplo_pratico, gatilho "sempre"): "**Uma lei municipal diz que o vencimento dos fiscais será sempre igual ao dos procuradores do Município.**"
  - antes: — · depois: Essa equiparação automática é proibida pelo inciso XIII.
  - validador: **INDETERMINADO** — quantificador/expressão no núcleo; depende da leitura do dispositivo · ação: restringir o quantificador ao alcance da Lei Seca (ou confirmar que o…
- **AUTOMATIC_CONSEQUENCE** (atencao, gatilho "automaticamente"): "**O que ele proíbe é a regra que faz uma acompanhar a outra automaticamente.**"
  - antes: …III não impede que duas carreiras tenham, por decisão de lei, remunerações de mesmo valor. · depois: —
  - validador: **PROVÁVEL FALSO POSITIVO** — mesmo termo já justificado no editorial_checks (ABSOLUTE_CLAIM): descreve a regra proibida…
- Dep. externa: nenhuma · [ ] CONFIRMAR C   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:INC.XVIII` — Art. 37, incisos XVIII e XXII — Administração tributária · LOW**

- **UNIVERSAL_CLAIM** (o_que_significa, gatilho "todas as"): "**Os dois incisos valorizam a atividade de arrecadar e fiscalizar tributos, porque dela depende o financiamento de todas as políticas públicas.**"
  - antes: — · depois: Precedência significa prioridade: quando a fiscalização tributária atua na sua área, ela…
  - validador: **INDETERMINADO** — quantificador/expressão no núcleo; depende da leitura do dispositivo · ação: restringir o quantificador ao alcance da Lei Seca (ou confirmar que o…
- Dep. externa: nenhuma · [ ] CONFIRMAR C   [ ] RECLASSIFICAR → ____

**`CF88:ART.37:PAR.13` — Art. 37, § 13 — Readaptação do servidor · MEDIUM**

- **TELEOLOGY_SPECULATIVE** (o_que_significa, gatilho "evita"): "**Ela evita duas soluções piores:**"
  - antes: …aptação é a mudança do servidor para um cargo compatível com a sua nova condição de saúde. · depois: O texto traz condições: o servidor deve ser titular de cargo efetivo; a limitação deve…
  - validador: **PROVÁVEL PROBLEMA** — mesmo padrão corrigido nas rodadas (R01 37 XVI "aproveitar o profissional"; R02 38 V "evitar… · ação: retirar a frase de finalidade (o texto nao a declara) ou reduzi-la ao…
- Dep. externa: nenhuma · [ ] CONFIRMAR C   [ ] RECLASSIFICAR → ____

**`CF88:ART.38:INC.II` — Art. 38, inciso II — Servidor eleito Prefeito · MEDIUM**

- **PERMISSION_NOT_IN_TEXT** (o_que_significa, gatilho "pode ser menor"): "**A opção existe porque, em muitos municípios, o subsídio do Prefeito pode ser menor do que a remuneração do cargo efetivo.**"
  - antes: …Ele recebe uma ou outra, não as duas. · depois: —
  - validador: **INDETERMINADO** — comparação de valores, não necessariamente permissão; confirmar · ação: nao converter a ausencia de garantia em permissao; remeter a…
- Dep. externa: nenhuma · [ ] CONFIRMAR C   [ ] RECLASSIFICAR → ____

**`CF88:ART.39:PAR.2` — Art. 39, § 2º — Escolas de governo · LOW**

- **UNIVERSAL_CLAIM** (exemplo_pratico, gatilho "só pode"): "**Um servidor federal só pode ser promovido se tiver concluído os cursos de capacitação exigidos pela regulamentação da sua carreira.**"
  - antes: — · depois: Ele os faz na escola de governo da União.
  - validador: **PROVÁVEL FALSO POSITIVO** — quantificador dentro de exemplo que reproduz situação prevista na Lei Seca
- Dep. externa: nenhuma · [ ] CONFIRMAR C   [ ] RECLASSIFICAR → ____

**`CF88:ART.39:PAR.7` — Art. 39, § 7º — Aplicação da economia com despesas correntes · MEDIUM**

- **TELEOLOGY_SPECULATIVE** (o_que_significa, gatilho "A ideia é"): "**A ideia é incentivar a eficiência.**"
  - antes: — · depois: Se um órgão gasta menos com despesas do dia a dia, como energia, aluguel e materiais,…
  - validador: **PROVÁVEL PROBLEMA** — mesmo padrão corrigido nas rodadas (R01 37 XVI "aproveitar o profissional"; R02 38 V "evitar… · ação: retirar a frase de finalidade (o texto nao a declara) ou reduzi-la ao…
- Dep. externa: nenhuma · [ ] CONFIRMAR C   [ ] RECLASSIFICAR → ____

## D — FULL_HUMAN_REVIEW (2): pacote completo

### `CF88:ART.37:PAR.7` — Art. 37, § 7º — Informações privilegiadas · risco LOW · DEVICE

**Lei Seca**

- `CF88:ART.37:PAR.7`: A lei disporá sobre os requisitos e as restrições ao ocupante de cargo ou emprego da administração direta e indireta que possibilite o acesso a informações privilegiadas.

**O QUE DIZ**

O parágrafo manda a lei estabelecer requisitos e restrições para quem ocupa cargo ou emprego, na administração direta ou indireta, que dê acesso a informações privilegiadas.

**O QUE SIGNIFICA**

Alguns agentes públicos conhecem, antes do mercado e da população, decisões que valem dinheiro: mudanças de juros, contratos, regulações. Essa informação é chamada privilegiada.

**⟦O parágrafo quer evitar o conflito de interesses, isto é, o uso dessa informação em benefício próprio ou de terceiros.⟧** Por isso a lei pode exigir requisitos para ocupar esses cargos e impor restrições, como períodos de impedimento depois de deixar o cargo.

**EXEMPLO PRÁTICO**

Um diretor de agência reguladora conhece de antemão uma nova regra que valorizará empresas de um setor. A lei pode proibi-lo de negociar ações dessas empresas e de trabalhar para elas por certo período depois de deixar o cargo, como restrição prevista para quem acessa informações privilegiadas.

**ATENÇÃO**

O parágrafo não fixa quais são as restrições: ele depende de lei. A quarentena após a saída do cargo é um exemplo de restrição legal, não está escrita no texto constitucional.

**PALAVRAS DIFÍCEIS**

- *Informação privilegiada*: informação relevante ainda não divulgada, que dá vantagem a quem a conhece.
- *Conflito de interesses*: situação em que o interesse particular do agente pode influenciar a sua atuação pública.
- *Quarentena*: período em que o ex-ocupante de cargo fica impedido de exercer certas atividades.

**CAMADA EXTERNA**

- **⟦A lei sobre conflito de interesses no Poder Executivo federal está na camada de leis correlatas.⟧**

**Warnings/checks:** nenhum
**Validator v2:** TELEOLOGY_SPECULATIVE (REVIEW_REQUIRED); LAW_STATUS_CLAIM (REVIEW_REQUIRED)
**Proveniência:** nenhuma registrada (item pendente)
**Vigência (registro do projeto):** EC 138/2025: "um cargo de professor com outro de qualquer natureza" (antes: tecnico ou cientifico; fonte estrutural canonica); EC 34/2001 (profissionais de saude com profissoes regulamentadas); texto oficial traz "( Vide o art. 3º da Emenda Constitucional nº 135/2024 )"; conteudo da EC fora do art. 37 (ATENCAO + camada externa); Incluidos pela EC 103/2019 (fonte estrutural canonica); Incluido pela EC 109/2021
**Motivo da fila D:** LAW_STATUS_CLAIM (A lei sobre conflito de interesses no Poder Executivo federal está na ca; TELEOLOGY_SPECULATIVE (evitar)
**Catálogo externo:** nenhuma entrada vinculada

**Calibração (evidência local):**

- Afirmação a calibrar: CAMADA EXTERNA — "A lei sobre conflito de interesses no Poder Executivo federal está na camada de leis correlatas."
- Lei mencionada: o draft não a identifica (nem número nem data).
- O que o runtime sustenta: só que "A lei disporá sobre os requisitos e as restrições" (§ 7º). Não sustenta a existência, o conteúdo nem a localização de uma lei federal específica.
- Fonte local disponível: `updater/saida/18_AGENCIAS_E_ORGAOS_REGULADORES/lei_13848_2019_agencias_reguladoras.txt` (linhas 878–879) cita "conflito de interesse, nos termos da Lei nº 12.813, de 16 de maio de 2013". Isso indica que a lei existe, mas o corpus local não traz o texto dela nem sua vigência, e o draft não a nomeia.
- Veio só do draft: a afirmação de estado ("está na camada de leis correlatas"), o recorte "Poder Executivo federal" e, no O QUE SIGNIFICA/EXEMPLO, a quarentena e a proibição de negociar ações como restrições ilustrativas (a ATENÇÃO já diz que a quarentena não está no texto constitucional).
- Proveniência registrada: nenhuma. **EXTERNAL_VERIFICATION_REQUIRED.**

- [ ] CONFIRMAR FULL_HUMAN_REVIEW   - [ ] RECLASSIFICAR → ____

### `CF88:ART.38:INC.III` — Art. 38, inciso III — Servidor eleito Vereador · risco MEDIUM · ITEM

**Lei Seca**

- `CF88:ART.38:INC.III`: investido no mandato de Vereador, havendo compatibilidade de horários, perceberá as vantagens de seu cargo, emprego ou função, sem prejuízo da remuneração do cargo eletivo, e, não havendo compatibilidade, será aplicada a norma do inciso anterior;

**Dispositivos citados pelo draft (runtime)**

- `CF88:ART.38:INC.II`: investido no mandato de Prefeito, será afastado do cargo, emprego ou função, sendo-lhe facultado optar pela sua remuneração;
- `CF88:ART.37:INC.XI`: a remuneração e o subsídio dos ocupantes de cargos, funções e empregos públicos da administração direta, autárquica e fundacional, dos membros de qualquer dos Poderes da União, dos Estados, do Distrito Federal e dos Municípios, dos detentores de mandato eletivo e dos demais agentes políticos e os proventos, pensões ou outra espécie remuneratória, percebidos cumulativamente ou não, incluídas as vantagens pessoais ou de qualquer outra natureza, não poderão exceder o subsídio mensal, em espécie, dos Ministros do Supremo Tribunal Federal, aplicando-se como limite, nos Municípios, o subsídio do Prefeito, e nos Estados e no Distrito Federal, o subsídio mensal do Governador no âmbito do Poder Executivo, o subsídio dos Deputados Estaduais e Distritais no âmbito do Poder Legislativo e o subsídio dos Desembargadores do Tribunal de Justiça, limitado a noventa inteiros e vinte e cinco centésimos por cento do subsídio mensal, em espécie, dos Ministros do Supremo Tribunal Federal, no âmbito do Poder Judiciário, aplicável este limite aos membros do Ministério Público, aos Procuradores e aos Defensores Públicos;

**O QUE DIZ**

Este inciso do art. 38 trata do servidor eleito Vereador. Se houver compatibilidade de horários, ele continua no cargo e recebe as vantagens dele junto com a remuneração do mandato. Se não houver, aplica-se a regra do Prefeito: afastamento com opção de remuneração.

**O QUE SIGNIFICA**

O mandato de Vereador costuma ser exercido em sessões com dias e horários definidos. Por isso a Constituição admite que o servidor continue trabalhando e receba as duas remunerações, desde que consiga cumprir os dois compromissos.

Se os horários se chocam, a solução é a do inciso II: afastamento do cargo e escolha entre a remuneração do cargo e a do mandato.

A compatibilidade é verificada no caso concreto, considerando a jornada do cargo e as atividades da Câmara.

**EXEMPLO PRÁTICO**

Uma servidora municipal com jornada pela manhã é eleita vereadora, e as sessões da Câmara acontecem à noite. Ela mantém o cargo e recebe as duas remunerações. Se, em outro município, as sessões ocorressem no mesmo horário da sua jornada, ela seria afastada e teria de escolher uma das remunerações.

**ATENÇÃO**

É a única hipótese do art. 38 em que cargo e mandato podem ser exercidos ao mesmo tempo, e só com compatibilidade de horários. **⟦A soma das remunerações continua sujeita ao teto do art. 37, XI.⟧**

**PALAVRAS DIFÍCEIS**

- *Compatibilidade de horários*: possibilidade de cumprir a jornada do cargo e as atividades do mandato sem conflito.
- *Vantagens do cargo*: remuneração e demais parcelas a que o servidor tem direito pelo cargo que ocupa.

**CAMADA EXTERNA**

—

**Warnings/checks:** nenhum
**Validator v2:** CATALOG_CONTRADICTION (REVIEW_REQUIRED, STF_TEMAS_377_384)
**Proveniência:** nenhuma registrada (item pendente)
**Vigência (registro do projeto):** nenhuma observação específica registrada
**Motivo da fila D:** CATALOG_CONTRADICTION (soma das remunerações continua sujeita ao teto)
**Catálogo externo:** STF_TEMAS_377_384

**Calibração (evidência local):**

- Afirmação a calibrar: ATENÇÃO, 2ª frase — "A soma das remunerações continua sujeita ao teto do art. 37, XI."
- Catálogo: `STF_TEMAS_377_384` registra que, nas acumulações constitucionalmente autorizadas de cargos, empregos e funções, o teto do art. 37, XI, é considerado em relação a cada vínculo, e não sobre o somatório (validado nas Rodadas 01, 03A e 03B).
- O draft afirma a leitura oposta (soma) como regra, sem remissão à camada externa. Se a combinação cargo + mandato de Vereador do art. 38, III, se enquadra exatamente na tese dos Temas 377/384 é questão jurídica para a revisão humana: não resolvida aqui.
- Proveniência registrada: nenhuma (item pendente). Camada externa: vazia.

- [ ] CONFIRMAR FULL_HUMAN_REVIEW   - [ ] RECLASSIFICAR → ____

## Fora deste pacote

- Acervo anterior aprovado: 45 alertas registrados em `T1_LEGACY_AUDIT_BACKLOG.md` (não bloqueiam o Batch05; nada alterado).
