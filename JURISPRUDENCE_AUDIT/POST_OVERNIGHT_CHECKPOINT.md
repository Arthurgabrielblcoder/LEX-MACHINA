# OPERAÇÃO PÓS-NOTURNA — CHECKPOINT (2026-10-17)

## Estado atual (J2J, 2026-10-18) — prevalece sobre o histórico abaixo

```
CURRENT_PHYSICAL_JURIS_BASELINE = J2I   (J2I_FROZEN_315_198)
RELATIONS = 315
TARGETS = 198
GENERIC_FIRMWARE = PHYSICALLY_APPROVED   (app 1371e69a…, app0 @ 0x10000)
J2I_PHYSICAL_VALIDATION = 32/32 PASS
FROZEN_LAYERS_MODIFIED = NO · STJ_SUMULA_403 = UNRESOLVED_EXTERNAL
NEXT_RESEARCH_BATCH = BATCH10   (NÃO iniciado)
```

Documento de freeze: `JURIS_CF_ADCT_J2I_FROZEN.md`. Registro físico: `J2I_PHYSICAL_FLASH/J2I_PHYSICAL_VALIDATION.json`. Toda nova rodada parte explicitamente de `J2I_FROZEN_315_198`.

O restante deste arquivo é o checkpoint histórico de 2026-10-17 (baseline físico 261/160 da época).

> Sucede `OVERNIGHT_MISSION_CHECKPOINT.md`. Host-only: sem deploy, sem flash e sem acesso ao microSD.

```
PHYSICAL_BASELINE = 261/160 (J2C, inalterado) · J2E_VARIANT_A = HOLD · J2E_VARIANT_B = HOLD
FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE = PASS · GENERAL_JURIS_TYPE_ARCHITECTURE = PASS · GENERAL_FIRMWARE_PROTOTYPE = PASS (não gravado)
BATCH09 = CONCLUÍDO (AWAITING_USER_RATIFICATION) · UNRATIFIED_RELATIONS_PUBLISHED = 0
MICROSD_TOUCHED = NO · FIRMWARE_FLASHED = NO · FROZEN_LAYERS_MODIFIED = NO · MAIN_MERGED = NO · BATCH10 = NÃO INICIADO
```

## Partes

| Parte | Resultado | Artefatos |
|---|---|---|
| A | J2E-A e J2E-B em HOLD (nada instalado) | — |
| B | Dossiê de ratificação: 55 recomendações dos Batches 03–09, agrupadas por decisão; provisórios com natureza, último status e gatilho; realocações como `ORIGINAL → CORRETO` | `J2_RATIFICATION_DOSSIER.md`, `render_j2_ratification_dossier.py` |
| C | Reconciliação: físico 261/160; ratificado host-only 8 (A 7, B 1); aguardando 55 recomendações (39 vinculam, até 58 relações em 40 targets); 1 UNRESOLVED; 0 em pesquisa; 69 não pesquisadas (MEDIUM 42, LOW 27) | `J2_RECONCILIATION.json` |
| D | `firmware/` com header de 124 fichas reconstrói o app aprovado (70–71 bytes de metadado). Os guards aceitam só esse header (sha fixado) e o header pré-R1 é lido do Git @10e199f | `FIRMWARE_REPRODUCIBILITY/*`, `aa8cdd3` |
| E | Tribunal separado da classe; tabela de classes; súmula com tribunal; lista de tribunais; legado inalterado | `JURIS_TYPE_ARCHITECTURE.md`, `juris_types.py` |
| F | Protótipo de firmware generalizado: +1.040 B de programa, +0 B de RAM, partição livre 208.544 B; não gravado | `JURIS_TYPE_PROTOTYPE/*` |
| G | Nenhuma relação não ratificada publicada | — |
| H | Batch09: 5 promoções, 3 já cobertas, 2 duplicatas | `J2_MEDIUM_BACKLOG/J2_BATCH09_*` |
| I | Súmula 403 do STJ segue UNRESOLVED_EXTERNAL: desafio anti-robô não contornado; o PDF oficial é download (não baixado) | `STJ_SUMULA403_ATTEMPTS.md` |
| J | Registro consolidado de provisórios: ADI 7697, ADI 5017, ADPF 378, Rcl 84738; gate PASS em 2026-10-17 | `J2_PROVISIONAL_REGISTRY.json`, `build_j2_provisional_registry.py` |
| K | Mock 367/387 só de dados (texto das fichas); vínculos, IDX e rótulos intactos; não aplicado | `UI_MOCK_TEMAS_367_387/*` |
| L | Especificação curta do Updater | `JURIS_UPDATER_SPEC.md` |
| M | Ver tabela abaixo | — |

## Testes (Parte M)

| Suíte | Resultado |
|---|---|
| Jurisprudência (J1/J2, auditores, lotes, dossiê, provisórios, tipos, HC) | 90/90 |
| Motor de referências (`LEGAL_TARGET_ID`) | 90/90 |
| Referências nº 4 (`REFERENCE_COVERAGE_AUDIT`) | 15/15 |
| Correlatas | 115/120. As 5 falhas são todas PREEXISTING: c0 `test_committed_artifacts_are_the_build`; c3a1 `test_15`; c3a_engine `test_16` (`_tmp_det_*.log` não rastreado); c3b1 `test_reproducible`; c3b2 `test_c3b2_package_reproducible…`. NEW_REGRESSION = 0 |

**Regressões novas da Parte D, corrigidas na causa.** Seis guards fixavam o header antigo de `firmware/`:

- `test_hc_prototype`, `test_j2b`, `test_j2b_1` e `test_j2e`;
- `test_references4_r1_device` (2 testes);
- `test_references4_r1.test_generators_up_to_date`, que dependia de `build_references4_r1_isolation_audit.py`.

Todos passam a usar `firmware_baseline.py`: só o header R1 com sha fixado pode diferir, e o pré-R1 é lido do Git. Saída do gerador byte-idêntica (UP_TO_DATE).

## Próximo passo

Decisão do usuário: ratificar os lotes 03–09 e escolher a estratégia de deploy. **Não** iniciar o Batch10 automaticamente.
