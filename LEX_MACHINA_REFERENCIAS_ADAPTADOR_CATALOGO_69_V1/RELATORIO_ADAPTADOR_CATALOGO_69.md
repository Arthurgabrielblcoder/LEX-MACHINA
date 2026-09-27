# Adaptador determinístico do catálogo de 69 obras

## Resultado

O adaptador normalizou 24 obras históricas e 45 obras aprovadas para `REFERENCIA_CANONICA_V1`, com 69 IDs únicos, reversibilidade integral e preservação do homônimo `O Processo`.

## Esquemas

- **Esquema A — 24 antigas:** 22 campos históricos; inclui temas sem faixas, `forca_por_tema` numérica e `valor_pedagogico` numérico.
- **Esquema B — 45 novas:** 28 campos; distingue temas centrais/fortes/secundários, objetos compatíveis/fracos, áreas categóricas, alertas e travas.
- **REFERENCIA_CANONICA_V1:** 21 campos principais, extensões de origem e cópia integral do registro-fonte para reversibilidade.

Foram mapeados diretamente **20 campos canônicos distintos**. Nas antigas houve **291 ocorrências de campos vazios/default explícito**; nas novas, **73**. Nenhum conteúdo foi inventado e nenhuma informação de origem foi perdida, pois `registro_origem_integral` preserva cada registro byte-semanticamente.

## Contrato real da Engine

A v1.3.2 é calibradora: recebe resultados da v1.3.1 e não lê catálogo de obras. O leitor histórico aplicável está na v1.2 (`DeterministicSemanticAnalyzer.analyze_work`). Ele lê 22 campos e acessa diretamente 8 deles. Converte `ano`, `valor_pedagogico` e `forca_por_tema` em números.

As 45 novas não possuem `valor_pedagogico` numérico nem `forca_por_tema` numérica. Converter `CENTRAL/FORTE/SECUNDARIO` em números ou escolher um valor pedagógico violaria a proibição de pesos ocultos. Por isso, `CATALOGO_69_INPUT_ENGINE_V132.json` é um artefato de preflight marcado `engine_executavel=false`, com 24 registros compatíveis e 45 bloqueados de forma explícita.

## Retrocompatibilidade das 24

`CATALOGO_24_INPUT_ENGINE_V132_ADAPTADO.json` é cópia byte a byte da entrada histórica. SHA-256 original e adaptado: `48189658c9bd850895d043ba3489158744a3ec6c9754b8bd1559c19942b35d47`. Não há diferença estrutural ou semântica.

## Determinismo e preservação

O script ordena chaves, usa ordem fixa das fontes e não contém relógio, aleatoriedade ou rede. A validação executa o adaptador duas vezes e exige hashes idênticos. Engine, benchmark, CF segmentada e arquivos-fonte permanecem somente leitura.

## Recomendação

Os 69 registros estão prontos no esquema canônico, mas **não estão prontos para scoring da Engine**. Antes da execução comparativa, é necessária uma decisão humana/versionada sobre os campos numéricos exigidos pelo leitor histórico, ou um contrato de entrada novo em versão futura da Engine. Nenhuma dessas decisões deve ser introduzida silenciosamente pelo adaptador.
