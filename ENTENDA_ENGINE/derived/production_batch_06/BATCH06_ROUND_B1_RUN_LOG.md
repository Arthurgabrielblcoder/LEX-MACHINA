# Batch06 — rodada B1 (fila B, itens B1–B9): registro de execução

Data: 2026-10-09 · branch `batch06-scale-cloud` · checkpoint de partida `bb52c65afecc5a195e7f7d1e03db3f08afafb0ef`.

## Decisões aplicadas

Decisões humanas B1–B9 de 2026-10-09 e decisões complementares do mesmo dia, registradas em `ROUND_B1_HUMAN_REVIEW_DECISIONS.json` (escopo `CF88_BATCH06_TRIAGE_QUEUE_B_PART1`). Os 9 itens são os primeiros 9 dos 27 da fila B, em ordem estrutural da Constituição.

Decisões complementares:

- B7: "atribuir automaticamente" substituído por "estender" na ATENÇÃO (elimina pela redação o falso positivo `ABSOLUTE_CLAIM`, sem mudar o sentido jurídico);
- glossários: B1 e B2 sem "Decreto legislativo"; B4 com "Pedido escrito de informação" no lugar de "Requerimento de informação"; B5 com "Arguição" no lugar de "Sabatina"; B9 sem "Cassação".

| Item | Target | Decisão humana | Versão final |
|---|---|---|---|
| B1 | `CF88:ART.48` | ADJUST_THEN_APPROVE | v2 |
| B2 | `CF88:ART.49:INC.I` | ADJUST_THEN_APPROVE | v2 |
| B3 | `CF88:ART.50` | APPROVE | v1 (byte-idêntico) |
| B4 | `CF88:ART.50:PAR.2` | ADJUST_THEN_APPROVE | v2 |
| B5 | `CF88:ART.52` | ADJUST_THEN_APPROVE | v2 |
| B6 | `CF88:ART.52:INC.I` | ADJUST_THEN_APPROVE | v2 |
| B7 | `CF88:ART.53` | ADJUST_THEN_APPROVE | v2 |
| B8 | `CF88:ART.53:PAR.8` | ADJUST_THEN_APPROVE | v2 |
| B9 | `CF88:ART.55` | ADJUST_THEN_APPROVE | v2 |

As v1 dos 8 ajustados permanecem no corpus como RETIRED / CHANGES_REQUESTED (`superseded_by` → v2).

## Alertas

- Nenhuma resolução registrada em `T1_KNOWN_RESOLUTIONS.json` nem em `EDITORIAL_REVIEW_INPUT.json`: todos os alertas da primeira tentativa desapareceram pela própria redação.
- Eliminados pela redação: `ABSOLUTE_CLAIM` (B7); `TERM_NOT_USED` de "Decreto legislativo" (B1, B2), "Requerimento de informação" (B4), "Sabatina" (B5) e "Cassação" (B9).
- Avisos informativos remanescentes (lint, não bloqueiam): `NEAR_COPY_OF_OFFICIAL_TEXT` (trechos abaixo do limite de cópia do contrato), `EXAMPLE_REQUIREMENT_LANGUAGE` (B3 e B5, exemplos mantidos pela decisão humana) e `JURISPRUDENCE_WORDING_IN_BODY` em B7 (remissão à camada JURISPRUDÊNCIA, sem afirmação jurisprudencial; o mesmo aviso já existe em itens aprovados nas rodadas D e C).

## Portão de aprovação

9/9 contrato do motor PASS (tamanhos dentro dos limites) · 0 HARD_FAIL · 0 REVIEW_REQUIRED · 0 ENTENDA_COPIES_OFFICIAL_TEXT · 0 ENTENDA_EXTERNAL_CASE_CONTENT · 0 EXTRAPOLATION_NUMBER · 0 NUMBER_NOT_IN_TEXT · 0 achado editorial aberto · 0 TERM_NOT_USED nos nove targets. Nenhuma nova afirmação jurisprudencial; B2 e B6 continuam com jurisprudência CONTEXT_ONLY. Só os 9 targets mudaram em drafts e corpus; o mapa de risco não mudou.

Coerência com explicações já aprovadas: B7 remete às explicações específicas e deixa de afirmar que as garantias cessam com o fim do cargo (o que conflitaria com a v2 aprovada do art. 53, § 1º); B6 cita o art. 51, I literalmente, sem concluir sobre o alcance da autorização (compatível com a ATENÇÃO aprovada do art. 51, I); B5 e B9 são compatíveis com os aprovados do art. 52 (X, parágrafo único) e do art. 55 (VI, § 2º).

## Totais

HUMAN_APPROVED_T1: 313 antes → **322** depois (+9). Batch06 pendentes: **60** (A 42, B 18, C 0, D 0, E 0).

## Código

- `build_entenda_batch06_candidate.py`: só a lista `INPUTS` (+4 arquivos versionados da rodada B1), para que o determinismo copie as entradas que o build passa a ler (`BATCH_SPEC.round_approvals`) e o manifesto registre seus hashes. Sem mudança de lógica.
- Testes: `tests/test_entenda_batch06.py` (contagens e rodada B1).

## Limitação conhecida (mantida até o fechamento do Batch06)

`BATCH06_SCALE_REPORT.md` continua com os rótulos fixos da rodada D no código do builder (ver `BATCH06_ROUND_C_RUN_LOG.md`); os números da seção estão corretos. Correção adiada por decisão humana para o fechamento do Batch06.

## Verificações

- Determinismo: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` → 3 builds byte-idênticos entre si e ao build no lugar.
- `tests/test_entenda_batch06.py`: 30/30 PASS.
- Suíte ENTENDA_ENGINE completa: 182/182 PASS.
- Materialização Git (`git_materialization_check.py`): conferida após o commit.
