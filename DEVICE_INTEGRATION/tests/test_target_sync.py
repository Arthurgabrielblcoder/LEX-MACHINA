"""TARGET SYNC (uncommitted until the human test): CONTEXTO and layers 1-4 use ONE target (ACTIVE_TARGET).

Physical bug (video): the footer showed CONTEXTO: ART. 5 | INC. XVI and key 4 opened DISPOSITIVO: CF ART. 5, INC. XV (Papers,
Please). Root cause: CONTEXTO came from the CENTER line of the viewport (escolherContextoPredominante), while the V1 layers
resolved the TEXT_MAP at the TOP line (offsetsLinhas[linhaTopo]). Short incisos (XV/XVI) put both on screen at once.

Fix mirrored here: ACTIVE_TARGET = TEXT_MAP(offset of the line that generates CONTEXTO), resolved immediately (no debounce);
CONTEXTO label is built from ACTIVE_TARGET; key press re-resolves ACTIVE_TARGET and rejects an availability cache of another
target; the 250 ms debounce only delays the TARGETS flags I/O.
The viewport model wraps each physical line of CF88_RUNTIME.txt greedily (approximation of the Arimo wrap); the invariant does
not depend on the wrap width, so it is also swept at several widths.
"""
import bisect
import collections
import json
import re
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(DI / 'tests'))
import device_lookup_simulator as S  # noqa: E402
from test_a3b_prep import INO, SD  # noqa: E402

RT = (SD / '05_TEXT/CF88_RUNTIME.txt').read_bytes()
VISIVEIS = 12                                   # LEITOR_LINHAS_VISIVEIS
CENTRO = VISIVEIS // 2                          # escolherContextoPredominante: the center line has priority
DEBOUNCE_MS = 250
EXPORT = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run1'
CANON = ROOT / 'LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json'
QUAR = ROOT / 'LEGAL_TARGET_ID/derived/CF88_QUARANTINE_RESOLUTION.json'


def func(name):
    body = INO[INO.index(name):]
    return body[:body.index('\n}\n')]


def text_map():
    rows = []
    for l in (SD / '10_TARGETS/CF88_TEXT_MAP.IDX').read_text(encoding='utf-8').splitlines():
        if l and l[0] != '#':
            p = l.split('|')
            rows.append((int(p[0]), p[2]))
    return rows


MAP = text_map()
MAP_OFF = [o for o, _ in MAP]


def target_at(off):
    i = bisect.bisect_right(MAP_OFF, off) - 1
    return MAP[i][1] if i >= 0 else None


def visual_lines(width):
    """Byte offsets of every visual line (greedy word wrap of each physical line at `width` characters)."""
    out, pos = [], 0
    for phys in RT.split(b'\n'):
        text = phys.decode('utf-8')
        start = 0
        while True:
            out.append(pos + len(text[:start].encode('utf-8')))
            if len(text) - start <= width:
                break
            cut = text.rfind(' ', start, start + width)
            start = cut + 1 if cut > start else start + width
        pos += len(phys) + 1
    return out


def rotulo_contexto(tid):                        # mirror of lexV1RotuloContexto
    r = ''
    for p in tid.split(':'):
        if p == 'CF88':
            continue
        if p == 'ADCT':
            q = 'ADCT'
        elif p.startswith('ART.'):
            q = 'ART. ' + p[4:]
        elif p == 'PAR.UNICO':
            q = 'PAR. UNICO'
        elif p.startswith('PAR.'):
            q = '§ ' + p[4:] + 'º'
        elif p.startswith('INC.'):
            q = 'INC. ' + p[4:]
        elif p.startswith('AL.'):
            q = 'AL. ' + p[3:] + ')'
        else:
            q = p
        if r:
            r += ' ' if r == 'ADCT' else ' | '
        r += q
    return r


def rotulo_dispositivo(tid):                     # mirror of lexV1Rotulo (header "DISPOSITIVO: ...")
    r = ''
    for p in tid.split(':'):
        if p == 'CF88':
            q = 'CF'
        elif p.startswith('ART.'):
            q = 'ART. ' + p[4:]
        elif p == 'PAR.UNICO':
            q = 'PAR. ÚNICO'
        elif p.startswith('PAR.'):
            q = '§ ' + p[4:] + 'º'
        elif p.startswith('INC.'):
            q = 'INC. ' + p[4:]
        elif p.startswith('AL.'):
            q = 'AL. ' + p[3:] + ')'
        else:
            q = p
        if r:
            r += ' ' if (p.startswith('ART.') or r in ('CF', 'ADCT')) else ', '
        r += q
    return r


def componentes(label):
    """'CONTEXTO: ART. 5 | INC. XVI' and 'DISPOSITIVO: CF ART. 5, INC. XVI' -> ('ART.5', 'INC.XVI')."""
    label = label.split(': ', 1)[1].replace('ÚNICO', 'UNICO')
    toks = [t.replace(' ', '') for t in re.split(r' \| |, ', label)]
    toks = [t[2:] if t.startswith('CF') and t != 'CF' else t for t in toks]
    return tuple(t for t in toks if t not in ('CF',))


class Firmware:
    """Host model of the reader + DEVICE V1 layer state. `fixed=False` reproduces the pre-fix firmware."""

    def __init__(self, dev, lines, flags, fixed=True):
        self.dev, self.lines, self.flags, self.fixed = dev, lines, flags, fixed
        self.now = 0
        self.ultimo_scroll = -10_000
        self.alvo = None                         # ACTIVE_TARGET
        self.disp = None                         # LAYER_AVAILABILITY_CACHE: (tid, entenda, refs)
        self.tid_rodape = None
        self.contexto = None                     # footer text actually drawn
        self.top = 0
        self.log = []

    def center_off(self):
        return self.lines[self.top + CENTRO]

    def top_off(self):
        return self.lines[self.top]

    def flags_of(self, tid):
        f = self.flags.get(tid)
        if not f:
            return (False, False)
        return (f[0] in 'EB', f[1] == 'C' or f[2] == 'J' or f[3] == 'W')

    def draw(self):                              # desenharViewportLeitor -> diagnosticarContextoSeMudou -> desenharBarraBusca
        ctx_tid = target_at(self.center_off())   # the line that generates CONTEXTO (same for the parser before the fix)
        if self.fixed:
            self.alvo = ctx_tid                  # lexV1SincronizarAlvo: immediate
            if self.disp and self.disp[0] != self.alvo:
                self.disp = None                 # availability of another target: invalid at once
            self.tid_rodape = self.alvo
            self.contexto = 'CONTEXTO: ' + rotulo_contexto(self.alvo)
        else:
            self.contexto = 'CONTEXTO: ' + rotulo_contexto(ctx_tid)

    def scroll(self, delta, dt=10):
        self.now += dt
        self.ultimo_scroll = self.now
        self.top += delta
        self.draw()

    def idle(self, ms):                          # loop(): lexV1AtualizarDisponibilidade(false)
        self.now += ms
        self.atualizar(False)

    def atualizar(self, forcar):
        if self.fixed:
            if self.alvo is None:
                self.disp = None
                return
            if self.disp and self.disp[0] == self.alvo:
                return
            if not forcar and self.now - self.ultimo_scroll < DEBOUNCE_MS:
                return
            self.disp = (self.alvo,) + self.flags_of(self.alvo)
        else:                                    # old: cache keyed by the TOP line's TEXT_MAP record
            tid = target_at(self.top_off())
            if self.disp and self.disp[0] == tid:
                return
            if not forcar and self.now - self.ultimo_scroll < DEBOUNCE_MS:
                return
            self.disp = (tid,) + self.flags_of(tid)

    def mask(self):
        m = 0
        if self.disp and (not self.fixed or self.disp[0] == self.alvo):
            m |= 4 if self.disp[1] else 0
            m |= 8 if self.disp[2] else 0
        return m

    def key(self, k, dt=5):
        """Returns (layer, opened_target) or None. 1/2 are per ARTICLE of the target (legacy CF relations)."""
        self.now += dt
        if self.fixed:
            alvo = target_at(self.center_off())  # lexV1ResolverAlvoKeypress: synchronous, from the current viewport
            self.alvo = alvo
            if self.disp and self.disp[0] != alvo:
                self.log.append(f'STALE_CACHE_DETECTED cache={self.disp[0]} active={alvo}')
            if self.tid_rodape != alvo:
                self.log.append('STALE_CONTEXT_DETECTED')
                self.draw()
                return None
            if not alvo:
                return None
            if k in '12':
                art = re.match(r'^(CF88:ART\.[^:]+)', alvo)
                return (k, art.group(1)) if art else None      # ADCT: legacy 1/2 are CF only
            if not self.disp or self.disp[0] != alvo:
                self.atualizar(True)
            if not self.disp or self.disp[0] != alvo:
                return None
            ok = self.disp[1] if k == '3' else self.disp[2]
            return (k, alvo) if ok else None
        # pre-fix firmware: forced recompute at the TOP line, opens with lexV1Disp.tid
        if k in '12':
            art = re.match(r'^(CF88:ART\.[^:]+)', target_at(self.center_off()) or '')
            return (k, art.group(1)) if art else None
        self.atualizar(True)
        ok = self.disp[1] if k == '3' else self.disp[2]
        return (k, self.disp[0]) if ok and self.disp[0] else None


def first_line_of(lines, tid, after=0):
    for i in range(after, len(lines)):
        if target_at(lines[i]) == tid:
            return i
    raise AssertionError(tid)


def transition_pairs():
    """Consecutive TEXT_MAP records by transition type (first match of each)."""
    kinds = collections.OrderedDict()
    for (_, a), (_, b) in zip(MAP, MAP[1:]):
        pa, pb = a.split(':'), b.split(':')
        if a == 'CF88:ART.5:INC.XV' and b == 'CF88:ART.5:INC.XVI':
            kinds.setdefault('XV->XVI', (a, b))
        elif a == 'CF88:ART.5:INC.XVI' and b == 'CF88:ART.5:INC.XVII':
            kinds.setdefault('XVI->XVII', (a, b))
        elif len(pa) == 3 and pa[2].startswith('PAR.') and len(pb) == 4 and pb[3].startswith('INC.'):
            kinds.setdefault('paragrafo->inciso', (a, b))
        elif len(pa) == 3 and pa[2].startswith('INC.') and len(pb) == 3 and pb[2].startswith('PAR.') and pa[1] == pb[1]:
            kinds.setdefault('inciso->paragrafo', (a, b))
        elif len(pa) == 2 and pa[0] == 'CF88' and b == a + ':PAR.1':
            kinds.setdefault('caput->par1', (a, b))
        elif a.endswith(':PAR.1') and b == a[:-1] + '2':
            kinds.setdefault('par1->par2', (a, b))
        elif pa[0] == pb[0] == 'CF88' and len(pb) == 2 and pa[1] != pb[1]:
            kinds.setdefault('artigo->artigo', (a, b))
        elif pa[0] == 'CF88' and pb[0] == 'ADCT':
            kinds.setdefault('CF->ADCT', (a, b))
    return kinds


class TargetSyncModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = S.Device(SD)
        cls.flags = {}
        for l in (SD / '10_TARGETS/CF88_TARGETS.IDX').read_text(encoding='utf-8').splitlines():
            if l and l[0] != '#':
                p = l.split('|')
                cls.flags[p[0]] = p[3]
        cls.lines = visual_lines(52)

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def fw(self, fixed=True, lines=None):
        return Firmware(self.dev, lines or self.lines, self.flags, fixed)

    def at_center(self, fw, line_index):
        fw.top = line_index - CENTRO
        fw.draw()

    def scenario(self, src, dst, key, fixed=True, lines=None):
        """Settle on `src` (cache computed), scroll ONE line so the CONTEXTO line enters `dst`, press `key` at once."""
        lines = lines or self.lines
        fw = self.fw(fixed, lines)
        i_dst = first_line_of(lines, dst)
        down = target_at(lines[i_dst - 1]) == src                       # src right before dst -> scroll down
        if down:
            self.at_center(fw, i_dst - 1)
        else:
            i_src = first_line_of(lines, src)
            self.assertEqual(target_at(lines[i_src - 1]), dst)
            self.at_center(fw, i_src)                                  # first line of src; line above is dst
        fw.idle(DEBOUNCE_MS + 50)
        fw.scroll(+1 if down else -1)
        return fw, fw.key(key)

    def test_simulator_and_map_agree(self):
        size, sha = self.dev.verify_runtime_file()
        for off in self.lines[::997]:
            self.assertEqual(self.dev.resolve_text_position(off, size, sha)['target_id'], target_at(off))

    def test_prefix_bug_reproduced_by_old_model(self):
        # XV -> XVI, 4 pressed right after CONTEXTO changes: the old firmware opened the TOP line's target, not CONTEXTO's
        fw, opened = self.scenario('CF88:ART.5:INC.XV', 'CF88:ART.5:INC.XVI', '4', fixed=False)
        self.assertEqual(fw.contexto, 'CONTEXTO: ART. 5 | INC. XVI')
        self.assertEqual(opened, ('4', target_at(fw.top_off())))
        self.assertNotEqual(opened[1], 'CF88:ART.5:INC.XVI')           # CONTEXTO X, DISPOSITIVO Y
        # the exact video (top line in XV, CONTEXTO line in XVI, key 4 -> XV / Papers, Please) at some wrap widths,
        # even with the wheel stopped for 1 s: speed is not required, the two lines disagree
        video = []
        for width in range(36, 72):
            lines = visual_lines(width)
            old = self.fw(False, lines)
            self.at_center(old, first_line_of(lines, 'CF88:ART.5:INC.XVI'))
            old.idle(1000)
            if target_at(old.top_off()) == 'CF88:ART.5:INC.XV':
                self.assertEqual(old.key('4'), ('4', 'CF88:ART.5:INC.XV'))
                new = self.fw(True, lines)
                self.at_center(new, first_line_of(lines, 'CF88:ART.5:INC.XVI'))
                new.idle(1000)
                self.assertEqual(new.key('4'), None if not self.flags_ref('CF88:ART.5:INC.XVI') else ('4', 'CF88:ART.5:INC.XVI'))
                video.append(width)
        self.assertTrue(video)

    def flags_ref(self, tid):
        f = self.flags.get(tid, '----')
        return f[1] == 'C' or f[2] == 'J' or f[3] == 'W'

    def test_xv_to_xvi_immediate(self):
        for k in '1234':
            fw, opened = self.scenario('CF88:ART.5:INC.XV', 'CF88:ART.5:INC.XVI', k)
            self.assertEqual(fw.contexto, 'CONTEXTO: ART. 5 | INC. XVI')
            self.assertNotEqual(opened and opened[1], 'CF88:ART.5:INC.XV', k)
            if k == '4':
                vis = [r for r in self.dev.references('CF88:ART.5:INC.XVI') if r[2] == 'CURRENT_VISIBLE']
                self.assertEqual(opened, ('4', 'CF88:ART.5:INC.XVI') if vis else None)
            if k in '12':
                self.assertEqual(opened, (k, 'CF88:ART.5'))

    def test_xvi_to_xv_immediate(self):
        fw, opened = self.scenario('CF88:ART.5:INC.XVI', 'CF88:ART.5:INC.XV', '4')
        self.assertEqual(fw.contexto, 'CONTEXTO: ART. 5 | INC. XV')
        self.assertEqual(opened, ('4', 'CF88:ART.5:INC.XV'))           # Papers, Please is here
        self.assertEqual(fw.disp[0], 'CF88:ART.5:INC.XV')

    def test_stale_cache_rejected(self):
        fw2 = self.fw()
        self.at_center(fw2, first_line_of(self.lines, 'CF88:ART.5:INC.XV'))
        fw2.idle(DEBOUNCE_MS + 1)
        self.assertEqual(fw2.disp[0], 'CF88:ART.5:INC.XV')
        fw2.scroll(+(first_line_of(self.lines, 'CF88:ART.5:INC.XVI') - first_line_of(self.lines, 'CF88:ART.5:INC.XV')))
        self.assertIsNone(fw2.disp)                                     # invalidated at once, not after 250 ms
        self.assertEqual(fw2.mask() & 12, 0)                            # 3/4 hidden until the new mask is ready
        fw2.idle(DEBOUNCE_MS + 1)
        self.assertEqual(fw2.disp[0], 'CF88:ART.5:INC.XVI')

    def test_every_transition_kind_every_key(self):
        kinds = transition_pairs()
        self.assertEqual(set(kinds), {'XV->XVI', 'XVI->XVII', 'paragrafo->inciso', 'inciso->paragrafo', 'caput->par1',
                                      'par1->par2', 'artigo->artigo', 'CF->ADCT'})
        for name, (a, b) in kinds.items():
            for src, dst in ((a, b), (b, a)):
                for k in '1234':
                    fw, opened = self.scenario(src, dst, k)
                    self.assertEqual(fw.alvo, dst, (name, src, dst))
                    self.assertEqual(componentes(fw.contexto), componentes('X: ' + rotulo_contexto(dst)))
                    if opened is None:
                        continue
                    if k in '34':
                        self.assertEqual(opened[1], dst, (name, k))
                        # CONTEXTO: X  =>  DISPOSITIVO: X
                        self.assertEqual(componentes(fw.contexto),
                                         componentes('DISPOSITIVO: ' + rotulo_dispositivo(opened[1])), (name, k))
                    else:
                        self.assertTrue(dst.startswith(opened[1] + ':') or dst == opened[1], (name, k, opened))

    def test_sweep_all_transitions_all_widths(self):
        """Every consecutive TEXT_MAP pair, both directions, keys 3/4, three wrap widths: never the previous target."""
        checked = 0
        for width in (40, 52, 64):
            lines = visual_lines(width)
            tids = [target_at(o) for o in lines]
            fw = self.fw(True, lines)
            for i in range(CENTRO + 1, len(lines) - VISIVEIS):
                if tids[i] == tids[i - 1] or tids[i] is None or tids[i - 1] is None:
                    continue
                for down, (before, after) in ((True, (i - 1, i)), (False, (i, i - 1))):
                    fw.top = before - CENTRO
                    fw.draw()
                    fw.idle(DEBOUNCE_MS + 1)
                    fw.scroll(after - before)
                    for k in '34':
                        opened = fw.key(k)
                        if opened:
                            self.assertEqual(opened[1], tids[after])
                            self.assertEqual(componentes(fw.contexto), componentes('D: ' + rotulo_dispositivo(opened[1])))
                        checked += 1
                    self.assertEqual(fw.tid_rodape, tids[after])
        self.assertGreater(checked, 20000)

    def test_labels_agree(self):
        for tid in ('CF88:ART.5:INC.XVI', 'CF88:ART.1:PAR.UNICO', 'CF88:ART.60:PAR.4:INC.IV', 'CF88:ART.37:PAR.6',
                    'ADCT:ART.10:INC.II', 'CF88:ART.103-A', 'CF88:ART.5'):
            self.assertEqual(componentes('C: ' + rotulo_contexto(tid)), componentes('D: ' + rotulo_dispositivo(tid)), tid)
        self.assertEqual(rotulo_contexto('CF88:ART.5:INC.XVI'), 'ART. 5 | INC. XVI')
        self.assertEqual(rotulo_dispositivo('CF88:ART.5:INC.XV'), 'CF ART. 5, INC. XV')


class TargetSyncFirmwareSourceTest(unittest.TestCase):
    def test_active_target_from_context_line(self):
        diag = func('void diagnosticarContextoSeMudou()\n{')
        self.assertIn('lexV1SincronizarAlvo(indice);', diag)
        self.assertLess(diag.index('lexV1SincronizarAlvo(indice);'), diag.index('if(indice<0) return;'))
        self.assertIn('if(!visualizandoReferencia && novo.artigo[0] && !v1){', diag)   # 1/2 follow ACTIVE_TARGET in V1
        sync = func('void lexV1SincronizarAlvo(int indiceContexto)\n{')
        self.assertIn('lexV1OffsetContexto=lexV1OffsetContextoOk?offsetLinhaCache[i]:0;', sync)
        self.assertIn('lexv1TargetAtOffset(lexV1MapIdx,lexV1RuntimeBytes,lexV1RuntimeSha,off,tid,sizeof(tid),&ini,&fim)', sync)
        self.assertIn('if(strcmp(lexV1Disp.tid,lexV1Alvo.tid)!=0) lexV1Disp.valido=false;', sync)
        for banned in ('linhaTopo', 'millis()', '250'):
            self.assertNotIn(banned, sync, banned)                     # immediate, never the top line
        ctx = func('String rotuloContextoFixoRodape()\n{')
        self.assertIn('if(lexV1CamadaV1Aplicavel()) return lexV1RotuloContexto(lexV1Alvo.valido?lexV1Alvo.tid:"");', ctx)
        self.assertIn('return ativo<lexV1AdctStart;', func('bool arquivoAtualPertenceACF()\n{'))

    def test_debounce_only_for_availability_io(self):
        disp = func('bool lexV1AtualizarDisponibilidade(bool forcar)\n{')
        self.assertIn('if(lexV1Disp.valido && !strcmp(lexV1Disp.tid,lexV1Alvo.tid)) return false;', disp)
        self.assertIn('if(!forcar && (uint32_t)(millis()-lexV1UltimoScrollMs)<250) return false;', disp)
        self.assertIn('strncpy(lexV1Disp.tid,lexV1Alvo.tid,sizeof(lexV1Disp.tid)-1);', disp)
        self.assertNotIn('linhaTopo', disp)
        self.assertNotIn('lexv1TargetAtOffset', disp)
        self.assertIn('lexV1Disp.valido && lexV1Alvo.valido && !strcmp(lexV1Disp.tid,lexV1Alvo.tid)',
                      func('uint8_t lexV1MascaraCamadas()\n{'))

    def test_keypress_uses_resolved_target(self):
        num = func('void lexV1AbrirCamadaNumero(char tecla)\n{')
        self.assertIn('if(v1cf && !lexV1ResolverAlvoKeypress(tecla,alvo,sizeof(alvo))) return;', num)
        self.assertLess(num.index('lexV1ResolverAlvoKeypress'), num.index("case '1':"))  # before ANY layer (1-4)
        self.assertIn("if(v1cf) lexV1AbrirCamada('E',alvo);", num)
        self.assertIn("if(v1cf) lexV1AbrirCamada('R',alvo);", num)
        res = func('static bool lexV1ResolverAlvoKeypress(char tecla, char *alvo, size_t cap)\n{')
        for s in ('lexV1SincronizarAlvo(indice);', 'lexV1SincronizarRelacoes();', 'STALE_CACHE_DETECTED',
                  'ACTIVE_TARGET=%s CACHE_TARGET=%s CONTEXTO_TARGET=%s KEY=%c', 'if(strcmp(lexV1TidRodape,alvo)!=0){'):
            self.assertIn(s, res, s)
        ab = func('void lexV1AbrirCamada(char tipo, const char *tid)\n{')
        self.assertNotIn('strncpy(tid,lexV1Disp.tid', ab)             # never opens with the cache's target
        self.assertIn('if(!lexV1Disp.valido || strcmp(lexV1Disp.tid,tid)!=0) lexV1AtualizarDisponibilidade(true);', ab)
        self.assertIn('if(!lexV1Disp.valido || strcmp(lexV1Disp.tid,tid)!=0) return;', ab)
        self.assertIn('strncpy(lexV1RefTid,tid,sizeof(lexV1RefTid)-1);', ab)   # LAYER_TARGET for list and detail
        self.assertIn('OPEN_LAYER_TARGET=%s', ab)
        self.assertIn('lexV1MontarEntenda(tid);', ab)

    def test_layer_target_is_frozen_and_detail_keyed_by_target(self):
        self.assertIn('snprintf(chave,sizeof(chave),"%s|%s",tid,fonte);', func('static const LexV1RefDetalhe *lexV1BuscarDetalhe('))
        for f in ('static void lexV1MontarListaRef()', 'static void lexV1MontarDetalheRef('):
            if f in INO:
                body = func(f)
                self.assertNotIn('lexV1Disp', body)
                self.assertNotIn('lexV1Alvo', body)
        self.assertEqual(INO.count('strncpy(lexV1RefTid,'), 1)                   # LAYER_TARGET set only on open


class PapersPleaseAndExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canon = json.loads(CANON.read_text(encoding='utf-8'))['records']
        cls.export = json.loads((EXPORT / 'CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))
        cls.payload = [l.rstrip('\n').split('|') for l in (EXPORT / 'REF_PAYLOAD.IDX').read_text(encoding='utf-8').splitlines()
                       if l and l[0] != '#']

    def test_papers_please_approved_only_at_xv(self):
        rc2 = [r for r in self.canon if r['subject_id'] == 'REF-JOG-0001' and r['catalog_role'] == 'PRODUCT_REFERENCE_RC2']
        self.assertEqual([r['target_id'] for r in rc2], ['CF88:ART.5:INC.XV'])
        self.assertEqual(rc2[0]['provenance']['decisao_humana'], 'APROVAR')
        rows = [r for r in self.payload if r[5] == 'REF-JOG-0001']
        self.assertEqual([(r[0], r[2]) for r in rows], [('CF88:ART.5:INC.XV', 'CURRENT_VISIBLE')])
        self.assertFalse([r for r in self.payload if r[0] == 'CF88:ART.5:INC.XVI' and r[5] == 'REF-JOG-0001'])
        sd = (SD / '20_REFERENCES/REF_PAYLOAD.IDX').read_bytes()
        self.assertEqual(sd, (EXPORT / 'REF_PAYLOAD.IDX').read_bytes())
        hdr = (ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h').read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'"([^"|]+)\|REF-JOG-0001"', hdr), ['CF88:ART.5:INC.XV'])

    def test_export_did_not_shift_targets(self):
        idx = collections.defaultdict(set)
        for r in self.canon:
            idx[(r['reference_type'], r['source_record_id'])].add(r['target_id'])
        for r in json.loads(QUAR.read_text(encoding='utf-8'))['records']:
            if r.get('klass') == 'MIXED_RESOLVED_BY_SPLIT':
                idx[('JURISPRUDENCE_LINK', r['original_record_id'])] |= set(r['targets'])
        checked, mism = 0, []
        for grp, links in self.export['references'].items():
            for r in links:
                checked += 1
                t = r['reference_type']
                if t == 'WORK_REFERENCE':
                    keys = [('WORK_REFERENCE', x['reference_id']) for x in r['routes']]
                elif t == 'JURISPRUDENCE':
                    keys = [('JURISPRUDENCE_LINK', r['source_reference_id'])]
                else:
                    keys = [('CORRELATA_INDEX_ENTRY', r['provenance']['index_row'])]
                src = set().union(*(idx.get(k, set()) for k in keys))
                ok = grp == r['target_id'] and r['reference_id'].endswith('@' + r['target_id']) and r['target_id'] in src
                if t == 'WORK_REFERENCE':
                    ok = ok and src == {r['target_id']}
                if not ok:
                    mism.append((r['reference_id'], sorted(src)))
        self.assertEqual(checked, 432)
        self.assertEqual(mism, [])
        ej = {r['reference_id']: r['target_id'] for links in self.export['references'].values() for r in links}
        self.assertEqual(len(self.payload), 432)
        self.assertEqual([p for p in self.payload if ej.get(p[4]) != p[0] or not p[4].endswith('@' + p[0])], [])


if __name__ == '__main__':
    unittest.main()
