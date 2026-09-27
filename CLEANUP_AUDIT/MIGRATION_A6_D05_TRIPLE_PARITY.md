# Migração A6 — paridade tripla D05

## 1. Escopo

Esta etapa compara, somente em leitura, a Golden Reference histórica, o Dataset Lock sombra e a evidência do replay isolado A5B. Nenhum pipeline foi reexecutado e o Lock permanece sombra; `LEGACY_AUTHORITATIVE` continua vigente.

Pergunta de prova: **o comportamento observado no replay corresponde à seleção, ordem, multiplicidade, dependências, ausências e outputs historicamente comprovados e explicitados no Lock?**

Resposta: **sim para todas as dimensões observáveis de P1/P2, sem mismatch; há dimensões históricas deliberadamente não observáveis porque suas fases não foram executadas.**

## 2. Fontes

- Golden Reference: `CLEANUP_AUDIT/D05_GOLDEN_REFERENCE.json`, SHA-256 `f82e82d9c3907186e916a54436493ebe8f426d1a09f7b3a3aa3b092c2e09cdc7`.
- Dataset Lock: `DATASET_LOCKS/d05-historical-parity-v1.lock.json`, SHA-256 `5d9f6d0ba4fa1895f70a139510b0d441d62e187eb63ad99de030820946c29f39`.
- Replay: `CLEANUP_AUDIT/D05_REPLAY_RUN.json`, run `d05-replay-2026-09-27-a5b`.
- Registry index e fragmento D05 versionados.
- Relatórios A3, A4A, A4B, A5A e A5B apenas como explicação auxiliar.

## 3. Golden ↔ Lock

O verifier atual retorna PASS. A referência declarada pelo Lock aponta para o hash atual da Golden. Resultado formal: 855/855 ocorrências MATCH; 11 conjuntos e 1.699 itens; `MEMBER_MATCH=true`, `ORDER_MATCH=true`, `MULTIPLICITY_MATCH=true`, `ABSENCE_MATCH=true`, `DEPENDENCY_MATCH=true`, `EXTRA_ITEMS=0`.

**GOLDEN_LOCK_PARITY = PASS.**

## 4. Golden ↔ Replay

Os nove outputs registrados pela A5B têm os mesmos SHA-256 e tamanhos dos nove outputs da Golden. As seis cardinalidades requeridas também coincidem. P1/P2 observaram os inputs funcionais previstos; as fases históricas de coleta, checkpoints intermediários e fechamento do manifesto externo não foram executadas.

**GOLDEN_REPLAY_PARITY = PASS_WITH_NOT_OBSERVABLE_DIMENSIONS.**

## 5. Lock ↔ Replay por conjunto

| selection_set | itens | classificação | membros | ordem | multiplicidade |
|---|---:|---|---|---|---|
| `triage_batch_paths` | 8 | OBSERVED_MATCH | MATCH | ORDER_MATCH | MATCH |
| `triage_candidate_numbers` | 200 | NOT_OBSERVABLE_BY_REPLAY | NOT_DIRECTLY_OBSERVABLE | ORDER_NOT_OBSERVABLE | MATCH |
| `base_catalog_work_ids` | 199 | OBSERVED_MATCH | MATCH | ORDER_MATCH | MATCH |
| `catalog_69_ids` | 69 | OBSERVED_MATCH | MATCH | ORDER_MATCH | MATCH |
| `enrichment_queue_work_ids` | 111 | OBSERVED_MATCH | MATCH | ORDER_NOT_OBSERVABLE | MATCH |
| `enrichment_checkpoints` | 12 | NOT_APPLICABLE_TO_EXECUTED_PHASE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |
| `enrichment_capture_paths_lexical` | 128 | NOT_APPLICABLE_TO_EXECUTED_PHASE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |
| `enrichment_overlay_paths_build_order` | 111 | OBSERVED_MATCH | MATCH | ORDER_MATCH | MATCH |
| `enriched_payload_paths` | 6 | OBSERVED_MATCH | MATCH | ORDER_MATCH | MATCH |
| `outer_manifest_member_paths` | 852 | NOT_APPLICABLE_TO_EXECUTED_PHASE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |
| `post_codex_revision_members` | 3 | OBSERVED_MATCH | MATCH | UNORDERED_SET | MATCH |

Sete conjuntos têm seleção observada e coincidente; um conjunto executado tem sequência interna não observável; três conjuntos pertencem a fases não executadas. Não há `OBSERVED_MISMATCH`.

**LOCK_REPLAY_PARITY = PASS_WITH_NOT_OBSERVABLE_DIMENSIONS.**

## 6. Outputs

| role | golden_sha256 | replay_sha256 | golden_size | replay_size | status |
|---|---|---|---:|---:|---|
| `base_catalog` | `5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43` | `5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43` | 959745 | 959745 | **BYTE_IDENTICAL** |
| `combined_base_catalog` | `6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6` | `6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6` | 76121 | 76121 | **BYTE_IDENTICAL** |
| `enriched_catalog` | `cddb00344f6e3075f552fb042b168d184463b85e513f695eb1089139ee301da7` | `cddb00344f6e3075f552fb042b168d184463b85e513f695eb1089139ee301da7` | 1154254 | 1154254 | **BYTE_IDENTICAL** |
| `combined_enriched_catalog` | `5446da1294cee6311dcef3a0c5438b7c7de2bc2adec586fe38b85f199394305d` | `5446da1294cee6311dcef3a0c5438b7c7de2bc2adec586fe38b85f199394305d` | 69418 | 69418 | **BYTE_IDENTICAL** |
| `enrichment_decisions_output` | `de779c2f5873d665953d849d37643e21219da428df89b534a24781b8031e8c30` | `de779c2f5873d665953d849d37643e21219da428df89b534a24781b8031e8c30` | 116799 | 116799 | **BYTE_IDENTICAL** |
| `enriched_cards_flat` | `3446c073eda030045bc20efe0ac0854c924fe7b11e66a71d0671d6717f054a07` | `3446c073eda030045bc20efe0ac0854c924fe7b11e66a71d0671d6717f054a07` | 607221 | 607221 | **BYTE_IDENTICAL** |
| `enriched_metadata` | `27a427ccd18813992f633e8f94bb59e8a2e46a1d6558b95d8c37ef7e037c2f02` | `27a427ccd18813992f633e8f94bb59e8a2e46a1d6558b95d8c37ef7e037c2f02` | 11588 | 11588 | **BYTE_IDENTICAL** |
| `enriched_package_documentation` | `423b90dde03d10cd268681b55f18e6fa51007fd1af939d09b80be952a2cbe9e3` | `423b90dde03d10cd268681b55f18e6fa51007fd1af939d09b80be952a2cbe9e3` | 1269 | 1269 | **BYTE_IDENTICAL** |
| `enriched_package_manifest` | `0312e5f091981f8065673529aca04437ed0fc7ecaac26cd144d2af26ab37774c` | `0312e5f091981f8065673529aca04437ed0fc7ecaac26cd144d2af26ab37774c` | 1044 | 1044 | **BYTE_IDENTICAL** |

**OUTPUT_PARITY = 100% (9/9 BYTE_IDENTICAL).**

## 7. Seleção

- Lock completo: 1.699 itens.
- Diretamente relevantes para P1/P2: 707 itens.
- Itens com seleção observada e match: 507.
- Itens da fase executada sem observação member-level suficiente: 200 números de candidata.
- Itens de fases não executadas: 992.

`FULL_LOCK_SELECTION_PARITY = NOT_FULLY_OBSERVED`. Isso não é divergência: o replay não executou as fases correspondentes.

`EXECUTED_PHASE_SELECTION_PARITY = PASS_WITH_NOT_OBSERVABLE_DIMENSIONS`.

## 8. Ordem

Dos dez conjuntos ordenados, cinco têm ordem observada e coincidente: lotes, dossiês-base, catálogo 69 materializado nos outputs, overlays e payloads enriquecidos. A ordem dos 200 membros dentro dos lotes e a ordem histórica da fila não foram capturadas como comportamento runtime. Três sequências pertencem a fases não executadas.

Resultado: cinco `ORDER_MATCH`, dois `ORDER_NOT_OBSERVABLE` e três `NOT_APPLICABLE_TO_EXECUTED_PHASE`.

## 9. Multiplicidade

As contagens dos 707 itens relevantes a P1/P2 coincidem: 8 lotes, 200 candidatas únicas, 199 dossiês, 69 membros da referência, 111 itens de fila, 111 overlays, seis payloads e três revisões. As 992 ocorrências das fases não executadas continuam validadas Golden ↔ Lock, mas não foram observadas no replay. Nenhuma deduplicação por hash foi usada.

## 10. Ausências semânticas

| categoria | quantidade | classificação | evidência |
|---|---:|---|---|
| `NO_ENRICHMENT_OVERLAY_BY_DESIGN` | 88 | **CONFIRMED_BY_REPLAY** | 199 base works minus 111 observed overlay reads; byte-identical decisions output preserves the exact no-overlay cases |
| `CANDIDATE_EXCLUDED_FROM_USABLE_CATALOG` | 1 | **CONFIRMED_BY_REPLAY** | P1 consumed 200 unique candidates and emitted 199 usable works with byte-identical output |
| `NO_ADDITIONAL_CARD_AFTER_EXAMINATION` | 47 | **CONFIRMED_BY_REPLAY** | byte-identical decisions and metadata outputs preserve the 47 +0 decisions |
| `WEB_SOURCE_WITHOUT_COMPLETE_LOCAL_RECEIPT` | 9 | **OUTSIDE_EXECUTED_PHASE** | remote/source collection was excluded |
| `REMOTE_FETCH_FAILED_WITH_METADATA_PRESERVED` | 6 | **OUTSIDE_EXECUTED_PHASE** | remote/source collection was excluded |

Total: 151. O replay confirma 136 ausências ligadas a P1/P2; 15 pertencem à coleta remota excluída. Mismatches: zero.

## 11. Dependências

| dependência | LOCK_SELECTED | REPLAY_OBSERVED | resultado | evidência |
|---|---|---|---|---|
| `catalog_69` | sim | `FROZEN_REFERENCE_WRAPPER` | **CONSISTENT_BUT_NOT_DIRECTLY_OBSERVABLE** | P1/P2 read REFERENCIA_CATALOGO_69.json and reproduced outputs, but did not open the external CATALOG_69_ROOT occurrence itself |
| `base_catalog` | sim | `True` | **MATCH** | P1 produced the exact base catalog and P2 read it |
| `enrichment_checkpoint_state` | sim | `True` | **MATCH** | P2 audit records the exact checkpoint read |
| `enrichment_revision_layer` | sim | `True` | **MATCH** | P2 audit records the exact revision layer read and three applied revisions |

O catálogo 69 foi consumido pelo wrapper congelado; a ocorrência externa original não foi aberta no replay. As outras três dependências foram diretamente observadas.

## 12. Dimensões não observáveis

- sequência interna dos 200 números de candidata nos oito lotes;
- ordem histórica da fila de 111 itens, porque P2 a converte em mapa;
- 12 checkpoints intermediários;
- 128 capturas de fonte;
- 852 membros do manifesto externo;
- leitura direta da ocorrência externa do catálogo 69;
- nove recibos incompletos e seis falhas remotas como eventos de execução.

Esses pontos permanecem consistentes com Golden ↔ Lock, mas não são promovidos a observação de runtime.

## 13. Limites da prova

A igualdade determinística provada é específica ao run A5B, em Windows, CPython 3.12.9, UTF-8, `PYTHONHASHSEED=0` e os inputs congelados copiados. A prova não afirma reprodução em qualquer máquina ou ambiente.

## 14. Mismatches e bloqueios

`blocking_mismatches = []`. Não existe `OBSERVED_MISMATCH`, divergência de output, cardinalidade, dependência diretamente observada ou ausência executada.

## 15. Resultado agregado

`TRIPLE_PARITY_STATUS = PASS_WITH_NOT_OBSERVABLE_DIMENSIONS`.

O resultado evita um PASS absoluto porque 1.192 itens/dimensões de seleção não foram diretamente observados como seleção runtime: 200 pertencem à fase executada sem instrumentação member-level e 992 pertencem a fases não executadas.

## 16. Próximo passo recomendado

Adotar a opção A: introduzir futuramente um resolver **somente sombra e somente leitura** que leia Registry + Lock e produza uma seleção candidata para comparação. Ele não deve alimentar o pipeline nem substituir a seleção legada. `LEGACY_AUTHORITATIVE` deve permanecer explícito. Nenhuma implementação foi iniciada nesta etapa.
