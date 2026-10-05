# T1_EDITORIAL_STANDARD_FREEZE_AND_SCALE — diagnóstico

Data de referência: 2026-10-04. Diagnóstico **somente leitura**: nenhum MEDIUM/LOW foi alterado ou aprovado; sem staging, commit, tag ou push.
Dados: `CF88_BATCH_05.entenda.jsonl`, decisões e ajustes das Rodadas 01, 02, 03A e 03B, `EDITORIAL_CHECKS.json`, lint do build.
Regras aprendidas: detectores candidatos em `T1_FREEZE_AND_SCALE_DIAGNOSTIC.json` (`rules`), ainda fora do motor.

## 1. Situação

| Indicador | Valor |
|---|---|
| HUMAN_APPROVED_T1 no Batch05 (novos) | 38 (+ 3 pilotos reutilizados) |
| HIGH aprovados | 38/38 |
| HUMAN_APPROVED_T1 já integrados antes do Batch05 (CF88) | 220 |
| Total CF88 aprovado, se o Batch05 for integrado | 258 |
| MEDIUM pendentes | 23 |
| LOW pendentes | 8 |
| editorial_checks sem resolução | 0 |

**Rodadas HIGH:**

| Rodada | Escopo | Itens | Aprovados sem alteração | Ajustados | Desvios T1/edições registrados |
|---|---|---|---|---|---|
| 01 | `CF88_ART37_HIGH_ROUND_1` | 7 | 1 | 6 | 8 |
| 02 | `CF88_ART38_39_41_HIGH_ROUND_2` | 9 | 2 | 7 | 2 |
| 03A | `CF88_ART40_HIGH_ROUND_3A` | 11 | 3 | 8 | 2 |
| 03B | `CF88_ART40_HIGH_ROUND_3B` | 11 | 1 | 10 | 1 |

Taxa de ajuste nos HIGH: 31 de 38 (82%).

## 2. Alertas ainda existentes nos 31 pendentes

- editorial_checks: 7 achados, todos já resolvidos com justificativa (ABSOLUTE_CLAIM 3, EXAMPLE_NUMBER 1, MODALITY_SHIFT 2, TECHNICAL_TERM_UNDEFINED 1).
- Lint do motor (não bloqueante): PARENT_REPETITION 1, ABSOLUTE_CLAIM 4, EXAMPLE_REQUIREMENT_LANGUAGE 9, NEAR_COPY_OF_OFFICIAL_TEXT 3.
- Regras aprendidas (novas): TELEOLOGY_SPECULATIVE 6, UNIVERSAL_CLAIM 9, AUTOMATIC_CONSEQUENCE 3, JURIS_SENSITIVE_TOPIC 1.

## 3. Quanto as regras aprendidas conseguem decidir

As 8 regras foram extraídas dos motivos de AJUSTAR das quatro rodadas (finalidade especulativa, generalização universal, consequência automática, tema com jurisprudência catalogada no núcleo, afirmação sobre estado de lei, identificador interno, controvérsia tratada como aberta, critério inventado no exemplo). Medição contra as decisões humanas reais:

- **Pegaram 19 de 31** versões v1 que o revisor mandou ajustar (61%).
- Dispararam em 4 das 7 v1 aprovadas sem alteração (falsos positivos), e em 9 dos 38 textos finais aprovados (quase sempre ressalvas legítimas, como "não ... todos os" ou o tema do teto citado para remeter à jurisprudência).
- **Não pegaram 12**: `CF88:ART.37:PAR.14`, `CF88:ART.37:PAR.15`, `CF88:ART.40:CAPUT`, `CF88:ART.40:PAR.1:INC.I`, `CF88:ART.40:PAR.1:INC.II`, `CF88:ART.40:PAR.2`, `CF88:ART.40:PAR.5`, `CF88:ART.40:PAR.7`, `CF88:ART.40:PAR.9`, `CF88:ART.40:PAR.12`, `CF88:ART.40:PAR.18`, `CF88:ART.40:PAR.22`. Nesses casos o problema era de conteúdo jurídico (regra de transição e artigos da EC 103/2019, lei complementar já editada ou pendente, piso da pensão, contagem recíproca, base de contribuição do art. 149, § 1º-A): só se detecta com conhecimento externo, não por padrão de texto.

**Conclusão:** as regras aprendidas servem como **triagem** (separar o que precisa de olho humano), não como aprovação. Em 39% dos HIGH ajustados elas não teriam visto o problema. Nos MEDIUM/LOW o risco jurídico é menor, mas a taxa de erro não detectado não é zero.

## 4. Pendentes: quantos poderiam ser aprovados só com as regras aprendidas

| Classe | MEDIUM | LOW | Total |
|---|---|---|---|
| Sem nenhum alerta (regras aprendidas + lint relevante) | 10 | 5 | 15 |
| Sem regra aprendida, mas com lint relevante | 1 | 0 | 1 |
| Regra aprendida disparou | 12 | 3 | 15 |

- **Aprovação automática possível usando exclusivamente as regras aprendidas: 15** (limite superior 16, aceitando o lint).
- **Exigem nova intervenção humana: 15** (+ 1 se o lint relevante for tratado como impeditivo).
- Recomendação: não aprovar automaticamente sem amostragem. Para os candidatos, revisão humana **em lista** (aprovar/ajustar por exceção), com auditoria completa dos LOW e amostra dos MEDIUM; os HUMAN_REQUIRED vão para rodada curta com o achado já indicado.
- Caso concreto: `CF88:ART.38:INC.III` repete o padrão "soma das remunerações sujeita ao teto" que as Rodadas 01, 03A e 03B corrigiram; é o tipo de item que a regra aprendida deve barrar.

| Target | Risco | Papel | Classe | Regras aprendidas | Lint | editorial_checks (resolvidos) |
|---|---|---|---|---|---|---|
| `CF88:ART.37:INC.VIII` | LOW | ITEM | AUTO_APPROVAL_CANDIDATE | — | — | — |
| `CF88:ART.37:PAR.1` | LOW | DEVICE | AUTO_APPROVAL_CANDIDATE | — | — | — |
| `CF88:ART.37:PAR.16` | LOW | DEVICE | AUTO_APPROVAL_CANDIDATE | — | — | — |
| `CF88:ART.37:PAR.3` | LOW | BLOCK | AUTO_APPROVAL_CANDIDATE | — | — | — |
| `CF88:ART.37:PAR.8` | LOW | BLOCK | AUTO_APPROVAL_CANDIDATE | — | — | MODALITY_SHIFT:deve |
| `CF88:ART.37:INC.III` | MEDIUM | BLOCK | AUTO_APPROVAL_CANDIDATE | — | EXAMPLE_REQUIREMENT_LANGUAGE | — |
| `CF88:ART.37:INC.VI` | MEDIUM | BLOCK | AUTO_APPROVAL_CANDIDATE | — | EXAMPLE_REQUIREMENT_LANGUAGE | — |
| `CF88:ART.37:INC.XIX` | MEDIUM | BLOCK | AUTO_APPROVAL_CANDIDATE | — | EXAMPLE_REQUIREMENT_LANGUAGE | — |
| `CF88:ART.37:INC.XV` | MEDIUM | ITEM | AUTO_APPROVAL_CANDIDATE | — | — | EXAMPLE_NUMBER:10% |
| `CF88:ART.37:INC.XXI` | MEDIUM | ITEM | AUTO_APPROVAL_CANDIDATE | — | EXAMPLE_REQUIREMENT_LANGUAGE | — |
| `CF88:ART.37:PAR.2` | MEDIUM | DEVICE | AUTO_APPROVAL_CANDIDATE | — | — | — |
| `CF88:ART.38:INC.II` | MEDIUM | ITEM | AUTO_APPROVAL_CANDIDATE | — | — | — |
| `CF88:ART.39:PAR.1` | MEDIUM | BLOCK | AUTO_APPROVAL_CANDIDATE | — | — | — |
| `CF88:ART.39:PAR.3` | MEDIUM | DEVICE | AUTO_APPROVAL_CANDIDATE | — | — | — |
| `CF88:ART.39:PAR.5` | MEDIUM | BLOCK | AUTO_APPROVAL_CANDIDATE | — | — | MODALITY_SHIFT:obriga |
| `CF88:ART.37:INC.I` | MEDIUM | ITEM | AUTO_CANDIDATE_IF_LINT_ACCEPTED | — | ABSOLUTE_CLAIM, EXAMPLE_REQUIREMENT_LANGUAGE, EXAMPLE_REQUIREMENT_LANGUAGE | ABSOLUTE_CLAIM:incondicional |
| `CF88:ART.37:INC.XVIII` | LOW | BLOCK | HUMAN_REQUIRED | UNIVERSAL_CLAIM:todas as | — | — |
| `CF88:ART.37:PAR.7` | LOW | DEVICE | HUMAN_REQUIRED | TELEOLOGY_SPECULATIVE:evitar | — | — |
| `CF88:ART.39:PAR.2` | LOW | DEVICE | HUMAN_REQUIRED | UNIVERSAL_CLAIM:só pode | NEAR_COPY_OF_OFFICIAL_TEXT | — |
| `CF88:ART.37:CAPUT` | MEDIUM | DEVICE | HUMAN_REQUIRED | TELEOLOGY_SPECULATIVE:serve para; UNIVERSAL_CLAIM:todos os; UNIVERSAL_CLAIM:só pode | PARENT_REPETITION | — |
| `CF88:ART.37:INC.II` | MEDIUM | ITEM | HUMAN_REQUIRED | UNIVERSAL_CLAIM:todos os | EXAMPLE_REQUIREMENT_LANGUAGE | — |
| `CF88:ART.37:INC.IX` | MEDIUM | ITEM | HUMAN_REQUIRED | TELEOLOGY_SPECULATIVE:serve para | — | — |
| `CF88:ART.37:INC.V` | MEDIUM | ITEM | HUMAN_REQUIRED | AUTOMATIC_CONSEQUENCE:passa a receber | — | — |
| `CF88:ART.37:INC.X` | MEDIUM | ITEM | HUMAN_REQUIRED | UNIVERSAL_CLAIM:todos os | ABSOLUTE_CLAIM, EXAMPLE_REQUIREMENT_LANGUAGE, EXAMPLE_REQUIREMENT_LANGUAGE | ABSOLUTE_CLAIM:sempre |
| `CF88:ART.37:INC.XII` | MEDIUM | BLOCK | HUMAN_REQUIRED | UNIVERSAL_CLAIM:sempre; AUTOMATIC_CONSEQUENCE:automaticamente | ABSOLUTE_CLAIM, ABSOLUTE_CLAIM | ABSOLUTE_CLAIM:automaticamente |
| `CF88:ART.37:PAR.13` | MEDIUM | DEVICE | HUMAN_REQUIRED | TELEOLOGY_SPECULATIVE:evita | — | — |
| `CF88:ART.38` | MEDIUM | OVERVIEW | HUMAN_REQUIRED | UNIVERSAL_CLAIM:todos os | NEAR_COPY_OF_OFFICIAL_TEXT | TECHNICAL_TERM_UNDEFINED:economia mista |
| `CF88:ART.38:INC.I` | MEDIUM | ITEM | HUMAN_REQUIRED | AUTOMATIC_CONSEQUENCE:passa a receber | — | — |
| `CF88:ART.38:INC.III` | MEDIUM | ITEM | HUMAN_REQUIRED | JURIS_SENSITIVE_TOPIC:soma das remunerações continua sujeita ao teto | — | — |
| `CF88:ART.38:INC.IV` | MEDIUM | ITEM | HUMAN_REQUIRED | UNIVERSAL_CLAIM:todos os | — | — |
| `CF88:ART.39:PAR.7` | MEDIUM | DEVICE | HUMAN_REQUIRED | TELEOLOGY_SPECULATIVE:A ideia é; TELEOLOGY_SPECULATIVE:incentivar | NEAR_COPY_OF_OFFICIAL_TEXT | — |

## 5. Regras editoriais que podem virar validação automática

| Regra | Origem | Tipo proposto |
|---|---|---|
| Identificador interno no corpo (`CF88_RUNTIME` etc.) | Rodada 02 | **bloqueante** |
| Controvérsia tratada como aberta ("qual redação produz efeitos") | Rodada 02 | **bloqueante** com lista de frases |
| Sigla de tribunal / número de processo no corpo | T1 (já existe) | bloqueante (mantida) |
| Cópia literal > 10 palavras | T1 (já existe) | bloqueante + **sugestão automática** de microajuste (preposição/artigo), registrada como desvio da política |
| Finalidade especulativa ("objetivo é", "evita", "incentivo", "reduz custos") | Rodadas 02, 03B | alerta com resolução obrigatória |
| Generalização universal ("todos os", "só pode", "cada ente tem"), ciente de negação | Rodadas 02, 03A, 03B | alerta com resolução obrigatória |
| Consequência automática ("automaticamente", "pode ser exonerado", "busca a diferença") | Rodadas 02, 03A, 03B | alerta com resolução obrigatória |
| Tema com jurisprudência catalogada no núcleo (teto × soma/acumulação, magistério × sala de aula, paridade, regime jurídico único) | Rodadas 01, 02, 03A, 03B | alerta + **nota externa obrigatória** a partir de um catálogo de temas |
| Afirmação sobre estado de lei regulamentadora ("já foi editada", "está na camada") | Rodadas 03A, 03B | alerta + proveniência obrigatória |
| Fato externo (Lei nº, LC nº, art. de EC, Tema) sem `content_provenance` | Rodadas 01–03B | **bloqueante no fechamento da rodada** |
| Critério/mecanismo inventado no exemplo | Rodada 02 | alerta |
| Versão carimbada é imutável; aprovação só por round_approvals; desvio só com categoria da política | Rodadas 02, 03A | já automatizado (motor + testes) |

## 6. Pipeline proposto (arts. 42 em diante e, depois, outras normas)

1. **Congelar o padrão:** ENTENDA-T1 com um adendo (A6) contendo as regras acima, a política de microajustes e as regras de proveniência e versionamento. A partir daí o padrão não muda por lote.
2. **Validador v2:** levar ao motor os bloqueantes novos e, ao `editorial_checks`, as regras aprendidas como alertas que exigem resolução; manter o teste de precisão/cobertura contra as decisões humanas já registradas (este diagnóstico vira teste de regressão das regras).
3. **Catálogo de temas externos como dado:** tema → nota da camada externa + proveniência (Temas 377/384/359/965, ADI 2.135/3.772, LC 152/2015, EC 103/2019 arts. 6º/7º/9º/13). O gerador insere a nota e o validador exige que o corpo remeta à camada externa, sem resolver a controvérsia.
4. **Redação dos drafts** com o checklist das regras aprendidas embutido (sem finalidade especulativa, sem universal, sem consequência automática, sem estado de lei sem fonte).
5. **Triagem automática em três filas:** (a) sem alerta → revisão humana em lista, aprovação por exceção, com amostragem; (b) alerta de regra aprendida → rodada curta com o achado indicado; (c) HIGH por tema (previdência, remuneração, estabilidade, temas catalogados) → rodada completa como as deste lote.
6. **Microajustes T1 automáticos:** o próprio pipeline aplica e registra os desvios da política (preposição/artigo, sigla por extenso, glossário acima de 5), com o teste que prova "só adaptação T1".
7. **Lotes maiores:** com as filas (a)/(b), o lote pode passar dos ~70 itens atuais sem aumentar a revisão artesanal; manter determinismo (3 builds idênticos) e os testes por lote.
8. **Outras normas:** mesma esteira, com runtime aprovado de cada norma como autoridade textual e um catálogo de temas por norma; começar por uma norma curta para calibrar a precisão das regras fora da CF.
9. **Medir a cada lote:** % de ajuste humano, cobertura e falsos positivos das regras, desvios T1 por item. Se a cobertura cair abaixo do nível atual, voltar a rodadas completas.

## 7. Não feito nesta etapa

- Nenhum MEDIUM/LOW alterado, aprovado ou reclassificado; nenhuma regra nova entrou no motor ou no `editorial_checks`; nenhum Batch06; sem staging, commit, tag ou push.
