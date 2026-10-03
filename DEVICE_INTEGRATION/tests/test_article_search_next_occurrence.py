"""ARTICLE_SEARCH_NEXT_OCCURRENCE_FIX (DEVICE V1, uncommitted until the human test).

Legacy executarBusca: same number + ENTER -> next occurrence from inicioProximaBusca (= last + 1); no wrap; at the end
"SEM OUTRA OCORRENCIA" (500 ms) and the position stays; editing the number / opening a file resets (reiniciarEstadoBusca).
DEVICE V1 before: every hit closed the search and the next ENTER opened a NEW search from offset 0 -> always the first occurrence.
Fix: the same legacy state + a repeat anchor (file, size, top of the landing). ENTER in NORMAL_READING_MODE while the reader is still on
the landing -> next STRUCTURAL occurrence (TEXT_MAP row NS:ART.n exactly at the offset), landed by lexV1PousarBuscaNaLinhaAtiva.
`ArticleSearchV1` (tools/reader_viewport.py) is the host model; the source tests pin that the firmware encodes the same rules.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(DI / 'tests'))
import reader_viewport as V  # noqa: E402
from test_article_search_landing import func, strip_v1  # noqa: E402

INO = (ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
OLD = subprocess.run(['git', 'show', 'HEAD:firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'], cwd=ROOT,
                     capture_output=True, text=True, encoding='utf-8').stdout
SD1 = DI / 'staging_sd_v1/SD/99_LEX_V1'
SD3 = DI / 'staging_sd_v1_run3_candidate/SD/99_LEX_V1'
NEW_IDS = ('lexV1BuscaRepetivel', 'lexV1PodeRepetirBusca', 'lexV1MarcarRepeticaoBusca', 'lexV1InvalidarRepeticaoBusca',
           'lexV1ProximaOcorrenciaArtigo', 'lexV1PesquisarArtigoEstrutural', 'lexV1OcorrenciaEstrutural', 'lexV1BuscaTopoPouso')


class SourceContractTest(unittest.TestCase):
    def test_repeat_condition(self):
        f = func(INO, 'static bool lexV1PodeRepetirBusca()\n{')
        for s in ('lexV1BuscaRepetivel', 'temOcorrenciaDaBusca', '!numeroBuscaEditado', 'numeroUltimaBusca.length()>0',
                  'lexV1BuscaArquivoPouso==caminhoArquivoAtual', 'lexV1BuscaTamanhoPouso==tamanhoArquivoAtual', 'cacheLeitorValido',
                  'lexV1OffsetTopo()==lexV1BuscaTopoPouso'):
            self.assertIn(s, f, s)
        loop = INO[INO.index('if(pedirEntrarBuscaV1){'):]
        loop = loop[:loop.index('if(pedirCancelarBuscaV1){')]
        self.assertIn('if(lexV1EstadoLeitor()==LEXV1_NORMAL_READING_MODE && !displayApagado) lexV1EntrarBusca();', loop)   # ENTER always opens
        self.assertNotIn('lexV1ProximaOcorrenciaArtigo', loop)
        ex = func(INO, 'void lexV1ExecutarBuscaArtigo()\n{')                       # next occurrence only from the search (REPEAT_READY)
        self.assertIn('bool repetir=lexV1RepetirPronto && !numeroBuscaEditado && artigoDigitado==numeroUltimaBusca && lexV1PodeRepetirBusca();', ex)
        self.assertLess(ex.index('if(repetir){ lexV1ProximaOcorrenciaArtigo(); return; }'), ex.index('reiniciarEstadoBusca();'))

    def test_next_occurrence(self):
        f = func(INO, 'void lexV1ProximaOcorrenciaArtigo()\n{')
        self.assertIn('String n=numeroUltimaBusca;', f)                                     # same query, never retyped
        self.assertIn('if(lexV1PesquisarArtigoEstrutural(n,inicioProximaBusca)){', f)        # strictly after the last occurrence
        self.assertIn('lexV1PousarBuscaNaLinhaAtiva(offsetUltimaOcorrencia);', f)          # every occurrence lands on the active row
        self.assertIn('lexV1MarcarRepeticaoBusca();', f)
        end = f[f.index('}else{'):]
        self.assertIn('tft.print("SEM OUTRA OCORRENCIA");', end)                           # legacy end policy
        self.assertIn('delay(500);', end)
        for s in ('reiniciarIndice', 'pesquisarArtigo(n,0)', 'reiniciarEstadoBusca', 'lexV1MarcarRepeticaoBusca'):
            self.assertNotIn(s, end, s)                                                     # no wrap, position and cursor kept

    def test_resets(self):
        e = func(INO, 'void lexV1EntrarBusca()\n{')
        self.assertIn('bool repetir=lexV1PodeRepetirBusca();', e)                           # previous query only while still valid
        self.assertIn('lexV1InvalidarRepeticaoBusca();', e[e.index('}else{'):])            # otherwise: cursor dropped, empty search
        c = func(INO, 'void lexV1CancelarBusca()\n{')
        self.assertIn('lexV1InvalidarRepeticaoBusca();', c)
        self.assertIn('reiniciarEstadoBusca();', c)
        self.assertIn('if(atual!=lexV1BuscaOffsetOrigem){ reiniciarIndice(lexV1BuscaOffsetOrigem); desenharViewportLeitor(); }', c)  # BACK contract
        first = func(INO, 'void lexV1ExecutarBuscaArtigo()\n{')
        self.assertLess(first.index('reiniciarEstadoBusca();'), first.index('lexV1PesquisarArtigoEstrutural(n,0)'))   # new query: fresh cursor
        self.assertIn('lexV1MarcarRepeticaoBusca();', first[first.index('if(lexV1PesquisarArtigoEstrutural(n,0)){'):first.index('}else{')])
        self.assertEqual(OLD.count('reiniciarEstadoBusca(); // Inclusive ao reabrir o mesmo TXT.'), 1)
        self.assertIn('reiniciarEstadoBusca(); // Inclusive ao reabrir o mesmo TXT.', INO)  # opening a file still resets the cursor

    def test_structural_occurrence(self):
        f = func(INO, 'static bool lexV1OcorrenciaEstrutural(const String &n, uint32_t off)\n{')
        self.assertIn('if(!lexV1CamadaV1Aplicavel()) return true;', f)                     # other files: legacy textual match
        self.assertIn('lexv1TargetAtOffset(lexV1MapIdx,lexV1RuntimeBytes,lexV1RuntimeSha,off,tid,sizeof(tid),&ini,&fim)!=LEXV1_OK || ini!=off', f)
        self.assertIn('return a && !strchr(a+5,\':\') && n==String(a+5);', f)             # namespace from the map row, not from the number
        g = func(INO, 'static bool lexV1PesquisarArtigoEstrutural(const String &n, uint32_t inicio)\n{')
        self.assertIn('while(pesquisarArtigo(n,inicio)){', g)                               # same matcher as the legacy search
        self.assertIn('inicio=inicioProximaBusca;', g)
        fail = g[g.index('if(moveu){'):]
        for s in ('reiniciarIndice(topo);', 'offsetUltimaOcorrencia=ultima;', 'temOcorrenciaDaBusca=tinha;', 'desenharViewportLeitor();'):
            self.assertIn(s, fail, s)                                                       # nothing structural: back where it was

    def test_no_sticky_target_and_no_stale_cache(self):
        for name in ('void lexV1ProximaOcorrenciaArtigo()\n{', 'static bool lexV1PesquisarArtigoEstrutural(const String &n, uint32_t inicio)\n{',
                     'static void lexV1MarcarRepeticaoBusca()\n{', 'static bool lexV1PodeRepetirBusca()\n{'):
            f = func(INO, name)
            for s in ('lexV1Alvo', 'lexV1Disp', 'lexV1TidRodape', 'contextoJuridicoAtivo=', 'guardarCheckpointContexto'):
                self.assertNotIn(s, f, (name, s))
        alvo = func(INO, 'void lexV1SincronizarAlvo(int indiceContexto)\n{')
        self.assertIn('if(strcmp(lexV1Disp.tid,lexV1Alvo.tid)!=0) lexV1Disp.valido=false;', alvo)  # new target -> old availability dropped
        self.assertIn('lexV1SincronizarAlvo(indice);', func(INO, 'void diagnosticarContextoSeMudou()\n{'))
        self.assertIn('diagnosticarContextoSeMudou();', func(INO, 'void desenharViewportLeitor()\n{'))

    def test_legacy_untouched_and_flag0(self):
        for name in ('bool pesquisarArtigo(const String &numero, uint32_t inicioBusca)', 'void executarBusca()', 'void executarBuscaTexto()',
                     'void reiniciarEstadoBusca()'):
            self.assertEqual(func(INO, name), func(OLD, name), name)
        old_h = OLD[OLD.index('// Maquina de estados do leitor (DEVICE V1).'):]
        new_h = INO[INO.index('// Maquina de estados do leitor (DEVICE V1).'):]
        old_h, new_h = old_h[:old_h.index('#endif')], new_h[:new_h.index('#endif')]
        changed = 'if(artigoDigitado.length()>0){ artigoDigitado.remove(artigoDigitado.length()-1); pedirRedesenharBusca=true; }'
        for line in old_h.split('\n'):                                                       # keyboard handler: only REPEAT_READY added
            if line.strip() != changed:
                self.assertIn(line, new_h, line)
        extra = [l for l in new_h.split('\n') if l not in old_h.split('\n')]
        self.assertTrue(all(('lexV1RepetirPronto' in l or 'artigoDigitado.remove' in l or l.strip() in ('}', 'if(artigoDigitado.length()>0){'))
                            for l in extra), extra)
        self.assertEqual(strip_v1(INO), strip_v1(OLD))
        flag0 = strip_v1(INO)
        for s in NEW_IDS:
            self.assertNotIn(s, flag0, s)


def article_rows(r, n):
    return [o for o, _, t in r.map if t.count(':') == 1 and t.split(':ART.')[1] == str(n)]


@unittest.skipUnless((SD1 / '05_TEXT/CF88_RUNTIME.txt').is_file(), 'baseline staging not built')
class NextOccurrenceModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = V.Reader(SD1)
        cls.start = cls.r.land_top(cls.r.search_article(37))

    def m(self, top=None):
        return V.ArticleSearchV1(self.r, self.start if top is None else top)

    def assert_landed(self, m, occ, tid):
        v = m.view()
        self.assertEqual(self.r.map_row_at(occ), tid)                                       # confirmed by the TEXT_MAP
        self.assertEqual((v['active_target'], v['contexto']), (tid, tid))
        row = next(x['row'] for x in v['rows'] if x['offset'] == occ)
        self.assertEqual(row, min(self.r.ACTIVE, len(self.r.visual_lines_before(occ, self.r.ACTIVE))))   # active row (clamped at the start)

    def test_art5_cf_then_adct_then_end(self):
        m = self.m().keys('ENTER', '5', 'ENTER')
        cf5, adct5 = article_rows(self.r, 5)
        self.assert_landed(m, cf5, 'CF88:ART.5')
        self.assertEqual(m.view()['rows'][self.r.ACTIVE]['offset'], cf5)
        m.keys('ENTER', 'ENTER')                                                             # ENTER: '5' preloaded; ENTER: next (no retyping)
        self.assertEqual(m.state, m.NORMAL)
        self.assert_landed(m, adct5, 'ADCT:ART.5')
        self.assertEqual(m.view()['rows'][self.r.ACTIVE]['offset'], adct5)
        self.assertGreater(adct5, cf5)
        top = m.top
        m.keys('ENTER', 'ENTER')
        self.assertEqual((m.messages, m.top, m.view()['active_target'], m.state), (['SEM OUTRA OCORRENCIA'], top, 'ADCT:ART.5', m.NORMAL))
        m.keys('ENTER', 'ENTER')                                                             # legacy: repeats the message, no wrap
        self.assertEqual((m.messages[-1], len(m.messages), m.top, m.log), ('SEM OUTRA OCORRENCIA', 2, top, [cf5, adct5]))

    def test_unique_article(self):
        self.assertEqual(len(article_rows(self.r, 193)), 1)
        m = self.m().keys('ENTER', '1', '9', '3', 'ENTER')
        top = m.top
        self.assert_landed(m, article_rows(self.r, 193)[0], 'CF88:ART.193')
        m.keys('ENTER', 'ENTER')
        self.assertEqual((m.messages, m.top, m.view()['active_target']), (['SEM OUTRA OCORRENCIA'], top, 'CF88:ART.193'))

    def test_near_start_and_adct(self):
        m = self.m().keys('ENTER', '1', 'ENTER')
        cf1, adct1 = article_rows(self.r, 1)
        self.assert_landed(m, cf1, 'CF88:ART.1')
        self.assertGreaterEqual(m.top, 0)
        m.keys('ENTER', 'ENTER')
        self.assert_landed(m, adct1, 'ADCT:ART.1')

    def test_remission_is_never_an_occurrence(self):
        self.assertEqual(self.r.search_article(2, 429520), 494627)                          # "art. 2º da Lei nº 12.858" at a line start
        self.assertIsNone(self.r.map_row_at(494627))
        m = self.m().keys('ENTER', '2', 'ENTER', 'ENTER', 'ENTER', 'ENTER', 'ENTER')
        self.assertEqual(m.log, article_rows(self.r, 2))                                    # CF88:ART.2, ADCT:ART.2, then the end
        self.assertEqual(m.messages, ['SEM OUTRA OCORRENCIA'])
        self.assertEqual(m.view()['active_target'], 'ADCT:ART.2')

    def test_every_number_walks_its_structural_occurrences(self):
        nums = sorted({t.split(':ART.')[1] for _, _, t in self.r.map if t.count(':') == 1 and re.fullmatch(r'\d+', t.split(':ART.')[1])}, key=int)
        self.assertGreaterEqual(len(nums), 250)
        for n in nums:
            want = article_rows(self.r, n)
            m = self.m().keys('ENTER', *n, 'ENTER')
            for _ in range(len(want)):
                m.keys('ENTER', 'ENTER')
            self.assertEqual(m.log, want, n)                                                # every occurrence, in order, nothing else
            self.assertEqual(m.messages, ['SEM OUTRA OCORRENCIA'], n)
            for occ in want:
                st = self.r.state(self.r.land_top(occ))
                self.assertEqual(st['active_target'], self.r.map_row_at(occ), n)            # each one active after its landing

    def test_query_change_resets_cursor(self):
        m = self.m().keys('ENTER', '5', 'ENTER', 'SCROLL1', 'ENTER')                        # moved away -> ENTER opens a new search
        self.assertEqual((m.state, m.buffer, m.edited), (m.SEARCH, '', True))
        m.keys('5', 'ENTER')
        self.assertEqual(m.log[-1], article_rows(self.r, 5)[0])                             # fresh query: first occurrence again
        m = self.m().keys('ENTER', '5', 'ENTER', 'ENTER', 'ENTER', 'SCROLL-1', 'ENTER', '3', '7', 'ENTER')
        self.assertEqual(m.log, article_rows(self.r, 5) + [article_rows(self.r, 37)[0]])   # old cursor never reused for 37
        m = self.m().keys('ENTER', '5', 'BACKSPACE', '6', 'ENTER')                          # edited digits
        self.assertEqual(m.log, [article_rows(self.r, 6)[0]])

    def test_back_resets_and_restores_origin_of_the_operation(self):
        m = self.m().keys('ENTER', '5', 'ENTER', 'ENTER', 'ENTER')                          # now on ADCT art. 5 (second occurrence)
        adct_top = m.top
        m.keys('ENTER', 'ENTER')                                                             # end: still on ADCT art. 5
        m.keys('SCROLL2', 'ENTER')                                                           # new search operation from here
        origin = m.top
        m.keys('9', 'BACKSPACE', 'BACKSPACE')                                                # BACK with an empty buffer: cancel
        self.assertEqual((m.state, m.top), (m.NORMAL, origin))                               # origin of THIS operation, not CF art. 5
        self.assertNotEqual(m.top, self.r.land_top(article_rows(self.r, 5)[0]))
        self.assertEqual(origin, self.r.scroll(adct_top, 2))
        self.assertFalse(m.has)
        m.key('ENTER')
        self.assertEqual(m.state, m.SEARCH)                                                  # cursor gone: ENTER opens a search

    def test_file_change_invalidates(self):
        m = self.m().keys('ENTER', '5', 'ENTER', 'OPEN_FILE', 'ENTER')
        self.assertEqual((m.state, m.buffer, m.repeat_ready), (m.SEARCH, '', False))   # nothing preloaded
        m = self.m().keys('ENTER', '5', 'ENTER')
        m.size += 1                                                                          # different runtime size -> no repeat
        self.assertFalse(m.can_repeat())


@unittest.skipUnless((SD3 / '10_TARGETS/CF88_TARGETS.IDX').is_file(), 'RUN3 staging candidate not built')
class LayersAfterNextOccurrenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = V.Reader(SD3)

    def test_layers_only_for_the_new_active_target(self):
        m = V.ArticleSearchV1(self.r).keys('ENTER', '5', 'ENTER')
        cf = m.view()
        self.assertEqual((cf['active_target'], cf['layer4'], sorted(cf['works'])), ('CF88:ART.5', True, ['A Revolução dos Bichos', 'Filadélfia']))
        m.keys('ENTER', 'ENTER')
        adct = m.view()
        fresh = self.r.state(m.top)
        self.assertEqual(adct['active_target'], 'ADCT:ART.5')
        for k in ('layer4', 'works', 'entenda', 'juris', 'correlatas'):
            self.assertEqual(adct[k], fresh[k], k)                                          # stale layer cache = 0
            self.assertEqual(adct[k], {'layer4': self.r.layer_flag('ADCT:ART.5', 3), 'works': [r[6] for r in self.r.layer_rows('ADCT:ART.5', 'WORK_REFERENCE')],
                                       'entenda': self.r.entenda('ADCT:ART.5'), 'juris': self.r.layer_flag('ADCT:ART.5', 2),
                                       'correlatas': self.r.layer_flag('ADCT:ART.5', 1)}[k], k)
        self.assertFalse(set(adct['works']) & set(cf['works']))
        self.assertEqual(self.r.query_keys('ADCT:ART.5'), ['ADCT:ART.5'])                  # ART<->CAPUT only for CF88 article lines

    def test_art193_still_lands_with_layer4(self):
        v = V.ArticleSearchV1(self.r).keys('ENTER', '1', '9', '3', 'ENTER').view()
        self.assertEqual((v['active_target'], v['contexto'], v['layer4']), ('CF88:ART.193', 'CF88:ART.193', True))
        self.assertEqual(v['works'], ['Capital no Século XXI', 'Desigualdade para Todos', 'O Triunfo da Injustiça'])


if __name__ == '__main__':
    unittest.main()
