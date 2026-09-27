# Onda 2A — plano de arquivamento histórico

**Somente planejamento. Nenhum arquivo funcional foi movido, apagado, renomeado, compactado ou deduplicado. A Onda 2B não foi executada.**

Checkpoint confirmado: `53c419ab9c3b0bbd264d580fcc174e54681e9cc1`. Retomada dos artefatos parciais de 26/09, validada em 27/09/2026. O inventário, os grupos de duplicatas e as buscas anteriores foram reaproveitados; nenhuma auditoria global ou hashing global novo foi executado.

Foram analisadas **81 unidades**, em **7 famílias**, com **23.379 arquivos e 2.921.061.459 bytes** (2,921 GB decimais). São 76 pastas da raiz e 5 subpastas de firmware. A estimativa antiga de cerca de 70 pastas não era uma lista exata. As unidades não se sobrepõem.

## Resultado da classificação

| Classificação | Pastas | Arquivos | Bytes |
|---|---:|---:|---:|
| ARQUIVAR_ONDA2B | 1 | 5 | 49.357 |
| ARQUIVAR_APOS_AJUSTE | 17 | 283 | 7.721.328 |
| BLOQUEADO_POR_PROTECTED545 | 55 | 22.598 | 2.888.909.303 |
| MANTER_ATIVA | 0 | 0 | 0 |
| REVISAR_MANUALMENTE | 8 | 493 | 24.381.471 |

`MANTER_ATIVA = 0` nesta tabela significa zero entre as 81 unidades históricas analisadas. `updater`, o sketch ativo, V2 e adaptador 69 permanecem ativos fora do escopo de arquivamento. A baseline física v7.12, J4 e CF_SEGMENTADA_V2 têm papel operacional, mas foram classificados pelo bloqueio mais forte: protected545.

## Famílias e estado ativo

| Família | Unidades | Estado ativo / evidência |
|---|---:|---|
| UPDATER_ETAPAS | 32 | `updater`. Pipeline operacional em updater. Etapas preservam a cadeia de preparação de correlatas; 2E41 é consumida pelo montador 2E6, não se presume ativa por numeração. Evidência: `CLEANUP_AUDIT/MAPA_PASTAS_ATUAL.md`; `updater/implantar_sd.py:344`; `updater/relations_v2.py:13`. |
| RELATIONS_VERSOES_ANTIGAS | 2 | `updater/relations_v2.py`; `updater/saida`. Implementação versionada usa catálogo e saida locais. Cópias históricas ainda contêm IDX protegidos. Evidência: `updater/relations_v2.py:13`; `updater/relations_v2.py:320`. |
| REFERENCIAS_V1 | 34 | `LEX_MACHINA_REFERENCIAS_V2`; `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1`. V2 é a linha atual de provas, isolada do produto; V1 continua fonte de evidências e rótulos. Sucessão não dispensa os caminhos antigos. Evidência: `LEX_MACHINA_REFERENCIAS_V2/README.md`; `LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/consolidate_labels.py:56`; `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/adaptar_catalogo_69.py:9`. |
| JURIS_CF_ETAPAS | 6 | `LEX_MACHINA_JURIS_CF_J4`; `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA`. J4 é o corpus da baseline física validada. J4_6 não foi promovida a ativa apenas pelo nome. Evidência: `HISTORICO_RELEASES.md:7`; `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/test_capacidade_juris_v7120.py:11`. |
| FIRMWARE_ANTIGO | 5 | `firmware/LEX_MACHINA.ino`; `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA`. Sketch de trabalho e baseline física imutável têm papéis distintos. A v7.12 permanece bloqueada pelo protected545 e necessária como baseline. Evidência: `CLEANUP_AUDIT/MAPA_PASTAS_ATUAL.md`; `HISTORICO_RELEASES.md:3`. |
| BACKUPS_MANUAIS | 1 | `updater`; `updater/backup_sd`. Backup histórico não substitui updater ativo; backup_sd é prova de implantação e não é descartável. Evidência: `CLEANUP_AUDIT/GIT_VERSIONING_PLAN.md`; `updater/implantar_sd.py:347`. |
| OUTROS_LEGADOS | 1 | `CF_SEGMENTADA_V2`; `LEX_MACHINA_REFERENCIAS_V2`. CF_SEGMENTADA_V2 é entrada ainda consumida. Não há sucessora substitutiva confirmada. Evidência: `LEX_MACHINA_REFERENCIAS_V2/05_COMPILADOR/prepare_expansion.py:17`; `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/adaptar_catalogo_69.py:12`. |

O README geral e o README de firmware ainda descrevem a estrutura inicial. O histórico de releases, os checkpoints e os scripts existentes têm evidência mais específica do estado atual; não foi inferida atividade pelo maior número da versão.

## Critérios, dependências e conteúdo único

- Protected545 é veto a mover a pasta inteira. Todas as 34 árvores de referências anteriores, CF_SEGMENTADA_V2, as maiores cópias do updater e as cinco unidades de firmware têm esse bloqueio. Não se propõe retirar apenas os arquivos não protegidos.
- `LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/consolidate_labels.py:56` descobre `LEX_MACHINA_REFERENCIAS*` por glob. A engine, os benchmarks e o adaptador 69 também têm dependências explícitas de árvores anteriores.
- `gerar_manifest.py:50` e `enriquecer_v1.py:28` procuram IDX pela árvore. Todos os 130 IDX continuam em seus paths.
- As menções em `INTEGRITY_BEFORE.json` → `git_before`, `INTEGRITY_FINAL.json` → `git_status` e `INTEGRITY_R1C_FINAL.json` → `git_status` são HISTORICA. As entradas efetivas de `files` e os hashes de baseline permanecem CRITICA. Nenhuma referência foi alterada.
- Receitas de etapas apontam para os resultados de etapas anteriores. A pasta 2E41, por exemplo, é default do montador SD preservado em `LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/montar_sd_teste_relations_v2.py:46`. Isso é motivo para ajuste prévio, sem executar o montador.
- Único na unidade significa sem cópia conhecida fora da pasta, segundo os hashes existentes; não significa que seja dado descartável. O JSON lista cada arquivo único, natureza, bytes, hash, cobertura Git/snapshot e referências. A classificação por natureza é indicativa, com DESCONHECIDO explícito.
- A cobertura do snapshot é por arquivo, não por nome de pasta. Nenhuma das 26 unidades sem protected545 está integralmente protegida pelo snapshot ou pelo Git; todas têm cobertura zero nesses dois mecanismos. A proposta de baixo risco preserva sua unidade e redundância interna, sem alegar backup independente.

Referências absolutas externas às unidades: **171 registros alvo/fonte/linha**, em 167 linhas distintas. Dessas, **122 referências ativas** em 122 linhas. São 64 arestas adicionais por descoberta dinâmica. Estes números medem o corpus delimitado, não qualquer dependência possível.

## Tabela completa das unidades

Duplicação é a porcentagem de arquivos com cópia fora da unidade. Únicos são os que não têm cópia externa conhecida. Ref. é a quantidade de referências ativas sem os registros históricos de Git; fontes/linhas estão no JSON. Bytes são lógicos, incluindo caches e ambientes.

| Pasta | Família | Bytes | Arquivos | Dup. % | Únicos / bytes | P545 | Ref. | Classe | Risco |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `1- LEX-MACHINAETAPA_2D3` | UPDATER_ETAPAS | 255.003.071 | 2.060 | 83.93 | 331 / 31.687.295 | 9 | 20 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `CF_SEGMENTADA_V2` | OUTROS_LEGADOS | 1.733.591 | 5 | 0.00 | 5 / 1.733.591 | 5 | 923 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX-MACHINAETAPA_2C` | UPDATER_ETAPAS | 225.107.994 | 1.734 | 99.02 | 17 / 1.866.236 | 9 | 20 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX-MACHINAETAPA_2D` | UPDATER_ETAPAS | 225.551.763 | 1.736 | 99.48 | 9 / 2.285.316 | 9 | 20 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX-MACHINAETAPA_2D10` | UPDATER_ETAPAS | 191.937 | 11 | 9.09 | 10 / 191.901 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D11` | UPDATER_ETAPAS | 222.508 | 12 | 8.33 | 11 / 222.472 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D12` | UPDATER_ETAPAS | 1.127.159 | 35 | 68.57 | 11 / 257.803 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D13` | UPDATER_ETAPAS | 297.192 | 12 | 8.33 | 11 / 297.145 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D14` | UPDATER_ETAPAS | 317.678 | 12 | 8.33 | 11 / 317.631 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D15` | UPDATER_ETAPAS | 365.122 | 12 | 8.33 | 11 / 365.075 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D16` | UPDATER_ETAPAS | 352.185 | 11 | 0.00 | 11 / 352.185 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D17` | UPDATER_ETAPAS | 56.208 | 8 | 0.00 | 8 / 56.208 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D2` | UPDATER_ETAPAS | 224.619.125 | 1.739 | 99.42 | 10 / 1.303.349 | 9 | 20 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX-MACHINAETAPA_2D4` | UPDATER_ETAPAS | 1.512.426 | 80 | 1.25 | 79 / 1.512.390 | 0 | 0 | REVISAR_MANUALMENTE | ALTO |
| `LEX-MACHINAETAPA_2D5` | UPDATER_ETAPAS | 552.521 | 24 | 4.17 | 23 / 552.485 | 0 | 0 | REVISAR_MANUALMENTE | ALTO |
| `LEX-MACHINAETAPA_2D6` | UPDATER_ETAPAS | 55.328 | 10 | 0.00 | 10 / 55.328 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D6_1` | UPDATER_ETAPAS | 56.716 | 10 | 0.00 | 10 / 56.716 | 0 | 0 | REVISAR_MANUALMENTE | ALTO |
| `LEX-MACHINAETAPA_2D6_2` | UPDATER_ETAPAS | 46.578 | 8 | 37.50 | 5 / 46.198 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D6_3` | UPDATER_ETAPAS | 48.501 | 8 | 37.50 | 5 / 48.121 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2D6_4` | UPDATER_ETAPAS | 166.471 | 12 | 8.33 | 11 / 166.434 | 0 | 0 | REVISAR_MANUALMENTE | ALTO |
| `LEX-MACHINAETAPA_2D7` | UPDATER_ETAPAS | 14.748.414 | 200 | 6.00 | 188 / 14.640.327 | 0 | 0 | REVISAR_MANUALMENTE | ALTO |
| `LEX-MACHINAETAPA_2D8` | UPDATER_ETAPAS | 6.618.625 | 137 | 32.85 | 92 / 3.378.428 | 0 | 0 | REVISAR_MANUALMENTE | ALTO |
| `LEX-MACHINAETAPA_2D9` | UPDATER_ETAPAS | 2.102.330 | 36 | 72.22 | 10 / 224.820 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2E` | UPDATER_ETAPAS | 95.971 | 9 | 0.00 | 9 / 95.971 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2E1` | UPDATER_ETAPAS | 120.570 | 10 | 0.00 | 10 / 120.570 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2E2` | UPDATER_ETAPAS | 737.743 | 29 | 58.62 | 12 / 119.428 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2E3` | UPDATER_ETAPAS | 683.641 | 25 | 68.00 | 8 / 65.337 | 0 | 0 | REVISAR_MANUALMENTE | MEDIO |
| `LEX-MACHINAETAPA_2E31` | UPDATER_ETAPAS | 743.503 | 29 | 68.97 | 9 / 82.227 | 0 | 0 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2E4` | UPDATER_ETAPAS | 49.357 | 5 | 20.00 | 4 / 47.651 | 0 | 0 | ARQUIVAR_ONDA2B | BAIXO |
| `LEX-MACHINAETAPA_2E41` | UPDATER_ETAPAS | 840.815 | 31 | 70.97 | 9 / 140.628 | 0 | 1 | ARQUIVAR_APOS_AJUSTE | MEDIO |
| `LEX-MACHINAETAPA_2E5` | UPDATER_ETAPAS | 292.452 | 14 | 35.71 | 9 / 196.192 | 4 | 10 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX-MACHINA_ETAPA_2E6_SD_TESTE` | UPDATER_ETAPAS | 732.697 | 31 | 90.32 | 3 / 16.475 | 8 | 18 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_JURIS_CF_J1` | JURIS_CF_ETAPAS | 42.657 | 5 | 0.00 | 5 / 42.657 | 0 | 0 | REVISAR_MANUALMENTE | MEDIO |
| `LEX_MACHINA_JURIS_CF_J2` | JURIS_CF_ETAPAS | 347.908 | 14 | 21.43 | 11 / 257.784 | 2 | 6 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_JURIS_CF_J2_5` | JURIS_CF_ETAPAS | 260.073 | 13 | 23.08 | 10 / 169.949 | 2 | 6 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_JURIS_CF_J3` | JURIS_CF_ETAPAS | 40.864 | 35 | 5.71 | 33 / 33.797 | 2 | 6 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_JURIS_CF_J4` | JURIS_CF_ETAPAS | 7.436.773 | 84 | 5.95 | 79 / 7.186.751 | 2 | 7 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_JURIS_CF_J4_6` | JURIS_CF_ETAPAS | 279.831 | 229 | 0.87 | 227 / 221.869 | 2 | 6 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_AUDITORIA_ASTRA_V1` | REFERENCIAS_V1 | 653.063 | 7 | 0.00 | 7 / 653.063 | 7 | 206 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_AUDITORIA_CAUSAL_V132_V1` | REFERENCIAS_V1 | 1.029.253 | 17 | 5.88 | 16 / 359.999 | 17 | 20 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_AUDITORIA_CONTRATO_ENGINE_V1` | REFERENCIAS_V1 | 162.521 | 10 | 0.00 | 10 / 162.521 | 10 | 11 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_AVALIACAO_J5_LOTE45_V1` | REFERENCIAS_V1 | 165.113 | 8 | 0.00 | 8 / 165.113 | 8 | 9 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_AVALIACAO_J5_LOTE45_V2_FINAL` | REFERENCIAS_V1 | 590.169 | 11 | 0.00 | 11 / 590.169 | 11 | 22 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_BENCHMARK_69_HUMANO_V1` | REFERENCIAS_V1 | 669.254 | 1 | 100.00 | 0 / 0 | 1 | 299 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_BENCHMARK_CF_V2` | REFERENCIAS_V1 | 393.760 | 9 | 0.00 | 9 / 393.760 | 9 | 371 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_CATALOGO_EXPANSAO_V1` | REFERENCIAS_V1 | 127.575 | 7 | 0.00 | 7 / 127.575 | 7 | 8 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_CATALOGO_LOTE_45_V1` | REFERENCIAS_V1 | 316.045 | 8 | 0.00 | 8 / 316.045 | 8 | 9 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_CATALOGO_LOTE_45_V2` | REFERENCIAS_V1 | 413.109 | 6 | 0.00 | 6 / 413.109 | 6 | 21 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_CF_ENGINE_RUN_V1` | REFERENCIAS_V1 | 7.965.659 | 11 | 0.00 | 11 / 7.965.659 | 11 | 14 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_CF_J5` | REFERENCIAS_V1 | 100.385 | 6 | 0.00 | 6 / 100.385 | 6 | 7 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_CF_J5_1` | REFERENCIAS_V1 | 81.566 | 2 | 0.00 | 2 / 81.566 | 2 | 3 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_CF_REVISAO_ALTA_CONFIANCA_V1` | REFERENCIAS_V1 | 503.841 | 9 | 0.00 | 9 / 503.841 | 9 | 12 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_DIAGNOSTICO_NUCLEOS_V1` | REFERENCIAS_V1 | 238.381 | 8 | 0.00 | 8 / 238.381 | 8 | 9 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_ENGINE_V1` | REFERENCIAS_V1 | 307.228 | 18 | 22.22 | 14 / 254.530 | 18 | 23 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_ENGINE_V1_1` | REFERENCIAS_V1 | 283.371 | 21 | 52.38 | 10 / 156.641 | 21 | 26 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_ENGINE_V1_2` | REFERENCIAS_V1 | 282.107 | 31 | 35.48 | 20 / 155.377 | 31 | 43 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_ENGINE_V1_3` | REFERENCIAS_V1 | 705.636 | 15 | 0.00 | 15 / 705.636 | 15 | 19 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_ENGINE_V1_3_1` | REFERENCIAS_V1 | 819.539 | 15 | 0.00 | 15 / 819.539 | 15 | 19 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_ENGINE_V1_3_2` | REFERENCIAS_V1 | 941.487 | 17 | 0.00 | 17 / 941.487 | 17 | 22 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_ENGINE_V1_4_ALPHA` | REFERENCIAS_V1 | 52.129 | 7 | 0.00 | 7 / 52.129 | 7 | 8 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_ENGINE_V1_4_ALPHA2` | REFERENCIAS_V1 | 45.079 | 7 | 0.00 | 7 / 45.079 | 7 | 8 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_ENGINE_V1_4_ALPHA3` | REFERENCIAS_V1 | 35.676 | 11 | 0.00 | 11 / 35.676 | 11 | 12 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_EXPERIMENTO_24_VS_69_V1` | REFERENCIAS_V1 | 27.973.403 | 16 | 0.00 | 16 / 27.973.403 | 16 | 17 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_FORCA_TEMA_LOTE45_V1_FINAL` | REFERENCIAS_V1 | 664.888 | 11 | 0.00 | 11 / 664.888 | 11 | 170 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_PREPARACAO_V14_ALPHA2` | REFERENCIAS_V1 | 191.835 | 11 | 0.00 | 11 / 191.835 | 11 | 70 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_REFINAMENTO_R7_V2` | REFERENCIAS_V1 | 57.922 | 8 | 0.00 | 8 / 57.922 | 8 | 21 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_TEMAS_LOTE45_V1` | REFERENCIAS_V1 | 408.005 | 9 | 0.00 | 9 / 408.005 | 9 | 10 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_TESTE_COMPLETO_ALPHA3_V1` | REFERENCIAS_V1 | 8.620.157 | 14 | 0.00 | 14 / 8.620.157 | 14 | 22 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_VALIDACAO_EXTERNA_R7_V1` | REFERENCIAS_V1 | 154.331 | 5 | 0.00 | 5 / 154.331 | 5 | 6 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_VALIDACAO_V14_ALPHA` | REFERENCIAS_V1 | 917.002 | 12 | 0.00 | 12 / 917.002 | 12 | 23 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_VALIDACAO_V14_ALPHA2` | REFERENCIAS_V1 | 465.601 | 8 | 0.00 | 8 / 465.601 | 8 | 19 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_REFERENCIAS_VALIDACAO_V14_ALPHA3` | REFERENCIAS_V1 | 415.175 | 7 | 0.00 | 7 / 415.175 | 7 | 153 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_UPDATER_BACKUP_V1_17-09-2026` | BACKUPS_MANUAIS | 456.585.722 | 4.197 | 98.33 | 70 / 566.095 | 9 | 20 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_UPDATER_RELATIONS_V2` | RELATIONS_VERSOES_ANTIGAS | 223.029.243 | 1.696 | 99.59 | 7 / 32.589 | 9 | 20 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `LEX_MACHINA_UPDATER_RELATIONS_V2_ETAPA2A` | RELATIONS_VERSOES_ANTIGAS | 252.414.298 | 1.704 | 99.59 | 7 / 29.379.185 | 9 | 20 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `updater_stage2a_corrigida_v2` | UPDATER_ETAPAS | 954.305.408 | 6.911 | 99.22 | 54 / 61.553.240 | 36 | 74 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `firmware/LEX MAQUINA INO 2` | FIRMWARE_ANTIGO | 914.952 | 7 | 42.86 | 4 / 236.401 | 7 | 8 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `firmware/LEX_MACHINA_BACKUP_POS_CODEX_16-09` | FIRMWARE_ANTIGO | 831.728 | 4 | 75.00 | 1 / 155.375 | 4 | 5 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `firmware/LEX_MACHINA_v7.11.0_JURIS_CF_PILOTO` | FIRMWARE_ANTIGO | 882.401 | 6 | 50.00 | 3 / 203.850 | 6 | 7 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `firmware/LEX_MACHINA_v7.11.1_JURIS_CF_PILOTO` | FIRMWARE_ANTIGO | 890.116 | 7 | 57.14 | 3 / 204.404 | 7 | 9 | BLOQUEADO_POR_PROTECTED545 | ALTO |
| `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA` | FIRMWARE_ANTIGO | 899.028 | 9 | 44.44 | 5 / 213.316 | 9 | 10 | BLOQUEADO_POR_PROTECTED545 | ALTO |

## Datas, função, sucessão e justificativas por unidade

### 1- LEX-MACHINAETAPA_2D3

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-07T09:01:34+00:00 a 2026-09-19T14:32:06+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 90; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DESCONHECIDO=2, CACHE=3, RAW_SOURCE=316, CODIGO=2, OUTPUT=8.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### CF_SEGMENTADA_V2

Constituição segmentada e scripts, insumo preservado das referências. Modificação aproximada: 2026-09-22T16:46:36+00:00 a 2026-09-22T16:46:44+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 5; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=2, DOCUMENTACAO=1, CODIGO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 5 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX-MACHINAETAPA_2C

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-07T09:01:34+00:00 a 2026-09-19T13:49:41+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 90; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: CACHE=3, OUTPUT=12, RAW_SOURCE=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX-MACHINAETAPA_2D

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-07T09:01:34+00:00 a 2026-09-19T13:57:40+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 90; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: CACHE=1, OUTPUT=6, RAW_SOURCE=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX-MACHINAETAPA_2D10

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T15:50:22+00:00 a 2026-09-19T18:49:26+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D11`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=5.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D11/etapa2d11_work/LEIA_ME_ETAPA_2D11.txt:51`.

### LEX-MACHINAETAPA_2D11

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T15:56:28+00:00 a 2026-09-19T18:55:24+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D12`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=6.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D12/etapa2d12_work/LEIA_ME_ETAPA_2D12.txt:41`.

### LEX-MACHINAETAPA_2D12

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T16:04:39+00:00 a 2026-09-19T19:01:58+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D13`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=6.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D13/etapa2d13_work/LEIA_ME_ETAPA_2D13.txt:63`.

### LEX-MACHINAETAPA_2D13

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T16:11:19+00:00 a 2026-09-19T19:10:24+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D14`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=6.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D14/etapa2d14_work/LEIA_ME_ETAPA_2D14.txt:55`.

### LEX-MACHINAETAPA_2D14

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T16:20:32+00:00 a 2026-09-19T19:17:00+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D15`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=6.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D15/etapa2d15_work/LEIA_ME_ETAPA_2D15.txt:5`.

### LEX-MACHINAETAPA_2D15

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T17:59:16+00:00 a 2026-09-19T20:58:32+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D16`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=6.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D16/etapa2d16_work/LEIA_ME_ETAPA_2D16.txt:37`.

### LEX-MACHINAETAPA_2D16

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T18:06:49+00:00 a 2026-09-19T21:06:12+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D17`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=6.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D17/etapa2d17_work/LEIA_ME_ETAPA_2D17.txt:22`.

### LEX-MACHINAETAPA_2D17

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T18:11:47+00:00 a 2026-09-19T21:10:46+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2E`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=3.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2E/etapa2e_work/LEIA_ME_ETAPA_2E.txt:21`.

### LEX-MACHINAETAPA_2D2

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-07T09:01:34+00:00 a 2026-09-19T14:08:23+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 90; manifests: sim.

Sucessoras/consumidoras documentadas: `1- LEX-MACHINAETAPA_2D3`. Natureza dos únicos: CACHE=1, OUTPUT=7, RAW_SOURCE=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

Dependências exemplificadas: `1- LEX-MACHINAETAPA_2D3/LEIA-ME_ETAPA_2D3.txt:6`.

### LEX-MACHINAETAPA_2D4

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T14:43:25+00:00 a 2026-09-19T14:46:13+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D5`, `LEX-MACHINAETAPA_2D7`. Natureza dos únicos: DOCUMENTACAO=1, DESCONHECIDO=1, CACHE=2, RAW_SOURCE=64, CODIGO=2, OUTPUT=9.

**REVISAR_MANUALMENTE — risco ALTO.** Capturas oficiais únicas na unidade; ausência de cobertura integral no snapshot. Alta duplicação não comprova dispensabilidade das fontes.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D5/etapa2d5_work/LEIA_ME_ETAPA_2D5.txt:15`; `LEX-MACHINAETAPA_2D7/etapa2d7_work/LEIA_ME_ETAPA_2D7.txt:46`.

### LEX-MACHINAETAPA_2D5

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T14:50:06+00:00 a 2026-09-19T14:53:56+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D6`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=2, CODIGO=2, OUTPUT=11, RAW_SOURCE=6.

**REVISAR_MANUALMENTE — risco ALTO.** Capturas oficiais únicas na unidade; ausência de cobertura integral no snapshot. Alta duplicação não comprova dispensabilidade das fontes.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D6/etapa2d6_work/LEIA_ME_ETAPA_2D6.txt:13`.

### LEX-MACHINAETAPA_2D6

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T15:01:15+00:00 a 2026-09-19T18:00:18+00:00. Conteúdo: codigo, dados, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D6_1`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CODIGO=2, OUTPUT=6.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D6_1/etapa2d6_1_work/LEIA_ME_ETAPA_2D6_1.txt:12`.

### LEX-MACHINAETAPA_2D6_1

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T15:04:11+00:00 a 2026-09-19T18:02:52+00:00. Conteúdo: codigo, dados, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D6_2`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CODIGO=1, OUTPUT=5, RAW_SOURCE=2.

**REVISAR_MANUALMENTE — risco ALTO.** Capturas oficiais únicas na unidade; ausência de cobertura integral no snapshot. Alta duplicação não comprova dispensabilidade das fontes.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D6_2/etapa2d6_2_work/LEIA_ME_ETAPA_2D6_2.txt:12`.

### LEX-MACHINAETAPA_2D6_2

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T15:06:34+00:00 a 2026-09-19T18:05:46+00:00. Conteúdo: codigo, dados, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D6_3`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CODIGO=1, OUTPUT=2.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D6_3/etapa2d6_3_work/LEIA_ME_ETAPA_2D6_3.txt:17`.

### LEX-MACHINAETAPA_2D6_3

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T15:09:46+00:00 a 2026-09-19T18:08:34+00:00. Conteúdo: codigo, dados, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D6_4`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CODIGO=1, OUTPUT=2.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D6_4/etapa2d6_4_work/LEIA_ME_ETAPA_2D6_4.txt:38`.

### LEX-MACHINAETAPA_2D6_4

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T15:16:58+00:00 a 2026-09-19T18:14:36+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=4, RAW_SOURCE=2.

**REVISAR_MANUALMENTE — risco ALTO.** Capturas oficiais únicas na unidade; ausência de cobertura integral no snapshot. Alta duplicação não comprova dispensabilidade das fontes.

### LEX-MACHINAETAPA_2D7

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T15:24:44+00:00 a 2026-09-19T18:23:10+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D8`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, RAW_SOURCE=177, CODIGO=2, OUTPUT=6.

**REVISAR_MANUALMENTE — risco ALTO.** Capturas oficiais únicas na unidade; ausência de cobertura integral no snapshot. Alta duplicação não comprova dispensabilidade das fontes.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D8/etapa2d8_work/LEIA_ME_ETAPA_2D8.txt:29`.

### LEX-MACHINAETAPA_2D8

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T15:32:43+00:00 a 2026-09-19T18:31:46+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D9`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=6, RAW_SOURCE=81.

**REVISAR_MANUALMENTE — risco ALTO.** Capturas oficiais únicas na unidade; ausência de cobertura integral no snapshot. Alta duplicação não comprova dispensabilidade das fontes.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D9/etapa2d9_work/LEIA_ME_ETAPA_2D9.txt:47`.

### LEX-MACHINAETAPA_2D9

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T15:43:59+00:00 a 2026-09-19T18:41:32+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2D10`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=5.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2D10/etapa2d10_work/LEIA_ME_ETAPA_2D10.txt:37`.

### LEX-MACHINAETAPA_2E

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T18:17:34+00:00 a 2026-09-19T21:16:32+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2E4`, `LEX-MACHINAETAPA_2E41`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=4.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2E4/etapa2e4_work/LEIA_ME_ETAPA_2E4.txt:30`; `LEX-MACHINAETAPA_2E41/etapa2e4_work/LEIA_ME_ETAPA_2E4.txt:32`.

### LEX-MACHINAETAPA_2E1

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T18:28:20+00:00 a 2026-09-19T21:27:10+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2E2`, `LEX-MACHINAETAPA_2E4`, `LEX-MACHINAETAPA_2E41`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=5.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2E2/etapa2e2_work/LEIA_ME_ETAPA_2E2.txt:18`; `LEX-MACHINAETAPA_2E4/etapa2e4_work/LEIA_ME_ETAPA_2E4.txt:29`.

### LEX-MACHINAETAPA_2E2

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T18:34:44+00:00 a 2026-09-19T21:33:56+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2E3`, `LEX-MACHINAETAPA_2E31`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=7.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2E3/etapa2e3_work/LEIA_ME_ETAPA_2E3.txt:18`; `LEX-MACHINAETAPA_2E31/etapa2e31_work/LEIA_ME_ETAPA_2E31.txt:23`.

### LEX-MACHINAETAPA_2E3

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T18:35:09+00:00 a 2026-09-19T21:38:54+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=2, OUTPUT=3.

**REVISAR_MANUALMENTE — risco MEDIO.** Há conteúdo único sem cobertura independente; não foi comprovada sua dispensabilidade para a reprodução histórica.

### LEX-MACHINAETAPA_2E31

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T18:35:09+00:00 a 2026-09-19T21:42:54+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2E4`, `LEX-MACHINAETAPA_2E41`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=2, CACHE=1, CODIGO=2, OUTPUT=3.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2E4/etapa2e4_work/LEIA_ME_ETAPA_2E4.txt:31`; `LEX-MACHINAETAPA_2E4/etapa2e4_work/LEIA_ME_ETAPA_2E4.txt:32`.

### LEX-MACHINAETAPA_2E4

Protótipo de fusão CF 2E.4; pacote com código, teste, instruções e bytecode, sem dados de saída. Modificação aproximada: 2026-09-19T18:49:54+00:00 a 2026-09-19T21:48:14+00:00. Conteúdo: codigo, caches. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2E41`. Natureza dos únicos: OUTPUT=1, DOCUMENTACAO=1, CACHE=1, CODIGO=1.

**ARQUIVAR_ONDA2B — risco BAIXO.** Protótipo substituído pela correção 2E.4.1 documentada. Sem IDX, fontes primárias, dados curados, outputs operacionais ou referência ativa ao path. Cinco arquivos conferidos; ZIP existente replica integralmente os quatro arquivos de conteúdo. Teste de 2E41 resolve o script local à própria pasta.

### LEX-MACHINAETAPA_2E41

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-13T11:38:22+00:00 a 2026-09-19T20:41:26+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX-MACHINAETAPA_2E5`, `LEX-MACHINA_ETAPA_2E6_SD_TESTE`. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=1, CODIGO=1, OUTPUT=5.

**ARQUIVAR_APOS_AJUSTE — risco MEDIO.** Receitas de reprodução ou ferramenta preservada dependem deste path. Conteúdo único e cobertura de segurança ainda precisam ser resolvidos no plano futuro.

Dependências exemplificadas: `LEX-MACHINAETAPA_2E5/etapa2e5_work/LEIA_ME_ETAPA_2E5.txt:33`; `LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/montar_sd_teste_relations_v2.py:46`.

### LEX-MACHINAETAPA_2E5

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T20:49:46+00:00 a 2026-09-19T23:48:20+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 4; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CACHE=3, CODIGO=2, OUTPUT=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 4 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX-MACHINA_ETAPA_2E6_SD_TESTE

Etapa de coleta, validação ou montagem de relações constitucionais; função específica nos scripts e LEIA_ME listados. Modificação aproximada: 2026-09-19T18:35:09+00:00 a 2026-09-20T00:24:36+00:00. Conteúdo: codigo. Git: 0 arquivos; snapshot: 8; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DESCONHECIDO=1, DOCUMENTACAO=1, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 8 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_JURIS_CF_J1

Auditoria inicial, plano J2 e schema canônico proposto de jurisprudência. Modificação aproximada: 2026-09-21T15:13:31+00:00 a 2026-09-21T15:16:38+00:00. Conteúdo: dados. Git: 0 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: `LEX_MACHINA_JURIS_CF_J2`. Natureza dos únicos: DOCUMENTACAO=4, DADO_CURADO=1.

**REVISAR_MANUALMENTE — risco MEDIO.** Schema canônico/proposta contratual única e documentação inicial não cobertos pelo snapshot/Git. Nenhuma dependência ativa literal foi encontrada, mas isso não basta para liberar a unidade.

### LEX_MACHINA_JURIS_CF_J2

Etapa da série de jurisprudência CF; J4 é baseline física, demais estados mantêm evidências próprias. Modificação aproximada: 2026-09-21T15:33:51+00:00 a 2026-09-21T16:10:51+00:00. Conteúdo: codigo, dados, caches. Git: 0 arquivos; snapshot: 2; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=5, DOCUMENTACAO=1, CACHE=2, CODIGO=3.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 2 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_JURIS_CF_J2_5

Etapa da série de jurisprudência CF; J4 é baseline física, demais estados mantêm evidências próprias. Modificação aproximada: 2026-09-21T16:07:35+00:00 a 2026-09-21T16:13:01+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 2; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=3, DADO_CURADO=5, CODIGO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 2 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_JURIS_CF_J3

Etapa da série de jurisprudência CF; J4 é baseline física, demais estados mantêm evidências próprias. Modificação aproximada: 2026-09-21T16:19:48+00:00 a 2026-09-21T22:43:40+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 2; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=2, DOCUMENTACAO=2, DESCONHECIDO=27, CODIGO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 2 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_JURIS_CF_J4

Etapa da série de jurisprudência CF; J4 é baseline física, demais estados mantêm evidências próprias. Modificação aproximada: 2026-09-21T21:47:38+00:00 a 2026-09-21T22:43:46+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 2; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=7, RAW_SOURCE=60, DOCUMENTACAO=10, CODIGO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 2 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_JURIS_CF_J4_6

Etapa da série de jurisprudência CF; J4 é baseline física, demais estados mantêm evidências próprias. Modificação aproximada: 2026-09-21T22:37:45+00:00 a 2026-09-21T22:43:41+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 2; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=3, DESCONHECIDO=221, DADO_CURADO=1, CODIGO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 2 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_AUDITORIA_ASTRA_V1

Histórico de referências: auditoria astra v1. Modificação aproximada: 2026-09-23T22:01:45+00:00 a 2026-09-23T22:11:54+00:00. Conteúdo: dados. Git: 0 arquivos; snapshot: 7; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=5, DADO_CURADO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 7 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_AUDITORIA_CAUSAL_V132_V1

Histórico de referências: auditoria causal v132 v1. Modificação aproximada: 2026-09-23T15:14:04+00:00 a 2026-09-23T15:38:42+00:00. Conteúdo: codigo, dados, caches. Git: 0 arquivos; snapshot: 16; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=12, DOCUMENTACAO=2, CACHE=1, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 17 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_AUDITORIA_CONTRATO_ENGINE_V1

Histórico de referências: auditoria contrato engine v1. Modificação aproximada: 2026-09-23T12:11:16+00:00 a 2026-09-23T12:11:56+00:00. Conteúdo: codigo, dados, caches. Git: 0 arquivos; snapshot: 9; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=6, DOCUMENTACAO=2, CACHE=1, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 10 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_AVALIACAO_J5_LOTE45_V1

Histórico de referências: avaliacao j5 lote45 v1. Modificação aproximada: 2026-09-23T12:19:34+00:00 a 2026-09-23T12:21:00+00:00. Conteúdo: codigo, dados, caches. Git: 0 arquivos; snapshot: 7; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=4, DOCUMENTACAO=2, CACHE=1, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 8 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_AVALIACAO_J5_LOTE45_V2_FINAL

Histórico de referências: avaliacao j5 lote45 v2 final. Modificação aproximada: 2026-09-23T12:36:40+00:00 a 2026-09-23T12:38:13+00:00. Conteúdo: codigo, dados, caches. Git: 0 arquivos; snapshot: 10; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=8, DOCUMENTACAO=1, CACHE=1, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 11 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_BENCHMARK_69_HUMANO_V1

Histórico de referências: benchmark 69 humano v1. Modificação aproximada: 2026-09-23T15:38:42+00:00 a 2026-09-23T15:38:42+00:00. Conteúdo: dados. Git: 0 arquivos; snapshot: 1; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: .

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 1 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_BENCHMARK_CF_V2

Histórico de referências: benchmark cf v2. Modificação aproximada: 2026-09-22T14:06:36+00:00 a 2026-09-22T14:07:03+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 9; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=6, DOCUMENTACAO=1, CODIGO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_CATALOGO_EXPANSAO_V1

Histórico de referências: catalogo expansao v1. Modificação aproximada: 2026-09-23T01:02:28+00:00 a 2026-09-23T01:03:06+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 7; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=5, DOCUMENTACAO=1, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 7 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_CATALOGO_LOTE_45_V1

Histórico de referências: catalogo lote 45 v1. Modificação aproximada: 2026-09-23T01:33:40+00:00 a 2026-09-23T02:20:09+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 8; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=4, DOCUMENTACAO=3, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 8 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_CATALOGO_LOTE_45_V2

Histórico de referências: catalogo lote 45 v2. Modificação aproximada: 2026-09-23T02:46:31+00:00 a 2026-09-23T02:47:06+00:00. Conteúdo: dados. Git: 0 arquivos; snapshot: 6; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=5, DOCUMENTACAO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 6 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_CF_ENGINE_RUN_V1

Histórico de referências: cf engine run v1. Modificação aproximada: 2026-09-22T10:07:30+00:00 a 2026-09-23T14:41:59+00:00. Conteúdo: codigo, dados, caches. Git: 0 arquivos; snapshot: 10; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=7, DOCUMENTACAO=1, CACHE=1, CODIGO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 11 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_CF_J5

Histórico de referências: cf j5. Modificação aproximada: 2026-09-21T23:40:29+00:00 a 2026-09-21T23:44:08+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 6; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=3, DOCUMENTACAO=1, CODIGO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 6 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_CF_J5_1

Histórico de referências: cf j5 1. Modificação aproximada: 2026-09-21T23:52:13+00:00 a 2026-09-21T23:52:13+00:00. Conteúdo: documentação/artefatos. Git: 0 arquivos; snapshot: 2; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 2 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_CF_REVISAO_ALTA_CONFIANCA_V1

Histórico de referências: cf revisao alta confianca v1. Modificação aproximada: 2026-09-22T10:16:33+00:00 a 2026-09-22T10:19:33+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 9; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=5, DOCUMENTACAO=2, CODIGO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_DIAGNOSTICO_NUCLEOS_V1

Histórico de referências: diagnostico nucleos v1. Modificação aproximada: 2026-09-23T17:53:53+00:00 a 2026-09-23T18:04:28+00:00. Conteúdo: codigo, dados, caches. Git: 0 arquivos; snapshot: 7; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=5, DOCUMENTACAO=1, CACHE=1, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 8 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_ENGINE_V1

Histórico de referências: engine v1. Modificação aproximada: 2026-09-22T01:34:15+00:00 a 2026-09-22T02:41:18+00:00. Conteúdo: codigo, dados, outputs. Git: 0 arquivos; snapshot: 18; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=2, CODIGO=8, DADO_CURADO=2, OUTPUT=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 18 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_ENGINE_V1_1

Histórico de referências: engine v1 1. Modificação aproximada: 2026-09-22T01:34:15+00:00 a 2026-09-22T02:41:18+00:00. Conteúdo: codigo, dados, outputs. Git: 0 arquivos; snapshot: 21; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=2, CODIGO=4, OUTPUT=4.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 21 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_ENGINE_V1_2

Histórico de referências: engine v1 2. Modificação aproximada: 2026-09-22T01:34:15+00:00 a 2026-09-23T14:41:59+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 24; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=3, DADO_CURADO=1, CACHE=7, CODIGO=5, OUTPUT=4.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 31 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_ENGINE_V1_3

Histórico de referências: engine v1 3. Modificação aproximada: 2026-09-22T16:55:30+00:00 a 2026-09-23T14:41:59+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 12; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=1, CODIGO=5, CACHE=3, OUTPUT=5, DOCUMENTACAO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 15 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_ENGINE_V1_3_1

Histórico de referências: engine v1 3 1. Modificação aproximada: 2026-09-22T17:19:51+00:00 a 2026-09-23T14:41:59+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 13; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=1, CODIGO=4, CACHE=2, OUTPUT=7, DOCUMENTACAO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 15 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_ENGINE_V1_3_2

Histórico de referências: engine v1 3 2. Modificação aproximada: 2026-09-22T17:48:16+00:00 a 2026-09-23T14:41:59+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 15; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=2, DADO_CURADO=1, CODIGO=4, CACHE=2, OUTPUT=8.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 17 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_ENGINE_V1_4_ALPHA

Histórico de referências: engine v1 4 alpha. Modificação aproximada: 2026-09-23T15:35:38+00:00 a 2026-09-23T16:58:35+00:00. Conteúdo: codigo, caches. Git: 0 arquivos; snapshot: 5; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=1, CODIGO=4, CACHE=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 7 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_ENGINE_V1_4_ALPHA2

Histórico de referências: engine v1 4 alpha2. Modificação aproximada: 2026-09-23T16:38:14+00:00 a 2026-09-23T17:01:36+00:00. Conteúdo: codigo, caches. Git: 0 arquivos; snapshot: 5; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=1, CODIGO=4, CACHE=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 7 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_ENGINE_V1_4_ALPHA3

Histórico de referências: engine v1 4 alpha3. Modificação aproximada: 2026-09-23T19:40:25+00:00 a 2026-09-23T19:44:21+00:00. Conteúdo: codigo, caches. Git: 0 arquivos; snapshot: 7; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=1, CODIGO=6, CACHE=4.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 11 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_EXPERIMENTO_24_VS_69_V1

Histórico de referências: experimento 24 vs 69 v1. Modificação aproximada: 2026-09-23T14:44:05+00:00 a 2026-09-23T14:45:42+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 16; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=13, DOCUMENTACAO=2, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 16 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_FORCA_TEMA_LOTE45_V1_FINAL

Histórico de referências: forca tema lote45 v1 final. Modificação aproximada: 2026-09-23T13:05:22+00:00 a 2026-09-23T13:07:05+00:00. Conteúdo: codigo, dados, caches. Git: 0 arquivos; snapshot: 10; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=8, DOCUMENTACAO=1, CACHE=1, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 11 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_PREPARACAO_V14_ALPHA2

Histórico de referências: preparacao v14 alpha2. Modificação aproximada: 2026-09-23T16:04:39+00:00 a 2026-09-23T16:04:39+00:00. Conteúdo: dados. Git: 0 arquivos; snapshot: 11; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=9, DOCUMENTACAO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 11 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_REFINAMENTO_R7_V2

Histórico de referências: refinamento r7 v2. Modificação aproximada: 2026-09-23T19:34:13+00:00 a 2026-09-23T19:34:29+00:00. Conteúdo: codigo, dados. Git: 0 arquivos; snapshot: 8; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=6, DOCUMENTACAO=1, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 8 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_TEMAS_LOTE45_V1

Histórico de referências: temas lote45 v1. Modificação aproximada: 2026-09-23T12:52:09+00:00 a 2026-09-23T12:52:57+00:00. Conteúdo: codigo, dados, caches. Git: 0 arquivos; snapshot: 8; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=5, DOCUMENTACAO=2, CACHE=1, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_TESTE_COMPLETO_ALPHA3_V1

Histórico de referências: teste completo alpha3 v1. Modificação aproximada: 2026-09-23T19:58:17+00:00 a 2026-09-23T20:01:36+00:00. Conteúdo: dados. Git: 0 arquivos; snapshot: 14; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=4, DADO_CURADO=10.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 14 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_VALIDACAO_EXTERNA_R7_V1

Histórico de referências: validacao externa r7 v1. Modificação aproximada: 2026-09-23T18:04:28+00:00 a 2026-09-23T18:04:28+00:00. Conteúdo: dados. Git: 0 arquivos; snapshot: 5; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=3, DOCUMENTACAO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 5 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_VALIDACAO_V14_ALPHA

Histórico de referências: validacao v14 alpha. Modificação aproximada: 2026-09-23T17:03:22+00:00 a 2026-09-23T17:03:22+00:00. Conteúdo: dados. Git: 0 arquivos; snapshot: 12; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=11, DOCUMENTACAO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 12 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_VALIDACAO_V14_ALPHA2

Histórico de referências: validacao v14 alpha2. Modificação aproximada: 2026-09-23T19:44:33+00:00 a 2026-09-23T19:44:33+00:00. Conteúdo: dados. Git: 0 arquivos; snapshot: 8; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=7, DOCUMENTACAO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 8 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_REFERENCIAS_VALIDACAO_V14_ALPHA3

Histórico de referências: validacao v14 alpha3. Modificação aproximada: 2026-09-23T19:44:33+00:00 a 2026-09-23T19:44:33+00:00. Conteúdo: dados. Git: 0 arquivos; snapshot: 7; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DADO_CURADO=6, DOCUMENTACAO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 7 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_UPDATER_BACKUP_V1_17-09-2026

Backup manual do updater, incluindo ambiente Python e outputs. Modificação aproximada: 2026-09-07T12:01:34+00:00 a 2026-09-17T01:25:18+00:00. Conteúdo: codigo, dados, venv, caches, outputs. Git: 0 arquivos; snapshot: 90; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: AMBIENTE=48, CACHE=20, RAW_SOURCE=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_UPDATER_RELATIONS_V2

Snapshot do updater com a camada de relações V2. Modificação aproximada: 2026-09-07T09:01:34+00:00 a 2026-09-18T20:02:27+00:00. Conteúdo: codigo, dados, outputs. Git: 0 arquivos; snapshot: 90; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: OUTPUT=5, RAW_SOURCE=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### LEX_MACHINA_UPDATER_RELATIONS_V2_ETAPA2A

Snapshot do updater com a camada de relações V2. Modificação aproximada: 2026-09-07T09:01:34+00:00 a 2026-09-18T20:13:16+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 90; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DESCONHECIDO=1, CACHE=3, CODIGO=1, RAW_SOURCE=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### updater_stage2a_corrigida_v2

Coleção aninhada de snapshots stage2a/2b/2c/2d do updater. Modificação aproximada: 2026-09-07T09:01:34+00:00 a 2026-09-19T13:35:50+00:00. Conteúdo: codigo, dados, caches, outputs. Git: 0 arquivos; snapshot: 360; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DESCONHECIDO=2, CACHE=7, OUTPUT=37, RAW_SOURCE=8.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 36 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### firmware/LEX MAQUINA INO 2

Versão ou backup de firmware; v7.12 também é baseline física validada. Modificação aproximada: 2026-09-12T19:48:37+00:00 a 2026-09-21T02:43:46+00:00. Conteúdo: codigo. Git: 6 arquivos; snapshot: 1; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=2, CODIGO=1, DESCONHECIDO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 7 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### firmware/LEX_MACHINA_BACKUP_POS_CODEX_16-09

Versão ou backup de firmware; v7.12 também é baseline física validada. Modificação aproximada: 2026-09-12T19:48:37+00:00 a 2026-09-17T02:52:18+00:00. Conteúdo: codigo. Git: 0 arquivos; snapshot: 4; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 4 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### firmware/LEX_MACHINA_v7.11.0_JURIS_CF_PILOTO

Versão ou backup de firmware; v7.12 também é baseline física validada. Modificação aproximada: 2026-09-12T19:48:37+00:00 a 2026-09-21T16:34:32+00:00. Conteúdo: codigo. Git: 0 arquivos; snapshot: 6; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=2, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 6 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### firmware/LEX_MACHINA_v7.11.1_JURIS_CF_PILOTO

Versão ou backup de firmware; v7.12 também é baseline física validada. Modificação aproximada: 2026-09-12T19:48:37+00:00 a 2026-09-21T21:07:58+00:00. Conteúdo: codigo. Git: 0 arquivos; snapshot: 7; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=2, CODIGO=1.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 7 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

### firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA

Versão ou backup de firmware; v7.12 também é baseline física validada. Modificação aproximada: 2026-09-12T19:48:37+00:00 a 2026-09-21T22:38:31+00:00. Conteúdo: codigo. Git: 9 arquivos; snapshot: 0; manifests: sim.

Sucessoras/consumidoras documentadas: não confirmadas; ver estado ativo da família. Natureza dos únicos: DOCUMENTACAO=3, CODIGO=2.

**BLOQUEADO_POR_PROTECTED545 — risco ALTO.** Contém 9 caminhos da prova protected545. Arquivamento integral tornaria a prova inválida, independentemente da duplicação.

## Lotes futuros e ganho operacional

**LOTE 1 — piloto de risco baixo:** somente `LEX-MACHINAETAPA_2E4` (5 arquivos; 49.357 bytes). A sucessora 2E41 se identifica como correção da criação de saída em seu LEIA_ME. O teste dessa sucessora carrega o script da própria pasta. Os cinco hashes do candidato e os quatro membros do ZIP existente foram conferidos; não há dados de saída, fontes primárias ou IDX na unidade. Nenhum código crítico único ativo foi identificado. A unidade contém código histórico único e deve ser preservada inteira; o ZIP no mesmo diretório não equivale a backup independente.

**LOTE 2 — risco baixo adicional:** vazio. Nenhuma inclusão por semelhança de nome ou por duplicação.

**LOTE 3 — requer ajustes:** as 17 unidades ARQUIVAR_APOS_AJUSTE. Há receitas de reprodução com caminhos atuais e/ou consumo pelo montador preservado. Preparar proposta separada de remapeamento da invocação e proteção dos únicos, sem editar artefatos congelados. Depois reclassificar e dividir em uma pasta ou cadeia validada por lote.

**LOTE REVISÃO:** oito unidades REVISAR_MANUALMENTE. Seis têm capturas oficiais únicas; J1 contém schema/proposta contratual única; 2E3 tem resultados únicos cuja dispensabilidade histórica não foi comprovada.

**LOTE BLOQUEADO:** 55 unidades com protected545. Não existe proposta de movimentação automática nem de desmontagem parcial.

Cada lote futuro deve ter autorização própria, destino absoluto revisado e sem colisão, conjunto exato de paths e hashes, registro de custódia e rollback. Validar os hashes da unidade e as provas protegidas após a movimentação; criar commit documental do lote antes de considerar o seguinte. Uma divergência interrompe o lote. O JSON tem `execucao_autorizada=false`, destinos nulos e listas condicionais; não é um script de execução.

**TAMANHO_LOGICO_ARQUIVADO previsto:** 49.357 bytes e uma entrada a menos na raiz, somente se o lote 1 for futuramente aprovado. **ESPACO_FISICO_REAL_RECUPERADO: 0 bytes demonstrados.** Mover no mesmo disco não libera esse volume. Nada foi movimentado nesta missão. Não foi criada a pasta conceitual `_ARCHIVE_PRE_CLEANUP_2026-09/`.

## Ambientes virtuais

| Path | Arquivos | Bytes | Situação |
|---|---:|---:|---|
| `LEX_MACHINA_UPDATER_BACKUP_V1_17-09-2026/.venv` | 1847 | 139.365.847 | Exclusivo do backup histórico; pasta bloqueada por P545 |
| `updater/.venv` | 1847 | 139.365.847 | Aparentemente ativo: updater operacional |

Total: **2 ambientes, 278.731.694 bytes**, incluindo os caches internos. Há requirements nos diretórios pais. Nenhuma execução, alteração ou remoção de `.venv`; a política será decidida em outra onda.

## Validação e limites

Na retomada, HEAD e status coincidiram com o checkpoint e os metadados de todos os 28.844 arquivos existentes permaneceram idênticos ao registro parcial. A verificação de integridade existente retornou PASSA: protected545 545/545, IDX 130/130, V2 281/281, firmware, catálogo 69, Engine, RC1/RC2, holdout, ontologia/contratos, ENRIQUECIDO_V1, snapshot e bundle válidos. Foram lidos scripts; nenhum pipeline/Engine/teste de hardware foi executado.

O único hashing dirigido novo para a elegibilidade foi dos cinco arquivos do lote 1 e dos membros do ZIP já existente. A verificação constitucional reutilizou o verificador anterior. Duplicação e natureza do restante usam a auditoria existente, com tamanho/mtime conferidos; todos os hashes do lote futuro devem ser revalidados antes de mover. A busca excluiu ambientes/caches/capturas e grandes dados não operacionais; não prova ausência absoluta de caminhos construídos dinamicamente.

Verificação após gerar os relatórios: **PASSA**. Os 28.844 arquivos anteriores mantêm tamanho e mtime; nenhum path anterior foi removido ou acrescentado fora dos dois relatórios. Somente `WAVE2_ARCHIVE_PLAN.md` e `WAVE2_ARCHIVE_PLAN.json` foram criados. A integridade constitucional foi novamente validada com PASSA; os totais e os bloqueios do plano foram conferidos. Commit documental local: `docs: plan historical archive cleanup wave`. Tag anotada local: `pre-cleanup-wave2-2026-09-26`, mensagem `Archive plan before LEX MACHINA cleanup wave 2`. O commit/tag efetivos são verificáveis pelo Git; nenhuma publicação remota.

**Próximo passo:** revisão humana do plano e decisão específica sobre o lote 1. A Onda 2B depende de nova autorização.

ONDA_2A_PLANEJADA — AGUARDANDO_REVISAO
