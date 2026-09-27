# ENRIQUECIDO_V1 — pacote congelado

Catálogo candidato enriquecido da expansão de 200 candidatas (`status_catalogo = CANDIDATO_NAO_INTEGRADO`).

- Obras utilizáveis: 199 (28 APTA + 171 APTA_COM_RESSALVA).
- Evidence cards: 292 (221 da base + 71 do enriquecimento V1).
- Todos os cards: `not_targeted_to_device: true`; `ONTOLOGY_GAP` preservado (sem mapeamento ontológico).
- Engine não executada; nenhum vínculo jurídico; catálogo base (`../CATALOGO_EXPANSAO_200.json`) não foi substituído.

## Arquivos

- `CATALOGO_EXPANSAO_ENRIQUECIDO_V1.json`: 199 obras com cards base + novos.
- `CATALOGO_TOTAL_ENRIQUECIDO_V1.json`: 69 obras congeladas + 199 candidatas (visão resumida).
- `EVIDENCE_CARDS_ENRIQUECIDOS_V1.json`: lista plana de todos os cards, com `origem_card`.
- `DECISOES_ENRIQUECIMENTO.json`: decisão por obra (examinada, cards adicionados, rejeitados, justificativa).
- `METADADOS_ENRIQUECIDO_V1.json`: contagens e hashes das entradas.
- `MANIFEST.json`: SHA-256 de cada arquivo do pacote.

Reproduzir: `python 07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py <pasta>`; saída determinística (sem timestamps).
Política: `06_RELATORIOS/POLITICA_ENRIQUECIMENTO_EVIDENCE_CARDS_V1.md`. Relatório: `06_RELATORIOS/RELATORIO_ENRIQUECIMENTO_V1.md`.
