# SEARCH UX — validação física (centering + next occurrence + REPEAT_READY)

**Status:** `SEARCH_UX_PHYSICAL_CANDIDATE_FLASHED`, com `PHYSICAL_HUMAN_VALIDATION = PENDING_ARTHUR`.

- Gravada somente a app, em 0x10000.
- SD físico não alterado.
- RUN3 e Batch04 não implantados.
- Sem commit.

## Pré-condições (somente leitura, antes de qualquer escrita)

| Item | Resultado |
|---|---|
| Porta | COM3, USB-Enhanced-SERIAL CH343 `VID_1A86&PID_55D3`, a única porta USB serial |
| Chip | ESP32-S3 (QFN56) v0.2, PSRAM 8 MB, MAC `e0:72:a1:f4:fd:28` (igual ao baseline) |
| Flash | 16 MB (fabricante 0x68, device 0x4018) |
| Partições (0x8000) | nvs 0x9000, otadata 0xE000, **app0 0x10000 / 0x140000**, app1 0x150000, spiffs 0x290000, coredump 0x3F0000. sha256 `148b959c…53a1`, idêntico ao dump físico anterior |
| otadata | slot0 seq=1 (app0 ativa); idêntico ao dump pós-rollback A3B |
| app0 atual | primeiros 1.075.744 B = baseline físico aprovado `c01e923a…1a90` (`candidate_caput_flag1`) |
| Rollback disponível | `backups/fast_track/candidate_caput_flag1/candidate_app_caput.bin` sha256 `c01e923a…1a90`, igual ao `readback_caput.bin` do flash aprovado; legado: `backups/esp32_a3b/legacy_app0_partition.bin` |
| Candidato | `backups/search_centering/candidate_ux_flag1/candidate_app_search_ux.bin`, 1.077.600 B, sha256 `5c38f7521f55ef45061120c5c6350aab603e7cd0e2fa5cde913da5133b86b94d`, checksum 0x28 e validation hash válidos (`esptool image-info`). É o mesmo arquivo do build (programa 1.077.451 B, RAM 125.644 B) |

## Gravação (app-only)

- Comando:
  ```
  python -m esptool --chip esp32s3 --port COM3 --before default-reset --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 candidate_app_search_ux.bin
  ```
- Erase limitado a 0x10000–0x117FFF, dentro do app0. esptool: "Hash of data verified".
- **Readback** `read-flash 0x10000 1077600`: sha256 `5c38f752…b94d`, `cmp` idêntico, logo **`PHYSICAL_READBACK_MATCH = TRUE`**.
- Partições e otadata relidos após a escrita: inalterados.
- Não foram gravados bootloader, partition table, NVS, otadata, PHY, app1 nem spiffs.
- Evidências em `backups/search_ux_flash/` (fora do Git): `flash_id.txt`, `partitions_prewrite.bin`, `otadata_prewrite.bin`, `app0_prewrite.bin`, `write.log`, `readback_app0.bin`, `pt_ota_postwrite.bin`, `boot_serial.bin`.

## Boot (serial, 40 s, `boot_serial.bin`)

- 1 reset (`rst:0x1 POWERON`, boot SPI_FAST_FLASH), sem reboot loop, 0 Guru Meditation, 0 panic, 0 FAIL_IO.
- `LEX MACHINA V7.12.0 JURIS CF EXPANDIDA`; `JUR CACHE: lookups=178 registros=296`.
- Schema: `schema_3_aceito`, 2/4/30 rejeitados; `lexv1_ver_device_version status=OK lido=3`.
- `runtime hash CONFERE` (587.133 B, `7ef82290…2e42a`).
- `text_map_sha256_pinned`.
- Descritores: `fd_steady_state OPEN_COUNT=3`, `fd_pico MAX_OPEN_COUNT=4 limite=6 OPEN_COUNT_FINAL=0`.
- **`LEXV1: DIAG RESULT PASS pass=33 fail=0 MAX_OPEN_COUNT=4`**.
- SD montado e lido (`/99_LEX_V1`, dataset atual RUN1). O firmware só abre arquivos com `FILE_READ`; o SD não foi escrito.

## Validação humana (PENDENTE — Arthur)

O SD continua no RUN1. Não espere as novas obras do RUN3 (37, 43, 62, 201…).

Durante a sessão, o serial está sendo gravado sem reset em `backups/search_ux_flash/session_serial.bin` (30 min). Linhas esperadas:
- `LEXV1: BUSCA_POUSO ocorrencia=… TEXT_MAP=… linha_ativa=6 linha_da_ocorrencia=6 topo=…`
- `LEXV1: ESTADO ARTICLE_SEARCH_MODE (… REPEAT_READY=0/1)`
- `LEXV1: BUSCA Art. 5 PROXIMA 2507 -> 430836`
- `LEXV1: ACTIVE_TARGET=…`
- `LEXV1: BUSCA Art. n -> SEM OUTRA OCORRENCIA`

| # | Passo | Esperado | Resultado |
|---|---|---|---|
| 1 | ENTER, 193, ENTER | CONTEXTO ART. 193 sem rolar; rodapé com 4 REF. | PENDENTE |
| 2 | 4 | Capital no Século XXI, Desigualdade para Todos, O Triunfo da Injustiça | PENDENTE |
| 3 | BACK, rolar até o parágrafo único | CONTEXTO ART. 193 / PAR. ÚNICO; 4 REF. some | PENDENTE |
| 4 | rolar de volta ao caput | 4 REF. reaparece | PENDENTE |
| 5 | ENTER | caixa com `193` pré-carregado | PENDENTE |
| 6 | 3, 7 | caixa `37` (nunca `19337`) | PENDENTE |
| 7 | ENTER | CONTEXTO ART. 37 | PENDENTE |
| 8 | ENTER, 5, ENTER | CF art. 5 | PENDENTE |
| 9 | ENTER (caixa `5`), ENTER | ADCT art. 5; CONTEXTO do ADCT; nenhuma camada do CF art. 5 | PENDENTE |
| 10 | ENTER, ENTER | SEM OUTRA OCORRENCIA (~500 ms), sem sair do ADCT art. 5 | PENDENTE |
| 11 | ENTER, 193, ENTER, depois ENTER, ENTER | SEM OUTRA OCORRENCIA; continua no art. 193 | PENDENTE |
| 12 | 1/2/3/4 em targets conhecidos | abrem as camadas; nenhuma vira dígito de busca | PENDENTE |
| 13 | ENTER e BACKSPACE até cancelar | volta à mesma posição; nenhuma busca executada | PENDENTE |
| 14 | após uma busca, rolar 1 linha, ENTER | caixa vazia (regra aprovada). UX: OK / INCÔMODO? | PENDENTE |
| 15 | ENTER, 98, ENTER | CONTEXTO ART. 98, sem 4 REF. | PENDENTE |
| 16 | geral | fluido, sem travar, sem reboot | PENDENTE |

**Se uma falha afetar o uso normal:** fazer o rollback app-only com `candidate_app_caput.bin` (`c01e923a…`) em 0x10000, ler de volta e exigir igualdade. Não restaurar a flash inteira.
