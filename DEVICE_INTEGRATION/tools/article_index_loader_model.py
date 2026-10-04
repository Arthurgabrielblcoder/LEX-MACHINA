"""Loader scale model for the full-corpus article indexes: Python mirror of the firmware selection (lexV1ArtIdxPronto) with operation
counts and a CONSERVATIVE time model calibrated on physical logs of this device (ESP32-S3, microSD over SPI):

  open (SD.open path lookup)      17.3 ms   boot 'LEXV1: TIME open_indices_us=52014' for 3 opens
  read + sha256                   0.977 ms/KB  '[ARTIDX] TEXT_SHA bytes=660268 ms=645' (CC2002)
  directory entry listed          7.2 ms    remainder of '[ARTIDX] LOADED ... load_ms=103' (CF88: dir open + 4 entries + 2 headers +
                                            5.216 B index) and of 'load_ms=767' - 645 ms text sha (CC2002, 25.036 B): both give
                                            4 entries x 7.15 ms; ALL unexplained time is attributed to listing (upper bound).
The sha256 of the opened TEXT (needed once per text, any strategy) is reported separately, never as index-selection cost.

Strategies:
  GENERIC_CAP8   current firmware: list *_ARTICLE_SEARCH.IDX names (at most LEXV1_ARTIDX_MAX_CANDIDATOS = 8, FAT order), open each
                 header (96 B), keep the ones whose source size = text size.
  GENERIC_ALL    same, without the cap (what the generic scan would cost to reach every index).
  CATALOG        ARTICLE_SEARCH_CATALOG.IDX: one open, 64 B + 56 B per norm read entry by entry, candidates by size (fast path).
After selection every strategy loads ONE index (open + read + body sha256) into PSRAM.
"""
import hashlib
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import article_index_corpus as C  # noqa: E402

OPEN_MS, ENTRY_MS, KB_MS = 17.3, 7.2, 0.977
CAP = 8
SUFFIX = '_ARTICLE_SEARCH.IDX'


def _hdr(blob):
    return struct.unpack('<8sHHHHII32s32s8s', blob[:96])


def select(directory, text_bytes, text_sha, strategy, catalog_name=C.CATALOG_NAME):
    """directory: ordered list of (name, bytes) as the FAT directory lists /99_LEX_V1/10_TARGETS. -> dict(index, state, ops, ms, fd_peak).
    State: LOADED | SEM_INDICE | NENHUM_INDICE_VALIDO | UNREACHABLE (an index for this text exists but the strategy cannot see it)."""
    files = dict(directory)
    ops = dict(dir_entries=0, headers=0, opens=0, bytes_read=0)
    fd_peak = 1
    cands = []
    if strategy == 'CATALOG' and catalog_name in files:
        ops['opens'] += 1
        cat = files[catalog_name]
        try:
            entries = C.read_catalog(cat)
            ops['bytes_read'] += len(cat)
            cands = [(f"{e['norma']}{SUFFIX}", e['source_sha256']) for e in entries if e['source_bytes'] == text_bytes][:CAP]
        except C.CorpusError:
            ops['bytes_read'] += len(cat)
            strategy = 'GENERIC_CAP8'                          # invalid catalog -> previous generic scan
    elif strategy == 'CATALOG':
        strategy = 'GENERIC_CAP8'                              # absent catalog -> previous generic scan
    if strategy.startswith('GENERIC'):
        ops['opens'] += 1                                      # directory
        names = []
        for name, _ in directory:
            if strategy == 'GENERIC_CAP8' and len(names) >= CAP:
                break
            ops['dir_entries'] += 1
            if name.endswith(SUFFIX):
                names.append(name)
        ops['dir_entries'] += 1 if strategy == 'GENERIC_ALL' or len(names) < CAP else 0   # end of directory
        for n in names:
            ops['headers'] += 1
            ops['opens'] += 1
            ops['bytes_read'] += 96
            h = _hdr(files[n])
            if h[0] == b'LXARTIX1' and h[6] == text_bytes:
                cands.append((n, h[7].hex()))
        fd_peak = 1                                            # directory closed before any header is opened (one FD at a time)
    sel_ms = ops['opens'] * OPEN_MS + ops['dir_entries'] * ENTRY_MS + ops['bytes_read'] / 1024 * KB_MS
    state, index, load_ms = 'SEM_INDICE', None, 0.0
    for n, ssha in cands:
        if ssha != text_sha:
            continue
        blob = files.get(n)
        ok = blob is not None and _hdr(blob)[0] == b'LXARTIX1' and _hdr(blob)[6] == text_bytes and _hdr(blob)[7].hex() == text_sha \
            and hashlib.sha256(blob[96:]).digest() == _hdr(blob)[8]
        load_ms = OPEN_MS + (len(blob) if blob else 0) / 1024 * KB_MS
        if ok:
            state, index = 'LOADED', n
            break
        state = 'NENHUM_INDICE_VALIDO'
    if state != 'LOADED' and cands and state == 'SEM_INDICE':
        state = 'NENHUM_INDICE_VALIDO'
    if state == 'SEM_INDICE':
        target = [n for n, b in directory if n.endswith(SUFFIX) and _hdr(b)[6] == text_bytes and _hdr(b)[7].hex() == text_sha]
        if target:
            state = 'UNREACHABLE'
    return dict(strategy=strategy, state=state, index=index, ops=ops, selection_ms=round(sel_ms, 1), load_ms=round(load_ms, 1),
                fd_peak=fd_peak, psram_bytes=len(files[index]) if index else 0)


def model(staging_sd, texts, physical_order=('CF88_TARGETS.IDX', 'CF88_TEXT_MAP.IDX', 'CF88_ARTICLE_SEARCH.IDX', 'CC2002_ARTICLE_SEARCH.IDX')):
    """staging_sd: <staging>/SD/99_LEX_V1/10_TARGETS (indexes + catalog); texts: {norma: (bytes, sha)}.
    Directory order = the physical SD today (V1 files + CF88/CC2002 indexes first, as created) + the new files in name order."""
    tdir = Path(staging_sd)
    present = {p.name: p.read_bytes() for p in sorted(tdir.iterdir()) if p.is_file()}
    present.setdefault('CF88_TARGETS.IDX', b'not an article index')
    present.setdefault('CF88_TEXT_MAP.IDX', b'not an article index')
    order = [n for n in physical_order if n in present] + sorted(n for n in present if n not in physical_order)
    directory = [(n, present[n]) for n in order]
    out = {}
    for strategy in ('GENERIC_CAP8', 'GENERIC_ALL', 'CATALOG'):
        rows = {norma: select(directory, b, s, strategy) for norma, (b, s) in texts.items()}
        sel = [r['selection_ms'] for r in rows.values()]
        out[strategy] = dict(
            loaded=sum(r['state'] == 'LOADED' for r in rows.values()), unreachable=sorted(n for n, r in rows.items() if r['state'] == 'UNREACHABLE'),
            other=sorted((n, r['state']) for n, r in rows.items() if r['state'] not in ('LOADED', 'UNREACHABLE')),
            selection_ms_max=max(sel), selection_ms_mean=round(sum(sel) / len(sel), 1),
            headers_max=max(r['ops']['headers'] for r in rows.values()), dir_entries_max=max(r['ops']['dir_entries'] for r in rows.values()),
            bytes_read_max=max(r['ops']['bytes_read'] for r in rows.values()), fd_peak=max(r['fd_peak'] for r in rows.values()),
            psram_max=max(r['psram_bytes'] for r in rows.values()), load_ms_max=max(r['load_ms'] for r in rows.values()))
    out['directory_entries'] = len(directory)
    out['text_sha_ms'] = {n: round(b / 1024 * KB_MS) for n, (b, _) in sorted(texts.items(), key=lambda kv: -kv[1][0])[:5]}
    return out
