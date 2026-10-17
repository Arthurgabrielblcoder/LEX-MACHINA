# JURISPRUDÊNCIA — CF: J2A, revisão externa do primeiro lote HIGH do backlog (BATCH01)

```
MISSION = J2A (HOST-ONLY; web só para os 10 candidatos; decisões, sem materialização)
BRANCH = cf-jurisprudence-audit
DECISÕES = JURISPRUDENCE_AUDIT/J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json
GERADOR = JURISPRUDENCE_AUDIT/build_j2a_batch01.py (+ J2_HIGH_BACKLOG/j2a_batch01_review.py; 3/3 idêntico)
STATUS = AWAITING_USER_RATIFICATION (nenhuma recomendação está aprovada só porque o Claude concluiu)
J1_PHYSICAL_CLOSURE_RECORDED = PASS · HIGH_BACKLOG_RECONSTRUCTED = PASS · BATCH_SELECTED = 10/10 · BATCH_SELECTION_REPRODUCIBLE = YES
OFFICIAL_SOURCE_REVIEW = 10/10 · NAMESPACE_CHECK = 10/10 · DECISIONS_COMPLETE = 10/10
CURRENT_256_CHANGED = NO · BACKLOG_OUTSIDE_BATCH_CHANGED = NO · FROZEN_LAYERS_MODIFIED = NO · MICROSD_TOUCHED = NO · FIRMWARE_CHANGED = NO
```

## 0. Fechamento físico da J1

Está registrado em `JURISPRUDENCE_AUDIT/J1_5_DEPLOY_REPORT.md`, seção "Resultado físico":

```
J1_5_PHYSICAL_VALIDATION = 11/11 PASS · ORIGINAL_277_REVIEW_COMPLETE = YES · CURRENT_APPROVED_J_BASELINE = 256
```

Não houve freeze geral nem tag. A base de 256 vínculos (156 targets) é o `REF_PAYLOAD.IDX` instalado no cartão (`d07cb076…`) e não foi tocada.

## A. Fila HIGH reconstruída sobre a base atual (256)

**Método:** a regra do J0 foi reexecutada sobre os mesmos 8 arquivos `ENTENDA_ENGINE/derived/*/JURISPRUDENCE_LINK_RECOMMENDATIONS.json` (hash registrado em `inputs`), agora contra a base instalada de 256 vínculos.

- **Categorias:** idênticas às do J0.
- **Identificador:** `recommendation_id = J0-BL-nnn`, a posição estável no backlog do J0.

| Contagem | J0 (base 277) | Agora (base 256) |
|---|---:|---:|
| Recomendações únicas | 170 | 170 |
| `NEEDS_EXTERNAL_INGESTION` (backlog) | 148 | **148** |
| Targets do backlog | 110 | **110** |
| `ALREADY_LINKED` / `EXCLUDED` | 19 / 3 | 19 / 3 |
| **HIGH** | 40 | **42** |
| MEDIUM / LOW | 81 / 27 | 80 / 26 |

**Por que HIGH = 42.** A J1.1 removeu falsos positivos que eram a única jurisprudência dos arts. 96 e 98. Esses artigos passaram a "artigo sem jurisprudência", um dos 4 sinais da regra de prioridade do J0. Por isso duas recomendações subiram para HIGH:

- `J0-BL-072` (art. 96, III, Rcl 84738), que veio de MEDIUM;
- `J0-BL-074` (art. 98, "ADIN 3392"), que veio de LOW.

Nada foi ajustado à mão.

**Efeito no lote:** o `J0-BL-074` entrou no lote como 8º. Com a fila antiga de 40, o 10º seria o `J0-BL-166` (ADCT art. 101, ADI 7047). A revisão mostrou que o `J0-BL-074` é falso positivo (ver C).

**Dados de cada item HIGH** (`high_queue`):

- recommendation_id;
- target;
- origem (lote ENTENDA);
- texto original;
- identificadores sugeridos;
- tipo sugerido;
- motivo da prioridade;
- equivalente na base atual;
- pontuação de seleção.

## B. Seleção determinística dos 10

Critérios aplicados em ordem lexicográfica (`selection_rules`), cada um medido por um sinal objetivo:

1. **Identificador explícito:** 2 se a referência nomeia exatamente um identificador.
2. **Peso constitucional:** 2 para ADI/ADC/ADO/ADPF, Tema RG ou SV, decisões de efeito geral ou vinculante.
3. **Recorrência:** o mesmo identificador aparece em mais de uma recomendação.
4. **Especificidade:** o alvo está abaixo do nível de artigo.
5. **Baixa ambiguidade:** um único identificador.
6. **Utilidade:** o artigo não tem jurisprudência.
7. **Desempate:** `recommendation_id`.

O seletor rodou 3 vezes com saída idêntica (`BATCH_SELECTION_REPRODUCIBLE = YES`). Os 10 escolhidos vêm todos de **anotações "Vide ADI" do texto compilado do Planalto** (`CANONICAL_VIGENCY_ANNOTATION`).

## C. Resultado da revisão (fontes oficiais, `NAMESPACE_CHECK` explícito)

| # | Rec. | Target do backlog | Precedente | Namespace | Decisão | Razão curta |
|---|---|---|---|---|---|---|
| 1 | J0-BL-136 | CF art. 166, § 9º | ADI 7697 | PASS (CF) | **PROMOTE_RECOMMENDED** (provisório) | O § 9º é expressamente interpretado conforme na cautelar referendada pelo Pleno (16/08/2024); mérito pendente |
| 2 | J0-BL-137 | CF art. 166, § 11 | ADI 7697 | PASS (CF) | **PROMOTE_RECOMMENDED** (provisório) | Núcleo da tese "impositividade não absoluta" das emendas individuais; mérito pendente |
| 3 | J0-BL-080 | CF art. 100, § 9º | ADI 4425 | PASS (CF) | **REJECT_TEMPORAL_MISMATCH** | Julgou o § 9º da EC 62/2009, que não existe mais; o § 9º atual (EC 113/2021) é coberto pelas ADIs 7047/7064 |
| 4 | J0-BL-081 | CF art. 100, § 9º | ADI 7047 | PASS (CF) | **PROMOTE_RECOMMENDED** | Mérito (30/11/2023): o § 9º vigente (EC 113/21) é inconstitucional |
| 5 | J0-BL-082 | CF art. 100, § 9º | ADI 7064 | PASS (CF) | **PROMOTE_RECOMMENDED** | Mesmo julgamento conjunto; a ementa (item 28) liga o novo § 9º às ADIs 4425/4357 |
| 6 | J0-BL-084 | CF art. 100, § 12 | ADI 4425 | PASS (CF) | **PROMOTE_RECOMMENDED** | O § 12 atual é o texto julgado (poupança inconstitucional; "independentemente de sua natureza"); modulação QO 2015 |
| 7 | J0-BL-069 | CF art. 92 | ADI 3392 | PASS (CF) | **REJECT_FALSE_POSITIVE** | Anotação genérica da EC 45/2004; a ADI 3392 trata do art. 114, §§ 2º e 3º (dissídio coletivo) |
| 8 | J0-BL-074 | CF art. 98 | ADI 3392 | PASS (CF) | **REJECT_FALSE_POSITIVE** | Idem; nada sobre o art. 98 |
| 9 | J0-BL-135 | CF art. 166 | ADI 7697 | PASS (CF) | **DUPLICATE_RECOMMENDATION** | A cautelar interpreta os §§ 9º a 20, não o caput; já coberto pelos itens 1 e 2 |
| 10 | J0-BL-138 | CF art. 166-A | ADI 7697 | PASS (CF) | **PROMOTE_RECOMMENDED** (provisório) | O artigo inteiro é interpretado conforme ("emendas PIX": plano de trabalho prévio, transparência) |

```
BATCH_SIZE = 10 · PROMOTE_RECOMMENDED = 6 · REJECT_FALSE_POSITIVE = 2 · REJECT_NOT_MATERIAL = 0 · REJECT_TEMPORAL_MISMATCH = 1
ALREADY_COVERED = 0 · DUPLICATE = 1 · UNRESOLVED_EXTERNAL = 0 · HIGH_REMAINING_AFTER_BATCH = 32
```

**Controle anti-erro J1.** Em todos os 10 casos o artigo citado é da **Constituição Federal**: `NAMESPACE_CHECK = PASS` 10/10. Mesmo assim, apareceu o mesmo tipo de erro da J1 por outra via:

- **ADI 3392:** o número aparece em todos os dispositivos da EC 45, mas a ação trata de **outro dispositivo** (art. 114). Daí as 2 rejeições.
- **ADI 4425:** julgou uma **redação que não existe mais** (§ 9º da EC 62/2009). Daí a rejeição temporal.

Por isso, além do namespace, o JSON traz `target_check` (PASS / FAIL / FAIL_TEMPORAL / FAIL_GRANULARITY) e `temporal_version`.

**Recomendações de alvo:**

- **Política temporal J1.3/J1.4:** o `J0-BL-080` não vai para o § 9º atual. Um vínculo da ADI 4425 em nível de artigo, com nota temporal, cabe à recomendação `J0-BL-075` (art. 100), fora deste lote.
- **Granularidade:** o firmware não herda vínculos entre níveis (`query_keys` exatas). Por isso preferi os parágrafos que a ADI 7697 nomeia (§§ 9º e 11) ao caput do art. 166. O art. 166-A fica em nível de artigo porque a decisão nomeia o artigo inteiro.
- **ADIs 7047 e 7064:** foram julgadas em conjunto e ambas declaram o § 9º inconstitucional. Recomendo **as duas**, porque são números distintos e pesquisáveis, a mesma lógica do KEEP_BOTH 367/387. Se preferir, a ratificação pode consolidar em uma só.

**Provisórios:** os itens 1, 2 e 10 vêm de **medida cautelar referendada** pelo Pleno, com mérito pendente: o processo estava concluso ao relator em 16/06/2026. Se forem aprovados, cada vínculo precisa:

- trazer o status "medida cautelar referendada — mérito pendente";
- ser revalidado quando o mérito for julgado.

O campo `confidence` separa a confiança na identidade/alvo (HIGH) da estabilidade do entendimento (MEDIUM).

## D. Limitação para a materialização (J2B)

O aparelho resolve cada vínculo de jurisprudência pela chave no `JURISPRUDENCIA.IDX` legado (`f85108ba…`). Esse índice tem **só Temas de RG (284) e SVs (12), nenhuma ADI**.

Por isso, os 6 `PROMOTE_RECOMMENDED`, todos ADIs, **não podem** ser materializados só com o `REF_PAYLOAD`. A J2B precisa definir um tipo de registro e um arquivo de conteúdo para controle concentrado (título, dispositivo do julgado, status, nota temporal ou provisória). Isso deve ser feito no formato que o firmware atual já lê, ou com um teste físico próprio. Antes disso, nenhum desses vínculos aparece no aparelho.

## E. Fontes (todas TIER A; consulta em 2026-10-16)

| Id | Órgão | Página | Captura |
|---|---|---|---|
| P1 | Planalto | CF compilada (`constituicao.htm`) | bytes `51ac764a…` (download direto) |
| S1 | STF | Jurisprudência: acórdão ADI 3423 (mesmo sentido: ADI 3392) | texto renderizado `e34505f3…` |
| S2 | STF | Portal: ADI 3392, aba Informações | texto renderizado `ba74c40c…` |
| S3 | STF | Jurisprudência: ADI 4425 (mérito, QO, ED) | texto renderizado `ac1ee1c7…` |
| S4 | STF | Jurisprudência: acórdão ADI 7064 | texto renderizado `4d1e398d…` |
| S5 | STF | Portal: ADI 7047, aba Decisões | texto renderizado `d63a0050…` |
| S6 | STF | Portal: ADI 7064, aba Decisões | texto renderizado `b71b5b66…` |
| S7 | STF | Portal: ADI 7697, aba Decisões | texto renderizado `2d68ff18…` |

**Como as páginas foram capturadas:**

- O `portal.stf.jus.br` responde 403 a clientes automáticos. As páginas do STF foram lidas no navegador embutido, como na J1.3, e o sha256 é do texto renderizado.
- O Planalto foi baixado direto. O hash difere do da J1.3 (`a87c9479…`) porque a página é atualizada.
- As URLs completas, as datas e a razão de cada fonte estão em `J2A_BATCH01_DECISIONS.json` → `sources`.
- Não foram usados blogs, agregadores, cursinhos nem snippets.

## F. Testes

`JURISPRUDENCE_AUDIT/tests/test_j2a.py`, 5 testes:

- gerador `UP_TO_DATE`;
- seleção 3/3 idêntica;
- exatamente 10, todos HIGH, únicos e `NEEDS_EXTERNAL_INGESTION` (nenhum excluded ou already linked);
- decisões completas, com schema, fontes Tier A com hash, e `PROMOTE` só com alvo verificado;
- base de 256 inalterada (hash instalado, RUN7, pacote J1.4) e entradas do backlog inalteradas.

Junto com J1.1, J1.3 e J1.4: **30/30 OK**.

```
NEXT_RECOMMENDED_MISSION = J2B — RATIFICAÇÃO DO BATCH01 + desenho do registro de ADI para o aparelho (antes de materializar)
                           ou J2A_BATCH02 (próximos 10 HIGH; restam 32)
```
