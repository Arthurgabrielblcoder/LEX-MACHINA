# CC-J1 — primeiro lote real do Código Civil (propostas aguardando ratificação)

```
LOTE = CC-J1 · NORMA = CC2002 · HOST-ONLY · NADA MATERIALIZADO · STATUS = AWAITING_USER_RATIFICATION (human_approved = false)
CC_J1_CANDIDATES = 30 · CC_J1_PROMOTE = 17 · CC_J1_REALLOCATE = 7 · CC_J1_REJECT = 6 · CC_J1_UNRESOLVED = 0 · CC_J1_TEMPORAL_ALERTS = 2 · CC_J1_HISTORICAL_BUT_RELEVANT = 1 · CC_J1_HUMAN_REVIEW_REQUIRED = 15 · CC_J1_RELATIONS_PROPOSED = 25 · CC_J1_TARGETS_PROPOSED = 22 · CC_J1_SIMULATION_RELATIONS = 23 · CC_J1_AWAITING_RATIFICATION = 30 · STJ_RELATIONS_DISCOVERABLE_TOTAL = 727 · STJ_CC2002_RELATIONS = 59
```

## Seleção

(deterministic, 30): 10 from Planalto/STF = the first candidate of each distinct precedent of the portability pilot (ADI 6792/7055
judged together count as one) + the next one; 20 from the official STJ súmulas channel = the two mandatory Súmula 403 links (CC 186, 927)
+ 18 súmulas by round-robin over the STJ's own legal branch, taking per súmula its first pair that is CURRENT, on a dispositivo present in the
CC2002 index, from a vigente súmula (revoked insurance articles, cancelled súmulas and CC/1916-only references are avoided at selection).

## Decisões

| # | Canal | Target descoberto | Precedente | Tribunal | Temporalidade | Proposta | Alvo proposto | Humano | Razão |
|---|---|---|---|---|---|---|---|---|---|
| 1 | PLANALTO_VIDE | CC2002:ART.20 | ADI 4815 | STF | CURRENT | **PROMOTE** | CC2002:ART.20 | não | Ementa: interpretação conforme aos arts. 20 e 21 do CC (biografias), sem redução de texto. |
| 2 | PLANALTO_VIDE | CC2002:ART.186 | ADI 6792/7055 | STF | CURRENT | **PROMOTE** | CC2002:ART.186, CC2002:ART.927 | sim | ADI 6792 e 7055 julgadas em conjunto (22/05/2024): interpretação conforme aos arts. 186 e 927 (responsabilidade de jornalistas só com dolo ou culpa grave). Um registro conjunto em dois targets; o registro conjunto é decisão humana. |
| 3 | PLANALTO_VIDE | CC2002:ART.1790 | RG TEMA 498 | STF | CURRENT | **PROMOTE** | CC2002:ART.1790 | não | Tese: inconstitucional a distinção de regimes sucessórios do art. 1.790 (união homoafetiva). |
| 4 | PLANALTO_VIDE | CC2002:ART.1790 | RG TEMA 809 | STF | CURRENT | **PROMOTE** | CC2002:ART.1790 | não | Mesma tese, tema próprio (registro separado do Tema 498). |
| 5 | STF_SEARCH_Q1 | CC2002:ART.1727 | RG TEMA 529 | STF | CURRENT | **REALLOCATE** | CC2002:ART.1723:PAR.1 | sim | A tese ressalva a exceção do art. 1.723, § 1º; o art. 1.727 aparece só como fundamento. |
| 6 | STF_SEARCH_Q1 | CC2002:ART.1641 | RG TEMA 1236 | STF | CURRENT | **REALLOCATE** | CC2002:ART.1641:INC.II | não | Tese sobre o inciso II (maiores de 70 anos): norma dispositiva, afastável por convenção. |
| 7 | STF_SEARCH_Q1 | CC2002:ART.927 | RG TEMA 932 | STF | CURRENT | **REALLOCATE** | CC2002:ART.927:PAR.UNICO | não | Tese nomeia o art. 927, parágrafo único (teoria do risco). |
| 8 | STF_SEARCH_Q1 | CC2002:ART.1521 | RG TEMA 526 | STF | CURRENT | **REJECT_NOT_MATERIAL** | — | sim | Tema previdenciário (pensão a concubina); o art. 1.521 (impedimentos) é só fundamento. |
| 9 | STF_SEARCH_Q1 | CC2002:ART.206 | RG TEMA 1194 | STF | CURRENT | **REALLOCATE** | CC2002:ART.206-A | sim | O texto oficial cita o art. 206-A (prescrição intercorrente), afastado na execução de dano ambiental. |
| 10 | PLANALTO_VIDE | CC2002:ART.21 | ADI 4815 | STF | CURRENT | **PROMOTE** | CC2002:ART.21 | não | Mesmo acórdão; art. 21 nomeado na ementa. |
| 11 | STJ_SUMULAS_PDF | CC2002:ART.186 | Súmula 403 STJ | STJ | CURRENT | **PROMOTE** | CC2002:ART.186 | não | Dano à imagem com fins comerciais: dano presumido; o art. 186 ("ainda que exclusivamente moral") é referência oficial do STJ. O art. 20 seria alvo adicional possível (não referenciado pelo STJ). |
| 12 | STJ_SUMULAS_PDF | CC2002:ART.927 | Súmula 403 STJ | STJ | CURRENT | **PROMOTE** | CC2002:ART.927 | não | Mesma súmula: dever de indenizar independentemente de prova do prejuízo. Mesma ficha do art. 186. |
| 13 | STJ_SUMULAS_PDF | CC2002:ART.1420 | Súmula 308 STJ | STJ | CURRENT | **PROMOTE** | CC2002:ART.1420 | sim | Ineficácia da hipoteca da construtora perante adquirentes; art. 1.420 (legitimação para hipotecar) é a referência do STJ; pertinência indireta. |
| 14 | STJ_SUMULAS_PDF | CC2002:ART.877 | Súmula 322 STJ | STJ | CURRENT | **PROMOTE** | CC2002:ART.877 | não | Excepciona expressamente a exigência de prova do erro do art. 877 (contas-correntes). |
| 15 | STJ_SUMULAS_PDF | CC2002:ART.1647:INC.III | Súmula 332 STJ | STJ | CURRENT | **PROMOTE** | CC2002:ART.1647:INC.III | não | Fiança sem outorga do cônjuge: o inciso III exige a autorização. |
| 16 | STJ_SUMULAS_PDF | CC2002:ART.2028 | Súmula 371 STJ | STJ | CURRENT | **REJECT_NOT_MATERIAL** | — | não | A súmula trata do cálculo do VPA; a regra de transição de prazos não é o seu objeto. |
| 17 | STJ_SUMULAS_PDF | CC2002:ART.2028 | Súmula 405 STJ | STJ | NEEDS_REVIEW | **REALLOCATE** | CC2002:ART.206:PAR.3:INC.IX | sim | O prazo trienal do DPVAT é o do art. 206, § 3º, IX (outra referência oficial do STJ); o art. 2.028 é transição. O regime do seguro obrigatório mudou em 2024: revisar a vigência para fatos novos. |
| 18 | STJ_SUMULAS_PDF | CC2002:ART.205 | Súmula 412 STJ | STJ | CURRENT | **PROMOTE** | CC2002:ART.205 | sim | Repetição de tarifas de água e esgoto: "prazo prescricional estabelecido no Código Civil"; a referência oficial é o art. 205 (prazo geral). |
| 19 | STJ_SUMULAS_PDF | CC2002:ART.1142 | Súmula 451 STJ | STJ | CURRENT | **REJECT_NOT_MATERIAL** | — | sim | Penhorabilidade da sede é questão processual (CPC/LEF); o conceito de estabelecimento é só pano de fundo. |
| 20 | STJ_SUMULAS_PDF | CC2002:ART.186 | Súmula 476 STJ | STJ | CURRENT | **REALLOCATE** | CC2002:ART.917 | não | O núcleo é o endosso-mandato (art. 917, outra referência oficial); o art. 186 é genérico. |
| 21 | STJ_SUMULAS_PDF | CC2002:ART.1231 | Súmula 496 STJ | STJ | CURRENT | **REALLOCATE** | CC2002:ART.99 | sim | Inoponibilidade do registro à União decorre da natureza de bem público (art. 99, outra referência oficial); a presunção do art. 1.231 é o que a súmula afasta. |
| 22 | STJ_SUMULAS_PDF | CC2002:ART.966 | Súmula 499 STJ | STJ | CURRENT | **PROMOTE** | CC2002:ART.966 | sim | Prestadoras de serviço são empresas: a súmula se apoia no conceito de empresário do art. 966. |
| 23 | STJ_SUMULAS_PDF | CC2002:ART.206:PAR.5:INC.I | Súmula 503 STJ | STJ | CURRENT | **PROMOTE** | CC2002:ART.206:PAR.5:INC.I | não | Monitória de cheque sem força executiva: prazo quinquenal do § 5º, I. |
| 24 | STJ_SUMULAS_PDF | CC2002:ART.122 | Súmula 543 STJ | STJ | CURRENT | **REJECT_NOT_MATERIAL** | — | sim | Restituição na resolução de compra de imóvel é regra consumerista; condição potestativa (art. 122) é fundamento lateral. |
| 25 | STJ_SUMULAS_PDF | CC2002:ART.2028 | Súmula 547 STJ | STJ | HISTORICAL_BUT_RELEVANT | **PROMOTE** | CC2002:ART.2028 | não | O enunciado manda observar "a regra de transição disciplinada em seu art. 2.028" (CC/1916 → CC/2002). |
| 26 | STJ_SUMULAS_PDF | CC2002:ART.187 | Súmula 550 STJ | STJ | CURRENT | **REJECT_NOT_MATERIAL** | — | sim | Credit scoring: núcleo no CDC e na Lei do Cadastro Positivo; abuso de direito (art. 187) é lateral. |
| 27 | STJ_SUMULAS_PDF | CC2002:ART.1226 | Súmula 585 STJ | STJ | CURRENT | **PROMOTE** | CC2002:ART.1226 | sim | Alienação do veículo (móvel) pela tradição afasta o IPVA posterior do ex-proprietário; o art. 1.267 é alternativa (também referência oficial). |
| 28 | STJ_SUMULAS_PDF | CC2002:ART.186 | Súmula 595 STJ | STJ | CURRENT | **REJECT_NOT_MATERIAL** | — | sim | Responsabilidade objetiva da instituição de ensino (CDC); o ilícito culposo do art. 186 não é o fundamento. |
| 29 | STJ_SUMULAS_PDF | CC2002:ART.1696 | Súmula 596 STJ | STJ | CURRENT | **PROMOTE** | CC2002:ART.1696 | não | Alimentos avoengos complementares e subsidiários (art. 1.696; o art. 1.698 é a outra referência oficial). |
| 30 | STJ_SUMULAS_PDF | CC2002:ART.422 | Súmula 609 STJ | STJ | NEEDS_REVIEW | **PROMOTE** | CC2002:ART.422 | sim | Boa-fé objetiva (art. 422) segue vigente, mas os arts. 765 e 766 também referenciados foram revogados pela Lei 15.040/2024 (seguros): revisar se a súmula subsiste sob a lei nova. |

## Fontes

- STF: fontes do piloto (`pilot_cc/cc_pilot_evidence.py`, sha256 do innerText).
- STJ: PDF oficial "Súmulas do STJ" (sha256 `bf92bdb1ae0d2573…`), enunciado e referências legislativas do próprio STJ.

Nenhuma decisão é HUMAN_APPROVED. A ratificação é do usuário.
