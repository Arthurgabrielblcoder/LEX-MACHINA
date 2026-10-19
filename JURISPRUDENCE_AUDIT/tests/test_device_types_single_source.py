"""Device-type status: juris_types is the single source for Batch11+; Batches 03–10 keep the frozen table so their pinned files stay identical."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
sys.path.insert(0, str(AUD))
import build_j2_batch as G  # noqa: E402
import j2_review_common as RC  # noqa: E402
import juris_types as JT  # noqa: E402


class DeviceTypes(unittest.TestCase):
    def test_single_source_for_future_batches(self):
        doc11 = dict(batch='BATCH11')
        for k in ('RG', 'SV', 'ADI', 'HC', 'MS', 'AP', 'AI', 'INQ', 'RCL', 'ADPF', 'SUMULA', 'SUMULA_TSE', 'SUMULA_STJ', 'REPETITIVO', 'IAC'):
            self.assertEqual(RC.device_status(doc11, k), 'VALIDATED', k)              # J2I 32/32; SUMULA_STJ CC-J1 36/36; REPETITIVO/IAC CC-J2 38/38
        for k in ('ADC', 'RE', 'ARE', 'MI', 'RHC'):
            self.assertEqual(RC.device_status(doc11, k), 'FIRMWARE_LABEL_EXISTS_NOT_PHYSICALLY_VALIDATED', k)
        self.assertEqual(RC.device_status(doc11, 'XYZ'), 'NEW_JURIS_TYPE_REQUIRES_DESIGN')
        self.assertTrue(all(RC.device_status(doc11, k) == JT.physical_status(k) for k in JT.KLASS_TO_TIPO))

    def test_historical_batches_unchanged(self):
        self.assertEqual(JT.device_status('SUMULA_STJ'), 'FIRMWARE_LABEL_EXISTS_NOT_PHYSICALLY_VALIDATED')   # frozen-batch table unchanged
        self.assertEqual(RC.device_status(dict(batch='BATCH10'), 'ADPF'), 'FIRMWARE_LABEL_EXISTS_NOT_PHYSICALLY_VALIDATED')   # frozen table
        rec = json.loads((AUD / 'J2_RATIFICATION_RECORD_03_09.json').read_text(encoding='utf-8'))
        rec10 = json.loads((AUD / 'J2_RATIFICATION_RECORD_10.json').read_text(encoding='utf-8'))
        pins = dict(rec['decision_files_sha256_lf'], **rec10['decision_files_sha256_lf'])
        self.assertEqual(len(pins), 7)
        for rel, h in pins.items():
            self.assertEqual(G.B.sha_lf(AUD / rel), h, rel)                           # HISTORICAL_BATCH_HASHES_UNCHANGED
        for script in ('build_j2_ratification_record.py', 'build_j2_ratification_record_10.py'):
            r = subprocess.run([sys.executable, '-I', '-B', str(AUD / script), '--check'], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), script)


if __name__ == '__main__':
    unittest.main()
