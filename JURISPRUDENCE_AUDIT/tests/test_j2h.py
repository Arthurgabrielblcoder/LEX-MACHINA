"""J2H — Candidate B data over the physically approved Candidate A: package reproducible, evidence of the SD deploy and of the generic
firmware simulation on the card bytes. Host-only (reads committed evidence; never touches the card)."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
EV = AUD / 'J2H_PHYSICAL_DEPLOY'


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class J2H(unittest.TestCase):
    def test_package_up_to_date(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'build_j2h_candidate.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))

    def test_package(self):
        m = load(AUD / 'J2H_CANDIDATE_B_OVER_A/J2H_PACKAGE_MANIFEST.json')
        self.assertEqual((m['juris_relations'], m['juris_targets']), (315, 198))
        self.assertEqual((m['legacy']['A_INDEX_PREFIX_IDENTICAL'], m['legacy']['OLD_OFFSETS_PRESERVED']), ('YES', 'YES'))
        self.assertTrue(m['legacy']['same_rows_as_j2f_b'] and m['legacy']['same_lookup_tuples_as_j2f_b'])
        self.assertEqual((len(m['file_diff']), len(m['file_additions']), m['legacy']['rows_appended']), (7, 15, 16))
        a_card = {k: v['sha256'] for k, v in load(AUD / 'J2G_PHYSICAL_DEPLOY/sd_manifest_post_full.json')['entries'].items()}
        for d in m['file_diff']:                                   # rollback = Candidate A as physically approved, never J2C
            rel = d['path'].lstrip('/')
            self.assertEqual(d['before_sha256'], a_card[rel], rel)
            self.assertEqual(hashlib.sha256((AUD / 'J2H_CANDIDATE_B_OVER_A/rollback/SD' / rel).read_bytes()).hexdigest(), a_card[rel], rel)
        self.assertFalse(any('STJ_SUMULA_403' in d['path'] for d in m['file_additions']))

    def test_a_physical_approval_recorded(self):
        v = load(AUD / 'J2G_PHYSICAL_DEPLOY/J2G_PHYSICAL_VALIDATION.json')
        self.assertEqual((v['J2G_PHYSICAL_VALIDATION'], v['CANDIDATE_A_PHYSICAL_APPROVED'], v['PHYSICAL_BASELINE_RELATIONS'],
                          v['PHYSICAL_BASELINE_TARGETS']), ('21/21 PASS', 'YES', 299, 186))

    def test_deploy_evidence(self):
        pre, val, sem = load(EV / 'physical_pre.json'), load(EV / 'physical_validation.json'), load(EV / 'semantic_check.json')
        self.assertEqual((pre['PREDEPLOY_SD_BASELINE'], pre['CANDIDATE_A_HASHES'], pre['CARD_FILESET_MATCHES_A'], pre['PROVISIONAL_GATE'],
                          pre['ROLLBACK_TO_A_READY']), ('299/186', 'ALL_EXACT', 'YES', 'PASS', 'YES'))
        self.assertEqual(pre['gates']['firmware']['FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE'], 'PASS')
        self.assertEqual(pre['gates']['firmware']['GENERIC_FIRMWARE_PROTOTYPE'], 'PASS')
        self.assertEqual((val['result'], val['SD_HASHES'], val['MANIFEST_VS_SD'], val['CARD_FILESET_MATCHES_B'], val['UNEXPECTED_SD_CHANGES'],
                          val['JURIS_RELATIONS'], val['JURIS_TARGETS'], val['FIRMWARE_FLASHED'], val['SAFE_TO_BOOT_WITH_CURRENT_FIRMWARE']),
                         ('SD_VALIDATED', 'PASS', 'PASS', 'YES', 0, 315, 198, 'NO', 'NO'))
        self.assertEqual((sem['GENERIC_FW_SIMULATION'], sem['NO_LABEL_OUTRO'], sem['ALL_B_FICHAS_RESOLVE'], sem['BACK_BEHAVIOR_SIMULATION'],
                          sem['CACHE_LIMITS'], sem['A_RELATIONS_PRESERVED'], sem['UNRESOLVED_EXTERNAL_PUBLISHED']),
                         ('PASS', 'YES', 'YES', 'PASS', 'PASS', '299/299', 0))
        self.assertEqual((sem['CORRELATAS_CHANGED'], sem['REFERENCES4_CHANGED'], sem['ENTENDA_CHANGED']), ('NO', 'NO', 'NO'))
        self.assertEqual({k: v for k, v in sem['FLAG_CHANGES'].items() if k != 'J'}, dict(E=0, C=0, W=0, R=0, X=0))
        self.assertTrue(all(sem['REQUIRED_LABELS_FOUND'].values()) and all(sem['IMPORTANT_TARGETS_OK'].values()))
        self.assertEqual((sem['REJECTED_RELATIONS_PUBLISHED'], sem['DUPLICATE_OR_ALREADY_COVERED_CREATED_NEW_RELATIONS']), ([], []))


if __name__ == '__main__':
    unittest.main()
