# Política de preservação de bytes do LEX MACHINA

Status: **política validada nas Etapas 0A/0B e consolidada na Etapa 0C**.

Esta política precede qualquer Artifact Registry ou Migração A. Ela define como o Git deve materializar os artefatos atuais sem alterar os bytes usados pelas provas de integridade.

## Problema original

O ambiente Windows usa `core.autocrlf=true`, `core.eol` não configurado e não possuía `.gitattributes`. Nesse estado, o Git pode guardar LF no blob e materializar CRLF no checkout sem considerar isso uma mudança lógica.

A V2 tinha 1.132 arquivos versionados:

| Estado anterior | Arquivos |
|---|---:|
| LF no índice e no working tree, sem atributo | **781** |
| LF no índice e CRLF no working tree, sem atributo | 349 |
| binários | 2 |

Assim, 781 arquivos em LF podiam sair em CRLF num clone Windows novo. Isso mudaria tamanho e SHA-256 de freezes, manifests, fontes, resultados e outputs sem alteração semântica aparente. Um checkout Git ainda não podia ser tratado como restauração byte-preservante.

## Classes funcionais

### BYTE_IMMUTABLE

Os bytes integram a identidade, prova, proveniência ou release. A classe prevalece sobre a extensão:

- os 281 arquivos do freeze V2, inclusive código e documentação incluídos no manifest;
- os sete arquivos de ENRIQUECIDO_V1;
- 826 entradas, capturas, triagens, dossiers, decisões, relatórios, manifests e outputs da expansão;
- os 29 membros versionados do protected545;
- os 130 IDX snapshot-only;
- demais artefatos binários protegidos pelas regras exatas.

Na V2 são 1.114 BYTE_IMMUTABLE: 764 textos LF, 348 textos CRLF e dois binários.

### TEXT_CANONICAL_LF

Somente os 18 scripts mantidos da expansão recebem política textual de código. Dezessete já são LF. `gerar_relatorios.py` continua temporariamente CRLF para preservar seus bytes atuais; convertê-lo é uma mudança separada e não faz parte desta política.

Código incluído no freeze de 281 arquivos permanece BYTE_IMMUTABLE. Uma regra por extensão não pode superar um freeze.

### CRLF preservado

Os 349 arquivos V2 atuais em CRLF são reproduzidos por 85 padrões explícitos `text eol=crlf`. Os padrões foram derivados dos paths existentes e validados antes da implementação: todos existem, são versionados e contêm CRLF puro. Diretórios só foram compactados em um padrão quando todos os descendentes rastreados compartilhavam a mesma condição.

CRLF aqui é um requisito de reprodução dos bytes atuais, não uma convenção variável da plataforma.

### SNAPSHOT_ONLY

Os 516 membros do protected545 fora do Git continuam sob custódia do snapshot da Onda 0. `.gitattributes` não os restaura e não substitui o snapshot.

## Política final de `.gitattributes`

A política versionada segue esta precedência:

1. `LEX_MACHINA_REFERENCIAS_V2/** -text` preserva a V2 por padrão;
2. cinco padrões restritos aplicam `text eol=lf` aos scripts mantidos da expansão;
3. 85 regras posteriores aplicam `text eol=crlf` aos 349 paths V2 atuais em CRLF;
4. seis protected545 versionados CRLF recebem `text eol=crlf`;
5. os outros 23 protected545 versionados recebem `-text`;
6. `*.IDX -text` e `*.idx -text` protegem prospectivamente qualquer IDX que venha a ser versionado;
7. `.gitattributes text eol=lf` fixa o próprio arquivo de política.

Não existe wildcard global `* text=auto`, regra global de normalização ou `git add --renormalize`. As exceções posteriores são deliberadas porque o blob dos arquivos CRLF já está em LF; aplicar apenas `-text` faria um clone materializar o byte errado.

## Protected545

O protected545 contém 545 entradas com path, tamanho e SHA-256. A prova exige bytes e path:

| Grupo | Resultado |
|---|---:|
| versionados | **29/29 preservados no clone** |
| snapshot-only | **516/516 intactos no repositório original** |
| total no verificador constitucional | **545/545** |

Entre os 29 versionados, 20 textos LF e três PNG usam `-text`; seis textos CRLF usam `text eol=crlf`. Os 516 não versionados não participaram do clone e continuam nos paths originais.

## IDX

Os 130 IDX são textuais, LF, byte-immutable e snapshot-only. Isso inclui os 12 chamados `NORMAS_BIN.IDX`: o nome indica a relação com artefatos binários, mas o IDX em si é textual.

Resultado: **130/130 intactos**. Nenhum foi adicionado ao Git, convertido ou regenerado. A regra `*.IDX -text` é proteção futura.

## ENRIQUECIDO_V1

O grupo contém o manifest e seis membros, todos LF e hash-sensitive. Resultado antes/depois e no clone: **7/7 idênticos**.

## Evidência das Etapas 0A/0B

O baseline registra SHA-256, tamanho, mtime e EOL de 1.677 arquivos únicos. Após aplicar a política:

- 1.677/1.677 mantiveram tamanho e SHA-256;
- nenhuma das 1.677 entradas mudou mtime;
- V2: **1.132/1.132** no clone externo;
- anteriormente vulneráveis: **781/781**;
- congelados V2: **281/281**;
- protected545 versionados: **29/29**;
- ENRIQUECIDO_V1: **7/7**;
- scripts mantidos: **18/18**;
- IDX no original: **130/130**;
- divergências: **zero**.

O clone externo recebeu a política candidata num commit temporário cujo parent era o HEAD testado. Ele usou `core.autocrlf=true`, materializou a árvore e ficou sem mudança rastreada. A distribuição V2 resultante foi:

- 764 arquivos LF com `-text`;
- 349 arquivos CRLF com `text eol=crlf`;
- 17 scripts LF com `text eol=lf`;
- dois binários com `-text`.

Não houve renormalização, checkout forçado no repositório original, execução da Engine, alteração de firmware, geração de IDX ou acesso ao SD.

## Long paths no Windows

`core.longpaths=true` foi necessário **somente no clone temporário**. Nenhuma configuração global ou do repositório original foi alterada.

O requisito depende do tamanho da raiz de destino:

- em `C:\GitHub\LEX-MACHINA`, nenhum path versionado ultrapassa 259 caracteres; o máximo observado é 211;
- no clone temporário sob uma raiz mais longa, quatro paths atingiram 261–275 caracteres e o checkout falhou até habilitar `core.longpaths=true` localmente.

Portanto, não há um path relativo que falhe em toda instalação Windows. Há paths suficientemente longos para ultrapassar o limite comum quando o repositório é clonado sob uma raiz extensa. Isso é requisito do ambiente de desenvolvimento/restauração, não motivo para reorganizar o legado nesta etapa.

Futuros scripts de clone/restauração devem:

1. calcular `len(destino absoluto + separador + path relativo)` antes do checkout;
2. detectar qualquer resultado acima do limite suportado pelo ambiente;
3. configurar `core.longpaths=true` somente no clone quando disponível, ou exigir uma raiz de destino mais curta;
4. abortar com erro claro antes de um checkout parcial quando nenhuma opção for possível;
5. nunca alterar `core.longpaths` global silenciosamente.

## Rollback

Antes da consolidação, o rollback é remover apenas os artefatos novos não rastreados. Depois do commit, usar um `git revert` dedicado do commit da política; não usar renormalização nem regravar arquivos funcionais.

O rollback deve confirmar que:

- os arquivos funcionais continuam com os mesmos SHA-256;
- nenhum IDX ou snapshot-only foi tocado;
- o índice contém somente a reversão documental/política;
- a remoção da política reabre conscientemente o risco de checkout não byte-preservante.

Não usar `git reset --hard` como procedimento de rollback desta política.

## Limitações

- A política garante os conjuntos e paths validados; novos artefatos precisam de classificação antes de serem adicionados.
- Os 516 snapshot-only dependem do snapshot, não do Git.
- Os blobs Git dos atuais arquivos CRLF continuam normalizados em LF; `text eol=crlf` garante a materialização. Migrá-los para blobs CRLF com `-text` seria outra mudança.
- O script `gerar_relatorios.py` permanece CRLF apesar de pertencer à classe de código canônico; conversão futura exige autorização e novos hashes.
- Ambientes Windows com raiz longa precisam de `core.longpaths=true` local ou destino mais curto.
- A política não cria Artifact Registry, Dataset Lock, Release Manifest ou Relocation Ledger.

## Critérios para avançar à Migração A

A Migração A só pode começar quando:

1. `.gitattributes` e os documentos 0A/0B/0C estiverem versionados num commit dedicado;
2. a tag local de checkpoint estiver criada;
3. o clone com `core.autocrlf=true` continuar reproduzindo 1.132/1.132 V2 e 781/781 anteriormente expostos;
4. protected545 estiver 545/545, IDX 130/130, V2 congelada 281/281 e ENRIQUECIDO_V1 7/7;
5. firmware e catálogo 69 permanecerem idênticos;
6. o working tree funcional e o staging não contiverem renormalização;
7. os requisitos de long paths forem detectados pelo ambiente;
8. houver autorização explícita para iniciar a Migração A.

Esta consolidação não autoriza nem inicia a Migração A.
