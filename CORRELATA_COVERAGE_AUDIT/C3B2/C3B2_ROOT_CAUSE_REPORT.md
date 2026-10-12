# C3B.2 — causa raiz das falhas residuais do C3B.1

- `C3B1_PHYSICAL_TEST` = `FAIL_RESIDUAL`
- `FULL_PASS` = `12/15`
- `PARTIAL_FAIL` = `2`
- `FAIL` = `1`
- `LC63_DESTINATION_ROOT_CAUSE` = `CONFIRMED`
- `LC63_CORRECT_DESTINATION_ART158` = `article (art. 3º)`
- `LC63_CORRECT_DESTINATION_ART161` = `article (art. 3º)`
- `ART202_CAPUT_LC109_ROOT_CAUSE` = `CONFIRMED`
- `ART202_CAPUT_LC109_SHOULD_EXIST` = `YES`
- `DEVICE_READY_EDITORIAL_MODE` = `24/24`
- `TARGET_DUPLICATION_AUDIT` = `PASS`
- `RELATIONS_CORRECTED` = `0`
- `C3B2_DEVICE_BYTES_EQUAL_C3B1` = `True`

## LC 63/1990 (testes 3 e 5)

- EXPECTATION_MISMATCH: as decisões humanas registradas fixam o art. 3º (C1A REPLACE "ABRIR_ARTIGO_INTERNO art. 3º"; retarget legado com route_fix art. 3º); o aparelho executa exatamente essa rota.
- Detalhe: `C3B2_LC63_ROUTE_AUDIT.md`.

## LC 109/2001 no caput do art. 202 (teste 7)

- EXPECTATION_MISMATCH: o caput tem decisão humana própria (KEEP legado, art. 1º); o § 1º é um HIGH independente (target original § 1º, sem supersedes); não é relação movida nem duplicação de materialização.
- Detalhe: `C3B2_ART202_LC109_AUDIT.md`.

## Auditorias globais

- **Modo de rota editorial × aparelho:** 24/24.
  - 23 vínculos de artigo específico e 1 de norma inteira.
  - Nenhum artigo inferido; nenhuma norma inteira transformada em artigo, nem o inverso.
- **Duplicidade de target:** `PASS`, com 5 grupos de mesma norma no mesmo artigo:
  - CF88:ART.155 × EXT_LC87_1996: ['CF88:ART.155:PAR.2:INC.VII', 'CF88:ART.155:PAR.2:INC.XII'] → INDEPENDENT_HUMAN_DECISIONS.
  - CF88:ART.161 × EXT_LC62_1989: ['CF88:ART.161:INC.II', 'CF88:ART.161:INC.III'] → INDEPENDENT_HUMAN_DECISIONS.
  - CF88:ART.202 × EXT_LC108_2001: ['CF88:ART.202:PAR.4', 'CF88:ART.202:PAR.5', 'CF88:ART.202:PAR.6'] → INDEPENDENT_HUMAN_DECISIONS.
  - CF88:ART.202 × EXT_LC109_2001: ['CF88:ART.202:PAR.1', 'CF88:ART.202:CAPUT'] → INDEPENDENT_HUMAN_DECISIONS.
  - CF88:ART.239 × EXT_LEI7998_1990: ['CF88:ART.239:PAR.3', 'CF88:ART.239:PAR.4'] → INDEPENDENT_HUMAN_DECISIONS.

## Simulador × hardware

- O simulador reproduz o estado físico observado no C3B.1:
  - LC 63 no art. 3º nos dois dispositivos;
  - LC 109 visível no caput e no § 1º (art. 3º);
  - os demais 12 testes com o resultado observado.
- **C3B.2:** nenhum defeito de dados, então nenhuma relação foi alterada (`RELATIONS_CORRECTED = 0`).
  - O pacote C3B.2 tem os MESMOS bytes de aparelho do C3B.1 e corrige só as expectativas do plano.
  - Firmware inalterado.

## Decisão pendente (humana)

- **Se as decisões registradas forem mantidas:** o C3B.1/C3B.2 cumpre as 15 expectativas corrigidas, e o próximo passo é a decisão de promoção. Antes de promover, é preciso regenerar o `LEX_DEVICE_MANIFEST.json`.
- **Se quiser a LC 63 no início da norma, ou sem a LC 109 no caput:** é uma nova decisão jurídica. Ela entra como decisão humana nos arquivos de decisão e gera outro candidato.

