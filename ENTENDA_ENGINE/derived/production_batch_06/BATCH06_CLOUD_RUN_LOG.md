# BATCH06 — registro da execução Cloud (recalibração de risco, 2026-10-05)

Missão `BATCH06_SCALE_RISK_RECALIBRATION`, branch `batch06-scale-cloud`, sobre o checkpoint WIP `7c59f2e` (base `main` = `f1a6966`).
Executado numa VM remota com o clone do GitHub, Python 3.12. **Nenhum ENTENDA aprovado**: 0 novos `HUMAN_APPROVED_T1`.

Este arquivo não é gerado pelo builder: registra as suítes rodadas e o que não pôde rodar fora da máquina local.

## Pré-condições verificadas

- branch `batch06-scale-cloud`, working tree limpo, `origin/main` = `f1a6966ad35e5786a88e1f4806cef6bf1a65d3ba`;
- HEAD inicial `7c59f2e` (1 commit à frente de `main`, descendente direto);
- hashes do estado WIP em `PRE_RECALIBRATION_MANIFEST.json`;
- tag `entenda-batch05-t1-frozen-2026-10-04` → `342ab9a`, não movida.

## Suítes

| Suíte | Resultado no Cloud |
|---|---|
| ENTENDA completa (`ENTENDA_ENGINE/tests`) | **PASS** — 176 testes, OK (2 skips: candidato host do Batch05 não construído; integração opcional com pastas locais do Relations Engine) |
| Batch06 (`test_entenda_batch06`) | **PASS** — 24 testes |
| validator v2 (`test_t1_validator_v2`) | **PASS** — 18 testes (1 skip opcional) |
| Batch05 (`test_entenda_batch05`) | **PASS** — 26 testes (1 skip: candidato host) |
| resolver externo hermético (`test_t1_external_resolver`) | **PASS** — 9 testes |
| materialização Git (`test_git_materialization` + `git_materialization_check.py --source HEAD`) | **PASS** — 2 testes; 210/210 arquivos críticos byte-idênticos, 836/836 blocos de payload, 10 pares de índice |
| materialização com `core.autocrlf=true` + suítes na árvore materializada | **PASS** para ENTENDA (todas as falhas restantes são as 4 listadas como `requires_git_checkout`, que precisam de `git diff`/`git show`) |
| editorial_checks (Batch06) | **PASS** — 0 achados abertos (13 falsos positivos resolvidos com justificativa) |
| determinismo do builder | **PASS** — 3 builds completos + build no lugar byte-idênticos (`DETERMINISM_EVIDENCE.json`) |
| LEGAL_TARGET_ID | **63/65 PASS**; 2 = `NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY` (abaixo) |
| DEVICE_INTEGRATION | **111/282 PASS** no Cloud, 136 skips; 35 = `NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY` (abaixo). Conjunto de falhas idêntico ao do checkpoint intocado `7c59f2e` rodado no mesmo ambiente |

## NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY

Não contam como PASS.

| Item | Motivo |
|---|---|
| LEGAL_TARGET_ID `test_superset_of_v2_segmentation_keys` | precisa de `CF_SEGMENTADA_V2/CF_DISPOSITIVOS_LIMPOS.json` (pasta local não versionada) |
| LEGAL_TARGET_ID `test_source_hash` | espera o sha256 do `cf.txt` legado materializado em CRLF (`d9f3d6b9…`, checkout Windows com autocrlf); o blob do Git é LF (`0742175b…`). Conferido: LF→CRLF reproduz `d9f3d6b9…` |
| DEVICE_INTEGRATION (28 erros) | staging local do SD não versionado (`DEVICE_INTEGRATION/staging_sd_v1/…`, `staging_article_indexes_full_corpus_candidate/…`) |
| DEVICE_INTEGRATION (6 falhas "flag0/sketch untouched") | comparam o firmware com a tag local `lex-device-v1-physical-approved-2026-10-01`, que não existe no remoto |
| DEVICE_INTEGRATION `test_ec45_cross_source` | cópia de verificação da EC 45 com bytes da máquina local (sha divergente no clone) |
| Atualização do `BATCH06_RELATIONS_PIN.json` para todo o escopo | exige as pastas de trabalho do Relations Engine (`LEX-MACHINAETAPA_2D4/2E41`); o pin atual tem só a relação registrada no checkpoint (art. 45, § 1º) |
| ESP32, microSD, firmware conectado, staging/teste físico | fora do alcance da VM |

## Reprodutibilidade

- O texto operacional da CF (ignorado pelo Git) é reconstruído byte a byte do conteúdo versionado: sha256 `3100e097…`, igual ao de todos os registros ENTENDA (ver `ENTENDA_ENGINE/REPRODUCIBILITY.md`).
- `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` reconstrói o Batch06 inteiro sem os scripts temporários `b06_*`.
- O Relations Engine entra pelo pin versionado, em qualquer ambiente; o build não depende das pastas locais.
- Os scripts e o código exigem Python ≥ 3.12 (f-strings com barra invertida, já presentes em `t1_triage.py` antes desta missão). O Python 3.11 padrão da VM não importa `t1_triage.py`.
