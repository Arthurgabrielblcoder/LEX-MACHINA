"""REFERÊNCIAS Nº 4 R1 on the DEVICE simulator + host-only package. Read-only: firmware folder, baseline header and physical SD untouched.

Layer 4 = WORK_REFERENCE rows of the query keys of the ACTIVE_TARGET (ART.n -> [ART.n, ART.n:CAPUT]; anything else -> itself) with the
W flag of CF88_TARGETS.IDX. CORRELATA C3B.2 invariants are re-checked on the same candidate SD (Correlatas 1 is frozen).
"""
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DI = ROOT / 'DEVICE_INTEGRATION'
sys.path.insert(0, str(DI / 'tools'))
import canonical_layer_audit as A  # noqa: E402
import device_lookup_simulator as S  # noqa: E402

SD = DI / 'staging_sd_v1_references4_r1_candidate/SD'
PKG = ROOT / 'REFERENCE_COVERAGE_AUDIT/REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY'
C3B2 = ROOT / 'CORRELATA_COVERAGE_AUDIT/C3B2_PHYSICAL_TEST_PACKAGE/candidate/SD'
C3B2_STAGING = DI / 'C3B2_CORRELATA_PROMOTION/STAGING_FILE_MANIFEST.json'
RUN5 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate'
HDR = RUN5 / 'device_candidate/lex_ref_detail_data.RUN5_CANDIDATE.h'
HDR_BASE = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h'
REF, COR = A.REFERENCIA, A.CORRELATA


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def c_unescape(s):
    return bytes(s.replace('""', ''), 'latin-1').decode('unicode_escape').encode('latin-1').decode('utf-8')


def header_table(p):
    """{key: (titulo, tipo, ano, nota10, sobre, fonte)} parsed from the generated C table, in file order."""
    txt = Path(p).read_text(encoding='utf-8')
    out = {}
    for m in re.finditer(r'\n  \{("(?:[^"\\]|\\.|"")*?"), ("(?:[^"\\]|\\.|"")*?"), ("(?:[^"\\]|\\.|"")*?"), (\d+), (-?\d+),\n   '
                         r'("(?:[^"\\]|\\.|"")*?"),\n   ("(?:[^"\\]|\\.|"")*?"),\n   ("(?:[^"\\]|\\.|"")*?"), ("(?:[^"\\]|\\.|"")*?"), '
                         r'("(?:[^"\\]|\\.|"")*?")\},', txt):
        g = [c_unescape(x[1:-1]) if x.startswith('"') else int(x) for x in m.groups()]
        out[g[0]] = (g[1], g[2], g[3], g[4], g[5], g[9])
    return out, int(re.search(r'#define LEXV1_REF_DETAIL_COUNT (\d+)', txt).group(1))


def busca_detalhe(keys, tid, fonte):             # mirror of lexV1BuscarDetalhe (strcmp binary search)
    k = f'{tid}|{fonte}'.encode('utf-8')
    lo, hi = 0, len(keys) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        c = keys[mid].encode('utf-8')
        if c == k:
            return keys[mid]
        lo, hi = (mid + 1, hi) if c < k else (lo, mid - 1)
    return None


class DetailHeaderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t, cls.n = header_table(HDR)
        cls.t0, cls.n0 = header_table(HDR_BASE)
        cls.keys = list(cls.t)

    def test_counts_and_old_entries(self):
        self.assertEqual((self.n0, len(self.t0), self.n, len(self.t)), (122, 122, 124, 124))
        self.assertEqual({k: v for k, v in self.t.items() if k in self.t0}, self.t0)
        self.assertEqual(sorted(set(self.t) - set(self.t0)), ['CF88:ART.196|R1A-DOC-001', 'CF88:ART.206:INC.I|R1A-DOC-002'])
        self.assertEqual(self.keys, sorted(self.keys, key=lambda k: k.encode('utf-8')))

    def test_new_details(self):
        s = self.t['CF88:ART.196|R1A-DOC-001']
        self.assertEqual(s[:4], ('Sicko - S.O.S. Saúde', 'DOCUMENTÁRIO', 2007, 74))
        self.assertIn('Michael Moore', s[4])
        self.assertTrue(s[5].startswith('R1A-DOC-001'))
        p = self.t['CF88:ART.206:INC.I|R1A-DOC-002']
        self.assertEqual(p[:4], ('Pro Dia Nascer Feliz', 'DOCUMENTÁRIO', 2005, 80))
        self.assertIn('João Jardim', p[4])
        self.assertEqual(busca_detalhe(self.keys, 'CF88:ART.196', 'R1A-DOC-001'), 'CF88:ART.196|R1A-DOC-001')
        self.assertEqual(busca_detalhe(self.keys, 'CF88:ART.206:INC.I', 'R1A-DOC-002'), 'CF88:ART.206:INC.I|R1A-DOC-002')
        for k in self.t0:                                                              # every old ficha still found
            self.assertEqual(busca_detalhe(self.keys, *k.split('|')), k)

    def test_baseline_header_untouched(self):
        self.assertEqual(sha(HDR_BASE), '2ca5820a170a3b08ecfa869685d319d65eee5bc94ddf0bfa5854282acce9710b')


class HostOnlyPackageTest(unittest.TestCase):
    def test_package_manifest_and_rollback(self):
        m = json.loads((PKG / 'REFERENCES_4_R1_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual((m['status'], m['physical_approved'], m['card_touched'], m['device_flashed']), ('HOST_ONLY_CANDIDATE', False, False, False))
        self.assertTrue(m['c3b2_baseline_reproduced'] and m['byte_identical_rebuild'] and m['device_manifest_matches_package'])
        self.assertEqual(m['changed_vs_c3b2'], ['99_LEX_V1/00_SYS/LEXV1.VER', '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json',
                                                '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX', '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX',
                                                '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'])
        self.assertEqual(sorted(m['targets_r_only_divergence_vs_generator'])[:0], [])
        self.assertEqual(len(m['targets_r_only_divergence_vs_generator']), 25)        # 23 of C3B.2 + the 2 new targets (R kept)
        base = {f['path'].lstrip('/'): f['sha256'] for f in json.loads(C3B2_STAGING.read_text(encoding='utf-8'))['files']}
        for d in m['file_diff']:
            rel = d['path'].lstrip('/')
            self.assertEqual(sha(PKG / 'rollback/SD' / rel), base[rel], rel)          # rollback = C3B.2 approved bytes
            self.assertEqual(sha(PKG / 'candidate/SD' / rel), d['after_sha256'], rel)
        for name, rel in (('REF_LOOKUP.IDX', '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX'), ('REF_PAYLOAD.IDX', '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'),
                          ('CF88_TARGETS.IDX', '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX')):
            self.assertEqual(sha(PKG / 'candidate/SD' / rel), sha(RUN5 / 'device_ready' / name), name)
        ver = (PKG / 'candidate/SD/99_LEX_V1/00_SYS/LEXV1.VER').read_text(encoding='utf-8')
        self.assertIn('REFERENCE_ENGINE|cf-reference-engine-run5-references4-r1', ver)
        self.assertNotIn('99_RELATIONS_V2', ' '.join(m['changed_vs_c3b2']))


@unittest.skipUnless((SD / '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX').is_file(), 'R1 staging candidate not built')
class R1DeviceLayersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = S.Device(SD / '99_LEX_V1')
        cls.flags = {p[0]: p[3] for p in A.rows(SD / '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX')}
        cls.mapped = {p[2] for p in A.rows(SD / '99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX')}
        cls.rel = {r[5]: r for r in A.rows(SD / '99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX')}

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def layer(self, short, layer):
        return sorted(r[6] for r in A.device_query_union(self.dev, S.Device.canonical(short))[0].get(layer, []))

    def available(self, short, layer):
        tid = S.Device.canonical(short)
        return any(A.flag(self.flags.get(k, '------'), layer) for k in A.query_keys(tid))

    def check(self, short, expected):
        self.assertIn(S.Device.canonical(short), self.mapped, short)
        self.assertEqual(self.layer(short, REF), sorted(expected), short)
        self.assertEqual(self.available(short, REF), bool(expected), short)

    def test_new_references(self):
        self.check('CF88.196', ['Sicko - S.O.S. Saúde'])
        self.check('CF88.206.I', ['Pro Dia Nascer Feliz'])

    def test_no_propagation(self):
        for short in ('CF88.206', 'CF88.206.II', 'CF88.206.III', 'CF88.197', 'CF88.195', 'CF88.196.UNICO'):
            if S.Device.canonical(short) in self.mapped:
                self.check(short, [])

    def test_old_references_unchanged(self):
        self.check('CF88.37', ['Os Donos do Poder', 'Raízes do Brasil'])
        self.check('CF88.193', ['Capital no Século XXI', 'Desigualdade para Todos', 'O Triunfo da Injustiça'])
        self.check('ADCT.68', ['Torto Arado'])
        self.check('CF88.201.I', ['Eu, Daniel Blake'])
        for art in ('CF88:ART.98', 'CF88:ART.202'):                                     # CONFIRMED_REFERENCE_GAP
            for t in [t for t in self.mapped if t == art or t.startswith(art + ':')]:
                self.assertEqual(A.device_query_union(self.dev, t)[0].get(REF, []), [], t)
                self.assertFalse(any(A.flag(self.flags.get(k, '------'), REF) for k in A.query_keys(t)), t)

    def test_correlatas_c3b2_critical_routes(self):
        cases = {'CF88:ART.202:PAR.5': ('EXT_LC108_2001', '26'), 'CF88:ART.158:PAR.1:INC.I': ('EXT_LC63_1990', '3'),
                 'CF88:ART.202': ('EXT_LC109_2001', '1')}
        for tid, (norm, art) in cases.items():
            rows = A.device_query_union(self.dev, tid)[0].get(COR, [])
            self.assertEqual([r[5] for r in rows], [norm], tid)
            self.assertTrue(self.available(tid, COR), tid)
            rid = rows[0][4].split(':', 1)[1].split('@')[0]
            self.assertEqual(self.rel[rid][6], norm, tid)                              # REFERENCE_ID -> exactly that RELACOES row
            self.assertIn(art, self.rel[rid][9].split(','), tid)
        self.assertFalse(self.available('CF88:ART.37:PAR.3:INC.III', COR))             # no ghost 1 CORR.

    def test_correlata_device_ready_set_and_c_flags(self):
        payload = A.rows(SD / '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX')
        base = A.rows(C3B2 / '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX')
        cor = sorted(r for r in payload if r[1] == 'CORRELATA')
        self.assertEqual(cor, sorted(r for r in base if r[1] == 'CORRELATA'))
        visible = {r[0] for r in cor if r[2] == 'CURRENT_VISIBLE'}
        self.assertEqual(sum(r[2] == 'CURRENT_VISIBLE' for r in cor), 24)
        self.assertEqual({t for t, f in self.flags.items() if f[1] == 'C'}, visible)
        ids = [r[4].split(':', 1)[1].split('@')[0] for r in cor if r[2] == 'CURRENT_VISIBLE']
        self.assertEqual(len(ids), len(set(ids)))
        for i in ids:
            self.assertIn(i, self.rel)
        for name in ('RELACOES.IDX', 'REL_LOOKUP.IDX', 'EXT_ARTIGOS.IDX'):
            self.assertEqual(sha(SD / '99_RELATIONS_V2/05_INDICES_ESP32_V2' / name), sha(C3B2 / '99_RELATIONS_V2/05_INDICES_ESP32_V2' / name), name)


if __name__ == '__main__':
    unittest.main()
