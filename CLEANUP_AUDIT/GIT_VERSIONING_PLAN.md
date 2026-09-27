# Plano de versionamento Git — ONDA 0

Data: 2026-09-26. Base: `INVENTARIO_REPOSITORIO.json` e `PROTEGIDO_NAO_TOCAR.json` da auditoria; a análise global não foi refeita.

- **Proibido:** `git add .`
- **Somente paths explícitos** dos grupos VERSIONAR abaixo.
- **Commit apenas local.** Não fazer push.

## Verificações feitas nos candidatos a VERSIONAR

- **Candidatos:** 1.161 arquivos, 39,7 MB. O maior arquivo tem 1,6 MB.
- **Tamanho:** nenhum arquivo acima de 50 MB ou de 100 MB. Não há binários grandes; os únicos binários são o PNG de preview, 40 KB, e o header de imagem do boot, 627 KB de texto.
- **Varredura de segredos:** chaves privadas, AWS, GitHub, OpenAI/Anthropic, Google, Slack, Bearer, atribuições `api_key`/`token`/`password`/`senha`/`secret`/`cookie`, credenciais Wi-Fi no firmware e arquivos sensíveis por nome (`.env`, `.pem`, `.key`, `credentials.json`).
  - **1 achado:**

    | Path | Tipo de risco |
    |---|---|
    | `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/03_FONTES/BUSCA_118.json` | URL pré-assinada AWS S3 de terceiro (identificador de chave de acesso + assinatura) capturada em resultado de busca |

  - O arquivo fica classificado como **BLOQUEADO_POR_SEGREDO**: não é adicionado ao Git e fica preservado apenas no snapshot. O valor não foi exibido nem corrigido.
  - Scripts do updater não versionados (`implantar_sd.py`, `relations_v2.py` e testes): nenhum achado.
- **Fins de linha:** `core.autocrlf=true`. O índice normaliza CRLF para LF, mas os arquivos de trabalho não são tocados.

## A) Código e configuração crítica

| Grupo | Paths | Decisão | Justificativa |
|---|---|---|---|
| A1 | `LEX_MACHINA_REFERENCIAS_V2/05_COMPILADOR/`, `01_SCHEMA/`, `02_DISPOSITIVOS/`, `04_CONCEITOS/`, `tests/`, `README.md` | **VERSIONAR** | Engine R1D1, ontologia e contratos: núcleo sem nenhuma cópia versionada |
| A2 | `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/**/*.py` (scripts da expansão e do enriquecimento) | **VERSIONAR** | Necessários para reproduzir o catálogo e o ENRIQUECIDO_V1 |
| A3 | `firmware/LEX_MACHINA.ino/LEX_MACHINA.ino.ino` (modificado) e `firmware/LEX_MACHINA.ino/assets/` | **VERSIONAR** | Sketch ativo e assets que ele inclui; o diff foi preservado antes em `FIRMWARE_PRE_CLEANUP.diff` |
| A4 | `updater/implantar_sd.py`, `updater/relations_v2.py`, `updater/test_implantar_sd.py`, `updater/test_relations_v2.py` | **VERSIONAR** | Scripts ativos do updater, fora do Git; sem segredos |
| A5 | `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/*.py` | **VERSIONAR** | Adaptador que gerou o catálogo 69 |

## B) Dados curados importantes

| Grupo | Paths | Decisão | Justificativa |
|---|---|---|---|
| B1 | `LEX_MACHINA_REFERENCIAS_V2/03_OBRAS/`, `08_RELEASE_CANDIDATE/` (RC1 e RC2 com `DECISOES_HUMANAS.json`), `00_CHECKPOINTS/`, `06_BENCHMARKS/`, `07_EXECUCAO_COMPLETA/`, `09_RELATORIOS/` | **VERSIONAR** | Provas congeladas, revisão humana e benchmarks: tudo pequeno (JSON) |
| B2 | Holdout: `00_CHECKPOINTS/HOLDOUT_RESERVATION.json`, `06_BENCHMARKS/HOLDOUT_V2_BLIND.json` | **VERSIONAR (local)** | Proteção contra perda. **REVISAR antes de qualquer push**: o remote `origin` é GitHub e o holdout deve permanecer cego |
| B3 | `09_CATALOGO_EXPANSAO_200/` (entradas, identidade, triagem, fontes, dossiês, overlays, rejeitadas, relatórios, checkpoints, catálogos, **ENRIQUECIDO_V1**, manifests) | **VERSIONAR**, exceto B4 e B5 | Curadoria de 200 obras e pacote congelado |
| B4 | `09_CATALOGO_EXPANSAO_200/03_FONTES/BUSCA_118.json` | **NAO_VERSIONAR — BLOQUEADO_POR_SEGREDO** | Ver varredura de segredos acima; preservado no snapshot |
| B5 | `09_CATALOGO_EXPANSAO_200/06_RELATORIOS/CONSULTA_CP11.txt` e `CONSULTA_CP12.txt` | **NAO_VERSIONAR** | Captura web bruta com texto de páginas de terceiros, parcialmente binária. A proveniência (URL, data, hash) já está versionada em `03_FONTES/ENRIQUECIMENTO_V1/`. Preservados no snapshot |
| B6 | `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/*.json` e `.md` (inclui `CATALOGO_69_CANONICO.json`) | **VERSIONAR** | Catálogo original de 69 obras |

## C) Artefatos gerados e binários

| Grupo | Paths | Decisão | Justificativa |
|---|---|---|---|
| C1 | 130 `**/*.IDX` (4,25 MB, espalhados por `saida/` de 27 cópias) | **NAO_VERSIONAR → IDX_SNAPSHOT_APENAS** | Ver política IDX abaixo |
| C2 | `updater/saida/` (935 arquivos, 62 MB) | **NAO_VERSIONAR** (snapshot) | Mistura de output reproduzível e dados baixados; ver política |
| C3 | Zips de etapa (4 × ~29 MB), `saida.zip`, zip do firmware v7.10.1 | **NAO_VERSIONAR** | Pacotes redundantes com as pastas |

## D) Outputs reproduzíveis

| Grupo | Paths | Decisão | Justificativa |
|---|---|---|---|
| D1 | `**/.venv/`, `**/__pycache__/`, `**/.pytest_cache/` | **NAO_VERSIONAR** | Recriáveis |
| D2 | `CLEANUP_AUDIT/INVENTARIO_REPOSITORIO.json` (24 MB), `DEPENDENCIAS.json` (12 MB), `DUPLICATAS_EXATAS.json` (7,6 MB), `_ESTATISTICAS.json` (2,5 MB) | **NAO_VERSIONAR** | Reproduzíveis por `_auditoria_higiene.py` e `_gerar_relatorios_auditoria.py`; preservados no snapshot |
| D3 | Demais arquivos de `CLEANUP_AUDIT/` (md, scripts, `PROTEGIDO_NAO_TOCAR.json`, `ORFAOS_CANDIDATOS.json`, integridades, diff do firmware, plano e políticas) | **VERSIONAR** | Documentação da limpeza, pequena e necessária para as próximas ondas |

## E) Backups e legado

| Grupo | Paths | Decisão | Justificativa |
|---|---|---|---|
| E1 | `updater/backup_sd/` | **NAO_VERSIONAR** (snapshot) | Ver política `backup_sd` |
| E2 | `firmware/LEX_MACHINA_v7.11.0_*`, `v7.11.1_*`, `LEX_MACHINA_BACKUP_POS_CODEX_16-09/`, zip v7.10.1 | **REVISAR** | Versões intermediárias; incluídas no snapshot; decidir depois entre `firmware/releases/` versionado e archive |
| E3 | `LEX_MACHINA_REFERENCIAS_*_V1…ALPHA3`, `CF_SEGMENTADA_V2` (parte do `protected545`) | **REVISAR** | Histórico da engine; os arquivos da prova estão no snapshot e **não podem mudar de path** (ver `PROTECTED545_POLICY.md`) |
| E4 | `LEX-MACHINAETAPA_*`, `LEX_MACHINA_UPDATER_*`, `updater_stage2a_corrigida_v2`, `LEX_MACHINA_JURIS_CF_*` | **NAO_VERSIONAR** | Cópias volumosas e redundantes (2,5 GB duplicados). Candidatas a archive na ONDA 4 |
| E5 | `LEX_MACHINA_PRE_CLEANUP.bundle` e `LEX_MACHINA_CRITICAL_UNTRACKED_PRE_CLEANUP.zip` | **NAO_VERSIONAR** | Artefatos de segurança, mantidos fora do repositório |

## Políticas

**IDX → IDX_SNAPSHOT_APENAS**

- **Formato:** índices binários `ARTIGOS.IDX`, `JURIS.IDX`, `MENU.IDX`, `NORMAS.IDX` e `NORMAS_BIN.IDX`, consumidos pelo firmware ESP32 no microSD. Total: 130 arquivos, 4,25 MB.
- **Geração:** scripts do updater (`gerar_indice_esp32*.py`, `gerar_indices_binarios_v1.py`), a partir de LEXDATA construído com os caches de fontes (`cache_lexdata_*`, parcialmente versionados).
- **Reprodutibilidade:** não verificada byte a byte, e depende de fontes remotas. Por isso não é IDX_REPRODUZIVEL_COM_MANIFEST.
- **Onde ficam:** quase todos em `saida/` de cópias legadas. O firmware precisa deles diretamente, via cartão SD.
- **Proteção:** todos os 130 estão no snapshot, com SHA-256 no `SAFETY_MANIFEST.json` e na auditoria. Não foram alterados, gerados nem movidos.

**`updater/saida` → mistura de output reproduzível e dado primário baixado**

- Contém builds `LEXDATA_*_BUILD` e `INDICES_BINARIOS_V1_BUILD`, que são reproduzíveis pelo updater.
- Contém também conjuntos baixados, como `qlik_*_completo.json` (~15 MB cada), dependentes de fonte remota.
- **Política:** fora do Git (continua ignorado pelo `.gitignore` da raiz), preservado integralmente no snapshot. Em uma release futura do SD, publicar o pacote com manifest de hash.

**`updater/backup_sd` → backup histórico e único**

- É a cópia do conteúdo do microSD físico feita por `implantar_sd.py` em 2026-09-16 22:33, antes de uma implantação.
- Não é reproduzível: o cartão foi sobrescrito depois.
- **Política:** fora do Git, preservado no snapshot e candidato a cópia fria externa. Não deduplicar nem remover sem a cópia externa.
