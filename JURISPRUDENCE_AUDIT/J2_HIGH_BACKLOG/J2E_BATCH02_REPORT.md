# JURISPRUDÊNCIA — CF: J2E, materialização HOST-ONLY do Batch02 ratificado

```
MISSION = J2E (operação noturna, fases A/B) · HOST-ONLY · BRANCH = cf-jurisprudence-audit · DADOS = 8f685ad
RATIFICAÇÃO = Arthur, 2026-10-17: Batch02 (J2D) integral · HC232627_EDITORIAL_APPROVAL = YES · HC232627_PHYSICAL_APPROVAL = NO
PHYSICAL_BASELINE_REPRODUCED = PASS (J2C: 19/19 arquivos gerados = manifesto do cartão) · ONLY_APPROVED_RELATIONS_ADDED = YES
FROZEN_LAYERS_MODIFIED = NO · FIRMWARE_FLASH = NO · MICROSD_TOUCHED = NO · DEPLOY = NO
```

## Grandezas (não confundir)

| Grandeza | Valor |
|---|---|
| `EDITORIAL_DECISIONS` | 10 (9 aprovadas e 1 rejeição: ADI 2167) |
| `DEVICE_RELATIONS` | **A: 7** · **B: 8** (B = A + HC 232627) |
| `PRECEDENT_RECORDS` (legado) | 7 linhas em A e 8 em B. Fontes: ADI 7047/7064 (2 alvos), ADI 7064, Tema 793, SV 46 (2 alvos), Tema 950, HC 232627 |
| `NEW_FICHAS` | **A: 4** (`STF_ADI_7064`, `STF_RG_793`, `STF_RG_950`, `STF_SV_46`) · **B: 5** (+ `STF_HC_232627`). A ficha conjunta 7047/7064 é reaproveitada do cartão |
| `NEW_TARGETS_WITH_J` | **A: 6** (ADCT 101 § 5º; ADCT 107-A; CF 100 § 11; CF 23, II; CF 53 caput; CF 85, p.u.); o art. 22, I já tinha J · **B: 7** (+ CF 53, § 1º) |
| Jurisprudência visível | 261/160 → **A: 268/166** · **B: 269/167** |

## Variantes

- **A (`VARIANT_A_CURRENT_FIRMWARE`):** tudo o que o firmware atual mostra corretamente. Pode ir a um futuro deploy só de SD, depois de autorizado.
- **B (`VARIANT_B_REQUIRES_HC_FIRMWARE`):** A + HC 232627. Com o firmware atual, o HC apareceria como `OUTRO 232627`, como mostra a simulação. **B exige** um firmware candidato com tipo HC (fase C) e um teste físico próprio.

## Decisões de modelagem

- **ADI 7064 no ADCT art. 107-A:** registro e ficha **próprios** (`STF:ADI:7064`, rótulo `ADI 7064`). A ação foi julgada junto com a ADI 7047, mas o art. 107-A é objeto **só da 7064**: mesmo julgamento, escopo diferente (`SAME_JUDGMENT_NOT_SAME_SCOPE`). A ficha diz isso e remete à ficha conjunta para os pontos comuns.
- **ADI 7047/7064 no ADCT 101, § 5º e no CF 100, § 11:** usam o registro conjunto já validado no cartão. Nenhuma ficha nova.
- **Tema 793:** ficha gerada do **corpus oficial arquivado** (endpoint de teses do STF, captura de 2026-09-21; sha no JSON). A tese é idêntica à do RE 855178 ED, conferida em 2026-10-17. Não havia ficha no cartão.
- **SV 46:** ficha única para os dois alvos. Uso o texto da página oficial atual ("**da** competência"); o corpus arquivado dizia "**de** competência".
- **Tema 950:** não estava no corpus arquivado. A tese foi copiada da página oficial do acórdão (RE 632115, 2026-10-17).
- **Formato das fichas RG/SV:** usa a mesma função `texto_detalhe` do pacote J4.6. Ela regenera **byte a byte** fichas que já estão no cartão (147, SV 17, 558, 1246), e isso está provado em teste.
- **Chave legada de ADCT:** mantive a convenção existente, com prefixo `CF88` na chave e no lookup. Exemplos: `STF:RG:231:CF88:78:4:-:-` é o ADCT art. 78, § 4º; o novo `STF:ADI:7047-7064:CF88:101:5:-:-` é o ADCT art. 101, § 5º. O target lógico (`ADCT:ART.…`) é o do `REF_PAYLOAD`. O firmware (caminho V1) resolve pela chave exata; o lookup legado só serve ao cache e ao caminho antigo, que não é usado na CF.
- **`LOOKUP_TUPLE_SHARED`:** `CF88|22||I||` já existia (Tema 1246). Como o índice é append-only, a SV 46 ganhou uma segunda linha com a mesma tupla. O cache de boot continua válido (soma 308 = 308 registros em A).

## Pacotes

**Local:** `J2_HIGH_BACKLOG/J2E_BATCH02_CANDIDATE_HOST_ONLY/` (`VARIANT_A_…` e `VARIANT_B_…`), cada um com `candidate/`, `rollback/` (= bytes do cartão J2C) e `J2E_PACKAGE_MANIFEST.json`.

**Ferramenta:** `build_j2e_candidate.py --commit 8f685ad`. Ela usa o gerador oficial, reproduz o cartão J2C antes e verifica determinismo 2/2.

| Variante | BUILD_ID | Alterados | Novos (rollback: apagar) | R conhecida |
|---|---|---:|---:|---:|
| A | `c3736c4bce089ce1` | 7 | 4 | 48 |
| B | `91280967133de3e6` | 7 | 5 | 49 |

## Auditoria (`J2E_ISOLATION_AUDIT.json`, 3/3 idêntico)

Nas duas variantes:

- os 261 instalados estão byte-idênticos;
- só as relações ratificadas foram adicionadas;
- Correlatas e obras: 0 mudanças;
- flags: só J;
- índices legados com prefixo idêntico;
- regras do cache de boot válidas;
- todos os itens simulados resolvem e têm ficha;
- regressão (art. 100 § 5º, 40, 16, 37 XI, 100, 100 § 12, 166 §§ 9º/11, 166-A) idêntica;
- rejeitados não vinculados.

**Simulação da lista `2 JURIS.` com o firmware atual:**

| Dispositivo | Lista |
|---|---|
| ADCT art. 101, § 5º | `ADI 7047/7064` |
| ADCT art. 107-A | **`ADI 7064`** |
| CF art. 100, § 11 | `ADI 7047/7064` |
| CF art. 23, II | `RG TEMA 793` |
| CF art. 22, I | `SV 46` · `RG TEMA 1246` |
| CF art. 85, p.u. | `SV 46` |
| CF art. 53 (caput) | `RG TEMA 950` |
| CF art. 53, § 1º | A: nada · B com firmware atual: `OUTRO 232627` · B com firmware HC: `HC 232627` |

## Testes

`JURISPRUDENCE_AUDIT/tests/test_j2e.py`, 8 testes:

- geradores atualizados;
- RUN10 reproduzível;
- fidelidade do formato das fichas;
- contagens normalizadas;
- ADI 7064 sem rótulo conjunto no 107-A;
- convenção de chave do ADCT;
- isolamento e pacotes;
- baseline físico intocado.

Suíte J1/J2 completa: **60/60 OK**.
