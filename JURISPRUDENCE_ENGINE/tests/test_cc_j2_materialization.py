"""CC-J2 materialization preflight: only the 20 ratified relations, CC-J1 and CF intact, shared targets merged, labels valid, candidate hashes."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
C = ENG / 'CC_J2_MATERIALIZATION_CANDIDATE'


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class CCJ2Preflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = load(C / 'host/PREFLIGHT_RESULT.json')
        cls.c = cls.r['checks']

    def test_up_to_date_and_history_untouched(self):
        for s in ('build_cc_j2_materialization.py', 'build_cc_j2_ratification_record.py', 'build_cc_j2.py', 'build_cc_j1_materialization.py'):
            p = subprocess.run([sys.executable, '-B', str(ENG / s), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((p.returncode, p.stdout.strip()), (0, 'UP_TO_DATE'), s + p.stderr[-1500:])

    def test_relations_and_targets(self):
        c = self.c
        self.assertEqual((c['APPROVED_RELATIONS'], c['DISTINCT_TARGETS_TOUCHED'], c['NEW_TARGETS'], c['CC2002'], c['PROJECTED_TOTAL_MULTINORM']),
                         (20, 18, 15, '49/39', '364/237'))
        self.assertEqual((c['REJECTED_MATERIALIZED'], c['INVALID_TARGETS'], c['INVALID_ART943_INC1_TARGET_CREATED'], c['TEMA1130_PROVISIONAL']),
                         (0, 0, 'NO', 'NO'))
        self.assertEqual((c['NEW_FICHAS'], c['REUSED_FICHA_NAMES'], c['DUPLICATED_FICHA_BYTES']), (17, ['STF_RG_498.TXT', 'STF_RG_809.TXT'], 0))
        self.assertTrue(all(v == 'PASS' for v in c['SHARED_TARGETS_MERGED'].values()))

    def test_simulation_and_regressions(self):
        c = self.c
        self.assertEqual((c['CCJ2_TARGETS_E2E'], c['CCJ2_RELATIONS_VISIBLE'], c['CCJ1_RELATIONS_PRESERVED'], c['CCJ1_TARGETS_PRESERVED']),
                         ('18/18', '20/20', '29/29', '24/24'))
        self.assertEqual((c['CCJ1_REGRESSION'], c['CF_REGRESSION'], c['CF_SEMANTIC'], c['CF_TARGETS'], c['DUPLICATE_QUERY_KEYS'],
                          c['LOOKUP_LOST_RELATIONS']), (0, 0, '315/315', '198/198', 0, 0))
        self.assertEqual((c['ART62'], c['TEMA932_CROSS_NORM']), (['RG TEMA 33', 'RG TEMA 1196'], 'PASS'))
        self.assertEqual((c['IAC_LABEL_SIMULATION'], c['REPETITIVO_STJ_LABEL_SIMULATION'], c['OUTRO_LABELS']), ('PASS', 'PASS', 0))
        self.assertEqual((c['IAC_PHYSICAL_VALIDATION'], c['REPETITIVO_STJ_PHYSICAL_VALIDATION'], c['SUMULA_STJ_PHYSICALLY_VALIDATED'],
                          c['DEVICE_STATUS_SOURCE']), ('NO', 'NO', 'YES', 'physical_status'))
        self.assertLess(c['CACHE_ENTRIES_USED'], c['CACHE_ENTRIES_MAX'] // 4)

    def test_fichas_content(self):
        f = lambda n: (C / 'candidate/SD/99_JURISPRUDENCIA_V2/03_CONTEUDO' / n).read_text(encoding='utf-8')  # noqa: E731
        self.assertIn('CPC/1973', f('STJ_IAC_1.TXT'))
        self.assertIn('HISTORICAL_BUT_RELEVANT', f('STJ_IAC_1.TXT'))
        self.assertTrue(f('STJ_REPETITIVO_381.TXT').split('\n\n')[1].startswith('INAPLICABILIDADE À COMPENSAÇÃO TRIBUTÁRIA'))
        self.assertIn('Tema 1236', f('STJ_SUMULA_655.TXT'))
        self.assertIn('Tema 1432', f('STJ_REPETITIVO_1130.TXT'))
        self.assertNotIn('provisório:', f('STJ_REPETITIVO_1130.TXT').lower())
        self.assertIn('ART943_INC1', f('STJ_SUMULA_642.TXT'))
        self.assertIn('art. 943\n', f('STJ_SUMULA_642.TXT'))
        self.assertIn('EXCEÇÃO', f('STJ_SUMULA_637.TXT'))
        self.assertFalse((C / 'candidate/SD/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_498.TXT').exists())        # reused, not duplicated

    def test_deploy_shape_and_manifest(self):
        d = load(C / 'host/DEPLOY_PLAN.json')
        self.assertEqual((d['additive_only'], len(d['files_to_add']), len(d['files_to_replace']), d['unexpected_path_collisions']), (False, 17, 4, []))
        self.assertTrue(all(k.startswith('99_JURISPRUDENCIA_V2/06_NORMALIZADO/') for k in d['files_to_replace']))
        m = load(C / 'SHA256_MANIFEST.json')
        self.assertEqual((m['deployed'], m['deploy_ready']), (False, False))
        for k, v in m['files'].items():
            self.assertEqual(hashlib.sha256((C / k).read_bytes()).hexdigest(), v['sha256'], k)
        rb = load(C / 'host/ROLLBACK_PLAN.json')
        self.assertEqual((rb['executed'], rb['expected_after']['CC'], rb['expected_after']['CF_ADCT']), (False, '29/24', '315/198'))
        self.assertEqual(len(rb['delete']) + len(rb['restore']), 21)


if __name__ == '__main__':
    unittest.main()
