# P545A — Prova de realocação do protected545

**Resultado: PROVA DE REALOCAÇÃO VALIDADA.** Nenhum dos 55 candidatos foi movido, renomeado ou apagado. `INTEGRITY_BEFORE.json` não foi alterado (SHA-256 `a319f0ea917b0e6c00e037ba5b7a5c97b351d1b0af00b79862ae98db7cfd91c2`).

- **HEAD:** `9e7ae67f8f9ae49a618f1cf14953187b36c4dc92` (`post-wave2-execution-2026-09-28`).
- **Baseline, antes e depois:**

  | Verificação | Resultado |
  |---|---|
  | protected545 | 545/545 |
  | IDX | 130/130 |
  | V2 congelada | 281/281 |
  | ENRIQUECIDO_V1 | 7/7 |
  | Registry / Lock / Resolver | PASS |

## 1. Números

| Classe | Candidatos | Bytes | Arquivos |
|---|---:|---:|---:|
| A. READY_AFTER_P545_RELOCATION_PROOF | 16 | 32.464.454 | 121 |
| B. READY_AFTER_P545_PLUS_DYNAMIC_DISCOVERY_FIX | 12 | 14.310.109 | 156 |
| C. READY_AFTER_P545_PLUS_IDX_PROOF | 13 | 2.824.982.073 | 22.152 |
| D. READY_AFTER_MULTIPLE_FIXES | 2 | 1.025.149 | 45 |
| E. STILL_ACTIVE_KEEP | 12 | 16.127.518 | 124 |
| F. MANUAL_REVIEW_REQUIRED | 0 | 0 | 0 |
| **Total com protected545** | **55** | **2.888.909.303** | |

- **P545-only:** 16 candidatos, 32.464.454 bytes.
- **P545 + outros bloqueios:** 39 candidatos, 2.856.444.849 bytes.
- **Movíveis depois de todas as correções (A–D):** **43 candidatos, 2.872.781.785 bytes (99,44 % do volume protected545).**
- **Movíveis só com a prova de realocação + a prova IDX (A + C, sem mexer no D01):** 29 candidatos, 2.857.446.527 bytes.
- **Espaço físico liberado se o archive ficar no mesmo volume C::** **0**.

## 2. Como a prova atual funciona (código)

**Prova original.**

- Arquivo: `LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/INTEGRITY_BEFORE.json`, schema `2.0.phase0`.
- Estrutura: `files[545] = {path, sha256, bytes}`.
- Os paths são relativos à raiz do repositório, em POSIX; não há path absoluto.
- Nenhum script do repositório cria esse arquivo (ele veio da fase 0). Só existem leitores.

**Verificação.**

- **Função:** `05_COMPILADOR/r1d_support.py:36-45` → `integrity()` compara `file_hash(ROOT.parent/r['path']) != r['sha256']`.
- **Identidade usada pelo código:** path + sha256. O tamanho não é verificado.
- **Ausência física:** `FileNotFoundError`. Falha por exceção, sem status explícito.
- **Alias ou relocação:** não existe nenhum mecanismo.
- **Encapsulamento:** `r1d1_pipeline.py:29-35` envolve a função. Estes gates exigem `integrity()['passed']`:
  - `r1d1_pipeline.py:55,128,156`;
  - `gate_r1d.py:20`;
  - `run_regression_r1d.py:30`;
  - `runner_integral_r1d.py:21`;
  - `finalize_r1d.py:12`.

**Consequência central.** `r1d_support.py`, `r1d1_pipeline.py`, `consolidate_labels.py`, `compare_pilot.py`, `run_regression_r1d.py` e `prepare_expansion.py` pertencem ao conjunto **congelado V2 (281)** e não podem ser editados. Depois de qualquer move de um membro protected545, a linha R1D/R1D1 **não pode ser reexecutada no repositório vivo**.

A solução adotada não edita nada congelado:

- **Verificação viva:** verificador derivado (prova original + ledger).
- **Reexecução legada:** sobre uma **visão reconstruída** do layout original, gerada pelo ledger. A prova de sandbox validou esse caminho.

## 3. Mecanismo implementado (`PROTECTED545_RELOCATION/`)

| Arquivo | Função |
|---|---|
| `schemas/protected545-relocation-ledger.schema.json` | Schema do ledger |
| `relocation_ledger.py` | `occurrence_id`, `append_event`, cadeia de hash |
| `verify_relocation.py` | Verificador derivado (CLI) |
| `materialize_legacy_view.py` | Reconstrói o layout original para ferramentas congeladas |
| `sandbox_proof.py` | Prova completa em sandbox externo |
| `tests/test_verify_relocation.py` | 23 testes |

**Identidade.**

- `occurrence_id = "p545-" + sha256("INTEGRITY_BEFORE\0" + path + "\0" + sha256 + "\0" + bytes)[:24]`.
- Um SHA igual **não** identifica a ocorrência: dois arquivos idênticos em paths diferentes são ocorrências distintas.
- O evento carrega `original{path, sha256, size}`, conferido contra a prova original.

**Evento (append-only):**

- `seq`, `event_type` (RELOCATE ou ROLLBACK), `occurrence_id`, `original`;
- `from_location`, `to_location` (`root_id` + path relativo);
- `post_move_sha256`, `post_move_size`, `byte_identity_verified`;
- `reason`, `source_manifest`;
- `batch{batch_id, directory_from, directory_to, directory_inventory_sha256}`;
- `prev_event_hash`, `event_hash`.

**Proteção do ledger.**

- `head{count, event_hash}` mais uma âncora externa (commit/tag) detectam adulteração e truncamento.
- A→B→C fica registrado como dois eventos; a lineage é preservada.
- ROLLBACK é um novo evento que volta ao local anterior, sem apagar nada.

**Status por ocorrência:**

| Status | Significado |
|---|---|
| `ORIGINAL_PATH_PRESENT` | Arquivo no path original |
| `VALID_RELOCATION` | Realocação válida |
| `MISSING` | Arquivo ausente |
| `HASH_MISMATCH` | Hash ou tamanho diferente |
| `AMBIGUOUS_RELOCATION` | Ramificação, cópia remanescente ou colisão casefold/NFC |
| `INVALID_LINEAGE` | Path errado, ciclo, rollback inválido, ocorrência errada ou path inseguro |

Qualquer corrupção do ledger ou da prova original gera FAIL global (fail-closed).

**Execução no repositório real, sem ledger:** PASS, com 545 `ORIGINAL_PATH_PRESENT`.

## 4. Prova em sandbox (`CLEANUP_AUDIT/P545_SANDBOX_PROOF.json`)

- **Sandbox:** `C:\GitHub_LEX_MACHINA_P545_TEMP\p545a-2026-09-28-r2`. A execução anterior `…-28` foi preservada.
- **Conteúdo:** cópia da prova original e dos 545 membros (69 MB).
- **Movidos dentro do sandbox:** três diretórios representativos com 14 membros:
  - `LEX_MACHINA_REFERENCIAS_CF_J5` (JSON);
  - `LEX_MACHINA_JURIS_CF_J2` (IDX);
  - `firmware/LEX_MACHINA_v7.11.0_JURIS_CF_PILOTO` (firmware e PNG).

| Etapa | Verificador derivado | Verificador legado |
|---|---|---|
| Antes | PASS: 545 PRESENT | PASS |
| Depois do move (identidade de bytes 3/3 diretórios) | PASS: 531 PRESENT + 14 VALID_RELOCATION | **FAIL** (FileNotFoundError), como esperado |
| 2ª geração (J2: A→B→C) + ROLLBACK (CF_J5: A→B→A) | PASS: 537 + 8 | — |
| Visão legada reconstruída (545 cópias verificadas) | — | **PASS** |

**Testes negativos (11/11 falharam explicitamente; o estado foi restaurado e verificado depois de cada um):**

| # | Cenário | Resultado |
|---:|---|---|
| 1 | Destino faltando | MISSING |
| 2 | Hash alterado | HASH_MISMATCH / SHA256_MISMATCH |
| 3 | Tamanho alterado | HASH_MISMATCH / SIZE_MISMATCH |
| 4 | Ledger sem a ocorrência | MISSING |
| 5 | Dois destinos | AMBIGUOUS_RELOCATION / AMBIGUOUS_BRANCH |
| 6 | Ciclo | INVALID_LINEAGE / CYCLE |
| 7 | Path errado | INVALID_LINEAGE / BROKEN_LINEAGE |
| 8 | Ocorrência errada | INVALID_LINEAGE / WRONG_OCCURRENCE |
| 9 | Colisão casefold | AMBIGUOUS_RELOCATION / LOCATION_COLLISION_CASEFOLD_NFC |
| 10 | Ledger adulterado | LEDGER_CORRUPT |
| 11 | Ledger truncado com head reescrito | LEDGER_TRUNCATED_OR_CORRUPT (âncora) |

Os testes unitários (23/23) cobrem também path traversal, NFC, ocorrência desconhecida, cópia remanescente no original e prova original alterada.

## 5. Descoberta dinâmica

| Ponto | Código | Raiz / padrão | Candidatos selecionáveis | Natureza | Correção mínima |
|---|---|---|---|---|---|
| **D01** | `06_BENCHMARKS/consolidate_labels.py:56` (congelado) | `REPO.glob('LEX_MACHINA_REFERENCIAS*')` + `rglob('*.json')` + marcadores; SRCnnn pela ordem | **20** pastas com 55 marcadores. Das 20, 8 já estão em E (ativas) e 12 formam a classe B | Operacional: reprodução do ledger de rótulos | Reexecutar só na visão legada; futuro: lista explícita ordenada das 55 fontes numa versão não congelada; archive **sempre fora do repo** |
| D01b | `consolidate_labels.py:82-93`, `compare_pilot*.py:20-27`, `run_regression*.py`, `r1d1_pipeline.py:20`, `runner_integral_r1d.py:50`, adaptador 69 | Paths literais | 10 pastas REFERENCIAS mais CF_SEGMENTADA_V2 | Operacional literal (congelado) | Manter (E) ou reexecutar na visão legada |
| **D02** | `09_CATALOGO_EXPANSAO_200/06_RELATORIOS/enriquecer_v1.py:28`; `08_MANIFEST/gerar_manifest.py:50,54` | `REPO.rglob('*.IDX')` e `REPO.rglob('*')` (mtime) | 15 pastas com IDX | Histórico: `baseline()` é one-shot e aborta; `gerar_manifest` não roda no replay; ambos são membros do Registry D05 (editar quebraria Registry PASS) | Não reexecutar no repo vivo; futuro: manifesto fechado das 130 ocorrências IDX resolvido pelo ledger |
| **D12** | `LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/montar_sd_teste_relations_v2.py:46,71,78,144` | `--pacote` (default absoluto para 2E41) + `iterdir`/`glob` EXT_*; `shutil.rmtree(SD_PRONTO)` | 2E41 (fora dos 55) e 2E6 (relativo ao script) | Ferramenta preservada, **destrutiva** sobre IDX protegidos | Nunca executar no repo vivo; mover 2E6 e 2E41 juntos |
| Outros | `updater/*.py` (auditar, construir_lexdata, implantar_sd, sanear), firmware `openNextFile` | `updater/saida`, `backup_sd`, SD | Nenhum dos 55 | — | — |

Das 34 pastas REFERENCIAS_V1, as que não têm marcador não afetam o D01: mover essas pastas não altera nenhuma saída.

## 6. IDX (15 candidatos entre os 55, 130 arquivos no total)

**Achados.**

- Nenhum IDX contém path absoluto do repositório.
- Os paths são relativos à raiz do SD (`/99_LEXDATA_ESP32_OFICIAL_V4_TESTE/...`, `/99_RELATIONS_V2/...`).
- Os offsets são em bytes: do TXT da norma (ARTIGOS/EXT_ARTIGOS) ou do índice irmão (JUR_LOOKUP → JURISPRUDENCIA.IDX; REL_LOOKUP → RELACOES.IDX).
- A ordem física só importa no SD (firmware).
- Offsets verificados dentro do próprio candidato: **100 % válidos**. São 12.637/12.637 em cada build do updater e 50.548/50.548 em `updater_stage2a_corrigida_v2`.

| Grupo | Candidatos | Classificação |
|---|---|---|
| Builds do updater (LEXDATA/INDICES_BINARIOS) | 2C, 2D, 2D2, 2D3, UPDATER_BACKUP_V1, UPDATER_RELATIONS_V2, UPDATER_RELATIONS_V2_ETAPA2A, updater_stage2a_corrigida_v2 | **IDX_RELOCATABLE_WITH_PARENT** |
| JURIS CF | J2, J2_5, J3, J4, J4_6 | **IDX_RELOCATABLE_WITH_PARENT** |
| Relations | 2E5, 2E6 | **IDX_REQUIRES_FURTHER_PROOF**: EXT_* aponta textos que só existem no pacote 2E41 |

Nenhum grupo é IDX_REQUIRES_REBUILD ou IDX_ACTIVE_BLOCKER. A condição é mover o diretório **inteiro** (nunca só o IDX) e registrar cada IDX protected545 no ledger.

## 7. STILL_ACTIVE_KEEP (12, 16,1 MB)

| Candidato | Por que fica |
|---|---|
| `CF_SEGMENTADA_V2` | `prepare_expansion.py:17`, testes V2, adaptador 69 |
| `TESTE_COMPLETO_ALPHA3_V1` | `r1d1_pipeline.py:20`, `run_regression*.py`, `runner_integral_r1d.py:50` |
| `BENCHMARK_69_HUMANO_V1`, `VALIDACAO_V14_ALPHA3`, `AUDITORIA_ASTRA_V1` | `compare_pilot*.py`, `consolidate_labels.py` (groupdefs) |
| `PREPARACAO_V14_ALPHA2` | `consolidate_labels.py` (groupdefs) |
| `BENCHMARK_CF_V2` | `consolidate_labels.py` (groupdefs), adaptador 69 |
| `ENGINE_V1_2`, `ENGINE_V1_3_2`, `CATALOGO_LOTE_45_V2` | `adaptar_catalogo_69.py` e testes |
| `firmware/v7.12.0` | Baseline física, arquivos tracked |
| `firmware/LEX MAQUINA INO 2` | Arquivos tracked |

## 8. Plano P545E (não executado)

| Lote | Classe | Candidatos | Bytes |
|---|---|---:|---:|
| P545E_1 | Somente protected545 (12 REFERENCIAS sem marcador + 3 firmware antigos + EXPERIMENTO_24_VS_69) | 16 | 32.464.454 |
| P545E_2 | + D01 | 12 | 14.310.109 |
| P545E_3 | + IDX relocável com o pai | 13 | 2.824.982.073 |
| P545E_4 | Múltiplos (2E5, 2E6; em lote conjunto com 2E41) | 2 | 1.025.149 |

**Pré-condições obrigatórias:**

1. **Aprovação humana explícita** da política "PROVA ORIGINAL + PROVA DE REALOCAÇÃO". O `PROTECTED545_POLICY.md` hoje proíbe mover sem nova autorização.
2. **Archive root fora do repositório e com prefixo curto** (ex.: `C:\LMA\p545e`), ou ferramentas com suporte a paths longos. Com o prefixo da ONDA 2E (44 caracteres), 6 candidatos passariam de 260 caracteres: 2C, 2D, 2D2, BACKUP_V1, RELATIONS_V2_ETAPA2A (283) e stage2a_corrigida (287).
3. **Ledger real** com um RELOCATE por membro protected545 e um `batch` com o hash do inventário do diretório. Ele deve ser versionado e ancorado em commit/tag a cada lote.
4. **Gates por lote:**
   - `verify_relocation` PASS;
   - `materialize_legacy_view` + verificação legada PASS;
   - IDX 130/130 via ledger;
   - V2 281/281;
   - Registry, Lock e Resolver PASS.
5. **P545E_2** só depois de decidir o caminho oficial do D01: visão legada ou lista explícita numa versão não congelada.
6. **P545E_4** só junto com 2E41, sem executar o montador.
7. **Rollback:** evento ROLLBACK de `archive_path` para o path original exato, com hash e inventário conferidos.

**Observações:**

- LEX_MACHINA_JURIS_CF_J4 é o corpus da baseline física validada. Mover preserva o conteúdo, mas convém confirmar.
- UPDATER_BACKUP_V1 contém um `.venv` de 139 MB e 96 nomes não-ASCII.
