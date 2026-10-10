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
import editorial_checks as EC  # noqa: E402
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
ROUND_B1_AS_IS = ('CF88:ART.50',)
ROUND_B1_ADJUSTED = ('CF88:ART.48', 'CF88:ART.49:INC.I', 'CF88:ART.50:PAR.2', 'CF88:ART.52', 'CF88:ART.52:INC.I', 'CF88:ART.53', 'CF88:ART.53:PAR.8',
                     'CF88:ART.55')
ROUND_B2_AS_IS = ('CF88:ART.57:PAR.4',)
ROUND_B2_ADJUSTED = ('CF88:ART.55:PAR.1', 'CF88:ART.55:PAR.4', 'CF88:ART.56', 'CF88:ART.62:PAR.1', 'CF88:ART.62:PAR.5', 'CF88:ART.65', 'CF88:ART.66',
                     'CF88:ART.66:PAR.1')
ROUND_B3_AS_IS = ()
ROUND_B3_ADJUSTED = ('CF88:ART.69', 'CF88:ART.71:INC.III', 'CF88:ART.71:INC.VIII', 'CF88:ART.71:PAR.1', 'CF88:ART.71:PAR.3', 'CF88:ART.73',
                     'CF88:ART.73:PAR.3', 'CF88:ART.74', 'CF88:ART.74:PAR.1')
ROUND_A1_AS_IS = ('CF88:ART.44', 'CF88:ART.53:PAR.6')
ROUND_A1_ADJUSTED = ('CF88:ART.42', 'CF88:ART.42:PAR.1', 'CF88:ART.42:PAR.3', 'CF88:ART.43:PAR.2', 'CF88:ART.45', 'CF88:ART.46', 'CF88:ART.47',
                     'CF88:ART.49', 'CF88:ART.49:INC.V', 'CF88:ART.49:INC.IX', 'CF88:ART.51', 'CF88:ART.52:INC.III', 'CF88:ART.54')
ROUND_A2_AS_IS = ('CF88:ART.56:PAR.1', 'CF88:ART.57:PAR.2', 'CF88:ART.58', 'CF88:ART.61:PAR.2')
ROUND_A2_ADJUSTED = ('CF88:ART.54:INC.II', 'CF88:ART.57:PAR.7', 'CF88:ART.58:PAR.2', 'CF88:ART.59', 'CF88:ART.62:PAR.2', 'CF88:ART.62:PAR.3',
                     'CF88:ART.62:PAR.10', 'CF88:ART.62:PAR.11', 'CF88:ART.64', 'CF88:ART.64:PAR.2', 'CF88:ART.66:PAR.7')
ROUND_A3_AS_IS = ('CF88:ART.70',)
ROUND_A3_ADJUSTED = ('CF88:ART.67', 'CF88:ART.68', 'CF88:ART.68:PAR.1', 'CF88:ART.68:PAR.2', 'CF88:ART.70:PAR.UNICO', 'CF88:ART.71:INC.I',
                     'CF88:ART.71:INC.II', 'CF88:ART.71:INC.IX', 'CF88:ART.72', 'CF88:ART.73:PAR.2', 'CF88:ART.74:PAR.2')
APPROVED = (ROUND_D_AS_IS + ROUND_D_ADJUSTED + ROUND_C_AS_IS + ROUND_C_ADJUSTED + ROUND_B1_AS_IS + ROUND_B1_ADJUSTED + ROUND_B2_AS_IS
            + ROUND_B2_ADJUSTED + ROUND_B3_AS_IS + ROUND_B3_ADJUSTED + ROUND_A1_AS_IS + ROUND_A1_ADJUSTED + ROUND_A2_AS_IS + ROUND_A2_ADJUSTED
            + ROUND_A3_AS_IS + ROUND_A3_ADJUSTED)
SCOPE = {'D': 'CF88_BATCH06_TRIAGE_QUEUE_D', 'C': 'CF88_BATCH06_TRIAGE_QUEUE_C', 'B1': 'CF88_BATCH06_TRIAGE_QUEUE_B_PART1',
         'B2': 'CF88_BATCH06_TRIAGE_QUEUE_B_PART2', 'B3': 'CF88_BATCH06_TRIAGE_QUEUE_B_PART3', 'A1': 'CF88_BATCH06_TRIAGE_QUEUE_A_PART1',
         'A2': 'CF88_BATCH06_TRIAGE_QUEUE_A_PART2', 'A3': 'CF88_BATCH06_TRIAGE_QUEUE_A_PART3'}
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
        cls.pre_tri_b1 = {x['target_id']: x for x in load('BATCH06_TRIAGE_PRE_ROUND_B1.json')['rows']}
        cls.pre_tri_b2 = {x['target_id']: x for x in load('BATCH06_TRIAGE_PRE_ROUND_B2.json')['rows']}
        cls.pre_tri_b3 = {x['target_id']: x for x in load('BATCH06_TRIAGE_PRE_ROUND_B3.json')['rows']}
        cls.pre_tri_a1 = {x['target_id']: x for x in load('BATCH06_TRIAGE_PRE_ROUND_A1.json')['rows']}
        cls.pre_tri_a2 = {x['target_id']: x for x in load('BATCH06_TRIAGE_PRE_ROUND_A2.json')['rows']}
        cls.pre_tri_a3 = {x['target_id']: x for x in load('BATCH06_TRIAGE_PRE_ROUND_A3.json')['rows']}
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
        for t in ROUND_B1_AS_IS + ROUND_B1_ADJUSTED:                    # os 9 da rodada B1 vieram da fila B (primeiros 9 em ordem estrutural)
            self.assertEqual(self.pre_tri_b1[t]['queue'], 'B_CLEAN_MEDIUM', t)
            self.assertEqual(self.by[t]['human_review']['review_scope'], SCOPE['B1'], t)
            self.assertEqual(self.by[t]['human_review']['calibration_queue'], 'B', t)
        b_order = sorted((t for t, x in self.pre_tri_b1.items() if x['queue'] == 'B_CLEAN_MEDIUM'), key=self.ctx.order.__getitem__)
        self.assertEqual((len(b_order), b_order[:9]), (27, [d['target_id'] for d in load('ROUND_B1_HUMAN_REVIEW_DECISIONS.json')['decisions']]))
        for t in ROUND_B2_AS_IS + ROUND_B2_ADJUSTED:                    # os 9 da rodada B2 sao os itens 10 a 18 da fila B em ordem estrutural
            self.assertEqual(self.pre_tri_b2[t]['queue'], 'B_CLEAN_MEDIUM', t)
            self.assertEqual(self.by[t]['human_review']['review_scope'], SCOPE['B2'], t)
            self.assertEqual(self.by[t]['human_review']['calibration_queue'], 'B', t)
        self.assertEqual(b_order[9:18], [d['target_id'] for d in load('ROUND_B2_HUMAN_REVIEW_DECISIONS.json')['decisions']])
        for t in ROUND_B3_AS_IS + ROUND_B3_ADJUSTED:                    # os 9 da rodada B3 sao os itens 19 a 27 da fila B em ordem estrutural
            self.assertEqual(self.pre_tri_b3[t]['queue'], 'B_CLEAN_MEDIUM', t)
            self.assertEqual(self.by[t]['human_review']['review_scope'], SCOPE['B3'], t)
            self.assertEqual(self.by[t]['human_review']['calibration_queue'], 'B', t)
        self.assertEqual(b_order[18:], [d['target_id'] for d in load('ROUND_B3_HUMAN_REVIEW_DECISIONS.json')['decisions']])
        for t in ROUND_A1_AS_IS + ROUND_A1_ADJUSTED:                    # os 15 da rodada A1 sao os itens 1 a 15 da fila A em ordem estrutural
            self.assertEqual(self.pre_tri_a1[t]['queue'], 'A_CLEAN_LOW', t)
            self.assertEqual(self.by[t]['human_review']['review_scope'], SCOPE['A1'], t)
            self.assertEqual(self.by[t]['human_review']['calibration_queue'], 'A', t)
        a_order = sorted((t for t, x in self.pre_tri_a1.items() if x['queue'] == 'A_CLEAN_LOW'), key=self.ctx.order.__getitem__)
        self.assertEqual((len(a_order), a_order[:15]), (42, [d['target_id'] for d in load('ROUND_A1_HUMAN_REVIEW_DECISIONS.json')['decisions']]))
        for t in ROUND_A2_AS_IS + ROUND_A2_ADJUSTED:                    # os 15 da rodada A2 sao os itens 16 a 30 da fila A em ordem estrutural
            self.assertEqual(self.pre_tri_a2[t]['queue'], 'A_CLEAN_LOW', t)
            self.assertEqual(self.by[t]['human_review']['review_scope'], SCOPE['A2'], t)
            self.assertEqual(self.by[t]['human_review']['calibration_queue'], 'A', t)
        self.assertEqual(a_order[15:30], [d['target_id'] for d in load('ROUND_A2_HUMAN_REVIEW_DECISIONS.json')['decisions']])
        for t in ROUND_A3_AS_IS + ROUND_A3_ADJUSTED:                    # os 12 da rodada A3 sao os itens 31 a 42 da fila A em ordem estrutural
            self.assertEqual(self.pre_tri_a3[t]['queue'], 'A_CLEAN_LOW', t)
            self.assertEqual(self.by[t]['human_review']['review_scope'], SCOPE['A3'], t)
            self.assertEqual(self.by[t]['human_review']['calibration_queue'], 'A', t)
        self.assertEqual(a_order[30:], [d['target_id'] for d in load('ROUND_A3_HUMAN_REVIEW_DECISIONS.json')['decisions']])
        pending = [r for r in self.corpus if r['review_status'] == 'PENDING_HUMAN_REVIEW']
        self.assertEqual(pending, [])                                    # nenhuma explicacao do Batch06 fica pendente de revisao humana
        self.assertEqual(self.tri['human_approved_t1_granted'], 93)
        self.assertEqual(self.sel['summary']['review_status_counts'], {'HUMAN_APPROVED_T1': 96})
        tot = self.tri['approval_totals']
        self.assertEqual((tot['global_before'], tot['global_after'], tot['batch06_new_pending']), (289, 382, 0))
        for name, counts in (('ROUND_D_HUMAN_REVIEW_DECISIONS.json', {'APPROVED': 2, 'APPROVED_AFTER_ADJUSTMENT': 9, 'REJECTED': 0}),
                             ('ROUND_C_HUMAN_REVIEW_DECISIONS.json', {'APPROVED': 8, 'APPROVED_AFTER_ADJUSTMENT': 5, 'REJECTED': 0}),
                             ('ROUND_B1_HUMAN_REVIEW_DECISIONS.json', {'APPROVED': 1, 'APPROVED_AFTER_ADJUSTMENT': 8, 'REJECTED': 0}),
                             ('ROUND_B2_HUMAN_REVIEW_DECISIONS.json', {'APPROVED': 1, 'APPROVED_AFTER_ADJUSTMENT': 8, 'REJECTED': 0}),
                             ('ROUND_B3_HUMAN_REVIEW_DECISIONS.json', {'APPROVED': 0, 'APPROVED_AFTER_ADJUSTMENT': 9, 'REJECTED': 0}),
                             ('ROUND_A1_HUMAN_REVIEW_DECISIONS.json', {'APPROVED': 2, 'APPROVED_AFTER_ADJUSTMENT': 13, 'REJECTED': 0}),
                             ('ROUND_A2_HUMAN_REVIEW_DECISIONS.json', {'APPROVED': 4, 'APPROVED_AFTER_ADJUSTMENT': 11, 'REJECTED': 0}),
                             ('ROUND_A3_HUMAN_REVIEW_DECISIONS.json', {'APPROVED': 1, 'APPROVED_AFTER_ADJUSTMENT': 11, 'REJECTED': 0})):
            dec = load(name)
            self.assertEqual(dec['review_status'], 'ROUND_REVIEW_COMPLETED')
            self.assertEqual(dec['decision_counts'], counts)
            for ev, h in dec['original_evidence_sha256'].items():
                self.assertEqual(sha(BD / ev), h, ev)
        self.assertEqual([ra['review_scope'] for ra in self.spec['round_approvals']],
                         [SCOPE['D'], SCOPE['C'], SCOPE['B1'], SCOPE['B2'], SCOPE['B3'], SCOPE['A1'], SCOPE['A2'], SCOPE['A3']])

    def test_round_d_and_c_versions_and_history(self):
        retired = {r['target_id']: r for r in self.all if r['status'] == 'RETIRED'}
        adjusted = (ROUND_D_ADJUSTED + ROUND_C_ADJUSTED + ROUND_B1_ADJUSTED + ROUND_B2_ADJUSTED + ROUND_B3_ADJUSTED + ROUND_A1_ADJUSTED
                    + ROUND_A2_ADJUSTED + ROUND_A3_ADJUSTED)
        self.assertEqual(sorted(retired), sorted(adjusted))
        for t in adjusted:
            old, new = retired[t], self.by[t]
            self.assertEqual((old['editorial_version'], new['editorial_version']), (1, 2), t)
            self.assertEqual(old['review_status'], 'CHANGES_REQUESTED', t)
            self.assertEqual(old['superseded_by'], new['explanation_id'], t)
            self.assertEqual(old['content'], self.pre_by[t]['content'], t)            # earlier version preserved, never overwritten
            self.assertEqual(old['source'], self.pre_by[t]['source'], t)
            self.assertEqual(new['human_review']['decision'], 'APPROVED_AFTER_ADJUSTMENT', t)
        for t in (ROUND_D_AS_IS + ROUND_C_AS_IS + ROUND_B1_AS_IS + ROUND_B2_AS_IS + ROUND_A1_AS_IS + ROUND_A2_AS_IS
                  + ROUND_A3_AS_IS):                                     # sem reescrita: mesma versao e bytes
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
            self.assertNotEqual((self.rows.get(t) or self.pre_tri_b1[t])['queue'], 'D_FULL_HUMAN_REVIEW', t)   # aprovado na rodada B1: triagem anterior

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

    def test_round_b1_wording_and_glossary(self):
        b1 = ROUND_B1_AS_IS + ROUND_B1_ADJUSTED
        known = V.load_json(V.KNOWN)['resolutions']
        man = V.load_json(BD / 'index/ENTENDA_BUILD_MANIFEST.json')
        self.assertFalse([w for w in man['warnings'] if w['target_id'] in b1 and w['code'] == 'TERM_NOT_USED'])   # glossario so com termos usados
        for t in b1:
            self.assertNotIn(self.by[t]['explanation_id'], known, t)   # nenhuma resolucao registrada: os alertas sumiram pela redacao
        terms = {t: [p['termo'] for p in self.by[t]['content']['palavras_dificeis']] for t in b1}
        self.assertEqual(terms['CF88:ART.48'], ['Sanção', 'Anistia', 'Subsídio'])
        self.assertEqual(terms['CF88:ART.49:INC.I'], ['Tratado', 'Encargo gravoso'])
        self.assertEqual(terms['CF88:ART.50:PAR.2'], ['Mesa', 'Pedido escrito de informação'])
        self.assertEqual(terms['CF88:ART.52'], ['Arguição', 'Dívida consolidada'])
        self.assertEqual(terms['CF88:ART.55'], ['Decoro parlamentar', 'Ampla defesa'])
        body = {t: json.dumps(self.by[t]['content'], ensure_ascii=False) for t in b1}
        self.assertNotIn('exercidas por resolução', body['CF88:ART.48'])
        self.assertNotIn('palavra final', body['CF88:ART.49:INC.I'])
        self.assertNotIn('o deputado ou senador apresenta o requerimento', body['CF88:ART.50:PAR.2'])
        self.assertIn('arguição em sessão secreta', body['CF88:ART.52'])
        self.assertIn('o Vice-Presidente da República e os Ministros de Estado', body['CF88:ART.52:INC.I'])
        for gone in ('automaticamente', 'As imunidades começam', 'deixa de tê-las'):
            self.assertNotIn(gone, body['CF88:ART.53'])
        self.assertIn('Emenda Constitucional nº 35, de 2001', self.by['CF88:ART.53']['content']['atencao'])
        self.assertNotIn('silenciar o Parlamento', body['CF88:ART.53:PAR.8'])
        self.assertIn('pelo menos um terço', self.by['CF88:ART.55']['content']['exemplo_pratico'])
        self.assertNotIn('mais de um terço', body['CF88:ART.55'])

    def test_round_b2_wording_and_glossary(self):
        b2 = ROUND_B2_AS_IS + ROUND_B2_ADJUSTED
        known = V.load_json(V.KNOWN)['resolutions']
        man = V.load_json(BD / 'index/ENTENDA_BUILD_MANIFEST.json')
        self.assertFalse([w for w in man['warnings'] if w['target_id'] in b2 and w['code'] in ('TERM_NOT_USED', 'ABSOLUTE_CLAIM')])
        for t in b2:
            self.assertNotIn(self.by[t]['explanation_id'], known, t)   # nenhuma resolucao registrada: os alertas sumiram pela redacao
        terms = {t: [p['termo'] for p in self.by[t]['content']['palavras_dificeis']] for t in b2}
        self.assertEqual(terms['CF88:ART.55:PAR.1'], ['Prerrogativa', 'Vantagem indevida', 'Decoro parlamentar'])
        self.assertEqual(terms['CF88:ART.65'], ['Casa revisora', 'Turno', 'Casa iniciadora'])
        self.assertEqual(terms['CF88:ART.66:PAR.1'], ['Veto parcial', 'Sanção tácita'])
        self.assertEqual(terms['CF88:ART.62:PAR.1'], ['Crédito extraordinário', 'Sequestro de bens', 'Limite material'])
        body = {t: json.dumps(self.by[t]['content'], ensure_ascii=False) for t in b2}
        r = self.by['CF88:ART.55:PAR.4']                                # maior sequencia literal do B11 abaixo do limite (era 12)
        src = [w.lower() for w in E.words(r['source']['source_text_snapshot'])]
        grams = {tuple(src[i:i + 6]) for i in range(len(src) - 5)}
        w = [x.lower() for x in E.words(r['content']['o_que_significa'])]
        self.assertFalse([i for i in range(len(w) - 5) if tuple(w[i:i + 6]) in grams])
        self.assertIn('que vise à perda do mandato ou que possa levar a ela', body['CF88:ART.55:PAR.4'])
        for gone in ('escapar', 'voltar a se candidatar', 'prevalece'):
            self.assertNotIn(gone, body['CF88:ART.55:PAR.4'])
        self.assertIn('o afastamento não pode ultrapassar cento e vinte dias', body['CF88:ART.56'])
        for gone in ('exceção ao art. 54', 'lista', 'fechada'):
            self.assertNotIn(gone, body['CF88:ART.56'])
        self.assertIn('carreira', self.by['CF88:ART.62:PAR.1']['content']['o_que_diz'])
        self.assertIn('poupança popular', self.by['CF88:ART.62:PAR.1']['content']['o_que_diz'])
        for gone in ('rejeitada sem exame do mérito', 'mera formalidade'):
            self.assertNotIn(gone, body['CF88:ART.62:PAR.5'])
        self.assertIn('O projeto de lei aprovado', self.by['CF88:ART.65']['content']['o_que_significa'])
        self.assertNotIn('jamais', body['CF88:ART.65'])
        self.assertIn('art. 67', self.by['CF88:ART.65']['content']['atencao'])
        self.assertNotIn('publicada', body['CF88:ART.66'])
        for gone in ('jurídico', 'político', 'porque'):
            self.assertNotIn(gone, body['CF88:ART.66:PAR.1'])

    def test_round_b3_wording_and_glossary(self):
        b3 = ROUND_B3_AS_IS + ROUND_B3_ADJUSTED
        known = V.load_json(V.KNOWN)['resolutions']
        man = V.load_json(BD / 'index/ENTENDA_BUILD_MANIFEST.json')
        self.assertFalse([w for w in man['warnings'] if w['target_id'] in b3 and w['code'] in ('TERM_NOT_USED', 'ABSOLUTE_CLAIM')])
        for t in b3:
            self.assertNotIn(self.by[t]['explanation_id'], known, t)   # nenhuma resolucao registrada: os alertas sumiram pela redacao
        chk = {r['target_id']: r for r in self.chk['rows']}
        self.assertEqual([f['code'] for f in chk['CF88:ART.74']['findings']], ['LAW_DEPENDENCY_OMITTED'])   # so a resolucao antiga do § 2º
        self.assertTrue(chk['CF88:ART.74']['findings'][0]['resolution'])
        self.assertIn('CF88:ART.74:PAR.2', ' '.join(load('ROUND_B3_HUMAN_REVIEW_DECISIONS.json')['pending_revalidation']))
        # revalidacao concluida na rodada A3 (B26 = VALID), registrada no artefato da A3; o historico da B3 fica intacto
        self.assertEqual(self.by['CF88:ART.74:PAR.2']['review_status'], 'HUMAN_APPROVED_T1')
        a3 = load('ROUND_A3_HUMAN_REVIEW_DECISIONS.json')
        b26 = [x for x in a3['resolutions_reviewed'] if x['target_id'] == 'CF88:ART.74']
        self.assertEqual([(x['code'], x['revalidation']) for x in b26], [('LAW_DEPENDENCY_OMITTED', 'B26_RESOLUTION_REVALIDATION: VALID')])
        self.assertIn('CF88:ART.74', ' '.join(a3['pending_revalidation_resolved']))
        self.assertEqual(a3['pending_revalidation'], [])
        a42 = self.by['CF88:ART.74:PAR.2']['content']
        self.assertIn('na forma da lei', a42['o_que_diz'])
        self.assertIn('“na forma da lei” significa que os requisitos e a forma de apresentação', a42['o_que_significa'])
        terms = {t: [p['termo'] for p in self.by[t]['content']['palavras_dificeis']] for t in b3}
        self.assertEqual(terms['CF88:ART.71:INC.VIII'], ['Sanção', 'Cominação', 'Título executivo', 'Erário'])
        self.assertEqual(terms['CF88:ART.71:PAR.1'], ['Sustação'])
        self.assertEqual(terms['CF88:ART.73:PAR.3'], ['Equiparação', 'Impedimento'])
        body = {t: json.dumps(self.by[t]['content'], ensure_ascii=False) for t in b3}
        for t, limit in (('CF88:ART.71:INC.III', 8), ('CF88:ART.73', 10), ('CF88:ART.74', 10)):   # maior sequencia literal abaixo de 10
            r = self.by[t]
            src = [w.lower() for w in E.words(r['source']['source_text_snapshot'])]
            grams = {tuple(src[i:i + limit]) for i in range(len(src) - limit + 1)}
            for k in ('o_que_diz', 'o_que_significa'):
                w = [x.lower() for x in E.words(r['content'][k])]
                self.assertFalse([i for i in range(len(w) - limit + 1) if tuple(w[i:i + limit]) in grams], (t, k))
        self.assertNotIn('mais difícil', body['CF88:ART.69'])
        self.assertNotIn('deve corrigi', body['CF88:ART.71:INC.III'])
        self.assertNotIn('lei orgânica', body['CF88:ART.71:INC.VIII'])
        for gone in ('nem o Congresso nem', 'passa a ser dele', 'prefere'):
            self.assertNotIn(gone, body['CF88:ART.71:PAR.1'])
        self.assertIn('No inciso X', self.by['CF88:ART.71:PAR.1']['content']['o_que_significa'])
        for gone in ('não executa a própria decisão', 'representação judicial'):
            self.assertNotIn(gone, body['CF88:ART.71:PAR.3'])
        self.assertIn('com aprovação do Senado Federal', self.by['CF88:ART.73']['content']['o_que_significa'])
        self.assertNotIn('repassados a Estados', body['CF88:ART.73'])
        self.assertNotIn('Em troca', body['CF88:ART.73:PAR.3'])
        for gone in ('ao Congresso e ao Tribunal', 'quatro anos', 'de forma contínua'):
            self.assertNotIn(gone, body['CF88:ART.74'])
        for gone in ('Quem trabalha', 'integralmente'):
            self.assertNotIn(gone, body['CF88:ART.74:PAR.1'])

    def test_round_a1_wording_glossary_and_old_resolutions(self):
        a1 = ROUND_A1_AS_IS + ROUND_A1_ADJUSTED
        known = V.load_json(V.KNOWN)['resolutions']
        man = V.load_json(BD / 'index/ENTENDA_BUILD_MANIFEST.json')
        self.assertFalse([w for w in man['warnings'] if w['target_id'] in a1 and w['code'] == 'TERM_NOT_USED'])
        absolute = [(w['target_id'], w['detail']) for w in man['warnings'] if w['target_id'] in a1 and w['code'] == 'ABSOLUTE_CLAIM']
        self.assertEqual(absolute, [('CF88:ART.43:PAR.2', 'sempre')])   # "sempre que possivel" do proprio § 4º (INFO no validador v3)
        for t in a1:
            self.assertNotIn(self.by[t]['explanation_id'], known, t)   # nenhuma resolucao registrada: os alertas sumiram pela redacao
        terms = {t: [p['termo'] for p in self.by[t]['content']['palavras_dificeis']] for t in a1}
        self.assertEqual(terms['CF88:ART.47'], ['Quórum', 'Maioria absoluta'])               # "Maioria simples" retirado do glossario
        self.assertEqual(terms['CF88:ART.49'], ['Competência exclusiva', 'Referendo', 'Plebiscito', 'Subsídio'])   # sem "Decreto legislativo"
        self.assertEqual(terms['CF88:ART.49:INC.V'], ['Poder regulamentar', 'Exorbitar', 'Sustar'])
        for t, limit in (('CF88:ART.43:PAR.2', 9), ('CF88:ART.49', 10)):    # maior sequencia literal final: 8 (A4) e 9 (A9)
            r = self.by[t]
            src = [w.lower() for w in E.words(r['source']['source_text_snapshot'])]
            grams = {tuple(src[i:i + limit]) for i in range(len(src) - limit + 1)}
            for k in ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao'):
                w = [x.lower() for x in E.words(r['content'][k])]
                self.assertFalse([i for i in range(len(w) - limit + 1) if tuple(w[i:i + limit]) in grams], (t, k))
        # resolucoes antigas: A3 continua disparada e valida; A8 sem uso na v2, mantida no historico
        chk = {r['target_id']: r for r in self.chk['rows']}
        self.assertEqual([f['code'] for f in chk['CF88:ART.42:PAR.3']['findings']], ['EXCEPTION_NOT_IN_TEXT'])
        self.assertTrue(chk['CF88:ART.42:PAR.3']['findings'][0]['resolution'])
        self.assertEqual(chk['CF88:ART.47']['findings'], [])
        res = load('EDITORIAL_REVIEW_INPUT.json')['resolutions']
        self.assertIn('EXCEPTION_NOT_IN_TEXT', res['CF88:ART.42:PAR.3'])
        self.assertIn('TRANSITION_IN_CORE', res['CF88:ART.47'])
        rev = {x['target_id']: x['status'] for x in load('ROUND_A1_HUMAN_REVIEW_DECISIONS.json')['resolutions_reviewed']}
        self.assertEqual(rev, {'CF88:ART.42:PAR.3': 'MANTIDA_APLICAVEL', 'CF88:ART.47': 'MANTIDA_SEM_USO_NA_V2'})
        body = {t: json.dumps(self.by[t]['content'], ensure_ascii=False) for t in a1}
        # regressoes juridicas corrigidas
        self.assertNotIn('servidor estadual', body['CF88:ART.42'])
        for t in ('CF88:ART.42', 'CF88:ART.42:PAR.1'):
            self.assertIn('art. 22, XXI', body[t], t)
        self.assertNotIn('medicina', body['CF88:ART.42:PAR.3'])
        self.assertNotIn('regras anteriores', body['CF88:ART.42:PAR.3'])
        for kept in ('art. 37, XI', 'Emenda Constitucional nº 138, de 2025', 'outro de qualquer natureza'):
            self.assertIn(kept, body['CF88:ART.42:PAR.3'])
        for kept in ('preços', 'represáveis', 'pessoas físicas ou jurídicas', 'redução das emissões de carbono'):
            self.assertIn(kept, body['CF88:ART.43:PAR.2'])
        self.assertNotIn('Atualmente não existem', body['CF88:ART.45'])
        self.assertIn('Distrito Federal', self.by['CF88:ART.45']['content']['o_que_significa'])
        self.assertNotIn('mesma chapa', body['CF88:ART.46'])
        self.assertIn('licença superior a cento e vinte dias', self.by['CF88:ART.46']['content']['atencao'])
        self.assertNotIn('dos presentes', body['CF88:ART.47'])
        self.assertIn('estado de sítio', self.by['CF88:ART.49']['content']['o_que_diz'])
        self.assertIn('ressalva de lei complementar prevista no inciso II', self.by['CF88:ART.49']['content']['o_que_diz'])
        for t in ('CF88:ART.49', 'CF88:ART.49:INC.V', 'CF88:ART.51'):
            self.assertNotIn('decreto legislativo', body[t].lower(), t)
        self.assertIn('art. 71, I', self.by['CF88:ART.49:INC.IX']['content']['o_que_significa'])
        self.assertNotIn('não vincula', body['CF88:ART.49:INC.IX'])
        for gone in ('em regra, a resolução', 'sem participação do Senado nem sanção'):
            self.assertNotIn(gone, body['CF88:ART.51'])
        self.assertNotIn('em comissão', body['CF88:ART.52:INC.III'])
        self.assertIn('sessão secreta', self.by['CF88:ART.52:INC.III']['content']['atencao'])
        for gone in ('contra essas entidades', 'leva à perda', 'durante o mandato'):
            self.assertNotIn(gone, body['CF88:ART.54'])
        self.assertIn('em que essas entidades sejam interessadas', self.by['CF88:ART.54']['content']['o_que_diz'])
        self.assertIn('art. 55, § 2º', self.by['CF88:ART.54']['content']['o_que_significa'])

    def test_round_a2_wording_glossary_and_old_resolutions(self):
        a2 = ROUND_A2_AS_IS + ROUND_A2_ADJUSTED
        known = V.load_json(V.KNOWN)['resolutions']
        man = V.load_json(BD / 'index/ENTENDA_BUILD_MANIFEST.json')
        self.assertFalse([w for w in man['warnings'] if w['target_id'] in a2 and w['code'] in ('TERM_NOT_USED', 'TERM_LOW_UTILITY')])
        absolute = sorted({(w['target_id'], w['detail']) for w in man['warnings'] if w['target_id'] in a2 and w['code'] == 'ABSOLUTE_CLAIM'})
        self.assertEqual(absolute, [('CF88:ART.57:PAR.7', 'automaticamente')])   # "automaticamente" do proprio § 8º
        for t in a2:
            self.assertNotIn(self.by[t]['explanation_id'], known, t)   # nenhuma resolucao registrada: os alertas sumiram pela redacao
        terms = {t: [p['termo'] for p in self.by[t]['content']['palavras_dificeis']] for t in a2}
        self.assertEqual(terms['CF88:ART.58:PAR.2'], ['Audiência pública'])                # "Poder conclusivo" retirado
        self.assertEqual(terms['CF88:ART.62:PAR.2'], ['Exercício financeiro', 'Anterioridade tributária', 'Majoração'])
        self.assertEqual(terms['CF88:ART.59'], ['Processo legislativo', 'Lei delegada', 'Resolução', 'Decreto legislativo', 'Quórum'])
        self.assertEqual(terms['CF88:ART.64'], ['Casa iniciadora', 'Casa revisora', 'Urgência constitucional'])
        gloss = {t: {p['termo']: p['explicacao'] for p in self.by[t]['content']['palavras_dificeis']} for t in a2}
        for t in ('CF88:ART.59', 'CF88:ART.62:PAR.3', 'CF88:ART.62:PAR.11'):
            self.assertNotIn('competência exclusiva', gloss[t]['Decreto legislativo'], t)
        promulg = {p['termo']: p['explicacao'] for p in self.by['CF88:ART.66']['content']['palavras_dificeis']}['Promulgação']
        self.assertEqual(gloss['CF88:ART.66:PAR.7']['Promulgação'], promulg)                # mesma definicao do art. 66 (v2)
        for t, limit in (('CF88:ART.54:INC.II', 11), ('CF88:ART.58:PAR.2', 11), ('CF88:ART.64', 10)):   # maior sequencia literal: 10, 10 e 9
            r = self.by[t]
            src = [w.lower() for w in E.words(r['source']['source_text_snapshot'])]
            grams = {tuple(src[i:i + limit]) for i in range(len(src) - limit + 1)}
            for k in E.REQUIRED_TEXT:
                w = [x.lower() for x in E.words(r['content'][k])]
                self.assertFalse([i for i in range(len(w) - limit + 1) if tuple(w[i:i + limit]) in grams], (t, k))
        # resolucoes antigas: quatro continuam disparadas e validas; a do art. 58, § 2º, ficou sem uso na v2 e segue no historico
        chk = {r['target_id']: r for r in self.chk['rows']}
        for t, code in (('CF88:ART.57:PAR.2', 'EXAMPLE_NUMBER'), ('CF88:ART.57:PAR.7', 'ABSOLUTE_CLAIM'), ('CF88:ART.58', 'LAW_DEPENDENCY_OMITTED'),
                        ('CF88:ART.64:PAR.2', 'EXCEPTION_NOT_IN_TEXT')):
            self.assertEqual({f['code'] for f in chk[t]['findings']}, {code}, t)
            self.assertTrue(all(f['resolution'] for f in chk[t]['findings']), t)
        self.assertEqual(chk['CF88:ART.58:PAR.2']['findings'], [])
        res = load('EDITORIAL_REVIEW_INPUT.json')['resolutions']
        self.assertIn('LAW_DEPENDENCY_OMITTED', res['CF88:ART.58:PAR.2'])
        rev = {x['target_id']: x['status'] for x in load('ROUND_A2_HUMAN_REVIEW_DECISIONS.json')['resolutions_reviewed']}
        self.assertEqual(rev, {'CF88:ART.57:PAR.2': 'MANTIDA_APLICAVEL', 'CF88:ART.57:PAR.7': 'MANTIDA_APLICAVEL', 'CF88:ART.58': 'MANTIDA_APLICAVEL',
                               'CF88:ART.58:PAR.2': 'MANTIDA_SEM_USO_NA_V2', 'CF88:ART.64:PAR.2': 'MANTIDA_APLICAVEL'})
        body = {t: json.dumps(self.by[t]['content'], ensure_ascii=False) for t in a2}
        # regressoes juridicas corrigidas
        self.assertNotIn('poder público', body['CF88:ART.54:INC.II'])
        self.assertNotIn('entidades públicas', body['CF88:ART.54:INC.II'])
        self.assertIn('pessoa jurídica de direito público', self.by['CF88:ART.54:INC.II']['content']['o_que_diz'])
        self.assertNotIn('porque têm prazo', body['CF88:ART.57:PAR.7'])
        for kept in ('entidades da sociedade civil', 'omissões', 'nacionais, regionais e setoriais', 'emitindo parecer'):
            self.assertIn(kept, self.by['CF88:ART.58:PAR.2']['content']['o_que_diz'])
        for gone in ('Para aprovar um tratado', 'o Senado edita resolução', 'competência própria'):
            self.assertNotIn(gone, body['CF88:ART.59'])
        for gone in ('instrumentos de regulação', 'ano civil'):
            self.assertNotIn(gone, body['CF88:ART.62:PAR.2'])
        self.assertIn('anterioridade tributária', self.by['CF88:ART.62:PAR.2']['content']['atencao'])
        for gone in ('como se não tivesse existido', 'não depende de novo ato do Presidente', 'competência exclusiva'):
            self.assertNotIn(gone, body['CF88:ART.62:PAR.3'])
        self.assertIn('cento e vinte dias corridos', self.by['CF88:ART.62:PAR.3']['content']['o_que_significa'])
        for gone in ('Antes de 2001', 'por anos', 'ano legislativo'):
            self.assertNotIn(gone, body['CF88:ART.62:PAR.10'])
        self.assertIn('legislatura', self.by['CF88:ART.62:PAR.10']['content']['o_que_significa'])
        for gone in ('fora do Congresso', 'Casa do autor'):
            self.assertNotIn(gone, body['CF88:ART.64'])
        self.assertIn('Casa iniciadora', self.by['CF88:ART.64']['content']['o_que_significa'])
        self.assertNotIn('não se sujeitam a essa urgência', body['CF88:ART.64:PAR.2'])
        self.assertIn('não se aplicam aos projetos de código', self.by['CF88:ART.64:PAR.2']['content']['o_que_significa'])
        self.assertNotIn('cada um com quarenta e oito horas', body['CF88:ART.66:PAR.7'])
        self.assertIn('não fixa expressamente outro prazo', self.by['CF88:ART.66:PAR.7']['content']['o_que_significa'])

    def test_round_a3_wording_glossary_and_final_state(self):
        a3 = ROUND_A3_AS_IS + ROUND_A3_ADJUSTED
        known = V.load_json(V.KNOWN)['resolutions']
        man = V.load_json(BD / 'index/ENTENDA_BUILD_MANIFEST.json')
        self.assertFalse([w for w in man['warnings'] if w['target_id'] in a3 and w['code'] in ('TERM_NOT_USED', 'TERM_LOW_UTILITY', 'ABSOLUTE_CLAIM')])
        parent = [(w['target_id'], w['detail']) for w in man['warnings'] if w['target_id'] in a3 and w['code'] == 'PARENT_REPETITION']
        self.assertEqual(parent, [('CF88:ART.73:PAR.2', 'CF88:ART.73: 0.311')])   # aviso informativo aceito pela revisao humana
        accepted = load('ROUND_A3_HUMAN_REVIEW_DECISIONS.json')['accepted_info_warnings']
        self.assertEqual([(x['target_id'], x['code']) for x in accepted], [('CF88:ART.73:PAR.2', 'PARENT_REPETITION')])
        for t in a3:
            self.assertNotIn(self.by[t]['explanation_id'], known, t)   # nenhuma resolucao registrada: os alertas sumiram pela redacao
        chk = {r['target_id']: r for r in self.chk['rows']}
        self.assertFalse([t for t in a3 if chk[t]['findings']])
        self.assertEqual(sum(r['unresolved'] for r in self.chk['rows']), 0)
        act = [r for r in self.all if r['status'] == 'ACTIVE']
        self.assertEqual(EC.duplication(act, self.ctx.limits['max_section_similarity']), [])
        self.assertLess(E.similarity(self.by['CF88:ART.71:INC.I']['content']['exemplo_pratico'],
                                     self.by['CF88:ART.49:INC.IX']['content']['exemplo_pratico']), 0.35)   # A37 x A11: 0,25
        terms = {t: [p['termo'] for p in self.by[t]['content']['palavras_dificeis']] for t in a3}
        self.assertEqual(terms['CF88:ART.67'], ['Sessão legislativa'])                      # "Irrepetibilidade" retirado
        self.assertEqual(terms['CF88:ART.68'], ['Delegação legislativa', 'Resolução'])
        self.assertEqual(terms['CF88:ART.68:PAR.1'], ['Competência exclusiva', 'Direitos individuais'])   # sem "Decreto legislativo"
        self.assertEqual(terms['CF88:ART.71:INC.II'], ['Erário', 'Imputação de débito'])    # "Título executivo" retirado
        gloss = {t: {p['termo']: p['explicacao'] for p in self.by[t]['content']['palavras_dificeis']} for t in a3}
        g = lambda t, k: {p['termo']: p['explicacao'] for p in self.by[t]['content']['palavras_dificeis']}[k]  # noqa: E731
        self.assertEqual(gloss['CF88:ART.71:INC.I']['Parecer prévio'], g('CF88:ART.49:INC.IX', 'Parecer prévio'))
        self.assertEqual(gloss['CF88:ART.71:INC.II']['Erário'], g('CF88:ART.71:INC.VIII', 'Erário'))
        self.assertNotIn('sem participação', gloss['CF88:ART.68:PAR.1']['Competência exclusiva'])
        self.assertNotIn('tempo', gloss['CF88:ART.68:PAR.2']['Termos da delegação'])
        for t, limit in (('CF88:ART.68:PAR.1', 10), ('CF88:ART.70:PAR.UNICO', 11), ('CF88:ART.71:INC.II', 10),
                         ('CF88:ART.71:INC.IX', 11), ('CF88:ART.72', 11)):   # maior sequencia literal: 9, 10, 9, 10 e 10
            r = self.by[t]
            src = [w.lower() for w in E.words(r['source']['source_text_snapshot'])]
            grams = {tuple(src[i:i + limit]) for i in range(len(src) - limit + 1)}
            for k in E.REQUIRED_TEXT:
                w = [x.lower() for x in E.words(r['content'][k])]
                self.assertFalse([i for i in range(len(w) - limit + 1) if tuple(w[i:i + limit]) in grams], (t, k))
        body = {t: json.dumps(self.by[t]['content'], ensure_ascii=False) for t in a3}
        # regressoes juridicas corrigidas
        for gone in ('ano legislativo', 'assinada', 'subscrito'):
            self.assertNotIn(gone, body['CF88:ART.67'])
        self.assertIn('havida por prejudicada', self.by['CF88:ART.67']['content']['atencao'])
        for gone in ('pouco usado', 'por tempo', 'temporária'):
            self.assertNotIn(gone, body['CF88:ART.68'])
        self.assertIn('delegação legislativa', self.by['CF88:ART.68']['content']['o_que_significa'])
        for gone in ('exercidas por decreto legislativo', 'porque exige maioria absoluta', 'não devem ficar à disposição'):
            self.assertNotIn(gone, body['CF88:ART.68:PAR.1'])
        self.assertIn('se a resolução determinar', self.by['CF88:ART.68:PAR.2']['content']['o_que_diz'])
        self.assertIn('obrigações de natureza pecuniária', self.by['CF88:ART.70:PAR.UNICO']['content']['o_que_diz'])
        for gone in ('peso político', 'aprovação com ressalvas'):
            self.assertNotIn(gone, body['CF88:ART.71:INC.I'])
        self.assertIn('sessenta dias, contados desse recebimento', self.by['CF88:ART.71:INC.I']['content']['exemplo_pratico'])
        self.assertIn('art. 49, IX', self.by['CF88:ART.71:INC.I']['content']['o_que_significa'])
        self.assertNotIn('regulares ou irregulares', body['CF88:ART.71:INC.II'])
        self.assertNotIn('trinta dias', body['CF88:ART.71:INC.IX'])
        self.assertIn('pertence à camada externa', self.by['CF88:ART.71:INC.IX']['content']['atencao'])
        self.assertNotIn('e não para contratos', body['CF88:ART.71:INC.IX'])
        self.assertNotIn('disfarçados', body['CF88:ART.72'])
        self.assertIn('A decisão final de sustar é do Congresso', self.by['CF88:ART.72']['content']['o_que_significa'])
        for gone in ('órgão próprio', 'ordem de vacância', 'livre escolha'):
            self.assertNotIn(gone, body['CF88:ART.73:PAR.2'])
        self.assertIn('requisitos constitucionais do § 1º', self.by['CF88:ART.73:PAR.2']['content']['o_que_significa'])
        self.assertNotIn('morador', body['CF88:ART.74:PAR.2'])
        self.assertIn('Um cidadão', self.by['CF88:ART.74:PAR.2']['content']['exemplo_pratico'])

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
        r = self.by['CF88:ART.49']                                      # v2 aprovada na rodada A1
        old = with_text(self.pre_by['CF88:ART.49'], 'o_que_diz', self.edit('CF88:ART.49', 'o_que_diz'))   # redacao do checkpoint (v1)
        fs = [f for f in V3.validate(old, self.ctx, self.catalog) if f['code'] == 'RESSALVA_OMITTED_IN_SUMMARY']
        self.assertTrue(fs)
        self.assertIn('ART.49:INC.II', fs[0]['detail'])
        self.assertFalse([f for f in V3.validate(r, self.ctx, self.catalog) if f['code'] == 'RESSALVA_OMITTED_IN_SUMMARY'])

    def test_list_completeness_regression_art68_par1(self):
        r = self.by['CF88:ART.68:PAR.1']                                # v2 aprovada na rodada A3
        old = with_text(self.pre_by['CF88:ART.68:PAR.1'], 'o_que_diz', self.edit('CF88:ART.68:PAR.1', 'o_que_diz'))   # redacao do checkpoint (v1)
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
        self.assertEqual(sum(c.values()), 0)                             # saem da triagem: 11 da rodada D, 13 da C, 27 da B e 42 da A (A1-A3)
        self.assertEqual((c['A_CLEAN_LOW'], c['B_CLEAN_MEDIUM'], c['C_QUICK_REVIEW'], c['D_FULL_HUMAN_REVIEW']), (0, 0, 0, 0))
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
        self.assertEqual(compact.count('nenhum item nesta fila'), 2)     # filas A e B vazias depois da rodada A3
        compact_pre = (BD / 'BATCH06_COMPACT_CLEAN_REVIEW_PRE_ROUND_A3.md').read_text(encoding='utf-8')   # formato do pacote com itens
        for field in ('Risco:', 'complexidade:', 'Ponto jurídico:', 'Interpretação principal:', 'ATENÇÃO:', 'Dependência externa:', 'Warnings:',
                      'Motivo da fila:'):
            self.assertIn(field, compact_pre)
        self.assertIn('nenhum item nesta fila', quick)                 # queue C fully decided in round C
        for field in ('**Detector:**', '**Motivo:**', '**Proposta de correção segura:**'):
            self.assertIn(field, (BD / 'BATCH06_QUICK_REVIEW_PRE_ROUND_C.md').read_text(encoding='utf-8'))

    def test_migration_of_previous_d(self):
        m = self.tri['migration']
        old_d = {t for t, v in load('PRE_RECALIBRATION_MANIFEST.json')['queues_by_target'].items() if v['queue'] == 'D_FULL_HUMAN_REVIEW'}
        self.assertEqual(len(old_d), 89)
        self.assertEqual(old_d - set(APPROVED), set())                    # os 89 D antigos foram todos decididos: D, C, B e A1-A3 (A3: 10)
        self.assertEqual((m['previous_D'], m['previous_D_now'], m['previous_D_migrated']), (0, {}, 0))   # migration = so pendentes atuais
        h = self.tri['triage_history']                                   # historico: snapshot versionado, nunca a triagem atual vazia
        snap = load('BATCH06_TRIAGE_PRE_ROUND_D.json')
        self.assertEqual(h['source'], 'BATCH06_TRIAGE_PRE_ROUND_D.json')
        self.assertEqual((h['pending_items'], h['counts'], h['legal_risk_counts'], h['complexity_counts'], h['jurisprudence_counts']),
                         (93, snap['counts'], snap['legal_risk_counts'], snap['complexity_counts'], snap['jurisprudence_counts']))
        hd = h['checkpoint_d']
        moved = {q: sum(1 for t in old_d if self.pre_tri[t]['queue'] == q) for q in BP.QUEUES}
        self.assertEqual(hd['items'], len(old_d))
        self.assertEqual(hd['left_d'], 78)
        self.assertEqual(hd['recalibrated_queue'], {q: n for q, n in moved.items() if n})
        self.assertEqual(hd['recalibrated_queue'], {'A_CLEAN_LOW': 38, 'B_CLEAN_MEDIUM': 27, 'C_QUICK_REVIEW': 13, 'D_FULL_HUMAN_REVIEW': 11})
        self.assertEqual(hd['final_review_status'], {'HUMAN_APPROVED_T1': 89})
        self.assertEqual(sum(hd['final_decision'].values()), 89)
        self.assertEqual(sum(hd['decided_by_round'].values()), 89)
        self.assertEqual(h['checkpoint']['counts'], {'A_CLEAN_LOW': 1, 'C_QUICK_REVIEW': 3, 'D_FULL_HUMAN_REVIEW': 89})

    def test_volume_reduction_measured(self):
        m = self.tri['metrics']
        self.assertEqual(m['presented_chars'], sum(m['presented_by_file'].values()))
        self.assertLess(m['presented_chars'], m['checkpoint_presented_chars'])
        for name, n in m['presented_by_file'].items():
            self.assertEqual(len((BD / name).read_text(encoding='utf-8')), n, name)
        self.assertEqual(m['total_draft_chars'], 0)                     # sem pendentes, os pacotes trazem so cabecalhos
        last = load('BATCH06_TRIAGE_PRE_ROUND_A3.json')['metrics']       # ultimo estado com itens a revisar (12 da fila A)
        self.assertLess(last['presented_chars'], last['old_model_full_package_chars'])
        self.assertLess(last['presented_chars'], last['checkpoint_presented_chars'])

    def test_micro_adjustments_not_applied(self):
        m = load('MICRO_ADJUSTMENTS_LOG.json')
        self.assertFalse(m['microauto_apply'])
        self.assertEqual(m['applied'], 0)

    def test_editorial_open_findings_are_routed(self):
        open_ = {r['target_id'] for r in self.chk['rows'] if r['unresolved']}
        for t in open_:
            self.assertIn(self.rows[t]['queue'], ('C_QUICK_REVIEW', 'D_FULL_HUMAN_REVIEW'), t)

    # ------------------------------------------------------------ fechamento final do Batch06 (apresentação do estado encerrado)

    def test_closure_scale_report_final_state(self):
        rep = (BD / 'BATCH06_SCALE_REPORT.md').read_text(encoding='utf-8')
        for bad in ('WIP: nenhum ENTENDA', 'WIP', 'nenhum item aprovado', 'A, B e C não foram decididos', 'Rodada D (revisão',
                    'Correções editoriais desta rodada', 'Pacote D: GERADO', 'Migração dos 0 D', 'Risco no checkpoint: .', '| Papéis das novas |  |',
                    'Jurisprudência:  ('):
            self.assertNotIn(bad, rep, bad)
        self.assertIsNone(re.search(r'\(-\d', rep))                      # nenhuma reducao percentual negativa
        self.assertIsNone(re.search(r'\|  +\|', rep))                    # nenhuma celula vazia (valor nao calculado)
        for good in ('**FECHADO: revisão jurídica humana concluída', '93/93 aprovadas após revisão humana', '289 antes → **382** depois',
                     '+93 do lote', 'os 3 pilotos reutilizados não são contados de novo', 'Novos pendentes do lote: **0**',
                     'Todas as filas de revisão humana foram concluídas', 'Revisão jurídica humana consolidada (BATCH06)', '8 rodadas componentes',
                     '19 aprovados sem alteração jurídica · 74 ajustados e aprovados · 0 rejeitados',
                     'Versões anteriores preservadas como RETIRED / CHANGES_REQUESTED: 74', 'Nenhum item D permanece pendente',
                     'Correções editoriais da recalibração (ROUND_0B)', 'Artefato D: gerado, sem itens pendentes', 'Histórico da triagem',
                     '**Migração dos 89 D antigos**', 'Destino final dos 89 D antigos: HUMAN_APPROVED_T1 89',
                     '| Papéis das novas | BLOCK 25, DEVICE 25, ITEM 10, OVERVIEW 33 |'):
            self.assertIn(good, rep, good)
        for scope in SCOPE.values():
            self.assertIn(f'`{scope}`', rep)
        for q in BP.QUEUES:
            self.assertEqual(self.tri['counts'][q], 0)
            self.assertIn(f'| {q} | 0 |', rep)
        man = load('BATCH06_MANIFEST.json')
        self.assertEqual(man['status'], 'CLOSED: revisao humana concluida; 93 HUMAN_APPROVED_T1 novos; 0 pendentes')
        self.assertEqual(self.tri['d_full_package'], 'GERADO_SEM_ITENS_PENDENTES')
        tot = self.tri['approval_totals']
        self.assertEqual((tot['global_before'], tot['global_after'], tot['batch06_new_approved'], tot['batch06_new_pending']), (289, 382, 93, 0))

    def test_closure_empty_queue_shells(self):
        shells = {n: (BD / n).read_text(encoding='utf-8') for n in ('BATCH06_COMPACT_CLEAN_REVIEW.md', 'BATCH06_QUICK_REVIEW.md',
                                                                    'BATCH06_FULL_HUMAN_REVIEW.md', 'BATCH06_HARD_FAIL_REPORT.md')}
        self.assertIn('filas A e B encerradas: nenhuma revisão pendente nas filas A e B', shells['BATCH06_COMPACT_CLEAN_REVIEW.md'])
        self.assertIn('fila C encerrada: nenhum item pendente', shells['BATCH06_QUICK_REVIEW.md'])
        self.assertIn('fila D encerrada: nenhum item pendente', shells['BATCH06_FULL_HUMAN_REVIEW.md'])
        self.assertIn('fila E encerrada: nenhum item pendente com HARD_FAIL', shells['BATCH06_HARD_FAIL_REPORT.md'])
        for name, text in shells.items():
            for bad in ('nenhum item aprovado', 'nenhum aprovado', '## Índice'):
                self.assertNotIn(bad, text, name)

    def test_closure_volume_metrics_without_pending(self):
        m = self.tri['metrics']
        self.assertEqual((m['pending_items'], m['total_draft_chars'], m['old_model_full_package_chars']), (0, 0, 0))
        self.assertIsNone(m['reduction_abs'])
        self.assertIsNone(m['reduction_pct'])
        rep = (BD / 'BATCH06_SCALE_REPORT.md').read_text(encoding='utf-8')
        self.assertEqual(rep.count('N/A — não existem mais itens pendentes'), 2)
        for snap in ('BATCH06_TRIAGE_PRE_ROUND_D.json', 'BATCH06_TRIAGE_PRE_ROUND_A3.json'):   # comparacao historica com fonte declarada
            hm = load(snap)['metrics']
            self.assertIn(f"`{snap}` ({len(load(snap)['rows'])} pendentes)", rep)
            self.assertIn(B._n(hm['presented_chars']), rep)
            self.assertGreater(hm['reduction_pct'], 0)

    def test_closure_did_not_change_t1_decisions_or_resolutions(self):
        base = '8b3ec1e0eb733847b65487e3473023b94cbaf7c3'                 # checkpoint de partida do fechamento (rodada A3 aplicada)
        p6 = 'ENTENDA_ENGINE/derived/production_batch_06/'
        names = ['CF88_BATCH_06.entenda.jsonl', 'BATCH_06_DRAFTS.json'] + [r['decisions'] for r in self.spec['round_approvals']]
        for n in names:
            old = subprocess.run(['git', 'show', f'{base}:{p6}{n}'], cwd=ROOT, capture_output=True, check=True).stdout
            self.assertEqual(old.replace(b'\r\n', b'\n'), (BD / n).read_bytes().replace(b'\r\n', b'\n'), n)
        old_inp = json.loads(subprocess.run(['git', 'show', f'{base}:{p6}EDITORIAL_REVIEW_INPUT.json'], cwd=ROOT, capture_output=True,
                                            check=True).stdout.decode('utf-8'))
        self.assertEqual(old_inp['resolutions'], load('EDITORIAL_REVIEW_INPUT.json')['resolutions'])
        a3 = load('ROUND_A3_HUMAN_REVIEW_DECISIONS.json')
        self.assertEqual([x['revalidation'] for x in a3['resolutions_reviewed']], ['B26_RESOLUTION_REVALIDATION: VALID'])
        self.assertEqual(a3['pending_revalidation'], [])
        p2 = self.by['CF88:ART.74:PAR.2']
        self.assertEqual((p2['review_status'], p2['editorial_version']), ('HUMAN_APPROVED_T1', 2))
        self.assertIn('na forma da lei', p2['content']['o_que_diz'])
        self.assertIn('disciplina legal aplicável', p2['content']['o_que_significa'])

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
