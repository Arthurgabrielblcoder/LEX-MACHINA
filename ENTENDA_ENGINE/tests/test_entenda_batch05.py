"""Tests for ENTENDA CF PRODUCTION BATCH 05 (arts. 37-41): T1 drafts pending human review (READY_FOR_EDITORIAL_REVIEW)."""
import contextlib
import hashlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import editorial_checks as EC  # noqa: E402
import entenda_engine as E  # noqa: E402
import production_batch as PB  # noqa: E402
import structure_parser as SP  # noqa: E402

BD = HERE / 'derived/production_batch_05'
LK, PL = BD / 'index/ENTENDA_LOOKUP.IDX', BD / 'index/ENTENDA_PAYLOAD.DAT'
RUNTIME = ROOT / 'DEVICE_INTEGRATION/runtime/CF88_RUNTIME.txt'
CANDIDATE = ROOT / 'DEVICE_INTEGRATION/staging_entenda_batch05_candidate'
# the batch corpus is evidence (RETIRED v1 of adjusted items) and is re-stamped idempotently; round decisions feed round_approvals
INPUTS = ('BATCH_SPEC.json', 'BATCH_05_DRAFTS.json', 'EDITORIAL_REVIEW_INPUT.json', 'ROUND_1_HUMAN_REVIEW_DECISIONS.json',
          'ROUND_2_HUMAN_REVIEW_DECISIONS.json', 'ROUND_3A_HUMAN_REVIEW_DECISIONS.json',
          'ROUND_3B_HUMAN_REVIEW_DECISIONS.json',
          'ROUND_D_HUMAN_REVIEW_DECISIONS.json', 'ROUND_FINAL_HUMAN_REVIEW_DECISIONS.json', 'CF88_BATCH_05.entenda.jsonl')
ROUND1_ADJUSTED = ('CF88:ART.37:INC.XI', 'CF88:ART.37:INC.XVI', 'CF88:ART.37:PAR.4', 'CF88:ART.37:PAR.9', 'CF88:ART.37:PAR.14',
                   'CF88:ART.37:PAR.15')
ROUND2_APPROVED = ('CF88:ART.41:PAR.1', 'CF88:ART.41:PAR.3')
ROUND2_ADJUSTED = ('CF88:ART.38:INC.V', 'CF88:ART.39', 'CF88:ART.39:PAR.4', 'CF88:ART.39:PAR.9', 'CF88:ART.41', 'CF88:ART.41:PAR.2',
                   'CF88:ART.41:PAR.4')
ROUND3A_APPROVED = ('CF88:ART.40:PAR.3', 'CF88:ART.40:PAR.1:INC.III', 'CF88:ART.40:PAR.4-A')
ROUND3A_ADJUSTED = ('CF88:ART.40', 'CF88:ART.40:CAPUT', 'CF88:ART.40:PAR.2', 'CF88:ART.40:PAR.4', 'CF88:ART.40:PAR.5', 'CF88:ART.40:PAR.1:INC.I',
                    'CF88:ART.40:PAR.1:INC.II', 'CF88:ART.40:PAR.6')
ROUND3B_APPROVED = ('CF88:ART.40:PAR.8',)
ROUND3B_ADJUSTED = ('CF88:ART.40:PAR.7', 'CF88:ART.40:PAR.9', 'CF88:ART.40:PAR.11', 'CF88:ART.40:PAR.12', 'CF88:ART.40:PAR.13',
                    'CF88:ART.40:PAR.14', 'CF88:ART.40:PAR.18', 'CF88:ART.40:PAR.19', 'CF88:ART.40:PAR.20', 'CF88:ART.40:PAR.22')
ROUND_D_ADJUSTED = ('CF88:ART.38:INC.III', 'CF88:ART.37:PAR.7')                 # triage queue D (FULL_HUMAN_REVIEW), 2026-10-04
ROUND_FINAL_AS_IS = ('CF88:ART.37:PAR.1', 'CF88:ART.37:PAR.16', 'CF88:ART.37:PAR.3', 'CF88:ART.37:PAR.8', 'CF88:ART.37:INC.I', 'CF88:ART.37:INC.III',
                     'CF88:ART.37:INC.V', 'CF88:ART.37:INC.VI', 'CF88:ART.37:INC.XIX', 'CF88:ART.37:INC.XXI', 'CF88:ART.37:PAR.2', 'CF88:ART.39:PAR.1',
                     'CF88:ART.39:PAR.3', 'CF88:ART.39:PAR.5', 'CF88:ART.37:INC.II', 'CF88:ART.37:INC.X', 'CF88:ART.37:INC.XII', 'CF88:ART.39:PAR.2')
ROUND_FINAL_MICRO = ('CF88:ART.38',)
ROUND_FINAL_ADJUSTED = ('CF88:ART.37:INC.VIII', 'CF88:ART.37:INC.IX', 'CF88:ART.37:INC.XV', 'CF88:ART.38:INC.I', 'CF88:ART.38:INC.IV',
                        'CF88:ART.37:CAPUT', 'CF88:ART.37:INC.XVIII', 'CF88:ART.37:PAR.13', 'CF88:ART.38:INC.II', 'CF88:ART.39:PAR.7')
ROUND_FINAL_CHANGED = ROUND_FINAL_ADJUSTED + ROUND_FINAL_MICRO + ('CF88:ART.37:PAR.7',)
# T1 micro-adjustment policy (round 3A): only function words may change, numbers never
FUNCTION_WORDS = {'a', 'o', 'as', 'os', 'de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'nas', 'nos', 'ao', 'aos', 'à', 'às', 'para', 'por',
                  'pelo', 'pela', 'pelos', 'pelas', 'e', 'um', 'uma'}
_NEW_PARA = re.compile(r'^[A-ZÁÉÍÓÚÂÊÔÃÕÇ“"§]')


def unwrap(raw):
    lines = [x.strip() for x in raw.strip().split('\n')]
    out = lines[0]
    for prev, cur in zip(lines, lines[1:]):
        out += ('\n' if prev.endswith(('.', ':', ';')) and _NEW_PARA.match(cur) else ' ') + cur
    return out


def unwrap_lists(raw):                                                   # round 3B rule: same as unwrap + "* " list items on own line
    lines = [x.strip() for x in raw.strip().split('\n') if x.strip()]
    out = lines[0]
    for prev, cur in zip(lines, lines[1:]):
        out += ('\n' if cur.startswith('* ') or (prev.endswith(('.', ':', ';')) and _NEW_PARA.match(cur)) else ' ') + cur
    return out
GENERATED = ('CF88_BATCH_05.entenda.jsonl', 'SELECTION_REPORT.json', 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json', 'REVIEW_BATCH_05.md',
             'EDITORIAL_CHECKS.json', 'REVIEW_BATCH_05_RISK_TRIAGE.md', 'index/ENTENDA_LOOKUP.IDX', 'index/ENTENDA_PAYLOAD.DAT',
             'index/ENTENDA_BUILD_MANIFEST.json')
PILOTS = ('CF88:ART.37', 'CF88:ART.37:PAR.6', 'CF88:ART.37:PAR.10')


def _body(r):
    c = r['content']
    return ' '.join([c[k] for k in E.REQUIRED_TEXT] + [c['atencao'] or ''] + [t['explicacao'] for t in c['palavras_dificeis']])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@unittest.skipUnless((BD / 'SELECTION_REPORT.json').is_file(), 'batch 05 not built')
class Batch05Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.spec = json.loads((BD / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
        cls.ctx.ncfg = dict(cls.ctx.ncfg, reference_export=cls.spec['reference_export'])
        cls.all = E.load_corpus(BD / cls.spec['batch_corpus'])
        cls.new = [r for r in cls.all if r['status'] == 'ACTIVE']
        cls.by = {r['target_id']: r for r in cls.new}
        cls.rep = json.loads((BD / 'SELECTION_REPORT.json').read_text(encoding='utf-8'))
        cls.rows = {r['target_id']: r for r in cls.rep['selection']}
        cls.checks = json.loads((BD / 'EDITORIAL_CHECKS.json').read_text(encoding='utf-8'))
        cls.plan = json.loads((BD / 'BATCH05_TARGET_PLAN.json').read_text(encoding='utf-8'))
        cls.main = [r for r in E.load_corpus(HERE / 'corpus/CF88.entenda.jsonl') if r['status'] == 'ACTIVE']

    # ---------------- scope, counts, status ----------------
    def test_scope_counts_and_pending(self):
        self.assertEqual(self.spec['scope'], ['CF88:ART.37', 'CF88:ART.38', 'CF88:ART.39', 'CF88:ART.40', 'CF88:ART.41'])
        scope = [t for a in self.spec['scope'] for t in self.ctx.subtree(a)]
        self.assertEqual(sorted(self.rows), sorted(scope))
        s = self.rep['summary']
        self.assertEqual((s['targets_evaluated'], s['targets_legally_current'], s['targets_revoked'], s['historical_excluded']),
                         (133, 118, 1, 14))
        self.assertEqual((len(self.new), s['reused_from_pilot'], s['batch_total_explanations']), (69, 3, 72))
        self.assertLessEqual(len(self.new), self.spec['hard_cap'])
        self.assertEqual(s['soft_target_status'], 'OUTSIDE_JUSTIFIED')
        self.assertTrue(self.spec['soft_target_justification'].startswith('69 explicacoes novas'))
        self.assertEqual(s['review_status_counts'], {'HUMAN_APPROVED_T1': 72})  # pilots 3 + 69 new (HIGH 38, queue D 2, final 29)
        self.assertEqual(s['retired_versions'], 47)

    def test_no_invented_approval(self):
        approved = {t for t, r in self.by.items() if r['review_status'] == 'HUMAN_APPROVED_T1'}
        self.assertEqual(approved, {'CF88:ART.37:PAR.5', *ROUND1_ADJUSTED, *ROUND2_APPROVED, *ROUND2_ADJUSTED, *ROUND3A_APPROVED,
                                    *ROUND3A_ADJUSTED, *ROUND3B_APPROVED, *ROUND3B_ADJUSTED, *ROUND_D_ADJUSTED,
                                    *ROUND_FINAL_AS_IS, *ROUND_FINAL_MICRO, *ROUND_FINAL_ADJUSTED})
        p5 = self.by['CF88:ART.37:PAR.5']
        self.assertEqual((p5['editorial_version'], p5['human_review']['review_scope'], p5['human_review']['reviewer_decision']),
                         (1, 'CF88_ART37_HIGH_ROUND_1', 'ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW'))
        for t, r in self.by.items():
            if t not in approved:
                self.assertEqual(r['review_status'], 'PENDING_HUMAN_REVIEW', t)
                self.assertNotIn('human_review', r)
        self.assertEqual(self.checks['human_approved_t1'], 69)
        self.assertEqual(self.checks['ready_for_editorial_review'], 69)
        self.assertEqual(self.checks['unresolved_findings'], 0)
        drafts = json.loads((BD / 'BATCH_05_DRAFTS.json').read_text(encoding='utf-8'))
        self.assertEqual(drafts['review_status'], 'PENDING_HUMAN_REVIEW')
        dec = json.loads((BD / 'ROUND_1_HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual(sorted(d['target_id'] for d in dec['decisions']), sorted({'CF88:ART.37:PAR.5', *ROUND1_ADJUSTED}))
        self.assertEqual(dec['decision_counts'], {'APPROVED': 1, 'APPROVED_AFTER_ADJUSTMENT': 6})
        self.assertTrue(dec['final_check']['approved_without_new_version'])
        for t in ('CF88:ART.37:PAR.14', 'CF88:ART.37:PAR.15'):                                     # reviewer-supplied facts: provenance
            prov = self.by[t]['human_review']['content_provenance']
            self.assertEqual([p['source_type'] for p in prov], ['HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE'])
            self.assertFalse(prov[0]['in_cf88_runtime'])
            self.assertNotIn('EC 103', self.by[t]['source']['source_text_snapshot'])

    def test_round1_adjustments_versioned_and_preserved(self):
        adj = json.loads((BD / 'ROUND_1_EDITORIAL_ADJUSTMENTS.json').read_text(encoding='utf-8'))
        self.assertEqual(adj['round_result'], {'reviewed': 7, 'approved_unchanged': 1, 'adjust': 6, 'rejected': 0})
        self.assertEqual(adj['review_status'], 'APPROVED_AFTER_FINAL_CHECK')
        self.assertEqual(sum(len(a['t1_contract_deviations']) for a in adj['adjustments']), 8)
        self.assertEqual([x['termo'] for x in self.by['CF88:ART.37:INC.XI']['content']['palavras_dificeis']],
                         ['Teto remuneratório', 'Subteto', 'Vantagem pessoal', 'Proventos', 'Pensionista'])
        self.assertEqual(sorted(a['target_id'] for a in adj['adjustments']), sorted(ROUND1_ADJUSTED))
        pre = {e['target_id']: e for e in json.loads((BD / 'BATCH_05_DRAFTS_PRE_ROUND1.json').read_text(encoding='utf-8'))['explanations']}
        self.assertEqual(sha(BD / 'BATCH_05_DRAFTS_PRE_ROUND1.json'), adj['original_evidence_sha256']['BATCH_05_DRAFTS_PRE_ROUND1.json'])
        retired = {r['target_id']: r for r in self.all if r['status'] == 'RETIRED' and r['editorial_version'] == 1}
        self.assertEqual(sorted(retired), sorted(ROUND1_ADJUSTED + ROUND2_ADJUSTED + ROUND3A_ADJUSTED + ROUND3B_ADJUSTED + ROUND_D_ADJUSTED
                                                  + ROUND_FINAL_ADJUSTED + ROUND_FINAL_MICRO))
        for a in adj['adjustments']:
            t = a['target_id']
            self.assertEqual((self.by[t]['editorial_version'], self.by[t]['review_status']), (2, 'HUMAN_APPROVED_T1'))   # no v3
            self.assertEqual(self.by[t]['human_review']['decision'], 'APPROVED_AFTER_ADJUSTMENT')
            self.assertEqual(retired[t]['content'], pre[t]['content'])                              # v1 kept as evidence
            self.assertEqual(retired[t]['superseded_by'], f'ENTENDA/{t}/BASE/2')
            self.assertEqual(self.by[t]['content'], a['after']['content'])
            self.assertEqual(self.by[t]['granularity'].get('covered_targets', []), pre[t].get('covered_targets', []))
            applied = json.loads(json.dumps(a['reviewer_text_verbatim']['content']))             # reviewer text + listed deviations only
            for d in a['t1_contract_deviations']:
                if d['section'] == 'palavras_dificeis':
                    applied['palavras_dificeis'] = [x for x in applied['palavras_dificeis'] if x['termo'] != d['reviewer_text'].split(':')[0]]
                else:
                    applied[d['section']] = applied[d['section']].replace(d['reviewer_text'], d['applied_text'])
            self.assertEqual(applied, self.by[t]['content'], t)
        for t in pre:
            if t not in ROUND1_ADJUSTED + ROUND2_ADJUSTED + ROUND3A_ADJUSTED + ROUND3B_ADJUSTED + ROUND_D_ADJUSTED + ROUND_FINAL_CHANGED:
                self.assertEqual(self.by[t]['content'], pre[t]['content'], t)

    def test_round2_decisions_adjustments_and_provenance(self):
        dec = json.loads((BD / 'ROUND_2_HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual((dec['review_status'], dec['review_scope'], dec['decision_counts']),
                         ('ROUND_REVIEW_COMPLETED', 'CF88_ART38_39_41_HIGH_ROUND_2', {'APPROVED': 2, 'APPROVED_AFTER_ADJUSTMENT': 7}))
        self.assertEqual(sorted(d['target_id'] for d in dec['decisions']), sorted(ROUND2_APPROVED + ROUND2_ADJUSTED))
        adj = json.loads((BD / 'ROUND_2_EDITORIAL_ADJUSTMENTS.json').read_text(encoding='utf-8'))
        self.assertEqual(adj['round_result'], {'reviewed': 9, 'approved_unchanged': 2, 'adjust': 7, 'rejected': 0})
        self.assertEqual(adj['review_status'], 'APPROVED_AFTER_FINAL_CHECK')
        self.assertEqual(sorted(a['target_id'] for a in adj['adjustments']), sorted(ROUND2_ADJUSTED))
        self.assertEqual(sum(len(a['t1_contract_deviations']) for a in adj['adjustments']), 1)
        pre = {e['target_id']: e for e in json.loads((BD / 'BATCH_05_DRAFTS_PRE_ROUND2.json').read_text(encoding='utf-8'))['explanations']}
        self.assertEqual(sha(BD / 'BATCH_05_DRAFTS_PRE_ROUND2.json'), adj['original_evidence_sha256']['BATCH_05_DRAFTS_PRE_ROUND2.json'])
        retired = {r['explanation_id']: r for r in self.all if r['status'] == 'RETIRED'}
        for t in ROUND2_APPROVED:                                                                  # approved as is: v1, content untouched
            r = self.by[t]
            self.assertEqual((r['editorial_version'], r['review_status'], r['human_review']['review_scope']),
                             (1, 'HUMAN_APPROVED_T1', 'CF88_ART38_39_41_HIGH_ROUND_2'))
            self.assertEqual(r['content'], pre[t]['content'])
        for a in adj['adjustments']:                                     # approved v2 (ART.39: v3), earlier versions retired as evidence
            t = a['target_id']
            ver = 3 if t == 'CF88:ART.39' else 2
            self.assertEqual((self.by[t]['editorial_version'], self.by[t]['review_status']), (ver, 'HUMAN_APPROVED_T1'))
            self.assertEqual(self.by[t]['human_review']['decision'], 'APPROVED_AFTER_ADJUSTMENT')
            v1 = retired[f'ENTENDA/{t}/BASE/1']
            self.assertEqual(v1['content'], pre[t]['content'])
            self.assertEqual(v1['superseded_by'], f'ENTENDA/{t}/BASE/{ver}')                  # engine: superseded_by = current version
            self.assertEqual(self.by[t]['granularity'].get('covered_targets', []), pre[t].get('covered_targets', []))
            applied = json.loads(json.dumps(a['reviewer_text_verbatim']['content']))
            for d in a['t1_contract_deviations']:
                applied[d['section']] = applied[d['section']].replace(d['reviewer_text'], d['applied_text'])
            if ver == 3:                                                 # v2 = reviewer text + deviation, kept RETIRED/CHANGES_REQUESTED
                v2 = retired[f'ENTENDA/{t}/BASE/2']
                self.assertEqual((v2['review_status'], v2['superseded_by']), ('CHANGES_REQUESTED', f'ENTENDA/{t}/BASE/3'))
                self.assertEqual(applied, v2['content'])
                self.assertEqual(len(a['final_check_edits']), 1)
            for d in a['final_check_edits']:
                applied[d['section']] = applied[d['section']].replace(d['before'], d['after'])
            self.assertEqual(applied, self.by[t]['content'], t)
            notes = a['reviewer_text_verbatim']['external_layer_notes']
            self.assertEqual(self.by[t]['external_layer_notes'], pre[t]['external_layer_notes'] if isinstance(notes, str) else notes, t)
        for t in pre:                                                                              # round 1 and everything else intact
            if t not in ROUND2_ADJUSTED + ROUND3A_ADJUSTED + ROUND3B_ADJUSTED + ROUND_D_ADJUSTED + ROUND_FINAL_CHANGED:
                self.assertEqual(self.by[t]['content'], pre[t]['content'], t)
        prov = {a['target_id']: a['content_provenance'] for a in adj['adjustments'] if a['content_provenance']}
        self.assertEqual(sorted(prov), ['CF88:ART.39', 'CF88:ART.39:PAR.9'])
        for t, ps in prov.items():
            self.assertEqual([x['source_type'] for x in ps], ['HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE'])
            self.assertFalse(ps[0]['in_cf88_runtime'])
        self.assertNotIn('art. 13', self.by['CF88:ART.39:PAR.9']['source']['source_text_snapshot'])

    def test_round3b_pre_authorized_t1_policy(self):
        dec = json.loads((BD / 'ROUND_3B_HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual((dec['review_status'], dec['review_scope'], dec['decision_counts']),
                         ('ROUND_REVIEW_COMPLETED', 'CF88_ART40_HIGH_ROUND_3B', {'APPROVED': 1, 'APPROVED_AFTER_ADJUSTMENT': 10}))
        self.assertEqual(sorted(d['target_id'] for d in dec['decisions']), sorted(ROUND3B_APPROVED + ROUND3B_ADJUSTED))
        adj = json.loads((BD / 'ROUND_3B_EDITORIAL_ADJUSTMENTS.json').read_text(encoding='utf-8'))
        self.assertEqual(adj['round_result'], {'reviewed': 11, 'approved_unchanged': 1, 'adjust': 10, 'rejected': 0})
        self.assertEqual(adj['review_status'], 'APPROVED_UNDER_PRE_AUTHORIZED_T1_POLICY')
        self.assertEqual(len(adj['t1_microadjust_policy']['authorized']), 5)
        pre = {e['target_id']: e for e in json.loads((BD / 'BATCH_05_DRAFTS_PRE_ROUND3B.json').read_text(encoding='utf-8'))['explanations']}
        self.assertEqual(sha(BD / 'BATCH_05_DRAFTS_PRE_ROUND3B.json'), adj['original_evidence_sha256']['BATCH_05_DRAFTS_PRE_ROUND3B.json'])
        retired = {r['explanation_id']: r for r in self.all if r['status'] == 'RETIRED'}
        for t in ROUND3B_APPROVED:                                                                 # approved as is: v1, content untouched
            r = self.by[t]
            self.assertEqual((r['editorial_version'], r['review_status'], r['human_review']['review_scope']),
                             (1, 'HUMAN_APPROVED_T1', 'CF88_ART40_HIGH_ROUND_3B'))
            self.assertEqual(r['content'], pre[t]['content'])
        self.assertEqual(sorted(a['target_id'] for a in adj['adjustments']), sorted(ROUND3B_ADJUSTED))
        ndev = 0
        for a in adj['adjustments']:
            t = a['target_id']
            r = self.by[t]
            self.assertEqual((r['editorial_version'], r['review_status'], r['human_review']['decision']), (2, 'HUMAN_APPROVED_T1', 'APPROVED_AFTER_ADJUSTMENT'))
            v1 = retired[f'ENTENDA/{t}/BASE/1']
            self.assertEqual((v1['content'], v1['review_status'], v1['superseded_by']), (pre[t]['content'], 'CHANGES_REQUESTED', f'ENTENDA/{t}/BASE/2'))
            self.assertEqual(r['granularity'].get('covered_targets', []), pre[t].get('covered_targets', []))
            v = a['reviewer_text_verbatim']
            for k in ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao'):                  # verbatim (hard-wrapped) -> paragraphs
                self.assertEqual(unwrap_lists(v['raw_wrapped'][k]), v['content'][k], (t, k))
            applied = json.loads(json.dumps(v['content']))
            for d in a['t1_contract_deviations']:
                ndev += 1
                self.assertIn(d['policy_item'], (1, 2, 3, 4, 5))
                self.assertEqual(d['policy_text'], adj['t1_microadjust_policy']['authorized'][d['policy_item'] - 1])
                if d['section'] == 'palavras_dificeis':
                    applied['palavras_dificeis'] = [x for x in applied['palavras_dificeis'] if x['termo'] != d['reviewer_text'].split(':')[0]]
                    continue
                self.assertEqual(re.findall(r'\d+', d['reviewer_text']), re.findall(r'\d+', d['applied_text']))   # no number changes
                if d['policy_item'] == 2:                                                          # only function words differ
                    wa, wb = E.words(d['reviewer_text'].lower()), E.words(d['applied_text'].lower())
                    self.assertTrue(set(wa) ^ set(wb) <= FUNCTION_WORDS, (t, set(wa) ^ set(wb)))
                applied[d['section']] = applied[d['section']].replace(d['reviewer_text'], d['applied_text'])
            self.assertEqual(applied, r['content'], t)                                             # reviewer text + registered deviations only
            notes = v['external_layer_notes']
            want = pre[t]['external_layer_notes'] if isinstance(notes, str) else \
                (pre[t]['external_layer_notes'] + [notes[1]] if notes[0] == 'ACRESCENTAR' else notes)
            self.assertEqual(r['external_layer_notes'], want, t)
        self.assertEqual(ndev, 1)
        for t in pre:                                                                              # rounds 1-3A, pilots, MEDIUM/LOW untouched
            if t not in ROUND3B_ADJUSTED + ROUND_D_ADJUSTED + ROUND_FINAL_CHANGED:
                self.assertEqual(self.by[t]['content'], pre[t]['content'], t)
        prov = {t: self.by[t]['human_review'].get('content_provenance') for t in ROUND3B_ADJUSTED if self.by[t]['human_review'].get('content_provenance')}
        self.assertEqual(sorted(prov), sorted(['CF88:ART.40:PAR.11', 'CF88:ART.40:PAR.14', 'CF88:ART.40:PAR.18', 'CF88:ART.40:PAR.22']))
        for ps in prov.values():
            self.assertEqual({x['source_type'] for x in ps}, {'HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE'})
        p11 = self.by['CF88:ART.40:PAR.11']
        self.assertNotIn('total delas se sujeita ao teto', _body(p11))
        self.assertTrue(any(n.startswith('Tema 359') for n in p11['external_layer_notes']))
        p22 = self.by['CF88:ART.40:PAR.22']
        self.assertFalse(any('está na camada de leis correlatas' in n for n in p22['external_layer_notes']))   # LC not presented as edited
        self.assertTrue(any('Lei nº 9.717/1998' in n for n in p22['external_layer_notes']))
        self.assertEqual(sum(1 for line in p22['content']['o_que_significa'].split('\n') if line.startswith('* ')), 9)
        self.assertEqual((p22['granularity']['role'], p22['granularity'].get('covered_targets', [])), ('BLOCK', []))  # incisos = subtree
        incs = [t for t in self.rows if t.startswith('CF88:ART.40:PAR.22:INC.')]
        self.assertEqual(len(incs), 10)
        for t in incs:
            self.assertEqual((self.rows[t]['classification'], self.rows[t]['coverage']), ('NO_SEPARATE_EXPLANATION', 'BLOCK_SUBDIVISION'), t)
        self.assertEqual(self.by['CF88:ART.40:PAR.9']['granularity']['covered_targets'], ['CF88:ART.40:PAR.10'])
        self.assertEqual(self.by['CF88:ART.40:PAR.14']['granularity']['covered_targets'], ['CF88:ART.40:PAR.15', 'CF88:ART.40:PAR.16'])
        self.assertIn('da agressão sofrida', self.by['CF88:ART.40:PAR.7']['content']['o_que_diz'])

    def test_round3a_pre_authorized_t1_policy(self):
        dec = json.loads((BD / 'ROUND_3A_HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual((dec['review_status'], dec['review_scope'], dec['decision_counts']),
                         ('ROUND_REVIEW_COMPLETED', 'CF88_ART40_HIGH_ROUND_3A', {'APPROVED': 3, 'APPROVED_AFTER_ADJUSTMENT': 8}))
        self.assertEqual(sorted(d['target_id'] for d in dec['decisions']), sorted(ROUND3A_APPROVED + ROUND3A_ADJUSTED))
        adj = json.loads((BD / 'ROUND_3A_EDITORIAL_ADJUSTMENTS.json').read_text(encoding='utf-8'))
        self.assertEqual(adj['round_result'], {'reviewed': 11, 'approved_unchanged': 3, 'adjust': 8, 'rejected': 0})
        self.assertEqual(adj['review_status'], 'APPROVED_UNDER_PRE_AUTHORIZED_T1_POLICY')
        self.assertEqual(len(adj['t1_microadjust_policy']['authorized']), 5)
        pre = {e['target_id']: e for e in json.loads((BD / 'BATCH_05_DRAFTS_PRE_ROUND3A.json').read_text(encoding='utf-8'))['explanations']}
        self.assertEqual(sha(BD / 'BATCH_05_DRAFTS_PRE_ROUND3A.json'), adj['original_evidence_sha256']['BATCH_05_DRAFTS_PRE_ROUND3A.json'])
        retired = {r['explanation_id']: r for r in self.all if r['status'] == 'RETIRED'}
        for t in ROUND3A_APPROVED:                                                                 # approved as is: v1, content untouched
            r = self.by[t]
            self.assertEqual((r['editorial_version'], r['review_status'], r['human_review']['review_scope']),
                             (1, 'HUMAN_APPROVED_T1', 'CF88_ART40_HIGH_ROUND_3A'))
            self.assertEqual(r['content'], pre[t]['content'])
        self.assertEqual(sorted(a['target_id'] for a in adj['adjustments']), sorted(ROUND3A_ADJUSTED))
        ndev = 0
        for a in adj['adjustments']:
            t = a['target_id']
            r = self.by[t]
            self.assertEqual((r['editorial_version'], r['review_status'], r['human_review']['decision']), (2, 'HUMAN_APPROVED_T1', 'APPROVED_AFTER_ADJUSTMENT'))
            v1 = retired[f'ENTENDA/{t}/BASE/1']
            self.assertEqual((v1['content'], v1['review_status'], v1['superseded_by']), (pre[t]['content'], 'CHANGES_REQUESTED', f'ENTENDA/{t}/BASE/2'))
            self.assertEqual(r['granularity'].get('covered_targets', []), pre[t].get('covered_targets', []))
            v = a['reviewer_text_verbatim']
            for k in ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao'):                  # verbatim (hard-wrapped) -> paragraphs
                self.assertEqual(unwrap(v['raw_wrapped'][k]), v['content'][k], (t, k))
            applied = json.loads(json.dumps(v['content']))
            for d in a['t1_contract_deviations']:
                ndev += 1
                self.assertIn(d['policy_item'], (1, 2, 3, 4, 5))
                self.assertEqual(d['policy_text'], adj['t1_microadjust_policy']['authorized'][d['policy_item'] - 1])
                if d['section'] == 'palavras_dificeis':
                    applied['palavras_dificeis'] = [x for x in applied['palavras_dificeis'] if x['termo'] != d['reviewer_text'].split(':')[0]]
                    continue
                self.assertEqual(re.findall(r'\d+', d['reviewer_text']), re.findall(r'\d+', d['applied_text']))   # no number changes
                if d['policy_item'] == 2:                                                          # only function words differ
                    wa, wb = E.words(d['reviewer_text'].lower()), E.words(d['applied_text'].lower())
                    self.assertTrue(set(wa) ^ set(wb) <= FUNCTION_WORDS, (t, set(wa) ^ set(wb)))
                applied[d['section']] = applied[d['section']].replace(d['reviewer_text'], d['applied_text'])
            self.assertEqual(applied, r['content'], t)                                             # reviewer text + registered deviations only
            notes = v['external_layer_notes']
            want = pre[t]['external_layer_notes'] if isinstance(notes, str) else \
                (pre[t]['external_layer_notes'] + [notes[1]] if notes[0] == 'ACRESCENTAR' else notes)
            self.assertEqual(r['external_layer_notes'], want, t)
        self.assertEqual(ndev, 2)
        for t in pre:                                                                              # rounds 1-2, pilots, 03B untouched
            if t not in ROUND3A_ADJUSTED + ROUND3B_ADJUSTED + ROUND_D_ADJUSTED + ROUND_FINAL_CHANGED:
                self.assertEqual(self.by[t]['content'], pre[t]['content'], t)
        prov = {t: self.by[t]['human_review'].get('content_provenance') for t in ROUND3A_ADJUSTED if self.by[t]['human_review'].get('content_provenance')}
        self.assertEqual(sorted(prov), sorted(['CF88:ART.40', 'CF88:ART.40:PAR.5', 'CF88:ART.40:PAR.1:INC.II', 'CF88:ART.40:PAR.6']))
        for ps in prov.values():
            self.assertEqual({x['source_type'] for x in ps}, {'HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE'})
        self.assertTrue(any('Tema 965' in n for n in self.by['CF88:ART.40:PAR.5']['external_layer_notes']))
        self.assertNotIn('sala de aula', self.by['CF88:ART.40:PAR.5']['content']['palavras_dificeis'][0]['explicacao'])
        self.assertNotIn('Todas as somas', _body(self.by['CF88:ART.40:PAR.6']))
        self.assertNotIn('152/2015', self.by['CF88:ART.40:PAR.1:INC.II']['source']['source_text_snapshot'])

    def test_round_d_queue_resolution(self):
        dec = json.loads((BD / 'ROUND_D_HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual((dec['review_status'], dec['review_scope'], dec['decision_counts']),
                         ('ROUND_REVIEW_COMPLETED', 'CF88_BATCH05_TRIAGE_QUEUE_D', {'APPROVED_AFTER_ADJUSTMENT': 2}))
        pre = {e['target_id']: e for e in json.loads((BD / 'BATCH_05_DRAFTS_PRE_ROUND_D.json').read_text(encoding='utf-8'))['explanations']}
        self.assertEqual(sha(BD / 'BATCH_05_DRAFTS_PRE_ROUND_D.json'), dec['original_evidence_sha256']['BATCH_05_DRAFTS_PRE_ROUND_D.json'])
        retired = {r['explanation_id']: r for r in self.all if r['status'] == 'RETIRED'}
        for t in ROUND_D_ADJUSTED:
            r = self.by[t]
            ver = 3 if t == 'CF88:ART.37:PAR.7' else 2                                       # § 7º: post-approval edit (final round)
            self.assertEqual((r['editorial_version'], r['review_status'], r['human_review']['review_scope']),
                             (ver, 'HUMAN_APPROVED_T1', 'CF88_BATCH05_TRIAGE_QUEUE_D'))
            v1 = retired[f'ENTENDA/{t}/BASE/1']
            self.assertEqual((v1['content'], v1['review_status'], v1['superseded_by']), (pre[t]['content'], 'CHANGES_REQUESTED', f'ENTENDA/{t}/BASE/{ver}'))
            self.assertEqual([p['source_type'] for p in r['human_review']['content_provenance']], ['HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE'])
        a, b = pre['CF88:ART.38:INC.III']['content'], self.by['CF88:ART.38:INC.III']['content']          # only the ATENCAO sentence
        self.assertEqual({k for k in a if a[k] != b[k]}, {'atencao'})
        self.assertNotIn('soma das remunerações continua sujeita ao teto', b['atencao'])
        self.assertIn('pertence à camada de JURISPRUDÊNCIA', b['atencao'])
        self.assertTrue(b['atencao'].startswith(a['atencao'].split('. ')[0]))
        n38 = self.by['CF88:ART.38:INC.III']['external_layer_notes'][0]
        self.assertIn('Temas 377 e 384', n38)
        self.assertIn('Não são precedente específico', n38)
        p7 = self.by['CF88:ART.37:PAR.7']
        self.assertEqual(retired['ENTENDA/CF88:ART.37:PAR.7/BASE/2']['content'], pre['CF88:ART.37:PAR.7']['content'])   # v2: body unchanged
        self.assertTrue(p7['external_layer_notes'][0].startswith('No âmbito do Poder Executivo federal, a Lei nº 12.813/2013'))
        rel = p7['human_review']['content_provenance'][0]['relations_engine']
        self.assertEqual((rel['destino'], rel['status_resolvedor'], rel['decisao']), ('EXT_LEI12813_2013', 'PENDING', 'OCULTAR_ATE_VALIDAR_VIGENCIA'))
        for t, r in self.by.items():                                                          # A/B/C untouched
            if t not in ROUND_D_ADJUSTED and r['review_status'] == 'PENDING_HUMAN_REVIEW':
                self.assertEqual(r['content'], pre[t]['content'], t)

    def test_round_final_calibrated_review(self):
        dec = json.loads((BD / 'ROUND_FINAL_HUMAN_REVIEW_DECISIONS.json').read_text(encoding='utf-8'))
        self.assertEqual((dec['review_status'], dec['review_scope'], dec['decision_counts']),
                         ('ROUND_REVIEW_COMPLETED', 'CF88_BATCH05_TRIAGE_FINAL_29', {'APPROVED': 19, 'APPROVED_AFTER_ADJUSTMENT': 10}))
        self.assertEqual(len(dec['decisions']), 29)
        self.assertEqual(dec['calibration']['queue_c_precision'], '5/9')
        self.assertEqual(dec['calibration']['clean_low_found_problem'], ['CF88:ART.37:INC.VIII'])
        pre = {e['target_id']: e for e in json.loads((BD / 'BATCH_05_DRAFTS_PRE_ROUND_FINAL.json').read_text(encoding='utf-8'))['explanations']}
        self.assertEqual(sha(BD / 'BATCH_05_DRAFTS_PRE_ROUND_FINAL.json'), dec['original_evidence_sha256']['BATCH_05_DRAFTS_PRE_ROUND_FINAL.json'])
        retired = {r['explanation_id']: r for r in self.all if r['status'] == 'RETIRED'}
        for t in ROUND_FINAL_AS_IS:                                                          # approved as is: v1, content untouched
            r = self.by[t]
            self.assertEqual((r['editorial_version'], r['review_status'], r['content']), (1, 'HUMAN_APPROVED_T1', pre[t]['content']), t)
        for t in ROUND_FINAL_ADJUSTED + ROUND_FINAL_MICRO:                                     # v2 approved; v1 kept as evidence
            r = self.by[t]
            ver = 3 if t == 'CF88:ART.38:INC.II' else 2                                         # 38 II: final sanity fix (v2 -> v3)
            self.assertEqual((r['editorial_version'], r['review_status']), (ver, 'HUMAN_APPROVED_T1'), t)
            v1 = retired[f'ENTENDA/{t}/BASE/1']
            self.assertEqual((v1['content'], v1['review_status']), (pre[t]['content'], 'CHANGES_REQUESTED'), t)
        c = lambda t: self.by[t]['content']  # noqa: E731
        self.assertNotIn('compatível com as atribuições', ' '.join(c('CF88:ART.37:INC.VIII')[k] for k in ('o_que_diz', 'o_que_significa', 'atencao')))
        self.assertIn('Esses pontos dependem da legislação aplicável', c('CF88:ART.37:INC.VIII')['o_que_significa'])
        self.assertIn('exceto para promoção por merecimento', c('CF88:ART.38:INC.IV')['o_que_significa'])
        self.assertNotIn('Mandatos federais são os de', c('CF88:ART.38:INC.I')['o_que_significa'])
        self.assertIn('montante nominal', c('CF88:ART.37:INC.XV')['o_que_significa'])
        self.assertNotIn('10%', c('CF88:ART.37:INC.XV')['exemplo_pratico'])
        self.assertTrue(self.by['CF88:ART.37:INC.IX']['external_layer_notes'][0].startswith('Tema 612 do Supremo Tribunal Federal'))
        self.assertNotIn('só pode agir com base em autorização da lei', c('CF88:ART.37:CAPUT')['o_que_significa'])
        for t, frag in (('CF88:ART.37:INC.XVIII', 'todas as políticas públicas'), ('CF88:ART.37:PAR.13', 'Ela evita'),
                        ('CF88:ART.38:INC.II', 'A opção existe porque'), ('CF88:ART.39:PAR.7', 'A ideia é incentivar')):
            self.assertNotIn(frag, c(t)['o_que_significa'], t)
        p7 = self.by['CF88:ART.37:PAR.7']                                                    # post-approval edit: v2 -> v3
        self.assertEqual((p7['editorial_version'], p7['review_status']), (3, 'HUMAN_APPROVED_T1'))
        self.assertNotIn('quer evitar', p7['content']['o_que_significa'])
        v2 = retired['ENTENDA/CF88:ART.37:PAR.7/BASE/2']
        self.assertEqual((v2['review_status'], v2['superseded_by']), ('HUMAN_APPROVED_T1', 'ENTENDA/CF88:ART.37:PAR.7/BASE/3'))
        self.assertEqual(p7['external_layer_notes'], v2['external_layer_notes'])
        self.assertEqual(p7['human_review']['content_provenance'][0]['relations_engine']['status_resolvedor'], 'PENDING')   # not promoted
        for t, e in pre.items():                                                             # nothing else changed
            if t not in ROUND_FINAL_CHANGED:
                self.assertEqual(self.by[t]['content'], e['content'], t)

    def test_final_sanity_fix_art38_ii(self):
        fix = json.loads((BD / 'SANITY_FIX_POST_APPROVAL_EDIT.json').read_text(encoding='utf-8'))
        self.assertEqual(sha(BD / 'BATCH_05_DRAFTS_PRE_SANITY_FIX.json'), fix['original_evidence_sha256']['BATCH_05_DRAFTS_PRE_SANITY_FIX.json'])
        retired = {r['explanation_id']: r for r in self.all if r['status'] == 'RETIRED'}
        v2, v3 = retired['ENTENDA/CF88:ART.38:INC.II/BASE/2'], self.by['CF88:ART.38:INC.II']
        self.assertEqual((v3['editorial_version'], v3['review_status']), (3, 'HUMAN_APPROVED_T1'))
        self.assertEqual((v2['review_status'], v2['superseded_by']), ('HUMAN_APPROVED_T1', 'ENTENDA/CF88:ART.38:INC.II/BASE/3'))   # historical status kept
        self.assertNotIn('exige dedicação', v3['content']['o_que_significa'])
        self.assertTrue(v3['content']['o_que_significa'].startswith('O afastamento do cargo, emprego ou função é obrigatório.'))
        self.assertIn('pode escolher entre a remuneração do vínculo funcional e a remuneração do mandato de Prefeito', v3['content']['o_que_significa'])
        a, b = v2['content'], v3['content']
        self.assertEqual({k for k in a if a[k] != b[k]}, {'o_que_significa'})
        pre = {e['target_id']: e for e in json.loads((BD / 'BATCH_05_DRAFTS_PRE_SANITY_FIX.json').read_text(encoding='utf-8'))['explanations']}
        for t, e in pre.items():                                                                     # only this target changed
            if t != 'CF88:ART.38:INC.II':
                self.assertEqual(self.by[t]['content'], e['content'], t)

    def test_classification_per_article(self):
        own = lambda a: [t for t, r in self.rows.items() if (t == a or t.startswith(a + ':')) and r['classification'] in PB.SELECTED]  # noqa: E731
        self.assertEqual({a: len(own(a)) for a in self.spec['scope']},
                         {'CF88:ART.37': 31, 'CF88:ART.38': 6, 'CF88:ART.39': 8, 'CF88:ART.40': 22, 'CF88:ART.41': 5})
        self.assertEqual(self.rep['summary']['by_classification'],
                         {'BLOCK': 18, 'DEVICE': 32, 'EXCLUDED_HISTORICAL': 14, 'EXCLUDED_REVOKED': 1, 'ITEM': 17,
                          'NO_SEPARATE_EXPLANATION': 46, 'OVERVIEW': 5})
        self.assertEqual(self.rows['CF88:ART.40:PAR.21']['classification'], 'EXCLUDED_REVOKED')
        for t in ('CF88:ART.40:INC.I', 'CF88:ART.40:PAR.1:INC.III:AL.a', 'CF88:ART.40:PAR.7:INC.II'):
            self.assertEqual(self.rows[t]['classification'], 'EXCLUDED_HISTORICAL', t)
        self.assertEqual(self.rows['CF88:ART.40:PAR.1']['coverage'], 'ARTICLE_OVERVIEW')
        for c in ('CF88:ART.38:CAPUT', 'CF88:ART.39:CAPUT', 'CF88:ART.41:CAPUT'):
            self.assertEqual(self.rows[c]['coverage'], 'ARTICLE_OVERVIEW', c)

    def test_pilots_reused_unchanged(self):
        for t in PILOTS:
            self.assertEqual(self.rows[t]['explanation_source'], 'PILOT_T1_APPROVED')
            self.assertNotIn(t, self.by)
        prior = [r for p in self.spec['prior_corpora'] for r in E.load_corpus(ROOT / p) if r['status'] == 'ACTIVE']
        self.assertFalse({r['target_id'] for r in prior} & set(self.by))                         # no duplication of approved batches
        self.assertFalse({r['target_id'] for r in self.main} & set(self.by))

    # ---------------- text authority ----------------
    def test_runtime_is_the_authority(self):
        self.assertEqual(sha(RUNTIME), self.plan['text_base']['runtime_sha256'])
        self.assertTrue(self.plan['text_base']['runtime_equals_physical_staging'])
        parsed, _, _ = SP.parse_structure(RUNTIME.read_bytes().decode('utf-8-sig'), 'CF88', preview_len=10 ** 6)
        rtx = {t['target_id']: E.norm_text(t['preview']) for t in parsed if t['preview']}
        for r in self.new:
            s = r['source']
            self.assertEqual(E.sha256(s['source_text_snapshot']), s['source_text_sha256'], r['target_id'])
            self.assertEqual(s['source_text_snapshot'], self.ctx.snapshot(r['target_id'], r['granularity'].get('covered_targets', [])))
            for line in s['source_text_snapshot'].split('\n'):
                tid, txt = line.split('\t', 1)
                self.assertEqual(txt, rtx[tid], tid)                                               # snapshot == approved runtime text

    def test_engine_contract_and_no_jurisprudence(self):
        E.validate_corpus(self.main + self.new, self.ctx)
        for r in self.new:
            self.assertIsNone(E.EXTERNAL_CASE_RE.search(_body(r)), r['target_id'])
            self.assertEqual(r['usage_policy'], 'EDITORIAL_OUTPUT_ONLY')
            self.assertEqual(r['template_version'], 'ENTENDA-T1 (O QUE DIZ / O QUE SIGNIFICA / EXEMPLO PRATICO / ATENCAO / PALAVRAS DIFICEIS)')
            self.assertTrue(r['granularity']['editorial_reason'].strip())

    # ---------------- key targets ----------------
    def test_art37_caput_principles(self):
        c = self.by['CF88:ART.37:CAPUT']['content']
        for p in ('legalidade', 'impessoalidade', 'moralidade', 'publicidade', 'eficiência'):
            self.assertIn(p, (c['o_que_diz'] + c['o_que_significa']).lower(), p)
        sim = max(E.similarity(c[k], next(r for r in self.main if r['target_id'] == 'CF88:ART.37')['content'][k]) for k in E.REQUIRED_TEXT)
        self.assertLessEqual(sim, 0.35)

    def test_art37_concurso_validade_prioridade(self):
        c = self.by['CF88:ART.37:INC.II']['content']
        self.assertIn('concurso', c['o_que_diz'])
        self.assertIn('cargo em comissão', c['o_que_diz'])
        b = self.by['CF88:ART.37:INC.III']
        self.assertEqual(b['granularity']['covered_targets'], ['CF88:ART.37:INC.IV'])
        self.assertIn('dois anos', b['content']['o_que_diz'])
        self.assertIn('não diz que todo aprovado será nomeado', b['content']['atencao'])
        self.assertEqual(E.resolve_explanation('CF88:ART.37:INC.IV', self.new)['resolution_type'], 'COVERED_BY_BLOCK')

    def test_art37_acumulacao_current_wording(self):
        r = self.by['CF88:ART.37:INC.XVI']
        self.assertEqual(r['granularity']['covered_targets'], ['CF88:ART.37:INC.XVII'])
        self.assertIn('de qualquer natureza', self.ctx.text['CF88:ART.37:INC.XVI:AL.b'])
        self.assertIn('outro de qualquer natureza', r['content']['o_que_diz'])
        self.assertNotIn('técnico ou científico', r['content']['o_que_diz'] + r['content']['o_que_significa'])
        self.assertIn('EC 138/2025', r['content']['atencao'])
        self.assertNotIn('aproveitar', _body(r))
        self.assertEqual(self.rows['CF88:ART.37:INC.XVI:AL.a']['coverage'], 'BLOCK_SUBDIVISION')

    def test_art37_teto_and_par6(self):
        xi = self.by['CF88:ART.37:INC.XI']['content']
        self.assertIn('90,25%', xi['o_que_significa'])
        self.assertIn('Prefeito', xi['o_que_significa'])
        p9 = self.by['CF88:ART.37:PAR.9']
        self.assertEqual(p9['granularity']['covered_targets'], ['CF88:ART.37:PAR.11', 'CF88:ART.37:PAR.12'])
        self.assertIn('EC 135/2024', p9['content']['atencao'])
        self.assertNotIn('estatal dependente', _body(p9).lower())
        self.assertIn('não se deve concluir', xi['atencao'])
        self.assertEqual(self.rows['CF88:ART.37:PAR.6']['explanation_source'], 'PILOT_T1_APPROVED')       # responsabilidade civil
        p5 = self.by['CF88:ART.37:PAR.5']['content']
        self.assertIn('Não se deve ler o parágrafo como se tornasse imprescritível', p5['atencao'])  # controversy not resolved

    def test_art38_mandates(self):
        self.assertEqual(sorted(t for t in self.by if t.startswith('CF88:ART.38')),
                         ['CF88:ART.38', 'CF88:ART.38:INC.I', 'CF88:ART.38:INC.II', 'CF88:ART.38:INC.III', 'CF88:ART.38:INC.IV',
                          'CF88:ART.38:INC.V'])
        self.assertIn('pode escolher', self.by['CF88:ART.38:INC.II']['content']['o_que_diz'])
        self.assertIn('afastamento do cargo', self.by['CF88:ART.38:INC.I']['content']['o_que_diz'])
        self.assertIn('compatibilidade de horários', self.by['CF88:ART.38:INC.III']['content']['o_que_diz'])
        self.assertIn('promoção por merecimento', self.by['CF88:ART.38:INC.IV']['content']['o_que_diz'])
        self.assertIn('ente federativo de origem', self.by['CF88:ART.38:INC.V']['content']['o_que_diz'])

    def test_art39_caput_controversy_external(self):
        r = self.by['CF88:ART.39']
        self.assertIn('longa controvérsia constitucional', r['content']['atencao'])
        self.assertIn('EC 19/1998', r['content']['atencao'])
        self.assertNotIn('qual redação produz efeitos', _body(r))                                 # outdated framing removed (round 2)
        self.assertNotIn('CF88_RUNTIME', _body(r))                                                # no internal identifier for the reader
        self.assertTrue(any('ADI nº 2.135' in n for n in r['external_layer_notes']))
        self.assertNotIn('ADI', _body(r))
        self.assertIn('Municípios não aparecem', self.by['CF88:ART.39:PAR.2']['content']['atencao'])
        self.assertEqual(self.by['CF88:ART.39:PAR.4']['granularity']['covered_targets'], ['CF88:ART.39:PAR.8'])

    def test_art40_permanent_vs_transition(self):
        a40 = [r for t, r in self.by.items() if t.startswith('CF88:ART.40')]
        self.assertEqual(len(a40), 22)
        for r in a40:
            for k in ('o_que_diz', 'o_que_significa'):
                self.assertNotRegex(r['content'][k], r'regras? de transi[çc][ãa]o', r['target_id'])       # never in the core
        self.assertIn('regras de transição', self.by['CF88:ART.40']['content']['atencao'].lower())
        iii = self.by['CF88:ART.40:PAR.1:INC.III']['content']['o_que_diz']
        self.assertIn('62 anos para a mulher e 65 para o homem', iii)
        self.assertIn('emenda à Constituição estadual ou à Lei Orgânica', iii)
        self.assertIn('70 anos', self.by['CF88:ART.40:PAR.1:INC.II']['content']['o_que_diz'])
        self.assertEqual(self.by['CF88:ART.40:PAR.14']['granularity']['covered_targets'], ['CF88:ART.40:PAR.15', 'CF88:ART.40:PAR.16'])
        self.assertEqual(self.by['CF88:ART.40:PAR.4-A']['granularity']['covered_targets'], ['CF88:ART.40:PAR.4-B', 'CF88:ART.40:PAR.4-C'])
        self.assertIn('art. 149, § 1º-A', self.by['CF88:ART.40:PAR.18']['content']['o_que_significa'])

    def test_art41_stability(self):
        ov = self.by['CF88:ART.41']['content']
        self.assertIn('três anos', ov['o_que_diz'])
        self.assertIn('art. 169, § 4º', ov['atencao'])
        p1 = self.by['CF88:ART.41:PAR.1']
        self.assertEqual(p1['granularity']['role'], 'BLOCK')
        for inc in ('INC.I', 'INC.II', 'INC.III'):
            self.assertEqual(self.rows[f'CF88:ART.41:PAR.1:{inc}']['coverage'], 'BLOCK_SUBDIVISION')
        self.assertIn('Reintegração', self.by['CF88:ART.41:PAR.2']['content']['o_que_significa'])
        self.assertIn('proporcional', self.by['CF88:ART.41:PAR.3']['content']['o_que_diz'])
        self.assertIn('avaliação periódica', self.by['CF88:ART.41:PAR.4']['content']['atencao'])

    def test_no_duplication_inside_batch(self):
        self.assertEqual(self.checks['duplication_pairs'], [])
        self.assertEqual(EC.duplication(self.new, self.ctx.limits['max_section_similarity']), [])

    def test_risk_classification(self):
        self.assertEqual(self.checks['risk_counts'], {'LOW': 8, 'MEDIUM': 23, 'HIGH': 38})
        risk = {r['target_id']: r['risk'] for r in self.checks['rows']}
        for t in ('CF88:ART.37:INC.XI', 'CF88:ART.37:INC.XVI', 'CF88:ART.37:PAR.4', 'CF88:ART.37:PAR.5', 'CF88:ART.39'):
            self.assertEqual(risk[t], 'HIGH', t)
        self.assertTrue(all(v == 'HIGH' for t, v in risk.items() if t.startswith(('CF88:ART.40', 'CF88:ART.41'))))

    # ---------------- index and determinism ----------------
    def test_lookup_resolution(self):
        e = E.lookup_idx('CF88:ART.40:PAR.4-C', LK, PL)
        self.assertEqual((e['resolution_type'], e['anchor_target_id']), ('COVERED_BY_BLOCK', 'CF88:ART.40:PAR.4-A'))
        self.assertEqual(E.lookup_idx('CF88:ART.37:CAPUT', LK, PL)['review'], 'HUMAN_APPROVED_T1')
        self.assertEqual(E.lookup_idx('CF88:ART.37:PAR.6', LK, PL)['review'], 'HUMAN_APPROVED_T1')
        self.assertEqual(E.lookup_idx('CF88:ART.37:PAR.5', LK, PL)['review'], 'HUMAN_APPROVED_T1')
        self.assertEqual(E.lookup_idx('CF88:ART.37:INC.XI', LK, PL)['explanation_id'], 'ENTENDA/CF88:ART.37:INC.XI/BASE/2')
        self.assertIsNone(E.lookup_idx('CF88:ART.40:PAR.21', LK, PL))

    def test_three_fresh_builds_byte_identical(self):
        trees = []
        with tempfile.TemporaryDirectory() as t:
            for k in range(3):
                d = Path(t) / f'r{k}'
                d.mkdir()
                for n in INPUTS:
                    shutil.copyfile(BD / n, d / n)
                with contextlib.redirect_stdout(io.StringIO()):
                    PB.run(d)
                    EC.run(d)
                trees.append({n: sha(d / n) for n in GENERATED})
        self.assertEqual(trees[0], trees[1])
        self.assertEqual(trees[1], trees[2])
        self.assertEqual(trees[0], {n: sha(BD / n) for n in GENERATED})


@unittest.skipUnless((CANDIDATE / '_host/CANDIDATE_STATUS.json').is_file(), 'host candidate not built')
class Batch05CandidateTest(unittest.TestCase):
    def test_candidate_preserves_approved_and_is_not_deployable(self):
        st = json.loads((CANDIDATE / '_host/CANDIDATE_STATUS.json').read_text(encoding='utf-8'))
        self.assertEqual(st['status'], 'HOST_CANDIDATE_ALL_APPROVED_NOT_STAGED')
        self.assertTrue(st['byte_identical'])
        self.assertTrue(st['preservation_ok'])
        self.assertEqual(st['explanations'], {'approved_reused': 220, 'batch05_approved': 69, 'total': 289, 'total_human_approved_t1': 289})
        self.assertEqual(st['diff_vs_approved']['removed'], [])
        self.assertEqual(st['diff_vs_approved']['changed_except_offset'], [])
        approved = ROOT / st['approved_pair']['path']
        self.assertEqual(sha(approved / 'ENTENDA_LOOKUP.IDX'), st['approved_pair']['lookup_sha256'])   # physical pair untouched
        self.assertEqual(sha(approved / 'ENTENDA_PAYLOAD.DAT'), st['approved_pair']['payload_sha256'])
        for n, v in st['candidate_pair'].items():
            self.assertEqual(sha(CANDIDATE / 'SD/99_LEX_V1/30_ENTENDA' / n), v['sha256'], n)
        rows = [l.split('|') for l in (CANDIDATE / 'SD/99_LEX_V1/30_ENTENDA/ENTENDA_LOOKUP.IDX').read_text(encoding='utf-8').splitlines()
                if l and not l.startswith('#')]
        self.assertEqual(sum(1 for r in rows if r[6] == 'PENDING_HUMAN_REVIEW'), 0)
        self.assertEqual(sum(1 for r in rows if r[6] == 'HUMAN_APPROVED_T1'), 448)
        self.assertEqual(st['diff_vs_approved']['added'], 86)
        self.assertTrue(st['diff_vs_approved']['added_equals_batch05_targets'])


if __name__ == '__main__':
    unittest.main()
