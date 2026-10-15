# Macro07 — fechamento técnico final: registro de execução

Data: 2026-10-11 · branch `cf-macro-76-175-cloud` · lote `ENTENDA_CF_MACRO_BATCH_07` (CF/88, arts. 76 a 175) · checkpoint de conteúdo final `8daf73a4b7a67833c879f4f64e75ace16cfbdc80` (rodada A2 aplicada; local = remoto; árvore limpa) · checkpoint final: o commit de fechamento que contém este registro.

Esta etapa não é rodada editorial: nenhum texto jurídico, versão de T1, decisão humana, provenance ou resolução foi alterado. Mudaram apenas a apresentação dos relatórios gerados no estado encerrado (gerador), os testes e este registro, seguindo o padrão do fechamento do Batch06 (`BATCH06_FINAL_CLOSURE_LOG.md`).

**Declaração:** toda a revisão humana T1 do Macro07 foi concluída. Isso não significa que todo o backlog jurídico externo esteja resolvido; os itens não bloqueantes estão separados abaixo.

## Estado final

- Explicações novas do lote: **249** no início da revisão humana; **249** `HUMAN_APPROVED_T1` no fim; **0** `PENDING_HUMAN_REVIEW`.
- Filas A/B/C/D/E = **0/0/0/0/0**; portão de aprovação **249/249 PASS** (0 HARD_FAIL, 0 REVIEW_REQUIRED aberto, 0 achado editorial aberto).
- Acervo global da branch: **631** `HUMAN_APPROVED_T1` (chaves distintas) = **382** herdados do Batch06 (corpus principal 11, Batch01 53, Batch02 50, Batch03 49, Batch04 57, Batch05 69, Batch06 93) + **249** do Macro07. Nenhuma aprovação perdida: os 382 herdados continuam ativos e aprovados.
- Nenhuma chave ACTIVE duplicada (nem por `explanation_key`, nem por `target_id`) nos 8 corpora.
- AUTO_APPROVE_LOW/MEDIUM = OFF e MICROAUTO_APPLY = OFF: toda aprovação veio de rodada humana registrada.

## Rodadas humanas

| Rodada | Arquivo de decisões | Itens | Sem alteração | Ajustados | Rejeitados |
|---|---|---|---|---|---|
| `CF88_MACRO07_TRIAGE_QUEUE_D_PART1` | `MACRO07_ROUND_D1_HUMAN_REVIEW_DECISIONS.json` | 12 (D1–D12) | 1 | 11 | 0 |
| `CF88_MACRO07_TRIAGE_QUEUE_D_PART2` | `MACRO07_ROUND_D2_HUMAN_REVIEW_DECISIONS.json` | 12 (D13–D24) | 0 | 12 | 0 |
| `CF88_MACRO07_TRIAGE_QUEUE_B_PART1` | `MACRO07_ROUND_B1_HUMAN_REVIEW_DECISIONS.json` | 15 (B1–B15) | 4 | 11 | 0 |
| `CF88_MACRO07_TRIAGE_QUEUE_B_PART2` | `MACRO07_ROUND_B2_HUMAN_REVIEW_DECISIONS.json` | 30 (B16–B45) | 22 | 8 | 0 |
| `CF88_MACRO07_TRIAGE_QUEUE_B_PART3` | `MACRO07_ROUND_B3_HUMAN_REVIEW_DECISIONS.json` | 37 (B46–B82) | 15 | 22 | 0 |
| `CF88_MACRO07_TRIAGE_QUEUE_A_PART1` | `MACRO07_ROUND_A1_HUMAN_REVIEW_DECISIONS.json` | 72 (A1–A72) | 64 | 8 | 0 |
| `CF88_MACRO07_TRIAGE_QUEUE_A_PART2` | `MACRO07_ROUND_A2_HUMAN_REVIEW_DECISIONS.json` | 71 (A73–A143) | 56 | 15 | 0 |
| **Total** | 7 arquivos | **249** | **162** | **87** | **0** |

Nenhum item ficou `HELD_FOR_HUMAN_REVIEW` em nenhuma rodada.

## Versionamento e histórico

- 162 aprovados sem alteração continuam em v1, com conteúdo idêntico ao draft; 87 ajustados estão em v2.
- As 87 v1 substituídas permanecem no corpus como `RETIRED / CHANGES_REQUESTED`, cada uma com `superseded_by` apontando para a v2 ativa do mesmo target, e com conteúdo idêntico ao original.
- Todo T1 ativo tem `human_review.review_scope` igual ao da rodada que o decidiu.
- A evidência pré-rodada de cada rodada está congelada em `history/pre_round_<rótulo>/`: corpus, triagem, pacote da fila e backlog de entrada. O histórico do segundo passe está em `history/pre_second_pass/`.
- `drafts/` (saída do segundo passe) não foi alterado por nenhuma rodada: as rodadas aplicam as seções `set` sobre `original_content`, em modo fail-closed.

## Provenance e resoluções

- Provenance de conteúdo: 184 entradas em 70 T1, todas `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE` com URL oficial (Planalto, STF), preservadas em `human_review.content_provenance`. Identificadores processuais ficam fora do corpo do T1 (0 `ENTENDA_EXTERNAL_CASE_CONTENT`).
- Resoluções editoriais (`EDITORIAL_INPUT.json`): 21, inalteradas desde a geração do lote (último commit no arquivo: `3742fc8`, anterior à rodada D1). Nenhuma rodada humana criou resolução para resolver redação.
- `editorial/T1_KNOWN_RESOLUTIONS.json`: inalterado pelo Macro07.

## PENDING_HUMAN_REVIEW = 0 × backlog não bloqueante

`PENDING_HUMAN_REVIEW = 0` encerra a revisão humana T1. Os itens de `BACKLOG_INPUT.json` (MB07-01 a MB07-21) são manutenção externa ou de ferramenta e **não reabrem o Macro07**, porque nenhum afeta a correção dos T1 aprovados:

| Natureza | Itens | Situação |
|---|---|---|
| `PENDING_EXTERNAL_INGESTION`: fontes oficiais já conferidas na revisão, ainda não ingeridas na camada externa com sha256 | MB07-10, MB07-11 (parcial), MB07-13, MB07-14, MB07-16, MB07-17, MB07-18, MB07-20, MB07-21 | ingestão futura na camada externa/JURISPRUDÊNCIA |
| Anomalias de anotação da fonte (Lei Seca congelada não alterada) | MB07-12, MB07-15 (anotações "Vide ADIN 3392"), MB07-19 (remissão do art. 135 às Seções II e III) | verificação futura em fonte oficial; os T1 não dependem da leitura em aberto |
| Texto do runtime e status congelado | MB07-01, MB07-02, MB07-08, MB07-09 | errata ou conferência da fonte em etapa própria |
| Ferramenta (detectores, validador, vigência, seleção) | MB07-03 a MB07-07 | manutenção do motor |
| Dívida de apresentação | frase fixa de `REVIEW_MACRO07_RISK_TRIAGE.md` ("nenhuma explicação foi aprovada"), gerada por `editorial_checks.py::triage_md` | mesmo módulo dos artefatos congelados do Batch05 e do Batch06; corrigir aqui os regeneraria, por isso fica para etapa própria. O arquivo já mostra, logo abaixo, "aprovadas (HUMAN_APPROVED_T1): 249" |

## Apresentação corrigida no gerador

Corrigida no gerador (`build_entenda_macro_batch.py`), sem edição manual de `.md`. A lógica é genérica (rodadas humanas registradas e 0 pendentes) e não fixa número de aprovados. Com pendentes, a saída fica como antes.

1. `MACRO07_MANIFEST.json`: status "IN_HUMAN_REVIEW: 249 ...; 0 pendente(s)" passou a "CLOSED: revisao humana concluida; 249 HUMAN_APPROVED_T1 novos; 0 pendentes".
2. `MACRO07_SCALE_REPORT.md`:
   - cabeçalho com status FECHADO calculado (249/249 em 7 rodadas, 0 pendências);
   - "Papéis das novas" calculado sobre as 249 explicações (BLOCK 44, DEVICE 58, ITEM 29, OVERVIEW 118), antes vazio;
   - nota de que as tabelas de sub-bloco, eixos e filas contam só pendentes;
   - "Jurisprudência:" e "Motivos dos D" sem campo vazio;
   - checks estruturais com "0 aprovação automática" no lugar de "0 aprovado novo".
3. `MACRO07_HUMAN_REVIEW_PRIORITY.md`: sem tabela vazia nem "todas `PENDING_HUMAN_REVIEW`".
4. Já no commit de conteúdo (`8daf73a`), o segundo passe ganhou o contrato de fila vazia do fix do Batch06: o pacote D diz "nenhum item pendente nesta fila." e o percentual de D é N/A, sem divisão por zero.
5. Este registro passou a ser entrada versionada do lote (`root_inputs`), e não arquivo gerado.

## Gates e testes (commit de conteúdo `8daf73a`)

- Portão: 249/249 PASS; checks estruturais PASS; 0 `ENTENDA_EXTERNAL_CASE_CONTENT` e 0 `TRANSITION_IN_CORE` no corpo.
- `tests/test_entenda_macro_batch07.py` em modo POSIX + UTF-8: 68/68 OK (rodadas D1, D2, B1, B2, B3, A1 e A2, mais as classes do lote e do segundo passe).
- `tests/test_entenda_batch06.py`: 40/40 OK.
- Suíte ENTENDA_ENGINE completa (Windows): 260 testes, com as mesmas 3 falhas ambientais do baseline `57b8d5e`:
  - `test_rebuild_is_byte_identical`: separador de caminho do Windows no manifesto;
  - `test_pre_second_pass_history_preserved`: mesma causa;
  - `test_critical_artifacts_byte_identical_after_checkout`: num worktree, `.git` é arquivo.
  
  Nenhuma regressão. As duas primeiras passam em POSIX, e a terceira passa num clone completo.
- Determinismo: 3 builds byte-idênticos.
- Build limpo num clone completo × build no lugar: os 118 arquivos versionados do lote ficam idênticos.
- Materialização Git num clone completo: OK.

Os mesmos gates foram repetidos no commit de fechamento; o resultado está na mensagem do commit.

## Propagação

Nenhuma. `reconcile-macro07-macro08`, `batch06-scale-cloud`, `cf-macro-176-250-adct-cloud` e `main` não foram alterados; nenhum merge, rebase ou cherry-pick. A propagação para a reconciliação é a próxima etapa, controlada separadamente.
