"""Host-side tests of DEVICE INTEGRATION V1-A1: SD overlay candidate, simulator, contracts. Never touches hardware."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_sd_staging as B  # noqa: E402
import context_parser_port as C  # noqa: E402
import device_lookup_simulator as S  # noqa: E402
import reference_engine as R  # noqa: E402

STAGING = DI / 'staging_sd_v1'
SD = STAGING / 'SD' / '99_LEX_V1'


def _without_build_commit(rel, data):
    """Drop only the build-provenance fields (HEAD and its commit time) from LEXV1.VER and the manifest."""
    if rel.endswith('00_SYS/LEXV1.VER'):
        return re.sub(rb'(?m)^GIT_COMMIT\|[0-9a-f]{40}$', b'GIT_COMMIT|-', data)
    if rel.endswith('00_SYS/LEX_DEVICE_MANIFEST.json'):
        m = json.loads(data.decode('utf-8'))
        for k in ('git_commit', 'git_tags_at_commit', 'build_date'):
            m.pop(k)
        m['files'].pop('99_LEX_V1/00_SYS/LEXV1.VER')
        return m
    return data


def _rows(p):
    return [l.split('|') for l in Path(p).read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]


@unittest.skipUnless((SD / '00_SYS/LEX_DEVICE_MANIFEST.json').is_file(), 'staging not built (run tools/build_sd_staging.py)')
class DeviceIntegrationV1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = S.Device(SD)
        cls.manifest = json.loads((SD / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
        cls.ent = _rows(SD / '30_ENTENDA/ENTENDA_LOOKUP.IDX')

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def test_entenda_163_only_approved(self):
        direct = [r for r in self.ent if r[7] == 'DIRECT']
        self.assertEqual(len(direct), 163)
        self.assertEqual(self.manifest['entenda_explanation_count'], 163)
        self.assertEqual(self.manifest['entenda_scope'], 'CF88_ARTS_1_24_PLUS_APPROVED_PILOTS')
        self.assertEqual(sorted(self.manifest['entenda_pilots_included']), sorted(B.APPROVED_PILOTS))
        self.assertEqual(len(B.APPROVED_PILOTS), 9)
        self.assertTrue(all(r[6] == 'HUMAN_APPROVED_T1' for r in self.ent))
        payload = (SD / '30_ENTENDA/ENTENDA_PAYLOAD.DAT').read_bytes()
        for bad in (b'PENDING_HUMAN_REVIEW', b'RETIRED', b'CHANGES_REQUESTED'):
            self.assertNotIn(bad, payload)
        for r in self.ent:
            if r[7] == 'DIRECT' and r[0] not in B.APPROVED_PILOTS:
                self.assertRegex(r[0], r'^CF88:ART\.([1-9]|1\d|2[0-4])(:|$)')

    def test_payload_identical_to_approved_batches(self):
        """Unification only re-packs: each explanation's payload bytes equal the approved batch payload."""
        approved = {}
        for b in B.BATCHES + ('pilot_t1',):
            bd = ROOT / 'ENTENDA_ENGINE/derived' / b
            data = (bd / 'ENTENDA_PAYLOAD.DAT').read_bytes()
            for r in _rows(bd / 'ENTENDA_LOOKUP.IDX'):
                if r[7] == 'DIRECT':
                    approved[r[0]] = data[int(r[1]):int(r[1]) + int(r[2])]
        data = (SD / '30_ENTENDA/ENTENDA_PAYLOAD.DAT').read_bytes()
        for r in self.ent:
            if r[7] == 'DIRECT':
                self.assertEqual(data[int(r[1]):int(r[1]) + int(r[2])], approved[r[0]], r[0])

    def test_block_and_direct_resolution(self):
        r = self.dev.query('CF88.5.V')
        self.assertEqual((r['resolution_type'], r['anchor_target_id']), ('COVERED_BY_BLOCK', 'CF88:ART.5:INC.IV'))
        self.assertIn('incisos IV, V, IX e XIV', r['display_title'])
        a = self.dev.query('CF88.5.IV')
        self.assertEqual(a['resolution_type'], 'DIRECT')
        self.assertEqual((a['payload_offset'], a['payload_length']), (r['payload_offset'], r['payload_length']))  # shared, not duplicated
        for q, anchor in (('CF88.12.5', 'CF88:ART.12:PAR.4'), ('CF88.24.4', 'CF88:ART.24:PAR.3'), ('CF88.22.V', 'CF88:ART.22:INC.IV')):
            x = self.dev.query(q)
            self.assertEqual((x['resolution_type'], x['anchor_target_id']), ('COVERED_BY_BLOCK', anchor), q)
        for q in ('CF88.5', 'CF88.7.XII', 'CF88.8.I', 'CF88.20.XI', 'CF88.21.XXIV', 'CF88.22.XXIX'):
            x = self.dev.query(q)
            self.assertEqual((x['resolution_type'], x['anchor_target_id']), ('DIRECT', S.Device.canonical(q)), q)

    def test_nine_pilots(self):
        for q, tid in (('CF88.37', 'CF88:ART.37'), ('CF88.37.6', 'CF88:ART.37:PAR.6'), ('CF88.37.10', 'CF88:ART.37:PAR.10'),
                       ('CF88.60', 'CF88:ART.60'), ('CF88.60.4', 'CF88:ART.60:PAR.4'), ('CF88.60.4.IV', 'CF88:ART.60:PAR.4:INC.IV'),
                       ('CF88.150', 'CF88:ART.150'), ('CF88.225', 'CF88:ART.225'), ('ADCT.10.II', 'ADCT:ART.10:INC.II')):
            r = self.dev.query(q)
            self.assertEqual((r['status'], r['resolution_type'], r['anchor_target_id'], r['review']), ('OK', 'DIRECT', tid, 'HUMAN_APPROVED_T1'), q)
        self.assertEqual(self.dev.query('CF88.37.6')['references'], 5)
        self.assertEqual(self.dev.query('ADCT.10.II')['legal_status'], 'CURRENT')   # A2B: status from the official monovigente runtime

    def test_text_map_runtime_and_fail_closed(self):
        h = self.dev.text_map.header
        self.assertEqual(h['LEXMACHINA'], ['TEXT_MAP', '2'])
        for k in ('TARGET_ID_VERSION', 'RUNTIME_STATUS', 'SOURCE_SHA256', 'SOURCE_BYTES', 'RECORD_COUNT', 'NAMESPACE_START_ADCT',
                  'NORMALIZATION_VERSION', 'SOURCE_NAME'):
            self.assertIn(k, h)
        self.assertEqual(int(h['RECORD_COUNT'][0]), len(_rows(SD / '10_TARGETS/CF88_TEXT_MAP.IDX')))
        # A2B: the map is RUNTIME and bound to exactly the staged CF88_RUNTIME.txt bytes
        self.assertEqual((h['RUNTIME_STATUS'], h['SOURCE_NAME']), (['RUNTIME'], ['CF88_RUNTIME.txt']))
        size, digest = self.dev.verify_runtime_file()
        self.assertEqual((str(size), digest), (h['SOURCE_BYTES'][0], h['SOURCE_SHA256'][0]))
        first = int(_rows(SD / '10_TARGETS/CF88_TEXT_MAP.IDX')[0][0])
        self.assertEqual(self.dev.resolve_text_position(first, size, digest)['status'], 'OK')
        self.assertEqual(self.dev.resolve_text_position(first, size - 1, digest)['reason'], 'SOURCE_BYTES_MISMATCH')
        self.assertEqual(self.dev.resolve_text_position(first, size, '0' * 64)['reason'], 'SOURCE_SHA256_MISMATCH')
        self.assertEqual(self.dev.resolve_text_position(first, size, None)['reason'], 'SOURCE_SHA256_MISMATCH')
        # legacy card text (physical cf.txt 429.242 B) must never be resolved with this map
        self.assertEqual(self.dev.resolve_text_position(first, 429242, digest)['status'], 'FAIL_CLOSED')
        h2 = dict(h, RUNTIME_STATUS=['LEGACY_STRUCTURAL_NOT_RUNTIME'])
        self.dev.text_map.header = h2
        try:
            self.assertEqual(self.dev.resolve_text_position(first, size, digest)['reason'], 'TEXT_MAP_NOT_RUNTIME')
        finally:
            self.dev.text_map.header = h
        ver = dict(l.split('|', 1) for l in (SD / '00_SYS/LEXV1.VER').read_text(encoding='utf-8').splitlines() if not l.startswith('#'))
        self.assertEqual((ver['ENTENDA_COUNT'], ver['ENTENDA_PILOTS'], ver['RUNTIME_CF'], ver['RUNTIME_CF_SHA256'], ver['RUNTIME_CF_BYTES']),
                         ('163', '9', 'CF88_RUNTIME_RESOLVED', digest, str(size)))

    def test_layer_flags(self):
        v = self.dev.query('CF88.5.V')['layers']
        self.assertTrue(v['HAS_ENTENDA'] and v['BLOCK_COVERED'])
        p6 = self.dev.query('CF88.37.6')['layers']
        self.assertTrue(p6['HAS_ENTENDA'])
        self.assertEqual(p6['HAS_ANY_REFERENCE_ROW'], True)
        self.assertTrue(self.dev.query('CF88.18.4')['layers']['EXTERNAL_NOTES_AVAILABLE'])  # LC 230/2026 note
        rows = _rows(SD / '10_TARGETS/CF88_TARGETS.IDX')
        self.assertEqual(sum(1 for r in rows if r[3][0] == 'E'), 163)
        self.assertTrue(all(len(r[3]) == 6 for r in rows))

    def test_target_without_entenda_and_invalid(self):
        r = self.dev.query('CF88.25')
        self.assertEqual((r['status'], r['entenda_available'], r['resolution_type']), ('OK', False, 'NONE'))
        self.assertIsNone(r['parent_context'])
        for q in ('CF88.999', 'CF88.5.XCIX', 'XYZ.1', 'CF88.5.??'):
            r = self.dev.query(q)
            self.assertEqual(r['status'], 'INVALID_OR_UNKNOWN_TARGET', q)
            self.assertFalse(r['entenda_available'])
        rev = self.dev.query('CF88.7.XXIX.a')
        self.assertEqual((rev['legal_status'], rev['entenda_available']), ('REVOKED', False))

    def test_references(self):
        ref_dir = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run1'
        for tid, n in (('CF88:ART.37:PAR.6', 5), ('CF88:ART.5', 0), ('CF88:ART.100', 4)):
            got = self.dev.references(tid)
            self.assertEqual(len(got), n, tid)
            self.assertEqual(got, R.lookup_idx(tid, ref_dir / 'REF_LOOKUP.IDX', ref_dir / 'REF_PAYLOAD.IDX'))
            self.assertTrue(all(x[0] == tid for x in got))
        for n in ('REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
            self.assertEqual((SD / '20_REFERENCES' / n).read_bytes(), (ref_dir / n).read_bytes())

    def test_manifest_hashes_and_offsets(self):
        for rel, meta in self.manifest['files'].items():
            p = STAGING / 'SD' / rel
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), meta['sha256'], rel)
            self.assertEqual(p.stat().st_size, meta['bytes'], rel)
        size = (SD / '30_ENTENDA/ENTENDA_PAYLOAD.DAT').stat().st_size
        data = (SD / '30_ENTENDA/ENTENDA_PAYLOAD.DAT').read_bytes()
        for r in self.ent:
            off, n = int(r[1]), int(r[2])
            self.assertLessEqual(off + n, size)
            self.assertTrue(data[off:off + n].startswith(b'@' + r[3].encode()), r[0])
        ref = (SD / '20_REFERENCES/REF_PAYLOAD.IDX').read_bytes()
        for r in _rows(SD / '20_REFERENCES/REF_LOOKUP.IDX'):
            self.assertTrue(ref[int(r[1]):].startswith(r[0].encode() + b'|'), r[0])
        for p in (SD / '10_TARGETS/CF88_TARGETS.IDX', SD / '30_ENTENDA/ENTENDA_LOOKUP.IDX', SD / '20_REFERENCES/REF_LOOKUP.IDX', SD / '10_TARGETS/CF88_TEXT_MAP.IDX'):
            keys = [r[0].encode() for r in _rows(p)]
            self.assertEqual(keys, sorted(keys), p.name)       # bytewise order = binary search contract
            self.assertEqual(len(keys), len(set(keys)), p.name)

    def test_no_linear_scan(self):
        b = S.bench(self.dev, 1)
        for name, bound in (('targets', 'targets'), ('entenda_lookup', 'entenda'), ('references_lookup+payload', 'references')):
            self.assertLessEqual(b[name]['max_seeks'], b['log2_bound'][bound] + 1, name)

    def test_text_resolution_strategy(self):
        self.assertEqual(self.dev.target_at_offset(0), None)
        rows = _rows(SD / '10_TARGETS/CF88_TEXT_MAP.IDX')
        by_tid = {r[2]: int(r[0]) for r in rows}
        for tid in ('CF88:ART.5:INC.V', 'CF88:ART.37:PAR.6', 'CF88:ART.24:PAR.4', 'ADCT:ART.10:INC.II'):
            off = by_tid[tid]
            self.assertEqual(self.dev.target_at_offset(off), tid)
            self.assertEqual(self.dev.target_at_offset(off + 5), tid)   # inside the device's line
        cmp = C.compare(SD / '10_TARGETS/CF88_TEXT_MAP.IDX')
        self.assertGreaterEqual(cmp['agreement'], 0.97)
        self.assertEqual(S.Device.from_context('5', '', 'V'), 'CF88:ART.5:INC.V')
        self.assertEqual(S.Device.from_context('37', '6'), 'CF88:ART.37:PAR.6')
        self.assertEqual(S.Device.from_context('1', 'unico'), 'CF88:ART.1:PAR.UNICO')

    def test_deterministic_rebuild(self):
        tmp = Path(tempfile.mkdtemp(prefix='_tmp_det_', dir=DI))
        try:
            B.build(tmp)
            a = {p.relative_to(tmp).as_posix(): p.read_bytes() for p in tmp.rglob('*') if p.is_file()}
            b = {p.relative_to(STAGING).as_posix(): p.read_bytes() for p in STAGING.rglob('*') if p.is_file()}
            self.assertEqual(sorted(a), sorted(b))
            for k in a:
                # LEXV1.VER / manifest record the HEAD they were built at; the staging deployed to the SD may predate a later
                # commit that does not touch the package, so only those provenance fields are allowed to differ.
                self.assertEqual(_without_build_commit(k, a[k]), _without_build_commit(k, b[k]), k)
        finally:
            shutil.rmtree(tmp)

    def test_builder_refuses_physical_or_outside_paths(self):
        for p in ('E:/', 'D:/99_LEX_V1', str(ROOT / 'updater'), str(ROOT)):
            with self.assertRaises(B.BuildError):
                B._guard_out(p)

    def test_approved_artifacts_and_firmware_unchanged(self):
        for path in ('ENTENDA_ENGINE/derived', 'ENTENDA_ENGINE/corpus', 'LEGAL_TARGET_ID/derived', 'firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA',
                     'firmware/LEX_MACHINA.ino'):
            self.assertEqual(subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', path], cwd=ROOT).returncode, 0, path)
        ino = ROOT / 'firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA.ino'
        self.assertEqual(hashlib.sha256(ino.read_bytes()).hexdigest(), 'fd0227e6cc6ee0e00c569b76adfaa918261d28dd557a9d5b4d9cafd9667206dc')


if __name__ == '__main__':
    unittest.main()
