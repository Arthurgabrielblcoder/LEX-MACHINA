# Macro07 — rodada humana D1 (fila D, itens D1–D12): registro de execução

Data: 2026-10-10 · branch `cf-macro-76-175-cloud` · checkpoint de partida `1cf879f61433b6abb03238dbdb0e544a5d357d9b` (Macro07 com o Batch06 final; 249 pendentes; filas 143/82/0/24/0).

Primeira rodada humana do Macro07. Decisões registradas em `production_batch_07_macro/MACRO07_ROUND_D1_HUMAN_REVIEW_DECISIONS.json` (escopo `CF88_MACRO07_TRIAGE_QUEUE_D_PART1`). Cada decisão registra:
- o texto revisado (`original_content`) e as seções aplicadas (`set`), com antes e depois;
- a decisão e a versão;
- a justificativa e os flags resolvidos;
- as fontes oficiais.

D13–D24 e as filas A e B não foram decididos.

## Decisões

| Item | Target | Decisão humana | Versão final |
|---|---|---|---|
| D1 | `CF88:ART.82` | ADJUST_THEN_APPROVE | v2 |
| D2 | `CF88:ART.100` | ADJUST_THEN_APPROVE | v2 |
| D3 | `CF88:ART.100:PAR.5` | ADJUST_THEN_APPROVE | v2 |
| D4 | `CF88:ART.100:PAR.9` | ADJUST_THEN_APPROVE (reescrita integral) | v2 |
| D5 | `CF88:ART.100:PAR.12` | ADJUST_THEN_APPROVE | v2 |
| D6 | `CF88:ART.102:PAR.2` | ADJUST_THEN_APPROVE | v2 |
| D7 | `CF88:ART.105:PAR.2` | ADJUST_THEN_APPROVE | v2 |
| D8 | `CF88:ART.114` | ADJUST_THEN_APPROVE | v2 |
| D9 | `CF88:ART.114:INC.I` | ADJUST_THEN_APPROVE | v2 |
| D10 | `CF88:ART.114:PAR.1` | ADJUST_THEN_APPROVE | v2 |
| D11 | `CF88:ART.114:PAR.3` | APPROVE_WITH_PROVENANCE_ONLY | **v1 (conteúdo e notas byte-idênticos)** |
| D12 | `CF88:ART.142` | ADJUST_THEN_APPROVE | v2 |

As 11 v1 substituídas permanecem no corpus como `RETIRED / CHANGES_REQUESTED`, com `superseded_by` apontando para a v2. Elas foram carimbadas sobre o corpus congelado em `history/pre_round_d1/`.

## Reformulações autorizadas, aplicadas por redação e sem nenhuma resolução nova

- **Contrato do motor (`ENTENDA_EXTERNAL_CASE_CONTENT`):** o corpo do T1 não usa sigla de tribunal, número de ação nem "decidiu". Usa "Supremo Tribunal Federal", "assentou" e "afastou". Os identificadores ficam só nas notas externas, na provenance e no arquivo de decisões.
- **D1:** a frase sobre a EC 111 saiu do O QUE SIGNIFICA (já está na ATENÇÃO). No exemplo, ficou "no primeiro dia de 2023".
- **D3:** a ATENÇÃO diz que a ausência de juros de mora foi verificada para os requisitórios federais e que Estados, DF e Municípios têm disciplina própria.
- **D4:** o O QUE SIGNIFICA usa "na redação de 2009" e "uma nova redação do § 9º, de 2021", e as emendas aparecem na ATENÇÃO.
- **D5:** o O QUE SIGNIFICA usa "a regra constitucional atual", e a base normativa (EC 113, art. 3º, na redação da EC 136) aparece na ATENÇÃO.
- **D7:** a lei é citada como "Lei nº 15.484, de 2026".
- **D12:** "subsidiário" foi retirado de todo o T1, inclusive do glossário. A GLO ficou definida como emprego excepcional, após o esgotamento dos instrumentos ordinários.

## Provenance e fontes

Cada item aprovado leva `human_review.content_provenance` com `HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`, o link oficial e `PENDING_EXTERNAL_INGESTION`. São 18 fontes:
- **Planalto:** EC 111/2021, EC 113/2021, EC 114/2021, EC 125/2022, EC 136/2025, Lei 15.484/2026, Lei 9.868/1999, Lei 7.783/1989, Lei 4.320/1964 e LC 97/1999.
- **STF:** ADI 4425, 7064/7047, 3392, 3423, 3395, 3684 e 6457.
- **Tema 558 / RE 678360:** fonte indicada pela revisão humana.

Essas fontes deixam de ser `EXTERNAL_VERIFICATION_REQUIRED`. A ingestão na camada externa segue pendente.

**Exceção, D11:** as notas da v1, preservadas por decisão, ainda trazem o marcador textual antigo. A verificação está registrada na provenance.

Backlog:
- MB07-12: anomalia da anotação "Vide ADIN 3392" no art. 102, § 2º. A fonte congelada não foi alterada.
- MB07-13: fontes verificadas pendentes de ingestão.

## Infraestrutura (`build_entenda_macro_batch.py`)

Camada de rodada humana que reutiliza mecanismos existentes:
- `MACRO_SPEC.human_review_rounds` gera `round_approvals` e `stamping_evidence_corpus` no `BATCH_SPEC`; o `production_batch` aplica o versionamento e os `RETIRED`.
- `apply_human_rounds` é fail-closed: o draft precisa ser igual ao `original_content`, as seções precisam ser permitidas e a contagem precisa bater.
- Portão de aprovação portado do Batch06.
- `checks` e `slice_stats` reconhecem as aprovações da rodada registrada.
- O log do segundo passe é calculado sobre a triagem congelada antes da rodada; ficou byte-idêntico.
- Status e relatório de escala viraram genéricos.

Os drafts dos sub-blocos (saída do segundo passe) não foram alterados.

Ambiente de build: worktree LF com `PYTHONUTF8=1` e serialização de caminhos POSIX no builder, equivalente ao Cloud. A equivalência foi provada antes, reproduzindo byte a byte `c963acd` e `8ef7312`.

## Resultado

- **Portão de aprovação:** 12/12 PASS.
  - 0 HARD_FAIL, 0 REVIEW_REQUIRED aberto e 0 achado editorial aberto.
  - 0 `ENTENDA_EXTERNAL_CASE_CONTENT`, 0 `TRANSITION_IN_CORE`, 0 `ABSOLUTE_CLAIM`, 0 `QUALIFIER_NOT_IN_TEXT` e 0 `EXTRAPOLATION_NUMBER`.
  - Nenhuma resolução nova.
- **Contagem:** `HUMAN_APPROVED_T1` 382 → **394**. Macro07 pendentes 249 → **237**.
- **Filas:** A 143 · B 82 · C 0 · **D 12** · E 0.
- **Não revisados:** os 237 explicações estão byte-idênticas ao checkpoint, tanto o registro do corpus quanto a linha de triagem.
- **Verificações:**
  - testes do Macro07: 35 testes (28 + 7 da rodada), com só as 2 falhas ambientais do baseline no Windows (`\`); as duas passam em modo POSIX;
  - Batch06: 40/40;
  - suíte ENTENDA: 227 testes, com só as 3 falhas ambientais do baseline;
  - determinismo: 3 builds byte-idênticos;
  - materialização: conferida a partir do checkout principal antes do push.

Nenhuma propagação para `reconcile-macro07-macro08`. `batch06-scale-cloud`, Macro08 e `main` não foram tocados.
