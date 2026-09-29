"""Tests for the human-approved ENTENDA CF88 Batch 02 (arts. 6º-17): review, legal status axes, jurisprudence policy, temporal notes."""
import copy
import hashlib
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

FD = HERE / 'derived/production_batch_02_final'
LK, PL = FD / 'ENTENDA_LOOKUP.IDX', FD / 'ENTENDA_PAYLOAD.DAT'
REVOKED = ['CF88:ART.7:INC.XXIX:AL.a', 'CF88:ART.7:INC.XXIX:AL.b', 'CF88:ART.12:PAR.4:INC.II:AL.a', 'CF88:ART.12:PAR.4:INC.II:AL.b']


def _norm_sha(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


@unittest.skipUnless((FD / 'SELECTION_REPORT.json').is_file(), 'final batch 02 not built')
class Batch02FinalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.all = E.load_corpus(FD / 'CF88_BATCH_02_FINAL.entenda.jsonl')
        cls.new = [r for r in cls.all if r['status'] == 'ACTIVE']
        cls.rep = json.loads((FD / 'SELECTION_REPORT.json').read_text(encoding='utf-8'))
        cls.rows = {r['target_id']: r for r in cls.rep['selection']}
        cls.dec = json.loads((FD / 'HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        cls.jur = json.loads((FD / 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json').read_text(encoding='utf-8'))
        cls.tmp = json.loads((FD / 'TEMPORAL_NOTES.json').read_text(encoding='utf-8'))
        cls.by = {r['target_id']: r for r in cls.new}

    def test_totals_and_review(self):
        self.assertEqual(len(self.new), 50)
        self.assertIn('CF88:ART.7:INC.XII', self.by)
        self.assertIn('CF88:ART.8:INC.I', self.by)
        self.assertTrue(all(r['review_status'] == 'HUMAN_APPROVED_T1' for r in self.new))
        self.assertFalse([r for r in self.all if r['review_status'] == 'PENDING_HUMAN_REVIEW'])
        self.assertEqual((self.dec['review_status'], self.dec['review_date']), ('HUMAN_REVIEW_COMPLETED', '2026-09-28'))
        self.assertEqual(len(self.dec['decisions']), 50)
        retired = [r for r in self.all if r['status'] == 'RETIRED']
        self.assertEqual(len(retired), self.dec['decision_counts']['APPROVED_AFTER_ADJUSTMENT'])
        original = {e['target_id']: e['content'] for e in json.loads((HERE / 'derived/production_batch_02/BATCH_02_DRAFTS.json').read_text(encoding='utf-8'))['explanations']}
        for r in retired:
            self.assertEqual(r['content'], original[r['target_id']])  # evidence preserved
        E.validate_corpus(self.new, self.ctx)

    def test_batch01_immutable(self):
        b01 = HERE / 'derived/production_batch_01_final'
        corpus = E.load_corpus(b01 / 'CF88_BATCH_01_FINAL.entenda.jsonl')
        self.assertEqual(len([r for r in corpus if r['status'] == 'ACTIVE']), 53)
        self.assertTrue(all(r['review_status'] == 'HUMAN_APPROVED_T1' for r in corpus if r['status'] == 'ACTIVE'))
        tmp = Path(tempfile.mkdtemp(prefix='b01chk_'))
        try:
            reused = [r for r in E.load_corpus(HERE / 'corpus/CF88.entenda.jsonl') if r['status'] == 'ACTIVE' and r['target_id'] in ('CF88:ART.1', 'CF88:ART.5')]
            E.build_entenda_index(self.ctx, reused + [r for r in corpus if r['status'] == 'ACTIVE'], tmp)
            for name in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT', 'ENTENDA_BUILD_MANIFEST.json'):
                self.assertEqual(_norm_sha(tmp / name), _norm_sha(b01 / name), name)
        finally:
            shutil.rmtree(tmp)

    def test_block_lookup_and_titles(self):
        got = E.lookup_idx('CF88:ART.7:INC.V', LK, PL)
        self.assertEqual((got['anchor_target_id'], got['resolution_type']), ('CF88:ART.7:INC.IV', 'COVERED_BY_BLOCK'))
        self.assertEqual(E.lookup_idx('CF88:ART.7:INC.XII', LK, PL)['display_title'], 'Art. 7º, inciso XII — Salário-família')
        self.assertEqual(E.lookup_idx('CF88:ART.8:INC.I', LK, PL)['display_title'], 'Art. 8º, inciso I — Liberdade sindical: registro não é autorização')
        self.assertEqual(E.lookup_idx('CF88:ART.12:PAR.5', LK, PL)['display_title'], 'Art. 12, §§ 4º e 5º — Perda e reaquisição da nacionalidade')
        self.assertEqual(self.rows['CF88:ART.7:INC.XII']['classification'], 'ITEM')
        self.assertEqual(self.rows['CF88:ART.8:INC.I']['classification'], 'ITEM')

    def test_revoked_axis(self):
        for t in REVOKED:
            self.assertTrue(self.ctx.structurally_present(t))
            self.assertEqual((self.ctx.legal_status(t), self.ctx.legally_current(t)), ('REVOKED', False))
            row = self.rows[t]
            self.assertEqual((row['classification'], row['structurally_present'], row['legal_status'], row['legally_current']),
                             ('EXCLUDED_REVOKED', True, 'REVOKED', False))
            self.assertIsNone(E.lookup_idx(t, LK, PL))
            self.assertIsNone(E.resolve_explanation(t, self.new))
        s = self.rep['summary']
        self.assertEqual((s['targets_structurally_present'], s['targets_revoked']), (151, 4))
        self.assertEqual(s['targets_legally_current'], 147)
        self.assertEqual(s['targets_current'], 147)  # CURRENT count excludes revoked
        bad = copy.deepcopy(self.by['CF88:ART.7:INC.XXIX'])
        bad.update(target_id=REVOKED[0], explanation_id=E.explanation_id(REVOKED[0], 'BASE', 1), explanation_key=E.explanation_key(REVOKED[0]),
                   editorial_version=1)
        bad['granularity'].update(target_kind='ALINEA', role='ITEM', context_targets=self.ctx.context_chain(REVOKED[0]))
        bad['validity']['target_status'] = 'REVOKED'
        with self.assertRaises(E.EntendaError) as cm:
            E.validate_explanation(bad, self.ctx)
        self.assertEqual(cm.exception.code, 'ENTENDA_REVOKED_NOT_ALLOWED')

    def test_jurisprudence_requires_subject_verification(self):
        self.assertEqual(self.jur['schema_version'], 2)
        for r in self.jur['recommendations']:
            if r['status'] == 'READY_TO_LINK':
                v = r['subject_verification']
                self.assertTrue(v['verified'] and not v['missing_keywords'] and v['official_source_sha256'] and r['already_linked_to_target'])
            elif r['status'] == 'PENDING_EXTERNAL_INGESTION':
                self.assertFalse(r['local_record_found'])
        tema1229 = next(r for r in self.jur['recommendations'] if r['local_identity_searched'] == 'STF:RG:1229')
        self.assertEqual(tema1229['status'], 'PENDING_EXTERNAL_INGESTION')
        self.assertIn('human_supplied', tema1229)
        # identity present locally but subject not proven -> not READY
        spec = dict(batch_id='fixture', jurisprudence_recommendations=[
            dict(target_id='CF88:ART.8:INC.IV', desired_reference='x', purpose='x', local_identity='STF:SV:40', subject_keywords=['assistencial']),
            dict(target_id='CF88:ART.8:INC.IV', desired_reference='x', purpose='x', local_identity='STF:SV:40', subject_keywords=[]),
            dict(target_id='CF88:ART.8:INC.IV', desired_reference='x', purpose='x', local_identity='STF:SV:40', subject_keywords=['confederativa', 'filiados'])])
        ex = json.loads((HERE.parent / 'LEGAL_TARGET_ID/derived/export_test/run1/CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))
        local = {}
        for tid, links in ex['references'].items():
            for l in links:
                if l['reference_type'] == 'JURISPRUDENCE':
                    local.setdefault(l['source_id'], []).append(dict(target_id=tid, reference_id=l['reference_id'], label=l['label']))
        got = [r['status'] for r in P.jurisprudence_recommendations_v2(spec, self.ctx, local)['recommendations']]
        catalog_available = bool(P._catalog(self.ctx))
        self.assertEqual(got[:2], ['IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION'] * 2)
        self.assertEqual(got[2], 'READY_TO_LINK' if catalog_available else 'IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION')

    def test_temporal_notes(self):
        self.assertEqual(self.tmp['as_of'], '2026-09-28')
        ids = {n['note_id']: n for n in self.tmp['notes']}
        self.assertEqual(set(ids), {'LICENCA_PATERNIDADE_LEI_15371_2026', 'IDADE_MINIMA_AFERICAO_LEI_9504_ART11_PAR2', 'CLAUSULA_DESEMPENHO_TRANSICAO_ELEICOES_2026'})
        lp = ids['LICENCA_PATERNIDADE_LEI_15371_2026']
        self.assertEqual((lp['state'], lp['review_due'], lp['target_id']), ('NOT_YET_EFFECTIVE', False, 'CF88:ART.7:INC.XVIII'))
        self.assertEqual(E.temporal_state(lp['note'], '2027-01-01'), dict(state='IN_EFFECT', review_due=True))
        rec = self.by['CF88:ART.7:INC.XVIII']
        self.assertEqual((rec['temporal']['effective_change_date'], rec['temporal']['future_legislation']), ('2027-01-01', 'Lei 15.371/2026'))
        body = ' '.join(rec['content'][k] or '' for k in ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao'))
        self.assertNotIn('15.371', body)  # the future law is not presented as the constitutional/current regime
        self.assertIn('sem fixar no inciso XIX a sua duração', body)
        got = E.lookup_idx('CF88:ART.7:INC.XVIII', LK, PL)
        self.assertIn('NOTAS TEMPORAIS', got['sections'])
        cl = self.by['CF88:ART.17:PAR.3']['temporal']
        self.assertEqual((cl['temporal_scope'], cl['next_rule_change']), ('ELEICOES_2026', 'ELEICOES_2030'))
        self.assertIn('2030', self.by['CF88:ART.17:PAR.3']['content']['atencao'])
        for bad in (dict(time_sensitive=True, notes=[dict(note_id='x', text='t', source_type='LEI', source_id='y', review_after='2027-13')]),
                    dict(time_sensitive=True, notes=[]), dict(time_sensitive='yes', notes=[{}])):
            with self.assertRaises(E.EntendaError):
                E.validate_temporal(bad)

    def test_editorial_corrections(self):
        g = {t: r['content'] for t, r in self.by.items()}
        self.assertNotIn('voltar a ser brasileiro nato', g['CF88:ART.12:PAR.4']['o_que_significa'])
        self.assertIn('possuía nacionalidade brasileira originária', g['CF88:ART.12:PAR.4']['o_que_significa'])
        self.assertNotIn('situação definitiva', g['CF88:ART.15']['o_que_significa'])
        self.assertNotIn('temporária', g['CF88:ART.15']['o_que_significa'])
        self.assertNotIn('restabelecidos', g['CF88:ART.15']['exemplo_pratico'])
        self.assertNotIn('multa sobre os depósitos', g['CF88:ART.7:INC.I']['o_que_significa'])
        self.assertIn('art. 61, § 2º', g['CF88:ART.14:CAPUT']['exemplo_pratico'])
        self.assertNotIn('órgão colegiado', g['CF88:ART.14:PAR.9']['exemplo_pratico'])
        self.assertNotIn('com liberdade', g['CF88:ART.17:PAR.1']['o_que_significa'])

    def test_invalid_target_fails_closed(self):
        with self.assertRaises(E.EntendaError):
            E.resolve_explanation('CF88/ART.7', self.new)
        self.assertIsNone(E.lookup_idx('CF88:ART.7:INC.XXXV', LK, PL))
        self.assertIsNone(E.lookup_idx('CF88:ART.18', LK, PL))

    def test_deterministic(self):
        tmp = Path(tempfile.mkdtemp(prefix='b02final_'))
        try:
            for run in ('a', 'b'):
                E.build_entenda_index(self.ctx, self.new, tmp / run)
            for name in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT', 'ENTENDA_BUILD_MANIFEST.json'):
                self.assertEqual((tmp / 'a' / name).read_bytes(), (tmp / 'b' / name).read_bytes(), name)
                self.assertEqual(_norm_sha(tmp / 'a' / name), _norm_sha(FD / name), name)
            self.assertEqual(E.temporal_report(self.new, '2026-09-28'), self.tmp['notes'])
        finally:
            shutil.rmtree(tmp)


if __name__ == '__main__':
    unittest.main()
