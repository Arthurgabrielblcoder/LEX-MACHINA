# Política protected545 — V2 (adendo de realocação)

**Status: `OPERATOR_APPROVAL_RECORDED` — 2026-09-28.**

Este adendo não revoga nem reescreve a política histórica `CLEANUP_AUDIT/PROTECTED545_POLICY.md`. Ela continua como registro do que valia antes. Sua regra era: os 545 arquivos devem permanecer byte a byte idênticos e **exatamente nos paths atuais**; mover, renomear, deduplicar, arquivar ou editar tornava a prova inverificável e era proibido sem nova autorização explícita.

## Histórico

1. **ONDA 0 a 2E.** A realocação de qualquer membro protected545 estava proibida. Os 55 candidatos que contêm membros protected545 ficaram na raiz.
2. **P545A** (`CLEANUP_AUDIT/P545_RELOCATION_ANALYSIS.md`, `P545_SANDBOX_PROOF.json`). Validou em sandbox externo uma prova **derivada** de realocação:
   - ledger append-only com cadeia de hash;
   - verificador derivado;
   - visão legada reconstruída;
   - 23 testes unitários e 11 cenários negativos, todos falhando de forma explícita.
3. **Aprovação do operador**, registrada textualmente abaixo.

## Autorização do operador (texto literal)

> "Aprovo a nova política de relocação do protected545 e autorizo a execução da P545E para os 29 candidatos já comprovados como relocáveis, mantendo rollback, hashes e sem mover os candidatos com discovery dinâmica, dependências múltiplas ou ativos."

- **Registro:** aprovação dada em texto na sessão de trabalho de 2026-09-28. Não há assinatura digital; este documento e o commit que o contém servem de registro.
- **Escopo:** somente os 29 candidatos dos lotes P545E_1 (16 "P545-only") e P545E_3 (13 "P545 + IDX_RELOCATABLE_WITH_PARENT") em `CLEANUP_AUDIT/P545_RELOCATION_ANALYSIS.json`, somando 2.857.446.527 bytes.
- **Fora da autorização:**
  - os 12 candidatos P545 + descoberta dinâmica (D01);
  - os 2 com bloqueios múltiplos (2E5 e 2E6);
  - os 12 ativos;
  - 2E41 e qualquer outro diretório.

  Estender a autorização exige nova aprovação explícita.

## Regras

1. **A prova original é imutável.** `LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/INTEGRITY_BEFORE.json` (SHA-256 `a319f0ea917b0e6c00e037ba5b7a5c97b351d1b0af00b79862ae98db7cfd91c2`) nunca é editado, regenerado ou substituído.
2. **O ledger de realocação é prova derivada** (`PROTECTED545_RELOCATION/ledger/`, formato de `relocation_ledger.py` e do schema). Ele acrescenta informação à prova original e nunca a substitui.
3. **Os eventos são append-only** (RELOCATE ou ROLLBACK), com `prev_event_hash`, `event_hash` e `head`. O head é ancorado em commit ou tag a cada lote. Um evento registrado nunca é editado; correções entram como novos eventos.
4. **A lineage precisa ser unívoca.** Não pode haver ramificação, ciclo, cópia remanescente no local anterior nem colisão casefold/NFC entre localizações correntes.
5. **Hash não define a ocorrência sozinho.** Identidade = ocorrência histórica da prova original (path original + SHA-256 + tamanho), com `occurrence_id` derivado desses três campos.
6. **O verificador derivado é obrigatório** (`verify_relocation.py`). O estado vivo é aceito somente com:
   - `result = PASS`;
   - MISSING, HASH_MISMATCH, AMBIGUOUS_RELOCATION e INVALID_LINEAGE iguais a 0.
7. **A visão legada é obrigatória para ferramentas congeladas** (`materialize_legacy_view.py`).
   - `r1d_support.integrity()` e as demais ferramentas congeladas da V2 (e do D05, como `enriquecer_v1.py` e `gerar_manifest.py`, que têm descoberta histórica de IDX) só rodam sobre a visão reconstruída fora do repo (`HISTORICAL_TOOL_REQUIRES_LEGACY_VIEW`).
   - No repo vivo, a falha delas por ausência do path original é **esperada** e não é corrupção.
8. **Rollback exato é obrigatório.** Todo move preserva o path relativo sob o archive root. O rollback é um evento ROLLBACK, do archive para o path original exato, com hash e inventário conferidos.
9. **Inventário antes do move.** Nada é movido sem inventário completo (path relativo, tamanho e SHA-256 de cada arquivo) e sem hash determinístico do inventário.
10. **Identidade de bytes depois do move.** O inventário pós-move precisa ser 100 % idêntico: contagem, tamanho, conjunto de paths, SHA-256 e hash do inventário.
11. **Qualquer divergência bloqueia o lote seguinte.** Isso inclui divergência de ledger, prova, visão legada, IDX ou lineage.
12. **O archive não é backup.** `C:\LMA\p545e\20260928` está no mesmo volume C:, então o espaço físico liberado é 0.
13. **Realocação não equivale a exclusão.** Nenhum arquivo é apagado; o archive nunca é removido sem nova decisão explícita.
14. **Esta política foi autorizada explicitamente pelo operador** (texto acima).
15. **A autorização desta data cobre somente os 29 candidatos aprovados.**
