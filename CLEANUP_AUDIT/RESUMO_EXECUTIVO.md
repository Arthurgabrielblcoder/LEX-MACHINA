# Resumo executivo — auditoria de higiene do repositório

Auditoria de 2026-09-26, somente leitura. **Nenhum arquivo foi apagado, movido ou renomeado, e o Git não foi alterado.**

**O repositório está muito sujo?** Em volume, sim. Em conteúdo, não.

- A árvore tem 3,42 GB e 28.838 arquivos.
- **75% do volume (2,55 GB) são cópias byte a byte idênticas** de arquivos que já existem em `updater/`: caches de fontes oficiais e saídas de build.
- O conteúdo único e ativo é pequeno: V2 com 37 MB, `updater/` com ~300 MB excluindo o `.venv`, firmware com 5 MB.

**Onde está a maior desorganização?** Na **raiz**, com ~70 pastas-snapshot de etapas e versões:

- `LEX-MACHINAETAPA_2B…2E6` (30 pastas);
- `updater_stage2a_corrigida_v2` (910 MB, a maior pasta);
- `LEX_MACHINA_UPDATER_BACKUP_V1_17-09-2026` (435 MB);
- `LEX_MACHINA_UPDATER_RELATIONS_V2*`;
- 29 pastas `LEX_MACHINA_REFERENCIAS_*_V1…ALPHA3`;
- 6 pastas `LEX_MACHINA_JURIS_CF_*`.

**O problema principal é volume, duplicação ou organização?**

- Duplicação é a causa do volume.
- Organização é a causa da confusão.

Os pipelines ativos (`firmware/`, `updater/` e V2) estão razoavelmente organizados por dentro.

**Quanto pode ser removido com risco quase zero?**

- Só caches (`__pycache__` e `.pytest_cache`): **25 MB** (cenário A).
- As duplicatas somam **2,55 GB** de risco baixo quanto ao conteúdo, mas só depois de backup e versionamento, porque até as cópias principais em `updater/` estão parcialmente ignoradas pelo Git.
- Com os ambientes virtuais recriáveis, o total chega a 2,83 GB.

**Quanto deveria apenas ser arquivado?**

- **143 MB de conteúdo único legado** (778 arquivos) vão para archive.
- Alternativa mais segura: arquivar as ~70 pastas legadas inteiras e comprimidas. São ≈ 2,9 GB brutos, que comprimem bem por serem quase todo duplicados.
- Em qualquer caso, a árvore operacional cai para **≈ 0,45 GB**.
- Nada foi classificado como CANDIDATO_EXCLUSAO fora os caches.

**Existem riscos sérios de versionamento?** **Sim, graves.**

- `LEX_MACHINA_REFERENCIAS_V2/` está **100% untracked** (0 de 1.135 arquivos). Ali estão Engine R1D1, ontologia, contratos, RC1, RC2 com decisões humanas, holdout, benchmarks, a expansão 200 e **ENRIQUECIDO_V1**.
- Também estão fora do Git:
  - o catálogo original de 69 obras;
  - **todos os 130 IDX**;
  - `updater/saida` e `updater/backup_sd`;
  - os `assets/` do firmware ativo;
  - a modificação pendente do sketch ativo.
- Um `git clean -fdx` ou uma limpeza "por pasta" destruiria isso sem volta.

**BLOQUEIO_DE_SEGURANCA_PARA_EXCLUSAO = true**

**O que precisa acontecer antes de apagar qualquer coisa (ONDA 0):**

1. Backup frio externo da árvore inteira, verificado por hash com `INVENTARIO_REPOSITORIO.json`.
2. Versionar `LEX_MACHINA_REFERENCIAS_V2/`, o catálogo 69 e o firmware ativo (incluindo a modificação pendente e os `assets/`).
3. Definir a política para IDX, `updater/saida` e `backup_sd`: versionar, fazer release externa com hash ou manter backup dedicado.
4. Preservar caminho e hash dos 545 arquivos do escopo `protected545` da prova de integridade da V2.
5. Só então executar, nesta ordem: caches (ONDA 1), arquivamento comprimido das pastas de etapa (ONDA 4, preferível à deduplicação arquivo a arquivo), ambientes virtuais (ONDA 3, opcional) e reorganização (ONDA 5, opcional).

**Integridade durante a auditoria:** idêntica antes e depois.

- Congelados da V2: 281/281.
- Engine R1D1, RC1, RC2, holdout, ontologia e contratos: intactos.
- Catálogo 69 e ENRIQUECIDO_V1: intactos (manifest válido).
- Firmware: hash `62f256e4…` inalterado.
- 130 IDX: intactos. SD não tocado.
