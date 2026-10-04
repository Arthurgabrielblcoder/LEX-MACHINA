# MARIA2006_SOURCE_REPAIR — relatório

**Data:** 2026-10-04.

**Baseline:** `108469319bbe903f59dfecd4c33f9642f8984b91` / tag `lex-device-v1-full-corpus-indexes-approved-2026-10-04` (não alterada).

**Estado:** reparo pronto em staging host. Nada foi gravado no SD físico, nenhum flash, sem commit, tag ou push.

**Atualização (2026-10-04):** implantado no SD físico e aprovado (`MARIA2006_PHYSICAL_PASS`, `PHYSICAL_HUMAN_VALIDATION = APPROVED`). Ver `MARIA2006_SOURCE_REPAIR_PHYSICAL_REPORT.md`.

## 1. Arquivo operacional corrompido (antes)

`/15-LEI MARIA DA PENHA/Lei Maria da Penha.txt` no cartão: 215.426 B, SHA-256 `a560439bfa7bbb6cfa77f42578bf1688183c9047004eb022af0a6444af5e775c`.

**Encoding real:**
- O arquivo é UTF-8 válido, sem BOM e sem bytes nulos.
- O conteúdo, porém, é o HTML de uma página UTF-16LE decodificada como **cp1252**:
  - o BOM `FF FE` virou `ÿþ`, regravado como `C3 BF C3 BE`, logo após o cabeçalho LEX;
  - cada byte nulo do UTF-16 virou espaço (`<h t m l >`, `L e i n º 1 1 . 3 4 0`).

**Cabeçalho:** declara `CODIFICACAO_ORIGEM: cp1252` e `ATUALIZADO_EM: 13/09/2026 14:52`. Não tem as linhas `METODO_ATUALIZACAO` / `VALIDACAO_INTEGRIDADE`, que o Updater versionado sempre grava.

**HTML presente:** 2.258 tags (122.035 caracteres de marcação: `<html>`, `<head>`, `<meta ... FrontPage 6.0>`, `<link>`, `<style>`, `<p>`...).

**Charset declarado:** nenhum. Nem a página nem o HTTP (`Content-Type: text/html`) declaram charset.

**Conteúdo jurídico embutido:** sim, mas espaçado e com travessões perdidos. Diagnóstico contra o texto oficial (somente diagnóstico; o corrompido nunca foi fonte):

| Classe | Resultado |
|---|---|
| MATCHABLE_TEXT | 596/619 linhas recuperáveis ignorando espaços |
| MISSING_TEXT | 23 linhas, todas com `–` (U+2013 = `13 20` em UTF-16LE, lido como controle + espaço) ou quebras vizinhas |
| HTML_NOISE | 2.258 tags |
| ENCODING_CORRUPTION | 2.429 sequências de letras espaçadas + BOM lido como 8 bits |

**Por que foi salvo assim (cronologia comprovada):**
1. Até 13/09/2026 o TXT era válido: 47.078 B, preservado em `updater/backup_catalogos/catalogo_mestre_20260913_145232/`, com 57 artigos.
2. Às 14:52, uma execução de atualização do Catálogo Mestre baixou `l11340.htm` do Planalto (HTTP 200, 264.515 B: o mesmo tamanho de hoje). A página é servida em **UTF-16LE com BOM**, sem charset.
3. `decodificar_html` só testava utf-8/cp1252/iso-8859-1. Bytes UTF-16 "decodificam" sem erro em cp1252, então foi escolhido cp1252.
4. O BeautifulSoup não reconheceu as tags espaçadas, e o HTML inteiro virou "texto". Esse Updater ainda não tinha as travas fail-closed: elas entraram no primeiro commit do Updater, `281f3a4` (15/09). O arquivo de 47 KB foi sobrescrito pelo HTML de 215 KB.

**Classificação:**

| Código | Etapa |
|---|---|
| `ENCODING_MISMATCH` | UTF-16LE não detectado, lido como cp1252 |
| `HTML_EXTRACTION_FAILURE` | marcação ilegível para o parser |
| `HTTP_WRAPPER_SAVED_AS_TEXT` | gravado sem trava |

**Defeito ainda presente antes desta missão:** com as travas atuais, a gravação seria bloqueada (a validação acusa crescimento de 3×, 57 → 0 artigos). Mas como o decodificador continuava cego para UTF-16, a norma ficaria permanentemente bloqueada e o Updater nunca a repararia. Além disso, o local corrompido seria usado como referência de comparação.

## 2. Backend do Updater corrigido (`updater/main.py`)

**SOURCE_PROVIDER:** Presidência da República — Planalto. É a fonte do Catálogo Mestre (`fonte_oficial`); não houve troca de fonte.
- **SOURCE_URL:** `https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2006/lei/l11340.htm`.
- **Adaptador específico:** nenhum (MARIA2006 não está em `FONTES_ESPECIAIS_MESTRE`).
- **Fallback:** nenhum.
- **Caminho:** `_obter_candidato_mestre` → genérico HTML Planalto.

**Fluxo agora:**
1. `baixar_fonte_oficial`: download.
2. `validar_resposta_fonte`: valida a resposta:
   - HTTP 200;
   - sem redirecionamento para outro host;
   - content-type html/plain;
   - mínimo de 1 KB.
3. `detectar_codificacao_estrutural` / `decodificar_html`:
   - detecta BOM UTF-8/UTF-16 e UTF-16 sem BOM;
   - decodificação estrita;
   - remove só o enchimento final de espaços ASCII de 1 byte em UTF-16LE (o Planalto anexa 1.559 B `0x20` depois de `</html>`);
   - qualquer outro resíduo dá `ENCODING_INVALIDO`.
4. Extração/normalização.
5. `verificar_texto`, com os sinais novos:
   - byte nulo;
   - letras espaçadas;
   - BOM UTF-16 lido como 8 bits;
   - HTML residual;
   - páginas de erro, bloqueio ou captcha.
6. `validar_identidade_norma`: o número do ato precisa estar no texto.
7. `_validar_candidato_generico`.

**Fail-closed:** qualquer falha levanta `AtualizacaoBloqueada` (`UPDATE_BLOCKED <código>`), roteada para `BLOQUEADO_INTEGRIDADE`. **O last-known-good é preservado** (testado com 7 respostas ruins).

**Local corrompido:** `arquivo_local_corrompido` reprova um local que mostra os mesmos sinais de corrupção. Ele deixa de ser tratado como last-known-good; valem então as regras de arquivo ausente (cabeçalhos de artigo + identidade).

**Reprodutibilidade:**
- `candidato_mestre_de_bytes` separa a validação do download, para reproduzir a partir dos bytes arquivados.
- `criar_cabecalho_mestre(atualizado_em=...)` fixa a data do cabeçalho.

## 3. Fonte oficial e prova de origem

Arquivada em `DEVICE_INTEGRATION/source_evidence/MARIA2006/`:
- `l11340_planalto_20261004.htm`: bytes brutos;
- `.provenance.json`.

| Campo | Valor |
|---|---|
| URL pedida = final | sem redirecionamento |
| HTTP | 200 |
| Content-Type | `text/html` (sem charset) |
| Last-Modified | `Mon, 24 Aug 2026 18:36:26 GMT` |
| ETag | `"4032c-659cf438fa7f7"` |
| Data | `Sun, 04 Oct 2026 04:31:47 GMT` |
| Bytes | 264.515 |
| SHA-256 | `488268242fbb9247107248cd2fca73b00e7084fd6d296d193558ce1236907587` |
| Primeiros bytes | `ff fe 0d 00 0a 00 3c 00 68 00 ...` |
| Encoding detectado | `utf-16-le` (BOM) |

**Origem rastreável:** SIM. O TXT é reconstruído byte a byte a partir desses bytes por `tools/repair_maria2006_source.py`, usando apenas funções do Updater.

## 4. TXT candidato

**Arquivo:** `DEVICE_INTEGRATION/staging_maria2006_source_repair/SD/15-LEI MARIA DA PENHA/Lei Maria da Penha.txt`, no mesmo caminho do cartão.

| Campo | Valor |
|---|---|
| Bytes | 46.902 |
| SHA-256 | `f1d43b76e1ae4013cbf812d5ac2169561e6bc6c4ecfa1e5ab7fbf2721c7d341f` |
| Encoding final | UTF-8 sem BOM, LF, zero bytes nulos |
| Cabeçalho | Catálogo Mestre padrão: `METODO_ATUALIZACAO: HTML_PLANALTO_COM_GUARDRAILS`, `VALIDACAO_INTEGRIDADE: APROVADA`, `CODIFICACAO_ORIGEM: utf-16-le`, `ATUALIZADO_EM: 04/10/2026 01:31` |

**Estrutura validada** (parser estrutural em modo estrito, sem texto preenchido por conhecimento de modelo):

| Item | Resultado |
|---|---|
| Identificação | "LEI Nº 11.340, DE 7 DE AGOSTO DE 2006" e "(Lei Maria da Penha)" |
| Artigos | 57 = arts. 1 a 46, mais 11 com sufixo (10-A, 12-A, 12-B, 12-C, 12-D, 14-A, 16-A, 17-A, 24-A, 38-A, 40-A) |
| Parágrafos | 45 |
| Parágrafos únicos | 17 |
| Incisos | 83 |
| Alíneas | 4 |
| Marcas de alteração | 9 "Redação dada", 60 "Incluído pela" (até a Lei 15.212/2025), 2 "(VETADO)"; nenhum "(Revogado)" |
| Fechamento | assinaturas (LUIZ INÁCIO LULA DA SILVA / Dilma Rousseff) e nota do DOU de 8.8.2006 |

Nenhuma marcação HTML, letra espaçada ou mojibake (`verificar_texto` vazio).

## 5. Índice `MARIA2006_ARTICLE_SEARCH.IDX`

Gerado pelo pipeline full-corpus aprovado (`article_index_corpus.build_corpus`, com `source_overrides` para o texto reparado).

| Campo | Valor |
|---|---|
| Schema / namespace | LXARTIX1 v1, namespace `MARIA2006` |
| Registros | 57 |
| Bytes | 796 |
| SHA-256 | `61e00407355f37f516eede152d0436f8e7e2897ebf4fff81eca2ecf5e86ad2d6` |
| Fonte vinculada | 46.902 B / `f1d43b76…341f`; hash do corpo conferido |

**Auditoria de 100% dos registros (57/57):**
- todo offset fica dentro do arquivo e no início de uma linha;
- cada linha é o cabeçalho estrutural daquela chave (número + sufixo);
- nenhuma remissão;
- namespace correto;
- nenhuma chave repetida, nenhum intervalo coletivo.

**Equivalência com o oráculo (varredura linear):** PASS, 57 chaves. Os arts. 1..46 sem sufixo aparecem exatamente uma vez; o 47 não é encontrado.

**Falsos positivos:** 0.

## 6. Catálogo e acervo completo

**`ARTICLE_SEARCH_CATALOG.IDX`:**

| | Entradas | Bytes | SHA-256 |
|---|---|---|---|
| Antes | 71 | 4.040 | `efadd17e…2f3b` |
| Depois | 72 | 4.096 | `8d7d11db81dfa1a07f647260e17a88b197b90a3b912012880a3701e5ca31a4c9` |

As 71 entradas antigas não mudam. As 72 cobrem exatamente o Catálogo Mestre.

**Regeneração completa do acervo** (`_host/full_corpus/`, base = staging full-corpus aprovado):
- **72 normas, 72 índices, BLOCKED 0** (KEEP 71, ADD 1, REBUILD 0, REMOVE 0);
- 12.953 registros, 163.516 B de índices mais o catálogo.

Os outros 71 arquivos de deploy continuam idênticos ao manifesto físico. A MARIA2006 aparece como `NEEDS_PHYSICAL_HASH_CONFIRMATION` até a implantação, porque o cartão ainda tem o texto corrompido.

**Loader (modelo do firmware):**
- o catálogo novo seleciona `MARIA2006_ARTICLE_SEARCH.IDX` para o TXT reparado;
- para o TXT corrompido, o resultado é `SEM_INDICE`: nunca um índice errado;
- o CC continua no próprio índice.

**Determinismo:** o reparo completo foi rodado 1 + 3 vezes, com 79 arquivos idênticos byte a byte (TXT, índice MARIA2006, catálogo, manifesto do reparo, staging e manifesto full-corpus).

## 7. Firmware

**Não precisa mudar.** O formato do catálogo é o mesmo (LXARTCT1) e 72 entradas cabem no limite de 4.096. A fonte do firmware tem diff zero contra o commit aprovado.

| Build | Programa / RAM | Imagem / SHA-256 |
|---|---|---|
| flag1 aprovado (gravado no aparelho) | 1.098.195 B / 126.148 B | 1.098.336 B / `2dc522590213db139187feee73d8c1ad6e49209ea933a551466ca15415cc6acc` |
| flag0 aprovado | 989.395 B / 124.452 B | 989.536 B / `33ab41a6…10e9` |

**Flash necessário:** NÃO.

## 8. Testes

| Suíte | Resultado |
|---|---|
| DEVICE | **327/327**, 0 skip |
| ENTENDA | 97/97 |
| LEGAL_TARGET_ID (inclui Reference Engine e RUN3) | 65/65 |
| Updater | 116 testes: 113 PASS (inclui os 12 novos de `test_fonte_oficial_failclosed.py`) + 3 ERROR ambientais |

**Detalhe do DEVICE:**
- novo `test_maria2006_source_repair`: 9/9;
- full corpus: 17/17;
- Batch04/consolidação: 24;
- busca indexada: 20;
- índice do CC: 12;
- milhares: 19;
- scroll: 25;
- RUN3 device: 9;
- próxima ocorrência, REPEAT_READY e política de descritores: incluídos.

**Os 12 testes novos do Updater cobrem os 10 casos pedidos:**
1. fonte oficial válida (os bytes arquivados);
2. UTF-8;
3. UTF-16 LE/BE, com e sem BOM, e com enchimento;
4. HTML que precisa de extração;
5. página sem a norma ou de outra lei;
6. página de erro (404/503, "Request Rejected", captcha);
7. conteúdo vazio;
8. charset incorreto (o defeito original);
9. redirecionamento e content-type inesperados;
10. last-known-good preservado em 7 respostas ruins, mais o reparo de um local corrompido.

**Erros ambientais:** os 3 ERROR do Updater são `ModuleNotFoundError: truststore`, em `test_importar_stf_controle_concentrado`, `test_importar_stf_repercussao_geral` e `test_importar_stf_sumulas_vinculantes`. A dependência está em `updater/requirements.txt`, mas não está instalada em nenhum Python desta máquina. Esses arquivos não foram tocados; não há relação com a MARIA2006.

**FAIL_REAL = 0.**

## 9. Mini-deploy

**Staging:** `DEVICE_INTEGRATION/staging_maria2006_source_repair/SD/` (3 arquivos, 51.794 B).
- REPLACE: TXT;
- ADD: `MARIA2006_ARTICLE_SEARCH.IDX`;
- REPLACE: `ARTICLE_SEARCH_CATALOG.IDX`.

Nenhum outro índice ou arquivo de versão precisa mudar.

**Plano:** `DEVICE_INTEGRATION/MARIA2006_SOURCE_REPAIR_DEPLOY_PLAN.md` (fases A–H e rollback).

**Arquivos desta missão:**
- `updater/main.py`, `updater/test_fonte_oficial_failclosed.py`;
- `DEVICE_INTEGRATION/tools/repair_maria2006_source.py`, `tools/article_index_corpus.py` (`source_overrides`);
- `tests/test_maria2006_source_repair.py`;
- `source_evidence/MARIA2006/`;
- `.gitignore`;
- este relatório e o plano.

Firmware físico: NÃO alterado. SD físico: NÃO alterado. Commit, tag, push: NÃO.
