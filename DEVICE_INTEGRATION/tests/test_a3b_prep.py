"""DEVICE INTEGRATION V1-A3B-PREP: schema v3 contract builder<->firmware, complete read-only diagnostic, flash integrity policy.

No host C++ compiler is available (Windows App Control); the C++ parser is exercised on the ESP32 itself by the boot self-test
(schema 2/3/4/30/3|X) and checked here statically plus against a Python mirror of the same rule.
"""
import json
import re
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
import build_sd_staging as B  # noqa: E402
import device_lookup_simulator as S  # noqa: E402
import flash_region_diff as F  # noqa: E402

FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
HDR = (FW / 'lex_device_v1.h').read_text(encoding='utf-8')
INO = (FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
SD = DI / 'staging_sd_v1/SD/99_LEX_V1'
BACKUPS = DI / 'backups'


def fw_schema():
    m = re.findall(r'^#define LEX_DEVICE_SCHEMA_VERSION (\d+)\s*$', HDR, re.M)
    assert len(m) == 1
    return int(m[0])


def device_v1_ino_sections():
    """Every region of the sketch compiled only with LEX_DEVICE_V1_ENABLED (the DEVICE V1 code paths)."""
    out, lines, depth, inside, flag0_branch = [], INO.split('\n'), 0, False, False
    for l in lines:
        s = l.strip()
        if s.startswith('#if LEX_DEVICE_V1_ENABLED'):
            inside, depth, flag0_branch = True, 1, False
            continue
        if inside:
            if s.startswith('#if'):
                depth += 1
            elif s.startswith('#else') and depth == 1:
                flag0_branch = True                       # '#else' of a V1 block = the flag0 code, not a DEVICE V1 path
                continue
            elif s.startswith('#endif'):
                depth -= 1
                if depth == 0:
                    inside = False
                    continue
            if not flag0_branch:
                out.append(l)
    return '\n'.join(out)


def mirror_parse_version_line(line, expected):
    """Python mirror of lexv1ParseDeviceVersionLine + the exact check in lexv1ReadVersion."""
    prefix = '#LEXMACHINA|DEVICE_VERSION|'
    if not line.startswith(prefix):
        return False
    d = line[len(prefix):]
    return bool(d) and len(d) <= 4 and d.isdigit() and d.isascii() and int(d) == expected


class SchemaContractTest(unittest.TestCase):
    def test_builder_equals_firmware(self):
        self.assertEqual(B.SCHEMA, 3)
        self.assertEqual(fw_schema(), B.SCHEMA)
        first = (SD / '00_SYS/LEXV1.VER').read_text(encoding='utf-8').split('\n', 1)[0]
        self.assertEqual(first, f'#LEXMACHINA|DEVICE_VERSION|{B.SCHEMA}')
        m = json.loads((SD / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual(m['schema_version'], fw_schema())

    def test_exact_version_rule(self):
        exp = fw_schema()
        self.assertTrue(mirror_parse_version_line('#LEXMACHINA|DEVICE_VERSION|3', exp))
        for bad in ('#LEXMACHINA|DEVICE_VERSION|2', '#LEXMACHINA|DEVICE_VERSION|4', '#LEXMACHINA|DEVICE_VERSION|30',
                    '#LEXMACHINA|DEVICE_VERSION|3|X', '#LEXMACHINA|DEVICE_VERSION|', '#LEXMACHINA|DEVICE_VERSION|03x', '#LEXMACHINA|TARGETS|3'):
            self.assertFalse(mirror_parse_version_line(bad, exp), bad)

    def test_firmware_source_uses_single_constant(self):
        self.assertNotIn('DEVICE_VERSION|2', HDR)
        self.assertNotIn('DEVICE_VERSION|3"', HDR)                           # no literal version string
        body = HDR[HDR.index('static inline LexV1Status lexv1ReadVersion'):]
        body = body[:body.index('\n}\n')]
        self.assertIn('v.schemaVersion != LEX_DEVICE_SCHEMA_VERSION) return LEXV1_FAIL_VERSION', body)
        parse = HDR[HDR.index('static inline int lexv1ParseDeviceVersionLine'):]
        parse = parse[:parse.index('\n}\n')]
        self.assertIn("if (*c < '0' || *c > '9') return -1;", parse)       # digits only: "3|X" rejected
        # on-device self-test covers 2 / 3 / 4 / 30 / 3|X with the real C++ code
        diag = device_v1_ino_sections()
        for name in ('schema_2_rejeitado', 'schema_3_aceito', 'schema_4_rejeitado', 'schema_30_e_3X_rejeitados'):
            self.assertIn(f'"{name}"', diag)

    def test_flag_default_off(self):
        for src in (HDR, INO):
            self.assertRegex(src, r'#ifndef LEX_DEVICE_V1_ENABLED\s*\n#define LEX_DEVICE_V1_ENABLED 0\s*\n#endif')


class DiagnosticCoverageTest(unittest.TestCase):
    CASE_RE = re.compile(r'\{"([A-Z0-9:.]+)",(true|false),LEXV1_RES_(NONE|DIRECT|COVERED_BY_BLOCK),"([A-Z0-9:.]*)",(\d+),(\d+)\}')

    def test_all_queries_and_expectations_match_simulator(self):
        cases = self.CASE_RE.findall(device_v1_ino_sections())
        ids = [c[0] for c in cases]
        self.assertEqual(ids, ['CF88:ART.5:INC.V', 'CF88:ART.21:INC.XXIV', 'CF88:ART.22:INC.XXIX', 'CF88:ART.24:PAR.4', 'CF88:ART.37:PAR.6',
                               'CF88:ART.60:PAR.4:INC.IV', 'ADCT:ART.10:INC.II', 'CF88:ART.114:INC.VIII', 'CF88:ART.25', 'CF88:ART.999'])
        dev = S.Device(SD)
        try:
            for tid, exists, res, anchor, refs, visible in cases:
                q = dev.query(tid.replace(':ART.', '.').replace(':PAR.', '.').replace(':INC.', '.'))
                self.assertEqual(q['target_id'], tid)
                self.assertEqual(q['status'] == 'OK', exists == 'true', tid)
                self.assertEqual(q['resolution_type'], res, tid)
                self.assertEqual(q.get('anchor_target_id') or '', anchor, tid)
                rows = dev.references(tid) if exists == 'true' else []
                self.assertEqual((len(rows), sum(r[2] == 'CURRENT_VISIBLE' for r in rows)), (int(refs), int(visible)), tid)
        finally:
            dev.close()

    def test_block_same_payload_as_anchor(self):
        dev = S.Device(SD)
        try:
            for t, a in (('CF88:ART.5:INC.V', 'CF88:ART.5:INC.IV'), ('CF88:ART.24:PAR.4', 'CF88:ART.24:PAR.3')):
                e, ea = dev.entenda(t), dev.entenda(a)
                self.assertEqual((e['resolution_type'], ea['resolution_type']), ('COVERED_BY_BLOCK', 'DIRECT'))
                self.assertEqual((e['payload_offset'], e['payload_length']), (ea['payload_offset'], ea['payload_length']))
        finally:
            dev.close()
        self.assertIn('"block_sem_payload_duplicado"', device_v1_ino_sections())

    def test_text_to_target_114_viii(self):
        """Mirror of lexV1OffsetEstrutural (structural labels only) + TEXT_MAP floor lookup."""
        rt = (SD / '05_TEXT/CF88_RUNTIME.txt').read_bytes()
        a = rt.index(b'\nArt. 114.')
        off = rt.index(b'\nVIII - ', a) + 1
        dev = S.Device(SD)
        try:
            size, sha = dev.verify_runtime_file()
            self.assertEqual(dev.resolve_text_position(off, size, sha)['target_id'], 'CF88:ART.114:INC.VIII')
            self.assertEqual(dev.target_at_offset(dev.text_map.header and int(dev.text_map.header['NAMESPACE_START_ADCT'][0])), 'ADCT')
            self.assertEqual(dev.resolve_text_position(off, size, '0' * 64)['status'], 'FAIL_CLOSED')
        finally:
            dev.close()
        diag = device_v1_ino_sections()
        self.assertIn('lexV1OffsetEstrutural(rtPath,"Art. 114.","VIII - ",off114,falhaRt)', diag)
        self.assertIn('"text_to_target_114_VIII"', diag)
        self.assertIn('"text_map_guard_sha_errado"', diag)

    def test_reference_zero_single_multiple(self):
        diag = device_v1_ino_sections()
        for name in ('references_zero_result', 'references_single_result', 'references_multiple_result'):
            self.assertIn(f'"{name}"', diag)
        dev = S.Device(SD)
        try:
            self.assertEqual(len(dev.references('CF88:ART.21:INC.XXIV')), 0)
            self.assertEqual(len(dev.references('CF88:ART.25')), 1)
            self.assertEqual(len(dev.references('CF88:ART.37:PAR.6')), 5)
            for r in dev.references('CF88:ART.37:PAR.6'):
                self.assertEqual((len(r), r[0]), (7, 'CF88:ART.37:PAR.6'))            # the firmware requires 6 '|' and same key
        finally:
            dev.close()

    def test_runtime_and_text_map_guards(self):
        diag = device_v1_ino_sections()
        for name in ('"RUNTIME_HASH_MATCH"', '"pinned_runtime_vs_ver"', '"text_map_runtime_guard"', '"text_map_sha256_pinned"',
                     '"lexv1_ver_device_version"', '"targets_idx"', '"entenda_lookup_idx"', '"references_lookup_idx"', 'DIAG RESULT'):
            self.assertIn(name, diag)
        self.assertRegex(HDR, r'#define LEXV1_PINNED_RUNTIME_SHA256 "7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a"')
        self.assertRegex(HDR, r'#define LEXV1_PINNED_TEXT_MAP_SHA256 "889f82002e82fb2b7d9165e6ce2a4e0dcb78d311432e268c341f1d0b1e436b96"')

    def test_timing_and_memory_instrumentation(self):
        diag = device_v1_ino_sections()
        for t in ('open_indices_us', 'runtime_sha256_us', 'text_map_lookup_us', 'us_target', 'us_lookup', 'us_entenda', 'us_payload',
                  'us_refs', 'block_resolution_us'):
            self.assertIn(t, diag)
        for api in ('ESP.getFreeHeap()', 'ESP.getMinFreeHeap()', 'ESP.getMaxAllocHeap()', 'ESP.getPsramSize()', 'ESP.getFreePsram()',
                    'ESP.getMinFreePsram()'):
            self.assertIn(api, diag)
        self.assertIn('lexV1Mem("antes_device_v1")', diag)
        self.assertIn('lexV1Mem("depois_device_v1")', diag)
        body = INO[INO.index('void lexV1DiagnosticoBoot()\n{'):]
        body = body[:body.index('\n}\n')]
        self.assertNotRegex(body, r'\b(malloc|ps_malloc|heap_caps_malloc|new\s+\w+\[)')    # no allocations just to measure

    def test_sd_read_only(self):
        code = device_v1_ino_sections() + '\n' + HDR
        for pat in (r'FILE_WRITE', r'FILE_APPEND', r'SD\.(mkdir|remove|rename|rmdir)', r'\.write\(', r'(?<!Serial)(?<!tft)\.print\w*\(', r'\bfopen\b',
                    r'\bappend\b'):
            hits = [l for l in code.split('\n') if re.search(pat, l) and 'Serial.' not in l]
            self.assertFalse(hits, (pat, hits))
        opens = re.findall(r'SD\.open\(([^)]*)\)', code)
        self.assertTrue(opens)
        self.assertTrue(all(o.rstrip().endswith('FILE_READ') for o in opens), opens)


@unittest.skipUnless((BACKUPS / 'esp32_a3b/pre_a3b_full_flash_16MB.bin').is_file(), 'flash dumps are local only (not in Git)')
class FlashIntegrityPolicyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = (BACKUPS / 'esp32/raw_flash_16MB_read1.bin').read_bytes()
        cls.pre = (BACKUPS / 'esp32_a3b/pre_a3b_full_flash_16MB.bin').read_bytes()

    def test_real_diff_confined_to_explained_nvs(self):
        r = F.compare_images(self.base, self.pre)
        self.assertEqual(r['verdict'], 'PASS')
        changed = [x for x in r['regions'] if x['changed_bytes']]
        self.assertEqual([(x['name'], x['classification'], x['changed_bytes'], x['nvs_verdict']) for x in changed],
                         [('nvs', 'MUTABLE_PERSISTENT', 1966, 'ALLOWED_EXPLAINED')])
        self.assertEqual(changed[0]['changed_nvs_keys'], [dict(namespace='phy', key='cal_data')])
        self.assertEqual((r['active_app'], r['otadata_seq'], r['partition_table_equal']), ('app0', 1, True))
        self.assertEqual([(p['name'], p['offset'], p['size']) for p in r['partitions']],
                         [('nvs', '0x9000', '0x5000'), ('otadata', '0xe000', '0x2000'), ('app0', '0x10000', '0x140000'),
                          ('app1', '0x150000', '0x140000'), ('spiffs', '0x290000', '0x160000'), ('coredump', '0x3f0000', '0x10000')])
        self.assertEqual(sum(int(x['size'], 16) for x in r['regions']), F.FLASH_SIZE)              # every byte classified

    def _mut(self, off):
        b = bytearray(self.pre)
        b[off] ^= 0xFF
        return bytes(b)

    def test_fail_closed_outside_nvs(self):
        for off in (0x100, 0x10000 + 0x1000, 0x150000 + 5, 0x290000 + 7, 0xE000 + 40, 0x800000):
            self.assertEqual(F.compare_images(self.pre, self._mut(off))['verdict'], 'BLOCK', hex(off))
        self.assertEqual(F.compare_images(self.pre, self._mut(0x3F0000 + 3))['verdict'], 'REVIEW')     # coredump: never silent

    def test_nvs_not_blanket_safe(self):
        self.assertEqual(F.compare_images(self.base, self.pre, nvs_allowed=set())['verdict'], 'BLOCK')


if __name__ == '__main__':
    unittest.main()
