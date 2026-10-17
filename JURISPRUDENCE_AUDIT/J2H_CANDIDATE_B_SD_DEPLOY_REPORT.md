# J2H — Deploy controlado do Candidato B no microSD (SD-only, sem flash)

> **⚠ NÃO RECOLOQUE O CARTÃO NEM LIGUE O LEX MACHINA AINDA.**
> O cartão agora traz dados que dependem do firmware genérico (`SAFE_TO_BOOT_WITH_CURRENT_FIRMWARE = NO`).
> A próxima missão é **J2I — FLASH CONTROLADO DO FIRMWARE GENÉRICO + TESTE FÍSICO DO CANDIDATO B**.

```
J2H_STATUS = PASS · J2G_PHYSICAL_VALIDATION = 21/21 PASS · PREDEPLOY = 299/186 · INSTALADO NO SD = 315/198
FIRMWARE_FLASHED = NO · SAFE_TO_BOOT_WITH_CURRENT_FIRMWARE = NO · BATCH10 = NÃO INICIADO
```

## 1. Aprovação física do Candidato A (Parte A)

- **Registro:** `J2G_PHYSICAL_DEPLOY/J2G_PHYSICAL_VALIDATION.json`.
- **Resultado:** J2G_PHYSICAL_VALIDATION = 21/21 PASS e CANDIDATE_A_PHYSICAL_APPROVED = YES.
- **Novo baseline físico:** 299/186.
- **Testes aprovados:** boot, Tema 793, SV 46 (dois targets), ADI 7047/7064, ADI 7064 isolada no ADCT 107-A, ADI 5017 (CAUTELAR), Temas 157/835, SV 5, Tema 1046, Tema 935, Tema 1068, SV 25, Tema 1229, ADI 6457, Tema 1093, ADI 7697, Tema 558, Correlatas, Referências nº 4, ENTENDA e ausência de OUTRO.
- **Observação:** o checklist publicado na J2G tinha 22 itens; o resultado foi registrado como o usuário informou (21/21).

## 2. Gates antes da escrita

| Gate | Resultado |
|---|---|
| PREDEPLOY_SD_BASELINE | 299/186: recontado nos bytes do cartão; 1175 arquivos idênticos ao manifesto pós-J2G (CANDIDATE_A_HASHES = ALL_EXACT, CARD_FILESET_MATCHES_A = YES) |
| PROVISIONAL_GATE (data real 2026-10-17) | PASS: STF:ADI:7697 1/90 dias; STF:ADI:5017 0/90 dias; STF:ADPF:378 0/180 dias; STF:RCL:84738 0/90 dias; nenhum status material mudou |
| FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE | PASS: `firmware/` recompilado nesta missão; 70 bytes diferem do app aprovado `6e329c91…`, todos de metadado |
| GENERIC_FIRMWARE_PROTOTYPE | PASS: recompilado; PROGRAM_DELTA = +1040 B; STATIC_RAM_DELTA = +0 B; tabelas do firmware = tabelas do host |

## 3. Pacote B sobre A

O Candidato B da J2F foi montado sobre o J2C, com as linhas A e B intercaladas no índice legado. Sobre um cartão que já tem o Candidato A, as linhas do A não seriam prefixo. O pacote `J2H_CANDIDATE_B_OVER_A` (`build_j2h_candidate.py`) resolve isso:
- **Índices legados:** mantém os bytes do A como prefixo exato e acrescenta só as **16 linhas do grupo B**.
- **`/99_LEX_V1`:** byte a byte do Candidato B ratificado (RUN11-B).
- **Fichas:** só as 15 fichas novas do grupo B.
- **Equivalência:** o pacote tem exatamente as mesmas linhas e tuplas de lookup do Candidato B J2F; só a ordem muda.
- **Contagem:** 315 vínculos em 198 targets; build `def71b31a64c2a54`.

**Os 16 vínculos acrescentados:**

| Target | Precedente | Origem |
|---|---|---|
| CF88:ART.29:INC.X | STF:SUMULA:702 | J2F |
| CF88:ART.52:PAR.UNICO | STF:MS:21689 | J2F |
| CF88:ART.55:INC.VI | STF:AP:694 | J2F |
| CF88:ART.35:INC.IV | STF:AI:343461 | J2F |
| CF88:ART.86 | STF:MS:21564 | J2F |
| CF88:ART.86:PAR.1:INC.II | STF:ADPF:378 | J2F |
| CF88:ART.52:INC.I | STF:ADPF:378 | J2F |
| CF88:ART.86:PAR.4 | STF:INQ:672 | J2F |
| CF88:ART.96:INC.III | STF:RCL:84738 | J2F |
| CF88:ART.198 | STF:ADPF:672 | J2F |
| CF88:ART.15:INC.III | TSE:SUMULA:9 | J2F |
| CF88:ART.62:PAR.6 | STF:MS:27931 | J2F |
| CF88:ART.53:CAPUT | STF:INQ:4781 | J2F |
| CF88:ART.84:INC.XII | STF:ADPF:964 | J2F |
| CF88:ART.142:PAR.2 | STF:HC:70648 | J2F |
| CF88:ART.53:PAR.1 | STF:HC:232627 | J2E |

**Decisões editoriais preservadas:**
- nenhum registro conjunto novo;
- ADPF 964 sozinha (as ADPFs 965 a 967 não foram fundidas);
- ADPF 378 com o mesmo registro nos dois targets ratificados;
- MS 21564 e ADPF 378 em registros separados no art. 86;
- Súmula 702 do STF e Súmula 9 do TSE separadas por tribunal.

## 4. Rollback A ← B (`ROLLBACK_TO_A_READY = YES`)

- **Cópia PRE real do cartão com o Candidato A:** `DEVICE_INTEGRATION/backups/juris_j2h_physical_deploy/sd_pre/`, com 7 arquivos.
- **ROLLBACK_DELETE_FILES:** 15 fichas.
- **Procedimento:**
  1. Apagar as 15 fichas.
  2. Restaurar os 7 arquivos.
  3. Conferir com `J2G_PHYSICAL_DEPLOY/sd_manifest_post_full.json`.
- **Resultado:** o cartão volta a **299/186**, e não ao J2C.

| Arquivo substituído | sha256 PRE (A) | sha256 instalado (B) |
|---|---|---|
| `99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX` | `c4c12a764cf76a81…` | `483656791f107838…` |
| `99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX` | `3d2b5f3ebf81dfcf…` | `396e1e34374ba22e…` |
| `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | `716f79a1f48410e0…` | `b16f1f81c484e64a…` |
| `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | `ba00a4e9c01d31fb…` | `2ea28d50dec6b2ab…` |
| `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | `8b422e1d4eb18a0b…` | `fe233de1af79d645…` |
| `99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | `441a6b751896c54c…` | `d8bb3278bd282d96…` |
| `99_LEX_V1/00_SYS/LEXV1.VER` | `16449faf75c592e8…` | `ed258cd30f2f6b40…` |

**Arquivos criados (15):**

- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADPF_378.TXT` (`e4983a47398b469f…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADPF_672.TXT` (`d5f686f19978fd86…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADPF_964.TXT` (`3e424bc5e0d09fbd…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_AI_343461.TXT` (`4543027cafa8d7b2…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_AP_694.TXT` (`f99b0fac51419f7e…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_HC_232627.TXT` (`b2d0ff8a19556c45…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_HC_70648.TXT` (`6c22e0b51e15b719…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_INQ_4781.TXT` (`0a4751c14ba939a2…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_INQ_672.TXT` (`65e98eaeedca9899…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_MS_21564.TXT` (`9adaafe0f24f77fc…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_MS_21689.TXT` (`93ff54957f5b5184…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_MS_27931.TXT` (`ce353ce46bc83ef5…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RCL_84738.TXT` (`55a1366d5c4acac2…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_SUMULA_702.TXT` (`eb5c0a02fd63ace9…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/TSE_SUMULA_9.TXT` (`7c0e74fa16221a4c…`)

| Índice legado | A_INDEX_PREFIX_IDENTICAL | OLD_OFFSETS_PRESERVED | Linhas do A | Linhas acrescentadas |
|---|---|---|---:|---:|
| `JURISPRUDENCIA.IDX` | YES | YES | 340 | 16 |
| `JUR_LOOKUP.IDX` | YES | YES | 222 | 16 |

## 5. Validação pós-escrita (bytes de D:\)

| Verificação | Resultado |
|---|---|
| SD_HASHES | PASS |
| MANIFEST_VS_SD | PASS |
| CARD_FILESET_MATCHES_B | YES |
| UNEXPECTED_SD_CHANGES | 0 |
| Arquivos substituídos / criados / apagados | 7 / 15 / 0 |
| Arquivos no cartão | 1175 → 1190 |
| JURIS_RELATIONS / JURIS_TARGETS | 315 / 198 (+16 vínculos, +12 targets) |
| A_RELATIONS_PRESERVED | 299/299 |
| Itens do A preservados nos targets com novos vínculos | True |
| Targets não afetados idênticos | True |
| Acrescentados = grupo B ratificado | True |
| CORRELATAS / REFERENCES4 / ENTENDA alterados | NO / NO / NO |
| Flags alteradas | E=0, C=0, J=12, W=0, R=0, X=0 |
| J = jurisprudência visível | True |
| R_FLAG_KNOWN_DIVERGENCE | 76. Só registro: nenhuma flag R mudou; o firmware não lê R |
| Tipos no índice legado (tipo/tribunal) | adi/STF 27, adpf/STF 4, ai/STF 1, ap/STF 1, hc/STF 2, inq/STF 2, ms/STF 3, rcl/STF 1, repercussao_geral/STF 296, sumula/STF 1, sumula/TSE 1, sumula_vinculante/STF 16 |
| REJECTED_RELATIONS_PUBLISHED | 0 (12 pares conferidos) |
| DUPLICATE / ALREADY_COVERED que criaram relação | 0 |
| UNRESOLVED_EXTERNAL_PUBLISHED (Súmula 403 STJ) | 0 |
| Provisórios no cartão | ADI 5017 (CAUTELAR), ADI 7697 (CAUTELAR), ADPF 378 (CAUTELAR), Rcl 84738 (PROVISÓRIA) |

## 6. Simulação do firmware GENÉRICO sobre os bytes do cartão

| Verificação | Resultado |
|---|---|
| GENERIC_FW_SIMULATION | PASS |
| NO_LABEL_OUTRO | YES |
| ALL_B_FICHAS_RESOLVE | YES |
| BACK_BEHAVIOR_SIMULATION | PASS |
| CACHE_LIMITS | PASS |
| IDs aceitos (lista de tribunais = coluna TRIBUNAL) | True |
| Limites | lookups 237/4096; itens visíveis por target 10/40; jurisprudências por target 10/32; regras do cache de boot OK |

**Rótulos obrigatórios encontrados:** `HC 232627`, `HC 70648`, `MS 21689`, `AP 694`, `AI 343461`, `Inq 4781`, `Rcl 84738 (PROVISÓRIA)`, `ADPF 378 (CAUTELAR)`, `ADPF 964`, `Súmula 9 TSE`.

| Target | Lista (firmware genérico) | OK |
|---|---|---|
| CF88:ART.52:PAR.UNICO | MS 21689 | PASS |
| CF88:ART.55:INC.VI | AP 694 | PASS |
| CF88:ART.35:INC.IV | ADI 7369, AI 343461 | PASS |
| CF88:ART.86 | MS 21564 | PASS |
| CF88:ART.86:PAR.1:INC.II | ADPF 378 (CAUTELAR) | PASS |
| CF88:ART.52:INC.I | ADPF 378 (CAUTELAR) | PASS |
| CF88:ART.96:INC.III | Rcl 84738 (PROVISÓRIA) | PASS |
| CF88:ART.53 | Inq 4781, RG TEMA 950 | PASS |
| CF88:ART.84:INC.XII | ADPF 964, RG TEMA 371 | PASS |
| CF88:ART.142:PAR.2 | HC 70648 | PASS |
| CF88:ART.15:INC.III | Súmula 9 TSE, RG TEMA 1190, RG TEMA 370 | PASS |
| CF88:ART.53:PAR.1 | HC 232627 | PASS |
| CF88:ART.29:INC.X | Súmula 702 STF | PASS |
| CF88:ART.62:PAR.6 | MS 27931 | PASS |
| CF88:ART.86:PAR.4 | Inq 672 | PASS |
| CF88:ART.198 | ADPF 672 | PASS |
| CF88:ART.86:PAR.3 | ADI 978 | PASS |
| ADCT:ART.107-A | ADI 7064 | PASS |

**Como o BACK foi simulado** (modelo do firmware, não teste físico):
1. Para cada target com jurisprudência, a lista é resolvida.
2. Cada item é "aberto": a ficha existe e o título não é OUTRO nem repete o tribunal da súmula.
3. O BACK re-resolve a lista a partir da origem salva.
4. A lista e o item selecionado precisam ser os mesmos.

**Por que o cartão não pode rodar no firmware atual:** com ele, 14 precedentes do grupo B apareceriam como "OUTRO n" ou nem seriam aceitos: OUTRO 21564, OUTRO 21689, OUTRO 232627, OUTRO 27931, OUTRO 343461, OUTRO 378 (CAUTELAR), OUTRO 4781, OUTRO 672, OUTRO 694, OUTRO 702, OUTRO 70648, OUTRO 84738 (PROVISÓRIA), OUTRO 9, OUTRO 964.

## 7. Testes host

| Suíte | Resultado |
|---|---|
| Jurisprudência (inclui tipos, J2F, J2H e gate de provisórios) | 102/102 |
| Motor de referências | 90/90 |
| Referências nº 4 | 15/15 |
| Correlatas | 115/120; as 5 falhas históricas são as mesmas, nome a nome. NEW_REGRESSION = 0 |

## 8. Preparação da J2I (flash controlado; NADA foi gravado)

| Item | Valor |
|---|---|
| Porta esperada | COM3: USB-Enhanced-SERIAL CH343 (VID:PID 1A86:55D3), conforme o registro R2. Detecção: listar as portas e confirmar o VID:PID; depois `esptool --chip esp32s3 -p COMx flash-id` (ESP32-S3 QFN56 rev v0.2, 8 MB de PSRAM, flash de 16 MB, MAC e0:72:a1:f4:fd:28) |
| Board / FQBN | `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default` |
| Core | esp32:esp32 3.3.11 (arduino-cli 1.5.1) |
| Opções | `--build-property compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1` |
| Fonte | `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE` + `JURIS_TYPE_PROTOTYPE/juris_types.patch` (9 edições) |
| Binário genérico congelado | `DEVICE_INTEGRATION/backups/j2i_flash_candidate/generic_app.bin` (fora do Git) |
| SHA-256 do app genérico | `1371e69a0ef3b16773c36e240b166ee99f73d48c2629d11ebf09191701de2b6c` |
| Tamanho | app 1102176 B; programa 1102031 B; RAM estática 126148 B; partição app0 de 1310720 B, livres 208544 B |
| Tabela de partições | build genérico = `148b959c…` = a do aparelho (registro R2): gravar **só o app0 em 0x10000** |
| Firmware físico atual | app `6e329c91…` (R2). Cópia: `DEVICE_INTEGRATION/backups/j2i_flash_candidate/current_approved_app_6e329c91.bin`; imagem anterior ao R2: `DEVICE_INTEGRATION/backups/references4_r1_physical_deploy/fw/app0_pre.bin` |
| Antes do flash (J2I) | ler o app0 inteiro (0x10000, 1.310.720 B) e conferir que contém `6e329c91…`; ler partitions, otadata e nvs; gravar os hashes |
| Comando (modelo R2) | `esptool --chip esp32s3 -p COMx -b 460800 --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 generic_app.bin`, depois readback do app0 e conferência do sha; partitions e otadata devem ficar inalterados |
| Recuperação | `write-flash 0x10000 current_approved_app_6e329c91.bin` + readback, com o cartão revertido para A (seção 4). Firmware antigo + cartão B: NÃO usar |
| Smoke tests pós-flash | boot; rótulos HC 232627 (art. 53, § 1º), HC 70648 (art. 142, § 2º), MS 21689 (art. 52, p.u.), AP 694, AI 343461, Inq 4781, Rcl 84738 (PROVISÓRIA), ADPF 378 (CAUTELAR) em dois targets, ADPF 964, Súmula 9 TSE, Súmula 702 STF; abrir a ficha e voltar com BACK; regressão do A (Tema 793, SV 46, ADI 7064 no 107-A, ADI 5017, ADI 7697, Tema 558); Correlatas, Referências nº 4, ENTENDA; nenhum OUTRO |

## 9. Ferramentas e evidências

- **Pacote:** `build_j2h_candidate.py`.
- **Deploy:** `deploy_j2h_sd.py` (`pre`, `copy`, `verify`).
- **Checagem semântica:** `semantic_check_j2h_sd.py`.
- **Testes:** `tests/test_j2h.py`.
- **Evidências:** `JURISPRUDENCE_AUDIT/J2H_PHYSICAL_DEPLOY/`.
- **Backups:** `DEVICE_INTEGRATION/backups/juris_j2h_physical_deploy/` e `DEVICE_INTEGRATION/backups/j2i_flash_candidate/` (fora do Git).
