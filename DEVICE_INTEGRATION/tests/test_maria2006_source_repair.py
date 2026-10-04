"""MARIA2006_SOURCE_REPAIR: official source -> operational TXT -> MARIA2006_ARTICLE_SEARCH.IDX -> catalog 72/72 (host staging only).

The authority is the Planalto download archived in source_evidence/MARIA2006 (raw bytes + provenance). The staging is produced by
tools/repair_maria2006_source.py with the Updater backend and the approved full-corpus pipeline; these tests rebuild it and audit it.
"""
import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DI / 'tools'))
import article_index_corpus as C  # noqa: E402
import article_index_loader_model as LM  # noqa: E402
import build_article_search_index as AI  # noqa: E402
import repair_maria2006_source as R  # noqa: E402

OUT = R.OUT
CARD_TXT = '15-LEI MARIA DA PENHA/Lei Maria da Penha.txt'
TXT_SHA = 'f1d43b76e1ae4013cbf812d5ac2169561e6bc6c4ecfa1e5ab7fbf2721c7d341f'
IDX_SHA = '61e00407355f37f516eede152d0436f8e7e2897ebf4fff81eca2ecf5e86ad2d6'
CAT_SHA = '8d7d11db81dfa1a07f647260e17a88b197b90a3b912012880a3701e5ca31a4c9'
CORRUPT_SHA = 'a560439bfa7bbb6cfa77f42578bf1688183c9047004eb022af0a6444af5e775c'
OLD_CAT_SHA = 'efadd17ee2483a325f1451d71ee40e8fedbf3c032ed0127cbdbc61a9c72b2f3b'


def sha(b):
    return hashlib.sha256(b).hexdigest()


@unittest.skipUnless(R.CORPUS.is_dir() and R.APPROVED_FULL.is_dir(), 'local SD copy / approved staging absent')
class Maria2006RepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.man = R.run(Path(cls.tmp.name) / 'repair')                       # fresh rebuild from the archived official bytes
        cls.out = Path(cls.tmp.name) / 'repair'
        cls.txt = (cls.out / 'SD' / CARD_TXT).read_bytes()
        cls.blob = (cls.out / 'SD' / C.SD_DIR / 'MARIA2006_ARTICLE_SEARCH.IDX').read_bytes()
        cls.cat = (cls.out / 'SD' / C.SD_DIR / C.CATALOG_NAME).read_bytes()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_provenance_of_the_official_source(self):
        p = json.loads(R.PROVENANCE.read_text(encoding='utf-8'))
        raw = R.RAW.read_bytes()
        self.assertEqual((len(raw), sha(raw)), (p['bytes'], p['sha256']))
        self.assertEqual(p['source_url'], self.man['catalog_item']['fonte_oficial'])
        self.assertEqual((p['final_url'], p['http_status'], p['redirects']), (p['source_url'], 200, []))
        self.assertTrue(p['source_url'].startswith('https://www.planalto.gov.br/'))
        self.assertEqual(raw[:2], b'\xff\xfe')                                    # UTF-16LE BOM: the cause of the 2026-09-13 corruption

    def test_txt_candidate(self):
        self.assertEqual(sha(self.txt), TXT_SHA)
        self.assertEqual(self.man['txt']['bytes'], len(self.txt))
        self.assertNotEqual(self.txt[:3], b'\xef\xbb\xbf')
        self.assertEqual((self.txt.count(b'\r'), self.txt.count(b'\x00')), (0, 0))
        t = self.txt.decode('utf-8')                                              # strict UTF-8
        self.assertIn('CODIFICACAO_ORIGEM: utf-16-le', t)
        self.assertIn('URL_FONTE: ' + self.man['catalog_item']['fonte_oficial'], t)
        self.assertIn('LEI Nº 11.340, DE 7 DE AGOSTO DE 2006', t)
        self.assertNotIn('ÿþ', t)
        self.assertNotRegex(t, r'<\s*/?\s*(html|body|head|p|span)\b')
        s = self.man['txt']['structure']
        self.assertTrue(s['has_date'] and s['signature'])
        self.assertGreater(s['kinds']['ARTIGO'], 0)
        for k in ('PARAGRAFO', 'INCISO', 'ALINEA'):
            self.assertGreater(s['kinds'].get(k, 0), 0, k)

    def test_corrupted_file_only_diagnosed(self):
        d = self.man['corrupted']
        self.assertEqual(d['sha256'], CORRUPT_SHA)
        self.assertTrue(d['diagnosis']['corrupted_has_bom_mojibake'])
        self.assertGreater(d['diagnosis']['HTML_NOISE_tags'], 1000)
        self.assertGreater(d['diagnosis']['MATCHABLE_TEXT_lines'], 0.9 * d['diagnosis']['new_lines'])

    def test_index_schema_binding_and_full_record_audit(self):
        self.assertEqual(sha(self.blob), IDX_SHA)
        magic, schema, hsz, rsz, ns, n, sbytes, ssha, bsha, _ = struct.unpack('<8sHHHHII32s32s8s', self.blob[:96])
        self.assertEqual((magic, schema, hsz, rsz, ns), (b'LXARTIX1', 1, 96, 12, 1))
        self.assertEqual((sbytes, ssha.hex()), (len(self.txt), sha(self.txt)))
        self.assertEqual(hashlib.sha256(self.blob[96:]).digest(), bsha)
        self.assertEqual(self.blob[96:112].rstrip(b'\0'), b'MARIA2006')
        a = self.man['index']['audit']
        self.assertEqual((a['records'], a['audited'], a['bad']), (n, n, []))
        self.assertTrue(a['oracle_equivalence'])
        self.assertEqual(a['repeated_keys'], [])
        self.assertEqual(a['collective_ranges'], [])
        ai = AI.ArticleIndex(self.blob, self.txt)
        plain = sorted(r[0] for r in ai.recs if r[1] == 0)
        self.assertEqual(plain, list(range(1, a['max_article'] + 1)))           # every article 1..max present once
        for k in (1, a['max_article']):
            off, nsn, occ = ai.find(k)
            self.assertTrue(self.txt[off:off + 12].startswith(f'Art. {k}'.encode()), k)
            self.assertIsNone(ai.find(k, 0, off + 1))                           # no second occurrence
        self.assertIsNone(ai.find(a['max_article'] + 1))
        for label in a['suffixed']:
            num, suf = label.split('-')
            off, _, _ = ai.find(int(num), ord(suf) - 64)
            self.assertTrue(self.txt[off:off + 16].decode('utf-8', 'replace').startswith(f'Art. {num}-{suf}'), label)

    def test_catalog_71_to_72_covers_catalogo_mestre(self):
        self.assertEqual(sha(self.cat), CAT_SHA)
        new = C.read_catalog(self.cat)
        old = C.read_catalog((R.APPROVED_FULL / 'SD' / C.SD_DIR / C.CATALOG_NAME).read_bytes())
        self.assertEqual((len(old), len(new)), (71, 72))
        self.assertEqual({e['norma'] for e in new} - {e['norma'] for e in old}, {'MARIA2006'})
        self.assertEqual([e for e in old], [e for e in new if e['norma'] != 'MARIA2006'])   # the 71 entries are unchanged
        ids = {i['id'] for i in json.loads(C.CATALOG_JSON.read_text(encoding='utf-8'))['itens']}
        self.assertEqual({e['norma'] for e in new}, ids)
        m = [e for e in new if e['norma'] == 'MARIA2006'][0]
        self.assertEqual((m['source_bytes'], m['source_sha256'], m['index_bytes']), (len(self.txt), sha(self.txt), len(self.blob)))

    def test_full_corpus_72_of_72(self):
        s = self.man['full_corpus']['summary']
        self.assertEqual((s['norms_analysed'], s['indexes'], s['BLOCKED'], s['KEEP'], s['ADD'], s['REBUILD'], s['REMOVE']), (72, 72, 0, 71, 1, 0, 0))
        self.assertEqual(self.man['full_corpus']['blocked'], [])
        self.assertTrue(self.man['full_corpus']['other_deploy_files_unchanged_vs_physical'])
        self.assertTrue(self.man['full_corpus']['catalog_covers_catalog_mestre'])
        self.assertEqual(s['needs_physical_confirmation'], ['MARIA2006'])        # the card still has the corrupted text until deploy

    def test_mini_deploy_only_three_files(self):
        d = {f['path']: f for f in self.man['deploy']}
        self.assertEqual(sorted(d), sorted(['/' + CARD_TXT, f'/{C.SD_DIR}/MARIA2006_ARTICLE_SEARCH.IDX', f'/{C.SD_DIR}/{C.CATALOG_NAME}']))
        self.assertEqual(d['/' + CARD_TXT]['action'], 'REPLACE')
        self.assertEqual(d['/' + CARD_TXT]['physical_before']['sha256'], CORRUPT_SHA)
        self.assertEqual(d[f'/{C.SD_DIR}/{C.CATALOG_NAME}']['action'], 'REPLACE')
        self.assertEqual(d[f'/{C.SD_DIR}/{C.CATALOG_NAME}']['physical_before']['sha256'], OLD_CAT_SHA)
        self.assertEqual(d[f'/{C.SD_DIR}/MARIA2006_ARTICLE_SEARCH.IDX']['action'], 'ADD')

    def test_deterministic_against_the_committed_staging(self):
        if OUT.is_dir():
            self.assertEqual(C.tree(OUT), C.tree(self.out))

    def test_device_loader_selects_maria_index_through_catalog(self):
        tdir = Path(self.tmp.name) / 't'
        tdir.mkdir()
        for p in (R.APPROVED_FULL / 'SD' / C.SD_DIR).iterdir():
            (tdir / p.name).write_bytes(p.read_bytes())
        for p in (self.out / 'SD' / C.SD_DIR).iterdir():
            (tdir / p.name).write_bytes(p.read_bytes())
        directory = [(p.name, p.read_bytes()) for p in sorted(tdir.iterdir())]
        r = LM.select(directory, len(self.txt), sha(self.txt), 'CATALOG')
        self.assertEqual((r['state'], r['index']), ('LOADED', 'MARIA2006_ARTICLE_SEARCH.IDX'))
        corrupt = (R.CORPUS / CARD_TXT).read_bytes()
        self.assertEqual(LM.select(directory, len(corrupt), sha(corrupt), 'CATALOG')['state'], 'SEM_INDICE')   # old text: never the new index
        cc = (R.CORPUS / '2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt').read_bytes()
        self.assertEqual(LM.select(directory, len(cc), sha(cc), 'CATALOG')['index'], 'CC2002_ARTICLE_SEARCH.IDX')


if __name__ == '__main__':
    unittest.main()
