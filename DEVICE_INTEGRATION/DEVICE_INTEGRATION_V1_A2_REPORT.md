# DEVICE INTEGRATION V1-A2 — relatório para revisão humana

**Resultado:** `BLOQUEADO — CANONICAL_CF_SOURCE_UNRESOLVED`, por falta de fonte do ADCT vigente (`CANONICAL_ADCT_SOURCE_NOT_RESOLVED`). A flash foi salva com backup verificado. O backup do cartão continua pendente. Nada foi escrito no hardware e nada foi commitado.

| Item | Resultado |
|---|---|
| Firmware físico | `PHYSICAL_FIRMWARE_CONFIRMED_V7_12_0`: banner serial, string na flash no offset 0x11385, app0 IDF v5.5.5 com build de 20/07/2026 |
| ESP32 | COM3 (CH343); ESP32-S3 QFN56 rev 0.2; MAC `e0:72:a1:f4:fd:28`; flash de 16 MB (0x68/0x4018); PSRAM de 8 MB |
| Dump da flash | `PHYSICAL_FLASH_BACKUP_VERIFIED`: 16.777.216 B, sha256 `061849a3…6727`, duas leituras idênticas (`backups/esp32/`, ignorado pelo Git) |
| Cartão SD | `BACKUP_NOT_AVAILABLE`: o cartão está no aparelho e nenhum volume removível aparece no PC; o arquivo físico da CF segue **UNKNOWN** |
| CF88_RUNTIME | **não criado**; ver `CF88_RUNTIME_SOURCE_AUDIT.md` |
| Pacote `/99_LEX_V1` | 731.341 B; **163 ENTENDA** (154 + 9 pilotos, `CF88_ARTS_1_24_PLUS_APPROVED_PILOTS`); `TEXT_MAP` v2 `LEGACY_STRUCTURAL_NOT_RUNTIME` (fail closed) |
| Parser legado × mapa | 97,84% (3.986/4.074); **0 divergências nos 163 targets com ENTENDA** |
| Firmware candidato | `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/` atrás de `LEX_DEVICE_V1_ENABLED` (padrão 0); detalhes de compilação abaixo |
| Teste host do C++ | não executado: a política de Controle de Aplicativo do Windows bloqueou o compilador host; o algoritmo é validado pelo simulador Python equivalente |
| Issue de 64 linhas | `RELATIONS_V2_LEGACY_64_LINE_LIMIT`: **NON_BLOCKING** (41/64 linhas hoje) |
| Testes | DEVICE 14/14 · ENTENDA 80/80 · LEGAL_TARGET_ID 47/47 |
| Determinismo | staging BYTE_IDENTICAL em 2 builds |

**Compilação do firmware candidato:**
- Flag 0: 989.395 B de flash e 124.452 B de RAM, exatamente como a v7.12.0.
- Flag 1: 995.271 B de flash (+5.876) e 124.452 B de RAM (+0).
