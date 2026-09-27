# Saneamento pré-enriquecimento — V1

Data: 2026-09-26. Missão curta, com quatro tarefas: resolver as candidatas em revisão, reavaliar Cyberpunk 2077, auditar uma amostra dos lotes 1–4 e escrever a política de enriquecimento.

Nesta missão **a Engine não foi executada**, não houve enriquecimento em massa, nenhum vínculo jurídico foi gerado, nada foi alterado na ontologia e nenhuma pasta foi limpa.

## 1. Pendências FONTE_EM_REVISAO

| # | Obra | Antes | Depois | Base |
|---|---|---|---|---|
| 41 | Kingdom Come: Deliverance II | FONTE_EM_REVISAO | APTA_COM_RESSALVA | Deep Silver (publisher; kingdomcomerpg.com redireciona para lá) e PlayStation Store, ambas tier A e consultadas |
| 113 | Black Mirror | FONTE_EM_REVISAO | APTA_COM_RESSALVA | Netflix Tudum, tier A, página baixada (sha256 `af0b443c…`) |
| 142 | Terms and Conditions May Apply | FONTE_EM_REVISAO | APTA_COM_RESSALVA | Marquette University e-Publications (B), entrevista com o diretor no The Next Web (C) e site oficial tacma.net (Hyrax Films) |

**#41 Kingdom Come II.** A premissa narrativa pretendida foi confirmada e delimitada: guerra civil na Boêmia do século XV, ataque das forças de Sigismundo, vingança de Henry e entrada na resistência. Gerou 1 card CENTRAL. Nenhuma mecânica específica foi documentada; "as ações moldam o mundo" é genérico e foi descartado.

**#113 Black Mirror.** Adotei a estrutura A: obra agregadora única, com evidências explicitamente vinculadas a episódios (`unidade_documental`, `escopo_centralidade: EPISODIO`). Os três episódios, todos com fatos delimitados na página oficial, são:

- T3E1 "Nosedive": pontuação social que condiciona trabalho e moradia;
- T1E3 "The Entire History of You": implantes que gravam memórias;
- T7E1 "Common People": contrato de assinatura do qual depende a vida da protagonista.

Nenhum episódio virou obra nova.

**#142 Terms and Conditions May Apply.** Os snippets de busca anteriores não foram aceitos como evidência final e ficam só como apoio de identidade. Gerou 2 cards: um CENTRAL (fonte B) e um FORTE (entrevista primária, fonte C).

## 2. Cyberpunk 2077

- **Decisão:** REJEITADA_EVIDENCIA_FRACA → **APTA_COM_RESSALVA**. Detalhes em `DECISAO_CYBERPUNK_REVISADA.json`.
- **Pergunta A** (a obra não tem evidência delimitável?): **não**.
- **Pergunta B** (a fonte usada antes era insuficiente?): **sim**. Era a descrição da Steam, ampla e promocional. A rejeição do Codex estava correta para aquela fonte.
- **Evidências aceitas** (site oficial da CD PROJEKT RED):
  - **CENTRAL narrativa:** o chip implantado sobrescreve a personalidade de V com a de Johnny Silverhand;
  - **FORTE mecânica:** implantes que aprimoram o corpo e hacking na construção do personagem.
- **Evidências rejeitadas:**
  - ambientação geral (poder corporativo, desigualdade);
  - ficha do personagem Adam Smasher;
  - "escolhas importam";
  - classes não documentadas (dados, polícia, contratos, trabalho);
  - expansão Phantom Liberty.

## 3. Auditoria amostral dos lotes 1–4

Detalhes em `AUDITORIA_LOTES_1_4.md` e `AMOSTRA_AUDITORIA_LOTES_1_4.json`.

| Classificação | Obras |
|---|---|
| AUDITORIA_OK | 15 |
| AJUSTE_MENOR | 3 (#44, #51, #88) |
| AJUSTE_IMPORTANTE | 1 (#80) |
| FONTE_INSUFICIENTE | 1 (#100) |

- **Taxa de problemas importantes:** 10%. Pela regra da missão, os lotes 1–4 são **satisfatórios por amostragem**. Uma segunda amostra é opcional e não bloqueia; não foi executada.
- **Correções:** 5 dossiês corrigidos (4 paráfrases que iam além da fonte e 1 link morto). Nenhuma decisão editorial dos lotes 1–4 mudou por causa da auditoria.

## 4. Política de enriquecimento

Criada em `POLITICA_ENRIQUECIMENTO_EVIDENCE_CARDS_V1.md`. A estimativa obra a obra está em `ESTIMATIVA_ENRIQUECIMENTO.json`.

| Estimativa | Obras |
|---|---|
| Provavelmente completas | 88 |
| +1 card | 93 |
| +2 ou mais | 18 |

É estimativa, não meta, e **nada foi executado**.

## 5. Contagens atualizadas

| Métrica | Antes | Depois |
|---|---|---|
| APTA | 28 | 28 |
| APTA_COM_RESSALVA | 167 | 171 |
| FONTE_EM_REVISAO | 3 | 0 |
| REJEITADA_EVIDENCIA_FRACA | 1 | 0 |
| REJEITADA_DUPLICATA_EXISTENTE | 1 | 1 |
| **Utilizáveis** | **195** | **199** |
| **Evidence cards** | **213** | **221** (+2 Cyberpunk, +1 KCD2, +3 Black Mirror, +2 Terms) |
| Total potencial 69 + utilizáveis | 264 | 268 |

A soma continua 200. Os 221 cards seguem com `not_targeted_to_device: true`.

## 6. Recompilação e rastreabilidade

- **Arquivos alterados** (somente os estritamente necessários): `02_TRIAGEM/LOTE_01..06`, `01_IDENTIDADE/LOTE_01..06` e os arquivos de `03_FONTES` e `04_DOSSIERS` dos 9 candidatos afetados.
- **Hashes antes e depois:** `REVISOES_POS_CHECKPOINT.json`. O `CHECKPOINT_LOTES.json` permanece como registro histórico de fechamento, e `estado_retomada.py` reconhece as revisões registradas.
- **Catálogo recompilado:**

| Arquivo | Antes | Depois |
|---|---|---|
| CATALOGO_EXPANSAO_200.json | `8f107e65…` | `5764d749…` |
| CATALOGO_TOTAL_69_MAIS_APTAS.json | `5c31b224…` | `6bf04fec…` |

  Duas compilações e o artefato local são idênticos (`DETERMINISMO_COMPILACAO.json`).
- **Relatórios regenerados:** `METRICAS_FINAIS`, `REJEICOES`, `FONTE_EM_REVISAO` (agora vazio), `JOGOS_EXPANSAO`, `COBERTURA_EDITORIAL`, `CORRECOES_ENTRADA`, `REDUNDANCIA_69_MAIS_200` e `ESTADO_FINAL`.

## 7. Próximo passo recomendado

1. **Enriquecimento pelo Codex,** sob `POLITICA_ENRIQUECIMENTO_EVIDENCE_CARDS_V1.md`, começando pelas 18 obras "+2 ou mais" e pelos jogos com card só mecânico ou só narrativo.
2. **Auditoria determinística de 20 cards novos** antes de qualquer ingestão.
3. **Mapeamento na ontologia congelada** (`ONTOLOGY_GAP`), numa missão própria e anterior à Engine R1D1.
