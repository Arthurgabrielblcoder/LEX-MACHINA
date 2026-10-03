# ENTENDA CF — Batch 04: relatório de revisão (arts. 25 a 36)

**Estado:** lote em revisão. Round 1 (arts. 25 a 28): **13 explicações `HUMAN_APPROVED_T1`** (APPROVAL_METHOD = ASSISTED_RISK_BASED_HUMAN_REVIEW; REVIEWER_DECISION = ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW). Round 2 (arts. 29 a 31): **24 explicações `HUMAN_APPROVED_T1`** (mesmo método). Round 3 (arts. 32 a 36): **20 explicações `HUMAN_APPROVED_T1`** (mesmo método). **Batch 04 integralmente aprovado: 57 `HUMAN_APPROVED_T1`, 0 pendentes.** Ainda não implantado: a consolidação BATCH04 + run2 → pacote DEVICE V1 é missão separada.
Nada foi commitado. Firmware, SD, vínculos (432), Batches 01–03 e os 9 pilotos não foram alterados.

## 1. Escopo e texto-base

- Arts. 25, 26, 27, 28, 29, 29-A, 30, 31, 32, 33, 34, 35 e 36 da CF88 (13 artigos). Começa no art. 25 e termina no art. 36; o art. 37 e os pilotos não foram tocados.
- Texto-base: CF88_RUNTIME do baseline DEVICE V1 (`7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a`, 587133 bytes).
- O texto por target que o motor ENTENDA usa para o hash é idêntico ao do runtime em **142/142** targets; por isso o `source_text_sha256` de cada explicação vale para o runtime e a detecção STALE continua funcionando (0 explicações STALE).
- Gramática canônica de target_id já aprovada (`CF88:ART.29-A:PAR.2`, `CF88:ART.29:INC.IV:AL.a` …); nenhuma sintaxe nova.

## 2. Números

- Targets estruturais no escopo: **142**; vigentes (CURRENT): **140**; revogado: 1; histórico: 1.
- Explicações candidatas: **57** (OVERVIEW 13, DEVICE 15, BLOCK 16, ITEM 13); média de 217 palavras e 1781 bytes de payload.
- Decisões do plano: BLOCK_ANCHOR 16, COVERED_BY_BLOCK 22, EXPLAIN_DIRECTLY 41, HISTORICAL 1, NO_EXPLANATION_NEEDED 61, REVOKED 1.
- Lookup: 79 linhas (DIRECT 57, COVERED_BY_BLOCK 22).
- Meta: [35, 55] (teto 60): **OUTSIDE_JUSTIFIED**. Justificativa: 57 explicacoes novas (duas acima da meta de 55, abaixo do teto de 60) para 13 artigos e 140 dispositivos vigentes. O lote cobre quatro entes (Estados, Municipios, Distrito Federal e Territorios) e os tres artigos de intervencao; os arts. 29, 29-A e 30 concentram 79 dispositivos. Mesmo com 16 blocos (13 de irmaos, cobrindo 22 dispositivos, e 3 enunciados com alineas), que alcancam ao todo 62 dispositivos sem explicacao propria, separar competencia legislativa de administrativa (art. 30), o parecer previo (art. 31, § 2º) e cada grupo de hipoteses de intervencao exige explicacoes proprias; fundir mais misturaria categorias que o lote deve distinguir.
- Lint (avisos, não bloqueiam): ABSOLUTE_CLAIM 1, JURISPRUDENCE_WORDING_IN_BODY 1, NEAR_COPY_OF_OFFICIAL_TEXT 21, PARENT_REPETITION 2. Os NEAR_COPY são listas e nomes técnicos curtos em O QUE DIZ; os 2 PARENT_REPETITION (26, IV e 36, § 3º, similaridade 0,25 em O QUE DIZ) estão abaixo do limite de bloqueio (0,35).

## 3. BLOCKS e covered targets

| ÂNCORA | TÍTULO | COVERED TARGETS |
|---|---|---|
| `CF88:ART.29:INC.I` | Art. 29, incisos I, II e III — Eleição, mandato e posse no Município | `CF88:ART.29:INC.II`, `CF88:ART.29:INC.III` |
| `CF88:ART.29:INC.IV` | Art. 29, inciso IV — Número máximo de Vereadores | — (enunciado com alíneas/incisos) |
| `CF88:ART.29:INC.V` | Art. 29, incisos V, VI e VII — Remuneração dos agentes políticos municipais | `CF88:ART.29:INC.VI`, `CF88:ART.29:INC.VII` |
| `CF88:ART.29:INC.VIII` | Art. 29, incisos VIII e IX — Garantias e proibições dos Vereadores | `CF88:ART.29:INC.IX` |
| `CF88:ART.29:INC.XII` | Art. 29, incisos XII e XIII — Participação popular no Município | `CF88:ART.29:INC.XIII` |
| `CF88:ART.29-A:INC.I` | Art. 29-A, incisos I, II, III, IV, V e VI — Percentuais por faixa de população | `CF88:ART.29-A:INC.II`, `CF88:ART.29-A:INC.III`, `CF88:ART.29-A:INC.IV`, `CF88:ART.29-A:INC.V`, `CF88:ART.29-A:INC.VI` |
| `CF88:ART.29-A:PAR.2` | Art. 29-A, §§ 2º e 3º — Crimes de responsabilidade no repasse | `CF88:ART.29-A:PAR.3` |
| `CF88:ART.30:INC.VI` | Art. 30, incisos VI e VII — Educação básica e saúde com cooperação | `CF88:ART.30:INC.VII` |
| `CF88:ART.31:PAR.1` | Art. 31, §§ 1º e 4º — Órgãos de contas que auxiliam a Câmara | `CF88:ART.31:PAR.4` |
| `CF88:ART.32:PAR.2` | Art. 32, §§ 2º e 3º — Eleições e Legislativo do Distrito Federal | `CF88:ART.32:PAR.3` |
| `CF88:ART.34:INC.I` | Art. 34, incisos I, II e III — Unidade nacional e ordem pública | `CF88:ART.34:INC.II`, `CF88:ART.34:INC.III` |
| `CF88:ART.34:INC.V` | Art. 34, inciso V — Reorganização das finanças | — (enunciado com alíneas/incisos) |
| `CF88:ART.34:INC.VII` | Art. 34, inciso VII — Princípios constitucionais sensíveis | — (enunciado com alíneas/incisos) |
| `CF88:ART.35:INC.I` | Art. 35, incisos I, II e III — Falhas graves de gestão municipal | `CF88:ART.35:INC.II`, `CF88:ART.35:INC.III` |
| `CF88:ART.36:INC.I` | Art. 36, incisos I, II e III — Quem provoca a intervenção | `CF88:ART.36:INC.II`, `CF88:ART.36:INC.III` |
| `CF88:ART.36:PAR.1` | Art. 36, §§ 1º e 2º — Decreto e controle pelo Legislativo | `CF88:ART.36:PAR.2` |

Covered targets (irmãos): **22**, todos CURRENT, irmãos estruturais reais, sem explicação própria e sem dupla cobertura. Lookup de cada covered target resolve para a âncora (`COVERED_BY_BLOCK`).
Subdivisões de blocos (alíneas do art. 29, IV e VI; incisos do art. 29-A, § 2º; alíneas do art. 34, V e VII) são explicadas no bloco ancestral e, como nos Batches 01–03, não têm linha própria no lookup.

## 4. Explicações candidatas

| TARGET | PAPEL | TÍTULO | PALAVRAS | BYTES |
|---|---|---|---|---|
| `CF88:ART.25` | OVERVIEW | Art. 25 — Estados: auto-organização e competências | 278 | 2329 |
| `CF88:ART.25:PAR.1` | DEVICE | Art. 25, § 1º — Competência remanescente dos Estados | 221 | 1676 |
| `CF88:ART.25:PAR.2` | DEVICE | Art. 25, § 2º — Serviços locais de gás canalizado | 255 | 1957 |
| `CF88:ART.25:PAR.3` | DEVICE | Art. 25, § 3º — Regiões metropolitanas, aglomerações urbanas e microrregiões | 252 | 2201 |
| `CF88:ART.26` | OVERVIEW | Art. 26 — Bens dos Estados | 263 | 1656 |
| `CF88:ART.26:INC.I` | ITEM | Art. 26, inciso I — Águas estaduais | 245 | 1772 |
| `CF88:ART.26:INC.IV` | ITEM | Art. 26, inciso IV — Terras devolutas estaduais | 191 | 1622 |
| `CF88:ART.27` | OVERVIEW | Art. 27 — Assembleias Legislativas e Deputados Estaduais | 239 | 1763 |
| `CF88:ART.27:PAR.1` | DEVICE | Art. 27, § 1º — Mandato e regime dos Deputados Estaduais | 223 | 1993 |
| `CF88:ART.27:PAR.2` | DEVICE | Art. 27, § 2º — Subsídio dos Deputados Estaduais | 183 | 1464 |
| `CF88:ART.28` | OVERVIEW | Art. 28 — Governador e Vice-Governador | 228 | 2071 |
| `CF88:ART.28:PAR.1` | DEVICE | Art. 28, § 1º — Perda do mandato do Governador | 212 | 1668 |
| `CF88:ART.28:PAR.2` | DEVICE | Art. 28, § 2º — Subsídios do Governador, do Vice e dos Secretários | 216 | 1646 |
| `CF88:ART.29` | OVERVIEW | Art. 29 — Município e Lei Orgânica | 283 | 2034 |
| `CF88:ART.29:INC.I` | BLOCK | Art. 29, incisos I, II e III — Eleição, mandato e posse no Município | 232 | 2041 |
| `CF88:ART.29:INC.IV` | BLOCK | Art. 29, inciso IV — Número máximo de Vereadores | 196 | 1480 |
| `CF88:ART.29:INC.V` | BLOCK | Art. 29, incisos V, VI e VII — Remuneração dos agentes políticos municipais | 261 | 1971 |
| `CF88:ART.29:INC.VIII` | BLOCK | Art. 29, incisos VIII e IX — Garantias e proibições dos Vereadores | 229 | 2109 |
| `CF88:ART.29:INC.X` | ITEM | Art. 29, inciso X — Julgamento do Prefeito no Tribunal de Justiça | 201 | 2139 |
| `CF88:ART.29:INC.XII` | BLOCK | Art. 29, incisos XII e XIII — Participação popular no Município | 212 | 1740 |
| `CF88:ART.29:INC.XIV` | ITEM | Art. 29, inciso XIV — Perda do mandato do Prefeito | 174 | 1523 |
| `CF88:ART.29-A` | OVERVIEW | Art. 29-A — Limites de despesa da Câmara Municipal | 251 | 1899 |
| `CF88:ART.29-A:INC.I` | BLOCK | Art. 29-A, incisos I, II, III, IV, V e VI — Percentuais por faixa de população | 267 | 2114 |
| `CF88:ART.29-A:PAR.1` | DEVICE | Art. 29-A, § 1º — Limite da folha de pagamento da Câmara | 184 | 1398 |
| `CF88:ART.29-A:PAR.2` | BLOCK | Art. 29-A, §§ 2º e 3º — Crimes de responsabilidade no repasse | 229 | 1969 |
| `CF88:ART.30` | OVERVIEW | Art. 30 — Competências dos Municípios | 304 | 2350 |
| `CF88:ART.30:INC.I` | ITEM | Art. 30, inciso I — Interesse local | 207 | 1762 |
| `CF88:ART.30:INC.II` | ITEM | Art. 30, inciso II — Competência suplementar do Município | 176 | 1466 |
| `CF88:ART.30:INC.III` | ITEM | Art. 30, inciso III — Tributos municipais e prestação de contas | 176 | 1648 |
| `CF88:ART.30:INC.V` | ITEM | Art. 30, inciso V — Serviços públicos de interesse local | 211 | 1755 |
| `CF88:ART.30:INC.VI` | BLOCK | Art. 30, incisos VI e VII — Educação básica e saúde com cooperação | 205 | 1702 |
| `CF88:ART.30:INC.VIII` | ITEM | Art. 30, inciso VIII — Ordenamento do solo urbano | 183 | 1479 |
| `CF88:ART.30:INC.IX` | ITEM | Art. 30, inciso IX — Patrimônio histórico-cultural local | 207 | 1690 |
| `CF88:ART.31` | OVERVIEW | Art. 31 — Fiscalização do Município | 232 | 1736 |
| `CF88:ART.31:PAR.1` | BLOCK | Art. 31, §§ 1º e 4º — Órgãos de contas que auxiliam a Câmara | 258 | 2099 |
| `CF88:ART.31:PAR.2` | DEVICE | Art. 31, § 2º — Parecer prévio sobre as contas do Prefeito | 205 | 1842 |
| `CF88:ART.31:PAR.3` | DEVICE | Art. 31, § 3º — Contas à disposição do contribuinte | 170 | 1453 |
| `CF88:ART.32` | OVERVIEW | Art. 32 — Distrito Federal | 204 | 1602 |
| `CF88:ART.32:PAR.1` | DEVICE | Art. 32, § 1º — Competências legislativas do Distrito Federal | 155 | 1385 |
| `CF88:ART.32:PAR.2` | BLOCK | Art. 32, §§ 2º e 3º — Eleições e Legislativo do Distrito Federal | 182 | 1556 |
| `CF88:ART.32:PAR.4` | DEVICE | Art. 32, § 4º — Forças de segurança do Distrito Federal | 168 | 1375 |
| `CF88:ART.33` | OVERVIEW | Art. 33 — Territórios Federais | 228 | 2200 |
| `CF88:ART.33:PAR.3` | DEVICE | Art. 33, § 3º — Territórios com mais de cem mil habitantes | 195 | 1673 |
| `CF88:ART.34` | OVERVIEW | Art. 34 — Intervenção federal: regra e exceção | 272 | 2082 |
| `CF88:ART.34:INC.I` | BLOCK | Art. 34, incisos I, II e III — Unidade nacional e ordem pública | 169 | 1564 |
| `CF88:ART.34:INC.IV` | ITEM | Art. 34, inciso IV — Livre exercício dos Poderes estaduais | 158 | 1417 |
| `CF88:ART.34:INC.V` | BLOCK | Art. 34, inciso V — Reorganização das finanças | 224 | 1718 |
| `CF88:ART.34:INC.VI` | ITEM | Art. 34, inciso VI — Execução de lei federal e de decisões judiciais | 183 | 1494 |
| `CF88:ART.34:INC.VII` | BLOCK | Art. 34, inciso VII — Princípios constitucionais sensíveis | 237 | 1981 |
| `CF88:ART.35` | OVERVIEW | Art. 35 — Intervenção nos Municípios | 225 | 1705 |
| `CF88:ART.35:INC.I` | BLOCK | Art. 35, incisos I, II e III — Falhas graves de gestão municipal | 246 | 1962 |
| `CF88:ART.35:INC.IV` | ITEM | Art. 35, inciso IV — Representação ao Tribunal de Justiça | 177 | 1528 |
| `CF88:ART.36` | OVERVIEW | Art. 36 — Procedimento da intervenção | 213 | 1558 |
| `CF88:ART.36:INC.I` | BLOCK | Art. 36, incisos I, II e III — Quem provoca a intervenção | 330 | 3079 |
| `CF88:ART.36:PAR.1` | BLOCK | Art. 36, §§ 1º e 2º — Decreto e controle pelo Legislativo | 219 | 1800 |
| `CF88:ART.36:PAR.3` | DEVICE | Art. 36, § 3º — Decreto limitado à suspensão do ato | 191 | 1547 |
| `CF88:ART.36:PAR.4` | DEVICE | Art. 36, § 4º — Fim da intervenção | 125 | 1102 |

Texto integral de cada explicação, com caixas APROVAR / AJUSTAR / REJEITAR: `REVIEW_BATCH_04.md`.

## 5. CAMADA EXTERNA (external notes)

- `CF88:ART.25`: A extensão em que a Constituição estadual deve reproduzir modelos da Constituição Federal (o chamado princípio da simetria) é tema de interpretação constitucional tratado na camada externa.
- `CF88:ART.25:PAR.3`: A forma de gestão compartilhada entre Estado e Municípios nas regiões metropolitanas, especialmente no saneamento, é tratada na camada externa.
- `CF88:ART.27:PAR.1`: O alcance das imunidades dos Deputados Estaduais, por aplicação das regras federais, é tema de interpretação tratado na camada externa.
- `CF88:ART.28`: A data de posse em 6 de janeiro decorre da Emenda Constitucional nº 111/2021 e se aplica a partir das eleições de 2026 (nota temporal).
- `CF88:ART.29:INC.I`: Nota histórica: a remissão do texto oficial do inciso II à Emenda Constitucional nº 107/2020 refere-se ao adiamento das eleições municipais de 2020, em razão da pandemia de Covid-19. Não altera a regra permanente explicada aqui.
- `CF88:ART.29:INC.VIII`: O alcance da inviolabilidade do Vereador (nexo com o mandato e limite territorial) é tema de interpretação tratado na camada externa.
- `CF88:ART.29:INC.X`: Súmula 702 do STF (identidade confirmada em fonte oficial): a competência do Tribunal de Justiça para julgar prefeitos restringe-se aos crimes de competência da Justiça comum estadual; nos demais casos, a competência originária cabe ao respectivo tribunal de segundo grau.
- `CF88:ART.29:INC.X`: Jurisprudência do STF firmada em 2025 (HC 232627 e Inq 4787): a prerrogativa de foro para crimes praticados no cargo e em razão das funções subsiste mesmo após o afastamento do cargo. Entendimento mutável, mantido fora do texto principal.
- `CF88:ART.29:INC.XIV`: Remissão constitucional desatualizada: o antigo parágrafo único do art. 28 foi convertido no atual § 1º; o texto oficial do inciso XIV não foi atualizado.
- `CF88:ART.29-A:PAR.2`: A definição dos crimes de responsabilidade e das normas de processo e julgamento, e a competência legislativa sobre o tema, são tratadas na camada externa.
- `CF88:ART.30:INC.I`: A medida do interesse local em temas compartilhados, como meio ambiente, é tratada na camada JURISPRUDÊNCIA (recomendação registrada separadamente).
- `CF88:ART.30:INC.III`: O conjunto de tributos municipais foi alterado pela reforma tributária, com regras de transição; a situação atual dos impostos municipais é tratada na camada externa.
- `CF88:ART.31:PAR.1`: Redação atual do § 1º decorrente da Emenda Constitucional nº 139, de 05/05/2026.
- `CF88:ART.31:PAR.2`: A natureza do parecer prévio, a competência da Câmara para julgar as contas do Prefeito e a distinção entre contas de governo e contas de gestão são tratadas na camada JURISPRUDÊNCIA (recomendação registrada separadamente).
- `CF88:ART.36:INC.I`: O STF registra que a intervenção, conforme a hipótese constitucional, pode apresentar caráter vinculado ou discricionário (ADI 2167). Essa distinção não é generalizada no texto principal do ENTENDA e deve ser analisada conforme a hipótese concreta.

## 6. Recomendações de jurisprudência

Total 11: READY_TO_LINK 1 · IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION 0 · PENDING_EXTERNAL_INGESTION 8 · MATERIAL_MISMATCH_EXCLUDED 2. Nenhum vínculo foi criado; os dois MATERIAL_MISMATCH_EXCLUDED foram excluídos do export visível pelo overlay da seção 7; as demais recomendações são só para integração e revisão.

| STATUS | TARGET | REFERÊNCIA DESEJADA | OBSERVAÇÃO |
|---|---|---|---|
| MATERIAL_MISMATCH_EXCLUDED | `CF88:ART.25` | Vinculo local existente (STF Tema 113) — verificar pertinencia ao art. 25 da CF | tese local trata de: nao recepcao do art. 25 da Lei de Contravencoes Penais (Decreto-lei 3.688/1941) por violacao a dignidade e a isonomia. A tese local cita o art. 25 da Lei de Contravencoes Penais, nao o art. 25 da Constituicao; o vinculo local e um falso positivo de numeracao. |
| MATERIAL_MISMATCH_EXCLUDED | `CF88:ART.31:PAR.3` | Vinculo local existente (STF Tema 756) — verificar pertinencia ao art. 31, § 3º, da CF | tese local trata de: nao cumulatividade do PIS e da COFINS (art. 195, § 12, da CF) e constitucionalidade do § 3º do art. 31 da Lei 10.865/2004. A tese local cita o § 3º do art. 31 da Lei 10.865/2004, nao o art. 31, § 3º, da Constituicao; o vinculo local e um falso positivo de numeracao. |
| READY_TO_LINK | `CF88:ART.30:INC.I` | STF Tema 145 (Repercussao Geral) — Municipio e legislacao ambiental no limite do interesse local (art. 24, VI, c/c 30, I e II) | tese local conferida (palavras-chave ['interesse local', '30, I']); vínculo curado em `CF88:ART.24:INC.VI`; alvo correlato `CF88:ART.30:INC.I` |
| PENDING_EXTERNAL_INGESTION | `CF88:ART.31:PAR.2` | STF Tema 157 (RE 729744) — natureza opinativa do parecer previo; julgamento das contas anuais do Prefeito pela Camara | Registro nao existe no acervo local curado; nada foi fabricado. Requer ingestao oficial. |
| PENDING_EXTERNAL_INGESTION | `CF88:ART.31:PAR.2` | STF Tema 835 (RE 848826) — contas de governo e de gestao do Prefeito apreciadas pela Camara (LC 64/1990) | Registro nao existe no acervo local curado; nada foi fabricado. Requer ingestao oficial. |
| PENDING_EXTERNAL_INGESTION | `CF88:ART.29:INC.X` | STF Sumula 702 — competencia do Tribunal de Justica para julgar prefeitos restrita aos crimes da Justica comum estadual | Registro nao existe no acervo local curado; nada foi fabricado. Requer ingestao oficial. |
| PENDING_EXTERNAL_INGESTION | `CF88:ART.29:INC.X` | STF 2025 — HC 232627 e Inq 4787: prerrogativa de foro para crimes praticados no cargo e em razao das funcoes subsiste apos o afastamento | Registro nao existe no acervo local curado; nada foi fabricado. Requer ingestao oficial. |
| PENDING_EXTERNAL_INGESTION | `CF88:ART.29-A:PAR.2` | STF Sumula Vinculante 46 — competencia legislativa privativa da Uniao para definir crimes de responsabilidade e normas de processo e julgamento | Registro nao existe no acervo local curado; nada foi fabricado. Requer ingestao oficial. |
| PENDING_EXTERNAL_INGESTION | `CF88:ART.25:PAR.3` | STF — gestao compartilhada das funcoes publicas de interesse comum em regioes metropolitanas (saneamento) (candidato a confirmar em fonte oficial) | Registro nao existe no acervo local curado; nada foi fabricado. Requer ingestao oficial. |
| PENDING_EXTERNAL_INGESTION | `CF88:ART.35:INC.IV` | STF — taxatividade das hipoteses de intervencao estadual (art. 35) e natureza politico-administrativa do procedimento no Judiciario (ADI 336, ADI 7369, AI 343461 AgR) | Registro nao existe no acervo local curado; nada foi fabricado. Requer ingestao oficial. |
| PENDING_EXTERNAL_INGESTION | `CF88:ART.36:INC.I` | STF ADI 2167 — intervencao com carater vinculado ou discricionario conforme a hipotese constitucional | Registro nao existe no acervo local curado; nada foi fabricado. Requer ingestao oficial. |

## 7. Correção no Reference Engine (dois falsos positivos)

- **Fonte de verdade:** os vínculos de jurisprudência vêm do catálogo canônico `LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json` (camada `SD_JURIS_J4_6_IDS`), transformado em export pelo `reference_engine.py`.
- **Correção aplicada na fonte editorial:** novo overlay `LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json` (ligado em `engine_config.json`, chave `link_exclusions`). Cada registro retira exatamente um vínculo (`reference_id`) do export visível, com status `MATERIAL_MISMATCH_EXCLUDED`, assunto verificado, motivo e evidência (fonte oficial do STF, conferida em 2026-10-01). Fail closed: exclusão que não corresponda a exatamente um vínculo existente interrompe o build.
- O catálogo canônico **não foi editado**: os dois vínculos continuam no corpus-fonte, mas ficam fora de `references`, `REF_LOOKUP.IDX` e `REF_PAYLOAD.IDX`, e aparecem listados em `excluded_links` do JSON exportado.
- **Tema 113** antes: `CF88:ART.1:INC.III`, `CF88:ART.5:CAPUT`, `CF88:ART.25`. Excluído: `CF88:ART.25`. Depois: `CF88:ART.1:INC.III`, `CF88:ART.5:CAPUT`.
- **Tema 756** antes: `CF88:ART.195:PAR.12`, `CF88:ART.31:PAR.3`. Excluído: `CF88:ART.31:PAR.3`. Depois: `CF88:ART.195:PAR.12`.
- **Contagens:** `run1` (baseline físico) 432 vínculos exportados = 424 visíveis + 8 históricos ocultos; `run2` (export corrigido) **430** exportados = **422 visíveis** (JURISPRUDÊNCIA 277, REFERÊNCIA 101, CORRELATA 44) + 8 históricos ocultos, mais 2 em `excluded_links`; targets com vínculo 242 → 240.
- **Regressão:** o build sem o overlay reproduz o `run1` byte a byte; `run2` = `run1` menos exatamente as 2 linhas; nenhum outro vínculo, target, nota, obra ou rótulo mudou (teste `CfLinkExclusionsTest`).
- **DEVICE:** o `run1` foi mantido congelado, porque é o export copiado no SD implantado e cujo sha256 está registrado em `lex_ref_detail_data.h` (firmware). Até o próximo deploy DEVICE (overlay do SD + header do firmware, ambos proibidos nesta etapa), o aparelho físico ainda mostra as duas arestas. O `run2` é o export a implantar.
- O Batch 04 usa o `run2` (`reference_export` no `BATCH_SPEC.json`); os Batches 01–03 continuam com a configuração original.

## 8. Vigência e texto (decisões de 2026-10-01)

- `CF88:ART.28:PAR.UNICO`: HISTORICAL → excluído. `CF88:ART.36:INC.IV`: REVOKED → excluído; o bloco do art. 36, I cobre apenas II e III.
- **ART31_PAR1_SOURCE_CHANGE = EC_139_2026.** A cláusula “vedada sua extinção, criação ou instalação” do art. 31, § 1º vem da Emenda Constitucional nº 139, de 05/05/2026 (verificada em fonte oficial do Senado). O CF88_RUNTIME está correto e não foi alterado. CAMADA EXTERNA: “Redação atual do § 1º decorrente da Emenda Constitucional nº 139, de 05/05/2026.”
- **ART28_POSSE_6_JANEIRO = EC_111_2021; APLICAÇÃO = ELEIÇÕES_2026_EM_DIANTE.** O corpo do art. 28 mantém a regra vigente; nota temporal `ART28_POSSE_6_JANEIRO_EC111_2021` (efeito da mudança em 2027-01-06, revisão após 2027-01-31) e CAMADA EXTERNA curta.
- **Art. 29, XIV:** o texto oficial continua remetendo ao “art. 28, parágrafo único” (Lei Seca intacta). A ATENÇÃO e a CAMADA EXTERNA explicam que o antigo parágrafo único foi convertido no atual § 1º: remissão constitucional desatualizada decorrente da renumeração.
- **EC 107/2020 (art. 29, II):** tratada como nota histórica na CAMADA EXTERNA (adiamento das eleições municipais de 2020 pela pandemia de Covid-19); não entra como regra no texto principal.
- Nenhum dado institucional mutável no corpo; a reforma tributária (tributos municipais) ficou na CAMADA EXTERNA do art. 30, III.

## 9. Itens para a revisão humana artigo por artigo

- Rodada 1 — arts. 25 a 28: `REVIEW_BATCH_04_ROUND_1_ART25_28.md` — **APROVADA** (ver seção 12).
- Rodada 2 — arts. 29 a 31 (inclui 29-A): `REVIEW_BATCH_04_ROUND_2_ART29_31.md` — **APROVADA** (ver seção 13).
- Rodada 3 — arts. 32 a 36: `REVIEW_BATCH_04_ROUND_3_ART32_36.md` — **APROVADA** (ver seção 14).
- Pontos jurídicos da geração: **resolvidos** (EC 139/2026, EC 111/2021, art. 29, XIV, EC 107/2020, Temas 113 e 756).
- Tamanho do lote: 57 explicações (meta 35–55, teto 60), justificado na spec; não reduzido.
- Recomendações ainda pendentes de ingestão oficial (sem confirmação inventada): art. 31, § 2º; art. 29, X; art. 29-A, § 2º; art. 25, § 3º.

## 10. Possíveis dúvidas editoriais

- Art. 36, I a III: a distinção “solicitação = pedido / requisição = força de ordem” é a leitura usual, mas o grau de vinculação do Presidente em cada caso é interpretação (registrado na ATENÇÃO).
- Art. 26 (visão geral): a leitura de “incluem-se” como rol exemplificativo é interpretação razoável; confirmar o tom.
- Art. 25, § 1º: o exemplo do transporte intermunicipal como competência remanescente estadual.
- Art. 29, X: “em regra, está ligado ao exercício da função” sobre o foro do Prefeito; a delimitação foi para a camada externa.
- Art. 28, § 2º e art. 37, § 12: a menção ao modelo alternativo de teto estadual.
- Art. 27 (visão geral): exemplos numéricos do cálculo de Deputados Estaduais (8 → 24; 20 → 44).
- Art. 29-A: exemplos numéricos hipotéticos (identificados como hipotéticos no texto).
- Granularidade: art. 26 com visão geral + I + IV (ilhas na visão geral); art. 29 com 5 blocos e 2 itens; art. 30 separando competência legislativa (I, II) e administrativa (III a IX).

## 11. Integridade

- Batch 01, Batch 02, Batch 03 (pendentes e finais), corpus principal e pilotos: **byte-idênticos** (71 arquivos conferidos por sha256 antes e depois).
- Nenhum target fora de 25–36; nenhuma colisão de `explanation_id` ou de `explanation_key` com lotes anteriores; nenhum covered target órfão, coberto duas vezes ou com explicação própria; nenhum BLOCK circular; todas as âncoras são o próprio target.
- Arquivos do lote: `BATCH_SPEC.json`, `BATCH_04_DRAFTS.json` (fonte editorial), `CF88_BATCH_04.entenda.jsonl` (corpus carimbado), `SELECTION_REPORT.json`, `JURISPRUDENCE_LINK_RECOMMENDATIONS.json`, `TEMPORAL_NOTES.json`, `REVIEW_BATCH_04.md`, `REVIEW_BATCH_04_ROUND_1_ART25_28.md`, `REVIEW_BATCH_04_ROUND_2_ART29_31.md`, `REVIEW_BATCH_04_ROUND_3_ART32_36.md`, `BATCH04_TARGET_PLAN.json`, `ENTENDA_CF_BATCH04_EDITORIAL_PLAN.md`, `index/` (par ENTENDA de pré-visualização; não implantado no SD).

## 12. Round 1 (arts. 25 a 28): aprovação assistida

- **APPROVAL_METHOD = ASSISTED_RISK_BASED_HUMAN_REVIEW**; **REVIEWER_DECISION = ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW** (2026-10-01).
- 13 explicações auditadas: 7 aprovadas sem alteração e 6 aprovadas após ajustes pontuais obrigatórios, aplicados literalmente (`ROUND_1_REVIEW_SPEC.json` → `apply_batch_review.py`, modo `partial_round`).
- Rascunho anterior preservado como evidência: `BATCH_04_DRAFTS_PRE_ROUND1.json`. Decisões, textos anteriores e posteriores de cada seção: `ROUND_1_HUMAN_REVIEW_DECISIONS.json`.
- As 6 versões anteriores (editorial_version 1) permanecem no corpus como `RETIRED` (22 registros); as ajustadas passaram à versão 2.
- Ao fechar o Round 1, Rounds 2 e 3 continuavam `PENDING_HUMAN_REVIEW` e os seus arquivos de revisão não foram alterados.

| TARGET | DECISÃO | SEÇÕES AJUSTADAS | MOTIVO |
|---|---|---|---|
| `CF88:ART.25` | APPROVED_AFTER_ADJUSTMENT | exemplo_pratico | Exemplo substituido: a emenda sobre a estrutura de secretarias abria discussao desnecessaria sobre iniciativa reservada e separacao de Poderes. |
| `CF88:ART.25:PAR.1` | APPROVED | — | Aprovada sem alteracao na auditoria editorial do Round 1. |
| `CF88:ART.25:PAR.2` | APPROVED_AFTER_ADJUSTMENT | o_que_significa | A frase "depende de lei aprovada pelo Legislativo" sugeria que toda disciplina tecnica ou regulamentar do servico precisa estar em lei; o texto passa a refletir exploracao na forma da lei e a vedacao de medida provisoria. |
| `CF88:ART.25:PAR.3` | APPROVED_AFTER_ADJUSTMENT | o_que_significa | Removidas definicoes rigidas das tres figuras, que o dispositivo constitucional nao estabelece. |
| `CF88:ART.26` | APPROVED | — | Aprovada sem alteracao na auditoria editorial do Round 1. |
| `CF88:ART.26:INC.I` | APPROVED_AFTER_ADJUSTMENT | exemplo_pratico, palavras_dificeis | Exemplo e definicao de outorga ajustados: a exigencia de autorizacao depende da legislacao de recursos hidricos e das caracteristicas do uso. |
| `CF88:ART.26:INC.IV` | APPROVED_AFTER_ADJUSTMENT | o_que_significa, palavras_dificeis | Removida a explicacao historica sobre o nome; a acao discriminatoria deixa de aparecer como etapa necessaria universal. |
| `CF88:ART.27` | APPROVED | — | Aprovada sem alteracao na auditoria editorial do Round 1. |
| `CF88:ART.27:PAR.1` | APPROVED_AFTER_ADJUSTMENT | o_que_significa | A frase "valem enquanto ele exerce o mandato" podia sugerir responsabilizacao retroativa de manifestacao protegida apos o mandato. |
| `CF88:ART.27:PAR.2` | APPROVED | — | Aprovada sem alteracao na auditoria editorial do Round 1. |
| `CF88:ART.28` | APPROVED | — | Aprovada sem alteracao na auditoria editorial do Round 1. |
| `CF88:ART.28:PAR.1` | APPROVED | — | Aprovada sem alteracao na auditoria editorial do Round 1. |
| `CF88:ART.28:PAR.2` | APPROVED | — | Aprovada sem alteracao na auditoria editorial do Round 1. |

- Limpeza posterior do art. 26, IV (**EDITORIAL_CLEANUP_NO_SEMANTIC_CHANGE**, `ART26_IV_CLEANUP_REVIEW_SPEC.json` → `ART26_IV_CLEANUP_DECISIONS.json`): o verbete *Ação discriminatória*, que deixou de aparecer no texto, foi removido de PALAVRAS DIFÍCEIS; versão 3, com a versão 2 mantida como `RETIRED`. O aviso `TERM_NOT_USED` foi resolvido.

## 13. Round 2 (arts. 29, 29-A, 30 e 31): aprovação assistida

- **APPROVAL_METHOD = ASSISTED_RISK_BASED_HUMAN_REVIEW**; **REVIEWER_DECISION = ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW** (2026-10-01). Auditoria com texto constitucional vigente, fontes oficiais e STF.
- 24 explicações auditadas: 18 aprovadas sem alteração e 6 aprovadas após ajustes pontuais aplicados literalmente (`ROUND_2_REVIEW_SPEC.json`); 0 decisões do Arthur necessárias.
- Evidência: `BATCH_04_DRAFTS_PRE_ROUND2.json` → `BATCH_04_DRAFTS_ART26_IV_CLEANUP.json` → `BATCH_04_DRAFTS.json`; decisões e textos anteriores em `ROUND_2_HUMAN_REVIEW_DECISIONS.json`; as versões anteriores das 6 ajustadas ficam `RETIRED`.
- **Verificações oficiais registradas** (sem ingestão local inventada): Súmula 702 e jurisprudência de 2025 sobre o foro (HC 232627, Inq 4787) só na CAMADA EXTERNA do art. 29, X; Súmula Vinculante 46 (art. 29-A, § 2º); Temas 157 (RE 729744) e 835 (RE 848826) (art. 31, § 2º); Tema 145 (RE 586224) (art. 30, I). Só o Tema 145 existe no acervo local (READY_TO_LINK); os demais ficam `PENDING_EXTERNAL_INGESTION` com `official_verification.identity_officially_verified = true`.
- Art. 31, § 1º: **EXTERNAL_VERIFICATION_RESOLVED = TRUE**; **SOURCE_CHANGE = EC_139_2026**; aprovado sem alteração, CAMADA EXTERNA mantida.
- Art. 29-A, caput: a inclusão dos subsídios dos Vereadores e dos gastos com inativos e pensionistas decorre da EC 109/2021 (confirmado); texto mantido.
- Art. 29-A, I a VI: faixas reproduzidas literalmente, incluindo a **redação literal atípica** (100.000 nos incisos I e II; “acima de 8.000.001” no inciso VI).
- Avisos de lint não bloqueantes vindos dos textos literais autorizados: `JURISPRUDENCE_WORDING_IN_BODY` (art. 29, X: “dependem da jurisprudência”) e `ABSOLUTE_CLAIM` (art. 30: “não é absoluta”, em negação).

| TARGET | DECISÃO | SEÇÕES AJUSTADAS | MOTIVO |
|---|---|---|---|
| `CF88:ART.29` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.29:INC.I` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.29:INC.IV` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.29:INC.V` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.29:INC.VIII` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.29:INC.X` | APPROVED_AFTER_ADJUSTMENT | exemplo_pratico, external_layer_notes, o_que_significa | Exemplo trocado (verbas da merenda podem atrair competencia federal) e trecho sobre o foro ajustado; Sumula 702 e jurisprudencia de 2025 (HC 232627, Inq 4787) somente na CAMADA EXTERNA. |
| `CF88:ART.29:INC.XII` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.29:INC.XIV` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.29-A` | APPROVED_AFTER_ADJUSTMENT | o_que_significa | "A Camara Municipal nao arrecada dinheiro" era absoluto demais; o restante (inclusive inativos e pensionistas no caput, redacao da EC 109/2021) foi mantido. |
| `CF88:ART.29-A:INC.I` | APPROVED_AFTER_ADJUSTMENT | atencao, o_que_diz | Faixas reproduzidas exatamente como na redacao oficial (sem suavizar fronteiras) e ATENCAO complementada sobre a redacao literal atipica. |
| `CF88:ART.29-A:PAR.1` | APPROVED_AFTER_ADJUSTMENT | o_que_significa | A frase sobre os 30% podia sugerir obrigacao de gasta-los. |
| `CF88:ART.29-A:PAR.2` | APPROVED | — | Aprovada sem alteracao. Sumula Vinculante 46 confirmada em fonte oficial (competencia legislativa privativa da Uniao para definir crimes de responsabilidade e normas de processo). |
| `CF88:ART.30` | APPROVED_AFTER_ADJUSTMENT | o_que_significa | A divisao rigida (I-II legislativos, III-IX administrativos) foi mantida como recurso de estudo, com a ressalva de que nao e absoluta. |
| `CF88:ART.30:INC.I` | APPROVED | — | Aprovada sem alteracao. Tema 145 (RE 586224) confirmado em fonte oficial. |
| `CF88:ART.30:INC.II` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.30:INC.III` | APPROVED | — | Aprovada sem alteracao. Corpo deliberadamente generico (IPTU como exemplo, taxas e contribuicoes); reforma tributaria somente na CAMADA EXTERNA. |
| `CF88:ART.30:INC.V` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.30:INC.VI` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.30:INC.VIII` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.30:INC.IX` | APPROVED_AFTER_ADJUSTMENT | exemplo_pratico | O exemplo descrevia como automatico um efeito concreto do tombamento. |
| `CF88:ART.31` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.31:PAR.1` | APPROVED | — | Aprovada sem alteracao. EXTERNAL_VERIFICATION_RESOLVED = TRUE; SOURCE_CHANGE = EC_139_2026 (redacao vigente do § 1º com "vedada sua extincao, criacao ou instalacao"); CAMADA EXTERNA mantida. |
| `CF88:ART.31:PAR.2` | APPROVED | — | Aprovada sem alteracao. Temas 157 (RE 729744) e 835 (RE 848826) confirmados em fonte oficial: parecer opinativo; julgamento das contas anuais do Prefeito pela Camara; parecer so deixa de prevalecer por 2/3 dos vereadores. |
| `CF88:ART.31:PAR.3` | APPROVED | — | Aprovada sem alteracao. |

## 14. Round 3 (arts. 32 a 36): aprovação assistida

- **APPROVAL_METHOD = ASSISTED_RISK_BASED_HUMAN_REVIEW**; **REVIEWER_DECISION = ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW** (2026-10-01). Texto constitucional vigente e pontos sensíveis conferidos em fontes oficiais.
- 20 explicações auditadas: 11 aprovadas sem alteração e 9 aprovadas após ajustes pontuais aplicados literalmente (`ROUND_3_REVIEW_SPEC.json`); 0 decisões do Arthur necessárias.
- Evidência: `BATCH_04_DRAFTS_PRE_ROUND3.json` → `BATCH_04_DRAFTS.json`; decisões e textos anteriores em `ROUND_3_HUMAN_REVIEW_DECISIONS.json`; as versões anteriores das 9 ajustadas ficam `RETIRED`.
- **Art. 33 (decisão editorial):** a informação factual sobre a inexistência atual de Territórios saiu do núcleo permanente e virou nota temporal `ART33_SITUACAO_ATUAL_TERRITORIOS` (FACTUAL_TEMPORAL_NOTE = TRUE; SOURCE = IBGE; REVIEW_ON_TERRITORIAL_CHANGE = TRUE), coerente com a decisão do Batch 03 sobre o art. 18.
- **Art. 35, IV:** verificação STF resolvida como provenance, sem alterar o texto principal: hipóteses do art. 35 taxativas, não ampliáveis nem restringíveis pelos Estados; procedimento no Judiciário de natureza político-administrativa (ADI 336, ADI 7369, AI 343461 AgR). Nenhum legitimado único nacional atribuído.
- **Art. 36, I a III (RED principal):** O QUE SIGNIFICA, ATENÇÃO e as três definições reescritos sem generalizar o grau de vinculação do chefe do Executivo; O QUE DIZ mantido; ADI 2167 na CAMADA EXTERNA (EXTERNAL_VERIFICATION_RESOLVED = TRUE).
- **Art. 36, IV:** continua REVOKED, sem explicação vigente e fora de qualquer BLOCK.
- Avisos de lint não bloqueantes: `NEAR_COPY_OF_OFFICIAL_TEXT` passou de 20 para 21 com o texto literal autorizado do art. 36, I; o termo *Intervenção federal* em PALAVRAS DIFÍCEIS do art. 34 ("suspende temporariamente a autonomia") não estava entre os ajustes autorizados e foi mantido.

| TARGET | DECISÃO | SEÇÕES AJUSTADAS | MOTIVO |
|---|---|---|---|
| `CF88:ART.32` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.32:PAR.1` | APPROVED_AFTER_ADJUSTMENT | exemplo_pratico | A classificacao do primeiro exemplo como "tema de perfil estadual" era desnecessariamente discutivel. |
| `CF88:ART.32:PAR.2` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.32:PAR.4` | APPROVED_AFTER_ADJUSTMENT | o_que_significa | A comparacao com os Estados simplificava demais o regime constitucional das forcas de seguranca estaduais. |
| `CF88:ART.33` | APPROVED_AFTER_ADJUSTMENT | atencao, o_que_significa, temporal | DECISAO EDITORIAL: informacao factual sobre a existencia atual de Territorios sai do nucleo permanente e vai para nota factual temporal (FACTUAL_TEMPORAL_NOTE = TRUE; SOURCE = IBGE; REVIEW_ON_TERRITORIAL_CHANGE = TRUE). |
| `CF88:ART.33:PAR.3` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.34` | APPROVED_AFTER_ADJUSTMENT | o_que_significa | "Intervir e suspender temporariamente essa autonomia" era amplo demais. |
| `CF88:ART.34:INC.I` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.34:INC.IV` | APPROVED_AFTER_ADJUSTMENT | palavras_dificeis | Definicao de requisicao sem afirmacao geral sobre o grau de vinculacao presidencial. |
| `CF88:ART.34:INC.V` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.34:INC.VI` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.34:INC.VII` | APPROVED_AFTER_ADJUSTMENT | o_que_significa | "A intervencao pode ser decretada" podia ser lido como afirmacao sobre discricionariedade do Presidente. |
| `CF88:ART.35` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.35:INC.I` | APPROVED_AFTER_ADJUSTMENT | atencao, exemplo_pratico | O requisito temporal de dois anos e especifico da divida fundada; exemplo e ATENCAO ajustados. |
| `CF88:ART.35:INC.IV` | APPROVED | — | Aprovada sem alteracao. Verificacao STF resolvida (provenance; texto principal inalterado): as hipoteses de intervencao estadual do art. 35 sao taxativas; os Estados nao podem amplia-las ou restringi-las; o procedimento perante o Judiciario tem natureza politico-administrativa (ADI 336, ADI 7369, AI 343461 AgR). Nenhum legitimado unico nacional foi atribuido a representacao. |
| `CF88:ART.36` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.36:INC.I` | APPROVED_AFTER_ADJUSTMENT | atencao, external_layer_notes, o_que_significa, palavras_dificeis | RED principal do Round 3: O QUE SIGNIFICA, ATENCAO e definicoes reescritos sem generalizar o grau de vinculacao; ADI 2167 na CAMADA EXTERNA (EXTERNAL_VERIFICATION_RESOLVED = TRUE). O QUE DIZ mantido. |
| `CF88:ART.36:PAR.1` | APPROVED | — | Aprovada sem alteracao. |
| `CF88:ART.36:PAR.3` | APPROVED_AFTER_ADJUSTMENT | o_que_significa | A frase contrapunha de maneira absoluta atuacao judicial e atuacao do Executivo. |
| `CF88:ART.36:PAR.4` | APPROVED | — | Aprovada sem alteracao. |
