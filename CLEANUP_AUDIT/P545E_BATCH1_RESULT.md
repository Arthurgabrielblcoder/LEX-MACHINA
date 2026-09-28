# P545E_1 — Realocação protected545 (lote 1: P545-only)

**Status: COMPLETED.** 16/16 candidatos movidos com identidade de bytes verificada.

| Item | Valor |
|---|---|
| Autorização | `PROTECTED545_RELOCATION/PROTECTED545_RELOCATION_POLICY_V2.md` (OPERATOR_APPROVAL_RECORDED) |
| Commit/tag âncora pré-execução | `d114f68aed7828a98df127cdb06976de4255f2ef` / `pre-protected545-relocation-2026-09-28` |
| Archive root | `C:\LMA\p545e\20260928`, com o mesmo comprimento da raiz do repo (21 caracteres) |
| Maior path de destino | 127 caracteres |
| `ARCHIVE_IS_BACKUP` | false (mesmo volume C:) |
| `DISK_SPACE_FREED_BY_MOVE` | 0 |
| Ledger | `PROTECTED545_RELOCATION/ledger/P545_RELOCATION_LEDGER.json` |
| Head do ledger | count 121, event_hash `9b872e44d6e95cc686f46937d769cca6c69b43d11ac6ae2469b6779493dccb27` |
| SHA-256 do ledger | `a79d1f1a9f80e372f1db538958d6807a1f234b794aaf3dc30530163bfb96d110` |
| Executor (scratch, não versionado) | `p545e_exec.py`, SHA-256 `b772228696898bb95ce5b0cf24814c755cfb6b247c9c54062637da961c74771e`; usa o framework commitado sem modificação |

**Seleção.** Classe `READY_AFTER_P545_RELOCATION_PROOF` em `CLEANUP_AUDIT/P545_RELOCATION_ANALYSIS.json`: 16 candidatos, 32.464.454 bytes. Nenhum tem ACTIVE_DEPENDENCY, D01 ou D12.

## Movimentos

Todos os candidatos passaram nas pré-checagens:

- zero arquivos tracked;
- zero reparse points;
- zero colisões casefold/NFC;
- destino inexistente;
- inventário igual ao da análise.

A lista completa de verificações está na seção **Verificação**.

| ID | Candidato | Arquivos | Bytes | Membros P545 | Hash do inventário (pré = pós) | Pós | Maior path destino |
|---|---|---:|---:|---:|---|---|---:|
| W2R-062 | `LEX_MACHINA_REFERENCIAS_ENGINE_V1_4_ALPHA3` | 11 | 35.676 | 11 | 44298f688c521b9c… | igual | 123 |
| W2R-061 | `LEX_MACHINA_REFERENCIAS_ENGINE_V1_4_ALPHA2` | 7 | 45.079 | 7 | d440ba700704d5ad… | igual | 110 |
| W2R-060 | `LEX_MACHINA_REFERENCIAS_ENGINE_V1_4_ALPHA` | 7 | 52.129 | 7 | a362e28447c18395… | igual | 108 |
| W2R-051 | `LEX_MACHINA_REFERENCIAS_CF_J5_1` | 2 | 81.566 | 2 | 0ce15825b029b88d… | igual | 89 |
| W2R-050 | `LEX_MACHINA_REFERENCIAS_CF_J5` | 6 | 100.385 | 6 | e963f94d2d6906f9… | igual | 80 |
| W2R-046 | `LEX_MACHINA_REFERENCIAS_CATALOGO_EXPANSAO_V1` | 7 | 127.575 | 7 | f08c7de05833026f… | igual | 103 |
| W2R-069 | `LEX_MACHINA_REFERENCIAS_VALIDACAO_EXTERNA_R7_V1` | 5 | 154.331 | 5 | 3eb25a4fa71fad2f… | igual | 105 |
| W2R-041 | `LEX_MACHINA_REFERENCIAS_AUDITORIA_CONTRATO_ENGINE_V1` | 10 | 162.521 | 10 | 0b85bda7b716eb7a… | igual | 126 |
| W2R-042 | `LEX_MACHINA_REFERENCIAS_AVALIACAO_J5_LOTE45_V1` | 8 | 165.113 | 8 | 60891746eb2e8115… | igual | 115 |
| W2R-053 | `LEX_MACHINA_REFERENCIAS_DIAGNOSTICO_NUCLEOS_V1` | 8 | 238.381 | 8 | 5a2d9bf3d602e313… | igual | 127 |
| W2R-047 | `LEX_MACHINA_REFERENCIAS_CATALOGO_LOTE_45_V1` | 8 | 316.045 | 8 | a18d8f2002af0471… | igual | 98 |
| W2R-067 | `LEX_MACHINA_REFERENCIAS_TEMAS_LOTE45_V1` | 9 | 408.005 | 9 | c6313d2b4f762dd6… | igual | 110 |
| W2R-078 | `firmware/LEX_MACHINA_BACKUP_POS_CODEX_16-09` | 4 | 831.728 | 4 | ea592e08c6278b39… | igual | 100 |
| W2R-079 | `firmware/LEX_MACHINA_v7.11.0_JURIS_CF_PILOTO` | 6 | 882.401 | 6 | f96796a6a55bd11d… | igual | 106 |
| W2R-080 | `firmware/LEX_MACHINA_v7.11.1_JURIS_CF_PILOTO` | 7 | 890.116 | 7 | 9b55277000fe3b36… | igual | 106 |
| W2R-063 | `LEX_MACHINA_REFERENCIAS_EXPERIMENTO_24_VS_69_V1` | 16 | 27.973.403 | 16 | 3b83bf0e87f1e00b… | igual | 104 |

**Totais:** 16 candidatos, 121 arquivos, 32.464.454 bytes, **121 ocorrências protected545 realocadas** (121 eventos RELOCATE, seq 1–121). Os hashes completos, pré e pós, estão no JSON.

## Verificação (antes do move → depois do move)

| Verificação | Antes | Depois |
|---|---|---|
| Verificador derivado (repo vivo) | PASS: 545 ORIGINAL_PATH_PRESENT | **PASS: 424 ORIGINAL_PATH_PRESENT + 121 VALID_RELOCATION**; MISSING, HASH_MISMATCH, AMBIGUOUS e INVALID_LINEAGE = 0 |
| IDX (ocorrências protected545) | 130/130 | 130/130 (nenhum IDX neste lote) |
| Hash de `INTEGRITY_BEFORE.json` | `a319f0ea…c91c2` | inalterado |
| Visão legada `C:\LMA\lv\batch1-post` | — | 545/545 reconstruídos (121 vindos do archive) |
| `r1d_support.integrity()` congelado sobre a visão | passed (162 + 545 + holdout) | **passed** (162 + 545 + holdout) |
| V2 281 (vivo / visão) | 281/281 | 281/281 / 281/281 |
| ENRIQUECIDO_V1 | 7/7 | 7/7 |
| Registry / Lock / Resolver | PASS / PASS / PASS | PASS / PASS / PASS |
| Seleção D01 (55 marcadores, hash `0a1a32ba…`) | igual | **igual** (nenhum candidato do lote tinha marcador) |
| 26 não autorizados + 2E41 | presentes | presentes |
| Git | tracked limpo, staging vazio | tracked limpo, staging vazio |

No repo vivo, `r1d_support.integrity()` agora falha por ausência dos paths originais. Isso é **esperado** (política V2, regra 7) e não é corrupção. As ferramentas congeladas rodam somente sobre a visão legada (`HISTORICAL_TOOL_REQUIRES_LEGACY_VIEW`).

## Rollback

Para cada candidato: `rollback_from = C:\LMA\p545e\20260928\<path>` e `rollback_to = C:\GitHub\LEX-MACHINA\<path>`, com `rollback_possible = true`.

O rollback é um novo evento ROLLBACK por ocorrência no ledger (append-only), seguido do rename inverso e de uma nova verificação de inventário. Nenhum rollback foi executado.
