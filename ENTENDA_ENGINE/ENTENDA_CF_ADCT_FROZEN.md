# ENTENDA — Constituição Federal + ADCT: camada congelada

```
LAYER = ENTENDA_CF_ADCT
STATUS = FROZEN_APPROVED_BASELINE
BASELINE = ENTENDA_810
HUMAN_APPROVED_T1 = 810
PENDING = 0
CF_DIRECT_APPROVED = 743
ADCT_APPROVED = 67
PHYSICAL_VALIDATION = PASS
EDITORIAL_ALIGNMENT_WITH_DEVICE = PASS
FREEZE_DATE = 2026-10-16
REFERENCE_COMMIT = fa9719a6bd335275252473a5f154e4e11f5532f4
REFERENCE_TAG = lex-device-v1-entenda-810-physical-approved-2026-10-11
PHYSICAL_APPROVAL_COMMIT = 44ef69ba3957d9c55a6b4b5fe9f9f68fcd77efef
BRANCH = cf-references4-finalize
```

- **`REFERENCE_COMMIT`:** a reconciliação autoritativa (`reconcile-macro07-macro08`), origem jurídica do pacote físico.
- **`REFERENCE_TAG`:** a tag física existente, que aponta para `44ef69b` (*chore(device): approve physical ENTENDA 810 baseline*, 2026-10-11).
- **Sem tag nova:** a tag física existente já identifica de forma inequívoca o baseline ENTENDA 810. Este freeze é documental.

## Estado aprovado (confirmado por leitura em 2026-10-16)

**Contagem.** Foi refeita de forma independente sobre os 12 corpora vivos (`*.entenda.jsonl` fora de `history/` e sem `_PRE_`, incluindo `ENTENDA_ENGINE/corpus/CF88.entenda.jsonl`):

- 810 chaves ACTIVE, todas `HUMAN_APPROVED_T1`;
- 743 targets CF88 e 67 ADCT;
- 0 chaves só pendentes.

As 145 presenças multi-corpus são os pares históricos rascunho/final dos lotes 01–03, já documentados.

**Reconciliação** (`ENTENDA_ENGINE/derived/reconciliation_macro07_macro08/RECONCILIATION_UPDATE_MACRO07_FINAL.{md,json}`):

| Métrica | Valor |
|---|---|
| Aprovados | 561 → **810** |
| Pendentes | 249 → **0** |
| Aprovações perdidas | 0 |
| `active_conflict` | 0 |
| Macro07 | 249/249 |
| Macro08 | `MACRO08_APPROVALS_PRESERVED` 179/179 |

**Lotes incorporados** (composição 382 + 249 + 179):

- Piloto T1, base e Batch01–06: 382. Batch06 fechado em `3cc0cfc`.
- Macro07 (`cf-macro-76-175-cloud`, `bc831c5`, conteúdo jurídico `8daf73a`): 249 decisões em 7 rodadas humanas.
- Macro08 ADCT (`cf-macro-176-250-adct-cloud`, `5c4f1a0`): 179 aprovadas.
  - Essa branch **não está** na ancestralidade direta.
  - O conteúdo foi incorporado pela reconciliação (`8ef7312`): 76/94 arquivos byte-idênticos, e os demais são agregados e apresentação regeneráveis.
  - Nenhum merge adicional dela é necessário ou autorizado.

## Alinhamento com o aparelho

`EDITORIAL_ALIGNMENT_WITH_DEVICE = PASS`, só com evidência versionada; o cartão não foi acessado.

- **Pacote físico:** `FULL_CF_ENTENDA_810`, build `de963699728cb66e`, com `GIT_COMMIT = fa9719a…`.
  - `ENTENDA_LOOKUP.IDX` `017050dc98b76cdbea9997c6d3ad49f34673393c6768fcb43fa0eb9767120c99` (1.069 linhas: 810 DIRECT + 259 COVERED_BY_BLOCK).
  - `ENTENDA_PAYLOAD.DAT` `dbea72601046e6d9fba2f6a6442a490f905a03911186f9aeb44db7e6184e0fd3`.
- **Conjunto:** o conjunto DIRECT do lookup é **idêntico** ao conjunto de targets `HUMAN_APPROVED_T1` dos corpora (810 = 810).
- **Preservação:**
  - os mesmos dois hashes constam do manifesto pós-C3B.2 (`DEVICE_INTEGRATION/C3B2_CORRELATA_PROMOTION/sd_manifest_post_full.json`) e do manifesto pós-Referências nº 4 (`REFERENCE_COVERAGE_AUDIT/R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json`);
  - o pacote ENTENDA 810 não foi alterado por nenhuma promoção posterior;
  - o manifesto do aparelho atual (`R2_PHYSICAL_DEPLOY/promoted_sys/`) registra `ENTENDA_COUNT 810`, `ENTENDA_SCOPE CF88_ADCT_FULL_HUMAN_APPROVED_T1` e a origem `fa9719a`.

## Validação física (evidência existente; nenhum teste novo)

Fonte: `DEVICE_INTEGRATION/FULL_ENTENDA_810_PHYSICAL_BASELINE_APPROVED.md`, `FULL_ENTENDA_810_DIAG_FLASH_REPORT.md` e `FULL_ENTENDA_810_PREDEPLOY_REPORT.md`.

- **Resultado:** 2026-10-11, `PHYSICAL_HUMAN_VALIDATION = APPROVED_BY_ARTHUR`.
- **SD:** deploy oficial `pre/copy/verify`, `SD_VALIDATED`.
- **Firmware:** app `445fdb7f…` com DIAG de boot 33/33 PASS e `runtime hash CONFERE`.
- **Smoke:** arts. 5, 127, 156-A, um ADCT, scroll e BACK.
- **Confirmações posteriores:** o teste 8 da rodada física de Referências nº 4 (2026-10-16, CF art. 127 ENTENDA) passou no baseline atual, com firmware `6e329c91…`.

## SKIPs do ADCT (intencionais, não são pendência)

O `ENTENDA_ENGINE/derived/production_batch_08_macro/MACRO08_SKIP_REGISTER.json` registra 73 artigos e 317 targets avaliados e **não explicados por decisão editorial**, cada um com motivo, classe temporal e proveniência:

| Decisão | Artigos |
|---|---:|
| `SKIP_EXHAUSTED_TRANSITION` | 38 |
| `SKIP_TRANSITION_EVENT_DEPENDENT` | 15 |
| `SKIP_RESIDUAL_PERSONAL_TRANSITION` | 14 |
| `SKIP_CONSUMED_CONSTITUTIVE_ACT` | 5 |
| `SKIP_APPROVED_PILOT_LEGACY_MODEL` | 1 |

Um SKIP não é lacuna nem pendência. Só pode virar explicação numa rodada editorial explicitamente aberta.

**Monitoramento temporal** (não é pendência). Em `MACRO08_TRANSITION_EVIDENCE.json`, 18 explicações **já aprovadas** têm situação temporal não resolvida de forma determinística pelo parser (`EXTERNAL_STATUS_REQUIRED`, `FUTURE_TRIGGER`, `PARTIALLY_OPERATIVE`). São os primeiros candidatos a revalidação se houver mudança legislativa ou o evento esperado ocorrer.

Na CF, todo artigo vigente tem ENTENDA, direto ou por bloco.

## Artefatos autoritativos

- **Corpora:** `ENTENDA_ENGINE/corpus/CF88.entenda.jsonl` e `ENTENDA_ENGINE/derived/production_batch_*/…entenda.jsonl` (versões ACTIVE; históricos e `_PRE_*` preservados).
- **Decisões humanas** de cada lote/rodada nos respectivos diretórios, incluindo `MACRO08_HUMAN_REVIEW_DECISIONS*.json` e as rodadas do Macro07.
- **Reconciliação:** `ENTENDA_ENGINE/derived/reconciliation_macro07_macro08/`.
- **Padrão editorial:** `ENTENDA_T1_EDITORIAL_STANDARD.md` (tag `entenda-batch05-t1-frozen-2026-10-04`) + adendo A6.
- **Pacote do aparelho:** gerado por `DEVICE_INTEGRATION/tools/build_sd_staging.py`, perfil `FULL_CF_ENTENDA_810` (`build_full_entenda_810_candidate.py`, reprodutível byte a byte).

## Significado de "frozen"

`FROZEN_APPROVED_BASELINE` NÃO significa que a camada nunca poderá evoluir. Significa:

- a rodada atual de produção do ENTENDA CF + ADCT está encerrada;
- o conjunto 810 é o baseline aprovado;
- nenhuma alteração oportunista deve ser feita enquanto outras camadas são trabalhadas;
- mudanças futuras exigem uma missão explícita de reabertura;
- mudanças legislativas, erro comprovado ou uma nova rodada editorial podem justificar a reabertura;
- toda reabertura preserva o histórico e a proveniência (versões RETIRED, `superseded_by`, decisões, snapshots `PRE_*`) e parte deste baseline.

## Guardrail

- **Trabalhos cobertos:** Jurisprudência, Lei Seca, Correlatas, Referências, firmware, updater e outras normas.
- **Regra:** esses trabalhos NÃO devem modificar incidentalmente o baseline ENTENDA 810. Isso inclui:
  - os corpora e as decisões;
  - `ENTENDA_LOOKUP.IDX` e `ENTENDA_PAYLOAD.DAT`;
  - as flags E/B (`[0]`) e X (`[5]`) de `CF88_TARGETS.IDX`;
  - o perfil `FULL_CF_ENTENDA_810`.
- **Se um pipeline futuro alterar esses bytes ou dados:** PARAR e tratar como reabertura explícita da camada.

**Camadas congeladas no mesmo baseline físico:**

```
CORRELATAS_1_CF = FROZEN (CORRELATA_COVERAGE_AUDIT/CORRELATAS_1_CF_FROZEN.md)
REFERENCES_4_CF = FROZEN (REFERENCE_COVERAGE_AUDIT/REFERENCES_4_CF_FROZEN.md)
ENTENDA_CF_ADCT = FROZEN (este documento)
```

## Fora do escopo (registrado, não corrigido)

As dívidas abaixo estão detalhadas em `CF_GENERAL_LAYER_STATUS_2026-10-16.md`:

- o header `firmware/` de Referências ainda com 122 fichas;
- 4 falhas históricas de reconstrução/hash de Correlatas;
- a flag R com 25 divergências;
- `main` desatualizada em relação aos baselines físicos;
- testes que dependem de arquivos não versionados.
