# BATCH06 — REVISÃO RÁPIDA (fila C)

Lote `ENTENDA_CF_PRODUCTION_BATCH_06` · 13 itens · só o trecho com problema; nenhuma correção foi aplicada.

## `CF88:ART.43` — Art. 43 — Regiões de desenvolvimento · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** 3/4 itens de ART.43:PAR.2 reconhecidos; sem traco: ART.43:PAR.2:INC.I "igualdade de tarifas, fretes, seguros e outros ite"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.45:PAR.1` — Art. 45, § 1º — Número de deputados por Estado · risco MEDIUM · EXTERNAL

- **Trecho:** "A fonte estrutural do projeto registra a remissão "Vide Lei Complementar nº 78, de 1993"."
- **Contexto mínimo:** external_layer_notes ⟦trecho⟧ A relação com essa lei está pendente de validação no Relations Engine (evidência local pendente) e o conteúdo dela não…
- **Detector:** EXTERNAL_FACT_NEEDS_PROVENANCE
- **Motivo:** so na camada externa: o nucleo T1 nao depende do fato
- **Proposta de correção segura:** manter so a remissao registrada pela fonte; nao afirmar conteudo/estado da norma externa sem proveniencia

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.53:PAR.3` — Art. 53, §§ 3º, 4º e 5º — Sustação do processo penal contra o parlamentar · risco MEDIUM · EXTERNAL

- **Trecho:** "Antes da Emenda Constitucional nº 35, de 2001, o texto exigia licença prévia da Casa para processar o parlamentar;"
- **Contexto mínimo:** atencao ⟦trecho⟧ Crimes praticados antes da diplomação não admitem sustação.
- **Detector:** HISTORICAL_CLAIM_UNVERIFIED
- **Motivo:** afirmacao sobre redacao/regime anterior sem evidencia no plano de vigencia (conferir na fonte historica)
- **Proposta de correção segura:** retirar a afirmacao historica ou conferi-la na fonte historica (cf.txt legado versionado) e registrar proveniencia

- **Trecho:** "materiais antigos podem trazer essa regra."
- **Contexto mínimo:** atencao ⟦trecho⟧ Crimes praticados antes da diplomação não admitem sustação.
- **Detector:** HISTORICAL_CLAIM_UNVERIFIED
- **Motivo:** afirmacao sobre redacao/regime anterior sem evidencia no plano de vigencia (conferir na fonte historica)
- **Proposta de correção segura:** retirar a afirmacao historica ou conferi-la na fonte historica (cf.txt legado versionado) e registrar proveniencia

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.54:INC.I` — Art. 54, inciso I — Vedações desde a expedição do diploma · risco LOW · STRUCTURED

- **Trecho:** "Um senador pode ter conta em um banco público com contrato padrão, igual ao de qualquer cliente. Não pode, porém, assinar com esse banco um contrato de consulto"
- **Contexto mínimo:** exemplo_pratico ⟦trecho⟧ Não pode, porém, assinar com esse banco um contrato de consultoria negociado individualmente.
- **Detector:** EXCEPTION_OR_RESSALVA_DROPPED
- **Motivo:** ressalva do texto: "salvo quando o contrato obedecer a cláusulas uniformes"
- **Proposta de correção segura:** confirmar que o trecho nao generaliza a regra contra a ressalva do texto

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.55:PAR.2` — Art. 55, §§ 2º e 3º — Quem decide a perda do mandato · risco MEDIUM · EXTERNAL

- **Trecho:** "materiais anteriores podem trazer outra forma de votação."
- **Contexto mínimo:** atencao ⟦trecho⟧ A relação com a condenação criminal é tratada no inciso VI.
- **Detector:** HISTORICAL_CLAIM_UNVERIFIED
- **Motivo:** afirmacao sobre redacao/regime anterior sem evidencia no plano de vigencia (conferir na fonte historica)
- **Proposta de correção segura:** retirar a afirmacao historica ou conferi-la na fonte historica (cf.txt legado versionado) e registrar proveniencia

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.57` — Art. 57 — Funcionamento do Congresso: sessões e reuniões · risco MEDIUM · EXTERNAL

- **Lei Seca sem traço na explicação (o_que_diz):** 3/4 itens de ART.57:PAR.3 reconhecidos; sem traco: ART.57:PAR.3:INC.II "elaborar o regimento comum e regular a criação de "
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- **Trecho:** "materiais anteriores trazem outro calendário."
- **Contexto mínimo:** atencao ⟦trecho⟧ Fora desses períodos, o Congresso só se reúne mediante convocação extraordinária.
- **Detector:** HISTORICAL_CLAIM_UNVERIFIED
- **Motivo:** afirmacao sobre redacao/regime anterior sem evidencia no plano de vigencia (conferir na fonte historica)
- **Proposta de correção segura:** retirar a afirmacao historica ou conferi-la na fonte historica (cf.txt legado versionado) e registrar proveniencia

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.57:PAR.6` — Art. 57, § 6º — Convocação extraordinária do Congresso · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** ART.57:PAR.6:INC.II: 3/4 elementos reconhecidos; sem traco: "a requerimento da maioria dos membros de ambas as Casas"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.61` — Art. 61 — Iniciativa das leis · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** 4/6 itens de ART.61:PAR.1:INC.II reconhecidos; sem traco: ART.61:PAR.1:INC.II:AL.a "criação de cargos, funções ou empregos públicos na"; ART.61:PAR.1:INC.II:AL.c "servidores públicos da União e Territórios, seu re"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.61:PAR.1` — Art. 61, § 1º — Iniciativa privativa do Presidente da República · risco MEDIUM · EXTERNAL

- **Lei Seca sem traço na explicação (o_que_diz):** ART.61:PAR.1:INC.II:AL.d: 5/6 elementos reconhecidos; sem traco: "do Distrito Federal"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.62` — Art. 62 — Medidas provisórias · risco MEDIUM · EXTERNAL

- **Trecho:** "materiais anteriores descrevem um regime diferente, com reedições sucessivas."
- **Contexto mínimo:** atencao: … Medida provisória não é lei: é ato com força de lei, sujeito à conversão.
- **Detector:** HISTORICAL_CLAIM_UNVERIFIED
- **Motivo:** afirmacao sobre redacao/regime anterior sem evidencia no plano de vigencia (conferir na fonte historica)
- **Proposta de correção segura:** retirar a afirmacao historica ou conferi-la na fonte historica (cf.txt legado versionado) e registrar proveniencia

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.66:PAR.4` — Art. 66, §§ 4º, 5º e 6º — Apreciação do veto pelo Congresso · risco MEDIUM · EXTERNAL

- **Trecho:** "materiais anteriores podem trazer outra forma de votação."
- **Contexto mínimo:** atencao ⟦trecho⟧ O sobrestamento do § 6º alcança as demais proposições da sessão conjunta.
- **Detector:** HISTORICAL_CLAIM_UNVERIFIED
- **Motivo:** afirmacao sobre redacao/regime anterior sem evidencia no plano de vigencia (conferir na fonte historica)
- **Proposta de correção segura:** retirar a afirmacao historica ou conferi-la na fonte historica (cf.txt legado versionado) e registrar proveniencia

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.71` — Art. 71 — Competências do Tribunal de Contas da União · risco MEDIUM · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** 9/11 itens de ART.71:CAPUT reconhecidos; sem traco: ART.71:INC.IX "assinar prazo para que o órgão ou entidade adote a"; ART.71:INC.XI "representar ao Poder competente sobre irregularida"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.73:PAR.1` — Art. 73, § 1º — Requisitos para Ministro do Tribunal de Contas da União · risco MEDIUM · EXTERNAL

- **Trecho:** "materiais anteriores trazem limite diferente."
- **Contexto mínimo:** atencao ⟦trecho⟧ A avaliação de "notórios conhecimentos" é feita por quem indica e por quem aprova o nome.
- **Detector:** HISTORICAL_CLAIM_UNVERIFIED
- **Motivo:** afirmacao sobre redacao/regime anterior sem evidencia no plano de vigencia (conferir na fonte historica)
- **Proposta de correção segura:** retirar a afirmacao historica ou conferi-la na fonte historica (cf.txt legado versionado) e registrar proveniencia

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

