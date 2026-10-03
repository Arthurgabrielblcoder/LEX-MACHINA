# ENTENDA CF — Batch 04 · Round 2 (arts. 29, 29-A, 30 e 31): triagem de risco

Triagem para a revisão assistida por risco. **Nenhum texto foi alterado**; as 24 explicações continuam `PENDING_HUMAN_REVIEW`.
O texto completo de cada explicação está em `REVIEW_BATCH_04_ROUND_2_ART29_31.md`.

- **GREEN:** texto estável, diretamente derivado da Constituição, sem dado temporal sensível, percentual, prazo, quantidade ou teto, sem jurisprudência necessária, sem remissão problemática e sem risco conceitual relevante.
- **YELLOW:** exige auditoria jurídica/editorial mais cuidadosa (percentual, prazo, quantidade, teto, remissão, exceção, competência federativa, regra eleitoral, conceito técnico, interpretação além do texto, CAMADA EXTERNA ou jurisprudência recomendada).
- **RED:** dúvida jurídica real, dispositivo ambíguo ou recente, risco de erro relevante, jurisprudência essencial não confirmada ou necessidade de decisão editorial humana.

**Contagem:** GREEN 3 · YELLOW 19 · RED 2 (total 24).

| # | TARGET_ID | TITLE | RISK | EXTERNAL_VERIFICATION_NEEDED | EDITORIAL_DECISION_NEEDED |
|---|---|---|---|---|---|
| 1 | `CF88:ART.29` | Art. 29 — Município e Lei Orgânica | **YELLOW** | NO | NO |
| 2 | `CF88:ART.29:INC.I` | Art. 29, incisos I, II e III — Eleição, mandato e posse no Município | **YELLOW** | NO | NO |
| 3 | `CF88:ART.29:INC.IV` | Art. 29, inciso IV — Número máximo de Vereadores | **YELLOW** | NO | NO |
| 4 | `CF88:ART.29:INC.V` | Art. 29, incisos V, VI e VII — Remuneração dos agentes políticos municipais | **YELLOW** | NO | NO |
| 5 | `CF88:ART.29:INC.VIII` | Art. 29, incisos VIII e IX — Garantias e proibições dos Vereadores | **YELLOW** | NO | NO |
| 6 | `CF88:ART.29:INC.X` | Art. 29, inciso X — Julgamento do Prefeito no Tribunal de Justiça | **YELLOW** | YES | NO |
| 7 | `CF88:ART.29:INC.XII` | Art. 29, incisos XII e XIII — Participação popular no Município | **YELLOW** | NO | NO |
| 8 | `CF88:ART.29:INC.XIV` | Art. 29, inciso XIV — Perda do mandato do Prefeito | **YELLOW** | NO | NO |
| 9 | `CF88:ART.29-A` | Art. 29-A — Limites de despesa da Câmara Municipal | **YELLOW** | NO | NO |
| 10 | `CF88:ART.29-A:INC.I` | Art. 29-A, incisos I, II, III, IV, V e VI — Percentuais por faixa de população | **YELLOW** | NO | NO |
| 11 | `CF88:ART.29-A:PAR.1` | Art. 29-A, § 1º — Limite da folha de pagamento da Câmara | **YELLOW** | NO | NO |
| 12 | `CF88:ART.29-A:PAR.2` | Art. 29-A, §§ 2º e 3º — Crimes de responsabilidade no repasse | **YELLOW** | YES | NO |
| 13 | `CF88:ART.30` | Art. 30 — Competências dos Municípios | **YELLOW** | NO | NO |
| 14 | `CF88:ART.30:INC.I` | Art. 30, inciso I — Interesse local | **YELLOW** | NO | NO |
| 15 | `CF88:ART.30:INC.II` | Art. 30, inciso II — Competência suplementar do Município | **YELLOW** | NO | NO |
| 16 | `CF88:ART.30:INC.III` | Art. 30, inciso III — Tributos municipais e prestação de contas | **YELLOW** | YES | NO |
| 17 | `CF88:ART.30:INC.V` | Art. 30, inciso V — Serviços públicos de interesse local | **YELLOW** | NO | NO |
| 18 | `CF88:ART.30:INC.VI` | Art. 30, incisos VI e VII — Educação básica e saúde com cooperação | **GREEN** | NO | NO |
| 19 | `CF88:ART.30:INC.VIII` | Art. 30, inciso VIII — Ordenamento do solo urbano | **GREEN** | NO | NO |
| 20 | `CF88:ART.30:INC.IX` | Art. 30, inciso IX — Patrimônio histórico-cultural local | **YELLOW** | NO | NO |
| 21 | `CF88:ART.31` | Art. 31 — Fiscalização do Município | **GREEN** | NO | NO |
| 22 | `CF88:ART.31:PAR.1` | Art. 31, §§ 1º e 4º — Órgãos de contas que auxiliam a Câmara | **RED** | YES | YES |
| 23 | `CF88:ART.31:PAR.2` | Art. 31, § 2º — Parecer prévio sobre as contas do Prefeito | **RED** | YES | YES |
| 24 | `CF88:ART.31:PAR.3` | Art. 31, § 3º — Contas à disposição do contribuinte | **YELLOW** | NO | NO |

## RISK_REASONS

### `CF88:ART.29` — YELLOW

- **TITLE:** Art. 29 — Município e Lei Orgânica
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - quórum e prazo (dois turnos, interstício de dez dias, dois terços)
  - inferência além do texto literal: promulgação pela Câmara "sem sanção do Prefeito"

### `CF88:ART.29:INC.I` — YELLOW

- **TITLE:** Art. 29, incisos I, II e III — Eleição, mandato e posse no Município
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - regra eleitoral (eleição simultânea, segundo turno só acima de 200 mil eleitores)
  - quantidade (200 mil eleitores; eleitores x habitantes)
  - CAMADA EXTERNA com nota histórica (EC 107/2020), já decidida

### `CF88:ART.29:INC.IV` — YELLOW

- **TITLE:** Art. 29, inciso IV — Número máximo de Vereadores
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - quantidades (24 faixas populacionais, 9 a 55 Vereadores)
  - exemplo numérico (40 mil habitantes → até 13)
  - afirmação de que a composição considera a população apurada oficialmente (fora do texto do inciso)

### `CF88:ART.29:INC.V` — YELLOW

- **TITLE:** Art. 29, incisos V, VI e VII — Remuneração dos agentes políticos municipais
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - percentuais e tetos (20% a 75% do subsídio estadual; 5% da receita)
  - regra temporal (fixação de uma legislatura para a seguinte)
  - remissão ao teto do art. 37, XI e interação com o art. 29-A

### `CF88:ART.29:INC.VIII` — YELLOW

- **TITLE:** Art. 29, incisos VIII e IX — Garantias e proibições dos Vereadores
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - conceito técnico (inviolabilidade, circunscrição)
  - exceção: o Vereador não tem as demais imunidades parlamentares
  - CAMADA EXTERNA (alcance da inviolabilidade: nexo com o mandato e limite territorial)

### `CF88:ART.29:INC.X` — YELLOW

- **TITLE:** Art. 29, inciso X — Julgamento do Prefeito no Tribunal de Justiça
- **EXTERNAL_VERIFICATION_NEEDED:** YES · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - competência (foro por prerrogativa de função)
  - interpretação além do texto: "em regra, está ligado ao exercício da função"
  - jurisprudência recomendada pendente de ingestão (alcance do foro do Prefeito; candidato: Súmula 702, a confirmar)

### `CF88:ART.29:INC.XII` — YELLOW

- **TITLE:** Art. 29, incisos XII e XIII — Participação popular no Município
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - percentual (5% do eleitorado)
  - conceito técnico (iniciativa popular)

### `CF88:ART.29:INC.XIV` — YELLOW

- **TITLE:** Art. 29, inciso XIV — Perda do mandato do Prefeito
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - remissão constitucional desatualizada (art. 28, parágrafo único → § 1º), já decidida na sanitização
  - CAMADA EXTERNA

### `CF88:ART.29-A` — YELLOW

- **TITLE:** Art. 29-A — Limites de despesa da Câmara Municipal
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - base de cálculo complexa (receita tributária + transferências dos arts. 153, § 5º, 158 e 159, realizada no exercício anterior)
  - conceito técnico (repasse/duodécimo)
  - inclui inativos e pensionistas no total da despesa

### `CF88:ART.29-A:INC.I` — YELLOW

- **TITLE:** Art. 29-A, incisos I, II, III, IV, V e VI — Percentuais por faixa de população
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - percentuais por faixa (7% a 3,5%)
  - faixas do texto oficial com fronteira sobreposta em 100 mil habitantes (incisos I e II)
  - exemplo numérico hipotético

### `CF88:ART.29-A:PAR.1` — YELLOW

- **TITLE:** Art. 29-A, § 1º — Limite da folha de pagamento da Câmara
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - percentual (70% com folha)
  - interpretação de "receita da Câmara" como o valor recebido para funcionar
  - exemplo numérico hipotético

### `CF88:ART.29-A:PAR.2` — YELLOW

- **TITLE:** Art. 29-A, §§ 2º e 3º — Crimes de responsabilidade no repasse
- **EXTERNAL_VERIFICATION_NEEDED:** YES · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - prazo (repasse até o dia 20)
  - conceito técnico (crime de responsabilidade) e competência legislativa federal
  - jurisprudência recomendada pendente de ingestão (candidato: Súmula Vinculante 46, a confirmar)

### `CF88:ART.30` — YELLOW

- **TITLE:** Art. 30 — Competências dos Municípios
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - competência federativa (legislativa x administrativa/material; competência comum do art. 23)
  - definição de interesse local por predominância (interpretação além do texto)

### `CF88:ART.30:INC.I` — YELLOW

- **TITLE:** Art. 30, inciso I — Interesse local
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - competência federativa e conceito indeterminado (interesse local)
  - critério da predominância é construção interpretativa
  - jurisprudência recomendada READY_TO_LINK (Tema 145) e CAMADA EXTERNA

### `CF88:ART.30:INC.II` — YELLOW

- **TITLE:** Art. 30, inciso II — Competência suplementar do Município
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - competência federativa (suplementar x concorrente)
  - interpretação além do texto sobre a atuação municipal nos temas do art. 24

### `CF88:ART.30:INC.III` — YELLOW

- **TITLE:** Art. 30, inciso III — Tributos municipais e prestação de contas
- **EXTERNAL_VERIFICATION_NEEDED:** YES · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - sistema tributário com vigência em transição (reforma tributária; regras de transição dos tributos municipais)
  - CAMADA EXTERNA sobre a reforma; o corpo cita apenas o IPTU e os arts. 145 e 156

### `CF88:ART.30:INC.V` — YELLOW

- **TITLE:** Art. 30, inciso V — Serviços públicos de interesse local
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - conceitos técnicos (concessão, permissão, titularidade)
  - caracterização da permissão como "em regra mais simples e precária"

### `CF88:ART.30:INC.VI` — GREEN

- **TITLE:** Art. 30, incisos VI e VII — Educação básica e saúde com cooperação
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - texto estável e diretamente derivado da Constituição (educação infantil, ensino fundamental, saúde, cooperação)

### `CF88:ART.30:INC.VIII` — GREEN

- **TITLE:** Art. 30, inciso VIII — Ordenamento do solo urbano
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - texto estável e diretamente derivado da Constituição (uso, parcelamento e ocupação do solo; remissão simples ao art. 182)

### `CF88:ART.30:INC.IX` — YELLOW

- **TITLE:** Art. 30, inciso IX — Patrimônio histórico-cultural local
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - conceito técnico (tombamento)
  - exemplo descreve efeitos do tombamento que dependem da legislação aplicável

### `CF88:ART.31` — GREEN

- **TITLE:** Art. 31 — Fiscalização do Município
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - texto estável e diretamente derivado da Constituição (controle externo pela Câmara e controle interno do Executivo)

### `CF88:ART.31:PAR.1` — RED

- **TITLE:** Art. 31, §§ 1º e 4º — Órgãos de contas que auxiliam a Câmara
- **EXTERNAL_VERIFICATION_NEEDED:** YES · **EDITORIAL_DECISION_NEEDED:** YES
- **RISK_REASONS:**
  - redação nova (EC 139/2026) com alcance ainda sem leitura consolidada: vedação de extinção, criação ou instalação
  - relação entre a cláusula final do § 1º e a vedação do § 4º; situação dos órgãos de contas municipais existentes
  - risco de erro relevante ao descrever quais órgãos são alcançados

### `CF88:ART.31:PAR.2` — RED

- **TITLE:** Art. 31, § 2º — Parecer prévio sobre as contas do Prefeito
- **EXTERNAL_VERIFICATION_NEEDED:** YES · **EDITORIAL_DECISION_NEEDED:** YES
- **RISK_REASONS:**
  - jurisprudência essencial não confirmada localmente (natureza do parecer prévio; julgamento das contas do Prefeito pela Câmara; contas de governo x contas de gestão; candidatos Temas 157 e 835, a confirmar)
  - quórum de dois terços dos membros
  - decisão editorial: quanto dessa distinção entra no corpo e quanto fica na CAMADA EXTERNA

### `CF88:ART.31:PAR.3` — YELLOW

- **TITLE:** Art. 31, § 3º — Contas à disposição do contribuinte
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - prazo (sessenta dias por ano)
  - vínculo local falso (Tema 756) já excluído pelo overlay CF88_LINK_EXCLUSIONS

## Sugestão de fluxo

1. GREEN (3): aprovação em bloco após leitura rápida.
2. YELLOW (19): auditoria editorial focada nas razões listadas; verificação externa onde indicado (art. 29, X; art. 29-A, § 2º; art. 30, III).
3. RED (2): decisão humana antes de aprovar (art. 31, §§ 1º/4º e § 2º), com fonte oficial para EC 139/2026 e para a jurisprudência do parecer prévio.
