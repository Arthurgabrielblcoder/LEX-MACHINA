# Primeiro baseline físico multinorma — CF/ADCT + Código Civil (CC-J1): congelado

```
BASELINE_ID = MULTINORM_FROZEN_CF315_198_CC29_24   (CF/ADCT = J2I_FROZEN_315_198 · CC2002 = CC_J1_FROZEN_29_24)
STATUS = FROZEN_APPROVED_BASELINE · FREEZE_DATE = 2026-10-18 · BRANCH = cf-jurisprudence-audit
FREEZE_TAG = lex-device-v1-juris-cc-j1-physical-approved-2026-10-18
MULTINORM_FIRMWARE_PHYSICAL_VALIDATION = 25/25 PASS · CC_J1_PHYSICAL_VALIDATION = 36/36 PASS
CF88 + ADCT = 315 relações / 198 targets · CC2002 = 29 relações / 24 targets · TOTAL = 344 / 222 · NORMAS COM JURISPRUDÊNCIA FÍSICA = 2
SHARED_FICHA_CROSS_NORM (Tema 932) = PHYSICALLY_VALIDATED · CC_PENDING_PHYSICAL_RELATIONS = 0 · CC_REJECTED_PHYSICAL_RELATIONS = 0
CORRELATAS_1_CF = FROZEN · REFERENCES_4_CF = FROZEN · ENTENDA_CF_ADCT = FROZEN · J2I_CF_ADCT = FROZEN · FROZEN_LAYERS_MODIFIED = NO
```

As contagens por namespace são as autoritativas; o total combinado (344/222) é só uma soma. Esta missão foi apenas de documentação: não acessou o cartão, não conectou o ESP32 e não gravou firmware.

## 1. Baseline CF/ADCT

- **Rodada:** `J2I_FROZEN_315_198`, inalterado: **CF88 311 / 194 + ADCT 4 / 4 = 315 / 198**.
- **Documento:** `JURISPRUDENCE_AUDIT/JURIS_CF_ADCT_J2I_FROZEN.md`.
- **No aparelho:** a CF continua servida pela camada LEXV1 (`REF_PAYLOAD`, `CF88_TARGETS.IDX`), byte-idêntica ao J2I.
- **Camada normalizada:** a CF também está nela, com as mesmas 315 relações alcançáveis.
- **Ratificado e ainda não instalado:** 9 relações da CF aprovadas pelo usuário ficam **fora** deste baseline físico: Batch10 (6) e Súmulas 203/403 STJ (3). Elas entram numa futura rodada de materialização da CF.

## 2. Baseline CC2002 (CC-J1)

| Item | Valor |
|---|---|
| Relações | **29** |
| Targets com J | **24** |
| Precedentes | **20** (STF: ADI 4815, ADI 6792/7055, Temas 498, 809, 529, 1236, 932; STJ: Súmulas 308, 322, 332, 403, 405, 412, 476, 496, 499, 503, 547, 585, 596) |
| Fichas lógicas | **20**: 19 novas + 1 compartilhada (Tema 932) |
| Ratificação | `CC_J1_RATIFICATION_RECORD.json` (22 propostas aprovadas, 2 pendentes, 6 não aprovadas) |
| Candidato implantado | `CC_J1_MATERIALIZATION_CANDIDATE/` (build `4c0615575e3da8fc`, `SHA256_MANIFEST.json` `71f9eb76a3c8458357d20f2ef697006991347ff109a3cea214015a3c63e95ccc`) |
| Cartão | 1.190 → **1.213** arquivos (+23, aditivo); manifesto `CC_J1_PHYSICAL_DEPLOY/sd_manifest_post_full.json` |
| Validação física | **36/36 PASS** (`CC_J1_PHYSICAL_DEPLOY/CC_J1_PHYSICAL_VALIDATION.json`) |

## 3. Total combinado

**344 relações / 222 targets** em 2 normas: CF (com ADCT) e CC2002. Os namespaces não se sobrepõem.

## 4. Firmware multinorma (fisicamente aprovado)

| Item | Valor |
|---|---|
| SHA-256 do app | **`38c4d71f77b89223860a6643ef9880416cb1f22a8ba933524e6b083442216bb2`** |
| Tamanho | 1.107.504 B |
| Programa / RAM estática | **+5.332 B / +40 B** em relação ao app J2I (1.107.363 B / 126.188 B) |
| app0 livre | 203.216 B (partição 0x140000) |
| Endereço | **0x10000** (APP_ONLY; readback EXATO) |
| FQBN | `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default` |
| Core / opções | esp32:esp32 3.3.11; `-DLEX_DEVICE_V1_ENABLED=1` |
| Fonte | J2I (`juris_types.patch`) + `firmware_multinorm/multinorm.patch` (10 edições) |
| Commit do flash físico | `07d3dc6` (`07d3dc60a543eaab09089f621c0a11588e469a90`) |
| Validação | **25/25 PASS** (`firmware_multinorm/PHYSICAL_FLASH/MULTINORM_PHYSICAL_VALIDATION.json`) |

## 5. Arquitetura multinorma (fisicamente comprovada)

**Motor:**
- namespace de target por norma (`LEGAL_TARGET_ID`; `CC2002` do Catálogo Mestre);
- empacotador genérico (`generic_packager.py`);
- lookup normalizado com **0 chaves duplicadas** e 0 relações perdidas;
- ficha compartilhada entre normas;
- BACK multinorma (29/29 no cartão e 36/36 físico).

**Firmware:**
- identificação da norma pelo arquivo aberto (tabela gerada do Catálogo Mestre, 71 normas; pasta compartilhada exige o nome do arquivo);
- fallback legado da CF (provado no flash: 237/355 sem a camada nova);
- camada `06_NORMALIZADO` preferida quando presente;
- IDs de norma com até 16 bytes (`norma[16]`, confirmado pelos 68 B por lookup no boot);
- alternância CF ↔ CC.

## 6. Empacotador genérico

- **Entrada:** relações normalizadas `{norm, target, precedente}`, um registro por precedente e fichas.
- **Saída:** `06_NORMALIZADO/{JUR_LOOKUP.IDX, JURISPRUDENCIA.IDX, MULTINORM_MANIFEST.json, LAYER.VER}` + fichas novas.
- **Coalescência:** uma linha de lookup por chave; o "primeira ocorrência ganha" do legado deixou de importar.
- **Documento:** `GENERIC_PACKAGER.md`.
- **Diferença documentada:** na CF, o art. 62 artigo + caput compartilham a chave de leitura e a lista é a união (Temas 33 e 1196). Isso foi validado no aparelho.

## 7. Ficha compartilhada: Tema 932

- **Primeiro caso fisicamente aprovado de `ONE_FICHA -> MULTIPLE_NORMS`.**
- **Ficha:** `99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_932.TXT`, sha256 `7bd339337d38caefb5505c8933b395df9a6d129195e9b02060e40f196a10e4d5`.
- **Mesmo arquivo físico para:**
  - **CF art. 7º, XXVIII** (`CF88:ART.7:INC.XXVIII`, baseline J2I);
  - **CC art. 927, parágrafo único** (`CC2002:ART.927:PAR.UNICO`, CC-J1).
- **Integridade:** não foi copiada nem modificada, e o hash físico foi conferido antes do deploy.

## 8. Pendências (fora do baseline; nenhuma relação publicada)

| ID | Precedente | Estado | Reabertura |
|---|---|---|---|
| CCJ1-09 | Tema 1194 | `PENDING_HUMAN_REVIEW` | Evidência oficial de pertinência direta ao art. 206-A |
| CCJ1-30 | Súmula 609/STJ | `PENDING_TEMPORAL_REVALIDATION` | Decisão do STJ depois da Lei 15.040/2024, revisão ou cancelamento, e correspondência com a nova Lei de Seguros |

## 9. Rejeições (não publicadas; `REJECTED_PHYSICAL_RELATIONS = 0`)

| ID | Precedente | Categoria |
|---|---|---|
| CCJ1-08 | Tema 526 | REJECT_NOT_MATERIAL |
| CCJ1-16 | Súmula 371 STJ | REJECT_NOT_MATERIAL |
| CCJ1-19 | Súmula 451 STJ | REJECT_NOT_MATERIAL |
| CCJ1-24 | Súmula 543 STJ | REJECT_NOT_MATERIAL |
| CCJ1-26 | Súmula 550 STJ | REJECT_NOT_MATERIAL |
| CCJ1-28 | Súmula 595 STJ | REJECT_NOT_MATERIAL |

## 10. Rollback (não executado)

**Somente o CC:**
1. Apagar os 23 arquivos criados (`CC_J1_PHYSICAL_DEPLOY/rollback_plan.json`) e a pasta `06_NORMALIZADO`, se ficar vazia.
2. O firmware multinorma permanece; sem a camada normalizada ele usa os índices legados.
3. Resultado: CF/ADCT 315/198, igual ao manifesto J2H (1.190 arquivos).

**Firmware:**
1. Regravar o app J2I `1371e69a0ef3b16773c36e240b166ee99f73d48c2629d11ebf09191701de2b6c` em 0x10000 (`DEVICE_INTEGRATION/backups/j2i_flash_candidate/generic_app.bin`); alternativa bit a bit: `backups/multinorm_physical_flash/app0_pre_flash.bin`.
2. Usar um cartão compatível: o firmware J2I ignora a camada normalizada e não exibe o CC. Para manter o baseline exato, fazer antes o rollback do CC.

## 11. Testes host (2026-10-18)

| Suíte | Resultado |
|---|---|
| Jurisprudência (inclui freeze J2I e gate de provisórios) | 119/119 |
| Motor (CC-J1: ratificação, preflight, deploy e freeze; empacotador; simulação multinorma; adaptador STJ; piloto) | 51/51 |
| Gramática de target (inclui alínea sem inciso) | 93/93 |
| Referências nº 4 | 15/15 |
| Correlatas | 115/120, as mesmas 5 falhas históricas; NEW_REGRESSION = 0 |

O motor de referências é a mesma suíte `LEGAL_TARGET_ID` (93/93).

## 12. Testes físicos

| Rodada | Resultado | Escopo |
|---|---|---|
| J2I | 32/32 PASS | Firmware genérico de classes e tribunais + CF 315/198 |
| Firmware multinorma sobre o cartão J2I | **25/25 PASS** | Regressão CF/ADCT, CC ainda invisível, nenhum vazamento entre normas |
| CC-J1 sobre o firmware multinorma | **36/36 PASS** | 24 targets do CC, negativos (pendentes e rejeitados), Tema 932 nas duas normas, regressões CF/ADCT, Correlatas, Referências nº 4, ENTENDA |

## 13. Regras para expansões futuras

- **CC-J2:** parte explicitamente de `CC_J1_FROZEN_29_24` dentro de `MULTINORM_FROZEN_CF315_198_CC29_24`. Nenhuma relação do CC-J1 pode sumir, trocar de target, trocar de ficha ou mudar silenciosamente. Qualquer mudança exige nova decisão editorial, diff explícito, testes e, quando o cartão muda, nova validação física.
- **CF:** continua regida pelo freeze J2I. As 9 relações ratificadas e não instaladas só entram com materialização e teste físico próprios.
- **Outras normas:** a arquitetura comprovou que recebe novas normas sem patch de firmware. Mesmo assim, nenhuma norma é publicada sem passar por todas as etapas:
  1. descoberta;
  2. auditoria;
  3. ratificação;
  4. preflight de materialização;
  5. deploy aditivo;
  6. teste físico.
- **Camadas congeladas:** Correlatas 1, Referências nº 4, ENTENDA e J2I não podem ser alteradas incidentalmente. Se for necessário, parar e tratar como reabertura explícita.

## Commits de referência

| Commit | Etapa |
|---|---|
| `399d9b4` | Freeze J2I (CF/ADCT 315/198), tag `lex-device-v1-juris-j2i-physical-approved-2026-10-18` |
| `e217555` | Empacotador genérico e camada normalizada |
| `f84d267` | CC-J1: propostas |
| `a927384` | Dossiê de ratificação |
| `4525e04` | Ratificação humana do CC-J1 |
| `a193dd8` | Preflight de materialização (candidato) |
| `07d3dc6` | Flash físico do firmware multinorma |
| `2d53e6c` | Deploy do CC-J1 no microSD + registro 25/25 |
| tag `FREEZE_TAG` | Este freeze (registro 36/36) |
