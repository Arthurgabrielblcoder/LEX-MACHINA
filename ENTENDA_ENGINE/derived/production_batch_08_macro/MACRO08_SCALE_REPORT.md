# ENTENDA_CF_MACRO_BATCH_08 — relatório de escala

Data de referência: 2026-10-05 · gerado por `ENTENDA_ENGINE/build_entenda_macro_segment.py` (determinístico, só conteúdo versionado) · **0 HUMAN_APPROVED_T1 novos**: todas as explicações novas estão `PENDING_HUMAN_REVIEW`; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF.

Config de texto: `ENTENDA_ENGINE/profiles/CF88_OFFICIAL_RUNTIME/entenda_config.json`.

Sub-blocos construídos: MACRO_08_A, MACRO_08_B, MACRO_08_C, MACRO_08_D, MACRO_08_E, MACRO_08_F.

## Seleção (lote inteiro)

| | |
|---|---|
| Artigos no escopo | 112 explicados/avaliados no SELECTION_REPORT + 62 SKIP de artigo inteiro (SKIP_REGISTER) |
| Targets analisados | 848 (785 vigentes; excluídos: EXCLUDED_HISTORICAL 18, EXCLUDED_REVOKED 45) |
| SELECT | 148 = 147 novas + 1 reutilizada(s) já aprovada(s) |
| SKIP | 637 dispositivos (com motivo) + 62 artigos inteiros |

## Por sub-bloco

| Sub-bloco | Segmento | Artigos | SKIP art. | Vigentes | SELECT | SKIP | Novas | LOW/MED/HIGH | A/B/C/D/E | Correções do critic |
|---|---|---|---|---|---|---|---|---|---|---|
| MACRO_08_A | CORPO | 25 | 0 | 182 | 41 | 141 | 41 | 30/10/1 | 26/9/5/1/0 | 66 |
| MACRO_08_B | CORPO | 29 | 0 | 287 | 43 | 244 | 42 | 37/5/0 | 35/4/3/0/0 | 89 |
| MACRO_08_C | CORPO | 25 | 0 | 112 | 30 | 82 | 30 | 21/6/3 | 18/6/3/3/0 | 44 |
| MACRO_08_D | ADCT | 9 | 22 | 53 | 9 | 44 | 9 | 1/3/5 | 1/3/0/5/0 | 13 |
| MACRO_08_E | ADCT | 13 | 19 | 103 | 14 | 89 | 14 | 6/1/7 | 4/1/2/7/0 | 20 |
| MACRO_08_F | ADCT | 11 | 21 | 48 | 11 | 37 | 11 | 9/0/2 | 9/0/0/2/0 | 21 |

## Por segmento

| Segmento | Novas | LOW/MED/HIGH | SIMPLE/STRUCT/EXT | A/B/C/D/E |
|---|---|---|---|---|
| CORPO | 113 | 88/21/4 | 2/66/45 | 79/19/11/4/0 |
| ADCT | 34 | 16/4/14 | 0/12/22 | 14/4/2/14/0 |

## Mapa temporal (ADCT)

| Classe | Artigos |
|---|---|
| EFFECT_EXHAUSTED | 38 |
| EXTERNAL_STATUS_REQUIRED | 33 |
| NAO_CLASSIFICADO | 43 |
| OPERATIVE_CURRENT | 13 |
| OPERATIVE_TRANSITION | 6 |
| PARTIALLY_OPERATIVE | 5 |
| REVOKED | 10 |

## Dois eixos e filas (lote)

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 104 | | SIMPLE | 2 |
| MEDIUM | 25 | | STRUCTURED | 78 |
| HIGH | 18 | | EXTERNAL | 67 |

| Fila | Itens |
|---|---|
| A_CLEAN_LOW | 93 |
| B_CLEAN_MEDIUM | 23 |
| C_QUICK_REVIEW | 13 |
| D_FULL_HUMAN_REVIEW | 18 |
| E_HARD_FAIL | 0 |

D = 12.2% das novas.
Jurisprudência: CONTEXT_ONLY 23, NONE 122, REQUIRED_FOR_CORRECTNESS 2.

## Motivos dos D

- CONSTITUTIONAL_AMBIGUITY: 1
- INTERPRETIVE_CONTROVERSY: 1
- JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS: 1
- JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: 2
- SANCTION_WITH_INTERPRETATION: 1
- TEMPORAL_STATUS_UNRESOLVED: 15

## Achados REVIEW_REQUIRED

- EXTERNAL_FACT_NEEDS_PROVENANCE: 2
- LIST_ITEM_POSSIBLY_DROPPED: 16
- PERMISSION_NOT_IN_TEXT: 1

## Volume para o humano

| Métrica | Caracteres |
|---|---|
| Rascunhos (5 seções + glossário) | 204.274 |
| Modelo antigo (pacote completo de todos os itens) | 448.851 |
| **Apresentado ao humano (pacotes + prioridade)** | **189.428** |
| — MACRO08_COMPACT_AB_REVIEW.md | 89.779 |
| — MACRO08_FULL_D_REVIEW.md | 70.689 |
| — MACRO08_HARD_FAIL_REPORT.md | 119 |
| — MACRO08_HUMAN_REVIEW_PRIORITY.md | 20.410 |
| — MACRO08_QUICK_C_REVIEW.md | 8.431 |
| Redução vs. modelo antigo | 259.423 (57.8%) |

## Checks estruturais

- PASS: contrato do motor, Lei Seca idêntica ao texto do perfil em todos os registros, 0 HARD_FAIL, 0 aprovado novo, 0 STALE.

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
