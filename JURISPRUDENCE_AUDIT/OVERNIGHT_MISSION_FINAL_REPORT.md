# LEX MACHINA — RELATÓRIO DA OPERAÇÃO NOTURNA (PARCIAL: limite de uso atingido)

```
J2C_PHYSICAL_BASELINE: 261/160 · J2E_HOST_ONLY: PASS · BATCH02_DEVICE_CANDIDATE_READY: YES (variante A)
HC_TYPE_DESIGN: PASS · HC_HOST_PROTOTYPE: PASS (compilado, não gravado) · HC_FIRMWARE_FLASHED: NO
BATCH03: CONCLUÍDO · BATCH04: CONCLUÍDO (5; HIGH esgotado) · BATCH05: VAZIO (fechamento HIGH)
ADDITIONAL_BATCHES_COMPLETED: 3 (MEDIUM 06–08) · BATCH09: INICIADO, NÃO CONCLUÍDO
FROZEN_LAYERS_MODIFIED: NO · MICROSD_TOUCHED: NO · FIRMWARE_FLASHED: NO · MAIN_MERGED: NO
```

## 1–3. Estados

| Estado | Conteúdo |
|---|---|
| **Instalado no aparelho** | **261 vínculos / 160 targets** (J2C) |
| **Ratificado, não instalado** | Batch02, materializado no J2E |
| **Candidato A** (`J2_HIGH_BACKLOG/J2E_BATCH02_CANDIDATE_HOST_ONLY/VARIANT_A_CURRENT_FIRMWARE`) | 268/166; usa o firmware atual |
| **Candidato B** (`…/VARIANT_B_REQUIRES_HC_FIRMWARE`) | 269/167; exige o firmware HC |

## 4. HC 232627

- **Estado:** estudado, implementado como `hc_type.patch` (4 edições), compilado e testado em simulação. **Não gravado.**
- **Firmware base:** reproduzido; difere do app aprovado `6e329c91` só em metadados de build.
- **Detalhes:** `HC_FIRMWARE_PROTOTYPE/HC_TYPE_DESIGN.md`.

## 5. Lotes (propostas aguardando ratificação, exceto 01–02)

| Lote | Pesquisados | Promoções | Realocações | Rejeições | Pendentes / outros |
|---|---:|---:|---:|---:|---|
| 03 HIGH | 10 | 6 (1 provisória) | 1 | 3 | 0 |
| 04 HIGH | 5 | 5 (1 provisória) | 0 | 0 | 0 |
| 06 MEDIUM | 10 | 5 | 2 | 3 | 0 |
| 07 MEDIUM | 10 | 6 | 3 | 0 | 1 já coberto |
| 08 MEDIUM | 10 | 4 | 2 | 1 | 2 duplicatas · 1 UNRESOLVED (STJ bloqueado) |

**Totais dos lotes 03–08:**

- 45 candidatos pesquisados;
- **26 promoções propostas** (3 provisórias);
- **8 realocações**;
- **7 rejeições**;
- 1 UNRESOLVED_EXTERNAL.

## 6. Backlog (após o Batch08)

- **Original:** 148 pendentes.
- **Analisados:** 55 (lotes 01–08).
- **Cobertos por ratificação:** 4.
- **Pendentes:** ~89.
- **HIGH:** 0.
- **MEDIUM:** 42 restantes.
- **LOW:** 27.

Recontar com `build_j2_batch.py --selection-only`.

## 7. Problemas jurídicos encontrados

- **Namespace:**
  - ADI 2167 (Constituição de Roraima);
  - ADI 3392, anotada genericamente em toda a EC 45 (arts. 92, 98, 102, 114 § 1º).
- **Alvo trocado:**
  - ADI 1616/1254 vão para o art. 103, § 3º;
  - Inq 672 vai para o art. 86, § 4º;
  - Tema 1068 vai para o art. 5º, XXXVIII;
  - Tema 935 vai para o art. 7º, XXVI;
  - SV 46 vai para o art. 22, I e o art. 85, p.u.
- **Tempo:**
  - o art. 165, § 18 é de 2025, posterior à ADI 7047/7064;
  - a ADI 4425 julgou redação histórica (art. 100, com nota).
- **Provisórios:** ADI 5017, ADPF 378, Rcl 84738 (Tema 1147) e ADI 7697.
- **Julgamentos conjuntos:**
  - ADI 7064 sozinha no art. 107-A (mesmo julgamento da ADI 7047, escopo diferente);
  - grupo ADI 3423/3392/3432/3520;
  - Inq 4787 = HC 232627.
- **Divergência de texto:** o corpus arquivado difere do texto oficial atual na SV 46 e na SV 25.

## 8. Ferramentas criadas e testadas

- `apply_j2e_batch02_overlay.py`
- `build_export_run10_juris_j2e.py`
- `build_j2e_candidate.py`
- `build_j2e_isolation_audit.py`
- `HC_FIRMWARE_PROTOTYPE/build_hc_firmware_prototype.py`
- `j2_auditors.py`
- `j2_review_common.py`
- `build_j2_batch.py`
- `render_j2_batch_report.py`

**Testes:** `test_j2e`, `test_hc_prototype`, `test_j2_auditors`, `test_j2_batches`.

## 9. Testes

| Suíte | Resultado |
|---|---|
| J1/J2 (até a J2E) | 60/60 |
| Lotes e auditores | 11/11 |
| HC | 5/5 |
| `LEGAL_TARGET_ID` | 90/90 |
| Correlatas | Só as falhas antigas conhecidas, não reexecutadas na rodada final |

## 10. Commits

| Commit | Conteúdo |
|---|---|
| `8f685ad` | J2E dados |
| `4e318ac` | J2E pacotes |
| `9e1dc84` | HC |
| `d2ada99` | Fase D + Batch03 |
| `368e644` | Batch04/05 + cobertura HIGH |
| `a5cb2e3` | Batch06 |
| `1738773` | Batch07 |
| `150ae1c` | Batch08 |
| este commit | relatório parcial |

## 11. Decisões que dependem do usuário

1. Ratificar os Batches 03, 04, 06, 07 e 08 (`J2_*_BACKLOG/J2_BATCHNN_REVIEW.md`).
2. Decidir sobre os tipos novos no aparelho: MS, AP, AI, Inq, Rcl, ADPF, súmula comum e súmulas do TSE/STJ. O firmware hoje exige ID `STF:`.
3. Para o HC, escolher entre deploy do J2E-A agora (só SD) ou aguardar o firmware HC (J2E-B, com gravação de firmware e teste físico).

## 12. Pendências (não executadas)

- **Batch09:** iniciado. As teses dos Temas 841, 184, 201 e 1093 foram lidas no corpus. Falta verificar ADPF 964, HC 70648, ADI 2777 e MI 7300 e decidir os 10.
- **MEDIUM restantes e LOW:** não iniciados.
- **Fases K** (ampliar o registro de revalidação para ADI 5017, ADPF 378 e Rcl 84738), **L** (UI dos Temas 367/387) e **M** (especificação do Updater): não executadas.

```
NEXT_RECOMMENDED_MISSION = ratificação dos Batches 03–08; depois deploy do J2E-A; depois concluir o Batch09 e as fases K/L/M
```
