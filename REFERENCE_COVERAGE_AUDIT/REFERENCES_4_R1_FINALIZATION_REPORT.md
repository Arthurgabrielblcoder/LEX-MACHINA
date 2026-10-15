# REFERÊNCIAS Nº 4 — CF: R1, finalização das duas aprovações retidas

```
MISSION = R1 — finalizar as duas aprovações retidas (HOST-ONLY)
DATE = 2026-10-15
BRANCH = cf-references4-finalize
BRANCH_BASE = af8f68dace695de6b332c5e8cf7920e5754c6f99 (HEAD de cf-correlata-coverage-audit)
RESULT = BLOCKED_BEFORE_MATERIALIZATION
SOS_SAUDE_EDITORIAL_APPROVAL = CONFIRMED
PRO_DIA_NASCER_FELIZ_EDITORIAL_APPROVAL = CONFIRMED
SOS_SAUDE_WORK_IDENTITY = BLOCKED_MISSING_BIBLIOGRAPHIC_METADATA
PRO_DIA_NASCER_FELIZ_WORK_IDENTITY = BLOCKED_MISSING_BIBLIOGRAPHIC_METADATA
WORK_REGISTRY_DUPLICATE_CHECK = PASS
RETAINED_APPROVALS_MATERIALIZED = 0/2
NEW_EDITORIAL_RELATIONS = 0
REGISTRY / EXPORT / TARGETS / REF_* / HEADER / FIRMWARE = NÃO ALTERADOS
MICROSD_TOUCHED = NO
DEVICE_FLASHED = NO
```

## 1. Linha de trabalho (Parte A)

- Foi feito `git fetch origin` sem force. O HEAD local e o remoto de `cf-correlata-coverage-audit` são iguais: `af8f68d` (`docs: freeze CF correlatas 1 approved baseline`).
- Ancestralidade conferida em `af8f68d`:
  - a tag `lex-device-v1-correlata-c3b2-physical-approved-2026-10-12` (`74c6662`, promoção C3B.2);
  - `CORRELATA_COVERAGE_AUDIT/CORRELATAS_1_CF_FROZEN.md`;
  - `DEVICE_INTEGRATION/C3B2_CORRELATA_PHYSICAL_BASELINE_APPROVED.md`;
  - `DEVICE_INTEGRATION/C3B2_CORRELATA_PROMOTION/promoted_sys/LEX_DEVICE_MANIFEST.json`.
- `main` **não** contém a tag C3B.2, portanto não serviria de base.
- `cf-references4-finalize` foi criada a partir de `af8f68d`, não de `batch06-scale-cloud`.
- `C3B2_BASELINE_PRESENT = YES` · `CORRELATAS_1_FREEZE_PRESENT = YES` · `REFERENCES_BRANCH_BASE_IS_SAFE = YES`.
- O checkpoint R0 (`REFERENCIAS_4_CF_RESUME_CHECKPOINT.md`) foi preservado byte a byte na troca de branch. O SHA-256 `178f4b7a…7655` é igual antes e depois. Foi versionado no commit `2950d1e`.

## 2. Decisões retidas (Parte B)

Fonte: `REFERENCE_COVERAGE_AUDIT/REFERENCE_EXPANSION_ROUND1_DECISIONS.json` (`status FINAL`, `decided_on 2026-10-02`, `authority ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW`).

| | P20 | P21 |
|---|---|---|
| `decision_id` | `REFERENCE_EXPANSION_01-P20` | `REFERENCE_EXPANSION_01-P21` |
| Target | `CF88:ART.196` | `CF88:ART.206:INC.I` |
| Obra pretendida | SOS Saúde (Sicko), DOCUMENTÁRIO, 2007 | Pro Dia Nascer Feliz, DOCUMENTÁRIO, 2006 |
| Decisão / status | `APPROVE` / `HUMAN_APPROVED_REFERENCE_V1`, score 7,4 | `APPROVE` / `HUMAN_APPROVED_REFERENCE_V1`, score 8,0 |
| Integração | `APPROVED_PENDING_WORK_IDENTITY` | `APPROVED_PENDING_WORK_IDENTITY` |
| Motivo da retenção | `work_id: null`, `work_registry_status: NO_WORK_IDENTITY`, `candidate_catalog_id` nulo | idem |

As duas decisões aparecem também no `promotion_log` com status `APPROVED_PENDING_WORK_IDENTITY`.

Não existe rejeição nem *supersession* posterior:

- nenhum commit posterior altera o arquivo de decisões;
- `DEVICE_V1_PERFORMANCE_PHYSICAL_BASELINE_APPROVED.md` (item 5) repete que ambas "continuam `APPROVED_PENDING_WORK_IDENTITY`".

A ausência no aparelho decorre **somente** da falta de identidade da obra. É exatamente isso que o `apply_reference_expansion_round1.py` faz: ele retém a proposta quando `candidate_catalog_id` é nulo.

**Resultado: `SOS_SAUDE_EDITORIAL_APPROVAL = CONFIRMED` e `PRO_DIA_NASCER_FELIZ_EDITORIAL_APPROVAL = CONFIRMED`.**

## 3. Cadastro no registry (Parte C): BLOQUEADO

### Registry e mecanismo oficial

- **Registry:** `REFERENCE_REGISTRY/WORK_REGISTRY_V2.json` (`OFFICIAL_REGISTRY`, 73 obras).
- **Política declarada no próprio registry:** "Somente obras exigidas por vínculos aprovados no REFERENCE_EXPANSION_01 e com identidade real no catálogo candidato."
- **Mecanismo oficial de promoção:** `REFERENCE_COVERAGE_AUDIT/apply_reference_expansion_round1.py::promote()`. Ele:
  - exige um `CAND200-NNN` do `CATALOGO_EXPANSAO_200`;
  - confere título, tipo e ano com o registro do catálogo;
  - copia do catálogo `descricao_factual` (`resumo_factual_curto`), `fontes`, `riscos` e `criadores`;
  - copia também o registro de origem integral e a proveniência (`candidate_record_sha256`).
- **As 4 obras promovidas até hoje** (EXP2-LIV-040, EXP2-FIL-039, EXP2-FIL-006, EXP2-FIL-038) têm todas `fontes` com `url`, `accessed_on`, `tier` e `supports: identidade`.

### Duplicatas: `WORK_REGISTRY_DUPLICATE_CHECK = PASS`

A busca normalizada (sem acentos ou pontuação, termos `sicko`, `sossaude`, `prodianascerfeliz`, `nascerfeliz`) cobriu:

- o registry (73);
- `CATALOGO_EXPANSAO_200.json` (199);
- `CANDIDATAS_200.json` (200);
- todo o repositório (`.json`, `.md`, `.csv`, `.txt`, `.py`).

Nenhum registro existente corresponde a essas obras. O único acerto do catálogo (índice 158, *Estação Carandiru*) foi falso positivo de substring entre palavras. Não há documentário de 2006/2007 com essas identidades no registry. **Não existe duplicata**, mas também não existe registro que dê identidade às obras.

### Evidência disponível e o que falta

A única ocorrência dos metadados está nos literais da função `P(...)` em `REFERENCE_COVERAGE_AUDIT/build_reference_expansion_candidates.py` (linhas 142–151). São textos da *proposta editorial* gerada na rodada, sem fonte:

- **P20:** título "SOS Saúde (Sicko)", tipo DOCUMENTÁRIO, ano 2007. O nome "Michael Moore" aparece apenas na prosa "por que está aqui".
- **P21:** título "Pro Dia Nascer Feliz", tipo DOCUMENTÁRIO, ano 2006. Não há realizador.

Não há URL, `accessed_on`, locator, paráfrase de fonte, *tier* ou registro de coleta para nenhuma das duas.

Campos que o mecanismo oficial exige e que não têm suporte documental no projeto:

| Campo | SOS Saúde (Sicko) | Pro Dia Nascer Feliz |
|---|---|---|
| Registro de identidade no catálogo candidato (`CAND200-*`, `candidate_record_sha256`) | **AUSENTE** | **AUSENTE** |
| `extensoes_origem.fontes` (fonte que sustente `identidade`) | **AUSENTE** | **AUSENTE** |
| `extensoes_origem.descricao_factual`, que é o "SOBRE" do header de detalhes | **AUSENTE** | **AUSENTE** |
| `criadores` | **AUSENTE como dado de fonte** (só aparece na prosa editorial da proposta) | **AUSENTE** |
| `titulo_original` | **AUSENTE como dado de fonte** (só no parêntese do título da proposta) | **AUSENTE** |
| `ano`, `tipo` | presentes **somente** como literais da proposta, sem fonte | idem |

Preencher esses campos exigiria inferir por plausibilidade ou fazer pesquisa nova fora de fonte já registrada no workflow. As duas coisas são vedadas nesta missão. Por isso, as duas obras ficam:

```
BLOCKED_MISSING_BIBLIOGRAPHIC_METADATA
  campos ausentes: candidate_catalog_record, fontes(identidade), descricao_factual, criadores, titulo_original
```

Nenhum ID foi criado e o registry não foi alterado.

## 4. Consequência para as Partes D–L

Sem obra no registry, o gate `fail closed` do motor recusaria a adição com `ADDITION_WORK_NOT_IN_REGISTRY` (`LEGAL_TARGET_ID/reference_engine.py`). Por isso **não houve nada a materializar**, e nenhum artefato foi gerado:

- sem novo export `REF_LOOKUP`/`REF_PAYLOAD`;
- sem regeneração de `CF88_TARGETS.IDX`;
- sem regeneração de `lex_ref_detail_data.h`;
- sem compilação de firmware;
- sem pacote host-only.

Um pacote idêntico ao baseline não teria valor de teste. Também não foram criados o `REFERENCES_4_R1_ISOLATION_AUDIT.json` nem o `REFERENCES_4_R1_PHYSICAL_TEST_PLAN.md`: não há candidato a auditar ou testar.

O baseline publicado permanece o do C3B.2:

- 122 `WORK_REFERENCE`;
- 63 targets W;
- 54 obras usadas;
- 24 + 2 CORRELATA.

Isolamento de Correlatas 1: **trivialmente preservado**, porque nenhum byte de `REF_*`, `TARGETS`, `RELACOES`, `REL_LOOKUP`, `EXT_ARTIGOS`, manifestos ou firmware foi tocado.

Registro para a futura materialização (não executado): o baseline C3B.2 não tem obra em `CF88:ART.196` nem em `CF88:ART.206:INC.I`. A matriz RUN3 lista os arts. 196 e 206 como "SEM COBERTURA — aprovado, retido".

## 5. O que destrava

Uma missão própria de **ingestão de identidade** das duas obras. Ela precisa reproduzir o padrão do `CATALOGO_EXPANSAO_200`:

- fonte consultada com URL, data, locator, *tier* e `supports: identidade`;
- resumo factual;
- criadores e título original confirmados na fonte;
- registro de coleta.

Esse trabalho pode ser feito por pesquisa autorizada pelo usuário ou por uma fonte fornecida pelo usuário. Depois dele, uma nova execução de R1 pode materializar os dois vínculos pelo `promote()` e pelo motor, partindo desta branch.
