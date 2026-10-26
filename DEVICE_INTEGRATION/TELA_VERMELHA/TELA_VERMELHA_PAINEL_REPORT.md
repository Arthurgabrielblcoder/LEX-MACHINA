# Firmware jurídico + painel da tela vermelha 3,2" — candidato (2026-10-26)

Branch `fw-tela-vermelha` (base `58a22b0`). Status: **HOST/PHYSICAL CANDIDATE — NÃO APROVADO**; aguarda validação física.
Evidência local: `DEVICE_INTEGRATION/TELA_VERMELHA/_local/painel_gate_20261026_000522/`.

## 1. Baselines
| Item | SHA-256 do app | Situação |
|---|---|---|
| Firmware jurídico aprovado (Content V2, 21/10) | `f7e6b190…09f9` | aprovado fisicamente (tela antiga) |
| INVON=0 (`fe190d8`) | `93685178…302d` | aprovado para cores; base deste candidato |
| LEX_DIAG_CFG5_BOOT (`58a22b0`) | `d91df174…221f` | diagnóstico aprovado; com `b`, MADCTL 0x40 deu cores corretas |
| **Candidato painel** | **`1bb3deb0561451a1a998d530470204fd200cc4160b878aba28200ad1372f4ce3`** | gravado; validação pendente |

Configuração aprovada no diagnóstico: `TFT_RST=15`, `MADCTL=0x40`, 320×240 lógico, RGB, INVOFF, SPI 40 MHz.

## 2. Auditoria (antes de alterar)
- `tft.begin(40000000)`, `tft.setRotation(3)` e `tft.invertDisplay(...)` aparecem **uma única vez**, no `setup()`.
  Não há outro `tft.begin`, `setRotation`, escrita de MADCTL, `scrollTo`/scroll por hardware, `readPixel` nem `getRotation`.
  Os únicos comandos crus são `DISPOFF/DISPON` (`desenharTransicaoSplash` e `definirDisplayLigado`), que não alteram o MADCTL nem a GRAM.
- O desenho usa literais de 320×240 (`tft.width()/height()` não são usados). O splash usa `setAddrWindow(0,0,320,240)` + `writePixels`.
- Adafruit_ILI9341 1.6.3: `setAddrWindow` envia CASET/PASET com os valores pedidos, sem limitar por rotação. Adafruit_GFX recorta só por
  `_width/_height`. Portanto, MADCTL 0x40 (sem MV) + `_width=320,_height=240` não precisa de ajuste no driver (o mesmo mecanismo do diagnóstico aprovado).
  `Adafruit_GFX::setRotation` é virtual, então uma subclasse pode neutralizá-lo.
- Serial do firmware principal: `Serial` = **UART0** (FQBN aprovado sem CDC on boot). Não há o bloqueio do HWCDC visto no diagnóstico.
  Há `delay(800)` após `Serial.begin` e testes de contexto antes da tela; foram **mantidos** (não são bloqueios de Serial comprovados).
- Pinos: `TFT_RST` só em `#define` e no construtor do `tft`. **GPIO15** não tinha uso. **TOUCH_INT=8** só em `pinMode(INPUT_PULLUP)`
  (touch FT6336U intocado). O GPIO14 deixa de ser usado. `aplicarBacklight()` é vazio (não há GPIO de backlight).

Nenhuma incompatibilidade técnica não resolvida foi encontrada.

## 3. Patch (`painel.patch`, 6 edições; gerado por `build_painel_candidate.py`)
1. `TFT_RST 14 → 15`.
2. `tft` passa a ser `Adafruit_ILI9341_PainelLex`: `setRotation()` sobrescrito aplica `MADCTL 0x40` e `_width=320/_height=240` (`rotation=0`).
   Qualquer `setRotation` futuro reaplica a configuração aprovada.
3. Primeira linha do `setup()`: `TFT_RST` em LOW (painel em reset até `tft.begin()`; sem chuvisco).
4. `DISPOFF` logo após `tft.begin()` (a init da lib termina com DISPON). O splash já fazia DISPOFF → desenho → DISPON.
5. `msSplashVisivel` registrado após o splash.
6. Ao fim do `setup()`: uma linha `[LEXUSB]` pela USB nativa (`HWCDC lexUsbSerial`, `setTxTimeoutMs(0)`, não bloqueante).
   Os logs em `Serial` (UART0) não mudaram.
Sem troca manual de R/B: a ordem de cor vem do MADCTL (bit BGR desligado). Nada jurídico, de SD, BLE, touch, menus, índices, ENTENDA,
correlatas, jurisprudência ou referências foi alterado.

## 4. Build e regressão
- FQBN `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default` + `compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1`;
  arduino-cli 1.5.1, core 3.3.11; 0 avisos.
- Base INVON=0 recompilada: 1.109.011 / 127.724 / 1.109.152 B; difere de `93685178` só em metadados (0 bytes fora).
- Candidato: **1.113.799 B de programa (+4.788)**, **127.892 B de RAM estática (+168)**, `.bin` de **1.113.952 B**, margem de app0 196.768 B.
  O acréscimo vem do driver HWCDC da linha de boot.
- `build_painel_candidate.py --check`, `build_tela_vermelha.py --check` e `build_turma_content_v2_candidate.py --check`: **UP_TO_DATE**.

## 5. Gravação
- COM5 `303A:1001`, SER `E0:72:A1:F4:FD:28`, ESP32-S3 rev v0.2, 16 MB; nenhum `serial-monitor` ativo.
- Backup PRE: o app0 completo (`8ec50502…`) começava com `d91df174…` (LEX_DIAG_CFG5_BOOT); boot `110f4d29…`, tabela `f3134b74…`, otadata `f94c5d78…`.
- Somente app0 (`0x10000..0x11ffff`), `Hash of data verified`; readback **idêntico byte a byte** (`1bb3deb0…`).
- POST: boot, tabela e otadata **inalterados**. Nenhum erase total. SD não foi tocado pelo host.
- Boot pela USB (reset do esptool, porta aberta, 120 s de escuta):
  `[LEXUSB] BOOT OK 11404ms splash=1919ms SD=OK pastas=48 MADCTL=0x40 320x240 RST=15` — uma única mensagem, sem reinícios.
  Splash visível 1,9 s após o início do app; setup completo (SD, BLE, caches, diagnóstico V1) em 11,4 s.
  Observação: com a porta fechada no instante dessa linha, ela é descartada (não bloqueante, por projeto).

## 6. Rollback (somente app0, COM5)
Diagnóstico funcional (`d91df174`, cópia em `_local/painel_gate_20261026_000522/ROLLBACK_LEX_DIAG_CFG5_BOOT_d91df174.bin`):
```
python -m esptool --chip esp32s3 -p COM5 -b 460800 --before default-reset --after hard-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/TELA_VERMELHA/_local/painel_gate_20261026_000522/ROLLBACK_LEX_DIAG_CFG5_BOOT_d91df174.bin
```
Outros pontos: INVON=0 `candidate_invon0/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin` (`93685178`, versionado); aprovado da tela antiga
`content_v2_candidate_f7e6b190.bin` (no checkout principal, em `_local`). Depois do rollback: `read-flash 0x10000 <tamanho>` deve dar o SHA esperado.

## 7. Validação física pendente
- [ ] Tela inicia rapidamente, sem chuvisco prolongado
- [ ] Orientação correta, sem espelhamento
- [ ] Cores corretas (verde/preto da interface; acentos vermelhos e azuis no lugar certo)
- [ ] Sem a faixa lateral
- [ ] Menu principal funciona
- [ ] Teclado BLE funciona
- [ ] microSD reconhecido (a USB já reportou `SD=OK pastas=48`)
- [ ] Uma norma abre corretamente
- [ ] Navegação por artigo funciona
- [ ] ENTENDER, correlatas, jurisprudência e referências acessíveis

`PAINEL_FIRMWARE_PHYSICAL: PENDING` — sem aprovação, sem tag e sem merge até a validação.
