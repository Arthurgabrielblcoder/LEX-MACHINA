"""J1.3 — light checks: decisions generator up to date, counts reconcile, nothing published changed."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
RUN6 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run6_juris_j1_candidate'


class J13(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads((AUD / 'J1_3_DECISIONS.json').read_text(encoding='utf-8'))

    def test_generator_up_to_date(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'build_j1_3_external_review.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))

    def test_decisions_and_reconciliation(self):
        s, r = self.d['summary'], self.d['reconciliation']
        self.assertEqual((s['REALLOCATE_RECOMMENDED'], s['UNRESOLVED_EXTERNAL'], s['REDUNDANT_DECISION']), (4, 0, 'KEEP_BOTH'))
        self.assertEqual((r['original'], r['removed_in_j1_1'], r['current_device'], r['PROPOSED_FINAL_ORIGINAL_SET_RELATIONS']), (277, 20, 257, 253))
        self.assertEqual(r['HUMAN_REVIEWED_SIGNAL_RELATIONS'] + r['NO_SIGNAL_STRUCTURAL_CONTROL_RELATIONS'], 277)
        self.assertEqual(self.d['ORIGINAL_277_REVIEW_COMPLETE'], 'YES')
        for x in self.d['decisions']:
            self.assertTrue(x['sources'] and x['main_source'] in self.d['sources'])
        for s_ in self.d['sources'].values():
            self.assertEqual(s_['tier'], 'A')
            self.assertTrue(s_.get('dom_text_sha256') or s_.get('snapshot_sha256'))

    def test_nothing_published_changed(self):
        for line in (RUN6 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
            h, name = line.split('  ', 1)
            self.assertEqual(hashlib.sha256((RUN6 / name).read_bytes()).hexdigest(), h, name)
        r = subprocess.run(['git', 'diff', '--quiet', 'd873037', '7b644ab', '--', 'LEGAL_TARGET_ID', 'JURISPRUDENCE_AUDIT/J1_1_CANDIDATE_HOST_ONLY',
                            'CORRELATA_COVERAGE_AUDIT', 'REFERENCE_COVERAGE_AUDIT', 'ENTENDA_ENGINE', 'firmware', 'DEVICE_INTEGRATION'], cwd=ROOT)
        self.assertEqual(r.returncode, 0)


if __name__ == '__main__':
    unittest.main()
