# Batch06 — correção de compatibilidade do módulo de pacotes: registro de execução

Data: 2026-10-10 · branch `batch06-scale-cloud` · checkpoint de partida `67df0053cf95fdbfe7b1606fe09bea77daa09316` (fechamento formal do Batch06).

## Motivo

O dry-run de propagação (Batch06 → Macro07 → reconciliation) encontrou uma regressão no módulo compartilhado `t1_batch_packets.py`, introduzida no fechamento formal:

1. **`metrics()`:** com 0 pendentes, gravava `reduction_abs` e `reduction_pct` como `None`. O builder do Macro08 (`build_entenda_macro_segment.py`, sobre o `build_entenda_macro_batch._n` do Macro07) formata esses campos como número. No estado combinado, o rebuild do Macro08 falhava com `TypeError`.
2. **Shells de fila vazia:** passaram a dizer "fila X encerrada", o que descreve o lote e não a fila. Num lote ainda em revisão, como o Macro07, uma fila vazia não significa revisão encerrada.

## Correção

Mudou apenas `t1_batch_packets.py`:

- `metrics()` volta a ter contrato numérico. Sem pendentes: `old_model_full_package_chars` = 0, `reduction_abs` = 0, `reduction_pct` = 0.0 e `pending_items` = 0. Exibir "N/A — não existem mais itens pendentes" continua sendo decisão do builder do Batch06 (`scale_report`), que não mudou.
- Shells de fila vazia com texto neutro, que só descreve a fila:
  - A/B: "nenhum item pendente nas filas A e B";
  - C e D: "nenhum item pendente nesta fila";
  - E: "nenhum item pendente com HARD_FAIL nesta fila".

  O status `CLOSED` do Batch06 continua vindo só do relatório próprio do lote.

Artefatos regenerados deterministicamente:
- os quatro shells;
- `BATCH06_SCALE_REPORT.md` (só a contagem de caracteres dos pacotes; o N/A foi mantido);
- `BATCH06_TRIAGE.json` (`metrics`, `d_full_package` inalterado);
- `BATCH06_MANIFEST.json` (hash do módulo e dos arquivos);
- `DETERMINISM_EVIDENCE.json`.

## Integridade

- Snapshot antes e depois: 613 registros (382 ativos `HUMAN_APPROVED_T1`) idênticos em conteúdo, notas, `human_review`, versão, status e `superseded_by`. Corpora, drafts, 8 arquivos de decisão, `EDITORIAL_REVIEW_INPUT.json` e `T1_KNOWN_RESOLUTIONS.json` estão iguais byte a byte.
- 93 decisões (19 APPROVED, 74 APPROVED_AFTER_ADJUSTMENT, 0 rejeitadas); 74 RETIRED / CHANGES_REQUESTED com `superseded_by` íntegro.
- Filas A/B/C/D/E = 0; portão de aprovação 93/93; `B26_RESOLUTION_REVALIDATION: VALID`.

## Verificações

- `tests/test_entenda_batch06.py`: 40/40 PASS.
  - Teste novo: `test_shared_packet_metrics_numeric_contract_without_pending`, que confere o contrato numérico e a formatação dos builders macro.
  - Testes de shells e de volume ajustados ao contrato neutro. O teste de volume continua exigindo o N/A no relatório e proíbe "0 (0.0%)" nele.
- Suíte ENTENDA_ENGINE completa: 192/192 PASS.
- Determinismo: 3 builds byte-idênticos entre si e ao build no lugar (18 arquivos).
- Materialização Git: conferida no índice antes do commit e no HEAD depois.

Nenhuma propagação; Macro07, Macro08, reconciliation e `main` não foram alterados.
