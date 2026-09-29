"""Tests for the human-approved ENTENDA CF88 Batch 03 (arts. 18-24): review, competence categories, jurisprudence policy, temporal notes."""
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

FD = HERE / 'derived/production_batch_03_final'
PD = HERE / 'derived/production_batch_03'
LK, PL = FD / 'ENTENDA_LOOKUP.IDX', FD / 'ENTENDA_PAYLOAD.DAT'
NEW = ('CF88:ART.21:INC.XXIV', 'CF88:ART.21:INC.XXV', 'CF88:ART.22:INC.XXIX')


def _body(r):
    c = r['content']
    return ' '.join([c[k] for k in E.REQUIRED_TEXT] + [c['atencao'] or ''] + [t['explicacao'] for t in c['palavras_dificeis']])


@unittest.skipUnless((FD / 'SELECTION_REPORT.json').is_file(), 'final batch 03 not built')
class Batch03FinalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.all = E.load_corpus(FD / 'CF88_BATCH_03_FINAL.entenda.jsonl')
        cls.new = [r for r in cls.all if r['status'] == 'ACTIVE']
        cls.by = {r['target_id']: r for r in cls.new}
        cls.rep = json.loads((FD / 'SELECTION_REPORT.json').read_text(encoding='utf-8'))
        cls.rows = {r['target_id']: r for r in cls.rep['selection']}
        cls.dec = json.loads((FD / 'HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        cls.jur = json.loads((FD / 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json').read_text(encoding='utf-8'))
        cls.tmp = json.loads((FD / 'TEMPORAL_NOTES.json').read_text(encoding='utf-8'))

    def test_totals_and_review(self):
        self.assertEqual(len(self.new), 49)
        self.assertTrue(all(r['review_status'] == 'HUMAN_APPROVED_T1' for r in self.new))
        self.assertFalse([r for r in self.all if r['review_status'] == 'PENDING_HUMAN_REVIEW'])
        for t in NEW:
            self.assertIn(t, self.by)
            self.assertEqual(self.rows[t]['classification'], 'ITEM')
        self.assertEqual((self.dec['review_status'], self.dec['review_date'], self.dec['review_scope']),
                         ('HUMAN_REVIEW_COMPLETED', '2026-09-29', 'CF88_ARTS_18_24'))
        self.assertEqual(len(self.dec['decisions']), 49)
        self.assertEqual(sorted(self.dec['created_by_review']), sorted(NEW))
        self.assertTrue(all(d['decision'] in ('APPROVED', 'APPROVED_AFTER_ADJUSTMENT') and d['review_reason'] for d in self.dec['decisions']))
        retired = [r for r in self.all if r['status'] == 'RETIRED']
        self.assertEqual(len(retired), self.dec['decision_counts']['APPROVED_AFTER_ADJUSTMENT'])
        original = {e['target_id']: e['content'] for e in json.loads((PD / 'BATCH_03_DRAFTS.json').read_text(encoding='utf-8'))['explanations']}
        for r in retired:
            self.assertEqual(r['content'], original[r['target_id']])  # evidence preserved
            self.assertEqual(self.by[r['target_id']]['editorial_version'], r['editorial_version'] + 1)
        E.validate_corpus(self.new, self.ctx)

    def test_pending_evidence_preserved(self):
        spec = json.loads((PD / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
        self.assertEqual(spec['superseded_by_final'], 'ENTENDA_ENGINE/derived/production_batch_03_final')
        ev = self.dec['original_evidence_sha256']
        for name in ('BATCH_03_DRAFTS.json', 'REVIEW_BATCH_03.md', 'CF88_BATCH_03.entenda.jsonl', 'index/ENTENDA_LOOKUP.IDX', 'index/ENTENDA_PAYLOAD.DAT'):
            self.assertEqual(hashlib.sha256((PD / name).read_bytes()).hexdigest(), ev[name], name)
        pending = E.load_corpus(PD / 'CF88_BATCH_03.entenda.jsonl')
        self.assertEqual(len(pending), 46)
        self.assertTrue(all(r['review_status'] == 'PENDING_HUMAN_REVIEW' for r in pending))

    def test_scope_targets_current(self):
        scope = [t for a in json.loads((FD / 'BATCH_SPEC.json').read_text(encoding='utf-8'))['scope'] for t in self.ctx.subtree(a)]
        self.assertEqual(sorted(self.rows), sorted(scope))
        s = self.rep['summary']
        self.assertEqual((s['targets_evaluated'], s['targets_legally_current'], s['targets_revoked']), (134, 134, 0))
        self.assertLessEqual(len(self.new), s['hard_cap'])
        self.assertFalse(any(re.match(r'CF88:ART\.(2[5-9]|[3-9]\d|\d{3})\b', r['target_id']) for r in self.new))

    def test_block_lookup(self):
        cases = {'CF88:ART.22:INC.V': 'CF88:ART.22:INC.IV', 'CF88:ART.24:PAR.4': 'CF88:ART.24:PAR.3', 'CF88:ART.20:INC.VII': 'CF88:ART.20:INC.III'}
        for tid, anchor in cases.items():
            got = E.lookup_idx(tid, LK, PL)
            self.assertEqual((got['anchor_target_id'], got['resolution_type']), (anchor, 'COVERED_BY_BLOCK'), tid)
        for t, title in (('CF88:ART.21:INC.XXIV', 'Art. 21, inciso XXIV — Inspeção do trabalho'),
                         ('CF88:ART.21:INC.XXV', 'Art. 21, inciso XXV — Áreas e condições para garimpagem associativa'),
                         ('CF88:ART.22:INC.XXIX', 'Art. 22, inciso XXIX — Propaganda comercial')):
            got = E.lookup_idx(t, LK, PL)
            self.assertEqual((got['resolution_type'], got['display_title']), ('DIRECT', title))
        for r in self.new:
            for t in r['granularity'].get('covered_targets', []):
                self.assertEqual(E.lookup_idx(t, LK, PL)['anchor_target_id'], r['target_id'], t)

    def test_art21_material_art22_legislative(self):
        self.assertIn('materiais ou administrativas', self.by['CF88:ART.21']['content']['o_que_significa'])
        self.assertIn('Não tratam de legislar', self.by['CF88:ART.21']['content']['o_que_significa'])
        self.assertIn('competência é legislativa', self.by['CF88:ART.22']['content']['o_que_significa'])
        xxiv = _body(self.by['CF88:ART.21:INC.XXIV'])
        self.assertIn('art. 22, I', xxiv)
        self.assertIn('Justiça do Trabalho', xxiv)
        xxv = _body(self.by['CF88:ART.21:INC.XXV'])
        for ref in ('art. 20, IX', 'art. 21, XXV', 'art. 22, XII'):
            self.assertIn(ref, xxv)
        self.assertIn('propaganda eleitoral', _body(self.by['CF88:ART.22:INC.XXIX']))
        self.assertNotIn('Uma lei estadual ou municipal que invada esses temas é inconstitucional', self.by['CF88:ART.22']['content']['o_que_significa'])

    def test_art22_pu_delegation_states_only(self):
        t = _body(self.by['CF88:ART.22:PAR.UNICO'])
        for w in ('lei complementar federal', 'Estados', 'questões específicas', 'Os Municípios não são destinatários', 'Distrito Federal'):
            self.assertIn(w, t)
        for tid in ('CF88:ART.22', 'CF88:ART.22:INC.I'):
            s = self.by[tid]['content']['o_que_significa']
            self.assertNotRegex(s, r'Estados e Municípios não podem editar leis sobre esses ramos, salvo delegação')
            self.assertIn('autorize os Estados', s)

    def test_art23_common_not_everyone_does_everything(self):
        s = self.by['CF88:ART.23']['content']['o_que_significa']
        self.assertIn('atribuições administrativas', s)
        self.assertIn('Não se trata de competência para legislar', s)
        self.assertNotIn('todos os entes podem e devem atuar nessas áreas ao mesmo tempo', s)
        self.assertNotIn('nenhum ente pode se omitir', _body(self.by['CF88:ART.23:INC.II']))
        self.assertNotIn('responsabilidade solidária', _body(self.by['CF88:ART.23:INC.II']))

    def test_art24_concurrent_and_suspension(self):
        self.assertIn('não significa competição', self.by['CF88:ART.24']['content']['o_que_significa'])
        b = self.by['CF88:ART.24:PAR.3']
        t = _body(b)
        for w in ('suspende a eficácia', 'suspensão da eficácia', 'superveniência', 'surgir posteriormente', 'não é revogada'):
            self.assertIn(w, t)
        for r in self.new:
            if r['target_id'].startswith('CF88:ART.24'):
                for m in re.finditer(r'revoga\w*', _body(r)):
                    self.assertRegex(_body(r)[max(0, m.start() - 20):m.start()], r'(não|não é|não em)\s*$', r['target_id'])

    def test_editorial_adjustments(self):
        self.assertNotIn('Hoje não há Territórios', _body(self.by['CF88:ART.18']))
        self.assertNotIn('índios', _body(self.by['CF88:ART.20']) + _body(self.by['CF88:ART.20:INC.XI']))
        self.assertNotRegex(_body(self.by['CF88:ART.19']), r'não financia cultos|templo|sem desconfiança')
        xvi = _body(self.by['CF88:ART.21:INC.XVI'])
        self.assertNotRegex(xvi, r'violência|drogas')
        self.assertNotIn('toda atividade nuclear está sob monopólio', _body(self.by['CF88:ART.21:INC.XXIII']))
        self.assertIn('comercialização e utilização de radioisótopos', self.by['CF88:ART.21:INC.XXIII']['content']['o_que_diz'])
        xxvi = _body(self.by['CF88:ART.21:INC.XXVI'])
        self.assertNotRegex(xxvi, r'ANPD|Autoridade Nacional|órgão pelo qual')  # institutional data only in external layer
        self.assertIn('ANPD', ' '.join(self.by['CF88:ART.21:INC.XXVI']['external_layer_notes']))
        self.assertIn('Esse procedimento é chamado de licenciamento ambiental', _body(self.by['CF88:ART.23:INC.VI']))
        self.assertIn('Essa autorização é chamada de outorga', _body(self.by['CF88:ART.21:INC.XVIII']))

    def test_temporal_notes(self):
        ids = {n['note_id']: n for n in self.tmp['notes']}
        self.assertEqual(sorted(ids), ['ANPD_AGENCIA_REGULADORA_LEI_15352_2026', 'LC_230_2026_DESMEMBRAMENTO_INCORPORACAO_LIMITROFE'])
        lc = ids['LC_230_2026_DESMEMBRAMENTO_INCORPORACAO_LIMITROFE']
        self.assertEqual((lc['target_id'], lc['state']), ('CF88:ART.18:PAR.4', 'IN_EFFECT'))
        self.assertIn('Em nenhuma hipótese esse desmembramento pode resultar na criação de novo Município', lc['note']['text'])
        self.assertIn('A lei não disciplina a criação de novos Municípios', lc['note']['text'])
        body = _body(self.by['CF88:ART.18:PAR.4'])
        self.assertNotIn('230', body)  # constitutional core stays stable
        self.assertIn('Ela não é autorização geral para criar Municípios', ' '.join(self.by['CF88:ART.18:PAR.4']['external_layer_notes']))

    def test_jurisprudence(self):
        st = {}
        for r in self.jur['recommendations']:
            st.setdefault(r['status'], []).append(r)
        self.assertEqual({k: len(v) for k, v in st.items()},
                         {'READY_TO_LINK': 11, 'PENDING_EXTERNAL_INGESTION': 6, 'MATERIAL_MISMATCH_EXCLUDED': 1})
        for r in st['READY_TO_LINK']:  # material verification, not just the number
            self.assertTrue(r['already_linked_to_target'] and r['subject_verification']['verified'], r['desired_reference'])
            self.assertFalse(r['subject_verification']['missing_keywords'])
        (mm,) = st['MATERIAL_MISMATCH_EXCLUDED']
        self.assertEqual((mm['target_id'], mm['local_identity_searched']), ('CF88:ART.19', 'STF:RG:1157'))
        t1031 = next(r for r in self.jur['recommendations'] if r['local_identity_searched'] == 'STF:RG:1031')
        self.assertEqual((t1031['primary_target_id'], t1031['correlated_target_id']), ('CF88:ART.231', 'CF88:ART.20:INC.XI'))
        self.assertTrue(t1031['local_reference_id'].endswith('@CF88:ART.231'))
        self.assertNotIn('CF88:ART.16', t1031['local_reference_id'])
        self.assertEqual([(x['target_id'], x['status']) for x in t1031['excluded_local_links']], [('CF88:ART.16', 'MATERIAL_MISMATCH_EXCLUDED')])
        t676 = next(r for r in self.jur['recommendations'] if r['local_identity_searched'] == 'STF:RG:676')
        self.assertEqual(t676['status'], 'READY_TO_LINK')
        self.assertIn('46/2005', t676['subject_verification']['keywords'])
        for ident in ('STF:ADI:2404', 'STF:RG:793'):
            r = next(x for x in self.jur['recommendations'] if x['local_identity_searched'] == ident)
            self.assertEqual(r['status'], 'PENDING_EXTERNAL_INGESTION')
        for r in self.new:
            self.assertIsNone(E.EXTERNAL_CASE_RE.search(_body(r)), r['target_id'])

    def test_deterministic_build(self):
        tmp = Path(tempfile.mkdtemp(prefix='b03f_'))
        try:
            for run in ('a', 'b'):
                E.build_entenda_index(self.ctx, self.new, tmp / run)
            for name in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT', 'ENTENDA_BUILD_MANIFEST.json'):
                self.assertEqual((tmp / 'a' / name).read_bytes(), (tmp / 'b' / name).read_bytes(), name)
                self.assertEqual((tmp / 'a' / name).read_bytes(), (FD / name).read_bytes(), name)
        finally:
            shutil.rmtree(tmp)

    def test_approved_batches_immutable(self):
        root = HERE.parent
        for d in ('production_batch_01_final', 'production_batch_02_final', 'production_batch_01', 'production_batch_02'):
            out = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', f'ENTENDA_ENGINE/derived/{d}'], cwd=root)
            self.assertEqual(out.returncode, 0, d)


if __name__ == '__main__':
    unittest.main()
