"""FASE C — HC type: design evidence, prototype build record, patch shape, simulation regressions. Never flashes; firmware/ untouched."""
import json
import subprocess
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
import sys  # noqa: E402
sys.path.insert(0, str(AUD / 'FIRMWARE_REPRODUCIBILITY'))
import firmware_baseline as FB  # noqa: E402  (Parte D: only the sha-pinned 124-ficha header may differ)
HC = AUD / 'HC_FIRMWARE_PROTOTYPE'


class HCPrototype(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads((HC / 'HC_PROTOTYPE_BUILD.json').read_text(encoding='utf-8'))
        cls.v = json.loads((AUD / 'J2_HIGH_BACKLOG/J2E_ISOLATION_AUDIT.json').read_text(encoding='utf-8'))['variants']

    def test_not_flashed_and_firmware_dir_untouched(self):
        self.assertEqual((self.r['flashed'], self.r['firmware_dir_modified'], self.r['physical_approval']), (False, False, False))
        self.assertEqual(FB.firmware_changes('e9c7d53'), [])

    def test_baseline_reproduced_with_124_header(self):
        rp = self.r['reproducibility']
        self.assertEqual(rp['header']['fichas'], 124)
        self.assertTrue(rp['approved_bin_sha_matches'] and rp['base_vs_approved_metadata_only'])
        self.assertEqual(rp['base_rebuild']['program_bytes'], 1100991)

    def test_patch_shape(self):
        p = (HC / 'hc_type.patch').read_text(encoding='utf-8')
        added = [l for l in p.splitlines() if l.startswith('+') and not l.startswith('+++')]
        removed = [l for l in p.splitlines() if l.startswith('-') and not l.startswith('---')]
        self.assertEqual(len(removed), 2)
        self.assertIn('+  JTIPO_ACORDAO, JTIPO_HC, JTIPO_OUTRO', added)
        self.assertIn('+    case JTIPO_HC: return "HC "+r.numero;', added)
        self.assertIn('+  if(tipo=="hc" || tipo=="habeas_corpus") return JTIPO_HC;', added)
        self.assertTrue(self.r['hc_patch']['other_files_identical'])

    def test_size_budget(self):
        b = self.r['hc_build']
        self.assertEqual(self.r['delta_vs_base']['static_ram_bytes'], 0)
        self.assertLess(self.r['delta_vs_base']['program_bytes'], 1024)
        self.assertGreater(b['app_partition_free'], 100000)

    def test_simulation_labels(self):
        b = self.v['B']
        self.assertEqual(b['verdict']['HC_LABEL_HC_FIRMWARE'], ['HC 232627'])
        self.assertEqual(b['verdict']['HC_LABEL_CURRENT_FIRMWARE'], ['OUTRO 232627'])
        cur, hc = b['device_simulation']['CURRENT'], b['device_simulation']['HC_CANDIDATE']
        for t in cur:                                     # RG / SV / ADI / joint labels identical under the HC firmware
            if t != 'CF88:ART.53:PAR.1':
                self.assertEqual(cur[t], hc[t], t)
        self.assertIn('/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_HC_232627.TXT', b['verdict']['NEW_FICHAS'])
        self.assertNotIn('/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_HC_232627.TXT', self.v['A']['verdict']['NEW_FICHAS'])


if __name__ == '__main__':
    unittest.main()
