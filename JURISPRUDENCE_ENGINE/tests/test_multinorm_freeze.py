"""Multinorm freeze: CF/ADCT 315/198 + CC2002 29/24 (36/36), firmware 25/25 with full sha, Tema 932 shared, no pending/rejected published."""
import json
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
DOC = ENG / 'MULTINORM_CF_CC_J1_FROZEN.md'
FW_SHA = '38c4d71f77b89223860a6643ef9880416cb1f22a8ba933524e6b083442216bb2'


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class MultinormFreeze(unittest.TestCase):
    def test_records(self):
        cc = load(ENG / 'CC_J1_PHYSICAL_DEPLOY/CC_J1_PHYSICAL_VALIDATION.json')
        self.assertEqual((cc['PHYSICAL_VALIDATION'], cc['RELATIONS'], cc['TARGETS'], cc['PRECEDENTS'], cc['LOGICAL_FICHAS'], cc['NEW_FICHAS'],
                          cc['SHARED_FICHAS']), ('36/36 PASS', 29, 24, 20, 20, 19, 1))
        self.assertEqual((cc['SHARED_FICHA_CROSS_NORM'], cc['CC_PENDING_PHYSICAL_RELATIONS'], cc['CC_REJECTED_PHYSICAL_RELATIONS']),
                         ('PHYSICALLY_VALIDATED', 0, 0))
        fw = load(ENG / 'firmware_multinorm/PHYSICAL_FLASH/MULTINORM_PHYSICAL_VALIDATION.json')
        self.assertEqual((fw['MULTINORM_FIRMWARE_PHYSICAL_VALIDATION'], fw['app']['sha256']), ('25/25 PASS', FW_SHA))
        self.assertEqual(load(ENG / 'firmware_multinorm/PHYSICAL_FLASH/06_verify.json')['APP0_READBACK_SHA256'], FW_SHA)

    def test_doc_and_checkpoint(self):
        t = DOC.read_text(encoding='utf-8')
        for s in ('BASELINE_ID = MULTINORM_FROZEN_CF315_198_CC29_24', 'CC_J1_FROZEN_29_24', 'J2I_FROZEN_315_198', FW_SHA, '25/25 PASS', '36/36 PASS',
                  'TOTAL = 344 / 222', 'FROZEN_LAYERS_MODIFIED = NO', 'CCJ1-09', 'CCJ1-30', 'CF88:ART.7:INC.XXVIII', 'CC2002:ART.927:PAR.UNICO'):
            self.assertIn(s, t)
        c = (ROOT / 'JURISPRUDENCE_AUDIT/POST_OVERNIGHT_CHECKPOINT.md').read_text(encoding='utf-8')
        self.assertIn('NORMS_WITH_PHYSICAL_JURISPRUDENCE = 2', c)
        self.assertIn('TOTAL_RELATIONS = 344 · TOTAL_TARGETS = 222', c)

    def test_card_evidence_consistent(self):
        v = load(ENG / 'CC_J1_PHYSICAL_DEPLOY/physical_validation.json')
        self.assertEqual((v['CF_RELATIONS'], v['CF_TARGETS'], v['normalized_counts']['CC2002']['relations'], v['normalized_counts']['CC2002']['targets']),
                         ('315/315', '198/198', 29, 24))
        self.assertEqual((v['PENDING_PRESENT'], v['REJECTED_PRESENT'], v['FROZEN_LAYER_CHANGES'], v['CROSS_NORM_SHARED_FICHA']), (0, 0, 0, 'PASS'))
        self.assertEqual(315 + 29, 344)
        self.assertEqual(198 + 24, 222)


if __name__ == '__main__':
    unittest.main()
