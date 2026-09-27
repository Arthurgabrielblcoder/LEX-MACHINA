"""R1C artifact/invariant checks only: no old or new regression is executed."""
import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'05_COMPILADOR'))
from canonical_input_r1b import load_canonical as load_base
from canonical_input_r1c import load_canonical
from prepare_r1c_data import contracts, invariants
from proof_compiler_r1 import load, digest, file_hash, source_hash, serialized

class R1CArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=load_base();cls.inp=load_canonical()
        cls.proof=load(ROOT/'06_BENCHMARKS/PROVAS_EXPANSAO_R1C.json')
        cls.freeze=load(ROOT/'00_CHECKPOINTS/EXPANSION_R1C_FREEZE.json')
        cls.reg=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1C.json')
        cls.old=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1B.json')
    def test_01_scope(self):
        self.assertEqual((len(self.inp.works),len(self.inp.devices)),(69,3461))
    def test_02_contracts(self):
        self.assertEqual(contracts(self.base),contracts(self.inp))
    def test_03_ontology(self):
        self.assertEqual(self.base.data['ontology'],self.inp.data['ontology'])
    def test_04_sources_and_catalog(self):
        invariants(self.base,self.inp)
    def test_05_baseline_hash(self):
        self.assertEqual(self.base.hash,'3401d086d8a68e7b61ac9456732d133a6d61a00f2ff5c94ce03f589519cdcc91')
    def test_06_inventory_preserved(self):
        inv=load(ROOT/'06_BENCHMARKS/INVENTARIO_OPERACIONAL_105_R1C.json')
        self.assertEqual(len(inv['rows']),105)
        self.assertEqual(len({r['pair_id'] for r in inv['rows']}),105)
    def test_07_triage_complete(self):
        t=load(ROOT/'06_BENCHMARKS/TRIAGEM_RECUPERABILIDADE_105_R1C.json')
        self.assertEqual(sum(t['counts'].values()),105)
        self.assertEqual(sum(r['pesquisa_externa_autorizada'] for r in t['rows']),22)
    def test_08_52_audited(self):
        a=load(ROOT/'06_BENCHMARKS/AUDITORIA_52_REPRESENTACOES_R1C.json')
        self.assertEqual(len(a['rows']),52)
        self.assertEqual(len({r['dispositivo'] for r in a['rows']}),36)
    def test_09_24_proposals(self):
        a=load(ROOT/'06_BENCHMARKS/AUDITORIA_24_PROPOSTAS_R1C.json')
        self.assertEqual(len(a['rows']),24)
        self.assertEqual(a['counts'],dict(VALIDADA=18,INSUFICIENTE=6,CONTRADITA=0,PROPOSTA=0))
    def test_10_17_sources(self):
        a=load(ROOT/'06_BENCHMARKS/AUDITORIA_17_FONTES_R1C.json')
        self.assertEqual(len(a['rows']),17)
        self.assertEqual((a['resolvidas'],a['nao_resolvidas']),(8,9))
    def test_11_adjudications(self):
        a=load(ROOT/'06_BENCHMARKS/CONTRATOS_12_PARA_ADJUDICACAO.json')
        self.assertEqual(len(a['cases']),12)
        self.assertTrue(all(r['adjudicacao']=='PENDENTE_HUMANA' for r in a['cases']))
    def test_12_fp_diagnoses(self):
        a=load(ROOT/'06_BENCHMARKS/DIAGNOSTICO_FP_4_PARA_ADJUDICACAO.json')
        self.assertEqual(len(a['cases']),4)
        self.assertTrue(all(not r['alteracao_implementada'] for r in a['cases']))
    def test_13_validated_source_cards(self):
        for w in self.inp.works.values():
            for e in w['evidences']:
                if e['state']=='VALIDADA':
                    self.assertEqual(e['source']['hash'],source_hash(e['source']))
                    self.assertTrue(e['transposition_limits'])
    def test_14_old_validated_unchanged(self):
        for w in self.base.works.values():
            current={e['evidence_id']:e for e in self.inp.works[w['work_id']]['evidences']}
            for e in w['evidences']:
                if e['state']=='VALIDADA':self.assertEqual(e,current[e['evidence_id']])
    def test_15_representation_freeze(self):
        freeze=load(ROOT/'00_CHECKPOINTS/R1C_REPRESENTATIONS_FROZEN.json')
        self.assertEqual(freeze['canonical_input_hash'],self.inp.hash)
        for r in freeze['hashes']:self.assertEqual(file_hash(ROOT/r['path']),r['sha256'],r['path'])
    def test_16_proof_freeze(self):
        self.assertEqual(digest(self.proof),self.freeze['proof_content_hash'])
        self.assertEqual(self.proof['input_hash'],self.inp.hash)
    def test_17_scope_398(self):
        master=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json')
        keys=lambda xs:[(r['device_id'],r['work_id']) for r in xs]
        self.assertEqual(keys(self.proof['rows']),keys(master['pairs']))
        self.assertEqual(len(self.proof['rows']),398)
    def test_18_regression_394_valid(self):
        c=self.reg['counts'];self.assertEqual(sum(c[k] for k in ['TP','FP','TN_NAO_PUBLICADO','FN']),394)
        self.assertEqual(c['NAO_AVALIAVEL'],4)
    def test_19_all_prior_tp_preserved(self):
        new={(r['device_id'],r['work_id']):r['metric'] for r in self.reg['cases']}
        self.assertTrue(all(new[(r['device_id'],r['work_id'])]=='TP' for r in self.old['cases'] if r['metric']=='TP'))
    def test_20_fp_identical(self):
        ids=lambda x:{(r['device_id'],r['work_id']) for r in x['cases'] if r['metric']=='FP'}
        self.assertEqual(ids(self.old),ids(self.reg));self.assertEqual(len(ids(self.reg)),4)
    def test_21_recent_negatives(self):
        g=self.reg['groups']['recent60']['counts']
        self.assertEqual(g.get('FP',0),0);self.assertEqual(g['TN_NAO_PUBLICADO'],35)
    def test_22_recent_twenty(self):
        self.assertEqual(self.reg['groups']['recent20']['counts'],{'TN_NAO_PUBLICADO':18,'TP':2})
    def test_23_mechanism_controls(self):
        self.assertEqual(self.reg['groups']['mechanisms15']['counts'],{'TP':12,'FN':3})
        self.assertEqual(self.reg['groups']['negatives10']['counts'],{'TN_NAO_PUBLICADO':10})
    def test_24_residual_causal_audit(self):
        a=load(ROOT/'06_BENCHMARKS/DECOMPOSICAO_CAUSAL_FN_R1C.json')
        self.assertEqual(len(a['cases']),93);self.assertEqual(sum(a['counts'].values()),93)
        self.assertEqual({(r['device_id'],r['work_id']) for r in a['cases']},{(r['device_id'],r['work_id']) for r in self.reg['cases'] if r['metric']=='FN'})
    def test_25_no_selection_claim(self):
        self.assertTrue(all(r['final_selection'] is None for r in self.reg['cases']))
    def test_26_input_determinism_not_full_run(self):
        self.assertEqual(self.inp.hash,load_canonical().hash)
        self.inp.assert_unchanged()
    def test_27_holdout_hash_only(self):
        self.assertEqual(file_hash(ROOT/'06_BENCHMARKS/HOLDOUT_V2_BLIND.json'),'b71a87a8292ac621a209201e2082935813563f8002f9203430af3b781414adf1')
    def test_28_old_artifacts_preserved(self):
        for p in load(ROOT/'00_CHECKPOINTS/FINAL_ARTIFACT_MANIFEST.json')['files']:
            if p['path'] not in ['00_CHECKPOINTS/RESUME_STATE.json','00_CHECKPOINTS/RESUME_INSTRUCTIONS.md']:
                self.assertEqual(file_hash(ROOT/p['path']),p['sha256'],p['path'])
    def test_29_all_proofs_use_validated_evidence(self):
        for r in self.proof['rows']:
            e={e['evidence_id']:e for e in self.inp.works[r['work_id']]['evidences']}
            for p in r['proofs']:
                self.assertTrue(all(e[i]['state']=='VALIDADA' for i in p['evidence_ids']))
    def test_30_no_new_nucleus_or_equivalence(self):
        self.assertEqual(sum(len(d['nuclei']) for d in self.inp.devices.values()),233)
        self.assertEqual(self.base.synonyms,self.inp.synonyms)
    def test_31_one_regression_checkpoint(self):
        self.assertEqual(load(ROOT/'00_CHECKPOINTS/R1C_REGRESSION_COMPLETE.json')['regression_runs'],1)
    def test_32_historical_scores_not_recomputed(self):
        self.assertEqual(self.old['historical_sha256'],self.reg['historical_sha256'])

if __name__=='__main__':unittest.main()
