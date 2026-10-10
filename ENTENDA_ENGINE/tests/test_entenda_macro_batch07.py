"""Tests for ENTENDA CF MACRO BATCH 07 (arts. 76-175): T1 drafts (drafter + critic passes), risk triage and review packets.
Explanations leave PENDING_HUMAN_REVIEW only through a recorded human round (MACRO_SPEC.human_review_rounds); the decided ones leave
the triage, and the tests read their pre-round triage rows from the frozen snapshot (history/pre_round_*)."""
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
import t1_second_pass as SP  # noqa: E402

BD = HERE / 'derived/production_batch_07_macro'
BODY = ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao')


def load(name):
    return json.loads((BD / name).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows_with_decided(ms, triage):
    """Triage rows of the pending explanations plus, for those decided in a recorded human round, the row frozen before that round."""
    rows = {}
    for rnd in M.human_rounds(ms):
        dec = {d['target_id'] for d in load(rnd['decisions'])['decisions']}
        rows.update({x['target_id']: x for x in load(rnd['pre_review_evidence']['triage'])['rows'] if x['target_id'] in dec})
    rows.update({x['target_id']: x for x in triage['rows']})
    return rows


class MacroBatch07(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = M.norm_context('CF88')   # NormContext + target status errata (LEGAL_TARGET_ID/status_errata.py)
        cls.ms = load('MACRO_SPEC.json')
        cls.spec = load('BATCH_SPEC.json')
        cls.all = E.load_corpus(BD / 'CF88_MACRO_07.entenda.jsonl')
        cls.corpus = [r for r in cls.all if r['status'] == 'ACTIVE']
        cls.triage = load('MACRO07_TRIAGE.json')
        cls.decided = M.round_targets(BD, cls.ms)
        cls.sel = load('SELECTION_REPORT.json')
        cls.plan = load('BATCH07_TARGET_PLAN.json')

    def test_scope_is_76_to_175_in_four_sub_blocks(self):
        sb = self.ms['sub_blocks']
        self.assertEqual([(x, sb[x]['start'], sb[x]['end']) for x in 'ABCD'], [('A', 76, 100), ('B', 101, 125), ('C', 126, 150), ('D', 151, 175)])
        self.assertEqual(self.ms['sub_blocks_built'], ['A', 'B', 'C', 'D'])
        arts = [a for x in 'ABCD' for a in M.article_targets(self.ctx, 'CF88', sb[x]['start'], sb[x]['end'])]
        self.assertEqual(self.spec['scope'], arts)
        self.assertNotIn('CF88:ART.176', arts)

    def test_only_recorded_rounds_approve(self):
        self.assertTrue(self.corpus)
        for r in self.corpus:
            self.assertEqual(r['review_status'], 'HUMAN_APPROVED_T1' if r['target_id'] in self.decided else 'PENDING_HUMAN_REVIEW', r['target_id'])
        self.assertEqual(self.triage['human_approved_t1_granted'], len(self.decided))
        self.assertEqual(self.triage['checks']['new_not_pending'], [])
        self.assertEqual(self.triage['micro_adjustments']['applied'], 0)
        cfg = json.loads((HERE / 'editorial/T1_PIPELINE_CONFIG.json').read_text(encoding='utf-8')) if (HERE / 'editorial/T1_PIPELINE_CONFIG.json').is_file() else {}
        for k in ('AUTO_APPROVE_LOW', 'AUTO_APPROVE_MEDIUM', 'MICROAUTO_APPLY'):
            self.assertFalse(cfg.get(k, False), k)

    def test_engine_contract_and_lei_seca(self):
        E.validate_corpus(self.all, self.ctx)
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
                subprocess.run([sys.executable, str(HERE / 'macro_critic_pass.py'), str(t), x, str(t / f'drafts/pass1/MACRO07_{x}_CRITIC_EDITS.json'),
                                '--second-pass', str(t / f'drafts/pass1/MACRO07_{x}_SECOND_PASS_EDITS.json'), *parts],
                               check=True, capture_output=True)
                for n in (f'MACRO07_{x}_DRAFTS.json', f'MACRO07_{x}_CRITIC_LOG.json', f'MACRO07_{x}_SECOND_PASS_LOG.json'):
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

    def test_judicial_review_annotation_classified(self):
        """Vide ADI in scope: REQUIRED_FOR_CORRECTNESS -> HIGH/D; CONTEXT_ONLY -> MEDIUM (never D by itself); none left unclassified."""
        vig = self.plan['vigency_by_target']
        rows = rows_with_decided(self.ms, self.triage)
        cls_ = load('SECOND_PASS_INPUT.json')['judicial_review']
        n = 0
        for r in self.corpus:
            scope = [r['target_id']] + r['granularity'].get('covered_targets', [])
            scope += [t for s in list(scope) for t in self.ctx.subtree(s) if t != s]
            if any(M.JUDICIAL_REVIEW_RE.search(a) for t in scope for a in vig.get(t, [])):
                n += 1
                x = rows[r['target_id']]
                self.assertIn(r['target_id'], cls_)
                if cls_[r['target_id']]['classification'] == 'REQUIRED_FOR_CORRECTNESS':
                    self.assertIn('JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS', x['legal_rules'])
                    self.assertEqual(x['queue'], 'D_FULL_HUMAN_REVIEW', r['target_id'])
                else:
                    self.assertNotIn('JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS', x['legal_rules'] + x['legal_secondary'])
                    self.assertTrue(any(s.startswith('JUDICIAL_REVIEW_CONTEXT_ONLY') for s in x['legal_reasons'] + x['legal_secondary']))
        self.assertEqual(n, len(cls_))
        self.assertEqual(self.triage['checks']['judicial_review_unclassified'], [])

    def test_queues_close_and_packets_exist(self):
        rows = self.triage['rows']
        self.assertEqual(len(rows), len(self.corpus) - len(self.decided))
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
        self.assertEqual((BD / 'MACRO07_D_SECOND_PASS_DIAGNOSTIC.md').is_file(), self.triage['d_ratio'] > M.SECOND_PASS_D_LIMIT)

    def test_checkpoints_per_sub_block(self):
        for x in 'ABCD':
            cp = load(f'MACRO07_{x}_CHECKPOINT.json')
            self.assertEqual(cp['status'], 'PASS')
            st = cp['stats']
            self.assertEqual(cp['human_approved_t1_granted'], st.get('human_approved_t1', 0))
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
            shutil.copytree(BD / M.HISTORY, t / M.HISTORY)
            for f in M.root_inputs(BD, self.ms):
                shutil.copy(BD / f, t / f)
            M.build(t)
            for p in sorted(BD.rglob('*')):
                rel = p.relative_to(BD)
                if p.is_file() and p.name != 'DETERMINISM_EVIDENCE.json' and rel.parts[0] != M.HISTORY:
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
        # contagem derivada da mesma fonte do builder (old_content_scan): registros ACTIVE do corpus principal + prior_corpora do
        # MACRO_SPEC; continua valida quando os lotes anteriores mudarem (ex.: 300 -> 382 com o fechamento do Batch06)
        prior = [r for f in [f"ENTENDA_ENGINE/corpus/{self.ms['norma_id']}.entenda.jsonl"] + self.ms['prior_corpora']
                 for r in E.load_corpus(ROOT / f) if r['status'] == 'ACTIVE']
        self.assertNotIn(f"production_batch_07_macro/{self.spec['batch_corpus']}", ' '.join(self.ms['prior_corpora']))
        self.assertEqual(b['old_content']['records_checked'], len(prior))
        self.assertEqual(b['old_content']['by_review_status'], dict(sorted(Counter(r['review_status'] for r in prior).items())))
        self.assertGreater(b['old_content']['by_review_status'].get('HUMAN_APPROVED_T1', 0), 0)
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


class MacroBatch07SecondPass(unittest.TestCase):
    """MACRO07_SECOND_PASS_RISK_COMPRESSION_AND_SOURCE_SANITY."""

    @classmethod
    def setUpClass(cls):
        cls.ctx = M.norm_context('CF88')
        cls.triage = load('MACRO07_TRIAGE.json')
        cls.rows = rows_with_decided(load('MACRO_SPEC.json'), cls.triage)
        cls.corpus = {r['target_id']: r for r in E.load_corpus(BD / 'CF88_MACRO_07.entenda.jsonl') if r['status'] == 'ACTIVE'}
        cls.log = load('MACRO07_SECOND_PASS_EDITORIAL_LOG.json')
        cls.ev = SP.load_transition_evidence(BD / 'MACRO07_TRANSITION_EVIDENCE.json', ROOT)

    def test_art114_viii_separated_in_runtime(self):
        snap = self.corpus['CF88:ART.114']['source']['source_text_snapshot'].split('\n')
        lines = dict(ln.split('\t', 1) for ln in snap)
        self.assertTrue(lines['CF88:ART.114:INC.VIII'].startswith('a execução, de ofício'))
        self.assertNotIn('a execução, de ofício', lines['CF88:ART.114:INC.VII'])
        self.assertEqual(self.ctx.effective_status('CF88:ART.114:INC.VIII'), 'CURRENT')
        self.assertNotIn('Observação estrutural', ' '.join(self.corpus['CF88:ART.114']['external_layer_notes']))

    def test_art155_i_c_is_historical_renumbered(self):
        self.assertEqual(self.ctx.effective_status('CF88:ART.155:INC.I:AL.c'), 'HISTORICAL')
        sel = {r['target_id']: r for r in load('SELECTION_REPORT.json')['selection']}
        self.assertEqual(sel['CF88:ART.155:INC.I:AL.c']['classification'], 'EXCLUDED_HISTORICAL')
        self.assertNotIn('alinea c do inciso I', load('drafts/MACRO07_D_DRAFTS.json')['article_notes']['CF88:ART.155'])

    def test_source_files_and_frozen_status_unchanged(self):
        lock = json.loads((ROOT / 'updater/fontes_oficiais_senado/SOURCES_LOCK.json').read_text(encoding='utf-8'))['sources']['CF88']
        self.assertEqual(sha(ROOT / 'updater/fontes_oficiais_senado' / lock['dir'] / 'normalizado.txt'), lock['normalizado_sha256'])
        man = json.loads((HERE / 'derived/production_batch_06/BATCH06_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual(M.sha_lf(ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS.json'),
                         man['inputs_global_sha256_lf']['LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS.json'])

    def test_transition_evidence_verified_and_decisive(self):
        self.assertEqual(len(self.ev), 26)
        for t, e in self.ev.items():
            x = self.rows[t]
            if e['resolution'] == SP.RESOLVED:
                self.assertNotIn('TRANSITION_OR_TEMPORAL', x['legal_rules'], t)
                self.assertTrue(any(s.startswith('TRANSITION_RESOLVED_BY_VERSIONED_SOURCE') for s in x['legal_reasons'] + x['legal_secondary']), t)
            else:
                self.assertIn('TRANSITION_OR_TEMPORAL', x['legal_rules'], t)
                self.assertEqual(x['queue'], 'D_FULL_HUMAN_REVIEW', t)
        self.assertEqual(self.triage['checks']['transition_without_evidence'], [])

    def test_transition_evidence_fails_closed(self):
        doc = json.loads((BD / 'MACRO07_TRANSITION_EVIDENCE.json').read_text(encoding='utf-8'))
        bad = [dict(doc, targets=[dict(doc['targets'][0], quotes=[dict(source='ADCT_SENADO', quote='Em 2026, o imposto sera extinto.')])]),
               dict(doc, targets=[dict(doc['targets'][0], resolution=SP.ACTIVE, high_criteria=[])]),
               dict(doc, sources=dict(doc['sources'], ADCT_SENADO=dict(doc['sources']['ADCT_SENADO'], sha256='0' * 64)))]
        with tempfile.TemporaryDirectory() as tmp:
            for i, d in enumerate(bad):
                p = Path(tmp) / f'{i}.json'
                p.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')
                with self.assertRaises(SP.SecondPassError):
                    SP.load_transition_evidence(p, ROOT)

    def test_controversy_term_from_lei_seca_is_not_high(self):
        for t in ('CF88:ART.103-A', 'CF88:ART.114'):
            self.assertNotIn('INTERPRETIVE_CONTROVERSY', self.rows[t]['legal_rules'], t)
        self.assertIn('INTERPRETIVE_CONTROVERSY', self.rows['CF88:ART.142']['legal_rules'])

    def test_parent_child_consistency(self):
        self.assertEqual(self.log['parent_child']['open_findings'], [])
        r = dict(self.corpus['CF88:ART.167'])
        r['content'] = dict(r['content'], atencao='Os incisos III e IV têm explicação própria.')
        fs = SP.parent_child_findings(r, self.ctx, {'CF88:ART.167:INC.IV'})
        self.assertEqual([f['code'] for f in fs], ['PARENT_CHILD_LEGAL_CONSISTENCY'])
        self.assertIn('INC.III', fs[0]['detail'])

    def test_d_only_deep_legal_reasoning(self):
        d = [x for x in self.triage['rows'] if x['queue'] == 'D_FULL_HUMAN_REVIEW']
        self.assertLessEqual(len(d) / len(self.triage['rows']), M.SECOND_PASS_D_LIMIT)
        allowed = {'TRANSITION_OR_TEMPORAL', 'JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS', 'JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS', 'INTERPRETIVE_CONTROVERSY'}
        for x in d:
            self.assertTrue(set(x['legal_rules']) <= allowed, x['target_id'])
        full = (BD / 'MACRO07_FULL_D_REVIEW.md').read_text(encoding='utf-8')
        for k in ('**Motivo HIGH exato:**', '**Afirmação que depende da revisão humana**', '**Lei Seca relevante**', '**Evidência local (versionada)**',
                  '**Evidência externa faltante**', '**Decisão sugerida:'):
            self.assertEqual(full.count(k), len(d), k)

    def test_second_pass_log_complete(self):
        ec = self.log['editorial_corrections']
        self.assertEqual(ec['total'], sum(len(load(f'drafts/MACRO07_{x}_SECOND_PASS_LOG.json')['corrections']) for x in 'ABCD'))
        for c in ec['entries']:
            self.assertTrue(c['reason'] and c['category'] and 'before' in c and 'after' in c)
        pre = {x['target_id']: x for x in load('history/pre_second_pass/MACRO07_TRIAGE_PRE_SECOND_PASS.json')['rows']}
        moved = {m['target_id'] for m in self.log['risk_reclassification']['entries']}
        for t, x in self.rows.items():
            self.assertEqual(t in moved, (pre[t]['queue'], pre[t]['legal_risk'], pre[t]['jurisprudence']) != (x['queue'], x['legal_risk'], x['jurisprudence']), t)
        self.assertEqual(self.log['human_approved_t1_granted'], 0)

    def test_pre_second_pass_history_preserved(self):
        hist = BD / 'history/pre_second_pass'
        for n in ('MACRO07_COMPACT_AB_REVIEW', 'MACRO07_QUICK_C_REVIEW', 'MACRO07_FULL_D_REVIEW', 'MACRO07_HARD_FAIL_REPORT', 'MACRO07_HUMAN_REVIEW_PRIORITY'):
            self.assertTrue((hist / f'{n}_PRE_SECOND_PASS.md').is_file(), n)
        man = load('MACRO07_MANIFEST.json')
        self.assertEqual(sorted(k for k in man['history'] if k.startswith('history/pre_second_pass/')),
                         sorted(str(p.relative_to(BD)) for p in hist.rglob('*') if p.is_file()))
        for p, h in man['history'].items():
            self.assertEqual(sha(BD / p), h, p)


class MacroBatch07HumanRoundD1(unittest.TestCase):
    """Primeira rodada humana do Macro07 (fila D, itens D1-D12): aplicacao fail closed sobre o texto revisado, aprovacao so com portao PASS."""

    @classmethod
    def setUpClass(cls):
        cls.ms = load('MACRO_SPEC.json')
        cls.rnd = M.human_rounds(cls.ms)[0]
        cls.dec = load(cls.rnd['decisions'])
        cls.all = E.load_corpus(BD / 'CF88_MACRO_07.entenda.jsonl')
        cls.act = {r['target_id']: r for r in cls.all if r['status'] == 'ACTIVE'}
        cls.pre = {r['explanation_id']: r for r in E.load_corpus(BD / cls.rnd['pre_review_evidence']['corpus'])}
        cls.triage = load('MACRO07_TRIAGE.json')
        cls.by = {d['target_id']: d for d in cls.dec['decisions']}

    def test_round_scope_counts_and_status(self):
        self.assertEqual(self.dec['review_status'], 'ROUND_REVIEW_COMPLETED')
        self.assertEqual(self.dec['review_scope'], 'CF88_MACRO07_TRIAGE_QUEUE_D_PART1')
        self.assertEqual(len(self.by), 12)
        self.assertEqual(self.dec['decision_counts'], dict(APPROVED=1, APPROVED_AFTER_ADJUSTMENT=11, REJECTED=0))
        pre_rows = {x['target_id']: x for x in load(self.rnd['pre_review_evidence']['triage'])['rows']}
        for t, d in self.by.items():
            self.assertEqual(pre_rows[t]['queue'], 'D_FULL_HUMAN_REVIEW', t)
            self.assertEqual(self.act[t]['review_status'], 'HUMAN_APPROVED_T1', t)
            self.assertEqual(self.act[t]['human_review']['review_scope'], self.dec['review_scope'])
            self.assertEqual(self.act[t]['explanation_id'], d['to_explanation_id'], t)
            self.assertTrue(d['original_content'] and d['review_reason'] and d['flags_resolved'], t)
        self.assertFalse({x['target_id'] for x in self.triage['rows']} & set(self.by))

    def test_versions_retired_and_d11_kept_v1(self):
        retired = [r for r in self.all if r['status'] != 'ACTIVE']
        self.assertEqual(sorted(r['target_id'] for r in retired), sorted(t for t, d in self.by.items() if d['decision'] == 'APPROVED_AFTER_ADJUSTMENT'))
        for r in retired:
            self.assertEqual((r['status'], r['review_status'], r['editorial_version']), ('RETIRED', 'CHANGES_REQUESTED', 1))
            self.assertEqual(r['superseded_by'], self.act[r['target_id']]['explanation_id'])
            self.assertEqual(r['content'], self.pre[r['explanation_id']]['content'])
        d11, old = self.act['CF88:ART.114:PAR.3'], self.pre['ENTENDA/CF88:ART.114:PAR.3/BASE/1']
        self.assertEqual(self.by['CF88:ART.114:PAR.3']['human_decision'], 'APPROVE_WITH_PROVENANCE_ONLY')
        self.assertEqual((d11['editorial_version'], d11['content'], d11['external_layer_notes']), (1, old['content'], old['external_layer_notes']))

    def test_undecided_explanations_unchanged(self):
        n = 0
        for t, r in self.act.items():
            if t in self.by:
                continue
            self.assertEqual(r, self.pre[r['explanation_id']], t)
            n += 1
        self.assertEqual(n, 237)

    def test_provenance_and_case_content_out_of_the_body(self):
        for t in self.by:
            r = self.act[t]
            prov = r['human_review']['content_provenance']
            self.assertTrue(prov, t)
            self.assertTrue(all(p['source_type'] == 'HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE' and p['official_source'].startswith('https://') for p in prov), t)
            body = [r['content'][k] or '' for k in BODY] + [g['explicacao'] for g in r['content']['palavras_dificeis']]
            self.assertFalse([b for b in body if E.EXTERNAL_CASE_RE.search(b)], t)
            self.assertFalse([n for n in r['external_layer_notes'] if 'EXTERNAL_VERIFICATION_REQUIRED' in n and t != 'CF88:ART.114:PAR.3'], t)

    def test_legal_points_of_the_round(self):
        body = lambda t: ' '.join([self.act[t]['content'][k] or '' for k in BODY] + [g['termo'] + ' ' + g['explicacao'] for g in self.act[t]['content']['palavras_dificeis']])  # noqa: E731
        self.assertNotRegex(body('CF88:ART.142'), r'(?i)subsidi')
        self.assertIn('poder moderador', body('CF88:ART.142'))
        self.assertNotIn('objeto de debate', body('CF88:ART.142'))
        d4 = body('CF88:ART.100:PAR.9')
        self.assertIn('não podem ser utilizados como fundamento para uma compensação ou retenção unilateral', d4)
        self.assertNotIn('perde o direito de abater', d4)
        d5 = self.act['CF88:ART.100:PAR.12']['content']['o_que_significa']
        self.assertIn('Fazenda Pública federal', d5)
        self.assertIn('Estados, Distrito Federal e Municípios', d5)
        self.assertIn('Selic', d5)
        self.assertIn('Lei nº 15.484, de 2026', body('CF88:ART.105:PAR.2'))
        self.assertNotRegex(body('CF88:ART.114:PAR.1'), r'(?i)escada|degrau|conquistas')
        self.assertNotIn('tudo o que dela decorre', body('CF88:ART.114'))

    def test_gate_and_totals(self):
        ra = self.triage['round_approvals']
        self.assertEqual([g['gate'] for g in ra['gate']], ['PASS'] * 12)
        self.assertEqual(sum(len(g['hard_fail']) + len(g['review_required_open']) + g['editorial_checks_open'] for g in ra['gate']), 0)
        tot = self.triage['approval_totals']
        prior = {r['explanation_key'] for f in [f"ENTENDA_ENGINE/corpus/{self.ms['norma_id']}.entenda.jsonl"] + self.ms['prior_corpora']
                 for r in E.load_corpus(ROOT / f) if r['status'] == 'ACTIVE' and r['review_status'] == 'HUMAN_APPROVED_T1'}
        self.assertEqual((tot['global_before'], tot['batch_new_approved'], tot['global_after']), (len(prior), 12, len(prior) + 12))
        self.assertEqual(tot['batch_new_pending'], len(self.triage['rows']))
        self.assertEqual(self.triage['counts']['D_FULL_HUMAN_REVIEW'], 12)
        bl = {i['id'] for i in load('BACKLOG_INPUT.json')['items']}
        self.assertTrue({'MB07-12', 'MB07-13'} <= bl)

    def test_round_application_fails_closed(self):
        ms = json.loads(json.dumps(self.ms))
        expl = [e for x in ms['sub_blocks_built'] for e in load(f'drafts/MACRO07_{x}_DRAFTS.json')['explanations']]
        bad = [e for e in expl if e['target_id'] == 'CF88:ART.82'][0]
        bad['content'] = dict(bad['content'], o_que_diz=bad['content']['o_que_diz'] + ' x')
        with self.assertRaises(M.MacroBuildError):
            M.apply_human_rounds(BD, ms, expl)


if __name__ == '__main__':
    unittest.main()
