# Retomada após interrupção do Codex — 09_CATALOGO_EXPANSAO_200

Registro feito **antes de qualquer edição** nos arquivos já produzidos.
Levantamento em 2026-09-26T19:01Z. Os dados por candidata estão em `06_RELATORIOS/ESTADO_RETOMADA.json`, gerado por `06_RELATORIOS/estado_retomada.py`, script somente leitura que só escreve esse JSON.

## 1. Estado do git

- Branch `main`, HEAD `d4e816f` ("Preserva v7.12.0 validada no hardware").
- `git status --short` lista 89 entradas: 1 modificada e 88 não rastreadas.
- A pasta inteira `LEX_MACHINA_REFERENCIAS_V2/` está **não rastreada**: `git ls-files` retorna 0 arquivos. Por isso `git diff --stat` não mostra nada da missão. A única modificação rastreada aparece em `firmware/LEX_MACHINA.ino/LEX_MACHINA.ino.ino` (+951/−189).
- O firmware foi modificado em **2026-09-17 13:22 (-03)**, antes desta missão. Hash atual: `62f256e443d3ada9489fe5565744533851f14ac30c9c3c3754de26f4d01d058d`. A missão não tocou nesse arquivo.
- Nenhum arquivo do repositório fora de `09_CATALOGO_EXPANSAO_200/` foi alterado em 2026-09-26 depois das 09:30 (-03).
- A execução do Codex durou de 12:39Z a 12:52Z, pelos timestamps dos arquivos e do checkpoint.
- A mensagem de handoff falava em cerca de 73 arquivos. Na verdade o Codex deixou **333 arquivos** dentro de `09_CATALOGO_EXPANSAO_200/`.

## 2. Arquivos existentes (deixados pelo Codex)

| Pasta | Arquivos | Conteúdo |
|---|---|---|
| 00_ENTRADA | 3 | `CANDIDATAS_200.json` (200 registros, `EXP2-*` work_ids), `INSTRUCAO_USUARIO.txt`, `REFERENCIA_CATALOGO_69.json` (cópia com o sha256 do canônico) |
| 01_IDENTIDADE | 4 | `LOTE_01..04.json` (25 registros cada) |
| 02_TRIAGEM | 10 | `LOTE_01..04.json`, `CURADORIA_03.tsv`, `CURADORIA_04.tsv`, `editorial.py`, `lote01.py`, `lote02.py`, `from_table.py` |
| 03_FONTES | 217 | 100 `EXP2-*.json` (fonte selecionada, candidatas 1–100), 50 `STEAM_001..050.json`, 66 `BUSCA_55..120.json`, `collect_steam.py` |
| 04_DOSSIERS | 97 | Dossiês das 97 aptas com ressalva dos lotes 1–4 |
| 05_REJEITADAS | 0 | — |
| 06_RELATORIOS | 1 | `CHECKPOINT_LOTES.json` (lotes 1–4) |
| 07_CATALOGO_CANDIDATO | 0 | — |
| 08_MANIFEST | 1 | `INTEGRIDADE_ANTES.json` (281 hashes dos congelados da V2) |

## 3. Último lote concluído

**Lote 4 (candidatas 76–100)**, fechado às 12:51:55Z.

Os quatro lotes fechados foram conferidos contra os arquivos reais. Os 205 hashes registrados em `CHECKPOINT_LOTES.json` foram recalculados e todos conferem.

| Lote | Intervalo | APTA | APTA_COM_RESSALVA | FONTE_EM_REVISAO | Rejeitadas |
|---|---|---|---|---|---|
| 1 | 1–25 | 0 | 24 | 0 | 1 (#9 Cyberpunk 2077, REJEITADA_EVIDENCIA_FRACA) |
| 2 | 26–50 | 0 | 24 | 1 (#41 Kingdom Come: Deliverance II) | 0 |
| 3 | 51–75 | 0 | 25 | 0 | 0 |
| 4 | 76–100 | 0 | 24 | 0 | 1 (#92 The Wire, REJEITADA_DUPLICATA_EXISTENTE) |

A contagem do handoff para o lote 1 (24 APTA_COM_RESSALVA e 1 REJEITADA_EVIDENCIA_FRACA) **confere** com `02_TRIAGEM/LOTE_01.json`.

**The Wire (#92).** O catálogo de 69 contém `EXP-SER-002`, com título "A Escuta", `titulo_original` "The Wire", ano 2002 e tipo SÉRIE. A comparação normalizada por título registrou `exact_normalized=true` só para esse par. A duplicata está confirmada e o status REJEITADA_DUPLICATA_EXISTENTE fica mantido, sem gerar dossiê.

## 4. Lote parcialmente concluído

**Lote 5 (candidatas 101–125)** foi interrompido **sem checkpoint**.

- 101–120 têm apenas `03_FONTES/BUSCA_101..120.json`. São listagens brutas de busca: query, título e URL de cada resultado, **sem conteúdo da página, sem fonte selecionada e sem paráfrase**. Não existem `CURADORIA_05.tsv`, identidade, triagem nem dossiê para elas.
- 121–125 não têm nenhum arquivo.

## 5. Primeira candidata ainda não processada

**#101 — The People v. O.J. Simpson: American Crime Story** (`CAND200-101` / `EXP2-SER-011`).

A primeira candidata sem nenhum arquivo é a **#125 Carcereiros**, e antes dela a **#121 Sob Pressão**, primeira do grupo 121–125.

Plano de continuação:

1. Reaproveitar as URLs de `BUSCA_101..120` sem repetir as buscas. A fonte é escolhida nessas listagens e a página escolhida é consultada para extrair a paráfrase.
2. Processar 121–125 normalmente.
3. Fechar o lote 5.
4. Seguir com os lotes 6–8 (126–200).

## 6. Inconsistências encontradas

1. **BUSCA_51..54 ausentes.** O lote 3 está fechado, mas as buscas das candidatas 51–54 não foram salvas. As fontes selecionadas dessas candidatas existem em `03_FONTES/EXP2-FIL-001..004.json`. Não há perda de decisão, só falta o rastro da busca.
2. **Buscas sem conteúdo.** Os `BUSCA_*.json` guardam só título e URL, e os `STEAM_*.json` guardam a descrição oficial. Para os lotes 3–4, as paráfrases das TSVs não têm trecho da página salvo localmente, então a verificação depende de reabrir a URL. Por instrução ("não pesquisar novamente"), essas paráfrases **não foram reabertas**: só a integridade foi validada.
3. **Status pré-definidos em `from_table.py`.** O script traz status pré-fixados para candidatas **ainda não pesquisadas** (126–200):
   - `APTA` por padrão para n>125;
   - uma lista fixa que rebaixa algumas para APTA_COM_RESSALVA;
   - `content_type` definido por faixa numérica.

   Isso é pré-julgamento sem evidência. O script **não foi alterado**, mas **não será usado** para os lotes 5–8. As decisões desses lotes vêm de colunas explícitas por candidata, num novo driver (`02_TRIAGEM/lote_retomada.py`) que reutiliza `editorial.process` sem modificá-lo.
4. **`from_table.py` já trazia notas para candidatas futuras** (#101, #107, #110, #138, #152). Elas são tratadas como hipóteses a verificar, não como fatos. Exemplo: #138 Dirty Money reclassificado como série documental.
5. **`05_REJEITADAS/REJEICOES.json` não existe**, embora os lotes 1 e 4 tenham rejeições (#9, #92). Ele será gerado ao final a partir das triagens, sem alterar decisões.
6. **`pais_origem` = null nas 100 candidatas processadas**, com nota em `metadata_pendente`. **`titulo_ptbr` está preenchido em apenas 1** (#92). É lacuna de metadado, não erro. Ficam como pendência declarada, não inferida.
7. **Editora ou distribuidora desconhecida em #83 Pureza e #88 Tropa de Elite** (`publisher_distribuidor_editora` vazio). #88 usa fonte tier C (AdoroCinema).
8. **Uma evidence card por obra** nos lotes 1–4. Isso é compatível com o mínimo exigido (1 CENTRAL) e não é erro. Não haverá inflação retroativa.
9. **Ainda não existem** `CORRECOES_ENTRADA.json`, os relatórios de redundância e de jogos, o catálogo candidato e o `MANIFEST.json`. Serão gerados ao final.
10. **Nenhuma decisão editorial dos lotes 1–4 tem erro objetivo identificado.** Os anos originais foram separados das edições de plataforma (#2, #6, #7, #10, #12, #14), e as identidades Steam conferem com os títulos informados. **Nada nos lotes 1–4 será alterado.**
