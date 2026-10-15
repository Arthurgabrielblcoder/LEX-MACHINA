# MACRO08 — aplicação da revisão jurídica humana e promoção (179 HUMAN_APPROVED_T1)

Branch `cf-macro-176-250-adct-cloud`, sobre o checkpoint `1286875ddeb19f2c4608ee12a766dd0cd02462df` (sem divergência). Execução local
(Windows, Python 3.12). Sem merge, rebase ou force push; `main`, Batch06, Macro07 e módulos compartilhados fixados por hash inalterados.

## Revisão humana registrada

| Artefato (em `production_batch_08_macro/`) | Conteúdo |
|---|---|
| `MACRO08_HUMAN_REVIEW_DECISIONS_R1.json` | revisão 1 (sha256 `1c5273c5…`): 179 revisados, 148 aprovados sem alteração, 31 ajustes (A 20, B 7, C 4), 0 rejeitados |
| `MACRO08_HUMAN_REVIEW_DECISIONS_R2.json` | revisão 2: 12 reformulações (9 bloqueios do contrato do motor + 3 alertas eliminados pela redação) |
| `MACRO08_HUMAN_REVIEW_DECISIONS.json` | revisão 3 (vigente): CF88:ART.220:PAR.3 e CF88:ART.213 reformulados; cadeia R1 → R2 → R3 por sha256 |
| `MACRO08_HUMAN_FLAG_RESOLUTIONS.json` | 25 decisões humanas explícitas por target/flag (26 ocorrências), cada uma com flag, match, decisão, reason_code, justificativa, versão aprovada e proveniência |
| `MACRO08_HUMAN_REVIEW_APPLY_AUDIT.json`, `MACRO08_HUMAN_REVIEW_METADATA.json` | registro do `apply_macro08_human_review.py` (30 patches de conteúdo + 1 só de provenance, ADCT:ART.101) |
| `*_PRE_HUMAN_REVIEW.*` | evidência pré-revisão congelada (rascunhos, corpus, triagem e pacotes revisados), byte-idêntica ao checkpoint |
| `MACRO08_ROUND_FINAL_HUMAN_REVIEW_DECISIONS.json` | derivado pelo builder: por target, decisão, motivo, texto anterior e aprovado, versões, proveniência, flags fechadas |

Mecanismo: o de `round_approvals` dos Batches 04–06 (`production_batch.py`, inalterado). O builder do Macro08 lê `MACRO_SPEC.human_review`,
falha fechado se a cadeia de revisões, o registro de aplicação ou o escopo divergirem, marca `HUMAN_APPROVED_T1` por explicação, dá nova
`editorial_version` aos 30 ajustados (v1 preservada como RETIRED/CHANGES_REQUESTED) e roda o portão de aprovação do Batch06 sobre as 179:
contrato do motor, validador v3 sem HARD_FAIL nem REVIEW_REQUIRED aberto, editorial_checks sem pendência. Um achado só fecha por registro
humano explícito, e cada registro precisa fechar exatamente as ocorrências declaradas na versão aprovada. Os registros entram nos mecanismos
que já existiam: resolução conhecida do validador (escopo explanation_id + flag:match, sem tocar `editorial/T1_KNOWN_RESOLUTIONS.json`),
resolução do editorial_checks (ADCT:ART.127) e `human_review.content_provenance` (`HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE`) para as quatro
decisões OFFICIAL_CANONICAL_ANNOTATION. A anotação oficial de cada uma é conferida no arquivo versionado: `cf.txt` canônico para
ADCT:ART.27, ART.101 e ART.107-A; `RUNTIME_TEXT.txt` para CF88:ART.231:PAR.1. Sem regra genérica; limites do motor e validadores inalterados.

## Resultado

| Item | Resultado |
|---|---|
| Contrato do motor nos 179 | 179/179 (revisão 1: 9 bloqueios; revisão 2: 1; revisão 3: 0) |
| Patches de conteúdo | 30 (+ 1 só de provenance, ADCT:ART.101, T1 byte-idêntico) |
| Textos preservados | 149 objeto-idênticos aos rascunhos pré-revisão (148 + ADCT:ART.101) |
| Decisões de resolução de flags | 25 registros, 26 ocorrências fechadas; 0 REVIEW_REQUIRED aberto; 0 HARD_FAIL |
| Status | 179/179 HUMAN_APPROVED_T1 (149 APPROVED v1, 30 APPROVED_AFTER_ADJUSTMENT v2); 30 v1 RETIRED; 0 pendentes; 0 rejeitados |
| Determinismo | PASS: 3 builds completos + build no lugar byte-idênticos (`DETERMINISM_EVIDENCE.json`, 92 arquivos) |

## Reprodução

```
python -I ENTENDA_ENGINE/apply_macro08_human_review.py            # sobre os rascunhos do critic (já aplicado; registro no APPLY_AUDIT)
python ENTENDA_ENGINE/build_entenda_macro_segment.py ENTENDA_ENGINE/derived/production_batch_08_macro --determinism 3
```

`test_entenda_macro_batch08` reproduz pass1 → critic → patch humano byte a byte.

## Suítes (`PYTHONUTF8=1`, paridade com o Cloud)

| Suíte | Branch | Checkpoint `1286875` na mesma máquina |
|---|---|---|
| `test_entenda_macro_batch08` | PASS 30/30 (27 originais, 2 adaptados à promoção, 3 novos) | — |
| ENTENDA completa (`ENTENDA_ENGINE/tests`) | 228: 227 PASS, 1 FAIL ambiental | 225: 220 PASS, 2 FAIL + 1 ERROR, 2 SKIP |
| Macro07 (`test_entenda_macro_batch07`) | 17 PASS + 1 FAIL ambiental | idem |
| Batch06 / Batch05 | 28/28 · 26/26 PASS | — |
| Materialização Git (teste + `git_materialization_check.py`) | ver commit | — |

Falha ambiental (preexistente, não regressão): `test_entenda_macro_batch07.test_rebuild_is_byte_identical`. O builder do Macro07
(`build_entenda_macro_batch.py`, fixado por hash, não alterado) grava caminhos com `\` no Windows; o manifesto reconstruído é idêntico ao
versionado depois de normalizar o separador. No Linux/Cloud passa (baseline do Macro07).

Ambiente Windows (não regressões; documentado para reprodução local):
- `core.autocrlf=true` sem atributo de eol para `ENTENDA_ENGINE/profiles/**` e três arquivos de `ENTENDA_ENGINE/editorial/` gera cópias
  CRLF, cujos hashes entram nas saídas. Esses arquivos foram rematerializados em LF, idênticos aos blobs
  (`git -c core.autocrlf=false checkout`), sem mudar a configuração nem o status do Git. Com isso, o rebuild do checkpoint no Windows sai
  byte-idêntico ao versionado.
- `macro_critic_pass.py` (fixado) abre JSON sem encoding: no Windows exige `PYTHONUTF8=1`; sem ele o teste de reprodução do critic falha
  também no checkpoint.
- O builder do Macro08 passou a gravar caminhos relativos em POSIX (manifesto e evidência de determinismo), igual ao gerado no Cloud.

DEVICE_INTEGRATION e LEGAL_TARGET_ID não foram reexecutados: diff vazio nessas pastas contra o checkpoint; o baseline do
`MACRO08_CLOUD_RUN_LOG.md` continua válido.
