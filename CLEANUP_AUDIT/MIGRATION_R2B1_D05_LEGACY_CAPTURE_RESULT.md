# Migração R2B1 — resultado do capture legado D05

## 1. Resultado e escopo

O artefato independente `CLEANUP_AUDIT/D05_LEGACY_SELECTION_CAPTURE.json` foi construído exclusivamente a partir da evidência legada permitida, canonizado e selado antes de qualquer consulta operacional a Registry, Dataset Lock, Golden Reference, Shadow Resolver, resolved selection ou triple parity.

- HEAD do pre-flight: `19d116a6635da64ef9f8f5d8994fe9cc8ca85515`.
- Autoridade do capture: `LEGACY_OBSERVATION`.
- Pipeline P1/P2 executado nesta missão: **não**.
- Replay novo executado nesta missão: **não**.
- Consumidor legado alterado: **não**.
- Conteúdo funcional alterado: **não**.
- Comparação Legacy × Shadow executada: **não**.

## 2. Fontes usadas antes do selo

Somente estas fontes tiveram o conteúdo lido para construir e interpretar o capture:

| fonte | uso | SHA-256 |
|---|---|---|
| `CLEANUP_AUDIT/MIGRATION_R2A_D05_LEGACY_SHADOW_SPEC.md` | contrato R2A narrativo | `cc107fc01607b0abbbf14b44fcdee8c0eba4507db6ba345b4c42fd64c233a780` |
| `CLEANUP_AUDIT/MIGRATION_R2A_D05_LEGACY_SHADOW_SPEC.json` | contrato R2A estruturado | `74fefbc5e379723033f5afb9024865a90e34439e45af7eef5e325dc18d5a5249` |
| `CLEANUP_AUDIT/D05_REPLAY_RUN.json` | evidência primária A5B, eventos de leitura, hashes, cardinalidades e outputs | `24b934fc5a578314ba3dbf27ae567c8f79c271e9c2ced97f19ec6df5efaebc82` |
| `CLEANUP_AUDIT/MIGRATION_A5B_D05_REPLAY_RESULT.md` | evidência complementar A5B | `37796dfa97cf8e973603f59459e30545a1e78bafc19fff8926032b4a5f672716` |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/compilar_catalogo.py` | interpretação semântica; não executado | `4e53ca2a87bd0577facb4461b09b685223c4daabe869cfaff81610e6cdc66a7d` |
| `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py` | interpretação semântica; não executado | `d0621feaeaf0288285475cebc747ffad76a4cb40a8e65ec076b8541bb5053a08` |

`MIGRATION_A5A_D05_REPLAY_PLAN.md` não foi necessário e não foi lido.

## 3. Fontes proibidas antes do selo

Não foram lidos nem usados operacionalmente antes do selo:

- `ARTIFACT_REGISTRY/index.json`;
- `ARTIFACT_REGISTRY/datasets/d05.catalogo-expansao-200.json`;
- `DATASET_LOCKS/d05-historical-parity-v1.lock.json`;
- `CLEANUP_AUDIT/D05_GOLDEN_REFERENCE.json`;
- `CLEANUP_AUDIT/D05_TRIPLE_PARITY.json`;
- `CLEANUP_AUDIT/D05_SHADOW_RESOLVED_SELECTION.json`;
- `SHADOW_RESOLVER/*`.

Também não foram executados os verificadores de Registry, Lock ou Shadow. A enumeração dos membros, as ordens, a multiplicidade e a classificação de observabilidade não receberam dados dessas fontes.

Garantia de independência: **SIM**.

## 4. Conjuntos diretamente observados

O capture materializa 318 eventos de membro diretamente observados, sem deduplicação:

| conjunto | fase | eventos | ordem |
|---|---:|---:|---|
| `triage_batch_paths` | P1 | 8 | `OBSERVED`, `LOTE_01..08` |
| `base_catalog_work_ids` | P1 | 199 | `OBSERVED`, na sequência registrada pelo audit hook |
| `enrichment_overlay_paths_build_order` | P2 | 111 | `OBSERVED`, na sequência registrada pelo audit hook |

Cada evento conserva path, sequência observada, índice zero-based dentro de `observed_reads` da fase, papel legado, método de observação e índice de multiplicidade. Os códigos `LOTE_*` e `EXP2-*` extraídos do filename são marcados como derivação lexical do próprio path observado.

Os 318 eventos do capture não devem ser confundidos com os 507 itens diretamente correspondentes da cobertura de planejamento R2A/A6. O capture registra eventos de leitura legados; R2A registra uma dimensão de correspondência futura entre conjuntos. Foram preservados no resumo, sem declarar 1.699 itens runtime-observed: 507 correspondentes observados, 707 relevantes às fases P1/P2, 200 sem event-level e 992 fora das fases executadas.

## 5. Conjuntos derivados

| conjunto | cardinalidade comprovada | valores materializados | situação |
|---|---:|---:|---|
| `triage_candidate_numbers` | 200 | 0 | cardinalidade e unicidade derivadas da concatenação e assert legado; valores não embutidos nas fontes permitidas |
| `catalog_69_ids` | 69 | 0 | cardinalidade e regra `sorted(..., id)` comprovadas; IDs não embutidos nas fontes permitidas |
| `enrichment_queue_work_ids` | 111 | 111 | conjunto fechado derivado dos overlays observados, das ausências afirmadas pelo P2 e da igualdade de cardinalidade pós-indexação |
| `post_codex_revision_members` | 3 | 0 | cardinalidade aplicada/pós-indexação comprovada; `evidence_id` não embutidos nas fontes permitidas |

Há 383 ocorrências de membro com cardinalidade comprovada nos quatro conjuntos derivados. Destas, 111 identidades legadas foram materializadas e 272 ficaram explicitamente em nível de cardinalidade, sem consultar os próprios arquivos de dados ou contratos sombra para preencher valores ausentes.

Todos os 111 membros materializados da fila têm classificação `DERIVED_FROM_OBSERVED_LEGACY_INPUT`, `derived_from`, regra de derivação e fontes de evidência. Nenhum deles é rotulado como observação direta.

## 6. Conjuntos não observáveis ou não aplicáveis

- `enrichment_checkpoints`: `NOT_RUNTIME_OBSERVABLE`; fase histórica não executada.
- `enrichment_capture_paths_lexical`: `NOT_RUNTIME_OBSERVABLE`; coleta remota excluída.
- `outer_manifest_member_paths`: `NOT_RUNTIME_OBSERVABLE`; fechamento histórico não executado.
- `enriched_payload_paths`: `NOT_APPLICABLE`; são outputs P2 e não membros da seleção de inputs.

Nenhum conjunto histórico foi preenchido por Shadow, Golden, Lock ou Registry.

## 7. Ordem

- Lotes, dossiês e overlays conservam `observed_sequence` exatamente como registrada em A5B.
- A sequência dos 200 números de candidatura é `DERIVED_FROM_LEGACY`, mas seus valores não foram materializados porque não estão embutidos nas fontes permitidas.
- O catálogo 69 tem regra derivada por `id`, sem materialização dos IDs.
- A fila de enriquecimento é `NOT_OBSERVABLE_NOT_CONSUMED`: o checkpoint é transformado em dict e P2 consome membership, não a ordem persistida.
- Revisões formam conjunto sem ordem contratual.
- Ordens de fases históricas e outputs enquanto input selection são `NOT_OBSERVABLE` ou `NOT_APPLICABLE`.

Nenhum ordinal do Dataset Lock foi usado.

## 8. Multiplicidade

Eventos repetidos seriam preservados; não houve deduplicação por path, ID, conteúdo ou SHA-256.

- Lotes: concatenação preservadora; 8 leituras explícitas.
- Dossiês: 199 eventos, um por entrada utilizável observada.
- Overlays: 111 eventos, um por path existente observado.
- Fila: `POST_INDEX_MULTIPLICITY = 111`; `PRE_INDEX_MULTIPLICITY = NOT_OBSERVABLE` porque o array não está embutido nas fontes permitidas.
- Revisões: cardinalidade pós-indexação/aplicada = 3; multiplicidade pré-indexação não observável.
- Capturas remotas: tentativas versus arquivos finais não observáveis nas fases executadas.

## 9. Leituras auxiliares

Foram registradas separadamente 11 leituras não promovidas a membros de seleção:

- 2 scripts executados, classificados como suporte executável;
- 2 releituras de outputs P1 para hash;
- 7 releituras de outputs P2 para hash e/ou manifesto interno.

O catálogo-base P1 lido por P2 não foi classificado como auxiliar: ele é dependência funcional direta.

## 10. Outputs separados

Os nove outputs A5B estão exclusivamente em `observed_outputs` e não entram em `selection_sets.items`:

- 2 catálogos-base;
- 7 arquivos `ENRIQUECIDO_V1`;
- 9/9 `BYTE_IDENTICAL`.

Outputs separados corretamente: **SIM**.

## 11. Dependências legadas observadas

| dependência | consumo capturado |
|---|---|
| `catalog_69` | `EMBEDDED`; wrapper congelado diretamente lido em P1 e P2; ocorrência externa `NOT_DIRECTLY_OPENED` |
| `base_catalog` | produzido por P1 e `DIRECT_READ` por P2 |
| `enrichment_checkpoint_state` | `DIRECT_READ`, depois indexado por `work_id` |
| `enrichment_revision_layer` | `DIRECT_READ`, depois indexado por `evidence_id` |

Não houve comparação com as dependências do Dataset Lock.

## 12. Ausências

- 1 `CANDIDATE_EXCLUDED_FROM_USABLE_CATALOG`: `DERIVED_LEGACY_ABSENCE`, identidade não embutida.
- 88 `NO_ENRICHMENT_OVERLAY_BY_DESIGN`: `DERIVED_LEGACY_ABSENCE`, IDs enumerados pelo conjunto diferença entre os 199 dossiês-base e os 111 overlays observados.
- 47 `NO_ADDITIONAL_CARD_AFTER_EXAMINATION`: `DERIVED_LEGACY_ABSENCE`, identidades não embutidas.
- 15 ausências de coleta remota: `NOT_OBSERVABLE`, correspondentes a 9 receipts locais incompletos e 6 falhas remotas preservadas apenas fora das fases executadas.

Cobertura de ausências: 136 deriváveis nas fases executadas e 15 não observáveis. As 151 ausências do Lock não foram artificialmente reproduzidas nem consultadas.

## 13. Cobertura e lacunas

Cobertura diretamente observável no capture: 318 eventos materializados nos três conjuntos diretamente observáveis.

Cobertura derivada: cardinalidade total comprovada de 383 membros; 111 valores materializados e 272 valores não embutidos nas fontes permitidas.

Lacunas explícitas:

1. valores dos 200 `triage_candidate_numbers`;
2. valores dos 69 `catalog_69_ids`;
3. valores dos 3 `post_codex_revision_members`;
4. multiplicidade pré-indexação da fila e das revisões;
5. membros e ordem das três fases históricas não executadas;
6. identidades de 1 candidata excluída e 47 decisões sem card adicional;
7. tentativas remotas anteriores à materialização final.

Essas lacunas não foram preenchidas por nova execução, abertura de dados fora da lista permitida ou consulta ao Shadow.

## 14. Canonicalização, selo e determinismo

O core foi escrito em UTF-8 sem BOM, somente LF, chaves ordenadas, `indent=2`, newline final e sem timestamp volátil.

- Tamanho: 397.863 bytes.
- SHA-256 selado: `c9c48e8852f3952a1c05de528a6cf25124ce264f1f86194400bea2812f460ae0`.
- Determinismo: **PASS**.

O helper temporário gerou o capture três vezes — duas cópias temporárias e o arquivo final — e as três produziram o mesmo SHA-256. O helper foi removido e não integra os artefatos R2B1. Após o cálculo do hash final, o capture não foi modificado.

## 15. Condição para R2B2

R2B2 deverá ocorrer somente em nova missão. Ela poderá verificar primeiro que o capture continua com SHA-256 `c9c48e8852f3952a1c05de528a6cf25124ce264f1f86194400bea2812f460ae0` e, apenas então, carregar Registry, Dataset Lock, Shadow Resolver, resolved selection e Golden/Triple Parity conforme o contrato aplicável. O conjunto capturado não poderá ser filtrado ou reescrito pela comparação.

R2B2 não foi iniciada.

## 16. Consolidação R2B1C — investigação do helper temporário

O path exibido durante a construção foi `C:\GitHub\LEX-MACHINA\CLEANUP_AUDIT\_tmp_build_r2b1_capture.py`.

- existência atual: não;
- tracked: não;
- untracked: não;
- staged: não;
- situação ao final da R2B1: removido conscientemente depois das três gerações determinísticas;
- função: gerador temporário evidence-only do JSON canônico;
- necessário para validar o capture selado: não;
- necessário para auditar a evidência: não;
- efeito da ausência: não compromete a auditabilidade do artefato existente, pois o capture conserva fontes e hashes, regras de derivação, eventos, cardinalidades e formato canônico, e seu selo pode ser validado diretamente; a ausência apenas significa que não há um comando auxiliar versionado para regeneração automática bit a bit.

Classificação: `TEMPORARY_HELPER_REMOVED`.

O helper não deve ser recriado nem versionado nesta consolidação.

## 17. Reconciliação exata de 707 versus 701

```text
R2A_RELEVANT_TOTAL = 707
R2B1_DIRECT = 318
R2B1_DERIVED = 383
R2B1_SELECTION_MEMBERS_OR_CARDINALITIES = 701
REMAINDER = 6
REMAINDER_EXPLANATION = enriched_payload_paths: seis outputs P2 relevantes à fase executada, mas NOT_APPLICABLE como seleção de inputs
UNRESOLVED_COUNT_GAP = 0
```

Os seis restantes são exatamente os seis filenames que P2 materializa antes de construir o manifesto interno:

1. `CATALOGO_EXPANSAO_ENRIQUECIDO_V1.json`;
2. `CATALOGO_TOTAL_ENRIQUECIDO_V1.json`;
3. `EVIDENCE_CARDS_ENRIQUECIDOS_V1.json`;
4. `DECISOES_ENRIQUECIMENTO.json`;
5. `METADADOS_ENRIQUECIDO_V1.json`;
6. `README.md`.

A R2A classifica `enriched_payload_paths` como `NOT_APPLICABLE_TO_EXECUTED_CONSUMER` para a seleção de inputs e declara que seus filenames únicos representam seis outputs, não inputs. Por isso eles pertencem aos 707 itens relevantes a P1/P2, mas não entram nos 318 eventos diretamente observados nem nos 383 membros/cardinalidades derivados da `LEGACY_SELECTION` R2B1.

O sétimo output `ENRIQUECIDO_V1`, `MANIFEST.json`, é produzido depois a partir da descoberta ordenada desses seis payloads e está preservado entre os nove `observed_outputs`; ele não é um dos seis `enriched_payload_paths`. A classificação do remainder é `OUTPUT_NOT_SELECTION` e `COUNTING_MODEL_DIFFERENCE`, não lacuna de membro.

Assim, `701 selection members/cardinalities + 6 phase-relevant output paths = 707 executed-phase-relevant items`. O remainder 6 está formalmente resolvido sem Registry, Lock, Golden ou Shadow.

## 18. Decomposição dos 272 valores não embutidos

| set_id | cardinalidade | motivo da indisponibilidade individual | limite para R2B2 |
|---|---:|---|---|
| `triage_candidate_numbers` | 200 | A evidência permitida autentica as oito leituras, a concatenação, a cardinalidade 200 e a unicidade afirmada pelo legado, mas não embute os valores `number` dos arrays | apenas cardinalidade e regras de ordem/multiplicidade; identidade member-level não pode ser afirmada sem nova evidência legada |
| `catalog_69_ids` | 69 | A evidência permitida autentica o wrapper lido e a cardinalidade 69, mas não embute os valores `id` de `ref['obras']` | apenas cardinalidade e semântica `sorted(..., id)`; identidade member-level não pode ser afirmada sem nova evidência legada |
| `post_codex_revision_members` | 3 | A evidência permitida comprova três revisões aplicadas e a igualdade entre o conjunto aplicado e as chaves pós-indexação, mas não embute os três `evidence_id` | apenas cardinalidade pós-indexação/aplicada; identidade member-level e multiplicidade pré-indexação não podem ser afirmadas sem nova evidência legada |
| **total** | **272** | `200 + 69 + 3` | limitação explícita de observabilidade |

R2B2 não poderá usar Registry, Lock, Golden ou Shadow para retropreencher esses valores como se fossem observação legada. Para esses três conjuntos, a comparação fica limitada à cardinalidade e às semânticas comprovadas. Paridade member-level somente seria possível com nova evidência legada independente, em missão e autorização próprias. Os 111 `enrichment_queue_work_ids` derivados já estão materializados e não compõem os 272.

A independência permanece preservada: antes do selo, Artifact Registry, Dataset Lock, Golden Reference, Shadow Resolver, `D05_SHADOW_RESOLVED_SELECTION.json` e `D05_TRIPLE_PARITY.json` não determinaram membros, ordem, multiplicidade ou classificação do capture.

## Resultado

`MIGRACAO_R2B1_CONCLUIDA — LEGACY_CAPTURE_SELADO`
