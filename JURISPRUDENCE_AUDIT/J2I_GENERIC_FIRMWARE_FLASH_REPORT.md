# J2I — Flash controlado do firmware genérico (app0 @ 0x10000)

```
J2I_FLASH_STATUS = PASS · FLASH_SCOPE = APP_ONLY · FLASH_READBACK_HASH = EXACT · BOOT_WITHOUT_SD = EXPECTED_SD_ERROR
FULL_ROLLBACK_READY = YES · MICROSD_B_STATUS = 315/198 (fora do aparelho durante toda a missão)
J2I_PHYSICAL_VALIDATION = PENDENTE (teste humano) · firmware genérico NÃO declarado fisicamente aprovado · BATCH10 = NÃO INICIADO
```

**Ferramenta:** `j2i_flash_generic_firmware.py`. Uma etapa por chamada, cada uma com gate; evidências em `J2I_PHYSICAL_FLASH/`.

## 1. Porta e chip

| Item | Valor |
|---|---|
| Portas presentes | COM1 (ACPI, placa-mãe) e **COM3** |
| ESP32_PORT | **COM3**: USB-Enhanced-SERIAL CH343, VID:PID 1A86:55D3, nº de série 5C38165292 (mesma instância do histórico R2/J2G); sem ambiguidade |
| Chip | **ESP32-S3** (QFN56), revisão v0.2; Wi-Fi, BT 5 (LE), dual core + LP core, 240 MHz, PSRAM embutida de 8 MB (AP_3v3); cristal de 40 MHz |
| MAC | e0:72:a1:f4:fd:28 (= R2) |
| Flash detectada | 16 MB (fabricante 0x68, dispositivo 0x4018) |
| Configuração dos builds | FQBN `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`; core esp32 3.3.11; arduino-cli 1.5.1; `-DLEX_DEVICE_V1_ENABLED=1` (sem mudança) |

## 2. Estado pré-flash (lido do chip)

| Região | Endereço / tamanho | sha256 | Conferência |
|---|---|---|---|
| Tabela de partições | 0x8000 / 0xC00 | `148b959c…53a1` | = R2 = `partitions.bin` do build genérico |
| otadata | 0xe000 / 0x2000 | `f94c5d78…17f0` | = R2 (boot pelo app0) |
| NVS | 0x9000 / 0x5000 | `2ad43c13…36ea` | só registrado (não gravado) |
| app0, partição inteira | 0x10000 / 0x140000 (1.310.720 B) | `dde8fa29…673d` | lida 2 vezes, idênticas |
| **App atual** (primeiros 1.101.136 B do app0) | — | **`6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c`** | = cópia congelada = registro R2 → **CURRENT_APP_MATCHES_APPROVED = PASS** |

**Mapa de partições:**

| Partição | Endereço | Tamanho |
|---|---|---|
| nvs | 0x9000 | 0x5000 |
| otadata | 0xe000 | 0x2000 |
| **app0** | **0x10000** | **0x140000** |
| app1 | 0x150000 | 0x140000 |
| spiffs | 0x290000 | 0x160000 |
| coredump | 0x3f0000 | 0x10000 |

Backup físico PRE em `DEVICE_INTEGRATION/backups/j2i_physical_flash/` (fora do Git):
- `app0_pre_flash.bin` (partição inteira);
- `partitions_pre.bin`;
- `otadata_pre.bin`;
- `nvs_pre.bin`.

## 3. Gates antes da gravação (`04_gates.json`)

| Gate | Resultado |
|---|---|
| GENERIC_APP_BIN | `DEVICE_INTEGRATION/backups/j2i_flash_candidate/generic_app.bin` (congelado na J2H; não recompilado) |
| GENERIC_BINARY_HASH | **EXPECTED**: `1371e69a0ef3b16773c36e240b166ee99f73d48c2629d11ebf09191701de2b6c` = registro J2H = relatório do build |
| Tamanho | app 1.102.176 B ≤ partição app0 de 1.310.720 B; **208.544 B livres**; magic 0xE9 OK |
| FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE | PASS (recompilado nesta missão; 70 bytes diferem do app aprovado, todos de metadado) |
| Firmware genérico | PROGRAM_DELTA +1.040 B; **STATIC_RAM_DELTA 0** |
| GENERIC_FIRMWARE_TESTS | PASS (`test_juris_types`, `test_hc_prototype`, `test_j2h`: 17/17) |

## 4. Gravação e verificação

| Item | Valor |
|---|---|
| Comando executado | `esptool --chip esp32s3 -p COM3 -b 460800 --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 …\generic_app.bin` |
| FLASH_ADDRESS / FLASH_SCOPE | 0x10000 / **APP_ONLY**: sem `erase-flash`; bootloader, partições, otadata, NVS, app1, spiffs e coredump não foram gravados |
| Resultado do esptool | 1.102.176 bytes gravados (595.696 comprimidos) em 14,2 s; "Hash of data verified" |
| Readback do app0 (partição inteira) | `app0_post_flash.bin`; os primeiros 1.102.176 B = **`1371e69a…2b6c`** → **FLASH_READBACK_HASH = EXACT** |
| Resto do app0 | 3.539 bytes mudaram, todos entre 0x11d160 e 0x11dfff (sobra do último setor de 4 KB da nova imagem), apagados para 0xFF pela gravação; nada fora do app0 |
| Partições / otadata depois | idênticas às de antes (`148b959c…` / `f94c5d78…`) |

## 5. Primeiro boot sem microSD (`07_boot_without_sd.json`, `boot_without_sd.log`)

- **Reinício:** o ESP32 foi reiniciado pelo auto-reset do CH343, com o cartão **fora** do aparelho (estava no PC como D:\). O serial foi capturado por 30 s.
- **Boot:** um único boot, por power-on (`rst:0x1`).
- **Inicialização:**
  - "TESTE CONTEXTO JURIDICO: OK";
  - banner "LEX MACHINA V7.12.0 JURIS CF EXPANDIDA";
  - BLE inicializado;
  - PSRAM detectada, com 8.313.580 B livres após os caches;
  - checagens de schema da camada V1: PASS.
- **Ausência do cartão:** "SD indisponivel -> camadas V1 desativadas". O autoteste `sd_montado` reporta `FAIL_IO`, o que é o esperado sem cartão.
- **Estabilidade:** nenhum panic, Guru Meditation, abort, brownout ou reset em loop.
- **Display:** não observável pelo serial; fica para o teste humano.
- **Resultado:** **BOOT_WITHOUT_SD = EXPECTED_SD_ERROR**. O patch de tipos não derruba o firmware.
- **Correção de classificação:** o classificador v1 contou o banner do ROM duas vezes no mesmo boot (`ESP-ROM:` e `rst:0x`) e marcou FAIL por engano. A v2 reclassificou o **mesmo log salvo**, sem novo reset.

## 6. Rollback completo (`FULL_ROLLBACK_READY = YES`; NÃO executado)

**Firmware:**
- **Comando:** `esptool --chip esp32s3 -p COM3 -b 460800 --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/backups/j2i_flash_candidate/current_approved_app_6e329c91.bin`.
- **Readback:** os primeiros 1.101.136 B devem dar `6e329c91…`.
- **Restauração bit a bit (alternativa):** gravar `DEVICE_INTEGRATION/backups/j2i_physical_flash/app0_pre_flash.bin`, a partição inteira lida do chip, em 0x10000.

**Cartão (Candidato A, 299/186):**
1. Apagar as 15 fichas de `ROLLBACK_DELETE_FILES` (`J2H_PHYSICAL_DEPLOY/sd_pre_backup_manifest.json`).
2. Restaurar os 7 arquivos de `DEVICE_INTEGRATION/backups/juris_j2h_physical_deploy/sd_pre/`; os hashes foram conferidos nesta missão.
3. Conferir o cartão com `J2G_PHYSICAL_DEPLOY/sd_manifest_post_full.json`.

**Regra:** firmware antigo e cartão B nunca juntos. Para voltar, reverta os dois.

## 7. Próximo passo (humano)

1. Desconecte o USB e desligue o LEX MACHINA.
2. No PC, ejete D:\ com segurança.
3. Insira o microSD no aparelho.
4. Ligue.
5. Execute o checklist abaixo.

O firmware genérico só é considerado fisicamente aprovado depois que você confirmar `J2I_PHYSICAL_VALIDATION = PASS`.

## 8. Checklist físico do Candidato B (firmware genérico)

**Tipos novos.** Em cada item: ver o rótulo, abrir a ficha e voltar com BACK para a mesma lista.

1. **Boot com o cartão B:** o aparelho liga normalmente, aceita versão e manifesto, não trava e a navegação funciona.
2. **CF art. 53, § 1º:** **HC 232627**, nunca "OUTRO 232627". Abrir, ler a ficha e voltar.
3. **CF art. 142, § 2º:** **HC 70648**. Abrir e voltar.
4. **CF art. 52, parágrafo único:** **MS 21689**. Abrir e voltar.
5. **CF art. 55, VI:** **AP 694**. Abrir e voltar.
6. **CF art. 35, IV:** **AI 343461** e **ADI 7369**. Abrir e voltar.
7. **CF art. 86 (caput):** **MS 21564**. Abrir e voltar.
8. **CF art. 86, § 1º, II:** **ADPF 378 (CAUTELAR)**. A ficha mostra "DECISÃO PROVISÓRIA". Abrir e voltar.
9. **CF art. 52, I:** **ADPF 378 (CAUTELAR)** também aqui (segundo target ratificado). Abrir e voltar.
10. **CF art. 96, III:** **Rcl 84738 (PROVISÓRIA)**, com aviso de provisoriedade na ficha. Abrir e voltar.
11. **CF art. 53 (caput):** **Inq 4781**, junto com o RG TEMA 950. Abrir e voltar.
12. **CF art. 84, XII:** **ADPF 964**, junto com o RG TEMA 371. Abrir e voltar.
13. **CF art. 15, III:** **Súmula 9 TSE**, nunca "SUMULA STF 9" ou "OUTRO 9". O título da ficha diz "Súmula 9 TSE", sem tribunal repetido. Abrir e voltar.

**Outros tipos novos** (rápido):

14. CF art. 29, X → **Súmula 702 STF**.
15. CF art. 62, § 6º → **MS 27931**.
16. CF art. 86, § 4º → **Inq 672**.
17. CF art. 198 → **ADPF 672**.

**Tipo e tribunal:**

18. Em nenhum lugar aparece "OUTRO". HC, MS, AP, AI, Inq, Rcl e ADPF aparecem com a própria classe, e a súmula do TSE mostra "TSE".

**Regressão do Candidato A:**

19. Tema 793 (CF art. 23, II).
20. SV 46 (CF art. 22, I).
21. Só a ADI 7064 no ADCT 107-A.
22. ADI 7047/7064 no ADCT 101, § 5º.
23. ADI 5017 (CAUTELAR) no ADCT 27, § 11.
24. Tema 935 (CF art. 7º, XXVI).
25. Tema 1093 (CF art. 155, § 2º, VII).

**Regressão da base antiga:**

26. ADI 7697 (CAUTELAR) no art. 166-A.
27. Tema 558 no art. 100.
28. Temas 367 e 387 no art. 16.

**Camadas congeladas:**

29. CF art. 202, § 5º → CORR. → LC 108/2001, art. 26.
30. CF art. 196 → REF. → "Sicko - S.O.S. Saúde".
31. CF art. 127 → ENTENDA abre.

**Ausência:**

32. A Súmula 403/STJ não aparece em lugar nenhum (continua UNRESOLVED_EXTERNAL).

**Se algum item falhar:** anote o item e a tela, não altere nada no cartão e me avise. O rollback completo está na seção 6.
