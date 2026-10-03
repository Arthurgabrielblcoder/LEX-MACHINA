"""BIDIRECTIONAL_SCROLL_PERFORMANCE_FIX: bounded SCROLL_UP/DOWN after a random landing (ARTICLE_SEARCH / next occurrence / jumps).

Cause (measured on the device, backups/indexed_bench/bench_serial.bin): after ARTICLE_SEARCH art. 2000 on a large legacy norm, the
first SCROLL_UP above the landing ran reconstruirContextoAntesOffset from the checkpoint left near offset 0 when the file was opened:
"PERF CONTEXTO_UP: 11293148 us (checkpoint=sim, bytes=647150)" -> 11,3 s frozen, then one clamped jump (wheel backlog).
Fix (LEX_DEVICE_V1_ENABLED only): buffered reads, block refill of the visual-line cache (offsetsLinhas) before AND after the
viewport, context rebuilt from the nearest "Art." anchor validated by the parser (bounded), bidirectional cache prepared at landing.
`scroll_model.Reader` replays both firmware paths (old/new) with exact byte accounting; old == new is checked for every visible row.
"""
import re
import subprocess
import sys
import unittest
from functools import lru_cache
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
import reader_viewport as V  # noqa: E402
import scroll_model as M  # noqa: E402
import scroll_performance_benchmark as B  # noqa: E402

FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
INO = (FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
HDR = (FW / 'lex_leitor_scroll.h').read_text(encoding='utf-8')
KIB = 1024
PROC_HIT_MS, COLD_MS, HARD_MS = 20.0, 80.0, 250.0           # mission targets (processing before render) / hard failure


def head(path):
    return subprocess.run(['git', 'show', f'lex-device-v1-physical-approved-2026-10-01:{path}'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8').stdout


def func(src, name):
    body = src[src.index(name):]
    return body[:body.index('\n}\n')]


def strip_v1(src):
    out, stack = [], []
    for line in src.replace('\r\n', '\n').split('\n'):
        s = line.strip()
        if s.startswith('#if'):
            stack.append('v1' if s == '#if LEX_DEVICE_V1_ENABLED' else 'other')
            if stack[-1] == 'other' and all(x != 'v1' for x in stack[:-1]):
                out.append(line)
            continue
        if s.startswith('#else') and stack and stack[-1] in ('v1', 'v1else'):
            stack[-1] = 'v1else'
            continue
        if s.startswith('#endif') and stack:
            k = stack.pop()
            if k == 'other' and all(x != 'v1' for x in stack):
                out.append(line)
            continue
        if all(x != 'v1' for x in stack):
            out.append(line)
    return '\n'.join(out)


@lru_cache(maxsize=None)
def fixture():
    return B.civil_like_norm(2500)


@lru_cache(maxsize=None)
def landed(art, mode):
    """Arthur's sequence up to (and including) the first UP; returns (reader, result). Cached: callers must not mutate it."""
    return B.landing_case(fixture(), art, mode)


def fresh_pair(art, landing='top', data=None, **kw):
    data = data or fixture()
    pair = []
    for mode in ('old', 'new'):
        r = M.Reader(data, mode, **kw)
        r.open_file()
        pos = M.article_offset(data, art)
        (r.land_top if landing == 'top' else r.land_centered)(pos)
        pair.append(r)
    return pair


def ms(rec):
    return rec['us'] / 1000.0


class FixtureTest(unittest.TestCase):
    def test_codigo_civil_like_fixture(self):
        d = fixture()
        self.assertGreaterEqual(len(d), 3 * 1024 * KIB)                         # several MB
        for k in (10, 500, 1000, 2000, 2400, 2500):
            self.assertIsNotNone(M.article_offset(d, k), k)
        self.assertGreater(max(len(x) for x in d.split(b'\n')), 3 * KIB)       # long paragraphs (one physical line)
        self.assertGreater(M.article_offset(d, 2000), 2 * 1024 * KIB)


class ColdFirstUpTest(unittest.TestCase):
    def test_01_art2000_landing_then_first_up(self):
        _, old = landed(2000, 'old')
        r, new = landed(2000, 'new')
        o, n = old['first_up'], new['first_up']
        self.assertGreater(o['io'], 500 * KIB)                                  # the stall is reproduced: hundreds of KB, byte by byte
        self.assertGreater(ms(o), 5000)
        self.assertEqual(n['moved'], -1)                                       # exactly one line, immediately
        self.assertLess(n['io'], 16 * KIB)
        self.assertLess(ms(n), COLD_MS)
        ro, _ = landed(2000, 'old')
        self.assertEqual(r.viewport(), ro.viewport())
        self.assertEqual(r.contexts(), ro.contexts())

    def test_02_first_up_has_no_global_scan(self):
        for art in (10, 500, 1000, 2000, 2400):
            _, res = landed(art, 'new')
            f = res['first_up']
            self.assertEqual(f['perbyte'], 0, art)                              # no File::read() byte by byte any more
            self.assertNotIn(f['origin'], ('janela', 'janela_failsafe'), art)    # never the 256 KiB / blind window
            self.assertLessEqual(f['reread'], M.C['anchor_max'], art)
            self.assertLess(f['io'], 16 * KIB, art)
            self.assertLessEqual(f['opens'], 3, art)

    def test_03_first_up_bytes_do_not_grow_with_offset(self):
        io = {a: landed(a, 'new')[1]['first_up']['io'] for a in (10, 500, 1000, 2000, 2400)}
        self.assertLess(max(io.values()), 4 * min(io.values()) + 4 * KIB, io)
        self.assertLess(io[2000], 3 * io[10] + 4 * KIB, io)                    # art. 2000 ~ art. 10 (local window only)
        old10, old2000 = landed(10, 'old')[1]['first_up']['io'], landed(2000, 'old')[1]['first_up']['io']
        self.assertGreater(old2000, 50 * old10)                                # before: O(file offset)


class SequenceTest(unittest.TestCase):
    def _lockstep(self, pattern, art=2000, landing='top', data=None, **kw):
        old, new = fresh_pair(art, landing, data, **kw)
        recs = []
        for d in pattern:
            ro, rn = old.scroll(d), new.scroll(d)
            self.assertEqual(old.viewport(), new.viewport())
            self.assertEqual(old.contexts(), new.contexts())
            if rn and rn.get('moved'):
                self.assertEqual(ro['moved'], rn['moved'])
                recs.append(rn)
        return old, new, recs

    def _limits(self, recs):
        for x in recs:
            limit = COLD_MS if (x['prev_refill'] or x['next_refill'] or x['origin'] == 'ancora') else PROC_HIT_MS
            self.assertLess(ms(x), limit, x)
            self.assertLess(ms(x), HARD_MS)

    def test_04_ten_up(self):
        _, _, recs = self._lockstep([-1] * 10)
        self.assertEqual(len(recs), 10)
        self._limits(recs)
        self.assertLess(ms(recs[-1]), PROC_HIT_MS)                              # warm UP

    def test_05_ten_down(self):
        _, _, recs = self._lockstep([1] * 10)
        self.assertEqual(len(recs), 10)
        self._limits(recs)
        self.assertTrue(all(x['origin'] == '-' for x in recs))                  # DOWN never rebuilds the context

    def test_06_alternating(self):
        _, _, recs = self._lockstep([-1, 1] * 10)
        self.assertEqual(len(recs), 20)
        self._limits(recs)

    def test_07_previous_cache_refill(self):
        old, new, recs = self._lockstep([-1] * 150)
        refills = [x for x in recs if x['prev_refill']]
        self.assertGreaterEqual(len(refills), 2)
        for x in refills:
            self.assertLessEqual(x['prev_refill'], M.C['prev_alvo'])
            self.assertLess(x['io'], 32 * KIB)
            self.assertLess(ms(x), COLD_MS)
        self.assertGreaterEqual(new.top, M.C['prev_min'] - 1)                  # always >= ~one screen of known lines above
        self._limits(recs)

    def test_08_next_cache_refill(self):
        old, new, recs = self._lockstep([1] * 150)
        refills = [x for x in recs if x['next_refill']]
        self.assertGreaterEqual(len(refills), 2)
        self.assertLess(len(refills), 150 // 10)                                # by block, not one open per line
        for x in refills:
            self.assertGreaterEqual(x['next_refill'], M.C['next_alvo'] - M.C['next_min'] - 2)
        self._limits(recs)

    def test_09_target_transition(self):
        old, new = fresh_pair(2000)
        seq_o, seq_n = [], []
        for _ in range(150):
            old.scroll(-1)
            new.scroll(-1)
            seq_o.append(old.contexts()[old.ACTIVE][0])
            seq_n.append(new.contexts()[new.ACTIVE][0])
        self.assertEqual(seq_o, seq_n)
        changes = [b for a, b in zip(seq_n, seq_n[1:]) if a != b]
        self.assertGreaterEqual(len(changes), 3, changes)                      # crossed several articles going up
        self.assertIn('1999', seq_n)

    def test_10_context_transition(self):
        old, new = fresh_pair(1000)
        seen = set()
        for d in [-1] * 80 + [1] * 80:
            old.scroll(d)
            new.scroll(d)
            self.assertEqual(old.contexts(), new.contexts())
            a = new.contexts()[new.ACTIVE]
            seen.add(('par' if a[1] else '') + ('inc' if a[2] else '') + ('al' if a[3] else ''))
        self.assertTrue({'par', 'inc'} <= seen or {'par'} <= seen, seen)

    @unittest.skipUnless((V.BASE_SD / '05_TEXT/CF88_RUNTIME.txt').is_file(), 'staging SD not built')
    def test_11_layer_footer_transition_cf_runtime(self):
        cf = V.Reader(V.BASE_SD)
        for art in (193, 5):
            old, new = fresh_pair(art, 'centered', cf.data, kind='cf', text_map=cf.map, cf_compat=True)
            for d in [-1] * 40 + [1] * 40 + [-6] * 4:
                ro, rn = old.scroll(d), new.scroll(d)
                self.assertEqual(old.viewport(), new.viewport())
                self.assertEqual(old.contexts(), new.contexts())
                off = new.offs[new.top + new.ACTIVE]
                tid = cf.target_at(off)                                           # ACTIVE_TARGET of the active row (TEXT_MAP)
                self.assertEqual(tid, cf.target_at(old.offs[old.top + old.ACTIVE]))
                self.assertEqual([cf.layer_flag(tid, p) for p in (1, 2, 3)] + [cf.entenda(tid)],   # footer 1-4 availability
                                 [cf.layer_flag(cf.target_at(old.offs[old.top + old.ACTIVE]), p) for p in (1, 2, 3)] +
                                 [cf.entenda(cf.target_at(old.offs[old.top + old.ACTIVE]))])
                if rn and rn.get('moved'):
                    self.assertEqual(rn['textmap'], 0)                             # no TEXT_MAP seed per UP step any more
                    self.assertLess(ms(rn), COLD_MS)

    def test_12_rapid_event_backlog(self):
        data = fixture()

        def backlog(mode, direction, events=20, gap_ms=40.0):
            r = M.Reader(data, mode)
            r.open_file()
            r.land_top(M.article_offset(data, 2000))
            t, pend, i, maxpend, lost, worst, moved = 0.0, 0, 0, 0, 0, 0.0, 0
            arr = [k * gap_ms for k in range(events)]
            while i < len(arr) or pend:
                while i < len(arr) and arr[i] <= t:
                    pend, i = pend + 1, i + 1
                if not pend:
                    t = arr[i]
                    continue
                maxpend, lost = max(maxpend, pend), lost + max(0, pend - 12)
                rec = r.scroll(direction * pend)
                pend = 0
                step = ms(rec) + M.RATES['render_ms'] if rec and rec.get('moved') else 1.0
                worst, moved, t = max(worst, step), moved + abs(rec['moved'] if rec else 0), t + step
            return maxpend, lost, worst, moved

        mp, lost, worst, moved = backlog('old', -1)
        self.assertGreater(lost, 0)                                            # before: freeze -> backlog -> one clamped jump
        self.assertGreater(worst, 5000)
        for d in (-1, 1):
            mp, lost, worst, moved = backlog('new', d)
            self.assertLessEqual(mp, 3)
            self.assertEqual(lost, 0)
            self.assertEqual(moved, 20)                                        # navigation precision preserved
            self.assertLess(worst, HARD_MS)


class EdgeTest(unittest.TestCase):
    def test_no_article_in_32k_is_bounded(self):
        filler = ('Texto preambular sem dispositivo algum, apenas considerandos e notas extensas. ' * 12 + '\n') * 160
        data = ('Art. 1. Primeiro.\n' + filler + 'Art. 2. Segundo artigo.\n' + filler + 'Art. 3. Terceiro.\n').encode('utf-8')
        old, new = fresh_pair(3, data=data)
        for _ in range(30):
            rn = new.scroll(-1)
            old.scroll(-1)
            if rn and rn.get('moved'):
                self.assertLess(rn['io'], 2 * M.C['anchor_max'] + 16 * KIB)
                self.assertLess(ms(rn), HARD_MS)
        self.assertEqual(old.viewport(), new.viewport())

    def test_giant_paragraph_refill_failsafe(self):
        data = ('Art. 1. Inicio.\n' + 'palavra ' * 40000 + '\nArt. 2. Fim.\n').encode('utf-8')   # one 320 KB physical line
        r = M.Reader(data, 'new')
        r.open_file()
        r.land_top(M.article_offset(data, 2))
        for _ in range(20):
            rec = r.scroll(-1)
            self.assertLess(rec['io'], 4 * M.C['par_max'])
            self.assertLess(ms(rec), 4 * HARD_MS)                               # pathological; never O(file)
        self.assertIn('REFILL_FAILSAFE', [x[0] for x in r.log])

    def test_file_start_without_article_is_exact(self):
        pre = ''.join(f'Considerando {i} da exposição de motivos, sem artigo.\n' for i in range(120))
        data = (pre + 'Art. 1. Primeiro.\n§ 1º Parágrafo.\nArt. 2. Segundo.\n').encode('utf-8')
        old, new = fresh_pair(2, data=data)
        for d in [-1] * 40 + [1] * 10:
            old.scroll(d)
            new.scroll(d)
            self.assertEqual(old.contexts(), new.contexts())
            self.assertEqual(old.viewport(), new.viewport())

    def test_cf_isolated_article_marker_anchor(self):
        body = ''.join(f'Art.\n{k}. Texto do artigo {k} com redação longa o bastante para quebrar em várias linhas visuais da tela.\n'
                       f'I - inciso do artigo {k};\nII - outro inciso;\nParágrafo único. Fecho do artigo {k}.\n' for k in range(1, 400))
        data = body.encode('utf-8')
        pos = data.index(b'Art.\n300. ')
        pair = []
        for mode in ('old', 'new'):
            r = M.Reader(data, mode, cf_compat=True)
            r.open_file()
            r.land_top(pos)
            pair.append(r)
        old, new = pair
        for _ in range(60):
            old.scroll(-1)
            rn = new.scroll(-1)
            self.assertEqual(old.contexts(), new.contexts())
            self.assertLess(rn['io'], 16 * KIB)
        self.assertIn('29', {c[0][:2] for c in new.contexts()})

    def test_chosen_previous_block_size(self):
        self.assertEqual(M.C['prev_alvo'], 48)
        self.assertEqual(M.C['next_alvo'], 48)
        r = M.Reader(fixture(), 'new')
        r.open_file()
        r.land_top(M.article_offset(fixture(), 2000))
        recs = [x for x in (r.scroll(-1) for _ in range(240)) if x and x.get('moved')]
        ref = [x for x in recs if x['prev_refill']]
        self.assertLessEqual(len(ref), 6)
        self.assertLess(max(ms(x) for x in recs), 40)
        self.assertLess(sum(ms(x) for x in recs) / len(recs), PROC_HIT_MS)


class FirmwareContractTest(unittest.TestCase):
    def test_header_buffered_reader(self):
        self.assertIn('#include "lex_leitor_scroll.h"', INO)
        inc = INO[:INO.index('#include "lex_leitor_scroll.h"')]
        self.assertEqual(inc.rstrip().split('\n')[-1].strip().startswith('//'), True)
        self.assertGreater(inc.rfind('#if LEX_DEVICE_V1_ENABLED'), inc.rfind('#endif'))      # included only with the flag
        self.assertEqual(re.findall(r'SD\.open\(([^)]*)\)', HDR), ['caminho,FILE_READ'])     # read only, one open
        for s in ('~LexArquivoBuffer(){ close(); }', 'LexArquivoBuffer(const LexArquivoBuffer&)=delete;', 'lexScrollPerf.bytes+=',
                  'lexScrollPerf.seeks++', 'maxAbertos', '#define LEX_LEITOR_BLOCO 512'):
            self.assertIn(s, HDR, s)
        self.assertNotRegex(HDR, r'\b(malloc|ps_malloc|heap_caps_malloc|new\s+\w+\[)')

    def test_same_wrap_body(self):
        wrap = INO[INO.index('#if LEX_DEVICE_V1_ENABLED\n// Mesmo corpo'):]
        self.assertIn('bool avancarUmaLinhaVisual(LexArquivoBuffer &f, uint32_t inicio, uint32_t &proximo)\n#else\n'
                      'bool avancarUmaLinhaVisual(File &f, uint32_t inicio, uint32_t &proximo)\n#endif\n{', wrap)

    def test_context_rebuild_order(self):
        r = func(INO, 'void reconstruirContextoAntesOffset(uint32_t limite, ContextoJuridicoAtivo &saida)\n{')
        v1 = r[:r.index('#else')]
        self.assertLess(v1.index('if(usouCheckpoint && inicio>=limite)'), v1.index('LexArquivoBuffer f('))   # exact: no open
        self.assertLess(v1.index('lexAncoraArtigoAntes(f,limite'), v1.index('lexV1ContextoEstruturalAntes(limite,base,inicioMapa,saida)'))
        self.assertIn('if(!usouCheckpoint) inicio=limite>LEX_CTX_ANCORA_MAX ? limite-LEX_CTX_ANCORA_MAX : 0;', v1)
        self.assertNotIn('limite-JANELA_RECONSTRUCAO : 0;', v1)              # the 256 KiB blind window is gone from V1
        a = func(INO, 'static int lexAncoraArtigoAntes(LexArquivoBuffer &f, uint32_t limite, uint32_t piso, uint32_t &ancora)\n{')
        self.assertIn('if(limite-cursor>=LEX_CTX_ANCORA_MAX) return -1;', a)
        self.assertIn('lexLinhaEhAncoraArtigo(f,p,limite)', a)
        v = func(INO, 'static bool lexLinhaEhAncoraArtigo(LexArquivoBuffer &f, uint32_t p, uint32_t limite)\n{')
        self.assertIn('aplicarLinhaContextoCompatCF(t,linha,true,p,comProxima?proxima:nullptr);', v)   # the parser decides
        self.assertIn('return t.artigo[0] && t.offsetArtigo==p;', v)

    def test_refill_blocks_and_limits(self):
        p = func(INO, 'static int lexIndexarAntesDaJanelaV1()\n{')
        for s in ('LEX_CACHE_ANTERIOR_ALVO', 'LEX_REFILL_ORCAMENTO', 'lexInicioLinhaFisicaAntes(f,fim,inicio,failsafe)',
                  'avancarUmaLinhaVisual(f,pos,seguinte)', 'cacheLeitorTopo+=quantidade;', 'REFILL_FAILSAFE'):
            self.assertIn(s, p, s)
        b = func(INO, 'static bool lexInicioLinhaFisicaAntes(LexArquivoBuffer &f, uint32_t fim, uint32_t &inicio, bool &failsafe)\n{')
        self.assertIn('fim>LEX_PARAGRAFO_MAX?fim-LEX_PARAGRAFO_MAX:0', b)
        r = func(INO, 'void rolarLeitor(int delta)')
        for s in ('while(linhaTopo+delta<LEX_CACHE_ANTERIOR_MIN && offsetsLinhas[0]>0){',
                  'desejado+LEITOR_LINHAS_VISIVEIS+LEX_CACHE_SEGUINTE_MIN>=linhasIndexadas',
                  'indexarAte(desejado+LEITOR_LINHAS_VISIVEIS+LEX_CACHE_SEGUINTE_ALVO);',
                  'if(delta>LEITOR_LINHAS_VISIVEIS) delta=LEITOR_LINHAS_VISIVEIS;',                 # clamp preserved (no acceleration)
                  '[SCROLL] dir=%s passos=%d pend=%d'):
            self.assertIn(s, r, s)
        c = func(INO, 'void carregarCacheLeitorCompleto()\n{')
        self.assertIn('lexPrepararCacheBidirecional();', c)
        prep = func(INO, 'static void lexPrepararCacheBidirecional()\n{')
        for s in ('indexarAntesDaJanela();', 'indexarAte(linhaTopo+LEITOR_LINHAS_VISIVEIS+LEX_CACHE_SEGUINTE_ALVO);',
                  'reconstruirContextoAntesOffset(offAquece,descartado);'):
            self.assertIn(s, prep, s)

    def test_landing_and_search_untouched(self):
        f = func(INO, 'static void lexV1PousarBuscaNaLinhaAtiva(uint32_t ocorrencia)')
        self.assertNotIn('lexPreparar', f)                                     # prepared by the normal full cache load
        for name in ('static bool lexV1PesquisarArtigoEstrutural(const String &n, uint32_t inicio)',
                     'static bool lexV1ArtIdxBuscar(uint16_t num, uint8_t suf, uint32_t inicio'):
            self.assertNotIn('LexArquivoBuffer', func(INO, name))
            self.assertNotIn('lexPasso', func(INO, name))
        self.assertNotIn('lexScrollPerf', func(INO, 'void lexV1SincronizarAlvo(int indiceContexto)\n{'))

    def test_flag0_unchanged(self):
        self.assertEqual(strip_v1(INO), strip_v1(head('firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino')))
        for s in ('LexArquivoBuffer', 'lexPasso', 'lexAncoraArtigoAntes', 'LEX_CACHE_ANTERIOR', 'lex_leitor_scroll.h'):
            self.assertNotIn(s, strip_v1(INO), s)

    def test_model_reads_firmware_constants(self):
        self.assertEqual(M.C['rows'], 12)
        self.assertEqual(M.C['checkpoints'], 128)
        self.assertEqual(M.C['seed_min'], 2048)
        self.assertEqual(M.C['anchor_max'], 32768)
        self.assertEqual(M.C['par_max'], 65536)
        self.assertEqual(M.C['refill_budget'], 8192)
        self.assertEqual(M.C['block'], 512)


if __name__ == '__main__':
    unittest.main()
