# Precedentes Relevantes

A interface usa uma única categoria, `precedente_relevante`, com os subtipos
internos `adi`, `adc`, `adpf`, `ado`, `iac` e `sirdr`. O subtipo `irdr` fica
reservado para futura importação direta dos tribunais de origem. Repercussão Geral,
Recursos Repetitivos, Súmulas, Súmulas Vinculantes e Acórdãos continuam em suas
categorias principais próprias.

## Controle concentrado do STF

Os registros existentes de ADI, ADC, ADPF e ADO são consolidados sem alterar
identificação, texto, relações, fonte ou metadados processuais. O antigo tipo
fica registrado em `tipo_original`; `subtipo` identifica a classe dentro da
gaveta única.

## IAC

A cobertura de IAC é a coleção completa de Incidentes de Assunção de
Competência presente nos CSVs oficiais de **Precedentes Qualificados** do Portal
de Dados Abertos do STJ. O importador cruza `temas.csv` e `processos.csv` para
obter questão, tese, situação, processos representativos, relator, órgão e
datas. IAC cancelado não é importado como precedente atual.

## SIRDR e IRDR: cobertura efetiva

Não existe atualmente importação direta ou cobertura nacional de IRDR. A
cobertura é limitada às **Suspensões em Incidente de Resolução de Demandas
Repetitivas (SIRDR)** registradas na coleção estruturada do STJ. Esses registros
usam `subtipo: sirdr` e mantêm o número do SIRDR no STJ, sua situação e URL,
além do tribunal e da identificação do IRDR de origem quando disponíveis.

Uma SIRDR é um pedido ao STJ de suspensão nacional relacionado a um IRDR já
admitido em TJ ou TRF. Portanto, as contagens desta camada medem somente esse
recorte oficial e não o universo nacional de IRDRs. SIRDR marcada pelo STJ como
`Vinculada a tema repetitivo` não é recriada na gaveta de Precedentes
Relevantes, pois a matéria já pertence à categoria Recursos Repetitivos.

## Integridade

As fontes são acessadas por HTTPS com o *truststore* do updater, sem
`verify=False` e sem seguir redirecionamentos. Os dois CSVs são validados antes
da substituição atômica do catálogo. Resposta vazia, falso HTTP 200, estrutura
alterada, situação desconhecida, coleção truncada ou duplicação preservam o
arquivo anterior.

Relações `CDC art. X` são extraídas somente quando a fonte oficial traz, na
mesma expressão, o artigo e a identificação do CDC ou da Lei 8.078/1990.
