"""Tests for ENTENDA CF PRODUCTION BATCH 06 (arts. 42-75): T1 drafts and triage only (no human approval in this phase)."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import editorial_checks as EC  # noqa: E402
import entenda_engine as E  # noqa: E402
import production_batch as PB  # noqa: E402
import t1_batch_packets as BP  # noqa: E402
import t1_risk as R  # noqa: E402
import t1_validator_v2 as V  # noqa: E402

BD = HERE / 'derived/production_batch_06'
INPUTS = ('BATCH_SPEC.json', 'BATCH_06_DRAFTS.json', 'EDITORIAL_REVIEW_INPUT.json', 'BATCH06_TARGET_PLAN.json')
PILOTS = ('CF88:ART.60', 'CF88:ART.60:PAR.4', 'CF88:ART.60:PAR.4:INC.IV')


def load(name):
    return json.loads((BD / name).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Batch06(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.spec = load('BATCH_SPEC.json')
        cls.corpus = [r for r in E.load_corpus(BD / 'CF88_BATCH_06.entenda.jsonl') if r['status'] == 'ACTIVE']
        cls.sel = load('SELECTION_REPORT.json')
        cls.tri = load('BATCH06_TRIAGE.json')
        cls.chk = load('EDITORIAL_CHECKS.json')

    def test_scope_and_prior_corpora(self):
        self.assertEqual(self.spec['scope'], [f'CF88:ART.{n}' for n in range(42, 76)])
        self.assertIn('ENTENDA_ENGINE/derived/production_batch_05/CF88_BATCH_05.entenda.jsonl', self.spec['prior_corpora'])
        self.assertEqual(sorted(self.spec['reused']), sorted(PILOTS))

    def test_no_human_approval_granted(self):
        cfg = V.load_json(V.CONFIG)
        self.assertFalse(cfg['AUTO_APPROVE_LOW'])
        self.assertFalse(cfg['AUTO_APPROVE_MEDIUM'])
        self.assertEqual(len(self.corpus), 93)
        self.assertTrue(all(r['review_status'] == 'PENDING_HUMAN_REVIEW' for r in self.corpus))
        self.assertEqual(self.tri['human_approved_t1_granted'], 0)
        self.assertEqual(self.sel['summary']['review_status_counts'], {'HUMAN_APPROVED_T1': 3, 'PENDING_HUMAN_REVIEW': 93})

    def test_every_current_target_selected_or_skipped_with_reason(self):
        rows = self.sel['selection']
        cur = [r for r in rows if r['status'] == 'CURRENT']
        self.assertEqual(len(cur), 309)
        self.assertEqual(sum(1 for r in rows if r['classification'] == 'EXCLUDED_HISTORICAL'), 9)
        for r in cur:
            self.assertTrue(r.get('selection_reason'), r['target_id'])
        skips = [r for r in cur if r['classification'] == 'NO_SEPARATE_EXPLANATION']
        self.assertEqual(len(cur) - len(skips), 96)
        self.assertTrue(all(r.get('covered_by') for r in skips))

    def test_article_60_only_pilots(self):
        own60 = [r['target_id'] for r in self.corpus if r['target_id'] == 'CF88:ART.60' or r['target_id'].startswith('CF88:ART.60:')]
        self.assertEqual(own60, [])

    def test_no_historical_target_explained(self):
        for r in self.corpus:
            for t in [r['target_id']] + r['granularity'].get('covered_targets', []):
                self.assertEqual(self.ctx.effective_status(t), 'CURRENT', t)

    def test_art75_recent_wording_flagged(self):
        r = next(x for x in self.corpus if x['target_id'] == 'CF88:ART.75')
        self.assertTrue(any('EXTERNAL_VERIFICATION_REQUIRED' in n for n in r['external_layer_notes']))
        risk = load('EDITORIAL_REVIEW_INPUT.json')['risk']['CF88:ART.75']
        self.assertEqual(risk['level'], 'HIGH')
        self.assertIn('EC_WORDING', risk['rules'])
        self.assertIn('EXTERNAL_LAW_STATE', risk['rules'])
        self.assertIn('EC 139', load('BATCH06_TARGET_PLAN.json')['vigency_findings']['ART75_EC139_2026'])

    def test_risk_classifier_rules(self):
        risk = load('EDITORIAL_REVIEW_INPUT.json')['risk']
        self.assertEqual(sorted(risk), sorted(r['target_id'] for r in self.corpus))
        for t, v in risk.items():
            if v['level'] == 'HIGH':
                self.assertTrue(v['rules'], t)
        rec = next(x for x in self.corpus if x['target_id'] == 'CF88:ART.49:INC.IX')
        self.assertNotIn('COMPLEX_REMISSION', R.classify(rec, self.ctx)['rules'])  # snapshot ids are not remissions

    def test_queues_and_packets(self):
        c = self.tri['counts']
        self.assertEqual(sum(c.values()), 93)
        self.assertEqual(c['E_HARD_FAIL'], 0)
        self.assertIn('Total: **0**', (BD / 'BATCH06_HARD_FAIL_REPORT.md').read_text(encoding='utf-8'))
        full = (BD / 'BATCH06_FULL_HUMAN_REVIEW.md').read_text(encoding='utf-8')
        compact = (BD / 'BATCH06_COMPACT_CLEAN_REVIEW.md').read_text(encoding='utf-8')
        for x in self.tri['rows']:
            if x['queue'] == 'D_FULL_HUMAN_REVIEW':
                self.assertIn(f"`{x['target_id']}`", full)
                self.assertNotIn(f"### `{x['target_id']}`", compact)
            if x['risk'] == 'HIGH':
                self.assertEqual(x['queue'], 'D_FULL_HUMAN_REVIEW', x['target_id'])

    def test_micro_adjustments_not_applied(self):
        m = load('MICRO_ADJUSTMENTS_LOG.json')
        self.assertFalse(m['microauto_apply'])
        self.assertEqual(m['applied'], 0)

    def test_editorial_open_findings_are_routed(self):
        open_ = {r['target_id'] for r in self.chk['rows'] if r['unresolved']}
        q = {x['target_id']: x['queue'] for x in self.tri['rows']}
        for t in open_:
            self.assertIn(q[t], ('C_QUICK_REVIEW', 'D_FULL_HUMAN_REVIEW'), t)

    def test_batch05_untouched(self):
        p = 'ENTENDA_ENGINE/derived/production_batch_05/CF88_BATCH_05.entenda.jsonl'
        head = subprocess.run(['git', 'show', f'HEAD:{p}'], cwd=ROOT, capture_output=True, check=True).stdout
        self.assertEqual(hashlib.sha256(head).hexdigest(), sha(ROOT / p))

    def test_rebuild_is_byte_identical(self):
        ev = load('DETERMINISM_EVIDENCE.json')
        self.assertTrue(ev['byte_identical'])
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp) / 'production_batch_06'
            td.mkdir()
            for n in INPUTS:
                shutil.copy(BD / n, td / n)
            PB.run(td)
            EC.run(td)
            BP.run(td)
            for n in ('CF88_BATCH_06.entenda.jsonl', 'index/ENTENDA_LOOKUP.IDX', 'index/ENTENDA_PAYLOAD.DAT', 'EDITORIAL_CHECKS.json',
                      'BATCH06_TRIAGE.json', 'BATCH06_FULL_HUMAN_REVIEW.md', 'BATCH06_QUICK_REVIEW.md', 'BATCH06_COMPACT_CLEAN_REVIEW.md'):
                self.assertEqual(sha(td / n), ev['sha256'][n], n)


if __name__ == '__main__':
    unittest.main()
