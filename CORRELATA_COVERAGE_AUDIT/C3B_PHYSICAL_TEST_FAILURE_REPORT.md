# C3B — relatório de falha do teste físico

**`C3B_PHYSICAL_TEST = FAIL`.** O C3B NÃO foi aprovado.

| # | Onde | Observado | Resultado |
|---|---|---|---|
| 1 | CF art. 5º, XLIII | Lei 13.260/2016 aparece e abre | `PASS` |
| 2 | CF art. 202, § 5º | LC 108/2001 aparece, mas abre no início (não no art. 26) | `FAIL_WRONG_DESTINATION_ARTICLE` |
| 3 | CF art. 158, § 1º, I / II | LC 63 não aparece no I; `1` aparece no II e não abre nada | `FAIL_STALE_LAYER_FLAG_AND_MISSING_NEW_FLAG` |
| 4 | CF art. 161, I | substituição LC 62 → LC 63 funciona | `PASS` |
| 5 | CF art. 202, § 1º | LC 109 não aparece no § 1º; continua no caput (abre no início) | `FAIL_STALE_TARGET_FLAGS` |
| 6 | CF art. 214 | não aparece no caput; `1` nos incisos I–VI não abre nada | `FAIL_STALE_TARGET_FLAGS` |
| 7 | CF art. 150, § 7º | LC 87/1996 abre no art. 10 | `PASS` |
| 8 | CF art. 239, § 3º | nenhuma correlata; só ENTENDA | `FAIL_MISSING_NEW_TARGET_FLAG` |
| 9 | CF art. 37, § 3º, III | `1` aparece; pressionar `1` não abre nada | `FAIL_STALE_TARGET_FLAG_ART37_PAR3_INCIII` |
| 10 | Lei 14.965 (arts. 131 § 2º, 132, 37 II) | não aparece em 131 § 2º e 132; no 37 II `1` aparece e não abre nada | `FAIL_STALE_TARGET_FLAG_ART37_II` |
| 11 | Outras camadas | não executado | `NOT_EXECUTED` |

- **Passes:** testes 1, 4 e 7.
- **Falhas:** testes 2, 3, 5, 6, 8, 9 e 10 (parcial).
- **Não executado:** teste 11.
- **Teste 9:** executado e confirmado como `FAIL_STALE_TARGET_FLAG_ART37_PAR3_INCIII`.
- **Teste 5:** a LC 109 no caput do art. 202 é um vínculo legado mantido (KEEP), então aparecer ali é o esperado. A falha é a ausência no § 1º.

## Rollback físico

- **Identificação do cartão:** D:\ (BUILD_ID de963699728cb66e; GIT_COMMIT fa9719a6; REFERENCE_ENGINE cf-reference-engine-run3).
- **Antes:** candidato C3B encontrado em 5/5.
- **Restauração:** o conjunto completo dos 5 arquivos voltou a 5/5 BASELINE EXACT.
- **Escopo da escrita:** 5 arquivos alterados na sessão, de 1142 no cartão.
  - `99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX` = `a156a2d6c1546fd1f692f0dfec19c15a728621647dce467632caca91b7c1ecad`
  - `99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX` = `bb3c37168829f4fc102ad51f8fd413f8c8658785181c46888e4d3d76c64af96d`
  - `99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX` = `863ff5383d9b338fef2e980edb7972953fe57943e170e42d909e9c7c4ddb4b7e`
  - `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` = `6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8`
  - `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` = `24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea`
- **Inalterados:** LEXV1.VER 2be2e369…, LEX_DEVICE_MANIFEST.json 7394cb6a…, CF88_TARGETS.IDX 616a469b… (baseline).
- **Estado final:** o cartão voltou ao baseline físico aprovado. Nenhum candidato foi reinstalado.

