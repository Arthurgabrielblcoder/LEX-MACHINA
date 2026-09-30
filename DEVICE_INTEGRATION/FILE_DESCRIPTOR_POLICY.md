# FILE DESCRIPTOR POLICY: SD handles in DEVICE V1 (since A3B-PREP2)

## Values

| Parameter | Value | Where |
|---|---|---|
| `max_files` of the legacy SD mount (flag 0) | **5** (core default; the v7.12.0 call does not pass it) | `iniciarSDUmaVez()`, `#else` branch |
| `max_files` of the DEVICE V1 SD mount (flag 1) | **12** (`LEXV1_SD_MAX_FILES`) | `iniciarSDUmaVez()`, `#if LEX_DEVICE_V1_ENABLED` branch |
| `format_if_empty` | **false**, explicit in DEVICE V1. DEVICE V1 never formats the card. | same place |
| DEVICE V1 handles in steady state | **≤ 3** (`LEXV1_FD_STEADY_MAX`; the policy allows ≤ 4) | TARGETS, ENTENDA_LOOKUP, REF_LOOKUP |
| DEVICE V1 diagnostic peak | **≤ 6** (`LEXV1_FD_PEAK_MAX`); the current flow reaches **4** | steady set + 1 payload |
| Minimum headroom | **≥ 4** (`LEXV1_FD_HEADROOM_MIN`): 12 − legacy reserve (2) − DEVICE V1 peak ceiling 6 = **4**. With today's numbers: 12 − 0 observed at boot − peak 4 = **8** | |

**Core signature** (esp32 3.3.11, `libraries/SD/src/SD.h`):

```cpp
bool begin(uint8_t ssPin = SS, SPIClass &spi = SPI, uint32_t frequency = 4000000,
           const char *mountpoint = "/sd", uint8_t max_files = 5, bool format_if_empty = false);
```

**Current arguments:**
- CS = `SD_CS` (4);
- SPI = `spiBus` (`SPIClass(FSPI)`, shared with the ILI9341);
- frequency 12 MHz, with a retry at 4 MHz after `SD.end()`;
- mountpoint `/sd`.

DEVICE V1 changes only `max_files` and makes `format_if_empty=false` explicit. Pins, bus, frequencies and mountpoint are unchanged. With flag 0 the call stays exactly as in v7.12.0.

## Why the default 5 failed (A3B-FLASH, 2026-09-29)

- **The legacy code was not the cause.** At that point it held **0** handles: all its `File` objects are local and closed at the end of their function. The serial log shows 5 DEVICE V1 opens succeeding (VER, TARGETS, TEXT_MAP, ENTENDA_LOOKUP, REF_LOOKUP).
- For the headroom calculation, a **legacy reserve of 2** is assumed anyway: the reader file plus one index or directory opened by the legacy UI while DEVICE V1 is active.
- The candidate `04cb218a` opened VER, TARGETS, TEXT_MAP, ENTENDA_LOOKUP, ENTENDA_PAYLOAD, REF_LOOKUP and REF_PAYLOAD, and kept them all open. It then opened CF88_RUNTIME and TEXT_MAP again for the sha256 calculations, 9 opens in total.
- From the 5th handle on: `vfs_fat: open: no free file descriptors`. The payloads and the runtime did not open, the fail closed refused the valid runtime, and the app-only rollback was run.

## Why raising `max_files` alone is not enough

1. **Every open handle costs heap.** The FatFS in this build uses `CONFIG_FATFS_SECTOR_4096` and `CONFIG_FATFS_PER_FILE_CACHE`, so each `FIL` carries a 4 KB buffer. On top of that come the Arduino/newlib buffers. In A3B-FLASH, internal heap fell from 136.988 to 112.172 B (−24,8 KB, about **6,2 KB per open file**) and the largest block went from 90.100 to 69.620 B. Nine handles kept open would be about 56 KB, on a heap that has about 137 KB after BLE.
2. **`max_files` also reserves space at mount.** In ESP-IDF, `esp_vfs_fat_register` reserves space in proportion to `max_files`, with `CONFIG_FATFS_ALLOC_PREFER_EXTRAM=1`. The real cost of 12 vs 5 (heap/PSRAM at mount) must be **measured in the next A3B**, comparing "PSRAM livre antes dos caches" and "Heap antes do BLE" with the legacy log. It is not assumed to be irrelevant.
3. **Handles are shared with the legacy code and the future UI.** The reader, jurisprudence and Relations code open their own files. Without a narrow lifecycle, any future DEVICE V1 growth would eat the headroom again.

## Lifecycle (flag 1)

| Handle | File | Opens at | Closes at | Persistent? | Needs to be persistent? | Concurrent with |
|---|---|---|---|---|---|---|
| `ver` | `/99_LEX_V1/00_SYS/LEXV1.VER` | stage `version` | right after the parse (`ver.fechar()`) | no | no | — (only one open) |
| `r` (sha) | `/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt` | stage `runtime_sha256` | end of the streaming (`lexV1Sha256Arquivo`) | no | no | — |
| `r` (sha) | `/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX` | stage `text_map_sha256` | end of the streaming | no | no | — |
| `r` (position) | `CF88_RUNTIME.txt` | stage `text_position` (structural labels of art. 114, VIII) | end of the search (`lexV1OffsetEstrutural`) | no | no | — |
| `map` | `CF88_TEXT_MAP.IDX` | stage `text_map_index` | after the guards and the TEXT→TARGET lookups (`map.fechar()`) | no | no; reopen when needed | — |
| `tgt` | `/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX` | stage `steady` | end of the diagnostic | **yes** | yes: used by every query | lk, rl, + 1 payload |
| `lk` | `/99_LEX_V1/30_ENTENDA/ENTENDA_LOOKUP.IDX` | stage `steady` | end of the diagnostic | **yes** | yes | tgt, rl, + 1 payload |
| `rl` | `/99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX` | stage `steady` | end of the diagnostic | **yes** | yes | tgt, lk, + 1 payload |
| `pl` | `/99_LEX_V1/30_ENTENDA/ENTENDA_PAYLOAD.DAT` | **on demand**: only when the ENTENDA lookup has a row (lazy reader, `preparar`) | end of the query, and after the BLOCK anchor (`pl.fechar()`) | no | no | tgt, lk, rl |
| `rp` | `/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX` | **on demand**: only when `QUANTIDADE > 0` | end of the query | no | no | tgt, lk, rl |

**Rules:**
- **MAX_CONCURRENT_SET** = {tgt, lk, rl, pl} or {tgt, lk, rl, rp}. The peak is 4.
- There are never two handles to the same file.
- A zero-result reference query or a target without ENTENDA **does not open** a payload.
- Strategy B was chosen: keep open only the 3 small indices used in every query, and open the large payloads on demand. That keeps lookups without an `open` (which costs milliseconds on the SD) and at most 4 handles, about 25 KB of heap.
- Strategy A (open/close per lookup) stays available if heap becomes more critical than latency. It gets measured when the UI goes in.

## Instrumentation (flag 1 only, serial)

**Tracker lines:**
- `LEXV1: OPEN <TIPO> <path> stage=<stage> OPEN_COUNT=n MAX_OPEN_COUNT=m`
- `LEXV1: CLOSE <path> OPEN_COUNT=n`

**Open failure:** `LEXV1: FAIL_IO|<TIPO>|<path>|stage=<stage>|open=<n>|max_open=<m>`.

**Checks:**
- `fd_steady_state`: OPEN_COUNT ≤ 3 after the steady set opens;
- `fd_pico_e_fechamento`: MAX_OPEN_COUNT ≤ 6 and OPEN_COUNT = 0 at the end.

**Failure categories:** `FAIL_SCHEMA`, `FAIL_HASH`, `FAIL_IO`, `FAIL_PARSE`, `FAIL_TARGET`, `FAIL_REFERENCE`.

## Regression guards (`tests/test_a3b_prep2.py`)

- **Model** (`tools/fd_model.py`): replays the OPEN/CLOSE sequence against `max_files` with 1 handle taken by the legacy code.
  - The old flow **fails** with 5.
  - The new flow **passes** with 12, with peak 4, steady set = the 3 indices, 0 handles at the end, no duplicates and headroom ≥ 4.
- **Source:** the order of `abrir`/`preparar` calls in the source must match the model.
- **Scope:** only `ver`, `map` and `tgt, lk, rl, pl, rp` are declared at function scope.
- **Payloads:** they are lazy and never opened by `abrir`.
- **Tracker coverage:** the only `SD.open` in DEVICE V1 is the tracker's.
- **Read-only:** no `FILE_WRITE`, `FILE_APPEND`, `mkdir`, `remove`, `rename`, `format`, `.write(` or file `print`.
- **Mount:** `SD.begin` of DEVICE V1 is `(SD_CS,spiBus,12000000|4000000,"/sd",LEXV1_SD_MAX_FILES,false)`, and the legacy call is unchanged.
