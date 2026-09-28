# Migração R1A — especificação do Shadow Resolver D05

## 1. Estado e escopo

Esta etapa especifica o primeiro resolver sombra do Dataset Lock D05. Nenhum resolver, schema, consumidor ou output resolvido foi implementado. O pipeline legado permanece **`LEGACY_AUTHORITATIVE`**.

O piloto R1B ficará restrito a `d05-historical-parity-v1`: 11 conjuntos, 1.699 itens semânticos, 151 ausências explícitas e quatro dependências. D01, 72 normas, IDX, ENTENDA, firmware, Release Manifest e SD ficam fora do escopo.

## 2. Responsabilidades

Os três contratos têm papéis separados:

- **Registry:** declara quais ocorrências existem, sua identidade lógica, versão, storage root, localização relativa, tamanho, SHA-256, papel e classe de acesso.
- **Dataset Lock:** seleciona explicitamente ocorrências, membros, conjuntos, ordem, multiplicidade, ausências e dependências para um perfil.
- **Shadow Resolver:** transforma as referências explícitas do Lock em uma seleção concreta validada, sem decidir conteúdo e sem alimentar o pipeline.

O resolver não escolhe versão melhor ou mais recente, não enumera pastas, não inclui arquivos novos, não aplica regras editoriais e não substitui filtros históricos. Tudo que não estiver selecionado explicitamente fica fora.

## 3. Entradas operacionais

Entradas mínimas futuras:

```text
--registry ARTIFACT_REGISTRY/index.json
--lock DATASET_LOCKS/d05-historical-parity-v1.lock.json
--expected-lock-sha256 <digest aprovado>
--root-bindings <arquivo runtime>
```

Como alternativa ao arquivo de bindings, a CLI poderá aceitar `--bind STORAGE_ROOT_ID=ABSOLUTE_PATH` repetido. Os dois modos serão mutuamente exclusivos. Binding duplicado, desconhecido, ausente ou fornecido nos dois modos causa falha.

O digest esperado do Lock é obrigatório porque o Lock precisa de uma âncora externa para detectar adulteração sem depender da Golden. O Lock já ancora o hash do Registry index e dos fragmentos.

Não são inputs operacionais:

- `D05_GOLDEN_REFERENCE.json`;
- `D05_REPLAY_RUN.json`;
- relatório A5B ou A6;
- inventário do filesystem;
- output de consumidor.

Golden e replay permanecem evidência para testes e comparação.

## 4. Root bindings

Root bindings separam identidade persistente de localização física runtime. Exemplo conceitual:

```text
D05_MANAGED_ROOT -> <repo>/LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200
CATALOG_69_ROOT  -> <local explícito do catálogo 69>
```

O arquivo real de bindings é local, não autoritativo e não deve ser versionado. Um futuro `root-bindings.example.json` poderá conter apenas placeholders neutros. O resolver exige exatamente os IDs usados pelas ocorrências selecionadas e dependências; não procura uma pasta compatível.

O path absoluto do binding nunca integra a identidade nem o hash lógico da seleção.

## 5. Vínculos criptográficos

Antes da resolução, R1B deverá:

1. validar JSON canônico e schemas;
2. comparar o hash real do Lock com `--expected-lock-sha256`;
3. comparar o hash real do Registry index com `registry_index_sha256` fixado pelo Lock;
4. abrir somente os fragmentos listados literalmente no index;
5. conferir tamanho e hash dos descritores do index;
6. conferir que os hashes de fragmento fixados pelo Lock coincidem;
7. validar `registry_id`, `dataset_id`, `profile_id`, modo `SHADOW` e constraints fail-closed.

O resolver não chamará a parte de orphan scanning do verifier atual do Registry, pois isso exigiria enumeração. O Registry verifier completo permanece um gate externo. Dentro do resolver, “Registry válido” significa estrutura canônica, schemas, vínculos, unicidade e integridade dos paths explicitamente selecionados.

## 6. Identidade e resolução de ocorrência

A chave de resolução é a tupla:

```text
(logical_id, version, occurrence_id)
```

O fragmento é indexado em memória por `occurrence_id`, por identidade lógica/versionada e por `(storage_root_id, relative_path)`. Duplicatas ou conflitos falham antes de qualquer output.

Para cada item do Lock:

1. localizar `occurrence_id` exatamente uma vez;
2. exigir igualdade de `logical_id` e `version`;
3. exigir que o storage root tenha binding explícito;
4. resolver e validar o path físico;
5. conferir existência, tamanho e SHA-256;
6. validar `member_ref`, quando presente;
7. emitir um item `RESOLVED` na mesma posição do Lock.

Zero ou mais de uma ocorrência/membro produz falha. Não existe fallback por nome, basename, hash, path semelhante ou versão mais recente.

## 7. Resolução de `member_ref`

R1B terá adaptadores fechados para os tipos usados pelo D05:

| kind/contexto | regra exata |
|---|---|
| sem `member_ref` | a própria ocorrência é o membro |
| `candidate_number` | exatamente um item da lista com `number == value` |
| `work_id`, dossiê-base | `work_id` do objeto deve ser exatamente igual |
| `work_id`, fila | exatamente um item de `fila` com o valor |
| `catalog_69_id` | exatamente um item de `obras` com `id == value` |
| `checkpoint` | `numero` e `obras_examinadas` devem coincidir integralmente com o valor estruturado |
| `evidence_id` | exatamente um item de `revisoes` com o valor |

O adaptador é escolhido por `set_id`, `item_kind` e `member_ref.kind`, nunca por heurística de filename. Combinação desconhecida falha.

Para validar `expected_items_sha256` sem Golden, o piloto terá projeções inversas fixas por `set_id`: paths relativos para conjuntos de ocorrências, valores de `member_ref` para conjuntos internos e basename somente no conjunto `enriched_payload_paths`, onde essa projeção faz parte do contrato. A projeção serve para validar o digest do Lock, não para descobrir membros.

## 8. Segurança de path

`relative_path` deve usar POSIX/NFC canônico. O resolver rejeitará:

- path absoluto, drive-relative, UNC ou device path;
- backslash, `.` ou `..` como componente;
- ADS/colon fora do identificador de drive do binding;
- nomes reservados do Windows;
- aliases por ponto ou espaço final;
- colisão por NFC + casefold dentro do mesmo storage root;
- substituição de identidade por basename.

O binding é resolvido para um diretório existente. Cada componente do target será inspecionado; symlink, junction ou outro reparse point no caminho selecionado falha no piloto. O target final resolvido deve continuar dentro da root resolvida. O arquivo deve ser aberto e ter tamanho conferido antes e depois do hash; mudança durante leitura falha.

## 9. Hash e tamanho

Path existente não basta. Cada ocorrência e dependência precisa satisfazer simultaneamente:

```text
is_file = true
size == Registry.size
sha256 == Registry.sha256
```

O hash é calculado sobre bytes do arquivo explicitamente aberto. Falha de leitura, alteração concorrente, tamanho divergente ou digest divergente encerra a execução sem seleção parcial válida.

## 10. Ordem

A ordem externa de `selection_sets` e a ordem interna de `items` são copiadas exatamente do Lock.

- `ordered=true`: os ordinais devem ser `1..N`, sem lacuna, repetição ou reordenação.
- `ordered=false`: nenhum item pode possuir ordinal e o resolver não inventa um.

Nenhuma ordenação por path, nome, hash, casefold ou filesystem será aplicada. O JSON usa chaves ordenadas, mas arrays preservam a ordem contratual.

## 11. Multiplicidade

Cada ocorrência do item no Lock gera exatamente uma ocorrência correspondente no output, preservando `set_id`, `semantic_role`, `occurrence_id`, `member_ref` e ordinal quando aplicável.

O mesmo artefato pode aparecer em vários conjuntos. Bytes iguais podem representar ocorrências ou papéis distintos. SHA-256 nunca é chave de deduplicação.

## 12. Ausências explícitas

As 151 ausências são copiadas para `explicit_absences` na mesma ordem e com o mesmo conteúdo. Elas são fatos semânticos e não se tornam arquivos sintéticos.

O resolver não abre path para uma ausência, não tenta preenchê-la e não procura substituto. Duplicação, perda ou alteração de uma ausência falha na verificação do output.

## 13. `restricted_local`

Os três `restricted_local` continuam fora do Git. Se uma ocorrência selecionada, dependência ou constraint exigir qualquer um deles, o binding precisa conduzir ao arquivo real e o resolver valida tamanho e SHA-256.

Ausência ou divergência resulta em `FAIL_CLOSED`. O resolver não copia, versiona, ignora, substitui ou busca equivalente.

## 14. Output derivado

O output canônico futuro será semelhante a:

```text
<runtime-dir>/SHADOW_RESOLVER_OUTPUT/d05-historical-parity-v1.resolved.json
```

O caller escolhe o diretório, preferencialmente temporário e fora do D05, Registry e Dataset Lock. O arquivo será marcado:

```text
DERIVED
SHADOW
NON_AUTHORITATIVE
```

`CLEANUP_AUDIT` não será destino runtime padrão. Uma etapa posterior poderá copiar explicitamente evidência revisada, sem transformar o resolved output em fonte autoritativa.

## 15. Schema da seleção resolvida

O núcleo conterá:

- versões do resolver e schema;
- modo e autoridade;
- `dataset_id`, `profile_id` e `registry_id`;
- hashes do Registry index, fragmentos e Lock;
- IDs dos root bindings, sem paths;
- `selection_sets`;
- `explicit_absences`;
- dependências resolvidas;
- resumo de resolução.

Cada item conterá `set_id`, `semantic_role`, ordinal quando aplicável, `logical_id`, `version`, `occurrence_id`, `member_ref` quando presente, `storage_root_id`, `relative_path`, `sha256`, `size` e `resolution_status`.

Proveniência completa do Registry não será duplicada.

## 16. Paths absolutos e diagnóstico

Paths absolutos não entram no núcleo canônico. Quando necessários para diagnóstico, ficam em relatório runtime separado, não canônico, ligado pelo SHA-256 do resolved output.

Assim, máquinas com bindings diferentes e bytes iguais produzem o mesmo núcleo canônico.

## 17. Canonicalização e determinismo

Formato:

- JSON UTF-8 sem BOM;
- LF;
- chaves ordenadas;
- indentação de dois espaços;
- newline final;
- sem timestamp, cwd, usuário ou hostname;
- arrays em ordem do Lock.

Com o mesmo Registry, Lock e bytes sob bindings válidos, o conteúdo canônico deve ser idêntico. O path absoluto runtime não participa do digest lógico.

## 18. Verifier futuro

`verify_resolved_selection.py` deverá validar:

1. Registry canônico, schemas, hashes e vínculos;
2. Lock canônico, hash esperado e pins do Registry;
3. bindings completos e únicos;
4. resolução única de ocorrência e membro;
5. segurança e confinamento dos paths;
6. existência, tamanho e SHA-256;
7. ordem e continuidade de ordinais;
8. multiplicidade sem deduplicação;
9. ausências preservadas;
10. quatro dependências resolvidas;
11. `restricted_local` fail-closed;
12. zero item extra;
13. zero descoberta implícita;
14. labels `DERIVED/SHADOW/NON_AUTHORITATIVE`;
15. nenhuma referência operacional a Golden ou replay.

Qualquer erro produz saída não zero e nenhum resultado declarado válido.

## 19. Zero filesystem discovery

O resolver e seu verifier não usarão `glob`, `rglob`, `os.walk`, `listdir`, `scandir`, regex de seleção, `latest`, enumeração de pasta ou busca de fallback.

Filesystem será acessado somente para abrir um path explicitamente derivado de Registry + Lock + binding, conferir existência/tamanho/hash e inspecionar seus componentes contra reparse points.

O Registry verifier completo atual pode continuar como gate externo, mas sua varredura de órfãos não será incorporada ao resolver.

**Zero-discovery garantido por design: SIM.**

## 20. Relação com legado, Golden e replay

O futuro comparador medirá `LEGACY_SELECTION` versus `SHADOW_RESOLVED_SELECTION` por membros, ordem, multiplicidade, dependências, ausências, paths efetivos quando relevantes e hashes.

R1A não instrumenta o legado. R1B também não alimentará o pipeline. Golden será apenas oracle de teste; replay A5B será somente evidência. Nenhum dos dois será importado ou exigido pelo resolver operacional.

## 21. Testes negativos R1B

Todos devem falhar de modo fechado:

1. hash divergente do Registry;
2. hash divergente do Lock;
3. root ausente;
4. ocorrência inexistente;
5. ocorrência ambígua;
6. arquivo ausente;
7. tamanho divergente;
8. hash divergente;
9. path traversal;
10. path absoluto indevido;
11. symlink/junction escapando root;
12. ordinal duplicado;
13. multiplicidade alterada;
14. wildcard introduzido;
15. tentativa de fallback;
16. `restricted_local` ausente.

Testes positivos devem comprovar 11 conjuntos, 1.699 itens, dez sequências ordenadas, um conjunto não ordenado, 151 ausências, quatro dependências e zero extras.

## 22. Arquivos previstos para R1B

```text
SHADOW_RESOLVER/resolve_selection.py
SHADOW_RESOLVER/verify_resolved_selection.py
SHADOW_RESOLVER/schemas/resolved-selection.schema.json
SHADOW_RESOLVER/schemas/root-bindings.schema.json
SHADOW_RESOLVER/root-bindings.example.json
SHADOW_RESOLVER/tests/test_d05_shadow_resolver.py
```

O example não conterá path pessoal. Nenhum arquivo real de bindings ou resolved selection será versionado automaticamente.

## 23. Riscos e critérios de sucesso

Riscos principais:

- divergência entre validação operacional do Lock e o verifier histórico que usa Golden;
- aliases e reparse points específicos do Windows;
- mudança do arquivo durante hashing;
- adaptador de `member_ref` aceitar mais de uma forma;
- output derivado ser confundido com autoridade;
- futura instrumentação alterar acidentalmente o consumidor legado.

Mitigações: adapters fechados, hashes fixados, paths explícitos, schema estrito, labels de autoridade, testes negativos e nenhuma integração com consumidor em R1B.

R1B será válida somente se funcionar sem Golden e replay, não fizer discovery, reproduzir 11 conjuntos e 1.699 itens, preservar ordem/multiplicidade/ausências, resolver quatro dependências, validar bytes, falhar sem `restricted_local`, não alterar consumidor e manter `LEGACY_AUTHORITATIVE`.

## Resultado R1A

Especificação concluída. Implementação, schemas, resolved selection e instrumentação do legado não foram iniciados.
