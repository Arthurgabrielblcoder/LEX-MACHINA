# CC-J2 — MATERIALIZATION PREFLIGHT (host-only)

```
CC_J2_PREFLIGHT = PARTIAL · ADDITIVE_ONLY = NO · SD_CHANGED = NO · FIRMWARE_CHANGED = NO
RELAÇÕES 20 · TARGETS 18 (15 novos) · CC 49/39 · TOTAL 364/237
DUPLICATE_QUERY_KEYS 0 · LOOKUP_LOST_RELATIONS 0 · CCJ1_REGRESSION 0 · CF_REGRESSION 0
```

## 1. Ratificação autoritativa

`CC_J2_RATIFICATION_RECORD.json`, com todos os hashes fixados reconferidos: PASS. Aprovadas 19, não aprovadas 11, pendentes 0. REJECTED_MATERIALIZED = 0.

## 2–4. Relações e targets

| Target | Lista no aparelho (simulada) | E2E |
|---|---|---|
| CC2002:ART.50 | REPETITIVO STJ 1210 | PASS |
| CC2002:ART.76:PAR.UNICO | REPETITIVO STJ 1130 | PASS |
| CC2002:ART.191 | REPETITIVO STJ 1109 | PASS |
| CC2002:ART.202:PAR.UNICO | IAC 1 | PASS |
| CC2002:ART.206:PAR.3:INC.III | REPETITIVO STJ 308 | PASS |
| CC2002:ART.206:PAR.3:INC.IV | Súmula 547 STJ; REPETITIVO STJ 610 | PASS |
| CC2002:ART.206:PAR.5:INC.I | Súmula 503 STJ; Súmula 547 STJ; REPETITIVO STJ 639 | PASS |
| CC2002:ART.286 | REPETITIVO STJ 368 | PASS |
| CC2002:ART.354 | REPETITIVO STJ 381; REPETITIVO STJ 426 | PASS |
| CC2002:ART.405 | REPETITIVO STJ 1133 | PASS |
| CC2002:ART.835 | Súmula 656 STJ | PASS |
| CC2002:ART.943 | Súmula 642 STJ | PASS |
| CC2002:ART.1208 | Súmula 619 STJ | PASS |
| CC2002:ART.1210:PAR.2 | Súmula 637 STJ | PASS |
| CC2002:ART.1238:PAR.UNICO | REPETITIVO STJ 1019 | PASS |
| CC2002:ART.1255 | Súmula 619 STJ | PASS |
| CC2002:ART.1641:INC.II | RG TEMA 1236; Súmula 655 STJ | PASS |
| CC2002:ART.1829 | RG TEMA 498; RG TEMA 809 | PASS |

Targets novos (15): CC2002:ART.50, CC2002:ART.76:PAR.UNICO, CC2002:ART.191, CC2002:ART.202:PAR.UNICO, CC2002:ART.206:PAR.3:INC.III, CC2002:ART.286, CC2002:ART.354, CC2002:ART.405, CC2002:ART.835, CC2002:ART.943, CC2002:ART.1208, CC2002:ART.1210:PAR.2, CC2002:ART.1238:PAR.UNICO, CC2002:ART.1255, CC2002:ART.1829.
Todos os 18 existem no índice do CC2002, com granularidade correta, round-trip do ID, namespace CC2002 e sem nota de revogação (INVALID_TARGETS = 0). A Súmula 642 está só no art. 943 (INVALID_ART943_INC1_TARGET_CREATED = NO).

Targets compartilhados (listas antigas preservadas, novas acrescentadas no fim): CC2002:ART.206:PAR.5:INC.I PASS, CC2002:ART.206:PAR.3:INC.IV PASS, CC2002:ART.1641:INC.II PASS, CC2002:ART.1829 PASS, CC2002:ART.354 PASS.

## 5–7. Fichas e tipos

Fichas lógicas 19: 17 novas e 2 reaproveitadas do cartão (STF_RG_498.TXT, STF_RG_809.TXT, mesmos bytes; a nota delas já cita o art. 1.829). Bytes duplicados: 0.
Tipos novos: {'iac': 1, 'repetitivo_stj': 11, 'sumula': 5}. Tribunais: {'STF': 2, 'STJ': 17}. Fichas compartilhadas entre normas: STF_RG_932 (CF + CC), STF_ADI_7047-7064 (CF + ADCT).
As notas ratificadas estão nas fichas: IAC 1 (HISTORICAL_BUT_RELEVANT, CPC/1973), Súmula 637 (EXCEPTION), Súmula 655 (SUBJECT_TO_TEMA_1236_STF), Tema 381 (abre com INAPLICABILIDADE À COMPENSAÇÃO TRIBUTÁRIA), Tema 1130 (STJ defasado × Tema 1432/STF), Súmula 642 (proveniência ART943_INC1 → ART943).

## 8–9. IAC e REPETITIVO STJ

Rótulos derivados de `juris_types.label`. Visto na simulação: {'IAC n': 1, 'REPETITIVO STJ n': 11, 'RG TEMA n': 2, 'Súmula n STJ': 6}; rótulos OUTRO: 0. IAC_LABEL_SIMULATION = PASS, REPETITIVO_STJ_LABEL_SIMULATION = PASS ("REPETITIVO STJ n", distinto de "RG TEMA n" do STF).
IAC: suporte arquitetural YES, validação física NO. REPETITIVO STJ: suporte YES, validação física NO. Súmula STJ: validada fisicamente YES (fonte: `physical_status`).
Dívida do motor: `batch_engine.py`, `apply_review`, linha 249, ainda chama `JT.device_status`. Trocar ali mudaria os hashes fixados do CC-J2 (métricas e decisões), por isso não foi trocado. Este preflight usa `JT.physical_status` diretamente; a troca no motor entra na refatoração antes do CC-J3. HISTORICAL_CCJ2_HASHES_CHANGED = NO.

## 10. Simulação (firmware multinorma, modelo host)

CC-J2: CCJ2_TARGETS_E2E = 18/18, CCJ2_RELATIONS_VISIBLE = 20/20 (abrir CC → target → JURIS → lista completa → cada ficha → BACK → mesma lista → artigo).
CC-J1: CCJ1_RELATIONS_PRESERVED = 29/29, CCJ1_TARGETS_PRESERVED = 24/24 (linhas antigas byte-idênticas e na mesma ordem; ausentes 0); CCJ1_REGRESSION = 0.
CF/ADCT: 315/315 relações e 198/198 targets alcançáveis; chaves CF/ADCT alteradas: 0; CF_REGRESSION = 0. Art. 62: RG TEMA 33, RG TEMA 1196. Tema 932 entre normas: PASS.

## 11. Cache / PSRAM

Chaves de lookup 236 de 4096 (margem 3860); registros 364; JURISPRUDENCIA.IDX 66909 B; JUR_LOOKUP.IDX 5087 B; PSRAM estimada 82958 B (camada atual: 78270 B; 68 B por entrada, medido no aparelho).

## 12. Candidato e forma de deploy

`CC_J2_MATERIALIZATION_CANDIDATE/`, imutável e host-only. Arquivos a acrescentar: 17; a substituir: 4; colisões inesperadas: 0.

**ADDITIVE_ONLY = NO.** O firmware multinorma lê caminhos FIXOS (06_NORMALIZADO/JUR_LOOKUP.IDX e JURISPRUDENCIA.IDX) e uma única camada; os índices são agregados (uma linha por chave). Acrescentar relações a uma camada já instalada exige substituir esses índices. LAYER.VER e MULTINORM_MANIFEST.json não são lidos pelo firmware, mas ficariam com contagens antigas se não forem trocados.

Arquivos que seriam substituídos (bytes atuais no cartão):

- `99_JURISPRUDENCIA_V2/06_NORMALIZADO/JUR_LOOKUP.IDX` (4734 B, `135e81a52ddbfc08…`)
- `99_JURISPRUDENCIA_V2/06_NORMALIZADO/JURISPRUDENCIA.IDX` (63241 B, `181416428f2a8bac…`)
- `99_JURISPRUDENCIA_V2/06_NORMALIZADO/MULTINORM_MANIFEST.json` (4003 B, `0939d31153243a58…`)
- `99_JURISPRUDENCIA_V2/06_NORMALIZADO/LAYER.VER` (277 B, `28808539de6058c7…`)

Opções (decisão do usuário antes de qualquer deploy):

- A — substituir os 4 arquivos da camada (2 índices + LAYER.VER + manifesto) com escrita segura e backup; rollback restaura os bytes do CC-J1 (hashes conhecidos) e apaga as fichas novas
- B — substituir só os 2 índices (mínimo para o firmware); LAYER.VER e manifesto ficam com as contagens do CC-J1
- C — mudar o firmware para ler camadas aditivas (exige novo flash e nova validação física; não recomendado agora)

Recomendação: A. O preflight fica PARTIAL até essa decisão; o candidato não está liberado para deploy.

## 13. Hashes

`SHA256_MANIFEST.json` sha256 `a4e496bcffb798fa2f42e1a9bf0ac3698a03820b2d57ea91ff90871ee7a2eb3e` (lista todos os arquivos do candidato com bytes e sha256).

## 14. Rollback (não executado)

Apagar os 17 arquivos novos e restaurar os 4 arquivos da camada a partir de `CC_J1_MATERIALIZATION_CANDIDATE` (hashes conferidos). Resultado: CC 29/24, CF/ADCT 315/198, 1.213 arquivos; firmware não muda.

## 15. Checklist físico futuro (não executado)

1. **Boot:** Boot geral; diagnóstico LEXV1 PASS; cache juris carregado pela camada normalizada.
2. **IAC (rótulo nunca validado):** CC art. 202, p.u. → "IAC 1"; abrir a ficha (HISTORICAL_BUT_RELEVANT, CPC/1973); BACK volta à mesma lista.
3. **REPETITIVO STJ (rótulo nunca validado):** CC art. 405 → "REPETITIVO STJ 1133"; abrir; BACK.
4. **REPETITIVO STJ:** CC art. 50 → "REPETITIVO STJ 1210"; abrir; BACK.
5. **REPETITIVO STJ + EXCLUSION_CONTEXT:** CC art. 354 → "REPETITIVO STJ 426" e "REPETITIVO STJ 381"; a ficha do 381 começa por INAPLICABILIDADE À COMPENSAÇÃO TRIBUTÁRIA; BACK.
6. **Súmula 642:** CC art. 943 → "Súmula 642 STJ" (ficha registra a correção ART943_INC1 → ART943); nenhum "inciso I" no art. 943.
7. **Tema 1130:** CC art. 76, p.u. → "REPETITIVO STJ 1130"; a ficha NÃO diz provisório e explica STJ defasado × Tema 1432/STF.
8. **Target compartilhado:** CC art. 206, § 5º, I → Súmula 503 + Súmula 547 + REPETITIVO STJ 639 (3 itens, os 2 antigos primeiro).
9. **Target compartilhado:** CC art. 206, § 3º, IV → Súmula 547 + REPETITIVO STJ 610 (2 itens).
10. **Target compartilhado:** CC art. 1.641, II → RG TEMA 1236 + Súmula 655 STJ; a ficha da 655 traz a qualificação do Tema 1236.
11. **Fichas reaproveitadas:** CC art. 1.829 → RG TEMA 498 + RG TEMA 809 (mesmas fichas físicas do art. 1.790).
12. **Súmula 619:** CC art. 1.208 e art. 1.255 → a mesma ficha "Súmula 619 STJ".
13. **Novos targets:** Arts. 835, 286, 191, 206 § 3º III, 1.238 p.u., 1.210 § 2º: cada um abre a ficha e volta com BACK.
14. **Regressão CC-J1:** Os 24 targets do CC-J1 (checklist 36/36) com as mesmas listas; art. 206-A sem Tema 1194; art. 422 sem Súmula 609.
15. **Rejeitados:** Nenhum dos 11 não aprovados aparece (ex.: art. 1.639, § 2º sem Tema 1236; art. 1.566, I sem Tema 529; art. 368 sem Tema 587).
16. **Tema 932 cross-norm:** CC art. 927, p.u. e CF art. 7º, XXVIII abrem a mesma ficha STF_RG_932.
17. **Regressão CF:** CF art. 62 → RG TEMA 33 e RG TEMA 1196; CF art. 53, § 1º → HC 232627; ADCT art. 107-A → só ADI 7064.
18. **Camadas congeladas:** CF art. 196 → REF. "Sicko - S.O.S. Saúde" (Referências nº 4); CF art. 127 → ENTENDA; CF art. 202, § 5º → CORR. LC 108/2001.

Nada foi implantado, gravado ou conectado. Próximo passo: decisão do usuário sobre a forma de deploy (opção A/B/C).
