# DEVICE DATA CONTRACT V1 — LEX MACHINA (ESP32-S3 + microSD)

> **Atualização V1-A2B.**
>
> - **Texto exibido pelo runtime V1:** `/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt` (CF + ADCT monovigentes oficiais, UTF-8, LF). São exatamente os bytes indexados.
> - **`CF88_TARGETS.IDX` v3:** 3.810 targets do runtime. O cabeçalho traz `TARGET_ID_VERSION` e `SOURCE_SHA256`, e `LEGAL_STATUS` vem da compilação monovigente: `(Revogado)`/`(Suprimido)` dá REVOKED; os demais são CURRENT.
> - **`CF88_TEXT_MAP.IDX` v2:** `RUNTIME_STATUS|RUNTIME`, `SOURCE_NAME|CF88_RUNTIME.txt`, `NORMALIZATION_VERSION` e uma linha por target na ocorrência canônica.
>   - O firmware usa o mapa **somente** se o **tamanho E o sha256** do arquivo exibido coincidirem com o cabeçalho (sha256 calculado uma vez por boot). Caso contrário, **fail closed**.
> - **`LEXV1.VER`:** `RUNTIME_CF_PATH`, `RUNTIME_CF_BYTES`, `RUNTIME_CF_SHA256` e `REFERENCE_ENGINE`.

Status: **CANDIDATO para revisão humana** (V1-A1; atualizado na V1-A2).

> **Atualização V1-A2**
>
> - O ENTENDA no pacote passa a ter **163 explicações**: 154 dos Batches 01–03 mais 9 pilotos aprovados. O escopo agora é `CF88_ARTS_1_24_PLUS_APPROVED_PILOTS`.
> - `TEXT_MAP` v2 traz no cabeçalho `TARGET_ID_VERSION`, `RUNTIME_STATUS`, `SOURCE_BYTES`, `SOURCE_SHA256`, `RECORD_COUNT` e `NAMESPACE_START_ADCT`.
>   - O firmware **só** usa o mapa com `RUNTIME_STATUS|RUNTIME` e `SOURCE_BYTES` igual ao tamanho do arquivo exibido; o sha256 é conferido pelo updater. Caso contrário, **fail closed**.
>   - O mapa atual é `LEGACY_STRUCTURAL_NOT_RUNTIME` porque o `CF88_RUNTIME` não foi resolvido (`CANONICAL_ADCT_SOURCE_NOT_RESOLVED`, ver `CF88_RUNTIME_SOURCE_AUDIT.md`).
> - `LEXV1.VER` v2 acrescenta `ENTENDA_PILOTS`, `TEXT_MAP_SOURCE_BYTES`, `TEXT_MAP_RUNTIME_STATUS` e `RUNTIME_CF`.
> - A implementação de referência em C++ está em `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_device_v1.h`. Nenhum firmware implementa este contrato ainda. Os formatos abaixo são os
**formatos reais** produzidos pelos motores aprovados (Reference Engine e ENTENDA). O overlay só os empacota e acrescenta dois
índices estruturais derivados do índice de targets aprovado.

## 1. Identificação da norma

- Cada norma tem um `norma_id` curto e estável: `CF88`. O ADCT é o namespace `ADCT`, dentro do mesmo texto.
- A gramática é a de `LEGAL_TARGET_ID/target_id.py`. O firmware não valida a gramática; ele só compara strings.

## 2. Artigo/dispositivo → target_id

`NORMA:ART.n[:PAR.n|:PAR.UNICO][:INC.<romano>][:AL.<letra>]`

- O artigo aceita sufixo de letra (`ART.29-A`). O caput tem target próprio (`ART.n:CAPUT`), mas as camadas usam a chave do artigo.
- Tamanho máximo atual: 35 bytes (`target_id_length.max` do índice). Buffer recomendado: **48 bytes**.
- Conversão da tupla do firmware (`ContextoJuridicoAtivo`) para target_id:
  - `"unico"` → `PAR.UNICO`;
  - os demais campos entram literalmente, na ordem art → par → inc → al.

  Implementação de referência: `Device.from_context` em `tools/device_lookup_simulator.py`.

## 3. Posição atual → target_id

Ver `TARGET_RESOLUTION_STRATEGY.md`. Resumo:

1. **Primária:** `CF88_TEXT_MAP.IDX`. Busca-se a maior linha com `OFFSET <= offset da linha central`.
   - Só vale quando o arquivo aberto tem exatamente o `SOURCE_BYTES` (e, no diagnóstico, o `SOURCE_SHA256`) do cabeçalho.
   - O namespace sai do cabeçalho `#NAMESPACE_START_<ns>|<offset>`.
2. **Fallback:** parser de contexto em runtime (`contexto_juridico.h`, já validado no aparelho) seguido da conversão do item 2.
3. **Validação:** o target_id obtido é procurado em `CF88_TARGETS.IDX`. Se não existir, nenhuma camada é oferecida.

## 4–6. Consultas (todas por busca binária no arquivo)

| Camada | Lookup | Payload | Resolução |
|---|---|---|---|
| Referências | `REF_LOOKUP.IDX`: `TARGET_ID\|OFFSET\|QUANTIDADE` | `REF_PAYLOAD.IDX`: seek(OFFSET) e leitura de QUANTIDADE linhas `TARGET_ID\|TIPO\|VISIBILIDADE\|STATUS\|REFERENCE_ID\|SOURCE_ID\|LABEL` | direta; `TIPO` ∈ `CORRELATA`, `JURISPRUDENCE`, `WORK_REFERENCE`; esconder `HISTORICAL_HIDDEN_BY_DEFAULT` por padrão |
| ENTENDA | `ENTENDA_LOOKUP.IDX`: `TARGET_ID\|OFFSET\|BYTES\|EXPLANATION_ID\|VALIDITY\|FRESHNESS\|REVIEW\|RESOLUTION` | `ENTENDA_PAYLOAD.DAT`: seek(OFFSET) e leitura de BYTES | `RESOLUTION` = `DIRECT` ou `COVERED_BY_BLOCK` |

**Resolução de BLOCK.** Cada target coberto tem linha própria no lookup, com o **mesmo** `OFFSET`/`BYTES` do âncora, e o payload
não é duplicado. O âncora vem da linha `T|` do payload; o título, da linha `D|`. Exemplo: `CF88:ART.5:INC.V` resolve para
`CF88:ART.5:INC.IV`, com o título "Art. 5º, incisos IV, V, IX e XIV — Liberdade de expressão e informação". Não há segundo salto.

**Layout do payload ENTENDA (versão 2).**
- Bloco `@<EXPLANATION_ID>`.
- Linhas de metadados `K|V`:
  - `T` alvo;
  - `K` tipo/papel/autonomia;
  - `V` vigência;
  - `R` revisão;
  - `F` frescor;
  - `H` hash;
  - `D` título;
  - `C` contexto;
  - `B` cobertos;
  - `X` ordem de exibição;
  - `N` número de referências;
  - `W` avisos;
  - `Z|TIME_SENSITIVE|data`.
- Seções `#O QUE DIZ`, `#O QUE SIGNIFICA`, `#EXEMPLO PRÁTICO`, `#ATENÇÃO`, `#PALAVRAS DIFÍCEIS`, `#CAMADAS EXTERNAS` e `#NOTAS TEMPORAIS`, terminando em `@END`.
- Os metadados vêm antes da primeira seção, então o firmware pode ler só o começo do bloco para montar a lista.

## 7. Quais camadas existem para um target

Uma única busca em `CF88_TARGETS.IDX` (`TARGET_ID|KIND|LEGAL_STATUS|FLAGS`) responde. `FLAGS` tem 6 posições fixas:

| Pos. | Valores | Significado |
|---|---|---|
| 0 | `E` / `B` / `-` | ENTENDA direto / coberto por BLOCK / sem ENTENDA |
| 1 | `C` / `-` | correlatas visíveis |
| 2 | `J` / `-` | jurisprudência visível |
| 3 | `W` / `-` | referências de obra visíveis |
| 4 | `R` / `-` | existe linha no `REF_LOOKUP` (inclui históricas ocultas) |
| 5 | `X` / `-` | ENTENDA com camada externa ou nota temporal |

`LEGAL_STATUS` ∈ `CURRENT`, `REVOKED`, `HISTORICAL_ONLY` ou `UNKNOWN` (modelo de dois eixos do ENTENDA; o ADCT fica `UNKNOWN`).

## 8–11. Ausências e falhas

- **Target sem ENTENDA.** Não há linha no lookup (ex.: `CF88:ART.25`). O firmware mostra "sem explicação aprovada".
  - Pode oferecer o ancestral com ENTENDA, rotulado como "contexto do artigo", **nunca** como explicação do dispositivo.
  - ENTENDA existe **somente para CF88 arts. 1 a 24 e para os 9 pilotos aprovados** (arts. 37, 37 §6, 37 §10, 60, 60 §4, 60 §4 IV, 150, 225 e ADCT 10 II).
- **Target sem referências:** não há linha no `REF_LOOKUP`. A camada fica oculta.
- **Target inválido ou desconhecido** (ex.: `CF88:ART.999`): não existe em `CF88_TARGETS.IDX`. Nenhuma camada é oferecida e o texto da Lei Seca continua exibido.
- **Falha segura** (em todos os casos, o leitor da Lei Seca continua funcionando):
  - arquivo ausente;
  - cabeçalho `#LEXMACHINA|<TIPO>|<versão>` com tipo ou versão desconhecidos;
  - `OFFSET + BYTES` fora do arquivo;
  - bloco que não começa por `@<EXPLANATION_ID>` igual ao do lookup;
  - linha maior que o buffer.

  Qualquer um desses casos desativa **só aquela camada** e registra no Serial (`LEXV1: <camada> desativada: <motivo>`).

## 12. Arquivos no SD (overlay novo, não substitui nada)

```
/99_LEX_V1/00_SYS/LEXV1.VER                  versão compacta para o runtime (K|V por linha)
/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json   diagnóstico/updater (o firmware não precisa carregar)
/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX       targets + status + FLAGS
/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX      offset no cf.txt estrutural -> target_id
/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX      cópia byte a byte do Reference Engine aprovado
/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX     idem
/99_LEX_V1/30_ENTENDA/ENTENDA_LOOKUP.IDX     163 explicações aprovadas + linhas de BLOCK
/99_LEX_V1/30_ENTENDA/ENTENDA_PAYLOAD.DAT    idem
```

O cartão legado continua com `/99_RELATIONS_V2`, `/99_JURISPRUDENCIA_V2` e as pastas das normas. O v7.12.0 não lê `/99_LEX_V1`.

## 13–17. Formato, versionamento, endianness, offsets e integridade

- **Codificação.** Todos os índices são texto UTF-8 com LF, campos separados por `|` e cabeçalhos iniciados por `#`. A primeira linha é sempre `#LEXMACHINA|<TIPO>|<versão>`.
  - Versões atuais: `TARGETS` 2, `TEXT_MAP` 2, `REF_LOOKUP` 1, `REF_PAYLOAD` 1, `ENTENDA_LOOKUP` 2, `ENTENDA_PAYLOAD` 2, `DEVICE_VERSION` 2.
- **Ordenação.** A ordem é **bytewise** pelo primeiro campo, que é o contrato da busca binária (`CF88:ART.100` < `CF88:ART.12`). No `TEXT_MAP`, o offset tem 10 dígitos com zeros à esquerda, então a ordem de string é igual à numérica.
- **Endianness.** Não se aplica: nenhum formato é binário. Os números são decimais ASCII.
- **Offsets.** Absolutos, em bytes, contados a partir do início do próprio arquivo de payload (incluindo o cabeçalho). `BYTES`/`QUANTIDADE` delimitam a leitura.
- **Tamanhos máximos medidos:**

  | Item | Tamanho |
  |---|---|
  | Linha de índice | 119 B |
  | Linha do `REF_PAYLOAD` | 193 B |
  | Bloco ENTENDA (teto do contrato: 6.144 B) | 3.097 B |
  | Título | 139 B |
  | Referências por target | 10 |
  | Linha de seção do ENTENDA | 718 B (quebrar na UI) |

- **Integridade.** O `LEX_DEVICE_MANIFEST.json` traz sha256 e tamanho de cada arquivo, e o `build_id` deriva desses hashes.
  - `LEXV1.VER` repete `BUILD_ID`, `GIT_COMMIT`, `ENTENDA_COUNT` e `TEXT_MAP_SOURCE_SHA256`.
  - O firmware compara o tamanho dos arquivos com o `LEXV1.VER` no boot. A verificação de hash fica no updater, no PC.

## 18. Compatibilidade futura

- **Nova norma:** novos arquivos `<NORMA>_TARGETS.IDX` e `<NORMA>_TEXT_MAP.IDX`. Lookups de ENTENDA e referências continuam únicos, porque o target_id já traz a norma.
- **Nova versão de formato:** incrementar a versão no cabeçalho. O firmware recusa versões desconhecidas e cai em modo seguro.
- **Novos lotes do ENTENDA:** o builder recalcula o pacote inteiro de forma determinística, e a contagem sai do manifest.
- **Formato binário compacto:** se medições no hardware exigirem, criar um formato novo, mantendo este como referência e com teste de equivalência.
