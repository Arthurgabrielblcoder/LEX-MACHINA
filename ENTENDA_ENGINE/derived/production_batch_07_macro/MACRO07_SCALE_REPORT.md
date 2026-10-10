# ENTENDA_CF_MACRO_BATCH_07 — relatório de escala

Data de referência: 2026-10-05 · gerado por `ENTENDA_ENGINE/build_entenda_macro_batch.py` (determinístico, só conteúdo versionado) · **0 HUMAN_APPROVED_T1 novos**: todas as explicações novas estão `PENDING_HUMAN_REVIEW`; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF.

Sub-blocos construídos: MACRO_07_A (arts. 76–100), MACRO_07_B (arts. 101–125), MACRO_07_C (arts. 126–150), MACRO_07_D (arts. 151–175).

## Seleção

| | |
|---|---|
| Artigos | 121 |
| Targets analisados | 1367 (1309 vigentes; excluídos: EXCLUDED_HISTORICAL 39, EXCLUDED_REVOKED 19) |
| SELECT | 250 = 249 novas + 1 reutilizada(s) já aprovada(s) |
| SKIP | 1059 (todos com motivo e explicação que os cobre) |
| Papéis das novas | BLOCK 44, DEVICE 58, ITEM 29, OVERVIEW 118 |

## Por sub-bloco

| Sub-bloco | Artigos | Vigentes | SELECT | SKIP | Novas | LOW/MED/HIGH | A/B/C/D/E | Correções do critic |
|---|---|---|---|---|---|---|---|---|
| MACRO_07_A | 25 | 260 | 55 | 205 | 55 | 31/19/5 | 31/19/0/5/0 | 75 |
| MACRO_07_B | 28 | 257 | 49 | 208 | 49 | 23/20/6 | 23/20/0/6/0 | 77 |
| MACRO_07_C | 30 | 267 | 67 | 200 | 66 | 43/21/2 | 43/21/0/2/0 | 133 |
| MACRO_07_D | 38 | 525 | 79 | 446 | 79 | 46/22/11 | 46/22/0/11/0 | 156 |

## Dois eixos e filas

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 143 | | SIMPLE | 11 |
| MEDIUM | 82 | | STRUCTURED | 135 |
| HIGH | 24 | | EXTERNAL | 103 |

| Fila | Itens |
|---|---|
| A_CLEAN_LOW | 143 |
| B_CLEAN_MEDIUM | 82 |
| C_QUICK_REVIEW | 0 |
| D_FULL_HUMAN_REVIEW | 24 |
| E_HARD_FAIL | 0 |

D = 9.6% das novas.
Jurisprudência: CONTEXT_ONLY 33, NONE 207, REQUIRED_FOR_CORRECTNESS 9.

## Motivos dos D

- INTERPRETIVE_CONTROVERSY: 1
- JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS: 11
- JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: 9
- TRANSITION_OR_TEMPORAL: 10

## Achados REVIEW_REQUIRED

- EXTERNAL_FACT_NEEDS_PROVENANCE: 22

## Dependências externas

- `CF88:ART.100`: ADI 4425, ADI 7047, JURISPRUDENCIA (contexto) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.100:PAR.9`: ADI 4425, ADI 7047, JURISPRUDENCIA (contexto) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.100:PAR.12`: ADI 4425, JURISPRUDENCIA (necessaria) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.114`: ADI 3423, JURISPRUDENCIA (necessaria) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.114:PAR.1`: ADI 3423, JURISPRUDENCIA (necessaria) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.114:PAR.3`: ADI 3423 · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.166`: ADI 7697, JURISPRUDENCIA (necessaria) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.166:PAR.9`: ADI 7697 · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.166:PAR.11`: ADI 7697, JURISPRUDENCIA (necessaria) · resolver EXTERNAL_VERIFICATION_REQUIRED
- `CF88:ART.166-A`: ADI 7697, JURISPRUDENCIA (necessaria) · resolver EXTERNAL_VERIFICATION_REQUIRED

## Volume para o humano

| Métrica | Caracteres |
|---|---|
| Rascunhos (5 seções + glossário) | 357.481 |
| Modelo antigo (pacote completo de todos os itens) | 823.155 |
| **Apresentado ao humano (pacotes + prioridade)** | **316.741** |
| — MACRO07_COMPACT_AB_REVIEW.md | 169.874 |
| — MACRO07_FULL_D_REVIEW.md | 112.033 |
| — MACRO07_HARD_FAIL_REPORT.md | 143 |
| — MACRO07_HUMAN_REVIEW_PRIORITY.md | 34.321 |
| — MACRO07_QUICK_C_REVIEW.md | 370 |
| Redução vs. modelo antigo | 506.414 (61.5%) |

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

## Segundo passe (compressão de risco e saneamento de fonte)

| | Antes | Depois |
|---|---|---|
| A_CLEAN_LOW | 143 | 143 |
| B_CLEAN_MEDIUM | 53 | 82 |
| C_QUICK_REVIEW | 0 | 0 |
| D_FULL_HUMAN_REVIEW | 53 | 24 |
| E_HARD_FAIL | 0 | 0 |
| LEGAL_RISK LOW | 143 | 143 |
| LEGAL_RISK MEDIUM | 53 | 82 |
| LEGAL_RISK HIGH | 53 | 24 |
| D (%) | 21.3% | 9.6% |
| Caracteres apresentados ao humano | 441.681 | 316.741 |

- Correções editoriais do segundo passe: 94 (ABSOLUTO 12, AFIRMACAO_NAO_VERIFICAVEL 2, DUPLICACAO_COM_DIFERENCA_JURIDICA 1, ENUMERACAO_INCOMPLETA 4, EXEMPLO_CRIA_REQUISITO 3, FONTE_SANEADA 2, GLOSSARIO_ERRADO 1, JURISPRUDENCIA_RECLASSIFICADA 9, JURISPRUDENCIA_VELADA 7, LEI_COMO_CONSTITUICAO 4, NUMERO 4, PAI_CONTRADIZ_FILHO 8, REGRA_INVENTADA 12, REMISSAO_ERRADA 7, TELEOLOGIA 18).
- Reclassificações de risco/fila: 29.
- Transições: 26 com evidência versionada; 16 resolvidas pelo Git (MEDIUM); 10 mantidas HIGH com critério explícito.
- Vide ADI: 14 classificados (CONTEXT_ONLY 3, REQUIRED_FOR_CORRECTNESS 11).
- PARENT_CHILD_LEGAL_CONSISTENCY: 118 visões gerais verificadas; 0 achado(s) em aberto; 6 corrigido(s) no segundo passe.
