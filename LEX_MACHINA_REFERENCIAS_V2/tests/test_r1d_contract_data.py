"""Structural and synthetic policy tests only; never re-evaluates a benchmark."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'05_COMPILADOR'))
from canonical_input_r1c import load_canonical as load_base
from canonical_input_r1d import load_canonical
from proof_compiler_r1 import match_claim, load, digest, file_hash
from r1d_support import ROOT, dependent_contracts, integrity, key


class PolicyDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=load_base();cls.inp=load_canonical()

    def test_unchanged_interpreter_and_history(self):
        self.assertTrue(integrity()['passed'])

    def test_universe_and_ontology_unchanged(self):
        self.assertEqual((len(self.inp.devices),len(self.inp.works)),(3461,69))
        self.assertEqual(self.base.data['ontology'],self.inp.data['ontology'])

    def test_existing_nuclei_not_removed(self):
        for did,d in self.base.devices.items():
            self.assertTrue({n['nucleus_id'] for n in d['nuclei']} <= {n['nucleus_id'] for n in self.inp.devices[did]['nuclei']})
            self.assertEqual(d['text'],self.inp.devices[did]['text'])
            self.assertEqual(d['source_hash'],self.inp.devices[did]['source_hash'])

    def test_same_claim_anchor_no_generic_accused(self):
        d=self.inp.devices['CF88:ART.247:PAR.UNICO'];cs=d['nuclei'][0]['contracts_by_relation']
        claim=dict(predicate='OBSTRUIR',objects=['DEFESA_EFETIVA'],context=[],participants=[dict(concept='ACUSADO',role='AFFECTED')])
        self.assertFalse(any(match_claim(self.inp,claim,c['requires']) for c in cs))
        claim['participants'].append(dict(concept='SERVIDOR_PUBLICO',role='AFFECTED'))
        self.assertTrue(any(match_claim(self.inp,claim,c['requires']) for c in cs))
        claim['participants']=[dict(concept='SERVIDOR_PUBLICO',role='CONTEXT')]
        self.assertFalse(any(match_claim(self.inp,claim,c['requires']) for c in cs))

    def test_context_alternative_keeps_original_participant(self):
        cs=self.inp.devices['CF88:ART.247:PAR.UNICO']['nuclei'][0]['contracts_by_relation']
        claim=dict(predicate='OBSTRUIR',objects=['DEFESA_EFETIVA'],context=['CARGO_PUBLICO'],participants=[dict(concept='ACUSADO',role='AFFECTED')])
        self.assertTrue(any(match_claim(self.inp,claim,c['requires']) for c in cs))
        claim['objects']=['PROVA_PENAL']
        self.assertFalse(any(match_claim(self.inp,claim,c['requires']) for c in cs))

    def test_transversal_scope_all_six_families(self):
        before={d['device_id'] for d in self.base.devices.values() if any(n['role']=='GARANTIA_TRANSVERSAL' for n in d['nuclei'])}
        sim=load(ROOT/'06_BENCHMARKS/SIMULACAO_GARANTIA_DEPENDENTE_V1.json')
        self.assertEqual(before,{d['device_id'] for d in sim['scope']})
        self.assertEqual(sim['total'],12)
        for did in before:
            for n in self.inp.devices[did]['nuclei']:
                if n['role']=='GARANTIA_TRANSVERSAL':
                    self.assertTrue(all(c.get('anchor_policy')=='GARANTIA_DEPENDENTE_EXIGE_ANCORA' for c in n['contracts_by_relation']))

    def test_no_automatic_ancestry_for_equality(self):
        claim=dict(predicate='DISCRIMINAR',objects=['IGUALDADE_GENERICA'],context=['FABULA'],participants=[dict(concept='ELITE',role='ACTOR')])
        d=self.inp.devices['CF88:ART.3:INC.IV']
        for n in d['nuclei'][:2]:
            self.assertFalse(any(match_claim(self.inp,claim,c['requires']) for c in n['contracts_by_relation']))
        self.assertTrue(match_claim(self.inp,claim,d['nuclei'][-1]['contracts_by_relation'][0]['requires']))

    def test_analyzing_not_practicing(self):
        e=self.inp.works['REF-LIV-0005']['evidences'][0]
        self.assertEqual(e['claim']['predicate'],'ANALISAR')
        self.assertEqual(e['source'],self.base.works['REF-LIV-0005']['evidences'][0]['source'])
        n=self.inp.devices['CF88:ART.5:INC.III']['nuclei'][0]
        self.assertFalse(match_claim(self.inp,e['claim'],n['contracts_by_relation'][0]['requires']))
        self.assertTrue(match_claim(self.inp,e['claim'],n['contracts_by_relation'][-1]['requires']))

    def test_labels_separate_and_provenance_retained(self):
        old=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json');new=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1.json')
        self.assertEqual([key(r) for r in old['pairs']],[key(r) for r in new['pairs']])
        for a,b in zip(old['pairs'],new['pairs']):
            self.assertEqual(a['label'],b['rotulo_historico']);self.assertEqual(a['provenance'],b['provenance'])
        r=next(p for p in new['pairs'] if key(p)==('CF88:ART.5:INC.LV','REF-FIL-0001'))
        self.assertEqual((r['rotulo_historico'],r['rotulo_adjudicado_v1']),('APROVAR','REJEITAR'))

    def test_scope_technical_and_conditional(self):
        tech=load(ROOT/'06_BENCHMARKS/OITO_LACUNAS_TECNICAS_R1D.json')
        old=load(ROOT/'00_CHECKPOINTS/R1C_GATE_DECISION.json')['curation_blocking_cases']
        self.assertEqual({key(r) for r in old},{key(r) for r in tech['cases']})
        self.assertTrue(all(r['research_rounds']<=1 and r['research_closed'] for r in tech['cases']))
        human=load(ROOT/'06_BENCHMARKS/ADJUDICACAO_HUMANA_R1C_V1.json')['cases']
        for r in human:
            if r['decisao']=='ROTA_EDITORIAL_AUTORIZADA_CONDICIONALMENTE':self.assertEqual(r['rotulo_adjudicado_v1'],'EVIDENCIA_INSUFICIENTE')

    def test_deterministic_loader_and_no_label_features(self):
        self.assertEqual(self.inp.hash,load_canonical().hash)
        def check(v):
            if isinstance(v,dict):
                self.assertFalse(set(v)&{'rotulo_historico','rotulo_adjudicado_v1','human_label','expected_label'})
                for a in v.values():check(a)
            elif isinstance(v,list):
                for a in v:check(a)
        check(self.inp.data)


if __name__=='__main__':unittest.main()
