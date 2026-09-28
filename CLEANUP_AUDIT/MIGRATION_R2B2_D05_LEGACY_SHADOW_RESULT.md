# Migração R2B2 — comparação LEGACY_SELECTION × SHADOW_RESOLVED_SELECTION

## 1. Escopo e selos

A comparação foi executada somente sobre evidência existente. Nenhum pipeline, replay, compilador, gerador de manifesto, coleta remota ou consumidor foi executado ou alterado.

- Legacy capture: `CLEANUP_AUDIT/D05_LEGACY_SELECTION_CAPTURE.json`.
- SHA-256 Legacy: `c9c48e8852f3952a1c05de528a6cf25124ce264f1f86194400bea2812f460ae0`.
- Shadow selection: `CLEANUP_AUDIT/D05_SHADOW_RESOLVED_SELECTION.json`.
- SHA-256 Shadow: `28212c24f88f07538d4cd5c50d1ce9f0ff603d684c477dfd23ec9984ae8db57a`.
- Registry index SHA-256: `a14e1365de384b627d76f6bf5bfed18d2deac41704c90370581590d179d40aa6`.
- Registry fragment SHA-256: `022c88a293b9cdb9e661fca0b5d0dbd3ccb814cf57fb44acdcb51aff83d4a921`.
- Dataset Lock SHA-256: `5d9f6d0ba4fa1895f70a139510b0d441d62e187eb63ad99de030820946c29f39`.

O capture legado permaneceu imutável. Registry, Lock e Shadow foram usados somente depois do selo para mapear e comparar, nunca para completar o capture.

## 2. Mapeamento Registry

Foram resolvidos por locator literal `(D05_MANAGED_ROOT, relative_path)` todos os 318 itens diretamente observados. Cada locator teve exatamente uma ocorrência Registry. O container da fila e as quatro dependências também foram resolvidos por locator explícito.

- `REGISTRY_RESOLVED` em itens diretos: 318/318.
- `LEGACY_UNREGISTERED`: 0.
- `LEGACY_AMBIGUOUS`: 0.

Somente após a resolução por locator foram comparados SHA-256 e tamanho. Hash não foi usado como identidade.

## 3. Sets comparados

Os 11 conjuntos conceituais foram preservados:

- diretamente observados: `triage_batch_paths`, `base_catalog_work_ids`, `enrichment_overlay_paths_build_order`;
- derivado materializado: `enrichment_queue_work_ids`;
- cardinality-only: `triage_candidate_numbers`, `catalog_69_ids`, `post_codex_revision_members`;
- históricos/não runtime: `enrichment_checkpoints`, `enrichment_capture_paths_lexical`, `outer_manifest_member_paths`;
- output/não input: `enriched_payload_paths`.

## 4. Membership

- `DIRECT_MEMBER_MATCH`: 318/318.
- `DERIVED_MEMBER_MATCH`: 111/111.
- Total member-level comparável: 429/429.
- Member mismatches: 0.
- Legacy extras: 0.
- Shadow extras no escopo comparável: 0.

Os 272 valores ausentes do capture foram excluídos do denominador member-level.

## 5. Cardinality-only: 272

| set_id | Legacy | Shadow | resultado | identidade member-level |
|---|---:|---:|---|---|
| `triage_candidate_numbers` | 200 | 200 | `CARDINALITY_MATCH` | `NOT_OBSERVABLE` |
| `catalog_69_ids` | 69 | 69 | `CARDINALITY_MATCH` | `NOT_OBSERVABLE` |
| `post_codex_revision_members` | 3 | 3 | `CARDINALITY_MATCH` | `NOT_OBSERVABLE` |

Registry, Lock e Shadow não foram usados para retropreencher esses IDs. R2B2 comprova cardinalidade e semântica, não identidade individual, nesses três conjuntos.

## 6. Reconciliação 707

`701 selection members/cardinalities + 6 P2 outputs not selection = 707 relevant to P1/P2`.

Os seis `enriched_payload_paths` continuam outputs e não foram promovidos a inputs.

## 7. Ordem

As três ordens diretamente observadas coincidiram: lotes, dossiês-base e overlays. A fila teve membership comparado, mas sua ordem é `ORDER_NOT_OBSERVABLE`, pois o consumidor usa dict/membership. Os conjuntos cardinality-only sem valores não receberam ordem inventada. Revisões são unordered; conjuntos históricos são não observáveis; outputs são não aplicáveis.

Resultado agregado: `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS`.

## 8. Multiplicidade

Não houve deduplicação por path, ID, hash ou identidade lógica. A multiplicidade dos três conjuntos diretos coincidiu. A fila coincidiu em `POST_INDEX_MULTIPLICITY = 111`; seu estado pré-indexação permanece não observável. Revisões coincidiram em cardinalidade pós-indexação 3, com pré-indexação não observável.

Resultado agregado: `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS`.

## 9. Dependências

- `base_catalog`: `MATCH`, produzido por P1 e diretamente lido por P2.
- `enrichment_checkpoint_state`: `MATCH`, leitura direta e indexação por `work_id`.
- `enrichment_revision_layer`: `MATCH`, leitura direta e indexação por `evidence_id`.
- `catalog_69`: `CONSISTENT_DIFFERENT_CONSUMPTION_MODE`; o legado lê o wrapper embedded e não abre diretamente a ocorrência externa usada como dependência Shadow.

Resultado agregado: `PASS_WITH_DIFFERENT_CONSUMPTION_MODE`.

## 10. Ausências

- 88 `NO_ENRICHMENT_OVERLAY_BY_DESIGN`: member-level match.
- 1 candidata excluída: cardinalidade match, identidade não observável.
- 47 obras sem card adicional: cardinalidade match, identidades não observáveis.
- 15 ausências remotas: 9 receipts incompletos + 6 fetches falhos, `NOT_RUNTIME_OBSERVABLE`.

As 136 ausências comparáveis são consistentes; as 15 remotas não foram classificadas como missing.

## 11. Auxiliary reads

Os 11 eventos auxiliares permaneceram fora da seleção Legacy. Paths que também aparecem no Shadow somente em papel histórico, output ou dependência foram mantidos nessa classificação contextual; não houve promoção automática por igualdade de path.

- Classification mismatches: 0.

## 12. Outputs

Os nove outputs A5B permaneceram fora da membership. Cross-check: `OUTPUT_BYTE_PARITY = 9/9 BYTE_IDENTICAL`.

## 13. Extras e mismatches

- Legacy extras: 0.
- Shadow extras comparáveis: 0.
- Member mismatches: 0.
- Blocking mismatches: 0.

Conjuntos históricos, identidades cardinality-only, ausências remotas e outputs não foram falsamente classificados como extras.

## 14. Byte identity

- Membros diretos: 318/318 `BYTE_MATCH` após resolução Registry.
- Fila derivada: 111 `BYTE_NOT_REVALIDATED` no nível do membro; a identidade do checkpoint foi resolvida, mas o capture não embute hash legado por membro da fila.
- Outputs: 9/9 byte-idênticos como cross-check, fora da seleção.

Resultado agregado: `PASS_WITH_NOT_REVALIDATED_DIMENSIONS`.

## 15. Dimensões não observáveis

- 272 identidades member-level em três conjuntos cardinality-only;
- ordem da fila e ordens sem valores legados materializados;
- multiplicidade pré-indexação da fila e das revisões;
- membership runtime dos três conjuntos históricos;
- 15 ausências remotas;
- byte identity member-level dos 111 membros derivados da fila.

Esses limites impedem `PASS` absoluto e não constituem mismatch.

## 16. Métricas agregadas

| métrica | resultado |
|---|---|
| `LEGACY_SHADOW_MEMBER_PARITY` | `PASS` |
| `LEGACY_SHADOW_CARDINALITY_PARITY` | `PASS` |
| `LEGACY_SHADOW_ORDER_PARITY` | `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS` |
| `LEGACY_SHADOW_MULTIPLICITY_PARITY` | `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS` |
| `LEGACY_SHADOW_DEPENDENCY_PARITY` | `PASS_WITH_DIFFERENT_CONSUMPTION_MODE` |
| `LEGACY_SHADOW_ABSENCE_PARITY` | `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS` |
| `LEGACY_SHADOW_BYTE_PARITY` | `PASS_WITH_NOT_REVALIDATED_DIMENSIONS` |
| `LEGACY_EXTRAS_COUNT` | `0` |
| `SHADOW_EXTRAS_COMPARABLE_COUNT` | `0` |
| `BLOCKING_MISMATCHES` | `0` |

## 17. Status final

`LEGACY_SHADOW_STATUS = PASS_WITH_NOT_OBSERVABLE_DIMENSIONS`.

O resultado não é `PASS` absoluto porque há dimensões explicitamente não observáveis. Não há mismatch bloqueante. O pipeline legado permanece autoritativo e a seleção Shadow permanece derivada, não autoritativa e desconectada do consumidor.

## 18. Limites da prova e próximo passo

A prova não autoriza retropreencher os 272 IDs, reexecutar fases históricas, inferir ordem não consumida ou usar Golden como autoridade. Golden e Triple Parity podem permanecer cross-checks independentes, sem alterar o resultado desta comparação.

Próximo passo recomendado: revisão humana dos limites e do status `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS` antes de autorizar qualquer desenho de consumer adapter. Nenhuma próxima fase foi iniciada nesta missão.

## Resultado

`MIGRACAO_R2B2_CONCLUIDA — LEGACY_SHADOW_PARIDADE_VALIDADA`
