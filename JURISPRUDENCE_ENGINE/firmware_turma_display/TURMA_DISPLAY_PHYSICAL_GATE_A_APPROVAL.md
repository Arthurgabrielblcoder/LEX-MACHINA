# Turma Display — aprovação física Gate A

`FIRMWARE_GATE_A_PHYSICAL = APPROVED`  
`TURMA_DISPLAY_PHYSICAL = PENDING_PHASE_B`

Em 2026-10-19, o gate técnico e o checklist humano **20/20** aprovaram apenas a regressão do firmware e sua compatibilidade com o formato legado. O firmware físico é `e2945cf55a00f27f6c35ff709e81732d804fd8c6f01958230cef0016f740a4a0` (LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin, 1.109.120 bytes).

- Baseline preservado: CF/ADCT `315/198`; CC `49/39`; nenhuma das 653 relações instalada.
- Flash, readback e boot: PASS; tabela de partições, otadata e bootloader: inalterados.
- Parser legado de oito colunas: PASS.
- O SD não foi alterado pelo gate.
- Nenhum dado de Turma foi fisicamente testado. A aprovação do renderer depende do fixture da Fase B.
