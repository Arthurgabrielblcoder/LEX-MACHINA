# DEVICE V1: physical baseline approved (2026-10-01)

## Status

**PHYSICAL_HUMAN_VALIDATION = APPROVED** (by Arthur, on the real LEX MACHINA, 2026-10-01).

- Previous HEAD: `4d1f06ec0b37b6491e7bac40632bcd700366ff3e` (tag `lex-device-v1-a3b-retry-ready-2026-09-29`).
- Freeze tag: `lex-device-v1-physical-approved-2026-10-01`.
- This freeze adds no content and changes no logic. It versions the exact sources that were flashed and approved.

**Approved physically:**
- ENTER starts the article search;
- numeric keyboard;
- keys 1 CORRELATAS, 2 JURISPRUDÊNCIA, 3 ENTENDA, 4 REFERÊNCIAS;
- dynamic footer;
- ENTENDA typography and smooth scrolling;
- rich references;
- CONTEXTO / ACTIVE_TARGET sync;
- JURISPRUDÊNCIA × REFERÊNCIAS separation;
- jurisprudence and correlatas by canonical target;
- ART.n ↔ ART.n:CAPUT equivalence;
- no undue inheritance to incisos or parágrafos;
- general physical navigation.

## Firmware (what is on app0)

| Item | Value |
|---|---|
| Sketch | `firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino` sha256 `f06cdc14ad066e2575fe03552eb0090f39c77ab350d095de7bf26d41c86a81ed` |
| Module | `lex_device_v1.h` sha256 `1c0971089e2e2c2489e1dadba12879a42b5a8b27be58e7927baca62f3a0357bb` |
| Rich reference data | `lex_ref_detail_data.h` sha256 `08f8fbdf2362610a6915324f8f62765cbfa10c36fca4954899b508056ac0b72f` (`build_ref_detail_header.py --check`: UP_TO_DATE) |
| Toolchain | arduino-cli 1.5.1, esp32 core 3.3.11, `esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default` |
| flag 1 (`-DLEX_DEVICE_V1_ENABLED=1`) | **1.075.603 B program, 125.612 B static RAM** |
| flag 0 (default) | 989.395 B / 124.452 B, the same sizes as the approved legacy v7.12.0 baseline |
| Flashed and approved image | app0 @ 0x10000, 1.075.744 B, sha256 `c01e923a…1a90`, readback byte-identical (local backup, not versioned) |

- The image sha256 changes on every rebuild because the ESP-IDF app descriptor embeds the build date and time. The source hashes above identify the approved build.
- Hardware and the SD card were not touched in this freeze.

## Runtime and schema

- **LEI SECA:** `CF88_RUNTIME` complete plus the current ADCT (`/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt`, 587.133 B, sha256 `7ef82290…2e42a`).
  - The runtime is verified at boot by size and sha256 (fail closed).
  - The ADCT starts at the `#NAMESPACE_START_ADCT` offset.
- **Schema:** `LEXV1.VER` DEVICE_VERSION 3 (2 and 4 rejected), TARGETS 3.810, `REFERENCE_ENGINE cf-reference-engine-final-2026-09-28`.
- **ENTENDA:** 163 approved explanations in the current DEVICE V1:
  - 154 sequential explanations, arts. 1–24;
  - 9 pilots outside the sequential scope.

  `ENTENDA_COUNT 163`, `ENTENDA_SCOPE CF88_ARTS_1_24_PLUS_APPROVED_PILOTS`, `ENTENDA_PILOTS 9`.
- **Boot self-test:**
  - `DIAG RESULT PASS 33/0 MAX_OPEN_COUNT=4`;
  - `runtime hash CONFERE`; no FAIL_IO;
  - legacy `JUR CACHE 178/296` preserved.

## Reader state machine

- `NORMAL_READING_MODE`:
  - wheel and arrows scroll;
  - ENTER enters `ARTICLE_SEARCH_MODE`;
  - 1–4 open a layer only if it is available for ACTIVE_TARGET (otherwise the key is ignored);
  - 5–9 and 0 do nothing.
- `ARTICLE_SEARCH_MODE`:
  - digits edit the article number and ENTER searches;
  - BACKSPACE/ESC with an empty buffer returns to the same reading point;
  - the text does not move during the search.
- `LAYER_VIEW_MODE` (V1 layer, legacy correlata/jurisprudence lists, opened document):
  - digits and ENTER open no other layer;
  - BACK returns to the same line.

## Canonical target model

- **ACTIVE_TARGET** = `CF88_TEXT_MAP.IDX` at the offset of the same line that produces the CONTEXTO label. It is resolved immediately, with no debounce, and re-resolved synchronously on each key press.
  - If the cached availability belongs to another target, it is stale and recomputed.
  - If the drawn CONTEXTO is a different target, the key is ignored.
- **LAYER_TARGET** = ACTIVE_TARGET copied at the key press. The list, the detail and the opened item all use it until BACK.
- **Availability cache:** the TARGETS flags of the ACTIVE_TARGET query keys, debounced at 250 ms while scrolling.
  - The flags E/B drive 3; C/J/W drive 1/2/4.
  - The C/J/W flags are derived from the exact records of each target: 0 mismatches.

## The four layers

All four start from the same ACTIVE_TARGET. One classifier, `lexV1ClassificarDestino`, routes every REF_PAYLOAD row to a single layer. Hidden and historical rows go nowhere, and unknown types are hidden and logged.

| Key | Layer | Source |
|---|---|---|
| 1 CORR. | CORRELATA | REF_LOOKUP (exact query keys) → REF_PAYLOAD → classifier. The item is resolved by its link id (`REL_…`) in legacy `RELACOES.IDX` to open the external law. |
| 2 JURIS. | JURISPRUDENCIA | Same path. The item is resolved by its link key (`STF:RG:n:CF88:…`) in legacy `JURISPRUDENCIA.IDX` to open the thesis. |
| 3 ENTENDA | ENTENDA_LOOKUP / ENTENDA_PAYLOAD | DIRECT or COVERED_BY_BLOCK. ACTIVE_TARGET only; its own semantics, no caput equivalence. Arimo 12 px, smooth viewport scroll. |
| 4 REF. | REFERENCIA (WORK_REFERENCE) | Same exact path. List sorted by note, then rich detail (SOBRE, POR QUE ESTÁ AQUI, ALCANCE) keyed by the link's real `TARGET\|WORK`. |

- The legacy per-article indices (`JUR_LOOKUP` / `REL_LOOKUP`) are no longer a source for the V1 lists.
- The legacy caches remain intact for flag 0, the other laws, and opening items.

## ART ↔ CAPUT (the only equivalence)

`lexV1QueryKeysForActiveTarget`:
- `CF88:ART.n` (the TEXT_MAP article line, i.e. the visual caput) → `[CF88:ART.n, CF88:ART.n:CAPUT]`;
- every other target → `[target]`.

The records of the keys are unioned and deduplicated by (layer, SOURCE_ID). Footer and list use the same union. There is no inheritance to incisos, parágrafos or alíneas, and no fallback to the parent.

- 32 visible links on 17 `:CAPUT` targets are reachable, each only from its own article line. 0 duplicates, 0 descendant leakage.
- Example: RG 113 appears at the art. 5 caput, and not in V, VI or VIII. RG 66 appears at the art. 37 caput, and not in §6.

## Validation for this freeze (2026-10-01)

| Suite | Result |
|---|---|
| DEVICE (`DEVICE_INTEGRATION/tests`, all modules) | **141/141 PASS** |
| … fast-track UI / reader state machine / UI refinement | 3 / 10 / 10 PASS |
| … target sync / layer routing | 14 / 9 PASS |
| … canonical layers / caput equivalence | 19 / 12 PASS |
| … device integration / runtime A2B / predeploy A2C / A3B prep / A3B prep2 | 14 / 17 / 8 / 14 / 11 PASS |
| ENTENDA (`ENTENDA_ENGINE/tests`) | **80/80 PASS** |
| LEGAL_TARGET_ID (`LEGAL_TARGET_ID/tests`) | **47/47 PASS** |

**Audit** (`tools/canonical_layer_audit.py`, `CANONICAL_LAYERS_AUDIT.json`):
- 432 links classified: JURISPRUDENCIA 279, REFERENCIA 101, CORRELATA 44, HIDDEN 8, UNKNOWN 0;
- export target == runtime target 432/432 (0 target mismatches);
- layer-routing intersections between 1/2/4: 0;
- canonical mismatches: CORRELATA 0, JURISPRUDENCIA 0, REFERENCIA 0;
- flag mismatches: 0;
- caput equivalence: 0 unreachable, 0 duplicates, 0 leaks.

## Known issues (non-blocking, not fixed in this freeze)

1. **KNOWN_ARCHITECTURAL_DEBT: REFERENCE_RICH_METADATA_CURRENTLY_EMBEDDED_IN_FIRMWARE.**
   - The rich metadata of the 101 work-reference links is compiled into flash (`lex_ref_detail_data.h`, about 52 KB).
   - Future action: migrate it to the `/99_LEX_V1` overlay as a versioned file with fail closed.
2. 18 work links have no indication note (`score_editorial` is null in the approved catalog). The note is not shown.
3. There is no TEMAS field in the approved corpus. It is not shown and not invented.
4. Art. 114, VIII: SV 53 and Tema 36 still carry the inherited classification `HISTORICAL_HIDDEN_BY_DEFAULT`, so 4 REF. does not appear there.
5. Touch is not integrated in the new V1 layers (keyboard only).
6. `RELATIONS_V2_LEGACY_64_LINE_LIMIT` stays legacy and non-blocking (see that document).
7. Sequential ENTENDA covers only arts. 1–24 plus the 9 pilots. Other targets show no 3.
8. Other documented limitations that do not block current use:
   - 3 art. 40 targets (§4 II/III, §7 I) hold only hidden historical rows;
   - `max_files=12` costs about 29,7 KB of PSRAM.

## Next phase

The editorial production **ENTENDA_CF_BATCH04** starts at art. 25. It has not been started in this freeze.
