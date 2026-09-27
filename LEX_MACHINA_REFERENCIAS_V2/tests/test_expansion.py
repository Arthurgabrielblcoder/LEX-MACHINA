import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'05_COMPILADOR'))
from canonical_input import load_canonical
from proof_compiler_r1 import ContractError, CanonicalInput, digest, load, file_hash
from proof_compiler_v2 import evaluate_pair, run_pairs, rank_select


class Expansion(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.inp=load_canonical()

    def test_01_universe(self): self.assertEqual((len(self.inp.devices),len(self.inp.works)),(3461,69))
    def test_02_priority(self):
        ids=load(ROOT/'02_DISPOSITIVOS/UNIVERSO_PRIORITARIO_V2.json')['ids']
        self.assertEqual(len(ids),210)
        self.assertTrue(all(self.inp.devices[d]['nuclei'] for d in ids))
    def test_03_exact_source(self):
        src=load(ROOT.parent/'CF_SEGMENTADA_V2/CF_DISPOSITIVOS_LIMPOS.json')['dispositivos']
        self.assertTrue(all(self.inp.devices[d['chave_dispositivo']]['text']==d['texto'] for d in src))
    def test_04_cf_adct(self):
        self.assertEqual(sum(d.startswith('CF88:') for d in self.inp.devices),2656)
        self.assertEqual(sum(d.startswith('ADCT:') for d in self.inp.devices),805)
    def test_05_quarantine(self):
        self.assertEqual(evaluate_pair(self.inp,'CF88:ART.37:INC.XVI:AL.c','EXP-FIL-006')['state'],'FONTE_EM_REVISAO')
    def test_06_all_works_have_dossier(self): self.assertTrue(all(w['evidences'] for w in self.inp.works.values()))
    def test_07_unrepresented_never_inherits(self):
        d=next(k for k,v in self.inp.devices.items() if not v['nuclei'] and v['text_identity_status']!='FONTE_EM_REVISAO')
        self.assertEqual(evaluate_pair(self.inp,d,'REF-LIV-0001')['state'],'EVIDENCIA_INSUFICIENTE')
    def test_08_pilot_parity(self):
        old=load(ROOT/'06_BENCHMARKS/PROVAS_PILOTO_V2_R1.json')['pairs']
        self.assertTrue(all(evaluate_pair(self.inp,r['device_id'],r['work_id'])['state']==r['state'] for r in old))
    def test_09_partial_batch_parity(self):
        ps=[dict(device_id='CF88:ART.5:INC.LIV',work_id='REF-FIL-0001')]
        self.assertEqual(run_pairs(self.inp,ps),[evaluate_pair(self.inp,**ps[0])])
    def test_10_score_after_proof(self):
        r=evaluate_pair(self.inp,'CF88:ART.198:PAR.7','EXP-FIL-006')
        out=rank_select(self.inp,[r],{(r['device_id'],r['work_id']):10})[0]
        self.assertIsNone(out['editorial_score']); self.assertFalse(out['selected'])
    def test_11_selection_limit(self):
        rs=[evaluate_pair(self.inp,'CF88:ART.5:INC.XLII',w) for w in self.inp.works]
        out=rank_select(self.inp,rs,{(r['device_id'],r['work_id']):9 for r in rs},2)
        self.assertLessEqual(sum(r['selected'] for r in out),2)
    def test_12_selection_admissible_only(self):
        rs=[evaluate_pair(self.inp,'CF88:ART.5:INC.XLII',w) for w in self.inp.works]
        out=rank_select(self.inp,rs,{(r['device_id'],r['work_id']):10 for r in rs})
        self.assertTrue(all(r['state']=='ADMISSIVEL' for r in out if r['selected']))
    def test_13_missing_score_no_invention(self):
        r=evaluate_pair(self.inp,'CF88:ART.5:INC.LIV','REF-FIL-0001')
        self.assertIsNone(rank_select(self.inp,[r],{})[0]['editorial_score'])
    def test_14_no_empty_semantic_diagnosis_claim(self):
        empty=[n for d in self.inp.devices.values() for n in d['nuclei'] if not n['proposition']['objetos']]
        self.assertEqual(len(empty),8); self.assertTrue(all(n['state']=='PROPOSTA' for n in empty))
    def test_15_paperwork_not_employment(self):
        self.assertEqual(evaluate_pair(self.inp,'CF88:ART.37:INC.II','REF-JOG-0001')['state'],'EVIDENCIA_INSUFICIENTE')
    def test_16_data_not_interception(self):
        self.assertEqual(evaluate_pair(self.inp,'CF88:ART.5:INC.XII','REF-DOC-0001')['state'],'EVIDENCIA_INSUFICIENTE')
    def test_17_stasi_documentary_support(self):
        self.assertEqual(evaluate_pair(self.inp,'CF88:ART.5:INC.XII','REF-FIL-0003')['state'],'ADMISSIVEL')
    def test_18_deterministic_selection(self):
        rs=[evaluate_pair(self.inp,'CF88:ART.5:INC.XLII',w) for w in self.inp.works]
        scores={(r['device_id'],r['work_id']):8 for r in rs}
        self.assertEqual(rank_select(self.inp,rs,scores),rank_select(self.inp,rs,scores))
    def test_19_proposed_sources_not_validated(self):
        self.assertTrue(any(e['state']=='PROPOSTA' for w in self.inp.works.values() for e in w['evidences']))
    def test_20_freeze_input_hash(self):
        f=load(ROOT/'00_CHECKPOINTS/EXPANSION_PROOFS_FREEZE.json')
        self.assertEqual(self.inp.hash,f['canonical_input_hash'])


if __name__=='__main__': unittest.main()
