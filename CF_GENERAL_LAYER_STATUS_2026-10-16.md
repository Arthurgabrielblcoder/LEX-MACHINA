# LEX MACHINA — Constituição Federal: estado geral das camadas (2026-10-16)

```
MISSION = inventário geral pós-congelamento (HOST-ONLY, READ-ONLY; só este relatório foi criado)
BASE = cf-references4-finalize @ 45a0084 (tag lex-device-v1-references4-physical-approved-2026-10-16)
MICROSD_TOUCHED = NO · FIRMWARE_CHANGED = NO · FROZEN_LAYERS_CHANGED = NO
```

Fontes do levantamento:

- `git log` / `git show` / `rev-list`;
- documentos de baseline e freeze;
- manifestos versionados (`R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json` e pacotes);
- os corpora e relatórios do ENTENDA;
- os bytes do pacote promovido (`REF_PAYLOAD`, `CF88_TARGETS`) e o lookup ENTENDA 810 do staging local, cujo hash `017050dc…` é igual ao do cartão.

Nada foi recompilado, pesquisado ou regenerado.

## 1. Baseline físico atual

**Base de trabalho correta:** `cf-references4-finalize` (`45a0084`). É a única branch que contém, ao mesmo tempo, o ENTENDA 810, CORRELATAS 1 (C3B.2) e REFERÊNCIAS Nº 4.

- `main`, `batch06-scale-cloud`, `device-entenda-810`, `reconcile-macro07-macro08`, `cf-macro-76-175-cloud` e `cf-correlata-coverage-audit` são todas ancestrais dela.
- `cf-macro-176-250-adct-cloud` (Macro08) tem 13 commits fora da ancestralidade. O conteúdo dele foi incorporado pela reconciliação (`8ef7312` → `fa9719a`): 179/179 aprovações preservadas.

**Cadeia de tags físicas, sem tag movida:**

| Tag | Data |
|---|---|
| `lex-device-v1-physical-approved` | 10-01 |
| `lex-device-v1-batch04-run3-physical-approved` | 10-03 |
| `lex-device-v1-full-corpus-indexes-approved` | 10-04 |
| `lex-device-v1-72-indexes-approved` | 10-04 |
| `lex-device-v1-context-citation-guard-approved` | 10-04 |
| `lex-device-v1-entenda-810-physical-approved` | 10-11 |
| `lex-device-v1-correlata-c3b2-physical-approved` | 10-12 |
| `lex-device-v1-references4-physical-approved` | **10-16** |

**Estado lógico do aparelho** (manifesto pós-R2, verificado por leitura em 2026-10-16):

- **SD:** 1.142 arquivos, build `5eb2a9298c1edbd6`, `REFERENCE_ENGINE cf-reference-engine-run5-references4-r1`, `ENTENDA_COUNT 810`, `TARGETS 3810`.
- **Firmware:** app0 `6e329c91…` (DEVICE V1, flag 1).

## 2. Camadas existentes (derivadas do firmware e dos índices)

Rodapé do leitor: `1 CORR.` · `2 JURIS.` · `3 ENTENDA` · `4 REF.`. A disponibilidade de cada tecla vem de `CF88_TARGETS.IDX`.

| Camada | Tecla | Dataset autoritativo | Índices no cartão |
|---|---|---|---|
| Lei Seca CF + ADCT (texto, targets, navegação, busca) | leitor + busca | `LEGAL_TARGET_ID` (target_id canônico, runtime CF88_RUNTIME 587.133 B `7ef82290…`, errata `3dff200`) | `05_TEXT/CF88_RUNTIME.txt`, `CF88_TEXT_MAP.IDX`, `CF88_TARGETS.IDX`, 72 índices de artigo |
| CORRELATAS 1 | 1 | `CORRELATA_COVERAGE_AUDIT` (C1A/C1B/C2/C3A → C3B.2) | `REF_*` (linhas CORRELATA) + `99_RELATIONS_V2` (RELACOES/REL_LOOKUP/EXT_ARTIGOS) |
| JURISPRUDÊNCIA | 2 | camada `SD_JURIS_J4_6_IDS` do catálogo canônico (`CF88_REFERENCES_CANONICAL.json`; origem J4 `VINCULOS_EXPLICITOS`, fora do Git/archive) + `CF88_LINK_EXCLUSIONS.json` | `REF_*` (linhas JURISPRUDENCE); conteúdo legado em `99_JURISPRUDENCIA_V2` |
| ENTENDA | 3 | `ENTENDA_ENGINE` (corpora `*.entenda.jsonl`; reconciliação `fa9719a`) | `30_ENTENDA/ENTENDA_LOOKUP.IDX` + `ENTENDA_PAYLOAD.DAT` |
| REFERÊNCIAS Nº 4 | 4 | RC2 + `CF88_WORK_REFERENCE_ADDITIONS{,_R1}.json` + `WORK_REGISTRY_V3` | `REF_*` (linhas WORK_REFERENCE) + tabela `lex_ref_detail_data.h` no firmware |

**Flags de `CF88_TARGETS.IDX`** (6 posições, conforme o firmware atual):

| Pos. | Flag | Camada | Firmware lê? | Em uso | Targets | Divergência |
|---|---|---|---|---|---|---|
| [0] | E/B | ENTENDA DIRECT / COVERED_BY_BLOCK | sim (`flags[0]`) | sim | 810 E + 259 B | — |
| [1] | C | CORRELATA visível | sim | sim | 24 | — (C3B.2) |
| [2] | J | JURISPRUDENCE visível | sim | sim | 170 | — |
| [3] | W | WORK_REFERENCE visível | sim | sim | 65 | — |
| [4] | R | qualquer linha no REF_LOOKUP | **não** | não | 253 | **25 divergências R-only em relação ao gerador** (dívida conhecida, não recalculada) |
| [5] | X | ENTENDA com camada externa ou nota temporal | **não** | não (informativa) | 461 | nenhuma conhecida |

## 3. Status por camada

| Camada | Classificação | Motivo |
|---|---|---|
| **Lei Seca / estrutura-base** | `PHYSICAL_APPROVED_NOT_FROZEN` | Texto, targets, TEXT_MAP, busca e navegação estão no baseline físico e cobertos por tags (10-01 a 10-04, mais a errata `3dff200`), mas não existe documento de freeze próprio |
| **CORRELATAS 1** | `FROZEN_PHYSICAL_APPROVED` | `CORRELATAS_1_CF_FROZEN.md`, baseline C3B.2, tag `…correlata-c3b2…`, físico 15/15 + smoke; preservada no R2 (testes físicos 6 e 7 PASS) |
| **REFERÊNCIAS Nº 4** | `FROZEN_PHYSICAL_APPROVED` | `REFERENCES_4_CF_FROZEN.md`, tag `…references4…`, físico 8/8; 124 WORK_REFERENCE / 56 obras / 65 W conferidos nos bytes |
| **ENTENDA** | `PHYSICAL_APPROVED_NOT_FROZEN` | 810/810 `HUMAN_APPROVED_T1`, 0 pendentes, instalado e validado pelo usuário (tag `…entenda-810…`), mas sem documento de freeze |
| **JURISPRUDÊNCIA** | `PARTIAL` | 277 vínculos publicados e funcionando no aparelho, mas sem rodada de revisão humana/cobertura própria, sem freeze e com backlog de 148 recomendações de ingestão externa |

## 4. Contagens

**ENTENDA** (`ENTENDA_SCOPE CF88_ADCT_FULL_HUMAN_APPROVED_T1`):

| | CF | ADCT | Total |
|---|---:|---:|---:|
| Explicações aprovadas (targets DIRECT) | 743 | 67 | **810** |
| Linhas COVERED_BY_BLOCK (sem texto próprio) | 259 | 0 | 259 |
| Artigos com ENTENDA | 273 | 66 | 339 |
| Artigos vigentes sem ENTENDA | **0** | 72 (SKIP intencional, `MACRO08_SKIP_REGISTER.json`: 73 artigos / 317 targets, cada um com motivo) | — |

- `HUMAN_APPROVED_T1` = 810; `PENDING_HUMAN_REVIEW` = 0. Composição: 382 (base + Batch01–06) + 249 (Macro07) + 179 (Macro08).
- **Lotes mais recentes:** Batch06 (fechado em `67df005`/`3cc0cfc`), Macro07 (fechado em 249/249, `bc831c5`) e Macro08 (179/179, `5c4f1a0`).
- **Autoritativo:** a reconciliação `fa9719a`, que gerou o pacote físico 810. Não existe etapa posterior.
- **Discrepância editorial × físico:** nenhuma. O lookup/payload do cartão (`017050dc…`/`dbea7260…`) é o pacote 810, inalterado em C3B.2 e R2.

**JURISPRUDÊNCIA** (bytes do baseline):

| Métrica | Valor |
|---|---|
| Vínculos visíveis | 277 (RG 267 + SV 10) |
| Ocultos históricos | 6 |
| Targets cobertos | 170 (169 CF + 1 ADCT) |
| Fontes distintas | 214 |
| Exclusões aprovadas | 2 (Tema 113 × art. 25; Tema 756 × art. 31, § 3º) |

- Acórdãos e repetitivos não existem como tipo no dataset atual.

**CORRELATAS 1:** 24 visíveis + 2 ocultas (C3B.2), 24 flags C.

**REFERÊNCIAS Nº 4:** 124 vínculos / 56 obras / 65 W.

**TARGETS:** 3.810 (CF 2.920 + ADCT 890), 276 artigos CF e 148 ADCT, 13 artigos REVOKED.

## 5. Pendências reais (necessárias para encerrar a rodada atual)

| Camada | Pendências humanas | Outras pendências |
|---|---|---|
| Lei Seca | — | Formalizar o freeze; opcionalmente, documento único de baseline estrutural |
| CORRELATAS 1 | — | — |
| REFERÊNCIAS Nº 4 | — | — |
| ENTENDA | **0** decisões editoriais pendentes | Freeze formal ausente. As 18 evidências temporais `unresolved` do Macro08 (`MACRO08_TRANSITION_EVIDENCE.json`) referem-se a itens já aprovados ou SKIP; vale confirmar na missão de freeze que não exigem ação |
| JURISPRUDÊNCIA | Nenhuma fila formal de decisão aberta | **148** recomendações `PENDING_EXTERNAL_INGESTION` (110 targets), oriundas dos lotes ENTENDA, que exigem ingestão e pesquisa externa. Os 277 vínculos legados nunca passaram por auditoria de cobertura/qualidade como C0/C1 (Correlatas) ou RC2 (Referências). 3 `MATERIAL_MISMATCH_EXCLUDED` já tratadas; 19 `READY_TO_LINK` já vinculadas |

**Não contam como pendência:**

- as 199 obras candidatas e as 19 obras do registry sem vínculo (Referências);
- os SKIP intencionais do ADCT;
- as lacunas confirmadas dos arts. 98 e 202;
- as 27 referências `CROSS_NORM_PENDING` (outras normas, fora do escopo CF).

**Esforço relativo** das camadas não encerradas:

| Camada | Esforço | Por quê |
|---|---|---|
| ENTENDA (freeze) | **BAIXO** | Sem decisões, sem pesquisa, sem firmware, sem deploy |
| Lei Seca (freeze) | **BAIXO** | Documental |
| JURISPRUDÊNCIA | **ALTO** | Auditoria de 277 vínculos e 148 ingestões com pesquisa externa; possível novo export de `REF_*`/`TARGETS` (arquivos compartilhados com as camadas congeladas) e teste físico |
| Reprodutibilidade do firmware | **MÉDIO** | Promover o header de 124 fichas para `firmware/` exige reabrir o guard de Correlatas 1 (`test_14`/`test_16`), recompilar e provar que o binário é igual a `6e329c91…` |

## 6. Dívidas técnicas (registradas, não corrigidas)

1. **`REPRODUCIBILITY_DEBT` (firmware/Referências).** `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h` ainda tem `LEXV1_REF_DETAIL_COUNT 122`, enquanto o app gravado usa 124 fichas (header em `run5_references4_r1_candidate/device_candidate/`). Uma recompilação a partir de `firmware/` não reproduz o baseline.
2. **`PREEXISTING_CORRELATA_TEST_DEBT = 4`.** Falhas de reconstrução/hash em C0, C3A.1, C3B.1 e C3B.2, idênticas no checkout limpo. Continuam documentadas em `REFERENCES_4_CF_FROZEN.md` e no relatório de aprovação.
3. **Flag R.** 25 divergências R-only em relação ao gerador. O firmware não lê essa posição.
4. **Integração de branches.** `main` (`f1a6966`, 2026-10-04) não contém nenhum baseline físico posterior a 10-04: nem ENTENDA 810, nem C3B.2, nem REFERÊNCIAS Nº 4. Todo o estado aprovado vive em `cf-references4-finalize`.
5. **Dependências não versionadas dos testes.** Num checkout limpo:
   - `LEGAL_TARGET_ID/tests/test_target_id` depende de `CF_SEGMENTADA_V2/`, que não está no Git;
   - `DEVICE_INTEGRATION/tests` tem 23 erros e 144 skips por depender de stagings e backups ignorados;
   - neste working tree, `test_16` falha por causa de arquivos soltos (`DEVICE_INTEGRATION/_tmp_det_*.log`, `staging_entenda_batch05_candidate/`).

## 7. Prioridade recomendada

**`FINALIZAR ENTENDA`**, na forma de freeze formal da ENTENDA 810 (CF + ADCT).

- **Proximidade:** é a camada mais perto do fim, com 810/810 aprovadas, 0 pendentes, já instalada e validada fisicamente, faltando só a formalização.
- **Ganho:** é a camada de maior volume de conteúdo para o usuário.
- **Risco:** praticamente nulo, porque é verificação somente de leitura mais documento, sem tocar em `REF_*`/`TARGETS`.
- **Reaproveitamento:** reaproveita tag e relatórios existentes.
- **Pesquisa:** não exige Claude/Web.

**Por que não as outras agora:**

- **JURISPRUDÊNCIA** é a lacuna mais relevante para a maturidade da CF, mas tem esforço ALTO, depende de pesquisa externa e regera arquivos compartilhados com duas camadas congeladas. Deve vir depois, como missão própria, começando por uma auditoria diagnóstica no molde do C0 das Correlatas.
- **Reprodutibilidade do firmware** deve ser resolvida antes da próxima mudança de firmware. Hoje não bloqueia o uso.

## 8. Próxima missão sugerida

```
NEXT_RECOMMENDED_MISSION = E-FREEZE — congelamento formal da ENTENDA 810 (CF + ADCT): verificação somente leitura de
ENTENDA_LOOKUP/PAYLOAD no baseline físico atual, confirmação 810/0 a partir da reconciliação fa9719a, conferência das 18
evidências temporais unresolved do Macro08, e criação de ENTENDA_CF_FROZEN.md (sem regenerar, sem deploy, sem tag nova
se a tag física 810 for suficiente).
```

Em seguida, nesta ordem sugerida:

1. **J0:** auditoria diagnóstica de cobertura da JURISPRUDÊNCIA CF (molde C0).
2. **Freeze da Lei Seca.**
3. **Correção da `REPRODUCIBILITY_DEBT` do firmware**, antes de qualquer novo flash.
4. **Integração das branches em `main`**, como decisão do usuário.
