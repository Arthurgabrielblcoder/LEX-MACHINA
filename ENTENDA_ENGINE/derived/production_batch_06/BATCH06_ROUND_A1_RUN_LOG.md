# Batch06 — rodada A1 (fila A, itens A1–A15): registro de execução

Data: 2026-10-09 · branch `batch06-scale-cloud` · checkpoint de partida `9fb7be8fc31004df82aea9d1305621147d880c1e`.

## Decisões aplicadas

Decisões humanas A1–A15 de 2026-10-09 e complementações do mesmo dia, registradas em `ROUND_A1_HUMAN_REVIEW_DECISIONS.json` (escopo `CF88_BATCH06_TRIAGE_QUEUE_A_PART1`). Os 15 itens são os itens 1 a 15 dos 42 da fila A, em ordem estrutural da Constituição. A classificação `A_CLEAN_LOW` não foi tratada como aprovação: cada item passou por revisão jurídica humana. A rodada final foi reaplicada do zero a partir do checkpoint, sem aproveitar estado temporário dos ensaios.

Um ensaio prévio em cópia temporária (sem aprovação) apontou bloqueios novos nas redações humanas. As menores reformulações foram apresentadas e autorizadas antes da promoção (eliminam os alertas pela própria redação, sem resolução registrada):

- A3: "somente pode ocorrer" → "é admitida apenas" — elimina `UNIVERSAL_CLAIM`;
- A4: "demais itens", "sob responsabilidade", "em regiões" e "dos tributos federais devidos por pessoas físicas ou jurídicas" — eliminam `ENTENDA_COPIES_OFFICIAL_TEXT` (17 palavras seguidas; maior sequência literal agora: 8) e `LIST_ITEM_POSSIBLY_DROPPED`;
- A8: "Maioria simples" retirado do glossário (o corpo fala em "maioria dos votos") — elimina `TERM_NOT_USED`;
- A9: "intervenção federal e autorizar o estado de sítio" — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (16 palavras; agora 9); "fique excluído de todo o procedimento" — elimina `ABSOLUTE_CLAIM`; "com a ressalva de lei complementar prevista no inciso II" — elimina `LAW_DEPENDENCY_OMITTED`;
- A15: frase final do O QUE DIZ dividida — elimina `LONG_SENTENCE`.

Decisões editoriais complementares: "Decreto legislativo" retirado dos glossários de A9 e A10 (o detector não acusava `TERM_NOT_USED`, mas o termo deixou de ser usado e o T1 não afirma instrumento único).

| Item | Target | Decisão humana | Versão final |
|---|---|---|---|
| A1 | `CF88:ART.42` | ADJUST_THEN_APPROVE | v2 |
| A2 | `CF88:ART.42:PAR.1` | ADJUST_THEN_APPROVE | v2 |
| A3 | `CF88:ART.42:PAR.3` | ADJUST_THEN_APPROVE | v2 |
| A4 | `CF88:ART.43:PAR.2` | ADJUST_THEN_APPROVE | v2 |
| A5 | `CF88:ART.44` | APPROVE | v1 (byte-idêntica) |
| A6 | `CF88:ART.45` | ADJUST_THEN_APPROVE | v2 |
| A7 | `CF88:ART.46` | ADJUST_THEN_APPROVE | v2 |
| A8 | `CF88:ART.47` | ADJUST_THEN_APPROVE | v2 |
| A9 | `CF88:ART.49` | ADJUST_THEN_APPROVE | v2 |
| A10 | `CF88:ART.49:INC.V` | ADJUST_THEN_APPROVE | v2 |
| A11 | `CF88:ART.49:INC.IX` | ADJUST_THEN_APPROVE | v2 |
| A12 | `CF88:ART.51` | ADJUST_THEN_APPROVE | v2 |
| A13 | `CF88:ART.52:INC.III` | ADJUST_THEN_APPROVE | v2 |
| A14 | `CF88:ART.53:PAR.6` | APPROVE | v1 (byte-idêntica) |
| A15 | `CF88:ART.54` | ADJUST_THEN_APPROVE | v2 |

As v1 dos 13 ajustados permanecem no corpus como RETIRED / CHANGES_REQUESTED (`superseded_by` → v2).

## Resoluções antigas

- A3 (`CF88:ART.42:PAR.3`), `EXCEPTION_NOT_IN_TEXT`: continua disparada pela v2 ("prevê exceções") e continua válida — a justificativa antiga (as exceções são as hipóteses do art. 37, XVI, para o qual o § 3º remete) corresponde à nova redação. Mantida sem alteração; nenhuma resolução nova.
- A8 (`CF88:ART.47`), `TRANSITION_IN_CORE`: não é mais disparada pela v2, portanto não foi usada para aprová-la. Mantida no histórico (`EDITORIAL_REVIEW_INPUT.json`), sem apagar nem substituir.
- Nenhuma resolução nova em `T1_KNOWN_RESOLUTIONS.json` nem em `EDITORIAL_REVIEW_INPUT.json`.

## Alertas

- Eliminados pela redação: os listados acima; nas v2, também deixam de existir as imprecisões jurídicas apontadas na revisão (militar estadual como "servidor estadual", exemplo fora da alínea c do art. 37, XVI, "Atualmente não existem Territórios federais", suplência "em caso de licença" sem o limite do art. 56, § 1º, maioria simples como "maioria dos presentes", competência exclusiva/privativa "sem participação" do Presidente ou do Senado, instrumento único, procedimento regimental "em comissão", patrocínio "contra essas entidades" e perda automática do mandato).
- Avisos informativos remanescentes (não bloqueiam): `NEAR_COPY_OF_OFFICIAL_TEXT` (abaixo do limite de cópia do contrato) em A1, A3, A4, A6, A7, A9, A10, A12, A13 e A15; `ABSOLUTE_CLAIM` "sempre" no exemplo do A4 ("sempre que possível" do próprio § 4º, INFO no validador v3); `EXAMPLE_REQUIREMENT_LANGUAGE` no exemplo do A15; `NUMBER_FROM_OTHER_DEVICE` em A5, A7 e A8.
- Mapa de risco: os 15 saem da triagem. As 27 pendentes continuam LOW (A_CLEAN_LOW); complexidade STRUCTURED 25, SIMPLE 2, EXTERNAL 0 (o único EXTERNAL era o art. 45, aprovado nesta rodada).

## Portão de aprovação

15/15 contrato do motor PASS · 0 HARD_FAIL · 0 REVIEW_REQUIRED · 0 achado aberto em editorial_checks · 0 ENTENDA_COPIES_OFFICIAL_TEXT · 0 ENTENDA_EXTERNAL_CASE_CONTENT · 0 EXTRAPOLATION_NUMBER · 0 NUMBER_NOT_IN_TEXT · 0 TERM_NOT_USED · 0 TECHNICAL_TERM_UNDEFINED · 0 LIST_ITEM_POSSIBLY_DROPPED · 0 EXCEPTION_OR_RESSALVA_DROPPED · 0 LAW_DEPENDENCY_OMITTED · 0 MODALITY_SHIFT · 0 LONG_SENTENCE nos quinze targets. Nenhuma dependência externa nova; nenhuma nova afirmação jurisprudencial. Só os 15 targets mudaram em drafts e corpus.

Coerência com aprovados: A9 alinhado ao art. 48 (v2) quanto à ausência de instrumento único; A12 alinhado ao art. 52 (v2) e ao art. 51, I (v1); A13 mantém a distinção entre os incisos III e IV do art. 52 (v2); A7 alinhado ao art. 56 (v2); A11 compatível com o art. 71 (v1); A15 alinhado ao art. 54, I (v1), ao art. 55 (v2) e ao art. 55, § 2º (v1).

## Totais

HUMAN_APPROVED_T1: 340 antes → **355** depois (+15). Batch06 pendentes: **27** (A 27, B 0, C 0, D 0, E 0).

## Código

- `build_entenda_batch06_candidate.py`: só a lista `INPUTS` (+4 arquivos versionados da rodada A1). Sem mudança de lógica.
- Testes: `tests/test_entenda_batch06.py` (contagens, versões, rodada A1, resoluções antigas e regressões jurídicas; a regressão da ressalva do art. 49 passa a partir da v1 congelada).

## Limitação conhecida (mantida até o fechamento do Batch06)

`BATCH06_SCALE_REPORT.md` continua com os rótulos fixos da rodada D no código do builder (ver `BATCH06_ROUND_C_RUN_LOG.md`); os números da seção estão corretos.

## Verificações

- Determinismo: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` → 3 builds byte-idênticos entre si e ao build no lugar.
- `tests/test_entenda_batch06.py`: 33/33 PASS.
- Suíte ENTENDA_ENGINE completa: 185/185 PASS.
- Materialização Git (`git_materialization_check.py`): conferida após o commit.
