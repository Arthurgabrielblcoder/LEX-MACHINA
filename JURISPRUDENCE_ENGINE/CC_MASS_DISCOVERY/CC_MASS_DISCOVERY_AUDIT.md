# CC MASS DISCOVERY — auditoria de qualidade do motor (Passagem 2)

```
SAMPLED_RELATIONS = 40 · REVIEWED = 40 · SOURCE_IDENTITY_ERRORS = 0 · TARGET_MAPPING_ERRORS = 0 · TEMPORAL_ERRORS = 0 · MATERIAL_RELEVANCE_ERRORS = 3 · DUPLICATE_ERRORS = 0
```

Amostra determinística e estratificada (primeiro item de cada estrato tier × fonte × classe, completada pela ordem do sha256 do id). Cada item foi relido na fonte oficial (texto da tese/enunciado/ementa e referência estruturada já capturados com hash). Erros sistemáticos encontrados durante a operação foram corrigidos na regra e o grupo inteiro reprocessado (seção final).

| ID | Tier | Precedente | Target | Fonte | Identidade | Target | Temporal | Pertinência | Duplicata | Nota |
|---|---|---|---|---|---|---|---|---|---|---|
| CCMD-0C190B7EAC | B | STJ:RESP:2145365 | CC2002:ART.1668 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 2145365: comunhão universal, "ressalvadas as hipóteses do art. 1.668" nas razões; listado nos dispositivos relevantes. |
| CCMD-0CBA176F7F | A | STJ:REPETITIVO:310 | CC2002:ART.2028 | STJ_PRECEDENTES_QUALIFICADOS | OK | OK | OK | OK | OK | Tema 310: a tese nomeia "regra de transição prevista no art. 2.028 do Código Civil de 2002". |
| CCMD-10DDDFCC37 | B | STJ:RESP:1679434 | CC2002:ART.2045 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1679434: "O art. 2.045 do CC/2002 revogou o art. 499 do CCo/1850" — fundamento da decisão (prazo do frete). |
| CCMD-151261A851 | B | STJ:RESP:1642331 | CC2002:ART.935 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1642331: "Nos termos do art. 935 do CC/02, a responsabilidade civil é independente da criminal". |
| CCMD-2820EB2A75 | B | STJ:ERESP:1951463 | CC2002:ART.205 | STJ_ESPELHOS_ACORDAOS | OK | OK | OK | OK | OK | EREsp 1951463: dispositivo e tese aplicam o prazo decenal do art. 205; o § 3º, IV só aparece na questão (corretamente em C). |
| CCMD-2C2E1C2939 | A | STJ:REPETITIVO:919 | CC2002:ART.2028 | STJ_ESPELHOS_ACORDAOS, STJ_PRECEDENTES_QUALIFICADOS | OK | OK | OK | OK | OK | Tema 919: "norma de transição do art. 2.028 desse último Diploma Legal" (CC/2002) na tese. |
| CCMD-2D74B31D75 | A | STJ:SUMULA:464 | CC2002:ART.354 | STJ_SUMULAS_PDF | OK | OK | OK | OK | OK | Súmula 464: o enunciado nomeia o art. 354 do Código Civil (imputação de pagamento). |
| CCMD-2FAFBF3E2A | B | STJ:RESP:2000938 | CC2002:ART.1876 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 2000938: testamento particular sem testemunhas, art. 1.876 nas razões. |
| CCMD-30C7163126 | A | STF:RG:1232 | CC2002:ART.50 | STF_JURISPRUDENCIA | OK | OK | OK | OK | OK | Tema 1232 STF: a tese remete ao incidente de desconsideração (art. 50 do CC); § 4º colapsado ao artigo (sem apoio textual). |
| CCMD-32DDED89ED | B | STJ:RESP:2230861 | CC2002:ART.1368-E | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 2230861: "responsabilidade civil do fundo ... à luz do art. 1.368-E" nas razões (o REsp da corretora não foi conhecido, o outro sim). |
| CCMD-346650603A | B | STJ:EARESP:749198 | CC2002:ART.205 | STJ_ESPELHOS_ACORDAOS | OK | OK | OK | OK | OK | EAREsp 749198: prescrição decenal (art. 205 do CC/2002) na verbetação e nas razões. |
| CCMD-43C15E049C | B | STF:ADPF:132 | CC2002:ART.1723 | STF_JURISPRUDENCIA | OK | OK | OK | OK | OK | ADPF 132 (com ADI 4277): interpretação conforme do art. 1.723; sinal USO_CONTEXTUAL é cautela, a pertinência é direta. |
| CCMD-4BE8F727D8 | B | STJ:RESP:1256825 | CC2002:ART.1229 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1256825: "O art. 1.229 do Código Civil ... critério de utilidade" — fundamento. |
| CCMD-5153BF964A | B | STJ:REPETITIVO:1418 | CC2002:ART.168:PAR.UNICO | STJ_PRECEDENTES_QUALIFICADOS | OK | OK | OK | OK | OK | Tema 1418 (afetado): art. 168, parágrafo único, na questão; corretamente PROVISÓRIO (B). |
| CCMD-559F64C0DA | B | STJ:RESP:2253418 | CC2002:ART.202:INC.III | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 2253418: "nos termos do art. 202, III, do CC/02, houve a interrupção" — aplicação direta. |
| CCMD-5683B057FF | B | STJ:REPETITIVO:433 | CC2002:ART.381 | STJ_ESPELHOS_ACORDAOS, STJ_PRECEDENTES_QUALIFICADOS | OK | OK | OK | OK | OK | Tema 433: confusão (art. 381) é o fundamento da tese sobre honorários à Defensoria; evidência na questão (B). |
| CCMD-592825F303 | B | STJ:RESP:1148631 | CC2002:ART.1201:PAR.UNICO | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1148631: justo título do parágrafo único do art. 1.201 como critério da melhor posse. |
| CCMD-5AFED73989 | B | STJ:RESP:1099480 | CC2002:ART.108 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1099480: "interpretação do art. 108 do CC" é o objeto do julgamento. |
| CCMD-6199799E8E | B | STJ:ARESP:3006916 | CC2002:ART.1348:INC.II | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | AREsp 3006916: nas razões, legitimidade do condomínio "com base no art. 1.348, II, do CC". |
| CCMD-6263C35580 | B | STJ:SUMULA:504 | CC2002:ART.206:PAR.5:INC.I | STJ_SUMULAS_PDF | OK | OK | OK | OK | OK | Súmula 504: referência legislativa oficial ao art. 206, § 5º, I (monitória de nota promissória); evidência estruturada (B). |
| CCMD-676822FFFA | B | STJ:RESP:1994309 | CC2002:ART.1368-B | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1994309: penhora do imóvel "em violação do art. 1.368-B do Código Civil" — fundamento. |
| CCMD-7442242D4C | B | STJ:REPETITIVO:1173 | CC2002:ART.722 | STJ_ESPELHOS_ACORDAOS | OK | OK | OK | OK | OK | Tema 1173 (corretor): referência legislativa do leading case ao art. 722 (contrato de corretagem); só estruturada (B). |
| CCMD-8E2CA0B9DF | B | STJ:RESP:715894 | CC2002:ART.112 | STJ_ESPELHOS_ACORDAOS | OK | OK | OK | OK | OK | REsp 715894 (2006): "arts. 112 e 113 do CC/02" nomeados expressamente; estruturada + lista (B). |
| CCMD-90D0827DD1 | B | STF:ADI:3890 | CC2002:ART.45 | STF_JURISPRUDENCIA | OK | OK | OK | ERRO: uso conceitual (personalidade/registro de entidade sindical) em ADI trabalhista | OK | ADI 3890: o art. 45 é citado como conceito; não é jurisprudência sobre o dispositivo. Sinal USO_CONTEXTUAL o pôs no grupo de risco. |
| CCMD-9D7DBC8E22 | B | STJ:RESP:2050372 | CC2002:ART.1347 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 2050372: administração pelo síndico (art. 1.347 do CC/02) fundamenta a ilegitimidade do condômino. |
| CCMD-9DDEB4D26D | B | STJ:RESP:447431 | CC2002:ART.406 | STJ_ESPELHOS_ACORDAOS | OK | OK | OK | OK | OK | REsp 447431 (2007): juros "a partir da vigência do atual Código Civil na forma do respectivo art. 406"; sinal de redação alterada correto. |
| CCMD-A5C6A7EA91 | B | STF:RG:581 | CC2002:ART.247 | STF_JURISPRUDENCIA | OK | OK | OK | ERRO: uso conceitual (obrigação de fazer) em tese tributária de ISS | OK | Tema 581 STF: o art. 247 entra só na legislação citada; a tese é de ISS. Sinal USO_CONTEXTUAL o pôs no grupo de risco. |
| CCMD-AEEB402E4E | B | STF:ADC:29 | CC2002:ART.187 | STF_JURISPRUDENCIA | OK | OK | OK | ERRO: abuso de direito usado como analogia em matéria eleitoral | OK | ADC 29/30 + ADI 4578 (julgamento conjunto, contado uma vez): o art. 187 é analogia; sinal USO_CONTEXTUAL correto. |
| CCMD-BFF84F1F9B | B | STJ:RESP:1385957 | CC2002:ART.281 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1385957: "Inteligência do art. 281 do CC/02" — exceções pessoais do devedor solidário. |
| CCMD-C474A5287E | B | STJ:RESP:1792271 | CC2002:ART.161 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1792271: fraude contra credores exige ação pauliana (CC/2002, art. 161). |
| CCMD-CBA1562FD9 | B | STJ:RESP:665651 | CC2002:ART.1499:INC.IV | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 665651: aplicou o CC/1916 (arts. 849, III, e 851), "correspondentes aos arts. 1.499, IV, e 1.500"; sinal CORRESPONDENCIA_CC1916 correto. |
| CCMD-CD9CE0D87D | B | STJ:ARESP:3007847 | CC2002:ART.1660:INC.V | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | AREsp 3007847: "Interpretação do art. 1.660, V, do CC" sobre benfeitorias na partilha. |
| CCMD-D2CC9B4160 | B | STJ:RESP:2198859 | CC2002:ART.1336:PAR.2 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 2198859: mérito sobre a "interpretação do art. 1.336, § 2º" (multa condominial). |
| CCMD-D68F6F62CC | B | STJ:RESP:1621610 | CC2002:ART.2027 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1621610: rejeita exegese extensiva da exceção do art. 2.027 (anulação da partilha) — fundamento. |
| CCMD-DCDF574EC7 | B | STJ:RESP:1183133 | CC2002:ART.548 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1183133: "O art. 548 do Código Civil estabelece ser nula a doação de todos os bens" — fundamento. |
| CCMD-E457197ADF | B | STJ:SEC:1735 | CC2002:ART.1030:PAR.UNICO | STJ_ESPELHOS_ACORDAOS | OK | OK | OK | OK | OK | SEC 1735: interesse do sócio pelo parágrafo único do art. 1.030; classe homologatória sinalizada (B). |
| CCMD-E736FD445A | B | STJ:RESP:2039541 | CC2002:ART.1857:PAR.1 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 2039541: interpretação do art. 1.857, § 1º (legítima e testamento) — mérito provido. |
| CCMD-E9A1EB9C99 | B | STJ:RESP:1559595 | CC2002:ART.627 | STJ_ESPELHOS_TURMAS | OK | OK | OK | OK | OK | REsp 1559595: depósito (art. 627 do CC) na qualificação da relação. |
| CCMD-EFF7D6EB99 | B | STJ:ERESP:1171820 | CC2002:ART.1641:INC.II | STJ_ESPELHOS_ACORDAOS | OK | OK | OK | OK | OK | EREsp 1171820: CC/1916 vigente à época, "matéria atualmente regida pelo art. 1.641, II"; sinal CORRESPONDENCIA_CC1916 correto. |
| CCMD-F1AAAD4657 | B | STJ:ERESP:1141037 | CC2002:ART.3 | STJ_ESPELHOS_ACORDAOS | OK | OK | OK | OK | OK | EREsp 1141037: "art. 3º do mesmo Codex" (absolutamente incapaz) — fundamento da não fluência da prescrição. |

## Regras corrigidas durante a operação (com reprocessamento do grupo)

- **CC/1916 confundido com CC/2002:** "art. 993 do Código Civil de 1916" e "arts. 1.062 e 1.063 do CC/1916" chegaram a virar alvos do CC/2002 (SAME_DIPLOMA e NEAREST_MARKER aceitavam "do Código Civil de 1916"). A regra passou a exigir "mesmo diploma/código" e a respeitar a lei que fecha a lista. Teste de regressão incluído.
- **Granularidade herdada da indexação:** a referência estruturada aponta incisos (art. 1.790, I a IV) que o texto não discute; sem citação textual da unidade, o vínculo sobe ao artigo, e um vínculo genérico cede ao específico do mesmo precedente.
- **Dupla contagem do acórdão paradigma:** o REsp paradigma de um Tema Repetitivo contava como precedente próprio e como o Tema; agora conta uma vez.
- **Indexação documental sem texto:** legislação citada (STF e espelhos do STJ) sem o artigo na tese/ementa vira C (só menção); o mesmo critério para STF e STJ.
- **Questão submetida contra a tese:** dispositivo só na questão, com a tese aplicando outra norma, vira C.
- **Julgamentos conjuntos do STJ:** acórdãos gêmeos da mesma sessão (mesmo órgão, data e ementa salvo "provido/improvido") contavam um por processo (ex.: REsp 2082647, 2100103 e 1929926, 2ª Seção, 12/03/2025); agora uma relação, como já era no STF (ADC 29/30 + ADI 4578).
- **Fallback antes da deduplicação:** "art. 723, parágrafo único" (inexistente no índice) caía no art. 723 e duplicava o par já existente; o fallback passou a ser resolvido antes do agrupamento, e a classe do julgamento conjunto vem do precedente canônico.
- **Inflação por acórdãos de Turma:** a 3ª e a 4ª Turmas repetem o mesmo artigo centenas de vezes (art. 205: 384 acórdãos). Contar cada um seria replicar a relação. Acórdão de Turma (não qualificado) só preenche dispositivo sem vínculo publicado, decidido ou de fonte superior; por dispositivo, um representante (evidência textual forte na ementa; artigo na verbetação; julgamento mais recente; id), os demais viram corroboração (C, ligada ao representante).
- **Recurso não conhecido:** acórdão não qualificado que não conhece do recurso por óbice de admissibilidade (Súmulas 5/7/211/282/283/284, prequestionamento, paradigma) e não dá nem nega provimento não decide o dispositivo → C. O verbo de mérito tem de ser do próprio julgado ("a origem negou provimento" não conta); acórdãos antigos que "não conhecem" depois de decidir a questão, sem óbice, ficam.
- **Menção só na alegação:** dispositivo citado apenas na alegação da parte, na questão em discussão ("saber se..."), no óbice de admissibilidade ou na seção "caso em exame" → C. A lista "Dispositivos relevantes citados" (formato CNJ) cita também os dispositivos barrados: é neutra, e só mantém o vínculo quando for a única menção.
- **Correspondência com o CC/1916:** "arts. 849, III, e 851 do CC/1916, correspondentes aos arts. 1.499, IV, e 1.500 do CC/2002" — a decisão aplicou o código antigo; o vínculo recebe CORRESPONDENCIA_CC1916 (grupo TEMPORALIDADE, nunca TIER A) e perde prioridade como representante.
- **Fonte oficial malformada:** o arquivo mensal 20240229.json da 2ª Seção é JSON inválido ("Sem lançamentos para o mês de fevereiro/2024") e um campo de referência traz "PAR:000P3": registrados (MALFORMED_FILES / GRAMMAR_REJECTS), nunca reparados nem adivinhados.
