# JURISPRUDÊNCIA — CF: J1.3, fechamento da revisão dos 277 vínculos originais

```
MISSION = J1.3 (HOST-ONLY; web só para os 4 casos externos e o par redundante; sem materialização)
BRANCH = cf-jurisprudence-audit (base d873037)
DECISÕES = JURISPRUDENCE_AUDIT/J1_3_DECISIONS.json (gerador build_j1_3_external_review.py, 3/3 idêntico)
AUTORIDADE = revisão em fontes oficiais (Claude), PENDENTE DE RATIFICAÇÃO HUMANA
J1_2_PHYSICAL_TEST = 10/10 PASS · BACKLOG_148_TOUCHED = NO · DEVICE_DATA_CHANGED = NO · MICROSD_TOUCHED = NO · FIRMWARE_CHANGED = NO
```

## 1. Teste físico J1.2 (registrado)

`J1_CLEANUP_PHYSICAL_VALIDATION = PASS` (10/10, relatado por Arthur em 2026-10-16). Os 10 itens estão em `J1_2_DEPLOY_REPORT.md`, seção "Resultado físico".

## 2. Os 4 casos `EXTERNAL_REVIEW_REQUIRED` (4/4 identificados e revisados)

| # | Vínculo atual | Precedente | Dúvida | Decisão | Destino potencial |
|---|---|---|---|---|---|
| 1 | CF art. 100, § 1º | **SV 17** | O "período do § 1º" do enunciado é o § 1º atual? | `REALLOCATE_RECOMMENDED` | CF art. 100, **§ 5º** |
| 2 | CF art. 100, § 1º | **Tema 147** (RE 591085) | Idem (o Tema 147 deu origem à SV 17) | `REALLOCATE_RECOMMENDED` | CF art. 100, **§ 5º** |
| 3 | CF art. 40, § 4º | **Tema 594** (RE 627294) | A tese sobre a redação **originária** pode ficar no § 4º atual? | `REALLOCATE_RECOMMENDED` | CF **art. 40** (artigo), com nota "redação originária" |
| 4 | CF art. 40, § 5º | **Tema 594** | Idem, para o § 5º | `REALLOCATE_RECOMMENDED` | mesmo destino (um único vínculo) |

**Fundamentos**, todos com confiança ALTA:

- **Casos 1 e 2.**
  - **Tema 1037** (STF): diz expressamente que a EC 62/2009 não afetou a SV 17 e que o período sem juros é o do **§ 5º** do art. 100.
  - **Página oficial da SV 17:** associa ao enunciado as teses dos Temas 1037 e 1335, ambas referidas ao § 5º.
  - **Texto compilado do Planalto:** o § 1º originário era a inclusão orçamentária com pagamento até o fim do exercício seguinte, conteúdo hoje no § 5º. O § 1º atual define débitos alimentícios.
  - **Conclusão:** o vínculo está no parágrafo errado. O § 5º **já exibe** os Temas 1037 e 1335.
- **Casos 3 e 4.**
  - **Página oficial do Tema 594:** o objeto são os "§§ 4º e 5º do art. 40 (redação originária)".
  - **Planalto:** o § 4º originário era a revisão paritária de proventos e o § 5º originário a pensão integral. Os §§ 4º e 5º atuais tratam de vedação a critérios diferenciados e da redução de idade do professor.
  - **Conclusão:** nenhum parágrafo atual tem o conteúdo original. O destino possível é o art. 40, com nota temporal.

`REALLOCATE_RECOMMENDED` = remover o vínculo atual, cujo alvo está errado. O vínculo no destino **não foi criado** e depende de decisão separada.

`KEEP_CONFIRMED` 0 · `REMOVE_FALSE_POSITIVE` 0 · `REALLOCATE_RECOMMENDED` **4** · `UNRESOLVED_EXTERNAL` **0**.

## 3. Caso redundante: `KEEP_BOTH`

O par é Tema 367 × Tema 387 → CF art. 16. A tese é textualmente idêntica (LC 135/2010 inaplicável às eleições de 2010, art. 16), mas os temas são **distintos**:

| | Tema 367 | Tema 387 |
|---|---|---|
| Leading case | RE 631102 (paradigma substituído pelo RE 630147) | RE 633703 |
| Relator | Joaquim Barbosa | Gilmar Mendes |
| Objeto | Inelegibilidade por renúncia (LC 64/90, art. 1º, I, k) | Aplicabilidade da LC 135/2010 às eleições de 2010 |

Não houve julgamento conjunto. O modelo publica um vínculo por precedente, e consolidar apagaria um número de tema que o usuário pode procurar. **Os dois ficam.**

## 4. Fontes (todas TIER A)

| Id | Órgão | Página | Captura |
|---|---|---|---|
| S1 | STF | Tema 1037 (RE 1169289) | DOM `f7bedbe6…` |
| S2 | STF | Súmula Vinculante 17 | DOM `2483c8f0…` |
| S3 | STF | Tema 147 (RE 591085) | DOM `fff81faf…` |
| S4 | STF | Tema 594 (RE 627294) | DOM `39a2d3c5…` |
| S5 | Planalto | CF compilada (`constituicao.htm`) | bytes `a87c9479…` |
| S6 | STF | Tema 387 (RE 633703) | DOM `a38c5686…` |
| S7 | STF | Tema 367 (RE 631102) | DOM `f9ec041e…` |

**Como as páginas foram capturadas:**

- O `portal.stf.jus.br` responde HTTP 403 a clientes automáticos (limitação já registrada na J2). Por isso as páginas do STF foram lidas no navegador embutido, e o sha256 é do texto renderizado. Esse é o precedente "fotografia por navegador" da J2.
- O Planalto foi baixado diretamente.
- As URLs completas, os trechos parafraseados e o motivo de cada consulta estão em `J1_3_DECISIONS.json` → `sources`.
- Não foram usados blogs, resumos nem snippets como prova.

## 5. Reconciliação do conjunto original

| Etapa | Vínculos |
|---|---:|
| Original | 277 |
| Removidos na J1.1 (ratificados; validados fisicamente) | −20 |
| No aparelho hoje | **257** |
| Remoções propostas na J1.3 (realocações) | −4 |
| **`PROPOSED_FINAL_ORIGINAL_SET_RELATIONS`** | **253** |

**Composição da revisão:**

- `HUMAN_REVIEWED_SIGNAL_RELATIONS` = 86;
- `NO_SIGNAL_STRUCTURAL_CONTROL_RELATIONS` = 191 (`NO_SIGNAL_CONTROL = PASS`, não reaberto);
- `UNRESOLVED_RELATIONS` = **0**.

**Efeito de uma futura materialização:**

- **CF art. 100, § 1º:** perde o último vínculo J, então a flag J mudaria.
- **CF art. 40, §§ 4º e 5º:** mantêm jurisprudência (Temas 727, 888, 942 e 965).
- **Realocações, se aprovadas depois:** criariam até 3 vínculos: SV 17 e Tema 147 → art. 100, § 5º; Tema 594 → art. 40.

## 6. Fechamento

```
ORIGINAL_277_REVIEW_COMPLETE = YES
```

O status YES se apoia em cinco condições cumpridas:

- 20 falsos positivos removidos e validados fisicamente;
- 4 casos externos decididos com fonte oficial;
- redundância decidida;
- 191 vínculos sem sinal controlados;
- nenhum `UNRESOLVED_EXTERNAL`.

**Condição:** as 4 decisões ainda precisam da sua ratificação antes da materialização.

```
NEXT_RECOMMENDED_MISSION = J1.4 — MATERIALIZAR DECISÕES FINAIS (remover os 4 vínculos de alvo errado; realocação só se aprovada como decisão própria)
```
