# LEX_DIAG_CFG5 — CFG 5 (RAW 48) fixa no boot (2026-10-25)

Branch `fw-tela-vermelha`, base `73208ea`. Evidência local: `_local/diag_cfg5_20261025_232219/`.

## Escolha visual do usuário (LEX_DIAG_ORIENTACAO)
Percorrendo as configurações com `n`⏎, a imagem ficou corretamente orientada e **sem a faixa de ~80 px** em:
`[SEL] CFG 5/9 RAW 48 MADCTL=0x48 geometria=320x240 BGR INVOFF SPI=40000000Hz`.
Ao fechar o Monitor Serial, o ESP32 reiniciou e voltou à CFG 0 (a padrão do seletor), por isso a orientação mudou. Isso é esperado
naquele sketch e não indica falha da CFG 5.

**Status: CFG 5 é uma candidata visual, ainda sujeita a validação após reinicialização.** Não está aprovada.

## Variante `LEX_DIAG_CFG5` (sketch separado; o `LEX_DIAG_ORIENTACAO` foi preservado)
Diferenças em relação a `LEX_DIAG_ORIENTACAO`, e somente estas:
- `#define CFG_INICIAL 5` e `atual = CFG_INICIAL`: o boot já desenha a CFG 5.
- Comentário de cabeçalho, mensagem de boot no Serial e a linha de texto "CFG5 FIXA NO BOOT - LEX MACHINA" quando a CFG 5 está ativa.

Ordem no boot: `tft.begin(40 MHz)` → `setRotation(3)` → `invertDisplay(false)` → `desenhar()`, que aplica `MADCTL 0x48` cru,
fixa a geometria lógica em 320×240 e aplica INVOFF. Nada chama `setRotation` depois, então o MADCTL não é sobrescrito.
Não há sequência automática: a imagem fica estática indefinidamente, com ou sem Monitor Serial. Os comandos `n/p/0–9/b/i/r/?`
continuam disponíveis, só para voltar ao seletor sem regravar.
Pinos inalterados: CS 10, DC 9, **RST 15**, MOSI 11, SCK 12, MISO 13, SD_CS 4 (HIGH; SD nunca iniciado).

## Gate
- Compilação: FQBN `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default,CDCOnBoot=cdc`, 0 avisos; 342.828 B de programa,
  24.432 B de RAM, `.bin` de 342.976 B, SHA **`9dec91c3e32fc8dff2c3e5871d22d838b57d9c6c2ed983f54e3aeaffe58bdc21`**.
- COM5 livre (`303A:1001`, SER `E0:72:A1:F4:FD:28`), ESP32-S3 rev v0.2, 16 MB.
- Backup PRE: o app0 completo (`ead4e1c4…8bed`) começa com `1f2ec992…` (LEX_DIAG_ORIENTACAO), como esperado.
- Gravação somente de app0 (`0x10000..0x63fff`), `Hash of data verified`; readback **idêntico byte a byte**.
- Boot `110f4d29…`, tabela `f3134b74…` e otadata `f94c5d78…`: **inalterados**. SD não acessado.
- Serial em **dois resets seguidos**: as duas vezes iniciaram direto em
  `[SEL] CFG 5/9 RAW 48 MADCTL=0x48 geometria=320x240 BGR INVOFF SPI=40000000Hz`.

## Pendente: validação física
- [ ] Desligar e ligar (USB fora e dentro): a imagem volta correta?
- [ ] As quatro bordas inteiras (vermelho em cima, azul embaixo, verde à esquerda, amarelo à direita), os cantos 1-2-3-4 na ordem e sem faixa?
- [ ] O "F" e os textos sem espelhamento; barras R, G e B com as cores certas?
- [ ] Estável parada por alguns minutos?

Se algo falhar, registrar aqui. O seletor `LEX_DIAG_ORIENTACAO` (`1f2ec992…`) continua disponível, e os comandos manuais
também funcionam neste sketch.

`USER_VISUAL_REBOOT_VALIDATION: PENDING`
