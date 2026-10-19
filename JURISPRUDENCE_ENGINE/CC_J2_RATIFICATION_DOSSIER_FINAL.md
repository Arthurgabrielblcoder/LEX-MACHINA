# CC-J2 — dossiê FINAL de ratificação

```
TOTAL = 30 · GREEN_FINAL = 9 (SAFE_FOR_BLOCK_RATIFICATION) · YELLOW_FINAL = 10 (INDIVIDUAL_DECISION_REQUIRED) · RED_FINAL = 11 (DO_NOT_RATIFY)
HUMAN_APPROVED_NEW = 0 · SD_CHANGED = NO · FIRMWARE_CHANGED = NO · baseline físico CC = 29/24
PROJECTED_GREEN = 38/32 · PROJECTED_FULL = 49/39 (projeções, não baseline)
```

Lote preservado: 30 candidatos, hashes fixados de 14 arquivos (decisões, revisão, métricas, backlog, simulação, dossiê preliminar e fontes oficiais). Mudanças em relação ao dossiê preliminar: 3 de grupo e 6 de proposta, registradas aqui; `CC_J2_DECISIONS.json` não foi reescrito.

## GREEN FINAL (9) — SAFE_FOR_BLOCK_RATIFICATION (não ratificado)

Os 7 critérios (fonte oficial, precedente vigente, target existente, pertinência direta, sem alerta temporal, sem duplicação com o CC-J1, sem superação) foram reconferidos em todos.

| ID | Precedente | Alvo | Relação material |
|---|---|---|---|
| CCJ2-02 | Súmula 656 STJ | CC2002:ART.835 | O enunciado nomeia o art. 835 (exoneração do fiador por notificação). |
| CCJ2-04 | REPETITIVO STJ 1133 | CC2002:ART.405 | A tese fixa o termo inicial dos juros de mora com base no art. 405. |
| CCJ2-05 | REPETITIVO STJ 1210 | CC2002:ART.50 | Requisitos da desconsideração (Teoria Maior) "nos termos exigidos pelo art. 50". |
| CCJ2-07 | RG TEMA 498 | CC2002:ART.1829 | A tese manda aplicar o regime do art. 1.829; o Planalto anota o RE 646.721 no art. 1.829. |
| CCJ2-14 | REPETITIVO STJ 368 | CC2002:ART.286 | Cessão dos créditos do empréstimo compulsório "notadamente [pelo] art. 286". |
| CCJ2-16 | REPETITIVO STJ 1109 | CC2002:ART.191 | Delimita a renúncia tácita à prescrição do art. 191. |
| CCJ2-17 | RG TEMA 809 | CC2002:ART.1829 | Mesma tese do Tema 498 em tema próprio (questão diferente: união heteroafetiva); o Planalto anota o RE 878.694 no art. 1.829. |
| CCJ2-23 | REPETITIVO STJ 308 | CC2002:ART.206:PAR.3:INC.III | Dividendos prescrevem em três anos "nos termos do art. 206, § 3º, inciso III". |
| CCJ2-25 | REPETITIVO STJ 426 | CC2002:ART.354 | Aplica ao SFH a imputação do art. 354, salvo cláusula em contrário. |

## YELLOW FINAL (10) — decisão individual

### CCJ2-01 — Súmula 619 STJ

- **Target proposto:** CC2002:ART.1208, CC2002:ART.1255
- **Fonte oficial:** https://processo.stj.jus.br/SCON/getFile?url=/docs_internet/jurisprudencia/tematica/download/SU/Sumulas/SumulasSTJ.pdf (sha256 `bf92bdb1ae0d…`); CORTE ESPECIAL, 24/10/2018
- **Relação material (DIRECT):** Dois pontos distintos: (i) ocupação de bem público é detenção (art. 1.208: atos de mera tolerância não induzem posse); (ii) não há indenização por acessões (o art. 1.255 dá indenização ao construtor de boa-fé, aqui afastada). Benfeitorias e retenção (art. 1.219) também são afastadas, mas o STJ não referencia esse artigo. O art. 1.198 (detentor por dependência) não é o caso.
- **Temporalidade:** CURRENT
- **Risco:** Baixo. Duas referências do STJ, dois vínculos materiais reais; o 1.219 fica de fora por falta de referência oficial.
- **Alternativas:** A. aprovar como proposto (1.208 e 1.255) · B. só o art. 1.208 (detenção) · C. rejeitar · D. manter pendente
- **Recomendação do motor:** A — MULTI_TARGET; ficha: Explicar os dois efeitos: detenção (1.208) e ausência de indenização por acessões (1.255) e benfeitorias.
- **Minha confiança:** HIGH

### CCJ2-06 — IAC 1

- **Target proposto:** CC2002:ART.202:PAR.UNICO
- **Fonte oficial:** https://dadosabertos.web.stj.jus.br/dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/resource/df29da13-7d6b-41ba-ad96-cd1a5bbd191c/download/temas.csv (sha256 `98f1506ec8f0…`); S2, j. 2018-06-27
- **Relação material (DIRECT):** Prescrição intercorrente nas execuções do CPC/73 "conforme interpretação extraída do art. 202, parágrafo único". Utilidade atual: execuções antigas ainda em curso e a leitura do reinício do prazo; para o CPC/2015 vale o art. 921.
- **Temporalidade:** HISTORICAL_BUT_RELEVANT
- **Risco:** Médio: leitor aplicar a regra a execuções do CPC/2015. Primeiro IAC do aparelho: o rótulo "IAC n" existe no firmware, mas não foi validado fisicamente (requisito de teste físico futuro, não impede a ratificação jurídica).
- **Alternativas:** A. aprovar como proposto (HISTORICAL_BUT_RELEVANT, com nota CPC/73) · B. — · C. rejeitar (só histórico) · D. manter pendente
- **Recomendação do motor:** A — PROMOTE; ficha: "Aplica-se às execuções regidas pelo CPC/1973; sob o CPC/2015, ver art. 921."
- **Minha confiança:** MEDIUM

### CCJ2-08 — REPETITIVO STJ 639

- **Target proposto:** CC2002:ART.206:PAR.5:INC.I (antes: CC2002:ART.206:PAR.5:INC.I, CC2002:ART.2028)
- **Fonte oficial:** https://dadosabertos.web.stj.jus.br/dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/resource/df29da13-7d6b-41ba-ad96-cd1a5bbd191c/download/temas.csv (sha256 `98f1506ec8f0…`); S1, j. 2014-10-22
- **Relação material (DIRECT):** Para contratos sob o CC/2002 a tese aplica diretamente o art. 206, § 5º, I. O art. 2.028 aparece como ressalva ("sem embargo da norma de transição") e já tem a Súmula 547 (CC-J1) com a mesma função: vincular de novo não acrescenta informação.
- **Temporalidade:** CURRENT
- **Risco:** Baixo. Tema da Primeira Seção (crédito rural cedido à União, execução fiscal); a ficha deve dizer o contexto.
- **Alternativas:** A. aprovar como proposto originalmente (206, § 5º, I + 2.028) · B. aprovar só o art. 206, § 5º, I · C. rejeitar · D. manter pendente
- **Recomendação do motor:** B — PROMOTE; ficha: Contexto: crédito rural, execução fiscal; 20 anos (CC/1916) ou 5 anos (CC/2002).
- **Minha confiança:** HIGH
- **Mudança:** MULTI_TARGET (206, § 5º, I + 2.028) → PROMOTE só no 206, § 5º, I

### CCJ2-09 — Súmula 642 STJ

- **Target proposto:** CC2002:ART.943
- **Fonte oficial:** https://processo.stj.jus.br/SCON/getFile?url=/docs_internet/jurisprudencia/tematica/download/SU/Sumulas/SumulasSTJ.pdf (sha256 `bf92bdb1ae0d…`); CORTE ESPECIAL, 02/12/2020
- **Relação material (DIRECT):** Transmissibilidade do direito à indenização por dano moral: o art. 943 ("transmitem-se com a herança") é o fundamento direto. 1.829/1.839 só identificam os herdeiros; 948 trata do homicídio; o 12 é referência oficial, mas sobre tutela da personalidade.
- **Temporalidade:** CURRENT
- **Risco:** Baixo para o vínculo; a anomalia da fonte fica registrada e nenhum alvo inexistente é criado.
- **Alternativas:** A. aprovar como proposto (realocar para o art. 943) · B. 943 e também o art. 12 · C. rejeitar · D. manter pendente
- **Recomendação do motor:** A — REALLOCATE
- **Minha confiança:** HIGH
- **Anomalia da fonte:** STJ_REFERENCE_TO_NONEXISTENT_DISPOSITIVO: o PDF oficial referencia "ART:00943 INC:00001", mas o art. 943 não tem incisos (texto compilado do Planalto). Erro estrutural/editorial da fonte.

### CCJ2-11 — REPETITIVO STJ 1019

- **Target proposto:** CC2002:ART.1238:PAR.UNICO
- **Fonte oficial:** https://dadosabertos.web.stj.jus.br/dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/resource/df29da13-7d6b-41ba-ad96-cd1a5bbd191c/download/temas.csv (sha256 `98f1506ec8f0…`); S1, j. 2020-02-12
- **Relação material (DIRECT):** A tese usa o prazo de 10 anos "conforme parágrafo único do art. 1.238", e o fundamento é o requisito especial do p.u. ("obras ou serviços de caráter produtivo"), equiparado às obras do Poder Público. Não trata do caput (15 anos).
- **Temporalidade:** CURRENT
- **Risco:** Baixo; tema de direito público (desapropriação indireta) num dispositivo de usucapião: a ficha deve dizer isso.
- **Alternativas:** A. aprovar como proposto (1.238, p.u.) · B. manter no artigo (caput) · C. rejeitar · D. manter pendente
- **Recomendação do motor:** A — REALLOCATE
- **Minha confiança:** HIGH

### CCJ2-18 — Súmula 637 STJ

- **Target proposto:** CC2002:ART.1210:PAR.2
- **Fonte oficial:** https://processo.stj.jus.br/SCON/getFile?url=/docs_internet/jurisprudencia/tematica/download/SU/Sumulas/SumulasSTJ.pdf (sha256 `bf92bdb1ae0d…`); CORTE ESPECIAL, 06/11/2019
- **Relação material (EXCEPTION):** Exceção: o § 2º veda a exceção de domínio na possessória; a súmula permite que o ente público que intervém alegue até o domínio. Útil justamente por limitar a leitura literal do dispositivo.
- **Temporalidade:** CURRENT
- **Risco:** Médio: a ficha precisa dizer "exceção", não concordância com o texto.
- **Alternativas:** A. aprovar como proposto (como EXCEPTION) · B. — · C. rejeitar (processual) · D. manter pendente
- **Recomendação do motor:** A — PROMOTE; ficha: "Exceção ao art. 1.210, § 2º: o ente público pode deduzir o domínio ao intervir na possessória entre particulares."
- **Minha confiança:** MEDIUM

### CCJ2-20 — Súmula 655 STJ

- **Target proposto:** CC2002:ART.1641:INC.II
- **Fonte oficial:** https://processo.stj.jus.br/SCON/getFile?url=/docs_internet/jurisprudencia/tematica/download/SU/Sumulas/SumulasSTJ.pdf (sha256 `bf92bdb1ae0d…`); SEGUNDA SEÇÃO, 09/11/2022
- **Relação material (DIRECT):** Compatível com o Tema 1236: o STF manteve a separação do art. 1.641, II como regime legal que vale "à falta de convenção" (o caso concreto a aplicou); a súmula rege a união estável sem pacto e acrescenta a comunicação dos aquestos com esforço comum. Não é duplicata: o Tema 1236 trata do afastamento por escritura, a súmula, do regime aplicável sem ela.
- **Temporalidade:** CURRENT
- **Risco:** Médio: sem a ressalva, a ficha faria o regime parecer cogente.
- **Alternativas:** A. aprovar como proposto (ficha com a ressalva do Tema 1236) · B. — · C. rejeitar (superada) · D. manter pendente
- **Recomendação do motor:** A — PROMOTE; ficha: "Após o Tema 1236/STF (2024), o regime pode ser afastado por escritura pública; sem pacto, aplica-se esta súmula."
- **Minha confiança:** MEDIUM
- **Mudança:** temporal NEEDS_REVIEW → CURRENT (compatibilidade com o Tema 1236 verificada)

### CCJ2-21 — REPETITIVO STJ 381

- **Target proposto:** CC2002:ART.354
- **Fonte oficial:** https://dadosabertos.web.stj.jus.br/dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/resource/df29da13-7d6b-41ba-ad96-cd1a5bbd191c/download/temas.csv (sha256 `98f1506ec8f0…`); S1, j. 2010-06-09
- **Relação material (EXCLUSION_CONTEXT):** Jurisprudência negativa: delimita o campo do art. 354 (não se aplica à compensação tributária; originou a Súmula 464/STJ). Útil ao lado do Tema 426 (que aplica o art. 354 ao SFH): o leitor vê onde a regra vale e onde não vale.
- **Temporalidade:** CURRENT
- **Risco:** Médio: não pode parecer interpretação positiva da regra civil.
- **Alternativas:** A. aprovar como proposto (EXCLUSION_CONTEXT, com nota editorial) · B. — · C. rejeitar (tributário) · D. manter pendente
- **Recomendação do motor:** A — PROMOTE; ficha: "Exclusão: a imputação do art. 354 NÃO se aplica à compensação tributária."
- **Minha confiança:** MEDIUM

### CCJ2-22 — REPETITIVO STJ 1130

- **Target proposto:** CC2002:ART.76:PAR.UNICO
- **Fonte oficial:** https://dadosabertos.web.stj.jus.br/dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/resource/df29da13-7d6b-41ba-ad96-cd1a5bbd191c/download/temas.csv (sha256 `98f1506ec8f0…`); S1, j. 2024-10-09
- **Relação material (DIRECT):** "Domicílio necessário (art. 76, parágrafo único)" do servidor define o alcance do título coletivo do sindicato.
- **Temporalidade:** CURRENT
- **Risco:** Médio e diminuindo: o obstáculo no STF acabou (sem RG), mas o dataset do STJ ainda não registra o trânsito.
- **Alternativas:** A. aprovar como proposto (PROVISIONAL, com gatilho) · B. — · C. rejeitar · D. manter pendente até o STJ registrar o trânsito
- **Recomendação do motor:** A — PROMOTE_PROVISIONAL
- **Minha confiança:** MEDIUM
- **Provisório:** STJ: "Acórdão Publicado - RE Pendente" (dataset de 2026-10-09); gatilho: confirmar no STJ a situação "Trânsito em Julgado"; o STF já negou repercussão geral no Tema 1432 (trânsito em 18/09/2026), então o RE não deve alterar a tese; registro: J2_PROVISIONAL_REGISTRY (se ratificado)

### CCJ2-29 — REPETITIVO STJ 610

- **Target proposto:** CC2002:ART.206:PAR.3:INC.IV (antes: CC2002:ART.206:PAR.3:INC.IV, CC2002:ART.2028)
- **Fonte oficial:** https://dadosabertos.web.stj.jus.br/dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/resource/df29da13-7d6b-41ba-ad96-cd1a5bbd191c/download/temas.csv (sha256 `98f1506ec8f0…`); S2, j. 2016-08-10
- **Relação material (DIRECT):** O prazo trienal do art. 206, § 3º, IV para a nulidade de reajuste de plano de saúde é informação própria (setor). O art. 2.028 cumpre a mesma função da Súmula 547 já no CC-J1: não multiplicar vínculos de transição.
- **Temporalidade:** CURRENT
- **Risco:** Baixo.
- **Alternativas:** A. aprovar como proposto originalmente (206, § 3º, IV + 2.028) · B. aprovar só o art. 206, § 3º, IV · C. rejeitar · D. manter pendente
- **Recomendação do motor:** B — PROMOTE
- **Minha confiança:** HIGH
- **Mudança:** MULTI_TARGET (206, § 3º, IV + 2.028) → PROMOTE só no 206, § 3º, IV

## RED FINAL (11) — não ratificar

| ID | Precedente | Categoria | Razão | Reabrir se |
|---|---|---|---|---|
| CCJ2-03 | RG TEMA 1236 | REJECT_NOT_MATERIAL (antes YELLOW) | O art. 1.639, § 2º aparece só como exemplo ("e.g.") na modulação do ARE 1309642; não é interpretado e não é necessário para compreender a tese, que já está no art. 1.641, II (CCJ1-06). | Se STF ou STJ decidirem a mudança de regime (art. 1.639, § 2º) de casamentos com maiores de 70 anos. |
| CCJ2-10 | RG TEMA 920 | REJECT_SUPERSEDED | Repercussão geral negada (questão infraconstitucional), sem tese de mérito; a matéria foi decidida com RG no Tema 932, já no CC-J1 (art. 927, p.u.). | Nunca como precedente de mérito. |
| CCJ2-12 | REPETITIVO STJ 26 | REJECT_TEMPORAL_MISMATCH | A tese afasta o limite "do art. 591 c/c o art. 406". A Lei 14.905/2024 reescreveu os dois: o art. 591 só presume juros e o art. 406 remete à taxa legal. O limite discutido não existe mais no texto. | Se o STJ reafirmar a tese sob a redação da Lei 14.905/2024. |
| CCJ2-13 | RG TEMA 529 | REJECT_NOT_MATERIAL (antes YELLOW) | A fidelidade aparece como valor do "ordenamento jurídico-constitucional" (monogamia), não como interpretação do art. 1.566, I. A ratio é constitucional e previdenciária; a mesma razão levou o usuário a recusar o art. 1.727 no CC-J1. A evidência não é forte o bastante para um novo vínculo contextual. | Se surgir precedente que interprete o dever de fidelidade do art. 1.566, I como regra civil. |
| CCJ2-15 | Súmula 530 STJ | REJECT_NOT_MATERIAL | Núcleo é a taxa média do Bacen nos contratos bancários; arts. 112/122/170 são cânones gerais e 406/591 foram reescritos pela Lei 14.905/2024. | Se um precedente fundamentar a taxa média no art. 170 ou no art. 122. |
| CCJ2-19 | Súmula 539 STJ | REJECT_TEMPORAL_MISMATCH | A referência ao art. 591 era à "capitalização anual"; a Lei 14.905/2024 tirou a capitalização do texto. | Se a capitalização voltar ao CC ou o STJ vincular a súmula à redação nova. |
| CCJ2-24 | Súmula 541 STJ | REJECT_TEMPORAL_MISMATCH | Mesma razão da Súmula 539 (pactuação da capitalização contra a redação antiga do art. 591). | Idem à Súmula 539. |
| CCJ2-26 | REPETITIVO STJ 309 | DUPLICATE_RECOMMENDATION | Duplicata material do Tema 308: questão submetida e tese firmada idênticas, caractere por caractere, no dataset oficial (mesmo julgamento, outro recurso). | Só se o usuário quiser registrar os dois temas. |
| CCJ2-27 | Súmula 465 STJ | REJECT_TEMPORAL_MISMATCH | Arts. 757, 765 e 785 revogados pela Lei 15.040/2024 (o contrato de seguro saiu do CC). | Se o STJ reafirmar a súmula sob a Lei 15.040/2024 (o vínculo iria para a lei nova, fora do CC). |
| CCJ2-28 | REPETITIVO STJ 587 | REJECT_NOT_MATERIAL (antes YELLOW) | Predominantemente processual (honorários de embargos e de execução, CPC/73; o CPC/2015, art. 85, § 14, resolve a questão). O art. 368 entra só como premissa (falta de reciprocidade); o leitor do art. 368 ganha pouco. | Se surgir precedente civil sobre o requisito de reciprocidade da compensação. |
| CCJ2-30 | Súmula 610 STJ | REJECT_TEMPORAL_MISMATCH | Arts. 797 e 798 revogados pela Lei 15.040/2024. | Idem à Súmula 465. |

## Escala

| Item | Linhas | Natureza |
|---|---:|---|
| batch_engine.py | 351 | ONE_TIME_ENGINE_GENERALIZATION (não recorrente) |
| discovery_stj_precedentes.py | 122 | adapter novo (uma vez por fonte) |
| build_cc_j2.py, configuração recorrente | 146 | RECURRING_BATCH_CODE |
| build_cc_j2.py, comparação CC-J1 | 89 | só deste lote |
| build_cc_j2.py, relatórios genéricos | 54 | mover para o motor (uma vez) |
| build_cc_j2_final_dossier.py | 195 | código de lote desta missão (não é motor) |
| Dados de revisão (preliminar + final) | 341 | julgamento humano, não código |

NEW_CORE_ENGINE_CODE_THIS_DOSSIER = 0. Meta do próximo lote: NEW_CORE_ENGINE_CODE = 0; o custo recorrente esperado é só configuração e tabela de revisão. Os relatórios genéricos e este gerador de dossiê final devem ir para o motor uma única vez.

Requisitos de teste físico se ratificados: IAC (FIRMWARE_LABEL_EXISTS_NOT_PHYSICALLY_VALIDATED), REPETITIVO (FIRMWARE_LABEL_EXISTS_NOT_PHYSICALLY_VALIDATED).
Entram no registro de provisórios se ratificados: STJ:REPETITIVO:1130.

Nada foi ratificado, materializado, implantado ou gravado. A decisão é do usuário.
