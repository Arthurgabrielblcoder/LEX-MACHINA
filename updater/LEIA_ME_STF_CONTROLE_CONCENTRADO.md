# STF — Controle concentrado: ADI, ADC, ADPF e ADO

O `main.py` atualiza o `catalogo_precedentes.json` com tipos distintos `adi`,
`adc`, `adpf` e `ado`. O importador preserva os registros de Repercussão Geral,
entradas manuais e outras categorias. Não altera o importador de RG.

## Fonte oficial e pesquisa realizada

Fonte adotada: [STF / Corte Aberta / Controle Concentrado](https://transparencia.stf.jus.br/extensions/controle_concentrado/controle_concentrado.html).
As tabelas públicas são consultadas diretamente por JSON-RPC sobre WebSocket
seguro, usando os mesmos objetos das exportações do painel, sem scraping de
decisões em HTML e sem filtros de sessão.

- [Script oficial que declara aplicação e objetos](https://transparencia.stf.jus.br/extensions/controle_concentrado/qliksense.js).
- Aplicação: `c47ea922-dbfe-4c3e-9d21-77cd2fed770d`.
- Endpoint: `wss://transparencia.stf.jus.br/app/c47ea922-dbfe-4c3e-9d21-77cd2fed770d`.
- Processos: objeto `LBZHET`.
- Decisões: objeto `750a9fab-e94b-477f-ab91-f58cb67b854e`.
- Métodos: `OpenDoc`, `GetAppLayout`, `GetObject`, `GetLayout`, `GetHyperCubeData`.
- Caminho de dados: `/qHyperCubeDef`; todas as páginas são lidas, respeitando
  o limite de células. `qColumnOrder` define a correspondência entre colunas e
  células: na tabela de decisões, a coluna Data não está na ordem da lista de
  dimensões. Tamanho, área, número de linhas, duplicatas e esquema são validados.
- Os registros retêm o link oficial individual `portal.stf.jus.br/processos/detalhe.asp?incidente=...`.

Alternativas examinadas em 15/09/2026:

1. [Pesquisa de jurisprudência](https://jurisprudencia.stf.jus.br/pages/search):
   retornou HTTP 202 vazio na consulta HTTP e não forneceu dados no navegador.
2. [Pesquisa de ADI/ADC/ADO/ADPF](https://portal.stf.jus.br/peticaoInicial/pesquisarPeticaoInicial.asp):
   apresenta tabela HTML com paginação local DataTables e remete à jurisprudência
   para decisões. A busca e duas fichas foram examinadas, mas seus dados não são
   usados na importação.
3. [Corte Aberta](https://portal.stf.jus.br/hotsites/corteaberta/): conduziu ao painel
   de Controle Concentrado. Os scripts oficiais publicam objetos de exportação
   de processos e decisões. A conexão WebSocket inicial, sem a sessão normal do
   painel, retornou 403. O fluxo normal (sessão HTTP do painel, cookies próprios
   e cabeçalho de agente compatível) permitiu a leitura JSON anônima. Não há login,
   credenciais incorporadas, desativação de certificados ou solução de CAPTCHA.

O contrato é o da aplicação pública do STF, não uma API com garantia de versão.
Mudanças de contrato interrompem a atualização e preservam o catálogo.

## Critérios e limites de cobertura

- `encontrados`: processos únicos presentes na tabela oficial, antes do filtro.
  Não representa a totalidade histórica de processos que eventualmente não
  estejam nesse painel. `decisoes_encontradas` conta separadamente seus andamentos
  de decisão, inclusive liminares e decisões interlocutórias.
- `consumeristas`: triagem lexical pelos sinais já usados em RG, aplicada aos
  campos Ramo do Direito, Assunto relacionado, Legislação e Observação das decisões
  finais. Referência estruturada explícita a artigo do CDC também seleciona o
  processo. É um sinal textual de relevância, não classificação jurídica definitiva.
  A triagem pode incluir assuntos tributários que mencionem consumidor final e
  pode deixar de identificar casos cujo vocabulário não contenha esses sinais.
- `importados`: candidatos com ao menos um registro oficial classificado como
  Decisão Final, resultado Procedente, Procedente em parte ou Improcedente, data
  válida e texto que identifique o Tribunal como autor do julgamento colegiado.
  Liminares isoladas, decisões monocráticas, extinções sem mérito e textos não
  informados não geram precedentes automaticamente.
- Havendo mais de uma decisão de mérito, usa-se a mais recente. Empate ambíguo
  não é resolvido automaticamente. Decisões posteriores são incluídas no texto,
  inclusive embargos classificados pelo painel como Decisão Final, e andamentos
  sem data são identificados como tal. Não há interpretação automática de efeitos
  modificativos, modulação, vigência ou superação. Os registros não equivalem ao
  inteiro teor dos acórdãos: são os textos de andamento publicados pelo STF.
- ADO tem suporte completo e testes; zero selecionados não significa inexistência
  de ADOs de possível interesse consumerista fora deste recorte e desta triagem.

## Vínculos com artigos do CDC

Não se infere artigo por assunto. Um vínculo exige uma expressão explícita de
artigo e CDC/Lei 8.078 na mesma referência, sem atravessar referências a outras
leis. Os números de parágrafos, incisos, anos e artigos da Constituição não são
aproveitados como artigos do CDC.

Fontes de vínculo:

- Texto individual de Observação das decisões oficiais: extrator restritivo já
  usado em RG, aplicado separadamente por decisão.
- Campo estruturado Legislação: por exemplo,
  `Código de Defesa do Consumidor de 1990, Art. 3º, § 2º`. A extração admite somente
  a sequência direta de lei identificada e artigo, não inferência a partir do tema.

Cada relação guarda `evidencias_relacoes_cdc`, com campo e texto oficial.
Na execução validada, ADI 2591 liga-se a CDC art. 3 por esse campo Legislação.
Esse vínculo documental não afirma que todos os trechos da decisão tratem do artigo.

## Segurança e preservação

- HTTPS e WSS usam o contexto `truststore` da sessão STF, com validação de cadeia
  e hostname. Não há `verify=False`, alteração global de SSL ou certificado customizado.
- URLs de processo são restritas ao host e caminho oficiais, sem credenciais,
  portas alternativas ou destinos externos. Redirecionamentos são bloqueados.
- HTTP vazio, 202, páginas de erro com HTTP 200, JSON inválido, filtros ativos,
  classe ausente, página truncada/repetida ou mudança da base durante a leitura
  impedem a substituição do catálogo.
- As quatro classes formam uma transação: só há substituição atômica após a leitura
  completa e validação. Registro automático anterior fora da seleção bloqueia a
  substituição e exige revisão. Zero candidatos de uma classe é permitido quando
  ela está presente na base e não causa perda de registro anterior.
- Deduplicação por tribunal, classe, número, processo associado e URL. ADI 10 e
  ADC 10 são identidades distintas. Entradas manuais prevalecem. A integração em
  `main.py` também verifica os catálogos de jurisprudência e acórdãos.
- RG continua com sua própria transação e preserva todas as novas classes.

## Executar

No diretório `C:\GitHub\LEX-MACHINA\updater`, com Python 3.10 ou superior:

```powershell
python -m pip install -r requirements.txt
python -m unittest -v test_importar_stf_repercussao_geral test_importar_stf_controle_concentrado
python main.py
```

Também é possível executar `python importar_stf_controle_concentrado.py` isoladamente.
O comando isolado termina com código 1 quando a atualização é preservada por falha.

- `python main.py --sem-stf-controle`: atualiza RG, sem consultar controle concentrado.
- `python main.py --sem-stf`: não consulta nenhuma das duas camadas STF.
- Sem argumento de destino externo, saídas ficam em `updater/saida/`.
- `saida/` é temporária e ignorada pelo Git. O script investigativo
  `saida/pesquisar_qlik_stf.py` foi removido na revisão final; o funcionamento
  normal depende somente dos módulos fora dessa pasta. As amostras versionáveis
  de teste estão em `tests/fixtures/`.
- Relatório por classe: `saida/relatorio_stf_controle_concentrado.json`.
  `ok` e `contagens_completas` devem ser conferidos antes de interpretar as contagens.
- Logs desta validação: `saida/testes_stf_controle.log`,
  `saida/verificacao_stf_controle.log`, `saida/verificacao_main_stf_controle.log`.

## Validação de 15/09/2026

Base atualizada pelo STF em `2026-09-15T09:20:41.019Z`.

| Classe | Processos oficiais | Decisões na base | Sinal consumerista | Importados | Com artigo CDC explícito |
| --- | ---: | ---: | ---: | ---: | ---: |
| ADI | 7.143 | 15.342 | 194 | 142 | 1 |
| ADC | 99 | 300 | 1 | 1 | 0 |
| ADPF | 1.338 | 3.036 | 34 | 17 | 0 |
| ADO | 95 | 180 | 0 | 0 | 0 |

Total: 8.675 processos, 18.858 decisões na base, 160 registros novos de controle
concentrado. Os 37 registros de RG são preservados. As amostras oficiais reduzidas
em `tests/fixtures/` permitem testar parsing e ordem de colunas sem conexão.
Os demais testes simulam falhas de rede, respostas inválidas, disco, duplicação,
preservação entre importadores e geração do índice. São 40 testes incluindo os
18 testes anteriores de RG.

`python main.py` concluiu com código 0, 0 erros e 1 alerta de integridade
preexistente do Catálogo Mestre (Lei Maria da Penha). RG repetiu 811 temas
oficiais, 37 candidatos e 37 importados, com Tema 1075 → CDC art. 93.
O catálogo final tem 197 registros, sem identidades duplicadas. Os 37 objetos
de RG são idênticos aos versionados antes desta expansão. `pip check` e
`git diff --check` passaram. Os hashes de `firmware/` e `sdcard/` permaneceram
iguais; não foi realizado commit.
