"""REFERÊNCIAS Nº 4 R1/R1A: identity of the two held works, registry V3, overlay R1 and the RUN5 candidate (host-only).

The RUN3/RUN4 artifacts and their tests stay as they are (RUN3 = 122 links, registry V2 = 73 works): R1 never edits them.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import reference_engine as E  # noqa: E402
import build_export_run5_references4_r1 as R5  # noqa: E402

AUD = ROOT / 'REFERENCE_COVERAGE_AUDIT'
IDENT = AUD / 'R1A_WORK_IDENTITY'
V2 = ROOT / 'REFERENCE_REGISTRY/WORK_REGISTRY_V2.json'
V3 = ROOT / 'REFERENCE_REGISTRY/WORK_REGISTRY_V3.json'
ADDS = HERE / 'derived/CF88_WORK_REFERENCE_ADDITIONS_R1.json'
DECISIONS = AUD / 'REFERENCE_EXPANSION_ROUND1_DECISIONS.json'
C3B2 = ROOT / 'CORRELATA_COVERAGE_AUDIT/C3B2_PHYSICAL_TEST_PACKAGE/candidate/SD/99_LEX_V1'
NEW = {'WORK_REFERENCE:R1A-DOC-001@CF88:ART.196': ('R1A-DOC-001', 'Sicko - S.O.S. Saúde', 'STRUCTURAL'),        # article line, like ART.192
       'WORK_REFERENCE:R1A-DOC-002@CF88:ART.206:INC.I': ('R1A-DOC-002', 'Pro Dia Nascer Feliz', 'CURRENT')}


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_lf(p):                                       # committed (LF) form of a text file (checkout may use autocrlf)
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def run(*args):
    return subprocess.run([sys.executable, '-I', '-B', *map(str, args)], capture_output=True, text=True, cwd=ROOT)


def payload_rows(p):
    return [l.split('|') for l in Path(p).read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]


class R1AIdentityTest(unittest.TestCase):
    def test_generators_up_to_date(self):
        for script in (IDENT / 'build_r1a_identity.py', AUD / 'apply_references4_r1.py', AUD / 'build_references4_r1_isolation_audit.py'):
            r = run(script, '--check')
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), script.name)

    def test_identity_backed_by_consulted_sources(self):
        cat = load(IDENT / 'R1A_WORK_IDENTITY_CATALOG.json')
        self.assertEqual([o['work_id'] for o in cat['obras']], ['R1A-DOC-001', 'R1A-DOC-002'])
        for o in cat['obras']:
            self.assertTrue(o['criadores'] and o['resumo_factual_curto'] and o['titulo_original'], o['work_id'])
            ident = [f for f in o['fontes'] if 'identidade' in f['supports']]
            self.assertTrue(ident, o['work_id'])
            for f in o['fontes']:
                rec = load(ROOT / f['collection_record'])
                self.assertEqual((rec['url'], rec['verificacao'], rec['snapshot_sha256']), (f['url'], 'PAGINA_CONSULTADA', f['snapshot_sha256']))
                self.assertNotIn('texto', rec)                                       # metadata only, no third-party text
        sicko, pro = cat['obras']
        self.assertEqual((sicko['titulo'], sicko['titulo_original'], sicko['ano'], sicko['criadores']),
                         ('Sicko - S.O.S. Saúde', 'Sicko', 2007, ['Michael Moore']))
        self.assertEqual((pro['titulo'], pro['ano'], pro['criadores']), ('Pro Dia Nascer Feliz', 2005, ['João Jardim']))
        self.assertEqual(pro['ano_decisao']['value'], 2005)                           # user decision; divergences recorded
        self.assertEqual({d['value'] for d in pro['ano_decisao']['divergences']}, {2006, 2007})


class R1RegistryAndOverlayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v2, cls.v3, cls.adds = load(V2), load(V3), load(ADDS)

    def test_registry_v3_is_v2_plus_two(self):
        self.assertEqual((self.v3['total_before'], self.v3['total'], len(self.v3['obras'])), (73, 75, 75))
        self.assertEqual(self.v3['obras'][:73], self.v2['obras'])                    # V2 records unchanged
        self.assertEqual(self.v3['promoted'], ['R1A-DOC-001', 'R1A-DOC-002'])
        self.assertEqual(self.v3['supersedes']['sha256'], sha_lf(V2))
        ids = [o['id'] for o in self.v3['obras']]
        self.assertEqual(len(ids), len(set(ids)))
        for log in self.v3['promotion_log']:
            self.assertTrue(all(log['checks'].values()), log['work_id'])
            self.assertEqual(log['duplicates_in_registry'], [])

    def test_new_works_do_not_duplicate_registry_titles(self):
        import apply_reference_expansion_round1 as R1E
        old = {R1E.norm(x) for o in self.v2['obras'] for x in (o['titulo'], o.get('titulo_original'), *(o.get('aliases') or [])) if x}
        for o in self.v3['obras'][73:]:
            names = {R1E.norm(x) for x in (o['titulo'], o['titulo_original'], *o['aliases'])}
            self.assertFalse(names & old, o['id'])

    def test_overlay_is_exactly_the_two_held_approvals(self):
        dec = {d['decision_id']: d for d in load(DECISIONS)['decisions']}
        recs = self.adds['records']
        self.assertEqual([r['decision_id'] for r in recs], ['REFERENCE_EXPANSION_01-P20', 'REFERENCE_EXPANSION_01-P21'])
        for r in recs:
            d = dec[r['decision_id']]
            self.assertEqual((d['decision'], d['final_status'], d['integration']), ('APPROVE', 'HUMAN_APPROVED_REFERENCE_V1', 'APPROVED_PENDING_WORK_IDENTITY'))
            self.assertEqual(r['target_id'], d['target_id'])
            for k in ('conexao_juridica', 'por_que_esta_aqui', 'alcance_neste_dispositivo', 'limites', 'confidence'):
                self.assertEqual(r[k], d['final'][k], k)                                # approved text transported, not rewritten
            self.assertEqual(r['score_editorial'], d['final']['score'])
        self.assertEqual(self.adds['work_registry_sha256'], sha_lf(V3))

    def test_engine_fail_closed_without_registry_v3(self):
        reg = E.TargetRegistry()
        clone = R5.r1_registry(reg)
        clone.cfg['norms']['CF88']['work_registry'] = '../REFERENCE_REGISTRY/WORK_REGISTRY_V2.json'
        with self.assertRaises(E.EngineError) as cm:
            E.work_reference_additions('CF88', clone)
        self.assertTrue(str(cm.exception).startswith('ADDITION_WORK_NOT_IN_REGISTRY'), str(cm.exception))


class Run5CandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = R5.OUT / 'device_ready'
        cls.summary = load(R5.OUT / 'RUN5_SUMMARY.json')

    def test_reproducible_byte_identical(self):
        with tempfile.TemporaryDirectory() as t:
            R5.build(t)
            for line in (R5.OUT / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
                h, name = line.split('  ', 1)
                self.assertEqual(sha(Path(t) / name), h, name)
                self.assertEqual(sha(R5.OUT / name), h, name)

    def test_base_is_c3b2_and_untouched(self):
        for name, rel in R5.C3B2_MAP.items():
            self.assertEqual((R5.RUN4_DEV / name).read_bytes(), (R5.C3B2 / rel).read_bytes(), name)
        for name in R5.COPIED:                                                        # CORRELATA files: byte copies
            self.assertEqual((self.dev / name).read_bytes(), (R5.RUN4_DEV / name).read_bytes(), name)

    def test_counts(self):
        w = self.summary['work_reference']
        self.assertEqual((w['relations_before'], w['relations_after']), (122, 124))
        self.assertEqual((w['works_used_before'], w['works_used_after']), (54, 56))
        self.assertEqual((w['w_targets_before'], w['w_targets_after']), (63, 65))
        lt = self.summary['links_by_type']
        for k in ('CORRELATA|CURRENT_VISIBLE', 'CORRELATA|HISTORICAL_HIDDEN_BY_DEFAULT', 'JURISPRUDENCE|CURRENT_VISIBLE',
                  'JURISPRUDENCE|HISTORICAL_HIDDEN_BY_DEFAULT'):
            self.assertEqual(lt['run4'][k], lt['run5'][k], k)

    def test_two_new_links_and_old_set_preserved(self):
        old = {tuple(r) for r in payload_rows(R5.RUN4_DEV / 'REF_PAYLOAD.IDX')}
        new = {tuple(r) for r in payload_rows(self.dev / 'REF_PAYLOAD.IDX')}
        self.assertTrue(old <= new)                                                   # nothing removed or changed
        added = new - old
        self.assertEqual({r[4] for r in added}, set(NEW))
        for r in added:
            wid, label, status = NEW[r[4]]
            self.assertEqual((r[1], r[2], r[3], r[5], r[6]), ('WORK_REFERENCE', 'CURRENT_VISIBLE', status, wid, label))
        exp = load(self.dev / 'CF88_REFERENCES_EXPORT.json')
        self.assertEqual(exp['total_added_by_overlay'], 23)
        link = {l['reference_id']: l for ls in exp['references'].values() for l in ls}
        self.assertEqual(link['WORK_REFERENCE:R1A-DOC-001@CF88:ART.196']['payload']['ano'], 2007)
        self.assertEqual(link['WORK_REFERENCE:R1A-DOC-002@CF88:ART.206:INC.I']['payload']['score_editorial'], 8.0)

    def test_lookup_resolves_new_targets(self):
        for ref_id, (wid, label, _) in NEW.items():
            tid = ref_id.split('@', 1)[1]
            rows = E.lookup_idx(tid, self.dev / 'REF_LOOKUP.IDX', self.dev / 'REF_PAYLOAD.IDX')
            self.assertEqual([(r[0], r[1], r[5], r[6]) for r in rows], [(tid, 'WORK_REFERENCE', wid, label)], tid)

    def test_targets_only_w_on_the_two_new_targets(self):
        b = {r[0]: r for r in payload_rows(C3B2 / '10_TARGETS/CF88_TARGETS.IDX')}
        c = {r[0]: r for r in payload_rows(self.dev / 'CF88_TARGETS.IDX')}
        self.assertEqual(set(b), set(c))
        diff = {t: (b[t][3], c[t][3]) for t in b if b[t] != c[t]}
        self.assertEqual(diff, {'CF88:ART.196': ('E----X', 'E--W-X'), 'CF88:ART.206:INC.I': ('------', '---W--')})
        for t in ('CF88:ART.206', 'CF88:ART.206:CAPUT', 'CF88:ART.206:INC.II', 'CF88:ART.196:CAPUT'):
            self.assertEqual(c[t][3][3], '-', t)                                      # no inheritance

    def test_isolation_verdict(self):
        v = load(AUD / 'REFERENCES_4_R1_ISOLATION_AUDIT.json')['verdict']
        for k in ('CORRELATA_RELATION_SET_CHANGED', 'CORRELATA_REFERENCE_IDS_CHANGED', 'CORRELATA_ROUTES_CHANGED', 'CORRELATA_DESTINATIONS_CHANGED',
                  'C_FLAGS_CHANGED', 'E_FLAGS_CHANGED', 'J_FLAGS_CHANGED', 'R_FLAGS_CHANGED', 'X_FLAGS_CHANGED', 'NON_W_TARGET_FLAGS_CHANGED'):
            self.assertEqual(v[k], 0, k)
        self.assertEqual(v['W_FLAGS_CHANGED'], 'DERIVED_ONLY_FROM_NEW_APPROVED_WORK_REFERENCES')
        self.assertEqual(v['OLD_WORK_REFERENCE_SET_PRESERVED'], 'PASS')
        self.assertEqual(v['FIRMWARE_LIMITS'], 'PASS')
        self.assertTrue(v['JURISPRUDENCE_UNCHANGED'] and v['CORRELATA_FILES_BYTE_IDENTICAL'])


sys.path.insert(0, str(AUD))

if __name__ == '__main__':
    unittest.main()
