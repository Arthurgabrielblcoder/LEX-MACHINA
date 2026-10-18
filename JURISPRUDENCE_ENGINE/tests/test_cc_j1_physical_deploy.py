"""CC-J1 physical deploy evidence (data only): PRE baseline match, additive copy, readback and card-byte simulation; firmware 25/25 record."""
import json
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
EV = ENG / 'CC_J1_PHYSICAL_DEPLOY'


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class PhysicalDeploy(unittest.TestCase):
    def test_firmware_record(self):
        r = load(ENG / 'firmware_multinorm/PHYSICAL_FLASH/MULTINORM_PHYSICAL_VALIDATION.json')
        self.assertEqual((r['MULTINORM_FIRMWARE_PHYSICAL_VALIDATION'], r['MULTINORM_FIRMWARE_PHYSICALLY_APPROVED']), ('25/25 PASS', 'YES'))
        self.assertEqual(r['app']['sha256'], load(ENG / 'firmware_multinorm/PHYSICAL_FLASH/06_verify.json')['APP0_READBACK_SHA256'])

    def test_pre(self):
        p = load(EV / 'physical_pre.json')
        self.assertEqual((p['result'], p['SD_PRE_BASELINE_MATCH'], p['card_files']), ('PRE_OK', 'PASS', 1190))
        self.assertEqual((p['CF_ADCT_RELATIONS'], p['CF_ADCT_TARGETS'], p['CC2002_RELATIONS'], p['normalized_layer_present']), (315, 198, 0, False))
        self.assertEqual((p['tema932']['TEMA932_PHYSICAL_HASH_MATCH'], p['tema932']['TEMA932_SHARED_FICHA']), ('YES', 'VERIFIED_PHYSICAL_REUSE'))
        self.assertEqual((p['UNEXPECTED_PATH_COLLISIONS'], p['tema932_in_add_list'], p['ROLLBACK_TO_CF_ONLY_READY']), (0, False, 'YES'))

    def test_copy_additive(self):
        c = load(EV / 'copy_log.json')
        self.assertEqual((c['created_count'], c['replaced'], c['deleted']), (23, [], []))
        self.assertNotIn('99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_932.TXT', c['created'])
        self.assertEqual(sorted(c['created']), sorted(load(EV / 'rollback_plan.json')['delete_files']))

    def test_validation_on_card_bytes(self):
        v = load(EV / 'physical_validation.json')
        self.assertEqual(v['result'], 'SD_VALIDATED')
        for k, want in dict(DEPLOYED_HASHES='EXACT', EXTRA_UNEXPECTED_FILES=0, EXISTING_FILES_MODIFIED=0, FILES_REMOVED=0, FROZEN_LAYER_CHANGES=0,
                            CF_ADCT_LEXV1='315/198', DUPLICATE_QUERY_KEYS=0, LOOKUP_LOST_RELATIONS=0, CC_RELATIONS_VISIBLE='29/29',
                            CC_TARGETS_VISIBLE='24/24', PENDING_PRESENT=0, REJECTED_PRESENT=0, FICHA_OPEN='29/29', BACK_SIMULATION='29/29',
                            CROSS_NORM_SHARED_FICHA='PASS', CF_RELATIONS='315/315', CF_TARGETS='198/198', CF_LOST_RELATIONS=0, CF_CHANGED='NO',
                            CF_REGRESSION='PASS', card_files_post=1213).items():
            self.assertEqual(v[k], want, k)
        self.assertEqual(v['normalized_counts']['CC2002'], dict(relations=29, targets=24, precedents=20))
        self.assertEqual(v['art62_list'], ['RG TEMA 33', 'RG TEMA 1196'])
        self.assertEqual(v['cases']['CC2002:ART.186']['labels'], ['ADI 6792/7055', 'Súmula 403 STJ'])
        self.assertEqual(v['cases']['CC2002:ART.2028']['labels'], ['Súmula 405 STJ', 'Súmula 547 STJ'])
        self.assertTrue(all(c['ok'] for c in v['cases'].values()))


if __name__ == '__main__':
    unittest.main()
