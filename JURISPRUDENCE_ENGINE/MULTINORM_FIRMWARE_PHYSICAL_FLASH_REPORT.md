# Firmware multinorma — primeiro flash físico (sobre o cartão J2I, sem o CC)

```
MULTINORM_FLASH_STATUS = PASS · FLASH_SCOPE = APP_ONLY · READBACK = EXACT · BOOT_WITH_J2I_SD = PASS · LEGACY_J2I_FALLBACK = PASS
SD_CHANGED = NO (cartão dentro do aparelho; não montado, não escrito) · CC_J1_DEPLOYED = NO
MULTINORM_FIRMWARE_PHYSICAL_VALIDATION = PENDENTE (teste humano) · firmware multinorma NÃO declarado fisicamente aprovado
```

Ferramenta: `firmware_multinorm/flash_multinorm_firmware.py`. São 8 etapas, uma por chamada, cada uma com gate. Evidências em `firmware_multinorm/PHYSICAL_FLASH/`. Backups binários ficam em `DEVICE_INTEGRATION/backups/multinorm_physical_flash/` e `multinorm_flash_candidate/`, fora do Git.

## 1. Porta e chip

| Item | Valor |
|---|---|
| Portas presentes | COM1 (ACPI) e **COM3** |
| ESP32_PORT | **COM3**: USB-Enhanced-SERIAL CH343, VID:PID 1A86:55D3, nº de série 5C38165292; sem ambiguidade |
| Chip | ESP32-S3 (QFN56) **rev v0.2**; dual core + LP core, 240 MHz; **PSRAM 8 MB embutida** (AP_3v3); cristal de 40 MHz |
| MAC | e0:72:a1:f4:fd:28 (mesmo aparelho de R2, J2G e J2I) |
| Flash | **16 MB** (fabricante 0x68, dispositivo 0x4018) |

## 2. Binário multinorma autoritativo (congelado antes do flash)

| Item | Valor |
|---|---|
| MULTINORM_APP_BIN | `DEVICE_INTEGRATION/backups/multinorm_flash_candidate/multinorm_app.bin` |
| MULTINORM_APP_SHA256 | **`38c4d71f77b89223860a6643ef9880416cb1f22a8ba933524e6b083442216bb2`** (= build registrado em `MULTINORM_PROTOTYPE_BUILD.json`) |
| MULTINORM_APP_SIZE | **1.107.504 B** |
| Programa / RAM estática | 1.107.363 B (**+5.332 B**) / 126.188 B (**+40 B**) em relação à base J2I recompilada |
| app0 livre | **203.216 B** |
| Fonte | J2I (base + `juris_types.patch`) + `multinorm.patch` (10 edições); sha do .ino `46308981…` = fonte atual |
| Toolchain | esp32:esp32 3.3.11; FQBN `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`; `-DLEX_DEVICE_V1_ENABLED=1` |
| Recompilado depois de congelar | Não |

## 3. Gates host (`01_gates.json`): **HOST_GATES = PASS**

- **Suítes:** motor/empacotador/simulação 44/44, jurisprudência (inclui freeze J2I e gate de provisórios) 119/119, gramática 93/93.
- **CF:** semântica 315/198.
- **Integridade:** binário congelado com sha conferido; a fonte é igual à registrada.
- **Partições:** o `partitions.bin` do build é igual à tabela do chip (`148b959c…`).
- **Rollback:** o app J2I de rollback está presente (`1371e69a…`).

## 4. Estado pré-flash (lido do chip; `04_pre.json`)

| Região | Valor |
|---|---|
| Tabela de partições | sha256 `148b959cbff1c38aa8e1d5c0ba9d612c54997b945e56a63f41223eef650653a1` (= J2I); **app0 @ 0x10000, tamanho 0x140000 (1.310.720 B)** recomputado da tabela → **PARTITION_LAYOUT_MATCH = PASS** |
| otadata | `f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0` (= J2I) |
| NVS | `2ad43c13…` (só registrado) |
| app0 inteiro (2 leituras) | `8bab9de537a091cfdffdf3d494749809e1592cc2184e329e4ea676b048355833`, idênticas → **PRE_APP_READ_STABLE = PASS**. É exatamente o readback pós-flash da J2I |
| App atual (primeiros 1.102.176 B) | **`1371e69a0ef3b16773c36e240b166ee99f73d48c2629d11ebf09191701de2b6c`** = app J2I aprovado (SHA-256 completo) → **CURRENT_APP_MATCHES_J2I_APPROVED = YES** |

## 5. Gravação e verificação

| Item | Valor |
|---|---|
| Comando | `esptool --chip esp32s3 -p COM3 -b 460800 --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 …\multinorm_app.bin` |
| Escopo | **APP_ONLY**: sem `erase-flash`; bootloader, partições, otadata, NVS, app1, spiffs e coredump não gravados |
| esptool | 1.107.504 B (598.226 comprimidos) em 14,2 s; "Hash of data verified" |
| Readback do app0 | primeiros 1.107.504 B = **`38c4d71f…`** → **FLASH_READBACK_MATCH = EXACT**; app0 inteiro pós-flash `be01e268…` |
| Partições / otadata depois | idênticas às de antes |

## 6. Primeiro boot com o cartão J2I (`07_boot_with_j2i_sd.json`, `boot_with_j2i_sd.log`)

- **Boot:** um único boot (POWERON, `rst:0x1`); nenhum panic, abort, brownout ou reset em loop.
- **Banner:** "LEX MACHINA V7.12.0 JURIS CF EXPANDIDA"; teste de contexto jurídico OK; BLE e teclado HID prontos.
- **SD montado:** `LEXV1.VER` lido; build `def71b31a64c2a54` (cartão B/J2I); hash do runtime da CF confere.
- **Diagnóstico da camada V1:** `LEXV1: DIAG RESULT PASS pass=33 fail=0`, com MAX_OPEN_COUNT 4 de 6. Consultas de teste: ADCT 10, II; CF 127 com J; CF 999 inválido.
- **Cache juris:** `JUR CACHE: lookups=237 registros=355 bytes=80812 local=PSRAM … fonte=CACHE`.
- **BOOT_WITH_J2I_SD = PASS.**

## 7. Fallback legado

- **Camada normalizada:** o cartão não tem a camada `06_NORMALIZADO`, e o firmware **não** a exigiu (nenhuma linha "camada normalizada multinorma").
- **Índices carregados:** os legados `05_INDICES_ESP32`, com os mesmos 237 lookups e 355 registros do J2I.
- **CF:** segue pela camada LEXV1, com o diagnóstico aprovado.
- **LEGACY_J2I_FALLBACK = PASS.**

## 8. Cache e memória (medidos no aparelho)

| Item | Medido | Observação |
|---|---|---|
| Lookups no cache | 237 / 4096 | Legado J2I; o candidato normalizado CC-J1 terá 221 |
| PSRAM do cache juris | 81.672 B (8.254.080 → 8.172.408) | O bloco reportado (80.812 B) é exatamente 237 × 68 B + 64.695 B + 1, o que confirma no hardware a entrada de 68 B (`norma[16]`). A estimativa do preflight para a camada normalizada é 78.270 B |
| PSRAM livre depois de tudo | 8.172.408 B de 8.388.608 | — |
| Heap livre / mínimo / maior bloco | 134.388 / 115.536 / 90.100 B | Mesma ordem dos boots anteriores; nenhum erro de alocação |

## 9. Rollback (FIRMWARE_ROLLBACK_READY = YES; não executado)

- **Firmware:** `esptool --chip esp32s3 -p COM3 -b 460800 --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/backups/j2i_flash_candidate/generic_app.bin`. Readback: os primeiros 1.102.176 B devem dar `1371e69a…`.
- **Alternativa bit a bit:** gravar `DEVICE_INTEGRATION/backups/multinorm_physical_flash/app0_pre_flash.bin` (app0 inteiro, `8bab9de5…`) em 0x10000.
- **Cartão:** nenhum rollback necessário, porque não foi alterado.

## 10. Próximo passo

Teste humano (checklist na resposta da missão e abaixo). O firmware multinorma só é considerado fisicamente aprovado depois que o usuário confirmar `MULTINORM_FIRMWARE_PHYSICAL_VALIDATION = PASS`.

**Checklist (resumo):**
- **Itens 1–17:** classes jurisprudenciais da CF e do ADCT, com BACK; inclui o art. 62.
- **Itens 18–20:** Correlatas, Referências nº 4 e ENTENDA.
- **Item 21:** teste negativo do Código Civil; nada do CC-J1 pode aparecer.
- **Item 22:** norma sem jurisprudência, sem vazamento de outra norma.
