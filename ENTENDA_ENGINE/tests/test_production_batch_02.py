"""Tests for ENTENDA CF PRODUCTION BATCH 02 (arts. 6º-17), pending human review."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import entenda_engine as E  # noqa: E402

BD = HERE / 'derived/production_batch_02'
LK, PL = BD / 'index/ENTENDA_LOOKUP.IDX', BD / 'index/ENTENDA_PAYLOAD.DAT'
SELECTED = ('OVERVIEW', 'DEVICE', 'BLOCK', 'ITEM')


@unittest.skipUnless((BD / 'SELECTION_REPORT.json').is_file(), 'batch 02 not built')
class Batch02Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.new = E.load_corpus(BD / 'CF88_BATCH_02.entenda.jsonl')
        cls.rep = json.loads((BD / 'SELECTION_REPORT.json').read_text(encoding='utf-8'))
        cls.rows = {r['target_id']: r for r in cls.rep['selection']}
        cls.spec = json.loads((BD / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
        cls.jur = json.loads((BD / 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json').read_text(encoding='utf-8'))

    def test_scope_evaluated_and_pending(self):
        scope = [t for a in self.spec['scope'] for t in self.ctx.subtree(a)]
        self.assertEqual(sorted(self.rows), sorted(scope))
        self.assertTrue(all(r['selection_reason'] for r in self.rows.values()))
        self.assertTrue(all(r['review_status'] == 'PENDING_HUMAN_REVIEW' and r['status'] == 'ACTIVE' for r in self.new))
        self.assertEqual(len(self.new), self.rep['summary']['new_explanations'])
        self.assertTrue(30 <= len(self.new) <= self.spec['hard_cap'])
        self.assertFalse(any(r['target_id'].startswith(('CF88:ART.18', 'CF88:ART.19')) for r in self.new))

    def test_revoked_excluded_and_current_only(self):
        revoked = sorted(t for t, r in self.rows.items() if r['classification'] == 'EXCLUDED_REVOKED')
        self.assertEqual(revoked, ['CF88:ART.12:PAR.4:INC.II:AL.a', 'CF88:ART.12:PAR.4:INC.II:AL.b',
                                   'CF88:ART.7:INC.XXIX:AL.a', 'CF88:ART.7:INC.XXIX:AL.b'])
        self.assertTrue(all(r['validity']['target_status'] == 'CURRENT' for r in self.new))

    def test_no_separate_covered_and_no_duplicates_with_batch01(self):
        explained = {r['target_id'] for r in self.new}
        for r in self.rows.values():
            if r['classification'] == 'NO_SEPARATE_EXPLANATION':
                self.assertIn(r['covered_by'], explained, r['target_id'])
        b01 = {r['explanation_key'] for r in E.load_corpus(HERE / 'derived/production_batch_01_final/CF88_BATCH_01_FINAL.entenda.jsonl')}
        self.assertFalse(b01 & {r['explanation_key'] for r in self.new})

    def test_art7_semantic_not_mechanical(self):
        f = self.rep['summary']['focus_article']
        self.assertEqual((f['target'], f['incisos_evaluated']), ('CF88:ART.7', 34))
        self.assertLessEqual(f['own_explanations'], 15)
        self.assertGreaterEqual(f['by_classification']['BLOCK'], 5)

    def test_block_resolution_and_titles(self):
        cases = {'CF88:ART.7:INC.V': ('CF88:ART.7:INC.IV', 'Art. 7º, incisos IV, V, VI, VII e X — Salário mínimo, piso e proteção do salário'),
                 'CF88:ART.12:PAR.2': ('CF88:ART.12:PAR.3', 'Art. 12, §§ 2º e 3º — Distinções entre natos e naturalizados e cargos privativos'),
                 'CF88:ART.14:PAR.11': ('CF88:ART.14:PAR.10', 'Art. 14, §§ 10 e 11 — Ação de impugnação de mandato eletivo'),
                 'CF88:ART.17:PAR.9': ('CF88:ART.17:PAR.7', 'Art. 17, §§ 7º, 8º e 9º — Recursos para participação política de mulheres e de pessoas pretas e pardas')}
        for tid, (anchor, title) in cases.items():
            got = E.lookup_idx(tid, LK, PL)
            self.assertEqual((got['anchor_target_id'], got['resolution_type'], got['display_title']), (anchor, 'COVERED_BY_BLOCK', title), tid)
            r = E.resolve_explanation(tid, self.new)
            self.assertEqual((r['anchor_target_id'], r['display_title']), (anchor, title))
        self.assertEqual(E.lookup_idx('CF88:ART.14:CAPUT', LK, PL)['resolution_type'], 'DIRECT')
        self.assertIsNone(E.lookup_idx('CF88:ART.7:INC.XXIX:AL.a', LK, PL))  # revoked: no ENTENDA

    def test_jurisprudence_recommendations_only_with_local_identity(self):
        ex = json.loads((HERE.parent / 'LEGAL_TARGET_ID/derived/export_test/run1/CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))
        local = {l['source_id'] for ls in ex['references'].values() for l in ls if l['reference_type'] == 'JURISPRUDENCE'}
        for r in self.jur['recommendations']:
            if r['status'] == 'READY_TO_LINK':
                self.assertIn(r['local_identity_searched'], local)
                self.assertTrue(r['local_reference_id'])
            else:
                self.assertTrue(r['local_identity_searched'] is None or r['local_identity_searched'] not in local)
                self.assertIsNone(r['local_reference_id'])
        for r in self.new:
            c = r['content']
            for t in [c[k] for k in E.REQUIRED_TEXT] + [c['atencao'] or '']:
                self.assertIsNone(E.EXTERNAL_CASE_RE.search(t), r['target_id'])

    def test_deterministic_build(self):
        tmp = Path(tempfile.mkdtemp(prefix='b02_'))
        try:
            for run in ('a', 'b'):
                E.build_entenda_index(self.ctx, self.new, tmp / run)
            for name in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT', 'ENTENDA_BUILD_MANIFEST.json'):
                self.assertEqual((tmp / 'a' / name).read_bytes(), (tmp / 'b' / name).read_bytes(), name)
                self.assertEqual((tmp / 'a' / name).read_bytes(), (BD / 'index' / name).read_bytes(), name)
        finally:
            shutil.rmtree(tmp)


if __name__ == '__main__':
    unittest.main()
