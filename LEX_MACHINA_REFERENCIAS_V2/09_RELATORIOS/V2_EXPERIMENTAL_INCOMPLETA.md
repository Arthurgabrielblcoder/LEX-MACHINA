# V2_EXPERIMENTAL_INCOMPLETA — encerramento controlado

Data: 24/09/2026. Recomendação: **PRECISA_DE_MAIS_TRABALHO**.

## Decisão e limite de escopo

O gate falhou após a única revisão estrutural EXPANSION_R1 e o único passe factual EXPANSAO_R1B. Foram preservados 55 de 160 positivos humanos conhecidos (34,375%), incluindo 15/25 recentes (60%). Reduzir FP não compensa perder 105 positivos conhecidos. Não foi executada a fase 9 final; não há RC1, índices de produção, integração ao firmware ou escrita no cartão SD.

A anotação de FN é relativa ao benchmark, não um juízo de que toda associação humana deva ser admitida. Casos como poluição → estudo prévio de impacto exigem fonte específica ou adjudicação. Não se inventou evidência para satisfazer os rótulos.

## Continuidade comprovada

Na retomada, as provas R1, entrada congelada e ledger de 398 pares existiam; o resultado completo R1 não existia. O checkpoint desatualizado da fase 5 foi corrigido antes de prosseguir. R1 foi executada uma vez e persistida, seguida da decomposição individual de 110 FN. Não se repetiu snapshot, auditoria ASTRA, piloto, construção dos 69 dossiês, anotação dos 210 dispositivos, consolidação do ledger ou primeira regressão da expansão.

R1B acrescentou dimensões factuais em 1984 e The Handmaid's Tale, uma afirmação sobre moradia em A Cor da Lei e um núcleo literal de ingresso no território em CF art. 5º, XV. Reutilizou somente fontes já verificadas. Nenhuma PROPOSTA foi promovida. Nenhum contrato preexistente, ontologia, núcleo do piloto ou intérprete foi alterado. Fontes, dispositivos e catálogo oficiais permanecem intactos. R1B recuperou cinco positivos, sem novo FP ou perda de TP em relação à R1.

A redução R1B foi congelada antes de calcular suas métricas: 398 provas reais, não uma execução final de 238.809 pares. Todas as intervenções estão no overlay de dados e seus hashes.

## Matrizes e estados

| Versão | TP | FP | TN/não publicado | FN | Fora da matriz |
|---|---:|---:|---:|---:|---:|
| alpha3, artefato histórico | 128 | 56 | 178 | 32 | 4 |
| EXPANSION_1 | 45 | 2 | 232 | 115 | 4 |
| EXPANSION_R1 | 50 | 4 | 230 | 110 | 4 |
| EXPANSION_R1B | 55 | 4 | 230 | 105 | 4 |

A mesma população binária é usada: 394 pares (160 positivos e 234 negativos). Os 3 conflitos e 1 pendente conservam proveniência e não entram nessa matriz. Redução de FP vs alpha3: 92,857%; recall de admissão conhecido: 34,375%. A alpha3 não foi reexecutada: comparação usa o artefato congelado.

| Estados — somente 398 pares conhecidos | EXPANSION_1 | R1 | R1B |
|---|---:|---:|---:|
| ADMISSIVEL | 47 | 54 | 59 |
| REVISAO_EDITORIAL | 0 | 0 | 0 |
| EVIDENCIA_INSUFICIENTE | 342 | 335 | 330 |
| INCOMPATIVEL | 0 | 0 | 0 |
| FONTE_EM_REVISAO | 9 | 9 | 9 |

Os 59 ADMISSIVEL incluem 4 FP conhecidos: NÃO são 59 vínculos aprovados para produto. O estado FONTE_EM_REVISAO é triagem conservadora da fotografia, não declaração de invalidade jurídica. Ausência de prova não foi classificada como incompatibilidade.

Os freezes diagnósticos já existentes R1 abrangiam 238.809 pares e registraram 84 ADMISSIVEL, 1 REVISAO_EDITORIAL, 230.996 EVIDENCIA_INSUFICIENTE e 7.728 FONTE_EM_REVISAO. Esses números são **da R1 anterior**, não do passe R1B nem de execução final aprovada. Não foram reconstruídos.

## Grupos solicitados

Contagens conservam os rótulos originais de cada grupo. Há sobreposição e divergências históricas: não somar linhas. O JSON comparativo também fornece partição mutuamente exclusiva dos 398 pares, usando consenso para os cálculos principais. Não restou par fora dos grupos inventariados.

| Grupo | EXPANSION_1 | R1 | R1B |
|---|---|---|---|
| human134 | {"TN_NAO_PUBLICADO":114,"FN":11,"TP":9} | {"TN_NAO_PUBLICADO":114,"FN":11,"TP":9} | {"TN_NAO_PUBLICADO":114,"FN":10,"TP":10} |
| external36 | {"FN":6,"TN_NAO_PUBLICADO":23,"TP":7} | {"FN":6,"TN_NAO_PUBLICADO":23,"TP":7} | {"FN":6,"TN_NAO_PUBLICADO":23,"TP":7} |
| old176 | {"TP":27,"FN":96,"TN_NAO_PUBLICADO":49,"NAO_AVALIAVEL":2,"FP":2} | {"TP":31,"FN":92,"TN_NAO_PUBLICADO":47,"NAO_AVALIAVEL":2,"FP":4} | {"TP":34,"FN":89,"TN_NAO_PUBLICADO":47,"NAO_AVALIAVEL":2,"FP":4} |
| mechanisms15 | {"TP":6,"FN":9} | {"TP":10,"FN":5} | {"TP":11,"FN":4} |
| negatives10 | {"TN_NAO_PUBLICADO":10} | {"TN_NAO_PUBLICADO":10} | {"TN_NAO_PUBLICADO":10} |
| protected20 | {"FN":11,"TP":9} | {"FN":11,"TP":9} | {"FN":10,"TP":10} |
| recent60 | {"TN_NAO_PUBLICADO":35,"TP":12,"FN":13} | {"TN_NAO_PUBLICADO":35,"TP":15,"FN":10} | {"TN_NAO_PUBLICADO":35,"TP":15,"FN":10} |
| recent20 | {"TN_NAO_PUBLICADO":18,"TP":2} | {"TN_NAO_PUBLICADO":18,"TP":2} | {"TN_NAO_PUBLICADO":18,"TP":2} |

Nos 35 negativos recentes originalmente apresentados, nenhum foi admitido; **2 desses pares têm conflito histórico**, ficando fora da matriz binária deduplicada. No grupo informal “20 rejeitados recentes”, o ledger efetivo contém **18 REJEITAR + 2 APROVAR**: ambos os positivos são preservados e os 18 negativos não publicados. Não se alteraram rótulos para fabricar 20 TN.

## Mecanismos reais e natureza pedagógica

Dossiê → conceito tipado → recuperação exaustiva → contrato de prova → decisão, usando a mesma entrada R1B e o mesmo intérprete. Não há features_simulacao ou rótulos nos argumentos do compilador.

- 15 positivos: 11 RECUPERADO_COM_EVIDENCIA, 4 EVIDENCIA_INSUFICIENTE, 0 INCOMPATIVEL, 0 NAO_RECUPERADO.
- 10 negativos pareados: 10 EVIDENCIA_INSUFICIENTE, nenhum admitido. Seis desses negativos têm dispositivo sem representação: o acerto por abstenção não comprova capacidade de reconhecer uma incompatibilidade específica.
- Borderlands só é admitido em provas apoiadas em afirmação VALIDADA de fonte acadêmica; isso foi testado.
- Cidadania no Brasil → salário mínimo é CONTEXTUALIZACAO_HISTORICA. A passagem validada não justifica sua associação à educação no art. 205; esse FN permanece explicitamente documentado.

## Causas individuais dos 105 FN remanescentes

| Primeiro bloqueio demonstrável | Pares FN |
|---|---:|
| REPRESENTACAO_DISPOSITIVO_INCOMPLETA | 52 |
| EVIDENCIA_OBRA_PROPOSTA_NAO_VALIDADA | 24 |
| FONTE_INSUFICIENTE | 17 |
| CONTRATO_DE_NATUREZA_INADEQUADO | 12 |

As classes são mutuamente exclusivas como causa primária; há coocorrência de falta de curadoria e fonte, preservada como causa secundária. O arquivo causal individual contém dispositivo, texto, contrato, afirmação disponível, motivo e ação. Nenhum FN ficou sem diagnóstico. Não se presumiu que “VALIDADA em algum aspecto da obra” prova todos os seus vínculos.

As 52 perdas de representação incluem 23 pares fora da prioridade sem núcleo, 26 pares com proposições técnicas propostas e 3 com representação curada parcial. Não são necessariamente 52 dispositivos distintos. O universo atual contém 211 dispositivos com representação (210 originais + um núcleo adicional), mas somente 75 com curadoria de núcleos, 128 com propostas técnicas e 8 com fonte não decomposta; as fontes suspeitas permanecem em quarentena. Os 69 dossiês possuem 76 evidências: 47 VALIDADA documentalmente e 29 PROPOSTA. Não há 69 dossiês integralmente curados.

## Bloqueio de contrato e quatro FP

A garantia de ampla defesa é provada por rota autônoma GARANTIA_TRANSVERSAL, sem que a representação do mecanismo funcional dependente seja necessária. Isso permite generalização indevida nas comparações humanas:

- O Processo → CF 103-B, §4º, III.
- Olhos que Condenam → CF 103-B, §4º, III.
- Olhos que Condenam → CF 247, parágrafo único.
- Olhos que Condenam → CF 41, §1º, III.

R1 introduziu os dois FP do art. 103-B; os demais já existiam. Completar fonte não resolve sozinho a fronteira entre analogia de uma garantia e extrapolação de regime. Restringir por título, trocar rótulo ou reescrever contratos específicos apenas para passar o benchmark seria indevido. Nenhuma R2 foi criada.

Os 12 FN de natureza de contrato mostram o problema complementar: consequência social ou argumento acadêmico não satisfaz uma rota escrita apenas como implementação de programa ou evento de violação. Nem todos são bugs do intérprete; há insuficiência do contrato editorial e decisões humanas a arbitrar. O passe factual não disfarça isso como simples troca de IDs.

## Holdout

120 pares reservados deterministicamente, fora de todos os 398 pares conhecidos, em 20 estratos: CF/ADCT × cinco mídias × presença/ausência de representação, seis pares por estrato. Nenhum rótulo novo foi criado e nenhuma previsão R1B desses pares foi avaliada nesta retomada. A seleção usa apenas identidades para exclusão, nunca o valor da decisão humana.

SHA256: `b71a87a8292ac621a209201e2082935813563f8002f9203430af3b781414adf1`.

A cegueira é quanto a rótulos humanos; não é um teste externo totalmente intocado: obras, fonte e provas diagnósticas R1 já existiam antes da reserva. O estrato sem representação mede também abstenção, não apenas precisão dos aprovados. A amostra ainda precisa de adjudicação independente e não autoriza publicar estimativa de precisão externa.

## Paridade, testes e determinismo

122/122 testes aprovados: 90 preexistentes preservados + 32 testes atuais R1B. Os testes atuais, regressão e runner integral preparado usam exatamente canonical_input_r1b.load_canonical. Os testes antigos continuam fixtures históricas, não adaptadores alternativos da versão atual. Paridade de provas reais conferida nos 25 mecanismos/negativos pareados.

Substring intra-palavra, conceito ancestral ≠ espécie, IDs não equivalentes, proibição de fonte proposta como prova, score posterior à prova, preservação de contratos e gate de parada passam. Hash canônico R1B: `3401d086d8a68e7b61ac9456732d133a6d61a00f2ff5c94ce03f589519cdcc91`.

Determinismo de entrada, reserva e prova local confirmado; hashes da prova local repetida: `378c5c77194959bbcedd86d963920afe491e7830593b09cc132ceb0bb354ebc0`. **Determinismo integral em duas execuções R1B não foi testado**, pois a execução final ficou bloqueada pelo gate. Não se apresenta o determinismo local como substituto desse teste.

## Integridade e entrega

545/545 arquivos protegidos permanecem byte a byte iguais ao snapshot inicial. Nenhuma diferença de git status fora da nova árvore V2. O arquivo firmware/LEX_MACHINA.ino/LEX_MACHINA.ino.ino já estava modificado antes desta missão e foi preservado exatamente nesse estado. Nenhum commit ou tag foi criado nesta retomada. Um arquivo vazio acidental desta execução, LEX-MACHINA-UNUSED, foi removido; não continha dados.

As baselines v1.3.2, v1.4-alpha/alpha2/alpha3, catálogo/DNA, CF_SEGMENTADA_V2, benchmarks, firmware, IDX e SD locais conferidos continuam intactos. Cartão físico não acessado.

Não há RC: 0 referências, 0 dispositivos, 0 obras em release. No diagnóstico conhecido apenas, os 59 estados ADMISSIVEL estão em 37 dispositivos e 24 obras; isso não constitui cobertura aprovada global.

## Continuidade exata

Parar em EXPANSION_R1B_REGRESSION_COMPLETE_GATE_FAILED. Não refazer pilotos, fontes, ledger ou regressões. Ler RESUME_INSTRUCTIONS.md, o diagnóstico dos 105 FN e os quatro FP. A próxima decisão é humana: adjudicar conflitos e alcance pedagógico/contratual, priorizar curadoria documental e autorizar uma nova missão versionada se houver mudança estrutural. O passe factual permitido está consumido; R2 não está autorizada. Não desbloquear a fase 9, gerar RC, IDX, firmware ou SD automaticamente.
