"""Adapter #4 (STJ qualified precedents, official open data): citation extraction fails closed; index consistent with the grammar."""
import json
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ENG), str(ENG.parent / 'LEGAL_TARGET_ID')]
import discovery_stj_precedentes as D  # noqa: E402
import target_id as T  # noqa: E402


class STJPrecedentes(unittest.TestCase):
    def test_citations(self):
        c = lambda s: D.cites(s, 'CC2002')  # noqa: E731
        self.assertEqual(c('prescreve em três anos, nos termos do art. 206, § 3º, inciso III, do Código Civil de 2002')[0],
                         ['CC2002:ART.206:PAR.3:INC.III'])
        self.assertEqual(c('as disposições do art. 591 c/c o art. 406 do CC/02.')[0], ['CC2002:ART.591', 'CC2002:ART.406'])
        self.assertEqual(c('conforme interpretação extraída do art. 202, parágrafo único, do Código Civil de 2002.')[0], ['CC2002:ART.202:PAR.UNICO'])
        self.assertEqual(c('a regra de transição do art. 2.028 do CC/2002')[0], ['CC2002:ART.2028'])
        t, old, _ = c('prescreve em 20 anos (art. 177 do CC/1916) ou em 3 anos (art. 206, § 3º, IV, do CC/2002)')
        self.assertEqual((t, old), (['CC2002:ART.206:PAR.3:INC.IV'], 1))                 # CC/1916 never becomes a CC2002 target
        self.assertEqual(c('não se aplica a regra do art. 442 do CCom')[0], [])           # other code
        self.assertEqual(D.reflex_cites('Art. 206, § 3º, IX - Código Civil', 'CC2002'), ['CC2002:ART.206:PAR.3:INC.IX'])

    def test_index(self):
        d = json.loads((ENG / 'stj/STJ_PRECEDENTES_INDEX.json').read_text(encoding='utf-8'))
        self.assertEqual((d['adapter'], d['source']['tier'], d['source']['licence']), ('discovery_stj_precedentes', 'A', 'CC-BY'))
        self.assertEqual(len(d['source']['csv_sha256']), 64)
        self.assertEqual(d['stats']['ENTRIES_CITING_NORM'], len([e for e in d['entries'] if e['targets_from_tese'] or e['targets_from_reference']]))
        self.assertEqual(d['stats']['GRAMMAR_REJECTS'], 0)
        for e in d['entries']:
            self.assertRegex(e['id'], r'^STJ:(REPETITIVO|IAC|SIRDR|PUIL|CONTROVERSIA):\d+$')
            for t in e['targets_from_tese'] + e['targets_from_reference']:
                self.assertEqual(T.parse_target_id(t)['namespace'], 'CC2002')


if __name__ == '__main__':
    unittest.main()
