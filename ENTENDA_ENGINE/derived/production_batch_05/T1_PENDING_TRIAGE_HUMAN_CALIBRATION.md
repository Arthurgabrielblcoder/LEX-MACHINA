# T1 — CALIBRAÇÃO HUMANA DA TRIAGEM (Batch05, 31 pendentes)

`T1_VALIDATOR_V2 (A6, 2026-10-04)` · 2026-10-04 · nada alterado: textos, status e versões intactos; autoaprovação OFF (LOW e MEDIUM). Objetivo: decidir se o roteamento A/B/C/D está correto. Não é aprovação.

**Como responder:** por item, `CONFIRMAR` a fila ou `RECLASSIFICAR → <fila>` (com motivo curto). Na fila D, só confirmar se o roteamento está certo; a correção virá depois.

**Classificação do validador na fila C** (regras determinísticas, a calibrar com a sua resposta):
- PROVÁVEL FALSO POSITIVO: o mesmo termo já está justificado no editorial_checks, ou o quantificador está num exemplo que reproduz a Lei Seca;
- PROVÁVEL PROBLEMA: mesmo padrão já corrigido nas rodadas (finalidade, consequência automática, condição inexistente, permissão sobre garantia);
- INDETERMINADO: o restante.

## A — CLEAN_LOW (0)

## B — CLEAN_MEDIUM (0)

## C — QUICK_REVIEW (0)

Reclassificar para A/B se o alerta for falso positivo; para D se houver problema jurídico.

## D — FULL_HUMAN_REVIEW (0): pacote completo

## Fora deste pacote

- Acervo anterior aprovado: 45 alertas registrados em `T1_LEGACY_AUDIT_BACKLOG.md` (não bloqueiam o Batch05; nada alterado).
