"""J1.1 — removal of the 20 ratified jurisprudence false positives (RUN6 candidate, host-only). Frozen layers must be byte/semantically intact."""
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
import build_export_run6_juris_j1 as R6  # noqa: E402

EXCL = ROOT / 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J1.json'
BASE = ROOT / 'REFERENCE_COVERAGE_AUDIT/REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1'
LOST = {'CF88:ART.1', 'CF88:ART.3', 'CF88:ART.7', 'CF88:ART.19', 'CF88:ART.47', 'CF88:ART.96', 'CF88:ART.14:PAR.2', 'CF88:ART.41:PAR.1',
        'CF88:ART.43:CAPUT', 'CF88:ART.43:PAR.1', 'CF88:ART.48:INC.III', 'CF88:ART.98:CAPUT', 'CF88:ART.98:PAR.2'}
PENDING = {  # EXTERNAL_REVIEW_REQUIRED (4) + DUPLICATE_OR_REDUNDANT (1): must remain published
    'JURISPRUDENCE:STF:SV:17:CF88:100:-:-:-@CF88:ART.100:PAR.1', 'JURISPRUDENCE:STF:RG:147:CF88:100:-:-:-@CF88:ART.100:PAR.1',
    'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40:PAR.4', 'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40:PAR.5',
    'JURISPRUDENCE:STF:RG:387:CF88:16:-:-:-@CF88:ART.16'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    return [l.split('|') for l in Path(p).read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')]


def run(*a):
    return subprocess.run([sys.executable, '-I', '-B', *map(str, a)], capture_output=True, text=True, cwd=ROOT)


class J11(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = R6.OUT / 'device_ready'
        cls.excl = json.loads(EXCL.read_text(encoding='utf-8'))
        cls.pb, cls.pc = rows(BASE / '20_REFERENCES/REF_PAYLOAD.IDX'), rows(cls.dev / 'REF_PAYLOAD.IDX')

    def test_generators_up_to_date(self):
        for s in (AUD / 'apply_j1_exclusions.py', AUD / 'build_j1_1_isolation_audit.py', AUD / 'build_j1_risk_review.py', AUD / 'build_j0_diagnostic_audit.py'):
            r = run(s, '--check')
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), s.name)

    def test_overlay_is_the_ratified_20(self):
        d = json.loads((AUD / 'J1_DECISIONS.json').read_text(encoding='utf-8'))
        rem = {x['relation_id'] for x in d['decisions'] if x['decision'] == 'REMOVE_FALSE_POSITIVE'}
        self.assertEqual({r['reference_id'] for r in self.excl['records']}, rem)
        self.assertEqual((self.excl['total'], self.excl['ratification']['statement']), (20, 'J1_REMOVE_FALSE_POSITIVE_APPROVED = 20/20'))
        self.assertTrue(all(r['status'] == 'MATERIAL_MISMATCH_EXCLUDED' for r in self.excl['records']))

    def test_run6_reproducible(self):
        with tempfile.TemporaryDirectory() as t:
            R6.build(t)
            for line in (R6.OUT / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
                h, name = line.split('  ', 1)
                self.assertEqual(sha(Path(t) / name), h, name)
                self.assertEqual(sha(R6.OUT / name), h, name)

    def test_only_the_20_removed_nothing_added_or_relocated(self):
        b, c = {tuple(r) for r in self.pb}, {tuple(r) for r in self.pc}
        self.assertTrue(c <= b)
        gone = b - c
        self.assertEqual({r[4] for r in gone}, {r['reference_id'] for r in self.excl['records']})
        self.assertTrue(all(r[1] == 'JURISPRUDENCE' for r in gone))
        self.assertFalse([r for r in c if r[0].startswith('ADCT:') and r[1] == 'JURISPRUDENCE' and r not in b])   # no ADCT relocation
        self.assertTrue(PENDING <= {r[4] for r in c})                                                            # pending stay published

    def test_counts(self):
        v = [r for r in self.pc if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
        self.assertEqual((len(v), len({r[0] for r in v})), (257, 157))
        self.assertEqual(sum(r[1] == 'WORK_REFERENCE' for r in self.pc), 124)
        self.assertEqual(sum(r[1] == 'CORRELATA' for r in self.pc), 26)

    def test_flags(self):
        tb, tc = {r[0]: r for r in rows(BASE / '10_TARGETS/CF88_TARGETS.IDX')}, {r[0]: r for r in rows(self.dev / 'CF88_TARGETS.IDX')}
        diff = {t for t in tb if tb[t] != tc[t]}
        self.assertEqual(diff, LOST)
        for t in diff:
            self.assertEqual((tb[t][3][2], tc[t][3][2]), ('J', '-'), t)
            self.assertEqual(tb[t][3][:2] + tb[t][3][3:], tc[t][3][:2] + tc[t][3][3:], t)      # E/C/W/R/X untouched
            self.assertEqual(tb[t][:3], tc[t][:3], t)

    def test_isolation_verdict(self):
        v = json.loads((AUD / 'J1_1_ISOLATION_AUDIT.json').read_text(encoding='utf-8'))['verdict']
        for k in ('CORRELATA_RELATION_SET_CHANGED', 'WORK_REFERENCE_SET_CHANGED', 'JURIS_ADDED_OR_ALTERED', 'C_FLAGS_CHANGED', 'E_FLAGS_CHANGED',
                  'W_FLAGS_CHANGED', 'R_FLAGS_CHANGED', 'X_FLAGS_CHANGED', 'NON_J_TARGET_FLAGS_CHANGED'):
            self.assertEqual(v[k], 0, k)
        for k in ('JURIS_REMOVED_EQUALS_RATIFIED_20', 'J_FLAG_CHANGES_ONLY_LOST_LAST_LINK', 'J_FLAG_EQUALS_VISIBLE_JURIS', 'CORRELATA_FILES_BYTE_IDENTICAL',
                  'HISTORICAL_HIDDEN_JURIS_UNCHANGED'):
            self.assertTrue(v[k], k)
        self.assertEqual((v['JURIS_REMOVED'], v['J_FLAGS_CHANGED']), (20, 13))

    def test_frozen_inputs_untouched(self):
        for p, h in ((ROOT / 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json', None),):
            r = subprocess.run(['git', 'diff', '--quiet', 'af8f68d', '--', str(p.relative_to(ROOT))], cwd=ROOT)
            self.assertEqual(r.returncode, 0, p.name)


if __name__ == '__main__':
    unittest.main()
