"""Permanent tests for CF-REF-A2 (reference canonicalization, quarantine, status, golden corpus)."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import reference_canonicalization as R  # noqa: E402
import target_id as T  # noqa: E402

D = HERE / 'derived'


def load(name):
    return json.loads((D / name).read_text(encoding='utf-8'))


class RuleUnitTest(unittest.TestCase):
    TEXT = {'CF88:ART.9:CAPUT': 'Texto do caput do artigo nove com conteudo suficiente.',
            'CF88:ART.9:PAR.1': 'Paragrafo primeiro original com conteudo.',
            'CF88:ART.9:PAR.1-A': 'O limite para elegibilidade do benefício de que trata o § 1º deste artigo não será inferior.'}

    def test_article_vs_caput_rules(self):
        self.assertEqual(R.article_vs_caput_from_text('CF88:ART.9', 'Texto do caput do artigo nove com conteudo suficiente.', self.TEXT)[:2],
                         ('MIGRATED_TO_CAPUT', 'CF88:ART.9:CAPUT'))
        self.assertEqual(R.article_vs_caput_from_text('CF88:ART.9', 'Texto do caput do artigo nove com conteudo suficiente. I - um; II - dois.', self.TEXT)[:2],
                         ('KEPT_AS_ARTICLE', 'CF88:ART.9'))
        self.assertEqual(R.article_vs_caput_from_text('CF88:ART.9', 'Outro texto qualquer sem relação.', self.TEXT)[0], 'NEEDS_REVIEW')
        self.assertEqual(R.article_vs_caput_from_text('CF88:ART.9', '', self.TEXT)[0], 'NEEDS_REVIEW')

    def test_collision_resolution_requires_remnant_and_text(self):
        tid, why = R.resolve_collision('CF88:ART.9:PAR.1', '-A. O limite para elegibilidade do benefício de que trata o § 1º deste artigo não será inferior.', self.TEXT)
        self.assertEqual(tid, 'CF88:ART.9:PAR.1-A')
        self.assertIsNone(R.resolve_collision('CF88:ART.9:PAR.1', 'Paragrafo primeiro original com conteudo.', self.TEXT)[0])
        self.assertIsNone(R.resolve_collision('CF88:ART.9:PAR.1', '-B. O limite para elegibilidade do benefício de que trata', self.TEXT)[0])
        self.assertIsNone(R.resolve_collision('CF88:ART.9:PAR.1', '-A. texto completamente diferente do candidato e longo o bastante', self.TEXT)[0])

    def test_catalog_gate_fails_closed(self):
        tg = {'CF88:ART.37:PAR.6': {}}
        good = dict(reference_id='X', target_id='CF88:ART.37:PAR.6', target_scope='PARAGRAFO', reference_type='T', source_record_id='S',
                    migration_status='AUTO_MEMBER_MATCH', validation_status='TARGET_STRUCTURALLY_VALID')
        self.assertTrue(R.validate_reference_record(good, tg))
        for bad, code in ((dict(good, target_id='CF88:ART.1:PAR.1'), 'CATALOG_TARGET_NOT_IN_INDEX'),
                          (dict(good, target_id='cf88:art.37'), 'CATALOG_INVALID_TARGET_ID'),
                          (dict(good, target_id=None), 'CATALOG_INVALID_TARGET_ID'),
                          (dict(good, source_record_id=''), 'CATALOG_MISSING_FIELD')):
            with self.assertRaises(T.TargetIdError) as cm:
                R.validate_reference_record(bad, tg)
            self.assertEqual(cm.exception.code, code)


@unittest.skipUnless((D / 'CF88_REFERENCES_CANONICAL.json').is_file(), 'A2 derived catalogs not built')
class DerivedCatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.idx = {t['target_id']: t for t in load('CF88_TARGET_INDEX.json')['targets']}
        cls.st = load('CF88_TARGET_STATUS.json')['targets']
        cls.cat = load('CF88_REFERENCES_CANONICAL.json')['records']
        cls.q = load('CF88_REFERENCES_QUARANTINE.json')['records']

    def test_corpus_closes(self):
        self.assertEqual(len(self.cat) + len(self.q), 1186)

    def test_every_catalog_record_passes_gate(self):
        for r in self.cat:
            self.assertTrue(R.validate_reference_record(r, self.idx))
            self.assertIn(r['migration_status'], ('AUTO_MEMBER_MATCH', 'MIGRATED_TO_CAPUT', 'KEPT_AS_ARTICLE', 'RESOLVED_WITH_EVIDENCE'))

    def test_quarantine_never_in_catalog(self):
        cat_ids = {(r['source_layer'], r['source_record_id']) for r in self.cat}
        for x in self.q:
            self.assertNotIn((x['record_original']['source_layer'], x['record_original']['source_record_id']), cat_ids)
            self.assertTrue(x['manual_review_required'])

    def test_key_targets(self):
        for tid, kind in (('CF88:ART.37:CAPUT', 'CAPUT'), ('CF88:ART.37:PAR.6', 'PARAGRAFO'), ('CF88:ART.37:PAR.10', 'PARAGRAFO'),
                          ('CF88:ART.60:PAR.4:INC.IV', 'INCISO'), ('ADCT:ART.5', 'ARTIGO')):
            self.assertEqual(self.idx[tid]['kind'], kind)
        self.assertEqual(self.st['CF88:ART.37:PAR.6']['status'], 'CURRENT')
        self.assertEqual(self.st['ADCT:ART.5:PAR.1']['status'], 'UNKNOWN_VALIDITY')
        self.assertEqual(self.st['CF88:ART.37']['status'], 'STRUCTURAL')

    def test_article_vs_caput_in_catalog(self):
        rc2 = [r for r in self.cat if r['source_layer'] == 'V2_RC2_REFERENCES' and r['original_device_key'] == 'CF88:ART.14']
        self.assertTrue(rc2)
        for r in rc2:
            self.assertEqual(r['target_id'], 'CF88:ART.14:CAPUT')
            self.assertEqual(r['migration_reason'], 'LEGACY_V2_ARTICLE_KEY_REPRESENTED_CAPUT')
        kept = [r for r in self.cat if r['migration_status'] == 'KEPT_AS_ARTICLE']
        self.assertTrue(kept)
        for r in kept:
            self.assertEqual(self.idx[r['target_id']]['kind'], 'ARTIGO')

    def test_v2_collisions_resolved_only_with_evidence(self):
        res = {r['original_device_key']: r['target_id'] for r in self.cat if r['migration_status'] == 'RESOLVED_WITH_EVIDENCE' and r['source_layer'].startswith('V2')}
        self.assertEqual(res, {'CF88:ART.239:PAR.3': 'CF88:ART.239:PAR.3-A', 'CF88:ART.40:PAR.4': 'CF88:ART.40:PAR.4-C',
                               'CF88:ART.93:INC.VIII': 'CF88:ART.93:INC.VIII-B'})

    def test_invalid_targets_quarantined_or_evidence_fixed(self):
        keys = {x['record_original']['original_device_key'] for x in self.q if x['classification'] == 'INVALID_TARGET'}
        for k in ('CF88:1:1:-:-', 'CF88:3:3:-:-', 'CF88:25:-:I:-'):
            self.assertIn(k, keys)
        adct = [r for r in self.cat if r['target_id'] == 'ADCT:ART.78:PAR.4']
        self.assertEqual(len(adct), 2)
        self.assertTrue(all('ADCT' in r['migration_reason'] for r in adct))
        self.assertFalse([r for r in self.cat if r['target_id'] in ('CF88:ART.1:PAR.1', 'CF88:ART.25:INC.I', 'CF88:ART.78:PAR.4')])

    def test_historical_only_status(self):
        self.assertEqual(self.st['CF88:ART.40:PAR.4:INC.II']['status'], 'HISTORICAL_ONLY')
        self.assertEqual(self.st['CF88:ART.102:PAR.UNICO']['status'], 'HISTORICAL_ONLY')
        hist = [r for r in self.cat if r['target_id'] == 'CF88:ART.40:PAR.4:INC.II']
        self.assertTrue(hist)
        self.assertTrue(all(r['target_status'] == 'HISTORICAL_ONLY' and not r['target_present_in_operational_text'] for r in hist))

    def test_suffix_targets(self):
        self.assertEqual(self.st['CF88:ART.92:INC.I-A']['status'], 'CURRENT')
        self.assertEqual(self.st['CF88:ART.40:PAR.4-C']['status'], 'CURRENT')
        self.assertTrue([r for r in self.cat if r['target_id'] == 'CF88:ART.40:PAR.4-C'])

    def test_golden_corpus(self):
        g = load('CF88_GOLDEN_CORPUS.json')
        self.assertEqual([a['article'] for a in g['articles']],
                         ['CF88:ART.1', 'CF88:ART.5', 'CF88:ART.37', 'CF88:ART.60', 'CF88:ART.150', 'CF88:ART.225', 'ADCT:ART.5'])
        self.assertTrue(all(v['exists'] for v in g['key_targets'].values()))


if __name__ == '__main__':
    unittest.main()
