# BATCH06 — REVISÃO COMPACTA (filas A e B)

Lote `ENTENDA_CF_PRODUCTION_BATCH_06` · 2026-10-04 · nenhum item aprovado (AUTO_APPROVE_LOW/MEDIUM = OFF). Revisão humana obrigatória em formato compacto; T1 completo só sob pedido. Risco = LEGAL_RISK; complexidade = VERIFICATION_COMPLEXITY.

## A — CLEAN_LOW (27)

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

