# Content V2 — aprovação física do firmware

`CONTENT_V2_FIRMWARE_TECHNICAL = PASS`  
`CONTENT_V2_FIRMWARE_USER_VALIDATION = 13/13 PASS`  
`CONTENT_V2_FIRMWARE_PHYSICAL = APPROVED`  
`CONTENT_V2_PHYSICAL = PENDING_DATA_VALIDATION`

Em 2026-10-21, o gate técnico e o checklist humano **13/13** aprovaram fisicamente o parser/renderer Content V2 e sua compatibilidade com o estado legado. O firmware instalado tem SHA-256 `f7e6b1908e8c91c99582c377b6db3a46b06f18d4f59f2cddeb1b4666514b09f9` e 1.109.152 bytes.

- Flash exclusivo de `app0`, readback e boot: PASS.
- Tabela de partições, otadata e bootloader: inalterados.
- Parser V1 e fallback quando `FICHA_RELACAO` está ausente: PASS.
- Baseline preservado: CF/ADCT `315/198`; CC `55/45`; nenhuma relação massiva instalada.
- O gate de firmware não alterou o SD e não instalou dados Content V2.

Esta aprovação autoriza o gate físico separado dos seis fixtures Content V2. Ela não aprova os dados Content V2 completos, não autoriza mass deploy e não substitui a futura validação humana das seis fichas relation-specific.
