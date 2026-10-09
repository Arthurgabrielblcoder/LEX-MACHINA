"""Tests for ENTENDA CF MACRO BATCH 08 (CF arts. 176-250 + ADCT): segment builder, CF88_OFFICIAL_RUNTIME text profile, temporal layer,
T1 drafts (drafter + critic passes + recorded human patch), risk triage and review packets, and the recorded human review round: every new
explanation is HUMAN_APPROVED_T1 only through MACRO_SPEC.human_review (round decisions, explicit per-target flag resolutions, approval gate)."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_entenda_macro_batch as M  # noqa: E402
import build_entenda_macro_segment as S  # noqa: E402
import entenda_engine as E  # noqa: E402
import entenda_text_profile as TP  # noqa: E402
import production_batch as PB  # noqa: E402

BD = HERE / 'derived/production_batch_08_macro'
BD07 = HERE / 'derived/production_batch_07_macro'
BODY = ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao')
SUBS = 'ABCDEFGH'


def load(name, bd=BD):
    return json.loads((bd / name).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class TextProfile(unittest.TestCase):
    def test_profile_rebuilds_byte_identical(self):
        res = TP.check('CF88_OFFICIAL_RUNTIME')
        self.assertTrue(res)
        self.assertTrue(all(res.values()), res)

    def test_round_trip_and_cf88_unchanged(self):
        man = json.loads((HERE / 'profiles/CF88_OFFICIAL_RUNTIME/PROFILE_MANIFEST.json').read_text(encoding='utf-8'))
        rt = man['round_trip']
        self.assertEqual(rt['status'], 'PASS')
        self.assertEqual(rt['mismatched_count'], 0)
        self.assertGreater(rt['profiled_targets_with_text'], 0)
        self.assertEqual((rt['other_namespaces_text_mismatch'], rt['other_namespaces_status_mismatch']), (0, 0))
        ctx_g = E.NormContext('CF88')
        ctx_p = E.NormContext('CF88', HERE / 'profiles/CF88_OFFICIAL_RUNTIME/entenda_config.json')
        for t in ('CF88:ART.1', 'CF88:ART.176', 'CF88:ART.225', 'CF88:ART.250'):
            self.assertEqual(ctx_g.snapshot(t), ctx_p.snapshot(t), t)
            self.assertEqual(ctx_g.legal_status(t), ctx_p.legal_status(t), t)

    def test_adct_ids_canonical_no_new_namespace(self):
        ctx = E.NormContext('CF88', HERE / 'profiles/CF88_OFFICIAL_RUNTIME/entenda_config.json')
        ids = [t for t in ctx.order if t.startswith('ADCT:')]
        self.assertTrue(ids)
        self.assertEqual({t.split(':')[0] for t in ctx.order}, {'CF88', 'ADCT'})
        self.assertIn('ADCT:ART.10:INC.II:AL.a', ids)
        self.assertIn('ADCT:ART.18-A', ids)
        self.assertEqual(ctx.effective_status('ADCT:ART.125'), 'CURRENT')


class MacroBatch08(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ms = load('MACRO_SPEC.json')
        cls.ctx = E.NormContext('CF88', S.config_path(cls.ms))
        cls.spec = load('BATCH_SPEC.json')
        cls.records = E.load_corpus(BD / 'CF88_MACRO_08.entenda.jsonl')
        cls.corpus = [r for r in cls.records if r['status'] == 'ACTIVE']
        cls.retired = [r for r in cls.records if r['status'] == 'RETIRED']
        cls.triage = load('MACRO08_TRIAGE.json')
        cls.pre_triage = load('MACRO08_TRIAGE_PRE_HUMAN_REVIEW.json')  # calibration the human review worked on (frozen)
        cls.hr = cls.ms['human_review']
        cls.round = load(cls.hr['round_decisions'])
        cls.sel = load('SELECTION_REPORT.json')
        cls.tin = load('TEMPORAL_INPUT.json')
        cls.tmap = load('MACRO08_ADCT_TEMPORAL_MAP.json')
        cls.skips = load('MACRO08_SKIP_REGISTER.json')

    def test_scope_sub_blocks_and_segments(self):
        sb = self.ms['sub_blocks']
        self.assertEqual(self.ms['sub_blocks_built'], list(SUBS))
        self.assertEqual([(x, sb[x]['namespace'], sb[x]['start'], sb[x]['end']) for x in 'ABC'],
                         [('A', 'CF88', 176, 200), ('B', 'CF88', 201, 225), ('C', 'CF88', 226, 250)])
        self.assertEqual({sb[x]['namespace'] for x in 'DEFGH'}, {'ADCT'})
        arts = [a for x in SUBS for a in S.article_targets(self.ctx, sb[x])]
        adct = [a for a in self.ctx.order if a.startswith('ADCT:') and a.count(':') == 1]
        self.assertEqual(sorted(a for a in arts if a.startswith('ADCT:')), sorted(adct))
        self.assertNotIn('CF88:ART.175', arts)
        self.assertNotIn('CF88:ART.251', arts)

    def test_approved_only_by_recorded_round(self):
        self.assertEqual(len(self.corpus), 179)
        self.assertEqual({r['review_status'] for r in self.corpus}, {'HUMAN_APPROVED_T1'})
        for r in self.corpus:
            self.assertEqual(r['human_review']['review_scope'], self.hr['review_scope'], r['target_id'])
            self.assertIn(r['human_review']['decision'], ('APPROVED', 'APPROVED_AFTER_ADJUSTMENT'), r['target_id'])
        self.assertEqual(self.spec['round_approvals'], [dict(review_scope=self.hr['review_scope'], decisions=self.hr['round_decisions'])])
        self.assertEqual(self.round['review_status'], 'ROUND_REVIEW_COMPLETED')
        self.assertEqual(sorted(d['target_id'] for d in self.round['decisions']), sorted(r['target_id'] for r in self.corpus))
        self.assertEqual(self.triage['human_approved_t1_granted'], 179)
        self.assertEqual(self.triage['rows'], [])  # nothing left pending
        ra = self.triage['round_approvals']
        self.assertEqual((ra['approved'], ra['approved_unchanged'], ra['approved_after_adjustment'], ra['rejected'], ra['pending']), (179, 149, 30, 0, []))
        self.assertEqual(ra['gate']['status'], 'PASS')
        self.assertEqual(self.triage['checks']['approval_gate'], 'PASS')
        self.assertEqual(self.triage['micro_adjustments']['applied'], 0)
        cfg = json.loads((HERE / 'editorial/T1_PIPELINE_CONFIG.json').read_text(encoding='utf-8')) if (HERE / 'editorial/T1_PIPELINE_CONFIG.json').is_file() else {}
        for k in ('AUTO_APPROVE_LOW', 'AUTO_APPROVE_MEDIUM', 'MICROAUTO_APPLY'):
            self.assertFalse(cfg.get(k, False), k)

    def test_engine_contract_and_lei_seca(self):
        E.validate_corpus(self.records, self.ctx)
        for r in self.corpus:
            E.validate_explanation(r, self.ctx)
            self.assertEqual(r['source']['source_text_snapshot'], self.ctx.snapshot(r['target_id'], r['granularity'].get('covered_targets', [])))
        self.assertEqual(self.triage['checks']['status'], 'PASS')

    def test_every_current_target_selected_or_skipped_with_reason(self):
        cur = [r for r in self.sel['selection'] if r['status'] == 'CURRENT']
        self.assertTrue(all(r['classification'] in PB.SELECTED + ('NO_SEPARATE_EXPLANATION',) for r in cur))
        for r in cur:
            if r['classification'] == 'NO_SEPARATE_EXPLANATION':
                self.assertTrue(r.get('selection_reason') and r.get('covered_by'), r['target_id'])
        for row in self.skips['rows']:
            self.assertIn(row['decision'], S.SKIP_CODES, row['article'])
            self.assertTrue(row['reason'], row['article'])

    def test_every_adct_article_has_temporal_class_with_provenance(self):
        rows = self.tmap['articles']
        self.assertEqual(len(rows), len([a for a in self.ctx.order if a.startswith('ADCT:') and a.count(':') == 1]))
        for r in rows:
            self.assertIn(r['temporal_class'], S.TEMPORAL_CLASSES, r['article'])
            if r['temporal_class'] != 'REVOKED':
                self.assertTrue(r['provenance'], r['article'])
        self.assertEqual(sum(self.tmap['counts'].values()), len(rows))

    def test_exhausted_adct_not_explained_as_current(self):
        own = {r['target_id'] for r in self.corpus}
        for r in self.tmap['articles']:
            if r['temporal_class'] in ('REVOKED', 'HISTORICAL_ONLY'):
                self.assertNotIn(r['article'], own, r['article'])
            if r['temporal_class'] == 'EFFECT_EXHAUSTED' and r['article'] in own:
                # selected only as historical-pedagogical, declared as producing no effects
                self.assertEqual(r['decision'], 'SELECT', r['article'])
                self.assertIs(r['produces_effects'], False, r['article'])
                self.assertIn('Exaurido', r['situation_as_of'], r['article'])
            elif r['temporal_class'] == 'EFFECT_EXHAUSTED':
                self.assertTrue(r['decision'].startswith(('SKIP_', 'EXCLUDED_')), r['article'])

    def test_unresolved_temporal_goes_to_d(self):
        rows = {x['target_id']: x for x in self.pre_triage['rows']}
        for r in self.corpus:
            t = r['target_id']
            if not t.startswith('ADCT:'):
                continue
            cls = S.temporal_class_of(self.tin, t, self.ctx)
            if cls in S.UNRESOLVED_CLASSES and not S.dated_trigger(self.tin, t):
                self.assertEqual(rows[t]['queue'], 'D_FULL_HUMAN_REVIEW', t)
                self.assertIn('TEMPORAL_STATUS_UNRESOLVED', rows[t]['legal_rules'], t)
            if S.dated_trigger(self.tin, t):
                self.assertNotIn('TEMPORAL_STATUS_UNRESOLVED', rows[t]['legal_rules'], t)

    def test_transition_evidence_matches_temporal_layer(self):
        te = load('MACRO08_TRANSITION_EVIDENCE.json')
        self.assertEqual(te['resolved'] + te['unresolved'], te['total'])
        for e in te['entries']:
            self.assertEqual(e['resolved_deterministically'], S.is_resolved(self.tin, e['target_id'], self.ctx), e['target_id'])
            self.assertTrue(e['source_text_sha256'] and e['runtime_sha256'], e['target_id'])

    def test_every_built_article_overview_or_skip(self):
        own = {r['target_id'] for r in self.corpus} | set(self.spec['reused'])
        skipped = {r['article'] for r in self.skips['rows']}
        for a in self.spec['scope']:
            if self.ctx.effective_status(a) == 'CURRENT' and a not in skipped:
                self.assertIn(a, own)

    def test_approved_overview_reused_unchanged(self):
        self.assertIn('CF88:ART.225', self.spec['reused'])
        self.assertNotIn('CF88:ART.225', {r['target_id'] for r in self.corpus})

    def test_body_free_of_case_numbers(self):
        for r in self.corpus:
            for k in BODY:
                self.assertIsNone(E.EXTERNAL_CASE_RE.search(r['content'][k] or ''), (r['target_id'], k))

    def test_judicial_review_annotations_classified(self):
        rows = {x['target_id']: x for x in self.pre_triage['rows']}
        for t, e in self.tin['explanations'].items():
            jr = e.get('judicial_review')
            if jr and t in rows:
                self.assertIn(jr['classification'], ('JUDICIAL_REVIEW_CONTEXT_ONLY', 'JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS'))
                self.assertTrue(jr['reason'])
                if jr['classification'] == 'JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS':
                    self.assertEqual(rows[t]['queue'], 'D_FULL_HUMAN_REVIEW', t)

    def test_critic_pass_and_human_patch_reproduce_versioned_drafts(self):
        """pass1 (drafter) -> macro_critic_pass (critic) reproduces the frozen pre-review drafts; + apply_macro08_human_review (recorded
        human patch) reproduces the versioned sub-block drafts and the apply record byte for byte."""
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp) / 'ENTENDA_ENGINE/derived' / BD.name
            shutil.copytree(BD / 'drafts', t / 'drafts')
            for f in ('MACRO_SPEC.json', self.hr['decisions']):
                shutil.copy(BD / f, t / f)
            for x in SUBS:
                parts = sorted(str(p) for p in (t / 'drafts/pass1').glob(f'MACRO08_{x}_PASS1_*.json'))
                subprocess.run([sys.executable, str(HERE / 'macro_critic_pass.py'), str(t), x, str(t / f'drafts/pass1/MACRO08_{x}_CRITIC_EDITS.json'), *parts],
                               check=True, capture_output=True)
                self.assertEqual(sha(t / 'drafts' / f'MACRO08_{x}_CRITIC_LOG.json'), sha(BD / 'drafts' / f'MACRO08_{x}_CRITIC_LOG.json'), x)
            pre = {e['target_id']: e for e in load(self.hr['pre_review_evidence']['drafts'])['explanations']}
            critic = {e['target_id']: e for x in SUBS for e in load(f'drafts/MACRO08_{x}_DRAFTS.json', t)['explanations']}
            self.assertEqual(critic, pre)
            subprocess.run([sys.executable, '-I', str(HERE / 'apply_macro08_human_review.py'), '--root', tmp], check=True, capture_output=True)
            for x in SUBS:
                self.assertEqual(sha(t / 'drafts' / f'MACRO08_{x}_DRAFTS.json'), sha(BD / 'drafts' / f'MACRO08_{x}_DRAFTS.json'), x)
            self.assertEqual(load(self.hr['apply_metadata'], t), load(self.hr['apply_metadata']))
            a, b = load(self.hr['apply_audit'], t), load(self.hr['apply_audit'])
            self.assertEqual(sorted(a['after_sha256'].values()), sorted(b['after_sha256'].values()))
            self.assertEqual((a['content_patches_applied'], a['metadata_only_patches'], a['total_decisions']),
                             (b['content_patches_applied'], b['metadata_only_patches'], b['total_decisions']))

    def test_human_patch_scope(self):
        """30 content patches only in the authorized fields; the other 149 (148 + ADCT:ART.101, provenance only) object-identical."""
        dec = load(self.hr['decisions'])
        self.assertEqual((len(dec['patches']), dec['review_summary']['approved_unchanged'], dec['review_summary']['rejected']), (31, 148, 0))
        self.assertEqual(Counter(p['queue'] for p in dec['patches']), Counter(A=20, B=7, C=4))
        pre = {e['target_id']: e for e in load(self.hr['pre_review_evidence']['drafts'])['explanations']}
        now = {e['target_id']: e for x in SUBS for e in load(f'drafts/MACRO08_{x}_DRAFTS.json')['explanations']}
        content = {p['target_id'] for p in dec['patches'] if p.get('set')}
        self.assertEqual(len(content), 30)
        self.assertEqual({t for t in pre if pre[t] != now[t]}, content)
        self.assertEqual(now['ADCT:ART.101'], pre['ADCT:ART.101'])
        by = {d['target_id']: d for d in self.round['decisions']}
        self.assertEqual(self.round['decision_counts'], dict(APPROVED=149, APPROVED_AFTER_ADJUSTMENT=30, REJECTED=0))
        self.assertEqual(by['ADCT:ART.101']['human_decision'], 'ADJUST_PROVENANCE_THEN_APPROVE')
        self.assertEqual(by['ADCT:ART.101']['to_explanation_id'], 'ENTENDA/ADCT:ART.101/BASE/1')
        for t in content:
            self.assertEqual(by[t]['decision'], 'APPROVED_AFTER_ADJUSTMENT', t)
            self.assertTrue(by[t]['changes'] and by[t]['original_content'], t)
            self.assertTrue(by[t]['to_explanation_id'].endswith('/2'), t)
        retired = {r['explanation_id']: r for r in self.retired}
        self.assertEqual(sorted(retired), sorted(f'ENTENDA/{t}/BASE/1' for t in content))
        self.assertEqual({r['review_status'] for r in self.retired}, {'CHANGES_REQUESTED'})
        frozen = {r['explanation_id']: r for r in E.load_corpus(BD / self.hr['pre_review_evidence']['corpus'])}
        for r in self.corpus:
            if r['editorial_version'] == 1:
                self.assertEqual(r['content'], frozen[r['explanation_id']]['content'], r['target_id'])
                self.assertEqual(r['source'], frozen[r['explanation_id']]['source'], r['target_id'])

    def test_decision_revision_chain(self):
        dec = load(self.hr['decisions'])
        self.assertEqual(dec['revision'], 3)
        self.assertEqual([c['file'] for c in dec['revision_chain']], self.hr['decision_revisions'])
        for c in dec['revision_chain']:
            self.assertEqual(sha(BD / c['file']), c['sha256'], c['file'])
        self.assertEqual(sha(BD / dec['supersedes']['file']), dec['supersedes']['sha256'])
        self.assertEqual(self.round['decisions_source']['sha256'], sha(BD / self.hr['decisions']))
        for f, h in self.round['original_evidence_sha256'].items():
            self.assertEqual(sha(BD / f), h, f)

    def test_flag_resolutions_explicit_and_exact(self):
        """Every finding closed by the review has an explicit per-target record (flag, decision, reason, approved version, provenance), each
        record closes exactly its declared occurrences, and nothing is left open (no generic rule)."""
        recs = load(self.hr['flag_resolutions'])['records']
        self.assertEqual((len(recs), sum(r['occurrences'] for r in recs)), (25, 26))
        active = {r['target_id']: r for r in self.corpus}
        for r in recs:
            for k in ('flag', 'decision', 'reason_code', 'justification', 'approved_explanation_id', 'provenance'):
                self.assertTrue(r.get(k), (r['id'], k))
            self.assertEqual(r['approved_explanation_id'], active[r['target_id']]['explanation_id'], r['id'])
            self.assertIn(r['applied_as'], ('VALIDATOR_KNOWN_RESOLUTION', 'EDITORIAL_CHECK_RESOLUTION', 'HUMAN_REVIEW_CONTENT_PROVENANCE'), r['id'])
        g = self.triage['round_approvals']['gate']
        used = Counter(c['resolution'] for x in g['rows'] for c in x['closed_by_human_resolution'])
        self.assertEqual(dict(used), {r['id']: r['occurrences'] for r in recs})
        self.assertEqual((g['failing'], g['resolution_occurrence_mismatch']), ([], []))
        for x in g['rows']:
            self.assertEqual((x['hard_fail'], x['review_required_open'], x['editorial_checks_open'], x['external_fact_not_covered_by_provenance']),
                             ([], [], 0, []), x['target_id'])
        known = json.loads((HERE / 'editorial/T1_KNOWN_RESOLUTIONS.json').read_text(encoding='utf-8'))['resolutions']
        self.assertFalse({r['approved_explanation_id'] for r in recs} & set(known))  # shared file untouched: resolutions stay batch-local

    def test_critic_log_is_complete(self):
        total = 0
        for x in SUBS:
            log = load(f'drafts/MACRO08_{x}_CRITIC_LOG.json')
            self.assertTrue(log['corrections'], x)
            for c in log['corrections']:
                self.assertTrue(c['reason'] and c['category'] and 'before' in c and 'after' in c)
            total += len(log['corrections'])
        self.assertEqual(total, sum(v['corrections'] for v in self.triage['critic'].values()))

    def test_queues_close_and_packets_exist(self):
        rows = self.pre_triage['rows']  # the calibration handed to the human review (frozen); the live triage has nothing pending
        self.assertEqual(len(rows), len(self.corpus))
        self.assertEqual(sum(self.pre_triage['counts'].values()), len(rows))
        self.assertEqual(self.pre_triage['counts']['E_HARD_FAIL'], 0)
        self.assertEqual(sum(self.triage['counts'].values()), 0)
        for f in ('MACRO08_COMPACT_AB_REVIEW.md', 'MACRO08_QUICK_C_REVIEW.md', 'MACRO08_FULL_D_REVIEW.md', 'MACRO08_HARD_FAIL_REPORT.md',
                  'MACRO08_HUMAN_REVIEW_PRIORITY.md', 'MACRO08_BACKLOG.md', 'MACRO08_SCALE_REPORT.md', 'MACRO08_SOURCE_ANOMALIES.md',
                  'MACRO08_ADCT_STRUCTURAL_AUDIT.md', 'MACRO08_D_DIAGNOSTIC.md'):
            self.assertTrue((BD / f).is_file(), f)
        for f in self.hr['pre_review_evidence']['packets']:
            self.assertTrue((BD / f).is_file(), f)
        full = (BD / 'MACRO08_FULL_D_REVIEW_PRE_HUMAN_REVIEW.md').read_text(encoding='utf-8')
        for x in rows:
            if x['queue'] == 'D_FULL_HUMAN_REVIEW':
                self.assertIn(f"`{x['target_id']}`", full)

    def test_segments_add_up(self):
        seg = self.triage['segments']
        self.assertEqual(set(seg), {'CORPO', 'ADCT'})
        self.assertEqual(sum(s['new_explanations'] for s in seg.values()), len(self.corpus))
        for q in ('A_CLEAN_LOW', 'B_CLEAN_MEDIUM', 'C_QUICK_REVIEW', 'D_FULL_HUMAN_REVIEW', 'E_HARD_FAIL'):
            self.assertEqual(sum(s['queues'][q] for s in seg.values()), self.triage['counts'][q], q)
        n = Counter(r['target_id'].split(':')[0] for r in self.corpus)
        self.assertEqual(n['CF88'], seg['CORPO']['new_explanations'])
        self.assertEqual(n['ADCT'], seg['ADCT']['new_explanations'])
        for s in seg.values():
            self.assertEqual((s['human_approved_t1'], s['pending_in_triage']), (s['new_explanations'], 0))

    def test_checkpoints_per_sub_block(self):
        tot = Counter()
        for x in SUBS:
            cp = load(f'MACRO08_{x}_CHECKPOINT.json')
            self.assertEqual(cp['status'], 'PASS')
            st = cp['stats']
            self.assertEqual(cp['human_approved_t1_granted'], st['new_explanations'])
            self.assertEqual(st['select'] + st['skip'], st['targets_current'])
            tot['new'] += st['new_explanations']
        self.assertEqual(tot['new'], len(self.corpus))

    def test_source_anomalies_registered(self):
        a = load('MACRO08_SOURCE_ANOMALIES.json')
        reg = {r['id'] for r in load('SOURCE_ANOMALIES_INPUT.json')['registered']}
        self.assertTrue({'MB08-SRC-01', 'MB08-SRC-02', 'MB08-SRC-03', 'MB08-SRC-06'} <= reg)
        self.assertTrue(a)

    def test_adct_structural_audit_answers(self):
        au = load('MACRO08_ADCT_STRUCTURAL_AUDIT.json')
        self.assertGreaterEqual(len(au['questions']), 10)
        self.assertTrue(all(q['a'] for q in au['questions']))
        self.assertEqual(au['articles'], len([a for a in self.ctx.order if a.startswith('ADCT:') and a.count(':') == 1]))

    def test_determinism_evidence(self):
        ev = load('DETERMINISM_EVIDENCE.json')
        self.assertTrue(ev['byte_identical'])
        self.assertGreaterEqual(ev['runs'], 3)
        self.assertEqual(ev['sub_blocks_built'], list(SUBS))

    def test_rebuild_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp) / BD.name
            S.copy_inputs(BD, t)
            S.build(t)
            for p in sorted(BD.rglob('*')):
                rel = p.relative_to(BD)
                if p.is_file() and p.name != 'DETERMINISM_EVIDENCE.json' and not p.name.startswith('MACRO08_D_DIAGNOSTIC'):
                    self.assertEqual(sha(t / rel), sha(p), str(rel))

    def test_shared_modules_untouched(self):
        for man in (HERE / 'derived/production_batch_06/BATCH06_MANIFEST.json', BD07 / 'MACRO07_MANIFEST.json'):
            code = json.loads(man.read_text(encoding='utf-8')).get('code_sha256_lf') or {}
            self.assertTrue(code, man.name)
            for name, h in code.items():
                if (HERE / name).is_file():
                    self.assertEqual(M.sha_lf(HERE / name), h, f'{man.name}: {name}')

    def test_prior_batches_untouched(self):
        self.assertEqual(self.triage['backlog']['old_content']['by_review_status'].get('HUMAN_APPROVED_T1'), 300)
        text = (BD / 'MACRO08_BACKLOG.md').read_text(encoding='utf-8')
        self.assertIn('Nenhum foi alterado', text)
        own = {r['target_id'] for r in self.corpus}
        for prior in self.spec['prior_corpora']:
            p = ROOT / prior if not Path(prior).is_absolute() else Path(prior)
            if p.is_file():
                for r in E.load_corpus(p):
                    if r.get('review_status') == 'HUMAN_APPROVED_T1':
                        self.assertNotIn(r['target_id'], own, r['target_id'])

    def test_backlog_items_registered(self):
        ids = {i['id'] for i in load('BACKLOG_INPUT.json')['items']}
        self.assertIn('MB08-11', ids)
        text = (BD / 'MACRO08_BACKLOG.md').read_text(encoding='utf-8')
        self.assertIn('PARALLEL_BRANCH_RECONCILIATION', text)


if __name__ == '__main__':
    unittest.main()
