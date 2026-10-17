# JURISPRUDÊNCIA — CF: J2C, deploy controlado do BATCH01 de ADIs + correção temporal do Tema 558

```
DATE = 2026-10-16 · BRANCH = cf-jurisprudence-audit (HEAD e185d44 no deploy; contém J1.5 físico, J2A, J2B e J2B.1)
PACOTE = JURISPRUDENCE_AUDIT/J2B_1_CANDIDATE_HOST_ONLY (BUILD_ID 12b9fb5624112d9e) · SUPERSEDED_J2B_PACKAGE_USED = NO
HOST_GATES = PASS · ADI7697_PROVISIONAL_GATE = PASS (as-of 2026-10-16; 0/90 dias) · PREDEPLOY_SD_BASELINE = PASS (1.142 arquivos)
SD_ROLLBACK_READY = YES · DELETE_NEW_ADI_FILES = YES
FILES_MODIFIED = 7 · FILES_CREATED = 3 · FILES_DELETED = 0 · UNEXPECTED_SD_CHANGES = 0 · 1.142 → 1.145 arquivos
LEGACY_INDEX_PREFIX_IDENTICAL = YES · OLD_OFFSETS_PRESERVED = YES · TEMA558_FICHA_CHANGED = NO
SD_CANDIDATE_HASHES = PASS · MANIFEST_VS_SD = PASS · JURIS_RELATIONS_INSTALLED = 261 · JURIS_TARGETS_INSTALLED = 160
CORRELATA_RELATIONS_CHANGED = 0 · WORK_REFERENCE_RELATIONS_CHANGED = 0 · ENTENDA_DATA_CHANGED = NO · R_FLAG_KNOWN_DIVERGENCE = 42
FIRMWARE_FLASH = NO · FIRMWARE_CHANGED = NO (app 6e329c91… mantido)
STATUS = AGUARDANDO TESTE FÍSICO · JURISPRUDENCE_FROZEN = NO · Batch02 não iniciado
```

**Ferramentas:**

- `JURISPRUDENCE_AUDIT/deploy_j2c_sd.py pre|copy|verify`: o mesmo fluxo da J1.5, com **criação** de arquivos novos. O destino não pode existir; a escrita usa `.LEX_NEW`, `fsync`, `os.replace`, releitura e sha256. O gate de revalidação roda antes de qualquer escrita.
- `JURISPRUDENCE_AUDIT/semantic_check_j2c_sd.py`: leitura apenas, direto de `D:`.

**Evidências:**

- **Versionadas** em `J2C_PHYSICAL_DEPLOY/`:
  - `physical_pre.json`;
  - `sd_pre_backup_manifest.json`;
  - `physical_validation.json`;
  - `sd_manifest_post_full.json`;
  - `semantic_check.json`.
- **Backup PRE** (fora do Git): `DEVICE_INTEGRATION/backups/juris_j2c_physical_deploy/sd_pre/`.

## Gates

| Gate | Resultado |
|---|---|
| **Host** | JURIS 46/46 · LEGAL_TARGET_ID 90/90 · REFERENCES_4 15/15 · isolamento J2B.1 `UP_TO_DATE`/PASS · RUN9 reproduzível (teste 3/3) · overlays `UP_TO_DATE` |
| **ADI 7697** | `check_j2b_provisional.py --as-of 2026-10-16` dá PASS (`last_verified_on 2026-10-16`, sem mérito registrado) |
| **Cartão (pré)** | D: inteiro (1.142 arquivos) idêntico ao manifesto físico pós-J1.5. `LEXV1.VER` = `cbed709a40356681` / `run7-juris-j1-4`. As 3 fichas ADI **não existiam** |
| **Índices legados** | `JURISPRUDENCIA.IDX`: 54.207 bytes / 297 linhas do cartão são **prefixo exato** (+899 bytes / +5 linhas). `JUR_LOOKUP.IDX`: 3.755 / 179 linhas são prefixo exato (+108 / +5). Offsets antigos preservados |
| **Rollback** | `sd_pre/` = 7 arquivos lidos do cartão = `J2B_1_CANDIDATE_HOST_ONLY/rollback/` (7/7). Arquivos novos: rollback **apaga** |
| **Invariantes (pré)** | `J2B_1_ISOLATION_AUDIT` + `J2B_ISOLATION_AUDIT`, ambos sobre os bytes instalados, que são os do cartão: Correlatas 0, obras 0, ENTENDA intacto, só J |

## Arquivos escritos (sha256 lido de D: depois do deploy)

**Fichas criadas:**

| Arquivo | Bytes | SHA-256 |
|---|---:|---|
| `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_4425.TXT` | 1.441 | `be757508b3472dc4a25fa538a3f7915f290f10c7be5c7e5850982c3b5aa1a3eb` |
| `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7047-7064.TXT` | 1.338 | `1a4ca8c76dc0588ca1b6fbc9063c0d4cbc4746d9777d4c52b771bd6b784a283b` |
| `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7697.TXT` | 1.206 | `0b62db3e0d5b3f9032f4cbf1733afe5b385fd569737d0ea902b957d5e6e68527` |

**Arquivos substituídos:**

| Arquivo | Bytes | SHA-256 depois | SHA-256 antes (rollback) |
|---|---:|---|---|
| `/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX` | 55.106 | `05e9c2afec5991d25a84ccc99ba4077b4a9730e9009a70983b00dd304d1bc09d` | `f85108baf4ee296a7672e11733d63a32be60882d60364063a5a466e7a982b6f1` |
| `/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX` | 3.863 | `603d9963181727d22aa8a99af50f197cfc71702e136309ace536979bc936c1f3` | `7931e28e7a0592e2bd1a1872ee0904149eac50365c1c98990370a1235c618956` |
| `/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | 63.095 | `62b06deb45b3c1ec9e2ead4fe577241b78658fc62d67f91516b61841e83456e9` | `d07cb0764735a56d9f7eecb915a56ed083d35e662cd47164293e388d048f72e1` |
| `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | 6.557 | `aa84fbbf8929495a599a70532860ac4e2f90739ecb07e03ece5d3e8145aef03b` | `66bea5f0ddddb4c17ef4c25e587fcb95cc705f955b7620c6c31ea2a072bcfe38` |
| `/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | 165.466 | `103abadec9c4af3c131de744d49efd1f11c291b16f39f676bdca8b204056d570` | `75d483c081c23e5fea981f516abae510af0a8104c4fa9e3e59ca52a8bbb9d213` |
| `/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | 7.712 | `dce393db84f7fe8a392e9bf13da67272c2e90414805c83b2cf87cd985e3f1672` | `28b412d163aaccc183c0751e026debfcad2f0a40248e462135ea161750d7cf4e` |
| `/99_LEX_V1/00_SYS/LEXV1.VER` | 597 | `01ff09b4af77e4bbf91d5cf2f328b7cc89c0a4e2eab09e0b922242b51fd357f1` | `71eb25ce67c461c7b573976f1f299065f77beaccb5d3e5224c5a3f11131a1af8` |

**Novo `LEXV1.VER`:**

- `BUILD_ID 12b9fb5624112d9e`;
- `GIT_COMMIT de0b181`;
- `REFERENCE_ENGINE cf-reference-engine-run9-juris-j2b-1`.

A ficha `STF_RG_558.TXT` continua byte-idêntica (`e1c02285…`).

## Verificação pós-deploy (bytes de D:)

| Item | Resultado |
|---|---|
| Diferença no cartão inteiro × PRE | 7 alterados (exatamente os previstos), 3 criados (exatamente as fichas ADI), 0 removidos; `UNEXPECTED_SD_CHANGES = 0` |
| Manifesto × cartão | PASS (10 entradas) |
| RELACOES / REL_LOOKUP / EXT_ARTIGOS / ENTENDA_LOOKUP / ENTENDA_PAYLOAD | byte-idênticos |
| Delta de vínculos | −1 (Tema 558 no § 9º); +6 (Tema 558 no art. 100 e as 5 ADIs). É exatamente o J2B.1 |
| Jurisprudência instalada | **261** vínculos em **160** targets |
| Flags × J1.5 | J **4** (art. 100 § 12; art. 166 §§ 9º e 11; art. 166-A) · E/C/W/R/X 0 · J = jurisprudência visível · R = 42 |
| Cache de boot (regras do firmware, nos bytes do cartão) | válido: 301 registros = soma das quantidades 301 |

## Simulação do firmware sobre os bytes de D:

| Dispositivo | Lista `2 JURIS.` (simulada) |
|---|---|
| CF art. 100, § 9º | `ADI 7047/7064` (o Tema 558 **não** aparece) |
| CF art. 100 | `RG TEMA 1262` · `RG TEMA 253` · `RG TEMA 416` · **`RG TEMA 558`** · `RG TEMA 831` |
| CF art. 100, § 10 | `RG TEMA 558` (inalterado) |
| CF art. 100, § 12 | `ADI 4425` |
| CF art. 166, § 9º / § 11 / art. 166-A | `ADI 7697 (CAUTELAR)` |
| CF art. 166 (caput) / arts. 92 e 98 | nenhum item (ADI 7697 não está no caput; ADI 3392 não aparece) |

Todos os itens resolvem no `JURISPRUDENCIA.IDX` do cartão, com a ficha presente. As fichas no cartão começam assim:

- **7047/7064:** "AÇÕES DIRETAS DE INCONSTITUCIONALIDADE 7047 E 7064 (JULGAMENTO CONJUNTO)";
- **4425:** "… 4425 / STATUS: mérito julgado (com modulação de efeitos)";
- **7697:** "… STATUS: medida cautelar referendada pelo Plenário - mérito pendente", seguido de **DECISÃO PROVISÓRIA**.

**Regressões:**

- CF art. 16: Temas 367 e 387;
- CF art. 37, XI: 10 temas, incluindo o 1167;
- CF art. 100, § 5º: SV 17 e Temas 1037, 1335 e 147;
- CF art. 40: Temas 1254 e 594;
- CF art. 202, § 5º: `EXT_LC108_2001`;
- CF art. 196: Sicko;
- CF art. 127: ENTENDA disponível.

Tudo igual ao aprovado.

## Teste físico J2C (o usuário executa)

Remova o cartão com segurança, recoloque no LEX MACHINA e ligue normalmente.

| # | Ação | Esperado |
|---|---|---|
| 1 | Boot | Normal, sem erro de versão ou manifesto |
| 2 | CF art. 100, § 9º → `2 JURIS.` | `ADI 7047/7064`; o Tema 558 **não** aparece. Abrir: a ficha "JULGAMENTO CONJUNTO" abre, legível; BACK funciona |
| 3 | CF art. 100 (caput) → `2 JURIS.` | `RG TEMA 558` com os Temas 1262, 253, 416 e 831; abrir o 558: a tese abre |
| 4 | CF art. 100, § 12 → `2 JURIS.` | `ADI 4425`; abrir; leitura e BACK |
| 5 | CF art. 166, § 9º → `2 JURIS.` | `ADI 7697 (CAUTELAR)`; a ficha mostra **DECISÃO PROVISÓRIA** e "mérito pendente" |
| 6 | CF art. 166, § 11 | `ADI 7697 (CAUTELAR)`; a ficha abre |
| 7 | CF art. 166-A | `ADI 7697 (CAUTELAR)`; a ficha abre |
| 8 | CF art. 16 | Temas 367 e 387; abrir um |
| 9 | CF art. 37, XI | O Tema 1167 abre |
| 10 | CF art. 202, § 5º → `1 CORR.` | LC 108/2001 abre no art. 26 |
| 11 | CF art. 196 → `4 REF.` | Sicko |
| 12 | CF art. 127 → `3 ENTENDA` | Abre normalmente |

**Se algo falhar:** não corrija nada no cartão e não gere novo pacote. Anote:

- o target;
- os itens mostrados e a ordem da lista;
- o rótulo da ADI;
- o conteúdo da ficha;
- o comportamento de BACK;
- qualquer travamento ou reinicialização.

Depois, devolva o cartão ao PC.

**Rollback** (volta exatamente ao estado J1.5):

1. Restaurar os 7 arquivos de `DEVICE_INTEGRATION/backups/juris_j2c_physical_deploy/sd_pre/`, que são idênticos a `J2B_1_CANDIDATE_HOST_ONLY/rollback/SD/`.
2. **Apagar** as fichas criadas:
   - `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_4425.TXT`
   - `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7047-7064.TXT`
   - `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7697.TXT`

O firmware não precisa de rollback.

```
READY_FOR_J2C_PHYSICAL_TEST = YES · JURISPRUDENCE_FROZEN = NO (restam 32 HIGH)
```

## Resultado físico (relatado por Arthur)

```
J2C_PHYSICAL_TEST = 12/12 PASS · J2C_PHYSICAL_VALIDATION = 12/12 PASS
BASELINE INSTALADO = 261 vínculos J / 160 targets (candidato J2B.1, BUILD_ID 12b9fb5624112d9e)
JURISPRUDENCE_FROZEN = NO (backlog HIGH pendente)
```

Confirmado no aparelho:

- ADI 7047/7064 no art. 100, § 9º;
- ADI 4425 no § 12;
- ADI 7697 nos três targets (§§ 9º e 11 do art. 166 e art. 166-A), com o marcador `(CAUTELAR)` e o aviso provisório;
- as fichas abrem;
- Tema 558 corrigido (fora do § 9º, presente no art. 100);
- Temas 367/387 preservados;
- jurisprudência antiga preservada;
- Correlatas, Referências nº 4 e ENTENDA sem regressão.

As decisões do Batch01 e a correção do Tema 558 não devem ser reabertas.
