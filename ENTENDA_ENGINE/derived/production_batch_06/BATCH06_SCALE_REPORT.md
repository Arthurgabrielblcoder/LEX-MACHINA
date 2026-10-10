# ENTENDA_CF_PRODUCTION_BATCH_06 — relatório de escala (recalibração de risco)

Data de referência: 2026-10-04 · gerado por `ENTENDA_ENGINE/build_entenda_batch06_candidate.py` (determinístico, só conteúdo versionado) · **FECHADO: revisão jurídica humana concluída para todas as explicações novas do lote** (93/93 aprovadas após revisão humana; 0 pendências; os 3 pilotos reutilizados já estavam aprovados). AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY permaneceram OFF.

## Seleção

| | |
|---|---|
| Targets analisados | 318 (309 vigentes + 9 históricos excluídos) |
| SELECT | 96 = 93 explicações novas + 3 pilotos reutilizados |
| SKIP | 213 (todos com motivo e explicação que os cobre) |
| Sub-blocos (vigentes / novas / reutilizadas / SKIP) | A 17/5/0/12 · B 153/44/0/109 · C 92/25/3/64 · D 47/19/0/28 |
| Papéis das novas | BLOCK 25, DEVICE 25, ITEM 10, OVERVIEW 33 |

## Dois eixos

- **LEGAL_RISK** — há risco real de interpretação jurídica incorreta?
- **VERIFICATION_COMPLEXITY** — quão difícil é verificar o draft deterministicamente?
Número, percentual, prazo, idade, votos, quórum, BLOCK, lista, artigo longo, remissão simples, dependência de lei e emenda constitucional elevam só a complexidade.

### Estado atual das pendências

Nenhuma explicação nova pendente. As tabelas desta subseção contam só itens ainda pendentes; por isso estão zeradas. A classificação que as explicações tiveram está em “Histórico da triagem”.

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 0 | | SIMPLE | 0 |
| MEDIUM | 0 | | STRUCTURED | 0 |
| HIGH | 0 | | EXTERNAL | 0 |

Jurisprudência (pendentes): nenhum item pendente (CONTEXT_ONLY não gera D; REQUIRED_FOR_CORRECTNESS é gatilho de D).

### Histórico da triagem

Fonte: `BATCH06_TRIAGE_PRE_ROUND_D.json` (triagem recalibrada versionada, congelada antes da primeira rodada humana; 93 explicações novas pendentes). Não é reconstruída da triagem atual.

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 46 | | SIMPLE | 5 |
| MEDIUM | 36 | | STRUCTURED | 59 |
| HIGH | 11 | | EXTERNAL | 29 |

Jurisprudência: CONTEXT_ONLY 15, NONE 72, REQUIRED_FOR_CORRECTNESS 6 · motivos dos D: CONSTITUTIONAL_AMBIGUITY 1, INTERPRETIVE_CONTROVERSY 2, JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS 6, SANCTION_WITH_INTERPRETATION 4.

## Filas

| Fila | Agora (pendentes) | Triagem recalibrada | Checkpoint pré-recalibração |
|---|---|---|---|
| A_CLEAN_LOW | 0 | 42 | 1 |
| B_CLEAN_MEDIUM | 0 | 27 | 0 |
| C_QUICK_REVIEW | 0 | 13 | 3 |
| D_FULL_HUMAN_REVIEW | 0 | 11 | 89 |
| E_HARD_FAIL | 0 | 0 | 0 |

Triagem recalibrada: `BATCH06_TRIAGE_PRE_ROUND_D.json` · checkpoint pré-recalibração: `PRE_RECALIBRATION_MANIFEST.json`.
Risco no checkpoint: HIGH 89, LOW 3, MEDIUM 1.

**Migração dos 89 D antigos** (checkpoint → triagem recalibrada): 78 saíram de D → A_CLEAN_LOW 38, B_CLEAN_MEDIUM 27, C_QUICK_REVIEW 13, D_FULL_HUMAN_REVIEW 11.
Destino final dos 89 D antigos: HUMAN_APPROVED_T1 89 · decisões: APPROVED 18, APPROVED_AFTER_ADJUSTMENT 71 · por rodada: CF88_BATCH06_TRIAGE_QUEUE_D 11, CF88_BATCH06_TRIAGE_QUEUE_C 13, CF88_BATCH06_TRIAGE_QUEUE_B_PART1 9, CF88_BATCH06_TRIAGE_QUEUE_B_PART2 9, CF88_BATCH06_TRIAGE_QUEUE_B_PART3 9, CF88_BATCH06_TRIAGE_QUEUE_A_PART1 14, CF88_BATCH06_TRIAGE_QUEUE_A_PART2 14, CF88_BATCH06_TRIAGE_QUEUE_A_PART3 10.

## Revisão jurídica humana consolidada (BATCH06)

8 rodadas componentes · 93 decisões · 19 aprovados sem alteração jurídica · 74 ajustados e aprovados · 0 rejeitados.

| Rodada (escopo) | Decisões | Itens | Sem alteração | Ajustados | Rejeitados |
|---|---|---|---|---|---|
| `CF88_BATCH06_TRIAGE_QUEUE_D` | `ROUND_D_HUMAN_REVIEW_DECISIONS.json` | 11 | 2 | 9 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_C` | `ROUND_C_HUMAN_REVIEW_DECISIONS.json` | 13 | 8 | 5 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | `ROUND_B1_HUMAN_REVIEW_DECISIONS.json` | 9 | 1 | 8 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | `ROUND_B2_HUMAN_REVIEW_DECISIONS.json` | 9 | 1 | 8 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | `ROUND_B3_HUMAN_REVIEW_DECISIONS.json` | 9 | 0 | 9 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | `ROUND_A1_HUMAN_REVIEW_DECISIONS.json` | 15 | 2 | 13 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | `ROUND_A2_HUMAN_REVIEW_DECISIONS.json` | 15 | 4 | 11 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | `ROUND_A3_HUMAN_REVIEW_DECISIONS.json` | 12 | 1 | 11 | 0 |

| Target | Rodada | Versão aprovada | Decisão | Proveniência | Portão de checks |
|---|---|---|---|---|---|
| `CF88:ART.42` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.42:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.42:PAR.3` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.43` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.43:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.44` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.45` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.45:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v1 | APPROVED | 1 item(ns) | PASS |
| `CF88:ART.46` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.47` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.48` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.49` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.49:INC.I` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.49:INC.V` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.49:INC.IX` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.50` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.50:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.51` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.51:INC.I` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.52` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.52:INC.I` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.52:INC.III` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.52:INC.X` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.52:PAR.UNICO` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.53` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.53:CAPUT` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.53:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.53:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v2 | APPROVED_AFTER_ADJUSTMENT | 3 item(ns) | PASS |
| `CF88:ART.53:PAR.3` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v2 | APPROVED_AFTER_ADJUSTMENT | 1 item(ns) | PASS |
| `CF88:ART.53:PAR.6` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.53:PAR.8` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.54` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.54:INC.I` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.54:INC.II` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.55` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.55:INC.VI` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.55:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.55:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v1 | APPROVED | 1 item(ns) | PASS |
| `CF88:ART.55:PAR.4` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.56` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.56:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.57` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v2 | APPROVED_AFTER_ADJUSTMENT | 1 item(ns) | PASS |
| `CF88:ART.57:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.57:PAR.4` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.57:PAR.6` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.57:PAR.7` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.58` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.58:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.58:PAR.3` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.59` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.61` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.61:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.61:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.62` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v2 | APPROVED_AFTER_ADJUSTMENT | 1 item(ns) | PASS |
| `CF88:ART.62:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.62:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.62:PAR.3` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.62:PAR.5` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.62:PAR.6` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.62:PAR.10` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.62:PAR.11` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.63` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.64` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.64:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.65` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.66` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.66:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.66:PAR.4` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v1 | APPROVED | 1 item(ns) | PASS |
| `CF88:ART.66:PAR.7` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.67` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.68` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.68:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.68:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.69` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.70` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.70:PAR.UNICO` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.71` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.71:INC.I` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.71:INC.II` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.71:INC.III` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.71:INC.VIII` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.71:INC.IX` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.71:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.71:PAR.3` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.72` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.73` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.73:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_C` | v2 | APPROVED_AFTER_ADJUSTMENT | 1 item(ns) | PASS |
| `CF88:ART.73:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.73:PAR.3` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.74` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.74:PAR.1` | `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.74:PAR.2` | `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.75` | `CF88_BATCH06_TRIAGE_QUEUE_D` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |

Versões anteriores preservadas como RETIRED / CHANGES_REQUESTED: 74 (v1 dos ajustados).
Acervo HUMAN_APPROVED_T1: 289 antes → **382** depois (+93 do lote; os 3 pilotos reutilizados não são contados de novo).
Novos pendentes do lote: **0**. Todas as filas de revisão humana foram concluídas.

## Motivos dos D pendentes

- Nenhum item D permanece pendente (fila D encerrada).

## Achados que ainda pedem revisão (REVIEW_REQUIRED)

- nenhum

## Falsos positivos corrigidos por regra geral (validator v3)

- nenhum item pendente
- "incentivo(s)" como substantivo do próprio texto ou como matéria da lei não é teleologia; "todos os"/"só pode" que reproduzem quórum/condição explícitos não são universalização; "automaticamente" expresso no artigo não é consequência inventada.
- Rótulo truncado do fato externo ("Lei Complementar nº 7") passa a mostrar a identificação inteira; fato só na camada externa vai para C (o núcleo T1 não depende dele).

## Correções editoriais da recalibração (ROUND_0B)

21 edições em 19 explicações: DUPLICATION 1, EC_EVIDENCE 1, EXTERNAL 1, LONG_SENTENCE 8, RESSALVA 1, SEMANTIC 2, TELEOLOGY 7 (antes/depois em `RECALIBRATION_EDITORIAL_LOG.json`).

## Volume para o humano

| Métrica | Caracteres |
|---|---|
| Itens pendentes | 0 |
| Conteúdo pendente para revisão humana (5 seções + glossário) | 0 |
| Pacotes atuais (só cabeçalhos de filas vazias, mantidos por contrato) | 740 |
| — BATCH06_COMPACT_CLEAN_REVIEW.md | 295 |
| — BATCH06_FULL_HUMAN_REVIEW.md | 152 |
| — BATCH06_HARD_FAIL_REPORT.md | 150 |
| — BATCH06_QUICK_REVIEW.md | 143 |
| Redução vs. modelo antigo | N/A — não existem mais itens pendentes |
| Redução vs. checkpoint | N/A — não existem mais itens pendentes |

Volume histórico (métricas registradas nos snapshots versionados que ainda tinham itens pendentes; não recalculadas):

| Métrica | `BATCH06_TRIAGE_PRE_ROUND_D.json` (93 pendentes) | `BATCH06_TRIAGE_PRE_ROUND_A3.json` (12 pendentes) |
|---|---|---|
| Rascunhos (5 seções + glossário) | 124.343 | 14.372 |
| Modelo antigo (pacote completo dos pendentes) | 245.266 | 25.823 |
| Pacotes apresentados | 96.146 | 9.602 |
| Redução vs. modelo antigo | 149.120 (60.8%) | 16.221 (62.8%) |
| Checkpoint pré-recalibração (pacotes apresentados, D=89) | 265.430 | 265.430 |

Artefato D: gerado, sem itens pendentes (arquivo mantido por contrato determinístico).

## Dependências externas

- nenhuma

## Reprodutibilidade

- Texto CF/ADCT (sha256 dos bytes lidos, idêntico com arquivo local ou reconstrução do Git): `constituicao_federal_1988.txt` 3100e09700b1c0ce… (reconstruível do Git).
- Relations Engine: `BATCH06_RELATIONS_PIN.json` (cobertura parcial: só a relação consultada no checkpoint; atualização do pin para todo o escopo = NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY).
- Determinismo: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` (evidência em `DETERMINISM_EVIDENCE.json`).

## Regressão do validator v3 contra as decisões humanas do Batch05 (só leitura)

- v1 devolvidas pelo humano: 43 · detectadas v2 40 · v3 41 (perdidas pelo v3: nenhuma; ganhas: CF88:ART.37:PAR.9).
- v1 aprovadas sem mudança: 26 · com alerta v2 8 · v3 14 (custo em ruído dos detectores novos: CONDITION_NOT_IN_TEXT 1, HISTORICAL_CLAIM_UNVERIFIED 3, LIST_ITEM_POSSIBLY_DROPPED 2, NUMBER_NOT_IN_TEXT 1, RESSALVA_OMITTED_IN_SUMMARY 3).

## Limites do validador

- NUMBER_NOT_IN_TEXT compara quantidades, nao o sentido: um numero correto do texto usado no lugar errado passa; numeros por extenso so sao lidos em formas cardinais (um..mil) e fracoes (terco, quinto, quarto, metade, decimo); ordinais e datas ficam fora.
- RESSALVA_OMITTED_IN_SUMMARY reconhece que a explicacao "fala" de um dispositivo por radicais compartilhados (>= 2); parafrase com vocabulario totalmente diferente nao e reconhecida (falso negativo), e dispositivo com explicacao propria no lote nao e cobrado.
- LIST_ITEM_POSSIBLY_DROPPED usa radicais distintivos de cada item; sinonimos escapam (falso positivo) e omissao em lista curta (< 3 itens) nao e verificada. Listas declaradas seletivas ("entre elas", "por exemplo") nao sao cobradas.
- EXTERNAL_NORMATIVE_CONTENT_CLAIM depende de verbo de afirmacao normativa perto da referencia; afirmacao implicita sobre lei externa sem esse verbo nao e detectada. Remissao a artigo da propria CF presente no runtime e tratada como ancorada (o pacote D lista o texto).
- A distincao JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS x CONTEXT_ONLY le os marcadores de dependencia interpretativa que o proprio draft escreve; jurisprudencia necessaria e nao sinalizada pelo draft so e pega quando ha nota da camada e condicao sem base no texto.
- JURISPRUDENCE_CLAIM_WITHOUT_PROVENANCE so reconhece afirmacoes explicitas ("o Supremo decidiu/exige/admite", "a jurisprudencia delimita/reconhece"); jurisprudencia implicita (regra afirmada sem atribuicao) nao e detectada.
- PRISON_SCOPE_UNQUALIFIED cobre so a vedacao de prisao formulada como absoluta; outras garantias processuais ensinadas como absolutas dependem de UNIVERSAL_CLAIM/EXCEPTION_OR_RESSALVA_DROPPED.
- Nenhum check interpreta juridicamente o dispositivo: eles roteiam risco para revisao humana.
