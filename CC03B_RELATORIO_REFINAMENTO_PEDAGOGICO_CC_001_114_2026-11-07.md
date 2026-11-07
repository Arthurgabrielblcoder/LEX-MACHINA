# LEX MACHINA — CC-03B — refinamento pedagógico do ENTENDA

Data: 2026-11-07  
Branch: `cc03b-refinamento-pedagogico-cc-001-114`  
Baseline preservada: `c616d4a3969948a3d6336ffc2fbeeef2e9b020a5`  
Commit principal do refinamento: `85cf8b5e67addfe2765551e27c294ae2cb169a0b`

## 1. Resultado

| Item | Quantidade |
|---|---:|
| Registros ativos refinados | 116 |
| Preservados sem mudança | 0 |
| Artigos complexos reconferidos | 15 |
| Novas correções de precisão substancial | 5 |
| Registros promovidos juridicamente | 0 |

Todos os registros ativos continuam `PENDING_HUMAN_REVIEW`. As versões da CC-02 e CC-03 foram preservadas; os novos registros receberam a versão editorial seguinte, sem reutilização de identificador.

## 2. Causa e solução estrutural

O limite global mínimo de 120 palavras incentivava preenchimento padronizado até em artigos simples. A CC-03B passou a permitir, somente para CC2002, visões gerais de 45 a 360 palavras. O contrato ENTENDA, os cinco campos, os target IDs e o limite de payload foram preservados.

As seis fórmulas repetitivas identificadas foram removidas. A remoção não foi mecânica isolada: cada núcleo específico de regra, efeito, exemplo, ressalva e glossário foi reconferido, e os artigos complexos foram comparados integralmente com caput e subdivisões vigentes.

Fonte oficial confrontada em 2026-11-07: <https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html>.

## 3. Métricas antes e depois

| Métrica | CC-03 antes | CC-03B depois | Variação |
|---|---:|---:|---:|
| Palavras totais | 18.402 | 8.514 | -9.888 |
| Média por registro | 158,64 | 73,40 | -85,24 |
| Menor registro | 138 | 51 | -87 |
| Maior registro | 188 | 118 | -70 |
| Ocorrências de preenchimento | 696 | 0 | -696 |
| Repetições exatas excedentes | 575 | 0 | -575 |
| Frequência máxima da mesma frase | 116 | 1 | -115 |
| Razão de frases únicas | 0,5494 | 1,0000 | +0,4506 |
| Similaridade média com vizinho mais próximo | 0,5083 | 0,1071 | -0,4012 |
| Payload candidato | 153.664 bytes | 88.086 bytes | -65.578 bytes |

O payload caiu 42,68%, sem perda de campo obrigatório. A média textual caiu 53,73%, concentrando o espaço em conteúdo próprio de cada artigo.

## 4. Principais melhorias

- `O QUE DIZ` passou a traduzir diretamente a regra, sem descrição do próprio processo editorial.
- `O QUE SIGNIFICA` deixou de repetir advertências gerais e passou a explicar efeitos e requisitos específicos.
- Exemplos genéricos e ressalvas universais foram removidos.
- Glossários foram mantidos apenas com termos usados e necessários no corpo.
- Artigos simples ficaram entre aproximadamente 50 e 80 palavras; os complexos cresceram somente quando a estrutura jurídica exigiu.
- Arts. 4, 20, 44 e 50 receberam cobertura explícita de incisos, parágrafos, exceções e consequências.
- Art. 1 passou a distinguir capacidade de direito de capacidade de exercício.

## 5. Correções de precisão encontradas na revisão pedagógica

| Artigo | Problema anterior | Correção CC-03B |
|---|---|---|
| 1 | “Desde que nasce” criava ambiguidade e o exemplo se aproximava do tema do art. 2. | Regra reformulada como aptidão geral e distinção expressa entre titularidade e exercício. |
| 4 | Categorias de incapacidade relativa estavam resumidas como limitações de discernimento ou administração. | Todas as hipóteses foram enumeradas, com regra indígena e cautela sobre diagnóstico e curatela. |
| 20 | Faltavam exceções legais, legitimidade de familiares e tensão constitucional. | Requisitos, justiça, ordem pública, proteção pós-morte e liberdade de expressão foram qualificados. |
| 44 | Subdivisões recentes estavam excessivamente comprimidas. | Incluídos liberdade religiosa, lei partidária e alcance subsidiário da alteração de 2024. |
| 50 | Conceitos e limites da desconsideração estavam genéricos. | Explicados desvio, confusão, beneficiários, via inversa e fatores que não bastam isoladamente. |

Não foi identificado novo erro jurídico demonstrável remanescente. Essa conclusão significa ausência de erro detectado nesta auditoria automatizada, não aprovação jurídica.

## 6. Artigos complexos e pendências

Foram reconferidos os arts. 2, 4, 7, 15, 20, 25, 35, 44, 50, 62, 66, 99, 108, 113 e 114.

Permanecem prioritárias as questões registradas na CC-03: nascituro; incapacidade e curatela; autonomia médica; direitos da personalidade e liberdade de expressão; responsabilidade estatal; economia solidária; desconsideração; direitos da personalidade de pessoas jurídicas; devido processo associativo; domicílio necessário; validade e interpretação dos negócios; reserva mental; silêncio e renúncia.

## 7. Matriz de revisão humana — 15 casos

| Artigo | Foco da comparação CC-02 → CC-03 → CC-03B | Risco remanescente |
|---|---|---|
| 1 | Capacidade de direito e exercício | Fronteira conceitual com personalidade do art. 2 |
| 2 | Nascimento com vida e nascituro | Controvérsia sobre alcance dos direitos pré-natais |
| 4 | Quatro categorias e regra indígena | Curatela e Lei Brasileira de Inclusão |
| 7 | Duas hipóteses de morte presumida | Prova, buscas e fixação da data |
| 15 | Recusa de tratamento com risco | Emergência, incapacidade e consentimento |
| 20 | Imagem, palavra e escritos | Liberdade de expressão e controle constitucional |
| 25 | Ordem dos curadores do ausente | Separação de fato e impedimentos |
| 35 | Data real da morte | Reconstituição dos herdeiros daquela data |
| 44 | Tipos de pessoa jurídica privada | Alteração de 2024 e leis especiais |
| 50 | Desconsideração | Prova do abuso, benefício e nexo |
| 62 | Nove finalidades fundacionais | Inciso vetado e finalidade estatutária |
| 66 | Velamento das fundações | Competência territorial do Ministério Público |
| 99 | Classes de bens públicos | Afetação e regra do parágrafo único |
| 113 | Critérios interpretativos | Negociação razoável e regras pactuadas |
| 114 | Interpretação estrita | Compatibilidade com boa-fé e contexto |

O arquivo `CC03B_HUMAN_REVIEW_SAMPLE_15.json` contém, para cada caso, texto legal, ENTENDA da CC-02, ENTENDA da CC-03, ENTENDA da CC-03B, justificativa e risco remanescente.

## 8. Testes

```text
python -X utf8 ENTENDA_ENGINE\build_entenda_cc02.py --check
python -X utf8 ENTENDA_ENGINE\cc03_audit.py --check
python -X utf8 ENTENDA_ENGINE\cc03b_refinement.py --check
python -m unittest ENTENDA_ENGINE.tests.test_entenda_engine ENTENDA_ENGINE.tests.test_entenda_cc02 ENTENDA_ENGINE.tests.test_entenda_cc03 ENTENDA_ENGINE.tests.test_entenda_cc03b
```

- 32/32 testes aprovados.
- Build, auditoria CC-03 e artefatos CC-03B reproduzíveis.
- 116 chaves ativas, sem duplicidade.
- 250 registros totais: 116 ativos e 134 versões anteriores preservadas.
- Zero frases de preenchimento e zero alertas editoriais.
- UTF-8, schema, cobertura e compatibilidade do motor aprovados.
- Firmware, microSD, ESP32 e índices de produção não alterados.

## 9. Hashes

| Artefato | SHA-256 |
|---|---|
| Corpus baseline CC-03 | `f4f44ab5334f9adc5aa7c88015762028b2a5d1381b2cfd0e0d9959799191407e` |
| Corpus refinado CC-03B | `be75e9bdb93e9c28f76dd0577957d128471f159e8fe931e72276d7456dbbc1d2` |
| Métricas | `7784cce68f348b6f507639a32aba50e3b735a3d639a4025226cb570e911ff782` |
| Matriz de mudanças | `67040037ba5b1d8bf74d6ea96d681a29175253c23998973ca280dddbb7b0c301` |
| Amostra de 15 casos | `325a222bfd4af361f535aa4b017b7f32fb305417219375e53eadb07322c9b64e` |
| Auditoria de qualidade | `0def00df24b04aca1867fae8983da1e6e8bd2798be8a49103c896c0abc661722` |
| Lookup candidato | `38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82` |
| Payload candidato | `6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638` |
| Manifesto de build | `213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760` |

## 10. Git e recomendação

- Branch candidata: `cc03b-refinamento-pedagogico-cc-001-114`.
- Commit do refinamento: `85cf8b5e67addfe2765551e27c294ae2cb169a0b`.
- A branch remota homônima não existia na verificação anterior à publicação.
- Push deve ser normal, sem force; merge, tag, deploy e promoção continuam proibidos.

Recomendação: submeter a matriz de 15 casos à revisão humana e manter os 116 registros como candidatos. Não iniciar outro lote automaticamente.
