"""J2B — ADI record model, RUN8 (256 + 5), host-only SD package, isolation and the provisional revalidation gate."""
import datetime as dt
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
import build_export_run8_juris_j2b as R8  # noqa: E402
import check_j2b_provisional as G  # noqa: E402

PKG = AUD / 'J2B_CANDIDATE_HOST_ONLY'
CARD = AUD / 'J1_5_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
ADD = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADI_ADDITIONS_J2B.json'
CONTENT = PKG / 'candidate/SD/99_JURISPRUDENCIA_V2/03_CONTEUDO'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class J2B(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.add = json.loads(ADD.read_text(encoding='utf-8'))
        cls.m = json.loads((PKG / 'J2B_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
        cls.v = json.loads((AUD / 'J2B_ISOLATION_AUDIT.json').read_text(encoding='utf-8'))['verdict']

    def test_generators_up_to_date(self):
        for s in (AUD / 'apply_j2b_adi_overlay.py', AUD / 'build_j2b_isolation_audit.py', AUD / 'build_j2a_batch01.py'):
            r = subprocess.run([sys.executable, '-I', '-B', str(s), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), s.name)

    def test_run8_reproducible(self):
        with tempfile.TemporaryDirectory() as t:
            R8.build(t)
            for line in (R8.OUT / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
                h, name = line.split('  ', 1)
                self.assertEqual(sha(Path(t) / name), h, name)
                self.assertEqual(sha(R8.OUT / name), h, name)

    def test_ratified_model(self):
        rat = self.add['ratification']['decisions']
        self.assertEqual(sum(1 for v in rat.values() if v.startswith('PROMOTE')), 6)
        recs = self.add['records']
        self.assertEqual(len(recs), 5)
        joint = [r for r in recs if r['source_id'] == 'STF:ADI:7047-7064']
        self.assertEqual(len(joint), 1)                                   # one record, both identifiers
        self.assertEqual(joint[0]['aliases'], ['ADI 7047', 'ADI 7064'])
        self.assertEqual(joint[0]['ratified_decisions'], ['J0-BL-081', 'J0-BL-082'])
        for r in recs:
            prov = r['source_id'] == 'STF:ADI:7697'
            self.assertEqual(r['provisional'], prov)
            self.assertEqual(r['status_processual'], ['cautelar_referendada', 'merito_pendente'] if prov else ['merito_julgado'])
            f = r['legacy_idx_row'].split('|')
            self.assertEqual((len(f), f[1], f[2], f[6]), (8, 'adi', 'STF', r['source_id']))
            self.assertTrue(f[3].endswith('(CAUTELAR)') == prov)
        self.assertNotIn('CF88:ART.166', {r['target_id'] for r in recs})   # DUPLICATE / DO_NOT_PROMOTE
        self.assertNotIn('STF:ADI:3392', {r['source_id'] for r in recs})

    def test_fichas(self):
        names = sorted(p.name for p in CONTENT.iterdir())
        self.assertEqual(names, ['STF_ADI_4425.TXT', 'STF_ADI_7047-7064.TXT', 'STF_ADI_7697.TXT'])
        t7697 = (CONTENT / 'STF_ADI_7697.TXT').read_text(encoding='utf-8')
        self.assertIn('DECISÃO PROVISÓRIA', t7697)
        self.assertIn('mérito pendente', t7697)
        joint = (CONTENT / 'STF_ADI_7047-7064.TXT').read_text(encoding='utf-8')
        self.assertIn('JULGAMENTO CONJUNTO', joint)
        self.assertIn('7047', joint)
        self.assertIn('7064', joint)
        for p in CONTENT.iterdir():
            b = p.read_bytes()
            self.assertFalse(b.startswith(b'\xef\xbb\xbf') or b'\r' in b, p.name)   # same encoding as the current fichas

    def test_package_and_rollback(self):
        m = self.m
        self.assertEqual((m['status'], m['card_touched'], m['device_flashed']), ('HOST_ONLY_CANDIDATE', False, False))
        self.assertTrue(m['physical_baseline_reproduced'] and m['byte_identical_rebuild'] and m['device_manifest_matches_package'] and m['legacy_append_only'])
        self.assertEqual((len(m['changed_vs_physical']), len(m['added_vs_physical'])), (7, 3))
        card = {k: v['sha256'] for k, v in json.loads(CARD.read_text(encoding='utf-8'))['entries'].items()}
        for d in m['file_diff']:
            rel = d['path'].lstrip('/')
            self.assertEqual(sha(PKG / 'rollback/SD' / rel), card[rel], rel)
            self.assertEqual(sha(PKG / 'candidate/SD' / rel), d['after_sha256'], rel)
        for a in m['file_additions']:
            rel = a['path'].lstrip('/')
            self.assertNotIn(rel, card)
            self.assertEqual(a['rollback'], 'DELETE')
            self.assertEqual(sha(PKG / 'candidate/SD' / rel), a['after_sha256'], rel)
        for name in ('REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX', 'CF88_TARGETS.IDX'):
            sub = '10_TARGETS' if name.startswith('CF88') else '20_REFERENCES'
            self.assertEqual(sha(PKG / 'candidate/SD/99_LEX_V1' / sub / name), sha(R8.OUT / 'device_ready' / name), name)

    def test_isolation(self):
        v = self.v
        for k in ('CURRENT_256_BYTE_IDENTICAL', 'ADDED_EQUALS_RATIFIED_5', 'J_FLAG_EQUALS_VISIBLE_JURIS', 'TARGET_SET_UNCHANGED',
                  'CORRELATA_FILES_BYTE_IDENTICAL', 'ENTENDA_FILES_BYTE_IDENTICAL', 'LEGACY_IDX_APPEND_ONLY', 'LEGACY_LOOKUP_APPEND_ONLY',
                  'FIRMWARE_CACHE_RULES_HOLD', 'ALL_ADI_LINKS_RESOLVE', 'REGRESSION_TARGETS_UNCHANGED'):
            self.assertTrue(v[k], k)
        for k in ('ROWS_REMOVED', 'CORRELATA_RELATION_SET_CHANGED', 'WORK_REFERENCE_SET_CHANGED', 'E_FLAGS_CHANGED', 'C_FLAGS_CHANGED',
                  'W_FLAGS_CHANGED', 'R_FLAGS_CHANGED', 'X_FLAGS_CHANGED', 'NON_FLAG_FIELDS_CHANGED'):
            self.assertEqual(v[k], 0, k)
        self.assertEqual((v['JURIS_RELATIONS_AFTER'], v['JURIS_TARGETS_AFTER'], v['J_FLAGS_CHANGED']), (261, 160, 4))
        self.assertEqual(v['R_FLAG_KNOWN_DIVERGENCE'], 42)

    def test_provisional_gate(self):
        self.assertTrue(all(r['result'] == 'PASS' for r in G.check(dt.date(2026, 10, 16))))
        self.assertTrue(all(r['result'] == 'REVALIDATION_REQUIRED' for r in G.check(dt.date(2027, 1, 15))))   # > 90 days
        reg = json.loads(G.REG.read_text(encoding='utf-8'))
        reg['items'][0]['merit_judged'] = True                                                     # trigger fired
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'reg.json'
            p.write_text(json.dumps(reg), encoding='utf-8')
            self.assertEqual(G.check(dt.date(2026, 10, 16), p)[0]['result'], 'REVALIDATION_REQUIRED')
        self.assertEqual(reg['items'][0]['targets'], ['CF88:ART.166:PAR.9', 'CF88:ART.166:PAR.11', 'CF88:ART.166-A'])

    def test_firmware_untouched(self):
        self.assertEqual(FB.firmware_changes('a57937e'), [])


if __name__ == '__main__':
    unittest.main()
