"""C3A — host-only CORRELATA overlay engine and RUN4_CANDIDATE_HOST_ONLY (LEGAL_APPROVED != DEVICE_READY)."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
ROOT = AUDIT.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
sys.path.insert(0, str(AUDIT / 'C3A/tools'))
import reference_engine as E  # noqa: E402
import correlata_overlay as O  # noqa: E402
import build_export_run4_candidate as R4  # noqa: E402
import build_c3a_overlay as OV  # noqa: E402

BASELINE = '7c6d421585d971e5eef6af2bc3fa85ccab078d83'
REG = E.TargetRegistry()
CTX = R4.context(REG)
LINKS = E.build_links('CF88', REG)
ADDS = R4.load(R4.ADDITIONS)['records']
REGISTER = R4.load(R4.REGISTER)['records']
CORR = R4.load(R4.CORRECTIONS)['records']
VIEW = R4.load(R4.OUT / 'legal_view/CF88_CORRELATA_LEGAL_VIEW.json')
DEVICE = R4.load(R4.OUT / 'device_ready/CF88_REFERENCES_EXPORT.json')
DEV_LINKS = [l for ls in DEVICE['references'].values() for l in ls]


def find(target, norm_key):
    return copy.deepcopy(next(r for r in REGISTER if r['target_id'] == target and r['destination_norm_key'] == norm_key))


def mut(r, **kw):
    r = copy.deepcopy(r)
    r.update(kw)
    r['relation_id'] = O.relation_id_for(r['target_id'], r['destination_norm_id'])
    return r


def entry(kind, target, dest=None):
    return next(e for e in VIEW['entries'] if e['kind'] == kind and e['target_id'] == target and (dest is None or e['destination_norm_id'] == dest))


class Overlay(unittest.TestCase):
    def rejects(self, code, records, ctx=CTX, **kw):
        with self.assertRaises(O.OverlayError) as e:
            O.validate_records(records, ctx, **kw)
        self.assertEqual(e.exception.code, code)

    def test_01_valid_overlay_accepted(self):
        res = O.validate_records(ADDS, CTX, materialized_only=True)
        self.assertEqual(len(res), len(ADDS))
        self.assertTrue(all(r['review_status'] == O.APPROVED and r['destination_resolution'] == 'ON_CARD' for r in ADDS))
        self.assertEqual(len(O.validate_records(REGISTER, CTX)), len(REGISTER))

    def test_02_not_approved_rejected(self):
        self.rejects('NOT_APPROVED', [dict(ADDS[0], review_status='PENDING_REVIEW')])

    def test_03_invalid_target_rejected(self):
        self.rejects('TARGET_NOT_FOUND', [mut(ADDS[0], target_id='CF88:ART.5:INC.XCIX')])
        self.rejects('TARGET_NOT_FOUND', [mut(ADDS[0], target_id='CF88:ART.999')])

    def test_04_historical_target_rejected(self):
        self.rejects('TARGET_HISTORICAL_OR_REVOKED', [mut(ADDS[0], target_id='CF88:ART.40:PAR.4:INC.II')])

    def test_05_adct_runtime_confirmed_accepted(self):
        adct = [r for r in REGISTER if r['target_id'].startswith('ADCT:')]
        self.assertTrue(adct)
        for r in adct:
            self.assertEqual(CTX.engine_status(r['target_id']), 'UNKNOWN_VALIDITY')
            self.assertEqual(O.validate_record(r, CTX)['target_check'], 'ADCT_RUNTIME_CONFIRMED')

    def test_06_adct_unknown_not_confirmed_rejected(self):
        r = next(r for r in REGISTER if r['target_id'].startswith('ADCT:'))
        ctx = copy.copy(CTX)
        ctx.text_map = set(CTX.text_map) - {O.presentation_unit(r['target_id'])}       # not reachable on the device
        self.rejects('ADCT_NOT_CONFIRMED_BY_RUNTIME', [r], ctx)
        ctx = copy.copy(CTX)
        ctx.runtime = {k: v for k, v in CTX.runtime.items() if k != r['target_id']}     # absent from the runtime
        self.rejects('ADCT_NOT_CONFIRMED_BY_RUNTIME', [r], ctx)
        # a non-ADCT UNKNOWN_VALIDITY target is never opened (status simulated: no CF88 target is UNKNOWN in the real status file)
        ctx = copy.copy(CTX)
        ctx.engine_status = lambda t: 'UNKNOWN_VALIDITY'
        self.rejects('TARGET_STATUS_NOT_ALLOWED', [ADDS[0]], ctx)

    def test_07_ext_normas_on_card_device_ready(self):
        e = entry('ADDITION', 'CF88:ART.161:INC.I', 'EXT_LC63_1990')
        self.assertEqual((e['destination_route'], e['device_state'], e['article_check']), ('EXT_NORMAS', 'DEVICE_READY', 'ARTICLES_VERIFIED'))
        self.assertIn(f"CORRELATA:{e['relation_id']}@CF88:ART.161:INC.I", {l['reference_id'] for l in DEV_LINKS})

    def test_08_main_corpus_validated_but_blocked(self):
        e = entry('ADDITION', 'CF88:ART.5:INC.XXXII')
        self.assertEqual((e['destination_route'], e['article_check'], e['device_state']),
                         ('MAIN_CORPUS', 'ARTICLES_VERIFIED', 'BLOCKED_DEVICE_ROUTE_MAIN_CORPUS'))
        self.assertFalse(e['materialized_in_additions'])
        self.assertNotIn(e['relation_id'], json.dumps(DEVICE))
        r = find('CF88:ART.5:INC.XXXII', 'LEI:8078/1990')
        self.rejects('DESTINATION_ARTICLE_INVALID', [mut(r, destination_articles=['9999'])])
        self.rejects('MAIN_CORPUS_UNRESOLVABLE', [mut(r, destination_norm_id='NAO_EXISTE')])
        self.rejects('MAIN_CORPUS_NORM_DUPLICATED_AS_EXT', [mut(r, destination_route='EXT_NORMAS', destination_resolution='ON_CARD')])
        self.assertFalse(any(x['destination_route'] == 'MAIN_CORPUS' for x in ADDS))

    def test_09_ingestion_validated_but_blocked(self):
        ing = [e for e in VIEW['entries'] if e['kind'] == 'ADDITION' and e['destination_resolution'] == 'INGESTION_REQUIRED']
        self.assertTrue(ing)
        for e in ing:
            self.assertEqual(e['device_state'], 'BLOCKED_INGESTION_REQUIRED')
            self.assertEqual(e['article_check'], 'ARTICLES_DEFERRED_UNTIL_INGESTION')
        r = next(r for r in REGISTER if r['destination_resolution'] == 'INGESTION_REQUIRED')
        self.rejects('ADDITION_NOT_RESOLVABLE_ON_CARD', [r], materialized_only=True)
        self.rejects('DESTINATION_NORM_NOT_FOUND', [mut(r, destination_resolution='ON_CARD')])

    def test_10_vacatio_suppressed(self):
        vac = [e for e in VIEW['entries'] if e['kind'] == 'ADDITION' and e['temporal_status'] == 'VACATIO_LEGIS']
        self.assertTrue(vac)
        self.assertTrue(all(e['device_state'] == 'TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE' for e in vac))
        leg = entry('LEGACY', 'CF88:ART.37:INC.II')
        self.assertEqual((leg['device_state'], leg['legal_state'], leg['until']), ('TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE', 'LEGAL_KEPT', '2028-01-01'))
        self.assertNotIn(leg['reference_id'], {l['reference_id'] for l in DEV_LINKS})
        r = next(r for r in ADDS if r['temporal_status'] == 'VACATIO_LEGIS')
        self.assertEqual(O.device_blockers(r, CTX, '2028-01-01'), [])           # relation kept: shows up from the effective date
        self.rejects('VACATIO_WITHOUT_POLICY', [dict(r, vacatio_policy=None)])
        c = next(c for c in CORR if c['action'] == 'SUPPRESS_TEMPORAL')
        self.assertEqual(O.correction_effect(c, '2028-01-01'), 'VISIBLE')

    def test_11_hold_suppressed(self):
        e = entry('LEGACY', 'CF88:ART.37:PAR.3:INC.III')
        self.assertEqual((e['legacy_decision'], e['device_state'], e['legal_state']), ('HOLD', 'REVIEW_HOLD_SUPPRESSED', 'LEGAL_HOLD'))
        self.assertNotIn(e['reference_id'], {l['reference_id'] for l in DEV_LINKS})
        self.assertIn(e['reference_id'], {l['reference_id'] for l in LINKS})          # the catalog still has it (restorable)

    def test_12_judicial_status_required(self):
        r = find('CF88:ART.231:PAR.1', 'LEI:14701/2023')
        self.assertTrue(r['judicial_status']['notice_short'])
        self.rejects('JUDICIAL_RESTRICTIONS_INCOMPLETE', [dict(r, judicial_status=None)])
        j = dict(r['judicial_status'])
        j.pop('cases')
        self.rejects('JUDICIAL_RESTRICTIONS_INCOMPLETE', [dict(r, judicial_status=j)])
        self.rejects('JUDICIAL_RESTRICTIONS_INCOMPLETE', [dict(r, flags=[])])
        self.assertIn('BLOCKED_DEVICE_JUDICIAL_NOTICE_UNSUPPORTED', entry('ADDITION', 'CF88:ART.231:PAR.1')['device_blockers'])
        pe = next(r for r in REGISTER if r['temporal_status'] == 'PARTIAL_EFFECTS' and not r['judicial_status'])
        self.rejects('PARTIAL_EFFECTS_WITHOUT_BASIS', [dict(pe, temporal_note=None)])
        tr = next(r for r in REGISTER if r['temporal_status'] == 'TRANSITIONAL')
        self.rejects('TRANSITIONAL_WITHOUT_REVALIDATION', [dict(tr, revalidate_on=None)])

    def test_13_high_legacy_duplicate_collapsed(self):
        lc199 = [r for r in REGISTER if r['destination_norm_key'] == 'LC:199/2023']
        self.assertEqual(len(lc199), 1)
        self.assertEqual(lc199[0]['target_id'], 'CF88:ART.146:INC.III:AL.b')
        self.assertTrue(any(d.startswith('CORRC0-') for d in lc199[0]['decision_ids']))
        self.assertTrue(any(d.startswith('LEGACY:') for d in lc199[0]['decision_ids']))
        self.assertEqual(sum(1 for l in DEV_LINKS if l['source_id'] == 'EXT_LC199_2023'), 1)
        self.rejects('DUPLICATE', [lc199[0], copy.deepcopy(lc199[0])])

    def test_14_art_caput_no_duplication(self):
        r = find('CF88:ART.214:CAPUT', 'LEI:15388/2026')
        self.rejects('DUPLICATE', [r, mut(r, target_id='CF88:ART.214')])
        units = [(O.presentation_unit(l['target_id']), l['source_id']) for l in DEV_LINKS if l['reference_type'] == 'CORRELATA']
        self.assertEqual(len(units), len(set(units)))
        pne = [l for l in DEV_LINKS if l['source_id'] == 'EXT_LEI15388_2026']
        self.assertEqual([l['target_id'] for l in pne], ['CF88:ART.214:CAPUT'])     # six fan-out links -> one presentation unit
        art182 = [l for l in DEV_LINKS if O.presentation_unit(l['target_id']) == 'CF88:ART.182' and l['reference_type'] == 'CORRELATA']
        self.assertEqual(len(art182), 1)                                              # presentation-equivalent retarget: no-op


class Build(unittest.TestCase):
    def test_15_determinism_two_clean_builds(self):
        sums = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as t:
                R4.build(t)
                sums.append((Path(t) / 'SHA256SUMS.txt').read_bytes())
        self.assertEqual(sums[0], sums[1])
        self.assertEqual(sums[0], (R4.OUT / 'SHA256SUMS.txt').read_bytes().replace(b'\r\n', b'\n'))
        self.assertEqual(OV.build(), OV.build())
        for p, b in zip((OV.OUT_REGISTER, OV.OUT_ADDITIONS, OV.OUT_CORRECTIONS), OV.build()):
            self.assertEqual(p.read_bytes().replace(b'\r\n', b'\n'), b, p.name)

    def test_16_operational_files_untouched(self):
        self.assertTrue(R4.run3_reproduced())
        paths = ['LEGAL_TARGET_ID/derived/export_test/run3', 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json',
                 'LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json', 'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json',
                 'LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS.json', 'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json',
                 'LEGAL_TARGET_ID/engine_config.json', 'LEGAL_TARGET_ID/reference_engine.py', 'DEVICE_INTEGRATION', 'firmware']
        diff = subprocess.run(['git', 'diff', '--name-only', BASELINE, '--'] + paths, cwd=ROOT, capture_output=True, text=True, check=True).stdout
        self.assertEqual(diff.strip(), '')
        untracked = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', '--'] + paths, cwd=ROOT, capture_output=True,
                                   text=True, check=True).stdout
        self.assertEqual(untracked.strip(), '')
        pin = R4.load(R4.PIN)['relations_v2_package']['files']
        for f in ('RELACOES.IDX', 'REL_LOOKUP.IDX', 'EXT_NORMAS.IDX', 'EXT_ARTIGOS.IDX'):
            self.assertEqual(hashlib.sha256((R4.CARD / f).read_bytes()).hexdigest(), pin[f'99_RELATIONS_V2/05_INDICES_ESP32_V2/{f}']['sha256'])

    def test_relacoes_writer_reproduces_card_and_caps(self):
        rel, look, caps = O.write_relacoes(CTX.relacoes, CTX)
        self.assertEqual((rel, look), (CTX.card_relacoes, CTX.card_lookup))
        s = R4.load(R4.OUT / 'RUN4_CANDIDATE_SUMMARY.json')
        for k, lim in O.FIRMWARE_CACHE.items():
            self.assertLessEqual(s['device_ready']['firmware_cache']['used'][k], lim)
        self.assertTrue(s['device_ready']['non_correlata_links_identical_to_run3'])

    def test_traceability_and_legacy_coverage(self):
        for e in VIEW['entries']:
            if e['kind'] == 'ADDITION':
                self.assertTrue(e['decision_ids'])
            elif e['action'] not in (None,):
                self.assertTrue(e['decision_id'])
        with self.assertRaises(O.OverlayError) as x:
            O.validate_corrections(CORR[1:], LINKS, CTX)
        self.assertEqual(x.exception.code, 'LEGACY_LINK_WITHOUT_DECISION')
        new = [l for l in DEV_LINKS if l['reference_type'] == 'CORRELATA' and l['migration'] == O.APPROVED]
        self.assertTrue(all(l['provenance']['decision_ids'] for l in new))
        self.assertEqual(R4.load(R4.OUT / 'RUN4_CANDIDATE_SUMMARY.json')['status'], 'RUN4_CANDIDATE_HOST_ONLY')


if __name__ == '__main__':
    unittest.main()
