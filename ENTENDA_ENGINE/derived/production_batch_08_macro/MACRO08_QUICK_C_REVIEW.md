# MACRO08 — REVISÃO RÁPIDA (fila C)

Lote `ENTENDA_CF_MACRO_BATCH_08` · 5 itens · só o trecho com problema; nenhuma correção foi aplicada.

## `CF88:ART.177` — Art. 177 — Monopólio da União sobre petróleo, gás e minérios nucleares · risco LOW · EXTERNAL

- **Lei Seca sem traço na explicação (o_que_diz):** 4/5 itens de ART.177:CAPUT reconhecidos; sem traco: ART.177:INC.II "a refinação do petróleo nacional ou estrangeiro;"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.177:PAR.4` — Art. 177, § 4º — Contribuição sobre combustíveis · risco LOW · EXTERNAL

- **Trecho:** "A alíquota pode ser diferenciada por produto ou uso e pode ser reduzida e restabelecida por ato do Poder Executivo, sem a regra do art."
- **Contexto mínimo:** o_que_diz: … O § 4º fixa requisitos para a lei que criar contribuição de intervenção no domínio econômico sobre importação ou… ⟦trecho⟧ Os recursos vão para subsídios a preços ou transporte de combustíveis, projetos ambientais ligados ao petróleo e ao…
- **Detector:** PERMISSION_NOT_IN_TEXT
- **Motivo:** LIST_ITEM_POSSIBLY_DROPPED (ao pagamento de subsídios a preços); PERMISSION_NOT_IN_TEXT (pode ser reduzida)
- **Proposta de correção segura:** nao converter a ausencia de garantia em permissao; remeter a legislacao aplicavel

- **Lei Seca sem traço na explicação (o_que_diz):** ART.177:PAR.4:INC.II:AL.a: 3/4 elementos reconhecidos; sem traco: "ao pagamento de subsídios a preços"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.182` — Art. 182 — Política de desenvolvimento urbano · risco MEDIUM · EXTERNAL

- **Lei Seca sem traço na explicação (o_que_diz):** 2/3 itens de ART.182:PAR.4 reconhecidos; sem traco: ART.182:PAR.4:INC.I "parcelamento ou edificação compulsórios;"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.194` — Art. 194 — Seguridade social · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** 5/7 itens de ART.194:PAR.UNICO reconhecidos; sem traco: ART.194:PAR.UNICO:INC.I "universalidade da cobertura e do atendimento;"; ART.194:PAR.UNICO:INC.V "eqüidade na forma de participação no custeio;"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.195:INC.I` — Art. 195, inciso I — Contribuições do empregador e da empresa · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** ART.195:INC.I:AL.a: 4/5 elementos reconhecidos; sem traco: "a qualquer título"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

