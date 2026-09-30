# A3B-PREP2 REPORT: bounded SD file handles for DEVICE V1 (no physical write)

- **Mission:** `LEX_MACHINA_DEVICE_INTEGRATION_V1_A3B_PREP2`, 2026-09-29.
- **HEAD at start:** `868c24ee05d5e10e9bb98d52bd53eecb7cc52ba5` (tag `lex-device-v1-a3b-ready-2026-09-29`).
- **Hardware:** not touched (no esptool command, no serial). The ESP32 stays on v7.12.0 after the A3B-FLASH rollback. The SD card was not accessed.

## 1. The physical failure (A3B-FLASH, recorded in `FLASH_DEPLOY_A3B_REPORT.md`)

**What worked:**
- The write was app-only at 0x10000, the readback was byte-identical, and the pre-boot diff showed only app0 changed.
- The first boot was stable, the SD mounted, and `DEVICE_VERSION 3` was accepted.

**What failed:**
- `vfs_fat: open: no free file descriptors`: the payloads, the runtime and the TEXT_MAP hash could not be opened.
- The valid runtime was therefore refused (fail closed).
- An app-only rollback followed. The flash is identical to PRE_A3B (`02403736…`) and the v7.12.0 firmware is running (JUR CACHE 178/296).

**Correction made in this mission.** A careful re-read of the serial log shows **5 successful opens**: VER, TARGETS, TEXT_MAP, ENTENDA_LOOKUP and REF_LOOKUP, all with status OK. After them come 5 `no free file descriptors` errors: ENTENDA_PAYLOAD, REF_PAYLOAD, the runtime sha, the TEXT_MAP sha and the text-position search.

So at boot the legacy firmware held **0** handles, and DEVICE V1 alone (7 persistent, 10 opens) exceeded the core default of 5. The earlier line of the A3B report ("4 opens, legacy probably keeps 1") was corrected in the report itself. The legacy `File` objects are all local and closed at the end of their functions (audited: 13 functions with `SD.open` + `close()`, plus directory `openNextFile()` calls).

## 2. `SD.begin`: real signature and arguments

**Core esp32 3.3.11, `libraries/SD/src/SD.h`:**

```cpp
bool begin(uint8_t ssPin = SS, SPIClass &spi = SPI, uint32_t frequency = 4000000,
           const char *mountpoint = "/sd", uint8_t max_files = 5, bool format_if_empty = false);
```

**v7.12.0 call (`iniciarSDUmaVez()`):**
- `SD.begin(SD_CS=4, spiBus=SPIClass(FSPI), 12000000)`, with a retry after `SD.end()` at 4 MHz;
- implicit mountpoint `/sd`, `max_files=5`, `format_if_empty=false`.

**Change:**
- **Flag 0:** the original call, unchanged.
- **Flag 1:** `SD.begin(SD_CS,spiBus,12000000|4000000,"/sd",LEXV1_SD_MAX_FILES=12,false)`. Pin, bus, frequencies and mountpoint are the same; `format_if_empty=false` is explicit, and DEVICE V1 never formats.

## 3. New handle lifecycle (details: `FILE_DESCRIPTOR_POLICY.md`)

| | Old flow (candidate `04cb218a`) | New flow (PREP2) |
|---|---|---|
| SD `max_files` | 5 (default) | **12** (flag 1 only) |
| Handles kept open together | 7 (VER, TARGETS, TEXT_MAP, ENTENDA_LOOKUP, ENTENDA_PAYLOAD, REF_LOOKUP, REF_PAYLOAD), plus 3 temporary | **3** in steady state (TARGETS, ENTENDA_LOOKUP, REF_LOOKUP) |
| Diagnostic peak | 7–8 required, 5 achieved (then failure) | **4** (3 + 1 on-demand payload); ceiling 6 |
| Headroom (12 − legacy − peak) | — | 8 with today's legacy (0); **4** with the assumed reserve of 2 and the ceiling of 6 |

**Short-lived files** (open → read → close):
- `LEXV1.VER`;
- `CF88_RUNTIME.txt`, for the sha256 and for the structural search for the position of art. 114, VIII;
- `CF88_TEXT_MAP.IDX`, for the sha256, and then as an index only during the guards and the TEXT→TARGET lookups, closed before the steady set opens.

**On demand:**
- `ENTENDA_PAYLOAD.DAT` opens only if the lookup has a row;
- `REF_PAYLOAD.IDX` opens only if `QUANTIDADE > 0`;
- both close at the end of each query and after the BLOCK anchor.

A zero-result reference query or a target without ENTENDA opens no payload. There are never two handles to the same file.

**Strategy B** (the 3 small indices open, payloads on demand) was chosen over A (open/close per lookup):
- the latency of the lookups is kept (no `open` per query on the indices);
- only 3 persistent handles, about 18 KB of internal heap at the ~6,2 KB/handle measured in A3B-FLASH.

**Tracker** (`LexV1FileReader`, flag 1 only):
- `LEXV1: OPEN <TIPO> <path> stage=<s> OPEN_COUNT=n MAX_OPEN_COUNT=m`;
- `LEXV1: CLOSE <path> OPEN_COUNT=n`;
- on failure: `LEXV1: FAIL_IO|<TIPO>|<path>|stage=<s>|open=<n>|max_open=<m>`.

**New checks:**
- `fd_steady_state`: at most 3;
- `fd_pico_e_fechamento`: MAX_OPEN_COUNT ≤ 6 and 0 open at the end.

**Categories printed on failure:** `FAIL_SCHEMA`, `FAIL_HASH`, `FAIL_IO`, `FAIL_PARSE`, `FAIL_TARGET`, `FAIL_REFERENCE`. A file that did not open is no longer reported as an "invalid runtime".

**Idea discarded during the mission:** a capacity probe (10 simultaneous transient opens of `LEXV1.VER`). It would cost about 60 KB of temporary heap and would break the "never two handles to the same file" rule, so it was removed before the final build. Headroom is proven by the tracker plus the policy arithmetic.

**Coverage preserved:**
- schema self-test 2/3/4/30/3|X, `LEXV1.VER`;
- `RUNTIME_HASH_MATCH`, pinned vs VER, TEXT_MAP sha256 and guards;
- TEXT→TARGET 114.VIII and ADCT;
- targets, the 10 queries, BLOCK without a duplicated payload, references zero/single/multiple;
- timings (the payload timing now includes the on-demand `open`), heap and PSRAM.

## 4. Build (arduino-cli 1.5.1, core esp32 3.3.11, `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default`)

| Build | Program | Static RAM | App .bin | sha256 |
|---|---|---|---|---|
| flag 0 | **989.395 B** (same as v7.12.0 and PREP) | 124.452 B | 989.536 B | `74032afc…5904`¹ |
| flag 1 PREP (`04cb218a`, rolled back) | 1.003.787 B | 124.460 B | 1.003.936 B | `04cb218a…8b1c` |
| **flag 1 PREP2** | **1.005.375 B** (+1.588 vs PREP) | **124.468 B** (+8) | **1.005.520 B** | **`d6b1bd05af3e6c71c74aaaddefa1b54af6f88890bffbe8517c63bd4a51e717be`** |

1. The flag 0 `.bin` differs byte for byte from the PREP one only by the embedded build metadata. The program size is identical, and no DEVICE V1 code is compiled with flag 0.

**What the delta is:**
- The +1.588 B of program and +8 B of static RAM come from the tracker, the lazy reader, the error categories and the FAIL_IO/OPEN/CLOSE messages.
- `max_files` is a **runtime** argument of `esp_vfs_fat_register`, so it has no static footprint. An attempted comparative build with `max_files=5` produced identical numbers, because the `-D` override has no effect on the macro; that comparison measured nothing.
- **Dynamic cost not yet measured** (to be done in the A3B retry):
  - VFS/FatFS reserves space in proportion to `max_files` at mount (`CONFIG_FATFS_SECTOR_4096`, `CONFIG_FATFS_PER_FILE_CACHE`, `CONFIG_FATFS_ALLOC_PREFER_EXTRAM`);
  - compare "Heap antes do BLE" and "PSRAM livre antes dos caches" against the legacy log (209.612 B / 8.334.248 B).

**Candidate v2**, outside Git: `DEVICE_INTEGRATION/backups/esp32_a3b_prep2/candidate_v2_flag1/candidate_app_v2.bin`.
- 1.005.520 B, sha256 `d6b1bd05…17be`.
- `esptool image-info`: app image, 6 segments, chip ID 9, DIO/80m/4MB (header identical to the physical app0), checksum 0xAC valid, validation hash valid, ESP-IDF v5.5.5.
- Not a merged image, not a bootloader, not a partition table.
- Size < 0x140000, with **305.200 B** to spare.
- `flash_args`: app at **0x10000**. The build `.partitions.bin` and `.bootloader.bin` are byte-identical to the physical flash (PRE_A3B dump). `VERIFIED_APP_OFFSET = 0x10000` is unchanged.
- **Source link:** the flag 1 build used `.ino` sha256 `845c577d3afaf3dc8746311bd7fe135a578a304870d596c48aabb976ddf2a83f` and `lex_device_v1.h` `6d326296a99a1bc35318e7a14377c206d436ae02f04c2b048bfee2e5b8f86ca7`. The copy in the build folder differs only by the `#line` directive added by arduino-cli. These are the files being committed.
- The previous candidate `backups/esp32_a3b/candidate_flag1/candidate_app.bin` (`04cb218a…`) was kept for audit, not overwritten.

## 5. Tests

| Suite | Result |
|---|---|
| DEVICE | **64/64**: 53 existing (2 names updated) + 11 new in `tests/test_a3b_prep2.py` |
| ENTENDA | 80/80 |
| LEGAL_TARGET_ID | 47/47 |

**New tests:**
- **SD mount:** the core signature; `SD.begin` of DEVICE V1 with `"/sd",LEXV1_SD_MAX_FILES,false` in both attempts; the legacy call unchanged; only 4 `SD.begin` in the sketch; no `format_if_empty=true`.
- **Policy constants:** firmware and model agree (steady 3 ≤ 4, peak 6, headroom 4).
- **FD model** (`tools/fd_model.py`):
  - the **old flow fails** with `max_files=5`: peak 5, failures ENTENDA_PAYLOAD, REF_PAYLOAD, runtime, TEXT_MAP sha and position search, exactly as in the log;
  - the **new flow passes** with 12: peak **4** ≤ 6, 0 at the end, no duplicates, headroom ≥ 4 even with a legacy reserve of 2;
  - with 5 and the reserve, the headroom would not be enough, which justifies raising `max_files`.
- **On demand:** 9 ENTENDA_PAYLOAD opens (7 targets with ENTENDA + 2 BLOCK anchors), 6 REF_PAYLOAD opens; zero-result does not open; every payload closes before the next open.
- **Source tied to the model:**
  - the order of `abrir`/`preparar` calls in the source matches the model;
  - reader declarations are limited to `ver`, `map` and `tgt, lk, rl, pl, rp`;
  - exactly 3 `"steady"`;
  - `ver.fechar()` right after the parse;
  - the runtime sha and the position search run before the indices open;
  - `map.fechar()` runs before the steady set;
  - `r.fechar()` in the sha and position helpers;
  - payloads are lazy.
- **Tracker:** the only `SD.open` in DEVICE V1 is the tracker's; `FAIL_IO` has type, path, stage, open and max_open; every `abrir` passes three arguments; all 6 categories are present.
- **Earlier diagnostics preserved.**
- **Read-only:** no `FILE_WRITE`, `FILE_APPEND`, `mkdir`, `remove`, `rename`, `rmdir`, `format`, `.write(`, `fopen` or file `print`.

## 6. What was not done

- No write-flash, upload or erase, and no serial access.
- The SD card was not accessed, renamed or formatted.
- No new UI. The flag stays 0 in versioned code.
