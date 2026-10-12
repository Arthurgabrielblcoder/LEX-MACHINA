# C3B.1 — relatório do teste físico

**`C3B1_PHYSICAL_TEST = FAIL_RESIDUAL`** (12/15 PASS, 2 PARTIAL_FAIL, 1 FAIL). O C3B.1 NÃO foi promovido a baseline.

- O relatório do C3B (`C3B_PHYSICAL_TEST_FAILURE_REPORT.md`) continua como evidência separada.

| # | Onde | Observado | Resultado |
|---|---|---|---|
| 1 | CF art. 5º, XLIII | Lei 13.260/2016 aparece e abre | `PASS` |
| 2 | CF art. 202, § 5º | LC 108/2001 abre direto no art. 26 | `PASS` |
| 3 | CF art. 158, § 1º, I | LC 63 aparece e abre a partir do art. 3º (esperava-se o início) | `PARTIAL_FAIL_WRONG_DESTINATION_LC63` |
| 4 | CF art. 158, § 1º, II | `1 CORR.` não aparece | `PASS` |
| 5 | CF art. 161, I | LC 63 aparece e abre a partir do art. 3º (esperava-se o início) | `PARTIAL_FAIL_WRONG_DESTINATION_LC63` |
| 6 | CF art. 202, § 1º | LC 109/2001 abre no art. 3º | `PASS` |
| 7 | CF art. 202, caput | LC 109/2001 continua aparecendo | `FAIL_LC109_STILL_PUBLISHED_AT_ART202_CAPUT` |
| 8 | CF art. 214, caput | Lei 15.388/2026 aparece | `PASS` |
| 9 | CF art. 214, I a VI | sem `1 CORR.` fantasma | `PASS` |
| 10 | CF art. 150, § 7º | LC 87/1996 abre no art. 10 | `PASS` |
| 11 | CF art. 239, § 3º | correlata aparece e abre | `PASS` |
| 12 | CF art. 37, § 3º, III | `1 CORR.` não aparece | `PASS` |
| 13 | CF art. 37, II | correlata indevida não aparece | `PASS` |
| 14 | CF art. 131, § 2º | Lei 14.965/2024 não aparece | `PASS` |
| 15 | CF art. 132 | Lei 14.965/2024 não aparece | `PASS` |

- **Partial fail:** testes 3 e 5.
- **Fail:** teste 7.
- **Diagnóstico posterior:** `C3B2/C3B2_ROOT_CAUSE_REPORT.md`. As três divergências são de expectativa, não de dados.

## Candidato testado (6 arquivos instalados, hashes confirmados no cartão)

- `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` = `d2fcc15bbe41ef16c51bbe1ef7cb201bd9677b6ac54198b96ad2abc08395e06c`
- `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` = `27c67eea6a38e3cba012d4a3d02c3856d37fd4cd1bae15473854fab0edea5430`
- `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` = `1762642d337aff83ac5b95e074235bc58028b8a68bac17a384e9eed4a4a5addd`
- `99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX` = `5c54face7ea7eff62dbbb0a4193b5e2452e7fb03d82012d09919e74d234b3e5e`
- `99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX` = `691790f3ee5d4aaa9b88235bca33008357b99d87324c07b1da8b51355c20685c`
- `99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX` = `efac06cee0a1d8f0676564ba128d0ab8f474b89399f40de6422cc6fded37ef2c`

## Rollback físico

- **Antes:** 6/6 C3B.1 no cartão.
- **Restauração:** conjunto completo → 6/6 BASELINE EXACT.
- **Escopo da escrita:** 6 arquivos alterados na sessão, de 1142.
  - `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` = `616a469b11dd673347dc665232a83fc8d5bcd8e3c6bfd5f07a4a56c62f5972a7`
  - `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` = `6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8`
  - `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` = `24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea`
  - `99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX` = `a156a2d6c1546fd1f692f0dfec19c15a728621647dce467632caca91b7c1ecad`
  - `99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX` = `bb3c37168829f4fc102ad51f8fd413f8c8658785181c46888e4d3d76c64af96d`
  - `99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX` = `863ff5383d9b338fef2e980edb7972953fe57943e170e42d909e9c7c4ddb4b7e`
- **Inalterados:** LEXV1.VER 2be2e369…, LEX_DEVICE_MANIFEST.json 7394cb6a….
- **Estado final:** cartão de volta ao baseline físico; firmware inalterado; nenhum candidato reinstalado.

