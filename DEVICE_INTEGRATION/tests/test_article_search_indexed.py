"""INDEXED ARTICLE SEARCH (DEVICE V1, uncommitted until the physical benchmark).

Physical cause (Arthur's device log): search art. 230 = 471 ms text scan (pesquisarArtigo, O(offset)) + 6.592 ms context
reconstruction after the centered landing (reconstruirContextoAntesOffset re-read 383.690 B byte by byte, O(offset)).
Fix: ARTICLE_SEARCH.IDX (LXARTIX1, 12 B/record, built on the PC from the structural target index, bound to the text by sha256)
loaded once in PSRAM -> lower_bound O(log n), no text scan; the context before the landing is seeded from the TEXT_MAP row (bounded
re-read). These tests pin correctness, occurrence order, bounded comparisons, fail-closed validation and the firmware contract.
"""
import hashlib
import json
import math
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(DI / 'tests'))
import article_search_benchmark as BM  # noqa: E402
import build_article_search_index as AI  # noqa: E402
import reader_viewport as V  # noqa: E402
from test_article_search_landing import func, strip_v1  # noqa: E402

FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
INO = (FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
OLD = subprocess.run(['git', 'show', 'HEAD:firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'], cwd=ROOT,
                     capture_output=True, text=True, encoding='utf-8').stdout
SD1 = DI / 'staging_sd_v1/SD/99_LEX_V1'
SD3 = DI / 'staging_sd_v1_run3_candidate/SD/99_LEX_V1'
HOST = DI / 'staging_sd_v1/_host'
REMISSIONS = (494539, 494627, 496649, 564587, 568164, 586543)        # line-start "art. n da Lei ..." in the runtime (not targets)


def walk(reader, n):
    out, start = [], 0
    while True:
        o = reader.search_structural(n, start)
        if o is None:
            return out
        out.append(o)
        start = o + 1


@unittest.skipUnless(V.ARTIDX.is_file() and (SD1 / '05_TEXT/CF88_RUNTIME.txt').is_file(), 'index / staging not built')
class CfIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = V.ARTIDX.read_bytes()
        cls.data = (SD1 / '05_TEXT/CF88_RUNTIME.txt').read_bytes()
        cls.idx = AI.ArticleIndex(cls.blob, cls.data)
        cls.r = V.Reader(SD1, artidx=V.ARTIDX)
        cls.lin = V.Reader(SD1)                                                       # previous firmware (structural linear)

    def test_header_and_size(self):
        magic, schema, hsize, rsize, nsc, n, sbytes, ssha, bsha, _ = struct.unpack('<8sHHHHII32s32s8s', self.blob[:96])
        self.assertEqual((magic, schema, hsize, rsize, nsc, n), (b'LXARTIX1', 1, 96, 12, 2, 424))
        self.assertEqual((sbytes, ssha.hex()), (len(self.data), hashlib.sha256(self.data).hexdigest()))
        self.assertEqual(len(self.blob), 96 + 2 * 16 + 424 * 12)                         # 5.216 B
        self.assertEqual(self.idx.ns, ['CF88', 'ADCT'])

    def test_deterministic_rebuild(self):
        with tempfile.TemporaryDirectory() as t:
            for k in (1, 2):
                blob, man = AI.build(SD1 / '05_TEXT/CF88_RUNTIME.txt', HOST / 'CF88_RUNTIME_TARGET_INDEX.json', SD1 / '10_TARGETS/CF88_TEXT_MAP.IDX')
                (Path(t) / f'{k}.idx').write_bytes(blob)
            self.assertEqual((Path(t) / '1.idx').read_bytes(), (Path(t) / '2.idx').read_bytes())
            self.assertEqual((Path(t) / '1.idx').read_bytes(), self.blob)               # BYTE_IDENTICAL with the staged candidate
        man = json.loads((DI / 'staging_article_index/_host/CF88_ARTICLE_SEARCH.manifest.json').read_text(encoding='utf-8'))
        self.assertEqual((man['records'], man['bytes'], man['sha256']), (424, len(self.blob), hashlib.sha256(self.blob).hexdigest()))

    def test_every_article_matches_the_text_map(self):
        rows = {o: t for o, _, t in self.r.map}
        for num, suf, ns, off, occ, _ in self.idx.recs:
            tid = f"{self.idx.ns[ns]}:ART.{num}" + (f"-{chr(64 + suf)}" if suf else '')
            self.assertEqual(rows.get(off), tid, tid)                                   # structural, confirmed by the TEXT_MAP
        targets = [t for t in json.loads((HOST / 'CF88_RUNTIME_TARGET_INDEX.json').read_text(encoding='utf-8'))['targets'] if t['kind'] == 'ARTIGO']
        self.assertEqual(len(targets), len(self.idx.recs))

    def test_parity_with_the_structural_linear_search(self):
        nums = sorted({str(r[0]) for r in self.idx.recs}, key=int) + ['0', '05', '251', '999', '65536']
        for n in nums:
            self.assertEqual(walk(self.r, n), walk(self.lin, n), n)                      # same occurrences, same order

    def test_occurrences_and_namespaces(self):
        self.assertEqual([(o, self.r.map_row_at(o)) for o in walk(self.r, 5)], [(2507, 'CF88:ART.5'), (430836, 'ADCT:ART.5')])
        self.assertEqual(self.idx.find(5, 0, 2508)[1:], ('ADCT', 1))                    # next occurrence = occurrence + 1
        self.assertEqual(walk(self.r, 193), [349277])
        self.assertIsNone(self.idx.find(5, 0, 430837))                                   # end: no wrap
        self.assertEqual(self.idx.find(29, 1)[0], next(o for o, _, t in self.r.map if t == 'CF88:ART.29-A'))   # suffix kept apart
        self.assertEqual(walk(self.r, 29), [o for o, _, t in self.r.map if t in ('CF88:ART.29', 'ADCT:ART.29')])

    def test_remissions_never_indexed(self):
        offs = {r[3] for r in self.idx.recs}
        for o in REMISSIONS:
            self.assertNotIn(o, offs)
            self.assertIsNone(self.r.map_row_at(o))
        self.assertEqual(walk(self.r, 2), [1185, 429519])

    def test_bounded_comparisons_and_no_text_scan(self):
        bound = math.ceil(math.log2(len(self.idx.recs))) + 1
        self.r.text_scans = 0
        for n in range(1, 251):
            self.idx.comparisons = 0
            self.r.index.comparisons = 0
            self.r.search_structural(str(n))
            self.assertLessEqual(self.r.index.comparisons, bound + 3, n)                 # O(log n) + contiguous occurrences
        self.assertEqual(self.r.text_scans, 0)                                           # the runtime text is never scanned
        self.assertEqual(self.r.scanned_bytes, 0)
        self.lin.search_structural('230')
        self.assertGreater(self.lin.scanned_bytes, 400000)                               # what the old path read

    def test_landing_context_reread_is_bounded(self):
        worst_old = worst_new = 0
        for o, _, t in self.r.map:
            if not re.fullmatch(r'(CF88|ADCT):ART\.\d+(-[A-Z])?', t):
                continue
            top = self.r.land_top(o)
            new, _ = self.r.context_reread(top)
            worst_new, worst_old = max(worst_new, new), max(worst_old, min(top, 262144))
        self.assertLess(worst_new, 8192)                                                  # bytes from the TEXT_MAP row, not from the start
        self.assertGreater(worst_old, 250000)
        self.assertEqual(self.r.context_reread(self.r.land_top(685)), (self.r.land_top(685), False))   # near the start: no seed (cheaper)


class FailClosedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = V.ARTIDX.read_bytes()
        cls.data = (SD1 / '05_TEXT/CF88_RUNTIME.txt').read_bytes()

    def assert_invalid(self, blob, data, code):
        with self.assertRaises(AI.IndexError_) as cm:
            AI.ArticleIndex(blob, data)
        self.assertEqual(str(cm.exception), code)

    def test_rejections(self):
        b = bytearray(self.blob)
        b[200] ^= 1
        self.assert_invalid(bytes(b), self.data, 'BODY_HASH')                            # any record changed
        self.assert_invalid(self.blob, self.data + b' ', 'SOURCE_MISMATCH')             # different text: offsets never used
        b = bytearray(self.blob)
        b[8] = 2
        self.assert_invalid(bytes(b), self.data, 'SCHEMA')
        self.assert_invalid(self.blob[:50], self.data, 'SHORT')

    def test_reader_falls_back_safely(self):
        with tempfile.TemporaryDirectory() as t:
            bad = Path(t) / 'x.idx'
            b = bytearray(self.blob)
            b[300] ^= 0xFF
            bad.write_bytes(bytes(b))
            r = V.Reader(SD1, artidx=bad)
            self.assertTrue(r.index_state.startswith('INVALID'))
            self.assertIsNone(r.index)                                                   # INDEX_INVALID_FALLBACK_LINEAR
            self.assertEqual(walk(r, 5), [2507, 430836])                                 # still correct (structural linear)


class SyntheticNormTest(unittest.TestCase):
    """2.500 articles (+200 of a second structure, remissions at line starts): lookup cost does not grow with the article number."""

    @classmethod
    def setUpClass(cls):
        cls.data, idx = BM.synthetic_norm(2500)
        cls.tmp = tempfile.mkdtemp(prefix='artidx_fx_')
        (Path(cls.tmp) / 'T.txt').write_bytes(cls.data)
        (Path(cls.tmp) / 'I.json').write_text(json.dumps(idx), encoding='utf-8')
        cls.blob, cls.man = AI.build(Path(cls.tmp) / 'T.txt', Path(cls.tmp) / 'I.json')
        cls.idx = AI.ArticleIndex(cls.blob, cls.data)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def cmp(self, k, start=0):
        self.idx.comparisons = 0
        hit = self.idx.find(k, 0, start)
        return hit, self.idx.comparisons

    def test_size(self):
        self.assertEqual(self.man['records'], 2700)
        self.assertEqual(len(self.blob), 96 + 2 * 16 + 2700 * 12)                       # 32.528 B: tens of KB
        self.assertLess(len(self.blob), 64 * 1024)

    def test_art10_vs_art2400(self):
        (o10, ns10, _), c10 = self.cmp(10)
        (o2400, ns2400, _), c2400 = self.cmp(2400)
        self.assertEqual((ns10, ns2400), ('F1', 'F1'))
        self.assertTrue(self.data[o2400:].startswith(b'Art. 2400.'))
        bound = math.ceil(math.log2(2700)) + 2
        self.assertLessEqual(max(c10, c2400), bound)                                     # ~12-13, never ~2.500
        self.assertLessEqual(abs(c10 - c2400), 2)
        self.assertGreater(o2400 / o10, 100)                                              # while the text distance grows > 100x

    def test_second_structure_and_remissions(self):
        first, _ = self.cmp(10)
        second, c = self.cmp(10, first[0] + 1)
        self.assertEqual((second[1], second[2]), ('F2', 1))
        self.assertIsNone(self.cmp(10, second[0] + 1)[0])
        for m in re.finditer(rb'(?m)^art\. (\d+) da Lei', self.data):
            self.assertNotIn(m.start(), {r[3] for r in self.idx.recs})


@unittest.skipUnless(V.ARTIDX.is_file() and (SD3 / '10_TARGETS/CF88_TARGETS.IDX').is_file(), 'index / RUN3 staging not built')
class UxPreservedWithIndexTest(unittest.TestCase):
    def test_flows(self):
        r = V.Reader(SD3, artidx=V.ARTIDX)
        m = V.ArticleSearchV1(r).keys('ENTER', '5', 'ENTER')
        self.assertEqual(m.view()['active_target'], 'CF88:ART.5')
        self.assertEqual(m.view()['rows'][r.ACTIVE]['offset'], 2507)                     # centered
        m.keys('ENTER', 'ENTER')
        self.assertEqual(m.view()['active_target'], 'ADCT:ART.5')
        m.keys('ENTER', 'ENTER')
        self.assertEqual((m.messages, m.view()['active_target']), (['SEM OUTRA OCORRENCIA'], 'ADCT:ART.5'))
        m.keys('ENTER', '1', '9', '3', 'ENTER')
        v = m.view()
        self.assertEqual((v['active_target'], v['layer4'], len(v['works'])), ('CF88:ART.193', True, 3))
        m.keys('ENTER', '3', '7', 'ENTER', '4')
        self.assertEqual((m.opened[-1]['target'], sorted(m.opened[-1]['works'])), ('CF88:ART.37', ['Os Donos do Poder', 'Raízes do Brasil']))
        self.assertEqual(r.text_scans, 0)


class FirmwareContractTest(unittest.TestCase):
    def test_indexed_branch_first_and_no_scan(self):
        f = func(INO, 'static bool lexV1PesquisarArtigoEstrutural(const String &n, uint32_t inicio)\n{')
        fast = f[f.index('if(lexV1ArtIdxPronto()){'):f.index('if(LEXV1_ARTSEARCH_LOG){')]   # CC_INDEX: any text with its own index
        self.assertNotIn('pesquisarArtigo(', fast)                                       # no text scan in the fast path
        self.assertNotIn('SD.open', fast)
        for s in ('lexV1ArtIdxBuscar(num,0,inicio,off,occ,ns,lexV1ArtUltima.comparacoes)', 'reiniciarIndice(off);',
                  'offsetUltimaOcorrencia=off;', 'inicioProximaBusca=off+1;', 'temOcorrenciaDaBusca=true;', 'if(!achou) return false;'):
            self.assertIn(s, fast, s)
        self.assertLess(f.index('lexV1ArtIdxPronto()'), f.index('while(pesquisarArtigo(n,inicio)){'))
        self.assertIn('[ARTIDX] FALLBACK_LINEAR', f)

    def test_lookup_is_binary(self):
        f = func(INO, 'static bool lexV1ArtIdxBuscar(uint16_t num, uint8_t suf, uint32_t inicio, uint32_t &off, uint16_t &occ, uint8_t &ns, uint32_t &cmp)\n{')
        self.assertIn('while(lo<hi){', f)
        self.assertIn('uint32_t mid=(lo+hi)/2; cmp++;', f)
        self.assertNotIn('SD.', f)                                                      # in-memory only

    def test_loader_fail_closed(self):
        # CC_INDEX: generic loader. lexV1ArtIdxCarregar validates; lexV1ArtIdxPronto binds the index to the OPEN text.
        f = func(INO, 'static bool lexV1ArtIdxCarregar(const char *caminho, const char *shaTexto, uint32_t t0)\n{')
        for s in ('memcmp(b,"LXARTIX1",8)!=0', 'lexV1Le16(b+8)!=1', 'lexV1Le32(b+20)!=tamanhoArquivoAtual', 'strcmp(hex,shaTexto)!=0',
                  'memcmp(dig,b+56,32)!=0', 'MALLOC_CAP_SPIRAM', 'LexV1FileReader f;', 'f.fechar();'):
            self.assertIn(s, f, s)
        p = func(INO, 'static bool lexV1ArtIdxPronto()\n{')
        for s in ('lexV1ArtIdx.texto!=caminhoArquivoAtual || lexV1ArtIdx.textoBytes!=tamanhoArquivoAtual', 'lexV1ArtIdxLiberar();',
                  'nome.endsWith(LEXV1_ARTIDX_SUFIXO)', 'lexV1Le32(h+20)!=tamanhoArquivoAtual', 'lexV1ShaTextoAtual(sha)',
                  'strcmp(shaHeader[c],sha)!=0', 'lexV1ArtIdx.estado=2;'):
            self.assertIn(s, p, s)
        self.assertNotIn('CF88', p + f)
        self.assertIn('lexV1ArtIdxLiberar();', func(INO, 'static bool lexV1ArtIdxInvalido(const char *motivo)\n{'))
        self.assertIn('heap_caps_free(lexV1ArtIdx.buf)', func(INO, 'static void lexV1ArtIdxLiberar()\n{'))

    def test_context_seed_hook(self):
        r = func(INO, 'void reconstruirContextoAntesOffset(uint32_t limite, ContextoJuridicoAtivo &saida)\n{')
        hook = r[r.index('#if LEX_DEVICE_V1_ENABLED'):r.index('#endif')]
        self.assertIn('limite-base>LEXV1_CTX_SEMENTE_MIN && lexV1ContextoEstruturalAntes(limite,base,inicioMapa,saida)', hook)
        c = func(INO, 'bool lexV1ContextoEstruturalAntes(uint32_t limite, uint32_t checkpoint, uint32_t &inicio, ContextoJuridicoAtivo &saida)\n{')
        self.assertIn('if(!lexV1CamadaV1Aplicavel()', c.replace('limite==0 || ', ''))
        self.assertIn('if(checkpoint>=ini) return false;', c)

    def test_landing_has_no_textmap_io_and_logs(self):
        f = func(INO, 'static void lexV1PousarBuscaNaLinhaAtiva(uint32_t ocorrencia)\n{')
        self.assertNotIn('lexv1TargetAtOffset', f)
        self.assertIn('const int alvo=linhaContextoAtivo(LEITOR_LINHAS_VISIVEIS);', f)
        for s in ('[ARTSEARCH] q=%s modo=%s', 'lookup_us=%lu landing_ms=%lu render_ms=%lu total_ms=%lu', 'records=%lu bytes=%lu', '[ARTIDX] LOADED %s'):
            self.assertIn(s, INO, s)

    def test_flag0_unchanged(self):
        self.assertEqual(strip_v1(INO), strip_v1(OLD))
        for s in ('lexV1ArtIdx', 'LXARTIX1', 'lexV1ContextoEstruturalAntes', 'ARTSEARCH'):
            self.assertNotIn(s, strip_v1(INO), s)


if __name__ == '__main__':
    unittest.main()
