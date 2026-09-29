# ROLLBACK PLAN (V1, atualizado na A3B-PREP)

**Estado em 2026-09-29 (V1-A3B-PREP): `FULL_PHYSICAL_ROLLBACK_AVAILABLE`.**
- O cartão tem o overlay `/99_LEX_V1` (A3A); o legado está intacto (0 alterações).
- A flash **não** foi escrita; o ESP32 continua com a v7.12.0.
- Nenhuma restauração foi executada.
- A política de integridade da flash está em `FLASH_INTEGRITY_POLICY.md`.

| Evidência | Situação |
|---|---|
| Flash: `LEGACY_BASELINE_FLASH_BACKUP` | `backups/esp32/raw_flash_16MB_read1.bin` (A2), 16.777.216 B, sha256 `061849a3…6727`, duas leituras idênticas |
| Flash: `PRE_A3B_FULL_FLASH_BACKUP_VERIFIED` | `backups/esp32_a3b/pre_a3b_full_flash_16MB.bin`, sha256 `02403736…ef05`, confirmado por segunda leitura idêntica (`prep_read2_full_flash_16MB.bin`). Em relação ao baseline, só difere na NVS `phy/cal_data` (1.966 B, `ALLOWED_EXPLAINED`) |
| `NVS_PRE_A3B` | `backups/esp32_a3b/nvs_pre_a3b.bin`, 0x9000 + 0x5000, sha256 `3f53eb85…92c0`, igual à leitura direta |
| `LEGACY_APP0_PARTITION` | `backups/esp32_a3b/legacy_app0_partition.bin`, 0x10000 + 0x140000, sha256 `ab6d4ffc…1c1f`, igual à leitura direta e ao app0 do baseline |
| Firmware físico | **PHYSICAL_FIRMWARE_CONFIRMED_V7_12_0**, app ativa `app0` (otadata seq=1) |
| Cartão SD | **BACKUP_VERIFIED**: `backups/sd_20260929T163407Z/`, com 1.062 arquivos, 24.574.047 B e hash agregado `f00e6d56…9b38` |
| Fonte do firmware | `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/` |

## Ordem preferencial de restauração da flash

Vá para o próximo passo só se o anterior não recuperar o aparelho.

1. **Só a app (`LEGACY_APP0_PARTITION`).** Reverte o firmware sem mexer em bootloader, partições, NVS, otadata ou spiffs.
   1. Conferir o sha256 `ab6d4ffc…` do arquivo.
   2. Conferir a identidade do aparelho com `esptool --port <COM> flash-id`: ESP32-S3 v0.2, 16 MB, MAC `e0:72:a1:f4:fd:28`.
   3. Gravar: `esptool --chip esp32s3 --port <COM> --before default-reset --after hard-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 legacy_app0_partition.bin`.
   4. Ler de volta `read-flash 0x10000 0x140000` e exigir igualdade byte a byte com o arquivo.
   5. Validar o banner `LEX MACHINA V7.12.0 JURIS CF EXPANDIDA` e o log `JUR CACHE: lookups=178 registros=296`.
2. **`PRE_A3B_FULL_FLASH_BACKUP` (16 MB).** Use quando a app sozinha não basta, por exemplo se outra região tiver sido afetada.
   1. `write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x0 pre_a3b_full_flash_16MB.bin`.
   2. Ler tudo de volta e exigir sha256 `02403736…`.
   3. Rodar `flash_region_diff.py` contra o dump com veredito `PASS`.

   Esse dump contém a NVS mais recente (calibração de rádio atual).
3. **`LEGACY_BASELINE_FLASH_BACKUP` (16 MB) — último recurso.** Mesmo procedimento com `raw_flash_16MB_read1.bin` (sha256 `061849a3…`). Restaura a NVS de A2, mais antiga, com a calibração de rádio anterior. A NVS é mutável e o ESP-IDF recalibra, mas não há motivo para regredir se o passo 2 bastar.

- **Snapshot de NVS.** `nvs_pre_a3b.bin` serve para diagnóstico e para restauração pontual da região 0x9000–0xDFFF (`write-flash 0x9000 nvs_pre_a3b.bin`), e só com autorização explícita. Nenhum deploy da V1 escreve NVS.
- **Alternativa de build.** Recompilar a v7.12.0 (`esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`) dá um resultado funcionalmente igual, mas não byte a byte. Prefira o snapshot da app.

## Procedimentos do cartão (sem mudança)

**Caso mínimo.** O overlay V1 é removível. Com autorização, apague apenas `/99_LEX_V1`; nenhuma outra pasta é tocada pela V1.

**Caso completo:**
1. Com autorização explícita, formatar em FAT32 ou limpar o volume.
2. Copiar `backups/sd_20260929T163407Z/data/*` para a raiz.
3. Rodar `python DEVICE_INTEGRATION/tools/backup_sd_readonly.py --verify <DRIVE>\ backups/sd_20260929T163407Z` e exigir `BACKUP_VERIFIED`.

**Voltar ao último estado funcional.** Passo 1 da flash e, se necessário, o caso mínimo do cartão. Depois, o checklist físico `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/CHECKLIST_FISICO.md`.

## Pré-condições para a gravação A3B

- Nova leitura integral com veredito `PASS` contra `PRE_A3B` pela `FLASH_INTEGRITY_POLICY.md`, com snapshot de NVS e de app0 feitos antes.
- Gravar apenas `candidate_app.bin` em `VERIFIED_APP_OFFSET = 0x10000`.
  - Nada de `erase-flash`, imagem merged, bootloader, partições, `boot_app0.bin`/otadata, NVS ou spiffs.
  - Usar `--flash-mode keep --flash-freq keep --flash-size keep`, para que os bytes escritos sejam exatamente os do arquivo.
- Autorização humana explícita para a gravação.
