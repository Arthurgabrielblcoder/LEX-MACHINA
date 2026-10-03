"""Physical keyboard state machine of the DEVICE V1 reader (uncommitted until the human test).

Human decision: in the dry law text 1 = CORRELATAS, 2 = JURISPRUDENCIA, 3 = ENTENDA, 4 = REFERENCIAS; article search starts ONLY
with ENTER (ENTER -> digits -> ENTER). States: NORMAL_READING_MODE, ARTICLE_SEARCH_MODE, LAYER_VIEW_MODE.

`Reader` below is the reference model of the firmware rules; the source tests pin that the firmware encodes the same rules, and
the search tests replay pesquisarArtigo's matcher on CF88_RUNTIME.txt and resolve the landing line through the TEXT_MAP.
"""
import re
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(DI / 'tests'))
import device_lookup_simulator as S  # noqa: E402
from test_a3b_prep import INO, SD  # noqa: E402

RT = (SD / '05_TEXT/CF88_RUNTIME.txt').read_bytes()
ENTER, BACKSPACE, ESC = 'ENTER', 'BACKSPACE', 'ESC'


def find_article(num):
    """Mirror of pesquisarArtigo/correspondeArtigoNoInicioLinhaRapido: first line starting with Art[.] <num> not followed by a digit."""
    for m in re.finditer(rb'(?m)^[Aa][Rr][Tt]\.?[ \t]*' + num.encode() + rb'(?![0-9]|\.[0-9])', RT):
        return m.start()
    return None


class Reader:
    NORMAL, SEARCH, LAYER = 'NORMAL_READING_MODE', 'ARTICLE_SEARCH_MODE', 'LAYER_VIEW_MODE'

    def __init__(self, offset=0):
        self.state, self.buffer, self.offset, self.layer, self.origin, self.messages = self.NORMAL, '', offset, None, None, []

    def key(self, k):
        if self.state == self.LAYER:
            if k in (BACKSPACE, ESC):
                self.state, self.layer = self.NORMAL, None                    # back to the same point
            return                                                            # digits / ENTER do nothing in a layer
        if self.state == self.SEARCH:
            if k.isdigit():
                if len(self.buffer) < 8:
                    self.buffer += k
            elif k == BACKSPACE:
                if self.buffer:
                    self.buffer = self.buffer[:-1]
                else:
                    self.state, self.offset = self.NORMAL, self.origin        # cancel: same file, same offset
            elif k == ESC:
                self.state, self.buffer, self.offset = self.NORMAL, '', self.origin
            elif k == ENTER and self.buffer:
                off = find_article(self.buffer)
                if off is None:
                    self.messages.append('NAO ENCONTRADO')                    # stays in the search with the number
                else:
                    self.state, self.buffer, self.offset = self.NORMAL, '', off
            return
        # NORMAL_READING_MODE
        if k == ENTER:
            self.state, self.buffer, self.origin = self.SEARCH, '', self.offset
        elif k in '1234' and len(k) == 1:
            self.state, self.layer = self.LAYER, {'1': 'CORRELATAS', '2': 'JURISPRUDENCIA', '3': 'ENTENDA', '4': 'REFERENCIAS'}[k]
        # 5-9, 0 and BACKSPACE: no action; never starts a search

    def keys(self, *ks):
        for k in ks:
            self.key(k)
        return self


class StateMachineModelTest(unittest.TestCase):
    ART5 = find_article('5')

    def search(self, *digits):
        r = Reader(self.ART5).keys(ENTER, *digits, ENTER)
        self.assertEqual((r.state, r.layer, r.buffer), (Reader.NORMAL, None, ''))
        return r.offset

    def test_searches_land_on_the_article(self):
        dev = S.Device(SD)
        try:
            size, sha = dev.verify_runtime_file()
            for num in ('3', '4', '21', '24', '37', '60', '114', '225'):
                off = self.search(*num)
                self.assertEqual(off, find_article(num))
                self.assertTrue(RT[off:off + 20].decode('utf-8', 'replace').startswith(f'Art. {num}'), num)
                r = dev.resolve_text_position(off, size, sha)                  # TEXT_MAP -> current target after the jump
                self.assertEqual((r['status'], r['target_id']), ('OK', f'CF88:ART.{num}'), num)
        finally:
            dev.close()

    def test_digits_never_open_layers_in_search(self):
        r = Reader(self.ART5).keys(ENTER, '3')
        self.assertEqual((r.state, r.layer, r.buffer), (Reader.SEARCH, None, '3'))       # 3 is a digit, not ENTENDA
        r.keys('7')
        self.assertEqual(r.buffer, '37')
        for d in '1234':
            self.assertIsNone(Reader(self.ART5).keys(ENTER, d).layer)

    def test_normal_mode_numbers(self):
        for k, layer in (('1', 'CORRELATAS'), ('2', 'JURISPRUDENCIA'), ('3', 'ENTENDA'), ('4', 'REFERENCIAS')):
            r = Reader(self.ART5).keys(k)
            self.assertEqual((r.state, r.layer), (Reader.LAYER, layer))
        for k in '567890':
            r = Reader(self.ART5).keys(k)
            self.assertEqual((r.state, r.layer, r.buffer, r.offset), (Reader.NORMAL, None, '', self.ART5))   # no search started

    def test_backspace_edits_then_cancels_to_same_point(self):
        r = Reader(self.ART5).keys(ENTER, '1', '1', '4')
        self.assertEqual(r.buffer, '114')
        for expected in ('11', '1', ''):
            r.key(BACKSPACE)
            self.assertEqual((r.state, r.buffer), (Reader.SEARCH, expected))              # still searching when empty
        r.key(BACKSPACE)
        self.assertEqual((r.state, r.offset, r.layer), (Reader.NORMAL, self.ART5, None))  # same file / same offset

    def test_empty_enter_and_not_found(self):
        r = Reader(self.ART5).keys(ENTER, ENTER)
        self.assertEqual((r.state, r.offset), (Reader.SEARCH, self.ART5))
        r = Reader(self.ART5).keys(ENTER, '9', '9', '9', ENTER)
        self.assertEqual((r.state, r.buffer, r.messages), (Reader.SEARCH, '999', ['NAO ENCONTRADO']))

    def test_layers_block_numbers_and_enter(self):
        r = Reader(self.ART5).keys('3', '4', '1', ENTER, '7')
        self.assertEqual((r.state, r.layer), (Reader.LAYER, 'ENTENDA'))
        r.key(BACKSPACE)
        self.assertEqual((r.state, r.offset), (Reader.NORMAL, self.ART5))

    def test_forbidden_sequence(self):
        # "wants art. 37, presses 3 and ENTENDA opens" can only happen WITHOUT ENTER first, which is the defined meaning of 3
        r = Reader(self.ART5).keys(ENTER, '3', '7', ENTER)
        self.assertIsNone(r.layer)
        self.assertEqual(r.offset, find_article('37'))


class FirmwareEncodesStateMachineTest(unittest.TestCase):
    def handler(self):
        s = INO[INO.index('// Maquina de estados do leitor (DEVICE V1).'):]
        return s[:s.index('#endif')]

    def test_handler_rules(self):
        h = self.handler()
        search = h[h.index('if(estado==LEXV1_ARTICLE_SEARCH_MODE){'):h.index("if(event.usage==0x28){ pedirEntrarBuscaV1=true; return; }")]
        self.assertIn("if(event.ascii>='0' && event.ascii<='9'){", search)
        self.assertIn('artigoDigitado+=(char)event.ascii;', search)
        self.assertNotIn('pedirCamadaV1', search)                                     # no layer from the search mode
        self.assertIn('artigoDigitado.remove(artigoDigitado.length()-1)', search)
        self.assertIn('else pedirCancelarBuscaV1=true;', search)
        self.assertIn('if(event.usage==0x28){ if(artigoDigitado.length()>0) pedirBuscar=true; else pedirRedesenharBusca=true; return; }', search)
        normal = h[h.index("if(event.usage==0x28){ pedirEntrarBuscaV1=true; return; }"):]
        self.assertIn("if(event.ascii>='1' && event.ascii<='4'){ pedirCamadaV1=(char)event.ascii; return; }", normal)
        self.assertIn("if(event.ascii>='0' && event.ascii<='9') return;", normal)          # 5-9 / 0: nothing
        self.assertNotIn('artigoDigitado', normal)                                   # typing never starts a search

    def test_provisional_letters_removed(self):
        self.assertNotIn('[E]ENTENDA', INO)
        self.assertNotIn('0x08 || event.ascii==\'e\'', INO)
        self.assertNotIn('0x15 || event.ascii==\'r\'', INO)
        self.assertIn('tft.print("ENTER=BUSCAR");', INO)          # dynamic footer (test_ui_refinement) keeps ENTER=BUSCAR

    def test_layers_and_loop(self):
        self.assertIn('if(telaAtual==TELA_LEXV1_CAMADA){\n      if(event.usage==0x2A){pedirVoltar=true; return;}', INO)
        for s in ('if(lexV1EstadoLeitor()==LEXV1_NORMAL_READING_MODE && !displayApagado) lexV1EntrarBusca();',   # ENTER always opens it
                  'if(lexV1EstadoLeitor()==LEXV1_NORMAL_READING_MODE && !displayApagado) lexV1AbrirCamadaNumero(tecla);',
                  'if(telaAtual==TELA_LEITOR && lexV1ModoBusca) lexV1ExecutarBuscaArtigo();',
                  'if(lexV1ModoBusca) dl=0;',                                           # text never moves during the search
                  'if(telaAtual==TELA_LEITOR && lexV1ModoBusca){ lexV1CancelarBusca(); return; }',
                  'lexV1BuscaOffsetOrigem=lexV1OffsetTopo();',
                  'if(atual!=lexV1BuscaOffsetOrigem){ reiniciarIndice(lexV1BuscaOffsetOrigem); desenharViewportLeitor(); }',
                  'if(totalCorrelatasArtigo>0) abrirCategoriaRelacao(REL_CORRELATAS);',
                  'else abrirTelaCategoriasJuris();'):
            self.assertIn(s, INO, s)
        found = INO[INO.index('void lexV1ExecutarBuscaArtigo()\n{'):]
        found = found[:found.index('\n}\n')]
        ok = found[found.index('if(lexV1PesquisarArtigoEstrutural(n,0)){'):found.index('}else{')]
        self.assertIn('lexV1ModoBusca=false;', ok)
        self.assertIn('artigoDigitado="";', ok)


if __name__ == '__main__':
    unittest.main()
