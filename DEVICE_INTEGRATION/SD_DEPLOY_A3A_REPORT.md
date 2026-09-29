# SD DEPLOY A3A REPORT: overlay /99_LEX_V1 on the physical microSD

**Result:** `OVERLAY_VERIFIED_ON_SD` and `LEGACY_CHANGED = 0`.

| Item | Value |
|---|---|
| Date (UTC) | 2026-09-29, deploy at ~19:06Z |
| Drive | `D:` (the only removable volume): FAT32, 31.902.400.512 B, Generic STORAGE DEVICE (USB) |
| Free space | before 31.843.516.416 B, after 31.841.845.248 B |
| HEAD | `c1fb3dfd802f546b93834f8bbfba9754267fa632` ("feat: prepare LEX device v1 predeploy runtime") |
| Tag | `lex-device-v1-predeploy-2026-09-29` |
| Predeploy build id | `e634aa1aa009ab25` (`LEXV1.VER` and manifest `GIT_COMMIT` = c1fb3dfd) |
| Tool | `DEVICE_INTEGRATION/tools/deploy_sd_overlay_a3a.py` (`precheck` / `deploy` / `verify`, fail closed) |

**Card signature:**
- `/99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX`
- `/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX`
- `/1- CONSTITUIÇÃO FEDERAL/`
- plus 1.062/1.062 hashes matching the backup manifest.

## Preconditions (all verified before the first byte was written)

- **Git:** HEAD c1fb3dfd, predeploy tag present, staging empty, no tracked file modified.
- **Test suites:** DEVICE 39/39, ENTENDA 80/80, LEGAL_TARGET_ID 47/47.
- **SD backup:** `BACKUP_VERIFIED`. The 1.062 files (24.574.047 B) in `backups/sd_20260929T163407Z/data` were re-hashed against the manifest. The aggregate was recomputed: `f00e6d562f239b23c033844b879a9afdf2b878980550068e3acc4101bad49b38`.
- **Flash backup:** `PHYSICAL_FLASH_BACKUP_VERIFIED`. The dump (16.777.216 B) was re-hashed: `061849a357d77f571d735a108fc5f4a032d7c12e4f7e3c8f3b34c0f3357d6727`.
- **Rollback:** `FULL_PHYSICAL_ROLLBACK_AVAILABLE = TRUE`.
- **Staging:** rebuilt from scratch twice (`staging_sd_v1` and `staging_sd_v1_run2`) from HEAD; the two builds are `BYTE_IDENTICAL`.
- **Manifest:** self-consistent. The 8 files it declares match the package exactly in path, size and sha256; the 9th file is the manifest itself. There are no missing, extra or divergent files.
- **Legacy files on the card, before:** 1.062 files, 24.574.047 B, 0 differences. `/1- CONSTITUIÇÃO FEDERAL/cf.txt` is 429.242 B with sha256 `d8469e18…ca6e`.
- **Overlay folder:** `/99_LEX_V1` did not exist, and no temporary folder existed either.

## Package written (9 files, 1.288.670 B)

| File | Bytes | sha256 |
|---|---|---|
| 00_SYS/LEXV1.VER | 600 | `7c4b1a971b3e21788f49f819f5349b65bd4268a967e947181bc697edf5dce763` |
| 00_SYS/LEX_DEVICE_MANIFEST.json | 6.391 | `d2ab919f3e95de6e38e082993205be80ce8bddc122a880042140bb1dde000097` |
| 05_TEXT/CF88_RUNTIME.txt | 587.133 | `7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a` |
| 10_TARGETS/CF88_TARGETS.IDX | 165.466 | `36db8b871163262dacb97d5f4ecd36044ea70aa223f021f93a4dad2d91f888c1` |
| 10_TARGETS/CF88_TEXT_MAP.IDX | 123.578 | `889f82002e82fb2b7d9165e6ce2a4e0dcb78d311432e268c341f1d0b1e436b96` |
| 20_REFERENCES/REF_LOOKUP.IDX | 6.579 | `9665fb854fe5b91fc5a1aa640b6eb8270583e3c6414720e99f37f9608ccb3c12` |
| 20_REFERENCES/REF_PAYLOAD.IDX | 65.546 | `1c772c83b6cfe381ddb1674b73126dbf2fb6cf354fe16d708194cdad0de94228` |
| 30_ENTENDA/ENTENDA_LOOKUP.IDX | 30.462 | `93613275d4e0caf95ed58f1fe8e29cc90039d73ec9d302fc7ce0af2e5f816ddc` |
| 30_ENTENDA/ENTENDA_PAYLOAD.DAT | 302.915 | `a7511b917f658fd411b0f46c241415e77148c9b1c8ed1780a797958fe640c029` |

Package contents: 3.810 targets in the table (3.812 in the index), 163 ENTENDA explanations, and the approved Reference Engine export copied byte for byte.

## Procedure

1. `mkdir D:\99_LEX_V1.DEPLOYING`. This fails if the folder already exists.
2. Copy only the 9 staging files, each opened with `xb`, then `flush` + `fsync`.
3. Reopen every file and compute its sha256 from the card: **9/9 OK**.
4. Run the simulator directly on the temporary folder: OK.
5. `os.rename(99_LEX_V1.DEPLOYING → 99_LEX_V1)`, a single directory-entry rename. The destination did not exist, so nothing was replaced.
6. Re-hash the final folder: **9/9 OK**. The temporary folder no longer exists.
7. Re-check the legacy files after the write: **1.062/1.062 identical**, and `cf.txt` is intact.
8. Flush the volume with `Write-VolumeCache D`.
9. Independent `verify` pass, read-only, run again: overlay 9/9 and legacy 1.062/1.062.

**Result:**
- Legacy files before: 1.062. After: 1.062. Legacy bytes: 24.574.047.
- **LEGACY_FILES_CHANGED = 0.**
- **NEW_DEVICE_V1_FILES = 9**, totalling 1.288.670 B, in the new folder `/99_LEX_V1`.
- The only new top-level entry is `99_LEX_V1`. Nothing changed outside it.

## Simulator run directly on `D:\99_LEX_V1` (identical to local staging: `simulator_card_equals_staging = True`)

**Runtime checks:**
- Runtime on the card is 587.133 B with sha `7ef82290…`: **CONFERE**.
- TEXT_MAP lookup at the offset of "VIII - a execução, de ofício" returns `CF88:ART.114:INC.VIII`.
- The same lookup with a wrong sha256 returns `FAIL_CLOSED` (`SOURCE_SHA256_MISMATCH`).

**Queries:**

| Query | Status | Resolution | Anchor | Refs |
|---|---|---|---|---|
| CF88.5.V | OK | COVERED_BY_BLOCK | CF88:ART.5:INC.IV | 1 |
| CF88.21.XXIV | OK | DIRECT | CF88:ART.21:INC.XXIV | 0 |
| CF88.22.XXIX | OK | DIRECT | CF88:ART.22:INC.XXIX | 0 |
| CF88.24.4 | OK | COVERED_BY_BLOCK | CF88:ART.24:PAR.3 | 0 |
| CF88.37.6 | OK | DIRECT | CF88:ART.37:PAR.6 | 5 |
| CF88.60.4.IV | OK | DIRECT | CF88:ART.60:PAR.4:INC.IV | 0 |
| ADCT.10.II | OK | DIRECT | ADCT:ART.10:INC.II | 0 |
| CF88.114.VIII | OK | NONE | — | 2 hidden rows; jurisprudence layer off |
| CF88.25 (no ENTENDA) | OK | NONE | — | 1 |
| CF88.1 | OK | DIRECT | CF88:ART.1 | 1 (jurisprudence layer on) |
| ADCT.78.4 | OK | NONE | — | 1 (RG 231) |
| CF88.40.4.II (filtered historical target) | INVALID_OR_UNKNOWN_TARGET | NONE | — | 0 |
| CF88.999 / XYZ | INVALID_OR_UNKNOWN_TARGET | NONE | — | 0 |

## Known issues

- **KNOWN_NON_BLOCKING_REFERENCE_ISSUE.** `CF88:ART.114:INC.VIII` exists correctly in the runtime. Its references, SV 53 and Tema 36, are still classified `HISTORICAL_HIDDEN_BY_DEFAULT` by the approved Reference Engine, so **they will not appear on the device**. The Reference Engine was not reopened in this phase.
- `RELATIONS_V2_LEGACY_64_LINE_LIMIT`: non-blocking, unchanged.

## What was not done

- No firmware flashing, no `write_flash` / `erase_flash`, no Arduino upload.
- Bootloader, partitions and the ESP32 were not touched.
- The feature flag stays 0 in versioned code.
- No legacy file was changed, renamed or deleted.
- No commit, tag or push. This report and the deploy tool are left uncommitted for review before A3B.
- A3B was not started.
