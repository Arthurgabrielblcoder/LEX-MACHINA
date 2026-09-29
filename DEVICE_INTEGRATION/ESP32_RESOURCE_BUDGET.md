# ESP32_RESOURCE_BUDGET (V1, estimativa sem hardware)

Alvo: ESP32-S3 Dev Module, 240 MHz, **8 MB de PSRAM (OPI)**, ILI9341 3,2", microSD por SPI (`SD_CS` 4).

O firmware v7.12.0 já usa PSRAM para dois caches:
- cache de Relations V2 (lookup de até 64 linhas + `RELACOES.IDX` inteiro);
- cache J4 (log real validado: cerca de 64,9 KB).

**Medidas reais (V1-A2).**

- **Boot do v7.12.0 no aparelho:** heap inicial 213.696 B; heap depois do BLE 136.988 B; PSRAM livre antes dos caches 8.334.248 B; PSRAM livre depois do J4 8.218.772 B.
- **Compilação** (arduino-cli, core 3.3.11, partições default de 4 MB):

  | Build | Flash | RAM estática |
  |---|---|---|
  | v7.12.0 e candidato com flag 0 | 989.395 B (75% de 1.310.720) | 124.452 B |
  | candidato com `LEX_DEVICE_V1_ENABLED=1` (A2B, com sha256 do runtime) | 997.319 B (+7.924) | 124.452 B (+0) |

- **Buffers do `lex_device_v1.h` na pilha:** `line[256]` ×2 dentro de `lexv1Find`, `title[160]`, `key[48]`. Isso cabe com folga nos 8 KB da task do loop. **[MEDIR]** o stack high-water no aparelho.

Os valores marcados **[MEDIR]** dependem do hardware e não devem ser tratados como fato.

## Tamanhos medidos no pacote (PC)

| Item | Máximo medido | Buffer proposto |
|---|---|---|
| target_id | 35 B (índice); 22 B entre os targets com ENTENDA | `char key[48]` |
| Linha de índice (TARGETS/TEXT_MAP/ENTENDA/REF lookup) | 119 B | `char line[256]` |
| Linha do `REF_PAYLOAD` | 193 B | o mesmo `line[256]` |
| Referências por target | 10 | 10 × `{uint32 offset; uint16 len; uint8 tipo}` = 80 B (texto lido sob demanda) |
| Título (`D\|`) | 139 B | `char title[160]` |
| Bloco ENTENDA | 3.097 B (teto do contrato: 6.144 B) | streaming em `chunk[1024]` **ou** bloco inteiro em PSRAM (6 KB) |
| Linha de seção do ENTENDA | 718 B | quebra por largura em pixels (rotina existente) |
| Janela final da busca binária | 512 B | não exige buffer: ressincroniza linha a linha com `line[256]` |

## RAM mínima para lookup, sem cache

`key 48 + line 256 + title 160 + estado da busca (~32) + lista de refs 80 + chunk 1024` ≈ **1,6 KB** de RAM interna (ou PSRAM).
Isso basta para os quatro lookups (targets, text map, ENTENDA e referências) com seek + leitura de linha.

## PSRAM recomendada (cache opcional, por prioridade)

| Arquivo | Bytes | Motivo |
|---|---|---|
| `CF88_TEXT_MAP.IDX` | ≈148 KB | consultado a cada mudança de linha central, ao rolar; evita cerca de 9 seeks por mudança |
| `ENTENDA_LOOKUP.IDX` + `REF_LOOKUP.IDX` | ≈36 KB | consultados a cada mudança de dispositivo |
| `CF88_TARGETS.IDX` | ≈160 KB | flags de camada; pode ficar no SD (10 seeks) se a PSRAM apertar |
| Payloads (`ENTENDA_PAYLOAD.DAT` 303 KB com 163 explicações, `REF_PAYLOAD.IDX` 66 KB) | 0 | **não** carregar: lidos só quando o usuário abre a camada |

- **Total com todos os índices em PSRAM:** cerca de 0,35 MB (≈4,3% de 8 MB).
- **Somado aos caches legados:** bem abaixo de 1 MB. **[MEDIR]** a PSRAM livre real depois do boot do v7.12.0.

## Acessos típicos ao SD

| Evento | Sem cache | Com os índices em PSRAM |
|---|---|---|
| Mudança de dispositivo ao rolar | TEXT_MAP (~9) + TARGETS (~10) + ENTENDA lookup (~8) + REF lookup (~6) ≈ 33 seeks, ~2–4 KB lidos | 0 acessos |
| Abrir ENTENDER | 1 seek + ≤ 6 KB | igual |
| Abrir REFERÊNCIAS | 1 seek + ≤ 10 linhas (≤ 2 KB) | igual |

**[MEDIR]** a latência de seek/leitura do SD no barramento atual. Se 33 seeks por rolagem for perceptível, o cache em PSRAM resolve.

## Benchmark no PC (só complexidade; não prevê o tempo do ESP32)

Consultas em todos os 3.954 targets, 5 repetições, com contagem de seeks por consulta:

| Lookup | Seeks máximos | Limite log2 + folga |
|---|---|---|
| Targets | 10 | 11 |
| ENTENDA lookup | 8 | 8 |
| ENTENDA com payload | 9 | — |
| Referências com payload | 6 | 6 |

A resolução de BLOCK é uma única linha, sem segundo salto. Não há varredura linear em nenhum lookup novo.

## Princípios

- Buffers pequenos e fixos, busca binária no arquivo e leitura por seek. Nada de `String` dinâmica no caminho quente.
- Não carregar payload inteiro na RAM interna. Se usar PSRAM, alocar com `heap_caps_malloc(MALLOC_CAP_SPIRAM)`, como os caches existentes.
- **[MEDIR]** fragmentação do heap interno com BLE ativo. O v7.12.0 já prioriza PSRAM para preservar o heap do BLE.
