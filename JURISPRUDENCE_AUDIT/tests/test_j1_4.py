"""J1.4 — ratified J1.3 decisions materialized host-only (RUN7): 4 links removed from wrong targets, 3 relocated, frozen layers intact."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_export_run7_juris_j1_4 as R7  # noqa: E402

BASE = ROOT / 'JURISPRUDENCE_AUDIT/J1_1_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1'
REMOVED = {'JURISPRUDENCE:STF:SV:17:CF88:100:-:-:-@CF88:ART.100:PAR.1', 'JURISPRUDENCE:STF:RG:147:CF88:100:-:-:-@CF88:ART.100:PAR.1',
           'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40:PAR.4', 'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40:PAR.5'}
ADDED = {'JURISPRUDENCE:STF:SV:17:CF88:100:-:-:-@CF88:ART.100:PAR.5', 'JURISPRUDENCE:STF:RG:147:CF88:100:-:-:-@CF88:ART.100:PAR.5',
         'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    return [l.split('|') for l in Path(p).read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')]


class J14(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = R7.OUT / 'device_ready'
        cls.pb, cls.pc = rows(BASE / '20_REFERENCES/REF_PAYLOAD.IDX'), rows(cls.dev / 'REF_PAYLOAD.IDX')

    def test_generators_up_to_date(self):
        for s in (AUD / 'apply_j1_4_overlays.py', AUD / 'build_j1_4_isolation_audit.py', AUD / 'build_j1_3_external_review.py'):
            r = subprocess.run([sys.executable, '-I', '-B', str(s), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), s.name)

    def test_run7_reproducible(self):
        with tempfile.TemporaryDirectory() as t:
            R7.build(t)
            for line in (R7.OUT / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
                h, name = line.split('  ', 1)
                self.assertEqual(sha(Path(t) / name), h, name)
                self.assertEqual(sha(R7.OUT / name), h, name)

    def test_exact_delta(self):
        b, c = {tuple(r) for r in self.pb}, {tuple(r) for r in self.pc}
        self.assertEqual({r[4] for r in b - c}, REMOVED)
        self.assertEqual({r[4] for r in c - b}, ADDED)
        self.assertTrue(all(r[1] == 'JURISPRUDENCE' for r in (b - c) | (c - b)))
        v = [r for r in self.pc if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
        self.assertEqual((len(v), len({r[0] for r in v})), (256, 156))
        self.assertEqual({r[5] for r in self.pc if r[0] == 'CF88:ART.16' and r[1] == 'JURISPRUDENCE'}, {'STF:RG:367', 'STF:RG:387'})   # KEEP_BOTH

    def test_temporal_note_and_same_key(self):
        exp = json.loads((self.dev / 'CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))
        links = {l['reference_id']: l for ls in exp['references'].values() for l in ls}
        for rid in ADDED:
            l = links[rid]
            self.assertEqual(l['migration'], 'RELOCATED_J1_4')
            self.assertTrue(l['payload']['nota_temporal'] and l['provenance']['relocation']['temporal_note'])
            self.assertEqual(rid.split(':', 1)[1].rsplit('@', 1)[0], l['source_reference_id'])
        self.assertIn('redação originária', links['JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40']['payload']['nota_temporal'])

    def test_flags_and_isolation(self):
        tb, tc = {r[0]: r for r in rows(BASE / '10_TARGETS/CF88_TARGETS.IDX')}, {r[0]: r for r in rows(self.dev / 'CF88_TARGETS.IDX')}
        self.assertEqual({t for t in tb if tb[t] != tc[t]}, {'CF88:ART.100:PAR.1'})
        self.assertEqual((tb['CF88:ART.100:PAR.1'][3], tc['CF88:ART.100:PAR.1'][3]), ('E-J-RX', 'E---RX'))
        v = json.loads((AUD / 'J1_4_ISOLATION_AUDIT.json').read_text(encoding='utf-8'))['verdict']
        for k in ('CORRELATA_RELATION_SET_CHANGED', 'WORK_REFERENCE_SET_CHANGED', 'C_FLAGS_CHANGED', 'E_FLAGS_CHANGED', 'W_FLAGS_CHANGED',
                  'R_FLAGS_CHANGED', 'X_FLAGS_CHANGED', 'NON_J_TARGET_FLAGS_CHANGED'):
            self.assertEqual(v[k], 0, k)
        for k in ('JURIS_REMOVED_EQUALS_RATIFIED_4', 'JURIS_ADDED_EQUALS_RELOCATIONS_3', 'RELOCATED_KEYS_IN_LEGACY_IDX', 'J_FLAG_EQUALS_VISIBLE_JURIS',
                  'CORRELATA_FILES_BYTE_IDENTICAL', 'HISTORICAL_HIDDEN_JURIS_UNCHANGED'):
            self.assertTrue(v[k], k)


SD = ROOT / 'DEVICE_INTEGRATION/staging_sd_v1_juris_j1_4_candidate/SD'
PKG = AUD / 'J1_4_CANDIDATE_HOST_ONLY'


class Package(unittest.TestCase):
    def test_package_manifest_and_rollback(self):
        m = json.loads((PKG / 'J1_4_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual((m['status'], m['card_touched'], m['device_flashed']), ('HOST_ONLY_CANDIDATE', False, False))
        self.assertTrue(m['physical_baseline_reproduced'] and m['byte_identical_rebuild'] and m['device_manifest_matches_package'])
        self.assertEqual(len(m['changed_vs_physical']), 5)
        self.assertEqual(len(m['targets_r_only_divergence_vs_generator']), 38)
        card = {k: v['sha256'] for k, v in json.loads((AUD / 'J1_2_PHYSICAL_DEPLOY/sd_manifest_post_full.json')
                                                      .read_text(encoding='utf-8'))['entries'].items()}
        for d in m['file_diff']:
            rel = d['path'].lstrip('/')
            self.assertEqual(sha(PKG / 'rollback/SD' / rel), card[rel], rel)
            self.assertEqual(sha(PKG / 'candidate/SD' / rel), d['after_sha256'], rel)
        for n in ('CF88_TARGETS.IDX', 'REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
            sub = '10_TARGETS' if n.startswith('CF88') else '20_REFERENCES'
            if n != 'CF88_TARGETS.IDX':
                self.assertEqual(sha(PKG / 'candidate/SD/99_LEX_V1' / sub / n), sha(R7.OUT / 'device_ready' / n), n)


@unittest.skipUnless((SD / '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX').is_file(), 'J1.4 staging not built')
class DeviceSimulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'DEVICE_INTEGRATION/tools'))
        import canonical_layer_audit as A
        import device_lookup_simulator as S
        cls.A, cls.S = A, S
        cls.dev = S.Device(SD / '99_LEX_V1')
        cls.flags = {p[0]: p[3] for p in A.rows(SD / '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX')}

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def juris(self, tid):
        return sorted(r[5] for r in self.A.device_query_union(self.dev, tid)[0].get(self.A.JURIS, []))

    def available(self, tid, layer):
        return any(self.A.flag(self.flags.get(k, '------'), layer) for k in self.A.query_keys(tid))

    def test_wrong_targets_cleared(self):
        self.assertEqual(self.juris('CF88:ART.100:PAR.1'), [])
        self.assertFalse(self.available('CF88:ART.100:PAR.1', self.A.JURIS))
        for tid in ('CF88:ART.40:PAR.4', 'CF88:ART.40:PAR.5'):
            self.assertNotIn('STF:RG:594', self.juris(tid), tid)
            self.assertTrue(self.available(tid, self.A.JURIS), tid)   # Temas 727/888/942/965 remain

    def test_relocated(self):
        self.assertTrue({'STF:SV:17', 'STF:RG:147', 'STF:RG:1037', 'STF:RG:1335'} <= set(self.juris('CF88:ART.100:PAR.5')))
        self.assertIn('STF:RG:594', self.juris('CF88:ART.40'))
        self.assertTrue(self.available('CF88:ART.100:PAR.5', self.A.JURIS) and self.available('CF88:ART.40', self.A.JURIS))

    def test_kept_links(self):
        self.assertTrue({'STF:RG:367', 'STF:RG:387'} <= set(self.juris('CF88:ART.16')))
        self.assertIn('STF:RG:295', self.juris('CF88:ART.6'))
        self.assertEqual(self.juris('CF88:ART.1'), [])
        self.assertEqual(len(self.juris('CF88:ART.37:INC.XI')), 10)

    def test_frozen_layers_on_device(self):
        A = self.A
        rows_ = A.device_query_union(self.dev, 'CF88:ART.202:PAR.5')[0].get(A.CORRELATA, [])
        self.assertEqual([r[5] for r in rows_], ['EXT_LC108_2001'])
        works = lambda t: sorted(r[6] for r in A.device_query_union(self.dev, t)[0].get(A.REFERENCIA, []))  # noqa: E731
        self.assertEqual(works('CF88:ART.196'), ['Sicko - S.O.S. Saúde'])
        self.assertEqual(works('CF88:ART.43'), ['Formação Econômica do Brasil'])


if __name__ == '__main__':
    unittest.main()
