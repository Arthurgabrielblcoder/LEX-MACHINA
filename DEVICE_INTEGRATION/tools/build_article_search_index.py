"""ARTICLE_SEARCH.IDX — compact binary article index for the DEVICE V1 article search (generic, any norm / indexed text).

Built on the PC from the CANONICAL structure, never from loose regex over the text:
  * --target-index : runtime target index JSON (LEGAL_TARGET_ID grammar; kind ARTIGO + line_start), bound to the text by sha256;
  * --text         : the exact displayed text (bytes indexed);
  * --text-map     : optional <NORM>_TEXT_MAP.IDX cross-check (each article row must be the map row at its offset).
Only structural ARTIGO targets enter: remissions such as "art. 2º da Lei nº ..." are not targets, so they are never indexed.

Binary format (little-endian), schema 1
  header (96 B)
    0  magic       8s   b'LXARTIX1'
    8  schema      u16  1
   10  header_size u16  96
   12  record_size u16  12
   14  ns_count    u16  namespaces in the table below
   16  records     u32
   20  source_bytes u32 size of the indexed text
   24  source_sha256 32s raw sha256 of the indexed text   (fail closed if it differs from the displayed text)
   56  body_sha256   32s raw sha256 of namespace table + records (integrity of everything after the header)
   88  reserved    8s   zero
  namespace table: ns_count x 16 B, ASCII, NUL padded (e.g. "CF88", "ADCT"), in text order of first appearance
  records (12 B each), sorted by (number, suffix, occurrence):
    u16 number      article number (1..65535)
    u8  suffix      0 = none, 1..26 = '-A'..'-Z' (e.g. 29-A -> (29, 1)); not reachable from the numeric keypad today
    u8  ns          index into the namespace table
    u32 offset      byte offset of the article line (line start) in the indexed text
    u16 occurrence  0-based order of this (number, suffix) in the text
    u16 reserved    0
Lookup: lower_bound on (number, suffix) -> occurrences are contiguous -> occurrence k = record[lb + k]. O(log n).
Usage: python build_article_search_index.py --text T --target-index J [--text-map M] --out OUT.IDX [--manifest OUT.json]
       python build_article_search_index.py --all --corpus-root DIR --output-dir DIR [...]   (whole corpus: article_index_corpus.py)
all_occurrences=True (corpus mode): one record per heading OCCURRENCE of the article (a repeated label, e.g. the preamble 'Art. 1º'
of a decree-law followed by the code's own 'Art. 1º', or a quoted amending text, keeps every line in text order, as the linear search
finds them); default False = one record per target at its line_start (approved CF88/CC2002 indexes, which have no repeated label).
"""
import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

MAGIC, SCHEMA, HEADER, RECORD, NS_SIZE = b'LXARTIX1', 1, 96, 12, 16
ART = re.compile(r'^(?P<ns>[A-Z0-9]+):ART\.(?P<num>\d+)(?:-(?P<suf>[A-Z]))?$')


class IndexError_(ValueError):
    pass


def line_starts(data):
    starts = [0]
    for i, b in enumerate(data):
        if b == 0x0A:
            starts.append(i + 1)
    return starts


def heading_offset(data, starts, lineno):
    """Byte offset of the heading of the article whose parser line is `lineno` (1-based). A heading split by the source
    ('Art.' alone, number on the next line) starts at the 'Art.' line: the parser joins them and records the number line."""
    off = starts[lineno - 1]
    if data[off:off + 12].decode('utf-8', 'replace').lstrip().lower().startswith('art'):
        return off
    j = lineno - 1
    while j > 0:
        j -= 1
        prev = data[starts[j]:starts[j + 1]].decode('utf-8', 'replace').strip()
        if prev:
            return starts[j] if prev.rstrip('.') in ('Art', 'art') else off
    return off


def build(text_path, target_index_path, text_map_path=None, all_occurrences=False, target_index=None):
    data = Path(text_path).read_bytes()
    idx = target_index if target_index is not None else json.loads(Path(target_index_path).read_text(encoding='utf-8'))
    src_sha = hashlib.sha256(data).hexdigest()
    if idx['source']['sha256'] != src_sha or idx['source']['bytes'] != len(data):
        raise IndexError_('TARGET_INDEX_NOT_BUILT_FROM_THIS_TEXT')
    starts = line_starts(data)
    mapped = None
    if text_map_path:
        mapped = {}
        for l in Path(text_map_path).read_text(encoding='utf-8').splitlines():
            if l and not l.startswith('#'):
                p = l.split('|')
                mapped[int(p[0])] = p[2]
    ns_order, recs = [], []
    for t in idx['targets']:
        if t['kind'] != 'ARTIGO':
            continue
        m = ART.match(t['target_id'])
        if not m:
            raise IndexError_(f"UNSUPPORTED_ARTICLE_ID {t['target_id']}")
        num, suf = int(m['num']), (ord(m['suf']) - 64 if m['suf'] else 0)
        if not 1 <= num <= 0xFFFF:
            raise IndexError_(f"ARTICLE_NUMBER_OUT_OF_RANGE {t['target_id']}")
        if m['ns'] not in ns_order:
            ns_order.append(m['ns'])
        for line in (t['occurrences'] if all_occurrences else [t['line_start']]):
            off = heading_offset(data, starts, line) if all_occurrences else starts[line - 1]
            head = data[off:off + 12].decode('utf-8', 'replace').lstrip()
            if not head.lower().startswith('art'):
                raise IndexError_(f"ARTICLE_LINE_MISMATCH {t['target_id']} {head!r}")
            if mapped is not None and mapped.get(off) != t['target_id']:
                raise IndexError_(f"TEXT_MAP_MISMATCH {t['target_id']} @ {off}: {mapped.get(off)}")
            recs.append([num, suf, ns_order.index(m['ns']), off, t['target_id']])
    if len(ns_order) > 255 or any(len(n) >= NS_SIZE for n in ns_order):
        raise IndexError_('NAMESPACE_TABLE')
    recs.sort(key=lambda r: (r[0], r[1], r[3]))                     # occurrence order = text order
    occ, prev = 0, None
    for r in recs:
        occ = occ + 1 if prev == (r[0], r[1]) else 0
        prev = (r[0], r[1])
        r.insert(4, occ)
    body = b''.join(n.encode('ascii').ljust(NS_SIZE, b'\0') for n in ns_order)
    body += b''.join(struct.pack('<HBBIHH', r[0], r[1], r[2], r[3], r[4], 0) for r in recs)
    header = struct.pack('<8sHHHHII32s32s8s', MAGIC, SCHEMA, HEADER, RECORD, len(ns_order), len(recs), len(data),
                         bytes.fromhex(src_sha), hashlib.sha256(body).digest(), b'\0' * 8)
    assert len(header) == HEADER
    blob = header + body
    manifest = dict(schema='LXARTIX1', schema_version=SCHEMA, record_size=RECORD, header_size=HEADER, records=len(recs),
                    namespaces=ns_order, bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
                    source=dict(path=Path(text_path).name, bytes=len(data), sha256=src_sha),
                    target_index=dict(path=Path(target_index_path).name if target_index_path else None,
                                      sha256=hashlib.sha256(Path(target_index_path).read_bytes()).hexdigest() if target_index_path else None,
                                      target_index_sha256=idx.get('target_index_sha256')),
                    text_map=dict(path=Path(text_map_path).name, sha256=hashlib.sha256(Path(text_map_path).read_bytes()).hexdigest()) if text_map_path else None,
                    by_namespace={n: sum(1 for r in recs if ns_order[r[2]] == n) for n in ns_order},
                    suffixed=[r[5] for r in recs if r[1]], multi_occurrence_keys=sum(1 for r in recs if r[4] == 1))
    return blob, manifest


class ArticleIndex:
    """Reader with the same algorithm as the firmware (lower_bound + contiguous occurrences); counts comparisons."""

    def __init__(self, blob, source=None):
        if len(blob) < HEADER:
            raise IndexError_('SHORT')
        magic, schema, hsize, rsize, nsc, n, sbytes, ssha, bsha, _ = struct.unpack('<8sHHHHII32s32s8s', blob[:HEADER])
        if (magic, schema, hsize, rsize) != (MAGIC, SCHEMA, HEADER, RECORD):
            raise IndexError_('SCHEMA')
        body = blob[HEADER:]
        if len(body) != nsc * NS_SIZE + n * RECORD or hashlib.sha256(body).digest() != bsha:
            raise IndexError_('BODY_HASH')
        if source is not None and (len(source) != sbytes or hashlib.sha256(source).digest() != ssha):
            raise IndexError_('SOURCE_MISMATCH')
        self.ns = [body[i * NS_SIZE:(i + 1) * NS_SIZE].rstrip(b'\0').decode('ascii') for i in range(nsc)]
        r0 = nsc * NS_SIZE
        self.recs = [struct.unpack('<HBBIHH', body[r0 + i * RECORD:r0 + (i + 1) * RECORD]) for i in range(n)]
        self.source_bytes, self.source_sha256, self.comparisons = sbytes, ssha.hex(), 0

    def lower_bound(self, num, suf=0):
        lo, hi = 0, len(self.recs)
        while lo < hi:
            mid = (lo + hi) // 2
            self.comparisons += 1
            if (self.recs[mid][0], self.recs[mid][1]) < (num, suf):
                lo = mid + 1
            else:
                hi = mid
        return lo

    def find(self, num, suf=0, start_offset=0):
        """First occurrence of (num, suf) with offset >= start_offset -> (offset, namespace, occurrence) or None."""
        i = self.lower_bound(num, suf)
        while i < len(self.recs) and (self.recs[i][0], self.recs[i][1]) == (num, suf):
            self.comparisons += 1
            if self.recs[i][3] >= start_offset:
                return self.recs[i][3], self.ns[self.recs[i][2]], self.recs[i][4]
            i += 1
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--text')
    ap.add_argument('--target-index')
    ap.add_argument('--text-map')
    ap.add_argument('--out')
    ap.add_argument('--manifest')
    ap.add_argument('--all', action='store_true', help='whole corpus (Catalogo Mestre + updater locator): one index per norm + catalog')
    ap.add_argument('--corpus-root', help='vade mecum root (SD or a local copy of it)')
    ap.add_argument('--output-dir', help='staging: SD/99_LEX_V1/10_TARGETS/*_ARTICLE_SEARCH.IDX + catalog, _host/ manifest + report')
    ap.add_argument('--previous-dir', help='previous staging (incremental KEEP/REBUILD/ADD/REMOVE); default: the approved V1 package')
    ap.add_argument('--physical-manifest', help='manifest of the last validated physical SD (PHYSICAL_HASH_CONFIRMED)')
    ap.add_argument('--runtime', help='CF88 runtime text opened by the device (default: <corpus-root>/99_LEX_V1/... or the approved package)')
    a = ap.parse_args()
    if a.all:
        import article_index_corpus as C
        if not (a.corpus_root and a.output_dir):
            ap.error('--all needs --corpus-root and --output-dir')
        man = C.build_corpus(a.corpus_root, a.output_dir, previous_dir=a.previous_dir or C.APPROVED_STAGING,
                             physical_manifest=a.physical_manifest, runtime_path=a.runtime)
        print(C.report_text(man), end='')
        return 0 if not man['summary']['BLOCKED'] else 2
    if not (a.text and a.target_index and a.out):
        ap.error('--text, --target-index and --out (or --all)')
    blob, man = build(a.text, a.target_index, a.text_map)
    ArticleIndex(blob, Path(a.text).read_bytes())                 # self-check
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_bytes(blob)
    if a.manifest:
        Path(a.manifest).parent.mkdir(parents=True, exist_ok=True)
        Path(a.manifest).write_bytes((json.dumps(dict(man, file=Path(a.out).name), ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({k: man[k] for k in ('records', 'bytes', 'sha256', 'namespaces', 'by_namespace')}))


if __name__ == '__main__':
    sys.exit(main())
