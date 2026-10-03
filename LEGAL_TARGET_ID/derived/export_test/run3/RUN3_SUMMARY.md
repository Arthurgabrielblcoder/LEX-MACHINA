# Reference Engine RUN3 (CANDIDATO — pendente de revisão)

Derivado de: run2 + CF88_WORK_REFERENCE_ADDITIONS (REFERENCE_EXPANSION_01). RUN1 e RUN2 preservados byte a byte e reproduzidos pelo engine (run1 sem exclusões/adições; run2 sem adições): True.

| | RUN2 | RUN3 |
|---|---|---|
| Relações totais | 430 | 451 |
| Jurisprudências visíveis | 277 | 277 |
| Correlatas visíveis | 44 | 44 |
| WORK_REFERENCE | 101 | 122 |
| Hidden (HISTORICAL_HIDDEN_BY_DEFAULT) | 8 | 8 |
| Targets com obra | 43 | 63 |
| Artigos distintos da CF com obra | 18 | 33 |
| Artigos do ADCT com obra | 0 | 1 |
| Targets do ADCT com obra | 0 | 1 |

- Novos vínculos: **21** (todos WORK_REFERENCE do overlay; nenhum vínculo removido ou alterado).
- Targets validados: **21/21** (índice, CF88_RUNTIME, TARGETS CURRENT, alcançável por ACTIVE_TARGET, não filtrado).
- Tema 113 × CF88.25 e Tema 756 × CF88.31.3: ausentes (listados só em `excluded_links`): True.
- Determinismo (export, header candidato, staging DEVICE): {'export': True, 'header': True, 'staging': True}.
- Registry oficial: 69 → 73 obras (promovidas: EXP2-LIV-040, EXP2-FIL-039, EXP2-FIL-006, EXP2-FIL-038).
- Header rico candidato: `LEGAL_TARGET_ID/derived/export_test/run3/device_candidate/lex_ref_detail_data.RUN3_CANDIDATE.h` (122 fichas; 21 novas; as 101 do baseline mantidas). O header do firmware NÃO foi alterado.
- Staging DEVICE candidato: `DEVICE_INTEGRATION/staging_sd_v1_run3_candidate` (flags de 22 targets mudam; ENTENDA, texto e TEXT_MAP idênticos ao baseline).

## Vínculos adicionados

- `WORK_REFERENCE:EXP-DOC-005@CF88:ART.52:INC.I`
- `WORK_REFERENCE:EXP-DOC-006@CF88:ART.86:CAPUT`
- `WORK_REFERENCE:EXP-DOC-007@CF88:ART.231:CAPUT`
- `WORK_REFERENCE:EXP-DOC-008@CF88:ART.184:CAPUT`
- `WORK_REFERENCE:EXP-DOC-010@CF88:ART.182:CAPUT`
- `WORK_REFERENCE:EXP-FIL-006@CF88:ART.201:INC.I`
- `WORK_REFERENCE:EXP-FIL-007@CF88:ART.192`
- `WORK_REFERENCE:EXP-JOG-002@CF88:ART.62:CAPUT`
- `WORK_REFERENCE:EXP-JOG-003@CF88:ART.7:INC.XXXIII`
- `WORK_REFERENCE:EXP-JOG-004@CF88:ART.182:PAR.1`
- `WORK_REFERENCE:EXP-JOG-006@CF88:ART.215:PAR.1`
- `WORK_REFERENCE:EXP-LIV-001@CF88:ART.37:CAPUT`
- `WORK_REFERENCE:EXP-LIV-002@CF88:ART.37:CAPUT`
- `WORK_REFERENCE:EXP-LIV-003@CF88:ART.43:CAPUT`
- `WORK_REFERENCE:EXP-LIV-005@ADCT:ART.68`
- `WORK_REFERENCE:EXP-LIV-009@CF88:ART.145:PAR.1`
- `WORK_REFERENCE:EXP-SER-002@CF88:ART.144:PAR.7`
- `WORK_REFERENCE:EXP2-FIL-006@CF88:ART.134:CAPUT`
- `WORK_REFERENCE:EXP2-FIL-038@CF88:ART.144:PAR.5`
- `WORK_REFERENCE:EXP2-FIL-039@CF88:ART.58:PAR.3`
- `WORK_REFERENCE:EXP2-LIV-040@CF88:ART.43:PAR.2:INC.IV`

## Não feito nesta missão

- firmware nao alterado
- header do baseline nao substituido
- nada copiado para SD fisico
- sem flash
- sem merge com Batch04
- sem commit/tag/push
