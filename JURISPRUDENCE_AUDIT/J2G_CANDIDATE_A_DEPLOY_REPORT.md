# J2G — Deploy controlado do Candidato A (SD-only, firmware atual)

```
J2G_STATUS = PASS · INSTALLED_CANDIDATE = A (J2_CURRENT_FW_CANDIDATE) · PHYSICAL_BASELINE (antes) = J2C 261/160 · INSTALADO = 299/186
FIRMWARE_FLASHED = NO · FIRMWARE_CHANGED = NO · CANDIDATE_B = NÃO USADO · BATCH10 = NÃO INICIADO · READY_FOR_PHYSICAL_TEST = YES
```

## 1. Base e gates (antes de qualquer escrita)

| Gate | Resultado |
|---|---|
| Branch / pacote | `cf-jurisprudence-audit`; pacote construído no commit `64564d6` (build `7fa6c609d2aadbc7`) |
| Reconciliação 301 × 261 | PASS: vínculos físicos 261, targets 160, linhas do índice legado 301; 301 ≠ vínculos físicos: SIM |
| Gate de provisórios (data real: 2026-10-17) | PASS: STF:ADI:7697 1/90 dias; STF:ADI:5017 0/90 dias; STF:ADPF:378 0/180 dias; STF:RCL:84738 0/90 dias |
| Tema 935 | Evidência ratificada preservada: acórdão de mérito publicado em 09/12/2025, sem trânsito em julgado; não provisório; ficha com nota |
| PREDEPLOY_SD_BASELINE | PASS: 1145 arquivos de D:\ idênticos ao manifesto físico J2C (sem adição, remoção ou mudança) |
| Pacote | Candidato A (`firmware_files = null`); o deployer recusa o Candidato B |

## 2. Rollback (`ROLLBACK_READY = YES`)

- **Cópia PRE real do cartão:** `DEVICE_INTEGRATION/backups/juris_j2g_physical_deploy/sd_pre/` (fora do Git), com 7 arquivos.
- **ROLLBACK_DELETE_FILES:** 30 fichas novas, a apagar para voltar ao J2C (lista na seção 3).
- **Procedimento:**
  1. Apagar os arquivos de `ROLLBACK_DELETE_FILES`.
  2. Restaurar os 7 arquivos de `sd_pre`.
  3. Conferir o cartão com `J2C_PHYSICAL_DEPLOY/sd_manifest_post_full.json`.

| Arquivo substituído | sha256 PRE (J2C) | sha256 instalado |
|---|---|---|
| `99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX` | `05e9c2afec5991d2…` | `c4c12a764cf76a81…` |
| `99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX` | `603d9963181727d2…` | `3d2b5f3ebf81dfcf…` |
| `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | `62b06deb45b3c1ec…` | `716f79a1f48410e0…` |
| `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | `aa84fbbf8929495a…` | `ba00a4e9c01d31fb…` |
| `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | `103abadec9c4af3c…` | `8b422e1d4eb18a0b…` |
| `99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | `dce393db84f7fe8a…` | `441a6b751896c54c…` |
| `99_LEX_V1/00_SYS/LEXV1.VER` | `01ff09b4af77e4bb…` | `16449faf75c592e8…` |

## 3. Arquivos criados (30)

- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_1254.TXT` (`77c81b555987371a…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_1616.TXT` (`be3702ba3b787e71…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_2404.TXT` (`d83e6a28c4e4f177…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_2681.TXT` (`a66b3b7329e8aea9…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_2777.TXT` (`696285860cdede37…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_3114.TXT` (`0570701cb199267b…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_336.TXT` (`2cbcfc1664527e34…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_3395.TXT` (`d3f4d35b41787a5c…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_3423-3392-3432-3520.TXT` (`529697f1a298abc8…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_3684.TXT` (`cb6052ee2c0955fe…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_5017.TXT` (`d79aae45b6755bd1…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_6457.TXT` (`f664f4769d86bd34…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7064.TXT` (`2ea5247aa0f5ac34…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7369.TXT` (`933e028dd9ac73bb…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_789.TXT` (`7ff33d2d192dd544…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_978.TXT` (`313c40abf73178d4…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_1046.TXT` (`8622593c5c045548…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_1068.TXT` (`9ee0b4932825eda0…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_1093.TXT` (`2d544ef8ffef86da…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_1229.TXT` (`a20a82afc7b07498…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_157.TXT` (`d5354b3b34232d92…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_184.TXT` (`cdc4d04f08a01e2d…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_201.TXT` (`cc39b1a3e38aa5d7…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_793.TXT` (`b4c52c4ea0d77aee…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_835.TXT` (`6b4fa9a9da7de101…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_855.TXT` (`79c327ebec18e265…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_935.TXT` (`e646d6035425d17f…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_950.TXT` (`0c0252364b92e8e4…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_SV_46.TXT` (`8fe0e0b1ff3502cb…`)
- `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_SV_5.TXT` (`3a2121448c56c7ab…`)

## 4. Índices legados (só acréscimo)

| Arquivo | LEGACY_PREFIX_IDENTICAL | OLD_OFFSETS_PRESERVED | Linhas antigas | Linhas acrescentadas |
|---|---|---|---:|---:|
| `JURISPRUDENCIA.IDX` | YES | YES | 302 | 38 |
| `JUR_LOOKUP.IDX` | YES | YES | 184 | 38 |

Registros legados no cartão: 339 (= 301 + 38). Soma das quantidades do lookup: 339. Regras do cache de boot: OK.

## 5. Validação pós-deploy (lida dos bytes de D:\)

| Verificação | Resultado |
|---|---|
| SD_HASHES | ALL_EXACT |
| MANIFEST_VS_SD | PASS |
| CARD_FILESET_MATCHES_CANDIDATE | YES |
| UNEXPECTED_SD_CHANGES | 0 |
| Arquivos substituídos / criados / apagados | 7 / 30 / 0 |
| Arquivos no cartão (antes → depois) | 1145 → 1175 |
| JURIS_RELATIONS / JURIS_TARGETS (recontados no cartão) | 299 / 186 |
| LEGACY_261_RELATIONS_PRESERVED | 261/261 |
| Itens antigos preservados nos targets que receberam novos | True |
| Targets não afetados idênticos | True |
| Relações acrescentadas = Candidato A | 38 (conjunto exato: True) |
| CORRELATAS_CHANGED / WORK_REFERENCES_CHANGED / ENTENDA_CHANGED | NO / NO / NO |
| Flags alteradas | E=0, C=0, J=26, W=0, R=0, X=0 |
| J = jurisprudência visível | True |
| R_FLAG_KNOWN_DIVERGENCE | 65. Só registro: nenhuma flag R mudou. O número sobe em relação ao J2C porque o REF_LOOKUP ganhou os novos targets de jurisprudência e a R histórica, que o firmware não lê, não foi recalculada |
| NO_LABEL_OUTRO (firmware atual simulado) | YES |
| Todos os IDs com prefixo STF: | True |
| Toda relação resolve com ficha no cartão | True |
| Tipos no índice legado | adi 27, repercussao_geral 296, sumula_vinculante 16 |
| GENERIC_FW_ONLY_RELATIONS_PUBLISHED | 0 |
| REJECTED_RELATIONS_PUBLISHED | 0 (12 pares rejeitados conferidos, Batches 01–09) |
| DUPLICATE / ALREADY_COVERED que criaram relação | 0 |
| Provisórios no cartão | ADI 5017 (CAUTELAR), ADI 7697 (CAUTELAR) |
| Correlatas (art. 202, § 5º) | EXT_LC108_2001 |
| Referências nº 4 (art. 196) | Sicko - S.O.S. Saúde |
| ENTENDA (art. 127) | True |

**Amostras (lista exibida pelo firmware atual simulado sobre os bytes do cartão):**

| Target | Lista | OK |
|---|---|---|
| CF88:ART.23:INC.II | RG TEMA 793 | PASS |
| CF88:ART.22:INC.I | SV 46, RG TEMA 1246 | PASS |
| CF88:ART.85:PAR.UNICO | SV 46 | PASS |
| ADCT:ART.101:PAR.5 | ADI 7047/7064 | PASS |
| ADCT:ART.107-A | ADI 7064 | PASS |
| CF88:ART.100:PAR.11 | ADI 7047/7064 | PASS |
| CF88:ART.103:PAR.3 | ADI 1254, ADI 1616 | PASS |
| ADCT:ART.27:PAR.11 | ADI 5017 (CAUTELAR) | PASS |
| CF88:ART.31:PAR.2 | RG TEMA 157, RG TEMA 835 | PASS |
| CF88:ART.5:INC.LV | SV 5 | PASS |
| CF88:ART.7:INC.XXVI | RG TEMA 1046, RG TEMA 935 | PASS |
| CF88:ART.5:INC.XXXVIII | RG TEMA 1068, RG TEMA 154 | PASS |
| CF88:ART.5:INC.LXVII | SV 25, RG TEMA 937 | PASS |
| CF88:ART.14:PAR.5 | RG TEMA 1229, RG TEMA 172, RG TEMA 564 | PASS |
| CF88:ART.142 | ADI 6457 | PASS |
| CF88:ART.150:PAR.7 | ADI 2777, RG TEMA 201 | PASS |
| CF88:ART.155:PAR.2:INC.VII | RG TEMA 1093 | PASS |
| CF88:ART.166-A | ADI 7697 (CAUTELAR) | PASS |
| CF88:ART.100 | ADI 4425, RG TEMA 1262, RG TEMA 253, RG TEMA 416, RG TEMA 558, RG TEMA 831 | PASS |

No ADCT 107-A a lista é exatamente "ADI 7064"; o registro conjunto 7047/7064 não aparece ali.

**Ausências conferidas no cartão:**
- HC 232627 e HC 70648;
- MS 21689, 21564 e 27931;
- AP 694 e AI 343461;
- Inq 4781 e Inq 672;
- Rcl 84738;
- ADPF 378, 964 e 672;
- Súmula 702 STF, Súmula 9 TSE e Súmula 403 STJ.

## 6. Testes host pós-deploy

| Suíte | Resultado |
|---|---|
| Jurisprudência (inclui candidatos J2F e gate de provisórios) | 98/98 |
| Motor de referências | 90/90 |
| Referências nº 4 | 15/15 |
| Correlatas | 115/120. As 5 falhas históricas são idênticas nome a nome: c0 `test_committed_artifacts_are_the_build`, c3a1 `test_15`, c3a_engine `test_16`, c3b1 `test_reproducible`, c3b2 `test_c3b2_package_reproducible…`. NEW_REGRESSION = 0 |

## 7. Checklist físico (para o usuário; não executado)

Recoloque o microSD no LEX MACHINA, com o **mesmo firmware** de hoje (não gravar nada), e confira:

1. **Boot:** liga normalmente, sem erro de cartão; a tela inicial abre a CF.
2. **CF art. 23, II → JURIS:** aparece **RG TEMA 793**; abrir a ficha.
3. **CF art. 22, I → JURIS:** aparecem **SV 46** e RG TEMA 1246; abrir a SV 46.
4. **CF art. 85, parágrafo único → JURIS:** aparece **SV 46** e a ficha é a mesma do item 3.
5. **ADCT art. 101, § 5º → JURIS:** aparece **ADI 7047/7064**.
6. **ADCT art. 107-A → JURIS:** aparece **só ADI 7064**, sem 7047/7064; abrir a ficha.
7. **CF art. 100, § 11 → JURIS:** aparece **ADI 7047/7064**.
8. **ADCT art. 27, § 11 → JURIS:** aparece **ADI 5017 (CAUTELAR)**; a ficha mostra "DECISÃO PROVISÓRIA".
9. **CF art. 31, § 2º → JURIS:** aparecem **RG TEMA 157** e **RG TEMA 835**.
10. **CF art. 5º, LV → JURIS:** aparece **SV 5**.
11. **CF art. 7º, XXVI → JURIS:** aparecem **RG TEMA 1046** e **RG TEMA 935**; a ficha do 935 tem a nota sobre o acórdão de 09/12/2025.
12. **CF art. 5º, XXXVIII → JURIS:** aparecem **RG TEMA 1068** e RG TEMA 154.
13. **CF art. 5º, LXVII → JURIS:** aparecem **SV 25** e RG TEMA 937.
14. **CF art. 14, § 5º → JURIS:** aparecem **RG TEMA 1229**, RG TEMA 172 e RG TEMA 564.
15. **CF art. 142 → JURIS:** aparece **ADI 6457**.
16. **CF art. 150, § 7º → JURIS:** aparecem **ADI 2777** e **RG TEMA 201**.
17. **CF art. 155, § 2º, VII → JURIS:** aparece **RG TEMA 1093**.
18. **CF art. 103, § 3º → JURIS:** aparecem **ADI 1254** e **ADI 1616**.
19. **Regressão da ADI 7697:** art. 166-A → **ADI 7697 (CAUTELAR)**; art. 166, §§ 9º e 11 continuam.
20. **Regressão do Tema 558:** CF art. 100 → RG TEMA 558 continua (com ADI 4425 e Temas 1262, 253, 416, 831); art. 100, § 9º sem o Tema 558.
21. **Regressão das camadas congeladas:** CF art. 202, § 5º → CORR. → LC 108/2001; CF art. 196 → REF. → "Sicko - S.O.S. Saúde"; CF art. 127 → ENTENDA abre.
22. **Sem tipo novo:** em nenhum artigo deve aparecer "OUTRO n", HC, MS, AP, Inq, Rcl, ADPF ou Súmula TSE/STJ.

**Se algo falhar:**
- não corrija nada no cartão;
- anote o item e a tela;
- o rollback (seção 2) devolve o cartão ao J2C.

## 8. Ferramentas

- `deploy_j2g_sd.py` (`pre`, `copy`, `verify`);
- `semantic_check_j2g_sd.py`;
- evidências em `JURISPRUDENCE_AUDIT/J2G_PHYSICAL_DEPLOY/`;
- backups em `DEVICE_INTEGRATION/backups/juris_j2g_physical_deploy/` (fora do Git).
