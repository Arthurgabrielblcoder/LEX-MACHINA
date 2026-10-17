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
