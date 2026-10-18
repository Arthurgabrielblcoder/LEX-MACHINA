# CC-J1 — primeiro deploy físico de jurisprudência multinorma (somente dados)

```
CC_J1_DEPLOY = PASS · SD_DRIVE = D: · ADDITIVE ONLY (23 arquivos criados; 0 modificados; 0 removidos) · FIRMWARE_FLASHED = NO
MULTINORM_FIRMWARE_PHYSICAL_VALIDATION = 25/25 PASS (registrado) · CC_J1_PHYSICAL_VALIDATION = PENDENTE (teste humano)
```

Ferramenta: `deploy_cc_j1_sd.py` (etapas `pre`, `copy` e `verify`). Evidências em `CC_J1_PHYSICAL_DEPLOY/`. Manifestos completos PRE e POST também ficam em `DEVICE_INTEGRATION/backups/cc_j1_physical_deploy/` (fora do Git). Testes: `tests/test_cc_j1_physical_deploy.py`.

## 0. Firmware multinorma: aprovação física registrada

`firmware_multinorm/PHYSICAL_FLASH/MULTINORM_PHYSICAL_VALIDATION.json` registra:

| Item | Valor |
|---|---|
| Resultado | **25/25 PASS**, informado pelo usuário em 2026-10-18 |
| App testado | `38c4d71f77b89223860a6643ef9880416cb1f22a8ba933524e6b083442216bb2` (1.107.504 B, 0x10000); commit do flash `07d3dc6` |
| Cartão usado | J2I/J2H (build `def71b31a64c2a54`), CF/ADCT 315/198, sem o CC e sem camada normalizada |
| Resultados | regressões aprovadas; nenhum CC antes do deploy; nenhum vazamento entre normas |

O projeto não tem convenção de tag para firmware (as tags físicas são por camada de dados), por isso nenhuma tag foi criada.

## 1. Cartão e PRE (`physical_pre.json`)

| Item | Valor |
|---|---|
| Unidade | **D:**, a única removível (FAT32, 31,9 GB, "Generic STORAGE DEVICE" USB); assinatura do acervo conferida (`99_LEX_V1`, `99_JURISPRUDENCIA_V2`, `99_RELATIONS_V2`, `1- CONSTITUIÇÃO FEDERAL`, `2- CÓDIGO CIVIL`) |
| Arquivos | 1.190, **idênticos** ao manifesto `J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json` (0 alterados, 0 extras, 0 ausentes) → **SD_PRE_BASELINE_MATCH = PASS** |
| CF/ADCT (recontado do `REF_PAYLOAD` do cartão) | **315 / 198** |
| CC2002 no cartão | 0 linhas no lookup; camada `06_NORMALIZADO` ausente |
| Tema 932 | `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_932.TXT`, 672 B, sha256 físico `7bd339337d38caefb5505c8933b395df9a6d129195e9b02060e40f196a10e4d5` = preflight = manifesto J2H → **TEMA932_SHARED_FICHA = VERIFIED_PHYSICAL_REUSE** |
| Candidato | `SHA256_MANIFEST.json` `71f9eb76…` (build `4c0615575e3da8fc`) com hashes conferidos, sem extras; 29 relações, 24 targets, 20 precedentes, 19 fichas novas, 1 compartilhada → **CCJ1_CANDIDATE_HASHES = PASS** |
| Colisões | 0. Os 23 destinos não existiam no cartão; o Tema 932 não está na lista de cópia |

## 2. Rollback (`rollback_plan.json`; ROLLBACK_TO_CF_ONLY_READY = YES; não executado)

1. Apagar **somente** os 23 arquivos criados (lista no plano) e a pasta `06_NORMALIZADO`, se ficar vazia.
2. Não restaurar nada: nenhum arquivo existente foi tocado.
3. Conferir o cartão contra o manifesto J2H (1.190 arquivos).

O firmware não é tocado. Sem a camada normalizada, o firmware multinorma volta aos índices legados, como no teste 25/25.

## 3. Deploy (`copy_log.json`)

- **Escrita segura:** `.LEX_NEW` exclusivo → fsync → readback → `os.replace` só sobre destino inexistente → readback.
- **Ordem:** 19 fichas, depois `JURISPRUDENCIA.IDX`, `LAYER.VER` e `MULTINORM_MANIFEST.json`, por último `JUR_LOOKUP.IDX`. Assim o lookup só aparece quando tudo o que ele aponta já existe.
- **Resultado:** 23 criados, 0 substituídos, 0 apagados.

## 4. Readback e diff POST (`physical_validation.json`, `sd_manifest_post_full.json`)

| Item | Valor |
|---|---|
| DEPLOYED_HASHES | **EXACT** (os 23 arquivos = `SHA256_MANIFEST.json`) |
| Arquivos no cartão | 1.190 → **1.213** (+23) |
| EXTRA_UNEXPECTED_FILES / EXISTING_FILES_MODIFIED / removidos | 0 / 0 / 0 |
| FROZEN_LAYER_CHANGES | **0**: Correlatas (`99_RELATIONS_V1/V2`), `99_LEX_V1` (ENTENDA, Referências nº 4, targets, texto), índices legados de jurisprudência e fichas existentes, todos byte-idênticos |

## 5. Recontagem e simulação sobre os bytes do cartão

| Item | Valor |
|---|---|
| CF/ADCT (LEXV1) | **315/198**, inalterado (`CF_CHANGED = NO`) |
| Camada normalizada por namespace | CF88 311 relações / 254 precedentes; ADCT 4/4; **CC2002 29 relações / 24 targets / 20 precedentes** |
| DUPLICATE_QUERY_KEYS / LOOKUP_LOST_RELATIONS | **0 / 0** |
| CC_RELATIONS_VISIBLE / CC_TARGETS_VISIBLE | **29/29 / 24/24** |
| FICHA_OPEN / BACK_SIMULATION | **29/29 / 29/29**: ficha no cartão, cabeçalho com número e tribunal, sem "OUTRO"; lista idêntica depois do BACK |
| Exclusões | PENDING_PRESENT = 0 (Tema 1194, Súmula 609); REJECTED_PRESENT = 0 (Tema 526, Súmulas 371, 451, 543, 550 e 595) |
| Ficha compartilhada | `STF_RG_932.TXT` resolve o mesmo arquivo físico pelo CC (art. 927, p.u.) e pela CF (art. 7º, XXVIII); hash inalterado; nenhuma cópia → **CROSS_NORM_SHARED_FICHA = PASS** |
| Regressão da CF com a camada nova (que o firmware passa a preferir) | todas as 315 relações alcançáveis pela chave do seu target: **CF_RELATIONS 315/315, CF_TARGETS 198/198, CF_LOST_RELATIONS 0**. O art. 62 lista `RG TEMA 33` e `RG TEMA 1196` (artigo e caput na mesma chave, nenhum perdido) → **CF_REGRESSION = PASS** |

Os 24 targets do CC, com as listas obtidas do cartão, estão em `physical_validation.json` → `cases`. Todos conferem com a ratificação.

Uma observação sobre a contagem de targets da CF: pelo ID das linhas, a camada normalizada mostra 193 targets CF88, porque artigo e caput do art. 62 compartilham a chave de leitura. Por relação, a CF continua 315/315 e 198/198.

## 6. Testes host

| Suíte | Resultado |
|---|---|
| Jurisprudência (inclui freeze J2I e gate de provisórios) | 119/119 |
| Motor (ratificação CC-J1, preflight, empacotador, simulação multinorma, STJ, deploy) | 48/48 |
| Gramática de target | 93/93 |
| Referências nº 4 | 15/15 |
| Correlatas | 115/120 (as mesmas 5 falhas históricas); NEW_REGRESSION = 0 |

## 7. Próximo passo (humano)

O ESP32 continua desconectado e nenhum boot foi feito.

1. Ejetar D: com segurança.
2. Retirar o cartão do PC.
3. Inserir o cartão no LEX MACHINA.
4. Ligar normalmente.
5. Executar o checklist físico (36 itens, abaixo).

O CC-J1 só é considerado fisicamente aprovado depois da sua confirmação.

## 8. Checklist físico do CC-J1

Nos testes com jurisprudência nova: conferir o rótulo, abrir a ficha, ler título e status, e voltar com BACK para a mesma lista.

1. Boot geral.
2. CC art. 20 → ADI 4815.
3. CC art. 21 → ADI 4815.
4. CC art. 186 → ADI 6792/7055 + Súmula 403 STJ.
5. CC art. 927, caput → ADI 6792/7055 + Súmula 403 STJ.
6. CC art. 1.790 → RG TEMA 498 + RG TEMA 809.
7. CC art. 1.723, § 1º → RG TEMA 529.
8. CC art. 1.641, II → RG TEMA 1236.
9. CC art. 927, parágrafo único → RG TEMA 932.
10. CC art. 1.420 → Súmula 308 STJ.
11. CC art. 877 → Súmula 322 STJ.
12. CC art. 1.647, III → Súmula 332 STJ.
13. CC art. 206, § 3º, IX → Súmula 405 STJ.
14. CC art. 2.028 → Súmulas 405 + 547 STJ.
15. CC art. 205 → Súmula 412 STJ.
16. CC art. 662 → Súmula 476 STJ.
17. CC art. 917 → Súmula 476 STJ.
18. CC art. 99 → Súmula 496 STJ.
19. CC art. 1.231 → Súmula 496 STJ.
20. CC art. 966 → Súmula 499 STJ.
21. CC art. 206, § 5º, I → Súmulas 503 + 547 STJ.
22. CC art. 206, § 3º, IV → Súmula 547 STJ.
23. CC art. 1.226 → Súmula 585 STJ.
24. CC art. 1.267 → Súmula 585 STJ.
25. CC art. 1.696 → Súmula 596 STJ.
26. CC art. 206-A → o Tema 1194 **não** aparece.
27. CC art. 422 → a Súmula 609 **não** aparece.
28. Nenhum dos 6 RED aparece nos targets originalmente propostos:
    - Tema 526 (art. 1.521);
    - Súmula 371 (art. 2.028);
    - Súmula 451 (art. 1.142);
    - Súmula 543 (art. 122);
    - Súmula 550 (art. 187);
    - Súmula 595 (art. 186: só ADI 6792/7055 + Súmula 403).
29. Abrir o Tema 932 no CC (art. 927, p.u.) e voltar com BACK. Depois abrir a **mesma** ficha pela CF, **art. 7º, XXVIII** (target real no baseline: `CF88:ART.7:INC.XXVIII`).
30. CF art. 62 → RG TEMA 33 e RG TEMA 1196 (nenhuma perdida).
31. CF art. 53, § 1º → HC 232627.
32. CF art. 15, III → Súmula 9 TSE.
33. ADCT art. 107-A → somente ADI 7064.
34. CF art. 196 → REF. → "Sicko - S.O.S. Saúde".
35. CF art. 127 → ENTENDA abre.
36. CF art. 202, § 5º → CORR. → LC 108/2001, art. 26.
