"""CC mass discovery: generated outputs up to date; every qualified relation is real, official, valid, new, unique and unratified;
baselines untouched; checkpoint consistent."""
import collections
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
OUT = ENG / 'CC_MASS_DISCOVERY'
sys.path.insert(0, str(ENG))
import batch_engine as E  # noqa: E402


def jl(p):
    return [json.loads(l) for l in (OUT / p).read_text(encoding='utf-8').splitlines() if l.strip()]


class CCMassDiscovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q = jl('CC_MASS_DISCOVERY_QUALIFIED.jsonl')
        cls.rej = jl('CC_MASS_DISCOVERY_REJECTED.jsonl')
        cls.m = json.loads((OUT / 'CC_MASS_DISCOVERY_METRICS.json').read_text(encoding='utf-8'))
        cls.index = {t['target_id'] for t in json.loads((ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json')
                                                        .read_text(encoding='utf-8'))['targets']}

    def test_up_to_date(self):
        r = subprocess.run([sys.executable, '-B', str(ENG / 'build_cc_mass_discovery.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), r.stderr[-1500:])

    def test_qualified_integrity(self):
        ids = [x['id'] for x in self.q]
        self.assertEqual(len(ids), len(set(ids)))
        keys = [(x['target_id'], x['precedent_id']) for x in self.q]
        self.assertEqual(len(keys), len(set(keys)))                                     # no relation counted twice
        _, _, rows = E.physical_layer(ENG / 'CC_J2_MATERIALIZATION_CANDIDATE/candidate/SD')
        phys = {(r['target_id'], r['precedent_id']) for r in rows}
        for x in self.q:
            self.assertIn(x['tier'], ('A', 'B'))
            self.assertIn(x['target_id'], self.index, x['id'])                            # valid target
            self.assertTrue(x['target_id'].startswith('CC2002:'))
            self.assertNotIn((x['target_id'], x['precedent_id']), phys, x['id'])         # new
            self.assertTrue(x['sources'] and x['source_hashes'] and x['raw_ids'], x['id'])  # official, traceable
            self.assertEqual((x['status'], x['human_approved']), ('AWAITING_USER_RATIFICATION', False))
            self.assertNotIn('ART.943:INC', x['target_id'])
        self.assertEqual(self.m['NEW_QUALIFIED_CANDIDATE_RELATIONS'], len(self.q))
        self.assertEqual(self.m['INVALID_TARGETS_IN_QUALIFIED_OUTPUT'], 0)

    def test_tier_rules(self):
        for x in self.q:
            if x['tier'] == 'A':
                self.assertTrue(x['qualified_precedent'] and x['evidence_strength'] == 'STRONG', x['id'])
                self.assertFalse(set(x['flags']) & {'REDACAO_ALTERADA_APOS_JULGAMENTO', 'PRECEDENTE_PROVISORIO', 'DECISAO_CAUTELAR',
                                                    'TARGET_FALLBACK_TO_PARENT', 'PRECEDENTE_ANTERIOR_AO_CC2002'}, x['id'])
            self.assertNotEqual(x['evidence_strength'], 'WEAK', x['id'])
            self.assertNotIn('DISPOSITIVO_REVOGADO', x['flags'], x['id'])
        codes = collections.Counter(x['tier_code'] for x in self.rej)
        self.assertTrue(codes['DUPLICATE_PHYSICAL_BASELINE'] and codes['MENTION_ONLY_UNVERIFIED'])

    def test_no_older_code_leak(self):
        x = {(r['target_id'], r['precedent_id']) for r in self.q + self.rej}
        self.assertNotIn(('CC2002:ART.993', 'STJ:REPETITIVO:426'), x)                 # "art. 993 do Código Civil de 1916"
        self.assertNotIn(('CC2002:ART.1062', 'STJ:REPETITIVO:74'), x)

    def test_joint_judgments_counted_once(self):
        # twin acórdãos of one session (STJ 2ª Seção 12/03/2025, same ementa) and STF joint ADC/ADI: one relation each, not one per process
        twins = {x['precedent_id'] for x in self.q if x['target_id'] == 'CC2002:ART.1345'} & {'STJ:RESP:2082647', 'STJ:RESP:2100103', 'STJ:RESP:1929926'}
        self.assertLessEqual(len(twins), 1, twins)
        adc29 = [x for x in self.q if x['precedent_id'] == 'STF:ADC:29' and x['target_id'] == 'CC2002:ART.187']
        self.assertLessEqual(len(adc29), 1)

    def test_fallback_resolved_before_dedupe(self):
        # art. 723 has no parágrafo único in the index: '723:PAR.UNICO' falls back to '723' and must merge with the direct '723' link
        t = [x for x in self.q if x['precedent_id'] == 'STJ:REPETITIVO:1173' and x['target_id'] == 'CC2002:ART.723']
        self.assertLessEqual(len(t), 1)
        for x in self.q:
            if x['target_raw'] != x['target_id'] and not x['target_collapsed_from']:
                self.assertIn('TARGET_FALLBACK_TO_PARENT', x['flags'], x['id'])
                self.assertEqual(x['tier'], 'B', x['id'])

    def test_baselines_and_flags(self):
        m = self.m
        self.assertEqual((m['BASELINE_CC_PHYSICAL'], m['BASELINE_CF_PHYSICAL'], m['SD_CHANGED'], m['FIRMWARE_CHANGED'],
                          m['NEW_RELATIONS_PHYSICALLY_PUBLISHED'], m['RATIFICATION_PERFORMED']), ('49/39', '315/198', 'NO', 'NO', 0, 'NO'))
        self.assertEqual((m['CF_REGRESSION'], m['CC_J1_J2_REGRESSION'], m['SIMULATION_DUPLICATE_QUERY_KEYS']), (0, 0, 0))

    def test_checkpoint(self):
        ck = json.loads((OUT / 'CC_MASS_DISCOVERY_CHECKPOINT.json').read_text(encoding='utf-8'))
        for k, h in ck['OUTPUT_HASHES'].items():
            self.assertEqual(hashlib.sha256((OUT / k).read_bytes().replace(b'\r\n', b'\n')).hexdigest(), h, k)
        self.assertEqual(ck['QUALIFIED_COUNT'], len(self.q))
        self.assertFalse(ck['SOURCES_PENDING'])


if __name__ == '__main__':
    unittest.main()
