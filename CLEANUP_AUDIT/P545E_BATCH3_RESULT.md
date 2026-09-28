# P545E_3 — Realocação protected545 com IDX relocável junto com o diretório pai

**Status: COMPLETED.** 13/13 candidatos movidos com identidade de bytes verificada; 109/109 IDX validados; nenhuma reconstrução de IDX necessária.

| Item | Valor |
|---|---|
| Seleção | `READY_AFTER_P545_PLUS_IDX_PROOF` e `IDX_RELOCATABLE_WITH_PARENT` em `CLEANUP_AUDIT/P545_RELOCATION_ANALYSIS.json`: 13 candidatos, 2.824.982.073 bytes. Nenhum com ACTIVE_DEPENDENCY, D01 ou D12. |
| Archive root | `C:\LMA\p545e\20260928`, com o mesmo comprimento da raiz do repo |
| Maior path de destino | 264 caracteres, idêntico ao maior path atual (`LongPathsEnabled = 1`) |
| `ARCHIVE_IS_BACKUP` | false |
| `DISK_SPACE_FREED_BY_MOVE` | 0 |
| Ledger | `PROTECTED545_RELOCATION/ledger/P545_RELOCATION_LEDGER.json` |
| Head do ledger | count 230, event_hash `4665bae677a9dd5bdfe8e4f04df537a48d1fce994dc01ab22222618dda436ae1` |
| SHA-256 do ledger | `b1522733cddf42bda9239aef1d4fe00b7fa7273900c4243be9af9606bcf44b52` |

**Append-only verificado:**

- header idêntico;
- eventos 1–121 (lote 1) byte-idênticos ao commit `2afc9976`;
- o evento 122 encadeia no head do lote 1;
- só existem eventos RELOCATE.

Os 109 eventos novos são os de seq 122–230.

O executor registrou `STOPPED` apenas porque o gate "tracked limpo" viu o ledger versionado com essas entradas novas. Não foi falha: todas as demais verificações passaram (detalhe no JSON, em `status_note`).

## Movimentos

Candidatos movidos um de cada vez, com inventário SHA-256 completo antes e depois de cada um e validação IDX antes e depois.

| ID | Candidato | Arquivos | Bytes | Membros P545 | IDX | Offsets válidos | Refs resolvidas | Hash do inventário (pré = pós) | Maior path |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| W2R-036 | `LEX_MACHINA_JURIS_CF_J3` | 35 | 40.864 | 2 | 2 | 35/35 | 0/0 (só URLs) | 468737fcdfd92fc5… | 117 |
| W2R-035 | `LEX_MACHINA_JURIS_CF_J2_5` | 13 | 260.073 | 2 | 2 | 35/35 | 0/0 | 9f163b41008cdd8f… | 82 |
| W2R-038 | `LEX_MACHINA_JURIS_CF_J4_6` | 229 | 279.831 | 2 | 2 | 178/178 | 0/0 | deb890736d206495… | 122 |
| W2R-034 | `LEX_MACHINA_JURIS_CF_J2` | 14 | 347.908 | 2 | 2 | 35/35 | 0/0 | 433bd8e0aac27021… | 90 |
| W2R-037 | `LEX_MACHINA_JURIS_CF_J4` | 84 | 7.436.773 | 2 | 2 | 178/178 | 0/0 | d47aa18951b5272b… | 91 |
| W2R-074 | `LEX_MACHINA_UPDATER_RELATIONS_V2` | 1.696 | 223.029.243 | 9 | 9 | 12.637/12.637 | 304/304 | c43a1311ca2fb711… | 236 |
| W2R-013 | `LEX-MACHINAETAPA_2D2` | 1.739 | 224.619.125 | 9 | 9 | 12.637/12.637 | 304/304 | 1150d4278681d93b… | 240 |
| W2R-003 | `LEX-MACHINAETAPA_2C` | 1.734 | 225.107.994 | 9 | 9 | 12.637/12.637 | 304/304 | 01eca792055effe6… | 239 |
| W2R-004 | `LEX-MACHINAETAPA_2D` | 1.736 | 225.551.763 | 9 | 9 | 12.637/12.637 | 304/304 | e11d84c8d9b3b19a… | 239 |
| W2R-075 | `LEX_MACHINA_UPDATER_RELATIONS_V2_ETAPA2A` | 1.704 | 252.414.298 | 9 | 9 | 12.637/12.637 | 304/304 | 2a55733194c9556d… | 260 |
| W2R-001 | `1- LEX-MACHINAETAPA_2D3` | 2.060 | 255.003.071 | 9 | 9 | 12.637/12.637 | 304/304 | f815dddc95215f90… | 227 |
| W2R-073 | `LEX_MACHINA_UPDATER_BACKUP_V1_17-09-2026` | 4.197 | 456.585.722 | 9 | 9 | 12.637/12.637 | 304/304 | 37b24f7a413e998d… | 244 |
| W2R-076 | `updater_stage2a_corrigida_v2` | 6.911 | 954.305.408 | 36 | 36 | 50.548/50.548 | 1.216/1.216 | 368c325dccc5ed32… | 264 |

**Totais:** 13 candidatos, 22.152 arquivos, 2.824.982.073 bytes, **109 ocorrências protected545 realocadas** (todas são IDX).

**Validação IDX, por IDX, antes e depois do move:**

- hash e tamanho do IDX iguais;
- textos e BIN referenciados resolvidos pelo mesmo path relativo interno, com o mesmo SHA-256;
- offsets ARTIGOS→TXT e JUR_LOOKUP/REL_LOOKUP→índice irmão 100 % válidos;
- nenhum path absoluto de repositório.

Resultado: **IDX_RELOCATABLE_WITH_PARENT_VALIDATED**.

## Verificação (antes do lote → depois do lote)

| Verificação | Antes | Depois |
|---|---|---|
| Verificador derivado | PASS: 424 PRESENT + 121 VALID | **PASS: 315 ORIGINAL_PATH_PRESENT + 230 VALID_RELOCATION**; MISSING, HASH_MISMATCH, AMBIGUOUS e INVALID_LINEAGE = 0 |
| IDX (ocorrências protected545 válidas) | 130/130 | 130/130 (109 realocados + 21 no local original) |
| Hash de `INTEGRITY_BEFORE.json` | `a319f0ea…c91c2` | inalterado (também na visão) |
| Visão legada `C:\LMA\lv\batch3-post` | 545/545 | 545/545 reconstruídos (230 vindos do archive) |
| `r1d_support.integrity()` congelado sobre a visão | passed | **passed** (162 V2 + 545 protegidos + holdout) |
| V2 281 (vivo / visão) | 281/281 | 281/281 / 281/281 |
| ENRIQUECIDO_V1 | 7/7 | 7/7 |
| Registry / Lock / Resolver | PASS | PASS |
| Seleção D01 (55 marcadores, `0a1a32ba…`) | igual | igual |
| 26 não autorizados + 2E41 | presentes | presentes |

**`HISTORICAL_TOOL_REQUIRES_LEGACY_VIEW`.** As ferramentas congeladas e as ferramentas D05 com descoberta histórica de IDX (`enriquecer_v1.py:28`, `gerar_manifest.py:50,54`) **não** devem ser executadas no repo vivo realocado; qualquer reprodução histórica usa a visão reconstruída. Nenhum script foi editado.

## Rollback

`C:\LMA\p545e\20260928\<path>` → `C:\GitHub\LEX-MACHINA\<path>` exato, com `rollback_possible = true` para os 13. O rollback é feito por eventos ROLLBACK acrescentados ao ledger, seguidos do rename inverso e da nova verificação do inventário e dos IDX. Nenhum rollback foi executado.
