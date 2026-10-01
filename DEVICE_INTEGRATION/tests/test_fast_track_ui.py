"""FAST TRACK physical test UI (uncommitted until human validation): host-side smoke test of the E/R flow.

Mirrors the firmware: the offset of the first visible reader line of CF88_RUNTIME.txt -> CF88_TEXT_MAP.IDX (floor) -> target
-> ENTENDA (DIRECT / COVERED_BY_BLOCK via the anchor block / NONE) and REFERENCES (only CURRENT_VISIBLE rows are listed).
"""
import re
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(DI / 'tests'))
import device_lookup_simulator as S  # noqa: E402
from test_a3b_prep import INO, SD, device_v1_ino_sections  # noqa: E402

RT = (SD / '05_TEXT/CF88_RUNTIME.txt').read_bytes()

# (labels at line starts, in order, from `start`) -> expected target, ENTENDA resolution, anchor, visible references
CASES = [
    (0, ('Art. 5º', 'V - '), 'CF88:ART.5:INC.V', 'COVERED_BY_BLOCK', 'CF88:ART.5:INC.IV', 1),
    (0, ('Art. 21.', 'XXIV - '), 'CF88:ART.21:INC.XXIV', 'DIRECT', 'CF88:ART.21:INC.XXIV', 0),
    (0, ('Art. 22.', 'XXIX - '), 'CF88:ART.22:INC.XXIX', 'DIRECT', 'CF88:ART.22:INC.XXIX', 0),
    (0, ('Art. 24.', '§ 4º'), 'CF88:ART.24:PAR.4', 'COVERED_BY_BLOCK', 'CF88:ART.24:PAR.3', 0),
    (0, ('Art. 37.', '§ 6º'), 'CF88:ART.37:PAR.6', 'DIRECT', 'CF88:ART.37:PAR.6', 5),
    (0, ('Art. 60.', '§ 4º', 'IV - '), 'CF88:ART.60:PAR.4:INC.IV', 'DIRECT', 'CF88:ART.60:PAR.4:INC.IV', 0),
    ('ADCT', ('Art. 10.', 'II - '), 'ADCT:ART.10:INC.II', 'DIRECT', 'ADCT:ART.10:INC.II', 0),
    (0, ('Art. 25.',), 'CF88:ART.25', 'NONE', None, 1),
    (0, ('Art. 114.', 'VIII - '), 'CF88:ART.114:INC.VIII', 'NONE', None, 0),      # known issue: 2 historical refs stay hidden
]


def line_offset(start, labels):
    p = start
    for lab in labels:
        p = RT.index(b'\n' + lab.encode('utf-8'), p) + 1
    return p


class FastTrackUiFlowTest(unittest.TestCase):
    def test_reader_position_to_layers(self):
        dev = S.Device(SD)
        try:
            size, sha = dev.verify_runtime_file()
            adct = int(dev.text_map.header['NAMESPACE_START_ADCT'][0])
            for start, labels, tid, res, anchor, visible in CASES:
                off = line_offset(adct if start == 'ADCT' else start, labels)
                for probe in (off, off + 5):                      # top line = start of the dispositivo or a wrapped continuation
                    r = dev.resolve_text_position(probe, size, sha)
                    self.assertEqual((r['status'], r['target_id']), ('OK', tid), (labels, probe))
                self.assertIsNotNone(dev.targets.find(tid))
                e = dev.entenda(tid)
                self.assertEqual(e['resolution_type'] if e else 'NONE', res, tid)
                if e:
                    self.assertEqual(e['anchor_target_id'], anchor)
                    blob = e['blob'].decode('utf-8')
                    for sec in ('#O QUE DIZ', '#O QUE SIGNIFICA', '#EXEMPLO PRÁTICO', '#ATENÇÃO', '#PALAVRAS DIFÍCEIS'):
                        self.assertIn(sec, blob, tid)
                    self.assertLessEqual(e['payload_length'], 8192)              # LEXV1_BLOCO_MAX
                    if res == 'COVERED_BY_BLOCK':                                # same block as the anchor, no duplicated payload
                        ea = dev.entenda(anchor)
                        self.assertEqual((ea['payload_offset'], ea['payload_length']), (e['payload_offset'], e['payload_length']))
                rows = dev.references(tid)
                self.assertEqual(sum(r[2] == 'CURRENT_VISIBLE' for r in rows), visible, tid)
            # the preamble / namespace nodes are not targets: no layer
            r = dev.resolve_text_position(10, size, sha)
            self.assertIsNone(dev.targets.find(r['target_id']) if r['target_id'] else None)
            # wrong file (e.g. the legacy cf.txt) -> fail closed, no layer
            self.assertEqual(dev.resolve_text_position(off, 429242, sha)['status'], 'FAIL_CLOSED')
        finally:
            dev.close()


class FastTrackUiSourceTest(unittest.TestCase):
    def test_ui_wiring_is_flag_gated_and_fail_closed(self):
        v1 = device_v1_ino_sections()
        for s in ('lexV1Pronto=runtimeOk && guardOk && s1==LEXV1_OK && s3==LEXV1_OK && s4==LEXV1_OK;',
                  'caminho=LEXV1_RUNTIME_CF_PATH;',                                       # CF opened from the verified runtime
                  'if(event.ascii>=\'1\' && event.ascii<=\'4\'){ pedirCamadaV1=(char)event.ascii; return; }',
                  'case \'3\':\n      if(v1cf) lexV1AbrirCamada(\'E\',alvo);',      # target resolved at the key press
                  'case \'4\':\n      if(v1cf) lexV1AbrirCamada(\'R\',alvo);',
                  'if(telaAtual==TELA_LEXV1_CAMADA){ lexV1FecharCamada(); return; }',     # ESC / BACKSPACE close the layer
                  'else if(telaAtual==TELA_LEXV1_CAMADA) deltaCamadaV1 += d;',            # scroll wheel
                  'return ativo<lexV1AdctStart;',                                         # legacy CF layers never on the ADCT part
                  'if(!visibilidade || strcmp(visibilidade,"CURRENT_VISIBLE")!=0) return LEXV1_LAYER_HIDDEN;',  # hidden stay hidden
                  # refinement: layers without content are not offered (no "not available" screens); target from the TEXT_MAP
                  'lexv1TargetAtOffset(lexV1MapIdx,lexV1RuntimeBytes,lexV1RuntimeSha,off,tid,sizeof(tid),&ini,&fim)'):
            self.assertIn(s, v1, s)
        # layer buffers are released on BACK and payloads are closed right after reading
        close = INO[INO.index('void lexV1FecharCamada()\n{'):]
        self.assertIn('lexV1LiberarCamada();', close[:close.index('\n}\n')])
        ent = INO[INO.index('static void lexV1MontarEntenda('):]
        self.assertIn('pl.fechar(); lk.fechar();', ent[:ent.index('\n}\n')])
        self.assertIn('rp.fechar(); rl.fechar();', INO[INO.index('static int lexV1CarregarItensRef('):])

    def test_legacy_paths_untouched_without_flag(self):
        # every new identifier of the UI only appears inside LEX_DEVICE_V1_ENABLED sections
        outside = INO
        for sec in re.findall(r'#if LEX_DEVICE_V1_ENABLED\n.*?#(?:else|endif)', INO, re.S):
            outside = outside.replace(sec, '')
        for ident in ('TELA_LEXV1_CAMADA', 'pedirCamadaV1', 'deltaCamadaV1', 'lexV1Pronto', 'lexV1AbrirCamada', 'LEXV1_RUNTIME_CF_PATH'):
            self.assertNotIn(ident, outside, ident)


if __name__ == '__main__':
    unittest.main()
