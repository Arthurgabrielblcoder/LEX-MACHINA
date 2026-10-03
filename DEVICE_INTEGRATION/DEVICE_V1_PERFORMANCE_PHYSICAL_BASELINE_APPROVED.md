# DEVICE V1 — PERFORMANCE PHYSICAL BASELINE APPROVED

**Status:** `LEX_DEVICE_V1_PERFORMANCE_BASELINE_APPROVED`
- **Validação humana:** `PHYSICAL_HUMAN_VALIDATION = APPROVED` (Arthur, 2026-10-03). Funcionamento físico correto e fluido.
- **Checkpoint:** tag `lex-device-v1-performance-approved-2026-10-03`. A tag anterior `lex-device-v1-physical-approved-2026-10-01` foi preservada.
- **Nesta missão:** sem flash e sem alteração do SD.

## 1. Funcionalidades incluídas

| Funcionalidade | Relatório |
|---|---|
| ARTICLE_SEARCH centering (ocorrência na linha ativa) | `ARTICLE_SEARCH_TARGET_CENTERING_REPORT.md` |
| Próxima ocorrência (CF art. 5 → ADCT art. 5, sem wrap) | `ARTICLE_SEARCH_NEXT_OCCURRENCE_REPORT.md` |
| REPEAT_READY (ENTER pré-carrega a consulta; o 1º dígito substitui) | `SEARCH_UX_PHYSICAL_VALIDATION_REPORT.md` |
| Busca indexada por artigo (`ARTICLE_SEARCH.IDX`, O(log n), sem scan) | `INDEXED_ARTICLE_SEARCH_REPORT.md` |
| **Carregador genérico de índices por texto** (`<NORMA>_ARTICLE_SEARCH.IDX`, vínculo por tamanho + SHA256 do texto aberto) | este relatório, §3 |
| Parser de artigos com milhar ("Art. 2.000." = 2000) | `ARTICLE_THOUSANDS_PARSER_FIX_REPORT.md` |
| Scroll bidirecional otimizado (cache de linhas visuais, contexto por âncora "Art.", leitura em bloco) | `BIDIRECTIONAL_SCROLL_PERFORMANCE_REPORT.md` |
| Índice físico da CF e índice físico do Código Civil | §2 |

## 2. Índices fisicamente validados (no SD em `/99_LEX_V1/10_TARGETS/`)

| Arquivo | Bytes | SHA256 | Registros | Texto vinculado | Bytes do texto | SHA256 do texto |
|---|---|---|---|---|---|---|
| `CF88_ARTICLE_SEARCH.IDX` | 5.216 | `56e437a0c9cebb113c47f6a7b100ee64363c63207a647eca0456e86d6db27fae` | 424 (276 CF88 + 148 ADCT) | `/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt` | 587.133 | (runtime verificado no boot) |
| `CC2002_ARTICLE_SEARCH.IDX` | 25.036 | `674c9971925c29aaca9685fb2d0b9515fe87e4072d644858ea27495c327d3a68` | 2.077 | `/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt` | 660.268 | `ad5ba178613b6181e2d8a61919eda0c6223c68feb6e47bef4ea65bc45c13e6ae` |

**Índice do CC:**
- Foi gerado a partir do índice estrutural `LEGAL_TARGET_ID/build_target_index.py --norma CC2002`: 2.077 artigos, 0 duplicatas, 0 anomalias. O modo estrito dá o mesmo resultado.
- Contém 2.030 números distintos até 2046, mais 47 artigos com sufixo.
- Os arts. 1.620–1.629 e 1.768–1.773 existem no texto apenas como "Arts. … a …" (revogados) e não são indexados.

**Cópias versionadas:**
- `staging_article_index/SD/…/CF88_ARTICLE_SEARCH.IDX`
- `staging_article_index_cc/SD/…/CC2002_ARTICLE_SEARCH.IDX`
- Manifestos e índice estrutural em `_host/`.

**SD físico:** a cópia do índice do CC adicionou exatamente 1 arquivo. Os outros 1.070 arquivos, inclusive o índice da CF, ficaram byte a byte idênticos. Manifestos antes/depois em `backups/cc_index/` (fora do Git).

## 3. Carregador genérico (DEVICE V1)

Fluxo:
- Ao abrir um texto, lista `/99_LEX_V1/10_TARGETS/*_ARTICLE_SEARCH.IDX` só pelos nomes, sem abrir as entradas.
- Lê o header de 96 B de cada candidato.
- Só considera os que têm o MESMO tamanho de texto.
- Calcula o SHA256 do texto aberto. O runtime da CF usa o hash já verificado no boot; os outros textos são calculados uma vez por sessão (CC: 645 ms).
- Carrega o índice cujo SHA256 confere e valida o SHA256 do corpo.

Regras:
- Fica um índice por vez em PSRAM. Trocar de texto descarrega o anterior: nenhum offset de outra norma sobrevive.
- Índice errado (mesmo tamanho com outro SHA, ou corpo corrompido) nunca é usado: `[ARTIDX] IGNORADO` / `INVALIDO` / `NENHUM_INDICE_VALIDO` → FALLBACK_LINEAR.
- Nenhum nome de norma no código.
- A busca pelo índice centraliza o pouso também fora do runtime da CF (o offset vem do índice estrutural).
- Política de FDs mantida: diretório fechado antes de abrir cada header; pico de 4 arquivos abertos no aparelho.

## 4. Resultados físicos (sessão de 2026-10-03, candidato `candidate_app_cc_index.bin` com logs de benchmark ligados)

**Flash app-only:**
- Gravado em 0x10000; `PHYSICAL_READBACK_MATCH = TRUE` (sha256 `f23e77cd…dfbb`).
- Partições e otadata inalteradas.
- Chip ESP32-S3 v0.2, MAC `e0:72:a1:f4:fd:28`.
- Rollback: `backups/cc_index/flash/app0_prewrite.bin`.

**Boot:**
- 1 reset POWERON.
- `TESTE CONTEXTO JURIDICO: OK` (inclui os 13 casos de milhar).
- `DIAG RESULT PASS pass=33 fail=0`.
- Nenhum panic, nenhum FAIL_IO.

**Índices no aparelho:**

| Evento | Detalhe |
|---|---|
| CF aberta | `LOADED CF88_ARTICLE_SEARCH.IDX records=424 bytes=5216 load_ms=103 PSRAM` |
| CF → CC | `UNLOAD CF88…` |
| CC aberto | `TEXT_SHA bytes=660268 ms=645 sha=ad5ba178613b` → `LOADED CC2002_ARTICLE_SEARCH.IDX records=2077 bytes=25036 load_ms=767 PSRAM` |

Nenhum FALLBACK_LINEAR no CC.

**Buscas (`[ARTSEARCH]`, todas `modo=INDEX`):**

| Texto | Art. | Offset | Comparações | Lookup | Pouso | Render | Total |
|---|---|---|---|---|---|---|---|
| CF | 230 | 414.869 | 10 | 69 µs | 86 ms | 243 ms | 343 ms |
| CF | 193 | 349.277 | 10 | 72 µs | 53 ms | 214 ms | 281 ms |
| CF | 30 | 61.093 | 9 | 73 µs | 70 ms | 350 ms | 433 ms |
| CC | 1000 | 277.339 | 12 | 74 µs | 62 ms | 131 ms | **206 ms** |
| CC | 2000 | 647.337 | 12 | **72 µs** | **62 ms** | **148 ms** | **224 ms** |
| CC | 2010 | 651.089 | 12 | 73 µs | 62 ms | 130 ms | **206 ms** |

- O tempo não cresce com a posição no arquivo. Antes, a busca linear do CC levava 712 ms para o art. 2000.
- CF art. 193: CONTEXTO ART=193 e camada 4 aberta para `CF88:ART.193`.
- Buscas de números inexistentes na CF (1000, 1500, 2000, 2001): "NAO ENCONTRADO" em 13 ms, sem pouso falso.

**CONTEXTO:** após pousar no CC art. 2.000, `CONTEXTO: ART=2000`. Na rolagem apareceram 1998 → 1999 → 2000. **Nenhum `ART=2` nem `ART=1`** em toda a sessão do CC.

**Scroll (154 passos com `[SCROLL]`):**

| Medida | Valor |
|---|---|
| Passo, total | média 86,9 ms, máximo 179 ms; **0 passos > 250 ms**; nenhum stall em segundos |
| UP | média 91,0 ms, máximo 179 ms |
| DOWN | média 83,9 ms, máximo 160 ms |
| Cache / contexto | média 17,0 ms, máximo 47,5 ms |
| ACTIVE_TARGET + CONTEXTO + camadas | média 9,1 ms, máximo 79,1 ms |
| TFT | média 60,7 ms, máximo 66,1 ms |
| 1º UP após o pouso no CC art. 2000 | **68,7 ms** total (cache HIT, contexto por checkpoint exato em 59 µs, 512 B lidos) |
| Contexto em passos típicos | 9 ms com ~100 B, 66–80 µs com checkpoint exato |

**Eventos:**
- Roda: no máximo 3 eventos coalescidos por redesenho, sem perda.
- PageDown em rajada: limite de ±12 linhas por redesenho (ver §7).

**Aprovação física de Arthur:** scroll e contexto profundos sem stall em segundos; funcionamento considerado correto e fluido.

## 5. Logs de benchmark desligados (versão de produção)

**Flags de produção:**
- `LEXV1_ARTSEARCH_LOG 0`: `[ARTSEARCH]`, `[ARTIDX] LOADED/UNLOAD/TEXT_SHA/SEM_INDICE`, `FALLBACK_LINEAR`.
- `LEX_SCROLL_PERF_LOG 0`: `[SCROLL]` por passo, `[SCROLL] PREPARO`, `PERF CONTEXTO_UP` estendido.

A infraestrutura continua no código: basta mudar para 1 para um novo benchmark físico.

**Sempre visíveis** (anomalias): `[ARTIDX] INVALIDO`, `IGNORADO`, `NENHUM_INDICE_VALIDO`, `TEXT_SHA falhou` e `[SCROLL] REFILL_FAILSAFE`.

**Efeito no comportamento:** os logs só imprimem. Nenhum valor medido entra em decisão. Os testes com logs desligados confirmam que nada mudou.

## 6. Testes (com logs desligados): 100% PASS

| Suíte | Resultado |
|---|---|
| DEVICE (todas) | **276/276** |
| ENTENDA | **95/95** |
| LEGAL_TARGET_ID | **65/65** |
| Reference Engine | 20/20 |
| RUN3 engine | 14/14 |
| RUN3 DEVICE | 9/9 |
| indexed article search | 20/20 |
| CC article index | 12/12 |
| article landing | 18/18 |
| next occurrence | 16/16 |
| REPEAT_READY | 16/16 |
| thousands parser | 19/19 |
| bidirectional scroll | 25/25 |
| reader state machine | 10/10 |
| FD policy (A3B-PREP2) | 11/11 |

O que foi reconfirmado no host:
- **Seleção de índice:** CF → índice CF; CC → índice CC; CC → CF → CC sem índice antigo.
- **Fail-closed:** mesmo tamanho com outro SHA e corpo corrompido.
- **Parser:** arts. 999, 1000, 1001, 1999, 2000, 2001 e 2046 corretos no Código Civil real e na fixture de 2.500 artigos. "Art. 2.000" nunca vira ART.2.
- **Logs:** valores de produção 0, e os avisos de anomalia continuam ativos.

## 7. Build (arduino-cli 1.5.1, `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`, logs desligados)

| Build | Programa | RAM estática | Imagem | SHA256 da imagem |
|---|---|---|---|---|
| flag 0 | 989.379 B | 124.452 B | 989.520 B | `e0a95dc0f32672df8e08e0e65c888cf34e522e95d08fa0b99cdd170672cb9e3c` |
| **flag 1 (baseline)** | **1.084.259 B** | **126.148 B** | **1.084.400 B** | **`9ff1ffc0ddead3633c9487e071c7c8d24e10548ffb1259f6e601de9e54d0d35d`** (checksum e hash válidos) |
| flag 1 validado no aparelho (logs ligados) | 1.086.439 B | 126.164 B | 1.086.592 B | `f23e77cd…dfbb` |

**Flag 1 sem logs vs. o validado no aparelho:** −2.180 B de programa e −16 B de RAM. A diferença são as chamadas `Serial.printf` e as strings de formato removidas pelo compilador quando a flag é 0. A lógica é idêntica.

**Flag 0 (−16 B vs. builds anteriores, 989.395 B):** o código do sketch é idêntico.
- O `.o` tem as mesmas seções de código e dados; só o debug difere, pelo nome da pasta de build.
- No `.flash.rodata`, a única string diferente é o `__TIME__` do build ("12:40:13").
- O linker passou a reaproveitar o final "13" dessa string para o literal `"13"` do autoteste, e o alinhamento mudou.
- É metadata de build, não mudança funcional. O texto flag0 do `.ino` e do `contexto_juridico.h` é idêntico ao HEAD (contrato `strip_v1`).

**Fontes:**
- `.ino` sha256 `b4e4ca19858fd3584ac6359f229a57fa6bf7d61ea552ed6fca2e1fc40c710028`
- `contexto_juridico.h` `82c7c02e…9595`
- `lex_leitor_scroll.h` `e5b574c4…449b`

**Imagem de produção:** `backups/perf_baseline/candidate_flag1/candidate_app_perf_baseline.bin` (fora do Git). **Não gravada.** O aparelho continua com o candidato validado (logs ligados). Gravar a imagem de produção fica para uma missão futura, se autorizada.

## 8. Limitações conhecidas (não bloqueiam)

1. O render da TFT custa ~60–150 ms por redesenho: 12 linhas + rodapé, e mais em pousos com camadas, como CF art. 30 com 350 ms. Otimizar o render é uma missão separada.
2. Só a CF e o CC têm `ARTICLE_SEARCH.IDX` no SD. As demais normas usam FALLBACK_LINEAR, que já reconhece "1.000".
3. Os índices das outras normas serão gerados depois, pelo pipeline/Updater: `build_target_index.py` + `build_article_search_index.py`, mesma convenção.
4. Arts. 98 e 202 continuam sem WORK_REFERENCE.
5. *Sicko* e *Pro Dia Nascer Feliz* continuam `APPROVED_PENDING_WORK_IDENTITY`.
6. RUN3 ainda não foi implantado fisicamente.
7. Batch04 ainda não foi implantado fisicamente.
8. PageUp/PageDown em rajada são somados e limitados a ±12 linhas por redesenho. É o limite pré-existente, sem aceleração. Na sessão, 7 PageDown que chegaram juntos viraram 12 linhas. A roda nunca perdeu eventos.
9. O 1º acesso ao CC na sessão calcula o SHA256 do texto (645 ms); reaberturas usam o cache.
10. O CC não tem TEXT_MAP: o CONTEXTO vem do parser, e camadas e ACTIVE_TARGET de camadas existem só no runtime da CF.

## 9. Próxima missão

`BATCH04 + RUN3 DEVICE CONSOLIDATION` sobre esta baseline. O código de RUN3/Batch04 que já existe no working tree foi deixado fora deste checkpoint e será consolidado nessa missão.
