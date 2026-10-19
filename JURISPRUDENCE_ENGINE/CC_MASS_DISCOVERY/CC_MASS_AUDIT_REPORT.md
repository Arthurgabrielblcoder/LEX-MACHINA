# CC MASS AUDIT — relatório (host-only, nenhuma ratificação)

```
MASS_AUDIT_STATUS = PASS
INPUT_RELATIONS = 932
RECONCILED_RELATIONS = 932
TIER_A_REASSESSED = 29
TIER_B_REASSESSED = 903
DEEP_AUDIT_SAMPLE = 200
READY_FOR_BLOCK_DECISION = 18
READY_WITH_QUALIFICATION = 663
INDIVIDUAL_REVIEW_REQUIRED = 60
NEEDS_MORE_EVIDENCE = 137
REJECT_RECOMMENDED = 54
BLOCKED_BY_SYSTEMIC_AUDIT = 0
READY_TOTAL = 681
TARGET_200_READY_REACHED = YES
STJ_TURMA_READY = 579
STJ_TURMA_REVIEW = 138
STJ_TURMA_REJECTED = 31
NEW_CC_TARGETS_READY = 624
PROJECTED_CC_READY_ONLY = 67/42
PROJECTED_CC_WITH_QUALIFICATIONS = 730/663
PROJECTED_CC_CEILING = 927/833
CURRENT_CC_PHYSICAL = 49/39
CURRENT_CF_PHYSICAL = 315/198
NEW_CORE_ENGINE_CODE_LINES = 0
REPRODUCIBILITY = PASS
SD_CHANGED = NO
FIRMWARE_CHANGED = NO
RATIFIED_NEW_RELATIONS = 0
DEPLOYED_NEW_RELATIONS = 0
RATIFICATION_PACKET_COUNT = 5
```

## Autoridade jurídica (independente da confiança da extração)

| Categoria | Relações |
|---|---:|
| CONCENTRATED_REVIEW | 12 |
| CORTE_ESPECIAL_ACORDAO | 35 |
| HOMOLOGATION_DECISION | 13 |
| QUALIFIED_PRECEDENT | 64 |
| QUALIFIED_PRECEDENT_PENDING | 4 |
| SECAO_ACORDAO | 52 |
| SUMULA_STJ | 4 |
| TURMA_ACORDAO | 748 |

Acórdão de Turma não é apresentado como precedente obrigatório, tese repetitiva, orientação pacificada nem posição unânime do STJ; acórdão de Seção/Corte Especial não é tratado como precedente obrigatório só pela origem colegiada.

## Auditoria aprofundada (200) e validação independente

Amostra: 200 relações; com erro: 29; por dimensão: identity 0, target 8, temporal 4, merits 0, pertinence 18, duplicate 1, authority 2; por estrato: OUTROS_NAO_TURMA 1/32; STF 14/19; TIER_A 1/29; TURMA 13/120.
Estado da regra (sem a auditoria) = estado final em 178/200 da amostra; 29 decisões do auditor prevalecem sobre a regra para os próprios casos. estratificada e deliberadamente enriquecida de casos de risco (todo o TIER A, todo o STF, julgados antigos, corroborados, sinalizados); a taxa de erro da amostra NÃO é estimativa da taxa da população.
Validação independente de acórdãos de Turma prontos, fora da amostra: rodada 1 (antes das últimas correções): 37/40 corretos; rodada 2 (regras congeladas): 30/30 corretos. Os erros da rodada 1 viraram regra; a rodada 2 mediu a regra final.

## Erros sistemáticos

Ver `CC_MASS_SYSTEMIC_ERRORS.md`. Impacto (relações que deixaram o estado favorável): S01_CC1916_NUMBERING 55, S02_OTHER_LAW 11, S03_ADMISSIBILITY 12, S04_QUESTION_NARRATIVE 15, S05_HEADING_ONLY 64, S06_UNIT_NOT_IN_TEXT 26, S07_STF_CONTEXTUAL 15, S08_DUPLICATES 3, S09_REPRESENTATIVE 81. Total fora do estado favorável: 251 de 932.

## Acórdãos de Turma

Prontos (com nota de natureza persuasiva): 579; revisão/evidência: 138; rejeição recomendada: 31. Classificação: {'CORROBORATED_TURMA_CASELAW': 100, 'INSUFFICIENT_EVIDENCE': 67, 'ISOLATED_MERITS_DECISION': 563, 'POTENTIAL_DIVERGENCE': 18}. Substituições de representante: 81 aplicadas nos prontos (83 propostas). 'CORROBORATED' é indício textual entre acórdãos, não consolidação.

## Pacotes

- `CC_MASS_RATIFICATION_PACKET_01.md` — PRECEDENTES QUALIFICADOS, SÚMULAS, STF E ACÓRDÃOS DE SEÇÃO/CORTE ESPECIAL (102)
- `CC_MASS_RATIFICATION_PACKET_02.md` — ACÓRDÃOS DE TURMA DO STJ (PERSUASIVOS) — PARTE_GERAL (95)
- `CC_MASS_RATIFICATION_PACKET_03.md` — ACÓRDÃOS DE TURMA DO STJ (PERSUASIVOS) — OBRIGACOES (parte) (150)
- `CC_MASS_RATIFICATION_PACKET_04.md` — ACÓRDÃOS DE TURMA DO STJ (PERSUASIVOS) — OBRIGACOES + EMPRESA + COISAS (188)
- `CC_MASS_RATIFICATION_PACKET_05.md` — ACÓRDÃOS DE TURMA DO STJ (PERSUASIVOS) — FAMILIA + SUCESSOES + DISPOSICOES_FINAIS_TRANSITORIAS (146)

Não pronto: `CC_MASS_RATIFICATION_HOLD.json` (revisão individual / mais evidência) e `CC_MASS_RATIFICATION_REJECT.json`.

## Projeção (não é baseline; nada foi ratificado)

| Cenário | Relações CC | Targets CC | Relações novas | Targets novos |
|---|---:|---:|---:|---:|
| Baseline físico | 49 | 39 | — | — |
| READY_ONLY | 67 | 42 | 18 | 3 |
| READY_WITH_QUALIFICATIONS | 730 | 663 | 681 | 624 |
| CEILING_ALL_NOT_REJECTED | 927 | 833 | 878 | 794 |

O cenário de teto inclui casos ainda em revisão/sem evidência: limite quantitativo, não recomendação de publicação.

## Capacidade do aparelho (SIMULATION_ONLY, maior conjunto não rejeitado)

Lookups 1030 (baseline 236; limite de segurança 4096); PSRAM do lookup 70040 B; JURISPRUDENCIA.IDX 154625 B (limite 16777216); fichas novas 758 (40185 B no cartão); máximo de relações por dispositivo 19 (limite 32); chaves duplicadas 0; regressão CF 0, CC-J1/J2 0; visíveis 878/878; rótulos {'ACORDAO': 811, 'ADI': 2, 'REPETITIVO': 58, 'RG': 3, 'Súmula': 4}.
Consulta: busca linear no cache — 4.36x as comparações do baseline por consulta (sem medir tempo).
Mudança arquitetural NÃO exigida pelos limites; nota de projeto separada: acórdãos aparecem como "ACORDAO n" (rótulo existente, sem validação física, sem classe nem órgão) — distinguir "REsp n (3ª Turma)" exigiria evolução de firmware, fora desta missão.

## Fichas futuras

As notas para o leitor (`NOTA NECESSÁRIA`) não contêm metadado interno (tier, estado editorial, flags, hashes); esses ficam no registro de auditoria. Nenhuma ficha definitiva foi produzida.

## Próximo passo

`NEXT_STEP = MASS HUMAN RATIFICATION` — não ratificado, não materializado, sem deploy.
