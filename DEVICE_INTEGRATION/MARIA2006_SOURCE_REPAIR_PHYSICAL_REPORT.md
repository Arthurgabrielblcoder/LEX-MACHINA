# MARIA2006_SOURCE_REPAIR — relatório de implantação física

**Data:** 2026-10-04.

**Baseline:** `108469319bbe903f59dfecd4c33f9642f8984b91` / tag `lex-device-v1-full-corpus-indexes-approved-2026-10-04` (não alterada).

**Firmware:** não alterado, sem flash. O aparelho continua com o flag1 aprovado `2dc52259…cc6acc` (catálogo LXARTCT1).

**Estado:** **APROVADO.**
- SD validado (`SD_VALIDATED`).
- Boot PASS.
- `MARIA2006_PHYSICAL_PASS`.
- `PHYSICAL_HUMAN_VALIDATION = APPROVED`.
- Commit `LEX DATA: repair MARIA2006 source and complete article indexes`, tag `lex-device-v1-72-indexes-approved-2026-10-04`. Sem push.

**Ferramenta:** `tools/deploy_maria2006_source_repair_sd.py` (`pre` / `copy` / `verify`). Evidências em `backups/maria2006_physical_deploy_20261004/`.

## 1. Identificação do cartão

| Campo | Valor |
|---|---|
| Unidade | `D:` |
| Sistema de arquivos | FAT32, removível |
| Tamanho | 31.902.400.512 B (disco USB "Generic STORAGE DEVICE", 31.914.983.424 B) |
| Assinatura | `/99_LEX_V1/{00_SYS,05_TEXT,10_TARGETS,20_REFERENCES,30_ENTENDA}`, `1- CONSTITUIÇÃO FEDERAL`, `15-LEI MARIA DA PENHA` |

## 2. Auditoria antes da escrita (`pre` → `PRE_OK`)

| Verificação | Resultado |
|---|---|
| Manifesto completo vs `full_corpus_physical_deploy_20261003/sd_manifest_post_full.json` | 1.141 arquivos, **0 diferenças** (excluindo `System Volume Information`) |
| Manifesto `/99_LEX_V1` | 81 arquivos |
| TXT MARIA2006 atual | 215.426 B, `a560439bfa7bbb6cfa77f42578bf1688183c9047004eb022af0a6444af5e775c` = corrompido conhecido |
| Assinatura de corrupção | `C3 BF C3 BE` (ÿþ) no byte 475, seguido de `<h t m l >` |
| Catálogo atual | 4.040 B, `efadd17ee2483a325f1451d71ee40e8fedbf3c032ed0127cbdbc61a9c72b2f3b`, **71 entradas**, sem MARIA2006 |
| `*_ARTICLE_SEARCH.IDX` | 71 |
| `MARIA2006_ARTICLE_SEARCH.IDX` | **ausente** |
| Loader (modelo do firmware) com o TXT corrompido | `SEM_INDICE` |
| CF88 / CC2002 `ARTICLE_SEARCH.IDX` | `56e437a0…7fae` / `674c9971…3a68` (aprovados) |

Manifestos: `sd_manifest_pre_full.json`, `sd_manifest_pre_99_lex_v1.json`, `physical_pre.json`.

## 3. Backup verificável

Em `backups/maria2006_physical_deploy_20261004/sd_pre/` (`sd_pre_backup_manifest.json`):

| Arquivo | Bytes | SHA-256 |
|---|---|---|
| `sd_pre/15-LEI MARIA DA PENHA/Lei Maria da Penha.txt` | 215.426 | `a560439bfa7bbb6cfa77f42578bf1688183c9047004eb022af0a6444af5e775c` |
| `sd_pre/99_LEX_V1/10_TARGETS/ARTICLE_SEARCH_CATALOG.IDX` | 4.040 | `efadd17ee2483a325f1451d71ee40e8fedbf3c032ed0127cbdbc61a9c72b2f3b` |

Cada cópia foi relida e conferida (size + SHA-256) contra o cartão.

## 4. Cópia (`copy` → `COPY_OK 3`)

Origem: `staging_maria2006_source_repair/SD/`. Por arquivo:
1. gravação em `<nome>.LEX_NEW`;
2. `fsync`;
3. releitura (size + SHA-256);
4. `os.replace` para o nome final;
5. nova releitura.

Ordem: índice → TXT → catálogo, para que nenhum estado intermediário tenha um catálogo apontando para um índice inexistente.

| Ação | Caminho | Bytes | SHA-256 |
|---|---|---|---|
| ADD | `/99_LEX_V1/10_TARGETS/MARIA2006_ARTICLE_SEARCH.IDX` | 796 | `61e00407355f37f516eede152d0436f8e7e2897ebf4fff81eca2ecf5e86ad2d6` |
| REPLACE | `/15-LEI MARIA DA PENHA/Lei Maria da Penha.txt` | 46.902 | `f1d43b76e1ae4013cbf812d5ac2169561e6bc6c4ecfa1e5ab7fbf2721c7d341f` |
| REPLACE | `/99_LEX_V1/10_TARGETS/ARTICLE_SEARCH_CATALOG.IDX` | 4.096 | `8d7d11db81dfa1a07f647260e17a88b197b90a3b912012880a3701e5ca31a4c9` |

## 5. Readback e validação do SD (`verify` → `SD_VALIDATED`)

| Verificação | Resultado |
|---|---|
| Readback dos 3 arquivos direto do SD | **3/3 MATCH** (size + SHA-256) |
| Diff completo pré → pós | added = [`MARIA2006_ARTICLE_SEARCH.IDX`], changed = [TXT, catálogo], removed = [] |
| Demais arquivos | 1.140 byte-idênticos (`other_files_untouched: true`); 1.141 → 1.142 arquivos |
| Temporários `.LEX_NEW` | nenhum |
| Catálogo | **72 entradas** |
| `*_ARTICLE_SEARCH.IDX` | **72** |
| Entrada MARIA2006 | `source_bytes` 46.902, `source_sha256` `f1d43b76…341f`, `index_bytes` 796 |
| Loader (modelo do firmware, estratégia CATALOG) | `LOADED MARIA2006_ARTICLE_SEARCH.IDX` (seleção ≈21 ms, carga ≈18 ms, estimados) |
| CF88 / CC2002 índices | inalterados (`56e437a0…7fae` / `674c9971…3a68`); `cf.txt` e TXT do CC inalterados |

**Texto novo, lido do SD:**
- UTF-8 sem BOM, LF;
- 0 bytes nulos, 0 tags HTML, 0 `ÿþ`, 0 U+FFFD;
- começa em "LEI Nº 11.340, DE 7 DE AGOSTO DE 2006".

Manifestos: `sd_manifest_post_full.json`, `sd_manifest_post_99_lex_v1.json`, `physical_validation.json`.

## 6. Boot (sem flash)

**PASS.** Arthur recolocou o cartão com o aparelho desligado e o leitor alimentado. O boot foi capturado pela COM3 (CH343,
ESP32-S3) depois de um reset por RTS/EN, sem flash.

**Log:** `backups/maria2006_physical_deploy_20261004/serial/serial_boot.log`, 25.324 B, SHA-256
`000ab09b619f82f08997b687afc7a47f0ffdbe72ed6d307b8d78f7065698bc62`. Captura feita por `serial/capture.py` (somente leitura).

| Critério | Resultado |
|---|---|
| SD montado | `rst:0x1 (POWERON),boot:0x2b (SPI_FAST_FLASH_BOOT)` |
| JUR CACHE | `lookups=178 registros=296 bytes=64888 ... fonte=CACHE` |
| DIAG | `LEXV1: DIAG RESULT PASS pass=33 fail=0 MAX_OPEN_COUNT=4`, 0 `CHECK FAIL` |
| Catálogo aceito | `OPEN ARTIDX_CAT .../ARTICLE_SEARCH_CATALOG.IDX` seguido da seleção do índice, sem `CATALOGO_INVALIDO` |
| FAIL_IO / panic / watchdog / Guru / Backtrace | 0 |
| Reboots durante a sessão | 0 (uma única linha `rst:` em todo o log) |

O único `FAIL_SOURCE_MISMATCH` do log é o teste negativo intencional `CHECK PASS text_map_guard_sha_errado`.

## 7. Validação física

**Seleção do índice (serial):** ao abrir a Lei Maria da Penha, a serial registrou:
1. `OPEN ARTIDX_CAT` (catálogo);
2. `OPEN ARTIDX_TEXT /15-LEI MARIA DA PENHA/Lei Maria da Penha.txt` (vínculo);
3. `OPEN ARTIDX .../MARIA2006_ARTICLE_SEARCH.IDX`.

Sem `NENHUM_INDICE_VALIDO`. Todos os FDs foram fechados (`OPEN_COUNT=0`).

**Buscas registradas na serial, conferidas contra o TXT gravado:**

| Busca | Ocorrência (byte) | Linha no TXT |
|---|---|---|
| Art. 5 | 3.681 | "Art. 5º Para os efeitos desta Lei, conf…" |
| Art. 12 | 17.336 | "Art. 12. Em todos os casos de violência…" |
| Art. 46 | 46.638 | "Art. 46. Esta Lei entra em vigor 45 (qua…" |

Todas pousaram com `ESTADO NORMAL_READING_MODE`.

**CONTEXTO (serial):** acompanhou a rolagem de ART=1 a 7, incluindo incisos e parágrafo único, e depois ART=5 e ART=12 após as
buscas. A atualização leva cerca de 0,6 ms.

**Troca de norma (serial):** MARIA2006 → CF passou por `OPEN ARTIDX_CAT` e `OPEN ARTIDX .../CF88_ARTICLE_SEARCH.IDX`. Em seguida
vieram `BUSCA Art. 193 -> offset=349179` e `ACTIVE_TARGET=CF88:ART.193`. CONTEXTO, CACHE_TARGET e as camadas R (referências)
também apontaram para CF88:ART.193. Não houve stale index.

**Cobertura da serial:** a captura não registrou a troca CF → CC → MARIA2006, nem as buscas dos demais artigos. Esses itens se
apoiam na confirmação humana (seção 8).

**Known limitation (não bloqueante):** ao rolar o art. 1, o CONTEXTO mostrou `ART=1 PAR=8`, porque leu a remissão "§ 8º do
art. 226 da Constituição Federal" como parágrafo local. O problema está registrado à parte em `KNOWN_LIMITATION_CONTEXTO_REMISSAO.md` e não
será corrigido durante o freeze da MARIA2006.

| Item | Resultado |
|---|---|
| Texto legível (sem HTML, tags, `ÿþ`, nulos ou mojibake) | PASS (humano + checagem no SD) |
| Busca: 1, 5, 10, 10-A, 12, 12-A, 12-B, 12-C, 12-D, 14-A, 24-A, 38-A, 40-A, 46 | PASS humano; 5, 12 e 46 também na serial |
| CONTEXTO / scroll | PASS (humano + serial) |
| CF → MARIA2006 → CC → MARIA2006, sem stale index | PASS humano; MARIA2006 → CF também na serial |
| Amostra visual: cabeçalho, arts. 1, 5, 7, 10-A, 12-C, 14-A, 24-A, 40-A, 46 | PASS humano |

## 8. Validação humana

**`PHYSICAL_HUMAN_VALIDATION = APPROVED`**, aprovação formal de Arthur em 2026-10-04.

Arthur confirmou:
- texto da Lei Maria da Penha legível e correto;
- sem HTML, tags, `ÿþ` ou caracteres corrompidos;
- acentuação correta;
- buscas rápidas e artigos corretos;
- CONTEXTO funcional;
- scroll fluido;
- troca entre normas funcionando;
- nenhum travamento, reboot ou erro de SD.

**Resultado: `MARIA2006_PHYSICAL_PASS = PASS`.**

| # | Critério | Resultado |
|---|---|---|
| 1 | SD monta | ✅ |
| 2 | Novo TXT abre | ✅ |
| 3 | Texto limpo | ✅ |
| 4 | Catálogo aceita 72 entradas | ✅ |
| 5 | Índice MARIA2006 selecionado | ✅ |
| 6 | Busca rápida | ✅ |
| 7 | Sufixos funcionam | ✅ |
| 8 | CONTEXTO correto | ✅ (com a known limitation registrada à parte) |
| 9 | Scroll correto | ✅ |
| 10 | Troca entre normas sem stale index | ✅ |
| 11 | Nenhum crash | ✅ |
| 12 | Nenhum reboot | ✅ |
| 13 | Nenhum erro SD | ✅ |

## 9. Regressão final

| Suíte | Resultado |
|---|---|
| DEVICE | 327/327, 0 skip |
| ENTENDA | 97/97 |
| LEGAL_TARGET_ID | 65/65 |
| Updater | 116: 113 PASS + 3 ERROR ambientais (`ModuleNotFoundError: truststore` nos testes TLS dos importadores STF, os mesmos de antes) |

**FAIL_REAL = 0.**

## 10. Baseline

| Campo | Valor |
|---|---|
| Anterior | `108469319bbe903f59dfecd4c33f9642f8984b91` / `lex-device-v1-full-corpus-indexes-approved-2026-10-04` (preservada) |
| Nova tag | `lex-device-v1-72-indexes-approved-2026-10-04` |
| Firmware | inalterado, flag1 `2dc52259…cc6acc` |
| SD físico | 72/72 normas indexadas; catálogo `8d7d11db81dfa1a07f647260e17a88b197b90a3b912012880a3701e5ca31a4c9` |
| Fora do commit | `staging_*`, `backups/` (manifestos, backups `sd_pre`, log serial bruto), binários e caches, conforme o `.gitignore` |

## Rollback (sem Git)

1. Restaurar o TXT e o catálogo a partir de `backups/maria2006_physical_deploy_20261004/sd_pre/`.
2. Remover `/99_LEX_V1/10_TARGETS/MARIA2006_ARTICLE_SEARCH.IDX`.
