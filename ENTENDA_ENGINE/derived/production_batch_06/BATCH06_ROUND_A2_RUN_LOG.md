# Batch06 — rodada A2 (fila A, itens A16–A30): registro de execução

Data: 2026-10-09 · branch `batch06-scale-cloud` · checkpoint de partida `ad1c6999c814aa9d74982155f4cbea93291d4ac9`.

## Decisões aplicadas

Decisões humanas A16–A30 de 2026-10-09 e complementações do mesmo dia, registradas em `ROUND_A2_HUMAN_REVIEW_DECISIONS.json` (escopo `CF88_BATCH06_TRIAGE_QUEUE_A_PART2`). Os 15 itens são os itens 16 a 30 dos 42 da fila A, em ordem estrutural da Constituição. A classificação `A_CLEAN_LOW` não foi tratada como aprovação: cada item passou por revisão jurídica humana. A rodada final foi reaplicada do zero a partir do checkpoint, sem aproveitar estado temporário dos ensaios.

Um ensaio prévio em cópia temporária (sem aprovação) apontou bloqueios novos nas redações humanas. As menores reformulações foram apresentadas e autorizadas antes da promoção (eliminam os alertas pela própria redação, sem resolução registrada):

- A16: "favor decorrente de contrato" → "favor resultante de contrato" no O QUE SIGNIFICA — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (15 palavras seguidas; maior sequência literal agora: 10);
- A21: inciso VI completado com "planos nacionais, regionais e setoriais de desenvolvimento" — elimina `LIST_ITEM_POSSIBLY_DROPPED`;
- A22: "A emenda constitucional" → "A emenda à Constituição" (espécie do art. 59, I) — elimina `TRANSITION_IN_CORE`;
- A24: "anterioridade tributária" na ATENÇÃO — elimina `TERM_NOT_USED`, mantendo o termo no glossário;
- A28: "bem como do Supremo Tribunal Federal" no O QUE SIGNIFICA — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (17 palavras; agora 9). Foi mantida a forma testada "projetos de lei de iniciativa", fiel ao caput do art. 64.

Decisão editorial complementar: "Poder conclusivo" retirado do glossário do A21 (glossário final: Audiência pública).

| Item | Target | Decisão humana | Versão final |
|---|---|---|---|
| A16 | `CF88:ART.54:INC.II` | ADJUST_THEN_APPROVE | v2 |
| A17 | `CF88:ART.56:PAR.1` | APPROVE | v1 (byte-idêntica) |
| A18 | `CF88:ART.57:PAR.2` | APPROVE | v1 (byte-idêntica) |
| A19 | `CF88:ART.57:PAR.7` | ADJUST_THEN_APPROVE | v2 |
| A20 | `CF88:ART.58` | APPROVE | v1 (byte-idêntica) |
| A21 | `CF88:ART.58:PAR.2` | ADJUST_THEN_APPROVE | v2 |
| A22 | `CF88:ART.59` | ADJUST_THEN_APPROVE | v2 |
| A23 | `CF88:ART.61:PAR.2` | APPROVE | v1 (byte-idêntica) |
| A24 | `CF88:ART.62:PAR.2` | ADJUST_THEN_APPROVE | v2 |
| A25 | `CF88:ART.62:PAR.3` | ADJUST_THEN_APPROVE | v2 |
| A26 | `CF88:ART.62:PAR.10` | ADJUST_THEN_APPROVE | v2 |
| A27 | `CF88:ART.62:PAR.11` | ADJUST_THEN_APPROVE | v2 |
| A28 | `CF88:ART.64` | ADJUST_THEN_APPROVE | v2 |
| A29 | `CF88:ART.64:PAR.2` | ADJUST_THEN_APPROVE | v2 |
| A30 | `CF88:ART.66:PAR.7` | ADJUST_THEN_APPROVE | v2 |

As v1 dos 11 ajustados permanecem no corpus como RETIRED / CHANGES_REQUESTED (`superseded_by` → v2).

## Resoluções antigas

- A18 (`CF88:ART.57:PAR.2`), `EXAMPLE_NUMBER`: continua disparada por "17 de julho"; válida (o número vem do caput do art. 57).
- A19 (`CF88:ART.57:PAR.7`), `ABSOLUTE_CLAIM`: continua disparada por "automaticamente", agora também no exemplo; válida (reproduz o próprio § 8º; nenhuma afirmação absoluta externa).
- A20 (`CF88:ART.58`), `LAW_DEPENDENCY_OMITTED`: continua disparada; válida ("de lei" é parte de "projeto de lei").
- A21 (`CF88:ART.58:PAR.2`), `LAW_DEPENDENCY_OMITTED`: não é mais disparada pela v2 (o corpo menciona "projetos de lei"); não usada para aprovar a v2; mantida no histórico, sem apagar nem substituir.
- A29 (`CF88:ART.64:PAR.2`), `EXCEPTION_NOT_IN_TEXT`: continua disparada; válida (a exceção corresponde a "com exceção das que tenham prazo constitucional determinado").
- Nenhuma resolução nova em `T1_KNOWN_RESOLUTIONS.json` nem em `EDITORIAL_REVIEW_INPUT.json`.

## Alertas

- Eliminados pela redação: os listados acima; `TERM_LOW_UTILITY` de "Majoração" (A24, definição completada); `TERM_NOT_USED` de "Casa iniciadora" (A28, termo usado no corpo). Nas v2 também deixam de existir as imprecisões jurídicas apontadas na revisão ("contrato com o poder público" e "entidades públicas" no A16; causalidade "porque têm prazo" no A19; incisos incompletos no A21; instrumento atribuído a competências dos arts. 49 e 52 no A22; doutrina das exceções e "ano civil" no A24; "como se não tivesse existido" e "não depende de novo ato do Presidente" no A25; narrativa histórica e "ano legislativo" no A26; "fora do Congresso" e "Casa do autor" no A28; "não se sujeitam a essa urgência" no A29; prazo de quarenta e oito horas atribuído ao Vice-Presidente do Senado no A30).
- Avisos informativos remanescentes (não bloqueiam): `NEAR_COPY_OF_OFFICIAL_TEXT` abaixo do limite de cópia do contrato; `ABSOLUTE_CLAIM` / `AUTOMATIC_CONSEQUENCE` e `UNIVERSAL_CLAIM` informativo no A19 ("automaticamente" e "somente deliberará" do próprio texto); `EXAMPLE_REQUIREMENT_LANGUAGE` em A22 e A23; `NUMBER_FROM_OTHER_DEVICE` "120 dias" no A25.
- Mapa de risco: os 15 saem da triagem. As 12 pendentes continuam LOW (A_CLEAN_LOW); complexidade STRUCTURED 11, SIMPLE 1.

## Portão de aprovação

15/15 contrato do motor PASS · 0 HARD_FAIL · 0 REVIEW_REQUIRED · 0 achado aberto em editorial_checks · 0 ENTENDA_COPIES_OFFICIAL_TEXT · 0 ENTENDA_EXTERNAL_CASE_CONTENT · 0 EXTRAPOLATION_NUMBER · 0 NUMBER_NOT_IN_TEXT · 0 TERM_NOT_USED · 0 TECHNICAL_TERM_UNDEFINED · 0 TERM_LOW_UTILITY · 0 LIST_ITEM_POSSIBLY_DROPPED · 0 EXCEPTION_OR_RESSALVA_DROPPED · 0 LAW_DEPENDENCY_OMITTED novo · 0 MODALITY_SHIFT · 0 LONG_SENTENCE nos quinze targets. Nenhuma dependência externa nova; nenhuma nova afirmação jurisprudencial. Só os 15 targets mudaram em drafts e corpus.

Coerência com aprovados: A16 alinhado ao art. 54 (v2), art. 54, I (v1) e art. 55 (v2); A17 ao art. 46 (v2) e art. 56 (v2); A19 ao art. 57 (v2); A22 ao art. 49 (v2), art. 51 (v2) e art. 52 (v2) quanto à ausência de instrumento único; A25 e A27 ao art. 62 (v2); A28 ao art. 65 (v2); A30 ao art. 66 (v2), com a mesma definição de Promulgação.

## Totais

HUMAN_APPROVED_T1: 355 antes → **370** depois (+15). Batch06 pendentes: **12** (A 12, B 0, C 0, D 0, E 0).

## Código

- `build_entenda_batch06_candidate.py`: só a lista `INPUTS` (+4 arquivos versionados da rodada A2). Sem mudança de lógica.
- Testes: `tests/test_entenda_batch06.py` (contagens, versões, rodada A2, resoluções antigas e regressões jurídicas).

## Limitação conhecida (mantida até o fechamento do Batch06)

`BATCH06_SCALE_REPORT.md` continua com os rótulos fixos da rodada D no código do builder (ver `BATCH06_ROUND_C_RUN_LOG.md`); os números da seção estão corretos.

## Verificações

- Determinismo: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` → 3 builds byte-idênticos entre si e ao build no lugar.
- `tests/test_entenda_batch06.py`: 34/34 PASS.
- Suíte ENTENDA_ENGINE completa: 186/186 PASS.
- Materialização Git (`git_materialization_check.py`): conferida no índice antes do commit e no HEAD depois.
