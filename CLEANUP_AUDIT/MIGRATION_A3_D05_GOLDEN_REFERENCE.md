# Migração A3 — Golden Reference histórica do D05

Status: **VÁLIDA PARA REVISÃO**. Esta referência foi reconstruída exclusivamente de evidências históricas já persistidas. Nenhum compilador, gerador de manifesto, pipeline, Engine ou build foi executado.

## 1. Escopo e método

Dataset: `d05.catalogo-expansao-200`.

A referência composta contém **855 ocorrências**:

- 852 membros registrados diretamente em `08_MANIFEST/MANIFEST.json`;
- os dois arquivos chamados `MANIFEST.json`, que o produtor global omitiu por basename e que possuem evidência histórica separada;
- o catálogo canônico de 69 obras, dependência externa comprovada pela referência de entrada e pelo relatório de integridade.

O registry A2 não foi usado para construir esse conjunto. Ele foi lido somente depois da reconstrução, para a comparação passiva.

## 2. Fontes históricas e força

Foram usadas 25 fontes ou conjuntos: 16 `AUTHORITATIVE_HISTORICAL`, seis `SUPPORTING_HISTORICAL` e três `DERIVED_REPORT`. Nenhuma fonte foi classificada como `AMBIGUOUS`.

| ID | Path/conjunto | Força | Função |
|---|---|---|---|
| E01 | `08_MANIFEST/MANIFEST.json` | AUTHORITATIVE_HISTORICAL | 852 paths, hashes e tamanhos do fechamento |
| E02 | `07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/MANIFEST.json` | AUTHORITATIVE_HISTORICAL | seis payloads do pacote enriquecido |
| E03 | `07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/METADADOS_ENRIQUECIDO_V1.json` | AUTHORITATIVE_HISTORICAL | hashes de entradas e métricas da compilação |
| E04 | `06_RELATORIOS/DETERMINISMO_COMPILACAO.json` | SUPPORTING_HISTORICAL | duas recompilações idênticas dos catálogos-base |
| E05 | `06_RELATORIOS/RELATORIO_ENRIQUECIMENTO_V1.md` | DERIVED_REPORT | fechamento narrativo e prova registrada de três compilações |
| E06 | `08_MANIFEST/INTEGRIDADE_ANTES.json` | AUTHORITATIVE_HISTORICAL | snapshot anterior da V2 |
| E07 | `08_MANIFEST/INTEGRIDADE_DEPOIS.json` | AUTHORITATIVE_HISTORICAL | integridade posterior e catálogo 69 |
| E08 | `06_RELATORIOS/BASELINE_ENRIQUECIMENTO_V1.json` | AUTHORITATIVE_HISTORICAL | snapshot temporal de 580 arquivos anterior ao enriquecimento |
| E09 | `06_RELATORIOS/CHECKPOINT_ENRIQUECIMENTO.json` | AUTHORITATIVE_HISTORICAL | fila, 12 checkpoints, 111 exames e 71 cards |
| E10 | `06_RELATORIOS/CHECKPOINTS_ENRIQUECIMENTO/CP_*.json` | AUTHORITATIVE_HISTORICAL | 12 checkpoints individuais |
| E11 | `06_RELATORIOS/ESTADO_ENRIQUECIMENTO_APOS_CODEX.json` | DERIVED_REPORT | reconstrução de estado e atribuição dos exames |
| E12 | `04_DOSSIERS/ENRIQUECIMENTO_V1/*.json` | AUTHORITATIVE_HISTORICAL | 111 decisões primárias em overlays |
| E13 | `06_RELATORIOS/REVISOES_ENRIQUECIMENTO_V1.json` | AUTHORITATIVE_HISTORICAL | três patches aplicados por `evidence_id` |
| E14 | `06_RELATORIOS/CHECKPOINT_LOTES.json` | AUTHORITATIVE_HISTORICAL | oito checkpoints dos lotes de triagem |
| E15 | `06_RELATORIOS/REVISOES_POS_CHECKPOINT.json` | AUTHORITATIVE_HISTORICAL | ledger de alterações pós-checkpoint |
| E16 | `00_ENTRADA/REFERENCIA_CATALOGO_69.json` | AUTHORITATIVE_HISTORICAL | 69 obras e hash declarado do catálogo externo |
| E17 | `07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json` | AUTHORITATIVE_HISTORICAL | output-base de 199 obras e 221 cards |
| E18 | `07_CATALOGO_CANDIDATO/CATALOGO_TOTAL_69_MAIS_APTAS.json` | AUTHORITATIVE_HISTORICAL | output combinado 69 + 199 |
| E19 | `07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/*` | AUTHORITATIVE_HISTORICAL | sete membros do pacote congelado |
| E20 | `07_CATALOGO_CANDIDATO/compilar_catalogo.py` | SUPPORTING_HISTORICAL | algoritmo histórico de seleção e ordem do catálogo-base |
| E21 | `07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py` | SUPPORTING_HISTORICAL | algoritmo histórico de overlays, revisões e ordem |
| E22 | `06_RELATORIOS/editorial_enriquecimento_v1.py` | SUPPORTING_HISTORICAL | precedência lexicográfica das capturas |
| E23 | `08_MANIFEST/gerar_manifest.py` | SUPPORTING_HISTORICAL | `rglob` ordenado e omissão de basenames `MANIFEST.json` |
| E24 | `06_RELATORIOS/ESTADO_FINAL.json` | DERIVED_REPORT | resumo final derivado da triagem |
| E25 | `06_RELATORIOS/CORRECOES_DURANTE_ENRIQUECIMENTO.json` | SUPPORTING_HISTORICAL | ledger auxiliar de correções |

O baseline de 580 arquivos é autoritativo apenas para seu ponto temporal. Ele não substitui o manifesto final de 852 membros.

## 3. Conjunto historicamente comprovado

O JSON registra individualmente path histórico, role, storage root, tamanho, SHA-256, força e links de evidência para todas as 855 ocorrências. A distribuição de roles reproduz a topologia histórica, incluindo:

- 200 registros de entrada distribuídos em oito lotes de identidade e oito lotes de triagem;
- 199 dossiês-base;
- 316 capturas/fontes da fase-base e 128 capturas de enriquecimento;
- 111 overlays;
- 12 checkpoints individuais;
- dois catálogos-base;
- seis payloads enriquecidos e seu manifesto;
- uma ocorrência externa do catálogo 69.

Os três membros `restricted_local` fazem parte da prova histórica porque estão no manifesto final, embora continuem fora do Git.

## 4. Ordem histórica

Dez conjuntos possuem `ORDEM_COMPROVADA`:

1. `LOTE_01` a `LOTE_08` por loop explícito;
2. os 200 números na ordem persistida dentro dos lotes;
3. 199 `work_id` na ordem do catálogo-base, confirmada pelo `sorted(work_id)` do compilador;
4. 69 IDs do catálogo original em ordem de `id` antes da concatenação;
5. 111 `work_id` na ordem persistida da fila;
6. checkpoints 1–12 e a ordem das candidatas dentro de cada checkpoint;
7. 128 paths de captura em ordem lexicográfica usada pelo seletor;
8. 111 overlays na ordem efetiva dos `work_id` do build;
9. seis payloads na ordem persistida do manifesto enriquecido;
10. 852 membros na ordem persistida do manifesto global.

Duas ordens são `ORDEM_DESCONHECIDA`:

- cronologia completa da deliberação humana dentro de cada decisão;
- cronologia de recuperação remota das capturas.

A ordenação lexicográfica utilizada pelo código é comprovada; ela não prova a cronologia de consulta. Nenhuma ordem foi promovida silenciosamente a `ORDEM_INFERIDA`.

## 5. Multiplicidade

As 128 capturas pertencem a 111 candidatas:

- 97 candidatas possuem uma captura;
- 11 possuem duas;
- três possuem três.

O JSON preserva cada path. Também preserva 111 overlays, 12 checkpoints e três revisões como ocorrências distintas. Não há hashes repetidos nas 855 ocorrências atuais, mas a regra histórica proíbe deduplicar ocorrências futuras apenas por igualdade de SHA-256.

## 6. Ausências semânticas

| Estado | Quantidade | Significado |
|---|---:|---|
| `NO_ENRICHMENT_OVERLAY_BY_DESIGN` | 88 | obras classificadas como completas prováveis ficaram fora da fila; ausência de overlay não é arquivo faltante |
| `NO_ADDITIONAL_CARD_AFTER_EXAMINATION` | 47 | overlay existe e registra decisão +0 |
| `WEB_SOURCE_WITHOUT_COMPLETE_LOCAL_RECEIPT` | 9 | confirmação histórica existe, recibo local completo não |
| `REMOTE_FETCH_FAILED_WITH_METADATA_PRESERVED` | 6 | falha HTTP foi registrada; conteúdo remoto não foi inventado |
| `CANDIDATE_EXCLUDED_FROM_USABLE_CATALOG` | 1 | candidata 92, `EXP2-SER-002`, foi rejeitada como duplicata existente |

Nenhum arquivo vazio, overlay fictício, card fictício ou recibo retroativo foi criado.

## 7. Decisões humanas e revisões

A referência contém 111 relações de decisão por overlay:

- 64 `ENRIQUECIDA`;
- 47 `SEM_CARD_ADICIONAL_JUSTIFICADO`;
- 71 cards adicionados;
- 12 candidatos a card recusados, preservados nas decisões;
- `candidate_number`, `work_id`, checkpoint, estado, cards antes/depois, `evidence_id`, hash do overlay e revisor quando registrado.

O campo `examinada_por = CODEX` para as 111 decisões provém do estado reconstruído E11 e é ligado aos overlays/checkpoints primários; não foi inferido do conteúdo dos overlays, que não contém campo de revisor.

As três revisões pós-Codex permanecem vinculadas aos `evidence_id`:

- `EXP2-DOC-013-E03`;
- `EXP2-DOC-013-E04`;
- `EXP2-SER-012-E02`.

O ledger registra os patches aplicados, mas não contém identidade formal do revisor; esse campo permanece `null`.

## 8. Outputs históricos comprovados

| Output | SHA-256 | Bytes | Métricas históricas |
|---|---|---:|---|
| `CATALOGO_EXPANSAO_200.json` | `5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43` | 959.745 | 199 obras, 221 cards |
| `CATALOGO_TOTAL_69_MAIS_APTAS.json` | `6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6` | 76.121 | 69 existentes + 199 novas = 268 |
| `CATALOGO_EXPANSAO_ENRIQUECIDO_V1.json` | `cddb00344f6e3075f552fb042b168d184463b85e513f695eb1089139ee301da7` | 1.154.254 | 199 obras; 221 + 71 = 292 cards |
| `CATALOGO_TOTAL_ENRIQUECIDO_V1.json` | `5446da1294cee6311dcef3a0c5438b7c7de2bc2adec586fe38b85f199394305d` | 69.418 | 69 + 199 = 268 |
| `EVIDENCE_CARDS_ENRIQUECIDOS_V1.json` | `3446c073eda030045bc20efe0ac0854c924fe7b11e66a71d0671d6717f054a07` | 607.221 | 292 cards |
| `DECISOES_ENRIQUECIMENTO.json` | `de779c2f5873d665953d849d37643e21219da428df89b534a24781b8031e8c30` | 116.799 | 199 obras, 111 examinadas |
| `METADADOS_ENRIQUECIDO_V1.json` | `27a427ccd18813992f633e8f94bb59e8a2e46a1d6558b95d8c37ef7e037c2f02` | 11.588 | 199 obras, 71 novos, 292 finais |
| `README.md` | `423b90dde03d10cd268681b55f18e6fa51007fd1af939d09b80be952a2cbe9e3` | 1.269 | documento do pacote |
| `MANIFEST.json` | `0312e5f091981f8065673529aca04437ed0fc7ecaac26cd144d2af26ab37774c` | 1.044 | seis payloads |

Essas métricas foram lidas dos próprios outputs, manifests e metadados congelados. Nenhum output foi regenerado.

## 9. Comparação passiva com o registry

| Classificação | Quantidade |
|---|---:|
| `MATCH` | **855** |
| `REGISTRY_EXTRA` | 0 |
| `HISTORICAL_ONLY` | 0 |
| `HASH_MISMATCH` | 0 |
| `PATH_DIFFERENCE` | 0 |
| `ROLE_DIFFERENCE` | 0 |
| `EVIDENCE_INSUFFICIENT` | 0 |

Cada ocorrência tem classificação individual no JSON. A comparação verificou root, path, role, hash e tamanho.

Existem duas diferenças estruturais `INFORMATIONAL`, sem diferença de ocorrência:

- a Golden Reference contém as sequências históricas completas; o registry apenas descreve artefatos;
- a Golden Reference contém o grafo de decisões/checkpoints; o registry não tem essa responsabilidade.

Não há diferença `NEEDS_EXPLANATION` na comparação de ocorrências nem diferença `BLOCKING_FOR_A4`.

## 10. Lacunas explícitas

1. nove consultas web não têm recibo local completo;
2. três membros do manifesto são `restricted_local` e não existem em checkout somente Git;
3. o manifesto global omite os dois basenames `MANIFEST.json`;
4. não há `created_by_run_id` histórico uniforme;
5. o ledger de três revisões não identifica formalmente o revisor;
6. cronologia completa da consulta remota e da deliberação humana não é comprovável.

As duas primeiras exigem explicação operacional em uma futura comparação, mas não invalidam a referência no workspace histórico atual.

## 11. O que não pode ser provado

- a ordem cronológica exata de toda consulta ou deliberação;
- a reprodutibilidade de conteúdo remoto hoje;
- identidade formal do revisor das três revisões;
- portabilidade integral para um clone que não possua os três `restricted_local`;
- verdade editorial ou factual apenas a partir dos hashes;
- que o manifesto global, sozinho, inclua seus próprios bytes ou o manifesto interno.

## 12. Critérios para futura paridade

Uma futura comparação poderá exigir igualdade estrita de:

- 855 ocorrências compostas, paths, tamanhos e hashes;
- nove outputs e suas métricas;
- ordens marcadas `ORDEM_COMPROVADA`;
- multiplicidade das capturas, overlays, checkpoints e revisões;
- 111 decisões, seus estados e vínculos;
- cinco classes de ausência semântica;
- cardinalidades 200, 199, 221, 71, 292, 111, 88, 12, 3 e 69.

Não poderá exigir igualdade de cronologia onde a Golden Reference declara `ORDEM_DESCONHECIDA`. Um checkout sem os três `restricted_local` deve falhar explicitamente e reportar a limitação, sem fabricar substitutos.

## 13. Integridade e não alteração

A3 criou somente:

- `CLEANUP_AUDIT/D05_GOLDEN_REFERENCE.json`;
- `CLEANUP_AUDIT/MIGRATION_A3_D05_GOLDEN_REFERENCE.md`.

Nenhum arquivo D05 ou do registry foi alterado. O verifier do registry permanece como gate somente leitura. Não houve staging, commit, tag, build ou execução de pipeline.

## 14. Severidade e bloqueios

- `BLOCKING_FOR_A4`: **0**;
- `NEEDS_EXPLANATION`: as limitações dos nove recibos e três arquivos locais, já explicitadas;
- `INFORMATIONAL`: omissão histórica dos manifests, ausência de run IDs/revisor e cronologias desconhecidas.

A base histórica é suficiente para a futura comparação porque conjunto, bytes, outputs, ordens comprováveis, multiplicidade, decisões e ausências estão materializados sem preencher lacunas.

## 15. Condição para A4

A4 pode ser proposta após revisão humana destes dois artefatos. Deve usar esta referência antes de qualquer reexecução, respeitar `ORDEM_DESCONHECIDA`, tratar a ausência dos três `restricted_local` como falha explícita e manter o pipeline legado autoritativo até decisão posterior. A4 não foi iniciada nesta missão.
