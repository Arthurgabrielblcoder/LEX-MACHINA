"""CF88_CORRELATA_C1B: Batch02 independent review, Batch03, Batch04 and the 106/106 HIGH closure — complete, founded, deterministic, NOT applied."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
ROOT = AUDIT.parent
sys.path.insert(0, str(AUDIT / 'tools'))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_c1b_high_batch01 as B1  # noqa: E402
import build_c1b_high_batch02 as B2  # noqa: E402
import build_c1b_high_batch03 as B3  # noqa: E402
import build_c1b_high_batch04 as B4  # noqa: E402
import build_c1b_high_consolidated as C  # noqa: E402
import target_id as T  # noqa: E402

OUT3, OUT4, OUTC = B3.build(), B4.build(), C.build()
IN3, DEC3 = json.loads(OUT3[0]), json.loads(OUT3[1])
IN4, DEC4 = json.loads(OUT4[0]), json.loads(OUT4[1])
CONS = json.loads(OUTC[0])
HIGH = [x['candidate_id'] for x in json.loads(B1.QUEUE.read_text(encoding='utf-8'))['HIGH']]
OPERATIONAL = ('LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json', 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json',
               'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json', 'LEGAL_TARGET_ID/derived/export_test/run3/REF_LOOKUP.IDX',
               'LEGAL_TARGET_ID/derived/export_test/run3/REF_PAYLOAD.IDX', 'LEGAL_TARGET_ID/derived/export_test/run3/CF88_REFERENCES_EXPORT.json')


def ids_of(path):
    return json.loads(path.read_text(encoding='utf-8'))['selection']['candidate_ids']


class Determinism(unittest.TestCase):
    def test_all_artifacts_reproduce_and_are_committed(self):
        self.assertEqual(B3.build(), OUT3)
        self.assertEqual(B4.build(), OUT4)
        self.assertEqual(C.build(), OUTC)
        for paths, out in (((B3.OUT_IN, B3.OUT_DEC, B3.OUT_MD), OUT3), ((B4.OUT_IN, B4.OUT_DEC, B4.OUT_MD), OUT4), ((C.OUT_JSON, C.OUT_MD), OUTC),
                           ((B2.OUT_IN, B2.OUT_DEC, B2.OUT_MD), B2.build())):
            for p, b in zip(paths, out):
                self.assertEqual(p.read_bytes().replace(b'\r\n', b'\n'), b, p.name)


class Selections(unittest.TestCase):
    def test_batch03_is_the_next_30_original_high(self):
        ids = IN3['selection']['candidate_ids']
        self.assertEqual(len(ids), 30)
        self.assertEqual(len(set(ids)), 30)
        self.assertTrue(set(ids) <= set(HIGH))
        self.assertFalse(set(ids) & (set(ids_of(B1.OUT_IN)) | set(ids_of(B2.OUT_IN))))
        _, pool, _ = B3.remaining_pool()
        self.assertEqual([x['candidate_id'] for x in pool[:30]], ids)            # structural order, nothing skipped

    def test_batch04_is_exactly_all_remaining(self):
        ids = IN4['selection']['candidate_ids']
        self.assertEqual(len(ids), 17)
        self.assertEqual(len(set(ids)), 17)
        done = set(ids_of(B1.OUT_IN)) | set(ids_of(B2.OUT_IN)) | set(ids_of(B3.OUT_IN))
        self.assertFalse(set(ids) & done)
        self.assertEqual(set(ids) | done, set(HIGH))
        self.assertEqual(IN4['selection']['remaining_after'], [])

    def test_pairs_not_duplicated(self):
        for doc in (DEC3, DEC4):
            pairs = [(d['target'], d['norm_key']) for d in doc['decisions']]
            self.assertEqual(len(pairs), len(set(pairs)))


class Decisions(unittest.TestCase):
    def test_requirements_batch03_04(self):
        for doc in (DEC3, DEC4):
            self.assertEqual(sum(doc['summary']['decisions'].values()), len(doc['decisions']))
            for d in doc['decisions']:
                self.assertIn(d['legal_decision'], B1.DECISIONS)
                self.assertFalse(d['applied'])
                self.assertIn(d['temporal']['temporal_status'], B3.TEMPORAL)
                self.assertGreater(len(d['legal_analysis']), 60, d['candidate_id'])
                self.assertTrue(all(s in B3.SCOPES for s in d['scope']))
                if d['legal_decision'] in ('APPROVE', 'ADJUST'):
                    self.assertTrue(d['official_sources'])
                    for s in d['official_sources']:
                        self.assertRegex(s['url'], r'^https://www\.planalto\.gov\.br/ccivil_03/')
                        self.assertRegex(s['sha256'], r'^[0-9a-f]{64}$')
                    self.assertIn(d['relation_type_final'], B1.RELATION_TYPES)
                    self.assertTrue(T.validate_target_id(d['target_final'])[0], d['target_final'])
                    self.assertTrue(d['route'] and d['device_route_status'])
                    if d['legal_decision'] == 'ADJUST':
                        self.assertTrue(d['relation_type_final'] != d['c0_relation_type'] or d['target_final'] != d['target'])
                    if d['target_final'] != d['target']:
                        # no automatic inheritance: a retarget only goes DOWN to a more specific device of the same article (or stays)
                        self.assertTrue(d['target_final'].startswith(d['target'] + ':'), d['candidate_id'])
                    if d['relation_type_final'] == 'IMPLEMENTA':
                        self.assertTrue(d['scope'])
                else:
                    self.assertIsNone(d['target_final'])
                if d['legal_decision'] in ('HOLD', 'NEEDS_SOURCE'):
                    self.assertTrue(d['notes'])
                if d['temporal']['temporal_status'] == 'VACATIO_LEGIS' and d['legal_decision'] in ('APPROVE', 'ADJUST'):
                    self.assertIn('TEMPORAL_DEVICE_BLOCK', d['device_flags'])

    def test_amending_laws_not_promoted(self):
        for doc in (DEC3, DEC4):
            for d in doc['decisions']:
                if 'ALTERADORA_INCORPORADA' in (d['notes'] or ''):
                    self.assertEqual(d['legal_decision'], 'REJECT')

    def test_backlog_entries_complete(self):
        for doc in (DEC3, DEC4):
            for b in doc['NEW_CANDIDATE_BACKLOG']:
                self.assertEqual(b['status'], 'BACKLOG_NOT_DECIDED')
                for k in ('target_id', 'norm', 'basis', 'origin', 'suggested_priority', 'reason_not_decided'):
                    self.assertTrue(b[k], k)
                self.assertIn(b['origin'], HIGH)                                   # discovered while reviewing an original HIGH


class Batch02IndependentReview(unittest.TestCase):
    def test_two_adjustments_counts_unchanged(self):
        doc = json.loads(B2.build()[1])
        ir = doc['independent_review']
        self.assertEqual(ir['verdict'], 'APPROVED_WITH_TWO_ADJUSTMENTS')
        s = doc['summary']['decisions']
        self.assertEqual((s['APPROVE'] + s['ADJUST'], s['REJECT'], s['HOLD']), (22, 8, 0))
        by = {d['candidate_id']: d for d in doc['decisions']}
        d = by['CORRC0-4A80B12218AA']
        self.assertEqual((d['target_final'], d['relation_type_final']), ('CF88:ART.153:PAR.6', 'REGULAMENTA'))
        self.assertIn('NON_EXCLUSIVE', d['scope_flags'])
        for cid in ('CORRC0-29C48A0D5DA7', 'CORRC0-08F347BF86E6'):
            t = by[cid]['temporal']
            self.assertEqual((by[cid]['legal_decision'], by[cid]['relation_type_final']), ('APPROVE', 'COMPLEMENTA'))
            self.assertEqual((t['temporal_status'], t['effective_from'], t['early_application_possible']), ('VACATIO_LEGIS', '2028-01-01', True))
        bl = {(b['norm_key'], b['target_id']): b for b in doc['NEW_CANDIDATE_BACKLOG']}
        self.assertEqual(bl[('LC:214/2025', 'CF88:ART.153:INC.VIII')]['suggested_priority'], 'HIGH')
        self.assertEqual(bl[('LC:227/2026', 'CF88:ART.155:PAR.1:INC.III')]['suggested_priority'], 'HIGH')
        self.assertEqual(ir['architectural_debt']['id'], 'FUTURE_EFFECTIVE_CORRELATA_POLICY_REQUIRED')


class Consolidated(unittest.TestCase):
    def test_106_exactly_once(self):
        rows = CONS['candidates']
        ids = [r['candidate_id'] for r in rows]
        self.assertEqual(len(ids), 106)
        self.assertEqual(len(set(ids)), 106)
        self.assertEqual(set(ids), set(HIGH))
        s = CONS['summary']
        self.assertEqual((s['HIGH_ORIGINAL_TOTAL'], s['HIGH_ORIGINAL_REVIEWED'], s['HIGH_ORIGINAL_REMAINING']), (106, 106, 0))
        self.assertEqual(sum(s['per_batch'].values()), 106)
        self.assertEqual(s['per_batch'], dict(BATCH01=29, BATCH02=30, BATCH03=30, BATCH04=17))
        backlog_keys = {(b['norm_key'], b['target_id']) for b in CONS['NEW_CANDIDATE_BACKLOG']}
        self.assertEqual(len(backlog_keys), s['new_candidate_backlog_total'])
        # no backlog pair is counted among the 106 (backlogs never become original HIGH rows)
        self.assertFalse(backlog_keys & {(r['norm_key'], r['target_original']) for r in rows})

    def test_final_closure_resolves_all_holds(self):
        s = CONS['summary']
        self.assertEqual(s['decisions'], dict(APPROVE=36, ADJUST=41, REJECT=29, HOLD=0, NEEDS_SOURCE=0))
        self.assertEqual(s['accepted'], 77)
        by = {r['candidate_id']: r for r in CONS['candidates']}
        r = by['CORRC0-78E258F9B624']
        self.assertEqual((r['batch_decision'], r['decision'], r['reject_reason']),
                         ('HOLD', 'REJECT', 'CURRENT_CONSTITUTIONAL_REGIME_NOT_REPRESENTED_BY_LEI_8112'))
        self.assertEqual(by['CORRC0-E0C9C2F5CDBD']['reject_reason'], 'CROSS_REFERENCE_ONLY')
        for cid, rel, tgt in (('CORRC0-E86B55D28D44', 'REGULAMENTA', 'CF88:ART.231:PAR.1'), ('CORRC0-FC57ED913387', 'COMPLEMENTA', 'CF88:ART.231:PAR.6')):
            r = by[cid]
            self.assertEqual((r['decision'], r['relation_type_final'], r['target_final'], r['temporal_status']), ('ADJUST', rel, tgt, 'PARTIAL_EFFECTS'))
            self.assertIn('JUDICIAL_RESTRICTIONS', r['flags'])
            self.assertIn('NON_EXCLUSIVE', r['scope'])
            j = r['judicial']
            self.assertEqual((j['judicial_status'], j['merits_decided_on'], j['REVALIDATE_ON_FINAL_ED'], j['CORRELATA_REQUIRES_JUDICIAL_STATUS']),
                             ('STF_PARTIAL_UNCONSTITUTIONALITY', '2025-12-19', True, True))
            self.assertTrue(any(x['url'].startswith('https://portal.stf.jus.br/') for x in r['final_sources']))
        self.assertIn('ESCOPO_PARCIAL', by['CORRC0-FC57ED913387']['scope'])
        self.assertIn('DOES_NOT_IMPLEMENT_COMPLEMENTARY_LAW_EXCEPTION', by['CORRC0-FC57ED913387']['flags'])

    def test_rows_complete(self):
        for r in CONS['candidates']:
            self.assertIn(r['temporal_status'], B3.TEMPORAL)
            self.assertIn(r['decision'], B1.DECISIONS)
            if r['decision'] in ('APPROVE', 'ADJUST'):
                self.assertTrue(T.validate_target_id(r['target_final'])[0])
                self.assertIn(r['device_route_status'], C.ROUTES)
                if r['temporal_status'] == 'VACATIO_LEGIS':
                    self.assertIn('TEMPORAL_DEVICE_BLOCK', r['device_flags'])
        s = CONS['summary']
        self.assertEqual(s['accepted'], s['decisions']['APPROVE'] + s['decisions']['ADJUST'])
        self.assertEqual(sum(s['accepted_device_route'].values()), s['accepted'])

    def test_required_backlogs_preserved(self):
        keys = {(b['norm_key'], b['target_id']) for b in CONS['NEW_CANDIDATE_BACKLOG']}
        for k in (('LEI:13709/2018', 'CF88:ART.21:INC.XXVI'), ('LEI:8429/1992', 'CF88:ART.37:PAR.5'), ('LEI:13303/2016', 'CF88:ART.173:PAR.1:INC.III'),
                  ('LEI:7783/1989', 'CF88:ART.9'), ('LEI:7783/1989', 'CF88:ART.9:PAR.1'), ('LEI:6880/1980', 'CF88:ART.142:PAR.3'),
                  ('LC:214/2025', 'CF88:ART.156-A'), ('LC:214/2025', 'CF88:ART.195:INC.V'), ('LC:214/2025', 'CF88:ART.153:INC.VIII'),
                  ('LC:227/2026', 'CF88:ART.155:PAR.1:INC.III'), ('LEI:11417/2006', 'CF88:ART.103-A')):
            self.assertIn(k, keys)
        self.assertTrue(any(b['norm_key'] == 'LC:214/2025' and b['target_id'].startswith('ADCT') for b in CONS['NEW_CANDIDATE_BACKLOG']))

    def test_operational_files_unchanged(self):
        for p in OPERATIONAL:
            blob = subprocess.run(['git', 'show', f"{B3.BASE['head']}:{p}"], cwd=ROOT, capture_output=True, check=True).stdout
            self.assertEqual((ROOT / p).read_bytes().replace(b'\r\n', b'\n'), blob.replace(b'\r\n', b'\n'), p)
        # since C3A the overlay exists, but only as a host-only candidate that the engine configuration (RUN3) does not reference
        ov = ROOT / 'LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json'
        self.assertTrue(not ov.exists() or json.loads(ov.read_text(encoding='utf-8'))['status'] == 'RUN4_CANDIDATE_HOST_ONLY')
        self.assertNotIn('CORRELATA_ADDITIONS', (ROOT / 'LEGAL_TARGET_ID/engine_config.json').read_text(encoding='utf-8'))
        self.assertFalse(CONS['applied'])


if __name__ == '__main__':
    unittest.main()
