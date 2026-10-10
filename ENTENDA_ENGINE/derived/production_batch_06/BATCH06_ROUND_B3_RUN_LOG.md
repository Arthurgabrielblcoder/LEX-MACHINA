# Batch06 — rodada B3 (fila B, itens B19–B27): registro de execução

Data: 2026-10-09 · branch `batch06-scale-cloud` · checkpoint de partida `88f6f787d46de3985a8c1ca1ec1f0aba024cef8a`.

## Decisões aplicadas

Decisões humanas B19–B27 de 2026-10-09 e complementações do mesmo dia, registradas em `ROUND_B3_HUMAN_REVIEW_DECISIONS.json` (escopo `CF88_BATCH06_TRIAGE_QUEUE_B_PART3`). Os 9 itens são os itens 19 a 27 dos 27 da fila B, em ordem estrutural da Constituição; com esta rodada a fila B fica encerrada. A rodada final foi reaplicada do zero a partir do checkpoint, sem aproveitar estado de testes anteriores.

Complementações autorizadas (eliminam alertas pela própria redação, sem resolução registrada):

- B20: O QUE DIZ reformulado — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (a redação anterior repetia 15 e 19 palavras seguidas da Lei Seca; maior sequência literal agora: 7);
- B24: frase da estrutura do O QUE SIGNIFICA reformulada — elimina `ENTENDA_COPIES_OFFICIAL_TEXT` (15 palavras; agora 9);
- B21: "Erário" acrescentado ao glossário — elimina `TECHNICAL_TERM_UNDEFINED`, mantendo o termo do próprio dispositivo no corpo;
- B26: 2º parágrafo do O QUE SIGNIFICA dividido, com "entidades da administração federal" e "aplicação de recursos públicos por entidades privadas" — elimina `LIST_ITEM_POSSIBLY_DROPPED` sem cópia literal nem `LONG_SENTENCE` (maior sequência literal: 9).

Glossários: B20 com "Registro" redefinido; B21 com "Erário"; B22 sem "Contrato administrativo"; B24 com "Jurisdição" redefinida; B25 sem "Vitaliciedade" (deixou de aparecer no corpo e na fonte); B26 com "Plano plurianual" sem duração temporal; B27 com "Responsabilidade solidária" redefinida.

| Item | Target | Decisão humana | Versão final |
|---|---|---|---|
| B19 | `CF88:ART.69` | ADJUST_THEN_APPROVE | v2 |
| B20 | `CF88:ART.71:INC.III` | ADJUST_THEN_APPROVE | v2 |
| B21 | `CF88:ART.71:INC.VIII` | ADJUST_THEN_APPROVE | v2 |
| B22 | `CF88:ART.71:PAR.1` | ADJUST_THEN_APPROVE | v2 |
| B23 | `CF88:ART.71:PAR.3` | ADJUST_THEN_APPROVE | v2 |
| B24 | `CF88:ART.73` | ADJUST_THEN_APPROVE | v2 |
| B25 | `CF88:ART.73:PAR.3` | ADJUST_THEN_APPROVE | v2 |
| B26 | `CF88:ART.74` | ADJUST_THEN_APPROVE | v2 |
| B27 | `CF88:ART.74:PAR.1` | ADJUST_THEN_APPROVE | v2 |

As v1 dos 9 permanecem no corpus como RETIRED / CHANGES_REQUESTED (`superseded_by` → v2).

## Alertas

- Nenhuma resolução nova em `T1_KNOWN_RESOLUTIONS.json` nem em `EDITORIAL_REVIEW_INPUT.json`.
- Eliminados pela redação: os quatro acima; `TERM_NOT_USED` de "Contrato administrativo" (B22) e "Vitaliciedade" (B25).
- Resolução antiga do B26 (`LAW_DEPENDENCY_OMITTED`, "na forma da lei" do § 2º): permanece válida nesta rodada, mas sua justificativa depende da existência da explicação própria de `CF88:ART.74:PAR.2`. Deverá ser reavaliada quando esse target for submetido à revisão humana na fila A; a revalidação **não** foi feita agora (registrada em `pending_revalidation` do arquivo de decisões).
- Avisos informativos remanescentes (lint, não bloqueiam): `NEAR_COPY_OF_OFFICIAL_TEXT` em B21, B24, B25, B26 e B27 (abaixo do limite de cópia do contrato) e `EXAMPLE_REQUIREMENT_LANGUAGE` nos exemplos didáticos de B19 e B25.
- Mapa de risco: B19, B22 e B23 deixam de ter `INTERPRETIVE_QUESTION_DEFERRED` (as novas ATENÇÕES remetem à camada externa); todos continuam MEDIUM e CONTEXT_ONLY.

## Portão de aprovação

9/9 contrato do motor PASS (tamanhos dentro dos limites) · 0 HARD_FAIL · 0 REVIEW_REQUIRED · 0 achado aberto em editorial_checks · 0 ENTENDA_COPIES_OFFICIAL_TEXT · 0 ENTENDA_EXTERNAL_CASE_CONTENT · 0 EXTRAPOLATION_NUMBER · 0 NUMBER_NOT_IN_TEXT · 0 TERM_NOT_USED · 0 TECHNICAL_TERM_UNDEFINED · 0 LIST_ITEM_POSSIBLY_DROPPED · 0 ABSOLUTE_CLAIM · 0 LAW_DEPENDENCY_OMITTED novo nos nove targets. Nenhuma nova afirmação jurisprudencial. Só os 9 targets mudaram em drafts e corpus.

Distinção de competências: B22 separa a sustação de ato (inciso X, Tribunal) da sustação de contrato (§ 1º, Congresso) e não antecipa o alcance de "decidirá a respeito"; B23 não afirma quem executa; B24 separa a jurisdição territorial (art. 73) das competências materiais (art. 71); B26 separa controle interno (art. 74 e art. 70) de controle externo (arts. 70 e 71). Compatível com o art. 71 (v1) e o art. 73, § 1º (v2) já aprovados.

## Totais

HUMAN_APPROVED_T1: 331 antes → **340** depois (+9). Batch06 pendentes: **42** (A 42, B 0, C 0, D 0, E 0). Fila B encerrada.

## Código

- `build_entenda_batch06_candidate.py`: só a lista `INPUTS` (+4 arquivos versionados da rodada B3). Sem mudança de lógica.
- Testes: `tests/test_entenda_batch06.py` (contagens e rodada B3).

## Limitação conhecida (mantida até o fechamento do Batch06)

`BATCH06_SCALE_REPORT.md` continua com os rótulos fixos da rodada D no código do builder (ver `BATCH06_ROUND_C_RUN_LOG.md`); os números da seção estão corretos.

## Verificações

- Determinismo: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` → 3 builds byte-idênticos entre si e ao build no lugar.
- `tests/test_entenda_batch06.py`: 32/32 PASS.
- Suíte ENTENDA_ENGINE completa: 184/184 PASS.
- Materialização Git (`git_materialization_check.py`): conferida após o commit.
