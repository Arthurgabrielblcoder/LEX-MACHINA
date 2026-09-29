# DEVICE_INTEGRATION_V1_PREDEPLOY_REPORT

Baseline de predeploy do LEX DEVICE V1 (fase A2C, 2026-09-29). Nada foi escrito no cartão nem no ESP32.

## Runtime canônico

| Item | Valor |
|---|---|
| `CF88_RUNTIME.txt` | 587.133 B · 4.537 linhas · sha256 `7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a` |
| Fontes | Senado 579494 (CF, publicação 16434817) + 604119 (ADCT, publicação 16434816), Compilação Monovigente, com raw preservado |
| Normalização | `HEADER_NORMALIZATION_RULE_V1` (casos A/B/C) |
| Correção documental | `SRC-CORR-CF88-579494-16434817-ART114-INC-VIII` (`SOURCE_TRANSCRIPTION_NORMALIZATION`): `VII I -` → `VIII -`, validada contra a EC 45/2004 (Planalto, sha256 `76f9b562…`), fail closed |
| Início do ADCT | byte 429.242 |

## Targets e mapa

| Item | Valor |
|---|---|
| Targets no runtime | 3.812 (3.810 em `CF88_TARGETS.IDX`); índice sha256 `09ad649e9b0ab798af1f5991ebfaab443c050d97a4124c9c615333d6fb2d15c5` |
| Status legal | {'CURRENT': 3707, 'REVOKED': 103} |
| Legado × runtime | {'ADDED:EXPECTED_RUNTIME_CHANGE': 2, 'REMOVED:EXPECTED_REMOVAL_HISTORICAL': 143, 'REMOVED:EXPECTED_RUNTIME_CHANGE': 3}; UNEXPECTED_MISSING = 0, UNEXPECTED_NEW = 0, PARSER_ERROR = 0; exceções revisadas: CF 155, I, c (histórico/renumerado), ADCT 77, I, a/b (vigentes, antes não indexados) |
| Art. 114 | `CF88:ART.114:INC.VII`, `INC.VIII` e `INC.IX` presentes |
| `CF88_TEXT_MAP.IDX` | 3.387 registros. RUNTIME. sha256 `889f82002e82fb2b7d9165e6ce2a4e0dcb78d311432e268c341f1d0b1e436b96` |

## Camadas

| Item | Valor |
|---|---|
| ENTENDA | 163 explicações HUMAN_APPROVED_T1 (163 DIRECT); 283/283 linhas resolvem; 9 pilotos OK; 0 PENDING, 0 RETIRED |
| References | 239/242 targets no runtime; 432 linhas |
| `HISTORICAL_REFERENCE_TARGET_FILTERED` | CF88:ART.40:PAR.4:INC.II, CF88:ART.40:PAR.4:INC.III, CF88:ART.40:PAR.7:INC.I (todas as linhas `HISTORICAL_HIDDEN_BY_DEFAULT`; não navegáveis; export aprovado intacto) |

## Overlay `/99_LEX_V1`

build_id `e634aa1aa009ab25` · total 1.288.674 B

| Arquivo | Bytes | sha256 |
|---|---|---|
| `99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | 6.395 | `27fc4521c3a4ab2ec67c64cbe20050f4371fe2d65fc26846e354ceec9f96aa54` |
| `99_LEX_V1/00_SYS/LEXV1.VER` | 600 | `df1615b81d40257f0ef3890d73ab9fbfc44b83b1a4f5580145041cff958312cb` |
| `99_LEX_V1/05_TEXT/CF88_RUNTIME.txt` | 587.133 | `7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a` |
| `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | 165.466 | `36db8b871163262dacb97d5f4ecd36044ea70aa223f021f93a4dad2d91f888c1` |
| `99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX` | 123.578 | `889f82002e82fb2b7d9165e6ce2a4e0dcb78d311432e268c341f1d0b1e436b96` |
| `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | 6.579 | `9665fb854fe5b91fc5a1aa640b6eb8270583e3c6414720e99f37f9608ccb3c12` |
| `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | 65.546 | `1c772c83b6cfe381ddb1674b73126dbf2fb6cf354fe16d708194cdad0de94228` |
| `99_LEX_V1/30_ENTENDA/ENTENDA_LOOKUP.IDX` | 30.462 | `93613275d4e0caf95ed58f1fe8e29cc90039d73ec9d302fc7ce0af2e5f816ddc` |
| `99_LEX_V1/30_ENTENDA/ENTENDA_PAYLOAD.DAT` | 302.915 | `a7511b917f658fd411b0f46c241415e77148c9b1c8ed1780a797958fe640c029` |

Obs.: `LEXV1.VER` e `LEX_DEVICE_MANIFEST.json` registram o `GIT_COMMIT` do build; após o commit desta fase, um rebuild atualiza esses dois arquivos. O conteúdo jurídico e os índices não mudam (o build_id deriva só deles).

## Firmware candidato (`firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/`)

| Build | Flash | RAM estática |
|---|---|---|
| v7.12.0 original (intocada) | 989.395 B | 124.452 B |
| candidato, `LEX_DEVICE_V1_ENABLED=0` (padrão) | 989.395 B | 124.452 B |
| candidato, `LEX_DEVICE_V1_ENABLED=1` | 997.583 B | 124.452 B |

O runtime e o TEXT_MAP deste predeploy ficam fixados (`LEXV1_PINNED_*`) para diagnóstico. A guarda de segurança é tamanho + sha256 do arquivo exibido contra `LEXV1.VER` e o TEXT_MAP (fail closed).

## Rollback físico — `FULL_PHYSICAL_ROLLBACK_AVAILABLE`

| Backup | Valor |
|---|---|
| Cartão SD | `BACKUP_VERIFIED`: `backups/sd_20260929T163407Z`, 1.062 arquivos, 24.574.047 B, agregado `f00e6d562f239b23c033844b879a9afdf2b878980550068e3acc4101bad49b38`; reverificado nesta fase contra o cartão (idêntico) |
| Flash | `PHYSICAL_FLASH_BACKUP_VERIFIED`: 16 MB, sha256 `061849a357d77f571d735a108fc5f4a032d7c12e4f7e3c8f3b34c0f3357d6727` (reconferido) |

## Testes

DEVICE 39/39 · ENTENDA 80/80 · LEGAL_TARGET_ID 47/47 · runtime e staging BYTE_IDENTICAL (2 builds).

## Known issues

- **`RELATIONS_V2_LEGACY_64_LINE_LIMIT`:** NON_BLOCKING. O cartão físico tem 41/64 (`REL_LOOKUP`) e 20/32 (`EXT_NORMAS`). A V1 usa o Reference Engine; a correção está proposta.
- **Referências do art. 114, VIII:** o target agora existe, mas as duas referências aprovadas (SV 53, Tema 36) continuam `HISTORICAL_HIDDEN_BY_DEFAULT` no Reference Engine aprovado, cuja classificação veio do defeito da fonte. Não foi editado; revisitar numa fase do Reference Engine.
- **Parser legado do firmware:** 97,3% de concordância com o mapa (sufixos de letra e fragmentos de link do ADCT). Fica apenas como diagnóstico; a fonte primária é o TEXT_MAP.
