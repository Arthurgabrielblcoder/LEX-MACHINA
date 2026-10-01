"""CAPUT EQUIVALENCE (uncommitted until the human test): ART.n <-> ART.n:CAPUT only on the visual caput.

Limitation found after the exact-target migration: the approved CF88_TEXT_MAP maps the caput text line to "CF88:ART.n"
(TARGET_RESOLUTION_STRATEGY: on the article line ART.n wins over ART.n:CAPUT), while 32 visible approved links point to
"CF88:ART.n:CAPUT" (17 targets) and were never reachable. Three more targets (art. 40 §4 II/III, §7 I) hold only 6
HISTORICAL_HIDDEN rows: hidden by design, not affected.

Approved rule (resolution only, DEVICE V1 layers 1/2/4; ENTENDA untouched; no data changed):
lexV1QueryKeysForActiveTarget("CF88:ART.n") = [ART.n, ART.n:CAPUT]; any other target -> [target].
Records of the keys are unioned and deduplicated by (destination_layer, SOURCE_ID). No inheritance to descendants.
"""
import collections
import sys
import tempfile
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(DI / 'tests'))
import canonical_layer_audit as A  # noqa: E402
import device_lookup_simulator as S  # noqa: E402
from test_a3b_prep import INO, SD  # noqa: E402
from test_canonical_layers import build_ref_files  # noqa: E402

CORRELATA, JURIS, REFERENCIA = A.CORRELATA, A.JURIS, A.REFERENCIA


def func(name):
    body = INO[INO.index(name):]
    return body[:body.index('\n}\n')]


def ids(u, layer):
    return [r[5] for r in u.get(layer, [])]


class FixtureDevice:
    """Device stand-in over fixture REF files (the audit's device_query only needs .references)."""

    def __init__(self, d):
        self.d = d

    def references(self, tid):
        ix = S.SortedIndex(self.d / 'REF_LOOKUP.IDX')
        try:
            row = ix.find(tid)
        finally:
            ix.close()
        if not row:
            return []
        with open(self.d / 'REF_PAYLOAD.IDX', 'rb') as f:
            f.seek(int(row[1]))
            return [f.readline().decode('utf-8').rstrip('\n').split('|') for _ in range(int(row[2]))]


class QueryKeysTest(unittest.TestCase):
    def test_only_the_article_line_gets_two_keys(self):
        self.assertEqual(A.query_keys('CF88:ART.5'), ['CF88:ART.5', 'CF88:ART.5:CAPUT'])
        self.assertEqual(A.query_keys('CF88:ART.37'), ['CF88:ART.37', 'CF88:ART.37:CAPUT'])
        self.assertEqual(A.query_keys('CF88:ART.5-A'), ['CF88:ART.5-A', 'CF88:ART.5-A:CAPUT'])
        for t in ('CF88:ART.5:INC.V', 'CF88:ART.37:PAR.6', 'CF88:ART.5:CAPUT', 'CF88:ART.34:INC.V:AL.B',
                  'CF88:ART.1:PAR.UNICO', 'ADCT:ART.10:INC.II', 'ADCT:ART.2', 'CF88'):
            self.assertEqual(A.query_keys(t), [t], t)

    def test_firmware_rule_mirrors_host(self):
        f = func('static int lexV1QueryKeysForActiveTarget(const char *tid, char (*out)[LEXV1_KEY_MAX])')
        self.assertIn('if(!strncmp(tid,"CF88:ART.",9) && tid[9] && !strchr(tid+9,\':\')', f)
        self.assertIn('snprintf(out[1],LEXV1_KEY_MAX,"%s:CAPUT",tid);', f)
        self.assertEqual(INO.count('lexV1QueryKeysForActiveTarget('), 4)       # definition + lists 1/2 + list 4 + availability
        for name in ('static bool lexV1CarregarRelacoesTarget(const char *tid)', 'static int lexV1CarregarItensRef(const char *tid)\n{',
                     'bool lexV1AtualizarDisponibilidade(bool forcar)\n{'):
            self.assertIn('lexV1QueryKeysForActiveTarget(', func(name), name)

    def test_entenda_untouched(self):
        e = func('static void lexV1MontarEntenda(const char *tid)')
        self.assertNotIn('QueryKeys', e)
        self.assertIn('st=lexv1Entenda(lookup,&pl,tid,e);', e)
        d = func('bool lexV1AtualizarDisponibilidade(bool forcar)\n{')
        self.assertIn("if(c==0) lexV1Disp.entenda=(t.flags[0]=='E' || t.flags[0]=='B');", d)   # ENTENDA only from ACTIVE_TARGET


class FixtureUnionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        j = lambda t, s: [t, 'JURISPRUDENCE', 'CURRENT_VISIBLE', 'CURRENT', f'JURISPRUDENCE:{s}@{t}', s, s]  # noqa: E731
        w = lambda t, s: [t, 'WORK_REFERENCE', 'CURRENT_VISIBLE', 'CURRENT', f'WORK_REFERENCE:{s}@{t}', s, s]  # noqa: E731
        build_ref_files(d, [j('CF88:ART.9', 'J1'), j('CF88:ART.9:CAPUT', 'J2'), j('CF88:ART.9:CAPUT', 'J1'),
                            w('CF88:ART.9:CAPUT', 'W1'), j('CF88:ART.9:INC.I', 'J3'), j('CF88:ART.9:PAR.1', 'J4')])
        self.dev = FixtureDevice(d)

    def tearDown(self):
        self.tmp.cleanup()

    def test_art_plus_caput_union(self):
        u, _ = A.device_query_union(self.dev, 'CF88:ART.9')
        self.assertEqual(ids(u, JURIS), ['J1', 'J2'])
        self.assertEqual(ids(u, REFERENCIA), ['W1'])

    def test_dedup(self):
        u, dups = A.device_query_union(self.dev, 'CF88:ART.9')
        self.assertEqual(dups, 1)                                  # J1 on ART.9 and on ART.9:CAPUT -> shown once
        self.assertEqual(ids(u, JURIS).count('J1'), 1)

    def test_no_descendant_inheritance(self):
        for t, own in (('CF88:ART.9:INC.I', ['J3']), ('CF88:ART.9:PAR.1', ['J4']), ('CF88:ART.9:INC.II', [])):
            u, _ = A.device_query_union(self.dev, t)
            self.assertEqual(ids(u, JURIS), own, t)
            self.assertEqual(ids(u, REFERENCIA), [], t)


class RealDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = S.Device(SD)
        cls.r = A.audit()
        cls.flags = {p[0]: p[3] for p in A.rows(SD / '10_TARGETS/CF88_TARGETS.IDX')}
        cls.mapped = {p[2] for p in A.rows(SD / '10_TARGETS/CF88_TEXT_MAP.IDX')}

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def u(self, t):
        return A.device_query_union(self.dev, t)[0]

    def avail(self, t, layer):                                   # mirror of lexV1AtualizarDisponibilidade (union of flags)
        return any(A.flag(self.flags.get(k, '------'), layer) for k in A.query_keys(t))

    def test_rg113_caput_art5(self):
        u = self.u('CF88:ART.5')
        self.assertEqual(ids(u, JURIS), ['STF:RG:113'])
        self.assertEqual(sorted(ids(u, REFERENCIA)), ['REF-FIL-0004', 'REF-LIV-0006'])
        self.assertTrue(self.avail('CF88:ART.5', JURIS))           # footer shows 2 JURIS. ...
        self.assertTrue(self.avail('CF88:ART.5', REFERENCIA))      # ... and 4 REF.
        self.assertFalse(A.flag(self.flags['CF88:ART.5'], JURIS))  # the ART.n flags alone would have hidden it

    def test_rg113_excluded_from_incisos(self):
        for inc in ('V', 'VI', 'VIII', 'XV', 'I', 'II'):
            t = f'CF88:ART.5:INC.{inc}'
            self.assertNotIn('STF:RG:113', ids(self.u(t), JURIS), t)
        self.assertEqual(ids(self.u('CF88:ART.5:INC.V'), JURIS), ['STF:RG:995'])
        self.assertEqual(ids(self.u('CF88:ART.5:INC.VIII'), JURIS), ['STF:RG:1021', 'STF:RG:386'])

    def test_paragraph_exclusion_art37(self):
        self.assertEqual(ids(self.u('CF88:ART.37'), JURIS), ['STF:RG:66'])            # caput: RG 66
        p6 = ids(self.u('CF88:ART.37:PAR.6'), JURIS)
        self.assertNotIn('STF:RG:66', p6)
        self.assertEqual(sorted(p6), sorted(['STF:RG:1031', 'STF:RG:130', 'STF:RG:362', 'STF:RG:365', 'STF:RG:940']))
        for t in self.mapped:
            if t.startswith('CF88:ART.37:'):
                self.assertNotIn('STF:RG:66', ids(self.u(t), JURIS), t)

    def test_32_links_17_targets_all_reachable(self):
        ce = self.r['caput_equivalence']
        links = ce['visible_links']
        self.assertEqual(len(links), 32)
        self.assertEqual(len({c['target_id'] for c in links}), 17)
        self.assertTrue(all(c['target_id'].endswith(':CAPUT') for c in links))
        self.assertEqual(collections.Counter(c['destination_layer'] for c in links), {REFERENCIA: 25, JURIS: 6, CORRELATA: 1})
        self.assertEqual(ce['unreachable_after_rule'], [])
        for c in links:
            self.assertEqual(c['reached_by'], [c['target_id'][:-len(':CAPUT')]])           # only by its own article line
            self.assertTrue(self.avail(c['reached_by'][0], c['destination_layer']))
            self.assertIn(c['reference_id'], {r[4] for r in self.u(c['reached_by'][0])[c['destination_layer']]})
        self.assertEqual(ce['hidden_only_targets'],
                         ['CF88:ART.40:PAR.4:INC.II', 'CF88:ART.40:PAR.4:INC.III', 'CF88:ART.40:PAR.7:INC.I'])
        self.assertEqual(ce['duplicates'], 0)

    def test_no_leak_and_union_equals_export(self):
        exp, _ = A.expected_groups()
        leaks = mism = 0
        for a in self.mapped:
            u = self.u(a)
            for layer in (CORRELATA, JURIS, REFERENCIA):
                want = set().union(*(exp[k][layer] for k in A.query_keys(a)))
                got = {r[4] for r in u.get(layer, [])}
                mism += want != got
                leaks += sum(1 for r in u.get(layer, []) if r[0] not in A.query_keys(a))
                self.assertEqual(bool(got), self.avail(a, layer), (a, layer))           # footer == list
        self.assertEqual((leaks, mism), (0, 0))

    def test_detail_keyed_by_real_link_target(self):
        load = func('static int lexV1CarregarItensRef(const char *tid)\n{')
        self.assertIn('it.d=lexV1BuscarDetalhe(chaves[c],it.fonte);', load)
        hdr = (DI.parent / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h').read_text(encoding='utf-8')
        self.assertIn('"CF88:ART.5:CAPUT|REF-LIV-0006"', hdr)


if __name__ == '__main__':
    unittest.main()
