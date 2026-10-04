# ARTICLE_SEARCH.IDX — generalização para o acervo completo

Status técnico: **READY para revisão host; nenhuma implantação física executada**. Baseline protegida: commit `10e199f`, tag
`lex-device-v1-batch04-run3-physical-approved-2026-10-03`.

## Resultado reproduzido

O localizador do Updater descobriu 72/72 normas no backup somente-leitura do último SD validado. Foram aceitas 71 fontes e gerados
71 índices: `KEEP=2` (CF88 e CC2002), `REBUILD=0`, `ADD=69`, `REMOVE=0`, `BLOCKED=1` (MARIA2006). CF88 e CC2002 são cópias binárias
idênticas aos artefatos físicos aprovados: respectivamente SHA-256 `56e437a0c9cebb113c47f6a7b100ee64363c63207a647eca0456e86d6db27fae`
e `674c9971925c29aaca9685fb2d0b9515fe87e4072d644858ea27495c327d3a68`.

O conjunto válido contém 12.896 records, 162.720 B de índices e catálogo de 4.040 B; payload de deploy = 72 arquivos/166.760 B.
Incluindo manifesto e relatório host, o staging contém 74 arquivos/328.494 B. Índice médio 2.291,8 B, mediana 1.072 B, mínimo
160 B, máximo 25.036 B (`CC2002`). Há 71 namespaces de norma únicos. Somente um índice fica em PSRAM: máximo e simultâneo
25.036 B. O catálogo reside no SD, não é embutido em flash e não é retido em PSRAM; o leitor usa buffers locais de 64 B e 56 B,
além do contexto SHA e até oito descritores lógicos de candidato, com pico de um arquivo aberto.

## Auditoria estrutural

`test_full_corpus_article_indexes.py` validou todos os 12.896 records: header/body SHA-256, vínculo por tamanho+SHA da fonte,
namespace, número, suffix, occurrence, offset dentro do arquivo e texto estrutural no offset. Para cada norma, validou primeiro,
intermediário e último record, mais suffixes, repetições e casos especiais. A caminhada indexada por ocorrência é idêntica ao
parser estrutural linear estrito em 71/71 índices; `INDEX_ERROR=0`.

Comparação em três níveis:

- parser estrutural estrito/corpus ↔ índice: PASS, zero divergências;
- busca linear legacy fora do conjunto estrutural: 1.708 `LEGACY_FALSE_POSITIVE`;
- headings estruturais não alcançados pelo legacy: 1.858 `LEGACY_FALSE_NEGATIVE`;
- fontes com blocos alteradores/citações incorporados: registradas como `AMBIGUOUS_SOURCE`, não usadas para culpar o índice.

Foram medidos 77 headings fora de ordem em 13 normas: LRP1973 18, LIC2021 17, LBI2015 11, HEDIONDOS1990 7, RJU1990 5,
CPC2015 4, CUSTEIO1991 3, ORCRIM2013 3, PARTIDOS1995 3, IDOSO2003 2, RPS1999 2, CLT1943 1 e LPI1996 1. A inspeção mostrou
que o retorno de numeração ocorre após blocos de alteração legislativa que contêm dispositivos de outras leis (por exemplo, LIC
retorna aos arts. 179–194 após transcrições penais; LBI retorna aos arts. 117–127 após alterações incorporadas). Classificação:
`AMBIGUOUS_SOURCE`, explicitamente testada e contabilizada. O índice preserva a busca estrutural do texto operacional e todas as
ocorrências; não reclassifica silenciosamente esses trechos como verdade canônica de outra norma. Uma futura segmentação semântica
de blocos alteradores deve ter schema/namespace próprios e não foi inferida por heurística nesta missão.

As opções `remission_guard` e `heading_variants` permanecem desligadas por padrão. No modo corpus, testes cobrem `Art . 2º`,
`Art. 22A`, `Art. 4`/`o`/`-A`, `Art. 21`/`7`, remissões por palavra e citação embrulhada; lowercase/remissões não viram headings.

Artigos acima de 999: `CC2002` (1.031 chaves acima de 999, máximo 2.046), `CPC2015` (73, máximo 1.072) e `LBI2015`
(um caso, `1783-A`, vindo de bloco alterador e portanto `AMBIGUOUS_SOURCE`). Foram verificados 999/1000 quando presentes,
primeiro/intermediário/último alto. Há 1.003 records com suffix (966 chaves distintas). Exemplos por norma:

- ABUSO2019 15-A; ALIENPAR2010 8-A; ARBIT1996 22-A/22-B/22-C; ARMAS2003 7-A/11-A/21-A/34-A.
- BENEF1991 21-A/27-A/29-A; CBA1986 36-A/38-A/86-A; CC2002 48-A/49-A/69-A; CDC1990 42-A/54-A/54-B.
- CE1965 23-A/233-A/326-A; CIDADE2001 34-A/42-A/42-B; CLT1943 10-A/11-A/29-A; COND1964 30-F/31-A/31-B.
- COOP1971 43-A/88-A; CP1940 91-A/121-A/121-B; CPC2015 699-A/1035-A; CPP1941 3-A/3-B/3-C.
- CRIMAMB1998 38-A/40-A/50-A; CTN1966 18-A/35-A/82-A; CUSTEIO1991 22-A/22-B/25-A; CVM1976 10-A/17-A/21-A.
- DROGAS2006 7-A/8-A/8-B; ECA1990 8-A/11-A/14-A; ELEICOES1997 6-A/16-A/16-B; FALENCIA2005 6-A/6-B/6-C.
- FGTS1990 6-A/6-B/9-A; FINPUB1964 39-A; INELEG1990 26-A/26-B/26-C; INQUIL1991 54-A; JEC1995 12-A/90-A.
- LAI2011 8-A/8-B; LAVAGEM1998 4-A/4-B/10-A; LBI2015 2-A/62-A/73-A; LDA1998 98-A/98-B/98-C.
- LEP1984 9-A/18-A/21-A; LGPD2018 55-A/55-B/55-C; LIA1992 8-A/17-A/17-B; LIC2021 44-A/184-A/337-E.
- LPI1996 71-A/229-A/229-B; LRF2000 14-A/26-A/41-A; LRP1973 7-A/70-A/94-A; MINER1967 6-A/43-A/47-A.
- ORCRIM2013 3-A/3-B/3-C; PAF1999 49-A/49-B/49-C; PARTIDOS1995 11-A/15-A/22-A; PATERN1992 2-A.
- PNMA1981 9-A/9-B/9-C; REFAGR1993 2-A/18-A/18-B; RJU1990 60-A/60-B/60-C; RPEM1994 35-A/39-A/39-B.
- RPS1999 19-A/19-B/19-C; SA1976 4-A/16-A/110-A; SEGUROS1966 24-A/24-B/24-C; SFI1997 26-A/27-A/33-A.
- TEMP1974 4-A/4-B/4-C; TERRA1964 95-A.

Sete ranges coletivos revogados foram detectados e não geraram records artificiais: CC2002 `1.620–1.629` e `1.768–1.773`;
CTN1966 `52–58` e `59–62`; SEGUROS1966 `49–54`, `65–69` e `70–71`.

## MARIA2006

`INDEX_BUILD_BLOCKED`: `15-LEI MARIA DA PENHA/Lei Maria da Penha.txt`, 215.426 B,
SHA-256 `a560439bfa7bbb6cfa77f42578bf1688183c9047004eb022af0a6444af5e775c`. Os primeiros bytes são o wrapper UTF-8
`LEX MACHINA\n...`; na linha 15 aparece a assinatura textual UTF-8 `c3 bf c3 be` (`ÿþ`), seguida de HTML UTF-16 previamente
decodificado como cp1252, com letras separadas (`<h t m l >`). Nenhum `MARIA2006_ARTICLE_SEARCH.IDX` foi produzido.

Existe fonte limpa rastreável em `updater/saida/LEXDATA_V4_BUILD/LEIS/MARIA2006.TXT` (46.666 B, 57 headings), gerada pelo
backend oficial de LEXDATA a partir de `normas.leg.br` (`CURRENT_BINARIO`), mas ela não é ainda a fonte operacional do Updater
unificado. Promovê-la mudaria o corpus jurídico, e por isso não foi misturada ao staging nem ao SD. `MARIA2006_SOURCE_FIX_READY=NÃO`:
fonte candidata identificada, integração autoritativa ainda requer revisão editorial/pipeline.

## Catálogo, loader e incremental

O limite antigo não é do FAT nem do leitor: `LEXV1_ARTIDX_MAX_CANDIDATOS=8` encerra a enumeração após oito nomes
`*_ARTICLE_SEARCH.IDX`, na ordem do diretório. Resultado modelado: 8 carregáveis e 63 inalcançáveis. Scan ilimitado: 71 headers,
6.816 B de header, 75 directory entries, 1.792,1 ms de seleção. Catálogo LXARTCT1: zero headers/directory entries, leitura única de
4.040 B, lookup modelado em 21,2 ms. Hash do texto e carga do índice são medidos à parte; pior hash de fonte modelado 797 ms e
pior carga de índice 41,2 ms.

O catálogo é ordenado deterministicamente por `(source_bytes, source_sha256, norma)` e mapeia para
`<NORMA>_ARTICLE_SEARCH.IDX`. Catálogo válido é autoritativo; ausente/corrompido recua ao scan genérico. Em todos os caminhos, o
índice selecionado ainda valida magic/schema, tamanho+SHA da fonte e SHA do corpo. Mismatch/corrupção/troca de norma falham fechados
e nunca carregam índice errado.

Incremental real/sintético testado: mesma fonte+mesmos bytes = KEEP; fonte alterada = REBUILD; nova = ADD; removida = REMOVE;
erro estrutural = BLOCKED. Também foi corrigido o resumo quando todas as normas ficam bloqueadas. O teste final executou três
gerações completas novas e comparou-as automaticamente: mesmos 74 filenames, bytes, SHA-256, catálogo e manifesto.

## Updater autoritativo e regressão

`AUTHORITATIVE_UPDATER_BACKEND = updater/main.py`. É o entrypoint atual, configura `RAIZ_VADEMECUM`, fornece
`inventariar_vademecum`/`localizar_item_mestre`, importa `updater/indices_artigos.py`, expõe a CLI e chama a etapa após o Catálogo
Mestre tanto no fluxo padrão quanto em `--somente-mestre`. `--help` contém `--sem-indices-artigos` e `--indices-artigos-saida`.
A etapa escreve somente no staging; `--simular-mestre` usa diretório temporário. Cópias históricas não foram editadas.

Matriz final: DEVICE 318 PASS + 1 `SKIP_EXPECTED_MISSING_LOCAL_DATA` (header do core Arduino ilegível no sandbox; compensado pelos
dois builds reais), ENTENDA 97 PASS, LEGAL_TARGET_ID/Reference/RUN3 65 PASS, Updater 104 PASS, Reference Engine v1.3.2 35 checks
PASS. Indexed search, CC, thousands, scroll, next occurrence, REPEAT_READY, FD policy, reader state machine e Batch04 estão incluídos
nos 318 DEVICE. `FAIL_REAL=0`.

## Firmware host-only

Build final flag0: programa 989.395 B, RAM 124.452 B, imagem 989.536 B,
SHA-256 `33ab41a61e9552106ef49f779bad74a0ad21fc700c7e22cbbbe2dadd616610e9`. Programa/RAM são idênticos à baseline legacy; a
mudança está dentro da flag e diferenças binárias de imagem são metadata de build.

Build final flag1: programa 1.098.195 B, RAM 126.148 B, imagem 1.098.336 B,
SHA-256 `2dc522590213db139187feee73d8c1ad6e49209ea933a551466ca15415cc6acc`. Contra `10e199f`/r2: +960 B de programa,
0 B de RAM global e +960 B de imagem, correspondentes ao leitor/validador LXARTCT1. Não houve flash.
