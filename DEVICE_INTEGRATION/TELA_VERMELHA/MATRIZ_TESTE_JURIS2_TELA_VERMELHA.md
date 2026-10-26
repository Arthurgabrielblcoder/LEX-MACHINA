# Jurisprudência nº 2 — preservação no firmware da tela vermelha (`a7beea0b…`)

**Resultado físico (usuário, 2026-10-26): `JURIS2_PRESERVATION_TELA_VERMELHA = 3/3 PASS`** — rodapé, tecla 2, ficha, BACK ficha→lista e
BACK lista→texto conferidos nos três casos. Nenhum dado, índice, microSD ou firmware foi alterado para este teste.

## Fonte histórica
- J2G 299/186, 21/21 PASS (17/10): `JURISPRUDENCE_AUDIT/J2G_PHYSICAL_DEPLOY/J2G_PHYSICAL_VALIDATION.json`.
- J2H (cartão B, 315/198) + J2I (firmware genérico), **32/32 PASS** (18/10), com BACK testado nos itens 2–13:
  `JURISPRUDENCE_AUDIT/J2I_PHYSICAL_FLASH/J2I_PHYSICAL_VALIDATION.json`; checklist em `J2I_GENERIC_FIRMWARE_FLASH_REPORT.md` §8.
- Baseline `J2I_FROZEN_315_198` (tag `lex-device-v1-juris-j2i-physical-approved-2026-10-18`): `JURISPRUDENCE_AUDIT/JURIS_CF_ADCT_J2I_FROZEN.md`.
- Estado atual registrado do cartão: camada normalizada do mass V2 CC 653 (22/10), POST CF/ADCT 315/198. O firmware atual lê a CF por ela.

## Matriz
| # | Dispositivo | Target ID | Precedente | Juris no target | Evidência anterior (J2I) | Hoje (tela vermelha) |
|---|---|---|---|---|---|---|
| 1 | CF, art. 53, § 1º | `CF88:ART.53:PAR.1` | HC 232627 (STF, Plenário) — foro por prerrogativa após o afastamento do cargo | 1 | item 2 PASS | PASS |
| 2 | CF, art. 52, parágrafo único | `CF88:ART.52:PAR.UNICO` | MS 21689 (STF, Pleno, 1993) — impeachment: perda do cargo e inabilitação autônomas | 1 | item 4 PASS | PASS |
| 3 | CF, art. 15, III | `CF88:ART.15:INC.III` | Súmula 9 TSE — suspensão de direitos políticos cessa com o cumprimento ou a extinção da pena (+ Temas RG 1190 e 370) | 3 | item 13 PASS (Temas 1190/370 só implantados) | PASS |

Conferência de dados no host (sem ler o cartão):
- `CF88_TARGETS` com flag J (`E-J--X`, `E-J--X`, `--J-R-`).
- `REF_LOOKUP` com quantidades 1, 1 e 3.
- Ids na camada normalizada `06_NORMALIZADO/JURISPRUDENCIA.IDX` (linhas 235, 232, 116–118) e no `JUR_LOOKUP.IDX`.
- Fichas `STF_HC_232627.TXT`, `STF_MS_21689.TXT` e `TSE_SUMULA_9.TXT` presentes no manifesto J2H.

## Roteiro executado
CF → busca por artigo → linha do dispositivo no topo → rodapé "2 JURIS." → tecla 2 (lista) → ENTER (ficha) → BACK (mesma lista) → BACK (texto).
