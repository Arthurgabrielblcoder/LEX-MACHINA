# Reconciliação Macro07 × Macro08 — atualização com o Macro07 final

Branch `reconcile-macro07-macro08`. Checkpoint anterior: `1e8d9ce97904cc3be26b54dceac3c49f6f1fb66b`. Data: 2026-10-11.

Registros históricos preservados sem alteração: `RECONCILIATION_LOG.md` e `RECONCILIATION_AUDIT.json` (reconciliação original, 479 aprovados) e `RECONCILIATION_UPDATE_BATCH06_FINAL.md` (atualização anterior, 561 aprovados). Versão para automação: `RECONCILIATION_UPDATE_MACRO07_FINAL.json`.

Esta etapa é de integração e auditoria. Não houve revisão jurídica nova, alteração de T1 nem aprovação humana nova.

| Entrada | Branch | SHA |
|---|---|---|
| Macro07 final (CLOSED) | `cf-macro-76-175-cloud` | `bc831c539185ecddb04fe0bbcf7bf6eb7fe95783` (conteúdo jurídico `8daf73a`) |
| Macro08 (congelado, não alterado) | `cf-macro-176-250-adct-cloud` | `5c4f1a0c71c5081c5d57622acf9d306edb27904c` |
| Reconciliação anterior | `reconcile-macro07-macro08` | `1e8d9ce97904cc3be26b54dceac3c49f6f1fb66b` |

## Estratégia

Merge controlado `--no-ff` de `bc831c5`, com a ancestralidade Batch06 final → Macro07 final → reconciliação. O Macro08 continua incorporado pelo histórico já existente da reconciliação. Não houve squash, rebase, cherry-pick nem cópia manual de corpus.

- Merge-base: `1cf879f`. Caminhos tocados pelos dois lados desde o merge-base: 0. Conflitos: 0.
- **Dry-run:** `git merge-tree` produziu a árvore `d7e0a97`, idêntica à do merge real.
  - Em relação à reconciliação anterior, a árvore muda exatamente os caminhos que o Macro07 alterou desde `1cf879f`.
  - Em relação ao Macro07, ela mantém o código próprio da reconciliação: `build_entenda_macro_segment.py`, `apply_macro08_human_review.py`, `entenda_text_profile.py`, `editorial/TEXT_PROFILES.json`, perfil `CF88_OFFICIAL_RUNTIME`, `test_entenda_macro_batch08.py` e `test_git_materialization.py` (12 pares).
  - Nenhuma adaptação semântica da reconciliação foi sobrescrita.

## Macro07 recebido

O diretório `production_batch_07_macro` está idêntico a `bc831c5`. Ele traz:
- o corpus final;
- as 7 rodadas humanas (D1, D2, B1, B2, B3, A1, A2), com 249 decisões: 162 sem alteração, 87 ajustadas, 0 rejeitadas, 0 HELD;
- as versões: 162 ACTIVE v1, 87 ACTIVE v2 e 87 RETIRED v1, com `superseded_by`;
- 184 entradas de provenance em 70 T1;
- os snapshots `pre_round_*`, o backlog, `MACRO07_FINAL_CLOSURE_LOG.md`, a apresentação CLOSED, o contrato de fila vazia e os testes generalizados.

Nenhuma decisão foi reconstruída: foram propagados os artefatos reais.

## Regeneração

Builders canônicos (`build_entenda_macro_batch.py`, `build_entenda_macro_segment.py`), cada um com `--determinism 3`, byte-idênticos. O ambiente foi o mesmo da atualização anterior: worktree LF, `PYTHONUTF8=1` e lançador POSIX de caminhos, sem alterar código versionado.

- **Macro07:** a regeneração reproduziu o estado CLOSED com 0 diferenças: 249/249 aprovados, 0 pendentes, filas 0, determinismo verde.
- **Macro08:** mudaram só agregados e apresentação.
  - `MACRO08_BACKLOG.md` e `MACRO08_TRIAGE.json`: os corpora anteriores passam de 382 aprovados + 249 pendentes para **631 aprovados + 0 pendentes**. A tabela "Vide ADI" mostra os 14 targets do Macro07 como `HUMAN_APPROVED_T1`.
  - `MACRO08_HUMAN_REVIEW_PRIORITY.md`: herdou do gerador do Macro07 o contrato genérico de lote fechado ("fechado: nenhuma explicação nova pendente; revisão humana concluída (179 HUMAN_APPROVED_T1 novos…)"), sem tabela vazia.
  - `MACRO08_SCALE_REPORT.md`: tem a métrica de caracteres do arquivo de prioridade e duas correções genéricas de fila vazia em `build_entenda_macro_segment.py`, que são só texto do relatório e já existiam no Macro08 congelado:
    - "Jurisprudência: ." passou a "Jurisprudência: nenhum item pendente.";
    - "0 (None%)" nas linhas CORPO e ADCT passou a "0 (N/A)".
  - `MACRO08_MANIFEST.json`: hashes de código e de arquivos. `DETERMINISM_EVIDENCE.json` foi atualizado pelo mecanismo normal.

Nenhum builder divide por zero ou afirma que há itens aguardando revisão. Nenhum total está hardcodado.

## Contabilidade (derivada dos corpora reais)

Corpora vivos considerados: todos os `*.entenda.jsonl` fora de `history/` e sem `_PRE_` no nome. A contagem é por `explanation_key` ACTIVE.

| | Antes (`1e8d9ce`) | Depois |
|---|---|---|
| `HUMAN_APPROVED_T1` | 561 | **810** = 382 (base e Batch06) + 249 (Macro07) + 179 (Macro08) |
| `PENDING_HUMAN_REVIEW` | 249 (todas do Macro07) | **0** |
| Chaves ACTIVE únicas | 810 | **810** |

- **Delta:** +249 aprovados, −249 pendentes, 0 chaves ACTIVE novas, 0 removidas.
- Os 249 convertidos são exatamente as 249 chaves e os 249 targets do Macro07 final.
- **Interseção:** Macro07 × Macro08 = 0; Macro07 × aprovados anteriores = 0.
- Os 561 aprovados anteriores continuam aprovados. Os 967 registros fora do Macro07 (382 ativos aprovados anteriores, lotes históricos e os 209 do Macro08) ficaram idênticos em conteúdo, versão, status, `human_review` e `superseded_by`.
- **Aprovações perdidas: 0.**

## Unicidade

- `active_conflict` = **0**:
  - nenhum target com duas versões ACTIVE no mesmo corpus;
  - nenhum conflito Macro07 × Macro08;
  - nenhuma chave ACTIVE ao mesmo tempo aprovada e pendente fora dos pares históricos.
- `historical_multi_corpus_presence` = 145: são os pares preexistentes rascunho pendente / final aprovado dos lotes 01–03, iguais aos da reconciliação original. Nenhum envolve o Macro07 ou o Macro08.

## Preservação do Macro08

- **`MACRO08_APPROVALS_PRESERVED = 179/179`.**
- Distribuição do corpus: 149 ACTIVE/HUMAN_APPROVED_T1/v1, 30 ACTIVE/HUMAN_APPROVED_T1/v2 e 30 RETIRED/CHANGES_REQUESTED/v1 (validada).
- 76 dos 94 arquivos versionados do Macro08 estão byte-idênticos a `5c4f1a0`. Entre eles:
  - corpus e par de índice;
  - drafts;
  - decisões humanas e `MACRO08_HUMAN_FLAG_RESOLUTIONS.json`;
  - todos os `*_PRE_HUMAN_REVIEW*`;
  - auditorias estruturais, mapa temporal, anomalias de fonte, registro de SKIP e evidência de transição;
  - entradas editoriais e `MACRO_SPEC`.
- Os 18 restantes são agregados e apresentação regeneráveis:
  - `DETERMINISM_EVIDENCE.json`;
  - os 8 checkpoints (iguais aos da reconciliação anterior);
  - backlog, manifesto e triagem;
  - os pacotes de fila vazia (compacto A/B, rápido C, completo D e HARD_FAIL), a prioridade e o relatório de escala.

## Resoluções e provenance

- `editorial/` está inalterado em relação a `1e8d9ce`, incluindo `T1_KNOWN_RESOLUTIONS.json`.
- As resoluções do Macro07 (`EDITORIAL_INPUT.json`, 21) e do Macro08 (`MACRO08_HUMAN_FLAG_RESOLUTIONS.json`) foram preservadas. Nenhuma resolução nova foi criada.
- A provenance humana dos dois lotes foi preservada no `human_review` dos corpora idênticos. A regeneração não levou nenhum identificador processual para o corpo de T1.

## Verificações

| Verificação | Resultado |
|---|---|
| Batch06 / Macro07 (POSIX + UTF-8) / Macro08 | 40/40 · 72/72 · 30/30 |
| Suíte ENTENDA_ENGINE (worktree LF, Windows, `PYTHONUTF8=1`) | 294 testes (baseline `1e8d9ce`: 250); as mesmas 3 falhas ambientais do baseline; nenhuma regressão |
| Determinismo | Macro07 e Macro08: 3 builds byte-idênticos, iguais ao build no lugar |
| Build limpo em clone completo × versionado | Macro07 e Macro08: 0 diferenças |
| Materialização Git (clone completo, `INDEX`) | PASS: 483/483 arquivos críticos byte-idênticos; 12 pares de índice; 1346/1346 linhas/blocos; 0 problemas |

As 3 falhas ambientais já estão registradas em `RECONCILIATION_LOG.md`:
- `test_entenda_macro_batch07.test_rebuild_is_byte_identical`: separador `\` no Windows;
- `test_entenda_macro_batch07.test_pre_second_pass_history_preserved`: mesma causa;
- `test_git_materialization` dentro de worktree: `.git` é arquivo.

As duas primeiras passam em POSIX; a terceira passa no clone completo.

A aprovação não alterou a quantidade de blocos. Os pares de índice continuam 12 e os blocos continuam 1346, valores derivados no clone e não presumidos.

## Dívidas conhecidas, não bloqueantes

- `KNOWN_PRESENTATION_DEBT`: a frase fixa "nenhuma explicação foi aprovada" em `REVIEW_*_RISK_TRIAGE.md`, gerada por `editorial_checks.py::triage_md`, é compartilhada com artefatos congelados do Batch05 e do Batch06.
- O backlog externo do Macro07 (MB07-01 a MB07-21, incluindo `PENDING_EXTERNAL_INGESTION`) e o do Macro08 não reabrem nenhum lote.
- `PR_METADATA_DEBT`: os textos de PR não foram alterados nesta etapa e não são gate jurídico.

## Propagação

Nenhum merge em `main`. `cf-macro-76-175-cloud` (`bc831c5`), `cf-macro-176-250-adct-cloud` (`5c4f1a0`), `batch06-scale-cloud` (`3cc0cfc`) e `main` (`f1a6966`) não foram alterados.
