# Correção da afirmação anterior sobre REFERÊNCIAS (camada 4 = WORK_REFERENCE)

A lista anterior de 17 artigos vinha do relatório da equivalência ART ↔ CAPUT: **32 vínculos em 17 targets `:CAPUT`**, dos quais apenas
**25 eram WORK_REFERENCE**; 6 eram JURISPRUDÊNCIA e 1 era CORRELATA. Ler essa lista como “17 artigos com obra” misturou tipos de vínculo.
Este documento fixa a verdade canônica com o export corrigido (run2) e o classificador atual (somente `WORK_REFERENCE` `CURRENT_VISIBLE` vai para o botão 4).

| ARTIGO | CLASSIFICAÇÃO | WORK_REFERENCE NO CAPUT | O QUE HAVIA NO CAPUT (NÃO-OBRA) | OBRAS NO ARTIGO INTEIRO |
|---|---|---|---|---|
| Art. 2 | **CONFIRMED_WORK_REFERENCE** | O Federalista (EXP-LIV-006) | JURISPRUDÊNCIA: Tema de Repercussão Geral 1120 (STF:RG:1120) | 1 |
| Art. 5 | **CONFIRMED_WORK_REFERENCE** | A Revolução dos Bichos (REF-LIV-0006); Filadélfia (REF-FIL-0004) | JURISPRUDÊNCIA: Tema de Repercussão Geral 113 (STF:RG:113) | 33 |
| Art. 6 | **CONFIRMED_WORK_REFERENCE** | A Cor da Lei (EXP-LIV-008); Ensaio sobre a Cegueira (REF-LIV-0007); Eu, Daniel Blake (EXP-FIL-006); Filadélfia (REF-FIL-0004); Ilha das Flores (REF-DOC-0004); Quarto de Despejo (REF-LIV-0004) | JURISPRUDÊNCIA: Tema de Repercussão Geral 295 (STF:RG:295); JURISPRUDÊNCIA: Tema de Repercussão Geral 455 (STF:RG:455) | 6 |
| Art. 14 | **CONFIRMED_WORK_REFERENCE** | Selma (REF-FIL-0005) | — | 1 |
| Art. 37 | **MISCLASSIFIED_NON_WORK_RELATION** | — | JURISPRUDÊNCIA: Tema de Repercussão Geral 66 (STF:RG:66) | 0 |
| Art. 43 | **MISCLASSIFIED_NON_WORK_RELATION** | — | JURISPRUDÊNCIA: Tema de Repercussão Geral 975 (STF:RG:975) | 0 |
| Art. 62 | **MISCLASSIFIED_NON_WORK_RELATION** | — | JURISPRUDÊNCIA: Tema de Repercussão Geral 33 (STF:RG:33); JURISPRUDÊNCIA: Tema de Repercussão Geral 1196 (STF:RG:1196) | 0 |
| Art. 98 | **MISCLASSIFIED_NON_WORK_RELATION** | — | JURISPRUDÊNCIA: Tema de Repercussão Geral 847 (STF:RG:847) | 0 |
| Art. 170 | **CONFIRMED_WORK_REFERENCE** | Capital no Século XXI (EXP-DOC-002); Desigualdade para Todos (EXP-DOC-003); Eu, Daniel Blake (EXP-FIL-006); Ilha das Flores (REF-DOC-0004); O Triunfo da Injustiça (EXP-LIV-009); Quarto de Despejo (REF-LIV-0004) | — | 15 |
| Art. 193 | **CONFIRMED_WORK_REFERENCE** | Capital no Século XXI (EXP-DOC-002); Desigualdade para Todos (EXP-DOC-003); O Triunfo da Injustiça (EXP-LIV-009) | — | 3 |
| Art. 194 | **CONFIRMED_WORK_REFERENCE** | Eu, Daniel Blake (EXP-FIL-006) | — | 1 |
| Art. 201 | **MISCLASSIFIED_NON_WORK_RELATION** | — | JURISPRUDÊNCIA: Tema de Repercussão Geral 88 (STF:RG:88) | 0 |
| Art. 202 | **MISCLASSIFIED_NON_WORK_RELATION** | — | CORRELATA: EXT_LC109_2001 (EXT_LC109_2001) | 0 |
| Art. 205 | **CONFIRMED_WORK_REFERENCE** | Cidadania no Brasil: O Longo Caminho (EXP-LIV-004) | — | 1 |
| Art. 220 | **CONFIRMED_WORK_REFERENCE** | The Post: A Guerra Secreta (REF-FIL-0006) | — | 4 |
| Art. 225 | **CONFIRMED_WORK_REFERENCE** | Chernobyl (REF-SER-0003); O Preço da Verdade (REF-FIL-0007) | — | 2 |
| Art. 227 | **CONFIRMED_WORK_REFERENCE** | Quarto de Despejo (REF-LIV-0004) | JURISPRUDÊNCIA: Tema de Repercussão Geral 1182 (STF:RG:1182); JURISPRUDÊNCIA: Tema de Repercussão Geral 966 (STF:RG:966); JURISPRUDÊNCIA: Tema de Repercussão Geral 976 (STF:RG:976) | 1 |

**Resumo:** CONFIRMED_WORK_REFERENCE = arts. 2, 5, 6, 14, 170, 193, 194, 205, 220, 225, 227; MISCLASSIFIED_NON_WORK_RELATION = arts. 37, 43, 62, 98, 201, 202.

Nos MISCLASSIFIED, o vínculo do caput era jurisprudência ou correlata: ele aparece em 2 JURIS. ou 1 CORR., nunca em 4 REF. Nesses 6 artigos não existe nenhuma obra em todo o artigo (CONFIRMED_REFERENCE_GAP).

## Auditoria individual (17 artigos)

### Art. 2

1. Existe WORK_REFERENCE? **SIM** (1 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.2:CAPUT` — O Federalista (EXP-LIV-006, LIVRO) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.2`, via ART↔CAPUT)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO** — vínculos não-obra no artigo: JURISPRUDENCE/CURRENT_VISIBLE 1

### Art. 5

1. Existe WORK_REFERENCE? **SIM** (33 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.5:CAPUT` — A Revolução dos Bichos (REF-LIV-0006, LIVRO) — score 5.7 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5`, via ART↔CAPUT)
   - `CF88:ART.5:CAPUT` — Filadélfia (REF-FIL-0004, FILME) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5`, via ART↔CAPUT)
   - `CF88:ART.5:INC.I` — The Handmaid's Tale (REF-SER-0002, SÉRIE) — score 9.2 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.I`)
   - `CF88:ART.5:INC.III` — Vigiar e Punir (REF-LIV-0005, LIVRO) — score 7.9 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.III`)
   - `CF88:ART.5:INC.IV` — 1984 (REF-LIV-0001, LIVRO) — score 7.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.IV`)
   - `CF88:ART.5:INC.IV` — The Post: A Guerra Secreta (REF-FIL-0006, FILME) — score 8.5 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.IV`)
   - `CF88:ART.5:INC.IV` — V de Vingança (REF-FIL-0002, FILME) — score 8.7 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.IV`)
   - `CF88:ART.5:INC.VI` — Timbuktu (EXP-FIL-009, FILME) — score 8.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.VI`)
   - `CF88:ART.5:INC.VIII` — Timbuktu (EXP-FIL-009, FILME) — score 9.0 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.VIII`)
   - `CF88:ART.5:INC.IX` — 1984 (REF-LIV-0001, LIVRO) — score 8.3 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.IX`)
   - `CF88:ART.5:INC.IX` — The Post: A Guerra Secreta (REF-FIL-0006, FILME) — score 9.2 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.IX`)
   - `CF88:ART.5:INC.X` — 1984 (REF-LIV-0001, LIVRO) — score 9.1 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.X`)
   - `CF88:ART.5:INC.X` — A Vida dos Outros (REF-FIL-0003, FILME) — score 9.1 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.X`)
   - `CF88:ART.5:INC.X` — Privacidade Hackeada (REF-DOC-0001, DOCUMENTÁRIO) — score 9.1 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.X`)
   - `CF88:ART.5:INC.XII` — A Vida dos Outros (REF-FIL-0003, FILME) — score 8.9 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XII`)
   - `CF88:ART.5:INC.XIII` — Filadélfia (REF-FIL-0004, FILME) — score 7.9 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XIII`)
   - `CF88:ART.5:INC.XIV` — Chernobyl (REF-SER-0003, SÉRIE) — score 8.2 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XIV`)
   - `CF88:ART.5:INC.XV` — Papers, Please (REF-JOG-0001, JOGO) — score 3.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XV`)
   - `CF88:ART.5:INC.XXII` — Leviatã (EXP-FIL-005, FILME) — score 6.6 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XXII`)
   - `CF88:ART.5:INC.XXXV` — O Preço da Verdade (REF-FIL-0007, FILME) — score 7.4 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XXXV`)
   - `CF88:ART.5:INC.XLII` — A 13ª Emenda (REF-DOC-0002, DOCUMENTÁRIO) — score 8.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XLII`)
   - `CF88:ART.5:INC.XLII` — A Cor da Lei (EXP-LIV-008, LIVRO) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XLII`)
   - `CF88:ART.5:INC.XLII` — AmarElo — É Tudo Pra Ontem (EXP-DOC-009, DOCUMENTÁRIO) — score 8.4 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XLII`)
   - `CF88:ART.5:INC.XLII` — Borderlands/La Frontera: The New Mestiza (EXP-LIV-010, LIVRO) — score 8.0 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XLII`)
   - `CF88:ART.5:INC.XLIX` — A 13ª Emenda (REF-DOC-0002, DOCUMENTÁRIO) — score 7.0 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XLIX`)
   - `CF88:ART.5:INC.XLIX` — Olhos que Condenam (REF-SER-0001, SÉRIE) — score 6.5 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.XLIX`)
   - `CF88:ART.5:INC.LIV` — 12 Homens e uma Sentença (REF-FIL-0001, FILME) — score 9.2 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.LIV`)
   - `CF88:ART.5:INC.LIV` — O Processo (REF-LIV-0002, LIVRO) — score 9.2 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.LIV`)
   - `CF88:ART.5:INC.LIV` — Olhos que Condenam (REF-SER-0001, SÉRIE) — score 9.2 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.LIV`)
   - `CF88:ART.5:INC.LV` — O Processo (REF-LIV-0002, LIVRO) — score 8.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.LV`)
   - `CF88:ART.5:INC.LVII` — 12 Homens e uma Sentença (REF-FIL-0001, FILME) — score 8.5 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.LVII`)
   - `CF88:ART.5:INC.LXXIX` — A Vida dos Outros (REF-FIL-0003, FILME) — score 9.1 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.LXXIX`)
   - `CF88:ART.5:INC.LXXIX` — Privacidade Hackeada (REF-DOC-0001, DOCUMENTÁRIO) — score 9.1 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.5:INC.LXXIX`)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO** — vínculos não-obra no artigo: JURISPRUDENCE/CURRENT_VISIBLE 27, CORRELATA/CURRENT_VISIBLE 1

### Art. 6

1. Existe WORK_REFERENCE? **SIM** (6 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.6:CAPUT` — A Cor da Lei (EXP-LIV-008, LIVRO) — score 7.5 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.6`, via ART↔CAPUT)
   - `CF88:ART.6:CAPUT` — Ensaio sobre a Cegueira (REF-LIV-0007, LIVRO) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.6`, via ART↔CAPUT)
   - `CF88:ART.6:CAPUT` — Eu, Daniel Blake (EXP-FIL-006, FILME) — score 7.3 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.6`, via ART↔CAPUT)
   - `CF88:ART.6:CAPUT` — Filadélfia (REF-FIL-0004, FILME) — score 7.6 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.6`, via ART↔CAPUT)
   - `CF88:ART.6:CAPUT` — Ilha das Flores (REF-DOC-0004, DOCUMENTÁRIO) — score 7.3 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.6`, via ART↔CAPUT)
   - `CF88:ART.6:CAPUT` — Quarto de Despejo (REF-LIV-0004, LIVRO) — score 8.7 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.6`, via ART↔CAPUT)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO** — vínculos não-obra no artigo: JURISPRUDENCE/CURRENT_VISIBLE 2

### Art. 14

1. Existe WORK_REFERENCE? **SIM** (1 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.14:CAPUT` — Selma (REF-FIL-0005, FILME) — score 7.4 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.14`, via ART↔CAPUT)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO** — vínculos não-obra no artigo: JURISPRUDENCE/CURRENT_VISIBLE 8

### Art. 37

1. Existe WORK_REFERENCE? **NÃO** (0 no artigo inteiro).
2. Target exato: —
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **SIM** — vínculos não-obra no artigo: JURISPRUDENCE/CURRENT_VISIBLE 27, CORRELATA/CURRENT_VISIBLE 4

**Auditoria do artigo inteiro (verificação física de Arthur):**
- WORK_REFERENCE NO CAPUT = NO
- WORK_REFERENCE EM QUALQUER INCISO = nenhum
- WORK_REFERENCE EM QUALQUER PARÁGRAFO = nenhum
- WORK_REFERENCE EM QUALQUER ALÍNEA = nenhuma
- TOTAL WORK_REFERENCE = 0
- STATUS = **ZERO_COVERAGE** · **CONFIRMED_REFERENCE_GAP**

### Art. 43

1. Existe WORK_REFERENCE? **NÃO** (0 no artigo inteiro).
2. Target exato: —
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **SIM** — vínculos não-obra no artigo: JURISPRUDENCE/CURRENT_VISIBLE 3, CORRELATA/CURRENT_VISIBLE 2

**Auditoria do artigo inteiro (verificação física de Arthur):**
- WORK_REFERENCE NO CAPUT = NO
- WORK_REFERENCE EM QUALQUER INCISO = nenhum
- WORK_REFERENCE EM QUALQUER PARÁGRAFO = nenhum
- WORK_REFERENCE EM QUALQUER ALÍNEA = nenhuma
- TOTAL WORK_REFERENCE = 0
- STATUS = **ZERO_COVERAGE** · **CONFIRMED_REFERENCE_GAP**

### Art. 62

1. Existe WORK_REFERENCE? **NÃO** (0 no artigo inteiro).
2. Target exato: —
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **SIM** — vínculos não-obra no artigo: JURISPRUDENCE/CURRENT_VISIBLE 2

**Auditoria do artigo inteiro (verificação física de Arthur):**
- WORK_REFERENCE NO CAPUT = NO
- WORK_REFERENCE EM QUALQUER INCISO = nenhum
- WORK_REFERENCE EM QUALQUER PARÁGRAFO = nenhum
- WORK_REFERENCE EM QUALQUER ALÍNEA = nenhuma
- TOTAL WORK_REFERENCE = 0
- STATUS = **ZERO_COVERAGE** · **CONFIRMED_REFERENCE_GAP**

### Art. 98

1. Existe WORK_REFERENCE? **NÃO** (0 no artigo inteiro).
2. Target exato: —
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **SIM** — vínculos não-obra no artigo: JURISPRUDENCE/CURRENT_VISIBLE 2

**Auditoria do artigo inteiro (verificação física de Arthur):**
- WORK_REFERENCE NO CAPUT = NO
- WORK_REFERENCE EM QUALQUER INCISO = nenhum
- WORK_REFERENCE EM QUALQUER PARÁGRAFO = nenhum
- WORK_REFERENCE EM QUALQUER ALÍNEA = nenhuma
- TOTAL WORK_REFERENCE = 0
- STATUS = **ZERO_COVERAGE** · **CONFIRMED_REFERENCE_GAP**

### Art. 170

1. Existe WORK_REFERENCE? **SIM** (15 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.170:CAPUT` — Capital no Século XXI (EXP-DOC-002, DOCUMENTÁRIO) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170`, via ART↔CAPUT)
   - `CF88:ART.170:CAPUT` — Desigualdade para Todos (EXP-DOC-003, DOCUMENTÁRIO) — score 6.5 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170`, via ART↔CAPUT)
   - `CF88:ART.170:CAPUT` — Eu, Daniel Blake (EXP-FIL-006, FILME) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170`, via ART↔CAPUT)
   - `CF88:ART.170:CAPUT` — Ilha das Flores (REF-DOC-0004, DOCUMENTÁRIO) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170`, via ART↔CAPUT)
   - `CF88:ART.170:CAPUT` — O Triunfo da Injustiça (EXP-LIV-009, LIVRO) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170`, via ART↔CAPUT)
   - `CF88:ART.170:CAPUT` — Quarto de Despejo (REF-LIV-0004, LIVRO) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170`, via ART↔CAPUT)
   - `CF88:ART.170:INC.II` — Leviatã (EXP-FIL-005, FILME) — score 6.6 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170:INC.II`)
   - `CF88:ART.170:INC.VI` — Chernobyl (REF-SER-0003, SÉRIE) — score 8.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170:INC.VI`)
   - `CF88:ART.170:INC.VI` — O Preço da Verdade (REF-FIL-0007, FILME) — score 9.2 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170:INC.VI`)
   - `CF88:ART.170:INC.VII` — Capital no Século XXI (EXP-DOC-002, DOCUMENTÁRIO) — score 5.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170:INC.VII`)
   - `CF88:ART.170:INC.VII` — Desigualdade para Todos (EXP-DOC-003, DOCUMENTÁRIO) — score 5.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170:INC.VII`)
   - `CF88:ART.170:INC.VII` — Eu, Daniel Blake (EXP-FIL-006, FILME) — score 6.6 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170:INC.VII`)
   - `CF88:ART.170:INC.VII` — Ilha das Flores (REF-DOC-0004, DOCUMENTÁRIO) — score 7.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170:INC.VII`)
   - `CF88:ART.170:INC.VII` — O Triunfo da Injustiça (EXP-LIV-009, LIVRO) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170:INC.VII`)
   - `CF88:ART.170:INC.VII` — Quarto de Despejo (REF-LIV-0004, LIVRO) — score 8.3 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.170:INC.VII`)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO**

### Art. 193

1. Existe WORK_REFERENCE? **SIM** (3 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.193:CAPUT` — Capital no Século XXI (EXP-DOC-002, DOCUMENTÁRIO) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.193`, via ART↔CAPUT)
   - `CF88:ART.193:CAPUT` — Desigualdade para Todos (EXP-DOC-003, DOCUMENTÁRIO) — score 6.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.193`, via ART↔CAPUT)
   - `CF88:ART.193:CAPUT` — O Triunfo da Injustiça (EXP-LIV-009, LIVRO) — score ausente — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.193`, via ART↔CAPUT)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO**

**Auditoria do artigo inteiro (verificação física de Arthur):**
- WORK_REFERENCE NO CAPUT = YES
- WORK_REFERENCE EM QUALQUER INCISO = nenhum
- WORK_REFERENCE EM QUALQUER PARÁGRAFO = nenhum
- WORK_REFERENCE EM QUALQUER ALÍNEA = nenhuma
- TOTAL WORK_REFERENCE = 3
- STATUS = **COVERED**
- **Divergência com o teste físico:** os dados têm 3 obras em `CF88:ART.193:CAPUT`, alcançáveis pela linha do art. 193 (ACTIVE_TARGET `CF88:ART.193`, chaves `ART.193 + ART.193:CAPUT`). Hipótese a confirmar no aparelho: o CONTEXTO é escolhido pela linha central do viewport; o art. 193 é curto e, após a busca, a linha central costuma cair no parágrafo único ou no art. 194. O botão 4 só aparece quando o rodapé mostra `CONTEXTO: ART. 193` (sem `PAR.`). Reteste físico recomendado; não é lacuna de dados.

### Art. 194

1. Existe WORK_REFERENCE? **SIM** (1 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.194:CAPUT` — Eu, Daniel Blake (EXP-FIL-006, FILME) — score 6.0 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.194`, via ART↔CAPUT)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO**

### Art. 201

1. Existe WORK_REFERENCE? **NÃO** (0 no artigo inteiro).
2. Target exato: —
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **SIM** — vínculos não-obra no artigo: JURISPRUDENCE/CURRENT_VISIBLE 4, CORRELATA/CURRENT_VISIBLE 5

**Auditoria do artigo inteiro (verificação física de Arthur):**
- WORK_REFERENCE NO CAPUT = NO
- WORK_REFERENCE EM QUALQUER INCISO = nenhum
- WORK_REFERENCE EM QUALQUER PARÁGRAFO = nenhum
- WORK_REFERENCE EM QUALQUER ALÍNEA = nenhuma
- TOTAL WORK_REFERENCE = 0
- STATUS = **ZERO_COVERAGE** · **CONFIRMED_REFERENCE_GAP**

### Art. 202

1. Existe WORK_REFERENCE? **NÃO** (0 no artigo inteiro).
2. Target exato: —
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **SIM** — vínculos não-obra no artigo: CORRELATA/CURRENT_VISIBLE 4, JURISPRUDENCE/CURRENT_VISIBLE 1

**Auditoria do artigo inteiro (verificação física de Arthur):**
- WORK_REFERENCE NO CAPUT = NO
- WORK_REFERENCE EM QUALQUER INCISO = nenhum
- WORK_REFERENCE EM QUALQUER PARÁGRAFO = nenhum
- WORK_REFERENCE EM QUALQUER ALÍNEA = nenhuma
- TOTAL WORK_REFERENCE = 0
- STATUS = **ZERO_COVERAGE** · **CONFIRMED_REFERENCE_GAP**

### Art. 205

1. Existe WORK_REFERENCE? **SIM** (1 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.205:CAPUT` — Cidadania no Brasil: O Longo Caminho (EXP-LIV-004, LIVRO) — score 6.9 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.205`, via ART↔CAPUT)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO**

### Art. 220

1. Existe WORK_REFERENCE? **SIM** (4 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.220:CAPUT` — The Post: A Guerra Secreta (REF-FIL-0006, FILME) — score 8.4 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.220`, via ART↔CAPUT)
   - `CF88:ART.220:PAR.2` — 1984 (REF-LIV-0001, LIVRO) — score 8.3 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.220:PAR.2`)
   - `CF88:ART.220:PAR.2` — The Post: A Guerra Secreta (REF-FIL-0006, FILME) — score 9.2 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.220:PAR.2`)
   - `CF88:ART.220:PAR.2` — V de Vingança (REF-FIL-0002, FILME) — score 8.5 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.220:PAR.2`)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO**

### Art. 225

1. Existe WORK_REFERENCE? **SIM** (2 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.225:CAPUT` — Chernobyl (REF-SER-0003, SÉRIE) — score 8.4 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.225`, via ART↔CAPUT)
   - `CF88:ART.225:CAPUT` — O Preço da Verdade (REF-FIL-0007, FILME) — score 8.8 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.225`, via ART↔CAPUT)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO**

### Art. 227

1. Existe WORK_REFERENCE? **SIM** (1 no artigo inteiro).
2. Target exato, obra e score:
   - `CF88:ART.227:CAPUT` — Quarto de Despejo (REF-LIV-0004, LIVRO) — score 7.4 — botão 4 no DEVICE atual: **YES** (exibido em `CF88:ART.227`, via ART↔CAPUT)
3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **NÃO** — vínculos não-obra no artigo: JURISPRUDENCE/CURRENT_VISIBLE 4

