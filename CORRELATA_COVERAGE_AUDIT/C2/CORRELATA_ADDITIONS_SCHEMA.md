# C2 — Schema do overlay CORRELATA_ADDITIONS

**Projeto, não implementação.** O arquivo `LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json` **não foi criado**. O protótipo em
`C2/prototype/correlata_overlay.py` valida fixtures, mas não está ligado ao `reference_engine.py` nem ao export RUN3.

## Princípios

1. **O catálogo legado é imutável.** O `CF88_REFERENCES_CANONICAL.json` e a camada `SD_RELATIONS_REL_LOOKUP` não são editados.
2. **Erro legado é neutralizado por exclusão.** Cada REMOVE, ou a parte "remover" de um RETARGET ou REPLACE, vira um registro em `CF88_LINK_EXCLUSIONS.json`, que retira exatamente um `reference_id` (ver § Exclusões).
3. **Relação nova entra só por additions.** Isso vale para APPROVE e ADJUST do HIGH, para o destino de RETARGET e REPLACE e para a rota corrigida de KEEP_WITH_ROUTE_FIX.
4. **Fail closed.** Um único registro inválido interrompe o build e não sai overlay parcial. O padrão é o mesmo de `work_reference_additions` (`HUMAN_APPROVED_REFERENCE_V1`).

## Registro

| Campo | Tipo | Regra |
|---|---|---|
| `relation_id` | str | Único. Prefixo `CORR_ADD_`. |
| `target_id` | str | Target canônico existente (ver regra de status abaixo). |
| `destination_norm_id` | str | Id do registro de destinos: id do acervo principal (`CDC1990`) ou `EXT_*`. |
| `destination_route` | enum | `MAIN_CORPUS` ou `EXT_NORMAS`. |
| `destination_articles` | list[str] | Cada artigo existe no índice da norma. Lista vazia só com a flag `OPEN_NORM_FALLBACK`. |
| `relation_type` | enum | REGULAMENTA, COMPLEMENTA, IMPLEMENTA, PROCEDIMENTO, CONDIÇÃO_OU_EXCEÇÃO, ORGANIZA_INSTITUIÇÃO. |
| `legal_basis` | str | Dispositivo e fundamento, curto. |
| `scope` | list | ESCOPO_* , NON_EXCLUSIVE, TRANSITORIA, SUBSIDIARIA. |
| `flags` | list | JUDICIAL_RESTRICTIONS, OPEN_NORM_FALLBACK, DOES_NOT_IMPLEMENT_COMPLEMENTARY_LAW_EXCEPTION etc. |
| `temporal_status` | enum | IN_FORCE, VACATIO_LEGIS, PARTIAL_EFFECTS, TRANSITIONAL. REVOKED e UNCERTAIN são rejeitados. |
| `effective_from` | date \| null | Obrigatório em VACATIO_LEGIS. |
| `early_application_possible` | bool \| null | Informativo. |
| `revalidate_on` | date/str \| null | Obrigatório em TRANSITIONAL. |
| `vacatio_policy` | enum \| null | Obrigatório em VACATIO_LEGIS: `DO_NOT_PUBLISH_AS_CURRENT`. |
| `judicial_status` | obj \| null | Obrigatório com PARTIAL_EFFECTS ou JUDICIAL_RESTRICTIONS (ver política judicial). |
| `review_status` | const | `HUMAN_APPROVED_CORRELATA_V1`. |
| `reviewer` | str | Rodada ou revisor. |
| `decision_id` | str | `candidate_id` do HIGH, ou id da decisão C1A ou da revisão legada. |
| `provenance` | str | Artefato de decisão de origem. |

## Regra de status do target

- Status `CURRENT` ou `STRUCTURAL` no motor: aceito.
- Status `HISTORICAL_ONLY` no motor, ou runtime diferente de `CURRENT`: rejeitado (`TARGET_HISTORICAL_OR_REVOKED`).
- Status `UNKNOWN_VALIDITY`: rejeitado (`TARGET_STATUS_NOT_ALLOWED`). A única exceção é a regra do ADCT, descrita em `CORRELATA_DEVICE_ROUTE_DESIGN.md`.

## Resultado do validador por registro

| `device` | Quando |
|---|---|
| `PUBLISH` | Destino no cartão ou no acervo principal, sem restrição. |
| `PUBLISH_WITH_JUDICIAL_NOTICE` | Destino disponível e `judicial_status` presente: exibe `notice_short`. |
| `HIDDEN_UNTIL_EFFECTIVE` | VACATIO_LEGIS com `as_of < effective_from`. |
| `BLOCKED_INGESTION_REQUIRED` | Norma EXT ainda não ingerida. A decisão jurídica vale, o aparelho espera a ingestão. |

## Códigos de rejeição (fail closed)

- **Registro:** `MISSING_FIELD`, `NOT_APPROVED`, `RELATION_TYPE_INVALID`, `DUPLICATE`.
- **Target:** `TARGET_NOT_FOUND`, `TARGET_HISTORICAL_OR_REVOKED`, `TARGET_STATUS_NOT_ALLOWED`, `ADCT_NOT_CONFIRMED_BY_RUNTIME`.
- **Rota e destino:** `ROUTE_INVALID`, `DESTINATION_NORM_NOT_FOUND`, `MAIN_CORPUS_UNRESOLVABLE`, `MAIN_CORPUS_NORM_DUPLICATED_AS_EXT`.
- **Artigos de destino:** `DESTINATION_ARTICLE_INVALID`, `DESTINATION_ARTICLES_EMPTY_WITHOUT_FALLBACK`.
- **Temporal e judicial:** `TEMPORAL_STATUS_INVALID`, `TEMPORAL_STATUS_NOT_PUBLISHABLE`, `VACATIO_WITHOUT_POLICY`, `TRANSITIONAL_WITHOUT_REVALIDATION`, `JUDICIAL_RESTRICTIONS_INCOMPLETE`.

## Exclusões (`CF88_LINK_EXCLUSIONS.json`)

O mecanismo atual continua adequado para os erros materiais legados.

- **Como funciona hoje:** status `MATERIAL_MISMATCH_EXCLUDED`, um `reference_id` por registro, com conferência de `target_id` e `source_id` contra o build sem filtro e fail closed.
- **REMOVE:** gera uma exclusão.
- **RETARGET e REPLACE:** geram uma exclusão do vínculo antigo e uma addition do novo.
- **KEEP_WITH_ROUTE_FIX:** a rota está na linha `RELACOES` legada. A correção mais limpa é excluir o vínculo legado e reemitir a mesma relação por addition, com `destination_articles` corrigidos. O legado continua intocado.
- **Lacuna:** o status `MATERIAL_MISMATCH_EXCLUDED` não descreve uma supressão temporária, como Lei 14.965 × art. 37, II, que está correta mas ainda em vacatio.
  - Proposta: um segundo status, `TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE`, com campo `until`, aceito pelo mesmo validador.
  - É uma mudança futura no motor (C3) e não foi implementada.
