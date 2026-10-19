# Ratificação humana massiva — Código Civil

Registro emitido em `2026-10-19T15:50:57-03:00` para a composição exata fixada no commit `aeb769d`, com auditoria-base `9e1febc`.

## Decisão

| Grupo | Decisão | Relações | SHA-256 da composição |
| --- | --- | ---: | --- |
| GROUP_A | `APPROVE_GROUP` | 17 | `f10770801f7ff6360d064c675886114f1ae551a738a6453bcafcaf9f072cfa9d` |
| GROUP_B | `APPROVE_GROUP` | 77 | `e4b56d26f9d044bfcdb2d593a1402c0193d803937b83e024bea64e71721ee07d` |
| GROUP_C | `APPROVE_GROUP` | 88 | `313efdaa924640c5075bea9b9d7bac5fa627fa07bda004558b7b11c25266a709` |
| GROUP_D | `APPROVE_GROUP` | 395 | `8605bbfeda8d892494e7deda619a0ee2ca17f9626ef518bbc740d9b2d979accf` |
| GROUP_E | `APPROVE_GROUP` | 76 | `1a312f49fa62e9532d942ce5012283767ad245629598d979c6a41027a74b7929` |
| GROUP_F | `HOLD_GROUP` | 28 | `5d386498f6846d7f0c34eb5c09084964a2d9825d2cc5359c32523210889189c1` |

A–E estão aprovados em bloco: 653 relações, 610 targets tocados e 597 novos targets distintos. O GROUP_F permanece integralmente em hold: 28 relações, zero aprovações.

Cada um dos 681 IDs e seu estado consta em `CC_MASS_RATIFICATION_RECORD.json`. Os hashes dos seis grupos são obrigatórios e coincidem com a preparação imutável.

## Autoridade e publicação

A ratificação aprova a relação sem promover a autoridade. As 559 relações de Turma em C, D e E continuam `PERSUASIVE_NON_BINDING`. Em C, corroboração não significa caráter vinculante nem orientação necessariamente pacificada. Em D, cada item continua sendo decisão isolada obtida de fonte oficial. Em E, deve ser publicado exclusivamente o replacement precedent validado; o candidato superado não pode ser publicado.

## Tracks e gates

| Track | Grupos | Relações | Estado / próximo gate |
| --- | --- | ---: | --- |
| 1 — alta autoridade | A + B | 94 | apto a posterior preflight de materialização |
| 2 — Turma | C + D + E | 559 | exige `TURMA_DISPLAY_GATE` antes da materialização |
| 3 — hold | F | 28 | revisão individual |

`TURMA_DISPLAY_GATE=PENDING`. Nenhuma materialização, alteração de SD, firmware ou baseline físico foi feita.

## Reconciliação

- Projeção ratificada do CC: **702 relações / 636 targets**.
- Baseline físico do CC: **49/39** (inalterado).
- Baseline físico de CF/ADCT: **315/198** (inalterado).
- Elevações de autoridade: **0**.
- Erros de publicação de substituição: **0**.
- Novas relações materializadas: **0**.
