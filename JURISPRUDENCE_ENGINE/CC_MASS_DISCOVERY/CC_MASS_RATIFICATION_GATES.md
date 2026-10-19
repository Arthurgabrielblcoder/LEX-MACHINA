# CC MASS RATIFICATION — gates futuros

Esta preparação não aprova, materializa nem implanta qualquer relação.

## Precedentes qualificados e autoridades superiores

`ratificação humana com group_id + group_sha256 → validação da decisão → materialization preflight → revisão`

## Acórdãos de Turma

`ratificação humana com group_id + group_sha256 → TURMA_DISPLAY_GATE → simulação host-only → flash somente se necessário → regressão física → deploy de dados`

## Regras de bloqueio

- Hash ausente ou composição alterada: rejeitar a ratificação e pedir reconciliação.
- Exceção não pertencente ao grupo: rejeitar.
- ID repetido ou desconhecido: rejeitar.
- Relação `HOLD`/`REJECT` presente nos grupos: rejeitar.
- Decisão de Turma tratada como vinculante/repetitiva: rejeitar.
- Substituição que volte ao processo antigo: rejeitar.
- `TURMA_DISPLAY_GATE = PENDING`: bloquear materialização de Turma.

## Formato de decisão

O template JSON aceita decisões de grupo `APPROVE_GROUP`, `REJECT_GROUP`, `HOLD_GROUP` e `APPROVE_GROUP_WITH_EXCEPTIONS`, além de ações por IDs `APPROVE_IDS`, `REJECT_IDS` e `HOLD_IDS`. O estado inicial é sempre `PENDING`.
