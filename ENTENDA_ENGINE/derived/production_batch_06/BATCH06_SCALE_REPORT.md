# ENTENDA_CF_PRODUCTION_BATCH_06 — relatório de escala (rascunho + triagem)

Data de referência: 2026-10-04 · base `f1a6966` · tag `entenda-batch05-t1-frozen-2026-10-04` intacta (aponta para `342ab9a`).
Escopo: CF88 arts. 42–75. A missão termina na triagem: **0 HUMAN_APPROVED_T1 concedidos**. AUTO_APPROVE_LOW e AUTO_APPROVE_MEDIUM estão OFF; MICROAUTO_APPLY está OFF.
Nada foi commitado, tagueado, enviado (push) ou colocado em staging físico. Batch05, Lei Seca, firmware, Relations Engine e SD não foram alterados: nenhum arquivo rastreado foi modificado.

## Totais

| | |
|---|---|
| Targets analisados | 318 (309 CURRENT + 9 HISTORICAL excluídos: art. 42 §§ 4º–11 e art. 62, parágrafo único) |
| SELECT | 96 = 93 explicações novas + 3 pilotos aprovados reutilizados (art. 60, art. 60 § 4º, art. 60 § 4º IV) |
| SKIP | 213, todos com motivo: 141 pela visão geral do artigo, 52 subdivisões de bloco, 20 irmãos cobertos por bloco |
| Por sub-bloco (CURRENT / novos / SKIP) | A 17/5/12 · B 153/44/109 · C 92/25/64 · D 47/19/28 |
| Papéis das novas | 33 OVERVIEW · 25 BLOCK · 25 DEVICE · 10 ITEM |
| Risco | LOW 3 · MEDIUM 1 · HIGH 89 |
| Filas | A 1 · B 0 · C 3 · D 89 · E 0 |
| BLOCKs | 25 novos (+1 reutilizado) |
| Dependências externas | 2: art. 45 § 1º (LC 78/1993: resolver → `EXTERNAL_EVIDENCE_LOCAL_PENDING`, relação PENDING, **não promovida**) e art. 75 (EC 139/2026: `EXTERNAL_VERIFICATION_REQUIRED` na nota) |
| Itens com jurisprudência | 21 com nota genérica "camada JURISPRUDÊNCIA" (nenhum tribunal, número ou tema no corpo) · 0 recomendações de vínculo |
| Micro-ajustes automáticos | 0 aplicados · 41 elegíveis (NEAR_COPY_MICROFIX) registrados sem aplicação em `MICRO_ADJUSTMENTS_LOG.json` |
| Edições da redação (round 0, antes da triagem) | 17 correções + 19 adições de glossário, registradas em `ROUND_0_EDITORIAL_LOG.json` |
| editorial_checks | Achados reais corrigidos no texto na rodada 0. Depois dela, 25 achados: 13 falsos positivos resolvidos com justificativa (12 itens) e 12 abertos (9 LONG_SENTENCE, 1 par DUPLICATION 62 § 1º × 68 § 1º, 1 LAW_DEPENDENCY_OMITTED no art. 49) |

## Volume de apresentação

| Métrica | Caracteres |
|---|---|
| Total dos rascunhos (5 seções + glossário) | 124.028 |
| Modelo antigo (pacote completo de todos os itens) | 249.608 |
| Apresentado (4 pacotes) | 265.430 (A/B 1.151 · C 2.281 · D 261.879 · E 119) |
| **Redução** | **−6,3 % (aumento)** |

Não houve redução porque 89 dos 93 itens são HIGH, e a regra de escalonamento manda todo item HIGH para o pacote completo D. O pacote D também acrescenta, por item, gatilhos, vigência e checks.

O conteúdo dos arts. 42–75 é denso. Com os gatilhos da missão aplicados literalmente, alguma regra dispara em quase todo artigo: emenda, quórum, prazo, número, imunidade/sanção, ressalva ou lei complementar.

Simulações de calibração (não aplicadas):

| Ajuste simulado | Itens HIGH |
|---|---|
| EC_WORDING só para emendas de 2019 em diante | 86 |
| + sem NUMBER_OR_PERCENTAGE | 84 |
| + sem DEADLINE | 76 |
| + sem BLOCK_MULTI_DEPENDENCY | 74 |

Afrouxar gatilhos não resolve o volume. Se a meta é reduzir o volume, a alavanca é o formato: um "D enxuto", mostrando a Lei Seca e só as frases que acionaram cada gatilho. A decisão é humana.

## Falsos positivos (validator v2, 25 alertas REVIEW_REQUIRED fora do editorial_checks: 17 falsos positivos, 8 verdadeiros)

- **TELEOLOGY_SPECULATIVE: 14 alertas, 7 falsos positivos.**
  - Falsos positivos: o substantivo "incentivo(s)", que é termo da própria Lei Seca (arts. 43 e 43 § 2º; arts. 68 e 68 § 2º nos exemplos).
  - Verdadeiros (7): teleologia que o texto não declara, nos arts. 49 V, 53 § 3º, 57 § 2º, 62 § 1º, 62 § 6º, 64 § 2º e 67. Nesses casos a fila está correta.
- **UNIVERSAL_CLAIM: 7 de 7 falsos positivos.** "todos os membros" e "só pode" reproduzem quóruns e condições do próprio texto (arts. 43 § 2º, 46, 47, 51 I, 55, 67, 69).
- **AUTOMATIC_CONSEQUENCE: 2 de 2 falsos positivos.**
  - 54 I: definição de cargo ad nutum.
  - 57 § 7º: o § 8º diz "automaticamente incluídas".
- **EXCEPTION_OR_RESSALVA_DROPPED: 1 falso positivo.** No art. 54 I o exemplo descreve justamente a exceção das cláusulas uniformes.
- **EXTERNAL_FACT_NEEDS_PROVENANCE: 1 verdadeiro.** Art. 45 § 1º, LC 78/1993: o rótulo do match sai truncado ("nº 7"), o que é só cosmético.
- **editorial_checks:** 13 falsos positivos resolvidos, entre eles:
  - "sempre que possível" do texto;
  - "projeto de lei" lido como dependência de lei;
  - "com exceção" fora da lista de marcadores;
  - "devendo submetê-las" tratado como mudança de modalidade.

## Padrões jurídicos novos que o validator não detecta

1. **Referente ambíguo em redação recente.** No art. 75, "vedada sua extinção, criação ou instalação": nada impede que a explicação escolha um referente para "sua". Isso foi corrigido à mão na redação (round 0) e o item foi sinalizado.
2. **Quantidade derivada escrita por extenso.** EXTRAPOLATION_NUMBER só lê algarismos. Exemplos:
   - "54 dos 81 senadores": foi pego e removido;
   - "até cento e vinte dias" (art. 62 § 3º): passaria por extenso.
   - Falta checar números por extenso contra o snapshot.
3. **Ressalva omitida de um dispositivo SKIP coberto pela visão geral.** O art. 49 II diz "ressalvados os casos previstos em lei complementar". As regras semânticas olham só o snapshot do próprio registro, e não cobram que a visão geral carregue as ressalvas dos itens que ela cobre.
4. **Jurisprudência velada.** Frases como "foi delimitado pela interpretação constitucional" (art. 62 § 6º) afirmam a existência de precedente sem citar tribunal e escapam de EXTERNAL_CASE_RE.
5. **Completude de enumeração parafraseada.** O validator não verifica se a paráfrase de uma lista (art. 61 § 1º, art. 62 § 1º, art. 68 § 1º) manteve todos os itens. EXHAUSTIVE_ENUMERATION_RISK cobre só a linguagem de exaustividade.
6. **Afirmação histórica não verificada.** "Materiais anteriores trazem outra regra" (arts. 66 § 4º, 73 § 1º, 62) depende do histórico da redação, que não é conferido.
7. **Remissão a artigo fora do snapshot afirmada como texto.** Exemplo: "nos crimes comuns, julgamento pelo Supremo (art. 102, I, b)". O pacote D lista os dispositivos citados, mas não há checagem automática do conteúdo.

## Execuções

| Suíte | Resultado |
|---|---|
| ENTENDA (inclui validator v2, Batch05, Batch06, resolver hermético e materialização git) | 164 OK |
| Batch06 | 12 OK |
| validator v2 | 18 OK |
| resolver hermético | 9 OK |
| materialização git | 2 OK |
| LEGAL_TARGET_ID | 65 OK |
| DEVICE_INTEGRATION | 353 OK |
| editorial_checks, validator v2 (triagem) e validação de targets (engine) | sem HARD_FAIL |

- **Determinismo:** 3 execuções completas do pipeline saíram byte-idênticas (20 arquivos). Um rebuild limpo (corpus e índice apagados) também reproduziu os mesmos hashes (`DETERMINISM_EVIDENCE.json`).

## Arquivos (`ENTENDA_ENGINE/derived/production_batch_06/`)

| Grupo | Arquivos |
|---|---|
| Entrada | `BATCH_SPEC.json` (inclui `no_separate_reasons` com os 108 SKIPs explícitos), `BATCH_06_DRAFTS.json`, `BATCH06_TARGET_PLAN.json` (vigência por target), `EDITORIAL_REVIEW_INPUT.json` (risco, regras de fato, termos, resoluções) |
| Build | `CF88_BATCH_06.entenda.jsonl`, `index/`, `SELECTION_REPORT.json` (SELECT/SKIP por target), `REVIEW_BATCH_06.md`, `JURISPRUDENCE_LINK_RECOMMENDATIONS.json` |
| Triagem | `EDITORIAL_CHECKS.json`, `REVIEW_BATCH_06_RISK_TRIAGE.md`, `BATCH06_TRIAGE.json`, `MICRO_ADJUSTMENTS_LOG.json`, `ROUND_0_EDITORIAL_LOG.json` |
| Pacotes | `BATCH06_COMPACT_CLEAN_REVIEW.md` (A/B), `BATCH06_QUICK_REVIEW.md` (C), `BATCH06_FULL_HUMAN_REVIEW.md` (D), `BATCH06_HARD_FAIL_REPORT.md` (E = 0) |
| Evidência | `BATCH06_MANIFEST.json`, `DETERMINISM_EVIDENCE.json` |

Módulos novos e permanentes (não commitados):

- `ENTENDA_ENGINE/t1_risk.py` (classificador LOW/MEDIUM/HIGH);
- `ENTENDA_ENGINE/t1_batch_packets.py` (filas A–E, 4 pacotes, métricas, micro-auto);
- `ENTENDA_ENGINE/tests/test_entenda_batch06.py`.

`BATCH06_SCALE_DRAFT_AND_TRIAGE_READY` — 0 novos HUMAN_APPROVED_T1.
