"""CC_INDEX: ARTICLE_SEARCH.IDX for the REAL Codigo Civil + generic per-text loader (no norm hard-coded in the firmware).

Convention: /99_LEX_V1/10_TARGETS/<NORMA>_ARTICLE_SEARCH.IDX. The firmware lists *_ARTICLE_SEARCH.IDX (names only), reads the 96 B
headers, and binds the index whose source bytes AND sha256 equal the OPEN text. One index in PSRAM at a time; changing text unloads.
The CC index is built from the structural target index (LEGAL_TARGET_ID/build_target_index.py --norma CC2002), never from a loose
regex. Source = the CC TXT of the SD backup (backups/sd_20260929T163407Z, not in Git); the physical SD file is re-checked on the PC.
"""
import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
import build_article_search_index as AI  # noqa: E402
import context_parser_port as P  # noqa: E402

FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
INO = (FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
STAGE = DI / 'staging_article_index_cc'
CC_IDX = STAGE / 'SD/99_LEX_V1/10_TARGETS/CC2002_ARTICLE_SEARCH.IDX'
CC_TI = STAGE / '_host/CC2002_TARGET_INDEX.json'
CF_IDX = DI / 'staging_article_index/SD/99_LEX_V1/10_TARGETS/CF88_ARTICLE_SEARCH.IDX'
CF_TXT = DI / 'staging_sd_v1/SD/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt'
CC_TXT = DI / 'backups/sd_20260929T163407Z/data/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'
CC_SHA = 'ad5ba178613b6181e2d8a61919eda0c6223c68feb6e47bef4ea65bc45c13e6ae'
REQUIRED = (1, 10, 100, 999, 1000, 1001, 1500, 1999, 2000, 2001, 2046)


def func(src, name):
    body = src[src.index(name):]
    return body[:body.index('\n}\n')]


def header(blob):
    magic, schema, hsz, rsz, ns, regs, src_bytes, src_sha, body_sha, _ = struct.unpack('<8sHHHHII32s32s8s', blob[:96])
    return dict(magic=magic, schema=schema, ns=ns, records=regs, src_bytes=src_bytes, src_sha=src_sha.hex())


def select(sd_indexes, text_path, text_bytes, text_sha, cap=8):
    """Python mirror of lexV1ArtIdxPronto: names ending in _ARTICLE_SEARCH.IDX -> header size match -> text sha match -> load."""
    names = [n for n in sd_indexes if n.endswith('_ARTICLE_SEARCH.IDX')][:cap]
    cands = [n for n in names if sd_indexes[n][:8] == b'LXARTIX1' and header(sd_indexes[n])['src_bytes'] == text_bytes]
    if not cands:
        return None, 'SEM_INDICE'
    for n in cands:
        if header(sd_indexes[n])['src_sha'] != text_sha:
            continue
        blob = sd_indexes[n]
        if hashlib.sha256(blob[96:]).digest() != blob[56:88]:
            continue
        return n, 'LOADED'
    return None, 'NENHUM_INDICE_VALIDO'


@unittest.skipUnless(CC_TXT.is_file() and CC_IDX.is_file(), 'CC TXT (local SD backup) / staged CC index not present')
class CcIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = CC_TXT.read_bytes()
        cls.blob = CC_IDX.read_bytes()
        cls.ai = AI.ArticleIndex(cls.blob, cls.data)                  # self-check: text bytes + sha256 + body sha256

    def test_source_binding(self):
        h = header(self.blob)
        self.assertEqual((h['magic'], h['schema'], h['ns']), (b'LXARTIX1', 1, 1))
        self.assertEqual(h['src_bytes'], len(self.data))
        self.assertEqual(h['src_sha'], hashlib.sha256(self.data).hexdigest())
        self.assertEqual(h['src_sha'], CC_SHA)
        self.assertEqual(self.blob[96:112].rstrip(b'\0'), b'CC2002')
        self.assertEqual(len(self.blob), 96 + 16 + h['records'] * 12)

    def test_records_computed_not_assumed(self):
        ti = json.loads(CC_TI.read_text(encoding='utf-8'))
        arts = [t for t in ti['targets'] if t['kind'] == 'ARTIGO']
        self.assertEqual(header(self.blob)['records'], len(arts))
        self.assertEqual(ti['target_id_duplicates'], 0)
        self.assertEqual(len(ti['anomalies']), 0)
        nums = {int(t['target_id'].split('ART.')[1].split('-')[0]) for t in arts}
        self.assertEqual(max(nums), 2046)
        revoked = set(range(1620, 1630)) | set(range(1768, 1774))           # "Arts. 1.620 a 1.629." / "Arts. 1.768 a 1.773."
        self.assertEqual(set(range(1, 2047)) - nums, revoked)
        self.assertGreater(len(arts), 2046)                                   # suffixed articles (-A, -B...) are extra records

    def test_required_articles(self):
        for k in REQUIRED:
            self.ai.comparisons = 0
            off, ns, occ = self.ai.find(k)
            self.assertEqual((ns, occ), ('CC2002', 0), k)
            line = self.data[off:self.data.index(b'\n', off)]
            c = dict(artigo='', paragrafo='', inciso='', alinea='')
            self.assertTrue(P.apply_line(c, line[:511]), k)
            self.assertEqual(c['artigo'], str(k), k)                          # parser of the device on the indexed line
            self.assertTrue(off == 0 or self.data[off - 1:off] == b'\n', k)   # line start
            self.assertLessEqual(self.ai.comparisons, 12 + 4)
        self.assertEqual(self.ai.find(2000)[0], 647337)                       # same offset the device logged (legacy linear)

    def test_suffix_records(self):
        off, ns, occ = self.ai.find(48, 1)                                    # 48-A
        self.assertTrue(self.data[off:off + 12].startswith(b'Art. 48-A'))
        c = dict(artigo='', paragrafo='', inciso='', alinea='')
        P.apply_line(c, self.data[off:self.data.index(b'\n', off)])
        self.assertEqual(c['artigo'], '48-A')
        self.assertIsNone(self.ai.find(1620))                                  # revoked range: not found (no false landing)

    def test_rebuild_byte_identical(self):
        with tempfile.TemporaryDirectory() as t:
            blob, man = AI.build(CC_TXT, CC_TI)
        self.assertEqual(blob, self.blob)
        self.assertEqual(man['records'], header(self.blob)['records'])


@unittest.skipUnless(CC_TXT.is_file() and CC_IDX.is_file() and CF_IDX.is_file() and CF_TXT.is_file(), 'staged files not present')
class LoaderSelectionModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sd = {'/99_LEX_V1/10_TARGETS/CF88_ARTICLE_SEARCH.IDX': CF_IDX.read_bytes(),
                  '/99_LEX_V1/10_TARGETS/CC2002_ARTICLE_SEARCH.IDX': CC_IDX.read_bytes(),
                  '/99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX': b'not an article index'}
        cf, cc = CF_TXT.read_bytes(), CC_TXT.read_bytes()
        cls.cf = ('/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt', len(cf), hashlib.sha256(cf).hexdigest())
        cls.cc = ('/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt', len(cc), hashlib.sha256(cc).hexdigest())

    def test_cf_cc_cf(self):
        seq = [select(self.sd, *t) for t in (self.cf, self.cc, self.cf, self.cc)]
        self.assertEqual([s[0].rsplit('/', 1)[1] for s in seq],
                         ['CF88_ARTICLE_SEARCH.IDX', 'CC2002_ARTICLE_SEARCH.IDX', 'CF88_ARTICLE_SEARCH.IDX', 'CC2002_ARTICLE_SEARCH.IDX'])

    def test_wrong_or_missing_index_never_used(self):
        self.assertEqual(select(self.sd, 'x.txt', 1234, '0' * 64), (None, 'SEM_INDICE'))
        path, n, sha = self.cc
        self.assertEqual(select(self.sd, path, n, 'f' * 64), (None, 'NENHUM_INDICE_VALIDO'))   # same size, other text
        bad = dict(self.sd)
        b = bytearray(bad['/99_LEX_V1/10_TARGETS/CC2002_ARTICLE_SEARCH.IDX'])
        b[200] ^= 1
        bad['/99_LEX_V1/10_TARGETS/CC2002_ARTICLE_SEARCH.IDX'] = bytes(b)
        self.assertEqual(select(bad, *self.cc), (None, 'NENHUM_INDICE_VALIDO'))                # body sha256 fails closed

    def test_psram_one_index_at_a_time(self):
        self.assertLess(max(len(v) for v in self.sd.values()), 32 * 1024)


class FirmwareLoaderContractTest(unittest.TestCase):
    def test_no_norm_in_loader(self):
        start = INO.index('// ---------------- ARTICLE_SEARCH.IDX')
        loader = INO[start:INO.index('// numero do teclado -> chave')]
        self.assertNotIn('CF88_ARTICLE_SEARCH', INO)
        self.assertNotIn('CC2002', loader)
        for s in ('#define LEXV1_ARTIDX_DIR "/99_LEX_V1/10_TARGETS"', '#define LEXV1_ARTIDX_SUFIXO "_ARTICLE_SEARCH.IDX"',
                  'd.f.getNextFileName(&ehDir)', '[ARTIDX] UNLOAD %s', '[ARTIDX] SEM_INDICE', '[ARTIDX] IGNORADO',
                  '[ARTIDX] TEXT_SHA bytes=%lu ms=%lu'):
            self.assertIn(s, loader, s)

    def test_hooks(self):
        self.assertIn('lexV1ArtIdxAoAbrirTexto();', func(INO, 'void abrirPastaSelecionada()'))
        f = func(INO, 'static bool lexV1PesquisarArtigoEstrutural(const String &n, uint32_t inicio)\n{')
        self.assertIn('if(lexV1ArtIdxPronto()){', f)
        self.assertNotIn('lexV1CamadaV1Aplicavel() && lexV1ArtIdxPronto()', f)

    def test_production_logs_off(self):
        # PERFORMANCE_BASELINE_FREEZE: benchmark logs exist but are disabled by default (1 only for a physical benchmark)
        self.assertIn('#define LEXV1_ARTSEARCH_LOG 0 ', INO)
        self.assertIn('#define LEX_SCROLL_PERF_LOG 0 ', INO)
        for s in ('if(LEX_SCROLL_PERF_LOG){\n    const bool hit=', 'if(LEX_SCROLL_PERF_LOG)\n    Serial.printf("[SCROLL] PREPARO',
                  'if(LEX_SCROLL_PERF_LOG) Serial.printf("PERF CONTEXTO_UP: %lu us (checkpoint=%s, bytes=%lu) origem=%s',
                  'if(LEXV1_ARTSEARCH_LOG) Serial.printf("[ARTIDX] SEM_INDICE', 'if(LEXV1_ARTSEARCH_LOG) Serial.printf("[ARTIDX] TEXT_SHA'):
            self.assertIn(s, INO, s)
        # anomalies stay visible in production
        for s in ('"[ARTIDX] INVALIDO %s %s', '"[ARTIDX] IGNORADO %s', '"[ARTIDX] NENHUM_INDICE_VALIDO', '"[SCROLL] REFILL_FAILSAFE'):
            self.assertIn('Serial.printf(' + s, INO, s)

    def test_fd_policy(self):
        p = func(INO, 'static bool lexV1ArtIdxPronto()\n{')
        self.assertEqual(p.count('LexV1FileReader'), 2)                       # directory (names only) + one header at a time
        self.assertIn('d.fechar();', p)
        self.assertLess(p.index('d.fechar();'), p.index('f.abrir("ARTIDX_HDR"'))   # directory closed before any header open
        self.assertNotIn('openNextFile', p)
        self.assertNotIn('SD.open', p)


if __name__ == '__main__':
    unittest.main()
