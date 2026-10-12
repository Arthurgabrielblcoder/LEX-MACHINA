# C3B.1 — reclassificação documental do teste físico

**`C3B1_PHYSICAL_TEST = PASS_AFTER_EXPECTATION_CORRECTION`**
**`PHYSICAL_BEHAVIOR_MATCHES_AUTHORIZED_DECISIONS = 15/15`**

Este documento NÃO altera nenhum resultado físico. O registro original (`C3B1_PHYSICAL_TEST_REPORT.md`, `FAIL_RESIDUAL`, 12/15 PASS) continua intacto. O que muda é a **expectativa** de três testes, que estava errada.

## 1. Resultado originalmente registrado (preservado)

- **Testes 3 e 5:** `PARTIAL_FAIL_WRONG_DESTINATION_LC63`. A LC 63/1990 abre no art. 3º.
- **Teste 7:** `FAIL_LC109_STILL_PUBLISHED_AT_ART202_CAPUT`. A LC 109/2001 continua no caput do art. 202.
- **Os outros 12 testes:** PASS.

## 2. Descoberta posterior (auditoria C3B.2, `C3B2/C3B2_ROOT_CAUSE_REPORT.md`)

- **Testes 3 e 5:** o art. 3º vem das decisões humanas registradas.
  - C1A REPLACE no art. 161, I: rota `ABRIR_ARTIGO_INTERNO art. 3º`.
  - Retarget legado no art. 158, § 1º, I: `route_fix` com o art. 3º.
- **Teste 7:** o caput do art. 202 tem decisão humana própria (KEEP legado, art. 1º).
  - O § 1º é um HIGH independente (`CORRC0-362157C332DE`, target original § 1º, sem supersedes).
  - Não houve relação "movida" nem duplicação de materialização.
- O simulador do firmware reproduz exatamente o comportamento observado no cartão.

## 3. Decisão humana final e justificativa da reclassificação

Decisão humana final (2026-10-12): manter exatamente as decisões editoriais existentes.

1. CF art. 158, § 1º, I → LC 63/1990, art. 3º (salto intencional).
2. CF art. 161, I → LC 63/1990, art. 3º (salto intencional).
3. CF art. 202, caput → LC 109/2001, art. 1º (relação independente e válida).
4. CF art. 202, § 1º → LC 109/2001, art. 3º (relação independente; não consolidar).

O comportamento físico observado nos 15 testes é exatamente o que as decisões autorizadas determinam. As expectativas originais dos testes 3, 5 e 7 estavam equivocadas, e os resultados físicos não foram modificados retroativamente.

| Teste | Resultado original (preservado) | Comportamento conforme decisão autorizada |
|---|---|---|
| 1, 2, 4, 6, 8–15 | PASS | SIM |
| 3 | PARTIAL_FAIL_WRONG_DESTINATION_LC63 | SIM (art. 3º é a decisão) |
| 5 | PARTIAL_FAIL_WRONG_DESTINATION_LC63 | SIM (art. 3º é a decisão) |
| 7 | FAIL_LC109_STILL_PUBLISHED_AT_ART202_CAPUT | SIM (o caput tem decisão própria) |

## 4. Consequência para o C3B.2

- O C3B.2 tem bytes de aparelho idênticos, byte a byte, aos do C3B.1 testado: 6/6 SHA-256 e comparação direta.
- O teste físico C3B.1 é, portanto, evidência física válida para os bytes C3B.2.
- `SECOND_PHYSICAL_RETEST_REQUIRED = NO`, motivo `BYTE_IDENTICAL_TO_PHYSICALLY_TESTED_CANDIDATE`.
