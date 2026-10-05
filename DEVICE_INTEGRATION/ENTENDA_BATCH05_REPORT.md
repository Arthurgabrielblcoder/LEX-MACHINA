# LEX_ENTENDA_BATCH05_CF_ART37_41 — relatório

**Data:** 2026-10-04.

**Baseline:** commit `1754186824c29a95c5b05cf4ea77b2a910eb2da9` / tag `lex-device-v1-context-citation-guard-approved-2026-10-04`.

**Estado:** `ENTENDA_BATCH05_DRAFT_READY`:
- 69 drafts T1 em `PENDING_HUMAN_REVIEW`, todos `READY_FOR_EDITORIAL_REVIEW`;
- **nenhuma** aprovação humana registrada;
- sem flash, SD, commit, tag ou push.

## 1. Base textual

**Autoridade:** o `CF88_RUNTIME` aprovado. `DEVICE_INTEGRATION/runtime/CF88_RUNTIME.txt`, SHA-256 `7ef82290…`, é idêntico ao `/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt`
do baseline físico.

**Texto por target:** o texto do motor ENTENDA (fonte operacional configurada) é igual ao do runtime em **113/113** dispositivos vigentes
com texto próprio.

**Lei Seca:** não alterada.

**Fonte estrutural canônica:** o compilado `cf.txt` do Catálogo Mestre, já existente no projeto. Foi usado **somente** para confirmar a
origem das redações citadas (anotações "Redação dada / Incluído pela EC…"). Não houve pesquisa web nem jurisprudência nova, e o RUN3
não foi alterado.

**Achados de vigência e redação** (`BATCH05_TARGET_PLAN.json`):

| Dispositivo | Achado |
|---|---|
| Art. 37, XVI, "b" | Redação da **EC 138/2025**: "professor com outro **de qualquer natureza**". Materiais antigos dizem "técnico ou científico". O primeiro rascunho, feito de memória, estava errado e foi corrigido pelo runtime. |
| Art. 37, § 11 | O texto oficial remete ao art. 3º da EC 135/2024. O conteúdo dessa disposição fica na ATENÇÃO e na camada externa, sem ser afirmado. |
| Art. 37, §§ 14 e 15 / art. 39, § 9º | Incluídos pela EC 103/2019. |
| Art. 37, § 16 | Incluído pela EC 109/2021. |
| Art. 39, caput | Redação da EC 19/1998, com "Vide ADI nº 2.135" e a redação original sobre regime jurídico único na fonte canônica. **A controvérsia não é resolvida no corpo**: vai para a ATENÇÃO e para a camada JURISPRUDÊNCIA. |
| Art. 40 | Caput e a maioria dos parágrafos com redação da EC 103/2019; §§ 8, 17 e 18 da EC 41/2003; §§ 10, 11 e 16 da EC 20/1998. Regras de transição ficam fora do núcleo da explicação. |
| Art. 41 | Redação da EC 19/1998. |

## 2. Targets estruturais e granularidade

| | Total |
|---|---|
| Targets estruturais | 133 |
| Vigentes | 118 |
| Históricos (`EXCLUDED_HISTORICAL`) | 14: caput do art. 40, I–III e alíneas; § 1º, III, "a" e "b"; § 4º, I–III; § 7º, I–II |
| Revogados (`EXCLUDED_REVOKED`) | 1: art. 40, § 21 |

| Classificação | Quantidade |
|---|---|
| OVERVIEW | 5 (um por artigo; o do art. 37 é o piloto aprovado) |
| DEVICE | 32 (2 deles pilotos aprovados: art. 37, §§ 6º e 10) |
| BLOCK_CANDIDATE → BLOCK | 18: 13 cobrem 17 irmãos; 6 têm subdivisões próprias (o inciso XVI do art. 37 tem as duas coisas) |
| ITEM_CANDIDATE → ITEM | 17 |
| SKIP → NO_SEPARATE_EXPLANATION | 46: 25 subdivisões de blocos, 17 irmãos cobertos, 4 por visão geral (3 caputs e o art. 40, § 1º) |

**Explicações por artigo:**

| Artigo | Explicações | Novas | Reutilizadas |
|---|---|---|---|
| Art. 37 | 31 | 28 | 3 (art. 37, § 6º, § 10) |
| Art. 38 | 6 | 6 | — |
| Art. 39 | 8 | 8 | — |
| Art. 40 | 22 | 22 | — |
| Art. 41 | 5 | 5 | — |

**Total do Batch05:** 72 explicações (69 novas + 3 aprovadas reutilizadas).

**Total ENTENDA projetado após aprovação:** 220 + 69 = **289** explicações (448 linhas de lookup).

**Por que 69 e não 50–65:** o art. 37 tem 49 dispositivos e o art. 40 tem 39 vigentes. Mesmo com 18 blocos, separar concurso, teto,
acumulação, licitação, improbidade e prescrição, e cada hipótese de aposentadoria, piso/teto, pensão, acumulação de benefícios,
contribuição de inativos, abono e previdência complementar, exige explicações próprias. A justificativa está registrada no
`BATCH_SPEC.json` (`OUTSIDE_JUSTIFIED`; teto de 70).

**Blocos de destaque:**

| Bloco | Conteúdo |
|---|---|
| Art. 37, III+IV | validade e prioridade |
| Art. 37, VI+VII | sindicalização e greve |
| Art. 37, XII+XIII+XIV | vedações remuneratórias |
| Art. 37, XVI (+XVII e alíneas) | acumulação |
| Art. 37, XVIII+XXII | administração tributária |
| Art. 37, XIX+XX | criação de entidades |
| Art. 37, §§ 9º, 11 e 12 | alcance do teto |
| Art. 39, §§ 4º+8º | subsídio |
| Art. 39, §§ 5º+6º | relação de remunerações e publicação |
| Art. 40, §§ 3º+17 | cálculo e atualização |
| Art. 40, §§ 4º-A/B/C | critérios diferenciados |
| Art. 40, §§ 9º+10 | contagem de tempo |
| Art. 40, §§ 14–16 | previdência complementar |
| Art. 40, § 22 e incisos | vedação de novos regimes próprios |
| Art. 41, § 1º e incisos | perda do cargo |

## 3. Drafts

**Arquivo:** `ENTENDA_ENGINE/derived/production_batch_05/BATCH_05_DRAFTS.json`.

**Campos de cada draft:** `target_id`, `role`, `semantic_autonomy`, `selection_criteria`, `display_topic`, `editorial_reason`,
`content` (O QUE DIZ / O QUE SIGNIFICA / EXEMPLO PRÁTICO / ATENÇÃO / PALAVRAS DIFÍCEIS), `external_layer_notes` e `covered_targets` (nos blocos).

**Metadados do corpus** (`CF88_BATCH_05.entenda.jsonl`): `status=ACTIVE`, `review_status=PENDING_HUMAN_REVIEW`,
`template_version=ENTENDA-T1`, `editorial_version=1`, snapshot e hash do texto oficial.

**Tamanho:** 243 palavras em média e 2.042 B de payload por explicação. A maior é a visão geral do art. 40 (3.075 B; limite 6.144).

**Contrato do motor:** o validador (`validate_corpus`) passou com 0 erros. Isso cobre:
- cópia literal (no máximo 10 palavras seguidas);
- similaridade com o pai (no máximo 0,35);
- faixa de palavras;
- ausência de jurisprudência no corpo;
- cobertura e contexto;
- vigência.

## 4. Checagens editoriais

**Ferramenta:** `ENTENDA_ENGINE/editorial_checks.py`. Ela não reescreve conteúdo nem muda status.

**Verificações:**
- extrapolação numérica;
- número em exemplo;
- exceção ausente do texto;
- termos absolutos;
- transição no núcleo da explicação;
- duplicação no lote;
- inconsistência factual (8 regras: estabilidade em três anos, validade de até dois anos, idades 62/65, compulsória 70/75, subteto de 90,25%, escolas de governo sem Municípios, redação vigente da alínea "b", disponibilidade proporcional);
- termo técnico sem definição;
- frase longa;
- troca de modalidade (permissão lida como obrigação);
- dependência de lei omitida.

**Resultado final:** 18 achados, todos com resolução registrada em `EDITORIAL_REVIEW_INPUT.json`. Não há achado sem resolução.

**Inconsistências encontradas e drafts corrigidos.** Foi a rodada editorial 0, antes de qualquer revisão humana. As 34 explicações
afetadas continuam na versão 1, porque nenhuma versão havia sido revisada.

| # | Problema | Correção |
|---|---|---|
| 1 | Art. 37, XVI, "b": "técnico ou científico" (memória) ≠ runtime | Texto vigente, com a origem na EC 138/2025 citada |
| 2 | Art. 39, ATENÇÃO afirmava "o caput não menciona regime jurídico único" (resolveria a controvérsia) | Reescrita sem resolver; ADI 2.135 só na camada externa |
| 3 | Art. 40, § 18: "incide só sobre a parcela excedente" (mais que o texto) | Leitura apresentada como usual, mais o art. 149, § 1º-A (runtime) |
| 4 | Art. 40, § 14: "contribuições do ente" (fora do texto) | Removido |
| 5 | Art. 40, § 22: "antes, cada ente podia criar" (afirmação histórica de memória) | Removido |
| 6 | Exemplos do art. 40, §§ 2º e 14 duplicados (similaridade 0,40) | Exemplo do § 2º reescrito (piso) |
| 7 | Art. 37, § 15: "situação de transição" no núcleo da explicação | Reformulado |
| 8 | 11 trechos com mais de 10 palavras do texto oficial (bloqueio do validador) | Parafraseados |
| 9 | Caput do art. 37 parecido com a visão geral aprovada (0,415) | Reescrito (0,25) |
| 10 | 21 termos técnicos sem definição, em 16 explicações (regra A5) | Definições uniformes adicionadas |
| 11 | Afirmações absolutas desnecessárias ("sempre", "para sempre", "automaticamente") | Removidas |

**Avisos de lint restantes** (não bloqueiam; decisão do revisor):
- 15 `EXAMPLE_REQUIREMENT_LANGUAGE`: exemplos que descrevem a regra do próprio texto;
- 20 `NEAR_COPY_OF_OFFICIAL_TEXT`, de 8 a 10 palavras: nomes técnicos e listas;
- 4 `ABSOLUTE_CLAIM` (negações ou descrição da regra proibida), 1 `PARENT_REPETITION` (0,25) e 2 `LONG_EXPLANATION`;
- 1 `TERM_LOW_UTILITY`, no piloto aprovado e não alterado.

## 5. Risco editorial

`REVIEW_BATCH_05_RISK_TRIAGE.md` e `EDITORIAL_CHECKS.json`:

| Risco | Qtde | Exemplos |
|---|---|---|
| HIGH | 38 | todo o art. 40 (22), todo o art. 41 (5); art. 37: XI, XVI, §§ 4º, 5º, 9º, 14, 15; art. 38, V; art. 39: caput, §§ 4º e 9º |
| MEDIUM | 23 | concurso, validade, cargos em comissão, greve, temporários, remuneração, irredutibilidade, licitação, criação de entidades, art. 38, I–IV |
| LOW | 8 | reserva de vagas, administração tributária, publicidade, participação do usuário, informações privilegiadas, contrato de desempenho, avaliação de políticas, escolas de governo |

**Estado editorial:**
- `READY_FOR_EDITORIAL_REVIEW`: 69;
- `HUMAN_APPROVED_T1`: 0.

**Revisão assistida:** o mecanismo `ASSISTED_RISK_BASED_HUMAN_REVIEW` do Batch04 exige um revisor autorizado por Arthur, registrado em
`ROUND_*_HUMAN_REVIEW_DECISIONS.json`. Ele **não foi usado** nesta missão. A aprovação fica para a revisão editorial.

## 6. Determinismo e staging host

**Artefatos do lote:** 3 gerações do zero, só a partir das 3 entradas (`BATCH_SPEC`, `BATCH_05_DRAFTS`, `EDITORIAL_REVIEW_INPUT`),
produziram **BYTE_IDENTICAL** os 9 artefatos gerados:
- corpus, seleção, recomendações, folha de revisão;
- checagens, triagem;
- lookup, payload, manifesto.

Todos iguais aos do diretório do lote.

**Staging host:** `DEVICE_INTEGRATION/staging_entenda_batch05_candidate/` (`tools/build_entenda_batch05_candidate.py`).

| Campo | Valor |
|---|---|
| Status | `HOST_CANDIDATE_NOT_DEPLOYABLE`. O builder físico recusa explicações pendentes. |
| Base aprovada | `build_sd_staging.approved_entenda` (220 `HUMAN_APPROVED_T1`) + 69 pendentes = 289 |
| `ENTENDA_LOOKUP.IDX` | 448 linhas (362 aprovadas + 86 pendentes); 48.020 B, `7112f9da…` |
| `ENTENDA_PAYLOAD.DAT` | 547.539 B, `6a306bbf…` |
| Rebuilds | 3, **BYTE_IDENTICAL** |
| Preservação | as 362 linhas aprovadas mantêm a mesma linha (exceto OFFSET) e o mesmo bloco de payload que o par físico aprovado (`staging_sd_v1_batch04_run3_candidate`, lookup `3014442e…`, payload `4efa5478…`, intocados); 0 removidas, 0 alteradas, 86 adicionadas = exatamente os targets do Batch05 |

**Par físico:** `ENTENDA_LOOKUP/PAYLOAD` físico não substituído.

## 7. Testes

**Novo:** `ENTENDA_ENGINE/tests/test_entenda_batch05.py`, 19 testes:
- escopo e contagens;
- nenhuma aprovação inventada;
- classificação por artigo;
- pilotos reutilizados sem duplicação;
- runtime como autoridade (snapshot igual ao runtime em cada target);
- contrato do motor e ausência de jurisprudência;
- art. 37: caput, concurso, validade e prioridade, acumulação com a redação vigente, teto, § 5º e § 6º;
- art. 38, art. 39 (caput complexo não resolvido), art. 40 (permanente × transição, idades, blocos, § 18), art. 41;
- duplicação, risco, lookup e cobertura;
- 3 builds byte-idênticos;
- staging host preservando o par aprovado.

| Suíte | Resultado |
|---|---|
| DEVICE | 353/353 |
| ENTENDA | 116/116 (97 + 19) |
| LEGAL_TARGET_ID | 65/65 |
| RUN3 / Batch04 consolidação | 25/25 |
| Full corpus indexes | 17/17 |
| MARIA2006 | 9/9 |
| Context citation guard | 26/26 |
| Busca indexada / milhares / scroll / next occurrence / REPEAT_READY / FD | 20/20 · 19/19 · 25/25 · 16/16 · 16/16 · 11/11 |
| Updater | 113/116 (3 ERROR ambientais: `truststore`) |

**FAIL_REAL = 0.**

## 8. Arquivos

**Novos:**
- `ENTENDA_ENGINE/derived/production_batch_05/`:
  - `BATCH_SPEC.json`, `BATCH_05_DRAFTS.json`, `CF88_BATCH_05.entenda.jsonl`;
  - `SELECTION_REPORT.json`, `REVIEW_BATCH_05.md`, `JURISPRUDENCE_LINK_RECOMMENDATIONS.json` (0 recomendações);
  - `EDITORIAL_REVIEW_INPUT.json`, `EDITORIAL_CHECKS.json`, `REVIEW_BATCH_05_RISK_TRIAGE.md`, `BATCH05_TARGET_PLAN.json`;
  - `index/`.
- `ENTENDA_ENGINE/editorial_checks.py`.
- `ENTENDA_ENGINE/tests/test_entenda_batch05.py`.
- `DEVICE_INTEGRATION/tools/build_entenda_batch05_candidate.py`.
- `DEVICE_INTEGRATION/staging_entenda_batch05_candidate/`.

**Alterados:** nenhum arquivo versionado.

**Não tocados:** firmware, SD, índices, catálogo, Batches 01–04, pilotos, RUN3, runtime.

## 9. Revisão editorial assistida

**Rodada 01, art. 37, HIGH:** `ROUND01_ART37_HIGH_HUMAN_APPROVED`, 7 de 7.

**Revisor:** `ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW`, escopo `CF88_ART37_HIGH_ROUND_1`.

| Situação | Itens | Status |
|---|---|---|
| Aprovado sem alteração | § 5º | v1 |
| Aprovados após ajuste e verificação final | XI, XVI, §§ 4º, 9º, 14 e 15 | v2; as v1 ficam `RETIRED` / `CHANGES_REQUESTED` |

**Desvios do texto do revisor:** 8, mínimos, exigidos pelo padrão T1 e confirmados pelo revisor.

**Proveniência das informações externas** trazidas pela revisão: `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`.

**Arquivos:**
- `BATCH_05_DRAFTS_PRE_ROUND1.json`;
- `ROUND_1_HUMAN_REVIEW_DECISIONS.json`;
- `ROUND_1_EDITORIAL_ADJUSTMENTS.json`;
- `ENTENDA_BATCH05_REVIEW_ROUND01_DIFF.md`.

**Estado do lote:**
- `HUMAN_APPROVED_T1`: 10 (3 pilotos + 7);
- `PENDING_HUMAN_REVIEW`: 62;
- editorial_checks: 0 achados sem resolução.

**Staging host:** não regenerado. O candidato de 2026-10-04 reflete o estado anterior à rodada.

**Rodada 02, arts. 38, 39 e 41, HIGH:** `ROUND02_ART38_39_41_HIGH_HUMAN_APPROVED`, 9 de 9 (verificação final em 2026-10-04).

**Revisor:** `ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW`, escopo `CF88_ART38_39_41_HIGH_ROUND_2`.

| Situação | Itens | Status |
|---|---|---|
| Aprovados sem alteração | art. 41 §§ 1º (BLOCK, incisos I–III) e 3º | `HUMAN_APPROVED_T1`, v1 |
| Aprovados após ajuste e verificação final | art. 38 V; art. 39 §§ 4º e 9º; art. 41 (visão geral), §§ 2º e 4º | `HUMAN_APPROVED_T1`, v2; as v1 ficam `RETIRED` / `CHANGES_REQUESTED` |
| Aprovado após ajuste e edição da verificação final | art. 39 (visão geral) | `HUMAN_APPROVED_T1`, v3; v1 e v2 ficam `RETIRED` / `CHANGES_REQUESTED` |

**Desvios do texto do revisor:** 1, confirmado (art. 39, O QUE DIZ: "integrado" → "composto", contra cópia literal de 16 palavras do caput).

**Edição da verificação final:** art. 39, ATENÇÃO, retirado o identificador interno "CF88_RUNTIME" do corpo visível, com o texto do revisor ("…que corresponde ao texto constitucional vigente utilizado neste aplicativo."). Como a v2 já estava carimbada e o motor não permite mudar o conteúdo de uma versão carimbada, a edição gerou a v3. Pela regra do motor, `superseded_by` de v1 e v2 aponta para a versão vigente (v3); a cadeia v1 → v2 → v3 está em `ROUND_2_EDITORIAL_ADJUSTMENTS.json` (`version_history`).

**Proveniência** `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`: resultado da ADI nº 2.135 (art. 39 caput) e art. 13 da EC 103/2019 (art. 39 § 9º). Número da ADI só na camada externa.

**Arquivos:**
- `BATCH_05_DRAFTS_PRE_ROUND2.json`;
- `ROUND_2_HUMAN_REVIEW_DECISIONS.json`;
- `ROUND_2_EDITORIAL_ADJUSTMENTS.json`;
- `ENTENDA_BATCH05_REVIEW_ROUND02_DIFF.md`.

**Rodada 03A, art. 40 (1ª metade), HIGH:** `ROUND03A_ART40_HIGH_HUMAN_APPROVED`, 11 de 11.

**Revisor:** `ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW`, escopo `CF88_ART40_HIGH_ROUND_3A`. A revisão pré-autorizou uma **política de microajustes T1** (siglas por extenso; troca de artigo/preposição/ordem/sinônimo contra cópia literal; remoção de termo redundante acima de 5; ajuste gramatical exigido pelo validador; troca de identificador interno), com significado jurídico idêntico, registro de cada desvio e prova por teste. Mudança jurídica ou factual exigida pelo validador teria parado a aplicação; não houve.

| Situação | Itens | Status |
|---|---|---|
| Aprovados sem alteração | §§ 3º/17 (BLOCK), § 1º III, §§ 4º-A–4º-C (BLOCK) | `HUMAN_APPROVED_T1`, v1 |
| Aprovados após ajuste, sob a política pré-autorizada | visão geral, caput, §§ 2º, 4º, 5º e 6º, § 1º I e II | `HUMAN_APPROVED_T1`, v2; as v1 ficam `RETIRED` / `CHANGES_REQUESTED` |

**Desvios do texto do revisor:** 2, ambos do item 2 da política (preposição contra cópia literal): visão geral, "dos servidores" → "para os servidores"; § 5º, "exercício das funções" → "exercício nas funções".

**Texto quebrado em linhas:** a revisão chegou com quebras a ~60 colunas. O texto foi guardado como recebido e convertido por regra determinística (parágrafo só após ". : ;" seguido de início de frase), conferida por teste.

**Proveniência** `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`: "nem todo ente possui RPPS" (visão geral), Tema 965 / ADI 3.772 (§ 5º, camada externa), LC 152/2015 (§ 1º II, corpo e camada externa), Temas 377/384 (§ 6º, camada externa).

**Arquivos:**
- `BATCH_05_DRAFTS_PRE_ROUND3A.json`;
- `ROUND_3A_HUMAN_REVIEW_DECISIONS.json`;
- `ROUND_3A_EDITORIAL_ADJUSTMENTS.json`;
- `ENTENDA_BATCH05_REVIEW_ROUND03A_DIFF.md`.

**Estado do lote:**
- `HUMAN_APPROVED_T1`: 30 (3 pilotos + 7 da Rodada 01 + 9 da Rodada 02 + 11 da Rodada 03A);
- `PENDING_HUMAN_REVIEW`: 42;
- versões `RETIRED`: 22;
- editorial_checks: 0 achados sem resolução;
- testes: `test_entenda_batch05` 22/22 (3 builds idênticos byte a byte), ENTENDA 119/119;
- hash do runtime (Lei Seca) inalterado: `7ef82290…`.

**Staging host:** não regenerado.

**Rodada 03B, art. 40 (2ª metade), HIGH:** `ROUND03B_ART40_HIGH_HUMAN_APPROVED`, 11 de 11. Última rodada HIGH: **`BATCH05_HIGH_REVIEW_COMPLETE`, 38 de 38 HIGH aprovados.**

**Revisor:** `ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW`, escopo `CF88_ART40_HIGH_ROUND_3B`, com a política de microajustes T1 da 03A.

| Situação | Itens | Status |
|---|---|---|
| Aprovado sem alteração | § 8º | `HUMAN_APPROVED_T1`, v1 |
| Aprovados após ajuste, sob a política pré-autorizada | §§ 7º, 9º/10 (BLOCK), 11, 12, 13, 14–16 (BLOCK), 18, 19, 20, 22 (BLOCK) | `HUMAN_APPROVED_T1`, v2; as v1 ficam `RETIRED` / `CHANGES_REQUESTED` |

**Desvio do texto do revisor:** 1, item 2 da política (§ 7º, "decorrente de agressão" → "decorrente da agressão", contra cópia literal de 11 palavras).

**BLOCK do § 22:** confirmado. Os incisos I–X são subdivisões do próprio § 22 e ficam cobertos como `BLOCK_SUBDIVISION`, o mesmo mecanismo do art. 41, § 1º. `covered_targets` é só para irmãos estruturais (o motor rejeita filhos nesse campo), por isso os incisos não foram listados ali; o teste confere os 10.

**Camada externa:** § 11 com Temas 377/384 e 359; § 22 sem a nota antiga que sugeria a lei complementar já editada, agora com o art. 9º da EC 103/2019 e a Lei nº 9.717/1998; §§ 14–16 com nota do marco de instituição; § 18 com "Art. 149, § 1º-A.". Proveniência `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE` nos §§ 11, 14–16, 18 e 22.

**Arquivos:** `BATCH_05_DRAFTS_PRE_ROUND3B.json`, `ROUND_3B_HUMAN_REVIEW_DECISIONS.json`, `ROUND_3B_EDITORIAL_ADJUSTMENTS.json`, `ENTENDA_BATCH05_REVIEW_ROUND03B_DIFF.md`.

**Estado do lote após a 03B:**
- `HUMAN_APPROVED_T1`: 41 (3 pilotos + 38 HIGH);
- `PENDING_HUMAN_REVIEW`: 31 (23 MEDIUM, 8 LOW);
- versões `RETIRED`: 32;
- editorial_checks: 0 achados sem resolução;
- testes: `test_entenda_batch05` 23/23 (3 builds idênticos byte a byte), ENTENDA 120/120;
- hash do runtime (Lei Seca) inalterado: `7ef82290…`.

**Staging host:** não regenerado.

## 10. Próximo passo

**Etapa `T1_EDITORIAL_STANDARD_FREEZE_AND_SCALE`.** Diagnóstico preparado em `ENTENDA_ENGINE/derived/production_batch_05/T1_FREEZE_AND_SCALE_DIAGNOSTIC.md` (e `.json`), somente leitura: totais, alertas nos 31 MEDIUM/LOW, avaliação das regras aprendidas contra as decisões humanas, quantos pendentes seriam candidatos a aprovação automática, regras que podem virar validação e pipeline para os arts. 42 em diante e outras normas.

Sem revisão artesanal dos MEDIUM/LOW, sem Batch06 no modelo antigo, sem staging, commit, tag ou push até nova decisão.

## 11. T1_EDITORIAL_STANDARD_FREEZE_AND_SCALE (2026-10-04)

**`T1_EDITORIAL_STANDARD_FROZEN`.** O padrão aprendido nas Rodadas 01–03B virou infraestrutura host-side. Nenhum pendente foi alterado, aprovado ou versionado.

**Artefatos:**
- `ENTENDA_ENGINE/ENTENDA_T1_EDITORIAL_STANDARD_A6.md` — adendo A6. Único arquivo versionado tocado: `ENTENDA_T1_EDITORIAL_STANDARD.md` ganhou a seção 16, que remete ao A6.
- `ENTENDA_ENGINE/t1_validator_v2.py` — validador v2 (camada sobre motor e `editorial_checks`; não reescreve, não aprova).
- `ENTENDA_ENGINE/t1_triage.py` — regressão contra as decisões humanas e triagem em filas A–E.
- `ENTENDA_ENGINE/editorial/T1_EXTERNAL_CATALOG.json` — 12 entradas, só as usadas nas rodadas.
- `ENTENDA_ENGINE/editorial/T1_KNOWN_RESOLUTIONS.json` — 5 resoluções por versão carimbada.
- `ENTENDA_ENGINE/editorial/T1_PIPELINE_CONFIG.json` — `AUTO_APPROVE_LOW=false`, `AUTO_APPROVE_MEDIUM=false`, `MICROAUTO_APPLY=false`.
- `ENTENDA_ENGINE/tests/test_t1_validator_v2.py` — 13 testes.
- `ENTENDA_ENGINE/T1_SCALE_PIPELINE_PROPOSAL.md`.
- No lote: `T1_PENDING_TRIAGE.json`, `T1_PENDING_TRIAGE_REPORT.md`, `T1_QUEUE_D_FULL_REVIEW.md`, `T1_VALIDATOR_V2_REGRESSION.json`.

**Desempenho do validador v2 contra as decisões humanas:**
- v1 com CHANGES_REQUESTED: 28 de 31 detectadas (24 por regra generalizável, 4 só por memória de target catalogado).
- Falsos negativos conhecidos (3, documentados): art. 37 § 9º, art. 40 caput, art. 40 § 9º.
- v1 aprovadas sem alteração: 2 de 7 disparam; são falsos positivos e foram registrados.
- 38 textos finais aprovados: 0 alertas pendentes após resoluções, 0 `HARD_FAIL`.
- Pilotos e acervo anterior (220): 0 `HARD_FAIL`.

**Triagem dos 31 pendentes (só classificação):**

| Fila | LOW | MEDIUM | Total |
|---|---|---|---|
| A — CLEAN_LOW | 5 | — | 5 |
| B — CLEAN_MEDIUM | — | 15 | 15 |
| C — QUICK_REVIEW | 2 | 7 | 9 |
| D — FULL_HUMAN_REVIEW | 1 | 1 | 2 |
| E — HARD_FAIL | 0 | 0 | 0 |

D: `CF88:ART.38:INC.III` ("soma … sujeita ao teto", contra os Temas 377/384) e `CF88:ART.37:PAR.7` (afirmação sobre estado de lei externa). Volume apresentado ao revisor: 85.155 → 21.751 caracteres (−74,5%).

**Testes:** ENTENDA 133/133 (120 + 13 novos), LEGAL_TARGET_ID 65/65, DEVICE 353/353; editorial_checks 0 sem resolução; builds e triagem determinísticos; Lei Seca intacta.

**Calibração humana (preparada):** `T1_PENDING_TRIAGE_HUMAN_CALIBRATION.md`, um único pacote com 36.970 caracteres (−56,6% frente ao pacote completo de 85.155). Formato por fila:
- A: T1 integral dos 5 LOW;
- B: fichas compactas, com o parágrafo exato quando há termo sensível;
- C: só o trecho, o contexto e a leitura do validador (provável problema / provável falso positivo / indeterminado);
- D: pacote completo dos 2 itens.

Em `CF88:ART.37:PAR.7`, a afirmação sobre a lei de conflito de interesses ficou marcada `EXTERNAL_VERIFICATION_REQUIRED`: o draft não nomeia a lei, e o corpus local só traz a citação da Lei nº 12.813/2013 feita pela Lei 13.848/2019.

`T1_LEGACY_AUDIT_BACKLOG.md` registra os 45 alertas do acervo anterior, com prioridade para art. 7º I e art. 5º LXXI. Não bloqueia o Batch05 e nada foi alterado.

## 12. Fila D da triagem resolvida (2026-10-04)

**`BATCH05_FULL_HUMAN_REVIEW_QUEUE_D_RESOLVED` — 2 de 2.** Escopo `CF88_BATCH05_TRIAGE_QUEUE_D`. Os 2 itens foram ajustados, ganharam v2 e estão `HUMAN_APPROVED_T1`; as v1 ficaram `RETIRED` / `CHANGES_REQUESTED`.

- **`CF88:ART.38:INC.III`:** na ATENÇÃO, só a frase "A soma das remunerações continua sujeita ao teto do art. 37, XI." foi trocada por "A forma de incidência do teto remuneratório nessa combinação não deve ser deduzida apenas da leitura deste inciso e pertence à camada de JURISPRUDÊNCIA."
  - A 1ª frase, que já dizia que cargo e mandato podem ser exercidos ao mesmo tempo com compatibilidade de horários, foi mantida.
  - Camada externa: Temas 377/384 como jurisprudência relevante, sem afirmá-los como precedente sobre mandato de Vereador. Proveniência `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`.
- **`CF88:ART.37:PAR.7`:** o corpo não mudou. A camada externa passou a ser "No âmbito do Poder Executivo federal, a Lei nº 12.813/2013 disciplina conflito de interesses…".
  - Proveniência `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`, com o registro da relação do Relations Engine.
  - A finalidade "quer evitar o conflito de interesses" foi mantida como resolução registrada, sujeita a veto humano.

**Divergência registrada.** A relação local CF88 37 § 7º → `EXT_LEI12813_2013` existe, mas só em `LEX-MACHINAETAPA_2D4/.../QUARENTENA_2D3_PRESERVADA.json`, como:
- classe `C_EXTERNA_PENDENTE_VALIDACAO`;
- decisão `OCULTAR_ATE_VALIDAR_VIGENCIA`;
- vigência `NAO_LOCALIZADA`.

Ela não aparece nas relações exibíveis (2D4/2D5), no catálogo global 2E4 nem no export RUN3. A aprovação do § 7º apoia-se na proveniência da revisão humana com fonte oficial, não na relação.

**Resolvedor externo** (`t1_external_resolver.py`, configurado em `T1_PIPELINE_CONFIG.json`). Consulta, em ordem:
1. catálogo T1;
2. relações validadas (A/B + EXIBIR, ou status ATUAL no catálogo global);
3. texto local;
4. proveniência do ENTENDA.

Se nada disso existir, o resultado é `EXTERNAL_EVIDENCE_LOCAL_PENDING` (só relação pendente) ou `EXTERNAL_VERIFICATION_REQUIRED` (nada). Relação fraca ou pendente não basta, e há testes para isso.

Para o § 7º: a v1 resulta em `EXTERNAL_EVIDENCE_LOCAL_PENDING` (relação encontrada, mas em quarentena); a v2 resulta em `EXTERNAL_EVIDENCE_AVAILABLE`, pela proveniência humana. Catálogo externo: + `LEI_12813_2013` (13 entradas).

**Estado:**
- 43 `HUMAN_APPROVED_T1` (3 pilotos + 38 HIGH + 2 da fila D);
- 29 pendentes: A 5, B 15, C 9, D 0, E 0, com os mesmos membros de antes em A, B e C;
- 34 versões `RETIRED`;
- autoaprovação OFF;
- testes: ENTENDA 137/137, LEGAL_TARGET_ID 65/65, DEVICE 353/353;
- Lei Seca e Rodadas HIGH intactas.

**Próximo passo:** revisão humana da triagem (para confirmar A/B) e decisão sobre a ativação gradual. Depois, fechamento do Batch05 e Batch06 = arts. 42–75 no novo pipeline (`T1_SCALE_PIPELINE_PROPOSAL.md`).

## 13. Revisão final calibrada dos 29 pendentes (2026-10-04)

**`BATCH05_ENTENDA_HUMAN_REVIEW_COMPLETE` — 69 de 69.** Detalhes, números e lições em `ENTENDA_BATCH05_FINAL_REPORT.md`.

- 72/72 entradas do lote aprovadas; 0 pendentes; 46 versões `RETIRED`.
- Candidato host: 289 `HUMAN_APPROVED_T1`, sem staging físico.
- Art. 37, § 7º, em v3 (finalidade não declarada retirada).
- Três regras novas no validador v2.
- Autoaprovação OFF.
