# A3B-PREP REPORT: schema v3, flash integrity policy and verified rollback (no physical write)

- **Mission:** `LEX_MACHINA_DEVICE_INTEGRATION_V1_A3B_PREP`, 2026-09-29.
- **HEAD at start:** `92e1833e77bddda5331a628c82d47fe8d9b1ef87` (tag `lex-device-v1-sd-deployed-2026-09-29`).
- **Hardware operations:** only `read-flash` (esptool v5.4.0). No `write-flash`, `erase-flash` or upload. The SD card was not accessed.

## 1. Why the first A3B was blocked (confirmed)

1. **Flash differed from the A2 backup.** The 16 MB read was not identical to `061849a3…`. The whole difference was 1.966 bytes in NVS (`phy/cal_data`, RF calibration rewritten by ESP-IDF when BLE starts at boot). Details: `FLASH_DEPLOY_A3B_REPORT.md`.
2. **Committed firmware incompatible with the SD overlay.** The candidate at `c1fb3dfd` accepted only `DEVICE_VERSION|2`, but the `LEXV1.VER` on the SD is version 3. On the device, all V1 layers would have been disabled.

## 2. New integrity policy

`FLASH_INTEGRITY_POLICY.md` classifies every region of the flash:
- `IMMUTABLE_CRITICAL`: bootloader, partition table, active app, secondary app, otadata, spiffs;
- `MUTABLE_PERSISTENT`: nvs, accepted only when every changed key is decoded and on the allow-list, currently `phy/cal_*`;
- `DIAGNOSTIC_CONDITIONAL`: coredump, which gives `REVIEW`;
- `UNPARTITIONED`: 4 MB–16 MB, which blocks on any change.

The verdict is fail closed. The tool is `tools/flash_region_diff.py`; it re-parses the partition table from the current dump and validates its MD5.

## 3. Flash reads and region diff

**The two reads:**

| Read | File (outside Git) | sha256 |
|---|---|---|
| Pre-A3B (first A3B attempt) | `backups/esp32_a3b/pre_a3b_full_flash_16MB.bin` | `0240373663354a600240c15ca22384cdbea3bb3cc99166c717ae1963a884ef05` |
| PREP, second read (`--after no-reset`) | `backups/esp32_a3b/prep_read2_full_flash_16MB.bin` | `0240373663354a600240c15ca22384cdbea3bb3cc99166c717ae1963a884ef05` |

- The two reads are **identical**. The pre-A3B → PREP comparison gives verdict `PASS` with 0 differing bytes.
- The device stayed in the bootloader between the PREP reads (the app did not run), so NVS could not be rewritten between them.

**Region by region against `LEGACY_BASELINE_FLASH_BACKUP` (`061849a3…`).** The full detail is in `FLASH_REGION_DIFF_REPORT.json`; verdict **PASS**.

| Region | Offset | Size | Equal | Changed bytes | Class |
|---|---|---|---|---|---|
| bootloader | 0x0 | 0x8000 | yes | 0 | IMMUTABLE_CRITICAL |
| partition_table | 0x8000 | 0x1000 | yes | 0 | IMMUTABLE_CRITICAL |
| nvs | 0x9000 | 0x5000 | **no** | **1.966** | MUTABLE_PERSISTENT: `phy/cal_data` → `ALLOWED_EXPLAINED` |
| otadata | 0xE000 | 0x2000 | yes | 0 | IMMUTABLE_CRITICAL |
| app0 (ACTIVE_APP) | 0x10000 | 0x140000 | yes | 0 | IMMUTABLE_CRITICAL |
| app1 | 0x150000 | 0x140000 | yes | 0 | IMMUTABLE_CRITICAL |
| spiffs | 0x290000 | 0x160000 | yes | 0 | IMMUTABLE_CRITICAL |
| coredump | 0x3F0000 | 0x10000 | yes | 0 | DIAGNOSTIC_CONDITIONAL |
| unpartitioned | 0x400000 | 0xC00000 | yes | 0 | UNPARTITIONED |

- **No divergence outside NVS.** The latest dump is classified as `PRE_A3B_FULL_FLASH_BACKUP_VERIFIED`, with manifest `backups/esp32_a3b/PRE_A3B_BACKUP_MANIFEST.json`.
- **The original A2 dump is untouched.** It stays in place as `LEGACY_BASELINE_FLASH_BACKUP`, and no backup was overwritten.

## 4. Snapshots for rollback (outside Git)

| Snapshot | File | Offset / size | sha256 | Direct read |
|---|---|---|---|---|
| `NVS_PRE_A3B` | `backups/esp32_a3b/nvs_pre_a3b.bin` | 0x9000 / 0x5000 | `3f53eb85502a85fb9e30e31ae1f55e25ca31768407ee6326e07f4873fe3592c0` | `read-flash 0x9000 0x5000` **BYTE_IDENTICAL** |
| `LEGACY_APP0_PARTITION` | `backups/esp32_a3b/legacy_app0_partition.bin` | 0x10000 / 0x140000 | `ab6d4ffc8c4063139d93fae330d860b70a1ec97380ce371b1d6f1ce1eb181c1f` | `read-flash 0x10000 0x140000` **BYTE_IDENTICAL**, and equal to app0 of the A2 baseline |

The restore order (app only → PRE_A3B → historical baseline) is in `ROLLBACK_PLAN.md`.

## 5. Partition table: re-parsed from the current dump (MD5 `972dae2ff872a0142d60bad124c0666b` valid)

| Name | Type/subtype | Offset | Size |
|---|---|---|---|
| nvs | data/nvs | 0x9000 | 0x5000 |
| otadata | data/ota | 0xE000 | 0x2000 |
| app0 | app/ota_0 | 0x10000 | 0x140000 |
| app1 | app/ota_1 | 0x150000 | 0x140000 |
| spiffs | data/spiffs | 0x290000 | 0x160000 |
| coredump | data/coredump | 0x3F0000 | 0x10000 |

- **otadata:** sector 0 has seq=1 with a valid CRC (`esp_rom_crc32_le(UINT32_MAX)`), so the active app is **app0**.
- **app1:** does not contain a valid image (magic 0xA2).

## 6. Schema fix (firmware `lex_device_v1.h`)

- A single constant, `#define LEX_DEVICE_SCHEMA_VERSION 3`, is used by the parser, the diagnostic and the compatibility checks.
- `lexv1ParseDeviceVersionLine`:
  - requires exactly `#LEXMACHINA|DEVICE_VERSION|<decimal digits>`, with no extra fields;
  - `lexv1ReadVersion` then accepts **only** `== LEX_DEVICE_SCHEMA_VERSION`. There is no `2 OR 3`, no `>= 3` and no fallback.
- **Cross test** (`tests/test_a3b_prep.py`), all equal to 3:
  - `SCHEMA` in `build_sd_staging.py`;
  - `LEX_DEVICE_SCHEMA_VERSION`;
  - the first line of the staged `LEXV1.VER`;
  - `schema_version` in the manifest.
- **On-device self-test** at boot, run on the real C++ code with in-memory buffers:
  - accepts schema 3;
  - rejects 2, 4, 30 and `3|X`.

  There is no C++ compiler on the host (Windows App Control), so on the host the rule is checked statically and against a Python mirror.
- `DEVICE_DATA_CONTRACT_V1.md` now says `DEVICE_VERSION 3` and `TARGETS 3`.

## 7. Serial diagnostic, read-only (`lexV1DiagnosticoBoot`, only with `LEX_DEVICE_V1_ENABLED=1`)

Output lines: `LEXV1: CHECK PASS|FAIL <name> …`, then the summary `LEXV1: DIAG RESULT PASS|FAIL pass=N fail=M`.

**What it checks:**
1. **LEXV1.VER and DEVICE_VERSION:** exactly 3, plus the self-test of 2, 3, 4, 30 and `3|X`.
2. **Runtime:** size and streaming sha256 compared with LEXV1.VER; the result is `RUNTIME_HASH_MATCH`.
3. **Pinned runtime:** the runtime pinned in the firmware compared with LEXV1.VER.
4. **TEXT_MAP guard:** status `RUNTIME`, `SOURCE_BYTES`/`SOURCE_SHA256` equal to the runtime that was read, and the TEXT_MAP file's sha256 compared with the pinned value.
5. **Wrong-sha guard:** the lookup must return `FAIL_SOURCE_MISMATCH` with no target.
6. **TEXT → TARGET:**
   - the position of art. 114, VIII is located in the runtime only by the structural labels `Art. 114.` and `VIII - `;
   - the TEXT_MAP lookup at that offset must return `CF88:ART.114:INC.VIII`;
   - the start of the ADCT must return `ADCT`.
7. **Indices:** target table, ENTENDA lookup and payload, REF lookup and payload.

**Queries** (expected values cross-checked against the simulator in the tests):

| Target | Expected resolution | Anchor | Refs (visible) |
|---|---|---|---|
| CF88:ART.5:INC.V | COVERED_BY_BLOCK | CF88:ART.5:INC.IV | 1 (1) |
| CF88:ART.21:INC.XXIV | DIRECT | self | 0 |
| CF88:ART.22:INC.XXIX | DIRECT | self | 0 |
| CF88:ART.24:PAR.4 | COVERED_BY_BLOCK | CF88:ART.24:PAR.3 | 0 |
| CF88:ART.37:PAR.6 | DIRECT | self | 5 (5) |
| CF88:ART.60:PAR.4:INC.IV | DIRECT | self | 0 |
| ADCT:ART.10:INC.II | DIRECT | self | 0 |
| CF88:ART.114:INC.VIII | NONE (valid target) | — | 2 (0), known issue: historical references hidden |
| CF88:ART.25 | NONE (valid target) | — | 1 (1) |
| CF88:ART.999 | INVALID_OR_UNKNOWN_TARGET | — | — |

**Other checks:**
- **BLOCK:** the target and its anchor must point to the **same** `offset/length` in the payload, so the payload is not duplicated.
- **References:**
  - zero results: `CF88:ART.21:INC.XXIV`;
  - one result: `CF88:ART.25`;
  - several results: `CF88:ART.37:PAR.6`, 5.

  Only count, offset and parsing are validated: 7 fields, same TARGET_ID. Editorial content is never checked.

**Timings (`micros()`):**
- opening the indices;
- the runtime sha256;
- the TEXT_MAP lookup;
- per query: target table, ENTENDA lookup, full ENTENDA, payload seek/read, references;
- BLOCK resolution.

**Memory** (`ESP.*`), before and after DEVICE V1:
- heap: free, minimum, largest block;
- PSRAM: total, free, minimum.

No allocation is made just to measure.

**Read-only guarantee:**
- every `SD.open` uses `FILE_READ`;
- no `FILE_WRITE`/`APPEND`, no `mkdir`/`remove`/`rename`/`rmdir`, no `.write(` in the DEVICE V1 code. This is checked by a static test.

## 8. Build (arduino-cli 1.5.1, core esp32 3.3.11). Nothing was flashed.

**Command:**

```
arduino-cli compile --fqbn esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default --build-path <dir> \
  [--build-property "compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1"] firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE
```

**Build settings:**
- Board: ESP32S3 Dev Module.
- PSRAM: OPI. The legacy build uses the same setting, and the physical app header matches.
- Flash: size 4MB, mode DIO, frequency 80m, as given by `flash_args`. The app image header is identical to the physical app0 (mode 2, size/freq 0x2F).
- Partition scheme: `default`. The generated `partitions.csv` is identical to the physical table.
- Other options: CPU 240 MHz, USB Mode HW CDC, CDC on boot disabled.
- Flag default: `LEX_DEVICE_V1_ENABLED 0` in versioned code. It is enabled only by a build property.

**Results:**

| Build | Program | Static RAM | App .bin | sha256 |
|---|---|---|---|---|
| flag 0 | 989.395 B (same size as v7.12.0) | 124.452 B | 989.536 B | `c6a27231e534a78196df3e93748dc74465473b4cba5ae182a409dca07a283cb8` |
| flag 1 | 1.003.787 B | 124.460 B | **1.003.936 B** | **`04cb218a3cacba29b78a65897547d19383c85564b6db8e62d2c2fc2f8a388b1c`** |

**Generated artifacts** (saved to `backups/esp32_a3b/candidate_flag{0,1}/`, outside Git; none of them was flashed):
- `LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin` (app);
- `.bootloader.bin`;
- `.partitions.bin`;
- `flash_args`;
- `partitions.csv`;
- `build.options.json`.

`.merged.bin` (4 MB) was ignored.

**Proof of the app offset (all three sources agree):**
1. **Physical partition table** (current dump): `app0` = ota_0 at **0x10000**, size 0x140000, active according to otadata.
2. **Build partition scheme:** the generated `partitions.csv`/`.partitions.bin` has `app0` at 0x10000, and `.partitions.bin` is **byte-identical** to 0x8000–0x8BFF of the physical flash (the rest of the sector is 0xFF). The build bootloader is also byte-identical to the physical one.
3. **Build `flash_args`:** `0x10000 LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin`. It also lists `0x0` bootloader, `0x8000` partitions and `0xe000 boot_app0.bin`; **none of these will be written**.

→ **`VERIFIED_APP_OFFSET = 0x10000`**

**The candidate is an APP BINARY only** (`esptool image-info`):
- magic 0xE9, 6 segments, entry 0x40375DA8, chip ID 9 (ESP32-S3);
- checksum valid, validation hash valid, app descriptor present (ESP-IDF v5.5.5);
- not a merged image, bootloader, partition table, otadata or filesystem.

**Size:** 1.003.936 B < 0x140000 (1.310.720 B), so **it fits in app0** with 306.784 B to spare.

**Source-to-binary link:**
- the `.ino`/`.h` sources were last modified at 17:17 and the build ran at 17:25;
- the build used exactly the files being committed in this PREP;
- source sha256 at build time: `.ino` `00dc13da…bace`, `lex_device_v1.h` `4594cbc7…01fa`.

**Flag 0:** same program size as v7.12.0 (989.395 B) and the same static RAM. The DEVICE V1 code is not compiled in. Known limitation: the `.bin` is not byte-identical to the physical legacy app, because the build environment and path strings differ. The functional rollback uses the `LEGACY_APP0_PARTITION` snapshot, not a rebuild.

## 9. Tests

| Suite | Result |
|---|---|
| DEVICE | 53/53 (39 existing + 14 new in `test_a3b_prep.py`) |
| ENTENDA | 80/80 |
| LEGAL_TARGET_ID | 47/47 |

**New tests:**
- builder SCHEMA equal to firmware SCHEMA, and the exact rule (2 and 4 rejected, 3 accepted);
- a single constant, with no version literal;
- flag default 0;
- the 10 queries with expectations equal to the simulator;
- BLOCK without a duplicated payload;
- 114.VIII by offset;
- references zero, single and multiple;
- runtime and TEXT_MAP guards;
- timing and memory instrumentation;
- SD read-only audit;
- integrity policy: the real diff is confined to explained NVS; any flipped byte in bootloader, app0, app1, spiffs, otadata or the unpartitioned area gives BLOCK; coredump gives REVIEW; NVS with an empty allow-list gives BLOCK.

**Adjusted test:** `test_deterministic_rebuild`. It compared a fresh build against the staging deployed to the SD, which was built at c1fb3dfd. Now it ignores **only** the build-provenance fields: `GIT_COMMIT` in the VER, and in the manifest `git_commit`, `git_tags_at_commit`, `build_date` (the commit time) and the VER hash. All legal content, indices and ENTENDA/References are still compared byte for byte.

## 10. What was not done

- No flash write, erase or upload; bootloader, partitions, NVS, otadata and spiffs were not changed.
- The SD card was not accessed or changed.
- No new UI.
- The feature flag stays off in versioned code.
