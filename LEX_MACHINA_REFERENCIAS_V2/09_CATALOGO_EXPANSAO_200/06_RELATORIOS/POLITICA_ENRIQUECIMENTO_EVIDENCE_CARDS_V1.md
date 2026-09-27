# Política de enriquecimento de evidence cards — V1

Esta política é o contrato para uma missão futura (Codex ou outro agente) que acrescente evidence cards às obras utilizáveis de `09_CATALOGO_EXPANSAO_200`.

**Estado de partida:** 199 obras utilizáveis e 221 cards. Os dados estão em `07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json`, compilado em 2026-09-26.

## 1. Princípios

1. **Não existe meta obrigatória de cards por obra.** Um card sólido vale mais que quatro artificiais.
2. **Documentar a obra, não o direito.** Pesquise o que a obra efetivamente contém, representa, analisa ou permite fazer. Nunca "qual artigo combina com esta obra?".
3. **Cada frase do claim deve estar na fonte citada no card.** A auditoria dos lotes 1–4 mostrou que o erro mais frequente é completar a sinopse com conhecimento próprio. O que a fonte não diz não entra no card.
4. **Todo card novo carrega `"not_targeted_to_device": true`.** Não gerar CF88:ART…, CC:ART… nem qualquer vínculo com dispositivo.
5. **Não alterar a ontologia.** Quando faltar conceito, use descrição factual controlada e mantenha `ONTOLOGY_GAP`.
6. **Não executar a Engine.** Não alterar RC1, RC2, holdout, contratos, score, firmware, IDX nem o SD.

## 2. Quantos cards por obra

| Perfil da obra | Cards |
|---|---|
| Obra simples: premissa única e bem delimitada | 1 pode bastar |
| Obra com dois fatos centrais independentes | 2 |
| Obra rica: vários sistemas, partes, casos ou episódios documentados | 3–5, quando documentalmente sustentados |
| Acima de 5 | Somente com justificativa editorial escrita no dossiê |

## 3. Quando criar um card adicional

Um card novo só pode ser criado quando existir **um elemento independente** de um destes tipos:

- fato independente;
- mecânica independente;
- argumento acadêmico independente;
- evento narrativo independente;
- prática institucional independente.

Além disso, o elemento precisa ser **sustentado por fonte concreta e consultável**, e a página tem de ter sido aberta. Snippet de mecanismo de busca não basta como fonte final.

## 4. O que é proibido

- **Fatiar uma única evidência.**

  Errado (é uma evidência só):
  - Card 1: existe vigilância.
  - Card 2: pessoas são vigiadas.
  - Card 3: a vigilância afeta as pessoas.

  Certo, quando os dois fatos forem distintos e documentados:
  - Card 1: o sistema coleta comunicações privadas.
  - Card 2: o sistema atribui classificação estatal aos indivíduos.

- **Usar a ambientação geral como evidência.** Frases como "cidade obcecada por poder" ou "mundo distópico" não viram card.
- **Transformar tema amplo em prova específica:**
  - prisão não vira devido processo;
  - empresa não vira ordem econômica;
  - guerra não vira norma internacional;
  - pobreza não vira assistência social;
  - vigilância não vira interceptação;
  - racismo não vira crime constitucional;
  - trabalho não vira direito trabalhista específico.
- **Repetir o mesmo argumento em vários cards** só porque ele aparece em capítulos diferentes.
- **Promover elemento PONTUAL a CENTRAL.**
- **Trocar fonte boa por outra por preferência,** ou reescrever claim correto por estilo.

## 5. Mecânica × narrativa (jogos)

- `MECANICA_INTERATIVA` e `EVENTO_NARRATIVO` são evidências distintas quando forem efetivamente independentes.
- Uma **mecânica repetível** (verificar documentos, alocar recursos, julgar casos) pode ter card próprio mesmo quando o mesmo objeto também aparece na narrativa.
- Uma mecânica documentada prova uma *possibilidade* do jogo, não a ocorrência em toda partida. Registre esse limite no card.
- Afirmações genéricas de design ("suas escolhas importam", "o mundo reage a você") não são mecânica documentada.

## 6. Não ficção (livros e documentários)

Use o predicado que corresponde ao que o autor faz:

| Predicado | O autor... |
|---|---|
| **ANALISAR** | examina um fenômeno |
| **HISTORIAR** | narra processo ou evento histórico |
| **ARGUMENTAR** | sustenta posição normativa ou tese |
| **COMPARAR** | contrapõe casos ou sistemas |

- ANALISAR e HISTORIAR existem no vocabulário congelado de predicados. **ARGUMENTAR e COMPARAR não existem** (verificado em 2026-09-26). Para eles:
  - `claim.predicate` fica ANALISAR;
  - a distinção vai num campo editorial separado, `modo_discursivo: ARGUMENTAR | COMPARAR`;
  - não crie predicado novo.
- Separe a descrição histórica da posição normativa do autor.
- Casos independentes de um mesmo livro (por exemplo, Tanzânia × Brasília em *Seeing Like a State*) podem gerar cards distintos, se a fonte descrever cada caso.

## 7. Séries antológicas e episódios

Segue o modelo aplicado a Black Mirror (#113):

- A obra permanece **única** no catálogo. Episódios não viram obras novas.
- Cada card de episódio leva `unidade_documental` (por exemplo, `T3E1 'Nosedive'`) e `escopo_centralidade: EPISODIO`.
- Máximo de 3 episódios por rodada, sempre com fonte oficial por episódio.

## 8. Fontes

- **Prioridade:**
  - A: oficial ou primária;
  - B: institucional ou acadêmica;
  - C: secundária reputável.
- **Não usar como prova:** Wikipédia, Fandom, Reddit, fóruns, blogs pessoais, SEO, resumo de IA ou listas "top 10".
- **Registrar em cada fonte:**
  - `verificacao`: `PAGINA_CONSULTADA` ou `RESULTADO_DE_BUSCA`;
  - `locator`;
  - `accessed_on`;
  - quando a página for baixada, `snapshot_sha256` (só o hash, sem copiar o conteúdo).
- **Link morto:** substitua por fonte oficial acessível equivalente e registre `fonte_substituida`.

## 9. Procedimento obrigatório por lote

1. Trabalhar em lotes de 25, com checkpoint após cada lote.
2. Para cada obra: ler o dossiê, abrir a fonte e decidir entre **nenhum card novo**, **+1** ou **+N**, justificando por escrito.
3. Não alterar `status_triagem`, salvo erro objetivo registrado.
4. Registrar cada alteração com hashes antes e depois, como em `REVISOES_POS_CHECKPOINT.json`.
5. Recompilar o catálogo duas vezes e confirmar hashes idênticos.
6. Reverificar a integridade dos congelados (`08_MANIFEST/gerar_manifest.py`).
7. Antes da ingestão, auditar uma amostra determinística de 20 cards novos com o mesmo método de `amostra_auditoria.py`.

## 10. Estimativa de partida (não é meta)

Detalhes obra a obra em `ESTIMATIVA_ENRIQUECIMENTO.json`. É uma heurística transparente, não uma decisão.

| Estimativa | Obras |
|---|---|
| Provavelmente completas | 88 (os 40 filmes, 33 das 34 séries utilizáveis e obras que já têm 2+ cards) |
| Provavelmente +1 card | 93 (sobretudo jogos com card só mecânico ou só narrativo, documentários e livros com card único) |
| Provavelmente +2 ou mais | 18 (grande estratégia/simulação, antologias, livros em várias partes ou casos) |
| Cards adicionais possíveis | 129 a 147, indicativo |

Para cada obra, "nenhum card novo" continua sendo uma resposta legítima.
