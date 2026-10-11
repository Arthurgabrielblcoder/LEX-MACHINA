# FULL CF ENTENDA 810 — relatório de pré-deploy (pacote host)

Data: 2026-10-11. Fonte canônica: `reconcile-macro07-macro08` @ `fa9719a6bd335275252473a5f154e4e11f5532f4`:
- 810 ACTIVE, 810 HUMAN_APPROVED_T1, 0 pendentes;
- Macro07 249/249 CLOSED, Macro08 179/179;
- 0 aprovações perdidas, 0 conflitos ativos.

**Estado: PACOTE HOST PASS. Nada foi gravado no microSD nem no flash.**

**Decisão pendente:** o autodiagnóstico do firmware aprovado (ver §5).

## 1. Baseline física real

O pacote de referência é o BATCH04+RUN3 (`staging_sd_v1_batch04_run3_candidate`, 220 ENTENDA), mas o cartão aprovado é posterior:
- **04/10** — índices de artigo do corpus completo: +70 arquivos;
- **04/10** — MARIA2006: TXT, catálogo e +1 índice;
- **04/10** — flash app-only da guarda de citação de contexto: flag1 `03df230e…f495`, SD inalterado.

O último manifesto físico aprovado é `backups/maria2006_physical_deploy_20261004/sd_manifest_post_full.json`: 1.142 arquivos, 82 em `/99_LEX_V1`, 72 índices de artigo.

Os 11 arquivos do pacote BATCH04+RUN3 estão nesse cartão sem mudança, porque as etapas de 04/10 só adicionaram arquivos ou trocaram arquivos fora desses 11. O diff abaixo vale contra esse estado.

## 2. Builder

- **Novo perfil explícito:** `FULL_CF_ENTENDA_810`, em `tools/build_sd_staging.py`, e `tools/build_full_entenda_810_candidate.py`, que faz 3 builds, compara e gera o manifesto host.
- **Seleção derivada dos corpora reais** (`approved_entenda_chain`): união dos registros ACTIVE/HUMAN_APPROVED_T1 de:
  - corpus principal;
  - `prior_corpora` do `MACRO_SPEC` do Macro08;
  - corpus do Macro08.

  É fail-closed: falha se houver ACTIVE não aprovado, target ou chave duplicados, cobertura de bloco conflitante ou piloto ausente. Nenhum target é enumerado.
- **Contabilidade derivada:** 382 (base + Batch01–06) + 249 (Macro07) + 179 (Macro08) = **810**.
- **Contextos:**
  - cada T1 é validado e renderizado por `entenda_engine.build_entenda_index` no contexto em que o lote foi aprovado. O Macro08 usa o perfil `CF88_OFFICIAL_RUNTIME`, derivado do próprio runtime físico `7ef82290…`, e os demais lotes usam a config base;
  - os blocos são compostos num único par, no mesmo layout de `build_entenda_index`: mesmo cabeçalho, blocos e lookup ordenados por target, mesmo formato de linha;
  - a regra de hierarquia entre grupos é reaplicada;
  - runtime, targets e TEXT_MAP usam sempre a config base.
- **Baselines históricas preservadas:**
  - default (163): 9/9 arquivos byte-idênticos a `staging_sd_v1`, com `build_commit=c1fb3df`, como no original;
  - BATCH04_RUN3 (220): 11/11 idênticos ao staging aprovado.
- **Ambiente:** o export do runtime exige a cópia de verificação `updater/fontes_oficiais_verificacao/EC45_2004/planalto_raw.html` com sha256 `76f9b562…`. Esses bytes existem só no checkout principal: nem o blob versionado (LF, `0c46…`) nem a conversão CRLF (`e8c1…`) os reproduzem. Usei a cópia do checkout principal sem commitá-la. Fica registrado como `MATERIALIZATION_DEBT` preexistente; o exportador confere o hash e falha fechado.

## 3. Pacote (`staging_sd_v1_full_entenda_810_candidate`, build_id `de963699728cb66e`)

| Arquivo `/99_LEX_V1/…` | Bytes | sha256 | × BATCH04+RUN3 |
|---|---|---|---|
| `00_SYS/LEXV1.VER` | 585 | `2be2e369…` | REPLACE |
| `00_SYS/LEX_DEVICE_MANIFEST.json` | 7.646 | `7394cb6a…` | REPLACE |
| `05_TEXT/CF88_RUNTIME.txt` | 587.133 | `7ef82290…` | igual |
| `10_TARGETS/CF88_TARGETS.IDX` | 165.466 | `616a469b…` | REPLACE |
| `10_TARGETS/CF88_TEXT_MAP.IDX` | 123.578 | `889f8200…` | igual |
| `10_TARGETS/CF88_ARTICLE_SEARCH.IDX` | 5.216 | `56e437a0…` | igual |
| `10_TARGETS/CC2002_ARTICLE_SEARCH.IDX` | 25.036 | `674c9971…` | igual |
| `20_REFERENCES/REF_LOOKUP.IDX` | 6.955 | `6d6c88d7…` | igual (RUN3) |
| `20_REFERENCES/REF_PAYLOAD.IDX` | 68.075 | `24b4f0d9…` | igual (RUN3) |
| `30_ENTENDA/ENTENDA_LOOKUP.IDX` | 110.312 | `017050dc…` | REPLACE |
| `30_ENTENDA/ENTENDA_PAYLOAD.DAT` | 1.560.621 | `dbea7260…` | REPLACE |

- **Diff real:** exatamente os 5 arquivos previstos; nenhum inesperado.
- **`LEXV1.VER`:** `DEVICE_VERSION 3`, `ENTENDA_COUNT 810`, `ENTENDA_SCOPE CF88_ADCT_FULL_HUMAN_APPROVED_T1`, `GIT_COMMIT fa9719a…`, `TARGETS 3810`. O runtime continua `7ef82290…`/587.133 e o `REFERENCE_ENGINE` continua `cf-reference-engine-run3`.
- **Determinismo:** 3 builds byte-idênticos.

## 4. Validação host

**Lookup:**
- 1.069 linhas: 810 DIRECT + 259 COVERED_BY_BLOCK;
- chaves únicas, ordenadas bytewise, todas `HUMAN_APPROVED_T1`;
- maior linha: 130 B.

**Payload:**
- 810 blocos contíguos que cobrem o arquivo inteiro;
- todo bloco começa por `@<EXPLANATION_ID>` e termina em `@END`;
- toda linha BLOCK aponta para o bloco da âncora;
- maior bloco: 4.830 B (limite do motor: 6.144 B).

**Os 220 físicos:**
- as 362 linhas do lookup de 220 estão idênticas (linha e bytes do bloco): 362 unchanged, 0 superseded, 0 removed, 0 conflicts;
- +707 linhas novas.

**Blocos × índice próprio de cada lote:**
- 648 idênticos e 89 sem índice próprio (finais e pilotos);
- 73 diferem só em metadados não exibidos:
  - `R|` PENDING→APPROVED e `D|`: título final contra os índices de rascunho dos lotes 01–03;
  - `N|`: contagem de referências do contexto.

  As seções não mudam.

**`CF88_TARGETS.IDX`:**
- 3.810 linhas, igual à baseline;
- E = 810 e B = 259, iguais ao lookup;
- tipo, status e colunas C/J/W/R inalterados;
- a coluna X (camada externa ou nota temporal do ENTENDA) é derivada dos blocos e mudou em 309 targets novos.

**Simulador do firmware** (`device_lookup_simulator`):
- todas as 1.069 linhas resolvem, com no máximo 11 seeks;
- amostra: art. 5, 5 V (BLOCK), 37, 76, 100, 100 § 10 (BLOCK), 142, 156-A, 175, 225, ADCT 10 II e ADCT 101 resolvem;
- `CF88:ART.999` falha fechado e `CF88:ART.114:INC.VIII` fica sem ENTENDA (sem camada 3).

**Benchmark host:**

| Consulta | 220 | 810 |
|---|---|---|
| Lookup ENTENDA (média) | 58,6 µs, máx. 8 seeks | 67,3 µs, máx. 10 seeks |
| Lookup + payload | 75,0 µs | 78,3 µs |
| Resolução BLOCK | 123 µs | 91 µs |

O limite log2 do lookup passa de 9 para 10 seeks. Nada carrega o arquivo inteiro.

## 5. Firmware aprovado (flag1, `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE`)

Auditoria do código:
- Não há limite fixo de 163 ou 220: os únicos `220` são coordenadas de tela, e nenhuma comparação usa `entendaCount`.
- `ENTENDA_COUNT` é lido para `uint16_t` (810 < 65.536) e só se exige que seja > 0.
- O lookup é busca binária no arquivo (`LEXV1_WINDOW` 512), sem cache de quantidade. O payload é lido por seek + leitura de `BYTES`.
- **Limites, todos atendidos:**

  | Limite | Valor | Pacote |
  |---|---|---|
  | `LEXV1_BLOCO_MAX` | 8.192 | maior bloco 4.830 |
  | `LEXV1_CAMADA_TXT_MAX` | 16.384 | — |
  | `LEXV1_LINE_MAX` | 256 | maior linha de lookup 130 |
  | `LEXV1_TITLE_MAX` | 160 | maior título 139 |
  | `LEXV1_KEY_MAX` | 48 | maior chave 27 |
  | ID | 64 | maior ID 41 |
  | glossário | 255 por parte | maior parte 193 |

  As linhas longas do corpo (até 1.739 B; na baseline, 718 B) são lidas para o buffer do bloco e quebradas por largura, sem limite por linha.
- `DEVICE_VERSION` continua 3.

**Achado — autodiagnóstico de boot:**
- O DIAG tem 10 casos fixos (`casos[]` em `LEX_MACHINA_DEVICE_V1_CANDIDATE.ino`).
- O caso `{"CF88:ART.127",true,LEXV1_RES_NONE,"",1,1}` exige o art. 127 **sem ENTENDA**, mas o Macro07 aprovou o art. 127.
- Com o pacote de 810, o DIAG deve terminar `DIAG RESULT FAIL pass=32 fail=1`. Os outros 9 casos passam; `CF88:ART.114:INC.VIII` continua sem ENTENDA.
- `lexV1Pronto`, que habilita as camadas V1, não depende do resultado do DIAG. A tecla 3 e a leitura do ENTENDA funcionam, inclusive no próprio art. 127.
- É o mesmo tipo de expectativa desatualizada que superou o r1.
- Teste permanente: `test_firmware_fixed_diag_case_art127_is_the_only_stale_expectation`.

Nenhuma incompatibilidade de leitura exige flash. **Exigir DIAG PASS exige flash.**

| Opção | Firmware | DIAG |
|---|---|---|
| **A. SD-only** | flag1 atual | `FAIL fail=1`, caso desatualizado documentado |
| **B. SD + app-only** | atualizar só a expectativa do caso art. 127 (por exemplo, `CF88:ART.127` → DIRECT, mantendo a contagem de referências 1/1) | `PASS 33/33` |

## 6. Testes

| Suíte | Novo | Baseline `fa9719a` (mesmo worktree CRLF e mesmas entradas) |
|---|---|---|
| DEVICE_INTEGRATION | 353 testes; 4 falhas preexistentes | 344; as mesmas 4 |
| `test_full_entenda_810` (novo) | 9/9 | — |
| LEGAL_TARGET_ID | 77; 1 erro preexistente | igual |
| ENTENDA_ENGINE | 284; 5 preexistentes (artefatos fixados em LF num checkout CRLF; validados em LF na reconciliação) | igual |

As 4 falhas preexistentes do DEVICE_INTEGRATION são de materialização no worktree: bytes CRLF do fonte do firmware e um manifesto de backup ausente.

## 7. Deploy SD (preparado, não executado)

- `tools/deploy_full_entenda_810_sd.py pre|copy|verify <unidade>`. As substituições vêm do manifesto host. O `pre` exige o cartão idêntico ao manifesto MARIA2006 e os 5 arquivos no estado BATCH04+RUN3, e faz backup verificável dos 5.
- O `copy` usa `.LEX_NEW` + `fsync` + readback + `os.replace`, na ordem payload → lookup → targets → manifesto → `LEXV1.VER`.
- Depois, `Write-VolumeCache <unidade>`, `verify` e ejeção segura.
- Ensaio num cartão simulado: PRE_OK → COPY_OK 5 → SD_VALIDATED; um cartão divergente gera PARAR.
- O microSD não estava conectado ao PC.
- **Rollback:** copiar os 5 arquivos de `backups/full_entenda_810_physical_deploy/sd_pre/99_LEX_V1/` de volta.
