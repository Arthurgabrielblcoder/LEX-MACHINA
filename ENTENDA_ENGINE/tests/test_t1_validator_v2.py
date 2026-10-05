"""ENTENDA-T1 A6: validator v2 regression against the human decisions of the Batch05 HIGH rounds, and pending triage (classification only)."""
import copy
import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'LEGAL_TARGET_ID'))
import entenda_engine as E  # noqa: E402
import t1_external_resolver as X  # noqa: E402
import t1_triage as T  # noqa: E402
import t1_validator_v2 as V  # noqa: E402

BD = HERE / 'derived/production_batch_05'
ROUNDS = ('ROUND_1_HUMAN_REVIEW_DECISIONS.json', 'ROUND_2_HUMAN_REVIEW_DECISIONS.json', 'ROUND_3A_HUMAN_REVIEW_DECISIONS.json',
          'ROUND_3B_HUMAN_REVIEW_DECISIONS.json', 'ROUND_D_HUMAN_REVIEW_DECISIONS.json', 'ROUND_FINAL_HUMAN_REVIEW_DECISIONS.json')
KNOWN_FALSE_NEGATIVES = ['CF88:ART.37:PAR.9', 'CF88:ART.40:CAPUT', 'CF88:ART.40:PAR.9']   # conceptual corrections, not textual patterns


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@unittest.skipUnless((BD / 'ROUND_3B_HUMAN_REVIEW_DECISIONS.json').is_file(), 'batch 05 rounds not available')
class ValidatorV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.cat = V.load_catalog()
        cls.known = V.load_json(V.KNOWN)
        cls.reg = T.regression(BD, cls.ctx, cls.cat, cls.known)
        cls.all = E.load_corpus(BD / 'CF88_BATCH_05.entenda.jsonl')
        cls.act = {r['target_id']: r for r in cls.all if r['status'] == 'ACTIVE'}

    # ---------------- configuration and catalog ----------------
    def test_auto_approval_is_off(self):
        cfg = V.load_json(V.CONFIG)
        self.assertIs(cfg['AUTO_APPROVE_LOW'], False)
        self.assertIs(cfg['AUTO_APPROVE_MEDIUM'], False)
        self.assertIs(cfg['MICROAUTO_APPLY'], False)

    def test_catalog_only_learned_entries(self):
        doc = V.load_json(V.CATALOG)
        ids = [e['id'] for e in doc['entries']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 15)
        targets = {d['target_id'] for f in ROUNDS for d in V.load_json(BD / f)['decisions']}
        for e in doc['entries']:
            self.assertTrue(e['learned_from'], e['id'])
            self.assertTrue(set(e['applies_to_targets']) <= targets, e['id'])           # only targets decided in the rounds
            self.assertIn(e['placement'], ('EXTERNAL_LAYER_ONLY', 'CORE_WITH_PROVENANCE', 'CORE_ALLOWED'))
            for k in ('trigger', 'contradicts', 'open_framing', 'context'):
                if e.get(k):
                    re.compile(e[k])
        for code, *_, learned in V.PATTERN_RULES:
            self.assertTrue(learned, code)                                                # every pattern rule names its human case

    # ---------------- regression against human decisions ----------------
    def test_changes_requested_v1_detection(self):
        r = self.reg['changes_requested_v1']
        self.assertEqual(r['total'], 43)                                                   # 31 HIGH + 2 queue D + 10 final
        self.assertEqual(r['true_positives'], 40)
        self.assertEqual(r['true_positives_generalizable'], 34)
        self.assertEqual(r['false_negatives'], KNOWN_FALSE_NEGATIVES)                    # documented; detector does not replace review

    def test_approved_texts_clean_after_registered_resolutions(self):
        self.assertEqual(self.reg['approved_unchanged_v1']['total'], 26)
        self.assertEqual(len(self.reg['approved_unchanged_v1']['flagged_raw']), 8)          # known false positives, registered
        self.assertEqual(self.reg['approved_unchanged_v1']['flagged_after_known'], [])
        self.assertEqual(self.reg['approved_final']['total'], 69)
        self.assertEqual(self.reg['approved_final']['flagged_after_known'], [])
        self.assertEqual(self.reg['approved_final']['hard_fail'], [])

    def test_pilots_and_prior_corpus_have_no_hard_fail(self):
        self.assertEqual(self.reg['pilots']['hard_fail'], [])
        self.assertEqual(self.reg['prior_approved_corpus']['total'], 220)
        self.assertEqual(self.reg['prior_approved_corpus']['hard_fail'], [])
        self.assertEqual(self.reg['version_chain']['findings'], [])

    def test_known_resolutions_are_version_scoped(self):
        ids = {r['explanation_id'] for r in self.all} | {r['explanation_id'] for r in E.load_corpus(HERE / 'corpus/CF88.entenda.jsonl')}
        for eid in self.known['resolutions']:
            self.assertIn(eid, ids)

    # ---------------- severities (synthetic) ----------------
    def _rec(self, tid='CF88:ART.40:PAR.18'):
        return copy.deepcopy(self.act[tid])

    def test_hard_fail_internal_identifier_and_lei_seca(self):
        r = self._rec()
        r['content']['atencao'] += ' Ver CF88_RUNTIME.'
        self.assertIn('INTERNAL_IDENTIFIER', [f['code'] for f in V.validate(r, self.ctx, self.cat) if f['severity'] == 'HARD_FAIL'])
        r = self._rec()
        r['source']['source_text_snapshot'] = r['source']['source_text_snapshot'].replace('aposentadorias', 'aposentadoria', 1)
        codes = [f['code'] for f in V.validate(r, self.ctx, self.cat) if f['severity'] == 'HARD_FAIL']
        self.assertIn('LEI_SECA_DIVERGENCE', codes)
        self.assertEqual(V.route(V.validate(r, self.ctx, self.cat), 'LOW'), 'E_HARD_FAIL')

    def test_hard_fail_external_fact_without_provenance_on_a6_approval(self):
        r = self._rec('CF88:ART.40:PAR.22')
        r['human_review'] = {k: v for k, v in r['human_review'].items() if k != 'content_provenance'}
        self.assertIn('EXTERNAL_FACT_NO_PROVENANCE', [f['code'] for f in V.validate(r, self.ctx, self.cat) if f['severity'] == 'HARD_FAIL'])
        r['review_status'] = 'PENDING_HUMAN_REVIEW'
        r.pop('human_review')
        fs = V.validate(r, self.ctx, self.cat)
        self.assertIn('EXTERNAL_FACT_NEEDS_PROVENANCE', [f['code'] for f in fs if f['severity'] == 'REVIEW_REQUIRED'])
        self.assertEqual(V.route(fs, 'LOW'), 'D_FULL_HUMAN_REVIEW')

    def test_hard_fail_version_mutation_and_chain(self):
        prev = [copy.deepcopy(r) for r in self.all]
        cur = [copy.deepcopy(r) for r in self.all]
        cur[0]['content']['o_que_diz'] += ' x'
        self.assertIn('VERSION_MUTATION', [f['code'] for f in V.version_chain_findings(cur, prev)])
        cur = [copy.deepcopy(r) for r in self.all]
        ret = next(r for r in cur if r['status'] == 'RETIRED')
        ret['superseded_by'] = ret['explanation_id']
        self.assertIn('VERSION_CHAIN_BROKEN', [f['code'] for f in V.version_chain_findings(cur)])
        self.assertEqual(V.version_chain_findings(self.all, self.all), [])

    def test_negation_and_text_suppression(self):
        r = self._rec('CF88:ART.40:PAR.2')                                              # "não significa ... automaticamente" (approved)
        self.assertNotIn('AUTOMATIC_CONSEQUENCE', [f['code'] for f in V.pattern_findings(r)])
        r['content']['atencao'] = 'O servidor receberá automaticamente a diferença.'
        self.assertIn('AUTOMATIC_CONSEQUENCE', [f['code'] for f in V.pattern_findings(r)])
        r = self._rec('CF88:ART.40:PAR.8')                                              # finality stated by the text itself
        self.assertNotIn('TELEOLOGY_SPECULATIVE', [f['code'] for f in V.pattern_findings(r)])

    def test_catalog_context_avoids_unrelated_teto(self):
        main = {r['target_id']: r for r in E.load_corpus(HERE / 'derived/production_batch_02_final/CF88_BATCH_02_FINAL.entenda.jsonl')
                if r['status'] == 'ACTIVE'}
        if 'CF88:ART.29:INC.V' in main:                                                 # "teto" of councillors' pay is not Temas 377/384
            codes = [f['code'] for f in V.catalog_findings(main['CF88:ART.29:INC.V'], self.cat)]
            self.assertNotIn('CATALOG_CONTRADICTION', codes)

    # ---------------- micro-auto (suggestion only) ----------------
    def test_copy_microfix_suggestions_on_recorded_cases(self):
        n = 0
        for f in ('ROUND_1_EDITORIAL_ADJUSTMENTS.json', 'ROUND_2_EDITORIAL_ADJUSTMENTS.json', 'ROUND_3A_EDITORIAL_ADJUSTMENTS.json',
                  'ROUND_3B_EDITORIAL_ADJUSTMENTS.json'):
            for a in V.load_json(BD / f)['adjustments']:
                snap = self.act[a['target_id']]['source']['source_text_snapshot']
                for d in a['t1_contract_deviations']:
                    if 'COPIES_OFFICIAL_TEXT' not in d['reason']:
                        continue
                    text = a['reviewer_text_verbatim']['content'][d['section']]
                    sug = V.suggest_copy_microfix(text, snap)
                    self.assertIsNotNone(sug, (a['target_id'], d['section']))
                    fixed = text.replace(sug[0], sug[1], 1)
                    self.assertEqual(V.copy_runs(fixed, snap), [])
                    self.assertEqual(re.findall(r'\d+', fixed), re.findall(r'\d+', text))   # numbers never change
                    n += 1
        self.assertEqual(n, 9)

    # ---------------- triage of the pending (classification only) ----------------
    def test_triage_classifies_without_mutation_and_is_deterministic(self):
        with tempfile.TemporaryDirectory() as t:
            outs = []
            for k in range(2):
                d = Path(t) / f'r{k}'
                shutil.copytree(BD, d)
                before = {p.relative_to(d).as_posix(): sha(p) for p in d.rglob('*') if p.is_file() and not p.name.startswith('T1_')}
                T.run(d)
                after = {p.relative_to(d).as_posix(): sha(p) for p in d.rglob('*') if p.is_file() and not p.name.startswith('T1_')}
                self.assertEqual(before, after)                                            # no text, status or version changed
                outs.append({n: sha(d / n) for n in ('T1_PENDING_TRIAGE.json', 'T1_PENDING_TRIAGE_REPORT.md', 'T1_QUEUE_D_FULL_REVIEW.md',
                                                     'T1_VALIDATOR_V2_REGRESSION.json', 'T1_PENDING_TRIAGE_HUMAN_CALIBRATION.md',
                                                     'T1_LEGACY_AUDIT_BACKLOG.md')})
            self.assertEqual(outs[0], outs[1])
            self.assertEqual(outs[0], {n: sha(BD / n) for n in outs[0]})
        doc = V.load_json(BD / 'T1_PENDING_TRIAGE.json')
        self.assertEqual(sum(doc['counts'].values()), 0)                                      # all 69 resolved
        self.assertEqual(doc['auto_approve'], {'LOW': False, 'MEDIUM': False})
        self.assertEqual(doc['counts'], {'A_CLEAN_LOW': 0, 'B_CLEAN_MEDIUM': 0, 'C_QUICK_REVIEW': 0, 'D_FULL_HUMAN_REVIEW': 0, 'E_HARD_FAIL': 0})
        q = {x['target_id']: x for x in doc['rows']}
        self.assertTrue(all(x['review_status'] == 'PENDING_HUMAN_REVIEW' for x in doc['rows']))
        self.assertNotIn('CF88:ART.38:INC.III', q)                                           # queue D resolved by human review
        self.assertNotIn('CF88:ART.37:PAR.7', q)
        self.assertTrue(all(x['show_full_t1'] == (x['queue'] in ('D_FULL_HUMAN_REVIEW', 'E_HARD_FAIL')) for x in doc['rows']))
        self.assertIsNone(doc['presentation_volume']['reduction_pct'])                       # nothing pending to present

    # ---------------- semantic rules (final calibration) ----------------
    def test_semantic_rules_regression_cases(self):
        v1 = {r['target_id']: r for r in self.all if r['editorial_version'] == 1}
        for t, code in (('CF88:ART.37:INC.VIII', 'EXTERNAL_NORMATIVE_CLAIM_WITHOUT_PROVENANCE'), ('CF88:ART.38:INC.IV', 'EXCEPTION_OR_RESSALVA_DROPPED'),
                        ('CF88:ART.38:INC.I', 'EXHAUSTIVE_ENUMERATION_RISK')):
            self.assertIn(code, [f['code'] for f in V.semantic_findings(v1[t], self.ctx)], t)            # caught on the v1 the human corrected
            self.assertEqual(V.semantic_findings(self.act[t], self.ctx), [], t)                         # silent on the approved v2
        raw = {t: V.semantic_findings(r, self.ctx) for t, r in self.act.items()}
        self.assertEqual(sorted(t for t, fs in raw.items() if fs), ['CF88:ART.37:INC.V', 'CF88:ART.38'])   # 2 known false positives
        for t in ('CF88:ART.37:INC.V', 'CF88:ART.38'):
            fs = V.apply_known(self.act[t], V.semantic_findings(self.act[t], self.ctx), self.known)
            self.assertTrue(all(f['severity'] == 'INFO' for f in fs), t)

    def test_teleology_causal_regression_art38_ii(self):
        old = [r for r in self.all if r['explanation_id'] in ('ENTENDA/CF88:ART.38:INC.II/BASE/1', 'ENTENDA/CF88:ART.38:INC.II/BASE/2')]
        for r in old:
            self.assertIn('TELEOLOGY_SPECULATIVE', [f['code'] for f in V.pattern_findings(r)], r['explanation_id'])
        self.assertNotIn('TELEOLOGY_SPECULATIVE', [f['code'] for f in V.pattern_findings(self.act['CF88:ART.38:INC.II'])])

    # ---------------- external dependency resolver ----------------
    def test_resolver_real_relation_is_pending_not_validated(self):
        idx = X.RelationsIndex.from_config(V.load_json(V.CONFIG))
        cat = V.load_json(V.CATALOG)
        v1 = next(r for r in self.all if r['explanation_id'] == 'ENTENDA/CF88:ART.37:PAR.7/BASE/1')
        res = X.resolve(v1, cat, idx, V._provenance(v1))
        rels = [e for e in res['evidence'] if e.get('norma') == 'EXT_LEI12813_2013']
        if not rels:
            self.skipTest('Relations Engine working files not available')
        self.assertEqual((res['status'], res['via']), (X.PENDING, 'RELATIONS_ENGINE_PENDING'))   # found, but quarantined: no false AVAILABLE
        self.assertEqual((rels[0]['tipo'], rels[0]['fonte'], rels[0]['status']), ('REGULAMENTACAO', 'CAMARA_REGULAMENTACAO_CF', 'PENDING'))
        self.assertIn('ArtCF0862', rels[0]['url'])
        v2 = self.act['CF88:ART.37:PAR.7']                                                    # human provenance with official source
        self.assertEqual(X.resolve(v2, cat, idx, V._provenance(v2))['status'], X.AVAILABLE)
        self.assertEqual(X.resolve(v2, cat, idx, V._provenance(v2))['via'], 'ENTENDA_CONTENT_PROVENANCE')

    def test_resolver_only_validated_relations_suffice(self):
        cat = dict(entries=[])
        rec = copy.deepcopy(next(r for r in self.all if r['explanation_id'] == 'ENTENDA/CF88:ART.37:PAR.7/BASE/1'))
        base = dict(origem_norma='CF88', origem_artigo='37', origem_paragrafo='7', destino_norma='EXT_X', tipos=['REGULAMENTACAO'],
                    fontes=['CAMARA_REGULAMENTACAO_CF'], urls=['u'])
        mk = lambda **k: X.RelationsIndex([dict(source='synthetic', relations=[dict(base, **k)])])   # noqa: E731
        self.assertEqual(X.resolve(rec, cat, mk(classe='B_REGULAMENTACAO_OFICIAL', decisao='EXIBIR'), [])['status'], X.AVAILABLE)
        self.assertEqual(X.resolve(rec, cat, mk(classe='D_FRACA', decisao='OCULTAR_ATE_REVISAO'), [])['status'], X.REQUIRED)
        self.assertEqual(X.resolve(rec, cat, mk(classe='C_SECAO_INDETERMINADA', decisao='OCULTAR_ATE_REVISAO'), [])['status'], X.REQUIRED)
        self.assertEqual(X.resolve(rec, cat, mk(classe='C_EXTERNA_PENDENTE_VALIDACAO', decisao='OCULTAR_ATE_VALIDAR_VIGENCIA'), [])['status'],
                         X.PENDING)
        self.assertEqual(X.resolve(rec, cat, X.RelationsIndex([dict(path='nao/existe.json')]), [])['status'], X.REQUIRED)

    def test_human_calibration_packet_and_legacy_backlog(self):
        doc = V.load_json(BD / 'T1_PENDING_TRIAGE.json')
        self.assertTrue(doc['human_calibration_packet_generated'])
        pk = (BD / 'T1_PENDING_TRIAGE_HUMAN_CALIBRATION.md').read_text(encoding='utf-8')
        self.assertEqual(doc['human_calibration_packet']['chars'], len(pk))
        self.assertLess(len(pk), 5000)                                                         # empty queues
        for x in doc['rows']:                                                                  # every pending target appears once
            self.assertEqual(pk.count(f"`{x['target_id']}` — "), 1, x['target_id'])
        rv = (BD / 'T1_PENDING_TRIAGE_HUMAN_CALIBRATION_REVIEWED_2026-10-04.md').read_text(encoding='utf-8')   # packet the human reviewed
        self.assertIn('**⟦A soma das remunerações continua sujeita ao teto do art. 37, XI.⟧**', rv)
        self.assertEqual(rv.count('### `CF88:ART.38:INC.III`') + rv.count('### `CF88:ART.37:PAR.7`'), 2)
        self.assertNotIn('`CF88:ART.38:INC.III` — ', pk)
        bl = (BD / 'T1_LEGACY_AUDIT_BACKLOG.md').read_text(encoding='utf-8')
        self.assertEqual(doc['legacy_audit_backlog'], {'file': 'T1_LEGACY_AUDIT_BACKLOG.md', 'items': 49, 'blocks_batch05': False})
        prio = bl[bl.index('## Prioridade'):bl.index('## Todos')]
        self.assertIn('`CF88:ART.7:INC.I`', prio)
        self.assertIn('`CF88:ART.5:INC.LXXI`', prio)


if __name__ == '__main__':
    unittest.main()
