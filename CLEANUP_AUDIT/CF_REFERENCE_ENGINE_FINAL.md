# CF-REF-A3 — Motor de Referências da CF (fechamento)

**Resultado: `MOTOR_REFERENCIAS_CF_FECHADO = SIM` → `CF_REF_A3_CONCLUIDA — MOTOR_REFERENCIAS_CF_FECHADO`.**

- A CF-REF-A2 foi versionada nesta missão: commit `85597db407b755fd766df908df842bbb07bfa4bd`, tag `cf-references-canonical-2026-09-28`.
- Os artefatos da A3 estão **untracked**, para revisão.
- Não foram alterados: firmware, SD real, texto da CF, archives, protected545 e D05.

## 1. Quarentena original (56): resolvida só com evidência literal

| Classe | Registros | Explicação |
|---|---:|---|
| MIXED_RESOLVED_BY_SPLIT | 17 | A citação literal nomeia os dispositivos. São 22 vínculos (fan-out) com o mesmo `source_reference_id`; 5 registros geram mais de um alvo |
| MIXED_RESOLVED_VIA_CONSTITUENT_LINKS | 12 | Linhas de índice (`JUR_LOOKUP`) cujos vínculos constituintes estão todos no catálogo, resolvidos ou pendentes. O export reconstrói o índice a partir dos vínculos |
| MIXED_STILL_AMBIGUOUS | 0 | — |
| CROSS_NORM_REFERENCE_PENDING | 27 | Os 20 originais, mais 5 IDs e 2 linhas de índice das mistas, que citam outra norma |
| OTHER_QUARANTINE | 0 | — |
| **Total** | **56** | |

**Splits (fonte → alvos):**

| Fonte | Alvos |
|---|---|
| RG 969 | `CF88:ART.5:INC.II` + `INC.XIII` |
| RG 995 | `CF88:ART.5:INC.V` + `INC.X` |
| RG 160 | `CF88:ART.40:PAR.8` + `PAR.12` |
| RG 571 | `CF88:ART.40:PAR.1:INC.II` |
| RG 594 | `CF88:ART.40:PAR.4` + `PAR.5` (`wording_note`: cita redação anterior) |
| RG 966/976 | `CF88:ART.73:PAR.3`, `CF88:ART.75`, `CF88:ART.131`, `CF88:ART.134:PAR.2` |
| RG 147 / SV 17 | `CF88:ART.100:PAR.1` |
| RG 558 | `CF88:ART.100:PAR.9` + `PAR.10` |
| RG 647 | `CF88:ART.243:PAR.UNICO` |

**Gramática de citação (`citation_parser.py`, genérica e fail-closed):**

- **Aceita:**
  - subdivisão antes ou depois do artigo;
  - `§§`, parágrafo(s), parágrafo único;
  - incisos/incs., `caput e I`, romano solto após o artigo;
  - união do mesmo artigo citado mais de uma vez sob a mesma norma;
  - contexto `(CF, …)`;
  - norma decidida pelo primeiro marcador da frase, com parênteses removidos.
- **Rejeita** (AMBIGUOUS ou UNPARSEABLE):
  - "e seguintes" e intervalos ("I a IV");
  - alíneas;
  - subdivisão anterior não capturada;
  - o mesmo artigo sob normas diferentes;
  - vários parágrafos combinados com incisos;
  - ausência de contexto de norma.
- **Nunca** expande "art. 5º" em caput mais incisos.

**Outras normas (`CROSS_NORM_PENDING.json`, 27, preservadas fora do catálogo da CF).** Cada registro traz `cited_norm_label`, `cited_device_text`, `original_source` e `original_record_id`:

- Código Civil, Código Penal, Código Penal Militar;
- EC 41/2003 (antecedente de "seu art. 7º"), EC 47/05, EC 113/2021;
- LC 35/79;
- Leis 6.880/1980, 8.625/1993, 8.742/1993, 8.870/1994, 9.472/1997 e 10.259/2001.

Não foram mapeadas para `target_id` de outras normas, que ainda não foram canonicalizadas.

## 2. Históricos, duplicatas e visibilidade

- **Visibilidade:** `HISTORICAL_ONLY` → `visibility = HISTORICAL_HIDDEN_BY_DEFAULT`; os demais → `CURRENT_VISIBLE`, com o status preservado (CURRENT, STRUCTURAL, UNKNOWN_VALIDITY).
- **No export:** 8 vínculos históricos, ocultos por padrão, e 424 visíveis. `get_references(..., include_historical=True)` devolve os históricos. Exemplo: `CF88:ART.40:PAR.4:INC.II` tem 0 visíveis e 3 com `include_historical=True`.
- **As 9 possíveis duplicatas da A2:** todas são `MULTI_ROUTE_DISTINCT_PROVENANCE` (núcleo e/ou evidência diferentes), sem nenhum registro repetido.
  - RC2 (4 pares): o export agrupa `(target, work_id)` num vínculo com `routes[]`, preservando cada rota.
  - RC1 (5 pares): fica fora do export, porque foi superado pelo RC2.

## 3. Pipeline atual e ponto de integração

| Etapa | Obras | Jurisprudência | Correlatas |
|---|---|---|---|
| Fonte | V2 R1D1 → `REFERENCIAS_RC2.json` | J4 `VINCULOS_EXPLICITOS.json` | Relations V2 / 2E4.1 `RELACOES_CF88.json` |
| Exportador atual | **não existe** (firmware: tela REFERÊNCIAS provisória) | `preparar_staging_j4_6.py` → `99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX` + `JURISPRUDENCIA.IDX` | 2E5 + montador 2E6 → `99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX` + `RELACOES.IDX` |
| Firmware (v7.12.0 baseline) | — | lookup `norma\|art\|par\|inc\|ali` + offset | idem |

**Integração.** `LEGAL_TARGET_ID/reference_engine.py` é um adapter genérico entre o catálogo canônico e o SD. Ele emite o **mesmo padrão lookup+offset já usado pelo firmware**, mas com chave `target_id`. Não foi criado um "V3" paralelo: as fontes e o parser existentes continuam, e o motor só substitui a chave e a etapa de export.

## 4. Modelo genérico e gate

- **Vínculo:** `norma_id`, `target_id`, `reference_id`, `reference_type` (WORK_REFERENCE, JURISPRUDENCE ou CORRELATA), `source_id`, `source_reference_id`, `provenance`, `status`, `visibility`, `label`, `payload`, `validation_status`, `routes`, `migration`, `duplicate_class`.
- **Configuração:** `engine_config.json` (norma → índice, status, catálogo, resolução). O motor **não tem CF88 no código** (teste automático).
- **Gate `validate_link()`** (fail closed), aplicado a 100 % dos vínculos:
  - `validate_target_id`;
  - `target_exists_for_norm(norma_id, target_id)`;
  - campos obrigatórios.

## 5. Export (derivado; SD não tocado)

| Arquivo (`LEGAL_TARGET_ID/derived/export_test/run1/`) | Bytes | SHA-256 |
|---|---:|---|
| `CF88_REFERENCES_EXPORT.json` (agrupado por `target_id`, ordem estrutural) | 416.519 | `004df87b0977b6f8624d7edf349d3d4b6ae60ad2016bbdba020aa8fe5ba67a89` |
| `REF_LOOKUP.IDX` (`TARGET_ID\|OFFSET\|QUANTIDADE`, ordenado por ASCII) | 6.579 | `9665fb854fe5b91fc5a1aa640b6eb8270583e3c6414720e99f37f9608ccb3c12` |
| `REF_PAYLOAD.IDX` (`TARGET_ID\|TIPO\|VISIBILIDADE\|STATUS\|REFERENCE_ID\|SOURCE_ID\|LABEL`) | 65.546 | `1c772c83b6cfe381ddb1674b73126dbf2fb6cf354fe16d708194cdad0de94228` |

- **Determinismo:** duas execuções geraram os mesmos arquivos, byte a byte (confirmado também em teste).
- **Alvos sem referência** não geram payload; o lookup devolve vazio.

**Métricas:**

| Métrica | Valor |
|---|---|
| Alvos com referências | 242 |
| Vínculos | 432 (101 obras, 285 jurisprudência, 46 correlatas) |
| Máximo de vínculos por alvo | 10 (`CF88:ART.37:INC.XI`) |
| Média / mediana | 1,79 / 1 |
| Maior payload | 1.583 bytes |
| Maior `target_id` exportado | 26 caracteres |

**Recomendação para ESP32/SD:** índice + payload por norma (o padrão atual), com o namespace no próprio `target_id`. Busca binária no lookup (6,6 KB) e seek no payload. Não carregar o JSON. Segmentar por norma quando houver 72.

## 6. Corpus-ouro end-to-end: PASS

**Rastro:** registro-fonte → `target_id` canônico → referência normalizada → export → lookup (JSON e IDX binário, iguais em todos os casos).

| Artigo | Vínculos | Tipos |
|---|---:|---|
| CF88:ART.1 | 13 | 7 obras, 6 jurisprudência |
| CF88:ART.5 | 61 | 33 obras, 27 jurisprudência, 1 correlata |
| CF88:ART.37 | 31 | 27 jurisprudência, 4 correlatas |
| CF88:ART.60 | 0 | — |
| CF88:ART.150 | 22 | 21 jurisprudência, 1 correlata |
| CF88:ART.225 | 2 | 2 obras |
| ADCT:ART.5 | 0 | — |

**Lookups obrigatórios:**

| Alvo | Resultado |
|---|---|
| `CF88:ART.37:PAR.6` | 5 vínculos de jurisprudência |
| `CF88:ART.37:PAR.10` | 0 |
| `CF88:ART.60:PAR.4:INC.IV` | 0 |
| `ADCT:ART.5` | 0 |
| `CF88:ART.5` (artigo) | 0 |
| `CF88:ART.5:CAPUT` | 3 (obras e jurisprudência) |

**Sem colisão:**

- `ADCT:ART.78:PAR.4` tem 1 vínculo;
- `CF88:ART.78:PAR.4` não existe (nem no índice, nem no lookup);
- CF art. 5 e ADCT art. 5 devolvem resultados distintos.

## 7. Generalização

Um teste com a norma sintética **CDC1990** faz o ciclo completo:

- Art. 6º, VI e parágrafo único, com índice gerado pelo parser genérico;
- catálogo sintético, links, rotas múltiplas, export e lookup;
- determinismo;
- fail-closed para `CF88:…` sob CDC1990, alvo inexistente e norma não configurada.

Nenhuma outra norma real foi migrada.

## 8. Contrato de firmware (não implementado)

**`FIRMWARE_NAMESPACE_FIX_REQUIRED = true`.**

| Item | Contrato |
|---|---|
| Entrada | `target_id` canônico (ASCII, sem espaço) com namespace obrigatório (CF88, ADCT, CDC1990…) |
| Tamanho | Máximo observado 35 (índice) / 26 (exportado); buffer recomendado `char[48]` (a gramática limita a 64) |
| Lookup | Busca binária em `REF_LOOKUP.IDX` (`TARGET_ID\|OFFSET\|QUANTIDADE`) e leitura de QUANTIDADE linhas em `REF_PAYLOAD.IDX` a partir de OFFSET |
| Chave de contexto | O `target_id` do dispositivo sob o cursor, com o caput como `…:CAPUT`. **Acaba a chave `artigo\|paragrafo\|inciso\|alinea` sem norma** |
| Fallback | Sem linha exata: ancestrais estruturais (INC → PAR/CAPUT → ART) só para navegação visual, marcados como "herdado"; **nunca** trocar namespace; esconder `HISTORICAL_HIDDEN_BY_DEFAULT` |

## 9. Contrato ADCT (não implementado no SD)

**`OPERATIONAL_CF_TEXT_MISSING_ADCT = true`.**

- **Plano:** texto principal da CF mais um **arquivo ADCT separado** (namespace ADCT) na pasta da CF.
- **Export:** já trata `ADCT:ART.n` como namespace distinto.

## 10. Checklist MOTOR_FECHADO (12/12)

- [x] `target_id` canônico
- [x] fontes normalizadas
- [x] inválidos em quarentena
- [x] fan-out de citações mistas
- [x] históricos separados
- [x] validação obrigatória
- [x] export determinístico
- [x] lookup funciona
- [x] corpus-ouro passa
- [x] ADCT não colide
- [x] motor generalizável
- [x] nenhuma referência inválida silenciosa

**Testes:** 47/47 OK. São 18 da A1, 13 da A2 e 16 da A3; os da A3 cobrem fan-out, outras normas, visibilidade histórica, rotas múltiplas, gate, ADCT, lookup do corpus-ouro, export determinístico e a fixture não-CF.

## 11. Arquivos da A3 (untracked)

| Arquivo | Conteúdo |
|---|---|
| `LEGAL_TARGET_ID/citation_parser.py` | Gramática de citação |
| `LEGAL_TARGET_ID/resolve_quarantine.py` | Resolução da quarentena |
| `LEGAL_TARGET_ID/reference_engine.py` + `engine_config.json` | Motor genérico e configuração |
| `LEGAL_TARGET_ID/engine_e2e.py` | Prova end-to-end |
| `LEGAL_TARGET_ID/tests/test_reference_engine.py` | Testes da A3 |
| `LEGAL_TARGET_ID/derived/CF88_QUARANTINE_RESOLUTION.json`, `CROSS_NORM_PENDING.json`, `CF88_ENGINE_E2E.json` | Resolução, pendências e E2E |
| `LEGAL_TARGET_ID/derived/export_test/run1/` | Export (3 arquivos) |
| `CLEANUP_AUDIT/CF_REFERENCE_ENGINE_FINAL.md` / `.json` | Este relatório |

## 12. Próximo passo (não iniciado)

1. Versionar a A3 depois da revisão.
2. Implementar no firmware a chave com namespace e a leitura de `REF_LOOKUP`/`REF_PAYLOAD`, e produzir o arquivo ADCT separado (fonte monovigente).
3. Canonicalizar a próxima norma (estrutura + `target_id`) e mapear as 27 pendências de outras normas quando a norma citada existir.
4. Só depois disso, iniciar o ENTENDA sobre o mesmo `target_id`.
