# ENTENDA_CF_MACRO_BATCH_07 — relatório de escala

Data de referência: 2026-10-05 · gerado por `ENTENDA_ENGINE/build_entenda_macro_batch.py` (determinístico, só conteúdo versionado) · **0 HUMAN_APPROVED_T1 novos**: todas as explicações novas estão `PENDING_HUMAN_REVIEW`; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF.

Sub-blocos construídos: MACRO_07_A (arts. 76–100), MACRO_07_B (arts. 101–125), MACRO_07_C (arts. 126–150).

## Seleção

| | |
|---|---|
| Artigos | 83 |
| Targets analisados | 814 (783 vigentes; excluídos: EXCLUDED_HISTORICAL 23, EXCLUDED_REVOKED 8) |
| SELECT | 171 = 170 novas + 1 reutilizada(s) já aprovada(s) |
| SKIP | 612 (todos com motivo e explicação que os cobre) |
| Papéis das novas | BLOCK 31, DEVICE 32, ITEM 26, OVERVIEW 81 |

## Por sub-bloco

| Sub-bloco | Artigos | Vigentes | SELECT | SKIP | Novas | LOW/MED/HIGH | A/B/C/D/E | Correções do critic |
|---|---|---|---|---|---|---|---|---|
| MACRO_07_A | 25 | 260 | 55 | 205 | 55 | 31/16/8 | 31/16/0/8/0 | 75 |
| MACRO_07_B | 28 | 256 | 49 | 207 | 49 | 23/16/10 | 23/16/0/10/0 | 77 |
| MACRO_07_C | 30 | 267 | 67 | 200 | 66 | 43/13/10 | 43/13/0/10/0 | 133 |

## Dois eixos e filas

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 97 | | SIMPLE | 8 |
| MEDIUM | 45 | | STRUCTURED | 93 |
| HIGH | 28 | | EXTERNAL | 69 |

| Fila | Itens |
|---|---|
| A_CLEAN_LOW | 97 |
| B_CLEAN_MEDIUM | 45 |
| C_QUICK_REVIEW | 0 |
| D_FULL_HUMAN_REVIEW | 28 |
| E_HARD_FAIL | 0 |

D = 16.5% das novas.
Jurisprudência: CONTEXT_ONLY 22, NONE 134, REQUIRED_FOR_CORRECTNESS 14.

## Motivos dos D

- INTERPRETIVE_CONTROVERSY: 3
- JUDICIAL_REVIEW_ANNOTATED: 10
- JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: 14
- TRANSITION_OR_TEMPORAL: 6

## Achados REVIEW_REQUIRED

- EXTERNAL_FACT_NEEDS_PROVENANCE: 18

## Dependências externas

- `CF88:ART.100`: ADI 4425, ADI 7047, JURISPRUDENCIA (contexto) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.100:PAR.9`: ADI 4425, ADI 7047, JURISPRUDENCIA (contexto) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.100:PAR.12`: ADI 4425, JURISPRUDENCIA (necessaria) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.114`: ADI 3423, JURISPRUDENCIA (necessaria) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.114:PAR.1`: ADI 3423, JURISPRUDENCIA (necessaria) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.114:PAR.3`: ADI 3423 · resolver EXTERNAL_VERIFICATION_REQUIRED

## Volume para o humano

| Métrica | Caracteres |
|---|---|
| Rascunhos (5 seções + glossário) | 238.394 |
| Modelo antigo (pacote completo de todos os itens) | 516.818 |
| **Apresentado ao humano (pacotes + prioridade)** | **248.062** |
| — MACRO07_COMPACT_AB_REVIEW.md | 105.086 |
| — MACRO07_FULL_D_REVIEW.md | 119.801 |
| — MACRO07_HARD_FAIL_REPORT.md | 119 |
| — MACRO07_HUMAN_REVIEW_PRIORITY.md | 22.891 |
| — MACRO07_QUICK_C_REVIEW.md | 165 |
| Redução vs. modelo antigo | 268.756 (52.0%) |

## Checks estruturais

- PASS: contrato do motor, Lei Seca idêntica ao runtime em todos os registros, 0 HARD_FAIL, 0 aprovado novo, 0 STALE.

## Limites do validador

- NUMBER_NOT_IN_TEXT compara quantidades, nao o sentido: um numero correto do texto usado no lugar errado passa; numeros por extenso so sao lidos em formas cardinais (um..mil) e fracoes (terco, quinto, quarto, metade, decimo); ordinais e datas ficam fora.
- RESSALVA_OMITTED_IN_SUMMARY reconhece que a explicacao "fala" de um dispositivo por radicais compartilhados (>= 2); parafrase com vocabulario totalmente diferente nao e reconhecida (falso negativo), e dispositivo com explicacao propria no lote nao e cobrado.
- LIST_ITEM_POSSIBLY_DROPPED usa radicais distintivos de cada item; sinonimos escapam (falso positivo) e omissao em lista curta (< 3 itens) nao e verificada. Listas declaradas seletivas ("entre elas", "por exemplo") nao sao cobradas.
- EXTERNAL_NORMATIVE_CONTENT_CLAIM depende de verbo de afirmacao normativa perto da referencia; afirmacao implicita sobre lei externa sem esse verbo nao e detectada. Remissao a artigo da propria CF presente no runtime e tratada como ancorada (o pacote D lista o texto).
- A distincao JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS x CONTEXT_ONLY le os marcadores de dependencia interpretativa que o proprio draft escreve; jurisprudencia necessaria e nao sinalizada pelo draft so e pega quando ha nota da camada e condicao sem base no texto.
- JURISPRUDENCE_CLAIM_WITHOUT_PROVENANCE so reconhece afirmacoes explicitas ("o Supremo decidiu/exige/admite", "a jurisprudencia delimita/reconhece"); jurisprudencia implicita (regra afirmada sem atribuicao) nao e detectada.
- PRISON_SCOPE_UNQUALIFIED cobre so a vedacao de prisao formulada como absoluta; outras garantias processuais ensinadas como absolutas dependem de UNIVERSAL_CLAIM/EXCEPTION_OR_RESSALVA_DROPPED.
- Nenhum check interpreta juridicamente o dispositivo: eles roteiam risco para revisao humana.
