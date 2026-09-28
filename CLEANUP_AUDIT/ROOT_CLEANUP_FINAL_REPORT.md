# LEX MACHINA — Relatório final da limpeza da raiz

**Status: `LIMPEZA_RAIZ_FINALIZADA`.** A limpeza pesada da raiz está encerrada. O que permanece é intencional (ativo, canônico ou hold humano) ou depende de trabalho específico futuro.

## Resumo

| Métrica | Valor |
|---|---|
| **BEFORE** | Repo auditado em 2026-09-26, sem `.git`: 28.838 arquivos e **3.421.025.370 bytes**. Universo WAVE2: **81 candidatos**, 23.379 arquivos, **2.921.061.459 bytes** |
| **AFTER** | Repo atual, sem `.git`: 6.383 arquivos e **615.124.817 bytes** (−82,0 %). WAVE2 restante: **35 candidatos, 56.050.778 bytes** (−98,1 %) |
| **MOVED_FROM_ROOT** | 46 candidatos. ONDA 2E: 17. P545E: 29. São 43 entradas de topo e 3 subpastas de `firmware/` |
| **BYTES_RELOCATED** | **2.865.010.681** (ONDA 2E: 7.564.154; P545E: 2.857.446.527) em 22.550 arquivos |
| **PHYSICAL_DISK_SPACE_FREED** | **583.302 bytes**, somente pelos 22 `.pyc` da ONDA 1. As relocações ficaram no mesmo volume C: e liberaram 0 |
| **PROTECTED545_RELOCATED** | 230 ocorrências (VALID_RELOCATION) |
| **PROTECTED545_REMAINING** | 315 ocorrências no path original. Total 545; MISSING, HASH_MISMATCH, AMBIGUOUS e INVALID_LINEAGE = 0 |
| **WAVE2_CANDIDATES_REMAINING** | 35: 33 na raiz e 2 em `firmware/` |
| **TOP_LEVEL_DIRECTORIES_BEFORE** | 88 (medido antes da ONDA 2E) |
| **TOP_LEVEL_DIRECTORIES_AFTER** | **46**, incluindo o novo `PROTECTED545_RELOCATION/`, e 4 arquivos de topo |
| **REMAINING_BLOCKERS** | A: 12 · B: 12 · C: 3 · D: 1 · E: 7 · F: 1 (detalhes abaixo) |

O archive externo **não é exclusão física nem backup**. Ele está no mesmo disco:

| Local | Arquivos | Bytes |
|---|---:|---:|
| `C:\GitHub_LEX_MACHINA_ARCHIVE\2026-09-28-wave2` (ONDA 2E) | 277 | 7.564.154 |
| `C:\LMA\p545e\20260928` (P545E) | 22.273 | 2.857.446.527 |

Artefatos de verificação externos descartáveis, **não apagados**, somam cerca de 1,09 GB. A remoção fica a critério do operador:

| Local | Conteúdo | Tamanho |
|---|---|---:|
| `C:\LMA\lv` | Visões legadas | 742 MB |
| `C:\LMA\ct` | Clone de teste | 146 MB |
| `C:\GitHub_LEX_MACHINA_P545_TEMP` | Sandbox P545A | 206 MB |

Os sandboxes D05/SCA1B2 e o snapshot de segurança da ONDA 0 continuam preservados.

## Raiz operacional atual

Aproximadamente 559 MB.

| Área | Arquivos | Bytes |
|---|---:|---:|
| `updater` (inclui `.venv` de 139 MB e `saida`/`backup_sd`) | 4.282 | 460.582.794 |
| `CLEANUP_AUDIT` | 86 | 57.691.662 |
| `LEX_MACHINA_REFERENCIAS_V2` | 1.135 | 37.294.564 |
| `firmware` (sketch ativo + 2 históricos mantidos) | 21 | 2.660.045 |
| `ARTIFACT_REGISTRY`, `DATASET_LOCKS`, `SHADOW_RESOLVER`, `SHADOW_CONSUMER_ADAPTER`, `PROTECTED545_RELOCATION` | 30 | ≈2,0 MB |
| `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1`, `docs`, `sdcard` | 12 | ≈0,65 MB |

## O que permanece e por quê

| Categoria | Qtde | Bytes | Motivo |
|---|---:|---:|---|
| **A) ACTIVE / KEEP** | 12 | 16.127.518 | Lidos por path literal em código congelado ou ativo; ou firmware versionado no Git (baseline física v7.12.0, INO 2). São canônicos |
| **B) D01_DYNAMIC_DISCOVERY** | 12 | 14.310.109 | protected545 (156 membros) + marcadores selecionados por `consolidate_labels.py:56`. Mover renumeraria os SRCnnn. Depende de decidir o caminho oficial do D01 |
| **C) MULTIPLE_BLOCKER** | 3 | 1.865.964 | 2E5 e 2E6: protected545 + IDX ligados aos textos do pacote 2E41, e montador D12 destrutivo. 2E41: default absoluto do montador e alvo D12. Só em lote conjunto com prova adicional |
| **D) HUMAN_HOLD** | 1 | 49.357 | 2E4: tecnicamente pronto, mas há decisão humana anterior de não mover |
| **E) EXTRACT_PRIMARY_EVIDENCE** | 7 | 23.697.830 | Capturas oficiais e dado curado únicos, sem cópia Git/snapshot. Exigem cópia fria verificada antes de arquivar |
| **F) OTHER INTENTIONAL** | 1 | 0 | `LEX-MACHINAETAPA_2B`: diretório vazio fora do universo WAVE2 (NEW_CLEANUP_CANDIDATE); nenhuma ação sem decisão |

**Candidatos por categoria:**

- **A:**
  - `CF_SEGMENTADA_V2`;
  - `LEX_MACHINA_REFERENCIAS_AUDITORIA_ASTRA_V1`;
  - `LEX_MACHINA_REFERENCIAS_BENCHMARK_69_HUMANO_V1`;
  - `LEX_MACHINA_REFERENCIAS_BENCHMARK_CF_V2`;
  - `LEX_MACHINA_REFERENCIAS_CATALOGO_LOTE_45_V2`;
  - `LEX_MACHINA_REFERENCIAS_ENGINE_V1_2`;
  - `LEX_MACHINA_REFERENCIAS_ENGINE_V1_3_2`;
  - `LEX_MACHINA_REFERENCIAS_PREPARACAO_V14_ALPHA2`;
  - `LEX_MACHINA_REFERENCIAS_TESTE_COMPLETO_ALPHA3_V1`;
  - `LEX_MACHINA_REFERENCIAS_VALIDACAO_V14_ALPHA3`;
  - `firmware/LEX MAQUINA INO 2`;
  - `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA`.
- **B:**
  - `LEX_MACHINA_REFERENCIAS_AUDITORIA_CAUSAL_V132_V1`;
  - `AVALIACAO_J5_LOTE45_V2_FINAL`;
  - `CF_ENGINE_RUN_V1`;
  - `CF_REVISAO_ALTA_CONFIANCA_V1`;
  - `ENGINE_V1`, `ENGINE_V1_1`, `ENGINE_V1_3`, `ENGINE_V1_3_1`;
  - `FORCA_TEMA_LOTE45_V1_FINAL`;
  - `REFINAMENTO_R7_V2`;
  - `VALIDACAO_V14_ALPHA`, `VALIDACAO_V14_ALPHA2`.

  Todos com o prefixo `LEX_MACHINA_REFERENCIAS_`.
- **C:** `LEX-MACHINAETAPA_2E41`, `LEX-MACHINAETAPA_2E5`, `LEX-MACHINA_ETAPA_2E6_SD_TESTE`.
- **D:** `LEX-MACHINAETAPA_2E4`.
- **E:**
  - `LEX-MACHINAETAPA_2D4`, `2D5`, `2D6_1`, `2D6_4`, `2D7`, `2D8`;
  - `LEX_MACHINA_JURIS_CF_J1`.

## Pendência técnica corrigida: preservação do ledger

- **Ledger:** `PROTECTED545_RELOCATION/ledger/P545_RELOCATION_LEDGER.json`, com 230 eventos, head `4665bae6…36ae1` e SHA-256 `b1522733cddf42bda9239aef1d4fe00b7fa7273900c4243be9af9606bcf44b52`. O hash é idêntico antes e depois da edição do `.gitattributes`; o ledger não foi reescrito.
- **Regra exata acrescentada** ao final do `.gitattributes`, sem alterar nenhuma outra regra de fim de linha:

  ```
  PROTECTED545_RELOCATION/ledger/P545_RELOCATION_LEDGER.json -text
  ```

  O efeito foi `git check-attr text` = `unset`, com `i/lf w/lf attr/-text`.
- **Clone de teste** (`C:\LMA\ct\ledger-attr-test-1`, com `core.autocrlf=true` e `core.longpaths=true`):
  - **sem a regra**, o checkout gravou SHA-256 `4dc46a0d…ea91`: bytes alterados, o que confirma o risco;
  - **com a regra**, gravou `b1522733…4b52`: **BYTE_IDENTICAL = true**.

## Verificação final

| Verificação | Resultado |
|---|---|
| Testes do `PROTECTED545_RELOCATION` | 23/23 OK |
| Verificador derivado (âncora do head do ledger) | PASS: 315 PRESENT + 230 VALID_RELOCATION, 0 erros |
| Visão legada `C:\LMA\lv\finalize` | 545/545; `r1d_support.integrity()` congelado passed; V2 281/281 |
| V2 (vivo) | 281/281 |
| IDX (ocorrências protected545) | 130/130 |
| ENRIQUECIDO_V1 | 7/7 |
| Registry / Lock / Resolver | PASS / PASS / PASS |
| `INTEGRITY_BEFORE.json` | `a319f0ea…c91c2`, inalterado |
| Seleção D01 | inalterada (55 marcadores) |
| 26 não autorizados + 2E41 | presentes |

## Trilha da fase

| Etapa | Commit | Tag |
|---|---|---|
| ONDA 0 (segurança) | `f251cea` / `1dddc43` | `pre-cleanup-2026-09-26` |
| ONDA 1 (22 `.pyc`) | `53c419a` | `post-cleanup-wave1-2026-09-26` |
| WAVE2R / ONDA 2E (17 movidos) | `63947ad` / `9e7ae67` | `pre-wave2-execution-2026-09-28` / `post-wave2-execution-2026-09-28` |
| P545A + política V2 | `d114f68` | `pre-protected545-relocation-2026-09-28` |
| P545E lote 1 e lote IDX | `2afc997` / `a2192f5` | `protected545-relocation-batch1-2026-09-28` / `protected545-relocation-idx-batch-2026-09-28` |
| P545E resultado | `bdd9fc4` | `post-protected545-relocation-2026-09-28` |
| Finalização (este relatório + `.gitattributes`) | este commit | `root-cleanup-finalized-2026-09-28` |

## Trabalho futuro (fora desta fase)

- **D01:** decidir o caminho oficial de reexecução (visão legada ou lista explícita não congelada). Isso libera a categoria B.
- **2E5/2E6/2E41:** prova conjunta; nunca executar o montador no repo vivo.
- **EXTRACT:** cópia fria verificada das capturas primárias.
- **2E4:** reconfirmação humana.
- **Regra operacional permanente:** `HISTORICAL_TOOL_REQUIRES_LEGACY_VIEW`.
