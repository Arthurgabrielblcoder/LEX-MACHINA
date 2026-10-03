# ARTICLE_SEARCH — benchmark de desempenho (busca indexada × busca linear)

Gerado por `tools/article_search_benchmark.py`. **OLD** físico = log serial da sessão de Arthur com o candidato anterior (busca linear + pouso centralizado); **OLD** modelo = taxas ajustadas nesse mesmo log (scan 1,135 µs/B; reconstrução de contexto 17,2 µs/B, sem checkpoint, janela ≤ 256 KiB). **NEW_LOOKUP** = medido no host com o algoritmo do firmware. **LANDING/RENDER/TOTAL NEW** são **estimativas** pelas taxas físicas até a medição no aparelho (linha serial `[ARTSEARCH] … total_ms=`).

Índice CF: **424 registros**, **5216 B** (header 96 + 2 namespaces × 16 + 424 × 12), ⌈log2 n⌉ = 9.

| ARTICLE | TARGET | BYTE_OFFSET | OLD_LOOKUP_MS | OLD_CONTEXT_MS | OLD fonte | NEW_LOOKUP (host) | CMP | LANDING_MS (est.) | RELIDOS p/ contexto | RENDER_MS (est.) | TOTAL_MS (est.) | OLD_TOTAL_MS | SPEEDUP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `CF88:ART.1` | 685 | 0.8 | 8.2 | MODELO | 1.73 µs | 10 | 3.6 | 474 B | 147.2 | 150.8 | 147.9 | 1.0× |
| 5 | `CF88:ART.5` | 2507 | 42 | 55.3 | FISICO | 1.78 µs | 10 | 2.9 | 159 B (semente TEXT_MAP) | 191.7 | 194.6 | 236.3 | 1.2× |
| 15 | `CF88:ART.15` | 30727 | 45 | 535.7 | FISICO | 1.81 µs | 10 | 4.8 | 263 B (semente TEXT_MAP) | 193.5 | 198.4 | 719.7 | 3.6× |
| 37 | `CF88:ART.37` | 68365 | 114 | 1189.9 | FISICO | 1.67 µs | 9 | 2.6 | 48 B (semente TEXT_MAP) | 189.8 | 192.5 | 1442.9 | 7.5× |
| 100 | `CF88:ART.100` | 161019 | 182.8 | 2764.2 | MODELO | 1.75 µs | 9 | 5.3 | 259 B (semente TEXT_MAP) | 193.5 | 198.8 | 3086.0 | 15.5× |
| 150 | `CF88:ART.150` | 249552 | 283.2 | 4289.2 | MODELO | 1.93 µs | 10 | 3.1 | 156 B (semente TEXT_MAP) | 191.7 | 194.8 | 4711.4 | 24.2× |
| 193 | `CF88:ART.193` | 349277 | 399 | 5994.4 | FISICO | 2.05 µs | 10 | 1.7 | 19 B (semente TEXT_MAP) | 189.3 | 191.0 | 6532.4 | 34.2× |
| 230 | `CF88:ART.230` | 414869 | 471 | 6591.5 | FISICO | 2.02 µs | 10 | 4.1 | 54 B (semente TEXT_MAP) | 189.9 | 194.0 | 7201.5 | 37.1× |
| 250 | `CF88:ART.250` | 428375 | 486.2 | 4508.9 | MODELO | 1.95 µs | 10 | 4.9 | 204 B (semente TEXT_MAP) | 192.5 | 197.4 | 5134.1 | 26.0× |

- Comparações do lookup: 9–10 (art. 1 a art. 250): **independe do offset**. Art. 230 (offset 414869): 10 comparações.
- Releitura para o contexto após o pouso: só do registro do TEXT_MAP anterior ao topo (dezenas a poucos milhares de bytes), em vez de centenas de KB desde um checkpoint distante.

## Fixture sintética: 2700 registros (433720 B de texto, 2.500 artigos + 200 da 2ª estrutura, remissões 'art. k da Lei…' em início de linha que **não** entram)

Índice: **32528 B**; ⌈log2 n⌉ = 12.

| ARTICLE | BYTE_OFFSET | CMP (índice) | LOOKUP (host) | SCAN LINEAR (bytes) | SCAN LINEAR (host) | SCAN LINEAR no aparelho (est.) |
|---|---|---|---|---|---|---|
| 10 | 1393 | 13 | 2.4 µs | 1393 | 13.1 µs | 1.6 ms |
| 100 | 15401 | 13 | 2.37 µs | 15401 | 127.8 µs | 17.5 ms |
| 1000 | 158663 | 13 | 2.37 µs | 158663 | 1284.7 µs | 180.1 ms |
| 2400 | 385743 | 13 | 2.48 µs | 385743 | 2373.0 µs | 437.8 ms |
| 2500 | 401963 | 12 | 2.34 µs | 401963 | 3002.7 µs | 456.2 ms |

- Art. 10 e art. 2.400: 13 e 13 comparações (máximo 13), mesma ordem de grandeza; o scan linear cresce de 1393 B para 385743 B.
- 2ª ocorrência do art. 10 (outra estrutura): namespace `F2`, ocorrência 1, 14 comparações.

## Projeção

- Código Civil (~2.046 artigos; ~2.100 registros com sufixos): ≈ **25328 B** (~24 KiB) em PSRAM; ⌈log2 2100⌉ = 12 comparações.
- 72 normas: um índice por texto indexado (carregado só o da norma aberta); 12 B/ocorrência.
