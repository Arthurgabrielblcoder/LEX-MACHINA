# Cobertura da camada 4 REFERÊNCIAS — RUN2 → RUN3

`WORK_REFERENCE` com `CURRENT_VISIBLE` apenas (mesmo classificador do firmware). Artigo repetido conta uma vez; target ≠ artigo.
RUN2: `LEGAL_TARGET_ID/derived/export_test/run2/CF88_REFERENCES_EXPORT.json` · RUN3 (candidato): `LEGAL_TARGET_ID/derived/export_test/run3/CF88_REFERENCES_EXPORT.json`.

## Antes × depois

| MÉTRICA | RUN2 | RUN3 | Δ |
|---|---|---|---|
| Vínculos WORK_REFERENCE | 101 | 122 | +21 |
| Targets canônicos com obra | 43 | 63 | +20 |
| Artigos distintos da CF com obra | 18 | 33 | +15 |
| Artigos do ADCT com obra | 0 | 1 | +1 |
| Targets do ADCT com obra | 0 | 1 | +1 |

- Relações totais do export: 430 → 451 (só WORK_REFERENCE mudou; jurisprudência, correlatas e ocultos idênticos).
- Exclusões do RUN2 mantidas no RUN3: `JURISPRUDENCE:STF:RG:113:CF88:25:-:-:-@CF88:ART.25`, `JURISPRUDENCE:STF:RG:756:CF88:31:3:-:-@CF88:ART.31:PAR.3`.

## Artigos-alvo da expansão

| ARTIGO | OBRAS RUN2 | OBRAS RUN3 | NOVAS | SITUAÇÃO |
|---|---|---|---|---|
| Art. 37 | 0 | 2 | Os Donos do Poder (CF88.37.CAPUT)<br>Raízes do Brasil (CF88.37.CAPUT) | NOVA COBERTURA |
| Art. 43 | 0 | 2 | Formação Econômica do Brasil (CF88.43.CAPUT)<br>Vidas Secas (CF88.43.2.IV) | NOVA COBERTURA |
| Art. 52 | 0 | 1 | O Processo (CF88.52.I) | NOVA COBERTURA |
| Art. 58 | 0 | 1 | Tropa de Elite 2: O Inimigo Agora É Outro (CF88.58.3) | NOVA COBERTURA |
| Art. 62 | 0 | 1 | Suzerain (CF88.62.CAPUT) | NOVA COBERTURA |
| Art. 86 | 0 | 1 | Excelentíssimos (CF88.86.CAPUT) | NOVA COBERTURA |
| Art. 134 | 0 | 1 | Luta por Justiça (CF88.134.CAPUT) | NOVA COBERTURA |
| Art. 144 | 0 | 2 | A Escuta (CF88.144.7)<br>Tropa de Elite (CF88.144.5) | NOVA COBERTURA |
| Art. 145 | 0 | 1 | O Triunfo da Injustiça (CF88.145.1) | NOVA COBERTURA |
| Art. 182 | 0 | 2 | Cities: Skylines (CF88.182.1)<br>Citizen Jane: Battle for the City (CF88.182.CAPUT) | NOVA COBERTURA |
| Art. 184 | 0 | 1 | Cabra Marcado para Morrer (CF88.184.CAPUT) | NOVA COBERTURA |
| Art. 192 | 0 | 1 | A Grande Aposta (CF88.192) | NOVA COBERTURA |
| Art. 196 | 0 | 0 | — | SEM COBERTURA — aprovado, retido (obra sem identidade) |
| Art. 201 | 0 | 1 | Eu, Daniel Blake (CF88.201.I) | NOVA COBERTURA |
| Art. 206 | 0 | 0 | — | SEM COBERTURA — aprovado, retido (obra sem identidade) |
| Art. 215 | 0 | 1 | Never Alone (Kisima Inŋitchuŋa) (CF88.215.1) | NOVA COBERTURA |
| Art. 231 | 0 | 1 | Martírio (CF88.231.CAPUT) | NOVA COBERTURA |
| ADCT art. 68 | 0 | 1 | Torto Arado (ADCT.68) | NOVA COBERTURA |
| Art. 7 | 1 | 2 | Frostpunk (CF88.7.XXXIII) | REFORÇADO |

## Lacunas e rejeições deliberadas

- **CF88.98** `CONFIRMED_REFERENCE_GAP` — Nenhuma obra adequada foi encontrada sem forçar vínculo (juizados especiais / justiça de paz). Obras no RUN3: 0.
- **CF88.202** `CONFIRMED_REFERENCE_GAP` — Nenhuma obra adequada foi encontrada sem forçar vínculo (previdência complementar privada). Obras no RUN3: 0.
- **CF88.76** Borgen: `REJECTED_EDITORIAL_WEAK_CONNECTION` — A série retrata parlamentarismo dinamarquês. A ligação com o art. 76 depende de comparação por contraste com o presidencialismo brasileiro. Associação excessivamente indireta.
- **CF88.142.CAPUT** Argentina, 1985: `REJECTED_EDITORIAL_WEAK_CONNECTION` — A obra trata primordialmente do julgamento e responsabilização de integrantes das juntas militares argentinas. Não representa adequadamente a finalidade, organização ou regime constitucional das Forças Armadas previsto no art. 142.
- **CF88.196** SOS Saúde (Sicko): aprovado (score 7.4), `APPROVED_PENDING_WORK_IDENTITY` — obra sem ID em nenhum catálogo; fora do RUN3.
- **CF88.206.I** Pro Dia Nascer Feliz: aprovado (score 8.0), `APPROVED_PENDING_WORK_IDENTITY` — obra sem ID em nenhum catálogo; fora do RUN3.

## Novos vínculos (21) e expectativa no aparelho

| TARGET | OBRA | TIPO | ANO | SCORE | DECISÃO | LINHA DO APARELHO (ACTIVE_TARGET) | CHAVES CONSULTADAS |
|---|---|---|---|---|---|---|---|
| `CF88.7.XXXIII` | Frostpunk (EXP-JOG-003) | JOGO | 2018 | 7.8 | ADJUST_APPROVE | `CF88:ART.7:INC.XXXIII` | CF88:ART.7:INC.XXXIII |
| `CF88.37.CAPUT` | Os Donos do Poder (EXP-LIV-002) | LIVRO | 1958 | 8.6 | APPROVE | `CF88:ART.37` | CF88:ART.37+CF88:ART.37:CAPUT |
| `CF88.37.CAPUT` | Raízes do Brasil (EXP-LIV-001) | LIVRO | 1936 | 8.0 | APPROVE | `CF88:ART.37` | CF88:ART.37+CF88:ART.37:CAPUT |
| `CF88.43.CAPUT` | Formação Econômica do Brasil (EXP-LIV-003) | LIVRO | 1959 | 8.6 | APPROVE | `CF88:ART.43` | CF88:ART.43+CF88:ART.43:CAPUT |
| `CF88.43.2.IV` | Vidas Secas (EXP2-LIV-040) | LIVRO | 1938 | 8.4 | APPROVE | `CF88:ART.43:PAR.2:INC.IV` | CF88:ART.43:PAR.2:INC.IV |
| `CF88.52.I` | O Processo (EXP-DOC-005) | DOCUMENTÁRIO | 2018 | 7.4 | APPROVE | `CF88:ART.52:INC.I` | CF88:ART.52:INC.I |
| `CF88.58.3` | Tropa de Elite 2: O Inimigo Agora É Outro (EXP2-FIL-039) | FILME | 2010 | 7.6 | APPROVE | `CF88:ART.58:PAR.3` | CF88:ART.58:PAR.3 |
| `CF88.62.CAPUT` | Suzerain (EXP-JOG-002) | JOGO | 2020 | 7.4 | ADJUST_APPROVE | `CF88:ART.62` | CF88:ART.62+CF88:ART.62:CAPUT |
| `CF88.86.CAPUT` | Excelentíssimos (EXP-DOC-006) | DOCUMENTÁRIO | 2018 | 7.6 | APPROVE | `CF88:ART.86` | CF88:ART.86+CF88:ART.86:CAPUT |
| `CF88.134.CAPUT` | Luta por Justiça (EXP2-FIL-006) | FILME | 2019 | 7.8 | APPROVE | `CF88:ART.134` | CF88:ART.134+CF88:ART.134:CAPUT |
| `CF88.144.5` | Tropa de Elite (EXP2-FIL-038) | FILME | 2007 | 7.4 | APPROVE | `CF88:ART.144:PAR.5` | CF88:ART.144:PAR.5 |
| `CF88.144.7` | A Escuta (EXP-SER-002) | SÉRIE | 2002 | 7.2 | APPROVE | `CF88:ART.144:PAR.7` | CF88:ART.144:PAR.7 |
| `CF88.145.1` | O Triunfo da Injustiça (EXP-LIV-009) | LIVRO | 2019 | 8.2 | APPROVE | `CF88:ART.145:PAR.1` | CF88:ART.145:PAR.1 |
| `CF88.182.CAPUT` | Citizen Jane: Battle for the City (EXP-DOC-010) | DOCUMENTÁRIO | 2016 | 8.2 | APPROVE | `CF88:ART.182` | CF88:ART.182+CF88:ART.182:CAPUT |
| `CF88.182.1` | Cities: Skylines (EXP-JOG-004) | JOGO | 2015 | 7.6 | APPROVE | `CF88:ART.182:PAR.1` | CF88:ART.182:PAR.1 |
| `CF88.184.CAPUT` | Cabra Marcado para Morrer (EXP-DOC-008) | DOCUMENTÁRIO | 1984 | 7.8 | APPROVE | `CF88:ART.184` | CF88:ART.184+CF88:ART.184:CAPUT |
| `CF88.192` | A Grande Aposta (EXP-FIL-007) | FILME | 2015 | 7.8 | APPROVE | `CF88:ART.192` | CF88:ART.192+CF88:ART.192:CAPUT |
| `CF88.201.I` | Eu, Daniel Blake (EXP-FIL-006) | FILME | 2016 | 8.4 | APPROVE | `CF88:ART.201:INC.I` | CF88:ART.201:INC.I |
| `CF88.215.1` | Never Alone (Kisima Inŋitchuŋa) (EXP-JOG-006) | JOGO | 2014 | 7.4 | APPROVE | `CF88:ART.215:PAR.1` | CF88:ART.215:PAR.1 |
| `CF88.231.CAPUT` | Martírio (EXP-DOC-007) | DOCUMENTÁRIO | 2016 | 8.6 | APPROVE | `CF88:ART.231` | CF88:ART.231+CF88:ART.231:CAPUT |
| `ADCT.68` | Torto Arado (EXP-LIV-005) | LIVRO | 2019 | 9.2 | ADJUST_APPROVE | `ADCT:ART.68` | ADCT:ART.68 |

Regra ART↔CAPUT preservada: obra em `CF88:ART.n:CAPUT` aparece na linha `CF88:ART.n`; nunca em incisos, parágrafos ou alíneas.

## Tabela por artigo (RUN3)

| ARTIGO | TARGETS COM OBRA | VÍNCULOS | NOVOS NO RUN3 |
|---|---|---|---|
| Art. 1 | CF88.1.III<br>CF88.1.UNICO | 7 | 0 |
| Art. 2 | CF88.2.CAPUT | 1 | 0 |
| Art. 3 | CF88.3.III<br>CF88.3.IV | 14 | 0 |
| Art. 4 | CF88.4.VIII | 6 | 0 |
| Art. 5 | CF88.5.CAPUT<br>CF88.5.I<br>CF88.5.III<br>CF88.5.IV<br>CF88.5.VI<br>CF88.5.VIII<br>CF88.5.IX<br>CF88.5.X<br>CF88.5.XII<br>CF88.5.XIII<br>CF88.5.XIV<br>CF88.5.XV<br>CF88.5.XXII<br>CF88.5.XXXV<br>CF88.5.XLII<br>CF88.5.XLIX<br>CF88.5.LIV<br>CF88.5.LV<br>CF88.5.LVII<br>CF88.5.LXXIX | 33 | 0 |
| Art. 6 | CF88.6.CAPUT | 6 | 0 |
| Art. 7 | CF88.7.IV<br>CF88.7.XXXIII | 2 | 1 |
| Art. 14 | CF88.14.CAPUT | 1 | 0 |
| Art. 23 | CF88.23.IX | 1 | 0 |
| Art. 37 | CF88.37.CAPUT | 2 | 2 |
| Art. 43 | CF88.43.CAPUT<br>CF88.43.2.IV | 2 | 2 |
| Art. 52 | CF88.52.I | 1 | 1 |
| Art. 58 | CF88.58.3 | 1 | 1 |
| Art. 62 | CF88.62.CAPUT | 1 | 1 |
| Art. 86 | CF88.86.CAPUT | 1 | 1 |
| Art. 134 | CF88.134.CAPUT | 1 | 1 |
| Art. 144 | CF88.144.5<br>CF88.144.7 | 2 | 2 |
| Art. 145 | CF88.145.1 | 1 | 1 |
| Art. 170 | CF88.170.CAPUT<br>CF88.170.II<br>CF88.170.VI<br>CF88.170.VII | 15 | 0 |
| Art. 182 | CF88.182.CAPUT<br>CF88.182.1 | 2 | 2 |
| Art. 184 | CF88.184.CAPUT | 1 | 1 |
| Art. 192 | CF88.192 | 1 | 1 |
| Art. 193 | CF88.193.CAPUT | 3 | 0 |
| Art. 194 | CF88.194.CAPUT | 1 | 0 |
| Art. 201 | CF88.201.I | 1 | 1 |
| Art. 203 | CF88.203.VI | 3 | 0 |
| Art. 205 | CF88.205.CAPUT | 1 | 0 |
| Art. 215 | CF88.215.1 | 1 | 1 |
| Art. 220 | CF88.220.CAPUT<br>CF88.220.2 | 4 | 0 |
| Art. 225 | CF88.225.CAPUT | 2 | 0 |
| Art. 226 | CF88.226.7 | 1 | 0 |
| Art. 227 | CF88.227.CAPUT | 1 | 0 |
| Art. 231 | CF88.231.CAPUT | 1 | 1 |
| ADCT art. 68 | ADCT.68 | 1 | 1 |

CSV completo (um vínculo por linha, 122 linhas): `REFERENCE_WORK_COVERAGE_RUN3.csv`.
