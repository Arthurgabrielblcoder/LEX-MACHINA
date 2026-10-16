# REFERÊNCIAS Nº 4 — Constituição Federal: camada congelada

```
LAYER = REFERENCES_4_CF
STATUS = FROZEN_APPROVED_BASELINE
PHYSICAL_VALIDATION = PASS
PHYSICAL_TESTS = 8/8
WORK_REFERENCE_RELATIONS = 124
WORKS_USED = 56
W_TARGETS = 65
FIRMWARE_LOGIC_CHANGED = NO
FIRMWARE_DATA_CHANGED = YES
FREEZE_DATE = 2026-10-16
BRANCH = cf-references4-finalize
REFERENCE_TAG = lex-device-v1-references4-physical-approved-2026-10-16
FIRMWARE_APP_SHA256 = 6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c
LEX_DEVICE_MANIFEST_SHA256 = 7b8da57d943aef59f6dda55f1eb86484b516f7170da7074e3638949c7ce292fb
PREEXISTING_CORRELATA_TEST_DEBT = 4
```

**Commit final:** o commit apontado pela tag `REFERENCE_TAG`, que contém este documento e a aprovação física. O deploy físico está registrado em `2a3cf60`, e o pacote de bytes aprovado em `453922f` (`GIT_COMMIT` do `LEXV1.VER`).

## Estado aprovado

- **124 WORK_REFERENCE** no aparelho, **56 obras** e **65 targets W**. São os 122 do baseline C3B.2 (RC2 + REFERENCE_EXPANSION_01) mais 2.
- **As duas adições:**
  - **Sicko - S.O.S. Saúde** (`R1A-DOC-001`) → CF art. 196. DOCUMENTÁRIO, 2007, Michael Moore.
  - **Pro Dia Nascer Feliz** (`R1A-DOC-002`) → CF art. 206, I. DOCUMENTÁRIO, 2005, João Jardim.
- **Ano de Pro Dia Nascer Feliz:** 2005 vem do arquivo institucional da Mostra SP. As divergências 2006 e 2007 estão preservadas na proveniência (`ano_decisao`).
- **Lacunas editoriais confirmadas:** CF arts. 98 e 202.
- **Reserva editorial, não dívida:** 199 obras candidatas e 19 obras do registry sem vínculo.

**Evidência:** `REFERENCES_4_CF_PHYSICAL_BASELINE_APPROVED.md` e `R2_PHYSICAL_DEPLOY/`, que inclui `final_physical_verification.json` e `promoted_sys/`.

### Arquivos SD do baseline (`/99_LEX_V1`)

| Arquivo | SHA-256 |
|---|---|
| `20_REFERENCES/REF_PAYLOAD.IDX` | `da49c43b7a21990334a6a1af63fbc605fec7fde195a06a2014776285455006eb` |
| `20_REFERENCES/REF_LOOKUP.IDX` | `efabb245e3beb8b63df33249a7a2e3c178aace02b361d9d344cb348d0fa823a0` |
| `10_TARGETS/CF88_TARGETS.IDX` | `d4e3342b99f5a5efb732eb9b36f786f3eaf5a33ab651500c7ce8a387bfe593f7` |
| `00_SYS/LEX_DEVICE_MANIFEST.json` | `7b8da57d943aef59f6dda55f1eb86484b516f7170da7074e3638949c7ce292fb` |
| `00_SYS/LEXV1.VER` | `edaf6147767ceece3fdd3149b63d79037e8e06a9de8ca71e3589da88a3758125` |

O manifesto completo do cartão (1.142 arquivos) é `R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json`. Ele é a referência de pré-deploy da próxima rodada física.

### Rollback

- **SD:** os bytes C3B.2 estão em `DEVICE_INTEGRATION/backups/references4_r1_physical_deploy/sd_pre/` e em `REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/rollback/`.
- **Firmware:** o app0 anterior (`445fdb7f…`, partição inteira) está em `DEVICE_INTEGRATION/backups/references4_r1_physical_deploy/fw/app0_pre.bin`. O comando está no documento de aprovação.

## Coexistência com CORRELATAS 1

```
CORRELATAS_1_CF = FROZEN (CORRELATA_COVERAGE_AUDIT/CORRELATAS_1_CF_FROZEN.md, C3B.2)
REFERENCES_4_CF = FROZEN
CORRELATAS_1_REGRESSION = PASS
```

As duas camadas coexistem no mesmo baseline físico, sem regressão:

- RELACOES, REL_LOOKUP e EXT_ARTIGOS estão byte-idênticos ao C3B.2;
- o conjunto, os IDs, as rotas e os destinos de CORRELATA não mudaram;
- as flags C não mudaram;
- os testes físicos CF art. 202, § 5º → LC 108/2001, art. 26, e CF art. 37, § 3º, III, sem `1 CORR.`, passaram.

## Dívidas conhecidas (registradas, sem alteração oportunista)

- **`PREEXISTING_CORRELATA_TEST_DEBT = 4`:** quatro testes históricos de reconstrução/hash de Correlatas falham igualmente no checkout limpo do baseline. Não são regressão desta camada.
- **Flag R** (`CF88_TARGETS.IDX`, posição [4]): não foi recalculada, e o firmware não a lê. Há 25 divergências R-only em relação ao gerador, 2 delas desta rodada.
- **Header do sketch:** o sketch versionado em `firmware/` mantém o header de 122 fichas, porque o guard de Correlatas 1 proíbe modificar essa pasta. O app gravado foi compilado com o header RUN5 de 124 fichas, guardado em `LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate/device_candidate/`.
  - Uma reconstrução do firmware a partir de `firmware/` **não** reproduz este baseline sem esse header.
  - Promover o header para o sketch exige uma missão explícita que também trate o guard.

## Significado de "frozen"

"Frozen" NÃO significa que a camada nunca poderá evoluir. Significa:

- esta rodada da camada REFERÊNCIAS Nº 4 está encerrada;
- o estado atual é o baseline físico aprovado;
- nenhuma alteração oportunista deve ser feita enquanto outras camadas são trabalhadas;
- qualquer mudança futura em Referências nº 4 exige uma missão explícita de reabertura;
- alterações legislativas, novos projetos editoriais ou erro comprovado podem justificar a reabertura;
- toda reabertura preserva a trilha histórica (R0, R1, R1A, R2 e esta aprovação) e parte deste baseline.

## Guardrail para as próximas rodadas

- **Trabalhos cobertos:** ENTENDA, Jurisprudência, outras normas, updater, firmware e outras funcionalidades.
- **O que não pode ser alterado incidentalmente:**
  - as linhas `WORK_REFERENCE` de `REF_*`;
  - a flag W do `CF88_TARGETS.IDX`;
  - `WORK_REGISTRY_V3`;
  - os overlays `CF88_WORK_REFERENCE_ADDITIONS*.json`;
  - a tabela de fichas do aparelho.
- **Se uma etapa futura exigir alterar esses bytes ou dados:** PARAR e tratar como reabertura explícita.
- **Regra equivalente para CORRELATAS 1:** continua valendo, conforme o documento de congelamento daquela camada.
