"""CC-J2 final dossier: pinned batch unchanged, 30 items, group rules, projections from the physical baseline, nothing ratified."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent


class CCJ2FinalDossier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = json.loads((ENG / 'CC_J2_RATIFICATION_DOSSIER_FINAL.json').read_text(encoding='utf-8'))

    def test_up_to_date_and_pins(self):
        for script in ('build_cc_j2_final_dossier.py', 'build_cc_j2.py'):     # pins checked inside; preliminary batch still reproducible
            r = subprocess.run([sys.executable, '-B', str(ENG / script), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), script + r.stderr[-1500:])

    def test_totals_and_rules(self):
        o, t = self.o, self.o['totals']
        self.assertEqual((t['TOTAL'], t['GREEN_FINAL'], t['YELLOW_FINAL'], t['RED_FINAL']), (30, 9, 10, 11))
        self.assertEqual((o['HUMAN_APPROVED_NEW'], o['SD_CHANGED'], o['FIRMWARE_CHANGED'], o['scale']['NEW_CORE_ENGINE_CODE_THIS_DOSSIER']),
                         (0, 'NO', 'NO', 0))
        for it in o['items']:
            self.assertEqual((it['status'], it['human_approved']), ('AWAITING_USER_RATIFICATION', False))
            if it['group_final'] == 'GREEN':
                self.assertTrue(all(it['green_checks'].values()), it['id'])
                self.assertEqual(it['state'], 'SAFE_FOR_BLOCK_RATIFICATION')
            if it['group_final'] == 'RED':
                self.assertEqual(it['targets_final'], [])
                self.assertTrue(it['reopen'])
            if it['group_final'] == 'YELLOW':
                self.assertEqual(set(it['alternatives']), {'A', 'B', 'C', 'D'})
        ids = {it['precedent']: it for it in o['items']}
        self.assertEqual(ids['STJ:SUMULA:642']['targets_final'], ['CC2002:ART.943'])            # no nonexistent "943, I"
        self.assertIn('ART:00943 INC:00001', ids['STJ:SUMULA:642']['source_anomaly'])
        self.assertEqual(ids['STF:RG:1236']['group_final'], 'RED')                              # illustrative only
        self.assertEqual(ids['STJ:REPETITIVO:1130']['decision_final'], 'PROMOTE_PROVISIONAL_RECOMMENDED')
        self.assertEqual(ids['STJ:REPETITIVO:381']['relation'], 'EXCLUSION_CONTEXT')

    def test_projection(self):
        p = self.o['projection']
        self.assertEqual(p['CC_PHYSICAL_BASELINE'], '29/24')
        self.assertEqual((p['PROJECTED_GREEN_RELATIONS'], p['PROJECTED_GREEN_TARGETS']), (38, 32))
        self.assertEqual((p['PROJECTED_FULL_RELATIONS'], p['PROJECTED_FULL_TARGETS']), (49, 39))


if __name__ == '__main__':
    unittest.main()
