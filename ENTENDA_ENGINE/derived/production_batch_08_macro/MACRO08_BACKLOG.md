# MACRO08 — BACKLOG (não corrigido nesta missão)

Registro de problemas encontrados durante a missao em modulos compartilhados, runtime, fonte ou conteudo antigo. Nada aqui foi corrigido nesta missao.

## Regra nova aplicada ao conteúdo antigo

`JUDICIAL_REVIEW_ANNOTATED` (anotação Vide ADI/ADIN/ADC/ADPF/ADO no escopo) aplicada a 631 registros ACTIVE dos corpora anteriores (HUMAN_APPROVED_T1 300, PENDING_HUMAN_REVIEW 331). 26 registro(s) seriam LEGAL_RISK HIGH pela regra nova. Nenhum foi alterado; a revisão fica para missão própria.

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
| `CF88:ART.92` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADIN 3392 |
| `CF88:ART.98` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADIN 3392 |
| `CF88:ART.100` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADI 4425, Vide ADI 7047, Vide ADI 7064 |
| `CF88:ART.100:PAR.9` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADI 4425, Vide ADI 7047, Vide ADI 7064 |
| `CF88:ART.100:PAR.12` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADI 4425 |
| `CF88:ART.102` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADIN 3392 |
| `CF88:ART.102:PAR.2` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADIN 3392 |
| `CF88:ART.114` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADI n. 3392, Vide ADI n. 3423, Vide ADI n. 3431, Vide ADI n. 3432, Vide ADI n. 3520, Vide ADIN 3392, Vide ADIN 3432 |
| `CF88:ART.114:PAR.1` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADI n. 3392, Vide ADI n. 3423, Vide ADI n. 3431, Vide ADI n. 3432, Vide ADI n. 3520, Vide ADIN 3432 |
| `CF88:ART.114:PAR.3` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADI n. 3423, Vide ADI n. 3431, Vide ADI n. 3520, Vide ADIN 3392, Vide ADIN 3432 |
| `CF88:ART.166` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADI 7697 |
| `CF88:ART.166:PAR.9` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADI 7697 |
| `CF88:ART.166:PAR.11` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADI 7697 |
| `CF88:ART.166-A` | PENDING_HUMAN_REVIEW | CF88_MACRO_07.entenda.jsonl | Vide ADI 7697 |

## Itens registrados durante a missão

| ID | Tipo | Alvo | Detalhe | Ação sugerida |
|---|---|---|---|---|
| MB08-01 | PILOT_LEGACY_MODEL_CONFLICT | `ADCT:ART.10:INC.II` | ADCT:ART.10:INC.II tem explicacao HUMAN_APPROVED_T1 carimbada com o texto do cf.txt legado (status UNKNOWN); sob o perfil oficial o status e CURRENT e o snapshot diverge (MB08-SRC-05). O Macro08 nao gerou explicacao para o art. 10 (SKIP_APPROVED_PILOT_LEGACY_MODEL) para nao alterar conteudo aprovado. | Revisao humana do registro piloto contra o texto oficial do runtime; decidir substituicao em missao propria. |
| MB08-02 | OPERATIONAL_SOURCE_ANOMALY | `CF88:ART.239:PAR.4` | Fonte operacional do namespace CF88 cola o § 4º ao § 3º-A (MB08-SRC-01); o runtime ja separa. Nao corrigido; explicado na visao geral. | Estender o perfil CF88_OFFICIAL_RUNTIME ao namespace CF88 com reconciliacao dos 300 HUMAN_APPROVED_T1 (missao propria). |
| MB08-03 | OPERATIONAL_SOURCE_ANOMALY | `CF88:ART.250:CAPUT` | Caput do art. 250 absorve a formula de encerramento e as assinaturas na fonte operacional (MB08-SRC-02). | Mesma acao de MB08-02 (perfil runtime tambem para CF88). |
| MB08-04 | RUNTIME_TEXT_ANOMALY | `ADCT:ART.134:PAR.4` | § 4º truncado e fragmento de hiperlink no § 6º no texto oficial versionado (MB08-SRC-03). A visao geral do art. 134 avisa o leitor. | Conferir o art. 134 na fonte oficial (Senado) e regenerar o runtime se necessario. |
| MB08-05 | RUNTIME_TEXT_ANOMALY | `ADCT:ART.77:INC.I:AL.a` | Grafia "anº" no lugar de "ano" nas alineas a e b do inciso I do art. 77 do ADCT (MB08-SRC-06). | Revisar o normalizador do sinal ordinal na geracao do runtime. |
| MB08-06 | LEGACY_READER_ADCT | `ADCT` | O config global le o ADCT do cf.txt multi-versao (812 alvos UNKNOWN_VALIDITY, 139 divergencias com o parser estrito); o Macro08 usa o perfil CF88_OFFICIAL_RUNTIME (MB08-SRC-04). Os lotes anteriores e o config global nao foram alterados. | Promover o perfil runtime a config padrao do ADCT apos reconciliacao (missao propria). |
| MB08-07 | SHARED_VALIDATOR_LIMIT | `t1_validator_v2.cited_targets` | O validador compartilhado v2 so resolve citacoes do namespace CF88; remissoes ao ADCT viram EXTERNAL_*. O Macro08 refina no builder (namespace_cited / ADCT_REFERENCE_GROUNDED_IN_RUNTIME) sem tocar o modulo hash-pinned. | Tornar cited_targets ciente de namespace no validador compartilhado (com novo pin de hash). |
| MB08-08 | SHARED_VALIDATOR_FALSE_POSITIVE | `t1_validator_v2.LAW_STATUS_CLAIM` | A regex de LAW_STATUS_CLAIM dispara mesmo em frases que negam conhecer o estado da lei ("O texto nao informa se essa lei foi editada"). Os drafts foram reescritos para contornar. | Ajustar a regex para ignorar formulacoes negativas/condicionais. |
| MB08-09 | NUMERIC_PARITY_LIMIT | `CF88:ART.212` | O texto diz "dezoito, e os Estados, o Distrito Federal e os Municipios vinte e cinco por cento"; o detector de paridade numerica nao associa "dezoito" a "por cento" e marca 18% como NUMBER_NOT_IN_TEXT (fila C). | Ensinar ao extrator de quantidades a distribuicao de "por cento" em enumeracoes. |
| MB08-10 | OLD_CONTENT_JUDICIAL_REVIEW | `corpora anteriores` | 26 registros antigos (12 HUMAN_APPROVED_T1, 14 PENDING) seriam HIGH pela regra JUDICIAL_REVIEW_ANNOTATED (tabela acima). Nenhum alterado. | Classificar CONTEXT_ONLY x REQUIRED em missao propria. |
| MB08-11 | PARALLEL_BRANCH_RECONCILIATION | `cf-macro-176-250-adct-cloud` | Branch criado do checkpoint fixo 03e6f259 em paralelo a cf-macro-76-175-cloud (STACKED_PARALLEL_BRANCH). Contagem global de aprovacoes e corpora precisam de reconciliacao antes de qualquer merge (GLOBAL_APPROVAL_COUNT_REQUIRES_PARALLEL_RECONCILIATION). | Reconciliar com cf-macro-76-175-cloud antes do merge (RECONCILIATION_REQUIRED_BEFORE_MERGE). |
| MB08-12 | EXTERNAL_INGESTION_PENDING | `ADCT (varios)` | Estado de leis complementares, emendas nao versionadas (ex.: EC 67/2010 no art. 79) e acoes de controle (ADI 7064, MI 7300) mantem 18 itens ADCT em D (TEMPORAL_STATUS_UNRESOLVED / JUDICIAL_REVIEW_REQUIRED). | Ingerir legislacao correlata e jurisprudencia (PENDING_EXTERNAL_INGESTION) e reavaliar os D. |
