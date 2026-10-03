# BATCH04 + RUN3 — plano de implantação física (NÃO EXECUTADO NESTA MISSÃO)

**Pré-requisitos:** revisão do candidato por Arthur e autorização explícita para cada fase que escreve, que são **C** (SD) e **G** (flash).

**Candidato:**

| Item | Detalhe |
|---|---|
| SD | `DEVICE_INTEGRATION/staging_sd_v1_batch04_run3_candidate/SD/99_LEX_V1/`: 7 arquivos a substituir, ver `BATCH04_RUN3_SD_DIFF_PLAN.md` |
| App | `DEVICE_INTEGRATION/backups/batch04_run3/candidate_flag1/candidate_app_batch04_run3.bin`: 1.097.376 B, sha256 `d12c7fceafcb13b02f789269d6aaf2b7ed77f06be003c6f502b8b69aa01ee8f6`, checksum e hash válidos |
| Fonte do app | `backups/batch04_run3/src_candidate/LEX_MACHINA_DEVICE_V1_CANDIDATE/`: sketch da baseline `6d0194b` + `lex_ref_detail_data.h` do RUN3 (`2ca5820a…710b`) |

**Rollback:**
- **App:** imagem lida na fase G (`app0_prewrite.bin`). Hoje o aparelho roda `candidate_app_cc_index.bin`, `f23e77cd…dfbb`.
- **SD:** os 7 arquivos salvos na fase B.

## FASE A — Arthur retira o SD do LEX MACHINA e coloca no PC
1. Desligar o LEX MACHINA (ou deixá-lo sem tocar no cartão) e retirar o microSD.
2. Inserir no PC e informar a letra da unidade.
3. Conferir: FAT32, volume de ~31,9 GB, raiz com as pastas da Lei Seca e `99_LEX_V1`.

## FASE B — backup e manifesto físico (somente leitura)
1. Gerar o manifesto completo (path, bytes, sha256 de todos os arquivos) em `backups/batch04_run3/sd_manifest_pre.json`.
2. Comparar com `backups/cc_index/sd_manifest_post.json`:
   - os 1.071 arquivos devem estar presentes e iguais;
   - exceção tolerada: `System Volume Information`, que é do Windows.
   - **Divergência → PARAR.**
3. Copiar os 7 arquivos que serão substituídos para `backups/batch04_run3/sd_pre/99_LEX_V1/…` e conferir os hashes.

## FASE C — copiar somente o staging necessário de `/99_LEX_V1`
1. Copiar **somente** os 7 arquivos REPLACED do candidato para os mesmos caminhos no cartão:
   - `00_SYS/LEXV1.VER`
   - `00_SYS/LEX_DEVICE_MANIFEST.json`
   - `10_TARGETS/CF88_TARGETS.IDX`
   - `20_REFERENCES/REF_LOOKUP.IDX`
   - `20_REFERENCES/REF_PAYLOAD.IDX`
   - `30_ENTENDA/ENTENDA_LOOKUP.IDX`
   - `30_ENTENDA/ENTENDA_PAYLOAD.DAT`
2. Não tocar em:
   - `05_TEXT/CF88_RUNTIME.txt`
   - `10_TARGETS/CF88_TEXT_MAP.IDX`
   - `10_TARGETS/CF88_ARTICLE_SEARCH.IDX`
   - `10_TARGETS/CC2002_ARTICLE_SEARCH.IDX`
   - nenhum arquivo fora de `/99_LEX_V1`
3. Esvaziar o cache de escrita do volume (`Write-VolumeCache`).

## FASE D — readback e hash
1. Reler os 7 arquivos e exigir sha256 = coluna "candidato" do diff plan.
2. Gerar `sd_manifest_post.json`. A comparação com o pré deve dar **exatamente 7 alterados, 0 adicionados e 0 removidos**; os outros 1.064 arquivos ficam idênticos.
3. **Divergência → restaurar os 7 arquivos da fase B e PARAR.**

## FASE E — ejetar o SD com segurança
"Remover hardware com segurança" para a unidade e aguardar a confirmação do Windows.

## FASE F — Arthur recoloca o SD no LEX MACHINA
Inserir o microSD no aparelho e avisar.

## FASE G — flash app-only
1. **Pré-condições (leitura):**
   - `flash-id`: ESP32-S3 v0.2, MAC `e0:72:a1:f4:fd:28`, flash 16 MB, porta COM3;
   - partições em 0x8000: app0 0x10000/0x140000, sha `148b959c…`;
   - otadata em 0xE000: slot0 seq=1;
   - backup de `app0_prewrite.bin` (0x140000 B).
2. Gravar:
   `python -m esptool --chip esp32s3 --port COM3 --before default-reset --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 candidate_app_batch04_run3.bin`
3. Não gravar bootloader, tabela de partições, NVS, otadata, app1 nem spiffs.

## FASE H — readback
1. `read-flash 0x10000 1097376`: deve ter sha256 `d12c7fce…e8f6` e `cmp` idêntico, ou seja, **PHYSICAL_READBACK_MATCH = TRUE**.
2. Reler partições e otadata: devem estar inalterados.
3. Falha → regravar `app0_prewrite.bin`, ler de volta e PARAR.

## FASE I — teste físico (serial capturado; logs de benchmark desligados no build)

**Boot:**
- 1 reset POWERON, sem panic e sem reboot loop.
- `TESTE CONTEXTO JURIDICO: OK`.
- `DIAG RESULT PASS` com `fail=0`.
- `runtime hash CONFERE`.
- schema 3 aceito, com `ENTENDA_COUNT=220`.

**CF:**
1. Abrir a CF, buscar 230 (rápido) e buscar 193: CONTEXTO ART. 193 e 4 REF com *Capital no Século XXI*, *Desigualdade para Todos* e *O Triunfo da Injustiça*.
2. ENTENDA (tecla 3) nos arts. 25, 29-A (via rolagem a partir do 29), 34 e 36:
   - texto aprovado;
   - no art. 34, o glossário diz "restringe temporariamente";
   - no art. 35, "restringe temporariamente a autonomia do Município, nos limites necessários à intervenção".
3. Camada 4:
   - art. 37 → *Os Donos do Poder*, *Raízes do Brasil*; os incisos e §§ do art. 37 sem essas obras;
   - art. 43 → *Formação Econômica do Brasil*;
   - art. 43 §2 IV → *Vidas Secas*;
   - art. 62 → *Suzerain*;
   - art. 201 I → *Eu, Daniel Blake*;
   - art. 7 XXXIII → *Frostpunk*;
   - ADCT 68 → *Torto Arado*.
4. Arts. 98 e 202: target certo e sem 4 REF (lacuna esperada).
5. Busca 5 → ENTER, ENTER → ADCT 5 → ENTER, ENTER → SEM OUTRA OCORRÊNCIA.

**CC:**
1. Abrir o CC e buscar 2000: ART. 2000 (nunca ART. 2), busca rápida; 1 UP imediato; rolagem 1999 ↔ 2001.
2. Voltar à CF e buscar 193: o índice correto acompanha o texto.

**Geral:** fluidez igual à baseline aprovada, sem crash e sem reboot.

Ao final: `PHYSICAL_HUMAN_VALIDATION` pelo Arthur. Commit, tag e push só depois disso, com autorização.
