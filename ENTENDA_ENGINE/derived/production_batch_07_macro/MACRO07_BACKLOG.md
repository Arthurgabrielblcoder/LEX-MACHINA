# MACRO07 — BACKLOG (não corrigido nesta missão)

Registro de problemas encontrados durante a missao em modulos compartilhados, runtime ou conteudo antigo. Nada aqui foi corrigido nesta missao.

## Regra nova aplicada ao conteúdo antigo

`JUDICIAL_REVIEW_ANNOTATED` (anotação Vide ADI/ADIN/ADC/ADPF/ADO no escopo) aplicada a 382 registros ACTIVE dos corpora anteriores (HUMAN_APPROVED_T1 300, PENDING_HUMAN_REVIEW 82). 12 registro(s) seriam LEGAL_RISK HIGH pela regra nova. Nenhum foi alterado; a revisão fica para missão própria.

| Target | Status | Corpus | Anotações |
|---|---|---|---|
| `CF88:ART.5` | HUMAN_APPROVED_T1 | CF88.entenda.jsonl | Vide ADIN 3392 |
| `CF88:ART.5:INC.LXXVIII` | HUMAN_APPROVED_T1 | CF88_BATCH_01_FINAL.entenda.jsonl | Vide ADIN 3392 |
| `CF88:ART.5:PAR.3` | HUMAN_APPROVED_T1 | CF88_BATCH_01_FINAL.entenda.jsonl | Vide ADIN 3392 |
| `CF88:ART.23` | HUMAN_APPROVED_T1 | CF88_BATCH_03_FINAL.entenda.jsonl | Vide ADPF 672 |
| `CF88:ART.23:INC.II` | HUMAN_APPROVED_T1 | CF88_BATCH_03_FINAL.entenda.jsonl | Vide ADPF 672 |
| `CF88:ART.24` | HUMAN_APPROVED_T1 | CF88_BATCH_03_FINAL.entenda.jsonl | Vide ADPF 672 |
| `CF88:ART.24:INC.IX` | HUMAN_APPROVED_T1 | CF88_BATCH_03_FINAL.entenda.jsonl | Vide ADPF 672 |
| `CF88:ART.30` | HUMAN_APPROVED_T1 | CF88_BATCH_04.entenda.jsonl | Vide ADPF 672 |
| `CF88:ART.30:INC.II` | HUMAN_APPROVED_T1 | CF88_BATCH_04.entenda.jsonl | Vide ADPF 672 |
| `CF88:ART.39` | HUMAN_APPROVED_T1 | CF88_BATCH_05.entenda.jsonl | Vide ADI n. 2.135 |
| `CF88:ART.40` | HUMAN_APPROVED_T1 | CF88_BATCH_05.entenda.jsonl | Vide ADIN 3133, Vide ADIN 3143, Vide ADIN 3184 |
| `CF88:ART.40:PAR.18` | HUMAN_APPROVED_T1 | CF88_BATCH_05.entenda.jsonl | Vide ADIN 3133, Vide ADIN 3143, Vide ADIN 3184 |

## Itens registrados durante a missão

| ID | Tipo | Alvo | Detalhe | Ação sugerida |
|---|---|---|---|---|
| MB07-01 | RUNTIME_TEXT_ANOMALY | `CF88:ART.114:INC.VII` | O texto do runtime traz o inciso VIII anexado ao VII ("VII I - a execucao..."), e INC.VIII esta marcado HISTORICAL. Nao corrigido: runtime e fonte estrutural fora do escopo da missao. A visao geral do art. 114 sinaliza a anomalia na camada externa. | Conferir a segmentacao do art. 114 na fonte oficial e no runtime (missao propria). |
| MB07-02 | RUNTIME_TEXT_ANOMALY | `CF88:ART.155:INC.I:AL.c` | Alinea marcada CURRENT com texto vazio no runtime (alineas a e b HISTORICAL). Coberta pela visao geral do art. 155; nao corrigida. | Conferir a situacao da alinea c na fonte oficial e no runtime. |
| MB07-03 | ENGINE_TERM_COLLISION | `entenda_engine.EXTERNAL_CASE_RE` | O contrato bloqueia "sumula" no corpo, inclusive quando a palavra designa o proprio instituto constitucional (art. 103-A). O corpo usa "enunciado vinculante" e a ATENCAO avisa o leitor; o termo constitucional fica na camada externa. | Avaliar excecao no contrato para o termo constitucional (alteraria modulo compartilhado com hash do Batch06). |
| MB07-04 | RISK_DETECTOR_GAP | `t1_risk.assess` | Somente "regra de transicao" (singular) no corpo eleva para TRANSITION_OR_TEMPORAL; o plural nao. Contornado na redacao dos drafts em que a aplicacao no tempo e material (146 § 1º, 149-B, 149-C e reforma tributaria em 151-159-A). | Aceitar singular e plural no detector (modulo compartilhado). |
| MB07-05 | VALIDATOR_GAP | `t1_validator_v3.EXCEPTION_IN_DRAFT` | "excetuado(s)" nao e reconhecido como marcador de excecao no draft (so "exceto"). Contornado na redacao (art. 155). | Incluir excetuad* no marcador (modulo compartilhado). |
| MB07-06 | VIGENCY_MATCH_COVERAGE | `entenda_vigency_plan.vigency_map` | A anotacao de vigencia so e casada quando o texto do dispositivo no runtime e identico (apos normalizacao) a linha anotada do cf.txt canonico; dispositivos sem casamento ficam sem anotacao (falso negativo possivel para JUDICIAL_REVIEW_ANNOTATED e para historico). | Casamento aproximado com revisao humana das divergencias. |
| MB07-07 | DUPLICATE_DRAFT_DROPPED | `CF88:ART.150` | A visao geral do art. 150 ja e HUMAN_APPROVED_T1 no corpus principal: reutilizada sem alteracao; o rascunho novo foi removido pelo critic (DROP_EXPLANATION, registrado no log). | Nenhuma. |
