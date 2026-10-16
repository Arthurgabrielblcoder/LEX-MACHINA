"""REFERÊNCIAS Nº 4: physical baseline promotion. Promoted bytes = R1 candidate package = bytes physically tested (R2, 8/8);
the device manifest matches the promoted card; C3B.2 CORRELATA files untouched; freeze document consistent with the artifacts."""
import hashlib
import json
import re
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
REC = AUD / 'R2_PHYSICAL_DEPLOY'
PKG = AUD / 'REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY'
C3B2_POST = ROOT / 'DEVICE_INTEGRATION/C3B2_CORRELATA_PROMOTION/sd_manifest_post_full.json'
FREEZE = AUD / 'REFERENCES_4_CF_FROZEN.md'
TESTED = {
    '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX': 'da49c43b7a21990334a6a1af63fbc605fec7fde195a06a2014776285455006eb',
    '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX': 'efabb245e3beb8b63df33249a7a2e3c178aace02b361d9d344cb348d0fa823a0',
    '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX': 'd4e3342b99f5a5efb732eb9b36f786f3eaf5a33ab651500c7ce8a387bfe593f7',
    '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json': '7b8da57d943aef59f6dda55f1eb86484b516f7170da7074e3638949c7ce292fb',
    '99_LEX_V1/00_SYS/LEXV1.VER': 'edaf6147767ceece3fdd3149b63d79037e8e06a9de8ca71e3589da88a3758125',
}
CORRELATA = ('99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX', '99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX',
             '99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX')
FIRMWARE = '6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def rows(p):
    return [l.split('|') for l in Path(p).read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')]


class Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.post = load(REC / 'sd_manifest_post_full.json')['entries']
        cls.c3b2 = load(C3B2_POST)['entries']
        cls.final = load(REC / 'final_physical_verification.json')

    def test_package_bytes_are_the_physically_tested_bytes(self):
        for rel, h in TESTED.items():
            self.assertEqual(sha((PKG / 'candidate/SD' / rel).read_bytes()), h, rel)
            self.assertEqual(self.post[rel]['sha256'], h, rel)
            self.assertEqual(sha((PKG / 'rollback/SD' / rel).read_bytes()), self.c3b2[rel]['sha256'], rel)   # rollback = C3B.2

    def test_card_is_c3b2_plus_exactly_five_files(self):
        self.assertEqual(set(self.post), set(self.c3b2))
        self.assertEqual(sorted(k for k in self.post if self.post[k] != self.c3b2[k]), sorted(TESTED))
        for rel in CORRELATA:
            self.assertEqual(self.post[rel], self.c3b2[rel], rel)
        val = load(REC / 'physical_validation.json')
        self.assertEqual((val['result'], val['manifest_vs_card'], val['files_written'], val['other_files_untouched']), ('SD_VALIDATED', 'PASS', 5, True))

    def test_device_manifest_matches_promoted_card(self):
        man_b = (REC / 'promoted_sys/LEX_DEVICE_MANIFEST.json').read_bytes()
        man = json.loads(man_b.decode('utf-8'))
        for k, v in man['files'].items():
            if k != '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json':
                self.assertEqual(self.post[k]['sha256'], v['sha256'], k)
        self.assertEqual(sha(man_b), TESTED['99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json'])
        ver_b = (REC / 'promoted_sys/LEXV1.VER').read_bytes()
        self.assertEqual(sha(ver_b), TESTED['99_LEX_V1/00_SYS/LEXV1.VER'])
        ver = ver_b.decode('utf-8').splitlines()
        self.assertEqual(ver[0], '#LEXMACHINA|DEVICE_VERSION|3')
        self.assertIn(f"BUILD_ID|{man['build_id']}", ver)
        self.assertIn('REFERENCE_ENGINE|cf-reference-engine-run5-references4-r1', ver)

    def test_final_read_only_verification(self):
        f = self.final
        self.assertEqual((f['firmware']['PHYSICALLY_TESTED_FIRMWARE'], f['firmware']['app_image_sha256'], f['firmware']['reads_identical']),
                         ('EXACT', FIRMWARE, True))
        self.assertEqual((f['sd']['PHYSICALLY_TESTED_SD_BYTES'], f['sd']['MANIFEST_VS_SD']), ('5/5', 'PASS'))
        self.assertEqual(f['sd']['whole_card_vs_r2_post'], {'added': [], 'removed': [], 'changed': []})
        self.assertTrue(all(f['sd']['correlata_vs_c3b2'].values()))
        self.assertEqual((f['writes']['SD_WRITES_THIS_MISSION'], f['writes']['FIRMWARE_FLASH_THIS_MISSION']), (0, 'NO'))
        self.assertEqual((f['human_physical_test']['result'], f['human_physical_test']['tests']), ('PASS', '8/8'))
        fw = load(REC / 'firmware_flash.json')
        self.assertEqual((fw['candidate']['sha256'], fw['post']['app0_readback_sha256'], fw['post']['readback_match']), (FIRMWARE, FIRMWARE, True))

    def test_editorial_counts_from_promoted_bytes(self):
        pay = rows(PKG / 'candidate/SD/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX')
        tgt = rows(PKG / 'candidate/SD/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX')
        w = [r for r in pay if r[1] == 'WORK_REFERENCE' and r[2] == 'CURRENT_VISIBLE']
        self.assertEqual((len(w), len({r[5] for r in w}), len({r[0] for r in w})), (124, 56, 65))
        self.assertEqual({r[0] for r in tgt if r[3][3] == 'W'}, {r[0] for r in w})
        self.assertEqual({r[0] for r in tgt if r[3][1] == 'C'}, {r[0] for r in pay if r[1] == 'CORRELATA' and r[2] == 'CURRENT_VISIBLE'})
        old = {tuple(r) for r in rows(PKG / 'rollback/SD/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX')}
        new = {tuple(r) for r in pay}
        self.assertTrue(old <= new)                                                   # 122 previous links preserved
        self.assertEqual(sorted(r[4] for r in new - old), ['WORK_REFERENCE:R1A-DOC-001@CF88:ART.196', 'WORK_REFERENCE:R1A-DOC-002@CF88:ART.206:INC.I'])

    def test_freeze_document_consistent(self):
        txt = FREEZE.read_bytes().replace(b'\r\n', b'\n').decode('utf-8')        # checkout may use autocrlf
        fields = dict(re.findall(r'^([A-Z_0-9]+) = (.+)$', txt, re.M))
        expect = dict(LAYER='REFERENCES_4_CF', STATUS='FROZEN_APPROVED_BASELINE', PHYSICAL_VALIDATION='PASS', PHYSICAL_TESTS='8/8',
                      WORK_REFERENCE_RELATIONS='124', WORKS_USED='56', W_TARGETS='65', FIRMWARE_LOGIC_CHANGED='NO', FIRMWARE_DATA_CHANGED='YES',
                      FREEZE_DATE='2026-10-16', PREEXISTING_CORRELATA_TEST_DEBT='4', REFERENCE_TAG='lex-device-v1-references4-physical-approved-2026-10-16',
                      FIRMWARE_APP_SHA256=FIRMWARE, LEX_DEVICE_MANIFEST_SHA256=TESTED['99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json'])
        for k, v in expect.items():
            self.assertEqual(fields.get(k), v, k)


if __name__ == '__main__':
    unittest.main()
