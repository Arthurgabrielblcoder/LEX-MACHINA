# J2F — Ratificação dos Batches 03–09 e preflight de materialização (host-only)

```
RATIFICATION_STATUS = PASS · TOTAL_RECOMMENDATIONS = 55 · RATIFIED_DECISIONS = 54 · UNRESOLVED_EXTERNAL = 1 (J0-BL-001, Súmula 403/STJ)
PHYSICAL_BASELINE = 261/160 · PHYSICAL_BASELINE_RECONCILED = PASS · PROVISIONAL_STATUS_PRESERVED = YES · PROVISIONAL_REVALIDATION_GATE = PASS
MICROSD_TOUCHED = NO · FIRMWARE_FLASHED = NO · DEPLOY = NO · BATCH10 = NÃO INICIADO
```

## 1. Ratificação (Partes A–C)

O registro formal está em `J2_RATIFICATION_RECORD_03_09.json` (`build_j2_ratification_record.py`).

- **Arquivos dos lotes:** os JSONs dos lotes continuam byte-idênticos ao que foi revisado; o registro fixa o sha256 de cada um.
- **Classificações:** todas preservadas. Rejeições, duplicatas e "já cobertas" não geram vínculo.
- **Provisórios:** ADI 5017, ADPF 378 e Rcl 84738 (mais a ADI 7697, já instalada) continuam provisórios.
  - O número no índice recebe sufixo: `(CAUTELAR)` ou `(PROVISÓRIA)`.
  - A ficha traz o bloco "DECISÃO PROVISÓRIA" e a data de verificação.
  - O gate (`check_j2b_provisional.py --registry J2_PROVISIONAL_REGISTRY.json --as-of 2026-10-17`) dá PASS nos 4.
- **Súmula 403/STJ:** sem ficha, sem vínculo e sem fonte não oficial. A auditoria confirma `STJ_SUMULA_403_ABSENT`.

## 2. Reconciliação 301 × 261 (Parte D)

`J2_BASELINE_RECONCILIATION.json` foi gerado a partir dos bytes do cartão J2C, com sha256 conferido no manifesto físico.

| Medida | Valor |
|---|---:|
| Vínculos físicos (REF_PAYLOAD, JURISPRUDENCE, CURRENT_VISIBLE) | **261** |
| Targets físicos | **160** |
| Linhas do índice legado `JURISPRUDENCIA.IDX` (registros de precedente) | 301 |
| Registros usados por vínculos visíveis | 257 |
| Registros usados só por vínculos históricos ocultos | 6 |
| Registros legados sem nenhum vínculo V1 | 38 |

Os 257 registros cobrem 261 vínculos porque 4 registros servem a dois targets cada (caput visual).

**O que era 301:** a contagem de **registros do índice legado**, e não de vínculos. O erro foi de texto:
- `JURIS_TYPE_ARCHITECTURE.md` rotulou essa contagem como "Vínculos";
- a resposta pós-noturna repetiu "301 vínculos já instalados".

O documento foi corrigido. Todos os builders J2F partem explicitamente de 261/160 e falham se a base for outra (`BASE_IS_NOT_PHYSICAL_BASELINE_261_160`).

## 3. Normalização (Parte E)

`apply_j2f_ratified_overlay.py` gera `LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2F.json`. Nenhuma contagem é fixada no código.

**Regras:**
- **Relação:** uma relação é um par (target, registro de precedente).
- **Divisão por alvo:** o `target` próprio do precedente prevalece sobre os targets da decisão.
  - A ADPF 378 (BL-067) vai para o art. 86, § 1º, II **e** para o art. 52, I, como diz a razão ratificada.
  - O teste exige que todo target ratificado fique coberto.
- **Registro conjunto:** ADI 3392 e ADI 3432 usam o registro único `STF:ADI:3423-3392-3432-3520`, conforme BL-102/103/116/117.
- **Deduplicação:** o mesmo par vindo de duas decisões vira uma relação só (ex.: ADI 3395 no art. 114, I, de BL-104 e BL-105).
- **Já presentes:** pares que já estão no cartão ou no J2E são descartados; nesta rodada, nenhum.

| Medida | Valor |
|---|---:|
| Decisões ratificadas | 54 |
| Decisões que vinculam (PROMOTE / PROMOTE_PROVISIONAL / REALLOCATE) | 39 |
| Pares antes da deduplicação | 51 |
| **NEW_DEVICE_RELATIONS_CURRENT_FW** (grupo A, Batches 03–09) | **31** |
| **NEW_DEVICE_RELATIONS_GENERIC_FW** (A + B, Batches 03–09) | **46** |
| Só grupo B | 15 |
| **NEW_PRECEDENT_RECORDS** (linhas novas no índice legado) | **46** |
| Precedentes distintos | 42 (28 no grupo A, 14 no grupo B) |
| **NEW_FICHAS_CURRENT_FW** (Batches 03–09) | **26** |
| **NEW_FICHAS_GENERIC_FW** (Batches 03–09) | **40** |
| **NEW_TARGETS_WITH_J** (Batches 03–09 sobre J2C + J2E), A / B | **20 / 31** |

As fichas da ADI 4425 e da SV 25 já estão no cartão e são reaproveitadas sem alteração.

**Textos das fichas:**
- **Temas e SVs:** formato J4 do cartão, com a tese integral do corpus oficial arquivado. As divergências em relação aos trechos dos lotes foram revisadas uma a uma; os trechos eram descrições ou versões resumidas, e nenhuma tese conflita.
- **Demais classes:** ficha gerada só com dados oficiais já registrados no lote (julgamento, publicação, resumo da fonte, trecho oficial, URL).
- **Tema 935:** a decisão ratificada mandava "revalidar antes de materializar". A página oficial, consultada em 17/10/2026 (sha `53861094…`), mostra acórdão de mérito publicado em 09/12/2025, sem trânsito em julgado. A ficha leva essa nota.

## 4. Grupos e candidatos (Partes F–H)

| | Candidato A — `J2_CURRENT_FW_CANDIDATE` | Candidato B — `J2_GENERIC_FW_CANDIDATE` |
|---|---|---|
| Firmware | atual (app aprovado `6e329c91…`, sem flash) | genérico de tribunal/classe (`juris_types.patch`; compilado, **não gravado**, sem aprovação física) |
| Conteúdo | J2C + J2E-A (7) + grupo A dos lotes 03–09 (31) | A + HC 232627 (J2E-B) + grupo B dos lotes 03–09 (15) |
| Vínculos / targets | **299 / 186** | **315 / 198** |
| Vínculos acrescentados | 38 | 54 |
| Arquivos modificados no cartão | 7 | 7 |
| Arquivos criados (fichas) | 30 | 45 |
| Registros no índice legado | 339 (= 301 + 38) | 355 (= 301 + 54) |
| Rótulo "OUTRO" no firmware de destino | 0 | 0 |
| Máx. de jurisprudências por target (limite 32) / itens visíveis por target (limite 40) | 10 / 10 | 10 / 10 |

**Arquivos modificados nos dois candidatos:**
- `JURISPRUDENCIA.IDX` e `JUR_LOOKUP.IDX` (só acréscimo);
- `LEXV1.VER` e `LEX_DEVICE_MANIFEST.json`;
- `CF88_TARGETS.IDX` (só a flag J);
- `REF_LOOKUP.IDX` e `REF_PAYLOAD.IDX`.

**Garantias (`J2F_ISOLATION_AUDIT.json`):**
- os 261 vínculos legados estão byte-idênticos e nenhuma linha foi removida;
- só entram relações ratificadas;
- Correlatas, Referências nº 4 (W) e ENTENDA intocadas;
- flags E/C/W/R/X intocadas;
- cache de boot válido;
- toda relação nova resolve com ficha;
- fichas dos Temas 367/387 intocadas (mock fica como UI_IMPROVEMENT_PROPOSAL);
- pacotes determinísticos;
- rollback igual aos bytes do cartão J2C.

**Tipos de cada grupo:**
- **Grupo A** (RG, SV, ADI): Temas 157, 835, 855, 1046, 1068, 935, 1229, 184, 201, 1093; SV 5, SV 25; ADI 1616, 1254, 789, 5017 (cautelar), 7369, 336, 978, 3423/3392/3432/3520, 2404, 3114, 2681, 4425 (art. 100), 3395, 3684, 6457, 2777.
- **Grupo B:**
  - Súmula 702 STF e Súmula 9 TSE;
  - MS 21689, MS 21564 e MS 27931;
  - AP 694 e AI 343461;
  - Inq 672 e Inq 4781;
  - Rcl 84738 (provisória);
  - ADPF 378 (cautelar, dois targets), ADPF 672 e ADPF 964;
  - HC 70648 e HC 232627 (J2E).
- **Com o firmware atual:** o grupo B apareceria como "OUTRO n" ou nem seria aceito (ID que não começa com `STF:`). Por isso B exige o firmware genérico.

**GENERIC_TYPES_LABELS_CORRECT = PASS** (simulação do firmware genérico):

| Rótulo exigido | Rótulo no aparelho |
|---|---|
| HC 232627 | HC 232627 |
| HC 70648 | HC 70648 |
| MS 21689 | MS 21689 |
| AP 694 | AP 694 |
| AI 343461 | AI 343461 |
| Inq 4781 | Inq 4781 |
| Rcl 84738 | Rcl 84738 (PROVISÓRIA) |
| ADPF 378 | ADPF 378 (CAUTELAR) |
| ADPF 964 | ADPF 964 |
| Súmula 9 TSE | Súmula 9 TSE |

## 5. Firmware (Parte M)

| Build | Programa (B) | RAM estática (B) | App (B) | Livre na partição (B) |
|---|---:|---:|---:|---:|
| Aprovado (R2) | 1.100.991 | 126.148 | 1.101.136 | 209.584 |
| `firmware/` recompilado | 1.100.991 | 126.148 | 1.101.136 | 209.584 |
| Genérico (protótipo) | 1.102.031 | 126.148 | 1.102.176 | 208.544 |
| **Delta do genérico** | **+1.040** | **+0** | **+1.040** | — |

- **FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE = PASS:** recompilado antes do protótipo; 70 bytes diferem, todos de metadado de build.
- **Firmware genérico:** não gravado.

## 6. Testes (Parte N)

| Suíte | Resultado |
|---|---|
| Jurisprudência (J1/J2, lotes, auditores, dossiê, provisórios, tipos, HC, **J2F: candidatos A/B**) | **98/98** |
| Motor de referências (`LEGAL_TARGET_ID`) | **90/90** |
| Referências nº 4 (`REFERENCE_COVERAGE_AUDIT`) | **15/15** |
| Correlatas | **115/120**; as 5 falhas são as mesmas do baseline, nome a nome |

Falhas das Correlatas, comparadas com `POST_OVERNIGHT_CHECKPOINT.md`:

| Módulo | Teste | Classificação |
|---|---|---|
| c0 | `test_committed_artifacts_are_the_build` | PREEXISTING |
| c3a1_c3b_prep | `test_15_run4_and_package_deterministic` | PREEXISTING |
| c3a_engine | `test_16_operational_files_untouched` (`_tmp_det_*.log` não rastreado) | PREEXISTING |
| c3b1 | `test_reproducible` | PREEXISTING |
| c3b2 | `test_c3b2_package_reproducible_and_equal_device_bytes` | PREEXISTING |

`NEW_CORRELATAS_REGRESSION = 0`.

## 7. Pendências físicas (fora desta missão)

- **Antes de qualquer deploy:**
  - rodar de novo o gate de provisórios na data do deploy (o prazo mais curto vence em 14/01/2027);
  - escrever o checklist físico do candidato escolhido.
- **SV 25:** a ficha já instalada traz "modalidade de depósito"; o enunciado oficial atual diz "do depósito". Ficha legada não alterada nesta missão.
