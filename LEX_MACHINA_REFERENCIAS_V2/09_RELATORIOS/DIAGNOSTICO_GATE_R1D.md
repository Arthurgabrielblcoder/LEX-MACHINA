# Bloqueio do gate R1D adjudicada

A única regressão pós-freeze revelou uma aplicação incompleta da regra E no grafo de provas: **Cidadania no Brasil: O Longo Caminho → CF88:ART.205**. A decisão editorial `APROVAR_SEGUNDO_POLITICA` é sustentada pela afirmação validada `EXP-LIV-004#R1C01`, que historia educação e cidadania. Entretanto, a nova rota foi anexada a `CF88:ART.205#N3`, dependente de `CF88:ART.205#N1`. A âncora N1 continua dispondo apenas de `NEGAR_ACESSO → EDUCACAO`. A afirmação histórica não satisfaz essa âncora; o compilador corretamente não libera N3. O par permanece FN na matriz adjudicada.

Isso é falha da montagem do overlay contratual, não falta de fonte, mudança do rótulo, necessidade de pesquisa ou motivo para afrouxar o matcher. Os testes estruturais e sintéticos passaram, mas não detectaram essa falta de cobertura ponta a ponta; a regressão única a detectou. O input não foi alterado depois do freeze e nenhuma segunda avaliação foi executada.

O próximo reparo exato, em futura revisão versionada de R1D, é adicionar ao núcleo autônomo N1 uma rota de `CONTEXTUALIZACAO_HISTORICA` que aceite `HISTORIAR/ANALISAR` sobre `EDUCACAO` e `CIDADANIA` conjuntamente, com alcance restrito à relação entre educação e cidadania documentada na fonte. Preservar a dependência de N3, o predicado da obra, a fonte e os demais contratos. Esse reparo ainda **não foi implementado**. Requer novo freeze e autorização para uma nova regressão, pois a execução única desta passagem já foi consumida. Não criar R2.

## Diagnóstico do grupo de 25 positivos recentes

O controle bruto de preservação numérica 17/25 não foi alcançado: R1D admite 15/25. Há quatro retiradas deliberadas pela política D (três vínculos de O Processo e um de Olhos que Condenam) e duas recuperações (This War of Mine → dignidade; Chernobyl → acesso à informação). Nenhuma perda de TP fora da simulação foi encontrada. Portanto, o indicador bruto `recent25_preserved=false` **não deve ser interpretado isoladamente como falha estrutural nem motivar a restauração dos TP antigos**. O protocolo humano determina o mesmo critério para positivos e negativos. O bloqueio independente e suficiente é a aprovação do art. 205 ainda sem rota completa de prova.

Os 35 negativos recentes continuam sem publicação. Os 20 recentes permanecem 18 TN + 2 TP. Os mecanismos conservam 12 admissões entre os 15 positivos históricos e 10/10 negativos não publicados; no ledger adjudicado dos 15, há 12 TP, 1 TN e 2 insuficientes excluídos. Não apresentar esse denominador menor como recuperação dos 15.

## Encerramento

Gate: **BLOQUEAR_EXECUCAO_COMPLETA_R1D**. Execução 69 × 3.461: **NÃO**. RC1: **NÃO**. Não há contagens globais R1D; os runners integrais foram preparados, mas não executados. O holdout de 120 pares continua fechado.
