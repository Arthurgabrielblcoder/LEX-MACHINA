# C3A.1 — fechamento editorial da C3A e preparação do C3B

**`RUN4_CANDIDATE_HOST_ONLY`.** Nenhum cartão foi tocado, nenhum firmware foi alterado e nada foi promovido a baseline.

## Tipos de relação (decisão humana C3A.1)

| Target | Norma | Tipo | Revalidar em |
|---|---|---|---|
| `CF88:ART.158:PAR.1:INC.I` | LC:63/1990 | REGULAMENTA | — |
| `CF88:ART.195:INC.I:AL.b` | LC:70/1991 | IMPLEMENTA | 2027-01-01 |
| `CF88:ART.214:CAPUT` | LEI:15388/2026 | EXECUTA_POLÍTICA_CONSTITUCIONAL | 2036-04-14 |

- **Não classificados restantes:** 0. O marcador `NAO_CLASSIFICADA_REVISAO_LEGADA` agora é rejeitado pelo motor.
- **PNE:** continuam um único vínculo no caput do art. 214 e `NEXT_STEP = ANNEX_ROUTE_SUPPORT`.

## Índice de artigos (EXT_ARTIGOS candidato)

- **Auditoria restrita** aos artigos que os vínculos DEVICE_READY abrem (23 artigos): {'OK': 21, 'MISSING_FROM_CARD_INDEX': 2, 'OFFSET_NOT_AT_HEADING': 0}.
- **Reparos** (offsets dos bytes reais do texto congelado; UTF-8 sem BOM, LF; o OFFSET aponta o início de "Art."):
  - EXT_LC87_1996 art. 10: offset 12152, tamanho 784.
    - O predecessor (art. 9) foi encurtado de 1905 para 1121, para manter as faixas contíguas.
  - EXT_LEI7998_1990 art. 9: offset 19559, tamanho 2165.
    - O predecessor (art. 8-C) foi encurtado de 2491 para 326, para manter as faixas contíguas.
  - O firmware só usa o OFFSET (busca linear em `buscarOffsetArtigoExternoV2`).
- **Resultado:** lacunas restantes nos vínculos DEVICE_READY: 0.
  - Resolução por vínculo: {'DIRECT_ARTICLE_RESOLUTION': 23, 'OPEN_NORM_START_BY_DECISION': 1}.
  - O único `OPEN_NORM_START_BY_DECISION` é um vínculo legado KEEP cuja rota sempre abriu a norma inteira.
- **Fallback:** `OPEN_NORM_START` continua no motor para casos sem entrada no índice.

## RUN4 regenerado

- **Visíveis DEVICE_READY:** 24, sem mudança: a correção do índice não altera a contagem.
- **Cache do firmware:** REL_LOOKUP 26/64 linhas; 15/32 normas.

## Pacote C3B

- `C3B_PHYSICAL_TEST_PACKAGE/` tem 5 arquivos alterados, com cópia de rollback de cada um.
- O teste foi preparado e NÃO executado; o plano está em `C3B_PHYSICAL_TEST_PLAN.md`.
- **`.gitattributes`:** os textos congelados e o pacote ficaram como `-text`, para que o checkout no Windows (`core.autocrlf=true`) não altere bytes.

