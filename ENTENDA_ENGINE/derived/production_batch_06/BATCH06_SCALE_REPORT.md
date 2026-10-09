# ENTENDA_CF_PRODUCTION_BATCH_06 — relatório de escala (recalibração de risco)

Data de referência: 2026-10-04 · gerado por `ENTENDA_ENGINE/build_entenda_batch06_candidate.py` (determinístico, só conteúdo versionado) · **WIP: nenhum ENTENDA do Batch06 aprovado** (0 HUMAN_APPROVED_T1 novos; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF).

## Seleção

| | |
|---|---|
| Targets analisados | 318 (309 vigentes + 9 históricos excluídos) |
| SELECT | 96 = 93 explicações novas + 3 pilotos reutilizados |
| SKIP | 213 (todos com motivo e explicação que os cobre) |
| Sub-blocos (vigentes / novas / reutilizadas / SKIP) | A 17/5/0/12 · B 153/44/0/109 · C 92/25/3/64 · D 47/19/0/28 |
| Papéis das novas | BLOCK 18, DEVICE 18, ITEM 7, OVERVIEW 26 |

## Dois eixos

- **LEGAL_RISK** — há risco real de interpretação jurídica incorreta?
- **VERIFICATION_COMPLEXITY** — quão difícil é verificar o draft deterministicamente?
Número, percentual, prazo, idade, votos, quórum, BLOCK, lista, artigo longo, remissão simples, dependência de lei e emenda constitucional elevam só a complexidade.

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 42 | | SIMPLE | 5 |
| MEDIUM | 27 | | STRUCTURED | 54 |
| HIGH | 0 | | EXTERNAL | 10 |

Jurisprudência: CONTEXT_ONLY 9, NONE 60 (CONTEXT_ONLY não gera D; REQUIRED_FOR_CORRECTNESS é gatilho de D).

## Filas

| Fila | Agora | Checkpoint |
|---|---|---|
| A_CLEAN_LOW | 42 | 1 |
| B_CLEAN_MEDIUM | 27 | 0 |
| C_QUICK_REVIEW | 0 | 3 |
| D_FULL_HUMAN_REVIEW | 0 | 65 |
| E_HARD_FAIL | 0 | 0 |

Risco no checkpoint: HIGH 65, LOW 3, MEDIUM 1.

**Migração dos 65 D antigos:** 65 saíram de D → A_CLEAN_LOW 38, B_CLEAN_MEDIUM 27.

## Rodada D (revisão jurídica humana dos 11 itens D)

Escopo `CF88_BATCH06_TRIAGE_QUEUE_D, CF88_BATCH06_TRIAGE_QUEUE_C` · decisões em `ROUND_D_HUMAN_REVIEW_DECISIONS.json` · 10 aprovados sem alteração jurídica · 14 ajustados e aprovados · 0 rejeitados.

| Target | Versão aprovada | Decisão | Proveniência | Portão de checks |
|---|---|---|---|---|
| `CF88:ART.43` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.45:PAR.1` | v1 | APPROVED | 1 item(ns) | PASS |
| `CF88:ART.51:INC.I` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.52:INC.X` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.52:PAR.UNICO` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.53:CAPUT` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.53:PAR.1` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.53:PAR.2` | v2 | APPROVED_AFTER_ADJUSTMENT | 3 item(ns) | PASS |
| `CF88:ART.53:PAR.3` | v2 | APPROVED_AFTER_ADJUSTMENT | 1 item(ns) | PASS |
| `CF88:ART.54:INC.I` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.55:INC.VI` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.55:PAR.2` | v1 | APPROVED | 1 item(ns) | PASS |
| `CF88:ART.57` | v2 | APPROVED_AFTER_ADJUSTMENT | 1 item(ns) | PASS |
| `CF88:ART.57:PAR.6` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.58:PAR.3` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.61` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.61:PAR.1` | v2 | APPROVED_AFTER_ADJUSTMENT | 0 item(ns) | PASS |
| `CF88:ART.62` | v2 | APPROVED_AFTER_ADJUSTMENT | 1 item(ns) | PASS |
| `CF88:ART.62:PAR.6` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.63` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |
| `CF88:ART.66:PAR.4` | v1 | APPROVED | 1 item(ns) | PASS |
| `CF88:ART.71` | v1 | APPROVED | 0 item(ns) | PASS |
| `CF88:ART.73:PAR.1` | v2 | APPROVED_AFTER_ADJUSTMENT | 1 item(ns) | PASS |
| `CF88:ART.75` | v2 | APPROVED_AFTER_ADJUSTMENT | 2 item(ns) | PASS |

Versões anteriores preservadas como RETIRED: 14 (v1 dos ajustados).
Acervo HUMAN_APPROVED_T1: 289 antes → **313** depois (+24 do Batch06; os 3 pilotos reutilizados não são contados de novo). Batch06 novos ainda pendentes: **69** (A, B e C não foram decididos).

## Motivos dos D pendentes



## Achados que ainda pedem revisão (REVIEW_REQUIRED)

- nenhum

## Falsos positivos corrigidos por regra geral (validator v3)

- AUTOMATIC_CONSEQUENCE: 1 alerta(s) rebaixado(s) para INFO
- TELEOLOGY_SPECULATIVE: 4 alerta(s) rebaixado(s) para INFO
- UNIVERSAL_CLAIM: 6 alerta(s) rebaixado(s) para INFO
- "incentivo(s)" como substantivo do próprio texto ou como matéria da lei não é teleologia; "todos os"/"só pode" que reproduzem quórum/condição explícitos não são universalização; "automaticamente" expresso no artigo não é consequência inventada.
- Rótulo truncado do fato externo ("Lei Complementar nº 7") passa a mostrar a identificação inteira; fato só na camada externa vai para C (o núcleo T1 não depende dele).

## Correções editoriais desta rodada (ROUND_0B)

21 edições em 19 explicações: DUPLICATION 1, EC_EVIDENCE 1, EXTERNAL 1, LONG_SENTENCE 8, RESSALVA 1, SEMANTIC 2, TELEOLOGY 7 (antes/depois em `RECALIBRATION_EDITORIAL_LOG.json`).

## Volume para o humano

| Métrica | Caracteres |
|---|---|
| Rascunhos (5 seções + glossário) | 90.413 |
| Modelo antigo (pacote completo de todos os itens) | 171.470 |
| Checkpoint (pacotes apresentados, D=89) | 265.430 |
| **Agora (pacotes apresentados)** | **55.054** |
| — BATCH06_COMPACT_CLEAN_REVIEW.md | 54.547 |
| — BATCH06_FULL_HUMAN_REVIEW.md | 218 |
| — BATCH06_HARD_FAIL_REPORT.md | 119 |
| — BATCH06_QUICK_REVIEW.md | 170 |
| Redução vs. modelo antigo | 116.416 (67.9%) |
| Redução vs. checkpoint | 210.376 (79.3%) |

Pacote D: GERADO (limite do diagnóstico: 40% em D).

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
