# JURISPRUDÊNCIA — CF: J1.4, materialização das decisões finais (HOST-ONLY)

```
MISSION = J1.4 (HOST-ONLY: materializar, auditar isolamento, testar, preparar candidato; SEM deploy)
BRANCH = cf-jurisprudence-audit · DADOS = 7786bbc · PACOTE = este commit
RATIFICAÇÃO = Arthur, 2026-10-16: J1_3_EXTERNAL_DECISIONS_APPROVED = 4/4 · TEMAS_367_387 = KEEP_BOTH
JURIS_REMOVED = 4 (os ratificados) · JURIS_RELOCATED_ADDED = 3 · JURIS_OTHER_CHANGES = 0
JURISPRUDÊNCIA VISÍVEL = 257 → 256 vínculos · 157 → 156 targets
CORRELATA_CHANGED = 0 · WORK_REFERENCE_CHANGED = 0 · ENTENDA_CHANGED = 0 · BACKLOG_148_TOUCHED = NO
MICROSD_TOUCHED = NO · FIRMWARE_CHANGED = NO · FLASH = NO · DEPLOY = NO
STATUS = CANDIDATO HOST-ONLY PRONTO · JURISPRUDENCE_FROZEN = NO · sem promoção de baseline
```

## 1. O que foi materializado

| # | Precedente | Antes (removido) | Depois (criado) | Nota temporal (resumo) |
|---|---|---|---|---|
| 1 | **SV 17** | CF art. 100, § 1º | CF art. 100, **§ 5º** | O "período do § 1º" do enunciado é a redação anterior à EC 62/2009; hoje está no § 5º (Tema 1037) |
| 2 | **Tema 147** | CF art. 100, § 1º | CF art. 100, **§ 5º** | Trata do § 1º na redação original e na da EC 30/2000; transferido ao § 5º pela EC 62/2009 |
| 3 | **Tema 594** | CF art. 40, § 4º | CF **art. 40** (um vínculo) | Trata dos §§ 4º e 5º na **redação originária** (paridade e pensão integral); os §§ atuais têm outro conteúdo |
| 4 | **Tema 594** | CF art. 40, § 5º | (mesmo vínculo do item 3) | — |

**Como foi feito:**

- **Exclusões:** `LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J1_4.json` traz 4 registros `MATERIAL_MISMATCH_EXCLUDED`. Usa o mesmo mecanismo fail-closed das exclusões J1 (`reference_engine.link_exclusions`).
- **Realocações:** `LEGAL_TARGET_ID/derived/CF88_JURIS_RELOCATIONS_J1_4.json` traz 3 registros. Cada vínculo novo é cópia do removido. Mudam só o target, o `reference_id`, o status e a visibilidade (recalculados pelo motor), `migration = RELOCATED_J1_4`, a `provenance.relocation` e o `payload.nota_temporal`. Cada um passa por `reference_engine.validate_link`.
- **Mesma chave de vínculo:** a chave (`STF:SV:17:CF88:100:-:-:-`, `STF:RG:147:…`, `STF:RG:594:CF88:40:…`) é mantida. Por isso o aparelho abre **a mesma tese** no `JURISPRUDENCIA.IDX` legado, e a auditoria confirmou que as 3 chaves existem nele.
- **Limite da nota temporal:** a nota fica no export e no `REF_PAYLOAD`, mas o firmware atual mostra o título vindo do IDX legado. Por isso a nota **não aparece na tela**. Ela é proveniência, não texto exibido.
- **Gerador das sobreposições:** `JURISPRUDENCE_AUDIT/apply_j1_4_overlays.py` (`--check` dá `UP_TO_DATE`).

**Preservado:**

- **Temas 367 e 387** em CF art. 16 (`KEEP_BOTH`);
- as **20 exclusões J1/J1.1** (continuam no export);
- os vínculos de CF art. 40, §§ 4º e 5º que não estavam em discussão (Temas 727, 888, 942 e 965);
- o **backlog de 148** (intocado).

## 2. RUN7 (motor de referências)

- **Builder:** `LEGAL_TARGET_ID/build_export_run7_juris_j1_4.py`.
- **Saída:** `LEGAL_TARGET_ID/derived/export_test/run7_juris_j1_4_candidate/` (determinística, 3/3).
- **Base:** RUN6. É conferida contra `SHA256SUMS` e contra os bytes do pacote J1.1 **instalado no cartão** (J1.2 10/10). Antes de qualquer mudança, o RUN6 é reexportado de forma byte-idêntica, como prova de fidelidade.
- **Flags:** só a posição J é recalculada. Muda **um único** target: `CF88:ART.100:PAR.1` vai de `E-J-RX` para `E---RX` (perdeu o último vínculo J). O art. 100, § 5º e o art. 40 já tinham J.
- **Arquivos de Correlatas** (`RELACOES`, `REL_LOOKUP`, `EXT_ARTIGOS`): cópias byte a byte.

## 3. Auditoria de isolamento

- **Arquivo:** `J1_4_ISOLATION_AUDIT.json`.
- **Gerador:** `build_j1_4_isolation_audit.py` (`--check` dá `UP_TO_DATE`).
- **Base de comparação:** o candidato J1.1 instalado.

| Verificação | Resultado |
|---|---|
| Vínculos J removidos | exatamente os 4 ratificados |
| Vínculos J adicionados | exatamente as 3 realocações; chaves presentes no IDX legado |
| Correlatas / Referências nº 4 (obras) | 0 mudanças; arquivos byte-idênticos |
| Flags | J **1** · E 0 · C 0 · W 0 · R 0 · X 0 |
| Jurisprudência histórica oculta | inalterada |
| `REF_LOOKUP` | 237 → 236 linhas (saiu `CF88:ART.100:PAR.1`) |
| `R_FLAG_KNOWN_DIVERGENCE` | 37 → **38** (esperado: o § 1º ficou sem linha no `REF_LOOKUP`; o firmware não lê R) |

## 4. Pacote SD HOST-ONLY (gerador oficial)

**Ferramenta:** `JURISPRUDENCE_AUDIT/build_j1_4_candidate.py --commit 7786bbc50a5f33fcf7eec01ce0de170b2d02a4f6`. Ela usa o `build_sd_staging.py` oficial com o perfil `FULL_CF_ENTENDA_810` e `require_committed_refs`.

**Gates:**

- **Cartão reproduzido primeiro:** o builder J1.1 (fixado em `6d1c65e`) reproduz `J1_2_PHYSICAL_DEPLOY/sd_manifest_post_full.json`, isto é, os bytes físicos atuais. Resultado: `physical_baseline_reproduced = true`.
- **Reconstrução:** byte-idêntica.
- **Manifesto do aparelho × pacote:** PASS.
- **`CF88_TARGETS`:** difere do gerado só na posição R (38 linhas).

**Saídas:**

- **Staging completo:** `DEVICE_INTEGRATION/staging_sd_v1_juris_j1_4_candidate/` (ignorado pelo Git).
- **Pacote versionado:** `JURISPRUDENCE_AUDIT/J1_4_CANDIDATE_HOST_ONLY/`, com `candidate/`, `rollback/` (= bytes do cartão hoje) e `J1_4_PACKAGE_MANIFEST.json`.
- **`LEXV1.VER` novo:**
  - `BUILD_ID cbed709a40356681`;
  - `GIT_COMMIT 7786bbc`;
  - `REFERENCE_ENGINE cf-reference-engine-run7-juris-j1-4`;
  - `ENTENDA_COUNT 810`.

| Arquivo (5 alterados; nenhum outro) | Antes (cartão) | Depois (candidato) | Bytes |
|---|---|---|---:|
| `/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | `1f87d1af…` | `d07cb0764735a56d9f7eecb915a56ed083d35e662cd47164293e388d048f72e1` | 62.528 → 62.364 |
| `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | `53ed7057…` | `66bea5f0ddddb4c17ef4c25e587fcb95cc705f955b7620c6c31ea2a072bcfe38` | 6.476 → 6.450 |
| `/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | `8eb99cd5…` | `75d483c081c23e5fea981f516abae510af0a8104c4fa9e3e59ca52a8bbb9d213` | 165.466 |
| `/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | `d6d5fc36…` | `28b412d163aaccc183c0751e026debfcad2f0a40248e462135ea161750d7cf4e` | 7.644 → 7.641 |
| `/99_LEX_V1/00_SYS/LEXV1.VER` | `9366524e…` | `71eb25ce67c461c7b573976f1f299065f77beaccb5d3e5224c5a3f11131a1af8` | 594 → 596 |

**Firmware:** nenhuma mudança necessária (o app `6e329c91…` continua).

## 5. Testes

| Suíte | Resultado |
|---|---|
| `JURISPRUDENCE_AUDIT/tests` (J1.1 + J1.3 + J1.4) | **25/25 OK** |
| `LEGAL_TARGET_ID/tests` | 90/90 OK |
| `REFERENCE_COVERAGE_AUDIT/tests` | 15/15 OK |
| `CORRELATA_COVERAGE_AUDIT/tests` (módulo a módulo) | Só as falhas já conhecidas: as 4 de `PREEXISTING_CORRELATA_TEST_DEBT` e o `test_16`, que acusa os arquivos não versionados `DEVICE_INTEGRATION/_tmp_det_*.log` |

**`test_j1_4.py` cobre:**

- geradores atualizados;
- RUN7 reproduzível;
- delta exato (256/156; 367/387 mantidos);
- nota temporal e mesma chave;
- flags e isolamento;
- pacote e rollback = cartão;
- simulador do aparelho:
  - § 1º sem `JURIS`;
  - § 5º com SV 17, Temas 147, 1037 e 1335;
  - art. 40 com o Tema 594;
  - §§ 4º e 5º do art. 40 ainda com J;
  - Correlata do art. 202, § 5º; Sicko no art. 196.

**Ajuste em `test_j1_3.py`:** o invariante "nada publicado mudou" passa a comparar `d873037..7b644ab` (o commit da J1.3). Antes ele comparava contra a árvore atual, que a J1.4 altera de propósito.

## 6. Plano do teste físico (para uma futura J1.5; NÃO executado)

**Deploy:** só SD, os 5 arquivos acima, com o mesmo fluxo `pre|copy|verify` da J1.2. Antes da cópia, o cartão inteiro precisa bater com `J1_2_PHYSICAL_DEPLOY/sd_manifest_post_full.json`.

| # | Ação | Esperado |
|---|---|---|
| 1 | Boot | Normal, sem erro de versão ou manifesto |
| 2 | CF art. 100, § 1º | **Sem** `2 JURIS.` (SV 17 e Tema 147 saíram) |
| 3 | CF art. 100, § 5º → `2 JURIS.` | **SV 17** e **Tema 147** aparecem junto com os Temas 1037 e 1335; abrir a SV 17 e conferir que a tese abre e que BACK funciona |
| 4 | CF art. 40 (caput) → `2 JURIS.` | **Tema 594** aparece (com o Tema 1254); a tese abre |
| 5 | CF art. 40, § 4º → `2 JURIS.` | Temas 727, 888 e 942; o **Tema 594 não** aparece |
| 6 | CF art. 40, § 5º → `2 JURIS.` | Tema 965; o **Tema 594 não** aparece |
| 7 | CF art. 16 → `2 JURIS.` | Temas 367 e 387 continuam |
| 8 | CF art. 1º e art. 47 | Continuam **sem** `2 JURIS.` (J1.1 preservada) |
| 9 | CF art. 202, § 5º → `1 CORR.` | LC 108/2001 abre no art. 26 |
| 10 | CF art. 196 → `4 REF.` | **Sicko - S.O.S. Saúde**; a ficha abre |
| 11 | CF art. 127 → `3 ENTENDA` | Abre normalmente |

**Rollback:** `J1_4_CANDIDATE_HOST_ONLY/rollback/SD/`. São os 5 arquivos do cartão hoje (candidato J1.1, J1.2 10/10). O firmware não precisa de rollback.

## 7. Reconciliação

| Etapa | Vínculos J visíveis |
|---|---:|
| Original | 277 |
| J1.1 (−20, validado fisicamente) | 257 |
| J1.4: −4 alvos errados | 253 (`PROPOSED_FINAL_ORIGINAL_SET_RELATIONS` da J1.3) |
| J1.4: +3 realocações | **256** |

**Dívidas conhecidas, não tratadas aqui:**

- divergência da flag R (agora 38);
- cabeçalho do firmware com 122 fichas (`REPRODUCIBILITY_DEBT`);
- `main` defasada;
- 4 testes Correlatas antigos.

```
NEXT_RECOMMENDED_MISSION = J1.5 — DEPLOY CONTROLADO DO SD (candidato J1.4) + TESTE FÍSICO (decisão do usuário)
```
