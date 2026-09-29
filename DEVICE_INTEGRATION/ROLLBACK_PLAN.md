# ROLLBACK PLAN (V1, atualizado na A2B)

**Estado em 2026-09-29 (V1-A2B): `FULL_PHYSICAL_ROLLBACK_AVAILABLE`.** Nada foi escrito no cartão nem no ESP32. Nenhuma restauração foi executada.

| Evidência | Situação |
|---|---|
| Flash | **PHYSICAL_FLASH_BACKUP_VERIFIED**: `backups/esp32/raw_flash_16MB_read1.bin`, 16.777.216 B, sha256 `061849a3…6727`, duas leituras idênticas |
| Firmware físico | **PHYSICAL_FIRMWARE_CONFIRMED_V7_12_0** |
| Cartão SD | **BACKUP_VERIFIED**: `backups/sd_20260929T163407Z/`, 1.062 arquivos, 24.574.047 B, hash agregado `f00e6d56…9b38`, reverificado contra a origem |
| Fonte do firmware | `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/` (hashes do HISTORICO conferem) |

## Procedimentos documentados (não executar sem autorização explícita)

**A. Restaurar o cartão legado.**
1. Desligar o aparelho, retirar o cartão e conectá-lo ao PC.
2. Identificar o volume pela assinatura. Nunca escolher um volume só por ser removível.
3. **Caso mínimo** (só o overlay V1 foi copiado): apagar apenas `/99_LEX_V1`. As demais pastas nunca são tocadas pela V1.
4. **Caso completo:**
   1. Com autorização explícita, formatar em FAT32 ou limpar o volume.
   2. Copiar `backups/sd_20260929T163407Z/data/*` para a raiz.
   3. Rodar `python DEVICE_INTEGRATION/tools/backup_sd_readonly.py --verify <DRIVE>\ backups/sd_20260929T163407Z` e exigir `BACKUP_VERIFIED`, isto é, conjunto de arquivos, tamanhos e sha256 iguais aos do manifest.

**B. Restaurar o firmware antigo (imagem integral).**
1. Confirmar o sha256 de `raw_flash_16MB_read1.bin`.
2. Identificar a porta com `esptool --port <COM> flash-id`. O resultado deve mostrar ESP32-S3, 16 MB e MAC `e0:72:a1:f4:fd:28`.
3. Gravar com `esptool --chip esp32s3 --port <COM> write-flash 0x0 raw_flash_16MB_read1.bin`. A imagem inclui bootloader, partições, NVS, otadata e app0.
4. Validar o banner `LEX MACHINA V7.12.0 JURIS CF EXPANDIDA` e o log `JUR CACHE: lookups=178 registros=296`.

**Alternativa:** recompilar a v7.12.0 (`esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`). O binário fica funcionalmente igual, mas não byte a byte, porque o ambiente de build é outro.

**C. Voltar ao último estado funcional:** executar A (completo) e B, depois o checklist físico `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/CHECKLIST_FISICO.md`.

## Pré-condições para a próxima escrita física (A3)

- Os dois backups continuam válidos: conferir os sha256 acima antes de qualquer gravação.
- Autorização humana explícita, por operação: cópia do overlay para o SD e, separadamente, gravação do firmware candidato.
