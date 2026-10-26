# Checkpoint funcional — firmware jurídico com a tela TFT vermelha 3,2" (2026-10-26)

```
CHECKPOINT = TELA_VERMELHA_FUNCTIONAL_CHECKPOINT
ESCOPO = adaptação da nova tela + repouso visual + preservação funcional por amostragem
NAO_E = aprovação de todo o conteúdo jurídico, freeze de dados, merge ou release
FIRMWARE_APP_SHA256 = a7beea0bba243bcc92d728bc4242f88a4aacaf3f273fa6ac8d5b6de6bc6c2bfe
FIRMWARE_APP_BYTES = 1113968
BRANCH = fw-tela-vermelha (worktree C:\GitHub\LEX-MACHINA-tela-vermelha; não enviada ao remoto)
TAG = lex-device-v1-tela-vermelha-functional-checkpoint-2026-10-26 (anotada; aponta para o commit deste relatório)
MERGE = NÃO
```

Este congelamento foi só documental: o ESP32 não foi lido, reiniciado nem gravado, o microSD não foi acessado e nenhum dado jurídico foi alterado.

## 1. Verificações de integridade (antes da tag)
- Branch `fw-tela-vermelha`, HEAD `2fc7104` antes deste relatório; working tree **limpa** (só artefatos ignorados: `_local/`, `__pycache__`, `.elf/.map`).
- Commits citados, todos ancestrais do HEAD:
  - `b11f4fb` (repouso PASS), `f8764c3` (correlata 161, I) e `2fc7104` (Jurisprudência nº 2);
  - `40272ed`, `22367f3`, `58a22b0`, `524168c`, `73208ea`, `7f63042`, `fe190d8`;
  - base `c2c0647`.
- Nenhuma tag anterior com o nome deste checkpoint; nenhuma tag foi movida.

## 2. Firmware gravado
| Item | Valor |
|---|---|
| Binário versionado | `DEVICE_INTEGRATION/TELA_VERMELHA/candidate_repouso/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin` (blob `15b16ba1…`) |
| SHA-256 | **`a7beea0bba243bcc92d728bc4242f88a4aacaf3f273fa6ac8d5b6de6bc6c2bfe`** (arquivo e `git show HEAD:` idênticos) |
| Prova física | gate de repouso de 26/10 (`_local/repouso_gate_20261026_004242/`, fora do Git): readback de `0x10000`+1.113.968 B **idêntico byte a byte**; boot, tabela e otadata inalterados; USB `[LEXUSB] BOOT OK … SD=OK pastas=48 MADCTL=0x40 320x240 RST=15`. Nenhuma gravação desde então. |
| Fonte | `candidate_repouso/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino` (sha CRLF `e304d7d1…`) |
| Cadeia de build | aprovado `f7e6b190` (Content V2, `bba91c1`) → `invon0.patch` → `painel.patch` (6 edições) → `repouso.patch` (2 edições) |
| Builders | `build_tela_vermelha.py`, `build_painel_candidate.py`, `build_repouso_candidate.py` (cada um reproduz a base anterior antes de gerar); `--check` dos três + `build_turma_content_v2_candidate.py`: **UP_TO_DATE** |
| Toolchain | arduino-cli 1.5.1; `esp32:esp32` 3.3.11; FQBN `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`; `compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1` |
| Tamanhos | programa 1.113.823 B; RAM estática 127.892 B; app0 livre 196.752 B |

**Configuração de tela:** `TFT_RST=GPIO15`; `MADCTL=0x40` (MX, RGB, sem MV) aplicado por `Adafruit_ILI9341_PainelLex` (que neutraliza `setRotation`);
geometria lógica 320×240; INVOFF; SPI 40 MHz; RST em LOW desde o início do `setup()` e DISPOFF até o splash (boot sem chuvisco; splash em ~1,9 s);
repouso após 180 s com `fillScreen` preto; a primeira tecla só acorda e redesenha a tela.

## 3. Validações
### 3.1 Aprovação física (usuário, no aparelho com `a7beea0b` ou com o candidato idêntico de tela `1bb3deb0`)
| Item | Resultado | Registro |
|---|---|---|
| Tela: orientação horizontal, sem espelhamento, sem a faixa de 80 px, cores RGB corretas, boot rápido | PASS | `diag_faixa/DIAG_CFG5_BOOT_REPORT.md`, `TELA_VERMELHA_PAINEL_REPORT.md` |
| Repouso visual (tela preta após 3 min, nada sobreposto) e despertar pela 1ª tecla com a tela anterior completa | PASS | `TELA_VERMELHA_REPOUSO_REPORT.md` (`b11f4fb`) |
| Navegação e leitura da CF | PASS | informado pelo usuário (26/10) |
| Legislação Correlata nº 1: CF art. 161, I → LC 63/1990, art. 3º, com BACK | PASS | `INVESTIGACAO_CORRELATA_CF161_I.md` (`f8764c3`) + confirmação do usuário |
| Referências nº 4: CF art. 196 → Sicko; art. 205 → Cidadania no Brasil: O Longo Caminho; art. 206, I → Pro Dia Nascer Feliz | PASS | informado pelo usuário (26/10) |
| Jurisprudência nº 2: art. 53, § 1º (HC 232627), art. 52, p.u. (MS 21689), art. 15, III (Súmula 9 TSE): rodapé, tecla 2, ficha, BACK ×2 | **3/3 PASS** | `MATRIZ_TESTE_JURIS2_TELA_VERMELHA.md` (`2fc7104`) |

### 3.2 Funcionamento demonstrado (sem matriz formal)
- ENTENDA: abertura demonstrada.
- Teclado BLE: navegação em todos os testes acima.
- Leitura do SD: navegação em todos os testes; a USB reportou `SD=OK pastas=48`.

### 3.3 Não coberto por este checkpoint
- Auditoria completa de todos os vínculos (CF/ADCT 315/198, CC, correlatas, referências, ENTENDA 810): o checkpoint é **amostragem funcional**.
- Os 48 itens do checklist físico do **mass deploy CC Content V2** (seção 5).

## 4. Recuperação do firmware (NÃO executar sem autorização)
Pré-requisitos: aparelho na COM do USB nativo (hoje **COM5**, `303A:1001`, SER `E0:72:A1:F4:FD:28`), Monitor Serial fechado, microSD no aparelho
(não é tocado). Sempre: backup PRE, depois gravação **só de app0**, readback e conferência de boot, tabela e otadata.
```
python -m esptool --chip esp32s3 -p COM5 -b 460800 --after no-reset read-flash 0x10000 0x140000 app0_pre.bin
python -m esptool --chip esp32s3 -p COM5 -b 460800 --before default-reset --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 DEVICE_INTEGRATION/TELA_VERMELHA/candidate_repouso/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin
python -m esptool --chip esp32s3 -p COM5 -b 460800 --after hard-reset read-flash 0x10000 1113968 app0_post.bin
```
O SHA-256 de `app0_post.bin` deve ser `a7beea0b…6bfe`. Sem `erase-flash`; nunca gravar bootloader, tabela de partições ou otadata.
Para reconstruir o binário a partir da fonte: `python build_repouso_candidate.py` (compila e reproduz a base antes; o SHA difere só por
metadados de build). A verificação sem compilar é feita com `--check`.

Outros pontos de retorno: `candidate_painel/…bin` (`1bb3deb0`, sem repouso preto); `candidate_invon0/…bin` (`93685178`, painel antigo/INVON=0);
aprovado da tela antiga `f7e6b190` (`JURISPRUDENCE_ENGINE/firmware_turma_content_v2/_local/physical_gate_20261021_102243/`, no checkout principal);
backup de flash inteira `C:\Users\arthu\Desktop\LEX_MACHINA_BACKUP\LEX_MACHINA_ORIGINAL.bin` (24/10, app0 = `f7e6b190`). **Atenção:** o hardware
atual (RST no GPIO15, painel nativo em paisagem) exige o firmware desta branch para a imagem correta.

## 5. Pendências
1. **Touch da nova tela não migrado:** o firmware ainda espera o FT6336U por I²C (GPIOs 5/6/7/8). O controlador resistivo (provável XPT2046) e os
   GPIOs ainda precisam ser confirmados antes de qualquer migração.
2. **Backlight ligado direto ao 3,3 V:** o repouso preto é **só visual**; não há economia de energia. Desligar a luz exige controle elétrico do pino
   LED (GPIO + transistor), fora do escopo.
3. **Mass deploy CC Content V2 (22/10):** `MASS_V2_TECHNICAL = PASS`, mas `MASS_V2_USER_VALIDATION = PENDING`. Há **48 verificações físicas** em
   aberto em `JURISPRUDENCE_ENGINE/CC_MASS_DEPLOY_653_V2/_local/mass_v2_gate_20261022/CC_MASS_V2_PHYSICAL_CHECKLIST.md` (fora do Git, no checkout principal).
4. **Amostragem ≠ auditoria completa:** as validações acima confirmam a preservação funcional por amostras, não a correção de todos os vínculos jurídicos.
5. Itens menores conhecidos: breves flashes brancos em transições que usam DISPOFF (abertura/fechamento do splash); a linha `[LEXUSB]` só aparece
   se a porta USB estiver aberta no fim do boot.
