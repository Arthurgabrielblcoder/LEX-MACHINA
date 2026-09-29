# HEADER_NORMALIZATION_RULE_V1

A regra está implementada em `updater/exportar_cf88_runtime.py::normalize_headers` e é aplicada à CF e ao ADCT monovigentes do Senado antes da composição do `CF88_RUNTIME.txt`. Os testes ficam em `DEVICE_INTEGRATION/tests/test_runtime_a2b.py::HeaderNormalizationTest`.

**Motivo.** O extrator oficial do pipeline (`BeautifulSoup.get_text("\n")`) quebra linhas nas fronteiras de tags HTML. Com isso, cabeçalhos de artigo chegam partidos, e o parser do firmware (`contexto_juridico.h`) só reconhece `Art` + número na mesma linha.

**Regra (puramente mecânica: nenhuma palavra é alterada, acrescentada ou removida).**

| Caso | Entrada | Condição (inequívoca) | Saída | Ocorrências |
|---|---|---|---|---|
| A | linha exatamente `Art.` + linha seguinte | a seguinte começa pelo rótulo `^\d{1,4}(º\|°\|o)?(-[A-Z])?` seguido de `.`, espaço ou fim | `Art. ` + seguinte (um espaço) | CF 276; ADCT 146 |
| B | linha exatamente `Art` + linha seguinte | a seguinte começa por `^\. <rótulo>\.\s` | `Art` + seguinte (concatenação exata, sem inserir caractere) | ADCT 2 (arts. 76-B e 101) |
| C | `<pontuação final>§ N<ordinal>` sem espaço, dentro de uma linha | `[.;:)]` seguido imediatamente de `§ ?\d{1,3}(º\|°)(-[A-Z])?\.? <Maiúscula>` | só uma quebra de linha antes do `§` | CF 1 (art. 239, § 4º, colado ao § 3º-A na fonte oficial) |

**Fail closed.**
- `Art.` ou `Art` isolado que não satisfaça a condição faz o export falhar (`HEADER_NORMALIZATION_UNSAFE`).
- Depois da normalização não pode restar nenhuma linha `Art.` ou `Art`.

**Nunca tocado.** Linhas que começam com `art.` minúsculo são citações quebradas em hyperlinks, no meio da frase (`…a que se refere o` / `art. 2º da Lei nº 12.858…`). Elas permanecem como vieram da fonte; o índice usa o parser aprovado em modo estrito (`article_case_sensitive=True`) para não tratá-las como cabeçalho. Remissões a parágrafo precedidas de espaço (`o § 3º`) nunca são separadas.

**Versão.** O nome `HEADER_NORMALIZATION_RULE_V1` fica gravado no `CF88_RUNTIME.provenance.json`, no cabeçalho do `CF88_TEXT_MAP.IDX` (`#NORMALIZATION_VERSION`) e no manifest. Qualquer mudança exige uma nova versão.
