"""Fase D — regression cases from J1/J2 for the reusable alert detectors (short excerpts of official texts already reviewed)."""
import sys
import unittest
from pathlib import Path

AUD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AUD))
import j2_auditors as D  # noqa: E402


class Auditors(unittest.TestCase):
    def test_namespace_state_constitution_adi_2167(self):
        ementa = 'Alteração dos arts. 33, XVIII; 46, § 3°; 62, parágrafo único, e 103 da Constituição do Estado de Roraima por emenda ' \
                 'constitucional estadual. Violação aos arts. 2º; 25 e 84 da Constituição da República.'
        r = D.namespace_alerts(ementa)
        self.assertIn('CONSTITUICAO_ESTADUAL', r['other_norms'])
        self.assertTrue(r['alert'])

    def test_namespace_other_norm_without_cf(self):
        r = D.namespace_alerts('art. 1º-F da Lei nº 9.494/97, com redação dada pela Lei nº 11.960/09')
        self.assertIn('LEI', r['other_norms'])
        self.assertTrue(r['alert'] and not r['cf_mentioned'])

    def test_namespace_adct(self):
        r = D.namespace_alerts('declarar a inconstitucionalidade do art. 101, § 5º, do ADCT, com redação da EC 113/21')
        self.assertIn('ADCT', r['other_norms'])

    def test_namespace_cf_only_no_alert(self):
        r = D.namespace_alerts('A imunidade material parlamentar (art. 53, caput, CF/1988) configura excludente')
        self.assertTrue(r['cf_mentioned'])
        self.assertFalse(r['alert'])

    def test_temporal_tema_594_and_558(self):
        t594 = D.temporal_alerts('As regras dos parágrafos 4º e 5º do artigo 40 da Constituição Federal, na redação anterior à EC 20/1998')
        self.assertTrue(t594['alert'])
        self.assertIn(20, t594['ecs_cited'])
        t558 = D.temporal_alerts('prevista nos §§ 9º e 10 do art. 100 da Constituição Federal, incluídos pela EC nº 62/09')
        self.assertIn('REDACAO_DADA_POR_EC', t558['signals'])
        self.assertIn(62, t558['ecs_cited'])
        orig = D.temporal_alerts('Recurso extraordinário sobre os §§ 4º e 5º do art. 40 (redação originária)')
        self.assertIn('REDACAO_ORIGINARIA', orig['signals'])

    def test_status_adi_7697_provisional(self):
        s = D.status_signals('O Tribunal, por unanimidade, referendou a decisão que concedeu parcialmente a medida cautelar')
        self.assertTrue(s['provisional'])
        m = D.status_signals('converteu o julgamento da medida cautelar em julgamento de mérito e julgou parcialmente procedente')
        self.assertFalse(m['provisional'])
        self.assertIn('MERITO_JULGADO', m['signals'])

    def test_status_modulation_and_object_loss(self):
        self.assertIn('MODULACAO', D.status_signals('modulam-se os efeitos das decisões declaratórias')['signals'])
        self.assertIn('PERDA_DE_OBJETO', D.status_signals('ação julgada parcialmente prejudicada')['signals'])

    def test_joint_scope_adi_7047_7064(self):
        dec = {'ADI 7047': {'CF:100:9', 'CF:100:11', 'ADCT:101:5'},
               'ADI 7064': {'CF:100:9', 'CF:100:11', 'ADCT:101:5', 'ADCT:107-A', 'EC114:6'}}
        r = D.joint_scope(dec)['ADI 7047|ADI 7064']
        self.assertEqual(r['relation'], 'SAME_JUDGMENT_NOT_SAME_SCOPE')
        self.assertEqual(r['only_in']['ADI 7064'], ['ADCT:107-A', 'EC114:6'])
        self.assertFalse(D.scope_allows(dec, 'ADI 7047', 'ADCT:107-A'))     # the regression the J2E label test protects
        self.assertTrue(D.scope_allows(dec, 'ADI 7047', 'ADCT:101:5'))


if __name__ == '__main__':
    unittest.main()
