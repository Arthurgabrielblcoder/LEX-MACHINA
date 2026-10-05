"""Tests for ENTENDA CF MACRO BATCH 07 (arts. 76-175): T1 drafts (drafter + critic passes), risk triage and review packets.
Nothing is approved in this batch: every new explanation is PENDING_HUMAN_REVIEW."""
import hashlib
import json
import re
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
import entenda_engine as E  # noqa: E402
import production_batch as PB  # noqa: E402

BD = HERE / 'derived/production_batch_07_macro'
BODY = ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao')


def load(name):
    return json.loads((BD / name).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class MacroBatch07(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = E.NormContext('CF88')
        cls.ms = load('MACRO_SPEC.json')
        cls.spec = load('BATCH_SPEC.json')
        cls.corpus = E.load_corpus(BD / 'CF88_MACRO_07.entenda.jsonl')
        cls.triage = load('MACRO07_TRIAGE.json')
        cls.sel = load('SELECTION_REPORT.json')
        cls.plan = load('BATCH07_TARGET_PLAN.json')

    def test_scope_is_76_to_175_in_four_sub_blocks(self):
        sb = self.ms['sub_blocks']
        self.assertEqual([(x, sb[x]['start'], sb[x]['end']) for x in 'ABCD'], [('A', 76, 100), ('B', 101, 125), ('C', 126, 150), ('D', 151, 175)])
        self.assertEqual(self.ms['sub_blocks_built'], ['A', 'B', 'C', 'D'])
        arts = [a for x in 'ABCD' for a in M.article_targets(self.ctx, 'CF88', sb[x]['start'], sb[x]['end'])]
        self.assertEqual(self.spec['scope'], arts)
        self.assertNotIn('CF88:ART.176', arts)

    def test_nothing_approved(self):
        self.assertTrue(self.corpus)
        self.assertEqual({r['review_status'] for r in self.corpus}, {'PENDING_HUMAN_REVIEW'})
        self.assertEqual(self.triage['human_approved_t1_granted'], 0)
        self.assertEqual(self.triage['micro_adjustments']['applied'], 0)
        cfg = json.loads((HERE / 'editorial/T1_PIPELINE_CONFIG.json').read_text(encoding='utf-8')) if (HERE / 'editorial/T1_PIPELINE_CONFIG.json').is_file() else {}
        for k in ('AUTO_APPROVE_LOW', 'AUTO_APPROVE_MEDIUM', 'MICROAUTO_APPLY'):
            self.assertFalse(cfg.get(k, False), k)

    def test_engine_contract_and_lei_seca(self):
        E.validate_corpus(self.corpus, self.ctx)
        for r in self.corpus:
            E.validate_explanation(r, self.ctx)
            self.assertEqual(r['source']['source_text_snapshot'], self.ctx.snapshot(r['target_id'], r['granularity'].get('covered_targets', [])))
        self.assertEqual(self.triage['checks']['status'], 'PASS')

    def test_every_current_target_selected_or_skipped_with_reason(self):
        rows = self.sel['selection']
        cur = [r for r in rows if r['status'] == 'CURRENT']
        self.assertTrue(all(r['classification'] in PB.SELECTED + ('NO_SEPARATE_EXPLANATION',) for r in cur))
        for r in cur:
            if r['classification'] == 'NO_SEPARATE_EXPLANATION':
                self.assertTrue(r.get('selection_reason') and r.get('covered_by'), r['target_id'])
        s = self.sel['summary']
        self.assertEqual(s['selected'] + s['by_classification'].get('NO_SEPARATE_EXPLANATION', 0), s['targets_current'])

    def test_every_article_has_overview(self):
        own = {r['target_id'] for r in self.corpus} | set(self.spec['reused'])
        for a in self.spec['scope']:
            if self.ctx.effective_status(a) == 'CURRENT':
                self.assertIn(a, own)

    def test_approved_overview_reused_unchanged(self):
        self.assertIn('CF88:ART.150', self.spec['reused'])
        self.assertNotIn('CF88:ART.150', {r['target_id'] for r in self.corpus})
        log = load('drafts/MACRO07_C_CRITIC_LOG.json')['corrections']
        self.assertTrue(any(c['target_id'] == 'CF88:ART.150' and c['section'] == '*' for c in log))

    def test_body_free_of_case_numbers_and_veiled_jurisprudence(self):
        for r in self.corpus:
            for k in BODY:
                self.assertIsNone(E.EXTERNAL_CASE_RE.search(r['content'][k] or ''), (r['target_id'], k))

    def test_critic_pass_reproduces_versioned_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp) / 'b'
            shutil.copytree(BD / 'drafts', t / 'drafts')
            shutil.copy(BD / 'MACRO_SPEC.json', t / 'MACRO_SPEC.json')
            for x in 'ABCD':
                parts = sorted(str(p) for p in (t / 'drafts/pass1').glob(f'MACRO07_{x}_PASS1_*.json'))
                subprocess.run([sys.executable, str(HERE / 'macro_critic_pass.py'), str(t), x, str(t / f'drafts/pass1/MACRO07_{x}_CRITIC_EDITS.json'), *parts],
                               check=True, capture_output=True)
                for n in (f'MACRO07_{x}_DRAFTS.json', f'MACRO07_{x}_CRITIC_LOG.json'):
                    self.assertEqual(sha(t / 'drafts' / n), sha(BD / 'drafts' / n), n)

    def test_critic_log_is_complete(self):
        total = 0
        for x in 'ABCD':
            log = load(f'drafts/MACRO07_{x}_CRITIC_LOG.json')
            self.assertTrue(log['corrections'])
            for c in log['corrections']:
                self.assertTrue(c['reason'] and c['category'] and 'before' in c and 'after' in c)
            total += len(log['corrections'])
        self.assertEqual(total, sum(v['corrections'] for v in self.triage['critic'].values()))

    def test_judicial_review_annotation_routes_to_high(self):
        vig = self.plan['vigency_by_target']
        rows = {x['target_id']: x for x in self.triage['rows']}
        n = 0
        for r in self.corpus:
            scope = [r['target_id']] + r['granularity'].get('covered_targets', [])
            scope += [t for s in list(scope) for t in self.ctx.subtree(s) if t != s]
            if any(M.JUDICIAL_REVIEW_RE.search(a) for t in scope for a in vig.get(t, [])):
                n += 1
                self.assertEqual(rows[r['target_id']]['legal_risk'], 'HIGH', r['target_id'])
                self.assertEqual(rows[r['target_id']]['queue'], 'D_FULL_HUMAN_REVIEW', r['target_id'])
        self.assertGreater(n, 0)

    def test_queues_close_and_packets_exist(self):
        rows = self.triage['rows']
        self.assertEqual(len(rows), len(self.corpus))
        self.assertEqual(sum(self.triage['counts'].values()), len(rows))
        self.assertEqual(self.triage['counts']['E_HARD_FAIL'], 0)
        for f in ('MACRO07_COMPACT_AB_REVIEW.md', 'MACRO07_QUICK_C_REVIEW.md', 'MACRO07_FULL_D_REVIEW.md', 'MACRO07_HARD_FAIL_REPORT.md',
                  'MACRO07_HUMAN_REVIEW_PRIORITY.md', 'MACRO07_BACKLOG.md', 'MACRO07_SCALE_REPORT.md'):
            self.assertTrue((BD / f).is_file(), f)
        full = (BD / 'MACRO07_FULL_D_REVIEW.md').read_text(encoding='utf-8')
        for x in rows:
            if x['queue'] == 'D_FULL_HUMAN_REVIEW':
                self.assertIn(f"`{x['target_id']}`", full)
        diag = (BD / 'MACRO07_D_ESCALATION_DIAGNOSTIC.md').is_file()
        self.assertEqual(diag, self.triage['d_ratio'] > 0.4)

    def test_checkpoints_per_sub_block(self):
        for x in 'ABCD':
            cp = load(f'MACRO07_{x}_CHECKPOINT.json')
            self.assertEqual(cp['status'], 'PASS')
            self.assertEqual(cp['human_approved_t1_granted'], 0)
            st = cp['stats']
            self.assertEqual(st['select'] + st['skip'], st['targets_current'])

    def test_jurisprudence_recommendations_not_fabricated(self):
        j = load('JURISPRUDENCE_LINK_RECOMMENDATIONS.json')
        self.assertGreater(j['total'], 0)
        self.assertEqual(j['ready_to_link'], 0)
        vig = self.plan['vigency_by_target']
        annotated = {m.group(0).replace('Vide ', '', 1).strip() for v in vig.values() for a in v for m in [M.JUDICIAL_REVIEW_RE.search(a)] if m}
        for r in j['recommendations']:
            self.assertTrue(r['desired_reference'] == 'IDENTIFICACAO_PENDENTE' or r['desired_reference'] in annotated, r)

    def test_determinism_evidence(self):
        ev = load('DETERMINISM_EVIDENCE.json')
        self.assertTrue(ev['byte_identical'])
        self.assertGreaterEqual(ev['runs'], 3)
        self.assertEqual(ev['sub_blocks_built'], ['A', 'B', 'C', 'D'])

    def test_rebuild_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp) / BD.name
            shutil.copytree(BD / 'drafts', t / 'drafts')
            for f in ('MACRO_SPEC.json', 'EDITORIAL_INPUT.json', 'RELATIONS_PIN.json', 'BACKLOG_INPUT.json'):
                shutil.copy(BD / f, t / f)
            M.build(t)
            for p in sorted(BD.rglob('*')):
                rel = p.relative_to(BD)
                if p.is_file() and p.name != 'DETERMINISM_EVIDENCE.json':
                    self.assertEqual(sha(t / rel), sha(p), str(rel))

    def test_shared_modules_untouched(self):
        man = json.loads((HERE / 'derived/production_batch_06/BATCH06_MANIFEST.json').read_text(encoding='utf-8'))
        code = man.get('code_sha256_lf') or {}
        self.assertTrue(code)
        for name, h in code.items():
            if (HERE / name).is_file():
                self.assertEqual(M.sha_lf(HERE / name), h, name)

    def test_backlog_registers_old_content_without_editing(self):
        b = self.triage['backlog']
        self.assertEqual(b['old_content']['by_review_status'].get('HUMAN_APPROVED_T1'), 300)
        text = (BD / 'MACRO07_BACKLOG.md').read_text(encoding='utf-8')
        self.assertIn('Nenhum foi alterado', text)

    def test_sub_block_counts_add_up(self):
        tot = Counter()
        for x in 'ABCD':
            st = load(f'MACRO07_{x}_CHECKPOINT.json')['stats']
            tot['new'] += st['new_explanations']
            tot.update({q: n for q, n in st['queues'].items()})
        self.assertEqual(tot['new'], len(self.corpus))
        for q, n in self.triage['counts'].items():
            self.assertEqual(tot[q], n, q)


if __name__ == '__main__':
    unittest.main()
