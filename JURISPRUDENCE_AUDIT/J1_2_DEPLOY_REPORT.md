# JURISPRUDÊNCIA — CF: J1.2, deploy controlado do SD (candidato J1.1)

```
DATE = 2026-10-16 · BRANCH = cf-jurisprudence-audit (HEAD ce8dd99 no deploy)
HOST_GATES = PASS · PREDEPLOY_SD_BASELINE = PASS · SD_ROLLBACK_READY = YES
SD_FILES_WRITTEN = 5 · SD_CANDIDATE_HASHES = PASS · MANIFEST_VS_SD = PASS · OTHER_SD_FILES_CHANGED = 0
FIRMWARE_FLASH = NO · FIRMWARE_CHANGED = NO (app 6e329c91… mantido)
STATUS = AGUARDANDO TESTE FÍSICO · JURISPRUDENCE_FROZEN = NO · sem promoção de baseline
```

**Evidências.**

- Versionadas em `J1_2_PHYSICAL_DEPLOY/`:
  - `physical_pre.json`;
  - `sd_pre_backup_manifest.json`;
  - `physical_validation.json`;
  - `sd_manifest_post_full.json`;
  - `semantic_check.json`.
- Backup PRE do cartão (fora do Git): `DEVICE_INTEGRATION/backups/juris_j1_1_physical_deploy/sd_pre/`.

**Ferramenta:** `JURISPRUDENCE_AUDIT/deploy_j1_1_sd.py pre|copy|verify`. É o mesmo fluxo da R2/C3B.2: arquivo temporário, `fsync`, `os.replace`, releitura e sha256.

## Gates

| Gate | Resultado |
|---|---|
| **Host** | Testes J1.1 12/12, isolamento `UP_TO_DATE`, RUN6 reconstruído idêntico, pacote íntegro (5 candidatos + 5 rollback batem com o manifesto; `UNEXPECTED_FILES_IN_CANDIDATE = 0`) |
| **Cartão (pré)** | D: inteiro (1.142 arquivos) idêntico ao manifesto físico pós-Referências nº 4. `LEXV1.VER` = `5eb2a9298c1edbd6` / `cf-reference-engine-run5-references4-r1` |
| **Rollback** | `sd_pre/`, 5 arquivos lidos do cartão e conferidos, mais `J1_1_CANDIDATE_HOST_ONLY/rollback/` |

**Hashes PRE:**

| Arquivo | sha256 |
|---|---|
| REF_PAYLOAD | `da49c43b7a21990334a6a1af63fbc605fec7fde195a06a2014776285455006eb` |
| REF_LOOKUP | `efabb245e3beb8b63df33249a7a2e3c178aace02b361d9d344cb348d0fa823a0` |
| CF88_TARGETS | `d4e3342b99f5a5efb732eb9b36f786f3eaf5a33ab651500c7ce8a387bfe593f7` |
| LEX_DEVICE_MANIFEST | `7b8da57d943aef59f6dda55f1eb86484b516f7170da7074e3638949c7ce292fb` |
| LEXV1.VER | `edaf6147767ceece3fdd3149b63d79037e8e06a9de8ca71e3589da88a3758125` |

## Arquivos escritos no cartão (sha256 pós-deploy, lidos de D:)

| Arquivo | Bytes | SHA-256 |
|---|---:|---|
| `/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | 62.528 | `1f87d1af57f1ecd4171212c23414c7e8540099ef20d62607a49a255746efc5e3` |
| `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | 6.476 | `53ed70579c5f4a8f6182f19f3020b231aa3af34f11045f159321c0eb0995664c` |
| `/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | 165.466 | `8eb99cd5d03b058437d4e024ea68dbb0a45daa37f56d69de7e27f81ad8b7dc1e` |
| `/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | 7.644 | `d6d5fc360a2878573c3f0ce642c8be48cd86b4a1cb0ca51d8e1b375b78f2fcf6` |
| `/99_LEX_V1/00_SYS/LEXV1.VER` | 594 | `9366524ec7a54f37175de76e6201a944e9c83b142ecfbba3c8096d0cd1c6acd0` |

**Novo `LEXV1.VER`:**

- `BUILD_ID c4046eaca3ef18a2`;
- `GIT_COMMIT 6d1c65e`;
- `REFERENCE_ENGINE cf-reference-engine-run6-juris-j1`;
- `ENTENDA_COUNT 810`.

## Verificação pós-deploy (bytes do cartão × backup PRE)

| Item | Resultado |
|---|---|
| Arquivos alterados | exatamente os 5; 0 adicionados ou removidos; 1.142 → 1.142 |
| Manifesto × cartão | PASS (10 entradas) |
| RELACOES / REL_LOOKUP / EXT_ARTIGOS | byte-idênticos |
| ENTENDA_LOOKUP / ENTENDA_PAYLOAD | byte-idênticos (`ENTENDA_DATA_CHANGED = NO`) |
| Jurisprudência instalada | **257** vínculos visíveis em **157** targets; os removidos são exatamente os 20 ratificados; 0 adicionados |
| `CORRELATA_RELATIONS_CHANGED` | 0 |
| `WORK_REFERENCE_RELATIONS_CHANGED` | 0 |
| Flags | E 0 · C 0 · **J 13** · W 0 · R 0 · X 0. As 13 mudanças J são exatamente os targets que perderam o último vínculo |
| `R_FLAG_KNOWN_DIVERGENCE` | **37** (inalterada; o firmware não lê R) |

**Os 13 targets que perderam o último vínculo J:**

- CF art. 1, 3, 7, 19, 47 e 96;
- CF art. 14, § 2º;
- CF art. 41, § 1º;
- CF art. 43, caput e § 1º;
- CF art. 48, III;
- CF art. 98, caput e § 2º.

## Checklist físico (o usuário executa)

Remova o cartão com segurança, recoloque no LEX MACHINA e ligue normalmente.

| # | Ação | Esperado |
|---|---|---|
| 1 | Boot | Normal, sem erro de versão ou manifesto; navegação normal |
| 2 | CF art. 1º | **Sem** `2 JURIS.` (o Tema 63 era o único vínculo) |
| 3 | CF art. 47 | **Sem** `2 JURIS.` (Tema 703 removido) |
| 4 | CF art. 19 | **Sem** `2 JURIS.`; o Tema 1157 não aparece (nada foi criado no ADCT) |
| 5 | CF art. 6º → `2 JURIS.` | Continua aparecendo; o **Tema 295** abre normalmente; o Tema 455 **não** aparece |
| 6 | CF art. 16 → `2 JURIS.` | Continua aparecendo (Temas 367/387); o Tema 1031 **não** aparece |
| 7 | CF art. 37, XI → `2 JURIS.` | Caso positivo do checklist histórico J4.6: 10 itens; abrir um (ex.: Tema 1167); a tese abre e BACK funciona |
| 8 | CF art. 202, § 5º → `1 CORR.` | LC 108/2001 abre no art. 26 |
| 9 | CF art. 196 → `4 REF.` | **Sicko - S.O.S. Saúde**; a ficha abre |
| 10 | CF art. 127 → `3 ENTENDA` | Abre normalmente |

**Se algo falhar:** não corrija nada no cartão. Anote:

- o target;
- as opções exibidas;
- a jurisprudência mostrada;
- a tese aberta;
- o comportamento das teclas;
- qualquer travamento ou reinicialização.

Depois, devolva o cartão ao PC.

**Rollback:** restaurar os 5 arquivos de `DEVICE_INTEGRATION/backups/juris_j1_1_physical_deploy/sd_pre/`, que são os bytes físicos de Referências nº 4. O firmware não precisa de rollback, porque não foi alterado.

## Resultado físico (relatado por Arthur em 2026-10-16)

```
J1_2_PHYSICAL_TEST = PASS · PHYSICAL_TESTS = 10/10 · J1_CLEANUP_PHYSICAL_VALIDATION = PASS
```

| # | Teste | Resultado |
|---|---|---|
| 1 | Boot | PASS: boot normal |
| 2 | CF art. 1º | PASS: sem jurisprudência indevida |
| 3 | CF art. 47 | PASS: sem jurisprudência indevida |
| 4 | CF art. 19 | PASS: sem o Tema 1157 indevido |
| 5 | CF art. 6º | PASS: jurisprudência válida preservada; Tema 455 removido |
| 6 | CF art. 16 | PASS: Temas 367/387 preservados; Tema 1031 removido |
| 7 | CF art. 37, XI | PASS: jurisprudência antiga mantida; a tese abre |
| 8 | Correlatas C3B.2 | PASS: sem regressão |
| 9 | Referências nº 4 | PASS: sem regressão |
| 10 | ENTENDA | PASS: sem regressão |

O cartão continua com o candidato J1.1 (257 vínculos J). A Jurisprudência **não** foi promovida nem congelada.
