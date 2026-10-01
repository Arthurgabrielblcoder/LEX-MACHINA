"""LAYER ROUTING (uncommitted until the human test): each visible link goes to ONE visual layer.

Physical bug (video): at CF88:ART.5:INC.V, key 4 (REFERENCIAS) listed "Tema de Repercussao Geral 995 / JURISPRUDENCIA",
which also appears in 2 (JURISPRUDENCIA). Root cause: the generic Reference Engine payload (REF_PAYLOAD) holds CORRELATA,
JURISPRUDENCE and WORK_REFERENCE rows; the footer turned 4 REF. on with flags C||J||W and the list took every CURRENT_VISIBLE
row regardless of type. Fix: one classifier (lexV1ClassificarDestino / lexV1FlagCamada) used by footer, count, list and detail;
layer 4 receives only WORK_REFERENCE. Layers 1/2 now use the same exact-target records (see test_canonical_layers.py).
"""
import collections
import re
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(DI / 'tests'))
import device_lookup_simulator as S  # noqa: E402
from test_a3b_prep import INO, SD  # noqa: E402

LEGACY = DI / 'backups/sd_20260929T163407Z/data'
EXPORT = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run1'
HDR = (ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h').read_text(encoding='utf-8')

CORRELATA, JURIS, REFERENCIA, HIDDEN, UNKNOWN = 'CORRELATA', 'JURISPRUDENCIA', 'REFERENCIA', 'HIDDEN', 'UNKNOWN'


def classify(tipo, vis):                        # mirror of lexV1ClassificarDestino
    if vis != 'CURRENT_VISIBLE':
        return HIDDEN
    return {'CORRELATA': CORRELATA, 'JURISPRUDENCE': JURIS, 'WORK_REFERENCE': REFERENCIA}.get(tipo, UNKNOWN)


def flag(flags, layer):                         # mirror of lexV1FlagCamada
    return len(flags) >= 4 and {CORRELATA: flags[1] == 'C', JURIS: flags[2] == 'J', REFERENCIA: flags[3] == 'W'}.get(layer, False)


def func(name):
    body = INO[INO.index(name):]
    return body[:body.index('\n}\n')]


def payload(path=SD / '20_REFERENCES/REF_PAYLOAD.IDX'):
    return [l.split('|') for l in path.read_text(encoding='utf-8').splitlines() if l and l[0] != '#']


def targets():
    return {p[0]: p[3] for p in (l.split('|') for l in (SD / '10_TARGETS/CF88_TARGETS.IDX').read_text(encoding='utf-8').splitlines()
                                  if l and l[0] != '#')}


def layer4_list(dev, tid):
    """Mirror of lexV1CarregarItensRef: only records routed to REFERENCIA; notes from the approved header (TARGET|WORK)."""
    out = []
    for r in dev.references(tid):
        if classify(r[1], r[2]) != REFERENCIA:
            continue
        m = re.search(r'\{"' + re.escape(f'{tid}|{r[5]}') + r'", "([^"]*)", "([^"]*)", (\d+), (-?\d+),', HDR)
        out.append(dict(fonte=r[5], rotulo=r[6], tipo=r[1], titulo=m and m.group(1), obra=m and m.group(2),
                        ano=m and int(m.group(3)), nota10=m and int(m.group(4))))
    return sorted(out, key=lambda x: -(x['nota10'] if x['nota10'] is not None else -1))


def legacy_juris(article):
    """Layer 2 source on the device (article level): JURISPRUDENCIA.IDX ids 'STF:RG:995:CF88:5:-:-:-'."""
    ids = []
    for l in (LEGACY / '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX').read_text(encoding='utf-8').splitlines():
        p = l.split('|')
        if len(p) > 6 and re.match(rf'^[A-Z]+:[A-Z]+:\d+:CF88:{re.escape(article)}:', p[0]):
            ids.append(p[6])
    return ids


class LayerRoutingAuditTest(unittest.TestCase):
    """Routing audit of the 432 exported/runtime links (no semantic audit)."""

    def test_routing_counts_and_no_duplicates(self):
        rows = payload()
        self.assertEqual(rows, payload(EXPORT / 'REF_PAYLOAD.IDX'))       # runtime == approved export
        dest = collections.Counter(classify(r[1], r[2]) for r in rows)
        self.assertEqual(len(rows), 432)
        self.assertEqual(dest, {JURIS: 279, REFERENCIA: 101, CORRELATA: 44, HIDDEN: 8})
        self.assertEqual(dest[UNKNOWN], 0)
        by = collections.defaultdict(set)
        for r in rows:
            by[classify(r[1], r[2])].add(r[4])                              # reference_id (unique per link)
        self.assertEqual(len({r[4] for r in rows}), 432)
        for a, b in ((CORRELATA, JURIS), (CORRELATA, REFERENCIA), (JURIS, REFERENCIA)):
            self.assertEqual(by[a] & by[b], set(), (a, b))
        # before the fix layer 4 took every visible row: 44 correlatas + 279 jurisprudence were duplicated into 4
        old4 = {r[4] for r in rows if r[2] == 'CURRENT_VISIBLE'}
        self.assertEqual((len(old4 & by[CORRELATA]), len(old4 & by[JURIS])), (44, 279))

    def test_flags_use_the_same_taxonomy(self):
        vis = collections.defaultdict(set)
        for r in payload():
            vis[r[0]].add(classify(r[1], r[2]))
        for tid, f in targets().items():
            for layer in (CORRELATA, JURIS, REFERENCIA):
                self.assertEqual(flag(f, layer), layer in vis[tid], (tid, layer))
        t = targets()
        old = sum(1 for f in t.values() if f[1] == 'C' or f[2] == 'J' or f[3] == 'W')
        new = sum(1 for f in t.values() if flag(f, REFERENCIA))
        self.assertEqual((old, new), (238, 43))                            # 195 targets showed 4 REF. without any work


class LayerRoutingCasesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = S.Device(SD)
        cls.t = targets()

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def test_rg995_layer2_not_layer4(self):
        tid = 'CF88:ART.5:INC.V'
        rows = [r for r in self.dev.references(tid) if r[5] == 'STF:RG:995']
        self.assertEqual(len(rows), 1)
        self.assertEqual(classify(rows[0][1], rows[0][2]), JURIS)
        self.assertEqual(layer4_list(self.dev, tid), [])                   # nothing in 4
        self.assertFalse(flag(self.t[tid], REFERENCIA))                    # 4 REF. hidden, key 4 ignored
        self.assertTrue(flag(self.t[tid], JURIS))
        for other in self.t:                                               # RG 995 never in any layer-4 list
            self.assertNotIn('STF:RG:995', [x['fonte'] for x in layer4_list(self.dev, other)] if flag(self.t[other], REFERENCIA) else [])

    @unittest.skipUnless(LEGACY.is_dir(), 'legacy SD backup is local only')
    def test_rg995_in_legacy_article_list(self):
        ids = legacy_juris('5')                                   # legacy per-article list (no longer the V1 source)
        for rg in ('STF:RG:113', 'STF:RG:969', 'STF:RG:995'):     # the video's "989" is 969: 989 is in no device index
            self.assertIn(rg, ids)
        self.assertNotIn('STF:RG:989', ids)

    def test_timbuktu_layer4(self):
        for tid, nota in (('CF88:ART.5:INC.VI', 88), ('CF88:ART.5:INC.VIII', 90)):
            self.assertTrue(flag(self.t[tid], REFERENCIA))
            items = layer4_list(self.dev, tid)
            tb = [x for x in items if x['fonte'] == 'EXP-FIL-009']
            self.assertEqual(len(tb), 1, tid)
            self.assertEqual((tb[0]['titulo'], tb[0]['obra'], tb[0]['ano'], tb[0]['nota10']), ('Timbuktu', 'FILME', 2014, nota))
            self.assertTrue(all(classify(x['tipo'], 'CURRENT_VISIBLE') == REFERENCIA for x in items))
        rows = [r for r in payload() if r[5] == 'EXP-FIL-009']
        self.assertTrue(rows and all(classify(r[1], r[2]) == REFERENCIA for r in rows))   # never layer 2

    def test_real_correlata_layer1_only(self):
        rows = [r for r in payload() if r[4] == 'CORRELATA:REL_DD3B2F9749F1A8A7@CF88:ART.5:INC.XLIII']
        self.assertEqual(len(rows), 1)
        self.assertEqual(classify(rows[0][1], rows[0][2]), CORRELATA)
        self.assertNotIn('REL_DD3B2F9749F1A8A7', [x['fonte'] for x in layer4_list(self.dev, 'CF88:ART.5:INC.XLIII')])

    def test_footer_combinations(self):
        f = self.t
        juris_only = [t for t in f if flag(f[t], JURIS) and not flag(f[t], REFERENCIA)]
        work_only = [t for t in f if flag(f[t], REFERENCIA) and not flag(f[t], JURIS)]
        both = [t for t in f if flag(f[t], REFERENCIA) and flag(f[t], JURIS)]
        self.assertIn('CF88:ART.5:INC.V', juris_only)
        self.assertIn('CF88:ART.5:INC.VI', work_only)
        self.assertTrue(juris_only and work_only and both)
        for tid in both:                                                   # both: distinct lists
            l4 = {x['fonte'] for x in layer4_list(self.dev, tid)}
            j = {r[5] for r in self.dev.references(tid) if classify(r[1], r[2]) == JURIS}
            self.assertTrue(l4 and j and not (l4 & j), tid)
        for tid in f:                                                      # every layer-4 item is a work
            if flag(f[tid], REFERENCIA):
                self.assertTrue(all(classify(x['tipo'], 'CURRENT_VISIBLE') == REFERENCIA for x in layer4_list(self.dev, tid)))


class LayerRoutingFirmwareSourceTest(unittest.TestCase):
    def test_central_classifier(self):
        cls = func('LexV1DestinoCamada lexV1ClassificarDestino(const char *tipo, const char *visibilidade)\n{')
        for s in ('if(!visibilidade || strcmp(visibilidade,"CURRENT_VISIBLE")!=0) return LEXV1_LAYER_HIDDEN;',
                  'if(!strcmp(tipo,"CORRELATA")) return LEXV1_LAYER_CORRELATA;',
                  'if(!strcmp(tipo,"JURISPRUDENCE")) return LEXV1_LAYER_JURISPRUDENCIA;',
                  'if(!strcmp(tipo,"WORK_REFERENCE")) return LEXV1_LAYER_REFERENCIA;',
                  'return LEXV1_LAYER_UNKNOWN;'):
            self.assertIn(s, cls)
        fl = func('bool lexV1FlagCamada(const char *flags, LexV1DestinoCamada camada)\n{')
        self.assertIn("case LEXV1_LAYER_REFERENCIA:     return flags[3]=='W';", fl)

    def test_footer_list_detail_use_the_classifier(self):
        self.assertIn('lexV1Disp.refs|=lexV1FlagCamada(t.flags,LEXV1_LAYER_REFERENCIA);', func('bool lexV1AtualizarDisponibilidade(bool forcar)\n{'))
        self.assertNotIn("t.flags[1]=='C' || t.flags[2]=='J'", INO)
        load = func('static int lexV1CarregarItensRef(const char *tid)\n{')
        self.assertIn('LexV1DestinoCamada dst=lexV1ClassificarDestino(tipo,vis);', load)
        self.assertIn('if(dst!=LEXV1_LAYER_REFERENCIA){ outros++; return; }', load)
        self.assertIn('UNKNOWN_LAYER_TYPE', load)
        self.assertNotIn('if(strcmp(f,"CURRENT_VISIBLE")!=0) continue;', load)
        self.assertIn('LAYER_ROUTING_ERROR', func('static void lexV1MontarListaRef()\n{'))
        self.assertIn('LAYER_ROUTING_ERROR', func('void lexV1AbrirItemRef()\n{'))
        # rich detail preserved; keyed by TARGET|WORK; ACTIVE_TARGET flow untouched
        det = func('static void lexV1MontarDetalheRef(const LexV1RefItem &it)\n{')
        for s in ('"Nota de indicação: "', '"SOBRE"', '"POR QUE ESTÁ AQUI"', '"ALCANCE NESTE DISPOSITIVO"'):
            self.assertIn(s, det)
        self.assertIn("if(v1cf) lexV1AbrirCamada('R',alvo);", INO)


if __name__ == '__main__':
    unittest.main()
