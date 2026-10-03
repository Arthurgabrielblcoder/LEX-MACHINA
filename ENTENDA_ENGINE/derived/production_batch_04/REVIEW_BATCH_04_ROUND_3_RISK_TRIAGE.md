# ENTENDA CF — Batch 04 · Round 3 (arts. 32 a 36): triagem de risco

Triagem para a revisão assistida por risco. **Nenhum texto foi alterado**; as 20 explicações continuam `PENDING_HUMAN_REVIEW`.
O texto completo de cada explicação está em `REVIEW_BATCH_04_ROUND_3_ART32_36.md`. Mesmos critérios do Round 2:

- **GREEN:** texto estável, diretamente derivado da Constituição, sem dado temporal sensível, percentual, prazo, quantidade ou teto, sem jurisprudência necessária, sem remissão problemática e sem risco conceitual relevante.
- **YELLOW:** exige auditoria jurídica/editorial mais cuidadosa (percentual, prazo, quantidade, teto, remissão, exceção, competência federativa, regra eleitoral, conceito técnico, interpretação além do texto, CAMADA EXTERNA ou jurisprudência recomendada).
- **RED:** dúvida jurídica real, dispositivo ambíguo, risco de erro relevante, jurisprudência essencial não confirmada, problema de vigência ou necessidade de decisão editorial humana.

**Contagem:** GREEN 1 · YELLOW 17 · RED 2 (total 20).

**Dispositivos históricos/revogados do intervalo:** CF88:ART.36:INC.IV (REVOKED: excluído; sem explicação vigente). O art. 28, parágrafo único (HISTORICAL), pertence ao Round 1.

| # | TARGET_ID | TITLE | RISK | EXTERNAL_VERIFICATION_NEEDED | EDITORIAL_DECISION_NEEDED |
|---|---|---|---|---|---|
| 1 | `CF88:ART.32` | Art. 32 — Distrito Federal | **YELLOW** | NO | NO |
| 2 | `CF88:ART.32:PAR.1` | Art. 32, § 1º — Competências legislativas do Distrito Federal | **YELLOW** | NO | NO |
| 3 | `CF88:ART.32:PAR.2` | Art. 32, §§ 2º e 3º — Eleições e Legislativo do Distrito Federal | **YELLOW** | NO | NO |
| 4 | `CF88:ART.32:PAR.4` | Art. 32, § 4º — Forças de segurança do Distrito Federal | **YELLOW** | NO | NO |
| 5 | `CF88:ART.33` | Art. 33 — Territórios Federais | **RED** | NO | YES |
| 6 | `CF88:ART.33:PAR.3` | Art. 33, § 3º — Territórios com mais de cem mil habitantes | **YELLOW** | NO | NO |
| 7 | `CF88:ART.34` | Art. 34 — Intervenção federal: regra e exceção | **YELLOW** | NO | NO |
| 8 | `CF88:ART.34:INC.I` | Art. 34, incisos I, II e III — Unidade nacional e ordem pública | **YELLOW** | NO | NO |
| 9 | `CF88:ART.34:INC.IV` | Art. 34, inciso IV — Livre exercício dos Poderes estaduais | **YELLOW** | NO | NO |
| 10 | `CF88:ART.34:INC.V` | Art. 34, inciso V — Reorganização das finanças | **YELLOW** | NO | NO |
| 11 | `CF88:ART.34:INC.VI` | Art. 34, inciso VI — Execução de lei federal e de decisões judiciais | **YELLOW** | NO | NO |
| 12 | `CF88:ART.34:INC.VII` | Art. 34, inciso VII — Princípios constitucionais sensíveis | **YELLOW** | NO | NO |
| 13 | `CF88:ART.35` | Art. 35 — Intervenção nos Municípios | **YELLOW** | NO | NO |
| 14 | `CF88:ART.35:INC.I` | Art. 35, incisos I, II e III — Falhas graves de gestão municipal | **YELLOW** | NO | NO |
| 15 | `CF88:ART.35:INC.IV` | Art. 35, inciso IV — Representação ao Tribunal de Justiça | **YELLOW** | YES | NO |
| 16 | `CF88:ART.36` | Art. 36 — Procedimento da intervenção | **YELLOW** | NO | NO |
| 17 | `CF88:ART.36:INC.I` | Art. 36, incisos I, II e III — Quem provoca a intervenção | **RED** | YES | YES |
| 18 | `CF88:ART.36:PAR.1` | Art. 36, §§ 1º e 2º — Decreto e controle pelo Legislativo | **YELLOW** | NO | NO |
| 19 | `CF88:ART.36:PAR.3` | Art. 36, § 3º — Decreto limitado à suspensão do ato | **YELLOW** | NO | NO |
| 20 | `CF88:ART.36:PAR.4` | Art. 36, § 4º — Fim da intervenção | **GREEN** | NO | NO |

## RISK_REASONS

### `CF88:ART.32` — YELLOW

- **TITLE:** Art. 32 — Distrito Federal
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - Distrito Federal: quórum e prazo da Lei Orgânica (dois turnos, dez dias, dois terços)
  - vedação de divisão em Municípios
  - afirmações de fato fora do texto: Brasília dentro do Distrito Federal; regiões administrativas sem autonomia de Município

### `CF88:ART.32:PAR.1` — YELLOW

- **TITLE:** Art. 32, § 1º — Competências legislativas do Distrito Federal
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - competências legislativas cumulativas (estaduais + municipais)
  - ATENÇÃO remete ao art. 21 (estruturas do Distrito Federal organizadas e mantidas pela União): limite da autonomia

### `CF88:ART.32:PAR.2` — YELLOW

- **TITLE:** Art. 32, §§ 2º e 3º — Eleições e Legislativo do Distrito Federal
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - regra eleitoral (coincidência com as eleições estaduais; art. 77)
  - remissão ao art. 27 (número, mandato, imunidades e subsídio dos Deputados Distritais)

### `CF88:ART.32:PAR.4` — YELLOW

- **TITLE:** Art. 32, § 4º — Forças de segurança do Distrito Federal
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - remissão ao art. 21 (organização e manutenção pela União)
  - lista de forças inclui a polícia penal (redação recente)
  - competência federativa (lei federal disciplina a utilização)

### `CF88:ART.33` — RED

- **TITLE:** Art. 33 — Territórios Federais
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** YES
- **RISK_REASONS:**
  - afirmação de situação fática atual no corpo ("Hoje não existe Território Federal no Brasil")
  - precedente editorial do Batch 03: a revisão humana retirou do núcleo permanente do art. 18 o mesmo dado de fato sobre a inexistência atual de Territórios
  - Territórios: previsão constitucional x situação atual; contas ao Congresso com parecer do Tribunal de Contas da União

### `CF88:ART.33:PAR.3` — YELLOW

- **TITLE:** Art. 33, § 3º — Territórios com mais de cem mil habitantes
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - quantidade (mais de cem mil habitantes)
  - Territórios: hipótese sem Território instalado
  - remissão implícita fora do texto do § 3º: Governador nomeado pelo Presidente após aprovação do Senado (arts. 84, XIV, e 52, III, c)

### `CF88:ART.34` — YELLOW

- **TITLE:** Art. 34 — Intervenção federal: regra e exceção
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - intervenção federal: regra (autonomia) x exceção; hipóteses taxativas
  - decretação pelo Presidente (art. 84, X, fora do texto do art. 34)
  - exemplo de intervenção limitada à segurança pública

### `CF88:ART.34:INC.I` — YELLOW

- **TITLE:** Art. 34, incisos I, II e III — Unidade nacional e ordem pública
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - hipóteses taxativas (integridade nacional, invasão, ordem pública)
  - interpretação de "grave comprometimento" (meios normais insuficientes)

### `CF88:ART.34:INC.IV` — YELLOW

- **TITLE:** Art. 34, inciso IV — Livre exercício dos Poderes estaduais
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - solicitação x requisição (art. 36, I)
  - definição de requisição como "força de ordem" é leitura doutrinária

### `CF88:ART.34:INC.V` — YELLOW

- **TITLE:** Art. 34, inciso V — Reorganização das finanças
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - prazo (mais de dois anos consecutivos) e exceção (força maior)
  - conceito técnico (dívida fundada, definida em lei)

### `CF88:ART.34:INC.VI` — YELLOW

- **TITLE:** Art. 34, inciso VI — Execução de lei federal e de decisões judiciais
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - procedimento dependente (art. 36, II e III)
  - decreto limitado à suspensão do ato (art. 36, § 3º)

### `CF88:ART.34:INC.VII` — YELLOW

- **TITLE:** Art. 34, inciso VII — Princípios constitucionais sensíveis
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - princípios sensíveis (cinco alíneas)
  - representação interventiva do Procurador-Geral da República ao Supremo
  - grau de vinculação do Presidente após o provimento (o texto do candidato diz "pode ser decretada")

### `CF88:ART.35` — YELLOW

- **TITLE:** Art. 35 — Intervenção nos Municípios
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - intervenção estadual x federal (distinção do art. 34)
  - União em Municípios de Território
  - decretação pelo Governador (fora do texto do art. 35)

### `CF88:ART.35:INC.I` — YELLOW

- **TITLE:** Art. 35, incisos I, II e III — Falhas graves de gestão municipal
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - prazo (dois anos consecutivos) e exceção (força maior)
  - mínimos constitucionais de ensino e saúde

### `CF88:ART.35:INC.IV` — YELLOW

- **TITLE:** Art. 35, inciso IV — Representação ao Tribunal de Justiça
- **EXTERNAL_VERIFICATION_NEEDED:** YES · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - hipótese judicial (representação ao Tribunal de Justiça)
  - legitimidade para a representação descrita de forma genérica ("alguém legitimado")
  - possível jurisprudência pertinente à representação interventiva estadual (não verificada)

### `CF88:ART.36` — YELLOW

- **TITLE:** Art. 36 — Procedimento da intervenção
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - procedimento: provocação, decreto, controle legislativo em 24 horas, decreto limitado, cessação
  - dispositivo revogado (inciso IV) mencionado na ATENÇÃO

### `CF88:ART.36:INC.I` — RED

- **TITLE:** Art. 36, incisos I, II e III — Quem provoca a intervenção
- **EXTERNAL_VERIFICATION_NEEDED:** YES · **EDITORIAL_DECISION_NEEDED:** YES
- **RISK_REASONS:**
  - solicitação x requisição x provimento: o grau de vinculação do Presidente em cada forma é interpretação (doutrina/jurisprudência)
  - decisão editorial: quanto dessa distinção entra no corpo e quanto vai à CAMADA EXTERNA
  - hipóteses de decretação por iniciativa própria (art. 34, I, II, III e V) descritas por exclusão
  - inciso IV revogado, fora do bloco

### `CF88:ART.36:PAR.1` — YELLOW

- **TITLE:** Art. 36, §§ 1º e 2º — Decreto e controle pelo Legislativo
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - prazo (vinte e quatro horas)
  - decreto de intervenção (amplitude, prazo, condições, interventor)
  - controle legislativo e convocação extraordinária

### `CF88:ART.36:PAR.3` — YELLOW

- **TITLE:** Art. 36, § 3º — Decreto limitado à suspensão do ato
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - exceção: dispensa de apreciação legislativa (art. 34, VI e VII; art. 35, IV)
  - decreto limitado à suspensão do ato impugnado

### `CF88:ART.36:PAR.4` — GREEN

- **TITLE:** Art. 36, § 4º — Fim da intervenção
- **EXTERNAL_VERIFICATION_NEEDED:** NO · **EDITORIAL_DECISION_NEEDED:** NO
- **RISK_REASONS:**
  - texto estável e diretamente derivado da Constituição (cessação da intervenção e retorno das autoridades, salvo impedimento legal)

## Pontos de atenção do Round 3

- **Distrito Federal (art. 32):** competências cumulativas, mas estruturas organizadas e mantidas pela União (art. 21); conferir que o texto não sugere autonomia plena de Estado.
- **Territórios (art. 33):** separar previsão constitucional de situação fática atual, à luz da decisão do Batch 03 sobre o art. 18.
- **Intervenção (arts. 34 a 36):** hipóteses taxativas; intervenção federal x estadual; solicitação x requisição x provimento; conteúdo do decreto; controle legislativo em 24 horas; dispensa de apreciação no art. 36, § 3º; cessação e retorno das autoridades.

## Sugestão de fluxo

1. GREEN (1): aprovação após leitura rápida.
2. YELLOW (17): auditoria editorial focada nas razões listadas; verificação externa no art. 35, IV.
3. RED (2): decisão editorial antes de aprovar (art. 33: dado de fato no corpo; art. 36, I a III: grau de vinculação nas formas de provocação).
