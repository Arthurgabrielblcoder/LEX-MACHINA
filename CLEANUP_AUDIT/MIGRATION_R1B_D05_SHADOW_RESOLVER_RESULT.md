# Migração R1B — resultado do Shadow Resolver D05

## 1. Implementação

Foi implementado o piloto D05 em `SHADOW_RESOLVER/`, restrito ao perfil `d05-historical-parity-v1`. O resolver transforma as referências explícitas do Artifact Registry e do Dataset Lock em uma seleção derivada, valida e determinística. Nenhum consumidor foi integrado e o pipeline permanece `LEGACY_AUTHORITATIVE`.

## 2. Inputs operacionais

- `ARTIFACT_REGISTRY/index.json`;
- fragmento D05 listado explicitamente pelo index;
- `DATASET_LOCKS/d05-historical-parity-v1.lock.json`;
- SHA-256 esperado do Lock fornecido pela CLI;
- bindings runtime explícitos.

Golden Reference, replay A5B, inventário de filesystem e output de consumidor não são inputs operacionais. A busca estática confirmou zero referência a Golden ou replay no resolver e no verifier.

## 3. Root bindings

Foram usados em runtime apenas os IDs `CATALOG_69_ROOT` e `D05_MANAGED_ROOT`. Os paths absolutos reais foram fornecidos por `--bind` e não foram gravados em artefato canônico nem em arquivo versionável. `root-bindings.example.json` contém somente placeholders neutros.

Bindings ausentes, desconhecidos, duplicados ou misturados entre arquivo e CLI falham de modo fechado. O resolver também rejeita duas IDs vinculadas ao mesmo diretório.

## 4. Vínculos criptográficos

| Objeto | SHA-256 |
|---|---|
| Registry index | `a14e1365de384b627d76f6bf5bfed18d2deac41704c90370581590d179d40aa6` |
| Fragmento Registry D05 | `022c88a293b9cdb9e661fca0b5d0dbd3ccb814cf57fb44acdcb51aff83d4a921` |
| Dataset Lock D05 | `5d9f6d0ba4fa1895f70a139510b0d441d62e187eb63ad99de030820946c29f39` |
| Resolved selection | `28212c24f88f07538d4cd5c50d1ce9f0ff603d684c477dfd23ec9984ae8db57a` |

Schemas, serialização canônica, descritor do fragmento, pins do Lock, identidades, tamanho e SHA-256 dos arquivos foram validados antes da emissão do resultado.

## 5. Resultado do perfil

| Dimensão | Resultado |
|---|---:|
| Selection sets | 11 |
| Conjuntos ordenados | 10 |
| Conjuntos não ordenados | 1 |
| Itens semânticos | 1.699 |
| Ausências explícitas | 151 |
| Dependências | 4/4 |
| `restricted_local` | 3/3 |
| Itens extras | 0 |

Todos os itens foram resolvidos por `(logical_id, version, occurrence_id)`, tiveram path confinado à root explícita e bytes verificados. Os adaptadores fechados validaram os membros internos por conjunto e tipo.

## 6. Ordem e multiplicidade

Os dez conjuntos ordenados preservaram a sequência literal do Lock e ordinais contíguos `1..N`. O conjunto não ordenado permaneceu sem ordinal. Cada item do Lock gerou exatamente um item no output; nenhuma deduplicação por path, hash ou identidade lógica foi aplicada. As projeções dos 11 conjuntos reproduziram todos os `expected_items_sha256` sem consultar a Golden.

## 7. Ausências e dependências

As 151 `explicit_absences` foram copiadas em ordem e não foram resolvidas como arquivos. As quatro dependências foram resolvidas univocamente e validadas por tamanho e SHA-256.

Os três artefatos `restricted_local` permaneceram fora do Git e foram validados no local runtime. A ausência de qualquer um produz `RESTRICTED_LOCAL_MISSING`, sem busca, cópia ou fallback.

## 8. Output canônico

`CLEANUP_AUDIT/D05_SHADOW_RESOLVED_SELECTION.json` está marcado como:

```text
artifact_class = DERIVED
mode = SHADOW
authority = NON_AUTHORITATIVE
```

O núcleo usa UTF-8 sem BOM, LF, chaves ordenadas, indentação de dois espaços e newline final. Não contém path absoluto, cwd, hostname, username ou timestamp volátil.

## 9. Determinismo

Duas execuções independentes com os mesmos inputs e bindings produziram SHA-256 idêntico:

```text
28212c24f88f07538d4cd5c50d1ce9f0ff603d684c477dfd23ec9984ae8db57a
```

O path físico dos bindings não participa do núcleo ou do hash canônico.

## 10. Verifier

`verify_resolved_selection.py` releu Registry, fragmento, Lock, bindings, resolved selection e arquivos físicos. Reconstruiu a seleção esperada sem usar o candidato como input e comparou integralmente o resultado. Resultado: `PASS`, com zero itens extras.

## 11. Testes negativos

Resultado: `16/16 FAIL-CLOSED`.

1. hash divergente do Registry;
2. hash divergente do Lock;
3. root binding faltando;
4. root binding desconhecido;
5. ocorrência inexistente;
6. ocorrência ambígua;
7. arquivo ausente;
8. tamanho divergente;
9. SHA-256 divergente;
10. traversal;
11. path absoluto;
12. escape por junction/reparse point;
13. ordinal duplicado;
14. multiplicidade reduzida;
15. wildcard/fallback;
16. `restricted_local` ausente.

Todos foram executados em estruturas temporárias. O teste de reparse point usou uma junction real no Windows após a plataforma negar criação de symlink sem privilégio.

## 12. Zero discovery

A inspeção AST e a busca textual dirigida encontraram zero chamadas a `glob`, `rglob`, `os.walk`, `os.listdir`, `os.scandir`, `Path.glob` ou `Path.rglob` no resolver e no verifier. O filesystem é acessado somente por paths derivados de Registry + Lock + binding explícito, para segurança, existência, stat, leitura e hash.

## 13. Isolamento do pipeline

Nenhum arquivo rastreado foi modificado. Nenhum consumidor rastreado referencia `SHADOW_RESOLVER`, `*.resolved.json` ou `D05_SHADOW_RESOLVED_SELECTION`. O output não alimentou build, pipeline ou descoberta legada. O replay A5B não foi reexecutado.

## 14. Limitações

O piloto é deliberadamente específico para D05 e para os adaptadores de membro usados pelo perfil `d05-historical-parity-v1`. O verifier compartilha as rotinas fail-closed de leitura, schema, path e bytes com o resolver, mas relê todas as fontes, reconstrói a seleção e não confia no conteúdo do output. O output permanece evidência derivada e não autoritativa.

## 15. Condição para R2

R2 poderá comparar a seleção sombra com observações do legado somente após revisão explícita destes artefatos. R1B não instrumenta o legado e não altera autoridade, consumidor ou pipeline.

## Resultado R1B

Resolver: `PASS`. Verifier: `PASS`. Determinismo: `PASS`. Testes negativos: `16/16 PASS`. Pipeline: `LEGACY_AUTHORITATIVE`.
