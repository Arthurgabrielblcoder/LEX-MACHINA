"""STJ adapter (official súmulas PDF): parser, reference -> target mapping, and the Súmula 403/203 official-source resolution. No network."""
import json
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
sys.path[:0] = [str(ENG), str(ROOT / 'LEGAL_TARGET_ID')]
import discovery_stj_sumulas as D  # noqa: E402
import target_id as T  # noqa: E402

FIXTURE = '''SÚMULA 403
DIREITO CIVIL - DANO MORAL
Enunciado:
Independe de prova do prejuízo a indenização pela publicação não autorizada de imagem de pessoa com fins econômicos ou comerciais.
Referências Legislativas:
LEG:FED CFB:****** ANO:1988 ***** CF-1988 CONSTITUIÇÃO FEDERAL DE 1988 ART:00005 INC:00005 INC:00010 LEG:FED LEI:003071 ANO:1916 ***** CC-16 CÓDIGO CIVIL DE 1916 ART:00159 LEG:FED LEI:010406 ANO:2002 ***** CC-02 CÓDIGO CIVIL DE 2002 ART:00186 ART:00927

Órgão Julgador:
SEGUNDA SEÇÃO
Data da decisão:
28/10/2009
Fonte:
DJE DATA:24/11/2009 RSSTJ VOL.:00038 PG:00053 RSTJ VOL.:00216 PG:00758

Excerto dos Precedentes Originários:
"..."
SÚMULA 404 (SÚMULA CANCELADA)
DIREITO X
Enunciado:
Texto.
Referências Legislativas:
LEG:FED LEI:010406 ANO:2002 ***** CC-02 ART:00927 PAR:UNICO LEG:FED DEL:002848 ANO:1940 ***** CP-40 ART:00007 PAR:00002 LET:A

Órgão Julgador:
SEGUNDA SEÇÃO
Data da decisão:
01/01/2010
Fonte:
DJE
'''


class STJAdapter(unittest.TestCase):
    def test_parser_and_targets(self):
        e = {x['number']: x for x in D.parse(FIXTURE, D.catalog_laws())}
        s403 = e[403]
        self.assertEqual((s403['status'], s403['orgao'], s403['data_decisao']), ('VIGENTE', 'SEGUNDA SEÇÃO', '28/10/2009'))
        self.assertTrue(s403['enunciado'].startswith('Independe de prova do prejuízo'))
        self.assertEqual([r['targets'] for r in s403['references']], [['CF88:ART.5:INC.V', 'CF88:ART.5:INC.X'], [], ['CC2002:ART.186', 'CC2002:ART.927']])
        self.assertIsNone(s403['references'][1]['catalog_id'])          # CC/1916 is not a catalog norm: never mapped to CC2002
        s404 = e[404]
        self.assertEqual(s404['status'], 'CANCELADA')
        self.assertEqual([r['targets'] for r in s404['references']], [['CC2002:ART.927:PAR.UNICO'], ['CP1940:ART.7:PAR.2:AL.a']])

    def test_index_from_official_pdf(self):
        d = json.loads((ENG / 'stj/STJ_SUMULAS_INDEX.json').read_text(encoding='utf-8'))
        src = d['source']
        self.assertEqual((src['tier'], src['org'], len(src['pdf_sha256'])), ('A', 'STJ', 64))
        self.assertIn('nenhum desafio anti-robô contornado', src['method'])
        self.assertEqual(d['stats']['SUMULAS'], len(d['entries']))
        self.assertEqual(d['stats']['GRAMMAR_REJECTS'], 0)
        for e in d['entries']:
            for r in e['references']:
                for t in r['targets']:
                    self.assertTrue(T.validate_target_id(t)[0], t)
                    self.assertTrue(t.startswith(r['catalog_id'] + ':'))

    def test_403_and_203_resolved_not_materialized(self):
        res = json.loads((ROOT / 'JURISPRUDENCE_AUDIT/STJ_OFFICIAL_SOURCE_RESOLUTIONS.json').read_text(encoding='utf-8'))
        idx = {e['number']: e for e in json.loads((ENG / 'stj/STJ_SUMULAS_INDEX.json').read_text(encoding='utf-8'))['entries']}
        for n in (403, 203):
            r = res['items'][f'STJ:SUMULA:{n}']
            self.assertEqual((r['source_status'], r['editorial_state_unchanged']), ('OFFICIAL_SOURCE_RESOLVED', 'UNRESOLVED_EXTERNAL'))
            self.assertEqual(r['enunciado'], idx[n]['enunciado'])
        self.assertEqual(res['items']['STJ:SUMULA:403']['data_decisao'], '28/10/2009')
        self.assertIn('CF88:ART.105:INC.III', [t for x in res['items']['STJ:SUMULA:203']['referencias_legislativas'] for t in x['targets']])
        b10 = json.loads((ROOT / 'JURISPRUDENCE_AUDIT/J2_RATIFICATION_RECORD_10.json').read_text(encoding='utf-8'))
        self.assertEqual({i['recommendation_id']: i['ratification_status'] for i in b10['items']}['J0-BL-093'], 'UNRESOLVED_EXTERNAL')
        for p in (ROOT / 'JURISPRUDENCE_AUDIT/J2H_CANDIDATE_B_OVER_A/candidate/SD/99_JURISPRUDENCIA_V2/05_INDICES_ESP32').glob('*.IDX'):
            self.assertNotIn(b'STJ:SUMULA:403', p.read_bytes())


if __name__ == '__main__':
    unittest.main()
