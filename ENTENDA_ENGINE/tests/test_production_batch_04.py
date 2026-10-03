"""Tests for ENTENDA CF PRODUCTION BATCH 04 (arts. 25-36), pending human review."""
import hashlib
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

BD = HERE / 'derived/production_batch_04'
LK, PL = BD / 'index/ENTENDA_LOOKUP.IDX', BD / 'index/ENTENDA_PAYLOAD.DAT'
RUNTIME = HERE.parent / 'DEVICE_INTEGRATION/runtime/CF88_RUNTIME.txt'
PRIOR = ('derived/production_batch_01_final/CF88_BATCH_01_FINAL.entenda.jsonl',
         'derived/production_batch_02_final/CF88_BATCH_02_FINAL.entenda.jsonl',
         'derived/production_batch_03_final/CF88_BATCH_03_FINAL.entenda.jsonl')
ROUND1_ADJUSTED = {'CF88:ART.25', 'CF88:ART.25:PAR.2', 'CF88:ART.25:PAR.3', 'CF88:ART.26:INC.I', 'CF88:ART.26:INC.IV', 'CF88:ART.27:PAR.1'}
ROUND3_ADJUSTED = {'CF88:ART.32:PAR.1', 'CF88:ART.32:PAR.4', 'CF88:ART.33', 'CF88:ART.34', 'CF88:ART.34:INC.IV', 'CF88:ART.34:INC.VII',
                   'CF88:ART.35:INC.I', 'CF88:ART.36:INC.I', 'CF88:ART.36:PAR.3'}
ROUND2_ADJUSTED = {'CF88:ART.29:INC.X', 'CF88:ART.29-A', 'CF88:ART.29-A:INC.I', 'CF88:ART.29-A:PAR.1', 'CF88:ART.30', 'CF88:ART.30:INC.IX'}
PILOTS = ('CF88:ART.37', 'CF88:ART.37:PAR.6', 'CF88:ART.37:PAR.10', 'CF88:ART.60', 'CF88:ART.60:PAR.4',
          'CF88:ART.60:PAR.4:INC.IV', 'CF88:ART.150', 'CF88:ART.225', 'ADCT:ART.10:INC.II')


def _body(r):
    c = r['content']
    return ' '.join([c[k] for k in E.REQUIRED_TEXT] + [c['atencao'] or ''] + [t['explicacao'] for t in c['palavras_dificeis']])


@unittest.skipUnless((BD / 'SELECTION_REPORT.json').is_file(), 'batch 04 not built')
class Batch04Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        spec = json.loads((BD / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
        cls.ctx.ncfg = dict(cls.ctx.ncfg, reference_export=spec['reference_export'])   # same export the batch was built with
        cls.all = E.load_corpus(BD / 'CF88_BATCH_04.entenda.jsonl')
        cls.new = [r for r in cls.all if r['status'] == 'ACTIVE']
        cls.by = {r['target_id']: r for r in cls.new}
        cls.rep = json.loads((BD / 'SELECTION_REPORT.json').read_text(encoding='utf-8'))
        cls.rows = {r['target_id']: r for r in cls.rep['selection']}
        cls.spec = json.loads((BD / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
        cls.jur = json.loads((BD / 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json').read_text(encoding='utf-8'))
        cls.plan = json.loads((BD / 'BATCH04_TARGET_PLAN.json').read_text(encoding='utf-8'))

    def test_scope_counts_and_pending(self):
        self.assertEqual(self.spec['scope'][0], 'CF88:ART.25')
        self.assertEqual(self.spec['scope'][-1], 'CF88:ART.36')
        scope = [t for a in self.spec['scope'] for t in self.ctx.subtree(a)]
        self.assertEqual(sorted(self.rows), sorted(scope))
        s = self.rep['summary']
        self.assertEqual((s['targets_evaluated'], s['targets_legally_current'], s['targets_revoked'], s['historical_excluded']),
                         (142, 140, 1, 1))
        self.assertEqual(len(self.new), 57)
        self.assertLessEqual(len(self.new), self.spec['hard_cap'])
        self.assertTrue(all(r['review_status'] == 'HUMAN_APPROVED_T1' for r in self.new))   # Rounds 1 (13) + 2 (24) + 3 (20)
        self.assertEqual(s['review_status_counts'], {'HUMAN_APPROVED_T1': 57})

    def test_targets_in_scope_current_and_excluded(self):
        scope = {t for a in self.spec['scope'] for t in self.ctx.subtree(a)}
        for r in self.new:
            for t in [r['target_id']] + r['granularity'].get('covered_targets', []):
                self.assertIn(t, scope, t)
                self.assertTrue(self.ctx.legally_current(t), t)
        self.assertFalse(any(re.match(r'CF88:ART\.(37|[4-9]\d|\d{3})\b', t) for t in self.rows))
        self.assertEqual(self.rows['CF88:ART.36:INC.IV']['classification'], 'EXCLUDED_REVOKED')
        self.assertEqual(self.rows['CF88:ART.28:PAR.UNICO']['classification'], 'EXCLUDED_HISTORICAL')

    def test_source_hash_valid_and_runtime_identical(self):
        self.assertEqual(hashlib.sha256(RUNTIME.read_bytes()).hexdigest(), self.plan['text_base']['runtime_sha256'])
        self.assertEqual(self.plan['text_base']['per_target_text_equal_to_runtime'], '142/142')
        for r in self.new:
            s = r['source']
            self.assertEqual(E.sha256(s['source_text_snapshot']), s['source_text_sha256'], r['target_id'])
            self.assertEqual(s['source_text_snapshot'], self.ctx.snapshot(r['target_id'], r['granularity'].get('covered_targets', [])))
        self.assertEqual([x for x in E.stale_report(self.new, self.ctx) if x['state'] != 'FRESH'], [])

    def test_blocks_covered_and_no_collisions(self):
        own = set(self.by)
        cov = [c for r in self.new for c in r['granularity'].get('covered_targets', [])]
        self.assertEqual(len(cov), len(set(cov)))
        self.assertFalse(set(cov) & own)
        for r in self.new:
            self.assertEqual(r['granularity'].get('anchor_target_id', r['target_id']), r['target_id'])
            for t in r['granularity'].get('covered_targets', []):
                got = E.lookup_idx(t, LK, PL)
                self.assertEqual((got['anchor_target_id'], got['resolution_type']), (r['target_id'], 'COVERED_BY_BLOCK'), t)
        for r in self.rows.values():
            if r['classification'] == 'NO_SEPARATE_EXPLANATION':
                self.assertIn(r['covered_by'], own, r['target_id'])
        prior = {r['explanation_key'] for p in PRIOR + ('corpus/CF88.entenda.jsonl',) for r in E.load_corpus(HERE / p)}
        self.assertFalse(prior & {r['explanation_key'] for r in self.new})
        self.assertEqual(len({r['explanation_id'] for r in self.new}), 57)
        self.assertFalse(set(PILOTS) & own)

    def test_editorial_distinctions(self):
        self.assertIn('Autonomia não é soberania', self.by['CF88:ART.25']['content']['o_que_significa'])
        s30 = self.by['CF88:ART.30']['content']['o_que_significa']
        self.assertIn('competência legislativa', s30)
        self.assertIn('competências administrativas', s30)
        self.assertIn('Interesse local não quer dizer qualquer assunto', self.by['CF88:ART.30']['content']['atencao'])
        for r in self.new:
            self.assertNotRegex(_body(r), r'(?i)legislar sobre qualquer assunto', r['target_id'])
        s34 = self.by['CF88:ART.34']['content']['o_que_significa']
        self.assertIn('A regra é a autonomia', s34)
        self.assertIn('taxativa', s34)
        self.assertIn('art. 35', self.by['CF88:ART.34']['content']['atencao'])
        self.assertIn('não é o julgamento final', self.by['CF88:ART.31:PAR.2']['content']['atencao'])
        self.assertIn('A Constituição admite a existência de Territórios Federais', self.by['CF88:ART.33']['content']['o_que_significa'])

    def test_jurisprudence_statuses_and_mismatches(self):
        st = {}
        for r in self.jur['recommendations']:
            st.setdefault(r['status'], []).append(r)
        self.assertEqual({k: len(v) for k, v in st.items()},
                         {'READY_TO_LINK': 1, 'PENDING_EXTERNAL_INGESTION': 8, 'MATERIAL_MISMATCH_EXCLUDED': 2})
        mm = {(r['target_id'], r['local_identity_searched']) for r in st['MATERIAL_MISMATCH_EXCLUDED']}
        self.assertEqual(mm, {('CF88:ART.25', 'STF:RG:113'), ('CF88:ART.31:PAR.3', 'STF:RG:756')})
        (ready,) = st['READY_TO_LINK']
        self.assertEqual((ready['target_id'], ready['primary_target_id']), ('CF88:ART.30:INC.I', 'CF88:ART.24:INC.VI'))
        self.assertTrue(ready['subject_verification']['verified'])
        for r in self.new:
            self.assertIsNone(E.EXTERNAL_CASE_RE.search(_body(r)), r['target_id'])

    def test_pre_review_sanitization(self):
        """Decisions of 2026-10-01: EC 139/2026 (art. 31, § 1º), EC 111/2021 (art. 28), art. 29, XIV, EC 107/2020, Temas 113/756."""
        self.assertEqual(self.spec['reference_export'], 'LEGAL_TARGET_ID/derived/export_test/run2/CF88_REFERENCES_EXPORT.json')
        self.assertIn('Emenda Constitucional nº 139, de 05/05/2026', ' '.join(self.by['CF88:ART.31:PAR.1']['external_layer_notes']))
        (note,) = self.by['CF88:ART.28']['temporal']['notes']
        self.assertEqual((note['note_id'], note['source_id'], note['effective_change_date']), ('ART28_POSSE_6_JANEIRO_EC111_2021', 'EC 111/2021', '2027-01-06'))
        self.assertIn('a partir das eleições de 2026', note['text'])
        self.assertNotIn('2022', json.dumps(self.by['CF88:ART.28'], ensure_ascii=False))
        self.assertNotIn('Emenda', _body(self.by['CF88:ART.28']))                         # transition stays outside the body
        self.assertIn('corresponde ao § 1º do art. 28', self.by['CF88:ART.29:INC.XIV']['content']['atencao'])
        self.assertIn('Nota histórica', ' '.join(self.by['CF88:ART.29:INC.I']['external_layer_notes']))
        self.assertNotIn('107', _body(self.by['CF88:ART.29:INC.I']))
        plan = self.plan['vigency_findings']
        self.assertEqual((plan['ART31_PAR1_SOURCE_CHANGE'], plan['ART28_POSSE_6_JANEIRO'], plan['ART28_POSSE_APLICACAO'], plan['runtime_changed']),
                         ('EC_139_2026', 'EC_111_2021', 'ELEICOES_2026_EM_DIANTE', False))
        for r in self.jur['recommendations']:
            if r['status'] == 'MATERIAL_MISMATCH_EXCLUDED':
                (x,) = r['excluded_local_links']
                self.assertEqual((x['target_id'], x['local_link_present']), (r['target_id'], False))   # gone from the corrected export

    def test_review_rounds_full_text(self):
        rounds = ('REVIEW_BATCH_04_ROUND_1_ART25_28.md', 'REVIEW_BATCH_04_ROUND_2_ART29_31.md', 'REVIEW_BATCH_04_ROUND_3_ART32_36.md')
        texts = [(BD / f).read_text(encoding='utf-8') for f in rounds]
        self.assertEqual([t.count('[ ] APROVAR') for t in texts], [0, 0, 0])
        self.assertEqual([t.count('[x] APROVAR') for t in texts], [13, 24, 20])
        allt = '\n'.join(texts)
        for r in self.new:
            self.assertIn(f"`{r['target_id']}`", allt)
            for k in E.REQUIRED_TEXT:
                for para in r['content'][k].split('\n'):
                    self.assertIn(para, allt, r['target_id'])

    def _drafts(self, name):
        return {e['target_id']: e for e in json.loads((BD / name).read_text(encoding='utf-8'))['explanations']}

    def test_round1_assisted_approval(self):
        """Round 1 (arts. 25-28): exactly the six authorized adjustments; seven unchanged; nothing else touched."""
        dec = json.loads((BD / 'ROUND_1_HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual((dec['review_status'], dec['review_scope'], dec['decision_counts']),
                         ('ROUND_REVIEW_COMPLETED', 'CF88_ARTS_25_28_ROUND_1', {'APPROVED': 7, 'APPROVED_AFTER_ADJUSTMENT': 6}))
        adjusted = {d['target_id'] for d in dec['decisions'] if d['changes']}
        self.assertEqual(adjusted, ROUND1_ADJUSTED)
        pre, post = self._drafts('BATCH_04_DRAFTS_PRE_ROUND1.json'), self._drafts('BATCH_04_DRAFTS_PRE_ROUND2.json')
        self.assertEqual({t for t in pre if pre[t]['content'] != post[t]['content']}, adjusted)
        for t in pre:
            if t not in {d['target_id'] for d in dec['decisions']}:
                self.assertEqual(pre[t], post[t], t)
        self.assertNotIn('voltou', _body(self.by['CF88:ART.26:INC.IV']))
        self.assertNotIn('valem enquanto ele exerce o mandato', _body(self.by['CF88:ART.27:PAR.1']))
        self.assertIn('pode depender de autorização do poder público', self.by['CF88:ART.26:INC.I']['content']['exemplo_pratico'])

    def test_art26_iv_cleanup_and_round2_approval(self):
        """Cleanup of art. 26, IV (only the unused term) and Round 2 (arts. 29-31): exactly the six authorized adjustments."""
        cl = json.loads((BD / 'ART26_IV_CLEANUP_DECISIONS.json').read_text(encoding='utf-8'))
        (d,) = cl['decisions']
        self.assertEqual((d['target_id'], d['changed_sections'], d['changes'][0]['kind'], d['changes'][0].get('removed')),
                         ('CF88:ART.26:INC.IV', ['palavras_dificeis'], 'EDITORIAL_CLEANUP_NO_SEMANTIC_CHANGE', True))
        self.assertNotIn('Ação discriminatória', [t['termo'] for t in self.by['CF88:ART.26:INC.IV']['content']['palavras_dificeis']])
        a, b = self._drafts('BATCH_04_DRAFTS_PRE_ROUND2.json'), self._drafts('BATCH_04_DRAFTS_ART26_IV_CLEANUP.json')
        self.assertEqual({t for t in a if a[t] != b[t]}, {'CF88:ART.26:INC.IV'})
        self.assertEqual({k for k in a['CF88:ART.26:INC.IV']['content'] if a['CF88:ART.26:INC.IV']['content'][k] != b['CF88:ART.26:INC.IV']['content'][k]},
                         {'palavras_dificeis'})
        dec = json.loads((BD / 'ROUND_2_HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual((dec['review_status'], dec['review_scope'], dec['decision_counts']),
                         ('ROUND_REVIEW_COMPLETED', 'CF88_ARTS_29_31_ROUND_2', {'APPROVED': 18, 'APPROVED_AFTER_ADJUSTMENT': 6}))
        adjusted = {d['target_id'] for d in dec['decisions'] if d['changes']}
        self.assertEqual(adjusted, ROUND2_ADJUSTED)
        post = self._drafts('BATCH_04_DRAFTS_PRE_ROUND3.json')
        changed = {t for t in b if (b[t]['content'], b[t].get('external_layer_notes')) != (post[t]['content'], post[t].get('external_layer_notes'))}
        self.assertEqual(changed, adjusted)
        for t in b:
            if t not in {d['target_id'] for d in dec['decisions']}:
                self.assertEqual(b[t], post[t], t)                                         # Round 1 and Round 3 untouched by Round 2
        retired = [r for r in self.all if r['status'] == 'RETIRED']
        self.assertEqual(sorted(r['explanation_id'] for r in retired), sorted(
            [f'ENTENDA/{t}/BASE/1' for t in ROUND1_ADJUSTED | ROUND2_ADJUSTED | ROUND3_ADJUSTED] + ['ENTENDA/CF88:ART.26:INC.IV/BASE/2',
                                                                                           'ENTENDA/CF88:ART.34/BASE/2',
                                                                                           'ENTENDA/CF88:ART.35/BASE/1']))
        self.assertEqual(self.by['CF88:ART.26:INC.IV']['editorial_version'], 3)
        for r in self.new:
            if r['review_status'] == 'HUMAN_APPROVED_T1':
                hr = r['human_review']
                self.assertEqual((hr['approval_method'], hr['reviewer_decision']),
                                 ('ASSISTED_RISK_BASED_HUMAN_REVIEW', 'ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW'))
        x = self.by['CF88:ART.29:INC.X']
        self.assertNotIn('merenda', _body(x))
        self.assertIn('Súmula 702', ' '.join(x['external_layer_notes']))
        self.assertIn('HC 232627', ' '.join(x['external_layer_notes']))
        self.assertIsNone(E.EXTERNAL_CASE_RE.search(_body(x)))                           # precedents only in the external layer
        i = self.by['CF88:ART.29-A:INC.I']['content']
        for f in ('7% até 100.000', '6% entre 100.000 e 300.000', '5% entre 300.001 e 500.000', '4,5% entre 500.001 e 3.000.000',
                  '4% entre 3.000.001 e 8.000.000', '3,5% acima de 8.000.001'):
            self.assertIn(f, i['o_que_diz'])
        self.assertIn('fronteiras numéricas atípicas', i['atencao'])
        for w in ('erro', 'inconstitucional', 'lapso'):
            self.assertNotIn(w, i['atencao'].lower())
        self.assertIn('não possui poder tributário próprio', self.by['CF88:ART.29-A']['content']['o_que_significa'])
        self.assertIn('inativos e pensionistas', self.by['CF88:ART.29-A']['content']['o_que_diz'])
        self.assertNotIn('no mínimo, ficam para despesas', _body(self.by['CF88:ART.29-A:PAR.1']))
        self.assertIn('não é absoluta', self.by['CF88:ART.30']['content']['o_que_significa'])
        self.assertIn('Emenda Constitucional nº 139', ' '.join(self.by['CF88:ART.31:PAR.1']['external_layer_notes']))

    def test_round3_approval(self):
        """Round 3 (arts. 32-36): exactly the nine authorized adjustments; eleven unchanged; Rounds 1 and 2 untouched."""
        dec = json.loads((BD / 'ROUND_3_HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual((dec['review_status'], dec['review_scope'], dec['decision_counts']),
                         ('ROUND_REVIEW_COMPLETED', 'CF88_ARTS_32_36_ROUND_3', {'APPROVED': 11, 'APPROVED_AFTER_ADJUSTMENT': 9}))
        self.assertEqual({d['target_id'] for d in dec['decisions'] if d['changes']}, ROUND3_ADJUSTED)
        a, b = self._drafts('BATCH_04_DRAFTS_PRE_ROUND3.json'), self._drafts('BATCH_04_DRAFTS.json')
        changed = {t for t in a if (a[t]['content'], a[t].get('external_layer_notes'), a[t].get('temporal')) !=
                   (b[t]['content'], b[t].get('external_layer_notes'), b[t].get('temporal'))}
        # later glossary cleanup (ART35_GLOSSARY_CLEANUP): only PALAVRAS DIFICEIS of art. 35 differs from the Round 3 text
        strip = lambda e: ({k: v for k, v in e['content'].items() if k != 'palavras_dificeis'}, e.get('external_layer_notes'), e.get('temporal'))  # noqa: E731
        self.assertEqual(strip(a['CF88:ART.35']), strip(b['CF88:ART.35']))
        self.assertEqual(changed - {'CF88:ART.35'}, ROUND3_ADJUSTED)
        for t in a:
            if t not in {d['target_id'] for d in dec['decisions']}:
                self.assertEqual(a[t], b[t], t)
        t33 = self.by['CF88:ART.33']
        self.assertNotIn('Hoje não existe', _body(t33))
        self.assertNotIn('nenhum está instalado', _body(t33))
        (n,) = t33['temporal']['notes']
        self.assertEqual((n['source_id'], n['factual_temporal_note'], n['review_on_territorial_change']), ('IBGE', True, True))
        self.assertIn('26 Estados e o Distrito Federal', n['text'])
        i = self.by['CF88:ART.36:INC.I']
        self.assertNotIn('graus diferentes de vinculação', _body(i))
        self.assertNotIn('força de ordem', _body(i))
        self.assertIn('ADI 2167', ' '.join(i['external_layer_notes']))
        self.assertEqual(i['granularity']['covered_targets'], ['CF88:ART.36:INC.II', 'CF88:ART.36:INC.III'])
        self.assertEqual(self.rows['CF88:ART.36:INC.IV']['classification'], 'EXCLUDED_REVOKED')
        self.assertNotIn('pode ser decretada', _body(self.by['CF88:ART.34:INC.VII']))
        self.assertNotIn('Falhas pontuais', _body(self.by['CF88:ART.35:INC.I']))
        self.assertEqual(self.by['CF88:ART.35:INC.IV']['editorial_version'], 1)                 # provenance only, text unchanged
        ov = [r for r in self.jur['recommendations'] if r['target_id'] in ('CF88:ART.35:INC.IV', 'CF88:ART.36:INC.I')]
        self.assertEqual(len(ov), 2)
        self.assertTrue(all(r['official_verification']['identity_officially_verified'] and r['status'] == 'PENDING_EXTERNAL_INGESTION' for r in ov))

    def test_official_verifications_without_invented_ingestion(self):
        ov = {(r['target_id'], r['local_identity_searched']): r for r in self.jur['recommendations'] if r.get('official_verification')}
        for k in (('CF88:ART.29:INC.X', 'STF:SUMULA:702'), ('CF88:ART.29:INC.X', None), ('CF88:ART.29-A:PAR.2', 'STF:SV:46'),
                  ('CF88:ART.31:PAR.2', 'STF:RG:157'), ('CF88:ART.31:PAR.2', 'STF:RG:835')):
            r = ov[k]
            self.assertEqual((r['status'], r['official_verification']['identity_officially_verified'], r['local_reference_id']),
                             ('PENDING_EXTERNAL_INGESTION', True, None), k)
        self.assertEqual(ov[('CF88:ART.30:INC.I', 'STF:RG:145')]['status'], 'READY_TO_LINK')

    def test_partial_round_fails_closed(self):
        import apply_batch_review as A
        import production_batch as P
        tmp = Path(tempfile.mkdtemp(prefix='b04_round_'))
        try:
            for n in ('BATCH_04_DRAFTS.json', 'BATCH_SPEC.json', 'ROUND_1_HUMAN_REVIEW_DECISIONS.json', 'ART26_IV_CLEANUP_DECISIONS.json',
                      'ROUND_2_HUMAN_REVIEW_DECISIONS.json', 'ROUND_3_HUMAN_REVIEW_DECISIONS.json', 'ART34_GLOSSARY_CLEANUP_DECISIONS.json',
                      'ART35_GLOSSARY_CLEANUP_DECISIONS.json',
                      'CF88_BATCH_04.entenda.jsonl'):
                shutil.copyfile(BD / n, tmp / n)
            # a review of a target that is not in the drafts is refused
            spec = dict(batch_id='X', review_scope='X', partial_round=True, original_drafts='BATCH_04_DRAFTS.json', reviewed_drafts_out='out.json',
                        decisions_out=['d.json'], human_review=dict(reviewed_on='2026-10-01'),
                        reviews=[dict(target_id='CF88:ART.99', decision='APPROVED', review_reason='x')])
            (tmp / 'spec.json').write_text(json.dumps(spec), encoding='utf-8')
            with self.assertRaises(SystemExit):
                A.apply(tmp / 'spec.json')
            # explanations marked approved without a recorded round decision are refused by the batch build
            sp = json.loads((tmp / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
            sp['round_approvals'] = [r for r in sp['round_approvals'] if r['review_scope'] != 'CF88_ARTS_32_36_ROUND_3']
            (tmp / 'BATCH_SPEC.json').write_text(json.dumps(sp, ensure_ascii=False), encoding='utf-8')
            with self.assertRaises(P.BatchError) as cm:
                P.run(tmp)
            self.assertEqual(cm.exception.code, 'BATCH_REVIEW_STATUS_MISMATCH')
        finally:
            shutil.rmtree(tmp)

    def test_art34_glossary_cleanup(self):
        # CONSOLIDATION_FINAL_PREDEPLOY: only the PALAVRAS DIFICEIS entry of art. 34 aligned to the approved text ("restringe")
        cur = {r['target_id']: r for r in self.all if r['status'] == 'ACTIVE'}
        e = cur['CF88:ART.34']
        self.assertEqual(e['explanation_id'], 'ENTENDA/CF88:ART.34/BASE/3')
        term = [t for t in e['content']['palavras_dificeis'] if t['termo'] == 'Intervenção federal']
        self.assertEqual(term[0]['explicacao'], 'medida excepcional em que a União restringe temporariamente a autonomia de um Estado ou do Distrito Federal.')
        self.assertIn('restringe temporariamente', e['content']['o_que_significa'])
        self.assertNotIn('suspende temporariamente', json.dumps(e['content'], ensure_ascii=False))
        prev = [r for r in self.all if r['explanation_id'] == 'ENTENDA/CF88:ART.34/BASE/2'][0]
        self.assertEqual(prev['status'], 'RETIRED')
        self.assertEqual({k: v for k, v in prev['content'].items() if k != 'palavras_dificeis'},
                         {k: v for k, v in e['content'].items() if k != 'palavras_dificeis'})   # nothing else changed
        dec = json.loads((BD / 'ART34_GLOSSARY_CLEANUP_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual([d['target_id'] for d in dec['decisions']], ['CF88:ART.34'])
        self.assertEqual(dec['decisions'][0]['changed_sections'], ['palavras_dificeis'])
        self.assertEqual(e['human_review']['approval_method'], 'ASSISTED_RISK_BASED_HUMAN_REVIEW')
        self.assertEqual(e['human_review']['reviewer_decision'], 'ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW')

    def test_art35_glossary_cleanup(self):
        # CONSOLIDATION_FINAL_PREDEPLOY (additional authorization): only the PALAVRAS DIFICEIS entry of art. 35
        cur = {r['target_id']: r for r in self.all if r['status'] == 'ACTIVE'}
        e = cur['CF88:ART.35']
        self.assertEqual(e['explanation_id'], 'ENTENDA/CF88:ART.35/BASE/2')
        term = [t for t in e['content']['palavras_dificeis'] if t['termo'] == 'Intervenção estadual']
        self.assertEqual(term[0]['explicacao'], 'medida excepcional em que o Estado restringe temporariamente a autonomia do Município, '
                                                'nos limites necessários à intervenção.')
        prev = [r for r in self.all if r['explanation_id'] == 'ENTENDA/CF88:ART.35/BASE/1'][0]
        self.assertEqual(prev['status'], 'RETIRED')
        self.assertEqual({k: v for k, v in prev['content'].items() if k != 'palavras_dificeis'},
                         {k: v for k, v in e['content'].items() if k != 'palavras_dificeis'})   # main text untouched
        dec = json.loads((BD / 'ART35_GLOSSARY_CLEANUP_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual([(d['target_id'], d['changed_sections']) for d in dec['decisions']], [('CF88:ART.35', ['palavras_dificeis'])])
        self.assertFalse([t for t, r in cur.items() if 'suspende temporariamente' in json.dumps(r['content'], ensure_ascii=False)])

    def test_deterministic_build(self):
        tmp = Path(tempfile.mkdtemp(prefix='b04_'))
        try:
            for run in ('a', 'b'):
                E.build_entenda_index(self.ctx, self.new, tmp / run)
            for name in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT', 'ENTENDA_BUILD_MANIFEST.json'):
                self.assertEqual((tmp / 'a' / name).read_bytes(), (tmp / 'b' / name).read_bytes(), name)
                self.assertEqual((tmp / 'a' / name).read_bytes(), (BD / 'index' / name).read_bytes(), name)
        finally:
            shutil.rmtree(tmp)

    def test_approved_content_immutable(self):
        """Batches 01-03 (pending evidence and finals), main corpus (pilots) and editorial sources match HEAD."""
        root = HERE.parent
        for d in ('corpus', 'editorial', 'derived/pilot_t1', 'derived/production_batch_01', 'derived/production_batch_01_final',
                  'derived/production_batch_02', 'derived/production_batch_02_final', 'derived/production_batch_03',
                  'derived/production_batch_03_final'):
            out = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', f'ENTENDA_ENGINE/{d}'], cwd=root)
            self.assertEqual(out.returncode, 0, d)


if __name__ == '__main__':
    unittest.main()
