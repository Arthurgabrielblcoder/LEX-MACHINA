"""CC-J2 physical deploy evidence (mixed transactional, data only): PRE baseline, backup, transactional copy, POST validation on the card bytes."""
import json
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
EV = ENG / 'CC_J2_PHYSICAL_DEPLOY'


def load(n):
    return json.loads((EV / n).read_text(encoding='utf-8'))


class CCJ2PhysicalDeploy(unittest.TestCase):
    def test_pre(self):
        p = load('physical_pre.json')
        self.assertEqual((p['result'], p['SD_PRE_BASELINE_MATCH'], p['CF_ADCT_LEXV1'], p['CC2002_ON_CARD'], p['CCJ1_RELATIONS_ON_CARD'],
                          p['CCJ2_RELATIONS_ALREADY_ON_CARD'], p['card_files']), ('PRE_OK', 'PASS', '315/198', '29/24', '29/29', 0, 1213))
        self.assertEqual((p['UNEXPECTED_FICHA_COLLISIONS'], p['BACKUP_EXACT'], p['ROLLBACK_TO_CCJ1_29_24_READY'],
                          p['tema932']['TEMA932_PHYSICAL_HASH_MATCH']), (0, 'PASS', 'YES', 'YES'))
        self.assertEqual(len(p['backup']), 4)

    def test_copy(self):
        c = load('copy_log.json')
        self.assertEqual((c['aborted'], c['created_count'], c['replaced_count'], c['NEW_FICHAS_READBACK'], c['NORMALIZED_STAGING'],
                          c['NORMALIZED_READBACK']), (None, 17, 4, 'EXACT', 'PASS', 'EXACT'))
        self.assertTrue(c['order_phase7'][-1].endswith('JUR_LOOKUP.IDX'))

    def test_post(self):
        v = load('physical_validation.json')
        self.assertEqual((v['result'], v['DEPLOYED_HASHES'], v['UNEXPECTED_CHANGED_FILES'], v['FROZEN_LAYER_CHANGES'], v['card_files_post']),
                         ('SD_VALIDATED', 'EXACT', 0, 0, 1230))
        self.assertEqual((v['CF_ADCT_LEXV1'], v['CC2002'], v['TOTAL'], v['CCJ1_RELATIONS'], v['CCJ2_RELATIONS'], v['CCJ2_TARGETS_VISIBLE'],
                          v['CCJ1_TARGETS']), ('315/198', '49/39', '364/237', '29/29', '20/20', '18/18', '24/24'))
        self.assertTrue(all(x == 'PASS' for x in list(v['SHARED_TARGETS'].values()) + list(v['CRITICAL'].values())))
        self.assertEqual((v['IAC_LABEL'], v['REPETITIVO_STJ_LABEL'], v['SHARED_FICHAS'], v['REJECTED_RELATIONS_PRESENT'], v['OUTRO_LABELS'],
                          v['CF_REGRESSION'], v['CCJ1_REGRESSION'], v['TEMA932_CROSS_NORM'], v['DUPLICATE_QUERY_KEYS']),
                         ('PASS', 'PASS', 'PASS', 0, 0, 'PASS', 'PASS', 'PASS', 0))
        self.assertEqual(v['ART62'], ['RG TEMA 33', 'RG TEMA 1196'])
        self.assertFalse((EV / 'rollback_log.json').exists())                       # no rollback was needed


if __name__ == '__main__':
    unittest.main()
