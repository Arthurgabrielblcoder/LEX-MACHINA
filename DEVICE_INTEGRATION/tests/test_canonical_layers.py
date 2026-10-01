"""CANONICAL LAYERS (uncommitted until the human test): layers 1 CORR. and 2 JURIS. by EXACT target.

Physical bug (Arthur): Art. 5, V / VI / VIII / XV showed exactly the same list in 1 and 2. Root cause: in DEVICE V1,
lexV1SincronizarRelacoes keyed layers 1/2 by ARTICLE ("CF88:ART.5") and loaded them once per article through the legacy
per-article indices (JUR_LOOKUP / REL_LOOKUP, most-specific key with ARTICLE fallback): art. 5 caput key = RG 113/969/995,
then never reloaded while scrolling inside art. 5.

Fix mirrored here: ACTIVE_TARGET -> REF_LOOKUP (exact key) -> REF_PAYLOAD rows of that key -> lexV1ClassificarDestino;
1 shows only CORRELATA, 2 only JURISPRUDENCIA, 4 only REFERENCIA. No ancestor/descendant expansion (the approved export has no
ARTICLE_WIDE / APPLIES_TO_DESCENDANTS / COVERAGE field). Availability = TARGETS flags C/J/W, which are derived from the same
exact records (audited below). The legacy indices only resolve the chosen ITEM by its id (thesis file / external law).
"""
import collections
import re
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

CORRELATA, JURIS, REFERENCIA = A.CORRELATA, A.JURIS, A.REFERENCIA


def func(name):
    body = INO[INO.index(name):]
    return body[:body.index('\n}\n')]


def build_ref_files(d, rows):
    """Same layout as the approved REF_LOOKUP/REF_PAYLOAD: payload sorted bytewise by target, lookup -> offset/count."""
    rows = sorted(rows, key=lambda r: r[0].encode('utf-8'))
    head = '#LEXMACHINA|REF_PAYLOAD|1\n#TARGET_ID|TIPO|VISIBILIDADE|STATUS|REFERENCE_ID|SOURCE_ID|LABEL\n'
    data, look, off = head.encode('utf-8'), collections.OrderedDict(), len(head.encode('utf-8'))
    for r in rows:
        line = ('|'.join(r) + '\n').encode('utf-8')
        if r[0] not in look:
            look[r[0]] = [off, 0]
        look[r[0]][1] += 1
        data += line
        off += len(line)
    (d / 'REF_PAYLOAD.IDX').write_bytes(data)
    (d / 'REF_LOOKUP.IDX').write_text('#LEXMACHINA|REF_LOOKUP|1\n#TARGET_ID|OFFSET|QUANTIDADE\n' +
                                      ''.join(f'{k}|{o}|{n}\n' for k, (o, n) in look.items()), encoding='utf-8')


def exact_query(d, tid):
    """Mirror of lexV1CarregarRelacoesTarget on arbitrary REF files: exact lookup, then rows while key == tid."""
    ix = S.SortedIndex(d / 'REF_LOOKUP.IDX')
    try:
        row = ix.find(tid)
    finally:
        ix.close()
    out = collections.defaultdict(list)
    if not row:
        return out
    with open(d / 'REF_PAYLOAD.IDX', 'rb') as f:
        f.seek(int(row[1]))
        for _ in range(int(row[2])):
            p = f.readline().decode('utf-8').rstrip('\n').split('|')
            if p[0] != tid:
                break
            out[A.classify(p[1], p[2])].append(p[5])
    return out


class FixtureNoInheritanceTest(unittest.TestCase):
    """ART.X has J1, ART.X:INC.I has J2 -> ACTIVE_TARGET INC.I lists J2 only (never J1 + J2)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        j = lambda t, s: [t, 'JURISPRUDENCE', 'CURRENT_VISIBLE', 'CURRENT', f'JURISPRUDENCE:{s}@{t}', s, s]  # noqa: E731
        c = lambda t, s: [t, 'CORRELATA', 'CURRENT_VISIBLE', 'CURRENT', f'CORRELATA:{s}@{t}', s, s]  # noqa: E731
        build_ref_files(self.d, [j('CF88:ART.9', 'J1'), j('CF88:ART.9:INC.I', 'J2'), c('CF88:ART.9', 'C1'),
                                 j('CF88:ART.9:INC.II', 'J3'), j('CF88:ART.9:INC.III', 'J4')])

    def tearDown(self):
        self.tmp.cleanup()

    def test_inciso_gets_only_its_own(self):
        q = exact_query(self.d, 'CF88:ART.9:INC.I')
        self.assertEqual(q[JURIS], ['J2'])
        self.assertEqual(q[CORRELATA], [])                    # article correlata C1 is not inherited

    def test_article_gets_only_its_own(self):
        q = exact_query(self.d, 'CF88:ART.9')
        self.assertEqual((q[JURIS], q[CORRELATA]), (['J1'], ['C1']))   # no descendant aggregation

    def test_prefix_keys_do_not_leak(self):
        # "INC.I" is a byte prefix of "INC.II"/"INC.III": the key compare must be exact
        self.assertEqual(exact_query(self.d, 'CF88:ART.9:INC.II')[JURIS], ['J3'])
        self.assertEqual(exact_query(self.d, 'CF88:ART.9:INC.III')[JURIS], ['J4'])

    def test_target_without_records_fails_closed(self):
        q = exact_query(self.d, 'CF88:ART.9:INC.IV')       # parent has J1 and C1, the target has nothing
        self.assertEqual((q[JURIS], q[CORRELATA]), ([], []))


class ExportEqualsDeviceQueryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = A.audit()

    def test_432_links_grouped_by_target(self):
        self.assertEqual(self.r['total_links'], 432)
        self.assertEqual(self.r['per_layer'], {JURIS: 279, REFERENCIA: 101, CORRELATA: 44})
        self.assertEqual(self.r['hidden'], 8)
        self.assertEqual(len(self.r['derived']), 424)                  # 432 - 8 hidden
        self.assertEqual(len({(d['target_id'], d['reference_id']) for d in self.r['derived']}), 424)

    def test_zero_mismatches_per_layer(self):
        self.assertEqual(self.r['mismatches'], {CORRELATA: 0, JURIS: 0, REFERENCIA: 0}, self.r['mismatch_detail'])

    def test_flags_derive_from_exact_records(self):
        self.assertEqual(self.r['flag_mismatches'], [])

    def test_items_resolvable_by_id_in_legacy_indices(self):
        self.assertEqual(self.r['legacy_detail_unresolved'], {'jurisprudence': [], 'correlata': []})


class RealDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = S.Device(SD)

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def q(self, tid):
        return {k: [r[5] for r in v] for k, v in A.device_query(self.dev, tid).items()}

    def test_art5_table(self):
        exp = {  # TARGET: (CORRELATAS, JURISPRUDENCIA, REFERENCIAS) from the approved REF_PAYLOAD
            'CF88:ART.5': ([], [], []),
            'CF88:ART.5:CAPUT': ([], ['STF:RG:113'], ['REF-LIV-0006', 'REF-FIL-0004']),
            'CF88:ART.5:INC.IV': ([], [], ['REF-LIV-0001', 'REF-FIL-0006', 'REF-FIL-0002']),
            'CF88:ART.5:INC.V': ([], ['STF:RG:995'], []),
            'CF88:ART.5:INC.VI': ([], [], ['EXP-FIL-009']),
            'CF88:ART.5:INC.VIII': ([], ['STF:RG:1021', 'STF:RG:386'], ['EXP-FIL-009']),
            'CF88:ART.5:INC.IX': ([], [], ['REF-LIV-0001', 'REF-FIL-0006']),
            'CF88:ART.5:INC.XIV': ([], [], ['REF-SER-0003']),
            'CF88:ART.5:INC.XV': ([], [], ['REF-JOG-0001']),
            'CF88:ART.5:INC.XVI': ([], [], []),
            'CF88:ART.5:INC.XVII': ([], [], []),
        }
        for tid, (c, j, w) in exp.items():
            q = self.q(tid)
            self.assertEqual((q.get(CORRELATA, []), q.get(JURIS, []), q.get(REFERENCIA, [])), (c, j, w), tid)

    def test_v_and_vi_differ_because_the_data_differs(self):
        v, vi = self.q('CF88:ART.5:INC.V'), self.q('CF88:ART.5:INC.VI')
        self.assertNotEqual(v.get(JURIS, []), vi.get(JURIS, []))
        self.assertNotIn('STF:RG:113', v.get(JURIS, []))                  # caput thesis is not inherited
        self.assertNotIn('STF:RG:969', v.get(JURIS, []))                  # RG 969 is linked to II / XIII, not V

    def test_art37_par6_only_par6(self):
        j = self.q('CF88:ART.37:PAR.6').get(JURIS, [])
        self.assertEqual(sorted(j), sorted(['STF:RG:1031', 'STF:RG:130', 'STF:RG:362', 'STF:RG:365', 'STF:RG:940']))
        art37 = {r[5] for t in ('CF88:ART.37', 'CF88:ART.37:CAPUT', 'CF88:ART.37:INC.XI', 'CF88:ART.37:INC.II')
                 for r in A.device_query(self.dev, t)[JURIS]}
        self.assertEqual(art37 & set(j), set())

    def test_papers_please_and_timbuktu_only_layer4(self):
        self.assertEqual(self.q('CF88:ART.5:INC.XV'), {REFERENCIA: ['REF-JOG-0001']})
        for t in ('CF88:ART.5:INC.XIV', 'CF88:ART.5:INC.XVI'):
            self.assertNotIn('REF-JOG-0001', sum(self.q(t).values(), []))
        for t in ('CF88:ART.5:INC.VI', 'CF88:ART.5:INC.VIII'):
            q = self.q(t)
            self.assertIn('EXP-FIL-009', q[REFERENCIA])
            self.assertNotIn('EXP-FIL-009', q.get(JURIS, []) + q.get(CORRELATA, []))

    def test_target_without_juris_hides_2_even_if_article_has_many(self):
        t = dict((p[0], p[3]) for p in A.rows(SD / '10_TARGETS/CF88_TARGETS.IDX'))
        art5_juris = sum(1 for p in A.rows(SD / '20_REFERENCES/REF_PAYLOAD.IDX')
                         if p[0].startswith('CF88:ART.5:') and A.classify(p[1], p[2]) == JURIS)
        self.assertGreater(art5_juris, 20)
        for tid in ('CF88:ART.5:INC.VI', 'CF88:ART.5:INC.XV', 'CF88:ART.5:INC.XVI'):   # caput: test_caput_equivalence
            self.assertFalse(A.flag(t[tid], JURIS), tid)                     # 2 JURIS. hidden, key 2 ignored
            self.assertFalse(A.flag(t[tid], CORRELATA), tid)                 # 1 CORR. hidden, key 1 ignored
            self.assertEqual(self.q(tid).get(JURIS, []), [])

    @unittest.skipUnless(A.LEGACY.is_dir(), 'legacy SD backup is local only')
    def test_why_the_old_list_was_identical(self):
        # legacy per-article sources: art. 5 article key = RG 113/969/995; V/VI/XV have no inciso key -> ARTICLE fallback
        self.assertEqual(A.legacy_juris_list('5')[1], ['STF:RG:113', 'STF:RG:969', 'STF:RG:995'])
        for inc in ('V', 'VI', 'XV'):
            k, ids = A.legacy_juris_list('5', inc=inc)
            self.assertEqual((k, ids), (('CF88', '5', '', '', ''), ['STF:RG:113', 'STF:RG:969', 'STF:RG:995']), inc)
        self.assertEqual(A.legacy_juris_list('5', inc='VIII')[1], ['STF:RG:1021', 'STF:RG:386'])
        # correlatas: art. 5 has only the XLIII key (Lei 13.260/2016); no article key
        self.assertEqual(A.legacy_correlata_list('5'), (None, []))
        self.assertEqual(A.legacy_correlata_list('5', inc='XLIII')[1], ['EXT_LEI13260_2016'])


class FirmwareSourceContractTest(unittest.TestCase):
    def test_exact_loader(self):
        body = func('static bool lexV1CarregarRelacoesTarget(const char *tid)')
        rd = func('static bool lexV1LerRegistrosChave(')
        self.assertIn('st=lexv1Find(refLookup,chave,linha,sizeof(linha),false);', rd)        # exact, never floor
        self.assertIn('if(lexv1ReadLine(rp,linha,sizeof(linha))<0 || lexv1KeyCmp(linha,chave)!=0) break;', rd)
        self.assertIn('int nChaves=lexV1QueryKeysForActiveTarget(tid,chaves);', body)
        self.assertIn('ioOk=lexV1LerRegistrosChave(refLookup,rp,chaves[c],st,', body)
        self.assertIn('LexV1DestinoCamada dst=lexV1ClassificarDestino(tipo,vis);', body)
        self.assertIn('if(dst!=LEXV1_LAYER_CORRELATA && dst!=LEXV1_LAYER_JURISPRUDENCIA){ foraDe12++; return; }', body)
        self.assertIn('if(regs[i].dst==LEXV1_LAYER_CORRELATA) ok=lexV1AdicionarCorrelataPorId(', body)
        self.assertIn('rp.fechar(); rl.fechar();', body)
        for forbidden in ('carregarRelacoesDoArtigo', 'buscarMelhorLookup', 'JUR_LOOKUP', 'REL_LOOKUP.IDX', 'floor=true',
                          'lexv1Find(refLookup,chave'):
            self.assertNotIn(forbidden, body, forbidden)

    def test_v1_never_loads_by_article(self):
        sync = func('void lexV1SincronizarRelacoes()\n{')
        self.assertNotIn('carregarRelacoesDoArtigo', sync)
        self.assertNotIn('lexV1ChaveArtigo', sync)
        self.assertNotIn('lexV1ArtRelacoes', INO)
        # flag 0 (v7.12.0) path untouched: legacy load only when !v1
        self.assertIn('if(!visualizandoReferencia && novo.artigo[0] && !v1){', INO)
        self.assertIn('    carregarRelacoesDoArtigo(String(novo.artigo));', INO)

    def test_keys_1_2_use_layer_target(self):
        num = func('void lexV1AbrirCamadaNumero(char tecla)\n{')
        self.assertIn('if(v1cf) lexV1AbrirRelacaoTarget(true,alvo); ', num)
        self.assertIn('if(v1cf) lexV1AbrirRelacaoTarget(false,alvo);', num)
        op = func('static void lexV1AbrirRelacaoTarget(bool corr, const char *tid)')
        self.assertIn('if(corr?!lexV1Disp.correlatas:!lexV1Disp.juris) return;', op)          # unavailable: ignored
        self.assertIn('if(!lexV1CarregarRelacoesTarget(tid)) return;', op)
        self.assertIn('abrirCategoriaRelacao(corr?REL_CORRELATAS:REL_JURIS_TODAS);', op)
        self.assertLess(op.index('lexV1CarregarRelacoesTarget(tid)'), op.index('abrirCategoriaRelacao('))

    def test_footer_mask_from_exact_flags(self):
        m = func('uint8_t lexV1MascaraCamadas()\n{')
        self.assertIn('if(lexV1Disp.correlatas) m|=1;', m)
        self.assertIn('if(lexV1Disp.juris) m|=2;', m)
        v1 = m[m.index('if(lexV1Disp.valido && lexV1Alvo.valido && !strcmp(lexV1Disp.tid,lexV1Alvo.tid)){'):]
        self.assertNotIn('totalCorrelatasArtigo', v1)
        self.assertNotIn('totalCategoriasJuris', v1)
        d = func('bool lexV1AtualizarDisponibilidade(bool forcar)\n{')
        self.assertIn('lexV1Disp.correlatas|=lexV1FlagCamada(t.flags,LEXV1_LAYER_CORRELATA);', d)
        self.assertIn('lexV1Disp.juris|=lexV1FlagCamada(t.flags,LEXV1_LAYER_JURISPRUDENCIA);', d)

    def test_legacy_caches_preserved(self):
        for s in ('bool carregarCacheJurisCF()', 'bool carregarCacheRelationsV2()', 'JUR CACHE: lookups=%d registros=%d',
                  'CAMINHO_JURISPRUDENCIA_CF', 'CAMINHO_RELACOES_V2'):
            self.assertIn(s, INO)
        body = func('static bool lexV1CarregarRelacoesTarget(const char *tid)')
        self.assertNotIn('heap_caps_free', body)
        self.assertNotIn('free(jurisprudenciaCFCache', INO[INO.index('static char lexV1RelTid'):])


if __name__ == '__main__':
    unittest.main()
