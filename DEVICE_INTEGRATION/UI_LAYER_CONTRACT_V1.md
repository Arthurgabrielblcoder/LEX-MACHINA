# UI LAYER CONTRACT V1 (preliminar, sem redesenho de interface)

A interface atual do v7.12.0 já tem leitor, relações/correlatas, jurisprudência e rodapé com opções "somente quando houver conteúdo".
Este contrato só define **quais sinais** o firmware recebe por dispositivo. Todos saem de **uma** linha de `CF88_TARGETS.IDX`.

| Camada (rótulo) | Flag | Origem | Quando mostrar |
|---|---|---|---|
| LEI | `HAS_LEI` | sempre verdadeiro | sempre |
| ENTENDER | `HAS_ENTENDA` | FLAGS[0] ∈ {E, B} | existe explicação aprovada (DIRECT ou coberta) |
| (selo) BLOCO | `BLOCK_COVERED` | FLAGS[0] = B | mostrar "explicado em conjunto: <título do bloco>" |
| CORRELATAS | `HAS_CORRELATAS` | FLAGS[1] = C | há CORRELATA visível no Reference Engine |
| JURISPRUDÊNCIA | `HAS_JURISPRUDENCIA` | FLAGS[2] = J | há JURISPRUDENCE visível |
| REFERÊNCIAS | `HAS_REFERENCIAS` | FLAGS[3] = W | há WORK_REFERENCE visível |
| (interno) | `HAS_ANY_REFERENCE_ROW` | FLAGS[4] = R | inclui históricas ocultas (modo diagnóstico) |
| (selo) NOTA | `EXTERNAL_NOTES_AVAILABLE` | FLAGS[5] = X | a explicação tem camada externa ou nota temporal |
| (selo) STATUS | `LEGAL_STATUS` | coluna 3 | REVOKED: sem ENTENDA, com aviso "dispositivo revogado"; UNKNOWN: sem selo de vigência |

## Regras

- **Sem ENTENDA:** a opção ENTENDER não aparece.
  - Opcionalmente, "ver explicação do artigo", **sempre** rotulada como contexto do artigo, e só se o ancestral tiver ENTENDA.
  - Não existe ENTENDA para art. 25 em diante.
- **BLOCK:** o título exibido é o do bloco (`D|`), e a explicação é a mesma do âncora.
- **Notas temporais** (`Z|TIME_SENSITIVE|data`): mostrar selo "revisar após <data>". O firmware não decide vigência.
- **Falha de camada:** ocultar só a camada afetada. A LEI nunca depende de camada alguma.
- **Coexistência:** enquanto houver índices legados (`/99_RELATIONS_V2`, `/99_JURISPRUDENCIA_V2`), a V1 mostra só uma fonte por camada, escolhida por configuração, para não duplicar itens. Decisão pendente para a A2.
