# Auditoria do estado Git

Levantamento feito em 2026-09-26, somente leitura. Nenhum comando alterou o Git.

## Identificação

| Item | Valor |
|---|---|
| Raiz Git | `C:/GitHub/LEX-MACHINA` |
| Branch | `main` |
| HEAD | `d4e816f` "Preserva v7.12.0 validada no hardware" (2026-09-21) |
| Commits | 16 |
| `.git/` | ≈ 95 MB |
| Staged | **0** |
| Modificados (tracked) | **1**: `firmware/LEX_MACHINA.ino/LEX_MACHINA.ino.ino` (+951/−189 em relação ao HEAD, modificado em 2026-09-17) |
| Tracked | **1.279** arquivos |
| Untracked (fora do `.gitignore`) | **5.038** arquivos |
| Ignored | **22.521** arquivos |
| Total na árvore (sem `.git`) | 28.838 arquivos, 3,42 GB |

**Só 4,4% dos arquivos estão versionados.** O que está versionado:

- `updater/`: 1.254 arquivos, incluindo caches de fontes;
- `firmware/`: 18 arquivos (sketch ativo, v7.10.1 FAST e v7.12.0);
- `docs/`, `sdcard/README.md`, `README.md`, `HISTORICO_RELEASES.md` e `.gitignore`.

**Por que tanto é ignorado.** O `.gitignore` da raiz é pequeno: build Arduino, `updater/saida/`, `.venv` e `.pyc`. Os 22.521 ignorados vêm de **`.gitignore` aninhados dentro de cópias de etapas** (por exemplo `LEX_MACHINA_UPDATER_BACKUP_V1_17-09-2026/.gitignore`, `LEX-MACHINAETAPA_2C/updater_stage2c/.gitignore`), que ignoram `.venv/`, `.pytest_cache/` e `saida/` dentro dessas cópias, e de `updater/saida/`.

## LEX_MACHINA_REFERENCIAS_V2 — confirmação

**CONFIRMADO: a pasta está 100% fora do controle do Git.**

- `git ls-files LEX_MACHINA_REFERENCIAS_V2` retorna **0 arquivos**.
- Os 1.135 arquivos (37,3 MB) aparecem como untracked (`?? LEX_MACHINA_REFERENCIAS_V2/`); nenhum está ignorado.
- Nenhum commit contém a pasta.

## Partes importantes versionadas

- `updater/`: pipeline e caches de fontes (`cache_lexdata_oficial`, `cache_lexdata_v4`, `cache_stj`…).
- `firmware/LEX_MACHINA.ino/` (sketch e `contexto_juridico.h`) e `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/`.
- Documentação da raiz e `docs/`.

## Partes importantes NÃO versionadas

| Área | Arquivos | Tamanho | Conteúdo crítico |
|---|---:|---:|---|
| `LEX_MACHINA_REFERENCIAS_V2/` | 1.135 | 37,3 MB | Engine R1D1, ontologia, contratos, RC1, RC2 com decisões humanas, holdout, benchmarks, checkpoints, expansão 200, **ENRIQUECIDO_V1** |
| `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/` | todos | — | **Catálogo original de 69 obras** (`CATALOGO_69_CANONICO.json`) |
| IDX (`**/*.IDX`) | 130 | — | **Nenhum IDX versionado**: 108 ignorados (em `saida/`) e 22 untracked |
| `updater/saida/` | 935 | 62 MB | Saída de build implantada no SD (ignorada) |
| `updater/backup_sd/` | 162 | 0,3 MB | Backup do SD (untracked) |
| `updater/cache_lexdata_v4/` (parte) | 72 | 22,7 MB | Cache de fontes (parte ignorada) |
| `firmware/LEX_MACHINA.ino/assets/`, `firmware/LEX_MACHINA_v7.11.*`, `firmware/LEX_MACHINA_BACKUP_POS_CODEX_16-09/`, zip v7.10.1 | — | ~5 MB | Assets do sketch ativo, versões intermediárias e backup |
| 545 arquivos da prova `protected545` (INTEGRITY_BEFORE da V2) | 545 | — | Referências V1, CF_SEGMENTADA_V2, firmware, IDX e sdcard hasheados como escopo da prova R1D1 |
| Pastas de etapa e versões antigas (`LEX-MACHINAETAPA_*`, `LEX_MACHINA_REFERENCIAS_*_V1`, `LEX_MACHINA_JURIS_CF_*`, backups do updater) | ≈ 25.000 | ≈ 2,9 GB | Legado, com grande volume duplicado |

No total, 3.694 arquivos (189 MB) classificados como protegidos estão fora do Git. Detalhes em `PROTEGIDO_NAO_TOCAR.json`.

## Riscos

- **Risco de perda: ALTO.** Os artefatos centrais do projeto (Engine R1D1, RC1, RC2, holdout, ENRIQUECIDO_V1 e catálogo 69) existem só nesta cópia de disco. Não há histórico nem cópia remota comprovada. Uma falha de disco ou uma limpeza equivocada seria irreversível.
- **Risco de futura exclusão: ALTO.** Com tudo untracked, um `git clean -fdx` apagaria a V2 inteira, o catálogo 69, todos os IDX, `updater/saida` e `backup_sd`. Uma remoção "por pasta" de legado também pode atingir os 545 arquivos que a prova de integridade da V2 referencia.
- **Modificação pendente no firmware.** O sketch ativo difere do HEAD desde 2026-09-17. Um checkout destrutivo perderia essas alterações.

## Recomendação de segurança (não executada)

1. Fazer **backup completo** externo (cópia fria) da árvore inteira, com verificação por hash usando `INVENTARIO_REPOSITORIO.json`.
2. **Versionar** (commit ou repositório separado) pelo menos:
   - `LEX_MACHINA_REFERENCIAS_V2/`;
   - `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_CANONICO.json`;
   - `firmware/LEX_MACHINA.ino/` (incluindo `assets/` e a modificação pendente);
   - `updater/backup_sd/`.
3. Decidir a política dos IDX e de `updater/saida/`: versionar, guardar como release externa com hash, ou manter backup dedicado.
4. Nunca usar `git clean` enquanto houver conteúdo crítico untracked.

**BLOQUEIO_DE_SEGURANCA_PARA_EXCLUSAO = true**
