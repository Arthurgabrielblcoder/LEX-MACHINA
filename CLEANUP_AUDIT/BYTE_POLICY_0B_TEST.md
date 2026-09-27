# Etapa 0B — teste da política de preservação de bytes

Resultado: **APROVADA para revisão e consolidação posterior**. A política candidata preservou os bytes atuais no repositório original e em um clone externo com `core.autocrlf=true`. Não houve staging, commit/tag no repositório original, renormalização ou execução funcional.

## Estado e escopo

| Item | Resultado |
|---|---|
| HEAD original | `c4462fffd3e532975fc4ad7a748b4d9b12a795b5` |
| branch | `main` |
| `core.autocrlf` original | `true` |
| índice antes/depois | vazio |
| mudanças rastreadas antes/depois | zero |
| política | `.gitattributes`, ainda não rastreado |
| baseline | `CLEANUP_AUDIT/BYTE_POLICY_0B_BASELINE.json`, não rastreado |
| relatório 0A preexistente | `CLEANUP_AUDIT/BYTE_POLICY_PROPOSAL.md`, não rastreado |
| Engine/pipeline/IDX | não executados nem regenerados |

O baseline foi capturado **antes** da criação de `.gitattributes`. Ele contém SHA-256, tamanho, mtime e EOL dos conjuntos, além das listas completas e da validação das exceções.

## Regras implementadas

1. `LEX_MACHINA_REFERENCIAS_V2/** -text` preserva bytes por padrão.
2. Cinco padrões restritos aplicam `text eol=lf` aos 18 scripts mantidos da expansão.
3. As exceções CRLF vêm depois e aplicam `text eol=crlf` aos paths que precisam reproduzir os bytes atuais.
4. Os 29 protected545 versionados possuem regras exatas: seis `text eol=crlf` e 23 `-text`.
5. `*.IDX -text` e `*.idx -text` são somente proteção prospectiva.
6. `.gitattributes text eol=lf` fixa o próprio arquivo de política.

A ordem foi validada pelo resultado efetivo de `git check-attr`, não apenas por inspeção visual.

## Validação das exceções CRLF

Quantidade prevista: **85 padrões**. Quantidade real: **85 padrões**.

Os padrões compactam **349 arquivos V2 atuais em CRLF**. Para cada padrão foi confirmado antes da escrita:

- ao menos um path correspondente;
- todos os paths existem e são versionados;
- todos usam CRLF puro no working tree;
- SHA-256 e tamanho foram registrados;
- motivo: o blob/index está em LF sob `autocrlf`, portanto `text eol=crlf` é necessário para reproduzir os bytes atuais.

Os padrões cobrem exatamente os 349 arquivos CRLF, sem path adicional e sem ausência.

## Baseline e working tree original

Foram hashados **1.677 arquivos únicos**:

| Grupo | Quantidade | Depois da política |
|---|---:|---:|
| V2 versionada | 1.132 | 1.132 idênticos |
| originalmente expostos LF→CRLF | 781 | 781 idênticos |
| protected545 total | 545 | 545 idênticos |
| protected545 versionados | 29 | 29 idênticos |
| protected545 snapshot-only | 516 | 516 idênticos no repositório original |
| ENRIQUECIDO_V1 | 7 | 7 idênticos |
| scripts mantidos | 18 | 18 idênticos |
| congelados V2 | 281 | 281 idênticos |
| IDX | 130 | 130 idênticos |

Resultado antes/depois no repositório original:

- divergências de SHA-256/tamanho: **zero**;
- divergências de mtime nos 1.677 arquivos monitorados: **zero**;
- `git status --short --untracked-files=no`: vazio;
- `git diff --stat`: vazio;
- `git diff -- .gitattributes`: vazio porque o arquivo permanece untracked;
- `git diff --cached --name-only`: vazio;
- SHA-256 da política: `b7e19bb3a3437fbce755340781c90e24900daeef146bc891a67e6a55df71bc0a`.

Não foi usado `git add`, `git add --renormalize`, checkout forçado no original ou qualquer ferramenta de conversão.

## Atributos efetivos

Na V2 original:

| Atributo efetivo | Arquivos |
|---|---:|
| `-text`, working tree LF | 764 |
| `-text`, binários | 2 |
| `text eol=crlf` | 349 |
| `text eol=lf` | 17 |

Nos 29 protected545 versionados:

| Atributo efetivo | Arquivos |
|---|---:|
| `-text` | 23 |
| `text eol=crlf` | 6 |

Nos 130 IDX fora do Git, `git check-attr` retorna `text: unset` por causa de `*.IDX -text`; nenhum foi adicionado ao índice.

Amostras confirmadas:

- `INTEGRITY_BEFORE.json` e `ENRIQUECIDO_V1/MANIFEST.json`: `text: unset`;
- `editorial_enriquecimento_v1.py`: `text`, `eol=lf`;
- `gerar_relatorios.py`: `text`, `eol=crlf`;
- `CATALOGO_69_CANONICO.json`: `text`, `eol=crlf`;
- firmware protegido atual: `text: unset`.

## Clone/test tree externo

Clone aprovado:

`C:\Users\arthu\AppData\Local\Temp\lex-byte-policy-0b-324c146437c742c98af84d4b2c67446d`

Método usado para garantir que a política candidata participou do checkout:

1. `git clone --no-checkout --no-hardlinks` do repositório local;
2. `git read-tree HEAD` para manter toda a árvore original no índice do clone;
3. cópia exata da `.gitattributes` candidata;
4. commit **somente no clone temporário**, com a política como única alteração;
5. configuração `core.autocrlf=true` e `core.longpaths=true` apenas no clone;
6. checkout forçado do commit temporário;
7. comparação de tamanho e SHA-256 contra o baseline original.

Commit temporário do clone: `ab7ad18d5834385baa95e35728a6718f9b64b4a6`.

Parent confirmado: `c4462fffd3e532975fc4ad7a748b4d9b12a795b5`.

O SHA-256 da `.gitattributes` no clone é igual ao original candidato. O clone ficou sem mudança rastreada.

### Resultados do clone

| Grupo | Idênticos |
|---|---:|
| V2 versionada | **1.132/1.132** |
| 781 anteriormente expostos | **781/781** |
| protected545 versionados | **29/29** |
| ENRIQUECIDO_V1 | **7/7** |
| scripts mantidos | **18/18** |
| congelados V2 | **281/281** |

Distribuição materializada no clone:

- 764 arquivos `i/lf`, `w/lf`, `attr/-text`;
- 349 arquivos `i/lf`, `w/crlf`, `attr/text eol=crlf`;
- 17 arquivos `i/lf`, `w/lf`, `attr/text eol=lf`;
- dois binários `i/-text`, `w/-text`, `attr/-text`.

Divergências de tamanho ou SHA-256: **zero**.

O arquivo confidencial não rastreado `BUSCA_118.json` não apareceu no clone.

## Protected545, ENRIQUECIDO_V1 e IDX

O verificador constitucional somente leitura terminou em `PASSA`:

- protected545: **545/545**;
- IDX: **130/130**, política `IDX_SNAPSHOT_APENAS`;
- congelados V2: **281/281**;
- firmware: idêntico;
- catálogo 69: idêntico;
- ENRIQUECIDO_V1: idêntico;
- Engine executada: não;
- SD tocado: não.

Os 516 protected545 fora do Git não participaram do clone, conforme o escopo. Permanecem nos paths originais e sob custódia do snapshot. Os 130 IDX, contidos nesse conjunto, não foram copiados para o Git, modificados ou regenerados.

## Scripts

Os 18 scripts mantidos conservaram os hashes. Os 17 que já estavam em LF foram materializados em LF. `gerar_relatorios.py`, atualmente CRLF, foi materializado em CRLF pela exceção explícita. Nenhum script foi corrigido ou executado.

## Ocorrências e limitações do teste

1. Uma primeira tentativa com clone local/hardlinks falhou antes do checkout por permissão de hardlink. Diretório parcial: `C:\Users\arthu\AppData\Local\Temp\lex-byte-policy-0b-476943df8858458ea6385b2c009689f2`.
2. O clone com `--no-hardlinks` foi criado corretamente. O primeiro checkout encontrou quatro paths longos do updater; após `core.longpaths=true` no clone, o checkout completo passou. Essa configuração não foi alterada no repositório original.
3. O teste prova a materialização Git dos arquivos versionados. A custódia dos 516 snapshot-only continua dependendo do snapshot, não de `.gitattributes`.
4. A política ainda é untracked e não protege outros clones até ser revisada e consolidada numa Etapa 0C autorizada.

## Arquivos criados na Etapa 0B

- `.gitattributes`;
- `CLEANUP_AUDIT/BYTE_POLICY_0B_BASELINE.json`;
- `CLEANUP_AUDIT/BYTE_POLICY_0B_TEST.md`.

Todos permanecem untracked. `CLEANUP_AUDIT/BYTE_POLICY_PROPOSAL.md` já existia ao iniciar a 0B e também permanece untracked.

Próximo passo: revisão humana dos três artefatos da 0B. Não iniciar consolidação, staging, commit ou tag sem autorização da Etapa 0C.

ETAPA_0B_APROVADA — AGUARDANDO_CONSOLIDACAO_0C
