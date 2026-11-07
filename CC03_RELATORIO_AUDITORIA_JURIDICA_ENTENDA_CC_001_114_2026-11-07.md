# LEX MACHINA — CC-03 — auditoria jurídica independente do ENTENDA

Data: 2026-11-07  
Branch: `cc03-auditoria-juridica-cc-001-114`  
Baseline preservada: `f7d94676ff5c937e0f537e29af20e7438fc604ec`  
Commit principal da auditoria: `5bd86b6f276674afc58fde80dc9e1b8cf95e3971`

## 1. Resultado consolidado

Foram auditadas individualmente as 116 explicações ativas da CC-02 contra o texto consolidado do Código Civil.

| Categoria de auditoria | Quantidade |
|---|---:|
| `SEM_PROBLEMA_IDENTIFICADO` | 75 |
| `CORRIGIDO_COM_EVIDENCIA` | 18 |
| `REVISAO_HUMANA_PRIORITARIA` | 23 |
| `BLOQUEADO_POR_INCONSISTENCIA` | 0 |
| Total | 116 |

O art. 69-A permanece como alvo estrutural bloqueado, pois foi vetado e não possui explicação ativa. Todos os 116 registros ativos continuam com `PENDING_HUMAN_REVIEW`. Nenhum registro recebeu `HUMAN_APPROVED_T1` ou `APPROVED`.

Esta auditoria automatizada não equivale à aprovação jurídica humana.

## 2. Fontes e método

Fonte oficial principal, acessada em 2026-11-07:

- Câmara dos Deputados, redação consolidada da Lei nº 10.406/2002: <https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html>
- Página da norma e alterações: <https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-norma-pl.html>
- Planalto: tentativa em 2026-11-07, bloqueada pelo controle de acesso do portal; não foi usado como evidência material.

Cada registro recebeu confronto de significado, requisitos, exceções, consequências, terminologia, exemplo, vigência, subdivisões e legibilidade. A evidência integral por artigo, incluindo snapshot e hash, está em `CC03_AUDIT_MATRIX.json`.

## 3. Preservação da CC-02

- Os três commits originais da CC-02 permanecem ancestrais e inalterados.
- O corpus original foi fixado em `CC2002_CC02_BASELINE.entenda.jsonl`.
- SHA-256 do corpus original: `86ef8d8f1843650e927b2fd2fd620dd92a7fe9508dac8934efbaae238beecd4d`.
- Os 18 registros corrigidos receberam `editorial_version: 2`.
- As 18 versões 1 correspondentes permanecem no corpus como `RETIRED` e `CHANGES_REQUESTED`, com conteúdo e proveniência originais.
- Os outros 98 registros ativos permanecem na versão editorial 1.

## 4. Correções substantivas

| Artigo | Correção fundamentada |
|---|---|
| 7 | Acrescentados o prazo de dois anos após o fim da guerra, o esgotamento das buscas e a fixação judicial da data provável. |
| 10 | Removida adoção da enumeração vigente; o antigo inciso III está revogado. |
| 22 | Incluída legitimidade de interessado ou Ministério Público para requerer ausência e curadoria. |
| 24 | Retirada ordem de preferência indevidamente deslocada do art. 25; mantidos poderes e deveres definidos pelo juiz. |
| 25 | Restaurada ordem completa: cônjuge qualificado, pais, descendentes e escolha judicial subsidiária. |
| 26 | Explicitados um ano após arrecadação e três anos quando havia representante ou procurador. |
| 28 | Explicitados 180 dias da publicação e distinguidos publicação, trânsito, inventário e comparecimento. |
| 35 | Corrigida inversão: o dispositivo trata da prova da data exata da morte. |
| 36 | Corrigida inversão: o dispositivo trata do retorno ou da prova de vida. |
| 39 | Substituído “herdeiro necessário” pelos sujeitos expressos: ausente, descendentes e ascendentes. |
| 62 | Enumeradas as nove finalidades fundacionais vigentes e identificado o inciso X vetado. |
| 65 | Incluídos submissão à autoridade, recurso ao juiz e prazo subsidiário de 180 dias. |
| 66 | Eliminada referência inexistente a fundações federais; restaurada a distribuição territorial do velamento. |
| 67 | Incluídos quórum de dois terços e prazo de 45 dias do Ministério Público. |
| 77 | Incluída citação no estrangeiro e os dois locais previstos para demanda. |
| 99 | Incluída regra do parágrafo único sobre pessoas públicas com estrutura privada. |
| 108 | Incluídos patamar superior a trinta salários mínimos e operações abrangidas. |
| 113 | Removida alocação de riscos, ausente do artigo, e restaurados os critérios interpretativos enumerados. |

O texto original, o texto revisado, o motivo, a fonte, a confiança e os testes de cada alteração constam de `CC03_SUBSTANTIVE_CORRECTIONS.json`.

## 5. Matriz estratégica de 15 casos

| Artigo | Categoria | Motivo da seleção | Decisão humana requerida |
|---|---|---|---|
| 1 | Sem problema identificado | Controle simples | Confirmar clareza da distinção entre personalidade e exercício. |
| 2 | Revisão prioritária | Nascituro e início da personalidade | Delimitar até onde o resumo pode tratar os direitos do nascituro sem adotar tese controvertida. |
| 4 | Revisão prioritária | Incapacidade relativa e várias subdivisões | Confirmar linguagem sobre assistência, curatela e impossibilidade de expressão da vontade. |
| 7 | Corrigido | Morte presumida, exceções e prazo | Confirmar suficiência do prazo de guerra e das buscas. |
| 15 | Revisão prioritária | Autonomia médica e risco de vida | Avaliar emergência, incapacidade e consentimento informado. |
| 20 | Revisão prioritária | Imagem, honra e controle constitucional | Definir quanto do contexto constitucional deve aparecer sem invadir jurisprudência. |
| 25 | Corrigido | Ordem legal de curadores | Confirmar separação correta entre arts. 24 e 25. |
| 35 | Corrigido | Erro anterior por inversão | Confirmar data real da morte e herdeiros daquele momento. |
| 44 | Revisão prioritária | Alteração legislativa de 2024 | Confirmar tratamento de economia solidária e aplicação subsidiária. |
| 50 | Revisão prioritária | Desconsideração e seis subdivisões | Confirmar beneficiários, abuso, confusão patrimonial e limites do grupo econômico. |
| 62 | Corrigido | Muitas subdivisões e inciso vetado | Confirmar enumeração das nove finalidades vigentes. |
| 66 | Corrigido | Competência institucional | Confirmar distribuição territorial do velamento. |
| 99 | Corrigido | Três classes e parágrafo único | Confirmar explicação de dominicais e pessoas públicas estruturadas sob direito privado. |
| 113 | Corrigido | Critérios interpretativos alterados em 2019 | Confirmar retirada de alocação de riscos e síntese dos critérios vigentes. |
| 114 | Revisão prioritária | Controle simples com risco conceitual | Confirmar que interpretação estrita não elimina boa-fé, contexto e validade. |

O texto legal correspondente, o ENTENDA integral, a avaliação, a evidência e os pontos de decisão estão em `CC03_HUMAN_REVIEW_SAMPLE_15.json`. A amostra não é prova de correção das 116 explicações.

## 6. Testes e limitações

Executados:

```text
python -X utf8 ENTENDA_ENGINE\build_entenda_cc02.py
python -X utf8 ENTENDA_ENGINE\cc03_audit.py
python -X utf8 ENTENDA_ENGINE\build_entenda_cc02.py --check
python -X utf8 ENTENDA_ENGINE\cc03_audit.py --check
python -m unittest ENTENDA_ENGINE.tests.test_entenda_engine ENTENDA_ENGINE.tests.test_entenda_cc02 ENTENDA_ENGINE.tests.test_entenda_cc03
```

Resultados:

- 27/27 testes aprovados.
- 116 registros ativos válidos e únicos.
- 18 versões 2 ativas e 18 versões 1 aposentadas e preservadas.
- 116/116 com `PENDING_HUMAN_REVIEW`.
- Cobertura e chaves: aprovadas.
- Schema JSON e UTF-8: aprovados, sem caractere de substituição.
- Referência interna expressa ao art. 81, no art. 84: conferida e pertinente.
- Motor ENTENDA: compatível.
- Build e matriz de auditoria: reproduzíveis.
- Alertas editoriais: zero.
- Firmware, microSD, ESP32 e índices de produção: não alterados.

Limitações: a auditoria não substitui parecer jurídico; não resolve controvérsias doutrinárias ou jurisprudenciais; o Planalto não estava acessível; e a classificação “sem problema identificado” significa ausência de erro demonstrável nesta revisão, não certificação absoluta.

## 7. Hashes do pacote auditado

| Artefato | SHA-256 |
|---|---|
| Corpus baseline CC-02 | `86ef8d8f1843650e927b2fd2fd620dd92a7fe9508dac8934efbaae238beecd4d` |
| Corpus auditado CC-03 | `f4f44ab5334f9adc5aa7c88015762028b2a5d1381b2cfd0e0d9959799191407e` |
| Matriz completa | `971ae38752fa20a5411625a553cc35a56dcf77083b9815bdc6529dce58f86921` |
| Correções substantivas | `311bacb6fc66a094cbdbe39d621ad104fdf5d172193fd25c4d9130ba0c189606` |
| Amostra de 15 casos | `2052d0ed96e5885f58d1ed629c7682d5f12a3cddf201eefb0bf735b89a60fdbc` |
| Lookup candidato | `edeadbcfc7ea1130d27d104d568c2c871dec093c36477250a443617626ad741a` |
| Payload candidato | `461f050efa988fdcacf043ebcc0c3a60515b76603e004376918ced4184439ef0` |
| Manifesto do build | `9f76d2363bbdcaaa9c67428812d4b1d8bd458066b9535439481222bce01124b7` |

## 8. GitHub e segurança

- Remoto: `https://github.com/Arthurgabrielblcoder/LEX-MACHINA.git`
- A branch CC-03 não existia remotamente antes da publicação.
- Branch candidata publicada por push normal: `cc03-auditoria-juridica-cc-001-114`.
- Commit do pacote auditado publicado: `5bd86b6f276674afc58fde80dc9e1b8cf95e3971`.
- Merge, force push, tag e promoção: não realizados.
- Arquivos ignorados, temporários, backups locais e segredos: não publicados.

## 9. Pendências e recomendação

Os 23 registros prioritários devem passar por revisão humana, começando pela amostra de 15 casos. Os 18 corrigidos devem receber conferência humana específica das mudanças antes de qualquer promoção.

Recomendação: não promover o lote neste momento. Manter todo o pacote como candidato, revisar os 15 casos estratégicos e depois decidir se os demais prioritários exigem nova versão editorial. Não iniciar CC-04 automaticamente.
