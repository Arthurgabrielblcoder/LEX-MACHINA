# CORRELATAS 1 — Constituição Federal: camada congelada

```
LAYER = CORRELATAS_1_CF
STATUS = FROZEN_APPROVED_BASELINE
BASELINE = C3B.2
PHYSICAL_VALIDATION = PASS
FINAL_PHYSICAL_SMOKE = PASS
AUTOMATED_TESTS = 120/120
FIRMWARE_CHANGED = NO
FREEZE_DATE = 2026-10-12
REFERENCE_COMMIT = 74c6662005801025b4c082e1041440a84cdd9681
REFERENCE_TAG = lex-device-v1-correlata-c3b2-physical-approved-2026-10-12
```

## Evidência (já registrada no repositório)

- **Promoção física:** `DEVICE_INTEGRATION/C3B2_CORRELATA_PHYSICAL_BASELINE_APPROVED.md`, com evidência em `DEVICE_INTEGRATION/C3B2_CORRELATA_PROMOTION/`.
- **Manifesto físico aprovado:** `LEX_DEVICE_MANIFEST.json`, SHA-256 `6186c3574b0fd46dd4d7fe9ce74d6769587eaac33d017e7f02833b5fd829665a`.
- **Testes automatizados:** 120/120 em 12 suítes, no estado final do commit de promoção.
- **Teste físico do C3B.1** (bytes idênticos ao C3B.2):
  - `C3B1/C3B1_PHYSICAL_TEST_REPORT.md`;
  - reclassificação em `C3B1/C3B1_PHYSICAL_TEST_RECLASSIFICATION.md` (15/15 conforme as decisões autorizadas).
- **Smoke test físico final, após a promoção C3B.2** (informado pelo usuário): `C3B2_FINAL_BASELINE_PHYSICAL_SMOKE = PASS` e `CORRELATAS_1_CF_PHYSICAL_STATUS = APPROVED`. Confirmados:
  - boot normal;
  - CF art. 202, § 5º → LC 108/2001, art. 26;
  - CF art. 37, § 3º, III sem `1 CORR.` fantasma;
  - CF art. 158, § 1º, I → LC 63/1990, art. 3º;
  - CF art. 202, caput → LC 109/2001, art. 1º;
  - camadas não-CORRELATA sem regressão.

## Decisões editoriais finais preservadas

- CF art. 158, § 1º, I → LC 63/1990, art. 3º (salto intencional).
- CF art. 161, I → LC 63/1990, art. 3º (salto intencional).
- CF art. 202, caput → LC 109/2001, art. 1º.
- CF art. 202, § 1º → LC 109/2001, art. 3º.
  - As duas relações da LC 109 são independentes, não uma duplicação indevida.

## Correções estruturais incorporadas ao baseline

1. A flag `C` do `CF88_TARGETS.IDX` é coerente com as CORRELATAS publicadas no DEVICE_READY.
2. Os IDs de relação materializados resolvem 1:1 (`REFERENCE_ID` → exatamente uma linha do RELACOES).
3. Os `1 CORR.` fantasmas identificados fisicamente foram eliminados.
4. As rotas específicas estão corretas, incluindo CF art. 202, § 5º → LC 108/2001, art. 26.
5. As demais camadas e flags não relacionadas foram preservadas.
6. Os índices e o manifesto foram promovidos como baseline físico C3B.2.

## Significado de "frozen"

"Frozen" NÃO significa que a camada nunca poderá ser alterada. Significa:

- esta rodada de construção está encerrada;
- o C3B.2 é o baseline aprovado;
- nenhuma alteração oportunista deve ser feita enquanto se trabalha em outras camadas;
- mudanças futuras exigem uma nova missão aberta explicitamente;
- mudanças legislativas futuras podem justificar revisão;
- erros juridicamente comprovados também podem justificar reabertura;
- qualquer reabertura preserva a trilha histórica e parte do baseline C3B.2.

## Guardrail para as próximas rodadas

- **Trabalhos cobertos:** Referências nº 4, ENTENDA, Jurisprudência, outras normas, updater, firmware e outras funcionalidades.
- **Regra:** enquanto a camada estiver congelada, esses trabalhos NÃO devem modificar incidentalmente os dados aprovados de CORRELATAS 1 — CF.
  - Isso inclui as decisões, o registro, as adições e correções, os índices `RELACOES`/`REL_LOOKUP`/`EXT_ARTIGOS`, as linhas CORRELATA de `REF_*` e a flag C do `CF88_TARGETS.IDX`.
- **Se uma etapa futura exigir alterar esses bytes ou dados:** PARAR e tratar como reabertura explícita da camada. A reabertura nunca é automática.

```
NEXT_PLANNED_LAYER = REFERENCES_4_CF
```
