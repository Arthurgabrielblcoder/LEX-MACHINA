# Acórdãos consumeristas

Esta camada usa somente os **Espelhos de Acórdãos** publicados em JSON no
portal oficial de Dados Abertos do STJ. A primeira amostra é fixa e auditável:
`20260831.json`, nos conjuntos da **Segunda Seção**, **Terceira Turma** e
**Quarta Turma**.
Esses órgãos concentram matéria de direito privado, mas a amostra não pretende
representar toda a jurisprudência do STJ.

## Critérios de importação

Um registro precisa ser acórdão colegiado, ter ementa substancial, mencionar
expressamente o CDC ou a Lei 8.078/1990 e trazer ao menos um artigo do CDC de
forma inequívoca. A relação `CDC art. X` só é criada quando o artigo aparece no
mesmo bloco de referência legislativa da Lei 8.078/1990 ou em construção direta
como `art. X do CDC`.

Processos identificados nos catálogos de Repercussão Geral, Recursos
Repetitivos, IAC, SIRDR, ADI, ADC, ADPF ou ADO são excluídos. Classes
qualificadas e julgados identificados como Tema Repetitivo também são excluídos.
Após deduplicação por tribunal, processo, data e identificador da decisão, são
mantidos no máximo 20 acórdãos. A seleção prioriza espelhos com tese jurídica ou
informações complementares elaboradas pela Secretaria de Jurisprudência.

Entre os registros elegíveis, um algoritmo guloso e determinístico escolhe cada
posição usando, nesta ordem: (1) quantidade de campos documentais oficiais
preenchidos e faixas de extensão desses campos; (2) presença de tese jurídica,
informações complementares e quantidade de referências legislativas
estruturadas; (3) quantidade de artigos do CDC ainda ausentes da seleção e menor
concentração nos artigos já escolhidos; (4) data de julgamento mais recente; e
(5) maior identificador oficial do Espelho como último desempate. A entrada é
deduplicada antes dessa etapa, portanto a ordem dos arquivos e respostas não
altera o resultado.

O máximo de 20 registros é um **limite editorial desta primeira versão**, não
uma limitação da fonte oficial. Os demais elegíveis continuam contabilizados no
relatório e podem integrar uma expansão editorial futura.

## Cobertura

O STF foi pesquisado, mas não foi incluído nesta primeira amostra porque não foi
localizada exportação oficial estruturada equivalente aos Espelhos do STJ que
permitisse coleta pequena, reproduzível e auditável sem scraping de resultados.
Uma expansão futura pode acrescentar o STF quando houver fonte estruturada
estável ou uma lista curada de processos com validação oficial individual.

Qualquer resposta vazia, falso HTTP 200, JSON inválido, redução anormal ou
mudança das colunas esperadas interrompe a atualização antes da troca atômica
do arquivo `catalogo_acordaos.json`, preservando o catálogo anterior.
