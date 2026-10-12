"""CF88_CORRELATA_C1B HIGH Batch02 + Batch01 independent review: complete, founded, deterministic, NOT applied."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
ROOT = AUDIT.parent
sys.path.insert(0, str(AUDIT / 'tools'))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_c1b_high_batch01 as B1  # noqa: E402
import build_c1b_high_batch02 as B2  # noqa: E402
import target_id as T  # noqa: E402

J_IN, J_DEC, MD = B2.build()
INP, DEC = json.loads(J_IN), json.loads(J_DEC)
OPERATIONAL = ('LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json', 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json',
               'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json', 'LEGAL_TARGET_ID/derived/export_test/run3/REF_LOOKUP.IDX',
               'LEGAL_TARGET_ID/derived/export_test/run3/REF_PAYLOAD.IDX', 'LEGAL_TARGET_ID/derived/export_test/run3/CF88_REFERENCES_EXPORT.json')
SCOPE_WORDS = ('ESCOPO_', 'SUBSIDIARIA', 'NON_EXCLUSIVE')


class Batch02(unittest.TestCase):
    def test_deterministic_and_committed(self):
        self.assertEqual(B2.build(), (J_IN, J_DEC, MD))
        for p, b in zip((B2.OUT_IN, B2.OUT_DEC, B2.OUT_MD), (J_IN, J_DEC, MD)):
            self.assertEqual(p.read_bytes().replace(b'\r\n', b'\n'), b, p.name)

    def test_selection_rules(self):
        q = json.loads(B1.QUEUE.read_text(encoding='utf-8'))
        high = {x['candidate_id']: x for x in q['HIGH']}
        b1 = set(json.loads(B1.OUT_IN.read_text(encoding='utf-8'))['selection']['candidate_ids'])
        ids = INP['selection']['candidate_ids']
        self.assertLessEqual(len(ids), 30)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(set(ids) <= set(high))
        self.assertFalse(set(ids) & b1)
        pairs = [(high[i]['target_id'], high[i]['norm_key']) for i in ids]
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertEqual([d['candidate_id'] for d in DEC['decisions']], ids)
        self.assertEqual(DEC['summary']['high_remaining_after_batch02'], len(INP['selection']['remaining_after']))
        # structural order and "no skipping": the batch is exactly the head of the eligible pool
        _, pool, batch, _, _ = B2.select()
        self.assertEqual([x['candidate_id'] for x in pool[:len(ids)]], ids)

    def test_decision_requirements(self):
        for d in DEC['decisions']:
            self.assertIn(d['legal_decision'], B1.DECISIONS)
            self.assertFalse(d['applied'])
            self.assertGreater(len(d['legal_analysis']), 60, d['candidate_id'])
            if d['legal_decision'] in ('APPROVE', 'ADJUST'):
                self.assertTrue(d['official_sources'])
                for s in d['official_sources']:
                    self.assertRegex(s['url'], r'^https://www\.planalto\.gov\.br/ccivil_03/')
                    self.assertRegex(s['sha256'], r'^[0-9a-f]{64}$')
                self.assertIn(d['relation_type_final'], B1.RELATION_TYPES)
                self.assertTrue(T.validate_target_id(d['target_final'])[0])
                self.assertTrue(d['route'] and d['device_route_status'] and d['ingestion_status'])
                if d['relation_type_final'] == 'IMPLEMENTA':
                    self.assertTrue(any(w in (d['notes'] or '') for w in SCOPE_WORDS), d['candidate_id'])
            else:
                self.assertIsNone(d['target_final'])
            if d['legal_decision'] in ('HOLD', 'NEEDS_SOURCE'):
                self.assertTrue(d['notes'])
            if d['legal_decision'] == 'ADJUST':
                self.assertTrue(d['relation_type_final'] != d['c0_relation_type'] or d['target_final'] != d['target'], d['candidate_id'])

    def test_backlog_is_not_a_decision(self):
        ids = set(INP['selection']['candidate_ids'])
        for b in DEC['NEW_CANDIDATE_BACKLOG']:
            self.assertEqual(b['status'], 'BACKLOG_NOT_DECIDED')
            self.assertIn(b['origin'], ids)

    def test_operational_files_unchanged(self):
        for p in OPERATIONAL:
            blob = subprocess.run(['git', 'show', f"{B2.BASE['head']}:{p}"], cwd=ROOT, capture_output=True, check=True).stdout
            self.assertEqual((ROOT / p).read_bytes().replace(b'\r\n', b'\n'), blob.replace(b'\r\n', b'\n'), p)
        self.assertFalse((ROOT / 'LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json').exists())


class Batch01IndependentReview(unittest.TestCase):
    def test_one_adjustment_only(self):
        doc = json.loads(B1.build()[1])
        ir = doc['independent_review']
        self.assertEqual(ir['verdict'], 'APPROVED_WITH_ONE_ADJUSTMENT')
        s = doc['summary']
        self.assertEqual(s['decisions']['APPROVE'] + s['decisions']['ADJUST'], 21)
        self.assertEqual((s['decisions']['REJECT'], s['decisions']['HOLD']), (7, 1))
        self.assertEqual(s['independent_review_relation_changes'], 1)
        by = {d['candidate_id']: d for d in doc['decisions']}
        d = by['CORRC0-E1D20570E8DC']
        self.assertEqual((d['legal_decision'], d['relation_type_final'], d['relation_type_final_initial']), ('APPROVE', 'IMPLEMENTA', 'REGULAMENTA'))
        self.assertEqual(d['scope']['scope'], 'FEDERAL_EXECUTIVE')
        self.assertIn('ESCOPO_PARCIAL', by['CORRC0-7C51431603DB']['scope']['flags'])
        self.assertTrue(by['CORRC0-DAD68D5F75A2']['scope']['REVALIDATE_ON_NEW_COMPLEMENTARY_LAW'])
        self.assertEqual(ir['new_candidate_backlog'][0]['target_id'], 'CF88:ART.21:INC.XXVI')


if __name__ == '__main__':
    unittest.main()
