# Recursos Repetitivos do STJ

O atualizador usa exclusivamente os dois CSVs oficiais do conjunto **Precedentes
Qualificados**, publicado no portal de Dados Abertos do Superior Tribunal de
Justiça:

- `temas.csv`: situação, questão submetida, tese, órgão julgador, datas,
  referências legislativas e assuntos;
- `processos.csv`: processos representativos, relator, datas e eventual
  desafetação.

As transferências usam HTTPS com a sessão TLS e o *truststore* do projeto. O
importador não segue redirecionamentos, rejeita respostas vazias, HTML servido
como falso HTTP 200, colunas ausentes, situações desconhecidas e coleções
truncadas.

## Situação e índice vigente

`situacao_oficial_stj` guarda literalmente a terminologia do STJ. Os campos
`tema_cancelado`, `tema_desafetado`, `sem_tese_aplicavel` e
`vigente_aplicavel` permitem ao índice excluir temas que não devem ser exibidos
como precedentes atuais. Uma desafetação isolada de processo representativo não
é tratada como cancelamento do tema; `tema_desafetado` só é verdadeiro quando
todos os processos vinculados trazem desafetação explícita no CSV oficial.

O arquivo gerado
`saida/99_RELATIONS_V1/05_RECURSOS_REPETITIVOS/INDICE_RECURSOS_REPETITIVOS.txt`
começa com `RECURSOS REPETITIVOS (quantidade)` e contém somente registros
vigentes/aplicáveis.

## Preservação e relações normativas

Registros históricos mantêm seus IDs, nomes de arquivo, campos editoriais e
`relacionado_a`. O campo `relacoes_automaticas_cdc` é independente e só recebe
uma relação quando o texto oficial menciona de forma explícita o CDC ou a Lei
8.078/1990 junto do artigo correspondente.

A escrita do catálogo é transacional: os dois conjuntos oficiais são baixados,
validados e cruzados antes da substituição atômica do JSON. Qualquer falha
preserva os bytes do catálogo anterior.
