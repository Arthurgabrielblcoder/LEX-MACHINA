"""CF88_CORRELATA_LEGACY_FULL_REVIEW: the 44 visible legacy links all carry an auditable decision; nothing applied."""
import json
import sys
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
ROOT = AUDIT.parent
sys.path.insert(0, str(AUDIT / 'tools'))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_legacy_full_review as LR  # noqa: E402
import target_id as T  # noqa: E402

OUT = LR.build()
DOC = json.loads(OUT[0])


class LegacyFullReview(unittest.TestCase):
    def test_deterministic_and_committed(self):
        self.assertEqual(LR.build(), OUT)
        for p, b in zip((LR.OUT_JSON, LR.OUT_MD), OUT):
            self.assertEqual(p.read_bytes().replace(b'\r\n', b'\n'), b, p.name)

    def test_all_44_visible_decided_once(self):
        s = DOC['summary']
        self.assertEqual((s['LEGACY_EXPORT_TOTAL'], s['LEGACY_VISIBLE_TOTAL'], s['LEGACY_HIDDEN_HISTORICAL']), (46, 44, 2))
        self.assertEqual((s['LEGACY_VISIBLE_REVIEWED'], s['decided_in_c1a'], s['reviewed_now']), (44, 19, 25))
        ids = [r['reference_id'] for r in DOC['links']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sum(s['decisions'].values()), 44)
        self.assertEqual(s['new_official_downloads'], 0)
        self.assertFalse(DOC['applied'])

    def test_rows_are_founded(self):
        for r in DOC['links']:
            self.assertIn(r['decision'], LR.DECISIONS)
            self.assertFalse(r['applied'])
            self.assertGreater(len(r['legal_analysis']), 60, r['reference_id'])
            if r['decision'] == 'RETARGET':
                self.assertTrue(T.validate_target_id(r['retarget_to'])[0], r['retarget_to'])
                self.assertNotEqual(r['retarget_to'], r['target_id'])
            if r['review_round'] == 'LEGACY_FULL_REVIEW':
                self.assertTrue(any(e['kind'] == 'CARD_TEXT_PIN' and len(e['sha256']) == 64 for e in r['evidence']))
                if r['decision'] == 'KEEP_WITH_ROUTE_FIX':
                    self.assertTrue(r['route_fix']['articles'])

    def test_key_decisions(self):
        by = {(r['target_id'], r['destination_norm_key']): r for r in DOC['links']}
        r = by[('CF88:ART.37:INC.II', 'LEI:14965/2024')]
        self.assertEqual((r['decision'], r['temporal']['temporal_status'], r['temporal']['effective_from']), ('KEEP', 'VACATIO_LEGIS', '2028-01-01'))
        self.assertIn('SUPPRESS_UNTIL_EFFECTIVE', r['flags'])
        self.assertEqual(by[('CF88:ART.195:INC.I', 'LC:70/1991')]['retarget_to'], 'CF88:ART.195:INC.I:AL.b')
        self.assertEqual(by[('CF88:ART.158:PAR.1:INC.II', 'LC:63/1990')]['retarget_to'], 'CF88:ART.158:PAR.1:INC.I')
        self.assertEqual(by[('CF88:ART.20:PAR.1', 'LEI:12734/2012')]['decision'], 'REMOVE')
        pne = [r for k, r in by.items() if k[1] == 'LEI:15388/2026']
        self.assertEqual(sorted(r['decision'] for r in pne), ['REMOVE'] * 5 + ['RETARGET'])


if __name__ == '__main__':
    unittest.main()
