"""JURISPRUDENCE_ENGINE — generic adapters + Código Civil portability pilot. Host-only. The pilot publishes nothing and the CF J2I
baseline (315/198) must stay byte-identical."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
sys.path[:0] = [str(ENG), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import discovery_planalto as DP  # noqa: E402
import norm_profiles as NP  # noqa: E402
import build_j2_batch as G  # noqa: E402

PILOT = ENG / 'pilot_cc' / 'PORTABILITY_PILOT_CC.json'
FIXTURE = ('<p>LIVRO I</p><p>Art. 205. A prescrição ocorre em dez anos.</p><p>Art. 206. Prescreve:</p><p>§ 1o Em um ano:</p>'
           '<p>I - a pretensão dos hospedeiros; <strike>(texto antigo)</strike></p><p class="x">Art. 206-A. A prescrição intercorrente '
           '(Redação dada pela Lei nº 14.382, de 2022) (Vide ADI nº 9.999)</p><p>CAPÍTULO II Da Decadência (Redação dada pela Lei nº 1, de 2030)</p>'
           '<p>Art. 1.641. É obrigatório:</p><p>II – da pessoa maior de 70 anos; (Redação dada pela Lei nº 12.344, de 2010) '
           '(Vide Recurso Extraordinário nº 646.721)</p>')


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


class Adapters(unittest.TestCase):
    def test_planalto_discovery_structure_and_struck_text(self):
        ann = DP.extract(FIXTURE, 'CC2002')
        self.assertEqual([(a['target_id'], a['klass'], a['number']) for a in ann],
                         [('CC2002:ART.206-A', 'ADI', '9999'), ('CC2002:ART.1641:INC.II', 'RE', '646721')])
        am = DP.amendment_index(FIXTURE, 'CC2002', ['CC2002:ART.206-A', 'CC2002:ART.206:PAR.1:INC.I', 'CC2002:ART.1641:INC.II'])
        self.assertEqual([a['year'] for a in am['CC2002:ART.206-A']], [2022])          # the CAPÍTULO note (2030) is NOT attributed to 206-A
        self.assertEqual(am['CC2002:ART.206:PAR.1:INC.I'], [])
        self.assertEqual(am['CC2002:ART.1641:INC.II'][0]['year'], 2010)

    def test_grammar_gap_recorded_not_invented(self):
        html = '<p>Art. 7º Ficam sujeitos:</p><p>§ 2º Nos casos:</p><p>a) entrar o agente;</p>'
        an = []                                       # codes: alínea without inciso is now a valid target (grammar extension)
        got = list(DP.walk(html, 'CP1940', an))
        self.assertEqual([t for t, _ in got], ['CP1940:ART.7', 'CP1940:ART.7:PAR.2', 'CP1940:ART.7:PAR.2:AL.a'])
        self.assertEqual(an, [])
        an = []                                       # CF stays strict: recorded as anomaly, never invented
        got = list(DP.walk(html, 'CF88', an))
        self.assertEqual([t for t, _ in got], ['CF88:ART.7', 'CF88:ART.7:PAR.2'])
        self.assertEqual([a['error'] for a in an], ['ALINEA_WITHOUT_INCISO'])
        y = load(ENG / 'pilot_cc' / 'PLANALTO_DISCOVERY_YIELD_7_NORMS.json')['norms']
        self.assertEqual(sorted(y), ['CC2002', 'CE1965', 'CLT1943', 'CP1940', 'CPC2015', 'CPP1941', 'CTN1966'])
        self.assertEqual(y['CC2002']['annotations'], len(load(ENG / 'pilot_cc' / 'PLANALTO_CC2002_ANNOTATIONS.json')['annotations']))

    def test_profiles_backward_compatible_with_cf(self):
        cf, cc = NP.PROFILES['CF88'], NP.PROFILES['CC2002']
        self.assertEqual(cf.namespaces, ('CF88', 'ADCT'))
        self.assertEqual(NP.namespace_check(cf, 'art. 5º da Constituição Federal')['result'], 'PASS')
        self.assertEqual(NP.namespace_check(cc, 'art. 927 do Código Civil')['result'], 'PASS')
        self.assertTrue(NP.namespace_check(cc, 'art. 927 do Código Civil')['cf_auditor_alert'])     # the CF auditor alone would flag it
        self.assertEqual(NP.temporal_check(cc, [dict(year=2022)], 2025)['result'], 'CURRENT')
        self.assertEqual(NP.temporal_check(cc, [dict(year=2022)], 2015)['result'], 'TEMPORAL_ALERT')
        self.assertEqual(NP.citation_granularity(cc, 'O artigo 927, parágrafo único, do Código Civil', '927')['targets'], ['CC2002:ART.927:PAR.UNICO'])
        self.assertEqual(NP.citation_granularity(cc, 'art. 927 do Código Penal', '927')['status'], 'OTHER_NORM')


class Pilot(unittest.TestCase):
    def test_up_to_date_and_deterministic(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(ENG / 'build_pilot_cc.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'))

    def test_publishes_nothing(self):
        d = load(PILOT)
        self.assertEqual((d['CC_RELATIONS_PUBLISHED'], d['CC_FILES_DEPLOYED'], d['SD_CHANGED'], d['FIRMWARE_CHANGED'], d['publishes']),
                         (0, 0, 'NO', 'NO', False))
        self.assertEqual(d['status'], 'PORTABILITY_EVIDENCE')
        for c in d['candidates']:
            self.assertEqual((c['decision_status'], c['human_approved']), ('PORTABILITY_PILOT_ONLY', False))
            self.assertTrue(c['discovered_target'].startswith('CC2002:'))
        self.assertTrue(10 <= d['metrics']['CANDIDATES_ANALYZED'] <= 20)

    def test_cf_baseline_untouched(self):
        self.assertEqual(hashlib.sha256(G.J2I_PAYLOAD.read_bytes()).hexdigest(), G.J2I_PAYLOAD_SHA)
        vis = G.j2i_baseline()
        self.assertEqual((len(vis), len({r[0] for r in vis})), (315, 198))
        self.assertFalse([r for r in vis if not r[0].startswith(('CF88:', 'ADCT:'))])
        idx = (G.J2I_PAYLOAD.parents[2] / '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX')
        for p in (idx, ROOT / 'JURISPRUDENCE_AUDIT/J2H_CANDIDATE_B_OVER_A/candidate/SD/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX'):
            if p.is_file():
                self.assertNotIn(b'CC2002', p.read_bytes())

    def test_metrics_consistent(self):
        d = load(PILOT)
        m, rows = d['metrics'], d['candidates']
        self.assertEqual(m['ITEMS_REQUIRING_HUMAN_JUDGMENT'] + m['CANDIDATES_FULLY_AUTOMATIC'], len(rows))
        self.assertEqual(m['FULLY_AUTOMATED_STEPS'], sum(m['STEP_AUTOMATION'].values()))
        self.assertEqual(sum(m['ASSESSMENTS'].values()), len(rows))
        self.assertEqual(m['TOOLS_REUSED_WITHOUT_CHANGE'] + m['TOOLS_REUSED_AFTER_PARAMETERIZATION'] + m['TOOLS_REQUIRING_NEW_CODE']
                         + m['TOOLS_NOT_REUSABLE'] + m['TOOLS_GENERIC_NOT_EXERCISED'], len(d['tools']))


if __name__ == '__main__':
    unittest.main()
