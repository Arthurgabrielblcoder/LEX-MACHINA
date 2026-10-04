# FULL CORPUS ARTICLE INDEX — implantação física do microSD

Data: 2026-10-03  
Unidade identificada: `D:`  
Escopo executado: fases A–D, readback e auditoria pós-cópia do microSD; flash app-only, readback e boot aprovado.  
Status final (2026-10-04): **BASELINE FÍSICA APROVADA**.
- **`PHYSICAL_HUMAN_VALIDATION = APPROVED`** (Arthur).
- SD e catálogo funcionaram fisicamente.
- Índices full-corpus aprovados: 71 normas indexadas.
- MARIA2006 permanece `INDEX_BUILD_BLOCKED`.
- Tag anotada: `lex-device-v1-full-corpus-indexes-approved-2026-10-04`.
- Push: **NÃO**.

## Baseline e gates

- Commit físico aprovado: `10e199f`.
- Tag: `lex-device-v1-batch04-run3-physical-approved-2026-10-03`, ainda apontando para `10e199f`.
- Estrutura física confirmada: acervo jurídico e `/99_LEX_V1/{00_SYS,05_TEXT,10_TARGETS,20_REFERENCES,30_ENTENDA}`.
- CF88 físico antes da cópia: 5.216 B, SHA-256
  `56e437a0c9cebb113c47f6a7b100ee64363c63207a647eca0456e86d6db27fae` — MATCH aprovado.
- CC2002 físico antes da cópia: 25.036 B, SHA-256
  `674c9971925c29aaca9685fb2d0b9515fe87e4072d644858ea27495c327d3a68` — MATCH aprovado.

## Manifestos anteriores e backup

- Manifesto completo prévio: `backups/full_corpus_physical_deploy_20261003/sd_manifest_pre_full.json`.
- Arquivos físicos pré-existentes: 1.071. Metadados internos do Windows em `System Volume Information` foram explicitamente
  excluídos; nenhum arquivo de conteúdo do LEX MACHINA foi excluído.
- Manifesto `/99_LEX_V1` prévio: `backups/full_corpus_physical_deploy_20261003/sd_manifest_pre_99_lex_v1.json`, 11 arquivos.
- Backup verificável: `backups/full_corpus_physical_deploy_20261003/sd_pre/99_LEX_V1`, 11/11 arquivos com size e SHA-256 MATCH.
- Manifesto do backup: `backups/full_corpus_physical_deploy_20261003/sd_pre_backup_manifest.json`.

O backup inclui, sem alteração, runtime CF/ADCT, TEXT_MAP, índices CF/CC, 220 ENTENDA, RUN3/Reference Engine e os metadados do
pacote V1.

## Staging e diff físico calculado

- Staging: `DEVICE_INTEGRATION/staging_article_indexes_full_corpus_candidate/SD/99_LEX_V1/10_TARGETS`.
- Validado: 71 `*_ARTICLE_SEARCH.IDX` + `ARTICLE_SEARCH_CATALOG.IDX` = 72 arquivos, 166.760 B.
- Artefatos `_host` não foram copiados.
- Diff prévio real: `KEEP=2`, `ADD=70`, `CONFLICT=0`, `REMOVE=0`.
- KEEP: `CF88_ARTICLE_SEARCH.IDX`, `CC2002_ARTICLE_SEARCH.IDX`.
- ADD: 69 índices de norma + `ARTICLE_SEARCH_CATALOG.IDX`.
- `MARIA2006_ARTICLE_SEARCH.IDX`: ausente no staging e no cartão.

## Cópia

Foram adicionados exclusivamente os 70 arquivos ausentes em `D:\99_LEX_V1\10_TARGETS`. Cada arquivo foi gravado sob nome
temporário exclusivo, sincronizado com `fsync`, relido e comparado por size+SHA-256; somente depois foi renomeado para o nome final.
Nenhum arquivo existente foi aberto para sobrescrita. Não houve remoção.

## Readback e manifesto posterior

- Resultado: `SD_VALIDATED`.
- Readback: 72/72 artefatos de deploy MATCH contra o staging.
- Manifesto completo posterior: `backups/full_corpus_physical_deploy_20261003/sd_manifest_post_full.json`.
- Manifesto `/99_LEX_V1` posterior: `backups/full_corpus_physical_deploy_20261003/sd_manifest_post_99_lex_v1.json`.
- Resultado estruturado: `backups/full_corpus_physical_deploy_20261003/physical_validation.json`.
- Diff completo: 70 ADD, 0 CHANGED, 0 REMOVED.
- CF88 posterior: hash aprovado intacto.
- CC2002 posterior: hash aprovado intacto.
- 69 índices novos: size+SHA-256 MATCH.
- Catálogo: size+SHA-256 MATCH.
- MARIA2006: índice ausente; estado preservado `INDEX_BUILD_BLOCKED` / `SOURCE_FIX_REQUIRED`.
- Arquivos legacy fora de `/99_LEX_V1`: byte-identical.
- Arquivos pré-existentes dentro de `/99_LEX_V1`: byte-identical.
- TXT jurídicos, runtime, TEXT_MAP, ENTENDA, relações, RUN3 e Reference Engine: não alterados.

## Firmware, boot, catálogo em runtime e amostras

- Porta/dispositivo: `COM3`, ESP32-S3 QFN56 rev. 0.2, PSRAM 8 MB, flash 16 MB, MAC `e0:72:a1:f4:fd:28`.
- Tabela real: `app0` ativo (`otadata` sequência 1), offset `0x10000`, tamanho `0x140000` (1.310.720 B).
- Candidato confirmado: 1.098.336 B, SHA-256
  `2dc522590213db139187feee73d8c1ad6e49209ea933a551466ca15415cc6acc`.
- Backup integral pré-flash de `app0`: `backups/full_corpus_physical_deploy_20261003/flash/app0_pre.bin`,
  1.310.720 B, SHA-256 `f17ae21b64221f0aa67233db51170f9dbd1feda64dcbf0fcda09d6fdc5f13351`.
- Flash: **PASS**, somente `write-flash 0x10000`, com mode/freq/size `keep`; 1.098.336 B gravados e verificação
  interna do esptool aprovada. Bootloader, NVS, tabela, `otadata`, `app1` e SPIFFS não foram alvos.
- Readback independente: **PASS**, 1.098.336/1.098.336 B byte-identical; SHA-256
  `2dc522590213db139187feee73d8c1ad6e49209ea933a551466ca15415cc6acc`.
- Tabela de partições pré/pós: byte-identical, SHA-256
  `f3134b747fef242287f33aa0be8a5008958132e0c7611f5bc5bb917c02c9e397`.
- `otadata` pré/pós: byte-identical, SHA-256
  `f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0`.
- Primeiro boot: app iniciou sem panic, `TESTE CONTEXTO JURIDICO: OK`, BLE e PSRAM OK; log em
  `backups/full_corpus_physical_deploy_20261003/flash/serial_boot.log`.
- Bloqueio do boot: `boot:0x8`, ausência de `JUR CACHE` e `LEXV1: SD indisponivel -> camadas V1 desativadas`.
  O histórico físico registra `boot:0x8` nos boots sem cartão e `boot:0x2b` no boot válido com cartão. É necessário
  conferir/reencaixar o microSD com o Lex sem alimentação e fazer power-cycle completo antes de repetir a captura.
- Nova captura após Arthur desligar totalmente o Lex, retirar/reencaixar o microSD sem alimentação e reconectar:
  `backups/full_corpus_physical_deploy_20261003/flash/serial_boot_after_reseat.log`, 1.114 B, SHA-256
  `dccbecf4b0fb8ca35a143a225ca52cc9496db8ab9db605aa0b519674f1a4973f`.
- Resultado da nova captura: o app iniciou uma única vez (`rst:0x1`), novamente com `boot:0x8`; contexto jurídico, BLE e
  PSRAM iniciaram, mas não houve `JUR CACHE`, acesso a `/99_LEX_V1` nem carregamento do catálogo. O log contém exatamente
  um `FAIL_IO`, exclusivamente `sd_montado`, e zero ocorrências de `Guru Meditation`, `panic` ou `watchdog`.
- Conforme a ordem de parada, nenhuma validação física de índices foi iniciada, nenhum novo flash/rollback foi executado e
  nenhuma alteração foi feita no microSD.
- Causa física informada por Arthur: o módulo/tela que alimenta o leitor microSD estava sem alimentação nas duas capturas
  anteriores. Após energizar o leitor desde o início e fazer power-cycle completo, nova captura em
  `backups/full_corpus_physical_deploy_20261003/flash/serial_boot_reader_powered.log`: 11.178 B, SHA-256
  `9e30617612e20df3d6e3320673356e8961a254a52dd65406c441949a560a4539`.
- Boot com leitor alimentado: **PASS**. `boot:0x2b`, `JUR CACHE: lookups=178 registros=296 ... fonte=CACHE`, 46 acessos
  registrados sob `/99_LEX_V1`, runtime/hash/TEXT_MAP/índices V1 aprovados e
  `LEXV1: DIAG RESULT PASS pass=33 fail=0 MAX_OPEN_COUNT=4`.
- Estabilidade desse boot: uma única linha `rst:0x1`; zero `FAIL_IO`, `Guru Meditation`, `panic` e `watchdog`.
- O `ARTICLE_SEARCH_CATALOG.IDX` não é aberto durante o diagnóstico de boot: por desenho, sua leitura ocorre ao abrir um
  texto jurídico. A captura passiva das amostras físicas foi iniciada para comprovar `ARTIDX_CAT` e a troca dos índices.
- Aceitação LXARTCT1 pelo firmware: **PASS**. Ao abrir a CF, a serial registrou `OPEN ARTIDX_CAT` e `CLOSE` de
  `/99_LEX_V1/10_TARGETS/ARTICLE_SEARCH_CATALOG.IDX`, seguidos de `OPEN ARTIDX`/`CLOSE` do
  `CF88_ARTICLE_SEARCH.IDX`; zero `CATALOGO_INVALIDO`, `INDEX_INVALID` ou `FALLBACK_LINEAR`. O timing específico do
  catálogo não é emitido porque `LEXV1_ARTSEARCH_LOG` permanece desligado, conforme a missão.
- Amostra CF: **PASS humano + serial**. Arthur confirmou arts. 193 e 230 corretos, rápidos, scroll fluido e camadas
  funcionando, sem anomalias. A serial confirmou `BUSCA Art. 193`, `ACTIVE_TARGET=CF88:ART.193`, `BUSCA Art. 230` e
  `ACTIVE_TARGET=CF88:ART.230`, sem stale index, `FAIL_IO`, crash ou reboot.
- Amostra CC: **PASS humano**. Arthur concluiu as buscas solicitadas dos arts. 1000, 2000 e 2046 sem relatar anomalia.
  A captura serial temporária expirou antes do bloco; a seleção serial do `CC2002_ARTICLE_SEARCH.IDX` será confirmada no
  teste obrigatório de troca entre normas.
- Amostras CPC/CLT/CTN/CPP/CP/CDC/LGPD/norma pequena: aprovadas por Arthur (seção "Validação física final").
- Teste de troca CF→CC→CPC→CLT→CTN→CF: aprovado por Arthur.
- MARIA2006: sem índice e sem entrada no catálogo; busca linear (aprovado).
- `PHYSICAL_HUMAN_VALIDATION`: **APPROVED**.

## Causa dos boots com "SD indisponível"

**Classificação: `ENVIRONMENTAL_HARDWARE_POWER_ISSUE`.**

- **O que aconteceu:** o módulo de tela que alimenta o leitor microSD estava sem alimentação nas capturas `serial_boot.log` e `serial_boot_after_reseat.log`.
- **Sintoma:** `boot:0x8`, sem `JUR CACHE`, um único `FAIL_IO sd_montado`.
- **Não era** firmware, cartão nem conteúdo do SD.
- **Depois de restaurar a alimentação** (`serial_boot_reader_powered.log`):
  - o SD montou (`boot:0x2b`) e `JUR CACHE` apareceu;
  - `DIAG RESULT PASS pass=33 fail=0`;
  - zero `FAIL_IO`, zero watchdog, zero panic, zero reboot inesperado (uma única linha `rst:0x1`, a do power-on).

## Validação física final

**Catálogo em runtime** (`serial_full_corpus_validation.log`):
- Abrir a CF fez o loader ler o catálogo (`OPEN ARTIDX_CAT` / `CLOSE`) e carregar o índice certo (`OPEN ARTIDX .../CF88_ARTICLE_SEARCH.IDX`).
- Nenhuma ocorrência de `CATALOGO_INVALIDO`, `INVALIDO`, `NENHUM_INDICE_VALIDO`, `FAIL_IO`, panic, watchdog ou reboot nos logs de validação.
- Os logs de benchmark continuam desligados. Por isso a evidência serial cobre a seleção pelo catálogo e o índice da CF; as demais amostras (CC, troca entre normas, fluidez) foram aprovadas por Arthur.

**Resultado:** `PHYSICAL_HUMAN_VALIDATION = APPROVED`.

**Índices full-corpus aprovados:**
- 71 `*_ARTICLE_SEARCH.IDX` mais `ARTICLE_SEARCH_CATALOG.IDX` = 72 arquivos, 166.760 B, 12.896 registros.
- CF88 e CC2002 continuam byte-identical aos aprovados.
- **MARIA2006 permanece `INDEX_BUILD_BLOCKED`** (`SOURCE_NOT_PLAIN_TEXT`): o TXT é HTML UTF-16 gravado como texto. Nenhum índice existe para ela, e a busca no aparelho continua linear.
- Próxima missão: `MARIA2006_SOURCE_REPAIR`, para chegar a 72/72.

## Reprodução do firmware a partir da fonte atual (2026-10-04)

**Recompilação flag1** de `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE`, em `backups/full_corpus_physical_deploy_20261003/source_rebuild_flag1_20261004/`:

| | Recompilado | Aprovado/físico |
|---|---|---|
| Programa | 1.098.195 B | 1.098.195 B |
| RAM | 126.148 B | 126.148 B |
| Imagem | 1.098.336 B | 1.098.336 B |
| SHA-256 | `627ac461f7bff718660e9cea05fb2641a6e9346b19228f60f26eed2b02e46d8d` | `2dc522590213db139187feee73d8c1ad6e49209ea933a551466ca15415cc6acc` (readback físico) |

**Comparação byte a byte:** 71 bytes diferem, todos metadados de build:
- `__TIME__`/`__DATE__` do sketch no offset 76.871: `19:02:04 Oct  3 2026` contra `01:24:34 Oct  4 2026`;
- SHA do ELF no app descriptor (0xB0–0xCF);
- hash final da imagem (32 B) e checksum.

Fora desses campos: **0 diferenças**. As datas internas das bibliotecas (Apr 13 2026) são idênticas. Não há diferença funcional.

**Fonte:** o diff contra `10e199f` se limita ao caminho rápido do catálogo (`lexV1ArtCatCandidatos` + uso em `lexV1ArtIdxPronto`), dentro de `#if LEX_DEVICE_V1_ENABLED`, com a varredura genérica anterior preservada como fallback.

## Regressão e reprodutibilidade (2026-10-04)

**Suítes:**

| Suíte | Resultado |
|---|---|
| DEVICE | 318/318 (inclui full corpus 17/17), 0 skip nesta execução |
| ENTENDA | 97/97 |
| LEGAL_TARGET_ID (inclui Reference Engine e RUN3) | 65/65 |

**Updater:** 104 testes.
- 101 PASS.
- 3 ERROR ambientais: `ModuleNotFoundError: truststore` em `test_importar_stf_controle_concentrado`, `test_importar_stf_repercussao_geral` e `test_importar_stf_sumulas_vinculantes`.
- `truststore` está em `updater/requirements.txt`, mas não está instalado em nenhum Python desta máquina.
- Esses arquivos não foram alterados nesta missão. Na execução anterior desta rodada, os 104 passaram.

**FAIL_REAL = 0.**

**Staging reproduzível:**
- 3 gerações completas byte-identical (`test_17`).
- Os 72 arquivos do staging são idênticos (size + SHA-256) aos do manifesto físico pós-deploy `sd_manifest_post_full.json`.

## Estado de parada

`FULL_CORPUS_INDEX_SD_PHYSICAL_PASS`: **SIM**.  
`FULL_CORPUS_INDEX_APP_ONLY_FLASH_PASS`: **SIM**.  
`FULL_CORPUS_INDEX_BOOT_PASS`: **SIM** (com o leitor alimentado).  
`FULL_CORPUS_INDEX_PHYSICAL_PASS`: **SIM** — `PHYSICAL_HUMAN_VALIDATION = APPROVED`.  
Commit: este relatório está no commit `LEX DEVICE V1: approve full corpus article indexes`.  
Tag anotada: `lex-device-v1-full-corpus-indexes-approved-2026-10-04`.  
Push: **NÃO**.
