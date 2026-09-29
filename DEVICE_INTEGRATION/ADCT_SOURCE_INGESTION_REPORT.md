# ADCT_SOURCE_INGESTION_REPORT (V1-A2B, 2026-09-29)

**Decisão humana:** o ADCT entra no pipeline oficial do updater como fonte canônica própria, pela mesma via da CF.

## Fontes oficiais ingeridas

| | CF | ADCT |
|---|---|---|
| Órgão / portal | Senado Federal, `legis.senado.leg.br` | Senado Federal, `legis.senado.leg.br` |
| Norma | 579494, Constituição da República Federativa do Brasil | 604119, Ato das Disposições Constitucionais Transitórias |
| Compilação | Monovigente (publicação 16434817) | Monovigente (publicação 16434816) |
| Aquisição (UTC) | 2026-09-29T16:37:48Z | 2026-09-29T16:37:50Z |
| Resposta bruta | 1.001.554 B, sha256 `5beff7a47d7723594a6c48b5a72a99bbe13b300c91f4befce2284ae7f3b86808` | 370.650 B, sha256 `2e7bf19d595106fdd83f6ddc13ed9dd2a8f3561c4d2e2b34bc036d50d70b03ee` |
| Normalizado (extrator do pipeline) | 429.241 B, sha256 `d2f681e014c68ab3cbd4758eaacc4cbf0bb22d20d4737945e25f4409abd07be2` | 157.892 B, sha256 `887617267a648cccd36128323db07c2659194326c1e85020f1ddfd636067006a` |
| Validação forte (`_validar_especial_mestre`) | aprovada (276 cabeçalhos, art. final 250) | aprovada (âncoras 1, 2, 10, 18-A, 34, 54-A, 60, 76, 76-B, 92-B, 107, 111-A, 120, 124, 130, 138; frases recentes da reforma tributária) |
| Outra publicação "Monovigente" listada | 37890870 (não usada; a primeira passou) | 37890881, rejeitada: título jurídico não localizado |

**Onde ficam os arquivos.**
- Pasta: `updater/fontes_oficiais_senado/<ID>/<publicação>_<sha8>/`, com `raw.html`, `normalizado.txt` e `metadata.json`. O `metadata.json` guarda URLs, norma, tipo de compilação, aquisição, os dois sha256 e o blob git do parser e do ingestor.
- Trava: `updater/fontes_oficiais_senado/SOURCES_LOCK.json`. O exportador lê **somente** o que está travado ali.

**Código.**
- `updater/main.py`: nova entrada `FONTES_ESPECIAIS_MESTRE['ADCT']`, com validação equivalente à da CF. A entrada não entra no catálogo mestre, então a execução normal do updater não muda.
- `updater/ingerir_fontes_oficiais_senado.py`: reaproveita, sem downloader paralelo, as funções já existentes do pipeline:
  - `_resolver_publicacoes_monovigentes`;
  - `_requisitar_com_retry`;
  - `_extrair_corpo_senado`;
  - `_validar_especial_mestre`.

## Comparação estrutural (parser aprovado; o runtime usa o modo estrito)

| Fonte | Bytes | Linhas | EOL | Artigos | Parágrafos (+ únicos) | Incisos | Alíneas | Rótulos repetidos | "Redação dada" / "Incluído pela" | Dispositivos "(Revogado)" | "Art." isolado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CF monovigente oficial | 429.241 | 3.723 | LF | 276 | 735 + 54 | 1.270 | 307 | 0 | 0 / 0 | 38 | 276 |
| ADCT monovigente oficial | 157.892 | 1.237 | LF | 148¹ | 264 + 28 | 236 | 66 | 1² | 0 / 0 | 20 | 148 |
| `cf.txt` legado | 928.009 | 8.634 | CRLF | 276 + 148 (ADCT) | 753 + 68 / 286 + 37 | 1.303 / 272 | 318 / 69 | **450** | **577 / 1.413** | 23 | 0 |
| `updater/saida` antiga | 429.832 | 3.739 | LF | 276 | 735 + 54 | 1.270 | 307 | 0 | 0 / 0 | 38 | 276 |
| **CF88_RUNTIME** | **587.133** | **4.537** | LF | 276 + 148 | 736 + 54 / 264 + 28 | 1.270 / 236 | 307 / 66 | 1² | **0 / 0** | 58 | **0** |

1. Conta obtida depois da normalização (casos A e B). Sem ela, 2 cabeçalhos quebrados como `Art` / `. N.` (arts. 76-B e 101) não são reconhecidos.
2. `ADCT:ART.134:PAR.6`: um fragmento de link (`§ 6º, todos da Constituição Federal`) começa com `§`. No mapa do runtime fica só a ocorrência canônica (`line_start`), que é a correta.

**Diferença entre CF oficial e runtime:** 735 → 736 parágrafos. É o art. 239, § 4º, colado ao § 3º-A na fonte oficial e separado pelo caso C (só uma quebra de linha).

## Conclusões

- **O cartão físico traz exatamente a CF monovigente oficial.** O `cf.txt` do cartão é igual ao `normalizado.txt` da CF mais o `\n` final, e também igual a `updater/saida/99_INDICES/CANDIDATOS_RECUPERACAO_3/CF88.txt`. Não houve mudança na CF desde 14/09.
- **Nenhuma redação histórica** no runtime: nenhuma marca "Redação dada", "Incluído pela" ou "Texto original". A única remissão editorial oficial, "(Vide Emenda…)" no ADCT art. 79, foi preservada e contada.
- **Defeito de transcrição da fonte oficial — corrigido na A2C** por correção documental auditável, com o raw.html intacto: `SRC-CORR-CF88-579494-16434817-ART114-INC-VIII` (`SOURCE_TRANSCRIPTION_NORMALIZATION`) em `updater/fontes_oficiais_senado/SOURCE_TEXT_CORRECTIONS.json`. A linha exata `VII I - a execução, de ofício…` vira `VIII - …`; a correção é validada contra a EC 45/2004 (cópia do Planalto com sha256 `76f9b562…`) e é fail closed se o hash ou o trecho mudarem. Com isso, `CF88:ART.114:INC.VIII` existe.
