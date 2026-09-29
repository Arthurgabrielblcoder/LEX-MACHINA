# ISSUE: RELATIONS_V2_LEGACY_64_LINE_LIMIT

**Classificação: NON_BLOCKING para o DEVICE V1.** Documentado e não corrigido nesta fase.

## Origem

- Arquivo: `firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA.ino`, função `carregarCacheRelationsV2()`.
- Introduzido em `498060e` ("Salva base v7.10.1 Relations V2 Fast") e preservado em `d4e816f` (v7.12.0).
- Mecanismo:

```cpp
#define MAX_LOOKUP_V2_CACHE 64   // l. 799
#define MAX_NORMAS_V2_CACHE 32   // l. 800
while(f.available() && totalLookupV2Cache<MAX_LOOKUP_V2_CACHE){ ... }   // l. 900
while(fn.available() && totalNormasV2Cache<MAX_NORMAS_V2_CACHE){ ... }  // l. 920
```

- O laço para ao chegar a 64 linhas de `REL_LOOKUP.IDX` (ou 32 de `EXT_NORMAS.IDX`) **sem aviso**. Mesmo assim, o cache é marcado como carregado.
- A consulta (l. ~1625) percorre só o cache. As entradas excedentes nunca são encontradas e não há fallback para o SD.

## Impacto medido

| Arquivo | Linhas de dados | Limite | Truncado hoje? |
|---|---|---|---|
| `REL_LOOKUP.IDX` (pacotes 2E5/2E6, sha `863ff538…`) | 41 | 64 | não |
| `EXT_NORMAS.IDX` (2E6) | 20 | 32 | não |

- O cartão físico não pôde ser lido nesta fase (está no aparelho). A contagem acima é dos pacotes do repositório que o originaram. **Confirmar no backup do cartão.**
- **Risco futuro:** qualquer expansão das correlatas V2 acima de 64 chaves perderia vínculos silenciosamente.

## Por que NON_BLOCKING

O DEVICE V1 obtém correlatas pelo Reference Engine (`REF_PAYLOAD.IDX`, tipo `CORRELATA`), com busca binária e sem teto. O cache legado só permanece enquanto a V1 conviver com a interface antiga.

## Correção proposta (A3 ou posterior, fora da integração V1)

1. Aplicar o mesmo padrão já validado no cache J4: contar as linhas na primeira passagem e alocar exatamente N em PSRAM.
2. Manter um limite só defensivo (4.096) e falhar para o fallback SD **com log** se o limite for ultrapassado.
3. Imprimir `RELV2 CACHE: lookup=N/total` e alertar se houver truncamento.
4. Adicionar teste de regressão com 0, 1, 64, 65 e 200 linhas simuladas.
