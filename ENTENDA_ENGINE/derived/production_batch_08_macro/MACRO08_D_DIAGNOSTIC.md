# MACRO08 — diagnóstico da fila D

Documento consolidado escrito pelo drafter (fora da comparação de determinismo). Data de referência: 2026-10-05.

## Números

- Lote: 22 D em 179 novas = 12.3% (abaixo de 20%).
- CORPO: 4 D em 113 = 3.5%.
- ADCT: 18 D em 66 = 27.3% (**acima de 20% no segmento ADCT**; por isso este diagnóstico).

## Causa dominante

No ADCT, 16 dos 18 D vêm só de `TEMPORAL_STATUS_UNRESOLVED`: o artigo tem utilidade atual, mas sua situação em 05/10/2026 depende de dado que não está em fonte versionada (lei complementar ainda não ingerida, emenda não versionada, fato administrativo). A regra do Macro08 é conservadora: sem evidência versionada, a classe fica `EXTERNAL_STATUS_REQUIRED`/`PARTIALLY_OPERATIVE`/`FUTURE_TRIGGER` (sem data) e o item vai para D, em vez de afirmar a situação de memória.

Não é falha de redação: os textos desses itens passaram pelo contrato do motor, pelo validador v3 e pelo critic; o que falta é a camada externa (PENDING_EXTERNAL_INGESTION). Os 2 D restantes do ADCT são de controle de constitucionalidade anotado (`JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS`: ADCT 27 e 107-A).

Medidas já tomadas para não inflar a fila D:

- ADCT esgotado não foi escrito como vigente: 73 artigos inteiros foram SKIP com motivo (SKIP_REGISTER), e artigos revogados ou históricos foram excluídos.
- `TRANSITION_OR_TEMPORAL` isolado não gera HIGH quando a classe temporal está resolvida por evidência versionada (OPERATIVE_CURRENT, OPERATIVE_TRANSITION, EFFECT_EXHAUSTED, HISTORICAL_ONLY).
- Gatilho futuro com data fixada pelo próprio texto (ex.: "Em 2027 e 2028", "a partir de 2033") é `DATED_FUTURE_TRIGGER`, resolvido (por isso ADCT 127, 128, 129, 131, 132 e 134 não foram para D).
- `JUDICIAL_REVIEW_CONTEXT_ONLY` com motivo (ADCT 101, CF 198 etc.) fica MEDIUM.

## Itens D e o que os resolveria

| # | Target | Regras | Classe temporal | O que resolveria |
|---|---|---|---|---|
| 1 | `CF88:ART.195:PAR.15` | TEMPORAL_STATUS_UNRESOLVED | — | Ingerir a lei instituidora da CBS (estado do § 15/§ 18) e classificar o gatilho; se datado pelo texto, vira DATED_FUTURE_TRIGGER. |
| 2 | `CF88:ART.226:PAR.3` | JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS | — | Ingerir a jurisprudencia sobre uniao estavel (camada JURISPRUDENCIA) e decidir CONTEXT_ONLY x REQUIRED. |
| 3 | `CF88:ART.228` | SANCTION_WITH_INTERPRETATION | — | Revisao juridica humana da relacao com a legislacao especial (sancao + interpretacao). |
| 4 | `CF88:ART.231:PAR.1` | INTERPRETIVE_CONTROVERSY | — | Revisao juridica humana (controversia interpretativa registrada pelo proprio draft). |
| 5 | `ADCT:ART.8` | TEMPORAL_STATUS_UNRESOLVED | PARTIALLY_OPERATIVE | Estado das leis e dos atos de anistia (externo). |
| 6 | `ADCT:ART.12` | TEMPORAL_STATUS_UNRESOLVED | PARTIALLY_OPERATIVE | Conclusao dos trabalhos da comissao e das leis de limites (externo). |
| 7 | `ADCT:ART.17` | TEMPORAL_STATUS_UNRESOLVED | PARTIALLY_OPERATIVE | Alcance residual atual (fatos individuais nao versionados). |
| 8 | `ADCT:ART.25` | TEMPORAL_STATUS_UNRESOLVED | EXTERNAL_STATUS_REQUIRED | Estado da legislacao que substituiu delegacoes e decretos-leis (externo). |
| 9 | `ADCT:ART.27` | JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS, CONSTITUTIONAL_AMBIGUITY, JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS, TEMPORAL_STATUS_UNRESOLVED | PARTIALLY_OPERATIVE | Resultado da acao anotada no § 11 (JUDICIAL_REVIEW_REQUIRED) + estado de implantacao dos tribunais. |
| 10 | `ADCT:ART.34` | TEMPORAL_STATUS_UNRESOLVED | PARTIALLY_OPERATIVE | Estado das leis complementares dos §§ 9º e 11 (externo). |
| 11 | `ADCT:ART.35` | TEMPORAL_STATUS_UNRESOLVED | EXTERNAL_STATUS_REQUIRED | Estado da lei complementar do art. 165, § 9º (externo). |
| 12 | `ADCT:ART.35:PAR.2` | TEMPORAL_STATUS_UNRESOLVED | EXTERNAL_STATUS_REQUIRED | Idem art. 35. |
| 13 | `ADCT:ART.38` | TEMPORAL_STATUS_UNRESOLVED | EXTERNAL_STATUS_REQUIRED | Estado da lei complementar do art. 169 e data de publicacao do § 2º (externo). |
| 14 | `ADCT:ART.52` | TEMPORAL_STATUS_UNRESOLVED | EXTERNAL_STATUS_REQUIRED | Estado das leis complementares do art. 192 (externo). |
| 15 | `ADCT:ART.54-A` | TEMPORAL_STATUS_UNRESOLVED | EXTERNAL_STATUS_REQUIRED | Situacao dos pagamentos da indenizacao (externo). |
| 16 | `ADCT:ART.60-A` | TEMPORAL_STATUS_UNRESOLVED | EXTERNAL_STATUS_REQUIRED | Termo inicial da vigencia dos fundos (externo ao artigo). |
| 17 | `ADCT:ART.79` | TEMPORAL_STATUS_UNRESOLVED | EXTERNAL_STATUS_REQUIRED | Conteudo da EC 67/2010 anotada no texto (emenda nao versionada). |
| 18 | `ADCT:ART.88` | TEMPORAL_STATUS_UNRESOLVED | EXTERNAL_STATUS_REQUIRED | Estado da lei complementar do art. 156, § 3º (externo). |
| 19 | `ADCT:ART.97` | TEMPORAL_STATUS_UNRESOLVED | PARTIALLY_OPERATIVE | Estado da lei complementar do art. 100, § 15, e relacao com o regime do art. 101 (externo). |
| 20 | `ADCT:ART.107-A` | JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS | OPERATIVE_TRANSITION | Resultado da ADI 7064 / MI 7300 anotados (JUDICIAL_REVIEW_REQUIRED). |
| 21 | `ADCT:ART.126` | TEMPORAL_STATUS_UNRESOLVED | FUTURE_TRIGGER | Instituicao da CBS (condicao do inciso II) (externo). |
| 22 | `ADCT:ART.135` | TEMPORAL_STATUS_UNRESOLVED | FUTURE_TRIGGER | Extincao dos tributos (art. 126, II) e lei complementar (externo). |

## Recomendação

1. Ingerir a legislação correlata citada (leis complementares dos arts. 100 § 15, 156 § 3º, 165 § 9º, 169, 192; lei instituidora da CBS) e a EC 67/2010; reavaliar os D temporais com `trigger_date`/classe resolvida quando houver evidência versionada.
2. Ingerir a camada JURISPRUDÊNCIA para as ações anotadas (ADI 7064, MI 7300, ação do ADCT 27) e reclassificar CONTEXT_ONLY x REQUIRED.
3. Até lá, os 22 D seguem para revisão humana completa (MACRO08_FULL_D_REVIEW.md). Nenhum item foi aprovado.
