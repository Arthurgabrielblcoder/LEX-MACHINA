# MACRO07 — BACKLOG (não corrigido nesta missão)

Registro de problemas encontrados durante a missao em modulos compartilhados, runtime ou conteudo antigo. Itens marcados RESOLVIDO foram tratados no segundo passe (MACRO07_SECOND_PASS); os demais seguem sem correcao.

## Regra nova aplicada ao conteúdo antigo

`JUDICIAL_REVIEW_ANNOTATED` (anotação Vide ADI/ADIN/ADC/ADPF/ADO no escopo) aplicada a 382 registros ACTIVE dos corpora anteriores (HUMAN_APPROVED_T1 382). 12 registro(s) caem na regra; pela recalibração do segundo passe cada um precisa ser classificado `JUDICIAL_REVIEW_CONTEXT_ONLY` (MEDIUM) ou `JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS` (HIGH); sem classificação, a regra é REQUIRED (fail closed). Nenhum foi alterado nem reclassificado; a revisão fica para missão própria.

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
| MB07-01 | RUNTIME_TEXT_ANOMALY | `CF88:ART.114:INC.VII` | RESOLVIDO no segundo passe. Causa: a fonte do Senado (raw.html e normalizado.txt) traz "VII I - a execucao..."; a segmentacao anexava o texto ao VII e o status marcava VIII HISTORICAL. Correcao aprovada SRC-CORR-CF88-579494-16434817-ART114-INC-VIII aplicada pelo parser compartilhado (fail closed, verificada contra o cf.txt canonico) e errata de status (VIII CURRENT). Ver MACRO07_SOURCE_ANOMALY_ART114_REPORT.md. | Nenhuma nesta camada. Consolidar a errata no status congelado numa missao que regenere os exports do DEVICE (MB07-09). |
| MB07-02 | RUNTIME_TEXT_ANOMALY | `CF88:ART.155:INC.I:AL.c` | RESOLVIDO no segundo passe. A alinea c do inciso I e a redacao original de 1988, renumerada para o inciso III pela EC 3/1993; a comparacao do status falhava so pelo ponto final. Errata de status: HISTORICAL_ONLY (rotulo renumerado). Ver MACRO07_SOURCE_ANOMALY_ART155_REPORT.md. | Nenhuma nesta camada (ver MB07-09). |
| MB07-03 | ENGINE_TERM_COLLISION | `entenda_engine.EXTERNAL_CASE_RE` | O contrato bloqueia "sumula" no corpo, inclusive quando a palavra designa o proprio instituto constitucional (art. 103-A). O corpo usa "enunciado vinculante" e a ATENCAO avisa o leitor; o termo constitucional fica na camada externa. | Avaliar excecao no contrato para o termo constitucional (alteraria modulo compartilhado com hash do Batch06). |
| MB07-04 | RISK_DETECTOR_GAP | `t1_risk.assess` | Somente "regra de transicao" (singular) no corpo eleva para TRANSITION_OR_TEMPORAL; o plural nao. Contornado na redacao dos drafts em que a aplicacao no tempo e material (146 § 1º, 149-B, 149-C e reforma tributaria em 151-159-A). No segundo passe a decisao passou a ser da evidencia versionada (MACRO07_TRANSITION_EVIDENCE.json), nao da redacao do draft. | Aceitar singular e plural no detector (modulo compartilhado). |
| MB07-05 | VALIDATOR_GAP | `t1_validator_v3.EXCEPTION_IN_DRAFT` | "excetuado(s)" nao e reconhecido como marcador de excecao no draft (so "exceto"). Contornado na redacao (art. 155). | Incluir excetuad* no marcador (modulo compartilhado). |
| MB07-06 | VIGENCY_MATCH_COVERAGE | `entenda_vigency_plan.vigency_map` | A anotacao de vigencia so e casada quando o texto do dispositivo no runtime e identico (apos normalizacao) a linha anotada do cf.txt canonico; dispositivos sem casamento ficam sem anotacao (falso negativo possivel para JUDICIAL_REVIEW_ANNOTATED e para historico). | Casamento aproximado com revisao humana das divergencias. |
| MB07-07 | DUPLICATE_DRAFT_DROPPED | `CF88:ART.150` | A visao geral do art. 150 ja e HUMAN_APPROVED_T1 no corpus principal: reutilizada sem alteracao; o rascunho novo foi removido pelo critic (DROP_EXPLANATION, registrado no log). | Nenhuma. |
| MB07-08 | STATUS_FORMAT_DIVERGENCE | `CF88:ART.239:PAR.4` | Unica outra entrada do status com motivo "rotulo com formatacao divergente"; fora do escopo dos arts. 76-175. A errata recalculada nao a altera (continua CURRENT). | Conferir na missao do art. 239. |
| MB07-09 | FROZEN_STATUS_ERRATA | `LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS.json` | O status e entrada fixada do manifesto do Batch06 e dos exports run1/run2/run3 do DEVICE; nao foi reescrito. As correcoes (114, VIII; 155, I, c) estao em CF88_TARGET_STATUS_ERRATA.json, aplicada pelo builder macro. | Missao propria para consolidar a errata e regenerar os exports do DEVICE com aprovacao. |
| MB07-10 | EXTERNAL_SOURCE_NOT_VERSIONED | `EC 111/2021, EC 125/2022, EC 132/2023, EC 136/2025` | As regras de transicao proprias dessas emendas (fora do ADCT) nao estao versionadas: 82, 100 § 5º, 105 § 2º, 155 § 6º, 159-A e 165 § 18 seguem HIGH com PENDING_EXTERNAL_INGESTION. | Ingerir o texto oficial das emendas (Planalto/Senado) com sha256 e reavaliar. |
| MB07-11 | JUDICIAL_REVIEW_DECISION_NOT_VERSIONED | `ADI 3392, 3423, 3431, 3432, 3520, 4425, 7047, 7064, 7697` | As decisoes dos controles anotados (Vide ADI) nao estao versionadas; 11 explicacoes ficam JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS (D). | Ingestao oficial das decisoes (STF) e reavaliacao. |
