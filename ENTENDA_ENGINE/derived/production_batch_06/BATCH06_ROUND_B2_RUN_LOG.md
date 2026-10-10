# Batch06 — rodada B2 (fila B, itens B10–B18): registro de execução

Data: 2026-10-09 · branch `batch06-scale-cloud` · checkpoint de partida `3a1a4234f13dc6839701fa68af9c827b279f389e`.

## Decisões aplicadas

Decisões humanas B10–B18 de 2026-10-09 e complementações do mesmo dia, registradas em `ROUND_B2_HUMAN_REVIEW_DECISIONS.json` (escopo `CF88_BATCH06_TRIAGE_QUEUE_B_PART2`). Os 9 itens são os itens 10 a 18 dos 27 da fila B, em ordem estrutural da Constituição. A rodada final foi reaplicada do zero a partir do checkpoint, sem aproveitar estado de testes anteriores.

Complementações autorizadas (eliminam alertas pela própria redação, sem resolução registrada):

- B11: "responde a processo que vise à perda do mandato ou que possa levar a ela" — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (a redação anterior repetia 12 palavras seguidas da Lei Seca; maior sequência literal agora: 5);
- B12: "o afastamento não pode ultrapassar cento e vinte dias por sessão legislativa" — elimina `LIST_ITEM_POSSIBLY_DROPPED`;
- B16, ATENÇÃO: "A matéria, porém, pode voltar a ser proposta nas condições do art. 67…" — elimina `ABSOLUTE_CLAIM` ("jamais");
- B16, O QUE SIGNIFICA: "O projeto de lei aprovado por uma das Casas…" — elimina `LAW_DEPENDENCY_OMITTED`.

Glossários: B10 sem "Imunidade parlamentar"; B14 com "Limite material" redefinido e usado no texto; B16 sem "Arquivamento" e com "Casa iniciadora"; B17 com Sanção, Veto e Promulgação redefinidos; B18 sem "Veto jurídico".

| Item | Target | Decisão humana | Versão final |
|---|---|---|---|
| B10 | `CF88:ART.55:PAR.1` | ADJUST_THEN_APPROVE | v2 |
| B11 | `CF88:ART.55:PAR.4` | ADJUST_THEN_APPROVE | v2 |
| B12 | `CF88:ART.56` | ADJUST_THEN_APPROVE | v2 |
| B13 | `CF88:ART.57:PAR.4` | APPROVE | v1 (byte-idêntico) |
| B14 | `CF88:ART.62:PAR.1` | ADJUST_THEN_APPROVE | v2 |
| B15 | `CF88:ART.62:PAR.5` | ADJUST_THEN_APPROVE | v2 |
| B16 | `CF88:ART.65` | ADJUST_THEN_APPROVE | v2 |
| B17 | `CF88:ART.66` | ADJUST_THEN_APPROVE | v2 |
| B18 | `CF88:ART.66:PAR.1` | ADJUST_THEN_APPROVE | v2 |

As v1 dos 8 ajustados permanecem no corpus como RETIRED / CHANGES_REQUESTED (`superseded_by` → v2).

## Alertas

- Nenhuma resolução registrada em `T1_KNOWN_RESOLUTIONS.json` nem em `EDITORIAL_REVIEW_INPUT.json`.
- Eliminados pela redação: os quatro acima e `TERM_NOT_USED` de "Imunidade parlamentar" (B10), "Limite material" (B14), "Arquivamento" (B16).
- Avisos informativos remanescentes (lint, não bloqueiam): `NEAR_COPY_OF_OFFICIAL_TEXT` em B10 e B14 (abaixo do limite de cópia do contrato) e `JURISPRUDENCE_WORDING_IN_BODY` em B15 (roteamento para a camada JURISPRUDÊNCIA, sem afirmação jurisprudencial).
- Mapa de risco: só B15 mudou (sai `INTERPRETIVE_QUESTION_DEFERRED`, porque a nova ATENÇÃO não usa mais "tema de interpretação constitucional"); continua MEDIUM e CONTEXT_ONLY.

## Portão de aprovação

9/9 contrato do motor PASS (tamanhos dentro dos limites) · 0 HARD_FAIL · 0 REVIEW_REQUIRED · 0 achado aberto em editorial_checks · 0 ENTENDA_COPIES_OFFICIAL_TEXT · 0 ENTENDA_EXTERNAL_CASE_CONTENT · 0 EXTRAPOLATION_NUMBER · 0 NUMBER_NOT_IN_TEXT · 0 TERM_NOT_USED · 0 LIST_ITEM_POSSIBLY_DROPPED · 0 ABSOLUTE_CLAIM · 0 LAW_DEPENDENCY_OMITTED nos nove targets. Nenhuma nova afirmação jurisprudencial. Só os 9 targets mudaram em drafts e corpus.

Coerência com explicações já aprovadas: B10 e B11 são compatíveis com o art. 55 (v2) e o art. 55, § 2º; B11 deixa de usar a teleologia retirada do art. 55 na rodada B1; B15 é compatível com o art. 62 (v2) e o art. 62, § 6º (v2); B17 e B18 são compatíveis com o art. 66, § 4º e o art. 57 (v2).

## Totais

HUMAN_APPROVED_T1: 322 antes → **331** depois (+9). Batch06 pendentes: **51** (A 42, B 9, C 0, D 0, E 0).

## Código

- `build_entenda_batch06_candidate.py`: só a lista `INPUTS` (+4 arquivos versionados da rodada B2). Sem mudança de lógica.
- Testes: `tests/test_entenda_batch06.py` (contagens e rodada B2).

## Limitação conhecida (mantida até o fechamento do Batch06)

`BATCH06_SCALE_REPORT.md` continua com os rótulos fixos da rodada D no código do builder (ver `BATCH06_ROUND_C_RUN_LOG.md`); os números da seção estão corretos.

## Verificações

- Determinismo: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` → 3 builds byte-idênticos entre si e ao build no lugar.
- `tests/test_entenda_batch06.py`: 31/31 PASS.
- Suíte ENTENDA_ENGINE completa: 183/183 PASS.
- Materialização Git (`git_materialization_check.py`): conferida após o commit.
