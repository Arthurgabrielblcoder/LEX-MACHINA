# JURISPRUDÊNCIA — CF: Batch08 (MEDIUM; propostas aguardando ratificação)

```
BATCH = 08 · NÍVEL = MEDIUM · HOST-ONLY · NADA MATERIALIZADO · STATUS = AWAITING_USER_RATIFICATION (human_approved = false)
DECISÕES = J2_MEDIUM_BACKLOG/J2_BATCH08_DECISIONS.json · fila: pendentes 89 · HIGH 0 · MEDIUM 62 · LOW 27 · restantes no nível após o lote: 52
```

| # | Target (backlog) | Precedentes | Proposta | Alvo proposto | Tipos no aparelho | Razão |
|---|---|---|---|---|---|---|
| 1 | art. 15 | TSE SUMULA 9 | **REALLOCATE** | art. 15, III | SUMULA_TSE: novo | Súmula do TSE cuja referência é o inciso III do art. 15 (condenação criminal), e não o artigo inteiro. É o primeiro precedente de outro tribunal: o firmware exige ID "STF:" e rotula súmula como "SUMULA STF", por isso exige desenho de tipo e tribunal antes de materializar. |
| 2 | art. 62, § 6 | MS 27931 | **PROMOTE** | art. 62, § 6 | MS: novo | Precedente do Plenário que define o alcance do trancamento de pauta por MP (art. 62, § 6º). MS é tipo novo no aparelho. |
| 3 | art. 5, X | STJ SUMULA 403 | **UNRESOLVED_EXTERNAL** | — | SUMULA_STJ: novo | A fonte oficial do STJ bloqueou o acesso com um desafio anti-robô, que não foi contornado (regra de segurança). Nenhum conteúdo foi presumido. Além disso, súmula do STJ é tribunal e tipo novos no aparelho. Retomar quando houver acesso (ou com a página fornecida pelo usuário). |
| 4 | art. 53 caput | INQ 4781 | **PROMOTE** | art. 53 caput | INQ: novo | Precedente do Plenário sobre o limite da imunidade material (nexo com a função). Complementa o Tema 950 (Batch02, aprovado) no caput. Inq é tipo novo no aparelho. O mesmo acórdão trata do § 2º (flagrante), o que pode virar uma proposta separada. |
| 5 | art. 53 caput | PET 7174 | **DUPLICATE_RECOMMENDATION** | — | PET: novo | Mesma tese do Inq 4781 Ref (item anterior), que é do Plenário. Para não multiplicar vínculos iguais no caput do art. 53, prefere-se o precedente do Plenário. Não é rejeição de mérito: a Pet 7174 é correta, mas redundante. |
| 6 | art. 53, § 1 | INQ 4787 | **DUPLICATE_RECOMMENDATION** | — | INQ: novo | Mesmo julgamento e mesmo escopo do HC 232627, já ratificado no Batch02 (SAME_JUDGMENT_SAME_SCOPE). Proposta: incluir "Inq 4787" como alias no registro do HC quando o tipo HC for materializado, sem nova ficha. |
| 7 | art. 114 | ADI 3395; ADI 3684 | **REALLOCATE** | art. 114, I, art. 114, IV, art. 114, IX | ADI: ok | Do caput para os incisos que os julgados interpretam: ADI 3395 no inciso I (estatutários); ADI 3684 nos incisos I, IV e IX (sem competência penal). |
| 8 | art. 114, I | ADI 3395 | **PROMOTE** | art. 114, I | ADI: ok | Interpretação conforme do inciso I: a Justiça do Trabalho não julga causas estatutárias. É o mesmo vínculo proposto no item anterior; materializado uma única vez. |
| 9 | art. 93, XII | ADI 3085 | **REJECT_NOT_MATERIAL** | — | ADI: ok | Questão de ordem que julgou a ação prejudicada; não há tese de mérito sobre o art. 93, XII (mesma lógica do MS 34418). A ADI 3823 MC, também citada na nota, não foi verificada nesta rodada e pode ser reexaminada. |
| 10 | art. 142 | ADI 6457 | **PROMOTE** | art. 142 | ADI: ok | Julgado de 2024 que interpreta diretamente o art. 142: as Forças Armadas não exercem poder moderador e sua missão é limitada. O alerta de namespace (LC 97/99) foi conferido: a lei era o objeto, e o art. 142 o parâmetro. |

```
DUPLICATE_RECOMMENDATION = 2 · PROMOTE_RECOMMENDED = 4 · REALLOCATE_RECOMMENDED = 2 · REJECT_NOT_MATERIAL_RECOMMENDED = 1 · UNRESOLVED_EXTERNAL = 1
```

## Fontes

| Id | Página | Captura |
|---|---|---|
| T7 | Jurisprudência — HC 232627 e HC 232627 ED | `310ca610…` (2026-10-17, reuso J2D) |
| U9 | Jurisprudência — Inq 4787 AgR-QO | `54ba687b…` (2026-10-17, reuso BATCH03) |
| Y1 | Súmula-TSE n. 9 (página oficial) | `1f4b62a5…` (2026-10-17) |
| Y2 | Jurisprudência — MS 27931 | `bb990605…` (2026-10-17) |
| Y3 | STJ — pesquisa de súmulas (Súmula 403) | `9423587e…` (2026-10-17) |
| Y4 | Jurisprudência — Inq 4781 (Ref e AgRs) | `f3c01596…` (2026-10-17) |
| Y5 | Jurisprudência — Pet 7174 | `93a4c5a3…` (2026-10-17) |
| Y6 | Jurisprudência — ADI 3395 | `a5784674…` (2026-10-17) |
| Y7 | Jurisprudência — ADI 3684 | `56e72461…` (2026-10-17) |
| Y8 | Jurisprudência — ADI 3085 | `5c56a381…` (2026-10-17) |
| Y9 | Jurisprudência — ADI 6457 | `bb0fd915…` (2026-10-17) |

Detectores da Fase D: os alertas (namespace, temporal, status) estão em `decisions[].auditor_flags`. Cada alerta foi conferido com a evidência oficial antes da decisão.
