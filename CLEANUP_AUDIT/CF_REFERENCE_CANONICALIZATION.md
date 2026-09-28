# CF-REF-A2 — Normalização canônica das referências da CF

**Resultado: `CF_REF_A2_CONCLUIDA — REFERENCIAS_CANONICAS_NORMALIZADAS`.**

- A CF-REF-A1 foi versionada: commit `0c2c14794ade9894761f017a629ad62540fc70ac`, tag `cf-target-id-canonical-2026-09-28`.
- Os artefatos da A2 continuam **untracked**, para revisão.
- Nenhuma fonte original foi alterada, e nenhuma referência jurídica nova foi criada.

## 1. Resumo

| Métrica | Valor |
|---|---:|
| TOTAL_SOURCE_REFERENCES | **1.186** |
| VALID_CANONICAL_REFERENCES | **1.130** |
| MIGRATED_AUTOMATICALLY (subdivisão já canônica) | 893 |
| MIGRATED_ARTICLE_TO_CAPUT | 176 |
| KEPT_AS_ARTICLE | 56 |
| Artigo×caput em NEEDS_REVIEW | 36 |
| RESOLVED_COLLISIONS (colisões V2) | 3/3 |
| Inválidos corrigidos com evidência (namespace ADCT) | 2 |
| QUARANTINED_AMBIGUOUS | 0 |
| QUARANTINED_INVALID | 20 |
| OTHER_REVIEW | 0 |
| Quarentena total (36 + 20) | 56 |
| DUPLICATES_EXACT / POSSIBLE_DUPLICATES | 0 / 9 |
| Status do alvo no catálogo: CURRENT / HISTORICAL_ONLY / STRUCTURAL / UNKNOWN_VALIDITY | 991 / 17 / 56 / 66 |

Classificação dos 1.186 registros, que fecha o corpus:

| Classe | Registros |
|---|---:|
| AUTO_MEMBER_MATCH | 893 |
| ARTICLE_VS_CAPUT_RESOLVABLE | 268 |
| AMBIGUOUS_V2_COLLISION | 3 |
| INVALID_TARGET | 22 |
| OTHER_REVIEW_REQUIRED | 0 |

## 2. Corpus e proveniência

Cada registro traz:

- `source_record_id`, `source_file`, `source_layer`, `original_device_key`;
- os campos originais (artigo, parágrafo, inciso, alínea);
- `provenance` e a classificação.

| Camada | Arquivo | Registros | Papel |
|---|---|---:|---|
| V2_RC2_REFERENCES | `LEX_MACHINA_REFERENCIAS_V2/08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED/REFERENCIAS_RC2.json` | 105 | Referências obra×dispositivo com revisão humana (produto) |
| V2_RC1_REFERENCES | `…/CF_REFERENCIAS_V2_RC1/REFERENCIAS_RC1.json` | 125 | Versão superada pelo RC2 |
| V2_ALL_DISTINCT_DEVICE_IDS | `device_id` distintos nos JSON da V2 | 441 | Inventário de auditoria |
| SD_RELATIONS_REL_LOOKUP | `LEX-MACHINA_ETAPA_2E6_SD_TESTE/…/REL_LOOKUP.IDX` | 41 | Índice de correlatas do SD de teste |
| SD_JURIS_J4_6_JUR_LOOKUP | archive (somente leitura) `LEX_MACHINA_JURIS_CF_J4_6/…/JUR_LOOKUP.IDX` | 178 | Índice de jurisprudência do SD de teste |
| SD_JURIS_J4_6_IDS | archive (somente leitura) `…/JURISPRUDENCIA.IDX` + `LEX_MACHINA_JURIS_CF_J4/VINCULOS_EXPLICITOS.json` | 296 | Vínculos de jurisprudência (evidência literal) |

## 3. Artigo × caput (268): decisão por proveniência

A regra não é aplicada às cegas. Cada camada usa a evidência documental que tem:

| Camada | Evidência usada | Caput | Artigo | Revisão |
|---|---|---:|---:|---:|
| RC2 | `texto_dispositivo` (texto que a V2 avaliou) = texto do caput | 27 | 0 | 0 |
| RC1 | idem | 32 | 0 | 0 |
| Inventário V2 | texto do registro V2 (`CF_SEGMENTADA_V2`) = caput. `ART.130-A` tinha caput + incisos, por isso fica como artigo | 106 | 1 | 0 |
| Relations | `origem_scope_editorial` do pacote 2E4.1: "202, caput" → caput; "146" e "182" → artigo inteiro | 1 | 2 | 0 |
| JUR_LOOKUP | citações dos vínculos agregados: todas citam "caput" → caput; todas citam o artigo sem subdivisão → artigo; mistas → revisão | 4 | 17 | 14 |
| IDs de jurisprudência | citação literal do vínculo (mesma regra) | 6 | 36 | 22 |
| **Total** | | **176** | **56** | **36** |

**Motivos registrados:**

| Motivo | Registros |
|---|---:|
| `LEGACY_V2_ARTICLE_KEY_REPRESENTED_CAPUT` | 165 |
| `CITATION_NAMES_ARTICLE_WITHOUT_SUBDIVISION` | 53 |
| `CITATION_NAMES_CAPUT` | 10 |
| `SOURCE_EDITORIAL_SCOPE_IS_WHOLE_ARTICLE` | 2 |
| `SOURCE_EDITORIAL_SCOPE_SAYS_CAPUT` | 1 |
| `LEGACY_V2_TEXT_INCLUDED_CHILD_DEVICES` | 1 |

Os 36 casos de revisão vão para a quarentena com `CITATION_EVIDENCE_MISSING_OR_MIXED` (ex.: citação "art. 5º, caput e I"). Nada foi adivinhado.

## 4. Colisões V2 (3): todas resolvidas com evidência documental

O texto gravado pelo parser antigo começa com o resto do sufixo, e o texto que vem depois é igual ao do dispositivo com sufixo:

| Chave V2 | Texto legado | Resolvido para |
|---|---|---|
| `CF88:ART.239:PAR.3` | "**-A.** O limite para elegibilidade…" (`DISPOSITIVOS_V2_05.json`) | `CF88:ART.239:PAR.3-A` |
| `CF88:ART.40:PAR.4` | "**-C.** Poderão ser estabelecidos…" (`DISPOSITIVOS_V2_06.json`) | `CF88:ART.40:PAR.4-C` |
| `CF88:ART.93:INC.VIII` | "**B -** a permuta de magistrados…" (`BENCHMARK_HUMANO_134.json`, caso B69-034; `CF_SEGMENTADA_V2`) | `CF88:ART.93:INC.VIII-B` |

## 5. Dispositivos inexistentes (22)

Classificados individualmente pela citação literal (`evidencia_vinculo.trecho` / `referencia_detectada`):

| Chave inválida | Citação real | Categoria | Resultado |
|---|---|---|---|
| `CF88:ART.78:PAR.4` (lookup + ID) | "§4º do art. 78 **do ADCT**" (RG 231) | A — extração perdeu o namespace | **Corrigido → `ADCT:ART.78:PAR.4`** (2) |
| `CF88:ART.1:PAR.1` | "§ 1º do artigo 1.361 do **Código Civil**" (RG 349) | C — outra norma (e número truncado) | Quarentena |
| `CF88:ART.3:PAR.3` | "art. 3º, § 3º, da **Lei 10.259/2001**" (RG 1277) | C | Quarentena |
| `CF88:ART.20:PAR.3` | "§ 3º do artigo 20 da **Lei 8.742/1993**" (RG 27) | C | Quarentena |
| `CF88:ART.25:INC.I/II` | "artigo 25, incisos I e II, da **Lei 8.870/1994**" (RG 651) | C | Quarentena |
| `CF88:ART.50:INC.II` | "art. 50, II, da **Lei 8.625/1993**" (RG 966, 976) | C | Quarentena |
| `CF88:ART.65:INC.I` | "art. 65, I, da **LC 35/79**" (RG 966, 976) | C | Quarentena |
| `CF88:ART.92:INC.I:AL.b` | "art. 92, I, 'b', do **Código Penal**" (RG 1200) | C | Quarentena |
| `CF88:ART.94:INC.II` | "art. 94, II, da **Lei 9.472/1997**" (RG 739) | C | Quarentena |

Resultado: **2 corrigidos com evidência** e **20 em quarentena**, todos C, porque o extrator de jurisprudência J4 associou à CF citações de outras normas. Nenhum foi remapeado por proximidade.

**Limitação.** A validação estrutural não detecta uma citação de outra norma que, por coincidência, caia num dispositivo que existe na CF. O detector `OTHER_REVIEW_REQUIRED` (citação que nomeia outra norma sem mencionar a CF) não encontrou casos. Mesmo assim, recomenda-se uma auditoria semântica na A3.

## 6. Catálogos derivados (`LEGAL_TARGET_ID/derived/`)

| Arquivo | Conteúdo | SHA-256 |
|---|---|---|
| `CF88_REFERENCES_CANONICAL.json` | 1.130 registros válidos | `89bd39c4…` |
| `CF88_REFERENCES_QUARANTINE.json` | 56 registros | `38fe75ef…` |
| `CF88_TARGET_STATUS.json` | Status de cada um dos 3.956 targets | `5b88efeb…` |
| `CF88_GOLDEN_CORPUS.json` | Corpus-ouro | `84a0bafb…` |

**Campos de cada registro canônico:**

- `reference_id`, `target_id`, `target_scope`;
- `target_status` e `target_present_in_operational_text`;
- `reference_type` e `catalog_role` (PRODUCT_REFERENCE_RC2, SUPERSEDED_BY_RC2, AUDIT_INVENTORY, SD_TEST_INDEX, SD_TEST_JURISPRUDENCE);
- `label`, `source_layer`, `source_file`, `source_record_id`, `original_device_key`, `provenance`;
- `migration_status`, `migration_reason`, `validation_status`, `duplicate_class`;
- `legal_fields_preserved`, com todos os campos jurídicos originais do RC1/RC2.

**Gate.** `validate_reference_record()` exige, com fail-closed:

- `validate_target_id`;
- o target presente no índice;
- os campos obrigatórios.

Foi aplicado a 100 % do catálogo e deve ser obrigatório para qualquer referência nova.

**Quarentena.** Cada registro traz:

- o registro original;
- `reason_code` e `invalid_category`;
- `candidate_targets` e `evidence`;
- `manual_review_required=true`.

Nenhum registro da quarentena está no catálogo.

**Determinismo:** duas execuções geraram canonical, quarantine e status byte-idênticos.

## 7. Fonte estrutural × texto vigente

| Papel | Fonte |
|---|---|
| **STRUCTURAL_CANONICAL_SOURCE** | `cf.txt` do catálogo mestre (Planalto; SHA-256 `d9f3d6b9…`): identidade estrutural, compatibilidade histórica com a V2, contém ADCT |
| **OPERATIONAL_CURRENT_TEXT_SOURCE** | `updater/saida/1- CONSTITUIÇÃO FEDERAL/constituicao_federal_1988.txt` (Senado monovigente; `3100e097…`): texto vigente mostrado ao usuário, **sem ADCT** |

O `target_id` não depende dos bytes de nenhuma das duas fontes.

**Status (`CF88_TARGET_STATUS.json`):**

| Status | Targets | Critério |
|---|---:|---|
| CURRENT | 2.644 | 2.642 com o rótulo no texto vigente; 2 só com o texto |
| HISTORICAL_ONLY | 74 | 58 ausentes do texto vigente; 16 **renumerados** (ex.: `CF88:ART.102:PAR.UNICO` → vigente `CF88:ART.102:PAR.1`) |
| STRUCTURAL | 426 | Norma, namespace e artigos |
| UNKNOWN_VALIDITY | 812 | ADCT, que não tem texto vigente disponível |

**Targets históricos não são apagados.** Das referências do catálogo, 17 apontam alvos HISTORICAL_ONLY, e todas estão marcadas com `target_status` e `target_present_in_operational_text=false`. Exemplos:

- `CF88:ART.40:PAR.4:INC.II/III`: redação da EC 47/2005, citada por correlatas (LC 144/2014) e por jurisprudência;
- `CF88:ART.114:INC.VIII`;
- `CF88:ART.40:PAR.7:INC.I`.

Nenhuma dessas referências aparece como vigente.

## 8. Deduplicação

- **Chave lógica:** `(source_layer, target_id, reference_type, subject_id)`, onde `subject_id` é o `work_id` ou o tema de jurisprudência.
- **EXACT_DUPLICATE:** 0.
- **SEMANTIC_POSSIBLE_DUPLICATE:** 9. São rotas múltiplas do mesmo vínculo obra×dispositivo (RC2: 105 rotas/101 vínculos; RC1: 125/120), que fazem parte do desenho da V2. Foram marcadas, não removidas.
- **RC1 × RC2:** são versões, não duplicatas.

## 9. Corpus-ouro (`CF88_GOLDEN_CORPUS.json`)

| Artigo | Alvos de lei seca | Referências (por tipo) | Migração |
|---|---|---|---|
| CF88:ART.1 | caput, 5 incisos, parágrafo único | 7 obras RC2, 6 jurisprudências, 3 índices de jurisprudência, 4 menções V2, 8 RC1 | 25 automáticas, 1 caput, 2 artigo |
| CF88:ART.5 | caput, 79 incisos, 24 alíneas, 4 parágrafos | 35 obras RC2, 23 jurisprudências, 15 índices de jurisprudência, 1 correlata, 39 menções, 43 RC1 | 150 automáticas, 6 caput |
| CF88:ART.37 | caput, 28 incisos, 16 parágrafos, 3 alíneas | 27 jurisprudências, 10 índices de jurisprudência, 4 correlatas, 15 menções | 53 automáticas, 3 caput |
| CF88:ART.60 | caput, 5 parágrafos, 7 incisos (§4º I–IV) | 1 menção | 1 automática |
| CF88:ART.150 | caput, 6 incisos, 8 alíneas, 7 parágrafos | 21 jurisprudências, 7 índices de jurisprudência, 1 correlata, 1 menção | 30 automáticas |
| CF88:ART.225 | caput, 7 parágrafos, 8 incisos | 2 obras RC2, 3 RC1, 8 menções | 8 automáticas, 5 caput |
| ADCT:ART.5 | caput, 5 parágrafos | nenhuma | — |

**Alvos-chave:**

| Target | Status | Referências |
|---|---|---:|
| `CF88:ART.37:CAPUT` | CURRENT | 3 |
| `CF88:ART.37:PAR.6` | CURRENT | 6 |
| `CF88:ART.37:PAR.10` | CURRENT | 1 |
| `CF88:ART.60:PAR.4:INC.IV` | CURRENT | 0 |
| `ADCT:ART.5:PAR.1` | UNKNOWN_VALIDITY | — |

**Testes permanentes** (`LEGAL_TARGET_ID/tests/test_reference_canonicalization.py`, 13 testes; suíte total 31/31 OK):

- art. 37 caput, § 6 e § 10;
- art. 60, § 4º, IV;
- ADCT art. 5;
- artigo inteiro × caput;
- gate de target inválido;
- colisão V2 (só com resto do sufixo + texto);
- inválidos em quarentena e correção ADCT;
- `HISTORICAL_ONLY`;
- inciso e parágrafo com sufixo;
- fechamento do corpus;
- corpus-ouro.

## 10. Firmware (não alterado)

**`FIRMWARE_NAMESPACE_FIX_REQUIRED = true`.**

- **Problema:** `chaveContextoAtual()` monta `artigo|paragrafo|inciso|alinea` sem namespace. Com o ADCT, o art. 5º da CF e o art. 5º do ADCT colidem. Os lookups do SD também fixam `CF88`.
- **Formato mínimo proposto:**
  - chave de contexto = `target_id` canônico (`CF88:ART.5:INC.LXXVIII`, `ADCT:ART.5:PAR.1`), em `char[40]`;
  - namespace definido pelo arquivo ou seção aberta;
  - `ORIGEM_NORMA` dos IDX aceitando `ADCT` (`to_pipe_fields` já produz `ADCT|5|1||`);
  - contexto no texto do caput = `…:CAPUT`;
  - referências de artigo inteiro exibidas em todo o artigo.

## 11. ADCT no SD (não alterado)

**`OPERATIONAL_CF_TEXT_MISSING_ADCT = true`.** Opções:

- **A)** incorporar o ADCT ao arquivo atual da CF;
- **B)** arquivo separado do ADCT;
- **C)** outra organização (ex.: pasta própria).

**Recomendação: B.** O namespace fica inequívoco por arquivo, não se reintroduz a colisão de numeração no mesmo arquivo, e o texto vigente da CF não muda. Antes de publicar, são necessárias a fonte monovigente do ADCT e a correção de namespace do firmware.

## 12. Arquivos da A2 (untracked)

| Arquivo | Conteúdo |
|---|---|
| `LEGAL_TARGET_ID/reference_canonicalization.py` | Regras, gate, status, catálogos |
| `LEGAL_TARGET_ID/build_golden_corpus.py` | Gerador do corpus-ouro |
| `LEGAL_TARGET_ID/tests/test_reference_canonicalization.py` | Testes da A2 |
| `LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json`, `CF88_REFERENCES_QUARANTINE.json`, `CF88_TARGET_STATUS.json`, `CF88_GOLDEN_CORPUS.json` | Catálogos derivados |
| `CLEANUP_AUDIT/CF_REFERENCE_CANONICALIZATION.md` / `.json` | Este relatório |

## 13. Recomendação para CF-REF-A3 (não iniciada)

1. **Revisão humana da quarentena**, apoiada pelas evidências já anexadas:
   - 36 casos artigo×caput com citação mista (ex.: "art. 5º, caput e I" poderia gerar dois vínculos);
   - 20 citações de outra norma: remover da CF e, no futuro, associar à norma correta, quando ela existir no acervo.
2. **Auditoria semântica dos vínculos de jurisprudência** que caem em alvos válidos (risco de outra norma coincidir com a CF).
3. **Decidir o destino das referências a alvos HISTORICAL_ONLY** (exibir como histórico ou migrar para o sucessor com evidência).
4. **Tornar `validate_reference_record` obrigatório** nos geradores de Referências, Correlatas e Jurisprudência.
5. **Especificar** o arquivo ADCT separado e a chave de firmware com namespace. Só depois disso, pensar em SD/firmware.
