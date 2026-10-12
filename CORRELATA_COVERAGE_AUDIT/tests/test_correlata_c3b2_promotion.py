"""C3B.2 promotion: promoted bytes = bytes physically tested as C3B.1; regenerated device manifest matches the promoted baseline."""
import hashlib
import json
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
ROOT = AUDIT.parent
REC = ROOT / 'DEVICE_INTEGRATION/C3B2_CORRELATA_PROMOTION'
C3B1 = AUDIT / 'C3B1_PHYSICAL_TEST_PACKAGE/candidate/SD'
C3B2 = AUDIT / 'C3B2_PHYSICAL_TEST_PACKAGE/candidate/SD'
PIN = json.loads((AUDIT / 'inputs/CORRELATA_EVIDENCE_PIN.json').read_text(encoding='utf-8'))['physical_sd']['files']
TESTED = {
    '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX': 'd2fcc15bbe41ef16c51bbe1ef7cb201bd9677b6ac54198b96ad2abc08395e06c',
    '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX': '27c67eea6a38e3cba012d4a3d02c3856d37fd4cd1bae15473854fab0edea5430',
    '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX': '1762642d337aff83ac5b95e074235bc58028b8a68bac17a384e9eed4a4a5addd',
    '99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX': '5c54face7ea7eff62dbbb0a4193b5e2452e7fb03d82012d09919e74d234b3e5e',
    '99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX': '691790f3ee5d4aaa9b88235bca33008357b99d87324c07b1da8b51355c20685c',
    '99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX': 'efac06cee0a1d8f0676564ba128d0ab8f474b89399f40de6422cc6fded37ef2c',
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(name):
    return json.loads((REC / name).read_text(encoding='utf-8'))


class Promotion(unittest.TestCase):
    def test_c3b2_device_bytes_equal_c3b1_physically_tested(self):
        for rel, h in TESTED.items():
            a, b = (C3B1 / rel).read_bytes(), (C3B2 / rel).read_bytes()
            self.assertEqual(a, b, rel)
            self.assertEqual(sha(b), h, rel)

    def test_staging_used_exact_tested_bytes_and_was_reproducible(self):
        host = load('STAGING_FILE_MANIFEST.json')
        self.assertTrue(host['byte_identical_rebuild'])
        self.assertGreaterEqual(host['deterministic_runs'], 2)
        self.assertTrue(all(host['promotion_bytes_match_physical_test'].values()))
        files = {f['path'].lstrip('/'): f['sha256'] for f in host['files']}
        for rel, h in TESTED.items():
            self.assertEqual(files[rel], h)
        self.assertEqual(host['changed_vs_physical_baseline'], ['00_SYS/LEXV1.VER', '00_SYS/LEX_DEVICE_MANIFEST.json', '10_TARGETS/CF88_TARGETS.IDX',
                                                               '20_REFERENCES/REF_LOOKUP.IDX', '20_REFERENCES/REF_PAYLOAD.IDX'])

    def test_device_manifest_matches_promoted_baseline(self):
        man = json.loads((REC / 'promoted_sys/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
        post = load('sd_manifest_post_full.json')['entries']
        for k, v in man['files'].items():
            if k != '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json':
                self.assertEqual(post[k]['sha256'], v['sha256'], k)
        self.assertEqual(post['99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json']['sha256'], sha((REC / 'promoted_sys/LEX_DEVICE_MANIFEST.json').read_bytes()))
        self.assertEqual(post['99_LEX_V1/00_SYS/LEXV1.VER']['sha256'], sha((REC / 'promoted_sys/LEXV1.VER').read_bytes()))
        ver = (REC / 'promoted_sys/LEXV1.VER').read_text(encoding='utf-8').splitlines()
        self.assertEqual(ver[0], '#LEXMACHINA|DEVICE_VERSION|3')
        self.assertIn(f"BUILD_ID|{man['build_id']}", ver)

    def test_card_after_promotion(self):
        val = load('physical_validation.json')
        self.assertEqual((val['result'], val['manifest_vs_card'], val['other_files_untouched']), ('SD_VALIDATED', 'PASS', True))
        post = load('sd_manifest_post_full.json')['entries']
        for rel, h in TESTED.items():
            self.assertEqual(post[rel]['sha256'], h)
        changed = sorted(k for k in PIN if post.get(k, {}).get('sha256') != PIN[k]['sha256'])
        self.assertEqual(changed, sorted(list(TESTED) + ['99_LEX_V1/00_SYS/LEXV1.VER', '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json']))
        self.assertEqual(val['file_count_pre'], val['file_count_post'])


if __name__ == '__main__':
    unittest.main()
