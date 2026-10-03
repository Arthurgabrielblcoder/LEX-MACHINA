# ARTICLE THOUSANDS PARSER FIX — "Art. 2.000." = artigo 2000

**Status:** `THOUSANDS_PARSER_E_SCROLL_FIX_PRONTOS — AGUARDANDO_TESTE_FISICO`
- Firmware físico **não** alterado (nada gravado).
- SD físico **não** alterado; `CF88_ARTICLE_SEARCH.IDX` permanece.
- Sem commit, sem tag, sem push.

## 1. Origem exata do bug

**Firmware:** `contexto_juridico.h` → `lerNumeroDispositivo()`, chamada por `aplicarLinhaContextoJuridico()` no ramo "Art".
- O laço lia apenas dígitos e parava no primeiro `.`.
- Em "Art. 2.000." o separador de milhar encerrava o número, e o resultado era `ART=2`.
- Log físico (`backups/indexed_bench/bench_serial.bin`): `CONTEXTO: ART=2` logo após `BUSCA Art. 2000 -> offset=647337`, e `ART=1` no art. 1.999.

**Mesmo defeito no host:** `LEGAL_TARGET_ID/structure_parser.py`, `ART_RE` = `(\d{1,4})` seguido de `.` como pontuação.
- Esse é o parser que geraria o TARGET_INDEX / `ARTICLE_SEARCH.IDX` de CC, CPC e CLT.
- "Art. 2.000." viraria `…:ART.2` com caput "000. …".

**Não afetados:**
- A busca linear legada (`correspondeArtigoNoInicioLinhaRapido`) já ignorava pontos de milhar.
- A busca indexada usa o número digitado, sem passar pelo parser.

**Código Civil real** (backup local do SD, fora do Git, 660.268 B):

| | Antes | Depois |
|---|---|---|
| Cabeçalhos lidos como `2` | 48 | 1 |
| Maior artigo | 1337 | 2046 |
| Números distintos | 1.008 | 2.075 (todos os cabeçalhos) |

## 2. Regra (genérica, sem caso especial)

Depois dos dígitos iniciais, um `.` só faz parte do número quando **duas condições** valem:
- o bloco inicial tem 1–3 dígitos;
- o ponto é seguido de **exatamente 3 dígitos** (o 4º caractere não é dígito).

O bloco se repete: `N.ddd`, `NN.ddd`, `NNN.ddd`, `N.ddd.ddd`.

Detalhes:
- O valor inteiro é acumulado em `uint32_t` com teto `LEX_NUMERO_DISPOSITIVO_MAX = 999.999.999`.
- Exceder o teto ou a capacidade do campo → `false`; o contexto não é alterado.
- Nunca é decimal. O último `.` continua sendo pontuação.
- Sufixo (`-A`) e ordinal (`º`/`ª`) seguem o tratamento existente, depois do número.

**Onde está:**
- **Firmware:** dentro de `#if LEX_DEVICE_V1_ENABLED` no header.
  - O flag0 continua idêntico (só 70 B de metadata de build diferem; mesmo tamanho).
  - O sketch tem `static_assert(LEX_CONTEXTO_MILHAR==1)`: um build V1 que inclua o header sem a flag falha na compilação.
- **Host:** o port Python (`context_parser_port.py`, chave `THOUSANDS` para reproduzir o bug) e o `structure_parser.py` aplicam a mesma regra.
  - A gramática de `target_id` continua limitando artigos a 4 dígitos (fail closed acima de 9.999).
  - Nenhum TXT da CF é afetado (nenhuma linha "Art. N.ddd"). LEGAL_TARGET_ID 65/65, rebuilds inalterados.

| Entrada | ART |
|---|---|
| Art. 1. / Art. 2. / Art. 20. / Art. 200. | 1 / 2 / 20 / 200 |
| Art. 5º / Art. 1º | 5 / 1 |
| Art. 29-A | 29-A |
| Art. 999. | 999 |
| Art. 1.000. / 1.001. / 1.234. / 1.999. | 1000 / 1001 / 1234 / 1999 |
| Art. 2.000. / 2.001. / 2.046. | 2000 / 2001 / 2046 |
| Art. 1.000-A / Art. 2.000º / Artigo 1.500 / Art 2.000 | 1000-A / 2000 / 1500 / 2000 |
| Art. 1.000.000 | 1000000 |
| **Malformados:** 1.00 / 1.0000 / 1234.567 / 2.0 / 2.000.00 / 12.34 / 2.00a | 1 / 1 / 1234 / 2 / 2000 / 12 / 2 (para no ponto, como antes) |
| Art. 999.999.999.999 / Art. .500 | rejeitado (contexto intacto) |

O autoteste de boot (`validarRotinaContextoJuridico`) ganhou 13 casos V1. Um teste host confere que o port produz exatamente a tabela do firmware.

**Remissões:**
- O parser de contexto continua lendo "art. 2º da Lei nº 12.858" como art. 2 (comportamento anterior). Nunca vira 12858.
- No índice estrutural, o modo estrito (`article_case_sensitive`) continua rejeitando a linha.
- A `ARTICLE_SEARCH` continua vindo só do TEXT_MAP / índice estrutural.

## 3. Validação

**Fixture de 2.500 artigos (3,89 MB):** passa a imprimir os números como o Código Civil ("Art. 2.000."). O mapa estrutural é gerado pelo gerador, independente do parser.

| Art. | Contexto antes da correção | ACTIVE_TARGET (mapa) | CONTEXTO depois |
|---|---|---|---|
| 998 / 999 | 998 / 999 | F1:ART.998 / 999 | 998 / 999 |
| 1000 / 1001 | **1 / 1** | F1:ART.1000 / 1001 | 1000 / 1001 |
| 1999 | **1** | F1:ART.1999 | 1999 |
| 2000 / 2001 | **2 / 2** | F1:ART.2000 / 2001 | 2000 / 2001 |
| 2400 | **2** | F1:ART.2400 | 2400 |

Vale para o pouso centralizado (linha ativa) e para o pouso legado (linha 0).

**Scroll** (pouso no 2000 → UP até 1999 → DOWN até 2000 → DOWN até 2001):
- A sequência da linha ativa é `2000 → 1999 → 2000 → 2001`.
- Em **todas as 12 linhas de todos os passos**, contexto = artigo estrutural.
- Nenhum `ART.1` ou `ART.2`.
- Também foram verificados: cache hit, reabastecimento anterior e seguinte (130 UP, 200 DOWN) e PageUp/PageDown ×8.

**Busca indexada:** `ARTICLE_SEARCH.IDX` construído para a fixture.
- `find(2000)` → offset exato do "Art. 2.000.", com ≤ ⌈log2 n⌉+4 comparações e sem scan.
- No firmware, `lexV1ArtigoChave` / `lexV1ArtIdxBuscar` / `lexV1PesquisarArtigoEstrutural` / `lexV1EntrarBusca` não usam o parser.
- REPEAT_READY pré-carrega `numeroUltimaBusca` (o texto digitado, "2000").
- Ressalva: hoje só a CF tem índice no SD. O CC continua no FALLBACK_LINEAR, que já reconhece "2.000".

**Scroll fix preservado** (benchmark reexecutado com a fixture de milhar):

| Medida | Resultado |
|---|---|
| 1º UP art. 2000 | **3.584 B**, ≈12,6 ms de processamento (total ≈111 ms com render); antes 3,1 MB / ≈53,6 s |
| art. 10 / 1000 / 2400 | 3.072 / 5.120 / 2.560 B |
| 10 UP | máx. 12,6 ms |
| 10 DOWN | 4,1 ms |
| 120 UP | máx. 22 ms |
| Backlog | ≤ 3 pendentes, 0 perdidos |

Viewport e contextos idênticos entre antigo e novo; nenhum scan global.

## 4. Testes

**Novo `tests/test_thousands_parser.py`: 19/19.** Cobre:
- tabela, malformados, overflow e reprodução do bug;
- sufixo/ordinal/§/inciso/alínea;
- remissões;
- `ART_RE` e `parse_structure` (incluindo `CF88:ART.2001-A`) e o modo estrito;
- fixture (pouso, ACTIVE_TARGET, CONTEXTO, 1999→2000→2001, refill);
- 1º UP limitado;
- índice;
- busca/REPEAT_READY intocados;
- contrato do header V1, autoteste de boot = port, flag0;
- Código Civil real.

`test_article_search_landing` agora compara o header na visão flag0 (`strip_v1`).

| Suíte | Resultado |
|---|---|
| DEVICE | **264/264** |
| ENTENDA | **95/95** |
| LEGAL_TARGET_ID | **65/65** (Reference Engine 20, RUN3 engine 14) |
| RUN3 DEVICE | 9/9 |
| indexed | 20/20 |
| landing | 18/18 |
| next occurrence | 16/16 |
| REPEAT_READY | 16/16 |
| reader state machine | 10/10 |
| bidirectional scroll | 25/25 |
| FD policy | 11/11 |
| thousands | 19/19 |

## 5. Build combinado (centering + next occurrence + REPEAT_READY + indexed + bidirectional scroll + thousands). Nada gravado.

arduino-cli 1.5.1, `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`.

| Build | Programa | RAM estática | App .bin |
|---|---|---|---|
| flag 0 | 989.395 B | 124.452 B | 989.536 B (igual; 70 B de metadata) |
| flag 1 indexado | 1.080.227 B | 125.700 B | — |
| flag 1 scroll | 1.083.615 B | 125.780 B | 1.083.760 B |
| **flag 1 combinado** | **1.084.251 B** | **125.780 B** | **1.084.400 B**, sha256 `eb3fe59d…f312`, checksum e hash válidos |

- **Delta:** +636 B de programa e +0 B de RAM contra o candidato scroll; +4.024 B e +80 B contra o indexado. PSRAM +0.
- **Candidato:** `backups/thousands_parser/candidate_flag1/candidate_app_combined.bin` (fora do Git).
- **Fontes:** `.ino` sha256 `4d3c4221…9345`, `contexto_juridico.h` `82c7c02e…9595`, `lex_leitor_scroll.h` `e5b574c4…449b`.

## 6. Logs temporários

`LEX_SCROLL_PERF_LOG=1` e `LEXV1_ARTSEARCH_LOG=1` continuam ligados para o benchmark físico.

**Depois do benchmark físico, desligar esses logs antes da baseline de produção e da avaliação final de fluidez.** As linhas `[SCROLL]` / `PERF CONTEXTO_UP` / `[ARTSEARCH]` no serial custam tempo por passo.

## 7. Teste físico sugerido

1. Gravar a app combinada (0x10000) e ler de volta.
2. No Código Civil, buscar 2000.
   - Rodapé `ART. 2000` (não `ART. 2`).
   - Serial `CONTEXTO: ART=2000`.
3. Fazer 1 UP: aparece `ART=1999` quando a linha ativa entra no artigo anterior, sem congelar. Depois DOWN → 2000 → 2001.
4. Fazer ENTER: a caixa vem com `2000`.
5. Boot: `validarRotinaContextoJuridico` = `OK`.
6. CF: 5, 193, ADCT 5 como antes.
