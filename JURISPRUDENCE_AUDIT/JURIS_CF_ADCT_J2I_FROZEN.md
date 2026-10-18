# JURISPRUDÊNCIA CF+ADCT — baseline físico congelado J2I (315/198)

```
LAYER = JURIS_CF_ADCT
BASELINE_ID = J2I_FROZEN_315_198
STATUS = FROZEN_APPROVED_BASELINE
J2I_PHYSICAL_VALIDATION = 32/32 PASS
PHYSICAL_RELATIONS = 315
PHYSICAL_TARGETS = 198
GENERIC_FIRMWARE_PHYSICAL_APPROVAL = YES
FIRMWARE_APP_SHA256 = 1371e69a0ef3b16773c36e240b166ee99f73d48c2629d11ebf09191701de2b6c
CARD_BUILD_ID = def71b31a64c2a54
LEX_DEVICE_MANIFEST_SHA256 = d8bb3278bd282d96ffa84a22d90a7e01e7ab976e445c7f3211197b4f6ad0643a
CORRELATAS_1_CF = FROZEN · REFERENCES_4_CF = FROZEN · ENTENDA_CF_ADCT = FROZEN · FROZEN_LAYERS_MODIFIED = NO
STJ_SUMULA_403 = UNRESOLVED_EXTERNAL (não publicada)
FREEZE_DATE = 2026-10-18
BRANCH = cf-jurisprudence-audit
FREEZE_TAG = lex-device-v1-juris-j2i-physical-approved-2026-10-18
NEXT_RESEARCH_BATCH = BATCH10 (NÃO iniciado)
```

**Commit final:** o commit apontado por `FREEZE_TAG`, que contém este documento e o registro `J2I_PHYSICAL_FLASH/J2I_PHYSICAL_VALIDATION.json`. **Reconciliação pós-freeze (J2J.1, `METADATA_ONLY_POST_FREEZE_RECONCILIATION`):** um commit posterior à tag corrigiu só os metadados editoriais dos provisórios (seção 6), este documento e os testes. A tag física não foi movida. O baseline físico, o cartão, o firmware, os índices, as fichas e os candidatos não mudaram (seção 10).

A missão de freeze (J2J) foi só documental: não acessou o microSD, não conectou o ESP32 e não gravou firmware. Nenhum conteúdo jurídico foi alterado e nenhuma relação foi acrescentada.

## 1. Baseline físico

| Item | Valor |
|---|---|
| Cartão | Candidato B, pacote `J2H_CANDIDATE_B_OVER_A`, instalado pela J2H (`13b3b7f`) sobre o Candidato A aprovado |
| Firmware | genérico multiclasse/multitribunal, gravado no app0 pela J2I (`f402bfd`) |
| Validação | teste humano J2I 32/32 PASS, informado pelo usuário em 2026-10-18 |
| Substitui | J2G, Candidato A 299/186 com o firmware `6e329c91…` (21/21 PASS em 2026-10-17) |

## 2. Contagens

| Contagem | Valor |
|---|---|
| Vínculos de jurisprudência (JURIS_RELATIONS) | **315** |
| Targets com jurisprudência (JURIS_TARGETS) | **198** |
| Linhas do índice legado `JURISPRUDENCIA.IDX` | 356 = 340 do A + 16 do grupo B (1 cabeçalho + 355 registros) |
| Linhas de `JUR_LOOKUP.IDX` | 238 = 222 do A + 16 (1 cabeçalho + 237 lookups; limite do cache 4096) |
| Registros legados (= soma das quantidades do lookup) | 355 |
| Arquivos no cartão | 1190 |
| Vínculos do A preservados | 299/299 |
| Máximo por target | 10 jurisprudências (limite 32); 10 itens visíveis (limite 40) |

**Tipos no índice legado (tipo/tribunal):** repercussao_geral/STF 296, adi/STF 27, sumula_vinculante/STF 16, adpf/STF 4, ms/STF 3, hc/STF 2, inq/STF 2, ai/STF 1, ap/STF 1, rcl/STF 1, sumula/STF 1, sumula/TSE 1.

### Estado do cartão (evidência J2H/J2I; cartão NÃO acessado nesta missão)

| Item | Valor |
|---|---|
| Manifesto completo do cartão | `J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json` (1190 entradas; sha256 do arquivo `2c53827f26f29ce5119b316a9a12c78ddc9add4fe816bcbe1579a909b0e313a5`) |
| Manifesto do pacote | `J2H_CANDIDATE_B_OVER_A/J2H_PACKAGE_MANIFEST.json` (sha256 `0c1817d514c8a3f71f39618ecfdc4fa7c5ffb9eed6c2ea7a63204739b5d69971`) |
| `BUILD_ID` (`LEXV1.VER`) | `def71b31a64c2a54` |
| `GIT_COMMIT` (`LEXV1.VER`) | `64564d6d667440208a7f71dbf1150c262524e017` |
| `REFERENCE_ENGINE` | `cf-reference-engine-run11-juris-j2f-b` |
| ENTENDA no `LEXV1.VER` | 810, `CF88_ADCT_FULL_HUMAN_APPROVED_T1` |
| Flags alteradas pela J2H | E=0, C=0, **J=12**, W=0, R=0, X=0 (J = jurisprudência visível) |
| Flag R | `R_FLAG_KNOWN_DIVERGENCE = 76`, só registro: nenhuma flag R mudou e o firmware não lê R |

**Arquivos de dados do baseline:**

| Arquivo | Bytes | SHA-256 |
|---|---:|---|
| `99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX` | 64695 | `483656791f1078389f1134ad8dcb55c291637c34b304289129f2137fb9c3e801` |
| `99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX` | 4996 | `396e1e34374ba22ece7e5e7b04ec98d4781fbeade5b2e9e3a374d27b8d6f3a58` |
| `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | 71064 | `b16f1f81c484e64a349a264f312d133be67b1a12d7716fa312ff02a5e9d757e1` |
| `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | 7434 | `2ea28d50dec6b2abea65dfe9fe16e47654557725b8a6ffd6a58ea5bcbff8c394` |
| `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | 165466 | `fe233de1af79d64552f4f1ee40d37f5498e06e26f015fdaa6bcee0f0644458a4` |
| `99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | 7624 | `d8bb3278bd282d96ffa84a22d90a7e01e7ab976e445c7f3211197b4f6ad0643a` |
| `99_LEX_V1/00_SYS/LEXV1.VER` | 598 | `ed258cd30f2f6b40bd0b674c251b83d6b1ad61ceb3441bdafd325b31edccf041` |

**Fichas acrescentadas pelo grupo B (15, em `99_JURISPRUDENCIA_V2/03_CONTEUDO/`):**

| Ficha | SHA-256 |
|---|---|
| `STF_ADPF_378.TXT` | `e4983a47398b469f9343da7a9e2ba533395e4f80318bca60691db33e55d24f51` |
| `STF_ADPF_672.TXT` | `d5f686f19978fd86c0a335ebed71a4b709d14b6972419af615d4fae89d6d0679` |
| `STF_ADPF_964.TXT` | `3e424bc5e0d09fbd2899f5c47153d06810ee25af275eb9fe5b1fc422c52bc301` |
| `STF_AI_343461.TXT` | `4543027cafa8d7b2c9d7ffd6984310336d3d05b4d31a6e5204de1feac678bc0f` |
| `STF_AP_694.TXT` | `f99b0fac51419f7e54df2834443d219f90703efdf3251b8e0fd2dc1d46f5c764` |
| `STF_HC_232627.TXT` | `b2d0ff8a19556c4532055653221b62e3328b0462db06b62555263c6aa21cc1a6` |
| `STF_HC_70648.TXT` | `6c22e0b51e15b719be17086ca7887a8d037b5531799e3555743c9d4dfac04c28` |
| `STF_INQ_4781.TXT` | `0a4751c14ba939a21bae04ab78bc46f9ead74798d48ccec2b738fe28890de772` |
| `STF_INQ_672.TXT` | `65e98eaeedca989935194d987c9cfab9719c5f649a5574675ba6f4298525a7bc` |
| `STF_MS_21564.TXT` | `9adaafe0f24f77fc4ca6d53023e080b493978db6cfcf106e5c781df446635645` |
| `STF_MS_21689.TXT` | `93ff54957f5b5184a0678bb83ecde249a1132e117eb2538abbe26dd962c46c1f` |
| `STF_MS_27931.TXT` | `ce353ce46bc83ef5f7be7198209a8834f27e24756cbed38de9134d4d664182eb` |
| `STF_RCL_84738.TXT` | `55a1366d5c4acac248dfa45beba67f64a6edd0a9cd3f2654f895c205fffa4cb2` |
| `STF_SUMULA_702.TXT` | `eb5c0a02fd63ace9c6b22241333f7b0110e775d712f142dc161e5220a866e891` |
| `TSE_SUMULA_9.TXT` | `7c0e74fa16221a4cf2a3867cc1fd2925d6964f3c70d8b58fb48e6359525e8c76` |

O hash de cada um dos 1190 arquivos está no manifesto completo. A validação pós-escrita da J2H (`J2H_PHYSICAL_DEPLOY/physical_validation.json`) deu SD_HASHES = PASS, MANIFEST_VS_SD = PASS e UNEXPECTED_SD_CHANGES = 0. A J2I não escreveu no cartão (ele ficou fora do aparelho durante o flash).

## 3. Firmware

### Baseline aprovado (genérico multiclasse/multitribunal)

| Item | Valor |
|---|---|
| SHA-256 do app | **`1371e69a0ef3b16773c36e240b166ee99f73d48c2629d11ebf09191701de2b6c`** |
| Tamanho do app | 1.102.176 B (programa 1.102.031 B; RAM estática 126.148 B) |
| Partição app0 | 1.310.720 B (0x140000); livres 208.544 B |
| Endereço físico | **`0x10000`** (app0); escopo APP_ONLY |
| Readback pós-flash | EXACT (primeiros 1.102.176 B do app0 = `1371e69a…`); app0 inteiro pós-flash `8bab9de537a091cfdffdf3d494749809e1592cc2184e329e4ea676b048355833` |
| Delta em relação ao `6e329c91…` | programa +1.040 B; RAM estática +0 B |
| FQBN | `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default` |
| Core / ferramenta | esp32:esp32 **3.3.11**; arduino-cli 1.5.1 |
| Flags de build | `--build-property compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1` |
| PSRAM / flash | PSRAM OPI (8 MB embutida, AP_3v3); FlashSize do build 4M; flash física detectada 16 MB (0x68/0x4018); `--flash-mode keep --flash-freq keep --flash-size keep` na gravação |
| Tabela de partições | `default`; sha256 `148b959cbff1c38aa8e1d5c0ba9d612c54997b945e56a63f41223eef650653a1` (inalterada); nvs 0x9000, otadata 0xe000, app0 0x10000, app1 0x150000, spiffs 0x290000, coredump 0x3f0000 |
| otadata | `f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0` (inalterada; boot pelo app0) |
| Fonte | `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE` + `JURIS_TYPE_PROTOTYPE/juris_types.patch` (9 edições) |
| Binário congelado | `DEVICE_INTEGRATION/backups/j2i_flash_candidate/generic_app.bin` (fora do Git; hash reconferido nesta missão) |
| Banner no boot | `LEX MACHINA V7.12.0 JURIS CF EXPANDIDA` |
| Chip | ESP32-S3 (QFN56) rev v0.2, MAC e0:72:a1:f4:fd:28, porta COM3 (CH343 1A86:55D3) |

### Rollback histórico (NÃO executado)

| Item | Valor |
|---|---|
| Firmware anterior (aprovado até J2G) | app `6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c` (1.101.136 B, R2) |
| Cópia do app anterior | `DEVICE_INTEGRATION/backups/j2i_flash_candidate/current_approved_app_6e329c91.bin` (hash reconferido nesta missão) |
| app0 inteiro antes do flash | `DEVICE_INTEGRATION/backups/j2i_physical_flash/app0_pre_flash.bin` (`dde8fa2990353409cae44f60ffbda0d6c13d4ba7af352779d081068b2d3a673d`, lido 2 vezes) |
| Outras leituras PRE | `partitions_pre.bin`, `otadata_pre.bin`, `nvs_pre.bin` (`2ad43c13d08634faec16fa4c8f36f4bcfbde61c562cf9159d019e08cf73036ea`) |
| Imagem anterior ao R2 | `DEVICE_INTEGRATION/backups/references4_r1_physical_deploy/fw/app0_pre.bin` |

Nenhum backup foi apagado.

## 4. Tipos suportados

**Fisicamente validados neste baseline** (rótulo exibido, ficha aberta e, nos itens 2 a 13, BACK testado):

| Tipo | Exemplo testado |
|---|---|
| RG/Tema (STF) | Temas 793, 935, 1093, 558, 367, 387, 950, 371 |
| SV (STF) | SV 46 |
| ADI (STF) | ADI 7369, 7047/7064, 7064, 5017 (CAUTELAR), 7697 (CAUTELAR) |
| HC (STF) | HC 232627, HC 70648 |
| MS (STF) | MS 21689, MS 21564, MS 27931 |
| AP (STF) | AP 694 |
| AI (STF) | AI 343461 |
| Inq (STF) | Inq 4781, Inq 672 |
| Rcl (STF) | Rcl 84738 (PROVISÓRIA) |
| ADPF (STF) | ADPF 378 (CAUTELAR) em dois targets, ADPF 964, ADPF 672 |
| Súmula TSE | Súmula 9 TSE |
| Súmula STF (comum) | Súmula 702 STF |

**Arquiteturalmente suportados, SEM precedente físico testado** (presentes nas tabelas do firmware genérico / `juris_types.py`, mas sem nenhum registro no cartão):

- classes: RHC, RMS, MI, Pet, ADO, RE, ARE, Ext (e o alias `habeas_corpus` → HC);
- rótulos legados: ADC, ACORDAO, IAC, SIRDR, REPETITIVO STJ;
- tribunais: STJ, TST e STM (só STF e TSE têm registro no cartão); em particular, nenhuma súmula do STJ foi publicada.

Esses tipos não têm cobertura física. A primeira publicação de qualquer um deles exige teste físico próprio.

## 5. Validação física

`J2I_PHYSICAL_VALIDATION = 32/32 PASS` (`J2I_PHYSICAL_FLASH/J2I_PHYSICAL_VALIDATION.json`):

- todos os 32 itens do checklist da seção 8 de `J2I_GENERIC_FIRMWARE_FLASH_REPORT.md` passaram;
- nenhum item falhou;
- nenhum rollback foi necessário.

Cobertura: boot com o cartão B; HC, MS, AP, AI, Inq, Rcl, ADPF, Súmula TSE e Súmula STF; BACK; ausência de `OUTRO`; regressões do Candidato A (7 itens); regressões da base antiga (3 itens); Correlatas, Referências nº 4 e ENTENDA; ausência da Súmula 403/STJ.

## 6. Provisórios (continuam provisórios)

Registro consolidado: `J2_PROVISIONAL_REGISTRY.json`, gerado por `build_j2_provisional_registry.py`. Os quatro itens estão no cartão e continuam juridicamente **provisórios**, sujeitos a revalidação temporal. **Não** foram convertidos em definitivos.

**Estado jurídico/processual (inalterado):**

| Precedente | Estado | Última verificação | Prazo (máx.) | Gatilho |
|---|---|---|---|---|
| ADI 7697 (CAUTELAR) | MERIT_PENDING | 2026-10-16 | 2027-01-14 (90 dias) | JULGAMENTO_DE_MERITO |
| ADI 5017 (CAUTELAR) | REFERENDUM_PENDING | 2026-10-17 | 2027-01-15 (90 dias) | REFERENDO_OU_JULGAMENTO_DE_MERITO |
| ADPF 378 (CAUTELAR) | CAUTIONARY_ONLY | 2026-10-17 | 2027-04-15 (180 dias) | JULGAMENTO_DE_MERITO_OU_EXTINCAO |
| Rcl 84738 (PROVISÓRIA) | LEADING_CASE_PENDING | 2026-10-17 | 2027-01-15 (90 dias) | JULGAMENTO_DO_TEMA_1147_OU_PLENARIO |

**Estado editorial/físico no LEX MACHINA** (reconciliado na J2J.1):

| Precedente | `editorial_state` | Ratificação humana | Instalado em | `physical_state` | Validações físicas |
|---|---|---|---|---|---|
| ADI 7697 | HUMAN_APPROVED | ARTHUR, 2026-10-16 (Batch01, `J2B_REPORT.md`) | J2C | PHYSICALLY_APPROVED | J2C 12/12; J2G 21/21; J2I 32/32 |
| ADI 5017 | HUMAN_APPROVED | ARTHUR, 2026-10-17 (`J2_RATIFICATION_RECORD_03_09.json`) | J2G | PHYSICALLY_APPROVED | J2G 21/21; J2I 32/32 |
| ADPF 378 | HUMAN_APPROVED | ARTHUR, 2026-10-17 (`J2_RATIFICATION_RECORD_03_09.json`) | J2H | PHYSICALLY_APPROVED | J2I 32/32 |
| Rcl 84738 | HUMAN_APPROVED | ARTHUR, 2026-10-17 (`J2_RATIFICATION_RECORD_03_09.json`) | J2H | PHYSICALLY_APPROVED | J2I 32/32 |

Em resumo: decisão humana ratificada, publicada e aprovada fisicamente, e o item permanece provisório e sujeito a revalidação. Nenhum item aprovado fisicamente consta como aguardando ratificação.

- **Gate obrigatório** antes de qualquer novo deploy ou ratificação material: `check_j2b_provisional.py --registry J2_PROVISIONAL_REGISTRY.json --as-of <data>`.
- **Fail closed:** item vencido ou com gatilho disparado volta a pendente até ser revisto (`on_trigger` igual para os quatro).
- **Campos do registro (J2J.1, só metadados, compatível com os consumidores):**
  - o estado jurídico continua nos campos `state`, `status_processual`, `last_verified_on`, `max_age_days`, `deadline` e `trigger`, mais o novo `legal_nature = PROVISIONAL`;
  - o estado editorial/físico foi separado em campos próprios: `editorial_state`, `ratification`, `installed_by`, `physical_state`, `physical_validations` e `physical_baseline`;
  - `publication_state` foi mantido e agora diz `PHYSICALLY_APPROVED (…)`;
  - o código da recomendação original dos lotes ficou em `decision`.
- **Correção desta seção:** a nota anterior, de que ADI 5017, ADPF 378 e Rcl 84738 constavam como aguardando ratificação, ficou obsoleta. Ela também atribuía a instalação da ADI 5017 à J2H; o correto é J2G.

## 7. Pendências

- **`STJ_SUMULA_403 = UNRESOLVED_EXTERNAL`.** Motivo: bloqueio anti-robô nas fontes oficiais acessíveis durante a auditoria (`STJ_SUMULA403_ATTEMPTS.md`). Não publicada, sem ficha, sem vínculo. Item 32 do teste físico confirmou a ausência.
- **Backlog não pesquisado:** segue o `J2_RECONCILIATION.json`. O próximo lote de pesquisa é o **Batch10**, que NÃO foi iniciado.
- **Flag R:** divergência conhecida de 76 targets, só registro (o firmware não lê R).
- **Correlatas:** 5 testes históricos falham da mesma forma (seção 10); não são regressão desta camada.

## 8. Rollback

Regra: **firmware antigo e cartão B nunca juntos.** Para voltar ao J2G (299/186), reverta os dois.

1. **Firmware:** `esptool --chip esp32s3 -p COM3 -b 460800 --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/backups/j2i_flash_candidate/current_approved_app_6e329c91.bin`; readback: os primeiros 1.101.136 B devem dar `6e329c91…`. Alternativa bit a bit: gravar `app0_pre_flash.bin` em 0x10000.
2. **Cartão (B → A):** apagar as 15 fichas de `ROLLBACK_DELETE_FILES` (`J2H_PHYSICAL_DEPLOY/sd_pre_backup_manifest.json`); restaurar os 7 arquivos de `DEVICE_INTEGRATION/backups/juris_j2h_physical_deploy/sd_pre/` (cópia também em `J2H_CANDIDATE_B_OVER_A/rollback/`); conferir com `J2G_PHYSICAL_DEPLOY/sd_manifest_post_full.json`.

Rollbacks anteriores (J2C 261/160 e antes) continuam documentados nos respectivos relatórios.

## 9. Commits relevantes

| Commit | Etapa |
|---|---|
| `64564d6` | Ratificação dos Batches 03–09 (54 + 1 UNRESOLVED), reconciliação e normalização J2F; `GIT_COMMIT` do `LEXV1.VER` |
| `cbfbef9` | Candidatos host-only J2F A (299/186) e B (315/198) |
| `d3f1952` | Bytes dos pacotes J2F preservados (`-text`) |
| `f6c362d` | J2G: Candidato A no microSD (299/186) |
| `13b3b7f` | J2H: Candidato B sobre A no microSD (315/198), sem flash |
| `f402bfd` | J2I: firmware genérico no app0 (0x10000), readback exato |
| `f384a76` | Arquitetura extensível de tipos + protótipo de firmware genérico |
| `aa8cdd3`, `f80d6b3` | `firmware/` reconstrói o app aprovado; guards com sha fixado |
| `45a0084` | Freeze de Referências nº 4 (tag `lex-device-v1-references4-physical-approved-2026-10-16`), ancestral deste baseline |
| `399d9b4` (tag `FREEZE_TAG`) | Este freeze (J2J) |
| commit posterior à tag | J2J.1: reconciliação de metadados dos provisórios (`METADATA_ONLY_POST_FREEZE_RECONCILIATION`) |

## 10. Testes host (J2J, 2026-10-18)

| Suíte | Resultado |
|---|---|
| Jurisprudência (`JURISPRUDENCE_AUDIT/tests`, inclui `test_j2j_freeze`) | 108/108 OK no freeze J2J; 110/110 OK após a J2J.1 (+2 testes: estado editorial reconciliado e gate temporal) |
| Motor de referências (`LEGAL_TARGET_ID/tests`) | 90/90 OK |
| Referências nº 4 (`REFERENCE_COVERAGE_AUDIT/tests`) | 15/15 OK |
| Correlatas (`CORRELATA_COVERAGE_AUDIT/tests`, por arquivo: 12 suítes, 120 testes) | 115/120. As 5 falhas são as históricas, nome a nome: c0 `test_committed_artifacts_are_the_build`; c3a1 `test_15_run4_and_package_deterministic`; c3a_engine `test_16_operational_files_untouched`; c3b1 `test_reproducible`; c3b2 `test_c3b2_package_reproducible_and_equal_device_bytes`. NEW_REGRESSION = 0 |

Antes da criação de `test_j2j_freeze.py`, a suíte de Jurisprudência deu 102/102 OK. Nenhum candidato foi reconstruído ou alterado; os testes não deixaram mudança em arquivo rastreado.

**Prova de metadata-only da J2J.1:** comparei o sha256 de 330 artefatos físicos autoritativos antes e depois da reconciliação. São os arquivos rastreados de `J2H_CANDIDATE_B_OVER_A`, `J2H_PHYSICAL_DEPLOY`, `J2I_PHYSICAL_FLASH`, `J2G_PHYSICAL_DEPLOY`, `J2F_CANDIDATES_HOST_ONLY`, `JURIS_TYPE_PROTOTYPE`, `firmware/` e `LEGAL_TARGET_ID/derived`, mais os binários de backup da J2I. Todos são idênticos. Arquivos alterados: só `J2_PROVISIONAL_REGISTRY.json`, o gerador dele, este documento e `test_j2j_freeze.py`.

```
DEVICE_DATA_CHANGED = NO · FIRMWARE_CHANGED = NO · SD_PACKAGE_CHANGED = NO
JURIS_RELATIONS = 315 · JURIS_TARGETS = 198 · PHYSICAL_BASELINE_CHANGED = NO
```

## 11. Testes físicos

| Rodada | Resultado | Baseline |
|---|---|---|
| J2C | aprovado | 261/160 |
| J2G (Candidato A, firmware `6e329c91…`) | 21/21 PASS | 299/186 |
| **J2I (Candidato B, firmware genérico `1371e69a…`)** | **32/32 PASS** | **315/198** |

Boot sem cartão na J2I: `EXPECTED_SD_ERROR`, sem panic nem reset em loop (`J2I_PHYSICAL_FLASH/07_boot_without_sd.json`).

## Camadas congeladas (inalteradas)

```
CORRELATAS_1_CF = FROZEN   (CORRELATA_COVERAGE_AUDIT/CORRELATAS_1_CF_FROZEN.md)
REFERENCES_4_CF = FROZEN   (REFERENCE_COVERAGE_AUDIT/REFERENCES_4_CF_FROZEN.md)
ENTENDA_CF_ADCT = FROZEN   (ENTENDA_ENGINE/ENTENDA_CF_ADCT_FROZEN.md)
FROZEN_LAYERS_MODIFIED = NO
```

Evidência:

- a checagem semântica da J2H (`J2H_PHYSICAL_DEPLOY/semantic_check.json`) deu CORRELATAS_CHANGED = NO, REFERENCES4_CHANGED = NO, ENTENDA_CHANGED = NO e flags C = 0, W = 0, E = 0;
- nesta missão, as linhas `WORK_REFERENCE` (124) e `CORRELATA` do `REF_PAYLOAD.IDX` do Candidato B foram comparadas com as do Candidato A (`J2H_CANDIDATE_B_OVER_A/rollback/`): idênticas (sha256 das linhas `54e45532…` e `f6936a77…`, respectivamente);
- nenhum arquivo de `99_RELATIONS_V1` nem de ENTENDA está no diff da J2H (7 substituídos, todos de índice/sistema; 15 fichas criadas);
- os itens físicos 29, 30 e 31 passaram.

## 12. Regra para futuras alterações

- **Nenhuma mudança de jurisprudência pode alterar silenciosamente este baseline.**
- **Toda nova rodada parte explicitamente de `J2I_FROZEN_315_198`:** o pré-deploy deve reconferir o cartão contra `J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json` (1190 arquivos) e o app0 contra `1371e69a…`.
- **Escopo:** acréscimos (Batch10 e seguintes), correções e remoções só por missão explícita, com candidato host-only, auditoria de isolamento, ratificação do usuário, gate de provisórios, deploy controlado e novo teste físico. O baseline seguinte recebe um novo freeze.
- **Preservação:** os 315 vínculos atuais, as fichas e as decisões editoriais (ADPF 964 sozinha; ADPF 378 com o mesmo registro nos dois targets; MS 21564 e ADPF 378 separados no art. 86; Súmula 702 STF e Súmula 9 TSE separadas por tribunal) só mudam com justificativa registrada.
- **Firmware:** qualquer novo flash parte do app `1371e69a…` como baseline e mantém rollback para ele.
- **Camadas congeladas:** se uma rodada de jurisprudência exigir alterar bytes ou dados de Correlatas, Referências nº 4 ou ENTENDA, PARAR e tratar como reabertura explícita daquela camada.
- **Súmula 403/STJ:** só pode ser publicada depois de resolvida em fonte oficial, sem contornar bloqueio anti-robô.
- **"Frozen"** não significa imutável para sempre. Significa que esta rodada está encerrada e que o estado acima é o ponto de partida obrigatório.
