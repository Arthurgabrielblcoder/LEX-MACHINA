# CF88_CORRELATA_C1B — HIGH Batch03

**Revisão jurídica assistida. Nada foi aplicado.** Não houve ADDITIONS, exclusões, RUN4, nem alteração no SD ou no firmware.

## Lote

- **Seleção:** fila HIGH original da C0 (106) menos os já decididos; 47 elegíveis antes do lote, em ordem estrutural do Target Index.
- **Tamanho:** entraram 30. HIGH originais restantes depois: **17**.
- **Fontes:** só oficiais (Planalto), verificadas em 2026-10-11, com sha256 de cada página.
- **Campos obrigatórios:** cada candidato tem `temporal_status`. Decisão jurídica e rota de aparelho ficam separadas.

## Contabilidade

| Decisão | n |
|---|---:|
| APPROVE | 7 |
| ADJUST | 11 |
| REJECT | 12 |
| HOLD | 0 |
| NEEDS_SOURCE | 0 |
| **Total** | **30** |

| Aceitos (APPROVE + ADJUST): rota de aparelho | n |
|---|---:|
| MAIN_CORPUS_ROUTE_REQUIRED | 4 |
| INGESTION_REQUIRED | 13 |
| DEVICE_RESOLVABLE_NOW | 1 |
| TEMPORAL_DEVICE_BLOCK | 0 |

- **Situação temporal dos aceitos:** {'IN_FORCE': 12, 'PARTIAL_EFFECTS': 6}.
- **Overlay:** aceitos em target com status do motor fora de CURRENT/STRUCTURAL (ADCT): 0.
- **Ajustes:** natureza reclassificada em 9; target ajustado em 2.
- **CF × ADCT:** {'CF88': {'ADJUST': 11, 'APPROVE': 7, 'REJECT': 12}, 'ADCT': {}}.

## Decisões

| # | Target | Norma | Decisão | Natureza | Target final | Temporal | Escopo | Aparelho |
|---:|---|---|---|---|---|---|---|---|
| 1 | CF art. 155, § 2 | Lei Complementar nº 214/2025 | **REJECT** | — | — | PARTIAL_EFFECTS | — | — |
| 2 | CF art. 155, § 2, VII | Lei Complementar nº 190/2022 | **REJECT** | — | — | IN_FORCE | — | — |
| 3 | CF art. 155, § 2, VII | Lei Complementar nº 87/1996 | **ADJUST** | REGULAMENTA | = | IN_FORCE | — | DEVICE_RESOLVABLE_NOW |
| 4 | CF art. 155, § 2, XII | Lei Complementar nº 102/2000 | **REJECT** | — | — | IN_FORCE | — | — |
| 5 | CF art. 155, § 2, XII | Lei Complementar nº 201/2023 | **REJECT** | — | — | IN_FORCE | — | — |
| 6 | CF art. 155, § 2, XII | Lei Complementar nº 24/1975 | **ADJUST** | REGULAMENTA | CF88:ART.155:PAR.2:INC.XII:AL.g | IN_FORCE | — | INGESTION_REQUIRED |
| 7 | CF art. 156, § 3 | Lei Complementar nº 214/2025 | **REJECT** | — | — | PARTIAL_EFFECTS | — | — |
| 8 | CF art. 156-A, § 1 | Lei Complementar nº 214/2025 | **APPROVE** | REGULAMENTA | = | PARTIAL_EFFECTS | NON_EXCLUSIVE | INGESTION_REQUIRED |
| 9 | CF art. 156-A, § 5 | Lei Complementar nº 214/2025 | **APPROVE** | REGULAMENTA | = | PARTIAL_EFFECTS | ESCOPO_PARCIAL, NON_EXCLUSIVE | INGESTION_REQUIRED |
| 10 | CF art. 156-A, § 5 | Lei Complementar nº 227/2026 | **ADJUST** | REGULAMENTA | CF88:ART.156-A:PAR.5:INC.VII | PARTIAL_EFFECTS | — | INGESTION_REQUIRED |
| 11 | CF art. 156-A, § 6 | Lei Complementar nº 214/2025 | **APPROVE** | REGULAMENTA | = | PARTIAL_EFFECTS | — | INGESTION_REQUIRED |
| 12 | CF art. 156-A, § 9 | Lei Complementar nº 214/2025 | **APPROVE** | REGULAMENTA | = | PARTIAL_EFFECTS | — | INGESTION_REQUIRED |
| 13 | CF art. 156-A, § 13 | Lei Complementar nº 214/2025 | **ADJUST** | REGULAMENTA | = | PARTIAL_EFFECTS | — | INGESTION_REQUIRED |
| 14 | CF art. 159, I | Lei Complementar nº 214/2025 | **REJECT** | — | — | PARTIAL_EFFECTS | — | — |
| 15 | CF art. 165, § 9 | Lei Complementar 101/2000 - Lei de Responsabilidade Fiscal | **ADJUST** | COMPLEMENTA | = | IN_FORCE | ESCOPO_PARCIAL, NON_EXCLUSIVE | MAIN_CORPUS_ROUTE_REQUIRED |
| 16 | CF art. 165, § 10 | Lei nº 14.436/2022 | **REJECT** | — | — | TRANSITIONAL | — | — |
| 17 | CF art. 165, § 18 | Lei Complementar nº 200/2023 | **APPROVE** | COMPLEMENTA | = | IN_FORCE | — | INGESTION_REQUIRED |
| 18 | CF art. 166, § 9 | Lei Complementar nº 210/2024 | **ADJUST** | COMPLEMENTA | = | IN_FORCE | — | INGESTION_REQUIRED |
| 19 | CF art. 166, § 11 | Lei Complementar nº 210/2024 | **APPROVE** | REGULAMENTA | = | IN_FORCE | NON_EXCLUSIVE | INGESTION_REQUIRED |
| 20 | CF art. 166, § 11 | Lei nº 14.436/2022 | **REJECT** | — | — | TRANSITIONAL | — | — |
| 21 | CF art. 169, § 3 | Lei Complementar 101/2000 - Lei de Responsabilidade Fiscal | **APPROVE** | REGULAMENTA | = | IN_FORCE | — | MAIN_CORPUS_ROUTE_REQUIRED |
| 22 | CF art. 169, § 4 | Lei Complementar 101/2000 - Lei de Responsabilidade Fiscal | **ADJUST** | COMPLEMENTA | = | IN_FORCE | NON_EXCLUSIVE | MAIN_CORPUS_ROUTE_REQUIRED |
| 23 | CF art. 170, p.u. | Lei nº 13.874/2019 | **ADJUST** | REGULAMENTA | = | IN_FORCE | NON_EXCLUSIVE | INGESTION_REQUIRED |
| 24 | CF art. 184, § 3 | Lei Complementar nº 76/1993 | **ADJUST** | PROCEDIMENTO | = | IN_FORCE | — | INGESTION_REQUIRED |
| 25 | CF art. 184, § 3 | Lei Complementar nº 93/1998 | **REJECT** | — | — | IN_FORCE | — | — |
| 26 | CF art. 195, § 1 | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio | **REJECT** | — | — | IN_FORCE | — | — |
| 27 | CF art. 195, § 3 | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio | **ADJUST** | REGULAMENTA | = | IN_FORCE | — | MAIN_CORPUS_ROUTE_REQUIRED |
| 28 | CF art. 195, § 4 | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio | **REJECT** | — | — | IN_FORCE | — | — |
| 29 | CF art. 195, § 7 | Lei Complementar nº 187/2021 | **ADJUST** | REGULAMENTA | = | IN_FORCE | — | INGESTION_REQUIRED |
| 30 | CF art. 195, § 7 | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio | **REJECT** | — | — | IN_FORCE | — | — |

### 1. CF art. 155, § 2 × Lei Complementar nº 214/2025: **REJECT** (MEDIA)

- **candidate_id:** `CORRC0-ED340FAA29A6`
- **Target:** `CF88:ART.155:PAR.2`; target final `None`; rota —.
- **Sinais C0:** S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** PARTIAL_EFFECTS; vigência 2025-01-16 (publicação; efeitos escalonados no art. 544); revalidar em 2027-01-01. LC 214/2025, art. 544: vigência na publicação, com produção de efeitos escalonada; transição do IBS/CBS até 2033.
- **Fonte oficial:**
  - Lei Complementar nº 214/2025: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm (2026-10-11, sha256 `56324955fe0d7644…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** Ementa da LC 214: institui o IBS, a CBS e o Imposto Seletivo. A redução e a extinção do ICMS estão no próprio ADCT (arts. 128 e 129), não em regras da LC 214 sobre o § 2º do art. 155.
- **Análise:** O § 2º fixa o regime constitucional do ICMS (não cumulatividade, seletividade, alíquotas, DIFAL, lei complementar). A LC 214 não disciplina esses atributos. A ligação com o ICMS é de transição e substituição, e a ENTENDA cita os arts. 128 e 129 do ADCT. A relação é temática.

### 2. CF art. 155, § 2, VII × Lei Complementar nº 190/2022: **REJECT** (ALTA)

- **candidate_id:** `CORRC0-FB5381D4D3A5`
- **Target:** `CF88:ART.155:PAR.2:INC.VII`; target final `None`; rota —.
- **Sinais C0:** S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 190/2022: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp190.htm (2026-10-11, sha256 `6b1863792fd850cd…`)
  - Lei Complementar nº 87/1996 (ICMS): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp87.htm (2026-10-11, sha256 `47bb22063ba170cd…`)
- **Dispositivos relevantes:** Ementa: "Altera a Lei Complementar nº 87 ... para regulamentar a cobrança do ICMS nas operações e prestações interestaduais destinadas a consumidor final não contribuinte". Os dispositivos estão incorporados à LC 87 (ex.: art. 4º, § 2º; art. 11, § 7º; art. 12, XVI). O art. 3º trata da produção de efeitos.
- **Análise:** É lei alteradora: a disciplina vigente do DIFAL está no texto compilado da LC 87, avaliada neste lote. O conteúdo autônomo que sobra é só a regra de produção de efeitos (art. 3º), já exaurida.
- **Observações:** ALTERADORA_INCORPORADA.

### 3. CF art. 155, § 2, VII × Lei Complementar nº 87/1996: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-BD6BE3620174`
- **Target:** `CF88:ART.155:PAR.2:INC.VII`; target final `CF88:ART.155:PAR.2:INC.VII`; rota art. 4º, § 2º (e art. 11, § 7º).
- **Sinais C0:** S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE; revalidar em 2033-01-01. ICMS em extinção gradual pela EC 132/2023 (ADCT, arts. 128 e 129).
- **Fonte oficial:**
  - Lei Complementar nº 87/1996 (ICMS): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp87.htm (2026-10-11, sha256 `47bb22063ba170cd…`)
  - Lei Complementar nº 190/2022: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp190.htm (2026-10-11, sha256 `6b1863792fd850cd…`)
- **Dispositivos relevantes:** LC 87/1996, na redação da LC 190/2022: fato gerador da saída a consumidor final não contribuinte de outro Estado (art. 12, XVI) e cálculo e sujeição da diferença de alíquotas (art. 4º, § 2º; art. 11, § 7º).
- **Análise:** O inciso VII atribui ao Estado de destino a diferença entre alíquotas. A LC 87 é a lei complementar de normas gerais que viabiliza essa cobrança. A natureza muda de COMPLEMENTA para REGULAMENTA.

### 4. CF art. 155, § 2, XII × Lei Complementar nº 102/2000: **REJECT** (ALTA)

- **candidate_id:** `CORRC0-EFBBD4456F98`
- **Target:** `CF88:ART.155:PAR.2:INC.XII`; target final `None`; rota —.
- **Sinais C0:** S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 102/2000: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp102.htm (2026-10-11, sha256 `9320865d69ec2ed7…`)
- **Dispositivos relevantes:** Ementa: "Altera dispositivos da Lei Complementar nº 87".
- **Análise:** Lei alteradora sem disciplina autônoma vigente: as alterações estão incorporadas à LC 87, a lei-base do inciso XII.
- **Observações:** ALTERADORA_INCORPORADA.

### 5. CF art. 155, § 2, XII × Lei Complementar nº 201/2023: **REJECT** (ALTA)

- **candidate_id:** `CORRC0-0EF4365F1CB4`
- **Target:** `CF88:ART.155:PAR.2:INC.XII`; target final `None`; rota —.
- **Sinais C0:** S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 201/2023: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp201.htm (2026-10-11, sha256 `ec15b7a30e9d0e39…`)
- **Dispositivos relevantes:** Ementa: "Dispõe sobre a compensação devida pela União nos termos dos arts. 3º e 14 da Lei Complementar nº 194, de 2022, a dedução das parcelas dos contratos de dívida...".
- **Análise:** O inciso XII lista matérias reservadas à lei complementar do ICMS. A LC 201 trata da compensação financeira federativa por perdas de arrecadação, não dessas matérias. A relação é temática.

### 6. CF art. 155, § 2, XII × Lei Complementar nº 24/1975: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-546E42DB4BCA`
- **Target:** `CF88:ART.155:PAR.2:INC.XII`; target final `CF88:ART.155:PAR.2:INC.XII:AL.g`; rota arts. 1º e 2º.
- **Sinais C0:** S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE; revalidar em 2033-01-01. ICMS em extinção gradual pela EC 132/2023 (ADCT, arts. 128 e 129).
- **Fonte oficial:**
  - Lei Complementar nº 24/1975: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp24.htm (2026-10-11, sha256 `2e521bd4a17ed0be…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** LC 24/1975: "Dispõe sobre os convênios para a concessão de isenções do ICM". O art. 1º diz que isenções são concedidas ou revogadas por convênios; o art. 2º trata do quórum e da forma de celebração.
- **Análise:** A LC 24 (recepcionada) é a lei complementar da alínea g: forma como, mediante deliberação dos Estados e do DF, isenções, incentivos e benefícios são concedidos e revogados. O target vai para a alínea g, não para o inciso XII inteiro.

### 7. CF art. 156, § 3 × Lei Complementar nº 214/2025: **REJECT** (ALTA)

- **candidate_id:** `CORRC0-A5A1F929253C`
- **Target:** `CF88:ART.156:PAR.3`; target final `None`; rota —.
- **Sinais C0:** S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** PARTIAL_EFFECTS; vigência 2025-01-16 (publicação; efeitos escalonados no art. 544); revalidar em 2027-01-01. LC 214/2025, art. 544: vigência na publicação, com produção de efeitos escalonada; transição do IBS/CBS até 2033.
- **Fonte oficial:**
  - Lei Complementar nº 214/2025: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm (2026-10-11, sha256 `56324955fe0d7644…`)
  - Lei Complementar nº 116/2003 (ISS): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp116.htm (2026-10-11, sha256 `24533ca41a83bc95…`)
- **Dispositivos relevantes:** LC 116/2003: "Dispõe sobre o Imposto Sobre Serviços de Qualquer Natureza". A LC 214 institui IBS, CBS e IS.
- **Análise:** O § 3º reserva à lei complementar alíquotas, exclusões e benefícios do ISS, matéria da LC 116/2003. A LC 214 não disciplina o ISS. A extinção do ISS está no ADCT. A relação é temática.
- **Observações:** NEW_CANDIDATE_BACKLOG: LC 116/2003 × art. 156, § 3º.

### 8. CF art. 156-A, § 1 × Lei Complementar nº 214/2025: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-D2CF3E042053`
- **Target:** `CF88:ART.156-A:PAR.1`; target final `CF88:ART.156-A:PAR.1`; rota art. 1º (Livro I).
- **Sinais C0:** S3_ENTENDA, S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** PARTIAL_EFFECTS; vigência 2025-01-16 (publicação; efeitos escalonados no art. 544); revalidar em 2027-01-01. LC 214/2025, art. 544: vigência na publicação, com produção de efeitos escalonada; transição do IBS/CBS até 2033.
- **Fonte oficial:**
  - Lei Complementar nº 214/2025: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm (2026-10-11, sha256 `56324955fe0d7644…`)
- **Dispositivos relevantes:** LC 214/2025, Livro I: normas do IBS e da CBS (incidência ampla, não cumulatividade, alíquotas de referência, arts. 14 a 19; regime regular e créditos).
- **Análise:** O § 1º fixa os princípios e características do IBS (neutralidade, incidência ampla, não cumulatividade, alíquota única por ente). A LC 214 concretiza esse regime.

### 9. CF art. 156-A, § 5 × Lei Complementar nº 214/2025: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-E3C2F652AB8A`
- **Target:** `CF88:ART.156-A:PAR.5`; target final `CF88:ART.156-A:PAR.5`; rota Livro I (art. 112 e ss. para o inciso VIII).
- **Sinais C0:** S3_ENTENDA, S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** PARTIAL_EFFECTS; vigência 2025-01-16 (publicação; efeitos escalonados no art. 544); revalidar em 2027-01-01. LC 214/2025, art. 544: vigência na publicação, com produção de efeitos escalonada; transição do IBS/CBS até 2033.
- **Fonte oficial:**
  - Lei Complementar nº 214/2025: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm (2026-10-11, sha256 `56324955fe0d7644…`)
  - Lei Complementar nº 227/2026: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp227.htm (2026-10-11, sha256 `39503f69ea3ce721…`)
- **Dispositivos relevantes:** LC 214/2025: regime de compensação e créditos; ressarcimento; destino da operação; bens de capital; regimes aduaneiros e ZPE; devolução personalizada (Título III, arts. 112 e ss.); obrigações acessórias.
- **Análise:** O § 5º lista nove matérias de lei complementar. A LC 214 cobre os incisos II a VI, VIII e IX. Os incisos I (distribuição da arrecadação) e VII (processo administrativo) estão na LC 227/2026.

### 10. CF art. 156-A, § 5 × Lei Complementar nº 227/2026: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-945D4CF3CD87`
- **Target:** `CF88:ART.156-A:PAR.5`; target final `CF88:ART.156-A:PAR.5:INC.VII`; rota art. 54.
- **Sinais C0:** S3_ENTENDA; natureza C0 REGULAMENTA.
- **Temporal:** PARTIAL_EFFECTS; vigência 2026-01-13 (publicação; parte dos dispositivos a partir de 2027-01-01); revalidar em 2027-01-01. LC 227/2026, art. 182.
- **Fonte oficial:**
  - Lei Complementar nº 227/2026: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp227.htm (2026-10-11, sha256 `39503f69ea3ce721…`)
- **Dispositivos relevantes:** LC 227/2026, ementa: "dispõe sobre o processo administrativo tributário do IBS e sobre a distribuição do produto da arrecadação". Título II, "Do Processo Administrativo Tributário do IBS" (art. 54 e ss.).
- **Análise:** O vínculo materialmente sustentado é com o inciso VII do § 5º (processo administrativo fiscal do imposto). A distribuição da arrecadação (inciso I) é vínculo distinto e vai para o backlog. Nada de fan-out para o § 5º inteiro.
- **Observações:** NEW_CANDIDATE_BACKLOG: LC 227/2026 × art. 156-A, § 5º, I.

### 11. CF art. 156-A, § 6 × Lei Complementar nº 214/2025: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-6236AB9C2784`
- **Target:** `CF88:ART.156-A:PAR.6`; target final `CF88:ART.156-A:PAR.6`; rota art. 172 (Título V).
- **Sinais C0:** S3_ENTENDA, S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** PARTIAL_EFFECTS; vigência 2025-01-16 (publicação; efeitos escalonados no art. 544); revalidar em 2027-01-01. LC 214/2025, art. 544: vigência na publicação, com produção de efeitos escalonada; transição do IBS/CBS até 2033.
- **Fonte oficial:**
  - Lei Complementar nº 214/2025: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm (2026-10-11, sha256 `56324955fe0d7644…`)
- **Dispositivos relevantes:** LC 214/2025, Título V, "Dos Regimes Específicos do IBS e da CBS": combustíveis (art. 172, incidência única), serviços financeiros, imóveis, planos de saúde, cooperativas, hotelaria e turismo, transporte coletivo.
- **Análise:** O § 6º manda a lei complementar dispor sobre regimes específicos para os setores que lista, e o Título V da LC 214 é essa disciplina.

### 12. CF art. 156-A, § 9 × Lei Complementar nº 214/2025: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-AE4FC77A0E24`
- **Target:** `CF88:ART.156-A:PAR.9`; target final `CF88:ART.156-A:PAR.9`; rota art. 19.
- **Sinais C0:** S3_ENTENDA, S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** PARTIAL_EFFECTS; vigência 2025-01-16 (publicação; efeitos escalonados no art. 544); revalidar em 2027-01-01. LC 214/2025, art. 544: vigência na publicação, com produção de efeitos escalonada; transição do IBS/CBS até 2033.
- **Fonte oficial:**
  - Lei Complementar nº 214/2025: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm (2026-10-11, sha256 `56324955fe0d7644…`)
- **Dispositivos relevantes:** LC 214/2025, art. 19: "Qualquer alteração na legislação federal que reduza ou eleve a arrecadação do IBS ou da CBS: I - deverá ser compensada pela elevação ou redução, pelo Senado Federal, ... das alíquotas de referência...; II - somente entrará em vigor com o início da produção de efeitos do ajuste...". O art. 18 trata das alíquotas de referência.
- **Análise:** O art. 19 reproduz e disciplina o mecanismo do § 9º. A relação é direta.

### 13. CF art. 156-A, § 13 × Lei Complementar nº 214/2025: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-E80CB2DF38CE`
- **Target:** `CF88:ART.156-A:PAR.13`; target final `CF88:ART.156-A:PAR.13`; rota art. 118.
- **Sinais C0:** S3_ENTENDA, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** PARTIAL_EFFECTS; vigência 2025-01-16 (publicação; efeitos escalonados no art. 544); revalidar em 2027-01-01. LC 214/2025, art. 544: vigência na publicação, com produção de efeitos escalonada; transição do IBS/CBS até 2033.
- **Fonte oficial:**
  - Lei Complementar nº 214/2025: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm (2026-10-11, sha256 `56324955fe0d7644…`)
- **Dispositivos relevantes:** LC 214/2025, Título III, "Da Devolução Personalizada do IBS e da CBS (Cashback)", arts. 112 e ss. O art. 118 fixa os percentuais de devolução, inclusive em energia elétrica e botijão de GLP.
- **Análise:** O § 13 torna obrigatória a devolução na energia elétrica e no GLP para a baixa renda e permite à lei complementar definir o cálculo no momento da cobrança. A LC 214 disciplina isso. A natureza muda de COMPLEMENTA para REGULAMENTA.

### 14. CF art. 159, I × Lei Complementar nº 214/2025: **REJECT** (MEDIA)

- **candidate_id:** `CORRC0-1A40567592C0`
- **Target:** `CF88:ART.159:INC.I`; target final `None`; rota —.
- **Sinais C0:** S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** PARTIAL_EFFECTS; vigência 2025-01-16 (publicação; efeitos escalonados no art. 544); revalidar em 2027-01-01. LC 214/2025, art. 544: vigência na publicação, com produção de efeitos escalonada; transição do IBS/CBS até 2033.
- **Fonte oficial:**
  - Lei Complementar nº 214/2025: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm (2026-10-11, sha256 `56324955fe0d7644…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** LC 214/2025, art. 409: institui o Imposto Seletivo. Os percentuais de repartição do art. 159, I, estão no próprio texto constitucional.
- **Análise:** O inciso I do art. 159 é regra constitucional de repartição. A LC 214 só institui um dos impostos repartidos, sem disciplinar a repartição. O vínculo útil da LC 214 com o IS fica no art. 153, VIII e § 6º.

### 15. CF art. 165, § 9 × Lei Complementar 101/2000 - Lei de Responsabilidade Fiscal: **ADJUST** (MEDIA)

- **candidate_id:** `CORRC0-EFB85C7CCADA`
- **Target:** `CF88:ART.165:PAR.9`; target final `CF88:ART.165:PAR.9`; rota art. 1º.
- **Sinais C0:** S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 101/2000 (LRF): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp101.htm (2026-10-11, sha256 `e353e6697c9e7ada…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** LRF, art. 1º: normas de finanças públicas voltadas para a responsabilidade na gestão fiscal, "com amparo no Capítulo II do Título VI". Disciplina gestão fiscal, limites e transparência.
- **Análise:** O § 9º reserva à lei complementar (I) exercício financeiro e organização das leis orçamentárias, (II) normas de gestão financeira e patrimonial e (III) execução equitativa. A LRF cobre parte do inciso II e não esgota o parágrafo (Lei 4.320/1964 e LC 210/2024 também atuam). A natureza muda de REGULAMENTA para COMPLEMENTA, com escopo parcial.

### 16. CF art. 165, § 10 × Lei nº 14.436/2022: **REJECT** (ALTA)

- **candidate_id:** `CORRC0-3EAE25BCF28E`
- **Target:** `CF88:ART.165:PAR.10`; target final `None`; rota —.
- **Sinais C0:** S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** TRANSITIONAL. lei periódica do exercício de 2023; eficácia exaurida.
- **Fonte oficial:**
  - Lei nº 14.436/2022 (LDO 2023): https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/lei/l14436.htm (2026-10-11, sha256 `4b3f4a68bafe46a4…`)
- **Dispositivos relevantes:** Ementa: "Dispõe sobre as diretrizes para a elaboração e a execução da Lei Orçamentária de 2023".
- **Análise:** Lei de diretrizes de um exercício encerrado, com eficácia exaurida. A nota oficial da ENTENDA se referia ao § 11 (fonte desalinhada), e o dever de executar do § 10 é permanente. Lei periódica não é correlata útil.

### 17. CF art. 165, § 18 × Lei Complementar nº 200/2023: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-68DD94F14824`
- **Target:** `CF88:ART.165:PAR.18`; target final `CF88:ART.165:PAR.18`; rota art. 3º.
- **Sinais C0:** S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 200/2023: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp200.htm (2026-10-11, sha256 `62d132404acbf2a4…`)
- **Dispositivos relevantes:** Ementa: "Institui regime fiscal sustentável ... com fundamento no art. 6º da Emenda Constitucional nº 126". O art. 3º fixa os limites individualizados de despesas primárias.
- **Análise:** O § 18 exclui despesas com precatórios e RPV do "limite individualizado ... estabelecido na lei complementar de que trata o art. 6º da EC 126", que é a LC 200/2023. A relação é de complementação recíproca.

### 18. CF art. 166, § 9 × Lei Complementar nº 210/2024: **ADJUST** (MEDIA)

- **candidate_id:** `CORRC0-56E3853E56E6`
- **Target:** `CF88:ART.166:PAR.9`; target final `CF88:ART.166:PAR.9`; rota art. 6º.
- **Sinais C0:** S3_ENTENDA; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 210/2024: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp210.htm (2026-10-11, sha256 `cda0c0c0035f17d6…`)
- **Dispositivos relevantes:** LC 210/2024, ementa: proposição e execução de emendas parlamentares na LOA. Capítulo IV, "Das Emendas Individuais" (arts. 6º e 7º).
- **Análise:** O § 9º fixa o limite constitucional das emendas individuais (2% da RCL, metade para a saúde). A LC 210 disciplina proposição e execução, sem criar o limite. A natureza muda de REGULAMENTA para COMPLEMENTA.

### 19. CF art. 166, § 11 × Lei Complementar nº 210/2024: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-FEF94155C26B`
- **Target:** `CF88:ART.166:PAR.11`; target final `CF88:ART.166:PAR.11`; rota art. 10.
- **Sinais C0:** S3_ENTENDA; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 210/2024: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp210.htm (2026-10-11, sha256 `cda0c0c0035f17d6…`)
- **Dispositivos relevantes:** LC 210/2024, Capítulo V, art. 10: "São consideradas hipóteses de impedimentos de ordem técnica para execução de emendas parlamentares, exclusivamente...".
- **Análise:** O § 11 torna obrigatória a execução das emendas individuais "conforme os critérios para a execução equitativa da programação definidos na lei complementar". A LC 210 disciplina execução e impedimentos.

### 20. CF art. 166, § 11 × Lei nº 14.436/2022: **REJECT** (ALTA)

- **candidate_id:** `CORRC0-40EDEC92644D`
- **Target:** `CF88:ART.166:PAR.11`; target final `None`; rota —.
- **Sinais C0:** S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** TRANSITIONAL. lei periódica do exercício de 2023; eficácia exaurida.
- **Fonte oficial:**
  - Lei nº 14.436/2022 (LDO 2023): https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/lei/l14436.htm (2026-10-11, sha256 `4b3f4a68bafe46a4…`)
- **Dispositivos relevantes:** Lei 14.436/2022: diretrizes da LOA de 2023.
- **Análise:** Lei periódica de exercício encerrado. Não é a lei complementar permanente que o § 11 exige.

### 21. CF art. 169, § 3 × Lei Complementar 101/2000 - Lei de Responsabilidade Fiscal: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-FE5F5C013375`
- **Target:** `CF88:ART.169:PAR.3`; target final `CF88:ART.169:PAR.3`; rota art. 23.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 101/2000 (LRF): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp101.htm (2026-10-11, sha256 `e353e6697c9e7ada…`)
- **Dispositivos relevantes:** LRF, art. 23: o percentual de despesa com pessoal que exceder o limite "terá de ser eliminado nos dois quadrimestres seguintes ..., adotando-se, entre outras, as providências previstas nos §§ 3º e 4º do art. 169".
- **Análise:** O § 3º manda adotar as providências "durante o prazo fixado na lei complementar referida no caput", e a LRF fixa esse prazo e remete expressamente ao § 3º.

### 22. CF art. 169, § 4 × Lei Complementar 101/2000 - Lei de Responsabilidade Fiscal: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-8A985C226863`
- **Target:** `CF88:ART.169:PAR.4`; target final `CF88:ART.169:PAR.4`; rota art. 23.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 101/2000 (LRF): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp101.htm (2026-10-11, sha256 `e353e6697c9e7ada…`)
  - Lei nº 9.801/1999: https://www.planalto.gov.br/ccivil_03/leis/l9801.htm (2026-10-11, sha256 `de298f9c6dcd6cfa…`)
- **Dispositivos relevantes:** LRF, art. 23 (prazo e remissão aos §§ 3º e 4º). Lei 9.801/1999, art. 1º: "regula a exoneração de servidor público estável com fundamento no § 4º e seguintes do art. 169".
- **Análise:** O § 4º prevê a perda do cargo do estável quando as medidas do § 3º não bastam "para assegurar o cumprimento da determinação da lei complementar referida neste artigo". A LRF dá o parâmetro (limites e prazo), mas as normas gerais da exoneração estão na Lei 9.801 (§ 7º). A natureza muda de REGULAMENTA para COMPLEMENTA.
- **Observações:** NEW_CANDIDATE_BACKLOG: Lei 9.801/1999 × art. 169, §§ 4º e 7º.

### 23. CF art. 170, p.u. × Lei nº 13.874/2019: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-0F1CB8ABDC7C`
- **Target:** `CF88:ART.170:PAR.UNICO`; target final `CF88:ART.170:PAR.UNICO`; rota art. 3º.
- **Sinais C0:** S3_ENTENDA, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 13.874/2019: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/l13874.htm (2026-10-11, sha256 `99cc67a286076f18…`)
- **Dispositivos relevantes:** Lei 13.874/2019, art. 3º: direitos de toda pessoa essenciais ao desenvolvimento econômico, "observado o disposto no parágrafo único do art. 170", inciso I: atividade de baixo risco sem atos públicos de liberação.
- **Análise:** O parágrafo único assegura o livre exercício de atividade econômica sem autorização, "salvo nos casos previstos em lei". A Declaração de Direitos de Liberdade Econômica disciplina exatamente o regime de liberação. A natureza muda para REGULAMENTA.

### 24. CF art. 184, § 3 × Lei Complementar nº 76/1993: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-31BBEFA99046`
- **Target:** `CF88:ART.184:PAR.3`; target final `CF88:ART.184:PAR.3`; rota art. 1º.
- **Sinais C0:** S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 76/1993: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp76.htm (2026-10-11, sha256 `f6b25ddbad94769f…`)
- **Dispositivos relevantes:** Ementa: "Dispõe sobre o procedimento contraditório especial, de rito sumário, para o processo de desapropriação de imóvel rural, por interesse social, para fins de reforma agrária".
- **Análise:** A ementa reproduz o § 3º. A natureza correta é PROCEDIMENTO, não REGULAMENTA genérico.

### 25. CF art. 184, § 3 × Lei Complementar nº 93/1998: **REJECT** (ALTA)

- **candidate_id:** `CORRC0-6BFA71365AA0`
- **Target:** `CF88:ART.184:PAR.3`; target final `None`; rota —.
- **Sinais C0:** S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 93/1998: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp93.htm (2026-10-11, sha256 `591e381ac041cab6…`)
- **Dispositivos relevantes:** Ementa: "Institui o Fundo de Terras e da Reforma Agrária - Banco da Terra".
- **Análise:** O § 3º trata do rito processual da desapropriação. A LC 93 cria um fundo de financiamento fundiário. A relação é temática, vinda da página legada da Câmara.

### 26. CF art. 195, § 1 × Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio: **REJECT** (ALTA)

- **candidate_id:** `CORRC0-E2384C29633B`
- **Target:** `CF88:ART.195:PAR.1`; target final `None`; rota —.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 8.212/1991 (compilada): https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm (2026-10-11, sha256 `12c5bda5cffd920d…`)
- **Dispositivos relevantes:** Lei 8.212/1991, art. 10: "A Seguridade Social será financiada por toda sociedade, ... nos termos do art. 195". Não há regra sobre a inclusão das receitas estaduais e municipais da seguridade nos respectivos orçamentos.
- **Análise:** O § 1º é regra orçamentária federativa. A citação do art. 10 é genérica ao art. 195. A remoção da LC 70 deste target (C1A) não deve ser compensada com vínculo temático.

### 27. CF art. 195, § 3 × Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-410A3EF072CA`
- **Target:** `CF88:ART.195:PAR.3`; target final `CF88:ART.195:PAR.3`; rota art. 47.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 8.212/1991 (compilada): https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm (2026-10-11, sha256 `12c5bda5cffd920d…`)
- **Dispositivos relevantes:** Lei 8.212/1991, Capítulo XI, "Da Prova de Inexistência de Débito", art. 47: exige CND da empresa "na contratação com o Poder Público e no recebimento de benefícios ou incentivo fiscal ou creditício".
- **Análise:** O § 3º veda contratar com o poder público ou receber benefícios à pessoa jurídica em débito "como estabelecido em lei". O art. 47 é essa disciplina. A natureza muda de COMPLEMENTA para REGULAMENTA.

### 28. CF art. 195, § 4 × Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio: **REJECT** (MEDIA)

- **candidate_id:** `CORRC0-123B2C35009A`
- **Target:** `CF88:ART.195:PAR.4`; target final `None`; rota —.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 8.212/1991 (compilada): https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm (2026-10-11, sha256 `12c5bda5cffd920d…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** Lei 8.212/1991: lei ordinária de custeio. A referência legada ao "cap. XI" aponta para a CND (art. 47), não para novas fontes.
- **Análise:** O § 4º autoriza outras fontes de custeio obedecido o art. 154, I (lei complementar, competência residual). A Lei 8.212 não institui fontes residuais. A indicação legada estava desalinhada.

### 29. CF art. 195, § 7 × Lei Complementar nº 187/2021: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-47F967871B91`
- **Target:** `CF88:ART.195:PAR.7`; target final `CF88:ART.195:PAR.7`; rota art. 1º.
- **Sinais C0:** S2_NOTA_EDITORIAL_VIDE, S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 187/2021: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp187.htm (2026-10-11, sha256 `cf47392daa3ed10c…`)
- **Dispositivos relevantes:** Ementa: "Dispõe sobre a certificação das entidades beneficentes e regula os procedimentos referentes à imunidade de contribuições à seguridade social de que trata o § 7º do art. 195".
- **Análise:** Remissão expressa: é a lei complementar das exigências do § 7º. A nota "Vide" da compilação não basta; a ementa oficial basta. A natureza muda de COMPLEMENTA para REGULAMENTA.

### 30. CF art. 195, § 7 × Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio: **REJECT** (ALTA)

- **candidate_id:** `CORRC0-80D1B099C1D9`
- **Target:** `CF88:ART.195:PAR.7`; target final `None`; rota —.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 8.212/1991 (compilada): https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm (2026-10-11, sha256 `12c5bda5cffd920d…`)
  - Lei Complementar nº 187/2021: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp187.htm (2026-10-11, sha256 `cf47392daa3ed10c…`)
- **Dispositivos relevantes:** Lei 8.212/1991, art. 55 (isenção das entidades beneficentes): "(Revogado pela Lei nº 12.101, de 2009)". O regime vigente é o da LC 187/2021.
- **Análise:** A disciplina da Lei 8.212 para o § 7º foi revogada, e a correlata vigente é a LC 187/2021, aprovada neste lote. O vínculo é histórico.
- **Observações:** DISPOSITIVO_REVOGADO.

## NEW_CANDIDATE_BACKLOG (não decidido; fora da contagem dos 106 HIGH originais)

- Lei Complementar nº 116/2003 (ISS) × `CF88:ART.156:PAR.3`, prioridade sugerida MEDIUM, origem `CORRC0-A5A1F929253C`.
  - Fundamento: ementa oficial: dispõe sobre o ISS; o § 3º reserva à LC alíquotas, exclusões e benefícios do ISS.
  - Por que não decidir agora: norma não estava na fila HIGH original; exige rodada própria.
- Lei Complementar nº 227/2026 × `CF88:ART.156-A:PAR.5:INC.I`, prioridade sugerida HIGH, origem `CORRC0-945D4CF3CD87`.
  - Fundamento: ementa oficial: dispõe sobre a distribuição do produto da arrecadação do IBS.
  - Por que não decidir agora: vínculo distinto do inciso VII; sem fan-out no mesmo candidate_id.
- Lei nº 9.801/1999 × `CF88:ART.169:PAR.4`, prioridade sugerida HIGH, origem `CORRC0-8A985C226863`.
  - Fundamento: art. 1º: regula a exoneração do estável "com fundamento no § 4º e seguintes do art. 169".
  - Por que não decidir agora: norma não estava na fila HIGH original.
- Lei nº 9.801/1999 × `CF88:ART.169:PAR.7`, prioridade sugerida HIGH, origem `CORRC0-8A985C226863`.
  - Fundamento: § 7º: "Lei federal disporá sobre as normas gerais" do § 4º; a Lei 9.801 é essa lei.
  - Por que não decidir agora: norma não estava na fila HIGH original.

