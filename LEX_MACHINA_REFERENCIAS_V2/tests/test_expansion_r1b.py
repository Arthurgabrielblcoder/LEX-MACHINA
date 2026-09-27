"""Current integration tests use the actual R1B input, never synthetic fixtures."""
import sys
import unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for folder in ('05_COMPILADOR','06_BENCHMARKS','07_EXECUCAO_COMPLETA'):
    sys.path.insert(0,str(ROOT/folder))
from canonical_input_r1b import load_canonical
from canonical_input_r1 import load_canonical as load_r1
from proof_compiler_r1 import load, digest, file_hash, lexical_phrase, ContractError
from proof_compiler_v2 import evaluate_pair, run_pairs, rank_select
import run_regression_r1b
import runner_integral
from reserve_holdout import reserve


class CurrentR1B(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inp=load_canonical(); cls.old=load_r1()
        cls.freeze=load(ROOT/'00_CHECKPOINTS/EXPANSION_R1B_FREEZE.json')
        cls.proofs=load(ROOT/'06_BENCHMARKS/PROVAS_EXPANSAO_R1B.json')
        cls.by={(p['device_id'],p['work_id']):p for p in cls.proofs['rows']}
        cls.reg=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1B.json')
        cls.master=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json')

    def test_01_canonical_hash(self): self.assertEqual(self.inp.hash,self.freeze['canonical_input_hash'])
    def test_02_frozen_parts(self):
        for h in self.freeze['hashes']:
            self.assertEqual(file_hash(ROOT/h['path']),h['sha256'])
    def test_03_proof_content_hash(self): self.assertEqual(digest(self.proofs),self.freeze['proof_content_hash'])
    def test_04_same_loader_regression(self): self.assertIs(run_regression_r1b.load_canonical,load_canonical)
    def test_05_same_loader_integral(self): self.assertIs(runner_integral.load_canonical,load_canonical)
    def test_06_universe_and_ids(self):
        self.assertEqual((len(self.inp.devices),len(self.inp.works)),(3461,69))
        self.assertEqual(self.inp.devices.keys(),self.old.devices.keys())
        self.assertEqual(self.inp.works.keys(),self.old.works.keys())
    def test_07_no_original_device_changed(self):
        for did,d in self.old.devices.items():
            if d['nuclei']: self.assertEqual(d,self.inp.devices[did])
    def test_08_one_new_representation_only(self):
        changed=[did for did in self.inp.devices if self.inp.devices[did]!=self.old.devices[did]]
        self.assertEqual(changed,['CF88:ART.5:INC.XV'])
    def test_09_three_dossiers_only(self):
        self.assertEqual({w for w in self.inp.works if self.inp.works[w]!=self.old.works[w]},
                         {'REF-LIV-0001','REF-SER-0002','EXP-LIV-008'})
    def test_10_no_proposal_promoted(self):
        for wid,w in self.old.works.items():
            after={e['evidence_id']:e for e in self.inp.works[wid]['evidences']}
            for e in w['evidences']:
                self.assertEqual(e['state'],after[e['evidence_id']]['state'])
    def test_11_source_cards_preserved(self):
        for wid,w in self.old.works.items():
            after={e['evidence_id']:e for e in self.inp.works[wid]['evidences']}
            for e in w['evidences']: self.assertEqual(e['source'],after[e['evidence_id']]['source'])
    def test_12_ontology_unchanged(self): self.assertEqual(self.inp.data['ontology'],self.old.data['ontology'])
    def test_13_no_substring_proof(self):
        for token,text in [('raça','reparação administração separação'),('voto','devoto'),('ato','contrato')]:
            self.assertFalse(lexical_phrase(token,text))
    def test_14_ancestor_never_identity(self):
        for e in self.inp.data['ontology']['hierarchy']:
            self.assertFalse(self.inp.same_concept(e['parent'],e['child']))
    def test_15_non_equivalences(self):
        for a,b in self.inp.data['ontology']['non_equivalences']:
            self.assertFalse(self.inp.same_concept(a,b))
        self.assertFalse(self.inp.same_concept('PRIVACIDADE','COMUNICACAO_PRIVADA'))
        self.assertFalse(self.inp.same_concept('IGUALDADE_GENERO','AUTONOMIA_REPRODUTIVA'))
    def test_16_no_artificial_adapter(self):
        self.assertNotIn('features_simulacao',str(self.inp.data))
        self.assertNotIn('expected_label',str(self.inp.data))
    def test_17_mechanisms_runtime_proof_parity(self):
        for group in ('mechanisms15','negatives10'):
            pairs=self.master['groups'][group]
            actual=run_pairs(self.inp,pairs)
            self.assertEqual(actual,[self.by[(p['device_id'],p['work_id'])] for p in pairs])
    def test_18_mechanism_states(self):
        rows=[self.by[(p['device_id'],p['work_id'])] for p in self.master['groups']['mechanisms15']]
        self.assertEqual(Counter(r['state'] for r in rows),{'ADMISSIVEL':11,'EVIDENCIA_INSUFICIENTE':4})
        self.assertTrue(all(r['retrieved'] for r in rows))
    def test_19_negatives_are_abstentions(self):
        rows=[self.by[(p['device_id'],p['work_id'])] for p in self.master['groups']['negatives10']]
        self.assertTrue(all(r['state']=='EVIDENCIA_INSUFICIENTE' for r in rows))
    def test_20_cidadania_nature(self):
        r=evaluate_pair(self.inp,'CF88:ART.7:INC.IV','EXP-LIV-004')
        self.assertEqual(r['state'],'ADMISSIVEL')
        self.assertEqual({p['relation'] for p in r['proofs']},{'CONTEXTUALIZACAO_HISTORICA'})
    def test_21_borderlands_source(self):
        w=next(w for w in self.inp.works.values() if 'Borderlands' in w['nome'])
        rows=[r for r in self.proofs['rows'] if r['work_id']==w['work_id'] and r['state']=='ADMISSIVEL']
        self.assertTrue(rows)
        valid={e['evidence_id'] for e in w['evidences'] if e['state']=='VALIDADA'}
        self.assertTrue(all(set(p['evidence_ids'])<=valid for r in rows for p in r['proofs']))
    def test_22_holdout_exclusion(self):
        h=load(ROOT/'06_BENCHMARKS/HOLDOUT_V2_BLIND.json')
        keys={(p['device_id'],p['work_id']) for p in h['pairs']}
        known={(p['device_id'],p['work_id']) for p in self.master['pairs']}
        self.assertEqual(len(keys),120); self.assertFalse(keys & known)
        self.assertTrue(all(p['human_label'] is None for p in h['pairs']))
    def test_23_holdout_determinism(self): self.assertEqual(reserve(),load(ROOT/'06_BENCHMARKS/HOLDOUT_V2_BLIND.json'))
    def test_24_conflicts_excluded(self):
        invalid=[r for r in self.reg['cases'] if r['human_label'] not in {'APROVAR','REJEITAR'}]
        self.assertEqual(len(invalid),4)
        self.assertTrue(all(r['metric']=='NAO_AVALIAVEL' for r in invalid))
    def test_25_gate_blocks_final(self):
        with self.assertRaises(ContractError): next(runner_integral.iter_full())
    def test_26_no_rc_or_idx(self):
        self.assertFalse(list(ROOT.rglob('*.IDX')))
        self.assertFalse(any('CF_REFERENCIAS_V2_RC1' in p.name for p in (ROOT/'08_RELEASE_CANDIDATE').iterdir()))
    def test_27_canonical_determinism(self): self.assertEqual(self.inp.hash,load_canonical().hash)
    def test_28_pair_determinism(self):
        pair=dict(device_id='CF88:ART.5:INC.XV',work_id='REF-JOG-0001')
        self.assertEqual(digest(evaluate_pair(self.inp,**pair)),digest(evaluate_pair(self.inp,**pair)))
    def test_29_scores_do_not_rescue(self):
        r=evaluate_pair(self.inp,'CF88:ART.37:INC.II','REF-JOG-0001')
        out=rank_select(self.inp,[r],{(r['device_id'],r['work_id']):10})[0]
        self.assertEqual(out['state'],'EVIDENCIA_INSUFICIENTE')
        self.assertIsNone(out['editorial_score']);self.assertFalse(out['selected'])
    def test_30_no_tp_lost_r1_to_r1b(self):
        old=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1.json')['cases']
        now={(r['device_id'],r['work_id']):r for r in self.reg['cases']}
        self.assertTrue(all(now[(r['device_id'],r['work_id'])]['metric']=='TP' for r in old if r['metric']=='TP'))
    def test_31_every_fn_has_cause(self):
        c=load(ROOT/'06_BENCHMARKS/DECOMPOSICAO_CAUSAL_FN_R1B.json')['cases']
        self.assertEqual({(p['device_id'],p['work_id']) for p in c},
                         {(r['device_id'],r['work_id']) for r in self.reg['cases'] if r['metric']=='FN'})
    def test_32_original_proof_interpreter(self):
        f=load(ROOT/'00_CHECKPOINTS/EXPANSION_R1_PROOFS_FREEZE.json')
        for item in f['hashes']: self.assertEqual(file_hash(ROOT/item['path']),item['sha256'])


if __name__=='__main__': unittest.main()
