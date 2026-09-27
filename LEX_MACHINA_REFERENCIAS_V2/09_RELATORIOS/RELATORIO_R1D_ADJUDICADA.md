# Encerramento R1D adjudicada

Status: **R1D_REGRESSION_COMPLETE_GATE_FAILED**. Política: POLITICA_EDITORIAL_REFERENCIAS_V2_V1.

R1C e todos os artefatos preexistentes foram preservados. A simulação precedeu a implementação; o freeze precedeu a única regressão. Nenhum novo matcher, score ou threshold foi introduzido.

## Adjudicação e escopo

12 decisões humanas: 6 aprovações, 1 rejeição e 5 rotas condicionais ainda insuficientes. Três reversões binárias APROVAR → REJEITAR: uma explícita humana (12 Homens e uma Sentença → art.5 LV), duas por aplicação B/D/F (O Processo → art.55 §3; Privacidade Hackeada → art.5 XII). Nenhum arquivo histórico foi sobrescrito.

Simulação: 12 pares, seis dispositivos; 4 FP eliminados, 5 TP históricos sem âncora enviados à readjudicação, 3 negativos preservados. Nenhum TP da família permaneceu admitido, nenhum FN alterado e nenhuma ambiguidade factual de âncora.

14 adicionais: {'APROVAR': 3, 'EVIDENCIA_INSUFICIENTE': 6, 'PENDENTE_HUMANO': 3, 'REJEITAR': 2}. Oito lacunas: {'EVIDENCIA_INSUFICIENTE': 2, 'RESOLVIDA': 6}.

As novas fontes limitam-se aos casos técnicos. Vigiar e Punir recebeu somente a anotação TORTURA já explícita na ficha validada, para executar a decisão humana 10; ANALISAR não foi transformado em PRATICAR. Dois complementos literais nas lacunas de representação preservam os 233 núcleos existentes.

## Regressão única após freeze

Matriz adjudicada: {'FN': 62, 'FP': 0, 'NAO_AVALIAVEL': 23, 'TN': 237, 'TP': 76, 'binary_total': 375, 'precision': 1.0, 'recall': 0.5507246376811594}

Sensibilidade com todos os rótulos históricos: {'FN': 84, 'FP': 0, 'NAO_AVALIAVEL': 4, 'TN': 234, 'TP': 76, 'binary_total': 394, 'precision': 1.0, 'recall': 0.475}

A diferença de denominadores está explícita: 11 insuficientes, 8 pendências humanas novas, 3 conflitos e 1 pendente histórico são não binários. Não são convertidos em TN. A matriz histórica retém os FN e perdas de TP para evitar melhoria aparente por exclusão de casos difíceis.

| Grupo | Resultado adjudicado | Histórico aplicado a R1D |
|---|---|---|
| external36 | {'FN': 3, 'FP': 0, 'NAO_AVALIAVEL': 2, 'TN': 23, 'TP': 8, 'binary_total': 34, 'precision': 1.0, 'recall': 0.7272727272727273} | {'FN': 5, 'FP': 0, 'NAO_AVALIAVEL': 0, 'TN': 23, 'TP': 8, 'binary_total': 36, 'precision': 1.0, 'recall': 0.6153846153846154} |
| human134 | {'FN': 7, 'FP': 0, 'NAO_AVALIAVEL': 2, 'TN': 114, 'TP': 11, 'binary_total': 132, 'precision': 1.0, 'recall': 0.6111111111111112} | {'FN': 9, 'FP': 0, 'NAO_AVALIAVEL': 0, 'TN': 114, 'TP': 11, 'binary_total': 134, 'precision': 1.0, 'recall': 0.55} |
| mechanisms15 | {'FN': 0, 'FP': 0, 'NAO_AVALIAVEL': 2, 'TN': 1, 'TP': 12, 'binary_total': 13, 'precision': 1.0, 'recall': 1.0} | {'FN': 3, 'FP': 0, 'NAO_AVALIAVEL': 0, 'TN': 0, 'TP': 12, 'binary_total': 15, 'precision': 1.0, 'recall': 0.8} |
| negatives10 | {'FN': 0, 'FP': 0, 'NAO_AVALIAVEL': 0, 'TN': 10, 'TP': 0, 'binary_total': 10, 'precision': None, 'recall': None} | {'FN': 0, 'FP': 0, 'NAO_AVALIAVEL': 0, 'TN': 10, 'TP': 0, 'binary_total': 10, 'precision': None, 'recall': None} |
| old176 | {'FN': 54, 'FP': 0, 'NAO_AVALIAVEL': 15, 'TN': 53, 'TP': 54, 'binary_total': 161, 'precision': 1.0, 'recall': 0.5} | {'FN': 69, 'FP': 0, 'NAO_AVALIAVEL': 2, 'TN': 51, 'TP': 54, 'binary_total': 174, 'precision': 1.0, 'recall': 0.43902439024390244} |
| protected20 | {'FN': 7, 'FP': 0, 'NAO_AVALIAVEL': 2, 'TN': 0, 'TP': 11, 'binary_total': 18, 'precision': 1.0, 'recall': 0.6111111111111112} | {'FN': 9, 'FP': 0, 'NAO_AVALIAVEL': 0, 'TN': 0, 'TP': 11, 'binary_total': 20, 'precision': 1.0, 'recall': 0.55} |
| recent20 | {'FN': 0, 'FP': 0, 'NAO_AVALIAVEL': 0, 'TN': 18, 'TP': 2, 'binary_total': 20, 'precision': 1.0, 'recall': 1.0} | {'FN': 0, 'FP': 0, 'NAO_AVALIAVEL': 0, 'TN': 18, 'TP': 2, 'binary_total': 20, 'precision': 1.0, 'recall': 1.0} |
| recent60 | {'FN': 2, 'FP': 0, 'NAO_AVALIAVEL': 7, 'TN': 36, 'TP': 15, 'binary_total': 53, 'precision': 1.0, 'recall': 0.8823529411764706} | {'FN': 10, 'FP': 0, 'NAO_AVALIAVEL': 0, 'TN': 35, 'TP': 15, 'binary_total': 60, 'precision': 1.0, 'recall': 0.6} |

Gate: **BLOQUEAR_EXECUCAO_COMPLETA_R1D**. Checks: {'contractual_cases_disposed': True, 'four_fp_eliminated': True, 'frozen_input': True, 'integrity': True, 'known_fp_controlled': True, 'mechanisms10_negative_preserved': True, 'mechanisms15_preserved': True, 'no_new_structural_failure': False, 'old_tp_not_artificially_protected': True, 'recent20_negative_preserved': True, 'recent25_preserved': False, 'recent35_controlled': True, 'single_regression': True, 'technical_eight_closed': True, 'tests': True}

## Execução e candidato

Execução completa: NÃO. RC1: NÃO.

## Integridade

162 artefatos V2 preexistentes e 545 arquivos protegidos: integridade True. Testes novos: 11, aprovados: True.

Holdout: b71a87a8292ac621a209201e2082935813563f8002f9203430af3b781414adf1; somente hash de bytes, sem abrir JSON. Sem firmware, SD, IDX, commit ou tag.

## Próximo passo

Revisar as falhas enumeradas em R1D_GATE_DECISION.json; manter R1D congelada, sem nova regressão, execução completa ou RC nesta passagem.

Diagnóstico causal e próximo reparo exato: [DIAGNOSTICO_GATE_R1D.md](DIAGNOSTICO_GATE_R1D.md). A queda bruta de 17 para 15 recentes contém quatro retiradas autorizadas e duas recuperações; não justifica proteger TP antigos. O bloqueio suficiente é a rota de art. 205 sem âncora completa.
