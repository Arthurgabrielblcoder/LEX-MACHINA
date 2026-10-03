# -*- coding: utf-8 -*-
"""Host replica of the DEVICE reader SCROLL path, OLD (baseline) vs NEW (BIDIRECTIONAL_SCROLL_PERFORMANCE_FIX), with I/O accounting.

Mirrors the firmware functions one by one (constants are READ from the sketch / headers, never re-typed):
  avancarUmaLinhaVisual, indexarAntesDaJanela (old: one physical line; new: lexIndexarAntesDaJanelaV1, block of lines),
  indexarAte, lerLinhaVisualParaBuffer, guardar/obterCheckpointContexto (ring of MAX_CHECKPOINTS_CONTEXTO),
  reconstruirContextoAntesOffset (old: checkpoint / 256 KiB window / TEXT_MAP seed; new: exact checkpoint without I/O ->
  checkpoint <= 2 KiB -> "Art." anchor validated by the parser -> TEXT_MAP seed -> 32 KiB fail-safe), recalcularContextosCache,
  carregarCacheLeitorCompleto (new: lexPrepararCacheBidirecional), atualizarCacheLeitor, rolarLeitor.
The legal parser is context_parser_port.apply_line (port of aplicarLinhaContextoJuridico) + the cf.txt compat look-ahead.

I/O model: OldFile = File::read() byte by byte (every byte = one call, 17.2 us/B measured on the device) + File::read(buf,n)
blocks; BufFile = LexArquivoBuffer (LEX_LEITOR_BLOCO-byte blocks). Bytes / seeks / opens / lines are exact for the algorithm;
times are ESTIMATES from rates measured on the device (see RATES).
"""
import re
from pathlib import Path

import context_parser_port as P
import reader_viewport as V

FW = V.FW
SRC = V.SKETCH.read_text(encoding='utf-8')
HDR = (FW / 'lex_leitor_scroll.h').read_text(encoding='utf-8')


def _d(name, src=SRC):
    return int(re.search(rf'#define {name} (\d+)u?\b', src).group(1))


C = dict(rows=_d('LEITOR_LINHAS_VISIVEIS'), max_lines=_d('MAX_LINHAS_INDEXADAS'), checkpoints=_d('MAX_CHECKPOINTS_CONTEXTO'),
         line_cap=_d('BYTES_CACHE_LINHA'), seed_min=_d('LEXV1_CTX_SEMENTE_MIN'),
         window=int(re.search(r'const uint32_t JANELA_RECONSTRUCAO=(\d+);', SRC).group(1)),
         prev_alvo=_d('LEX_CACHE_ANTERIOR_ALVO'), prev_min=_d('LEX_CACHE_ANTERIOR_MIN'),
         next_alvo=_d('LEX_CACHE_SEGUINTE_ALVO'), next_min=_d('LEX_CACHE_SEGUINTE_MIN'),
         refill_budget=_d('LEX_REFILL_ORCAMENTO'), par_max=_d('LEX_PARAGRAFO_MAX'), anchor_max=_d('LEX_CTX_ANCORA_MAX'),
         block=_d('LEX_LEITOR_BLOCO', HDR), old_back_block=256)

# Rates measured on the device (bench_serial.bin / session_serial.bin): per-byte File::read 17.2 us/B (11.293 s / 647.150 B =
# 17.45); SD.open+seek of the reader TXT ~3.4 ms (legacy path) / ~12.3 ms (/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt) from
# "PERF CONTEXTO_UP ... bytes=0"; TEXT_MAP seed ~68 ms (80 ms - 12 ms); block reads ~1.135 us/B (32 KiB scan) -> a 512 B read is
# modelled as 0.7 ms (conservative), CPU on bytes already in RAM 0.25 us/B; render floor (12 rows + footer, unchanged) ~98 ms
# (PERF SCROLL media 106,8 ms on DOWN steps minus I/O).
RATES = dict(old_byte_us=17.2, block_us=700.0, cpu_byte_us=0.25, textmap_us=68000.0, open_us={'legacy': 3400.0, 'cf': 12300.0},
             render_ms=98.0)


class Stats:
    FIELDS = ('opens', 'perbyte', 'blocks', 'block_bytes', 'cpu_bytes', 'textmap', 'ctx_lines', 'wrap_lines', 'anchors_checked')

    def __init__(self):
        for k in self.FIELDS:
            setattr(self, k, 0)

    def snap(self):
        return {k: getattr(self, k) for k in self.FIELDS}

    @staticmethod
    def diff(a, b):
        return {k: b[k] - a[k] for k in a}

    @staticmethod
    def io_bytes(d):
        return d['perbyte'] + d['block_bytes']

    @staticmethod
    def us(d, kind):
        r = RATES
        return (d['opens'] * r['open_us'][kind] + d['perbyte'] * r['old_byte_us'] + d['blocks'] * r['block_us'] +
                d['cpu_bytes'] * r['cpu_byte_us'] + d['textmap'] * r['textmap_us'])


class _FileBase:
    def __init__(self, m):
        self.m, self.d, self.n, self.pos = m, m.data, len(m.data), 0
        m.st.opens += 1

    def seek(self, p):
        if p > self.n:
            return False
        self.pos = p
        return True

    def available(self):
        return self.n - self.pos if self.pos < self.n else 0


class OldFile(_FileBase):
    """File: read() = one SD library call per byte; read(buf, n) = one block."""

    def read1(self):
        if self.pos >= self.n:
            return -1
        self.m.st.perbyte += 1
        b = self.d[self.pos]
        self.pos += 1
        return b

    def readblock(self, n):
        n = min(n, self.n - self.pos)
        self.m.st.blocks += 1
        self.m.st.block_bytes += n
        out = self.d[self.pos:self.pos + n]
        self.pos += n
        return out


class BufFile(_FileBase):
    """LexArquivoBuffer: read() served from a LEX_LEITOR_BLOCO block; read(buf, n) from the block when inside it, else direct."""

    def __init__(self, m):
        super().__init__(m)
        self.base, self.len = 0, 0

    def read1(self):
        if self.pos >= self.n:
            return -1
        if not (self.base <= self.pos < self.base + self.len):
            self.base, self.len = self.pos, min(C['block'], self.n - self.pos)
            self.m.st.blocks += 1
            self.m.st.block_bytes += self.len
        self.m.st.cpu_bytes += 1
        b = self.d[self.pos]
        self.pos += 1
        return b

    def contem(self, p):
        return self.len > 0 and self.base <= p < self.base + self.len

    def carregar_ate(self, fim):
        """LexArquivoBuffer::carregarAte: loads the block that ENDS at `fim`."""
        if fim <= 0:
            return False
        self.base = fim - C['block'] if fim > C['block'] else 0
        self.len = min(C['block'], self.n - self.base)
        self.m.st.blocks += 1
        self.m.st.block_bytes += self.len
        return self.contem(fim - 1)

    def byte_em(self, p):
        self.m.st.cpu_bytes += 1
        return self.d[p]

    def readblock(self, n):
        n = min(n, self.n - self.pos)
        if not (self.base <= self.pos and self.pos + n <= self.base + self.len):
            self.m.st.blocks += 1
            self.m.st.block_bytes += n
        self.m.st.cpu_bytes += n
        out = self.d[self.pos:self.pos + n]
        self.pos += n
        return out


def empty_ctx():
    return dict(artigo='', paragrafo='', inciso='', alinea='')


def ctx_key(c):
    return (c['artigo'], c['paragrafo'], c['inciso'], c['alinea'])


def isolated_marker(line):
    t = bytes(c for c in line.lstrip(b' \t') if c not in b' \t\r')[:7]
    return len(t) in (3, 4) and t[:3].lower() == b'art' and (len(t) == 3 or t[3:4] == b'.')


def starts_digit(line):
    t = line.lstrip(b' \t')
    return bool(t) and 48 <= t[0] <= 57


class Reader:
    """mode='old' | 'new'. kind='legacy' (non-V1 text, e.g. Codigo Civil) | 'cf' (V1 runtime: TEXT_MAP seed + centered landing).
    cf_compat: arquivoAtualEhConstituicao() (the runtime is opened as 'cf.txt')."""

    def __init__(self, data, mode, kind='legacy', text_map=None, cf_compat=False):
        self.data, self.n, self.mode, self.kind = data, len(data), mode, kind
        self.text_map, self.cf = text_map, cf_compat
        r = V.Reader.__new__(V.Reader)                      # reuse the validated wrap (glyph table read from the sketch)
        r.adv, c = V.glyph_advances(), V.firmware_constants()
        self.ROWS, self.WIDTH, self.ACTIVE, self._r = c['rows'], c['width'], c['active_row'], r
        self.st = Stats()
        self.cps, self.cp_next = [None] * C['checkpoints'], 0
        self.log = []
        self.reiniciar(0)

    def File(self):
        return BufFile(self) if self.mode == 'new' else OldFile(self)

    # ---------------- wrap ----------------
    def advance(self, f, start):
        """avancarUmaLinhaVisual(f, inicio, proximo) -> (temProxima, proximo)."""
        if not f.seek(start) or not f.available():
            return False, start
        px, last, found = 0, start, False
        while f.available():
            before = f.pos
            b0 = f.read1()
            if b0 == 0x0D:
                continue
            if b0 == 0x0A:
                return f.pos < self.n, f.pos
            cp = b0
            if b0 & 0xE0 == 0xC0:
                if f.available():
                    cp = ((b0 & 0x1F) << 6) | (f.read1() & 0x3F)
            elif b0 & 0xF0 == 0xE0:
                if f.available():
                    b1 = f.read1()
                    if f.available():
                        cp = ((b0 & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (f.read1() & 0x3F)
            elif b0 & 0xF8 == 0xF0:
                for _ in range(3):
                    if f.available():
                        f.read1()
                cp = ord('?')
            if cp == 0x09:
                cp = 0x20
            if cp in (0x20, 0xA0):
                last, found = f.pos, True
            av = self._r.advance(cp)
            if px + av > self.WIDTH:
                if found and last > start:
                    nxt = last
                elif before > start:
                    nxt = before
                else:
                    nxt = f.pos
                return nxt < self.n, nxt
            px += av
        return False, f.pos

    # ---------------- window ----------------
    def reiniciar(self, inicio=0):
        self.offs, self.top, self.end = [inicio], 0, inicio >= self.n
        self.cache_valid, self.cache_top = False, -1
        self.ctx_before = empty_ctx()
        self.lines, self.phys, self.valid, self.line_off, self.line_ctx = [b''] * self.ROWS, [False] * self.ROWS, [False] * self.ROWS, \
            [0] * self.ROWS, [empty_ctx() for _ in range(self.ROWS)]

    def _back_line_start(self, f, fim, block, cap):
        """Physical line start containing fim-1 (LF at fim-1 ignored). cap=None -> unbounded (old). -> (start, failsafe)."""
        floor = max(0, fim - cap) if cap else 0
        cur = fim
        while cur > floor:
            base = max(floor, cur - block)
            f.seek(base)
            buf = f.readblock(cur - base)
            for i in range(len(buf) - 1, -1, -1):
                if buf[i] == 0x0A and base + i < fim - 1:
                    return base + i + 1, False
            cur = base
        if floor == 0:
            return 0, False
        f.seek(floor)
        while f.available() and f.pos < fim:
            if f.read1() == 0x20:
                return f.pos, True
        return None, True

    def _back_line_start_new(self, f, fim):
        """lexInicioLinhaFisicaAntes (new): scans the LexArquivoBuffer block, loads the block ENDING at cursor only when needed."""
        floor = fim - C['par_max'] if fim > C['par_max'] else 0
        cur = fim
        while cur > floor:
            if not f.contem(cur - 1) and not f.carregar_ate(cur):
                return None, False
            base = max(f.base, floor)
            pos = cur
            while pos > base:
                pos -= 1
                if f.byte_em(pos) == 0x0A and pos < fim - 1:
                    return pos + 1, False
            cur = base
        if floor == 0:
            return 0, False
        f.seek(floor)
        while f.available() and f.pos < fim:
            if f.read1() == 0x20:
                return f.pos, True
        return None, True

    def indexar_antes(self):
        if not self.offs or self.offs[0] == 0:
            return 0
        f = self.File()
        limit = self.offs[0]
        if self.mode == 'old':
            start, _ = self._back_line_start(f, limit, C['old_back_block'], None)
            ring, cap = [], self.ROWS * 4
            pos = start
            while pos < limit:
                ring.append(pos)
                _, nxt = self.advance(f, pos)
                self.st.wrap_lines += 1
                if nxt <= pos:
                    return 0
                pos = nxt
            new = ring[-cap:]
            self.cache_valid, self.cache_top = False, -1
        else:
            cap, new, fim, fs = C['prev_alvo'], [], limit, False
            while len(new) < cap and fim > 0:
                if new and limit - fim >= C['refill_budget']:
                    break
                start, f1 = self._back_line_start_new(f, fim)
                fs = fs or f1
                if start is None:
                    break
                seg, pos, err = [], start, False
                while pos < fim:
                    seg.append(pos)
                    _, nxt = self.advance(f, pos)
                    self.st.wrap_lines += 1
                    if nxt <= pos:
                        err = True
                        break
                    pos = nxt
                if err:
                    break
                room = cap - len(new)
                new = seg[-room:] + new
                fim = start
            if fs:
                self.log.append(('REFILL_FAILSAFE', limit))
        if not new:
            return 0
        q = len(new)
        keep = min(len(self.offs), C['max_lines'] - q)
        if keep < len(self.offs):
            self.end = False
        self.offs = new + self.offs[:keep]
        self.top += q
        if self.mode == 'new':
            if self.cache_valid and self.cache_top >= 0 and self.cache_top + q + self.ROWS <= len(self.offs):
                self.cache_top += q
            else:
                self.cache_valid, self.cache_top = False, -1
        return q

    def indexar_ate(self, target):
        if self.end or target < len(self.offs) or len(self.offs) >= C['max_lines']:
            return
        f = self.File()
        while len(self.offs) <= target and not self.end and len(self.offs) < C['max_lines']:
            start = self.offs[-1]
            has, nxt = self.advance(f, start)
            self.st.wrap_lines += 1
            if nxt <= start or nxt >= self.n:
                self.end = True
                break
            self.offs.append(nxt)
            if not has:
                self.end = True

    def read_visual(self, f, idx):
        """lerLinhaVisualParaBuffer: text, inicioFisico."""
        start = self.offs[idx]
        end = self.offs[idx + 1] if idx + 1 < len(self.offs) else self.n
        phys = start == 0
        if start > 0 and f.seek(start - 1):
            phys = f.read1() == 0x0A
        f.seek(start)
        out = bytearray()
        while f.available() and f.pos < end and len(out) < C['line_cap'] - 4:
            b = f.read1()
            if b in (0x0D, 0x0A):
                continue
            out.append(b)
        return bytes(out).rstrip(b' \t'), phys

    # ---------------- context ----------------
    def cp_save(self, off, ctx):
        for e in self.cps:
            if e and e[0] == off:
                e[1] = dict(ctx)
                return
        self.cps[self.cp_next] = [off, dict(ctx)]
        self.cp_next = (self.cp_next + 1) % len(self.cps)

    def cp_get(self, limit):
        best = None
        for e in self.cps:
            if e and e[0] <= limit and (best is None or e[0] > best[0]):
                best = e
        return (best[0], dict(best[1])) if best else (None, None)

    def compat(self, ctx, line, phys, nxt=None):
        """aplicarLinhaContextoCompatCF: the cf.txt logical line is applied as a physical start; otherwise the parser rule."""
        if self.cf and nxt is not None and isolated_marker(line) and starts_digit(nxt):
            P.apply_line(ctx, (b'Art. ' + nxt)[:511])
            return
        if phys:
            P.apply_line(ctx, line[:511])

    def _readline(self, f, limit=None):
        out = bytearray()
        while f.available() and (limit is None or f.pos < limit):
            b = f.read1()
            if b == 0x0A:
                break
            if b != 0x0D:
                out.append(b)
        return bytes(out)

    def _seed(self, limit, checkpoint):
        """lexV1ContextoEstruturalAntes (V1 runtime only)."""
        if self.kind != 'cf' or not self.text_map or limit == 0:
            return None
        lo, hi, best = 0, len(self.text_map) - 1, None
        while lo <= hi:
            mid = (lo + hi) // 2
            if self.text_map[mid][0] <= limit - 1:
                best, lo = self.text_map[mid], mid + 1
            else:
                hi = mid - 1
        self.st.textmap += 1
        if best is None or checkpoint >= best[0]:
            return None
        ctx = empty_ctx()
        for seg in best[2].split(':')[1:]:
            if seg.startswith('ART.'):
                ctx['artigo'] = seg[4:]
            elif seg == 'PAR.UNICO':
                ctx['paragrafo'] = 'unico'
            elif seg.startswith('PAR.'):
                ctx['paragrafo'] = seg[4:]
            elif seg.startswith('INC.'):
                ctx['inciso'] = seg[4:]
            elif seg.startswith('AL.'):
                ctx['alinea'] = seg[3:]
        return best[0], ctx

    def _is_anchor(self, f, p, limit):
        self.st.anchors_checked += 1
        f.seek(p)
        line = self._readline(f)[:127]                       # lexLinhaEhAncoraArtigo: 128-byte buffers (prefix decides)
        nxt = None
        if self.cf and isolated_marker(line):
            nxt = self._readline(f, limit)[:127]
            if not starts_digit(nxt):
                nxt = None
        t = empty_ctx()
        self.compat(t, line, True, nxt)
        return bool(t['artigo'])

    def _anchor_before(self, f, limit, floor):
        """lexAncoraArtigoAntes (buffer based; a failed validation moves the block, the scan continues below that LF)."""
        cur = limit
        while cur > floor:
            if limit - cur >= C['anchor_max']:
                return -1, None
            if not f.contem(cur - 1) and not f.carregar_ate(cur):
                return -1, None
            base = max(f.base, floor)
            pos = cur
            while pos > base:
                pos -= 1
                if f.byte_em(pos) != 0x0A:
                    continue
                p = pos + 1
                if p >= limit:
                    continue
                j = p
                while f.contem(j) and f.byte_em(j) in (0x20, 0x09, 0xC2, 0xA0):
                    j += 1
                if f.contem(j) and f.byte_em(j) not in (0x41, 0x61):
                    continue
                if self._is_anchor(f, p, limit):
                    return 1, p
                break
            cur = pos if pos > base else base
        if floor == 0 and limit > 0 and self._is_anchor(f, 0, limit):
            return 1, 0
        return 0, None

    def reconstruct(self, limit):
        """reconstruirContextoAntesOffset(limite) -> (ctx, origin, bytes_reread)."""
        start, ctx = self.cp_get(limit)
        used = start is not None
        if not used:
            start, ctx = 0, empty_ctx()
        if self.mode == 'new':
            if used and start >= limit:
                return ctx, 'checkpoint_exato', 0
            f = self.File()
            origin = 'checkpoint' if used else 'janela'
            base = start if used else max(0, limit - C['window'])
            if limit - base > C['seed_min']:
                r, anc = self._anchor_before(f, limit, start if used else 0)
                if r == 1:
                    ctx, start, used, origin = empty_ctx(), anc, True, 'ancora'
                elif r == 0:
                    if not used:
                        start, used, origin = 0, True, 'inicio'
                else:
                    sd = self._seed(limit, base) if limit - base > C['seed_min'] else None
                    if sd:
                        start, ctx = sd
                        used, origin = True, 'text_map'
                    else:
                        ctx, used, origin = empty_ctx(), False, 'janela_failsafe'
                        self.log.append(('CTX_FAILSAFE', limit))
            if not used:
                start = max(0, limit - C['anchor_max'])
        else:
            f = self.File()
            origin = 'checkpoint' if used else 'janela'
            base = start if used else max(0, limit - C['window'])
            if limit - base > C['seed_min']:
                sd = self._seed(limit, base)
                if sd:
                    start, ctx = sd
                    used, origin = True, 'text_map'
            if not used:
                start = max(0, limit - C['window'])
        if start > 0 and not used:
            f.seek(start)
            while f.available() and f.pos < limit and f.read1() != 0x0A:
                pass
            start = f.pos
        else:
            f.seek(start)
        reread_from = start
        while f.available() and f.pos < limit:
            off = f.pos
            line = self._readline(f)
            if self.cf and isolated_marker(line) and f.pos < limit:
                ip = f.pos
                nxt = self._readline(f, limit)
                if starts_digit(nxt):
                    self.compat(ctx, line, True, nxt)
                    P.apply_line(ctx, nxt[:511])
                    self.cp_save(f.pos, ctx)
                    self.st.ctx_lines += 1
                    continue
                f.seek(ip)
            self.compat(ctx, line, True)
            self.cp_save(f.pos, ctx)
            self.st.ctx_lines += 1
        return ctx, origin, limit - reread_from

    def recalc(self):
        cur = dict(self.ctx_before)
        for i in range(self.ROWS):
            if not self.valid[i]:
                self.line_ctx[i] = empty_ctx()
                continue
            self.cp_save(self.line_off[i], cur)
            nxt = self.lines[i + 1] if i + 1 < self.ROWS and self.valid[i + 1] else None
            self.compat(cur, self.lines[i], self.phys[i], nxt)
            self.line_ctx[i] = dict(cur)

    # ---------------- viewport ----------------
    def prepare(self):
        """lexPrepararCacheBidirecional (new only)."""
        if self.top < C['prev_min'] and self.offs[0] > 0:
            self.indexar_antes()
        self.indexar_ate(self.top + self.ROWS + C['next_alvo'])
        i = max(0, self.top - C['prev_alvo'])
        warm = self.offs[i] if i < len(self.offs) else 0
        top = self.offs[self.top] if self.top < len(self.offs) else 0
        if 0 < warm < top:
            self.reconstruct(warm)

    def _fill(self, f, i):
        idx = self.top + i
        if idx < len(self.offs):
            self.lines[i], self.phys[i] = self.read_visual(f, idx)
            self.valid[i], self.line_off[i] = True, self.offs[idx]
        else:
            self.lines[i], self.phys[i], self.valid[i], self.line_off[i] = b'', False, False, 0

    def load_full(self):
        if self.mode == 'new':
            self.prepare()
        self.indexar_ate(self.top + self.ROWS + 1)
        f = self.File()
        for i in range(self.ROWS):
            self._fill(f, i)
        self.cache_top, self.cache_valid = self.top, True
        top = self.offs[self.top] if self.top < len(self.offs) else 0
        self.ctx_before, self.last_origin, self.last_reread = self.reconstruct(top)
        self.recalc()

    def update(self):
        self.last_origin, self.last_reread = '-', 0
        if not self.cache_valid or self.cache_top < 0:
            return self.load_full()
        delta = self.top - self.cache_top
        if delta == 0:
            return
        if abs(delta) >= self.ROWS:
            return self.load_full()
        self.indexar_ate(self.top + self.ROWS + 1)
        if delta > 0:
            before = dict(self.line_ctx[delta - 1])
        else:
            before, self.last_origin, self.last_reread = self.reconstruct(self.offs[self.top])
        f = self.File()
        R = self.ROWS
        if delta > 0:
            keep = R - delta
            for arr in (self.lines, self.phys, self.valid, self.line_off):
                arr[:keep] = arr[delta:]
            rng = range(keep, R)
        else:
            up = -delta
            keep = R - up
            for arr in (self.lines, self.phys, self.valid, self.line_off):
                arr[up:] = arr[:keep]
            rng = range(0, up)
        for i in rng:
            self._fill(f, i)
        self.cache_top = self.top
        self.ctx_before = before
        self.recalc()

    def draw(self):
        self.update()

    def scroll(self, delta):
        """rolarLeitor(delta) -> step record."""
        if delta == 0:
            return None
        s0 = self.st.snap()
        pend = delta
        delta = max(-self.ROWS, min(self.ROWS, delta))
        prev_refill = 0
        if delta < 0:
            floor = C['prev_min'] if self.mode == 'new' else 0
            while self.top + delta < floor and self.offs[0] > 0:
                q = self.indexar_antes()
                prev_refill += q
                if q == 0:
                    break
        old_top = self.top
        n_before = len(self.offs)
        if delta > 0:
            want = self.top + delta
            if self.mode == 'new':
                if not self.end and want + self.ROWS + C['next_min'] >= len(self.offs):
                    self.indexar_ate(want + self.ROWS + C['next_alvo'])
            else:
                self.indexar_ate(want + self.ROWS + 1)
            mx = max(0, len(self.offs) - self.ROWS) if self.end else len(self.offs) - 1
            self.top = max(self.top, min(want, mx))
        else:
            self.top = max(0, self.top + delta)
        moved = self.top - old_top
        if moved == 0:
            return dict(moved=0, pend=pend)
        self.last_origin, self.last_reread = '-', 0
        self.draw()
        d = Stats.diff(s0, self.st.snap())
        return dict(moved=moved, pend=pend, prev_refill=prev_refill, next_refill=max(0, len(self.offs) - n_before - prev_refill),
                    io=Stats.io_bytes(d), seeks=d['blocks'], opens=d['opens'], perbyte=d['perbyte'], ctx_lines=d['ctx_lines'],
                    wrap_lines=d['wrap_lines'], textmap=d['textmap'], origin=self.last_origin, reread=self.last_reread,
                    us=Stats.us(d, self.kind), top=self.offs[self.top])

    # ---------------- landings ----------------
    def open_file(self):
        self.reiniciar(0)
        self.draw()

    def land_top(self, pos):
        """pesquisarArtigo (legacy text): reiniciarIndice(pos), linhaTopo=0, checkpoint seeded at pos (empty ctx; non-CF)."""
        s0 = self.st.snap()
        self.reiniciar(pos)
        ctx = empty_ctx()
        self.cp_save(pos, ctx)
        self.draw()
        d = Stats.diff(s0, self.st.snap())
        return dict(io=Stats.io_bytes(d), us=Stats.us(d, self.kind), origin=self.last_origin, opens=d['opens'])

    def land_centered(self, pos):
        """lexV1PousarBuscaNaLinhaAtiva (V1 runtime): occurrence on the active row (clamp at 0)."""
        s0 = self.st.snap()
        self.reiniciar(pos)
        while self.top < self.ACTIVE and self.offs[0] > 0:
            if self.indexar_antes() == 0:
                break
        self.top = max(0, self.top - self.ACTIVE)
        self.draw()
        d = Stats.diff(s0, self.st.snap())
        return dict(io=Stats.io_bytes(d), us=Stats.us(d, self.kind), origin=self.last_origin, opens=d['opens'])

    # ---------------- views ----------------
    def viewport(self):
        return tuple(self.offs[self.top:self.top + self.ROWS])

    def contexts(self):
        return tuple(ctx_key(c) for c in self.line_ctx)


def article_offset(data, n, start=0):
    """Line-start 'Art. N' header, printed plainly ('Art. 2000') or with the thousands separator ('Art. 2.000')."""
    label = re.escape(f'{n:,}'.replace(',', '.').encode()) + rb'|' + str(n).encode()
    m = re.compile(rb'(?m)^[ \t]*Art\. (?:' + label + rb')(?![0-9]|\.[0-9])').search(data, start)
    return m.start() if m else None


def target_at(smap, off):
    """Floor lookup in a structural map [(offset, tid)] sorted by offset (TEXT_MAP semantics: lexv1TargetAtOffset)."""
    lo, hi, best = 0, len(smap) - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if smap[mid][0] <= off:
            best, lo = smap[mid][1], mid + 1
        else:
            hi = mid - 1
    return best


def ideal_contexts(data, offsets, cf=False):
    """Ground truth: full parse from offset 0 by physical lines (no checkpoints), then the visible rows like recalcularContextosCache."""
    ctx, pos = empty_ctx(), 0
    first = offsets[0] if offsets else 0
    while pos < first:
        e = data.find(b'\n', pos)
        e = len(data) if e < 0 else e
        P.apply_line(ctx, data[pos:e].rstrip(b'\r')[:511])
        pos = e + 1
    return ctx
