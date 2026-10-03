# ARTICLE_SEARCH — ENTER repetido = próxima ocorrência (DEVICE V1)

Status: **aprovado em testes, aguardando teste físico.**
- Nada gravado no ESP32.
- Nada escrito no SD.
- Sem commit.
- Complementa `ARTICLE_SEARCH_TARGET_CENTERING_REPORT.md`; a centralização foi preservada e vale para cada ocorrência.

## Comportamento legado (`executarBusca`, v7.12.0, inalterado)

**Estado da busca** (`numeroUltimaBusca`, `offsetUltimaOcorrencia`, `inicioProximaBusca`, `temOcorrenciaDaBusca`, `numeroBuscaEditado`):
- `pesquisarArtigo` grava `offsetUltimaOcorrencia=pos` e `inicioProximaBusca=pos+1`.

**ENTER com o mesmo número, sem edição:**
- busca a partir de `inicioProximaBusca`;
- **não dá a volta** ao início.

**Fim das ocorrências:**
- mostra "SEM OUTRA OCORRENCIA" por 500 ms e redesenha a barra;
- a posição e o cursor ficam como estão;
- um novo ENTER repete a mensagem.

**Primeira busca sem resultado:** "ART. n NAO ENCONTRADO".

**Reset** (`reiniciarEstadoBusca`):
- ao editar o número (`numeroBuscaEditado`);
- ao abrir ou reabrir qualquer TXT.

**Documentação:** nenhum `.md` do repositório descreve a regra de próxima ocorrência. A referência é a implementação legada, sem divergência a registrar.

## V1 antes (diferia: SIM)

- `lexV1ExecutarBuscaArtigo` sempre fazia `reiniciarEstadoBusca()` + `pesquisarArtigo(n,0)`.
- Ao encontrar, voltava ao NORMAL_READING_MODE com o buffer vazio.
- O ENTER seguinte abria **outra** busca, sempre a partir do offset 0.
- Resultado: o mesmo número achava sempre a primeira ocorrência. ADCT art. 5, ADCT art. 1 e as demais ocorrências posteriores ficavam inalcançáveis.

## Implementação

Tudo dentro de `#if LEX_DEVICE_V1_ENABLED`, sem tela, menu, tecla ou label novos.

**Cursor de repetição**
- Reusa o estado legado (número, última ocorrência, próximo início).
- Acrescenta uma âncora do pouso: arquivo, tamanho e byte do topo, gravados por `lexV1MarcarRepeticaoBusca()` após cada ocorrência encontrada.

**`lexV1PodeRepetirBusca()`** — o cursor só vale se tudo isto for verdade:
- ocorrência válida, número não editado, consulta não vazia;
- mesmo arquivo e mesmo tamanho;
- cache do leitor válido;
- **mesmo topo do pouso**.

**ENTER no NORMAL_READING_MODE**
- Cursor válido → `lexV1ProximaOcorrenciaArtigo()`.
- Caso contrário → `lexV1EntrarBusca()`, como antes.

**`lexV1ProximaOcorrenciaArtigo()`**
- Usa `numeroUltimaBusca` e busca a partir de `inicioProximaBusca`, ou seja, um offset estritamente posterior.
- Achou → `lexV1PousarBuscaNaLinhaAtiva`, depois `desenharViewportLeitor`, depois nova âncora.
- Não achou → "SEM OUTRA OCORRENCIA" + 500 ms (política legada): sem volta ao início, posição e cursor mantidos.

**Ocorrência estrutural** (`lexV1PesquisarArtigoEstrutural` + `lexV1OcorrenciaEstrutural`)
- Mesmo casamento do legado (`pesquisarArtigo`).
- No runtime V1, a ocorrência só vale se o `CF88_TEXT_MAP.IDX` tiver **exatamente nesse offset** a linha `NS:ART.n`. O namespace vem do mapa, nunca do número.
- Achado da auditoria: o matcher legado aceita "art." minúsculo no início de linha física. O runtime tem 20 remissões assim, por exemplo "art. 2º da Lei nº 12.858", offset 494627, dentro do ADCT art. 76 §6º. Elas agora são puladas.
- Se nenhuma ocorrência estrutural restar, o leitor volta ao topo de antes e o estado não fica apontando para a remissão.
- Vale para a primeira busca e para as seguintes (mesma lógica). Nos outros arquivos, a ocorrência textual continua valendo, como no legado.

**Resets do cursor**
- `lexV1EntrarBusca()`: toda nova operação de busca começa invalidando o cursor. Digitar ou editar dígitos só acontece dentro de uma nova busca, e `lexV1ExecutarBuscaArtigo` zera o estado antes de pesquisar.
- `lexV1CancelarBusca()` (BACK com buffer vazio): invalida o cursor e chama `reiniciarEstadoBusca()`. A restauração para a origem da operação continua igual.
- Rolar, abrir outro arquivo (`reiniciarEstadoBusca` na abertura) ou mudar o tamanho do runtime também invalidam: o ENTER seguinte abre uma nova busca.

**Target e camadas**
- Não há target fixo. O ACTIVE_TARGET de cada ocorrência sai do TEXT_MAP na linha `linhaContextoAtivo(LEITOR_LINHAS_VISIVEIS)`, que segue sendo a fonte única.
- `lexV1SincronizarAlvo` descarta `lexV1Disp` quando o target muda, então nenhuma camada da ocorrência anterior sobrevive.
- A regra ART↔CAPUT segue só para linha de artigo da CF. Para `ADCT:ART.5` as chaves são só `[ADCT:ART.5]`.

**Inalterados (comparados ao HEAD):**
- `pesquisarArtigo`, `executarBusca`, `executarBuscaTexto`, `reiniciarEstadoBusca`, o handler de teclado do state machine V1, `rolarLeitor` e `indexarAntesDaJanela`;
- RUN1, RUN2 e RUN3 (RUN3: 451 relações, 122 WORK_REFERENCE).

## State machine (DEVICE V1)

```
NORMAL --ENTER [cursor inválido]--> ARTICLE_SEARCH (buffer vazio, origem = topo atual)
NORMAL --ENTER [cursor válido: mesmo arquivo/tamanho/topo do pouso, sem edição]--> próxima ocorrência estrutural
        achou  -> pouso na linha ativa, NORMAL, nova âncora
        não    -> "SEM OUTRA OCORRENCIA", NORMAL, posição e cursor mantidos
ARTICLE_SEARCH --dígitos/BACKSPACE--> edita a consulta; ENTER --> busca do início (cursor novo)
ARTICLE_SEARCH --BACKSPACE vazio--> NORMAL na origem da operação; cursor zerado
qualquer rolagem / abrir arquivo --> cursor inválido
```

## Casos (modelo `tools/reader_viewport.ArticleSearchV1` + contrato de fonte)

| Consulta | ENTER 1 | ENTER 2 | ENTER 3 |
|---|---|---|---|
| 5 | `CF88:ART.5` (offset 2507), linha ativa | `ADCT:ART.5` (offset 430836), linha ativa | SEM OUTRA OCORRENCIA, fica no ADCT 5 |
| 1 | `CF88:ART.1` (offset 685, perto do início) | `ADCT:ART.1` (offset 429294) | SEM OUTRA OCORRENCIA |
| 2 | `CF88:ART.2` | `ADCT:ART.2` | SEM OUTRA OCORRENCIA (pula a remissão 494627) |
| 193 (único) | `CF88:ART.193`, 4 REF. (3 obras, RUN3) | SEM OUTRA OCORRENCIA, posição mantida | — |

- **Todos os números de artigo do mapa (≥250):** a sequência de ENTERs visita exatamente as linhas `NS:ART.n` do TEXT_MAP, em ordem, cada uma ativa após o pouso. Depois mostra a mensagem do fim.
- **Camadas** depois de CF 5 → ADCT 5 (RUN3):
  - disponibilidade e listas iguais às de um cálculo novo para `ADCT:ART.5`;
  - nenhuma obra do CF art. 5 (A Revolução dos Bichos, Filadélfia) permanece;
  - camadas stale: 0.
- **Consulta alterada:**
  - rolar e dar ENTER → nova busca, que reencontra a 1ª ocorrência;
  - 5 → … → 37 não reaproveita o cursor;
  - editar "5" para "6" busca o 6.
- **BACK depois da 2ª ocorrência:** com uma nova operação aberta a partir do ADCT 5 e cancelada, o leitor volta à origem **dessa** operação, não ao CF art. 5. O estado fica zerado e o ENTER seguinte abre uma busca.
- **Arquivo/runtime diferente:** abrir arquivo ou mudar o tamanho invalida o cursor.
- **Pouso:** 276/276 artigos da CF continuam pousando no próprio target. Art. 193 → `CF88:ART.193`, CONTEXTO ART.193, camada 4 com 3 obras (RUN3).

## Testes

- **Novo** `tests/test_article_search_next_occurrence.py`: **16/16**.
  - Contrato de fonte: condição de repetição; próxima ocorrência; política de fim; resets; ocorrência estrutural; sem target fixo e sem cache velho; legado e flag0.
  - Modelo: casos 5, 193, 1, 2; todos os números; mudança de consulta; BACK; troca de arquivo; camadas RUN3; art. 193.
- **`test_article_search_landing.py`: 18/18.** Contrato atualizado: o pouso agora é chamado na 1ª ocorrência e na próxima.
- **`test_reader_state_machine.py`: 10/10.** Contrato atualizado: o ENTER do NORMAL agora ramifica entre repetir e entrar na busca; a primeira busca usa a busca estrutural.
- **DEVICE 184/184**, incluindo:
  - target sync 14;
  - layer routing 9;
  - caput equivalence 12;
  - RUN3 DEVICE 9.
- **ENTENDA 95/95.**
- **LEGAL_TARGET_ID 65/65:** Reference Engine 20, RUN3 engine 14.

## Build (arduino-cli 1.5.1, ESP32S3 OPI / 4MB / default). Nada gravado.

| Build | Programa | RAM estática | App .bin | sha256 |
|---|---|---|---|---|
| flag 0 baseline aprovado (HEAD) | 989.395 B | 124.452 B | 989.536 B | `4d9ac64e…0de7` |
| flag 0 combinado | 989.395 B | 124.452 B | 989.536 B | `8ac5518c…a260` |
| flag 1 baseline físico aprovado (HEAD) | 1.075.603 B | 125.612 B | 1.075.744 B | `ddf93f51…1b26` |
| flag 1 só centering | 1.075.919 B | 125.612 B | 1.076.064 B | `d6fe0f7b…8dfa` |
| **flag 1 combinado (centering + next occurrence)** | **1.077.191 B (+1.588)** | **125.636 B (+24)** | **1.077.344 B (+1.600)** | **`0b17e904b822a29cc7e4cae4f9f33d5201183f620d226055dc851ca39ce6b2ba`** |

**flag 0 combinado × baseline:** os dois `.bin` diferem em 69 bytes, todos de metadata de build:
- `app_elf_sha256` do descritor, 0xB0–0xCF;
- dígitos de `__TIME__` em "Software Info", 0x3160–0x3164 (19:07 → 43:21);
- checksum + SHA256 da imagem, 0xF193F–0xF195F.

Código e dados são idênticos. Os testes também confirmam que o `.ino` sem as regiões V1 é igual ao HEAD e que nenhum identificador novo aparece fora delas.

**Candidato:** `backups/search_centering/candidate_combined_flag1/candidate_app_search.bin` (fora do Git), com checksum e hash válidos pelo `esptool image_info`.
- Fonte `.ino` sha256 `2418a730…02af6`.
- `contexto_juridico.h` sha256 `2cad3c38…8f68`.

## Teste físico sugerido (não executado)

1. ENTER, `5`, ENTER → `CONTEXTO: ART. 5` na linha central.
2. ENTER → ADCT art. 5 na linha central. Serial: `LEXV1: BUSCA Art. 5 PROXIMA 2507 -> 430836` e `ACTIVE_TARGET=ADCT:ART.5`.
3. ENTER → "SEM OUTRA OCORRENCIA"; o texto não se move.
4. Rolar uma linha e dar ENTER → abre "BUSCAR ARTIGO"; BACKSPACE volta ao mesmo ponto.
5. ENTER, `193`, ENTER → ART. 193 com 4 REF. (com SD em RUN3, 3 obras; o SD atual RUN1 também tem as 3 do art. 193); depois ENTER → "SEM OUTRA OCORRENCIA".

**Para decidir depois:** enquanto o leitor está parado no pouso, ENTER significa "próxima". Para abrir uma busca nova sem rolar não há tecla livre no NORMAL; basta uma linha de rolagem. É a mesma limitação prática do legado, em que digitar abria a nova busca. Avaliar no teste físico.

---

# Atualização — REPEAT_READY UX FIX (substitui a limitação "para decidir depois")

**Problema:** logo após uma busca, ENTER no NORMAL executava direto a próxima ocorrência. Para abrir uma busca nova era preciso rolar antes.

**Agora** (tudo dentro de `#if LEX_DEVICE_V1_ENABLED`; teclas, labels e telas inalterados):

- **NORMAL_READING:**
  - 1/2/3/4 abrem as camadas;
  - **ENTER sempre abre o ARTICLE_SEARCH** (`lexV1EntrarBusca`).
- **Sem busca anterior válida:** a busca abre vazia e o cursor é descartado.
- **Com busca anterior válida** (`lexV1PodeRepetirBusca`: mesmo arquivo, mesmo tamanho, leitor ainda no pouso, consulta não editada):
  - a caixa abre com a consulta anterior (ex.: `5`);
  - `lexV1RepetirPronto=true` (REPEAT_READY).
- **REPEAT_READY + ENTER sem edição** → `lexV1ProximaOcorrenciaArtigo()`:
  - busca estrutural (TEXT_MAP) a partir de `inicioProximaBusca`;
  - pouso na linha ativa;
  - volta ao NORMAL.
  - No fim: "SEM OUTRA OCORRENCIA" (500 ms), posição e cursor mantidos, volta ao NORMAL (política legada).
- **REPEAT_READY + 1º dígito:** o dígito **substitui** a consulta (`5` → `1`, nunca `51`) → NEW_QUERY:
  - `numeroBuscaEditado=true`;
  - o ENTER busca do offset 0, com cursor novo.
- **REPEAT_READY + 1º BACKSPACE:** passa a editar (`5` → vazio, `37` → `3`) → NEW_QUERY. Com a caixa vazia, BACKSPACE cancela, como antes.
- **Cancelar (BACK):** volta à origem da operação, que é a posição de leitura atual (o texto não se move durante a busca):
  - nenhuma busca é executada;
  - o ACTIVE_TARGET não muda;
  - o estado da busca é zerado.
- **Rolagem:** continua invalidando o cursor (regra já contratada). Após rolar, ENTER abre a busca **vazia**; nunca é preciso rolar para iniciar uma busca.
- **Preservados:**
  - `lexV1PousarBuscaNaLinhaAtiva` e `linhaContextoAtivo(total)` em toda ocorrência;
  - somente ocorrências estruturais;
  - sem target fixo;
  - ACTIVE_TARGET = viewport → linha ativa → TEXT_MAP;
  - RUN3 (451 relações / 122 WORK_REFERENCE).

| Sequência | Resultado (modelo `ArticleSearchV1`) |
|---|---|
| ENTER, 5, ENTER | `CF88:ART.5`, NORMAL |
| ENTER | caixa `5`, REPEAT_READY |
| ENTER | `ADCT:ART.5` na linha ativa, NORMAL |
| ENTER, ENTER | SEM OUTRA OCORRENCIA, posição mantida |
| (em CF 5) ENTER, 1, 9, 3, ENTER | caixa `1` → `193`; `CF88:ART.193`, NORMAL, sem rolagem |
| (em 193) 4 | abre REFERÊNCIAS do `CF88:ART.193`; a consulta não vira `1934` |
| (RUN3) ENTER, 3, 7, ENTER, 4 | Os Donos do Poder, Raízes do Brasil; depois ENTER → caixa `37` |

**Testes:**
- novo `tests/test_article_search_repeat_ready.py`: **16/16** (os 12 casos pedidos + contrato do handler, declaração na região V1, rolagem e RUN3);
- landing **18/18**; next occurrence **16/16** (fluxo ENTER, ENTER);
- reader state machine **10/10** (contrato original restaurado: ENTER no NORMAL → `lexV1EntrarBusca()`);
- DEVICE **200/200**; ENTENDA **95/95**; LEGAL_TARGET_ID **65/65**;
- RUN3 engine **14/14**; RUN3 DEVICE **9/9**; target sync 14, layer routing 9, caput equivalence 12.

**Build final (nada gravado):**

| Build | Programa | RAM estática | App .bin |
|---|---|---|---|
| flag 0 | 989.395 B | 124.452 B | 989.536 B, sha256 `4f3442f1…41a4b6` |
| **flag 1 final** (centering + next occurrence + REPEAT_READY) | **1.077.451 B** | **125.644 B** | **1.077.600 B**, sha256 `5c38f7521f55ef45061120c5c6350aab603e7cd0e2fa5cde913da5133b86b94d` |

- **Delta flag 1** contra o baseline físico aprovado (1.075.603 / 125.612): **+1.848 B** de programa, **+32 B** de RAM, **+1.856 B** de imagem.
- **flag 0 × baseline:** 69 bytes diferentes, nos mesmos campos de metadata de build (`app_elf_sha256`, `__TIME__`, checksum/SHA256 da imagem). Código e dados idênticos.
- **Candidato:** `backups/search_centering/candidate_ux_flag1/candidate_app_search_ux.bin` (fora do Git), checksum e hash válidos. Fonte `.ino` sha256 `e16b811f…3f84`.

**Teste físico sugerido:**
1. ENTER, 5, ENTER → ART. 5.
2. ENTER (a caixa mostra 5), ENTER → ADCT art. 5.
3. ENTER, 1, 9, 3, ENTER → ART. 193 → 4 abre as referências.
4. ENTER (mostra 193), BACKSPACE, BACKSPACE, BACKSPACE, BACKSPACE → volta ao mesmo ponto.
