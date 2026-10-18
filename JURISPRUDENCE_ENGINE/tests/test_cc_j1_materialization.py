"""CC-J1 materialization preflight: the host-only deploy candidate holds exactly the ratified relations, adds files only, keeps CF 315/198."""
import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
C = ENG / 'CC_J1_MATERIALIZATION_CANDIDATE'
sys.path.insert(0, str(ROOT / 'JURISPRUDENCE_AUDIT'))
import build_j2_batch as G  # noqa: E402


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class Preflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = load(C / 'host/PREFLIGHT_RESULT.json')
        cls.c = cls.r['checks']

    def test_reproducible_and_manifest(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(ENG / 'build_cc_j1_materialization.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))
        m = load(C / 'SHA256_MANIFEST.json')
        disk = {os.path.relpath(os.path.join(a, f), C).replace(os.sep, '/') for a, _, fs in os.walk(C) for f in fs}
        self.assertEqual(disk, set(m['files']) | {'SHA256_MANIFEST.json'})
        for k, v in m['files'].items():
            self.assertEqual(hashlib.sha256((C / k).read_bytes()).hexdigest(), v['sha256'], k)

    def test_authority_counts_and_exclusions(self):
        c = self.c
        self.assertEqual((c['CCJ1_RATIFICATION_RECORD_VALID'], c['APPROVED_PROPOSALS'], c['PENDING_PROPOSALS'], c['NOT_APPROVED_PROPOSALS']), ('PASS', 22, 2, 6))
        rec = load(ENG / 'CC_J1_RATIFICATION_RECORD.json')
        self.assertEqual((c['APPROVED_RELATIONS'], c['APPROVED_TARGETS'], c['APPROVED_PRECEDENTS']),
                         (rec['counts']['NORMALIZED_RELATIONS_APPROVED'], rec['counts']['DISTINCT_CC_TARGETS_APPROVED'], rec['counts']['DISTINCT_PRECEDENTS_APPROVED']))
        self.assertEqual((c['PENDING_MATERIALIZED'], c['REJECTED_MATERIALIZED']), (0, 0))
        recs = (C / 'candidate/SD/99_JURISPRUDENCIA_V2/06_NORMALIZADO/JURISPRUDENCIA.IDX').read_text(encoding='utf-8')
        cc = [l.split('|') for l in recs.split('\n') if ':CC2002:' in l]
        self.assertEqual(sorted((l[0].split(':CC2002:')[0], l[0]) for l in cc) and len(cc), c['APPROVED_RELATIONS'])
        for pid in ['STF:RG:1194', 'STJ:SUMULA:609', 'STF:RG:526', 'STJ:SUMULA:371', 'STJ:SUMULA:451', 'STJ:SUMULA:543', 'STJ:SUMULA:550', 'STJ:SUMULA:595']:
            self.assertFalse([l for l in cc if l[6] == pid], pid)
        ids = {l[6] for l in cc}
        self.assertEqual(sorted(x.split(':CC2002:')[1] for x in (l[0] for l in cc) if x.startswith('STJ:SUMULA:476')), ['662:-:-:-', '917:-:-:-'])
        self.assertIn('STF:ADI:6792-7055', ids)

    def test_quality_gates(self):
        c = self.c
        for k in ('INVALID_TARGETS', 'MISSING_TARGETS', 'DUPLICATE_QUERY_KEYS', 'LOOKUP_LOST_RELATIONS', 'FICHA_ID_COLLISIONS', 'DUPLICATED_SHARED_FICHAS',
                  'UNKNOWN_TYPE_LABELS', 'NON_J_FLAG_CHANGES', 'EXISTING_CARD_FILES_MODIFIED'):
            self.assertEqual(c[k], 0, k)
        self.assertEqual((c['TOTAL_FICHAS'], c['NEW_FICHAS'], c['SHARED_FICHAS'], c['SHARED_FICHA_TEMA932']), (20, 19, 1, 'REUSED'))
        self.assertEqual((c['CC_TARGETS_E2E'], c['CC_RELATIONS_VISIBLE'], c['CF_REGRESSION']), ('24/24', '29/29', 'PASS'))
        self.assertEqual((c['CF_BASELINE'], c['CC2002_RELATIONS'], c['CC2002_TARGETS']), ('315/198', 29, 24))
        self.assertEqual(c['J_FLAG_CHANGES'], 24)
        self.assertLess(c['CACHE_ENTRIES_USED'], c['CACHE_ENTRIES_MAX'] // 4)
        self.assertFalse((C / 'candidate/SD/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_932.TXT').exists())        # shared ficha reused, not copied
        self.assertFalse([p for p in (C / 'candidate/SD').rglob('*') if '05_INDICES_ESP32' in str(p) or '99_LEX_V1' in str(p)])
        d = load(C / 'host/DIFF_REPORT.json')
        self.assertEqual((d['UNEXPECTED_DIFFS'], d['files_modified'], d['files_removed']), (0, [], []))

    def test_special_fichas(self):
        f = C / 'candidate/SD/99_JURISPRUDENCIA_V2/03_CONTEUDO'
        self.assertIn('art. 186; art. 927', (f / 'STJ_SUMULA_403.TXT').read_text(encoding='utf-8'))
        self.assertIn('JULGAMENTO CONJUNTO', (f / 'STF_ADI_6792-7055.TXT').read_text(encoding='utf-8'))
        self.assertFalse((f / 'STF_ADI_6792.TXT').exists() or (f / 'STF_ADI_7055.TXT').exists())
        self.assertIn('DPVAT', (f / 'STJ_SUMULA_405.TXT').read_text(encoding='utf-8'))
        self.assertIn('1916', (f / 'STJ_SUMULA_547.TXT').read_text(encoding='utf-8'))
        for t in ('STF_RG_498.TXT', 'STF_RG_809.TXT'):
            self.assertIn('declarado inconstitucional', (f / t).read_text(encoding='utf-8'))
        for p in f.glob('*.TXT'):
            self.assertNotIn('SIMULAÇÃO', p.read_text(encoding='utf-8'))

    def test_cf_baseline_untouched(self):
        self.assertEqual(hashlib.sha256(G.J2I_PAYLOAD.read_bytes()).hexdigest(), G.J2I_PAYLOAD_SHA)
        vis = G.j2i_baseline()
        self.assertEqual((len(vis), len({r[0] for r in vis})), (315, 198))


if __name__ == '__main__':
    unittest.main()
