"""J2 BATCH10 — first batch after the J2I freeze: coverage measured over J2I_FROZEN_315_198 + ratified Batches 01–09; proposals only;
backlog state recomputed from the batch files. Host-only."""
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

B10 = AUD / 'J2_MEDIUM_BACKLOG/J2_BATCH10_DECISIONS.json'


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class Batch10(unittest.TestCase):
    def test_reconstruction_over_j2i(self):
        d = load(B10)
        self.assertTrue(d['state_model']['PHYSICALLY_INSTALLED'].startswith('J2I_FROZEN_315_198'))
        self.assertEqual(d['inputs'][G.J2I_PAYLOAD.relative_to(ROOT).as_posix()], G.B.sha_lf(G.J2I_PAYLOAD))
        self.assertEqual(len(G.j2i_baseline()), 315)
        r = d['reconstruction']
        self.assertEqual((r['HIGH_CURRENT'], d['level'], len(d['selected'])), (0, 'MEDIUM', 10))
        self.assertEqual({k: v for k, v in d['previous_batches'].items() if v != 'RATIFIED'}, {'5': 'CLOSED_EMPTY'})

    def test_no_selected_item_already_installed_or_ratified(self):
        d = load(B10)
        installed = {(r[0], r[5]) for r in G.j2i_baseline()}
        for x in d['decisions']:
            for t in x['recommended_targets']:
                for p in x['precedents']:
                    self.assertNotIn((t, p['id']), installed, x['recommendation_id'])
            self.assertEqual((x['status'], x['human_approved']), ('AWAITING_USER_RATIFICATION', False))

    def test_unresolved_not_promoted(self):
        for x in load(B10)['decisions']:
            if x['decision'].startswith('UNRESOLVED'):
                self.assertEqual(x['recommended_targets'], [])
                self.assertFalse(x['OFFICIAL_SOURCE_REVIEWED'])

    def test_report_and_backlog_up_to_date(self):
        for cmd in (['render_j2_batch_report.py', '--batch', '10', '--level', 'MEDIUM', '--check'], ['build_j2_backlog_state.py', '--check']):
            r = subprocess.run([sys.executable, '-I', '-B', str(AUD / cmd[0])] + cmd[1:], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), cmd[0])
        s = load(AUD / 'J2_BACKLOG_STATE.json')
        self.assertEqual((s['after_batch'], s['HIGH_REMAINING'], s['AWAITING_USER_RATIFICATION']), ('BATCH10', 0, 0))   # Batch10 ratified
        unresolved = sum(len(v) for v in s['UNRESOLVED'].values())
        self.assertEqual(s['ALREADY_REVIEWED'], s['HUMAN_APPROVED'] + s['AWAITING_USER_RATIFICATION'] + unresolved)

    def test_ratification_record(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'build_j2_ratification_record_10.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))
        rec = load(AUD / 'J2_RATIFICATION_RECORD_10.json')
        self.assertEqual({k: v for k, v in rec.items() if k.startswith('BATCH10_')},
                         dict(BATCH10_RATIFIED_RECOMMENDATIONS=8, BATCH10_NEW_RELATIONS=6, BATCH10_NEW_TARGETS=6, BATCH10_ALREADY_COVERED=2,
                              BATCH10_REJECTED=1, BATCH10_UNRESOLVED=2))
        it = {i['recommendation_id']: i for i in rec['items']}
        self.assertEqual(it['J0-BL-023']['ratified_targets'], ['CF88:ART.17:PAR.1'])
        self.assertEqual(it['J0-BL-023']['temporal_provenance']['judgment_year'], 2015)
        self.assertEqual(it['J0-BL-027']['ratified_targets'], ['CF88:ART.19:INC.I', 'CF88:ART.210:PAR.1'])
        self.assertEqual([i for i, x in it.items() if x['editorial_modification']], ['J0-BL-027'])
        self.assertFalse(any(t.endswith('ART.17:PAR.6') for x in rec['normalized_relations'] for t in [x['target_id']]))
        self.assertEqual(it['J0-BL-093']['ratification_status'], 'UNRESOLVED_EXTERNAL')
        self.assertEqual(it['J0-BL-118']['ratification_status'], 'UNRESOLVED_IDENTIFICATION')
        self.assertEqual((rec['materialized'], rec['deployed']), (False, False))

    def test_nothing_materialized(self):
        self.assertEqual(hashlib.sha256(G.J2I_PAYLOAD.read_bytes()).hexdigest(), G.J2I_PAYLOAD_SHA)
        derived = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in (ROOT / 'LEGAL_TARGET_ID/derived').glob('CF88_JURIS_*.json'))
        for rid in load(B10)['selected']:
            self.assertNotIn(rid, derived)


if __name__ == '__main__':
    unittest.main()
