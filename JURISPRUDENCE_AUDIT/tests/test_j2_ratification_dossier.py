"""PÓS-NOTURNA B/C — the ratification dossier and the reconciliation are reproducible and never claim ratification."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]


class Dossier(unittest.TestCase):
    def test_up_to_date(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'render_j2_ratification_dossier.py'), '--check'], capture_output=True, text=True,
                           cwd=AUD.parent)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))

    def test_reconciliation(self):
        r = json.loads((AUD / 'J2_RECONCILIATION.json').read_text(encoding='utf-8'))
        self.assertEqual((r['PHYSICAL_RELATIONS']['relations'], r['PHYSICAL_RELATIONS']['targets']), (261, 160))
        self.assertEqual(r['UNRATIFIED_RELATIONS_PUBLISHED'], 0)
        a = r['AWAITING_RATIFICATION_RECOMMENDATIONS']
        self.assertEqual(sum(a['decisions_by_type'].values()), a['reviewed_recommendations'])
        self.assertEqual((r['RATIFIED_RECOMMENDATIONS'], a['recommendations'], r['UNRESOLVED_RECOMMENDATIONS']['count']), (54, 0, 1))
        h = r['RATIFIED_HOST_ONLY_RELATIONS']
        self.assertEqual(h['relations'], h['j2e_batch02'] + h['j2f_batches_03_09'])
        self.assertEqual(h['relations'], h['group_A_current_firmware'] + h['group_B_requires_generic_firmware'])

    def test_rows_follow_ratification_record(self):
        md = (AUD / 'J2_RATIFICATION_DOSSIER.md').read_text(encoding='utf-8')
        rows = [l for l in md.splitlines() if l.split('|')[1:2] and l.split('|')[1].strip().isdigit() and 'J0-BL-' in l]
        rat = {i['recommendation_id']: i for i in json.loads((AUD / 'J2_RATIFICATION_RECORD_03_09.json').read_text(encoding='utf-8'))['items']}
        self.assertEqual(len(rows), len(rat))
        for l in rows:
            rid = l.split('|')[2].strip()
            self.assertIn(f"| {rat[rid]['ratification_status']} |", l)
        self.assertEqual([r for r, i in rat.items() if not i['human_approved']], ['J0-BL-001'])
        self.assertNotIn('AWAITING_USER_RATIFICATION |', md)


if __name__ == '__main__':
    unittest.main()
