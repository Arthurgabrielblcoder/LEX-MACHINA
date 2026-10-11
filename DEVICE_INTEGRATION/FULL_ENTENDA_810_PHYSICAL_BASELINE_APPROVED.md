# LEX MACHINA DEVICE V1 — baseline física aprovada com 810 ENTENDAs

**Status: BASELINE FÍSICA APROVADA (2026-10-11).**
- `PHYSICAL_HUMAN_VALIDATION = APPROVED_BY_ARTHUR`.
- Tag anotada: `lex-device-v1-entenda-810-physical-approved-2026-10-11`, no commit que contém este relatório.

## 1. Identidade

| Item | Valor |
|---|---|
| Data | 2026-10-11 |
| Branch | `device-entenda-810` |
| Origem jurídica | `reconcile-macro07-macro08` @ `fa9719a6bd335275252473a5f154e4e11f5532f4`: 810 ACTIVE, 810 HUMAN_APPROVED_T1, 0 pendentes, 0 aprovações perdidas, 0 conflitos ativos |
| Commits do deploy e do firmware | `fee60a5` (pacote, ferramentas e testes), `e9c7d53` (correção diagnóstica, antes do flash), `d53188c` (relatório do flash), e o commit deste relatório |
| Pacote | `FULL_CF_ENTENDA_810`, build id `de963699728cb66e`, `GIT_COMMIT fa9719a…` |
| Schema | `DEVICE_VERSION 3` (inalterado) |
| Relatórios desta baseline | `FULL_ENTENDA_810_PREDEPLOY_REPORT.md`, `FULL_ENTENDA_810_DIAG_FLASH_REPORT.md` e este |

**Cadeia física anterior, preservada:**
- `lex-device-v1-batch04-run3-physical-approved-2026-10-03`;
- `lex-device-v1-full-corpus-indexes-approved-2026-10-04`;
- `lex-device-v1-72-indexes-approved-2026-10-04`;
- `lex-device-v1-context-citation-guard-approved-2026-10-04`.

Nenhuma tag antiga foi movida.

## 2. Conteúdo

- **ENTENDA:** 810 `HUMAN_APPROVED_T1` e 0 `PENDING_HUMAN_REVIEW`, cobrindo CF/88 + ADCT (`ENTENDA_SCOPE CF88_ADCT_FULL_HUMAN_APPROVED_T1`).
- **Composição:** 382 (base + Batch01–06) + 249 (Macro07) + 179 (Macro08), derivada dos corpora reais pelo perfil `FULL_CF_ENTENDA_810` de `tools/build_sd_staging.py`.
- **Lookup:** 1.069 linhas (810 DIRECT + 259 COVERED_BY_BLOCK).

| Arquivo `/99_LEX_V1/…` | Bytes | SHA-256 |
|---|---|---|
| `30_ENTENDA/ENTENDA_LOOKUP.IDX` | 110.312 | `017050dc98b76cdbea9997c6d3ad49f34673393c6768fcb43fa0eb9767120c99` |
| `30_ENTENDA/ENTENDA_PAYLOAD.DAT` | 1.560.621 | `dbea72601046e6d9fba2f6a6442a490f905a03911186f9aeb44db7e6184e0fd3` |
| `10_TARGETS/CF88_TARGETS.IDX` | 165.466 | `616a469b11dd673347dc665232a83fc8d5bcd8e3c6bfd5f07a4a56c62f5972a7` |
| `00_SYS/LEX_DEVICE_MANIFEST.json` | 7.646 | `7394cb6a928dfde73e50ab73a0120ff38aadc0457a46a9f7678c04cd190be60b` |
| `00_SYS/LEXV1.VER` | 585 | `2be2e36934b7420d8bddd8a122ff6fd57a9361f215c5e139da103f498c928b45` |

- **Reprodutibilidade:** `python tools/build_full_entenda_810_candidate.py` produz builds byte-idênticos, com os mesmos 5 hashes. Isso foi reconferido no fechamento.
- **Perfis antigos:** o perfil default (163) e o BATCH04_RUN3 (220) continuam reproduzindo seus pacotes byte a byte.
- **Os 220 ENTENDAs anteriores:** as 362 linhas do lookup antigo estão byte-idênticas no pacote novo.

## 3. microSD (`D:`, FAT32, 31.902.400.512 B, "Generic STORAGE DEVICE")

- **Baseline anterior:** o manifesto físico pós-MARIA2006. O PRE confirmou 1.142 arquivos, 82 em `/99_LEX_V1` e 0 divergências.
- **Deploy** (`tools/deploy_full_entenda_810_sd.py pre/copy/verify`):
  - **5 substituídos, 0 adicionados, 0 removidos**;
  - os outros 1.137 arquivos estão byte-idênticos ao PRE.
- **Preservados:**
  - `CF88_RUNTIME.txt` (`7ef82290…`) e `CF88_TEXT_MAP.IDX` (`889f8200…`);
  - os 72 índices de artigo, incluindo CF88 `56e437a0…` e CC2002 `674c9971…`;
  - o reparo MARIA2006;
  - o Reference Engine RUN3 (`REF_LOOKUP` `6d6c88d7…`, `REF_PAYLOAD` `24b4f0d9…`);
  - a Lei Seca e as camadas legadas.
- **Cópia e conferência:**
  - cada arquivo passou por `.LEX_NEW` + `fsync` + readback + `os.replace`, seguido de `Write-VolumeCache D`;
  - o readback dos 5 bate com o candidato em bytes e SHA-256 (`SD_VALIDATED`);
  - o boot do aparelho confirmou a mídia: offsets do lookup idênticos e `runtime hash CONFERE`.

## 4. Firmware

| Item | Valor |
|---|---|
| Hardware | ESP32-S3 (QFN56) rev v0.2, PSRAM 8 MB, flash 16 MB, MAC `e0:72:a1:f4:fd:28`, COM3 (CH343) |
| Região gravada | **somente app0**, em `0x10000` (partição `0x140000`), com `--flash-mode/freq/size keep` |
| Candidato | 1.099.936 B, SHA-256 `445fdb7fe4d9392070c7c3b7524ba2d26fbefe85e4503135af40a65ccfbecca3` |
| Toolchain | arduino-cli 1.5.1, core esp32 3.3.11, `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`, `LEX_DEVICE_V1_ENABLED=1` |
| Readback | 1.099.936 B a partir de `0x10000`, byte-idêntico ao candidato |
| Partições / otadata | `148b959c…53a1` / `f94c5d78…17f0`, idênticas antes e depois |
| Demais regiões | bootloader, NVS, app1, SPIFFS e coredump não foram tocados |
| App anterior | flag1 `03df230e…f495` (guarda de citação de contexto) |

## 5. Correção diagnóstica (única mudança funcional do firmware)

A única mudança entre o firmware físico anterior e o novo é a expectativa do caso fixo `CF88:ART.127` na tabela `casos[]` do autodiagnóstico de boot (`LEX_MACHINA_DEVICE_V1_CANDIDATE.ino`):
- **Resolução:** `LEXV1_RES_NONE` → **`LEXV1_RES_DIRECT`**, âncora **`CF88:ART.127`**; referências 1/1 inalteradas.
- **Origem:** o `ENTENDA_LOOKUP.IDX` aprovado de 810 (`CF88:ART.127|256029|1778|ENTENDA/CF88:ART.127/BASE/1|…|DIRECT`).
- **Prova binária:** o fonte aprovado, recompilado no mesmo caminho, reproduz o app anterior; a diferença são só os metadados de build (SHA do ELF, `__TIME__`, hash final).
- **Diferença do candidato:** além desses metadados, 7 bytes, que são exatamente essa entrada da tabela. Nenhum algoritmo de lookup, UI, navegação, leitor, scroll, acesso ao SD, schema, buffers ou Reference Engine foi alterado.

## 6. Boot (`serial_boot.log`, SHA-256 `58c175a5…3c24`)

| Item | Resultado |
|---|---|
| Reset e SD | um único `rst:0x1 (POWERON),boot:0x2b`; SD montado |
| Parser | `TESTE CONTEXTO JURIDICO: OK` |
| JUR CACHE | `lookups=178 registros=296 … fonte=CACHE` |
| Versão e conteúdo | `DEVICE_VERSION` 3; `build=de963699728cb66e … entenda=810`; `runtime hash CONFERE` |
| Art. 127 | `res=DIRECT anchor=CF88:ART.127 off=256029 len=1778 lidos=1778` |
| DIAG | **`LEXV1: DIAG RESULT PASS pass=33 fail=0 MAX_OPEN_COUNT=4`** |
| Erros | nenhum crash, panic, Guru, watchdog ou reboot loop; 0 `FAIL_IO`, 0 `FAIL_HASH`, 0 `FAIL_SCHEMA`, 0 `FAIL_TARGET`, 0 `CHECK FAIL` |

## 7. Validação humana

`PHYSICAL_HUMAN_VALIDATION = APPROVED_BY_ARTHUR`.

Escopo testado por Arthur no aparelho:
- art. 5;
- art. 127;
- art. 156-A;
- dispositivo do ADCT;
- scroll para baixo e para cima;
- paginação;
- BACK;
- retorno à posição da Lei Seca;
- busca e navegação normal.

Resultado: **`ALL_PHYSICAL_SMOKE_TESTS_PASS`**.

## 8. Backups e rollback (fora do Git)

Locais: `DEVICE_INTEGRATION/backups/full_entenda_810_physical_deploy/` e `DEVICE_INTEGRATION/backups/full_entenda_810_diag_flash/`, no checkout principal; o Git os ignora.

| Evidência | SHA-256 |
|---|---|
| Manifesto pré-deploy do cartão (`sd_manifest_pre_full.json`) | `994b1108…0407` |
| Manifesto pós-deploy (`sd_manifest_post_full.json`) | `ed479b18…33d2` |
| Backup dos 5 arquivos antigos do SD (`sd_pre/99_LEX_V1/`, índice `sd_pre_backup_manifest.json`) | `872aa50d…3474` |
| Backup completo do app0 antes do flash (`app0_pre.bin`, 1.310.720 B) | `6ea6ff90b39e58bba751430d6db429413fad77a308c486be37cbdc7e2099ce20` |
| Partições e otadata pré e pós, candidato, base recompilada, logs de build e serial | — |

O staging do pacote também fica fora do Git: `DEVICE_INTEGRATION/staging_sd_v1_full_entenda_810_candidate/`.

**Rollback:**
- **SD:** copiar os 5 arquivos de `sd_pre/99_LEX_V1/` de volta para `D:\99_LEX_V1\` e conferir contra `sd_pre_backup_manifest.json`.
- **Firmware:** `esptool --chip esp32s3 -p COM3 write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 app0_pre.bin`, depois readback da partição contra `6ea6ff90…`.

## 9. Verificações do fechamento (sem hardware)

- **Integridade:** desde `fa9719a`, nenhum arquivo jurídico mudou; os commits só tocam ferramentas, testes e relatórios de dispositivo, mais a linha do diagnóstico.
- **Pacote 810:** reconstruído e byte-idêntico aos 5 arquivos lidos do cartão.
- **Testes:**
  - `test_full_entenda_810`, `test_a3b_prep`, `test_context_citation_guard` e `test_batch04_run3_consolidation`: 74 testes;
  - a única falha é a ambiental preexistente `test_firmware_source_candidate`, idêntica no baseline;
  - a suíte DEVICE_INTEGRATION completa, antes do flash, tinha 353 testes com as mesmas 4 falhas ambientais do baseline.
- **Sem escrita em hardware:** nesta etapa não houve flash nem escrita no SD.

## 10. Dívidas conhecidas, não bloqueantes

- **`MATERIALIZATION_DEBT`:** `updater/fontes_oficiais_verificacao/EC45_2004/planalto_raw.html` com o SHA-256 travado (`76f9b562…`) só existe no checkout principal; o blob versionado (`0c46…`) não o reproduz. O exportador do runtime falha fechado sem ele.
- **`KNOWN_PRESENTATION_DEBT`:** a frase fixa de `editorial_checks.py::triage_md` nos relatórios `REVIEW_*_RISK_TRIAGE.md`.
- **Merge:** não houve merge em `main`; a integração em `main` é uma etapa separada.
