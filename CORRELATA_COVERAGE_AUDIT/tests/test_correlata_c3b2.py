"""C3B.2 — residual C3B.1 physical findings (LC 63 route, LC 109 at art. 202 caput): data-chain audit, no regression, package."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AUDIT / 'C3A/tools'))
import build_c3b1_reports as B  # noqa: E402
import build_c3b2_reports as B2  # noqa: E402

P, O, R4 = B.P, B.O, B.R4
C3B1 = B.card('C3B1')
DOC = json.loads(B2.OUT_DUP.read_text(encoding='utf-8'))
S = DOC['summary']


def editorial(target, dest):
    ed = B2.editorial_sources()
    return ed.get((target, dest)) or next(v for k, v in ed.items() if k[0] == target and k[1].startswith('EXT:'))


class SimulatorMatchesHardware(unittest.TestCase):
    """The simulator reproduces what Arthur observed with C3B.1 installed."""

    def test_c3b1_observed_state(self):
        for t in ('CF88:ART.158:PAR.1:INC.I', 'CF88:ART.161:INC.I'):
            lc63 = [c for c in C3B1.open_correlatas(t) if c['row'][6] == 'EXT_LC63_1990']
            self.assertEqual([c['articles'] for c in lc63], [['3']])                  # opens at art. 3 (tests 3 and 5)
        cap = [c['row'][6] for c in C3B1.open_correlatas('CF88:ART.202')]
        self.assertIn('EXT_LC109_2001', cap)                                          # test 7: LC 109 shown at the article/caput
        self.assertEqual([c['articles'] for c in C3B1.open_correlatas('CF88:ART.202:PAR.1') if c['row'][6] == 'EXT_LC109_2001'], [['3']])
        self.assertEqual([c['articles'] for c in C3B1.open_correlatas('CF88:ART.202:PAR.5')], [['26']])


class LC63(unittest.TestCase):
    def test_destination_is_the_recorded_decision(self):
        self.assertEqual(S['LC63_DESTINATION_ROOT_CAUSE'], 'CONFIRMED')
        for t, dest in (('CF88:ART.158:PAR.1:INC.I', 'EXT_LC63_1990'), ('CF88:ART.161:INC.I', 'EXT_LC63_1990')):
            ed = editorial(t, dest)
            self.assertIn('3', ed['route'])                                           # the human decision fixes art. 3
            dev = [c for c in C3B1.open_correlatas(t) if c['row'][6] == dest][0]
            self.assertEqual(dev['articles'], ['3'])
            self.assertIn(dev['offsets']['3'], B.headings()[(dest, '3')])            # offset = heading of art. 3


class Art202(unittest.TestCase):
    def test_caput_and_par1_are_independent_decisions(self):
        self.assertEqual((S['ART202_CAPUT_LC109_ROOT_CAUSE'], S['ART202_CAPUT_LC109_SHOULD_EXIST']), ('CONFIRMED', 'YES'))
        view = R4.load(R4.OUT / 'legal_view/CF88_CORRELATA_LEGAL_VIEW.json')['entries']
        cap = next(e for e in view if e['kind'] == 'LEGACY' and e['target_id'] == 'CF88:ART.202:CAPUT')
        par = next(e for e in view if e['kind'] == 'ADDITION' and e['target_id'] == 'CF88:ART.202:PAR.1')
        self.assertEqual((cap['legacy_decision'], cap['device_state']), ('KEEP', 'DEVICE_READY'))
        self.assertEqual(par['supersedes'], [])
        self.assertFalse(set(par['decision_ids']) & {cap['decision_id']})
        self.assertEqual(json.loads((AUDIT / 'CF88_CORRELATA_C1B_HIGH_CONSOLIDATED.json').read_text(encoding='utf-8'))['candidates'][[
            r['candidate_id'] for r in json.loads((AUDIT / 'CF88_CORRELATA_C1B_HIGH_CONSOLIDATED.json').read_text(encoding='utf-8'))['candidates']
        ].index(par['decision_ids'][0])]['target_original'], 'CF88:ART.202:PAR.1')        # not a retarget from the caput


class GlobalAudits(unittest.TestCase):
    def test_route_modes_24(self):
        self.assertEqual(len(DOC['route_modes']), 24)
        self.assertEqual(S['DEVICE_READY_EDITORIAL_MODE'], '24/24')
        for m in DOC['route_modes']:
            self.assertEqual(m['editorial_mode'], m['device_mode'], m['target_id'])
            self.assertEqual(m['editorial_articles'], m['device_articles'], m['target_id'])

    def test_target_duplication(self):
        self.assertEqual(S['TARGET_DUPLICATION_AUDIT'], 'PASS')
        for d in DOC['duplication_groups']:
            self.assertEqual(d['verdict'], 'INDEPENDENT_HUMAN_DECISIONS')
            self.assertFalse(d['superseded_still_published'])


class NoRegression(unittest.TestCase):
    def test_c3b1_fixes_kept(self):
        a = json.loads(B.OUT_AUDIT.read_text(encoding='utf-8'))
        self.assertEqual((a['CORRELATA_REFERENCE_ID_RESOLUTION'], a['DEVICE_READY_ROUTE_SIMULATION']), ('1_TO_1', '24/24'))
        for t, want in (('CF88:ART.158:PAR.1:INC.I', True), ('CF88:ART.158:PAR.1:INC.II', False), ('CF88:ART.214', True),
                        ('CF88:ART.239:PAR.3', True), ('CF88:ART.37:PAR.3:INC.III', False), ('CF88:ART.37:INC.II', False)):
            self.assertEqual(C3B1.available(t), want, t)
        for t in ('I', 'II', 'III', 'IV', 'V', 'VI'):
            self.assertFalse(C3B1.available(f'CF88:ART.214:INC.{t}'))
        tf = json.loads((P.AUDIT / 'C3B1_PHYSICAL_TEST_PACKAGE/C3B1_FILE_DIFF.json').read_text(encoding='utf-8'))['isolation']['targets_flags']
        self.assertEqual(tf['verdict'], 'CORRELATA_FLAG_CHANGES_ONLY')


class Package(unittest.TestCase):
    def test_c3b2_package_reproducible_and_equal_device_bytes(self):
        self.assertTrue(S['C3B2_DEVICE_BYTES_EQUAL_C3B1'])
        self.assertEqual(S['RELATIONS_CORRECTED'], 0)
        trees = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as t:
                trees.append(P.build(Path(t) / 'pkg', 'C3B2'))
        self.assertEqual(trees[0], trees[1])
        self.assertEqual(trees[0], P.tree(P.PROFILE_OUT['C3B2']))
        plan = (P.PROFILE_OUT['C3B2'] / 'C3B2_PHYSICAL_TEST_PLAN.md').read_text(encoding='utf-8')
        self.assertIn('NO art. 3º', plan)
        self.assertIn('CONTINUA', plan)

    def test_reports_deterministic(self):
        out = B2.build()
        self.assertEqual(out, B2.build())
        for p, b in zip((B2.OUT_PHYS, B2.OUT_ROOT, B2.OUT_LC63, B2.OUT_202, B2.OUT_DUP), out):
            self.assertEqual(p.read_bytes().replace(b'\r\n', b'\n'), b, p.name)


if __name__ == '__main__':
    unittest.main()
