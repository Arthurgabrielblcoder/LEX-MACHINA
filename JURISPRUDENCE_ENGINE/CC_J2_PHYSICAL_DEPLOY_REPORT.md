# CC-J2 — deploy físico misto transacional (somente dados)

```
CC_J2_DEPLOY = PASS · DEPLOY_MODE = MIXED_TRANSACTIONAL · SD_DRIVE = D: · FIRMWARE_FLASHED = NO
SD_PRE_CC = 29/24 → SD_POST_CC = 49/39 · SD_POST_TOTAL = 364/237 · CF/ADCT = 315/198 (inalterado)
17 fichas criadas · 4 arquivos da 06_NORMALIZADO substituídos · UNEXPECTED_CHANGED_FILES = 0 · FROZEN_LAYER_CHANGES = 0
CC_J2_PHYSICAL_VALIDATION = PENDENTE (teste humano)
```

Ferramenta: `deploy_cc_j2_sd.py`, com as etapas `pre`, `copy`, `verify` e `rollback`.
- **Evidências:** `CC_J2_PHYSICAL_DEPLOY/`.
- **Backup e manifestos completos PRE/POST:** `DEVICE_INTEGRATION/backups/cc_j2_physical_deploy/` (fora do Git).
- **Testes:** `tests/test_cc_j2_physical_deploy.py`.

## 0. Ensaio antes do cartão

Antes de tocar no cartão real, o script rodou inteiro num cartão simulado montado no scratchpad:
- **Deploy completo:** todos os gates PASS.
- **Rollback explícito:** o cartão voltou idêntico ao PRE.
- **Falha injetada no commit:** a falha ocorreu depois de 3 dos 4 índices já substituídos. Os 4 arquivos PRE foram restaurados, as 17 fichas apagadas, e o cartão voltou idêntico ao PRE.

## 1. Hardware e PRE (`physical_pre.json`)

| Item | Valor |
|---|---|
| Unidade | **D:**, a única removível (FAT32, 31,9 GB, "Generic STORAGE DEVICE" USB); assinatura do acervo conferida |
| ESP32 | desconectado (só COM1; o CH343/COM3 ausente) |
| Cartão inteiro | 1.213 arquivos, **idênticos** a `CC_J1_PHYSICAL_DEPLOY/sd_manifest_post_full.json` → **SD_PRE_BASELINE_MATCH = PASS** |
| Recontagem dos bytes | CF/ADCT (LEXV1) **315/198**; CC2002 na camada normalizada **29/24**; CC-J1 29/29; vínculos do CC-J2 já presentes: **0** |
| Tema 932 | sha256 físico `7bd33933…` = freeze |
| Candidato | `SHA256_MANIFEST.json` `a4e496bc…` (build `1b0a0f5118787684`), hashes conferidos; 17 arquivos aditivos + 4 substituições; preflight 20/18/15/17/2/0/0 → **CCJ2_CANDIDATE = PASS** |
| Arquivos a substituir | os 4 do cartão = os "antes" do candidato |
| Colisões das fichas novas | **0** (nenhum caminho existia; nenhum temporário) |

## 2. Backup PRE (`rollback_plan.json`; ROLLBACK_TO_CCJ1_29_24_READY = YES)

| Arquivo | Bytes | sha256 |
|---|---:|---|
| 06_NORMALIZADO/JURISPRUDENCIA.IDX | 63.241 | `181416428f2a8bac…` |
| 06_NORMALIZADO/JUR_LOOKUP.IDX | 4.734 | `135e81a52ddbfc08…` |
| 06_NORMALIZADO/LAYER.VER | 277 | `28808539de6058c7…` |
| 06_NORMALIZADO/MULTINORM_MANIFEST.json | 4.003 | `0939d31153243a58…` |

O backup é cópia byte a byte, conferida, mais o manifesto completo PRE (1.213 arquivos).

Rollback, não executado:
1. restaurar exatamente esses 4 arquivos;
2. apagar exatamente as 17 fichas;
3. não tocar em mais nada;
4. conferir o cartão contra o manifesto do CC-J1.

## 3. Deploy transacional (`copy_log.json`)

1. **Fase 5 (aditiva):** 17 fichas. Cada uma vai para um temporário `.ccj2.tmp` (criação exclusiva) → fsync → readback → `os.replace` sobre destino inexistente → readback. **NEW_FICHAS_READBACK = EXACT.**
2. **Fase 6 (staging):** os 4 índices vão para `<nome>.ccj2.tmp` no mesmo diretório, com fsync e readback. **NORMALIZED_STAGING = PASS** antes de qualquer substituição.
3. **Fase 7 (commit):** `os.replace`, sem apagar antes, na ordem JURISPRUDENCIA.IDX → LAYER.VER → MULTINORM_MANIFEST.json → **JUR_LOOKUP.IDX por último**, com readback a cada passo. **NORMALIZED_READBACK = EXACT.** Abortado: não; restaurado: não; temporários restantes: 0.

## 4. POST (`physical_validation.json`, `sd_manifest_post_full.json`)

| Item | Valor |
|---|---|
| DEPLOYED_HASHES | **EXACT** |
| Arquivos | 1.213 → **1.230** (+17); alterados: só os 4 da 06_NORMALIZADO; removidos: 0 → **UNEXPECTED_CHANGED_FILES = 0** |
| Camadas congeladas | Correlatas, LEXV1 (ENTENDA, Referências nº 4, targets, texto), índices legados, fichas existentes e lei seca → **FROZEN_LAYER_CHANGES = 0** |
| Novos índices | JURISPRUDENCIA.IDX 66.909 B `d2f23058…`; JUR_LOOKUP.IDX 5.087 B `5d88ce3b…`; LAYER.VER 368 B `aae064b4…`; manifesto 3.851 B `e52f48fe…` |

## 5. Recontagem e simulação sobre os bytes do cartão

| Item | Valor |
|---|---|
| CF/ADCT (LEXV1) | **315/198** |
| Camada normalizada | CF88 311 · ADCT 4 · **CC2002 49** relações / **39** targets → **TOTAL 364/237** |
| CC-J1 / CC-J2 | **29/29** relações e 24/24 targets / **20/20** relações e **18/18** targets (lista completa, ficha, BACK, mesma lista) |
| DUPLICATE_QUERY_KEYS · cache | 0 · 236 chaves de 4.096 |
| Targets compartilhados | 206 § 5º I = Súm. 503 + 547 + REP 639 · 206 § 3º IV = Súm. 547 + REP 610 · 1.641 II = RG 1236 + Súm. 655 · 1.829 = RG 498 + RG 809 → PASS |
| Casos críticos | Súmula 642 só no art. 943 (nenhum 943, I) · Tema 1130 no art. 76, p.u., não provisório, ficha cita o Tema 1432 · IAC 1 no art. 202, p.u. (CPC/1973) · Tema 381 com EXCLUSION_CONTEXT · Súmula 637 com EXCEÇÃO · Súmula 655 com o Tema 1236 → todos PASS |
| Rótulos (modelo do firmware) | `IAC n`, `REPETITIVO STJ n`, `RG TEMA n`, `Súmula n STJ`; OUTRO = 0 → IAC_LABEL = PASS, REPETITIVO_STJ_LABEL = PASS |
| Fichas reaproveitadas | STF_RG_498 / STF_RG_809 inalteradas, resolvidas pelo art. 1.829 → SHARED_FICHAS = PASS |
| Rejeitadas | REJECTED_RELATIONS_PRESENT = 0 |
| CF | 315/315 relações, 198/198 targets, 0 chaves CF/ADCT alteradas; art. 62 = RG TEMA 33 + RG TEMA 1196 → CF_REGRESSION = PASS |
| Tema 932 entre normas | CC 927 p.u. e CF 7º XXVIII abrem a mesma `STF_RG_932.TXT` → PASS |

## 6. Ejeção

O cartão foi ejetado com segurança pelo Windows; D: ficou sem mídia. O firmware não foi gravado.

## 7. Próximo passo (humano)

Recolocar o cartão no LEX MACHINA, ligar e executar o checklist abaixo. O CC-J2 só será considerado fisicamente aprovado depois da sua confirmação. Se algum item falhar, o cartão volta ao PC para o rollback (`python deploy_cc_j2_sd.py rollback D:`).

## 8. Checklist físico do CC-J2

Em todo item novo, conferir: rótulo, abrir a ficha, conteúdo, BACK de volta à mesma lista.

1. Boot geral (sem erro de cartão; jurisprudência carregada).
2. **IAC:** CC art. 202, parágrafo único → "IAC 1". A ficha diz HISTORICAL_BUT_RELEVANT e CPC/1973.
3. **Repetitivo STJ (1):** CC art. 405 → "REPETITIVO STJ 1133".
4. **Repetitivo STJ (2):** CC art. 50 → "REPETITIVO STJ 1210".
5. **Repetitivo STJ (3):** CC art. 354 → "REPETITIVO STJ 381" e "REPETITIVO STJ 426". A ficha do 381 começa por INAPLICABILIDADE À COMPENSAÇÃO TRIBUTÁRIA.
6. **Súmula 642:** CC art. 943 → "Súmula 642 STJ". A ficha explica a correção ART943_INC1 → ART943; não existe "art. 943, I".
7. **Tema 1130:** CC art. 76, parágrafo único → "REPETITIVO STJ 1130". A ficha não diz provisório e cita o Tema 1432/STF.
8. **Súmula 655:** CC art. 1.641, II → "RG TEMA 1236" e "Súmula 655 STJ". A ficha da 655 traz a qualificação do Tema 1236.
9. **Compartilhado:** CC art. 206, § 5º, I → Súmula 503, Súmula 547 e REPETITIVO STJ 639 (3 itens).
10. **Compartilhado:** CC art. 206, § 3º, IV → Súmula 547 e REPETITIVO STJ 610 (2 itens).
11. **Fichas reaproveitadas:** CC art. 1.829 → RG TEMA 498 e RG TEMA 809 (as mesmas fichas do art. 1.790).
12. **Súmula 637:** CC art. 1.210, § 2º → a ficha indica a exceção.
13. **Súmula 619:** CC art. 1.208 e art. 1.255 → a mesma ficha "Súmula 619 STJ" nos dois.
14. **Novos targets:** CC art. 835 (Súmula 656), art. 286 (REP 368), art. 191 (REP 1109), art. 206, § 3º, III (REP 308), art. 1.238, p.u. (REP 1019).
15. **Regressão CC-J1:** art. 20 (ADI 4815), art. 186 (ADI 6792/7055 + Súm. 403), art. 1.790 (RG 498 + 809), art. 927, p.u. (RG 932), art. 2.028 (Súm. 405 + 547), art. 1.696 (Súm. 596).
16. **Negativos:** art. 206-A sem Tema 1194; art. 422 sem Súmula 609; art. 1.639, § 2º sem Tema 1236; art. 1.566, I sem Tema 529; art. 368 sem Tema 587.
17. **Tema 932 entre normas:** CC art. 927, p.u. e CF art. 7º, XXVIII abrem a mesma ficha.
18. **Regressão CF:** art. 62 → RG TEMA 33 e RG TEMA 1196; art. 53, § 1º → HC 232627; art. 15, III → Súmula 9 TSE; ADCT art. 107-A → só ADI 7064.
19. **Referências nº 4:** CF art. 196 → REF. → "Sicko - S.O.S. Saúde".
20. **ENTENDA:** CF art. 127 → ENTENDA abre.
21. **Correlatas:** CF art. 202, § 5º → CORR. → LC 108/2001, art. 26.
