# MACRO08 — REVISÃO RÁPIDA (fila C)

Lote `ENTENDA_CF_MACRO_BATCH_08` · 15 itens · só o trecho com problema; nenhuma correção foi aplicada.

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

## `CF88:ART.212-A` — Art. 212-A — Fundeb · risco MEDIUM · EXTERNAL

- **Lei Seca sem traço na explicação (o_que_diz):** ART.212-A:PAR.1:INC.I: 3/4 elementos reconhecidos; sem traco: "ao desenvolvimento do ensino não integrantes dos fundos referidos no inciso I do caput deste artigo"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.212-A:INC.V` — Art. 212-A, inciso V — Complementação da União ao Fundeb · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** 2/3 itens de ART.212-A:INC.V reconhecidos; sem traco: ART.212-A:INC.V:AL.a "10 (dez) pontos percentuais no âmbito de cada Esta"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.225:PAR.1` — Art. 225, § 1º — Deveres ambientais do poder público · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** ART.225:PAR.1:INC.VII: 3/4 elementos reconhecidos; sem traco: "provoquem a extinção de espécies"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.227` — Art. 227 — Proteção da criança, do adolescente e do jovem · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** 6/7 itens de ART.227:PAR.3 reconhecidos; sem traco: ART.227:PAR.3:INC.I "idade mínima de quatorze anos para admissão ao tra"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.227:PAR.3` — Art. 227, § 3º — Proteção especial de crianças, adolescentes e jovens · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** ART.227:PAR.3:INC.VII: 4/5 elementos reconhecidos; sem traco: "ao jovem dependente de entorpecentes"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `CF88:ART.235` — Art. 235 — Normas para os dez primeiros anos de novo Estado · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** ART.235:INC.I: 4/5 elementos reconhecidos; sem traco: "superior a esse número"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `ADCT:ART.53` — ADCT, art. 53 — Direitos dos ex-combatentes · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** ART.53:INC.III: 4/5 elementos reconhecidos; sem traco: "de valor igual à do inciso anterior"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `ADCT:ART.60` — ADCT, art. 60 — Implantação progressiva da complementação da União ao Fundeb · risco LOW · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** 5/6 itens de ART.60:PAR.1 reconhecidos; sem traco: ART.60:PAR.1:INC.VI "10,5 (dez inteiros e cinco décimos) pontos percent"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `ADCT:ART.101` — ADCT, art. 101 — Regime especial de precatórios até 2029 · risco MEDIUM · EXTERNAL

- **Trecho:** "A anotação oficial do § 5º remete à ADI 7047 e à ADI 7064;"
- **Contexto mínimo:** external_layer_notes
- **Detector:** EXTERNAL_FACT_NEEDS_PROVENANCE
- **Motivo:** so na camada externa: o nucleo T1 nao depende do fato
- **Proposta de correção segura:** manter so a remissao registrada pela fonte; nao afirmar conteudo/estado da norma externa sem proveniencia

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

## `ADCT:ART.116` — ADCT, art. 116 — Parcelamento das dívidas dos Municípios com o INSS · risco MEDIUM · STRUCTURED

- **Lei Seca sem traço na explicação (o_que_diz):** ART.116:PAR.12:INC.III: 3/4 elementos reconhecidos; sem traco: "desde que haja manifestação de aceite por ambas as partes"
- **Detector:** LIST_ITEM_POSSIBLY_DROPPED
- **Motivo:** enumeração parafraseada sem o item/elemento indicado
- **Proposta de correção segura:** incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")

- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D

