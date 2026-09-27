# Regressão EXPANSION_1 → EXPANSION_R1

Data: 24/09/2026. Resultado R1 ausente no filesystem na retomada; executado uma vez e persistido, sem reconstruir provas. Entrada R1: `de9b63833bacedbc2cef7f94045099e32b2b48c19d474b028d66bef4f72c22cd`.

398 pares únicos; 394 com consenso binário (160 positivos, 234 negativos). Três conflitos históricos e um pendente não entram na matriz principal. Os grupos históricos se sobrepõem e conservam seus rótulos originais; NÃO somar grupos como se fossem independentes.

| Matriz deduplicada | EXPANSION_1 | R1 |
|---|---:|---:|
| TP | 45 | 50 |
| FP | 2 | 4 |
| TN — não publicado | 232 | 230 |
| FN | 115 | 110 |
| Não avaliável | 4 | 4 |

R1 recuperou cinco positivos e admitiu dois negativos adicionais. Não houve perda de TP nesta comparação. A equivalência DEFESA/DEFESA_EFETIVA não é suficiente para aprovar a expansão.

| Grupo | EXPANSION_1 | R1 |
|---|---|---|
| human134 | {"TN_NAO_PUBLICADO":114,"FN":11,"TP":9} | {"TN_NAO_PUBLICADO":114,"FN":11,"TP":9} |
| external36 | {"FN":6,"TN_NAO_PUBLICADO":23,"TP":7} | {"FN":6,"TN_NAO_PUBLICADO":23,"TP":7} |
| old176 | {"TP":27,"FN":96,"TN_NAO_PUBLICADO":49,"NAO_AVALIAVEL":2,"FP":2} | {"TP":31,"FN":92,"TN_NAO_PUBLICADO":47,"NAO_AVALIAVEL":2,"FP":4} |
| mechanisms15 | {"TP":6,"FN":9} | {"TP":10,"FN":5} |
| negatives10 | {"TN_NAO_PUBLICADO":10} | {"TN_NAO_PUBLICADO":10} |
| protected20 | {"FN":11,"TP":9} | {"FN":11,"TP":9} |
| recent60 | {"TN_NAO_PUBLICADO":35,"TP":12,"FN":13} | {"TN_NAO_PUBLICADO":35,"TP":15,"FN":10} |
| recent20 | {"TN_NAO_PUBLICADO":18,"TP":2} | {"TN_NAO_PUBLICADO":18,"TP":2} |

“recent20” contém 18 REJEITAR e 2 APROVAR no material humano consolidado, apesar do nome informal “20 rejeitados”; R1 bloqueia os 18 negativos e preserva os 2 positivos. Não reclassificar os dois para fabricar 20 TN.

| Estados no universo diagnóstico pré-final (238.809 pares) | EXPANSION_1 | R1 |
|---|---:|---:|
| ADMISSIVEL | 76 | 84 |
| REVISAO_EDITORIAL | 1 | 1 |
| EVIDENCIA_INSUFICIENTE | 231004 | 230996 |
| INCOMPATIVEL | 0 | 0 |
| FONTE_EM_REVISAO | 7728 | 7728 |

Contagens acima reutilizam os freezes de provas existentes; NÃO constituem a execução final da fase 9. Ausência de prova não equivale a incompatibilidade.

Gate atual: **não satisfeito** — 15/25 positivos recentes e 50/160 positivos deduplicados preservados. Os 35 negativos recentes permanecem não publicados. Decomposição causal dos 110 FN e eventual passe factual único são os próximos passos. Nenhuma autorização para R2 estrutural ou RC.

