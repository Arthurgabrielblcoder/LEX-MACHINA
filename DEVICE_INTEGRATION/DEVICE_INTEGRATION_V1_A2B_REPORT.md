# DEVICE INTEGRATION V1-A2B — relatório para revisão humana

**Resultado:** runtime canônico e rollback físico prontos. Nada foi escrito no cartão nem no ESP32, e nada foi commitado.

| Item | Resultado |
|---|---|
| Fontes oficiais | CF: Senado 579494, publicação 16434817. ADCT: Senado 604119, publicação 16434816. Ambas Compilação Monovigente, com resposta bruta, metadata e sha256 guardados (`updater/fontes_oficiais_senado/`). Detalhes em `ADCT_SOURCE_INGESTION_REPORT.md` |
| Pipeline | `FONTES_ESPECIAIS_MESTRE['ADCT']` em `updater/main.py`; `ingerir_fontes_oficiais_senado.py`; `exportar_cf88_runtime.py` |
| CF88_RUNTIME | 587.134 B, 4.537 linhas, sha256 `75a27b0a2899e7082a2bf65f06f2725b1a40874746c49091e08225dd266e7998`; ADCT a partir do byte 429.243; 0 marcas históricas; nenhuma edição manual |
| Normalização | `HEADER_NORMALIZATION_RULE_V1`: A = 276 + 146, B = 2, C = 1 (ver `HEADER_NORMALIZATION_RULE.md`) |
| Targets | legado 3.956 → runtime 3.811 (3.809 no `TARGETS.IDX`). Diferenças: 144 remoções históricas, 3 renumerações oficiais, 2 alíneas antes não indexadas; **0 bloqueantes** (3 exceções revisadas com evidência) |
| Parser | opção nova e opcional `article_case_sensitive` (maiúsculas e título de namespace exatos); índice legado reconstruído **idêntico** |
| TEXT_MAP | `RUNTIME`, 3.386 registros, guarda de tamanho **e** sha256 do runtime, fail closed |
| Camadas | ENTENDA 163 DIRECT + 120 COVERED = 283/283 resolvem; pilotos e ADCT 10 II OK. References: 238/242 targets no runtime; os 4 ausentes são só linhas `HISTORICAL_HIDDEN_BY_DEFAULT` |
| Defeito da fonte oficial | art. 114, `VII I -` (inciso VIII): não corrigido; registrado |
| Cartão | `BACKUP_VERIFIED`: 1.062 arquivos, 24.574.047 B, hash agregado `f00e6d56…9b38`; reverificado ao final (inalterado). CF física: `MATCH_UPDATER_CF_BODY` (`d8469e18…`, 429.242 B) |
| Flash | `PHYSICAL_FLASH_BACKUP_VERIFIED` (`061849a3…6727`) → **FULL_PHYSICAL_ROLLBACK_AVAILABLE** |
| Firmware candidato | aponta para `/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt`, verifica o sha256 (mbedtls), usa TARGETS v3. Flag 0: 989.395 B e 124.452 B de RAM, igual à v7.12.0. Flag 1: 997.319 B e 124.452 B |
| Overlay | 1.288.050 B, incluindo o runtime de 587.134 B |
| Issue de 64 linhas | cartão físico com 41/64 e 20/32: NON_BLOCKING |
| Testes | DEVICE 31/31 · ENTENDA 80/80 · LEGAL_TARGET_ID 47/47 |
| Determinismo | runtime e staging BYTE_IDENTICAL em 2 builds |
