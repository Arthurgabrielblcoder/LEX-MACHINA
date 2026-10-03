# -*- coding: utf-8 -*-
"""Host replica of the DEVICE V1 reader viewport (read-only): visual wrap, article search, ACTIVE_TARGET line and layer availability.

Mirrors the firmware (constants are READ from the sketch, never re-typed):
  * visual lines   = avancarUmaLinhaVisual(): UTF-8 decode, Arimo glyph advances (FONTE_ARIMO_A4_GLYPHS), LEITOR_TEXTO_W px,
                     word wrap at the last space, '\\n' ends a line; lines above a point are rebuilt per physical line
                     (indexarAntesDaJanela);
  * article search = pesquisarArtigo(): first LINE-START "Art. N" (CF88_RUNTIME.txt is not "cf.txt");
  * active row     = linhaContextoAtivo(LEITOR_LINHAS_VISIVEIS) (contexto_juridico.h): the row that produces CONTEXTO and
                     ACTIVE_TARGET (escolherContextoPredominante, main rule);
  * ACTIVE_TARGET  = CF88_TEXT_MAP.IDX floor lookup at that row's offset (lexV1SincronizarAlvo);
  * layers         = lexV1QueryKeysForActiveTarget (ART.n -> [ART.n, ART.n:CAPUT]) + CF88_TARGETS.IDX flags; ENTENDA = flag[0] of the
                     ACTIVE_TARGET only.
Landing modes: 'top'   = baseline firmware (reiniciarIndice(pos) + linhaTopo=0, the occurrence is row 0);
               'active'= ARTICLE_SEARCH_TARGET_CENTERING_FIX (lexV1PousarBuscaNaLinhaAtiva: occurrence on the active row, clamp at 0).
"""
import re
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
SKETCH = FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'
CTX_H = FW / 'contexto_juridico.h'
BASE_SD = DI / 'staging_sd_v1/SD/99_LEX_V1'
ARTIDX = DI / 'staging_article_index/SD/99_LEX_V1/10_TARGETS/CF88_ARTICLE_SEARCH.IDX'


def _define(src, name):
    return int(re.search(rf'#define {name} (\d+)', src).group(1))


def firmware_constants(sketch=SKETCH, ctx_h=CTX_H):
    src = Path(sketch).read_text(encoding='utf-8')
    h = Path(ctx_h).read_text(encoding='utf-8')
    rows, width, row_h = _define(src, 'LEITOR_LINHAS_VISIVEIS'), _define(src, 'LEITOR_TEXTO_W'), _define(src, 'LEITOR_LINHA_H')
    y0 = int(re.search(r'const int TEXTO_Y0=(\d+);', src).group(1))
    m = re.search(r'static inline int linhaContextoAtivo\(int total\)\s*\{\s*return total/(\d+);\s*\}', h)
    if m:
        active = rows // int(m.group(1))
    else:                                                   # baseline header: the rule is inline in escolherContextoPredominante
        active = rows // int(re.search(r'int centro=total/(\d+);', h).group(1))
    return dict(rows=rows, width=width, row_h=row_h, y0=y0, active_row=active)


def glyph_advances(sketch=SKETCH):
    src = Path(sketch).read_text(encoding='utf-8')
    body = src[src.index('FONTE_ARIMO_A4_GLYPHS[148] PROGMEM = {'):]
    body = body[:body.index('};')]
    adv = {int(cp, 16): int(a) for a, cp in re.findall(r'\{\s*\d+,\s*\d+,\s*\d+,\s*-?\d+,\s*-?\d+,\s*(\d+)\},\s*//\s*U\+([0-9A-F]{4})', body)}
    if len(adv) != 148:
        raise SystemExit(f'GLYPH_TABLE_PARSE {len(adv)}')
    return adv


class Reader:
    def __init__(self, sd=BASE_SD, sketch=SKETCH, ctx_h=CTX_H, artidx=None):
        """artidx: path of an ARTICLE_SEARCH.IDX. Valid -> INDEXED search (no text scan); invalid -> INDEX_INVALID_FALLBACK_LINEAR;
        None -> FALLBACK_LINEAR (the structural linear search of the previous firmware)."""
        self.sd = Path(sd)
        c = firmware_constants(sketch, ctx_h)
        self.ROWS, self.WIDTH, self.ROW_H, self.Y0, self.ACTIVE = c['rows'], c['width'], c['row_h'], c['y0'], c['active_row']
        self.data = (self.sd / '05_TEXT/CF88_RUNTIME.txt').read_bytes()
        self.adv = glyph_advances(sketch)
        self.map = [(int(r[0]), int(r[1]), r[2]) for r in self._rows('10_TARGETS/CF88_TEXT_MAP.IDX')]
        self.flags = {r[0]: r[3] for r in self._rows('10_TARGETS/CF88_TARGETS.IDX')}
        self.refs = {}
        for r in self._rows('20_REFERENCES/REF_PAYLOAD.IDX'):
            self.refs.setdefault(r[0], []).append(r)
        self.text_scans, self.scanned_bytes, self.index, self.index_state = 0, 0, None, 'ABSENT'
        if artidx is not None:
            import build_article_search_index as AI
            try:
                self.index = AI.ArticleIndex(Path(artidx).read_bytes(), self.data)
                self.index_state = 'OK'
            except AI.IndexError_ as e:
                self.index_state = f'INVALID:{e}'                  # fail closed: no offset of this file is ever used

    def _rows(self, rel):
        return [l.split('|') for l in (self.sd / rel).read_text(encoding='utf-8').splitlines() if l and l[0] != '#']

    def advance(self, cp):
        if cp in (0x09, 0xA0):
            cp = 0x20
        return self.adv.get(cp, self.adv[ord('?')])

    def next_visual_line(self, start):
        """avancarUmaLinhaVisual(): offset of the next visual line."""
        d, n = self.data, len(self.data)
        px, last_space_after, found = 0, start, False
        i = start
        while i < n:
            before = i
            b0 = d[i]
            i += 1
            if b0 == 0x0D:
                continue
            if b0 == 0x0A:
                return i
            cp = b0
            if b0 & 0xE0 == 0xC0:
                cp = ((b0 & 0x1F) << 6) | (d[i] & 0x3F)
                i += 1
            elif b0 & 0xF0 == 0xE0:
                cp = ((b0 & 0x0F) << 12) | ((d[i] & 0x3F) << 6) | (d[i + 1] & 0x3F)
                i += 2
            elif b0 & 0xF8 == 0xF0:
                i += 3
                cp = ord('?')
            if cp in (0x20, 0x09, 0xA0):
                last_space_after, found = i, True
            av = self.advance(cp)
            if px + av > self.WIDTH:
                if found and last_space_after > start:
                    return last_space_after
                return before if before > start else i
            px += av
        return n

    def visual_lines(self, start, count):
        out, p = [], start
        for _ in range(count):
            if p >= len(self.data):
                break
            q = self.next_visual_line(p)
            out.append((p, q))
            p = q
        return out

    def visual_lines_before(self, start, count):
        """indexarAntesDaJanela(): visual lines ending at `start`, rebuilt one physical line at a time (never before offset 0)."""
        out, end = [], start
        while len(out) < count and end > 0:
            ls = self.data.rfind(b'\n', 0, end - 1) + 1
            seg, p = [], ls
            while p < end:
                q = self.next_visual_line(p)
                seg.append((p, min(q, end)))
                p = q
            out = seg + out
            end = ls
        return out[-count:] if count else []

    def text(self, a, b):
        return self.data[a:b].decode('utf-8').rstrip('\n').rstrip()

    def target_at(self, off):
        lo, hi, best = 0, len(self.map) - 1, None
        while lo <= hi:
            m = (lo + hi) // 2
            if self.map[m][0] <= off:
                best, lo = self.map[m], m + 1
            else:
                hi = m - 1
        return best[2] if best else None

    def map_row_at(self, off):
        return next((t for o, _, t in self.map if o == off), None)

    def search_article(self, n, start=0):
        """pesquisarArtigo(n, inicioBusca): first line-start occurrence at or after `start`."""
        rx = re.compile(rb'(?m)^[ \t]*([Aa][Rr][Tt](?:igo)?\.?[ \t]*' + re.escape(str(n).encode()) + rb')(?![0-9]|\.[0-9])')
        m = rx.search(self.data, start)
        self.text_scans += 1
        self.scanned_bytes += (m.start(1) if m else len(self.data)) - start
        return m.start(1) if m else None

    @staticmethod
    def query_keys(tid):
        if tid and tid.startswith('CF88:ART.') and ':' not in tid[len('CF88:ART.'):]:
            return [tid, tid + ':CAPUT']
        return [tid] if tid else []

    def layer_rows(self, tid, tipo):
        seen, out = set(), []
        for k in self.query_keys(tid):
            for r in self.refs.get(k, []):
                if r[1] == tipo and r[2] == 'CURRENT_VISIBLE' and r[5] not in seen:
                    seen.add(r[5])
                    out.append(r)
        return out

    def layer_flag(self, tid, pos):
        return any(len(self.flags.get(k, '')) > pos and self.flags[k][pos] == {1: 'C', 2: 'J', 3: 'W'}[pos] for k in self.query_keys(tid))

    def layer4(self, tid):
        return self.layer_flag(tid, 3), [r[6] for r in self.layer_rows(tid, 'WORK_REFERENCE')]

    def entenda(self, tid):
        return bool(tid) and self.flags.get(tid, '-')[0] in 'EB'

    def context_seed(self, limit):
        """lexV1ContextoEstruturalAntes: TEXT_MAP row valid at limit-1 -> bytes re-read before `limit` (fix) vs. from offset 0 (worst old)."""
        rows = [o for o, _, _ in self.map if o <= limit - 1]
        return (limit - rows[-1]) if rows and limit else 0

    SEED_MIN = 2048                                               # LEXV1_CTX_SEMENTE_MIN

    def context_reread(self, limit, checkpoint=None):
        """reconstruirContextoAntesOffset with the fix: (bytes re-read, TEXT_MAP seed used). checkpoint=None -> no checkpoint (window)."""
        base = checkpoint if checkpoint is not None else max(0, limit - 262144)
        if limit - base > self.SEED_MIN:
            seed = self.context_seed(limit)
            if limit - seed > base:
                return seed, True
        return limit - base, False

    def land_top(self, occurrence, mode='active'):
        """Top offset of the viewport after ARTICLE_SEARCH found `occurrence` ('top' = baseline, 'active' = centering fix)."""
        if mode == 'top':
            return occurrence
        above = self.visual_lines_before(occurrence, self.ACTIVE)
        return above[0][0] if above else occurrence                  # clamp: fewer lines above -> linhaTopo = 0 of the window

    def viewport(self, top):
        lines = self.visual_lines(top, self.ROWS)
        rows = [dict(row=i, y=self.Y0 + i * self.ROW_H, offset=a, end=b, target=self.target_at(a), text=self.text(a, b)) for i, (a, b) in enumerate(lines)]
        act = rows[self.ACTIVE]['target'] if len(rows) > self.ACTIVE else (rows[-1]['target'] if rows else None)
        return rows, act

    def state(self, top):
        rows, act = self.viewport(top)
        w, works = self.layer4(act)
        return dict(top=top, rows=rows, active_target=act, contexto=act, layer4=w, works=works, entenda=self.entenda(act),
                    juris=self.layer_flag(act, 2), correlatas=self.layer_flag(act, 1))

    def scroll(self, top, k):
        """rolarLeitor(k): k visual lines down (k>0) or up (k<0) from `top`."""
        if k >= 0:
            lines = self.visual_lines(top, k + 1)
            return lines[min(k, len(lines) - 1)][0]
        above = self.visual_lines_before(top, -k)
        return above[0][0] if above else top

    def is_structural(self, n, off):
        """lexV1OcorrenciaEstrutural: the TEXT_MAP row starting exactly at `off` is the article NS:ART.n itself."""
        t = self.map_row_at(off)
        return bool(t) and t.count(':') == 1 and t.split(':ART.', 1)[-1] == str(n)

    def search_structural(self, n, start=0):
        """lexV1PesquisarArtigoEstrutural. Index OK: key -> exact offset (lexV1ArtIdxBuscar), never the text. Otherwise:
        pesquisarArtigo from `start`, skipping non-structural (remission) hits."""
        if self.index is not None:
            n = str(n)
            if not n.isdigit() or n[0] == '0' or len(n) > 5 or not 1 <= int(n) <= 0xFFFF:
                return None                                       # lexV1ArtigoChave
            hit = self.index.find(int(n), 0, start)
            return hit[0] if hit else None
        while True:
            occ = self.search_article(n, start)
            if occ is None or self.is_structural(n, occ):
                return occ
            start = occ + 1

    def search(self, n, mode='active', start=0):
        occ = self.search_structural(n, start)
        if occ is None:
            return None
        st = self.state(self.land_top(occ, mode))
        st['occurrence'] = occ
        st['occurrence_row'] = next((r['row'] for r in st['rows'] if r['offset'] == occ), None)
        return st


class ArticleSearchV1:
    """DEVICE V1 ARTICLE_SEARCH state machine (centering + next occurrence + REPEAT_READY).

    Legacy search state (numeroUltimaBusca, offsetUltimaOcorrencia, inicioProximaBusca, temOcorrenciaDaBusca, numeroBuscaEditado) plus
    the repeat anchor of the landing (file, size, top offset).
      NORMAL  ENTER        -> ALWAYS opens ARTICLE_SEARCH: prefilled with the previous query (REPEAT_READY) when the anchor is valid,
                              empty otherwise (cursor dropped).                                             (lexV1EntrarBusca)
              1..4         -> opens that layer for the ACTIVE_TARGET (never edits the query).
              SCROLLk      -> moves the text (invalidates the anchor).
      SEARCH  digit        -> REPEAT_READY: the first digit REPLACES the query (-> NEW_QUERY); then appends.
              BACKSPACE    -> REPEAT_READY: edits (removes the last digit, -> NEW_QUERY); empty buffer: cancel at the origin.
              ENTER        -> REPEAT_READY and untouched -> next structural occurrence; otherwise new query from offset 0.
              scroll       -> ignored (the text does not move during the search).
    """
    NORMAL, SEARCH = 'NORMAL_READING_MODE', 'ARTICLE_SEARCH_MODE'

    def __init__(self, reader, top=0, file='CF88_RUNTIME.txt'):
        self.r, self.top, self.file, self.size = reader, top, file, len(reader.data)
        self.state, self.buffer, self.origin, self.messages, self.log, self.opened = self.NORMAL, '', None, [], [], []
        self.reset_legacy()
        self.repeat, self.repeat_ready = None, False

    def reset_legacy(self):                                   # reiniciarEstadoBusca()
        self.num, self.last, self.next_start, self.has, self.edited = '', 0, 0, False, False

    def can_repeat(self):                                     # lexV1PodeRepetirBusca()
        a = self.repeat
        return bool(a and self.has and not self.edited and self.num and a['file'] == self.file and a['size'] == self.size
                    and a['top'] == self.top)

    def _found(self, occ):
        self.last, self.next_start, self.has = occ, occ + 1, True
        self.top = self.r.land_top(occ)                       # lexV1PousarBuscaNaLinhaAtiva
        self.repeat = dict(file=self.file, size=self.size, top=self.top)
        self.log.append(occ)

    def _close_search(self):
        self.state, self.buffer, self.repeat_ready = self.NORMAL, '', False

    def key(self, k):
        if self.state == self.SEARCH:
            if k.isdigit():
                if self.repeat_ready:                         # first digit replaces the preloaded query
                    self.buffer, self.repeat_ready, self.edited = '', False, True
                if len(self.buffer) < 8:
                    self.buffer += k
            elif k == 'BACKSPACE':
                if self.buffer:
                    if self.repeat_ready:
                        self.repeat_ready, self.edited = False, True
                    self.buffer = self.buffer[:-1]
                else:                                         # lexV1CancelarBusca
                    self.repeat_ready, self.repeat = False, None
                    self.reset_legacy()
                    self.state, self.top = self.NORMAL, self.origin
            elif k == 'ENTER' and self.buffer:                # lexV1ExecutarBuscaArtigo
                repeat = self.repeat_ready and not self.edited and self.buffer == self.num and self.can_repeat()
                self.repeat_ready = False
                if repeat:                                    # lexV1ProximaOcorrenciaArtigo
                    self._close_search()
                    occ = self.r.search_structural(self.num, self.next_start)
                    if occ is None:
                        self.messages.append('SEM OUTRA OCORRENCIA')   # legacy: no wrap, position and cursor kept
                    else:
                        self._found(occ)
                    return self
                n = self.buffer
                self.reset_legacy()
                self.num = n
                occ = self.r.search_structural(n, 0)
                if occ is None:
                    self.messages.append(f'ART. {n} NAO ENCONTRADO')
                else:
                    self._close_search()
                    self._found(occ)
            return self                                       # scroll / other keys: nothing during the search
        if k == 'ENTER':                                      # lexV1EntrarBusca: always opens the search
            self.state, self.origin = self.SEARCH, self.top
            if self.can_repeat():
                self.buffer, self.repeat_ready = self.num, True
            else:
                self.repeat, self.repeat_ready = None, False
                self.buffer, self.edited = '', True
        elif k in ('1', '2', '3', '4'):
            st = self.view()
            avail = {'1': st['correlatas'], '2': st['juris'], '3': st['entenda'], '4': st['layer4']}[k]
            self.opened.append(dict(key=k, target=st['active_target'], available=avail, works=st['works'] if k == '4' else None))
        elif k.startswith('SCROLL'):
            self.top = self.r.scroll(self.top, int(k[6:]))
        elif k == 'OPEN_FILE':                                # abrir/reabrir arquivo: reiniciarEstadoBusca()
            self.reset_legacy()
            self.top = 0
        return self

    def keys(self, *ks):
        for k in ks:
            self.key(k)
        return self

    def view(self):
        return self.r.state(self.top)
