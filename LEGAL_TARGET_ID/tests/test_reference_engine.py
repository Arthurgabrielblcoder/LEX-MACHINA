"""Permanent tests for CF-REF-A3: citation fan-out, quarantine resolution, generic engine, export and lookup."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import build_target_index as B  # noqa: E402
import citation_parser as C  # noqa: E402
import reference_engine as E  # noqa: E402
import target_id as T  # noqa: E402

D = HERE / 'derived'


def targets(text, art):
    p = C.parse_for_article(text, art)
    return p['status'], (C.to_targets('CF88', art, p, T.format_target_id) if p['status'] == 'OK' and p['norm'] == 'CF' else p.get('norm'))


class CitationFanOutTest(unittest.TestCase):
    def test_split_only_when_literal(self):
        self.assertEqual(targets('art. 5º, caput e I, da Constituição', '5'), ('OK', ['CF88:ART.5:CAPUT', 'CF88:ART.5:INC.I']))
        self.assertEqual(targets('incisos V e X do artigo 5º da Constituição Federal', '5'), ('OK', ['CF88:ART.5:INC.V', 'CF88:ART.5:INC.X']))
        self.assertEqual(targets('artigo 40, parágrafo 1º, inciso II, da Constituição Federal', '40'), ('OK', ['CF88:ART.40:PAR.1:INC.II']))
        self.assertEqual(targets('§§ 9º e 10 do art. 100 da Constituição', '100'), ('OK', ['CF88:ART.100:PAR.9', 'CF88:ART.100:PAR.10']))
        self.assertEqual(targets('(CF, §3º, art. 73 e art. 75)', '75'), ('OK', ['CF88:ART.75']))
        self.assertEqual(targets('art. 243, parágrafo único, da Constituição Federal', '243'), ('OK', ['CF88:ART.243:PAR.UNICO']))

    def test_article_is_never_expanded(self):
        self.assertEqual(targets('art. 5º da Constituição', '5'), ('OK', ['CF88:ART.5']))

    def test_vague_or_unsupported_fail_closed(self):
        for text, art in (('art. 5º, caput e seguintes, da CF', '5'), ('incisos I a IV do art. 144 da Constituição', '144'),
                          ('alínea a do inciso I do art. 7º da CF', '7'), ('arts. 40, §§ 1º e 2º, incisos I e II, da CF', '40'),
                          ('art. 7º da CF e art. 7º da EC 41/2003', '7'), ('art. 5º, caput', '5')):
            self.assertIn(C.parse_for_article(text, art)['status'], ('AMBIGUOUS', 'UNPARSEABLE'), text)

    def test_cross_norm_detected(self):
        for text, art, label in (('art. 3º da EC nº 113/2021', '3', 'EC nº 113/2021'), ('art. 10 da Lei 6.880/1980', '10', 'Lei 6.880/1980'),
                                 ('art. 102 do Código Penal Militar e do art. 92', '102', 'Código Penal Militar')):
            p = C.parse_for_article(text, art)
            self.assertEqual((p['norm'], p['norm_label']), ('OTHER', label))


@unittest.skipUnless((D / 'CF88_QUARANTINE_RESOLUTION.json').is_file(), 'A3 resolution not built')
class QuarantineResolutionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = json.loads((D / 'CF88_QUARANTINE_RESOLUTION.json').read_text(encoding='utf-8'))
        cls.cross = json.loads((D / 'CROSS_NORM_PENDING.json').read_text(encoding='utf-8'))

    def test_56_explained(self):
        self.assertEqual(self.res['total'], 56)
        self.assertEqual(sum(self.res['counts'].values()), 56)
        self.assertNotIn('OTHER_QUARANTINE', self.res['counts'])

    def test_fan_out_preserves_source_reference(self):
        r = next(x for x in self.res['records'] if x['original_record_id'] == 'STF:RG:969:CF88:5:-:-:-')
        self.assertEqual(r['targets'], ['CF88:ART.5:INC.II', 'CF88:ART.5:INC.XIII'])

    def test_cross_norm_preserved_outside_cf(self):
        ids = {x['original_record_id'] for x in self.cross['records']}
        self.assertIn('STF:RG:349:CF88:1:1:-:-', ids)
        self.assertEqual(len(ids), self.res['counts']['CROSS_NORM_REFERENCE_PENDING'])
        self.assertTrue(all(x['target_norm_canonicalized'] is False for x in self.cross['records']))


def _fixture_engine(tmp, catalog_records):
    src = tmp / 'cdc.txt'
    src.write_text('Art. 6º São direitos básicos do consumidor:\nVI - a efetiva prevenção e reparação de danos;\n'
                   'Parágrafo único. Texto sintético de teste.\n', encoding='utf-8')
    idx = B.build('CDC1990', src)
    (tmp / 'CDC1990_TARGET_INDEX.json').write_text(json.dumps(idx, ensure_ascii=False), encoding='utf-8')
    (tmp / 'CDC1990_REFS.json').write_text(json.dumps(dict(records=catalog_records), ensure_ascii=False), encoding='utf-8')
    cfg = dict(schema_version=1, norms=dict(CDC1990=dict(target_index='CDC1990_TARGET_INDEX.json', references_catalog='CDC1990_REFS.json')),
               export=json.loads((HERE / 'engine_config.json').read_text(encoding='utf-8'))['export'])
    (tmp / 'cfg.json').write_text(json.dumps(cfg), encoding='utf-8')
    return E.TargetRegistry(tmp / 'cfg.json', base=tmp)


def _work(target, rid='R1', work='W-1'):
    return dict(target_id=target, source_layer='V2_RC2_REFERENCES', source_record_id=rid, migration_status='AUTO_MEMBER_MATCH',
                provenance=dict(system='fixture', work_id=work, obra='Obra Sintética', tipo='FILME'),
                legal_fields_preserved=dict(nucleo_id='N1', evidencias=[dict(evidence_id=rid + '#E1')]))


class GenericEngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='engine_fixture_'))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_non_cf_fixture(self):
        reg = _fixture_engine(self.tmp, [_work('CDC1990:ART.6:INC.VI'), _work('CDC1990:ART.6:INC.VI', 'R2'), _work('CDC1990:ART.6:PAR.UNICO', 'R3', 'W-2')])
        links = E.build_links('CDC1990', reg)
        self.assertEqual([l['target_id'] for l in links], ['CDC1990:ART.6:INC.VI', 'CDC1990:ART.6:PAR.UNICO'])  # structural (text) order
        vi = next(l for l in links if l['target_id'] == 'CDC1990:ART.6:INC.VI')
        self.assertEqual((len(vi['routes']), vi['duplicate_class']), (2, 'MULTI_ROUTE_DISTINCT_PROVENANCE'))
        files = E.export('CDC1990', links, self.tmp / 'out')
        self.assertEqual(len(E.lookup_idx('CDC1990:ART.6:INC.VI', self.tmp / 'out/REF_LOOKUP.IDX', self.tmp / 'out/REF_PAYLOAD.IDX')), 1)
        files2 = E.export('CDC1990', E.build_links('CDC1990', reg), self.tmp / 'out2')
        self.assertEqual(files, files2)

    def test_invalid_target_fails_closed(self):
        for bad in ('CDC1990:ART.99', 'CF88:ART.6:INC.VI', 'CDC1990:ART.6:INC.VII'):
            reg = _fixture_engine(self.tmp, [_work(bad)])
            with self.assertRaises(E.EngineError) as cm:
                E.build_links('CDC1990', reg)
            self.assertEqual(cm.exception.code, 'LINK_TARGET_NOT_IN_NORM')
        reg = _fixture_engine(self.tmp, [])
        with self.assertRaises(E.EngineError):
            E.validate_link(dict(norma_id='CDC1990', target_id='cdc:6', reference_id='x', reference_type='T', source_id='s', status='CURRENT',
                                 visibility='CURRENT_VISIBLE', label='l', validation_status='VALIDATED'), reg)
        with self.assertRaises(E.EngineError):
            E.TargetRegistry(self.tmp / 'cfg.json', base=self.tmp).load('CC2002')

    def test_engine_has_no_norm_hardcoded(self):
        src = (HERE / 'reference_engine.py').read_text(encoding='utf-8')
        self.assertNotIn("'CF88'", src.split('def main')[0])
        self.assertNotIn('"CF88"', src.split('def main')[0])


@unittest.skipUnless((D / 'CF88_ENGINE_E2E.json').is_file() and (D / 'export_test/run1/REF_LOOKUP.IDX').is_file(), 'A3 export not built')
class CfExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ex = D / 'export_test/run1'
        cls.doc = json.loads((cls.ex / 'CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))
        cls.e2e = json.loads((D / 'CF88_ENGINE_E2E.json').read_text(encoding='utf-8'))

    def test_golden_e2e(self):
        self.assertTrue(self.e2e['GOLDEN_E2E_PASS'])
        self.assertEqual(len(E.get_references('CF88:ART.37:PAR.6', self.doc)), 5)
        self.assertEqual(E.get_references('CF88:ART.60:PAR.4:INC.IV', self.doc), [])

    def test_adct_namespace(self):
        self.assertIn('ADCT:ART.78:PAR.4', self.doc['references'])
        self.assertNotIn('CF88:ART.78:PAR.4', self.doc['references'])
        self.assertEqual(E.lookup_idx('CF88:ART.78:PAR.4', self.ex / 'REF_LOOKUP.IDX', self.ex / 'REF_PAYLOAD.IDX'), [])
        self.assertNotEqual(E.get_references('CF88:ART.5:CAPUT', self.doc), E.get_references('ADCT:ART.5', self.doc))

    def test_historical_visibility(self):
        self.assertEqual(E.get_references('CF88:ART.40:PAR.4:INC.II', self.doc), [])
        hist = E.get_references('CF88:ART.40:PAR.4:INC.II', self.doc, include_historical=True)
        self.assertTrue(hist)
        self.assertTrue(all(l['visibility'] == 'HISTORICAL_HIDDEN_BY_DEFAULT' and l['status'] == 'HISTORICAL_ONLY' for l in hist))

    def test_every_exported_link_valid_and_fan_out_shares_source(self):
        reg = E.TargetRegistry().load('CF88')
        split = [l for ls in self.doc['references'].values() for l in ls if l['migration'] == 'SPLIT_FROM_LITERAL_CITATION']
        for ls in self.doc['references'].values():
            for l in ls:
                self.assertTrue(E.validate_link(l, reg))
        src = [l for l in split if l['source_reference_id'] == 'STF:RG:969:CF88:5:-:-:-']
        self.assertEqual(sorted(l['target_id'] for l in src), ['CF88:ART.5:INC.II', 'CF88:ART.5:INC.XIII'])

    def test_deterministic_export(self):
        tmp = Path(tempfile.mkdtemp(prefix='cf_export_'))
        try:
            reg = E.TargetRegistry()
            files = E.export('CF88', E.build_links('CF88', reg), tmp)
            for name, meta in files.items():
                self.assertEqual((tmp / name).read_bytes(), (self.ex / name).read_bytes(), name)
        finally:
            shutil.rmtree(tmp)

    def test_invalid_lookup_id_fails_closed(self):
        with self.assertRaises(E.EngineError):
            E.get_references('CF88/ART.5', self.doc)


if __name__ == '__main__':
    unittest.main()
