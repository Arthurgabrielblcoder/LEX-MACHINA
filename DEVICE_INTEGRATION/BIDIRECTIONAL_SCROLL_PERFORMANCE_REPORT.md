# BIDIRECTIONAL SCROLL PERFORMANCE FIX — rolagem limitada após pouso aleatório

**Status:** `BIDIRECTIONAL_SCROLL_PERFORMANCE_READY — AGUARDANDO_TESTE_FISICO`
- Candidato gerado e medido no host.
- Firmware físico **não** alterado (nada gravado).
- SD físico **não** alterado.
- Sem commit, sem tag, sem push.

## 1. Causa confirmada (medida no aparelho, antes de alterar o algoritmo)

**Fonte:** `backups/indexed_bench/bench_serial.bin` (fora do Git), sessão física com o candidato indexado. A sequência é a de Arthur: abrir a norma grande, buscar o art. 2000 (pouso rápido), descer 4 linhas e subir.

```
PERF BUSCA_ARTIGO: 712 ms (offset=647337, bloco=32768)
PERF CONTEXTO_UP: 3517 us (checkpoint=sim, bytes=0)          <- pouso: checkpoint semeado no próprio offset
PERF CONTEXTO_UP: 3463 us ... (4 passos, bytes=0)
PERF CONTEXTO_UP: 11293148 us (checkpoint=sim, bytes=647150) <- 1º SCROLL_UP acima do pouso
PERF SCROLL: media=431753 us max=11380644 us
```

**Função responsável:** `reconstruirContextoAntesOffset()`, chamada por `atualizarCacheLeitor()` em todo `SCROLL_UP`.

O que acontece:
- O pouso semeia um checkpoint exatamente no offset do artigo. A primeira linha acima dele fica **antes** desse checkpoint.
- `obterCheckpointContexto()` devolve então o checkpoint mais próximo **abaixo**, que é o deixado perto do offset 0 quando o arquivo foi aberto.
- O laço relê o texto desde ali, **byte a byte** (`File::read()`, ≈17,4 µs/B), até o topo.
- Resultado: **647.150 B** relidos, **11,29 s** de CPU bloqueada.

Isso também explica o comportamento visto:
- **Congelamento:** a viewport fica parada durante a releitura. No vídeo, 7–8 s; neste log, 11,3 s.
- **Salto tardio:** os eventos da roda acumulam em `deltaLeitor` durante o bloqueio. Ao destravar, viram um único passo, limitado a ±12 linhas (o salto de 2000/2001 para 1998/1999).

A hipótese de visual-line reflow caro foi **refutada** como causa do stall. `indexarAntesDaJanela()` relê só a linha física anterior (centenas de bytes).

Ela contribuía, porém, para a falta de fluidez depois do destravamento:
- descartava o cache do leitor a cada reabastecimento;
- lia byte a byte;
- abria o TXT várias vezes por passo.

No runtime CF havia ainda um segundo custo: a semente do TEXT_MAP (~68 ms) era consultada em quase todo `SCROLL_UP`. No log, eram passos de 80 ms, com mais ~100 ms de render.

| | Antes |
|---|---|
| 1º UP art. 2000, bytes | **647.150 B** (físico); 3.116.060 B na fixture de 3,9 MB |
| 1º UP art. 2000, tempo | **11,29 s** (físico); ≈53,6 s estimados na fixture |
| Algoritmo | contexto relido desde o checkpoint mais próximo **abaixo** do topo (ou janela cega de 256 KiB), byte a byte: **O(offset no arquivo)** |

## 2. Instrumentação adicionada (somente `LEX_DEVICE_V1_ENABLED=1`)

**`[SCROLL]` por passo**, emitida em `rolarLeitor`:

`dir`, `passos`, `pend` (eventos coalescidos), `topo`, `prev`/`next` (linhas visuais conhecidas acima/abaixo), `cache=HIT|MISS`, `ant=linhas/bytes/us` (reabastecimento anterior), `seg=linhas/bytes/us` (seguinte), `ctx=origem/bytes/linhas/us`, `io` (IO_BYTES), `seeks`, `opens`, `cache_us`, `alvo_us`, `tft_us`, `total_us`, `FAILSAFE`.
- `alvo_us` = ACTIVE_TARGET + CONTEXTO + camadas (`diagnosticarContextoSeMudou`).
- `tft_us` = viewport + rodapé.

**`PERF CONTEXTO_UP`:** mantém o formato antigo (o parser do benchmark continua válido) e acrescenta `origem=`, `io=`, `seeks=`, `linhas=`.

**`[SCROLL] PREPARO`** no pouso:
- linhas preparadas acima e abaixo;
- contexto aquecido;
- bytes lidos;
- `txt_abertos` / `txt_pico` (FDs do leitor).

**Flag:** `LEX_SCROLL_PERF_LOG 1` (mudar para 0 depois do teste físico).

## 3. Correção

Todas as mudanças estão dentro de `#if LEX_DEVICE_V1_ENABLED`. O texto do flag0 é idêntico ao HEAD; o build flag0 tem o mesmo tamanho.

1. **`lex_leitor_scroll.h` / `LexArquivoBuffer`.**
   - Mesma interface de `File` usada pelo leitor, mas `read()` sai de um bloco de 512 B.
   - `avancarUmaLinhaVisual`, `indexarAte`, `lerLinhaVisualParaBuffer`, `reconstruirContextoAntesOffset` e `posicionarResultadoTexto` mantêm **o mesmo corpo**; muda só o tipo do arquivo.
   - Abertura somente com `FILE_READ`, transitória, fechada no destrutor.
2. **Cache bidirecional de linhas VISUAIS.** É a própria janela `offsetsLinhas[]`: offsets de início de linha visual, 4 B cada.
   - **ANTERIOR:** `lexIndexarAntesDaJanelaV1()` reabastece em **bloco**: até 48 linhas, percorrendo linhas físicas para trás.
     - O 1º parágrafo é sempre inteiro (wrap exato); os seguintes só até 8 KiB.
     - A varredura reversa usa o bloco já em RAM.
     - Os índices do cache da viewport são deslocados, não descartados.
   - **SEGUINTE:** um bloco de 48 linhas por abertura.
   - Ambos disparam quando resta menos de uma tela (12 linhas). Um passo de uma linha usa só offsets já conhecidos.
3. **Contexto jurídico limitado** (`reconstruirContextoAntesOffset`, ordem nova):
   1. checkpoint **exato**: devolve sem abrir o TXT;
   2. checkpoint ≤ 2 KiB: relê dali (como antes);
   3. **âncora** `Art.` mais próxima (`lexAncoraArtigoAntes`), validada pelo **próprio parser** (`aplicarLinhaContextoCompatCF`, inclusive o look-ahead `Art.`/`12.` do cf.txt):
      - uma linha de artigo zera parágrafo/inciso/alínea, então reler a partir dela dá **o mesmo contexto** que reler desde o byte 0;
      - nenhuma regra jurídica nova;
   4. semente do TEXT_MAP (runtime V1, inalterada);
   5. fail-safe: nenhum artigo em 32 KiB → janela de 32 KiB com contexto vazio (log `janela_failsafe`).

   A janela cega de 256 KiB saiu do caminho V1.
4. **Pouso = centralizar + montar viewport + preparar cache.** `carregarCacheLeitorCompleto` → `lexPrepararCacheBidirecional()`:
   - bloco anterior;
   - bloco seguinte;
   - contexto aquecido 48 linhas acima do topo (deixa checkpoints).

   Vale para busca, próxima ocorrência, busca textual, saltos e abertura. Assim o 1º UP encontra offsets e checkpoint próximos, como o 10º.
5. **Hard limits:**

   | Limite | Valor |
   |---|---|
   | `LEX_CACHE_ANTERIOR_ALVO` / `_SEGUINTE_ALVO` | 48 |
   | `_MIN` | 12 |
   | `LEX_REFILL_ORCAMENTO` | 8 KiB |
   | `LEX_PARAGRAFO_MAX` (parágrafo sem LF → `REFILL_FAILSAFE`) | 64 KiB |
   | `LEX_CTX_ANCORA_MAX` | 32 KiB |
   | `LEX_LEITOR_BLOCO` | 512 B |

**Complexidade:**
- **Antes:** O(offset no arquivo) por `SCROLL_UP` acima de um pouso.
- **Depois:** O(tamanho do artigo/parágrafo local), com teto rígido de 32 KiB (contexto) e 64 KiB (wrap patológico). Não depende da posição no arquivo.

**Tamanho do bloco anterior (benchmark, 240 UP a partir do art. 2000):**

| Linhas/bloco | Reabastecimentos | Pior passo (est.) | Bytes por reabastecimento |
|---|---|---|---|
| 16 | 15 | 22,9 ms | 5,6 KB |
| 32 | 7 | 22,9 ms | 7,7 KB |
| **48** | **5** | **23,7 ms** | **8,7 KB** |
| 64 | 3 | 26,9 ms | 10,8 KB |
| 128 | 1 | 35,4 ms | 15,9 KB |

48 mantém a constante anterior (4 telas), com 5 reabastecimentos e pior passo < 25 ms.

**Cache e memória:**
- **Janela:** `offsetsLinhas` existente (16.000 × 4 B = 64 KB DRAM estática, inalterada). O cache "quente" fica em ≥ 12 + 12 + 12 linhas, até ~108 registros (≈432 B).
- **Temporário por reabastecimento:** 2 × 48 × 4 B = 384 B de pilha.
- **`LexArquivoBuffer`:** 512 B de pilha por abertura.
- **Anel de checkpoints:** existente (128 entradas, PSRAM), inalterado.
- **PSRAM adicional:** **0 B**.
- **Posse e tempo de vida:** a janela pertence ao leitor.
  - É invalidada por `reiniciarIndice`: novo arquivo, nova busca, próxima ocorrência, salto, restauração após cancelar.
  - Os checkpoints são zerados quando o arquivo muda.
  - Fonte, largura (`LEITOR_TEXTO_W`) e layout são constantes de compilação: não existe evento de runtime que mude o wrap. Se um dia existir, deve chamar `reiniciarIndice`.
  - Nenhum scroll reconstrói o cache inteiro.

## 4. Eventos (roda/touch/setas/PageUp/PageDown)

- O **backlog** foi confirmado como efeito do stall, não como causa: no log, 1 passo de 11,3 s e depois um salto.
- O **coalescing** já existia e foi preservado:
  - roda, touch e teclas acumulam em `deltaLeitor`;
  - o loop chama `rolarLeitor` **uma vez**, com um redesenho;
  - o clamp de ±12 linhas foi mantido;
  - nenhuma aceleração nova, nenhum evento descartado além do clamp aprovado.
- Com o custo eliminado, o modelo de 20 eventos a cada 40 ms dá:
  - **pendentes ≤ 3**, **0 perdidos**, 20/20 linhas percorridas (antes: 19 pendentes e 7 perdidos no clamp);
  - pior passo 110,6 ms com render.
- O render redesenha as 12 linhas e o rodapé a cada passo, como no comportamento aprovado (`montarLinhaRGB` + `drawRGBBitmap` por linha + `desenharBarraBusca`). **Não foi alterado.**

## 5. Benchmark host (`tools/scroll_performance_benchmark.py` → `SCROLL_PERFORMANCE_BENCHMARK.json`)

**Fixture tipo Código Civil:**
- 2.500 artigos, **3.891.826 B**, 12.410 linhas físicas;
- caput, parágrafos, incisos, alíneas e títulos;
- parágrafos de 3–6 KiB numa só linha física;
- artigos de ~20 KiB.

**Modelo:** `tools/scroll_model.py` replica cada função do firmware, antiga e nova. Bytes, seeks, aberturas e linhas são exatos.

**Tempos estimados** pelas taxas medidas no aparelho:

| Item | Custo |
|---|---|
| `File::read()` | 17,2 µs/B |
| bloco de 512 B | 0,7 ms |
| CPU | 0,25 µs/B |
| `SD.open` | 3,4 ms (legado) / 12,3 ms (runtime CF) |
| TEXT_MAP | 68 ms |
| render | ~98 ms (inalterado) |

"Proc" é o processamento antes do render; "total" é proc + 98 ms de render.

**1º SCROLL_UP após o pouso** (sequência de Arthur: abrir, buscar, 4 DOWN, 4 UP, 1 UP acima do pouso):

| Pouso | Antes: bytes | Antes: proc | Depois: bytes | Depois: proc | Depois: total | Origem do contexto |
|---|---|---|---|---|---|---|
| art. 10 | 16.486 | 286 ms | 3.072 | **11,5 ms** | 110 ms | checkpoint |
| art. 500 | 778.970 | 13,4 s | 3.072 | 11,5 ms | 110 ms | checkpoint |
| art. 1000 | 1.557.411 | 26,8 s | 5.120 | **14,8 ms** | 113 ms | âncora |
| art. 2000 | 3.116.060 | 53,6 s | 3.584 | **12,6 ms** | 111 ms | âncora |
| art. 2400 | 3.725.004 | 64,1 s | 2.560 | **10,8 ms** | 109 ms | checkpoint |

Viewport e contextos das 12 linhas são **idênticos** entre antigo e novo nos 5 casos.

**Sequências após o pouso no art. 2000 (novo):**

| Sequência | Proc |
|---|---|
| warm UP | 4,1–8,3 ms (cache HIT) |
| DOWN | 4,1 ms |
| 10 UP | máx. 12,6, média 7,5 ms |
| 10 DOWN | 4,1 ms cada |
| UP/DOWN alternado ×10 | máx. 12,6, média 4,5 ms |
| reabastecimento anterior (48 linhas) | 19–22 ms (5,6–7,7 KB) |
| reabastecimento seguinte | 10,8 ms (2,5 KB) |
| 120 UP | máx. 22 ms |
| PageUp ×10 | máx. 21 ms |
| 20 eventos rápidos UP/DOWN (coalescidos 2 a 2) | máx. 12,6 / 4,1 ms |

**Pouso no runtime CF** (centralizado, semente TEXT_MAP):

| Art. | Pouso antes → depois | 30 UP: média antes → depois | Consultas TEXT_MAP |
|---|---|---|---|
| 37 | 191 → 79 ms | 104 → 23 ms | 31 → 0 |
| 193 | 197 → 77 ms | 98 → 19 ms | 27 → 0 |
| 230 | 152 → 86 ms | 105 → 22 ms | 31 → 0 |

Contextos idênticos.

**Metas:**
- cache hit < 20 ms: ✔;
- cold refill < 80 ms: ✔ (≤ 22 ms);
- nenhum bloqueio > 250 ms: ✔;
- nenhum stall em segundos: ✔.

O "total ideal < 40–50 ms" **não** é alcançável sem mexer no render: o piso físico é ~98 ms por passo e era igual no baseline aprovado. Os campos `cache_us` / `alvo_us` / `tft_us` do `[SCROLL]` vão medir isso no aparelho. Otimizar o render (redesenho parcial / hardware scroll) fica como missão separada.

**Pouso legado:** fica 0–12 ms mais caro (estimado; art. 2000: 33,8 → 45,3 ms), porque passa a preparar as 48+48 linhas e o contexto anterior. No CF fica mais barato.

## 6. Testes

**Novo `tests/test_bidirectional_scroll.py`: 25/25.**
- Requisitos 1–12: pouso art. 2000 → 1º UP; sem scan global; bytes limitados e independentes do offset; 10 UP; 10 DOWN; alternância; reabastecimento anterior; reabastecimento seguinte; transição de target; transição de contexto; camadas/rodapé no runtime CF (ACTIVE_TARGET e flags 1–4 idênticos, 0 consultas de semente); backlog de eventos rápidos.
- Casos de borda:
  - 32 KiB sem artigo;
  - parágrafo de 320 KB (`REFILL_FAILSAFE`);
  - início do arquivo sem artigo;
  - marcador `Art.` isolado do cf.txt;
  - escolha do bloco 48.
- Contratos de fonte: header só com a flag e só `FILE_READ`; mesmo corpo de wrap; ordem da reconstrução; limites; pouso, busca e ACTIVE_TARGET intocados; flag0 idêntico ao HEAD.

**Contratos antigos ajustados** (a missão autoriza mudar `rolarLeitor`/`indexarAntesDaJanela`):
- `test_article_search_landing`: `rolarLeitor`/`indexarAntesDaJanela` agora são comparados no texto flag0 (`strip_v1`), e o corpo do wrap continua idêntico.
- `test_a3b_prep.device_v1_ino_sections`: deixou de contar os ramos `#else` (código flag0) como DEVICE V1.

**Suítes:**

| Suíte | Resultado |
|---|---|
| DEVICE (inclui landing 18, indexed 20, next occurrence 16, REPEAT_READY 16, reader state machine 10, RUN3 DEVICE 9, FD policy A3B-PREP2 11, scroll 25) | **245/245** |
| ENTENDA | **95/95** |
| LEGAL_TARGET_ID (inclui Reference Engine 20, RUN3 engine 14) | **65/65** |

## 7. Build (arduino-cli 1.5.1, `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`). Nada gravado.

| Build | Programa | RAM estática | App .bin |
|---|---|---|---|
| flag 0 | 989.395 B | 124.452 B | 989.536 B, idêntico ao anterior |
| flag 1 indexado (anterior) | 1.080.227 B | 125.700 B | 1.080.368 B |
| **flag 1 candidato scroll** | **1.083.615 B** | **125.780 B** | **1.083.760 B**, sha256 `8075e18a…de9d`, checksum e hash válidos (`esptool image-info`) |

- **Delta:** +3.388 B de programa, +80 B de RAM estática, **+0 B de PSRAM**. Pilha: +≈1,4 KB no pior caminho (reconstrução + âncora); a validação da âncora usa 2×128 B.
- **Candidato:** `backups/scroll_perf/candidate_flag1/candidate_app_scroll.bin` (fora do Git).
- **Fontes:** `.ino` sha256 `ad99c56b…9e12`; `lex_leitor_scroll.h` `e5b574c4…449b`.
- **Warnings novos:** nenhum. Os `-Wvolatile` são pré-existentes.

## 8. Teste físico sugerido (próxima missão, com autorização)

1. Gravar só a app (0x10000), ler de volta e exigir igualdade. O SD não precisa de arquivo novo.
2. Na norma grande: abrir, buscar 2000 e dar 1 UP imediato.
   - Esperado: `[SCROLL] dir=UP … ctx=ancora|checkpoint/<8 KB` e `total_us` ≈ render (~100–120 ms). Nenhum `PERF CONTEXTO_UP` com centenas de KB.
3. Depois, 10 UP / 10 DOWN / alternado e roda rápida.
   - Esperado: `pend` ≤ 3, sem congelamento, sem salto tardio.
4. CF: 193, 37, 5 e ADCT 5 (busca + próxima ocorrência).
   - Esperado: ACTIVE_TARGET, CONTEXTO e camadas 1–4 como antes; nenhum `origem=text_map` em cada UP.
5. Coletar `[SCROLL] PREPARO … txt_pico=` (espera-se ≤ 2) e confirmar `fd_pico MAX_OPEN_COUNT` ≤ 6.

## 9. Observação fora do escopo

O log físico mostra `CONTEXTO: ART=2` no art. 2.000 do Código Civil. `lerNumeroDispositivo` para no separador de milhar (`2.000` → `2`). É pré-existente e não foi alterado; foi registrado como tarefa separada.
