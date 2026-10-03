"""ARTICLE_SEARCH REPEAT_READY UX (DEVICE V1, uncommitted until the human test).

NORMAL_READING: 1 CORRELATAS, 2 JURISPRUDENCIA, 3 ENTENDA, 4 REFERENCIAS, ENTER = ALWAYS opens ARTICLE_SEARCH (no scrolling needed).
With a valid previous search the box comes preloaded with the previous query (REPEAT_READY): ENTER untouched -> next structural
occurrence (centered); the first digit REPLACES the query; the first BACKSPACE edits; both turn it into a NEW_QUERY (old cursor dropped).
After every result the reader is back in NORMAL_READING. `ArticleSearchV1` (tools/reader_viewport.py) is the host model; the source
tests pin the firmware handler.
"""
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(DI / 'tests'))
import reader_viewport as V  # noqa: E402
from test_article_search_landing import func  # noqa: E402
from test_article_search_next_occurrence import article_rows  # noqa: E402

INO = (ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
SD1 = DI / 'staging_sd_v1/SD/99_LEX_V1'
SD3 = DI / 'staging_sd_v1_run3_candidate/SD/99_LEX_V1'


class FirmwareRepeatReadyTest(unittest.TestCase):
    def handler(self):
        h = INO[INO.index('if(estado==LEXV1_ARTICLE_SEARCH_MODE){'):]
        return h[:h.index("if(event.usage==0x28){ pedirEntrarBuscaV1=true; return; }")]

    def test_flag_declared_in_v1_region(self):
        reg = INO[INO.index('#if LEX_DEVICE_V1_ENABLED'):]
        self.assertIn('volatile bool lexV1RepetirPronto=false;', reg[:reg.index('#endif')])

    def test_first_digit_replaces(self):
        h = self.handler()
        d = h[h.index("if(event.ascii>='0' && event.ascii<='9'){"):h.index('if(event.usage==0x2A){')]
        self.assertLess(d.index('if(lexV1RepetirPronto){ artigoDigitado=""; lexV1RepetirPronto=false; numeroBuscaEditado=true; }'),
                        d.index('artigoDigitado+=(char)event.ascii;'))

    def test_first_backspace_edits(self):
        h = self.handler()
        b = h[h.index('if(event.usage==0x2A){'):h.index('if(event.usage==0x28){')]
        self.assertLess(b.index('if(lexV1RepetirPronto){ lexV1RepetirPronto=false; numeroBuscaEditado=true; }'),
                        b.index('artigoDigitado.remove(artigoDigitado.length()-1);'))
        self.assertIn('else pedirCancelarBuscaV1=true;', b)                               # empty box: BACK cancels (unchanged)

    def test_enter_always_opens_search_with_preload(self):
        loop = INO[INO.index('if(pedirEntrarBuscaV1){'):]
        self.assertIn('lexV1EntrarBusca();', loop[:loop.index('if(pedirCancelarBuscaV1){')])
        e = func(INO, 'void lexV1EntrarBusca()\n{')
        self.assertIn('lexV1ModoBusca=true;', e)
        ok = e[e.index('if(repetir){'):e.index('}else{')]
        self.assertIn('artigoDigitado=numeroUltimaBusca;', ok)
        self.assertIn('lexV1RepetirPronto=true;', ok)
        self.assertNotIn('numeroBuscaEditado=', ok)                                         # preloaded query is NOT an edit
        els = e[e.index('}else{'):]
        for s in ('lexV1RepetirPronto=false;', 'artigoDigitado="";', 'numeroBuscaEditado=true;'):
            self.assertIn(s, els)

    def test_next_and_cancel_close_the_search(self):
        n = func(INO, 'void lexV1ProximaOcorrenciaArtigo()\n{')
        self.assertLess(n.index('lexV1ModoBusca=false;'), n.index('lexV1PesquisarArtigoEstrutural'))   # NORMAL in both outcomes
        self.assertIn('lexV1RepetirPronto=false;', func(INO, 'void lexV1CancelarBusca()\n{'))
        ex = func(INO, 'void lexV1ExecutarBuscaArtigo()\n{')
        self.assertLess(ex.index('lexV1RepetirPronto=false;'), ex.index('if(repetir){'))  # consumed by any ENTER


@unittest.skipUnless((SD1 / '05_TEXT/CF88_RUNTIME.txt').is_file(), 'baseline staging not built')
class RepeatReadyModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = V.Reader(SD1)
        cls.cf5, cls.adct5 = article_rows(cls.r, 5)

    def m(self, top=0):
        return V.ArticleSearchV1(self.r, top)

    def after5(self):
        m = self.m().keys('ENTER', '5', 'ENTER')
        self.assertEqual((m.state, m.view()['active_target']), (m.NORMAL, 'CF88:ART.5'))
        return m

    def test_01_no_history_enter_opens_empty_search(self):
        m = self.m().keys('ENTER')
        self.assertEqual((m.state, m.buffer, m.repeat_ready), (m.SEARCH, '', False))

    def test_02_history_preloaded(self):
        m = self.after5().keys('ENTER')
        self.assertEqual((m.state, m.buffer, m.repeat_ready, m.edited), (m.SEARCH, '5', True, False))

    def test_03_enter_untouched_is_next_occurrence(self):
        m = self.after5().keys('ENTER', 'ENTER')
        v = m.view()
        self.assertEqual((m.state, v['active_target'], v['contexto'], m.log), (m.NORMAL, 'ADCT:ART.5', 'ADCT:ART.5', [self.cf5, self.adct5]))
        self.assertEqual(v['rows'][self.r.ACTIVE]['offset'], self.adct5)                    # centered on the active row

    def test_04_05_06_07_first_digit_replaces_then_new_query(self):
        m = self.after5().keys('ENTER', '1')
        self.assertEqual((m.buffer, m.repeat_ready, m.edited), ('1', False, True))          # "1", not "51"
        m.keys('9', '3')
        self.assertEqual(m.buffer, '193')
        m.key('ENTER')
        v = m.view()
        self.assertEqual((m.state, v['active_target'], v['contexto']), (m.NORMAL, 'CF88:ART.193', 'CF88:ART.193'))   # no scrolling needed
        self.assertEqual(m.log, [self.cf5, article_rows(self.r, 193)[0]])                  # new query from offset 0, not the 5 cursor

    def test_08_key4_opens_layer_and_never_edits(self):
        m = self.m().keys('ENTER', '1', '9', '3', 'ENTER', '4')
        self.assertEqual(m.state, m.NORMAL)
        self.assertEqual(m.opened[-1]['key'], '4')
        self.assertEqual(m.opened[-1]['target'], 'CF88:ART.193')
        self.assertTrue(m.opened[-1]['available'])
        self.assertEqual((m.num, m.buffer), ('193', ''))                                    # query untouched: no "1934"
        m.key('ENTER')
        self.assertEqual((m.buffer, m.repeat_ready), ('193', True))                         # layer view did not move the text

    def test_09_back_cancels_and_keeps_current_position(self):
        m = self.after5().keys('ENTER', 'ENTER')                                            # on ADCT art. 5
        here = m.top
        m.keys('ENTER')                                                                      # preloaded box
        m.keys('BACKSPACE', 'BACKSPACE')                                                     # edit '5' -> '' then cancel
        self.assertEqual((m.state, m.top, m.view()['active_target']), (m.NORMAL, here, 'ADCT:ART.5'))   # same reading position
        self.assertEqual(m.log, [self.cf5, self.adct5])                                     # no new search executed
        self.assertFalse(m.has)                                                              # BACK resets the search state
        m.key('ENTER')
        self.assertEqual((m.buffer, m.repeat_ready), ('', False))

    def test_10_backspace_on_preloaded_query_edits(self):
        m = self.m().keys('ENTER', '3', '7', 'ENTER', 'ENTER')
        self.assertEqual((m.buffer, m.repeat_ready), ('37', True))
        m.key('BACKSPACE')
        self.assertEqual((m.buffer, m.repeat_ready, m.edited, m.state), ('3', False, True, m.SEARCH))
        m.key('ENTER')
        self.assertEqual(m.view()['active_target'], 'CF88:ART.3')                           # edited -> new query, never "next"

    def test_11_edited_query_never_uses_old_cursor(self):
        m = self.after5().keys('ENTER', 'BACKSPACE', '5', 'ENTER')                           # same digits, but edited
        self.assertEqual(m.log, [self.cf5, self.cf5])                                        # from offset 0 again, not ADCT 5
        m = self.after5().keys('ENTER', '5', 'ENTER')                                        # first digit replaces '5' with '5'
        self.assertEqual(m.log, [self.cf5, self.cf5])

    def test_12_end_of_occurrences_preserved(self):
        m = self.after5().keys('ENTER', 'ENTER')
        top = m.top
        m.keys('ENTER', 'ENTER')
        self.assertEqual((m.messages, m.top, m.state, m.view()['active_target']), (['SEM OUTRA OCORRENCIA'], top, m.NORMAL, 'ADCT:ART.5'))
        m.keys('ENTER')
        self.assertEqual((m.buffer, m.repeat_ready), ('5', True))                          # cursor kept (legacy): message again
        m.key('ENTER')
        self.assertEqual((m.messages, m.top), (['SEM OUTRA OCORRENCIA'] * 2, top))

    def test_scroll_drops_preload_but_enter_still_opens(self):
        m = self.after5().keys('SCROLL1', 'ENTER')
        self.assertEqual((m.state, m.buffer, m.repeat_ready), (m.SEARCH, '', False))


@unittest.skipUnless((SD3 / '10_TARGETS/CF88_TARGETS.IDX').is_file(), 'RUN3 staging candidate not built')
class RepeatReadyRun3Test(unittest.TestCase):
    def test_37_layer4_and_preload(self):
        r = V.Reader(SD3)
        m = V.ArticleSearchV1(r).keys('ENTER', '3', '7', 'ENTER', '4')
        self.assertEqual(m.state, m.NORMAL)
        self.assertEqual((m.opened[-1]['target'], m.opened[-1]['available'], sorted(m.opened[-1]['works'])),
                         ('CF88:ART.37', True, ['Os Donos do Poder', 'Raízes do Brasil']))
        m.key('ENTER')
        self.assertEqual((m.state, m.buffer, m.repeat_ready), (m.SEARCH, '37', True))


if __name__ == '__main__':
    unittest.main()
