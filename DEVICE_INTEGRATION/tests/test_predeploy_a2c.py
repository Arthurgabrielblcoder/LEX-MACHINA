"""DEVICE INTEGRATION V1-A2C: auditable source correction (art. 114, VIII), reviewed diff exceptions, historical reference filter."""
import copy
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(ROOT / 'updater'))
import exportar_cf88_runtime as XR  # noqa: E402
import device_lookup_simulator as S  # noqa: E402
import runtime_targets as RT  # noqa: E402

SRC = ROOT / 'updater/fontes_oficiais_senado'
SD = DI / 'staging_sd_v1/SD/99_LEX_V1'
HOST = DI / 'staging_sd_v1/_host'
CID = 'SRC-CORR-CF88-579494-16434817-ART114-INC-VIII'


def _plain(html):
    t = re.sub(r'<[^>]+>', ' ', html)
    t = t.replace('&nbsp;', ' ')
    t = re.sub(r'\s+', ' ', t)
    return re.sub(r'\s+([,;.])', r'\1', t)


class SourceCorrectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = json.loads((SRC / 'SOURCES_LOCK.json').read_text(encoding='utf-8'))
        cls.corr = json.loads((SRC / 'SOURCE_TEXT_CORRECTIONS.json').read_text(encoding='utf-8'))
        cls.c = next(c for c in cls.corr['corrections'] if c['correction_id'] == CID)
        cls.cf_dir = SRC / cls.lock['sources']['CF88']['dir']

    def test_raw_preserved_and_contains_anomaly(self):
        raw = (self.cf_dir / 'raw.html').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.c['raw_source_sha256'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.lock['sources']['CF88']['raw_sha256'])
        self.assertIn('VII I - a execução, de ofício'.encode('utf-8'), raw)            # anomaly in the untouched official response
        norm = (self.cf_dir / 'normalizado.txt').read_text(encoding='utf-8').split('\n')
        self.assertEqual(norm.count(self.c['exact_raw_text']), 1)

    def test_ec45_cross_source(self):
        ref = self.c['verification_reference']
        data = (ROOT / ref['stored_copy']).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), ref['stored_copy_sha256'])
        txt = _plain(data.decode('latin-1'))
        m = re.search(r'VII as ações relativas às penalidades administrativas.*?VIII a execução, de ofício, das contribuições sociais '
                      r'previstas no art\. 195, I, a, e II, e seus acréscimos legais, decorrentes das sentenças que proferir; IX outras', txt)
        self.assertIsNotNone(m)

    def test_only_structural_label_changed(self):
        before, after = self.c['exact_raw_text'], self.c['normalized_text']
        self.assertEqual((self.c['correction_type'], self.c['not_a']), ('SOURCE_TRANSCRIPTION_NORMALIZATION', 'LEGAL_CONTENT_EDIT'))
        self.assertTrue(before.startswith('VII I - ') and after.startswith('VIII - '))
        self.assertEqual(before[len('VII I'):], after[len('VIII'):])                   # body identical
        self.assertEqual(before.replace(' ', ''), after.replace(' ', ''))              # only the spurious space removed

    def test_runtime_sequence_114(self):
        lines = (SD / '05_TEXT/CF88_RUNTIME.txt').read_text(encoding='utf-8').split('\n')
        i = next(k for k, l in enumerate(lines) if l.startswith('Art. 114.'))
        labels = [re.match(r'^([IVXLC]+) -', l).group(1) for l in lines[i + 1:i + 10] if re.match(r'^[IVXLC]+ -', l)]
        self.assertEqual(labels, ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'])
        self.assertIn(self.c['normalized_text'], lines)
        self.assertNotIn(self.c['exact_raw_text'], lines)
        idx = {t['target_id']: t for t in json.loads((HOST / 'CF88_RUNTIME_TARGET_INDEX.json').read_text(encoding='utf-8'))['targets']}
        for tid in ('CF88:ART.114:INC.VII', 'CF88:ART.114:INC.VIII', 'CF88:ART.114:INC.IX'):
            self.assertIn(tid, idx)
        self.assertTrue(idx['CF88:ART.114:INC.VIII']['preview'].startswith('a execução, de ofício, das contribuições sociais'))
        # VII no longer absorbs VIII: its full body hash is exactly its own line
        vii = 'as ações relativas às penalidades administrativas impostas aos empregadores pelos órgãos de fiscalização das relações de trabalho;'
        self.assertEqual(idx['CF88:ART.114:INC.VII']['text_sha256_current'], hashlib.sha256(vii.encode('utf-8')).hexdigest())
        viii = self.c['normalized_text'][len('VIII - '):]
        self.assertEqual(idx['CF88:ART.114:INC.VIII']['text_sha256_current'], hashlib.sha256(viii.encode('utf-8')).hexdigest())
        prov = json.loads((HOST / 'CF88_RUNTIME.provenance.json').read_text(encoding='utf-8'))
        self.assertEqual([c['correction_id'] for c in prov['source_text_corrections']], [CID])

    def test_fail_closed(self):
        entry = self.lock['sources']['CF88']
        text = (self.cf_dir / 'normalizado.txt').read_text(encoding='utf-8')
        out, applied = XR.apply_source_corrections('CF88', text, entry, self.corr)
        self.assertEqual(len(applied), 1)
        # hash of the publication changed -> refuse
        bad = dict(entry, raw_sha256='0' * 64)
        with self.assertRaises(XR.ExportError):
            XR.apply_source_corrections('CF88', text, bad, self.corr)
        # exact line absent (e.g. the Senado fixed it) -> refuse, review required
        with self.assertRaises(XR.ExportError):
            XR.apply_source_corrections('CF88', text.replace(self.c['exact_raw_text'], self.c['normalized_text']), entry, self.corr)
        # duplicated -> refuse
        with self.assertRaises(XR.ExportError):
            XR.apply_source_corrections('CF88', text + '\n' + self.c['exact_raw_text'], entry, self.corr)
        # not reviewed -> refuse
        c2 = copy.deepcopy(self.corr)
        c2['corrections'][0]['reviewed'] = False
        with self.assertRaises(XR.ExportError):
            XR.apply_source_corrections('CF88', text, entry, c2)
        # ADCT has no correction: untouched
        adct = (SRC / self.lock['sources']['ADCT']['dir'] / 'normalizado.txt').read_text(encoding='utf-8')
        self.assertEqual(XR.apply_source_corrections('ADCT', adct, self.lock['sources']['ADCT'], self.corr), (adct, []))


class ReviewedExceptionsTest(unittest.TestCase):
    def test_three_exceptions_and_no_unexpected(self):
        diff = json.loads((HOST / 'TARGET_DIFF_LEGACY_VS_RUNTIME.json').read_text(encoding='utf-8'))
        rows = {r['target_id']: r for r in diff['rows']}
        self.assertEqual((rows['CF88:ART.155:INC.I:AL.c']['change'], rows['CF88:ART.155:INC.I:AL.c']['classification']),
                         ('REMOVED', 'EXPECTED_REMOVAL_HISTORICAL'))
        for al in ('a', 'b'):
            r = rows[f'ADCT:ART.77:INC.I:AL.{al}']
            self.assertEqual((r['change'], r['classification']), ('ADDED', 'EXPECTED_RUNTIME_CHANGE'))
        self.assertFalse([r for r in diff['rows'] if r['classification'] in ('UNEXPECTED_MISSING', 'UNEXPECTED_NEW', 'PARSER_ERROR')])
        runtime = (SD / '05_TEXT/CF88_RUNTIME.txt').read_text(encoding='utf-8')
        self.assertIn('\nIII - propriedade de veículos automotores.\n', runtime)          # IPVA is now art. 155, III
        self.assertIn('\na) no anº 2000, o montante empenhado', runtime)
        self.assertIn('\nb) do anº 2001 ao anº 2004', runtime)


class HistoricalReferenceFilterTest(unittest.TestCase):
    def test_filtered_targets_are_not_navigable(self):
        m = json.loads((SD / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
        filt = m['layer_validation']['historical_reference_targets_filtered']
        names = sorted(f['target_id'] for f in filt)
        self.assertEqual(names, ['CF88:ART.40:PAR.4:INC.II', 'CF88:ART.40:PAR.4:INC.III', 'CF88:ART.40:PAR.7:INC.I'])
        self.assertTrue(all(f['status'] == 'HISTORICAL_REFERENCE_TARGET_FILTERED' for f in filt))
        targets = {l.split('|')[0] for l in (SD / '10_TARGETS/CF88_TARGETS.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')}
        mapped = {l.split('|')[2] for l in (SD / '10_TARGETS/CF88_TEXT_MAP.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')}
        rows = [l.split('|') for l in (SD / '20_REFERENCES/REF_PAYLOAD.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
        dev = S.Device(SD)
        try:
            for t in names:
                self.assertNotIn(t, targets)                     # not navigable
                self.assertNotIn(t, mapped)                      # never produced by TEXT_MAP
                q = dev.query(t)
                self.assertEqual((q['status'], q['entenda_available']), ('INVALID_OR_UNKNOWN_TARGET', False))
                self.assertNotIn('layers', q)                    # no layer/button
                mine = [r for r in rows if r[0] == t]
                self.assertTrue(mine and all(r[2] == 'HISTORICAL_HIDDEN_BY_DEFAULT' for r in mine))
                # their reference ids are not attached to any CURRENT visible target by the device view
                for r in mine:
                    self.assertFalse([x for x in rows if x[4] == r[4] and x[0] != t and x[0] in targets and x[2] == 'CURRENT_VISIBLE'
                                      and x[0].rsplit(':', 1)[0] == t.rsplit(':', 1)[0]])
            # the approved Reference Engine export itself is untouched (byte copy)
            ref_dir = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run1'
            self.assertEqual((SD / '20_REFERENCES/REF_PAYLOAD.IDX').read_bytes(), (ref_dir / 'REF_PAYLOAD.IDX').read_bytes())
            # art. 114, VIII now exists; its approved references stay hidden (no layer shown)
            v = dev.query('CF88.114.VIII')
            self.assertEqual((v['status'], v['layers']['HAS_JURISPRUDENCIA'], v['layers']['HAS_CORRELATAS']), ('OK', False, False))
        finally:
            dev.close()

    def test_entenda_and_pilots(self):
        dev = S.Device(SD)
        try:
            for q, anchor in (('CF88.37.6', 'CF88:ART.37:PAR.6'), ('CF88.60.4.IV', 'CF88:ART.60:PAR.4:INC.IV'), ('ADCT.10.II', 'ADCT:ART.10:INC.II')):
                r = dev.query(q)
                self.assertEqual((r['status'], r['resolution_type'], r['anchor_target_id'], r['review']), ('OK', 'DIRECT', anchor, 'HUMAN_APPROVED_T1'))
        finally:
            dev.close()
        m = json.loads((SD / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual((m['entenda_explanation_count'], m['layer_validation']['entenda_direct'], m['layer_validation']['entenda_resolved']), (163, 163, 283))
        payload = (SD / '30_ENTENDA/ENTENDA_PAYLOAD.DAT').read_bytes()
        self.assertNotIn(b'PENDING_HUMAN_REVIEW', payload)
        self.assertNotIn(b'RETIRED', payload)


if __name__ == '__main__':
    unittest.main()
