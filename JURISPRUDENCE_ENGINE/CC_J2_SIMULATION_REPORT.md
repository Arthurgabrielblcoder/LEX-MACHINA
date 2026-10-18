# CC-J2 — candidato de simulação (SIMULATION_ONLY, nunca implantável)

```
STATUS = SIMULATION_ONLY · DEPLOYABLE = NO · SD_CHANGED = NO · FIRMWARE_CHANGED = NO
DUPLICATE_QUERY_KEYS = 0 · CC_J1_BASELINE_PRESERVED = YES · CF_REGRESSION = 0 · CC_J1_REGRESSION = 0
```

Base: a camada normalizada física congelada (`CC_J1_MATERIALIZATION_CANDIDATE/candidate/SD`, idêntica ao cartão), relida linha a linha (CF88 311 + ADCT 4 + CC2002 29 relações). Sobre ela entram as relações GREEN + YELLOW do CC-J2, empacotadas pelo `generic_packager.py` sem mudança. Pastas em `cc_j2_simulation/`.

| Item | Valor |
|---|---|
| Relações por norma (relações/alvos) | ADCT 4/4, CC2002 54/42, CF88 311/193 |
| Relações novas do CC-J2 | 25 |
| Visíveis no caminho multinorma do firmware (simulado) | 25/25 |
| Ficha abre / BACK volta à mesma lista | 25/25 / 25/25 |
| Rótulos | IAC 1, REPETITIVO 14, RG 4, Súmula 6 |
| Rótulos OUTRO | 0 |
| Chaves do baseline preservadas (grupo antigo = prefixo do novo) | 221/221 |
| Linhas de registro do baseline ausentes | 0 |
| Chaves CF/ADCT alteradas | 0 |
| Registros reaproveitados do cartão | STF:RG:1236, STF:RG:498, STF:RG:529, STF:RG:809 |
| Fichas novas (rascunho automático) | 18 |
| Fichas compartilhadas entre normas | STF_ADI_7047-7064.TXT, STF_RG_932.TXT |
| Projeção do CC se GREEN + YELLOW fossem ratificados | 54/42 |
| Projeção só com GREEN | 38/32 |

A projeção não é baseline. O baseline físico continua `CC_J1_FROZEN_29_24` (29/24), e a CF continua 315/198 (LEXV1 intocado).
Os rótulos "REPETITIVO STJ n" e "IAC n" já existem no firmware multinorma, mas nunca foram validados fisicamente.
