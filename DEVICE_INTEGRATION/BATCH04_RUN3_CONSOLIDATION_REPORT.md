# BATCH04 + RUN3 — consolidação final pré-implantação

**Status:** `BATCH04_RUN3_CONSOLIDATION_READY — AGUARDANDO_REVISAO_ANTES_DA_IMPLANTACAO_FISICA`

Nesta missão nada foi alterado no ESP32 físico nem no SD físico. Sem commit, sem tag e sem push.

## 1. Baseline

- **Performance (física):** tag `lex-device-v1-performance-approved-2026-10-03` = `6d0194b8ba82f0612ca73aa75a4377fa5b2b635a` (= HEAD).
- **Legado:** a tag `lex-device-v1-physical-approved-2026-10-01` (`2568999…`) continua intacta.

## 2. Auditoria do worktree (antes do build)

| Classe | Itens |
|---|---|
| BASELINE_ALREADY_COMMITTED | firmware, testes e ferramentas da baseline de performance (nada pendente nessa área) |
| RUN3_EXPECTED | `LEGAL_TARGET_ID/reference_engine.py`, `engine_config.json`, `tests/test_reference_engine.py`, `build_export_run3.py`, `tests/test_reference_run3.py`, `derived/CF88_LINK_EXCLUSIONS.json`, `derived/CF88_WORK_REFERENCE_ADDITIONS.json`, `derived/export_test/run2/`, `derived/export_test/run3/`, `REFERENCE_REGISTRY/WORK_REGISTRY_V2.json`, `REFERENCE_COVERAGE_AUDIT/` (entradas e auditoria do RUN3), `DEVICE_INTEGRATION/tools/build_ref_detail_header.py`, `tools/build_sd_staging.py`, `.gitignore` (staging RUN3) |
| BATCH04_EXPECTED | `ENTENDA_ENGINE/apply_batch_review.py`, `production_batch.py`, `derived/production_batch_04/`, `tests/test_production_batch_04.py` |
| TEST_FIX_EXPECTED | `DEVICE_INTEGRATION/tests/test_reference_run3_device.py` (referência à tag do baseline legado) |
| UNRELATED (não absorvidos) | `CF_SEGMENTADA_V2/`, `LEX_MACHINA_REFERENCIAS_*`, `LEX-MACHINAETAPA_*`, `LEX-MACHINA_ETAPA_2E6_SD_TESTE/`, `LEX_MACHINA_JURIS_CF_J1/`, `CLEANUP_AUDIT/*.json`, `updater/backup_sd/`, `firmware/LEX MAQUINA INO 2/*.zip` |

Sobre os itens UNRELATED:
- São dados-fonte e históricos locais, de 2026-09-13 a 2026-09-29, anteriores à baseline.
- Alguns (`CF_SEGMENTADA_V2`, `LEX_MACHINA_REFERENCIAS_V2`) já eram lidos pelo engine aprovado do RUN1.
- Nenhum foi modificado, e a consolidação não depende de nenhum deles.
- **Não contaminam.**

**Mudanças inesperadas:** NÃO.

## 3. ENTENDA

**Batch04:**
- 57/57 ativas `HUMAN_APPROVED_T1`, 0 pendentes, 0 obsoletas.
- Escopo: CF88 arts. 25–36, incluindo o 29-A.
- Aprovação por rodadas registradas:
  - `CF88_ARTS_25_28_ROUND_1`
  - `CF88_ART26_IV_EDITORIAL_CLEANUP`
  - `CF88_ARTS_29_31_ROUND_2`
  - `CF88_ARTS_32_36_ROUND_3`
  - mais as duas limpezas desta missão
- `APPROVAL_METHOD = ASSISTED_RISK_BASED_HUMAN_REVIEW`, `REVIEWER_DECISION = ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW`.

**Total final (calculado do corpus real): 220**
- 154 explicações sequenciais dos arts. 1–24 (Batches 01–03).
- 9 pilotos.
- 57 do Batch04.
- Sem sobreposição: nenhum piloto cai nos arts. 25–36. Bate com os 220 esperados.
- O lookup tem 362 linhas porque inclui as entradas `COVERED_BY_BLOCK`.

**Limpezas editoriais mínimas** (`EDITORIAL_CLEANUP_NO_SEMANTIC_CHANGE`, só PALAVRAS DIFÍCEIS; mesmo mecanismo de rodada registrada do art. 26 IV):

| Artigo | Antes | Depois | Versão | Evidência |
|---|---|---|---|---|
| Art. 34 (*Intervenção federal*) | "…a União **suspende** temporariamente a autonomia de um Estado ou do Distrito Federal." | "…a União **restringe** temporariamente a autonomia de um Estado ou do Distrito Federal." (coerente com o texto aprovado) | v2 → v3 | `ART34_GLOSSARY_CLEANUP_REVIEW_SPEC.json` / `_DECISIONS.json`, `BATCH_04_DRAFTS_PRE_ART34_CLEANUP.json` → `BATCH_04_DRAFTS_ART34_CLEANUP.json` |
| Art. 35 (*Intervenção estadual*), autorização adicional | "…o Estado **suspende** temporariamente a autonomia de um Município." | "…o Estado **restringe** temporariamente a autonomia do Município, nos limites necessários à intervenção." | v1 → v2 | `ART35_GLOSSARY_CLEANUP_REVIEW_SPEC.json` / `_DECISIONS.json`, `BATCH_04_DRAFTS_PRE_ART35_CLEANUP.json` → `BATCH_04_DRAFTS_ART35_CLEANUP.json` |

Em ambos o texto principal aprovado ficou inalterado (teste compara todas as seções exceto `palavras_dificeis`). Não sobra nenhum "suspende temporariamente" no lote.

**Linhas do corpus `CF88_BATCH_04.entenda.jsonl`:** 79 → 81.
- **2 linhas novas:** art. 34 v3 e art. 35 v2.
- **3 linhas antigas com mudança só de `status`/`superseded_by`:**
  - art. 34 v1: ponteiro passa a apontar para v3;
  - art. 34 v2: ACTIVE → RETIRED;
  - art. 35 v1: ACTIVE → RETIRED.
- **76 linhas byte-identical.**

**Artefatos editoriais alterados no Batch04:**
- `BATCH_04_DRAFTS.json`
- `BATCH_SPEC.json` (2 entradas novas em `round_approvals`)
- `CF88_BATCH_04.entenda.jsonl`
- derivados regenerados: `REVIEW_BATCH_04.md`, `SELECTION_REPORT.json`, `index/*` (3)

**Novos:** 8 arquivos de evidência (2 specs, 2 decisões, 4 snapshots de rascunho).

**Batches 01–03, pilotos, corpus principal:** inalterados, sem diff no git. No payload do staging, **as 163 explicações anteriores são byte-identical** às do SD físico aprovado (teste por registro).

**Históricos/revogados:** art. 28 parágrafo único não é target do runtime, então não tem ENTENDA; art. 36 IV é `REVOKED`, sem ENTENDA nem camadas. Nenhum conteúdo histórico vira CURRENT. Os BLOCKs continuam resolvendo para a âncora: os arts. 29-A II–VI cobertos por 29-A I.

## 4. Reference Engine RUN3 (consumido, não regenerado)

O RUN3 confere com o `SHA256SUMS.txt` aprovado. RUN1 e RUN2 são byte-identical (`previous_runs` do manifesto e testes de reprodução do Reference Engine).

**Contagens** (recalculadas do `REF_PAYLOAD.IDX` do staging):

| Item | Valor |
|---|---|
| Total | 451 |
| Jurisprudências visíveis | 277 |
| Correlatas visíveis | 44 |
| WORK_REFERENCE | 122 (21 novas integradas) |
| Ocultas | 8 |
| Targets com WORK_REFERENCE | 63 |
| Artigos da CF | 33 |
| Targets do ADCT | 1 |

**Mantidos fora:**
- **Retidas:** *SOS Saúde / Sicko* → CF88.196 e *Pro Dia Nascer Feliz* → CF88.206.I continuam `APPROVED_PENDING_WORK_IDENTITY`.
- **Rejeitadas:** *Borgen* → CF88.76 e *Argentina, 1985* → CF88.142 continuam `REJECTED_EDITORIAL_WEAK_CONNECTION`.

**Exclusões preservadas:** Tema 113 × CF88.25 e Tema 756 × CF88.31 §3 estão ausentes do payload e listados em `excluded_links`.

**Lookups:**

| Arquivo | Linhas | Bytes | sha256 |
|---|---|---|---|
| REF_LOOKUP | 256 | 6.955 | `6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8` |
| REF_PAYLOAD | 451 | 68.075 | `24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea` |

**Header rico candidato:** `lex_ref_detail_data.h` do RUN3, `2ca5820a170a3b08ecfa869685d319d65eee5bc94ddf0bfa5854282acce9710b`.
- Foi regenerado duas vezes e saiu byte-identical ao aprovado.
- Tem 122 entradas, com as mesmas chaves `TARGET|WORK` e os mesmos títulos das 122 linhas WORK_REFERENCE CURRENT_VISIBLE do payload.
- Tipo, nota e textos ricos vêm do mesmo gerador aprovado, verificado pela regeneração idêntica.
- O sketch do repositório mantém o header da baseline (`08f8fbdf…`).

## 5. Staging candidato

`DEVICE_INTEGRATION/staging_sd_v1_batch04_run3_candidate/`, ignorado pelo Git como os demais stagings.
- **11 arquivos, 1.432.861 B** em `SD/99_LEX_V1`.
- `_host/` com diagnósticos e `STAGING_FILE_MANIFEST.json` (path, bytes, sha256, papel, origem).

| Arquivo | Bytes | sha256 | Igual ao SD físico |
|---|---|---|---|
| 00_SYS/LEXV1.VER | 588 | `6e713989…11f6` | não |
| 00_SYS/LEX_DEVICE_MANIFEST.json | 7.604 | `25fceb1e…6b9a` | não |
| 05_TEXT/CF88_RUNTIME.txt | 587.133 | `7ef82290…e42a` | **sim** |
| 10_TARGETS/CC2002_ARTICLE_SEARCH.IDX | 25.036 | `674c9971…3a68` (2.077 registros) | **sim** |
| 10_TARGETS/CF88_ARTICLE_SEARCH.IDX | 5.216 | `56e437a0…7fae` (424 registros) | **sim** |
| 10_TARGETS/CF88_TARGETS.IDX | 165.466 | `5eb2da36…b980` | não (flags) |
| 10_TARGETS/CF88_TEXT_MAP.IDX | 123.578 | `889f8200…6b96` | **sim** |
| 20_REFERENCES/REF_LOOKUP.IDX | 6.955 | `6d6c88d7…0ac8` | não (RUN3) |
| 20_REFERENCES/REF_PAYLOAD.IDX | 68.075 | `24b4f0d9…58ea` | não (RUN3) |
| 30_ENTENDA/ENTENDA_LOOKUP.IDX | 38.700 (362 linhas) | `3014442e2da813215fa701aa67006e37cc59945bc280f632fedf056165370d21` | não |
| 30_ENTENDA/ENTENDA_PAYLOAD.DAT | 404.510 | `4efa54788fc468d1355b6d7937b3bd88a7c8c88f5a4a0dd20760082238b1e516` | não |

- **Runtime:** CF88_RUNTIME (Lei Seca, CF e ADCT) e TEXT_MAP são byte-identical à baseline. **Runtime alterado: NÃO.**
- **Determinismo:** foram 3 montagens completas (o build e a verificação interna do script, a remontagem depois do art. 35 e mais uma de reverificação), além do teste de rebuild. Todas byte-identical.
- **Ferramenta:** `build_sd_staging.py` ganhou o perfil explícito `BATCH04_RUN3`. O build padrão continua reproduzindo o `staging_sd_v1` aprovado (testes de rebuild determinístico da baseline OK).

## 6. Firmware candidato (logs de benchmark desligados: `LEXV1_ARTSEARCH_LOG 0`, `LEX_SCROLL_PERF_LOG 0`)

**Fonte:** `backups/batch04_run3/src_candidate/LEX_MACHINA_DEVICE_V1_CANDIDATE/`. É idêntica ao sketch da baseline `6d0194b`, exceto pelo `lex_ref_detail_data.h` do RUN3.

| Build | Programa | RAM estática | Imagem | sha256 |
|---|---|---|---|---|
| flag 0 | 989.395 B | 124.452 B | 989.536 B | `3cc0a846132b3046e0ba82461d7270a8183ce441f5467f13bd132238040e3eed` |
| flag 1 baseline de performance (sem logs) | 1.084.259 B | 126.148 B | 1.084.400 B | `9ff1ffc0…d35d` |
| **flag 1 candidato** | **1.097.235 B** | **126.148 B** | **1.097.376 B** | **`d12c7fceafcb13b02f789269d6aaf2b7ed77f06be003c6f502b8b69aa01ee8f6`** (checksum e hash válidos) |

**Flag 1, delta contra a baseline:** **+12.976 B, todos em `.flash.rodata`** (347.004 → 359.980). Esses bytes são os metadados ricos das obras: o header da baseline tinha 101 (RUN1), o do RUN3 tem 122, ou seja, 21 obras novas.
- `.flash.text`: idêntico (594.636), sem mudança de código.
- `.dram0.data`/`.bss`: idênticos.
- Uso de flash: 83,7% do app0 (1.310.720 B).

**Dívida arquitetural registrada:** os metadados ricos de WORK_REFERENCE estão no firmware. Custam ~618 B por obra nova em rodata (12.976 B / 21). Sobram ~213 KB no app0, o equivalente a ~340 obras no mesmo ritmo. Ainda não compensa migrar para overlay no SD; vale reavaliar quando o app0 passar de 90% (~130 obras novas a mais).

**Flag 0:** mesmo tamanho e mesmas seções que o build do baseline legado aprovado. 72 bytes diferentes, de metadata de build (`__TIME__` e o sha do ELF). Comportamento legado preservado.

## 7. Testes (árvore operacional, todos os dados locais presentes)

| Suíte | PASS | SKIP_EXPECTED_MISSING_LOCAL_DATA | FAIL_REAL |
|---|---|---|---|
| DEVICE (todas) | **300** | 0 | 0 |
| ENTENDA (todas) | **97** | 0 | 0 |
| LEGAL_TARGET_ID (todas) | **65** | 0 | 0 |

Nomeadas:

| Suíte | Testes |
|---|---|
| Reference Engine (com RUN1 + RUN2 reproduction) | 20 |
| RUN3 engine | 14 |
| RUN3 DEVICE | 9 |
| Batch04 | 17 |
| **consolidação (`test_batch04_run3_consolidation.py`)** | **24** |
| indexed search | 20 |
| CC article index | 12 |
| landing | 18 |
| next occurrence | 16 |
| REPEAT_READY | 16 |
| thousands parser | 19 |
| bidirectional scroll | 25 |
| reader state machine | 10 |
| FD policy | 11 |
| layer routing | 9 |
| target sync | 14 |
| caput equivalence | 12 |
| rich references (UI refinement) | 10 |
| device integration (rebuild da baseline) | 14 |

**FAIL_REAL = 0.**

**Os 18 casos da consolidação:**
1. ENTENDA art. 25
2. ENTENDA art. 29-A, com BLOCK II–VI → I e "29" no teclado nunca virando 29-A
3. ENTENDA art. 34, com a limpeza, e art. 35
4. ENTENDA art. 36, com o 36 IV revogado e o 28 parágrafo único histórico
5. REF art. 37, sem herança para I, §1 e §6
6. REF art. 43 caput
7. REF art. 43 §2 IV
8. REF art. 62 (mais 201 I e 7 XXXIII)
9. REF art. 193 após busca
10. REF ADCT 68
11. art. 98 sem ref
12. art. 202 sem ref
13. CF5 → ADCT5 com REPEAT_READY
14. CC art. 2000 (offset 647.337)
15. parser 2.000 → 2000
16. scroll profundo no CC real (1º UP < 16 KiB, sem leitura byte a byte)
17. loader CF → CC → CF, mais a busca do 230
18. Temas 113/756 ausentes

**Também cobertos:**
- amostra forte dos arts. 25–36 (busca → pouso → ENTENDA → payload, sem target obsoleto);
- obras pendentes e rejeitadas fora;
- contagens do RUN3;
- staging com 11 arquivos;
- runtime e TEXT_MAP iguais;
- refs = RUN3;
- índices validados;
- 220 explicações com as 163 anteriores byte-identical;
- header = payload;
- fonte do firmware;
- rebuild determinístico.

**Ajustes de teste:** em `test_production_batch_04.py`, lista de RETIRED, cópia das decisões, exceção do art. 35 na rodada 3 e 2 testes novos para as limpezas.

## 8. Planos (não executados)

- `BATCH04_RUN3_SD_DIFF_PLAN.md`: 7 REPLACED, 4 UNCHANGED, 0 ADDED, 0 REMOVED. 1.060 arquivos legados fora de `/99_LEX_V1` intocados.
- `BATCH04_RUN3_PHYSICAL_DEPLOY_PLAN.md`: fases A–I, com rollback de SD e de app.

## 9. Pontos para a revisão

1. O staging e a fonte do firmware dependem de artefatos RUN3/Batch04 ainda **não versionados**. O commit deve vir depois da validação física e incluir a troca do `lex_ref_detail_data.h` no sketch.
2. `ENTENDA_SCOPE` passa a `CF88_ARTS_1_36_PLUS_APPROVED_PILOTS`. O firmware só lê `ENTENDA_COUNT` e o schema (3), sem mudança de contrato.
3. A tag de ENTENDA do Batch04 ainda não existe. O manifesto do pacote registra `ENTENDA_CF_PRODUCTION_BATCH_04 (round approvals, uncommitted)`.
