# Súmulas comuns — STF e STJ

O módulo `importar_sumulas_comuns.py` mantém exclusivamente registros do tipo
`sumula`. Súmulas Vinculantes continuam no tipo `sumula_vinculante`.

## Fontes oficiais

- STF: lista `sumariosumulas.asp?base=30` e JSON de
  `aplicacaosumulapesquisa.asp`, endpoint utilizado pelo JavaScript oficial
  `aplicacaosumula.js`. A página individual confirma texto e data das
  candidatas consumeristas.
- STJ: coleção paginada SCON (`pesquisar.jsp?b=SUMU&tipo=sumula`) e pesquisa
  oficial específica de súmulas canceladas. O SCON informa texto, julgamento,
  publicação e contagem total.

As consultas usam TLS com o truststore do sistema, recusam redirecionamentos e
validam contagens, identidades, duplicatas, respostas vazias e páginas de erro
com HTTP 200. Qualquer falha impede a substituição atômica do catálogo.

## Preservação e relações

Os oito registros STJ existentes são preservados com os mesmos identificadores,
textos e relações. Metadados oficiais ausentes são acrescentados. O campo
`relacoes_automaticas_cdc` distingue vínculos extraídos nesta atualização das
relações históricas preservadas.

Novos vínculos `CDC art. X` exigem citação conjunta e inequívoca ao CDC, Código
de Defesa do Consumidor ou Lei 8.078/1990 e ao artigo. Súmulas canceladas não
entram no índice vigente `SÚMULAS (quantidade)`.
