# INDEXED ARTICLE SEARCH — busca por artigo via índice estrutural (DEVICE V1)

**Status:** `INDEXED_ARTICLE_SEARCH_READY`, aguardando benchmark físico.
- Firmware físico e SD físico não alterados.
- Sem commit.
- RUN1/RUN2/RUN3, ENTENDA, Reference Engine, camadas e semântica de targets intocados.

## 1. Causa da lentidão (medida no aparelho)

**Fonte:** log serial da sessão física de Arthur com o candidato `candidate_app_search_ux.bin` (`backups/search_ux_flash/session_serial.bin`, fora do Git).

| Busca | `PERF BUSCA_ARTIGO` (scan textual) | `PERF CONTEXTO_UP` (reconstrução de contexto) | Total |
|---|---|---|---|
| Art. 5 (2.507) | 42 ms | 55 ms (2.340 B) | ~0,1 s |
| Art. 37 (68.365) | 114 ms | 1.190 ms (68.211 B) | ~1,3 s |
| Art. 98 (158.307) | 187 ms | 2.721 ms (158.077 B) | ~2,9 s |
| Art. 193 (349.277) | 399 ms | **5.994 ms** (348.705 B) | ~6,4 s |
| **Art. 230 (414.869)** | **471 ms** | **6.592 ms** (383.690 B) | **~7,1 s** (vídeo: 6,5–7 s) |
| ADCT 5 (430.836, próxima) | 544 ms | 6.212 ms (361.942 B) | ~6,8 s |

Os dois termos crescem com o offset (O(n)):

1. **`pesquisarArtigo`** (busca textual linear) varre o `CF88_RUNTIME.txt` desde o offset 0, em blocos de 32 KiB, a cerca de **1,135 µs/B**. É **≈7%** do tempo.
2. **`reconstruirContextoAntesOffset`** responde por **≈93%** do tempo.
   - Depois do pouso centralizado, o topo da tela fica **acima** do checkpoint que a busca deixava na ocorrência.
   - O contexto jurídico é então relido **byte a byte** (`f.read()` por caractere, ~**17,2 µs/B**) desde o checkpoint anterior mais próximo, ou de até 256 KiB atrás.
   - **Regressão introduzida pelo ARTICLE_SEARCH_TARGET_CENTERING_FIX.** No baseline (pouso no topo) esse custo era 0, porque o checkpoint semeado estava exatamente no topo.

`indexarAntesDaJanela()` foi auditada e **não** é proporcional à posição. Ela lê para trás em blocos de 256 B só até o início da linha física anterior, e o pouso chama no máximo algumas linhas físicas.

## 2. Arquitetura anterior e auditoria dos índices existentes

- `CF88_TEXT_MAP.IDX`: ordenado por **offset**. Para resolver número → offset seria preciso varrer as 3.387 linhas, o que não serve.
- `CF88_TARGETS.IDX`: ordenado por `target_id` (busca binária possível em `CF88:ART.230`), mas **não tem offset**. Além disso, escolher `CF88:`/`ADCT:` pelo número seria inferência de namespace, proibida. Também não serve.
- `CF88_RUNTIME_TARGET_INDEX.json` (host, LEGAL_TARGET_ID): tem `kind=ARTIGO` + `line_start`. É a **fonte canônica** usada para gerar o novo índice no PC.

## 3. Novo formato: `ARTICLE_SEARCH.IDX` (LXARTIX1, schema 1)

Gerado no PC por `tools/build_article_search_index.py`, genérico para qualquer norma. Entradas: o target index estrutural da norma e o texto exato, mais o TEXT_MAP opcional para conferência cruzada. Não é feito com regex solta no texto.

**Header (96 B):**
- magic `LXARTIX1`;
- `schema=1`, `header_size=96`, `record_size=12`;
- `ns_count`, `records`;
- **bytes e sha256 do texto indexado** e **sha256 do corpo** (namespaces + registros).

**Tabela de namespaces:** 16 B por entrada (`CF88`, `ADCT`, …).

**Registro (12 B):** `u16 número | u8 sufixo (0 = nenhum, 1..26 = -A..-Z) | u8 namespace | u32 offset | u16 ocorrência | u16 reservado`.
- Ordenados por (número, sufixo, ocorrência); a ocorrência segue a ordem no texto.
- **Sufixo:** `29-A` = (29, 1). O teclado numérico atual nunca gera sufixo, então `29` encontra só `CF88:ART.29` e `ADCT:ART.29`. O schema já representa artigos com sufixo para uma UX futura.
- **Somente artigos estruturais:** cada registro precisa ser a linha do TEXT_MAP no seu offset. As 20 remissões "art. n da Lei…" do runtime nunca entram; por exemplo, o offset 494.627 ("art. 2º da Lei nº 12.858") não está no índice.

**Lookup:** `lower_bound` em (número, sufixo); as ocorrências são contíguas.
- Primeira ocorrência = registro[lb].
- Próxima ocorrência = primeiro registro da mesma chave com `offset ≥ inicioProximaBusca`. É o mesmo estado legado (`inicioProximaBusca = offset+1`), **sem reescanear o texto**.
- Complexidade **O(log n)**, sem I/O.

**CF (candidato):** `staging_article_index/SD/99_LEX_V1/10_TARGETS/CF88_ARTICLE_SEARCH.IDX`
- **424 registros** (276 CF88 + 148 ADCT), **5.216 B**, sha256 `56e437a0…7fae`;
- manifest em `staging_article_index/_host/`;
- **gerado duas vezes: BYTE_IDENTICAL**;
- não foi copiado para o SD físico.

## 4. Firmware (flag 1; tudo em regiões `LEX_DEVICE_V1_ENABLED`)

**`lexV1ArtIdxPronto()`** carrega o índice **uma vez**:
- `SD.exists` → `LexV1FileReader` rastreado (política de FDs: abre, lê tudo, fecha) → buffer em **PSRAM**, com fallback para RAM interna;
- **valida** magic, schema, tamanhos, `source_bytes == lexV1RuntimeBytes`, `source_sha256 == lexV1RuntimeSha` (o runtime já verificado no boot) e o sha256 do corpo;
- dono único do buffer (`lexV1ArtIdxLiberar`), liberado em qualquer falha.
- Log: `[ARTIDX] records=… bytes=… ns=… load_ms=… psram=PSRAM`.

**`lexV1PesquisarArtigoEstrutural()`:**
- **INDEX OK** → `lexV1ArtigoChave` (só dígitos, sem zero à esquerda, 1..65535) → `lexV1ArtIdxBuscar` → `reiniciarIndice(offset)` + estado legado. **Nenhum scan do texto.**
- **Índice ausente** → `[ARTIDX] AUSENTE … FALLBACK_LINEAR`: a busca estrutural linear anterior, compatível com o SD atual.
- **Índice presente mas inválido** → `[ARTIDX] INVALIDO <motivo> -> INDEX_INVALID_FALLBACK_LINEAR`: o índice é descartado e **nenhum offset dele é usado**.
  - O fallback linear é seguro porque cada ocorrência é validada no TEXT_MAP, que é hash-pinned.
  - Só a velocidade cai; o resultado continua correto.

**`reconstruirContextoAntesOffset()`** ganhou um gancho `#if LEX_DEVICE_V1_ENABLED`:
- quando o caminho antigo releria mais que `LEXV1_CTX_SEMENTE_MIN` (2 KiB), `lexV1ContextoEstruturalAntes()` consulta o TEXT_MAP em `limite-1`;
- o target (`CF88:ART.192:PAR.3`) vira artigo, parágrafo, inciso e alínea na representação do parser;
- a releitura começa no registro do mapa: **dezenas a centenas de bytes**, em vez de centenas de KB;
- perto do início do arquivo não há semente (reler é mais barato que o lookup).

**Pouso:** `lexV1PousarBuscaNaLinhaAtiva` não faz mais o lookup no TEXT_MAP só para o log (economia de ~50 ms). Continua usando `linhaContextoAtivo(LEITOR_LINHAS_VISIVEIS)`.

**Serial `[ARTSEARCH]`** (macro `LEXV1_ARTSEARCH_LOG 1`, que deve virar 0 depois do benchmark físico):
```
q=… modo=INDEX|LINEAR achou=… occ=… ns=… offset=… cmp=… lookup_us=… landing_ms=… render_ms=… total_ms=…
```
Pontos de medição: T0 = ENTER confirmado (entrada de `lexV1ExecutarBuscaArtigo` / `lexV1ProximaOcorrenciaArtigo`); T1 = início da procura; T2 = offset localizado; T3 = pouso calculado; T4 = `desenharViewportLeitor` concluído.

**UX preservada:** pouso centralizado, REPEAT_READY, CF5 → ADCT5, sem volta ao início, "SEM OUTRA OCORRENCIA" (500 ms), BACK, BACKSPACE, substituição da consulta, rolagem, ACTIVE_TARGET/CONTEXTO pelo TEXT_MAP, ART↔CAPUT, roteamento de camadas, sem vazamento.

## 5. Benchmark

A tabela completa está em `ARTICLE_SEARCH_PERFORMANCE_BENCHMARK.md`, gerada por `tools/article_search_benchmark.py`. O "Antigo" é físico quando há medição no log.

| Art. | Offset | Antigo (total) | Lookup novo (host) | Comparações | Total novo (estimado) | Speedup |
|---|---|---|---|---|---|---|
| 1 | 685 | ~148 ms (modelo) | ~1,7 µs | 10 | ~151 ms | 1,0× |
| 37 | 68.365 | 1.443 ms (físico) | ~1,7 µs | 9 | ~193 ms | 7,5× |
| 193 | 349.277 | 6.532 ms (físico) | ~2,0 µs | 10 | ~191 ms | 34× |
| **230** | 414.869 | **7.202 ms (físico)** | ~2,0 µs | 10 | **~194 ms** | **~37×** |
| 250 | 428.375 | ~5.134 ms (modelo) | ~2,0 µs | 10 | ~197 ms | 26× |

- O lookup é **constante em 9–10 comparações** do art. 1 ao 250.
- "Total novo" é uma estimativa pelas taxas físicas: pouso + 50 ms de lookup no TEXT_MAP para a semente + releitura × 17,2 µs/B + 139 ms (média `PERF SCROLL`, que cobre cache, ACTIVE_TARGET e redesenho).
- **Precisa ser confirmado no aparelho** com a linha `[ARTSEARCH] … total_ms=`.
- A meta física é < 200 ms (limite rígido de 300 ms).

**Fixture sintética:** 2.500 artigos + 200 de uma 2ª estrutura, com remissões em início de linha.
- **2.700 registros, 32.528 B.**
- Art. 10 e art. 2.400: **13 comparações cada** (⌈log2 2700⌉ = 12). Enquanto isso, o scan linear vai de 1.393 B a 385.743 B (≈438 ms estimados no aparelho, só o scan).
- A 2ª ocorrência do art. 10 está na 2ª estrutura (`F2`, ocorrência 1).
- Nenhuma remissão foi indexada.

## 6. Memória

| Índice | Registros | Bytes (PSRAM) |
|---|---|---|
| CF88 + ADCT (atual) | 424 | **5.216 B** |
| Fixture 2.500 | 2.700 | 32.528 B |
| Código Civil (projeção, ~2.100 com sufixos) | ~2.100 | **≈25,3 KB** |

- 12 B por ocorrência.
- Só o índice da norma aberta fica carregado; o texto nunca é carregado.
- Na troca de norma, `lexV1ArtIdxLiberar()` libera o buffer. Hoje só o runtime V1 tem índice.

## 7. Plano para as 72 normas

1. O Updater roda `build_article_search_index.py --text <NORMA>.txt --target-index <NORMA>_TARGET_INDEX.json [--text-map …] --out <NORMA>_ARTICLE_SEARCH.IDX` para cada texto indexado. O índice já é genérico: namespaces em tabela, sufixos, números até 65.535.
2. O firmware generaliza `LEXV1_ARTIDX_PATH` para o índice associado ao texto aberto. O loader já recebe o texto esperado (bytes + sha256) e falha fechado se não bater.
3. Normas sem índice continuam com a busca linear (FALLBACK_LINEAR), com o log identificando qual caminho foi usado.

## 8. Testes

- **Novo `tests/test_article_search_indexed.py`: 20/20.**
  - header e tamanho; rebuild BYTE_IDENTICAL; todo registro = linha do TEXT_MAP;
  - **paridade com a busca estrutural linear** para todos os números (e para `0`, `05`, `251`, `999`, `65536`);
  - CF5 → ADCT5 e fim sem volta ao início; sufixo `29-A` separado; remissões fora;
  - **comparações ≤ ⌈log2 n⌉+4 e 0 scans de texto**;
  - releitura de contexto limitada (< 8 KiB, contra > 250 KB antes);
  - fail closed (hash do corpo, texto diferente, schema, arquivo curto) com fallback correto;
  - fixture 2.500 (tamanho, art. 10 × art. 2.400, 2ª estrutura, remissões);
  - UX com índice (5 → ADCT5 → fim; 193 com camada 4; 37 → obras do RUN3);
  - contrato do firmware: ramo indexado primeiro e sem `pesquisarArtigo`/`SD.open`; busca binária em memória; validações do loader; gancho da semente; pouso sem I/O do TEXT_MAP; logs; flag0 inalterado.
- **Suítes relacionadas:** landing 18/18 (contrato atualizado: o pouso não consulta mais o TEXT_MAP); next occurrence 16/16; REPEAT_READY 16/16; reader state machine 10/10; target sync 14/14; layer routing 9/9; caput equivalence 12/12; RUN3 DEVICE 9/9; A3B-PREP2 (política de FDs) 11/11.
- **Totais:** DEVICE **220/220**, ENTENDA **95/95**, LEGAL_TARGET_ID **65/65** (Reference Engine 20/20, RUN3 engine 14/14).

## 9. Build (arduino-cli 1.5.1, ESP32S3 OPI / 4MB / default). Nada gravado.

| Build | Programa | RAM estática | App .bin |
|---|---|---|---|
| flag 0 | 989.395 B | 124.452 B | 989.536 B. Diferença do baseline: 70 B, todos de metadata de build (`app_elf_sha256`, dígitos de `__TIME__`, checksum/SHA256 da imagem). Código e dados idênticos |
| flag 1 baseline físico aprovado | 1.075.603 B | 125.612 B | 1.075.744 B |
| flag 1 candidato atual no aparelho (UX) | 1.077.451 B | 125.644 B | 1.077.600 B |
| **flag 1 indexado (centering + next + REPEAT_READY + INDEXED)** | **1.080.227 B** | **125.700 B** | **1.080.368 B**, sha256 `68ba79c09c574c1e854e0de1d187cfb864002cbea22b33d6ac77fb79ea93f6c6`, checksum e hash válidos |

- **Delta** contra o baseline físico: +4.624 B de programa, +88 B de RAM. Contra o candidato UX: +2.776 B, +56 B.
- **PSRAM em tempo de execução:** +5.216 B (índice CF).
- **Candidato:** `backups/search_centering/candidate_indexed_flag1/candidate_app_indexed.bin` (fora do Git). Fonte `.ino` sha256 `0984ee75…76e9`.

## 10. Benchmark físico sugerido (próxima missão)

1. Copiar `CF88_ARTICLE_SEARCH.IDX` para `/99_LEX_V1/10_TARGETS/` (com autorização) e gravar o candidato (app-only).
2. Buscar 1, 5, 15, 37, 100, 150, 193, 230 e 250, e depois 5 → ENTER, ENTER (ADCT 5).
3. Coletar as linhas `[ARTIDX]` e `[ARTSEARCH]`. Exigir `modo=INDEX`, `total_ms` < 200 (rígido < 300) e `lookup_us` na faixa de dezenas de µs.
4. Sem o arquivo de índice no SD, o firmware deve logar `FALLBACK_LINEAR`. O ganho da semente de contexto continua valendo: estimativa ~0,6 s para o art. 230, só pelo scan.
