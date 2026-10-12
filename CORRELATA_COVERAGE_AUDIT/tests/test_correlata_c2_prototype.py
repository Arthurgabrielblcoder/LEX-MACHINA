"""C2 prototype: CORRELATA additions overlay validator — routes, ADCT runtime gate, temporal/judicial policies and fail-closed cases."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
ROOT = AUDIT.parent
sys.path.insert(0, str(AUDIT / 'C2/prototype'))
import correlata_overlay as O  # noqa: E402

AS_OF = '2026-10-11'
CTX = O.load_context()
FIX = json.loads((AUDIT / 'C2/fixtures/correlata_additions_fixture.json').read_text(encoding='utf-8'))['records']
BY = {r['relation_id']: r for r in FIX}


def rec(rid, **changes):
    r = copy.deepcopy(BY[rid])
    r.update(changes)
    return r


class ValidFixtures(unittest.TestCase):
    def test_six_fixtures_accepted_with_expected_device_decision(self):
        res = {x['relation_id']: x for x in O.validate(FIX, CTX, AS_OF)}
        self.assertEqual(len(res), 6)
        exp = {'CORR_ADD_CDC1990_5_XXXII': ('MAIN_CORPUS', 'PUBLISH'), 'CORR_ADD_LC63_161_I': ('EXT_NORMAS', 'PUBLISH'),
               'CORR_ADD_L14965_132': ('EXT_NORMAS', 'HIDDEN_UNTIL_EFFECTIVE'),
               'CORR_ADD_L14701_231_P1': ('EXT_NORMAS', 'BLOCKED_INGESTION_REQUIRED'),
               'CORR_ADD_LC146_ADCT10_IIb': ('EXT_NORMAS', 'BLOCKED_INGESTION_REQUIRED'),
               'CORR_ADD_LC160_ADCT128_P2': ('EXT_NORMAS', 'BLOCKED_INGESTION_REQUIRED')}
        for rid, (route, dev) in exp.items():
            self.assertEqual((res[rid]['destination_route'], res[rid]['device']), (route, dev), rid)
        self.assertEqual(res['CORR_ADD_LC146_ADCT10_IIb']['target_check'], 'ADCT_RUNTIME_CONFIRMED')
        self.assertEqual(res['CORR_ADD_LC160_ADCT128_P2']['target_check'], 'ADCT_RUNTIME_CONFIRMED')
        self.assertTrue(res['CORR_ADD_L14701_231_P1']['notice'])

    def test_vacatio_publishes_only_after_effective_date(self):
        res = O.validate([BY['CORR_ADD_L14965_132']], CTX, '2028-01-01')
        self.assertEqual(res[0]['device'], 'PUBLISH')

    def test_judicial_notice_when_norm_is_on_card(self):
        ctx = copy.deepcopy(CTX)
        ctx['registry']['EXT_LEI14701_2023']['on_card'] = True
        self.assertEqual(O.validate([BY['CORR_ADD_L14701_231_P1']], ctx, AS_OF)[0]['device'], 'PUBLISH_WITH_JUDICIAL_NOTICE')

    def test_adct_engine_status_is_unknown_and_not_opened_generically(self):
        for rid in ('CORR_ADD_LC146_ADCT10_IIb', 'CORR_ADD_LC160_ADCT128_P2'):
            self.assertEqual(CTX['engine'][BY[rid]['target_id']]['status'], 'UNKNOWN_VALIDITY')


class FailClosed(unittest.TestCase):
    def assertRejects(self, code, records, ctx=CTX):
        with self.assertRaises(O.OverlayError) as e:
            O.validate(records, ctx, AS_OF)
        self.assertEqual(e.exception.code, code)

    def test_invalid_fixture_file(self):
        with self.assertRaises(O.OverlayError):
            O.validate_file(AUDIT / 'C2/fixtures/correlata_additions_invalid.json', CTX, AS_OF)

    def test_each_rule(self):
        cdc = 'CORR_ADD_CDC1990_5_XXXII'
        self.assertRejects('TARGET_NOT_FOUND', [rec(cdc, target_id='CF88:ART.5:INC.XCIX')])
        self.assertRejects('TARGET_HISTORICAL_OR_REVOKED', [rec(cdc, target_id='CF88:ART.40:PAR.4:INC.II')])
        ctx = copy.deepcopy(CTX)
        ctx['text_map'].discard('ADCT:ART.10:INC.II:AL.b')                      # runtime does not reach it -> not confirmed
        self.assertRejects('ADCT_NOT_CONFIRMED_BY_RUNTIME', [BY['CORR_ADD_LC146_ADCT10_IIb']], ctx)
        self.assertRejects('DESTINATION_NORM_NOT_FOUND', [rec(cdc, destination_norm_id='CDC2099')])
        self.assertRejects('ROUTE_INVALID', [rec(cdc, destination_route='RELACOES')])
        self.assertRejects('DESTINATION_ARTICLE_INVALID', [rec(cdc, destination_articles=['999'])])
        self.assertRejects('DESTINATION_ARTICLES_EMPTY_WITHOUT_FALLBACK', [rec(cdc, destination_articles=[])])
        self.assertRejects('NOT_APPROVED', [rec(cdc, review_status='PENDING_REVIEW')])
        self.assertRejects('VACATIO_WITHOUT_POLICY', [rec('CORR_ADD_L14965_132', vacatio_policy=None)])
        j = dict(BY['CORR_ADD_L14701_231_P1']['judicial_status'])
        j.pop('cases')
        self.assertRejects('JUDICIAL_RESTRICTIONS_INCOMPLETE', [rec('CORR_ADD_L14701_231_P1', judicial_status=j)])
        self.assertRejects('JUDICIAL_RESTRICTIONS_INCOMPLETE', [rec('CORR_ADD_L14701_231_P1', flags=[])])
        self.assertRejects('MAIN_CORPUS_UNRESOLVABLE', [rec('CORR_ADD_LC63_161_I', destination_route='MAIN_CORPUS')])
        self.assertRejects('MAIN_CORPUS_NORM_DUPLICATED_AS_EXT', [rec(cdc, destination_route='EXT_NORMAS')])
        self.assertRejects('TRANSITIONAL_WITHOUT_REVALIDATION', [rec('CORR_ADD_LC160_ADCT128_P2', revalidate_on=None)])
        self.assertRejects('TEMPORAL_STATUS_NOT_PUBLISHABLE', [rec(cdc, temporal_status='UNCERTAIN')])
        self.assertRejects('DUPLICATE', [BY[cdc], rec(cdc, relation_id='X')])
        self.assertRejects('MISSING_FIELD', [{k: v for k, v in BY[cdc].items() if k != 'provenance'}])


class NotOperational(unittest.TestCase):
    def test_prototype_not_wired_and_overlay_absent(self):
        self.assertFalse((ROOT / 'LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json').exists())
        eng = (ROOT / 'LEGAL_TARGET_ID/reference_engine.py').read_text(encoding='utf-8')
        self.assertNotIn('correlata_overlay', eng)
        for p in ('LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json', 'LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json',
                  'LEGAL_TARGET_ID/derived/export_test/run3/REF_LOOKUP.IDX', 'LEGAL_TARGET_ID/derived/export_test/run3/REF_PAYLOAD.IDX'):
            blob = subprocess.run(['git', 'show', f'44ef69ba3957d9c55a6b4b5fe9f9f68fcd77efef:{p}'], cwd=ROOT, capture_output=True, check=True).stdout
            self.assertEqual((ROOT / p).read_bytes().replace(b'\r\n', b'\n'), blob.replace(b'\r\n', b'\n'), p)


if __name__ == '__main__':
    unittest.main()
