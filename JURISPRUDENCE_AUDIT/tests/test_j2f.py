"""J2F — ratification 03–09, 301×261 reconciliation, normalization, RUN11 A/B, SD candidates A/B and isolation audit. Host-only."""
import datetime as dt
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
sys.path.insert(0, str(AUD))
import build_export_run11_juris_j2f as R11  # noqa: E402
import check_j2b_provisional as GATE  # noqa: E402

LINKING = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED')


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def run(script, *args):
    return subprocess.run([sys.executable, '-I', '-B', str(script), *args], capture_output=True, text=True, cwd=ROOT)


class J2F(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rat = load(AUD / 'J2_RATIFICATION_RECORD_03_09.json')
        cls.add = load(ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2F.json')
        cls.audit = load(AUD / 'J2F_CANDIDATES_HOST_ONLY/J2F_ISOLATION_AUDIT.json')['variants']

    def test_01_generators_up_to_date(self):
        for s in ('build_j2_ratification_record.py', 'build_baseline_reconciliation.py', 'apply_j2f_ratified_overlay.py',
                  'build_j2f_isolation_audit.py', 'render_j2_ratification_dossier.py'):
            r = run(AUD / s, '--check')
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), s)

    def test_02_ratification(self):
        r = self.rat
        self.assertEqual((r['TOTAL_RECOMMENDATIONS'], r['RATIFIED_DECISIONS'], r['UNRESOLVED_EXTERNAL']), (55, 54, 1))
        self.assertEqual([i['recommendation_id'] for i in r['items'] if not i['human_approved']], ['J0-BL-001'])
        self.assertEqual(r['provisional_items'], ['STF:ADI:5017', 'STF:ADPF:378', 'STF:RCL:84738'])
        self.assertEqual(r['PROVISIONAL_STATUS_PRESERVED'], 'YES')

    def test_03_baseline_reconciled(self):
        b = load(AUD / 'J2_BASELINE_RECONCILIATION.json')
        self.assertEqual((b['PHYSICAL_BASELINE_RELATIONS'], b['PHYSICAL_BASELINE_TARGETS'], b['PHYSICAL_BASELINE_RECONCILED']), (261, 160, 'PASS'))
        self.assertEqual(b['legacy_index']['LEGACY_JURIS_RECORDS'], 301)
        self.assertEqual(sum(v for k, v in b['decomposition_of_301'].items() if k.startswith('records_')), 301)
        arch = (AUD / 'JURIS_TYPE_ARCHITECTURE.md').read_text(encoding='utf-8')
        self.assertNotIn('301 vínculos', arch)
        self.assertNotIn('| Tipo | Vínculos |', arch)

    def test_04_normalization(self):
        new = [r for r in self.add['records'] if r['origin'] == 'J2F']
        n = self.add['normalization']
        self.assertEqual(n['NEW_DEVICE_RELATIONS_GENERIC_FW'], len(new))
        self.assertEqual(n['NEW_DEVICE_RELATIONS_CURRENT_FW'], sum(r['group'] == 'A' for r in new))
        self.assertEqual(len({(r['target_id'], r['source_id']) for r in new}), len(new))         # no duplicate relation
        status = {i['recommendation_id']: i for i in self.rat['items']}
        for r in new:
            for rid in r['ratified_decisions']:
                self.assertTrue(status[rid]['human_approved'] and status[rid]['decision'] in LINKING, rid)
            self.assertEqual(r['group'] == 'A', r['payload']['tipo'] in ('repercussao_geral', 'sumula_vinculante', 'adi'))
            self.assertNotIn('OUTRO', r['device_labels']['GENERIC'])
            if r['provisional']:
                self.assertRegex(r['payload']['numero'], r' \((CAUTELAR|PROVISÓRIA)\)$')
        linked = {rid for r in new for rid in r['ratified_decisions']}
        self.assertEqual(linked, {i['recommendation_id'] for i in self.rat['items'] if i['human_approved'] and i['decision'] in LINKING})
        self.assertFalse(any('STJ:SUMULA:403' in r['source_id'] for r in self.add['records']))
        self.assertEqual(self.add['provisional_gate']['result'], 'PASS')

    def test_05_run11_reproducible(self):
        for v, out in R11.OUT.items():
            with tempfile.TemporaryDirectory() as t:
                R11.build(t, v)
                self.assertEqual((Path(t) / 'SHA256SUMS.txt').read_bytes(), (out / 'SHA256SUMS.txt').read_bytes().replace(b'\r\n', b'\n'), v)

    def test_06_candidates(self):
        for v, name in (('A', 'J2_CURRENT_FW_CANDIDATE'), ('B', 'J2_GENERIC_FW_CANDIDATE')):
            pkg = AUD / 'J2F_CANDIDATES_HOST_ONLY' / name
            m = load(pkg / 'J2F_PACKAGE_MANIFEST.json')
            self.assertEqual((m['status'], m['physical_approved'], m['card_touched'], m['device_flashed']), ('HOST_ONLY_CANDIDATE', False, False, False))
            self.assertTrue(m['physical_baseline_reproduced'] and m['byte_identical_rebuild'] and m['legacy_append_only'] and m['device_manifest_matches_package'])
            self.assertTrue(m['temas_367_387_fichas_untouched'])
            for f in m['file_diff'] + m['file_additions']:
                rel = f['path'].lstrip('/')
                self.assertEqual(hashlib.sha256((pkg / 'candidate/SD' / rel).read_bytes()).hexdigest(), f['after_sha256'], rel)
            for f in m['file_diff']:
                rel = f['path'].lstrip('/')
                self.assertEqual(hashlib.sha256((pkg / 'rollback/SD' / rel).read_bytes()).hexdigest(), f['before_sha256'], rel)
            self.assertEqual(m['firmware_files'] is not None, v == 'B')

    def test_07_audit(self):
        for v, want in (('A', (299, 186)), ('B', (315, 198))):
            x = self.audit[v]['verdict']
            self.assertEqual((x['JURIS_RELATIONS'], x['JURIS_TARGETS']), want)
            for k in ('LEGACY_261_RELATIONS_UNCHANGED', 'BASE_IS_PHYSICAL_261_160', 'ONLY_RATIFIED_RELATIONS_ADDED', 'J_FLAG_EQUALS_VISIBLE_JURIS',
                      'LEGACY_PREFIX_IDENTICAL', 'FIRMWARE_CACHE_RULES_HOLD', 'ALL_NEW_RELATIONS_RESOLVE_WITH_FICHA', 'ALL_IDS_ACCEPTED_BY_TARGET_FIRMWARE',
                      'NO_OUTRO_LABEL_ON_TARGET_FIRMWARE', 'STJ_SUMULA_403_ABSENT', 'TEMAS_367_387_FICHAS_UNTOUCHED', 'REGRESSION_LEGACY_ITEMS_PRESERVED',
                      'REGRESSION_TARGETS_WITHOUT_NEW_RELATIONS_IDENTICAL', 'FIRMWARE_LIMITS_OK'):
                self.assertTrue(x[k], (v, k))
            self.assertEqual((x['ROWS_REMOVED'], x['CORRELATA_RELATION_SET_CHANGED'], x['WORK_REFERENCE_SET_CHANGED'], x['ENTENDA_SET_CHANGED']), (0, 0, 0, 0))
            self.assertEqual({k: x[f'{k}_FLAGS_CHANGED'] for k in 'ECWRX'}, dict.fromkeys('ECWRX', 0))
        self.assertEqual(self.audit['A']['verdict']['OUTRO_LABELS_IF_SHOWN_WITH_CURRENT_FIRMWARE'], [])
        self.assertEqual(self.audit['B']['verdict']['GENERIC_TYPES_LABELS_CORRECT'], 'PASS')
        self.assertEqual(sorted(self.audit['B']['verdict']['PROVISIONAL_SOURCES_IN_CANDIDATE']), self.audit['B']['verdict']['PROVISIONAL_REGISTRY_ITEMS'])

    def test_08_provisional_gate(self):
        res = GATE.check(dt.date(2026, 10, 17), AUD / 'J2_PROVISIONAL_REGISTRY.json')
        self.assertTrue(res and all(r['result'] == 'PASS' for r in res))


if __name__ == '__main__':
    unittest.main()
