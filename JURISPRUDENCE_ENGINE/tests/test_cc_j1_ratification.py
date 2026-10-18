"""CC-J1 human ratification: 30 reconciled proposals (22 approved / 2 pending / 6 not approved), final multi-target sets, nothing
materialized, proposals and dossier pinned and unchanged, CF baseline 315/198."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
sys.path.insert(0, str(ROOT / 'JURISPRUDENCE_AUDIT'))
import build_j2_batch as G  # noqa: E402


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class Ratification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = load(ENG / 'CC_J1_RATIFICATION_RECORD.json')
        cls.it = {i['id']: i for i in cls.rec['items']}

    def test_reproducible_and_inputs_unchanged(self):
        for s in ('build_cc_j1_ratification_record.py', 'build_cc_j1.py', 'build_cc_j1_dossier.py', 'build_cc_j1_simulation.py'):
            r = subprocess.run([sys.executable, '-I', '-B', str(ENG / s), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), s)
        self.assertTrue(all(x['status'] == 'AWAITING_USER_RATIFICATION' for x in load(ENG / 'CC_J1_DECISIONS.json')['decisions']))  # proposals untouched

    def test_counts(self):
        c = self.rec['counts']
        self.assertEqual((c['TOTAL_PROPOSALS'], c['PROPOSALS_HUMAN_APPROVED'], c['PROPOSALS_PENDING'], c['PROPOSALS_REJECTED']), (30, 22, 2, 6))
        self.assertEqual(c['NORMALIZED_RELATIONS_APPROVED'], len(self.rec['approved_relations']))
        self.assertEqual(c['NORMALIZED_RELATIONS_APPROVED'], len({(t, i['precedent']) for i in self.rec['items'] if i['human_approved'] for t in i['final_targets']}))

    def test_pending_and_red_not_materialized(self):
        self.assertEqual(self.it['CCJ1-09']['human_state'], 'PENDING_HUMAN_REVIEW')
        self.assertEqual(self.it['CCJ1-30']['human_state'], 'PENDING_TEMPORAL_REVALIDATION')
        rel_prec = {r['precedent'] for r in self.rec['approved_relations']}
        for i in ('CCJ1-09', 'CCJ1-30', 'CCJ1-08', 'CCJ1-16', 'CCJ1-19', 'CCJ1-24', 'CCJ1-26', 'CCJ1-28'):
            self.assertEqual((self.it[i]['final_targets'], self.it[i]['human_approved'], self.it[i]['materialized']), ([], False, False), i)
        self.assertEqual(sorted(self.rec['not_approved']), ['CCJ1-08', 'CCJ1-16', 'CCJ1-19', 'CCJ1-24', 'CCJ1-26', 'CCJ1-28'])
        self.assertNotIn('STF:RG:1194', rel_prec)
        self.assertNotIn('STJ:SUMULA:609', rel_prec)
        self.assertFalse(self.rec['materialized'] or self.rec['deployed'] or self.rec['physical_package'])

    def test_multi_target_sets(self):
        def targets(pid):
            return sorted(r['target_id'] for r in self.rec['approved_relations'] if r['precedent'] == pid)
        self.assertEqual(targets('STJ:SUMULA:403'), ['CC2002:ART.186', 'CC2002:ART.927'])
        self.assertEqual(targets('STF:ADI:6792-7055'), ['CC2002:ART.186', 'CC2002:ART.927'])
        self.assertEqual(targets('STJ:SUMULA:476'), ['CC2002:ART.662', 'CC2002:ART.917'])
        self.assertEqual(targets('STJ:SUMULA:496'), ['CC2002:ART.1231', 'CC2002:ART.99'])
        self.assertEqual(targets('STJ:SUMULA:547'), ['CC2002:ART.2028', 'CC2002:ART.206:PAR.3:INC.IV', 'CC2002:ART.206:PAR.5:INC.I'])
        self.assertEqual(targets('STJ:SUMULA:585'), ['CC2002:ART.1226', 'CC2002:ART.1267'])
        self.assertEqual(targets('STJ:SUMULA:405'), ['CC2002:ART.2028', 'CC2002:ART.206:PAR.3:INC.IX'])
        self.assertEqual(targets('STF:RG:932'), ['CC2002:ART.927:PAR.UNICO'])
        self.assertNotIn('CC2002:ART.186', targets('STJ:SUMULA:476'))
        self.assertEqual(self.it['CCJ1-22']['relation_note'], 'CONTEXTUAL_APPLICATION')
        self.assertEqual(self.it['CCJ1-25']['temporal_context'], 'CC1916_TO_CC2002')

    def test_cf_baseline_unchanged(self):
        vis = G.j2i_baseline()
        self.assertEqual((len(vis), len({r[0] for r in vis})), (315, 198))


if __name__ == '__main__':
    unittest.main()
