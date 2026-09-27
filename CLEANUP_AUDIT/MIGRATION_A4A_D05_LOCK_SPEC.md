# Migração A4A — especificação do Dataset Lock sombra D05

## 1. Escopo e estado

Este documento especifica, sem implementar, o Dataset Lock sombra do dataset `d05.catalogo-expansao-200`. O perfil proposto é `d05-historical-parity-v1`, com `lock_id` `d05-historical-parity-v1.lock`, `lock_version` `1` e modo `SHADOW`.

A A4A não cria um lock funcional, não altera consumidores, não executa o pipeline e não substitui o comportamento legado. O objetivo é fixar o contrato que a A4B deverá materializar e verificar contra a Golden Reference validada na A3.

## 2. Responsabilidades do perfil

O perfil representa a seleção histórica explicitamente comprovada para o D05. Ele deve:

- selecionar ocorrências e membros por referências estáveis;
- preservar ordem e multiplicidade quando comprovadas historicamente;
- declarar ausências operacionais sem inventar artefatos;
- vincular-se criptograficamente ao Artifact Registry e à Golden Reference;
- separar entradas de pipeline, entradas de proveniência, afirmações de ordem, referências de saída e fechamento de auditoria;
- falhar de forma fechada diante de ausência, ambiguidade, divergência ou descoberta implícita.

O perfil é imutável. Termos móveis como `latest`, `current` ou seleção automática não pertencem ao seu contrato.

## 3. Conjuntos de seleção

Os dez primeiros conjuntos reproduzem sequências ordenadas da Golden Reference. O décimo primeiro registra membros de revisão cuja ordem histórica não foi provada.

| conjunto | função semântica | classe de consumo | itens | referência | ordem | relação principal |
|---|---|---:|---:|---|---|---|
| `triage_batch_paths` | lotes de triagem | `PIPELINE_INPUT` | 8 | ocorrência | ordenada | produz o catálogo-base |
| `triage_candidate_numbers` | ordem dos candidatos | `HISTORICAL_ORDER_ASSERTION` | 200 | membro interno | ordenada | comprova a sequência 1–200 |
| `base_catalog_work_ids` | dossiês utilizáveis | `PIPELINE_INPUT` | 199 | ocorrência + membro | ordenada | exclui explicitamente o candidato 92 |
| `catalog_69_ids` | membros do catálogo externo | `PIPELINE_INPUT` | 69 | membro interno | ordenada | dependência editorial externa |
| `enrichment_queue_work_ids` | fila de enriquecimento | `PIPELINE_INPUT` | 111 | membro interno | ordenada | determina a seleção de overlays |
| `enrichment_checkpoints` | sequência de checkpoints | `PROVENANCE_INPUT` | 12 | ocorrência + membro | ordenada | comprova o estado intermediário |
| `enrichment_capture_paths_lexical` | capturas-fonte | `PROVENANCE_INPUT` | 128 | ocorrência | ordenada | preserva a ordem lexical comprovada |
| `enrichment_overlay_paths_build_order` | overlays | `PIPELINE_INPUT` | 111 | ocorrência | ordenada | preserva a ordem de composição |
| `enriched_payload_paths` | payload enriquecido | `OUTPUT_REFERENCE` | 6 | ocorrência | ordenada | referência de saída, não entrada |
| `outer_manifest_member_paths` | membros do snapshot final | `AUDIT_CLOSURE` | 852 | ocorrência | ordenada | fechamento histórico |
| `post_codex_revision_members` | patches pós-Codex | `PIPELINE_INPUT` | 3 | membro interno | não ordenada | incorpora a camada de revisão |

Os conjuntos somam 1.699 itens semânticos. Esse total inclui sobreposição intencional: uma ocorrência pode participar de conjuntos diferentes porque cada conjunto expressa uma função distinta. Isso não representa 1.699 artefatos únicos e não autoriza deduplicação de conteúdo.

## 4. Ordem

Cada conjunto ordenado deve materializar um campo `ordinal` inteiro, de base 1, único e contíguo até a cardinalidade esperada. A ordem vem exclusivamente da sequência correspondente na Golden Reference e é identificada por `ordering_rule_id` no formato `golden:<set_id>`.

O conjunto `post_codex_revision_members` é explicitamente não ordenado. Seus três `evidence_id` são selecionados, mas a A4B não pode inferir ordem pela posição física no arquivo, nome, timestamp ou enumeração do sistema de arquivos.

Os digests das sequências esperadas usam SHA-256 sobre o array de itens em JSON canônico UTF-8 (chaves ordenadas, indentação de dois espaços e LF final). Para o conjunto não ordenado de revisões, os `evidence_id` são ordenados lexicalmente apenas para calcular o digest, sem criar semântica ordinal.

| conjunto | SHA-256 da sequência Golden |
|---|---|
| `triage_batch_paths` | `91d4ae07891d4981a878f5476b2420c0a5c18d4cdc8c70543e6cadd8281732a0` |
| `triage_candidate_numbers` | `7b9e82b1e31b77b9e228ae1c1bdbc2380e179516a58b62ffcafaab2f85989a65` |
| `base_catalog_work_ids` | `38a3ffa2129de38505972ce211090c8f9201428f67644503822aab3f3a088ca8` |
| `catalog_69_ids` | `d2e55a60cd1297d85d966ed7ad476c36ffaf7862180afff609c3f47e52c9c8dd` |
| `enrichment_queue_work_ids` | `77bd5e43312655583a6b8e3a9643a7db58fbb9e1f1c1caba140bbdd16c4dbc02` |
| `enrichment_checkpoints` | `2ec2e5096c1367c155e37c0d1fb35a8763d44a9e66a8bfe5c4065a0bba1bec73` |
| `enrichment_capture_paths_lexical` | `afac00402ee36c5e046ae8e20e324a1afd0a6b2cf5586eacf9510a35cd5b3390` |
| `enrichment_overlay_paths_build_order` | `64361e9f00c98d6764b6c69277deaf7fd9035c6e8e38ad9c050d40c1cfdbd84a` |
| `enriched_payload_paths` | `7333603852b681c0e91ba474ac668142944e3dee4930bb9be3e631084a6fb222` |
| `outer_manifest_member_paths` | `8c1fea8d38cf4c70613b944650c5c184f05b3337ce9bde8bfa9473e108b0ab6b` |
| `post_codex_revision_members` | `3a2f84ba7db92425142b50432082e5222306293e608b54db622b95d8acba05c0` |

## 5. Identidade e multiplicidade

Uma ocorrência direta é referenciada por `(logical_id, version, occurrence_id)`. Um membro interno acrescenta `member_ref`, que pode representar `candidate_number`, `work_id`, `catalog_69_id` ou `evidence_id` conforme o conjunto.

Dentro de um conjunto de ocorrências, `occurrence_id` não pode repetir. Dentro de um conjunto de membros, a mesma ocorrência pode repetir somente quando cada par `(occurrence_id, member_ref)` for único. A mesma ocorrência pode aparecer em conjuntos distintos, pois a identidade do conjunto integra o significado da seleção.

Paths e hashes dos artefatos não são copiados para cada item do lock. Eles continuam sob autoridade do Registry e são resolvidos pelas referências estáveis. A A4B deve rejeitar resolução zero, múltipla ou divergente.

## 6. Ausências e exclusões

O lock deve distinguir três categorias:

### 6.1 Ausências operacionais do lock

- 88 trabalhos não possuem overlay por desenho histórico; cada `work_id` deve ser declarado explicitamente.
- o candidato 92, `EXP2-SER-002`, foi excluído do catálogo utilizável; a exclusão deve ser explícita.

Esses fatos afetam a seleção e a multiplicidade. Nenhum placeholder ou artefato vazio deve ser criado.

### 6.2 Evidência histórica apenas

- 47 exames não produziram cartão adicional; isso é um resultado registrado nos bytes selecionados, não uma ausência de arquivo.
- 9 fontes web não possuem recibo local completo; a lacuna deve permanecer declarada, sem recibo fictício.
- 6 buscas remotas falharam com metadados preservados; o lock seleciona as ocorrências de metadados existentes, sem inventar corpo remoto.

### 6.3 Fora do lock

As cronologias de recuperação remota e de deliberação humana não foram historicamente comprovadas. Elas permanecem fora da semântica de seleção. A A4B não pode reconstruí-las por timestamps, nomes ou heurística.

## 7. Filtros editoriais

Os predicados editoriais `APTA` e `APTA_COM_RESSALVA` continuam pertencendo à documentação histórica e de geração. O lock não deve reexecutar nem reinterpretar esses filtros.

O lock possui somente o resultado já comprovado: 199 trabalhos selecionados, 111 overlays, suas ordens, suas multiplicidades e as exclusões explícitas. Assim, a validação da A4B compara o resultado materializado com a Golden Reference, sem recomputar a decisão editorial.

## 8. Dependências obrigatórias

O perfil deve declarar e resolver exatamente estas dependências:

| dependência | ocorrência requerida |
|---|---|
| catálogo 69 | `CATALOG_69_ROOT:CATALOGO_69_CANONICO.json` |
| catálogo-base | `D05_MANAGED_ROOT:07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json` |
| estado de checkpoint | `D05_MANAGED_ROOT:06_RELATORIOS/CHECKPOINT_ENRIQUECIMENTO.json` |
| camada de revisões | `D05_MANAGED_ROOT:06_RELATORIOS/REVISOES_ENRIQUECIMENTO_V1.json` |

Lotes, dossiês, capturas, overlays, payloads e membros do manifesto são cobertos pelos conjuntos explícitos. A ausência de qualquer dependência obrigatória deve encerrar a verificação com erro.

## 9. Artefatos `restricted_local`

Três ocorrências permanecem deliberadamente fora do Git e preservam a política existente:

- `D05_MANAGED_ROOT:03_FONTES/BUSCA_118.json`;
- `D05_MANAGED_ROOT:06_RELATORIOS/CONSULTA_CP11.txt`;
- `D05_MANAGED_ROOT:06_RELATORIOS/CONSULTA_CP12.txt`.

Quando selecionadas pelo perfil, sua ausência deve causar `FAIL_CLOSED`. Não há fallback, cópia automática, promoção para o Git ou substituição por conteúdo semelhante. Portanto, um checkout somente com arquivos Git não satisfaz o perfil histórico.

## 10. Forma proposta do schema

O futuro lock JSON deve conter no topo:

- `schema_version`;
- `lock_version`;
- `lock_id`;
- `dataset_id`;
- `profile_id`;
- `mode`;
- `registry_index_sha256`;
- `registry_fragments`;
- `golden_reference`;
- `selection_sets`;
- `explicit_absences`;
- `dependencies`;
- `constraints`.

Cada conjunto deve conter `set_id`, `semantic_role`, `consumption_class`, `ordered`, `ordering_rule_id` e `items`. Cada item deve conter `logical_id`, `version` e `occurrence_id`; `ordinal` e `member_ref` são condicionais ao tipo do conjunto.

A serialização canônica proposta segue a política do Registry: UTF-8 sem BOM, LF, chaves ordenadas, indentação de dois espaços e LF final. O schema deve vedar propriedades desconhecidas onde isso não impedir evolução versionada explícita.

## 11. Vínculos de autoridade

O lock A4B deverá vincular-se exatamente a:

- Registry `lex-machina-artifact-registry`, schema 1;
- `ARTIFACT_REGISTRY/index.json`, SHA-256 `a14e1365de384b627d76f6bf5bfed18d2deac41704c90370581590d179d40aa6`;
- fragmento D05, SHA-256 `022c88a293b9cdb9e661fca0b5d0dbd3ccb814cf57fb44acdcb51aff83d4a921`;
- Golden Reference `d05-golden-reference/1` em `CLEANUP_AUDIT/D05_GOLDEN_REFERENCE.json`, SHA-256 `f82e82d9c3907186e916a54436493ebe8f426d1a09f7b3a3aa3b092c2e09cdc7`.

O Registry é a autoridade para identidade, localização, hash, papel e política das ocorrências. A Golden Reference é a autoridade transitória para a paridade histórica de conjunto, ordem, multiplicidade e ausência durante a migração sombra.

## 12. Invariantes e falha fechada

A implementação A4B deverá provar todos os invariantes abaixo:

1. JSON válido contra o schema e serialização canônica.
2. Hashes do índice e do fragmento do Registry idênticos aos vínculos.
3. Versão e hash da Golden Reference idênticos ao vínculo.
4. Cada item de artefato resolve exatamente uma ocorrência do Registry.
5. Cada `member_ref` existe no artefato referido e é único com sua ocorrência no conjunto.
6. `occurrence_id` é único em cada conjunto de ocorrências.
7. Ordinais dos conjuntos ordenados são únicos e formam `1..N`.
8. Conjuntos não ordenados não afirmam semântica ordinal.
9. Multiplicidade e ausências semânticas coincidem com a Golden Reference.
10. Não existe wildcard, glob, regex, `latest`, varredura de pasta ou fallback implícito.
11. A ausência de ocorrência `restricted_local` selecionada falha explicitamente.
12. Dependências internas e externas obrigatórias estão completas.
13. Não existe item selecionado além dos itens explicitamente declarados.

Qualquer violação deve produzir falha explícita, com identificação do conjunto e do item, sem continuar com seleção parcial.

## 13. Critérios de aceitação da A4B

A A4B só poderá ser considerada válida se produzir um lock funcional e um verificador que demonstrem 100% de correspondência lock ↔ Golden Reference em:

- associação de membros aos 11 conjuntos;
- dez sequências ordenadas comprovadas;
- multiplicidade;
- ausências operacionais;
- dependências obrigatórias;
- inexistência de itens extras no perfil.

O verificador da A4B também deverá validar os vínculos do Registry, o schema, a serialização canônica e a política `restricted_local`, com testes negativos fail-closed. Ele não deve executar nem reproduzir `ENRIQUECIDO_V1`; sua responsabilidade é validar o contrato do lock em leitura.

## 14. Arquivos previstos para A4B

- `DATASET_LOCKS/d05-historical-parity-v1.lock.json`;
- `DATASET_LOCKS/schemas/dataset-lock.schema.json`;
- `DATASET_LOCKS/verify_dataset_lock.py`;
- `CLEANUP_AUDIT/MIGRATION_A4B_D05_LOCK_BASELINE.json`;
- `CLEANUP_AUDIT/MIGRATION_A4B_D05_LOCK_RESULT.md`.

Esses arquivos são apenas previstos. Nenhum deles é criado na A4A.

## 15. Riscos controlados

- O lock será grande: pelo menos 1.699 itens semânticos, incluindo sobreposições intencionais entre conjuntos.
- A resolução de membros internos exige leitura e validação específica por tipo, sem modificar os artefatos.
- Conjuntos sobrepostos podem ser confundidos com consumo duplicado; `consumption_class` e `semantic_role` devem governar o uso.
- Os três itens `restricted_local` impedem portabilidade integral de um checkout somente Git.
- Qualquer alteração de bytes no Registry ou na Golden Reference invalida os vínculos.
- Cronologias desconhecidas não podem ser materializadas.
- Conjuntos `OUTPUT_REFERENCE` e `AUDIT_CLOSURE` não podem ser consumidos como entradas do pipeline.
- A raiz externa do catálogo 69 deve existir e resolver a ocorrência declarada.
- Predicados editoriais não podem ser duplicados ou recalculados pelo lock.
- Esta especificação não pode ser tratada como lock funcional.

## 16. Sequência futura

- A4A: especificar o contrato — esta etapa.
- A4B: materializar e verificar o lock sombra.
- A5: somente após revisão e autorização próprias, planejar a integração de consumidores.
- A6: somente após gates próprios, validar a migração operacional.
- A7: somente após gates próprios, decidir consolidação final.

Nenhuma etapa futura é autorizada por este documento.

## 17. Declaração de não alteração

A A4A produz apenas `CLEANUP_AUDIT/MIGRATION_A4A_D05_LOCK_SPEC.md` e `CLEANUP_AUDIT/MIGRATION_A4A_D05_LOCK_SPEC.json`, ambos documentos de especificação. Nenhum conteúdo funcional do D05, Registry, Golden Reference, pipeline, consumidor, schema funcional ou lock foi alterado.
