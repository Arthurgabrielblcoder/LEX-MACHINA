"""Permanent tests for the canonical legal target_id grammar and the structural parser (CF88 pilot)."""
import hashlib
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import build_target_index as B  # noqa: E402
import structure_parser as SP  # noqa: E402
import target_id as T  # noqa: E402

REPO = HERE.parent
CF_SOURCE = REPO / 'updater/backup_catalogos/catalogo_mestre_20260913_145217/1- CONSTITUI#U00c7#U00c3O FEDERAL/cf.txt'
CF_SHA = 'd9f3d6b92ffd524c26a73e311f8c7daa4bf31772193d6d24932acff29c4c2da4'
END = ('Brasília, 5 de outubro de 1988',)

CORPUS = {
    'CF88': ('NORMA', None),
    'ADCT': ('NAMESPACE', 'CF88'),
    'CF88:ART.1': ('ARTIGO', 'CF88'),
    'CF88:ART.1:CAPUT': ('CAPUT', 'CF88:ART.1'),
    'CF88:ART.1:INC.III': ('INCISO', 'CF88:ART.1:CAPUT'),
    'CF88:ART.1:PAR.UNICO': ('PARAGRAFO_UNICO', 'CF88:ART.1'),
    'CF88:ART.5': ('ARTIGO', 'CF88'),
    'CF88:ART.5:INC.LXXVIII': ('INCISO', 'CF88:ART.5:CAPUT'),
    'CF88:ART.5:INC.XXVIII:AL.a': ('ALINEA', 'CF88:ART.5:INC.XXVIII'),
    'CF88:ART.5:PAR.4': ('PARAGRAFO', 'CF88:ART.5'),
    'CF88:ART.7:INC.XXXIV': ('INCISO', 'CF88:ART.7:CAPUT'),
    'CF88:ART.7:PAR.UNICO': ('PARAGRAFO_UNICO', 'CF88:ART.7'),
    'CF88:ART.37': ('ARTIGO', 'CF88'),
    'CF88:ART.37:CAPUT': ('CAPUT', 'CF88:ART.37'),
    'CF88:ART.37:INC.XXI': ('INCISO', 'CF88:ART.37:CAPUT'),
    'CF88:ART.37:PAR.6': ('PARAGRAFO', 'CF88:ART.37'),
    'CF88:ART.37:PAR.10': ('PARAGRAFO', 'CF88:ART.37'),
    'CF88:ART.37:PAR.8:INC.II': ('INCISO', 'CF88:ART.37:PAR.8'),
    'CF88:ART.40:PAR.4-A': ('PARAGRAFO', 'CF88:ART.40'),
    'CF88:ART.60:PAR.4': ('PARAGRAFO', 'CF88:ART.60'),
    'CF88:ART.60:PAR.4:INC.IV': ('INCISO', 'CF88:ART.60:PAR.4'),
    'CF88:ART.92:INC.II-A': ('INCISO', 'CF88:ART.92:CAPUT'),
    'CF88:ART.103-A:PAR.1': ('PARAGRAFO', 'CF88:ART.103-A'),
    'CF88:ART.150:INC.VI:AL.a': ('ALINEA', 'CF88:ART.150:INC.VI'),
    'CF88:ART.225:PAR.1:INC.VII': ('INCISO', 'CF88:ART.225:PAR.1'),
    'CF88:ART.92:INC.I-A': ('INCISO', 'CF88:ART.92:CAPUT'),
    'CF88:ART.109:INC.V-A': ('INCISO', 'CF88:ART.109:CAPUT'),
    'CF88:ART.114:INC.IX': ('INCISO', 'CF88:ART.114:CAPUT'),
    'ADCT:ART.120:PAR.UNICO:INC.III:AL.b': ('ALINEA', 'ADCT:ART.120:PAR.UNICO:INC.III'),
    'ADCT:ART.5': ('ARTIGO', 'ADCT'),
    'ADCT:ART.5:PAR.1': ('PARAGRAFO', 'ADCT:ART.5'),
    'ADCT:ART.107:PAR.6-A:INC.I': ('INCISO', 'ADCT:ART.107:PAR.6-A'),
}

INVALID = {
    'XX99:ART.1': 'UNKNOWN_NAMESPACE',
    'cf88:ART.1': 'NAMESPACE_MALFORMED',
    'CF88:ART.0': 'INVALID_ARTICLE',
    'CF88:ART.01': 'INVALID_ARTICLE',
    'CF88:ART.5a': 'INVALID_ARTICLE',
    'CF88:ARTIGO.5': 'UNKNOWN_LEVEL',
    'CF88:ART.': 'MALFORMED_SEGMENT',
    'CF88:ART.37:PAR.': 'MALFORMED_SEGMENT',
    'CF88:ART.37::PAR.6': 'EMPTY_SEGMENT',
    'CF88:ART.37:PAR.06': 'INVALID_PARAGRAPH',
    'CF88:ART.37:PAR.unico': 'INVALID_PARAGRAPH',
    'CF88:ART.37:INC.IIII': 'INVALID_INCISO',
    'CF88:ART.37:INC.21': 'INVALID_INCISO',
    'CF88:ART.37:INC.xxi': 'INVALID_INCISO',
    'CF88:ART.37:AL.a': 'ALINEA_WITHOUT_INCISO',
    'CF88:ART.37:PAR.6:AL.a': 'ALINEA_WITHOUT_INCISO',
    'CF88:ART.150:INC.VI:AL.A': 'INVALID_ALINEA',
    'CF88:PAR.6': 'MISSING_ARTICLE',
    'CF88:ART.37:INC.I:PAR.6': 'LEVEL_ORDER',
    'CF88:ART.37:CAPUT:INC.I': 'NON_CANONICAL',
    'CF88:ADCT:ART.5': 'NESTED_NAMESPACE',
    'ADCT:5': 'MALFORMED_SEGMENT',
    'ADCT:ART.5:ADCT': 'NESTED_NAMESPACE',
    '1- CONSTITUIÇÃO FEDERAL/cf.txt': 'NON_ASCII',
    'updater/saida/cf.txt': 'PATH_OR_WHITESPACE',
    'CF88:ART.37 PAR.6': 'PATH_OR_WHITESPACE',
    'CF88:ART.37:PAR.6º': 'NON_ASCII',
    'CF88/ART.37': 'PATH_OR_WHITESPACE',
    '': 'EMPTY',
    'CF88:ART.37:PAR.6:INC.I:AL.a:AL.b': 'LEVEL_ORDER',
}


class GrammarTest(unittest.TestCase):
    def test_corpus_kind_parent_roundtrip(self):
        for tid, (kind, parent) in CORPUS.items():
            t = T.parse_target_id(tid)
            self.assertEqual(t['kind'], kind, tid)
            self.assertEqual(T.parent_target_id(tid), parent, tid)
            again = T.format_target_id(t['namespace'], t['article'], t['caput'], t['paragraph'], t['inciso'], t['alinea'])
            self.assertEqual(again, tid)
            self.assertTrue(tid.isascii() and ' ' not in tid)

    def test_article_unit_differs_from_caput(self):
        self.assertNotEqual(T.parse_target_id('CF88:ART.37')['kind'], T.parse_target_id('CF88:ART.37:CAPUT')['kind'])
        self.assertEqual(T.ancestors('CF88:ART.37:INC.XXI'), ['CF88:ART.37:CAPUT', 'CF88:ART.37', 'CF88'])
        self.assertEqual(T.ancestors('CF88:ART.60:PAR.4:INC.IV'), ['CF88:ART.60:PAR.4', 'CF88:ART.60', 'CF88'])

    def test_adct_is_its_own_namespace(self):
        self.assertNotEqual('ADCT:ART.5', 'CF88:ART.5')
        self.assertEqual(T.ancestors('ADCT:ART.5:PAR.1'), ['ADCT:ART.5', 'ADCT', 'CF88'])
        self.assertEqual(T.parse_target_id('ADCT:ART.5')['norma_id'], 'CF88')
        self.assertEqual(T.parse_target_id('ADCT:ART.5')['namespace'], 'ADCT')

    def test_invalid_fail_closed(self):
        for tid, code in INVALID.items():
            ok, err = T.validate_target_id(tid)
            self.assertFalse(ok, tid)
            self.assertEqual(err, code, tid)
            with self.assertRaises(T.TargetIdError):
                T.parse_target_id(tid)

    def test_label_normalization(self):
        for s in ('1º', '1o', '1', ' 1º ', '1°'):
            self.assertEqual(T.normalize_number_label(s), '1')
        self.assertEqual(T.normalize_number_label('4º-A'), '4-A')
        self.assertEqual(T.normalize_number_label('103-A'), '103-A')
        for s in ('§ 6º', '§6º', '§ 6o', '§ 6', '6'):
            self.assertEqual(T.normalize_paragraph_label(s), '6')
        for s in ('Parágrafo único', 'parágrafo único.', 'Paragrafo unico', 'UNICO'):
            self.assertEqual(T.normalize_paragraph_label(s), 'UNICO')
        self.assertEqual(T.normalize_inciso_label('xxi'), 'XXI')
        self.assertEqual(T.normalize_alinea_label('a)'), 'a')
        for bad in ('primeiro', '06', '6-', 'seis', '§', ''):
            with self.assertRaises(T.TargetIdError):
                T.normalize_paragraph_label(bad) if bad != 'primeiro' else T.normalize_number_label(bad)
        for bad in ('IIII', 'IL', 'A'):
            with self.assertRaises(T.TargetIdError):
                T.normalize_inciso_label(bad)

    def test_converters_existing_serializations(self):
        self.assertEqual(T.from_pipe_fields('CF88', '5', '', 'XLIII', ''), 'CF88:ART.5:INC.XLIII')
        self.assertEqual(T.from_pipe_fields('CF88', '20', '1', '', ''), 'CF88:ART.20:PAR.1')
        self.assertEqual(T.from_pipe_fields('CF88', '7', 'unico', '', ''), 'CF88:ART.7:PAR.UNICO')
        self.assertEqual(T.from_colon_fields('CF88:1:-:III:-'), 'CF88:ART.1:INC.III')
        self.assertEqual(T.to_pipe_fields('CF88:ART.7:PAR.UNICO'), 'CF88|7|unico||')
        with self.assertRaises(T.TargetIdError):
            T.from_colon_fields('CF88:1:III')

    def test_registry_is_catalog_driven(self):
        reg = T.registry()
        self.assertEqual(len(reg.norms), 72)
        for ns in ('CC2002', 'CPC2015', 'CP1940', 'CPP1941', 'CTN1966', 'CDC1990'):
            self.assertEqual(T.parse_target_id(ns + ':ART.1:PAR.UNICO')['norma_id'], ns)
        with self.assertRaises(T.TargetIdError):
            T.NamespaceRegistry(['CF88'], {'CF88': {'parent': 'CF88'}})
        with self.assertRaises(T.TargetIdError):
            T.NamespaceRegistry(['CF88'], {'ADCT': {'parent': 'XX'}})


class ParserFixtureTest(unittest.TestCase):
    TEXT = '\n'.join([
        'PREÂMBULO', 'TÍTULO I', 'DOS PRINCÍPIOS', 'Art. 1º Caput um:', 'I - a soberania;', 'II-A - incluído;',
        'Parágrafo único. Todo o poder.', 'Art 2 Caput dois.', 'ART. 3º Caput tres:', 'a) alinea solta',
        'art. 4o Caput quatro:', '§ 1º Primeiro.', '§ 4º - Será declarada', '§ 4º-A. Incluído A.', '§ 4º-B Incluído B.',
        '§ 10. Dez.', 'I - inciso do par;', 'a) alinea;', 'Art.', '5º Caput cinco.', 'Art. 5º Caput cinco nova redação.',
        'Brasília, 5 de outubro de 1988.', 'Assinaturas', 'ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS',
        'Art. 5º Caput ADCT cinco.', '§ 1º ADCT par.', 'Art. 60.Colado sem espaço.', 'Parágrafo único. Histórico.'])

    def test_fixture(self):
        targets, anomalies, _ = SP.parse_structure(self.TEXT, 'CF88', end_markers=END)
        ids = [t['target_id'] for t in targets]
        self.assertEqual(len(ids), len(set(ids)))
        for tid in ('CF88', 'CF88:ART.1', 'CF88:ART.1:CAPUT', 'CF88:ART.1:INC.I', 'CF88:ART.1:INC.II-A', 'CF88:ART.1:PAR.UNICO',
                    'CF88:ART.2:CAPUT', 'CF88:ART.3:CAPUT', 'CF88:ART.4:PAR.4', 'CF88:ART.4:PAR.4-A', 'CF88:ART.4:PAR.4-B',
                    'CF88:ART.4:PAR.10:INC.I:AL.a', 'CF88:ART.5:CAPUT', 'ADCT', 'ADCT:ART.5', 'ADCT:ART.5:PAR.1',
                    'ADCT:ART.60:PAR.UNICO'):
            self.assertIn(tid, ids)
        self.assertNotIn('CF88:ART.4:PAR.4-S', ids)
        by = {t['target_id']: t for t in targets}
        self.assertEqual(len(by['CF88:ART.5:CAPUT']['occurrences']), 2)
        self.assertEqual(by['CF88:ART.5:CAPUT']['preview'], 'Caput cinco nova redação.')
        self.assertNotIn('Assinaturas', by['CF88:ART.5:CAPUT']['preview'])
        self.assertTrue(any(a['code'] == 'ALINEA_WITHOUT_INCISO' for a in anomalies))
        self.assertNotIn('ADCT:ART.5', [t for t in ids if t.startswith('CF88')])

    def test_unmarked_incisos_only_in_sequence(self):
        text = '\n'.join(['Art. 7º Compete:', 'I as ações;', 'I-A o conselho;', 'II outras;', 'III mais;',
                         'Art. 8º Sem dois pontos.', 'I solto sem enumeração', 'Art. 9º Lista:', 'I - um;', 'V pulando;'])
        targets, anomalies, _ = SP.parse_structure(text, 'CF88')
        ids = [t['target_id'] for t in targets]
        for tid in ('CF88:ART.7:INC.I', 'CF88:ART.7:INC.I-A', 'CF88:ART.7:INC.II', 'CF88:ART.7:INC.III', 'CF88:ART.9:INC.I'):
            self.assertIn(tid, ids)
        self.assertNotIn('CF88:ART.8:INC.I', ids)
        self.assertNotIn('CF88:ART.9:INC.V', ids)
        rejected = [a['label'] for a in anomalies if a['code'] == 'POSSIBLE_INCISO_WITHOUT_SEPARATOR']
        self.assertEqual(rejected, ['I', 'V'])
        by = {t['target_id']: t for t in targets}
        self.assertEqual(by['CF88:ART.7:INC.I']['preview'], 'as ações;')
        self.assertEqual(len(by['CF88:ART.7:INC.I']['occurrences']), 1)

    def test_unknown_norm_fails(self):
        with self.assertRaises(T.TargetIdError):
            SP.parse_structure('Art. 1º x', 'XX99')
        with self.assertRaises(T.TargetIdError):
            SP.parse_structure('Art. 1º x', 'ADCT')


@unittest.skipUnless(CF_SOURCE.is_file(), 'CF source not available')
class RealConstitutionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.idx1 = B.build('CF88', CF_SOURCE, END)
        cls.idx2 = B.build('CF88', CF_SOURCE, END)
        cls.T = {t['target_id']: t for t in cls.idx1['targets']}

    def test_source_hash(self):
        self.assertEqual(self.idx1['source']['sha256'], CF_SHA)

    def test_no_duplicates_and_deterministic(self):
        self.assertEqual(self.idx1['target_id_duplicates'], 0)
        self.assertEqual(self.idx1['target_index_sha256'], self.idx2['target_index_sha256'])
        ids = sorted(self.T)
        self.assertEqual(hashlib.sha256('\n'.join(ids).encode('ascii')).hexdigest(), self.idx1['target_index_sha256'])

    def test_corpus_exists_in_real_cf(self):
        for tid, (kind, parent) in CORPUS.items():
            self.assertIn(tid, self.T, tid)
            self.assertEqual(self.T[tid]['parent_id'], parent, tid)
            self.assertEqual(self.T[tid]['kind'], kind, tid)

    def test_all_parents_exist_and_every_id_valid(self):
        for tid, t in self.T.items():
            self.assertEqual(T.validate_target_id(tid), (True, None))
            if t['parent_id']:
                self.assertIn(t['parent_id'], self.T, tid)

    def test_art37_structure(self):
        pars = [k for k, t in self.T.items() if t['parent_id'] == 'CF88:ART.37' and t['kind'] == 'PARAGRAFO']
        self.assertIn('CF88:ART.37:PAR.6', pars)
        self.assertIn('CF88:ART.37:PAR.10', pars)
        caput_incisos = [k for k, t in self.T.items() if t['parent_id'] == 'CF88:ART.37:CAPUT']
        self.assertIn('CF88:ART.37:INC.I', caput_incisos)
        self.assertIn('CF88:ART.37:INC.XXI', caput_incisos)
        self.assertTrue(self.T['CF88:ART.37:PAR.6']['preview'].startswith('As pessoas jurídicas de direito público'))

    def test_art60_par4_clauses(self):
        kids = sorted(k for k, t in self.T.items() if t['parent_id'] == 'CF88:ART.60:PAR.4')
        self.assertEqual(kids, ['CF88:ART.60:PAR.4:INC.I', 'CF88:ART.60:PAR.4:INC.II', 'CF88:ART.60:PAR.4:INC.III', 'CF88:ART.60:PAR.4:INC.IV'])

    def test_adct_separate_from_body(self):
        self.assertIn('ADCT:ART.5', self.T)
        self.assertIn('CF88:ART.5', self.T)
        self.assertNotEqual(self.T['ADCT:ART.5:CAPUT']['preview'], self.T['CF88:ART.5:CAPUT']['preview'])
        self.assertEqual(self.idx1['counts_by_namespace']['ADCT']['ARTIGO'], 148)
        self.assertEqual(self.idx1['counts_by_namespace']['CF88']['ARTIGO'], 276)

    def test_superset_of_v2_segmentation_keys(self):
        import json
        import re
        v2 = json.loads((REPO / 'CF_SEGMENTADA_V2/CF_DISPOSITIVOS_LIMPOS.json').read_text(encoding='utf-8'))['dispositivos']
        for d in v2:
            k = d['chave_dispositivo']
            k = k + ':CAPUT' if re.fullmatch(r'[A-Z0-9]+:ART\.[0-9A-Z-]+', k) else k
            self.assertIn(k, self.T, k)


if __name__ == '__main__':
    unittest.main()
