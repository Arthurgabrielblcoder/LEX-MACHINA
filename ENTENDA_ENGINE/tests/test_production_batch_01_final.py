"""Tests for the human-approved ENTENDA CF88 Batch 01 (arts. 1º-5º): review applied, block resolution, jurisprudence separation."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import entenda_engine as E  # noqa: E402

FD = HERE / 'derived/production_batch_01_final'
LK, PL = FD / 'ENTENDA_LOOKUP.IDX', FD / 'ENTENDA_PAYLOAD.DAT'


@unittest.skipUnless((FD / 'SELECTION_REPORT.json').is_file(), 'final batch 01 not built')
class Batch01FinalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.all = E.load_corpus(FD / 'CF88_BATCH_01_FINAL.entenda.jsonl')
        cls.new = [r for r in cls.all if r['status'] == 'ACTIVE']
        cls.reused = [r for r in E.load_corpus(HERE / 'corpus/CF88.entenda.jsonl') if r['status'] == 'ACTIVE' and r['target_id'] in ('CF88:ART.1', 'CF88:ART.5')]
        cls.corpus = cls.reused + cls.new
        cls.rep = json.loads((FD / 'SELECTION_REPORT.json').read_text(encoding='utf-8'))
        cls.dec = json.loads((FD / 'HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        cls.jur = json.loads((FD / 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json').read_text(encoding='utf-8'))

    def test_totals_and_review_status(self):
        self.assertEqual((len(self.new), len(self.corpus)), (53, 55))
        self.assertTrue(all(r['review_status'] == 'HUMAN_APPROVED_T1' for r in self.corpus))
        self.assertFalse([r for r in self.corpus if r['review_status'] == 'PENDING_HUMAN_REVIEW'])
        ids = {r['target_id'] for r in self.new}
        self.assertIn('CF88:ART.5:INC.LVIII', ids)
        self.assertIn('CF88:ART.5:PAR.4', ids)
        E.validate_corpus(self.corpus, self.ctx)

    def test_decisions_and_retirement(self):
        self.assertEqual((self.dec['review_status'], self.dec['review_date']), ('HUMAN_REVIEW_COMPLETED', '2026-09-28'))
        self.assertEqual(len(self.dec['decisions']), 53)
        self.assertEqual(self.dec['decision_counts'], {'APPROVED': 34, 'APPROVED_AFTER_ADJUSTMENT': 19})
        self.assertEqual((FD / 'HUMAN_REVIEW_DECISIONS.json').read_bytes(), (HERE / 'derived/production_batch_01/HUMAN_REVIEW_DECISIONS.json').read_bytes())
        retired = {r['target_id']: r for r in self.all if r['status'] == 'RETIRED'}
        adjusted = {d['target_id'] for d in self.dec['decisions'] if d['decision'] == 'APPROVED_AFTER_ADJUSTMENT'}
        self.assertEqual(set(retired), adjusted)
        original = {e['target_id']: e for e in json.loads((HERE / 'derived/production_batch_01/BATCH_01_DRAFTS.json').read_text(encoding='utf-8'))['explanations']}
        for tid, r in retired.items():
            self.assertEqual((r['review_status'], r['superseded_by']), ('CHANGES_REQUESTED', f'ENTENDA/{tid}/BASE/2'))
            self.assertEqual(r['content'], original[tid]['content'])  # evidence preserved
            d = next(x for x in self.dec['decisions'] if x['target_id'] == tid)
            self.assertEqual(d['original_content'], original[tid]['content'])
        for d in self.dec['decisions']:
            if d['decision'] == 'APPROVED' and d.get('origin') != 'CREATED_BY_HUMAN_REVIEW':
                self.assertEqual(E.get_explanation(d['target_id'], self.new)['content'], original[d['target_id']]['content'])

    def test_human_adjustments_present(self):
        g = {r['target_id']: r['content'] for r in self.new}
        self.assertIn('maioria absoluta dos Deputados e maioria absoluta dos Senadores', g['CF88:ART.2']['exemplo_pratico'])
        self.assertNotIn('conteúdo de proibição', g['CF88:ART.3']['o_que_significa'])
        self.assertNotIn('responde pelo que diz', g['CF88:ART.5:INC.IV']['o_que_significa'])
        self.assertIn('quando esse sigilo for necessário ao exercício profissional', g['CF88:ART.5:INC.IV']['exemplo_pratico'])
        self.assertNotIn('quartéis', g['CF88:ART.5:INC.VI']['o_que_significa'])
        self.assertNotIn('ofensiva', g['CF88:ART.5:INC.X']['exemplo_pratico'])
        self.assertNotIn('natureza da atividade', g['CF88:ART.5:INC.XIII']['o_que_significa'])
        self.assertIn('forma e o alcance', g['CF88:ART.5:INC.XVI']['o_que_significa'])
        self.assertNotIn('regime jurídico', g['CF88:ART.5:INC.XXXVI']['atencao'])
        self.assertIn('Conselho de Sentença', g['CF88:ART.5:INC.XXXVIII']['o_que_significa'])
        self.assertNotIn('ser assistido por advogado e recorrer', g['CF88:ART.5:INC.LV']['o_que_significa'])
        self.assertNotIn('complexidade', g['CF88:ART.5:INC.LXXVIII']['atencao'])

    def test_covered_target_opens_block(self):
        cases = {'CF88:ART.5:INC.IV': ('CF88:ART.5:INC.IV', 'DIRECT'), 'CF88:ART.5:INC.V': ('CF88:ART.5:INC.IV', 'COVERED_BY_BLOCK'),
                 'CF88:ART.5:INC.IX': ('CF88:ART.5:INC.IV', 'COVERED_BY_BLOCK'), 'CF88:ART.5:INC.XIV': ('CF88:ART.5:INC.IV', 'COVERED_BY_BLOCK')}
        cases.update({f'CF88:ART.5:INC.{i}': ('CF88:ART.5:INC.XVII', 'COVERED_BY_BLOCK') for i in ('XVIII', 'XIX', 'XX', 'XXI')})
        for tid, (anchor, kind) in cases.items():
            r = E.resolve_explanation(tid, self.corpus)
            self.assertEqual((r['matched_target_id'], r['anchor_target_id'], r['resolution_type']), (tid, anchor, kind), tid)
            got = E.lookup_idx(tid, LK, PL)
            self.assertEqual((got['matched_target_id'], got['anchor_target_id'], got['resolution_type']), (tid, anchor, kind), tid)
            self.assertTrue(got['target_id'].startswith('CF88:'))  # namespace intact
        # no covered target is left without ENTENDA
        for r in self.new:
            for c in r['granularity'].get('covered_targets', []):
                self.assertIsNotNone(E.lookup_idx(c, LK, PL), c)
                self.assertIsNotNone(E.resolve_explanation(c, self.corpus), c)
        self.assertIsNone(E.resolve_explanation('CF88:ART.4:INC.I', self.corpus))  # coverage is explicit, never structural inheritance

    def test_display_title(self):
        iv = E.resolve_explanation('CF88:ART.5:INC.V', self.corpus)
        self.assertEqual(iv['display_title'], 'Art. 5º, incisos IV, V, IX e XIV — Liberdade de expressão e informação')
        self.assertEqual(iv['display_targets'], ['CF88:ART.5:INC.IV', 'CF88:ART.5:INC.V', 'CF88:ART.5:INC.IX', 'CF88:ART.5:INC.XIV'])
        self.assertEqual(E.lookup_idx('CF88:ART.5:INC.XIV', LK, PL)['display_title'], iv['display_title'])
        self.assertEqual(E.lookup_idx('CF88:ART.5:INC.XIX', LK, PL)['display_title'], 'Art. 5º, incisos XVII, XVIII, XIX, XX e XXI — Liberdade de associação')
        self.assertEqual(E.lookup_idx('CF88:ART.5:INC.XLV', LK, PL)['display_targets'], ['CF88:ART.5:INC.XLV', 'CF88:ART.5:INC.XLVI'])
        self.assertEqual(E.resolve_explanation('CF88:ART.5:PAR.4', self.corpus)['display_title'], 'Art. 5º, § 4º — Tribunal Penal Internacional')
        for r in self.new:  # every title lists all displayed targets
            t = E.display_title(r)
            for tid in E.display_targets(r):
                self.assertIn(E._last_label(E.T.parse_target_id(tid))[1] or '', t)

    def test_stale_covers_covered_targets(self):
        src = self.ctx.ncfg['text_sources'][0]['path']
        text = E.read_source_bytes(REPO, src).decode('utf-8-sig')
        old = 'é assegurado o direito de resposta, proporcional ao agravo'
        self.assertIn(old, text)
        ctx2 = E.NormContext('CF88').reload_text({src: text.replace(old, 'é assegurado o direito de resposta, na medida do agravo')})
        st = {s['target_id']: s['state'] for s in E.stale_report(self.new, ctx2)}
        self.assertEqual(st['CF88:ART.5:INC.IV'], 'STALE_TEXT_CHANGED')  # covered inciso V changed
        self.assertEqual(st['CF88:ART.5:INC.II'], 'FRESH')
        self.assertTrue(all(s['state'] == 'FRESH' for s in E.stale_report(self.corpus, self.ctx)))

    def test_jurisprudence_separated(self):
        self.assertEqual((self.jur['total'], self.jur['ready_to_link'], self.jur['pending_external_ingestion']), (7, 0, 7))
        wanted = {'CF88:ART.5:INC.X', 'CF88:ART.5:INC.XVI', 'CF88:ART.5:INC.XXXVI', 'CF88:ART.5:INC.LV', 'CF88:ART.5:INC.LVII',
                  'CF88:ART.5:INC.LXVII', 'CF88:ART.5:PAR.3'}
        self.assertEqual({r['target_id'] for r in self.jur['recommendations']}, wanted)
        self.assertTrue(all(not r['local_record_found'] and r['local_reference_id'] is None for r in self.jur['recommendations']))
        for r in self.corpus:  # no leakage in the body
            c = r['content']
            for t in [c[k] for k in E.REQUIRED_TEXT] + [c['atencao'] or ''] + [x['explicacao'] for x in c['palavras_dificeis']]:
                self.assertIsNone(E.EXTERNAL_CASE_RE.search(t), r['target_id'])
        # CAMADA EXTERNA may name references; the body may not
        ok = copy.deepcopy(E.get_explanation('CF88:ART.5:INC.XVI', self.new))
        ok['external_layer_notes'] = ['Ver STF Tema 855 na camada JURISPRUDÊNCIA.']
        self.assertTrue(E.validate_explanation(ok, self.ctx))
        bad = copy.deepcopy(ok)
        bad['content']['atencao'] = 'O STF fixou tese no Tema 855.'
        with self.assertRaises(E.EntendaError) as cm:
            E.validate_explanation(bad, self.ctx)
        self.assertEqual(cm.exception.code, 'ENTENDA_EXTERNAL_CASE_CONTENT')

    def test_lint_section_aware(self):
        r = copy.deepcopy(E.get_explanation('CF88:ART.5:INC.XXXVII', self.new))
        codes = {w['code'] for w in E.lint(r, self.ctx, {})}
        self.assertNotIn('JURISPRUDENCE_WORDING_IN_BODY', codes)  # 'tribunais de exceção' is an ordinary legal term
        r['content']['atencao'] = 'O juiz e o tribunal exercem jurisdição.'
        self.assertNotIn('JURISPRUDENCE_WORDING_IN_BODY', {w['code'] for w in E.lint(r, self.ctx, {})})
        r['content']['atencao'] = 'Há Súmula Vinculante e precedente sobre o tema.'
        self.assertIn('JURISPRUDENCE_WORDING_IN_BODY', {w['code'] for w in E.lint(r, self.ctx, {})})
        r['content']['atencao'] = None
        r['external_layer_notes'] = ['Súmula Vinculante e Repercussão Geral na camada JURISPRUDÊNCIA.']
        self.assertNotIn('JURISPRUDENCE_WORDING_IN_BODY', {w['code'] for w in E.lint(r, self.ctx, {})})
        a2 = E.get_explanation('CF88:ART.2', self.new)
        self.assertNotIn('ABSOLUTE_CLAIM', {w['code'] for w in E.lint(a2, self.ctx, {})})  # 'maioria absoluta' is technical

    def test_invalid_target_fails_closed(self):
        with self.assertRaises(E.EntendaError):
            E.resolve_explanation('CF88/ART.5:INC.V', self.corpus)
        self.assertIsNone(E.lookup_idx('CF88:ART.5:INC.LXXX', LK, PL))
        self.assertIsNone(E.lookup_idx('ADCT:ART.5:INC.V', LK, PL))

    def test_deterministic_output(self):
        tmp = Path(tempfile.mkdtemp(prefix='b01final_'))
        try:
            for run in ('a', 'b'):
                E.build_entenda_index(self.ctx, self.corpus, tmp / run)
            for name in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT', 'ENTENDA_BUILD_MANIFEST.json'):
                self.assertEqual((tmp / 'a' / name).read_bytes(), (tmp / 'b' / name).read_bytes(), name)
                self.assertEqual((tmp / 'a' / name).read_bytes(), (FD / name).read_bytes(), name)
        finally:
            shutil.rmtree(tmp)


if __name__ == '__main__':
    unittest.main()
