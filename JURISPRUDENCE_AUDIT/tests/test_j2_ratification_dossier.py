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
        self.assertEqual(sum(a['decisions_by_type'].values()), a['recommendations'])

    def test_no_row_claims_ratification(self):
        md = (AUD / 'J2_RATIFICATION_DOSSIER.md').read_text(encoding='utf-8')
        rows = [l for l in md.splitlines() if l.startswith('| ') and 'J0-BL-' in l]
        self.assertTrue(rows)
        self.assertTrue(all('| AWAITING_USER_RATIFICATION |' in l for l in rows))
        self.assertNotIn('| RATIFIED |', md)


if __name__ == '__main__':
    unittest.main()
