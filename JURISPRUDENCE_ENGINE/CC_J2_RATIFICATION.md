# CC-J2 — ratificação humana (2026-10-18)

```
CC_J2_RATIFICATION = PASS · TOTAL 30 · APROVADAS 19 (9 GREEN + 10 YELLOW) · NÃO APROVADAS 11 (RED) · PENDENTES 0
RELAÇÕES APROVADAS 20 · TARGETS NOVOS 15 (3 já existiam no CC-J1) · PROJEÇÃO APÓS MATERIALIZAÇÃO 49/39 (não é baseline)
CC FÍSICO 29/24 · CF FÍSICA 315/198 · MATERIALIZED = NO · SD_CHANGED = NO · FIRMWARE_CHANGED = NO
```

Registro: `CC_J2_RATIFICATION_RECORD.json` (gerado por `build_cc_j2_ratification_record.py`). Ele fixa os hashes de:
- decisões originais, revisão e métricas;
- dossiê preliminar e dossiê final;
- backlog, simulação e fontes oficiais;
- registro do CC-J1.

As propostas originais não foram editadas. Cada mudança humana de target ou status fica no registro.

## Mudanças humanas em relação às propostas

| Item | Mudança |
|---|---|
| CCJ2-08 (Tema 639) | Só no art. 206, § 5º, I; o vínculo ao 2.028 não foi criado |
| CCJ2-29 (Tema 610) | Só no art. 206, § 3º, IV; o vínculo ao 2.028 não foi criado |
| CCJ2-22 (Tema 1130) | PROVISIONAL → definitivo (`STJ_SOURCE_STATUS_STALE = YES`; o Tema 1432/STF negou repercussão geral, trânsito em 18/09/2026); não entra no registro de provisórios |

## Notas editoriais obrigatórias nas fichas

- Súmula 619: uma ficha, dois vínculos (1.208 = detenção; 1.255 = acessões).
- IAC 1: `HISTORICAL_BUT_RELEVANT`, CPC/1973.
- Súmula 637: exceção ou limite interpretativo do art. 1.210, § 2º.
- Súmula 655: `SUBJECT_TO_TEMA_1236_STF`.
- Tema 381: `EXCLUSION_CONTEXT`; a ficha começa por "inaplicabilidade à compensação tributária".
- Súmula 642: `SOURCE_STRUCTURAL_ERROR_CORRECTED = ART943_INC1 -> ART943`; a anomalia original fica na proveniência.

## Fichas e tipos

- **Fichas reutilizadas do cartão:** `STF_RG_498.TXT` e `STF_RG_809.TXT`.
- **Fichas novas necessárias na materialização:** 17.
- **Correção de metadado em `juris_types`:** `PHYSICAL_VALIDATION_RECORDS` + `physical_status()` levam a `SUMULA_STJ_PHYSICALLY_VALIDATED = YES` (CC-J1 36/36). É só metadado. `device_status()` mantém a tabela com que o piloto, o CC-J1 e o CC-J2 foram gerados, para que os arquivos fixados continuem idênticos. Os lotes J2 a partir do Batch11 já usam `physical_status`.
- **Pendência para a próxima refatoração do motor:** o `batch_engine` ainda chama `device_status`. Passá-lo para `physical_status` agora mudaria as métricas fixadas do CC-J2.
- **IAC:** `IAC_SUPPORTED_ARCHITECTURALLY = YES`, `IAC_PHYSICALLY_VALIDATED = NO`. O rótulo "REPETITIVO STJ" também nunca foi exibido no aparelho. Os dois entram no checklist físico do CC-J2.

## Próximo passo

`CC-J2 MATERIALIZATION PREFLIGHT`. Nenhum candidato físico foi criado nesta missão.
