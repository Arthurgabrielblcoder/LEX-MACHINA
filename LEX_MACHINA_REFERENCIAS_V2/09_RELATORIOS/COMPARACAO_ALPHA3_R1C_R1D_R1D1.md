# Comparação de versões

Mesmos 398 pares e ledger adjudicado congelado para a coluna principal. Engines antigas não reexecutadas.

| Versão | TP | FP | TN | FN | Precision | Recall | Escopo |
|---|---:|---:|---:|---:|---:|---:|---|
| Alpha3 | 107 | 59 | 178 | 31 | 64.4578% | 77.5362% | 375 binários / 398 conhecidos |
| R1C | 62 | 4 | 233 | 76 | 93.9394% | 44.9275% | 375 binários / 398 conhecidos |
| R1D | 76 | 0 | 237 | 62 | 100.0000% | 55.0725% | 375 binários / 398 conhecidos |
| R1D1 | 77 | 0 | 237 | 61 | 100.0000% | 55.7971% | 375 binários / 398 conhecidos |

R1C e R1D não possuem execução global; não inventar volume, fila, cobertura ou concentração globais. O JSON acompanha suas métricas de cobertura/concentração apenas no subconjunto conhecido e a matriz histórica separada.

Alpha3: 589 aprováveis, 551 selecionados. R1D1 global: 120 admissíveis, 2 em revisão probatória, 82 selecionados pela mesma regra de score histórico.

Concentração Alpha3 aprováveis: {'unit': 'vínculos únicos obra-dispositivo', 'total': 589, 'works_used': 45, 'devices_covered': 198, 'top1': 0.10526315789473684, 'top5': 0.41256366723259763, 'top10': 0.597623089983022, 'HHI': 0.05119032863389648, 'HHI_10000': 511.9032863389648, 'effective_works': 19.534940030407117, 'counts_by_work': {'REF-FIL-0004': 62, 'EXP-SER-007': 61, 'EXP-DOC-003': 54, 'EXP-FIL-006': 41, 'REF-FIL-0007': 25, 'REF-FIL-0002': 24, 'REF-DOC-0001': 22, 'REF-FIL-0005': 22, 'EXP-FIL-005': 21, 'REF-DOC-0003': 20, 'REF-LIV-0006': 20, 'REF-SER-0003': 20, 'REF-SER-0001': 16, 'REF-DOC-0004': 14, 'REF-LIV-0002': 14, 'REF-LIV-0004': 14, 'REF-DOC-0002': 11, 'REF-LIV-0005': 11, 'EXP-JOG-003': 10, 'EXP-LIV-008': 9, 'REF-FIL-0006': 9, 'REF-LIV-0001': 9, 'REF-LIV-0003': 8, 'EXP-LIV-005': 6, 'EXP-SER-003': 6, 'REF-SER-0002': 6, 'EXP-LIV-001': 5, 'EXP-SER-005': 5, 'REF-FIL-0008': 5, 'EXP-DOC-009': 4, 'REF-FIL-0001': 4, 'REF-FIL-0003': 4, 'REF-LIV-0007': 4, 'EXP-FIL-009': 3, 'EXP-DOC-001': 2, 'EXP-DOC-008': 2, 'EXP-DOC-010': 2, 'EXP-FIL-007': 2, 'EXP-LIV-002': 2, 'EXP-LIV-010': 2, 'EXP-SER-006': 2, 'REF-JOG-0001': 2, 'REF-JOG-0002': 2, 'EXP-FIL-008': 1, 'EXP-LIV-004': 1}}

Concentração R1D1 admissíveis: {'unit': 'vínculos únicos obra-dispositivo', 'total': 120, 'works_used': 36, 'devices_covered': 49, 'top1': 0.06666666666666667, 'top5': 0.2916666666666667, 'top10': 0.4666666666666667, 'HHI': 0.03652777777777778, 'HHI_10000': 365.27777777777777, 'effective_works': 27.376425855513308, 'counts_by_work': {'EXP-FIL-006': 8, 'REF-FIL-0004': 8, 'REF-LIV-0004': 7, 'REF-DOC-0004': 6, 'REF-FIL-0006': 6, 'REF-LIV-0001': 5, 'EXP-DOC-002': 4, 'EXP-DOC-003': 4, 'EXP-LIV-008': 4, 'EXP-LIV-009': 4, 'EXP-SER-006': 4, 'REF-DOC-0002': 4, 'REF-FIL-0007': 4, 'REF-LIV-0003': 4, 'REF-LIV-0007': 4, 'REF-SER-0001': 4, 'EXP-DOC-009': 3, 'EXP-LIV-010': 3, 'REF-FIL-0002': 3, 'REF-FIL-0003': 3, 'REF-SER-0002': 3, 'REF-SER-0003': 3, 'EXP-FIL-005': 2, 'EXP-FIL-009': 2, 'EXP-LIV-004': 2, 'REF-DOC-0001': 2, 'REF-FIL-0001': 2, 'REF-FIL-0005': 2, 'REF-LIV-0002': 2, 'REF-LIV-0006': 2, 'EXP-DOC-010': 1, 'EXP-LIV-006': 1, 'EXP-SER-007': 1, 'REF-JOG-0001': 1, 'REF-JOG-0002': 1, 'REF-LIV-0005': 1}}

Volume, evidência e auditabilidade são distintos: admissíveis V2 têm prova tipada; links novos sem score histórico são preservados com null, sem inventar score ou usar score para admitir. A validação conhecida não comprova precisão global.
