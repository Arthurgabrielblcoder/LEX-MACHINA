# C3A — implementação host-only do motor CORRELATA

**Status: `RUN4_CANDIDATE_HOST_ONLY`.** Não é baseline nem deploy, e não foi aprovado fisicamente.

- **Intocados:** RUN3, REF_LOOKUP, REF_PAYLOAD, TARGETS, RELACOES do cartão, staging SD e firmware.
- **Princípio:** `LEGAL_APPROVED` ≠ `DEVICE_READY`.

## Arquitetura final

- **Motor genérico:** `LEGAL_TARGET_ID/correlata_overlay.py`, dirigido por dados, sem nenhuma norma, lei ou target no código.
  - Validação jurídica (`validate_record`, fail-closed).
  - Classificação do aparelho (`device_blockers`), separada da validação.
  - Correções do legado (`validate_corrections`).
  - Escritor das tabelas RELACOES e REL_LOOKUP no formato do cartão. Ele reproduz byte a byte as tabelas atuais.
- **Builder:** `LEGAL_TARGET_ID/build_export_run4_candidate.py`.
  - Parte dos links do RUN3, reproduzidos byte a byte pelo motor, e aplica correções e adições.
  - Gera `legal_view/` e `device_ready/` em `derived/export_test/run4_candidate/`.
  - `reference_engine.py` e `engine_config.json` não foram alterados, e o RUN3 continua sendo produzido como antes.
- **Derivação dos dados:** `CORRELATA_COVERAGE_AUDIT/C3A/tools/build_c3a_overlay.py`.
  - Converte as decisões humanas (consolidado HIGH e revisão legada) em registro jurídico, adições e correções. Não decide nada.
- **Correções do legado:** `CF88_CORRELATA_EXCLUSIONS_CANDIDATE.json`, uma por vínculo legado visível. Ações:
  - KEEP;
  - EXCLUDE (REMOVE, REPLACE e RETARGET);
  - ROUTE_FIX, que mantém o mesmo vínculo e corrige a rota só na linha RELACOES candidata;
  - SUPPRESS_HOLD (`REVIEW_HOLD_SUPPRESSED`);
  - SUPPRESS_TEMPORAL (`TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE`, com data `until`).
  - O `CF88_LINK_EXCLUSIONS.json` não foi usado nem editado: o status único dele não representa supressões reversíveis, e o RUN3 depende dele.
- **Adições:** `CF88_CORRELATA_ADDITIONS.json` só aceita `HUMAN_APPROVED_CORRELATA_V1` e, nesta C3A, só destino já no cartão (`DESTINATION_ON_CARD_ONLY`).
- **Política HOLD:** `REVIEW_HOLD_SUPPRESSED` não publica o vínculo, preserva a decisão HOLD e o vínculo continua no catálogo, restaurável.
- **Vacatio:** a relação continua registrada e só aparece a partir de `effective_from`/`until` (política C2 `DO_NOT_PUBLISH_AS_CURRENT`).
- **ADCT:** um target com `UNKNOWN_VALIDITY` só passa se o runtime do aparelho o confirmar: presente, CURRENT ou STRUCTURAL e alcançável no TEXT_MAP. Não há liberação genérica.
- **MAIN_CORPUS:** é validado contra o índice de artigos do acervo principal (pin C0) e serializado com `norm_id`, `source_path`, artigos e fallback.
  - No aparelho fica `BLOCKED_DEVICE_ROUTE_MAIN_CORPUS`, porque o firmware ainda não tem a rota.
  - Nenhuma norma do acervo principal é duplicada em EXT_NORMAS.
- **Status judicial:** exige `status`, `cases`, `decided_on`, `notice_short` e `checked_until`.
  - No aparelho fica bloqueado (`BLOCKED_DEVICE_JUDICIAL_NOTICE_UNSUPPORTED`) até haver UI de aviso.
- **Identidade jurídica:** unidade de apresentação (ART = CAPUT) × norma. A LC 199/2023 × art. 146, III, b gera uma única relação, com as duas decisões.
- **PNE:** os seis vínculos viram um só, no caput do art. 214. `NEXT_STEP = ANNEX_ROUTE_SUPPORT` (Meta 19.a) continua pendente.

## Refinamentos encontrados ao aplicar a C2 aos dados reais

1. **PARTIAL_EFFECTS não judicial.** A LC 214 e a LC 227 têm efeitos escalonados sem nenhuma decisão do STF.
   - O protótipo C2 exigia status judicial para todo PARTIAL_EFFECTS.
   - Agora: com JUDICIAL_RESTRICTIONS, exige status judicial completo; sem, exige `temporal_note` e `revalidate_on` (`PARTIAL_EFFECTS_WITHOUT_BASIS`).
2. **Lacunas no índice de artigos do cartão.** O `EXT_ARTIGOS.IDX` do cartão não tem o art. 10 da LC 87/1996 nem o art. 9º da Lei 7.998/1990, embora os dois estejam no texto.
   - A checagem jurídica usa o texto da norma (`ext_text_article_index.json`, sha do pin); o aparelho usa o índice do cartão.
   - Quando falta o artigo, o aparelho usa o fallback seguro da C2 (abrir a norma sem salto). Casos: 2.
3. **Tipo de relação dos retargets legados.** A revisão legada não classificou o tipo.
   - Esses registros levam `NAO_CLASSIFICADA_REVISAO_LEGADA`, aceito só quando todas as decisões de origem são legadas.
   - Nenhuma decisão jurídica nova foi tomada. Ponto para a revisão independente.
4. **Status judicial da Lei 14.701.** Foi acrescentado `notice_short` ao consolidado HIGH (campo exigido pela política C2). As decisões não mudaram.

## Contagens (derivadas)

| Item | n |
|---|---:|
| ADDITIONS_MATERIALIZED_IN_CANDIDATE | 11 |
| LEGACY_EXCLUSIONS_CANDIDATE | 27 |
| LEGACY_RETARGETS_CANDIDATE | 4 |
| LEGACY_RETARGET_PRESENTATION_NOOP | 1 |
| LEGACY_REPLACED | 5 |
| LEGACY_REMOVED | 18 |
| LEGACY_ROUTE_FIX | 5 |
| LEGACY_KEPT_UNCHANGED | 10 |
| TEMPORAL_SUPPRESSED | 3 |
| REVIEW_HOLD_SUPPRESSED | 1 |
| MAIN_CORPUS_BLOCKED | 21 |
| INGESTION_BLOCKED | 55 |
| JUDICIAL_NOTICE_BLOCKED | 2 |
| ADCT_RUNTIME_CONFIRMED | 2 |
| ADCT_DEVICE_READY | 0 |
| ADDITIONS_DEVICE_READY | 9 |
| RUN4_LEGAL_VIEW_ENTRIES | 133 |
| RUN4_LEGAL_VIEW_LINKS | 103 |
| RUN4_DEVICE_READY_VISIBLE_LINKS | 24 |
| RUN4_DEVICE_HIDDEN_HISTORICAL | 2 |
| DEVICE_ARTICLE_INDEX_GAPS_FALLBACK | 2 |
| Cache do firmware usado (linhas de lookup / normas) | 26 / 15 (limites 64 / 32) |

**Diferenças em relação às estimativas da missão:**

- **HIGH com destino no cartão:** 7. Dois estão em vacatio (Lei 14.965), então 5 são DEVICE_READY.
  - A LC 199 foi colapsada com o retarget legado.
  - Somam-se 4 adições do legado (3 retargets e a substituição LC 63 × art. 161, I): 11 materializadas e 9 DEVICE_READY.
- **MAIN_CORPUS bloqueados:** 21, e não 19. São os 19 HIGH mais 2 substituições do legado (LAI × art. 37, § 3º, II e Lei 8.212 × art. 195, II).
- **INGESTION bloqueados:** 55, e não 51. São os 51 HIGH mais 4 substituições do legado (Lei 7.990; LCs 124, 125 e 129).
- **Retargets legados:** 5 decididos. 4 são efetivos (exclusão e adição); o art. 182 → caput é equivalente na apresentação e fica sem alteração.

## Determinismo e regressões

- **Reprodutibilidade:** RUN4 construído 2 vezes em diretórios temporários limpos; SHA256SUMS idênticos entre si e ao versionado: **True**.
- **RUN3:** reconstruído pelo motor e byte-idêntico ao versionado. Arquivos operacionais sem diferença em relação à baseline (teste 16).
- **Testes antigos:** os que exigiam a ausência de `CF88_CORRELATA_ADDITIONS.json` passaram a exigir que ele seja candidato host-only e que o `engine_config.json` não o referencie.

## Arquivos

- **Criados:**
  - `LEGAL_TARGET_ID/correlata_overlay.py`
  - `LEGAL_TARGET_ID/build_export_run4_candidate.py`
  - `LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json`
  - `LEGAL_TARGET_ID/derived/CF88_CORRELATA_EXCLUSIONS_CANDIDATE.json`
  - `LEGAL_TARGET_ID/derived/export_test/run4_candidate/ (legal_view, device_ready, summary, SHA256SUMS)`
  - `CORRELATA_COVERAGE_AUDIT/C3A/CF88_CORRELATA_LEGAL_REGISTER_CANDIDATE.json`
  - `CORRELATA_COVERAGE_AUDIT/C3A/inputs/ (card_relations_v2, main_corpus_article_index.json, ext_text_article_index.json)`
  - `CORRELATA_COVERAGE_AUDIT/C3A/tools/ (build_c3a_overlay.py, build_c3a_reports.py, freeze_main_corpus_article_index.py)`
  - `CORRELATA_COVERAGE_AUDIT/C3A/ (RUN3_RUN4_CORRELATA_DIFF.md, C3A_IMPLEMENTATION_REPORT.md, C3A_RUN4_CANDIDATE_MANIFEST.json)`
  - `CORRELATA_COVERAGE_AUDIT/tests/test_correlata_c3a_engine.py`
- **Modificados:**
  - `CORRELATA_COVERAGE_AUDIT/tools/build_c1b_high_consolidated.py (+ notice_short) e o consolidado/fechamento regenerados`
  - `CORRELATA_COVERAGE_AUDIT/tests/test_correlata_c1b_batch01.py, _batch02.py, _high_closure.py, test_correlata_c2_prototype.py (asserção do overlay agora candidato)`

## Bloqueios e próximos passos (não iniciados)

- **C3B (aparelho):**
  - teste físico do candidato device_ready: RELACOES, REL_LOOKUP e REF_* candidatos num cartão de teste;
  - corrigir as lacunas do `EXT_ARTIGOS.IDX`.
- **C3C (firmware):**
  - rota `ABRIR_NORMA_PRINCIPAL` para os 21 MAIN_CORPUS;
  - UI do aviso judicial;
  - origem ADCT em RELACOES ainda não verificada no cartão;
  - limite de cache 32/64 para a escala futura.
- **Ingestão:** 55 relações dependem de normas novas. Adiada.
- **Revisão:** o tipo de relação dos 3 retargets legados não classificados.
- **MEDIUM (191) e LOW (446):** não iniciados.

