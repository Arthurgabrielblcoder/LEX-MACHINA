# FULL ENTENDA 810 — correção do autodiagnóstico e flash app-only

Data: 2026-10-11. Branch `device-entenda-810`. Commit do patch, anterior ao flash: `e9c7d53`. Base jurídica: `fa9719a`.

**Estado:** DIAG 33/33 no primeiro boot. Aguarda a validação visual de Arthur. **Não há tag de baseline final.**

Evidências, fora do Git: `backups/full_entenda_810_diag_flash/`.

## Hardware (somente leitura antes do flash)

| Item | Valor |
|---|---|
| Porta | `COM3`, USB-Enhanced-SERIAL CH343 (1A86:55D3); único dispositivo compatível. O COM1 é a porta ACPI da placa. |
| Chip | ESP32-S3 (QFN56) rev v0.2, PSRAM embutida de 8 MB, MAC `e0:72:a1:f4:fd:28` |
| Flash | 16 MB (fabricante 0x68, dispositivo 0x4018) |
| Partições (`0x8000`, `0xC00`) | `148b959c…53a1`: nvs 0x9000, otadata 0xE000, **app0 0x10000/0x140000**, app1 0x150000, spiffs 0x290000, coredump 0x3F0000 |
| otadata | `f94c5d78…17f0` (seq=1, app0 ativo) |
| App em execução | os primeiros 1.099.936 B do app0 = flag1 aprovado `03df230e…f495` |
| Backup do app0 inteiro | `app0_pre.bin`, 1.310.720 B, SHA-256 `6ea6ff90b39e58bba751430d6db429413fad77a308c486be37cbdc7e2099ce20`; duas leituras idênticas |

## Patch

**Onde:** `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino`, tabela `casos[]` do autodiagnóstico de boot. Uma linha:

```
-      {"CF88:ART.127",true,LEXV1_RES_NONE,"",1,1},
+      {"CF88:ART.127",true,LEXV1_RES_DIRECT,"CF88:ART.127",1,1},
```

**Expectativa derivada do lookup:** `ENTENDA_LOOKUP.IDX` do pacote 810, o mesmo arquivo que está no SD (`017050dc…`), tem a linha `CF88:ART.127|256029|1778|ENTENDA/CF88:ART.127/BASE/1|…|DIRECT`. O `REF_LOOKUP` RUN3 continua com 1 referência visível.

**Testes ajustados:**
- `test_a3b_prep`: a tabela `casos[]` é conferida contra o pacote físico de 810;
- `test_context_citation_guard.test_sketch_untouched`: o `.ino` só pode diferir da tag aprovada nesta linha;
- `test_full_entenda_810`: toda expectativa da tabela deve coincidir com o lookup.

**Regressão no host:**
- DEVICE_INTEGRATION: 353 testes, com as mesmas 4 falhas ambientais do baseline `fa9719a` no mesmo worktree;
- os testes do DIAG e do pacote 810 passam;
- o simulador resolve `CF88:ART.127` como DIRECT.

## Build

- Ferramentas: arduino-cli 1.5.1, core esp32 3.3.11, `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`, `-DLEX_DEVICE_V1_ENABLED=1`.
- Fontes: o `.ino` `6c8c98fb…` (blob de `e9c7d53`). Os demais são byte-idênticos aos fontes compilados no flag1 aprovado:
  - `contexto_juridico.h` `d3dd321b…`;
  - `lex_device_v1.h` `1c097108…`;
  - `lex_leitor_scroll.h` `e5b574c4…`;
  - `lex_ref_detail_data.h` `2ca5820a…`;
  - `assets/lex_boot_screen.h` `9304383b…`.

| Imagem | Programa | RAM | `.bin` | SHA-256 |
|---|---|---|---|---|
| Aprovado (flag1) | 1.099.791 | 126.148 | 1.099.936 | `03df230e…f495` |
| Base recompilada (fonte aprovado, mesmo caminho) | 1.099.791 | 126.148 | 1.099.936 | `d76531ef…05b7` |
| **Candidato** | **1.099.791** | **126.148** | **1.099.936** | **`445fdb7fe4d9392070c7c3b7524ba2d26fbefe85e4503135af40a65ccfbecca3`** |

**Diff binário:**
- **Aprovado × base:** 68 bytes, todos metadados de build: SHA do ELF (offsets 176–207), `__TIME__` (77.404–77.417) e hash final da imagem. O fonte aprovado reproduz o app aprovado.
- **Base × candidato:** os mesmos metadados mais 7 bytes em 132.696–132.702, que são exatamente a entrada `casos[]` do art. 127:
  - `res` 0 → 1 (DIRECT);
  - `ancora`: ponteiro de `""` (`0x3c0ba7b7`) → `"CF88:ART.127"` (`0x3c0a27ba`, string já existente).

  `tid`, `existe`, referências 1/1 e a entrada seguinte (`CF88:ART.999`) estão idênticos. Nenhum byte de código mudou.

**Validação da imagem:** `image-info` com checksum 0x17 válido e validation hash válido; cabe no app0 (`0x140000`).

## Flash e readback

- `esptool 5.4.0 --chip esp32s3 -p COM3 -b 460800 --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 <candidato>`.
- 1.099.936 B gravados em `0x00010000` com "Hash of data verified". Bootloader, partições, NVS, otadata, app1, SPIFFS e coredump não foram alvo.
- **Readback independente** de 1.099.936 B a partir de `0x10000`: SHA-256 `445fdb7f…cca3`, byte-idêntico ao candidato (**READBACK_MATCH**).
- Partições `148b959c…` e otadata `f94c5d78…`: byte-idênticas ao pré-flash.

## Primeiro boot

Log `serial_boot.log`, 11.447 B, SHA-256 `58c175a5985c264825eac455f344269855c7b8bf776362979c8710647de13c24`.

| Critério | Resultado |
|---|---|
| Boot | um único `rst:0x1 (POWERON),boot:0x2b (SPI_FAST_FLASH_BOOT)`, sem reboot |
| SD / parser | SD montado; `TESTE CONTEXTO JURIDICO: OK` |
| JUR CACHE | `lookups=178 registros=296 … fonte=CACHE` (preservado) |
| Versão | `lexv1_ver_device_version lido=3 esperado=3`; `build=de963699728cb66e commit=fa9719a… entenda=810 pilotos=9 ref=cf-reference-engine-run3` |
| Runtime | `runtime hash CONFERE` |
| Art. 127 | `res=DIRECT anchor=CF88:ART.127 off=256029 len=1778 lidos=1778 refs=1/1` |
| DIAG | **`LEXV1: DIAG RESULT PASS pass=33 fail=0 MAX_OPEN_COUNT=4`** |
| Erros | `CHECK FAIL` 0, `FAIL_IO` 0, `FAIL_HASH` 0, `FAIL_SCHEMA` 0, `FAIL_TARGET` 0, Guru/panic/Backtrace/WDT/abort 0, `SD indisponivel` 0 |

Os offsets e comprimentos de todos os 10 casos coincidem com o lookup de 810, o que confirma que o SD é o pacote instalado. O microSD não foi lido nem gravado pelo PC nesta etapa.

## Rollback (não necessário)

`write-flash 0x10000 backups/full_entenda_810_diag_flash/app0_pre.bin` (partição inteira, `6ea6ff90…`) e readback da partição.

## Pendente

A validação visual de Arthur: art. 5, art. 127, art. 156-A, um ADCT, scroll e BACK. Depois disso, criar a tag de baseline física.
