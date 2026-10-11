# CF88_CORRELATA_C1A — revisão dos vínculos CORRELATA atuais (19 NEEDS_REVIEW)

**Registro de decisão humana assistida. Nada foi aplicado.** Não houve overlay, exclusão, RUN4, nem alteração no SD ou no firmware.

## Baseline e escopo

- **Branch:** `cf-correlata-coverage-audit` @ `a4b9867411db431a84c5be06c35a83639ff8909d`; origem física `device-entenda-810 @ 44ef69ba3957d9c55a6b4b5fe9f9f68fcd77efef`; Reference Engine RUN3.
- **Estado confirmado nos artefatos C0:** 44 CORRELATAs visíveis em 39 targets, de 46 no export (2 ocultas históricas).
- **Escopo:** 19 itens NEEDS_REVIEW da seção CURRENT_LINK_REVIEW, que tem 21 entradas.
  - As 2 restantes são as ocultas OBSOLETE_HIDDEN (art. 40, § 4º, II e III × LC 144/2014) e não estão no escopo.
- **Snapshot:** os 19 itens foram congelados em `snapshot_before_review` do JSON antes das decisões.
- **Fontes:** só oficiais (Planalto), verificadas em 2026-10-11. Cada fonte tem URL e sha256 do HTML baixado.

## Contabilidade

| Decisão | n |
|---|---:|
| KEEP | 0 |
| KEEP_WITH_ROUTE_FIX | 0 |
| RETARGET | 1 |
| REPLACE | 5 |
| REMOVE | 12 |
| HOLD | 1 |
| **Total** | **19** |

**Simulação (não aplicada)**

| Medida | Hoje | Após decisões, sem substitutas | Com substitutas aprovadas e com rota |
|---|---:|---:|---:|
| CORRELATAs visíveis | 44 | 27 | 34 |
| Targets visíveis | 39 | 27 | 31 |

- **Targets que ficariam sem nenhuma correlata, sem substitutas (12):** `CF88:ART.155:PAR.1:INC.III`, `CF88:ART.161:INC.I`, `CF88:ART.195:INC.II`, `CF88:ART.195:PAR.1`, `CF88:ART.195:PAR.2`, `CF88:ART.201:INC.I`, `CF88:ART.201:INC.II`, `CF88:ART.201:INC.IV`, `CF88:ART.201:INC.V`, `CF88:ART.37:PAR.3:INC.II`, `CF88:ART.43:PAR.1:INC.I`, `CF88:ART.43:PAR.1:INC.II`.
- **Mesmo com as substitutas (8):** `CF88:ART.155:PAR.1:INC.III`, `CF88:ART.195:PAR.1`, `CF88:ART.195:PAR.2`, `CF88:ART.201:INC.I`, `CF88:ART.201:INC.II`, `CF88:ART.201:INC.IV`, `CF88:ART.201:INC.V`, `CF88:ART.43:PAR.1:INC.I`.
- **Ressalva:** SIMULACAO, nao aplicada. Substitutas so contam se aprovadas e com rota de aparelho (LAI e Lei 8.212 = acervo principal; LC 63 = ja no cartao; Lei 7.990 e LCs 124/125/129 = ingestao). O retarget ART.182 -> ART.182:CAPUT nao muda a contagem.

## Decisões, uma a uma

### 1. CF art. 20, § 1 × Lei nº 9.984/2000: **REPLACE** (confiança MEDIA)

- **reference_id:** `CORRELATA:REL_0628FE08FD9A170F@CF88:ART.20:PAR.1`
- **Vínculo atual:** target `CF88:ART.20:PAR.1`, relação `REL_0628FE08FD9A170F`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_NAO_CITA_O_TARGET.
- **Fonte oficial:**
  - Lei nº 9.984/2000 (ANA): https://www.planalto.gov.br/ccivil_03/leis/l9984.htm (verificado 2026-10-11, sha256 `558ae5d3c1fc8d6c…`)
  - Lei nº 7.990/1989 (compensação financeira): https://www.planalto.gov.br/ccivil_03/leis/l7990.htm (verificado 2026-10-11, sha256 `cf0d4faceb8e9f5b…`)
- **Dispositivos relevantes:** Lei 9.984/2000: ementa (cria a ANA); art. 28 altera o art. 17 da Lei 9.648/1998 (percentual da compensação financeira por recursos hídricos) e o art. 29 altera a Lei 8.001/1990 (rateio). Lei 7.990/1989: ementa "Institui ... compensação financeira pelo resultado da exploração de petróleo ou gás natural, de recursos hídricos para fins de geração de energia elétrica, de recursos minerais..."; arts. 1º e 2º.
- **Análise:** O § 1º assegura, nos termos da lei, participação ou compensação financeira pela exploração de petróleo, gás, recursos hídricos e minerais. A Lei 9.984/2000 é a lei da ANA: só os arts. 28 e 29, que alteram outras leis, tocam a compensação hídrica, e o salto atual abre a norma sem artigo. A lei que institui e disciplina a compensação do § 1º é a Lei 7.990/1989, depois complementada pela Lei 8.001/1990. Manter a Lei 9.984 como correlata do § 1º inteiro dá destaque a uma norma de órgão, com conteúdo só reflexo.
- **Norma substituta:** Lei nº 7.990/1989 (`LEI:7990/1989`) em `CF88:ART.20:PAR.1`, REGULAMENTA. Rota: ABRIR_ARTIGO_INTERNO art. 1º (ou norma inteira). Acervo: INGESTION_REQUIRED.
- **Nota:** A Lei 8.001/1990 (percentuais e rateio) e a Lei 12.734/2012, já vinculada (royalties), complementam. A Lei 9.984 sai do target.

### 2. CF art. 37, § 3, II × Lei nº 13.460/2017: **REPLACE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_9DFE2FF258879347@CF88:ART.37:PAR.3:INC.II`
- **Vínculo atual:** target `CF88:ART.37:PAR.3:INC.II`, relação `REL_9DFE2FF258879347`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SO_DISPOSITIVO_IRMAO.
- **Fonte oficial:**
  - Lei nº 13.460/2017 (usuário de serviços públicos): https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/lei/l13460.htm (verificado 2026-10-11, sha256 `28d0650407dea4bb…`)
  - Lei nº 12.527/2011 (LAI): https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12527.htm (verificado 2026-10-11, sha256 `763c95e3090fa0bd…`)
- **Dispositivos relevantes:** Lei 13.460/2017, art. 1º, § 1º: aplica-se "nos termos do inciso I do § 3º do art. 37"; art. 2º, parágrafo único: "O acesso do usuário a informações será regido pelos termos da Lei nº 12.527". Lei 12.527/2011: ementa e art. 1º, "acesso a informações previsto no inciso XXXIII do art. 5º, no inciso II do § 3º do art. 37 e no § 2º do art. 216".
- **Análise:** O inciso II trata do acesso a registros administrativos e a informações sobre atos de governo. A própria Lei 13.460 remete essa matéria à LAI e declara apoio apenas no inciso I. A LAI regulamenta expressamente o inciso II. O vínculo atual vem do fan-out da relação do inciso I.
- **Norma substituta:** Lei nº 12.527/2011 (LAI) (`LEI:12527/2011`) em `CF88:ART.37:PAR.3:INC.II`, REGULAMENTA. Rota: norma principal LAI2011, art. 1º. Acervo: IN_MAIN_CORPUS.
- **Nota:** A rota de aparelho para norma do acervo principal ainda não existe (MAIN_CORPUS_ROUTE_REQUIRED, C0).

### 3. CF art. 37, § 3, III × Lei nº 13.460/2017: **HOLD** (confiança BAIXA)

- **reference_id:** `CORRELATA:REL_9DFE2FF258879347@CF88:ART.37:PAR.3:INC.III`
- **Vínculo atual:** target `CF88:ART.37:PAR.3:INC.III`, relação `REL_9DFE2FF258879347`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SO_DISPOSITIVO_IRMAO.
- **Fonte oficial:**
  - Lei nº 13.460/2017 (usuário de serviços públicos): https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/lei/l13460.htm (verificado 2026-10-11, sha256 `28d0650407dea4bb…`)
- **Dispositivos relevantes:** Lei 13.460/2017, art. 1º, § 1º: fundamento declarado só no inciso I. Art. 2º, V: "manifestações" incluem reclamações e denúncias sobre "a conduta de agentes públicos na prestação e fiscalização de tais serviços".
- **Análise:** O inciso III trata da disciplina da representação contra exercício negligente ou abusivo de cargo, emprego ou função. A Lei 13.460 não se declara regulamentadora do inciso III, mas o regime de manifestações e denúncias sobre a conduta de agentes cobre parte da matéria, só no âmbito da prestação de serviços. Não localizei em fonte oficial uma norma geral apontada como disciplina do inciso III. Sem essa base, nem remover nem manter é seguro.
- **Nota:** Revisão independente: decidir entre REMOVE (fan-out do inciso I) e KEEP parcial (art. 2º, V), e pesquisar a norma geral do inciso III.

### 4. CF art. 43, § 1, I × Lei Complementar nº 112/2001: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_4468A85CBDDD620A@CF88:ART.43:PAR.1:INC.I`
- **Vínculo atual:** target `CF88:ART.43:PAR.1:INC.I`, relação `REL_4468A85CBDDD620A`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_O_DISPOSITIVO_SUPERIOR.
- **Fonte oficial:**
  - Lei Complementar nº 112/2001 (RIDE Grande Teresina): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp112.htm (verificado 2026-10-11, sha256 `c8103f55daa39ec9…`)
- **Dispositivos relevantes:** LC 112/2001, ementa e art. 1º: autoriza a criação da RIDE da Grande Teresina (Piauí e Maranhão), "conforme o previsto no inciso IX do art. 21, no art. 43, e no inciso IV do art. 48".
- **Análise:** O inciso I pede a lei complementar das condições gerais de integração de regiões em desenvolvimento. A LC 112 cria uma região específica: é aplicação concreta, uma entre várias RIDEs, e não a disciplina geral. Ela não cita o § 1º nem o inciso I. O vínculo é estreito e resulta do fan-out para os dois incisos.
- **Nota:** Nenhuma substituta confirmada para o inciso I nesta rodada.

### 5. CF art. 43, § 1, II × Lei Complementar nº 112/2001: **REPLACE** (confiança MEDIA)

- **reference_id:** `CORRELATA:REL_4468A85CBDDD620A@CF88:ART.43:PAR.1:INC.II`
- **Vínculo atual:** target `CF88:ART.43:PAR.1:INC.II`, relação `REL_4468A85CBDDD620A`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_O_DISPOSITIVO_SUPERIOR.
- **Fonte oficial:**
  - Lei Complementar nº 112/2001 (RIDE Grande Teresina): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp112.htm (verificado 2026-10-11, sha256 `c8103f55daa39ec9…`)
  - Lei Complementar nº 124/2007 (SUDAM): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp124.htm (verificado 2026-10-11, sha256 `fd48b9a47de04160…`)
  - Lei Complementar nº 125/2007 (SUDENE): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp125.htm (verificado 2026-10-11, sha256 `2460f6e9635a95b4…`)
  - Lei Complementar nº 129/2009 (SUDECO): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp129.htm (verificado 2026-10-11, sha256 `138ce8b84a7d1565…`)
- **Dispositivos relevantes:** LC 124/2007: "Institui, na forma do art. 43 da Constituição Federal, a SUDAM; estabelece sua composição...". LC 125/2007: idem para a SUDENE ("estabelece sua composição"). LC 129/2009: "Institui, na forma do art. 43 da Constituição Federal, a SUDECO, estabelece sua missão institucional, natureza jurídica, objetivos, área de atuação, instrumentos de ação".
- **Análise:** O inciso II trata da composição dos organismos regionais que executam os planos regionais. As LCs 124, 125 e 129 instituem, na forma do art. 43, SUDAM, SUDENE e SUDECO: são exatamente esses organismos. As ementas das LCs 124 e 125 dizem que elas estabelecem a composição; a da LC 129 fala em estrutura e natureza. A LC 112 (uma RIDE) não fixa composição de organismo executor de plano regional nacional. Substituição confirmada pelas ementas oficiais.
- **Norma substituta:** Lei Complementar nº 124/2007 (SUDAM) (`LC:124/2007`) em `CF88:ART.43:PAR.1:INC.II`, ORGANIZA_INSTITUIÇÃO. Rota: ementa / art. 1º. Acervo: INGESTION_REQUIRED.
- **Norma substituta:** Lei Complementar nº 125/2007 (SUDENE) (`LC:125/2007`) em `CF88:ART.43:PAR.1:INC.II`, ORGANIZA_INSTITUIÇÃO. Rota: ementa / art. 1º. Acervo: INGESTION_REQUIRED.
- **Norma substituta:** Lei Complementar nº 129/2009 (SUDECO) (`LC:129/2009`) em `CF88:ART.43:PAR.1:INC.II`, ORGANIZA_INSTITUIÇÃO. Rota: ementa / art. 1º. Acervo: INGESTION_REQUIRED.
- **Nota:** Confiança média: as LCs se apoiam no art. 43 como um todo; a revisão independente pode preferir o vínculo no art. 43 ou no § 1º.

### 6. CF art. 153, § 4, II × Lei nº 11.250/2005: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_0920FF60E61E5491@CF88:ART.153:PAR.4:INC.II`
- **Vínculo atual:** target `CF88:ART.153:PAR.4:INC.II`, relação `REL_0920FF60E61E5491`, rota ABRIR_ARTIGO_INTERNO ['1'].
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SO_DISPOSITIVO_IRMAO.
- **Fonte oficial:**
  - Lei nº 11.250/2005: https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2005/lei/l11250.htm (verificado 2026-10-11, sha256 `cf6fc96bbe7ed703…`)
  - Lei nº 9.393/1996 (ITR): https://www.planalto.gov.br/ccivil_03/leis/l9393.htm (verificado 2026-10-11, sha256 `3e81e78a7d7b56d0…`)
- **Dispositivos relevantes:** Lei 11.250/2005, ementa: "Regulamenta o inciso III do § 4º do art. 153"; art. 1º trata dos convênios com os Municípios optantes.
- **Análise:** O inciso II é a não incidência sobre pequenas glebas. A Lei 11.250 regula só a opção municipal do inciso III, irmão. A disciplina das pequenas glebas está no art. 2º da Lei 9.393/1996, que já tem vínculo nesse inciso (fora do escopo C1A, avaliado PLAUSIBLE pela C0). É fan-out puro.
- **Nota:** O vínculo da Lei 11.250 no inciso III continua (PLAUSIBLE_STRONG na C0).

### 7. CF art. 153, § 4, II × Lei nº 8.981/1995: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_2C57B972486FE4AE@CF88:ART.153:PAR.4:INC.II`
- **Vínculo atual:** target `CF88:ART.153:PAR.4:INC.II`, relação `REL_2C57B972486FE4AE`, rota ABRIR_ARTIGO_INTERNO ['90', '117'].
- **Evidência C0:** NEEDS_REVIEW / DESTINO_NAO_CITA_O_TARGET.
- **Fonte oficial:**
  - Lei nº 8.981/1995: https://www.planalto.gov.br/ccivil_03/leis/l8981.htm (verificado 2026-10-11, sha256 `3f6450796771ccde…`)
- **Dispositivos relevantes:** Lei 8.981/1995: ementa "Altera a legislação tributária federal". Os artigos do salto atual são o art. 90 (prazo de pagamento do ITR no art. 14 da Lei 8.847/1994, revogada pela Lei 9.393/1996) e o art. 117 (cláusula revogatória).
- **Análise:** Nenhum dispositivo da lei trata de pequenas glebas. O art. 90 alterava o prazo de pagamento numa lei de ITR já revogada. O vínculo é temático e obsoleto.

### 8. CF art. 153, § 4, III × Lei nº 8.981/1995: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_2C57B972486FE4AE@CF88:ART.153:PAR.4:INC.III`
- **Vínculo atual:** target `CF88:ART.153:PAR.4:INC.III`, relação `REL_2C57B972486FE4AE`, rota ABRIR_ARTIGO_INTERNO ['90', '117'].
- **Evidência C0:** NEEDS_REVIEW / DESTINO_NAO_CITA_O_TARGET.
- **Fonte oficial:**
  - Lei nº 8.981/1995: https://www.planalto.gov.br/ccivil_03/leis/l8981.htm (verificado 2026-10-11, sha256 `3f6450796771ccde…`)
- **Dispositivos relevantes:** Idem: arts. 90 e 117. Não há disposição sobre fiscalização ou cobrança do ITR por Municípios optantes. O inciso III foi criado pela EC 42/2003, depois da lei.
- **Análise:** A lei é anterior ao próprio inciso III, que nasceu com a EC 42/2003, e não tem conteúdo sobre a opção municipal. É falso vínculo.

### 9. CF art. 153, § 4, III × Lei nº 9.393/1996: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_D152FF761345E231@CF88:ART.153:PAR.4:INC.III`
- **Vínculo atual:** target `CF88:ART.153:PAR.4:INC.III`, relação `REL_D152FF761345E231`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_O_DISPOSITIVO_SUPERIOR.
- **Fonte oficial:**
  - Lei nº 9.393/1996 (ITR): https://www.planalto.gov.br/ccivil_03/leis/l9393.htm (verificado 2026-10-11, sha256 `3e81e78a7d7b56d0…`)
  - Lei nº 11.250/2005: https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2005/lei/l11250.htm (verificado 2026-10-11, sha256 `cf6fc96bbe7ed703…`)
- **Dispositivos relevantes:** Lei 9.393/1996: lei do ITR. O art. 2º regula a imunidade das pequenas glebas, "nos termos do art. 153, § 4º, in fine". As menções a "município" são regras de localização do imóvel. Não há regime de opção municipal.
- **Análise:** O inciso III, opção dos Municípios para fiscalizar e cobrar, foi criado pela EC 42/2003 e é regulamentado pela Lei 11.250/2005, que já está vinculada. A Lei 9.393 serve ao inciso II, não ao III. É fan-out entre irmãos.

### 10. CF art. 155, § 1, III × Lei Complementar nº 87/1996: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_FEB2B8ACAD1A48FA@CF88:ART.155:PAR.1:INC.III`
- **Vínculo atual:** target `CF88:ART.155:PAR.1:INC.III`, relação `REL_FEB2B8ACAD1A48FA`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_NAO_CITA_O_TARGET.
- **Fonte oficial:**
  - Lei Complementar nº 87/1996 (ICMS, Lei Kandir): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp87.htm (verificado 2026-10-11, sha256 `47bb22063ba170cd…`)
  - Constituição Federal (texto compilado, com redações anteriores): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (verificado 2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** LC 87/1996, ementa: "Dispõe sobre o imposto dos Estados ... sobre operações relativas à circulação de mercadorias ... (LEI KANDIR)". Não há disposição sobre transmissão causa mortis ou doação.
- **Análise:** O § 1º do art. 155 disciplina o imposto do inciso I (ITCMD). O inciso III pede lei complementar para a competência em casos com elemento no exterior. A LC 87 é a lei do ICMS (inciso II e § 2º). Não há relação normativa: é erro de atribuição. Não confirmei substituta específica para o inciso III nesta rodada.
- **Nota:** A LC 87/1996 continua vinculada ao art. 155, § 2º, XII (fora do escopo C1A).

### 11. CF art. 161, I × Lei Complementar nº 62/1989: **REPLACE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_B41DCE7A7582235E@CF88:ART.161:INC.I`
- **Vínculo atual:** target `CF88:ART.161:INC.I`, relação `REL_B41DCE7A7582235E`, rota ABRIR_ARTIGO_INTERNO ['1'].
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SO_DISPOSITIVO_IRMAO.
- **Fonte oficial:**
  - Lei Complementar nº 62/1989 (FPE/FPM): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp62.htm (verificado 2026-10-11, sha256 `a0970c8be6abcb36…`)
  - Lei Complementar nº 63/1990 (parcelas municipais; valor adicionado): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp63.htm (verificado 2026-10-11, sha256 `da8f7f7a27a50d58…`)
- **Dispositivos relevantes:** LC 62/1989, art. 1º: regula FPE e FPM, "consoante o disposto nos incisos II e III do art. 161". LC 63/1990, art. 3º, § 1º: "O valor adicionado corresponderá, para cada Município, ..." (conceito do art. 158, § 1º, I).
- **Análise:** O inciso I manda a lei complementar definir valor adicionado para o art. 158, § 1º, I. A LC 62 se declara apoiada só nos incisos II e III. A definição de valor adicionado está no art. 3º, § 1º, da LC 63/1990. A LC 62 continua correta nos incisos II e III.
- **Norma substituta:** Lei Complementar nº 63/1990 (`LC:63/1990`) em `CF88:ART.161:INC.I`, REGULAMENTA. Rota: ABRIR_ARTIGO_INTERNO art. 3º (EXT_LC63_1990). Acervo: EXTERNAL_ALREADY_INGESTED.
- **Nota:** A LC 63 já está no cartão (EXT_LC63_1990). Substituição sem ingestão: falta só a relação aprovada e a linha RELACOES.

### 12. CF art. 182 × Lei nº 13.425/2017: **RETARGET** (confiança MEDIA)

- **reference_id:** `CORRELATA:REL_70C4549A507F6E00@CF88:ART.182`
- **Vínculo atual:** target `CF88:ART.182`, relação `REL_70C4549A507F6E00`, rota ABRIR_ARTIGO_INTERNO ['1'].
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SUBDIVISAO_DO_TARGET.
- **Fonte oficial:**
  - Lei nº 13.425/2017 (prevenção de incêndios): https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/lei/l13425.htm (verificado 2026-10-11, sha256 `f02a9ce52170c0e1…`)
  - Lei nº 10.257/2001 (Estatuto da Cidade): https://www.planalto.gov.br/ccivil_03/leis/leis_2001/l10257.htm (verificado 2026-10-11, sha256 `ef4562c4c1a136f9…`)
- **Dispositivos relevantes:** Lei 13.425/2017, art. 1º, I: estabelece diretrizes gerais sobre prevenção e combate a incêndio, "atendendo ao disposto no inciso XX do art. 21, no inciso I, in fine, do art. 24, no § 5º, in fine, do art. 144 e no caput do art. 182".
- **Análise:** A lei declara expressamente apoio no caput do art. 182, que trata de diretrizes gerais da política urbana fixadas em lei, e não nos §§ 1º a 4º (plano diretor, desapropriação, parcelamento compulsório). A relação é real, mas setorial. O target correto é o caput, não o artigo inteiro. A correlata principal do art. 182 é o Estatuto da Cidade, Lei 10.257/2001, que "Regulamenta os arts. 182 e 183". Ele já é candidato C0, fora deste escopo, e não deve ser confundido com esta revisão.
- **Target substituto:** `CF88:ART.182:CAPUT`. Rota: ABRIR_ARTIGO_INTERNO art. 1º (inalterado).
- **Nota:** Na tela, ART.182 e ART.182:CAPUT são a mesma linha (única equivalência permitida). O retarget registra a especificidade no dado.

### 13. CF art. 195, II × Lei Complementar nº 70/1991: **REPLACE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_EA8171739858C1AC@CF88:ART.195:INC.II`
- **Vínculo atual:** target `CF88:ART.195:INC.II`, relação `REL_EA8171739858C1AC`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SO_DISPOSITIVO_IRMAO.
- **Fonte oficial:**
  - Lei Complementar nº 70/1991 (COFINS): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp70.htm (verificado 2026-10-11, sha256 `63315c060d197e27…`)
  - Lei nº 8.212/1991 (custeio da seguridade): https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm (verificado 2026-10-11, sha256 `12c5bda5cffd920d…`)
- **Dispositivos relevantes:** LC 70/1991, art. 1º: institui a contribuição "nos termos do inciso I do art. 195", devida pelas pessoas jurídicas e incidente sobre o faturamento (COFINS). Lei 8.212/1991, Capítulo III ("Da Contribuição do Segurado"), arts. 20 e 21.
- **Análise:** O inciso II é a contribuição do trabalhador e dos demais segurados. A LC 70 trata da contribuição do empregador sobre o faturamento (inciso I, b) e se declara apoiada só no inciso I. A contribuição dos segurados é disciplinada pela Lei 8.212/1991, arts. 20 e seguintes.
- **Norma substituta:** Lei nº 8.212/1991 (`LEI:8212/1991`) em `CF88:ART.195:INC.II`, REGULAMENTA. Rota: norma principal CUSTEIO1991, art. 20. Acervo: IN_MAIN_CORPUS.
- **Nota:** A LC 70 continua no inciso I (PLAUSIBLE_STRONG).

### 14. CF art. 195, § 1 × Lei Complementar nº 70/1991: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_EA8171739858C1AC@CF88:ART.195:PAR.1`
- **Vínculo atual:** target `CF88:ART.195:PAR.1`, relação `REL_EA8171739858C1AC`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SO_DISPOSITIVO_IRMAO.
- **Fonte oficial:**
  - Lei Complementar nº 70/1991 (COFINS): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp70.htm (verificado 2026-10-11, sha256 `63315c060d197e27…`)
- **Dispositivos relevantes:** LC 70/1991: nenhuma disposição sobre receitas de Estados, DF e Municípios nos respectivos orçamentos.
- **Análise:** O § 1º é regra orçamentária federativa. A COFINS é tributo federal sobre faturamento, sem relação normativa com o parágrafo. É fan-out da relação do inciso I.

### 15. CF art. 195, § 2 × Lei Complementar nº 70/1991: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_EA8171739858C1AC@CF88:ART.195:PAR.2`
- **Vínculo atual:** target `CF88:ART.195:PAR.2`, relação `REL_EA8171739858C1AC`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SO_DISPOSITIVO_IRMAO.
- **Fonte oficial:**
  - Lei Complementar nº 70/1991 (COFINS): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp70.htm (verificado 2026-10-11, sha256 `63315c060d197e27…`)
- **Dispositivos relevantes:** LC 70/1991: nenhuma disposição sobre a elaboração integrada da proposta de orçamento da seguridade.
- **Análise:** O § 2º trata da proposta orçamentária integrada (saúde, previdência e assistência) e das metas da LDO, matéria orçamentária e periódica. A LC 70 não a disciplina. É fan-out.

### 16. CF art. 201, I × Lei nº 7.998/1990: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_294595B0B7254C57@CF88:ART.201:INC.I`
- **Vínculo atual:** target `CF88:ART.201:INC.I`, relação `REL_294595B0B7254C57`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SO_DISPOSITIVO_IRMAO.
- **Fonte oficial:**
  - Lei nº 7.998/1990 (seguro-desemprego/abono/FAT): https://www.planalto.gov.br/ccivil_03/leis/l7998.htm (verificado 2026-10-11, sha256 `674335b5ec1bf3ed…`)
  - Constituição Federal (texto compilado, com redações anteriores): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (verificado 2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** Lei 7.998/1990, art. 1º: regula o Programa do Seguro-Desemprego e o abono "de que tratam o inciso II do art. 7º, o inciso IV do art. 201 e o art. 239" (numeração de 1990).
- **Análise:** O inciso I trata de incapacidade temporária ou permanente e idade avançada (Lei 8.213/1991). A Lei 7.998 não trata desses eventos. É fan-out temático.

### 17. CF art. 201, II × Lei nº 7.998/1990: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_294595B0B7254C57@CF88:ART.201:INC.II`
- **Vínculo atual:** target `CF88:ART.201:INC.II`, relação `REL_294595B0B7254C57`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SO_DISPOSITIVO_IRMAO.
- **Fonte oficial:**
  - Lei nº 7.998/1990 (seguro-desemprego/abono/FAT): https://www.planalto.gov.br/ccivil_03/leis/l7998.htm (verificado 2026-10-11, sha256 `674335b5ec1bf3ed…`)
- **Dispositivos relevantes:** Lei 7.998/1990: nenhuma disposição sobre proteção à maternidade.
- **Análise:** O inciso II é a proteção à maternidade (salário-maternidade, Lei 8.213/1991). Não há relação com o seguro-desemprego. É fan-out.

### 18. CF art. 201, IV × Lei nº 7.998/1990: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_294595B0B7254C57@CF88:ART.201:INC.IV`
- **Vínculo atual:** target `CF88:ART.201:INC.IV`, relação `REL_294595B0B7254C57`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_O_TARGET.
- **Fonte oficial:**
  - Lei nº 7.998/1990 (seguro-desemprego/abono/FAT): https://www.planalto.gov.br/ccivil_03/leis/l7998.htm (verificado 2026-10-11, sha256 `674335b5ec1bf3ed…`)
  - Constituição Federal (texto compilado, com redações anteriores): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm (verificado 2026-10-11, sha256 `d22db6b86fe90c86…`)
- **Dispositivos relevantes:** CF, texto compilado: a redação original do art. 201, IV, era "proteção ao trabalhador em situação de desemprego involuntário". Após a EC 20/1998, esse conteúdo está no inciso III, e o IV passou a ser "salário-família e auxílio-reclusão para os dependentes dos segurados de baixa renda".
- **Análise:** A Lei 7.998 cita o "inciso IV do art. 201" pela numeração anterior à EC 20/1998. No texto vigente o inciso IV trata de salário-família e auxílio-reclusão, sem relação com a lei. O conteúdo citado corresponde ao inciso III, que já tem o mesmo vínculo (REL_294595B0B7254C57@CF88:ART.201:INC.III). Retargetar duplicaria o vínculo, por isso a decisão é remover.
- **Nota:** O vínculo no inciso III fica (nota positiva da C0: renumeração).

### 19. CF art. 201, V × Lei nº 7.998/1990: **REMOVE** (confiança ALTA)

- **reference_id:** `CORRELATA:REL_294595B0B7254C57@CF88:ART.201:INC.V`
- **Vínculo atual:** target `CF88:ART.201:INC.V`, relação `REL_294595B0B7254C57`, rota ABRIR_NORMA_SEM_SALTO .
- **Evidência C0:** NEEDS_REVIEW / DESTINO_CITA_SO_DISPOSITIVO_IRMAO.
- **Fonte oficial:**
  - Lei nº 7.998/1990 (seguro-desemprego/abono/FAT): https://www.planalto.gov.br/ccivil_03/leis/l7998.htm (verificado 2026-10-11, sha256 `674335b5ec1bf3ed…`)
- **Dispositivos relevantes:** Lei 7.998/1990: nenhuma disposição sobre pensão por morte.
- **Análise:** O inciso V é a pensão por morte (Lei 8.213/1991). A Lei 7.998 não a disciplina. É fan-out.

## Fora do escopo desta rodada

Os itens que a missão lembrou como atenção especial e que NÃO estão entre os 19 NEEDS_REVIEW da C0 não foram revisados nem decididos aqui, por regra de escopo:
- art. 214, I a VI × Lei 15.388/2026 (PLAUSIBLE_NOT_VERIFIED);
- art. 161, II e III × LC 62/1989 (PLAUSIBLE_STRONG);
- art. 195, I × LC 70/1991 (PLAUSIBLE_STRONG);
- art. 201, III × Lei 7.998/1990 (nota positiva de renumeração);
- art. 153, § 4º, II × Lei 9.393/1996 e III × Lei 11.250/2005 (PLAUSIBLE);
- art. 155, § 2º, XII × LC 87/1996 (sem inconsistência evidente).
Ficam para C1B.

## Próximo passo

- **Revisão jurídica independente:** confirmar estas decisões.
  - Em especial o HOLD do art. 37, § 3º, III e as substituições de confiança média (art. 20, § 1º; art. 43, § 1º, II).
- **Só depois:** registrar as remoções em `CF88_LINK_EXCLUSIONS.json` e as substituições e o retarget no overlay futuro `CF88_CORRELATA_ADDITIONS.json`, numa missão de aplicação com RUN4 candidato.

