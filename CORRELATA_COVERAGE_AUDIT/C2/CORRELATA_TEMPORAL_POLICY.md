# C2 — Política temporal das CORRELATAs

## Estados

| `temporal_status` | Entra no overlay? | Exige | Aparelho |
|---|---|---|---|
| IN_FORCE | sim | — | publica |
| VACATIO_LEGIS | sim | `effective_from` (data), `vacatio_policy` | oculto até a vigência |
| PARTIAL_EFFECTS | sim | `judicial_status` completo e flag JUDICIAL_RESTRICTIONS | publica com aviso |
| TRANSITIONAL | sim | `revalidate_on` | publica; revalidação agendada |
| REVOKED | não | — | — |
| UNCERTAIN | não | — | — |

## Vacatio legis

**Caso de referência:** Lei 14.965/2024 (concursos públicos). Vigência em 2028-01-01, com aplicação antecipada possível (art. 13).

- Aceita no HIGH: arts. 131, § 2º e 132.
- Vínculo legado já visível: art. 37, II (KEEP na revisão legada, `SUPPRESS_UNTIL_EFFECTIVE`).

| Opção | A favor | Contra |
|---|---|---|
| **A) Ocultar até a vigência** | Nunca exibe lei futura como vigente. Não precisa de UI nova. O vínculo aparece sozinho na data. | Esconde uma lei que pode ser aplicada antes, por opção do ente. |
| **B) Publicar com aviso "VIGÊNCIA FUTURA"** | Mais informativo. | Depende de UI nova no aparelho, sem verificação visual. Um aviso perdido ou cortado faz a lei parecer vigente. |

**Recomendação: A, `vacatio_policy = DO_NOT_PUBLISH_AS_CURRENT`**, até existir suporte visual verificado no aparelho.

- O validador calcula `HIDDEN_UNTIL_EFFECTIVE` enquanto `as_of < effective_from`. A partir da data, publica.
- Para o vínculo legado (art. 37, II), a neutralização provisória é uma exclusão temporária: status `TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE`, a criar no motor (C3).
- Até essa mudança existir, a recomendação editorial é excluir o vínculo e reemiti-lo por addition em vacatio.
- A dívida `FUTURE_EFFECTIVE_CORRELATA_POLICY_REQUIRED` fica resolvida no plano de arquitetura e pendente de implementação.
- VACATIO sem política é rejeitado (`VACATIO_WITHOUT_POLICY`).

## Transitional

**Exemplos:**

- **Lei 9.717/1998:** faz as vezes da LC do art. 40, § 22 até a nova lei complementar (EC 103/2019, art. 9º). `revalidate_on` = nova LC.
- **LC 160/2017 × ADCT, art. 128, § 2º:** benefícios do ICMS reduzidos de 2029 a 2032; `revalidate_on` = 2033-01-01.

**Regras:**

- TRANSITIONAL sem `revalidate_on` é rejeitado (`TRANSITIONAL_WITHOUT_REVALIDATION`).
- `revalidate_on` pode ser uma data ou um evento normativo descrito. Na data ou no evento, a relação volta para revisão humana; ela não é removida automaticamente.

## Revalidações já registradas

| Relação | Quando | Motivo |
|---|---|---|
| LC 70/1991 × art. 195, I, b | 2027-01-01 | ADCT, art. 126, II: extinção da COFINS |
| LC 87/1996 (arts. 150, § 7º e 155, § 2º, XII) | 2033-01-01 | ADCT, arts. 128 a 133: extinção do ICMS |
| LC 160/2017 × ADCT, art. 128, § 2º | 2033-01-01 | fim da transição |
| PNE (Lei 15.388/2026) × art. 214 | 2036-04-14 | plano decenal |
| Lei 14.701/2023 | julgamento final dos embargos (ADC 87) | status judicial |
