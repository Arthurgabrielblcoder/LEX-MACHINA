# CF88_CORRELATA_C1B — HIGH Batch04

**Revisão jurídica assistida. Nada foi aplicado.** Não houve ADDITIONS, exclusões, RUN4, nem alteração no SD ou no firmware.

## Lote

- **Seleção:** fila HIGH original da C0 (106) menos os já decididos; 17 elegíveis antes do lote, em ordem estrutural do Target Index.
- **Tamanho:** entraram 17. HIGH originais restantes depois: **0**.
- **Fontes:** só oficiais (Planalto), verificadas em 2026-10-11, com sha256 de cada página.
- **Campos obrigatórios:** cada candidato tem `temporal_status`. Decisão jurídica e rota de aparelho ficam separadas.

## Contabilidade

| Decisão | n |
|---|---:|
| APPROVE | 7 |
| ADJUST | 7 |
| REJECT | 0 |
| HOLD | 3 |
| NEEDS_SOURCE | 0 |
| **Total** | **17** |

| Aceitos (APPROVE + ADJUST): rota de aparelho | n |
|---|---:|
| MAIN_CORPUS_ROUTE_REQUIRED | 5 |
| INGESTION_REQUIRED | 6 |
| DEVICE_RESOLVABLE_NOW | 3 |
| TEMPORAL_DEVICE_BLOCK | 0 |

- **Situação temporal dos aceitos:** {'IN_FORCE': 13, 'TRANSITIONAL': 1}.
- **Overlay:** aceitos em target com status do motor fora de CURRENT/STRUCTURAL (ADCT): 2.
- **Ajustes:** natureza reclassificada em 5; target ajustado em 2.
- **CF × ADCT:** {'CF88': {'ADJUST': 6, 'APPROVE': 6, 'HOLD': 3}, 'ADCT': {'ADJUST': 1, 'APPROVE': 1}}.

## Decisões

| # | Target | Norma | Decisão | Natureza | Target final | Temporal | Escopo | Aparelho |
|---:|---|---|---|---|---|---|---|---|
| 1 | CF art. 195, § 8 | Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio | **ADJUST** | REGULAMENTA | = | IN_FORCE | — | MAIN_CORPUS_ROUTE_REQUIRED |
| 2 | CF art. 198, § 3 | Lei Complementar nº 141/2012 | **APPROVE** | REGULAMENTA | = | IN_FORCE | — | INGESTION_REQUIRED |
| 3 | CF art. 201, § 1 | Lei Complementar nº 142/2013 | **ADJUST** | REGULAMENTA | CF88:ART.201:PAR.1:INC.I | IN_FORCE | — | INGESTION_REQUIRED |
| 4 | CF art. 201, § 4 | Lei 8.213/1991 - Planos de Benefícios da Previdência Social | **ADJUST** | REGULAMENTA | = | IN_FORCE | — | MAIN_CORPUS_ROUTE_REQUIRED |
| 5 | CF art. 202, § 1 | Lei Complementar nº 109/2001 | **ADJUST** | REGULAMENTA | = | IN_FORCE | — | DEVICE_RESOLVABLE_NOW |
| 6 | CF art. 227, § 3 | Lei 8.069/1990 - Estatuto da Criança e do Adolescente | **APPROVE** | REGULAMENTA | = | IN_FORCE | NON_EXCLUSIVE | MAIN_CORPUS_ROUTE_REQUIRED |
| 7 | CF art. 227, § 4 | Lei 8.069/1990 - Estatuto da Criança e do Adolescente | **APPROVE** | COMPLEMENTA | = | IN_FORCE | NON_EXCLUSIVE, ESCOPO_PARCIAL | MAIN_CORPUS_ROUTE_REQUIRED |
| 8 | CF art. 227, § 5 | Lei 8.069/1990 - Estatuto da Criança e do Adolescente | **ADJUST** | REGULAMENTA | = | IN_FORCE | NON_EXCLUSIVE | MAIN_CORPUS_ROUTE_REQUIRED |
| 9 | CF art. 231, § 1 | Lei nº 14.701/2023 | **HOLD** | — | — | UNCERTAIN | — | — |
| 10 | CF art. 231, § 3 | Lei nº 14.701/2023 | **HOLD** | — | — | UNCERTAIN | — | — |
| 11 | CF art. 231, § 6 | Lei nº 14.701/2023 | **HOLD** | — | — | UNCERTAIN | — | — |
| 12 | CF art. 239 | Lei Complementar nº 7/1970 | **APPROVE** | COMPLEMENTA | = | IN_FORCE | — | INGESTION_REQUIRED |
| 13 | CF art. 239 | Lei Complementar nº 8/1970 | **APPROVE** | COMPLEMENTA | = | IN_FORCE | — | INGESTION_REQUIRED |
| 14 | CF art. 239, § 3 | Lei nº 7.998/1990 | **APPROVE** | REGULAMENTA | = | IN_FORCE | — | DEVICE_RESOLVABLE_NOW |
| 15 | CF art. 239, § 4 | Lei nº 7.998/1990 | **ADJUST** | COMPLEMENTA | = | IN_FORCE | ESCOPO_PARCIAL | DEVICE_RESOLVABLE_NOW |
| 16 | ADCT art. 10, II | Lei Complementar nº 146/2014 | **ADJUST** | COMPLEMENTA | ADCT:ART.10:INC.II:AL.b | IN_FORCE | TRANSITORIA | INGESTION_REQUIRED |
| 17 | ADCT art. 128, § 2 | Lei Complementar nº 160/2017 | **APPROVE** | COMPLEMENTA | = | TRANSITIONAL | TRANSITORIA | INGESTION_REQUIRED |

### 1. CF art. 195, § 8 × Lei 8.212/1991 - Organização da Seguridade Social e Plano de Custeio: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-A88AB3189E73`
- **Target:** `CF88:ART.195:PAR.8`; target final `CF88:ART.195:PAR.8`; rota art. 25.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 8.212/1991 (compilada): https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm (2026-10-11, sha256 `12c5bda5cffd920d…`)
- **Dispositivos relevantes:** Lei 8.212/1991, Capítulo VI, art. 25: contribuição do segurado especial e do produtor rural pessoa física sobre a receita bruta da comercialização da produção.
- **Análise:** O § 8º prevê a contribuição do produtor em economia familiar sobre o resultado da comercialização. O art. 25 é essa disciplina; a referência legada ao "art. 55" estava errada. A natureza muda de COMPLEMENTA para REGULAMENTA.

### 2. CF art. 198, § 3 × Lei Complementar nº 141/2012: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-C4B7D896EEC4`
- **Target:** `CF88:ART.198:PAR.3`; target final `CF88:ART.198:PAR.3`; rota art. 1º.
- **Sinais C0:** S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 141/2012: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp141.htm (2026-10-11, sha256 `bef7e768506e0e9c…`)
- **Dispositivos relevantes:** Ementa: "Regulamenta o § 3º do art. 198 da Constituição Federal para dispor sobre os valores mínimos a serem aplicados anualmente ... em ações e serviços públicos de saúde; estabelece os critérios de rateio...".
- **Análise:** O § 3º exige lei complementar sobre os percentuais mínimos em saúde, os critérios de rateio e as normas de fiscalização. A LC 141 é essa lei, com remissão expressa.
- **Observações:** O § 3º exige reavaliação pelo menos a cada cinco anos; registrado para revalidação editorial futura.

### 3. CF art. 201, § 1 × Lei Complementar nº 142/2013: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-2053DEF59022`
- **Target:** `CF88:ART.201:PAR.1`; target final `CF88:ART.201:PAR.1:INC.I`; rota art. 1º.
- **Sinais C0:** S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 142/2013: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp142.htm (2026-10-11, sha256 `bf2272518f8b70e4…`)
- **Dispositivos relevantes:** Ementa: "Regulamenta o § 1º do art. 201 ..., no tocante à aposentadoria da pessoa com deficiência segurada do RGPS".
- **Análise:** Após a EC 103/2019, o § 1º tem dois incisos: (I) segurados com deficiência e (II) exposição a agentes nocivos. A LC 142 disciplina só a hipótese da pessoa com deficiência. O target vai para o inciso I, sem fan-out ao parágrafo inteiro.

### 4. CF art. 201, § 4 × Lei 8.213/1991 - Planos de Benefícios da Previdência Social: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-67B5D9C94E07`
- **Target:** `CF88:ART.201:PAR.4`; target final `CF88:ART.201:PAR.4`; rota art. 41-A.
- **Sinais C0:** S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 8.213/1991 (compilada): https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm (2026-10-11, sha256 `d9b8d1fe23dfe9cb…`)
- **Dispositivos relevantes:** Lei 8.213/1991, art. 41-A: "O valor dos benefícios em manutenção será reajustado, anualmente, na mesma data do reajuste do salário mínimo ... com base no INPC".
- **Análise:** O § 4º assegura o reajustamento para preservar o valor real "conforme critérios definidos em lei". O art. 41-A define esses critérios. A natureza muda de COMPLEMENTA para REGULAMENTA.

### 5. CF art. 202, § 1 × Lei Complementar nº 109/2001: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-362157C332DE`
- **Target:** `CF88:ART.202:PAR.1`; target final `CF88:ART.202:PAR.1`; rota art. 3º.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 109/2001: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp109.htm (2026-10-11, sha256 `98477f7eb4c80338…`)
- **Dispositivos relevantes:** LC 109/2001, art. 3º, IV: a ação do Estado visa "assegurar aos participantes e assistidos o pleno acesso às informações relativas à gestão de seus respectivos planos de benefícios".
- **Análise:** O § 1º manda a lei complementar assegurar o pleno acesso às informações da gestão, e o art. 3º, IV, da LC 109 reproduz e concretiza o comando. A natureza muda de COMPLEMENTA para REGULAMENTA.

### 6. CF art. 227, § 3 × Lei 8.069/1990 - Estatuto da Criança e do Adolescente: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-C8087244A9DB`
- **Target:** `CF88:ART.227:PAR.3`; target final `CF88:ART.227:PAR.3`; rota art. 60.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 8.069/1990 (ECA): https://www.planalto.gov.br/ccivil_03/leis/l8069.htm (2026-10-11, sha256 `6c98180184cea391…`)
- **Dispositivos relevantes:** ECA: Capítulo V, "Do Direito à Profissionalização e à Proteção no Trabalho" (art. 60: proibição de trabalho a menores de 14 anos, salvo aprendiz); garantias processuais (arts. 110 e 111); excepcionalidade da internação (art. 121).
- **Análise:** O § 3º enumera os aspectos da proteção especial (idade mínima, direitos trabalhistas, garantias processuais, brevidade da privação de liberdade). O ECA disciplina esses aspectos.

### 7. CF art. 227, § 4 × Lei 8.069/1990 - Estatuto da Criança e do Adolescente: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-8D80396BDEEB`
- **Target:** `CF88:ART.227:PAR.4`; target final `CF88:ART.227:PAR.4`; rota art. 240.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 8.069/1990 (ECA): https://www.planalto.gov.br/ccivil_03/leis/l8069.htm (2026-10-11, sha256 `6c98180184cea391…`)
- **Dispositivos relevantes:** ECA, crimes: art. 240 (cena de sexo explícito ou pornográfica com criança ou adolescente) e art. 244-A (submissão à prostituição ou exploração sexual).
- **Análise:** O § 4º manda a lei punir severamente o abuso, a violência e a exploração sexual. O ECA tipifica parte dessas condutas; o Código Penal tipifica outras.

### 8. CF art. 227, § 5 × Lei 8.069/1990 - Estatuto da Criança e do Adolescente: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-A2C12E99BECD`
- **Target:** `CF88:ART.227:PAR.5`; target final `CF88:ART.227:PAR.5`; rota art. 39.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 8.069/1990 (ECA): https://www.planalto.gov.br/ccivil_03/leis/l8069.htm (2026-10-11, sha256 `6c98180184cea391…`)
- **Dispositivos relevantes:** ECA, Subseção IV "Da Adoção": art. 39 ("A adoção de criança e de adolescente reger-se-á segundo o disposto nesta Lei") e adoção internacional (arts. 51 a 52-D).
- **Análise:** O § 5º manda a lei estabelecer casos e condições da adoção, inclusive por estrangeiros. O ECA é essa lei. A natureza muda de COMPLEMENTA para REGULAMENTA.

### 9. CF art. 231, § 1 × Lei nº 14.701/2023: **HOLD** (BAIXA)

- **candidate_id:** `CORRC0-E86B55D28D44`
- **Target:** `CF88:ART.231:PAR.1`; target final `None`; rota —.
- **Sinais C0:** S2_NOTA_EDITORIAL_VIDE, S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** UNCERTAIN; vigência 2023-10-20 (publicação). a página oficial do Planalto anota "(Vide ADC 87) (Vide ADI 7582) (Vide ADI 7583) (Vide ADI 7586)" no art. 4º: lei sob controle concentrado no STF; situação atual de eficácia não verificada nesta rodada.
- **Fonte oficial:**
  - Lei nº 14.701/2023: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14701.htm (2026-10-11, sha256 `d51bcfe35e5dbf03…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** Lei 14.701/2023, art. 4º (conceito de terras tradicionalmente ocupadas).
- **Análise:** A Lei 14.701/2023 se declara regulamentadora do art. 231 (ementa). A página oficial, porém, anota no art. 4º, que define as terras tradicionalmente ocupadas pelo critério da data da promulgação, a remissão a ADC 87 e ADIs 7582, 7583 e 7586. O núcleo da lei está sob controle concentrado no STF, e a situação atual de eficácia não foi verificada em fonte oficial nesta rodada. Aprovar pode exibir como correlata vigente disciplina cuja validade está em disputa; rejeitar ignora uma regulamentação expressa.
- **Observações:** Confirmar em fonte oficial (STF/Planalto) a situação atual de ADC 87 e ADIs 7582, 7583 e 7586 antes de decidir.

### 10. CF art. 231, § 3 × Lei nº 14.701/2023: **HOLD** (BAIXA)

- **candidate_id:** `CORRC0-E0C9C2F5CDBD`
- **Target:** `CF88:ART.231:PAR.3`; target final `None`; rota —.
- **Sinais C0:** S2_NOTA_EDITORIAL_VIDE, S3_ENTENDA, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** UNCERTAIN; vigência 2023-10-20 (publicação). a página oficial do Planalto anota "(Vide ADC 87) (Vide ADI 7582) (Vide ADI 7583) (Vide ADI 7586)" no art. 4º: lei sob controle concentrado no STF; situação atual de eficácia não verificada nesta rodada.
- **Fonte oficial:**
  - Lei nº 14.701/2023: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14701.htm (2026-10-11, sha256 `d51bcfe35e5dbf03…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** Lei 14.701/2023 (regulamenta o art. 231; aproveitamento de recursos em terras indígenas).
- **Análise:** A Lei 14.701/2023 se declara regulamentadora do art. 231 (ementa). A página oficial, porém, anota no art. 4º, que define as terras tradicionalmente ocupadas pelo critério da data da promulgação, a remissão a ADC 87 e ADIs 7582, 7583 e 7586. O núcleo da lei está sob controle concentrado no STF, e a situação atual de eficácia não foi verificada em fonte oficial nesta rodada. Aprovar pode exibir como correlata vigente disciplina cuja validade está em disputa; rejeitar ignora uma regulamentação expressa.
- **Observações:** Além do status no STF, identificar o artigo da lei que disciplina a participação nos resultados da lavra (§ 3º, "na forma da lei").

### 11. CF art. 231, § 6 × Lei nº 14.701/2023: **HOLD** (BAIXA)

- **candidate_id:** `CORRC0-FC57ED913387`
- **Target:** `CF88:ART.231:PAR.6`; target final `None`; rota —.
- **Sinais C0:** S2_NOTA_EDITORIAL_VIDE, S3_ENTENDA, S5_RELATIONS_V2_LEGADO; natureza C0 COMPLEMENTA.
- **Temporal:** UNCERTAIN; vigência 2023-10-20 (publicação). a página oficial do Planalto anota "(Vide ADC 87) (Vide ADI 7582) (Vide ADI 7583) (Vide ADI 7586)" no art. 4º: lei sob controle concentrado no STF; situação atual de eficácia não verificada nesta rodada.
- **Fonte oficial:**
  - Lei nº 14.701/2023: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14701.htm (2026-10-11, sha256 `d51bcfe35e5dbf03…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** Lei 14.701/2023 (regulamenta o art. 231).
- **Análise:** A Lei 14.701/2023 se declara regulamentadora do art. 231 (ementa). A página oficial, porém, anota no art. 4º, que define as terras tradicionalmente ocupadas pelo critério da data da promulgação, a remissão a ADC 87 e ADIs 7582, 7583 e 7586. O núcleo da lei está sob controle concentrado no STF, e a situação atual de eficácia não foi verificada em fonte oficial nesta rodada. Aprovar pode exibir como correlata vigente disciplina cuja validade está em disputa; rejeitar ignora uma regulamentação expressa. O § 6º exige, além disso, lei complementar para o relevante interesse público da União, e a Lei 14.701 é ordinária.
- **Observações:** Espécie normativa (LO × LC exigida pelo § 6º) a verificar.

### 12. CF art. 239 × Lei Complementar nº 7/1970: **APPROVE** (MEDIA)

- **candidate_id:** `CORRC0-7F28FCF12C37`
- **Target:** `CF88:ART.239`; target final `CF88:ART.239`; rota art. 1º.
- **Sinais C0:** S2_REMISSAO_NOMINAL; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 7/1970 (PIS): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp07.htm (2026-10-11, sha256 `ea1bc507aa5b234d…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** LC 7/1970, ementa: "Institui o Programa de Integração Social". Parte dos dispositivos aparece "(Revogado pela Lei Complementar nº 26, de 1975)".
- **Análise:** O caput do art. 239 cita nominalmente a LC 7/1970 como lei criadora do PIS, cuja arrecadação a Constituição redireciona. É remissão expressa ao diploma de origem; a destinação atual está na Lei 7.998/1990.
- **Observações:** Norma parcialmente revogada (LC 26/1975); vínculo útil como origem do PIS citada pelo texto.

### 13. CF art. 239 × Lei Complementar nº 8/1970: **APPROVE** (MEDIA)

- **candidate_id:** `CORRC0-D2D0CD6A150D`
- **Target:** `CF88:ART.239`; target final `CF88:ART.239`; rota art. 1º.
- **Sinais C0:** S2_REMISSAO_NOMINAL; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 8/1970 (PASEP): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp08.htm (2026-10-11, sha256 `87eed61b818add9c…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** LC 8/1970, ementa: "Institui o Programa de Formação do Patrimônio do Servidor Público". Parte dos dispositivos foi revogada pela LC 26/1975.
- **Análise:** Remissão expressa do caput do art. 239 à lei criadora do PASEP, com o mesmo raciocínio da LC 7/1970.
- **Observações:** Norma parcialmente revogada (LC 26/1975).

### 14. CF art. 239, § 3 × Lei nº 7.998/1990: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-5C8AFC368627`
- **Target:** `CF88:ART.239:PAR.3`; target final `CF88:ART.239:PAR.3`; rota art. 9º.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 7.998/1990: https://www.planalto.gov.br/ccivil_03/leis/l7998.htm (2026-10-11, sha256 `674335b5ec1bf3ed…`)
- **Dispositivos relevantes:** Lei 7.998/1990, art. 1º: regula o seguro-desemprego e "o abono de que tratam ... o art. 239". Art. 9º: "É assegurado o recebimento de abono salarial anual...".
- **Análise:** O § 3º assegura o abono anual aos empregados que ganham até o limite constitucional. O art. 9º da Lei 7.998 disciplina o abono.

### 15. CF art. 239, § 4 × Lei nº 7.998/1990: **ADJUST** (MEDIA)

- **candidate_id:** `CORRC0-7867B93D94DA`
- **Target:** `CF88:ART.239:PAR.4`; target final `CF88:ART.239:PAR.4`; rota art. 11.
- **Sinais C0:** S4_ACERVO_REVERSO, S5_RELATIONS_V2_LEGADO; natureza C0 REGULAMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei nº 7.998/1990: https://www.planalto.gov.br/ccivil_03/leis/l7998.htm (2026-10-11, sha256 `674335b5ec1bf3ed…`)
- **Dispositivos relevantes:** Lei 7.998/1990, art. 11, IV: entre os recursos do FAT, "o produto da arrecadação da contribuição adicional pelo índice de rotatividade, de que trata o § 4º do art. 239".
- **Análise:** A lei destina ao FAT a contribuição adicional do § 4º, mas não verifiquei nela a disciplina de cálculo e cobrança. A relação é direta e parcial (destinação). A natureza muda de REGULAMENTA para COMPLEMENTA.

### 16. ADCT art. 10, II × Lei Complementar nº 146/2014: **ADJUST** (ALTA)

- **candidate_id:** `CORRC0-F2C3596A37CB`
- **Target:** `ADCT:ART.10:INC.II`; target final `ADCT:ART.10:INC.II:AL.b`; rota art. 1º.
- **Sinais C0:** S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** IN_FORCE.
- **Fonte oficial:**
  - Lei Complementar nº 146/2014: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp146.htm (2026-10-11, sha256 `22dca8f0bef78dc8…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** Ementa: "Estende a estabilidade provisória prevista na alínea b do inciso II do art. 10 do ADCT à trabalhadora gestante, nos casos de morte desta, a quem detiver a guarda de seu filho".
- **Análise:** A remissão expressa é à alínea b. A LC 146 complementa a garantia, estendendo-a ao guardião. O target vai do inciso II para a alínea b.
- **Observações:** Target do ADCT: o status do motor (UNKNOWN_VALIDITY) bloqueia o overlay atual (dívida da C0).

### 17. ADCT art. 128, § 2 × Lei Complementar nº 160/2017: **APPROVE** (ALTA)

- **candidate_id:** `CORRC0-A28C8B1C8F51`
- **Target:** `ADCT:ART.128:PAR.2`; target final `ADCT:ART.128:PAR.2`; rota art. 3º.
- **Sinais C0:** S2_REMISSAO_NOMINAL, S3_ENTENDA; natureza C0 COMPLEMENTA.
- **Temporal:** TRANSITIONAL; revalidar em 2033-01-01. benefícios do ICMS reduzidos de 2029 a 2032 pelo ADCT, art. 128; extinção do ICMS em 2033.
- **Fonte oficial:**
  - Lei Complementar nº 160/2017: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp160.htm (2026-10-11, sha256 `56dca4c1d6f4d5e1…`)
  - Constituição Federal (compilada): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** LC 160/2017, ementa: convênio para remissão de créditos e reinstituição de benefícios fiscais do ICMS concedidos em desacordo com a alínea g do inciso XII do § 2º do art. 155. O art. 3º trata dos benefícios reinstituídos e prazos.
- **Análise:** O § 2º do art. 128 do ADCT manda reduzir os benefícios do art. 3º da LC 160, sem aplicar o § 2º-A desse artigo. A relação é expressa e operativa na transição.
- **Observações:** Target do ADCT: o status do motor bloqueia o overlay atual.

## NEW_CANDIDATE_BACKLOG (não decidido; fora da contagem dos 106 HIGH originais)

- Lei nº 8.213/1991 (arts. 57 e 58, aposentadoria especial) × `CF88:ART.201:PAR.1:INC.II`, prioridade sugerida MEDIUM, origem `CORRC0-2053DEF59022`.
  - Fundamento: o inciso II (exposição a agentes nocivos) é hipótese distinta da LC 142, que cobre só o inciso I.
  - Por que não decidir agora: vínculo distinto, sem herança do inciso I; exige verificação própria após a EC 103/2019.
- Decreto-Lei nº 2.848/1940 (Código Penal, crimes contra a dignidade sexual) × `CF88:ART.227:PAR.4`, prioridade sugerida LOW, origem `CORRC0-8D80396BDEEB`.
  - Fundamento: o § 4º é concretizado também pelo Código Penal (NON_EXCLUSIVE com o ECA).
  - Por que não decidir agora: fora da fila HIGH original.

