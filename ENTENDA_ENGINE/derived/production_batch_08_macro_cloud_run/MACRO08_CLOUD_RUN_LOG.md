# MACRO08 — execução no Cloud (CF arts. 176–250 + ADCT)

Branch `cf-macro-176-250-adct-cloud`, criada do checkpoint fixo `03e6f2592f099b6279d10ec91a307e737faffa88`, em paralelo a
`cf-macro-76-175-cloud` (**STACKED_PARALLEL_BRANCH**; **RECONCILIATION_REQUIRED_BEFORE_MERGE**). Python 3.12. Data de referência: 2026-10-05.
**0 HUMAN_APPROVED_T1 novos.** AUTO_APPROVE_LOW, AUTO_APPROVE_MEDIUM e MICROAUTO_APPLY continuam OFF.
`main`, `batch06-scale-cloud` e `cf-macro-76-175-cloud` não foram alterados. Sem merge, rebase ou force push.

## Reprodução a partir do Git

```
python ENTENDA_ENGINE/entenda_text_profile.py --check                      # perfil CF88_OFFICIAL_RUNTIME byte a byte
python ENTENDA_ENGINE/macro_critic_pass.py ENTENDA_ENGINE/derived/production_batch_08_macro <X> \
       ENTENDA_ENGINE/derived/production_batch_08_macro/drafts/pass1/MACRO08_<X>_CRITIC_EDITS.json \
       ENTENDA_ENGINE/derived/production_batch_08_macro/drafts/pass1/MACRO08_<X>_PASS1_*.json      # X = A..H
python ENTENDA_ENGINE/build_entenda_macro_segment.py ENTENDA_ENGINE/derived/production_batch_08_macro --determinism 3
```

Passo 1 (DRAFTER) em `drafts/pass1/MACRO08_<X>_PASS1_*.json`; passo 2 (CRITIC adversarial) em `drafts/pass1/MACRO08_<X>_CRITIC_EDITS.json`
(antes/depois, categoria, motivo e detector). Saída: `drafts/MACRO08_<X>_DRAFTS.json` e `drafts/MACRO08_<X>_CRITIC_LOG.json`.

## Commits e checkpoints

| Commit | Conteúdo | Checkpoint |
|---|---|---|
| `7b29781` | perfil de texto CF88_OFFICIAL_RUNTIME (ADCT pelo runtime oficial) + builder por segmento | — |
| `84d2965` | MACRO_08_A, CF arts. 176–200 | `MACRO08_A_CHECKPOINT.json` |
| `5015655` | MACRO_08_B, CF arts. 201–225 | `MACRO08_B_CHECKPOINT.json` |
| `1a65e78` | MACRO_08_C, CF arts. 226–250 | `MACRO08_C_CHECKPOINT.json` |
| `9897702` | MACRO_08_D, ADCT 1–30 + auditoria estrutural do ADCT | `MACRO08_D_CHECKPOINT.json` |
| `a1208d0` | MACRO_08_E, ADCT 31–60 | `MACRO08_E_CHECKPOINT.json` |
| `6095f24` | MACRO_08_F, ADCT 61–90 | `MACRO08_F_CHECKPOINT.json` |
| `0f1c002` | MACRO_08_G, ADCT 91–115 | `MACRO08_G_CHECKPOINT.json` |
| `c4cf95e` | MACRO_08_H, ADCT 116–138 (+ gatilho futuro datado) | `MACRO08_H_CHECKPOINT.json` |
| `f12804b` | consolidação: BACKLOG, diagnóstico D, métricas por segmento, testes, contabilidade | — |
| `b638303` | teste de materialização Git conta o par de índice do Macro08 (12) | — |

## Suítes

| Suíte | Resultado |
|---|---|
| ENTENDA completa (`ENTENDA_ENGINE/tests`: Batch05, Batch06, Macro07, Macro08, validator v2/v3, critic, reconstrução de fonte, índice/status de targets, resolver hermético, materialização Git) | **PASS**: 225 testes, 2 skips (os mesmos do baseline: candidato host do Batch05; integração opcional com o Relations Engine local) |
| `test_entenda_macro_batch08` | **PASS**: 27 testes (perfil byte a byte e round trip, contrato do motor e Lei Seca, camada temporal com proveniência, ADCT esgotado não escrito como vigente, D temporal, evidência de transição, reprodução do critic, rebuild byte a byte, módulos compartilhados inalterados, lotes anteriores intactos) |
| `test_entenda_macro_batch07` | **PASS**: 18 testes (Macro07 intacto, rebuild byte a byte) |
| Materialização Git (`git_materialization_check.py --source HEAD`) | **PASS**: 362/362 arquivos críticos byte-idênticos, 12 pares de índice, 1346/1346 blocos de payload, 0 problemas |
| Determinismo do builder | **PASS**: 3 builds + build no lugar byte-idênticos (`DETERMINISM_EVIDENCE.json`, 78 arquivos) |
| Hashes dos módulos compartilhados (manifestos do Batch06 e do Macro07) | **PASS**: inalterados |

## Contabilidade explícita (`ENTENDA_ENGINE/cloud_test_accounting.py`)

| Suíte | Total | PASS | FAIL | SKIPPED | NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY | NOT_COLLECTED |
|---|---|---|---|---|---|---|
| DEVICE_INTEGRATION | **353** | 119 | 3 | 136 | 68 | 27 |
| LEGAL_TARGET_ID | **65** | 63 | 1 | 0 | 1 | 0 |

Baseline (Macro07 Cloud): DEVICE_INTEGRATION 120/2/136/68/27; LEGAL_TARGET_ID 63/1/0/1/0. Esta branch não altera nenhum arquivo de
`DEVICE_INTEGRATION/` nem de `LEGAL_TARGET_ID/` (diff vazio contra o checkpoint).

- DEVICE_INTEGRATION FAIL 2 preexistentes (`test_predeploy_a2c`: `test_ec45_cross_source`, `test_fail_closed`).
- DEVICE_INTEGRATION FAIL 1 **de ambiente**: `test_runtime_a2b.OfficialSourcesTest.test_adct_registered_in_official_pipeline` falha com
  `ModuleNotFoundError: requests` (e depois `bs4`) porque este container não tem essas bibliotecas. Com `requests` e `beautifulsoup4`
  instalados num diretório temporário fora do repositório, o teste passa (OK). Nada foi instalado no repositório.
- LEGAL_TARGET_ID FAIL 1 preexistente (`test_source_hash`: espera `cf.txt` em CRLF).
- NOT_RUN 68 + 1 e NOT_COLLECTED 27: staging do SD, tags git só locais e pastas locais, como no baseline.

Detalhe por teste: `DEVICE_INTEGRATION_CLOUD_ACCOUNTING.json` e `LEGAL_TARGET_ID_CLOUD_ACCOUNTING.json` nesta pasta.

## Limites do Cloud

- Nada foi preenchido de memória: estado de leis complementares, emendas não versionadas e ações de controle ficam
  `PENDING_EXTERNAL_INGESTION`; as 32 recomendações de link de jurisprudência estão pendentes.
- ESP32, microSD, firmware e staging físico: fora do alcance da VM. Nenhum hardware ou SD foi tocado.
