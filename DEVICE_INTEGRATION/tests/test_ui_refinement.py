"""UI refinement after the physical video test (uncommitted until the human test):
DYNAMIC_LAYER_FOOTER, ENTENDA_TYPOGRAPHY_FIX, ENTENDA_SMOOTH_SCROLL, REFERENCE_RICH_DETAIL.
"""
import re
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(DI / 'tests'))
import build_ref_detail_header as RD  # noqa: E402
import device_lookup_simulator as S  # noqa: E402
from test_a3b_prep import INO, SD  # noqa: E402

LEGACY = DI / 'backups/sd_20260929T163407Z/data'
UI = INO[INO.index('// DEVICE V1 - PHYSICAL TEST UI'):INO.index('// ---------------- teclado numerico: estados do leitor')]


def v1_mask(dev, tid):
    """Mirror of lexV1AtualizarDisponibilidade + lexV1MascaraCamadas bits 3/4 (TARGETS flags come only from visible rows)."""
    row = dev.targets.find(tid)
    if not row:
        return 0
    f = row[3]
    return (4 if f[0] in 'EB' else 0) | (8 if f[3] == 'W' else 0)   # 4 REF. = editorial works only (layer routing fix)


def legacy_articles(path):
    arts = set()
    if path.is_file():
        for l in path.read_text(encoding='utf-8').splitlines():
            if l and not l.startswith('#'):
                p = l.split('|')
                if p[0] == 'CF88':
                    arts.add(p[1])
    return arts


class DynamicFooterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = S.Device(SD)

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def test_required_cases(self):
        m = lambda t: v1_mask(self.dev, t)            # noqa: E731
        self.assertEqual(m('CF88:ART.5:INC.V'), 4)                # BLOCK; only jurisprudence (RG 995) -> no 4 REF.
        self.assertEqual(m('CF88:ART.37:PAR.6'), 4)               # DIRECT; 5 jurisprudence rows -> layer 2, not 4
        self.assertEqual(len(self.dev.references('CF88:ART.37:PAR.6')), 5)
        self.assertEqual(m('CF88:ART.25'), 0)                     # no ENTENDA, only jurisprudence -> neither 3 nor 4
        self.assertEqual(m('CF88:ART.5:INC.VI'), 4 | 8)           # Timbuktu (work) -> 4 REF.
        self.assertEqual(m('CF88:ART.21:INC.XXIV'), 4)            # ENTENDA only
        self.assertEqual(m('CF88:ART.114:INC.VIII'), 0)           # only hidden historical refs -> nothing
        self.assertEqual(m('CF88:ART.999'), 0)                    # invalid target

    def test_real_targets_per_combination(self):
        rows = [l.split('|') for l in (SD / '10_TARGETS/CF88_TARGETS.IDX').read_text(encoding='utf-8').splitlines() if l and l[0] != '#']
        by = {}
        for r in rows:
            by.setdefault(v1_mask(self.dev, r[0]), []).append(r[0])
        for mask in (0, 4, 8, 12):                                  # none / ENTENDA only / refs only / both
            self.assertTrue(by.get(mask), mask)
        # 4 REF. agrees with the visible WORK_REFERENCE rows of the payload (hidden rows and jurisprudence never count)
        for tid in ('CF88:ART.114:INC.VIII', 'CF88:ART.25', 'CF88:ART.37:PAR.6', 'CF88:ART.5:INC.VI'):
            vis = sum(r[2] == 'CURRENT_VISIBLE' and r[1] == 'WORK_REFERENCE' for r in self.dev.references(tid))
            self.assertEqual(bool(v1_mask(self.dev, tid) & 8), vis > 0, tid)

    @unittest.skipUnless(LEGACY.is_dir(), 'legacy SD backup is local only')
    def test_full_mask_with_legacy_layers(self):
        corr = legacy_articles(LEGACY / '99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX')
        juris = legacy_articles(LEGACY / '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX')
        def full(tid):
            art = tid.split(':')[1][4:]
            return (1 if art in corr else 0) | (2 if art in juris else 0) | v1_mask(self.dev, tid)
        self.assertEqual(full('CF88:ART.5:INC.V'), 7)            # 1 + 2 + 3; no work -> no 4
        self.assertEqual(full('CF88:ART.5:INC.VI'), 15)          # all four layers (Timbuktu)
        self.assertEqual(full('CF88:ART.25') & 12, 0)
        rows = [l.split('|')[0] for l in (SD / '10_TARGETS/CF88_TARGETS.IDX').read_text(encoding='utf-8').splitlines() if l and l[0] != '#']
        masks = {full(t) for t in rows if t.startswith('CF88:ART.')}
        self.assertIn(15, masks)
        self.assertIn(0, masks)                                  # a real CF target with no layer at all -> footer without 1-4
        self.assertTrue(any(m & 2 and not m & 12 for m in masks))  # only jurisprudence

    def test_firmware_footer_and_keys(self):
        for s in ('if(m&1) s+="1 CORR.  ";', 'if(m&2) s+="2 JURIS.  ";', 'if(m&4) s+="3 ENTENDA  ";', 'if(m&8) s+="4 REF.";',
                  'tft.print("ENTER=BUSCAR");',
                  "lexV1Disp.entenda=(t.flags[0]=='E' || t.flags[0]=='B');",
                  "lexV1Disp.refs|=lexV1FlagCamada(t.flags,LEXV1_LAYER_REFERENCIA);",
                  'if(lexV1Alvo.valido && off>=lexV1Alvo.ini && off<lexV1Alvo.fim) return;',          # target per TEXT_MAP record
                  'if(lexV1Disp.valido && !strcmp(lexV1Disp.tid,lexV1Alvo.tid)) return false;',       # availability per target
                  'if(!forcar && (uint32_t)(millis()-lexV1UltimoScrollMs)<250) return false;',       # no I/O while scrolling
                  "if((tipo=='E' && !lexV1Disp.entenda) || (tipo=='R' && !lexV1Disp.refs)) return;",  # unavailable key ignored
                  'if(lexV1AtualizarDisponibilidade(false)) desenharBarraBusca();'):
            self.assertIn(s, INO, s)
        self.assertNotIn('Explicação ainda não disponível', INO)
        self.assertNotIn('SEM LEGISLAÇÃO CORRELATA NESTE PONTO', INO)
        self.assertNotIn('"1 CORR. 2 JURIS. 3 ENTENDA 4 REF.  ENTER=BUSCAR"', INO)
        num = INO[INO.index('void lexV1AbrirCamadaNumero(char tecla)\n{'):]
        num = num[:num.index('\n}\n')]
        self.assertIn('if(totalCorrelatasArtigo>0) abrirCategoriaRelacao(REL_CORRELATAS);\n      break;', num)
        self.assertIn('if(totalCategoriasJuris>0){', num)


class TypographyAndScrollTest(unittest.TestCase):
    def test_same_renderer_as_dry_law(self):
        # body text: Arimo glyphs into bufferLinhaLeitor, LEITOR_TEXTO_W wrap by real glyph advance, TEXTO_Y0/TEXTO_H viewport
        self.assertIn('desenharGlyphArimoNoBuffer(x,cp,invertido);', UI)
        self.assertIn('int av=avancoGlyphArimo(cp);', UI)
        self.assertIn('tft.drawRGBBitmap(4,y,bufferLinhaLeitor,LEITOR_BUFFER_W,TEXTO_H);', UI)
        self.assertIn('for(int i=0;i<LEITOR_LINHAS_VISIVEIS;i++) lexV1DesenharLinhaViewport(i);', UI)
        self.assertNotIn('LEXV1_CAMADA_COLS', UI)                                    # no more 6-px fixed-column body

    def test_scroll_without_clearing(self):
        rolar = UI[UI.index('void lexV1RolarCamada(int delta)\n{'):]
        rolar = rolar[:rolar.index('\n}\n')]
        self.assertNotIn('fillScreen', rolar)
        self.assertNotIn('lexV1DesenharCamada()', rolar)                            # header/footer not redrawn per step
        self.assertIn('lexV1DesenharViewportCamada();', rolar)
        body = UI[UI.index('void lexV1DesenharCamada()\n{'):]
        self.assertEqual(body[:body.index('\n}\n')].count('fillScreen'), 1)        # only when a screen is opened
        viewport = UI[UI.index('static void lexV1DesenharLinhaViewport(int i)\n{'):]
        self.assertNotIn('fill', viewport[:viewport.index('\n}\n')].replace('bufferLinhaLeitor[k]=COR_FUNDO', ''))
        # the dry-law wheel granularity: one line per wheel tick; PageUp/PageDown move a page
        self.assertIn('if(event.usage==0x4B){deltaCamadaV1-=LEXV1_CAMADA_VISIVEIS-1; return;}', INO)


class ReferenceRichDetailTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.txt, cls.recs, cls.inc = RD.render()
        cls.by = {r['key']: r for r in cls.recs}

    def test_header_up_to_date_and_counts(self):
        hdr = (ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h').read_text(encoding='utf-8')
        self.assertEqual(hdr, self.txt)                                             # deterministic, regenerated from approved data
        self.assertEqual(len(self.recs), 101)
        self.assertEqual(self.inc, {'tipo': 0, 'ano': 0, 'nota': 18, 'sobre': 0, 'por_que': 0, 'temas': 101})
        self.assertEqual([r['key'] for r in self.recs], sorted((r['key'] for r in self.recs), key=lambda k: k.encode('utf-8')))

    def test_timbuktu(self):
        r = self.by['CF88:ART.5:INC.VI|EXP-FIL-009']
        self.assertEqual((r['titulo'], r['tipo'], r['ano'], r['nota']), ('Timbuktu', 'FILME', 2014, 88))   # nota of THIS link
        self.assertEqual(self.by['CF88:ART.5:INC.VIII|EXP-FIL-009']['nota'], 90)                          # same work, other link
        self.assertTrue(r['sobre'])
        self.assertIn('liberdade de crença e de prática religiosa', r['por_que'])                          # specific to 5.VI
        self.assertEqual(r['relacao'], 'Ilustração de violação')

    def test_every_payload_work_row_has_detail(self):
        rows = [l.split('|') for l in (SD / '20_REFERENCES/REF_PAYLOAD.IDX').read_text(encoding='utf-8').splitlines() if l and l[0] != '#']
        work = [(r[0], r[5]) for r in rows if r[1] == 'WORK_REFERENCE' and r[2] == 'CURRENT_VISIBLE']
        self.assertEqual({f'{t}|{w}' for t, w in work}, set(self.by))
        for r in self.recs:
            self.assertTrue(r['por_que'].strip() and r['titulo'] and r['tipo'] and r['ano'], r['key'])

    def test_firmware_detail_and_list(self):
        for s in ('"Nota de indicação: "+lexV1Nota(it.nota10)', 'lexV1Anexar("SOBRE",-1,1);', 'lexV1Anexar("POR QUE ESTÁ AQUI",-1,1);',
                  'while(j>=0 && lexV1Itens[j].nota10<x.nota10)',                   # stable sort, highest nota first
                  'return String(nota10/10)+","+String(nota10%10);',                # PT-BR decimal comma
                  'if(lexV1RefModo==2 && lexV1Itens){ lexV1VoltarParaListaRef(); return; }',   # BACK: detail -> list -> text
                  'if(event.usage==0x28){pedirAbrirItemV1=true; return;}',
                  'String fo=String("Fonte: ")+(d?d->fonte:it.fonte);'):
            self.assertIn(s, INO, s)
        self.assertNotIn('"REFERÊNCIA DE OBRA"', INO)                              # real work type shown instead
        self.assertNotIn('TEMAS', UI)                                              # no invented themes (no approved field)


if __name__ == '__main__':
    unittest.main()
