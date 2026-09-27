# READY_FOR_WAVE1 — estado parcial da ONDA 0

A ONDA 0 foi interrompida pelo limite de uso da sessão antes do commit e da tag.

| Item | Estado |
|---|---|
| Snapshot local válido | **SIM** (`C:\GitHub_LEX_MACHINA_SAFETY_PRE_CLEANUP_2026-09-26\`, SNAPSHOT_LOCAL_DE_SEGURANCA, não é backup frio externo) |
| Git bundle válido | **SIM** (clone `--mirror`, `fsck` sem erros, 8 refs idênticas, 16 commits, mesma árvore do HEAD) |
| Commit de segurança | **NÃO** (pendente; plano em `GIT_VERSIONING_PLAN.md`) |
| Tag de segurança | **NÃO** (pendente: `pre-cleanup-2026-09-26`) |
| Segredos detectados | 1: `BUSCA_118.json`, BLOQUEADO_POR_SEGREDO, fora do Git |
| IDX policy | IDX_SNAPSHOT_APENAS |
| updater/saida policy | Mistura de output e dados baixados; fora do Git, no snapshot |
| backup_sd policy | Backup histórico e único; fora do Git, no snapshot |
| protected545 preservados | SIM (hashes conferidos no snapshot) |
| Integridade final | Pendente de revalidação direcionada |
| SHA256SUMS.txt | Pendente |
| Auditoria inicial executada por | CLAUDE CODE |
| ONDA 0 executada por | CLAUDE CODE (parcial) |

**Falta:**

1. `SHA256SUMS.txt` no snapshot;
2. `git add` com paths explícitos conforme `GIT_VERSIONING_PLAN.md`, excluindo `BUSCA_118.json` e `CONSULTA_CP11/12.txt`;
3. commit local `chore: preserve critical state before repository cleanup`;
4. tag anotada `pre-cleanup-2026-09-26`;
5. revalidação direcionada da integridade;
6. atualização deste arquivo.

BLOQUEADO_PARA_ONDA_1 — commit/tag de segurança e integridade final ainda não executados (sessão interrompida por limite de uso)
