# LEGACY SD / FLASH BACKUP REPORT

## V1-A2B (2026-09-29) — cartão SD: `BACKUP_VERIFIED`

**Identificação** (somente leitura, `Get-Volume`/`Get-Disk`):

| Item | Valor |
|---|---|
| Volume removível | D:, FAT32, sem rótulo |
| Capacidade | 31.902.400.512 B |
| Livres | 31.843.516.416 B |
| Disco | Generic STORAGE DEVICE (USB), 31.914.983.424 B |

**Assinatura forte**, presente e em um único candidato, o que classifica o volume como **PROBABLE_LEX_MACHINA_SD**:
- `/99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX`;
- `/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX`;
- pasta `/1- CONSTITUIÇÃO FEDERAL`.

**Estrutura:** 54 entradas na raiz, sendo as pastas das normas `1-` a `42-` e as de índices:
- `99_INDICES`, `99_INDICES_ESP32`, `99_INDICES_ESP32_V4_TESTE`, `_V5_TESTE`, `_V6_TESTE`;
- `99_JURISPRUDENCIA_V2`;
- `99_LEXDATA_ESP32_OFICIAL_V4_TESTE`;
- `99_RELATIONS_V1`, `99_RELATIONS_V2`.

**Backup:** `DEVICE_INTEGRATION/backups/sd_20260929T163407Z/`, ignorado pelo Git.
- **Conteúdo:** `data/` (cópia integral), `manifest.json` e `VERIFICATION.json`.
- **Ferramenta:** `tools/backup_sd_readonly.py`. Ela abre a origem só em modo `rb` e só grava no destino, preservando mtime/atime na cópia. No cartão nada foi criado, alterado, renomeado ou apagado.
- **Contagem:** 1.062 arquivos, 24.574.047 bytes e 0 erros de leitura.
- **Hash agregado:** `f00e6d562f239b23c033844b879a9afdf2b878980550068e3acc4101bad49b38`. É o sha256 das linhas `path\tsize\tsha256\n`. O próprio `manifest.json` tem sha256 `980173398de9dfa283e6651d9cba215c2f33ddb7fa4d28ff11239d71a926c36a`.
- **Verificação independente:** uma segunda passagem conferiu origem e cópia, arquivo por arquivo, pelo conjunto de arquivos, tamanho e sha256, com 0 divergências. Resultado: **`BACKUP_VERIFIED`**.

**CF física.** `PHYSICAL_CF_CLASSIFICATION = MATCH_UPDATER_CF_BODY`.
- Arquivo: `/1- CONSTITUIÇÃO FEDERAL/cf.txt`, com 429.242 B e sha256 `d8469e18e45e027872f04bc56ba1076bcc6d1bb3295c71173bd5b728b22dca6e` (mtime 13/09 16:23).
- É idêntico byte a byte a `updater/saida/99_INDICES/CANDIDATOS_RECUPERACAO_3/CF88.txt`, gerado por `recuperar_3_definitivo.py`.
- É o corpo de `updater/saida/…/constituicao_federal_1988.txt` sem o cabeçalho LEX de 590 B, e é igual à CF monovigente ingerida hoje (norma 579494) mais o `\n` final.
- **Não** é o `cf.txt` legado (928.009 B, `d9f3d6b9…`). O TEXT_MAP da A1, vinculado ao legado, nunca teria casado com o cartão, então o fail closed da A2 estava correto.
- Difere do `CF88_RUNTIME.txt` (587.133 B, `7ef82290…`): o runtime tem cabeçalhos juntados, o § 4º do art. 239 separado e o ADCT anexado.

**Índices legados no cartão:**
- `REL_LOOKUP.IDX`: 41 linhas (limite 64), sha `863ff538…`, igual aos pacotes 2E5/2E6;
- `EXT_NORMAS.IDX`: 20 linhas (limite 32);
- `JUR_LOOKUP.IDX`: sha `7931e28e…`, igual ao J4 (178 chaves).

## V1-A2 (2026-09-29) — flash do ESP32: `PHYSICAL_FLASH_BACKUP_VERIFIED`

**Porta e ferramentas.**
- Porta COM3, ponte CH343 (`USB\VID_1A86&PID_55D3`).
- `esptool v5.4.0`: só `flash-id` e `read-flash`.

**Identificação.**
- Chip: ESP32-S3 (QFN56), revisão v0.2, PSRAM de 8 MB, MAC `e0:72:a1:f4:fd:28`.
- Flash: fabricante 0x68, device 0x4018, **16 MB**.

**Dump.**
- Tamanho: 16.777.216 B.
- sha256: `061849a357d77f571d735a108fc5f4a032d7c12e4f7e3c8f3b34c0f3357d6727`.
- Verificação: segunda leitura completa, idêntica.
- Local: `DEVICE_INTEGRATION/backups/esp32/`.

**Firmware:** `PHYSICAL_FIRMWARE_CONFIRMED_V7_12_0`. Evidências:
- banner serial;
- string na flash no offset 0x11385;
- partições default de 4 MB.

## V1-A1

Nenhum hardware conectado. O backup parcial preexistente é `updater/backup_sd/microSD_20260916_223312_378647/` (736 KB).
