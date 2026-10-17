# PARTE D — Dívida do header de firmware (122 × 124 fichas)

```
FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE = PASS
FIRMWARE_FLASHED = NO · MICROSD_TOUCHED = NO
```

## D1. Diagnóstico

| Item | Valor |
|---|---|
| Arquivo antigo | `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h`, **122 fichas**, sha256 (LF) `2ca5820a…` |
| Último commit do arquivo antigo | `10e199f` (2026-10-03, "approve Batch04 and RUN3 physical baseline") |
| Arquivo correto | `LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate/device_candidate/lex_ref_detail_data.RUN5_CANDIDATE.h`, **124 fichas**, sha256 (LF) `e420f4de…f55f8` |
| Origem do arquivo correto | commit `b5ccf96` (2026-10-15, R1 de Referências nº 4) |
| Commit físico | `2a3cf60` (R2: firmware gravado; `REFERENCE_COVERAGE_AUDIT/R2_PHYSICAL_DEPLOY/firmware_flash.json`), app aprovado `6e329c91…` (1.101.136 B) |

**Por que `firmware/` ficou defasado:**

- O R1/R2 compilou o app a partir de uma cópia temporária do sketch com o header candidato de 124 fichas.
- O header nunca foi copiado de volta para `firmware/`.
- Os guards de isolamento das Correlatas proíbem qualquer diff em `firmware/` desde `9108d72`, e isso desencorajou a atualização. São eles:
  - `test_correlata_c3a1_c3b_prep.test_14`;
  - `test_correlata_c3a_engine.test_16`;
  - `C3A/tools/build_c3b_package.isolation`.

## D2. Correção

- **Header:** `firmware/…/lex_ref_detail_data.h` foi substituído pelo header de 124 fichas, sem outras alterações no sketch.
- **Guards:** os três guards aceitam agora apenas esse arquivo, e só com o sha256 LF `e420f4de…` fixado (`authorized_firmware_header_update`). Qualquer outra mudança em `firmware/` continua falhando.
- **Correlatas:** os dados e os pacotes não foram regenerados.

## D3. Recompilação e comparação

Para recompilar, rodar `python JURISPRUDENCE_AUDIT/FIRMWARE_REPRODUCIBILITY/verify_firmware_baseline.py`. O script:

- compila `firmware/` como está, sem o patch HC;
- usa a FQBN `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default` e o flag `-DLEX_DEVICE_V1_ENABLED=1`.

| Medida | App aprovado (R2) | Recompilado de `firmware/` |
|---|---|---|
| sha256 | `6e329c91…` | `5f014836…` |
| Bytes | 1.101.136 | 1.101.136 |
| Programa | 1.100.991 | 1.100.991 |
| RAM estática | 126.148 | 126.148 |
| Bytes diferentes | — | 70, todos de metadado |

Os 70 bytes diferentes ficam todos em metadados de build:

- SHA do ELF em `esp_app_desc` (0xb0–0xd0);
- `__TIME__`/`__DATE__` do banner "Software Info";
- checksum e sha final da imagem.

Resultado completo em `FIRMWARE_BASELINE_REPRODUCIBILITY.json`.

## Correlatas após a correção (Parte M antecipada)

| Módulo | Falha | Classificação |
|---|---|---|
| c0 | `test_committed_artifacts_are_the_build` | PREEXISTING |
| c3a1_c3b_prep | `test_15_run4_and_package_deterministic` (FAIL de asserção, como antes; o ERROR de isolamento foi eliminado) | PREEXISTING |
| c3a_engine | `test_16` (`DEVICE_INTEGRATION/_tmp_det_1.log`, não rastreado) | PREEXISTING |
| c3b1 | `test_reproducible` | PREEXISTING |
| c3b2 | `test_c3b2_package_reproducible_and_equal_device_bytes` | PREEXISTING |

- **Nova regressão:** nenhuma (`NEW_REGRESSION = 0`).
- **Demais módulos:** c1a, c1b_batch01/02, c1b_high_closure, c2, c3b2_promotion e legacy_review passaram (OK).

**Efeito no protótipo HC:** o protótipo já usava o header de 124 fichas, agora idêntico ao de `firmware/`. A base do patch HC passa a ser o próprio `firmware/`.
