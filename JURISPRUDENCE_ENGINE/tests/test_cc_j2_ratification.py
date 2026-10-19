"""CC-J2 human ratification: 30 reconciled, 19 approved, 11 not approved, final targets as decided by the user, baselines untouched."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
sys.path.insert(0, str(ROOT / 'JURISPRUDENCE_AUDIT'))
import juris_types as JT  # noqa: E402


class CCJ2Ratification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads((ENG / 'CC_J2_RATIFICATION_RECORD.json').read_text(encoding='utf-8'))
        cls.by = {it['precedent']: it for it in cls.r['items']}

    def t(self, precedent):
        it = self.by[precedent]
        self.assertTrue(it['human_approved'], precedent)
        return it['final_targets']

    def test_up_to_date(self):
        for s in ('build_cc_j2_ratification_record.py', 'build_cc_j2_final_dossier.py', 'build_cc_j2.py'):
            p = subprocess.run([sys.executable, '-B', str(ENG / s), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((p.returncode, p.stdout.strip()), (0, 'UP_TO_DATE'), s + p.stderr[-1500:])

    def test_counts(self):
        c = self.r['counts']
        self.assertEqual((c['TOTAL_PROPOSALS'], c['APPROVED_PROPOSALS'], c['NOT_APPROVED'], c['PENDING']), (30, 19, 11, 0))
        self.assertEqual(len(self.r['items']), 30)
        self.assertEqual(c['APPROVED_RELATIONS'], len(self.r['approved_relations']))
        self.assertEqual((self.r['materialized'], self.r['deployed'], self.r['physical_package']), (False, False, False))
        for it in self.r['items']:
            self.assertFalse(it['materialized'])
            if it['final_dossier']['group'] == 'RED':                                   # no RED materializable
                self.assertEqual((it['human_approved'], it['final_targets']), (False, []), it['id'])
                self.assertTrue(it['reopen'])

    def test_final_targets(self):
        self.assertEqual(self.t('STJ:REPETITIVO:1130'), ['CC2002:ART.76:PAR.UNICO'])
        it = self.by['STJ:REPETITIVO:1130']
        self.assertFalse(it['provisional'])
        self.assertIn('STJ_SOURCE_STATUS_STALE = YES', it['editorial_flags'])
        self.assertIn('STF_TEMA1432_RESOLVED_CONSTITUTIONAL_RISK = YES', it['editorial_flags'])
        self.assertEqual(self.r['counts']['PROVISIONAL_APPROVED'], 0)
        self.assertEqual(self.t('STJ:SUMULA:642'), ['CC2002:ART.943'])
        self.assertIn('ART943_INC1 -> ART943', ' '.join(self.by['STJ:SUMULA:642']['editorial_flags']))
        self.assertEqual(self.t('STJ:REPETITIVO:639'), ['CC2002:ART.206:PAR.5:INC.I'])
        self.assertEqual(self.t('STJ:REPETITIVO:610'), ['CC2002:ART.206:PAR.3:INC.IV'])
        self.assertEqual(self.t('STJ:SUMULA:619'), ['CC2002:ART.1208', 'CC2002:ART.1255'])
        self.assertEqual(self.t('STJ:IAC:1'), ['CC2002:ART.202:PAR.UNICO'])
        self.assertIn('HISTORICAL_BUT_RELEVANT', self.by['STJ:IAC:1']['editorial_flags'])
        self.assertEqual(self.t('STJ:REPETITIVO:1019'), ['CC2002:ART.1238:PAR.UNICO'])
        self.assertEqual(self.t('STJ:SUMULA:637'), ['CC2002:ART.1210:PAR.2'])
        self.assertEqual(self.t('STJ:SUMULA:655'), ['CC2002:ART.1641:INC.II'])
        self.assertIn('SUBJECT_TO_TEMA_1236_STF', self.by['STJ:SUMULA:655']['editorial_flags'])
        self.assertEqual(self.t('STJ:REPETITIVO:381'), ['CC2002:ART.354'])
        self.assertEqual(self.by['STJ:REPETITIVO:381']['relation'], 'EXCLUSION_CONTEXT')
        self.assertIn('EXCLUSION_CONTEXT', self.by['STJ:REPETITIVO:381']['editorial_flags'])

    def test_baselines_and_device(self):
        b, d = self.r['baselines'], self.r['device']
        self.assertEqual((b['CC_PHYSICAL_BASELINE'], b['CF_ADCT_NORMALIZED_RELATIONS']), ('29/24', 315))
        self.assertTrue(b['CF_PHYSICAL_BASELINE'].startswith('315/198'))
        self.assertEqual(json.loads((ENG / 'CC_J1_PHYSICAL_DEPLOY/CC_J1_PHYSICAL_VALIDATION.json').read_text(encoding='utf-8'))['RELATIONS'], 29)
        self.assertEqual((d['SUMULA_STJ_PHYSICALLY_VALIDATED'], d['IAC_SUPPORTED_ARCHITECTURALLY'], d['IAC_PHYSICALLY_VALIDATED']), ('YES', 'YES', 'NO'))
        self.assertEqual(JT.physical_status('SUMULA_STJ'), 'VALIDATED')
        self.assertEqual(JT.device_status('SUMULA_STJ'), 'FIRMWARE_LABEL_EXISTS_NOT_PHYSICALLY_VALIDATED')    # frozen batches reproducible
        self.assertEqual(sorted(self.r['counts']['FICHAS_REUSED_FROM_CARD']), ['STF_RG_498.TXT', 'STF_RG_809.TXT'])


if __name__ == '__main__':
    unittest.main()
