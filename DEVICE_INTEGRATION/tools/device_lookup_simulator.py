"""DEVICE INTEGRATION V1 - host-side simulator of the ESP32 lookups on the SD overlay (/99_LEX_V1).

It reproduces what the firmware is expected to do with small fixed buffers:
  * never loads an index or payload file into memory;
  * binary search directly on the sorted text index (seek to the middle, resync to the next LF, compare the key);
  * a short final scan inside a window of at most WINDOW bytes;
  * payloads are read with one seek + one read of BYTES (ENTENDA) or COUNT lines (References).
Every call reports the number of seeks and bytes read, so a linear scan would be visible.

Usage:
  python device_lookup_simulator.py [--sd DIR] CF88.5.V CF88.25 ...
  python device_lookup_simulator.py --demo          (mission test cases)
  python device_lookup_simulator.py --bench N       (repeated lookups over every target)
"""
import argparse
import json
import math
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SD = HERE.parent / 'staging_sd_v1' / 'SD' / '99_LEX_V1'
WINDOW = 512           # bytes: final linear window of the binary search (lines are < 200 bytes)
ROMAN = re.compile(r'^[IVXLCDM]+$')
DEMO = ['CF88.5', 'CF88.5.V', 'CF88.7.XII', 'CF88.8.I', 'CF88.12.5', 'CF88.20.XI', 'CF88.21.XXIV', 'CF88.22.XXIX',
        'CF88.24.4', 'CF88.37', 'CF88.37.6', 'CF88.37.10', 'CF88.60', 'CF88.60.4', 'CF88.60.4.IV', 'CF88.150', 'CF88.225',
        'ADCT.10.II', 'CF88.25', 'CF88.999', 'CF88.5.XCIX']


class Stats:
    def __init__(self):
        self.seeks = 0
        self.bytes = 0
        self.lines = 0


class SortedIndex:
    """Pipe-separated, LF, header lines '#...' at the top, data sorted bytewise by the first field."""

    def __init__(self, path):
        self.path = Path(path)
        self.fh = open(self.path, 'rb')
        self.size = self.path.stat().st_size
        self.header = {}
        pos = 0
        while True:
            self.fh.seek(pos)
            line = self.fh.readline()
            if not line.startswith(b'#'):
                break
            parts = line.decode('utf-8').rstrip('\n')[1:].split('|')
            self.header[parts[0]] = parts[1:]
            pos += len(line)
        self.start = pos

    def close(self):
        self.fh.close()

    def _readline(self, st):
        line = self.fh.readline()
        st.bytes += len(line)
        st.lines += 1
        return line

    def find(self, key, st=None, floor=False):
        """Exact row for `key` (or, with floor=True, the last row whose key <= key). Returns list of fields or None."""
        st = st or Stats()
        k = key.encode('utf-8')
        lo, hi = self.start, self.size
        while hi - lo > WINDOW:
            mid = (lo + hi) // 2
            self.fh.seek(mid)
            st.seeks += 1
            self._readline(st)                       # discard the partial line
            p = self.fh.tell()
            if p >= hi:
                hi = mid
                continue
            line = self._readline(st)
            if line.split(b'|', 1)[0] < k:
                lo = p
            else:
                hi = p
        self.fh.seek(lo)
        st.seeks += 1
        prev = None
        while self.fh.tell() < self.size:
            line = self._readline(st)
            lk = line.split(b'|', 1)[0]
            if lk == k:
                return line.decode('utf-8').rstrip('\n').split('|')
            if lk > k:
                break
            prev = line
            if self.fh.tell() > hi + WINDOW:
                break
        if floor and prev is not None:
            return prev.decode('utf-8').rstrip('\n').split('|')
        return None


class Device:
    def __init__(self, sd=DEFAULT_SD):
        sd = Path(sd)
        self.sd = sd
        self.targets = SortedIndex(sd / '10_TARGETS/CF88_TARGETS.IDX')
        self.text_map = SortedIndex(sd / '10_TARGETS/CF88_TEXT_MAP.IDX')
        self.ent = SortedIndex(sd / '30_ENTENDA/ENTENDA_LOOKUP.IDX')
        self.ref = SortedIndex(sd / '20_REFERENCES/REF_LOOKUP.IDX')
        self.ent_payload = open(sd / '30_ENTENDA/ENTENDA_PAYLOAD.DAT', 'rb')
        self.ref_payload = open(sd / '20_REFERENCES/REF_PAYLOAD.IDX', 'rb')

    def close(self):
        for x in (self.targets, self.text_map, self.ent, self.ref):
            x.close()
        self.ent_payload.close()
        self.ref_payload.close()

    # ---- identification
    @staticmethod
    def canonical(query):
        """'CF88.5.V' / 'CF88.12.5' / 'CF88.1.PU' / 'CF88:ART.5:INC.V' -> canonical target_id (None if malformed)."""
        q = query.strip()
        if ':' in q:
            return q
        parts = q.split('.')
        if len(parts) < 2 or parts[0] not in ('CF88', 'ADCT') or not re.match(r'^\d+(-[A-Z])?$', parts[1]):
            return None
        out = [parts[0], f'ART.{parts[1]}']
        for p in parts[2:]:
            if p.isdigit():
                out.append(f'PAR.{p}')
            elif p.upper() in ('PU', 'UNICO'):
                out.append('PAR.UNICO')
            elif ROMAN.match(p):
                out.append(f'INC.{p}')
            elif re.match(r'^[a-z]$', p):
                out.append(f'AL.{p}')
            else:
                return None
        return ':'.join(out)

    @staticmethod
    def from_context(artigo, paragrafo='', inciso='', alinea='', namespace='CF88'):
        """Firmware tuple (ContextoJuridicoAtivo) -> canonical target_id. 'unico' -> PAR.UNICO."""
        out = [namespace, f'ART.{artigo}']
        if paragrafo:
            out.append('PAR.UNICO' if paragrafo.lower() == 'unico' else f'PAR.{paragrafo}')
        if inciso:
            out.append(f'INC.{inciso}')
        if alinea:
            out.append(f'AL.{alinea}')
        return ':'.join(out)

    def resolve_text_position(self, offset, displayed_bytes, displayed_sha256, st=None):
        """Device contract (A2B): the map is used only if it is a RUNTIME map and BOTH size and sha256 of the displayed file match
        the header; otherwise FAIL_CLOSED (no target, no layers)."""
        h = self.text_map.header
        if h.get('RUNTIME_STATUS', [''])[0] != 'RUNTIME':
            return dict(status='FAIL_CLOSED', reason='TEXT_MAP_NOT_RUNTIME', target_id=None)
        if str(displayed_bytes) != h.get('SOURCE_BYTES', [''])[0]:
            return dict(status='FAIL_CLOSED', reason='SOURCE_BYTES_MISMATCH', target_id=None)
        if not displayed_sha256 or displayed_sha256 != h.get('SOURCE_SHA256', [''])[0]:
            return dict(status='FAIL_CLOSED', reason='SOURCE_SHA256_MISMATCH', target_id=None)
        return dict(status='OK', reason=None, target_id=self.target_at_offset(offset, st))

    def verify_runtime_file(self, path=None):
        """What the firmware does once per boot: size + streamed sha256 of the displayed runtime text vs the TEXT_MAP header."""
        import hashlib
        p = Path(path) if path else self.sd / '05_TEXT/CF88_RUNTIME.txt'
        h = hashlib.sha256()
        with open(p, 'rb') as fh:
            for b in iter(lambda: fh.read(4096), b''):
                h.update(b)
        return p.stat().st_size, h.hexdigest()

    def target_at_offset(self, offset, st=None):
        """Position in the structural text (cf.txt with the header sha256) -> target_id (floor search in CF88_TEXT_MAP.IDX)."""
        row = self.text_map.find(f'{offset:010d}', st, floor=True)
        return row[2] if row else None

    # ---- layers
    def entenda(self, target_id, st=None):
        row = self.ent.find(target_id, st)
        if not row:
            return None
        off, n = int(row[1]), int(row[2])
        self.ent_payload.seek(off)
        blob = self.ent_payload.read(n)
        if st:
            st.seeks += 1
            st.bytes += len(blob)
        meta = {}
        for line in blob.decode('utf-8').split('\n'):
            if line.startswith('#'):
                break                                  # metadata only; sections are streamed on demand by the UI
            if '|' in line:
                k, v = line.split('|', 1)
                meta.setdefault(k, v)
        return dict(resolution_type=row[7], anchor_target_id=meta.get('T'), explanation_id=row[3], display_title=meta.get('D'),
                    payload_offset=off, payload_length=n, review=row[6], validity=row[4], blob=blob)

    def references(self, target_id, st=None):
        row = self.ref.find(target_id, st)
        if not row:
            return []
        off, n = int(row[1]), int(row[2])
        self.ref_payload.seek(off)
        if st:
            st.seeks += 1
        out = []
        for _ in range(n):
            line = self.ref_payload.readline()
            if st:
                st.bytes += len(line)
            out.append(line.decode('utf-8').rstrip('\n').split('|'))
        return out

    def query(self, q):
        st = Stats()
        t0 = time.perf_counter()
        tid = self.canonical(q)
        res = dict(requested=q, target_id=tid)
        trow = self.targets.find(tid, st) if tid else None
        if not trow:
            res.update(status='INVALID_OR_UNKNOWN_TARGET', entenda_available=False, references=0, resolution_type='NONE')
        else:
            res.update(status='OK', kind=trow[1], legal_status=trow[2], flags=trow[3], layers=self.layers(trow[3]))
            e = self.entenda(tid, st)
            refs = self.references(tid, st)
            res.update(references=len(refs), entenda_available=bool(e))
            if e:
                res.update({k: v for k, v in e.items() if k != 'blob'})
            else:
                res.update(resolution_type='NONE', parent_context=self.parent_with_entenda(tid, st))
        res.update(lookup_us=round((time.perf_counter() - t0) * 1e6, 1), seeks=st.seeks, bytes_read=st.bytes)
        return res

    @staticmethod
    def layers(flags):
        """CF88_TARGETS.IDX FLAGS (6 chars) -> UI flags of UI_LAYER_CONTRACT_V1."""
        f = flags.ljust(6, '-')
        return dict(HAS_LEI=True, HAS_ENTENDA=f[0] in 'EB', BLOCK_COVERED=f[0] == 'B', HAS_CORRELATAS=f[1] == 'C',
                    HAS_JURISPRUDENCIA=f[2] == 'J', HAS_REFERENCIAS=f[3] == 'W', HAS_ANY_REFERENCE_ROW=f[4] == 'R',
                    EXTERNAL_NOTES_AVAILABLE=f[5] == 'X')

    def parent_with_entenda(self, tid, st=None):
        """Optional UI hint (never presented as the target's own explanation): nearest ancestor with an approved ENTENDA."""
        parts = tid.split(':')
        while len(parts) > 2:
            parts = parts[:-1]
            e = self.ent.find(':'.join(parts), st)
            if e:
                return ':'.join(parts)
        return None


def bench(dev, repeat):
    ids = [l.split('|')[0] for l in (dev.sd / '10_TARGETS/CF88_TARGETS.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
    out = {}
    for name, fn in (('targets', lambda t, st: dev.targets.find(t, st)), ('entenda_lookup', lambda t, st: dev.ent.find(t, st)),
                     ('entenda_lookup+payload', lambda t, st: dev.entenda(t, st)), ('references_lookup+payload', lambda t, st: dev.references(t, st))):
        worst, total_seeks, n = 0, 0, 0
        t0 = time.perf_counter()
        for _ in range(repeat):
            for t in ids:
                st = Stats()
                fn(t, st)
                worst = max(worst, st.seeks)
                total_seeks += st.seeks
                n += 1
        dt = time.perf_counter() - t0
        out[name] = dict(queries=n, mean_us=round(dt / n * 1e6, 2), max_seeks=worst, mean_seeks=round(total_seeks / n, 2))
    # BLOCK resolution = the covered target's own lookup row (no extra hop)
    covered = [l.split('|')[0] for l in (dev.sd / '30_ENTENDA/ENTENDA_LOOKUP.IDX').read_text(encoding='utf-8').splitlines() if l.endswith('|COVERED_BY_BLOCK')]
    t0 = time.perf_counter()
    for _ in range(repeat):
        for t in covered:
            dev.entenda(t, Stats())
    out['block_resolution'] = dict(queries=len(covered) * repeat, mean_us=round((time.perf_counter() - t0) / max(1, len(covered) * repeat) * 1e6, 2))
    out['log2_bound'] = {k: math.ceil(math.log2(max(2, (dev.sd / p).stat().st_size / WINDOW))) + 2 for k, p in
                         (('targets', '10_TARGETS/CF88_TARGETS.IDX'), ('entenda', '30_ENTENDA/ENTENDA_LOOKUP.IDX'), ('references', '20_REFERENCES/REF_LOOKUP.IDX'))}
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument('queries', nargs='*')
    ap.add_argument('--sd', default=str(DEFAULT_SD))
    ap.add_argument('--demo', action='store_true')
    ap.add_argument('--bench', type=int, default=0)
    a = ap.parse_args()
    dev = Device(a.sd)
    try:
        if a.bench:
            print(json.dumps(bench(dev, a.bench), indent=1))
            return
        for q in (DEMO if a.demo else a.queries):
            r = dev.query(q)
            print(json.dumps(r, ensure_ascii=False))
    finally:
        dev.close()


if __name__ == '__main__':
    main()
