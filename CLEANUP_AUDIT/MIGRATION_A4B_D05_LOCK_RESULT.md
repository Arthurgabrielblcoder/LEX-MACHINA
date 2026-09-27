# Migração A4B — resultado do Dataset Lock sombra D05

## 1. Resultado

O Dataset Lock sombra `d05-historical-parity-v1.lock` foi materializado e validado. O verifier respondeu `PASS` e demonstrou paridade total com a Golden Reference nas dimensões historicamente comprovadas.

O lock permanece em modo `SHADOW`. Nenhum consumidor ou script D05 o importa ou lê, e nenhum pipeline foi executado.

## 2. Identidade e vínculos

| campo | valor |
|---|---|
| `lock_id` | `d05-historical-parity-v1.lock` |
| `profile_id` | `d05-historical-parity-v1` |
| `lock_version` | `1` |
| modo | `SHADOW` |
| SHA-256 do lock | `5d9f6d0ba4fa1895f70a139510b0d441d62e187eb63ad99de030820946c29f39` |
| SHA-256 do Registry index | `a14e1365de384b627d76f6bf5bfed18d2deac41704c90370581590d179d40aa6` |
| SHA-256 do fragmento D05 | `022c88a293b9cdb9e661fca0b5d0dbd3ccb814cf57fb44acdcb51aff83d4a921` |
| SHA-256 da Golden Reference | `f82e82d9c3907186e916a54436493ebe8f426d1a09f7b3a3aa3b092c2e09cdc7` |

Os arquivos JSON usam UTF-8 sem BOM, LF, chaves ordenadas, indentação de dois espaços e LF final. Não há timestamp ou outro valor volátil no lock.

## 3. Conjuntos e cardinalidades

| conjunto | itens | ordem | classe de consumo |
|---|---:|---|---|
| `triage_batch_paths` | 8 | comprovada | `PIPELINE_INPUT` |
| `triage_candidate_numbers` | 200 | comprovada | `HISTORICAL_ORDER_ASSERTION` |
| `base_catalog_work_ids` | 199 | comprovada | `PIPELINE_INPUT` |
| `catalog_69_ids` | 69 | comprovada | `PIPELINE_INPUT` |
| `enrichment_queue_work_ids` | 111 | comprovada | `PIPELINE_INPUT` |
| `enrichment_checkpoints` | 12 | comprovada | `PROVENANCE_INPUT` |
| `enrichment_capture_paths_lexical` | 128 | comprovada | `PROVENANCE_INPUT` |
| `enrichment_overlay_paths_build_order` | 111 | comprovada | `PIPELINE_INPUT` |
| `enriched_payload_paths` | 6 | comprovada | `OUTPUT_REFERENCE` |
| `outer_manifest_member_paths` | 852 | comprovada | `AUDIT_CLOSURE` |
| `post_codex_revision_members` | 3 | não afirmada | `PIPELINE_INPUT` |

Total: **11 conjuntos e 1.699 itens semânticos**. Os dez conjuntos ordenados possuem ordinais explícitos, únicos e contíguos de 1 até `N`. O conjunto de revisões declara `ordered: false` e não contém ordinais.

## 4. Identidade e multiplicidade

Cada item contém somente a identidade estável necessária: `logical_id`, `version`, `occurrence_id`, `member_ref` quando aplicável e `ordinal` quando ordenado. Paths, hashes, tamanhos e proveniência continuam sob autoridade do Artifact Registry.

O verifier resolve cada ocorrência de modo unívoco, confere seus bytes contra o Registry e valida membros internos diretamente nos artefatos selecionados. A mesma ocorrência pode integrar conjuntos de funções diferentes; dentro de cada conjunto, o par ocorrência/membro é único. Nenhuma ocorrência foi deduplicada por hash.

Resultado: `MEMBER_MATCH=true`, `ORDER_MATCH=true`, `MULTIPLICITY_MATCH=true`.

## 5. Ausências explícitas

Foram materializados 151 registros individuais de ausência, sem criar arquivos artificiais:

| ausência | categoria | quantidade |
|---|---|---:|
| `NO_ENRICHMENT_OVERLAY_BY_DESIGN` | operacional do lock | 88 |
| `CANDIDATE_EXCLUDED_FROM_USABLE_CATALOG` | operacional do lock | 1 |
| `NO_ADDITIONAL_CARD_AFTER_EXAMINATION` | evidência histórica | 47 |
| `WEB_SOURCE_WITHOUT_COMPLETE_LOCAL_RECEIPT` | evidência histórica | 9 |
| `REMOTE_FETCH_FAILED_WITH_METADATA_PRESERVED` | evidência histórica | 6 |

As cronologias remota e de deliberação humana, não comprovadas, permanecem fora do lock. Resultado: `ABSENCE_MATCH=true`.

## 6. Dependências

Quatro dependências são obrigatórias e resolvidas pela identidade do Registry:

- catálogo 69 externo;
- catálogo-base;
- estado do checkpoint de enriquecimento;
- camada de revisões pós-Codex.

Nenhum path absoluto foi gravado no lock. Resultado: `DEPENDENCY_MATCH=true`.

## 7. Política `restricted_local`

As ocorrências abaixo continuam deliberadamente fora do Git:

- `D05_MANAGED_ROOT:03_FONTES/BUSCA_118.json`;
- `D05_MANAGED_ROOT:06_RELATORIOS/CONSULTA_CP11.txt`;
- `D05_MANAGED_ROOT:06_RELATORIOS/CONSULTA_CP12.txt`.

O verifier exige sua presença e seus bytes exatos. A simulação não destrutiva da ausência de `BUSCA_118.json` falhou como esperado. Não existe fallback, substituição, tolerância silenciosa ou inclusão automática no Git.

## 8. Paridade automática

| dimensão | resultado |
|---|---|
| `MEMBER_MATCH` | `true` |
| `ORDER_MATCH` | `true` |
| `MULTIPLICITY_MATCH` | `true` |
| `ABSENCE_MATCH` | `true` |
| `DEPENDENCY_MATCH` | `true` |
| `EXTRA_ITEMS` | `0` |

O Registry contém 855 ocorrências, e o verifier do próprio Registry também respondeu `PASS`, sem erros, órfãos ou conflitos.

## 9. Testes negativos

Os dez testes foram executados em cópias JSON canônicas temporárias, exceto a ausência `restricted_local`, simulada por opção somente leitura. Todos retornaram falha:

1. `occurrence_id` inexistente;
2. hash do Registry incorreto;
3. hash da Golden Reference incorreto;
4. ordinal duplicado;
5. ordinal fora da sequência;
6. item extra;
7. multiplicidade reduzida;
8. dependência removida;
9. `restricted_local` ausente;
10. wildcard introduzido.

Resultado: **10/10 fail-closed**. Os resultados estruturados estão em `CLEANUP_AUDIT/MIGRATION_A4B_D05_LOCK_TEST.json`.

## 10. Limitações

- O lock prova a seleção histórica; ele não reproduz nem valida outputs novos do pipeline.
- O perfil depende de três arquivos `restricted_local`, portanto um checkout apenas com Git falha explicitamente.
- A Golden Reference continua como autoridade transitória de paridade durante a migração sombra.
- Qualquer alteração de bytes no índice, fragmento, Golden Reference ou ocorrência selecionada invalida a verificação.
- A ordem das três revisões e as duas cronologias não comprovadas não são inferidas.

## 11. Integridade e isolamento

A verificação direcionada confirmou: Registry `PASS`; Golden Reference intacta; D05 funcional intacto; `ENRIQUECIDO_V1` 7/7; V2 281/281; `protected545` 545/545; IDX 130/130; política de bytes intacta.

Não há alterações rastreadas nem staging. Buscas direcionadas confirmam que nenhum consumidor D05 ganhou import ou referência a `DATASET_LOCKS`; nenhum glob/rglob funcional foi alterado e nenhum output foi produzido.

## 12. Condição para A5

A5 somente poderá começar após revisão conjunta dos artefatos A4A e A4B e autorização específica. A conclusão desta etapa não torna o lock autoritativo e não autoriza integração com consumidores.
