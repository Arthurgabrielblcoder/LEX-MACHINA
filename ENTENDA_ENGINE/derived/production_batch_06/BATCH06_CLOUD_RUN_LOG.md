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

---

# Atualização — Rodada D (revisão jurídica humana dos 11 itens D, 2026-10-05)

Missão `BATCH06_FULL_HUMAN_REVIEW_D_RESOLUTION`, branch `batch06-scale-cloud`, a partir de `5ce9f21` (descendente direto, sem rebase, merge ou force push).

## Decisões

- **Aprovados sem alteração jurídica (v1 mantida):** art. 51, I e art. 52, X.
- **Ajustados e aprovados (v2; v1 preservada como RETIRED/CHANGES_REQUESTED):** art. 52, p. único; art. 53, caput, § 1º e § 2º; art. 55, VI; art. 58, § 3º; art. 62, § 6º; art. 63; art. 75.
- **Rejeitados:** 0.
- Os 11 passaram pelo portão de aprovação do builder: contrato do motor, validator v3 sem HARD_FAIL e sem REVIEW_REQUIRED aberto, editorial_checks sem achado aberto.
- **Acervo HUMAN_APPROVED_T1:** 289 → **300**. Batch06 novos pendentes: **82** (A 42, B 27, C 13, não decididos).

## Fontes externas

- Registradas como `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE` (indicadas pela revisão humana) e como recomendações `PENDING_EXTERNAL_INGESTION` em `JURISPRUDENCE_LINK_RECOMMENDATIONS.json`.
- **Conferência direta nos portais oficiais: NÃO EXECUTADA.** O egress da VM bloqueia STF, Planalto e Câmara (curl e WebFetch: `connect_rejected`). Nenhum conteúdo externo foi acrescentado por memória.
- A EC 139/2026 tem evidência versionada no repositório:
  - a compilação oficial do Senado (`updater/fontes_oficiais_senado/CF88`) contém a vedação no art. 31, § 1º, e no art. 75;
  - a fonte canônica estrutural anota "Redação dada pela Emenda Constitucional nº 139, de 2026" nos dois dispositivos.
- Data de promulgação (5/5/2026) e finalidade vêm da revisão humana.

## Suítes (Python 3.12)

| Suíte | Resultado |
|---|---|
| ENTENDA completa | **PASS**: 180 testes (2 skips: candidato host do Batch05; integração opcional com o Relations Engine local) |
| Batch06 | **PASS**: 28 |
| validator v2 | **PASS**: 18 (1 skip) |
| Batch05 | **PASS**: 26 (1 skip) |
| ENTENDA engine | **PASS**: 19 |
| resolver hermético | **PASS**: 9 |
| materialização Git | **PASS**: 2 testes; 217/217 arquivos byte-idênticos; com `core.autocrlf=true`, ENTENDA sem falha fora dos 4 testes `requires_git_checkout` |
| editorial_checks | **PASS**: 0 abertos |
| validator v3 | regras novas com 0 alertas nos 289 aprovados anteriores e nos 82 pendentes; regressão do Batch05 sem perda (41/43 verdadeiros positivos) |
| determinismo do builder | **PASS**: 3 builds + build no lugar byte-idênticos |

## Contabilidade explícita (`ENTENDA_ENGINE/cloud_test_accounting.py`)

Cada método de teste cai em exatamente uma categoria; a soma bate com o total.

| Suíte | Total | PASS | FAIL | SKIPPED | NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY | NOT_COLLECTED |
|---|---|---|---|---|---|---|
| DEVICE_INTEGRATION | **353** | 120 | 2 | 136 | 68 | 27 |
| LEGAL_TARGET_ID | **65** | 63 | 1 | 0 | 1 | 0 |

**DEVICE_INTEGRATION** (detalhe por teste em `DEVICE_INTEGRATION_CLOUD_ACCOUNTING.json`):

- **NOT_RUN 68:**
  - 59 dependem do staging local do SD (`staging_sd_v1/…`, `staging_article_indexes…`): falhas e setUpClass.
  - 9 comparam o firmware com tags só locais, ausentes no remoto: `lex-device-v1-physical-approved-2026-10-01` e `lex-device-v1-72-indexes-approved-2026-10-04`.
- **NOT_COLLECTED 27:** `test_fast_track_ui`, `test_reader_state_machine` e `test_target_sync` não importam sem `staging_sd_v1/.../CF88_RUNTIME.txt`. Os métodos foram contados estaticamente.
- **SKIPPED 136:** os próprios testes pulam por staging, dump de flash, backup do SD ou core do ESP32 ausentes. Não estão contados como PASS.
- **FAIL 2:** `test_predeploy_a2c` `test_ec45_cross_source` e `test_fail_closed`. A cópia versionada `updater/fontes_oficiais_verificacao/EC45_2004/planalto_raw.html` tem sha `0c46fc85…` e o registrado é `76f9b562…`; nem a variante CRLF bate. É inconsistência preexistente do repositório (mesma falha no checkpoint `7c59f2e`), fora do escopo do Batch06.
- **Ambiente:** `requests` e `beautifulsoup4` foram instalados no Python do usuário da VM (não no repositório), para que `test_runtime_a2b` rodasse (PASS).
- **Correção do relatório anterior:** "111/282" contava só o que o unittest executou. O total real é 353 (282 executados + 27 não coletados + 44 testes que nunca rodaram porque o setUpClass falhou).

**LEGAL_TARGET_ID:**
- **NOT_RUN 1:** `CF_SEGMENTADA_V2/` local.
- **FAIL 1:** `test_source_hash` espera o `cf.txt` legado materializado em CRLF (checkout Windows). O blob do Git é LF; LF→CRLF reproduz o hash esperado. É dependência de ambiente de checkout, não do Batch06.
