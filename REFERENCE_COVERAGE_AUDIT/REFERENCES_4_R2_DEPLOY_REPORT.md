# REFERÊNCIAS Nº 4 — CF: R2, deploy controlado do candidato

```
DATE = 2026-10-16 · BRANCH = cf-references4-finalize
HOST_GATES = PASS · PREEXISTING_CORRELATA_TEST_DEBT = 4 (não tratada)
SD_ROLLBACK_READY = YES · FIRMWARE_ROLLBACK_READY = YES · PREDEPLOY_SD_BASELINE = PASS
CANDIDATE_FIRMWARE_SHA256 = 6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c
FIRMWARE_FLASH = PASS · SD_FILES_WRITTEN = 5 · SD_CANDIDATE_HASHES = PASS · MANIFEST_VS_SD = PASS
RELACOES / REL_LOOKUP / EXT_ARTIGOS UNCHANGED = YES
STATUS = AGUARDANDO TESTE FÍSICO MANUAL · REFERENCES4_FROZEN = NO · sem tag, sem promoção de baseline
```

**Evidências.** Os arquivos versionados estão em `R2_PHYSICAL_DEPLOY/`:

- `firmware_flash.json`
- `physical_pre.json`
- `sd_pre_backup_manifest.json`
- `physical_validation.json`
- `sd_manifest_post_full.json`

Os binários ficam fora do Git, em `DEVICE_INTEGRATION/backups/references4_r1_physical_deploy/`: `fw/` com os dumps e `sd_pre/` com os bytes C3B.2.

## Gates do host

| Verificação | Resultado |
|---|---|
| `LEGAL_TARGET_ID` | 90/90 |
| `DEVICE_INTEGRATION` | 362/362 |
| Testes novos R1 | 9/9 |
| `--check` de R1A, R1 e auditoria | UP_TO_DATE |
| Auditoria de isolamento | todos os invariantes 0 e `FIRMWARE_LIMITS PASS` |

**Firmware candidato.**

- `image-info`: checksum e validation hash válidos, ESP-IDF v5.5.5.
- Fonte: igual ao do firmware gravado (`e9c7d53`, `.ino` normalizado `6c8c98fb…`), exceto `lex_ref_detail_data.h`.
- A base recompilada difere do app gravado (`445fdb7f…`) só em 69 bytes de metadados de build.

## Rollback (provado antes de qualquer escrita)

- **SD:** os 5 arquivos de `rollback/` do pacote batem com o manifesto físico pós-C3B.2. O backup PRE no cartão foi lido e conferido em `sd_pre/`.
- **Firmware:** o app0 inteiro foi lido duas vezes, com resultado idêntico (`cd20fd52…`, 1.310.720 B). Os primeiros 1.099.936 B são exatamente o app aprovado `445fdb7f…`.
  - Para restaurar: `esptool --chip esp32s3 -p COM3 -b 460800 --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 fw/app0_pre.bin`, seguido de readback.
  - NVS foi preservado em `fw/nvs_pre.bin`.

## Pré-deploy do cartão

D: inteiro (1.142 arquivos) é byte-idêntico ao último manifesto físico aprovado (C3B.2), e `LEXV1.VER` mostra `3999dfc97c45d91d` / `cf-reference-engine-run4`.

## Flash

**Dispositivo:**

| Item | Valor |
|---|---|
| Porta | COM3 (CH343) |
| Chip | ESP32-S3 rev v0.2, PSRAM 8 MB |
| MAC | `e0:72:a1:f4:fd:28` |
| Flash | 16 MB |
| Partições | `148b959c…` |
| otadata | `f94c5d78…` (app0 ativo) |

**Gravação.**

- Comando: `write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000` com o candidato (1.101.136 B).
- Retorno: "Hash of data verified".
- Readback independente: `6e329c91…`, **idêntico**.
- Partições e otadata não mudaram.
- O aparelho ficou no bootloader (`--after no-reset`): o app novo ainda não rodou.

## SD: arquivos escritos

A escrita usou arquivo temporário, `fsync`, `os.replace` e readback.

| Arquivo | Bytes | SHA-256 |
|---|---:|---|
| `/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | 65.514 | `da49c43b7a21990334a6a1af63fbc605fec7fde195a06a2014776285455006eb` |
| `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | 6.750 | `efabb245e3beb8b63df33249a7a2e3c178aace02b361d9d344cb348d0fa823a0` |
| `/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | 165.466 | `d4e3342b99f5a5efb732eb9b36f786f3eaf5a33ab651500c7ce8a387bfe593f7` |
| `/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | 7.622 | `7b8da57d943aef59f6dda55f1eb86484b516f7170da7074e3638949c7ce292fb` |
| `/99_LEX_V1/00_SYS/LEXV1.VER` | 600 | `edaf6147767ceece3fdd3149b63d79037e8e06a9de8ca71e3589da88a3758125` |

**Verificação pós-escrita:**

- O diff do cartão inteiro mostra apenas esses 5 arquivos alterados: nenhum adicionado, nenhum removido, total de 1.142 mantido.
- Manifesto × cartão: PASS, com 10 entradas conferidas.
- RELACOES, REL_LOOKUP e EXT_ARTIGOS: byte-idênticos.

## Checklist físico (o usuário executa; o host não interpreta)

1. **Boot:** remova o cartão com segurança, recoloque-o no LEX MACHINA e ligue.
   - Esperado: inicialização normal, sem mensagem de incompatibilidade, navegação normal.
   - No serial, se houver captura: `DIAG RESULT PASS` e `ref=cf-reference-engine-run5-references4-r1`.
2. **Referência antiga:** CF art. 37 → `4 REF.`.
   - Esperado: Os Donos do Poder e Raízes do Brasil, com a ficha abrindo normalmente.
3. **CF art. 196** → `4 REF.`.
   - Esperado: **Sicko - S.O.S. Saúde**. A ficha mostra DOCUMENTÁRIO, 2007, nota 7,4, Michael Moore no "sobre" e o alcance com "Limites". BACK volta normalmente.
4. **CF art. 206, I** → `4 REF.`.
   - Esperado: **Pro Dia Nascer Feliz**. A ficha mostra DOCUMENTÁRIO, **2005**, nota 8,0 e João Jardim no "sobre". BACK volta normalmente.
5. **Sem herança de W:** CF art. 206 (caput) e art. 206, II.
   - Esperado: `4 REF.` **não** aparece.
6. **Correlata:** CF art. 202, § 5º → `1 CORR.`.
   - Esperado: LC 108/2001 aparece e abre no art. 26.
7. **Stale flag:** CF art. 37, § 3º, III.
   - Esperado: `1 CORR.` **não** aparece.
8. **ENTENDA (smoke):** CF art. 127 → `3 ENTENDA`.
   - Esperado: abre normalmente.

**Se algo falhar:** não corrija nada no cartão. Anote:

- o target;
- as opções exibidas;
- a obra exibida;
- o conteúdo da ficha: texto, ano e nome;
- o comportamento das teclas;
- qualquer travamento ou reinicialização.

Depois, devolva o cartão ao PC para diagnóstico.

**Rollback** (só se necessário): restaure o firmware pelo comando acima e os 5 arquivos de `sd_pre/`.
