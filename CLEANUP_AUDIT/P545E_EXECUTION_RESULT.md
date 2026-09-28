# P545E — Realocação protected545 dos candidatos aprovados

**Resultado: `P545E_CONCLUIDA — 29_CANDIDATOS_PROTECTED545_REALOCADOS`.**

A execução foi feita sob a `PROTECTED545_RELOCATION/PROTECTED545_RELOCATION_POLICY_V2.md`. A autorização do operador está registrada textualmente como `OPERATOR_APPROVAL_RECORDED` e cobre somente estes 29 candidatos. A política histórica `CLEANUP_AUDIT/PROTECTED545_POLICY.md` foi preservada sem alteração.

## Resumo

| Métrica | Valor |
|---|---|
| AUTHORIZED | 29 |
| MOVED | **29** (P545E_1: 16; P545E_3: 13) |
| DEFERRED / FAILED | 0 / 0 |
| BYTES_RELOCATED | **2.857.446.527** |
| FILES_RELOCATED | 22.273 |
| PROTECTED_OCCURRENCES_RELOCATED | 230 (121 + 109) |
| ORIGINAL_PATH_PRESENT / VALID_RELOCATION | 315 / 230 (total 545) |
| MISSING / HASH_MISMATCH / AMBIGUOUS / INVALID_LINEAGE | 0 / 0 / 0 / 0 |
| IDX_RELOCATED / IDX_VALIDATED | 109 / 109 (130/130 ocorrências IDX válidas) |
| LEGACY_VIEW_545 | 545/545 (`C:\LMA\lv\final`) |
| Verificador congelado `r1d_support.integrity()` na visão | passed |
| V2_281 (vivo / visão) | 281 / 281 |
| ENRIQUECIDO_V1 | 7/7 |
| REGISTRY / LOCK / RESOLVER | PASS / PASS / PASS |
| Hash de `INTEGRITY_BEFORE.json` | `a319f0ea917b0e6c00e037ba5b7a5c97b351d1b0af00b79862ae98db7cfd91c2` (inalterado) |
| Seleção D01 (55 marcadores) | inalterada |
| ROLLBACK_READY | true (29/29) |
| NON_AUTHORIZED_CANDIDATES_UNTOUCHED | 26/26 |
| 2E5, 2E6 e 2E41 | presentes |
| Candidatos ONDA 2 na raiz | 59 → **33** (26 de topo; os outros 3 eram subpastas de `firmware/`) |
| Diretórios de topo na raiz | 72 → **46** |
| Archive root | `C:\LMA\p545e\20260928` |
| ARCHIVE_IS_BACKUP | false |
| DISK_SPACE_FREED | **0** (mesmo volume C:; é relocação, não liberação física) |
| PERMANENT_DELETIONS | 0 |

## Âncoras

| Etapa | Commit | Tag |
|---|---|---|
| Framework, análise, sandbox e política aprovada | `d114f68aed7828a98df127cdb06976de4255f2ef` | `pre-protected545-relocation-2026-09-28` |
| Lote 1 (ledger 121 eventos) | `2afc9976b426e758c0c904f724eebca467ec5b74` | `protected545-relocation-batch1-2026-09-28` |
| Lote IDX (ledger 230 eventos) | `a2192f558234b87057130a2b227a952f6747445e` | `protected545-relocation-idx-batch-2026-09-28` |

**Ledger:** `PROTECTED545_RELOCATION/ledger/P545_RELOCATION_LEDGER.json`, com head count 230 e event_hash `4665bae677a9dd5bdfe8e4f04df537a48d1fce994dc01ab22222618dda436ae1`. Só contém eventos RELOCATE; o append-only foi verificado entre os dois lotes.

**Detalhes:** a lista por candidato, com inventário pré/pós, eventos e rollback, está em `P545E_EXECUTION_RESULT.json` e `P545E_MOVES.csv`. As tabelas por lote estão em `P545E_BATCH1_RESULT.md` e `P545E_BATCH3_RESULT.md`.

## Regras operacionais a partir de agora

- **`HISTORICAL_TOOL_REQUIRES_LEGACY_VIEW`.** Estas ferramentas **não** rodam no repo vivo; qualquer reprodução histórica é feita sobre uma visão gerada por `materialize_legacy_view.py`:
  - `r1d_support.integrity()` e os gates R1D/R1D1 (`r1d1_pipeline.py`, `gate_r1d.py`, `run_regression_r1d.py`, `runner_integral_r1d.py`, `finalize_r1d.py`);
  - `consolidate_labels.py`, `compare_pilot*.py`, `run_regression*.py`;
  - `enriquecer_v1.py`, `gerar_manifest.py`.

  No repo vivo elas falhariam pela ausência dos paths originais. Isso é esperado e não indica corrupção.
- **Verificação viva:** `verify_relocation.py --ledger PROTECTED545_RELOCATION/ledger/P545_RELOCATION_LEDGER.json --bind REPO_ROOT=… --bind P545_ARCHIVE=C:\LMA\p545e\20260928`.
- **Rollback:** eventos ROLLBACK append-only, rename inverso e reverificação do inventário e dos IDX.
- **2E6:** nunca executar `montar_sd_teste_relations_v2.py` no repo vivo.

## Aviso

Com `core.autocrlf=true` e sem regra no `.gitattributes` para `PROTECTED545_RELOCATION/ledger/**`, um checkout novo gravaria o ledger em CRLF. A validade dele é semântica (cadeia de hash sobre JSON canônico, então continua válido), mas o SHA-256 do arquivo mudaria. A recomendação é adicionar uma regra `-text` numa etapa futura; o `.gitattributes` não foi alterado nesta missão.

## Próximo bloqueio da limpeza

Restam 26 candidatos protected545 na raiz, com 31,5 MB, todos fora desta autorização:

| Grupo | Candidatos | Tamanho | O que falta |
|---|---:|---:|---|
| P545 + D01 | 12 | 14,3 MB | Decidir o caminho oficial do D01: visão legada ou lista explícita numa versão não congelada |
| Múltiplos bloqueios | 2 | 1,0 MB | 2E5/2E6, só em lote conjunto com 2E41 |
| Ativos | 12 | 16,1 MB | Referenciados por paths literais no código congelado ou versionados no Git |

Continuam também na raiz os 7 EXTRACT da ONDA 2R (23,7 MB, precisam de cópia fria das capturas primárias), o hold 2E4 e 2E41.
