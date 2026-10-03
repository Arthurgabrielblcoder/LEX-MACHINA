# BATCH04 + RUN3 — plano de diff do SD (NÃO EXECUTADO)

Origem do candidato: `DEVICE_INTEGRATION/staging_sd_v1_batch04_run3_candidate/SD/99_LEX_V1/`. Gerado por `tools/build_batch04_run3_candidate.py` (perfil `BATCH04_RUN3`); a reconstrução é byte-identical.

SD físico conhecido: manifesto `backups/cc_index/sd_manifest_post.json`, gerado em 2026-10-03 logo depois da cópia de `CC2002_ARTICLE_SEARCH.IDX`.
- **Total:** 1.071 arquivos — 11 em `/99_LEX_V1` e 1.060 fora.
- **`/99_LEX_V1` físico:** é exatamente o `staging_sd_v1` aprovado (9 arquivos, todos iguais) mais os 2 índices de artigo validados.

**Pré-condição da fase B do plano físico:** reconfirmar este estado com um manifesto novo do cartão. Se algum hash divergir do que está abaixo, PARAR: o diff precisa ser refeito.

## Resultado

| Ação | Arquivos |
|---|---|
| **REPLACED** | 7 |
| **UNCHANGED** | 4 |
| **ADDED** | 0 |
| **REMOVED** | 0 |
| Arquivos fora de `/99_LEX_V1` (Lei Seca legada, `99_RELATIONS_V2`, `99_JURISPRUDENCIA_V2`, índices antigos, inventário) | **1.060 intocados** |

Nenhum arquivo legado é removido, e nenhum arquivo é criado fora de `/99_LEX_V1`.

## Arquivo a arquivo (`/99_LEX_V1/...`)

| Ação | Arquivo | Bytes no SD físico | SHA256 no SD físico | Bytes no candidato | SHA256 no candidato | Motivo |
|---|---|---|---|---|---|---|
| REPLACED | `00_SYS/LEXV1.VER` | 600 | `7c4b1a971b3e2178…` | 588 | `6e713989d5693e7aa59565a5c7ae73d39788acae7fd89cb5ea15b71bbec311f6` | ENTENDA_COUNT 220, novo escopo, REFERENCE_ENGINE run3, BUILD_ID |
| REPLACED | `00_SYS/LEX_DEVICE_MANIFEST.json` | 6.391 | `d2ab919f3e95de6e…` | 7.604 | `25fceb1e99759c9aa115f9ec323daf1802602ef3f09beebe30de4d2eb31a6b9a` | manifesto do pacote consolidado |
| UNCHANGED | `05_TEXT/CF88_RUNTIME.txt` | 587.133 | `7ef82290d30f4af1…` | 587.133 | `7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a` | Lei Seca / CF / ADCT: não muda |
| UNCHANGED | `10_TARGETS/CC2002_ARTICLE_SEARCH.IDX` | 25.036 | `674c9971925c29aa…` | 25.036 | `674c9971925c29aaca9685fb2d0b9515fe87e4072d644858ea27495c327d3a68` | índice fisicamente validado |
| UNCHANGED | `10_TARGETS/CF88_ARTICLE_SEARCH.IDX` | 5.216 | `56e437a0c9cebb11…` | 5.216 | `56e437a0c9cebb113c47f6a7b100ee64363c63207a647eca0456e86d6db27fae` | índice fisicamente validado |
| REPLACED | `10_TARGETS/CF88_TARGETS.IDX` | 165.466 | `36db8b871163262d…` | 165.466 | `5eb2da36ff01a7e5cc976e3b7d3eabc8999b95ae8d4b5932f752501af351b980` | flags E/B (Batch04) e W (RUN3) |
| UNCHANGED | `10_TARGETS/CF88_TEXT_MAP.IDX` | 123.578 | `889f82002e82fb2b…` | 123.578 | `889f82002e82fb2b7d9165e6ce2a4e0dcb78d311432e268c341f1d0b1e436b96` | mapa offset → target: não muda |
| REPLACED | `20_REFERENCES/REF_LOOKUP.IDX` | 6.579 | `9665fb854fe5b91f…` (RUN1) | 6.955 | `6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8` | RUN3 |
| REPLACED | `20_REFERENCES/REF_PAYLOAD.IDX` | 65.546 | `1c772c83b6cfe381…` (RUN1) | 68.075 | `24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea` | RUN3 |
| REPLACED | `30_ENTENDA/ENTENDA_LOOKUP.IDX` | 30.462 | `93613275d4e0caf9…` | 38.700 | `3014442e2da813215fa701aa67006e37cc59945bc280f632fedf056165370d21` | +57 explicações do Batch04 |
| REPLACED | `30_ENTENDA/ENTENDA_PAYLOAD.DAT` | 302.915 | `a7511b917f658fd4…` | 404.510 | `4efa54788fc468d1355b6d7937b3bd88a7c8c88f5a4a0dd20760082238b1e516` | +57 explicações; as 163 anteriores ficam byte-identical |

**Bytes a escrever no cartão (7 arquivos):** 588 + 7.604 + 165.466 + 6.955 + 68.075 + 38.700 + 404.510 = **691.898 B**.

## Rollback do SD

1. Antes de substituir, copiar os 7 arquivos atuais para `backups/batch04_run3/sd_pre/99_LEX_V1/…` (os hashes devem bater com a coluna "SD físico" acima).
2. Se for preciso voltar: restaurar esses 7 arquivos e conferir o manifesto inteiro contra `sd_manifest_post.json`.

O schema do pacote continua 3, então firmware e SD podem ser revertidos de forma independente sem falha de carga. Uma combinação mista exibe dados incompletos:
- **SD RUN3 + firmware antigo:** as 21 obras novas aparecem na camada 4, mas sem o detalhe rico, porque o header antigo não as tem.
- **SD antigo + firmware novo:** o header traz detalhes de obras que o REF do RUN1 não lista.

Por isso o par recomendado é sempre o par completo (SD consolidado + `candidate_app_batch04_run3.bin`), ou o par anterior completo.
