"""DEVICE INTEGRATION V1-A2B: official ADCT ingestion, CF88_RUNTIME, runtime target index, TEXT_MAP binding, SD backup."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(ROOT / 'updater'))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_target_index as BTI  # noqa: E402
import exportar_cf88_runtime as XR  # noqa: E402
import runtime_targets as RT  # noqa: E402
import device_lookup_simulator as S  # noqa: E402

SRC = ROOT / 'updater/fontes_oficiais_senado'
SD = DI / 'staging_sd_v1/SD/99_LEX_V1'
HOST = DI / 'staging_sd_v1/_host'


def _sha(b):
    return hashlib.sha256(b).hexdigest()


@unittest.skipUnless((SRC / 'SOURCES_LOCK.json').is_file(), 'official sources not ingested')
class OfficialSourcesTest(unittest.TestCase):
    def test_lock_raw_and_metadata(self):
        lock = json.loads((SRC / 'SOURCES_LOCK.json').read_text(encoding='utf-8'))
        self.assertEqual(sorted(lock['sources']), ['ADCT', 'CF88'])
        for ident, norma in (('CF88', '579494'), ('ADCT', '604119')):
            s = lock['sources'][ident]
            d = SRC / s['dir']
            meta = json.loads((d / 'metadata.json').read_text(encoding='utf-8'))
            self.assertEqual((meta['norma_id_senado'], s['norma_id_senado']), (norma, norma))
            self.assertEqual(meta['tipo_compilacao'], 'COMPILACAO_MONOVIGENTE')
            self.assertTrue(meta['publicacao_url'].startswith(f'https://legis.senado.leg.br/norma/{norma}/publicacao/'))
            self.assertEqual(_sha((d / 'raw.html').read_bytes()), s['raw_sha256'])
            self.assertEqual(_sha((d / 'raw.html').read_bytes()), meta['raw_sha256'])
            self.assertEqual(_sha((d / 'normalizado.txt').read_bytes()), meta['normalizado_sha256'])
            self.assertTrue(meta['validacao']['aprovada'])
            for k in ('adquirido_em_utc', 'parser', 'ingestor_version', 'url_final'):
                self.assertIn(k, meta)

    def test_adct_registered_in_official_pipeline(self):
        import main as M
        cfg = M.FONTES_ESPECIAIS_MESTRE['ADCT']
        self.assertEqual(cfg['norma_url'], 'https://legis.senado.leg.br/norma/604119')
        self.assertEqual(M.FONTES_ESPECIAIS_MESTRE['CF88']['norma_url'], 'https://legis.senado.leg.br/norma/579494')
        lock = json.loads((SRC / 'SOURCES_LOCK.json').read_text(encoding='utf-8'))
        text = (SRC / lock['sources']['ADCT']['dir'] / 'normalizado.txt').read_text(encoding='utf-8')
        self.assertEqual(M._validar_especial_mestre('ADCT', text), [])


class HeaderNormalizationTest(unittest.TestCase):
    def test_case_a_joins_only_label(self):
        out, st = XR.normalize_headers('Art.\n37. A administração\ntexto')
        self.assertEqual(out, 'Art. 37. A administração\ntexto')
        self.assertEqual(st['joined_headers'], 1)
        out, _ = XR.normalize_headers('Art.\n5º Todos são iguais')
        self.assertEqual(out, 'Art. 5º Todos são iguais')
        out, _ = XR.normalize_headers('Art.\n29-A. O total')
        self.assertEqual(out, 'Art. 29-A. O total')

    def test_case_a_refuses_unsafe_join(self):
        for bad in ('Art.\nda Lei nº 1', 'Art.\n', 'Art.\nA administração'):
            with self.assertRaises(XR.ExportError):
                XR.normalize_headers(bad)

    def test_case_b_exact_concatenation(self):
        out, st = XR.normalize_headers('Art\n. 101. Os Estados')
        self.assertEqual(out, 'Art. 101. Os Estados')
        self.assertEqual(st['joined_headers_case_b'], 1)
        with self.assertRaises(XR.ExportError):
            XR.normalize_headers('Art\nigo qualquer')

    def test_lowercase_citations_untouched(self):
        src = 'a que se refere o\nart. 2º da Lei nº 12.858\n.'
        out, st = XR.normalize_headers(src)
        self.assertEqual((out, st['joined_headers'], st['joined_headers_case_b']), (src, 0, 0))

    def test_case_c_glued_paragraph_only_inserts_newline(self):
        src = 'cinco décimos).§ 4º O financiamento do seguro'
        out, st = XR.normalize_headers(src)
        self.assertEqual(out, 'cinco décimos).\n§ 4º O financiamento do seguro')
        self.assertEqual(out.replace('\n', ''), src)
        self.assertEqual(st['split_glued_paragraphs_case_c'], 1)
        for keep in ('conforme o § 4º do art. 5', 'previsto no § 3º.', 'arts. 5º e 6º.§'):
            self.assertEqual(XR.normalize_headers(keep)[0], keep)


@unittest.skipUnless((SD / '05_TEXT/CF88_RUNTIME.txt').is_file(), 'staging not built')
class RuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = (SD / '05_TEXT/CF88_RUNTIME.txt').read_bytes()
        cls.prov = json.loads((HOST / 'CF88_RUNTIME.provenance.json').read_text(encoding='utf-8'))
        cls.idx = json.loads((HOST / 'CF88_RUNTIME_TARGET_INDEX.json').read_text(encoding='utf-8'))
        cls.manifest = json.loads((SD / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))

    def test_runtime_deterministic_and_identical_to_export(self):
        a, pa = XR.build_runtime()
        b, pb = XR.build_runtime()
        self.assertEqual((a, pa), (b, pb))
        self.assertEqual(a, self.data)
        exported = DI / 'runtime/CF88_RUNTIME.txt'
        if exported.is_file():
            self.assertEqual(exported.read_bytes(), self.data)
        self.assertEqual(self.prov['sha256'], _sha(self.data))

    def test_runtime_encoding_content(self):
        text = self.data.decode('utf-8')
        self.assertFalse(self.data.startswith(b'\xef\xbb\xbf'))
        self.assertNotIn(b'\r', self.data)
        self.assertTrue(text.endswith('\n'))
        lines = text.split('\n')
        self.assertTrue(lines[0].startswith(XR.CF_TITLE))
        self.assertEqual(lines.count(XR.ADCT_MARKER), 1)
        self.assertEqual(self.data.index(XR.ADCT_MARKER.encode('utf-8')), self.prov['adct_offset'])
        for m in XR.HISTORICAL_MARKERS:
            self.assertNotIn(m, text)
        self.assertFalse([l for l in lines if l in ('Art.', 'Art')])
        self.assertFalse(self.prov['manual_edits'])
        self.assertIn('Art. 250.', text)            # CF complete
        self.assertIn('\nArt. 138.', text)          # ADCT complete
        for k in ('LEX MACHINA', 'PASTA_DESTINO', 'ATUALIZADO_EM'):
            self.assertNotIn(k, text)               # no pipeline header / timestamps inside the runtime bytes

    def test_target_index_built_from_runtime_bytes(self):
        self.assertEqual((self.idx['source']['sha256'], self.idx['source']['bytes']), (_sha(self.data), len(self.data)))
        rebuilt = RT.build_runtime_index(SD / '05_TEXT/CF88_RUNTIME.txt')
        self.assertEqual(rebuilt['target_index_sha256'], self.idx['target_index_sha256'])
        self.assertEqual(self.manifest['target_id_version']['target_index_sha256'], self.idx['target_index_sha256'])
        self.assertEqual(self.idx['target_id_duplicates'], 0)
        self.assertEqual([a for a in self.idx['anomalies'] if a['code'] != 'CLOSING_MARKER'], [])

    def test_text_map_bound_to_runtime(self):
        dev = S.Device(SD)
        try:
            h = dev.text_map.header
            self.assertEqual((h['SOURCE_SHA256'][0], int(h['SOURCE_BYTES'][0])), (_sha(self.data), len(self.data)))
            self.assertEqual(h['TARGET_ID_VERSION'][0], self.idx['target_index_sha256'])
            self.assertEqual(int(h['NAMESPACE_START_ADCT'][0]), self.prov['adct_offset'])
            self.assertEqual(h['NORMALIZATION_VERSION'][0], self.prov['normalization_version'])
            # every canonical line of every target resolves back to a target starting on that line
            starts = {}
            pos = 0
            for n, line in enumerate(self.data.split(b'\n')[:-1], start=1):
                starts[n] = pos
                pos += len(line) + 1
            by_tid = {t['target_id']: t for t in self.idx['targets']}
            for tid in ('CF88:ART.5', 'CF88:ART.5:INC.V', 'CF88:ART.7:INC.XII', 'CF88:ART.8:INC.I', 'CF88:ART.20:INC.XI',
                        'CF88:ART.21:INC.XXIV', 'CF88:ART.22:INC.XXIX', 'CF88:ART.24:PAR.4', 'CF88:ART.37:PAR.6',
                        'CF88:ART.60:PAR.4:INC.IV', 'CF88:ART.150', 'CF88:ART.225', 'ADCT:ART.10', 'ADCT:ART.10:INC.II',
                        'CF88:ART.239:PAR.4'):
                off = starts[by_tid[tid]['line_start']]
                r = dev.resolve_text_position(off + 3, len(self.data), _sha(self.data))
                self.assertEqual((r['status'], r['target_id']), ('OK', tid), tid)
            adct = dev.resolve_text_position(self.prov['adct_offset'], len(self.data), _sha(self.data))
            self.assertEqual(adct['target_id'], 'ADCT')
        finally:
            dev.close()

    def test_adct_targets_and_pilot(self):
        ids = {t['target_id'] for t in self.idx['targets']}
        for tid in ('ADCT', 'ADCT:ART.1', 'ADCT:ART.10', 'ADCT:ART.10:INC.I', 'ADCT:ART.10:INC.II', 'ADCT:ART.10:PAR.1',
                    'ADCT:ART.18-A', 'ADCT:ART.76-B', 'ADCT:ART.101', 'ADCT:ART.138'):
            self.assertIn(tid, ids)
        self.assertNotIn('ADCT:ART.156-A', ids)          # CF article cited inside the ADCT is not an ADCT target
        dev = S.Device(SD)
        try:
            r = dev.query('ADCT.10.II')
            self.assertEqual((r['resolution_type'], r['anchor_target_id'], r['legal_status']), ('DIRECT', 'ADCT:ART.10:INC.II', 'CURRENT'))
        finally:
            dev.close()

    def test_layers_resolve_and_diff_not_blocking(self):
        v = self.manifest['layer_validation']
        self.assertEqual((v['entenda_direct'], v['entenda_resolved'], v['entenda_lookup_rows']), (163, 283, 283))
        self.assertEqual((v['reference_targets'], v['reference_rows']), (242, 432))
        rows = [l.split('|') for l in (SD / '20_REFERENCES/REF_PAYLOAD.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
        for t in v['reference_targets_absent_historical_hidden']:
            self.assertTrue(all(r[2] == 'HISTORICAL_HIDDEN_BY_DEFAULT' for r in rows if r[0] == t), t)
        diff = json.loads((HOST / 'TARGET_DIFF_LEGACY_VS_RUNTIME.json').read_text(encoding='utf-8'))
        self.assertFalse([r for r in diff['rows'] if r['classification'] in RT.BLOCKING])
        self.assertFalse([r for r in diff['rows'] if r['change'] == 'REMOVED' and r['legacy_status'] == 'CURRENT'
                          and r['target_id'] not in RT.load_reviewed()])

    def test_legacy_index_unchanged_by_parser_option(self):
        legacy = json.loads(RT.LEGACY_INDEX.read_text(encoding='utf-8'))
        rebuilt = BTI.build('CF88', ROOT / legacy['source']['path'], RT.END_MARKERS)
        self.assertEqual(rebuilt['target_index_sha256'], legacy['target_index_sha256'])
        self.assertEqual(subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', 'LEGAL_TARGET_ID/derived'], cwd=ROOT).returncode, 0)


def _latest_sd_backup():
    b = sorted((DI / 'backups').glob('sd_*/manifest.json'))
    return b[-1].parent if b else None


@unittest.skipUnless(_latest_sd_backup(), 'no SD backup')
class SdBackupTest(unittest.TestCase):
    def test_manifest_and_verification(self):
        d = _latest_sd_backup()
        m = json.loads((d / 'manifest.json').read_text(encoding='utf-8'))
        agg = _sha(''.join(f"{f['relative_path']}\t{f['size']}\t{f['sha256']}\n" for f in m['files']).encode('utf-8'))
        self.assertEqual(agg, m['aggregate_manifest_sha256'])
        self.assertEqual((m['total_files'], m['total_bytes']), (len(m['files']), sum(f['size'] for f in m['files'])))
        self.assertEqual(m['errors'], [])
        self.assertEqual(json.loads((d / 'VERIFICATION.json').read_text(encoding='utf-8'))['result'], 'BACKUP_VERIFIED')
        cf = next(f for f in m['files'] if f['relative_path'] == '1- CONSTITUIÇÃO FEDERAL/cf.txt')
        self.assertEqual((cf['size'], cf['sha256']), (429242, 'd8469e18e45e027872f04bc56ba1076bcc6d1bb3295c71173bd5b728b22dca6e'))
        # physical CF = official monovigente CF body (same bytes as the locked normalized source + final LF)
        lock = json.loads((SRC / 'SOURCES_LOCK.json').read_text(encoding='utf-8'))
        norm = (SRC / lock['sources']['CF88']['dir'] / 'normalizado.txt').read_bytes()
        self.assertEqual((d / 'data/1- CONSTITUIÇÃO FEDERAL/cf.txt').read_bytes(), norm + b'\n')

    def test_sample_files_match_manifest(self):
        d = _latest_sd_backup()
        m = json.loads((d / 'manifest.json').read_text(encoding='utf-8'))
        for f in m['files'][::97]:
            self.assertEqual(_sha((d / 'data' / f['relative_path']).read_bytes()), f['sha256'], f['relative_path'])


class FirmwareCandidateTest(unittest.TestCase):
    def test_original_release_untouched_and_candidate_isolated(self):
        base = ROOT / 'firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA'
        self.assertEqual(_sha((base / 'LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA.ino').read_bytes()),
                         'fd0227e6cc6ee0e00c569b76adfaa918261d28dd557a9d5b4d9cafd9667206dc')
        self.assertEqual(subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', 'firmware/LEX_MACHINA_v7.12.0_JURIS_CF_EXPANDIDA'], cwd=ROOT).returncode, 0)
        cand = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
        ino = (cand / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
        self.assertIn('#define LEX_DEVICE_V1_ENABLED 0', ino)
        hdr = (cand / 'lex_device_v1.h').read_text(encoding='utf-8')
        for token in ('CF88_RUNTIME.txt', 'LEXV1_FAIL_SOURCE_MISMATCH', 'RUNTIME'):
            self.assertIn(token, hdr + ino)


if __name__ == '__main__':
    unittest.main()
