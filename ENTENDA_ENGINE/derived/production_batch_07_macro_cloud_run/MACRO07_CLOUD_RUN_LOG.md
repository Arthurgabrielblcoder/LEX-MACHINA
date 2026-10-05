# MACRO07 — execução no Cloud (arts. 76–175)

Branch `cf-macro-76-175-cloud`, empilhada sobre `batch06-scale-cloud` (`da0dbfa`). Python 3.12. Data de referência: 2026-10-05.
**0 HUMAN_APPROVED_T1 novos.** AUTO_APPROVE_LOW, AUTO_APPROVE_MEDIUM e MICROAUTO_APPLY continuam OFF (`editorial/T1_PIPELINE_CONFIG.json`).

## Reprodução a partir do Git

```
python ENTENDA_ENGINE/macro_critic_pass.py ENTENDA_ENGINE/derived/production_batch_07_macro <X> \
       ENTENDA_ENGINE/derived/production_batch_07_macro/drafts/pass1/MACRO07_<X>_CRITIC_EDITS.json \
       ENTENDA_ENGINE/derived/production_batch_07_macro/drafts/pass1/MACRO07_<X>_PASS1_*.json      # X = A, B, C, D
python ENTENDA_ENGINE/build_entenda_macro_batch.py ENTENDA_ENGINE/derived/production_batch_07_macro --determinism 3
```

Passo 1 (DRAFTER) em `drafts/pass1/MACRO07_<X>_PASS1_*.json`; passo 2 (CRITIC) em `drafts/pass1/MACRO07_<X>_CRITIC_EDITS.json`.
Saída do crítico: `drafts/MACRO07_<X>_DRAFTS.json` e `drafts/MACRO07_<X>_CRITIC_LOG.json`. Nenhuma dependência do scratchpad.

## Commits e checkpoints

| Commit | Conteúdo | Checkpoint |
|---|---|---|
| `8ff50e5` | MACRO_07_A, arts. 76–100 | `MACRO07_A_CHECKPOINT.json` |
| `177be56` | MACRO_07_B, arts. 101–125 | `MACRO07_B_CHECKPOINT.json` |
| `27abb6e` | MACRO_07_C, arts. 126–150 | `MACRO07_C_CHECKPOINT.json` |
| `3742fc8` | MACRO_07_D, arts. 151–175 | `MACRO07_D_CHECKPOINT.json` |
| `6b7dc72` | consolidação: recomendações de link, BACKLOG, testes | — |

## Suítes

| Suíte | Resultado |
|---|---|
| ENTENDA completa (`ENTENDA_ENGINE/tests`, inclui Batch05, Batch06, validator v2, resolver hermético, materialização Git e a nova `test_entenda_macro_batch07`) | **PASS**: 198 testes, 2 skips (os mesmos do baseline: candidato host do Batch05; integração opcional com o Relations Engine local) |
| `test_entenda_macro_batch07` | **PASS**: 18 testes (inclui rebuild byte a byte e reprodução do passo do crítico) |
| Validator v3 + editorial_checks no lote | 0 HARD_FAIL; 0 achados editoriais abertos (34 duplicações estruturais e 1 TRANSITION_IN_CORE resolvidos com justificativa em `EDITORIAL_INPUT.json`) |
| Materialização Git (`git_materialization_check.py --source HEAD`) | **PASS**: 277/277 arquivos críticos byte-idênticos, 11 pares de índice, 1146/1146 blocos de payload, 0 problemas |
| Determinismo do builder macro | **PASS**: 3 builds + build no lugar byte-idênticos (`DETERMINISM_EVIDENCE.json`) |
| Hashes dos módulos compartilhados (manifesto do Batch06) | **PASS**: inalterados |

## Contabilidade explícita (`ENTENDA_ENGINE/cloud_test_accounting.py`)

| Suíte | Total | PASS | FAIL | SKIPPED | NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY | NOT_COLLECTED |
|---|---|---|---|---|---|---|
| DEVICE_INTEGRATION | **353** | 120 | 2 | 136 | 68 | 27 |
| LEGAL_TARGET_ID | **65** | 63 | 1 | 0 | 1 | 0 |

Os números são idênticos ao baseline do Batch06. As falhas são preexistentes, não pioraram e estão registradas:
- DEVICE_INTEGRATION FAIL 2 (`test_predeploy_a2c`: `test_ec45_cross_source`, `test_fail_closed`): cópia versionada da EC 45 com sha divergente do registrado.
- LEGAL_TARGET_ID FAIL 1 (`test_source_hash`): espera o `cf.txt` legado em CRLF (checkout Windows); o blob é LF.
- NOT_RUN 68 + 1: staging do SD, tags git só locais e `CF_SEGMENTADA_V2/` local. NOT_COLLECTED 27: módulos que não importam sem o staging local.

Detalhe por teste: `DEVICE_INTEGRATION_CLOUD_ACCOUNTING.json` e `LEGAL_TARGET_ID_CLOUD_ACCOUNTING.json` nesta pasta.

## Limites do Cloud

- STF, Planalto e Câmara inacessíveis daqui (egress bloqueado). Nada foi preenchido de memória: dependências jurisprudenciais ficam como
  `EXTERNAL_VERIFICATION_REQUIRED` na camada externa, e as 67 recomendações de link são `PENDING_EXTERNAL_INGESTION`.
- As fontes locais de jurisprudência (`C:/LMA/...`) e o export local de referências não existem no Cloud: nenhuma recomendação pode ficar READY_TO_LINK.
- ESP32, microSD, firmware conectado e staging físico: fora do alcance da VM.
