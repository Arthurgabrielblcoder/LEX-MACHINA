# PARTE I — Súmula 403 do STJ: tentativas por vias oficiais (2026-10-17)

```
STJ_SUMULA_403 = UNRESOLVED_EXTERNAL (mantido)
CAPTCHA_OR_CHALLENGE_BYPASSED = NO · FONTES NÃO OFICIAIS USADAS = NÃO (sem Jusbrasil, blogs ou snippets)
```

| # | Via oficial | Resultado |
|---|---|---|
| 1 | `scon.stj.jus.br/SCON/pesquisar.jsp?b=SUMU&livre=@NUM=403` (Batch08, fonte Y3) | Desafio anti-robô; não contornado |
| 2 | `www.stj.jus.br/docs_internet/VerbetesSTJ.pdf` (PDF oficial de verbetes) | O servidor respondeu com download de arquivo. O navegador mostrou a caixa "salvar" ao usuário. Nada foi baixado nem lido, e a URL não foi repetida (download exige permissão) |
| 3 | `www.stj.jus.br/publicacaoinstitucional/index.php/sumstj` | 404 NOT FOUND |
| 4 | Portal `www.stj.jus.br/sites/portalp/Inicio` → links "Súmulas", "Súmulas Anotadas" e "Súmulas por ramo" | Todos apontam para `scon.stj.jus.br/SCON/sumstj/…` |
| 5 | `scon.stj.jus.br/SCON/sumstj/` (link oficial do portal) | "Verificação automática em andamento … responda ao desafio abaixo" (innerText sha256 `bdc578d5…`). Página abandonada, sem interação |

**Conclusão.** A recomendação J0-BL do Batch08 segue UNRESOLVED_EXTERNAL.

**Caminhos legítimos que restam (dependem do usuário):**

- abrir manualmente a página do STJ e informar o enunciado e a data;
- autorizar o download do PDF oficial `VerbetesSTJ.pdf`.

Nenhum vínculo da Súmula 403 será proposto sem a fonte oficial lida.

## Atualização (2026-10-18, sprint de escala): fonte oficial resolvida

```
STJ_SUMULA403_OFFICIAL_SOURCE = RESOLVED (OFFICIAL_SOURCE_RESOLVED) · EDITORIAL_STATE = UNRESOLVED_EXTERNAL (inalterado)
CAPTCHA_OR_CHALLENGE_BYPASSED = NO · MATERIALIZADO = NÃO · BATCH08 ALTERADO = NÃO
```

| # | Via oficial | Resultado |
|---|---|---|
| 6 | Página "Súmulas do STJ", `processo.stj.jus.br/SCON/sumstj/`. Respondeu sem desafio; o rodapé do PDF indica o endereço canônico `scon.stj.jus.br/SCON/sumstj/` | A página publica o link oficial "Súmulas do STJ (PDF)" |
| 7 | `processo.stj.jus.br/SCON/getFile?url=/docs_internet/jurisprudencia/tematica/download/SU/Sumulas/SumulasSTJ.pdf` | PDF oficial "Inteiro teor das súmulas", 40.255.386 bytes, sha256 `bf92bdb1…e6e2a0`. Download feito com a autorização desta missão para "PDFs/downloads oficiais"; texto extraído com `pdftotext` |

**Súmula 403/STJ, conforme o documento oficial (p. 1366):**

- **Enunciado:** "Independe de prova do prejuízo a indenização pela publicação não autorizada de imagem de pessoa com fins econômicos ou comerciais."
- **Órgão julgador:** Segunda Seção.
- **Decisão:** 28/10/2009.
- **Fonte:** DJe 24/11/2009; RSSTJ v. 38, p. 53; RSTJ v. 216, p. 758.
- **Referências legislativas do próprio STJ:** CF/1988, art. 5º, V e X; CC/1916, art. 159; CC/2002, arts. 186 e 927.

**Registro:** `STJ_OFFICIAL_SOURCE_RESOLUTIONS.json`, que também traz a Súmula 203 (Batch10, J0-BL-093: CF art. 105, III). Índice completo: `JURISPRUDENCE_ENGINE/stj/STJ_SUMULAS_INDEX.json`.

Nenhuma ficha ou vínculo foi criado. A recomendação do Batch08 só muda com nova decisão editorial do usuário.
