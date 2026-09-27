# ONDA 1 — resultado da remoção verificada de caches

**Resultado:** concluída dentro do escopo conservador autorizado. Foram removidos exatamente os 22 arquivos `.pyc` de `updater/__pycache__` aprovados em `WAVE1_BEFORE.json`, totalizando **583.302 bytes** (0,583302 MB decimais; 0,55628 MiB). Nenhum diretório foi removido.

| Medida | Valor |
|---|---:|
| Candidatos `CACHE_TEMPORARIO` da auditoria existente | 1.603 arquivos; 25.353.069 bytes |
| Removidos na Onda 1 | 22 arquivos; 583.302 bytes |
| Preservados dentro de `.venv` | 1.374 arquivos; 21.862.464 bytes |
| Preservados em pastas históricas ou fora do escopo ativo | 207 arquivos; 2.907.303 bytes |
| Total preservado | 1.581 arquivos; 24.769.767 bytes |

Cada arquivo removido foi conferido imediatamente antes da exclusão quanto a caminho, tipo, tamanho, SHA-256, fonte `.py` regeneradora, ausência do índice Git e permanência dentro de `updater/__pycache__`. A lista individual e os hashes anteriores constam de `WAVE1_BEFORE.json`. A classificação e os critérios constam de `WAVE1_CACHE_PLAN.md`.

## Medidas e integridade

- Árvore antes de criar os documentos desta onda e antes da exclusão, sem `.git`: **28.863 arquivos; 3.468.560.208 bytes**.
- Árvore após a exclusão e com os dois documentos preliminares desta onda, antes de escrever este resultado, sem `.git`: **28.843 arquivos; 3.467.989.741 bytes**. A variação líquida é de 20 arquivos e 570.467 bytes porque os dois documentos preliminares acrescentaram 12.835 bytes; a remoção efetiva foi de 22 arquivos e 583.302 bytes.
- Verificação constitucional `_concluir_onda0.verify()`: **PASSA** após a exclusão. Inclui V2 congelado, Engine, RC1/RC2, holdout, ontologia/contratos, firmware, 130 IDX, protected545, catálogo 69, enriquecido V1 e snapshot externo.
- Comparação SHA-256 dos **1.147 arquivos funcionais** com `_ONDA0_PRE_STAGING.json`: **zero divergências ou ausências**.
- `git diff --name-status` após a exclusão: vazio; nenhum arquivo versionado alterado pela limpeza.

O snapshot externo pré-limpeza permaneceu no local e passou na verificação de integridade existente. O segredo `BUSCA_118.json` foi preservado e não foi incluído neste relatório nem no commit. Não houve deduplicação, reorganização, remoção de `.venv` ou de versões históricas, alteração da Engine/IDX/SD, nem execução da Onda 2.

**Anomalias:** nenhuma na seleção, exclusão ou nas verificações de integridade. O total removido é menor que a estimativa inicial da auditoria porque 1.581 candidatos foram conscientemente preservados pelas restrições desta onda.

Commit local planejado: `chore: remove verified temporary caches`. Tag anotada local planejada: `post-cleanup-wave1-2026-09-26`.
