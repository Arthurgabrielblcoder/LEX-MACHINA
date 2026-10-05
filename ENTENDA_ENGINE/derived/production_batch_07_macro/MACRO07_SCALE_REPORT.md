# ENTENDA_CF_MACRO_BATCH_07 — relatório de escala

Data de referência: 2026-10-05 · gerado por `ENTENDA_ENGINE/build_entenda_macro_batch.py` (determinístico, só conteúdo versionado) · **0 HUMAN_APPROVED_T1 novos**: todas as explicações novas estão `PENDING_HUMAN_REVIEW`; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF.

Sub-blocos construídos: MACRO_07_A (arts. 76–100), MACRO_07_B (arts. 101–125).

## Seleção

| | |
|---|---|
| Artigos | 53 |
| Targets analisados | 540 (516 vigentes; excluídos: EXCLUDED_HISTORICAL 17, EXCLUDED_REVOKED 7) |
| SELECT | 104 = 104 novas + 0 reutilizada(s) já aprovada(s) |
| SKIP | 412 (todos com motivo e explicação que os cobre) |
| Papéis das novas | BLOCK 22, DEVICE 14, ITEM 16, OVERVIEW 52 |

## Por sub-bloco

| Sub-bloco | Artigos | Vigentes | SELECT | SKIP | Novas | LOW/MED/HIGH | A/B/C/D/E | Correções do critic |
|---|---|---|---|---|---|---|---|---|
| MACRO_07_A | 25 | 260 | 55 | 205 | 55 | 31/16/8 | 31/16/0/8/0 | 74 |
| MACRO_07_B | 28 | 256 | 49 | 207 | 49 | 23/16/10 | 23/16/0/10/0 | 76 |

## Dois eixos e filas

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 54 | | SIMPLE | 3 |
| MEDIUM | 32 | | STRUCTURED | 56 |
| HIGH | 18 | | EXTERNAL | 45 |

| Fila | Itens |
|---|---|
| A_CLEAN_LOW | 54 |
| B_CLEAN_MEDIUM | 32 |
| C_QUICK_REVIEW | 0 |
| D_FULL_HUMAN_REVIEW | 18 |
| E_HARD_FAIL | 0 |

D = 17.3% das novas.
Jurisprudência: CONTEXT_ONLY 18, NONE 79, REQUIRED_FOR_CORRECTNESS 7.

## Motivos dos D

- INTERPRETIVE_CONTROVERSY: 2
- JUDICIAL_REVIEW_ANNOTATED: 10
- JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: 7
- TRANSITION_OR_TEMPORAL: 3

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
| Rascunhos (5 seções + glossário) | 146.024 |
| Modelo antigo (pacote completo de todos os itens) | 325.392 |
| **Apresentado ao humano (pacotes + prioridade)** | **163.505** |
| — MACRO07_COMPACT_AB_REVIEW.md | 64.385 |
| — MACRO07_FULL_D_REVIEW.md | 84.635 |
| — MACRO07_HARD_FAIL_REPORT.md | 119 |
| — MACRO07_HUMAN_REVIEW_PRIORITY.md | 14.201 |
| — MACRO07_QUICK_C_REVIEW.md | 165 |
| Redução vs. modelo antigo | 161.887 (49.8%) |

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
