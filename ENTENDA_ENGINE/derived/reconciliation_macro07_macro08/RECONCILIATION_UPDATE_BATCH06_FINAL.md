# Reconciliação Macro07 × Macro08 — atualização com o Batch06 final

Branch `reconcile-macro07-macro08`. Checkpoint anterior `8ef73128bd5761a321bd2e8e68c11e780e0642b7`. `RECONCILIATION_LOG.md` e `RECONCILIATION_AUDIT.json` foram mantidos sem alteração: são o registro histórico da reconciliação original (479 aprovados).

| Entrada | Branch | SHA |
|---|---|---|
| Batch06 final (CLOSED, compatível) | `batch06-scale-cloud` | `3cc0cfcd8edfd06dc7b1eecdfe5fe860a21445f2` |
| Macro07 com o Batch06 final | `cf-macro-76-175-cloud` | `1cf879f61433b6abb03238dbdb0e544a5d357d9b` (merge `--no-ff` de `3cc0cfc` sobre `c963acd`) |
| Macro08 (congelado, não alterado) | `cf-macro-176-250-adct-cloud` | `5c4f1a0c71c5081c5d57622acf9d306edb27904c` |

## Estratégia

Merge controlado `--no-ff` da nova ponta do Macro07 (`1cf879f`), cuja ancestralidade já traz o Batch06. Não houve importação separada do Batch06 nem reimportação do Macro08.

- Merge-base: `c963acd`. Interseção de paths desde ele: 0. Conflitos: 0.
- Antes da propagação, um dry-run provou por `git merge-tree` que a árvore resultante de Batch06 → Macro07 → reconciliation é idêntica à simulada.

## Regeneração

Os agregados foram regenerados pelos builders canônicos (`build_entenda_macro_batch.py`, `build_entenda_macro_segment.py`), cada um com `--determinism 3`, byte-idêntico.

- **Ambiente:** worktree LF e `PYTHONUTF8=1`. A serialização de caminhos foi feita em POSIX por um lançador que, só no namespace do builder do Macro07, faz `str(Path)` devolver `as_posix()`, exatamente o que o Linux devolve. O código versionado não foi alterado.
- **Prova de equivalência com o Cloud:** o mesmo procedimento sobre `c963acd` e sobre `8ef7312` reproduziu byte a byte todos os artefatos versionados (0 diferenças).
- **Macro07:** os agregados ficaram idênticos aos de `1cf879f`.
- **Macro08:** o build completou normalmente (sem `TypeError`). Mudaram só agregados e apresentação:
  - `MACRO08_BACKLOG.md`: corpora anteriores de 300 aprovados + 331 pendentes para 382 aprovados + 249 pendentes;
  - `MACRO08_TRIAGE.json`: `backlog` e `metrics`;
  - `MACRO08_MANIFEST.json`: hashes de `t1_batch_packets.py` e dos arquivos;
  - `DETERMINISM_EVIDENCE.json`;
  - os pacotes de fila vazia (`MACRO08_COMPACT_AB_REVIEW.md`, `MACRO08_QUICK_C_REVIEW.md`, `MACRO08_FULL_D_REVIEW.md`, `MACRO08_HARD_FAIL_REPORT.md`) passam a ter texto neutro ("nenhum item pendente nesta fila");
  - `MACRO08_SCALE_REPORT.md`: a redução sai de "-1.212 (-2286.8%)" para "0 (0.0%)", com contrato numérico neutro sem pendentes.
- **Teste:** `test_entenda_macro_batch08.test_prior_batches_untouched` passou a derivar a contagem dos corpora anteriores da mesma fonte do builder (corpus principal + `prior_corpora` do `MACRO_SPEC`, sem o próprio Macro08), em vez do literal 300.

## Preservação do Macro08

Na árvore final, 92 dos 110 arquivos do Macro08 estão byte-idênticos a `5c4f1a0`. Estão nesse grupo:
- corpus `CF88_MACRO_08.entenda.jsonl` e par de índice;
- os 34 drafts;
- decisões humanas (`MACRO08_HUMAN_REVIEW_DECISIONS*.json` e `MACRO08_ROUND_FINAL_HUMAN_REVIEW_DECISIONS.json`) e `MACRO08_HUMAN_FLAG_RESOLUTIONS.json`;
- registro de aplicação e metadados;
- todos os `*_PRE_HUMAN_REVIEW*`;
- auditorias estruturais, mapa temporal, anomalias de fonte, registro de SKIP e evidência de transição;
- entradas editoriais e `MACRO_SPEC`.

Os 18 restantes são:
- os 13 agregados já regenerados na reconciliação original: builder de segmento, `DETERMINISM_EVIDENCE.json`, os 8 checkpoints (sem mudança nesta atualização), backlog, manifesto e triagem;
- os 5 pacotes e relatórios de apresentação acima.

179/179 continuam `HUMAN_APPROVED_T1`.

## Contagens (derivadas dos corpora reais)

| | Antes (`8ef7312`) | Depois |
|---|---|---|
| `HUMAN_APPROVED_T1` (chaves únicas) | 479 | **561** = 289 anteriores ao Batch06 + 93 do Batch06 + 179 do Macro08 |
| `PENDING_HUMAN_REVIEW` | 331 (82 do Batch06 + 249 do Macro07) | **249** (todas do Macro07) |
| Chaves ACTIVE únicas | 810 | **810** = 561 + 249 |

- **Integridade das aprovações:**
  - 0 aprovações perdidas; os 479 anteriores mantêm versão e conteúdo idênticos;
  - os 82 novos são do Batch06;
  - 0 Macro07 promovidos, 0 Macro08 ou Batch06 revertidos.
- **Unicidade:**
  - 0 conflitos de chave e nenhum target com duas versões ativas no mesmo corpus;
  - as 145 chaves presentes em mais de um corpus são só os pares preexistentes rascunho pendente / final aprovado dos lotes 01–03.

## Verificações

| Verificação | Resultado |
|---|---|
| Batch06 / Macro07 / Macro08 | 40/40 · 26 PASS + 2 ambientais · 30/30 |
| Suíte ENTENDA_ENGINE (worktree LF, `PYTHONUTF8=1`) | 250 testes: 245 PASS, 2 SKIP, 3 falhas ambientais preexistentes, iguais no baseline |
| Determinismo | Macro07 e Macro08: 3 builds + build no lugar byte-idênticos |
| Materialização Git | conferida a partir do checkout principal (`--source`), antes e depois do commit |

As 3 falhas ambientais são as já registradas em `RECONCILIATION_LOG.md`:
- `test_entenda_macro_batch07.test_rebuild_is_byte_identical`: o builder chamado direto no Windows grava `\` no manifesto;
- `test_entenda_macro_batch07.test_pre_second_pass_history_preserved`: o teste compara com `str(relative_to)`;
- `test_git_materialization` dentro de worktree: `.git` é arquivo.

Dívida conhecida, não corrigida: `KNOWN_PRESENTATION_DEBT` em `REVIEW_BATCH_06_RISK_TRIAGE.md`. A frase fixa "nenhuma explicação foi aprovada" vem de `editorial_checks.py::triage_md` e também aparece no Batch05.

Nenhum merge em `main`; Macro08 não foi alterado; nenhuma revisão humana do Macro07 foi iniciada.
