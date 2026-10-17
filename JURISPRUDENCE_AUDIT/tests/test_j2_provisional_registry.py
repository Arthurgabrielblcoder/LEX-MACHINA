"""PÓS-NOTURNA J — consolidated provisional registry: reproducible, every revalidation item present, no auto publish, gate works."""
import datetime as dt
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AUD))
import check_j2b_provisional as C  # noqa: E402


class Registry(unittest.TestCase):
    def test_up_to_date(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'build_j2_provisional_registry.py'), '--check'], capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))

    def test_items(self):
        d = json.loads((AUD / 'J2_PROVISIONAL_REGISTRY.json').read_text(encoding='utf-8'))
        self.assertIs(d['auto_publish'], False)
        ids = [x['source_id'] for x in d['items']]
        for pid in ('STF:ADI:7697', 'STF:ADI:5017', 'STF:ADPF:378', 'STF:RCL:84738'):
            self.assertIn(pid, ids)
        for x in d['items']:
            self.assertIn(x['state'], d['states'])
            for k in ('classe', 'processo', 'status_processual', 'last_verified_on', 'check', 'trigger', 'deadline'):
                self.assertTrue(x[k], (x['source_id'], k))

    def test_gate(self):
        reg = AUD / 'J2_PROVISIONAL_REGISTRY.json'
        self.assertTrue(all(r['result'] == 'PASS' for r in C.check(dt.date(2026, 10, 17), reg)))
        self.assertTrue(all(r['result'] == 'REVALIDATION_REQUIRED' for r in C.check(dt.date(2027, 6, 1), reg)))
        self.assertEqual(len(C.check(dt.date(2026, 10, 17))), 1)            # J2B registry untouched


if __name__ == '__main__':
    unittest.main()
