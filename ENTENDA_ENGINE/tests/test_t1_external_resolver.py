"""Hermetic tests of the external dependency resolver (t1_external_resolver): versioned fixture only, no Relations Engine working folders.

The integration test against the real (quarantined) relation CF88 art. 37, § 7º -> Lei nº 12.813/2013 stays optional in
test_t1_validator_v2 (skipped when the local Relations Engine folders are absent); the essential logic is proven here.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import t1_external_resolver as X  # noqa: E402

FIXTURE = 'ENTENDA_ENGINE/tests/fixtures/t1_relations_fixture.json'
CATALOG = json.loads((HERE / 'editorial/T1_EXTERNAL_CATALOG.json').read_text(encoding='utf-8'))
EMPTY = dict(entries=[])
HUMAN = [dict(section='external_layer_notes', content='fonte oficial', source_type='HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE', in_cf88_runtime=False)]


def rec(tid, notes=(), text='Texto neutro de explicação.'):
    return dict(target_id=tid, content=dict(o_que_diz=text, o_que_significa=text, exemplo_pratico=text, atencao=None),
                external_layer_notes=list(notes))


class ExternalResolverFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.idx = X.RelationsIndex([dict(path=FIXTURE, role='TEST_FIXTURE')])

    def test_fixture_is_versioned_and_loaded(self):
        self.assertTrue((HERE.parent / FIXTURE).is_file())
        self.assertEqual(self.idx.loaded, [dict(source=FIXTURE, available=True, relations=5)])

    def test_relation_status_classes(self):
        rels = {r['case']: r for r in json.loads((HERE.parent / FIXTURE).read_text(encoding='utf-8'))['relacoes']}
        self.assertEqual({k: X.relation_status(v) for k, v in rels.items()},
                         {'A_VALIDATED_2D': 'VALIDATED', 'A_VALIDATED_GLOBAL_2E4': 'VALIDATED', 'B_PENDING_QUARANTINE': 'PENDING',
                          'C_WEAK': 'WEAK', 'C_WEAK_SECTION_UNDETERMINED': 'WEAK'})

    def test_validated_relation_gives_available(self):
        r = X.resolve(rec('CF88:ART.37:PAR.8'), EMPTY, self.idx, [])
        self.assertEqual((r['status'], r['via']), (X.AVAILABLE, 'RELATIONS_ENGINE_VALIDATED'))
        e = r['evidence'][0]
        self.assertEqual((e['norma'], e['tipo'], e['fonte'], e['status'], e['decisao'], e['url']),
                         ('EXT_FIXTURE_VALIDADA', 'REGULAMENTACAO', 'CAMARA_REGULAMENTACAO_CF', 'VALIDATED', 'EXIBIR', 'https://example.invalid/validada'))
        g = X.resolve(rec('CF88:ART.146'), EMPTY, self.idx, [])                                    # global catalog schema (status ATUAL)
        self.assertEqual((g['status'], g['via'], g['evidence'][0]['url']), (X.AVAILABLE, 'RELATIONS_ENGINE_VALIDATED', 'https://example.invalid/global'))

    def test_pending_relation_gives_local_pending(self):
        r = X.resolve(rec('CF88:ART.37:PAR.7'), EMPTY, self.idx, [])
        self.assertEqual((r['status'], r['via']), (X.PENDING, 'RELATIONS_ENGINE_PENDING'))
        e = r['evidence'][0]
        self.assertEqual((e['norma'], e['status'], e['decisao'], e['vigencia']),
                         ('EXT_LEI12813_2013', 'PENDING', 'OCULTAR_ATE_VALIDAR_VIGENCIA', 'NAO_LOCALIZADA'))
        self.assertIn('ArtCF0862', e['url'])

    def test_human_provenance_supports_entenda_without_promoting_relation(self):
        r = X.resolve(rec('CF88:ART.37:PAR.7'), EMPTY, self.idx, HUMAN)
        self.assertEqual((r['status'], r['via']), (X.AVAILABLE, 'ENTENDA_CONTENT_PROVENANCE'))
        self.assertEqual([e['status'] for e in r['evidence'] if e.get('norma') == 'EXT_LEI12813_2013'], ['PENDING'])   # relation stays pending

    def test_weak_relation_is_never_promoted(self):
        for tid in ('CF88:ART.37:PAR.3', 'CF88:ART.37:PAR.1'):                                     # weak, even with local text
            r = X.resolve(rec(tid), EMPTY, self.idx, [])
            self.assertEqual((r['status'], r['via']), (X.REQUIRED, None), tid)
            self.assertEqual([e['status'] for e in r['evidence']], ['WEAK'], tid)

    def test_no_relation_requires_verification(self):
        r = X.resolve(rec('CF88:ART.37:PAR.16'), EMPTY, self.idx, [])
        self.assertEqual((r['status'], r['via'], r['evidence']), (X.REQUIRED, None, []))
        missing = X.RelationsIndex([dict(path='ENTENDA_ENGINE/tests/fixtures/nao_existe.json')])
        self.assertEqual(missing.loaded[0]['available'], False)
        self.assertEqual(X.resolve(rec('CF88:ART.37:PAR.8'), EMPTY, missing, [])['status'], X.REQUIRED)

    def test_catalog_order(self):
        r = X.resolve(rec('CF88:ART.37:INC.XVI'), CATALOG, self.idx, [])                           # catalog entry without provenance rule
        self.assertEqual((r['status'], r['via']), (X.AVAILABLE, 'T1_EXTERNAL_CATALOG'))
        r = X.resolve(rec('CF88:ART.37:PAR.7'), CATALOG, self.idx, [])                             # catalogued, provenance required -> not enough
        self.assertEqual(r['status'], X.PENDING)
        self.assertIn('LEI_12813_2013', [e.get('entry') for e in r['evidence']])

    def test_inputs_not_mutated(self):
        rr = rec('CF88:ART.37:PAR.7')
        before = copy.deepcopy(rr)
        X.resolve(rr, CATALOG, self.idx, HUMAN)
        self.assertEqual(rr, before)


if __name__ == '__main__':
    unittest.main()
