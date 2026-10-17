"""J2A BATCH01 — light checks: deterministic selection of 10 HIGH candidates, complete decisions, current 256 and frozen inputs untouched."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
sys.path.insert(0, str(AUD))
import build_j2a_batch01 as B  # noqa: E402

DEC = AUD / 'J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json'
FIELDS = ('recommendation_id', 'precedent', 'court', 'klass', 'number', 'judgment', 'subject', 'namespace', 'NAMESPACE_CHECK', 'target_check',
          'recommended_target', 'decision', 'confidence', 'sources', 'reason', 'status')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class J2A(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(DEC.read_text(encoding='utf-8'))

    def test_generator_up_to_date(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'build_j2a_batch01.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))

    def test_selection_deterministic_3x(self):
        runs = [B.build(selection_only=True) for _ in range(3)]
        self.assertEqual(len(set(runs)), 1)
        self.assertEqual(json.loads(runs[0])['selected'], self.d['selected'])

    def test_exactly_10_high_unique_pending(self):
        q = {x['recommendation_id']: x for x in self.d['high_queue']}
        self.assertEqual(len(self.d['selected']), 10)
        self.assertEqual(len(set(self.d['selected'])), 10)
        self.assertTrue(set(self.d['selected']) <= set(q))
        self.assertEqual(sorted(q[r]['rank'] for r in self.d['selected']), list(range(1, 11)))
        items, pending, _ = B.reconstruct()
        cat = {b['recommendation_id']: b['category'] for b in items}
        self.assertTrue(all(cat[r] == 'NEEDS_EXTERNAL_INGESTION' for r in self.d['selected']))   # none EXCLUDED / ALREADY_LINKED
        rc = self.d['reconstruction']
        self.assertEqual((rc['BACKLOG_PENDING'], rc['BACKLOG_TARGETS'], rc['HIGH_TOTAL']), (148, 110, 42))
        self.assertEqual(self.d['HIGH_REMAINING_AFTER_BATCH'], 32)

    def test_decisions_complete(self):
        ds = self.d['decisions']
        self.assertEqual([x['recommendation_id'] for x in ds], self.d['selected'])
        for x in ds:
            for f in FIELDS:
                self.assertIn(f, x, (x['recommendation_id'], f))
            self.assertEqual(x['NAMESPACE_CHECK'], 'PASS')
            self.assertTrue(x['OFFICIAL_SOURCE_REVIEWED'] and x['sources'])
            self.assertEqual(x['status'], 'AWAITING_USER_RATIFICATION')
            for s in x['sources']:
                src = self.d['sources'][s]
                self.assertEqual(src['tier'], 'A')
                self.assertTrue(src.get('dom_text_sha256') or src.get('snapshot_sha256'), s)
            if x['decision'] == 'PROMOTE_RECOMMENDED':
                self.assertEqual(x['target_check'], 'PASS')
                self.assertTrue(x['recommended_target'].startswith('CF88:'))
        self.assertEqual(sum(self.d['totals'].values()), 10)
        self.assertEqual(self.d['status'], 'AWAITING_USER_RATIFICATION')

    def test_current_256_and_inputs_unchanged(self):
        self.assertEqual(sha(B.CURRENT), B.CURRENT_SHA)                  # installed REF_PAYLOAD (J1.5)
        run7 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run7_juris_j1_4_candidate'
        for line in (run7 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
            h, name = line.split('  ', 1)
            self.assertEqual(sha(run7 / name), h, name)
        for rel, h in self.d['inputs'].items():                          # J0 backlog and ENTENDA recommendations (frozen)
            self.assertEqual(B.sha_lf(ROOT / rel), h, rel)
        m = json.loads((AUD / 'J1_4_CANDIDATE_HOST_ONLY/J1_4_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
        for d in m['file_diff']:
            self.assertEqual(sha(AUD / 'J1_4_CANDIDATE_HOST_ONLY/candidate/SD' / d['path'].lstrip('/')), d['after_sha256'])


if __name__ == '__main__':
    unittest.main()
