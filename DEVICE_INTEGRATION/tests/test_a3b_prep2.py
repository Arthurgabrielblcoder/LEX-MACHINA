"""DEVICE INTEGRATION V1-A3B-PREP2: bounded SD file handles (FILE_DESCRIPTOR_POLICY.md).

A3B-FLASH failed on hardware with "vfs_fat: open: no free file descriptors" (SD mounted with the core default max_files=5,
diagnostic kept 7 files open). These tests pin the fix: max_files 12 only with LEX_DEVICE_V1_ENABLED, format_if_empty=false,
short-lived handles (steady 3, peak 4 <= 6), payloads on demand, FAIL_IO with type/path/stage, read-only.
"""
import re
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(DI / 'tests'))
import device_lookup_simulator as S  # noqa: E402
import fd_model as M  # noqa: E402
from test_a3b_prep import HDR, INO, SD, device_v1_ino_sections  # noqa: E402


def define(name):
    m = re.findall(rf'^#define {name} (\S+)', HDR, re.M)
    assert len(m) == 1, name
    return m[0]


def diag_body():
    s = INO[INO.index('void lexV1DiagnosticoBoot()\n{'):]
    return s[:s.index('\n}\n')]


def sd_begin_block():
    s = INO[INO.index('bool iniciarSDUmaVez()'):]
    return s[:s.index('\n}\n')]


class SdBeginTest(unittest.TestCase):
    def test_core_signature(self):
        sd_h = Path.home() / 'AppData/Local/Arduino15/packages/esp32/hardware/esp32/3.3.11/libraries/SD/src/SD.h'
        if not sd_h.is_file():
            self.skipTest('esp32 core 3.3.11 not installed here')
        sig = re.sub(r'\s+', ' ', sd_h.read_text(encoding='utf-8'))
        self.assertIn('bool begin( uint8_t ssPin = SS, SPIClass &spi = SPI, uint32_t frequency = 4000000, const char *mountpoint = "/sd", '
                      'uint8_t max_files = 5, bool format_if_empty = false );', sig)

    def test_max_files_only_with_device_v1_and_legacy_preserved(self):
        b = sd_begin_block()
        v1 = b[b.index('#if LEX_DEVICE_V1_ENABLED'):b.index('#else')]
        legacy = b[b.index('#else'):b.index('#endif')]
        self.assertEqual(re.findall(r'SD\.begin\(([^)]*)\)', v1),
                         ['SD_CS,spiBus,12000000,"/sd",LEXV1_SD_MAX_FILES,false', 'SD_CS,spiBus,4000000,"/sd",LEXV1_SD_MAX_FILES,false'])
        self.assertEqual(re.findall(r'SD\.begin\(([^)]*)\)', legacy), ['SD_CS,spiBus,12000000', 'SD_CS,spiBus,4000000'])   # v7.12.0
        self.assertEqual(int(define('LEXV1_SD_MAX_FILES')), 12 == M.SD_MAX_FILES_DEVICE_V1 and 12)
        self.assertNotRegex(INO + HDR, r'format_if_empty\s*=\s*true|,\s*true\s*\)\s*;.*SD')
        self.assertEqual(len(re.findall(r'SD\.begin\(', INO)), 4)                       # no other mount point

    def test_policy_constants(self):
        self.assertEqual((int(define('LEXV1_FD_STEADY_MAX')), int(define('LEXV1_FD_PEAK_MAX')), int(define('LEXV1_FD_HEADROOM_MIN'))),
                         (M.FD_STEADY_MAX, M.FD_PEAK_MAX, M.FD_HEADROOM_MIN))
        self.assertLessEqual(M.FD_STEADY_MAX, 4)
        self.assertLessEqual(M.FD_PEAK_MAX, 6)
        self.assertGreaterEqual(M.SD_MAX_FILES_DEVICE_V1 - M.LEGACY_RESERVE - M.FD_PEAK_MAX, M.FD_HEADROOM_MIN)


class HandleModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = S.Device(SD)
        cls.flow = M.new_flow(cls.dev)

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def test_old_flow_exceeds_default_5(self):
        r = M.replay(M.OLD_FLOW, M.SD_MAX_FILES_LEGACY)
        self.assertFalse(r['ok'])
        # exactly what A3B-FLASH logged: 5 opens succeeded, then ENTENDA_PAYLOAD, REF_PAYLOAD, the runtime sha256, the TEXT_MAP
        # sha256 and the text-position search failed ("no free file descriptors" x5)
        self.assertEqual(r['peak'], 5)
        self.assertEqual(r['failed'], ['ENTENDA_PAYLOAD', 'REF_PAYLOAD', 'CF88_RUNTIME', 'TEXT_MAP#sha', 'CF88_RUNTIME'])
        self.assertEqual(len([s for s in M.OLD_FLOW if s[0] == 'open']), 10)

    def test_new_flow_bounded(self):
        r = M.replay(self.flow, M.SD_MAX_FILES_DEVICE_V1)
        self.assertTrue(r['ok'], r)
        self.assertEqual(r['peak'], 4)
        self.assertLessEqual(r['peak'], M.FD_PEAK_MAX)
        self.assertEqual(r['final_open'], 0)
        self.assertEqual(r['duplicates'], [])                                           # never two handles to the same file
        self.assertGreaterEqual(r['headroom'], M.FD_HEADROOM_MIN)
        self.assertTrue(M.replay(self.flow, M.SD_MAX_FILES_DEVICE_V1, legacy_open=M.LEGACY_RESERVE)['ok'])
        self.assertGreaterEqual(M.replay(self.flow, M.SD_MAX_FILES_DEVICE_V1, legacy_open=M.LEGACY_RESERVE)['headroom'], M.FD_HEADROOM_MIN)
        self.assertEqual(M.steady_set(self.flow), ['TARGETS', 'ENTENDA_LOOKUP', 'REF_LOOKUP'])
        # the new flow alone would fit even the legacy default (5, 0 legacy handles), but with the legacy reserve it would not keep
        # the required headroom: that is why max_files 12 is kept on top of the shorter lifecycle
        self.assertTrue(M.replay(self.flow, M.SD_MAX_FILES_LEGACY)['ok'])
        self.assertLess(M.replay(self.flow, M.SD_MAX_FILES_LEGACY, legacy_open=M.LEGACY_RESERVE)['headroom'], M.FD_HEADROOM_MIN)

    def test_payloads_on_demand(self):
        f = self.flow
        q = f[f.index(('open', 'REF_LOOKUP')) + 1:]
        opens = [n for op, n in q if op == 'open']
        # ENTENDA payload: 7 targets with a lookup row + 2 BLOCK anchors; NONE / invalid targets never open it
        self.assertEqual(opens.count('ENTENDA_PAYLOAD'), 9)
        # REF payload: 5.V, 37.6, 114.VIII, 25 (count > 0) + single + multiple; zero-result (21.XXIV) never opens it
        self.assertEqual(opens.count('REF_PAYLOAD'), 6)
        self.assertEqual(len(self.dev.references('CF88:ART.21:INC.XXIV')), 0)
        for i, (op, n) in enumerate(q):
            if op == 'open' and n in ('ENTENDA_PAYLOAD', 'REF_PAYLOAD'):
                self.assertEqual(q[i + 1], ('close', n))                               # closed before anything else opens


class SourceLifecycleTest(unittest.TestCase):
    """Ties the model to the firmware source (regression guard for persistent/undeclared handles)."""

    def test_open_sequence_matches_model(self):
        body = diag_body()
        calls = re.findall(r'(?:\.abrir|\.preparar|lexV1Sha256Arquivo|lexV1OffsetEstrutural)\((?:"([A-Z0-9_]+)"|rtPath)', body)
        kinds = [c or 'CF88_RUNTIME' for c in calls]
        self.assertEqual(kinds, ['LEXV1_VER', 'CF88_RUNTIME', 'TEXT_MAP', 'CF88_RUNTIME', 'TEXT_MAP', 'TARGETS', 'ENTENDA_LOOKUP',
                                 'REF_LOOKUP', 'ENTENDA_PAYLOAD', 'REF_PAYLOAD'])
        dev = S.Device(SD)
        try:
            model = [n for op, n in M.new_flow(dev) if op == 'open']
        finally:
            dev.close()
        seen = []
        for n in model:
            if not seen or seen[-1] != n:
                seen.append(n)
        # static opens in source order == first part of the model; payload readers are lazy (preparar), never abrir
        self.assertEqual(seen[:8], kinds[:8])
        self.assertIn('pl.preparar("ENTENDA_PAYLOAD"', body)
        self.assertIn('rp.preparar("REF_PAYLOAD"', body)
        self.assertNotRegex(body, r'(pl|rp)\.abrir\(')

    def test_short_lived_handles(self):
        body = diag_body()
        ver = body[body.index('LexV1FileReader ver;'):]
        self.assertIn('ver.fechar();', ver[:ver.index('}')])                         # LEXV1.VER closed right after parse
        idx_open = body.index('tgt.abrir(')
        self.assertLess(body.index('lexV1Sha256Arquivo("CF88_RUNTIME"'), idx_open)  # runtime hashed before indices open
        self.assertLess(body.index('lexV1OffsetEstrutural('), idx_open)
        self.assertLess(body.index('map.fechar();'), idx_open)                       # TEXT_MAP closed before steady set
        # only one function-scope reader declaration survives across the queries: the steady trio + 2 lazy payloads
        self.assertEqual(re.findall(r'^\s*LexV1FileReader ([^;]+);', body, re.M), ['ver', 'map', 'tgt, lk, rl, pl, rp'])
        self.assertEqual(len(re.findall(r'\.abrir\("[A-Z_]+","[^"]+","steady"\)', body)), M.FD_STEADY_MAX)
        self.assertEqual(body.count('pl.fechar();'), 3)                               # after each query, after BLOCK, at the end
        self.assertIn('pl.fechar(); rp.fechar(); tgt.fechar(); lk.fechar(); rl.fechar();', body)
        sha = INO[INO.index('uint32_t &bytes, char hex[65])\n{'):]
        self.assertIn('r.fechar();', sha[:sha.index('\n}\n')])
        pos = INO[INO.index('static bool lexV1OffsetEstrutural('):]
        self.assertIn('r.fechar();', pos[:pos.index('\n}\n')])

    def test_tracker_and_fail_io(self):
        v1 = device_v1_ino_sections()
        self.assertIn('Serial.printf("LEXV1: FAIL_IO|%s|%s|stage=%s|open=%d|max_open=%d\\n",t,c,e,lexV1FdOpen,lexV1FdMax);', v1)
        self.assertIn('LEXV1: OPEN %s %s stage=%s OPEN_COUNT=%d MAX_OPEN_COUNT=%d', v1)
        self.assertIn('LEXV1: CLOSE %s OPEN_COUNT=%d', v1)
        # every SD.open of DEVICE V1 goes through the tracker (LexV1FileReader::abrir); no probe / bulk opens
        opens = [l.strip() for l in v1.split('\n') if 'SD.open(' in l]
        self.assertEqual(opens, ['f=SD.open(c,FILE_READ);'])
        # every abrir(...) passes type, path and stage
        for m in re.findall(r'\.abrir\(([^)]*)\)', diag_body()):
            self.assertEqual(len(m.split(',')), 3, m)
        for cat in ('FAIL_SCHEMA', 'FAIL_HASH', 'FAIL_IO', 'FAIL_PARSE', 'FAIL_TARGET', 'FAIL_REFERENCE'):
            self.assertIn(f'"{cat}"', v1)
        for name in ('fd_steady_state', 'fd_pico_e_fechamento'):
            self.assertIn(f'"{name}"', v1)

    def test_previous_diagnostics_preserved(self):
        v1 = device_v1_ino_sections()
        for name in ('schema_2_rejeitado', 'schema_3_aceito', 'schema_4_rejeitado', 'schema_30_e_3X_rejeitados', 'lexv1_ver_device_version',
                     'RUNTIME_HASH_MATCH', 'pinned_runtime_vs_ver', 'text_map_sha256_pinned', 'text_map_idx', 'text_map_runtime_guard',
                     'text_map_guard_sha_errado', 'text_to_target_114_VIII', 'text_to_target_inicio_adct', 'targets_idx',
                     'block_sem_payload_duplicado', 'references_zero_result', 'references_single_result', 'references_multiple_result'):
            self.assertIn(f'"{name}"', v1)
        self.assertIn('lexV1Mem("antes_device_v1")', v1)
        self.assertIn('lexV1Mem("depois_device_v1")', v1)

    def test_read_only(self):
        code = device_v1_ino_sections() + '\n' + HDR
        for pat in (r'FILE_WRITE', r'FILE_APPEND', r'SD\.(mkdir|remove|rename|rmdir|format)', r'\.write\(', r'\bfopen\b', r'\bappend\b'):
            self.assertFalse([l for l in code.split('\n') if re.search(pat, l) and 'Serial.' not in l], pat)
        # only Serial and the TFT display are printed to; never a File
        self.assertFalse([l for l in code.split('\n') if re.search(r'(?<!Serial)(?<!tft)\.print\w*\(', l)])


if __name__ == '__main__':
    unittest.main()
