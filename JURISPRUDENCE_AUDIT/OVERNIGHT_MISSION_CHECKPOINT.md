# OPERAÇÃO NOTURNA — CHECKPOINT CENTRAL

> Consultar antes de qualquer fase, para não repetir trabalho. É atualizado a cada fase ou lote.

## Estado

| Item | Valor |
|---|---|
| Branch | `cf-jurisprudence-audit` (sem merge em main, sem tag, sem force push) |
| Fase atual | **H (MEDIUM)**; Batch08 concluído · próxima: Batch09 MEDIUM, depois as fases K/L/M e o relatório final |
| Baseline físico | J2C: **261 vínculos / 160 targets** (instalado, 12/12) |
| Candidatos preparados (NÃO instalados) | J2E-A (268/166, firmware atual) · J2E-B (269/167, exige firmware HC) |
| Firmware HC | protótipo compilado host-only (`169b6619…`); base reproduzida (= `6e329c91…` exceto metadados); **não gravado** |

## Guardrails (mantidos)

```
MICROSD_TOUCHED = NO · ESP32_FLASHED = NO · PHYSICAL_BASELINE_CHANGED = NO · MAIN_MERGED = NO · FROZEN_LAYERS_MODIFIED = NO
UNRATIFIED_JURIS_RELATIONS_PUBLISHED = 0 · UNRATIFIED_DECISIONS_MARKED_HUMAN_APPROVED = 0 · DEVICE_DEPLOY = NO
```

## Lotes

| Lote | Nível | Arquivo | Estado |
|---|---|---|---|
| 01 | HIGH | `J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json` | ratificado; instalado (J2C) |
| 02 | HIGH | `J2_HIGH_BACKLOG/J2D_BATCH02_DECISIONS.json` | ratificado; candidato J2E |
| 03 | HIGH | `J2_HIGH_BACKLOG/J2_BATCH03_DECISIONS.json` | aguardando ratificação |
| 04 | HIGH | `J2_HIGH_BACKLOG/J2_BATCH04_DECISIONS.json` | aguardando ratificação (5 itens; HIGH esgotado) |
| 05 | HIGH | `J2_HIGH_BACKLOG/J2_BATCH05_DECISIONS.json` | vazio (fechamento HIGH) |
| 06 | MEDIUM | `J2_MEDIUM_BACKLOG/J2_BATCH06_DECISIONS.json` | aguardando ratificação |
| 07 | MEDIUM | `J2_MEDIUM_BACKLOG/J2_BATCH07_DECISIONS.json` | aguardando ratificação |
| 08 | MEDIUM | `J2_MEDIUM_BACKLOG/J2_BATCH08_DECISIONS.json` | aguardando ratificação (1 UNRESOLVED: STJ bloqueado) |

**Como gerar o próximo lote:**

```
python -I -B -X utf8 JURISPRUDENCE_AUDIT/build_j2_batch.py --batch N --level MEDIUM --selection-only
```

Depois:

1. Pesquisar os candidatos em fonte oficial.
2. Escrever `J2_MEDIUM_BACKLOG/j2_batchNN_review.py` (`REVIEW` + `SOURCES`).
3. Gerar as decisões: `build_j2_batch.py --batch N --level MEDIUM`.
4. Gerar o relatório: `render_j2_batch_report.py --batch N --level MEDIUM`.
5. Rodar `tests/test_j2_batches.py`.

## Ferramentas criadas na operação

| Ferramenta | Função |
|---|---|
| `apply_j2e_batch02_overlay.py` + `LEGAL_TARGET_ID/build_export_run10_juris_j2e.py` + `build_j2e_candidate.py` + `build_j2e_isolation_audit.py` | Fases A/B |
| `HC_FIRMWARE_PROTOTYPE/build_hc_firmware_prototype.py` + `hc_type.patch` | Fase C |
| `j2_auditors.py` (alertas) + `j2_review_common.py` (validador) + `build_j2_batch.py` (seletor genérico) + `render_j2_batch_report.py` | Fases D–H |

**Testes de cada fase:** `test_j2e`, `test_hc_prototype`, `test_j2_auditors`, `test_j2_batches`.

## Bloqueios registrados

| Bloqueio | Situação |
|---|---|
| STJ (`scon.stj.jus.br`) | Desafio anti-robô; não contornado. Súmula 403 = UNRESOLVED_EXTERNAL |
| `constituicao.stf.jus.br` ("A Constituição e o Supremo") | Não carrega no navegador embutido; ADIs verificadas pela pesquisa de jurisprudência |
| Dívida do header em `firmware/` (122 fichas) | Não corrigida (guard das Correlatas); não bloqueia o protótipo HC, que usa o header versionado de 124 fichas |

## Commits relevantes

| Commit | Conteúdo |
|---|---|
| `8f685ad` | J2E dados |
| `4e318ac` | J2E pacotes |
| `9e1dc84` | HC |
| `d2ada99` | Fase D + Batch03 |
| `368e644` | Batch04/05 + cobertura HIGH |
| `a5cb2e3` | Batch06 |
| `1738773` | Batch07 |
| (próximo) | Batch08 |
