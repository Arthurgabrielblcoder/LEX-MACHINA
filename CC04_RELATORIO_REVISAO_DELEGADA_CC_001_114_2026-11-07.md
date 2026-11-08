# LEX MACHINA — CC-04 — revisão jurídica delegada

Data: 2026-11-07  
Branch: `cc04-revisao-delegada-cc-001-114`  
Baseline: `d1d4bc355488ea4b479b5aa23045ca3c3ef12666`  
Commit principal: `94c71921297060bb61caf75d8c298ff6277a9c76`

## Resultado

| Classificação | Quantidade |
|---|---:|
| A — revisão delegada satisfatória | 89 |
| B — satisfatória após correção | 19 |
| C — revisão pendente | 2 |
| D — bloqueado | 0 |
| Total revisado | 110 |

- Liberados editorialmente pela revisão delegada: 108.
- Pendentes: arts. 14 e 21.
- Excluídos e preservados: arts. 2, 4, 15, 20, 50 e 113.
- Aprovações humanas atribuídas pela CC-04: zero.
- Status formal dos 116 ativos: `PENDING_HUMAN_REVIEW`.

A indicação de liberação é uma classificação editorial produzida por revisão delegada de IA. Ela não equivale a aprovação humana pessoal e não altera o contrato formal de produção.

## Método e fontes

Três revisões independentes produziram evidência para 34, 39 e 37 registros. A consolidação verificou cobertura exata de 110 target IDs e foi reorganizada em cinco checkpoints reproduzíveis.

Fontes oficiais consultadas:

- Código Civil consolidado, Câmara dos Deputados: <https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html>
- STF, controle constitucional dos arts. 20 e 21: <https://portal.stf.jus.br/peticaoInicial/verPeticaoInicial.asp?base=ADI&numProcesso=4815>
- STJ, art. 111 e silêncio como anuência: <https://scon.stj.jus.br/SCON/GetInteiroTeorDoAcordao?dt_publicacao=21%2F09%2F2017&num_registro=201200335850>
- STJ, aplicação do art. 111 em relação de consumo: <https://processo.stj.jus.br/jurisprudencia/externo/informativo/?acao=pesquisar&aplicacao=informativo&livre=%40cnot%3D017132>
- STJ, enunciado científico relativo ao art. 13: <https://scon.stj.jus.br/SCON/ec/toc.jsp?b=TEMA&livre=%22276%22+INPATH%28NUM%29&operador=AND&tipo=EC&tp=T>

## Correções substantivas

Foram criadas novas versões editoriais para 19 artigos, preservando integralmente as versões anteriores:

| Artigo | Correção |
|---|---|
| 5 | Hipóteses de emancipação substituídas por categorias legais exatas. |
| 9 | Incluídos emancipação, interdição, ausência e morte presumida. |
| 11 | Removido o qualificador indevido “permanente” e delimitadas exceções legais. |
| 29 | Incluídos risco de extravio e destinos legais da conversão. |
| 30 | Identificados penhor, hipoteca, exclusão da posse e dispensas específicas. |
| 45 | Incluídos averbação e prazo decadencial de três anos. |
| 46 | Completados os elementos obrigatórios do registro. |
| 48 | Incluídos prazo e causas de anulação da deliberação. |
| 61 | Incluídos atualização das contribuições e destino subsidiário à Fazenda. |
| 64 | Corrigida a consequência obrigatória do mandado judicial. |
| 68 | Corrigido que o Ministério Público dá ciência à minoria vencida. |
| 69 | Incluídos legitimados e designação judicial da fundação destinatária. |
| 75 | Separados domicílio estatutário e agência brasileira ligada à obrigação. |
| 76 | Detalhados os cinco critérios e limitada a regra do preso ao cumprimento da sentença. |
| 83 | Incluídas as ações correspondentes aos direitos móveis. |
| 96 | Substituído “luxo” pelos critérios legais das três benfeitorias. |
| 103 | Exemplo trocado por pedágio em rodovia de uso comum. |
| 105 | Explicitado o efeito da indivisibilidade para cointeressados capazes. |
| 110 | Exemplo passou a distinguir reserva mental de intenção de inadimplemento. |

O arquivo `CC04_CORRECTIONS.json` contém texto anterior, texto revisado, explicação IDs, evidência e fundamento de cada mudança.

## Pendências

- Art. 14: participação familiar varia conforme modalidade e legislação sanitária; a explicação não deve universalizar requisito sem fonte específica.
- Art. 21: alcance das providências de privacidade exige consolidação explícita da ponderação constitucional relacionada à liberdade de expressão.

## Segunda verificação dos 23 prioritários

- 5 dos prioritários foram excluídos por aprovação humana externa ainda não incorporada: 2, 4, 15, 20 e 50. O art. 113 também foi excluído do lote, mas não integrava esta matriz prioritária da CC-03.
- 4 satisfatórios após correção: 11, 76, 105 e 110.
- 12 satisfatórios sem nova correção: 12, 13, 43, 44, 49-A, 52, 57, 59, 104, 111, 112 e 114.
- 2 pendentes: 14 e 21.

O detalhamento individual está em `CC04_PRIORITY_SECOND_REVIEW.json`.

## Qualidade e testes

- Matriz individual: 110/110, com evidência, fundamento, risco e hash do snapshot legal.
- Checkpoints: cinco, totalizando 110 registros.
- Corpus: 269 versões, sendo 116 ativas e 153 históricas.
- Frases genéricas: zero.
- Alertas editoriais: zero.
- Firmware, microSD, ESP32 e índices de produção: nenhuma alteração. A compatibilidade do índice candidato foi verificada apenas em diretório temporário, sem persistência ou promoção.
- Build e matrizes: reproduzíveis.
- Suíte aplicável CC-02 a CC-04: 18/18 testes aprovados, além dos quatro checks determinísticos das missões CC-02, CC-03, CC-03B e CC-04.

## Hashes

| Artefato | SHA-256 |
|---|---|
| Baseline CC-03B | `be75e9bdb93e9c28f76dd0577957d128471f159e8fe931e72276d7456dbbc1d2` |
| Corpus CC-04 | `1311c107504697a13a9a4b99d13af5b8c47d9e210edc2b446f761c1407b73bcf` |
| Matriz de 110 | `a6a9f8293803970f4d8943890adf28943eb26b73072a030cfd3d292d60f3493f` |
| Correções | `026cbc99da5bc6b73455c3997ebc83b6d87141cb97bccbfc75180d35c1fd6660` |
| Prioritários | `e4844ff0e4ff45618d82eb8168fe3a1205bf3c8822afe902780890d182560aef` |
| Manifesto de liberação | `f98229edbd304412b4e0d99e5f0a69f35e91fe25e6e87a65df316ab02dd8194a` |
| Lookup candidato | `c04c77c03348fb4450fe7383e4bcb85aa055b634b272dc27d43115246d741d79` |
| Payload candidato | `ef1a1dcd9d4b88ff4d53eec7f979e89008f2ab7fdb358e8799f9f5ca09a5dc52` |
| Manifesto do build | `05c8cd2f2890ebcc61ddcbb682fabf5d2a4e9f53d32e05fb66f674e8672e9d9a` |

## Recomendação

Manter os arts. 14 e 21 pendentes. Incorporar em missão separada os textos finais dos seis artigos aprovados externamente, com prova da redação humana efetivamente escolhida. Não promover automaticamente o corpus, não fazer merge e não iniciar deploy.
