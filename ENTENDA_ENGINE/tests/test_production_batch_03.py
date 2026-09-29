"""Tests for ENTENDA CF PRODUCTION BATCH 03 (arts. 18-24), pending human review."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import entenda_engine as E  # noqa: E402

BD = HERE / 'derived/production_batch_03'
LK, PL = BD / 'index/ENTENDA_LOOKUP.IDX', BD / 'index/ENTENDA_PAYLOAD.DAT'
PRIOR = ('derived/production_batch_01_final/CF88_BATCH_01_FINAL.entenda.jsonl',
         'derived/production_batch_02_final/CF88_BATCH_02_FINAL.entenda.jsonl')


def _body(r):
    c = r['content']
    return ' '.join([c[k] for k in E.REQUIRED_TEXT] + [c['atencao'] or ''] + [t['explicacao'] for t in c['palavras_dificeis']])


@unittest.skipUnless((BD / 'SELECTION_REPORT.json').is_file(), 'batch 03 not built')
class Batch03Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.new = E.load_corpus(BD / 'CF88_BATCH_03.entenda.jsonl')
        cls.by = {r['target_id']: r for r in cls.new}
        cls.rep = json.loads((BD / 'SELECTION_REPORT.json').read_text(encoding='utf-8'))
        cls.rows = {r['target_id']: r for r in cls.rep['selection']}
        cls.spec = json.loads((BD / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
        cls.jur = json.loads((BD / 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json').read_text(encoding='utf-8'))

    def test_scope_counts_and_pending(self):
        scope = [t for a in self.spec['scope'] for t in self.ctx.subtree(a)]
        self.assertEqual(sorted(self.rows), sorted(scope))
        s = self.rep['summary']
        self.assertEqual((s['targets_evaluated'], s['targets_legally_current'], s['targets_revoked']), (134, 134, 0))
        self.assertEqual(len(self.new), 46)
        self.assertLessEqual(len(self.new), self.spec['hard_cap'])
        self.assertTrue(all(r['review_status'] == 'PENDING_HUMAN_REVIEW' and r['status'] == 'ACTIVE' for r in self.new))
        self.assertEqual(s['review_status_counts'], {'PENDING_HUMAN_REVIEW': 46})

    def test_no_invented_targets_and_art25_untouched(self):
        scope = {t for a in self.spec['scope'] for t in self.ctx.subtree(a)}
        for r in self.new:
            for t in [r['target_id']] + r['granularity'].get('covered_targets', []):
                self.assertIn(t, scope, t)
                self.assertTrue(self.ctx.structurally_present(t), t)
                self.assertTrue(self.ctx.legally_current(t), t)
        self.assertFalse(any(re.match(r'CF88:ART\.(2[5-9]|[3-9]\d|\d{3})\b', t) for t in self.rows))

    def test_no_separate_covered_and_no_duplicates_with_prior_batches(self):
        explained = set(self.by)
        for r in self.rows.values():
            if r['classification'] == 'NO_SEPARATE_EXPLANATION':
                self.assertIn(r['covered_by'], explained, r['target_id'])
        prior = {r['explanation_key'] for p in PRIOR for r in E.load_corpus(HERE / p)}
        self.assertFalse(prior & {r['explanation_key'] for r in self.new})

    def test_covered_targets_resolve(self):
        cases = {'CF88:ART.22:INC.V': ('CF88:ART.22:INC.IV', 'Art. 22, incisos IV, V, IX, X e XI — Águas, energia, comunicações e transportes'),
                 'CF88:ART.24:PAR.4': ('CF88:ART.24:PAR.3', 'Art. 24, §§ 3º e 4º — Competência plena dos Estados e suspensão da eficácia'),
                 'CF88:ART.24:PAR.2': ('CF88:ART.24:PAR.1', None)}
        for tid, (anchor, title) in cases.items():
            got = E.lookup_idx(tid, LK, PL)
            self.assertEqual((got['anchor_target_id'], got['resolution_type']), (anchor, 'COVERED_BY_BLOCK'), tid)
            if title:
                self.assertEqual(got['display_title'], title)
            self.assertEqual(E.resolve_explanation(tid, self.new)['anchor_target_id'], anchor)
        self.assertEqual(E.lookup_idx('CF88:ART.22:PAR.UNICO', LK, PL)['resolution_type'], 'DIRECT')
        for r in self.new:  # every covered sibling resolves to its own block
            for t in r['granularity'].get('covered_targets', []):
                self.assertEqual(E.lookup_idx(t, LK, PL)['anchor_target_id'], r['target_id'], t)

    def test_art21_material_not_legislative(self):
        f = self.by['CF88:ART.21']
        self.assertIn('materiais ou administrativas', f['content']['o_que_significa'])
        self.assertIn('Não tratam de legislar', f['content']['o_que_significa'])
        for r in self.new:
            if r['target_id'].startswith('CF88:ART.21'):
                self.assertNotRegex(_body(r), r'(?<!não )compete à União legislar')
                self.assertNotIn('competência legislativa da União prevista no art. 21', _body(r))

    def test_art22_legislative_and_delegation(self):
        self.assertIn('competência é legislativa', self.by['CF88:ART.22']['content']['o_que_significa'])
        pu = self.by['CF88:ART.22:PAR.UNICO']
        self.assertEqual(self.rows['CF88:ART.22:PAR.UNICO']['classification'], 'DEVICE')
        t = _body(pu)
        for w in ('lei complementar', 'Estados', 'questões específicas'):
            self.assertIn(w, t)
        for r in self.new:
            if r['target_id'].startswith('CF88:ART.22'):
                for m in re.finditer(r'indelegáve', _body(r)):  # only ever denied, never asserted
                    self.assertIn('não', _body(r)[max(0, m.start() - 25):m.start()], r['target_id'])
        self.assertIn('"Privativa" não significa, porém, indelegável', self.by['CF88:ART.22']['content']['o_que_significa'])

    def test_art23_common_administrative(self):
        s = self.by['CF88:ART.23']['content']['o_que_significa']
        self.assertIn('Competência comum é administrativa', s)
        self.assertIn('Não se trata de competência para legislar', s)
        self.assertIn('cooperação', _body(self.by['CF88:ART.23:PAR.UNICO']))

    def test_art24_concurrent_and_suspension_not_revocation(self):
        s = self.by['CF88:ART.24']['content']['o_que_significa']
        self.assertIn('normas gerais', s)
        self.assertIn('Competência suplementar', ' '.join(t['termo'] for t in self.by['CF88:ART.24:PAR.1']['content']['palavras_dificeis']))
        b = self.by['CF88:ART.24:PAR.3']
        self.assertEqual(b['granularity']['covered_targets'], ['CF88:ART.24:PAR.4'])
        t = _body(b)
        self.assertIn('suspende a eficácia', t)
        self.assertIn('suspensão da eficácia', t)
        self.assertIn('competência legislativa plena', t)
        for r in self.new:
            if r['target_id'].startswith('CF88:ART.24'):
                for m in re.finditer(r'revoga\w*', _body(r)):
                    ctx = _body(r)[max(0, m.start() - 20):m.start()]
                    self.assertRegex(ctx, r'(não|não é|não em)\s*$', r['target_id'])

    def test_art19_laicidade_without_hostile_label(self):
        t = _body(self.by['CF88:ART.19'])
        for w in ('subvenc', 'embaraçar', 'colaboração de interesse público', 'fé', 'brasileiros', 'laicidade'):
            self.assertIn(w, t.lower() if w.islower() else t)
        self.assertNotRegex(t.lower(), r'estado ateu|ateísmo')
        self.assertNotIn('1157', json.dumps(self.by['CF88:ART.19'], ensure_ascii=False))

    def test_jurisprudence_statuses_and_tema1157_excluded(self):
        st = {}
        for r in self.jur['recommendations']:
            st.setdefault(r['status'], []).append(r)
        self.assertEqual({k: len(v) for k, v in st.items()},
                         {'READY_TO_LINK': 10, 'IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION': 1,
                          'PENDING_EXTERNAL_INGESTION': 5, 'MATERIAL_MISMATCH_EXCLUDED': 1})
        (mm,) = st['MATERIAL_MISMATCH_EXCLUDED']
        self.assertEqual((mm['target_id'], mm['local_identity_searched']), ('CF88:ART.19', 'STF:RG:1157'))
        self.assertFalse(mm['subject_verification']['verified'])
        self.assertIn('ADCT', mm['subject_verification']['thesis_excerpt'])
        for r in st['READY_TO_LINK']:
            self.assertTrue(r['already_linked_to_target'] and r['subject_verification']['verified'], r['desired_reference'])
        (idf,) = st['IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION']
        self.assertEqual(idf['local_identity_searched'], 'STF:RG:1031')  # local link sits on another target
        self.assertFalse(idf['already_linked_to_target'])
        for r in st['PENDING_EXTERNAL_INGESTION']:
            self.assertIsNone(r['local_reference_id'])
        self.assertEqual(self.rep['summary']['jurisprudence_recommendations']['material_mismatch_excluded'], 1)
        for r in self.new:
            self.assertIsNone(E.EXTERNAL_CASE_RE.search(_body(r)), r['target_id'])

    def test_deterministic_build(self):
        tmp = Path(tempfile.mkdtemp(prefix='b03_'))
        try:
            for run in ('a', 'b'):
                E.build_entenda_index(self.ctx, self.new, tmp / run)
            for name in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT', 'ENTENDA_BUILD_MANIFEST.json'):
                self.assertEqual((tmp / 'a' / name).read_bytes(), (tmp / 'b' / name).read_bytes(), name)
                self.assertEqual((tmp / 'a' / name).read_bytes(), (BD / 'index' / name).read_bytes(), name)
        finally:
            shutil.rmtree(tmp)

    def test_approved_batches_immutable(self):
        """Batch 01 and Batch 02 final artifacts match the committed blobs (HEAD)."""
        root = HERE.parent
        for d in ('production_batch_01_final', 'production_batch_02_final'):
            out = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', f'ENTENDA_ENGINE/derived/{d}'], cwd=root)
            self.assertEqual(out.returncode, 0, d)
        b02 = [r for r in E.load_corpus(HERE / PRIOR[1]) if r['status'] == 'ACTIVE']
        self.assertEqual(len(b02), 50)
        self.assertTrue(all(r['review_status'] == 'HUMAN_APPROVED_T1' for r in b02))


if __name__ == '__main__':
    unittest.main()
