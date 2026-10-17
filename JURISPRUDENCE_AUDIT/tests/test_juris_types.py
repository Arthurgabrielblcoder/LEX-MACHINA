"""PÓS-NOTURNA E/F — extensible jurisprudence types: labels, tribunal/classe separation, legacy compatibility, ficha names, firmware parity."""
import glob
import json
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
sys.path.insert(0, str(AUD))
import juris_types as JT  # noqa: E402

LEGACY_IDX = AUD / 'J2B_1_CANDIDATE_HOST_ONLY/candidate/SD/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX'
OLD_FIRMWARE = {'repercussao_geral': 'RG TEMA {n}', 'sumula_vinculante': 'SV {n}', 'adi': 'ADI {n}'}   # labels of the approved app


class JurisTypes(unittest.TestCase):
    def test_required_labels(self):
        cases = [(('hc', 'STF', '232627'), 'HC 232627'), (('ms', 'STF', '27931'), 'MS 27931'), (('ap', 'STF', '694'), 'AP 694'),
                 (('ai', 'STF', '343461'), 'AI 343461'), (('inq', 'STF', '4781'), 'Inq 4781'), (('rcl', 'STF', '84738'), 'Rcl 84738'),
                 (('adpf', 'STF', '378'), 'ADPF 378'), (('mi', 'STF', '7300'), 'MI 7300'), (('sumula', 'TSE', '9'), 'Súmula 9 TSE'),
                 (('sumula', 'STJ', '403'), 'Súmula 403 STJ')]
        for args, want in cases:
            self.assertEqual(JT.label(*args), want)
        self.assertEqual(JT.title('sumula', 'TSE', '9'), 'Súmula 9 TSE')
        self.assertEqual(JT.title('hc', 'STF', '232627'), 'STF HC 232627')

    def test_never_outro_and_never_stf_for_other_courts(self):
        with self.assertRaises(ValueError):
            JT.label('desconhecido', 'STF', '1')
        for trib in ('TSE', 'STJ'):
            self.assertNotIn('STF', JT.label('sumula', trib, '1'))

    def test_ficha_convention(self):
        self.assertEqual(JT.ficha(JT.identificador('STF', 'HC', '232627')), 'STF_HC_232627.TXT')
        self.assertEqual(JT.ficha(JT.identificador('TSE', 'SUMULA', '9')), 'TSE_SUMULA_9.TXT')
        self.assertEqual(JT.ficha(JT.identificador('STJ', 'SUMULA', '403')), 'STJ_SUMULA_403.TXT')
        self.assertEqual(JT.ficha('STF:ADI:7047-7064'), 'STF_ADI_7047-7064.TXT')

    def test_id_acceptance(self):
        self.assertTrue(JT.id_accepted('TSE:SUMULA:9:CF88:15:-:III:-', 'TSE'))
        self.assertFalse(JT.id_accepted('TSE:SUMULA:9:CF88:15:-:III:-', 'STF'))      # tribunal column must match the id
        self.assertFalse(JT.id_accepted('XYZ:HC:1:CF88:1:-:-:-', 'XYZ'))

    def test_legacy_ids_and_labels_unchanged(self):
        rows = [l.split('|') for l in LEGACY_IDX.read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
        self.assertTrue(rows)
        for r in rows:
            self.assertTrue(JT.id_accepted(r[0], r[2]), r[0])                         # LEGACY_IDS_SUPPORTED
            self.assertEqual(JT.label(r[1], r[2], r[3]), OLD_FIRMWARE[r[1]].format(n=r[3]))
            self.assertEqual(JT.ficha(r[6]), r[6].replace(':', '_').replace('/', '_') + '.TXT')   # LEGACY_FICHAS_SUPPORTED

    def test_every_batch_precedent_has_a_label_that_fits(self):
        for f in sorted(glob.glob(str(AUD / 'J2_*_BACKLOG/J2*_DECISIONS.json'))):
            for x in json.loads(Path(f).read_text(encoding='utf-8'))['decisions']:
                for p in x.get('precedents', []):
                    tipo, trib, num, ident, lb = JT.from_precedent(p)
                    self.assertNotIn('OUTRO', lb)
                    self.assertLessEqual(len(f'32 {lb}'), JT.LIST_WIDTH, lb)
                    self.assertTrue(JT.id_accepted(ident, trib))

    def test_firmware_patch_tables_equal_host(self):
        patch = (AUD / 'JURIS_TYPE_PROTOTYPE/juris_types.patch').read_text(encoding='utf-8')
        added = '\n'.join(l[1:] for l in patch.splitlines() if l.startswith('+') and not l.startswith('+++'))
        self.assertEqual(JT.parse_firmware_tables(added), (JT.CLASSES, JT.TRIBUNAIS))
        self.assertIn('if(rotuloClasseJuris(tipo)) return JTIPO_CLASSE;', added)
        self.assertIn('tribunalJurisSuportado(classe,tribunal)', added)
        self.assertNotIn('"STF:"', added)

    def test_build_report(self):
        r = json.loads((AUD / 'JURIS_TYPE_PROTOTYPE/JURIS_TYPE_PROTOTYPE_BUILD.json').read_text(encoding='utf-8'))
        self.assertEqual((r['flashed'], r['firmware_dir_modified'], r['physical_approval']), (False, False, False))
        self.assertTrue(r['base']['vs_approved_metadata_only'] and r['patch']['firmware_tables_equal_host'] and r['patch']['other_files_identical'])
        self.assertEqual(r['delta_vs_base']['static_ram_bytes'], 0)
        self.assertGreater(r['types_build']['app_partition_free'], 100000)


if __name__ == '__main__':
    unittest.main()
