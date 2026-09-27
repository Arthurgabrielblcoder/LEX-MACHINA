# Mapa de pastas atual — LEX-MACHINA

Estado em 2026-09-26. Tamanhos sem `.git/`. Detalhes em `USO_DE_DISCO.md` e `INVENTARIO_REPOSITORIO.json`.

Legenda:

- 🔴 crítico ou congelado (não tocar)
- 🟢 ativo
- 🟡 legado referenciado ou escopo de prova
- ⚪ legado ou snapshot de etapa
- 🔁 predominantemente duplicado

```text
C:/GitHub/LEX-MACHINA/                                  3,42 GB · 28.838 arquivos
├── README.md · HISTORICO_RELEASES.md · .gitignore      🟢 tracked
├── docs/ (ARCHITECTURE, HARDWARE, ROADMAP)             🟢 tracked
├── sdcard/README.md                                    🟢 tracked
├── firmware/                                           5,0 MB
│   ├── LEX_MACHINA.ino/                                🔴 sketch ATIVO (tracked, modificado) · assets/ untracked
│   ├── LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/         🟢 tracked (versão validada no hardware)
│   ├── LEX MAQUINA INO 2/ (v7.10.1 FAST + zip)         🟡 tracked parcialmente; zip untracked
│   ├── LEX_MACHINA_v7.11.0 / v7.11.1_JURIS_CF_PILOTO/  ⚪ untracked
│   └── LEX_MACHINA_BACKUP_POS_CODEX_16-09/             ⚪ backup untracked
├── updater/                                            440 MB · pipeline ATIVO de dados do SD
│   ├── *.py, testes, catálogos                         🟢 tracked
│   ├── cache_lexdata_oficial|v2|v3|v4, cache_stj…      🔴 capturas de fontes oficiais (majoritariamente tracked)
│   ├── saida/  (IDX, BIN, TXT implantados)             🔴 ignored (62 MB)
│   ├── backup_sd/ · backup_catalogos/ · backup_saida/  🔴 backups (untracked)
│   └── .venv/                                          ⚙ 138 MB, recriável (requirements.txt)
├── LEX_MACHINA_REFERENCIAS_V2/                         🔴 37 MB · 100% UNTRACKED
│   ├── 00_CHECKPOINTS/  (integridade, determinismo, holdout, freezes)
│   ├── 01_SCHEMA/ 02_DISPOSITIVOS/ 03_OBRAS/ 04_CONCEITOS/  (ontologia, contratos, evidências)
│   ├── 05_COMPILADOR/  (Engine R1D1)
│   ├── 06_BENCHMARKS/ · 07_EXECUCAO_COMPLETA/ · 09_RELATORIOS/ · tests/
│   ├── 08_RELEASE_CANDIDATE/ (RC1, RC2_HUMAN_REVIEWED)
│   └── 09_CATALOGO_EXPANSAO_200/
│       ├── 00_ENTRADA … 05_REJEITADAS  (entradas, triagem, fontes, dossiês + overlays ENRIQUECIMENTO_V1)
│       ├── 06_RELATORIOS/  (scripts, relatórios, checkpoints, CONSULTA_CP11/12.txt = captura bruta)
│       ├── 07_CATALOGO_CANDIDATO/ (catálogo base + ENRIQUECIDO_V1 congelado)
│       └── 08_MANIFEST/
├── LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/  🔴 catálogo original de 69 (untracked, 8 arquivos)
├── LEX_MACHINA_REFERENCIAS_*_V1/_V2/_ALPHA*/_FINAL (29 pastas)   🟡 histórico da engine V1 → V1.4
│       (ENGINE_V1…V1_4_ALPHA3, VALIDACAO_*, BENCHMARK_*, AUDITORIA_*, CATALOGO_*, CF_J5*, …)
│       parte hasheada pela prova protected545 da V2
├── CF_SEGMENTADA_V2/                                   🟡 1,7 MB · escopo da prova protected545
├── LEX_MACHINA_JURIS_CF_J1 … J4_6 (6 pastas)           🟡/⚪ série JURIS CF (J3/J4 citadas pelo firmware)
├── LEX-MACHINAETAPA_2B … 2E5, 2E6_SD_TESTE (30 pastas) ⚪🔁 etapas do updater/relations
│       2C, 2D, 2D2, "1- …2D3": ~215–243 MB cada, ≈99% duplicado de updater/
│       2D4 … 2E5: pequenas (≤15 MB), scripts de etapa + saídas
├── LEX_MACHINA_UPDATER_BACKUP_V1_17-09-2026/           ⚪🔁 435 MB (301 MB duplicado + .venv de 138 MB)
├── LEX_MACHINA_UPDATER_RELATIONS_V2/                   ⚪🔁 213 MB (≈100% duplicado)
├── LEX_MACHINA_UPDATER_RELATIONS_V2_ETAPA2A/           ⚪🔁 241 MB (212 MB duplicado + zip de 29 MB)
└── updater_stage2a_corrigida_v2/                       ⚪🔁 910 MB · MAIOR PASTA (849 MB duplicado)
        stage2a_fix3/ · stage2b/ (+ stage2c aninhado) · stage2d/  (cada uma com cópia completa dos caches do updater)
        + LEX_MACHINA_UPDATER_RELATIONS_V2_ETAPA2D.zip (29 MB)
```

## Regiões

- **Muitas versões antigas:**
  - famílias `LEX-MACHINAETAPA_2D*` (21 pastas) e `2E*` (8);
  - `LEX_MACHINA_REFERENCIAS_ENGINE_V1*` (9);
  - `VALIDACAO_V14_ALPHA*` (3);
  - `LEX_MACHINA_JURIS_CF_J*` (6);
  - firmware v7.10.1, v7.11.0, v7.11.1 e v7.12.0 com backup.
- **Outputs intermediários:**
  - `*/saida/` em cópias de etapa (49 pastas `saida`, ≈ 794 MB);
  - `saida.zip` repetidos (5 cópias idênticas);
  - 4 zips de etapa de ~29 MB;
  - `CONSULTA_CP11/12.txt`.
- **Caches e ambientes:**
  - 219 pastas `__pycache__` e 8 `.pytest_cache`;
  - 2 `.venv` (138 MB cada: `updater/` e backup do updater).
- **Áreas críticas:** `LEX_MACHINA_REFERENCIAS_V2/`, catálogo 69, `firmware/LEX_MACHINA.ino/`, `updater/`, todos os `*.IDX`.
- **Legado:** tudo o que está na raiz com prefixo `LEX-MACHINAETAPA_`, `LEX_MACHINA_UPDATER_*`, `updater_stage2a_corrigida_v2`, `LEX_MACHINA_REFERENCIAS_*` (exceto V2 e ADAPTADOR), `LEX_MACHINA_JURIS_CF_*` e `CF_SEGMENTADA_V2`.
