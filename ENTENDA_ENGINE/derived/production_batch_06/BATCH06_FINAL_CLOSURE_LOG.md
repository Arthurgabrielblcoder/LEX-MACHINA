# Batch06 — fechamento formal final: registro de execução

Data: 2026-10-10 · branch `batch06-scale-cloud` · checkpoint de partida `8b3ec1e0eb733847b65487e3473023b94cbaf7c3` (rodada A3 aplicada; local = remoto; árvore limpa) · checkpoint final: o commit de fechamento que contém este registro.

Esta etapa não é rodada editorial: nenhum texto jurídico, versão de T1, decisão humana ou resolução foi alterado. Mudaram apenas a apresentação dos relatórios gerados (builder e módulo de pacotes), os testes e este registro.

## Premissas conferidas antes de qualquer alteração

- HEAD local = `origin/batch06-scale-cloud` = `8b3ec1e`; 0 arquivos rastreados modificados.
- `HUMAN_APPROVED_T1`: 382 ativos (chaves distintas) nos corpora aprovados; 0 `PENDING_HUMAN_REVIEW`.
- Filas A/B/C/D/E = 0/0/0/0/0; portão de aprovação 93/93 PASS.
- 93 decisões humanas (19 `APPROVED`, 74 `APPROVED_AFTER_ADJUSTMENT`, 0 rejeitadas) em 8 rodadas; revalidação do B26 = `VALID`.

## Estado final

- Acervo `HUMAN_APPROVED_T1`: 289 antes do Batch06 → **382** depois (+93). Os 3 pilotos reutilizados (`CF88:ART.60`, `CF88:ART.60:PAR.4`, `CF88:ART.60:PAR.4:INC.IV`) já estavam aprovados e não entram no incremento.
- SELECT 96 = 93 explicações novas + 3 pilotos reutilizados. Batch06 novos pendentes: **0**. Filas A 0, B 0, C 0, D 0, E 0.
- Decisões por rodada:

| Rodada | Itens | Sem alteração | Ajustados | Rejeitados |
|---|---|---|---|---|
| `CF88_BATCH06_TRIAGE_QUEUE_D` | 11 | 2 | 9 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_C` | 13 | 8 | 5 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_B_PART1` | 9 | 1 | 8 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_B_PART2` | 9 | 1 | 8 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_B_PART3` | 9 | 0 | 9 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_A_PART1` | 15 | 2 | 13 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_A_PART2` | 15 | 4 | 11 | 0 |
| `CF88_BATCH06_TRIAGE_QUEUE_A_PART3` | 12 | 1 | 11 | 0 |
| **Total** | **93** | **19** | **74** | **0** |

- Versionamento: as 74 v1 substituídas permanecem como `RETIRED / CHANGES_REQUESTED`, cada uma com `superseded_by` apontando para a v2 ativa do mesmo target; os 19 aprovados sem alteração estão em v1 e os 74 ajustados em v2; nenhum target com duas versões ativas; toda aprovação ativa tem `human_review` igual à decisão e ao escopo registrados.
- `AUTO_APPROVE_LOW` = false, `AUTO_APPROVE_MEDIUM` = false, `MICROAUTO_APPLY` = false (0 microajustes aplicados); nenhuma decisão automática.

## Problemas de apresentação corrigidos

Corrigidos no gerador (`build_entenda_batch06_candidate.py::scale_report`, `triage_history`, `manifest`; `t1_batch_packets.py::compact/quick/full/hard/metrics`), não por edição manual dos `.md`. A lógica é genérica (estado `pendentes == 0` e snapshots versionados por rodada), sem número fixo de aprovados.

1. **WIP no relatório de escala:** o cabeçalho fixo "WIP: nenhum ENTENDA do Batch06 aprovado" deu lugar a um status calculado. Com 0 pendentes o texto é "FECHADO: revisão jurídica humana concluída para todas as explicações novas do lote (93/93 aprovadas após revisão humana; 0 pendências; os 3 pilotos reutilizados já estavam aprovados)", com AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY em OFF. O status do `BATCH06_MANIFEST.json`, antes "WIP_CANDIDATE: 0 HUMAN_APPROVED_T1; nada aprovado", passou a "CLOSED: revisao humana concluida; 93 HUMAN_APPROVED_T1 novos; 0 pendentes".
2. **Tabelas de risco e filas:** a seção "Estado atual das pendências" declara que conta só itens pendentes (todos 0). Ganhou a subseção "Histórico da triagem", lida de `BATCH06_TRIAGE_PRE_ROUND_D.json`, a triagem recalibrada congelada antes da primeira rodada humana, com 93 pendentes:
   - LEGAL_RISK: LOW 46, MEDIUM 36, HIGH 11;
   - VERIFICATION_COMPLEXITY: SIMPLE 5, STRUCTURED 59, EXTERNAL 29;
   - jurisprudência: NONE 72, CONTEXT_ONLY 15, REQUIRED_FOR_CORRECTNESS 6.

   A tabela de filas mostra três colunas: agora, triagem recalibrada e checkpoint pré-recalibração.
3. **Migração dos D antigos:** agora é calculada a partir de `PRE_RECALIBRATION_MANIFEST.json`, que confirma 89 itens D, cruzado com a triagem recalibrada:
   - 78 saíram de D: A 38, B 27, C 13; 11 ficaram em D;
   - destino final: 89/89 `HUMAN_APPROVED_T1` (18 sem alteração, 71 ajustados);
   - por rodada: D 11, C 13, B1 9, B2 9, B3 9, A1 14, A2 14, A3 10.

   O histórico também foi gravado em `BATCH06_TRIAGE.json` (`triage_history`). O campo `migration` continua descrevendo só os pendentes atuais e agora traz `scope` explícito.
4. **Cabeçalho "Rodada D (revisão jurídica humana dos 11 itens D)":** passou a "Revisão jurídica humana consolidada (BATCH06)". Inclui uma tabela das 8 rodadas componentes, com arquivo de decisões e contagens; a tabela por target ganhou a coluna da rodada; o número de rejeitados agora vem dos arquivos de decisão.
5. **Contagem final:** "289 antes → 382 depois (+93 do lote; os 3 pilotos reutilizados não são contados de novo)". A frase "Batch06 novos ainda pendentes: 0 (A, B e C não foram decididos)" passou a "Novos pendentes do lote: 0. Todas as filas de revisão humana foram concluídas."
6. **Motivos dos D pendentes:** com a fila D vazia, a seção diz "Nenhum item D permanece pendente (fila D encerrada)". Os motivos históricos dos 11 D aparecem no histórico da triagem.
7. **Campos vazios:**
   - "Papéis das novas" passou a ser calculado sobre as 93 explicações novas da seleção: BLOCK 25, DEVICE 25, ITEM 10, OVERVIEW 33;
   - "Jurisprudência:" vazio passou a "nenhum item pendente";
   - "Risco no checkpoint" vem do checkpoint: HIGH 89, LOW 3, MEDIUM 1;
   - "Falsos positivos" vazio passou a "nenhum item pendente".
8. **Métricas de volume:** com 0 pendentes, `old_model_full_package_chars` = 0 e `reduction_abs`/`reduction_pct` = null (antes: modelo antigo 53 e redução -840, -1584,9%). O relatório mostra:
   - itens pendentes 0 e conteúdo pendente 0;
   - os pacotes atuais como cabeçalhos de filas vazias;
   - redução "N/A — não existem mais itens pendentes".

   A comparação histórica usa as métricas registradas em `BATCH06_TRIAGE_PRE_ROUND_D.json` (93 pendentes, redução de 60,8%) e `BATCH06_TRIAGE_PRE_ROUND_A3.json` (12 pendentes, redução de 62,8%), com a fonte identificada.
9. **`BATCH06_COMPACT_CLEAN_REVIEW.md`:** "nenhum item aprovado" passou a "filas A e B encerradas: nenhuma revisão pendente nas filas A e B". Cada seção vazia mantém "nenhum item nesta fila".
10. **Shells C/D/E:**
    - `BATCH06_QUICK_REVIEW.md` diz "fila C encerrada: nenhum item pendente";
    - `BATCH06_FULL_HUMAN_REVIEW.md` diz "fila D encerrada: nenhum item pendente", sem o "nenhum aprovado" e sem o índice vazio;
    - `BATCH06_HARD_FAIL_REPORT.md` diz "fila E encerrada: nenhum item pendente com HARD_FAIL".

    Os arquivos continuam gerados por contrato.
11. **"Pacote D: GERADO":** com D = 0, o relatório diz "Artefato D: gerado, sem itens pendentes (arquivo mantido por contrato determinístico)", e `d_full_package` = `GERADO_SEM_ITENS_PENDENTES`.
12. **ROUND_0B:** a seção passou a "Correções editoriais da recalibração (ROUND_0B)". Os números históricos (21 edições em 19 explicações) vêm de `RECALIBRATION_EDITORIAL_LOG.json` e não são atribuídos à rodada A3.

Fora do escopo, sem alteração: a frase fixa de `REVIEW_BATCH_06_RISK_TRIAGE.md` ("nenhuma explicação foi aprovada: todas seguem PENDING_HUMAN_REVIEW") vem de `editorial_checks.py::triage_md`. O mesmo módulo gera o artefato congelado do Batch05, com a mesma frase. Corrigi-la regeneraria artefatos do Batch05, então ela fica registrada como pendência de apresentação para etapa própria. O próprio arquivo já informa, na linha seguinte, "aprovadas (HUMAN_APPROVED_T1): 93".

## Integridade jurídica (nenhum T1 mudou)

Snapshot antes e depois da regeneração, com sha256 do conteúdo canônico de cada registro: `content`, `external_layer_notes`, `human_review`, `target_id`, `editorial_version`, `status`, `review_status` e `superseded_by`. O snapshot cobre o corpus principal, os corpora anteriores e o corpus do Batch06.

- 613 registros (382 ativos aprovados) idênticos; mesmas 382 chaves aprovadas; mesmos targets, versões, status e decisões.
- Iguais byte a byte (LF): todos os corpora, `BATCH_06_DRAFTS.json`, os 8 `ROUND_*_HUMAN_REVIEW_DECISIONS.json`, `EDITORIAL_REVIEW_INPUT.json` (incluindo as `resolutions`) e `editorial/T1_KNOWN_RESOLUTIONS.json`.
- Teste permanente `test_closure_did_not_change_t1_decisions_or_resolutions`: compara corpus, drafts, decisões e resoluções com o checkpoint `8b3ec1e`.

## Auditoria de resoluções

- **Resoluções editoriais** (`EDITORIAL_REVIEW_INPUT.json`, 14):
  - 11 disparadas e aplicadas:
    - `CF88:ART.42:PAR.3` EXCEPTION_NOT_IN_TEXT;
    - `CF88:ART.43` ABSOLUTE_CLAIM;
    - `CF88:ART.57:PAR.2` EXAMPLE_NUMBER;
    - `CF88:ART.57:PAR.7` ABSOLUTE_CLAIM;
    - `CF88:ART.58` LAW_DEPENDENCY_OMITTED;
    - `CF88:ART.62` MODALITY_SHIFT;
    - `CF88:ART.63` ABSOLUTE_CLAIM;
    - `CF88:ART.64:PAR.2` EXCEPTION_NOT_IN_TEXT;
    - `CF88:ART.71` LAW_DEPENDENCY_OMITTED;
    - `CF88:ART.74` LAW_DEPENDENCY_OMITTED;
    - `CF88:ART.75` TRANSITION_IN_CORE.
  - 3 históricas preservadas e não mais disparadas: `CF88:ART.47` TRANSITION_IN_CORE, `CF88:ART.55:INC.VI` ABSOLUTE_CLAIM e `CF88:ART.58:PAR.2` LAW_DEPENDENCY_OMITTED.
  - Nenhum achado disparado sem resolução registrada.
- **Resoluções conhecidas** (`T1_KNOWN_RESOLUTIONS.json`): 10 entradas de explicações do Batch06, todas ativas e disparadas.
- **Revalidações concluídas:**
  - A1: `CF88:ART.42:PAR.3` MANTIDA_APLICAVEL; `CF88:ART.47` MANTIDA_SEM_USO_NA_V2.
  - A2: `CF88:ART.57:PAR.2`, `CF88:ART.57:PAR.7`, `CF88:ART.58` e `CF88:ART.64:PAR.2` MANTIDA_APLICAVEL; `CF88:ART.58:PAR.2` MANTIDA_SEM_USO_NA_V2.
  - A3: `CF88:ART.74` LAW_DEPENDENCY_OMITTED MANTIDA_APLICAVEL com `B26_RESOLUTION_REVALIDATION: VALID`.
- **B26:** `CF88:ART.74:PAR.2` (v2, `HUMAN_APPROVED_T1`) mantém "na forma da lei" no O QUE DIZ e explica no O QUE SIGNIFICA que os requisitos e a forma de apresentação da denúncia dependem da disciplina legal aplicável.
  - O `pending_revalidation` da rodada B3 é registro histórico, resolvido em `ROUND_A3_HUMAN_REVIEW_DECISIONS.json` (`pending_revalidation_resolved`).
  - Nenhum `pending_revalidation` operacional aberto (`pending_revalidation` da A3 = []).
- Nenhum registro histórico foi apagado.

## Gates

- Portão de aprovação: 93/93 PASS; 0 HARD_FAIL; 0 REVIEW_REQUIRED; 0 EDITORIAL_CHECK_UNRESOLVED (0 achados editoriais não resolvidos).
- `tests/test_entenda_batch06.py`: 39/39 PASS (35 anteriores + 4 do fechamento: relatório final, shells das filas vazias, métricas sem pendentes e integridade de T1/decisões/resoluções; a regressão da migração passou a conferir `triage_history` contra os snapshots versionados).
- Suíte ENTENDA_ENGINE completa: 191/191 PASS.
- Determinismo: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` → 3 builds byte-idênticos entre si e ao build no lugar (18 arquivos; `DETERMINISM_EVIDENCE.json` atualizado pelo mecanismo normal).
- Materialização Git (`git_materialization_check.py`): conferida no índice antes do commit e no HEAD depois.

## Código

- `build_entenda_batch06_candidate.py`:
  - `scale_report` reescrito para o estado encerrado;
  - novas funções `round_snapshot` (snapshot pré-rodada versionado) e `triage_history` (histórico gravado em `BATCH06_TRIAGE.json`);
  - status do manifesto e `d_full_package` calculados;
  - docstring atualizada.

  Sem mudança em `INPUTS`, seleção, drafts, validators, classificação, resoluções ou portão.
- `t1_batch_packets.py`: cabeçalhos dos shells A–E conforme haja ou não pendentes; `metrics` sem modelo antigo e sem redução quando não há pendentes (`pending_items` registrado).
- `tests/test_entenda_batch06.py`: 4 testes novos e a regressão da migração estendida.

## Propagação

Nenhuma. `main`, `cf-macro-76-175-cloud`, `cf-macro-176-250-adct-cloud` e `reconcile-macro07-macro08` não foram alterados; nenhum merge, rebase, cherry-pick ou resolução de PR.
