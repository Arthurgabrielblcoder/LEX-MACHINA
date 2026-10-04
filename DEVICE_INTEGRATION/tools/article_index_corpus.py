"""FULL-CORPUS ARTICLE_SEARCH.IDX: one LXARTIX1 v1 index per norm of the operational corpus + ARTICLE_SEARCH_CATALOG.IDX + incremental update.

Discovery (no norm list in this code):
  * norms   = Catalogo Mestre (updater/catalogo_mestre_vademecum.json, itens[].id = NORMA_ID, also the LEGAL_TARGET_ID norm registry);
  * text    = the updater's own locator (updater/main.py inventariar_vademecum + localizar_item_mestre) over the vade mecum root:
              exactly ONE TXT per norm, the file the reader opens from that norm's folder;
  * CF88    = device redirect: the reader opens /99_LEX_V1/05_TEXT/CF88_RUNTIME.txt (CF88 + ADCT) instead of cf.txt. Its index is produced
              by the V1 package pipeline (build_sd_staging, TEXT_MAP cross-check) and is only verified and kept here.
Structure (no second parser): LEGAL_TARGET_ID structural parser in strict mode (article_case_sensitive + remission_guard), the parser of
the approved CC2002 index (reproduced byte-identically); every heading OCCURRENCE is a record (build(..., all_occurrences=True)).
A norm gets an index only when the whole text is understood; otherwise INDEX_BUILD_BLOCKED (norm, file, line, reason), never a partial
index:
  * NO_STRUCTURE_FOUND / NO_ARTICLE_HEADINGS                  the parser finds no article;
  * SOURCE_NOT_PLAIN_TEXT                                     e.g. UTF-16 HTML stored as bytes (letters separated by spaces);
  * UNPARSED_ARTICLE_HEADING                                  a line-start 'Art<dots/spaces><digit>' that is neither a parsed heading nor a
                                                              remission ('Art . 2º' with a space before the dot);
  * ORACLE_MISMATCH                                           indexed lookup != linear structural scan (see legacy_structural_scan).
Oracle = the linear structural search of the device, re-implemented over raw bytes: every line start, the device context parser
(context_parser_port.apply_line = contexto_juridico.h) on the line ('Art.' alone joined with the next line), capital 'Art' only and the
same remission words. For EVERY article key of the norm the indexed occurrence walk (find(n, s, start=prev+1)) must equal the scan.

Incremental update (Updater): previous manifest/staging -> KEEP (same source bytes+sha256, same builder, valid index), REBUILD (source or
builder changed; identical output is reported as KEEP), ADD (new norm), REMOVE (norm no longer in the corpus: index dropped from the
staging), BLOCKED. Output is deterministic (no clock): same corpus -> same files, bytes and hashes.

ARTICLE_SEARCH_CATALOG.IDX (LXARTCT1 v1, little-endian), so the device does not open every index header:
  header 64 B: magic 8s 'LXARTCT1' | u16 schema 1 | u16 header_size 64 | u16 entry_size 56 | u16 reserved | u32 entries |
               32s body_sha256 (sha256 of all entries) | 12s zero
  entry 56 B:  u32 source_bytes | u32 index_bytes | 32s source_sha256 (raw) | 16s NORMA_ID (ASCII, NUL padded)
  entries sorted by (source_bytes, source_sha256, norma). Index file = /99_LEX_V1/10_TARGETS/<NORMA_ID>_ARTICLE_SEARCH.IDX.
The catalog only SELECTS: the chosen index is still fully validated against the open text (bytes + sha256 + body sha256).
"""
import bisect
import hashlib
import json
import re
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
ROOT = DI.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_article_search_index as AI  # noqa: E402
import build_target_index as BTI  # noqa: E402
import context_parser_port as P  # noqa: E402
import structure_parser as SP  # noqa: E402

CATALOG_JSON = ROOT / 'updater/catalogo_mestre_vademecum.json'
SD_DIR = '99_LEX_V1/10_TARGETS'
SUFFIX = '_ARTICLE_SEARCH.IDX'
CATALOG_NAME = 'ARTICLE_SEARCH_CATALOG.IDX'
CAT_MAGIC, CAT_SCHEMA, CAT_HEADER, CAT_ENTRY, NORMA_SIZE = b'LXARTCT1', 1, 64, 56, 16
# Builder identity recorded in the manifest. Bump when the produced bytes may change for the same source (parser/index rules).
BUILDER = dict(version='LXARTIX1-corpus-1', parser='LEGAL_TARGET_ID/structure_parser.py', article_case_sensitive=True, remission_guard=True,
               heading_variants=True, all_occurrences=True)
RUNTIME_REDIRECT = {'CF88': '99_LEX_V1/05_TEXT/CF88_RUNTIME.txt'}          # device: cf.txt -> V1 runtime (firmware abrirPastaSelecionada)
APPROVED_STAGING = DI / 'staging_sd_v1_batch04_run3_candidate'             # physically approved V1 package (runtime + CF88/CC2002 indexes)
LOOSE_HEADING = re.compile(r'^Art[\s.]*\d')
CITATION_RE = re.compile(r'^Art\. [\d.]+(?:º|°|o)?(?:-[A-Z])?\s*[,;]')            # 'Art. 101, I, ...' = citation list, not a heading
DOUBLE_SUFFIX_RE = re.compile(r'^Art\. [\d.]+(?:º|°|o)?-[A-Z]-[A-Z](?![A-Za-z])')   # 'Art. 359-M-A' (not representable)
RANGE_RE = re.compile(r'^Arts\.?\s*(\d{1,3}(?:\.\d{3})*|\d+)(?:º|°|o)?(?:-[A-Z])?\s*(?:a|e|,)\s*(\d{1,3}(?:\.\d{3})*|\d+)')


class CorpusError(ValueError):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------- discovery
def updater_locator():
    """(inventory_fn(root), locate_fn(item, inventory)) of the AUTHORITATIVE updater backend (updater/main.py)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('lex_updater_main', ROOT / 'updater/main.py')
    sys.path.insert(0, str(ROOT / 'updater'))
    U = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(U)
    U.ARQUIVO_CATALOGO_MESTRE = CATALOG_JSON

    def inventory(root):
        U.configurar_destino(str(root))
        return U.inventariar_vademecum()
    return inventory, U.localizar_item_mestre


def discover(corpus_root, items=None, locator=None):
    """Catalog items -> one located text each. -> list of dict(norma, rel, path, status)."""
    corpus_root = Path(corpus_root)
    items = items if items is not None else json.loads(CATALOG_JSON.read_text(encoding='utf-8'))['itens']
    inventory, locate = locator or updater_locator()
    inv = inventory(corpus_root)
    out, seen = [], set()
    for it in items:
        norma = str(it['id']).strip()
        if norma in seen:
            raise CorpusError(f'DUPLICATE_NORMA_ID {norma}')
        seen.add(norma)
        cands = locate(it, inv)
        cands = cands if isinstance(cands, list) else [cands]
        if len(cands) != 1:
            out.append(dict(norma=norma, rel=None, path=None, status='NOT_LOCATED' if not cands else 'AMBIGUOUS',
                            candidates=sorted(Path(c).relative_to(corpus_root).as_posix() for c in cands)))
            continue
        p = Path(cands[0])
        out.append(dict(norma=norma, rel=p.relative_to(corpus_root).as_posix(), path=p, status='LOCATED'))
    return out


# ---------------------------------------------------------------- oracle (linear structural scan over raw bytes)
NL, WS = bytes([10]), bytes([32, 9, 13])


def _lines(data):
    starts = AI.line_starts(data)
    return [(starts[i], data[starts[i]:(starts[i + 1] - 1 if i + 1 < len(starts) else len(data))]) for i in range(len(starts))]


def legacy_structural_scan(data):
    """[(label, offset)] in text order, straight over the raw bytes (no parser state, no target index, no namespaces): every line
    start, capital 'Art' only, 'Art.' alone joined with the next non-empty line (offset = the 'Art.' line), the same heading grammar
    (SP.ART_RE_CS + SP.heading_variant) and the same remission words. Independent of the index path (target index -> occurrences ->
    LXARTIX1 encoding -> lower_bound/occurrence walk), it checks that path end to end."""
    lines = _lines(data)
    txt = [r.decode('utf-8', 'replace').strip().lstrip('\ufeff') for _, r in lines]
    hits, prev = [], ''
    for k, (off, raw) in enumerate(lines):
        s = txt[k]
        if not s:
            continue
        ctx_prev, prev = prev, s
        if not s.startswith('Art'):
            continue
        after = [t for t in txt[k + 1:k + 9] if t]
        if SP.ART_ALONE_RE_CS.match(s):
            s = 'Art. ' + (after[0] if after else '')
            after = after[1:]
        s, used = SP.join_split_heading(SP.heading_variant(s), after[:2])
        m = SP.ART_RE_CS.match(s)
        if not m or SP.remission_heading(m, ctx_prev, after[used] if len(after) > used else ''):
            continue
        hits.append((m.group(1).replace('.', '') + ('-' + m.group(2) if m.group(2) else ''), off))
    return hits


LEGACY_LINE_RE = re.compile(rb'(?m)^[ \t]*[Aa][Rr][Tt](?:igo)?\.?[ \t]*(\d+)(?![0-9]|\.[0-9])')


def legacy_delta(data, blob):
    """Old device search WITHOUT index (pesquisarArtigo: line start, 'art'/'artigo', the typed digits, not followed by a digit or
    '.digit') vs the index, per (line, number) for plain keys. legacy_only = lines the old search lands on that are not article headings
    of the norm (lowercase 'art.' remissions, 'Art. 3º-A' taken as 3, '(Renumerado do' + 'Art. 83 pelo...'); index_only = headings the
    old search never reaches ('Art.' / number split over lines, thousands 'Art. 1.000', 'Art . 2º'). Informative (the oracle is
    legacy_structural_scan)."""
    starts = AI.line_starts(data)
    leg = {(bisect.bisect_right(starts, m.start()), int(m.group(1))) for m in LEGACY_LINE_RE.finditer(data)}
    ai = AI.ArticleIndex(blob, data)
    idx = {(bisect.bisect_right(starts, r[3]), r[0]) for r in ai.recs if r[1] == 0}
    return dict(legacy_hits=len(leg), index_plain_records=len(idx), legacy_only=len(leg - idx), index_only=len(idx - leg))


def device_context_agreement(data, hits):
    """CONTEXTO label the DEVICE parser (contexto_juridico.h port) shows on each indexed heading line. Display-only metric: the index
    lands on the line; a different label there is a context-parser limitation ('Art. 8º-A' read as 8, 'Art.1.992.' unread)."""
    diff = []
    for label, off in hits:
        end = data.find(NL, off)
        line = data[off:end if end >= 0 else len(data)].strip(WS)
        c = dict(artigo='', paragrafo='', inciso='', alinea='')
        P.apply_line(c, line[:511])
        if c['artigo'] != label:
            diff.append(dict(offset=off, indexed=label, device_context=c['artigo'] or None))
    return dict(headings=len(hits), agree=len(hits) - len(diff), differ=len(diff), examples=diff[:5])


def _key(label):
    m = re.fullmatch(r'(\d+)(?:-([A-Z]))?', label)
    return (int(m[1]), ord(m[2]) - 64 if m[2] else 0) if m else None


def equivalence(blob, data):
    """Indexed occurrence walk == oracle for every article key of the text (and no key outside it). -> dict(ok, keys, mismatches)."""
    ai = AI.ArticleIndex(blob, data)
    oracle = {}
    for label, off in legacy_structural_scan(data):
        k = _key(label)
        if k is None:
            return dict(ok=False, keys=0, mismatches=[dict(key=label, indexed=[], oracle=[off], reason='UNSUPPORTED_LABEL')])
        oracle.setdefault(k, []).append(off)
    keys = sorted(set(oracle) | {(r[0], r[1]) for r in ai.recs})
    bad = []
    for k in keys:
        walk, start = [], 0
        while True:
            hit = ai.find(k[0], k[1], start)
            if hit is None:
                break
            walk.append(hit[0])
            start = hit[0] + 1
        if walk != oracle.get(k, []):
            bad.append(dict(key=f'{k[0]}' + (f'-{chr(64 + k[1])}' if k[1] else ''), indexed=walk[:6], oracle=oracle.get(k, [])[:6]))
    top = max((k[0] for k in keys), default=0)
    for n in range(1, top + 6):                                   # absent numbers: nothing, never a neighbour (no 'ART.2' for 2.000)
        if (n, 0) not in oracle and ai.find(n) is not None:
            bad.append(dict(key=str(n), indexed=[ai.find(n)[0]], oracle=[]))
    return dict(ok=not bad, keys=len(keys), mismatches=bad[:20])


# ---------------------------------------------------------------- per-norm audit + build
def audit_text(norma, data, target_index):
    text = data.decode('utf-8-sig', 'replace')
    L = text.splitlines()
    arts = [t for t in target_index['targets'] if t['kind'] == 'ARTIGO']
    starts = AI.line_starts(data)
    occ_lines = set()
    for t in arts:                                             # heading line of each occurrence ('Art.' alone -> that line)
        for o in t['occurrences']:
            occ_lines.add(bisect.bisect_right(starts, AI.heading_offset(data, starts, o)))
    skipped = {a['line'] for a in target_index['anomalies'] if a['code'] == 'REMISSION_HEADING_SKIPPED'}
    loose = [(i, SP.heading_variant(s.strip())) for i, s in enumerate(L, 1)
             if LOOSE_HEADING.match(s.strip()) and i not in occ_lines and i not in skipped]
    citations = [(i, s[:70]) for i, s in loose if CITATION_RE.match(s)]
    unrepresentable = [(i, s[:70]) for i, s in loose if DOUBLE_SUFFIX_RE.match(s)]
    unparsed = [(i, s[:70]) for i, s in loose if not CITATION_RE.match(s) and not DOUBLE_SUFFIX_RE.match(s)]
    keys, occ_order = [], []
    for t in arts:
        k = _key(t['target_id'].split(':ART.', 1)[1])
        keys += [k] * len(t['occurrences'])
        occ_order += t['occurrences']
    nums = sorted({k[0] for k in keys})
    order = [k for _, k in sorted(zip(occ_order, keys))]                 # keys in text order
    ranges = [(i, s.strip()[:60]) for i, s in enumerate(L, 1) if RANGE_RE.match(s.strip())]
    revoked = sum(1 for t in arts if t.get('preview') and re.search(r'\(\s*Revogad', t['preview'] or '', re.I))
    first = min(keys) if keys else None
    return dict(
        articles=len({t['target_id'] for t in arts}), heading_occurrences=len(keys), max_article=nums[-1] if nums else 0,
        first_article=first and (first[0], first[1]), has_above_999=bool(nums and nums[-1] > 999), above_999_count=sum(1 for n in nums if n > 999), suffixed=sorted({f'{k[0]}-{chr(64 + k[1])}' for k in keys if k[1]}, key=lambda s: _key(s)),
        repeated_keys=sorted({f'{k[0]}' + (f'-{chr(64 + k[1])}' if k[1] else '') for k in keys if keys.count(k) > 1}, key=_key),
        out_of_order_headings=sum(1 for i, k in enumerate(order) if i and k < max(order[:i])),
        revoked_collective_ranges=ranges, revoked_single_headings=revoked, remission_lines_skipped=sorted(skipped),
        unparsed_headings=unparsed[:10], unparsed_count=len(unparsed), citation_lines=len(citations),
        unrepresentable_labels_excluded=unrepresentable,
        heading_variants_read=[a['line'] for a in target_index['anomalies'] if a['code'] == 'HEADING_VARIANT_READ'][:20])


def build_norm(norma, path):
    """-> (blob|None, manifest, audit, blocked|None)."""
    data = Path(path).read_bytes()
    text = data.decode('utf-8-sig', 'replace')
    if 'ÿþ' in text[:4000] or re.search(r'(?:\b\w ){12}', text[:20000]):
        line = next((i for i, l in enumerate(text.splitlines(), 1) if 'ÿþ' in l or re.search(r'(?:\b\w ){6}', l)), 1)
        return None, None, None, dict(reason='SOURCE_NOT_PLAIN_TEXT', line=line,
                                      detail='UTF-16 HTML stored as text (BOM ÿþ, letters separated by spaces); fix the text in the Updater')
    try:
        ti = BTI.build(norma, path, article_case_sensitive=BUILDER['article_case_sensitive'], remission_guard=BUILDER['remission_guard'],
                       heading_variants=BUILDER['heading_variants'])
    except Exception as e:                                     # TargetIdError NO_STRUCTURE_FOUND, grammar errors
        return None, None, None, dict(reason='NO_STRUCTURE_FOUND', line=0, detail=str(e))
    aud = audit_text(norma, data, ti)
    if aud['heading_occurrences'] == 0:
        return None, None, aud, dict(reason='NO_ARTICLE_HEADINGS', line=0, detail='no structural article heading')
    if aud['unparsed_count']:
        i, s = aud['unparsed_headings'][0]
        return None, None, aud, dict(reason='UNPARSED_ARTICLE_HEADING', line=i, detail=f'{aud["unparsed_count"]} line(s) like {s!r}')
    try:
        blob, man = AI.build(path, None, all_occurrences=True, target_index=ti)
    except AI.IndexError_ as e:
        return None, None, aud, dict(reason='INDEX_BUILD_ERROR', line=0, detail=str(e))
    eq = equivalence(blob, data)
    aud['equivalence'] = dict(ok=eq['ok'], keys=eq['keys'])
    aud['device_context'] = device_context_agreement(data, legacy_structural_scan(data))
    aud['legacy_delta'] = legacy_delta(data, blob)
    if not eq['ok']:
        m0 = eq['mismatches'][0]
        off = (m0['indexed'] or m0['oracle'] or [0])[0]
        return None, None, aud, dict(reason='ORACLE_MISMATCH', line=data[:off].count(b'\n') + 1, detail=json.dumps(eq['mismatches'][:3]))
    return blob, man, aud, None


def verify_kept(blob, data):
    AI.ArticleIndex(blob, data)                                # header, body sha256 and source bytes + sha256
    eq = equivalence(blob, data)
    if not eq['ok']:
        raise CorpusError(f'KEPT_INDEX_ORACLE_MISMATCH {eq["mismatches"][:2]}')
    return eq


# ---------------------------------------------------------------- catalog
def build_catalog(entries):
    """entries: [(norma, source_bytes, source_sha256_hex, index_bytes)] -> LXARTCT1 blob."""
    rows = sorted(entries, key=lambda e: (e[1], e[2], e[0]))
    if len({e[0] for e in rows}) != len(rows):
        raise CorpusError('CATALOG_DUPLICATE_NORMA')
    body = b''
    for norma, sbytes, ssha, ibytes in rows:
        if not re.fullmatch(r'[A-Z0-9]{1,15}', norma):
            raise CorpusError(f'CATALOG_NORMA_ID {norma}')
        body += struct.pack('<II32s16s', sbytes, ibytes, bytes.fromhex(ssha), norma.encode('ascii').ljust(NORMA_SIZE, b'\0'))
    head = struct.pack('<8sHHHHI32s12s', CAT_MAGIC, CAT_SCHEMA, CAT_HEADER, CAT_ENTRY, 0, len(rows), hashlib.sha256(body).digest(), b'\0' * 12)
    assert len(head) == CAT_HEADER
    return head + body


def read_catalog(blob):
    """Python mirror of the firmware catalog reader: any inconsistency -> CorpusError (the firmware then ignores the catalog)."""
    if len(blob) < CAT_HEADER:
        raise CorpusError('CATALOG_SHORT')
    magic, schema, hsz, esz, _, n, bsha, _ = struct.unpack('<8sHHHHI32s12s', blob[:CAT_HEADER])
    if (magic, schema, hsz, esz) != (CAT_MAGIC, CAT_SCHEMA, CAT_HEADER, CAT_ENTRY) or len(blob) != CAT_HEADER + n * CAT_ENTRY:
        raise CorpusError('CATALOG_SCHEMA')
    if hashlib.sha256(blob[CAT_HEADER:]).digest() != bsha:
        raise CorpusError('CATALOG_BODY_SHA256')
    out = []
    for i in range(n):
        sb, ib, ssha, norma = struct.unpack('<II32s16s', blob[CAT_HEADER + i * CAT_ENTRY:CAT_HEADER + (i + 1) * CAT_ENTRY])
        out.append(dict(norma=norma.rstrip(b'\0').decode('ascii'), source_bytes=sb, index_bytes=ib, source_sha256=ssha.hex()))
    return out


# ---------------------------------------------------------------- previous state (incremental)
def previous_state(prev_dir):
    """norma -> dict(source_bytes, source_sha256, index_sha256, builder, blob). From a previous manifest, or (seed) from the index files
    present in a staging (e.g. the physically approved V1 package: CF88/CC2002)."""
    if not prev_dir:
        return {}
    prev_dir = Path(prev_dir)
    tdir = prev_dir / 'SD' / SD_DIR
    man_p = prev_dir / '_host/ARTICLE_INDEX_MANIFEST.json'
    man = json.loads(man_p.read_text(encoding='utf-8')) if man_p.is_file() else None
    out = {}
    for p in sorted(tdir.glob('*' + SUFFIX)) if tdir.is_dir() else []:
        blob = p.read_bytes()
        norma = p.name[:-len(SUFFIX)]
        _, _, _, _, _, _, sbytes, ssha, _, _ = struct.unpack('<8sHHHHII32s32s8s', blob[:AI.HEADER])
        rec = (man or {}).get('norms', {}).get(norma, {})
        out[norma] = dict(source_bytes=sbytes, source_sha256=ssha.hex(), index_sha256=sha(blob), builder=rec.get('builder'), blob=blob,
                          source_rel=rec.get('source_rel'))
    return out


# ---------------------------------------------------------------- corpus build
def build_corpus(corpus_root, out_dir, previous_dir=None, physical_manifest=None, runtime_path=None, items=None, locator=None,
                 approved_staging=APPROVED_STAGING, source_overrides=None):
    """source_overrides: {NORMA_ID: path} = candidate text that REPLACES the located file of that norm (same SD path), e.g. a
    repaired source not yet on the card (its physical status is then NEEDS_PHYSICAL_HASH_CONFIRMATION until deployed)."""
    corpus_root, out_dir = Path(corpus_root), Path(out_dir)
    prev = previous_state(previous_dir)
    phys = json.loads(Path(physical_manifest).read_text(encoding='utf-8'))['entries'] if physical_manifest and Path(physical_manifest).is_file() else None
    found = discover(corpus_root, items, locator)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    tdir = out_dir / 'SD' / SD_DIR
    tdir.mkdir(parents=True)
    (out_dir / '_host').mkdir()
    norms, cat_entries, blocked = {}, [], []
    for d in found:
        norma = d['norma']
        rec = dict(norma=norma, discovery=d['status'], source_rel=d['rel'])
        if d['status'] != 'LOCATED':
            rec.update(status='BLOCKED', blocked=dict(reason=d['status'], line=0, detail=json.dumps(d.get('candidates', []))))
            blocked.append(dict(norma=norma, file=None, **rec['blocked']))
            norms[norma] = rec
            continue
        src = Path((source_overrides or {}).get(norma, d['path']))
        if norma in (source_overrides or {}):
            rec['source_override'] = True
        if norma in RUNTIME_REDIRECT:                          # the device opens the V1 runtime, not the catalog text
            rt_rel = RUNTIME_REDIRECT[norma]
            rt = Path(runtime_path) if runtime_path else (corpus_root / rt_rel if (corpus_root / rt_rel).is_file() else approved_staging / 'SD' / rt_rel)
            rec.update(catalog_text=d['rel'], source_rel=rt_rel, device_redirect=True)
            src = rt
        data = src.read_bytes()
        rec.update(source_bytes=len(data), source_sha256=sha(data))
        if phys is not None:
            ph = phys.get(rec['source_rel'])
            rec['physical'] = ('PHYSICAL_HASH_CONFIRMED' if ph and (ph['bytes'], ph['sha256']) == (len(data), rec['source_sha256'])
                               else 'NEEDS_PHYSICAL_HASH_CONFIRMATION')
        else:
            rec['physical'] = 'NEEDS_PHYSICAL_HASH_CONFIRMATION'
        p = prev.get(norma)
        same_src = bool(p) and (p['source_bytes'], p['source_sha256']) == (len(data), rec['source_sha256'])
        if norma in RUNTIME_REDIRECT:
            # managed by the V1 package: kept only if the previous index matches the runtime and passes the oracle
            if not same_src:
                rec.update(status='BLOCKED', blocked=dict(reason='MANAGED_BY_V1_PACKAGE', line=0,
                                                          detail='CF88 runtime index is built by build_sd_staging (TEXT_MAP); none valid for this runtime'))
                blocked.append(dict(norma=norma, file=rec['source_rel'], **rec['blocked']))
                norms[norma] = rec
                continue
            eq = verify_kept(p['blob'], data)
            blob, action, aud = p['blob'], 'KEEP', dict(equivalence=dict(ok=True, keys=eq['keys']), managed_by='build_sd_staging')
            hdr = AI.ArticleIndex(blob, data)
            aud['legacy_delta'] = legacy_delta(data, blob)
            aud.update(articles=None, heading_occurrences=len(hdr.recs), max_article=max(r[0] for r in hdr.recs),
                       has_above_999=max(r[0] for r in hdr.recs) > 999, namespaces=hdr.ns)
        else:
            blob, man, aud, blk = build_norm(norma, src)
            if blk:
                rec.update(status='BLOCKED', blocked=blk, audit=aud)
                blocked.append(dict(norma=norma, file=rec['source_rel'], **blk))
                norms[norma] = rec
                continue
            if p and same_src and sha(blob) == p['index_sha256']:
                action = 'KEEP'                                # identical source -> identical index (verified, not assumed)
            elif p:
                action = 'REBUILD'
            else:
                action = 'ADD'
        name = norma + SUFFIX
        (tdir / name).write_bytes(blob)
        hdr = AI.ArticleIndex(blob, data)
        rec.update(status=action, index=dict(file=f'/{SD_DIR}/{name}', bytes=len(blob), sha256=sha(blob), records=len(hdr.recs),
                                             namespaces=hdr.ns), builder=BUILDER if norma not in RUNTIME_REDIRECT else dict(version='build_sd_staging'),
                   audit=aud)
        cat_entries.append((norma, len(data), rec['source_sha256'], len(blob)))
        norms[norma] = rec
    removed = sorted(set(prev) - set(norms))
    for n in removed:
        norms[n] = dict(norma=n, status='REMOVE', previous_index_sha256=prev[n]['index_sha256'])
    cat = build_catalog(cat_entries)
    (tdir / CATALOG_NAME).write_bytes(cat)
    files = {p.relative_to(out_dir / 'SD').as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
             for p in sorted((out_dir / 'SD').rglob('*')) if p.is_file()}
    counts = {k: sum(1 for r in norms.values() if r['status'] == k) for k in ('KEEP', 'REBUILD', 'ADD', 'REMOVE', 'BLOCKED')}
    sizes = sorted(r['index']['bytes'] for r in norms.values() if 'index' in r)
    biggest = max((r for r in norms.values() if 'index' in r), key=lambda r: (r['index']['bytes'], r['norma']), default=None)
    summary = dict(
        norms_analysed=len(found), indexes=len(sizes), **counts,
        records_total=sum(r['index']['records'] for r in norms.values() if 'index' in r),
        index_storage_bytes=sum(sizes), catalog_bytes=len(cat), staging_files=len(files), staging_bytes=sum(f['bytes'] for f in files.values()),
        index_bytes_mean=round(sum(sizes) / len(sizes), 1) if sizes else 0,
        index_bytes_median=(sizes[len(sizes) // 2] if len(sizes) % 2 else
                            (sizes[len(sizes) // 2 - 1] + sizes[len(sizes) // 2]) / 2) if sizes else 0,
        index_bytes_max=sizes[-1] if sizes else 0, index_bytes_max_norma=biggest['norma'] if biggest else None,
        index_bytes_min=sizes[0] if sizes else 0,
        psram_runtime_worst_bytes=sizes[-1] if sizes else 0,
        namespaces_unique=len({r['norma'] for r in norms.values() if 'index' in r}) == len(sizes),
        physical_confirmed=sum(1 for r in norms.values() if r.get('physical') == 'PHYSICAL_HASH_CONFIRMED'),
        needs_physical_confirmation=sorted(r['norma'] for r in norms.values() if r.get('physical') == 'NEEDS_PHYSICAL_HASH_CONFIRMATION'))
    manifest = dict(schema='ARTICLE_INDEX_MANIFEST', schema_version=1, builder=BUILDER, catalog=dict(file=f'/{SD_DIR}/{CATALOG_NAME}', bytes=len(cat),
                    sha256=sha(cat), entries=len(cat_entries), format='LXARTCT1 v1'), summary=summary, blocked=blocked, norms=norms, files=files)
    (out_dir / '_host/ARTICLE_INDEX_MANIFEST.json').write_bytes((json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + '\n').encode('utf-8'))
    (out_dir / '_host/ARTICLE_INDEX_REPORT.txt').write_bytes(report_text(manifest).encode('utf-8'))
    return manifest


def report_text(man):
    s = man['summary']
    L = ['ARTICLE INDEXES',
         f"Normas analisadas: {s['norms_analysed']}",
         f"Indices mantidos: {s['KEEP']}",
         f"Regenerados: {s['REBUILD']}",
         f"Novos: {s['ADD']}",
         f"Removidos: {s['REMOVE']}",
         f"Bloqueados: {s['BLOCKED']}",
         f"Records totais: {s['records_total']}",
         f"Storage total: {s['index_storage_bytes']} B (+ catalogo {s['catalog_bytes']} B)",
         f"Maior indice: {s['index_bytes_max']} B ({s['index_bytes_max_norma']})"]
    for b in man['blocked']:
        L.append(f"  INDEX_BUILD_BLOCKED {b['norma']} | {b['file']} | linha {b['line']} | {b['reason']} | {b['detail'][:160]}")
    return '\n'.join(L) + '\n'


def tree(d):
    return {p.relative_to(d).as_posix(): sha(p.read_bytes()) for p in sorted(Path(d).rglob('*')) if p.is_file()}
