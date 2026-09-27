# Auditoria amostral — lotes 1–4 (trabalho do Codex)

Data: 2026-09-26. Os dados completos estão em `AMOSTRA_AUDITORIA_LOTES_1_4.json`, reproduzível por `amostra_auditoria.py`.

## Método

- **Universo:** candidatas 1–100.
- **Exclusão:** #9 Cyberpunk 2077, revisada à parte em `DECISAO_CYBERPUNK_REVISADA.json`.
- **Estratos:** 8 jogos, 8 filmes e 4 séries.
- **Seleção:** dentro de cada mídia, os menores valores de `SHA-256(candidate_id)` em ordem lexicográfica hexadecimal. A seleção é determinística.
- **Verificações, por obra:**
  - identidade;
  - acesso real à fonte;
  - se a fonte sustenta a paráfrase;
  - centralidade;
  - claim e content_type;
  - `not_targeted_to_device`;
  - limites de transposição;
  - ausência de conclusão jurídica embutida.
- **Como as fontes foram consultadas:**
  - jogos: pela API oficial `appdetails` da Steam;
  - filmes e séries: abrindo a URL citada no dossiê.

## Resultado

| # | Obra | Mídia | Classificação | Achado |
|---|---|---|---|---|
| 26 | Victoria 3 | Jogo | AUDITORIA_OK | — |
| 31 | Lawgivers II | Jogo | AUDITORIA_OK | — |
| 44 | This Is the Police | Jogo | AJUSTE_MENOR | "reúne provas" não consta; a fonte diz "investigate crimes" |
| 42 | Frostpunk 2 | Jogo | AUDITORIA_OK | — |
| 33 | Not Tonight 2 | Jogo | AUDITORIA_OK | — |
| 24 | Yes, Your Grace | Jogo | AUDITORIA_OK | — |
| 39 | The Case of the Golden Idol | Jogo | AUDITORIA_OK | — |
| 1 | Disco Elysium | Jogo | AUDITORIA_OK | — |
| 88 | Tropa de Elite | Filme | AJUSTE_MENOR | Paráfrase acrescentava "operações", "segurança pública" e "Rio"; fonte tier C |
| 78 | The Zone of Interest | Filme | AUDITORIA_OK | — |
| 66 | Blood Diamond | Filme | AUDITORIA_OK | — |
| 68 | Milk | Filme | AUDITORIA_OK | — |
| 80 | Ainda Estou Aqui | Filme | **AJUSTE_IMPORTANTE** | Nomes, "busca a verdade" e "retirada por agentes" não constam da fonte citada |
| 51 | Erin Brockovich | Filme | AJUSTE_MENOR | "Reúne informações" e "ação de moradores" não constam |
| 64 | The Constant Gardener | Filme | AUDITORIA_OK | — |
| 57 | The Trial of the Chicago 7 | Filme | AUDITORIA_OK | — |
| 97 | Maid | Série | AUDITORIA_OK | — |
| 100 | Your Honor | Série | **FONTE_INSUFICIENTE** | A URL citada retorna HTTP 404 |
| 98 | Dopesick | Série | AUDITORIA_OK | — |
| 93 | The Good Wife | Série | AUDITORIA_OK | — |

**Contagem:**

| Classificação | Obras |
|---|---|
| AUDITORIA_OK | 15 |
| AJUSTE_MENOR | 3 |
| AJUSTE_IMPORTANTE | 1 |
| FONTE_INSUFICIENTE | 1 |

**Taxa de problemas importantes** = (1 + 1) / 20 = **10%**.

Pela regra da missão (0–10%), os **lotes 1–4 são satisfatórios por amostragem**. A taxa está exatamente no limite da faixa, então a segunda amostra fica registrada apenas como opcional e **não bloqueia** o próximo passo. Ela não foi executada.

## Itens sem problema em toda a amostra

- Identidade confirmada nas 20 obras.
- `not_targeted_to_device: true` em todos os cards.
- content_type adequado (mecânica × narrativa).
- Limites de transposição presentes.
- Nenhuma conclusão jurídica embutida nos claims.

## Padrão observado

Os problemas não estão na escolha das obras nem nas decisões editoriais. Estão em **paráfrases que vão além do texto da fonte citada**: o Codex completou a sinopse com conhecimento sobre a obra. Quatro das cinco correções são desse tipo; a quinta é um link morto.

A missão futura de enriquecimento deve exigir que cada frase do claim seja sustentada pela fonte indicada no card.

## Correções aplicadas

Somente erros objetivos foram corrigidos, e apenas nos dossiês afetados. A trilha completa, com hashes antes e depois, está em `REVISOES_POS_CHECKPOINT.json`.

- **#44:** paráfrase alinhada a "investiga crimes".
- **#51:** paráfrase alinhada à sinopse da Universal.
- **#80:** paráfrase restringida ao que a La Biennale afirma.
- **#88:** paráfrase alinhada à sinopse do AdoroCinema. A fonte C fraca fica como observação, mas não houve troca por preferência.
- **#100:** fonte substituída por `paramountglobalcontent.com/title/your-honor` (tier A, acessível). "Nova Orleans" foi removido porque não consta da nova fonte.

Nenhuma decisão editorial dos lotes 1–4 mudou por causa da auditoria.
