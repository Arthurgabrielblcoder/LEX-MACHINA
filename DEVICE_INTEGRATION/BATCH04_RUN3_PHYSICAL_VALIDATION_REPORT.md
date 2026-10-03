# BATCH04 + RUN3 — relatório de validação física

**Status final (2026-10-03): BASELINE FÍSICA APROVADA.**
- `PHYSICAL_HUMAN_VALIDATION = APPROVED` (Arthur).
- Firmware **r2**, sha256 `3f0df29ee996e44399c78278a21895c7bdc661f22f79cb5b2bbcf853c5e2f5b5`.
- DIAG 33/33 PASS.
- SD Batch04 + RUN3 validado: 11/11.
- Commit: o que contém este relatório, tag anotada `lex-device-v1-batch04-run3-physical-approved-2026-10-03`.
- **Push: NÃO.**

**Autoridades:**
- SD: `DEVICE_INTEGRATION/staging_sd_v1_batch04_run3_candidate/SD/99_LEX_V1/`. É reconstruível de forma determinística por `tools/build_batch04_run3_candidate.py` e não foi regenerado nesta etapa.
- App aprovado: **r2**, `backups/batch04_run3/candidate_flag1_r2/candidate_app_batch04_run3_r2.bin` (seções 7–8).
- O r1 (`d12c7fce…e8f6`, seções 5–6) foi superado por causa dos casos fixos desatualizados do autodiagnóstico.

Ferramenta: `tools/deploy_batch04_run3_sd.py` (`pre` → `copy` → `verify`).

## 1. Identificação do cartão

| Item | Valor |
|---|---|
| Unidade | `D:` (Generic STORAGE DEVICE, USB, removível) |
| Sistema de arquivos | FAT32 |
| Tamanho | 31.902.400.512 B |
| Raiz | pastas da Lei Seca 1–43, `99_*`, `99_LEX_V1`, `LEX_MACHINA_INVENTARIO.txt` |

## 2. Estado antes (fase B — somente leitura)

- Manifesto completo: `backups/batch04_run3/sd_manifest_pre.json` (sha256 `15917c7b…b210`), **1.071 arquivos** (11 em `/99_LEX_V1` + 1.060 fora). `System Volume Information` excluída, como no manifesto anterior.
- Comparação com o estado físico conhecido (`backups/cc_index/sd_manifest_post.json`): **0 adicionados, 0 removidos, 0 alterados**.
- Os 4 UNCHANGED já eram iguais ao staging, e os 7 REPLACED eram diferentes, como previsto no diff plan.
- Backup verificável de **todo** o `/99_LEX_V1` (11 arquivos, bytes e sha256 conferidos) em `backups/batch04_run3/sd_pre/99_LEX_V1/`, com índice `backups/batch04_run3/sd_pre_backup_manifest.json`.

## 3. Cópia (fase C)

Foram copiados somente os 7 REPLACED, cada um com `fsync`, seguido de `Write-VolumeCache D`. Nenhum arquivo fora de `/99_LEX_V1` foi aberto para escrita. Os índices `CF88_ARTICLE_SEARCH.IDX` e `CC2002_ARTICLE_SEARCH.IDX` não foram tocados.

## 4. Readback e manifesto pós (fase D)

| Ação | Arquivo (`/99_LEX_V1/…`) | Antes: bytes | Antes: sha256 | Depois: bytes | Depois: sha256 | Staging |
|---|---|---|---|---|---|---|
| REPLACED | `00_SYS/LEXV1.VER` | 600 | `7c4b1a971b3e21788f49f819f5349b65bd4268a967e947181bc697edf5dce763` | 588 | `6e713989d5693e7aa59565a5c7ae73d39788acae7fd89cb5ea15b71bbec311f6` | MATCH |
| REPLACED | `00_SYS/LEX_DEVICE_MANIFEST.json` | 6.391 | `d2ab919f3e95de6e38e082993205be80ce8bddc122a880042140bb1dde000097` | 7.604 | `25fceb1e99759c9aa115f9ec323daf1802602ef3f09beebe30de4d2eb31a6b9a` | MATCH |
| UNCHANGED | `05_TEXT/CF88_RUNTIME.txt` | 587.133 | `7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a` | 587.133 | idem | MATCH |
| UNCHANGED | `10_TARGETS/CC2002_ARTICLE_SEARCH.IDX` | 25.036 | `674c9971925c29aaca9685fb2d0b9515fe87e4072d644858ea27495c327d3a68` | 25.036 | idem | MATCH |
| UNCHANGED | `10_TARGETS/CF88_ARTICLE_SEARCH.IDX` | 5.216 | `56e437a0c9cebb113c47f6a7b100ee64363c63207a647eca0456e86d6db27fae` | 5.216 | idem | MATCH |
| REPLACED | `10_TARGETS/CF88_TARGETS.IDX` | 165.466 | `36db8b871163262dacb97d5f4ecd36044ea70aa223f021f93a4dad2d91f888c1` | 165.466 | `5eb2da36ff01a7e5cc976e3b7d3eabc8999b95ae8d4b5932f752501af351b980` | MATCH |
| UNCHANGED | `10_TARGETS/CF88_TEXT_MAP.IDX` | 123.578 | `889f82002e82fb2b7d9165e6ce2a4e0dcb78d311432e268c341f1d0b1e436b96` | 123.578 | idem | MATCH |
| REPLACED | `20_REFERENCES/REF_LOOKUP.IDX` | 6.579 | `9665fb854fe5b91fc5a1aa640b6eb8270583e3c6414720e99f37f9608ccb3c12` | 6.955 | `6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8` | MATCH |
| REPLACED | `20_REFERENCES/REF_PAYLOAD.IDX` | 65.546 | `1c772c83b6cfe381ddb1674b73126dbf2fb6cf354fe16d708194cdad0de94228` | 68.075 | `24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea` | MATCH |
| REPLACED | `30_ENTENDA/ENTENDA_LOOKUP.IDX` | 30.462 | `93613275d4e0caf95ed58f1fe8e29cc90039d73ec9d302fc7ce0af2e5f816ddc` | 38.700 | `3014442e2da813215fa701aa67006e37cc59945bc280f632fedf056165370d21` | MATCH |
| REPLACED | `30_ENTENDA/ENTENDA_PAYLOAD.DAT` | 302.915 | `a7511b917f658fd411b0f46c241415e77148c9b1c8ed1780a797958fe640c029` | 404.510 | `4efa54788fc468d1355b6d7937b3bd88a7c8c88f5a4a0dd20760082238b1e516` | MATCH |

**Resultados:**
- **Readback:** 11/11 MATCH (bytes e sha256 contra o staging).
- **Manifesto pós:** `backups/batch04_run3/sd_manifest_post.json` (sha256 `9d059ddc…05ae`), 1.071 arquivos.
- **Diff pós × pré** (`sd_manifest_diff.json`): 7 substituídos, 4 idênticos, 0 adicionados, 0 removidos.
- **1.060 arquivos legacy fora de `/99_LEX_V1`:** intocados (bytes e sha256 iguais).
- **SD_VALIDATED.**

Ressalva: o readback foi feito pelo Windows logo após o flush. Parte das leituras pode ter vindo do cache do sistema. A confirmação definitiva da mídia é o boot no aparelho (`runtime hash CONFERE`, schema 3, `ENTENDA_COUNT=220`).

**Rollback do SD (sem Git):** copiar os 7 arquivos REPLACED de `backups/batch04_run3/sd_pre/99_LEX_V1/` para `D:\99_LEX_V1\` e conferir contra `sd_pre_backup_manifest.json`.

## 5. Flash app-only (fases G/H) — CONCLUÍDO

Arquivos em `backups/batch04_run3/flash/`.

**Pré-condições conferidas:**
- COM3 (CH343); ESP32-S3 (QFN56) v0.2; MAC `e0:72:a1:f4:fd:28`; flash 16 MB; PSRAM 8 MB.
- Partições em 0x8000 (sha256 `148b959c…53a1`, igual à sessão CC index): nvs 0x9000, otadata 0xE000, **app0 0x10000/0x140000**, app1 0x150000, spiffs 0x290000, coredump 0x3F0000.
- otadata `f94c5d78…17f0`, igual ao pós da sessão CC index.
- Backup do app0 instalado em `app0_prewrite.bin` (0x140000 B, sha256 `4c84aff2…0983`). A imagem contida nele é `candidate_app_cc_index.bin` (`f23e77cd…`).

**Gravação:**
- Candidato conferido: sha256 `d12c7fce…e8f6`.
- `write-flash 0x10000` com `--flash-mode/freq/size keep`: 1.097.376 B, "Hash of data verified".
- Somente app0 foi gravado; bootloader, partições, otadata, NVS, app1 e spiffs não foram tocados.

**Readback:**
- `readback_app0.bin` tem sha256 `d12c7fceafcb13b02f789269d6aaf2b7ed77f06be003c6f502b8b69aa01ee8f6` e `cmp` idêntico: **PHYSICAL_READBACK_MATCH = TRUE**.
- Partições e otadata relidas: inalteradas.

**Rollback do app:** `write-flash 0x10000 app0_prewrite.bin`.

## 6. Boot do r1 (fase I) — superado pelo r2

> **Correção (informada por Arthur):** os 4 boots abaixo foram feitos **sem o microSD instalado** no aparelho. `SD indisponivel` era esperado nessas condições e **não** indica falha de montagem, do slot ou do firmware. As hipóteses de diagnóstico abaixo ficam **anuladas**; registro mantido só como histórico.

### Histórico: boots sem cartão (inválidos para diagnóstico)

Log em `flash/session_serial.bin`, com 2 resets pela serial:
- `rst:0x1 (POWERON)`, `TESTE CONTEXTO JURIDICO: OK`, sem panic.
- Os checks de schema passam (2/3/4/3X).
- Mas: `LEXV1: SD indisponivel -> camadas V1 desativadas` e `LEXV1: CHECK FAIL FAIL_IO sd_montado`.
- A linha `JUR CACHE: …` (que aparece quando o SD monta) também está ausente, ou seja, o cartão não foi montado nem pelo sistema legado.
- Os straps de boot mudaram em relação à sessão aprovada: `boot:0x8` agora, `boot:0x2b` antes.

**Diagnóstico:**
- A falha ocorre antes de qualquer leitura de arquivo, na montagem do volume.
- A diferença do firmware em relação ao app anterior é só a tabela de obras (`.flash.rodata`), sem código novo. O conteúdo novo do SD também não participa da montagem.
- Hipótese principal: contato ou encaixe físico do microSD, ou cartão inserido com o aparelho energizado e sem um power-cycle completo (o reset pela serial não desliga a alimentação do cartão).

**Ação:** PARADO, sem nenhuma alteração adicional. Aguardando Arthur conferir o encaixe do cartão e fazer um power-cycle completo.

**Tentativa 3 (após power-cycle completo e reencaixe do microSD por Arthur):**
- Capturado somente o boot (reset pela serial, nada gravado): log `flash/boot3.bin`.
- Resultado idêntico: `boot:0x8`, `SD indisponivel`, `CHECK FAIL FAIL_IO sd_montado`, sem `JUR CACHE`.
- O firmware tenta `SD.begin` a 12 MHz e depois a 4 MHz; as duas falham.
- Teclado HID conectado, sem panic.
- `diff -r` entre o fonte do candidato e o sketch da baseline `6d0194b`: difere **somente** em `lex_ref_detail_data.h`, que só contém dados. O código de montagem do SD (CS=GPIO4, `SD.begin`) é o mesmo que montou o cartão na sessão aprovada.

**Tentativa 4 (cartão retirado do PC com ejeção segura, aparelho ligado só depois do cartão encaixado):**
- Capturado somente o boot (reset pela serial): log `flash/boot4.bin`.
- Resultado idêntico: `boot:0x8`, `SD indisponivel`, `CHECK FAIL FAIL_IO sd_montado`, sem `JUR CACHE`.

### Verificação read-only do cartão no PC (após os boots sem cartão)

- **Unidade:** `D:` — Generic STORAGE DEVICE (USB, disco 1). Volume FAT32 de 31.902.400.512 B.
- **Estado no Windows:** HealthStatus Healthy, OperationalStatus OK.
- **`chkdsk D:` sem `/f`** (somente leitura): "Não há problemas no sistema de arquivos. Nenhuma ação necessária."
- **Manifesto atual:** 1.071 arquivos.
  - Contra `sd_manifest_post.json`: 0 adicionados, 0 removidos, 0 alterados.
  - `/99_LEX_V1`: 11/11 iguais ao staging (bytes e sha256).
  - Legacy: os 1.060 arquivos estão idênticos ao manifesto pré-deploy.
  - O cartão tinha sido remontado, então esta leitura veio da mídia e não do cache do sistema.
- **Nenhuma escrita:** sem reparo, sem formatação, sem flash.
- **Conclusão: CARTÃO ÍNTEGRO.**

### Boot 5 — com o microSD instalado (primeiro boot válido)

Log: `flash/boot5.bin` (também anexado a `session_serial.bin`).

| Item | Resultado |
|---|---|
| Reset | `rst:0x1 (POWERON)`, `boot:0x2b`, sem panic |
| `TESTE CONTEXTO JURIDICO` | OK |
| SD montado | SIM (`JUR CACHE … fonte=CACHE`) |
| LEXV1 | `lexv1_ver_device_version` OK, schema 3 |
| Pacote | `build=bcdec3872ca79c06 commit=6d0194b… entenda=220 pilotos=9 runtime_cf=CF88_RUNTIME_RESOLVED map=RUNTIME ref=cf-reference-engine-run3` |
| Runtime CF | `runtime hash CONFERE`; `text_map_runtime_guard` PASS |
| Arquivos abertos | MAX_OPEN_COUNT=4 (limite 6) |
| Logs de benchmark | ARTSEARCH e SCROLL: nenhuma linha (`LEXV1_ARTSEARCH_LOG 0`) |
| UI | `UI TESTE ATIVA`, teclado HID pronto |
| **DIAG** | **FAIL — pass=31, fail=2** |

**As 2 falhas:**
1. `CHECK FAIL FAIL_PARSE CF88:ART.25 NONE`. O caso fixo do autodiagnóstico espera o art. 25 **sem** ENTENDA. O Batch04 aprovou ENTENDA para o art. 25 (o aparelho leu `entenda=OK res=DIRECT`, 2.333 B).
2. `CHECK FAIL FAIL_REFERENCE references_single_result count=0`. O caso fixo espera **1** referência no art. 25 (Tema 113). O RUN3 removeu Tema 113 × art. 25 por decisão aprovada (o aparelho leu `refs=0/0`).

**Classificação:** casos fixos desatualizados no autodiagnóstico do firmware. Os dados lidos estão corretos e conferem com o conteúdo aprovado. O contador `lexV1Fail` só é impresso e não desativa nenhuma função.

**Falha de processo:** a validação offline não reproduziu a tabela de casos do autodiagnóstico de boot contra o pacote novo, e devia ter reproduzido.

**Correção proposta (não aplicada; depende de autorização):** trocar o alvo dos 2 casos por `CF88:ART.127`, que tem 1 referência (Tema RG 471) no RUN1 e no RUN3 e não tem ENTENDA. Opcionalmente, incluir `CF88:ART.25` como caso DIRECT com 0 referências. Isso exige recompilar o flag1 (novo sha256) e um novo flash app-only.

## 7. Correção do autodiagnóstico (opção A, autorizada por Arthur) — candidato r2

**Fonte:** `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino`, 2 linhas, ambas dentro do código V1:
- caso `{"CF88:ART.25",true,LEXV1_RES_NONE,"",1,1}` → `{"CF88:ART.127",true,LEXV1_RES_NONE,"",1,1}`;
- `references_single_result`: `lexv1References(…,"CF88:ART.25",u)` → `"CF88:ART.127"`.

O art. 127 tem 1 referência visível (Tema RG 471) e nenhuma ENTENDA, tanto no RUN1 quanto no RUN3, então o caso vale para os dois pacotes.

**Testes:**
- `tests/test_a3b_prep.py` foi atualizado para o art. 127.
- Novo teste `test_boot_diagnostic_cases_on_both_packages`: executa a tabela de casos do boot (os 10 casos e as 3 consultas de referências) contra o SD candidato **e** contra o SD da baseline. Esta era a lacuna que deixou passar a falha.
- Regressão: DEVICE **301/301**, ENTENDA **97/97**, LEGAL_TARGET_ID **65/65**, 0 skips, FAIL_REAL 0.

**Staging:** reconstruído byte-identical. Os 11 arquivos têm os mesmos hashes já gravados no SD físico, então **o SD não precisa mudar**.

**Build r2** (`backups/batch04_run3/`):

| Build | Programa | RAM | sha256 | Observação |
|---|---|---|---|---|
| flag1 r2 | 1.097.235 B | 126.148 B | `3f0df29ee996e44399c78278a21895c7bdc661f22f79cb5b2bbcf853c5e2f5b5` | imagem 1.097.376 B, checksum e validation hash válidos; `candidate_flag1_r2/candidate_app_batch04_run3_r2.bin` |
| flag0 r2 | 989.395 B | 124.452 B | `68c29c0c…ff39` | — |

- O flag0 r2 tem o mesmo tamanho do flag0 r1. Os bytes diferentes são só hora de compilação, sha do ELF e hash final, sem diferença funcional.
- O candidato anterior (`d12c7fce…e8f6`, gravado hoje no app0) fica **superado** pelo r2.

**Próximo passo:** flash app-only do r2 em 0x10000, readback e boot com DIAG `fail=0`. Depende de autorização de Arthur.

## 8. Flash r2 + boot (fase G/H/I) — DIAG PASS

Arquivos em `backups/batch04_run3/flash_r2/`.

**Pré-condições:**
- ESP32-S3 v0.2, MAC `e0:72:a1:f4:fd:28`, flash 16 MB, COM3.
- Partições `148b959c…` e otadata `f94c5d78…` iguais às anteriores.
- `app0_prewrite.bin` contém o r1 (`d12c7fce…`).

**Gravação:**
- `write-flash 0x10000 candidate_app_batch04_run3_r2.bin`: 1.097.376 B, "Hash of data verified".
- Somente app0 foi gravado.

**Readback:**
- sha256 `3f0df29ee996e44399c78278a21895c7bdc661f22f79cb5b2bbcf853c5e2f5b5`, `cmp` idêntico: **PHYSICAL_READBACK_MATCH = TRUE**.
- Partições e otadata: inalteradas.

**Boot com SD** (`flash_r2/boot.bin`):
- `rst:0x1 (POWERON)`, `boot:0x2b`, sem panic.
- `TESTE CONTEXTO JURIDICO: OK`.
- SD montado (`JUR CACHE`).
- `build=bcdec3872ca79c06`, `entenda=220`, `ref=cf-reference-engine-run3`, `runtime hash CONFERE`.
- `CF88:ART.127`: `refs=1/1`, PASS; `references_single_result` PASS.
- **`DIAG RESULT PASS pass=33 fail=0 MAX_OPEN_COUNT=4`**.
- Nenhuma linha `[ARTSEARCH]`, `[ARTIDX]` ou `PERF SCROLL`: logs de benchmark OFF.
- UI ativa.
- Índices CF/CC: carregados sob demanda ao abrir cada texto (sem log em produção). A verificação fica com os testes de busca.

## 9. Testes físicos com Arthur — APROVADO

O resultado informado por Arthur foi cruzado com o log serial capturado durante a sessão (`flash_r2/human_tests_serial.bin`, 761 linhas, local e não versionado).

| # | Teste | Arthur | Evidência serial |
|---|---|---|---|
| 1 | Busca/desempenho: CF 193 e 230; CC 1000, 2000, 2046; ART.2000 nunca ART.2; scroll UP/DOWN | PASS | `BUSCA Art. 193/230/1000/2000` com pouso na linha 6. O CC usa o índice `CC2002_ARTICLE_SEARCH.IDX` (bind ao texto do CC) |
| 2 | ENTENDA Batch04: 25, 29-A, 34, 35, 36; glossários dos arts. 34 e 35 | PASS | `UI ENTENDA CF88:ART.25/34/35/36 -> DIRECT`. Art. 29 e incisos navegados. O texto do glossário foi conferido visualmente por Arthur |
| 3 | RUN3: 37 caput, 43 caput, 43 §2 IV, 62 caput, 201 I, 7 XXXIII, ADCT 68 | PASS | `UI REFERENCIAS … (OK)` para os arts. 37, 43, 62, 201 I, 7 XXXIII e ADCT 68. ADCT 68 alcançado por PRÓXIMA (`flags=---WR-`) |
| 4 | Art. 193: CONTEXTO, camada 4, 3 obras | PASS | `ACTIVE_TARGET=CF88:ART.193`, flags com `W` |
| 5 | Arts. 98 e 202 sem WORK_REFERENCE | PASS | relato de Arthur |
| 6 | Sem vazamento do art. 37 caput para §1 e §6 | PASS | relato de Arthur. Camada 4 do art. 37 com `query_keys=2` (art + caput) |
| 7 | Próxima ocorrência CF 5 → ADCT 5 → SEM OUTRA OCORRÊNCIA | PASS | relato de Arthur. O mesmo mecanismo aparece no log em 34 → ADCT 34 e 68 → ADCT 68 |
| 8 | Troca CF → CC → CF com o índice da norma certa | PASS | índices CF88 e CC2002 abertos e fechados alternadamente (`ARTIDX_HDR`) |
| 9 | Fluidez geral | PASS | `PERF SCROLL` média 90–125 ms, máx. 195 ms (o mesmo patamar da baseline). Heap estável ~115 KB |

**Saúde do log:**
- Zero reset (`rst:`), panic, Guru Meditation, watchdog, abort, exceção, `FAIL`, `FAIL_IO` ou erro/indisponibilidade de SD.
- `MAX_OPEN_COUNT` = 4 em todo o log (limite 6).
- Zero linhas `[SCROLL]`, `[ARTSEARCH]` ou `[ARTIDX]`: logs de benchmark OFF.
- As linhas `PERF SCROLL` (a cada 32 passos) e `PERF CONTEXTO_ATUALIZAR` são logs legados, sempre ativos e presentes desde a tag 2026-10-01. Não são benchmark.

**Ressalva:** a captura serial cobre os itens 1–4 e parte de 8–9. Os itens 5–7 constam do relato humano; o log tem o mecanismo equivalente, mas não esses alvos específicos.

**PHYSICAL_HUMAN_VALIDATION = APPROVED** (Arthur, 2026-10-03).

## 10. Integração ao repositório

**Sketch versionado:**
- `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/` é **idêntico byte a byte** à fonte do r2 (`backups/batch04_run3/src_candidate/…`): `.ino` com o autodiagnóstico corrigido (art. 127) e `lex_ref_detail_data.h` = header RUN3 (`2ca5820a170a3b08ecfa869685d319d65eee5bc94ddf0bfa5854282acce9710b`, 122 entradas).
- O header foi copiado sem regeneração, mantendo inclusive o comentário "CANDIDATO".
- O sketch versionado não aponta mais para o header antigo (`08f8fbdf…`).

**Reprodução do firmware a partir do repositório:**
- Compilei o flag1 diretamente de `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/`: 1.097.235 B de programa, 126.148 B de RAM, imagem de 1.097.376 B, ou seja, os mesmos tamanhos do r2.
- Comparado byte a byte com o r2 gravado: **69 bytes diferem e todos são metadados de build**: hora de compilação (`__TIME__`, offset 76727), sha do ELF no app descriptor (0xB0–0xCF) e hash final da imagem.
- Fora desses campos: **0 diferenças**. O código versionado reproduz o firmware testado.

**Gerador:** `tools/build_ref_detail_header.py --check` → UP_TO_DATE. O modo padrão agora reproduz o header aprovado a partir de RUN3 `REF_PAYLOAD.IDX` + `CF88_WORK_REFERENCE_ADDITIONS.json`.

**Testes atualizados para a baseline nova:**
- `test_ui_refinement`: 122 registros, e os 101 do RUN1 continuam inalterados.
- `test_reference_run3_device`: header do sketch = header RUN3.
- `test_batch04_run3_consolidation`: sketch versionado = fonte do r2; tabela de diagnóstico de boot passa nos dois pacotes.

**Regressão final:** DEVICE **301/301**, ENTENDA **97/97**, LEGAL_TARGET_ID **65/65**, 0 skips, **FAIL_REAL = 0**.

**Hashes do SD/staging aprovados** (idênticos no SD físico):

| Arquivo (`/99_LEX_V1/…`) | Bytes | sha256 |
|---|---|---|
| `00_SYS/LEXV1.VER` | 588 | `6e713989d5693e7aa59565a5c7ae73d39788acae7fd89cb5ea15b71bbec311f6` |
| `00_SYS/LEX_DEVICE_MANIFEST.json` | 7.604 | `25fceb1e99759c9aa115f9ec323daf1802602ef3f09beebe30de4d2eb31a6b9a` |
| `05_TEXT/CF88_RUNTIME.txt` | 587.133 | `7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a` |
| `10_TARGETS/CC2002_ARTICLE_SEARCH.IDX` | 25.036 | `674c9971925c29aaca9685fb2d0b9515fe87e4072d644858ea27495c327d3a68` |
| `10_TARGETS/CF88_ARTICLE_SEARCH.IDX` | 5.216 | `56e437a0c9cebb113c47f6a7b100ee64363c63207a647eca0456e86d6db27fae` |
| `10_TARGETS/CF88_TARGETS.IDX` | 165.466 | `5eb2da36ff01a7e5cc976e3b7d3eabc8999b95ae8d4b5932f752501af351b980` |
| `10_TARGETS/CF88_TEXT_MAP.IDX` | 123.578 | `889f82002e82fb2b7d9165e6ce2a4e0dcb78d311432e268c341f1d0b1e436b96` |
| `20_REFERENCES/REF_LOOKUP.IDX` | 6.955 | `6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8` |
| `20_REFERENCES/REF_PAYLOAD.IDX` | 68.075 | `24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea` |
| `30_ENTENDA/ENTENDA_LOOKUP.IDX` | 38.700 | `3014442e2da813215fa701aa67006e37cc59945bc280f632fedf056165370d21` |
| `30_ENTENDA/ENTENDA_PAYLOAD.DAT` | 404.510 | `4efa54788fc468d1355b6d7937b3bd88a7c8c88f5a4a0dd20760082238b1e516` |

Total: 11 arquivos, 1.432.861 B.

**Reprodução do staging após o commit:**
- O pacote registra o commit-base do build: `GIT_COMMIT|6d0194b8…` no `LEXV1.VER` e `git_commit`/`build_date`/tags no manifesto.
- `build_sd_staging.build(..., build_commit=…)` fixa esse commit, e `build_batch04_run3_candidate.py` usa `BUILD_COMMIT = 6d0194b8ba82f0612ca73aa75a4377fa5b2b635a`.
- Depois do commit da baseline, o staging reconstruído é **idêntico byte a byte** aos 11 arquivos do SD físico (`test_deterministic_rebuild` PASS).
- O build padrão continua usando o HEAD.

**Fora do commit** (ignorados ou não relacionados):
- `backups/` (flash, readbacks, logs seriais brutos, builds, binários);
- os stagings (reconstruíveis);
- pastas históricas não rastreadas anteriores à baseline;
- `updater/`, `CLEANUP_AUDIT/`, zip em `firmware/LEX MAQUINA INO 2/`.

**Commit:** `LEX DEVICE V1: approve Batch04 and RUN3 physical baseline`. **Tag anotada:** `lex-device-v1-batch04-run3-physical-approved-2026-10-03`. As tags anteriores estão preservadas. **Push: NÃO.**
