# Súmulas Vinculantes do STF

O importador `importar_stf_sumulas_vinculantes.py` mantém a camada
`sumula_vinculante` separada das súmulas comuns e das demais categorias
jurisprudenciais.

## Fonte oficial

- Lista: `https://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp?base=26`
- Detalhes: a página individual indicada pela própria lista oficial.

Foi pesquisada primeiro a existência de JSON, API, exportação ou dataset
oficial. A página não carrega a coleção por uma chamada estruturada: a lista e
os detalhes são entregues diretamente pelo servidor em HTML. Por isso, o
importador valida estritamente a estrutura oficial, a sequência completa, a
identidade de cada enunciado, a situação, a data quando disponível e a URL.

As consultas usam a sessão TLS com o truststore do sistema e bloqueiam
redirecionamentos. Resposta vazia, falso HTTP 200, fonte externa, sequência
incompleta ou estrutura inesperada abortam a atualização antes da troca
atômica do catálogo.

## Critérios

A triagem consumerista é textual. Somente os candidatos são integrados ao
catálogo. Relações `CDC art. X` exigem menção explícita e inequívoca ao CDC,
ao Código de Defesa do Consumidor ou à Lei 8.078/1990 junto ao artigo; nenhuma
relação é criada por proximidade temática.

O índice gerado em
`saida/99_RELATIONS_V1/02_SUMULAS_VINCULANTES/INDICE_SUMULAS_VINCULANTES.txt`
começa com `SÚMULAS VINCULANTES (quantidade)`. A pasta `saida/` é temporária e
permanece ignorada pelo Git.
