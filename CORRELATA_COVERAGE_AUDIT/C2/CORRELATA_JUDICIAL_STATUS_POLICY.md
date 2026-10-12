# C2 — Status judicial nas CORRELATAs

**Objetivo:** permitir um aviso curto e auditável quando a norma correlata foi atingida por controle de constitucionalidade. **Não duplica a
camada de jurisprudência.** O aviso não substitui a leitura do acórdão.

## Estrutura mínima (`judicial_status`)

| Campo | Obrigatório | Conteúdo |
|---|---|---|
| `status` | sim | ver tabela abaixo |
| `cases` | sim | lista de ações (ex.: `ADC 87`, `ADI 7582`) |
| `decided_on` | sim | data do julgamento de mérito (AAAA-MM-DD) |
| `notice_short` | sim | aviso para o aparelho, até 80 caracteres |
| `checked_until` | sim | data até a qual o status foi conferido em fonte oficial |
| `affected_provisions` | não | dispositivos declarados inconstitucionais |
| `interpretation_conforme` | não | dispositivos com interpretação conforme |
| `pending` | não | recursos pendentes |
| `revalidate_on_final_ed` | não | `true` quando há embargos pendentes |

| `status` | Uso |
|---|---|
| STF_PARTIAL_UNCONSTITUTIONALITY | inconstitucionalidade parcial |
| STF_INTERPRETATION_CONFORME | só interpretação conforme |
| STF_SUSPENDED_INJUNCTION | cautelar suspendendo dispositivos |
| STF_PARTIAL_EFFECTS | modulação ou efeitos parciais |
| PENDING_JUDICIAL_REVALIDATION | revalidação judicial futura conhecida |

## Regras

- `temporal_status = PARTIAL_EFFECTS` ou a flag `JUDICIAL_RESTRICTIONS` exigem `judicial_status` completo, e a flag é obrigatória.
- Faltando qualquer um desses requisitos, o registro é rejeitado com `JUDICIAL_RESTRICTIONS_INCOMPLETE`.
- O aparelho exibe `notice_short` junto do vínculo (`PUBLISH_WITH_JUDICIAL_NOTICE`). O texto original da lei não é apresentado como integralmente vigente.
- Quando `revalidate_on_final_ed = true`, a relação volta para revisão humana após o julgamento final dos embargos.
- `checked_until` torna explícita a data da última conferência.

## Caso de teste: Lei 14.701/2023

- **Fonte:** portal do STF, ADC 87 (incidente 6824155), abas Decisões e Andamentos, consulta única em 2026-10-11 com sha256 registrado no consolidado HIGH.
- **Mérito (2025-12-19):** procedência parcial na ADC 87 e nas ADIs 7582, 7583 e 7586.
  - **Inconstitucionais:** a expressão "na data da promulgação da Constituição Federal" do caput do art. 4º e os §§ 2º a 4º do art. 4º; os §§ 1º e 2º do art. 9º; os arts. 10 e 13; o parágrafo único do art. 20.
  - **Interpretação conforme:** arts. 5º, 6º, 14, 18, §§ 1º e 2º, 20, caput, e 22, entre outros.
- **Embargos:** os segundos embargos de declaração estão em sessão virtual, com vista ao Min. Dias Toffoli desde 19/08/2026. O último andamento é de 02/09/2026, e não há julgamento final até 2026-10-11.
- **Decisões HIGH:**
  - § 1º: ADJUST, REGULAMENTA, PARTIAL_EFFECTS, JUDICIAL_RESTRICTIONS e NON_EXCLUSIVE;
  - § 6º: ADJUST, COMPLEMENTA, ESCOPO_PARCIAL e `DOES_NOT_IMPLEMENT_COMPLEMENTARY_LAW_EXCEPTION`;
  - § 3º: REJECT (`CROSS_REFERENCE_ONLY`).
- **Aviso proposto:** "STF: inconstitucionalidade parcial (ADC 87). Embargos pendentes."
