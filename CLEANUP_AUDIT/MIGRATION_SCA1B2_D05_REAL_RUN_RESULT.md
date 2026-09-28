# Migração SCA1B2 — primeiro ensaio real do D05 Shadow Consumer Adapter

## Resultado

Status: `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS`.

Os dois outputs funcionais foram byte a byte idênticos nas três lanes:

| output | DIRECT | Shadow OFF | Shadow ON | resultado |
|---|---|---|---|---|
| `CATALOGO_EXPANSAO_200.json` | `5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43` | mesmo SHA-256 | mesmo SHA-256 | PASS |
| `CATALOGO_TOTAL_69_MAIS_APTAS.json` | `6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6` | mesmo SHA-256 | mesmo SHA-256 | PASS |

`TRIPLE_OUTPUT_PARITY = 2/2 PASS`.

## Ambiente e sandbox

- run ID: `d05-shadow-consumer-2026-09-28-sca1b2`;
- sandbox: `EXTERNAL_TEMP_SANDBOX`, externo ao repositório, preservado para auditoria e com path absoluto redigido nesta evidência;
- Python 3.12.9, Windows 11 build 26200, UTF-8;
- `PYTHONHASHSEED=0`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`;
- 208 inputs copiados; 208/208 byte-idênticos às origens;
- consumidor copiado com SHA-256 `4e53ca2a87bd0577facb4461b09b685223c4daabe869cfaff81610e6cdc66a7d`.

## Execuções reais

### DIRECT_LEGACY

- exit code `0`;
- duração observada: 165,300 ms (0,165300 s);
- 2/2 outputs idênticos aos históricos;
- stdout funcional e stderr capturados.

### RUNNER_SHADOW_OFF

- exit code `0`;
- duração observada: 242,948 ms (0,242948 s);
- 2/2 outputs idênticos ao DIRECT;
- stdout e stderr idênticos ao DIRECT;
- Registry e Lock ausentes da raiz operacional copiada;
- nenhum binding fornecido;
- `SHADOW_OFF_INDEPENDENT = true`.

### RUNNER_SHADOW_ON

- Legacy exit code `0`;
- `shadow_status = SHADOW_OK`;
- `comparison_status = PASS_WITH_NOT_OBSERVABLE_DIMENSIONS`;
- zero mismatches bloqueantes;
- diagnóstico válido contra o schema;
- `legacy_authoritative = true`;
- `shadow_authoritative = false`;
- `shadow_did_affect_output = false`;
- 2/2 outputs e stdout idênticos ao DIRECT/OFF.

## Observer e selo

O observer registrou exatamente:

- 8 batches de triagem;
- 199 dossiês;
- 207 selection paths diretamente comparáveis;
- 1 leitura do wrapper 69 como dependência embedded;
- 5 leituras auxiliares antes do selo, não promovidas a selection members.

O evento `LEGACY_SELECTION_COMPLETE_BEFORE_FIRST_FUNCTIONAL_OUTPUT_WRITE` foi visto na primeira abertura funcional para escrita. A seleção foi congelada antes dessa escrita e leituras posteriores não retroalteraram o snapshot.

## Comparação runtime

- membership dos batches e dossiês: `MATCH`;
- ordem: `MATCH`;
- multiplicidade: `MATCH`;
- dependência embedded 69: `MATCH`;
- `catalog_69_ids`, `triage_candidate_numbers` e ausências: `NOT_OBSERVABLE`, sem promoção indevida;
- resultado: `PASS_WITH_NOT_OBSERVABLE_DIMENSIONS`.

## Performance observada

Classificação: `OBSERVED_SINGLE_RUN_OVERHEAD`, não benchmark definitivo.

Unidade de todos os campos abaixo: milissegundos (`ms`). Os equivalentes em segundos eliminam ambiguidade de separador decimal.

- DIRECT: 165,300 ms (0,165300 s);
- OFF: 242,948 ms (0,242948 s);
- ON total externo: 1.561,018 ms (1,561018 s);
- Legacy dentro do ON: 116,6526 ms (0,1166526 s);
- Shadow: 1.316,1449 ms (1,3161449 s);
- comparação: 1,2758 ms (0,0012758 s);
- primeira escrita do diagnóstico: 11,4176 ms (0,0114176 s);
- overhead ON versus DIRECT: 1.395,718 ms (1,395718 s) / 844,355%.

`PERFORMANCE_REQUIRES_FOLLOWUP = true`.

Classificação do follow-up: `NON_BLOCKING_PERFORMANCE_FOLLOWUP`. O overhead não é mismatch funcional, mas performance ainda não está aprovada para produção.

## Isolamento negativo

| cenário | Legacy | Shadow/comparação | outputs vs DIRECT | afetou output? |
|---|---:|---|---|---:|
| binding ausente | 0 | `SHADOW_FAIL_CLOSED` | 2/2 | não |
| hash Shadow adulterado em cópia sandbox | 0 | `SHADOW_FAIL_CLOSED` | 2/2 | não |
| mismatch artificial | 0 | `MISMATCH` | 2/2 | não |
| diagnóstico não gravável | 0 | warning explícito / `WRITE_FAILED` | 2/2 | não |
| erro interno Shadow controlado | 0 | `SHADOW_INTERNAL_ERROR` | 2/2 | não |

`NEGATIVE_SHADOW_ISOLATION = PASS`: 10/10 outputs negativos byte-idênticos ao baseline DIRECT.

## Segurança, escrita e integridade

- nenhum secret, URL assinada completa ou conteúdo restricted-local foi incluído na evidência;
- diagnósticos brutos permaneceram somente no sandbox externo;
- zero escrita funcional fora do sandbox;
- consumidor, Registry, Lock, Resolver e árvores funcionais originais permaneceram intactos;
- nenhum staging, commit, tag ou push foi feito nesta etapa.

## Limitação

As medições são de uma única execução por lane e não constituem benchmark. As dimensões sem observabilidade direta continuam explicitamente `NOT_OBSERVABLE`.

## Próximo passo

Recomenda-se SCA1C, em missão separada, para caracterização e profiling de performance do primeiro adapter antes de P2 ou ativação mais ampla. SCA1C não foi iniciada.
