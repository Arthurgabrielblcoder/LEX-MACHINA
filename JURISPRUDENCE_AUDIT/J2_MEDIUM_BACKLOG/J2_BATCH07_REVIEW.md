# JURISPRUDÊNCIA — CF: Batch07 (MEDIUM; propostas aguardando ratificação)

```
BATCH = 07 · NÍVEL = MEDIUM · HOST-ONLY · NADA MATERIALIZADO · STATUS = AWAITING_USER_RATIFICATION (human_approved = false)
DECISÕES = J2_MEDIUM_BACKLOG/J2_BATCH07_DECISIONS.json · fila: pendentes 99 · HIGH 0 · MEDIUM 72 · LOW 27 · restantes no nível após o lote: 62
```

| # | Target (backlog) | Precedentes | Proposta | Alvo proposto | Tipos no aparelho | Razão |
|---|---|---|---|---|---|---|
| 1 | art. 7, XXVI | RG 1046 | **PROMOTE** | art. 7, XXVI | RG: ok | Tese central sobre o reconhecimento das convenções e acordos coletivos (art. 7º, XXVI): o negociado prevalece, respeitados os direitos absolutamente indisponíveis. |
| 2 | art. 21, XVI | ADI 2404 | **PROMOTE** | art. 21, XVI | ADI: ok | Interpreta diretamente o art. 21, XVI: a classificação indicativa é informativa e não autoriza censura nem condiciona a exibição. O alerta de namespace (Lei 8.069) foi conferido: a lei era o objeto e o parâmetro é a CF. |
| 3 | art. 63 | ADI 3114 | **PROMOTE** | art. 63 | ADI: ok | Firma os dois limites do poder de emenda: pertinência temática e não aumento de despesa. Como a pertinência não está só no inciso I, o alvo em nível de artigo (art. 63) é o adequado. |
| 4 | art. 63 | ADI 2681 | **REALLOCATE** | art. 63, I | ADI: ok | A recomendação citava a MC; o mérito (2018) a substituiu e decide especificamente o inciso I do art. 63, onde o Tema 686 já está instalado. |
| 5 | art. 63 | RG 686 | **ALREADY_COVERED** | — | RG: ok | O Tema 686 já está instalado no dispositivo exato (CF88:ART.63:INC.I, base de 261). Vincular de novo no art. 63 duplicaria a ficha. |
| 6 | art. 100 | ADI 4425 | **PROMOTE** | art. 100 | ADI: ok | Mesma política do Tema 558 (J2B.1) e do Tema 594: as partes históricas do julgado ficam no art. 100, com nota temporal. Confiança MEDIUM porque é decisão editorial: o essencial vigente (§ 12) já está coberto, e o vínculo no artigo serve à história do regime de precatórios. Sem a nota, recomenda-se não vincular. |
| 7 | art. 5, LVII | RG 1068 | **REALLOCATE** | art. 5, XXXVIII | RG: ok | A tese se apoia na soberania dos veredictos (art. 5º, XXXVIII, c). Pôr no inciso LVII sugeriria uma tese sobre presunção de inocência que o tema não fixa diretamente. Realocar para o inciso XXXVIII, que já tem o Tema 154. |
| 8 | art. 5, LXVII | SV 25 | **PROMOTE** | art. 5, LXVII | SV: ok | Informação indispensável no próprio inciso LXVII: o texto ainda prevê a prisão do depositário infiel, mas ela é ilícita. Usar o enunciado oficial atual ("do depósito"); o corpus arquivado dizia "de depósito". |
| 9 | art. 8, IV | RG 935 | **REALLOCATE** | art. 7, XXVI | RG: ok | O art. 8º, IV trata da contribuição confederativa (SV 40, já instalada ali). A assistencial do Tema 935 é instituída por acordo ou convenção coletiva, por isso a base oficial inclui o art. 7º, XXVI. Confiança MEDIUM porque a página não registra trânsito. Revalidar antes de materializar. |
| 10 | art. 14, § 5 | RG 1229 | **PROMOTE** | art. 14, § 5 | RG: ok | Tese específica sobre a contagem de mandato para a reeleição do art. 14, § 5º. Convive com os Temas 172 e 564 já instalados no parágrafo. |

```
ALREADY_COVERED = 1 · PROMOTE_RECOMMENDED = 6 · REALLOCATE_RECOMMENDED = 3
```

## Fontes

| Id | Página | Captura |
|---|---|---|
| P1 | Constituição Federal — texto compilado (com redações anteriores e anotações "Vide ADI") | `51ac764a…` (2026-10-16, reuso J2A) |
| S3 | Jurisprudência — acórdãos ADI 4425 (mérito, QO de modulação, ED) | `ac1ee1c7…` (2026-10-16, reuso J2A) |
| X1 | Repercussão Geral — Tema 1046 | `3a6f389f…` (2026-10-17) |
| X2 | Jurisprudência — ADI 2404 | `8ec3defd…` (2026-10-17) |
| X3 | Jurisprudência — ADI 3114 | `ab59b149…` (2026-10-17) |
| X4 | Jurisprudência — ADI 2681 (mérito e MC) | `469317de…` (2026-10-17) |
| X5 | Repercussão Geral — Tema 686 | `feb96f9f…` (2026-10-17) |
| X6 | Repercussão Geral — Tema 1068 | `425be9b4…` (2026-10-17) |
| X7 | Súmula Vinculante 25 (página oficial) | `18e25eda…` (2026-10-17) |
| X8 | Repercussão Geral — Tema 935 | `2f34046b…` (2026-10-17) |
| X9 | Repercussão Geral — Tema 1229 | `bfc776c2…` (2026-10-17) |

Detectores da Fase D: os alertas (namespace, temporal, status) estão em `decisions[].auditor_flags`. Cada alerta foi conferido com a evidência oficial antes da decisão.
