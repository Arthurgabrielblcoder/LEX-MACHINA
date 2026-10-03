"""RUN3 CANDIDATE on the DEVICE simulator (REFERENCE_EXPANSION_01). Read-only: firmware, baseline header and physical SD untouched.

Layer 4 = WORK_REFERENCE rows of the query keys of the ACTIVE_TARGET (lexV1QueryKeysForActiveTarget: ART.n -> [ART.n, ART.n:CAPUT];
anything else -> itself) with the W flag of CF88_TARGETS.IDX (union). No inheritance to incisos, paragraphs or alineas.
"""
import hashlib
import re
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(ROOT / 'REFERENCE_COVERAGE_AUDIT'))
import canonical_layer_audit as A  # noqa: E402
import device_lookup_simulator as S  # noqa: E402

SD3 = DI / 'staging_sd_v1_run3_candidate/SD/99_LEX_V1'
SD1 = DI / 'staging_sd_v1/SD/99_LEX_V1'
RUN3 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run3'
HDR3 = RUN3 / 'device_candidate/lex_ref_detail_data.RUN3_CANDIDATE.h'
FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
REF = A.REFERENCIA


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@unittest.skipUnless((SD3 / '10_TARGETS/CF88_TARGETS.IDX').is_file(), 'RUN3 staging candidate not built')
class Run3DeviceLayer4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = S.Device(SD3)
        cls.flags = {p[0]: p[3] for p in A.rows(SD3 / '10_TARGETS/CF88_TARGETS.IDX')}
        cls.mapped = {p[2] for p in A.rows(SD3 / '10_TARGETS/CF88_TEXT_MAP.IDX')}
        cls.hdr = HDR3.read_text(encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def works(self, short):
        tid = S.Device.canonical(short)
        return sorted(r[6] for r in A.device_query_union(self.dev, tid)[0].get(REF, []))

    def button4(self, short):                       # mirror of lexV1AtualizarDisponibilidade (union of W flags of the query keys)
        tid = S.Device.canonical(short)
        return any(A.flag(self.flags.get(k, '------'), REF) for k in A.query_keys(tid))

    def check(self, short, expected):
        self.assertIn(S.Device.canonical(short), self.mapped, short)                 # a real ACTIVE_TARGET line
        self.assertEqual(self.works(short), sorted(expected), short)
        self.assertEqual(self.button4(short), bool(expected), short)                  # footer == list

    def test_new_links(self):
        self.check('CF88.37', ['Os Donos do Poder', 'Raízes do Brasil'])
        self.check('CF88.43', ['Formação Econômica do Brasil'])
        self.check('CF88.43.2.IV', ['Vidas Secas'])
        self.check('CF88.62', ['Suzerain'])
        self.check('CF88.201.I', ['Eu, Daniel Blake'])
        self.check('ADCT.68', ['Torto Arado'])
        self.check('CF88.7.XXXIII', ['Frostpunk'])
        self.check('CF88.86', ['Excelentíssimos'])
        self.check('CF88.52.I', ['O Processo'])
        self.check('CF88.58.3', ['Tropa de Elite 2: O Inimigo Agora É Outro'])
        self.check('CF88.134', ['Luta por Justiça'])
        self.check('CF88.144.5', ['Tropa de Elite'])
        self.check('CF88.144.7', ['A Escuta'])
        self.check('CF88.145.1', ['O Triunfo da Injustiça'])
        self.check('CF88.182', ['Citizen Jane: Battle for the City'])
        self.check('CF88.182.1', ['Cities: Skylines'])
        self.check('CF88.184', ['Cabra Marcado para Morrer'])
        self.check('CF88.192', ['A Grande Aposta'])
        self.check('CF88.215.1', ['Never Alone (Kisima Inŋitchuŋa)'])
        self.check('CF88.231', ['Martírio'])
        self.check('CF88.193', ['Capital no Século XXI', 'Desigualdade para Todos', 'O Triunfo da Injustiça'])   # unchanged

    def test_rejected_and_gaps(self):
        self.check('CF88.76', [])                                                     # Borgen rejected
        self.check('CF88.142', [])                                                    # Argentina, 1985 rejected
        self.check('CF88.196', [])                                                    # Sicko: approved but held (no work identity)
        self.check('CF88.206.I', [])                                                  # Pro Dia Nascer Feliz: held
        for art in ('CF88:ART.98', 'CF88:ART.202'):                                   # CONFIRMED_REFERENCE_GAP: no line of the article
            lines = [t for t in self.mapped if t == art or t.startswith(art + ':')]
            self.assertTrue(lines, art)
            for t in lines:
                self.assertEqual(A.device_query_union(self.dev, t)[0].get(REF, []), [], t)
                self.assertFalse(any(A.flag(self.flags.get(k, '------'), REF) for k in A.query_keys(t)), t)
        labels = {r[6] for t in self.mapped for r in self.dev.references(t)}
        self.assertNotIn('Borgen', labels)
        self.assertNotIn('Argentina, 1985', labels)

    def test_no_propagation_from_caput(self):
        for short in ('CF88.37.I', 'CF88.37.1', 'CF88.37.6', 'CF88.37.4', 'CF88.43.I', 'CF88.43.1', 'CF88.43.2', 'CF88.62.1', 'CF88.86.1',
                      'CF88.134.1', 'CF88.182.2', 'CF88.184.1', 'CF88.231.1', 'CF88.193.UNICO', 'CF88.201', 'CF88.201.II', 'CF88.7',
                      'CF88.7.XXXII', 'CF88.144', 'CF88.144.I', 'CF88.145', 'CF88.58', 'CF88.52', 'CF88.215', 'ADCT.67', 'ADCT.69'):
            tid = S.Device.canonical(short)
            if tid not in self.mapped:
                continue
            self.assertEqual(self.works(short), [], short)
            self.assertFalse(self.button4(short), short)

    def test_caput_rule_only_on_article_line(self):
        self.assertEqual(A.query_keys('CF88:ART.37'), ['CF88:ART.37', 'CF88:ART.37:CAPUT'])
        self.assertEqual(A.query_keys('ADCT:ART.68'), ['ADCT:ART.68'])
        self.assertNotIn('CF88:ART.37:CAPUT', self.mapped)                           # caput reached only through the ART.37 line
        self.assertEqual(self.flags['CF88:ART.37'][3], '-')
        self.assertEqual(self.flags['CF88:ART.37:CAPUT'][3], 'W')

    def test_rich_detail_for_every_new_link(self):
        for short, key, nota in (('CF88.62', 'CF88:ART.62:CAPUT|EXP-JOG-002', 74), ('ADCT.68', 'ADCT:ART.68|EXP-LIV-005', 92),
                                 ('CF88.7.XXXIII', 'CF88:ART.7:INC.XXXIII|EXP-JOG-003', 78), ('CF88.37', 'CF88:ART.37:CAPUT|EXP-LIV-002', 86),
                                 ('CF88.43.2.IV', 'CF88:ART.43:PAR.2:INC.IV|EXP2-LIV-040', 84)):
            m = re.search(r'\{"' + re.escape(key) + r'", "([^"]*)", "([^"]*)", (\d+), (-?\d+),\n   ("[^\n]*"),\n   ("[^\n]*"),\n   ("[^\n]*"), "([^"]*)", "([^"]*)"\}',
                          self.hdr)
            self.assertTrue(m, key)
            self.assertEqual(int(m.group(4)), nota, key)
            for g in (5, 6, 7):
                self.assertGreater(len(m.group(g)), 10, (key, g))                     # SOBRE / POR QUE / ALCANCE present
            self.assertIn('REFERENCE_EXPANSION_01', m.group(9))                      # discreet provenance
        for r in A.rows(SD3 / '20_REFERENCES/REF_PAYLOAD.IDX'):                      # every visible work row of RUN3 has a detail record
            if r[1] == 'WORK_REFERENCE' and r[2] == 'CURRENT_VISIBLE':
                self.assertIn(f'{{"{r[0]}|{r[5]}"', self.hdr, r[4])
        self.assertIn('\\x0aLimites: Mundo fict', self.hdr)                         # LIMITES = 2nd paragraph of ALCANCE (LF split by the UI)

    def test_baseline_untouched(self):
        # approved physical sketch = HEAD blob (the working copy may carry later candidate fixes, e.g. ARTICLE_SEARCH landing)
        import subprocess
        blob = subprocess.run(['git', 'cat-file', '-p', 'lex-device-v1-physical-approved-2026-10-01:firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'],
                              cwd=ROOT, capture_output=True).stdout
        self.assertEqual(hashlib.sha256(blob).hexdigest(), 'f06cdc14ad066e2575fe03552eb0090f39c77ab350d095de7bf26d41c86a81ed')
        # BATCH04+RUN3 physical baseline (r2): the sketch header IS the RUN3 header, byte-identical (promoted after approval)
        self.assertEqual(sha(FW / 'lex_ref_detail_data.h'), sha(HDR3))
        self.assertEqual(sha(HDR3), '2ca5820a170a3b08ecfa869685d319d65eee5bc94ddf0bfa5854282acce9710b')
        self.assertFalse(list(FW.rglob('*RUN3*')))                                    # only lex_ref_detail_data.h inside the sketch folder
        for rel in ('05_TEXT/CF88_RUNTIME.txt', '10_TARGETS/CF88_TEXT_MAP.IDX', '30_ENTENDA/ENTENDA_LOOKUP.IDX', '30_ENTENDA/ENTENDA_PAYLOAD.DAT'):
            self.assertEqual(sha(SD3 / rel), sha(SD1 / rel), rel)
        for n in ('REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
            self.assertEqual(sha(SD3 / '20_REFERENCES' / n), sha(RUN3 / n), n)
            self.assertEqual(sha(SD1 / '20_REFERENCES' / n), sha(ROOT / 'LEGAL_TARGET_ID/derived/export_test/run1' / n), n)
        self.assertIn('REFERENCE_ENGINE|cf-reference-engine-run3-candidate', (SD3 / '00_SYS/LEXV1.VER').read_text(encoding='utf-8'))


@unittest.skipUnless((SD1 / '05_TEXT/CF88_RUNTIME.txt').is_file(), 'baseline staging not built')
class Art193DiagnosticTest(unittest.TestCase):
    """PRE-FIX model (baseline firmware f06cdc14, search lands on the top row): after 'Buscar Art. 193' the centre row is in the paragrafo
    unico, not in the caput. Kept as the 'before' evidence; the fix is pinned by test_article_search_landing.py."""

    @classmethod
    def setUpClass(cls):
        import diagnose_art193_device_target as G
        cls.G = G
        cls.rd = G.Reader(SD1)

    def test_after_search_active_target_is_paragrafo_unico(self):
        pos = self.rd.search_article(193)
        self.assertEqual(pos, 349277)
        rows, act = self.rd.viewport(pos)
        self.assertEqual([r['target'] for r in rows[:3]], ['CF88:ART.193'] * 3)
        self.assertEqual(act, 'CF88:ART.193:PAR.UNICO')
        self.assertEqual(self.rd.layer4(act), (False, []))
        self.assertEqual(self.rd.layer4('CF88:ART.193')[0], True)

    def test_caput_centred_shows_button4(self):
        sc = {s['scroll']: s for s in self.G.scan(self.rd, 349277)}
        self.assertEqual(sorted(k for k, s in sc.items() if s['active_target'] == 'CF88:ART.193'), [-6, -5, -4])
        self.assertTrue(all(sc[k]['layer4'] and sc[k]['works'] == 3 for k in (-6, -5, -4)))

    def test_wrap_matches_reader_width(self):
        for a, b in self.rd.visual_lines(349277, 12):
            seg = self.rd.data[a:b].decode('utf-8').rstrip('\n').rstrip(' ')
            self.assertLessEqual(sum(self.rd.advance(ord(c)) for c in seg), self.G.WIDTH, seg)


if __name__ == '__main__':
    unittest.main()
