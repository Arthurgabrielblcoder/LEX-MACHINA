# CC-J1 — preflight de materialização

```
CC_J1_PREFLIGHT = PASS · HOST-ONLY · NADA ESCRITO NO CARTÃO · NADA GRAVADO NO ESP32
CANDIDATO = JURISPRUDENCE_ENGINE/CC_J1_MATERIALIZATION_CANDIDATE/ (build 4c0615575e3da8fc)
SHA256_MANIFEST.json = 71f9eb76a3c8458357d20f2ef697006991347ff109a3cea214015a3c63e95ccc
```

Gerador: `build_cc_j1_materialization.py` (`--check` reprodutível). Testes: `tests/test_cc_j1_materialization.py`.

## 1. Fonte autoritativa

`CC_J1_RATIFICATION_RECORD.json`. Os hashes fixados nele (propostas, dossiê e índice STJ) foram reconferidos: **CCJ1_RATIFICATION_RECORD_VALID = PASS**. As propostas são 22 aprovadas, 2 pendentes e 6 não aprovadas.

As relações são **recalculadas** a partir dos targets finais do registro e conferidas com `approved_relations`. Se houvesse divergência, o gerador pararia com `PREFLIGHT_STOP`.

## 2–4. Relações, targets e precedentes

| Item | Valor |
|---|---|
| Relações CC2002 | **29** (exatamente as ratificadas) |
| Targets CC2002 com J | **24**. Todos existem no índice CC2002, com estrutura conferida (namespace, artigo, parágrafo, inciso, alínea, tipo) e vigentes no texto oficial; nenhum revogado |
| Precedentes distintos | **20** (STF 7: ADI 4815, ADI 6792/7055, Temas 498, 809, 529, 1236 e 932; STJ 13 súmulas) |
| Excluídos | Pendentes CCJ1-09 (Tema 1194) e CCJ1-30 (Súmula 609); não aprovados CCJ1-08, 16, 19, 24, 26 e 28 → `PENDING_MATERIALIZED = 0`, `REJECTED_MATERIALIZED = 0` |

**Casos especiais conferidos:**

| Precedente | Targets | Ficha |
|---|---|---|
| ADI 6792/7055 | 186, 927 | Ficha **conjunta** `STF_ADI_6792-7055.TXT`, com seção "JULGAMENTO CONJUNTO"; não há fichas separadas por ADI |
| Tema 932 | 927, p.u. | `STF_RG_932.TXT` já está no cartão (CF), sha `7bd33933…`. **Reaproveitada, não copiada** |
| Súmula 403 | 186, 927 | Uma ficha |
| Súmula 405 | 206, § 3º, IX; 2.028 | Nota DPVAT e revalidação |
| Súmula 476 | 662, 917 | Sem o art. 186 |
| Súmula 496 | 99, 1.231 | Contexto: terrenos de marinha / União |
| Súmula 547 | 2.028; 206, § 3º, IV; 206, § 5º, I | `CC1916_TO_CC2002` |
| Súmula 585 | 1.226, 1.267 | Contexto: veículo / IPVA / tradição |

## 5. Fichas

- **Total:** 20 fichas lógicas: **19 novas** e **1 reaproveitada** (Tema 932). `DUPLICATED_SHARED_FICHAS = 0`, `FICHA_ID_COLLISIONS = 0`.
- **Nomes:** seguem a regra do firmware, `TRIBUNAL_CLASSE_NUMERO.TXT`; o julgamento conjunto vira `STF_ADI_6792-7055`.
- **Conteúdo** (somente evidência ratificada):
  - tribunal, status, órgão ou processo;
  - enunciado ou resumo e trecho oficial;
  - julgamento e publicação;
  - dispositivos do CC relacionados;
  - notas aprovadas (Temas 498/809: art. 1.790 declarado inconstitucional; Tema 1236: trânsito em julgado em 10/04/2024; Súmulas 405, 496, 499, 547 e 585: contexto);
  - fonte oficial.
- **Sem banner de simulação:** nenhuma ficha traz "SIMULAÇÃO".

## 6. Flags

- **No cartão:** não existe índice de flags de camada para o CC2002. O firmware multinorma decide pela presença da chave no lookup.
- **Projeção host:** as flags J foram preparadas no mesmo esquema de 6 flags da CF (`host/CC2002_J_FLAGS.json`): **J em 24 targets; `NON_J_FLAG_CHANGES = 0`**.
- **CF:** o `CF88_TARGETS.IDX` da CF **não é alterado**, e as flags de Correlatas, Referências e ENTENDA não mudam.

## 7. Índices (camada `99_JURISPRUDENCIA_V2/06_NORMALIZADO/`)

| Arquivo | Linhas | Bytes | Observação |
|---|---:|---:|---|
| `JUR_LOOKUP.IDX` | 222 (1 + 221 chaves) | 4.734 | **0 chaves duplicadas** |
| `JURISPRUDENCIA.IDX` | 345 (1 + 344 registros) | 63.241 | CF88 311 + ADCT 4 + CC2002 29 |
| `MULTINORM_MANIFEST.json` | — | 4.003 | Contagens por norma |
| `LAYER.VER` | — | 277 | Build, baseline e sha da ratificação |
| 19 fichas novas | — | 11.550 | — |

**Manifesto por norma:**

| Norma | Relações / targets | Precedentes | Fichas | Tipos | Tribunais |
|---|---|---|---|---|---|
| CF88 | 311 / 194 | 254 | 254 | adi 17, adpf 3, ai 1, ap 1, hc 2, inq 2, ms 3, rcl 1, RG 209, súmula 2, SV 13 | STF 253, TSE 1 |
| ADCT | 4 / 4 | 4 | 4 | adi 3, RG 1 | STF 4 |
| CC2002 | 29 / 24 | 20 | 20 | adi 2, RG 5, súmula 13 | STF 7, STJ 13 |

- **Soma da CF:** CF88 + ADCT = **315/198**; nenhuma relação da CF desapareceu ou surgiu.
- **Fichas compartilhadas entre namespaces:** `STF_RG_932` (CF e CC) e `STF_ADI_7047-7064` (CF e ADCT).

## 8. Hashes

`SHA256_MANIFEST.json` lista os 27 arquivos do candidato (camada, fichas e relatórios host) com bytes e sha256, mais a ficha reaproveitada do cartão. Há proteção `-text` no `.gitattributes`, porque os offsets dependem dos bytes.

## 9. Simulação (modelo das funções C do firmware multinorma)

- **CC:** `CC_TARGETS_E2E = 24/24 PASS`. O fluxo testado em cada target foi: abrir a norma, localizar o target, abrir JURIS., conferir a lista completa, abrir cada ficha, BACK para a mesma lista e voltar ao dispositivo.
- **Relações e perdas:** `CC_RELATIONS_VISIBLE = 29/29`; `LOOKUP_LOST_RELATIONS = 0`.
- **Rótulos:** RG/STF 5, ADI/STF 4, Súmula/STJ 20 ocorrências; `UNKNOWN_TYPE_LABELS = 0`, sem "OUTRO" e sem tribunal trocado.
- **CF:** `CF_REGRESSION = PASS`; todas as chaves da CF são idênticas ao pacote só com a CF.
- **Pendentes:** Tema 1194 e Súmula 609 não aparecem.

## 10. Cache

| Item | Valor |
|---|---|
| CACHE_ENTRIES_USED | **221** (lookups) |
| CACHE_ENTRIES_MAX | 4096 (5,4% usados) |
| PSRAM_ESTIMATED | **78.270 B** (221 × 68 B + 63.241 B + 1) |
| Firmware multinorma | programa +5.332 B, RAM +40 B, app0 livre 203.216 B (`firmware_multinorm/MULTINORM_PROTOTYPE_BUILD.json`) |

## 11. Rollback futuro (não executado; `host/ROLLBACK_PLAN.json`)

O candidato **só acrescenta arquivos**: a camada `06_NORMALIZADO` e 19 fichas. Nenhum arquivo existente do cartão é modificado (`EXISTING_CARD_FILES_MODIFIED = 0`).

**Para remover só o CC:**
1. Apagar os arquivos acrescentados (lista no plano).
2. Conferir o cartão contra `J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json` (1190 arquivos).

**Por que isso preserva a CF:**
- não há arquivos a restaurar nem flags no cartão;
- sem a camada normalizada, o firmware multinorma volta aos índices legados, e a CF segue pela LEXV1.

**Firmware:** o rollback é independente dos dados (app J2I `1371e69a…`).

## 12. Ordem segura de deploy futuro (obrigatória; nada executado)

1. **Gravar o firmware multinorma**, mantendo o cartão J2I atual **sem** o CC.
2. **Teste físico completo de regressão da CF** com o firmware multinorma.
3. **Só depois, deploy do candidato CC-J1** no cartão (acrescentar os 23 arquivos de `candidate/SD/` e conferir os hashes do `SHA256_MANIFEST.json`).
4. **Teste físico do Código Civil.**

Firmware novo e dados novos nunca entram juntos.
