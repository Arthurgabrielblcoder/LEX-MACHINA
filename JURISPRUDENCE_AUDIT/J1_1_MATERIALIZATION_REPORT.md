# JURISPRUDÊNCIA — CF: J1.1, materialização das 20 remoções ratificadas (HOST-ONLY)

```
STATUS = HOST_ONLY_CANDIDATE (nada instalado; cartão e ESP32 não tocados; sem deploy)
RATIFICAÇÃO = Arthur, 2026-10-16: J1_REMOVE_FALSE_POSITIVE_APPROVED = 20/20
BRANCH = cf-jurisprudence-audit · dados RUN6 em 6d1c65e (GIT_COMMIT do pacote)
JURIS_RELATIONS 277 → 257 · JURIS_TARGETS 170 → 157 · J flags 170 → 157 (13 mudanças)
CORRELATA / WORK_REFERENCE / ENTENDA / Lei Seca: sem alteração · FIRMWARE: inalterado (não necessário)
```

## 1. O que foi feito

| Passo | Resultado |
|---|---|
| Overlay `LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J1.json` | 20 registros `MATERIAL_MISMATCH_EXCLUDED` com trecho oficial, sha da tese, norma realmente citada e ratificação. Gerado por `JURISPRUDENCE_AUDIT/apply_j1_exclusions.py` a partir de `J1_DECISIONS.json` |
| Validação pelo motor | `reference_engine.link_exclusions()` aceitou os 20: cada registro corresponde a exatamente um vínculo existente |
| Overlay anterior | `CF88_LINK_EXCLUSIONS.json` (Temas 113/756) **não foi editado**, então RUN3 a RUN5 continuam reproduzíveis |
| Export RUN6 | `LEGAL_TARGET_ID/build_export_run6_juris_j1.py` → `derived/export_test/run6_juris_j1_candidate/` |

**Como o RUN6 foi gerado:**

1. Partiu dos bytes RUN5, iguais ao pacote físico aprovado em 2026-10-16.
2. Reproduziu o RUN5 byte a byte antes de mexer em qualquer coisa.
3. Removeu exatamente os 20 vínculos.
4. Recalculou só a posição J de `CF88_TARGETS.IDX`.
5. Copiou byte a byte os arquivos de Correlatas.

**Reprodutibilidade:** 3 builds idênticos.

**O que não foi feito, como pedido:**

- nenhuma realocação para o ADCT (os 5 candidatos ficam registrados como `relocation_candidate_not_applied`);
- nenhum vínculo novo;
- os 4 `EXTERNAL_REVIEW_REQUIRED` e o `DUPLICATE_OR_REDUNDANT` continuam publicados e pendentes (teste automatizado);
- o backlog de 148 não foi tocado.

## 2. Isolamento (`J1_1_ISOLATION_AUDIT.json`, base = pacote físico aprovado)

| Verificação | Resultado |
|---|---|
| Linhas JURISPRUDENCE removidas | **20**, exatamente o conjunto ratificado |
| JURISPRUDENCE adicionadas ou alteradas | 0 |
| Ocultas históricas | inalteradas (6) |
| CORRELATA (conjunto) | **0 mudanças** (24 visíveis + 2 ocultas) |
| WORK_REFERENCE (conjunto) | **0 mudanças** (124) |
| RELACOES / REL_LOOKUP / EXT_ARTIGOS | byte-idênticos ao C3B.2 |
| Flags E/B, C, W, R, X | **0 mudanças** |
| Flag J | 13 mudanças, **só** onde o último vínculo J visível caiu; J igual aos targets com jurisprudência visível |
| `REF_LOOKUP` | 249 → 237 linhas (12 targets ficam sem nenhuma referência). O art. 43, caput mantém a linha por causa da obra de Referências nº 4 |

**Os 13 targets que perdem `2 JURIS.`:**

- CF art. 1º, 3º, 7º, 19, 47 e 96 (linha do artigo);
- CF art. 14, § 2º;
- CF art. 41, § 1º;
- CF art. 43, caput e § 1º;
- CF art. 48, III;
- CF art. 98, caput e § 2º.

**Continuam com jurisprudência por outro tema correto:** arts. 6º, 8º IV, 16 e 227.

**Flag R:** não foi recalculada (o firmware não a lê). A divergência R-only em relação ao gerador vai de 25 para **37**: os 12 targets sem linha no lookup mantêm R. É a mesma dívida conhecida, agora registrada no manifesto.

## 3. Pacote host-only (`JURISPRUDENCE_AUDIT/J1_1_CANDIDATE_HOST_ONLY/`)

**Gerador oficial:** `build_sd_staging`, perfil `FULL_CF_ENTENDA_810`, com `GIT_COMMIT 6d1c65e` e build `c4046eaca3ef18a2`.

**Provas executadas antes:**

- o builder do pacote R1, reexecutado no seu commit fixo, reproduziu o cartão físico atual (`R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json`);
- dois builds idênticos;
- o manifesto do aparelho bate com o pacote.

| Arquivo `/99_LEX_V1/…` | Antes (físico) | Depois (candidato) |
|---|---|---|
| `20_REFERENCES/REF_PAYLOAD.IDX` | `da49c43b…` (65.514 B) | `1f87d1af57f1ecd4171212c23414c7e8540099ef20d62607a49a255746efc5e3` (62.528 B) |
| `20_REFERENCES/REF_LOOKUP.IDX` | `efabb245…` (6.750 B) | `53ed70579c5f4a8f6182f19f3020b231aa3af34f11045f159321c0eb0995664c` (6.476 B) |
| `10_TARGETS/CF88_TARGETS.IDX` | `d4e3342b…` | `8eb99cd5d03b058437d4e024ea68dbb0a45daa37f56d69de7e27f81ad8b7dc1e` |
| `00_SYS/LEX_DEVICE_MANIFEST.json` | `7b8da57d…` | `d6d5fc360a2878573c3f0ce642c8be48cd86b4a1cb0ca51d8e1b375b78f2fcf6` |
| `00_SYS/LEXV1.VER` | `edaf6147…` | `9366524ec7a54f37175de76e6201a944e9c83b142ecfbba3c8096d0cd1c6acd0` |

- O rollback (`rollback/`) contém os bytes físicos atuais.
- **Firmware:** nenhuma mudança. A jurisprudência não tem tabela no firmware, e nenhum caso do DIAG de boot usa os targets afetados (art. 37, § 6º continua com 5).

## 4. Testes

| Suíte | Resultado |
|---|---|
| `JURISPRUDENCE_AUDIT/tests` (`test_j1_1.py`, novo) | **12/12**: overlay = 20 ratificados; RUN6 reproduzível; só os 20 saem; pendentes continuam; contagens; flags; isolamento; pacote e rollback; simulador do aparelho (13 linhas sem `2 JURIS.`, temas corretos mantidos, Correlata art. 202 § 5º → LC 108/2001, Sicko no art. 196, obra no art. 43) |
| `LEGAL_TARGET_ID/tests` | OK |
| `REFERENCE_COVERAGE_AUDIT/tests` | OK |
| `DEVICE_INTEGRATION/tests` | OK |
| `test_correlata_c3b2_promotion` | OK |

**Correlatas:**

- `test_15` continua falhando: é uma das 4 falhas pré-existentes já documentadas.
- `test_16` falha neste working tree só pelos arquivos soltos já conhecidos. Nenhum arquivo de `DEVICE_INTEGRATION/`, `firmware/`, `CORRELATA_COVERAGE_AUDIT/`, `REFERENCE_COVERAGE_AUDIT/` ou `ENTENDA_ENGINE/` foi alterado.

## 5. Plano do teste físico futuro (NÃO executado)

**Instalação:** só SD (5 arquivos), pelo fluxo `pre/copy/verify`.

- O pré-deploy é contra `R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json`.
- O firmware atual (`6e329c91…`) é mantido.

**Roteiro:**

| # | Ação | Esperado |
|---|---|---|
| 1 | Boot | Normal; `REFERENCE_ENGINE cf-reference-engine-run6-juris-j1` |
| 2 | CF art. 1º e art. 3º | **Sem** `2 JURIS.` |
| 3 | CF art. 19, 47, 96 e 98 | **Sem** `2 JURIS.` |
| 4 | CF art. 6º → `2 JURIS.` | Tema 295 presente; Tema 455 ausente |
| 5 | CF art. 5º, XIII → `2 JURIS.` | Tema 455 presente |
| 6 | CF art. 37, XI → `2 JURIS.` | 10 itens; uma ficha abre |
| 7 | CF art. 202, § 5º → `1 CORR.` | LC 108/2001, art. 26 |
| 8 | CF art. 196 → `4 REF.` | Sicko; CF art. 43 → `4 REF.` = Formação Econômica do Brasil |
| 9 | CF art. 127 → `3 ENTENDA` | Abre |

**Rollback:** os 5 arquivos de `rollback/`.

## 6. Próxima missão

```
NEXT_RECOMMENDED_MISSION = J1.2 — DEPLOY CONTROLADO DO CANDIDATO J1.1 (só SD) + TESTE FÍSICO
```

Depois disso:

- **J2:** pesquisa externa para os 4 `EXTERNAL_REVIEW_REQUIRED`, as 5 realocações para o ADCT e o backlog de 148;
- decisão sobre o par redundante (Temas 367/387);
- freeze da camada.
