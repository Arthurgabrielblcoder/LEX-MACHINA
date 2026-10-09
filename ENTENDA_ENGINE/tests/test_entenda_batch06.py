"""Tests for ENTENDA CF PRODUCTION BATCH 06 (arts. 42-75): T1 drafts, recalibrated triage and the human rounds D and C (queues D and C)."""
import copy
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
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_entenda_batch06_candidate as B  # noqa: E402
import entenda_engine as E  # noqa: E402
import t1_batch_packets as BP  # noqa: E402
import t1_external_resolver as X  # noqa: E402
import t1_risk as R  # noqa: E402
import t1_validator_v2 as V  # noqa: E402
import t1_validator_v3 as V3  # noqa: E402
import text_source_reconstruction as TSR  # noqa: E402

BD = HERE / 'derived/production_batch_06'
PILOTS = ('CF88:ART.60', 'CF88:ART.60:PAR.4', 'CF88:ART.60:PAR.4:INC.IV')
ROUND_D_AS_IS = ('CF88:ART.51:INC.I', 'CF88:ART.52:INC.X')
ROUND_D_ADJUSTED = ('CF88:ART.52:PAR.UNICO', 'CF88:ART.53:CAPUT', 'CF88:ART.53:PAR.1', 'CF88:ART.53:PAR.2', 'CF88:ART.55:INC.VI', 'CF88:ART.58:PAR.3',
                    'CF88:ART.62:PAR.6', 'CF88:ART.63', 'CF88:ART.75')
ROUND_C_AS_IS = ('CF88:ART.43', 'CF88:ART.45:PAR.1', 'CF88:ART.54:INC.I', 'CF88:ART.55:PAR.2', 'CF88:ART.57:PAR.6', 'CF88:ART.61', 'CF88:ART.66:PAR.4',
                 'CF88:ART.71')
ROUND_C_ADJUSTED = ('CF88:ART.53:PAR.3', 'CF88:ART.57', 'CF88:ART.61:PAR.1', 'CF88:ART.62', 'CF88:ART.73:PAR.1')
APPROVED = ROUND_D_AS_IS + ROUND_D_ADJUSTED + ROUND_C_AS_IS + ROUND_C_ADJUSTED
SCOPE = {'D': 'CF88_BATCH06_TRIAGE_QUEUE_D', 'C': 'CF88_BATCH06_TRIAGE_QUEUE_C'}
REQUIRED_SOURCES = {'CF88:ART.52:PAR.UNICO': ('MS 34.418', '25/09/2023', 'MS 21.689'), 'CF88:ART.53:CAPUT': ('Inq 4.781 Ref', 'Tema 950'),
                    'CF88:ART.53:PAR.1': ('HC 232.627', 'Inq 4.787-QO'), 'CF88:ART.55:INC.VI': ('AP 694',), 'CF88:ART.62:PAR.6': ('MS 27.931',),
                    'CF88:ART.63': ('ADI 3.114', 'ADI 2.681 MC', 'Tema 686'), 'CF88:ART.75': ('Emenda Constitucional nº 139',)}
COMPLEXITY_ONLY = {'QUORUM', 'DEADLINE', 'NUMBER_OR_PERCENTAGE', 'EXCEPTION', 'COMPLEX_REMISSION', 'BLOCK_MULTI_DEPENDENCY', 'LAW_DEPENDENCY',
                   'EC_WORDING', 'REMISSION_OR_LIST'}


def load(name):
    return json.loads((BD / name).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def with_text(rec, section, before_after):
    """Copy of a record whose section has the 'after' text of a logged edit replaced by its 'before' (the checkpoint wording)."""
    r = copy.deepcopy(rec)
    for after, before in before_after:
        r['content'][section] = r['content'][section].replace(after, before)
    return r


class Batch06(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.catalog = V.load_catalog()
        cls.spec = load('BATCH_SPEC.json')
        cls.all = E.load_corpus(BD / 'CF88_BATCH_06.entenda.jsonl')
        cls.corpus = [r for r in cls.all if r['status'] == 'ACTIVE']
        cls.pre = E.load_corpus(BD / 'CF88_BATCH_06_PRE_ROUND_D.entenda.jsonl')
        cls.pre_by = {r['target_id']: r for r in cls.pre}
        cls.pre_tri = {x['target_id']: x for x in load('BATCH06_TRIAGE_PRE_ROUND_D.json')['rows']}
        cls.pre_tri_c = {x['target_id']: x for x in load('BATCH06_TRIAGE_PRE_ROUND_C.json')['rows']}
        cls.by = {r['target_id']: r for r in cls.corpus}
        cls.sel = load('SELECTION_REPORT.json')
        cls.tri = load('BATCH06_TRIAGE.json')
        cls.rows = {x['target_id']: x for x in cls.tri['rows']}
        cls.chk = load('EDITORIAL_CHECKS.json')
        cls.log = load('RECALIBRATION_EDITORIAL_LOG.json')

    def edit(self, target, section):
        return [(e['after'], e['before']) for e in self.log['edits'] if e['target_id'] == target and e['section'] == section]

    # ------------------------------------------------------------ selection and status (unchanged contract of the checkpoint)

    def test_scope_and_prior_corpora(self):
        self.assertEqual(self.spec['scope'], [f'CF88:ART.{n}' for n in range(42, 76)])
        self.assertIn('ENTENDA_ENGINE/derived/production_batch_05/CF88_BATCH_05.entenda.jsonl', self.spec['prior_corpora'])
        self.assertEqual(sorted(self.spec['reused']), sorted(PILOTS))

    def test_only_queues_d_and_c_approved(self):
        cfg = V.load_json(V.CONFIG)
        self.assertFalse(cfg['AUTO_APPROVE_LOW'])
        self.assertFalse(cfg['AUTO_APPROVE_MEDIUM'])
        self.assertFalse(cfg['MICROAUTO_APPLY'])
        self.assertEqual(len(self.corpus), 93)
        approved = sorted(r['target_id'] for r in self.corpus if r['review_status'] == 'HUMAN_APPROVED_T1')
        self.assertEqual(approved, sorted(APPROVED))
        for t in ROUND_D_AS_IS + ROUND_D_ADJUSTED:                      # the 11 of round D came from queue D of the recalibrated triage
            self.assertEqual(self.pre_tri[t]['queue'], 'D_FULL_HUMAN_REVIEW', t)
            self.assertEqual(self.by[t]['human_review']['review_scope'], SCOPE['D'], t)
        for t in ROUND_C_AS_IS + ROUND_C_ADJUSTED:                      # the 13 of round C came from queue C of the same triage
            self.assertEqual(self.pre_tri_c[t]['queue'], 'C_QUICK_REVIEW', t)
            self.assertEqual(self.by[t]['human_review']['review_scope'], SCOPE['C'], t)
            self.assertEqual(self.by[t]['human_review']['calibration_queue'], 'C', t)
        self.assertEqual(sorted(t for t, x in self.pre_tri_c.items() if x['queue'] == 'C_QUICK_REVIEW'), sorted(ROUND_C_AS_IS + ROUND_C_ADJUSTED))
        pending = [r for r in self.corpus if r['review_status'] == 'PENDING_HUMAN_REVIEW']
        self.assertEqual(len(pending), 69)
        self.assertTrue(all(self.pre_tri_c[r['target_id']]['queue'] in ('A_CLEAN_LOW', 'B_CLEAN_MEDIUM') for r in pending))
        self.assertEqual(self.tri['human_approved_t1_granted'], 24)
        self.assertEqual(self.sel['summary']['review_status_counts'], {'HUMAN_APPROVED_T1': 27, 'PENDING_HUMAN_REVIEW': 69})
        tot = self.tri['approval_totals']
        self.assertEqual((tot['global_before'], tot['global_after'], tot['batch06_new_pending']), (289, 313, 69))
        for name, counts in (('ROUND_D_HUMAN_REVIEW_DECISIONS.json', {'APPROVED': 2, 'APPROVED_AFTER_ADJUSTMENT': 9, 'REJECTED': 0}),
                             ('ROUND_C_HUMAN_REVIEW_DECISIONS.json', {'APPROVED': 8, 'APPROVED_AFTER_ADJUSTMENT': 5, 'REJECTED': 0})):
            dec = load(name)
            self.assertEqual(dec['review_status'], 'ROUND_REVIEW_COMPLETED')
            self.assertEqual(dec['decision_counts'], counts)
            for ev, h in dec['original_evidence_sha256'].items():
                self.assertEqual(sha(BD / ev), h, ev)
        self.assertEqual([ra['review_scope'] for ra in self.spec['round_approvals']], [SCOPE['D'], SCOPE['C']])

    def test_round_d_and_c_versions_and_history(self):
        retired = {r['target_id']: r for r in self.all if r['status'] == 'RETIRED'}
        self.assertEqual(sorted(retired), sorted(ROUND_D_ADJUSTED + ROUND_C_ADJUSTED))
        for t in ROUND_D_ADJUSTED + ROUND_C_ADJUSTED:
            old, new = retired[t], self.by[t]
            self.assertEqual((old['editorial_version'], new['editorial_version']), (1, 2), t)
            self.assertEqual(old['review_status'], 'CHANGES_REQUESTED', t)
            self.assertEqual(old['superseded_by'], new['explanation_id'], t)
            self.assertEqual(old['content'], self.pre_by[t]['content'], t)            # earlier version preserved, never overwritten
            self.assertEqual(old['source'], self.pre_by[t]['source'], t)
            self.assertEqual(new['human_review']['decision'], 'APPROVED_AFTER_ADJUSTMENT', t)
        for t in ROUND_D_AS_IS + ROUND_C_AS_IS:                          # approved without rewriting content: same version and bytes
            r = self.by[t]
            self.assertEqual(r['editorial_version'], 1)
            self.assertEqual(r['content'], self.pre_by[t]['content'])
            self.assertEqual(r['external_layer_notes'], self.pre_by[t]['external_layer_notes'])
            self.assertEqual(r['human_review']['decision'], 'APPROVED')
        self.assertEqual(V.version_chain_findings(self.all, self.pre), [])

    def test_round_d_provenance_and_sources(self):
        for t in ROUND_D_ADJUSTED:
            prov = self.by[t]['human_review']['content_provenance']
            self.assertTrue(prov, t)
            self.assertTrue(all(p['source_type'] == 'HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE' for p in prov), t)
            notes = ' '.join(self.by[t]['external_layer_notes'])
            for ref in REQUIRED_SOURCES.get(t, ()):
                self.assertIn(ref, notes, (t, ref))
        recs = load('JURISPRUDENCE_LINK_RECOMMENDATIONS.json')
        self.assertTrue(all(r['status'] == 'PENDING_EXTERNAL_INGESTION' for r in recs['recommendations']))   # nothing fabricated locally
        self.assertIn('MS 27.931 (STF)', {r['desired_reference'] for r in recs['recommendations']})

    def test_round_d_approval_gate(self):
        gate = self.tri['round_approvals']['gate']
        self.assertEqual(sorted(g['target_id'] for g in gate), sorted(APPROVED))
        for g in gate:
            self.assertEqual(g['gate'], 'PASS', g['target_id'])
            self.assertEqual((g['hard_fail'], g['review_required_open'], g['editorial_checks_open']), ([], [], 0), g['target_id'])
        open_ = {r['target_id']: r['unresolved'] for r in self.chk['rows']}
        self.assertTrue(all(open_[t] == 0 for t in APPROVED))

    def test_round_c_resolutions_and_wording(self):
        dec = {d['target_id']: d for d in load('ROUND_C_HUMAN_REVIEW_DECISIONS.json')['decisions']}
        self.assertEqual(sorted(dec), sorted(ROUND_C_AS_IS + ROUND_C_ADJUSTED))
        known = V.load_json(V.KNOWN)['resolutions']
        c = BP.Context(BD, self.ctx, self.catalog, {}, V3.load_registry(), load('BATCH06_RELATIONS_PIN.json'))
        bare = {}                                                        # the gate's validator context without the recorded known resolutions
        for t, d in dec.items():
            r = self.by[t]
            open_bare = [f for f in c.validate(r) if f['severity'] in ('REVIEW_REQUIRED', 'HARD_FAIL')]
            bare[t] = {f['code'] for f in open_bare}
            decided = {x['flag'] for x in d.get('flag_resolutions', [])}
            self.assertFalse([f for f in open_bare if f['severity'] == 'HARD_FAIL'], t)
            self.assertTrue(bare[t] <= decided, (t, bare[t] - decided))  # every open flag has an explicit human resolution
            reg = known.get(r['explanation_id'], {})
            self.assertEqual(bool(reg), bool(bare[t]), t)                 # resolutions only where a flag stays open, on the approved version
            self.assertTrue(all(k.split(':', 1)[0] in decided for k in reg), t)
        self.assertEqual({t for t, v in bare.items() if not v}, {'CF88:ART.45:PAR.1', 'CF88:ART.61:PAR.1', 'CF88:ART.62'})
        c9 = self.by['CF88:ART.61:PAR.1']
        diz = c9['content']['o_que_diz']                                 # omission fixed by the wording itself (no resolution registered)
        for term in ('empregos', 'servidores da União e dos Territórios', 'Distrito Federal', 'normas gerais', 'Ministério Público',
                     'Defensoria Pública da União', 'Ministérios e órgãos', 'militares das Forças Armadas', 'regime jurídico',
                     'transferência para a reserva'):
            self.assertIn(term, diz, term)
        src = [w.lower() for w in E.words(c9['source']['source_text_snapshot'])]
        grams = {tuple(src[i:i + 10]) for i in range(len(src) - 9)}
        w = [x.lower() for x in E.words(diz)]
        self.assertFalse([i for i in range(len(w) - 9) if tuple(w[i:i + 10]) in grams])   # longest literal run < 10 words
        c13 = self.by['CF88:ART.73:PAR.1']
        self.assertIn('sessenta e cinco anos', c13['content']['atencao'])                 # historical number kept, resolved by official source
        self.assertNotIn('TCU', c13['content']['atencao'])
        self.assertIn('NUMBER_NOT_IN_TEXT:65', known[c13['explanation_id']])
        self.assertEqual(bare['CF88:ART.73:PAR.1'], {'NUMBER_NOT_IN_TEXT'})
        for t in ('CF88:ART.53:PAR.3', 'CF88:ART.57', 'CF88:ART.62', 'CF88:ART.73:PAR.1'):
            self.assertRegex(self.by[t]['content']['atencao'], r'Emenda Constitucional nº \d+, de \d{4}')
        prov = self.by['CF88:ART.45:PAR.1']['human_review']['content_provenance']
        self.assertEqual([p['human_reason_code'] for p in prov], ['OFFICIAL_CANONICAL_ANNOTATION'])
        self.assertEqual(self.by['CF88:ART.45:PAR.1']['content'], self.pre_by['CF88:ART.45:PAR.1']['content'])   # T1 byte-identical

    def test_every_current_target_selected_or_skipped_with_reason(self):
        rows = self.sel['selection']
        cur = [r for r in rows if r['status'] == 'CURRENT']
        self.assertEqual(len(rows), 318)
        self.assertEqual(len(cur), 309)
        self.assertEqual(sum(1 for r in rows if r['classification'] == 'EXCLUDED_HISTORICAL'), 9)
        for r in cur:
            self.assertTrue(r.get('selection_reason'), r['target_id'])
        skips = [r for r in cur if r['classification'] == 'NO_SEPARATE_EXPLANATION']
        self.assertEqual(len(skips), 213)
        self.assertEqual(len(cur) - len(skips), 96)
        self.assertTrue(all(r.get('covered_by') for r in skips))

    def test_article_60_only_pilots(self):
        own60 = [r['target_id'] for r in self.corpus if r['target_id'] == 'CF88:ART.60' or r['target_id'].startswith('CF88:ART.60:')]
        self.assertEqual(own60, [])

    def test_no_historical_target_explained(self):
        for r in self.corpus:
            for t in [r['target_id']] + r['granularity'].get('covered_targets', []):
                self.assertEqual(self.ctx.effective_status(t), 'CURRENT', t)

    # ------------------------------------------------------------ reproducibility from Git

    def test_text_source_reconstruction_is_byte_exact(self):
        for rel, rec in TSR.recipes().items():
            data = TSR.reconstruct(rel)
            self.assertEqual(hashlib.sha256(data).hexdigest(), rec['sha256'])
            if (ROOT / rel).is_file():
                self.assertEqual((ROOT / rel).read_bytes(), data, rel)
        ops = {r['source']['text_source_file_sha256'] for r in self.corpus}
        self.assertEqual(ops, {TSR.recipes()['updater/saida/1- CONSTITUIÇÃO FEDERAL/constituicao_federal_1988.txt']['sha256']})

    def test_recalibration_log_matches_drafts(self):
        drafts = {e['target_id']: e for e in load('BATCH_06_DRAFTS_PRE_ROUND_D.json')['explanations']}   # ROUND_0B edits precede round D
        for e in self.log['edits']:
            d = drafts[e['target_id']]
            text = '\n'.join(d['external_layer_notes']) if e['section'] == 'external_layer_notes' else d['content'][e['section']]
            self.assertIn(e['after'], text, e['target_id'])
            self.assertNotIn(e['before'], text, e['target_id'])
        pre = load('PRE_RECALIBRATION_MANIFEST.json')
        self.assertEqual(pre['commit'][:7], '7c59f2e')
        self.assertEqual(len(pre['queues_by_target']), 93)
        self.assertEqual(sum(1 for v in pre['queues_by_target'].values() if v['queue'] == 'D_FULL_HUMAN_REVIEW'), 89)

    def test_rebuild_is_byte_identical(self):
        ev = load('DETERMINISM_EVIDENCE.json')
        self.assertTrue(ev['byte_identical'])
        self.assertGreaterEqual(ev['runs'], 3)
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp) / 'production_batch_06'
            td.mkdir()
            for n in B.INPUTS:
                shutil.copy(BD / n, td / n)
            B.build(td)
            for n, h in ev['sha256'].items():
                self.assertEqual(sha(td / n), h, n)
                self.assertEqual(sha(BD / n), h, n)

    # ------------------------------------------------------------ two axes

    def test_legal_risk_separated_from_complexity(self):
        risk = load('EDITORIAL_REVIEW_INPUT.json')['risk']
        self.assertEqual(sorted(risk), sorted(self.by))
        for t, v in risk.items():
            self.assertIn(v['verification_complexity'], ('SIMPLE', 'STRUCTURED', 'EXTERNAL'))
            if v['level'] == 'HIGH':
                self.assertTrue(set(v['rules']) <= set(R.LEGAL_HIGH), t)
            self.assertFalse(set(v['rules']) & COMPLEXITY_ONLY, t)       # numbers/quorum/BLOCK/EC never set the legal level
        # quorum and numbers only: structured, not HIGH
        for t in ('CF88:ART.47', 'CF88:ART.45:PAR.1', 'CF88:ART.60', 'CF88:ART.64:PAR.2'):
            if t in risk:
                self.assertNotEqual(risk[t]['level'], 'HIGH', t)
                self.assertIn(risk[t]['verification_complexity'], ('STRUCTURED', 'EXTERNAL'), t)
        rec = self.by['CF88:ART.49:INC.IX']
        self.assertNotIn('COMPLEX_REMISSION', R.classify(rec, self.ctx)['rules'])  # legacy classifier: snapshot ids are not remissions

    def test_jurisprudence_context_vs_required(self):
        jur = {t: x['jurisprudence'] for t, x in self.pre_tri.items()}     # routing of the pending drafts that went to round D
        for t in ('CF88:ART.53:PAR.1', 'CF88:ART.62:PAR.6', 'CF88:ART.55:INC.VI'):
            self.assertEqual(jur[t], 'REQUIRED_FOR_CORRECTNESS', t)
            self.assertEqual(self.pre_tri[t]['queue'], 'D_FULL_HUMAN_REVIEW', t)
        for t in ('CF88:ART.49:INC.I', 'CF88:ART.69', 'CF88:ART.71:INC.III'):
            self.assertEqual(jur[t], 'CONTEXT_ONLY', t)
            self.assertNotEqual(self.rows[t]['queue'], 'D_FULL_HUMAN_REVIEW', t)

    def test_art75_official_evidence_and_ambiguity_closed(self):
        r = self.by['CF88:ART.75']
        body = (ROOT / 'updater/fontes_oficiais_senado/CF88/16434817_5beff7a4/normalizado.txt').read_text(encoding='utf-8')
        self.assertEqual(body.count('vedada sua extinção, criação ou instalação'), 2)     # art. 31, par. 1o, and art. 75 (EC 139/2026)
        self.assertFalse(any('EXTERNAL_VERIFICATION_REQUIRED' in n for n in r['external_layer_notes']))
        risk = load('EDITORIAL_REVIEW_INPUT.json')['risk']['CF88:ART.75']
        self.assertNotIn('CONSTITUTIONAL_AMBIGUITY', risk['rules'])
        self.assertIn('art. 31, § 4º', r['content']['atencao'])
        self.assertIn('Verificacao externa encerrada', load('BATCH06_TARGET_PLAN.json')['vigency_findings']['ART75_EC139_2026'])
        codes = {f['code'] for f in V3.validate(r, self.ctx, self.catalog)}
        self.assertIn('SEMANTIC_AMBIGUITY_RESOLVED', codes)
        # without the recorded resolution the same paraphrase would still be routed to D (the rule is data-driven, not per target)
        reg = V3.load_registry()
        reg['entries'] = [{k: v for k, v in e.items() if k != 'resolution'} for e in reg['entries']]
        open_codes = {f['code'] for f in V3.validate(r, self.ctx, self.catalog, registry=reg) if f['severity'] == 'REVIEW_REQUIRED'}
        self.assertIn('SEMANTIC_AMBIGUITY_REVIEW_REQUIRED', open_codes)
        # regression of the checkpoint paraphrase on the pre-round wording (registry without resolution)
        pre = self.pre_by['CF88:ART.75']
        old = with_text(pre, 'o_que_diz', self.edit('CF88:ART.75', 'o_que_diz'))
        self.assertIn('SEMANTIC_AMBIGUITY_REVIEW_REQUIRED', {f['code'] for f in V3.validate(old, self.ctx, self.catalog, registry=reg)
                                                             if f['severity'] == 'REVIEW_REQUIRED'})

    def test_round_d_generalized_rules(self):
        pre, now = self.pre_by['CF88:ART.53:PAR.2'], self.by['CF88:ART.53:PAR.2']
        self.assertIn('PRISON_SCOPE_UNQUALIFIED', {f['code'] for f in V3.validate(pre, self.ctx, self.catalog)})       # absolute prison ban
        self.assertNotIn('PRISON_SCOPE_UNQUALIFIED', {f['code'] for f in V3.validate(now, self.ctx, self.catalog)})   # cautelar x prisao-pena
        bare = copy.deepcopy(now)
        bare['human_review'] = {}
        codes = {f['code'] for f in V3.validate(bare, self.ctx, self.catalog) if f['severity'] == 'REVIEW_REQUIRED'}
        self.assertIn('JURISPRUDENCE_CLAIM_WITHOUT_PROVENANCE', codes)                  # current precedent needs provenance
        self.assertIn('JURISPRUDENCE_CLAIM_WITH_PROVENANCE', {f['code'] for f in V3.validate(now, self.ctx, self.catalog)})
        pending_codes = {d['code'] for x in self.tri['rows'] for d in x['detectors']}
        self.assertFalse(pending_codes & {'PRISON_SCOPE_UNQUALIFIED', 'JURISPRUDENCE_CLAIM_WITHOUT_PROVENANCE'})   # no new noise on the 82

    def test_art45_par1_resolver_status_preserved(self):
        x = self.pre_tri_c['CF88:ART.45:PAR.1']                              # triage row of the draft reviewed in round C
        self.assertEqual(x['external_resolution']['status'], X.PENDING)            # relation PENDING: not promoted
        self.assertEqual(x['external_resolution']['via'], 'RELATIONS_ENGINE_PENDING')
        self.assertIn('Lei Complementar nº 78, de 1993', x['external_dependency'])   # full identification (no "nº 7" truncation)
        self.assertNotEqual(x['legal_risk'], 'HIGH')                                # T1 core does not depend on the external law

    # ------------------------------------------------------------ deterministic checks (regressions from the checkpoint)

    def test_number_check_catches_derived_totals(self):
        r = copy.deepcopy(self.by['CF88:ART.52:PAR.UNICO'])
        r['content']['o_que_significa'] = 'O quórum é qualificado: dois terços dos votos do Senado, ou seja, 54 dos 81 senadores.'
        fs = [f for f in V3.validate(r, self.ctx, self.catalog) if f['code'] == 'NUMBER_NOT_IN_TEXT']
        self.assertTrue(fs)
        self.assertIn('54', fs[0]['match'])
        self.assertIn('81', fs[0]['match'])
        r['content']['o_que_significa'] = 'O quórum é qualificado: dois terços dos votos do Senado.'
        self.assertFalse([f for f in V3.validate(r, self.ctx, self.catalog) if f['code'] == 'NUMBER_NOT_IN_TEXT'])

    def test_quantities_parser(self):
        q = V3.quantities
        self.assertEqual(q('prazo de cento e vinte dias'), {('n', '120')})
        self.assertEqual(q('dois terços dos membros'), {('frac', '2/3')})
        self.assertEqual(q('mais da metade'), {('frac', '1/2')})
        self.assertEqual(q('cinco por cento do eleitorado'), {('pct', '5')})
        self.assertEqual(q('área superior a dois mil e quinhentos hectares'), {('n', '2500')})
        self.assertEqual(q('nos arts. 45 e 46 e no art. 142, §§ 2º e 3º'), set())            # device references
        self.assertEqual(q('Emenda Constitucional nº 35, de 2001'), set())                   # amendment number and year
        self.assertEqual(q('as duas Casas do Congresso'), set())                            # counting word without a legal unit
        self.assertEqual(q('mandato de 2 (dois) anos'), {('n', '2')})
        r = copy.deepcopy(self.by['CF88:ART.62:PAR.6'])
        r['content']['o_que_diz'] = 'Se a medida provisória não for apreciada em até cento e vinte dias, entra em regime de urgência.'
        self.assertTrue([f for f in V3.validate(r, self.ctx, self.catalog) if f['code'] == 'NUMBER_NOT_IN_TEXT'])

    def test_ressalva_in_overview_regression_art49(self):
        r = self.by['CF88:ART.49']
        old = with_text(r, 'o_que_diz', self.edit('CF88:ART.49', 'o_que_diz'))
        fs = [f for f in V3.validate(old, self.ctx, self.catalog) if f['code'] == 'RESSALVA_OMITTED_IN_SUMMARY']
        self.assertTrue(fs)
        self.assertIn('ART.49:INC.II', fs[0]['detail'])
        self.assertFalse([f for f in V3.validate(r, self.ctx, self.catalog) if f['code'] == 'RESSALVA_OMITTED_IN_SUMMARY'])

    def test_list_completeness_regression_art68_par1(self):
        r = self.by['CF88:ART.68:PAR.1']
        old = with_text(r, 'o_que_diz', self.edit('CF88:ART.68:PAR.1', 'o_que_diz'))
        fs = [f for f in V3.validate(old, self.ctx, self.catalog) if f['code'] == 'LIST_ITEM_POSSIBLY_DROPPED']
        self.assertTrue(any('carreira' in f['detail'] for f in fs))
        self.assertFalse([f for f in V3.validate(r, self.ctx, self.catalog) if f['code'] == 'LIST_ITEM_POSSIBLY_DROPPED'])

    def test_teleology_true_positives_kept_false_positives_refined(self):
        for t in ('CF88:ART.49:INC.V', 'CF88:ART.53:PAR.3', 'CF88:ART.57:PAR.2', 'CF88:ART.62:PAR.1', 'CF88:ART.62:PAR.6', 'CF88:ART.64:PAR.2', 'CF88:ART.67'):
            e = next(e for e in self.log['edits'] if e['target_id'] == t and e['category'] == 'TELEOLOGY')
            old = with_text(self.pre_by[t], e['section'], [(e['after'], e['before'])])
            codes = {f['code'] for f in V3.validate(old, self.ctx, self.catalog) if f['severity'] == 'REVIEW_REQUIRED'}
            self.assertIn('TELEOLOGY_SPECULATIVE', codes, t)
            now = {f['code'] for f in V3.validate(self.pre_by[t], self.ctx, self.catalog) if f['severity'] == 'REVIEW_REQUIRED'}
            self.assertNotIn('TELEOLOGY_SPECULATIVE', now, t)
        refined = {(x['target_id'], i['code']) for x in self.pre_tri.values() for i in x['info'] if i['code'] in ('TELEOLOGY_SPECULATIVE', 'UNIVERSAL_CLAIM',
                                                                                                          'AUTOMATIC_CONSEQUENCE')}
        for pair in (('CF88:ART.43', 'TELEOLOGY_SPECULATIVE'), ('CF88:ART.68', 'TELEOLOGY_SPECULATIVE'), ('CF88:ART.46', 'UNIVERSAL_CLAIM'),
                     ('CF88:ART.51:INC.I', 'UNIVERSAL_CLAIM'), ('CF88:ART.67', 'UNIVERSAL_CLAIM'), ('CF88:ART.57:PAR.7', 'AUTOMATIC_CONSEQUENCE')):
            self.assertIn(pair, refined)
        self.assertEqual(self.tri['validator_v3_regression_batch05']['lost_by_v3'], [])   # refinements lose no Batch05 true positive

    def test_external_claim_without_evidence_is_review(self):
        r = copy.deepcopy(self.by['CF88:ART.52:INC.I'])
        r['content']['o_que_significa'] += ' A Lei nº 1.079, de 1950, estabelece o rito completo do julgamento.'
        fs = [f for f in V3.validate(r, self.ctx, self.catalog) if f['code'] == 'EXTERNAL_NORMATIVE_CONTENT_CLAIM']
        self.assertTrue(fs)
        self.assertEqual(fs[0]['route'], 'FULL')

    # ------------------------------------------------------------ queues and packets

    def test_queues_and_packets(self):
        c = self.tri['counts']
        self.assertEqual(c['E_HARD_FAIL'], 0)
        self.assertIn('Total: **0**', (BD / 'BATCH06_HARD_FAIL_REPORT.md').read_text(encoding='utf-8'))
        self.assertEqual(sum(c.values()), 69)                            # the 11 of round D and the 13 of round C leave the triage
        self.assertEqual((c['A_CLEAN_LOW'], c['B_CLEAN_MEDIUM'], c['C_QUICK_REVIEW'], c['D_FULL_HUMAN_REVIEW']), (42, 27, 0, 0))
        self.assertTrue((BD / 'BATCH06_FULL_HUMAN_REVIEW.md').is_file())
        self.assertFalse((BD / 'BATCH06_D_ESCALATION_DIAGNOSTIC.md').is_file())
        full = (BD / 'BATCH06_FULL_HUMAN_REVIEW.md').read_text(encoding='utf-8')
        compact = (BD / 'BATCH06_COMPACT_CLEAN_REVIEW.md').read_text(encoding='utf-8')
        quick = (BD / 'BATCH06_QUICK_REVIEW.md').read_text(encoding='utf-8')
        for t in APPROVED:
            self.assertNotIn(f"`{t}`", compact + quick + full)
        for x in self.tri['rows']:
            t, q = x['target_id'], x['queue']
            if q == 'D_FULL_HUMAN_REVIEW':
                self.assertIn(f"`{t}`", full)
                self.assertNotIn(f"### `{t}`", compact)
                self.assertTrue(x['legal_risk'] == 'HIGH' or any(d['route'] == 'FULL' for d in x['detectors']), t)
            else:
                self.assertNotIn(f"`{t}` ·", full)
            if q in ('A_CLEAN_LOW', 'B_CLEAN_MEDIUM'):
                self.assertIn(f"### `{t}`", compact)
                self.assertFalse([d for d in x['detectors'] if d['severity'] == 'REVIEW_REQUIRED'], t)
                self.assertEqual(q == 'A_CLEAN_LOW', x['legal_risk'] == 'LOW', t)
            if q == 'C_QUICK_REVIEW':
                self.assertIn(f"## `{t}`", quick)
                self.assertNotEqual(x['legal_risk'], 'HIGH', t)
        for field in ('Risco:', 'complexidade:', 'Ponto jurídico:', 'Interpretação principal:', 'ATENÇÃO:', 'Dependência externa:', 'Warnings:',
                      'Motivo da fila:'):
            self.assertIn(field, compact)
        self.assertIn('nenhum item nesta fila', quick)                 # queue C fully decided in round C
        for field in ('**Detector:**', '**Motivo:**', '**Proposta de correção segura:**'):
            self.assertIn(field, (BD / 'BATCH06_QUICK_REVIEW_PRE_ROUND_C.md').read_text(encoding='utf-8'))

    def test_migration_of_previous_d(self):
        m = self.tri['migration']
        old_d = {t for t, v in load('PRE_RECALIBRATION_MANIFEST.json')['queues_by_target'].items() if v['queue'] == 'D_FULL_HUMAN_REVIEW'}
        self.assertEqual(len(old_d & set(APPROVED)), 24)
        self.assertEqual(m['previous_D'] + 24, 89)                        # old D decided in round D (11) and round C (13) leave the triage
        self.assertEqual(m['previous_D_migrated'], m['previous_D'] - m['previous_D_now'].get('D_FULL_HUMAN_REVIEW', 0))
        self.assertGreater(m['previous_D_migrated'], 0)

    def test_volume_reduction_measured(self):
        m = self.tri['metrics']
        self.assertEqual(m['presented_chars'], sum(m['presented_by_file'].values()))
        self.assertLess(m['presented_chars'], m['old_model_full_package_chars'])
        self.assertLess(m['presented_chars'], m['checkpoint_presented_chars'])
        for name, n in m['presented_by_file'].items():
            self.assertEqual(len((BD / name).read_text(encoding='utf-8')), n, name)

    def test_micro_adjustments_not_applied(self):
        m = load('MICRO_ADJUSTMENTS_LOG.json')
        self.assertFalse(m['microauto_apply'])
        self.assertEqual(m['applied'], 0)

    def test_editorial_open_findings_are_routed(self):
        open_ = {r['target_id'] for r in self.chk['rows'] if r['unresolved']}
        for t in open_:
            self.assertIn(self.rows[t]['queue'], ('C_QUICK_REVIEW', 'D_FULL_HUMAN_REVIEW'), t)

    # ------------------------------------------------------------ frozen baseline untouched

    def test_batch05_untouched(self):
        p = 'ENTENDA_ENGINE/derived/production_batch_05/CF88_BATCH_05.entenda.jsonl'
        head = subprocess.run(['git', 'show', f'HEAD:{p}'], cwd=ROOT, capture_output=True, check=True).stdout
        self.assertEqual(hashlib.sha256(head).hexdigest(), sha(ROOT / p))
        base = subprocess.run(['git', 'diff', '--name-only', 'f1a6966ad35e5786a88e1f4806cef6bf1a65d3ba', '--', 'ENTENDA_ENGINE/derived/production_batch_05',
                               'ENTENDA_ENGINE/corpus'], cwd=ROOT, capture_output=True, text=True)
        if base.returncode == 0:                                                     # baseline commit present (not a too-shallow clone)
            self.assertEqual(base.stdout.strip(), '')


if __name__ == '__main__':
    unittest.main()
