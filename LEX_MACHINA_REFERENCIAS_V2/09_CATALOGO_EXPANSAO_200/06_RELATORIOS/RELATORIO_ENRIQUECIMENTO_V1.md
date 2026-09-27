# Relatório — Enriquecimento de evidence cards V1

Concluído em 2026-09-26. O enriquecimento foi executado pelo Codex e fechado pelo Claude.

A Engine não foi executada, nenhum vínculo jurídico foi gerado, a ontologia não foi mapeada e nenhum arquivo foi limpo.

## Resumo

| Indicador | Valor |
|---|---|
| Cards antes | **221** |
| Ponto real de retomada | CP_12 (20:46:12Z): 12 checkpoints, 111 obras, 71 cards. O handoff dizia CP_08, 77 obras e 58 cards |
| Obras examinadas pelo Codex | **111** (toda a fila); 34 delas após o CP_08, persistidas mas sem fechamento |
| Obras examinadas pelo Claude | **0 novas**: nenhuma pendente. O trabalho foi de validação, revisão, deduplicação, auditoria e congelamento |
| Cards novos do Codex | **71** |
| Cards novos do Claude | **0** |
| Cards totais | **292** |
| Obras +0 (SEM_CARD_ADICIONAL_JUSTIFICADO) | **47** |
| Obras +1 | **57** |
| Obras +2 | **7**: Crusader Kings III, Orwell: Ignorance is Strength, This Is the Police, Contraband Police, The Red Strings Club, Dirty Money, Holocausto Brasileiro |
| Obras +3 ou mais | **0** |
| Obras fora da fila (completa provável) | 88, sem alteração |
| Jogos enriquecidos | **37** dos 49 jogos da fila; 42 cards novos em jogos |
| Novos MECANICA_INTERATIVA | **29** (total no pacote: 64) |
| Novos EVENTO_NARRATIVO | **15** (total no pacote: 116) |
| Outros novos | 9 ARGUMENTO_ACADEMICO, 9 ARGUMENTO_DOCUMENTAL, 5 EVENTO_HISTORICO, 4 PRATICA_INSTITUCIONAL |
| Centralidade dos novos | 11 CENTRAL, 58 FORTE, 2 PONTUAL |
| Fontes dos cards novos, por tier | Cards: A 57, B 13, C 1. URLs distintas: 64 (A 51, B 12, C 1) |
| Registros de coleta do Codex | 128 (122 consultados, 6 com falha de acesso) |
| Cards rejeitados pelo Codex (candidatos recusados) | **12**, com motivo registrado em cada decisão |
| Duplicações | 81 pares comparados, 14 triados e revisados; **0 confirmadas**, **0 removidas** |
| Auditoria (20 cards novos, menores SHA-256 do evidence_id) | 19 AUDITORIA_OK, 1 AJUSTE_MENOR |
| Problemas importantes | **0 / 20 = 0%** |
| Gate | **PASSA** |

## Revisões e verificações adicionais

**Revisões.** Três cards receberam a marcação de unidade documental que faltava (§7 da política), aplicada na compilação sem alterar os overlays do Codex. Registro em `REVISOES_ENRIQUECIMENTO_V1.json`.

- Dirty Money: T2E2 "O homem no topo" e T2E4 "Ouro sujo".
- American Crime: Temporada 2.

**Proveniência.** Os 9 cards cuja fonte o Codex abriu pela ferramenta web, sem registro local de coleta, foram verificados um a um. Todos foram confirmados.

**Divergência no handoff.** Os "pontos de intuição" pertencem a L.A. Noire (JOG-005-E02), não a Disco Elysium.

## Determinismo

**Catálogo base.** Foi recompilado duas vezes e os hashes são idênticos aos atuais: o catálogo base não mudou e não foi substituído.

| Arquivo | SHA-256 |
|---|---|
| CATALOGO_EXPANSAO_200.json | `5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43` |
| CATALOGO_TOTAL_69_MAIS_APTAS.json | `6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6` |

**Pacote ENRIQUECIDO_V1.** Foi compilado três vezes (duas no scratchpad e uma no local final), e as três saídas são idênticas byte a byte:

| Arquivo | SHA-256 |
|---|---|
| CATALOGO_EXPANSAO_ENRIQUECIDO_V1.json | `cddb00344f6e3075f552fb042b168d184463b85e513f695eb1089139ee301da7` |
| CATALOGO_TOTAL_ENRIQUECIDO_V1.json | `5446da1294cee6311dcef3a0c5438b7c7de2bc2adec586fe38b85f199394305d` |
| EVIDENCE_CARDS_ENRIQUECIDOS_V1.json | `3446c073eda030045bc20efe0ac0854c924fe7b11e66a71d0671d6717f054a07` |
| DECISOES_ENRIQUECIMENTO.json | `de779c2f5873d665953d849d37643e21219da428df89b534a24781b8031e8c30` |
| METADADOS_ENRIQUECIDO_V1.json | `27a427ccd18813992f633e8f94bb59e8a2e46a1d6558b95d8c37ef7e037c2f02` |
| README.md | `423b90dde03d10cd268681b55f18e6fa51007fd1af939d09b80be952a2cbe9e3` |
| MANIFEST.json | `0312e5f091981f8065673529aca04437ed0fc7ecaac26cd144d2af26ab37774c` |

Os 6 hashes listados no manifesto do pacote foram revalidados.

## Integridade

Detalhes em `08_MANIFEST/INTEGRIDADE_DEPOIS.json`.

| Item | Resultado |
|---|---|
| Congelados da V2 | 281/281 idênticos |
| Engine R1D1 | 65/65 |
| RC1 | 15/15 |
| RC2 | 6/6 |
| Holdout | 3/3 |
| Ontologia e contratos | 37/37 |
| Catálogo original 69 | sha256 igual ao declarado |
| Firmware | hash `62f256e4…` inalterado |
| IDX | 130 arquivos, nenhum alterado |
| SD | não tocado |
| Arquivos fora da pasta da missão | 0 alterados |

## Arquivos desta etapa

- **Relatórios em `06_RELATORIOS/`:**
  - `RETOMADA_ENRIQUECIMENTO_APOS_CODEX.md` e `ESTADO_ENRIQUECIMENTO_APOS_CODEX.json`;
  - `DEDUPLICACAO_EVIDENCE_CARDS_V1.json/.md`;
  - `AUDITORIA_CARDS_ENRIQUECIMENTO_V1.json`;
  - `REVISOES_ENRIQUECIMENTO_V1.json`;
  - `relatorios_enriquecimento_v1.py`;
  - este relatório.
- **Registros acrescentados em arquivos do Codex:**
  - `CHECKPOINT_ENRIQUECIMENTO.json`: registro de fechamento em `registros_pos_codex`; os 12 checkpoints foram preservados;
  - `CORRECOES_DURANTE_ENRIQUECIMENTO.json`: 3 registros.
- **Pacote:** `07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py` e `07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/` (7 arquivos).

## Para a auditoria de limpeza (não executada)

Candidatos a revisar:

- `06_RELATORIOS/CONSULTA_CP11.txt` e `CONSULTA_CP12.txt`: saída bruta com texto de páginas de terceiros;
- `03_FONTES/BUSCA_*.json` e `STEAM_*.json`: coletas brutas;
- scripts de uso único dos lotes (`lote01.py`, `lote02.py`, `from_table.py`);
- `BASELINE_ENRIQUECIMENTO_V1.json`.

Nada foi removido.
