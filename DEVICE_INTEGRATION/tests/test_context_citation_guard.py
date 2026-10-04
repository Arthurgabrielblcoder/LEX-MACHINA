"""CONTEXT_CITATION_GUARD: a remission at the start of a PHYSICAL line is never local structure for CONTEXTO.

Cause (physical, MARIA2006 art. 1): the official TXT breaks the physical line at the hyperlink of a remission ("...nos termos do" /
"§ 8º do art. 226 da Constituição Federal,"). aplicarLinhaContextoJuridico() only looks at the line start, so "§ 8º" set PAR=8 on
art. 1 of the Lei Maria da Penha. Fix (contexto_juridico.h, LEX_DEVICE_V1_ENABLED only): the bytes right after the device number
decide (remission words / citation comma of the approved structural parser), 'Art' only with capital A (strict mode of the approved
indexes), inciso/alínea heading shape. The decision uses only the line itself: identical on scroll DOWN/UP, landing, cache refill,
context rebuild and the "Art." anchor; no I/O and no state. ACTIVE_TARGET / layers come from the TEXT_MAP and are not touched.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import context_citation_audit as A  # noqa: E402
import context_parser_port as P  # noqa: E402
import scroll_model as M  # noqa: E402
import structure_parser as SP  # noqa: E402

FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
CTX = (FW / 'contexto_juridico.h').read_text(encoding='utf-8')
INO_REL = 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'
BASELINE_TAG = 'lex-device-v1-72-indexes-approved-2026-10-04'
MARIA = A.OVERRIDES['MARIA2006']
CF_RUNTIME = A.OVERRIDES['CF88']
CORPUS_OK = A.CORPUS.is_dir() and MARIA.is_file() and CF_RUNTIME.is_file()


def git_show(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8').stdout


def strip_v1(src):
    """Source as compiled with LEX_DEVICE_V1_ENABLED=0 (same helper as test_article_search_landing)."""
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


def ctx(art='1', par='', inc='', ali=''):
    return dict(artigo=art, paragrafo=par, inciso=inc, alinea=ali)


def apply(line, c=None, guard=True):
    c = dict(c or ctx())
    P.CITATION_GUARD = guard
    try:
        ok = P.apply_line(c, line.encode('utf-8'))
    finally:
        P.CITATION_GUARD = True
    return ok, c


def replay(data, guard=True):
    """Context after every physical line (1-based line number -> context)."""
    P.CITATION_GUARD = guard
    try:
        c, out = ctx(''), {}
        for n, line in enumerate(data.split(b'\n'), start=1):
            P.apply_line(c, line.rstrip(b'\r')[:511])
            out[n] = dict(c)
        return out
    finally:
        P.CITATION_GUARD = True


def line_no(data, prefix):
    for n, line in enumerate(data.split(b'\n'), start=1):
        if line.decode('utf-8', 'replace').strip().startswith(prefix):
            return n
    raise AssertionError(prefix)


def firmware_list(name):
    body = re.search(name + r'\[\]=\{(.*?)\};', CTX, re.S).group(1)
    return [bytes(x, 'latin-1').decode('unicode_escape').encode('latin-1').decode('utf-8')
            for x in re.findall(r'"((?:[^"\\]|\\.)*)"', body)]


class SourceContractTest(unittest.TestCase):
    def test_guard_only_in_device_v1_build(self):
        old = git_show(BASELINE_TAG, 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/contexto_juridico.h')
        self.assertTrue(old)
        self.assertEqual(strip_v1(CTX), strip_v1(old))                           # flag0 view of the header: byte-identical
        self.assertNotIn('remissaoAposDispositivo', strip_v1(CTX))
        self.assertIn('#define LEX_CONTEXTO_CITACAO 1', CTX)

    def test_sketch_untouched(self):
        # only the parser changed: reader, scroll, cache refill, landing, TEXT_MAP, layers and search code are byte-identical
        ino = (ROOT / INO_REL).read_text(encoding='utf-8')
        self.assertEqual(ino.replace('\r\n', '\n'), git_show(BASELINE_TAG, INO_REL).replace('\r\n', '\n'))

    def test_no_io_no_state_in_guard(self):
        guard = CTX[CTX.index('#define LEX_CONTEXTO_CITACAO 1'):CTX.index('static inline bool aplicarLinhaContextoJuridico(')]
        for forbidden in ('SD.', 'File', 'seek', 'read(', 'static char', 'static int', 'static uint', 'malloc', 'String'):
            self.assertNotIn(forbidden, guard, forbidden)                       # local, constant cost, never a scan

    def test_remission_words_are_the_approved_structural_ones(self):
        fw = set(firmware_list('PALAVRAS_REMISSAO'))
        self.assertEqual(fw, set(SP.REMISSION_WORDS))
        self.assertEqual({w.decode() for w in P.REMISSION_WORDS}, set(SP.REMISSION_WORDS))

    def test_firmware_self_test_table_matches_port(self):
        cites = firmware_list('citacoes')
        self.assertGreaterEqual(len(cites), 15)
        for line in cites:
            ok, c = apply(line)
            self.assertEqual((ok, c), (False, ctx()), line)                     # rejected, context intact
            ok_old, _ = apply(line, guard=False)
            if not line.startswith(('c', 'e)')):                                 # old parser read them as structure (the bug)
                self.assertTrue(ok_old or line.startswith(('art. 701', 'Art. 101')), line)


class LineRuleTest(unittest.TestCase):
    """Items 1-8: negative remissions in running text, positive structural headings."""

    def test_01_maria2006_art1_par8_line(self):
        line = '§ 8º do art. 226 da Constituição Federal,'
        self.assertEqual(apply(line, guard=False), (True, ctx('1', '8')))          # before: PAR=8 (physical bug)
        self.assertEqual(apply(line), (False, ctx('1')))                         # after: still ART.1

    def test_02_paragraph_in_running_text(self):
        for line in ('§ 2º do art. 236', '§ 3º do', '§ 5º deste artigo, não excluirá', '§ 6° deste artigo ficará',
                     '§ 6º, todos da Constituição Federal', '§ 1º, II,', '§ 3º pela Lei nº 6.018, de 1974',
                     'parágrafo único do art. 274', 'parágrafo único, inciso I do art. 34', 'parágrafo único pela Lei nº 13.964',
                     'art. 47 da Lei nº 12.351', 'art. 701', 'Art. 95 da Constituição', 'Art. 153, às 17 (dezessete) horas.'):
            self.assertEqual(apply(line, ctx('10', '1', 'II')), (False, ctx('10', '1', 'II')), line)

    def test_03_inciso_in_running_text(self):
        for line in ('III.', 'III do art. 5º', 'civil.', 'civil:', 'mil-réis a dois contos de réis.', 'dividi-los em outros',
                     'D.O.U. de 2.9.1981', 'L. F. Cirne Lima', 'c', 'x', 'IV, do art. 5º'):
            self.assertEqual(apply(line, ctx('10', '', 'II')), (False, ctx('10', '', 'II')), line)

    def test_04_alinea_in_running_text(self):
        for line in ('e), ou deixar de divulgá-la (§ 4º)', 'b), da Lei', 'alínea b do inciso II'):
            self.assertEqual(apply(line, ctx('10', '', 'II', 'a')), (False, ctx('10', '', 'II', 'a')), line)

    def test_05_structural_paragraph(self):
        for line, par in (('§ 1º O juiz', '1'), ('§ 2º A multa prevista no', '2'), ('§ 1º o trabalho terá a', '1'),
                          ('§ 4º os ex-administradores poderão', '4'), ('§ 2º (VETADO).', '2'),
                          ('§ 1° e § 2°', '1'), ('§ 3º', '3'), ('§ 12. Texto', '12'), ('§ 2º. O', '2')):
            self.assertEqual(apply(line, ctx('10', '', 'IV')), (True, ctx('10', par)), line)

    def test_06_paragrafo_unico(self):
        for line in ('Parágrafo único. O disposto', 'Parágrafo único - Texto', 'Parágrafo único. a exclusão do crédito',
                     'Paragrafo unico. Texto', 'Parágrafo único (VETADO)', 'Parágrafo único'):
            self.assertEqual(apply(line, ctx('10', '', 'IV', 'b')), (True, ctx('10', 'unico')), line)

    def test_07_structural_inciso(self):
        for line, inc in (('III - hipótese', 'III'), ('I – a soberania;', 'I'), ('II', 'II'), ('IV:', 'IV'),
                          ('Il - OCR', 'IL'), ('lI - OCR', 'LI'), ('XI - a casa é asilo', 'XI'), ('VII — texto', 'VII')):
            self.assertEqual(apply(line, ctx('10', '2')), (True, ctx('10', '2', inc)), line)

    def test_08_structural_alinea(self):
        for line, al in (('a) da receita do imposto', 'a'), ('b) do imposto previsto no art. 153, IV; e', 'b'),
                         ('c) curta', 'c'), ('d) pela remoção', 'd')):
            self.assertEqual(apply(line, ctx('10', '', 'II')), (True, ctx('10', '', 'II', al)), line)

    def test_article_headings_kept(self):
        for line, art in (('Art. 1º Esta Lei cria', '1'), ('Art. 2.000. Texto', '2000'), ('Art. 481. Pelo contrato', '481'),
                          ('Art. 1.358-O. condomínio edilício', '1358-O'), ('Artigo 13. Texto', '13'), ('Art. 5', '5')):
            self.assertEqual(apply(line, ctx('9', '1', 'II', 'a')), (True, ctx(art)), line)


@unittest.skipUnless(CORPUS_OK, 'local SD copy / MARIA2006 repair staging / CF runtime not present')
class CorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = A.run()
        cls.maria = MARIA.read_bytes()
        cls.cf = CF_RUNTIME.read_bytes()

    def test_01_maria2006_art1_context_before_after(self):
        n = line_no(self.maria, '§ 8º do art. 226')
        art2 = line_no(self.maria, 'Art. 2º')
        before, after = replay(self.maria, False), replay(self.maria, True)
        self.assertEqual(before[n], ctx('1', '8'))                               # reproduced
        for k in range(line_no(self.maria, 'Art. 1º'), art2):
            self.assertEqual(after[k], ctx('1'), k)                             # ART.1 until art. 2 (no real subdivision in art. 1)
        self.assertEqual(after[art2], ctx('2'))

    def test_maria2006_real_subdivisions(self):
        after = replay(self.maria)
        self.assertEqual(after[line_no(self.maria, 'Art. 5º')], ctx('5'))
        self.assertEqual(after[line_no(self.maria, 'Parágrafo único. As relações')], ctx('5', 'unico'))
        art7 = line_no(self.maria, 'Art. 7º')
        self.assertEqual(after[art7 + 1][('inciso')], 'I')
        n = line_no(self.maria, 'Art. 12-C')
        self.assertEqual(after[n], ctx('12-C'))
        lines = self.maria.split(b'\n')
        incs = [after[k]['inciso'] for k in range(n, n + 12) if lines[k - 1].strip()[:3] in (b'I -', b'II ', b'III')]
        self.assertTrue(incs)
        pars = {after[k]['paragrafo'] for k in range(1, len(lines) + 1)} - {''}
        self.assertTrue({'1', '2', '3', 'unico'} <= pars, pars)
        self.assertEqual(self.audit['per_norm']['MARIA2006']['eliminated'], {'PAR': 2, 'ART': 4})

    def test_cf_art37_par6_and_art40(self):
        after = replay(self.cf)
        n = line_no(self.cf, '§ 6º As pessoas jurídicas de direito público')
        self.assertEqual(after[n], ctx('37', '6'))
        n40 = line_no(self.cf, 'Art. 40.')
        self.assertEqual(after[n40]['artigo'], '40')
        pars40 = set()
        k = n40
        while after[k]['artigo'] == '40':
            pars40.add(after[k]['paragrafo'])
            k += 1
        self.assertTrue({'1', '2', '3', '4', '6'} <= pars40, pars40)

    def test_cc_and_cpc_paragraphs_preserved(self):
        per = self.audit['per_norm']
        self.assertEqual(per['CC2002']['eliminated'], {'INC': 1})                 # only a stray 'c' (alínea citation fragment)
        self.assertGreater(per['CC2002']['structural_after']['PAR'], 500)
        cpc = [e for e in self.audit['eliminated'] if e['norma'] == 'CPC2015' and e['kind'] in ('PAR', 'UNICO')]
        self.assertTrue(cpc)
        for e in cpc:                                                           # every CPC loss is a remission "... do art. N"
            self.assertRegex(e['text'], r'^(§ \d+º|parágrafo único)(,| do| da)', e)
        self.assertGreater(per['CPC2015']['structural_after']['PAR'], 1000)

    def test_full_corpus_no_legitimate_structure_lost(self):
        a = self.audit
        self.assertEqual(a['norms'], 72)
        self.assertEqual(a['added_total'], 0)                                    # the guard never creates a context
        self.assertGreater(a['oracle_records'], 15000)
        self.assertEqual(a['oracle_structural_lost'], 0)                         # no indexed heading / CF TEXT_MAP record lost
        self.assertFalse(any(e['oracle_structural'] for e in a['eliminated']))
        for e in a['eliminated']:
            if e['kind'] in ('PAR', 'UNICO'):
                self.assertTrue(re.match(r'^(§\s*\d+[º°o]?|[pP]ar[aá]grafo [uú]nico)\s*(,|;|\.?\s*(%s)(\s|$))'
                                         % '|'.join(map(re.escape, SP.REMISSION_WORDS)), e['text']), e)
            elif e['kind'] == 'ART':
                self.assertTrue(e['text'].startswith('art') or re.match(r'^Art\. [\d.]+º?\s*(,|;|(%s)\b)'
                                                                         % '|'.join(map(re.escape, SP.REMISSION_WORDS)), e['text']), e)

    def test_cf_text_map_agreement_not_reduced(self):
        m = A.CF_TEXT_MAP
        P.CITATION_GUARD = False
        try:
            before = P.compare(m)
        finally:
            P.CITATION_GUARD = True
        after = P.compare(m)
        self.assertGreaterEqual(after['agree'], before['agree'])
        self.assertLessEqual(after['differ'], before['differ'])
        self.assertNotIn('OUTROS', after['categories'])


@unittest.skipUnless(CORPUS_OK, 'MARIA2006 repair staging not present')
class ReaderPathTest(unittest.TestCase):
    """Items 9-13: the same contexts on every reader path (scroll_model replays the firmware reader with the port)."""

    @classmethod
    def setUpClass(cls):
        cls.maria = MARIA.read_bytes()

    def ideal(self, r):
        """Ground truth for the rows on screen: full parse from offset 0, then the rows like recalcularContextosCache."""
        c, out = M.ideal_contexts(self.maria, [r.line_off[0]]), []
        for i in range(r.ROWS):
            if not r.valid[i]:
                out.append(M.ctx_key(M.empty_ctx()))
                continue
            nxt = r.lines[i + 1] if i + 1 < r.ROWS and r.valid[i + 1] else None
            r.compat(c, r.lines[i], r.phys[i], nxt)
            out.append(M.ctx_key(c))
        return tuple(out)

    def test_09_visual_wrap(self):
        r = M.Reader(self.maria, 'new')
        r.open_file()
        r.land_centered(M.article_offset(self.maria, 1))
        rows = list(zip(r.lines, r.phys, r.contexts()))
        i = next(k for k, (t, _, _) in enumerate(rows) if t.startswith('§ 8º do art. 226'.encode()))
        self.assertTrue(rows[i][1])                                              # physical line start (the hyperlink split)
        self.assertFalse(rows[i - 1][1])                                         # "termos do" = visual continuation of art. 1
        for t, _, c in rows[r.ACTIVE:]:
            self.assertEqual(c, ('1', '', '', ''), t)
        long_par = M.Reader(self.maria, 'new')                                   # a wrapped REAL paragraph keeps PAR on its rows
        long_par.open_file()
        off = self.maria.index('§ 1º O juiz assegurará'.encode()) if '§ 1º O juiz assegurará'.encode() in self.maria else \
            self.maria.index(b'\n\xc2\xa7 1\xc2\xba ') + 1
        long_par.land_top(off)
        first = long_par.contexts()[0]
        self.assertEqual(first[1], '1')
        cont = [c for c, ph in zip(long_par.contexts()[1:], long_par.phys[1:]) if not ph]
        self.assertTrue(cont)

    def test_10_11_scroll_down_and_up_equal_fresh_landing(self):
        r = M.Reader(self.maria, 'new')
        r.open_file()
        tops = []
        for _ in range(120):                                                     # DOWN through arts. 1..12 (refills included)
            rec = r.scroll(1)
            if not rec or rec.get('moved', 0) == 0:
                break
            tops.append((r.offs[r.top], r.contexts()))
            self.assertEqual(r.contexts(), self.ideal(r), r.offs[r.top])         # no stale context on DOWN
        self.assertGreater(len(tops), 100)
        far = M.Reader(self.maria, 'new')                                        # UP after a far landing: anchor rebuild + refill
        far.open_file()
        far.land_centered(M.article_offset(self.maria, 12))
        for rd in (r, far):
            for _ in range(60):
                if not rd.scroll(-1) or rd.top == 0 and rd.offs[0] == 0:
                    break
                self.assertEqual(rd.contexts(), self.ideal(rd), rd.offs[rd.top])
        p8 = self.maria.index('§ 8º do art. 226'.encode())
        seen = [cs for off, cs in tops if off <= p8 < off + 600]
        self.assertTrue(seen)
        for cs in seen:
            self.assertNotIn('8', [c[1] for c in cs])

    def test_12_search_landing(self):
        for art in (1, 5, 7, 10, 12, 14, 24, 38, 40, 46):
            off = M.article_offset(self.maria, art)
            self.assertIsNotNone(off, art)
            r = M.Reader(self.maria, 'new')
            r.open_file()
            r.land_centered(off)
            self.assertEqual(r.contexts()[r.ACTIVE][0], str(art), art)
            old = M.Reader(self.maria, 'old')
            old.open_file()
            old.land_centered(off)
            self.assertEqual(r.contexts(), old.contexts(), art)                  # old and new reader paths agree

    def test_13_norm_switch_has_no_stale_context(self):
        cc = A.CORPUS / '2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'
        texts = [('CF', A.OVERRIDES['CF88'].read_bytes(), 193), ('MARIA', self.maria, 1)]
        if cc.is_file():
            texts.append(('CC', cc.read_bytes(), 2000))
        texts.append(('MARIA', self.maria, 1))
        seen = {}
        for name, data, art in texts:                                            # each open starts from an empty context
            r = M.Reader(data, 'new')
            r.open_file()
            r.land_centered(M.article_offset(data, art))
            cs = r.contexts()
            self.assertEqual(cs[r.ACTIVE][0], str(art), name)
            if name in seen:
                self.assertEqual(cs, seen[name])                                 # MARIA after CC == MARIA after CF
            seen[name] = cs
        self.assertNotIn('8', [c[1] for c in seen['MARIA']])


@unittest.skipUnless((DI / 'staging_sd_v1_batch04_run3_candidate/SD/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX').is_file(),
                     'approved RUN3 staging not present')
class ActiveTargetAndLayersTest(unittest.TestCase):
    """Items 14-15: ACTIVE_TARGET and layers come from the TEXT_MAP on the CONTEXTO row; the parser change cannot move them."""

    @classmethod
    def setUpClass(cls):
        import reader_viewport as V
        cls.r = V.Reader(DI / 'staging_sd_v1_batch04_run3_candidate/SD/99_LEX_V1',
                         artidx=DI / 'staging_sd_v1_batch04_run3_candidate/SD/99_LEX_V1/10_TARGETS/CF88_ARTICLE_SEARCH.IDX')

    def states(self):
        out = {}
        for n in (5, 37, 40, 193, 230):
            st = self.r.search(n)
            out[n] = (st['active_target'], st['layer4'], st['entenda'], st['juris'], st['correlatas'], tuple(st['works']))
        return out

    def test_14_15_active_target_and_layers_identical(self):
        P.CITATION_GUARD = False
        try:
            before = self.states()
        finally:
            P.CITATION_GUARD = True
        after = self.states()
        self.assertEqual(before, after)
        self.assertEqual(after[37][0], 'CF88:ART.37')
        self.assertEqual(after[193][0], 'CF88:ART.193')

    def test_14_active_row_context_matches_text_map_on_cf(self):
        data = self.r.data
        smap = [(o, t) for o, _, t in self.r.map]
        for n in (37, 40, 193):
            rm = M.Reader(data, 'new', kind='cf', cf_compat=True)
            rm.open_file()
            rm.land_centered(M.article_offset(data, n))
            c = rm.line_ctx[rm.ACTIVE]
            self.assertEqual(P.to_target(c, 'CF88'), M.target_at(smap, rm.line_off[rm.ACTIVE]), n)
            for k in range(1, 40):                                               # scroll through art. 37 §§ / art. 40 §§
                rm.scroll(1)
                if not rm.phys[rm.ACTIVE]:
                    continue
                tid = M.target_at(smap, rm.line_off[rm.ACTIVE])
                got = P.to_target(rm.line_ctx[rm.ACTIVE], 'CF88')
                if tid and not tid.endswith(':CAPUT') and not re.search(r'-[A-Z]$', tid.split(':')[-1]) \
                        and not tid.startswith('ADCT'):
                    self.assertEqual(got, tid, (n, k))


if __name__ == '__main__':
    unittest.main()
