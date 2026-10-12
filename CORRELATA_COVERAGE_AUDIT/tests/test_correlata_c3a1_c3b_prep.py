"""C3A.1 (relation types, candidate EXT_ARTIGOS repair) + C3B PREP (physical test package, prepared only)."""
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
import build_c3b_package as P  # noqa: E402

REG = R4.load(R4.REGISTER)['records']
ADDS = R4.load(R4.ADDITIONS)['records']
SUMMARY = R4.load(R4.OUT / 'RUN4_CANDIDATE_SUMMARY.json')
VIEW = R4.load(R4.OUT / 'legal_view/CF88_CORRELATA_LEGAL_VIEW.json')
DEV = R4.OUT / 'device_ready'
PKG = P.OUT
DIFF = json.loads((PKG / 'C3B_FILE_DIFF.json').read_text(encoding='utf-8'))
PHYS = P.physical()
TEXTS = R4.ext_texts()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rec(target, key):
    return next(r for r in REG if r['target_id'] == target and r['destination_norm_key'] == key)


def ext_offset(index_bytes, nid, art):
    """Firmware-style (buscarOffsetArtigoExternoV2): linear scan, fields 0/1 match, offset = field 2."""
    for l in index_bytes.decode('utf-8').split('\n'):
        l = l.strip()
        if l and l[0] != '#' and l.split('|')[0] == nid and l.split('|')[1] == art:
            return int(l.split('|')[2])
    return None


class RelationTypes(unittest.TestCase):
    def test_01_no_unclassified(self):
        for doc in (REG, ADDS):
            self.assertFalse([r for r in doc if r['relation_type'] == O.UNCLASSIFIED_RELATION_TYPE or r['relation_type'] not in O.RELATION_TYPES])
        self.assertEqual(SUMMARY['device_ready']['unclassified_relation_types'], 0)
        r = copy.deepcopy(ADDS[0])
        r['relation_type'] = O.UNCLASSIFIED_RELATION_TYPE
        with self.assertRaises(O.OverlayError) as e:
            O.validate_records([r], R4.context(E.TargetRegistry()))
        self.assertEqual(e.exception.code, 'RELATION_TYPE_INVALID')

    def test_02_04_types(self):
        exp = {('CF88:ART.158:PAR.1:INC.I', 'LC:63/1990'): ('REGULAMENTA', None),
               ('CF88:ART.195:INC.I:AL.b', 'LC:70/1991'): ('IMPLEMENTA', '2027-01-01'),
               ('CF88:ART.214:CAPUT', 'LEI:15388/2026'): ('EXECUTA_POLÍTICA_CONSTITUCIONAL', '2036-04-14')}
        for k, (t, rv) in exp.items():
            r = rec(*k)
            self.assertEqual((r['relation_type'], r['revalidate_on']), (t, rv), k)
            self.assertTrue(r['relation_type_basis'])
            self.assertIn(f'C3A1:RELATION_TYPE:{k[0]}', r['decision_ids'])
            self.assertIn(r, ADDS)
        self.assertIn('ANNEX_ROUTE_SUPPORT', rec('CF88:ART.214:CAPUT', 'LEI:15388/2026')['relation_type_basis'])
        self.assertEqual(len([r for r in REG if r['destination_norm_key'] == 'LEI:15388/2026']), 1)      # no fan-out recreated


class ArticleIndex(unittest.TestCase):
    IDX = (DEV / 'EXT_ARTIGOS.IDX').read_bytes()

    def jump(self, nid, art, origin, expected):
        off = ext_offset(self.IDX, nid, art)
        self.assertIsNotNone(off)
        self.assertTrue(TEXTS[nid][off:].decode('utf-8').startswith(expected), (nid, art))
        self.assertIsNone(ext_offset((R4.CARD / 'EXT_ARTIGOS.IDX').read_bytes(), nid, art))       # was missing on the card
        row = next(l.split('|') for l in (DEV / 'RELACOES.IDX').read_text(encoding='utf-8').splitlines() if l.startswith(origin))
        self.assertEqual((row[6], row[8], row[9]), (nid, 'ABRIR_ARTIGO_INTERNO', art))

    def test_05_lc87_art10_direct(self):
        self.jump('EXT_LC87_1996', '10', 'CF88|150|7|||', 'Art.\n10. É assegurado ao contribuinte substituído o direito à\nrestituição')

    def test_06_lei7998_art9_direct(self):
        self.jump('EXT_LEI7998_1990', '9', 'CF88|239|3|||', 'Art. 9º É assegurado o recebimento de abono salarial anual')

    def test_07_no_device_ready_depends_on_missing_article(self):
        self.assertEqual(SUMMARY['device_ready']['device_article_gaps'], 0)
        for l in (DEV / 'RELACOES.IDX').read_text(encoding='utf-8').splitlines():
            r = l.split('|')
            if l[0] != '#' and r[8] == 'ABRIR_ARTIGO_INTERNO':
                for a in r[9].split(','):
                    self.assertIsNotNone(ext_offset(self.IDX, r[6], a), (r[6], a))
        by_decision = [e for e in VIEW['entries'] if e.get('device_article_resolution') == 'OPEN_NORM_START_BY_DECISION']
        self.assertTrue(all(e['kind'] == 'LEGACY' and e['action'] == 'KEEP' for e in by_decision))
        audit = R4.load(AUDIT / 'C3A/inputs/ext_index_audit.json')
        self.assertEqual(audit['counts']['OFFSET_NOT_AT_HEADING'], 0)
        # only the two proven entries were added; the predecessors' sizes were cut, nothing else changed
        base = set((R4.CARD / 'EXT_ARTIGOS.IDX').read_text(encoding='utf-8').splitlines())
        cand = set(self.IDX.decode('utf-8').splitlines())
        self.assertEqual(sorted(l.split('|')[:2] for l in cand - base),
                         [['EXT_LC87_1996', '10'], ['EXT_LC87_1996', '9'], ['EXT_LEI7998_1990', '8-C'], ['EXT_LEI7998_1990', '9']])
        self.assertEqual(len(base - cand), 2)

    def test_08_fallback_still_works(self):
        ctx = R4.context(E.TargetRegistry())
        self.assertEqual(O.device_route('EXT_LC63_1990', ['999'], ctx), ('ABRIR_NORMA_SEM_SALTO', [], ['999']))
        with self.assertRaises(O.OverlayError) as e:
            O.repair_ext_artigos((R4.CARD / 'EXT_ARTIGOS.IDX').read_bytes(), {('EXT_LC87_1996', '999')}, TEXTS)
        self.assertEqual(e.exception.code, 'ARTICLE_HEADING_NOT_UNIQUE')
        with self.assertRaises(O.OverlayError) as e:
            O.repair_ext_artigos((R4.CARD / 'EXT_ARTIGOS.IDX').read_bytes(), {('EXT_LC63_1990', '99')}, TEXTS)
        self.assertEqual(e.exception.code, 'EXT_TEXT_REQUIRED_FOR_INDEX_REPAIR')


class Package(unittest.TestCase):
    def files(self, part):
        d = PKG / part / 'SD'
        return {p.relative_to(d).as_posix(): p.read_bytes() for p in d.rglob('*') if p.is_file()}

    def test_09_only_modified_files(self):
        cand, rb = self.files('candidate'), self.files('rollback')
        self.assertEqual(set(cand), {f['path'] for f in DIFF['files']})
        self.assertEqual(set(cand), set(rb))
        for p in cand:
            self.assertNotEqual(sha(cand[p]), sha(rb[p]), p)
            self.assertEqual(sha(cand[p]), next(f['candidate_sha256'] for f in DIFF['files'] if f['path'] == p))
        self.assertEqual(len(cand), 5)

    def test_10_rollback_is_physical_baseline(self):
        rb = self.files('rollback')
        man = json.loads((PKG / 'C3B_ROLLBACK_MANIFEST.json').read_text(encoding='utf-8'))
        for f in man['files']:
            self.assertEqual(sha(rb[f['path']]), PHYS[f['path']]['sha256'])
            self.assertEqual(len(rb[f['path']]), PHYS[f['path']]['bytes'])
            self.assertEqual(f['sha256'], PHYS[f['path']]['sha256'])

    def test_11_12_firmware_cache_limits(self):
        cand = self.files('candidate')
        look = [l for l in cand['99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX'].decode().splitlines() if l and l[0] != '#']
        rel = [l.split('|') for l in cand['99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX'].decode().splitlines() if l and l[0] != '#']
        self.assertLessEqual(len(look), 64)
        self.assertLessEqual(len({r[6] for r in rel}), 32)
        self.assertEqual((len(look), len({r[6] for r in rel})), (26, 15))

    def test_13_non_correlata_unchanged(self):
        cand, rb = self.files('candidate'), self.files('rollback')
        p = '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'
        self.assertEqual(P.payload_split(cand[p])[0], P.payload_split(rb[p])[0])
        self.assertTrue(DIFF['isolation']['non_correlata_identical'])
        for path in cand:
            self.assertTrue(path.startswith(P.CORRELATA_LAYER_DIRS) and not path.startswith(P.FORBIDDEN_DIRS), path)
        self.assertFalse([k for k in cand if '/10_TARGETS/' in k or '/05_TEXT/' in k or '/30_ENTENDA/' in k])

    def test_14_firmware_unchanged(self):
        for base in ('9108d72812802de941e54b7e4e3ec556b7abd019', '7c6d421585d971e5eef6af2bc3fa85ccab078d83'):
            out = subprocess.run(['git', 'diff', '--name-only', base, '--', 'firmware', 'DEVICE_INTEGRATION'], cwd=ROOT, capture_output=True,
                                 text=True, check=True).stdout
            self.assertEqual(out.strip(), '')

    def test_15_run4_and_package_deterministic(self):
        sums = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as t:
                R4.build(t)
                sums.append((Path(t) / 'SHA256SUMS.txt').read_bytes())
        self.assertEqual(sums[0], sums[1])
        self.assertEqual(sums[0], (R4.OUT / 'SHA256SUMS.txt').read_bytes().replace(b'\r\n', b'\n'))
        trees = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as t:
                trees.append(P.build(Path(t) / 'pkg'))
        self.assertEqual(trees[0], trees[1])
        self.assertEqual(trees[0], P.tree(PKG))


if __name__ == '__main__':
    unittest.main()
