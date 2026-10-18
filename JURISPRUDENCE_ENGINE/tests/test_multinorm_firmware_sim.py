"""Multinorm firmware prototype — host simulation (no card, no flash). CF behaviour must be identical to the J2I firmware on every CF lookup;
ADCT keeps its previous path; Código Civil (SIMULATION_ONLY package): target -> list -> ficha -> BACK."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
sys.path[:0] = [str(ENG / 'firmware_multinorm'), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import multinorm_sim as S  # noqa: E402
import build_multinorm_prototype as P  # noqa: E402
import build_j2_batch as G  # noqa: E402

J2I = ROOT / 'JURISPRUDENCE_AUDIT/J2H_CANDIDATE_B_OVER_A/candidate/SD/99_JURISPRUDENCIA_V2'
SIM = ENG / 'pilot_cc/SIM_CANDIDATE_CC'
CARD = ROOT / 'JURISPRUDENCE_AUDIT/J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
CC_FILE = '/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'
CF_FILE = '/1- CONSTITUIÇÃO FEDERAL/cf.txt'


def card_fichas():
    return {k.split('/')[-1] for k in json.loads(CARD.read_text(encoding='utf-8'))['entries'] if k.startswith('99_JURISPRUDENCIA_V2/03_CONTEUDO/')}


def pkg(base, extra=()):
    return S.Package((base / '05_INDICES_ESP32/JUR_LOOKUP.IDX').read_bytes(), (base / '05_INDICES_ESP32/JURISPRUDENCIA.IDX').read_bytes(),
                     card_fichas() | set(extra))


class MultinormSim(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.j2i = pkg(J2I)
        cls.sim = pkg(SIM, [p.name for p in (SIM / '03_CONTEUDO').glob('*.TXT')])

    def test_1_cf_identical_to_j2i_firmware(self):
        """Every CF lookup of the J2I card: multinorm firmware == J2I firmware (lists, labels, fichas), on both packages."""
        n = 0
        for norma, art, par, inc, ali, _, _ in self.j2i.lookups:
            self.assertEqual(norma, 'CF88')
            for p in (self.j2i, self.sim):
                new = S.carregar(p, CF_FILE, art, par, inc, ali)
                old = S.carregar(self.j2i, CF_FILE, art, par, inc, ali, legacy=True)
                self.assertEqual((new['branch'], new['relations']), ('CF', old['relations']), (art, par, inc, ali))
            n += len(old['relations'])
        keys = {l[:5] for l in self.j2i.lookups}
        # 237 lines, 355 records; repeated keys (groups appended by J2G/J2H) resolve to the FIRST group in both firmwares (pre-existing;
        # on the CF runtime the device shows jurisprudence through the LEXV1 layer, not this legacy path)
        self.assertEqual((len(self.j2i.lookups), sum(l[6] for l in self.j2i.lookups), len(keys)), (237, 355, 221))
        self.assertEqual((len(G.j2i_baseline()), len({r[0] for r in G.j2i_baseline()})), (315, 198))    # CF315 / CF198 unchanged

    def test_2_adct_keeps_previous_path(self):
        st = S.carregar(self.sim, S.CF_RUNTIME, '107-A', in_adct=True)
        self.assertEqual((st['norma'], st['branch'], st['relations']), ('ADCT', 'PREVIOUS_FLOW', []))
        self.assertEqual(S.carregar(self.sim, S.CF_RUNTIME, '107-A', in_adct=True, legacy=True)['relations'], [])
        self.assertTrue([r for r in G.j2i_baseline() if r[0].startswith('ADCT:')])          # ADCT juris still served by the LEXV1 layer

    def test_3_codigo_civil_list_ficha_back(self):
        st = S.carregar(self.sim, CC_FILE, '927', par='unico')
        self.assertEqual((st['norma'], st['branch'], [r['label'] for r in st['relations']]), ('CC2002', 'MULTINORMA', ['RG TEMA 932']))
        self.assertEqual(st['relations'][0]['referencia'], 'ART. 927, PAR. UNICO')
        st = S.carregar(self.sim, CC_FILE, '1790', inc='I')                  # falls back to the article (no inciso key)
        self.assertEqual(([r['label'] for r in st['relations']], st['used']), (['RG TEMA 498', 'RG TEMA 809'], ('', '', '')))
        for art in ('20', '21', '1790', '1829'):
            st = S.carregar(self.sim, CC_FILE, art)
            for i in range(len(st['relations'])):
                o = S.open_and_back(self.sim, st, i)
                self.assertTrue(o['opened'], (art, i))
                self.assertNotIn('OUTRO', o['title'])
                back = S.carregar(self.sim, CC_FILE, art)                     # BACK re-resolves from the saved origin
                self.assertEqual(back['relations'], st['relations'])
        self.assertEqual(S.carregar(self.j2i, CC_FILE, '927', par='unico')['branch'], 'PREVIOUS_FLOW')   # J2I card: no CC rows

    def test_4_alternation_cf_cc_cf(self):
        a = S.carregar(self.sim, CF_FILE, '7', inc='XXVIII')
        b = S.carregar(self.sim, CC_FILE, '20')
        c = S.carregar(self.sim, CF_FILE, '7', inc='XXVIII')
        self.assertEqual(a, c)
        self.assertEqual((b['branch'], [r['label'] for r in b['relations']]), ('MULTINORMA', ['ADI 4815']))
        self.assertTrue(all(not r['referencia'].startswith('CF ') for r in b['relations']))

    def test_5_norm_without_jurisprudence(self):
        st = S.carregar(self.sim, '/3-CÓDIGO PROCESSO CIVIL/codigo_processo_civil.txt', '1')
        self.assertEqual((st['norma'], st['branch'], st['relations']), ('CPC2015', 'PREVIOUS_FLOW', []))
        st = S.carregar(self.sim, '/21- DIREITO ADMINISTRATIVO/lei_8429_1992_improbidade.txt', '1')
        self.assertEqual((st['norma'], st['branch']), ('LIA1992', 'PREVIOUS_FLOW'))

    def test_6_invalid_namespace_fails_closed(self):
        self.assertEqual(S.norma_juris_atual('/21- DIREITO ADMINISTRATIVO/arquivo_desconhecido.txt'), '')
        self.assertEqual(S.norma_juris_atual('/99_PASTA_INEXISTENTE/x.txt'), '')
        self.assertEqual(S.carregar(self.sim, '/99_PASTA_INEXISTENTE/x.txt', '1')['branch'], 'PREVIOUS_FLOW')
        bad = S.Package(b'#H\nXX9999|1||||0|1\n', b'#H\nSTF:ADI:1:XX9999:1:-:-:-|adi|STF|1|x|ADI 1|STF:ADI:1|u\n', set())
        self.assertFalse(bad.has_norm('CC2002'))
        old_width = S.Package(b'#H\nHEDIONDOS1990|1||||0|1\n', b'#H\nr|adi|STF|1|x|t|STF:ADI:1|u\n', set(), norma_field=8)
        self.assertFalse(old_width.has_norm('HEDIONDOS1990'))                 # the J2I char[8] field would truncate long catalog ids
        self.assertTrue(S.Package(b'#H\nHEDIONDOS1990|1||||0|1\n', b'#H\nr|adi|STF|1|x|t|STF:ADI:1|u\n', set()).has_norm('HEDIONDOS1990'))
        with self.assertRaises(ValueError):
            S.Package(b'#H\nCC2002|1||||5|1\n', b'#H\nabc\n', set())          # misaligned offset: whole cache refused (fail closed)

    def test_long_catalog_ids_not_truncated(self):
        cases = {'/16- LEI DE CRIMES HEDIONDOS/lei.txt': 'HEDIONDOS1990',
                 '/39- MERCADO FINANCEIRO SEGUROS E CAPITAIS/lei_11795_2008_consorcios.txt': 'CONSORCIO2008',
                 '/43- FAMILIA E SUCESSOES ESPECIAL/lei_12318_2010_alienacao_parental.txt': 'ALIENPAR2010'}
        for path, nid in cases.items():
            self.assertEqual(S.norma_juris_atual(path), nid)
            self.assertGreater(len(nid), 7)
            lookup, rec = f'#H\n{nid}|1||||3|1\n'.encode(), b'#H\nSTF:ADI:1:x|adi|STF|1|x|ADI 1|STF:ADI:1|u\n'
            self.assertTrue(S.Package(lookup, rec, {'STF_ADI_1.TXT'}).has_norm(nid))                      # char[16]: exact
            self.assertFalse(S.Package(lookup, rec, set(), norma_field=8).has_norm(nid))                 # J2I char[8]: truncated
            self.assertEqual(S.carregar(S.Package(lookup, rec, {'STF_ADI_1.TXT'}), path, '1')['branch'], 'MULTINORMA')
        longest = max((i for *_, i in P.catalog_table()), key=len)
        self.assertLessEqual(len(longest), 15)

    def test_catalog_table_and_patch(self):
        rows = P.catalog_table()
        self.assertEqual(len(rows), 71)
        self.assertFalse([r for r in rows if r[2] == 'CF88'])
        self.assertTrue(all(len(i) <= 15 for *_, i in rows))
        base = P.types_module().patched_text()
        multi = P.multinorm_text(base)
        self.assertIn('char norma[16];', multi)
        self.assertIn('06_NORMALIZADO/JUR_LOOKUP.IDX', multi)                          # normalized layer preferred when present
        self.assertEqual(multi.count('normaJurisConsulta'), base.count('normaJurisConsulta') + 5)
        cf_branch = re.search(r'if\(arquivoAtualPertenceACF\(\)\)\{.*?return menuRelacoesAtivo;\r\n  \}', base, re.S).group(0)
        self.assertIn(cf_branch, multi)                                       # CF branch byte-identical
        r = subprocess.run([sys.executable, '-I', '-B', str(ENG / 'firmware_multinorm/build_cc_sim_candidate.py'), '--check'],
                           capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))
        m = json.loads((SIM / 'SIM_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual((m['status'], m['human_approved'], m['deployable']), ('SIMULATION_ONLY', False, False))
        self.assertTrue(SIM.joinpath('05_INDICES_ESP32/JURISPRUDENCIA.IDX').read_bytes().startswith((J2I / '05_INDICES_ESP32/JURISPRUDENCIA.IDX').read_bytes()))


if __name__ == '__main__':
    unittest.main()
