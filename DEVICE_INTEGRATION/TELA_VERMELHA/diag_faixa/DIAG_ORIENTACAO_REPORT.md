# LEX_DIAG_ORIENTACAO — seleção manual de orientação (2026-10-25)

Branch `fw-tela-vermelha`, base `7f63042`. O sketch `LEX_DIAG_FAIXA` foi **preservado**; esta é uma variante nova em
`diag_faixa/LEX_DIAG_ORIENTACAO/`. O firmware principal não foi modificado. Evidência local: `_local/diag_orientacao_20261025_230532/`.

## Contexto
Com o RESET no GPIO15 (`7f63042`), o `LEX_DIAG_FAIXA` passou a preencher praticamente toda a tela, aparentemente sem a faixa de ~80 px,
mas algumas configurações aparecem espelhadas. Como o ciclo automático dificultava a identificação, cada configuração agora fica parada até um comando no Serial.

## O que os testes anteriores aplicaram (de fato, no código)
- Init: `tft.begin(40 MHz)` da Adafruit_ILI9341 1.6.3 (sequência ILI9341; reset por hardware no pino RST) e `invertDisplay(false)`.
- `setRotation(n)` → MADCTL da lib: **0 = 0x48** (MX|BGR, 240×320), **1 = 0x28** (MV|BGR, 320×240), **2 = 0x88** (MY|BGR, 240×320), **3 = 0xE8** (MX|MY|MV|BGR, 320×240).
  O firmware principal usa a rotação 3, ou seja, 0xE8.
- RAW do `LEX_DIAG_FAIXA`: MADCTL **0x08, 0x48, 0x88, 0xC8**, com a geometria lógica **forçada em 320×240** (sem MV).
- Inversão: INVOFF em tudo, exceto 3 s de INVON na etapa "INV". SPI: 40 MHz em tudo, exceto uma etapa de 10 MHz.

## Candidatas (BGR ligado por padrão; 40 MHz; INVOFF)
| CFG | Nome | MADCTL | Geometria lógica | Origem |
|---|---|---|---|---|
| 0 | LIB ROT1 | 0x28 | 320×240 | setRotation(1) |
| 1 | LIB ROT3 | 0xE8 | 320×240 | setRotation(3), a do firmware principal |
| 2 | MV+MX | 0x68 | 320×240 | troca de eixos + espelho X |
| 3 | MV+MY | 0xA8 | 320×240 | troca de eixos + espelho Y |
| 4 | RAW 08 | 0x08 | 320×240 forçado | RAW do LEX_DIAG_FAIXA |
| 5 | RAW 48 | 0x48 | 320×240 forçado | RAW do LEX_DIAG_FAIXA |
| 6 | RAW 88 | 0x88 | 320×240 forçado | RAW do LEX_DIAG_FAIXA |
| 7 | RAW C8 | 0xC8 | 320×240 forçado | RAW do LEX_DIAG_FAIXA |
| 8 | LIB ROT0 | 0x48 | 240×320 | setRotation(0), retrato, só referência |
| 9 | LIB ROT2 | 0x88 | 240×320 | setRotation(2), retrato, só referência |

Com MV/MX/MY ∈ {0,1}, as configurações 0–7 cobrem as 8 combinações em 320×240. Os comandos `b` (BGR↔RGB) e `i` (INVON↔INVOFF)
alteram a configuração exibida sem mudar o índice.

## Padrão desenhado em cada configuração
- Bordas de 4 px, uma cor por lado: **cima vermelho**, **baixo azul**, **esquerda verde**, **direita amarelo**. As quatro inteiras = tela totalmente preenchida.
- Rótulos "CIMA", "BAIXO", "ESQ" e "DIR" junto da borda correspondente, e uma seta amarela apontando para a direita.
- Cantos numerados em ordem de leitura: **1 magenta** sup-esq, **2 ciano** sup-dir, **3 branco** inf-esq, **4 laranja** inf-dir.
- "F" branco grande e assimétrico. Correto = haste à esquerda e barras para a direita, com a barra longa em cima. Espelho X inverte as barras; espelho Y põe a barra longa embaixo.
- Texto: "CFG n NOME", "MADCTL=0x.. W=.. H=.. BGR/RGB INVON/INVOFF" e "LEX MACHINA leia normal?".
- Barras **R, G, B** rotuladas, para conferir as cores.
- Grade de 40 px.

## Gate
- Compilação: FQBN `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default,CDCOnBoot=cdc`, `--warnings all` sem avisos;
  342.764 B de programa, 24.432 B de RAM, `.bin` de 342.912 B, SHA **`1f2ec992a0e88f7309dcba71d7a987b71a3792c4fe29ce68d8d5beb2b9cb70b5`**.
- Pinos iguais ao `LEX_DIAG_FAIXA` (7f63042): CS 10, DC 9, **RST 15**, MOSI 11, SCK 12, MISO 13, SD_CS 4 (HIGH; SD nunca iniciado).
- COM5 livre (sem `serial-monitor` ativo); `303A:1001`, SER `E0:72:A1:F4:FD:28`; ESP32-S3 rev v0.2, 16 MB.
- Backup PRE: o app0 completo (`191394cf…2aea`) começa com `98774093…` (LEX_DIAG_FAIXA RST=15), como esperado.
- Gravação somente de app0 (`0x10000..0x63fff`), `Hash of data verified`; readback **idêntico byte a byte** (`1f2ec992…`).
- Boot `110f4d29…`, tabela `f3134b74…` e otadata `f94c5d78…`: **inalterados**. SD não acessado.
- Serial: boot OK e lista impressa; os comandos `n`, `p`, `7⏎` e `0⏎` responderam com `[SEL] …`. O aparelho foi deixado na **CFG 0**.

`USER_VISUAL_SELECTION: PENDING`
