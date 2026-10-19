# CC MASS RATIFICATION — painel de decisão humana

> Preparação host-only. Nenhuma relação foi aprovada, materializada ou implantada.

Baseline: `MULTINORM_FROZEN_CF315_198_CC49_39` · auditoria: `9e1febc` · relações prontas: **681**.

| Grupo | Natureza | Relações | Targets | Risco | Recomendação |
|---|---|---:|---:|---|---|
| GROUP_A | Autoridade elevada e relação direta, pronta para decisão em bloco. | 17 | 8 | BAIXO | `APPROVE_GROUP` |
| GROUP_B | Autoridade elevada com nota editorial obrigatória. | 77 | 49 | BAIXO A MODERADO | `APPROVE_GROUP` |
| GROUP_C | Acórdãos de Turma diretos com corroboração textual por outros julgados. | 88 | 88 | MODERADO | `APPROVE_GROUP` |
| GROUP_D | Acórdãos de Turma materialmente diretos, isolados nas fontes consultadas. | 395 | 395 | MODERADO | `APPROVE_GROUP` |
| GROUP_E | Acórdãos de Turma cuja publicação futura usa representante substituto superior ao candidato original. | 76 | 76 | MODERADO | `APPROVE_GROUP` |
| GROUP_F | Exceções materiais que merecem decisão individual, não aprovação genérica. | 28 | 28 | MODERADO A ALTO | `HOLD_GROUP` |

## Regras editoriais transversais

Qualidade material e autoridade são dimensões independentes. Uma relação direta de Turma continua `PERSUASIVE_NON_BINDING`.

**CORROBORATED != BINDING** e **CORROBORATED != NECESSARILY SETTLED**. Corroboração significa somente que outros acórdãos materialmente semelhantes foram encontrados; este painel não usa a expressão “jurisprudência pacífica”.

Todas as decisões permanecem `PENDING`. A aprovação futura exige `group_id` e `group_sha256`; composição alterada invalida a decisão.

## GROUP_A — 17 relações / 8 targets

Autoridade elevada e relação direta, pronta para decisão em bloco.

- Autoridade: Precedente qualificado com mérito e identidade validados.
- Qualificação/notas: Sem nota material especial além da identificação da autoridade.
- Risco residual: BAIXO. Baixo risco após correções sistêmicas; não inclui Tier A rejeitado nem duplicata de leading case.
- Auditadas previamente: 17/17.
- Exemplos: CCMD-0CBA176F7F (CC2002:ART.2028 → STJ:REPETITIVO:310); CCMD-1E3BDA68E1 (CC2002:ART.206:PAR.3:INC.IV → STJ:REPETITIVO:560); CCMD-214F38D88D (CC2002:ART.206:PAR.5:INC.I → STJ:REPETITIVO:1035).
- Consequência de aprovar: registra decisão humana para este conjunto exato; não materializa nem faz deploy. Hash `f10770801f7ff6360d064c675886114f1ae551a738a6453bcafcaf9f072cfa9d`.

## GROUP_B — 77 relações / 49 targets

Autoridade elevada com nota editorial obrigatória.

- Autoridade: Precedente qualificado, súmula ou acórdão de Seção/Corte Especial; autoridade não é inferida da qualidade da relação.
- Qualificação/notas: Aprovação somente com a nota individual já auditada.
- Risco residual: BAIXO A MODERADO. Notas preservam fundamento em paradigma, verbetação estruturada, exceção ou limitação de alcance.
- Auditadas previamente: 77/77.
- Exemplos: CCMD-006CC195E5 (CC2002:ART.682:INC.IV → STJ:REPETITIVO:1198); CCMD-006EC22C7F (CC2002:ART.404 → STJ:REPETITIVO:1368); CCMD-01C3E1F943 (CC2002:ART.1641:INC.II → STJ:ERESP:1623858).
- Consequência de aprovar: registra decisão humana para este conjunto exato; não materializa nem faz deploy. Hash `e4b56d26f9d044bfcdb2d593a1402c0193d803937b83e024bea64e71721ee07d`.

## GROUP_C — 88 relações / 88 targets

Acórdãos de Turma diretos com corroboração textual por outros julgados.

- Autoridade: PERSUASIVE_NON_BINDING; CORROBORATED != BINDING e CORROBORATED != NECESSARILY SETTLED.
- Qualificação/notas: Exige nota explícita de natureza persuasiva; corroboração não autoriza a expressão jurisprudência pacífica.
- Risco residual: MODERADO. A regra de corroboração é proxy textual, não prova de consolidação.
- Auditadas previamente: 88/88.
- Exemplos: CCMD-0124F833D5 (CC2002:ART.102 → STJ:RESP:2032586); CCMD-05878E63BA (CC2002:ART.953:PAR.UNICO → STJ:RESP:1197284); CCMD-0B872A43E6 (CC2002:ART.1973 → STJ:RESP:2183104).
- Consequência de aprovar: registra decisão humana para este conjunto exato; não materializa nem faz deploy. Hash `313efdaa924640c5075bea9b9d7bac5fa627fa07bda004558b7b11c25266a709`.

## GROUP_D — 395 relações / 395 targets

Acórdãos de Turma materialmente diretos, isolados nas fontes consultadas.

- Autoridade: PERSUASIVE_NON_BINDING; não é repetitivo, IAC, súmula nem precedente obrigatório.
- Qualificação/notas: Exige notas de natureza persuasiva e de decisão localizada isoladamente.
- Risco residual: MODERADO. Ausência de corroboração suficiente é explicitada ao leitor.
- Auditadas previamente: 395/395.
- Exemplos: CCMD-0030D273F2 (CC2002:ART.1337 → STJ:RESP:1921653); CCMD-006371F260 (CC2002:ART.1 → STJ:RESP:2142132); CCMD-0273C80981 (CC2002:ART.82 → STJ:ARESP:2328658).
- Consequência de aprovar: registra decisão humana para este conjunto exato; não materializa nem faz deploy. Hash `8605bbfeda8d892494e7deda619a0ee2ca17f9626ef518bbc740d9b2d979accf`.

## GROUP_E — 76 relações / 76 targets

Acórdãos de Turma cuja publicação futura usa representante substituto superior ao candidato original.

- Autoridade: PERSUASIVE_NON_BINDING; a substituição não eleva a autoridade.
- Qualificação/notas: Exige nota de substituição e uso obrigatório do replacement precedent validado.
- Risco residual: MODERADO. 81 substituições prontas foram conferidas estruturalmente; erros de identidade: 0.
- Auditadas previamente: 76/76.
- Exemplos: CCMD-082AC0C812 (CC2002:ART.2027:PAR.UNICO → STJ:RESP:2181097); CCMD-0BCA168976 (CC2002:ART.110 → STJ:RESP:1102424); CCMD-0D408BF14C (CC2002:ART.206:PAR.3 → STJ:RESP:2145475).
- Consequência de aprovar: registra decisão humana para este conjunto exato; não materializa nem faz deploy. Hash `1a312f49fa62e9532d942ce5012283767ad245629598d979c6a41027a74b7929`.

## GROUP_F — 28 relações / 28 targets

Exceções materiais que merecem decisão individual, não aprovação genérica.

- Autoridade: A autoridade é preservada individualmente; nenhum caso recebe elevação automática.
- Qualificação/notas: Revisão individual por temporalidade, correspondência histórica, contextualidade ou target sensível.
- Risco residual: MODERADO A ALTO. Concentra temporalidade, CC/1916, contextualidade, fallback de target e correspondências normativas.
- Auditadas previamente: 28/28.
- Exemplos: CCMD-0A7B64E596 (CC2002:ART.1748:INC.V → STJ:RESP:1705605); CCMD-1B052B7C92 (CC2002:ART.353 → STJ:ARESP:3091360); CCMD-1BBD1E7949 (CC2002:ART.1240 → STJ:ARESP:2318151).
- Consequência de aprovar: registra decisão humana para este conjunto exato; não materializa nem faz deploy. Hash `5d386498f6846d7f0c34eb5c09084964a2d9825d2cc5359c32523210889189c1`.

## Projeções deduplicadas

| Cenário | Relações CC | Targets CC |
|---|---:|---:|
| Baseline físico | 49 | 39 |
| Somente GROUP_A | 66 | 41 |
| GROUP_A + GROUP_B | 143 | 77 |
| + GROUP_C | 231 | 165 |
| + GROUP_D | 626 | 560 |
| Todos os grupos favoráveis | 730 | 663 |

Targets são deduplicados contra o baseline físico; não são soma ingênua das linhas dos grupos.

## Capacidade e bloqueios

A simulação versionada permanece coerente: 1030 lookup entries de limite 4096; PSRAM total estimada 224666 B; blocker: `NO`.

`TURMA_DISPLAY_GATE = PENDING`: nenhuma relação de Turma pode avançar à materialização antes da apresentação compacta e da ficha detalhada serem implementadas e validadas.

Lista completa: `CC_MASS_RATIFICATION_GROUP_MEMBERS.md`. Exceções: `CC_MASS_RATIFICATION_EXCEPTIONS.md`.
