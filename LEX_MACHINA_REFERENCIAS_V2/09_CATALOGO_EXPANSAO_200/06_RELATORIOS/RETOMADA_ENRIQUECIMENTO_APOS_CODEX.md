# Retomada do enriquecimento após a interrupção do Codex

Levantamento feito em 2026-09-26, **antes de qualquer pesquisa nova**.

- Dados por obra: `ESTADO_ENRIQUECIMENTO_APOS_CODEX.json`.
- Script de reconstrução: `relatorios_enriquecimento_v1.py`, que apenas lê os artefatos do Codex.

## Ponto real de retomada

O handoff reportava 8 checkpoints, 77 obras e 58 cards. Os arquivos mostram mais do que isso:

| Item | Handoff | Arquivos reais |
|---|---|---|
| Checkpoints | 8 | **12** (`CHECKPOINTS_ENRIQUECIMENTO/CP_01..CP_12.json`) |
| Obras examinadas | 77 | **111**: toda a fila |
| Cards novos | 58 | **71** |

- **Último checkpoint válido:** CP_12, gravado em 2026-09-26T20:46:12Z.
- **Trabalho após o CP_08 que ficou persistido:**
  - checkpoints CP_09 a CP_12;
  - 34 obras: documentários 152–160 e livros 166–200;
  - 13 cards novos.
- **O que faltou:** o Codex gravou tudo isso, mas não apresentou o fechamento. `CHECKPOINT_ENRIQUECIMENTO.json` ainda estava com `estado: EM_ANDAMENTO`.

**Obras pendentes: nenhuma.** A fila do Codex tinha 111 obras (as estimativas "+1" e "+2 ou mais" de `ESTIMATIVA_ENRIQUECIMENTO.json`), e as 111 têm overlay e decisão. As outras 88 obras utilizáveis ("completa provável") ficaram fora da fila por desenho da missão do Codex. Isso está registrado como tal, não como pendência.

## Artefatos do Codex encontrados (preservados sem alteração)

- **Scripts** em `06_RELATORIOS/`:
  - `enriquecer_v1.py`: baseline, fila e checkpoints append-only;
  - `consultar_fontes_enriquecimento.py`: coleta, guardando só metadados;
  - `editorial_enriquecimento_v1.py`: as decisões dos lotes 1–12.
- **Estado e integridade:** `CHECKPOINT_ENRIQUECIMENTO.json` (fila e 12 checkpoints) e `BASELINE_ENRIQUECIMENTO_V1.json` (hashes do estado de partida).
- **Correções:** `CORRECOES_DURANTE_ENRIQUECIMENTO.json`, que estava vazio.
- **Registros de coleta** em `03_FONTES/ENRIQUECIMENTO_V1/`: 128 arquivos, sendo 122 `PAGINA_CONSULTADA` e 6 `FALHA_DE_ACESSO` (403/406).
- **Overlays** em `04_DOSSIERS/ENRIQUECIMENTO_V1/`: 111 arquivos, com a decisão e os cards adicionais de cada obra. Os dossiês de base não foram tocados.
- **Arquivos intermediários:** `CONSULTA_CP11.txt` e `CONSULTA_CP12.txt` (saída bruta de consulta, com texto de páginas). Ficam para a auditoria de limpeza.

## Verificação do trabalho do Codex

- Todos os 71 cards têm `not_targeted_to_device: true` e fonte marcada `PAGINA_CONSULTADA`.
- 9 cards usam fontes abertas pela ferramenta web do Codex e não têm registro local de coleta. **Verifiquei os 9 nas páginas**, e todos foram confirmados:
  - DOC-008-E02, DOC-016-E02, DOC-034-E02;
  - JOG-005-E02, JOG-015-E02, JOG-038-E02, JOG-041-E02, JOG-049-E02;
  - LIV-040-E02.

  Os casos que exigiram outro meio de acesso:
  - **Konami e Rockstar:** abertas pelo navegador por causa do bloqueio anti-robô;
  - **The Cleaners:** press kit em PDF, com o texto extraído localmente;
  - **SICAV (#159):** o script do Codex registrou falha 406, mas a página abre normalmente e sustenta o card.
- **Os destaques citados no handoff foram conferidos nos arquivos.** Uma divergência: os "pontos de intuição" são de **L.A. Noire** (#5, JOG-005-E02, fonte Rockstar Support), não de Disco Elysium. O card de Disco Elysium (JOG-001-E02) trata de 24 habilidades e do Thought Cabinet.

## Modificações feitas

Os overlays do Codex **não foram reescritos**. Encontrei três violações objetivas do §7 da política: cards de episódio ou temporada sem `unidade_documental`. Elas foram corrigidas numa camada de revisão aplicada na compilação (`REVISOES_ENRIQUECIMENTO_V1.json`) e registradas em `CORRECOES_DURANTE_ENRIQUECIMENTO.json`:

- **EXP2-DOC-013-E03:** Dirty Money, T2E2 "O homem no topo". Episódio identificado na página oficial da Netflix.
- **EXP2-DOC-013-E04:** Dirty Money, T2E4 "Ouro sujo".
- **EXP2-SER-012-E02:** American Crime, Temporada 2.

Nenhum card foi removido e nenhum texto de claim foi alterado.
