# LEX_CONTEXT_CITATION_GUARD — relatório

**Data:** 2026-10-04.

**Base:** commit `c7424f10327a4782cfa27d3f702a051221ee7050` / tag `lex-device-v1-72-indexes-approved-2026-10-04`.

**Estado:** correção pronta no host e compilada (flag0 e flag1). Nada foi gravado:
- sem flash, firmware físico inalterado;
- SD físico inalterado;
- sem commit, tag ou push.

**Atualização (2026-10-04):** flash APP-ONLY e teste físico aprovados (`CONTEXT_CITATION_GUARD_PHYSICAL_PASS`, `PHYSICAL_HUMAN_VALIDATION = APPROVED`). Ver `CONTEXT_CITATION_GUARD_PHYSICAL_REPORT.md`.

**Escopo:** só o parser de CONTEXTO, em `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/contexto_juridico.h`, apenas dentro de `#if LEX_DEVICE_V1_ENABLED`.

**Não mudou:**
- o sketch `.ino`, byte a byte;
- ARTICLE_SEARCH.IDX, catálogo, hashes de fonte e offsets;
- TEXT_MAP;
- camadas;
- busca e scroll.

## 1. Mapa do caminho atual

| Etapa | Função | Papel |
|---|---|---|
| Leitura do número | `lerNumeroDispositivo()` (`contexto_juridico.h`) | Dígitos, milhar, sufixo `-A`, ordinal `º/ª`. **Não alterada.** |
| Parser de linha | `aplicarLinhaContextoJuridico(c, linha, inicioLinhaFisica, offset)` | Ramos ARTIGO → `§` → Parágrafo único → alínea → inciso. Só age se `inicioLinhaFisica`. |
| Linhas visuais | `recalcularContextosCache()` (`.ino`) | Aplica o parser em cada linha da tela. Linhas de continuação do wrap da TFT têm `inicioFisicoCache=false` e nunca mudam o contexto. |
| Releitura (scroll UP, pouso) | `reconstruirContextoAntesOffset()` | Relê linhas físicas desde um checkpoint, uma âncora "Art." ou a semente do TEXT_MAP. |
| Âncora | `lexLinhaEhAncoraArtigo()` | Usa o próprio parser: a linha é âncora se ele a lê como artigo. |
| Compat CF | `aplicarLinhaContextoCompatCF()` | Junta "Art." isolado com o número da linha seguinte. |
| Escolha | `escolherContextoPredominante()` | Usa a linha central (`linhaContextoAtivo`). |
| Saída | `diagnosticarContextoSeMudou()` | Imprime `CONTEXTO: ART= PAR= INC= ALINEA=`. |
| ACTIVE_TARGET / camadas | `lexV1SincronizarAlvo()` | Vem do **TEXT_MAP** pelo offset da mesma linha. Não usa a tupla do parser. |

## 2. Causa exata

**Função:** `aplicarLinhaContextoJuridico()`, ramo "PARAGRAFO COM §".

O TXT oficial quebra a **linha física** no hyperlink de uma remissão. Na MARIA2006, linhas 42–43:

```
Art. 1º Esta Lei cria mecanismos ... nos termos do
§ 8º do art. 226 da Constituição Federal,
```

A segunda linha é um início de linha física legítimo. O ramo `§` lia o número 8 e gravava `paragrafo="8"` sem olhar o que vem depois
do número. O texto seguinte, "do art. 226", indica que a linha cita outro dispositivo.

Não é efeito do wrap da TFT: as linhas visuais de continuação já eram ignoradas. É o início físico de uma linha que, sintaticamente,
é remissão.

A mesma falha atinge outros casos:
- `parágrafo único do art. 274`;
- `art. 47 da Lei nº 12.351` (ARTIGO falso; o ramo era case-insensitive);
- palavras que só têm letras romanas no início da linha ("civil.", "mil-réis", "D.O.U.") lidas como inciso;
- `e), ou deixar…` lido como alínea.

## 3. Correção

Toda a correção está dentro de `#if LEX_DEVICE_V1_ENABLED`. Ela reutiliza sinais estruturais já aprovados e não cria um parser novo.

**Regras:**
- **Remissão após o número** (`remissaoAposDispositivo`). Vale para `§`, Parágrafo único e Art. Logo depois do número ou de "único" vem:
  - `,` ou `;` (lista de citação; mesmo sinal de `article_index_corpus.CITATION_RE`); ou
  - uma das 16 palavras de remissão em minúsculas: `da do das dos desta deste destas destes inclusive pelo pela pelos pelas para combinado c/c`. São as `REMISSION_WORDS` do parser estrutural aprovado (`LEGAL_TARGET_ID/structure_parser.py`, modo estrito dos índices do acervo). Um teste exige igualdade entre firmware, porte Python e parser estrutural.
  - Aceita `°` ou `o` como ordinal.
- **Artigo só com `A` maiúsculo** (`article_case_sensitive` dos índices aprovados): `art. 701` no meio da frase é remissão.
- **Formato de inciso** (`incisoComFormatoEstrutural`):
  - inicial maiúscula (OCR "Il"/"Vl" continua aceito);
  - sem `.` depois do romano;
  - inicial minúscula ("lI -", OCR) só com travessão seguido de espaço ou fim de linha.
- **Alínea seguida de `,` ou `;`** é citação.

**Propriedades:**
- A decisão usa **só os bytes da própria linha**. Sem I/O, sem estado, sem linha anterior.
- Por isso o resultado é idêntico em scroll DOWN, scroll UP, pouso de busca, refill do cache, reconstrução, âncora e troca de norma.
- Nenhum scan global.

**Âncoras:** `lexLinhaEhAncoraArtigo` usa o mesmo parser. Remissões como `art. 701` deixam de ser âncoras falsas, que zeravam o contexto no scroll UP.

## 4. MARIA2006 art. 1

| | Linha 43: `§ 8º do art. 226 da Constituição Federal,` | Até o art. 2 |
|---|---|---|
| Antes (físico, serial `CONTEXTO: ART=1 PAR=8`) | `ART=1 PAR=8` | PAR=8 nas linhas seguintes do art. 1 |
| Depois (porte + modelo do leitor) | `ART=1 PAR=-` | `ART=1` em todas as linhas, até `Art. 2º` → `ART=2` |

A segunda remissão da MARIA2006 (`§ 3º do`, linha 333) também foi eliminada. As subdivisões reais da lei continuam: art. 5 parágrafo
único, art. 7 incisos, §§ 1–3, art. 12-C incisos.

## 5. Auditoria das 72 normas (antes × depois)

**Ferramenta:** `tools/context_citation_audit.py`. Ela relê todas as linhas físicas dos 72 textos que o aparelho abre (CF = `CF88_RUNTIME.txt`;
MARIA2006 = TXT reparado), com e sem o guard, mantendo o estado de linha a linha como o leitor faz.

**JSON completo:** `backups/context_citation_guard/CONTEXT_CITATION_AUDIT.json`, SHA-256 `f7bfb751…f184`.

**Oráculo de não regressão:** 15.916 offsets estruturais aprovados, formados por todos os registros dos 72 `ARTICLE_SEARCH.IDX` mais todos os registros do `CF88_TEXT_MAP.IDX`.

| Classe | Falsos contextos eliminados | Estruturais preservados (linhas aceitas) |
|---|---|---|
| `§` (PAR) | **104** | 12.045 |
| Parágrafo único | **24** | 2.471 |
| Inciso | **56** | 14.170 |
| Alínea | **1** | 3.616 |
| Artigo | **811**: 10 `Art. N da/,…` + 801 `art.` minúsculo | 12.143 |
| **Total** | **996** gatilhos falsos, em 66 das 72 normas | — |

**Verificações do oráculo:**
- registros do oráculo perdidos: **0**;
- linhas eliminadas que são registro aprovado: **0**;
- linhas que passaram a ser aceitas: **0** (o guard nunca cria contexto).

**Concordância CONTEXTO × CF88_TEXT_MAP**, em 3.387 linhas mapeadas:
- antes: 3.296;
- depois: **3.370**;
- recuperou 74 linhas do ADCT que remissões "art." quebravam;
- 0 linhas pioraram;
- as 17 restantes são a limitação conhecida de sufixo (`§ 4º-A`, `I-A`) e 1 do ADCT.

**Linhas com CONTEXTO diferente** no acervo (efeito acumulado até o próximo cabeçalho real): 22.833.

**Exemplos eliminados:**
- `§` e parágrafo único:
  - `§ 2º do art. 236` (CPC);
  - `§ 6º, todos da Constituição Federal` (CF);
  - `§ 5º deste artigo, não excluirá` (CTN);
  - `parágrafo único do art. 274` (CPC);
  - `parágrafo único pela Lei nº 13.964` (CPP).
- inciso:
  - `civil.` (Estatuto da Pessoa Idosa, LRP, CBA);
  - `mil-réis a dois contos` (CPP);
  - `dividi-los` (Terra);
  - `D.O.U. de 2.9.1981` (PNMA);
  - `III.` após "inciso" (RPS);
  - letras soltas `c`/`d`/`l` de citações de alínea;
  - células `x` de tabela (PNMA).
- alínea: `e), ou deixar de divulgá-la` (SA).
- artigo:
  - `art. 47 da Lei nº 12.351` (CF);
  - `Art. 95 da Constituição` (CE);
  - `Art. 101, I,` (CPP);
  - `(Renumerado do` / `Art. 96 para Art. 95 pelo Decreto-lei` (MINER).

**Preservados (amostra testada):**
- `§ 1º O juiz`;
- `§ 1º o trabalho terá a` (minúscula estrutural, LEP);
- `§ 4º os ex-administradores` (LIQFIN);
- `§ 1° e § 2°` (revogados, RJU);
- `Parágrafo único. a exclusão` (CTN);
- `lI -` (OCR, COND);
- `Il -`, `Vl -`, `XI -`;
- alíneas que começam por `da/do/pela/para` (CF, CPC, CLT);
- `Art. 481. Pelo contrato` e `Art. 1.358-O. condomínio` (CC).

**Casos ambíguos (não alterados, registrados):** 68.

| Tipo | Quantidade | Forma | Por que não é decidível pela própria linha |
|---|---|---|---|
| `§ N` sem continuação | 61 | Linha só com `§ 1` e o resto na linha seguinte ("…disposto no" / `§ 1` / `º deste artigo`); CPP 17, LRF 12, RPS 12… | `§ 3º` / "O período…" (RPS) e `§ 1` / "(Revogado…)" são estruturais com a **mesma** forma. Exigiria a linha anterior em todos os caminhos (scroll, pouso, âncora, reconstrução); ficou fora para não arriscar contexto stale. |
| `Art. N` maiúsculo sem continuação | 5 | CPP, CE | Mesma razão. Não são registros dos índices aprovados. |
| `parágrafo único` depois de "e" | 2 | HEDIONDOS | Mesma razão. |

## 6. Caminhos do leitor (modelo `scroll_model` com o porte corrigido)

| Item | Resultado |
|---|---|
| Wrap visual | A linha visual `§ 8º do art. 226…` é início físico; "termos do" é continuação. Todas as linhas desde a ativa ficam `ART=1`. Parágrafo real com wrap mantém PAR nas continuações. |
| Scroll DOWN | Mais de 100 passos pelos arts. 1–12 da MARIA2006, com refills. Em cada passo, os contextos das 12 linhas são iguais ao parse completo desde o offset 0. Sem PAR=8. |
| Scroll UP | 60 passos depois do DOWN e 60 depois de pouso distante (art. 12, reconstrução por âncora). Iguais ao parse completo. |
| Pouso por busca | Arts. 1, 5, 7, 10, 12, 14, 24, 38, 40 e 46: a linha ativa mostra o artigo buscado; leitor antigo e novo concordam. |
| Troca de norma | CF 193 → MARIA 1 → CC 2000 → MARIA 1: cada abertura começa vazia; MARIA depois do CC = MARIA depois da CF. Nenhum stale. |
| ACTIVE_TARGET | CF 5, 37, 40, 193 e 230: alvo, camada 4, ENTENDA, juris e correlatas idênticos com e sem o guard. Sai do TEXT_MAP, e o `.ino` não mudou. |
| CONTEXTO × ACTIVE_TARGET na CF | Pousos em 37, 40 e 193 mais 40 passos de scroll: a tupla da linha ativa = TEXT_MAP (fora as limitações conhecidas de sufixo, CAPUT e ADCT). |
| CF art. 37 § 6 | `ART=37 PAR=6` mantido. |
| CF art. 40 | §§ 1, 2, 3, 4 e 6 presentes. |
| CC | Única eliminação: um `c` solto. 539 `§` preservados. |
| CPC | Só remissões "§ N do art." eliminadas. 1.275 `§` preservados. |

## 7. Performance

**Custo por linha:**
- só roda numa linha que já casou um marcador (`§`, Parágrafo único, Art, alínea, romano);
- lê no máximo 11 bytes depois do número e faz até 16 `strcmp` de no máximo 10 bytes;
- zero I/O, zero alocação, zero estado.

**Estimativa no ESP32-S3:** menos de 2 µs por linha marcada. Por redesenho, até 12 linhas.

Para comparação, a serial mediu `PERF CONTEXTO_ATUALIZAR` em cerca de 600 µs na MARIA2006.

**Releitura:** nenhuma. A fonte do caminho de releitura, âncora e cache (`.ino`) é byte-idêntica à da tag; os testes de scroll e o I/O
do modelo continuam os mesmos.

**Medição física:** pendente, no teste físico (comparar `PERF CONTEXTO_ATUALIZAR`).

## 8. Testes

**Novo:** `tests/test_context_citation_guard.py`, 26 testes, cobrindo os itens 1–15 da missão:
- MARIA2006 art. 1 §8 CF;
- `§`, inciso e alínea em texto corrido;
- `§` estrutural, Parágrafo único, inciso e alínea estruturais;
- wrap visual;
- scroll UP e DOWN, pouso, troca de norma;
- ACTIVE_TARGET e camadas;
- contrato de fonte: flag0 idêntico, `.ino` intacto, sem I/O no guard, palavras = parser aprovado, tabela de autoteste do firmware = porte;
- corpus: oráculo com 0 perdas, CF TEXT_MAP sem piora, CC/CPC preservados.

**Ajustados:**
- `tools/context_parser_port.py` ganhou `CITATION_GUARD` (padrão `True`, o build DEVICE V1; `False` reproduz o bug).
- `test_thousands_parser.test_remissions_keep_their_own_number`: a intenção foi mantida ("nunca 12858"). Sem o guard a linha é lida como art. 2; com o guard, como remissão.
- `test_batch04_run3_consolidation`:
  - a regra de milhar é comparada pela função `lerNumeroDispositivo`, não pelo SHA do header inteiro;
  - o header entra na lista de arquivos alterados em relação à fonte r2.

| Suíte | Resultado |
|---|---|
| DEVICE | **353/353** (327 + 26 novos), 0 skip |
| ENTENDA | 97/97 |
| LEGAL_TARGET_ID | 65/65 |
| RUN3 / Batch04 (`test_batch04_run3_consolidation`) | 25/25 |
| Full corpus indexes | 17/17 |
| MARIA2006 | 9/9 |
| Article search (indexed / landing / next occurrence / REPEAT_READY) | 20/20, 18/18, 16/16, 16/16 |
| Thousands | 19/19 |
| Scroll bidirecional | 25/25 |
| FD policy (`test_a3b_prep2`, na suíte DEVICE) | PASS |
| Updater | 113/116; 3 ERROR ambientais (`ModuleNotFoundError: truststore`), os mesmos de antes |

**FAIL_REAL = 0.**

## 9. Build

Ambiente: arduino-cli 1.5.1 (Arduino IDE), `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`.

**Fontes:**
- `contexto_juridico.h`: `d3dd321be292bf7e5823459f998b9b28c4291e1db426395e4467b7fb793374bc`;
- `.ino`: `7bb99e88c902109a84f6f98cf48cdc7a398c036cd6c7497945b969387d17cfd0`, inalterado.

| Build | Programa | RAM estática | Imagem `.bin` | SHA-256 | Delta vs baseline |
|---|---|---|---|---|---|
| flag1 (novo) | 1.099.791 B | 126.148 B | 1.099.936 B | `03df230ec132c0526b94c1f13eaa841c7d6ae1bc64a7330e8239d975ae38f495` | +1.596 B programa (guard + tabela de autoteste); RAM +0; imagem +1.600 B |
| flag1 baseline (aprovado) | 1.098.195 B | 126.148 B | 1.098.336 B | `2dc52259…cc6acc` | — |
| flag0 (novo) | 989.395 B | 124.452 B | 989.536 B | `6818b9b95aa5307d2d04a5f7153e67fecc4df6e3f348cc86abfc6c38bcdf62bb` | **0** programa / RAM / imagem |
| flag0 baseline | 989.395 B | 124.452 B | 989.536 B | `33ab41a6…10e9` | — |

**Por que o SHA do flag0 muda:** a fonte do baseline e a nova foram compiladas no mesmo diretório (`same_path.log`). As duas imagens flag0
diferem só em 67 bytes, todos metadados de build:
- SHA do ELF em `esp_app_desc` (offsets 176–207);
- `__TIME__` (offsets 12.640–12.644);
- hash final da imagem.

O código do flag0 é idêntico, como também prova o teste `strip_v1` do header.

**Imagens arquivadas** (fora do Git): `backups/context_citation_guard/flag1/` e `flag0/`.

## 10. Teste físico sugerido

Flash do flag1 `03df230e…f495`, **somente com aprovação de Arthur**. Depois:
- **Boot:**
  - `TESTE CONTEXTO JURIDICO: OK` (inclui os 22 casos novos do autoteste);
  - DIAG PASS 33/0.
- **MARIA2006:**
  - abrir e rolar o art. 1: serial sem `PAR=8`;
  - art. 5 → parágrafo único;
  - art. 7 → incisos;
  - art. 12-C → incisos.
- **CF:**
  - art. 37 → `§ 6`;
  - art. 40 → §§;
  - ACTIVE_TARGET e camadas como antes.
- **CC e CPC:** um artigo com parágrafos em cada.
- **Troca:** CF → MARIA → CC → MARIA.
- **Performance:** `PERF CONTEXTO_ATUALIZAR` no mesmo nível (cerca de 600 µs).

## 11. Limitação registrada

`KNOWN_LIMITATION_CONTEXTO_REMISSAO.md`:
- o caso do art. 1 da MARIA2006 está corrigido nesta candidata, pendente de teste físico;
- ficam 68 casos ambíguos, em que o marcador aparece sozinho na linha e a remissão continua só na linha seguinte.
