"""J1.4 — ratified J1.3 decisions materialized host-only (RUN7): 4 links removed from wrong targets, 3 relocated, frozen layers intact."""
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
import build_export_run7_juris_j1_4 as R7  # noqa: E402

BASE = ROOT / 'JURISPRUDENCE_AUDIT/J1_1_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1'
REMOVED = {'JURISPRUDENCE:STF:SV:17:CF88:100:-:-:-@CF88:ART.100:PAR.1', 'JURISPRUDENCE:STF:RG:147:CF88:100:-:-:-@CF88:ART.100:PAR.1',
           'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40:PAR.4', 'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40:PAR.5'}
ADDED = {'JURISPRUDENCE:STF:SV:17:CF88:100:-:-:-@CF88:ART.100:PAR.5', 'JURISPRUDENCE:STF:RG:147:CF88:100:-:-:-@CF88:ART.100:PAR.5',
         'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    return [l.split('|') for l in Path(p).read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')]


class J14(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = R7.OUT / 'device_ready'
        cls.pb, cls.pc = rows(BASE / '20_REFERENCES/REF_PAYLOAD.IDX'), rows(cls.dev / 'REF_PAYLOAD.IDX')

    def test_generators_up_to_date(self):
        for s in (AUD / 'apply_j1_4_overlays.py', AUD / 'build_j1_4_isolation_audit.py', AUD / 'build_j1_3_external_review.py'):
            r = subprocess.run([sys.executable, '-I', '-B', str(s), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), s.name)

    def test_run7_reproducible(self):
        with tempfile.TemporaryDirectory() as t:
            R7.build(t)
            for line in (R7.OUT / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
                h, name = line.split('  ', 1)
                self.assertEqual(sha(Path(t) / name), h, name)
                self.assertEqual(sha(R7.OUT / name), h, name)

    def test_exact_delta(self):
        b, c = {tuple(r) for r in self.pb}, {tuple(r) for r in self.pc}
        self.assertEqual({r[4] for r in b - c}, REMOVED)
        self.assertEqual({r[4] for r in c - b}, ADDED)
        self.assertTrue(all(r[1] == 'JURISPRUDENCE' for r in (b - c) | (c - b)))
        v = [r for r in self.pc if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
        self.assertEqual((len(v), len({r[0] for r in v})), (256, 156))
        self.assertEqual({r[5] for r in self.pc if r[0] == 'CF88:ART.16' and r[1] == 'JURISPRUDENCE'}, {'STF:RG:367', 'STF:RG:387'})   # KEEP_BOTH

    def test_temporal_note_and_same_key(self):
        exp = json.loads((self.dev / 'CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))
        links = {l['reference_id']: l for ls in exp['references'].values() for l in ls}
        for rid in ADDED:
            l = links[rid]
            self.assertEqual(l['migration'], 'RELOCATED_J1_4')
            self.assertTrue(l['payload']['nota_temporal'] and l['provenance']['relocation']['temporal_note'])
            self.assertEqual(rid.split(':', 1)[1].rsplit('@', 1)[0], l['source_reference_id'])
        self.assertIn('redação originária', links['JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40']['payload']['nota_temporal'])

    def test_flags_and_isolation(self):
        tb, tc = {r[0]: r for r in rows(BASE / '10_TARGETS/CF88_TARGETS.IDX')}, {r[0]: r for r in rows(self.dev / 'CF88_TARGETS.IDX')}
        self.assertEqual({t for t in tb if tb[t] != tc[t]}, {'CF88:ART.100:PAR.1'})
        self.assertEqual((tb['CF88:ART.100:PAR.1'][3], tc['CF88:ART.100:PAR.1'][3]), ('E-J-RX', 'E---RX'))
        v = json.loads((AUD / 'J1_4_ISOLATION_AUDIT.json').read_text(encoding='utf-8'))['verdict']
        for k in ('CORRELATA_RELATION_SET_CHANGED', 'WORK_REFERENCE_SET_CHANGED', 'C_FLAGS_CHANGED', 'E_FLAGS_CHANGED', 'W_FLAGS_CHANGED',
                  'R_FLAGS_CHANGED', 'X_FLAGS_CHANGED', 'NON_J_TARGET_FLAGS_CHANGED'):
            self.assertEqual(v[k], 0, k)
        for k in ('JURIS_REMOVED_EQUALS_RATIFIED_4', 'JURIS_ADDED_EQUALS_RELOCATIONS_3', 'RELOCATED_KEYS_IN_LEGACY_IDX', 'J_FLAG_EQUALS_VISIBLE_JURIS',
                  'CORRELATA_FILES_BYTE_IDENTICAL', 'HISTORICAL_HIDDEN_JURIS_UNCHANGED'):
            self.assertTrue(v[k], k)


if __name__ == '__main__':
    unittest.main()
