"""Permanent tests for ENTENDA-T1 (A1 pilot + A2 human review): editorial contract, granularity, stale, deterministic index, generic engine."""
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
sys.path.insert(0, str(REPO / 'LEGAL_TARGET_ID'))
import build_target_index as B  # noqa: E402
import entenda_engine as E  # noqa: E402

CORPUS = HERE / 'corpus/CF88.entenda.jsonl'
RUN1 = HERE / 'derived/pilot_t1'
REVIEW_DIFF = HERE / 'derived/CF88_PILOT_HUMAN_REVIEW_DIFF.json'
PILOT = ['CF88:ART.1', 'CF88:ART.5', 'CF88:ART.37', 'CF88:ART.37:PAR.6', 'CF88:ART.37:PAR.10', 'CF88:ART.60', 'CF88:ART.60:PAR.4',
         'CF88:ART.60:PAR.4:INC.IV', 'CF88:ART.150', 'CF88:ART.225', 'ADCT:ART.10:INC.II']


def _code(fn, *a):
    try:
        fn(*a)
    except E.EntendaError as e:
        return e.code
    return None


@unittest.skipUnless(CORPUS.is_file(), 'pilot corpus not stamped')
class PilotCorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.corpus = E.load_corpus(CORPUS)
        cls.by = {r['target_id']: r for r in cls.corpus if r['status'] == 'ACTIVE'}

    def rec(self, tid):
        return copy.deepcopy(self.by[tid])

    def test_valid_pilot_corpus(self):
        E.validate_corpus(self.corpus, self.ctx)
        self.assertEqual(sorted(self.by), sorted(PILOT))
        self.assertTrue(all(r['review_status'] == 'HUMAN_APPROVED_T1' and r['usage_policy'] == 'EDITORIAL_OUTPUT_ONLY' for r in self.by.values()))

    def test_human_review_applied_and_evidence_preserved(self):
        diff = json.loads(REVIEW_DIFF.read_text(encoding='utf-8'))
        changed = ['ADCT:ART.10:INC.II', 'CF88:ART.225', 'CF88:ART.37:PAR.6', 'CF88:ART.5', 'CF88:ART.60:PAR.4:INC.IV']
        self.assertEqual(diff['changed_targets'], changed)
        self.assertTrue(all(c['human_review'] is True and c['reason'] for c in diff['changes']))
        retired = {r['target_id']: r for r in self.corpus if r['status'] == 'RETIRED'}
        self.assertEqual(sorted(retired), changed)
        original = {e['target_id']: e for e in json.loads((HERE / 'editorial/CF88_PILOT_DRAFTS.json').read_text(encoding='utf-8'))['explanations']}
        for tid, r in retired.items():
            self.assertEqual(r['superseded_by'], f'ENTENDA/{tid}/BASE/2')
            self.assertEqual(r['content'], original[tid]['content'])  # A1 evidence kept verbatim
            self.assertEqual(self.by[tid]['editorial_version'], 2)
        for tid in sorted(set(PILOT) - set(changed)):
            self.assertEqual((self.by[tid]['editorial_version'], self.by[tid]['content']), (1, original[tid]['content']))
        self.assertIn('nexo causal', self.by['CF88:ART.37:PAR.6']['content']['o_que_significa'])
        self.assertIn('regulamentação', self.by['CF88:ART.5']['content']['o_que_significa'])
        self.assertIn('interpretação constitucional', self.by['CF88:ART.60:PAR.4:INC.IV']['content']['o_que_significa'])
        self.assertNotIn('comunica', self.by['ADCT:ART.10:INC.II']['content']['exemplo_pratico'])
        self.assertNotIn('pertence', self.by['CF88:ART.225']['content']['palavras_dificeis'][0]['explicacao'])

    def test_invalid_target(self):
        r = self.rec('CF88:ART.37:PAR.6')
        r['target_id'] = 'CF88/ART.37'
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_INVALID_TARGET_ID')
        r['target_id'] = 'CF88:ART.78:PAR.4'  # exists only in the ADCT namespace
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_TARGET_NOT_IN_NORM')
        self.assertEqual(_code(E.get_explanation, 'CF88/ART.5', self.corpus), 'LOOKUP_INVALID_TARGET_ID')
        r = self.rec('CF88:ART.1')
        r.update(target_id='CF88', explanation_id='ENTENDA/CF88/BASE/1', explanation_key='ENTENDA/CF88/BASE')
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_TARGET_NOT_ELIGIBLE')

    def test_historical_target_rejected(self):
        tid = 'CF88:ART.40:PAR.4:INC.II'
        self.assertEqual(self.ctx.effective_status(tid), 'HISTORICAL')
        r = self.rec('CF88:ART.60:PAR.4:INC.IV')
        r.update(target_id=tid, explanation_id=E.explanation_id(tid), explanation_key=E.explanation_key(tid), editorial_version=1)
        r['granularity']['context_targets'] = self.ctx.context_chain(tid)
        r['validity']['target_status'] = 'HISTORICAL'
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_HISTORICAL_NOT_ALLOWED')
        self.assertEqual(self.ctx.snapshot(tid), '')  # no current text: stamp refuses (ENTENDA_NO_SOURCE_TEXT)

    def test_stale_detection(self):
        tid = 'CF88:ART.37:PAR.6'
        snap = self.ctx.snapshot(tid)
        self.assertEqual(E.check_stale(tid, snap, self.corpus)['state'], 'FRESH')
        self.assertEqual(E.check_stale(tid, snap.replace('dolo ou culpa', 'dolo'), self.corpus)['state'], 'STALE_TEXT_CHANGED')
        self.assertEqual(E.check_stale(tid, '', self.corpus)['state'], 'ORPHANED_TARGET')
        inc = 'CF88:ART.60:PAR.4:INC.IV'
        ctxh = dict(E.context_hashes(self.ctx, inc), **{'CF88:ART.60:PAR.4': E.sha256('outro enunciado')})
        self.assertEqual(E.check_stale(inc, self.ctx.snapshot(inc), self.corpus, current_context=ctxh)['state'], 'STALE_CONTEXT_CHANGED')
        self.assertTrue(all(s['state'] == 'FRESH' for s in E.stale_report(self.corpus, self.ctx)))

    def test_stale_end_to_end_when_official_text_changes(self):
        src = self.ctx.ncfg['text_sources'][0]['path']
        text = E.read_source_bytes(REPO, src).decode('utf-8-sig')
        old = 'Não será objeto de deliberação a proposta de emenda tendente a abolir:'
        self.assertIn(old, text)
        ctx2 = E.NormContext('CF88').reload_text({src: text.replace(old, 'Não será objeto de deliberação a proposta de emenda que vise abolir:')})
        st = {s['target_id']: s['state'] for s in E.stale_report(self.corpus, ctx2)}
        self.assertEqual(st['CF88:ART.60:PAR.4'], 'STALE_TEXT_CHANGED')
        self.assertEqual(st['CF88:ART.60'], 'STALE_TEXT_CHANGED')  # article snapshot covers its subtree
        self.assertEqual(st['CF88:ART.60:PAR.4:INC.IV'], 'STALE_CONTEXT_CHANGED')  # own text unchanged, parent enunciado changed
        self.assertEqual(st['CF88:ART.37:PAR.6'], 'FRESH')
        tmp = Path(tempfile.mkdtemp(prefix='entenda_stale_'))
        try:
            E.build_entenda_index(ctx2, self.corpus, tmp)
            self.assertEqual(E.lookup_idx('CF88:ART.60:PAR.4', tmp / 'ENTENDA_LOOKUP.IDX', tmp / 'ENTENDA_PAYLOAD.DAT')['freshness'], 'STALE_TEXT_CHANGED')
        finally:
            shutil.rmtree(tmp)

    def test_parent_context_declared_not_inherited(self):
        rec = E.get_explanation('CF88:ART.60:PAR.4:INC.IV', self.corpus)
        self.assertEqual(rec['granularity']['context_targets'], ['CF88:ART.60', 'CF88:ART.60:PAR.4'])
        self.assertEqual(E.context_links('CF88:ART.60:PAR.4:INC.IV', self.corpus), ['CF88:ART.60', 'CF88:ART.60:PAR.4'])
        self.assertIsNone(E.get_explanation('CF88:ART.60:PAR.4:INC.I', self.corpus))  # sibling without text: no fallback to parent
        self.assertIsNone(E.get_explanation('CF88:ART.37:CAPUT', self.corpus))
        r = self.rec('CF88:ART.60:PAR.4:INC.IV')
        r['granularity']['context_targets'] = ['CF88:ART.60:PAR.4']
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_CONTEXT_INVALID')
        r = self.rec('CF88:ART.60:PAR.4:INC.IV')
        r['granularity']['semantic_autonomy'] = 'AUTONOMOUS'
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_GRANULARITY_INVALID')

    def test_art60_hierarchical_composition(self):
        roles = [(t, self.by[t]['granularity']['role']) for t in ('CF88:ART.60', 'CF88:ART.60:PAR.4', 'CF88:ART.60:PAR.4:INC.IV')]
        self.assertEqual([r for _, r in roles], ['OVERVIEW', 'BLOCK', 'ITEM'])
        pairs = E.validate_corpus(self.corpus, self.ctx)
        art60 = [p for p in pairs if p['child'].startswith('CF88:ART.60')]
        self.assertEqual(len(art60), 3)
        self.assertTrue(all(max(p['similarity'].values()) <= self.ctx.limits['max_section_similarity'] for p in art60))
        bad = [copy.deepcopy(r) for r in self.corpus]
        child = next(r for r in bad if r['target_id'] == 'CF88:ART.60:PAR.4:INC.IV' and r['status'] == 'ACTIVE')
        child['content']['o_que_significa'] = self.by['CF88:ART.60:PAR.4']['content']['o_que_significa']
        self.assertEqual(_code(E.validate_corpus, bad, self.ctx), 'ENTENDA_REPEATED_ACROSS_HIERARCHY')

    def test_adct(self):
        r = E.get_explanation('ADCT:ART.10:INC.II', self.corpus)
        self.assertEqual((r['namespace'], r['norma_id'], r['validity']['target_status']), ('ADCT', 'CF88', 'UNKNOWN'))
        ev = r['validity']['external_verification']
        self.assertEqual((ev['status'], ev['current_in_operational_source'], ev['current_official_external'], ev['content_hash_stored']),
                         ('CURRENT_OFFICIAL_EXTERNAL_VERIFICATION', False, True, False))
        self.assertEqual(E.display_validity(r), 'CURRENT_OFFICIAL_EXTERNAL')
        bad = copy.deepcopy(r)
        bad['validity']['external_verification']['current_in_operational_source'] = True
        self.assertEqual(_code(E.validate_explanation, bad, self.ctx), 'ENTENDA_EXTERNAL_VERIFICATION_INVALID')
        self.assertEqual(r['source']['text_source_role'], 'STRUCTURAL_CANONICAL_SOURCE_FALLBACK')
        self.assertEqual(r['granularity']['context_targets'], ['ADCT:ART.10', 'ADCT:ART.10:CAPUT'])
        self.assertIsNone(E.get_explanation('CF88:ART.10:INC.II', self.corpus))
        r = copy.deepcopy(r)
        r['validity']['validity_note'] = None
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_UNKNOWN_VALIDITY_NEEDS_NOTE')

    @unittest.skipUnless((RUN1 / 'ENTENDA_LOOKUP.IDX').is_file(), 'pilot build missing')
    def test_lookup(self):
        for tid in PILOT:
            got = E.lookup_idx(tid, RUN1 / 'ENTENDA_LOOKUP.IDX', RUN1 / 'ENTENDA_PAYLOAD.DAT')
            rec = self.by[tid]
            self.assertEqual(got['explanation_id'], rec['explanation_id'])
            self.assertEqual(got['context_targets'], rec['granularity']['context_targets'])
            self.assertEqual(got['sections']['O QUE DIZ'], rec['content']['o_que_diz'])
            self.assertEqual(got['sections']['EXEMPLO PRÁTICO'], rec['content']['exemplo_pratico'])
            self.assertEqual((got['resolution_type'], got['review']), ('DIRECT', 'HUMAN_APPROVED_T1'))
        self.assertEqual(E.lookup_idx('CF88:ART.37:PAR.6', RUN1 / 'ENTENDA_LOOKUP.IDX', RUN1 / 'ENTENDA_PAYLOAD.DAT')['reference_count'], 5)
        for missing in ('CF88:ART.2', 'CF88:ART.60:PAR.4:INC.I', 'ADCT:ART.5', 'ZZZ:ART.1'):
            self.assertIsNone(E.lookup_idx(missing, RUN1 / 'ENTENDA_LOOKUP.IDX', RUN1 / 'ENTENDA_PAYLOAD.DAT'))

    def test_duplicate_explanation_id(self):
        self.assertEqual(_code(E.validate_corpus, self.corpus + [self.rec('CF88:ART.60')], self.ctx), 'ENTENDA_DUPLICATE_EXPLANATION_ID')
        v2 = self.rec('CF88:ART.60')
        v2.update(editorial_version=2, explanation_id=E.explanation_id('CF88:ART.60', 'BASE', 2))
        self.assertEqual(_code(E.validate_corpus, self.corpus + [v2], self.ctx), 'ENTENDA_DUPLICATE_ACTIVE_TARGET')

    def test_missing_or_wrong_source_hash(self):
        r = self.rec('CF88:ART.1')
        r['source']['source_text_sha256'] = None
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_MISSING_SOURCE_HASH')
        r['source']['source_text_sha256'] = '0' * 64
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_SOURCE_HASH_MISMATCH')

    def test_editorial_guards(self):
        r = self.rec('CF88:ART.37:PAR.6')
        r['content']['atencao'] = 'O STF decidiu que a vítima deve acionar o Estado.'
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_EXTERNAL_CASE_CONTENT')
        r = self.rec('CF88:ART.37:PAR.6')
        r['content']['o_que_diz'] = self.ctx.text['CF88:ART.37:PAR.6']
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_COPIES_OFFICIAL_TEXT')
        r = self.rec('CF88:ART.37:PAR.6')
        r['content']['atencao'] = ''
        self.assertEqual(_code(E.validate_explanation, r, self.ctx), 'ENTENDA_SECTION_EMPTY')

    def test_stamp_keeps_hash_and_requires_version_bump(self):
        drafts = json.loads((HERE / 'editorial/CF88_PILOT_T1_REVIEWED.json').read_text(encoding='utf-8'))
        again = E.stamp(drafts, self.ctx, self.corpus)
        self.assertEqual(sorted(json.dumps(r, sort_keys=True) for r in again), sorted(json.dumps(r, sort_keys=True) for r in self.corpus))
        drafts['explanations'][0]['content']['exemplo_pratico'] += ' Texto alterado.'
        self.assertEqual(_code(E.stamp, drafts, self.ctx, self.corpus), 'ENTENDA_CONTENT_CHANGED_WITHOUT_VERSION_BUMP')

    @unittest.skipUnless((RUN1 / 'ENTENDA_LOOKUP.IDX').is_file(), 'pilot build missing')
    def test_deterministic_build(self):
        tmp = Path(tempfile.mkdtemp(prefix='entenda_build_'))
        try:
            for run in ('a', 'b'):
                E.build_entenda_index(self.ctx, self.corpus, tmp / run)
            for name in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT', 'ENTENDA_BUILD_MANIFEST.json'):
                self.assertEqual((tmp / 'a' / name).read_bytes(), (tmp / 'b' / name).read_bytes(), name)
                self.assertEqual((tmp / 'a' / name).read_bytes(), (RUN1 / name).read_bytes(), name)
        finally:
            shutil.rmtree(tmp)


def _synthetic_words(prefix, n):
    return ' '.join(f'{prefix}{i}' for i in range(n)) + '.'


class GenericEngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='entenda_fixture_'))
        self.src = 'cdc.txt'
        (self.tmp / self.src).write_text('Art. 6º São direitos básicos do consumidor:\nVI - a efetiva prevenção e reparação de danos;\n'
                                         'Parágrafo único. Texto sintético de teste.\n', encoding='utf-8')
        idx = B.build('CDC1990', self.tmp / self.src)
        (self.tmp / 'idx.json').write_text(json.dumps(idx, ensure_ascii=False), encoding='utf-8')
        base_cfg = json.loads((HERE / 'entenda_config.json').read_text(encoding='utf-8'))
        cfg = dict(schema_version=1, limits=base_cfg['limits'], norms=dict(CDC1990=dict(
            target_index='idx.json', default_target_status='CURRENT', corpus='CDC1990.entenda.jsonl', allow_historical=False,
            text_sources=[dict(namespaces=['CDC1990'], path=self.src, role='OPERATIONAL_CURRENT_TEXT_SOURCE')],
            export_review_statuses=['PENDING_HUMAN_REVIEW'])))
        (self.tmp / 'cfg.json').write_text(json.dumps(cfg), encoding='utf-8')
        self.ctx = E.NormContext('CDC1990', self.tmp / 'cfg.json', base=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def drafts(self):
        def content(p, n):
            return dict(o_que_diz=_synthetic_words(p + 'd', n), o_que_significa=_synthetic_words(p + 's', n), exemplo_pratico=_synthetic_words(p + 'e', n),
                        atencao=None, palavras_dificeis=[dict(termo='Termo', explicacao='explicacao sintetica')])
        return dict(norma_id='CDC1990', template_version='T', prompt_version='P', review_status='PENDING_HUMAN_REVIEW',
                    authoring=dict(mode='fixture'), explanations=[
                        dict(target_id='CDC1990:ART.6', role='OVERVIEW', semantic_autonomy='AUTONOMOUS', editorial_reason='fixture', content=content('a', 50)),
                        dict(target_id='CDC1990:ART.6:INC.VI', role='ITEM', semantic_autonomy='DEPENDENT_ON_PARENT', editorial_reason='fixture',
                             content=content('b', 30))])

    def test_synthetic_norm_end_to_end(self):
        recs = E.stamp(self.drafts(), self.ctx)
        self.assertEqual(recs[1]['granularity']['context_targets'], ['CDC1990:ART.6', 'CDC1990:ART.6:CAPUT'])
        E.write_corpus(recs, self.tmp / 'CDC1990.entenda.jsonl', self.ctx)
        corpus = E.load_corpus(self.tmp / 'CDC1990.entenda.jsonl')
        f1 = E.build_entenda_index(self.ctx, corpus, self.tmp / 'o1')
        f2 = E.build_entenda_index(self.ctx, corpus, self.tmp / 'o2')
        self.assertEqual(f1, f2)
        got = E.lookup_idx('CDC1990:ART.6:INC.VI', self.tmp / 'o1/ENTENDA_LOOKUP.IDX', self.tmp / 'o1/ENTENDA_PAYLOAD.DAT')
        self.assertEqual((got['explanation_id'], got['freshness']), ('ENTENDA/CDC1990:ART.6:INC.VI/BASE/1', 'FRESH'))
        self.assertIsNone(E.lookup_idx('CDC1990:ART.6:PAR.UNICO', self.tmp / 'o1/ENTENDA_LOOKUP.IDX', self.tmp / 'o1/ENTENDA_PAYLOAD.DAT'))
        ctx2 = E.NormContext('CDC1990', self.tmp / 'cfg.json', base=self.tmp).reload_text(
            {self.src: (self.tmp / self.src).read_text(encoding='utf-8').replace('reparação de danos', 'reparação integral de danos')})
        st = {s['target_id']: s['state'] for s in E.stale_report(corpus, ctx2)}
        self.assertEqual(st, {'CDC1990:ART.6': 'STALE_TEXT_CHANGED', 'CDC1990:ART.6:INC.VI': 'STALE_TEXT_CHANGED'})

    def test_other_norm_rejected(self):
        with self.assertRaises(E.EntendaError):
            E.NormContext('CC2002', self.tmp / 'cfg.json', base=self.tmp)

    def test_engine_has_no_norm_hardcoded(self):
        src = (HERE / 'entenda_engine.py').read_text(encoding='utf-8')
        for token in ("'CF88'", '"CF88"', "'ADCT'", '"ADCT"'):
            self.assertNotIn(token, src)

    def test_entenda_is_not_a_source_for_other_layers(self):
        for p in list((REPO / 'LEGAL_TARGET_ID').glob('*.py')) + [REPO / 'LEGAL_TARGET_ID/engine_config.json']:
            text = p.read_text(encoding='utf-8')
            self.assertNotIn('ENTENDA_ENGINE', text, p.name)
            self.assertNotIn('.entenda.jsonl', text, p.name)
        self.assertTrue(json.loads((HERE / 'entenda_config.json').read_text(encoding='utf-8'))['usage_policy'].startswith('EDITORIAL_OUTPUT_ONLY'))


if __name__ == '__main__':
    unittest.main()
