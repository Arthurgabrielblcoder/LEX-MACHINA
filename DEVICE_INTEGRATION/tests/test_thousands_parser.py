"""THOUSANDS_PARSER_FIX: 'Art. 2.000.' is article 2000, never ART=2 (Codigo Civil, CPC, CLT and any norm above art. 999).

Origin (device log backups/indexed_bench/bench_serial.bin: "CONTEXTO: ART=2" after landing on art. 2.000): lerNumeroDispositivo()
(contexto_juridico.h) read digits and stopped at the first '.', so the thousands separator ended the number. The same defect
existed in the host structural parser (LEGAL_TARGET_ID/structure_parser.py ART_RE: '(\\d{1,4})' then '.' as punctuation).
Rule now: a '.' belongs to the number only when a 1-3 digit block is followed by '.' + EXACTLY 3 digits (4th char not a digit).
The firmware change is inside '#if LEX_DEVICE_V1_ENABLED' (flag0 unchanged); the host port mirrors the V1 build.
"""
import json
import math
import re
import subprocess
import sys
import tempfile
import unittest
from functools import lru_cache
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_article_search_index as AI  # noqa: E402
import context_parser_port as P  # noqa: E402
import scroll_model as M  # noqa: E402
import scroll_performance_benchmark as B  # noqa: E402
import structure_parser as S  # noqa: E402

FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
INO = (FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
CTX = (FW / 'contexto_juridico.h').read_text(encoding='utf-8')
CC_REAL = DI / 'backups/sd_20260929T163407Z/data/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'
CHECK = (998, 999, 1000, 1001, 1999, 2000, 2001, 2400)

TABLE = [('Art. 1. Texto', '1'), ('Art. 2. Texto', '2'), ('Art. 20. Texto', '20'), ('Art. 200. Texto', '200'),
         ('Art. 5º Texto', '5'), ('Art. 1º Texto', '1'), ('Art. 29-A. Texto', '29-A'), ('Art. 999. Texto', '999'),
         ('Art. 1.000. Texto', '1000'), ('Art. 1.001. Texto', '1001'), ('Art. 1.234. Texto', '1234'), ('Art. 1.999. Texto', '1999'),
         ('Art. 2.000. Texto', '2000'), ('Art. 2.001. Texto', '2001'), ('Art. 2.046. Texto', '2046'), ('Art. 2.000', '2000'),
         ('Art. 1.000-A. Texto', '1000-A'), ('Art. 1.000.000 Texto', '1000000'), ('Artigo 1.500. Texto', '1500'),
         ('Art 2.000 Texto', '2000'), ('Art. 2.000º Texto', '2000')]
MALFORMED = [('Art. 1.00. Texto', '1'), ('Art. 1.0000 Texto', '1'), ('Art. 1234.567 Texto', '1234'), ('Art. 2.0. Texto', '2'),
             ('Art. 2.000.00 Texto', '2000'), ('Art. 12.34 Texto', '12'), ('Art. 2.00a Texto', '2')]


def parse(line, fixed=True):
    old = P.THOUSANDS
    P.THOUSANDS = fixed
    try:
        c = dict(artigo='', paragrafo='', inciso='', alinea='')
        ok = P.apply_line(c, line.encode('utf-8'))
        return ok, c['artigo']
    finally:
        P.THOUSANDS = old


def head(path):
    return subprocess.run(['git', 'show', f'HEAD:{path}'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8').stdout


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
    return B.civil_like_norm_with_map(2500)


def landed(art, landing='centered'):
    data, smap = fixture()
    r = M.Reader(data, 'new')
    r.open_file()
    (r.land_centered if landing == 'centered' else r.land_top)(M.article_offset(data, art))
    return r


def rows_vs_targets(r, smap):
    """(context artigo, structural article) for the 12 visible rows."""
    out = []
    for i in range(r.ROWS):
        idx = r.top + i
        if idx < len(r.offs):
            tid = M.target_at(smap, r.offs[idx])
            out.append((r.contexts()[i][0], tid.split('ART.')[1] if tid else ''))
    return out


class ParsingTableTest(unittest.TestCase):
    def test_table(self):
        for line, want in TABLE:
            self.assertEqual(parse(line), (True, want), line)

    def test_malformed_fail_safe(self):
        for line, want in MALFORMED:
            self.assertEqual(parse(line), (True, want), line)              # stops at the dot, as before; never a decimal
        self.assertEqual(parse('Art. 999.999.999.999 Texto'), (False, ''))  # overflow: rejected, context untouched
        self.assertEqual(parse('Art. .500 Texto'), (False, ''))
        self.assertEqual(parse('Art. Texto'), (False, ''))

    def test_bug_reproduced_without_fix(self):
        self.assertEqual(parse('Art. 2.000. Texto', fixed=False), (True, '2'))
        self.assertEqual(parse('Art. 1.999. Texto', fixed=False), (True, '1'))

    def test_suffix_ordinal_and_other_devices_preserved(self):
        c = dict(artigo='', paragrafo='', inciso='', alinea='')
        for line in ('Art. 2.000. Caput.', '§ 1º Paragrafo.', 'II - inciso;', 'a) alinea;'):
            self.assertTrue(P.apply_line(c, line.encode('utf-8')), line)
        self.assertEqual((c['artigo'], c['paragrafo'], c['inciso'], c['alinea']), ('2000', '1', 'II', 'a'))
        self.assertEqual(parse('Parágrafo único. Texto'), (True, ''))  # not an article line

    def test_remissions_keep_their_own_number(self):
        # context parser: a line-start remission is parsed as before (art. 2), never as 12858 / 2858
        self.assertEqual(parse('art. 2º da Lei nº 12.858, de 2013'), (True, '2'))


class StructuralParserTest(unittest.TestCase):
    def test_host_art_re(self):
        for line, want in TABLE[:-3] + [('Art. 1.000-A. Texto', '1000-A')]:
            if 'º' in want or line.startswith('Artigo') or line.startswith('Art ') or 'Art. 1.000.000' in line:
                continue
            m = S.ART_RE.match(line)
            self.assertIsNotNone(m, line)
            got = m.group(1).replace('.', '') + ('-' + m.group(2) if m.group(2) else '')
            self.assertEqual(got, want, line)
        m = S.ART_RE.match('Art. 2. Texto')
        self.assertEqual((m.group(1), m.group(3)), ('2', 'Texto'))
        m = S.ART_RE.match('Art. 1234.567 Texto')
        self.assertEqual(m.group(1), '1234')

    def test_parse_structure_targets(self):
        text = 'Art. 999. Primeiro.\nArt. 1.000. Segundo.\n§ 1º Paragrafo.\nArt. 2.000. Terceiro.\nArt. 2.001-A. Quarto.\n'
        idx = S.parse_structure(text, 'CF88')
        tids = [t['target_id'] if isinstance(t, dict) else t for t in (idx['targets'] if isinstance(idx, dict) else idx[0])]
        for tid in ('CF88:ART.999', 'CF88:ART.1000', 'CF88:ART.1000:PAR.1', 'CF88:ART.2000', 'CF88:ART.2001-A'):
            self.assertIn(tid, tids, tid)
        self.assertNotIn('CF88:ART.2', tids)

    def test_strict_mode_still_rejects_remission_lines(self):
        idx = S.parse_structure('Art. 1.000. Caput.\nart. 2º da Lei nº 12.858, de 2013\n', 'CF88', article_case_sensitive=True)
        tids = [t['target_id'] if isinstance(t, dict) else t for t in (idx['targets'] if isinstance(idx, dict) else idx[0])]
        self.assertIn('CF88:ART.1000', tids)
        self.assertNotIn('CF88:ART.2', tids)


class FixtureTest(unittest.TestCase):
    def test_fixture_uses_thousands_separator(self):
        data, smap = fixture()
        self.assertIn(b'\nArt. 2.000. ', data)
        self.assertNotIn(b'\nArt. 2000. ', data)
        self.assertEqual(len(smap), 2500)

    def test_landing_active_target_and_context(self):
        data, smap = fixture()
        for art in CHECK:
            r = landed(art)
            off = r.offs[r.top + r.ACTIVE]
            self.assertEqual(M.target_at(smap, off), f'F1:ART.{art}', art)        # ACTIVE_TARGET (structural map)
            self.assertEqual(r.contexts()[r.ACTIVE][0], str(art), art)            # CONTEXTO
            self.assertEqual(r.contexts()[r.ACTIVE][0], M.target_at(smap, off).split('ART.')[1])
            top = landed(art, 'top')
            self.assertEqual(top.contexts()[0][0], str(art), art)                 # legacy landing: row 0 is the article

    def test_scroll_1999_2000_2001(self):
        data, smap = fixture()
        r = landed(2000)
        seen = [r.contexts()[r.ACTIVE][0]]

        def step(d):
            rec = r.scroll(d)
            for ctx, tgt in rows_vs_targets(r, smap):
                self.assertEqual(ctx, tgt)                                       # every row, every step
                self.assertNotIn(ctx, ('1', '2'))                                # never ART.2 from "2.000"
            seen.append(r.contexts()[r.ACTIVE][0])
            return rec

        first = step(-1)
        self.assertLess(first['io'], 16 * 1024)                                   # scroll fix preserved
        while seen[-1] != '1999':
            step(-1)
        while seen[-1] != '2000':
            step(1)
        while seen[-1] != '2001':
            step(1)
        self.assertLess(len(seen), 1500)                                        # loop guard
        order = [a for i, a in enumerate(seen) if i == 0 or a != seen[i - 1]]
        self.assertEqual(order[:4], ['2000', '1999', '2000', '2001'])

    def test_cache_hit_refill_and_landings(self):
        data, smap = fixture()
        r = landed(2000, 'top')
        for d in [-1] * 130 + [1] * 200 + [-6] * 8 + [6] * 8:
            r.scroll(d)
            for ctx, tgt in rows_vs_targets(r, smap):
                self.assertEqual(ctx, tgt)

    def test_first_up_art2000_bounded(self):
        data, smap = fixture()
        for mode in ('new',):
            res = B.landing_case(data, 2000, mode)[1]['first_up']
            self.assertLess(res['io'], 16 * 1024)
            self.assertEqual(res['perbyte'], 0)
            self.assertLess(res['us'] / 1000.0, 80.0)


class IndexedSearchTest(unittest.TestCase):
    def test_index_finds_2000_without_text_scan(self):
        data, smap = fixture()
        targets = [dict(target_id=t, kind='ARTIGO', line_start=data.count(b'\n', 0, o) + 1) for o, t in smap]
        import hashlib
        idx = dict(source=dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest()), targets=targets,
                   target_index_sha256='fixture')
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / 'T.txt').write_bytes(data)
            (Path(t) / 'I.json').write_text(json.dumps(idx), encoding='utf-8')
            blob, man = AI.build(Path(t) / 'T.txt', Path(t) / 'I.json')
        ai = AI.ArticleIndex(blob, data)
        ai.comparisons = 0
        hit = ai.find(2000)
        self.assertEqual(hit[0], dict((t, o) for o, t in smap)['F1:ART.2000'])
        self.assertLessEqual(ai.comparisons, math.ceil(math.log2(man['records'])) + 4)

    def test_firmware_search_and_repeat_untouched(self):
        for name in ('static bool lexV1ArtigoChave(', 'static bool lexV1ArtIdxBuscar(', 'static void lexV1MarcarRepeticaoBusca()',
                     'void lexV1EntrarBusca()\n{', 'static bool lexV1PesquisarArtigoEstrutural('):
            self.assertNotIn('lerNumeroDispositivo', func(INO, name), name)
        self.assertIn('artigoDigitado=numeroUltimaBusca;', func(INO, 'void lexV1EntrarBusca()\n{'))   # REPEAT_READY: typed "2000"
        self.assertNotIn('context_parser_port', (DI / 'tools/build_article_search_index.py').read_text(encoding='utf-8'))


class FirmwareContractTest(unittest.TestCase):
    def test_header_rule_inside_v1(self):
        n = func(CTX, 'static inline bool lerNumeroDispositivo(const char *&p, char *saida, size_t capacidade)')
        v1 = n[n.index('#if LEX_DEVICE_V1_ENABLED'):n.index('#endif')]
        for s in ("if(n<=3){", "while(p[0]=='.' && isdigit((unsigned char)p[1]) && isdigit((unsigned char)p[2]) &&",
                  "isdigit((unsigned char)p[3]) && !isdigit((unsigned char)p[4])){",
                  'if(valor>(LEX_NUMERO_DISPOSITIVO_MAX-grupo)/1000u) return false;', 'if(n+3>=capacidade) return false;'):
            self.assertIn(s, v1, s)
        self.assertLess(n.index('#endif'), n.index("if((*p=='-' || *p=='.') && isalpha((unsigned char)p[1])){"))  # suffix after
        self.assertIn('#define LEX_NUMERO_DISPOSITIVO_MAX 999999999u', CTX)
        self.assertIn('static_assert(LEX_CONTEXTO_MILHAR==1,', INO)
        self.assertEqual(P.THOUSANDS_MAX, 999999999)

    def test_boot_self_test_covers_table(self):
        v = func(CTX, 'static inline int validarRotinaContextoJuridico()')
        for s in ('"Art. 2.000. Texto"', '"2000"', '"Art. 1.000-A. Texto"', '"1000-A"', '"Art. 1.00. Texto"', '"Art. 1234.567 Texto"',
                  '"Art. 999.999.999.999 Texto"'):
            self.assertIn(s, v, s)
        entradas = re.search(r'entradas\[\]=\{(.*?)\};', v, re.S).group(1)
        esperados = re.search(r'esperados\[\]=\{(.*?)\};', v, re.S).group(1)
        ins = [bytes(x, 'latin-1').decode('unicode_escape').encode('latin-1').decode('utf-8')
               for x in re.findall(r'"((?:[^"\\]|\\.)*)"', entradas)]
        outs = re.findall(r'"([^"]*)"', esperados)
        self.assertEqual(len(ins), len(outs))
        for line, want in zip(ins, outs):
            self.assertEqual(parse(line), (True, want), line)                  # host port == firmware self-test table

    def test_flag0_header_unchanged(self):
        # full flag0 comparison against HEAD: test_article_search_landing.test_flag0_source_unchanged (strip_v1 view)
        self.assertNotIn('LEX_NUMERO_DISPOSITIVO_MAX', strip_v1(CTX))
        self.assertNotIn('LEX_CONTEXTO_MILHAR', strip_v1(CTX))
        n = func(strip_v1(CTX), 'static inline bool lerNumeroDispositivo(const char *&p, char *saida, size_t capacidade)')
        self.assertEqual(n, func(head('firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/contexto_juridico.h'),
                                 'static inline bool lerNumeroDispositivo(const char *&p, char *saida, size_t capacidade)'))


@unittest.skipUnless(CC_REAL.is_file(), 'Codigo Civil TXT from the local SD backup (not in Git)')
class RealCodigoCivilTest(unittest.TestCase):
    def test_every_header_distinct_and_up_to_2046(self):
        d = CC_REAL.read_bytes()
        for fixed, expect_ok in ((False, False), (True, True)):
            arts = []
            for line in d.split(b'\n'):
                line = line.rstrip(b'\r')
                if re.match(rb'[ \t]*Art', line):
                    old = P.THOUSANDS
                    P.THOUSANDS = fixed
                    c = dict(artigo='', paragrafo='', inciso='', alinea='')
                    if P.apply_line(c, line[:511]):
                        arts.append(c['artigo'])
                    P.THOUSANDS = old
            mx = max(int(re.match(r'\d+', a).group()) for a in arts)
            self.assertEqual(mx == 2046 and len(set(arts)) == len(arts), expect_ok, (fixed, mx, len(arts), len(set(arts))))
        for k in (1000, 1001, 1999, 2000, 2046):
            self.assertIn(str(k), arts)


if __name__ == '__main__':
    unittest.main()
