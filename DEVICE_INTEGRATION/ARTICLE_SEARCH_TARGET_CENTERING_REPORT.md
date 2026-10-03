# ARTICLE_SEARCH — pouso do target na linha ativa (TARGET CENTERING FIX)

Status: **aprovado em testes, aguardando validação física.** Nada gravado no ESP32, nada escrito no SD, sem commit.

## Comportamento antes

- `lexV1ExecutarBuscaArtigo` → `pesquisarArtigo(n,0)` → `reiniciarIndice(pos)` + `linhaTopo=0`: o "Art. N" encontrado ficava na **linha 0 (topo)**.
- CONTEXTO e ACTIVE_TARGET são resolvidos na **linha central** (`escolherContextoPredominante`, regra principal; `lexV1SincronizarAlvo` → `CF88_TEXT_MAP.IDX`).
- Em caputs curtos, a linha central já estava no parágrafo, no inciso ou no artigo seguinte. Exemplo: no art. 193, o ACTIVE_TARGET ficava em `CF88:ART.193:PAR.UNICO`, sem camada 4.
- No baseline físico (RUN1), só **48 de 276** artigos da CF ficavam ativos logo após a busca. Os demais 228 ativavam um descendente ou o artigo seguinte:
  - ENTENDA da linha do artigo disponível de imediato: 2 de 28;
  - J/C da linha do artigo disponível de imediato: 7 de 34.

## Causa

A posição de pouso da busca (topo) e a posição de amostragem do ACTIVE_TARGET (centro) eram **diferentes**. Os dados estavam corretos e a regra ART↔CAPUT também (`REFERENCE_COVERAGE_AUDIT/ART193_DEVICE_TARGET_DIAGNOSTIC.md`).

## Posição de amostragem do ACTIVE_TARGET

- `contexto_juridico.h`: nova função **`linhaContextoAtivo(total)`**, que retorna `total/2`, a mesma expressão que antes estava inline em `escolherContextoPredominante`.
- A função passa a ser a definição **única**, usada em três lugares:
  - `escolherContextoPredominante` → `int centro=linhaContextoAtivo(total);`;
  - `lexV1SincronizarAlvo` (fallback), que antes usava `LEITOR_LINHAS_VISIVEIS/2`;
  - o pouso da busca.
- Com `LEITOR_LINHAS_VISIVEIS = 12`, a linha ativa é a **6** (7ª linha, y = 113). Esse número não está escrito em lugar nenhum: se a regra mudar, busca e ACTIVE_TARGET continuam sincronizados.

## Algoritmo novo

É só visual: a viewport é reposicionada e nada mais muda.

`lexV1PousarBuscaNaLinhaAtiva(offsetUltimaOcorrencia)`, chamado no ramo "encontrado" de `lexV1ExecutarBuscaArtigo`, antes de `desenharViewportLeitor()`:

1. Só atua no texto runtime do DEVICE V1 (`lexV1CamadaV1Aplicavel()`). Os demais arquivos mantêm o pouso no topo.
2. Consulta o registro do `CF88_TEXT_MAP.IDX` no offset real da ocorrência e o registra no log serial (`LEXV1: BUSCA_POUSO …`). O namespace nunca é deduzido do número.
3. `reiniciarIndice(ocorrencia)`, depois `indexarAntesDaJanela()` em laço até haver `alvo` linhas visuais acima. É a mesma quebra visual usada ao rolar para cima.
4. `linhaTopo = max(0, linhaOcorrencia - alvo)`. Perto do início do arquivo há clamp: a ocorrência fica na linha mais próxima possível do centro. Não há offset negativo nem leitura além do arquivo. No fim do arquivo vale o caminho já existente ("busca perto do EOF").

O que o fix **não** faz:
- não cria target fixo ("sticky");
- não altera `lexV1Alvo`, `lexV1TidRodape` nem `lexV1Disp`;
- não semeia contexto.

O ACTIVE_TARGET continua saindo do TEXT_MAP na linha ativa. Wheel, setas, PageUp e PageDown seguem o fluxo normal de `rolarLeitor`.

**Inalterados** (testes comparam o corpo de cada função com o HEAD): `pesquisarArtigo`, `executarBusca` (legado), `executarBuscaTexto`, `lexV1EntrarBusca`, `lexV1CancelarBusca` (BACK restaura a origem), `rolarLeitor`, `indexarAntesDaJanela`, `reiniciarIndice`, `avancarUmaLinhaVisual`, `lexV1ResolverAlvoKeypress` e `lexV1AtualizarDisponibilidade`. Também não mudaram dados, RUN1/RUN2/RUN3, lookup do ENTENDA, cores, fontes, rodapé, labels e teclas.

**Custo:** o primeiro desenho após o pouso reconstrói o contexto das linhas acima da ocorrência. É o mesmo caminho de rolar para cima, limitado a 256 KB pelo checkpoint/janela existentes.

## Antes × depois (simulação host do leitor, dados RUN3 candidato)

| BUSCA | ANTES (pouso no topo) | DEPOIS (pouso na linha ativa) |
|---|---|---|
| 193 | `CF88:ART.193:PAR.UNICO`, sem camada 4 | `CF88:ART.193`, CONTEXTO ART.193, **4 REF.**: Capital no Século XXI, Desigualdade para Todos, O Triunfo da Injustiça |
| 37 | `CF88:ART.37:INC.I`, sem camada 4 | `CF88:ART.37`, **4 REF.**: Os Donos do Poder, Raízes do Brasil |
| 43 | `CF88:ART.43:PAR.1:INC.I`, sem camada 4 | `CF88:ART.43`, **4 REF.**: Formação Econômica do Brasil (Vidas Secas **não**: é só de 43 §2º IV) |
| 62 | `CF88:ART.62:PAR.1:INC.I`, sem camada 4 | `CF88:ART.62`, **4 REF.**: Suzerain |
| 98 | `CF88:ART.98:INC.I` | `CF88:ART.98` centralizado, **sem** camada 4 (lacuna confirmada) |
| 202 | `CF88:ART.202:PAR.1` | `CF88:ART.202` centralizado, **sem** camada 4 (lacuna confirmada) |

Nos quatro primeiros casos o "Art. N" fica na linha 6 (por exemplo, art. 193: ocorrência 349277, topo 349179).

## Casos testados

Arquivo novo: `tests/test_article_search_landing.py`, com 18 testes. Modelo host em `tools/reader_viewport.py`, que lê as constantes do próprio firmware.

- **CAPUT com WORK_REFERENCE no RUN3: 20/20.** Arts. 2, 5, 6, 14, 37, 43, 62, 86, 134, 170, 182, 184, 192, 193, 194, 205, 220, 225, 227 e 231. Antes do fix: 5/20.
  - Para cada um, após a busca: ACTIVE_TARGET = CONTEXTO = artigo, camada 4 visível, ocorrência na linha ativa.
  - Os 10 pedidos (37, 43, 62, 170, 193, 194, 205, 220, 225, 227) estão incluídos.
- **Todos os 276 artigos da CF** (dados físicos RUN1): 276/276 ficam ativos após a busca (antes 48/276).
  - Rodapé = lista para ENTENDA, J, C e REF em todos eles.
  - ENTENDA da linha do artigo disponível de imediato: 28/28 (antes 2/28).
- **Rolagem após o art. 37** (wheel, linha a linha até o art. 38): `37.I`, `37.§1º` e `37.§6º` são alcançados. Cada descendente mostra só as obras dele (nenhuma); Os Donos do Poder e Raízes do Brasil não vazam.
- **Rolagem após o art. 193:**
  - descendo até o parágrafo único → `CF88:ART.193:PAR.UNICO` e a camada 4 some (correto);
  - voltando → `CF88:ART.193` e a camada 4 reaparece;
  - continuando até o art. 194 → só as obras do 194, nenhuma do 193;
  - cada passo move exatamente uma linha visual.
- **Ocorrência no ADCT:** pousando na ocorrência `ADCT:ART.5` (offset real), o ACTIVE_TARGET é `ADCT:ART.5`; na ocorrência da CF, é `CF88:ART.5`.
- **Clamp:** offset 0 → topo 0; último registro do TEXT_MAP → nenhuma linha além do fim do arquivo. A quebra das linhas acima do pouso é idêntica à da leitura contínua (5, 37, 193, 225).
- **Texto:** `CF88_RUNTIME.txt` inalterado (sha256 `7ef82290…2e42a`).

## Regressões

- **DEVICE 168/168:** reader state machine 10, target sync 14, layer routing 9, caput equivalence 12, RUN3 DEVICE 9 e landing 18.
- **ENTENDA 95/95.**
- **LEGAL_TARGET_ID 65/65:** Reference Engine 20 e RUN3 engine 14.
- `test_reference_run3_device.test_baseline_untouched` agora fixa o sketch aprovado pelo blob do HEAD (`f06cdc14…81ed`), porque a cópia de trabalho carrega este fix candidato.
- O teste do art. 193 do diagnóstico ficou documentado como modelo **pré-fix**.

## Build (arduino-cli 1.5.1, core esp32, ESP32S3 OPI / 4MB / default). Nada gravado.

| Build | Programa / RAM | App .bin | sha256 |
|---|---|---|---|
| flag 0 baseline (HEAD) | 989.395 B / 124.452 B | 989.536 B | `4d9ac64e…0de7` |
| flag 0 candidato | 989.395 B / 124.452 B | 989.536 B | `b9b0a746…1026` |
| flag 1 baseline (HEAD) | 1.075.603 B / 125.612 B | 1.075.744 B | `ddf93f51…1b26` |
| **flag 1 candidato** | **1.075.919 B / 125.612 B** | **1.076.064 B (+320)** | **`d6fe0f7bd4d5d60e1fedcfb8520f6b4a76f436836f27606d0920dbf2d9c48dfa`** |

- **flag 0 é funcionalmente byte-identical.** Os dois `.bin` diferem em 68 bytes, todos metadados de build:
  - `app_elf_sha256` do descritor (0xB0–0xCF);
  - a string `__TIME__` do bloco "Software Info" (20:19:07 → 20:27:09);
  - o checksum e o SHA256 da imagem (últimos 33 bytes).
  
  Código e dados são idênticos. No `.ino`, removendo as regiões `#if LEX_DEVICE_V1_ENABLED`, o texto é idêntico ao HEAD (teste). Em `contexto_juridico.h`, a única mudança é a extração de `total/2` para `linhaContextoAtivo`.
- **Candidato flag 1:** `backups/search_centering/candidate_centering_flag1/candidate_app_centering.bin` (fora do Git). Checksum e hash da imagem válidos (`esptool image_info`).
- **Fontes do candidato:** `.ino` sha256 `998cb108…c53a`, `contexto_juridico.h` sha256 `2cad3c38…8f68`.

## Validação física sugerida (não executada)

1. Buscar 193 → `CONTEXTO: ART. 193` e 4 REF. com 3 obras. No serial devem aparecer:
   - `LEXV1: BUSCA_POUSO ocorrencia=349277 TEXT_MAP=CF88:ART.193 … linha_ativa=6 linha_da_ocorrencia=6`;
   - `ACTIVE_TARGET=CF88:ART.193`.
2. Repetir com 37, 43 e 62; depois 98 e 202 (sem 4 REF.).
3. BACKSPACE com o buffer vazio durante a busca deve voltar ao ponto de origem.

Os itens com WORK_REFERENCE nova (37, 43, 62) dependem do SD com RUN3, ou seja, da consolidação Batch04 + RUN3. Com o SD físico atual (RUN1) valem 193, 194, 205, 220, 225 e 227.

## Atualização — NEXT OCCURRENCE

O ENTER repetido para a próxima ocorrência foi implementado em cima deste fix (`ARTICLE_SEARCH_NEXT_OCCURRENCE_REPORT.md`). `lexV1PousarBuscaNaLinhaAtiva` agora é chamada na primeira ocorrência e em cada ocorrência seguinte. A busca V1 passou a aceitar só ocorrências estruturais (linha `NS:ART.n` do TEXT_MAP). Landing: 18/18 e 276/276 mantidos. O candidato flag1 vigente é o combinado (`candidate_combined_flag1`).
