"""CF88_CORRELATA_C1B HIGH Batch01 + C1A independent review: complete, founded, deterministic, NOT applied."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
ROOT = AUDIT.parent
sys.path.insert(0, str(AUDIT / 'tools'))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_c1a_review as C1A  # noqa: E402
import build_c1b_high_batch01 as B  # noqa: E402
import target_id as T  # noqa: E402

J_IN, J_DEC, MD = B.build()
INP, DEC = json.loads(J_IN), json.loads(J_DEC)
OPERATIONAL = ('LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json', 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json',
               'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json', 'LEGAL_TARGET_ID/derived/export_test/run3/REF_LOOKUP.IDX',
               'LEGAL_TARGET_ID/derived/export_test/run3/REF_PAYLOAD.IDX', 'LEGAL_TARGET_ID/derived/export_test/run3/CF88_REFERENCES_EXPORT.json')


class Batch01(unittest.TestCase):
    def test_deterministic_and_committed(self):
        self.assertEqual(B.build(), (J_IN, J_DEC, MD))
        for p, b in zip((B.OUT_IN, B.OUT_DEC, B.OUT_MD), (J_IN, J_DEC, MD)):
            self.assertEqual(p.read_bytes().replace(b'\r\n', b'\n'), b, p.name)

    def test_every_batch_candidate_decided_once_and_only_high(self):
        q = json.loads(B.QUEUE.read_text(encoding='utf-8'))
        high = {x['candidate_id'] for x in q['HIGH']}
        ids = INP['selection']['candidate_ids']
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual([d['candidate_id'] for d in DEC['decisions']], ids)
        self.assertTrue(set(ids) <= high)
        self.assertEqual(len(ids), INP['selection']['pool'] if INP['selection']['pool'] <= B.LIMIT_ALL else B.LIMIT_TAKE)
        self.assertEqual(sum(DEC['summary']['decisions'].values()), len(ids))

    def test_targets_valid_and_in_arts_5_43(self):
        for d in DEC['decisions']:
            for t in filter(None, (d['target'], d['target_final'])):
                self.assertTrue(T.validate_target_id(t)[0], t)
                art = int(T.parse_target_id(t)['article'].split('-')[0])
                self.assertTrue(5 <= art <= 43, t)

    def test_decision_requirements(self):
        for d in DEC['decisions']:
            self.assertIn(d['legal_decision'], B.DECISIONS)
            self.assertFalse(d['applied'])
            self.assertGreater(len(d['legal_analysis']), 60, d['candidate_id'])
            if d['legal_decision'] in ('APPROVE', 'ADJUST'):
                self.assertTrue(d['official_sources'], d['candidate_id'])
                for s in d['official_sources']:
                    self.assertRegex(s['url'], r'^https://www\.planalto\.gov\.br/ccivil_03/')
                    self.assertRegex(s['sha256'], r'^[0-9a-f]{64}$')
                self.assertIn(d['relation_type_final'], B.RELATION_TYPES)
                self.assertTrue(d['route'] and d['device_route_status'] and d['ingestion_status'])
            else:
                self.assertIsNone(d['target_final'])
                self.assertIsNone(d['device_route_status'])
            if d['legal_decision'] in ('HOLD', 'NEEDS_SOURCE'):
                self.assertTrue(d['notes'], d['candidate_id'])
            if d['legal_decision'] == 'ADJUST':
                self.assertTrue(d['relation_type_final'] != d['c0_relation_type'] or d['target_final'] != d['target'], d['candidate_id'])

    def test_amending_and_converted_acts_not_promoted(self):
        for d in DEC['decisions']:
            if any(k in (d['notes'] or '') for k in ('ALTERADORA_INCORPORADA', 'HISTORICA_CONVERTIDA')):
                self.assertEqual(d['legal_decision'], 'REJECT', d['candidate_id'])

    def test_operational_files_unchanged(self):
        for p in OPERATIONAL:
            blob = subprocess.run(['git', 'show', f"{C1A.BASE['head']}:{p}"], cwd=ROOT, capture_output=True, check=True).stdout
            self.assertEqual((ROOT / p).read_bytes().replace(b'\r\n', b'\n'), blob.replace(b'\r\n', b'\n'), p)
        self.assertFalse((ROOT / 'LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json').exists())


class C1AIndependentReview(unittest.TestCase):
    def test_verdict_and_unchanged_decisions(self):
        doc = json.loads(C1A.build()[0])
        self.assertEqual(doc['independent_review']['verdict'], 'APPROVED_WITH_NOTES')
        self.assertEqual(doc['independent_review']['decisions_materially_changed'], 'NO')
        self.assertEqual(doc['counts'], dict(KEEP=0, KEEP_WITH_ROUTE_FIX=0, RETARGET=1, REPLACE=5, REMOVE=12, HOLD=1))
        by = {d['current_target']: d for d in doc['decisions']}
        self.assertTrue(by['CF88:ART.20:PAR.1']['independent_review']['NON_EXCLUSIVE_PRIMARY_CORRELATA'])
        self.assertEqual(by['CF88:ART.43:PAR.1:INC.II']['independent_review']['independent_confidence'], 'ALTA')
        r182 = by['CF88:ART.182']['independent_review']
        self.assertTrue(r182['PRESENTATION_EQUIVALENT_RETARGET'])
        self.assertFalse(r182['ART_CAPUT_DUPLICATION'])
        self.assertEqual(by['CF88:ART.182']['decision'], 'RETARGET')


if __name__ == '__main__':
    unittest.main()
