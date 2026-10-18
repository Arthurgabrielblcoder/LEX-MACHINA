"""J2J — freeze of the physically approved J2I baseline (315/198, generic firmware). Host-only: the freeze document and the physical
validation record must agree with the committed J2H/J2I evidence (never touches the card or the device)."""
import json
import re
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
DOC = AUD / 'JURIS_CF_ADCT_J2I_FROZEN.md'
GENERIC_APP = '1371e69a0ef3b16773c36e240b166ee99f73d48c2629d11ebf09191701de2b6c'
PREVIOUS_APP = '6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c'


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class J2JFreeze(unittest.TestCase):
    def test_physical_validation_record(self):
        v = load(AUD / 'J2I_PHYSICAL_FLASH/J2I_PHYSICAL_VALIDATION.json')
        self.assertEqual(v['J2I_PHYSICAL_VALIDATION'], '32/32 PASS')
        self.assertEqual((v['PHYSICAL_RELATIONS'], v['PHYSICAL_TARGETS']), (315, 198))
        self.assertEqual(v['GENERIC_FIRMWARE_PHYSICAL_APPROVAL'], 'YES')
        self.assertEqual((v['tests_total'], v['tests_passed'], v['tests_failed'], v['rollback_executed']), (32, 32, 0, False))
        self.assertEqual(len(v['tests_passed_list']), 32)
        self.assertIn(GENERIC_APP, v['device'])

    def test_doc_header(self):
        t = DOC.read_text(encoding='utf-8')
        for line in ('BASELINE_ID = J2I_FROZEN_315_198', 'J2I_PHYSICAL_VALIDATION = 32/32 PASS', 'PHYSICAL_RELATIONS = 315',
                     'PHYSICAL_TARGETS = 198', 'GENERIC_FIRMWARE_PHYSICAL_APPROVAL = YES', f'FIRMWARE_APP_SHA256 = {GENERIC_APP}',
                     'CARD_BUILD_ID = def71b31a64c2a54', 'STJ_SUMULA_403 = UNRESOLVED_EXTERNAL', 'FROZEN_LAYERS_MODIFIED = NO'):
            self.assertIn(line, t)
        self.assertIn(PREVIOUS_APP, t)
        self.assertIn('0x10000', t)

    def test_doc_hashes_match_j2h_evidence(self):
        t = DOC.read_text(encoding='utf-8')
        readback = load(AUD / 'J2H_PHYSICAL_DEPLOY/physical_validation.json')['readback']
        card = load(AUD / 'J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json')
        self.assertEqual(card['file_count'], 1190)
        for path, e in readback.items():
            self.assertIn(e['sha256'], t, path)
            self.assertEqual(card['entries'][path]['sha256'], e['sha256'], path)
        self.assertIn(card['entries']['99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json']['sha256'], t)

    def test_card_and_firmware_evidence(self):
        sem = load(AUD / 'J2H_PHYSICAL_DEPLOY/semantic_check.json')
        self.assertEqual((sem['JURIS_RELATIONS'], sem['JURIS_TARGETS'], sem['RESULT']), (315, 198, 'PASS'))
        self.assertEqual((sem['CORRELATAS_CHANGED'], sem['REFERENCES4_CHANGED'], sem['ENTENDA_CHANGED']), ('NO', 'NO', 'NO'))
        self.assertEqual(sem['UNRESOLVED_EXTERNAL_PUBLISHED'], 0)
        ver = load(AUD / 'J2I_PHYSICAL_FLASH/06_verify.json')
        self.assertEqual(ver['APP0_READBACK_SHA256'], GENERIC_APP)
        self.assertEqual(load(AUD / 'J2I_PHYSICAL_FLASH/03_pre.json')['CURRENT_APP_PRE_HASH'], PREVIOUS_APP)

    def test_provisionals_preserved(self):
        reg = load(AUD / 'J2_PROVISIONAL_REGISTRY.json')
        ids = {i['source_id'] for i in reg['items']}
        self.assertEqual(ids, {'STF:ADI:7697', 'STF:ADI:5017', 'STF:ADPF:378', 'STF:RCL:84738'})
        t = DOC.read_text(encoding='utf-8')
        for i in reg['items']:
            self.assertIn(i['state'], t)
            self.assertIn(i['deadline'], t)

    def test_no_stj_sumula_403_on_card(self):
        entries = load(AUD / 'J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json')['entries']
        self.assertFalse([p for p in entries if re.search(r'STJ_SUMULA_403', p, re.I)])


if __name__ == '__main__':
    unittest.main()
