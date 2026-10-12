# C2 — Relatório de arquitetura da camada CORRELATA

**Status: PASS (projeto e protótipo).** Nada foi integrado ao export operacional.

- **Arquivos intocados:** `CF88_CORRELATA_ADDITIONS.json` (não existe), `CF88_LINK_EXCLUSIONS.json`, catálogo canônico, RUN3, REF_LOOKUP, REF_PAYLOAD, cartão e firmware.

## Documentos

- `CORRELATA_ADDITIONS_SCHEMA.md`: schema, princípios (catálogo imutável, exclusão e addition), códigos de rejeição e avaliação das exclusões.
- `CORRELATA_DEVICE_ROUTE_DESIGN.md`: rotas `EXT_NORMAS` e `MAIN_CORPUS` com fallback seguro, regra do ADCT e capacidade do cartão.
- `CORRELATA_TEMPORAL_POLICY.md`: estados temporais, vacatio (recomendação A, ocultar até a vigência), transitional e revalidações.
- `CORRELATA_JUDICIAL_STATUS_POLICY.md`: estrutura mínima do status judicial e caso Lei 14.701/2023.

## Protótipo

- `prototype/correlata_overlay.py`: validador fail-closed, só leitura.
- **Fixtures:**
  - `fixtures/destination_registry.json`: 6 normas, com índices de artigos tirados do pin C0 ou do texto oficial;
  - `fixtures/correlata_additions_fixture.json`: 6 registros válidos;
  - `fixtures/correlata_additions_invalid.json`: 1 registro inválido.
- **Testes:** `tests/test_correlata_c2_prototype.py`.

| Fixture | Rota | Verificação do target | Resultado no aparelho (2026-10-11) |
|---|---|---|---|
| CDC × art. 5º, XXXII | MAIN_CORPUS | ENGINE_CURRENT | PUBLISH |
| LC 63 × art. 161, I | EXT_NORMAS (no cartão) | ENGINE_CURRENT | PUBLISH |
| Lei 14.965 × art. 132 | EXT_NORMAS | ENGINE_STRUCTURAL | HIDDEN_UNTIL_EFFECTIVE (PUBLISH a partir de 2028-01-01) |
| Lei 14.701 × art. 231, § 1º | EXT_NORMAS | ENGINE_CURRENT | BLOCKED_INGESTION_REQUIRED (com aviso judicial quando ingerida) |
| LC 146 × ADCT, art. 10, II, b | EXT_NORMAS | ADCT_RUNTIME_CONFIRMED | BLOCKED_INGESTION_REQUIRED |
| LC 160 × ADCT, art. 128, § 2º | EXT_NORMAS | ADCT_RUNTIME_CONFIRMED | BLOCKED_INGESTION_REQUIRED |
| inválida (art. 40, § 4º, II) | — | — | rejeitada |

**Fail closed coberto por teste:**

- **Target:** inexistente; histórico ou revogado; ADCT não confirmado pelo runtime.
- **Destino:** norma inexistente; rota inválida; artigo inválido; lista de artigos vazia sem fallback; MAIN_CORPUS irresolúvel; norma do acervo principal duplicada como EXT.
- **Registro:** status não aprovado; duplicata; campo ausente.
- **Temporal e judicial:** VACATIO sem política; JUDICIAL_RESTRICTIONS incompleta (dois casos); TRANSITIONAL sem revalidação; status temporal não publicável.

## Blockers para a implementação (C3)

1. **Firmware:** modo `ABRIR_NORMA_PRINCIPAL` para a rota MAIN_CORPUS (19 aceitos) e fim do limite de 32 normas e 64 linhas.
2. **Ingestão:** as 51 relações aceitas com `INGESTION_REQUIRED` precisam de normas EXT novas (`INGESTION_PHASE_DEFERRED_FOR_CREDIT_BUDGET`).
3. **Motor:**
   - integrar o validador ao `reference_engine.py` como `correlata_additions`;
   - adicionar o status `TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE` nas exclusões;
   - aplicar a regra ADCT pelo runtime;
   - a solução definitiva é o motor reconhecer o ADCT no texto operacional.
4. **UI:** exibir `notice_short` (status judicial) no aparelho.

## Respostas da missão

- **ADCT suportado pelo projeto:** sim, pela confirmação do runtime, sem liberar `UNKNOWN_VALIDITY` genericamente.
- **MAIN_CORPUS suportado pelo projeto:** sim, com norma, artigo e fallback seguro, sem duplicar como EXT_NORMAS.
- **Política de vacatio definida:** sim, `DO_NOT_PUBLISH_AS_CURRENT` (opção A).
- **Política de status judicial definida:** sim, com estrutura mínima e aviso curto.
