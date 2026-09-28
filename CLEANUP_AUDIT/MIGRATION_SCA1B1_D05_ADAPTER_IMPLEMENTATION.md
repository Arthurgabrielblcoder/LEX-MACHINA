# Migração SCA1B1 — implementação isolada do D05 Shadow Consumer Adapter

## 1. Resultado e escopo

Foi implementada somente a infraestrutura isolada do primeiro Shadow Consumer Adapter para `compilar_catalogo.py`. Esta etapa não executou o consumidor, pipeline, ensaio DIRECT/OFF/ON real nem produziu os dois outputs funcionais.

Invariantes:

```text
LEGACY_AUTHORITATIVE = true
SHADOW_AUTHORITATIVE = false
SHADOW_MAY_AFFECT_FUNCTIONAL_OUTPUT = false
```

## 2. Arquivos implementados

- `SHADOW_CONSUMER_ADAPTER/run_d05_catalog_shadow.py`: runner opt-in, fronteiras de exceção, worker lazy e instrumentação;
- `SHADOW_CONSUMER_ADAPTER/legacy_observer.py`: observer externo de eventos `open` e marco semântico de selo;
- `SHADOW_CONSUMER_ADAPTER/runtime_compare.py`: comparador independente das seis dimensões;
- `SHADOW_CONSUMER_ADAPTER/diagnostic.py`: escrita atômica, sanitização e redação;
- `SHADOW_CONSUMER_ADAPTER/schemas/d05-shadow-consumer-run.schema.json`: schema do diagnóstico;
- `SHADOW_CONSUMER_ADAPTER/tests/test_d05_catalog_shadow.py`: suíte isolada com fixtures e fakes;
- `SHADOW_CONSUMER_ADAPTER/__init__.py` e `tests/__init__.py`: identidade do pacote e testes;
- `CLEANUP_AUDIT/MIGRATION_SCA1B1_D05_ADAPTER_TEST.json`: resultado canônico da suíte.

## 3. Arquitetura e feature flag

O runner é externo. `--shadow-compare` usa `store_true` e tem default `false`.

- Shadow OFF chama apenas a lane Legacy e não importa/carrega Registry, Lock ou Resolver;
- Shadow ON instala o observer na lane Legacy, chama o Resolver por import lazy, compara e produz diagnóstico;
- a API de orquestração aceita executores/workers injetáveis, permitindo comprovar isolamento sem executar o consumidor real;
- bindings existem somente em memória e aparecem no diagnóstico apenas como `storage_root_id` + status.

Não existe aresta que permita ao Shadow fornecer input, retorno, output, exit code ou fallback ao Legacy.

## 4. Observer Legacy e marco de selo

`LegacyObserver` registra contador monotônico, evento, operação, modo, path e path relativo ao D05 quando aplicável. Não substitui `open`, não altera argumento, retorno, bytes, exceção, ordem ou multiplicidade.

Ao primeiro evento de escrita dentro do output root, o observer congela as leituras anteriores sob o marco:

```text
LEGACY_SELECTION_COMPLETE_BEFORE_FIRST_FUNCTIONAL_OUTPUT_WRITE
```

A detecção depende do evento semântico e do output root, nunca das linhas 80/82. Leituras posteriores não entram no snapshot selado.

## 5. Shadow isolation

O worker converte falhas conhecidas em `SHADOW_FAIL_CLOSED` e exceções inesperadas em `SHADOW_INTERNAL_ERROR`. Ambas permanecem diagnósticas. A fronteira nunca modifica `LegacyResult`; falha de escrita do diagnóstico produz warning em `stderr` e preserva o resultado Legacy.

Não há `except Exception: pass`. Exceções inesperadas são classificadas, redigidas e registradas como `ADAPTER_INTERNAL_FAILURE`.

## 6. Comparador

O comparador suporta:

- dimensões `MEMBERSHIP`, `ORDER`, `MULTIPLICITY`, `DEPENDENCIES`, `ABSENCES` e `BYTE_IDENTITY`;
- statuses `MATCH`, `MATCH_CARDINALITY_ONLY`, `NOT_OBSERVABLE`, `LEGACY_ONLY`, `SHADOW_ONLY`, `ORDER_MISMATCH`, `MULTIPLICITY_MISMATCH`, `BYTE_MISMATCH`, `SHADOW_RESOLUTION_FAILURE` e `ADAPTER_INTERNAL_FAILURE`;
- comparação member-level somente de `triage_batch_paths` e `base_catalog_work_ids`;
- preservação de `triage_candidate_numbers` e `catalog_69_ids` como `NOT_OBSERVABLE` no Legacy runtime;
- omissão dos conjuntos Shadow que não pertencem ao consumo P1.

O adapter não promove 272 identidades históricas a observação runtime, não inventa ordem e não converte cardinalidade em member match.

## 7. Diagnóstico e segurança

O diagnóstico é marcado como `DERIVED_DIAGNOSTIC` e `NON_AUTHORITATIVE`, com `legacy_authoritative=true`, `shadow_authoritative=false` e `shadow_did_affect_output=false`.

O schema cobre status Legacy/Shadow, resumos runtime, comparação, mismatches, erros, hashes de output e performance. A implementação:

- não persiste paths de bindings;
- redige chaves de token, secret, password, API key, authorization, credential e assinatura;
- remove query string e fragmento de URLs;
- não recebe nem registra conteúdo `restricted_local`;
- escreve diagnóstico por arquivo temporário + substituição atômica;
- mantém falha de telemetria fora do resultado Legacy.

## 8. Performance instrumentation

São medidos com relógio monotônico:

- `legacy_duration_ms`;
- `shadow_duration_ms` e alias contratual `shadow_resolution_duration_ms`;
- `comparison_duration_ms`;
- `diagnostic_write_duration_ms`;
- `total_duration_ms` e `adapter_wall_duration_ms`;
- `shadow_overhead_ms` e `overhead_absolute_ms`;
- `shadow_overhead_percent` e `overhead_percent_vs_direct_legacy`.

A fórmula foi validada somente com fakes; nenhuma medição do consumidor real pertence à SCA1B1.

## 9. Testes

Resultado: `PASS`, 30 testes.

- positivos: 15/15, acima do mínimo 12;
- negativos: 12/12;
- crítico de isolamento: 1/1;
- suporte de redação/bindings: 2/2.

O teste crítico fixa `legacy_result = X`, força exceção Shadow e comprova: resultado Legacy igual a `X`, status Shadow diferente de sucesso e `shadow_did_affect_output=false`.

O teste Shadow OFF bloqueia `importlib.import_module` e comprova que Registry, Lock, Resolver e bindings não são exigidos.

## 10. Consumidor e integridade

O consumidor permaneceu sem import, callback, flag, assinatura, dump, sorting ou filtro novo. SHA-256 antes e depois:

```text
4e53ca2a87bd0577facb4461b09b685223c4daabe869cfaff81610e6cdc66a7d
```

Nenhum teste importa ou executa `compilar_catalogo.py`. A referência ao consumidor nos testes serve apenas para leitura de bytes e verificação SHA-256.

## 11. Limitações

- o audit hook e a integração real com o Resolver ainda não foram exercitados contra o consumidor;
- igualdade DIRECT/OFF/ON e overhead real ainda não foram medidos;
- paths absolutos podem existir somente no diagnóstico runtime local futuro;
- proteção de sandbox da futura execução real não foi validada nesta etapa;
- o runner contém o entrypoint futuro, mas a SCA1B1 testou exclusivamente funções com fixtures/fakes.

## 12. Plano SCA1B2

Em missão separada, executar DIRECT, wrapper OFF e wrapper ON em sandbox externo e vazio, validar igualdade byte a byte dos dois outputs, stdout e exit code, exercitar o audit hook real, verificar escrita do diagnóstico fora das árvores funcionais e medir overhead. Abortar se qualquer byte ou resultado Legacy divergir.

SCA1B2 não foi iniciada.
