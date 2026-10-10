# Reconciliação Macro07 × Macro08

Branch `reconcile-macro07-macro08`, criada do HEAD do Macro07. Os logs históricos (`MACRO07_CLOUD_RUN_LOG.md`, `MACRO08_CLOUD_RUN_LOG.md`,
`MACRO08_HUMAN_REVIEW_RUN_LOG.md`) não foram alterados e continuam representando seus contextos originais. Detalhe por arquivo e hashes:
`RECONCILIATION_AUDIT.json` (gerado a partir dos artefatos reais).

| Entrada | Branch | SHA |
|---|---|---|
| Macro07 | `cf-macro-76-175-cloud` | `c963acd48721a80168c27243f2495241f270f62f` |
| Macro08 | `cf-macro-176-250-adct-cloud` | `5c4f1a0c71c5081c5d57622acf9d306edb27904c` |
| Ancestral comum | — | `03e6f2592f099b6279d10ec91a307e737faffa88` |

Nenhum merge, rebase, cherry-pick ou force push; `main`, Macro07 e Macro08 inalterados.

## Estratégia

1. Branch nova a partir do Macro07 (`c963acd`); Macro07 e Macro08 ficam congelados como checkpoints auditáveis.
2. Classificação dos arquivos alterados desde o ancestral comum (69 no Macro07, 110 no Macro08). **Nenhum arquivo foi alterado pelos dois lados.**
   - A (código/infra do Macro08, incorporado): `build_entenda_macro_segment.py`, `entenda_text_profile.py`, `apply_macro08_human_review.py`,
     `editorial/TEXT_PROFILES.json`, `profiles/CF88_OFFICIAL_RUNTIME/*`, `tests/test_entenda_macro_batch08.py`, `tests/test_git_materialization.py`.
   - B (exclusivos do Macro08, preservados byte a byte): entradas do lote, decisões humanas R1/R2/R3, resoluções de flags, registro de aplicação.
   - C (agregados, regenerados pelo builder canônico): 12 arquivos do Macro08 (manifesto, triagem, 8 checkpoints, backlog, evidência de determinismo).
   - D (versão mais nova no Macro07, mantida e não sobrescrita): `build_entenda_macro_batch.py`, `macro_critic_pass.py`, `t1_second_pass.py`,
     `LEGAL_TARGET_ID/*` e todo o diretório do Macro07 (segundo passe).
   - E (histórico imutável): `history/pre_second_pass/*` do Macro07, `*_PRE_HUMAN_REVIEW*` e decisões R1/R2 do Macro08, logs de execução.
3. Importação por caminho explícito (`git checkout <sha> -- <caminho>`): 97 arquivos do Macro08 idênticos ao commit de origem.
4. Regeneração do Macro08 com `build_entenda_macro_segment.py --determinism 3` sobre o código composto.

## Conflitos encontrados

| # | Conflito | Natureza | Resolução |
|---|---|---|---|
| 1 | `build_entenda_macro_batch.MacroContext` (segundo passe do Macro07) passou a ler `<P>_TRANSITION_EVIDENCE.json` como **entrada** no esquema do Macro07 (`sources`/`targets`). No Macro08 o arquivo com esse nome é **saída** do builder de segmento (camada temporal, esquema `entries`). Num build novo o arquivo ainda não existe e o build passa; no lugar, o build quebrava (`KeyError: 'sources'`). | semântico (sem sobreposição textual) | `SegmentContext.__init__` (builder do Macro08, não fixado por hash) monta o contexto sem tratar essa saída como entrada: mantém a camada do segundo passe (`SECOND_PASS_INPUT`, consistência pai/filho) com evidência de transição vazia, que é exatamente o que todo build novo vê. A camada temporal do Macro08 continua resolvida por `TEMPORAL_INPUT`. O build no lugar passou a ser igual ao build novo; `t1_second_pass.py` entrou no registro de hashes de código do manifesto. |
| 2 | Novas chaves de `checks` do Macro07 (`transition_without_evidence`, `transition_evidence_unused`, `judicial_review_unclassified`), novo texto do BACKLOG e novos hashes de código de módulos do Macro07 nos artefatos do Macro08. | agregado | Regenerados pelo builder canônico (todas as chaves novas vazias; contagens do BACKLOG iguais: 631 registros, 300 aprovados). |
| 3 | Errata de status do LEGAL_TARGET_ID (`CF88:ART.114:INC.VIII`, `CF88:ART.155:INC.I:AL.c`). | verificação | Fora do escopo do Macro08; o arquivo de status base não foi reescrito (errata em overlay por sha256). O perfil `CF88_OFFICIAL_RUNTIME` se reconstrói byte a byte (`test_profile_rebuilds_byte_identical`). Nenhuma alteração. |

Módulos compartilhados fixados por hash: nenhum alterado; a reconciliação não exigiu mexer neles.

## Contagens (calculadas dos corpora reais)

| | |
|---|---|
| `approved_before_macro08` (todos os corpora do Macro07, por explanation_key) | **300** |
| `approved_macro08` | **179** (149 v1 + 30 v2; 30 v1 RETIRED preservadas) |
| interseção | 0 |
| `approved_after_reconciliation` | **479** = união sem duplicatas; 0 conflitos de chave; 0 aprovações perdidas |
| explanation_keys ACTIVE únicas | 810 (631 antes; +179) |
| chaves em mais de um corpus | 145, todas preexistentes (pares pendente/final dos lotes 01–03, iguais no Macro07); 0 envolvendo o Macro08 |
| Pares de índice | 12 (11 do Macro07 + o do Macro08); 1346/1346 linhas/blocos (1146 do Macro07 + 200 do Macro08) |

Os corpora e pares de índice do Macro07 e dos lotes anteriores estão byte-idênticos ao Macro07. O corpus, o par de índice, os rascunhos e as
decisões do Macro08 estão byte-idênticos ao Macro08: os textos aprovados não mudaram nenhum byte.

## Verificações

| Verificação | Resultado |
|---|---|
| Build composto do Macro08 | checks PASS; portão de aprovação PASS (179/179, 0 HARD_FAIL, 0 REVIEW_REQUIRED aberto, 25 resoluções fechando exatamente 26 ocorrências) |
| Determinismo do Macro08 | PASS: 3 builds + build no lugar byte-idênticos (92 arquivos) |
| Materialização Git (`--source INDEX`, `core.autocrlf=true`) | PASS: arquivos críticos byte-idênticos, 12 pares de índice, 1346/1346 blocos, 0 problemas |
| Suíte ENTENDA, ambiente equivalente ao Cloud (worktree LF, `PYTHONUTF8=1`) | 238 testes: 233 PASS, 2 SKIP, 3 falhas ambientais; baseline do Macro07 no mesmo ambiente: 208 testes com as mesmas 3 falhas |
| Macro08 / Macro07 / Batch06 / Batch05 | 30/30 · 26 PASS + 2 ambientais · 28/28 · 25 PASS + 1 SKIP |

As 3 falhas ambientais são preexistentes e iguais no baseline:
- `test_entenda_macro_batch07.test_rebuild_is_byte_identical`: o builder do Macro07 (compartilhado) grava `\` no manifesto no Windows. O
  manifesto reconstruído é idêntico ao versionado depois de normalizar o separador.
- `test_entenda_macro_batch07.test_pre_second_pass_history_preserved`: o próprio teste compara caminhos com `str(relative_to)`, o que dá `\` no Windows.
- `test_git_materialization` dentro de worktree: `.git` é arquivo, não diretório. No checkout principal o teste passa.

No checkout principal Windows (`core.autocrlf=true`), o `cf.txt` canônico (`updater/**`, sem atributo de eol) fica CRLF (sha `d9f3d6b9…`).
O segundo passe do Macro07 fixa o blob LF (`0742175b…`) e falha no `setUpClass` do `MacroBatch07SecondPass`, igual no baseline. É ambiental.

DEVICE_INTEGRATION e LEGAL_TARGET_ID não foram reexecutados nesta máquina: nenhum arquivo dessas pastas veio do Macro08 e o diff contra o
Macro07 é vazio. Valem as contabilidades do Macro07 (`*_CLOUD_ACCOUNTING_SECOND_PASS.json`, que já cobrem a correção de transcrição do
LEGAL_TARGET_ID) e do Macro08. Nenhum arquivo DEVICE_INTEGRATION, firmware ou updater referencia os Macros 07/08; a materialização para
dispositivo desses lotes é o par de índice, verificado acima.
