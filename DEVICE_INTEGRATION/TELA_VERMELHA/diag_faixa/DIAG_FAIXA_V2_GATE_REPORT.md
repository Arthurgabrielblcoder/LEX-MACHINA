# LEX_DIAG_FAIXA v2 — gate físico (2026-10-25)

Branch `fw-tela-vermelha` (descendente de `e75e068`). Evidência local, fora do Git:
`DEVICE_INTEGRATION/TELA_VERMELHA/_local/diag_faixa_gate_20261025_220730/`.
O diagnóstico v2 substitui o v1 (`1cbf55c3…`, nunca gravado), cujo `.bin` saiu do Git: binários e dumps ficam só em `_local/`.

## Estado físico declarado
ESP32-S3 Dev Module rev 0.2; tela 3,2" SPI ILI9341 em **3,3 V com J1 aberto**; microSD **instalado** (não acessado); USB no PC.
Pré-verificação elétrica: `POWER_PREFLIGHT = PASS` (detalhes em `PRE_VERIFICACAO_ELETRICA.md`).

## Gate 0 — preservação (somente leitura)
- Porta **COM5**, USB `303A:1001` (USB-Serial/JTAG nativo), SER `E0:72:A1:F4:FD:28`; ESP32-S3 (QFN56) rev v0.2; flash 16 MB; PSRAM 8 MB.
- Tabela real: `nvs 0x9000/0x5000`, `otadata 0xe000/0x2000`, **`app0 0x10000/0x140000`**, `app1 0x150000/0x140000`, `spiffs 0x290000/0x160000`, `coredump 0x3f0000/0x10000`.
- Backup do app0 completo (1.310.720 B): `app0_full_pre.bin` SHA `e04c14be…84f3`. Imagem válida de 1.109.152 B: **`936851787ee780c626a61d714ec798e806c5d4df45679b99c0becd9460ff302d`** = candidato INVON=0 (`fe190d8`).
- PRE: boot `110f4d29…42d0`, tabela `f3134b74…e397`, otadata `f94c5d78…17f0`. Manifesto: `manifest_pre.txt`.

## Gates 1–3 — fonte e compilação
- Fonte: `DEVICE_INTEGRATION/TELA_VERMELHA/diag_faixa/LEX_DIAG_FAIXA/LEX_DIAG_FAIXA.ino`. O sketch existente foi auditado e ampliado para a v2.
- Pinos copiados do firmware principal: CS 10, DC 9, RST 14, MOSI 11, SCK 12, MISO 13, SD_CS 4. O SD é mantido desselecionado e nunca é iniciado.
- Sem SD, BLE, touch ou conteúdo jurídico. SPI a 40 MHz, como no firmware principal; comparação a 10 MHz isolada em uma etapa.
- FQBN `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default,CDCOnBoot=cdc`. O CDC só vale para o diagnóstico, para o log sair na COM5.
- `--warnings all`: 0 avisos. Programa 344.368 B; RAM estática 24.560 B; `.bin` 344.512 B; SHA **`c5b334af694837b12765573992cf87f699d33851feef78d57a02f83422657a62`**.
  (A primeira gravação foi `0af75d99…`, idêntica exceto pelo buffer de log de 48 → 128 caracteres; foi substituída logo em seguida.)

## Gate 4 — gravação
- `write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000`: o esptool apagou somente `0x10000..0x64fff`; `Hash of data verified`.
- Readback de `0x10000`+344.512 B: `c5b334af…7a62`, **idêntico byte a byte**.
- POST: boot, tabela e otadata **inalterados** (mesmos hashes do PRE). Nada foi escrito fora de app0.
- Boot confirmado no Serial (`boot_serial.log`): cabeçalho v2, pinos, 40 MHz, `setRotation(0..3)` → 240×320, 320×240, 240×320, 320×240.
- ID: `RDID4 = FF FF FF` e `0A..0F = FF` → **MISO sem resposta útil** (SDO do LCD provavelmente não ligado ao GPIO13). Não dá para confirmar o controlador pela leitura.

## Ciclo do diagnóstico (~3 min 40 s, repete sozinho)
Para **ROT 0, 1, 2, 3**, nesta ordem:
1. Cores cheias por 1,8 s cada: PRETO → VERMELHO → VERDE → AZUL → BRANCO → PRETO, com um rótulo pequeno no centro ("ROT0 VERMELHO" etc.).
2. **Geometria** (8 s): borda verde de 1 px; borda **ciano** a 5 px; cantos em "L" (sup-esq **vermelho**, sup-dir **azul**,
   inf-esq **branco**, inf-dir **amarelo**); cruz magenta no centro; grade de 20/40 px com números a cada 40; "ROT n" grande e "W=… H=…".
3. **Limites** (7 s): linhas brancas em x=0, x=W-1, y=0, y=H-1; ciano em 1; **vermelho em 79; verde em 80; azul em 239; amarelo em 240; magenta em 319**
   (só as válidas na geometria).
4. **Blocos X** (5 s): faixas verticais 0–79 vermelho, 80–159 verde, 160–239 azul, 240–319 amarelo, com rótulo.
5. **Blocos Y** (5 s): as mesmas faixas, agora horizontais.

Depois, em ROT 3:
- **INV**: a geometria com INVON por 3 s (cores invertidas, esperado), depois volta a INVOFF.
- **10 MHz**: a geometria a 10 MHz por 8 s.
- **RAW 08 / 48 / 88 / C8**: MADCTL sem troca de eixos e geometria lógica forçada em 320×240, para testar a hipótese de um painel nativo em paisagem.
  Cada variante tem 8 s de geometria e depois blocos X.

Por fim aparece "FIM DO CICLO - REINICIANDO" (ROT 3, INVOFF, 40 MHz), e o ciclo recomeça.

## Reversão (quando o usuário autorizar)
Voltar ao INVON=0 (app0 apenas):
```
python -m esptool --chip esp32s3 -p COM5 -b 460800 --before default-reset --after hard-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/TELA_VERMELHA/candidate_invon0/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin
```
Readback de `0x10000`+1.109.152 B deve dar `936851787ee780c6…302d`. Também há o backup byte a byte em `_local/.../app0_full_pre.bin`.

## Resumo
```
POWER_PREFLIGHT: PASS
CURRENT_APP_BACKUP: PASS
CURRENT_APP_SHA256: 936851787ee780c626a61d714ec798e806c5d4df45679b99c0becd9460ff302d
DIAG_SOURCE: DEVICE_INTEGRATION/TELA_VERMELHA/diag_faixa/LEX_DIAG_FAIXA/LEX_DIAG_FAIXA.ino
DIAG_COMPILE: PASS
DIAG_BIN_SHA256: c5b334af694837b12765573992cf87f699d33851feef78d57a02f83422657a62
DEVICE_PORT: COM5 (303A:1001, SER E0:72:A1:F4:FD:28)
APP0_OFFSET: 0x10000
APP0_SIZE: 0x140000
DIAG_FLASH: PASS
DIAG_READBACK: PASS
BOOT: PASS
PARTITION_TABLE_UNCHANGED: YES
BOOTLOADER_UNCHANGED: YES
OTADATA_UNCHANGED: YES
SD_ACCESSED: NO
SD_MODIFIED: NO
MAIN_FIRMWARE_SOURCE_MODIFIED: NO
USER_VISUAL_DIAG: PENDING
```
