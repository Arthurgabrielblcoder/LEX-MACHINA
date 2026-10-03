"""ARTICLE_SEARCH_TARGET_CENTERING_FIX: the article search lands the found occurrence on the ACTIVE row (uncommitted until the human test).

Before: pesquisarArtigo -> reiniciarIndice(pos) + linhaTopo=0 put "Art. N" on row 0, while CONTEXTO / ACTIVE_TARGET are resolved on row
linhaContextoAtivo(LEITOR_LINHAS_VISIVEIS) (= 6). Short caputs -> the active row already belonged to a paragraph/inciso/next article
(art. 193 -> CF88:ART.193:PAR.UNICO, no layer 4). Fix (visual only): lexV1PousarBuscaNaLinhaAtiva moves the viewport so the occurrence
is on that same row; ACTIVE_TARGET is still the TEXT_MAP target of the active row (no sticky target), every layer follows it.
`Reader` (tools/reader_viewport.py) replays the firmware wrap / search / active row; constants are read from the sketch.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
import reader_viewport as V  # noqa: E402

FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
INO = (FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
CTX = (FW / 'contexto_juridico.h').read_text(encoding='utf-8')
SD1 = DI / 'staging_sd_v1/SD/99_LEX_V1'
SD3 = DI / 'staging_sd_v1_run3_candidate/SD/99_LEX_V1'
REQUESTED = (37, 43, 62, 170, 193, 194, 205, 220, 225, 227)


def head(path):
    return subprocess.run(['git', 'show', f'lex-device-v1-physical-approved-2026-10-01:{path}'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8').stdout


def func(src, name):
    body = src[src.index(name):]
    return body[:body.index('\n}\n')]


def strip_v1(src):
    """Source as compiled with LEX_DEVICE_V1_ENABLED=0 (drop '#if LEX_DEVICE_V1_ENABLED' branches, keep '#else' branches)."""
    out, stack = [], []
    for line in src.replace('\r\n', '\n').split('\n'):
        s = line.strip()
        if s.startswith('#if'):
            stack.append('v1' if s == '#if LEX_DEVICE_V1_ENABLED' else 'other')
            if stack[-1] == 'other' and all(x != 'v1' for x in stack[:-1]):
                out.append(line)
            continue
        if s.startswith('#else') and stack and stack[-1] in ('v1', 'v1else'):
            stack[-1] = 'v1else'
            continue
        if s.startswith('#endif') and stack:
            k = stack.pop()
            if k == 'other' and all(x != 'v1' for x in stack):
                out.append(line)
            continue
        if all(x != 'v1' for x in stack):
            out.append(line)
    return '\n'.join(out)


class SourceContractTest(unittest.TestCase):
    def test_single_definition_of_the_active_row(self):
        self.assertEqual(len(re.findall(r'static inline int linhaContextoAtivo\(int total\)', CTX)), 1)
        self.assertIn('int centro=linhaContextoAtivo(total);', func(CTX, 'static inline int escolherContextoPredominante('))
        self.assertNotIn('total/2', func(CTX, 'static inline int escolherContextoPredominante('))
        self.assertIn('i=linhaContextoAtivo(LEITOR_LINHAS_VISIVEIS);', func(INO, 'void lexV1SincronizarAlvo(int indiceContexto)\n{'))
        self.assertNotIn('LEITOR_LINHAS_VISIVEIS/2', func(INO, 'void lexV1SincronizarAlvo(int indiceContexto)\n{'))
        self.assertEqual(V.firmware_constants()['active_row'], 6)
        self.assertEqual(V.firmware_constants(FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino', FW / 'contexto_juridico.h')['rows'], 12)

    def test_landing_function(self):
        f = func(INO, 'static void lexV1PousarBuscaNaLinhaAtiva(uint32_t ocorrencia)')
        # DEVICE V1 runtime text, or an occurrence from the structural index of the open text (CC_INDEX: e.g. Codigo Civil)
        self.assertIn('if(!lexV1CamadaV1Aplicavel() && !lexV1ArtUltima.indice) return;', f)
        self.assertIn('const int alvo=linhaContextoAtivo(LEITOR_LINHAS_VISIVEIS);', f)  # SAME definition as CONTEXTO/ACTIVE_TARGET
        self.assertIn('reiniciarIndice(ocorrencia);', f)
        self.assertIn('if(indexarAntesDaJanela()==0) break;', f)                  # same wrap as scrolling up
        self.assertIn('linhaTopo=max(0,linhaOcorrencia-alvo);', f)                # clamp at the start of the file
        self.assertNotIn('lexv1TargetAtOffset', f)                                # no TEXT_MAP I/O just for logging (INDEXED_ARTICLE_SEARCH)
        for sticky in ('lexV1Alvo', 'lexV1TidRodape', 'lexV1Disp', 'contextoJuridicoAtivo=', 'guardarCheckpointContexto'):
            self.assertNotIn(sticky, f, sticky)                                    # no forced/sticky target, no seeded context
        self.assertNotRegex(f, r'\b7\b')

    def test_called_only_by_the_article_search(self):
        self.assertEqual(INO.count('lexV1PousarBuscaNaLinhaAtiva('), 3)          # definition + first occurrence + next occurrence
        b = func(INO, 'void lexV1ExecutarBuscaArtigo()\n{')
        ok = b[b.index('if(lexV1PesquisarArtigoEstrutural(n,0)){'):b.index('}else{')]
        self.assertLess(ok.index('lexV1PousarBuscaNaLinhaAtiva(offsetUltimaOcorrencia);'), ok.index('desenharViewportLeitor();'))
        nxt = func(INO, 'void lexV1ProximaOcorrenciaArtigo()\n{')
        self.assertLess(nxt.index('lexV1PousarBuscaNaLinhaAtiva(offsetUltimaOcorrencia);'), nxt.index('desenharViewportLeitor();'))
        old = head('firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino')
        for name in ('bool pesquisarArtigo(const String &numero, uint32_t inicioBusca)', 'void executarBusca()', 'void executarBuscaTexto()',
                     'void reiniciarIndice(uint32_t inicio=0)',
                     'static bool lexV1ResolverAlvoKeypress(char tecla, char *alvo, size_t cap)', 'bool lexV1AtualizarDisponibilidade(bool forcar)\n{'):
            self.assertEqual(func(INO, name), func(old, name), name)               # search, text search, BACK, keypress: untouched
        # BIDIRECTIONAL_SCROLL_PERFORMANCE_FIX changed the scroll path ONLY inside LEX_DEVICE_V1_ENABLED: the flag0 text is identical
        for name in ('void rolarLeitor(int delta)', 'int indexarAntesDaJanela()\n{'):
            self.assertEqual(strip_v1(func(INO, name)), strip_v1(func(old, name)), name)
        wrap = 'bool avancarUmaLinhaVisual(File &f, uint32_t inicio, uint32_t &proximo)'
        self.assertEqual(func(INO, wrap).replace(wrap + '\n#endif', wrap), func(old, wrap))  # same wrap body for File and buffer

    def test_flag0_source_unchanged(self):
        old_ino = head('firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino')
        self.assertEqual(strip_v1(INO), strip_v1(old_ino))                        # every .ino change is inside LEX_DEVICE_V1_ENABLED
        old_ctx = head('firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/contexto_juridico.h')
        # THOUSANDS_PARSER_FIX lives only inside '#if LEX_DEVICE_V1_ENABLED' in the header: compare the flag0 view
        norm = lambda s: strip_v1(s.replace('\r\n', '\n'))                        # noqa: E731
        diff = norm(CTX).replace(norm(old_ctx).split('static inline int escolherContextoPredominante(')[0], '', 1)
        self.assertTrue(norm(CTX).startswith(norm(old_ctx).split('static inline int escolherContextoPredominante(')[0]))
        self.assertEqual(norm(CTX).replace('int centro=linhaContextoAtivo(total);', 'int centro=total/2;')
                         .replace('// Linha visual que representa o dispositivo juridico ativo (regra principal abaixo).\n'
                                  '// Definicao UNICA: o CONTEXTO, o ACTIVE_TARGET e o pouso da busca por artigo (DEVICE V1) usam esta mesma posicao.\n'
                                  'static inline int linhaContextoAtivo(int total)\n{\n  return total/2;\n}\n\n', ''), norm(old_ctx))
        self.assertTrue(diff)


@unittest.skipUnless((SD3 / '10_TARGETS/CF88_TARGETS.IDX').is_file(), 'RUN3 staging candidate not built')
class LandingRun3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = V.Reader(SD3)
        caput_w = {k.rsplit(':CAPUT', 1)[0] for k, f in cls.r.flags.items() if len(f) > 3 and f[3] == 'W' and re.fullmatch(r'CF88:ART\.\d+(-[A-Z])?(:CAPUT)?', k)}
        cls.caput_articles = sorted(caput_w, key=lambda t: int(re.search(r'\d+', t).group()))

    def land(self, n):
        return self.r.search(n)

    def test_before_after_requested(self):
        before = {n: self.r.search(n, 'top')['active_target'] for n in (37, 43, 62, 193)}
        self.assertEqual(before, {37: 'CF88:ART.37:INC.I', 43: 'CF88:ART.43:PAR.1:INC.I', 62: 'CF88:ART.62:PAR.1:INC.I', 193: 'CF88:ART.193:PAR.UNICO'})
        for n in REQUESTED:
            s = self.land(n)
            self.assertEqual((s['active_target'], s['contexto'], s['occurrence_row']), (f'CF88:ART.{n}', f'CF88:ART.{n}', self.r.ACTIVE), n)
            self.assertTrue(s['layer4'], n)

    def test_art193(self):
        s = self.land(193)
        self.assertEqual(s['works'], ['Capital no Século XXI', 'Desigualdade para Todos', 'O Triunfo da Injustiça'])
        self.assertEqual(s['rows'][self.r.ACTIVE]['text'][:9], 'Art. 193.')

    def test_art37_43_62(self):
        self.assertEqual(sorted(self.land(37)['works']), ['Os Donos do Poder', 'Raízes do Brasil'])
        s43 = self.land(43)
        self.assertEqual(s43['works'], ['Formação Econômica do Brasil'])
        self.assertNotIn('Vidas Secas', s43['works'])                             # belongs only to CF88:ART.43:PAR.2:INC.IV
        self.assertEqual(self.land(62)['works'], ['Suzerain'])

    def test_every_caput_with_work_reference(self):
        self.assertGreaterEqual(len(self.caput_articles), 20)
        failed = []
        for a in self.caput_articles:
            s = self.land(a.split('ART.')[1])
            if not (s['active_target'] == a and s['layer4'] and s['works']):
                failed.append((a, s['active_target']))
        self.assertEqual(failed, [])

    def test_gaps_do_not_gain_layer4(self):
        for n in (98, 202):
            s = self.land(n)
            self.assertEqual((s['active_target'], s['occurrence_row'], s['layer4'], s['works']), (f'CF88:ART.{n}', self.r.ACTIVE, False, []), n)

    def test_scroll_after_art37_no_leak(self):
        top = self.land(37)['top']
        seen = {}
        for _ in range(400):                                                       # wheel: one visual line per step
            top = self.r.scroll(top, 1)
            s = self.r.state(top)
            seen.setdefault(s['active_target'], s)
            if s['active_target'] == 'CF88:ART.38':
                break
        for t in ('CF88:ART.37:INC.I', 'CF88:ART.37:PAR.1', 'CF88:ART.37:PAR.6'):
            self.assertIn(t, seen, t)
        for t, s in seen.items():
            if t.startswith('CF88:ART.37:'):
                own = [r[6] for r in self.r.refs.get(t, []) if r[1] == 'WORK_REFERENCE' and r[2] == 'CURRENT_VISIBLE']
                self.assertEqual((s['works'], s['layer4']), (own, bool(own)), t)
                self.assertNotIn('Os Donos do Poder', s['works'])
                self.assertNotIn('Raízes do Brasil', s['works'])

    def test_scroll_after_art193(self):
        top = self.land(193)['top']
        trail = [self.r.state(self.r.scroll(top, k)) for k in range(0, 14)]
        pu = next(s for s in trail if s['active_target'] == 'CF88:ART.193:PAR.UNICO')
        self.assertEqual((pu['layer4'], pu['works']), (False, []))               # caput layer 4 disappears: correct
        a194 = next(s for s in trail if s['active_target'] == 'CF88:ART.194')
        self.assertEqual(a194['works'], [r[6] for k in ('CF88:ART.194', 'CF88:ART.194:CAPUT') for r in self.r.refs.get(k, [])
                                         if r[1] == 'WORK_REFERENCE' and r[2] == 'CURRENT_VISIBLE'])
        self.assertFalse(set(a194['works']) & {'Capital no Século XXI', 'O Triunfo da Injustiça'})
        back = self.r.state(self.r.scroll(self.r.scroll(top, 4), -4))           # down to the paragraph and back up
        self.assertEqual((back['top'], back['active_target'], back['layer4']), (top, 'CF88:ART.193', True))
        tops = [s['top'] for s in trail]
        self.assertEqual(len(set(tops)), len(tops))                               # scrolling moves one visual line per step


@unittest.skipUnless((SD1 / '05_TEXT/CF88_RUNTIME.txt').is_file(), 'baseline staging not built')
class LandingBaselineDataTest(unittest.TestCase):
    """Same fix on the approved physical data (RUN1): every article line keeps its own layers right after the search."""

    @classmethod
    def setUpClass(cls):
        cls.r = V.Reader(SD1)
        cls.arts = [t for _, _, t in cls.r.map if re.fullmatch(r'CF88:ART\.\d+(-[A-Z])?', t)]

    def test_every_cf_article_lands_active(self):
        bad = []
        for a in self.arts:
            n = a.split('ART.')[1]
            s = self.r.search(n)
            if s is None or s['occurrence'] != next(o for o, _, t in self.r.map if t == a):
                continue                                                          # number found elsewhere first (e.g. 5-A vs 5): not this article
            if s['active_target'] != a:
                bad.append((a, s['active_target']))
        self.assertEqual(bad, [])
        self.assertGreaterEqual(len(self.arts), 250)

    def test_layers_follow_the_active_target(self):
        for a in self.arts:
            s = self.r.search(a.split('ART.')[1])
            if s is None or s['active_target'] != a:
                continue
            self.assertEqual(s['entenda'], self.r.flags.get(a, '-')[0] in 'EB', a)                       # ENTENDA: own target only
            self.assertEqual(s['juris'], bool(self.r.layer_rows(a, 'JURISPRUDENCE')), a)                  # footer == list
            self.assertEqual(s['correlatas'], bool(self.r.layer_rows(a, 'CORRELATA')), a)
            self.assertEqual(s['layer4'], bool(self.r.layer_rows(a, 'WORK_REFERENCE')), a)

    def test_entenda_immediately_available(self):
        ent = [a for a in self.arts if self.r.flags.get(a, '-')[0] in 'EB']
        self.assertGreaterEqual(len(ent), 20)
        for a in ent:
            s = self.r.search(a.split('ART.')[1])
            self.assertTrue(s['entenda'] and s['active_target'] == a, a)
        self.assertFalse(self.r.search('1', 'top')['entenda'] and self.r.search('1', 'top')['active_target'] == 'CF88:ART.1')

    def test_text_and_data_untouched(self):
        rt = V.Reader(DI / 'staging_sd_v1_run3_candidate/SD/99_LEX_V1') if (SD3 / '05_TEXT/CF88_RUNTIME.txt').is_file() else self.r
        self.assertEqual(self.r.data, rt.data)
        import hashlib
        self.assertEqual(hashlib.sha256(self.r.data).hexdigest(), '7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a')

    def test_clamp_start_and_end(self):
        s = self.r.search('1')                                                    # preamble has fewer lines? the occurrence row is still exact
        self.assertEqual(s['active_target'], 'CF88:ART.1')
        self.assertGreaterEqual(s['top'], 0)
        self.assertEqual(self.r.land_top(0), 0)                                   # occurrence at offset 0: no line above, no negative offset
        last = self.r.map[-1][0]
        st = self.r.state(self.r.land_top(last))
        self.assertLessEqual(st['rows'][-1]['end'], len(self.r.data))             # never past the end of the file
        self.assertEqual(st['active_target'], self.r.map[-1][2])
        lines = self.r.visual_lines(self.r.land_top(last), self.r.ROWS)
        self.assertTrue(all(0 <= a < b <= len(self.r.data) for a, b in lines))

    def test_adct_occurrence_lands_on_its_own_target(self):
        cf5 = self.r.search_article(5)
        adct5 = self.r.search_article(5, cf5 + 1)                                 # next occurrence (pesquisarArtigo(n, inicio))
        self.assertEqual((self.r.map_row_at(cf5), self.r.map_row_at(adct5)), ('CF88:ART.5', 'ADCT:ART.5'))
        for occ, tid in ((cf5, 'CF88:ART.5'), (adct5, 'ADCT:ART.5')):
            st = self.r.state(self.r.land_top(occ))
            self.assertEqual(st['active_target'], tid)                            # from the real offset, never from the number
        self.assertEqual(self.r.search('5')['occurrence'], cf5)                   # ARTICLE_SEARCH (V1) always starts at offset 0

    def test_landing_wrap_is_the_reading_wrap(self):
        for n in ('5', '37', '193', '225'):
            occ = self.r.search_article(n)
            above = self.r.visual_lines_before(occ, self.r.ACTIVE)
            start = self.r.data.rfind(b'\n', 0, above[0][0] - 1) + 1
            start = self.r.data.rfind(b'\n', 0, max(0, start - 300)) + 1         # read forward from further above
            fwd = [a for a, _ in self.r.visual_lines(start, 200)]
            self.assertIn(occ, fwd)
            i = fwd.index(occ)
            self.assertEqual(fwd[i - self.r.ACTIVE:i], [a for a, _ in above], n)  # same rows as continuous reading


if __name__ == '__main__':
    unittest.main()
