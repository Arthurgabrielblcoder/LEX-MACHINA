"""Súmulas 203/403 STJ — editorial closure: history kept, CF links HUMAN_APPROVED, CC links forwarded to CC-J1, decision files untouched."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parent
sys.path.insert(0, str(AUD))
import build_j2_batch as G  # noqa: E402


class STJResolution(unittest.TestCase):
    def test_record(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(AUD / 'build_j2_stj_resolution_record.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))
        d = json.loads((AUD / 'J2_STJ_RESOLUTION_RECORD.json').read_text(encoding='utf-8'))
        it = {i['precedent']: i for i in d['items']}
        self.assertEqual(it['STJ:SUMULA:203']['ratified_cf_targets'], ['CF88:ART.105:INC.III'])
        self.assertEqual(it['STJ:SUMULA:403']['ratified_cf_targets'], ['CF88:ART.5:INC.V', 'CF88:ART.5:INC.X'])
        self.assertEqual(it['STJ:SUMULA:403']['cc_targets_forwarded_to_cc_j1'], ['CC2002:ART.186', 'CC2002:ART.927'])
        for i in d['items']:
            self.assertEqual([h['state'].split(' ')[0] for h in i['history']], ['UNRESOLVED_EXTERNAL', 'OFFICIAL_SOURCE_RESOLVED', 'HUMAN_APPROVED'])
        self.assertIn('HISTÓRICO DO ENUNCIADO', it['STJ:SUMULA:203']['ficha_draft'])
        self.assertEqual((d['NEW_CF_RELATIONS'], d['NEW_CF_TARGETS'], d['materialized']), (3, 1, False))
        for rel, h in d['decision_files_unchanged'].items():
            self.assertEqual(G.B.sha_lf(AUD / rel), h)
        s = json.loads((AUD / 'J2_BACKLOG_STATE.json').read_text(encoding='utf-8'))
        self.assertEqual((s['UNRESOLVED_EXTERNAL'], sorted(s['RESOLVED_AFTER_REVIEW'])), (0, ['J0-BL-001', 'J0-BL-093']))


if __name__ == '__main__':
    unittest.main()
