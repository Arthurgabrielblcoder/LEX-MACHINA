# ENTENDA_CF_MACRO_BATCH_08 — relatório de escala

Data de referência: 2026-10-05 · gerado por `ENTENDA_ENGINE/build_entenda_macro_segment.py` (determinístico, só conteúdo versionado) · **0 HUMAN_APPROVED_T1 novos**: todas as explicações novas estão `PENDING_HUMAN_REVIEW`; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF.

Config de texto: `ENTENDA_ENGINE/profiles/CF88_OFFICIAL_RUNTIME/entenda_config.json`.

Sub-blocos construídos: MACRO_08_A.

## Seleção (lote inteiro)

| | |
|---|---|
| Artigos no escopo | 25 explicados/avaliados no SELECTION_REPORT + 0 SKIP de artigo inteiro (SKIP_REGISTER) |
| Targets analisados | 204 (182 vigentes; excluídos: EXCLUDED_HISTORICAL 7, EXCLUDED_REVOKED 15) |
| SELECT | 41 = 41 novas + 0 reutilizada(s) já aprovada(s) |
| SKIP | 141 dispositivos (com motivo) + 0 artigos inteiros |

## Por sub-bloco

| Sub-bloco | Segmento | Artigos | SKIP art. | Vigentes | SELECT | SKIP | Novas | LOW/MED/HIGH | A/B/C/D/E | Correções do critic |
|---|---|---|---|---|---|---|---|---|---|---|
| MACRO_08_A | CORPO | 25 | 0 | 182 | 41 | 141 | 41 | 30/10/1 | 26/9/5/1/0 | 66 |

## Por segmento

| Segmento | Novas | LOW/MED/HIGH | SIMPLE/STRUCT/EXT | A/B/C/D/E |
|---|---|---|---|---|
| CORPO | 41 | 30/10/1 | 1/23/17 | 26/9/5/1/0 |
| ADCT | 0 | 0/0/0 | 0/0/0 | 0/0/0/0/0 |

## Mapa temporal (ADCT)

| Classe | Artigos |
|---|---|
| NAO_CLASSIFICADO | 138 |
| REVOKED | 10 |

## Dois eixos e filas (lote)

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 30 | | SIMPLE | 1 |
| MEDIUM | 10 | | STRUCTURED | 23 |
| HIGH | 1 | | EXTERNAL | 17 |

| Fila | Itens |
|---|---|
| A_CLEAN_LOW | 26 |
| B_CLEAN_MEDIUM | 9 |
| C_QUICK_REVIEW | 5 |
| D_FULL_HUMAN_REVIEW | 1 |
| E_HARD_FAIL | 0 |

D = 2.4% das novas.
Jurisprudência: CONTEXT_ONLY 7, NONE 34.

## Motivos dos D

- TEMPORAL_STATUS_UNRESOLVED: 1

## Achados REVIEW_REQUIRED

- LIST_ITEM_POSSIBLY_DROPPED: 6
- PERMISSION_NOT_IN_TEXT: 1

## Volume para o humano

| Métrica | Caracteres |
|---|---|
| Rascunhos (5 seções + glossário) | 57.167 |
| Modelo antigo (pacote completo de todos os itens) | 122.062 |
| **Apresentado ao humano (pacotes + prioridade)** | **41.359** |
| — MACRO08_COMPACT_AB_REVIEW.md | 27.189 |
| — MACRO08_FULL_D_REVIEW.md | 4.152 |
| — MACRO08_HARD_FAIL_REPORT.md | 119 |
| — MACRO08_HUMAN_REVIEW_PRIORITY.md | 6.120 |
| — MACRO08_QUICK_C_REVIEW.md | 3.779 |
| Redução vs. modelo antigo | 80.703 (66.1%) |

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
