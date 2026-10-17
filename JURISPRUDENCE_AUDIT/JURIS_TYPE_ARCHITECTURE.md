# Arquitetura extensível de tipos de jurisprudência (Partes E/F)

```
GENERAL_JURIS_TYPE_ARCHITECTURE = PASS (host) · GENERAL_FIRMWARE_PROTOTYPE = PASS (compilado; NÃO gravado)
LEGACY_IDS_SUPPORTED = YES · LEGACY_FICHAS_SUPPORTED = YES · FIRMWARE_FLASHED = NO · firmware/ NÃO alterado
```

## 1. Problema

O app aprovado tem três limitações:

1. **Só aceita linhas com ID `STF:`.** A checagem fica em `adicionarLinhaJurisCF`. Súmulas do TSE e do STJ ficam invisíveis.
2. **Classes processuais caem em `OUTRO n`.** É o caso de HC, MS, AP, AI, Inq, Rcl e MI, que não têm `case` no `rotuloTipoJurisprudencia`.
3. **Súmula comum sai como `SUMULA STF n`, seja qual for o tribunal.**

No cartão J2C, tudo é STF. O baseline físico de **vínculos** é **261 em 160 targets** (`REF_PAYLOAD`, JURISPRUDENCE, CURRENT_VISIBLE). A tabela abaixo conta outra coisa: os **registros de precedente** (linhas) do índice legado `JURISPRUDENCIA.IDX`, que são 301 (ver `J2_BASELINE_RECONCILIATION.json`):

| Tipo | Registros no `JURISPRUDENCIA.IDX` (não são vínculos) |
|---|---:|
| `repercussao_geral` | 284 |
| `sumula_vinculante` | 12 |
| `adi` | 5 |

## 2. Modelo

| Campo | Onde | Regra |
|---|---|---|
| **Tribunal** | coluna `TRIBUNAL` do `JURISPRUDENCIA.IDX` | STF, STJ, TSE, TST ou STM (lista fechada) |
| **Classe** | coluna `TIPO` (minúscula) | entrada da tabela de classes ou tipo legado |
| **ID** | `TRIBUNAL:CLASSE:NUMERO:NORMA:ART:PAR:INC:ALI` | o prefixo do ID **deve** ser igual à coluna `TRIBUNAL` (fail closed) |
| **Identificador / ficha** | `TRIBUNAL:CLASSE:NUMERO` → `TRIBUNAL_CLASSE_NUMERO.TXT` | regra inalterada de `arquivoDetalheJurisCF` |
| **Rótulo** | derivado de (tipo, tribunal, número) | ver tabela abaixo |

**Rótulos.** São iguais no host (`juris_types.label`) e no firmware (`juris_types.patch`):

| TIPO no IDX | Tribunal | Rótulo | Ficha (exemplo) |
|---|---|---|---|
| `hc` | STF | **HC 232627** | `STF_HC_232627.TXT` |
| `ms` | STF | **MS 27931** | `STF_MS_27931.TXT` |
| `ap` | STF | **AP 694** | `STF_AP_694.TXT` |
| `ai` | STF | **AI 343461** | `STF_AI_343461.TXT` |
| `inq` | STF | **Inq 4781** | `STF_INQ_4781.TXT` |
| `rcl` | STF | **Rcl 84738** | `STF_RCL_84738.TXT` |
| `adpf` | STF | **ADPF 378** | `STF_ADPF_378.TXT` |
| `mi` | STF | **MI 7300** | `STF_MI_7300.TXT` |
| `sumula` | TSE | **Súmula 9 TSE** | `TSE_SUMULA_9.TXT` |
| `sumula` | STJ | **Súmula 403 STJ** | `STJ_SUMULA_403.TXT` |
| `sumula` | STF | Súmula 702 STF | `STF_SUMULA_702.TXT` |
| `repercussao_geral` (legado) | STF | RG TEMA 558 (inalterado) | `STF_RG_558.TXT` |
| `sumula_vinculante` (legado) | STF | SV 46 (inalterado) | `STF_SV_46.TXT` |
| `adi` (legado) | STF | ADI 7064 · ADI 7047/7064 (inalterado) | `STF_ADI_7047-7064.TXT` |

**Outras regras:**

- **Classes da tabela:** além das acima, a tabela traz RHC, RMS, Pet, ADO, RE, ARE e Ext. Uma classe nova é uma linha nova na tabela, sem enum novo e sem `case` novo.
- **Tipo desconhecido:** o host recusa publicar (`ValueError`), então o aparelho nunca recebe `OUTRO n` para um tipo conhecido. O `default` do firmware continua só como rede de segurança.
- **Título da ficha aberta:** `STF HC 232627`. Na súmula, o tribunal já está no rótulo (`Súmula 9 TSE`, e não `TSE Súmula 9 TSE`).
- **Largura:** todos os precedentes dos Batches 01–09 cabem na lista (34 colunas, contando o prefixo `NN `).

## 3. Migração compatível

Os vínculos legados não mudam:

- **IDs e registros:** os 301 registros do índice legado, que não são vínculos (`STF:RG:…`, `STF:SV:…`, `STF:ADI:…`, TRIBUNAL = STF) passam na nova checagem `tribunalJurisSuportado`.
- **Rótulos:** idênticos.
- **Fichas e índices:** mesmos nomes de ficha; `JUR_LOOKUP.IDX` e o formato do IDX inalterados.
- **Testes:** `test_legacy_ids_and_labels_unchanged`.

O único rótulo que muda é o da súmula comum (`SUMULA STF n` → `Súmula n STF`). Não há nenhuma súmula comum instalada, então nada visível muda no aparelho.

No caminho V1, o `REFERENCE_ID` (`JURISPRUDENCE:<chave>@<target>`) já extrai a chave sem supor STF, e `REF_PAYLOAD` e `REF_LOOKUP` não mudam.

**Host:** `juris_types.py` é a fonte única dos dados:

- tabela de classes;
- lista de tribunais;
- rótulo, título e nome da ficha;
- `from_precedent()` para os módulos de revisão;
- `parse_firmware_tables()`, que relê a tabela do patch, e o teste exige igualdade com o host.

## 4. Protótipo de firmware (Parte F, host-only)

**Arquivos:**

- `JURIS_TYPE_PROTOTYPE/build_juris_type_prototype.py` (9 edições por âncora exata, fail closed);
- `juris_types.patch`;
- `JURIS_TYPE_PROTOTYPE_BUILD.json`.

**Base:** `firmware/` após a Parte D, que reproduz o app aprovado exceto metadados.

| Build | Programa (B) | RAM estática (B) | App .bin (B) | Partição app livre (B) |
|---|---:|---:|---:|---:|
| Aprovado (R2, gravado) | 1.100.991 | 126.148 | 1.101.136 | 209.584 |
| Base `firmware/` (Parte D) | 1.100.991 | 126.148 | 1.101.136 | 209.584 |
| Protótipo HC (operação noturna) | 1.101.127 | 126.148 | 1.101.280 | 209.440 |
| **Protótipo tipos genéricos** | **1.102.031** | **126.148** | **1.102.176** | **208.544** |

- **Programa:** +1.040 B em relação à base.
- **RAM estática:** +0 B.
- **Buffers:** `MAX_RELACOES_ARTIGO = 32` e `RelacaoJuridica` inalterados, sem alocação nova.
- **PSRAM:** o código não muda o uso. O cache do `JURISPRUDENCIA.IDX` cresce só com as linhas de dados novas.
- **Partição:** 4 MB, esquema default (app de 1.310.720 B); folga de ~204 KB.
- **HC:** o protótipo HC fica **substituído**. O HC agora é uma linha da tabela.

**Não verificado (exige gravação e teste físico, fora desta operação):**

- boot;
- lista e ficha de cada tipo novo;
- acento de "Súmula" na tela;
- BACK;
- tempo de carga.

## 5. O que falta para um candidato físico

1. **Ratificação:** o usuário ratifica os lotes que contêm tipos novos.
2. **Exportador:** passa a emitir as linhas com `TIPO` e `TRIBUNAL` via `juris_types.from_precedent`, e as fichas com o nome `TRIBUNAL_CLASSE_NUMERO.TXT`.
3. **Firmware:** gravação do firmware de tipos genéricos.
4. **Teste físico:** HC, MS, súmula do TSE e regressão RG/SV/ADI.
