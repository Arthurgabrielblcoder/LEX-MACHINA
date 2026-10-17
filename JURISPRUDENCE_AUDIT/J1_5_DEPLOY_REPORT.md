# JURISPRUDÊNCIA — CF: J1.5, deploy controlado do SD (candidato J1.4)

```
DATE = 2026-10-16 · BRANCH = cf-jurisprudence-audit (HEAD 8a072cd no deploy; contém J0, J1, J1.1, J1.2, J1.3 e J1.4)
HOST_GATES = PASS · PREDEPLOY_SD_BASELINE = PASS · SD_ROLLBACK_READY = YES
EXPECTED_SD_FILES_CHANGED = 5 · SD_FILES_WRITTEN = 5 · UNEXPECTED_FILES_CHANGED = 0
SD_CANDIDATE_HASHES = PASS · MANIFEST_VS_SD = PASS · OTHER_SD_FILES_CHANGED = 0
JURIS_RELATIONS_INSTALLED = 256 · JURIS_TARGETS_INSTALLED = 156 · J_FLAG_CHANGES = 1 (CF art. 100, § 1º)
CORRELATA_RELATIONS_CHANGED = 0 · WORK_REFERENCE_RELATIONS_CHANGED = 0 · ENTENDA_DATA_CHANGED = NO
R_FLAG_KNOWN_DIVERGENCE = 38 (não corrigida; o firmware não lê R)
FIRMWARE_FLASH = NO · FIRMWARE_CHANGED = NO (app 6e329c91… mantido)
STATUS = AGUARDANDO TESTE FÍSICO · JURISPRUDENCE_FROZEN = NO · sem promoção de baseline · J2 não iniciada
```

**Ferramentas:**

- `JURISPRUDENCE_AUDIT/deploy_j1_4_sd.py pre|copy|verify`: mesmo fluxo da J1.2. Grava num arquivo temporário `.LEX_NEW`, faz `fsync`, substitui com `os.replace`, relê e confere o sha256.
- `JURISPRUDENCE_AUDIT/semantic_check_j1_4_sd.py`: leitura apenas.

**Evidências:**

- **Versionadas** em `J1_5_PHYSICAL_DEPLOY/`:
  - `physical_pre.json`;
  - `sd_pre_backup_manifest.json`;
  - `semantic_pre_candidate_vs_card.json`;
  - `physical_validation.json`;
  - `sd_manifest_post_full.json`;
  - `semantic_check.json`.
- **Backup PRE do cartão** (fora do Git): `DEVICE_INTEGRATION/backups/juris_j1_4_physical_deploy/sd_pre/`.

## Gates

| Gate | Resultado |
|---|---|
| **Host** | `JURIS_TESTS` 25/25 · `LEGAL_TARGET_ID` 90/90 · `REFERENCES_4` 15/15 · isolamento J1.4 `UP_TO_DATE` e PASS · RUN7 reproduzível · pacote reconstruído no commit `7786bbc` byte-idêntico ao versionado |
| **Pacote** | `J1_4_CANDIDATE_HOST_ONLY/J1_4_PACKAGE_MANIFEST.json`: `BUILD_ID cbed709a40356681` confirmado; 5 candidatos e 5 rollback batem com o manifesto |
| **Cartão (pré)** | D: inteiro (1.142 arquivos) idêntico ao manifesto físico pós-J1.2 (`J1_2_PHYSICAL_DEPLOY/sd_manifest_post_full.json`). `LEXV1.VER` = `c4046eaca3ef18a2` / `cf-reference-engine-run6-juris-j1` |
| **Rollback** | `J1_4_CANDIDATE_HOST_ONLY/rollback/` = backup `sd_pre/` = bytes lidos do cartão, 5/5 |
| **Invariantes (pré)** | Candidato × cartão: só a Jurisprudência muda. Saem os 4 ratificados, entram as 3 realocações. Flags E 0 · C 0 · J 1 · W 0 · R 0 · X 0; R = 38 |

**Hashes PRE (cartão = rollback):**

| Arquivo | Bytes | sha256 |
|---|---:|---|
| REF_PAYLOAD | 62.528 | `1f87d1af57f1ecd4171212c23414c7e8540099ef20d62607a49a255746efc5e3` |
| REF_LOOKUP | 6.476 | `53ed70579c5f4a8f6182f19f3020b231aa3af34f11045f159321c0eb0995664c` |
| CF88_TARGETS | 165.466 | `8eb99cd5d03b058437d4e024ea68dbb0a45daa37f56d69de7e27f81ad8b7dc1e` |
| LEX_DEVICE_MANIFEST | 7.644 | `d6d5fc360a2878573c3f0ce642c8be48cd86b4a1cb0ca51d8e1b375b78f2fcf6` |
| LEXV1.VER | 594 | `9366524ec7a54f37175de76e6201a944e9c83b142ecfbba3c8096d0cd1c6acd0` |

## Arquivos escritos no cartão (sha256 pós-deploy, lidos de D:)

| Arquivo | Bytes | SHA-256 |
|---|---:|---|
| `/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | 62.364 | `d07cb0764735a56d9f7eecb915a56ed083d35e662cd47164293e388d048f72e1` |
| `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | 6.450 | `66bea5f0ddddb4c17ef4c25e587fcb95cc705f955b7620c6c31ea2a072bcfe38` |
| `/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | 165.466 | `75d483c081c23e5fea981f516abae510af0a8104c4fa9e3e59ca52a8bbb9d213` |
| `/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | 7.641 | `28b412d163aaccc183c0751e026debfcad2f0a40248e462135ea161750d7cf4e` |
| `/99_LEX_V1/00_SYS/LEXV1.VER` | 596 | `71eb25ce67c461c7b573976f1f299065f77beaccb5d3e5224c5a3f11131a1af8` |

**Novo `LEXV1.VER`:**

- `BUILD_ID cbed709a40356681`;
- `GIT_COMMIT 7786bbc`;
- `REFERENCE_ENGINE cf-reference-engine-run7-juris-j1-4`;
- `ENTENDA_COUNT 810`.

## Verificação pós-deploy (bytes do cartão × backup PRE)

| Item | Resultado |
|---|---|
| Arquivos alterados | exatamente os 5; 0 adicionados ou removidos; 1.142 → 1.142 |
| Manifesto × cartão | PASS (10 entradas) |
| RELACOES / REL_LOOKUP / EXT_ARTIGOS | byte-idênticos |
| ENTENDA_LOOKUP / ENTENDA_PAYLOAD | byte-idênticos |
| `JURISPRUDENCIA.IDX` legado (`/99_JURISPRUDENCIA_V2`) | byte-idêntico; as 3 chaves realocadas estão presentes |
| Jurisprudência instalada | **256** vínculos visíveis em **156** targets |
| CF art. 100, § 1º | sem jurisprudência; flag J apagada (única mudança de flag) |
| CF art. 100, § 5º | SV 17, Temas 147, 1037 e 1335 |
| CF art. 40 | Temas 594 e 1254 |
| CF art. 40, § 4º / § 5º | Temas 727, 888 e 942 / Tema 965 (sem o Tema 594) |
| CF art. 16 | Temas 367 e 387 |

O simulador do aparelho, lendo direto de D:, confirmou os mesmos resultados. Confirmou também:

- art. 37, XI com 10 temas (inclui o Tema 1167);
- art. 1º sem jurisprudência;
- art. 202, § 5º → LC 108/2001;
- art. 196 → Sicko.

## Teste físico J1.5 (o usuário executa)

Remova o cartão com segurança, recoloque no LEX MACHINA e ligue normalmente.

| # | Ação | Esperado |
|---|---|---|
| 1 | Boot | Normal, sem erro de versão ou manifesto |
| 2 | CF art. 100, § 1º | `2 JURIS.` **não** aparece |
| 3 | CF art. 100, § 5º → `2 JURIS.` | SV 17, Tema 147, Tema 1037 e Tema 1335; abrir a SV 17 e o Tema 147; as teses abrem |
| 4 | CF art. 40 → `2 JURIS.` | Tema 594 aparece (com o Tema 1254); a tese abre. A nota temporal não aparece na tela, e isso é esperado |
| 5 | CF art. 40, § 4º | Tema 594 **não** aparece; Temas 727, 888 e 942 continuam |
| 6 | CF art. 40, § 5º | Tema 594 **não** aparece; Tema 965 continua |
| 7 | CF art. 16 → `2 JURIS.` | Temas 367 e 387; abrir ao menos um |
| 8 | CF art. 37, XI → `2 JURIS.` | Continua disponível; abrir o Tema 1167 |
| 9 | CF art. 202, § 5º → `1 CORR.` | LC 108/2001 abre no art. 26 |
| 10 | CF art. 196 → `4 REF.` | **Sicko - S.O.S. Saúde** |
| 11 | CF art. 127 → `3 ENTENDA` | Abre normalmente |

**Se algo falhar:** não corrija nada no cartão e não gere novo candidato. Anote:

- o target;
- as opções exibidas;
- o tema ou súmula mostrados;
- a tese aberta;
- o comportamento de BACK e das teclas;
- qualquer travamento ou reinicialização.

Depois, devolva o cartão ao PC.

**Rollback:** restaurar os 5 arquivos de `DEVICE_INTEGRATION/backups/juris_j1_4_physical_deploy/sd_pre/`, que são idênticos a `J1_4_CANDIDATE_HOST_ONLY/rollback/SD/` (candidato J1.1 validado na J1.2). O firmware não precisa de rollback.

```
READY_FOR_J1_5_PHYSICAL_TEST = YES · JURISPRUDENCE_FROZEN = NO (backlog J2 pendente)
```

## Resultado físico (relatado por Arthur em 2026-10-16)

```
J1_5_PHYSICAL_TEST = 11/11 PASS · J1_5_PHYSICAL_VALIDATION = 11/11 PASS
ORIGINAL_277_REVIEW_COMPLETE = YES · CURRENT_APPROVED_J_BASELINE = 256 (156 targets; cartão = candidato J1.4, BUILD_ID cbed709a40356681)
JURISPRUDENCE_FROZEN = NO (sem freeze geral, sem tag; backlog J2 pendente)
```

Validado no aparelho:

- art. 100, § 1º sem `2 JURIS.`;
- art. 100, § 5º com a SV 17 e os Temas 147, 1037 e 1335;
- Tema 594 no art. 40;
- Tema 594 ausente dos §§ 4º e 5º atuais do art. 40;
- Temas 367 e 387 preservados no art. 16;
- jurisprudência antiga funcionando (art. 37, XI);
- Correlatas, Referências nº 4 e ENTENDA sem regressão.

O cartão permanece com o candidato J1.4. A base de 256 vínculos é a referência da J2 e não deve ser reaberta.
