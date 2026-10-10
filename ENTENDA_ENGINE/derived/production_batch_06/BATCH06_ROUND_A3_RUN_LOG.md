# Batch06 — rodada A3 (fila A, itens A31–A42; última rodada humana): registro de execução

Data: 2026-10-09 · branch `batch06-scale-cloud` · checkpoint de partida `ec1b1aa2b036cda910744013c7649c79ae88049e`.

## Decisões aplicadas

Decisões humanas A31–A42 de 2026-10-09 e complementações do mesmo dia, registradas em `ROUND_A3_HUMAN_REVIEW_DECISIONS.json` (escopo `CF88_BATCH06_TRIAGE_QUEUE_A_PART3`). Os 12 itens são os itens 31 a 42 dos 42 da fila A, em ordem estrutural da Constituição. A classificação `A_CLEAN_LOW` não foi tratada como aprovação: cada item passou por revisão jurídica humana. A rodada final foi reaplicada do zero a partir do checkpoint, sem aproveitar estado temporário dos ensaios.

Um ensaio prévio em cópia temporária (sem aprovação) apontou bloqueios novos nas redações humanas. As menores reformulações foram apresentadas e autorizadas antes da promoção (eliminam os alertas pela própria redação, sem resolução registrada):

- A33: "ou, conforme o caso, do Senado Federal" — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (12 palavras seguidas; agora 9);
- A36: "seja pública ou privada" — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (16; agora 10);
- A37: novo exemplo prático — elimina `DUPLICATION` com o `CF88:ART.49:INC.IX` v2 já aprovado (similaridade 0,407 → 0,25; limite 0,35), que fazia o portão de aprovação reprovar o A11; o A11 não foi alterado;
- A38: "as fundações e as sociedades" — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (11; agora 9);
- A39: "tome as providências" — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (17; agora 9 no O QUE SIGNIFICA);
- A40: "ou sob a forma de subsídios não aprovados" — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (12; agora 8 no O QUE SIGNIFICA).

Remoções de glossário autorizadas: "Irrepetibilidade" (A31, `TERM_NOT_USED` na nova redação) e "Título executivo" (A38, deixou de ser usado). Também por decisão humana: "Decreto legislativo" retirado do A33; "Imputação de débito" redefinida no A38.

| Item | Target | Decisão humana | Versão final |
|---|---|---|---|
| A31 | `CF88:ART.67` | ADJUST_THEN_APPROVE | v2 |
| A32 | `CF88:ART.68` | ADJUST_THEN_APPROVE | v2 |
| A33 | `CF88:ART.68:PAR.1` | ADJUST_THEN_APPROVE | v2 |
| A34 | `CF88:ART.68:PAR.2` | ADJUST_THEN_APPROVE | v2 |
| A35 | `CF88:ART.70` | APPROVE | v1 (byte-idêntica) |
| A36 | `CF88:ART.70:PAR.UNICO` | ADJUST_THEN_APPROVE | v2 |
| A37 | `CF88:ART.71:INC.I` | ADJUST_THEN_APPROVE | v2 |
| A38 | `CF88:ART.71:INC.II` | ADJUST_THEN_APPROVE | v2 |
| A39 | `CF88:ART.71:INC.IX` | ADJUST_THEN_APPROVE | v2 |
| A40 | `CF88:ART.72` | ADJUST_THEN_APPROVE | v2 |
| A41 | `CF88:ART.73:PAR.2` | ADJUST_THEN_APPROVE | v2 |
| A42 | `CF88:ART.74:PAR.2` | ADJUST_THEN_APPROVE | v2 |

As v1 dos 11 ajustados permanecem no corpus como RETIRED / CHANGES_REQUESTED (`superseded_by` → v2).

## Revalidação da resolução do B26

`B26_RESOLUTION_REVALIDATION: VALID` (decisão humana). A resolução de `LAW_DEPENDENCY_OMITTED` de `CF88:ART.74` ("na forma da lei" é do § 2º, que tem explicação própria mencionando a lei) continua disparada e aplicável: o A42 aprovado (`CF88:ART.74:PAR.2` v2, DEVICE) preserva "na forma da lei" no O QUE DIZ e explica no O QUE SIGNIFICA que os requisitos e a forma de apresentação da denúncia dependem da disciplina legal aplicável.

- Texto da resolução inalterado em `EDITORIAL_REVIEW_INPUT.json`; nenhuma resolução nova.
- Revalidação registrada em `ROUND_A3_HUMAN_REVIEW_DECISIONS.json` (`resolutions_reviewed` e `pending_revalidation_resolved`).
- `ROUND_B3_HUMAN_REVIEW_DECISIONS.json` mantido intacto como registro histórico (o campo `pending_revalidation` da B3 não é lido pelo builder; nenhuma alteração operacional foi necessária).

## Alertas

- Eliminados pela redação: os listados acima; `TERM_NOT_USED` de "Delegação legislativa" (A32, termo usado no corpo). Nas v2 também deixam de existir as imprecisões jurídicas apontadas na revisão ("ano legislativo" e assinatura no A31; "pouco usado na prática" e prazo temporal no A32; instrumento único e glossários antigos no A33; "tempo" no A34; "peso político" e "aprovação com ressalvas" no A37; classificação infraconstitucional no A38; prazo numérico inventado e fechamento do § 2º no A39; "disfarçados" no A40; afirmações externas sobre o Ministério Público junto ao Tribunal e ordem de vacância no A41; "morador" no A42).
- Avisos informativos remanescentes (não bloqueiam): `PARENT_REPETITION` do A41 (0,311 × `CF88:ART.73`, limite 0,35), aceito pela revisão humana e registrado em `accepted_info_warnings`; `NEAR_COPY_OF_OFFICIAL_TEXT` abaixo do limite de cópia do contrato; `EXAMPLE_REQUIREMENT_LANGUAGE` em A34 e A36.
- Mapa de risco: os 12 saem da triagem. Filas A 0, B 0, C 0, D 0, E 0; nenhuma linha de triagem pendente.

## Portão de aprovação

12/12 contrato do motor PASS · portão de aprovação 93/93 PASS (todos os aprovados do Batch06, inclusive o A11) · 0 HARD_FAIL · 0 REVIEW_REQUIRED · 0 achado aberto em editorial_checks · 0 ENTENDA_COPIES_OFFICIAL_TEXT · 0 ENTENDA_EXTERNAL_CASE_CONTENT · 0 EXTRAPOLATION_NUMBER · 0 NUMBER_NOT_IN_TEXT · 0 TERM_NOT_USED · 0 TECHNICAL_TERM_UNDEFINED · 0 TERM_LOW_UTILITY · 0 LIST_ITEM_POSSIBLY_DROPPED · 0 EXCEPTION_OR_RESSALVA_DROPPED · 0 LAW_DEPENDENCY_OMITTED novo · 0 MODALITY_SHIFT · 0 LONG_SENTENCE · 0 DUPLICATION no lote. Nenhuma dependência externa nova; nenhuma nova afirmação jurisprudencial. Só os 12 targets mudaram em drafts e corpus.

Coerência com aprovados: A31 alinhado ao art. 65 (v2) e ao art. 62, § 10 (v2); A32 e A33 ao art. 49 (v2), art. 59 (v2) e art. 52 (v2); A34 ao art. 49, V (v2); A37 ao art. 49, IX (v2), com a mesma definição de Parecer prévio; A38 ao art. 71, VIII (v2), com a mesma definição de Erário; A39 ao art. 71, § 1º (v2); A41 ao art. 73 (v2) e art. 73, § 1º (v2); A42 ao art. 74 (v2) e art. 74, § 1º (v2).

## Totais

HUMAN_APPROVED_T1: 370 antes → **382** depois (+12). Batch06 pendentes: **0** (A 0, B 0, C 0, D 0, E 0). O fechamento formal do Batch06 é etapa separada.

## Código

- `build_entenda_batch06_candidate.py`: só a lista `INPUTS` (+4 arquivos versionados da rodada A3). Sem mudança de lógica.
- Testes: `tests/test_entenda_batch06.py` (contagens finais, versões, rodada A3, revalidação do B26, regressões jurídicas; regressão do art. 68, § 1º, a partir da v1 congelada; com zero pendentes, a medição de volume e o formato do pacote compacto passam a ser conferidos no último estado com itens, pré-rodada A3).

## Limitações conhecidas (para o fechamento final do Batch06)

- `BATCH06_SCALE_REPORT.md` continua com os rótulos fixos da rodada D no código do builder (ver `BATCH06_ROUND_C_RUN_LOG.md`); não foi corrigido nesta rodada, por decisão humana.
- Com zero pendentes, as métricas de volume do relatório de escala ficam degeneradas (pacotes só com cabeçalhos; redução negativa em relação ao "modelo antigo") e o cabeçalho de `BATCH06_COMPACT_CLEAN_REVIEW.md` ainda diz "nenhum item aprovado" (rótulo fixo do builder). Ambos ficam para o fechamento final.

## Verificações

- Determinismo: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` → 3 builds byte-idênticos entre si e ao build no lugar.
- `tests/test_entenda_batch06.py`: 35/35 PASS.
- Suíte ENTENDA_ENGINE completa: 187/187 PASS.
- Materialização Git (`git_materialization_check.py`): conferida no índice antes do commit e no HEAD depois.
