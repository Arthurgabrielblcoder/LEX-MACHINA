# LEX_DIAG_CFG5_BOOT — boot rápido e teste de cor (2026-10-25, EXPERIMENTAL)

Branch `fw-tela-vermelha`, base `524168c`. Evidência local: `_local/diag_cfg5_boot_20261025_233717/`.

## Validação física do CFG5 (usuário)
CFG 5 (`MADCTL 0x48`, 320×240): orientação horizontal correta, textos sem espelhamento, **sem a faixa de 80 px**, imagem estável.
Ressalvas: (1) ao ligar, **10–15 s de chuvisco colorido** antes da imagem; (2) na foto, as barras rotuladas R, G e B aparecem
**azul, verde e vermelho**.

**Ponto de retorno preservado:** `LEX_DIAG_CFG5` (`524168c`), binário exato `9dec91c3e32fc8dff2c3e5871d22d838b57d9c6c2ed983f54e3aeaffe58bdc21`
em `_local/diag_cfg5_20261025_232219/LEX_DIAG_CFG5.ino.bin` (cópia em `_local/diag_cfg5_boot_20261025_233717/ROLLBACK_LEX_DIAG_CFG5_9dec91c3.bin`). O fonte recompila
idêntico, exceto pelos metadados de build (68 bytes, todos nas faixas de metadados).

## Causa do atraso (código)
No `LEX_DIAG_CFG5`, nada era desenhado antes de:
1. `while (!Serial && millis() - t0 < 3000)`: **até 3 s** esperando um programa abrir a porta USB.
2. ~15 `Serial.print` (cabeçalho + lista de 10 configurações + ajuda), **antes** do primeiro desenho. No core 3.3.11, o `HWCDC::write`
   (USB-Serial/JTAG) com o PC conectado mas a porta fechada não esvazia o buffer: cada escrita bloqueia até
   `max_consec_timeouts (20) × tx_timeout_ms (100 ms)` ≈ **2 s** (`cores/esp32/HWCDC.cpp`). Com o buffer cheio após poucas linhas,
   as demais somam vários segundos. Isso é compatível com os 10–15 s observados (o tempo exato depende do host).
Enquanto isso, o painel exibia a GRAM aleatória (o chuvisco). Não há outros delays, reinicializações ou bloqueios no sketch.

**Reset no GPIO15:** a Adafruit_SPITFT 1.12.6 (`initSPI`) aciona o pino do construtor: HIGH 100 ms → LOW 100 ms → HIGH 200 ms. Como
`_rst = 15 ≥ 0`, ela não envia SWRESET. O reset por hardware está sendo usado.

**Backlight:** não existe GPIO de backlight no firmware nem nos diagnósticos (o LED do módulo não está em nenhum pino controlado).
Nenhum controle de backlight foi assumido.

## Variante `LEX_DIAG_CFG5_BOOT` (mudanças de boot, mesma CFG 5)
- `TFT_RST` vai para LOW na primeira linha do `setup()`: o painel fica em reset desde o início do app.
- Sem espera por Serial, e `Serial.setTxTimeoutMs(0)`: o log nunca bloqueia, e a impressão acontece **depois** do desenho.
- Logo após `tft.begin()` (cuja init termina com DISPON), envia `DISPOFF`, aplica `MADCTL 0x48` + 320×240 + INVOFF, desenha tudo e só então `DISPON`.
- Timestamps do boot no Serial (comando `t`) e "boot ate imagem: N ms" na tela.
- **Teste de cor sem alterar o MADCTL aprovado:** linha **1** = barras R, G e B com os valores normais; linha **2** = mesmas barras com R e B
  trocados no software. Se a linha 2 aparecer vermelho-verde-azul, o painel é RGB e o ajuste futuro seria **MADCTL 0x40** (sem o bit BGR).
  O comando `b` permite conferir 0x40 ao vivo, sem regravar.
- Pinos, SPI 40 MHz, MADCTL 0x48 e geometria 320×240 idênticos ao CFG5 (verificado por comparação textual).

## Compilação e regressão
- FQBN `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default,CDCOnBoot=cdc`, 0 avisos nos dois sketches.
- CFG5_BOOT: 344.008 B de programa, 24.520 B de RAM, `.bin` de 344.160 B, SHA **`d91df174ad28b4a77d88abcd258e529e5b4b34f8eb3820d73bfae5d1f1af221f`**.
- Regressões: o CFG5 aprovado reproduz (só metadados diferem); as definições de pinos, SPI, CFG 5 e entrada RAW 48 são idênticas; sem `while (!Serial`.

## Gravação
- COM5 livre (`303A:1001`, SER `E0:72:A1:F4:FD:28`). Backup PRE: o app0 (`6cc440b1…`) começava com `9dec91c3…` (CFG5), como esperado.
- Somente app0 (`0x10000..0x64fff`), `Hash of data verified`; readback **idêntico byte a byte** (`d91df174…`).
- Boot `110f4d29…`, tabela `f3134b74…` e otadata `f94c5d78…`: **inalterados**. SD não acessado.

## Medição do boot (USB, reset pelo esptool)
| Marco | ms desde o início do app |
|---|---|
| setup: RST=LOW | 25,3 |
| Serial.begin (sem espera) | 25,5 |
| spiBus.begin | 25,7 |
| tft.begin (reset 400 ms + init com SLPOUT/DISPON 150+150 ms) | 726,1 |
| DISPOFF | 726,1 |
| MADCTL 0x48 + primeiro desenho completo | 832,8 |
| **DISPON (imagem visível)** | **832,8** |

O tempo foi idêntico com a porta **fechada** durante o boot (o cenário do usuário) e com a porta aberta.
Limite do software: antes do app (ROM + bootloader, poucas centenas de ms), o pino RST fica flutuando, e um lampejo curto ainda é possível.
Eliminá-lo exigiria hardware (por exemplo, um pull-down no RST), o que **não** foi feito nem é recomendado agora.

## Pendente: validação física
- [ ] Ao ligar, o chuvisco some (ou fica abaixo de ~1 s)? Que valor aparece em "boot ate imagem"?
- [ ] Orientação, bordas, cantos e textos iguais ao CFG5 aprovado?
- [ ] **Cores:** qual linha aparece como vermelho, verde, azul da esquerda para a direita: **1** ou **2**?

`USER_VISUAL_VALIDATION: PENDING`
