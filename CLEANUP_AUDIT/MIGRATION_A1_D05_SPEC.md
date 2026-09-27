# Migração A1 — especificação do piloto do Artifact Registry para D05

Status: **ESPECIFICAÇÃO PARA REVISÃO**. Esta etapa não cria registry funcional, Dataset Lock, Release Manifest nem Relocation Ledger; não muda consumidores, seleção, dados ou saídas.

## 1. Definição exata de D05

D05 é o grupo de descoberta definido em `CLEANUP_AUDIT/WAVE2C_DECOUPLING_PLAN.md` como **“Selecionar lotes, capturas, overlays, checkpoints e catálogos da expansão”**. Sua raiz de referência é:

`LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200`

D05 não é a Engine, a V2 congelada nem o catálogo oficial de 69 obras. É o domínio de curadoria, relatórios e manifests da expansão de 200 candidatas, incluindo o pacote candidato `ENRIQUECIDO_V1`. Os catálogos produzidos mantêm `status_catalogo = CANDIDATO_NAO_INTEGRADO`; os próprios artefatos registram que a Engine não foi executada, vínculos jurídicos não foram gerados e a ontologia não foi mapeada.

O piloto deve representar dois planos sem confundi-los:

1. **cadeia de produto determinística**: lotes de triagem + dossiês + referência 69 → dois catálogos-base; catálogo-base + overlays + revisões + fila/checkpoint + referência 69 → pacote `ENRIQUECIDO_V1`;
2. **envelope de evidência e auditoria**: identidade, capturas, checkpoints, relatórios, baselines e manifests que explicam ou verificam a cadeia, mas não são todos entradas diretas dos compiladores.

## 2. Código envolvido

### Seletores dinâmicos classificados como D05 no plano aprovado

| Script | Seleção atual |
|---|---|
| `06_RELATORIOS/editorial_enriquecimento_v1.py` | capturas `03_FONTES/ENRIQUECIMENTO_V1/{candidate_number:03}_*.json`, ordenadas; escolhe a primeira captura consultada compatível |
| `06_RELATORIOS/enriquecer_v1.py` | `ROOT.rglob('*')` para o baseline histórico e `07_CATALOGO_CANDIDATO/CATALOGO_*.json` |
| `06_RELATORIOS/estado_retomada.py` | `01_IDENTIDADE/LOTE_*.json` e `02_TRIAGEM/LOTE_*.json`, ordenados |
| `06_RELATORIOS/gerar_relatorios.py` | catálogos `07_CATALOGO_CANDIDATO/CATALOGO_*.json` para conferir determinismo; o glob da pasta temporária é D10, não D05 |
| `06_RELATORIOS/relatorios_enriquecimento_v1.py` | `CP_*.json`, capturas de enriquecimento e overlays, todos ordenados antes do uso |
| `07_CATALOGO_CANDIDATO/compilar_enriquecido_v1.py` | presença de overlay pelo `work_id`; glob ordenado dos overlays para metadados e dos arquivos de saída para o manifesto interno |
| `08_MANIFEST/gerar_manifest.py` | árvore inteira por `ROOT.rglob('*')` e catálogos-base por `CATALOGO_*.json` |

### Produtores e verificadores do fluxo completo

- `02_TRIAGEM/editorial.py`, `from_table.py`, `lote01.py`, `lote02.py`, `lote_retomada.py`;
- `03_FONTES/collect_steam.py`;
- `06_RELATORIOS/amostra_auditoria.py`, `aplicar_saneamento_pre_enriquecimento.py`, `consultar_fontes_enriquecimento.py`, `editorial_enriquecimento_v1.py`, `enriquecer_v1.py`, `estado_retomada.py`, `estimar_enriquecimento.py`, `gerar_relatorios.py`, `relatorios_enriquecimento_v1.py`;
- `07_CATALOGO_CANDIDATO/compilar_catalogo.py`, `compilar_enriquecido_v1.py`;
- `08_MANIFEST/gerar_manifest.py`.

Os dois compiladores em `07_CATALOGO_CANDIDATO` são os únicos produtores da cadeia final que o piloto deve modelar como `generation_recipe` executável. Os demais scripts representam coleta, decisão editorial, reconstrução de estado ou prova.

## 3. Fluxo atual e paths exatos

### Entradas e evidências

| Papel | Path/conjunto | Por que entra |
|---|---|---|
| universo candidato | `00_ENTRADA/CANDIDATAS_200.json` | fixa as 200 candidatas e seus números/IDs |
| requisitos | `00_ENTRADA/REQUISITOS_EXPANSAO.md` | contrato editorial humano; não é entrada do compilador |
| referência 69 incorporada | `00_ENTRADA/REFERENCIA_CATALOGO_69.json` | contém 69 obras, path e SHA-256 declarado do catálogo canônico |
| catálogo 69 canônico | `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_CANONICO.json` | referência oficial externa ao diretório D05; SHA-256 declarado `58d742a2592f54eb309c3900871d77fc6253a1fb20f7571f1913755fd9797a77` |
| identidade | `01_IDENTIDADE/LOTE_01.json` … `LOTE_08.json` | oito lotes de identidade |
| triagem autoritativa | `02_TRIAGEM/LOTE_01.json` … `LOTE_08.json` | oito lotes de 25 registros; entrada direta do catálogo-base |
| material de curadoria | `02_TRIAGEM/CURADORIA_03.tsv`, `CURADORIA_04.tsv`, `CURADORIA_RETOMADA_05.json` … `08.json` | evidência/insumo histórico dos lotes; não lido pelo compilador final |
| capturas/fontes | `03_FONTES/` e `03_FONTES/ENRIQUECIMENTO_V1/` | prova de URL, tier, acesso, verificação e, quando existente, hash do snapshot |
| dossiês-base | `04_DOSSIERS/*.json` | 199 arquivos, selecionados exatamente pelo `work_id` de cada triagem utilizável |
| overlays | `04_DOSSIERS/ENRIQUECIMENTO_V1/*.json` | 111 decisões/adições; selecionadas por presença do path exato `<work_id>.json` |
| rejeições | `05_REJEITADAS/*.json` | evidência editorial; não é entrada direta dos compiladores |
| fila/checkpoint | `06_RELATORIOS/CHECKPOINT_ENRIQUECIMENTO.json` | fila de 111 obras, estado concluído e 12 checkpoints; entrada direta do enriquecido |
| checkpoints individuais | `06_RELATORIOS/CHECKPOINTS_ENRIQUECIMENTO/CP_01.json` … `CP_12.json` | reconstrução e prova da sequência de exame |
| revisões | `06_RELATORIOS/REVISOES_ENRIQUECIMENTO_V1.json` | três patches por `evidence_id`; entrada direta do enriquecido |
| baseline | `06_RELATORIOS/BASELINE_ENRIQUECIMENTO_V1.json` | fotografia histórica de 580 arquivos na abertura do enriquecimento, mais congelados/externos |

Há 128 registros em `03_FONTES/ENRIQUECIMENTO_V1`, 111 overlays e 12 checkpoints individuais. O relatório final registra nove fontes abertas por ferramenta web sem registro local de coleta; a confirmação existe como decisão de auditoria, não como snapshot local completo.

### Seleção e processamento

`compilar_catalogo.py` lê **exatamente** `LOTE_01..08`, exige 200 números únicos, ordena os registros por `work_id`, mantém apenas `APTA` e `APTA_COM_RESSALVA`, e abre um dossiê pelo path exato `<work_id>.json`. O resultado atual tem 199 obras e 221 evidence cards. A visão combinada ordena as 69 obras por `id` e acrescenta as 199 novas na ordem dos `work_id`.

`compilar_enriquecido_v1.py` ordena as 199 obras-base por `work_id`; para cada obra, usa no máximo um overlay no path exato `<work_id>.json`. Indexa revisões por `evidence_id` e a fila por `work_id`, rejeita duplicidade de `evidence_id`, exige que todas as três revisões sejam aplicadas e que o número de obras examinadas seja igual ao tamanho da fila. O resultado contém 221 cards-base + 71 novos = 292 cards.

Os seletores de relatórios usam globs ordenados. `editorial_enriquecimento_v1.py` preserva multiplicidade de capturas por candidata e escolhe a primeira captura com `verificacao == PAGINA_CONSULTADA` que também corresponda à URL quando ela é informada. Essa precedência precisa ser registrada; trocar uma lista ordenada por um conjunto altera o resultado.

### Saídas

Catálogos-base em `07_CATALOGO_CANDIDATO/`:

- `CATALOGO_EXPANSAO_200.json`: 199 obras, 221 cards, SHA-256 `5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43`;
- `CATALOGO_TOTAL_69_MAIS_APTAS.json`: 69 + 199 registros, SHA-256 `6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6`.

Pacote em `07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/`:

- `CATALOGO_EXPANSAO_ENRIQUECIDO_V1.json`;
- `CATALOGO_TOTAL_ENRIQUECIDO_V1.json`;
- `EVIDENCE_CARDS_ENRIQUECIDOS_V1.json`;
- `DECISOES_ENRIQUECIMENTO.json`;
- `METADADOS_ENRIQUECIDO_V1.json`;
- `README.md`;
- `MANIFEST.json`.

O manifesto interno lista seis payloads com path, tamanho e SHA-256. Seu próprio SHA-256 é `0312e5f091981f8065673529aca04437ed0fc7ecaac26cd144d2af26ab37774c`.

### Manifests e provas

- `06_RELATORIOS/DETERMINISMO_COMPILACAO.json`: duas recompilações do catálogo-base iguais entre si e aos arquivos locais (`identicos: true`);
- `06_RELATORIOS/RELATORIO_ENRIQUECIMENTO_V1.md`: três compilações do pacote enriquecido idênticas byte a byte e hashes dos sete arquivos;
- `07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/METADADOS_ENRIQUECIDO_V1.json`: hashes do catálogo-base, checkpoint, revisões e 111 overlays;
- `07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/MANIFEST.json`: hashes/tamanhos dos seis payloads;
- `08_MANIFEST/INTEGRIDADE_ANTES.json` e `INTEGRIDADE_DEPOIS.json`: congelados V2, catálogo 69 e proteções históricas;
- `08_MANIFEST/MANIFEST.json`: 852 membros e hashes da fotografia final da expansão, além dos hashes dos dois catálogos-base.

## 4. Ordem, multiplicidade e dependência de path

| Conjunto | Ordem/multiplicidade | Dependência material |
|---|---|---|
| triagem | oito lotes fixos; 25 registros cada; 200 números únicos | números e `work_id`; o compilador usa paths exatos e ordena por `work_id` |
| dossiês-base | exatamente um por obra utilizável | filename `<work_id>.json`, conteúdo e hash |
| referência 69 | 69 entradas ordenadas por `id` na compilação | conteúdo/hash; o path absoluto armazenado é localização histórica, não identidade |
| capturas de enriquecimento | zero ou várias por candidata; 128 no total | ordem lexicográfica e precedência da primeira captura consultada compatível |
| overlays | zero ou um por obra-base; 111 no total | path `<work_id>.json`, conteúdo/hash; ausência tem semântica |
| fila | 111 `work_id`; tratada como mapa na compilação, mas sua ordem histórica explica os checkpoints | associação e cardinalidade |
| checkpoints | CP_01..12 ordenados pelo campo `numero` | multiplicidade e associação candidato→checkpoint |
| revisões | três, identificadas por `evidence_id` | identidade, conteúdo e aplicação exatamente uma vez |
| outputs | ordem interna definida pelos compiladores; seis payloads ordenados por nome no manifesto | bytes e hash |

O registry descreve os artefatos e suas ocorrências. A ordem autorizada de consumo pertence ao futuro Dataset Lock. Até esse lock existir, o fragmento D05 deve registrar `observed_order` apenas como evidência do legado, sem ativar seleção.

## 5. Unidade e estrutura propostas

Estrutura fragmentada proposta para A2:

```text
ARTIFACT_REGISTRY/
  index.json
  datasets/
    d05_catalogo_expansao_200.json
  schemas/
    index.schema.json
    dataset.schema.json
  verify_registry.py
```

O índice só localiza e autentica fragmentos. O fragmento D05 descreve o dataset, suas raízes, artefatos, relações e invariantes. A fragmentação futura por norma ou camada pode adicionar outros arquivos em `datasets/` sem ampliar este fragmento nem criar um registry monolítico.

### Índice raiz mínimo

```json
{
  "canonicalization": "json-utf8-lf-sorted-keys-indent-2-final-lf-v1",
  "fragments": [
    {
      "dataset_id": "d05.catalogo-expansao-200",
      "path": "datasets/d05_catalogo_expansao_200.json",
      "sha256": "<hash-dos-bytes-canônicos>",
      "size": 0
    }
  ],
  "registry_id": "lex-machina-artifact-registry",
  "schema_version": 1
}
```

### Fragmento de dataset

Campos de topo: `schema_version`, `dataset_id`, `dataset_version`, `description`, `mode` (`SHADOW`), `authority` (`LEGACY_PIPELINE`), `storage_roots`, `managed_roots`, `artifacts`, `relations`, `observed_selection`, `invariants`, `golden_references` e `known_gaps`.

Cada elemento de `artifacts` terá:

- `logical_id` e `version`;
- `occurrence_id`;
- `artifact_role`;
- `storage_root_id` e `relative_path`;
- `sha256`, `size`, `canonical_hash_algo` (`SHA-256`);
- `byte_policy` (`BYTE_EXACT`, salvo justificativa expressa);
- `media_type`;
- `created_by_run_id` quando já houver evidência, senão `null`;
- `reproducibility`: `PROVEN`, `UNPROVEN` ou `NOT_APPLICABLE`, mais `evidence_refs`;
- `access_class` (`repository`, `restricted_local` ou outra classe já justificada pela evidência);
- `supersedes` como lista, vazia quando não documentado;
- `provenance` como referências a evidências existentes;
- `generation_recipe` somente quando o produtor e todas as entradas estão documentados;
- `lifecycle_state` descritivo e imutável para a versão, por exemplo `FROZEN_EVIDENCE`, `CANDIDATE_OUTPUT` ou `HISTORICAL_RECORD`.

Não haverá campo `active` ou equivalente. Ativação e ordem consumível serão responsabilidade do Dataset Lock.

## 6. Regras de identidade, ocorrência e localização

1. `(logical_id, version)` identifica uma versão lógica e deve ser única no registry inteiro.
2. A mesma dupla com `sha256` ou `size` distintos é erro fatal.
3. `(sha256, size)` identifica bytes; iguais podem aparecer em várias ocorrências.
4. `occurrence_id` identifica uma ocorrência física/histórica; não é derivado apenas do path nem do hash e não pode apontar para dois hashes.
5. O mesmo hash em papéis diferentes permanece em registros distintos; igualdade de bytes não deduplica função, proveniência ou ciclo de vida.
6. `(storage_root_id, relative_path)` localiza a ocorrência e não define sua identidade lógica.
7. Paths usam `/`, são relativos, NFC, sem drive, UNC, `..`, segmento vazio ou resolução fora da raiz.
8. Duplicidade de path e colisão de path sob `NFC + casefold` são erros fatais, mesmo em sistema case-sensitive.
9. IDs de candidato, `work_id`, `evidence_id`, número de checkpoint e ordem observada ficam em `provenance`/`relations`, não são inferidos do basename pelo verificador.
10. `supersedes` exige alvo existente e não significa ativação.

## 7. Serialização canônica

- JSON UTF-8 sem BOM;
- LF; exatamente um LF final;
- chaves de objetos em ordem lexicográfica;
- indentação de dois espaços;
- números inteiros; floats proibidos no piloto;
- nenhum valor `NaN`/infinito;
- ordem de arrays definida pelo schema: fragmentos por `dataset_id`, raízes por `storage_root_id`, artefatos por `occurrence_id`, relações por `relation_id`; arrays semanticamente ordenados, como `observed_order`, não são reordenados;
- o SHA-256 do fragmento é calculado sobre os bytes canônicos completos do fragmento;
- `index.json` armazena path relativo, tamanho e SHA-256 do fragmento. O índice não armazena o próprio hash.

## 8. Proveniência existente e lacunas

**Evidência existente:** URLs, tiers, datas de acesso, estado de verificação e alguns `snapshot_sha256` nas capturas; `fontes` e `provenance` nos dossiês; decisões, justificativas e rejeições nos overlays; associação a 12 checkpoints; três revisões humanas por `evidence_id`; hash declarado do catálogo 69; baseline histórico; hashes dos dois catálogos-base; hashes de entradas e outputs do pacote enriquecido; manifests de integridade e relatório de determinismo.

**Campo desejável ainda ausente ou incompleto:** `created_by_run_id` uniforme; identidade estável do agente/revisor; recibo local para nove consultas feitas via ferramenta web; receita reproduzível de coleta remota; licença/classificação de acesso uniforme; relação formal entre cada captura e cada card; versão lógica explícita para todo registro histórico.

O piloto deve usar `null`, lista vazia ou `UNPROVEN` para lacunas. Não deve fabricar proveniência retroativa.

## 9. Reprodutibilidade

| Tipo | Classe | Base da classificação |
|---|---|---|
| dois catálogos-base | `PROVEN` | duas recompilações iguais e iguais aos arquivos locais em `DETERMINISMO_COMPILACAO.json` |
| sete arquivos do pacote `ENRIQUECIDO_V1` | `PROVEN` | três saídas byte-idênticas, relatório e manifesto interno |
| serialização futura do registry | `PROVEN` somente após A2 validar duas emissões canônicas | nesta A1 é apenas requisito |
| coleta web/Steam e recaptura remota | `UNPROVEN` | conteúdo remoto e disponibilidade podem mudar |
| decisões editoriais, overlays, revisões e checkpoints como processo recriável | `UNPROVEN` | há registro/hashes, mas não receita automática suficiente para recriar a decisão |
| manifesto global como geração repetível | `UNPROVEN` | contém timestamp e depende do conteúdo ambiente de `rglob` |
| catálogo 69 e V2 congelada como produtos de D05 | `NOT_APPLICABLE` | são referências externas preservadas, verificáveis por hash, não geradas por D05 |
| políticas, requisitos e relatórios narrativos | `NOT_APPLICABLE` | são registros/contratos; sua preservação é byte-exata, não uma promessa de regeneração |

`PROVEN` refere-se à geração byte-idêntica, não apenas à possibilidade de conferir um hash existente.

## 10. Raízes gerenciadas do piloto

Raízes de armazenamento permitidas:

- `repo`: raiz do repositório, necessária para localizar o catálogo 69 canônico;
- `d05-expansion`: `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200`.

Para o verificador A2, a raiz fechada recomendada é `d05-expansion`: todo arquivo presente nela deverá possuir uma ocorrência no fragmento, e todo registro deverá existir. A enumeração inicial deve partir da fotografia já existente, não de uma reexecução de `gerar_manifest.py`, e deve suplementar explicitamente os dois manifests que o glob antigo omite por basename.

`ARTIFACT_REGISTRY/`, `.git/`, temporários de compilação, `__pycache__/`, toda a V2 fora de `09_CATALOGO_EXPANSAO_200`, firmware, IDX, SD e árvores históricas `LEX_MACHINA_REFERENCIAS*` não são raízes gerenciadas deste piloto. O catálogo 69 canônico é uma ocorrência externa ao domínio fechado: sua existência/hash é verificada, mas seu diretório-pai não recebe varredura de órfãos.

Há três ocorrências locais já incluídas no `08_MANIFEST/MANIFEST.json`, porém não versionadas pelo Git: `03_FONTES/BUSCA_118.json`, `06_RELATORIOS/CONSULTA_CP11.txt` e `06_RELATORIOS/CONSULTA_CP12.txt`. A2 deve registrá-las com a classe de acesso adequada sem copiar conteúdo para o registry. A ausência delas em outro checkout deve falhar de modo explícito; o registry não pode fingir portabilidade que a evidência atual não possui.

## 11. Invariantes e falha fechada

O verificador futuro deve falhar se:

- índice, fragmento ou schema não forem JSON válido/canônico;
- o hash/tamanho do fragmento no índice não conferir;
- arquivo registrado não existir, ou tamanho/SHA-256 divergir;
- path for absoluto, escapar da raiz, usar raiz desconhecida ou cair fora das raízes permitidas;
- houver colisão de `(logical_id, version)`, `occurrence_id`, path literal ou path `NFC + casefold`;
- uma ocorrência tiver dois hashes;
- existir arquivo órfão na raiz fechada, inclusive novo arquivo que um glob legado passaria a consumir;
- cardinalidades observadas divergirem: 8 lotes de triagem × 25, 200 números únicos, 199 dossiês/obras utilizáveis, 111 overlays/fila, 12 checkpoints, 3 revisões, 221 cards-base, 71 novos, 292 finais, 69 referências e 7 arquivos no pacote enriquecido;
- qualquer artefato marcado `PROVEN` não apontar para prova concreta;
- uma relação referenciar ID ausente;
- houver campo de ativação no fragmento;
- `mode != SHADOW` ou `authority != LEGACY_PIPELINE` durante A2.

O verificador apenas lê e relata. Nenhuma correção automática, normalização de bytes, movimentação ou alteração do pipeline é permitida.

## 12. Registry versus Dataset Lock

O Registry responde: **quais artefatos existem, quais bytes têm, onde ocorrem, que papel exercem e que evidência/proveniência existe?**

O futuro Dataset Lock responderá: **quais versões/ocorrências um perfil pode consumir, em qual ordem e com qual multiplicidade?**

Nesta A1, `observed_selection` documenta o comportamento legado; não autoriza consumo. A2 continua em sombra e não cria lock.

## 13. Golden reference independente

O conjunto de referência para A3 deve ser composto, não uma simples reexecução:

1. `08_MANIFEST/MANIFEST.json` para a fotografia e hashes de 852 membros da expansão;
2. `07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/MANIFEST.json` e seu hash externo registrado no relatório para os seis payloads e o próprio manifesto;
3. `06_RELATORIOS/DETERMINISMO_COMPILACAO.json` para os dois catálogos-base;
4. `07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/METADADOS_ENRIQUECIDO_V1.json` para catálogo-base, checkpoint, revisões e 111 overlays;
5. `06_RELATORIOS/RELATORIO_ENRIQUECIMENTO_V1.md` para a prova registrada das três compilações byte-idênticas;
6. `08_MANIFEST/INTEGRIDADE_ANTES.json` e `INTEGRIDADE_DEPOIS.json` para V2 e catálogo 69;
7. `06_RELATORIOS/BASELINE_ENRIQUECIMENTO_V1.json` como fotografia anterior de 580 arquivos, sem promovê-la a estado final.

O antigo manifesto global exclui qualquer basename `MANIFEST.json`; portanto não cobre nem a si próprio nem o manifesto interno. O golden composto fecha essa lacuna sem reescrever evidência histórica.

## 14. Arquivos exatos previstos para A2

- `ARTIFACT_REGISTRY/index.json`;
- `ARTIFACT_REGISTRY/datasets/d05_catalogo_expansao_200.json`;
- `ARTIFACT_REGISTRY/schemas/index.schema.json`;
- `ARTIFACT_REGISTRY/schemas/dataset.schema.json`;
- `ARTIFACT_REGISTRY/verify_registry.py`;
- `CLEANUP_AUDIT/MIGRATION_A2_D05_SHADOW_BASELINE.json`;
- `CLEANUP_AUDIT/MIGRATION_A2_D05_SHADOW_TEST.md`.

A2 não deverá editar nenhum arquivo sob `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200`, nenhum consumidor e nenhuma saída atual.

## 15. Riscos

1. O `rglob` global reage a arquivos ambientais; um novo arquivo muda o manifesto silenciosamente.
2. Três membros do manifesto final são não versionados, logo um clone Git isolado não contém toda a golden reference.
3. O filtro `p.name != 'MANIFEST.json'` omite também o manifesto interno, não apenas o arquivo de saída autorreferente.
4. O path absoluto gravado em `REFERENCIA_CATALOGO_69.json` é específico da máquina; identidade deve vir de logical ID/version/hash, com localização resolvida por `storage_root_id`.
5. Capturas múltiplas têm precedência lexicográfica; perder ordem ou multiplicidade pode trocar a fonte escolhida.
6. Ausência de overlay possui semântica; materializar overlay vazio mudaria identidade e contagens.
7. `created_by_run_id`, licenças e proveniência de nove consultas não existem de forma completa; preencher por suposição seria falsa precisão.
8. Hashes provam bytes, não confiabilidade editorial nem reprodutibilidade de coleta remota.
9. Sobreposição de raiz `repo` e `d05-expansion` deve ser resolvida por regra de maior especificidade para impedir dupla ocorrência acidental.
10. Um registry grande pode parecer autoritativo antes do lock; `SHADOW` e `LEGACY_PIPELINE` devem ser gates obrigatórios.

## 16. Critérios de sucesso do piloto A2

- fragmento D05 e índice passam schema e serialização canônica;
- todos os artefatos D05 da fotografia escolhida, inclusive manifests, possuem ocorrência explícita;
- zero órfãos na raiz fechada e zero apontamentos fora das raízes permitidas;
- hashes, tamanhos, contagens, relações e colisões passam;
- o verificador reproduz o mesmo resultado em duas execuções somente leitura;
- comparação com o golden composto não apresenta divergência;
- `git diff` funcional permanece vazio e o pipeline/outputs antigos permanecem byte-idênticos;
- nenhuma seleção do registry é consumida pelo sistema; qualquer divergência bloqueia A3.

## 17. Decisão A1

O piloto é tecnicamente adequado para D05 se A2 usar um fragmento único do dataset, enumeração explícita, modo sombra e golden composto. O risco médio vem principalmente da enumeração ambiental histórica, dos três membros não versionados e da omissão de manifests pelo glob antigo. Nenhum desses pontos exige alterar o legado nesta etapa.

## 18. Validação da A1

Validação somente leitura em 2026-09-27:

- HEAD `51ed82cbef67e7b06d76c690fd01ed6870740b0c`;
- árvore rastreada e índice sem alterações;
- baseline byte a byte: 1.677/1.677;
- protected545: 545/545;
- IDX: 130/130;
- V2 congelada: 281/281;
- `ENRIQUECIDO_V1`: 7/7;
- `.gitattributes` e os quatro documentos da política de bytes idênticos ao HEAD;
- somente estes dois relatórios A1 foram criados, ambos não rastreados; nenhum staging, commit, tag ou push foi feito.
