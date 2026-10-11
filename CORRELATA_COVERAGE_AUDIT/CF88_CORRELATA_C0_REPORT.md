# CF88_CORRELATA_COVERAGE_AUDIT_C0 — cobertura da camada CORRELATA (CF/88 + ADCT)

**Missão diagnóstica.** Nenhum vínculo foi adicionado, removido ou promovido. Os arquivos operacionais do Reference Engine, o microSD, o firmware, o ENTENDA e a Lei Seca não foram alterados.

## Baseline

- Branch criada de `device-entenda-810` @ `44ef69ba3957d9c55a6b4b5fe9f9f68fcd77efef`.
- Tag física: `lex-device-v1-entenda-810-physical-approved-2026-10-11`.
- Reconciliação jurídica: `fa9719a6bd335275252473a5f154e4e11f5532f4`: 810 HUMAN_APPROVED_T1 ACTIVE, 0 pendentes.
- No lookup físico, as 810 explicações aprovadas viram 1069 linhas: 810 DIRECT e 259 COVERED_BY_BLOCK.
- Os 810 **não** são o universo de targets.
- Evidência local congelada em `CORRELATA_COVERAGE_AUDIT/inputs/CORRELATA_EVIDENCE_PIN.json` (sha256 `1ee3376b7e91b4e0…`).
  - Ela reúne o Relations V2 legado, o acervo do cartão, as remissões reversas e as tabelas físicas.
  - Cada fonte tem sha256 próprio.

## Preservação (verificada pela própria auditoria)

- **RUN3:** reconstruído em diretório temporário. É byte-idêntico ao versionado: `True`.
- **REF_LOOKUP/REF_PAYLOAD:** idênticos aos do cartão: `True`.
- **Tabelas do aparelho** (TARGETS, TEXT_MAP, ENTENDA_LOOKUP e REF): conferidas contra o manifesto físico: `True`.
- **Arquivos operacionais:** os sha256 de `CF88_REFERENCES_CANONICAL.json`, `CF88_LINK_EXCLUSIONS.json`, `CF88_WORK_REFERENCE_ADDITIONS.json`, dos três arquivos do RUN3 e do `engine_config.json` ficam registrados no baseline.
  - Os testes os comparam com o commit de origem.

## Números (CF permanente × ADCT)

| Medida | CF | ADCT | Total |
|---|---:|---:|---:|
| Targets do runtime CURRENT/STRUCTURAL (sem NORMA/NAMESPACE; caput contado à parte) | 2876 | 831 | 3707 |
| Excluídos por motivo técnico: NORMA/NAMESPACE + caput dobrado em ART | 277 | 149 | 426 |
| Excluídos por serem históricos ou revogados (revogados no runtime + ausentes do runtime) | 115 | 121 | 236 |
| **Targets auditáveis** | 2603 | 693 | **3296** |
| … artigos (STRUCTURAL, ART ↔ CAPUT) | 273 | 138 | 411 |
| … dispositivos (CURRENT) | 2330 | 555 | 2885 |
| Targets com CORRELATA atual visível | 39 | 0 | 39 |
| **Novos candidatos** (target × norma, promovíveis à revisão) | 708 | 35 | **743** |
| … HIGH | 104 | 2 | 106 |
| … MEDIUM | 190 | 1 | 191 |
| … LOW | 414 | 32 | 446 |
| TOPICAL_ONLY rejeitados (fora da fila) | 35 | 0 | 35 |
| Targets em GENERIC_LEGISLATIVE_RESERVATION | 303 | 93 | 396 |
| Candidatos INGESTION_REQUIRED | 440 | 30 | 470 |
| Candidatos DEVICE_RESOLVABLE_NOW | 47 | 1 | 48 |
| Candidatos com texto no acervo principal (MAIN_CORPUS_ROUTE_REQUIRED) | 221 | 4 | 225 |
| Targets em NEEDS_HUMAN_REVIEW | 1898 | 574 | 2472 |

**Leitura dos números**

- **CORRELATAs atuais:** 46 links no export RUN3, dos quais 44 visíveis e 2 ocultos (alvo HISTORICAL_ONLY).
  - Os 44 visíveis estão em 39 targets e vêm de 23 relações e 20 normas externas.
  - O número foi derivado do export, não de relatório.
- **Itens de revisão humana:** 743 candidatos, mais 19 vínculos atuais com inconsistência evidente, mais 2472 targets em NEEDS_HUMAN_REVIEW.
  - Destes targets, 2381 não tiveram nenhum sinal automático. É ausência não confirmada, não ausência comprovada.
- **NO_CORRELATA_RELEVANT = 0, por desenho.** A busca textual sem sinal não basta para afirmar que um target não tem correlata.
  - Esse estado exige confirmação humana, prevista para C1.
- **Contagens de dispositivo** (por candidato target × norma):
  - DEVICE_RESOLVABLE_NOW: 48 candidatos, em 14 normas.
    - O texto e o índice de artigos já estão no cartão (EXT_NORMAS/EXT_ARTIGOS).
    - Falta só a relação aprovada e a linha RELACOES.
  - INGESTION_REQUIRED: 470 candidatos, em 314 normas sem texto no cartão.
  - MAIN_CORPUS_ROUTE_REQUIRED: 225 candidatos, em 46 normas.
    - O texto já está no cartão como norma principal, mas a rota CORRELATA → norma principal nunca foi exercitada no DEVICE V1.
    - O botão 1 resolve por `RELACOES.IDX`, e o salto de artigo usa `EXT_ARTIGOS`, que só existe para as externas.
- **EXTERNAL_VERIFICATION_REQUIRED:** 295 candidatos, por um destes motivos:
  - vigência sem evidência local;
  - norma recente sem proveniência oficial;
  - identidade vinda de alias do auditor.
- **Overlay bloqueado no ADCT:** 23 candidatos estão em targets com status do motor fora de CURRENT/STRUCTURAL (ADCT = UNKNOWN_VALIDITY).
  - O overlay atual do Reference Engine rejeitaria esses candidatos. Ver a seção de arquitetura.

## Os vínculos atuais (inventário em `CF88_CORRELATA_CURRENT_BASELINE.json`)

| Target | Norma destino | Visível | Citação no texto da norma | Avaliação C0 |
|---|---|---|---|---|
| CF art. 5, XLIII | Lei nº 13.260/2016 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 20, § 1 | Lei nº 12.734/2012 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 20, § 1 | Lei nº 9.984/2000 | sim | DESTINO_NAO_CITA_O_TARGET | NEEDS_REVIEW |
| CF art. 34, V, b) | Lei Complementar nº 63/1990 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 37, II | Lei nº 14.965/2024 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 37, § 3, I | Lei nº 13.460/2017 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 37, § 3, II | Lei nº 13.460/2017 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | NEEDS_REVIEW |
| CF art. 37, § 3, III | Lei nº 13.460/2017 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | NEEDS_REVIEW |
| CF art. 43, § 1, I | Lei Complementar nº 112/2001 | sim | DESTINO_CITA_O_DISPOSITIVO_SUPERIOR | NEEDS_REVIEW |
| CF art. 43, § 1, II | Lei Complementar nº 112/2001 | sim | DESTINO_CITA_O_DISPOSITIVO_SUPERIOR | NEEDS_REVIEW |
| CF art. 146 | Lei Complementar nº 199/2023 | sim | DESTINO_CITA_SUBDIVISAO_DO_TARGET | PLAUSIBLE_STRONG |
| CF art. 150, § 7 | Lei Complementar nº 87/1996 | sim | DESTINO_NAO_CITA_O_TARGET | PLAUSIBLE_NOT_VERIFIED |
| CF art. 153, § 4, II | Lei nº 11.250/2005 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | NEEDS_REVIEW |
| CF art. 153, § 4, II | Lei nº 8.981/1995 | sim | DESTINO_NAO_CITA_O_TARGET | NEEDS_REVIEW |
| CF art. 153, § 4, II | Lei nº 9.393/1996 | sim | DESTINO_CITA_O_DISPOSITIVO_SUPERIOR | PLAUSIBLE_NOT_VERIFIED |
| CF art. 153, § 4, III | Lei nº 11.250/2005 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 153, § 4, III | Lei nº 8.981/1995 | sim | DESTINO_NAO_CITA_O_TARGET | NEEDS_REVIEW |
| CF art. 153, § 4, III | Lei nº 9.393/1996 | sim | DESTINO_CITA_O_DISPOSITIVO_SUPERIOR | NEEDS_REVIEW |
| CF art. 155, § 1, III | Lei Complementar nº 87/1996 | sim | DESTINO_NAO_CITA_O_TARGET | NEEDS_REVIEW |
| CF art. 155, § 2, XII | Lei Complementar nº 87/1996 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | PLAUSIBLE_NOT_VERIFIED |
| CF art. 158, § 1, II | Lei Complementar nº 63/1990 | sim | DESTINO_NAO_CITA_O_TARGET | PLAUSIBLE_NOT_VERIFIED |
| CF art. 161, I | Lei Complementar nº 62/1989 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | NEEDS_REVIEW |
| CF art. 161, II | Lei Complementar nº 62/1989 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 161, III | Lei Complementar nº 62/1989 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 182 | Lei nº 13.425/2017 | sim | DESTINO_CITA_SUBDIVISAO_DO_TARGET | NEEDS_REVIEW |
| CF art. 195, I | Lei Complementar nº 70/1991 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 195, II | Lei Complementar nº 70/1991 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | NEEDS_REVIEW |
| CF art. 195, § 1 | Lei Complementar nº 70/1991 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | NEEDS_REVIEW |
| CF art. 195, § 2 | Lei Complementar nº 70/1991 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | NEEDS_REVIEW |
| CF art. 201, I | Lei nº 7.998/1990 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | NEEDS_REVIEW |
| CF art. 201, II | Lei nº 7.998/1990 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | NEEDS_REVIEW |
| CF art. 201, III | Lei nº 7.998/1990 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | PLAUSIBLE_NOT_VERIFIED |
| CF art. 201, IV | Lei nº 7.998/1990 | sim | DESTINO_CITA_O_TARGET | NEEDS_REVIEW |
| CF art. 201, V | Lei nº 7.998/1990 | sim | DESTINO_CITA_SO_DISPOSITIVO_IRMAO | NEEDS_REVIEW |
| CF art. 202, caput | Lei Complementar nº 109/2001 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 202, § 4 | Lei Complementar nº 108/2001 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 202, § 5 | Lei Complementar nº 108/2001 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 202, § 6 | Lei Complementar nº 108/2001 | sim | DESTINO_CITA_O_TARGET | PLAUSIBLE_STRONG |
| CF art. 214, I | Lei nº 15.388/2026 | sim | DESTINO_CITA_O_DISPOSITIVO_SUPERIOR | PLAUSIBLE_NOT_VERIFIED |
| CF art. 214, II | Lei nº 15.388/2026 | sim | DESTINO_CITA_O_DISPOSITIVO_SUPERIOR | PLAUSIBLE_NOT_VERIFIED |
| CF art. 214, III | Lei nº 15.388/2026 | sim | DESTINO_CITA_O_DISPOSITIVO_SUPERIOR | PLAUSIBLE_NOT_VERIFIED |
| CF art. 214, IV | Lei nº 15.388/2026 | sim | DESTINO_CITA_O_DISPOSITIVO_SUPERIOR | PLAUSIBLE_NOT_VERIFIED |
| CF art. 214, V | Lei nº 15.388/2026 | sim | DESTINO_CITA_O_DISPOSITIVO_SUPERIOR | PLAUSIBLE_NOT_VERIFIED |
| CF art. 214, VI | Lei nº 15.388/2026 | sim | DESTINO_CITA_O_DISPOSITIVO_SUPERIOR | PLAUSIBLE_NOT_VERIFIED |
| CF art. 40, § 4, II | Lei Complementar nº 144/2014 | não | DESTINO_NAO_CITA_O_TARGET | OBSOLETE_HIDDEN |
| CF art. 40, § 4, III | Lei Complementar nº 144/2014 | não | DESTINO_NAO_CITA_O_TARGET | OBSOLETE_HIDDEN |

**Leitura da tabela**

- **PLAUSIBLE_STRONG:** o texto da norma de destino cita literalmente o target.
- **PLAUSIBLE_NOT_VERIFIED:** nenhuma evidência contrária, mas sem prova local.
- **NEEDS_REVIEW:** inconsistência evidente, como dispositivo irmão, ementa alheia ou fan-out. As razões estão em `review_flags` e na fila `CURRENT_LINK_REVIEW`.
- **OBSOLETE_HIDDEN:** vínculo sobre target HISTORICAL_ONLY, oculto no aparelho. Exemplo: art. 40, § 4º, II/III × LC 144/2014, após a EC 103/2019.
- **Revalidação externa:** nenhum vínculo foi revalidado por pesquisa externa nesta C0.

## Ranking diagnóstico das normas candidatas (planejamento de ingestão; frequência NÃO é prova jurídica)

| # | Norma | Targets candidatos | HIGH | Acervo | Dispositivo |
|---:|---|---:|---:|---|---|
| 1 | Lei Complementar 101/2000 - Lei de Responsabilidade Fiscal (`LC:101/2000`) | 35 | 3 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 2 | Lei 8.213/1991 - Planos de Benefícios da Previdência Social (`LEI:8213/1991`) | 16 | 1 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 3 | Decreto 3.048/1999 - Regulamento da Previdência Social (`DEC:3048/1999`) | 15 | 0 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 4 | Lei Complementar nº 214/2025 (`LC:214/2025`) | 15 | 12 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 5 | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio (`LEI:8212/1991`) | 12 | 5 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 6 | Lei Complementar nº 63/1990 (`LC:63/1990`) | 9 | 0 | EXTERNAL_ALREADY_INGESTED | DEVICE_RESOLVABLE_NOW |
| 7 | Lei Complementar nº 75/1993 (`LC:75/1993`) | 8 | 4 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 8 | Lei Complementar nº 87/1996 (`LC:87/1996`) | 8 | 1 | EXTERNAL_ALREADY_INGESTED | DEVICE_RESOLVABLE_NOW |
| 9 | Lei nº 10.332/2001 (`LEI:10332/2001`) | 8 | 0 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 10 | Lei nº 10.669/2003 (`LEI:10669/2003`) | 8 | 0 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 11 | Lei nº 14.965/2024 (`LEI:14965/2024`) | 8 | 2 | EXTERNAL_ALREADY_INGESTED | DEVICE_RESOLVABLE_NOW |
| 12 | Lei 8.112/1990 - Regime Jurídico dos Servidores Públicos Federais (`LEI:8112/1990`) | 8 | 4 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 13 | Lei 8.629/1993 - Reforma Agrária (`LEI:8629/1993`) | 8 | 0 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 14 | Lei 5.172/1966 - Código Tributário Nacional (`LEI:5172/1966`) | 7 | 0 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 15 | Decreto-Lei 2.848/1940 - Código Penal (`DL:2848/1940`) | 6 | 0 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 16 | Lei 10.259/2001 - Juizados Especiais Federais (`LEI:10259/2001`) | 6 | 0 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 17 | Lei 10.406/2002 - Código Civil (`LEI:10406/2002`) | 6 | 0 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 18 | Lei 13.105/2015 - Código de Processo Civil (`LEI:13105/2015`) | 6 | 0 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 19 | Lei nº 15.388/2026 (`LEI:15388/2026`) | 6 | 0 | EXTERNAL_ALREADY_INGESTED | DEVICE_RESOLVABLE_NOW |
| 20 | Lei 9.504/1997 - Lei das Eleições (`LEI:9504/1997`) | 6 | 0 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 21 | Lei nº 9.717/1998 (`LEI:9717/1998`) | 6 | 1 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 22 | Decreto-Lei 3.689/1941 - Código de Processo Penal (`DL:3689/1941`) | 5 | 0 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 23 | Decreto-Lei 5.452/1943 - CLT (`DL:5452/1943`) | 5 | 0 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 24 | Lei Complementar nº 102/2000 (`LC:102/2000`) | 5 | 2 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 25 | Lei Complementar 64/1990 - Inelegibilidades (`LC:64/1990`) | 5 | 1 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 26 | Lei Complementar nº 77/1993 (`LC:77/1993`) | 5 | 0 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 27 | Lei Complementar nº 99/1999 (`LC:99/1999`) | 5 | 1 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 28 | Lei nº 10.256/2001 (`LEI:10256/2001`) | 5 | 0 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 29 | Lei 13.709/2018 - Lei Geral de Proteção de Dados (`LEI:13709/2018`) | 5 | 1 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 30 | Lei 8.069/1990 - Estatuto da Criança e do Adolescente (`LEI:8069/1990`) | 5 | 3 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 31 | Lei 8.072/1990 - Lei dos Crimes Hediondos (`LEI:8072/1990`) | 5 | 1 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 32 | Lei 8.078/1990 - Código de Defesa do Consumidor (`LEI:8078/1990`) | 5 | 1 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 33 | Lei nº 8.861/1994 (`LEI:8861/1994`) | 5 | 0 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 34 | Lei nº 8.870/1994 (`LEI:8870/1994`) | 5 | 0 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 35 | Lei nº 9.478/1997 (`LEI:9478/1997`) | 5 | 0 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 36 | Lei Complementar nº 227/2026 (`LC:227/2026`) | 4 | 2 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 37 | Lei Complementar nº 91/1997 (`LC:91/1997`) | 4 | 0 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 38 | Lei 12.527/2011 - Lei de Acesso à Informação (`LEI:12527/2011`) | 4 | 1 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |
| 39 | Lei nº 14.436/2022 (`LEI:14436/2022`) | 4 | 2 | INGESTION_REQUIRED | INGESTION_REQUIRED |
| 40 | Lei 4.320/1964 - Normas Gerais de Direito Financeiro (`LEI:4320/1964`) | 4 | 1 | IN_MAIN_CORPUS | MAIN_CORPUS_ROUTE_REQUIRED |

_374 normas distintas entre os candidatos. Lista completa em `CF88_CORRELATA_CANDIDATES.json`._

## Reforma tributária e áreas recentes (EC 132/2023, EC 136–139, LC 214/2025, LC 227/2026)

- **Recorte:** arts. 145 a 162 da CF (inclui 149-A a 149-C e 156-A), arts. 120 a 139 do ADCT e as normas recentes listadas.
- **Base:** só o estado jurídico já registrado no projeto.
- **Registros no recorte:** 142. Por estado: ALREADY_CURRENT_LINK 12, CANDIDATE_FOR_HUMAN_REVIEW 112, HISTORICAL_NORM_EXCLUDED 14, TOPICAL_ONLY_REJECTED 4.
- **Candidatos com LC 214/2025, LC 227/2026 ou EC recentes como norma:** 19.
  - Vêm do ENTENDA aprovado.
  - A vigência e o encaixe no dispositivo exigem EXTERNAL_VERIFICATION_REQUIRED quando o registro não tem proveniência oficial.
  - Essas normas não estão no cartão (INGESTION_REQUIRED).
  - CF art. 146, III × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 146, § 1 × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 149-B × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, MEDIUM, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 149-C × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, MEDIUM, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 149-C × Lei Complementar nº 227/2026: CANDIDATE_FOR_HUMAN_REVIEW, B, MEDIUM, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 153, § 3 × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 153, § 6 × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 155, § 1 × Lei Complementar nº 227/2026: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 155, § 2 × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 156, § 3 × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 156-A, § 1 × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 156-A, § 5 × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 156-A, § 5 × Lei Complementar nº 227/2026: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 156-A, § 6 × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 156-A, § 9 × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 156-A, § 13 × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 156-B × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, MEDIUM, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 156-B × Lei Complementar nº 227/2026: CANDIDATE_FOR_HUMAN_REVIEW, B, MEDIUM, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
  - CF art. 159, I × Lei Complementar nº 214/2025: CANDIDATE_FOR_HUMAN_REVIEW, B, HIGH, INGESTION_REQUIRED, EXTERNAL_VERIFICATION_REQUIRED.
- **Afirmações novas:** nada foi afirmado sem base local. Status novo de norma ou vigência pós-2026 fica como EXTERNAL_VERIFICATION_REQUIRED.

## Classes incluídas e excluídas

- **source:** CF88_RUNTIME (Compilacao Monovigente, CF88 + ADCT) = bytes do cartao; parser aprovado (runtime_targets.build_runtime_index)
- **legal_status:** runtime_targets.runtime_status: (Revogado)/(Suprimido) -> REVOKED; demais -> CURRENT (identico ao CF88_TARGETS.IDX do cartao)
- **included:**
  - CURRENT: paragrafo, paragrafo unico, inciso, alinea vigentes e alcancaveis (linha propria no TEXT_MAP)
  - STRUCTURAL: ART.n vigente (unidade de apresentacao ART.n <-> ART.n:CAPUT; status STRUCTURAL no motor)
- **excluded:**
  - TECHNICAL_TARGET_EXCLUDED/NORMA_OU_NAMESPACE: CF88, ADCT
  - TECHNICAL_TARGET_EXCLUDED/PRESENTATION_EQUIVALENCE_ART_CAPUT: ART.n:CAPUT dobrado na linha de ART.n (unica equivalencia permitida)
  - HISTORICAL_OR_REVOKED_EXCLUDED/REVOGADO_NO_RUNTIME_MONOVIGENTE: (Revogado)/(Suprimido) no runtime
  - HISTORICAL_OR_REVOKED_EXCLUDED/AUSENTE_DO_RUNTIME: target so do indice legado (HISTORICAL_ONLY, renumerado, ADCT do cf.txt antigo)
- **no_inheritance:** nenhuma heranca automatica artigo->paragrafo->inciso ou caput->descendente; cada candidato fica no target da evidencia
- **engine_status_note:** o status do motor (CF88_TARGET_STATUS) marca o ADCT como UNKNOWN_VALIDITY (texto operacional antigo sem ADCT): o overlay atual do Reference Engine so aceita CURRENT/STRUCTURAL -> candidatos ADCT exigem regra de status no overlay futuro

## Sinais (mantidos separados em cada candidato)

- **S1_RESERVA_LEGAL** (730 reservas em 625 linhas de auditoria; nao geram candidato por si): remissao generica a lei no texto constitucional do proprio target (nunca vira norma especifica sozinha)
- **S2_REMISSAO_NOMINAL** (50 sinais): lei/LC/decreto citado por numero no texto constitucional do proprio target
- **S2_NOTA_EDITORIAL_VIDE** (9 sinais): nota editorial 'Vide a Lei ...' da compilacao do Senado: sinal fraco (C), nao conta como familia independente
- **S3_ENTENDA** (128 sinais): mencao a norma no ENTENDA aprovado (conteudo + camadas externas), T1_EXTERNAL_CATALOG e backlog ENTENDA (sinal, nunca fonte)
- **S4_ACERVO_REVERSO** (287 sinais): norma do acervo (principal ou externa no cartao) que cita literalmente o dispositivo (citation_parser, fail closed)
- **S5_RELATIONS_V2_LEGADO** (726 sinais): registros das etapas 2D4..2E4 do Relations V2 (Camara leginfra / varredura reversa antiga): evidencia, nunca autoridade
- **Rejeitados:** 39 sinais apontavam para target inexistente ou ausente do runtime.
  - Exemplo: chaves legadas de redação revogada.
  - Ficam listados em `rejected_signals` e nunca viram candidato.
- **Emendas constitucionais citadas no texto:** são registradas como norma constitucional, não como correlata.

## Arquitetura futura (somente recomendação; nada implementado)

**Recomendação: overlay `LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json`**, análogo a `CF88_WORK_REFERENCE_ADDITIONS.json`.

- **Catálogo importado:** o `CF88_REFERENCES_CANONICAL.json` legado nunca é editado. As exclusões continuam em `CF88_LINK_EXCLUSIONS.json`.
- **Schema por registro:**
  - `relation_id` e `target_id` (canônico; ART × CAPUT decidido no registro);
  - `destination_norm_id` e `relation_type`, com a taxonomia desta C0;
  - `legal_basis` (dispositivo e fundamento) e `source/provenance`;
  - `review_status`, com valor `HUMAN_APPROVED_CORRELATA_V1`;
  - `reviewer` e `decision_id`;
  - `device_route`: `EXT_NORMAS` ou `MAIN_CORPUS`, com `artigos_destino`.
- **Comportamento fail closed**, espelhando `work_reference_additions()`:
  - campo ausente, status não aprovado, norma fora do registro ou duplicata (target, norma) param o build;
  - target revogado ou histórico para o build.
- **Pontos a decidir antes de C2:**
  1. **Regra de status para o ADCT.** O motor marca o ADCT como UNKNOWN_VALIDITY. O overlay deveria usar o status do runtime (CF88_TARGETS.IDX) ou consolidar a errata.
  2. **Rota de dispositivo para normas do acervo principal.** Hoje o botão 1 só abre RELACOES → EXT_NORMAS.
  3. **Limites do cache legado.** São 64 linhas de lookup e 32 normas, com truncamento silencioso.
     - Ver `DEVICE_INTEGRATION/RELATIONS_V2_LEGACY_64_LINE_LIMIT.md`.
     - Hoje há 20 normas externas no cartão. A expansão precisa da correção antes de passar de 32 normas.
  4. **Relação nova no cartão.** Cada relação aprovada precisa de uma linha RELACOES no cartão, porque o firmware resolve o item pelo `relacao_id`.

## Próximos passos sugeridos

- **C1:** revisão humana.
  - Primeiro a fila HIGH, depois os vínculos atuais com NEEDS_REVIEW.
  - Depois a confirmação de ausência nos targets sem sinal.
- **C2:** overlay CORRELATA_ADDITIONS, com o schema acima, e RUN4 em candidato.
- **C3:** ingestão das normas INGESTION_REQUIRED aprovadas e da rota do acervo principal.

## Artefatos

- `CORRELATA_COVERAGE_AUDIT/CF88_CORRELATA_CURRENT_BASELINE.json`
- `CORRELATA_COVERAGE_AUDIT/CF88_CORRELATA_TARGET_UNIVERSE.json`
- `CORRELATA_COVERAGE_AUDIT/CF88_CORRELATA_CANDIDATES.json`
- `CORRELATA_COVERAGE_AUDIT/CF88_CORRELATA_COVERAGE_MATRIX.csv`
- `CORRELATA_COVERAGE_AUDIT/CF88_CORRELATA_REVIEW_QUEUE.json`
- `CORRELATA_COVERAGE_AUDIT/CF88_CORRELATA_C0_REPORT.md`
- `CORRELATA_COVERAGE_AUDIT/inputs/CORRELATA_EVIDENCE_PIN.json`: evidência local congelada.
- `CORRELATA_COVERAGE_AUDIT/tools/`: o pin e a auditoria.
- `CORRELATA_COVERAGE_AUDIT/tests/`: os testes.

