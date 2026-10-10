# Batch06 — rodada C (fila C, 13 itens): registro de execução

Data: 2026-10-09 · branch `batch06-scale-cloud` · checkpoint de partida `da0dbfa452c2ce16310b58e868de8921441f0cef`.

## Decisões aplicadas

Decisões humanas C1–C13 de 2026-10-09 e três complementações do mesmo dia (todas registradas em `ROUND_C_HUMAN_REVIEW_DECISIONS.json`):

1. primeira complementação: nova redação de O QUE DIZ (C9) e de ATENÇÃO (C13); citação de emenda no formato "Emenda Constitucional nº X, de AAAA" (C3, C6, C10, C13); resolução histórica de C3;
2. segunda complementação: "regime jurídico" (servidores e militares) e "transferência para a reserva" em C9; o número histórico 65 em C13 resolvido como achado histórico coberto por fonte oficial.

Paráfrase mínima adicional em C9 (preferência da segunda complementação): "a organização **tanto** do Ministério Público **quanto** da Defensoria Pública da União" reduz a maior sequência literal coincidente com a Lei Seca de 10 para **9** palavras, sem novo alerta.

| Item | Target | Decisão humana | Versão final |
|---|---|---|---|
| C1 | `CF88:ART.43` | APPROVE | v1 |
| C2 | `CF88:ART.45:PAR.1` | ADJUST_PROVENANCE_THEN_APPROVE | v1 (T1 byte-idêntico; provenance OFFICIAL_CANONICAL_ANNOTATION) |
| C3 | `CF88:ART.53:PAR.3` | ADJUST_THEN_APPROVE | v2 |
| C4 | `CF88:ART.54:INC.I` | APPROVE | v1 |
| C5 | `CF88:ART.55:PAR.2` | APPROVE | v1 |
| C6 | `CF88:ART.57` | ADJUST_THEN_APPROVE | v2 |
| C7 | `CF88:ART.57:PAR.6` | APPROVE | v1 |
| C8 | `CF88:ART.61` | APPROVE | v1 |
| C9 | `CF88:ART.61:PAR.1` | ADJUST_THEN_APPROVE | v2 |
| C10 | `CF88:ART.62` | ADJUST_THEN_APPROVE | v2 |
| C11 | `CF88:ART.66:PAR.4` | APPROVE | v1 |
| C12 | `CF88:ART.71` | APPROVE | v1 |
| C13 | `CF88:ART.73:PAR.1` | ADJUST_THEN_APPROVE | v2 |

As v1 dos 5 ajustados permanecem no corpus como RETIRED / CHANGES_REQUESTED (`superseded_by` → v2).

## Resoluções de alertas

Mecanismo existente `editorial/T1_KNOWN_RESOLUTIONS.json` (por explanation_id aprovado, chave CODE:match); nenhum código de validador alterado.

| Explanation | Alerta | Resolução humana |
|---|---|---|
| `ENTENDA/CF88:ART.43/BASE/1` | LIST_ITEM_POSSIBLY_DROPPED | OVERVIEW_MAY_SUMMARIZE_CHILDREN |
| `ENTENDA/CF88:ART.53:PAR.3/BASE/2` | HISTORICAL_CLAIM_UNVERIFIED | HISTORICAL_CLAIM_SUPPORTED_BY_OFFICIAL_SOURCE |
| `ENTENDA/CF88:ART.54:INC.I/BASE/1` | EXCEPTION_OR_RESSALVA_DROPPED | EXCEPTION_SEMANTICALLY_PRESENT |
| `ENTENDA/CF88:ART.55:PAR.2/BASE/1` | HISTORICAL_CLAIM_UNVERIFIED | HISTORICAL_CLAIM_SUPPORTED_BY_OFFICIAL_SOURCE |
| `ENTENDA/CF88:ART.57/BASE/2` | LIST_ITEM_POSSIBLY_DROPPED | OVERVIEW_MAY_SUMMARIZE_CHILDREN |
| `ENTENDA/CF88:ART.57:PAR.6/BASE/1` | LIST_ITEM_POSSIBLY_DROPPED | SEMANTIC_ITEM_ALREADY_PRESENT |
| `ENTENDA/CF88:ART.61/BASE/1` | LIST_ITEM_POSSIBLY_DROPPED | OVERVIEW_MAY_SUMMARIZE_CHILDREN |
| `ENTENDA/CF88:ART.66:PAR.4/BASE/1` | HISTORICAL_CLAIM_UNVERIFIED | HISTORICAL_CLAIM_SUPPORTED_BY_OFFICIAL_SOURCE |
| `ENTENDA/CF88:ART.71/BASE/1` | LIST_ITEM_POSSIBLY_DROPPED | OVERVIEW_MAY_SUMMARIZE_CHILDREN |
| `ENTENDA/CF88:ART.73:PAR.1/BASE/2` | NUMBER_NOT_IN_TEXT (65) | HISTORICAL_CLAIM_SUPPORTED_BY_OFFICIAL_SOURCE |

Alertas eliminados pela própria redação ou pela provenance (sem resolução registrada): C9 LIST_ITEM_POSSIBLY_DROPPED (Distrito Federal; alíneas c e f); C2 EXTERNAL_FACT_NEEDS_PROVENANCE; HISTORICAL_CLAIM_UNVERIFIED de C6, C10 e C13 e o segundo de C3; EXTRAPOLATION_NUMBER (formato "nº X, de AAAA").

## Portão de aprovação

13/13 contrato do motor PASS (tamanhos dentro dos limites) · 0 HARD_FAIL · 0 REVIEW_REQUIRED sem resolução humana · 0 ENTENDA_COPIES_OFFICIAL_TEXT · 0 ENTENDA_EXTERNAL_CASE_CONTENT · 0 EXTRAPOLATION_NUMBER · 0 achado editorial aberto. Só os 13 targets da fila C mudaram em drafts, corpus e mapa de risco.

## Totais

HUMAN_APPROVED_T1: 300 antes → **313** depois (+13). Batch06 pendentes: **69** (A 42, B 27, C 0, D 0, E 0).

## Código

- `build_entenda_batch06_candidate.py`: só a lista `INPUTS` (+4 arquivos versionados da rodada C), para que o determinismo copie as entradas que o build passa a ler (`BATCH_SPEC.round_approvals`) e o manifesto registre seus hashes. Sem mudança de lógica.
- `apply_batch_review.py`: não alterado (a rodada C usa o mesmo formato de registro da rodada D).
- Testes: `tests/test_entenda_batch06.py` (rodada C) e `tests/test_t1_validator_v2.py` (o teste de escopo de versão das resoluções conhecidas passa a reconhecer os ids do corpus do Batch06).

## Limitação conhecida (não corrigida nesta rodada)

`BATCH06_SCALE_REPORT.md` é gerado com rótulos fixos da rodada D no código do builder: o título "Rodada D (revisão jurídica humana dos 11 itens D)", a menção só a `ROUND_D_HUMAN_REVIEW_DECISIONS.json` e a nota "(A, B e C não foram decididos)". Os números da seção (24 aprovados, 289 → 313, 69 pendentes) e a lista de escopos (D e C) estão corretos. A correção exige mudar texto do builder e ficou fora do escopo autorizado (somente `INPUTS`).

## Verificações

- Determinismo: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` → 3 builds byte-idênticos entre si e ao build no lugar (`DETERMINISM_EVIDENCE.json`).
- `tests/test_entenda_batch06.py`: 29/29 PASS.
- Suíte ENTENDA_ENGINE completa (181 testes): PASS após o commit (o guarda `test_production_batch_04.test_approved_content_immutable` compara `editorial/` com HEAD e só passa depois do commit de `T1_KNOWN_RESOLUTIONS.json`).
