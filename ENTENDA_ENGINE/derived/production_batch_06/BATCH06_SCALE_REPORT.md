# ENTENDA_CF_PRODUCTION_BATCH_06 — relatório de escala (recalibração de risco)

Data de referência: 2026-10-04 · gerado por `ENTENDA_ENGINE/build_entenda_batch06_candidate.py` (determinístico, só conteúdo versionado) · **WIP: nenhum ENTENDA do Batch06 aprovado** (0 HUMAN_APPROVED_T1 novos; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF).

## Seleção

| | |
|---|---|
| Targets analisados | 318 (309 vigentes + 9 históricos excluídos) |
| SELECT | 96 = 93 explicações novas + 3 pilotos reutilizados |
| SKIP | 213 (todos com motivo e explicação que os cobre) |
| Sub-blocos (vigentes / novas / reutilizadas / SKIP) | A 17/5/0/12 · B 153/44/0/109 · C 92/25/3/64 · D 47/19/0/28 |
| Papéis das novas | BLOCK 25, DEVICE 25, ITEM 10, OVERVIEW 33 |

## Dois eixos

- **LEGAL_RISK** — há risco real de interpretação jurídica incorreta?
- **VERIFICATION_COMPLEXITY** — quão difícil é verificar o draft deterministicamente?
Número, percentual, prazo, idade, votos, quórum, BLOCK, lista, artigo longo, remissão simples, dependência de lei e emenda constitucional elevam só a complexidade.

| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |
|---|---|---|---|---|
| LOW | 46 | | SIMPLE | 5 |
| MEDIUM | 36 | | STRUCTURED | 59 |
| HIGH | 11 | | EXTERNAL | 29 |

Jurisprudência: CONTEXT_ONLY 15, NONE 72, REQUIRED_FOR_CORRECTNESS 6 (CONTEXT_ONLY não gera D; REQUIRED_FOR_CORRECTNESS é gatilho de D).

## Filas

| Fila | Agora | Checkpoint |
|---|---|---|
| A_CLEAN_LOW | 42 | 1 |
| B_CLEAN_MEDIUM | 27 | 0 |
| C_QUICK_REVIEW | 13 | 3 |
| D_FULL_HUMAN_REVIEW | 11 | 89 |
| E_HARD_FAIL | 0 | 0 |

Risco no checkpoint: HIGH 89, LOW 3, MEDIUM 1.

**Migração dos 89 D antigos:** 78 saíram de D → A_CLEAN_LOW 38, B_CLEAN_MEDIUM 27, C_QUICK_REVIEW 13, D_FULL_HUMAN_REVIEW 11.

## Motivos dos D restantes

- CONSTITUTIONAL_AMBIGUITY: 1
- INTERPRETIVE_CONTROVERSY: 2
- JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: 6
- SANCTION_WITH_INTERPRETATION: 4

- `CF88:ART.51:INC.I` — SANCTION_WITH_INTERPRETATION: crimes de responsabilidade + "tema de interpretação constitucional"
- `CF88:ART.52:INC.X` — INTERPRETIVE_CONTROVERSY: "objeto de debate"
- `CF88:ART.52:PAR.UNICO` — SANCTION_WITH_INTERPRETATION: perda do cargo + "questão de interpretação constitucional"
- `CF88:ART.53:CAPUT` — JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: marcador do draft: "é definida pela interpretação"
- `CF88:ART.53:PAR.1` — JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: marcador do draft: "delimitados pela interpretação"
- `CF88:ART.53:PAR.2` — SANCTION_WITH_INTERPRETATION: presos + "questão de interpretação constitucional"
- `CF88:ART.55:INC.VI` — JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: marcador do draft: "Não se deve concluir apenas"; INTERPRETIVE_CONTROVERSY: "gera dúvidas"; SANCTION_WITH_INTERPRETATION: condenação criminal + "questão tratada pela interpretação constitucional"
- `CF88:ART.58:PAR.3` — JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: marcador do draft: "são definidos pela interpretação"
- `CF88:ART.62:PAR.6` — JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: marcador do draft: "delimitado pela interpretação"
- `CF88:ART.63` — JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS: nota JURISPRUDENCIA + CONDITION_NOT_IN_TEXT ("desde que guardem relação com o tema do projeto")
- `CF88:ART.75` — CONSTITUTIONAL_AMBIGUITY: "não é definido nesta explicação"

## Achados que ainda pedem revisão (REVIEW_REQUIRED)

- CONDITION_NOT_IN_TEXT: 1
- EXCEPTION_OR_RESSALVA_DROPPED: 1
- EXTERNAL_FACT_NEEDS_PROVENANCE: 1
- HISTORICAL_CLAIM_UNVERIFIED: 7
- LIST_ITEM_POSSIBLY_DROPPED: 6

## Falsos positivos corrigidos por regra geral (validator v3)

- AUTOMATIC_CONSEQUENCE: 2 alerta(s) rebaixado(s) para INFO
- TELEOLOGY_SPECULATIVE: 7 alerta(s) rebaixado(s) para INFO
- UNIVERSAL_CLAIM: 7 alerta(s) rebaixado(s) para INFO
- "incentivo(s)" como substantivo do próprio texto ou como matéria da lei não é teleologia; "todos os"/"só pode" que reproduzem quórum/condição explícitos não são universalização; "automaticamente" expresso no artigo não é consequência inventada.
- Rótulo truncado do fato externo ("Lei Complementar nº 7") passa a mostrar a identificação inteira; fato só na camada externa vai para C (o núcleo T1 não depende dele).

## Correções editoriais desta rodada (ROUND_0B)

21 edições em 19 explicações: DUPLICATION 1, EC_EVIDENCE 1, EXTERNAL 1, LONG_SENTENCE 8, RESSALVA 1, SEMANTIC 2, TELEOLOGY 7 (antes/depois em `RECALIBRATION_EDITORIAL_LOG.json`).

## Volume para o humano

| Métrica | Caracteres |
|---|---|
| Rascunhos (5 seções + glossário) | 124.343 |
| Modelo antigo (pacote completo de todos os itens) | 245.266 |
| Checkpoint (pacotes apresentados, D=89) | 265.430 |
| **Agora (pacotes apresentados)** | **96.146** |
| — BATCH06_COMPACT_CLEAN_REVIEW.md | 54.547 |
| — BATCH06_FULL_HUMAN_REVIEW.md | 31.787 |
| — BATCH06_HARD_FAIL_REPORT.md | 119 |
| — BATCH06_QUICK_REVIEW.md | 9.693 |
| Redução vs. modelo antigo | 149.120 (60.8%) |
| Redução vs. checkpoint | 169.284 (63.8%) |

Pacote D: GERADO (limite do diagnóstico: 40% em D).

## Dependências externas

- `CF88:ART.45:PAR.1`: Lei Complementar nº 78, de 1993 · resolver EXTERNAL_EVIDENCE_LOCAL_PENDING via RELATIONS_ENGINE_PENDING

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
- Nenhum check interpreta juridicamente o dispositivo: eles roteiam risco para revisao humana.
