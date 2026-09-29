# FLASH INTEGRITY POLICY (DEVICE V1, since A3B-PREP)

- **Scope:** every read and write operation on the flash of the physical ESP32-S3 (16 MB).
- **Tool:** `tools/flash_region_diff.py`, run on the host against full dumps.
- **Rule:** fail closed. Any difference outside a region explicitly classified **and** explained **blocks** the operation.

## Why the policy exists

In the first A3B, a new 16 MB read differed from the A2 backup (`061849a3…`) by 1.966 bytes, all inside NVS. Every difference was in the `phy/cal_data` entry (RF calibration), which ESP-IDF rewrites when the radio (BLE) is initialised at boot.

Requiring the SHA-256 of the whole flash to stay equal between boots is therefore not a valid condition for a deploy. Ignoring differences without a classification is not valid either.

## Classification of regions

The partition table is always **re-parsed from the current dump**; any MD5 mismatch is a failure. Every byte of the flash belongs to exactly one region.

| Class | Regions (current device) | Rule |
|---|---|---|
| **IMMUTABLE_CRITICAL** | `bootloader` 0x0–0x8000; `partition_table` 0x8000–0x9000; **active app** before the deploy (`app0` 0x10000, 0x140000, chosen by otadata seq=1); **secondary app** when unused (`app1` 0x150000, 0x140000); `otadata` 0xE000, 0x2000 (except an intentional change); filesystem `spiffs` 0x290000, 0x160000 (except an explicitly authorised operation) | Any difference **BLOCKS**. |
| **MUTABLE_PERSISTENT** | `nvs` 0x9000, size 0x5000 | A difference is accepted (`ALLOWED_EXPLAINED`) only if **every** changed NVS entry is decoded (namespace + key) **and** is on the explicit allow-list. Anything else is `BLOCK_UNEXPLAINED_NVS_CHANGE`. |
| **DIAGNOSTIC_CONDITIONAL** | `coredump` 0x3F0000, 0x10000 | A difference gives `REVIEW`: it is reported and never silently accepted. A new coredump means a panic, which must be investigated. |
| **UNPARTITIONED** | 0x400000–0x1000000 (12 MB outside the table) | Any difference **BLOCKS**. |

**NVS allow-list** (`NVS_ALLOWED` in the tool):
- `phy/cal_data`, `phy/cal_mac`, `phy/cal_version`: RF calibration, rewritten by ESP-IDF at radio init.
- **This is not a generalisation.** "Any difference in NVS is always safe" is wrong. Keys such as `nimble_bond` (BLE pairing), the security keys, or the application's own settings are **not** on the list, and any change to them blocks until a human reviews it.
- Expanding the allow-list requires a written explanation in this document plus a test.

## What gets recorded per region

Each region records:
- `name`, `offset`, `size`;
- `sha256_original` and `sha256_current`;
- `equal`, `changed_bytes`, `classification`;
- for NVS, `changed_nvs_keys` (namespace/key), `nvs_verdict` and `unexplained`.

Output: `FLASH_REGION_DIFF_REPORT.json`.

## Mandatory procedure before any flash write

1. Identify the device: chip, revision, flash size, PSRAM and MAC.
2. Make a new full read. Leave the device in the bootloader (`--after no-reset`) between reads, so the app does not run and does not rewrite NVS.
3. Compare region by region against the latest verified reference. The verdict must be `PASS`.
4. **Always take an NVS snapshot** (0x9000, 0x5000) before the operation, confirmed by a direct read.
5. Take a snapshot of the active app partition, confirmed by a direct read.
6. Write **only** the authorised region. After the write, read back and repeat steps 2–3, where the only allowed difference is the region written.

## Backup hierarchy (never overwrite)

| Identifier | File (outside Git, `DEVICE_INTEGRATION/backups/`) | sha256 |
|---|---|---|
| `LEGACY_BASELINE_FLASH_BACKUP` | `esp32/raw_flash_16MB_read1.bin` (A2) | `061849a357d77f571d735a108fc5f4a032d7c12e4f7e3c8f3b34c0f3357d6727` |
| `PRE_A3B_FULL_FLASH_BACKUP_VERIFIED` | `esp32_a3b/pre_a3b_full_flash_16MB.bin`, confirmed by `prep_read2_full_flash_16MB.bin` | `0240373663354a600240c15ca22384cdbea3bb3cc99166c717ae1963a884ef05` |
| `NVS_PRE_A3B` | `esp32_a3b/nvs_pre_a3b.bin` (0x9000, 0x5000) | `3f53eb85502a85fb9e30e31ae1f55e25ca31768407ee6326e07f4873fe3592c0` |
| `LEGACY_APP0_PARTITION` | `esp32_a3b/legacy_app0_partition.bin` (0x10000, 0x140000) | `ab6d4ffc8c4063139d93fae330d860b70a1ec97380ce371b1d6f1ce1eb181c1f` |

Restore order: see `ROLLBACK_PLAN.md`. App only first, then PRE_A3B, then the historical baseline. This avoids restoring an old NVS unnecessarily.
