# CF-REF-A1 — Identidade canônica de dispositivos jurídicos (`target_id`)

**Resultado: `CF_REF_A1_CONCLUIDA — TARGET_ID_CANONICO_VALIDADO`.**

- **Decisão: B) `EXISTING_ID_NEEDS_EXTENSION`.** A chave já existente foi reutilizada e estendida; nenhuma identidade concorrente foi criada.
- **Escopo:** nenhum conteúdo jurídico foi gerado ou alterado. O texto oficial permanece intacto; o parser apenas interpreta.

## 1. Fonte da Constituição

| | Estrutura canônica (índice) | Texto operacional do SD |
|---|---|---|
| Arquivo | `updater/backup_catalogos/catalogo_mestre_20260913_145217/1- CONSTITUI#U00c7#U00c3O FEDERAL/cf.txt` | `updater/saida/1- CONSTITUIÇÃO FEDERAL/constituicao_federal_1988.txt` |
| SHA-256 | `d9f3d6b92ffd524c26a73e311f8c7daa4bf31772193d6d24932acff29c4c2da4` | `3100e09700b1c0ce4ba97e30dc9978d31e5ec645f1ae03f437d7212f41d2a7a2` |
| Origem | Planalto, compilado com redações históricas; fonte da `CF_SEGMENTADA_V2` e do motor de referências V2 | Senado, compilação monovigente (catálogo mestre `CF88`) |
| ADCT | **sim** (a partir da linha 6825) | **não contém ADCT** |
| Encoding | UTF-8, CRLF | UTF-8, com cabeçalho LEX MACHINA |
| Estrutura física | Um dispositivo por linha: `Art. 1º …`, `§ 1º …`, `Parágrafo único. …`, `I - …`, `a) …`. Redações antigas repetem o rótulo antes da vigente. Alguns incisos vêm sem travessão (`I as ações…`, inclusive os **vigentes** do art. 114). Há cabeçalhos TÍTULO/CAPÍTULO/SEÇÃO/SUBSEÇÃO com título nominal. A fórmula de encerramento aparece antes do ADCT e no fim | `Art.` numa linha e o número na seguinte; a palavra "caput" aparece quebrada em linhas próprias; só a redação vigente |

**Comparação estrutural entre as duas fontes:**

- Todo alvo presente no texto do Senado existe no índice do `cf.txt` (0 faltantes).
- O `cf.txt` tem 76 rótulos a mais no corpo da CF, que aparecem só nas redações históricas (ex.: `CF88:ART.102:PAR.UNICO`). Isso é indicativo, não prova de vigência.

**Achado de produto:** o texto que vai para o SD **não tem ADCT**.

## 2. Esquemas de identidade encontrados

| Esquema | Formato | Onde | Decisão |
|---|---|---|---|
| `chave_dispositivo` / `device_id` | `CF88:ART.37:PAR.6:INC.I:AL.a`, `ADCT:ART.5`, `PAR.UNICO`, `ART.103-A` | `CF_SEGMENTADA_V2` (3.461), toda a V2 (Engine, benchmarks, RC1/RC2, checkpoints congelados) | **Reutilizado como `target_id`** |
| `norma_id` | `CF88`, `CC2002`, `CPC2015` … (72) | `updater/catalogo_mestre_vademecum.json` | Reutilizado como namespace |
| Campos com pipe (SD) | `CF88\|5\|\|XLIII\|` | `REL_LOOKUP`/`RELACOES`/`JUR_LOOKUP.IDX` | Conversores `from_pipe_fields`/`to_pipe_fields` |
| Chave de contexto do firmware | `artigo\|paragrafo\|inciso\|alinea`, **sem norma** | `chaveContextoAtual()` | Explica a colisão do ADCT com o corpo principal |
| Campos com dois-pontos (jurisprudência) | `STF:RG:1015:CF88:1:-:III:-` | `JURISPRUDENCIA.IDX` | Conversor `from_colon_fields` |
| `work_id` / `evidence_id` | obra / evidência | curadoria | Não são identidade de dispositivo |

**Defeitos da chave V2 corrigidos pela extensão:**

1. **Sem sufixo em parágrafo/inciso.** O gerador V2 guardava só a "última redação" por chave, e com isso **12 chaves V2 foram colapsadas silenciosamente**. Exemplo: `CF88:ART.40:PAR.4` guardava o texto do `§ 4º-C`; `CF88:ART.92:INC.I` guardava "A o Conselho Nacional de Justiça".
2. **Artigo = texto do caput.** Não havia como referenciar "o artigo inteiro" separado de "só o caput".
3. **Sem alvo raiz** `CF88`/`ADCT`.
4. **Incisos sem travessão ignorados**, inclusive os 9 incisos vigentes do art. 114.

Compatibilidade: **3.461/3.461** chaves V2 continuam válidas e presentes no índice.

## 3. Gramática final (`LEGAL_TARGET_ID/target_id.py`)

```
target_id := NS | NS ":ART." ART [ ":CAPUT" | [":PAR." PAR] [":INC." INC [":AL." AL]] ]
NS  := [A-Z][A-Z0-9]{1,15}  (registrado: 72 ids do catálogo mestre + subnamespaces de namespaces.json)
ART := [1-9][0-9]{0,3} ("-"[A-Z])?          PAR := [1-9][0-9]{0,2} ("-"[A-Z])? | "UNICO"
INC := romano canônico ("-"[A-Z])?          AL  := [a-z] ("-"[A-Z])?
```

- **Artigo e caput são alvos diferentes.** `CF88:ART.37` é o artigo como unidade; `CF88:ART.37:CAPUT` é só o caput.
- **Incisos do caput mantêm a forma V2** (`CF88:ART.37:INC.XXI`), mas o pai deles é `CF88:ART.37:CAPUT`. A forma `…:CAPUT:INC.I` é rejeitada (`NON_CANONICAL`).
- **ADCT é namespace próprio**, filho de `CF88`: `ADCT:ART.5` → `ADCT` → `CF88`. A forma `CF88:ADCT:…` é rejeitada (`NESTED_NAMESPACE`).
- **O pai é apenas estrutural:** AL → INC → PAR ou CAPUT → ART → NS → norma-pai. Não há herança jurídica.
- **Funções:** `parse_target_id`, `format_target_id`, `parent_target_id`, `validate_target_id`, `ancestors`, `normalize_*_label` (`1º`/`1o`/`1`, `§ 6º`/`§6º`/`§ 6o`/`§ 6`, `Parágrafo único`, `a)`), conversores e `roman_to_int`.
- **Fail-closed:** qualquer entrada inválida gera `TargetIdError(code)`.
- **Não normalizado de propósito:** "primeiro" por extenso não é convertido.

**Parser (`LEGAL_TARGET_ID/structure_parser.py`).** É genérico e configurado por `namespaces.json` e `--end-marker`, sem `if norma == CF`. Regras:

- O sufixo só existe colado ao número (`§ 4º-A`). `§ 4º - Será` é travessão, não sufixo.
- O travessão separador exige espaço depois. Por isso `I-A o Conselho` é o inciso I-A, e não o inciso I.
- Um romano sem travessão só vira inciso se continuar a enumeração do mesmo pai: o próximo número, o mesmo rótulo em redação posterior, ou `I` depois de caput/parágrafo terminado em `:`. Nos demais casos é anomalia, e 3 foram rejeitadas.
- O texto de redações antigas não é atribuído a outro dispositivo.

## 4. Índice da CF (`LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json`)

| Medida | Valor |
|---|---:|
| Total de targets | **3.956** |
| Normas (CF88) / namespaces (ADCT) | 1 / 1 |
| Artigos (CF 276 + ADCT 148) | 424 |
| Caputs | 424 |
| Parágrafos (CF 753 + ADCT 286) | 1.039 |
| Parágrafos únicos (CF 68 + ADCT 37) | 105 |
| Incisos (CF 1.303 + ADCT 272) | 1.575 |
| Alíneas (CF 318 + ADCT 69) | 387 |
| Targets do ADCT (namespace inteiro) | 961 |
| **TARGET_ID_DUPLICATES** | **0** |
| Rótulos repetidos (redações históricas do mesmo alvo) | 450 (a última ocorrência é a vigente) |
| Incisos sem travessão aceitos por sequência / rejeitados | 54 / 3 |
| Dispositivos com sufixo recuperados em relação à V2 | 23 (ex.: `CF88:ART.40:PAR.4-A/B/C`, `CF88:ART.92:INC.I-A`, `CF88:ART.109:INC.V-A`, `ADCT:ART.107:PAR.6-A`) |
| **TARGET_INDEX_SHA256** (lista ordenada de ids, unida por LF) | `96ab692a6f3b16f686974556683a1e2b2db69115efc2a6c0030e65f7ed14b5c0` |
| SHA-256 do arquivo do índice | `63a93c4477ec9e440c6ee279427fd33d59cc1835279e2501c2d3bf7098e7a2c2` |
| Determinismo | 2 execuções, arquivo byte-idêntico |

Cada entrada tem:

- `target_id`, `parent_id`, `kind`, `namespace`, `norma_id`;
- `article`, `paragraph`, `inciso`, `alinea`;
- `occurrences` (linhas) e `line_start`;
- `preview` de 100 caracteres e `text_sha256_current`.

O índice não duplica a CF.

**Casos pedidos:**

| Dispositivo | `target_id` | Pai |
|---|---|---|
| Art. 37 (artigo) | `CF88:ART.37` | `CF88` |
| Art. 37, caput | `CF88:ART.37:CAPUT` | `CF88:ART.37` |
| Art. 37, § 6º | **`CF88:ART.37:PAR.6`** (linha 1378, "As pessoas jurídicas de direito público…") | `CF88:ART.37` |
| Art. 37, § 10 | **`CF88:ART.37:PAR.10`** (linha 1392, "É vedada a percepção simultânea…") | `CF88:ART.37` |
| Art. 37, XXI | `CF88:ART.37:INC.XXI` | `CF88:ART.37:CAPUT` |
| Art. 60, § 4º, IV | `CF88:ART.60:PAR.4:INC.IV` (incisos I–IV) | `CF88:ART.60:PAR.4` → `CF88:ART.60` → `CF88` |
| ADCT, art. 5º | **`ADCT:ART.5`** (§§ 1–5) | `ADCT` → `CF88` (≠ `CF88:ART.5`) |
| Art. 5º | `CF88:ART.5` (79 incisos, até LXXIX; §§ 1–4) | `CF88` |

## 5. Testes (`LEGAL_TARGET_ID/tests/test_target_id.py`): 18/18 OK

**Positivos:**

- corpus de 32 ids com tipo, pai e ida e volta `parse(format(t)) == t`, cobrindo arts. 1, 5, 7, 37, 40, 60, 92, 103-A, 109, 114, 150 e 225 e o ADCT (arts. 5, 107 e 120);
- existência real de todos esses ids na CF;
- todo pai existe;
- artigo ≠ caput;
- ADCT separado;
- normalização de rótulos;
- conversores;
- registro guiado pelo catálogo (`CC2002`, `CPC2015`, `CP1940`, `CPP1941`, `CTN1966`, `CDC1990`);
- fixture com variantes (`Art. 1º`, `Art 2`, `ART. 3º`, `art. 4o`, `Art.`+número na linha seguinte, `§ 4º-A`, `§ 4º - Será`, `II-A -`, `Art. 60.Colado`, redação repetida, encerramento, ADCT);
- sequência de incisos sem travessão;
- determinismo;
- a CF inteira é superconjunto das chaves V2.

**Negativos:** 30 ids inválidos, todos rejeitados com o código esperado:

- norma desconhecida, artigo inválido ou com zero à esquerda;
- namespace minúsculo ou aninhado (`CF88:ADCT:ART.5`);
- segmento vazio, parágrafo vazio ou `06`;
- inciso malformado (`IIII`, `21`, minúsculo);
- alínea sem inciso;
- ADCT malformado;
- path (`updater/saida/cf.txt`), espaço, `º`, não-ASCII;
- ordem de níveis errada;
- `CAPUT` não terminal.

## 6. Cobertura das referências atuais

Diagnóstico somente leitura; nada foi migrado.

| Base | Total | Mapeamento automático (subdivisão) | Nível de artigo (precisa de regra) | Ambíguo (colisão V2) | Dispositivo inexistente |
|---|---:|---:|---:|---:|---:|
| RC2 V2 (105 referências/rotas, 101 vínculos únicos) | 105 | 78 | 27 | 0 | 0 |
| RC1 V2 | 125 | 93 | 32 | 0 | 0 |
| Todos os `device_id` distintos da V2 | 441 | 331 | 107 | 3 | 0 |
| `REL_LOOKUP` (relações do SD, 2E6) | 41 | 38 | 3 | 0 | 0 |
| `JUR_LOOKUP` J4_6 (lido do archive, sem alterar) | 178 | 133 | 35 | 0 | 10 |
| IDs de jurisprudência J4_6 | 296 | 220 | 64 | 0 | 12 |
| **Total** | **1.186** | **893 (75,3 %)** | **268 (22,6 %)** | **3 (0,3 %)** | **22 (1,9 %)** |

- **Nível de artigo:** referências `CF88:ART.N`. A V2 avaliou o texto do caput, então falta decidir por regra se viram ARTIGO (unidade) ou CAPUT.
- **Ambíguas:** `CF88:ART.239:PAR.3`, `CF88:ART.40:PAR.4` e `CF88:ART.93:INC.VIII`, cujo texto V2 veio de um dispositivo colapsado.
- **Inexistentes:** os índices de jurisprudência apontam dispositivos que **não existem na CF** (ex.: `CF88:ART.1:PAR.1`, `ART.3:PAR.3`, `ART.20:PAR.3`, `ART.25:INC.I/II`). A gramática detecta esses erros de dados.
- **Incisos históricos do § 4º do art. 40** (redação da EC 47/2005, citados pelo `REL_LOOKUP` para a LC 144/2014): viraram alvos reais pela regra de sequência.

## 7. ESP32

| Medida | Valor |
|---|---|
| Comprimento máximo | 35 caracteres (`ADCT:ART.120:PAR.UNICO:INC.III:AL.a`) |
| Média / mediana | 19,48 / 18 |
| Targets na CF | 3.956 |
| Bytes de id somados | 77.070 |
| Colisões FNV-1a de 32 bits | 0 |

- **Hoje:** o firmware usa a chave `artigo|paragrafo|inciso|alinea` **sem norma**, e por isso o ADCT colide com o corpo da CF. O `target_id` resolve isso pelo namespace.
- **Futuro:** índice ordenado no SD com busca binaria, ou hash de 32 bits com verificação da string. Não é preciso manter todos os ids em RAM. `to_pipe_fields` preserva a compatibilidade com os IDX atuais.

## 8. Generalização

- Os namespaces vêm do catálogo mestre (72 normas).
- O ADCT é só um subnamespace declarado em `namespaces.json`.
- O parser não tem regra específica da CF; o marcador de encerramento é passado por parâmetro.

A aplicação às outras 71 normas **não** foi feita.

## 9. Arquivos

| Arquivo | Conteúdo |
|---|---|
| `LEGAL_TARGET_ID/target_id.py` | Gramática central |
| `LEGAL_TARGET_ID/namespaces.json` | Subnamespace ADCT; catálogo mestre como fonte das normas |
| `LEGAL_TARGET_ID/structure_parser.py` | Parser estrutural genérico |
| `LEGAL_TARGET_ID/build_target_index.py` | Gerador do índice |
| `LEGAL_TARGET_ID/analyze_reference_coverage.py` | Diagnóstico de cobertura |
| `LEGAL_TARGET_ID/tests/test_target_id.py` | Testes |
| `LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json` | Índice derivado para inspeção; não vai para o SD |
| `CLEANUP_AUDIT/CF_REFERENCE_TARGET_ID_ANALYSIS.json` / `.md` | Este relatório |

Não foram tocados: archives, ledger protected545, relatórios antigos, Shadow, Registry/Lock D05, firmware, SD, `CF_SEGMENTADA_V2` e a V2 congelada.

## 10. Recomendação para CF-REF-A2 (não iniciada)

1. **Decidir a regra ARTIGO × CAPUT** para as 268 referências de nível de artigo. Sugestão: as vindas da V2 (que avaliou o texto do caput) → `…:CAPUT`, salvo marcação humana de "artigo inteiro".
2. **Revisar manualmente** as 3 referências ambíguas por colisão e os 22 dispositivos inexistentes da jurisprudência J4_6.
3. **Congelar o `CF88_TARGET_INDEX`** como referência estrutural versionada e usar `validate_target_id` como gate obrigatório em qualquer novo vínculo (Referências, Correlatas, Jurisprudência, ENTENDA).
4. **Decidir a fonte textual do SD.** O texto monovigente atual não tem ADCT; o índice estrutural vem do `cf.txt`, que tem histórico.
5. **Planejar a adoção no firmware:** chave com namespace (ou `to_pipe_fields` com a norma).
