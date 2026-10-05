# TRIAGEM DE RISCO EDITORIAL — ENTENDA_CF_PRODUCTION_BATCH_06

Data de referência: 2026-10-04. Nenhum texto foi alterado por esta triagem e nenhuma explicação foi aprovada: todas seguem `PENDING_HUMAN_REVIEW`. `READY_FOR_EDITORIAL_REVIEW` significa apenas que as checagens automáticas foram resolvidas pelo editor e que a explicação pode ir para a revisão humana.

- Explicações: 93 · risco LOW 3 · MEDIUM 1 · HIGH 89
- Prontas para revisão editorial: 82 · aprovadas (HUMAN_APPROVED_T1): 0
- Achados: ABSOLUTE_CLAIM 4, DUPLICATION 2, EXAMPLE_NUMBER 1, EXCEPTION_NOT_IN_TEXT 2, LAW_DEPENDENCY_OMITTED 5, LONG_SENTENCE 9, MODALITY_SHIFT 1, TRANSITION_IN_CORE 1 · não resolvidos: 12

## Risco HIGH

### Art. 42 — Militares dos Estados, do Distrito Federal e dos Territórios

- `CF88:ART.42` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.42:CAPUT: Redacao dada pela Emenda Constitucional n. 18, de 1998; ART.42:PAR.1: Redacao dada pela Emenda Constitucional n. 20, de 1998; ART.42:PAR.2: Redacao dada pela Emenda Constitucional n. 41, de 2003 (+1); LAW_DEPENDENCY: lei específica; COMPLEX_REMISSION: arts. 14, 37, 40, 142

### Art. 42, § 1º — Regras aplicáveis aos militares estaduais

- `CF88:ART.42:PAR.1` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.42:PAR.1: Redacao dada pela Emenda Constitucional n. 20, de 1998; COMPLEX_REMISSION: arts. 14, 40, 142

### Art. 42, § 3º — Acumulação de cargos pelo militar estadual

- `CF88:ART.42:PAR.3` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.42:PAR.3: Incluido pela Emenda Constitucional n. 101, de 2019
- EXCEPTION_NOT_IN_TEXT (o_que_diz/o_que_significa: exceções) → Falso positivo: "exceções" descreve as hipoteses do art. 37, XVI, para o qual o § 3º remete; nao cria excecao propria.

### Art. 43 — Regiões de desenvolvimento

- `CF88:ART.43` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.43:PAR.4: Incluido pela Emenda Constitucional n. 132, de 2023; LAW_DEPENDENCY: Lei complementar
- ABSOLUTE_CLAIM (o_que_significa: sempre) → Falso positivo: "sempre que possível" reproduz a expressao do § 4º, que e justamente uma ressalva (nao absoluta).
- ABSOLUTE_CLAIM (atencao: sempre) → Falso positivo: "sempre que possível" reproduz a expressao do § 4º, que e justamente uma ressalva (nao absoluta).

### Art. 43, § 2º — Incentivos regionais

- `CF88:ART.43:PAR.2` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: LAW_DEPENDENCY: na forma da lei; BLOCK_MULTI_DEPENDENCY: 5 dispositivos

### Art. 44 — Congresso Nacional e legislatura

- `CF88:ART.44` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: DEADLINE: quatro anos; NUMBER_OR_PERCENTAGE: quatro

### Art. 45 — Câmara dos Deputados

- `CF88:ART.45` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EXTERNAL_LAW_STATE: ART.45:PAR.1: Vide Lei Complementar n. 78, de 1993 (numero total de Deputados e representacao por Estado); NUMBER_OR_PERCENTAGE: oito; LAW_DEPENDENCY: lei complementar

### Art. 45, § 1º — Número de deputados por Estado

- `CF88:ART.45:PAR.1` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EXTERNAL_LAW_STATE: ART.45:PAR.1: Vide Lei Complementar n. 78, de 1993 (numero total de Deputados e representacao por Estado); NUMBER_OR_PERCENTAGE: oito; LAW_DEPENDENCY: lei complementar

### Art. 46 — Senado Federal

- `CF88:ART.46` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: QUORUM: dois terços; DEADLINE: oito anos; NUMBER_OR_PERCENTAGE: três

### Art. 47 — Quórum das deliberações

- `CF88:ART.47` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: QUORUM: maioria; EXCEPTION: Salvo
- TRANSITION_IN_CORE (o_que_significa: emenda constitucional) → Falso positivo: "emenda constitucional" designa a especie normativa (quorum de tres quintos), nao regra de transicao nem historico de redacao.

### Art. 48 — Competência legislativa do Congresso com sanção

- `CF88:ART.48` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.48:INC.IX: Redacao dada pela Emenda Constitucional n. 69, de 2012; ART.48:INC.X: Redacao dada pela Emenda Constitucional n. 32, de 2001; ART.48:INC.XI: Redacao dada pela Emenda Constitucional n. 32, de 2001 (+1); SENSITIVE_THEME: sanção; COMPLEX_REMISSION: arts. 39, 49, 84

### Art. 49 — Competência exclusiva do Congresso

- `CF88:ART.49` · OVERVIEW · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.49:INC.VII: Redacao dada pela Emenda Constitucional n. 19, de 1998; ART.49:INC.VIII: Redacao dada pela Emenda Constitucional n. 19, de 1998; ART.49:INC.XVIII: Incluido pela Emenda Constitucional n. 109, de 2021; QUORUM: dois terços; DEADLINE: quinze dias; NUMBER_OR_PERCENTAGE: quinze; EXCEPTION: ressalvados; LAW_DEPENDENCY: previstos em lei; COMPLEX_REMISSION: arts. 37, 167
- LONG_SENTENCE (o_que_diz: decidir definitivamente sobre tratados que gerem encargos gravosos, au) → NÃO RESOLVIDO
- LAW_DEPENDENCY_OMITTED (body: previstos em lei) → NÃO RESOLVIDO

### Art. 49, inciso I — Tratados que geram encargos ao patrimônio nacional

- `CF88:ART.49:INC.I` · ITEM · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional

### Art. 49, inciso V — Sustação de atos normativos do Executivo

- `CF88:ART.49:INC.V` · ITEM · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: LAW_DEPENDENCY: regulament

### Art. 50 — Convocação de ministros e pedidos de informação

- `CF88:ART.50` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.50:CAPUT: Redacao dada pela Emenda Constitucional n. 132, de 2023; ART.50:PAR.2: Redacao dada pela Emenda Constitucional de Revisao n. 2, de 1994; DEADLINE: prazo; NUMBER_OR_PERCENTAGE: trinta; SENSITIVE_THEME: crime

### Art. 50, § 2º — Pedidos escritos de informação

- `CF88:ART.50:PAR.2` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.50:PAR.2: Redacao dada pela Emenda Constitucional de Revisao n. 2, de 1994; DEADLINE: prazo; NUMBER_OR_PERCENTAGE: trinta; SENSITIVE_THEME: crime

### Art. 51 — Competências privativas da Câmara

- `CF88:ART.51` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.51:INC.IV: Redacao dada pela Emenda Constitucional n. 19, de 1998; QUORUM: dois terços; DEADLINE: sessenta dias; NUMBER_OR_PERCENTAGE: dois

### Art. 51, inciso I — Autorização para processo contra o Presidente

- `CF88:ART.51:INC.I` · ITEM · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: QUORUM: dois terços; NUMBER_OR_PERCENTAGE: dois; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional

### Art. 52 — Competências privativas do Senado

- `CF88:ART.52` · OVERVIEW · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.52:INC.I: Redacao dada pela Emenda Constitucional n. 23, de 1999; ART.52:INC.II: Redacao dada pela Emenda Constitucional n. 45, de 2004; ART.52:INC.XIII: Redacao dada pela Emenda Constitucional n. 19, de 1998 (+1); QUORUM: maioria; DEADLINE: oito anos; NUMBER_OR_PERCENTAGE: dois; SENSITIVE_THEME: crimes
- LONG_SENTENCE (o_que_diz: julgar autoridades por crime de responsabilidade, aprovar a escolha de) → NÃO RESOLVIDO

### Art. 52, incisos I e II — Autoridades julgadas pelo Senado por crime de responsabilidade

- `CF88:ART.52:INC.I` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.52:INC.I: Redacao dada pela Emenda Constitucional n. 23, de 1999; ART.52:INC.II: Redacao dada pela Emenda Constitucional n. 45, de 2004; SENSITIVE_THEME: crimes; JURISPRUDENCE: nota da camada JURISPRUDENCIA

### Art. 52, inciso III — Aprovação prévia de autoridades pelo Senado

- `CF88:ART.52:INC.III` · BLOCK · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: BLOCK_MULTI_DEPENDENCY: 7 dispositivos
- LONG_SENTENCE (o_que_diz: O inciso III exige aprovação prévia do Senado, por voto secreto e após) → NÃO RESOLVIDO

### Art. 52, inciso X — Suspensão de lei declarada inconstitucional

- `CF88:ART.52:INC.X` · ITEM · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: JURISPRUDENCE: nota da camada JURISPRUDENCIA

### Art. 52, parágrafo único — Julgamento político: presidência, quórum e pena

- `CF88:ART.52:PAR.UNICO` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: QUORUM: dois terços; DEADLINE: oito anos; NUMBER_OR_PERCENTAGE: dois; SENSITIVE_THEME: sanções; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: questão de interpretação

### Art. 53 — Imunidades e prerrogativas dos parlamentares

- `CF88:ART.53` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.53:CAPUT: Redacao dada pela Emenda Constitucional n. 35, de 2001; ART.53:PAR.1: Redacao dada pela Emenda Constitucional n. 35, de 2001; ART.53:PAR.2: Redacao dada pela Emenda Constitucional n. 35, de 2001 (+6); QUORUM: maioria; DEADLINE: quatro horas; NUMBER_OR_PERCENTAGE: vinte; SENSITIVE_THEME: invioláv; EXCEPTION: salvo

### Art. 53, caput — Inviolabilidade por opiniões, palavras e votos

- `CF88:ART.53:CAPUT` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.53:CAPUT: Redacao dada pela Emenda Constitucional n. 35, de 2001; SENSITIVE_THEME: invioláv; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional

### Art. 53, § 1º — Foro dos parlamentares no Supremo Tribunal Federal

- `CF88:ART.53:PAR.1` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.53:PAR.1: Redacao dada pela Emenda Constitucional n. 35, de 2001; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional

### Art. 53, § 2º — Limites à prisão do parlamentar

- `CF88:ART.53:PAR.2` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.53:PAR.2: Redacao dada pela Emenda Constitucional n. 35, de 2001; QUORUM: maioria; DEADLINE: quatro horas; NUMBER_OR_PERCENTAGE: vinte; SENSITIVE_THEME: crime; EXCEPTION: salvo; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: questão de interpretação

### Art. 53, §§ 3º, 4º e 5º — Sustação do processo penal contra o parlamentar

- `CF88:ART.53:PAR.3` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.53:PAR.3: Redacao dada pela Emenda Constitucional n. 35, de 2001; ART.53:PAR.4: Redacao dada pela Emenda Constitucional n. 35, de 2001; ART.53:PAR.5: Redacao dada pela Emenda Constitucional n. 35, de 2001; QUORUM: maioria; DEADLINE: prazo; NUMBER_OR_PERCENTAGE: quarenta; SENSITIVE_THEME: crime; BLOCK_MULTI_DEPENDENCY: 3 dispositivos

### Art. 53, § 6º — Dispensa de testemunhar sobre informações do mandato

- `CF88:ART.53:PAR.6` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.53:PAR.6: Redacao dada pela Emenda Constitucional n. 35, de 2001

### Art. 53, § 8º — Imunidades durante o estado de sítio

- `CF88:ART.53:PAR.8` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.53:PAR.8: Incluido pela Emenda Constitucional n. 35, de 2001; QUORUM: dois terços; NUMBER_OR_PERCENTAGE: dois; SENSITIVE_THEME: imunidade

### Art. 54 — Incompatibilidades dos parlamentares

- `CF88:ART.54` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: direito; EXCEPTION: salvo

### Art. 54, inciso I — Vedações desde a expedição do diploma

- `CF88:ART.54:INC.I` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: direito; EXCEPTION: salvo; BLOCK_MULTI_DEPENDENCY: 3 dispositivos

### Art. 54, inciso II — Vedações desde a posse

- `CF88:ART.54:INC.II` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: direito; BLOCK_MULTI_DEPENDENCY: 5 dispositivos

### Art. 55 — Perda do mandato de deputado ou senador

- `CF88:ART.55` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.55:PAR.2: Redacao dada pela Emenda Constitucional n. 76, de 2013; ART.55:PAR.4: Incluido pela Emenda Constitucional de Revisao n. 6, de 1994; QUORUM: terça parte; SENSITIVE_THEME: Perderá o mandato; EXCEPTION: salvo

### Art. 55, inciso VI — Condenação criminal definitiva e perda do mandato

- `CF88:ART.55:INC.VI` · ITEM · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional
- ABSOLUTE_CLAIM (o_que_significa: automaticamente) → Falso positivo: frase negativa ("e não declarada automaticamente"), que justamente afasta efeito automatico.

### Art. 55, § 1º — O que é incompatível com o decoro parlamentar

- `CF88:ART.55:PAR.1` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: incompatív

### Art. 55, §§ 2º e 3º — Quem decide a perda do mandato

- `CF88:ART.55:PAR.2` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.55:PAR.2: Redacao dada pela Emenda Constitucional n. 76, de 2013; QUORUM: maioria; SENSITIVE_THEME: perda do mandato

### Art. 55, § 4º — Renúncia durante processo de perda do mandato

- `CF88:ART.55:PAR.4` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.55:PAR.4: Incluido pela Emenda Constitucional de Revisao n. 6, de 1994; SENSITIVE_THEME: perda do mandato

### Art. 56 — Situações que não geram perda do mandato

- `CF88:ART.56` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: DEADLINE: vinte dias; NUMBER_OR_PERCENTAGE: cento; SENSITIVE_THEME: perderá o mandato

### Art. 56, §§ 1º e 2º — Suplente e eleição para preencher a vaga

- `CF88:ART.56:PAR.1` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: DEADLINE: vinte dias; NUMBER_OR_PERCENTAGE: cento

### Art. 57 — Funcionamento do Congresso: sessões e reuniões

- `CF88:ART.57` · OVERVIEW · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.57:CAPUT: Redacao dada pela Emenda Constitucional n. 50, de 2006; ART.57:PAR.4: Redacao dada pela Emenda Constitucional n. 50, de 2006; ART.57:PAR.6: Redacao dada pela Emenda Constitucional n. 50, de 2006 (+3); QUORUM: maioria; NUMBER_OR_PERCENTAGE: duas; EXCEPTION: ressalvada
- LONG_SENTENCE (o_que_diz: o calendário anual de reuniões, com dois períodos, um de fevereiro a j) → NÃO RESOLVIDO

### Art. 57, § 4º — Sessões preparatórias e eleição das Mesas

- `CF88:ART.57:PAR.4` · DEVICE · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.57:PAR.4: Redacao dada pela Emenda Constitucional n. 50, de 2006; NUMBER_OR_PERCENTAGE: dois; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional
- LONG_SENTENCE (o_que_diz: O § 4º prevê sessões preparatórias de cada Casa, a partir de 1º de fev) → NÃO RESOLVIDO

### Art. 57, § 6º — Convocação extraordinária do Congresso

- `CF88:ART.57:PAR.6` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.57:PAR.6: Redacao dada pela Emenda Constitucional n. 50, de 2006; ART.57:PAR.6:INC.II: Redacao dada pela Emenda Constitucional n. 50, de 2006; QUORUM: maioria; BLOCK_MULTI_DEPENDENCY: 3 dispositivos

### Art. 57, §§ 7º e 8º — Pauta da sessão extraordinária

- `CF88:ART.57:PAR.7` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.57:PAR.7: Redacao dada pela Emenda Constitucional n. 50, de 2006; ART.57:PAR.8: Incluido pela Emenda Constitucional n. 32, de 2001; EXCEPTION: ressalvada
- ABSOLUTE_CLAIM (o_que_significa: automaticamente) → Fiel ao texto: o § 8º diz que as medidas provisorias em vigor serao automaticamente incluidas na pauta.

### Art. 58 — Comissões do Congresso e de suas Casas

- `CF88:ART.58` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: QUORUM: um terço; DEADLINE: prazo; NUMBER_OR_PERCENTAGE: décimo; EXCEPTION: salvo
- LAW_DEPENDENCY_OMITTED (body: de lei) → Falso positivo: "de lei" no texto e parte de "projeto de lei" (competencia das comissoes), nao dependencia de lei.

### Art. 58, § 2º — O que as comissões podem fazer

- `CF88:ART.58:PAR.2` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: NUMBER_OR_PERCENTAGE: décimo; EXCEPTION: salvo; BLOCK_MULTI_DEPENDENCY: 7 dispositivos
- LAW_DEPENDENCY_OMITTED (body: de lei) → Falso positivo: "de lei" no texto e parte de "projeto de lei", nao dependencia de lei.

### Art. 58, § 3º — Comissões parlamentares de inquérito

- `CF88:ART.58:PAR.3` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: QUORUM: um terço; DEADLINE: prazo; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional

### Art. 59 — Espécies do processo legislativo

- `CF88:ART.59` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: LAW_DEPENDENCY: Lei complementar

### Art. 61 — Iniciativa das leis

- `CF88:ART.61` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.61:PAR.1:INC.II:AL.c: Redacao dada pela Emenda Constitucional n. 18, de 1998; ART.61:PAR.1:INC.II:AL.e: Redacao dada pela Emenda Constitucional n. 32, de 2001; ART.61:PAR.1:INC.II:AL.f: Incluido pela Emenda Constitucional n. 18, de 1998; NUMBER_OR_PERCENTAGE: por cento

### Art. 61, § 1º — Iniciativa privativa do Presidente da República

- `CF88:ART.61:PAR.1` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.61:PAR.1:INC.II:AL.c: Redacao dada pela Emenda Constitucional n. 18, de 1998; ART.61:PAR.1:INC.II:AL.e: Redacao dada pela Emenda Constitucional n. 32, de 2001; ART.61:PAR.1:INC.II:AL.f: Incluido pela Emenda Constitucional n. 18, de 1998; JURISPRUDENCE: nota da camada JURISPRUDENCIA; BLOCK_MULTI_DEPENDENCY: 9 dispositivos; INTERPRETIVE_CONTROVERSY: interpretação constitucional

### Art. 61, § 2º — Iniciativa popular de lei

- `CF88:ART.61:PAR.2` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: NUMBER_OR_PERCENTAGE: por cento

### Art. 62 — Medidas provisórias

- `CF88:ART.62` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.62:CAPUT: Redacao dada pela Emenda Constitucional n. 32, de 2001; ART.62:PAR.1: Incluido pela Emenda Constitucional n. 32, de 2001; ART.62:PAR.1:INC.I: Incluido pela Emenda Constitucional n. 32, de 2001 (+18); DEADLINE: prazo; NUMBER_OR_PERCENTAGE: sessenta; SENSITIVE_THEME: direitos; EXCEPTION: ressalvado; LAW_DEPENDENCY: lei complementar; COMPLEX_REMISSION: arts. 153, 167
- MODALITY_SHIFT (o_que_diz: devem) → Fiel ao texto: o caput diz "devendo submetê-las de imediato ao Congresso Nacional"; a obrigacao e textual.

### Art. 62, § 1º — Matérias vedadas às medidas provisórias

- `CF88:ART.62:PAR.1` · BLOCK · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.62:PAR.1: Incluido pela Emenda Constitucional n. 32, de 2001; ART.62:PAR.1:INC.I: Incluido pela Emenda Constitucional n. 32, de 2001; ART.62:PAR.1:INC.I:AL.a: Incluido pela Emenda Constitucional n. 32, de 2001 (+6); SENSITIVE_THEME: direitos; EXCEPTION: ressalvado; LAW_DEPENDENCY: lei complementar; JURISPRUDENCE: nota da camada JURISPRUDENCIA; BLOCK_MULTI_DEPENDENCY: 9 dispositivos; INTERPRETIVE_CONTROVERSY: questão de interpretação
- DUPLICATION (o_que_diz: CF88:ART.62:PAR.1 x CF88:ART.68:PAR.1 sim=0.356) → NÃO RESOLVIDO

### Art. 62, § 2º — Medida provisória sobre impostos

- `CF88:ART.62:PAR.2` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.62:PAR.2: Incluido pela Emenda Constitucional n. 32, de 2001; EXCEPTION: exceto

### Art. 62, §§ 3º, 4º e 7º — Prazo de vigência da medida provisória

- `CF88:ART.62:PAR.3` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.62:PAR.3: Incluido pela Emenda Constitucional n. 32, de 2001; ART.62:PAR.4: Incluido pela Emenda Constitucional n. 32, de 2001; ART.62:PAR.7: Incluido pela Emenda Constitucional n. 32, de 2001; DEADLINE: prazo; NUMBER_OR_PERCENTAGE: sessenta; EXCEPTION: ressalvado; BLOCK_MULTI_DEPENDENCY: 3 dispositivos

### Art. 62, §§ 5º, 8º e 9º — Tramitação da medida provisória no Congresso

- `CF88:ART.62:PAR.5` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.62:PAR.5: Incluido pela Emenda Constitucional n. 32, de 2001; ART.62:PAR.8: Incluido pela Emenda Constitucional n. 32, de 2001; ART.62:PAR.9: Incluido pela Emenda Constitucional n. 32, de 2001; JURISPRUDENCE: nota da camada JURISPRUDENCIA; BLOCK_MULTI_DEPENDENCY: 3 dispositivos; INTERPRETIVE_CONTROVERSY: interpretação constitucional

### Art. 62, § 6º — Regime de urgência e trancamento de pauta

- `CF88:ART.62:PAR.6` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.62:PAR.6: Incluido pela Emenda Constitucional n. 32, de 2001; DEADLINE: cinco dias; NUMBER_OR_PERCENTAGE: quarenta; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional

### Art. 62, § 10 — Proibição de reeditar medida provisória

- `CF88:ART.62:PAR.10` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.62:PAR.10: Incluido pela Emenda Constitucional n. 32, de 2001; DEADLINE: prazo; INTERPRETIVE_CONTROVERSY: questão de interpretação

### Art. 62, §§ 11 e 12 — Efeitos depois da rejeição ou da aprovação com alterações

- `CF88:ART.62:PAR.11` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.62:PAR.11: Incluido pela Emenda Constitucional n. 32, de 2001; ART.62:PAR.12: Incluido pela Emenda Constitucional n. 32, de 2001; DEADLINE: sessenta dias; NUMBER_OR_PERCENTAGE: sessenta

### Art. 63 — Proibição de aumentar despesa por emenda

- `CF88:ART.63` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EXCEPTION: ressalvado; JURISPRUDENCE: nota da camada JURISPRUDENCIA

### Art. 64 — Início na Câmara e urgência constitucional

- `CF88:ART.64` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.64:PAR.2: Redacao dada pela Emenda Constitucional n. 32, de 2001; DEADLINE: cinco dias; NUMBER_OR_PERCENTAGE: quarenta

### Art. 64, §§ 2º, 3º e 4º — Prazos da urgência pedida pelo Presidente

- `CF88:ART.64:PAR.2` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.64:PAR.2: Redacao dada pela Emenda Constitucional n. 32, de 2001; DEADLINE: cinco dias; NUMBER_OR_PERCENTAGE: quarenta; BLOCK_MULTI_DEPENDENCY: 3 dispositivos
- EXCEPTION_NOT_IN_TEXT (o_que_diz/o_que_significa: exceto) → Falso positivo do detector: o § 2º diz "com exceção das que tenham prazo constitucional determinado" ("exceção" nao esta na lista de marcadores).

### Art. 65 — Revisão do projeto pela outra Casa

- `CF88:ART.65` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: sanção

### Art. 66 — Sanção, veto e promulgação

- `CF88:ART.66` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.66:PAR.4: Redacao dada pela Emenda Constitucional n. 76, de 2013; ART.66:PAR.6: Redacao dada pela Emenda Constitucional n. 32, de 2001; QUORUM: maioria; DEADLINE: prazo; NUMBER_OR_PERCENTAGE: quinze; SENSITIVE_THEME: sanção

### Art. 66, §§ 1º, 2º e 3º — Veto: prazo, motivos, veto parcial e sanção tácita

- `CF88:ART.66:PAR.1` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: DEADLINE: prazo; NUMBER_OR_PERCENTAGE: quinze; SENSITIVE_THEME: sanção; BLOCK_MULTI_DEPENDENCY: 3 dispositivos

### Art. 66, §§ 4º, 5º e 6º — Apreciação do veto pelo Congresso

- `CF88:ART.66:PAR.4` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.66:PAR.4: Redacao dada pela Emenda Constitucional n. 76, de 2013; ART.66:PAR.6: Redacao dada pela Emenda Constitucional n. 32, de 2001; QUORUM: maioria; DEADLINE: trinta dias; NUMBER_OR_PERCENTAGE: trinta; BLOCK_MULTI_DEPENDENCY: 3 dispositivos

### Art. 66, § 7º — Quem promulga a lei

- `CF88:ART.66:PAR.7` · DEVICE · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: DEADLINE: oito horas; NUMBER_OR_PERCENTAGE: quarenta
- LONG_SENTENCE (o_que_diz: O § 7º determina que, se o Presidente da República não promulgar a lei) → NÃO RESOLVIDO

### Art. 67 — Reapresentação de projeto rejeitado

- `CF88:ART.67` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: QUORUM: maioria

### Art. 68 — Leis delegadas

- `CF88:ART.68` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: garantia; LAW_DEPENDENCY: lei complementar

### Art. 68, § 1º — Matérias que não podem ser delegadas

- `CF88:ART.68:PAR.1` · BLOCK · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: garantia; LAW_DEPENDENCY: lei complementar; BLOCK_MULTI_DEPENDENCY: 4 dispositivos
- DUPLICATION (o_que_diz: CF88:ART.62:PAR.1 x CF88:ART.68:PAR.1 sim=0.356) → NÃO RESOLVIDO

### Art. 69 — Quórum da lei complementar

- `CF88:ART.69` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: QUORUM: maioria; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: questão de interpretação

### Art. 70 — Fiscalização da União: controle externo e interno

- `CF88:ART.70` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.70:PAR.UNICO: Redacao dada pela Emenda Constitucional n. 19, de 1998

### Art. 70, parágrafo único — Quem deve prestar contas

- `CF88:ART.70:PAR.UNICO` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.70:PAR.UNICO: Redacao dada pela Emenda Constitucional n. 19, de 1998

### Art. 71 — Competências do Tribunal de Contas da União

- `CF88:ART.71` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: DEADLINE: sessenta dias; NUMBER_OR_PERCENTAGE: sessenta; SENSITIVE_THEME: sanções; EXCEPTION: excetuad; LAW_DEPENDENCY: previstas em lei
- LAW_DEPENDENCY_OMITTED (body: em lei) → Dependencia de lei e do inciso VIII (sancoes previstas em lei), que tem explicacao propria (ITEM) mencionando a lei.

### Art. 71, inciso I — Parecer prévio sobre as contas do Presidente

- `CF88:ART.71:INC.I` · ITEM · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: DEADLINE: sessenta dias; NUMBER_OR_PERCENTAGE: sessenta

### Art. 71, inciso III — Registro de admissões e aposentadorias

- `CF88:ART.71:INC.III` · ITEM · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: EXCEPTION: excetuad; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional
- LONG_SENTENCE (o_que_diz: O inciso III atribui ao Tribunal examinar, para registro, a legalidade) → NÃO RESOLVIDO

### Art. 71, inciso VIII — Sanções aplicadas pelo Tribunal

- `CF88:ART.71:INC.VIII` · ITEM · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: sanções; LAW_DEPENDENCY: previstas em lei

### Art. 71, incisos IX e X — Prazo para correção e sustação de atos

- `CF88:ART.71:INC.IX` · BLOCK · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: DEADLINE: prazo
- LONG_SENTENCE (o_que_diz: Os incisos IX e X permitem ao Tribunal, diante de ilegalidade, fixar p) → NÃO RESOLVIDO

### Art. 71, §§ 1º e 2º — Sustação de contratos

- `CF88:ART.71:PAR.1` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: DEADLINE: prazo; NUMBER_OR_PERCENTAGE: noventa; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional

### Art. 71, § 3º — Força das decisões que impõem débito ou multa

- `CF88:ART.71:PAR.3` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: multa; JURISPRUDENCE: nota da camada JURISPRUDENCIA; INTERPRETIVE_CONTROVERSY: interpretação constitucional

### Art. 72 — Despesas não autorizadas: atuação da comissão mista

- `CF88:ART.72` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: DEADLINE: prazo; NUMBER_OR_PERCENTAGE: cinco

### Art. 73 — Composição e organização do Tribunal de Contas da União

- `CF88:ART.73` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.73:PAR.1:INC.I: Redacao dada pela Emenda Constitucional n. 122, de 2022; ART.73:PAR.3: Redacao dada pela Emenda Constitucional n. 20, de 1998; QUORUM: um terço; DEADLINE: setenta anos; NUMBER_OR_PERCENTAGE: nove; SENSITIVE_THEME: garantias; COMPLEX_REMISSION: arts. 40, 96

### Art. 73, § 1º — Requisitos para Ministro do Tribunal de Contas da União

- `CF88:ART.73:PAR.1` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.73:PAR.1:INC.I: Redacao dada pela Emenda Constitucional n. 122, de 2022; DEADLINE: setenta anos; NUMBER_OR_PERCENTAGE: trinta; BLOCK_MULTI_DEPENDENCY: 5 dispositivos

### Art. 73, § 2º — Escolha dos Ministros do Tribunal de Contas da União

- `CF88:ART.73:PAR.2` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: QUORUM: um terço; NUMBER_OR_PERCENTAGE: dois; BLOCK_MULTI_DEPENDENCY: 3 dispositivos

### Art. 73, § 3º — Garantias dos Ministros do Tribunal de Contas da União

- `CF88:ART.73:PAR.3` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.73:PAR.3: Redacao dada pela Emenda Constitucional n. 20, de 1998; SENSITIVE_THEME: garantias

### Art. 74 — Sistema de controle interno

- `CF88:ART.74` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: direito; LAW_DEPENDENCY: na forma da lei
- LAW_DEPENDENCY_OMITTED (body: na forma da lei) → "Na forma da lei" e do § 2º (denuncia ao TCU), que tem explicacao propria (DEVICE) mencionando a lei.

### Art. 74, § 1º — Dever de comunicar irregularidades

- `CF88:ART.74:PAR.1` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: SENSITIVE_THEME: sob pena

### Art. 74, § 2º — Denúncia de irregularidades ao Tribunal

- `CF88:ART.74:PAR.2` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: LAW_DEPENDENCY: na forma da lei

### Art. 75 — Tribunais de Contas dos Estados, do Distrito Federal e dos Municípios

- `CF88:ART.75` · OVERVIEW · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: EC_WORDING: ART.75:CAPUT: Redacao dada pela Emenda Constitucional n. 139, de 2026 (redacao recente: "vedada sua extincao, criacao ou instalacao"; verificar redacao oficial e alcance); EXTERNAL_LAW_STATE: nota de verificacao externa; NUMBER_OR_PERCENTAGE: sete; JURISPRUDENCE: nota da camada JURISPRUDENCIA

## Risco MEDIUM

### Art. 68, §§ 2º e 3º — Forma da delegação e apreciação pelo Congresso

- `CF88:ART.68:PAR.2` · BLOCK · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: estrutura de lista/bloco: 2 dispositivos

## Risco LOW

### Art. 49, inciso IX — Julgamento das contas do Presidente

- `CF88:ART.49:INC.IX` · ITEM · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: regra simples, sem remissao, numero, prazo, excecao ou tema sensivel

### Art. 57, § 2º — Recesso condicionado à aprovação da LDO

- `CF88:ART.57:PAR.2` · DEVICE · READY_FOR_EDITORIAL_REVIEW · PENDING_HUMAN_REVIEW
- Motivos do risco: regra simples, sem remissao, numero, prazo, excecao ou tema sensivel
- EXAMPLE_NUMBER (exemplo_pratico: 17) → Data "17 de julho" vem do caput do art. 57 (fim do primeiro periodo), contexto do § 2º; nao e numero inventado.

### Art. 71, inciso II — Julgamento das contas de administradores

- `CF88:ART.71:INC.II` · ITEM · EDITORIAL_FIXES_REQUIRED · PENDING_HUMAN_REVIEW
- Motivos do risco: regra simples, sem remissao, numero, prazo, excecao ou tema sensivel
- LONG_SENTENCE (o_que_diz: O inciso II atribui ao Tribunal julgar as contas de quem administra ou) → NÃO RESOLVIDO

