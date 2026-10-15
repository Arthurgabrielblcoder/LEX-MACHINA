# REFERÊNCIAS Nº 4 — CF: checkpoint de retomada (R0)

```
LAYER = REFERENCES_4_CF
MISSION = R0 — inventário e reconstrução de estado (host, somente leitura)
DATE = 2026-10-15
STATE = PUBLICADA_NO_DEVICE (RUN3), SEM FREEZE FORMAL DA CAMADA
LATEST_VALID_CHECKPOINT = RUN3 / REFERENCE_EXPANSION_01
CHECKPOINT_COMMIT = 10e199f (tag lex-device-v1-batch04-run3-physical-approved-2026-10-03)
DEVICE_BASELINE_IN_FORCE = C3B.2 (74c6662, tag lex-device-v1-correlata-c3b2-physical-approved-2026-10-12)
```

Este documento foi produzido sem alterar dados, código, firmware, índices ou o microSD. Os números abaixo foram recontados a partir dos artefatos versionados (`git show` e leitura direta). Não são números de memória de conversa.

## 1. Estado atual

A camada 4 REFERÊNCIAS (vínculos `WORK_REFERENCE` obra ↔ dispositivo) **já está publicada e fisicamente aprovada no aparelho** desde o RUN3 (03/10/2026). O conteúdo de obras seguiu idêntico em todas as promoções físicas posteriores (ENTENDA 810 e CORRELATA C3B.2).

| Item | Valor |
|---|---|
| Vínculos `WORK_REFERENCE` publicados (`CURRENT_VISIBLE`) | **122** |
| Targets canônicos com obra (= targets com flag `W`) | **63** |
| Artigos distintos da CF com obra | **33** |
| ADCT com obra | 1 target (ADCT art. 68) |
| Obras usadas / registry oficial | **54 / 73** |
| Vínculos aguardando decisão humana | **0** |
| Aprovados retidos (obra sem identidade no catálogo) | **2** |

Falta um fechamento formal da camada (freeze/baseline próprio, como o de Correlatas 1). Restam também duas aprovações retidas e um catálogo candidato de 199 obras que ainda não foi integrado.

## 2. Último checkpoint válido

**RUN3 / REFERENCE_EXPANSION_01**, commit `10e199f`, 2026-10-03, tag `lex-device-v1-batch04-run3-physical-approved-2026-10-03`. `PHYSICAL_HUMAN_VALIDATION = APPROVED`.

Artefatos:

- `LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json`: overlay de 21 vínculos, `HUMAN_APPROVED_REFERENCE_V1`.
- `REFERENCE_COVERAGE_AUDIT/REFERENCE_EXPANSION_ROUND1_DECISIONS.json`: `status FINAL`, 2026-10-02.
- `REFERENCE_REGISTRY/WORK_REGISTRY_V2.json`: `OFFICIAL_REGISTRY`, 69 → 73 obras.
- `LEGAL_TARGET_ID/derived/export_test/run3/`: `CF88_REFERENCES_EXPORT.json`, `REF_LOOKUP.IDX`, `REF_PAYLOAD.IDX`, `RUN3_MANIFEST.json`, `SHA256SUMS.txt`.
- `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h`: header rico com 122 fichas, promovido como baseline.
- `DEVICE_INTEGRATION/BATCH04_RUN3_PHYSICAL_VALIDATION_REPORT.md`.

A conferência foi feita por byte. As 122 linhas `WORK_REFERENCE` do `REF_PAYLOAD.IDX` do RUN3 são idênticas às do pacote físico C3B.2 (`CORRELATA_COVERAGE_AUDIT/C3B2_PHYSICAL_TEST_PACKAGE/candidate/SD/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX`). Nenhuma rodada posterior alterou obras.

## 3. Fontes autoritativas

```
AUTHORITATIVE_REFERENCE_SOURCE =
  (a) LEX_MACHINA_REFERENCIAS_V2/08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED/REFERENCIAS_RC2.json  (101 vínculos base; ledger DECISOES_HUMANAS.json, sha 8e72e7cd…)
  (b) LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json  (+21 vínculos REFERENCE_EXPANSION_01)
  (c) REFERENCE_REGISTRY/WORK_REGISTRY_V2.json  (73 obras oficiais)
  (d) REFERENCE_COVERAGE_AUDIT/REFERENCE_EXPANSION_ROUND1_DECISIONS.json  (25 decisões, lacunas confirmadas)
Gerador: LEGAL_TARGET_ID/reference_engine.py + engine_config.json + build_export_run3.py
         (+ CF88_LINK_EXCLUSIONS.json, que exclui apenas jurisprudência)
Materialização vigente: REF_PAYLOAD/REF_LOOKUP do baseline C3B.2 (linhas WORK_REFERENCE = RUN3)
```

**Por quê:**

- O `CF_REFERENCE_CANONICALIZATION` (A2, `85597db`) declara o RC2 como a camada-fonte "produto" das obras e o RC1 como "superado".
- O motor (A3, `9fcab70`) exporta somente RC2.
- O RUN3 (`10e199f`) soma o overlay (b), validado *fail-closed* contra o registry (c).
- Os testes `LEGAL_TARGET_ID/tests/test_reference_run3.py` e `DEVICE_INTEGRATION/tests/test_reference_run3_device.py` fixam o header do sketch no RUN3.
- O gerador `tools/build_ref_detail_header.py --check` reproduz o header aprovado a partir de RUN3 `REF_PAYLOAD.IDX` + ADDITIONS.

## 4. Inventário

### Obras

| Categoria | n | Fonte |
|---|---:|---|
| Registry oficial (cadastradas) | **73** | `WORK_REGISTRY_V2.json` (69 base + 4 promovidas: EXP2-LIV-040, EXP2-FIL-039, EXP2-FIL-006, EXP2-FIL-038) |
| Efetivamente usadas (com ≥1 vínculo publicado) | **54** | SOURCE_ID distintos `WORK_REFERENCE` no REF_PAYLOAD |
| No registry sem vínculo ativo | **19** | 73 − 54 |
| Aprovadas mas fora do registry (sem identidade) | 2 | SOS Saúde (Sicko) → art. 196; Pro Dia Nascer Feliz → art. 206, I |
| Catálogo candidato não integrado | 199 utilizáveis (28 APTA, 171 APTA_COM_RESSALVA, 1 duplicata rejeitada) | `09_CATALOGO_EXPANSAO_200/06_RELATORIOS/METRICAS_FINAIS.json`; 4 delas já promovidas ao registry |
| Obras usadas em mais de 1 vínculo | 30 | — |

Os 292 *evidence cards* do pacote `ENRIQUECIDO_V1` têm todos `not_targeted_to_device = true`. São evidência de obra, não vínculos.

### Vínculos (estados realmente usados no projeto)

| Rodada | Total decidido | Aprovados | Rejeitados | Pendentes |
|---|---:|---:|---:|---:|
| RC1 → RC2 (revisão humana `REVISAO_HUMANA_RC1_FINAL_V1`) | 120 vínculos / 125 rotas | 101 vínculos / 105 rotas | 19 vínculos integrais + 1 rota (Eu, Daniel Blake → art. 6, saúde) | 0 |
| REFERENCE_EXPANSION_01 | 25 propostas | 23 (20 APPROVE + 3 ADJUST_APPROVE) | 2 (`REJECTED_EDITORIAL_WEAK_CONNECTION`: Borgen → art. 76; Argentina, 1985 → art. 142) | 0 |
| **Total** | **145** | **124** | **21** | **0** |

- **Publicados (DEVICE_READY):** 122 = 101 + 21. Os dois restantes são `APPROVED_PENDING_WORK_IDENTITY`, retidos fora do export.
- **Rotas vs. vínculos:** o export agrupa `(target, work_id)` com `routes[]`. As 105 rotas do RC2 viram 101 linhas.
- **Lacunas confirmadas** (`CONFIRMED_REFERENCE_GAP`, decisão editorial e não pendência): CF art. 98 e art. 202.
- **Visibilidade:** todos os 122 são `CURRENT_VISIBLE` (120 `CURRENT` e 2 `STRUCTURAL`).

### Cobertura (`COVERED_TARGETS = 63`)

| Nível do target | n |
|---|---:|
| Inciso | 33 |
| Caput | 19 |
| Parágrafo | 9 |
| Artigo sem subdivisão | 1 |
| ADCT | 1 |

Esses 63 targets estão distribuídos por 33 artigos da CF e 1 artigo do ADCT. A cobertura é um dado e não meta de qualidade. A política da camada (`REFERENCE_EXPANSION_PLAN_CF88.md`) rejeita forçar obra em todo artigo.

## 5. Histórico obsoleto: NÃO usar para continuar

| Artefato | Por quê |
|---|---|
| `LEX_MACHINA_REFERENCIAS_V2/08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1/` (120 vínculos / 125 rotas / 49 dispositivos / 36 obras) | Superado pelo RC2. São exatamente os "números históricos" da memória. |
| `LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/RESUME_STATE.json` e `RESUME_INSTRUCTIONS.md` | Estado congelado em `R1C_CURATION_IN_PROGRESS` (24–25/09), nunca atualizado após R1D/R1D1/RC2. |
| `LEX_MACHINA_REFERENCIAS_V2/README.md` ("nenhuma integração de produto autorizada") | Superado pelas missões CF-REF A2/A3 e pelo RUN3 integrado. |
| `LEGAL_TARGET_ID/derived/export_test/run1/`, `run2/` | Superados pelo RUN3 (preservados para regressão). |
| `LEGAL_TARGET_ID/derived/export_test/run3/RUN3_SUMMARY.md` ("CANDIDATO — pendente de revisão") | O rótulo é anterior à aprovação física do commit `10e199f`. |
| `REFERENCE_COVERAGE_AUDIT/REFERENCE_EXPANSION_PLAN_CF88.md`, `REFERENCE_EXPANSION_REVIEW.md` (status PENDING_HUMAN_REVIEW) | Decididos em `REFERENCE_EXPANSION_ROUND1_DECISIONS.json` (FINAL). |
| Engine V1.x e validações alpha (`LEX_MACHINA_REFERENCIAS_ENGINE_V1*`, `_VALIDACAO_V14_ALPHA*`, `_BENCHMARK_*`, `_CATALOGO_LOTE_45_V2`, etc., quase todos *untracked*, 21–23/09) | Linha anterior à V2. `ADAPTADOR_CATALOGO_69_V1` registra que a V1.3.2 não lê catálogo. |
| Pipeline R1C/R1D/R1D1 (engine V2) | Proveniência do RC1. O RC2 é seleção humana e não mudança de engine. Não reexecutar. |

## 6. Pendências reais

1. **Revisão humana pendente:** nenhuma. Todas as 145 decisões existentes estão fechadas.
2. **Aprovados retidos:** 2 vínculos aprovados aguardam ingestão de identidade de obra no registry: SOS Saúde (Sicko) → `CF88:ART.196` (score 7,4) e Pro Dia Nascer Feliz → `CF88:ART.206:INC.I` (score 8,0).
3. **Lacunas editoriais:** apenas as já tratadas. Arts. 98 e 202 são lacunas confirmadas. O catálogo de 199 obras candidatas e as 19 obras do registry sem vínculo são **reserva**, não dívida. Não há artefato que aponte dispositivo específico com "forte razão" pendente.
4. **Qualidade:** as auditorias existentes (seção 9) não deixaram item aberto. Não existe auditoria de qualidade *pós-publicação* dos 122 vínculos em conjunto: 101 foram revisados no RC2 e 21 na EXPANSION_01, em lotes separados.
5. **Técnico/higiene:**
   - **Não existe freeze formal da camada.** Não há documento equivalente a `CORRELATAS_1_CF_FROZEN.md` nem tag própria de Referências.
   - `RESUME_STATE.json` da V2 está desatualizado.
   - Há 3 arquivos *untracked* de coleta bruta em `09_CATALOGO_EXPANSAO_200`: `03_FONTES/BUSCA_118.json`, `06_RELATORIOS/CONSULTA_CP11.txt` e `CONSULTA_CP12.txt`, com texto de páginas de terceiros. O relatório de enriquecimento os marca para auditoria de limpeza.
6. **Integração DEVICE:** já funciona (seção 7). Qualquer vínculo novo exige um novo ciclo de export e implica tocar arquivos compartilhados com Correlatas 1 (seção 8).

## 7. Estado DEVICE

**CAMADA EDITORIAL:** RC2 + ADDITIONS + registry, com 124 aprovados, dos quais 122 publicados.

**CAMADA DEVICE: já existe e foi aprovada fisicamente.**

- **Firmware** (`LEX_MACHINA_DEVICE_V1_CANDIDATE.ino`):
  - tecla/rodapé `4 REFERÊNCIAS` (`TELA_REFERENCIAS`);
  - classificador `lexV1ClassificarDestino`: só `WORK_REFERENCE` `CURRENT_VISIBLE` vai para a camada 4;
  - leitura `lexv1References` sobre `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` + `REF_PAYLOAD.IDX`.
- **Header:** `lex_ref_detail_data.h` traz 122 fichas ricas (metadados editoriais). Essas fichas ficam no flash (`.flash.rodata`), não no SD.
- **Flag W:** em `CF88_TARGETS.IDX`, o campo 3 (`flags`, 6 caracteres) usa `flags[3] == 'W'` ⇔ o target tem `WORK_REFERENCE` visível. As posições são `[0]` E/B ENTENDA, `[1]` C CORRELATA, `[2]` J JURISPRUDENCE e `[3]` W WORK_REFERENCE.
  - No baseline C3B.2 há **63 targets com W**, exatamente os 63 targets com obra do RUN3.
  - Esses W vêm do RUN3, isto é, de RC2 + ADDITIONS. O RUN3 alterou as flags de 22 targets (21 vínculos novos mais o efeito do ART↔CAPUT).
- **Testes:** `test_reference_run3.py`, `test_reference_run3_device.py` e o self-test de boot `references_single_result`, hoje em `CF88:ART.127`.
- **Validação física RUN3:**
  - arts. 37, 43, 62, 201 I, 7 XXXIII e ADCT 68: PASS;
  - art. 193 com W e 3 obras: PASS;
  - arts. 98 e 202 sem obra: PASS.
- **Falta:** nada para a funcionalidade atual.
  - Uma futura inclusão de vínculos exigirá regenerar `REF_LOOKUP`, `REF_PAYLOAD` e `CF88_TARGETS.IDX` (flag W).
  - Também exigirá regenerar `lex_ref_detail_data.h`, o que significa **recompilar e gravar o firmware**.
  - Isso dependerá de missão específica com deploy físico.

## 8. Guardrails

- **Correlatas 1 está congelada** (`CORRELATA_COVERAGE_AUDIT/CORRELATAS_1_CF_FROZEN.md`, commit `af8f68d`). Não alterar:
  - as linhas `CORRELATA` de `REF_*`;
  - a flag `C` de `CF88_TARGETS.IDX`;
  - `RELACOES`/`REL_LOOKUP`/`EXT_ARTIGOS`, decisões, registry, manifestos e o pacote C3B.2.
- **Risco de arquivo compartilhado:** `REF_LOOKUP.IDX`, `REF_PAYLOAD.IDX` e `CF88_TARGETS.IDX` contêm Correlatas e Obras ao mesmo tempo. Um export de Referências precisa partir do baseline C3B.2 e provar que:
  - as linhas `CORRELATA` (24 visíveis + 2 ocultas) e `JURISPRUDENCE` (277 + 6) ficam idênticas byte a byte;
  - as flags `[0]`, `[1]` e `[2]` não mudam.

  Se não for possível, PARAR e tratar como reabertura explícita.
- **Atenção de branch:** o `HEAD` desta inspeção (`batch06-scale-cloud`, `3cc0cfc`) é **ancestral** de `cf-correlata-coverage-audit` e **não contém** o baseline C3B.2. O índice gerado a partir do RUN3 puro tem 44 correlatas visíveis, contra 24 no C3B.2. Gerar a partir dele **regrediria Correlatas 1**.
- **Não reabrir:** o holdout da V2, o ledger RC2 ou as regressões R1/R1B/R1C/R1D/R1D1.
- **Não preencher lacunas artificialmente:** QUALIDADE > QUANTIDADE. Arts. 98 e 202 são lacunas confirmadas.

## 9. Auditorias de qualidade já existentes (não refazer)

| Auditoria | Arquivo | Resultado |
|---|---|---|
| Revisão humana do RC1 | `LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/REVISAO_HUMANA_RC1_FINAL_V1.{json,md}`; `09_RELATORIOS/RELATORIO_CONSOLIDACAO_RC2_HUMANA.md` | 120 → 101; 19 rejeições. Escopo afirmado/não afirmado em todas as rotas. Concentração: HHI 0,0364, top1 6,9 %. Determinismo em 2 gerações. |
| Canonicalização de targets | `CLEANUP_AUDIT/CF_REFERENCE_CANONICALIZATION.md` | 9 possíveis duplicatas = rotas distintas; 0 duplicatas exatas. |
| Motor / export | `CLEANUP_AUDIT/CF_REFERENCE_ENGINE_FINAL.md` | Gate *fail-closed*; export determinístico. |
| Cobertura e correção de afirmação | `REFERENCE_COVERAGE_AUDIT/PREVIOUS_REFERENCE_CLAIM_CORRECTION.md`, `REFERENCE_WORK_COVERAGE_FULL.md`, `_RUN3.md` | A antiga lista de "17 artigos com obra" misturava jurisprudência e correlata. Arts. 37, 43, 62, 98, 201 e 202 não tinham obra. |
| Expansão 01 | `REFERENCE_EXPANSION_ROUND1_DECISIONS.json` | 2 conexões fracas rejeitadas; 2 lacunas confirmadas. |
| Catálogo 200 / enriquecimento | `09_CATALOGO_EXPANSAO_200/06_RELATORIOS/RELATORIO_FINAL.md`, `RELATORIO_ENRIQUECIMENTO_V1.md`, `DEDUPLICACAO_EVIDENCE_CARDS_V1.md`, `REDUNDANCIA_69_MAIS_200.md` | Gate PASSA. 0 duplicações confirmadas. Amostra de 20 cards sem problema importante. |

## 10. Divergências encontradas

1. **Memória vs. repositório:** "120 / 125 / 49 / 36" corresponde ao **RC1** (`METADADOS_RC1.json`: 120 vínculos únicos, 125 referências; 49 `device_id` e 36 obras recontados). O estado aprovado posterior é RC2 (101/105/43/35) e, depois, RUN3 (122 vínculos / 63 targets / 54 obras).
2. **Contagem de obras:** RC1 tinha 36 obras e RC2 tem 35, porque uma obra perdeu todos os vínculos na revisão humana. No RUN3 são 54 obras = 35 + 19 obras que entraram com a EXPANSION_01 (21 vínculos novos, dos quais 2 reutilizam obras já presentes no RC2). Não é divergência: são estados sucessivos.
3. **Rótulos defasados:** `RUN3_SUMMARY.md` ("CANDIDATO"), `RESUME_STATE.json` da V2 (R1C) e `CF_REFERENCE_ENGINE_FINAL.md` ("exportador de obras não existe; tela provisória") ficaram desatualizados. O estado real os superou.
4. **Correlatas nos índices:** são 44 visíveis no RUN3 e 24 no C3B.2. Essa diferença é da camada Correlatas 1 e não afeta obras (linhas `WORK_REFERENCE` idênticas).

## 11. Próxima missão recomendada (não iniciada)

```
R1 — Fechar as 2 aprovações retidas (ingestão de identidade das obras SOS Saúde/Sicko e
     Pro Dia Nascer Feliz no WORK_REGISTRY) e preparar, host-only e a partir do baseline
     C3B.2, um RUN candidato com prova de invariância das linhas CORRELATA/JURISPRUDENCE
     e das flags E/C/J — sem deploy, sem firmware.
```

**Justificativa:** é a única pendência editorial com decisão humana já tomada e não materializada. Não há vínculos aguardando decisão, e a expansão por catálogo é opcional (reserva).

Se se preferir não mexer no aparelho agora, a alternativa é fechar formalmente a camada como está, com freeze dos 122 vínculos. O R1 acima, porém, resolve a última pendência objetiva antes desse freeze.
