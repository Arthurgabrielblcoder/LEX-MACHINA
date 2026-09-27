# Etapa 0A — proposta de preservação de bytes

Status: **somente diagnóstico e proposta**. Nenhuma regra foi aplicada. Não houve conversão de EOL, staging, commit, tag, clone, execução da Engine ou alteração funcional.

Base examinada: `c4462fffd3e532975fc4ad7a748b4d9b12a795b5` (`pre-legacy-decoupling-2026-09-27`). A análise reutilizou os manifests e a auditoria existentes; não repetiu a auditoria das 81 pastas nem recalculou duplicatas.

## 1. Configuração encontrada

| Item | Resultado |
|---|---|
| `core.autocrlf` | `true`, vindo de `C:/Program Files/Git/etc/gitconfig` |
| `core.eol` | não configurado |
| `core.safecrlf` | não configurado |
| `core.attributesFile` | não configurado |
| `.gitattributes` | inexistente em todo o working tree |
| atributos nos exemplos críticos | `text`, `eol`, `binary` e `working-tree-encoding`: `unspecified` |
| estado inicial | 88 entradas não rastreadas preexistentes; zero mudança rastreada e índice vazio |

Com `core.autocrlf=true`, atributo não especificado e conteúdo reconhecido como texto, o Git guarda LF no blob e materializa CRLF no checkout Windows. Por isso, o blob e o arquivo de trabalho podem representar sequências de bytes diferentes sem aparecer como mudança lógica no Git.

## 2. Confirmação dos 781 arquivos

**Confirmado: 781.** `git ls-files --eol` encontrou 1.132 arquivos rastreados na V2:

| Estado do índice / working tree | Arquivos |
|---|---:|
| `i/lf`, `w/lf`, sem atributo | **781** |
| `i/lf`, `w/crlf`, sem atributo | 349 |
| binários (`i/-text`, `w/-text`) | 2 |

Os 781 arquivos `w/lf` podem sair em CRLF num checkout Windows novo. A previsão foi confirmada sem checkout usando os filtros do próprio Git com `core.autocrlf=true`:

- `00_CHECKPOINTS/INTEGRITY_BEFORE.json`: 117.372 bytes e SHA-256 `a319f0...` em LF; a materialização prevista tem 120.106 bytes e SHA-256 `40d539...` em CRLF;
- `ENRIQUECIDO_V1/MANIFEST.json`: 1.044 bytes e SHA-256 `0312e5...` em LF; a materialização prevista tem 1.079 bytes e SHA-256 `2b7f79...` em CRLF;
- `05_COMPILADOR/r1d_support.py`: 4.701 bytes e SHA-256 `c1bd6f...` em LF; a materialização prevista tem 4.807 bytes e SHA-256 `b97428...` em CRLF.

Logo, um clone/checkout Git comum ainda não é restauração byte a byte da V2.

## 3. Classificação por função

### A — BYTE_IMMUTABLE

Um arquivo entra nesta classe porque seus bytes são prova, entrada congelada, captura, decisão, output, artefato de release ou membro de manifest. A extensão não decide a classe.

1. **281 arquivos congelados da V2** listados por `09_CATALOGO_EXPANSAO_200/08_MANIFEST/INTEGRIDADE_ANTES.json`. O grupo contém JSON, Markdown, Python e GZip. Há 198 em LF, 81 em CRLF e dois binários.
2. **Sete arquivos de ENRIQUECIDO_V1**: o manifest e seus seis membros. Todos estão em LF e os seis membros são ligados por `path`, `bytes` e `sha256`.
3. **Demais 826 artefatos textuais da expansão**, por função conservadora: entradas, identidades, triagens/TSV, capturas em `03_FONTES`, dossiers, rejeitadas, decisões, relatórios, manifests e outputs de catálogo. Eles não devem ter EOL alterado enquanto sua cadeia de proveniência não for refeita e aprovada.
4. **29 membros versionados do protected545**, todos byte e path sensitive: 20 em LF, seis em CRLF e três PNG.
5. **130 IDX fora do Git**, todos protegidos pelo snapshot e pelo protected545.

Na V2, isso resulta em **1.114 BYTE_IMMUTABLE** e 18 scripts de expansão classificados abaixo. Entre os 1.114 há 764 textos LF, 348 textos CRLF e dois binários.

### B — TEXT_CANONICAL_LF

Os **18 scripts Python mantidos da expansão** são código, não captura/output. A política desejável é UTF-8/LF. Dezessete já estão em LF. `06_RELATORIOS/gerar_relatorios.py` está em CRLF; na política mínima de preservação ele deve continuar CRLF por exceção, pois convertê-lo agora violaria o objetivo desta etapa. A conversão para LF exigiria uma mudança funcional/documental separada, com diff explícito.

Código presente entre os 281 congelados continua BYTE_IMMUTABLE: ser `.py` não supera o freeze que inclui seu SHA-256.

### C — PLATFORM_SPECIFIC

Nenhum arquivo relevante exige EOL nativo ou variável por plataforma. Os 349 CRLF existentes devem ser reproduzidos como CRLF porque esse é o estado byte a byte atual, não porque precisem acompanhar o sistema operacional.

### D — SNAPSHOT_ONLY

Há **516 membros do protected545 fora do Git**, protegidos pelo snapshot da Onda 0. Os 130 IDX estão dentro desse grupo de 516. `.gitattributes` não os protege enquanto continuarem fora do índice; a restauração deles depende do snapshot e dos hashes existentes.

## 4. Protected545

O manifest contém 545 entradas com `path`, `bytes` e `sha256`; o verificador lê exatamente `ROOT.parent / path`. Portanto, todos dependem dos bytes e do path.

| Situação | Quantidade |
|---|---:|
| versionados | 29 |
| fora do Git | 516 |
| versionados LF sujeitos a CRLF em checkout novo | **20** |
| versionados CRLF que hoje dependem do smudge do Git | 6 |
| versionados binários | 3 |
| IDX dentro do protected545 | 130 |

Os 20 LF versionados seriam corrompidos para a prova por um checkout novo sem atributos. Os seis CRLF são hoje reconstituídos a partir de blobs LF pelo `autocrlf`; marcar esses seis simplesmente como `-text` faria um clone produzir LF e também quebraria a prova. Eles exigem `text eol=crlf` na política mínima, ou uma futura migração explícita do blob para CRLF bruto.

## 5. V2 e ENRIQUECIDO_V1

- A base V2 anterior à expansão coincide com os 281 arquivos do freeze: todos são BYTE_IMMUTABLE, inclusive os 48 `.py` e os documentos de configuração ali incluídos.
- A expansão tem 851 arquivos rastreados: 18 scripts mantidos e 833 artefatos de dados/evidência/output.
- `INTEGRITY_BEFORE.json` está em LF, não tem atributo e muda de SHA-256 na materialização prevista em CRLF.
- ENRIQUECIDO_V1 tem sete arquivos em LF. O manifest tem SHA-256 próprio usado pelo verificador, e seus seis membros são conferidos pelos hashes internos. Todos os sete divergiriam num checkout Windows novo sem atributos.
- `INTEGRIDADE_ANTES.json` está atualmente em CRLF, embora o blob esteja em LF. A regra mínima precisa pedir CRLF explicitamente; `-text` isolado produziria o byte errado num clone.

## 6. IDX

Os 130 IDX estão fora do Git, em LF e no snapshot. A inspeção de assinatura e bytes mostrou que **todos os 130 são textuais**, inclusive os 12 arquivos chamados `NORMAS_BIN.IDX`; esses arquivos começam com `#LEXMACHINA|NORMAS_BIN|1` e não contêm payload binário. Portanto:

- classificação funcional: **TEXTUAL_BYTE_IMMUTABLE + SNAPSHOT_ONLY**;
- binários entre os 130 IDX: **zero**;
- risco Git atual: nenhum, pois não são rastreados;
- risco futuro: alto se forem adicionados sem `-text`, porque offsets, tamanhos e hashes dependem dos bytes LF.

O nome `NORMAS_BIN.IDX` descreve um índice para artefatos binários; não torna o próprio IDX binário.

## 7. Política mínima proposta para `.gitattributes`

Esta é uma proposta para a Etapa 0B, não um arquivo pronto ou aplicado. A ordem é parte da política: regras posteriores vencem.

```gitattributes
# 1. Preservar por padrão todos os bytes atualmente rastreados da V2.
LEX_MACHINA_REFERENCIAS_V2/** -text

# 2. Código mantido da expansão que já está LF.
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/02_TRIAGEM/*.py text eol=lf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/03_FONTES/*.py text eol=lf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/*.py text eol=lf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/*.py text eol=lf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/08_MANIFEST/*.py text eol=lf

# 3. Exceção atual: este script ainda é CRLF; preservar bytes em 0B.
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/gerar_relatorios.py text eol=crlf

# 4. Se algum IDX vier a ser versionado, seus bytes nunca são normalizados.
*.IDX -text
*.idx -text

# 5. O próprio arquivo de política deve ser LF.
.gitattributes text eol=lf
```

O bloco acima precisa ser acompanhado pelas exceções CRLF exatas do Apêndice A e pelas regras protected545 do Apêndice B. Não usar `* text=auto`: com `core.autocrlf=true`, isso não preserva os 781 LF. Também não usar `git add --renormalize .`.

### Por que `-text` e `text eol=crlf` coexistem

- Para LF e binários byte-immutable cujo blob já contém os bytes corretos, `-text` impede transformação.
- Para os arquivos atuais CRLF, o blob Git já está normalizado em LF. `text eol=crlf` reproduz os bytes atuais sem reescrever o arquivo de trabalho ou o blob nesta etapa.
- Uma política futura mais forte poderia armazenar CRLF bruto com `-text`, mas isso exigiria adicionar novamente esses arquivos, mudaria blobs e produziria um commit grande. Não pertence à 0A nem deve ser confundida com simples proteção de atributo.

## 8. Impacto previsto

Com a política completa proposta e as exceções exatas:

- **1.132 arquivos V2** ficam com materialização determinística igual aos bytes atuais;
- 1.114 são tratados como BYTE_IMMUTABLE e 18 como código mantido, com uma exceção CRLF transitória;
- os 29 protected545 versionados recebem regra compatível com seus bytes atuais;
- os 516 protected545 não versionados permanecem sob snapshot, sem mudança;
- os 130 IDX recebem proteção apenas caso venham a ser adicionados no futuro;
- nenhum byte do working tree deve mudar; somente `.gitattributes` deverá aparecer como arquivo novo numa 0B corretamente executada.

Uma implementação ingênua teria impactos diferentes:

| Implementação ingênua | Impacto previsto |
|---|---|
| nenhuma regra / `* text=auto` | 781 arquivos V2 LF podem sair CRLF em novo checkout |
| `LEX_MACHINA_REFERENCIAS_V2/** text eol=lf` | checkout novo converteria 349 CRLF para LF; 348 são BYTE_IMMUTABLE |
| `LEX_MACHINA_REFERENCIAS_V2/** -text` sem exceções | checkout novo usaria os blobs LF para os 349 atuais CRLF |
| `-text` para todos os 317 arquivos já comprovados por manifests/protected | 87 arquivos CRLF apareceriam modificados contra seus blobs LF e seriam candidatos a staging acidental |
| `git add --renormalize .` | escopo amplo e difícil de revisar; pode stagear mudanças de representação em áreas não autorizadas |

“Proteger atributo futuro” significa declarar como cada path deve ser materializado, mantendo os bytes atuais. “Alterar bytes existentes” significa converter LF/CRLF ou regravar blobs; isso não está autorizado.

## 9. Riscos

1. A ordem das regras pode fazer um padrão amplo superar uma exceção byte-immutable.
2. `-text` em um arquivo hoje CRLF, sem gravar CRLF bruto no blob, produz LF num clone.
3. `text eol=lf` aplicado por extensão a JSON/Markdown inclui freezes, capturas e outputs cujos hashes dependem dos bytes.
4. Arquivos snapshot-only continuam fora da proteção de atributos.
5. Editores podem regravar EOL antes do primeiro hash da 0B; por isso os hashes devem ser capturados antes de criar `.gitattributes`.
6. Renormalização ampla pode esconder no mesmo staging uma mudança de política e centenas de mudanças de blob.
7. Uma regra que passe no working tree atual ainda pode falhar em clone; o clone externo é o gate decisivo.

## 10. Teste proposto para a Etapa 0B

Executar somente após aprovação humana desta proposta:

1. Confirmar o mesmo HEAD, índice vazio e ausência de mudança rastreada.
2. Registrar SHA-256 e tamanho de todos os 1.132 arquivos V2, dos 545 protected545 e dos 130 IDX antes de qualquer escrita.
3. Criar apenas `.gitattributes` com o bloco mínimo, os 85 padrões CRLF do Apêndice A e as 29 regras do Apêndice B.
4. Sem checkout forçado e sem renormalização, confirmar que nenhum arquivo preexistente mudou bytes, tamanho ou mtime; `git status --short --untracked-files=no` deve mostrar apenas `.gitattributes` se ele estiver rastreado/staged na missão autorizada.
5. Rodar `git check-attr text eol binary` em amostras e em toda a allowlist; conferir as contagens finais por classe.
6. Criar clone limpo em diretório externo, a partir do commit de teste que contenha apenas a política aprovada, configurando `core.autocrlf=true` antes do checkout validado.
7. Comparar SHA-256 do clone contra a fotografia do passo 2 para todos os 1.132 arquivos V2 e os 29 protected545 versionados. Qualquer divergência aborta.
8. Restaurar/copiar para uma área externa de teste, sem tocar o repositório, os 516 protected545 snapshot-only e os 130 IDX; verificar hashes e paths contra os manifests.
9. Executar somente os verificadores de integridade já autorizados, sem Engine/pipeline: protected545 545/545, freeze V2 281/281, ENRIQUECIDO_V1 e IDX 130/130.
10. Confirmar que o clone não contém secretamente arquivos excluídos como `BUSCA_118.json` e que o snapshot continua sendo a fonte desses bytes.
11. Se qualquer hash, path, atributo ou status divergir, descartar o clone de teste e não fazer commit/tag da política.

Condição para implementação: aprovação humana dos grupos, das 85 exceções CRLF, das 29 regras protected545 e do tratamento transitório do único script de expansão CRLF. A Etapa 0B deve continuar separada da criação do Artifact Registry.

## Apêndice A — padrões CRLF exatos para a V2

Estes 85 padrões cobrem exatamente os 349 arquivos V2 atualmente CRLF; diretórios só são usados quando todos os descendentes rastreados estão em CRLF. Eles devem vir depois da regra `V2/** -text` e das regras LF de código.

```gitattributes
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/DETERMINISMO_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/INTEGRITY_R1D1_FINAL.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/INTEGRITY_R1D_FINAL.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_FINAL_ARTIFACT_MANIFEST.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_FINAL_VERIFICATION.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_FULL_RUN1_COMPLETE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_FULL_RUN1_STARTED.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_FULL_RUN2_COMPLETE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_FULL_RUN2_STARTED.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_FULL_STRUCTURAL_AUDIT.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_GATE_DECISION.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_INPUT_FREEZE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_INTEGRITY_BEFORE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_PROOFS_FREEZE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_PROOF_PASS_STARTED.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_REGRESSION_COMPLETE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D1_REGRESSION_STARTED.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D_ADJUDICADA_FREEZE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D_CURATION_COMPLETE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D_FINAL_ARTIFACT_MANIFEST.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D_GATE_DECISION.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D_INTEGRITY_BEFORE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D_REGRESSION_COMPLETE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/R1D_REGRESSION_STARTED.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/RC2_HUMAN_REVIEW_INTEGRITY_BEFORE.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/RESUME_STATE_R1D.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/RESUME_STATE_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/TEST_RESULTS_R1D.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/TEST_RESULTS_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1D.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/01_SCHEMA/POLITICA_EDITORIAL_REFERENCIAS_V2_V1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/01_SCHEMA/POLITICA_EDITORIAL_REFERENCIAS_V2_V1.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/02_DISPOSITIVOS/PATCH_ART205_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/03_OBRAS/CURADORIA_EDITORIAL_R1D.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/ADJUDICACAO_HUMANA_R1C_V1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/ADJUDICACAO_HUMANA_R1C_V1.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/CONTRATOS_ADICIONAIS_14_POS_POLITICA.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/CONTRATOS_ADICIONAIS_14_POS_POLITICA.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/IMPACTO_ART205_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/IMPACTO_ART205_R1D1.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/OITO_LACUNAS_TECNICAS_R1D.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/OITO_LACUNAS_TECNICAS_R1D.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/PROVAS_EXPANSAO_R1D.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/PROVAS_EXPANSAO_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/SIMULACAO_ART205_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/SIMULACAO_ART205_R1D1.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/SIMULACAO_GARANTIA_DEPENDENTE_V1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/06_BENCHMARKS/SIMULACAO_GARANTIA_DEPENDENTE_V1.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/07_EXECUCAO_COMPLETA/METRICAS_COMPLETAS_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/07_EXECUCAO_COMPLETA/R1D1_RUN1_ADMISSIVEIS.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/07_EXECUCAO_COMPLETA/R1D1_RUN1_REVISAO.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/07_EXECUCAO_COMPLETA/R1D1_RUN1_SUMMARY.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/07_EXECUCAO_COMPLETA/R1D1_RUN2_ADMISSIVEIS.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/07_EXECUCAO_COMPLETA/R1D1_RUN2_REVISAO.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/07_EXECUCAO_COMPLETA/R1D1_RUN2_SUMMARY.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1/** text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/00_ENTRADA/** text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/02_TRIAGEM/CURADORIA_RETOMADA_06.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/02_TRIAGEM/CURADORIA_RETOMADA_08.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/03_FONTES/ENRIQUECIMENTO_V1/** text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/04_DOSSIERS/ENRIQUECIMENTO_V1/** text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/CHECKPOINTS_ENRIQUECIMENTO/** text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/BASELINE_ENRIQUECIMENTO_V1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/CHECKPOINT_ENRIQUECIMENTO.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/CORRECOES_DURANTE_ENRIQUECIMENTO.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/DECISAO_CYBERPUNK_REVISADA.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/DEDUPLICACAO_EVIDENCE_CARDS_V1.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/JOGOS_EXPANSAO.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/REDUNDANCIA_69_MAIS_200.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/RELATORIO_FINAL.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/REVISOES_ENRIQUECIMENTO_V1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/REVISOES_POS_CHECKPOINT.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/06_RELATORIOS/gerar_relatorios.py text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/08_MANIFEST/INTEGRIDADE_ANTES.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_RELATORIOS/COMPARACAO_ALPHA3_R1C_R1D_R1D1.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_RELATORIOS/COMPARACAO_ALPHA3_R1C_R1D_R1D1.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_RELATORIOS/CORRECAO_ART205_R1D1.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_RELATORIOS/RELATORIO_FINAL_R1D1.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_RELATORIOS/RELATORIO_R1D_ADJUDICADA.md text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_RELATORIOS/RESULTADO_FINAL_R1D.json text eol=crlf
LEX_MACHINA_REFERENCIAS_V2/09_RELATORIOS/RESULTADO_FINAL_R1D1.json text eol=crlf
```

## Apêndice B — regras exatas dos 29 protected545 versionados

```gitattributes
# Seis arquivos CRLF: preservar a materialização atual.
LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/AUDITORIA_ESQUEMAS_24_45.json text eol=crlf
LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_24_INPUT_ENGINE_V132_ADAPTADO.json text eol=crlf
LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_CANONICO.json text eol=crlf
LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_INPUT_ENGINE_V132.json text eol=crlf
LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/RASTREABILIDADE_ADAPTACAO_69.json text eol=crlf
LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/RELATORIO_ADAPTADOR_CATALOGO_69.md text eol=crlf

# Vinte textos LF e três PNG: bytes brutos.
LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/adaptar_catalogo_69.py -text
LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/test_adaptador_catalogo_69.py -text
"firmware/LEX MAQUINA INO 2/LEX_MACHINA_v7.10.1_FAST/LEIA_ME.txt" -text
"firmware/LEX MAQUINA INO 2/LEX_MACHINA_v7.10.1_FAST/LEX_MACHINA_v7.10.1_RELATIONS_V2_FAST/LEIA_ME.txt" -text
"firmware/LEX MAQUINA INO 2/LEX_MACHINA_v7.10.1_FAST/LEX_MACHINA_v7.10.1_RELATIONS_V2_FAST/LEX_MACHINA_v7.10.1_RELATIONS_V2_FAST.ino" -text
"firmware/LEX MAQUINA INO 2/LEX_MACHINA_v7.10.1_FAST/LEX_MACHINA_v7.10.1_RELATIONS_V2_FAST/assets/lex_boot_screen.h" -text
"firmware/LEX MAQUINA INO 2/LEX_MACHINA_v7.10.1_FAST/LEX_MACHINA_v7.10.1_RELATIONS_V2_FAST/assets/lex_boot_screen_preview.png" -text
"firmware/LEX MAQUINA INO 2/LEX_MACHINA_v7.10.1_FAST/LEX_MACHINA_v7.10.1_RELATIONS_V2_FAST/contexto_juridico.h" -text
firmware/LEX_MACHINA.ino/LEX_MACHINA.ino.ino -text
firmware/LEX_MACHINA.ino/assets/lex_boot_screen.h -text
firmware/LEX_MACHINA.ino/assets/lex_boot_screen_preview.png -text
firmware/LEX_MACHINA.ino/contexto_juridico.h -text
firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/CHECKLIST_FISICO.md -text
firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/LEIA_ME.txt -text
firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA.ino -text
firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/RELATORIO_J4_5.md -text
firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/assets/lex_boot_screen.h -text
firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/assets/lex_boot_screen_preview.png -text
firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/contexto_juridico.h -text
firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/test_capacidade_juris_v7120.py -text
firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/test_regressao_contexto_v7111.py -text
firmware/README.md -text
sdcard/README.md -text
```

ETAPA_0A_CONCLUIDA — AGUARDANDO_REVISAO
