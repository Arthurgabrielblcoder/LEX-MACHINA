# ENTENDA_CF_MACRO_BATCH_08 — relatório de escala

Data de referência: 2026-10-05 · gerado por `ENTENDA_ENGINE/build_entenda_macro_segment.py` (determinístico, só conteúdo versionado) · **0 HUMAN_APPROVED_T1 novos**: todas as explicações novas estão `PENDING_HUMAN_REVIEW`; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF.

Config de texto: `ENTENDA_ENGINE/profiles/CF88_OFFICIAL_RUNTIME/entenda_config.json`.

Sub-blocos construídos: MACRO_08_A, MACRO_08_B.

## Seleção (lote inteiro)

| | |
|---|---|
| Artigos no escopo | 54 explicados/avaliados no SELECTION_REPORT + 0 SKIP de artigo inteiro (SKIP_REGISTER) |
| Targets analisados | 494 (469 vigentes; excluídos: EXCLUDED_HISTORICAL 10, EXCLUDED_REVOKED 15) |
| SELECT | 84 = 83 novas + 1 reutilizada(s) já aprovada(s) |
| SKIP | 385 dispositivos (com motivo) + 0 artigos inteiros |

## Por sub-bloco

| Sub-bloco | Segmento | Artigos | SKIP art. | Vigentes | SELECT | SKIP | Novas | LOW/MED/HIGH | A/B/C/D/E | Correções do critic |
|---|---|---|---|---|---|---|---|---|---|---|
| MACRO_08_A | CORPO | 25 | 0 | 182 | 41 | 141 | 41 | 30/10/1 | 26/9/5/1/0 | 66 |
| MACRO_08_B | CORPO | 29 | 0 | 287 | 43 | 244 | 42 | 37/5/0 | 34/4/4/0/0 | 89 |

## Por segmento

| Segmento | Novas | LOW/MED/HIGH | SIMPLE/STRUCT/EXT | A/B/C/D/E |
|---|---|---|---|---|
| CORPO | 83 | 67/15/1 | 1/49/33 | 60/13/9/1/0 |
| ADCT | 0 | 0/0/0 | 0/0/0 | 0/0/0/0/0 |

## Mapa temporal (ADCT)

| Classe | Artigos |
|---|---|
| NAO_CLASSIFICADO | 138 |
| REVOKED | 10 |

## Dois eixos e filas (lote)

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 67 | | SIMPLE | 1 |
| MEDIUM | 15 | | STRUCTURED | 49 |
| HIGH | 1 | | EXTERNAL | 33 |

| Fila | Itens |
|---|---|
| A_CLEAN_LOW | 60 |
| B_CLEAN_MEDIUM | 13 |
| C_QUICK_REVIEW | 9 |
| D_FULL_HUMAN_REVIEW | 1 |
| E_HARD_FAIL | 0 |

D = 1.2% das novas.
Jurisprudência: CONTEXT_ONLY 11, NONE 72.

## Motivos dos D

- TEMPORAL_STATUS_UNRESOLVED: 1

## Achados REVIEW_REQUIRED

- LIST_ITEM_POSSIBLY_DROPPED: 11
- NUMBER_NOT_IN_TEXT: 2
- PERMISSION_NOT_IN_TEXT: 1

## Volume para o humano

| Métrica | Caracteres |
|---|---|
| Rascunhos (5 seções + glossário) | 118.705 |
| Modelo antigo (pacote completo de todos os itens) | 260.523 |
| **Apresentado ao humano (pacotes + prioridade)** | **78.708** |
| — MACRO08_COMPACT_AB_REVIEW.md | 55.963 |
| — MACRO08_FULL_D_REVIEW.md | 4.152 |
| — MACRO08_HARD_FAIL_REPORT.md | 119 |
| — MACRO08_HUMAN_REVIEW_PRIORITY.md | 11.635 |
| — MACRO08_QUICK_C_REVIEW.md | 6.839 |
| Redução vs. modelo antigo | 181.815 (69.8%) |

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
