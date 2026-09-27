# Encerramento da curadoria EXPANSAO_R1C

Data: 25/09/2026. Handoff: `9375eed2-6b52-479f-b8b9-e3f73cdd0758`.

Resultado: **AINDA_PRECISA_CURADORIA**. Checkpoint final: `R1C_REGRESSION_COMPLETE_GATE_FAILED`. Pesquisa encerrada; execução completa não realizada. Esta é uma passagem factual sobre a arquitetura R1/R1B, não R2 nem uma nova versão do matcher.

## Escopo e sequência efetivamente cumpridos

O inventário preexistente dos 105 FN foi reutilizado, sem reconstrução. A sequência foi: triagem; auditorias dos seis grupos; montagem do overlay; freeze das representações/evidências; produção das provas; uma regressão R1C; decomposição dos FN restantes e decisão do gate. Os checkpoints individuais estão em `00_CHECKPOINTS/R1C_*_COMPLETE.json`.

Não foram reexecutados R1, R1B, piloto, expansão dos 210 dispositivos, construção dos 69 dossiês ou consolidação dos rótulos. R1 e R1B foram comparados pelos resultados persistidos. Nenhum conteúdo do holdout foi carregado: somente seus bytes foram usados para SHA-256.

## Triagem e curadoria

| Recuperabilidade dos 105 | Quantidade |
|---|---:|
| RECUPERAVEL_DADOS_LOCAIS | 0 |
| RECUPERAVEL_PESQUISA_FONTE | 22 |
| PROVAVELMENTE_NAO_RECUPERAVEL_NO_CONTRATO_ATUAL | 68 |
| CONTRATO_REQUER_ADJUDICACAO | 15 |
| FONTE_JURIDICA_EM_REVISAO | 0 |

Os 15 casos contratuais da triagem incluem os 12 originais e três casos adicionais. Triagem é hipótese de recuperabilidade, não decisão de admissibilidade. Pesquisa externa nova ficou restrita aos casos triados para pesquisa; documentos já coletados foram reaproveitados. A proveniência, os localizadores e as paráfrases curtas constam de [FONTES_DOCUMENTAIS_R1C.json](../03_OBRAS/FONTES_DOCUMENTAIS_R1C.json).

**52 representações, 36 dispositivos:** todos auditados individualmente. Foram registrados 36 complementos literais; 19 dispositivos já tinham núcleos e receberam complementos de qualificadores, exceções ou finalidades. Os outros 17 não receberam núcleos novos. Isso é complementação parcial, **não 36 representações integralmente corrigidas**: zero reparos completos de prova e zero recuperações atribuídas isoladamente a esse grupo. Sujeitos/objetos/predicados tipados, papéis, dependências, templates, estados dos núcleos e contratos não foram alterados. A ausência do instituto específico não foi compensada por assunto genérico.

**24 propostas:** 18 VALIDADA, 6 INSUFICIENTE, zero CONTRADITA e zero PROPOSTA remanescente. Esses números são de pares: envolvem nove evidências únicas, das quais seis validadas e três insuficientes. Validação documental não significa aprovação automática do vínculo constitucional. Foram corrigidos os papéis dos jovens afetados em *3%* e da família afetada em *Pachinko*, sem inventar atores institucionais.

**17 lacunas de fonte:** oito resolvidas documentalmente e nove não resolvidas. Doze tiveram pesquisa dirigida; cinco foram encerradas por triagem/documentos locais. Uma fonte pode documentar a obra e ainda não satisfazer o predicado exigido pelo contrato; logo, oito fontes resolvidas não equivalem a oito TP.

**12 contratos e quatro FP:** preparados em [CONTRATOS_12_PARA_ADJUDICACAO.md](../06_BENCHMARKS/CONTRATOS_12_PARA_ADJUDICACAO.md), JSON equivalente e [DIAGNOSTICO_FP_4_PARA_ADJUDICACAO.md](../06_BENCHMARKS/DIAGNOSTICO_FP_4_PARA_ADJUDICACAO.md). Nenhum contrato foi corrigido automaticamente. As explicações causais e as hipóteses sobre a natureza pedagógica implícita são interpretações da auditoria, não novas justificativas atribuídas ao revisor humano.

**Quatro mecanismos positivos:** dois receberam suporte documental adicional, mas somente um foi recuperado na regressão: *Olhos que Condenam* → art. 5º, LVII. *O Processo* → art. 5º, LVII, *Privacidade Hackeada* → art. 5º, XII e *Democracia em Vertigem* → art. 2º continuam insuficientes. Documentar impeachment não equivale a provar o predicado de defesa da separação dos Poderes; documentar execução sem julgamento não equivale a localizar uma condenação judicial.

## Dados congelados e limites preservados

O overlay contém nove revisões de evidências propostas, dez novas afirmações documentadas e 36 complementos jurídicos literais. As 86 evidências finais distribuem-se em 63 VALIDADA, 20 PROPOSTA e três INSUFICIENTE. As 20 propostas restantes são externas ao grupo das nove evidências únicas auditadas nesta passagem; não foram promovidas silenciosamente.

Permanecem 69 obras, 3.461 dispositivos (2.656 CF e 805 ADCT) e 233 núcleos, sem novos núcleos ou contratos. Não foi acrescentada equivalência semântica; a equivalência preexistente de defesa permanece como estava. As novas rotinas apenas montam/carregam dados versionados e produzem diagnósticos: reutilizam os compiladores congelados. Não houve alteração de score, threshold, naturezas, lógica de admissibilidade, rótulos, catálogo/DNA oficiais, firmware, SD ou IDX.

O manifesto [R1C_REPRESENTATIONS_FROZEN.json](../00_CHECKPOINTS/R1C_REPRESENTATIONS_FROZEN.json) antecedeu as provas. [EXPANSION_R1C_FREEZE.json](../00_CHECKPOINTS/EXPANSION_R1C_FREEZE.json) registra as provas congeladas antes da regressão. Nenhum dado foi ajustado após observar métricas.

| Identidade | SHA-256 / digest |
|---|---|
| Input canônico R1C (digest lógico, não hash do arquivo descritor) | `ccf92bce6ffd07c93bb069c3b0783adc192c2e850feb0af94c1189c01c92849c` |
| Overlay factual | `f3aa148462fa0291db6b323b5e28d138294111aeefc79183749cee9e5d9a8e9c` |
| Conteúdo canônico das provas | `134e6c2c86a0d344f20f940c932490788a1520deb24a0c189d87e24ad1245054` |
| Arquivo de resultados R1C | `c91530afd050be9daf165f03822df8c94f19cbb8422769d85208a0bb0a2b6248` |

## Regressão única: comparação

Base: 398 pares conhecidos, com 394 rótulos binários válidos, três conflitos e um pendente excluídos da matriz. Não é teste cego nem medição de generalização fora da amostra de desenvolvimento.

| Métrica | R1 | R1B | R1C |
|---|---:|---:|---:|
| TP | 50 | 55 | 67 |
| FP | 4 | 4 | 4 |
| TN | 230 | 230 | 230 |
| FN | 110 | 105 | 93 |
| Precision | 92,5926% | 93,2203% | 94,3662% |
| Recall | 31,2500% | 34,3750% | 41,8750% |
| Specificity | 98,2906% | 98,2906% | 98,2906% |
| Accuracy | 71,0660% | 72,3350% | 75,3807% |

Estados nos 398 pares R1C: 71 ADMISSIVEL, 317 EVIDENCIA_INSUFICIENTE, nove FONTE_EM_REVISAO, um REVISAO_EDITORIAL e zero INCOMPATIVEL. Esses estados incluem os quatro pares não binários, diferentemente da matriz. O estado editorial não conta como admissão/TP.

Houve 12 novos TP, nenhum TP perdido e nenhum FP novo. Recuperações: *Chernobyl* → 170, VI e 225; *Ensaio sobre a Cegueira* → 1º, III; *The Post* → 220, § 2º; *Pachinko* → 3º, IV; *1984* → 5º, IV e IX; *O Sol é para Todos* → 5º, LVII; *Olhos que Condenam* → 5º, LVII e XLIX; *A Vida dos Outros* → 5º, LXXIX; *A 13ª Emenda* → 5º, XLIX.

| Grupo de controle | R1B | R1C |
|---|---:|---:|
| 25 positivos recentes admitidos | 15/25 | 17/25 |
| 35 negativos recentes não admitidos | 35/35 | 35/35 |
| 20 recentes | 18 TN + 2 TP | 18 TN + 2 TP |
| 15 mecanismos positivos | 11/15 | 12/15 |
| Dez negativos pareados não admitidos | 10/10 | 10/10 |

Os grupos se sobrepõem; seus totais não devem ser somados para reconstruir a matriz. *Ensaio sobre a Cegueira* → art. 5º, III passou a REVISAO_EDITORIAL, respeitando o contrato existente, e permanece FN. As transições individuais estão em [AUDITORIA_RECENTES_10_E_MECANISMOS_4_R1C.json](../06_BENCHMARKS/AUDITORIA_RECENTES_10_E_MECANISMOS_4_R1C.json).

## FN restantes, FP e gate

Dos 93 FN: 59 AUSENCIA_REAL_DE_EVIDENCIA, 26 CONTRATO_REQUER_ADJUDICACAO, quatro REPRESENTACAO_AINDA_INCOMPLETA, quatro FONTE_INSUFICIENTE. Zero CANDIDATO_NAO_RECUPERADO, FONTE_JURIDICA_EM_REVISAO ou OUTRO. A categoria de ausência significa **ausência da prova exigida nas fontes auditadas**, não demonstração de que a obra jamais contenha o fato. Os 26 achados contratuais incluem os 12 originais e 14 adicionais identificados após validação documental; nada foi alterado para fazê-los passar.

As quatro lacunas de representação são: *Desigualdade para Todos* → art. 170; *A Revolução dos Bichos* → art. 3º, IV; *Filadélfia* e *A Revolução dos Bichos* → art. 5º, caput. As anotações literais não completam por si sós as rotas de prova existentes.

As quatro lacunas de fonte são: *V de Vingança* → art. 5º, IV e IX; *1984* → art. 5º, LXXIX; *The Handmaid's Tale* → art. 5º, VI. Faltam respectivamente evento específico de repressão, exploração de dado pessoal e causa vinculada à crença/culto; não foram substituídos por relações temáticas.

Os quatro FP preservados são *O Processo* e *Olhos que Condenam* → art. 103-B, § 4º, III; e *Olhos que Condenam* → art. 247, parágrafo único e art. 41, § 1º, III. A hipótese causal é transposição de obstrução da defesa penal a regimes funcionais por GARANTIA_TRANSVERSAL sem ancoragem no mecanismo específico. Correção depende de adjudicação, não de uma blacklist.

Gate: **AINDA_PRECISA_CURADORIA**, documentado em [R1C_GATE_DECISION.json](../00_CHECKPOINTS/R1C_GATE_DECISION.json). Não é exigência de eliminar todos os FN nem alteração de threshold: os quatro casos de representação e quatro de fonte impedem considerar a curadoria concluída para liberação global. Há também questões contratuais que não se limitam aos 12 originais. A pesquisa desta passagem está encerrada, conforme a regra de parada.

## Integridade, testes e continuidade

Verificação final: 545/545 arquivos protegidos intactos e 113/113 artefatos do manifesto V2 anterior intactos. As únicas exclusões autorizadas desse manifesto histórico são os dois arquivos de continuidade atualizados: `RESUME_STATE.json` e `RESUME_INSTRUCTIONS.md`. O snapshot original não foi substituído. Holdout de 120 pares preservado, hash `b71a87a8292ac621a209201e2082935813563f8002f9203430af3b781414adf1`, sem abertura do conteúdo.

32/32 testes R1C aprovados, sem nova avaliação do benchmark. Os 122 testes históricos permanecem registrados e seus artefatos protegidos; não foram reexecutados porque a suíte histórica inclui reavaliações expressamente proibidas nesta missão. Determinismo do carregamento/hash verificado; determinismo integral em duas execuções **não** foi medido. Git HEAD: `d4e816fb5a904f401b5ea1133720fc052d69412d`. A modificação de firmware preexistente foi preservada; não foi criado commit/tag.

Execução completa 69 × 3.461: **NÃO**. Não há métricas globais R1C, seleção final, RC, IDX ou integração. Próximo passo é decisão humana sobre os 12 contratos e quatro FP, triagem dos 14 achados contratuais adicionais e definição, em nova autorização, do destino dos quatro casos de representação e quatro de fonte. Manter R1C congelada. Não repetir regressão, pesquisar indefinidamente ou criar R2 automaticamente.
