# ENTENDA-T1 — Padrão editorial

**ENTENDA_T1_STATUS = APPROVED** · aprovado em 2026-09-28 por revisão humana ("APROVADO COM AJUSTES") do piloto CF88 · adendo A3 (BLOCK formal, resolução por cobertura, lint por seção) na seção 13.

Este padrão vale para todas as normas do acervo. O piloto foi a Constituição.

O validador (`entenda_engine.validate_explanation` e `validate_corpus`) aplica automaticamente tudo o que este documento marca como **[BLOQUEIA]**. O que está marcado como **[AVISA]** só aparece como aviso de lint (`entenda_engine.lint`), para o revisor humano decidir. O código nunca reescreve conteúdo com base no lint.

---

## 1. Natureza da camada

- O ENTENDA é uma **explicação editorial derivada** do texto oficial.
  - Não é Lei Seca, Jurisprudência, Referências nem Correlatas.
  - Todas essas camadas usam a mesma chave: o `target_id` canônico (`LEGAL_TARGET_ID`).
- **A Lei Seca fica intacta.** A explicação guarda apenas uma cópia (snapshot) do texto oficial e o hash dela, para detectar mudanças. Essa cópia nunca é exibida como texto oficial.
- **`usage_policy = EDITORIAL_OUTPUT_ONLY`** **[BLOQUEIA]**. O ENTENDA nunca alimenta Correlatas, Jurisprudência, Referências ou o relations engine. Há teste automático para isso.
- **Referências.** O ENTENDA pode informar quantos vínculos existem para o target (`reference_count`). Não incorpora o conteúdo deles.

## 2. As cinco seções

| # | Seção | Campo | Regra |
|---|---|---|---|
| 1 | O QUE DIZ | `o_que_diz` | Obrigatória. Resumo fiel e curto do comando normativo. Não copia a Lei Seca. |
| 2 | O QUE SIGNIFICA | `o_que_significa` | Obrigatória. Português claro para quem estuda Direito. Sem infantilizar e sem trocar precisão por analogia vaga. |
| 3 | EXEMPLO PRÁTICO | `exemplo_pratico` | Obrigatória. Caso hipotético concreto (ver seção 6). |
| 4 | ATENÇÃO | `atencao` | Opcional (`null`). Só quando há ponto de confusão relevante: exceção, limite, condição, dependência do dispositivo-pai ou erro comum. |
| 5 | PALAVRAS DIFÍCEIS | `palavras_dificeis` | De 0 a 5 pares `termo` / `explicação` (ver seção 7). |

Tamanho **[BLOQUEIA]**:

- visão geral (OVERVIEW): 120 a 560 palavras;
- demais papéis: 80 a 400 palavras;
- payload: no máximo 6144 bytes.

Quando a explicação passa de 85% do limite, o lint **[AVISA]** `LONG_EXPLANATION`.

Nenhuma linha de conteúdo pode começar com `#` ou `@`, e o caractere `|` não pode aparecer **[BLOQUEIA]**. Esses caracteres são reservados ao formato do SD.

## 3. Granularidade: qual target recebe explicação

A unidade é escolhida editorialmente, por sentido. Nenhuma explicação é gerada automaticamente para todo target estrutural. Cada registro justifica a escolha em `editorial_reason` **[BLOQUEIA se vazio]**.

| Papel | Tipo de target | Uso | Autonomia |
|---|---|---|---|
| OVERVIEW | ARTIGO | Visão geral e estrutura do artigo. Situa as subdivisões sem repetir as explicações próprias delas. | AUTONOMOUS |
| DEVICE | CAPUT, PARÁGRAFO | Dispositivo com comando completo | declarada pelo editor |
| BLOCK | PARÁGRAFO, INCISO | Enunciado com enumeração (target que tem filhos) **ou** conjunto de irmãos com forte unidade de sentido, declarado em `covered_targets` | declarada (inciso: DEPENDENT) |
| ITEM | INCISO, ALÍNEA | Item com alcance próprio | sempre DEPENDENT_ON_PARENT |
| NO_SEPARATE_EXPLANATION | qualquer | Registrado apenas no relatório de seleção. Não gera explicação: o dispositivo é coberto pelo artigo ou por um bloco. | — |

**Quando criar explicação própria.** Quando pelo menos uma destas condições for verdadeira:

1. o dispositivo contém regra juridicamente autônoma;
2. é um bloco com comando e enumeração;
3. tem alta utilidade interpretativa independente;
4. perde significado se resumido apenas na visão geral;
5. traz conceitos próprios relevantes para estudo;
6. exige contexto específico que a visão geral não explica bem.

**Quando marcar NO_SEPARATE_EXPLANATION.** Quando o dispositivo:

- é fragmento inseparável do pai;
- teria uma explicação que repetiria praticamente todo o pai;
- é bem explicado em bloco com os irmãos.

Regras complementares:

- **Caput.** Só recebe explicação própria quando o artigo tem parágrafos e o caput traz comando distinto da visão geral. Nos demais casos, a unidade é o ARTIGO.
- **`covered_targets`** **[BLOQUEIA]**:
  - só com o papel BLOCK;
  - apenas irmãos estruturais **reais** do target principal (mesmo pai) e CURRENT;
  - um dispositivo coberto não pode ter explicação própria;
  - um dispositivo não pode ser coberto por dois blocos;
  - nunca se inventa `target_id` para representar um bloco.
- **Lookup de dispositivo coberto.** No índice, o dispositivo coberto aponta para o bloco com a marcação `MATCH=COVERED`. É uma associação editorial explícita, não herança estrutural.
- **Não elegíveis:** NORMA e NAMESPACE.

## 4. Pai e contexto

- **`context_targets`** é a cadeia estrutural completa, do artigo até o pai direto, e o validador a exige exatamente assim **[BLOQUEIA]**. Por exemplo, `CF88:ART.60:PAR.4:INC.IV` → `[CF88:ART.60, CF88:ART.60:PAR.4]`.
- **Sem herança automática.** `get_explanation(filho)` nunca devolve a explicação do pai. O firmware pode oferecer links de navegação para o contexto, sem mesclar conteúdo.
- **Complementaridade.** A explicação do filho complementa a do pai e não pode copiá-la.
  - **[BLOQUEIA]:** frase de 8 ou mais palavras repetida entre pai e filho, ou similaridade acima de 0,35 em uma seção.
  - **[AVISA]:** `PARENT_REPETITION` quando a similaridade passa de 0,20.
- **Dispositivo dependente não finge autonomia.** A explicação de um inciso ou alínea deve dizer como ele se liga ao enunciado do pai.

## 5. Lei Seca × explicação × jurisprudência

- **Cópia da Lei Seca.** A explicação não copia a Lei Seca.
  - **[BLOQUEIA]:** mais de 10 palavras seguidas iguais ao texto oficial.
  - **[AVISA]:** `NEAR_COPY_OF_OFFICIAL_TEXT` a partir de 8 palavras seguidas. É admissível para listas e nomes técnicos curtos.
- **Texto × interpretação.** O que o texto diz é separado do que é interpretação. Quando o alcance de um dispositivo depende de interpretação, a explicação diz isso expressamente e não apresenta o alcance doutrinário ou jurisprudencial como texto literal.
  - Exemplo aprovado: "O inciso não restringe expressamente essa proteção ao art. 5º. A definição de quais direitos fora dele também são abrangidos é questão de interpretação constitucional."
- **Jurisprudência não entra no corpo** **[BLOQUEIA]** (`ENTENDA_EXTERNAL_CASE_CONTENT`). Isso inclui:
  - siglas de tribunais: STF, STJ, TST, TSE, TCU;
  - "Súmula", "Tema nº", ADI, ADPF, ADC, ADO, RE, REsp, HC com número;
  - "decidiu" e "pacificou".
  
  Menções genéricas como "jurisprudência" e "tribunais" no corpo geram **[AVISA]** (`JURISPRUDENCE_WORDING_IN_BODY`).
- **Camada externa.** O que depende de jurisprudência ou doutrina vai em `external_layer_notes`, como apontamento para a camada externa, sem afirmar o conteúdo de decisões.
- **Afirmações absolutas.** Não se afirma que algo é absoluto quando não é. Palavras como "sempre", "nunca", "jamais", "absoluto", "automaticamente" e "sem exceção" geram **[AVISA]** `ABSOLUTE_CLAIM`. O revisor confirma se a afirmação é literal do texto.
- **O que a explicação evita:** opinião, aconselhamento jurídico personalizado e linguagem infantil.

## 6. Exemplos

- O exemplo é um caso hipotético concreto que **ilustra** a regra. Não cria requisito, condição ou exceção que o texto não traz.
  - Caso aprovado na revisão: o exemplo da estabilidade da gestante não pode partir da comunicação da gravidez ao empregador, porque isso sugeriria um requisito que o texto não traz.
- Quando o dispositivo não se presta a um exemplo cotidiano, usa-se uma situação institucional ou processual.
- Frases do exemplo com "deve", "precisa", "exige", "só se" ou "desde que" geram **[AVISA]** `EXAMPLE_REQUIREMENT_LANGUAGE`. O revisor confirma que a exigência está no texto.

## 7. Palavras difíceis

- Só termos realmente úteis para entender o dispositivo, em formato curto.
- A definição não deve criar falsa ideia jurídica.
  - Caso aprovado: "bem de uso comum do povo" passou a ser definido como bem destinado à fruição e à proteção de todos, e não como propriedade da coletividade.
- **[AVISA]** `TERM_NOT_USED` quando o termo não aparece na explicação nem no texto oficial, e `TERM_LOW_UTILITY` quando a definição tem menos de 25 caracteres.
- A lista poderá alimentar o futuro DICIONÁRIO. Esse motor ainda não existe.

## 8. Vigência: CURRENT, HISTORICAL e UNKNOWN

| Status | Regra |
|---|---|
| CURRENT | Gera explicação. É a prioridade do produto. |
| HISTORICAL | Não gera explicação **[BLOQUEIA]** (`allow_historical=false`). Na produção, um dispositivo histórico vai para a lista `excluded_historical` da seleção. |
| UNKNOWN | Só com `validity_note` **[BLOQUEIA]** e revisão humana. |
| UNKNOWN + `external_verification` | `status=CURRENT_OFFICIAL_EXTERNAL_VERIFICATION`, `current_in_operational_source=false`, `current_official_external=true`, `verified_on`, `evidence[]`, `content_hash_stored=false` (nenhum hash web inventado). O status exibido passa a ser `CURRENT_OFFICIAL_EXTERNAL`. |

Um ARTIGO (estrutural) herda o status da subárvore: CURRENT se houver algum dispositivo CURRENT; senão UNKNOWN, se houver algum UNKNOWN; senão HISTORICAL.

## 9. Desatualização (STALE)

- **O que se guarda.** `source_text_snapshot` é o texto oficial atual da subárvore do target, mais as subárvores dos `covered_targets` (`snapshot_scope`). Guardam-se também `source_text_sha256` e o hash do texto próprio de cada `context_target`.
- **Estados** (`check_stale()`): FRESH, STALE_TEXT_CHANGED, STALE_CONTEXT_CHANGED, ORPHANED_TARGET ou NO_EXPLANATION.
- **Como o estado chega ao usuário.** O build leva a desatualização para o lookup e para o payload (`F|…`). Uma explicação desatualizada nunca continua silenciosamente válida.
- **Stamp.** Um registro já carimbado mantém o hash original.

## 10. Revisão humana

`review_status` pode ser:

| Valor | Significado |
|---|---|
| DRAFT | rascunho |
| PENDING_HUMAN_REVIEW | aguardando revisão; é o estado de toda explicação nova |
| HUMAN_APPROVED_T1 | aprovada por humano segundo este padrão |
| CHANGES_REQUESTED | versão com ajuste pedido e já substituída |
| APPROVED | aprovada |
| REJECTED | rejeitada |

Regras:

- Explicações novas entram sempre como PENDING_HUMAN_REVIEW. Aprovadas e pendentes não se misturam no mesmo lote sem marcação.
- A revisão é registrada com `human_review` no registro e num diff (`target_id`, `before`, `after`, `reason`, `human_review=true`), por exemplo `derived/CF88_PILOT_HUMAN_REVIEW_DIFF.json`.
- O rascunho original é preservado; não é sobrescrito.

## 11. Versionamento editorial

- **`explanation_id`:** `ENTENDA/<target_id>/<VARIANTE>/<editorial_version>`. A chave estável entre versões é `explanation_key` (`ENTENDA/<target_id>/<VARIANTE>`).
- **Mudança de conteúdo exige nova versão** **[BLOQUEIA]** (`ENTENDA_CONTENT_CHANGED_WITHOUT_VERSION_BUMP`).
- **Versões anteriores ficam como evidência.** Elas continuam no corpus com `status=RETIRED` e `superseded_by`; nunca são apagadas.
- **Unicidade.** Só uma versão ACTIVE por chave **[BLOQUEIA]**, e `explanation_id` duplicado é recusado **[BLOQUEIA]**.
- **Versões de template e guia.** `template_version` (ENTENDA-T1) e `prompt_version` (guia editorial) ficam registrados em cada explicação.
- **`generated_at`.** É apenas metadado operacional e não entra no build, que é determinístico (BYTE_IDENTICAL).

## 12. Armazenamento

| Onde | Arquivo |
|---|---|
| Fonte editorial canônica | `ENTENDA_ENGINE/corpus/<NORMA>.entenda.jsonl`, uma linha por versão de explicação |
| Rascunhos legíveis | `ENTENDA_ENGINE/editorial/*.json` |
| SD (por norma) | `ENTENDA_LOOKUP.IDX`: `TARGET_ID\|OFFSET\|BYTES\|EXPLANATION_ID\|VALIDITY\|FRESHNESS\|REVIEW\|MATCH`, ordenado em ASCII |
| SD (por norma) | `ENTENDA_PAYLOAD.DAT`: blocos com `@ID`, linhas `T K V R F H C B N W`, as seções `#…` e `@END` |

---

## 13. Adendo A3 (2026-09-28): BLOCK formal, resolução e lint por seção

O conteúdo editorial do T1 não muda. Mudam o comportamento do BLOCK na consulta e o lint.

### BLOCK formal

Toda explicação com `covered_targets` grava os seguintes campos:

| Campo | Conteúdo |
|---|---|
| `anchor_target_id` | o target real que ancora a explicação |
| `covered_targets[]` | os irmãos cobertos |
| `coverage_type` | `BLOCK` |
| `display_targets[]` | âncora e cobertos, em ordem estrutural |
| `display_topic` (opcional) | tema editorial |

O `display_title` é gerado a partir desses metadados, sem valores fixos no código. Exemplo: "Art. 5º, incisos IV, V, IX e XIV — Liberdade de expressão e informação". Ele vai no payload na linha `D|`, e a linha `X|` leva os `display_targets`.

Validações:

- **Âncora** **[BLOQUEIA]:** a âncora deve ser o próprio target.
- **`display_targets`** **[BLOQUEIA]:** deve coincidir com a ordem estrutural.
- **`coverage_type`** **[BLOQUEIA]:** só pode existir quando há `covered_targets`.

### Resolução (botão ENTENDA)

`resolve_explanation(target_id)` e `lookup_idx` devolvem:

| Situação | `resolution_type` | Demais campos |
|---|---|---|
| O target tem explicação própria | `DIRECT` | `matched_target_id` = `anchor_target_id` = o target |
| O target está em `covered_targets` de um bloco | `COVERED_BY_BLOCK` | payload do bloco, `matched_target_id` = o target pedido, `anchor_target_id` = a âncora |

- Um dispositivo coberto nunca aparece como "sem ENTENDA".
- Não há herança estrutural: só a cobertura editorial explícita resolve.
- `get_explanation()` continua devolvendo apenas o target exato.
- O índice passa a ter a coluna `RESOLUTION` (`DIRECT` ou `COVERED_BY_BLOCK`).

### Lint e jurisprudência

- **Palavras jurídicas comuns** como "tribunal", "juiz" e "jurisdição" não são jurisprudência.
- **O que conta como referência jurisprudencial:**
  - no corpo, gera aviso `JURISPRUDENCE_WORDING_IN_BODY`: STF, STJ, TST, TSE, Súmula e Súmula Vinculante, Tema nº, Repercussão Geral, jurisprudência e precedente;
  - no corpo, bloqueia (`ENTENDA_EXTERNAL_CASE_CONTENT`): siglas de tribunais, Súmula, Tema nº e números de processo.
- **CAMADA EXTERNA** (`external_layer_notes`) pode citar essas referências sem falhar.
- **"Maioria absoluta"** é termo técnico e não gera `ABSOLUTE_CLAIM`.

### Revisão de lote e recomendações jurisprudenciais

- **Revisão de lote** (`apply_batch_review.py`):
  - uma decisão por explicação (`APPROVED` ou `APPROVED_AFTER_ADJUSTMENT`), com `review_reason` e `changed_sections[]`;
  - os textos originais ficam preservados em `HUMAN_REVIEW_DECISIONS.json`;
  - explicação ajustada ganha nova `editorial_version`, e a anterior fica `RETIRED`;
  - o lote pendente continua como evidência congelada (`superseded_by_final`).
- **Recomendações jurisprudenciais:** a lista `JURISPRUDENCE_LINK_RECOMMENDATIONS.json` é só para integração e revisão.
  - `READY_TO_LINK` só quando a identidade do registro local curado está comprovada (por exemplo, `source_id` `STF:SV:16`).
  - Caso contrário, `PENDING_EXTERNAL_INGESTION`.
  - Nenhum registro é fabricado.
