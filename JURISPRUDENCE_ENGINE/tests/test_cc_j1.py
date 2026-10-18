"""CC-J1 — first real Código Civil batch: deterministic selection, official sources, temporal audit, nothing approved or published."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
D = ENG / 'CC_J1_DECISIONS.json'


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class CCJ1(unittest.TestCase):
    def test_up_to_date(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(ENG / 'build_cc_j1.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))

    def test_selection_and_states(self):
        d = load(D)
        xs = d['decisions']
        self.assertEqual(len(xs), 30)
        self.assertEqual((d['selection']['planalto_stf'], d['selection']['stj']), (10, 20))
        self.assertEqual(len({(x['discovered_target'], x['precedent']) for x in xs}), 30)
        self.assertEqual(len({x['precedent'] for x in xs if x['channel'] == 'STJ_SUMULAS_PDF'}), 19)        # 403 twice + 18 distinct
        for x in xs:
            self.assertEqual((x['status'], x['human_approved']), ('AWAITING_USER_RATIFICATION', False))
            self.assertEqual(x['source']['tier'], 'A')
            self.assertNotIn('OUTRO', x['device_label'])
        s403 = {x['discovered_target']: x['decision'] for x in xs if x['precedent'] == 'STJ:SUMULA:403'}
        self.assertEqual(s403, {'CC2002:ART.186': 'PROMOTE_RECOMMENDED', 'CC2002:ART.927': 'PROMOTE_RECOMMENDED'})
        self.assertTrue(all(x['status_oficial'] in ('VIGENTE', 'ALTERADA') for x in xs if x['tribunal'] == 'STJ'))

    def test_targets_and_temporal(self):
        d = load(D)
        idx = {t['target_id'] for t in load(ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json')['targets']}
        amend = load(ENG / 'pilot_cc/PLANALTO_CC2002_ANNOTATIONS.json')['amendments']
        for x in d['decisions']:
            for t in x['proposed_targets']:
                self.assertIn(t, idx)
                self.assertFalse([a for a in amend.get(t, []) if a['kind'].lower().startswith('revogad')], t)   # never onto a revoked article
        sim = {(r['target_id'], r['precedent']) for r in d['simulation_relations']}
        blocked = {(t, x['precedent']) for x in d['decisions'] if x['temporal'] == 'NEEDS_REVIEW' for t in x['proposed_targets']}
        self.assertFalse(sim & blocked)
        self.assertEqual(d['metrics']['CC_J1_CANDIDATES'], d['metrics']['CC_J1_PROMOTE'] + d['metrics']['CC_J1_REALLOCATE']
                         + d['metrics']['CC_J1_REJECT'] + d['metrics']['CC_J1_UNRESOLVED'])


if __name__ == '__main__':
    unittest.main()
