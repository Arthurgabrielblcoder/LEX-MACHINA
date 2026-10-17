"""J2B.1 — J2B_PREDEPLOY_TEMPORAL_FIX (Tema 558: CF art. 100, § 9º -> CF art. 100), Batch01 preserved, package J2B.1 supersedes J2B."""
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
sys.path.insert(0, str(AUD))
import build_export_run9_juris_j2b_1 as R9  # noqa: E402
import build_j2b_isolation_audit as A  # noqa: E402

PKG = AUD / 'J2B_1_CANDIDATE_HOST_ONLY'
CARD = AUD / 'J1_5_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
OLD = 'JURISPRUDENCE:STF:RG:558:CF88:100:-:-:-@CF88:ART.100:PAR.9'
NEW = 'JURISPRUDENCE:STF:RG:558:CF88:100:-:-:-@CF88:ART.100'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class J2B1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = {k: v['sha256'] for k, v in json.loads(CARD.read_text(encoding='utf-8'))['entries'].items()}
        cls.m = json.loads((PKG / 'J2B_1_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
        cls.payload = A.rows((PKG / 'candidate/SD/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX').read_bytes())
        cls.idx = (PKG / 'candidate/SD' / A.IDX).read_bytes()
        cls.new_files = {a['path'].lstrip('/') for a in cls.m['file_additions']}
        cls.v = json.loads((AUD / 'J2B_1_ISOLATION_AUDIT.json').read_text(encoding='utf-8'))['verdict']

    def sources(self, tid):
        return [x['source'] for x in A.resolve(tid, self.payload, self.idx, self.card, self.new_files)]

    def test_1_tema558_not_on_current_par9(self):
        self.assertNotIn('STF:RG:558', self.sources('CF88:ART.100:PAR.9'))
        self.assertNotIn(OLD, {r[4] for r in self.payload})

    def test_2_tema558_on_art100_with_temporal_note(self):
        self.assertIn('STF:RG:558', self.sources('CF88:ART.100'))
        exp = json.loads((R9.OUT / 'device_ready/CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))
        link = {l['reference_id']: l for ls in exp['references'].values() for l in ls}[NEW]
        self.assertEqual(link['migration'], 'RELOCATED_J2B_1')
        self.assertEqual(link['payload']['versao_temporal'], 'EC 62/2009')
        self.assertIn('EC 113/2021', link['payload']['nota_temporal'])
        self.assertEqual(link['provenance']['relocation']['temporal_version'], 'EC 62/2009')

    def test_3_tema558_ficha_still_opens(self):
        x = [x for x in A.resolve('CF88:ART.100', self.payload, self.idx, self.card, self.new_files) if x['source'] == 'STF:RG:558'][0]
        self.assertTrue(x['resolved'] and x['ficha_present'])
        self.assertEqual(x['ficha'], '99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_558.TXT')
        self.assertNotIn(x['ficha'], self.m['changed_vs_physical'] + self.m['added_vs_physical'])     # card ficha byte for byte
        self.assertEqual(x['list_label'], 'RG TEMA 558')

    def test_4_5_6_batch01_preserved(self):
        self.assertEqual(self.sources('CF88:ART.100:PAR.9'), ['STF:ADI:7047-7064'])
        self.assertEqual(self.sources('CF88:ART.100:PAR.12'), ['STF:ADI:4425'])
        for t in ('CF88:ART.166:PAR.9', 'CF88:ART.166:PAR.11', 'CF88:ART.166-A'):
            self.assertEqual(self.sources(t), ['STF:ADI:7697'], t)
        r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'apply_j2b_adi_overlay.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.stdout.strip(), 'UP_TO_DATE')                                            # ADI model, aliases and revalidation registry
        self.assertTrue(self.v['ADI_BATCH01_ROWS_PRESERVED'] and self.v['LEGACY_FILES_SAME_AS_J2B'])

    def test_7_historical_256_intact_except_authorized(self):
        self.assertTrue(self.v['HISTORICAL_256_INTACT_EXCEPT_AUTHORIZED'])
        self.assertEqual((self.v['OLD_LINK_REMOVED'], self.v['TEMPORAL_REALLOCATION_ADDED']), (1, 1))
        self.assertEqual(self.sources('CF88:ART.100:PAR.10'), ['STF:RG:558'])                     # § 10 out of scope, untouched

    def test_8_frozen_layers(self):
        for k in ('CORRELATA_RELATION_SET_CHANGED', 'WORK_REFERENCE_SET_CHANGED', 'J_FLAG_CHANGES_VS_J2B', 'C_FLAG_CHANGES_VS_J2B',
                  'E_FLAG_CHANGES_VS_J2B', 'W_FLAG_CHANGES_VS_J2B', 'R_FLAG_CHANGES_VS_J2B', 'X_FLAG_CHANGES_VS_J2B'):
            self.assertEqual(self.v[k], 0, k)
        for k in ('CORRELATA_FILES_BYTE_IDENTICAL', 'ENTENDA_FILES_BYTE_IDENTICAL', 'FIRMWARE_CACHE_RULES_HOLD', 'REGRESSION_TARGETS_UNCHANGED'):
            self.assertTrue(self.v[k], k)
        r = subprocess.run(['git', 'diff', '--quiet', 'a57937e', 'HEAD', '--', 'firmware'], cwd=ROOT)
        self.assertEqual(r.returncode, 0)

    def test_9_reproducible(self):
        for _ in range(3):
            with tempfile.TemporaryDirectory() as t:
                R9.build(t)
                for line in (R9.OUT / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
                    h, name = line.split('  ', 1)
                    self.assertEqual(sha(Path(t) / name), h, name)
        for s in (AUD / 'apply_j2b_1_tema558.py', AUD / 'build_j2b_1_isolation_audit.py'):
            r = subprocess.run([sys.executable, '-I', '-B', str(s), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), s.name)

    def test_package(self):
        m = self.m
        self.assertEqual((m['package'], m['status'], m['card_touched'], m['device_flashed']), ('JURIS_J2B_1', 'HOST_ONLY_CANDIDATE', False, False))
        self.assertTrue(m['physical_baseline_reproduced'] and m['byte_identical_rebuild'] and m['device_manifest_matches_package'] and m['legacy_append_only'])
        for d in m['file_diff']:
            rel = d['path'].lstrip('/')
            self.assertEqual(sha(PKG / 'rollback/SD' / rel), self.card[rel], rel)
            self.assertEqual(sha(PKG / 'candidate/SD' / rel), d['after_sha256'], rel)
        for name in ('REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX', 'CF88_TARGETS.IDX'):
            sub = '10_TARGETS' if name.startswith('CF88') else '20_REFERENCES'
            self.assertEqual(sha(PKG / 'candidate/SD/99_LEX_V1' / sub / name), sha(R9.OUT / 'device_ready' / name), name)
        self.assertTrue((AUD / 'J2B_CANDIDATE_HOST_ONLY/SUPERSEDED.md').is_file())


if __name__ == '__main__':
    unittest.main()
