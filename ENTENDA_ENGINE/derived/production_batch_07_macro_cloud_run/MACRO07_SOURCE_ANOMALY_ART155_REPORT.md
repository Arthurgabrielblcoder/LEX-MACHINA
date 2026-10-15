# MACRO07 — Anomalia de fonte: art. 155, inciso I, alínea c

Missão MACRO07_SECOND_PASS_RISK_COMPRESSION_AND_SOURCE_SANITY · branch `cf-macro-76-175-cloud` · data de referência 2026-10-05.
**Nenhum texto foi inventado nem editado à mão.**

## Sintoma

- `CF88:ART.155:INC.I:AL.c` estava `CURRENT` no status, com o motivo "texto presente no texto operacional vigente (rótulo com formatação divergente)".
- O texto do runtime estava vazio.
- As alíneas a e b do mesmo inciso estavam `HISTORICAL_ONLY`.
- A visão geral do art. 155 dizia "a alínea c do inciso I (sem texto no runtime)" nas notas de artigo. O problema estava registrado como backlog MB07-02.

## Comparação das camadas

| Camada | O que traz | Situação |
|---|---|---|
| Fonte do Senado (`normalizado.txt`, sha256 `d2f681e0…`) | não existe alínea c no inciso I; linha 2248: `III - propriedade de veículos automotores.` | correta (texto vigente) |
| `cf.txt` canônico (sha256 `0742175b…`) | linha 4340: `c) propriedade de veículos automotores` (redação de 1988); linha 4350: `III - propriedade de veículos automotores. (Redação dada pela Emenda Constitucional nº 3, de 1993)` | correto (compilado histórico) |
| Índice de targets | `CF88:ART.155:INC.I:AL.c` (da linha 4340) e `CF88:ART.155:INC.III` | correto: o índice guarda o histórico |
| Segmentação do texto operacional | a alínea c não existe (correto) | correta |
| Status (`reference_canonicalization.build_status`) | o texto da alínea c "aparece" no operacional (dentro do III), mas a busca por rótulo renumerado exigia os 80 primeiros caracteres idênticos: `propriedade de veículos automotores` ≠ `propriedade de veículos automotores.` (ponto final). Cai no ramo "formatação divergente" e marca `CURRENT` | **defeito** |
| Apresentação (ENTENDA) | alvo vigente sem texto; nota "sem texto no runtime" | manifestação |

## Causa

**D — STATUS/ÍNDICE DE TARGETS.** É a mesma redação de 1988, renumerada para o inciso III pela EC 3/1993. A fonte, a normalização e a segmentação estão corretas.

O erro está só na regra que detecta rótulo renumerado: a pontuação final entrava na comparação.

## Correção (camada técnica mínima)

- `reference_canonicalization.build_status(..., errata=True)` compara a redação sem a pontuação final (`_head`: 80 primeiros caracteres, sem `.;,:` e espaços no fim).
  - O teste garante que palavras diferentes continuam diferentes, por exemplo "… automotores terrestres".
- O build legado (`errata=False`) segue idêntico e reproduz o `CF88_TARGET_STATUS.json` congelado. Esse arquivo é entrada fixada do manifesto do Batch06 e dos exports do DEVICE.
- A correção entra pela errata `LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS_ERRATA.json`:
  - `CF88:ART.155:INC.I:AL.c` `CURRENT` → `HISTORICAL_ONLY`;
  - motivo: "rótulo renumerado: o mesmo texto está no vigente sob CF88:ART.155:INC.III";
  - causa: `RENUMBERED_LABEL_FINAL_PUNCTUATION`.
- A única outra entrada "formatação divergente" do status é `CF88:ART.239:PAR.4`. Fica fora do escopo e a errata recalculada não a altera; está registrada como MB07-08.

## Depois

- A seleção do lote classifica a alínea c como `EXCLUDED_HISTORICAL`.
- A nota de artigo do art. 155 deixou de citá-la (log do segundo passe, `FONTE_SANEADA`).
- O backlog MB07-02 ficou resolvido.

## Dependentes regenerados

Lote macro 07: seleção, plano, rascunho consolidado e pacotes, com 3 builds byte-idênticos.

## O que não mudou (verificado)

- As fontes e o `cf.txt` canônico têm os mesmos sha256.
- O índice de targets e o status congelado ficaram intactos.
- Batch06 e os exports do DEVICE continuam byte-idênticos.

## Testes de regressão

- `LEGAL_TARGET_ID/tests/test_source_corrections.py`:
  - `test_renumbered_label_ignores_final_punctuation_only`;
  - `test_exactly_the_two_corrections`;
  - `test_errata_is_reproducible_from_git`;
  - `test_frozen_status_untouched`.
- `ENTENDA_ENGINE/tests/test_entenda_macro_batch07.py::MacroBatch07SecondPass.test_art155_i_c_is_historical_renumbered`.
