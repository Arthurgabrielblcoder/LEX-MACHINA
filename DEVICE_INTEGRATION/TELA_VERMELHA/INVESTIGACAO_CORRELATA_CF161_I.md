# Investigação independente — correlata nº 1 ausente em CF art. 161, inciso I

Registrada em 2026-10-26; auditoria somente leitura no mesmo dia. **Nada foi alterado** (firmware, ESP32, microSD, bases, índices).
O cartão físico **não foi lido**: todas as conclusões sobre o cartão vêm de manifestos e artefatos versionados.

## 1. Vínculo esperado
| Campo | Valor |
|---|---|
| Alvo | `CF88:ART.161:INC.I` |
| Decisão | C1A REPLACE `LEGACY:C1A:CORRELATA:REL_B41DCE7A7582235E@CF88:ART.161:INC.I` → registro `REL_39A8D87CD18EC477` |
| Destino | Lei Complementar 63/1990 (`EXT_LC63_1990`), **art. 3º** (salto intencional; definição de valor adicionado) |
| Rota | `ABRIR_ARTIGO_INTERNO` art. 3 → offset 1265 no texto da LC 63 |
| Fontes | `CORRELATA_COVERAGE_AUDIT/C3B2/C3B2_LC63_ROUTE_AUDIT.md` (l. 24–45); `CORRELATA_COVERAGE_AUDIT/CORRELATAS_1_CF_FROZEN.md` (l. 35) |

## 2. Aprovação física anterior
- `CORRELATA_COVERAGE_AUDIT/C3B1/C3B1_PHYSICAL_TEST_REPORT.md`, l. 13, teste 5: "LC 63 aparece e abre a partir do art. 3º". Foi reclassificado como PASS
  em `C3B1_PHYSICAL_TEST_RECLASSIFICATION.md` (decisão humana de 12/10: o art. 3º é intencional).
- C3B.2 = bytes idênticos aos do C3B.1 (6/6) → baseline aprovado: commit `74c6662`,
  tag `lex-device-v1-correlata-c3b2-physical-approved-2026-10-12`, `DEVICE_INTEGRATION/C3B2_CORRELATA_PHYSICAL_BASELINE_APPROVED.md`.

## 3. Situação no C3B.2 (`CORRELATA_COVERAGE_AUDIT/C3B2_PHYSICAL_TEST_PACKAGE/candidate/SD`)
- `99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` (`d2fcc15b…`), l. 1848: `CF88:ART.161:INC.I|INCISO|CURRENT|-C--R-`.
- `99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` (`27c67eea…`), l. 71: `CF88:ART.161:INC.I|17996|1`.
- `99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` (`1762642d…`), l. 116 (offset 17996):
  `CF88:ART.161:INC.I|CORRELATA|CURRENT_VISIBLE|CURRENT|CORRELATA:REL_39A8D87CD18EC477@CF88:ART.161:INC.I|EXT_LC63_1990|EXT_LC63_1990`.
- `99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX` (`691790f3…`), l. 15:
  `CF88|161||I||REL_39A8D87CD18EC477|EXT_LC63_1990|Lei Complementar 63/1990|ABRIR_ARTIGO_INTERNO|3|…/lc_63_1990_correlata.txt`.
- `REL_LOOKUP.IDX` (`efac06ce…`), l. 15: `CF88|161||I||2229|1`. `EXT_ARTIGOS.IDX` (`5c54face…`), l. 146: `EXT_LC63_1990|3|1265|6306`.

## 4. Implantações posteriores (manifestos `sd_manifest_post_full.json`)
| Deploy | Data | RELACOES / REL_LOOKUP / EXT_ARTIGOS | REF_PAYLOAD / REF_LOOKUP / CF88_TARGETS |
|---|---|---|---|
| C3B.2 | 12/10 | 691790f3 / efac06ce / 5c54face | 1762642d / 27c67eea / d2fcc15b |
| R2 (refs4) | 16/10 | iguais | regenerados |
| J1.2, J1.5, J2C, J2G | 16–17/10 | iguais | regenerados a cada deploy |
| J2H | 17/10 | iguais | **b16f1f81 / 2ea28d50 / fe233de1** |
| CC-J1, CC-J2 | 18–19/10 | iguais | iguais ao J2H |
| Content V2 fixtures (21/10), mass V2 CC 653 (22/10) | — | não tocados | não tocados (só `99_JURISPRUDENCIA_V2/06_NORMALIZADO`) |

O conteúdo do J2H, com cópia byte a byte em `DEVICE_INTEGRATION/staging_sd_v1_juris_j2f_b_candidate/SD` (árvore local), foi conferido por simulação no host:
- `CF88_TARGETS.IDX`, l. 1848: `-C--R-` (igual ao C3B.2).
- `REF_LOOKUP.IDX`, l. 82: `CF88:ART.161:INC.I|21196|1`. O offset 21196 aponta exatamente para a mesma linha CORRELATA `REL_39A8D87CD18EC477`.
  Os dois índices estão ordenados bytewise, sem violação (274 e 3810 linhas), compatíveis com a busca binária `lexv1Find`.
- `RELACOES.IDX` resolve `REL_39A8…` → LC 63, art. 3. `CF88_RUNTIME.txt`, `ENTENDA_*` e o texto da LC 63 não mudaram entre o C3B.2 e o CC-J2.
- **Controles positivos** pelo mesmo caminho: `CF88:ART.5:INC.XLIII` → `REL_DD3B2F9749F1A8A7` (Lei 13.260/2016); `CF88:ART.150:PAR.7` →
  `REL_839B2CF9F1A80DA2` (LC 87/1996, art. 10, além de 2 jurisprudências).

## 5. Caminhos esperados no microSD
- `/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` (flag C do rodapé "1 CORR.")
- `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` + `/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` (registro da camada 1)
- `/99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX` (item por id `REL_39A8D87CD18EC477`; também carregado no cache PSRAM)
- `/99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX` + `/99_RELATIONS_V2/03_NORMAS_EXTERNAS/EXT_LC63_1990/lc_63_1990_correlata.txt`

Hashes esperados (último estado registrado; CC-J2 = J2H nesses arquivos): CF88_TARGETS `fe233de1…`, REF_LOOKUP `2ea28d50…`,
REF_PAYLOAD `b16f1f81…`, RELACOES `691790f3…`, REL_LOOKUP `efac06ce…`, EXT_ARTIGOS `5c54face…`.

## 6. Firmware
- Caminho: `lexV1AtualizarDisponibilidade` (flag C de `CF88_TARGETS` nas query keys → "1 CORR.") → `lexV1CarregarRelacoesTarget`
  (REF_LOOKUP → REF_PAYLOAD → `lexV1ClassificarDestino` → `lexV1AdicionarCorrelataPorId`) → `lexV1LinhaLegadaPorId` no `RELACOES` (cache PSRAM
  ou SD) → `adicionarCorrelataV2` por artigo da rota. Logs no Serial **UART0**: `LEXV1: DISPONIBILIDADE …`, `LEXV1: LAYER_RECORDS …`,
  `LEXV1: ITEM_NAO_RESOLVIDO …`.
- Firmware de 12/10 (`74c6662`) × atual (`a7beea0b`, `40272ed`): `contexto_juridico.h`, `lex_device_v1.h` e `lex_leitor_scroll.h` **inalterados**.
  As diferenças no `.ino` são de jurisprudência (tipos, multinorma restrita a normas ≠ CF88, Turma, Content V2), da tela e do repouso.
  **Nenhuma** toca em TARGETS, REF_*, RELACOES, `lexV1AdicionarCorrelataPorId`, `adicionarCorrelataV2` ou no contexto.
- Limites: `MAX_RELACOES_ARTIGO 32`; leitura de até 64 linhas por chave no payload (161, I tem 1). A busca é binária no arquivo, sem limite de
  cache para o REF_LOOKUP. Em ordem bytewise, o 161, I fica **entre** os dois controles que passam (`ART.150…` < `ART.161…` < `ART.5…`),
  o que exclui truncamento por posição.

## 7. Hipóteses
| Hipótese | Situação |
|---|---|
| A. Vínculo ausente nos dados produzidos | **Descartada**: presente e resolvível no C3B.2 e no último pacote implantado (J2H/CC-J2). |
| B. Vínculo perdido na implantação ou no cartão | **Aberta**: os manifestos dizem que não; porém o cartão não foi lido desde 22/10 e esteve conectado ao PC durante a troca de tela (24–25/10). |
| C. Presente, mas não exibido pelo firmware | **Improvável no código** (caminho inalterado; controles passam). Uma causa de **contexto** continua possível: se o alvo ativo no momento do teste for `ART.161` (flags `E----X`) ou `ART.161:CAPUT` (`------`), o "1 CORR." não aparece. |

**Causa confirmada:** nenhuma ainda.

## 8. Próximo teste (separa B de C), na ordem
1. **Aparelho, sem gravar nada:** abrir CF art. 161 e posicionar a linha do inciso I no topo da leitura. Anotar o rótulo de contexto do
   rodapé ("ART. 161 | INC. I"?), se aparece "1 CORR." e o que a tecla 1 mostra.
   - Rótulo ≠ "INC. I" → **C (contexto/posição)**.
   - Rótulo "INC. I" e **sem** "1 CORR." → `CF88_TARGETS.IDX` do cartão diverge → **B**.
   - "1 CORR." presente e a lista vazia/sem LC 63 → REF_* ou RELACOES do cartão divergem → **B**.
   - Opcional: com o cabo na USB da UART (porta CH340 usada nos gates anteriores, não a COM5 nativa), capturar
     `LEXV1: DISPONIBILIDADE target=… corr=…` e `LEXV1: LAYER_RECORDS … correlatas=…`.
2. **Somente com autorização:** cartão no PC, **leitura** dos SHA-256 dos 6 arquivos da seção 5 comparada com os hashes esperados. Nenhuma escrita.

## 9. Proposta mínima de correção (não executada)
- Se for **B**: restaurar só os arquivos divergentes a partir do pacote J2H já aprovado
  (`staging_sd_v1_juris_j2f_b_candidate/SD/99_LEX_V1/…` e `99_RELATIONS_V2/05_INDICES_ESP32_V2/…` do C3B.2), via o deploy oficial
  pre/copy/verify, com backup e manifesto pós-deploy. Não regenerar nada.
- Se for **C** (contexto): nenhuma mudança de dados. Documentar a posição de teste correta. Se o rótulo de contexto estiver errado mesmo com o
  inciso I no topo, abrir uma auditoria separada de `contexto_juridico.h` (inalterado desde a aprovação), sem tocar nas correlatas.
