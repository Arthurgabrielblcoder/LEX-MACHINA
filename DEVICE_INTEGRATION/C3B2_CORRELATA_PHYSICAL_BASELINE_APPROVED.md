# C3B.2 CORRELATA — baseline físico aprovado (2026-10-12)

**`C3B2_BASELINE_PROMOTION = PASS`.** O cartão físico (D:) foi promovido do baseline FULL_CF_ENTENDA_810 para o baseline com a camada CORRELATA C3B.2. O firmware não mudou.

## Cadeia de aprovação

1. **C3B:** teste físico FAIL (passes 1, 4, 7). Rollback.
   - Duas causas raiz: flag C antiga no `CF88_TARGETS.IDX` e `relation_id` compartilhado no RELACOES.
   - Ver `CORRELATA_COVERAGE_AUDIT/C3B_PHYSICAL_TEST_FAILURE_REPORT.md`.
2. **C3B.1:** os bugs estruturais foram corrigidos no build.
   - A flag C passa a ser derivada do DEVICE_READY.
   - Cada linha do aparelho tem `relation_id` único, e cada `REFERENCE_ID` resolve para exatamente 1 linha do RELACOES.
3. **Teste físico C3B.1:** 15 comportamentos observados.
   - 12 expectativas originais estavam corretas.
   - 3 expectativas originais estavam equivocadas (LC 63 no art. 3º ×2; LC 109 no caput do art. 202).
   - Rollback.
4. **Auditoria jurídica e editorial (C3B.2):** os 3 comportamentos são as decisões humanas registradas.
   - Decisão humana final: manter as decisões.
   - O comportamento físico fica 15/15 conforme as decisões autorizadas.
   - Ver `CORRELATA_COVERAGE_AUDIT/C3B1/C3B1_PHYSICAL_TEST_RECLASSIFICATION.md`.
5. **C3B.2:** bytes de aparelho idênticos, byte a byte, aos do C3B.1 testado (6/6). Não precisa de novo reteste físico.
6. **Promoção:** gerador oficial `build_sd_staging` (via `tools/build_c3b2_promotion_candidate.py`) e deploy oficial (`tools/deploy_c3b2_promotion_sd.py` pre/copy/verify).

## O que o novo baseline incorpora

1. `CF88_TARGETS.IDX` com a flag C derivada do DEVICE_READY: a stale flag do art. 37, § 3º, III e as do art. 158, § 1º, II, art. 214, I a VI e art. 37, II foram removidas.
2. IDs de relação únicos no aparelho, com resolução 1:1 entre `REFERENCE_ID` e linha do RELACOES.
3. CF art. 202, § 5º → LC 108, art. 26.
4. Decisões editoriais preservadas:
   - LC 63, art. 3º (arts. 158, § 1º, I e 161, I);
   - LC 109, art. 1º (caput do art. 202);
   - LC 109, art. 3º (art. 202, § 1º).

## Arquivos escritos no cartão (8; demais 1134 intactos)

| Arquivo | SHA-256 |
|---|---|
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX` | `5c54face7ea7eff62dbbb0a4193b5e2452e7fb03d82012d09919e74d234b3e5e` |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX` | `691790f3ee5d4aaa9b88235bca33008357b99d87324c07b1da8b51355c20685c` |
| `99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX` | `efac06cee0a1d8f0676564ba128d0ab8f474b89399f40de6422cc6fded37ef2c` |
| `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | `1762642d337aff83ac5b95e074235bc58028b8a68bac17a384e9eed4a4a5addd` |
| `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | `27c67eea6a38e3cba012d4a3d02c3856d37fd4cd1bae15473854fab0edea5430` |
| `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | `d2fcc15bbe41ef16c51bbe1ef7cb201bd9677b6ac54198b96ad2abc08395e06c` |
| `99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | `6186c3574b0fd46dd4d7fe9ce74d6769587eaac33d017e7f02833b5fd829665a` |
| `99_LEX_V1/00_SYS/LEXV1.VER` | `9132a73deb6e7ef8f8cecca76ac35bf28d0d1202b6403a40d96a15f3f9266c9d` |

- **Verificação:** `SD_VALIDATED`; manifesto × cartão PASS (10 entradas); `other_files_untouched = true`; 1142 arquivos antes e depois.
- **Evidência versionada:** `DEVICE_INTEGRATION/C3B2_CORRELATA_PROMOTION/`.
  - Manifesto do host do staging.
  - `physical_pre.json` e `physical_validation.json`.
  - `sd_manifest_post_full.json`, que passa a ser o último manifesto físico aprovado.
  - VER e manifesto promovidos.

## LEXV1.VER e LEX_DEVICE_MANIFEST.json

- **Ambos foram regenerados pelo gerador oficial**, como em toda promoção do pacote `/99_LEX_V1` (a do 810 também mudou os dois).
- **`LEXV1_VER_CHANGED = YES`**, nos campos que o gerador deriva:
  - `BUILD_ID` = hash dos arquivos do pacote (`3999dfc97c45d91d`);
  - `GIT_COMMIT` = commit que contém os bytes C3B.2 aprovados (`9f83c56e`), fixado para manter a reprodutibilidade;
  - `REFERENCE_ENGINE` = `cf-reference-engine-run4`, rótulo do run seguindo a série run1/run2/run3.
- **Não mudaram:** `DEVICE_VERSION|3` (o único campo que o firmware valida), ENTENDA, TARGETS e o texto runtime.
- **Reprodutibilidade:** o gerador reconstrói o pacote byte a byte (3 execuções). Rodado no estado atual, ele também reproduz o baseline 810 anterior byte a byte, o que prova que o mecanismo é o mesmo.

## Divergência registrada (não corrigida por regra da missão)

- **Flag R:** o gerador, aplicado ao REF do RUN4, recalcularia a flag R em 23 targets.
  - O `CF88_TARGETS.IDX` aprovado mantém o R do baseline, porque só a flag C podia mudar.
  - O firmware não lê R (posições 0 a 3 apenas).
  - As flags C do arquivo aprovado coincidem com as do gerador.

## Rollback para o baseline anterior (FULL_CF_ENTENDA_810)

- **Bytes anteriores dos 8 arquivos** (local, gitignored): `DEVICE_INTEGRATION/backups/c3b2_correlata_physical_deploy/sd_pre/` no checkout principal.
  - Manifestos: `sd_pre_backup_manifest.json` e `sd_manifest_pre_full.json`.
- **Seis deles também estão versionados** em `CORRELATA_COVERAGE_AUDIT/C3B2_PHYSICAL_TEST_PACKAGE/rollback/SD/`.
- **O VER e o manifesto anteriores** são reproduzidos pelo gerador do 810 e listados no pin C0.
