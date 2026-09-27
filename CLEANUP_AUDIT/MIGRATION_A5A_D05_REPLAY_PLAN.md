# Migração A5A — plano de replay isolado do pipeline legado D05

## 1. Escopo e conclusão

Esta etapa planeja a futura A5B sem executar nenhum produtor D05. O replay seguro exige somente os dois compiladores determinísticos já registrados como receitas históricas:

1. `07_CATALOGO_CANDIDATO/compilar_catalogo.py`;
2. `07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py`.

O Dataset Lock não dirige nenhuma dessas execuções. Ele permanece sombra. A seleção continua sendo feita pelo código legado sobre cópias byte-idênticas dos inputs históricos.

A A5B é tecnicamente segura se cumprir integralmente os gates deste documento: cópia mínima fora do repositório, execução por um runner offline com escrita confinada, hashes de entrada conferidos antes da execução e retenção do sandbox após o replay.

## 2. Pipeline executável necessário

### Fase P1 — catálogo-base

`compilar_catalogo.py` lê, a partir de `ROOT = Path(__file__).resolve().parents[1]`:

- `02_TRIAGEM/LOTE_01.json` até `LOTE_08.json`;
- 199 dossiês em `04_DOSSIERS/<work_id>.json`, selecionados pelo próprio legado;
- `00_ENTRADA/REFERENCIA_CATALOGO_69.json`.

O código exige 200 números únicos, ordena por `work_id`, aplica `APTA`/`APTA_COM_RESSALVA` e produz:

- `07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json`;
- `07_CATALOGO_CANDIDATO/CATALOGO_TOTAL_69_MAIS_APTAS.json`.

Classificação: **PURE_LOCAL_DETERMINISTIC**. O argumento posicional de saída é suportado. Não há timestamp, rede, aleatoriedade, UUID, locale, mtime ou variável de ambiente no conteúdo.

### Fase P2 — pacote enriquecido

`compilar_enriquecido_v1.py` lê:

- o catálogo-base gerado pela P1 no path fixo `07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json`;
- 111 overlays em `04_DOSSIERS/ENRIQUECIMENTO_V1/<work_id>.json`;
- `06_RELATORIOS/REVISOES_ENRIQUECIMENTO_V1.json`;
- `06_RELATORIOS/CHECKPOINT_ENRIQUECIMENTO.json`;
- `00_ENTRADA/REFERENCIA_CATALOGO_69.json`.

Ele produz sete membros no diretório passado como argumento:

- quatro JSONs de catálogo, decisões e cards;
- `METADADOS_ENRIQUECIDO_V1.json`;
- `README.md`;
- `MANIFEST.json`.

Classificação: **PURE_LOCAL_DETERMINISTIC**. O compilador ordena obras por `work_id`, localiza overlays por path exato, exige aplicação das três revisões e confere 111 obras examinadas contra a fila.

## 3. Fases excluídas

| script/fase | classe | motivo da exclusão |
|---|---|---|
| `enriquecer_v1.py baseline/checkpoint` | `LOCAL_BUT_STATEFUL` | cria baseline, estado, checkpoints e overlays; usa hora atual e escrita in-place |
| `editorial_enriquecimento_v1.py` | `LOCAL_BUT_STATEFUL` | chama `checkpoint()` e recriaria overlays/checkpoints já congelados |
| `aplicar_saneamento_pre_enriquecimento.py` | `LOCAL_BUT_STATEFUL` | altera lotes, identidade, fontes e dossiês in-place |
| `consultar_fontes_enriquecimento.py` | `REMOTE_OR_NONDETERMINISTIC` | usa `urllib.request`, concorrência, URLs públicas e hora atual |
| `gerar_relatorios.py` | `REMOTE_OR_NONDETERMINISTIC` | usa `datetime.now`, escreve relatórios fixos e cria diretórios temporários |
| `gerar_manifest.py` | `REMOTE_OR_NONDETERMINISTIC` | usa hora, mtime, Git e varredura recursiva do repositório; regrava manifests históricos |
| `estado_retomada.py` | `NOT_REQUIRED_FOR_REPLAY` | inventaria estado e grava relatório; não alimenta os dois compiladores |
| `relatorios_enriquecimento_v1.py` | `NOT_REQUIRED_FOR_REPLAY` | reconstrói auditorias, mas seus outputs não alimentam a compilação |
| `estimar_enriquecimento.py` | `NOT_REQUIRED_FOR_REPLAY` | produz a estimativa que originou a fila histórica; a fila congelada já é input direto |

`gerar_relatorios.py` e `gerar_manifest.py` acumulam também a classe `NOT_REQUIRED_FOR_REPLAY`. Sua classificação primária acima destaca o risco que impede sua execução.

## 4. Rede

A A5B deve operar offline. Nenhum dos dois compiladores requer rede, importa biblioteca de rede, invoca modelo remoto ou consulta API. URLs existentes são dados históricos dentro dos JSONs.

Antes dos compiladores, a A5B deve criar no próprio sandbox um runner de controle, sem alterar os scripts legados. Esse runner deve:

- registrar um audit hook Python antes de `runpy.run_path`;
- rejeitar eventos `socket.*`, `subprocess.Popen` e `os.system`;
- rejeitar qualquer abertura para escrita cujo path resolvido fique fora do sandbox;
- definir `sys.argv` exatamente como numa chamada direta;
- encerrar com código diferente de zero em qualquer violação.

Se o runner não puder ser instalado ou demonstrado por um teste negativo antes do replay, a A5B deve parar.

## 5. Sandbox proposto

Raiz:

`C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\<run_id>`

Estrutura:

```text
<run_id>/
  control/
    offline_exec.py
  logs/
  run_record/
    D05_REPLAY_RUN.json
  workspace/
    LEX_MACHINA_REFERENCIAS_V2/
      09_CATALOGO_EXPANSAO_200/
        00_ENTRADA/
        02_TRIAGEM/
        04_DOSSIERS/
          ENRIQUECIMENTO_V1/
        06_RELATORIOS/
        07_CATALOGO_CANDIDATO/
          REPLAY_ENRIQUECIDO_V1/
```

O sandbox deve ser criado somente na A5B. Antes de qualquer cópia recursiva ou futura remoção, o path resolvido deve começar exatamente por `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\` e não pode estar dentro de `C:\GitHub\LEX-MACHINA`.

## 6. Contrato mínimo de cópia

Copiar somente:

| grupo | quantidade | digest SHA-256 do manifesto canônico path/hash/size |
|---|---:|---|
| lotes de triagem | 8 | `eca731b4f6b94ba2bc7f61a0a186ce666c91b1f441e694cad50a258bab69ece0` |
| dossiês-base | 199 | `7de5b76ccfd32be5baff828340b6dd246a6e37bd972fbc798043c19c24d4dcaf` |
| overlays | 111 | `d9e29c82dbd40b7c785bd11b1ec7f563d96a91789e9ad0fce0e1c6cae5ea076d` |

Arquivos únicos:

| arquivo | SHA-256 |
|---|---|
| `00_ENTRADA/REFERENCIA_CATALOGO_69.json` | `5443ae84050764950b1b9648733016f697eaf740a6c920be6201583327829129` |
| `06_RELATORIOS/CHECKPOINT_ENRIQUECIMENTO.json` | `479997a8aa3b09c8b56505705e0e4b75b14211bd061b4e1213cc4bbde4a9c293` |
| `06_RELATORIOS/REVISOES_ENRIQUECIMENTO_V1.json` | `1b1a8e439d52d24c379c13d2c2da1be8e1750f116f519f8cd77c4ba8f2d966dd` |
| `07_CATALOGO_CANDIDATO/compilar_catalogo.py` | `4e53ca2a87bd0577facb4461b09b685223c4daabe869cfaff81610e6cdc66a7d` |
| `07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py` | `d0621feaeaf0288285475cebc747ffad76a4cb40a8e65ec076b8541bb5053a08` |

Não copiar os nove outputs históricos. A pasta de saída começa vazia, exceto pelos dois scripts. Depois da cópia, a A5B deve recalcular os três manifests de grupo e os cinco hashes únicos. Qualquer divergência aborta antes da execução.

## 7. `restricted_local`

Os três artefatos `restricted_local` não participam do replay mínimo:

- `BUSCA_118.json` não é aberto por nenhum dos dois compiladores; o fato editorial necessário já está incorporado no dossiê selecionado.
- `CONSULTA_CP11.txt` e `CONSULTA_CP12.txt` não são lidos pelos compiladores; overlays, fila e revisões persistidas são as entradas relevantes.

Eles não devem ser copiados, versionados ou tocados. O Registry e o Dataset Lock continuam exigindo sua presença no repositório original para seus próprios gates, antes e depois do replay.

## 8. Paths absolutos

`REFERENCIA_CATALOGO_69.json` contém o path histórico absoluto:

`C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1\CATALOGO_69_CANONICO.json`

Os compiladores não abrem esse path. Eles usam a lista `obras` embutida e preservam a string do path nos outputs. A cópia deve permanecer byte-idêntica; reescrever o path para o sandbox mudaria os outputs.

Todos os demais inputs são resolvidos a partir de `__file__`. Preservar a estrutura relativa da árvore D05 no sandbox é suficiente. Nenhum código necessário calcula a raiz do repositório ou escreve no path original.

## 9. Checkpoints e estado

O replay começa do estado editorial já congelado, não de um checkpoint intermediário de criação:

- `CHECKPOINT_ENRIQUECIMENTO.json` é somente leitura e fornece a fila de 111 obras;
- os 12 `CP_*.json` comprovam a história, mas não são lidos pelos dois compiladores e não precisam ser copiados;
- nenhum novo checkpoint deve ser produzido;
- `enriquecer_v1.py`, `editorial_enriquecimento_v1.py` e qualquer comando `baseline`, `checkpoint` ou `inspect` ficam proibidos.

Se um comando tentar criar ou modificar arquivo fora dos dois roots de saída esperados, o runner deve abortar.

## 10. Volatilidade

| fonte | classificação | tratamento A5B |
|---|---|---|
| Python | `CONTROLAVEL` | exigir CPython 3.12.9 e registrar `sys.version` |
| hash seed | `CONTROLAVEL` | `PYTHONHASHSEED=0`; os compiladores já usam ordenação explícita onde importa |
| encoding/newlines | `CONTROLAVEL` | `PYTHONUTF8=1`, `-X utf8`; outputs usam UTF-8 e LF explícitos |
| plataforma | `CONTROLAVEL` | Windows; registrar versão do sistema |
| datetime/timestamp | ausente nos compiladores | não há mitigação necessária nos nove outputs |
| random/UUID | ausente | nenhuma |
| locale/timezone | `IGNORAVEL_POR_DESIGN` | não participam de ordenação nem serialização dos outputs |
| hostname/username | ausente | nenhuma |
| mtime | ausente | não copiar para os outputs nem usar `gerar_manifest.py` |
| path absoluto | `IGNORAVEL_POR_DESIGN` | string histórica da referência 69 deve permanecer intacta |
| run_id, logs e timestamps do run record | `IGNORAVEL_POR_DESIGN` | evidência operacional; não comparar com output histórico |

Não há fonte de volatilidade classificada como `BLOCKING` nos dois compiladores.

## 11. Ordem de filesystem

Plataforma esperada: Windows com Python 3.12.9.

- os lotes são abertos por nomes explícitos `LOTE_01..08`;
- as obras-base são ordenadas por `work_id`;
- as 69 referências são ordenadas por `id`;
- overlays são localizados por `<work_id>.json`;
- o mapa de hashes de overlays usa `sorted(ov_dir.glob('*.json'))`;
- os membros do manifesto interno usam `sorted` por nome.

Não há `os.listdir` ou `Path.iterdir` nos dois compiladores. Os dois `glob` existentes são ordenados explicitamente. A5B deve conferir que há exatamente 111 overlays e que a pasta de saída enriquecida começa vazia, evitando membros extras no manifesto.

## 12. Comandos planejados para A5B

Os comandos abaixo são especificação; não foram executados nesta etapa.

### 12.1 Preflight no repositório original

```powershell
Set-Location -LiteralPath 'C:\GitHub\LEX-MACHINA'
git rev-parse HEAD
python -X utf8 ARTIFACT_REGISTRY\verify_registry.py
python -X utf8 DATASET_LOCKS\verify_lock.py
git diff --quiet
git diff --cached --quiet
```

Condição: HEAD `b134aa2130965275d39aa3e6ab372aa010c17a47`, dois `PASS` e nenhuma alteração rastreada/staged.

### 12.2 Preparação

```powershell
$ReplayRoot = 'C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\<run_id>'
$SourceD05 = 'C:\GitHub\LEX-MACHINA\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200'
$ReplayD05 = Join-Path $ReplayRoot 'workspace\LEX_MACHINA_REFERENCIAS_V2\09_CATALOGO_EXPANSAO_200'
```

A A5B deverá criar os diretórios explícitos, copiar o contrato da seção 6 com `Copy-Item -LiteralPath`, criar `offline_exec.py` dentro de `control`, recalcular todos os hashes e testar que o runner bloqueia uma conexão e uma escrita para fora do sandbox.

### 12.3 P1

CWD: `$ReplayD05`.

```powershell
$env:PYTHONHASHSEED = '0'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
python -I -X utf8 "$ReplayRoot\control\offline_exec.py" --root "$ReplayRoot" --script "$ReplayD05\07_CATALOGO_CANDIDATO\compilar_catalogo.py" -- "$ReplayD05\07_CATALOGO_CANDIDATO"
```

Inputs: oito lotes, 199 dossiês e referência 69. Outputs: dois catálogos-base. Abortar em exit code não zero, escrita fora do sandbox, quantidade diferente de dois, cardinalidade diferente de 199/221 ou hash divergente.

### 12.4 P2

CWD: `$ReplayD05`.

```powershell
python -I -X utf8 "$ReplayRoot\control\offline_exec.py" --root "$ReplayRoot" --script "$ReplayD05\07_CATALOGO_CANDIDATO\compilar_enriquecido_v1.py" -- "$ReplayD05\07_CATALOGO_CANDIDATO\REPLAY_ENRIQUECIDO_V1"
```

Inputs: catálogo-base gerado, 111 overlays, fila/checkpoint, três revisões e referência 69. Outputs: sete arquivos. Abortar em exit code não zero, escrita externa, output extra/faltante, cardinalidade diferente de 199/221/71/292/111 ou hash divergente.

### 12.5 Pós-execução

Executar novamente no repositório original os verificadores do Registry e do Lock, o gate direcionado de integridade, `git diff --quiet`, `git diff --cached --quiet` e hashes da Golden Reference. Qualquer alteração no original invalida a A5B.

## 13. Outputs e comparação

Todos os nove outputs devem ser **BYTE_IDENTICAL** por SHA-256. Não há exceção semântica autorizada.

| output | SHA-256 esperado |
|---|---|
| `CATALOGO_EXPANSAO_200.json` | `5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43` |
| `CATALOGO_TOTAL_69_MAIS_APTAS.json` | `6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6` |
| `CATALOGO_EXPANSAO_ENRIQUECIDO_V1.json` | `cddb00344f6e3075f552fb042b168d184463b85e513f695eb1089139ee301da7` |
| `CATALOGO_TOTAL_ENRIQUECIDO_V1.json` | `5446da1294cee6311dcef3a0c5438b7c7de2bc2adec586fe38b85f199394305d` |
| `DECISOES_ENRIQUECIMENTO.json` | `de779c2f5873d665953d849d37643e21219da428df89b534a24781b8031e8c30` |
| `EVIDENCE_CARDS_ENRIQUECIDOS_V1.json` | `3446c073eda030045bc20efe0ac0854c924fe7b11e66a71d0671d6717f054a07` |
| `METADADOS_ENRIQUECIDO_V1.json` | `27a427ccd18813992f633e8f94bb59e8a2e46a1d6558b95d8c37ef7e037c2f02` |
| `README.md` | `423b90dde03d10cd268681b55f18e6fa51007fd1af939d09b80be952a2cbe9e3` |
| `MANIFEST.json` | `0312e5f091981f8065673529aca04437ed0fc7ecaac26cd144d2af26ab37774c` |

As verificações estruturais mínimas são: dois catálogos-base; sete membros enriquecidos; 199 obras utilizáveis; 221 cards-base; 71 novos; 292 finais; 111 decisões examinadas; três revisões aplicadas; manifesto interno com seis payloads.

A A5B deve registrar a seleção e a ordem efetivamente observadas, mas não fazer a comparação formal com o Dataset Lock. Essa comparação pertence à A6.

## 14. Run record

O run record será criado em `<sandbox>\run_record\D05_REPLAY_RUN.json`, sem escrita em `CLEANUP_AUDIT` do repositório original. Deve conter:

- `run_id`, HEAD, tag e sandbox resolvido;
- Windows, Python e variáveis controladas;
- hash do runner offline;
- manifests e hashes dos inputs antes/depois da cópia;
- comandos completos, cwd, stdout/stderr e exit codes;
- `network_disabled: true` e resultados dos testes negativos do runner;
- lista, tamanho e SHA-256 dos nove outputs;
- métricas e ordem observadas;
- diferenças byte a byte;
- hashes e status do repositório original antes/depois.

Logs ficam em `<sandbox>\logs`. Run record e logs são evidência operacional volátil, não outputs históricos.

## 15. Escritas potenciais

P1 escreve somente os dois catálogos no diretório recebido. P2 escreve somente sete arquivos no diretório recebido. Ambos criam diretórios pais quando necessário.

O risco residual é erro de argumento ou alteração inesperada do script. Ele é fechado por quatro barreiras: hashes exatos dos scripts, roots dentro do sandbox, audit hook de escrita e verificação pós-execução do original. Um path de saída fora do sandbox, output preexistente ou hash de script divergente deve bloquear antes do replay.

## 16. Condições de bloqueio

A A5B deve parar se ocorrer qualquer item abaixo:

- HEAD, Registry, Lock, Golden ou integridade divergente;
- script ou input copiado com hash divergente;
- sandbox resolvido dentro do repositório original;
- runner não bloquear rede, subprocesso ou escrita externa;
- Python diferente de 3.12.9 sem revisão explícita do risco de bytes;
- pasta de output não vazia;
- necessidade de rede, segredo ou alteração de código;
- tentativa de executar qualquer script excluído;
- tentativa de copiar ou modificar `restricted_local`;
- checkpoint ou output histórico exposto a escrita;
- cardinalidade, exit code, lista de outputs ou SHA-256 divergente.

Não foi encontrado bloqueio estrutural atual para a A5B sob esse contrato.

## 17. Retenção e rollback

O sandbox não deve ser apagado automaticamente. Após a execução, ele permanece disponível para inspeção, com logs, run record, inputs copiados e outputs.

A limpeza só pode ocorrer após aprovação específica. Antes de `Remove-Item -Recurse`, a A5B ou etapa posterior deve resolver o path absoluto, comprovar que ele começa por `C:\GitHub\_LEX_MACHINA_D05_REPLAY_TEMP\`, comprovar que não é a raiz compartilhada nem o repositório original e registrar os hashes finais. A remoção nunca integra o replay automático.

## 18. Critérios para autorizar A5B

A5B está pronta para autorização quando o executor concordar em:

1. criar o sandbox externo;
2. materializar e testar o runner offline/confinado;
3. copiar somente o contrato mínimo e conferir hashes;
4. executar somente P1 e P2;
5. exigir byte identity dos nove outputs;
6. preservar o sandbox para revisão;
7. revalidar o repositório original sem copiar resultados para ele;
8. parar antes de qualquer comparação formal Lock ↔ replay, reservada à A6.

Este documento não autoriza nem inicia a A5B.
