"""CC-J1 end-to-end SIMULATION on the multinorm firmware model + generic packager (no card, no flash):
abrir Código Civil -> artigo -> JURIS. -> lista -> precedente -> ficha -> BACK -> mesma lista -> artigo; depois a Constituição continua normal."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
sys.path[:0] = [str(ENG), str(ENG / 'firmware_multinorm')]
import generic_packager as P  # noqa: E402
import multinorm_sim as S  # noqa: E402

SIM = ENG / 'cc_j1_simulation'
CC_FILE = '/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'
CF_FILE = '/1- CONSTITUIÇÃO FEDERAL/cf.txt'


def pkg_from(root, card, extra):
    return S.Package((root / P.LAYER / 'JUR_LOOKUP.IDX').read_bytes(), (root / P.LAYER / 'JURISPRUDENCIA.IDX').read_bytes(), card | extra)


class E2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = P.card_fichas()
        new = {p.name for p in (SIM / 'SD' / P.CONTENT).glob('*.TXT')}
        cls.pkg = pkg_from(SIM / 'SD', cls.card, new)
        cls.dec = json.loads((ENG / 'CC_J1_DECISIONS.json').read_text(encoding='utf-8'))
        rels, prec = P.cf_fixture()
        cf_only = P.package(rels, prec, cls.card)
        cls.cf_pkg = S.Package(cf_only[P.LAYER + '/JUR_LOOKUP.IDX'], cf_only[P.LAYER + '/JURISPRUDENCIA.IDX'], cls.card)
        cls.cf_keys = [l.split('|')[:5] for l in cf_only[P.LAYER + '/JUR_LOOKUP.IDX'].decode('utf-8').split('\n')[1:] if l]

    def test_0_candidate_up_to_date_and_simulation_only(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(ENG / 'build_cc_j1_simulation.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))
        m = json.loads((SIM / 'CC_J1_SIMULATION_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual((m['status'], m['deployable'], m['cc_human_approved'], m['duplicate_query_keys']), ('SIMULATION_ONLY', False, False, 0))
        self.assertEqual(m['counts']['CF88'] + m['counts']['ADCT'], [311, 194, 4, 4])

    def test_1_cc_e2e(self):
        expected = {}
        for r in self.dec['simulation_relations']:
            expected.setdefault(P.query_key(r['target_id']), set()).add(P.JT.ficha(r['precedent']))
        self.assertEqual(sum(len(v) for v in expected.values()), len(self.dec['simulation_relations']) - 0)
        for key, fichas in expected.items():
            norma, art, par, inc, ali = key.split('|')
            self.assertEqual(norma, 'CC2002')
            artigo = S.carregar(self.pkg, CC_FILE, art, par, inc, ali)                         # abrir CC, localizar artigo, JURIS.
            self.assertEqual(artigo['branch'], 'MULTINORMA')
            self.assertEqual({x['arquivo'] for x in artigo['relations']}, fichas)              # lista correta
            for i in range(len(artigo['relations'])):
                o = S.open_and_back(self.pkg, artigo, i)                                      # selecionar precedente -> ficha
                self.assertTrue(o['opened'], (key, i))
                self.assertNotIn('OUTRO', o['title'])
                back = S.carregar(self.pkg, CC_FILE, art, par, inc, ali)                      # BACK -> mesma lista
                self.assertEqual(back['relations'], artigo['relations'])
            self.assertEqual(S.carregar(self.pkg, CC_FILE, art, par, inc, ali), artigo)       # voltar ao artigo: mesmo estado

    def test_2_sumula_403_one_ficha_two_targets(self):
        a = S.carregar(self.pkg, CC_FILE, '186')
        b = S.carregar(self.pkg, CC_FILE, '927')
        for st in (a, b):
            labels = [x['label'] for x in st['relations']]
            self.assertIn('Súmula 403 STJ', labels)
            self.assertIn('ADI 6792/7055', labels)
        f = {x['arquivo'] for x in a['relations'] if x['label'] == 'Súmula 403 STJ'} | {x['arquivo'] for x in b['relations'] if x['label'] == 'Súmula 403 STJ'}
        self.assertEqual(f, {'STJ_SUMULA_403.TXT'})
        pu = S.carregar(self.pkg, CC_FILE, '927', par='unico')
        self.assertEqual([x['label'] for x in pu['relations']], ['RG TEMA 932'])
        cf = S.carregar(self.pkg, CF_FILE, '7', inc='XXVIII')
        self.assertIn(pu['relations'][0]['arquivo'], {x['arquivo'] for x in cf['relations']})  # same physical ficha serves CF and CC

    def test_3_cf_after_cc_regression(self):
        S.carregar(self.pkg, CC_FILE, '20')
        for norma, art, par, inc, ali in self.cf_keys:
            if norma != 'CF88':
                continue
            after = S.carregar(self.pkg, CF_FILE, art, par, inc, ali)
            ref = S.carregar(self.cf_pkg, CF_FILE, art, par, inc, ali)
            self.assertEqual((after['branch'], after['relations']), ('CF', ref['relations']), (art, par, inc, ali))


if __name__ == '__main__':
    unittest.main()
