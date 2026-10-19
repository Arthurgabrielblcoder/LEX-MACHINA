# Baseline físico multinorma após o CC-J2 (checkpoint de freeze)

```
BASELINE_ID = MULTINORM_FROZEN_CF315_198_CC49_39   (J2I_FROZEN_315_198 + CC_J2_FROZEN_49_39)
CF/ADCT = 315 / 198 · CC2002 = 49 / 39 (CC-J1 29/24 + CC-J2 20/+15) · TOTAL = 364 / 237
CC_J2_PHYSICAL_VALIDATION = 38/38 PASS (usuário, 2026-10-19) · FIRMWARE = multinorma 38c4d71f… (sem novo flash)
TIPOS VALIDADOS FISICAMENTE AGORA: REPETITIVO STJ, IAC (juris_types.PHYSICAL_VALIDATION_RECORDS, metadado)
```

- **Cartão:** 1.230 arquivos (manifesto `CC_J2_PHYSICAL_DEPLOY/sd_manifest_post_full.json`). Camada 06_NORMALIZADO com JURISPRUDENCIA.IDX `d2f23058…` e JUR_LOOKUP.IDX `5d88ce3b…`.
- **Registros:** `CC_J2_PHYSICAL_DEPLOY/CC_J2_PHYSICAL_VALIDATION.json`, `CC_J2_RATIFICATION_RECORD.json` e `CC_J2_PHYSICAL_DEPLOY_REPORT.md`.
- **Rollback de dados para 29/24:** `deploy_cc_j2_sd.py rollback`, com o backup PRE fora do Git.
- **Fila não física da CF:** 9 relações ratificadas aguardando materialização futura, fora deste baseline.
- **Tag física:** não foi criada nesta etapa. Fica para o usuário, se quiser, na convenção `lex-device-v1-juris-cc-j2-physical-approved-<data>`.
