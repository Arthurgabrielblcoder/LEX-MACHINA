"""J2 Batches 03+ — generic checks for every batch decision file produced by build_j2_batch.py (HIGH/MEDIUM/LOW)."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
sys.path.insert(0, str(AUD))
import build_j2_batch as G  # noqa: E402


def batches():
    out = []
    for lvl, d in G.LEVEL_DIR.items():
        for p in sorted(d.glob('J2_BATCH*_DECISIONS.json')) if d.is_dir() else []:
            out.append((int(p.name[8:10]), lvl, p))
    return sorted(out)


class J2Batches(unittest.TestCase):
    def test_at_least_batch03_exists(self):
        self.assertTrue(any(n == 3 for n, _, _ in batches()))

    def test_each_batch(self):
        seen = {d['recommendation_id'] for k in (1, 2) for d in json.loads(G.RATIFIED[k].read_text(encoding='utf-8'))['decisions']}
        for n, lvl, p in batches():
            with self.subTest(batch=n):
                d = json.loads(p.read_text(encoding='utf-8'))
                r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'build_j2_batch.py'), '--batch', str(n), '--level', lvl, '--check'],
                                   capture_output=True, text=True, cwd=ROOT)
                self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))
                runs = {G.build(n, lvl, selection_only=True) for _ in range(3)}
                self.assertEqual(len(runs), 1)                                            # deterministic selection
                sel = d['selected']
                self.assertEqual(len(sel), len(set(sel)))
                self.assertLessEqual(len(sel), 10)
                self.assertFalse(set(sel) & seen, 'recommendation re-entered')             # never re-research a decided item
                q = {x['recommendation_id']: x for x in d['queue']}
                self.assertTrue(set(sel) <= set(q))
                self.assertEqual(d['level'], lvl)
                ds = d['decisions']
                self.assertEqual([x['recommendation_id'] for x in ds], sel)
                for x in ds:
                    self.assertEqual((x['status'], x['human_approved']), ('AWAITING_USER_RATIFICATION', False))
                    self.assertIn(x['NAMESPACE_CHECK'], ('PASS', 'FAIL'))
                    self.assertIn(x['temporal_version'], ('CURRENT', 'HISTORICAL', 'MIXED', 'NOT_APPLICABLE'))
                    self.assertTrue(x['OFFICIAL_SOURCE_REVIEWED'] and x['sources'] and x['reason'])
                    for s in x['sources']:
                        src = d['sources'][s]
                        self.assertTrue(src['url'].startswith('https://') and (src.get('dom_text_sha256') or src.get('snapshot_sha256')), s)
                    for pr in x['precedents']:
                        self.assertTrue(pr['id'].startswith('STF:'))
                seen |= set(sel)

    def test_installed_baseline_unchanged(self):
        import build_j2d_batch02 as D2
        self.assertEqual(hashlib.sha256(D2.CURRENT.read_bytes()).hexdigest(), D2.CURRENT_SHA)


if __name__ == '__main__':
    unittest.main()
