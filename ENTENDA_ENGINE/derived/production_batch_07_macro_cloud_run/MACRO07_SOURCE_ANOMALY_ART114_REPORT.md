# MACRO07 — Anomalia de fonte: art. 114, incisos VII e VIII

Missão MACRO07_SECOND_PASS_RISK_COMPRESSION_AND_SOURCE_SANITY · branch `cf-macro-76-175-cloud` · data de referência 2026-10-05.
**Nenhuma linha de Lei Seca foi editada à mão.** A correção vem de uma correção de transcrição já aprovada e versionada. Ela é verificada contra a fonte canônica versionada.

## Sintoma

No ENTENDA (`NormContext`, texto operacional do Senado), o texto do inciso VIII aparecia colado ao inciso VII. O status também marcava `CF88:ART.114:INC.VIII` como `HISTORICAL_ONLY`. Por isso, a visão geral do art. 114 precisava de uma "Observação estrutural" na camada externa. O problema estava registrado como backlog MB07-01.

## Comparação das camadas

| Camada | O que traz | Situação |
|---|---|---|
| Fonte do Senado: `updater/fontes_oficiais_senado/CF88/16434817_5beff7a4/raw.html` (sha256 `5beff7a4…`) | `VII I - a execução, de ofício…` (espaço espúrio dentro do numeral) | **origem do defeito** |
| Normalização: `normalizado.txt` (sha256 `d2f681e0…`), linha 1755 | `VII I - a execução, de ofício…` (reproduz a fonte fielmente) | correta em relação à fonte |
| Texto operacional: `updater/saida/…/constituicao_federal_1988.txt` (git-ignored, sha256 `3100e097…`, reconstruído byte a byte pela receita) | cabeçalho + `normalizado.txt` | correto em relação à fonte |
| Segmentação: `structure_parser.parse_structure` | `VII I` não é rótulo de inciso, então a linha vira continuação do VII; o VIII não existe | **manifestação** |
| Índice de targets: `CF88_TARGET_INDEX.json` (do `cf.txt` canônico) | `CF88:ART.114:INC.VIII` existe (linha 3450: `VIII a execução, de ofício…`) | correto |
| Status: `CF88_TARGET_STATUS.json` (congelado, sha256 `5b88efeb…`) | VIII `HISTORICAL_ONLY` ("ausente do texto operacional vigente") | **manifestação** |
| Runtime do DEVICE: `updater/exportar_cf88_runtime.py::apply_source_corrections` | já aplicava a correção aprovada | correto |
| Apresentação: ENTENDA | VII com o texto do VIII; VIII sem texto | **manifestação** |

Texto esperado, conferido no `cf.txt` canônico versionado e no registro aprovado:
- VII: "as ações relativas às penalidades administrativas impostas aos empregadores pelos órgãos de fiscalização das relações de trabalho;"
- VIII: "a execução, de ofício, das contribuições sociais previstas no art. 195, I, a, e II, e seus acréscimos legais, decorrentes das sentenças que proferir;"

## Causa

**A — FONTE.** A Compilação Monovigente do Senado grafa o rótulo como `VII I`. Normalização e reconstrução preservam a fonte, como devem. A segmentação e o status apenas propagam o defeito.

A correção humana já existia no registro `updater/fontes_oficiais_senado/SOURCE_TEXT_CORRECTIONS.json`:
- id `SRC-CORR-CF88-579494-16434817-ART114-INC-VIII`;
- `APPROVED` e `reviewed`;
- tipo `SOURCE_TRANSCRIPTION_NORMALIZATION`;
- `changed_span` `VII I` → `VIII`.

Ela era aplicada só pelo exportador do DEVICE.

## Correção (camada técnica mínima)

1. `LEGAL_TARGET_ID/source_corrections.py` (novo) aplica o **mesmo registro** às linhas recebidas por `parse_structure`, em modo fail closed:
   - só aceita correções `APPROVED`, revisadas, do tipo `SOURCE_TRANSCRIPTION_NORMALIZATION` e da norma em questão;
   - a linha exata deve ocorrer 0 vezes (no-op) ou exatamente `expected_occurrences` vezes;
   - só o rótulo (`changed_span`) pode mudar, e o corpo tem de ser idêntico;
   - o corpo corrigido precisa existir no `cf.txt` canônico versionado (verificação cruzada);
   - a lista recebida não é alterada, e cada correção usada é registrada como anomalia `SOURCE_TEXT_CORRECTION`, com sha256 antes/depois.
2. `structure_parser.parse_structure(..., source_corrections=True)`. O cálculo legado do status chama com `False`, para continuar reproduzindo o arquivo congelado.
3. O status não foi reescrito, porque `CF88_TARGET_STATUS.json` é entrada fixada do manifesto do Batch06 e dos exports run1/run2/run3 do DEVICE.
   - A correção foi para `LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS_ERRATA.json`, gerada por `LEGAL_TARGET_ID/status_errata.py`.
   - A errata é reproduzível do Git: o build legado precisa reproduzir o arquivo congelado (fail closed) e cada linha diferente leva uma causa.
   - Resultado: `CF88:ART.114:INC.VIII` `HISTORICAL_ONLY` → `CURRENT`, causa `SOURCE_TEXT_CORRECTION`.
4. O builder macro (`build_entenda_macro_batch.py`) usa `ErrataNormContext`: `NormContext` mais a errata, conferida pelo sha256 da base.
   - Os módulos compartilhados com hash fixado pelo Batch06 não foram editados.

## Depois

```
CF88:ART.114:INC.VII   as ações relativas às penalidades administrativas impostas aos empregadores pelos órgãos de fiscalização das relações de trabalho;
CF88:ART.114:INC.VIII  a execução, de ofício, das contribuições sociais previstas no art. 195, I, a, e II, e seus acréscimos legais, decorrentes das sentenças que proferir;
CF88:ART.114:INC.IX    outras controvérsias decorrentes da relação de trabalho, na forma da lei.
```

- O inciso VIII agora é `CURRENT` e fica coberto pela visão geral do art. 114 (`NO_SEPARATE_EXPLANATION`).
- A "Observação estrutural" saiu da camada externa da visão geral (log do segundo passe, categoria `FONTE_SANEADA`).
- O backlog MB07-01 ficou resolvido.

## Dependentes regenerados

- O lote macro 07 foi refeito com 3 builds byte-idênticos (`DETERMINISM_EVIDENCE.json`): snapshot do art. 114, seleção, plano, corpus, índice e pacotes.
- A errata foi gerada (`python LEGAL_TARGET_ID/status_errata.py`, conferida por `--check`).

## O que não mudou (verificado)

- `raw.html`, `normalizado.txt` e o `cf.txt` canônico têm os mesmos sha256.
- O texto operacional mantém o sha256 da receita.
- `CF88_TARGET_STATUS.json` e `CF88_TARGET_INDEX.json` ficaram intactos.
- O rebuild do Batch06 é byte-idêntico e os exports congelados do DEVICE (run1/run2/run3) também.

## Testes de regressão

`LEGAL_TARGET_ID/tests/test_source_corrections.py`:
- a fonte contém o defeito;
- sem a correção, a anomalia se reproduz;
- com a correção, VII e VIII ficam separados e o IX intacto;
- a entrada não é alterada;
- a correção ausente é no-op;
- fail closed em 4 casos: não aprovada, ocorrências, mudança de corpo, sem verificação cruzada;
- outra norma fica intocada;
- a errata é reproduzível;
- o status congelado está intacto;
- a errata tem exatamente as 2 correções;
- overlay fail closed.

`ENTENDA_ENGINE/tests/test_entenda_macro_batch07.py::MacroBatch07SecondPass.test_art114_viii_separated_in_runtime`.

## Pendência registrada

MB07-09: consolidar a errata no status congelado e regenerar os exports do DEVICE, numa missão própria e com aprovação.
