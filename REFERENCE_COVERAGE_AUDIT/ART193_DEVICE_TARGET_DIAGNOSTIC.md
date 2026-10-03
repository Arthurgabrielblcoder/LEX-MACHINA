# ART. 193 — diagnóstico do ACTIVE_TARGET no DEVICE (somente diagnóstico)

**Firmware, UI, algoritmo ACTIVE_TARGET e SD físico NÃO foram alterados.** Simulação host do leitor aprovado sobre os bytes do baseline físico.

## Fontes simuladas

- Sketch `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino` sha256 `f06cdc14ad066e2575fe03552eb0090f39c77ab350d095de7bf26d41c86a81ed` (baseline aprovado: `f06cdc14…81ed`).
- `contexto_juridico.h` sha256 `6d05430a2844098d344ad6a5ce84f64804b39b5223647a821c1f3ced49da8006`.
- SD baseline `DEVICE_INTEGRATION/staging_sd_v1/SD/99_LEX_V1`: `CF88_RUNTIME.txt` 587133 B sha256 `7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a`; `CF88_TEXT_MAP.IDX` sha256 `889f82002e82fb2b7d9165e6ce2a4e0dcb78d311432e268c341f1d0b1e436b96`.
- Quebra visual: `avancarUmaLinhaVisual()` com os avanços reais da fonte Arimo (148 glifos lidos do sketch), largura 312 px; viewport 12 linhas de 15 px; linha do CONTEXTO = linha central `6` (7ª linha, y=113) (`escolherContextoPredominante`, regra principal).

## 1–4. Offsets e estrutura

| ITEM | OFFSET | LINHA FÍSICA | TARGET (TEXT_MAP) |
|---|---|---|---|
| line_start Art. 193 (caput) | 349277 | 2840 | `CF88:ART.193` |
| Parágrafo único | 349389 | 2841 | `CF88:ART.193:PAR.UNICO` |
| Início do Art. 194 | 349699 | 2846 | `CF88:ART.194` |

- Byte range do caput: **[349277, 349389)** = 112 bytes → **3 linhas visuais**.
- Parágrafo único + cabeçalhos até o art. 194: [349389, 349699) = 310 bytes → **9 linhas visuais** (os cabeçalhos "CAPÍTULO II / Da Seguridade Social / SEÇÃO I / Disposições Gerais" não têm linha própria no TEXT_MAP e resolvem, por piso, para `CF88:ART.193:PAR.UNICO`).
- Dados: `CF88:ART.193` flags `------`; `CF88:ART.193:CAPUT` flags `---WR-`; `CF88:ART.193:PAR.UNICO` flags `------`. Com ACTIVE_TARGET = `CF88:ART.193`, as chaves `CF88:ART.193+CF88:ART.193:CAPUT` dão botão 4 = **True** com 3 obras: Capital no Século XXI, Desigualdade para Todos, O Triunfo da Injustiça.

## 5–6. Viewport logo após "Buscar Art. 193"

`pesquisarArtigo("193")` acha a linha em offset **349277** (= line_start do caput: True); `reiniciarIndice(pos)` + `linhaTopo=0` colocam o "Art. 193" na **linha 0 (topo)**.

| LINHA | y | OFFSET | TARGET DA LINHA | TEXTO |
|---|---|---|---|---|
| 0 | 23 | 349277 | `CF88:ART.193` | Art. 193. A ordem social tem como base o primado do |
| 1 | 38 | 349329 | `CF88:ART.193` | trabalho, e como objetivo o bem-estar e a justiça |
| 2 | 53 | 349380 | `CF88:ART.193` | sociais. |
| 3 | 68 | 349389 | `CF88:ART.193:PAR.UNICO` | Parágrafo único. O Estado exercerá a função de |
| 4 | 83 | 349441 | `CF88:ART.193:PAR.UNICO` | planejamento das políticas sociais, assegurada, na |
| 5 | 98 | 349493 | `CF88:ART.193:PAR.UNICO` | forma da lei, a participação da sociedade nos |
| 6 | 113 | 349541 | `CF88:ART.193:PAR.UNICO` **← CONTEXTO / ACTIVE_TARGET** | processos de formulação, de monitoramento, de |
| 7 | 128 | 349589 | `CF88:ART.193:PAR.UNICO` | controle e de avaliação dessas políticas. |
| 8 | 143 | 349634 | `CF88:ART.193:PAR.UNICO` | CAPÍTULO II |
| 9 | 158 | 349647 | `CF88:ART.193:PAR.UNICO` | Da Seguridade Social |
| 10 | 173 | 349668 | `CF88:ART.193:PAR.UNICO` | SEÇÃO I |
| 11 | 188 | 349678 | `CF88:ART.193:PAR.UNICO` | Disposições Gerais |

- **ACTIVE_TARGET calculado: `CF88:ART.193:PAR.UNICO`** (linha 6). Chaves: `CF88:ART.193:PAR.UNICO`. Flags W: **False** → layer4 expected **NO** (0 obras).

## 7. Quais posições de rolagem resolvem o quê

Rolagem = linha visual no topo relativa ao "Art. 193" (0 = estado logo após a busca; negativo = rolar para cima).

| ROLAGEM | TOPO | LINHA CENTRAL | ACTIVE_TARGET | BOTÃO 4 (do target ativo) |
|---|---|---|---|---|
| -10 | VI - (Revogado). | TÍTULO VIII | `CF88:ART.192:PAR.3` | não |
| -9 | VII - (Revogado). | Da Ordem Social | `CF88:ART.192:PAR.3` | não |
| -8 | VIII - (Revogado). | CAPÍTULO I | `CF88:ART.192:PAR.3` | não |
| -7 | § 1º (Revogado). | Disposição Geral | `CF88:ART.192:PAR.3` | não |
| -6 | § 2º (Revogado). | Art. 193. A ordem social tem como base o | `CF88:ART.193` | **SIM — art. 193** (3 obras) |
| -5 | § 3º (Revogado). | trabalho, e como objetivo o bem-estar e  | `CF88:ART.193` | **SIM — art. 193** (3 obras) |
| -4 | TÍTULO VIII | sociais. | `CF88:ART.193` | **SIM — art. 193** (3 obras) |
| -3 | Da Ordem Social | Parágrafo único. O Estado exercerá a fun | `CF88:ART.193:PAR.UNICO` | não |
| -2 | CAPÍTULO I | planejamento das políticas sociais, asse | `CF88:ART.193:PAR.UNICO` | não |
| -1 | Disposição Geral | forma da lei, a participação da sociedad | `CF88:ART.193:PAR.UNICO` | não |
| +0 | Art. 193. A ordem social tem c | processos de formulação, de monitorament | `CF88:ART.193:PAR.UNICO` | não |
| +1 | trabalho, e como objetivo o be | controle e de avaliação dessas políticas | `CF88:ART.193:PAR.UNICO` | não |
| +2 | sociais. | CAPÍTULO II | `CF88:ART.193:PAR.UNICO` | não |
| +3 | Parágrafo único. O Estado exer | Da Seguridade Social | `CF88:ART.193:PAR.UNICO` | não |
| +4 | planejamento das políticas soc | SEÇÃO I | `CF88:ART.193:PAR.UNICO` | não |
| +5 | forma da lei, a participação d | Disposições Gerais | `CF88:ART.193:PAR.UNICO` | não |
| +6 | processos de formulação, de mo | Art. 194. A seguridade social compreende | `CF88:ART.194` | sim — outro artigo (1 obras) |
| +7 | controle e de avaliação dessas | integrado de ações de iniciativa dos pod | `CF88:ART.194` | sim — outro artigo (1 obras) |
| +8 | CAPÍTULO II | e da sociedade, destinadas a assegurar o | `CF88:ART.194` | sim — outro artigo (1 obras) |
| +9 | Da Seguridade Social | relativos à saúde, à previdência e à ass | `CF88:ART.194` | sim — outro artigo (1 obras) |
| +10 | SEÇÃO I | Parágrafo único. Compete ao poder públic | `CF88:ART.194:PAR.UNICO` | não |
| +11 | Disposições Gerais | termos da lei, organizar a seguridade so | `CF88:ART.194:PAR.UNICO` | não |
| +12 | Art. 194. A seguridade social  | nos seguintes objetivos: | `CF88:ART.194:PAR.UNICO` | não |

- Botão 4 do art. 193 aparece só nas rolagens **-6 a -4** (o caput precisa estar na linha central). Na rolagem 0 (logo após a busca) o centro já está em `CF88:ART.193:PAR.UNICO`.

## Conclusão

- **Hipótese CONFIRMADA.** O caput do art. 193 ocupa 3 linhas visuais; após a busca ele fica no topo (linhas 0–2) e a linha central (6) cai em `CF88:ART.193:PAR.UNICO`. ACTIVE_TARGET ≠ `CF88:ART.193` → as chaves não incluem `CF88:ART.193:CAPUT` → sem flag W → o rodapé não mostra 4 REF. e a tecla 4 não abre nada.
- **Por que Arthur não viu o botão:** testou logo após "Buscar Art. 193" (ou rolando sem centralizar o caput). Os dados estão corretos: as 3 obras estão em `CF88:ART.193:CAPUT` no REF_PAYLOAD e a regra ART↔CAPUT as entrega quando o ACTIVE_TARGET é `CF88:ART.193`.
- **BUG de dados/engine: NÃO.** O comportamento é o **esperado** pela regra aprovada (ACTIVE_TARGET = linha central). É, porém, uma limitação de UX: em artigos de caput curto seguido de parágrafo/incisos, o estado logo após a busca nunca ativa o próprio caput.
- **Não é exclusivo do art. 193.** No baseline físico, 8 de 11 artigos com obra no caput/linha do artigo NÃO mostram o botão 4 logo após a busca: `CF88:ART.2` (centro em `CF88:ART.3:INC.II`), `CF88:ART.6` (centro em `CF88:ART.6:PAR.UNICO`), `CF88:ART.14` (centro em `CF88:ART.14:PAR.1`), `CF88:ART.193` (centro em `CF88:ART.193:PAR.UNICO`), `CF88:ART.194` (centro em `CF88:ART.194:PAR.UNICO`), `CF88:ART.205` (centro em `CF88:ART.206`), `CF88:ART.220` (centro em `CF88:ART.220:PAR.1`), `CF88:ART.225` (centro em `CF88:ART.225:PAR.1`).
- **RUN3 candidato** (mesmo texto e TEXT_MAP): 12 de 20 artigos com obra na linha do artigo ficam sem botão 4 logo após a busca: `CF88:ART.2` (subir 4 linha(s)), `CF88:ART.6` (subir 2 linha(s)), `CF88:ART.14` (subir 4 linha(s)), `CF88:ART.37` (subir 2 linha(s)), `CF88:ART.43` (subir 3 linha(s)), `CF88:ART.62` (subir 3 linha(s)), `CF88:ART.86` (subir 1 linha(s)), `CF88:ART.193` (subir 4 linha(s)), `CF88:ART.194` (subir 3 linha(s)), `CF88:ART.205` (subir 1 linha(s)), `CF88:ART.220` (subir 3 linha(s)), `CF88:ART.225` (subir 1 linha(s)). Isto deve orientar o teste físico do RUN3 (ex.: art. 37: centralizar o caput antes de apertar 4).

## Procedimento de teste físico (sem mudar firmware)

1. Buscar Art. 193; 2. rolar **para cima** até o texto "Art. 193. A ordem social…" ficar na 7ª linha (centro); 3. o rodapé deve mostrar `CONTEXTO: Art. 193` e 4 REF.; 4. tecla 4 → 3 obras.
5. Conferência objetiva: o monitor serial imprime `LEXV1: ACTIVE_TARGET=CF88:ART.193:PAR.UNICO off=349541` logo após a busca e `LEXV1: ACTIVE_TARGET=CF88:ART.193 off=…` com o caput no centro (offsets do caput: 349277, 349329, 349380).

## Possíveis soluções futuras (NÃO implementadas; decidir separadamente)

1. **Busca centraliza o artigo:** após `pesquisarArtigo`, posicionar `linhaTopo` de modo que a linha do "Art. N" fique na linha central (mudança só no posicionamento pós-busca; ACTIVE_TARGET inalterado).
2. **Linha de CONTEXTO = primeira linha de artigo visível quando o topo é o próprio "Art. N" logo após a busca** (estado "recém-buscado" até a primeira rolagem).
3. **Indicador de navegação:** quando o caput tem camada 4 mas o ACTIVE_TARGET é um descendente, mostrar dica "↑ caput tem REF." (sem herdar vínculos).
4. Manter o comportamento atual e documentar o procedimento de teste (custo zero; UX pior em caputs curtos).

Nenhuma opção altera a regra ART↔CAPUT nem propaga vínculos para incisos/parágrafos.

## Resposta

- art193 bug: **NÃO** (comportamento esperado do algoritmo atual; limitação de UX confirmada).
