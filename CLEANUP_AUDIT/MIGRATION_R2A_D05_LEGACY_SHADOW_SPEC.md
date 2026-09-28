# Migração R2A — especificação da comparação LEGACY_SELECTION × SHADOW_RESOLVED_SELECTION

## 1. Escopo e autoridade

R2A define como observar e comparar a seleção legada do D05 sem executar, instrumentar ou alterar o pipeline. O legado permanece `LEGACY_AUTHORITATIVE`; o resolver permanece `SHADOW_ONLY`; a seleção resolvida permanece `DERIVED / NON_AUTHORITATIVE`.

R2A não cria captura real, não compara legacy × shadow e não autoriza R2B. Golden, Dataset Lock e `D05_SHADOW_RESOLVED_SELECTION.json` não podem dirigir a observação legada.

## 2. Definição de `LEGACY_SELECTION`

`LEGACY_SELECTION` é a sequência ou o conjunto de artefatos e membros que os consumidores legados locais efetivamente escolhem, leem ou aplicam para produzir os resultados D05 cobertos pelo piloto. Inclui a identidade da fase, papel semântico, ordem observada ou derivada e multiplicidade conforme a semântica real do código.

Não inclui automaticamente todo arquivo aberto durante a execução. Scripts, imports, logs, schemas, configuração do runner, arquivos escritos, releituras apenas para hash e arquivos auxiliares sem influência sobre membership, ordem ou conteúdo do dataset são eventos operacionais e precisam ser classificados antes de serem considerados seleção.

Outputs não são seleção de inputs. Podem ser comparados como evidência derivada em dimensão própria.

## 3. Consumidores locais relevantes

O núcleo executável determinístico é formado por:

- P1: `07_CATALOGO_CANDIDATO/compilar_catalogo.py`, função `main`, linhas 31–85;
- P2: `07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py`, função `main`, linhas 30–139.

Fases históricas consultadas apenas para explicar proveniência:

- `06_RELATORIOS/enriquecer_v1.py`, funções `queue`, `baseline` e `checkpoint`, linhas 14–68;
- `06_RELATORIOS/consultar_fontes_enriquecimento.py`, função `run`, linhas 36–46;
- `06_RELATORIOS/relatorios_enriquecimento_v1.py`, corpo principal, linhas 24–29 e 45–68;
- `08_MANIFEST/gerar_manifest.py`, corpo principal, linhas 35–89.

As fases históricas stateful, remotas e de fechamento não devem ser reexecutadas em R2B.

## 4. Classificação dos 11 conjuntos

| set_id | classe R2A | fase | ponto de seleção | mecanismo | ordem | multiplicidade | cobertura A5B |
|---|---|---|---|---|---|---|---|
| `triage_batch_paths` | `DIRECTLY_OBSERVABLE_IN_LEGACY` | P1 | `compilar_catalogo.py:31-35` | `EXPLICIT_LIST` + `DIRECT_PATH`; `range(1, 9)` | `DETERMINISTIC_EXPLICIT`, `LOTE_01..08` | oito leituras, uma por nome | `ALREADY_OBSERVED_IN_A5B` |
| `triage_candidate_numbers` | `DERIVABLE_FROM_LEGACY_INPUTS` | P1/histórica | `compilar_catalogo.py:32-38` | concatenação dos arrays dos oito lotes; depois processamento por `sorted(..., work_id)` | ordem histórica dos arrays é `DETERMINISTIC_EXPLICIT`; ordem operacional de dossiês é outra dimensão, por `work_id` | `triage +=` preserva membros; assert exige 200 números únicos | `NOT_OBSERVABLE` no nível de evento interno; derivável dos lotes selados sem nova execução |
| `base_catalog_work_ids` | `DIRECTLY_OBSERVABLE_IN_LEGACY` | P1 | `compilar_catalogo.py:37-55` | `FILTERED_DATASET` por `APTA/APTA_COM_RESSALVA`, seguido de `DIRECT_PATH` | `DETERMINISTIC_DERIVED` por `work_id` | uma abertura por entrada utilizável; não há deduplicação por hash | `ALREADY_OBSERVED_IN_A5B` |
| `catalog_69_ids` | `DERIVABLE_FROM_LEGACY_INPUTS` | P1/P2 | P1 `:65-80`; P2 `:94-102` | wrapper congelado + `LOOKUP_BY_ID`/lista embutida | `DETERMINISTIC_DERIVED` por `id` | list comprehension preserva cada membro; sem deduplicação | `ALREADY_OBSERVED_IN_A5B`, por wrapper e outputs; ocorrência externa não foi aberta |
| `enrichment_queue_work_ids` | `DERIVABLE_FROM_LEGACY_INPUTS` | P2 | `compilar_enriquecido_v1.py:34-46,65,78` | `CHECKPOINT_STATE`, convertido para dict por `work_id` | array persistido tem ordem explícita, mas P2 usa membership e itera obras por `work_id`; ordem da fila não é operacionalmente observável | dict sobrescreve IDs duplicados; R2B deve checar unicidade antes de afirmar 1:1 | membership `ALREADY_OBSERVED_IN_A5B`; ordem `NOT_OBSERVABLE/NOT_CONSUMED` |
| `enrichment_checkpoints` | `HISTORICAL_ONLY_NOT_RUNTIME_SELECTED` | história | criação em `enriquecer_v1.py:43-68`; reconstrução em `relatorios_enriquecimento_v1.py:24-26` | `DIRECT_PATH` na criação; `GLOB` + `SORTED_DISCOVERY` por `numero` na reconstrução | `DETERMINISTIC_DERIVED` por número no estado congelado | um arquivo por número; reexecução poderia sobrescrever estado | `NOT_OBSERVABLE` em P1/P2 |
| `enrichment_capture_paths_lexical` | `HISTORICAL_ONLY_NOT_RUNTIME_SELECTED` | coleta remota | `consultar_fontes_enriquecimento.py:36-46`; leitura histórica em `relatorios_enriquecimento_v1.py:27-28` | jobs remotos e path candidato+hash; relatório usa `SORTED_DISCOVERY` | lock registra ordem lexical; produção depende dos jobs e `pool.map`; fase remota excluída | mesmo candidato+URL gera mesmo path e pode sobrescrever; arquivo final não prova tentativas repetidas | `NOT_OBSERVABLE` em P1/P2 |
| `enrichment_overlay_paths_build_order` | `DIRECTLY_OBSERVABLE_IN_LEGACY` | P2 | `compilar_enriquecido_v1.py:39-69` | `FILTERED_DATASET` + `DIRECT_PATH`; `exists()` e leitura por `work_id` | `DETERMINISTIC_DERIVED` por obras-base ordenadas por `work_id` | no máximo um path por obra; 111 leituras; zero deduplicação por hash | `ALREADY_OBSERVED_IN_A5B` |
| `enriched_payload_paths` | `NOT_APPLICABLE_TO_EXECUTED_CONSUMER` | output P2 | `compilar_enriquecido_v1.py:107-138` | produção explícita; manifesto interno usa `SORTED_DISCOVERY` de outputs | `DETERMINISTIC_DERIVED` por nome | filenames únicos; representam seis outputs, não inputs | `ALREADY_OBSERVED_IN_A5B` como output byte-idêntico, fora de `LEGACY_SELECTION` primária |
| `outer_manifest_member_paths` | `HISTORICAL_ONLY_NOT_RUNTIME_SELECTED` | fechamento | `gerar_manifest.py:80-89` | `RGLOB` + `SORTED_DISCOVERY` sobre a árvore histórica | determinística na árvore congelada e plataforma Windows; sensível ao conjunto de arquivos existente | cada path final uma vez; arquivos novos alterariam o universo | `NOT_OBSERVABLE` em P1/P2; não reexecutar gerador |
| `post_codex_revision_members` | `DERIVABLE_FROM_LEGACY_INPUTS` | P2 | `compilar_enriquecido_v1.py:34,52-58,77,105-116` | `DIRECT_PATH` + `LOOKUP_BY_ID` | Lock é unordered; aplicação segue obra/card, output registra `sorted(applied)` | dict por `evidence_id` sobrescreve duplicatas; assert final exige o conjunto aplicado | `ALREADY_OBSERVED_IN_A5B` |

Resumo: 3 diretamente observáveis, 4 deriváveis, 3 históricas fora do runtime P1/P2, 1 output não aplicável à seleção de inputs e 0 ambíguas.

## 5. Ordem legada

R2B deve comparar ordem somente quando a ordem tem significado no consumidor:

- lotes: nomes explícitos `01..08`;
- dossiês: `sorted(triage, key=work_id)` após filtro;
- catálogo 69: `sorted(ref['obras'], key=id)`;
- overlays: ordem das obras-base por `work_id`;
- payloads: ordem lexical dos nomes no manifesto interno, como evidência de output;
- revisões: conjunto sem ordem contratual.

A ordem dos 200 candidatos é uma afirmação histórica derivada dos arrays dos lotes. P1 cria essa sequência, mas muda para `work_id` antes de selecionar dossiês. A ordem dos 111 itens da fila é persistida no checkpoint, porém P2 a converte em dict e usa somente membership. Esses dois casos não podem receber `ORDER_MATCH` runtime sem explicitar a diferença entre ordem armazenada e ordem consumida.

## 6. Multiplicidade e sobrescrita

R2B deve manter eventos repetidos e não deduplicar por SHA-256, path ou `logical_id`.

Há quatro semânticas diferentes:

1. concatenação preservadora: lotes e seus membros;
2. uma leitura por entrada filtrada: dossiês e overlays;
3. indexação potencialmente sobrescritora: fila por `work_id` e revisões por `evidence_id`;
4. materialização por filename: capturas, payloads e manifesto.

Para fila e revisões, a captura deve registrar a cardinalidade do array antes do dict, a quantidade de chaves depois do dict e IDs duplicados. Para capturas, deve distinguir jobs tentados de arquivos finais. A equivalência 1:1 só é válida quando essas contagens coincidem.

## 7. Evidência A5B já disponível

`D05_REPLAY_RUN.json` já contém, em ordem:

- P1: oito lotes, 199 dossiês e o wrapper do catálogo 69;
- P2: catálogo-base, checkpoint, camada de revisões e 111 overlays;
- manifests byte-idênticos dos três grupos de inputs;
- nove outputs byte-idênticos;
- bloqueio de rede e de escrita externa;
- cardinalidades 199/221/71/292/111/3.

A6 já concluiu 507 itens diretamente correspondentes, 707 itens relevantes às fases executadas, 992 fora das fases e 200 membros sem observação event-level. Também confirmou 136 das 151 ausências; as 15 restantes pertencem à coleta remota excluída.

R2B deve primeiro converter essa evidência existente em captura normalizada. Nova execução é **parcial/condicional** apenas se a revisão exigir repetir eventos de arquivo P1/P2. Ela não torna observável a iteração interna de membros. Se for exigida prova event-level interna ou edição do legado, R2B deve bloquear antes da mudança.

## 8. Estratégia de captura R2B

Fases obrigatórias, nesta ordem:

1. **construir a captura somente da evidência A5B selada:** transformar `observed_reads` da A5B e os bytes congelados que ela autenticou em `D05_LEGACY_SELECTION_CAPTURE.json`, complementando apenas com derivações fechadas das regras visíveis no código legado e registradas como `DERIVED_FROM_OBSERVED_INPUT`;
2. **selar o capture core:** calcular e registrar seu SHA-256 antes de carregar qualquer contrato sombra;
3. **carregar Registry, Lock e Shadow somente após o selo:** mapear identidades e executar a comparação sem alterar ou filtrar o conjunto capturado;
4. **avaliar gaps:** classificar diferenças, limites de observabilidade e evidência insuficiente;
5. **executar novamente somente se necessário e justificado:** repetir apenas P1/P2 no sandbox A5B quando a revisão exigir eventos de arquivo que a evidência selada não comprova. Se a prova exigir instrumentação interna ou edição do legado, bloquear R2B.

Dentro da primeira fase, a ordem de preferência é:

1. **extração evidence-only:** transformar `observed_reads` da A5B e os bytes congelados que ela autenticou em `D05_LEGACY_SELECTION_CAPTURE.json`;
2. **derivação fechada:** aplicar somente as regras de iteração visíveis no código legado aos arquivos comprovadamente lidos, registrando `DERIVED_FROM_OBSERVED_INPUT`, sem chamar isso de evento runtime;

O wrapper externo pertence exclusivamente à quinta fase: se autorizado pela revisão, repete somente P1/P2 no sandbox A5B, com audit hook de `open`, contador monotônico, modo/flags, path resolvido e fase. Instrumentação interna permanece proibida sem nova revisão.

O audit hook é preferível a monkeypatch porque observa aberturas sem substituir retorno, bytes ou exceções. O wrapper não importa o resolver, não lê Lock/Golden/shadow, bloqueia rede/subprocesso e rejeita escrita fora do sandbox. Escritas são registradas separadamente e nunca promovidas automaticamente a seleção.

## 9. Independência do Shadow

A captura possui dois estágios isolados:

- **capture core:** produzido apenas por código legado, A5B ou wrapper observacional; não recebe Registry, Lock, Golden nem resolved selection;
- **comparison enrichment:** após selar o SHA-256 do capture core, mapeia paths no Registry e compara com Lock/shadow.

O comparador deve rejeitar captura cujo manifesto declare qualquer contrato sombra como input. O conjunto observado nunca será filtrado pelos itens esperados.

## 10. Formato `D05_LEGACY_SELECTION_CAPTURE.json`

Campos de topo:

```text
capture_version
dataset_id
legacy_authority
source_kind
source_evidence_sha256
consumer_phases
network_disabled
repository_writes_allowed
shadow_inputs_used
selection_sets
non_selection_reads
outputs_observed
capture_summary
```

Cada conjunto registra `set_id`, `consumer_phase`, `classification`, `observation_status`, `selection_mechanism`, `order_semantics`, `multiplicity_semantics` e `items`.

Cada item bruto contém `legacy_source`, `observed_path`, `read_order`, `event_index`, `member_value` quando derivado, `ordinal_observed`, `observation_method` e `derivation_basis`. Identidades Registry não entram no capture core; ficam no artefato de comparação.

## 11. Path observado → Registry

Depois de selar a captura:

1. resolver o path observado contra roots explicitamente declaradas para a comparação;
2. obter `(storage_root_id, relative_path)` canônico, sem discovery;
3. consultar o Registry por localização literal;
4. exigir exatamente uma ocorrência;
5. `0` matches → `LEGACY_UNREGISTERED`;
6. `>1` matches → `LEGACY_AMBIGUOUS`;
7. conferir size/SHA-256 depois da identidade, sem usar hash para escolher ocorrência.

Mesmo byte em dois paths não cria equivalência. A comparação primária usa `occurrence_id`, `set_id`, papel semântico e membro.

## 12. Dimensões de comparação

R2B produz resultados separados para:

- `SETS`;
- `MEMBERSHIP`;
- `ORDER`;
- `MULTIPLICITY`;
- `DEPENDENCIES`;
- `ABSENCES`;
- `BYTE_IDENTITY`;
- `EXTRAS`;
- `MISSING`.

Por conjunto: `MATCH`, `MISMATCH`, `PARTIAL_OBSERVABILITY`, `NOT_RUNTIME_OBSERVABLE` ou `NOT_APPLICABLE`.

Agregados: `LEGACY_SHADOW_MEMBER_PARITY`, `LEGACY_SHADOW_ORDER_PARITY`, `LEGACY_SHADOW_MULTIPLICITY_PARITY`, `LEGACY_SHADOW_DEPENDENCY_PARITY` e `LEGACY_SHADOW_STATUS`, com valores `PASS`, `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS` ou `FAIL`.

Um `MISMATCH`, `LEGACY_UNREGISTERED`, `LEGACY_AMBIGUOUS`, `LEGACY_EXTRA` funcional ou `SHADOW_EXTRA` sem explicação é bloqueante.

## 13. Extras, missing e leituras auxiliares

Uma leitura é seleção quando seus bytes ou membros influenciam membership, ordem ou conteúdo do dataset na fase observada. Scripts/imports, runner, logs, hash-only output reads e arquivos de infraestrutura são `NON_SELECTION_READ`, com motivo obrigatório.

Todo path de dados não presente no conjunto sombra é `LEGACY_EXTRA` antes de qualquer reclassificação. Todo item sombra ausente da dimensão observável é `SHADOW_EXTRA`. O comparador pode então classificar `FUNCTIONAL_INPUT`, `AUXILIARY`, `CONFIG_OR_SCHEMA`, `REPORT`, `OUTPUT_HASH_READ`, `SIDE_EFFECT` ou `OUTSIDE_EXECUTED_PHASE`. Nada é descartado silenciosamente.

`MISSING` só é diferença real quando a dimensão era observável e aplicável. Fase histórica não executada produz `NOT_RUNTIME_OBSERVABLE`, não missing artificial.

## 14. Ausências

Ausência não exige evento de filesystem:

- 88 `NO_ENRICHMENT_OVERLAY_BY_DESIGN`: inferíveis de 199 obras menos 111 overlays lidos, com decisões byte-idênticas;
- 1 `CANDIDATE_EXCLUDED_FROM_USABLE_CATALOG`: inferível de 200 candidatas e 199 utilizáveis;
- 47 `NO_ADDITIONAL_CARD_AFTER_EXAMINATION`: observáveis nas decisões byte-idênticas;
- 9 `WEB_SOURCE_WITHOUT_COMPLETE_LOCAL_RECEIPT`: fora das fases locais;
- 6 `REMOTE_FETCH_FAILED_WITH_METADATA_PRESERVED`: fora das fases locais.

Resultado atual planejado: 136 `DERIVABLE_FROM_EXECUTED_PHASE`, 15 `NOT_RUNTIME_OBSERVABLE`. R2B não deve executar coleta remota para converter essas 15 em eventos.

## 15. Dependências

| dependência | observação legada | tratamento R2B |
|---|---|---|
| `catalog_69` | `EMBEDDED`; P1/P2 leem `REFERENCIA_CATALOGO_69.json`, não a ocorrência externa | `CONSISTENT_BUT_NOT_DIRECTLY_OPENED`; comparar IDs/bytes declarados sem alegar leitura externa |
| `base_catalog` | P1 produz; P2 `DIRECTLY_READ` | comparar ocorrência, hash produzido e leitura P2 |
| `enrichment_checkpoint_state` | `DIRECTLY_READ` por P2 | comparar path, bytes e membros da fila com ressalva de ordem operacional |
| `enrichment_revision_layer` | `DIRECTLY_READ` por P2 | comparar path, bytes e três IDs aplicados |

## 16. Segurança e gates de aborto R2B

Se houver execução nova:

- sandbox externo ao repositório e outputs históricos;
- cópia mínima com hashes verificados;
- somente P1/P2 com hashes de script aprovados;
- rede, subprocessos e escrita externa bloqueados;
- output inicialmente vazio;
- nenhuma leitura de Lock, Golden ou shadow pelo runner;
- nenhuma alteração de código legado;
- preservar bytes, retornos, ordem e exceções;
- abortar em input/hash/cardinalidade/path divergente;
- revalidar repositório original ao final.

Se não for possível observar sem editar o legado, R2B fica bloqueada para revisão.

## 17. Artefatos futuros R2B

```text
CLEANUP_AUDIT/D05_LEGACY_SELECTION_CAPTURE.json
CLEANUP_AUDIT/D05_LEGACY_SHADOW_COMPARISON.json
CLEANUP_AUDIT/MIGRATION_R2B_D05_LEGACY_SHADOW_RESULT.md
```

Ferramenta opcional, ainda não criada:

```text
SHADOW_RESOLVER/compare_legacy_shadow.py
```

Se um novo wrapper for aprovado, ele deverá ficar separado do código legado e ter contrato próprio.

## 18. Critério de sucesso R2B

R2B pode passar quando a captura for independente, o capture core estiver selado antes da comparação, membros/ordem/multiplicidade observáveis coincidirem, quatro dependências estiverem explicadas, extras funcionais e missing reais forem zero, dimensões históricas forem explícitas, bytes conferirem e houver zero blocking mismatch.

O status esperado admite `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS`; ele não autoriza troca de autoridade.

## 19. Riscos

- confundir toda leitura com seleção;
- promover outputs a inputs;
- usar Lock/shadow para filtrar a captura;
- afirmar ordem runtime onde o código usa dict/membership;
- perder duplicatas antes de medir semântica de sobrescrita;
- considerar hashes iguais como identidade;
- transformar fase não executada em missing;
- reexecutar coleta remota ou fechamento stateful;
- alterar comportamento com monkeypatch;
- tratar o catálogo 69 externo como diretamente lido.

## 20. Consequência

Mesmo com R2B aprovada, a autoridade continua no legado. Uma etapa posterior poderá projetar um consumer adapter que calcule legacy e shadow em paralelo, mas use somente legacy para produzir resultado. Essa etapa não integra R2A nem R2B.

## Resultado R2A

Plano de observação e comparação concluído. Nenhum pipeline, replay, captura, comparador ou consumidor foi executado ou criado.
