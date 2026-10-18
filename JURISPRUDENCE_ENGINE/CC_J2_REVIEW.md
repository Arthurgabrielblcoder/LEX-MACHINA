# CC-J2 — segundo lote real do Código Civil (propostas aguardando ratificação)

```
LOTE = CC-J2 · NORMA = CC2002 · HOST-ONLY · NADA MATERIALIZADO · STATUS = AWAITING_USER_RATIFICATION (human_approved = false)
CC_J2_CANDIDATES = 30 · GREEN = 9 · YELLOW = 13 · RED = 8 · PROMOTE_RECOMMENDED = 14 · PROMOTE_PROVISIONAL_RECOMMENDED = 1 · REALLOCATE_RECOMMENDED = 2 · MULTI_TARGET_RECOMMENDED = 3 · CONTEXTUAL_RECOMMENDED = 2 · REJECT_RECOMMENDED = 7 · ALREADY_COVERED = 0 · DUPLICATE_RECOMMENDATION = 1 · UNRESOLVED = 0 · HUMAN_JUDGMENT_REQUIRED = 14 · RELATIONS_PROPOSED = 25 · TARGETS_PROPOSED = 22 · NEW_TARGETS_WITHOUT_J = 18 · CC_PHYSICAL_BASELINE = 29/24 · CC_PROJECTED_IF_RATIFIED = 54/42 · CC_PROJECTED_GREEN_ONLY = 38/32 · CC_J1_REVALIDATION_REQUIRED = 0 · CF_REGRESSION = 0 · CC_J1_REGRESSION = 0 · DUPLICATE_QUERY_KEYS = 0 · STJ_QUALIFIED_PRECEDENTS_SOURCE = AVAILABLE
```

## Seleção

Unidade = precedente (todos os alvos descobertos dele juntos). Pontuação = citação oficial direta + vigência do dispositivo + vigência do precedente + lacuna de cobertura do alvo + vários dispositivos; ordem dentro do tema por (-pontuação, canal, id); rodízio entre os temas do CC até 30.

## Decisões

| # | Canal | Tema | Precedente | Alvos descobertos | Temporalidade | Proposta | Alvos propostos | Grupo | Motivo |
|---|---|---|---|---|---|---|---|---|---|
| 1 | STJ_SUMULAS_PDF | COISAS | Súmula 619 STJ | CC2002:ART.1208, CC2002:ART.1255 | CURRENT | **MULTI_TARGET** | CC2002:ART.1208, CC2002:ART.1255 | YELLOW | Ocupação indevida de bem público é mera detenção (art. 1.208), sem indenização por acessões (art. 1.255); dois alvos. |
| 2 | STJ_SUMULAS_PDF | CONTRATOS | Súmula 656 STJ | CC2002:ART.835 | CURRENT | **PROMOTE** | CC2002:ART.835 | GREEN | O enunciado nomeia o art. 835: a exoneração do fiador depende da notificação ali prevista. |
| 3 | STF_SEARCH_Q1 | FAMILIA | RG TEMA 1236 | CC2002:ART.1639:PAR.2 | CURRENT | **CONTEXTUAL** | CC2002:ART.1639:PAR.2 | YELLOW | A ementa cita o art. 1.639, § 2º como exemplo de mudança consensual de regime para situações já constituídas; a tese não o nomeia. |
| 4 | STJ_PRECEDENTES_DADOS_ABERTOS | OBRIGACOES | REPETITIVO STJ 1133 | CC2002:ART.405 | CURRENT | **PROMOTE** | CC2002:ART.405 | GREEN | Tese fixa o termo inicial dos juros de mora "(art. 405 do Código Civil e art. 240 do CPC)"; art. 405 vigente, sem nota de redação. |
| 5 | STJ_PRECEDENTES_DADOS_ABERTOS | PARTE_GERAL | REPETITIVO STJ 1210 | CC2002:ART.50 | CURRENT | **PROMOTE** | CC2002:ART.50 | GREEN | Desconsideração exige abuso "nos termos exigidos pelo art. 50 do Código Civil (Teoria Maior)"; julgado em 2026, depois da redação da Lei 13.874/2019. |
| 6 | STJ_PRECEDENTES_DADOS_ABERTOS | PRESCRICAO_DECADENCIA | IAC 1 | CC2002:ART.202:PAR.UNICO | HISTORICAL_BUT_RELEVANT | **PROMOTE** | CC2002:ART.202:PAR.UNICO | YELLOW | Prescrição intercorrente "conforme interpretação extraída do art. 202, parágrafo único, do Código Civil de 2002", mas só nas causas regidas pelo CPC/73. |
| 7 | PLANALTO_VIDE | SUCESSOES | RG TEMA 498 | CC2002:ART.1829 | CURRENT | **PROMOTE** | CC2002:ART.1829 | GREEN | A tese manda aplicar "o regime do art. 1.829 do CC/2002"; o Planalto anota o RE 646.721 no próprio art. 1.829. |
| 8 | STJ_PRECEDENTES_DADOS_ABERTOS | TRANSICAO | REPETITIVO STJ 639 | CC2002:ART.2028, CC2002:ART.206:PAR.5:INC.I | HISTORICAL_BUT_RELEVANT | **MULTI_TARGET** | CC2002:ART.206:PAR.5:INC.I, CC2002:ART.2028 | YELLOW | Crédito rural sob o CC/2002 prescreve em 5 anos (art. 206, § 5º, I); sob o CC/1916, 20 anos, com a transição do art. 2.028. |
| 9 | STJ_SUMULAS_PDF | PERSONALIDADE | Súmula 642 STJ | CC2002:ART.12, CC2002:ART.943:INC.I, CC2002:ART.948, CC2002:ART.1829, CC2002:ART.1839 | CURRENT | **REALLOCATE** | CC2002:ART.943 | YELLOW | Transmissão do direito à indenização por dano moral com a morte: núcleo no art. 943; a referência "943, I" do STJ não existe no índice (o artigo não tem incisos). |
| 10 | STF_Q1_RECHECK | RESPONSABILIDADE_CIVIL | RG TEMA 920 | CC2002:ART.927 | SUPERSEDED | **REJECT_SUPERSEDED** | — | RED | Repercussão geral negada (questão infraconstitucional): não há tese de mérito; a matéria foi depois decidida no Tema 932. |
| 11 | STJ_PRECEDENTES_DADOS_ABERTOS | COISAS | REPETITIVO STJ 1019 | CC2002:ART.1238 | CURRENT | **REALLOCATE** | CC2002:ART.1238:PAR.UNICO | YELLOW | Desapropriação indireta prescreve em 10 anos "conforme parágrafo único do art. 1.238 do CC"; o adaptador pegou só o artigo. |
| 12 | STJ_PRECEDENTES_DADOS_ABERTOS | CONTRATOS | REPETITIVO STJ 26 | CC2002:ART.591, CC2002:ART.406 | SUPERSEDED | **REJECT_TEMPORAL_MISMATCH** | — | RED | Afasta o limite "do art. 591 c/c o art. 406"; a Lei 14.905/2024 reescreveu os dois artigos e o limite não existe mais no texto. |
| 13 | STF_SEARCH_Q1 | FAMILIA | RG TEMA 529 | CC2002:ART.1566 | CURRENT | **CONTEXTUAL** | CC2002:ART.1566:INC.I | YELLOW | A tese invoca "o dever de fidelidade e a monogamia"; a ementa cita o art. 1.566, I. |
| 14 | STJ_PRECEDENTES_DADOS_ABERTOS | OBRIGACOES | REPETITIVO STJ 368 | CC2002:ART.286 | CURRENT | **PROMOTE** | CC2002:ART.286 | GREEN | Créditos do empréstimo compulsório podem ser cedidos, incidindo "notadamente o art. 286 do Código Civil" (cessão de crédito). |
| 15 | STJ_SUMULAS_PDF | PARTE_GERAL | Súmula 530 STJ | CC2002:ART.112, CC2002:ART.122, CC2002:ART.170, CC2002:ART.406, CC2002:ART.591 | CURRENT | **REJECT_NOT_MATERIAL** | — | RED | Núcleo é a taxa média do Bacen nos contratos bancários; arts. 112/122/170 são cânones gerais e 406/591 foram reescritos em 2024. |
| 16 | STJ_PRECEDENTES_DADOS_ABERTOS | PRESCRICAO_DECADENCIA | REPETITIVO STJ 1109 | CC2002:ART.191 | CURRENT | **PROMOTE** | CC2002:ART.191 | GREEN | Tese delimita a renúncia tácita à prescrição "(art. 191 do Código Civil)" no reconhecimento administrativo de direito. |
| 17 | PLANALTO_VIDE | SUCESSOES | RG TEMA 809 | CC2002:ART.1829 | CURRENT | **PROMOTE** | CC2002:ART.1829 | GREEN | Mesma tese do Tema 498, tema próprio (união heteroafetiva); o Planalto anota o RE 878.694 no art. 1.829. |
| 18 | STJ_SUMULAS_PDF | COISAS | Súmula 637 STJ | CC2002:ART.1210:PAR.2 | CURRENT | **PROMOTE** | CC2002:ART.1210:PAR.2 | YELLOW | O ente público pode deduzir até o domínio na possessória entre particulares: exceção ao art. 1.210, § 2º. |
| 19 | STJ_SUMULAS_PDF | CONTRATOS | Súmula 539 STJ | CC2002:ART.591 | SUPERSEDED | **REJECT_TEMPORAL_MISMATCH** | — | RED | A referência ao art. 591 era à "capitalização anual"; a Lei 14.905/2024 tirou a capitalização do texto. |
| 20 | STJ_SUMULAS_PDF | FAMILIA | Súmula 655 STJ | CC2002:ART.1641:INC.II | NEEDS_REVIEW | **PROMOTE** | CC2002:ART.1641:INC.II | YELLOW | União estável de septuagenário: separação obrigatória, comunicando-se os aquestos com esforço comum; precisa ser lida junto com o Tema 1236 (2024). |
| 21 | STJ_PRECEDENTES_DADOS_ABERTOS | OBRIGACOES | REPETITIVO STJ 381 | CC2002:ART.354 | CURRENT | **PROMOTE** | CC2002:ART.354 | YELLOW | Tese de exclusão: a imputação do art. 354 não se aplica à compensação tributária (originou a Súmula 464/STJ). |
| 22 | STJ_PRECEDENTES_DADOS_ABERTOS | PARTE_GERAL | REPETITIVO STJ 1130 | CC2002:ART.76:PAR.UNICO | CURRENT | **PROMOTE_PROVISIONAL** | CC2002:ART.76:PAR.UNICO | YELLOW | Título coletivo do sindicato restrito aos que têm domicílio necessário (art. 76, p.u.) na base territorial; RE pendente no STF (RG 1432). |
| 23 | STJ_PRECEDENTES_DADOS_ABERTOS | PRESCRICAO_DECADENCIA | REPETITIVO STJ 308 | CC2002:ART.206:PAR.3:INC.III | CURRENT | **PROMOTE** | CC2002:ART.206:PAR.3:INC.III | GREEN | Dividendos da subscrição complementar CRT prescrevem em três anos "nos termos do art. 206, § 3º, inciso III, do Código Civil de 2002". |
| 24 | STJ_SUMULAS_PDF | CONTRATOS | Súmula 541 STJ | CC2002:ART.591 | SUPERSEDED | **REJECT_TEMPORAL_MISMATCH** | — | RED | Mesmo caso da Súmula 539: pactuação da capitalização contra a antiga redação do art. 591. |
| 25 | STJ_PRECEDENTES_DADOS_ABERTOS | OBRIGACOES | REPETITIVO STJ 426 | CC2002:ART.354 | CURRENT | **PROMOTE** | CC2002:ART.354 | GREEN | No SFH aplica-se, salvo cláusula em contrário, "a regra de imputação prevista no art. 354 do Código Civil de 2002". |
| 26 | STJ_PRECEDENTES_DADOS_ABERTOS | PRESCRICAO_DECADENCIA | REPETITIVO STJ 309 | CC2002:ART.206:PAR.3:INC.III | CURRENT | **DUPLICATE_RECOMMENDATION** | — | RED | Questão e tese idênticas às do Tema 308 (mesmo julgamento, outro recurso): um único vínculo basta. |
| 27 | STJ_SUMULAS_PDF | CONTRATOS | Súmula 465 STJ | CC2002:ART.757, CC2002:ART.765, CC2002:ART.785 | SUPERSEDED | **REJECT_TEMPORAL_MISMATCH** | — | RED | Arts. 757, 765 e 785 revogados pela Lei 15.040/2024 (contrato de seguro saiu do CC). |
| 28 | STJ_PRECEDENTES_DADOS_ABERTOS | OBRIGACOES | REPETITIVO STJ 587 | CC2002:ART.368 | HISTORICAL_BUT_RELEVANT | **PROMOTE** | CC2002:ART.368 | YELLOW | Honorários de embargos e de execução não se compensam por falta de reciprocidade, pressuposto do art. 368. |
| 29 | STJ_PRECEDENTES_DADOS_ABERTOS | PRESCRICAO_DECADENCIA | REPETITIVO STJ 610 | CC2002:ART.206:PAR.3:INC.IV, CC2002:ART.2028 | HISTORICAL_BUT_RELEVANT | **MULTI_TARGET** | CC2002:ART.206:PAR.3:INC.IV, CC2002:ART.2028 | YELLOW | Nulidade de reajuste de plano de saúde: 3 anos (art. 206, § 3º, IV) sob o CC/2002, com a transição do art. 2.028. |
| 30 | STJ_SUMULAS_PDF | CONTRATOS | Súmula 610 STJ | CC2002:ART.797, CC2002:ART.798 | SUPERSEDED | **REJECT_TEMPORAL_MISMATCH** | — | RED | Arts. 797 e 798 revogados pela Lei 15.040/2024. |

## Interações com o CC-J1 (congelado; nada alterado)

- RG TEMA 1236: CC_J1_SAME_PRECEDENT_NEW_TARGET — Mesmo precedente do CCJ1-06 (art. 1.641, II); novo alvo; ficha STF_RG_1236.TXT já no cartão.
- RG TEMA 498: CC_J1_SAME_PRECEDENT_NEW_TARGET — Mesmo precedente do CCJ1-03 (art. 1.790); novo alvo, mesma ficha STF_RG_498.TXT já no cartão. O CC-J1 não muda.
- REPETITIVO STJ 639: CC_J1_COMPATIBLE_INTERACTION — Alvos com a Súmula 547 (CCJ1-25), mesma solução de prazo e transição: coerente.
- RG TEMA 920: CC_J1_COMPATIBLE_INTERACTION — Confirma o CCJ1-07 (Tema 932 no art. 927, p.u.).
- RG TEMA 529: CC_J1_SAME_PRECEDENT_NEW_TARGET — Mesmo precedente do CCJ1-05 (art. 1.723, § 1º); o 1.566, I nunca foi apresentado no CC-J1. Ficha STF_RG_529.TXT já no cartão.
- RG TEMA 809: CC_J1_SAME_PRECEDENT_NEW_TARGET — Mesmo precedente do CCJ1-04; ficha STF_RG_809.TXT já no cartão.
- Súmula 655 STJ: CC_J1_COMPATIBLE_INTERACTION — Responde ao alerta do dossiê do CC-J1 (item 6): a súmula não foi superada; rege o caso sem pacto. O vínculo do Tema 1236 no CC-J1 não muda.
- REPETITIVO STJ 610: CC_J1_COMPATIBLE_INTERACTION — Mesma solução de prazo da Súmula 547 (CCJ1-25): coerente.

## Notas do lote

- **CCJ1_09**: Tema 1194 continua PENDING_HUMAN_REVIEW: nenhuma fonte oficial nova liga o tema ao art. 206-A (Planalto sem anotação; dataset do STJ sem tema sobre o art. 206-A).
- **CCJ1_30**: Súmula 609 continua PENDING_TEMPORAL_REVALIDATION: nenhuma decisão do STJ posterior à Lei 15.040/2024, nenhuma revisão ou cancelamento no PDF oficial nem no dataset de precedentes qualificados.
- **CC_J1_REVALIDATION_REQUIRED**: 0 — interações encontradas são todas compatíveis (Súmula 655 × Tema 1236; Temas 610/639 × Súmula 547; Tema 920 × Tema 932) ou novos alvos de precedentes já publicados.
- **CF_MATERIALIZATION_PENDING**: 9 relações da CF ratificadas e não instaladas (Batch10 6 + Súmulas 203/403 STJ 3): fila separada, não pesquisada nem tocada no CC-J2.

## Cobertura do CC por livro (atual → projetada; a projeção não é baseline)

| Livro | Relações | Alvos | Artigos com J | Artigos no CC | Densidade |
|---|---:|---:|---:|---:|---:|
| PARTE_GERAL | 10 → 17 | 8 → 13 | 6 → 10 | 236 | 2.54% → 4.24% |
| OBRIGACOES | 6 → 13 | 5 → 11 | 4 → 10 | 736 | 0.54% → 1.36% |
| EMPRESA | 1 → 1 | 1 → 1 | 1 → 1 | 232 | 0.43% → 0.43% |
| COISAS | 4 → 8 | 4 → 8 | 4 → 8 | 350 | 1.14% → 2.29% |
| FAMILIA | 4 → 7 | 4 → 6 | 4 → 6 | 259 | 1.54% → 2.32% |
| SUCESSOES | 2 → 4 | 1 → 2 | 1 → 2 | 245 | 0.41% → 0.82% |
| DISPOSICOES_FINAIS_TRANSITORIAS | 2 → 4 | 1 → 1 | 1 → 1 | 19 | 5.26% → 5.26% |

Menor densidade projetada: EMPRESA, SUCESSOES, OBRIGACOES.

## Velocidade da fábrica (CC-J1 × CC-J2)

| Métrica | CC-J1 | CC-J2 |
|---|---:|---:|
| Candidatos | 30 (pares) | 30 (precedentes) |
| Relações propostas | 25 | 25 |
| Etapas automáticas (6 checagens + ficha, por candidato) | 200/210 | 201/210 |
| Exclusões automáticas no backlog | — | 49 |
| Revisão humana (julgamento jurídico) | 15 | 14 |
| Correções manuais de alvo | — | 3 |
| Código novo de motor (linhas) | 310 | 351 |
| Código de configuração do lote (linhas) | — (misturado no motor do lote) | 270 |
| Dados de revisão humana (linhas) | 152 | 184 |
| Ferramentas existentes modificadas | 0 | 1 |
| Novos adapters | 0 (2 feitos logo antes) | 1 |
| Bloqueios de fonte | 1 | 0 |

Por etapa (CC-J2): AUTO_DISCOVERED 30/30, AUTO_TARGET_NORMALIZED 30/30, AUTO_NAMESPACE_CHECKED 30/30, AUTO_TEMPORAL_CHECKED 29/30, AUTO_DUPLICATE_CHECKED 30/30, AUTO_SOURCE_VERIFIED 30/30, AUTO_FICHA_DRAFTED 22/30.
SCALABILITY_WARNING = YES_ONE_TIME: O CC-J1 tinha a etapa de lote (seleção, revisão, dossiê, simulação) codificada só para ele; repeti-la exigiria reescrever lógica de lote a cada lote. O CC-J2 a generalizou uma vez em batch_engine.py, sem nada específico do CC (a norma entra por configuração). Nenhuma lógica específica do CC foi reescrita. Meta do próximo lote: NEW_CORE_ENGINE_CODE = 0 (só configuração + tabela de revisão).
Lacunas de automação: realocação "parágrafo único do art." (Tema 1019) e referência inexistente "943, I" (Súmula 642); duplicata de tese idêntica entre temas (308/309): detectável automaticamente (questão + tese iguais); hoje humana; pertinência material, temporalidade jurídica (Leis 14.905/2024 e 15.040/2024) e interação com o CC-J1: humanas.

## Fontes STJ fora das súmulas (Parte C)

STJ_QUALIFIED_PRECEDENTS_SOURCE = AVAILABLE. O Portal de Dados Abertos do STJ publica o dataset "Precedentes qualificados" (CC-BY; Temas.csv com temas repetitivos, IAC, SIRDR, PUIL e controvérsias, tese firmada e situação). A página oficial de pesquisa de precedentes qualificados também respondeu normalmente. Nenhum desafio anti-robô foi contornado. Integração host-only pelo adaptador #4 (`discovery_stj_precedentes.py` → `stj/STJ_PRECEDENTES_INDEX.json`).
Backlog: 111 pares descobertos, 49 excluídos automaticamente (CCJ1_DECIDED_TARGET_SET 5, CCJ1_PENDING 4, CCJ1_REJECTED_PRECEDENT 9, EQUIVALENT_SUMULA_DECIDED 4, IN_PHYSICAL_BASELINE 26, PRECEDENT_NOT_CURRENT 1), 41 precedentes candidatos, 30 selecionados; ficam para o próximo lote: STF:RG:1191, STJ:SUMULA:426, STJ:SUMULA:504, STJ:SUMULA:529, STJ:SUMULA:620, STJ:REPETITIVO:99, STJ:REPETITIVO:112, STJ:REPETITIVO:883, STJ:REPETITIVO:919, STJ:REPETITIVO:932, STJ:REPETITIVO:1035.

Nenhuma decisão é HUMAN_APPROVED. A ratificação é do usuário.
