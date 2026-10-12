# C3B.2 — LC 109/2001 no art. 202 (caput × § 1º)

| Item | `CF88:ART.202:CAPUT` | `CF88:ART.202:PAR.1` |
|---|---|---|
| flags (TARGETS) | -C--R- | -C---- |
| query keys do aparelho | ['CF88:ART.202', 'CF88:ART.202:CAPUT'] | ['CF88:ART.202:PAR.1'] |
| REF_PAYLOAD (LC 109) | [['CF88:ART.202:CAPUT', 'CORRELATA', 'CURRENT_VISIBLE', 'CURRENT', 'CORRELATA:REL_E3E07057AD3E162C@CF88:ART.202:CAPUT', 'EXT_LC109_2001']] | [['CF88:ART.202:PAR.1', 'CORRELATA', 'CURRENT_VISIBLE', 'CURRENT', 'CORRELATA:REL_301AD05C48332703@CF88:ART.202:PAR.1', 'EXT_LC109_2001']] |
| REFERENCE_ID | ['CORRELATA:REL_E3E07057AD3E162C@CF88:ART.202:CAPUT'] | ['CORRELATA:REL_301AD05C48332703@CF88:ART.202:PAR.1'] |
| RELACOES resolvida | `CORRELATA:REL_E3E07057AD3E162C@CF88:ART.202:CAPUT` → RELACOES `CF88|202||||REL_E3E07057AD3E162C|…|ABRIR_ARTIGO_INTERNO|1` → offsets {'1': 308} | `CORRELATA:REL_301AD05C48332703@CF88:ART.202:PAR.1` → RELACOES `CF88|202|1|||REL_301AD05C48332703|…|ABRIR_ARTIGO_INTERNO|3` → offsets {'3': 884} |
| status | ['CURRENT_VISIBLE'] | ['CURRENT_VISIBLE'] |
| decisão humana | LEGACY_FULL_REVIEW KEEP `LEGACY:LEGACY_FULL_REVIEW:CORRELATA:REL_E3E07057AD3E162C@CF88:ART.202:CAPUT` | HIGH ['CORRC0-362157C332DE'] |
| origem RUN4 | LEGACY KEEP (estado DEVICE_READY) | ADDITION (registro `REL_301AD05C48332703`; supersedes []) |
| artigos destino | ['1'] | ['3'] |

- **Classificação** (opções A a G da missão): nenhuma delas como defeito.
  - O caput tem REF, PAYLOAD e RELACOES próprios porque existe decisão humana própria (KEEP legado, art. 1º).
  - O § 1º é outra decisão humana (HIGH com target original no § 1º), não um retarget do caput.
  - Não há herança: o § 1º não usa a chave do caput.
  - Não há duplicação de materialização: as decisões são disjuntas e nenhuma relação substitui a outra.
- **`ART202_CAPUT_LC109_SHOULD_EXIST = YES`.**
  - O plano C3B.1 já registrava, no teste 6: "o caput continua com a LC 109 no art. 1º".
  - Remover exigiria uma nova decisão jurídica.

