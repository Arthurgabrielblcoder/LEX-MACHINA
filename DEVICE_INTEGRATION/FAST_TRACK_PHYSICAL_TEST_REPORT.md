# FAST TRACK PHYSICAL TEST REPORT (DEVICE V1, 2026-09-29)

**Status:**
- NOT COMMITTED: waiting for the human test on the device.
- Base: HEAD `4d1f06ec` (tag `lex-device-v1-a3b-retry-ready-2026-09-29`).

## Gate 1: retry firmware (candidate v2, no UI): PASS

**Pre-flight:**
- suites DEVICE 64/64, ENTENDA 80/80, LEGAL_TARGET_ID 47/47;
- ESP32-S3 v0.2, MAC `e0:72:a1:f4:fd:28`, 16 MB, on COM3;
- app0 before the write was `ab6d4ffc…1c1f` (legacy v7.12.0).

**Write and readback:**
- Written: `write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 candidate_app_v2.bin` with `--after no-reset`.
- Candidate: `d6b1bd05…17be`, 1.005.520 B.
- Erase covered 0x10000–0x105FFF. Readback of 1.005.520 B was byte-identical.

**Boot (`backups/fast_track/gate1_boot_serial.bin`):**
- 1 reset (POWERON); no Guru Meditation, panic, `no free file descriptors` or `FAIL_IO`.
- `DEVICE_VERSION` read 3, expected 3. `RUNTIME_HASH_MATCH` (runtime sha256 took 573 ms).
- **`DIAG RESULT PASS pass=33 fail=0 MAX_OPEN_COUNT=4`**; steady state OPEN_COUNT=3.

**Smoke tests:**

| Target | Result |
|---|---|
| CF88:ART.5:INC.V | COVERED_BY_BLOCK, anchor CF88:ART.5:INC.IV |
| CF88:ART.37:PAR.6 | DIRECT, 5/5 references |
| ADCT:ART.10:INC.II | DIRECT |
| CF88:ART.114:INC.VIII | valid target, ENTENDA NONE, 2 references hidden (known issue) |
| CF88:ART.25 | ENTENDA NONE, 1 reference |
| CF88:ART.999 | INVALID_OR_UNKNOWN_TARGET |

References: zero-result 0 (payload not opened), single 1, multiple 5.

**Legacy and memory:**
- `JUR CACHE: lookups=178 registros=296`.
- **Measured cost of `max_files=12`:** "PSRAM livre antes dos caches" was 8.304.524 B, against 8.334.248 B in legacy (**−29.724 B of PSRAM**). "Heap antes do BLE" was 209.596 B against 209.612 B (−16 B). The VFS reserves its structures in PSRAM.
- DEVICE V1 heap: before 136.788 B (largest block 90.100 B); after 135.284 B, minimum 116.432 B.
- **Measured times (not optimized):** a lookup on the SD takes about 40–80 ms (target 50–76 ms, ENTENDA 39–65 ms, TEXT_MAP 78 ms, BLOCK 59–81 ms, references 24–39 ms). The payload read takes about 80 µs. The index readers read byte by byte, so buffering them is the obvious next optimization.

## Gate 2: minimal physical test UI (flag 1 only)

**Keys** (in the Constitution reader):
- `E` (HID usage 0x08 or ascii e/E) opens **ENTENDA**.
- `R` (HID 0x15 or ascii r/R) opens **REFERÊNCIAS**.
- In the reader, letters had no function before; they are ignored during text search.
- In the layer: ↑/↓ and the scroll wheel scroll; PageUp/PageDown move by page. `ESC` or `BACKSPACE` closes the layer and returns to the text on exactly the same line (`linhaTopo` is preserved).
- Touch in the layer: **PENDING** (no action).

**Current dispositivo:**
- When DEVICE V1 is verified at boot (`lexV1Pronto`), opening `/1- CONSTITUIÇÃO FEDERAL/cf.txt` makes the reader display `/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt`. These are the exact bytes indexed by the TEXT_MAP, verified by size and sha256.
- The dispositivo is resolved by `lexv1TargetAtOffset` at the offset of the **first visible line** (floor lookup), then validated in the target table.
- If there is no target (preamble, headings, NORMA/NAMESPACE nodes), no layer opens; the strip shows "V1: SEM DISPOSITIVO NESTA POSIÇÃO".

**Legacy layers:**
- `arquivoAtualPertenceACF()` recognises the runtime only for positions before the ADCT. The legacy `cf.txt` had no ADCT, so the Juris/Correlatas shortcuts of v7.12.0 are not applied to ADCT articles.
- Name, article search, text search, context and scrolling stay those of the legacy code.

**Footer:** a discreet indicator `[E]ENTENDA [R]REF` on the context strip. The context text is shortened to 34 characters. The rest of the footer was not redesigned.

**ENTENDA screen:**
- Shows `DISPOSITIVO: <rótulo>` and, for BLOCK, `EXPLICAÇÃO COMPARTILHADA COM: <âncora>`.
- Then the title (`D|`) and **all** sections of the approved payload: O QUE DIZ, O QUE SIGNIFICA, EXEMPLO PRÁTICO, ATENÇÃO, PALAVRAS DIFÍCEIS (shown as `termo: definição`), and CAMADAS EXTERNAS when present. The text is not rewritten.
- BLOCK reads the anchor's block; the payload is not duplicated.
- Without ENTENDA: "Explicação ainda não disponível para este dispositivo nesta versão."

**REFERÊNCIAS screen:**
- Only `CURRENT_VISIBLE` rows. For each: type (JURISPRUDÊNCIA / CORRELATA / REFERÊNCIA DE OBRA), label and `Fonte: <id>`.
- With none: "Nenhuma referência vinculada a este dispositivo nesta versão."
- Hidden historical references stay hidden. For 114.VIII this means "Nenhuma…" (known issue).

**Memory and files:**
- Each ENTENDA/REFERÊNCIAS opening: TEXT_MAP open → lookup → close; TARGETS open → close; lookup + payload open → seek → read the block (≤ 8 KB) → close. Peak 2 files. The tracker logs OPEN/CLOSE to serial.
- The layer text (≤ 12 KB) and the screen lines go to PSRAM and are freed on BACK.
- Everything is read-only on the SD.

**Build:**
- flag 1 (UI): 1.013.423 B program, 124.580 B static RAM.
- flag 0: 989.395 B / 124.452 B, identical to v7.12.0.
- Candidate `backups/fast_track/candidate_ui_flag1/candidate_app_ui.bin`: 1.013.568 B, sha256 `24ff0f3e37f691c7bace9fa6a9daabdf4c972f3863d75230ca1d652aceb3d052`. App image (checksum and hash valid), 297.152 B to spare in app0, `flash_args` app at 0x10000.
- Sources used (not committed): `.ino` sha256 `62c0b2f2…`, `lex_device_v1.h` `6d326296…` (header unchanged since the tag).

**Second write:**
- Same procedure: app0 only, erase 0x10000–0x107FFF, readback of 1.013.568 B byte-identical.
- Boot (`gate2_boot_serial.bin`): 1 reset; no Guru Meditation, panic or FAIL_IO; `runtime hash CONFERE`; `DIAG RESULT PASS pass=33 fail=0 MAX_OPEN_COUNT=4`; `JUR CACHE 178/296`; `LEXV1: UI TESTE ATIVA`.

**Host tests:**
- DEVICE: 67/67, with 3 new tests in `tests/test_fast_track_ui.py`:
  - the 9 physical-test dispositivos resolved from the reader position (line start and wrapped continuation) → TEXT_MAP → ENTENDA/references;
  - BLOCK uses the same block as its anchor;
  - fail closed with the wrong file;
  - wiring gated by the flag;
  - new identifiers absent outside `#if LEX_DEVICE_V1_ENABLED`.
- Two earlier tests were scoped: the read-only check now allows `tft.print` (the display) and the no-allocation rule applies to the diagnostic.
- ENTENDA 80/80, LEGAL_TARGET_ID 47/47.

## State

- **Running:** DEVICE V1 PHYSICAL TEST UI (app0 `24ff0f3e…`).
- **Rollback:** not needed. The `legacy_app0_partition.bin` (`ab6d4ffc…`) rollback stays available (app only at 0x10000).
- **Git:** UI sources, tests and this report are **not committed**. No commit or tag was created.
- **Pending validation:** `PHYSICAL_UI_HUMAN_VALIDATION_PENDING`: display, keyboard (E/R/ESC/arrows), wheel, touch.

## Update: numeric physical keyboard (human decision), flashed for testing

**Reader state machine** (flag 1 only; flag 0 still builds to 989.395 B / 124.452 B, identical to v7.12.0):

- **NORMAL_READING_MODE** (dry law text):
  - `1` LEGISLAÇÃO CORRELATA, via the legacy mechanism `abrirCategoriaRelacao(REL_CORRELATAS)`;
  - `2` JURISPRUDÊNCIA, via the legacy mechanism: the categories screen, or all of them directly when the CF has a single category;
  - `3` ENTENDA and `4` REFERÊNCIAS, via DEVICE V1. These work only on the CF opened through the verified runtime; any other text gets a message in the strip;
  - `ENTER` enters ARTICLE_SEARCH_MODE;
  - `5`–`9` and `0` do nothing, and typing digits no longer starts a search;
  - `BACKSPACE` does nothing; `ESC` goes back to the folders, as in legacy;
  - arrows, wheel and PageUp/PageDown scroll as in legacy;
  - when there is no correlata or jurisprudence data at that point, the strip says so.
- **ARTICLE_SEARCH_MODE:**
  - the strip shows `BUSCAR ARTIGO   Art.: 37_`;
  - the bar shows `ENTER=BUSCAR  BACKSPACE=APAGAR`, or `DIGITE O ARTIGO  BACKSPACE=VOLTAR AO TEXTO` when the field is empty;
  - `0`–`9` are only digits (maximum 8);
  - `ENTER` with a number searches (legacy `pesquisarArtigo`, always from the start of the file); with an empty field it does nothing;
  - found: the search closes, the buffer is cleared, the state returns to NORMAL, and the viewport, context, TEXT_MAP and footer update through the normal flow;
  - not found: `ART. N NAO ENCONTRADO` for 0,7 s, then the state stays in the search with the number for editing;
  - `BACKSPACE` deletes the last digit; with the field empty, it cancels and returns to the **same file and offset**;
  - the text does not move during the search (wheel and arrows are ignored), and the offset is saved on entry and checked on cancel;
  - `ESC` also cancels.
- **LAYER_VIEW_MODE** (ENTENDA/REFERÊNCIAS, Correlatas, Juris, open document):
  - digits and ENTER open no other layer and start no search;
  - in the ENTENDA/REFERÊNCIAS layer only scrolling and `BACKSPACE`/`ESC` (back to the same point) work;
  - in the legacy Correlatas/Jurisprudência lists, the existing navigation (arrows, ENTER/digit to open the item) is preserved.
- **Removed:** the `E`/`R` shortcuts and the `[E]ENTENDA [R]REF` indicator.
- **Normal footer:** `1 CORR. 2 JURIS. 3 ENTENDA 4 REF.  ENTER=BUSCAR` on the CF, or `1 CORR. 2 JURIS.  ENTER=BUSCAR` on other texts. The font was not reduced.
- **Touch on the new footer:** pending. The legacy shortcut touch areas remain.

**Tests:**
- DEVICE: 77/77, including the new `tests/test_reader_state_machine.py` (10 tests) and the updated UI smoke tests. The state-machine tests cover:
  - `ENTER 3 ENTER` → art. 3 (never ENTENDA);
  - `ENTER 4 ENTER` → art. 4;
  - `ENTER 21`, `24`, `37`, `60`, `114`, `225` → the matching article; the landing line resolves through the TEXT_MAP to `CF88:ART.N`;
  - `ENTER 1 1 4` then BACKSPACE ×3 → still searching; one more BACKSPACE → same offset;
  - 1–4 in NORMAL open the layers, 5–9 and 0 do nothing;
  - empty ENTER, not-found article, and layers blocking digits and ENTER.

  The firmware source is checked against these rules.
- ENTENDA: 80/80. LEGAL_TARGET_ID: 47/47.

**Flash:**
- `candidate_app_numeric.bin` (`backups/fast_track/candidate_numeric_flag1/`): 1.015.408 B, sha256 `0ca25f1dc0a0ce3b064aec3aabb52045ce48573f4b48c5ab3d971f0ef812fadf`, app image with checksum and hash valid.
- Written to app0 only at 0x10000 (erase 0x10000–0x107FFF). Readback byte-identical. Source `.ino` sha256 `bbabe22b…`.

**Boot** (`numeric_boot_serial.bin`):
- 1 reset; no Guru Meditation, panic or FAIL_IO;
- `runtime hash CONFERE`; `DIAG RESULT PASS pass=33 fail=0 MAX_OPEN_COUNT=4`; `JUR CACHE 178/296`.

**Note:** the boot serial line still says "UI TESTE ATIVA (teclas E/R no leitor da CF)". It is only a log string, kept so that the flashed binary matches the source. Fix it when the change is committed.

**Git:** not committed. Waiting for Arthur's physical test.

## Refinement after the video test (Arthur): 4 fixes, flashed for a new physical test

### DYNAMIC_LAYER_FOOTER

- **What each option means.** An option appears only when there is real content for the current dispositivo. The numbers are fixed and never renumbered.
  - `1 CORR.`: legacy counter `totalCorrelatasArtigo>0`.
  - `2 JURIS.`: legacy counter `totalCategoriasJuris>0`.
  - `3 ENTENDA`: TARGETS flag `E` (DIRECT) or `B` (COVERED_BY_BLOCK).
  - `4 REF.`: TARGETS flag `C`, `J` or `W`. These flags are built only from `CURRENT_VISIBLE` rows, so hidden and historical references do not count (114.VIII shows no 4).
- **Layout.** `ENTER=BUSCAR` stays fixed on the right. With no layer, no options are shown. In ARTICLE_SEARCH_MODE the search bar is shown instead.
- **Unavailable key:** ignored. The "Explicação ainda não disponível…" and "SEM … NESTE PONTO" screens are gone.
- **Availability cache (`lexV1Disp`)** for the TEXT_MAP record of the first visible line, over the offset range `[ini, fim)` of that same record:
  - `lexv1Find` now also returns the next key;
  - scrolling inside the range costs no I/O;
  - outside it, recomputing waits until the wheel has been still for 250 ms, then does 1 TEXT_MAP lookup + 1 TARGETS lookup on the 2 indices kept open (steady state of the UI = 2 handles);
  - the footer is redrawn only if the mask changed;
  - keys 3/4 force the computation before opening.

### ENTENDA_TYPOGRAPHY_FIX

| | Before | Now (same as the dry law) |
|---|---|---|
| Font | `imprimirUTF8` (6 px fixed GFX font, accents drawn by hand) | Arimo proportional 12 px, antialias A4 (`desenharGlyphArimoNoBuffer`), same glyphs and accents (ç, º, §, –) |
| Line | 12 px tall, 14 lines | `LEITOR_LINHA_H` 15 px, baseline 12, 12 lines from `TEXTO_Y0` |
| Wrap | 52 columns | real glyph widths (`avancoGlyphArimo`), up to `LEITOR_TEXTO_W` = 312 px, cut at the last space |

Section bars (O QUE DIZ, …) are drawn as an inverted green bar with the same font.

### ENTENDA_SMOOTH_SCROLL

- **Cause of the flicker:** `lexV1DesenharCamada()` ran on every scroll step. It did `tft.fillScreen(COR_FUNDO)` followed by a slow character-by-character redraw (6 px font), so each step showed an almost empty frame.
- **Fix:** the text is prepared and wrapped only once, when the layer opens. The header and footer are also drawn only once. Scrolling (`lexV1RolarCamada`) redraws only the 12-line viewport, with each line rasterised in `bufferLinhaLeitor` and sent with `drawRGBBitmap`, the same mechanism as the dry law. There is no `fillScreen` during scrolling.
- **Controls:** wheel and arrows move 1 line; PageUp/PageDown move one page.

### REFERENCE_RICH_DETAIL

- **Pipeline audit:**
  - the approved RC2 catalog (`REFERENCIAS_RC2.json` → `CF88_REFERENCES_CANONICAL.json`, `legal_fields_preserved`) has, per work↔dispositivo link: `obra`, `tipo`, `ano`, `score_editorial`, `fontes[].paraphrase` (documented synopsis), `POR_QUE_ESTA_OBRA_SE_RELACIONA`, `PARTE_ALCANCADA` and `relacao_pedagogica`;
  - the approved device `REF_PAYLOAD` carries only `TARGET|TIPO|VISIBILIDADE|STATUS|REFERENCE_ID|SOURCE_ID|LABEL`, so the rich fields were being dropped before reaching the device.
- **Fix without touching the approved export and without an SD write:**
  - `REF_PAYLOAD` stays a byte copy;
  - the card was inside the device, not on the PC, so no overlay write was possible;
  - `tools/build_ref_detail_header.py` generates `lex_ref_detail_data.h` deterministically from the approved data: 101 links (all the visible `WORK_REFERENCE` rows), source sha256 `89bd39c4…`, `REF_DETAIL_SCHEMA 1`, `--check` to detect a stale header;
  - it is compiled into the firmware (about 52 KB of flash);
  - moving it to an SD overlay file (`REF_DETAIL`, versioned, with fail closed) is pending for when the card is on the PC.
- **Links with several approved nuclei** (e.g. REF-LIV-0004 @ 227): the approved texts are joined as paragraphs and the highest score is kept.
- **Screen:**
  - `4` opens a list: title; type – year – Nota x,y; items with a score first, sorted by score descending (stable), then the rest in the approved order;
  - arrows and wheel select, ENTER opens the detail, BACK goes from detail to the list and from the list to the text (same point);
  - the detail shows the title, TYPE – YEAR, **Nota de indicação: 8,8** (the score of the LINK: Timbuktu is 8,8 at 5.VI and 9,0 at 5.VIII), DISPOSITIVO, SOBRE, POR QUE ESTÁ AQUI, ALCANCE NESTE DISPOSITIVO (PARTE_ALCANCADA + relation), and `Fonte: EXP-FIL-009` discreetly at the end;
  - jurisprudence and correlata items show type and label, plus "Ficha editorial ainda não disponível".
- **REFERENCE_DETAIL_INCOMPLETE** (101 links):

  | Field | Missing |
  |---|---|
  | tipo | 0 |
  | ano | 0 |
  | **nota** | **18** (score_editorial null in the approved catalog) |
  | sobre | 0 |
  | por_que | 0 |
  | **temas** | **101**: there is no approved "temas" field. It is not shown and not invented. |

### Validation

- DEVICE 87/87 (10 new tests in `tests/test_ui_refinement.py`), ENTENDA 80/80, LEGAL_TARGET_ID 47/47.
- Build: flag 1 1.067.667 B / 125.460 B static RAM; flag 0 989.395 B / 124.452 B (identical to legacy).
- `candidate_app_refined.bin`: 1.067.808 B, sha256 `94e7462a74e0fb7f8f2ca606f82719a55069beb75b568e763746e752105f5163`, 242.912 B spare in app0.
- Written to app0 only at 0x10000 (erase 0x10000–0x114FFF). Readback byte-identical.
- Boot (`refined_boot_serial.bin`): 1 reset; no Guru Meditation, panic or FAIL_IO; `runtime hash CONFERE`; `DIAG RESULT PASS 33/0 MAX_OPEN_COUNT=4`; `JUR CACHE 178/296`.
- SD: not written; overlay unchanged (9 files); legacy unchanged.
- Git: not committed.

**Pending for the human test:** the look of the new typography and scrolling, the dynamic footer while scrolling, the list and detail of references, and ENTER/BACK in the list.

## TARGET SYNC fix (video: CONTEXTO ART. 5 | INC. XVI, key 4 opened CF ART. 5, INC. XV / Papers, Please)

- **Confirmed root cause:** two sources for the "current" device.
  - CONTEXTO came from the viewport's **center line** (`escolherContextoPredominante`, line 6 of 12).
  - The V1 layers resolved the TEXT_MAP at the **top line** (`offsetsLinhas[linhaTopo]`).
  - With short incisos (XV/XVI), both are on screen at once, so the footer said XVI while key 4 opened XV.
  - The 250 ms debounce was **not** the cause: the key press already forced a recompute, but from the wrong line. The debounce only left the footer mask stale for up to 250 ms.
- **Fix (firmware only; no data touched):**
  - `ACTIVE_TARGET` (`lexV1Alvo`) = TEXT_MAP(offset of the line that generates CONTEXTO). It is resolved immediately in `diagnosticarContextoSeMudou`, with no debounce.
  - The CONTEXTO label is built from ACTIVE_TARGET (`lexV1RotuloContexto`).
  - Keys 1/2 load the article of ACTIVE_TARGET (`lexV1SincronizarRelacoes`). CF vs ADCT is decided on the same line.
  - `LAYER_AVAILABILITY_CACHE` (`lexV1Disp`) stays debounced at 250 ms. It is invalidated as soon as the target changes, and 3/4 stay hidden until the new mask is ready.
  - Key press: `lexV1ResolverAlvoKeypress` re-resolves the target synchronously. A cache of another target is rejected (`STALE_CACHE_DETECTED`) and recomputed. If the drawn CONTEXTO is a different target, the key is ignored (`STALE_CONTEXT_DETECTED`).
  - `lexV1AbrirCamada(tipo, tid)` receives the target explicitly, and `lexV1RefTid` (LAYER_TARGET) is frozen for list and detail. Detail lookup stays keyed by `TARGET_ID|WORK_ID`.
  - Serial output for the physical test: `ACTIVE_TARGET= CACHE_TARGET= CONTEXTO_TARGET= KEY=` and `OPEN_LAYER_TARGET=`.
- **Data check (read-only):**
  - Papers, Please = `REF-JOG-0001`, approved (RC2, APROVAR) only at `CF88:ART.5:INC.XV`. There is no link to XVI.
  - XVI has no visible reference (`E----X`), so 4 must do nothing there.
  - Export audit: 432 links, source target equal to exported target 432/432, 0 mismatches (22 via the quarantine split). REF_PAYLOAD equals the SD staging file byte for byte.
- **Tests:** new `tests/test_target_sync.py` (14 tests: pre-fix bug reproduced, XV↔XVI, 8 transition kinds × keys 1–4 × both directions, all TEXT_MAP transitions at 3 wrap widths, CONTEXTO == DISPOSITIVO, source contract, Papers Please, export audit).
  - DEVICE 101/101, ENTENDA 80/80, LEGAL_TARGET_ID 47/47.
- **Build:** flag 1, 1.070.023 B (81%) / 125.612 B static RAM.
- **Candidate:** `candidate_targetsync_flag1/candidate_app_targetsync.bin`, 1.070.176 B, sha256 `145c29cd4715c4b51f882a7d4b90d34ea671353d2f945ce461641313b5a182a4`, image hash valid. Source `.ino` sha256 `091b43fd…`.
- **Flash:** app0 only at 0x10000 (erase 0x10000–0x115FFF), "Hash of data verified". Readback of 1.070.176 B byte-identical.
- **Boot** (`targetsync_boot_serial.bin`): 1 reset; no Guru Meditation, panic or FAIL_IO; `runtime hash CONFERE`; `DIAG RESULT PASS 33/0 MAX_OPEN_COUNT=4`; `JUR CACHE 178/296`.
- SD not written. Git: not committed.

## LAYER ROUTING fix (video: art. 5, V; key 4 listed "Tema de Repercussão Geral 995 / JURISPRUDÊNCIA")

- **Root cause (confirmed in code):**
  - The footer turned `4 REF.` on with `flags[1]=='C' || flags[2]=='J' || flags[3]=='W'`.
  - `lexV1CarregarItensRef` listed every `CURRENT_VISIBLE` row of `REF_PAYLOAD` (the generic Reference Engine export: CORRELATA, JURISPRUDENCE and WORK_REFERENCE), whatever its type.
  - Art. 5, V has flags `B-J-RX` (one RG 995 row), so `4 REF.` appeared and listed RG 995. RG 995 also comes in 2 from the legacy jurisprudence cache for art. 5.
- **Fix (firmware only; data untouched):**
  - Central classifier `lexV1ClassificarDestino(tipo, visibilidade)` returns CORRELATA / JURISPRUDENCIA / REFERENCIA / HIDDEN / UNKNOWN.
  - `lexV1FlagCamada(flags, camada)` maps the same taxonomy onto the TARGETS flags (C / J / W).
  - The footer (`lexV1Disp.refs`), the count and the list use the classifier: only REFERENCIA enters layer 4.
  - UNKNOWN is hidden and logged (`UNKNOWN_LAYER_TYPE`).
  - Guards `LAYER_ROUTING_ERROR` on the list and on the detail.
  - Rich detail (title, type, year, note, SOBRE, POR QUE, ALCANCE) is unchanged.
  - Layers 1/2 keep their own legacy sources (Relations V2 / jurisprudence cache).
- **Routing audit (432 links):** JURISPRUDENCIA 279, REFERENCIA 101, CORRELATA 44, HIDDEN 8, UNKNOWN 0.
  - Before: 44 correlatas and 279 jurisprudence were also eligible for layer 4.
  - `4 REF.` was lit on 238 targets, and 195 of them had no work.
  - After: `4 REF.` is lit on 43 targets, and the intersections between 1/2/4 are 0.
- The video's "RG 989" does not exist in any device index; art. 5 has RG 969. Probably a misreading.
- **Tests:** new `tests/test_layer_routing.py` (9). UI tests updated to the corrected footer (5.V → no 4; ART.25 → none; 5.VI Timbuktu → 4).
  - DEVICE 110/110, ENTENDA OK, LEGAL_TARGET_ID OK.
- **Build:** flag 1, 1.070.499 B.
- **Candidate:** `candidate_routing_flag1/candidate_app_routing.bin`, 1.070.640 B, sha256 `c2ba73f7…7079`. Source `.ino` sha256 `874c23c0…f481`.
- **Flash:** app0 only at 0x10000 (erase 0x10000–0x115FFF), hash verified. Readback byte-identical.
- **Boot:** 1 reset, no panic or FAIL_IO, `runtime hash CONFERE`, `DIAG PASS 33/0 MAX_OPEN_COUNT=4`.
- Not committed.

## CANONICAL LAYERS fix (Arthur: Art. 5 V / VI / VIII / XV showed the same list in 1 and 2)

- **Confirmed root cause:**
  - In DEVICE V1, `lexV1SincronizarRelacoes` keyed layers 1/2 by **article** (`CF88:ART.5`) and called `carregarRelacoesDoArtigo("5")` once per article. It never reloaded while scrolling inside art. 5.
  - That legacy loader uses the per-article indices (`JUR_LOOKUP.IDX` / `REL_LOOKUP.IDX`) with "most specific key, then ARTICLE" fallback. It also ran before `contextoJuridicoAtivo` was updated, so it saw the previous context.
  - `LEGACY_JUR_LIST(ART.5)` = key `CF88|5||||` = RG 113, RG 969, RG 995. V, VI and XV have no inciso key, so even a fresh load falls back to that article list.
  - `LEGACY_CORRELATA_LIST(ART.5)` has no article key. The only art. 5 key is `INC.XLIII` (Lei 13.260/2016). Whatever was loaded first stayed for every inciso.
- **Fix (firmware only; data, overlay and legacy caches untouched):**
  - `lexV1CarregarRelacoesTarget(tid)`: `REF_LOOKUP` exact key (`lexv1Find(..., floor=false)`), then the `REF_PAYLOAD` rows while the key equals `tid`, then `lexV1ClassificarDestino`. CORRELATA goes only to list 1, JURISPRUDENCIA only to list 2; WORK_REFERENCE and hidden rows never enter 1/2.
  - The chosen item is resolved **by its link id** in the legacy PSRAM caches (`JURISPRUDENCIA.IDX` row `STF:RG:995:CF88:5:-:-:-`, `RELACOES.IDX` row `REL_…`), so opening a thesis or an external law works as in v7.12.0. All 279 jurisprudence and 44 correlata ids resolve.
  - `lexV1SincronizarRelacoes` now only discards lists of another target (no I/O). Keys 1/2 call `lexV1AbrirRelacaoTarget(corr, alvo)`: availability for that target, exact load (once per target), then the legacy list screen. LAYER_TARGET = ACTIVE_TARGET until BACK.
  - The footer mask uses `lexV1Disp.correlatas/juris` = TARGETS flags C/J. The audit shows they are derived from the exact records (0 mismatches over all targets). Flags only gate availability; lists always come from the records.
  - With no record in the exact target, the option is hidden and the key ignored. There is no fallback to the parent.
  - Other laws (non-V1 file) and flag 0 keep the legacy path (`carregarRelacoesDoArtigo` only when `!v1`).
- **Exact data** (`tools/canonical_layer_audit.py`, `CANONICAL_LAYERS_AUDIT.json`):

  | Target | Correlatas | Jurisprudência | Referências |
  |---|---|---|---|
  | CF88:ART.5 (article line) | – | – | – |
  | CF88:ART.5:CAPUT | – | RG 113 | A Revolução dos Bichos, Filadélfia |
  | 5.IV | – | – | 1984, The Post, V de Vingança |
  | 5.V | – | **RG 995** | – |
  | 5.VI | – | – | Timbuktu |
  | 5.VIII | – | **RG 1021, RG 386** | Timbuktu |
  | 5.IX | – | – | 1984, The Post |
  | 5.XIV | – | – | Chernobyl |
  | 5.XV | – | – | Papers, Please |
  | 5.XVI | – | – | – |
  | 5.XVII | – | – | – |
  | 37.§6 | – | RG 1031, 130, 362, 365, 940 | – |

  - 37 §6 lists only its 5 theses, not the article's other 22 (caput RG 66, XI ×10, …).
  - Export (432 links: 279 J, 101 W, 44 C, 8 hidden) grouped by target vs device query: CORRELATA 0, JURISPRUDENCIA 0, REFERENCIA 0 mismatches.
- **Known limitation (not changed, needs a decision):**
  - The approved TEXT_MAP maps the article line to `ART.n`, never `ART.n:CAPUT` (TARGET_RESOLUTION_STRATEGY).
  - 20 link targets are never ACTIVE_TARGET: 17 `:CAPUT` targets holding the 32 visible links (25 W, 6 J, 1 C), plus art. 40 §4 II/III and §7 I, which hold only 6 HISTORICAL_HIDDEN rows. Example: RG 113 at 5 caput. Layer 4 already behaved this way. (Resolved by the CAPUT EQUIVALENCE section below.)
  - No `ART.n → ART.n:CAPUT` alias was invented.
- **Tests:** new `tests/test_canonical_layers.py` (19: J1/J2 fixture, prefix keys, fail closed, 432 grouped, art. 5 table, V≠VI, 37 §6, Papers Please / Timbuktu, legacy explanation, source contract).
  - DEVICE 129/129, ENTENDA 80/80, LEGAL_TARGET_ID 47/47.
- **Build:**
  - flag 1: 1.074.119 B / 125.612 B;
  - flag 0: 989.395 B / 124.452 B (identical to v7.12.0).
- **Candidate:** `candidate_canonical_flag1/candidate_app_canonical.bin`, 1.074.272 B, sha256 `fe014b1f…2a86`, checksum and hash valid. Source `.ino` sha256 `6a1078d9…9d75`.
- **Flash:** app0 only at 0x10000 (erase 0x10000–0x116FFF), hash verified. Readback of 1.074.272 B byte-identical.
- **Boot** (`canonical_boot_serial.bin`):
  - 1 reset (POWERON); no Guru Meditation, panic or FAIL_IO;
  - `runtime hash CONFERE`; `DIAG PASS 33/0 MAX_OPEN_COUNT=4`; `JUR CACHE 178/296`.
- SD not written. Not committed.

## CAPUT EQUIVALENCE (approved rule: ART.n ↔ ART.n:CAPUT only on the visual caput)

- **Rule (resolution only, DEVICE V1 layers 1/2/4).** `lexV1QueryKeysForActiveTarget(tid)` is the only equivalence:
  - `CF88:ART.n` (the TEXT_MAP article line, i.e. the visual caput) → `[CF88:ART.n, CF88:ART.n:CAPUT]`;
  - any other target → `[tid]`.

  No data changed: REF_PAYLOAD, target_ids and the 432 links are untouched.
- **Lists:** each key is read exactly (`lexV1LerRegistrosChave`: exact lookup, stop at the first row of another key), classified, and unioned.
  - Dedup is by (destination_layer, SOURCE_ID), since REFERENCE_ID embeds `@target` and is never shared between keys.
  - The layer-4 detail is looked up by the link's real key (`CF88:ART.5:CAPUT|REF-LIV-0006`).
- **Availability:** the `ART.n` flags do not include `:CAPUT` (`CF88:ART.5` = `E----X`, `CF88:ART.5:CAPUT` = `--JWR-`).
  - C/J/W = OR of the exact flags of each query key, which is the same union the list uses: footer == list for every mapped target.
  - ENTENDA comes only from ACTIVE_TARGET (unchanged; its own DIRECT/BLOCK semantics).
- **Data:**
  - 32 visible links on 17 `:CAPUT` targets (25 WORK_REFERENCE, 6 JURISPRUDENCE, 1 CORRELATA), listed in `CANONICAL_LAYERS_AUDIT.json` → `caput_equivalence.visible_links`;
  - all 32 are reachable only from their own article line; 0 unreachable;
  - duplicates between ART.n and ART.n:CAPUT: 0;
  - leaks to descendants: 0. The union equals the export groups for every mapped target (0 mismatches).
- **Checks:**
  - art. 5 caput → 2 JURIS. RG 113, 4 REF. A Revolução dos Bichos + Filadélfia;
  - 5.V → RG 995 only; 5.VI → none; 5.VIII → RG 1021, 386 (no RG 113 anywhere below the caput);
  - art. 37 caput → RG 66; §6 → its 5 theses, no RG 66 in any art. 37 descendant.
- **Tests:** new `tests/test_caput_equivalence.py` (12):
  - query keys;
  - fixture union, dedup and no-descendant tests;
  - RG 113 caput and inciso exclusion;
  - art. 37 paragraph exclusion;
  - 32/17 reachability;
  - no leak and footer == list;
  - detail key;
  - ENTENDA untouched.

  Source-contract strings updated in routing / UI / canonical tests. DEVICE 141/141, ENTENDA 80/80, LEGAL_TARGET_ID 47/47.
- **Build:**
  - flag 1: 1.075.603 B / 125.612 B;
  - flag 0: 989.395 B / 124.452 B (identical to v7.12.0).
- **Candidate:** `candidate_caput_flag1/candidate_app_caput.bin`, 1.075.744 B, sha256 `c01e923a…1a90`, checksum and hash valid. Source `.ino` sha256 `f06cdc14…81ed`.
- **Flash:** app0 only at 0x10000 (erase 0x10000–0x116FFF), hash verified. Readback of 1.075.744 B byte-identical.
- **Boot** (`caput_boot_serial.bin`):
  - 1 reset (POWERON); no Guru Meditation, panic or FAIL_IO;
  - `runtime hash CONFERE`; `DIAG PASS 33/0 MAX_OPEN_COUNT=4`; `JUR CACHE 178/296`.
- SD not written. Not committed.
