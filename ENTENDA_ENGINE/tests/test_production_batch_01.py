"""Tests for ENTENDA CF PRODUCTION BATCH 01 (arts. 1º-5º): selection policy, review states, coverage, cap, determinism."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import entenda_engine as E  # noqa: E402
import production_batch as P  # noqa: E402

BD = HERE / 'derived/production_batch_01'
SELECTED = ('OVERVIEW', 'DEVICE', 'BLOCK', 'ITEM')


@unittest.skipUnless((BD / 'SELECTION_REPORT.json').is_file(), 'batch 01 not built')
class Batch01Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.rep = json.loads((BD / 'SELECTION_REPORT.json').read_text(encoding='utf-8'))
        cls.rows = {r['target_id']: r for r in cls.rep['selection']}
        cls.new = E.load_corpus(BD / 'CF88_BATCH_01.entenda.jsonl')
        cls.main = [r for r in E.load_corpus(HERE / 'corpus/CF88.entenda.jsonl') if r['status'] == 'ACTIVE']
        cls.reused = [r for r in cls.main if r['target_id'] in ('CF88:ART.1', 'CF88:ART.5')]
        cls.spec = json.loads((BD / 'BATCH_SPEC.json').read_text(encoding='utf-8'))

    def test_every_scope_target_evaluated(self):
        scope = [t for a in self.spec['scope'] for t in self.ctx.subtree(a)]
        self.assertEqual(sorted(self.rows), sorted(scope))
        allowed = SELECTED + ('NO_SEPARATE_EXPLANATION', 'EXCLUDED_HISTORICAL', 'EXCLUDED_NOT_CURRENT')
        self.assertTrue(all(r['classification'] in allowed and r['selection_reason'] for r in self.rows.values()))

    def test_human_approved_vs_pending_review(self):
        self.assertTrue(all(r['review_status'] == 'PENDING_HUMAN_REVIEW' for r in self.new))
        self.assertTrue(all(r['review_status'] == 'HUMAN_APPROVED_T1' for r in self.reused))
        for r in self.rep['selection']:
            if r.get('explanation_source') == 'PILOT_T1_APPROVED':
                self.assertEqual(r['review_status'], 'HUMAN_APPROVED_T1')
            if r.get('explanation_source') == 'BATCH_NEW':
                self.assertEqual(r['review_status'], 'PENDING_HUMAN_REVIEW')
        lk = BD / 'index/ENTENDA_LOOKUP.IDX'
        self.assertEqual(E.lookup_idx('CF88:ART.1', lk, BD / 'index/ENTENDA_PAYLOAD.DAT')['review'], 'HUMAN_APPROVED_T1')
        self.assertEqual(E.lookup_idx('CF88:ART.2', lk, BD / 'index/ENTENDA_PAYLOAD.DAT')['review'], 'PENDING_HUMAN_REVIEW')

    def test_pilot_reused_not_duplicated(self):
        keys = [r['explanation_key'] for r in self.new]
        self.assertNotIn('ENTENDA/CF88:ART.1/BASE', keys)
        self.assertNotIn('ENTENDA/CF88:ART.5/BASE', keys)
        self.assertEqual(len(keys), len(set(keys)))
        dup = copy.deepcopy(self.spec)
        dup.pop('superseded_by_final', None)
        drafts = json.loads((BD / self.spec['drafts']).read_text(encoding='utf-8'))
        drafts['explanations'].append(dict(drafts['explanations'][0], target_id='CF88:ART.1'))
        tmp = Path(tempfile.mkdtemp(prefix='batch_dup_'))
        try:
            (tmp / 'BATCH_SPEC.json').write_text(json.dumps(dup), encoding='utf-8')
            (tmp / dup['drafts']).write_text(json.dumps(drafts, ensure_ascii=False), encoding='utf-8')
            with self.assertRaises(E.EntendaError) as cm:
                P.run(tmp)
            self.assertEqual(cm.exception.code, 'BATCH_DUPLICATE_TARGET_EXPLANATION')
        finally:
            shutil.rmtree(tmp)

    def test_no_separate_is_covered_by_real_explanation(self):
        explained = {r['target_id'] for r in self.new + self.reused}
        ns = [r for r in self.rows.values() if r['classification'] == 'NO_SEPARATE_EXPLANATION']
        self.assertTrue(ns)
        for r in ns:
            self.assertIn(r['covered_by'], explained, r['target_id'])
            self.assertNotIn(r['target_id'], explained)
        self.assertEqual(self.rows['CF88:ART.5:CAPUT']['covered_by'], 'CF88:ART.5')
        self.assertEqual(self.rows['CF88:ART.5:INC.XXXVIII:AL.d']['coverage'], 'BLOCK_SUBDIVISION')
        self.assertEqual(self.rows['CF88:ART.5:INC.LXX:AL.a']['covered_by'], 'CF88:ART.5:INC.LXIX')

    def test_covered_targets_are_real_siblings_and_lookup_marks_coverage(self):
        blocks = [r for r in self.new if r['granularity'].get('covered_targets')]
        self.assertTrue(blocks)
        for b in blocks:
            for c in b['granularity']['covered_targets']:
                self.assertTrue(self.ctx.exists(c))
                self.assertEqual(self.ctx.targets[c]['parent_id'], self.ctx.targets[b['target_id']]['parent_id'])
        got = E.lookup_idx('CF88:ART.5:INC.V', BD / 'index/ENTENDA_LOOKUP.IDX', BD / 'index/ENTENDA_PAYLOAD.DAT')
        self.assertEqual((got['target_id'], got['resolution_type']), ('CF88:ART.5:INC.IV', 'COVERED_BY_BLOCK'))
        bad = copy.deepcopy(blocks[0])
        bad['granularity']['covered_targets'] = ['CF88:ART.4:INC.I']  # not a sibling
        self.assertEqual(self.ctx and _code(E.validate_explanation, bad, self.ctx), 'ENTENDA_COVERED_INVALID')
        twice = copy.deepcopy(self.new)
        twice.append(dict(copy.deepcopy(self.new[5]), target_id='CF88:ART.5:INC.V'))
        self.assertIsNotNone(_code(E.validate_corpus, self.reused + twice, self.ctx))

    def test_historical_excluded_and_current_only(self):
        self.assertTrue(all(r['status'] == 'CURRENT' for r in self.rows.values() if r['classification'] != 'EXCLUDED_HISTORICAL'))
        self.assertEqual(self.rep['summary']['historical_excluded'], sum(1 for r in self.rows.values() if r['status'] == 'HISTORICAL'))
        for r in self.new:
            self.assertEqual(r['validity']['target_status'], 'CURRENT')
            for c in r['granularity'].get('covered_targets', []):
                self.assertEqual(self.ctx.effective_status(c), 'CURRENT')
        # a scope with historical devices: they are excluded, never explained
        fake = dict(target_id='CF88:ART.40', explanation_id='ENTENDA/CF88:ART.40/BASE/1', review_status='HUMAN_APPROVED_T1',
                    granularity=dict(role='OVERVIEW', editorial_reason='fixture'))
        spec = dict(self.spec, scope=['CF88:ART.40'], reused={'CF88:ART.40': 'fixture'}, _drafts=dict(explanations=[]),
                    overview_covers_all_subdivisions=['CF88:ART.40'], no_separate_reasons={})
        rows = P.classify(spec, self.ctx, [fake], [])
        hist = [r for r in rows if r['status'] == 'HISTORICAL']
        self.assertTrue(hist)
        self.assertTrue(all(r['classification'] == 'EXCLUDED_HISTORICAL' and 'covered_by' not in r for r in hist))

    def test_batch_cap(self):
        s = self.rep['summary']
        self.assertLessEqual(s['new_explanations'], self.spec['hard_cap'])
        tmp = Path(tempfile.mkdtemp(prefix='batch_cap_'))
        try:
            spec = dict(self.spec, hard_cap=10)
            spec.pop('superseded_by_final', None)
            (tmp / 'BATCH_SPEC.json').write_text(json.dumps(spec), encoding='utf-8')
            shutil.copy(BD / self.spec['drafts'], tmp / self.spec['drafts'])
            with self.assertRaises(E.EntendaError) as cm:
                P.run(tmp)
            self.assertEqual(cm.exception.code, 'BATCH_SPLIT_RECOMMENDED')
            self.assertTrue((tmp / 'BATCH_SPLIT_RECOMMENDED.json').is_file())
        finally:
            shutil.rmtree(tmp)

    def test_art5_hierarchy_and_no_explosion(self):
        f = self.rep['summary']['focus_article']
        self.assertEqual(f['incisos_evaluated'], 79)
        self.assertLess(f['own_explanations'], 79)
        self.assertGreater(f['no_separate'], 0)
        for r in self.new:
            if r['target_id'].startswith('CF88:ART.5:INC.'):
                self.assertEqual(r['granularity']['context_targets'], ['CF88:ART.5', 'CF88:ART.5:CAPUT'])
                self.assertEqual(r['granularity']['semantic_autonomy'], 'DEPENDENT_ON_PARENT')
        pairs = E.validate_corpus(self.reused + self.new, self.ctx)
        self.assertTrue(all(max(p['similarity'].values()) <= self.ctx.limits['max_section_similarity'] for p in pairs))
        self.assertIsNone(E.get_explanation('CF88:ART.5:INC.V', self.new))  # coverage is not inheritance

    def test_new_explanations_follow_t1(self):
        for r in self.new:
            E.validate_explanation(r, self.ctx)
            self.assertIn('ENTENDA-T1', r['template_version'])
            self.assertTrue(r['source']['source_text_sha256'])

    def test_deterministic_production_build(self):
        tmp = Path(tempfile.mkdtemp(prefix='batch_build_'))
        try:
            corpus = self.reused + self.new
            for run in ('a', 'b'):
                E.build_entenda_index(self.ctx, corpus, tmp / run)
            for name in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT', 'ENTENDA_BUILD_MANIFEST.json'):
                self.assertEqual((tmp / 'a' / name).read_bytes(), (tmp / 'b' / name).read_bytes(), name)
                self.assertEqual((tmp / 'a' / name).read_bytes(), (BD / 'index' / name).read_bytes(), name)
        finally:
            shutil.rmtree(tmp)


def _code(fn, *a):
    try:
        fn(*a)
    except E.EntendaError as e:
        return e.code
    return None


if __name__ == '__main__':
    unittest.main()
