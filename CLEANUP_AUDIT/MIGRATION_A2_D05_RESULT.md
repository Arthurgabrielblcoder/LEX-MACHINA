# Migração A2 — resultado do Artifact Registry sombra D05

Status: **PASSA**. O registry descreve e verifica o D05 sem participar da seleção operacional. O pipeline legado permanece autoritativo.

## 1. Estrutura criada

```text
ARTIFACT_REGISTRY/
  index.json
  datasets/
    d05.catalogo-expansao-200.json
  schemas/
    registry-index.schema.json
    registry-fragment.schema.json
  verify_registry.py
```

Artefatos de auditoria desta etapa:

- `CLEANUP_AUDIT/MIGRATION_A2_D05_BASELINE.json`;
- `CLEANUP_AUDIT/MIGRATION_A2_D05_RESULT.md`.

Todos os JSONs do registry e o baseline usam UTF-8 sem BOM, LF, chaves ordenadas, indentação de dois espaços e um LF final. O índice contém somente o fragmento D05, seu path, schema version, tamanho e SHA-256.

## 2. Entradas registradas

| Escopo | Ocorrências | Bytes |
|---|---:|---:|
| `D05_MANAGED_ROOT` | 854 | 14.218.773 |
| `CATALOG_69_ROOT` externo | 1 | 326.433 |
| **Total** | **855** | **14.545.206** |

A enumeração cobre todos os arquivos existentes na raiz D05, inclusive os dois arquivos chamados `MANIFEST.json`. Não foram criadas ocorrências fictícias para os 88 registros sem overlay.

## 3. Roles

| `artifact_role` | Quantidade |
|---|---:|
| `base_catalog_output` | 2 |
| `base_dossier` | 199 |
| `candidate_universe` | 1 |
| `catalog_69_reference` | 1 |
| `catalog_compiler` | 2 |
| `determinism_evidence` | 1 |
| `enriched_package_manifest` | 1 |
| `enriched_package_output` | 6 |
| `enrichment_baseline` | 1 |
| `enrichment_checkpoint` | 12 |
| `enrichment_overlay` | 111 |
| `enrichment_report` | 1 |
| `enrichment_revision` | 1 |
| `enrichment_source_capture` | 128 |
| `enrichment_state` | 1 |
| `expansion_manifest` | 1 |
| `external_catalog_69` | 1 |
| `identity_batch` | 8 |
| `integrity_evidence` | 2 |
| `manifest_tooling` | 1 |
| `rejection_record` | 2 |
| `report_evidence` | 26 |
| `report_tooling` | 9 |
| `requirements_record` | 1 |
| `source_capture` | 316 |
| `source_collection_tooling` | 1 |
| `triage_batch` | 8 |
| `triage_curator_input` | 6 |
| `triage_tooling` | 5 |

## 4. Storage roots

`D05_MANAGED_ROOT` resolve, a partir de `REPOSITORY_ROOT`, para `LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200`. É a única raiz fechada e sujeita à detecção de órfãos.

`CATALOG_69_ROOT` resolve para `LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1`. É uma raiz externa, não gerenciada: o arquivo registrado é verificado, mas o diretório não é varrido em busca de órfãos.

O verificador rejeita path absoluto, `..`, barras invertidas, path não NFC e qualquer resolução fora da raiz declarada.

## 5. Catálogo 69

`CATALOGO_69_CANONICO.json` foi registrado como `external_catalog_69`, sem cópia e sem mudança no consumidor legado. O locator é relativo a `CATALOG_69_ROOT`; tamanho 326.433 bytes; SHA-256 `58d742a2592f54eb309c3900871d77fc6253a1fb20f7571f1913755fd9797a77`.

Sua proveniência aponta para `00_ENTRADA/REFERENCIA_CATALOGO_69.json` e `08_MANIFEST/INTEGRIDADE_DEPOIS.json`.

## 6. Identidade e hashes

Cada ocorrência contém identidade lógica (`logical_id`, `version`), identidade física (`occurrence_id`), localização (`storage_root_id`, `relative_path`) e identidade dos bytes (`sha256`, `size`). Todos usam `canonical_hash_algo = SHA-256` e `byte_policy = BYTE_EXACT`.

Hashes principais:

- fragmento D05: `022c88a293b9cdb9e661fca0b5d0dbd3ccb814cf57fb44acdcb51aff83d4a921`;
- catálogo-base da expansão: `5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43`;
- catálogo combinado 69 + utilizáveis: `6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6`;
- manifesto `ENRIQUECIDO_V1`: `0312e5f091981f8065673529aca04437ed0fc7ecaac26cd144d2af26ab37774c`;
- manifesto global da expansão: `c1e21ae27c56233b58e2a65f074f433612f83620654bd37a5006c23ee7ff6b0d`.

## 7. Reproducibility

| Classe | Ocorrências | Regra aplicada |
|---|---:|---|
| `PROVEN` | 9 | dois catálogos-base e sete arquivos do pacote enriquecido, apoiados pelas provas existentes |
| `UNPROVEN` | 825 | dados editoriais, capturas, decisões e manifestações históricas sem receita byte-reprodutível completa |
| `NOT_APPLICABLE` | 21 | tooling, requisitos/relatórios narrativos e catálogo 69 como dependência externa de D05 |

Nenhum artefato foi promovido a `PROVEN` apenas porque seu hash pôde ser conferido.

## 8. Proveniência

O fragmento referencia o manifesto histórico quando o arquivo já era membro dele. Capturas registram a presença dos campos embutidos comprovados, como URL, source URL, tier, data de acesso, verificação e snapshot hash. Dossiês apontam para seu campo de proveniência; overlays apontam para a decisão humana embutida. Receitas de geração foram registradas somente para os dois compiladores determinísticos.

As nove consultas web sem recibo local completo permanecem como lacuna explícita, com seus `evidence_id`. `created_by_run_id` permanece `null` quando não há evidência uniforme.

## 9. Órfãos e membros não versionados

O verificador encontrou **zero órfãos** e **zero arquivos ausentes** em `D05_MANAGED_ROOT`.

Três membros já presentes no manifesto histórico continuam não versionados no Git e foram registrados como `restricted_local`:

- `03_FONTES/BUSCA_118.json`;
- `06_RELATORIOS/CONSULTA_CP11.txt`;
- `06_RELATORIOS/CONSULTA_CP12.txt`.

Eles não são órfãos do registry porque possuem ocorrências explícitas. A ausência em outro checkout falhará de forma fechada; o registry não afirma portabilidade desses arquivos.

## 10. Conflitos

Resultado atual:

- zero colisões de `(logical_id, version)`;
- zero `occurrence_id` duplicadas ou divergentes;
- zero localizações literais duplicadas;
- zero colisões NFC/casefold;
- zero paths fora das raízes;
- zero divergências de tamanho ou SHA-256;
- zero conflitos bloqueantes.

Hashes iguais em ocorrências diferentes continuariam permitidos e não provocariam deduplicação.

## 11. Comportamento fail-closed

Além da execução positiva, foram feitos cinco testes em cópias temporárias. Todos produziram falha e código diferente de zero:

1. fragmento adulterado;
2. campo obrigatório removido;
3. colisão lógica com bytes diferentes;
4. path traversal;
5. arquivo órfão em managed root.

O verificador também rejeita JSON não canônico, hash/tamanho de fragmento divergente, schemas inválidos, roots desconhecidas, arquivos ausentes e campos operacionais `active`, `enabled` ou `selected_for_consumption`.

## 12. Manifest legado

O comportamento legado não foi alterado. `08_MANIFEST/MANIFEST.json` continua com seus 852 membros e sua regra de exclusão por basename.

O fragmento sombra registra separadamente:

- `08_MANIFEST/MANIFEST.json`;
- `07_CATALOGO_CANDIDATO/ENRIQUECIDO_V1/MANIFEST.json`.

Assim, a omissão histórica fica representada sem corrigir ou reexecutar o produtor legado.

## 13. Comparação com A1

A2 implementa a estrutura fragmentada prevista por A1, com um índice e apenas um dataset. As cardinalidades contratuais foram preservadas: 200 candidatas, 8 lotes de identidade, 8 lotes de triagem, 199 dossiês, 128 capturas de enriquecimento, 111 overlays, fila de 111, 12 checkpoints, 3 revisões e pacote enriquecido com 7 arquivos.

As diferenças nominais em relação ao exemplo A1 são apenas os nomes mais explícitos dos schemas (`registry-index.schema.json` e `registry-fragment.schema.json`) e o filename do fragmento com o próprio `dataset_id`. Não há diferença de responsabilidade.

## 14. Resultado do verificador

Comando:

```text
python ARTIFACT_REGISTRY/verify_registry.py
```

Resultado:

```text
PASS
entries=855
external_entries=1
orphans=0
missing=0
conflicts=0
errors=0
```

O verificador é somente leitura. Não importa módulos do pipeline e não escreve em D05.

## 15. Limitações e riscos conhecidos

- O registry fotografa os bytes atuais; não torna coleta remota reproduzível.
- Os três membros `restricted_local` impedem que um clone Git isolado reproduza toda a fotografia.
- A proveniência histórica não possui run IDs uniformes.
- Nove consultas web continuam sem recibo local completo.
- O path absoluto ainda existe no arquivo legado de referência; o registry apenas fornece um locator relativo paralelo.
- O registry não representa ausência de overlay como arquivo e não decide seleção.
- A cobertura de schema é deliberadamente restrita ao piloto D05.
- O verificador não substitui auditoria editorial nem valida a veracidade do conteúdo.

## 16. Pipeline e integridade

Nenhum arquivo funcional D05 foi modificado. Nenhum import foi adicionado, nenhum glob/rglob foi substituído e nenhum output foi recompilado. O pipeline não conhece `ARTIFACT_REGISTRY` e continua autoritativo.

O gate direcionado final passou: baseline geral 1.677/1.677, byte policy intacta, D05 funcional 854/854 pelo registry, `ENRIQUECIDO_V1` 7/7, V2 281/281, protected545 545/545 e IDX 130/130.

## 17. Condição para A3

A3 somente poderá começar após revisão conjunta dos artefatos A1+A2. Sua condição inicial será manter o registry em modo sombra, comparar o resultado contra o golden composto e bloquear qualquer divergência. Esta etapa não criou Dataset Lock, Release Manifest ou Relocation Ledger.
