"""CC-J2: generated artifacts up to date, decisions valid and unratified, CC-J1 baseline intact, simulation without regression, factory
metrics consistent, generic batch engine rules fail closed."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
sys.path.insert(0, str(ENG))
import batch_engine as E  # noqa: E402


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class CCJ2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load(ENG / 'CC_J2_DECISIONS.json')
        cls.dec = cls.doc['decisions']
        cls.sim = load(ENG / 'cc_j2_simulation/CC_J2_SIMULATION_MANIFEST.json')
        cls.met = load(ENG / 'CC_J2_SCALE_METRICS.json')

    def test_generated_up_to_date(self):
        r = subprocess.run([sys.executable, '-B', str(ENG / 'build_cc_j2.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), r.stderr[-2000:])

    def test_decisions_unratified_and_valid(self):
        self.assertEqual(len(self.dec), 30)
        self.assertEqual(self.doc['status'], 'AWAITING_USER_RATIFICATION')
        for x in self.dec:
            self.assertEqual((x['status'], x['human_approved']), ('AWAITING_USER_RATIFICATION', False), x['id'])
            self.assertIn(x['decision'], E.DECISIONS)
            self.assertIn(x['group'], E.GROUPS)
            self.assertEqual(bool(x['proposed_targets']), x['decision'] in E.LINKING, x['id'])
            if x['group'] == 'GREEN':
                self.assertEqual((x['decision'], x['temporal']), ('PROMOTE_RECOMMENDED', 'CURRENT'), x['id'])
            for t in x['proposed_targets']:
                self.assertNotEqual(x['temporal_auto'].get(t, {}).get('result'), 'REVOKED', x['id'])
        m = self.doc['metrics']
        self.assertEqual((m['GREEN'], m['YELLOW'], m['RED']), (9, 13, 8))
        self.assertEqual((m['CC_PHYSICAL_BASELINE'], m['CF_REGRESSION'], m['CC_J1_REGRESSION'], m['DUPLICATE_QUERY_KEYS']), ('29/24', 0, 0, 0))

    def test_cc_j1_untouched(self):
        rec = load(ENG / 'CC_J1_RATIFICATION_RECORD.json')
        _, _, rows = E.physical_layer(ENG / 'CC_J1_MATERIALIZATION_CANDIDATE/candidate/SD')
        phys = {(r['target_id'], r['precedent_id']) for r in rows if r['target_id'].startswith('CC2002:')}
        approved = {(r['target_id'], r['precedent']) for r in rec['approved_relations']}
        self.assertEqual(phys, approved)
        self.assertEqual(len(phys), 29)
        proposed = {(r['target_id'], r['precedent']) for r in self.doc['proposed_relations']}
        self.assertFalse(proposed & phys)                                                  # nothing re-proposed, nothing replaced
        ids = {x['precedent'] for x in self.dec}
        for it in rec['items']:                                                            # pending and rejected CC-J1 precedents not reopened
            if it['human_state'] != 'HUMAN_APPROVED' and not it['human_state'].startswith('HUMAN_APPROVED'):
                self.assertNotIn(it['precedent'], ids, it['id'])
        man = load(ENG / 'CC_J1_MATERIALIZATION_CANDIDATE/SHA256_MANIFEST.json')
        files = man.get('files') or man.get('entries')
        import hashlib
        for k, v in files.items():
            h = v['sha256'] if isinstance(v, dict) else v
            self.assertEqual(hashlib.sha256((ENG / 'CC_J1_MATERIALIZATION_CANDIDATE' / k).read_bytes()).hexdigest(), h, k)

    def test_simulation(self):
        s = self.sim
        self.assertEqual((s['status'], s['deployable'], s['cc_j2_human_approved']), ('SIMULATION_ONLY', False, False))
        self.assertEqual((s['DUPLICATE_QUERY_KEYS'], s['BASELINE_RECORD_LINES_MISSING'], s['BASELINE_KEYS_NOT_PRESERVED'], s['OTHER_NORM_KEYS_CHANGED'],
                          s['OUTRO_LABELS']), (0, 0, 0, 0, 0))
        n = s['NEW_RELATIONS']
        self.assertEqual((s['NEW_VISIBLE'], s['NEW_FICHA_OPEN'], s['NEW_BACK']), (f'{n}/{n}',) * 3)
        self.assertEqual(s['counts']['CF88'][0] + s['counts']['ADCT'][0], 315)
        self.assertEqual(s['counts']['CC2002'][0], 29 + n)

    def test_scale_metrics(self):
        m = self.met
        self.assertEqual(m['NEW_CORE_ENGINE_CODE'], E.sloc(ENG / 'batch_engine.py')[0])
        self.assertEqual(m['SCALABILITY_WARNING']['cc_specific_logic_rewritten'], False)
        self.assertEqual((m['CC_J2']['NEW_SOURCE_ADAPTERS'], m['CC_J2']['SOURCE_BLOCKS'], m['CC_J1']['CANDIDATES']), (1, 0, 30))
        self.assertEqual(self.doc['metrics']['STJ_QUALIFIED_PRECEDENTS_SOURCE'], 'AVAILABLE')

    def test_engine_fails_closed(self):
        c = dict(precedent='STJ:SUMULA:1', channel='STJ_SUMULAS_PDF', theme='X', score=0, score_parts={}, discovered_targets=['CC2002:ART.757'],
                 pairs=[dict(target='CC2002:ART.757', in_index=True, temporal_auto=dict(checked=True, result='REVOKED', notes=[]),
                             steps={k: True for k in E.STEPS})], tribunal='STJ', klass='SUMULA_STJ', number='1', device_label='Súmula 1 STJ',
                 source=dict(tier='A', url='u', sha256='s'))
        idx = {'CC2002:ART.757', 'CC2002:ART.835'}
        base = dict(targets=['CC2002:ART.757'], temporal='CURRENT', confidence='HIGH', risk='BAIXO', motive='m')
        with self.assertRaises(E.BatchError):                                              # linking to a revoked dispositivo
            E.apply_review([c], {'STJ:SUMULA:1': dict(base, decision='PROMOTE_RECOMMENDED', group='YELLOW', yellow=('a',) * 5)}, 'CC2002', idx, 'T')
        with self.assertRaises(E.BatchError):                                              # GREEN that is a reallocation
            E.apply_review([c], {'STJ:SUMULA:1': dict(base, targets=['CC2002:ART.835'], decision='REALLOCATE_RECOMMENDED', group='GREEN')},
                           'CC2002', idx, 'T')
        with self.assertRaises(E.BatchError):                                              # RED that links
            E.apply_review([c], {'STJ:SUMULA:1': dict(base, targets=['CC2002:ART.835'], decision='REALLOCATE_RECOMMENDED', group='RED')},
                           'CC2002', idx, 'T')
        with self.assertRaises(E.BatchError):                                              # target outside the norm index
            E.apply_review([c], {'STJ:SUMULA:1': dict(base, targets=['CC2002:ART.999'], decision='REALLOCATE_RECOMMENDED', group='YELLOW')},
                           'CC2002', idx, 'T')
        ok = E.apply_review([c], {'STJ:SUMULA:1': dict(base, targets=[], decision='REJECT_TEMPORAL_MISMATCH_RECOMMENDED', group='RED')},
                            'CC2002', idx, 'T')
        self.assertEqual(ok[0]['status'], 'AWAITING_USER_RATIFICATION')

    def test_selection_deterministic_and_diverse(self):
        b = load(ENG / 'cc_j2/CC_J2_BACKLOG.json')
        self.assertEqual((b['CANDIDATE_PRECEDENTS'], b['SELECTED']), (41, 30))
        themes = {x['theme'] for x in self.dec}
        for th in ('OBRIGACOES', 'CONTRATOS', 'RESPONSABILIDADE_CIVIL', 'COISAS', 'FAMILIA', 'SUCESSOES', 'PRESCRICAO_DECADENCIA', 'PARTE_GERAL',
                   'PERSONALIDADE'):
            self.assertIn(th, themes)
        codes = b['excluded_by_code']
        self.assertTrue(codes.get('IN_PHYSICAL_BASELINE') and codes.get('CCJ1_PENDING') and codes.get('CCJ1_REJECTED_PRECEDENT'))


if __name__ == '__main__':
    unittest.main()
