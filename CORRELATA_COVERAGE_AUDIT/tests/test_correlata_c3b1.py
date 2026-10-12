"""C3B.1 — root causes of the failed physical C3B test reproduced host-only, and the fixed candidate (never installed here)."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
ROOT = AUDIT.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
sys.path.insert(0, str(AUDIT / 'C3A/tools'))
import correlata_overlay as O  # noqa: E402
import build_export_run4_candidate as R4  # noqa: E402
import build_c3b_package as P  # noqa: E402
import build_c3b1_reports as B  # noqa: E402

OLD, NEW, BASE = B.card('C3B_INSTALLED'), B.card('C3B1'), B.card('BASELINE')
VIEW = R4.load(R4.OUT / 'legal_view/CF88_CORRELATA_LEGAL_VIEW.json')
READY = [e for e in VIEW['entries'] if e['device_state'] == 'DEVICE_READY']
READY_UNITS = {O.presentation_unit(e['target_id']) for e in READY}
AUDIT_DOC = json.loads((B.OUT_AUDIT).read_text(encoding='utf-8'))
DIFF = json.loads((P.OUT / 'C3B1_FILE_DIFF.json').read_text(encoding='utf-8'))


def expected_c(tid):
    return any(k in READY_UNITS for k in B.Card.keys(tid))


class RootCause1TargetFlags(unittest.TestCase):
    def test_seven_physical_cases_reproduced_on_installed_c3b(self):
        # (target, physical observation): the C3B card state (new REF/RELACOES, OLD TARGETS) shows exactly what Arthur saw
        cases = {'CF88:ART.158:PAR.1:INC.I': 'MISSING_FLAG', 'CF88:ART.158:PAR.1:INC.II': 'GHOST', 'CF88:ART.214': 'MISSING_FLAG',
                 'CF88:ART.214:INC.I': 'GHOST', 'CF88:ART.37:INC.II': 'GHOST', 'CF88:ART.37:PAR.3:INC.III': 'GHOST', 'CF88:ART.239:PAR.3': 'MISSING_FLAG'}
        for t, kind in cases.items():
            has_list = bool(OLD.open_correlatas(t))
            if kind == 'GHOST':
                self.assertTrue(OLD.available(t) and not has_list, t)            # `1` shown, pressing it opens nothing
            else:
                self.assertTrue(has_list and not OLD.available(t), t)            # relation exists, `1` never shown
            self.assertEqual(NEW.available(t), has_list if kind == 'MISSING_FLAG' else False, t)

    def test_c_flags_derived_from_device_ready_only(self):
        corr = {l.split('|')[0] for l in P.lines(NEW.f['payload']) if not l.startswith('#') and l.split('|')[1] == 'CORRELATA'
                and l.split('|')[2] == 'CURRENT_VISIBLE'}
        self.assertEqual({t for t, f in NEW.flags.items() if f[1] == 'C'}, corr)
        # the same rule rebuilds the BASELINE C flags from the baseline REF_PAYLOAD (rule = SD staging generator)
        corr0 = {l.split('|')[0] for l in P.lines(BASE.f['payload']) if not l.startswith('#') and l.split('|')[1] == 'CORRELATA'
                 and l.split('|')[2] == 'CURRENT_VISIBLE'}
        self.assertEqual({t for t, f in BASE.flags.items() if f[1] == 'C'}, corr0)

    def test_non_correlata_flags_unchanged(self):
        tf = DIFF['isolation']['targets_flags']
        self.assertEqual(tf['verdict'], 'CORRELATA_FLAG_CHANGES_ONLY')
        for k in ('ENTENDA_FLAGS_CHANGED', 'JURIS_FLAGS_CHANGED', 'WORK_REFERENCE_FLAGS_CHANGED', 'R_FLAGS_CHANGED', 'X_FLAGS_CHANGED', 'OTHER_FIELDS_CHANGED'):
            self.assertEqual(tf[k], 0, k)
        b, c = P.lines(BASE.f['targets']), P.lines(NEW.f['targets'])
        self.assertEqual(len(b), len(c))
        for x, y in zip(b, c):
            if x != y:
                fx, fy = x.split('|'), y.split('|')
                self.assertEqual((fx[:3], fx[3][0], fx[3][2:]), (fy[:3], fy[3][0], fy[3][2:]))

    def test_cf37_par3_inciii_stale_flag_removed(self):
        t = 'CF88:ART.37:PAR.3:INC.III'
        self.assertEqual(BASE.flags[t][1], 'C')                                   # old target advertised C
        self.assertFalse([e for e in READY if e['target_id'] == t])               # no DEVICE_READY CORRELATA
        self.assertEqual(NEW.flags[t][1], '-')                                    # candidate C = NO
        self.assertFalse(NEW.available(t))                                        # firmware would not offer 1 CORR.
        self.assertFalse([r for r in NEW.payload_rows(t) if r[1] == 'CORRELATA'])  # no orphan reference
        self.assertEqual(AUDIT_DOC['cf37_par3_inciii']['result'], 'PASS')


class RootCause2RelationIds(unittest.TestCase):
    def test_installed_c3b_had_shared_ids_and_wrong_route(self):
        self.assertIn('REL_D7475B8BEB5B6C53', AUDIT_DOC['c3b_installed_shared_relation_ids'])
        c = OLD.open_correlatas('CF88:ART.202:PAR.5')[0]
        self.assertEqual((c['row'][2], c['articles']), ('4', ['1']))              # physical test 2: §4 row, art. 1

    def test_reference_id_one_to_one(self):
        self.assertEqual(AUDIT_DOC['CORRELATA_REFERENCE_ID_RESOLUTION'], '1_TO_1')
        ids = [l.split('|')[4] for l in P.lines(NEW.f['payload']) if not l.startswith('#') and l.split('|')[1] == 'CORRELATA']
        self.assertTrue(ids)
        for i in ids:
            self.assertEqual(NEW.matches(i[i.find(':') + 1:i.find('@')]), 1, i)
        rows = [l.split('|')[5] for l in P.lines(NEW.f['relacoes']) if not l.startswith('#')]
        self.assertEqual(len(rows), len(set(rows)))

    def test_route_simulation_24(self):
        self.assertEqual(len(AUDIT_DOC['matrix']), 24)
        self.assertEqual(AUDIT_DOC['DEVICE_READY_ROUTE_SIMULATION'], '24/24')
        c = NEW.open_correlatas('CF88:ART.202:PAR.5')
        self.assertEqual([(x['row'][6], x['articles']) for x in c], [('EXT_LC108_2001', ['26'])])
        off = c[0]['offsets']['26']
        self.assertIn(off, B.headings()[('EXT_LC108_2001', '26')])


class SimulatedPhysical(unittest.TestCase):
    def test_expectations_derived_from_data(self):
        probes = AUDIT_DOC['simulated_physical_expectations']
        self.assertEqual(len(probes), 19)
        for s in probes:
            self.assertEqual(s['expected_c'], expected_c(s['target']), s['target'])
            self.assertEqual(NEW.available(s['target']), s['expected_c'], s['target'])
            self.assertEqual(bool(NEW.open_correlatas(s['target'])), s['expected_c'], s['target'])
            self.assertEqual(s['result'], 'PASS')
        for t, norm, art in (('CF88:ART.150:PAR.7', 'EXT_LC87_1996', '10'), ('CF88:ART.239:PAR.3', 'EXT_LEI7998_1990', '9')):
            c = [x for x in NEW.open_correlatas(t) if x['row'][6] == norm][0]
            self.assertEqual(c['articles'], [art])
            self.assertIn(c['offsets'][art], B.headings()[(norm, art)])


class Package(unittest.TestCase):
    def test_package_contents_and_rollback(self):
        cand = {p.relative_to(P.OUT / 'candidate/SD').as_posix(): p.read_bytes() for p in (P.OUT / 'candidate/SD').rglob('*') if p.is_file()}
        rb = {p.relative_to(P.OUT / 'rollback/SD').as_posix(): p.read_bytes() for p in (P.OUT / 'rollback/SD').rglob('*') if p.is_file()}
        self.assertEqual(set(cand), {f['path'] for f in DIFF['files']})
        self.assertIn('99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX', cand)
        phys = P.physical()
        for p in cand:
            self.assertNotEqual(cand[p], rb[p])
            self.assertEqual(hashlib.sha256(rb[p]).hexdigest(), phys[p]['sha256'])
            self.assertFalse(p.startswith(('99_LEX_V1/05_TEXT/', '99_LEX_V1/30_ENTENDA/', '99_LEX_V1/00_SYS/')))
        self.assertLessEqual(DIFF['firmware_cache']['used']['lookup_rows'], 64)
        self.assertLessEqual(DIFF['firmware_cache']['used']['norms'], 32)
        plan = (P.OUT / 'C3B1_PHYSICAL_TEST_PLAN.md').read_text(encoding='utf-8')
        self.assertIn('CF art. 37, § 3º, III', plan)

    def test_reproducible(self):
        trees = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as t:
                trees.append(P.build(Path(t) / 'pkg'))
        self.assertEqual(trees[0], trees[1])
        self.assertEqual(trees[0], P.tree(P.OUT))
        self.assertEqual(B.build(), B.build())
        for p, b in zip((B.OUT_AUDIT, B.OUT_FAIL, B.OUT_ROOT, B.OUT_FLAGS), B.build()):
            self.assertEqual(p.read_bytes().replace(b'\r\n', b'\n'), b, p.name)


if __name__ == '__main__':
    unittest.main()
