# Tela vermelha 3,2" — reprodução do firmware aprovado e candidato INVON=0

Data: 2026-10-25 · Branch: `fw-tela-vermelha` (base `c2c0647`, commit da aprovação física do Content V2) · Status: **HOST_ONLY_CANDIDATE**

Nada foi gravado no ESP32. O microSD, o bootloader, a tabela de partições, o otadata e a NVS não foram tocados.
A correção visual **não** está aprovada: isso depende de teste na tela real.

## 1. Fonte do firmware aprovado (`f7e6b190…`)

| Item | Valor |
|---|---|
| `.ino` | `JURISPRUDENCE_ENGINE/firmware_turma_content_v2/candidate/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino` (commit `bba91c1`, inalterado até `c2c0647`), SHA-256 CRLF `b78d910b…197525e` |
| Headers/assets | `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/` — hashes (LF) fixados em `build_tela_vermelha.py` |
| FQBN | `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default` |
| Build property | `compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1` |
| Toolchain | arduino-cli 1.5.1, `esp32:esp32` 3.3.11; Adafruit GFX 1.12.6, Adafruit ILI9341 1.6.3, Adafruit BusIO 1.17.4, EspBle 1.3.0 |

## 2. Reprodução (evidência)

- Baseline recompilado: 1.109.011 B de programa, 127.724 B de RAM estática, `.bin` de 1.109.152 B, margem de app0 de 201.568 B.
  Os números são idênticos aos do gate de 21/10.
- Comparação com `content_v2_candidate_f7e6b190.bin` (evidência local do gate): mesmo tamanho; 73 bytes diferentes, **todos** dentro
  das faixas de metadados de build (SHA do ELF no `app_desc`, data e hora de compilação, checksum e SHA final da imagem). Fora dos
  metadados há **0 bytes** diferentes. Veredito: `REPRODUCED`.
- O SHA do `.bin` recompilado (`28bbdd9f…`) difere de `f7e6b190` apenas por esses metadados. Isso é esperado: a data e a hora entram na imagem.

## 3. Candidato INVON=0

Única alteração na fonte ([`invon0.patch`](invon0.patch)): `#define PAINEL_PRECISA_INVON 1` → `0`.
Ficaram intocados: frequência SPI (`tft.begin(40000000)`), rotação 3, touch FT6336U, menus, teclado BLE, SD e todo recurso jurídico.
O comentário antigo da linha anterior também foi mantido de propósito, para que a alteração seja só essa.

| | Baseline | INVON=0 | Δ |
|---|---|---|---|
| Programa | 1.109.011 | 1.109.011 | 0 |
| RAM estática | 127.724 | 127.724 | 0 |
| `.bin` | 1.109.152 | 1.109.152 | 0 |
| SHA-256 `.bin` | `28bbdd9f…` | `936851787ee780c626a61d714ec798e806c5d4df45679b99c0becd9460ff302d` | |

**Bytes afetados:** 71 bytes diferem do baseline. 70 deles são metadados (SHA do ELF, data e hora, checksum/SHA). Só **1 byte de código** muda:

```
offset no .bin 0x785ff → endereço 0x420185fe, em setup() (linha 5828/5830 do .ino)
baseline:  420185fe: 1b0c  movi.n a11, 1   → call8 Adafruit_ILI9341::invertDisplay(bool)
INVON=0:   420185fe: 0b0c  movi.n a11, 0   → call8 Adafruit_ILI9341::invertDisplay(bool)
```

**Comportamento afetado:** `invertDisplay(invert)` da Adafruit ILI9341 1.6.3 envia `ILI9341_INVON` (0x21) quando recebe `true` e
`ILI9341_INVOFF` (0x20) quando recebe `false`. O candidato passa a enviar **INVOFF** no boot. O painel deixa de inverter os pixels: o preto
volta a ser 0x0000 → preto e o verde 0x07E0 → verde, em vez de branco/magenta no painel novo. Essa é a única chamada a `invertDisplay`
no firmware; nenhuma outra rotina lê `PAINEL_PRECISA_INVON`.

Limitações a observar no teste físico:
- Se o painel novo usar a ordem BGR, o preto e o verde ficam corretos (o verde independe da troca R↔B), mas acentos vermelhos e azuis
  apareceriam trocados. Isso é ajuste de MADCTL, para uma etapa posterior.
- A faixa inferior com pixels aleatórios **não** é tratada aqui: ela depende de rotação, resolução, controlador e inicialização.
- O touch continua configurado para o FT6336U por I²C; no painel novo ele não deve responder (sem regressão em relação ao estado atual).

## 4. Verificações automatizadas executadas

- `python build_tela_vermelha.py`: compila baseline + candidato, confere os hashes da fonte e dos headers aprovados e exige que o baseline
  reproduza `f7e6b190` (só metadados). **PASS**
- `python build_tela_vermelha.py --check`: confere a fonte, o patch e o `.bin` do candidato contra o relatório. **UP_TO_DATE**
- `python JURISPRUDENCE_ENGINE/firmware_turma_content_v2/build_turma_content_v2_candidate.py --check`: a cadeia tipos → multinorma → turma →
  content V2 regenera exatamente a fonte aprovada. **UP_TO_DATE**
- Disassembly dos dois ELFs: diferença única em `setup()`, como descrito acima.

Não há testes unitários de firmware no projeto; o boot com `LEXV1: DIAG RESULT PASS` só pode ser verificado no aparelho.

## 5. Arquivos

- Candidato: `DEVICE_INTEGRATION/TELA_VERMELHA/candidate_invon0/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin`
  (SHA-256 `936851787ee780c626a61d714ec798e806c5d4df45679b99c0becd9460ff302d`)
- Fonte: `candidate_invon0/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino`; patch: `invon0.patch`; relatório: `TELA_VERMELHA_INVON0_BUILD.json`
- `.elf` e `.map` ficam ao lado do `.bin`, só localmente (gitignored).

## 6. Gravação somente de app0 — **NÃO EXECUTAR sem autorização expressa**

Pré-condições: o aparelho é `1A86:55D3`, serial `5C38165292`, MAC `e0:72:a1:f4:fd:28`, em `COM3`; app0 em `0x10000` (1.310.720 B).
Rodar a partir da raiz do worktree (`C:\GitHub\LEX-MACHINA-tela-vermelha`):

```
python -m esptool --chip esp32s3 -p COM3 -b 460800 read-flash 0x10000 1109152 app0_pre.bin
```
O SHA-256 de `app0_pre.bin` precisa ser `f7e6b190…09f9`. Se não for, parar.

```
python -m esptool --chip esp32s3 -p COM3 -b 460800 --before default-reset --after hard-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/TELA_VERMELHA/candidate_invon0/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin
```
Sem `erase-flash` nem `--erase-all`; nenhum outro offset é escrito. O esptool confere o hash (`Hash of data verified`).

```
python -m esptool --chip esp32s3 -p COM3 -b 460800 read-flash 0x10000 1109152 app0_post.bin
```
O SHA-256 de `app0_post.bin` precisa ser `936851787ee780c6…302d`.

## 7. Reversão

Backups verificados em 2026-10-25:
- `C:\Users\arthu\Desktop\LEX_MACHINA_BACKUP\LEX_MACHINA_ORIGINAL.bin` (16 MB, 24/10, SHA `9711fdb2…70bc`). Os bytes
  `0x10000..+1109152` têm SHA `f7e6b190…` (o app aprovado). Boot, tabela e otadata são idênticos aos do gate de 21/10.
- `JURISPRUDENCE_ENGINE/firmware_turma_content_v2/_local/physical_gate_20261021_102243/content_v2_candidate_f7e6b190.bin` (app aprovado, no checkout principal).

Reversão normal (só app0; a partição de 16 MB não é regravada):
```
python -m esptool --chip esp32s3 -p COM3 -b 460800 --before default-reset --after hard-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 C:\GitHub\LEX-MACHINA\JURISPRUDENCE_ENGINE\firmware_turma_content_v2\_local\physical_gate_20261021_102243\content_v2_candidate_f7e6b190.bin
```
Depois, `read-flash 0x10000 1109152` deve dar SHA `f7e6b190…09f9`.

Último recurso (restaura a flash inteira, inclusive a NVS do dia 24/10):
```
python -m esptool --chip esp32s3 -p COM3 -b 460800 write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x0 C:\Users\arthu\Desktop\LEX_MACHINA_BACKUP\LEX_MACHINA_ORIGINAL.bin
```
