# Migração SCA1A — especificação do primeiro Shadow Consumer Adapter D05

## 1. Escopo e decisão

Esta especificação projeta, mas não implementa, o primeiro piloto de Shadow Consumer Adapter do D05. O consumidor recomendado é:

```text
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/compilar_catalogo.py
```

Autoridade invariável:

```text
LEGACY_AUTHORITATIVE = true
SHADOW_AUTHORITATIVE = false
SHADOW_MAY_AFFECT_FUNCTIONAL_OUTPUT = false
```

O piloto será estritamente opt-in, observacional e limitado a um consumidor. Esta etapa não cria adapter, feature flag, teste executável ou alteração no consumidor.

Baseline validada para o projeto:

- HEAD: `1ab8a788dba29678ea0eae6cdd0cdaacb33e5180`;
- consumidor P1 SHA-256: `4e53ca2a87bd0577facb4461b09b685223c4daabe869cfaff81610e6cdc66a7d`;
- Legacy capture SHA-256: `c9c48e8852f3952a1c05de528a6cf25124ce264f1f86194400bea2812f460ae0`;
- Shadow selection SHA-256: `28212c24f88f07538d4cd5c50d1ce9f0ff603d684c477dfd23ec9984ae8db57a`;
- comparação R2B2 SHA-256: `1365007b58e74bdab0c8ddf6411ea670301671f6f156b88c057904e8486dc831`;
- estado R2B2: `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS`.

## 2. Escolha do consumidor

| critério | `compilar_catalogo.py` | `compilar_enriquecido_v1.py` |
|---|---|---|
| fluxo | linear: lotes → filtro → dossiês → referência 69 | ramificado: base → checkpoint/dict → overlays → revisões → cards |
| inputs observados A5B | 8 lotes + 199 dossiês + wrapper 69 | catálogo-base + checkpoint + revisões + 111 overlays + wrapper 69 |
| eventos diretamente comparáveis | 207 paths, em duas séries simples | 111 overlays; fila derivada adicional |
| outputs funcionais | 2 | 7 |
| semântica de sobrescrita | nenhuma indexação relevante por dict | fila por `work_id` e revisões por `evidence_id` |
| branching | filtro único `USABLE` | existência de overlay, aplicação de patch e várias asserts |
| ponto antes da primeira escrita | único e nítido | existe, mas após transformação substancial de cards |
| determinismo | 2/2 byte-idênticos em A5B | 7/7 byte-idênticos em A5B |
| risco do primeiro piloto | menor | maior |

Embora P1 abra mais arquivos, sua superfície comportamental e de output é menor. Ele não contém checkpoint, camada de revisão, overwrite por dict ou sete produtos correlacionados. P1 também maximiza a prova direta do primeiro piloto: 207 paths observáveis, contra 111 overlays diretamente observáveis em P2.

Recomendação: começar por `compilar_catalogo.py`. P2 permanece fora de SCA1B.

## 3. Opções de integração

| opção | alteração do consumidor | observa seleção real | risco | decisão |
|---|---:|---:|---:|---|
| A. wrapper externo + audit hook | zero | sim, para eventos de filesystem | mínimo | **escolhida** |
| B. adapter importado pelo consumidor | import e branch novos | sim | médio; acopla Registry/Lock/Resolver | rejeitada no primeiro piloto |
| C. callback observacional mínimo | assinatura/call site novos | sim, inclusive valores em memória | médio; callback pode interferir | adiada; exige revisão própria |
| D. cópia do consumidor | duplica código | não garante equivalência futura | alto | proibida |

SCA1B deve usar um runner externo. O consumidor não importará Registry, Lock, Resolver ou comparator. O runner instalará um audit hook CPython que apenas registra eventos; não substituirá `open`, não mudará argumentos, retornos, bytes, exceções ou ordem.

## 4. Arquitetura proposta

```text
                         ┌─────────────────────────────┐
                         │ runner opt-in SCA1B        │
                         └──────────────┬──────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 │                                             │
                 ▼                                             ▼
      LEGACY LANE / AUTHORITATIVE                    SHADOW LANE / DIAGNOSTIC
      consumidor original e imutável                 Registry + Lock + bindings
                 │                                             │
      audit hook observa leituras                              resolver fail-closed
                 │                                             │
                 ▼                                             ▼
      output funcional legado                         shadow runtime selection
                 │                                             │
                 └───────────────┐             ┌───────────────┘
                                 ▼             ▼
                              comparator runtime
                                      │
                                      ▼
                              diagnóstico somente
```

Não existe aresta do Shadow para a seleção, objetos de output, diretório de output, retorno ou exit code do Legacy.

## 5. Ponto de integração lógico

Consumidor: `compilar_catalogo.py`, função `main`.

Seleção legada:

- linhas 32–35: concatenação dos oito lotes e asserts de 200 candidatas únicas;
- linhas 36–55: filtro `USABLE`, ordem por `work_id` e leitura dos 199 dossiês;
- linhas 65–80: leitura do wrapper 69, ordem por `id` e construção da união.

Fronteira ideal: depois da construção de `total` na linha 80 e antes da primeira escrita funcional na linha 82.

Os números 80/82 são apenas referência humana para o snapshot atual do consumidor. O contrato operacional não depende de linha fixa: ele depende do evento semântico `LEGACY_SELECTION_COMPLETE_BEFORE_FIRST_FUNCTIONAL_OUTPUT_WRITE`, reconhecido pelo primeiro evento de escrita dentro do output root após as leituras de seleção.

Dados existentes nesse ponto:

- `triage`: lista legada de 200 entradas;
- `works`: 199 obras utilizáveis na ordem efetivamente consumida;
- `ref` e `existing`: representação embedded do catálogo 69;
- `novas`, `expansao` e `total`: objetos que serão escritos;
- multiplicidade preservada nas listas.

SCA1B não injetará código nessa fronteira. O audit hook externo capturará os eventos ao longo da seleção e congelará o registro quando observar a primeira tentativa de escrita dentro do output root. A comparação ocorrerá fora do consumidor, depois da execução Legacy; a fronteira serve para separar leituras de seleção de releituras de output.

## 6. Captura `LEGACY_RUNTIME_SELECTION`

O runner deve executar o arquivo original, com seus bytes previamente aprovados, usando `runpy.run_path` ou subprocesso controlado e os mesmos argumentos do consumidor.

O audit hook deve registrar, sem alterar o evento:

- contador monotônico;
- operação e modo/flags;
- path resolvido e path relativo ao root D05;
- fase `P1`;
- classificação inicial `READ`, `WRITE` ou `OTHER`;
- boundary da primeira escrita no output root.

Projeções permitidas:

- `triage_batch_paths`: oito leituras `02_TRIAGEM/LOTE_*.json`, com ordem e multiplicidade observadas;
- `base_catalog_work_ids`: leituras `04_DOSSIERS/*.json`, com ordem, multiplicidade e `work_id` derivável do filename;
- wrapper `00_ENTRADA/REFERENCIA_CATALOGO_69.json`: dependência embedded diretamente lida;
- scripts e releituras de output: `AUXILIARY_READ`, nunca selection member.

Limites obrigatórios do wrapper externo:

- `triage_candidate_numbers`: `NOT_OBSERVABLE` member-level; não parsear lotes para reimplementar a lógica;
- `catalog_69_ids`: `NOT_OBSERVABLE` member-level; não parsear wrapper para fabricar observação runtime;
- ausência da candidata excluída: não afirmar identidade sem valor observado;
- não recalcular `USABLE` fora do consumidor;
- não inferir seleção a partir do Shadow.

O adapter observa os mesmos opens que o consumidor usa. Ele não cria `LEGACY_MODEL_A` em paralelo.

## 7. Resolução `SHADOW_RUNTIME_SELECTION`

Com `--shadow-compare`, uma lane isolada deve executar o resolver existente com:

- `ARTIFACT_REGISTRY/index.json`;
- `DATASET_LOCKS/d05-historical-parity-v1.lock.json`;
- SHA-256 esperado do Lock;
- bindings runtime explícitos;
- roots permitidas exatas;
- nenhum discovery implícito.

O resultado mantém:

```text
artifact_class = DERIVED
mode = SHADOW
authority = NON_AUTHORITATIVE
```

O Shadow pode rodar em processo/worker separado enquanto o Legacy executa. O join e a comparação podem aumentar o tempo total do runner, mas nunca atrasar ou impedir as escritas funcionais do Legacy. O diretório funcional não será gravável pela lane Shadow.

## 8. Política de falha

O resolver continua fail-closed dentro da lane Shadow. A fronteira externa converte qualquer falha Shadow em diagnóstico não bloqueante para o Legacy.

| evento | resultado Legacy | diagnóstico | exit code do runner |
|---|---|---|---|
| binding/restricted_local ausente | preservado | `SHADOW_RESOLUTION_FAILURE` | exit code Legacy |
| Registry/Lock/hash/path inválido | preservado | `SHADOW_RESOLUTION_FAILURE` | exit code Legacy |
| erro interno do adapter | preservado | `ADAPTER_INTERNAL_FAILURE` | exit code Legacy |
| mismatch Legacy × Shadow | preservado | diferença estruturada | exit code Legacy |
| diagnóstico não gravável | preservado | warning explícito em stderr, sem secrets | exit code Legacy |
| falha do próprio Legacy | falha original | best-effort, separada de Shadow | exit code/exception Legacy |

É proibido `except Exception: pass`. Toda exceção Shadow/adapter deve ser capturada em fronteira estreita, classificada, sanitizada e emitida no diagnóstico ou, se impossível, em warning explícito. Nenhuma exceção Shadow pode substituir uma exceção Legacy.

## 9. Comparador runtime

Dimensões e regras:

- `MEMBERSHIP`: member-level apenas para os paths diretamente observados;
- `ORDER`: somente para lotes e dossiês, usando sequência do audit hook;
- `MULTIPLICITY`: `Counter` de eventos, sem deduplicação;
- `DEPENDENCIES`: wrapper 69 como `EMBEDDED`, não exigir open direto da ocorrência externa;
- `ABSENCES`: apenas quando deriváveis dos eventos Legacy observados; caso contrário `NOT_OBSERVABLE`;
- `BYTE_IDENTITY`: locator Registry primeiro; hash/tamanho somente depois; opcionalmente revalidado fora do caminho funcional.

Statuses:

```text
MATCH
MATCH_CARDINALITY_ONLY
NOT_OBSERVABLE
SHADOW_ONLY
LEGACY_ONLY
ORDER_MISMATCH
MULTIPLICITY_MISMATCH
BYTE_MISMATCH
SHADOW_RESOLUTION_FAILURE
ADAPTER_INTERNAL_FAILURE
```

As limitações R2B2 continuam válidas. O adapter não promoverá os 272 IDs históricos a member-level match e não tratará os 1.699 itens do Lock como runtime-observed.

## 10. Mismatch

Todo mismatch deve registrar:

- severidade diagnóstica;
- `set_id`;
- dimensão;
- membro/path Legacy, quando observado;
- membro Shadow, quando aplicável;
- identidade Registry somente após locator unívoco;
- evidência e classificação.

Severidades sugeridas: `INFO`, `WARNING`, `ERROR_DIAGNOSTIC`. Nenhuma severidade Shadow é funcionalmente bloqueante no piloto. É proibido substituir input, completar Legacy, corrigir output, fazer fallback Shadow ou abortar um Legacy saudável.

## 11. Feature flag

Ativação proposta no runner novo:

```text
python SHADOW_CONSUMER_ADAPTER/run_d05_catalog_shadow.py [legacy args] --shadow-compare ...
```

- execução direta do consumidor original: comportamento atual, sem adapter;
- runner sem `--shadow-compare`: delegação Legacy, sem carregar Registry/Lock/Resolver e sem audit hook Shadow;
- runner com `--shadow-compare`: Legacy normal + observação + Shadow + diagnóstico;
- default: Shadow desabilitado.

Não usar variável de ambiente como mecanismo primário. CLI explícita reduz ativação acidental e melhora rastreabilidade.

## 12. Diagnóstico runtime

Nome: `D05_SHADOW_CONSUMER_RUN.json`.

Campos mínimos:

```text
adapter_version
consumer
legacy_authoritative = true
shadow_authoritative = false
shadow_enabled
legacy_exit_status
registry_sha256
lock_sha256
resolved_selection_sha256
legacy_runtime_summary
shadow_runtime_summary
comparison
mismatches
shadow_errors
adapter_errors
legacy_output_hashes
shadow_did_affect_output = false
performance
```

Destino padrão recomendado: diretório temporário externo ao repositório. `CLEANUP_AUDIT/runtime_shadow/` somente com opção explícita de diagnóstico. Nunca gravar em D05, `ENRIQUECIDO_V1`, V2, firmware, SD ou output root funcional.

O diagnóstico é não canônico e pode conter paths absolutos necessários ao runtime. Eles devem ficar restritos ao diagnóstico local. Bindings persistidos devem ser redigidos para IDs e status.

## 13. Segurança

O adapter não deve:

- registrar conteúdo de `restricted_local`;
- copiar arquivos `restricted_local`;
- persistir binding local em artefato versionável;
- registrar tokens, URLs assinadas, headers, credenciais ou environment dump;
- seguir symlink/traversal fora das roots aprovadas;
- permitir escrita Shadow no output root Legacy.

Para restricted-local, registrar no máximo `storage_root_id`, `occurrence_id`, status e hash esperado/verificado quando seguro. Mensagens de exceção devem passar por redaction de paths/segredos antes do diagnóstico.

## 14. Garantia de zero impacto

SCA1B deverá comparar três execuções em sandbox externo e vazio:

```text
DIRECT_LEGACY
WRAPPER_SHADOW_OFF
WRAPPER_SHADOW_ON
```

Para os dois outputs funcionais, exigir igualdade de nomes, contagem, tamanho e SHA-256:

```text
DIRECT_LEGACY == WRAPPER_SHADOW_OFF == WRAPPER_SHADOW_ON
```

Também exigir mesmo stdout funcional e mesmo exit code Legacy, descontando apenas warnings/diagnóstico emitidos pela camada Shadow em canal separado. O adapter nunca poderá abrir os objetos de output para escrita.

## 15. Performance

Medidas obrigatórias futuras, com relógio monotônico:

- `legacy_duration_ms`;
- `shadow_resolution_duration_ms`;
- `comparison_duration_ms`;
- `diagnostic_write_duration_ms`;
- `adapter_wall_duration_ms`;
- `overhead_absolute_ms`;
- `overhead_percent_vs_direct_legacy`;
- bytes lidos e quantidade de hashes por lane, quando disponíveis.

Medir múltiplas repetições com mesma máquina e cache documentado; reportar mediana e dispersão. Não aprovar uso permanente enquanto overhead e contenção de I/O não forem conhecidos.

## 16. Testes positivos previstos SCA1B

1. execução direta do Legacy reproduz 2/2 outputs baseline;
2. wrapper Shadow OFF produz outputs byte-idênticos ao Legacy direto;
3. wrapper Shadow ON produz outputs byte-idênticos ao Legacy direto;
4. oito lotes são capturados em ordem;
5. 199 dossiês são capturados em ordem e sem deduplicação;
6. wrapper 69 é observado como embedded;
7. Shadow resolve com autoridade `NON_AUTHORITATIVE`;
8. comparação executa e preserva dimensões `NOT_OBSERVABLE`;
9. estado atual produz zero mismatch comparável;
10. diagnóstico contém `legacy_authoritative=true`, `shadow_authoritative=false` e `shadow_did_affect_output=false`;
11. diagnóstico fica fora das árvores funcionais;
12. overhead é medido.

## 17. Testes negativos previstos SCA1B

Para cada teste, o output Legacy deve continuar igual ao baseline, salvo falha independente do próprio Legacy:

1. Registry inválido;
2. Lock inválido;
3. binding faltando;
4. restricted-local faltando;
5. hash Shadow divergente;
6. mismatch Shadow artificial;
7. exceção interna do adapter;
8. diretório diagnóstico não gravável;
9. timeout da lane Shadow;
10. path traversal/symlink fora da root;
11. tentativa de logar secret é redigida/rejeitada;
12. falha Legacy simultânea permanece a falha principal.

Verificações específicas: nenhuma escrita Shadow no output root; nenhum fallback; exit code igual ao Legacy; warning explícito para falha de telemetria; diagnóstico de falha sanitizado.

## 18. Arquivos previstos para SCA1B

Proposta inicial, ainda não criada:

```text
SHADOW_CONSUMER_ADAPTER/run_d05_catalog_shadow.py
SHADOW_CONSUMER_ADAPTER/runtime_compare.py
SHADOW_CONSUMER_ADAPTER/schemas/d05-shadow-consumer-run.schema.json
SHADOW_CONSUMER_ADAPTER/tests/test_d05_catalog_shadow.py
CLEANUP_AUDIT/MIGRATION_SCA1B_D05_SHADOW_CONSUMER_RESULT.md
```

Não modificar `compilar_catalogo.py` em SCA1B sob a abordagem A. Se o audit hook se mostrar insuficiente, bloquear e pedir revisão antes de considerar callback; não mudar silenciosamente para opção C.

## 19. Riscos e gates de aborto

Riscos:

- audit hook classificar leitura auxiliar como seleção;
- runner alterar cwd, argv, encoding, ambiente ou exit code;
- lane Shadow competir por I/O e aumentar latência;
- exceção Shadow escapar para o Legacy;
- diagnóstico vazar binding/secret;
- comparação reivindicar identidade nas dimensões não observáveis;
- path igual ser tratado como papel semântico igual;
- escrever diagnóstico em árvore funcional;
- um callback futuro receber referência mutável a objetos Legacy.

Abortar SCA1B antes de consolidar se:

- qualquer byte funcional divergir;
- Shadow alterar seleção, output, retorno ou exceção Legacy;
- Shadow OFF exigir Registry/Lock/bindings;
- falha Shadow bloquear Legacy saudável;
- diagnóstico expuser secret/restricted-local;
- houver locator Registry ambíguo/não resolvido no escopo comparável;
- limites R2B2 forem promovidos a match sem nova evidência;
- for necessária edição do consumidor para a abordagem A.

## 20. Critérios de sucesso SCA1B

SCA1B somente poderá passar quando:

- ativação for opt-in e default OFF;
- consumidor original permanecer sem modificação;
- Shadow OFF funcionar sem Registry, Lock ou bindings;
- Legacy continuar exclusivamente autoritativo;
- outputs direct/off/on forem byte-idênticos;
- seleção Legacy for observada, não reimplementada;
- resolver e comparador rodarem quando habilitados;
- mismatches/falhas Shadow forem somente diagnóstico;
- zero fallback e zero alteração de seleção Legacy;
- diagnóstico seguro for produzido fora das árvores funcionais;
- overhead for medido;
- verificadores Registry, Lock e Resolver permanecerem `PASS`;
- nenhuma dimensão não observável receber match indevido.

## Resultado SCA1A

Consumidor recomendado: `compilar_catalogo.py`.

Integração recomendada: wrapper externo opt-in com audit hook somente observacional, resolver isolado e diagnóstico fora das árvores funcionais.

Nenhum adapter foi implementado e SCA1B não foi iniciada.

`MIGRACAO_SCA1A_CONCLUIDA — AGUARDANDO_REVISAO`
