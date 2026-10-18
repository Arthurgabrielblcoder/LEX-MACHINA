"""CC-J1 ratification dossier: 30 proposals, one group each, GREEN rules, nothing ratified or changed."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class Dossier(unittest.TestCase):
    def test_up_to_date(self):
        for s in ('build_cc_j1_dossier.py', 'build_cc_j1.py', 'build_cc_j1_simulation.py'):
            r = subprocess.run([sys.executable, '-I', '-B', str(ENG / s), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), s)        # CC_J1 decisions / simulation unchanged

    def test_groups(self):
        d = load(ENG / 'CC_J1_RATIFICATION_DOSSIER.json')
        items = d['items']
        self.assertEqual(len(items), 30)
        self.assertEqual(len({i['id'] for i in items}), 30)
        self.assertTrue(all(i['group'] in ('GREEN', 'YELLOW', 'RED') for i in items))
        c = d['counts']
        self.assertEqual(c['GREEN'] + c['YELLOW'] + c['RED'], 30)
        for i in items:
            self.assertEqual((i['status'], i['human_approved']), ('AWAITING_USER_RATIFICATION', False))
            if i['group'] == 'GREEN':
                self.assertEqual(i['temporal'], 'CURRENT')
                self.assertFalse(i['proposed_decision'].startswith(('UNRESOLVED', 'REJECT', 'REALLOCATE')))
                self.assertTrue(all(v == 'VIGENTE' for v in i['evidence']['target_validity'].values()))
            if i['temporal'] != 'CURRENT' or i['proposed_decision'].startswith(('REJECT', 'UNRESOLVED')):
                self.assertNotEqual(i['group'], 'GREEN')
            if i['proposed_decision'].startswith(('REJECT', 'UNRESOLVED')):
                self.assertEqual(i['group'], 'RED')
        reds = {i['id'] for i in items if i['group'] == 'RED'}
        prop = d['RATIFY_GREEN_SET_PROPOSAL']
        self.assertFalse(reds & set(prop['ids']))
        self.assertEqual(set(prop['ids']), {i['id'] for i in items if i['group'] == 'GREEN'})
        self.assertIs(prop['executed'], False)
        self.assertEqual((d['HUMAN_APPROVED_NEW'], d['CC_RELATIONS_PUBLISHED'], d['SD_CHANGED'], d['FIRMWARE_CHANGED']), (0, 0, 'NO', 'NO'))

    def test_insurance_and_403_never_green(self):
        d = load(ENG / 'CC_J1_RATIFICATION_DOSSIER.json')
        g = {i['label']: i['group'] for i in d['items']}
        for lab in ('Súmula 405 STJ', 'Súmula 609 STJ', 'Súmula 403 STJ'):
            self.assertNotEqual(g[lab], 'GREEN', lab)
        self.assertEqual(d['decisions_sha256_lf'], hashlib.sha256((ENG / 'CC_J1_DECISIONS.json').read_bytes().replace(b'\r\n', b'\n')).hexdigest())


if __name__ == '__main__':
    unittest.main()
