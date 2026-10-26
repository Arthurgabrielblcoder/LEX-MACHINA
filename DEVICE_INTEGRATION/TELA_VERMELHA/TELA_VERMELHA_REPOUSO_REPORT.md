# Repouso com tela preta — candidato EXPERIMENTAL (2026-10-26)

Branch `fw-tela-vermelha`, base `9c93091` (auditoria em `AUDITORIA_REPOUSO_TELA_BRANCA.md`). Evidência local: `_local/repouso_gate_20261026_004242/`.

> **SOLUÇÃO VISUAL PROVISÓRIA.** A tela fica preta no repouso, mas o **backlight continua aceso** (ligado no 3,3 V, sem GPIO).
> Não há a economia de energia de um desligamento real. Desligar a luz de verdade exige controle elétrico do pino LED, fora deste escopo.

## Base preservada
Candidato painel `22367f3`, `1bb3deb0561451a1a998d530470204fd200cc4160b878aba28200ad1372f4ce3` (versionado em `candidate_painel/`,
com cópia em `_local/repouso_gate_20261026_004242/ROLLBACK_PAINEL_1bb3deb0.bin`). O fonte recompila idêntico, exceto pelos metadados.

## Alteração (`repouso.patch`, 2 edições, só na rotina de repouso)
1. `definirDisplayLigado(false)`: `tft.fillScreen(COR_FUNDO)` (preto) com o display **ligado**; não envia mais DISPOFF.
   `definirDisplayLigado(true)`: `DISPON` (inócuo), seguido do `redesenharTelaAtual()` que já existia.
2. `atualizarInatividadeDisplay()`: `displayApagado=true` passa a ser marcado **antes** de pintar, e o timeout é reconferido.
   Uma tecla que chegou entre o teste e a marcação já atualizou `ultimaInteracaoMs` (o repouso é cancelado); uma que chegue depois é
   consumida só para acordar (`registrarAtividadeUsuario`). Com isso, nenhuma ação de tecla, roda ou busca desenha sobre a tela preta.
Inalterados: timeout de 180 s; a primeira tecla só acorda; MADCTL 0x40, RST GPIO15, RGB, INVOFF, SPI 40 MHz, inicialização, SD, BLE e conteúdo jurídico.

## Build e regressão
- FQBN aprovado + `-DLEX_DEVICE_V1_ENABLED=1`, 0 avisos. Programa **1.113.823 B (+24)**, RAM **127.892 B (+0)**, `.bin` **1.113.968 B**,
  SHA **`a7beea0bba243bcc92d728bc4242f88a4aacaf3f273fa6ac8d5b6de6bc6c2bfe`**.
- `--check` de `build_repouso_candidate`, `build_painel_candidate`, `build_tela_vermelha` e `build_turma_content_v2_candidate`: **UP_TO_DATE**.

## Gravação
- COM5 (`303A:1001`, SER `E0:72:A1:F4:FD:28`), sem Monitor Serial. Backup PRE: o app0 (`ed6dbd91…`) começava com `1bb3deb0…`.
- Somente app0 (`0x10000..0x11ffff`), `Hash of data verified`; readback **idêntico byte a byte**. Boot `110f4d29…`, tabela `f3134b74…` e
  otadata `f94c5d78…`: **inalterados**. SD não acessado pelo host.
- USB: `[LEXUSB] BOOT OK 11401ms splash=1919ms SD=OK pastas=48 MADCTL=0x40 320x240 RST=15`.

## Rollback (só app0)
```
python -m esptool --chip esp32s3 -p COM5 -b 460800 --before default-reset --after hard-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/TELA_VERMELHA/candidate_painel/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin
```
O readback de `0x10000`+1.113.952 B deve dar `1bb3deb0…`.

## Validação física (2026-10-26, usuário)
- [x] Após 3 min sem tocar, a tela fica **preta** (não branca)
- [x] Nada aparece sobre a tela preta durante o repouso
- [x] A primeira tecla só acorda e a tela anterior volta completa

`REPOUSO_PHYSICAL_VISUAL: PASS` — firmware `a7beea0b…` (commit `40272ed`). Continua sendo **solução visual provisória**: o backlight
segue aceso, sem economia de energia real. Sem merge e sem congelar o firmware: a validação completa do candidato (navegação jurídica,
BLE, SD, ENTENDER/correlatas/jurisprudência/referências) continua sob decisão do usuário.
