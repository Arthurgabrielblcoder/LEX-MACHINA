"""J2D BATCH02 — deterministic selection over the 261 baseline, Batch01 not re-entered, complete decisions, baseline untouched."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
sys.path.insert(0, str(AUD))
import build_j2d_batch02 as D  # noqa: E402

DEC = AUD / 'J2_HIGH_BACKLOG/J2D_BATCH02_DECISIONS.json'
FIELDS = ('recommendation_id', 'precedent', 'court', 'klass', 'number', 'process', 'judgment', 'publication', 'situation', 'namespace',
          'namespace_evidence', 'NAMESPACE_CHECK', 'temporal_version', 'TEMPORAL_CHECK', 'target_check', 'recommended_target', 'decision',
          'confidence', 'sources', 'reason', 'status', 'NEW_JURIS_TYPE_REQUIRES_DESIGN')
RESOLVED = {'J0-BL-069', 'J0-BL-074', 'J0-BL-080', 'J0-BL-081', 'J0-BL-082', 'J0-BL-084', 'J0-BL-135', 'J0-BL-136', 'J0-BL-137', 'J0-BL-138'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class J2D(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(DEC.read_text(encoding='utf-8'))

    def test_generator_up_to_date(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'build_j2d_batch02.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))

    def test_selection_deterministic_3x(self):
        runs = [D.build(selection_only=True) for _ in range(3)]
        self.assertEqual(len(set(runs)), 1)
        self.assertEqual(json.loads(runs[0])['selected'], self.d['selected'])

    def test_backlog_rebuilt_and_batch01_not_reentered(self):
        rc = self.d['reconstruction']
        self.assertEqual(set(rc['RESOLVED_BY_BATCH01']), RESOLVED)
        self.assertEqual(rc['RESOLVED_BATCH01_REENTERED'], 0)
        self.assertEqual(sorted(rc['COVERED_BY_BATCH01']), ['J0-BL-083', 'J0-BL-085'])
        self.assertEqual((rc['BACKLOG_PENDING_CURRENT'], rc['HIGH_CURRENT'], rc['MEDIUM_CURRENT'], rc['LOW_CURRENT']), (136, 31, 79, 26))
        self.assertEqual(rc['left_high'], ['J0-BL-075'])
        _, pending, _, covered, _ = D.reconstruct()
        ids = {b['recommendation_id'] for b in pending}
        self.assertFalse(ids & RESOLVED or ids & set(covered))

    def test_exactly_10_unique_high(self):
        q = {x['recommendation_id']: x for x in self.d['high_queue']}
        sel = self.d['selected']
        self.assertEqual((len(sel), len(set(sel))), (10, 10))
        self.assertTrue(set(sel) <= set(q) and not set(sel) & RESOLVED)
        self.assertEqual(sorted(q[r]['rank'] for r in sel), list(range(1, 11)))
        self.assertEqual(self.d['HIGH_REMAINING_AFTER_BATCH'], 21)

    def test_decisions_complete(self):
        ds = self.d['decisions']
        self.assertEqual([x['recommendation_id'] for x in ds], self.d['selected'])
        for x in ds:
            for f in FIELDS:
                self.assertIn(f, x, (x['recommendation_id'], f))
            self.assertIn(x['NAMESPACE_CHECK'], ('PASS', 'FAIL'))
            self.assertIn(x['temporal_version'], ('CURRENT', 'HISTORICAL', 'MIXED', 'NOT_APPLICABLE'))
            self.assertEqual(x['status'], 'AWAITING_USER_RATIFICATION')
            for s in x['sources']:
                src = self.d['sources'][s]
                self.assertEqual(src['tier'], 'A')
                self.assertTrue(src['url'].startswith('https://') and (src.get('dom_text_sha256') or src.get('snapshot_sha256')), s)
            if x['decision'] in ('PROMOTE', 'PROMOTE_PROVISIONAL', 'REALLOCATE_RECOMMENDED'):
                self.assertEqual((x['NAMESPACE_CHECK'], x['temporal_version']), ('PASS', 'CURRENT'))
            if x['decision'] == 'REJECT_FALSE_POSITIVE':
                self.assertEqual(x['NAMESPACE_CHECK'], 'FAIL')
        hc = [x for x in ds if x['klass'] == 'HC']
        self.assertTrue(hc and all(x['NEW_JURIS_TYPE_REQUIRES_DESIGN'] == 'YES' for x in hc))
        self.assertEqual(sum(self.d['totals'].values()), 10)

    def test_baseline_261_and_inputs_unchanged(self):
        self.assertEqual(sha(D.CURRENT), D.CURRENT_SHA)
        run9 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run9_juris_j2b_1_candidate'
        for line in (run9 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
            h, name = line.split('  ', 1)
            self.assertEqual(sha(run9 / name), h, name)
        m = json.loads((AUD / 'J2B_1_CANDIDATE_HOST_ONLY/J2B_1_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
        for d in m['file_diff'] + m['file_additions']:
            self.assertEqual(sha(AUD / 'J2B_1_CANDIDATE_HOST_ONLY/candidate/SD' / d['path'].lstrip('/')), d['after_sha256'])
        for rel, h in self.d['inputs'].items():
            self.assertEqual(D.B.sha_lf(ROOT / rel), h, rel)
        r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'apply_j2b_adi_overlay.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.stdout.strip(), 'UP_TO_DATE')                                  # ADI model, aliases, revalidation gate


if __name__ == '__main__':
    unittest.main()
