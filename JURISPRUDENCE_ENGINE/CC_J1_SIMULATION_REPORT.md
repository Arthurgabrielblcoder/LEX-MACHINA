# CC-J1 — candidato de simulação e teste ponta a ponta

```
CC_J1_SIMULATION_CANDIDATE = SIMULATION_ONLY (não implantável; relações do CC NÃO ratificadas)
CC_E2E_SIMULATION = PASS · CF_AFTER_CC_REGRESSION = PASS · DUPLICATE_QUERY_KEYS = 0
SD_CHANGED = NO · FIRMWARE_FLASHED = NO · CF_PHYSICAL_BASELINE_CHANGED = NO
```

Gerador: `build_cc_j1_simulation.py`. Pacote: `cc_j1_simulation/`. Teste: `tests/test_cc_j1_simulation.py`.

## Composição

| Norma | Relações | Targets com J | Origem |
|---|---:|---:|---|
| CF88 | 311 | 194 | J2I_FROZEN_315_198 (relações visíveis do `REF_PAYLOAD`) |
| ADCT | 4 | 4 | J2I_FROZEN_315_198 |
| CC2002 | 23 | 20 | CC-J1: PROMOTE/REALLOCATE com fonte oficial e sem bloqueio temporal (CURRENT ou HISTORICAL_BUT_RELEVANT) |

**Relações do CC-J1 fora da simulação:**
- **Súmula 405 → 206 § 3º IX:** fica de fora por NEEDS_REVIEW.
- **Súmula 609 → 422:** também fica de fora por NEEDS_REVIEW.
- **Rejeições:** as 6 rejeições não geram relação.

**Pacote:**
- **Formato:** camada normalizada `99_JURISPRUDENCIA_V2/06_NORMALIZADO`, gerada pelo empacotador genérico. Os arquivos legados e o `REF_PAYLOAD` do J2I não são tocados.
- **Fichas novas:** 19 (7 STF e 12 STJ). Todas trazem "SIMULAÇÃO — NÃO PUBLICADO".
- **Fichas reaproveitadas do cartão:** `STF_RG_932.TXT`, que serve à CF (art. 7º, XXVIII) e ao CC (art. 927, p.u.).

## Ponta a ponta (modelo do firmware multinorma)

**Código Civil:** para cada uma das chaves do CC, o fluxo testado é:
1. abrir o Código Civil;
2. localizar o artigo;
3. abrir JURIS. e conferir a lista;
4. selecionar cada precedente e abrir a ficha (existente, título sem "OUTRO");
5. BACK, que deve voltar à mesma lista;
6. voltar ao artigo, que deve estar no mesmo estado.

**Resultado: PASS.**

**Súmula 403 (regressão):**
- Os arts. 186 e 927 listam `Súmula 403 STJ` e `ADI 6792/7055`.
- **Uma única ficha** (`STJ_SUMULA_403.TXT`) serve aos dois targets.
- O art. 927, p.u., lista `RG TEMA 932`, com a mesma ficha física usada pela CF.

**Constituição depois do CC:** todas as chaves da CF depois de abrir o CC dão a mesma lista do pacote só com a CF. **CF_AFTER_CC_REGRESSION = PASS.**

## Limites (honestos)

- **Simulação:** o teste roda no modelo host das funções C (`multinorm_sim.py`), não no ESP32. Tempos, PSRAM em execução e renderização na tela não foram verificados.
- **Firmware:** o protótipo multinorma está compilado (+5.332 B de programa, +40 B de RAM, 203.216 B livres) e **não** foi gravado.
- **Ratificação:** as relações do CC são propostas `AWAITING_USER_RATIFICATION`.
