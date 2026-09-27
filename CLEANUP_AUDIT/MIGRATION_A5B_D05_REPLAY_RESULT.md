# Migração A5B — resultado do replay isolado D05

## 1. Sandbox

- Run ID: `d05-replay-2026-09-27-a5b`.
- Sandbox externo: `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b`.
- O sandbox não existia antes da execução, não é o working tree Git principal e foi preservado integralmente.
- O repositório original permaneceu sem alterações rastreadas ou staged durante P1/P2.

## 2. Ambiente

- Python: `3.12.9 (tags/v3.12.9:fdb8142, Feb  4 2025, 15:27:58) [MSC v.1942 64 bit (AMD64)]`.
- Executável: `C:\Program Files\Python312\python.exe`.
- Plataforma: `Windows-11-10.0.26200-SP0` (`win32`).
- Encoding default/filesystem: `utf-8` / `utf-8`.
- `PYTHONHASHSEED=0`, `PYTHONDONTWRITEBYTECODE=1`, UTF-8 e execução com `-I -X utf8`.

## 3. Inputs e hashes

Foram copiados **323 arquivos**, todos byte-idênticos às origens: 8 lotes de triagem, 199 dossiês-base, 111 overlays, três arquivos de estado/referência e os dois compiladores autorizados.

Os três manifests de grupo recalculados coincidiram entre origem e sandbox. Os cinco arquivos únicos coincidiram com os hashes do plano. O baseline completo está em `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\run_record\D05_REPLAY_PRECHECK.json`.

Os três artefatos `restricted_local` não foram copiados nem lidos.

## 4. Rede e write guard

O runner `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\control\offline_exec.py` instalou audit hook antes de `runpy.run_path`, bloqueando eventos `socket.*`, `subprocess.Popen`, `os.system` e escritas fora do sandbox.

Os testes negativos fail-closed passaram: `socket.__new__` foi bloqueado como tentativa de rede; `open` foi bloqueado para o path externo `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b-outside-write-probe.tmp`. Nenhuma operação bloqueada ocorreu durante P1 ou P2.

## 5. P1 — `compilar_catalogo.py`

- Exit code: **0**.
- CWD: `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200`.
- Conjunto de escrita: exatamente os dois catálogos-base esperados.
- Resultado: **2/2 BYTE_IDENTICAL**.

## 6. P2 — `compilar_enriquecido_v1.py`

- Exit code: **0**.
- CWD: `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200`.
- O output root começou vazio e recebeu exatamente sete arquivos.
- Resultado: **7/7 BYTE_IDENTICAL**.

## 7. Nove outputs

| role | historical_path | replay_path | historical_sha256 | replay_sha256 | size_historical | size_replay | status |
|---|---|---|---|---|---:|---:|---|
| `base_catalog_expansion` | `C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\CATALOGO_EXPANSAO_200.json` | `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\CATALOGO_EXPANSAO_200.json` | `5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43` | `5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43` | 959745 | 959745 | **BYTE_IDENTICAL** |
| `base_catalog_union` | `C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\CATALOGO_TOTAL_69_MAIS_APTAS.json` | `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\CATALOGO_TOTAL_69_MAIS_APTAS.json` | `6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6` | `6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6` | 76121 | 76121 | **BYTE_IDENTICAL** |
| `enriched_catalog` | `C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\ENRIQUECIDO_V1\CATALOGO_EXPANSAO_ENRIQUECIDO_V1.json` | `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\REPLAY_ENRIQUECIDO_V1\CATALOGO_EXPANSAO_ENRIQUECIDO_V1.json` | `cddb00344f6e3075f552fb042b168d184463b85e513f695eb1089139ee301da7` | `cddb00344f6e3075f552fb042b168d184463b85e513f695eb1089139ee301da7` | 1154254 | 1154254 | **BYTE_IDENTICAL** |
| `enriched_union` | `C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\ENRIQUECIDO_V1\CATALOGO_TOTAL_ENRIQUECIDO_V1.json` | `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\REPLAY_ENRIQUECIDO_V1\CATALOGO_TOTAL_ENRIQUECIDO_V1.json` | `5446da1294cee6311dcef3a0c5438b7c7de2bc2adec586fe38b85f199394305d` | `5446da1294cee6311dcef3a0c5438b7c7de2bc2adec586fe38b85f199394305d` | 69418 | 69418 | **BYTE_IDENTICAL** |
| `enrichment_decisions` | `C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\ENRIQUECIDO_V1\DECISOES_ENRIQUECIMENTO.json` | `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\REPLAY_ENRIQUECIDO_V1\DECISOES_ENRIQUECIMENTO.json` | `de779c2f5873d665953d849d37643e21219da428df89b534a24781b8031e8c30` | `de779c2f5873d665953d849d37643e21219da428df89b534a24781b8031e8c30` | 116799 | 116799 | **BYTE_IDENTICAL** |
| `enriched_evidence_cards` | `C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\ENRIQUECIDO_V1\EVIDENCE_CARDS_ENRIQUECIDOS_V1.json` | `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\REPLAY_ENRIQUECIDO_V1\EVIDENCE_CARDS_ENRIQUECIDOS_V1.json` | `3446c073eda030045bc20efe0ac0854c924fe7b11e66a71d0671d6717f054a07` | `3446c073eda030045bc20efe0ac0854c924fe7b11e66a71d0671d6717f054a07` | 607221 | 607221 | **BYTE_IDENTICAL** |
| `enriched_metadata` | `C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\ENRIQUECIDO_V1\METADADOS_ENRIQUECIDO_V1.json` | `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\REPLAY_ENRIQUECIDO_V1\METADADOS_ENRIQUECIDO_V1.json` | `27a427ccd18813992f633e8f94bb59e8a2e46a1d6558b95d8c37ef7e037c2f02` | `27a427ccd18813992f633e8f94bb59e8a2e46a1d6558b95d8c37ef7e037c2f02` | 11588 | 11588 | **BYTE_IDENTICAL** |
| `enriched_readme` | `C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\ENRIQUECIDO_V1\README.md` | `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\REPLAY_ENRIQUECIDO_V1\README.md` | `423b90dde03d10cd268681b55f18e6fa51007fd1af939d09b80be952a2cbe9e3` | `423b90dde03d10cd268681b55f18e6fa51007fd1af939d09b80be952a2cbe9e3` | 1269 | 1269 | **BYTE_IDENTICAL** |
| `enriched_inner_manifest` | `C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\ENRIQUECIDO_V1\MANIFEST.json` | `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\d05-replay-2026-09-27-a5b\workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200\07_CATALOGO_CANDIDATO\REPLAY_ENRIQUECIDO_V1\MANIFEST.json` | `0312e5f091981f8065673529aca04437ed0fc7ecaac26cd144d2af26ab37774c` | `0312e5f091981f8065673529aca04437ed0fc7ecaac26cd144d2af26ab37774c` | 1044 | 1044 | **BYTE_IDENTICAL** |

Resultado agregado: **9/9 BYTE_IDENTICAL**.

## 8. Cardinalidades observadas

- Obras utilizáveis: **199**.
- Cards-base: **221**.
- Cards novos: **71**.
- Cards finais: **292**.
- Decisões aplicadas/obras examinadas: **111**.
- Revisões aplicadas: **3**.

Todas coincidem com os valores previstos e com a referência histórica.

## 9. `MANIFEST.json`

`gerar_manifest.py` não foi executado. O único manifesto produzido foi `REPLAY_ENRIQUECIDO_V1/MANIFEST.json`, criado naturalmente por `compilar_enriquecido_v1.py`; ele é **BYTE_IDENTICAL** ao manifesto interno histórico, SHA-256 `0312e5f091981f8065673529aca04437ed0fc7ecaac26cd144d2af26ab37774c`.

## 10. Seleção efetivamente observada

- P1 leu 8 lotes explícitos, 199 dossiês-base e a referência 69; depois leu os dois outputs para calcular seus hashes.
- P2 leu o catálogo-base replayado, 111 overlays, o checkpoint, as revisões e a referência 69; depois leu os sete outputs para hashes e manifesto.
- A ordem completa observada está em `observed_reads` no run record.

A comparação formal dessa ordem com o Dataset Lock foi reservada para A6.

## 11. Integridade do repositório original

- Baseline e pós-execução dos arquivos funcionais relevantes: **MATCH**.
- HEAD: `73ce4d81d2e424a21bfe523eacc9d6134a99a2e9`.
- Nenhum arquivo tracked modificado; staging vazio.
- Registry: **PASS**, 855 ocorrências, zero erros, órfãos e conflitos.
- Dataset Lock: **PASS**, todos os cinco matches verdadeiros e zero extras.
- Golden Reference: SHA-256 `f82e82d9c3907186e916a54436493ebe8f426d1a09f7b3a3aa3b092c2e09cdc7`.
- Integridade dirigida: V2 281/281, protected545 545/545, IDX 130/130, ENRIQUECIDO_V1 7/7 e política de bytes intacta.

## 12. Evidências, limitações e condição para A6

Logs, audit trails, inputs copiados, outputs e o run record operacional permanecem no sandbox. A proteção é um audit hook do CPython validado por testes negativos para o escopo desses dois scripts locais. Nenhuma fase remota, editorial, de saneamento ou de geração externa de manifesto foi executada.

A A5B comprova reprodução byte a byte dos nove outputs. A comparação formal da seleção observada com o Dataset Lock pertence à A6 e não foi iniciada.

## Resultado

`MIGRACAO_A5B_CONCLUIDA — REPLAY_D05_BYTE_IDENTICO`
