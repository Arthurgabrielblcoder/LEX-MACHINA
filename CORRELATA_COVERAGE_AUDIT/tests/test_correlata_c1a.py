"""CF88_CORRELATA_C1A: the 19 current-link decisions are complete, well-founded, deterministic and NOT applied."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
ROOT = AUDIT.parent
sys.path.insert(0, str(AUDIT / 'tools'))
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_c1a_review as C  # noqa: E402
import target_id as T  # noqa: E402

J, M = C.build()
DOC = json.loads(J)
OPERATIONAL = ('LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json', 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json',
               'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json', 'LEGAL_TARGET_ID/derived/export_test/run3/REF_LOOKUP.IDX',
               'LEGAL_TARGET_ID/derived/export_test/run3/REF_PAYLOAD.IDX', 'LEGAL_TARGET_ID/derived/export_test/run3/CF88_REFERENCES_EXPORT.json')


class C1ADecisions(unittest.TestCase):
    def test_deterministic_and_committed(self):
        self.assertEqual(C.build(), (J, M))
        self.assertEqual(C.OUT_JSON.read_bytes().replace(b'\r\n', b'\n'), J)
        self.assertEqual(C.OUT_MD.read_bytes().replace(b'\r\n', b'\n'), M)

    def test_19_of_19_unique_and_inside_the_c0_set(self):
        q = json.loads(C.QUEUE.read_text(encoding='utf-8'))
        c0 = {x['reference_id'] for x in q['CURRENT_LINK_REVIEW'] if x['plausibility'] == 'NEEDS_REVIEW'}
        ids = [d['reference_id'] for d in DOC['decisions']]
        self.assertEqual(len(ids), 19)
        self.assertEqual(len(set(ids)), 19)
        self.assertEqual(set(ids), c0)
        self.assertEqual([s['reference_id'] for s in DOC['snapshot_before_review']], ids)
        self.assertEqual(sum(DOC['counts'].values()), 19)

    def test_every_decision_is_founded_and_sourced(self):
        for d in DOC['decisions']:
            self.assertIn(d['decision'], C.DECISIONS)
            self.assertFalse(d['applied'])
            self.assertTrue(d['official_sources'], d['reference_id'])
            for s in d['official_sources']:
                self.assertRegex(s['url'], r'^https://www\.planalto\.gov\.br/ccivil_03/')
                self.assertRegex(s['sha256'], r'^[0-9a-f]{64}$')
                self.assertEqual(s['verified_on'], C.VERIFIED_ON)
            if d['decision'] != 'HOLD':
                self.assertGreater(len(d['legal_analysis']), 80, d['reference_id'])
                self.assertGreater(len(d['destination_provisions']), 40, d['reference_id'])

    def test_retarget_replace_route_fix_are_explicit(self):
        for d in DOC['decisions']:
            if d['decision'] == 'RETARGET':
                ok, _ = T.validate_target_id(d['retarget_to'])
                self.assertTrue(ok and d['retarget_to'] != d['current_target'], d['reference_id'])
            if d['decision'] == 'REPLACE':
                self.assertTrue(d['replacement_norms'], d['reference_id'])
                for n in d['replacement_norms']:
                    self.assertRegex(n['norm_key'], r'^(LEI|LC):\d+/\d{4}$')
                    self.assertTrue(n['route'] and n['relation_type'])
                    self.assertNotEqual(n['norm_key'], d['current_norm_id'])
            if d['decision'] == 'KEEP_WITH_ROUTE_FIX':
                self.assertTrue(d['route_fix'], d['reference_id'])

    def test_no_sibling_fan_out_kept(self):
        """A destination that literally cites only a sibling device is never KEEP for this target."""
        for d in DOC['decisions']:
            if d['c0_evidence']['destination_text_citation'] == 'DESTINO_CITA_SO_DISPOSITIVO_IRMAO':
                self.assertNotIn(d['decision'], ('KEEP', 'KEEP_WITH_ROUTE_FIX'), d['reference_id'])

    def test_simulation_is_consistent_and_not_applied(self):
        s = DOC['simulation']
        c = DOC['counts']
        self.assertEqual((s['visible_links_now'], s['visible_targets_now']), (44, 39))
        self.assertEqual(s['visible_links_after_without_replacements'], 44 - c['REMOVE'] - c['REPLACE'])
        self.assertEqual(s['visible_links_after_with_replacements'], s['visible_links_after_without_replacements'] + s['replacement_links_if_approved_and_ingested'])
        self.assertFalse(DOC['applied'])

    def test_operational_files_unchanged(self):
        for p in OPERATIONAL:
            blob = subprocess.run(['git', 'show', f"{C.BASE['head']}:{p}"], cwd=ROOT, capture_output=True, check=True).stdout
            self.assertEqual((ROOT / p).read_bytes().replace(b'\r\n', b'\n'), blob.replace(b'\r\n', b'\n'), p)

    def test_report_counts(self):
        md = M.decode('utf-8')
        for k, v in DOC['counts'].items():
            self.assertRegex(md, rf'\| {k} \| {v} \|')
        self.assertEqual(len(re.findall(r'^### \d+\. ', md, re.M)), 19)


if __name__ == '__main__':
    unittest.main()
