# Plano de limpeza V1 (proposta — NADA foi executado)

- **Base:** `INVENTARIO_REPOSITORIO.json`, `DUPLICATAS_EXATAS.json`, `DEPENDENCIAS.json` e `PROTEGIDO_NAO_TOCAR.json`.
- **Listas exatas por onda:** `_ESTATISTICAS.json` → `ondas`.
- **Unidades:** MB/GB decimais.
- **Árvore atual:** 28.838 arquivos, 3.421.025.370 bytes (3,42 GB).

> **BLOQUEIO_DE_SEGURANCA_PARA_EXCLUSAO = true.** Nenhuma exclusão ou movimentação real deve ocorrer antes da ONDA 0. A V2 (Engine R1D1, RC1, RC2, holdout e ENRIQUECIDO_V1), o catálogo 69, os 130 IDX, `updater/saida` e `backup_sd` não estão no Git. Até as cópias "principais" das duplicatas (caches e `saida` do `updater/`) estão parcialmente ignoradas pelo Git.

Campos de cada ação: path · categoria · ação proposta · risco · dependências · economia (bytes) · economia humana · reversibilidade · pré-condições.

## ONDA 0 — Segurança e versionamento (obrigatória, antes de tudo)

| # | Path | Ação proposta | Risco | Economia | Reversibilidade | Pré-condições |
|---|---|---|---|---|---|---|
| 0.1 | Árvore inteira | Backup frio externo, verificado por hash contra `INVENTARIO_REPOSITORIO.json` | Nulo | 0 | Total | Disco externo ≥ 3,5 GB |
| 0.2 | `LEX_MACHINA_REFERENCIAS_V2/` (1.135 arquivos, 37 MB) | Versionar (commit dedicado ou repositório próprio) | Baixo | 0 | Total | Decidir se a V2 fica neste repositório |
| 0.3 | `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/` (8 arquivos, 0,7 MB) | Versionar | Baixo | 0 | Total | — |
| 0.4 | `firmware/LEX_MACHINA.ino/` (modificação pendente e `assets/`) | Commit da modificação pendente e de `assets/` | Baixo | 0 | Total | Validar o sketch no hardware |
| 0.5 | `**/*.IDX` (130), `updater/saida/`, `updater/backup_sd/` | Definir política: versionar, release externa com hash ou backup dedicado | Médio | 0 | Total | Decisão humana |
| 0.6 | 545 arquivos do `protected545` (lista em `00_CHECKPOINTS/INTEGRITY_BEFORE.json`) | Marcar como imutáveis e incluir no backup; qualquer arquivamento deve preservar caminho e hash | Baixo | 0 | Total | — |

Economia humana: evita a perda irrecuperável do trabalho de semanas (Engine, revisões humanas do RC2, curadoria de 200 obras).

## ONDA 1 — Lixo inequívoco (CACHE_TEMPORARIO)

| Path | Categoria | Ação | Risco | Dependências | Economia | Reversibilidade | Pré-condições |
|---|---|---|---|---|---|---|---|
| `**/__pycache__/**`, `*.pyc` (1.571 arquivos, 219 pastas, inclusive dentro dos `.venv`) | CACHE_TEMPORARIO | Excluir | Quase nulo | Recriado pelo Python | 25,3 MB | Automática | ONDA 0 concluída |
| `**/.pytest_cache/**` (32 arquivos, 8 pastas) | CACHE_TEMPORARIO | Excluir | Nulo | Recriado pelo pytest | < 0,1 MB | Automática | ONDA 0 |

**Total: 1.603 arquivos, 25.353.069 bytes (25,4 MB).** Economia humana: baixa, porque o volume é pequeno. O ganho principal é de ruído visual.

## ONDA 2 — Duplicatas exatas (SHA-256 idêntico)

São 3.812 grupos. Em cada um, a cópia principal fica mantida pela ordem de preferência: versionada, depois área ativa ou congelada, depois caminho mais curto. Remoção proposta: **18.671 cópias secundárias não protegidas, 2.550.363.537 bytes (2,55 GB)**.

| Path | Arquivos | Economia | Principal fica em | Risco |
|---|---:|---:|---|---|
| `updater_stage2a_corrigida_v2/**` | 6.449 | 890,5 MB | `updater/` (caches e saida) | Baixo quanto ao conteúdo; **médio quanto ao contexto** (o snapshot deixa de ser autocontido) |
| `LEX_MACHINA_UPDATER_BACKUP_V1_17-09-2026/**` | 2.238 | 316,2 MB | `updater/` | Idem |
| `1- LEX-MACHINAETAPA_2D3/**` | 1.758 | 222,9 MB | `updater/` | Idem |
| `LEX-MACHINAETAPA_2D2/**` | 1.622 | 222,7 MB | `updater/` | Idem |
| `LEX-MACHINAETAPA_2D/**` | 1.620 | 222,7 MB | `updater/` | Idem |
| `LEX-MACHINAETAPA_2C/**` | 1.606 | 222,6 MB | `updater/` | Idem |
| `LEX_MACHINA_UPDATER_RELATIONS_V2_ETAPA2A/**` | 1.606 | 222,6 MB | `updater/` | Idem |
| `LEX_MACHINA_UPDATER_RELATIONS_V2/**` | 1.599 | 222,5 MB | `updater/` | Idem |
| Demais pastas de etapa (2D4…2E6) | 173 | ≈ 7 MB | Variável | Baixo |

Observações:

- **2,54 GB dessas cópias têm a principal em área protegida** (`updater/cache_*` e `updater/saida`). Só 10,9 MB têm a principal em outra pasta legada.
- **Onde mais de uma cópia está em área protegida** (385 grupos de risco ALTO, por exemplo IDX e arquivos do `protected545`), **nenhuma cópia protegida deve ser removida**. Elas não entram nesta onda.
- **Pré-condições:** ONDA 0, e garantir que as cópias principais em `updater/cache_*` e `updater/saida` estejam versionadas ou em backup, porque parte delas é ignorada pelo Git.
- **Alternativa recomendada:** em vez de apagar arquivo a arquivo dentro dos snapshots, arquivar cada pasta de etapa inteira de forma **comprimida** (ONDA 4). O ganho em disco é semelhante e cada snapshot continua íntegro.
- **Reversibilidade:** total, se houver backup.
- **Economia humana:** alta. É daqui que vem o grosso do volume.

## ONDA 3 — Artefatos reproduzíveis (GERADO_REPRODUZIVEL, não protegidos)

| Path | Arquivos | Economia | Gerado por | Entradas existem? | Risco | Pré-condições |
|---|---:|---:|---|---|---|---|
| `LEX_MACHINA_UPDATER_BACKUP_V1_17-09-2026/.venv/` | 1.160 | 128,4 MB | `pip install -r requirements.txt` (arquivo presente no diretório pai) | Sim | Baixo (backup legado) | ONDA 0 |
| `updater/.venv/` | 1.160 | 128,4 MB | `pip install -r updater/requirements.txt` | Sim | **Médio**: é o ambiente ativo do updater, com `playwright` e driver `node.exe`; reinstalar exige rede e navegadores do Playwright | Só com concordância de quem opera o updater |

**Total da onda: 2.320 arquivos, 256.869.230 bytes (256,9 MB).** A remoção de `updater/.venv` é opcional.

Relatórios derivados da expansão (`METRICAS_FINAIS`, `COBERTURA_EDITORIAL`, `REDUNDANCIA_*`, `ESTADO_FINAL`, `REJEICOES`…) são reproduzíveis por `gerar_relatorios.py`, mas **ficam protegidos**: são pequenos (< 1 MB) e servem como prova.

## ONDA 4 — Legado para arquivamento (CANDIDATO_ARQUIVAMENTO e LEGADO_NAO_REFERENCIADO)

Destino sugerido, **não criado**: `_ARCHIVE_PRE_CLEANUP_2026-09/`, preferencialmente fora da árvore ativa (disco ou repositório de arquivo) e comprimido.

- **Arquivos únicos restantes nas pastas legadas depois da ONDA 2:** 778 arquivos, 143,3 MB.
  - Principais: zips de etapa de ~29 MB (ETAPA2A, ETAPA2D, 2D3); `saida/` e relatórios de etapa; scripts `etapa2d*_work`; `LEX_MACHINA_JURIS_CF_J4_6` (227 arquivos, não referenciado).
- **Sem a ONDA 2 (arquivando as pastas inteiras):** pastas `LEX-MACHINAETAPA_*`, `LEX_MACHINA_UPDATER_*`, `updater_stage2a_corrigida_v2` e `LEX_MACHINA_JURIS_CF_*`, somando ≈ 2,9 GB antes de comprimir.

Campos:

- **Risco:** baixo a médio. Algumas pastas são citadas por nome em relatórios da V2 (`LEGADO_REFERENCIADO`) ou fazem parte do `protected545`.
- **Dependências:** `DEPENDENCIAS.json` → `referencias_a_pastas_de_topo`.
- **Pré-condições:**
  - ONDA 0;
  - manter os 545 arquivos do `protected545` com caminho e hash preservados (ou registrar o novo local num manifest de arquivamento);
  - revisão humana das pastas `LEGADO_REFERENCIADO` (Referências V1…V1.4, JURIS_CF_J3/J4 citadas pelo firmware, CF_SEGMENTADA_V2).
- **Reversibilidade:** total (mover de volta).
- **Economia humana:** alta. A raiz passa de ~83 para ~12 entradas.

`LEGADO_REFERENCIADO` (478 arquivos, 65 MB: Referências V1…V1.4, JURIS_CF J3/J4, firmware antigos) **não entra automaticamente**: arquivar só depois de revisão manual.

## ONDA 5 — Reorganização estrutural opcional

Ver `ESTRUTURA_RECOMENDADA.md`:

- `firmware/releases/`;
- consolidação `referencias/`, **sem mover os congelados da V2** por causa dos caminhos absolutos em manifests e scripts.

Risco médio. Economia de disco zero; ganho de navegação. Pré-condição: ondas 0–4 concluídas e testes do updater e da compilação do catálogo passando.

## Capturas brutas (RAW_SOURCE_CAPTURE) — manter nesta fase

São 1.721 arquivos, 242,6 MB: caches de fontes oficiais do updater (`cache_lexdata_*`, `cache_stj`, `cache_auditoria_vigencia_72`) e capturas da curadoria (`BUSCA_*`, `STEAM_*`, `CONSULTA_CP11/12.txt`).

| Arquivo | Origem | Proveniência | Cards que dependem | Texto incorporado? | Outra forma de reprodução | Recomendação |
|---|---|---|---|---|---|---|
| `…/06_RELATORIOS/CONSULTA_CP11.txt` (54 KB) | Saída de `consultar_fontes_enriquecimento.py` no checkpoint 11 (obras 180–192) | URL, data e `snapshot_sha256` de cada página em `03_FONTES/ENRIQUECIMENTO_V1/*.json` | EXP2-LIV-021-E02, EXP2-LIV-022-E02, EXP2-LIV-023-E02 | Não literalmente: os cards trazem paráfrase | Refazer a consulta pela URL e comparar o hash | Manter como prova até a revisão humana; depois substituir por registro de proveniência enxuto (URL, data, hash, localizador), que já existe. O arquivo contém texto de páginas de terceiros |
| `…/06_RELATORIOS/CONSULTA_CP12.txt` (38 KB, parcialmente binário) | Idem, checkpoint 12 (obras 193–200) | Idem | EXP2-LIV-033-E02, EXP2-LIV-033-E03, EXP2-LIV-036-E02, EXP2-LIV-037-E02, EXP2-LIV-040-E02 | Idem | Idem | Idem |
| `03_FONTES/BUSCA_55..120.json` (66 arquivos) | Listas de resultados de busca (Codex) | `query` e data no arquivo | Referenciados em `origem_busca` dos dossiês 101–120 | Não (só URLs) | Não reproduzível (a busca muda com o tempo) | Manter (pequeno; prova de processo) |
| `03_FONTES/STEAM_001..050.json` | API oficial `appdetails` da Steam (`collect_steam.py`) | `api_url` e `accessed_at` | Base dos cards de jogos | Paráfrase | Reexecutar `collect_steam.py`, mas o conteúdo da loja muda | Manter: é a evidência de base dos jogos |
| `updater/cache_*` e cópias em pastas de etapa | Downloads de fontes oficiais (legislação, STJ) | Nomes por hash e scripts `baixar_*` / `importar_*` | Insumo do build de LEXDATA/IDX | — | Novo download (fontes podem mudar ou sair do ar) | Manter as cópias do `updater/`; as cópias em etapas são DUPLICATA_EXATA (ONDA 2) |

## Cenários (cálculo sem apagar nada)

| Cenário | Ondas | Arquivos envolvidos | Espaço recuperável |
|---|---|---:|---:|
| **A** | 1 | 1.603 | **25,4 MB** |
| **B** | 1 + 2 | 20.274 | **2,576 GB** (2.575.716.606 bytes) |
| **C** | 1 + 2 + 3 | 22.594 | **2,833 GB** (2.832.585.836 bytes); sem `updater/.venv`: 2,704 GB |
| **D** | C + ONDA 4 arquivada | +778 saem da árvore ativa | 143,3 MB vão para o archive |

No cenário D, a árvore operacional cai de **3,42 GB e 28.838 arquivos** para **≈ 445 MB e ≈ 5.466 arquivos**, uma redução de 87% em bytes e 81% em arquivos.

Se as pastas legadas forem arquivadas inteiras, sem a ONDA 2, o archive ficaria com ≈ 2,9 GB antes de comprimir (a compressão reduz muito, porque o conteúdo é quase todo duplicado), e a árvore ativa ficaria praticamente no mesmo ≈ 0,45–0,70 GB.

## Candidatos a exclusão (CANDIDATO_EXCLUSAO)

**Nenhum arquivo recebeu CANDIDATO_EXCLUSAO.** Os únicos itens que atendem a todos os critérios rigorosos são caches (ONDA 1), já classificados como CACHE_TEMPORARIO. As demais remoções (duplicatas e ambientes virtuais) dependem de pré-condições da ONDA 0.
