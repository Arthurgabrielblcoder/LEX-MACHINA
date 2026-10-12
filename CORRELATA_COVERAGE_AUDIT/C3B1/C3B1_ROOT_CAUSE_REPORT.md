# C3B.1 — causa raiz das falhas físicas do C3B

## Causa 1: `CF88_TARGETS.IDX` não foi atualizado — CONFIRMADA

- **Como o firmware decide:** `lexV1AtualizarDisponibilidade()` mostra `1 CORR.` quando `lexV1FlagCamada(flags, LEXV1_LAYER_CORRELATA)`, isto é, `flags[1]=='C'` no `CF88_TARGETS.IDX`.
  - A decisão usa as query keys do alvo (ART.n → ART.n e ART.n:CAPUT).
- **O que faltou:** o pacote C3B trocou REF_* e RELACOES, mas não o TARGETS. As flags continuaram as do RUN3.
- **Reprodução no simulador** (estado instalado no teste: pacote C3B mais o TARGETS antigo):

| Target | C no TARGETS instalado | CORRELATA no REF instalado | Sintoma |
|---|---|---|---|
| `CF88:ART.158:PAR.1:INC.I` | - | sim | vínculo existe mas `1` não aparece |
| `CF88:ART.158:PAR.1:INC.II` | C | não | `1` fantasma (lista vazia) |
| `CF88:ART.202:PAR.1` | - | sim | vínculo existe mas `1` não aparece |
| `CF88:ART.214` | - | sim | vínculo existe mas `1` não aparece |
| `CF88:ART.214:INC.I` | C | não | `1` fantasma (lista vazia) |
| `CF88:ART.239:PAR.3` | - | sim | vínculo existe mas `1` não aparece |
| `CF88:ART.37:PAR.3:INC.III` | C | não | `1` fantasma (lista vazia) |
| `CF88:ART.37:INC.II` | C | não | `1` fantasma (lista vazia) |

## Causa 2: `relation_id` compartilhado por várias linhas do RELACOES — CONFIRMADA

- **Como o firmware resolve:** `lexV1AdicionarCorrelataPorId()` chama `lexV1LinhaLegadaPorId(..., "|" + relId + "|", false, linha)`, um `strstr` sobre o RELACOES inteiro.
  - Fica com a PRIMEIRA linha que contém o id, sem olhar a origem.
- **IDs compartilhados no pacote C3B:** `REL_521CE46DBB902C96`, `REL_B41DCE7A7582235E`, `REL_D7475B8BEB5B6C53`.
- **Reprodução do teste 2:** no estado instalado, o § 5º do art. 202 resolve para a linha de origem `['CF88', '202', '4', '', '']`, com artigos `['1']` (a linha do § 4º), e não o art. 26.

## Correção escolhida (build, sem firmware)

- **IDs de relação únicos por linha do aparelho:** cada linha do RELACOES tem um id único.
  - Ids já únicos são mantidos.
  - Ids compartilhados ganham um `device_relation_id` determinístico (origem × id pai × destino × modo × artigos); o id pai fica na proveniência.
  - O REF_PAYLOAD aponta para o id exato.
  - Foram renomeadas 7 linhas, de 3 ids compartilhados.
- **Alternativa rejeitada:** mudar o firmware para resolver por id + origem também funciona, mas exige firmware novo. O build resolve de forma genérica e segura.
- **Flags:** a posição C do TARGETS passa a ser recalculada do mesmo export DEVICE_READY, com a mesma regra do gerador do SD.
  - Alvo exato, só CURRENT_VISIBLE, sem herança.
  - Todas as outras posições e campos ficam byte a byte iguais.

## Resultado no simulador (candidato C3B.1)

- **`CORRELATA_REFERENCE_ID_RESOLUTION`:** `1_TO_1` (26 reference ids).
- **`DEVICE_READY_ROUTE_SIMULATION`:** `24/24`.
- **Expectativas físicas simuladas:** 19/19 PASS.
- **CF art. 37, § 3º, III:** `PASS`.
  - Flag antes `-C--R-`, depois `----R-`.
  - Nenhum vínculo DEVICE_READY, nenhuma linha CORRELATA órfã, e `1 CORR.` indisponível.

## Outro bug descoberto: rotas erradas latentes no baseline físico atual

- **O que acontece:** o mesmo defeito de id compartilhado já existe no cartão baseline (RUN3).
  - 9 vínculos legados abrem hoje uma rota diferente da gravada na sua própria linha.
- **Situação no C3B.1:** todos ficam corrigidos (id único) ou não são publicados (excluídos ou suprimidos por decisão humana).

| Target | Destino | Rota pretendida | Rota que o firmware abre | C3B.1 |
|---|---|---|---|---|
| `CF88:ART.153:PAR.4:INC.III` | EXT_LEI11250_2005 | ABRIR_ARTIGO_INTERNO 1 | ABRIR_NORMA_SEM_SALTO | FIXED |
| `CF88:ART.195:INC.II` | EXT_LC70_1991 | ABRIR_NORMA_SEM_SALTO | ABRIR_ARTIGO_INTERNO 1 | NOT_PUBLISHED_IN_C3B1 |
| `CF88:ART.195:PAR.1` | EXT_LC70_1991 | ABRIR_NORMA_SEM_SALTO | ABRIR_ARTIGO_INTERNO 1 | NOT_PUBLISHED_IN_C3B1 |
| `CF88:ART.195:PAR.2` | EXT_LC70_1991 | ABRIR_NORMA_SEM_SALTO | ABRIR_ARTIGO_INTERNO 1 | NOT_PUBLISHED_IN_C3B1 |
| `CF88:ART.201:INC.II` | EXT_LEI7998_1990 | ABRIR_ARTIGO_INTERNO 1 | ABRIR_NORMA_SEM_SALTO | NOT_PUBLISHED_IN_C3B1 |
| `CF88:ART.201:INC.IV` | EXT_LEI7998_1990 | ABRIR_ARTIGO_INTERNO 1 | ABRIR_NORMA_SEM_SALTO | NOT_PUBLISHED_IN_C3B1 |
| `CF88:ART.214:INC.VI` | EXT_LEI15388_2026 | ABRIR_ARTIGO_INTERNO 4 | ABRIR_NORMA_SEM_SALTO | NOT_PUBLISHED_IN_C3B1 |
| `CF88:ART.37:PAR.3:INC.II` | EXT_LEI13460_2017 | ABRIR_NORMA_SEM_SALTO | ABRIR_ARTIGO_INTERNO 1 | NOT_PUBLISHED_IN_C3B1 |
| `CF88:ART.37:PAR.3:INC.III` | EXT_LEI13460_2017 | ABRIR_NORMA_SEM_SALTO | ABRIR_ARTIGO_INTERNO 1 | NOT_PUBLISHED_IN_C3B1 |

## Divergência registrada (não corrigida por regra da missão)

- **Flag R:** a posição R (`[4]`, "qualquer linha no REF_LOOKUP") não foi recalculada.
  - O firmware não lê R (só as posições 0 a 3).
  - A missão permite mudar apenas C. R fica com o valor do baseline.

