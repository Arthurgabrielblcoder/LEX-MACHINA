"""REFERENCE_EXPANSION_01 / RUN3: human-approved WORK_REFERENCE overlay, official registry V2, RUN1/RUN2 preserved, fail closed."""
import collections
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import reference_engine as E  # noqa: E402

D = HERE / 'derived'
RUN1, RUN2, RUN3 = D / 'export_test/run1', D / 'export_test/run2', D / 'export_test/run3'
AUD = ROOT / 'REFERENCE_COVERAGE_AUDIT'
REG69 = ROOT / 'LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_CANONICO.json'
REGV2 = ROOT / 'REFERENCE_REGISTRY/WORK_REGISTRY_V2.json'
EXCLUDED = {'JURISPRUDENCE:STF:RG:113:CF88:25:-:-:-@CF88:ART.25', 'JURISPRUDENCE:STF:RG:756:CF88:31:3:-:-@CF88:ART.31:PAR.3'}


def links(run):
    doc = json.loads((run / 'CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))
    return doc, {l['reference_id']: l for ls in doc['references'].values() for l in ls}


def work(ls, tid):
    return sorted(l['label'] for l in ls.values() if l['target_id'] == tid and l['reference_type'] == 'WORK_REFERENCE'
                  and l['visibility'] == 'CURRENT_VISIBLE')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@unittest.skipUnless((RUN3 / 'REF_LOOKUP.IDX').is_file(), 'RUN3 not built')
class Run3ExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d2, cls.l2 = links(RUN2)
        cls.d3, cls.l3 = links(RUN3)
        cls.man = json.loads((RUN3 / 'RUN3_MANIFEST.json').read_text(encoding='utf-8'))
        cls.adds = json.loads((D / 'CF88_WORK_REFERENCE_ADDITIONS.json').read_text(encoding='utf-8'))['records']

    def test_deterministic_byte_identical(self):
        tmp = Path(tempfile.mkdtemp(prefix='cf_run3_'))
        try:
            reg = E.TargetRegistry()
            files = E.export('CF88', E.build_links('CF88', reg), tmp, E.link_exclusions('CF88', reg), E.work_reference_additions('CF88', reg))
            for name in files:
                self.assertEqual((tmp / name).read_bytes(), (RUN3 / name).read_bytes(), name)
        finally:
            shutil.rmtree(tmp)
        self.assertTrue(all(self.man['checks']['byte_identical'].values()))
        for line in (RUN3 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
            h, name = line.split('  ', 1)
            self.assertEqual(sha(RUN3 / name), h, name)

    def test_counts(self):
        c = collections.Counter((l['reference_type'], l['visibility']) for l in self.l3.values())
        self.assertEqual(len(self.l3), 451)
        self.assertEqual(self.d3['total_links'], 451)
        self.assertEqual(c[('JURISPRUDENCE', 'CURRENT_VISIBLE')], 277)
        self.assertEqual(c[('CORRELATA', 'CURRENT_VISIBLE')], 44)
        self.assertEqual(c[('WORK_REFERENCE', 'CURRENT_VISIBLE')], 122)
        self.assertEqual(sum(v for (t, vis), v in c.items() if vis == 'HISTORICAL_HIDDEN_BY_DEFAULT'), 8)
        w = [l for l in self.l3.values() if l['reference_type'] == 'WORK_REFERENCE']
        arts = {':'.join(l['target_id'].split(':')[:2]) for l in w}
        self.assertEqual(len({l['target_id'] for l in w}), 63)
        self.assertEqual(len({a for a in arts if a.startswith('CF88:')}), 33)
        self.assertEqual({a for a in arts if a.startswith('ADCT:')}, {'ADCT:ART.68'})

    def test_run3_is_run2_plus_21_work_links(self):
        new = set(self.l3) - set(self.l2)
        self.assertEqual(set(self.l2) - set(self.l3), set())
        self.assertEqual([k for k in self.l2 if self.l2[k] != self.l3[k]], [])           # no existing link, note or route changed
        self.assertEqual(len(new), 21)
        self.assertTrue(all(self.l3[k]['reference_type'] == 'WORK_REFERENCE' and self.l3[k]['migration'] == 'HUMAN_APPROVED_REFERENCE_V1' for k in new))
        self.assertEqual(new, {f"WORK_REFERENCE:{a['work_id']}@{a['target_id']}" for a in self.adds})
        self.assertEqual(self.d3['total_added_by_overlay'], 21)

    def test_exclusions_never_reintroduced(self):
        self.assertEqual(EXCLUDED & set(self.l3), set())
        self.assertEqual({x['reference_id'] for x in self.d3['excluded_links']}, EXCLUDED)
        for t in ('CF88:ART.25', 'CF88:ART.31:PAR.3'):
            self.assertEqual(E.lookup_idx(t, RUN3 / 'REF_LOOKUP.IDX', RUN3 / 'REF_PAYLOAD.IDX'), [])

    def test_run1_run2_preserved(self):
        for run in ('run1', 'run2'):
            prev = self.man['previous_runs'][run]
            self.assertTrue(prev['preserved'])
            for name, h in prev['files'].items():
                self.assertEqual(sha(D / 'export_test' / run / name), h, (run, name))
        self.assertEqual(self.d2['total_links'], 430)
        self.assertNotIn('total_added_by_overlay', self.d2)

    def test_targets_valid_21_of_21(self):
        tv = self.man['target_validation']
        self.assertEqual(len(tv), 21)
        self.assertTrue(all(t['valid'] and t['in_runtime'] and t['device_legal_status'] == 'CURRENT' and not t['filtered'] for t in tv))
        self.assertEqual(self.man['checks']['additions_valid_targets'], '21/21')
        reg = E.TargetRegistry().load('CF88')
        for a in self.adds:
            self.assertTrue(reg.target_exists_for_norm('CF88', a['target_id']), a['target_id'])
            self.assertIn(reg.status('CF88', a['target_id']), ('CURRENT', 'STRUCTURAL'))

    def test_expected_works_per_target(self):
        self.assertEqual(work(self.l3, 'CF88:ART.37:CAPUT'), ['Os Donos do Poder', 'Raízes do Brasil'])
        self.assertEqual(work(self.l3, 'CF88:ART.43:CAPUT'), ['Formação Econômica do Brasil'])
        self.assertEqual(work(self.l3, 'CF88:ART.43:PAR.2:INC.IV'), ['Vidas Secas'])
        self.assertEqual(work(self.l3, 'CF88:ART.62:CAPUT'), ['Suzerain'])
        self.assertEqual(work(self.l3, 'CF88:ART.201:INC.I'), ['Eu, Daniel Blake'])
        self.assertEqual(work(self.l3, 'ADCT:ART.68'), ['Torto Arado'])
        self.assertEqual(work(self.l3, 'CF88:ART.7:INC.XXXIII'), ['Frostpunk'])
        self.assertEqual(work(self.l3, 'CF88:ART.193:CAPUT'), ['Capital no Século XXI', 'Desigualdade para Todos', 'O Triunfo da Injustiça'])
        for t in ('CF88:ART.76', 'CF88:ART.142', 'CF88:ART.142:CAPUT', 'CF88:ART.196', 'CF88:ART.206:INC.I'):
            self.assertEqual(work(self.l3, t), [], t)
        labels = {l['label'] for l in self.l3.values()}
        self.assertNotIn('Borgen', labels)
        self.assertNotIn('Argentina, 1985', labels)
        for art in ('CF88:ART.98', 'CF88:ART.202'):                                   # CONFIRMED_REFERENCE_GAP
            self.assertEqual([l for l in self.l3.values() if l['reference_type'] == 'WORK_REFERENCE'
                              and (l['target_id'] == art or l['target_id'].startswith(art + ':'))], [], art)

    def test_scores_and_rich_payload(self):
        by = {(a['target_id'], a['work_id']): a for a in self.adds}
        self.assertEqual(by[('CF88:ART.62:CAPUT', 'EXP-JOG-002')]['score_editorial'], 7.4)
        self.assertEqual(by[('ADCT:ART.68', 'EXP-LIV-005')]['score_editorial'], 9.2)
        self.assertEqual(by[('CF88:ART.7:INC.XXXIII', 'EXP-JOG-003')]['score_editorial'], 7.8)
        suz = by[('CF88:ART.62:CAPUT', 'EXP-JOG-002')]
        self.assertEqual(suz['confidence'], 'HIGH_AFTER_EXTERNAL_VERIFICATION')
        self.assertNotIn('medida provisória brasileira', (suz['por_que_esta_aqui'] + suz['alcance_neste_dispositivo']).lower())
        fro = by[('CF88:ART.7:INC.XXXIII', 'EXP-JOG-003')]
        self.assertTrue(fro['limites'].startswith('Mundo fictício. A mecânica ajuda a problematizar o trabalho infantil'))
        self.assertNotIn('confirmad', json.dumps({k: fro[k] for k in ('limites', 'alcance_neste_dispositivo', 'por_que_esta_aqui')}, ensure_ascii=False))
        ta = by[('ADCT:ART.68', 'EXP-LIV-005')]
        self.assertEqual(ta['external_editorial_support']['kind'], 'EXTERNAL_EDITORIAL_SUPPORT')
        for a in self.adds:
            self.assertEqual((a['review_status'], a['approval_method'], a['reviewer_decision']),
                             ('HUMAN_APPROVED_REFERENCE_V1', 'ASSISTED_RISK_BASED_HUMAN_REVIEW', 'ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW'))
            l = self.l3[f"WORK_REFERENCE:{a['work_id']}@{a['target_id']}"]
            for f in ('sobre', 'por_que_esta_aqui', 'alcance_neste_dispositivo', 'score_editorial'):
                self.assertTrue(l['payload'][f], (a['addition_id'], f))
            self.assertNotIn('AUTO_APPROVED', json.dumps(a))


class OverlayFailClosedTest(unittest.TestCase):
    def _build(self, mutate):
        tmp = Path(tempfile.mkdtemp(prefix='cf_add_'))
        try:
            doc = json.loads((D / 'CF88_WORK_REFERENCE_ADDITIONS.json').read_text(encoding='utf-8'))
            mutate(doc['records'])
            (tmp / 'a.json').write_text(json.dumps(doc), encoding='utf-8')
            reg = E.TargetRegistry()
            reg.cfg['norms']['CF88']['work_reference_additions'] = str(tmp / 'a.json')
            with self.assertRaises(E.EngineError) as cm:
                E.build_links('CF88', reg)
            return cm.exception.code
        finally:
            shutil.rmtree(tmp)

    def test_rejections(self):
        def set0(**kw):
            return lambda r: r[0].update(kw)
        self.assertEqual(self._build(set0(target_id='CF88:ART.999')), 'LINK_TARGET_NOT_IN_NORM')
        self.assertEqual(self._build(set0(target_id='CF88:ART.40:PAR.4:INC.II')), 'ADDITION_TARGET_NOT_CURRENT')   # HISTORICAL_ONLY target
        self.assertEqual(self._build(set0(work_id='EXP-XXX-999')), 'ADDITION_WORK_NOT_IN_REGISTRY')
        self.assertEqual(self._build(set0(review_status='AUTO_APPROVED')), 'ADDITION_NOT_APPROVED')
        self.assertEqual(self._build(set0(sobre='')), 'ADDITION_MISSING_FIELD')
        self.assertEqual(self._build(set0(target_id='CF88:ART.193:CAPUT', work_id='EXP-LIV-009', obra='O Triunfo da Injustiça', tipo='LIVRO')),
                         'ADDITION_DUPLICATES_EXISTING_LINK')
        self.assertEqual(self._build(lambda r: r.append(dict(r[0]))), 'ADDITION_DUPLICATE')

    def test_engine_still_norm_agnostic(self):
        src = (HERE / 'reference_engine.py').read_text(encoding='utf-8').split('def main')[0]
        self.assertNotIn("'CF88'", src)
        self.assertNotIn('"CF88"', src)


class RegistryAndDecisionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = json.loads(REGV2.read_text(encoding='utf-8'))
        cls.r69 = json.loads(REG69.read_text(encoding='utf-8'))
        cls.dec = json.loads((AUD / 'REFERENCE_EXPANSION_ROUND1_DECISIONS.json').read_text(encoding='utf-8'))

    def test_protected_registry_untouched(self):
        blob = subprocess.run(['git', 'rev-parse', f'HEAD:{REG69.relative_to(ROOT).as_posix()}'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        here = subprocess.run(['git', 'hash-object', str(REG69)], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        self.assertEqual(blob, here)
        self.assertEqual(self.reg['base']['sha256'], sha(REG69))

    def test_registry_v2_69_plus_promoted(self):
        self.assertEqual((self.reg['total_before'], self.reg['total'], len(self.reg['obras'])), (69, 73, 73))
        self.assertEqual(self.reg['obras'][:69], self.r69['obras'])
        self.assertEqual(self.reg['promoted'], ['EXP2-LIV-040', 'EXP2-FIL-039', 'EXP2-FIL-006', 'EXP2-FIL-038'])
        ids = [o['id'] for o in self.reg['obras']]
        self.assertEqual(len(ids), len(set(ids)))
        titles = {o['titulo'] for o in self.reg['obras']}
        for t in ('Vidas Secas', 'Tropa de Elite 2: O Inimigo Agora É Outro', 'Luta por Justiça', 'Tropa de Elite'):
            self.assertIn(t, titles)
        for t in ('SOS Saúde (Sicko)', 'Sicko', 'Pro Dia Nascer Feliz'):
            self.assertNotIn(t, titles)
        for o in self.reg['obras'][69:]:
            self.assertEqual((o['provenance']['status'], o['provenance']['editorial_approval']),
                             ('PROMOTED_FROM_EXPANSION_CATALOG', 'ARTHUR_AUTHORIZED_CHATGPT_REVIEW'))
            self.assertEqual(o['provenance']['candidate_id'], o['registro_origem_integral']['candidate_id'])
            self.assertEqual(o['id'], o['registro_origem_integral']['work_id'])
        jm = next(o for o in self.reg['obras'] if o['id'] == 'EXP2-FIL-006')
        self.assertEqual((jm['titulo'], jm['titulo_original']), ('Luta por Justiça', 'Just Mercy'))

    def test_decisions(self):
        d = self.dec
        self.assertEqual((d['counts']['proposals'], d['counts']['APPROVE'], d['counts']['ADJUST_APPROVE'], d['counts']['REJECT']), (25, 20, 3, 2))
        self.assertEqual((d['counts']['integrated_run3'], d['counts']['held_pending_work_identity']), (21, 2))
        by = {x['obra']: x for x in d['decisions']}
        self.assertEqual({k: by[k]['final']['score'] for k in ('Suzerain', 'Torto Arado', 'Frostpunk')}, {'Suzerain': 7.4, 'Torto Arado': 9.2, 'Frostpunk': 7.8})
        self.assertEqual({k: by[k]['original_proposal']['score_proposto'] for k in ('Suzerain', 'Torto Arado', 'Frostpunk')},
                         {'Suzerain': 6.8, 'Torto Arado': 8.4, 'Frostpunk': 7.2})
        for k in ('Borgen', 'Argentina, 1985'):
            self.assertEqual((by[k]['decision'], by[k]['final_status']), ('REJECT', 'REJECTED_EDITORIAL_WEAK_CONNECTION'))
        for k in ('SOS Saúde (Sicko)', 'Pro Dia Nascer Feliz'):
            self.assertEqual((by[k]['decision'], by[k]['integration'], by[k]['work_id']), ('APPROVE', 'APPROVED_PENDING_WORK_IDENTITY', None))
        self.assertEqual({g['target_id'] for g in d['confirmed_reference_gaps']}, {'CF88:ART.98', 'CF88:ART.202'})

    def test_review_marked_and_history_kept(self):
        md = (AUD / 'REFERENCE_EXPANSION_REVIEW.md').read_text(encoding='utf-8')
        self.assertNotIn('- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR', md)
        self.assertEqual(md.count('- [x] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR'), 20)
        self.assertEqual(md.count('- [x] APROVAR   - [x] AJUSTAR   - [ ] REJEITAR'), 3)
        self.assertEqual(md.count('- [ ] APROVAR   - [ ] AJUSTAR   - [x] REJEITAR'), 2)
        self.assertEqual(md.count('**SCORE PROPOSTO:**'), 25)                                  # original proposal text kept
        for s in ('SCORE FINAL: **7.4** (proposto: 6.8)', 'SCORE FINAL: **9.2** (proposto: 8.4)', 'SCORE FINAL: **7.8** (proposto: 7.2)'):
            self.assertIn(s, md)


if __name__ == '__main__':
    unittest.main()
