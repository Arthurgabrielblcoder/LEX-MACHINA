# CF88_CORRELATA_C1B — fechamento da fila HIGH original

**Fechamento editorial e jurídico. Nada foi aplicado.** Não houve ADDITIONS, exclusões, RUN4, nem alteração em TARGETS, RELACOES, SD ou firmware. MEDIUM e LOW não foram iniciados.

## Resultado

- **Revisão:** `HIGH_ORIGINAL_REVIEWED = 106/106`, `HIGH_ORIGINAL_REMAINING = 0`.
- **Por lote:** {'BATCH01': 29, 'BATCH02': 30, 'BATCH03': 30, 'BATCH04': 17}.

| Decisão | n |
|---|---:|
| APPROVE | 36 |
| ADJUST | 39 |
| REJECT | 27 |
| HOLD | 4 |
| NEEDS_SOURCE | 0 |
| **Aceitos (APPROVE + ADJUST)** | **75** |

| Aceitos: rota de aparelho / temporal | n |
|---|---:|
| MAIN_CORPUS_ROUTE_REQUIRED | 19 |
| INGESTION_REQUIRED | 49 |
| DEVICE_RESOLVABLE_NOW | 7 |
| TEMPORAL_DEVICE_BLOCK | 2 |
| VACATIO_LEGIS | 2 |
| TRANSITIONAL | 2 |

- **Situação temporal dos aceitos:** {'IN_FORCE': 62, 'PARTIAL_EFFECTS': 9, 'TRANSITIONAL': 2, 'VACATIO_LEGIS': 2}.

| CF permanente × ADCT | CF | ADCT |
|---|---:|---:|
| total | 104 | 2 |
| accepted | 73 | 2 |
| reject | 27 | 0 |
| hold | 4 | 0 |
| needs_source | 0 | 0 |

## Pontos para a revisão independente do fechamento

- **HOLD (4):**
  - art. 40, § 7º × Lei 8.112/1990 (Batch01);
  - art. 231, §§ 1º, 3º e 6º × Lei 14.701/2023 (Batch04). A lei está sob controle concentrado no STF (ADC 87; ADIs 7582, 7583 e 7586, anotadas na página oficial).
- **Vacatio legis:** Lei 14.965/2024 nos arts. 131, § 2º e 132, aceita com `TEMPORAL_DEVICE_BLOCK` até 2028-01-01.
  - Dívida `FUTURE_EFFECTIVE_CORRELATA_POLICY_REQUIRED`.
  - O vínculo atual Lei 14.965 × art. 37, II, já visível no RUN3, tem o mesmo problema; registrado para C2.
- **ADCT:** os aceitos no ADCT dependem da regra de status do motor (UNKNOWN_VALIDITY) para entrar no overlay futuro.
- **Reforma tributária:** a LC 214/2025 e a LC 227/2026 estão aprovadas em targets específicos, cada um com fundamento próprio.
  - LC 214: arts. 146, § 1º; 153, § 6º; 156-A, §§ 1º, 5º, 6º, 9º e 13.
  - LC 227: arts. 155, § 1º e 156-A, § 5º, VII.
  - Foram rejeitadas as ligações genéricas: 146, III; 153, § 3º; 155, § 2º; 156, § 3º; 159, I.

## Candidatos (106)

| Lote | Target | Norma | Decisão | Natureza final | Target final | Temporal | Aparelho |
|---|---|---|---|---|---|---|---|
| 01 | `CF88:ART.5:INC.XII` | Lei nº 9.296/1996 | ADJUST | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 01 | `CF88:ART.5:INC.XXXII` | Lei 8.078/1990 - Código de Defesa do Consumidor | ADJUST | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 01 | `CF88:ART.5:INC.XXXIII` | Lei 12.527/2011 - Lei de Acesso à Informação | ADJUST | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 01 | `CF88:ART.5:INC.XLIII` | Lei 8.072/1990 - Lei dos Crimes Hediondos | ADJUST | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 01 | `CF88:ART.5:INC.LXXIX` | Lei 13.709/2018 - Lei Geral de Proteção de Dados | ADJUST | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 01 | `CF88:ART.7:PAR.UNICO` | Lei Complementar nº 150/2015 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 01 | `CF88:ART.9:PAR.2` | Lei 7.783/1989 - Lei de Greve | APPROVE | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 01 | `CF88:ART.14:PAR.9` | Lei Complementar nº 135/2010 | REJECT | — | — | IN_FORCE | — |
| 01 | `CF88:ART.14:PAR.9` | Lei Complementar 64/1990 - Inelegibilidades | APPROVE | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 01 | `CF88:ART.17:PAR.2` | Lei 9.096/1995 - Lei dos Partidos Políticos | APPROVE | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 01 | `CF88:ART.17:PAR.3` | Lei 9.096/1995 - Lei dos Partidos Políticos | APPROVE | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 01 | `CF88:ART.18:PAR.4` | Lei Complementar nº 230/2026 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 01 | `CF88:ART.21:INC.IV` | Lei Complementar nº 90/1997 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 01 | `CF88:ART.21:INC.XXVI` | Lei nº 13.848/2019 | REJECT | — | — | IN_FORCE | — |
| 01 | `CF88:ART.21:INC.XXVI` | Lei nº 15.352/2026 | REJECT | — | — | IN_FORCE | — |
| 01 | `CF88:ART.21:INC.XXVI` | Medida Provisória nº 1317/2025 | REJECT | — | — | REVOKED | — |
| 01 | `CF88:ART.22:INC.XXVII` | Lei nº 13.303/2016 | APPROVE | COMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 01 | `CF88:ART.22:INC.XXVII` | Lei 14.133/2021 - Licitações e Contratos Administrativos | ADJUST | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 01 | `CF88:ART.22:PAR.UNICO` | Lei Complementar nº 103/2000 | ADJUST | IMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 01 | `CF88:ART.23:INC.VI` | Lei Complementar nº 140/2011 | ADJUST | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 01 | `CF88:ART.23:PAR.UNICO` | Lei Complementar nº 140/2011 | ADJUST | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 01 | `CF88:ART.37:PAR.2` | Lei 8.112/1990 - Regime Jurídico dos Servidores Públicos Federais | REJECT | — | — | IN_FORCE | — |
| 01 | `CF88:ART.37:PAR.4` | Lei 8.112/1990 - Regime Jurídico dos Servidores Públicos Federais | REJECT | — | — | IN_FORCE | — |
| 01 | `CF88:ART.37:PAR.4` | Lei 8.429/1992 - Improbidade Administrativa | ADJUST | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 01 | `CF88:ART.37:PAR.5` | Lei 8.112/1990 - Regime Jurídico dos Servidores Públicos Federais | REJECT | — | — | IN_FORCE | — |
| 01 | `CF88:ART.37:PAR.7` | Lei nº 12.813/2013 | APPROVE | IMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 01 | `CF88:ART.40:PAR.1:INC.II` | Lei Complementar nº 152/2015 | ADJUST | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 01 | `CF88:ART.40:PAR.7` | Lei 8.112/1990 - Regime Jurídico dos Servidores Públicos Federais | HOLD | — | — | IN_FORCE | — |
| 01 | `CF88:ART.40:PAR.22` | Lei nº 9.717/1998 | APPROVE | REGULAMENTA | = | TRANSITIONAL | INGESTION_REQUIRED |
| 02 | `CF88:ART.45:PAR.1` | Lei Complementar nº 78/1993 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.49:INC.II` | Lei Complementar nº 90/1997 | ADJUST | CONDIÇÃO_OU_EXCEÇÃO | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.59:PAR.UNICO` | Lei Complementar nº 107/2001 | REJECT | — | — | IN_FORCE | — |
| 02 | `CF88:ART.59:PAR.UNICO` | Lei Complementar nº 95/1998 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.84:INC.XXII` | Lei Complementar nº 90/1997 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.100:PAR.5` | Lei 4.320/1964 - Normas Gerais de Direito Financeiro | REJECT | — | — | IN_FORCE | — |
| 02 | `CF88:ART.102:PAR.2` | Lei nº 9.868/1999 | ADJUST | PROCEDIMENTO | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.103-A:PAR.2` | Lei nº 11.417/2006 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.103-A:PAR.3` | Lei nº 11.417/2006 | ADJUST | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.105:PAR.2` | Lei nº 15.484/2026 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.128:PAR.3` | Lei Complementar nº 75/1993 | ADJUST | IMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.128:PAR.4` | Lei Complementar nº 75/1993 | ADJUST | IMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.129:INC.VI` | Lei Complementar nº 75/1993 | ADJUST | IMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.129:INC.VII` | Lei Complementar nº 75/1993 | ADJUST | IMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.131:PAR.2` | Lei nº 14.965/2024 | APPROVE | COMPLEMENTA | = | VACATIO_LEGIS | DEVICE_RESOLVABLE_NOW, TEMPORAL_DEVICE_BLOCK |
| 02 | `CF88:ART.132` | Lei nº 14.965/2024 | APPROVE | COMPLEMENTA | = | VACATIO_LEGIS | DEVICE_RESOLVABLE_NOW, TEMPORAL_DEVICE_BLOCK |
| 02 | `CF88:ART.134:PAR.1` | Lei Complementar nº 80/1994 | ADJUST | ORGANIZA_INSTITUIÇÃO | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.142:PAR.1` | Lei Complementar nº 83/1995 | REJECT | — | — | REVOKED | — |
| 02 | `CF88:ART.142:PAR.1` | Lei Complementar nº 97/1999 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.142:PAR.3` | Lei Complementar nº 97/1999 | REJECT | — | — | IN_FORCE | — |
| 02 | `CF88:ART.144:PAR.8` | Lei nº 13.022/2014 | ADJUST | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.146:INC.III` | Lei Complementar nº 214/2025 | REJECT | — | — | PARTIAL_EFFECTS | — |
| 02 | `CF88:ART.146:INC.III:AL.b` | Lei Complementar nº 199/2023 | APPROVE | REGULAMENTA | = | IN_FORCE | DEVICE_RESOLVABLE_NOW |
| 02 | `CF88:ART.146:PAR.1` | Lei Complementar nº 123/2006 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 02 | `CF88:ART.146:PAR.1` | Lei Complementar nº 214/2025 | APPROVE | COMPLEMENTA | = | PARTIAL_EFFECTS | INGESTION_REQUIRED |
| 02 | `CF88:ART.153:PAR.3` | Lei Complementar nº 214/2025 | REJECT | — | — | PARTIAL_EFFECTS | — |
| 02 | `CF88:ART.153:PAR.6` | Lei Complementar nº 214/2025 | ADJUST | REGULAMENTA | = | PARTIAL_EFFECTS | INGESTION_REQUIRED |
| 02 | `CF88:ART.155:PAR.1` | Lei Complementar nº 227/2026 | APPROVE | REGULAMENTA | = | PARTIAL_EFFECTS | INGESTION_REQUIRED |
| 02 | `CF88:ART.155:PAR.1:INC.III` | Lei Complementar nº 102/2000 | REJECT | — | — | IN_FORCE | — |
| 02 | `CF88:ART.155:PAR.1:INC.III` | Lei Complementar nº 99/1999 | REJECT | — | — | IN_FORCE | — |
| 03 | `CF88:ART.155:PAR.2` | Lei Complementar nº 214/2025 | REJECT | — | — | PARTIAL_EFFECTS | — |
| 03 | `CF88:ART.155:PAR.2:INC.VII` | Lei Complementar nº 190/2022 | REJECT | — | — | IN_FORCE | — |
| 03 | `CF88:ART.155:PAR.2:INC.VII` | Lei Complementar nº 87/1996 | ADJUST | REGULAMENTA | = | IN_FORCE | DEVICE_RESOLVABLE_NOW |
| 03 | `CF88:ART.155:PAR.2:INC.XII` | Lei Complementar nº 102/2000 | REJECT | — | — | IN_FORCE | — |
| 03 | `CF88:ART.155:PAR.2:INC.XII` | Lei Complementar nº 201/2023 | REJECT | — | — | IN_FORCE | — |
| 03 | `CF88:ART.155:PAR.2:INC.XII` | Lei Complementar nº 24/1975 | ADJUST | REGULAMENTA | CF88:ART.155:PAR.2:INC.XII:AL.g | IN_FORCE | INGESTION_REQUIRED |
| 03 | `CF88:ART.156:PAR.3` | Lei Complementar nº 214/2025 | REJECT | — | — | PARTIAL_EFFECTS | — |
| 03 | `CF88:ART.156-A:PAR.1` | Lei Complementar nº 214/2025 | APPROVE | REGULAMENTA | = | PARTIAL_EFFECTS | INGESTION_REQUIRED |
| 03 | `CF88:ART.156-A:PAR.5` | Lei Complementar nº 214/2025 | APPROVE | REGULAMENTA | = | PARTIAL_EFFECTS | INGESTION_REQUIRED |
| 03 | `CF88:ART.156-A:PAR.5` | Lei Complementar nº 227/2026 | ADJUST | REGULAMENTA | CF88:ART.156-A:PAR.5:INC.VII | PARTIAL_EFFECTS | INGESTION_REQUIRED |
| 03 | `CF88:ART.156-A:PAR.6` | Lei Complementar nº 214/2025 | APPROVE | REGULAMENTA | = | PARTIAL_EFFECTS | INGESTION_REQUIRED |
| 03 | `CF88:ART.156-A:PAR.9` | Lei Complementar nº 214/2025 | APPROVE | REGULAMENTA | = | PARTIAL_EFFECTS | INGESTION_REQUIRED |
| 03 | `CF88:ART.156-A:PAR.13` | Lei Complementar nº 214/2025 | ADJUST | REGULAMENTA | = | PARTIAL_EFFECTS | INGESTION_REQUIRED |
| 03 | `CF88:ART.159:INC.I` | Lei Complementar nº 214/2025 | REJECT | — | — | PARTIAL_EFFECTS | — |
| 03 | `CF88:ART.165:PAR.9` | Lei Complementar 101/2000 - Lei de Responsabilidade Fiscal | ADJUST | COMPLEMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 03 | `CF88:ART.165:PAR.10` | Lei nº 14.436/2022 | REJECT | — | — | TRANSITIONAL | — |
| 03 | `CF88:ART.165:PAR.18` | Lei Complementar nº 200/2023 | APPROVE | COMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 03 | `CF88:ART.166:PAR.9` | Lei Complementar nº 210/2024 | ADJUST | COMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 03 | `CF88:ART.166:PAR.11` | Lei Complementar nº 210/2024 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 03 | `CF88:ART.166:PAR.11` | Lei nº 14.436/2022 | REJECT | — | — | TRANSITIONAL | — |
| 03 | `CF88:ART.169:PAR.3` | Lei Complementar 101/2000 - Lei de Responsabilidade Fiscal | APPROVE | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 03 | `CF88:ART.169:PAR.4` | Lei Complementar 101/2000 - Lei de Responsabilidade Fiscal | ADJUST | COMPLEMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 03 | `CF88:ART.170:PAR.UNICO` | Lei nº 13.874/2019 | ADJUST | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 03 | `CF88:ART.184:PAR.3` | Lei Complementar nº 76/1993 | ADJUST | PROCEDIMENTO | = | IN_FORCE | INGESTION_REQUIRED |
| 03 | `CF88:ART.184:PAR.3` | Lei Complementar nº 93/1998 | REJECT | — | — | IN_FORCE | — |
| 03 | `CF88:ART.195:PAR.1` | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio | REJECT | — | — | IN_FORCE | — |
| 03 | `CF88:ART.195:PAR.3` | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio | ADJUST | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 03 | `CF88:ART.195:PAR.4` | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio | REJECT | — | — | IN_FORCE | — |
| 03 | `CF88:ART.195:PAR.7` | Lei Complementar nº 187/2021 | ADJUST | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 03 | `CF88:ART.195:PAR.7` | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio | REJECT | — | — | IN_FORCE | — |
| 04 | `CF88:ART.195:PAR.8` | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio | ADJUST | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 04 | `CF88:ART.198:PAR.3` | Lei Complementar nº 141/2012 | APPROVE | REGULAMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 04 | `CF88:ART.201:PAR.1` | Lei Complementar nº 142/2013 | ADJUST | REGULAMENTA | CF88:ART.201:PAR.1:INC.I | IN_FORCE | INGESTION_REQUIRED |
| 04 | `CF88:ART.201:PAR.4` | Lei 8.213/1991 - Planos de Benefícios da Previdência Social | ADJUST | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 04 | `CF88:ART.202:PAR.1` | Lei Complementar nº 109/2001 | ADJUST | REGULAMENTA | = | IN_FORCE | DEVICE_RESOLVABLE_NOW |
| 04 | `CF88:ART.227:PAR.3` | Lei 8.069/1990 - Estatuto da Criança e do Adolescente | APPROVE | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 04 | `CF88:ART.227:PAR.4` | Lei 8.069/1990 - Estatuto da Criança e do Adolescente | APPROVE | COMPLEMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 04 | `CF88:ART.227:PAR.5` | Lei 8.069/1990 - Estatuto da Criança e do Adolescente | ADJUST | REGULAMENTA | = | IN_FORCE | MAIN_CORPUS_ROUTE_REQUIRED |
| 04 | `CF88:ART.231:PAR.1` | Lei nº 14.701/2023 | HOLD | — | — | UNCERTAIN | — |
| 04 | `CF88:ART.231:PAR.3` | Lei nº 14.701/2023 | HOLD | — | — | UNCERTAIN | — |
| 04 | `CF88:ART.231:PAR.6` | Lei nº 14.701/2023 | HOLD | — | — | UNCERTAIN | — |
| 04 | `CF88:ART.239` | Lei Complementar nº 7/1970 | APPROVE | COMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 04 | `CF88:ART.239` | Lei Complementar nº 8/1970 | APPROVE | COMPLEMENTA | = | IN_FORCE | INGESTION_REQUIRED |
| 04 | `CF88:ART.239:PAR.3` | Lei nº 7.998/1990 | APPROVE | REGULAMENTA | = | IN_FORCE | DEVICE_RESOLVABLE_NOW |
| 04 | `CF88:ART.239:PAR.4` | Lei nº 7.998/1990 | ADJUST | COMPLEMENTA | = | IN_FORCE | DEVICE_RESOLVABLE_NOW |
| 04 | `ADCT:ART.10:INC.II` | Lei Complementar nº 146/2014 | ADJUST | COMPLEMENTA | ADCT:ART.10:INC.II:AL.b | IN_FORCE | INGESTION_REQUIRED |
| 04 | `ADCT:ART.128:PAR.2` | Lei Complementar nº 160/2017 | APPROVE | COMPLEMENTA | = | TRANSITIONAL | INGESTION_REQUIRED |

## NEW_CANDIDATE_BACKLOG (18; fora dos 106; não decidido)

- **Por prioridade sugerida:** {'HIGH': 7, 'LOW': 2, 'MEDIUM': 9}.

- Lei nº 13.709/2018 (LGPD) × `CF88:ART.21:INC.XXVI` (MEDIUM), origem `—`
- Lei nº 8.429/1992 (LIA), art. 23 × `CF88:ART.37:PAR.5` (MEDIUM), origem `CORRC0-D961094C030C`
- Lei nº 13.303/2016 × `CF88:ART.173:PAR.1:INC.III` (MEDIUM), origem `CORRC0-9C3FB3B95B9B`
- Lei nº 7.783/1989 × `CF88:ART.9` (MEDIUM), origem `CORRC0-142570A4C40E`
- Lei nº 7.783/1989 × `CF88:ART.9:PAR.1` (HIGH), origem `CORRC0-142570A4C40E`
- Lei nº 6.880/1980 (Estatuto dos Militares) × `CF88:ART.142:PAR.3` (MEDIUM), origem `CORRC0-4A61114D26A5`
- Lei Complementar nº 214/2025 × `CF88:ART.156-A` (MEDIUM), origem `CORRC0-E6E419F28886`
- Lei Complementar nº 214/2025 × `CF88:ART.195:INC.V` (HIGH), origem `CORRC0-E6E419F28886`
- Lei Complementar nº 214/2025 (art. 454) × `ADCT (transição Zona Franca, EC 132/2023)` (LOW), origem `CORRC0-83C4D0DE51F8`
- Lei Complementar nº 227/2026 (art. 158) × `CF88:ART.155:PAR.1:INC.III` (HIGH), origem `CORRC0-A97DCCBA85CF`
- Lei nº 11.417/2006 (art. 2º) × `CF88:ART.103-A` (MEDIUM), origem `CORRC0-420E49E80EF9`
- Lei Complementar nº 214/2025 (art. 409) × `CF88:ART.153:INC.VIII` (HIGH), origem `CORRC0-4A80B12218AA`
- Lei Complementar nº 116/2003 (ISS) × `CF88:ART.156:PAR.3` (MEDIUM), origem `CORRC0-A5A1F929253C`
- Lei Complementar nº 227/2026 × `CF88:ART.156-A:PAR.5:INC.I` (HIGH), origem `CORRC0-945D4CF3CD87`
- Lei nº 9.801/1999 × `CF88:ART.169:PAR.4` (HIGH), origem `CORRC0-8A985C226863`
- Lei nº 9.801/1999 × `CF88:ART.169:PAR.7` (HIGH), origem `CORRC0-8A985C226863`
- Lei nº 8.213/1991 (arts. 57 e 58, aposentadoria especial) × `CF88:ART.201:PAR.1:INC.II` (MEDIUM), origem `CORRC0-2053DEF59022`
- Decreto-Lei nº 2.848/1940 (Código Penal, crimes contra a dignidade sexual) × `CF88:ART.227:PAR.4` (LOW), origem `CORRC0-8D80396BDEEB`

## Próximo passo

- Revisão independente dos Batch03 e Batch04 e do fechamento.
- Depois, decisão arquitetural (overlay CORRELATA_ADDITIONS, regra do ADCT, política de vacatio e rota do acervo principal).
- Nada de MEDIUM ou LOW antes disso.

