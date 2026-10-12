# CF88_CORRELATA — revisão integral dos vínculos legados visíveis

**Decisões editoriais. Nada foi aplicado.** O catálogo, as exclusões e o export RUN3 não mudaram.

- **Export:** 46 vínculos; 44 visíveis; 2 históricos ocultos (fora da contagem).
- **Revisados:** 44/44; 19 já decididos na C1A; 25 revisados agora.
- **Evidência reutilizada:** texto da norma no cartão (sha256 do pin C0) e páginas oficiais já baixadas na C1A/C1B. Nenhum download novo.

| Decisão | Total (44) | C1A | Agora |
|---|---:|---:|---:|
| KEEP | 10 | 0 | 10 |
| KEEP_WITH_ROUTE_FIX | 5 | 0 | 5 |
| RETARGET | 5 | 1 | 4 |
| REPLACE | 5 | 5 | 0 |
| REMOVE | 18 | 12 | 6 |
| HOLD | 1 | 1 | 0 |

## Pontos de atenção

- **Lei 14.965/2024 × art. 37, II:** KEEP jurídico, mas a lei está em vacatio até 2028-01-01. Pela política C2, o vínculo deve ser neutralizado por exclusão temporária até a vigência (`SUPPRESS_UNTIL_EFFECTIVE`).
- **LC 70/1991 × art. 195, I:** retarget para a alínea b; a COFINS é extinta a partir de 2027 (ADCT, art. 126, II): revalidar em 2027-01-01.
- **LC 87/1996 (arts. 150, § 7º e 155, § 2º, XII):** ICMS em transição até 2033; revalidar.
- **PNE (Lei 15.388/2026):** seis vínculos de fan-out nos incisos do art. 214 viram um único vínculo no caput.
- **Lei 12.734/2012 × art. 20, § 1º:** REMOVE (lei alteradora incorporada).
- **LC 199/2023:** o retarget para o art. 146, III, b converge com um HIGH aprovado; aplicar uma única relação.

## Vínculos (44)

| Rodada | Target | Norma | Decisão | Retarget / rota | Temporal |
|---|---|---|---|---|---|
| LEGACY_FULL_REVIEW | `CF88:ART.5:INC.XLIII` | Lei nº 13.260/2016 | KEEP | — | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.20:PAR.1` | Lei nº 12.734/2012 | REMOVE | — | IN_FORCE |
| C1A | `CF88:ART.20:PAR.1` | Lei nº 9.984/2000 | REPLACE | substituir: Lei nº 7.990/1989 | — |
| LEGACY_FULL_REVIEW | `CF88:ART.34:INC.V:AL.b` | Lei Complementar nº 63/1990 | KEEP | — | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.37:INC.II` | Lei nº 14.965/2024 | KEEP | — | VACATIO_LEGIS |
| LEGACY_FULL_REVIEW | `CF88:ART.37:PAR.3:INC.I` | Lei nº 13.460/2017 | KEEP | — | IN_FORCE |
| C1A | `CF88:ART.37:PAR.3:INC.II` | Lei nº 13.460/2017 | REPLACE | substituir: Lei nº 12.527/2011 (LAI) | — |
| C1A | `CF88:ART.37:PAR.3:INC.III` | Lei nº 13.460/2017 | HOLD | — | — |
| C1A | `CF88:ART.43:PAR.1:INC.I` | Lei Complementar nº 112/2001 | REMOVE | — | — |
| C1A | `CF88:ART.43:PAR.1:INC.II` | Lei Complementar nº 112/2001 | REPLACE | substituir: Lei Complementar nº 124/2007 (SUDAM), Lei Complementar nº 125/2007 (SUDENE), Lei Complementar nº 129/2009 (SUDECO) | — |
| LEGACY_FULL_REVIEW | `CF88:ART.146` | Lei Complementar nº 199/2023 | RETARGET | CF88:ART.146:INC.III:AL.b | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.150:PAR.7` | Lei Complementar nº 87/1996 | KEEP_WITH_ROUTE_FIX | arts. 10 | IN_FORCE |
| C1A | `CF88:ART.153:PAR.4:INC.II` | Lei nº 11.250/2005 | REMOVE | — | — |
| C1A | `CF88:ART.153:PAR.4:INC.II` | Lei nº 8.981/1995 | REMOVE | — | — |
| LEGACY_FULL_REVIEW | `CF88:ART.153:PAR.4:INC.II` | Lei nº 9.393/1996 | KEEP_WITH_ROUTE_FIX | arts. 2 | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.153:PAR.4:INC.III` | Lei nº 11.250/2005 | KEEP | — | IN_FORCE |
| C1A | `CF88:ART.153:PAR.4:INC.III` | Lei nº 8.981/1995 | REMOVE | — | — |
| C1A | `CF88:ART.153:PAR.4:INC.III` | Lei nº 9.393/1996 | REMOVE | — | — |
| C1A | `CF88:ART.155:PAR.1:INC.III` | Lei Complementar nº 87/1996 | REMOVE | — | — |
| LEGACY_FULL_REVIEW | `CF88:ART.155:PAR.2:INC.XII` | Lei Complementar nº 87/1996 | KEEP | — | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.158:PAR.1:INC.II` | Lei Complementar nº 63/1990 | RETARGET | CF88:ART.158:PAR.1:INC.I arts. 3 | IN_FORCE |
| C1A | `CF88:ART.161:INC.I` | Lei Complementar nº 62/1989 | REPLACE | substituir: Lei Complementar nº 63/1990 | — |
| LEGACY_FULL_REVIEW | `CF88:ART.161:INC.II` | Lei Complementar nº 62/1989 | KEEP | — | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.161:INC.III` | Lei Complementar nº 62/1989 | KEEP | — | IN_FORCE |
| C1A | `CF88:ART.182` | Lei nº 13.425/2017 | RETARGET | CF88:ART.182:CAPUT rota | — |
| LEGACY_FULL_REVIEW | `CF88:ART.195:INC.I` | Lei Complementar nº 70/1991 | RETARGET | CF88:ART.195:INC.I:AL.b arts. 1 | IN_FORCE |
| C1A | `CF88:ART.195:INC.II` | Lei Complementar nº 70/1991 | REPLACE | substituir: Lei nº 8.212/1991 | — |
| C1A | `CF88:ART.195:PAR.1` | Lei Complementar nº 70/1991 | REMOVE | — | — |
| C1A | `CF88:ART.195:PAR.2` | Lei Complementar nº 70/1991 | REMOVE | — | — |
| C1A | `CF88:ART.201:INC.I` | Lei nº 7.998/1990 | REMOVE | — | — |
| C1A | `CF88:ART.201:INC.II` | Lei nº 7.998/1990 | REMOVE | — | — |
| LEGACY_FULL_REVIEW | `CF88:ART.201:INC.III` | Lei nº 7.998/1990 | KEEP_WITH_ROUTE_FIX | arts. 2 | IN_FORCE |
| C1A | `CF88:ART.201:INC.IV` | Lei nº 7.998/1990 | REMOVE | — | — |
| C1A | `CF88:ART.201:INC.V` | Lei nº 7.998/1990 | REMOVE | — | — |
| LEGACY_FULL_REVIEW | `CF88:ART.202:CAPUT` | Lei Complementar nº 109/2001 | KEEP | — | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.202:PAR.4` | Lei Complementar nº 108/2001 | KEEP | — | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.202:PAR.5` | Lei Complementar nº 108/2001 | KEEP_WITH_ROUTE_FIX | arts. 26 | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.202:PAR.6` | Lei Complementar nº 108/2001 | KEEP_WITH_ROUTE_FIX | arts. 11, 20 | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.214:INC.I` | Lei nº 15.388/2026 | RETARGET | CF88:ART.214:CAPUT arts. 1 | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.214:INC.II` | Lei nº 15.388/2026 | REMOVE | — | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.214:INC.III` | Lei nº 15.388/2026 | REMOVE | — | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.214:INC.IV` | Lei nº 15.388/2026 | REMOVE | — | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.214:INC.V` | Lei nº 15.388/2026 | REMOVE | — | IN_FORCE |
| LEGACY_FULL_REVIEW | `CF88:ART.214:INC.VI` | Lei nº 15.388/2026 | REMOVE | — | IN_FORCE |

## Históricos ocultos (2, fora dos 44)

- `CF88:ART.40:PAR.4:INC.II` (HISTORICAL_HIDDEN_BY_DEFAULT)
- `CF88:ART.40:PAR.4:INC.III` (HISTORICAL_HIDDEN_BY_DEFAULT)

