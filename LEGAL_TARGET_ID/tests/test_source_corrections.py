"""Regression tests: approved source transcription corrections in the parser (art. 114, VIII) and the target status errata
(art. 114, VIII; art. 155, I, c). The frozen CF88_TARGET_STATUS.json is never rewritten."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import reference_canonicalization as RC  # noqa: E402
import source_corrections as SC  # noqa: E402
import status_errata as SE  # noqa: E402
import structure_parser as SP  # noqa: E402

SENADO = REPO / 'updater/fontes_oficiais_senado/CF88/16434817_5beff7a4/normalizado.txt'
CORR_ID = 'SRC-CORR-CF88-579494-16434817-ART114-INC-VIII'
EXEC = 'a execução, de ofício, das contribuições sociais'


def operational_bytes():
    """The operational text is git-ignored; on a clean clone it is rebuilt byte-exact by the recipe of the text source reconstruction."""
    if RC.OPERATIONAL.is_file():
        return RC.OPERATIONAL.read_bytes()
    sys.path.insert(0, str(REPO / 'ENTENDA_ENGINE'))
    import text_source_reconstruction as TSR
    return TSR.reconstruct(RC.OPERATIONAL.relative_to(REPO).as_posix())


def parsed(text, corrections):
    ts, anomalies, _ = SP.parse_structure(text, 'CF88', end_markers=RC.END, preview_len=10 ** 6, source_corrections=corrections)
    return {t['target_id']: t for t in ts}, anomalies


class SourceCorrectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = operational_bytes().decode('utf-8-sig')
        cls.reg = SC.load()
        cls.corr = next(c for c in cls.reg if c['correction_id'] == CORR_ID)

    def test_source_itself_has_the_defect(self):
        """Category A (fonte): the Senado text carries "VII I"; nothing in Git was edited by hand."""
        raw = SENADO.read_text(encoding='utf-8').splitlines()
        self.assertEqual(sum(1 for l in raw if l == self.corr['exact_raw_text']), 1)
        self.assertEqual(hashlib.sha256(SENADO.read_bytes()).hexdigest(), self.corr['normalized_source_sha256'])

    def test_without_correction_reproduces_the_anomaly(self):
        t, _ = parsed(self.text, False)
        self.assertNotIn('CF88:ART.114:INC.VIII', t)
        self.assertIn(EXEC, t['CF88:ART.114:INC.VII']['preview'])

    def test_with_correction_vii_and_viii_are_separate(self):
        t, anomalies = parsed(self.text, True)
        self.assertIn('CF88:ART.114:INC.VIII', t)
        self.assertTrue(t['CF88:ART.114:INC.VIII']['preview'].startswith(EXEC))
        self.assertNotIn(EXEC, t['CF88:ART.114:INC.VII']['preview'])
        self.assertTrue(t['CF88:ART.114:INC.IX']['preview'].startswith('outras controvérsias'))
        used = [a for a in anomalies if a['code'] == 'SOURCE_TEXT_CORRECTION']
        self.assertEqual([a['text'] for a in used], [CORR_ID])
        self.assertEqual(used[0]['correction']['cross_source'], str(SC.CANONICAL['CF88'].relative_to(REPO)).replace('\\', '/'))

    def test_input_text_not_modified(self):
        lines = self.text.splitlines()
        before = list(lines)
        SC.apply(lines, 'CF88')
        self.assertEqual(lines, before)

    def test_absent_line_is_a_no_op(self):
        out, used = SC.apply(['VIII - a execução'], 'CF88', self.reg)
        self.assertEqual((out, used), (['VIII - a execução'], []))

    def test_fail_closed(self):
        lines = [self.corr['exact_raw_text']]
        cases = {
            'NOT_APPROVED': dict(self.corr, status='PROPOSED'),
            'OCCURRENCES': dict(self.corr, expected_occurrences=2),
            'CHANGES_BODY': dict(self.corr, normalized_text=self.corr['normalized_text'].replace('proferir', 'julgar')),
            'NOT_CROSS_VERIFIED': dict(self.corr, exact_raw_text='VII I - texto inventado', normalized_text='VIII - texto inventado'),
        }
        for code, c in cases.items():
            with self.subTest(code=code):
                with self.assertRaises(SC.SourceCorrectionError) as cm:
                    SC.apply([c['exact_raw_text']] if code == 'NOT_CROSS_VERIFIED' else list(lines), 'CF88', [c])
                self.assertIn(code, str(cm.exception))

    def test_other_norm_untouched(self):
        out, used = SC.apply([self.corr['exact_raw_text']], 'ADCT', self.reg)
        self.assertEqual(used, [])


class StatusErrataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = None
        if not RC.OPERATIONAL.is_file():
            cls.tmp = tempfile.TemporaryDirectory()
            p = Path(cls.tmp.name) / 'op.txt'
            p.write_bytes(operational_bytes())
            cls.orig, RC.OPERATIONAL = RC.OPERATIONAL, p
        cls.doc = SE.build()
        cls.versioned = json.loads(SE.ERRATA.read_text(encoding='utf-8'))

    @classmethod
    def tearDownClass(cls):
        if cls.tmp:
            RC.OPERATIONAL = cls.orig
            cls.tmp.cleanup()

    def test_errata_is_reproducible_from_git(self):
        self.assertEqual(self.doc, self.versioned)

    def test_frozen_status_untouched(self):
        frozen = SE.FROZEN.read_bytes()
        self.assertEqual(self.versioned['base_status_sha256'], hashlib.sha256(frozen).hexdigest())
        st = json.loads(frozen)['targets']
        self.assertEqual(st['CF88:ART.114:INC.VIII']['status'], 'HISTORICAL_ONLY')
        self.assertEqual(st['CF88:ART.155:INC.I:AL.c']['status'], 'CURRENT')

    def test_exactly_the_two_corrections(self):
        t = self.versioned['targets']
        self.assertEqual(sorted(t), ['CF88:ART.114:INC.VIII', 'CF88:ART.155:INC.I:AL.c'])
        self.assertEqual(t['CF88:ART.114:INC.VIII']['corrected']['status'], 'CURRENT')
        self.assertEqual(t['CF88:ART.114:INC.VIII']['cause'], dict(kind='SOURCE_TEXT_CORRECTION', correction_id=CORR_ID))
        self.assertEqual(t['CF88:ART.155:INC.I:AL.c']['corrected']['status'], 'HISTORICAL_ONLY')
        self.assertIn('CF88:ART.155:INC.III', t['CF88:ART.155:INC.I:AL.c']['corrected']['reason'])

    def test_renumbered_label_ignores_final_punctuation_only(self):
        self.assertEqual(RC._head('propriedade de veículos automotores.'), RC._head('propriedade de veículos automotores'))
        self.assertNotEqual(RC._head('propriedade de veículos automotores terrestres'), RC._head('propriedade de veículos automotores'))

    def test_overlay_fail_closed(self):
        base = SE.FROZEN.read_bytes()
        st = json.loads(base)['targets']
        out, rows = SE.overlay(st, base)
        self.assertEqual(out['CF88:ART.114:INC.VIII']['status'], 'CURRENT')
        self.assertEqual(st['CF88:ART.114:INC.VIII']['status'], 'HISTORICAL_ONLY')   # input not mutated
        with self.assertRaises(SE.StatusErrataError):
            SE.overlay(st, base + b' ')
        bad = dict(st, **{'CF88:ART.114:INC.VIII': dict(st['CF88:ART.114:INC.VIII'], reason='x')})
        with self.assertRaises(SE.StatusErrataError):
            SE.overlay(bad, base)


if __name__ == '__main__':
    unittest.main()
