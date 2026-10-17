# JURISPRUDÊNCIA — CF: J2B.1, correção temporal do Tema 558 (antes do deploy do BATCH01)

```
MISSION = J2B.1 (HOST-ONLY) · REGISTRO = J2B_PREDEPLOY_TEMPORAL_FIX · BRANCH = cf-jurisprudence-audit
RATIFICAÇÃO = Arthur, 2026-10-16: TEMA_558_CURRENT_TARGET = CF art. 100 (nível estrutural)
TEMA558_OLD_TARGET = CF art. 100, § 9º · TEMA558_NEW_TARGET = CF art. 100 · TEMPORAL_VERSION = EC 62/2009
OLD_LINK_REMOVED = 1 · TEMPORAL_REALLOCATION_ADDED = 1 · FINAL = 261 vínculos / 160 targets · J_FLAG_CHANGES_VS_J2B = 0
ADI_BATCH01_PRESERVED = YES · PROVISIONAL_GATE_PRESERVED = YES · FROZEN_LAYERS_MODIFIED = NO
MICROSD_TOUCHED = NO · FIRMWARE_CHANGED = NO · DEPLOY = NO · BATCH02 = não iniciado · J1 não reaberta
PACOTE NOVO = JURISPRUDENCE_AUDIT/J2B_1_CANDIDATE_HOST_ONLY/ · PACOTE J2B = SUPERSEDED_BEFORE_PHYSICAL_DEPLOY (preservado)
```

## 1. Causa

O vínculo `CF art. 100, § 9º ← Tema 558` vem do J4. Ele foi gerado pela divisão de uma citação literal (`SPLIT_FROM_LITERAL_CITATION`, citação "§§ 9º e 10 do art. 100 … incluídos pela EC nº 62/09").

- O § 9º que o aparelho exibe hoje é a redação da **EC 113/2021**.
- A tese julgou a compensação do § 9º na redação da **EC 62/2009**, que não está mais em vigor.

O vínculo dava a impressão de que a tese tratava do texto mostrado. É o mesmo tipo de problema da SV 17, do Tema 147, do Tema 594 e da ADI 4425 no antigo § 9º. O caso foi identificado como observação na J2B.

## 2. Evidência (sem nova pesquisa; fontes já registradas na J2A)

- **Ficha do Tema 558 no cartão** (`STF_RG_558.TXT`, RE 678360): a tese trata da compensação "prevista nos §§ 9º e 10 do art. 100 … incluídos pela EC nº 62/09".
- **P1 (Planalto, compilado, `51ac764a…`):** o § 9º tem duas redações e a vigente é a da EC 113/2021.
- **S4 (ementa da ADI 7064, item 28):** a redação dada pela EC 113/2021 é "sensivelmente diferente" da declarada inconstitucional nas ADIs 4425/4357.

## 3. O que mudou

| | Antes (J2B, RUN8) | Depois (J2B.1, RUN9) |
|---|---|---|
| CF art. 100, § 9º | `ADI 7047/7064` · `RG TEMA 558` | **`ADI 7047/7064`** |
| CF art. 100 (artigo) | Temas 1262, 253, 416, 831 | Temas 1262, 253, 416, **558**, 831 |
| CF art. 100, § 10 | `RG TEMA 558` | `RG TEMA 558` (fora do escopo; o § 10 vigente ainda é o texto da EC 62/2009) |
| CF art. 100, § 12 | `ADI 4425` | `ADI 4425` |
| CF art. 166, §§ 9º e 11; art. 166-A | `ADI 7697 (CAUTELAR)` | `ADI 7697 (CAUTELAR)` |

**Como foi feito:**

- **Overlays**, gerados por `JURISPRUDENCE_AUDIT/apply_j2b_1_tema558.py`, com o mesmo mecanismo da J1.4:
  - `LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J2B_1.json` (1 registro `MATERIAL_MISMATCH_EXCLUDED`);
  - `CF88_JURIS_RELOCATIONS_J2B_1.json` (1 realocação).
- **Vínculo novo:** é cópia do removido. Mudam só o target, o status e a visibilidade (recalculados), `migration = RELOCATED_J2B_1`, `payload.nota_temporal`, `payload.versao_temporal = EC 62/2009` e `provenance.relocation`. Passa por `validate_link`.
- **Nota temporal:** "Tema referente aos antigos §§ 9º e 10 do art. 100, incluídos pela EC 62/2009 (compensação de precatórios). Não corresponde ao texto atual do § 9º, dado pela EC 113/2021."
- **Chave legada mantida** (`STF:RG:558:CF88:100:-:-:-`): o registro do `JURISPRUDENCIA.IDX` e a ficha `STF_RG_558.TXT` ficam **byte a byte** como estão no cartão. A tese não foi alterada e o tema continua no acervo.

## 4. RUN9 e contagens (calculadas dos dados)

- **Builder:** `LEGAL_TARGET_ID/build_export_run9_juris_j2b_1.py`.
- **Saída:** `LEGAL_TARGET_ID/derived/export_test/run9_juris_j2b_1_candidate/` (3/3 idêntico).
- **Base:** o RUN8 é conferido contra `SHA256SUMS` e contra o pacote J2B, e reexportado byte-idêntico antes da mudança.
- **Mudança:** RUN9 = RUN8 − 1 + 1.

| Contagem | J2B | J2B.1 |
|---|---:|---:|
| Vínculos J visíveis | 261 | **261** |
| Targets com J | 160 | **160** |
| Mudanças de flag (todas as posições) | — | **0** |

As flags não mudam porque o § 9º mantém J pela ADI 7047/7064 e o art. 100 já tinha J pelos Temas 1262, 253, 416 e 831.

## 5. Pacote HOST-ONLY novo

**Ferramenta:** `JURISPRUDENCE_AUDIT/build_j2b_1_candidate.py --commit de0b181`. É o builder da J2B (parametrizado, com os mesmos gates) apontado para o RUN9.

- **Cartão:** o físico pós-J1.5 é reproduzido primeiro.
- **`/99_LEX_V1`:** gerado pelo gerador oficial.
- **Legado:** só acrescido no fim.
- **Diferença na flag R:** 42.
- **Versão:** `BUILD_ID 12b9fb5624112d9e`, `REFERENCE_ENGINE cf-reference-engine-run9-juris-j2b-1`.

| Arquivo | Mudança | Bytes | SHA-256 do candidato |
|---|---|---:|---|
| `/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | alterado | 62.364 → 63.095 | `62b06deb45b3c1ec9e2ead4fe577241b78658fc62d67f91516b61841e83456e9` |
| `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | alterado | 6.450 → 6.557 | `aa84fbbf8929495a599a70532860ac4e2f90739ecb07e03ece5d3e8145aef03b` |
| `/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | alterado | 165.466 | `103abadec9c4af3c131de744d49efd1f11c291b16f39f676bdca8b204056d570` |
| `/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json` | alterado | 7.641 → 7.712 | `dce393db84f7fe8a392e9bf13da67272c2e90414805c83b2cf87cd985e3f1672` |
| `/99_LEX_V1/00_SYS/LEXV1.VER` | alterado | 596 → 597 | `01ff09b4af77e4bbf91d5cf2f328b7cc89c0a4e2eab09e0b922242b51fd357f1` |
| `/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX` | acréscimo no fim (igual à J2B) | 54.207 → 55.106 | `05e9c2afec5991d25a84ccc99ba4077b4a9730e9009a70983b00dd304d1bc09d` |
| `/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX` | acréscimo no fim (igual à J2B) | 3.755 → 3.863 | `603d9963181727d22aa8a99af50f197cfc71702e136309ace536979bc936c1f3` |
| `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_4425.TXT` | novo (igual à J2B) | 1.441 | `be757508b3472dc4a25fa538a3f7915f290f10c7be5c7e5850982c3b5aa1a3eb` |
| `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7047-7064.TXT` | novo (igual à J2B) | 1.338 | `1a4ca8c76dc0588ca1b6fbc9063c0d4cbc4746d9777d4c52b771bd6b784a283b` |
| `/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_7697.TXT` | novo (igual à J2B) | 1.206 | `0b62db3e0d5b3f9032f4cbf1733afe5b385fd569737d0ea902b957d5e6e68527` |

O pacote **J2B** (`J2B_CANDIDATE_HOST_ONLY/`, `4802b4a3…`) fica preservado como evidência, com o marcador `SUPERSEDED.md` (`SUPERSEDED_BEFORE_PHYSICAL_DEPLOY`). **A J2C deve usar só o J2B.1.**

## 6. Auditoria de isolamento

- **Arquivo:** `J2B_1_ISOLATION_AUDIT.json`.
- **Gerador:** `build_j2b_1_isolation_audit.py` (`--check` dá `UP_TO_DATE` 3/3).

| Verificação | Resultado |
|---|---|
| Removido / adicionado | exatamente o Tema 558 no § 9º / o Tema 558 no art. 100 |
| 256 históricos | intactos, exceto a realocação autorizada |
| ADIs do BATCH01 | as 5 linhas idênticas; modelo, aliases e registro de revalidação inalterados (`apply_j2b_adi_overlay --check` dá `UP_TO_DATE`) |
| Legado | `JURISPRUDENCIA.IDX`, `JUR_LOOKUP.IDX` e fichas ADI idênticos aos da J2B; `STF_RG_558.TXT` intocada; cache de boot válido (301 = 301) |
| Correlatas / obras / ENTENDA | 0 / 0 / arquivos byte-idênticos |
| Flags vs. J2B | E 0 · C 0 · J 0 · W 0 · R 0 · X 0 |
| Espelho do firmware | Tema 558 resolve no art. 100 com ficha; ausente do § 9º; regressão (art. 100 § 5º, art. 40, art. 16, art. 37 XI) idêntica |

## 7. Testes

`JURISPRUDENCE_AUDIT/tests/test_j2b_1.py`, 8 casos que cobrem os 9 itens exigidos:

1. o Tema 558 não resolve no § 9º atual;
2. resolve no art. 100, com nota e `EC 62/2009`;
3. a ficha continua abrindo e não foi tocada;
4. a ADI 7047/7064 continua no § 9º;
5. a ADI 4425 continua no § 12;
6. a ADI 7697 continua nos 3 targets;
7. os 256 continuam intactos, exceto o autorizado (e o § 10 também);
8. as camadas congeladas e o firmware estão intactos;
9. a reprodutibilidade é 3/3.

Há ainda um teste do pacote, que confere o rollback contra o cartão e o marcador de substituição.

| Suíte | Resultado |
|---|---|
| `JURISPRUDENCE_AUDIT/tests` (J1.1, J1.3, J1.4, J2A, J2B, J2B.1) | **46/46 OK** |
| `LEGAL_TARGET_ID/tests` | 90/90 OK |
| `REFERENCE_COVERAGE_AUDIT/tests` | 15/15 OK |
| `CORRELATA_COVERAGE_AUDIT/tests` (módulo a módulo) | Só as falhas já conhecidas: as 4 de `PREEXISTING_CORRELATA_TEST_DEBT` e o `test_16`, que acusa os `_tmp_det_*.log` não versionados |

## 8. Plano físico da J2C (atualiza a seção 10 do J2B_REPORT)

**Pré-requisito:** `check_j2b_provisional.py --as-of <data do deploy>` precisa dar PASS. O pacote é `J2B_1_CANDIDATE_HOST_ONLY`.

| # | Ação | Esperado |
|---|---|---|
| 1 | Boot | Normal |
| 2 | CF art. 100, § 9º → `2 JURIS.` | **Só** `ADI 7047/7064`; o Tema 558 **não** aparece; a ficha "julgamento conjunto" abre |
| 3 | CF art. 100 (caput) → `2 JURIS.` | `RG TEMA 558` com os Temas 1262, 253, 416 e 831; a tese do 558 abre |
| 4 | CF art. 100, § 10 → `2 JURIS.` | `RG TEMA 558` (como hoje) |
| 5 | CF art. 100, § 12 | `ADI 4425` (modulação, nota SELIC) |
| 6 | CF art. 166, § 9º; § 11; art. 166-A | `ADI 7697 (CAUTELAR)`; a ficha começa com DECISÃO PROVISÓRIA |
| 7 | CF art. 166, caput; arts. 92 e 98 | Sem ADI 7697 no caput; sem ADI 3392 |
| 8 | Regressão J1.5 | art. 100 § 5º; art. 40; art. 16; art. 37, XI |
| 9 | Camadas | Correlata art. 202 § 5º; Sicko no art. 196; ENTENDA no art. 127 |

```
NEXT_RECOMMENDED_MISSION = J2C — DEPLOY CONTROLADO DO BATCH01 + CORREÇÃO TEMA 558
```
