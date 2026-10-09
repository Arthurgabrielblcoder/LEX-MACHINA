# ENTENDA_CF_MACRO_BATCH_08 — relatório de escala

Data de referência: 2026-10-05 · gerado por `ENTENDA_ENGINE/build_entenda_macro_segment.py` (determinístico, só conteúdo versionado) · **179 HUMAN_APPROVED_T1** pela rodada humana registrada `MACRO08_FULL_HUMAN_REVIEW_179` (decisões em `MACRO08_ROUND_FINAL_HUMAN_REVIEW_DECISIONS.json`); 0 pendente(s); AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF.

Config de texto: `ENTENDA_ENGINE/profiles/CF88_OFFICIAL_RUNTIME/entenda_config.json`.

Sub-blocos construídos: MACRO_08_A, MACRO_08_B, MACRO_08_C, MACRO_08_D, MACRO_08_E, MACRO_08_F, MACRO_08_G, MACRO_08_H.

## Seleção (lote inteiro)

| | |
|---|---|
| Artigos no escopo | 154 explicados/avaliados no SELECTION_REPORT + 73 SKIP de artigo inteiro (SKIP_REGISTER) |
| Targets analisados | 1256 (1100 vigentes; excluídos: EXCLUDED_HISTORICAL 85, EXCLUDED_REVOKED 71) |
| SELECT | 180 = 179 novas + 1 reutilizada(s) já aprovada(s) |
| SKIP | 920 dispositivos (com motivo) + 73 artigos inteiros |

## Por sub-bloco

| Sub-bloco | Segmento | Artigos | SKIP art. | Vigentes | SELECT | SKIP | Novas | LOW/MED/HIGH | A/B/C/D/E | Correções do critic |
|---|---|---|---|---|---|---|---|---|---|---|
| MACRO_08_A | CORPO | 25 | 0 | 182 | 41 | 141 | 41 | 0/0/0 | 0/0/0/0/0 | 66 |
| MACRO_08_B | CORPO | 29 | 0 | 287 | 43 | 244 | 42 | 0/0/0 | 0/0/0/0/0 | 89 |
| MACRO_08_C | CORPO | 25 | 0 | 112 | 30 | 82 | 30 | 0/0/0 | 0/0/0/0/0 | 44 |
| MACRO_08_D | ADCT | 9 | 22 | 53 | 9 | 44 | 9 | 0/0/0 | 0/0/0/0/0 | 13 |
| MACRO_08_E | ADCT | 13 | 19 | 103 | 14 | 89 | 14 | 0/0/0 | 0/0/0/0/0 | 20 |
| MACRO_08_F | ADCT | 11 | 21 | 48 | 11 | 37 | 11 | 0/0/0 | 0/0/0/0/0 | 21 |
| MACRO_08_G | ADCT | 24 | 5 | 141 | 14 | 127 | 14 | 0/0/0 | 0/0/0/0/0 | 23 |
| MACRO_08_H | ADCT | 18 | 6 | 174 | 18 | 156 | 18 | 0/0/0 | 0/0/0/0/0 | 18 |

## Por segmento

| Segmento | Novas | LOW/MED/HIGH | SIMPLE/STRUCT/EXT | A/B/C/D/E |
|---|---|---|---|---|
| CORPO | 113 | 0/0/0 | 0/0/0 | 0/0/0/0/0 |
| ADCT | 66 | 0/0/0 | 0/0/0 | 0/0/0/0/0 |

## Mapa temporal (ADCT)

| Classe | Artigos |
|---|---|
| EFFECT_EXHAUSTED | 44 |
| EXTERNAL_STATUS_REQUIRED | 38 |
| FUTURE_TRIGGER | 8 |
| OPERATIVE_CURRENT | 20 |
| OPERATIVE_TRANSITION | 22 |
| PARTIALLY_OPERATIVE | 6 |
| REVOKED | 10 |

## Dois eixos e filas (lote)

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 0 | | SIMPLE | 0 |
| MEDIUM | 0 | | STRUCTURED | 0 |
| HIGH | 0 | | EXTERNAL | 0 |

| Fila | Itens |
|---|---|
| A_CLEAN_LOW | 0 |
| B_CLEAN_MEDIUM | 0 |
| C_QUICK_REVIEW | 0 |
| D_FULL_HUMAN_REVIEW | 0 |
| E_HARD_FAIL | 0 |

D = 0.0% das novas.
Jurisprudência: .

## Motivos dos D


## Achados REVIEW_REQUIRED

- nenhum

## Volume para o humano

| Métrica | Caracteres |
|---|---|
| Rascunhos (5 seções + glossário) | 0 |
| Modelo antigo (pacote completo de todos os itens) | 53 |
| **Apresentado ao humano (pacotes + prioridade)** | **1.265** |
| — MACRO08_COMPACT_AB_REVIEW.md | 381 |
| — MACRO08_FULL_D_REVIEW.md | 213 |
| — MACRO08_HARD_FAIL_REPORT.md | 119 |
| — MACRO08_HUMAN_REVIEW_PRIORITY.md | 387 |
| — MACRO08_QUICK_C_REVIEW.md | 165 |
| Redução vs. modelo antigo | -1.212 (-2286.8%) |

### Por segmento (cada segmento empacotado sozinho, mesmo código de pacotes)

| Segmento | Rascunhos | Modelo antigo | Apresentado | Redução |
|---|---|---|---|---|
| CORPO | 0 | 0 | 0 | 0 (None%) |
| ADCT | 0 | 0 | 0 | 0 (None%) |
| TOTAL (lote, empacotado junto) | 0 | 53 | 1.265 | -1.212 (-2286.8%) |

## Checks estruturais

- PASS: contrato do motor, Lei Seca idêntica ao texto do perfil em todos os registros, 0 HARD_FAIL, aprovação só pela rodada humana registrada (portão PASS), 0 STALE.

## Revisão humana (rodada registrada)

Escopo `MACRO08_FULL_HUMAN_REVIEW_179` · decisões em `MACRO08_ROUND_FINAL_HUMAN_REVIEW_DECISIONS.json` · 149 aprovados sem alteração · 30 ajustados e aprovados (nova editorial_version) · 0 rejeitados · 0 pendentes.

Portão de aprovação: **PASS** em 179 explicações (contrato do motor, validador v3 sem HARD_FAIL nem REVIEW_REQUIRED aberto, editorial_checks sem pendência). 25 decisões humanas por target/flag fecharam 26 ocorrência(s); nenhuma regra genérica.

Versões anteriores preservadas como RETIRED: 30. Evidência pré-revisão congelada em `*_PRE_HUMAN_REVIEW`.

| Target | Versão aprovada | Fila (calibração) | Decisão | Flags fechadas por decisão humana |
|---|---|---|---|---|
| `CF88:ART.177` | v1 | C | APPROVED | MB08-HFR-01 SEMANTIC_EQUIVALENCE_PRESENT, MB08-HFR-02 OVERVIEW_DESTINATION_CATEGORY_PRESERVED |
| `CF88:ART.177:PAR.4` | v2 | C | APPROVED_AFTER_ADJUSTMENT | MB08-HFR-03 FALSE_POSITIVE_PERMISSION_EXPLICIT_IN_SOURCE, MB08-HFR-04 SEMANTIC_ENUMERATION_PRESENT |
| `CF88:ART.182` | v1 | C | APPROVED | MB08-HFR-05 OVERVIEW_MAY_SUMMARIZE_CHILDREN |
| `CF88:ART.182:PAR.4` | v2 | B | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.184` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.194` | v2 | C | APPROVED_AFTER_ADJUSTMENT | MB08-HFR-06 OVERVIEW_MAY_SUMMARIZE_CHILDREN |
| `CF88:ART.195` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.195:INC.I` | v1 | C | APPROVED | MB08-HFR-07 SEMANTIC_EQUIVALENCE_PRESENT |
| `CF88:ART.195:PAR.5` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.195:PAR.7` | v2 | B | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.198:PAR.4` | v2 | B | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.198:PAR.12` | v2 | B | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.201` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.201:PAR.1` | v2 | A | APPROVED_AFTER_ADJUSTMENT | MB08-HFR-24 EXAMPLE_MAY_ILLUSTRATE_ONE_ENUMERATED_HYPOTHESIS |
| `CF88:ART.208:INC.I` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.209` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.212-A` | v1 | C | APPROVED | MB08-HFR-08 OVERVIEW_MAY_SUMMARIZE_CHILDREN |
| `CF88:ART.212-A:INC.V` | v1 | C | APPROVED | MB08-HFR-09 SEMANTIC_ITEM_ALREADY_PRESENT, MB08-HFR-10 SEMANTIC_ITEM_ALREADY_PRESENT |
| `CF88:ART.213` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.220:PAR.3` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.224` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.225:PAR.1` | v1 | C | APPROVED | MB08-HFR-11 SEMANTIC_ITEM_ALREADY_PRESENT, MB08-HFR-12 BLOCK_MAY_SUMMARIZE_SUBENUMERATION |
| `CF88:ART.227` | v1 | C | APPROVED | MB08-HFR-13 OVERVIEW_MAY_SUMMARIZE_CHILDREN |
| `CF88:ART.227:PAR.3` | v2 | C | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.231` | v2 | B | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.231:PAR.1` | v1 | D | APPROVED | MB08-HFR-20 OFFICIAL_CANONICAL_ANNOTATION |
| `CF88:ART.235` | v1 | C | APPROVED | MB08-HFR-14 SEMANTIC_ITEM_ALREADY_PRESENT |
| `CF88:ART.236` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.245` | v2 | B | APPROVED_AFTER_ADJUSTMENT | — |
| `CF88:ART.246` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `ADCT:ART.27` | v1 | D | APPROVED | MB08-HFR-21 OFFICIAL_CANONICAL_ANNOTATION |
| `ADCT:ART.49` | v2 | B | APPROVED_AFTER_ADJUSTMENT | — |
| `ADCT:ART.53` | v1 | C | APPROVED | MB08-HFR-15 SEMANTIC_REFERENCE_RESOLVES_LITERAL_CROSS_REFERENCE |
| `ADCT:ART.60` | v1 | C | APPROVED | MB08-HFR-16 SEMANTIC_ITEM_ALREADY_PRESENT |
| `ADCT:ART.68` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `ADCT:ART.76` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `ADCT:ART.76-B` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `ADCT:ART.97` | v1 | D | APPROVED | MB08-HFR-22 OVERVIEW_OMITS_NESTED_CONDITION_WITHOUT_CONTRADICTION |
| `ADCT:ART.101` | v1 | C | APPROVED | MB08-HFR-17 OFFICIAL_CANONICAL_ANNOTATION, MB08-HFR-17 OFFICIAL_CANONICAL_ANNOTATION |
| `ADCT:ART.107-A` | v1 | D | APPROVED | MB08-HFR-23 OFFICIAL_CANONICAL_ANNOTATION |
| `ADCT:ART.113` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `ADCT:ART.116` | v1 | C | APPROVED | MB08-HFR-18 SEMANTIC_ITEM_ALREADY_PRESENT, MB08-HFR-19 OVERVIEW_MAY_SUMMARIZE_SUBENUMERATION |
| `ADCT:ART.117` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `ADCT:ART.125` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |
| `ADCT:ART.127` | v2 | A | APPROVED_AFTER_ADJUSTMENT | MB08-HFR-25 TRANSITION_IS_THE_DEVICE_CORE |
| `ADCT:ART.130` | v2 | A | APPROVED_AFTER_ADJUSTMENT | — |

## Limites do validador

- NUMBER_NOT_IN_TEXT compara quantidades, nao o sentido: um numero correto do texto usado no lugar errado passa; numeros por extenso so sao lidos em formas cardinais (um..mil) e fracoes (terco, quinto, quarto, metade, decimo); ordinais e datas ficam fora.
- RESSALVA_OMITTED_IN_SUMMARY reconhece que a explicacao "fala" de um dispositivo por radicais compartilhados (>= 2); parafrase com vocabulario totalmente diferente nao e reconhecida (falso negativo), e dispositivo com explicacao propria no lote nao e cobrado.
- LIST_ITEM_POSSIBLY_DROPPED usa radicais distintivos de cada item; sinonimos escapam (falso positivo) e omissao em lista curta (< 3 itens) nao e verificada. Listas declaradas seletivas ("entre elas", "por exemplo") nao sao cobradas.
- EXTERNAL_NORMATIVE_CONTENT_CLAIM depende de verbo de afirmacao normativa perto da referencia; afirmacao implicita sobre lei externa sem esse verbo nao e detectada. Remissao a artigo da propria CF presente no runtime e tratada como ancorada (o pacote D lista o texto).
- A distincao JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS x CONTEXT_ONLY le os marcadores de dependencia interpretativa que o proprio draft escreve; jurisprudencia necessaria e nao sinalizada pelo draft so e pega quando ha nota da camada e condicao sem base no texto.
- JURISPRUDENCE_CLAIM_WITHOUT_PROVENANCE so reconhece afirmacoes explicitas ("o Supremo decidiu/exige/admite", "a jurisprudencia delimita/reconhece"); jurisprudencia implicita (regra afirmada sem atribuicao) nao e detectada.
- PRISON_SCOPE_UNQUALIFIED cobre so a vedacao de prisao formulada como absoluta; outras garantias processuais ensinadas como absolutas dependem de UNIVERSAL_CLAIM/EXCEPTION_OR_RESSALVA_DROPPED.
- Nenhum check interpreta juridicamente o dispositivo: eles roteiam risco para revisao humana.
- DATES_AND_YEARS_PARITY compara datas/anos por presenca na fundamentacao (Lei Seca do registro, artigo e dispositivos citados) e a data de referencia do lote; nao verifica calculos de prazo.
