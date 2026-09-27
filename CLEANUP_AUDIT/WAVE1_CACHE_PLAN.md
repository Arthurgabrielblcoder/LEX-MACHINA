# ONDA 1 — plano de caches e temporários

Base: inventário e lista ONDA_1 anteriores. HEAD inicial `1dddc43e9f5e1514d79462fdc988645e44466ac2`. Nenhuma auditoria global refeita.

| Grupo | Classificação | Arquivos | Bytes | Regra |
|---|---|---:|---:|---|
| `updater/__pycache__/*.pyc` com fonte `.py` existente, SHA e path conferidos | REMOVER_ONDA1 | 22 | 583302 | bytecode regenerável; nenhum path protegido, versionado ou externo ao diretório validado |
| PRESERVAR_DENTRO_VENV | PRESERVAR | 1374 | 21862464 | .venv, pastas históricas ou dúvida permanecem intactos |
| PRESERVAR_PASTA_HISTORICA_OU_FORA_ESCOPO_ATIVO | PRESERVAR | 207 | 2907303 | .venv, pastas históricas ou dúvida permanecem intactos |

**Candidatos auditados:** 1603 arquivos, 25353069 bytes. **Aprovados:** 22 arquivos, 583302 bytes. **Preservados:** 1581 arquivos.

Critérios: classificação CACHE_TEMPORARIO na auditoria, arquivo regular existente, caminho resolvido dentro de `updater/__pycache__`, fonte `.py` presente, mesmo tamanho e SHA-256 do inventário, ausência nas listas protected545/PROTEGIDO_NAO_TOCAR/Git. Não alterar V2, firmware, IDX, catálogo 69, fontes, manifests, backups, `updater/saida`, `.venv` ou pastas de etapa. Duplicação não é critério.

A lista exata aprovada, tamanho e hash pré-remoção estão em `WAVE1_BEFORE.json`. O diretório `updater/__pycache__` só poderá ser removido se ficar vazio; esta execução prevê remover arquivos individuais.

Árvore pré-remoção medida: 28863 arquivos, 3468560208 bytes. Snapshot externo: presente e acessível. Git status completo pré-remoção: `WAVE1_BEFORE.json`.
