# CC-J1 — ratificação humana

```
RATIFICADO PELO USUÁRIO EM 2026-10-18 · SEM MATERIALIZAÇÃO · SEM PACOTE FÍSICO · SEM DEPLOY · CF 315/198 INALTERADA
TOTAL_PROPOSALS = 30 · PROPOSALS_HUMAN_APPROVED = 22 · PROPOSALS_PENDING = 2 · PROPOSALS_REJECTED = 6 · NORMALIZED_RELATIONS_APPROVED = 29 · DISTINCT_CC_TARGETS_APPROVED = 24 · DISTINCT_PRECEDENTS_APPROVED = 20 · DISTINCT_FICHAS_REQUIRED = 20 · ADDITIONAL_TARGETS_APPROVED = 6
```

Registro: `CC_J1_RATIFICATION_RECORD.json` (gerado por `build_cc_j1_ratification_record.py`). Ele fixa por sha256 o `CC_J1_DECISIONS.json`, o dossiê e o índice STJ, sem modificá-los. Targets adicionais só são aceitos quando constam das referências legislativas oficiais do STJ.

## Aprovadas (22)

| ID | Precedente | Estado | Targets finais | Nota |
|---|---|---|---|---|
| CCJ1-01 | ADI 4815 | HUMAN_APPROVED | CC2002:ART.20 | — |
| CCJ1-02 | ADI 6792/7055 | HUMAN_APPROVED_MULTI_TARGET | CC2002:ART.186, CC2002:ART.927 | Julgamento conjunto ADI 6792/7055 (ficha conjunta); interpretação conforme aos arts. 186 e 927, caput (responsabilidade civil da imprensa). |
| CCJ1-03 | RG TEMA 498 | HUMAN_APPROVED | CC2002:ART.1790 | — |
| CCJ1-04 | RG TEMA 809 | HUMAN_APPROVED | CC2002:ART.1790 | — |
| CCJ1-05 | RG TEMA 529 | HUMAN_APPROVED_REALLOCATE | CC2002:ART.1723:PAR.1 | Somente o art. 1.723, § 1º (ressalvado pela tese); art. 1.727 não acrescentado. |
| CCJ1-06 | RG TEMA 1236 | HUMAN_APPROVED_REALLOCATE | CC2002:ART.1641:INC.II | A tese interpreta o inciso II; Tema 1236 com trânsito em julgado em 10/04/2024. |
| CCJ1-07 | RG TEMA 932 | HUMAN_APPROVED_REALLOCATE | CC2002:ART.927:PAR.UNICO | Parágrafo único (não o caput); ficha STF_RG_932 compartilhada entre CF e CC. |
| CCJ1-10 | ADI 4815 | HUMAN_APPROVED | CC2002:ART.21 | — |
| CCJ1-11 | Súmula 403 STJ | HUMAN_APPROVED | CC2002:ART.186 | Referência legislativa oficial do STJ; uma ficha para os dois vínculos da Súmula 403; art. 20 não acrescentado. |
| CCJ1-12 | Súmula 403 STJ | HUMAN_APPROVED | CC2002:ART.927 | Mesma ficha da CCJ1-11. |
| CCJ1-13 | Súmula 308 STJ | HUMAN_APPROVED | CC2002:ART.1420 | Referência legislativa oficial do STJ; eficácia da hipoteca perante adquirentes. |
| CCJ1-14 | Súmula 322 STJ | HUMAN_APPROVED | CC2002:ART.877 | — |
| CCJ1-15 | Súmula 332 STJ | HUMAN_APPROVED | CC2002:ART.1647:INC.III | — |
| CCJ1-17 | Súmula 405 STJ | HUMAN_APPROVED_MULTI_TARGET | CC2002:ART.206:PAR.3:INC.IX, CC2002:ART.2028 | Prescrição da cobrança do DPVAT; preservar o contexto legislativo; revalidar se a súmula for cancelada ou o STJ alterar a orientação. Não considerada superada pela reforma geral de seguros. |
| CCJ1-18 | Súmula 412 STJ | HUMAN_APPROVED | CC2002:ART.205 | Prazo geral decenal; art. 206 não acrescentado; eventual art. 2.028 exige evidência própria. |
| CCJ1-20 | Súmula 476 STJ | HUMAN_APPROVED_MULTI_TARGET | CC2002:ART.662, CC2002:ART.917 | Dispositivos específicos de mandato e endosso-mandato; vínculo genérico ao art. 186 NÃO criado. |
| CCJ1-21 | Súmula 496 STJ | HUMAN_APPROVED_MULTI_TARGET | CC2002:ART.99, CC2002:ART.1231 | Contexto da ficha: terrenos de marinha / propriedade da União. |
| CCJ1-22 | Súmula 499 STJ | HUMAN_APPROVED_CONTEXTUAL | CC2002:ART.966 | CONTEXTUAL_APPLICATION: assunto principal tributário (Sesc/Senac); o art. 966 entra como conceito de empresário usado pelo STJ. |
| CCJ1-23 | Súmula 503 STJ | HUMAN_APPROVED | CC2002:ART.206:PAR.5:INC.I | — |
| CCJ1-25 | Súmula 547 STJ | HUMAN_APPROVED_MULTI_TARGET | CC2002:ART.2028, CC2002:ART.206:PAR.3:INC.IV, CC2002:ART.206:PAR.5:INC.I | TEMPORAL_CONTEXT = CC1916_TO_CC2002. |
| CCJ1-27 | Súmula 585 STJ | HUMAN_APPROVED_MULTI_TARGET | CC2002:ART.1226, CC2002:ART.1267 | Contexto: alienação de veículo / IPVA / transferência da propriedade móvel. |
| CCJ1-29 | Súmula 596 STJ | HUMAN_APPROVED | CC2002:ART.1696 | — |

## Pendentes (2)

- **CCJ1-09, RG TEMA 1194:** `PENDING_HUMAN_REVIEW`. MATERIAL_EXCEPTION_POSSIBLE: a fonte oficial consultada não ancora a tese no art. 206-A. Reabrir com evidência oficial de pertinência direta ao art. 206-A. Não rejeitado.
- **CCJ1-30, Súmula 609 STJ:** `PENDING_TEMPORAL_REVALIDATION`. NO_CC_RELATION_PUBLISHED. Súmula 609 consta na base oficial, mas os arts. 765 e 766 de suas referências foram revogados pela Lei 15.040/2024. Reabrir com: (1) decisão do STJ posterior à vigência da lei aplicando a súmula; (2) eventual cancelamento, revisão ou distinção; (3) correspondência com a nova Lei de Seguros.

## Não aprovadas (6)

- **CCJ1-08, RG TEMA 526:** REJECT_NOT_MATERIAL_RECOMMENDED (categoria do dossiê). Reabrir só se surgir precedente que interprete os impedimentos do art. 1.521.
- **CCJ1-16, Súmula 371 STJ:** REJECT_NOT_MATERIAL_RECOMMENDED (categoria do dossiê). Reabrir só se o STJ revisar a súmula com foco na transição de prazos.
- **CCJ1-19, Súmula 451 STJ:** REJECT_NOT_MATERIAL_RECOMMENDED (categoria do dossiê). Reabrir se surgir precedente que interprete o art. 1.142.
- **CCJ1-24, Súmula 543 STJ:** REJECT_NOT_MATERIAL_RECOMMENDED (categoria do dossiê). Reabrir se surgir precedente sobre condição potestativa (art. 122).
- **CCJ1-26, Súmula 550 STJ:** REJECT_NOT_MATERIAL_RECOMMENDED (categoria do dossiê). Reabrir se o STJ fundamentar no art. 187.
- **CCJ1-28, Súmula 595 STJ:** REJECT_NOT_MATERIAL_RECOMMENDED (categoria do dossiê). Reabrir só com fundamentação no CC.

**Próximo passo:** `CC-J1 MATERIALIZATION PREFLIGHT`. O CC-J2 e o Batch11 não foram iniciados.
