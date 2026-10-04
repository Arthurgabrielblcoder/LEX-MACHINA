# LEX_CONTEXT_CITATION_GUARD — relatório físico

**Data:** 2026-10-04.

**Base:** commit `c7424f10327a4782cfa27d3f702a051221ee7050` / tag `lex-device-v1-72-indexes-approved-2026-10-04`.

**Correção:** `CONTEXT_CITATION_GUARD_REPORT.md`, completa (artigo, §, parágrafo único, inciso, alínea), conforme aprovado por Arthur. Os 68
casos ambíguos foram mantidos sem alteração.

**Estado:** **APROVADO.**
- `CONTEXT_CITATION_GUARD_PHYSICAL_PASS = PASS`;
- `PHYSICAL_HUMAN_VALIDATION = APPROVED` (Arthur, 2026-10-04);
- commit `LEX DEVICE V1: fix context citation false positives`, tag `lex-device-v1-context-citation-guard-approved-2026-10-04`;
- sem push.

**SD físico:** não alterado. O cartão ficou no aparelho; nada foi copiado e nenhum índice foi regenerado.

**Evidências** (fora do Git): `backups/context_citation_guard/flash/`.

## 1. Verificações antes do flash

| Item | Resultado |
|---|---|
| Leitor microSD / tela alimentado, SD instalado | Boot de referência com o firmware anterior (`serial_preflash_boot.log`, SHA-256 `ff4789b6…ed14`): `boot:0x2b`, `JUR CACHE`, `DIAG RESULT PASS pass=33 fail=0` |
| Porta | `COM3`, USB-Enhanced-SERIAL CH343 (1A86:55D3) |
| Chip | ESP32-S3 (QFN56) rev. v0.2, PSRAM 8 MB, MAC `e0:72:a1:f4:fd:28` |
| Flash | 16 MB detectados |
| Tabela de partições | `f3134b747fef242287f33aa0be8a5008958132e0c7611f5bc5bb917c02c9e397` = aprovada |
| `app0` | `0x10000`, `0x140000` |
| `otadata` | `0xe000`, `f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0` = aprovado (app0 ativo) |
| App em execução | Primeiros 1.098.336 B do `app0` = flag1 aprovado `2dc522590213db139187feee73d8c1ad6e49209ea933a551466ca15415cc6acc` |
| Backup integral do `app0` | `flash/app0_pre.bin`, 1.310.720 B, SHA-256 `9363247196b9b4180dc3a7e1cb7f98ef7a0ffe163933bd3095d96ab1f49b65e1` |

A primeira leitura do backup, a 921.600 baud, falhou por transferência (`Packet content transfer stopped`; só leitura). Foi repetida a
460.800 baud com sucesso.

**Candidato:** `backups/context_citation_guard/flag1/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin`.

| Campo | Valor |
|---|---|
| Programa | 1.099.791 B |
| RAM | 126.148 B |
| Imagem | 1.099.936 B |
| SHA-256 | `03df230ec132c0526b94c1f13eaa841c7d6ae1bc64a7330e8239d975ae38f495` (conferido antes do flash) |

## 2. Flash (APP-ONLY)

**Comando:**

```
esptool 5.4.0, --chip esp32s3 -p COM3 -b 460800
write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 <candidato>
```

**Resultado:** 1.099.936 B gravados em `0x10000`; `Hash of data verified`.

Bootloader, tabela de partições, `otadata`, NVS, `app1` e SPIFFS não foram alvos.

**Readback independente** (`flash/app0_readback.bin`): 1.099.936 B, SHA-256 `03df230e…f495`, byte-identical ao candidato
(**READBACK_MATCH**).

**Partições e `otadata`, antes e depois:** byte-identical (`f3134b74…e397` / `f94c5d78…17f0`).

## 3. Boot

**Log:** `flash/serial_boot_and_tests.log`, 36.788 B, SHA-256 `667f9bf8572e9b259da40d88e7896391545374408a4e6131dc047d92c2f869d9`. Cobre o boot e
toda a sessão de testes.

| Critério | Resultado |
|---|---|
| SD montado | `rst:0x1 (POWERON),boot:0x2b` |
| Autoteste do parser (inclui os 22 casos novos) | `TESTE CONTEXTO JURIDICO: OK` |
| JUR CACHE | `lookups=178 registros=296 ... fonte=CACHE` |
| DIAG | `LEXV1: DIAG RESULT PASS pass=33 fail=0 MAX_OPEN_COUNT=4` |
| FAIL_IO / CHECK FAIL / panic / Guru / watchdog / Backtrace / SD indisponível | **0** |
| Reboots na sessão | 0 (uma única linha `rst:`) |

## 4. Testes físicos (serial + Arthur)

| # | Teste | Serial | Resultado |
|---|---|---|---|
| A | MARIA2006 art. 1, passando por "§ 8º do art. 226 da Constituição Federal" | Sequência `BUSCA Art. 1` → `ART=1` → `ART=2` → `ART=1` → `ART=2`. **Nenhum `PAR=8`.** | **PASS** |
| A | Mudança para art. 2 só no cabeçalho real, e volta (UP) sobre a remissão | `ART=2` no `Art. 2º`; ao subir, `ART=1` sem PAR | **PASS** |
| B | Remissão de artigo: art. 44, linha "art. 129 do Decreto-Lei nº 2.848" | `ART=44`; **nunca `ART=129`** | **PASS** |
| B | Remissão de § e de artigo: art. 16-A, "§ 3º do / art. 100 do Decreto-Lei" | `ART=16` → `PAR=unico` → `ART=16-A`; **sem `PAR=3` e sem `ART=100`** | **PASS** |
| C | Parágrafo único real | MARIA art. 5 `PAR=unico`; art. 16 `PAR=unico`; art. 12-D `PAR=unico`; CF 193 `PAR=unico` (ACTIVE_TARGET `CF88:ART.193:PAR.UNICO`) | **PASS** |
| C | Inciso real | MARIA art. 5 I–III; art. 7 I–VI; art. 12 I–VII; art. 12-C I–III; CF art. 37 incisos I…XXII | **PASS** |
| C | Alínea real | MARIA art. 22 III a), b), c), depois IV; CF art. 37 XVI b) (ACTIVE_TARGET `CF88:ART.37:INC.XVI:AL.b`) | **PASS** |
| C | § real | MARIA art. 12 §§ 1–3 (com incisos do § 1º); 12-B §§ 1–3; 12-C §§ 1–2 | **PASS** |
| D | CF art. 37 § 6 | `ACTIVE_TARGET=CF88:ART.37:PAR.6` + `CONTEXTO: ART=37 PAR=6` | **PASS** |
| D | CF art. 193 e camadas | ACTIVE_TARGET 193 / 192 § 3 / 193 parágrafo único / 194, sempre sincronizado com o CONTEXTO; camadas corretas segundo Arthur | **PASS** |
| D | ACTIVE_TARGET × CONTEXTO na CF | Em todos os 34 eventos da CF, a tupla do CONTEXTO = ACTIVE_TARGET do TEXT_MAP | **PASS** |
| 1–5 | Busca, pouso, DOWN, UP, voltar sobre a remissão | 10 buscas MARIA/CF com pouso correto; DOWN e UP estáveis | **PASS** |
| E | Fluidez | Arthur: sem atraso novo | **PASS** |

Arthur digitou 373 e 137 por engano: `NAO ENCONTRADO` e o art. 137, ambos com o comportamento correto. Não afetam o resultado.

**Performance (`PERF CONTEXTO_ATUALIZAR`):**

| Situação | Antes (firmware anterior, sessão MARIA2006 de 2026-10-04) | Agora |
|---|---|---|
| MARIA2006 | mediana 614 µs (máx. 640, n=33) | mediana 607 µs (máx. 735, n=62) |
| CF | — | cerca de 54 ms (n=34) |

Na CF, o tempo inclui a consulta do ACTIVE_TARGET ao TEXT_MAP no SD. A única amostra CF do firmware anterior foi 49,8 ms. É o mesmo custo
de I/O, que esta missão não alterou.

O `PERF SCROLL` ficou com média entre 73 e 98 ms, sem travamentos.

**Sem impacto mensurável do guard.**

## 5. Observação (não bloqueante, fora do escopo)

**Onde:** no art. 44 da MARIA2006, a serial mostrou `CONTEXTO: ART=44 PAR=9`.

**Não é remissão.** É o **texto citado da norma alterada**. O art. 44 transcreve, entre aspas, o novo § 9º do art. 129 do Código Penal:

```
"Art. 129. ......
§ 9º
Se a lesão for praticada contra ascendente...
```

A linha `§ 9º` tem a forma de um cabeçalho estrutural real e está sozinha na linha. Por isso pertence aos casos que a própria linha não
decide. Distinguir texto transcrito entre aspas exigiria novo estado (aspas abertas), o que esta missão proíbe.

**Situação:**
- Arthur avaliou o funcionamento como correto;
- o comportamento é igual ao do firmware anterior, que não foi alterado nesse ponto;
- fica registrado como classe própria ("dispositivos transcritos em artigo alterador") para decisão futura.

## 6. Critérios

| # | Critério | Resultado |
|---|---|---|
| 1 | MARIA2006 art. 1 não vira PAR.8 | ✅ |
| 2 | Remissão de artigo não muda ART | ✅ (art. 44 / 129; art. 16-A / 100) |
| 3 | Parágrafo estrutural real funciona | ✅ |
| 4 | Inciso estrutural real funciona | ✅ |
| 5 | Alínea estrutural real funciona | ✅ |
| 6 | Parágrafo único funciona | ✅ |
| 7 | Busca e pouso continuam corretos | ✅ |
| 8 | Scroll continua fluido | ✅ |
| 9 | Camadas continuam corretas | ✅ |
| 10 | Nenhum crash, reboot ou erro de SD | ✅ |

**Resultado: `CONTEXT_CITATION_GUARD_PHYSICAL_PASS`.**

## 7. Rollback (se necessário)

Gravar `flash/app0_pre.bin` em `0x10000` (APP-ONLY) e conferir o readback. Os primeiros 1.098.336 B são o flag1 aprovado `2dc52259…cc6acc`.

## 8. Validação humana

**`PHYSICAL_HUMAN_VALIDATION = APPROVED`**, aprovação formal de Arthur em 2026-10-04.

Arthur confirmou:
- MARIA2006 art. 1 sem `PAR=8` na remissão ao § 8º do art. 226 da CF;
- art. 44 nunca vira `ART=129`;
- art. 16-A não vira `PAR=3` nem `ART=100`;
- parágrafo único, parágrafos, incisos e alíneas reais funcionando;
- CF art. 37 § 6 com CONTEXTO e camadas corretos;
- CF art. 193 correto;
- busca e pouso rápidos;
- scroll fluido;
- nenhum reboot, nenhum erro de SD, nenhum impacto de performance percebido.

**Performance física:** mediana do CONTEXTO 614 µs antes, 607 µs depois. Sem regressão.

**Nova limitação registrada** (não bloqueante, não corrigida nesta missão): `KNOWN_LIMITATION_CONTEXTO_EM_TRANSCRICAO_LEGISLATIVA.md`
(MARIA2006 art. 44, § 9º transcrito do art. 129 do CP).

## 9. Regressão final

| Suíte | Resultado |
|---|---|
| DEVICE | 353/353, 0 skip |
| ENTENDA | 97/97 |
| LEGAL_TARGET_ID | 65/65 |
| Updater | 113/116; 3 ERROR ambientais (`truststore`), os mesmos de antes |

**Falha intermitente no Updater, ambiental:** em cerca de 1 de cada 5 execuções completas, um teste diferente dos importadores falha.
Exemplos: `test_preserva_controle_e_outras_categorias`, `test_sucesso_preserva_outras_entradas`, `test_cancelada_nao_importada`.

- **Causa capturada:** `[WinError 5] Acesso negado` no `os.replace` de `catalogo.json.tmp` → `catalogo.json`, em diretórios temporários de
  `updater/saida/`. Outro processo do Windows (antivírus ou indexador) bloqueia o arquivo por um instante.
- **Comportamento:** cada teste passa isolado e nas demais execuções. O código dos importadores não foi alterado nesta missão.
- **Classificação:** `FAIL_AMBIENTAL`, não `FAIL_REAL`.

**FAIL_REAL = 0.**

## 10. Baseline

| Campo | Valor |
|---|---|
| Anterior | `lex-device-v1-72-indexes-approved-2026-10-04` (preservada) |
| Nova tag | `lex-device-v1-context-citation-guard-approved-2026-10-04` |
| Firmware físico | flag1 `03df230ec132c0526b94c1f13eaa841c7d6ae1bc64a7330e8239d975ae38f495` (1.099.936 B) |
| SD físico | inalterado (72/72 índices, catálogo `8d7d11db…a4c9`) |
| Fora do commit | `backups/` (imagens, dumps de flash, logs seriais, JSON da auditoria), binários e caches |
