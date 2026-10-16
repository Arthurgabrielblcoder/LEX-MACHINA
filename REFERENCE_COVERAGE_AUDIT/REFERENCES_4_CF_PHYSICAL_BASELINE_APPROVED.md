# REFERÊNCIAS Nº 4 — CF: baseline físico aprovado

**`REFERENCES_4_PHYSICAL_BASELINE_PROMOTION = PASS`.** O LEX MACHINA (ESP32 e microSD) roda o candidato R1, instalado na R2, e o teste físico humano passou em **8/8**. Esse estado passa a ser o baseline físico oficial. Ele contém CORRELATAS 1 (C3B.2) e REFERÊNCIAS Nº 4 sem regressão.

```
LAYER = REFERENCES_4_CF
PHYSICAL_VALIDATION = PASS · PHYSICAL_TESTS = 8/8 (relato humano, 2026-10-16)
BASE_PHYSICAL = C3B.2 (tag lex-device-v1-correlata-c3b2-physical-approved-2026-10-12)
SD_BUILD_ID = 5eb2a9298c1edbd6 (GIT_COMMIT 453922ffcbc5d15fb9bed832a9cfa5206348e3df, REFERENCE_ENGINE cf-reference-engine-run5-references4-r1)
FIRMWARE_APP_SHA256 = 6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c (1.101.136 B em app0 0x10000)
LEX_DEVICE_MANIFEST_SHA256 = 7b8da57d943aef59f6dda55f1eb86484b516f7170da7074e3638949c7ce292fb
```

## 1. Teste físico humano (R2): 8/8 PASS

| # | Teste | Resultado |
|---|---|---|
| 1 | Boot | PASS: boot normal |
| 2 | CF art. 37 → `4 REF.` (referências antigas) | PASS: obras antigas e ficha corretas. O teste foi feito primeiro, por engano, no art. 47; isso não conta como falha, e o teste foi repetido no art. 37 |
| 3 | CF art. 196 → **Sicko - S.O.S. Saúde** | PASS: aparece e a ficha abre |
| 4 | CF art. 206, I → **Pro Dia Nascer Feliz** | PASS: DOCUMENTÁRIO, 2005, João Jardim |
| 5 | CF art. 206 caput e art. 206, II | PASS: sem `4 REF.` indevido |
| 6 | CORRELATA: CF art. 202, § 5º → LC 108/2001, art. 26 | PASS |
| 7 | CF art. 37, § 3º, III | PASS: sem `1 CORR.` |
| 8 | ENTENDA: CF art. 127 | PASS |

## 2. Verificação final somente de leitura (2026-10-16)

Evidência em `R2_PHYSICAL_DEPLOY/final_physical_verification.json`. Os dumps estão fora do Git, em `DEVICE_INTEGRATION/backups/references4_final_promotion/`.

**Firmware.** O app0 foi lido duas vezes (`esptool 5.4.0`, COM3 CH343, `--after no-reset`), com leituras idênticas (`dde8fa29…`). Os primeiros 1.101.136 B são `6e329c91…`, o que dá **`PHYSICALLY_TESTED_FIRMWARE = EXACT`**.

- Partições: `148b959c…`.
- otadata: `f94c5d78…`.
- Ambos inalterados desde antes da R2.

**SD.**

- `PHYSICALLY_TESTED_SD_BYTES = 5/5 EXACT`.
- O cartão inteiro (1.142 arquivos) é idêntico ao `R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json`.
- `MANIFEST_VS_SD = PASS`, com 10 entradas conferidas.
- RELACOES, REL_LOOKUP e EXT_ARTIGOS são idênticos ao C3B.2.
- Nenhum outro arquivo difere do C3B.2 além dos 5 da R2.

**Nesta promoção:** `SD_WRITES_THIS_MISSION = 0` e `FIRMWARE_FLASH_THIS_MISSION = NO`.

## 3. Arquivos SD do baseline

| Arquivo | SHA-256 |
|---|---|
| `/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | `da49c43b7a21990334a6a1af63fbc605fec7fde195a06a2014776285455006eb` |
| `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | `efabb245e3beb8b63df33249a7a2e3c178aace02b361d9d344cb348d0fa823a0` |
| `/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | `d4e3342b99f5a5efb732eb9b36f786f3eaf5a33ab651500c7ce8a387bfe593f7` |
| `/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | `7b8da57d943aef59f6dda55f1eb86484b516f7170da7074e3638949c7ce292fb` |
| `/99_LEX_V1/00_SYS/LEXV1.VER` | `edaf6147767ceece3fdd3149b63d79037e8e06a9de8ca71e3589da88a3758125` |
| `/99_RELATIONS_V2/05_INDICES_ESP32_V2/{RELACOES,REL_LOOKUP,EXT_ARTIGOS}.IDX` | inalterados, iguais ao C3B.2 |

**Para o próximo deploy:** o manifesto físico completo deste baseline é `REFERENCE_COVERAGE_AUDIT/R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json`, com cópia de bytes em `DEVICE_INTEGRATION/backups/references4_r1_physical_deploy/`. Ele passa a ser a referência de pré-deploy. `promoted_sys/` guarda os bytes de `LEXV1.VER` e do manifesto do aparelho.

## 4. Estado editorial (contado nos bytes do cartão)

- **WORK_REFERENCE** (`CURRENT_VISIBLE`): **124**, contra 122 no C3B.2.
- **Obras usadas:** **56**, contra 54.
- **Targets com W:** **65**, contra 63. É igual ao número de targets com obra no payload.

**Adições da rodada final** (P20 e P21 do REFERENCE_EXPANSION_01, aprovadas em 2026-10-02 e retidas até a R1A):

- **Sicko - S.O.S. Saúde** (`R1A-DOC-001`) → CF art. 196.
  - DOCUMENTÁRIO, 2007, direção de Michael Moore.
  - Fontes: Festival de Cannes 2007 (tier B) e AdoroCinema (C).
- **Pro Dia Nascer Feliz** (`R1A-DOC-002`) → CF art. 206, I.
  - DOCUMENTÁRIO, direção de João Jardim.
  - **Ano autoritativo 2005**, pelo arquivo institucional da Mostra Internacional de Cinema de São Paulo (29ª Mostra), por decisão do usuário.
  - As divergências 2006 (UFMG, Guia da Semana, proposta P21) e 2007 (Dartmouth, lançamento comercial) estão preservadas em `ano_decisao`, no `R1A_WORK_IDENTITY_CATALOG.json`.

**`PREVIOUS_WORK_REFERENCE_SET_PRESERVED = PASS`.** Os 122 vínculos anteriores continuam iguais, linha a linha no `REF_PAYLOAD`. A rodada adicionou exatamente +2, sem remover nem alterar nada (`REFERENCES_4_R1_ISOLATION_AUDIT.json`).

## 5. CORRELATAS 1: `CORRELATAS_1_REGRESSION = PASS`

- RELACOES, REL_LOOKUP e EXT_ARTIGOS estão byte-idênticos ao C3B.2.
- O conjunto, os IDs, as rotas e os destinos de CORRELATA não mudaram (0/0/0/0).
- As flags C não mudaram: 24, iguais às CORRELATA visíveis.
- Testes físicos 6 e 7 PASS.
- Correlatas 1 não foi reaberta.

## 6. Dívidas registradas (não tratadas, sem alteração oportunista)

**`PREEXISTING_CORRELATA_TEST_DEBT = 4`.** Quatro testes de reconstrução/hash da suíte histórica de Correlatas falham igualmente num checkout limpo de `af8f68d`:

- C0 `test_committed_artifacts_are_the_build`;
- C3A.1 `test_15_run4_and_package_deterministic`;
- C3B.1 `test_reproducible`;
- C3B.2 `test_c3b2_package_reproducible_and_equal_device_bytes`.

Não são regressão de Referências, e nenhum relatório histórico foi alterado.

**Flag R** (`CF88_TARGETS.IDX`, posição [4]). Não foi recalculada nesta rodada, e o firmware não a lê. A divergência R-only em relação ao gerador de staging passou de 23 para 25: os targets `CF88:ART.196` e `CF88:ART.206:INC.I` ganharam linha no `REF_LOOKUP` com R=`-`. Isso fica registrado como dívida técnica conhecida.

## 7. Firmware

- `FIRMWARE_LOGIC_CHANGED = NO`.
- `FIRMWARE_DATA_CHANGED = YES`: a tabela `lex_ref_detail_data.h` passou de 122 para 124 fichas. As 122 antigas ficaram byte-idênticas.
- O header aprovado continua em `LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate/device_candidate/lex_ref_detail_data.RUN5_CANDIDATE.h` (sha `e420f4de…`).
- O sketch versionado em `firmware/` **não** foi substituído, porque o guard de Correlatas 1 proíbe modificar essa pasta. O app gravado foi compilado a partir de uma cópia do sketch com esse header.
- Binário: `DEVICE_INTEGRATION/backups/references4_r1/build_cand/`, fora do Git, com sha `6e329c91…`.

## 8. Rollback

| Alvo | Como restaurar |
|---|---|
| **SD** (volta ao C3B.2) | Restaurar os 5 arquivos de `DEVICE_INTEGRATION/backups/references4_r1_physical_deploy/sd_pre/`. Também estão versionados em `REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/rollback/SD/` |
| **Firmware** (volta ao app `445fdb7f…`) | `esptool --chip esp32s3 -p COM3 -b 460800 --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/backups/references4_r1_physical_deploy/fw/app0_pre.bin`, seguido de readback. NVS em `fw/nvs_pre.bin` |

## 9. Trilha (preservada)

- **R0:** `REFERENCIAS_4_CF_RESUME_CHECKPOINT.md`.
- **R1/R1A:** `REFERENCES_4_R1_FINALIZATION_REPORT.md`, `R1A_WORK_IDENTITY/`, `REFERENCE_REGISTRY/WORK_REGISTRY_V3.json`, RUN5 e `REFERENCES_4_R1_ISOLATION_AUDIT.json`.
- **Pacote:** `REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/`.
- **R2:** `REFERENCES_4_R2_DEPLOY_REPORT.md` e `R2_PHYSICAL_DEPLOY/`.
- **Congelamento:** `REFERENCES_4_CF_FROZEN.md`.
