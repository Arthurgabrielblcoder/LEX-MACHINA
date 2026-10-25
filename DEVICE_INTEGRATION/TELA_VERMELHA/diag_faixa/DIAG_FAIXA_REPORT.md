# Faixa de pixels aleatórios — hipóteses e teste diagnóstico

Data: 2026-10-25 · Branch `fw-tela-vermelha` · Firmware no aparelho: INVON=0 (`93685178…302d`), **aprovado para cores**.
Status deste documento: diagnóstico **preparado e compilado**; nada foi gravado. A gravação do teste depende de autorização.

## 1. O que o código garante

No firmware INVON=0 (o mesmo do aprovado, exceto INVOFF):
- `spiBus.begin(12, 13, 11)` (FSPI) → `tft.begin(40000000)` → `setRotation(3)` → `invertDisplay(false)`.
- Na lib Adafruit_ILI9341 1.6.3, a rotação 3 grava MADCTL = `MX|MY|MV|BGR` (0xE8) e define `width = 320` e `height = 240`.
- A init da lib usa a sequência ILI9341 completa (power control 0xC0/0xC1, VCOM 0xC5/0xC7, `PIXFMT 0x55` em 16 bits, `VSCRSADD 0`,
  `DFUNCTR 0xB6 = 08 82 27`, com NL = 0x27 → **320 linhas de gate**). Com o RST no GPIO14, a lib faz reset por hardware e **não** envia SWRESET.
- No boot, o firmware **escreve todos os 320×240 pixels** duas vezes: o splash usa uma janela `(0,0,320,240)` cheia
  (`desenharSplashLexMachina`) e cada tela começa com `fillScreen(COR_FUNDO)`. A moldura vai até `(2,2,316,236)`.
- Barramento compartilhado: o SD usa CS = GPIO4 no mesmo FSPI (MISO 13), a 12 MHz com fallback de 4 MHz. O touch FT6336U usa I²C (6/7) e
  os GPIOs 5/8, fora do SPI.

Conclusão: **num ILI9341 240×320 genuíno, não existe região que o firmware deixe sem escrever.** Uma faixa estável de pixels
aleatórios (o conteúdo da GRAM ao ligar) só aparece se (a) a região estiver fora do que o firmware endereça, ou (b) o vidro não
estiver exibindo o que está na GRAM.

## 2. Hipóteses, da mais para a menos provável

| # | Hipótese | A favor | Contra | Discriminador |
|---|---|---|---|---|
| H1 | **Defeito ou alimentação do módulo** (vidro/FPC/linhas de gate, ou o painel subalimentado) | Problema de VCC já confirmado e corrigido com solda; módulos vermelhos 3,2" têm LDO 3,3 V com jumper J1 (alimentados por 3,3 V sem J1 fechado, o painel fica abaixo da tensão nominal); região fixa que ignora as escritas | O resto da imagem está perfeito | Fase B continua aleatória **e** a fase C lê de volta corretamente na faixa (a GRAM guarda o dado, mas o vidro não mostra). Medir VCC no pino do módulo. |
| H2 | **Geometria ou controlador diferente do ILI9341 240×320** (GRAM ou vidro maiores; ex.: painel 240×400, ou um controlador compatível com DCS mas outro ID) | A faixa ocupa ~¼ (80/320 = 25 %; 80/400 = 20 %); os pixels aleatórios são típicos de GRAM nunca escrita | INVOFF dar cores corretas é típico de ILI9341 TN; um controlador estranho tenderia a falhar mais do que só uma faixa | Fase B: a faixa fica **MAGENTA uniforme**. Fase A: a grade 320×240 aparece inteira, com a faixa **fora** dela. ID ≠ `00 93 41`. |
| H3 | **Mapeamento de gate/scan** (DFUNCTR NL/SS/GS/SM, scroll vertical) incompatível com este vidro | Explicaria uma faixa fixa ligada às linhas | A lib zera o scroll e usa NL=320, valores do ILI9341 padrão | Fase A: a grade aparece **deslocada, cortada ou repetida** (não só uma faixa por cima). Fica para um teste posterior (uma variável: NL). |
| H4 | **Integridade SPI a 40 MHz** (fios longos, terra, reflexão) | 40 MHz está acima do clock nominal de escrita do ILI9341 (~10 MHz, embora na prática costume funcionar) | Erro de SPI gera pixels errados **espalhados** e diferentes a cada redesenho, não um bloco contíguo estável | Fases D (10 MHz) e E (30 redesenhos): a faixa muda ou some a 10 MHz → SPI. |
| H5 | **Conflito no barramento compartilhado** (SD/MISO, pinos do touch antigo) | O SD está no mesmo FSPI | O SD está fora; o CS do SD fica em nível alto; um conflito afetaria a tela toda | O diagnóstico não inicia SD, BLE nem I²C. Se a faixa persistir, H5 fica descartada. |
| H6 | **RST do módulo desconectado** (sem reset por hardware e sem SWRESET) | A lib só envia SWRESET quando `rst < 0` | Ao ligar, o controlador já parte do estado padrão | Visível no log (MADCTL/PIXFMT lidos). Não explica uma faixa persistente após desligar e ligar. |

## 3. Teste mínimo

**Passo 0 — custo zero, sem gravar nada** (fazer antes):
1. Foto da tela inteira com o firmware atual (splash e tela de erro do SD).
2. Onde está a faixa (base, topo, esquerda, direita), qual a espessura aproximada e se é **estática** ou **cintila/muda**.
3. Foto do verso do módulo: modelo impresso (ex.: "3.2 TFT SPI 240x320", "MSP3218"), CI do controlador, quantidade de pinos,
   jumper **J1** (aberto ou fechado), e se há o pino **SDO/MISO** e o chip de touch (XPT2046 é um SOIC/TSSOP de 16 pinos).
4. Em qual pino o VCC do módulo está ligado (3,3 V ou 5 V) e, se possível, a tensão medida entre VCC e GND com a tela acesa.

**Passo 1 — firmware diagnóstico** `LEX_DIAG_FAIXA` (separado, sem nenhum recurso jurídico):
- Init idêntico ao do firmware INVON=0 (mesmos pinos, FSPI, `begin(40 MHz)`, rotação 3, INVOFF). Não inicia SD, BLE nem touch.
- Ciclo de ~75 s, repetido. Cada fase muda **uma** coisa e mostra o título na tela:
  - **A · 40 MHz**: grade de 40 px com rótulos, borda 320×240 e cantos 12×12 (vermelho em cima à esquerda, azul em cima à direita,
    branco embaixo à esquerda, amarelo embaixo à direita).
  - **B · GRAM 480×480**: preenche uma janela 480×480 de MAGENTA e redesenha a grade A por cima.
  - **C · leitura da GRAM**: escreve e lê de volta 1 pixel no centro de cada célula 40×40. Quadrado verde = confere; vermelho = diverge.
    Só roda se o LCD responder no MISO.
  - **D · 10 MHz**: a grade A com o clock SPI a 10 MHz.
  - **E · 30 redesenhos a 40 MHz**: procura instabilidade.
- Log no Serial USB (COM5, 115200; build com `CDCOnBoot=cdc`, só no diagnóstico): `RDID4 (D3)`, `RDDID (04)`, `RDDST`, MADCTL, PIXFMT,
  e o mapa 8×6 da fase C. Eu mesmo posso capturar o log pela COM5 logo após a gravação.

Compilação (host, sem warnings com `--warnings all`):
`esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default,CDCOnBoot=cdc`
→ 343.224 B de programa, 24.432 B de RAM; `LEX_DIAG_FAIXA.ino.bin` com 343.376 B,
SHA-256 `1cbf55c372d6356c71d82532caf8fc19ea7e2b8af219a825ed77b5e5992954ea` (magic 0xE9, chip_id 9 = ESP32-S3; cabe em app0).
O candidato INVON=0 continua conferido (`build_tela_vermelha.py --check` = UP_TO_DATE).

## 4. Critérios objetivos

| Observação | Conclusão |
|---|---|
| Grade A inteira, quatro cantos visíveis **e** faixa fora dela; na fase B a faixa fica MAGENTA | **H2**: a memória e o vidro são maiores que 240×320. Próximo passo: identificar o controlador e ajustar resolução/janela, não SPI. |
| Faixa **por cima** de parte da grade (algum canto ou rótulo some) e continua aleatória em A, B, D e E | **H1**: aquela área do vidro não exibe a GRAM. Se a fase C der "." nessas células, a GRAM está boa e o defeito é de vidro/FPC/alimentação. Medir VCC e conferir J1 antes de qualquer mudança de firmware. |
| Fase C com "X" justamente nas células da faixa | Controlador ou GRAM defeituosos naquela região (hardware). |
| Faixa diminui, muda ou some em D (10 MHz), ou varia entre os redesenhos de E | **H4**: integridade SPI. Próximo candidato do firmware: só baixar o clock de `tft.begin`. |
| Grade deslocada, cortada ou repetida (não só encoberta) | **H3**: mapeamento de gate/scan. Próximo passo: testar só o NL/SS/GS do `0xB6`. |
| `RDID4 = 00 93 41` | É ILI9341: H2 por controlador diferente fica improvável (mas um vidro maior ainda é possível). |
| `MISO sem resposta` | Leituras inconclusivas (SDO do LCD não ligado ao GPIO13 ou MISO preso). Vale só a parte visual. |
| Faixa igual com SD, BLE e touch desligados | H5 descartada. |

## 5. Gravação do diagnóstico — **NÃO EXECUTADA; exige autorização**

Pré-checagem (só leitura): `flash-id` com MAC `e0:72:a1:f4:fd:28`; tabela de partições `f3134b74…`; app0 `0x10000`; o readback de
`0x10000`+1.109.152 B tem de ser `936851787ee780c6…302d` (o INVON=0 atual).

```
python -m esptool --chip esp32s3 -p COM5 -b 460800 --before default-reset --after hard-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/TELA_VERMELHA/diag_faixa/LEX_DIAG_FAIXA.ino.bin
```
Readback: `read-flash 0x10000 343376` deve ter SHA `1cbf55c3…54ea`. O resto de app0 (o fim antigo do INVON=0) não é apagado e não
é executado. Boot, tabela, otadata e NVS não são tocados. O SD continua fora do aparelho.

## 6. Reversão (logo após o teste)

Voltar ao INVON=0 aprovado para cores (só app0):
```
python -m esptool --chip esp32s3 -p COM5 -b 460800 --before default-reset --after hard-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/TELA_VERMELHA/candidate_invon0/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin
```
Readback de `0x10000`+1.109.152 B → `936851787ee780c6…302d`. Para voltar ao aprovado original (tela antiga), use `content_v2_candidate_f7e6b190.bin`
(seção 7 do relatório INVON=0, com COM5).
