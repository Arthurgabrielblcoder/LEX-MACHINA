# CF88_RUNTIME_SOURCE_AUDIT (V1-A2, 2026-09-29)

> **Atualização V1-A2B: RESOLVIDO.** Com a decisão humana, o ADCT (Senado, norma 604119, Compilação Monovigente) foi ingerido pelo pipeline oficial; ver `ADCT_SOURCE_INGESTION_REPORT.md`.
>
> O `CF88_RUNTIME.txt` foi gerado por `updater/exportar_cf88_runtime.py`, a partir apenas das fontes travadas, com `HEADER_NORMALIZATION_RULE_V1` (ver `HEADER_NORMALIZATION_RULE.md`). O arquivo tem 587.133 B, 4.537 linhas e sha256 `7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a`; o ADCT começa no byte 429.242.
>
> Os targets, o mapa e os offsets foram reconstruídos sobre esses bytes. O conteúdo abaixo registra a auditoria da A2.

Objetivo: definir o texto que o firmware vai **exibir** e sobre o qual índice, mapa, offsets e hashes serão gerados. O runtime deve ser a CF vigente + o ADCT vigente, sem redações históricas misturadas.

**Resultado:** `CANONICAL_ADCT_SOURCE_NOT_RESOLVED`. O `CF88_RUNTIME` **não foi criado**.

## Fontes encontradas

| | `cf.txt` legado (estrutural) | `updater/saida` (operacional) |
|---|---|---|
| Caminho | `updater/backup_catalogos/catalogo_mestre_20260913_145217/1- CONSTITUI#U00c7#U00c3O FEDERAL/cf.txt` | `updater/saida/1- CONSTITUIÇÃO FEDERAL/constituicao_federal_1988.txt` (pasta ignorada pelo Git) |
| sha256 | `d9f3d6b92ffd524c26a73e311f8c7daa4bf31772193d6d24932acff29c4c2da4` | `3100e09700b1c0ce4ba97e30dc9978d31e5ec645f1ae03f437d7212f41d2a7a2` |
| Bytes / linhas | 928.009 / 8.634 | 429.832 / 3.740 |
| Encoding / fim de linha | UTF-8 sem BOM / **CRLF** | UTF-8 sem BOM / **LF** |
| Proveniência | catálogo mestre de 13/09/2026 (texto consolidado com anotações de alteração) | "Senado Federal – Compilação Monovigente" (`legis.senado.leg.br/norma/579494/publicacao/16434817`), gerado por `updater/main.py` (`COMPILACAO_MONOVIGENTE_SENADO`), atualizado em 14/09/2026 |
| ADCT | **sim**: o cabeçalho "ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS" está no byte 661.181, o mesmo `NAMESPACE_START_ADCT` do índice aprovado | **não**: termina no art. 250 e nas assinaturas |
| Redações históricas | **sim**: 577 marcas "Redação dada", 1.413 "Incluído", 77 "(Revogado"; rótulos repetidos (ex.: art. 7º, XII e XXIX em duas versões) | não: é monovigente, restam 36 marcas "(Revogado" em dispositivos revogados |
| Cabeçalhos de artigo | 514 linhas `Art. N` na mesma linha | **todos os 276 partidos** (`Art.` sozinho e o número na linha seguinte) |
| Vigência no índice aprovado | base do `CF88_TARGET_INDEX` (3.956 targets); o ADCT fica `UNKNOWN_VALIDITY` | usado pelo ENTENDA para frescor/vigência do texto CF |

## Respostas da auditoria

1. **Origem da CF em `updater/saida`.** `updater/main.py` baixa a Compilação Monovigente oficial do Senado (norma 579494) e extrai o corpo com `_extrair_corpo_senado()`. Não interpreta revogações: a consolidação é do órgão oficial.
2. **Fonte atual separada do ADCT.** Não existe no repositório. O pipeline só registra a norma 579494 (CF), e a publicação usada termina nas assinaturas.
3. **ADCT vigente no repositório.** Não. O único texto do ADCT é o do `cf.txt` legado, **com redações históricas misturadas**, e seus targets estão `UNKNOWN_VALIDITY` no índice aprovado. Os caches do updater (`cache_lexdata_*`) só citam o ADCT, sem conter seu texto.
4. **O updater gera CF+ADCT consolidado?** Não. Não há registro do ADCT no catálogo do pipeline.
5. **Fonte oficial armazenada?** Só a da CF (a saída do Senado). O ADCT existe em fonte oficial on-line: LexML `urn:lex:br:federal:ato.disposicoes.constitucionais.transitorias:1988-10-05;1988` e a compilação do Senado. Ele **não está armazenado nem ingerido**.

## Por que não foi gerado agora

- Filtrar as redações históricas do ADCT a partir do `cf.txt` legado seria **edição jurídica por heurística**: a vigência do ADCT não foi resolvida pelo motor. Isso é proibido.
- Baixar agora o ADCT e compô-lo seria uma **ingestão nova**. Isso exige estender o pipeline oficial (catálogo e extrator), com revisão.
- Mesmo a CF operacional precisaria de composição determinística antes do runtime, por causa dos cabeçalhos partidos. Sem isso, o parser do firmware não reconhece nenhum artigo desse arquivo.

## Estado aplicado ao pacote

- `CF88_TEXT_MAP.IDX` v2 continua vinculado ao `cf.txt` legado, só para auditoria, com `#RUNTIME_STATUS|LEGACY_STRUCTURAL_NOT_RUNTIME`. O firmware candidato **recusa** o mapa (fail closed). `LEXV1.VER` e o manifest registram `RUNTIME_CF|CANONICAL_ADCT_SOURCE_NOT_RESOLVED`.
- O índice anterior permanece para auditoria e **não** é usado como runtime.

## Caminho proposto (V1-A3, com autorização)

1. Registrar o ADCT no catálogo do updater como norma própria, com a mesma via oficial do Senado (Compilação Monovigente) ou a do LexML. Guardar a resposta bruta com sha256 e a URL.
2. Exportador determinístico `CF88_RUNTIME.txt`:
   - CF monovigente, seguida de um separador fixo e do ADCT monovigente;
   - UTF-8 sem BOM, LF;
   - junção de `Art.` com o número por regra mecânica (sem alterar palavras);
   - cabeçalho de proveniência em linhas `#`.
3. Reindexar os targets **sobre esses bytes** com o motor de target_id, publicar o `TEXT_MAP` com `RUNTIME_STATUS|RUNTIME` e revalidar Reference Engine e ENTENDA contra os novos targets (sem mudança de significado).
