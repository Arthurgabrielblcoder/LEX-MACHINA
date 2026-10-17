"""J2E — ratified BATCH02 materialized host-only (variant A: current firmware; variant B: + HC, needs firmware). Nothing installed."""
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
sys.path.insert(0, str(AUD / 'FIRMWARE_REPRODUCIBILITY'))
import firmware_baseline as FB  # noqa: E402  (Parte D: only the sha-pinned 124-ficha header may differ)
import build_export_run10_juris_j2e as R10  # noqa: E402
import apply_j2e_batch02_overlay as O  # noqa: E402

PKG = AUD / 'J2_HIGH_BACKLOG/J2E_BATCH02_CANDIDATE_HOST_ONLY'
CARD = AUD / 'J2C_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
AUDIT = AUD / 'J2_HIGH_BACKLOG/J2E_ISOLATION_AUDIT.json'
ARCH_FICHAS = Path('C:/LMA/p545e/20260928/LEX_MACHINA_JURIS_CF_J4_6/SD_JURIS_J4_TESTE/99_JURISPRUDENCIA_V2/03_CONTEUDO')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class J2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.add = json.loads(O.OUT.read_text(encoding='utf-8'))
        cls.v = json.loads(AUDIT.read_text(encoding='utf-8'))['variants']
        cls.card = {k: x['sha256'] for k, x in json.loads(CARD.read_text(encoding='utf-8'))['entries'].items()}

    def test_generators_up_to_date(self):
        for s in (AUD / 'apply_j2e_batch02_overlay.py', AUD / 'build_j2e_isolation_audit.py'):
            r = subprocess.run([sys.executable, '-I', '-B', str(s), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), s.name)

    def test_run10_reproducible(self):
        for variant in ('A', 'B'):
            with tempfile.TemporaryDirectory() as t:
                R10.build(t, variant)
                for line in (R10.OUT[variant] / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
                    h, name = line.split('  ', 1)
                    self.assertEqual(sha(Path(t) / name), h, (variant, name))

    def test_ficha_format_fidelity(self):
        corpus, _ = O.corpus()
        for ident in ('STF:RG:147', 'STF:SV:17', 'STF:RG:558', 'STF:RG:1246'):       # regenerate card fichas byte for byte
            p = ARCH_FICHAS / (ident.replace(':', '_') + '.TXT')
            self.assertEqual(O.texto_detalhe(corpus[ident]).encode('utf-8'), p.read_bytes(), ident)

    def test_normalized_counts(self):
        recs = self.add['records']
        a = [r for r in recs if r['variant'] == 'A']
        self.assertEqual(len({x for r in recs for x in r['ratified_decisions']}), 9)        # 10 decisions - 1 rejection
        self.assertEqual((len(a), len(recs)), (7, 8))                                         # DEVICE_RELATIONS A / B
        self.assertEqual(len({r['source_id'] for r in recs}), 6)                              # PRECEDENT_RECORDS (7047-7064, 7064, 793, 46, 950, HC)
        self.assertEqual(sorted(k for k in self.add['fichas']), ['STF:ADI:7064', 'STF:HC:232627', 'STF:RG:793', 'STF:RG:950', 'STF:SV:46'])
        self.assertEqual(self.add['rejected']['precedent'], 'STF:ADI:2167')

    def test_adi_7064_not_joint_on_107a(self):
        r = [r for r in self.add['records'] if r['target_id'] == 'ADCT:ART.107-A'][0]
        self.assertEqual((r['source_id'], r['label'], r['joint']), ('STF:ADI:7064', 'ADI 7064', 'SAME_JUDGMENT_NOT_SAME_SCOPE'))
        self.assertNotIn('7047/', r['legacy_idx_row'])
        for v in self.v.values():
            self.assertTrue(v['verdict']['ADCT_107A_LABEL_IS_ADI_7064_ONLY'] and v['verdict']['ADCT_101_PAR5_LABEL_IS_JOINT'])
        ficha = self.add['fichas']['STF:ADI:7064']
        self.assertIn('somente da ADI 7064', ficha)

    def test_adct_key_convention(self):
        by_t = {r['target_id']: r for r in self.add['records']}
        self.assertTrue(by_t['ADCT:ART.101:PAR.5']['source_reference_id'].endswith(':CF88:101:5:-:-'))
        self.assertEqual(by_t['ADCT:ART.107-A']['legacy_lookup'][:2], ['CF88', '107-A'])

    def test_isolation_and_packages(self):
        exp = {'A': (268, 166, 6, 4), 'B': (269, 167, 7, 5)}
        for v, r in self.v.items():
            x = r['verdict']
            self.assertEqual((x['JURIS_RELATIONS'], x['JURIS_TARGETS'], x['J_FLAGS_CHANGED'], x['FILES_ADDED']), exp[v])
            for k in ('INSTALLED_261_BYTE_IDENTICAL', 'ONLY_APPROVED_RELATIONS_ADDED', 'J_FLAG_EQUALS_VISIBLE_JURIS', 'LEGACY_PREFIX_IDENTICAL',
                      'FIRMWARE_CACHE_RULES_HOLD', 'ALL_SIMULATED_RESOLVE_WITH_FICHA', 'SV46_SAME_FICHA_TWO_TARGETS', 'REJECTED_NOT_LINKED',
                      'REGRESSION_TARGETS_UNCHANGED'):
                self.assertTrue(x[k], (v, k))
            for k in ('ROWS_REMOVED', 'CORRELATA_RELATION_SET_CHANGED', 'WORK_REFERENCE_SET_CHANGED', 'E_FLAGS_CHANGED', 'C_FLAGS_CHANGED',
                      'W_FLAGS_CHANGED', 'R_FLAGS_CHANGED', 'X_FLAGS_CHANGED'):
                self.assertEqual(x[k], 0, (v, k))
            m = json.loads((PKG / r['package'] / 'J2E_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
            self.assertTrue(m['physical_baseline_reproduced'] and m['byte_identical_rebuild'] and not m['card_touched'] and not m['device_flashed'])
            for d in m['file_diff']:
                rel = d['path'].lstrip('/')
                self.assertEqual(sha(PKG / r['package'] / 'rollback/SD' / rel), self.card[rel], rel)
                self.assertEqual(sha(PKG / r['package'] / 'candidate/SD' / rel), d['after_sha256'], rel)
            for d in m['file_additions']:
                self.assertNotIn(d['path'].lstrip('/'), self.card)
        self.assertEqual(self.v['A']['verdict']['HC_LABEL_CURRENT_FIRMWARE'], [])               # A has no HC
        self.assertEqual(self.v['B']['verdict']['HC_LABEL_CURRENT_FIRMWARE'], ['OUTRO 232627'])   # why B needs firmware
        self.assertEqual(self.v['B']['verdict']['HC_LABEL_HC_FIRMWARE'], ['HC 232627'])

    def test_physical_baseline_untouched(self):
        m = json.loads((AUD / 'J2B_1_CANDIDATE_HOST_ONLY/J2B_1_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
        for d in m['file_diff'] + m['file_additions']:
            rel = d['path'].lstrip('/')
            self.assertEqual(sha(AUD / 'J2B_1_CANDIDATE_HOST_ONLY/candidate/SD' / rel), self.card[rel], rel)
        self.assertEqual(FB.firmware_changes('a57937e'), [])


if __name__ == '__main__':
    unittest.main()
