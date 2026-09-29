# ENTENDA-CF-A2: T1 aprovado e Production Batch 01 (arts. 1º a 5º)

Data: 2026-09-28. Os dados completos estão em `CLEANUP_AUDIT/ENTENDA_CF_PRODUCTION_BATCH_01.json` e em `ENTENDA_ENGINE/derived/production_batch_01/SELECTION_REPORT.json`.

## Parte 1: revisão do piloto e aprovação do T1 (versionada)

| Item | Resultado |
|---|---|
| HEAD inicial | `9fcab702a9b6467b71949071ba34741e940e366d`. Nada alterado nos arquivos versionados; staging vazio; 47/47 e 18/18 antes de começar |
| Ajustes humanos | 5 ajustes, em `ART.5`, `ART.37:PAR.6`, `ART.60:PAR.4:INC.IV`, `ART.225` e `ADCT:ART.10:INC.II`. Foram necessárias 3 mudanças mínimas de coerência no `ART.37:PAR.6`: exemplo, termo "Nexo causal" e vigência externa do ADCT |
| Evidência | O rascunho original foi preservado. As versões 1 alteradas ficaram como `RETIRED` + `superseded_by`. O diff está em `ENTENDA_ENGINE/derived/CF88_PILOT_HUMAN_REVIEW_DIFF.json` |
| Vigência do ADCT | `UNKNOWN_VALIDITY` no texto operacional. Com `external_verification`, passa a `CURRENT_OFFICIAL_EXTERNAL` (`current_in_operational_source=false`, `current_official_external=true`, nenhum hash web armazenado) |
| Piloto | 11 explicações `HUMAN_APPROVED_T1`. Build `ENTENDA_ENGINE/derived/pilot_t1`, repetido duas vezes, BYTE_IDENTICAL |
| **ENTENDA_T1_STATUS** | **APPROVED** (`ENTENDA_ENGINE/ENTENDA_T1_EDITORIAL_STANDARD.md`) |
| Commit / tag | `8ad6714988675e9e3ae71d6268a59f1530612f00` — "feat: establish approved ENTENDA editorial engine"; tag `entenda-t1-approved-2026-09-28`. Sem push |

O build canônico ficou em `derived/pilot_t1/`, e não em `build/`, porque o `.gitignore` do repositório ignora `build/`.

Mudanças no motor, versionadas no commit:

- `covered_targets` para blocos de irmãos reais;
- lookup com a coluna `MATCH` (EXACT ou COVERED);
- estados de revisão `HUMAN_APPROVED_T1` e `CHANGES_REQUESTED`;
- versões anteriores mantidas como RETIRED;
- `external_verification` de vigência;
- lint consultivo (`lint()`).

## Parte 2: Production Batch 01 (untracked, para revisão)

### Números

| Métrica | Valor |
|---|---|
| Targets avaliados | 138 (arts. 1º a 5º, todos os níveis) |
| Targets CURRENT | 138 |
| Históricos excluídos | 0 (nenhum dispositivo histórico no escopo) |
| Selecionados, com explicação própria | 53 |
| Reutilizados do piloto | 2 (`CF88:ART.1`, `CF88:ART.5`; `HUMAN_APPROVED_T1`, sem duplicar) |
| **Novas explicações** | **51** (`PENDING_HUMAN_REVIEW`) |
| Total do lote | 53 |
| Novas por papel | OVERVIEW 3 · DEVICE 1 · BLOCK 21 · ITEM 26 |
| NO_SEPARATE_EXPLANATION | 85: 31 irmãos cobertos por bloco, 18 subdivisões de bloco, 6 subdivisões de irmão coberto, 30 cobertos pela visão geral do artigo |
| Média de palavras (novas) | 205 (mínimo 123 no `INC.LXXVIII`; máximo 292 no `INC.XLII`) |
| Média de bytes (novas) | 1.655 |
| Maior explicação nova | `CF88:ART.5:INC.XLII` (2.484 bytes). A maior do lote é a visão geral do `ART.5` (2.744) |
| Payload | `ENTENDA_PAYLOAD.DAT` com 89.501 bytes (novas: 84.389) |
| Lookup | `ENTENDA_LOOKUP.IDX` com 9.013 bytes e 84 linhas (53 EXACT e 31 COVERED) |
| Targets com referências | 27 dos 53 explicados (`reference_count`, sem usar o conteúdo das referências) |
| Avisos de lint | 44 (detalhados abaixo) |

As 51 novas ficam acima da meta flexível de 20–45 e abaixo do teto de 60. A justificativa registrada é que o art. 5º tem 79 incisos de alta autonomia. Cortar mais exigiria fundir institutos distintos, como habeas corpus com mandado de segurança ou devido processo legal com contraditório, ou excluir dispositivos relevantes só para reduzir o número.

### Art. 5º: estratégia de granularidade

- **Avaliados:** 109 targets (caput, 79 incisos, 25 alíneas e 4 parágrafos).
- **Explicações próprias:** 49 — 1 visão geral reutilizada, 1 DEVICE (§ 3º), 21 BLOCK e 26 ITEM.
- **Sem explicação própria:** 60.

Os 79 incisos não viraram 79 explicações.

A seleção partiu do texto:

- **ITEM:** dispositivos com regra própria e alto uso, como:
  - legalidade (II), tortura (III), intimidade (X), casa (XI), sigilo (XII), profissão (XIII), locomoção (XV) e reunião (XVI);
  - consumidor (XXXII), informação (XXXIII), inafastabilidade (XXXV) e segurança jurídica (XXXVI);
  - devido processo legal (LIV), contraditório (LV), provas ilícitas (LVI), presunção de inocência (LVII), ação privada subsidiária (LIX) e publicidade processual (LX);
  - prisão civil (LXVII), habeas corpus (LXVIII), mandado de injunção (LXXI), ação popular (LXXIII), erro judiciário (LXXV), duração razoável do processo (LXXVIII) e proteção de dados (LXXIX).
- **BLOCK de irmãos** (`covered_targets`, sempre um target principal real):
  - expressão (IV + V, IX, XIV);
  - crença (VI + VII, VIII);
  - associação (XVII + XVIII–XXI);
  - propriedade (XXII + XXIII, XXVI);
  - desapropriação e requisição (XXIV + XXV);
  - propriedade intelectual (XXVII + XXVIII, XXIX);
  - herança (XXX + XXXI);
  - juiz natural (XXXVII + LIII);
  - legalidade penal (XXXIX + XL);
  - crimes com tratamento constitucional (XLII + XLI, XLIII, XLIV);
  - pena (XLVI + XLV);
  - presos (XLIX + XLVIII, L);
  - extradição (LI + LII);
  - prisão (LXI + LXV, LXVI);
  - direitos do preso (LXIII + LXII, LXIV);
  - mandado de segurança (LXIX + LXX);
  - assistência e gratuidades (LXXIV + LXXVI, LXXVII).
- **BLOCK com alíneas:** petição e certidões (XXXIV), júri (XXXVIII), penas proibidas (XLVII) e habeas data (LXXII).
- **NO_SEPARATE com motivo explícito:**
  - LVIII (identificação criminal): regra pontual, marcada como candidata para a revisão;
  - §§ 1º, 2º e 4º: já explicados na visão geral aprovada;
  - caput: coberto pela visão geral.

Todos os incisos novos declaram contexto `[CF88:ART.5, CF88:ART.5:CAPUT]` e `DEPENDENT_ON_PARENT`. A cobertura não é herança: `get_explanation(INC.V)` devolve `None`, e o lookup do INC.V aponta para o bloco com `MATCH=COVERED`.

### Arts. 1º a 4º

- **Art. 1º:** visão geral reutilizada do piloto.
- **Arts. 2º, 3º e 4º:** visões gerais novas.
- **Caputs, incisos e parágrafos únicos desses artigos:** NO_SEPARATE, cobertos pela visão geral (listas curtas ou caput único).

### Avisos de lint (consultivos; o conteúdo não foi reescrito automaticamente)

| Código | Qtde | Leitura |
|---|---|---|
| NEAR_COPY_OF_OFFICIAL_TEXT | 22 | 8 a 10 palavras seguidas iguais à Lei Seca, em geral listas e nomes técnicos. Antes disso, o bloqueio de mais de 10 palavras recusou trechos em 21 explicações, e 29 trechos foram reescritos por paráfrase |
| EXAMPLE_REQUIREMENT_LANGUAGE | 12 | "deve", "precisa" etc. nos exemplos. O revisor confirma que a exigência está no texto |
| ABSOLUTE_CLAIM | 3 | ART.2 "maioria absoluta" (termo técnico); LXXI "nunca foi editada" (hipótese do exemplo); LXXII "sempre informação relativa ao próprio impetrante" (literal) |
| TERM_NOT_USED | 3 | ART.5 "Remédio constitucional" (piloto aprovado); INC.I "Isonomia"; LXIX "Autoridade coatora" |
| JURISPRUDENCE_WORDING_IN_BODY | 2 | XXXVII "tribunais" (no sentido de "tribunais de exceção"); LXVII remissão explícita à camada JURISPRUDÊNCIA |
| TERM_LOW_UTILITY | 2 | LXXII "Impetrante"; LXXVIII "Celeridade" |

### Determinismo e testes

- O batch foi gerado duas vezes. Deram BYTE_IDENTICAL: LOOKUP, PAYLOAD, MANIFEST, `SELECTION_REPORT.json`, `REVIEW_BATCH_01.md` e o corpus do lote.
- **Suíte ENTENDA:** 29/29 OK — 19 do T1 versionado e 10 do batch.
- **Testes do batch** (`tests/test_production_batch_01.py`, untracked):
  - todos os targets do escopo avaliados;
  - HUMAN_APPROVED × PENDING;
  - piloto reutilizado sem duplicar;
  - NO_SEPARATE coberto por explicação real;
  - `covered_targets` apenas de irmãos reais, com lookup COVERED;
  - históricos excluídos e produção só com CURRENT;
  - teto do lote (BATCH_SPLIT_RECOMMENDED);
  - hierarquia do art. 5º sem explosão;
  - conformidade com o T1;
  - build de produção determinístico.
- **LEGAL_TARGET_ID:** 47/47 OK.

### Arquivos do batch (UNTRACKED; sem stage, commit ou tag)

- `ENTENDA_ENGINE/production_batch.py`: construtor genérico de lote.
- `ENTENDA_ENGINE/tests/test_production_batch_01.py`
- `ENTENDA_ENGINE/derived/production_batch_01/`:
  - `BATCH_SPEC.json`
  - `BATCH_01_DRAFTS.json` (fonte editorial)
  - `CF88_BATCH_01.entenda.jsonl`
  - `index/`: `ENTENDA_LOOKUP.IDX`, `ENTENDA_PAYLOAD.DAT` e `ENTENDA_BUILD_MANIFEST.json`
  - `SELECTION_REPORT.json`
  - **`REVIEW_BATCH_01.md`**: folha de revisão agrupada por artigo, com TARGET, DISPOSITIVO, ROLE, as 5 seções, STATUS e caixas APROVAR, AJUSTAR ou REJEITAR.
- `CLEANUP_AUDIT/ENTENDA_CF_PRODUCTION_BATCH_01.md` e `CLEANUP_AUDIT/ENTENDA_CF_PRODUCTION_BATCH_01.json`

Nada foi alterado em Lei Seca, jurisprudência, referências, firmware ou SD.

## Recomendação

1. Revisar `REVIEW_BATCH_01.md`, começando por:
   - LVII (presunção de inocência × prisão);
   - LXVII (depositário infiel);
   - XLII (imprescritibilidade);
   - LXIX (requisito de um ano);
   - XXXVI (direito adquirido × emenda);
   - § 3º (tratados).
2. Decidir os candidatos marcados: LVIII e § 4º com ou sem explicação própria.
3. Aprovar como `HUMAN_APPROVED_T1` e integrar ao corpus canônico (`corpus/CF88.entenda.jsonl`) com commit próprio.
4. Batch 02 (não iniciado): por exemplo, arts. 6º a 17 (direitos sociais, nacionalidade e direitos políticos), com a mesma política e o mesmo teto.

---

## Adendo A3 (2026-09-28): Batch 01 aprovado pela revisão humana

- **Decisões:** 53 decisões em `ENTENDA_ENGINE/derived/production_batch_01/HUMAN_REVIEW_DECISIONS.json` (`HUMAN_REVIEW_COMPLETED`).
  - 34 APPROVED, contando as duas explicações criadas pela revisão.
  - 19 APPROVED_AFTER_ADJUSTMENT.
- **Explicações criadas pela revisão:** `CF88:ART.5:INC.LVIII` (ITEM) e `CF88:ART.5:PAR.4` (DEVICE).
- **Lote final** (`ENTENDA_ENGINE/derived/production_batch_01_final/`):
  - 53 próprias + 2 reutilizadas do piloto = **55 explicações**, todas `HUMAN_APPROVED_T1`;
  - 19 versões anteriores ficaram `RETIRED` com `superseded_by`;
  - o lote pendente original (drafts, corpus, seleção e folha de revisão) foi preservado como evidência congelada.
- **BLOCK formal:** um dispositivo coberto abre o bloco (`COVERED_BY_BLOCK`), com `display_title` gerado a partir dos metadados. Por exemplo, o inciso V abre "Art. 5º, incisos IV, V, IX e XIV — Liberdade de expressão e informação".
- **Lint:** "tribunal", "juiz" e "jurisdição" deixaram de gerar aviso; a CAMADA EXTERNA pode citar referências.
- **Jurisprudência:** 7 recomendações, todas `PENDING_EXTERNAL_INGESTION`. Nenhum registro correspondente existe no acervo local curado: SV 5, SV 25, Tema 855, Tema 1068, STJ Súmula 403, regime jurídico e tratados sem rito do § 3º.
- **Build final:** executado duas vezes, BYTE_IDENTICAL.
