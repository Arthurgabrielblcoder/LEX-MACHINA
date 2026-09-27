"""Exactly one R1D known-pair proof pass, after freeze. Labels only score output."""
import sys
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'05_COMPILADOR'))
from canonical_input_r1d import load_canonical
from proof_compiler_v2 import run_pairs, rank_select
from proof_compiler_r1 import load, file_hash, require, digest
from r1d_support import ROOT, now, write, key, metric, integrity


def verify_freeze():
    freeze=load(ROOT/'00_CHECKPOINTS/R1D_ADJUDICADA_FREEZE.json')
    for f in freeze['files']:
        require(file_hash(ROOT/f['path'])==f['sha256'],'Frozen artifact changed: '+f['path'])
    return freeze


def matrix(rows, field='metric'):
    counts=Counter(r[field] for r in rows)
    out={k:counts[k] for k in ['TP','FP','TN','FN','NAO_AVALIAVEL']}
    out['precision']=counts['TP']/(counts['TP']+counts['FP']) if counts['TP']+counts['FP'] else None
    out['recall']=counts['TP']/(counts['TP']+counts['FN']) if counts['TP']+counts['FN'] else None
    out['binary_total']=sum(counts[k] for k in ['TP','FP','TN','FN'])
    return out


def run():
    freeze=verify_freeze()
    require(integrity()['passed'],'Historical integrity failed')
    inp=load_canonical()
    require(inp.hash==freeze['input_hash'],'Wrong frozen input')
    ledger=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1.json')
    prior=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1C.json')
    old={key(r):r for r in prior['cases']}
    hist_path=ROOT.parent/'LEX_MACHINA_REFERENCIAS_TESTE_COMPLETO_ALPHA3_V1/RESULTADO_COMPLETO_ALPHA3.json'
    historical=load(hist_path)['candidatos']
    scores={(r['dispositivo_id'],r['obra_id']):r['score_alpha3'] for r in historical}
    # Exclusive creation is a hard repeat guard even if an interrupted run did not finish.
    write('00_CHECKPOINTS/R1D_REGRESSION_STARTED.json',dict(at=now(),input_hash=inp.hash,scope=len(ledger['pairs']),max_runs=1))
    proofs=run_pairs(inp,ledger['pairs'])
    frozen_proofs=dict(schema='R1D_CANONICAL_PROOFS',input_hash=inp.hash,rows=proofs,at=now())
    write('06_BENCHMARKS/PROVAS_EXPANSAO_R1D.json',frozen_proofs)
    scored=rank_select(inp,proofs,scores)
    rows=[]
    for m,r in zip(ledger['pairs'],scored):
        rows.append(dict(device_id=r['device_id'],work_id=r['work_id'],obra=inp.works[r['work_id']]['nome'],
            rotulo_historico=m['rotulo_historico'],rotulo_adjudicado_v1=m['rotulo_adjudicado_v1'],
            metric=metric(m['rotulo_adjudicado_v1'],r['state']),historical_metric=metric(m['rotulo_historico'],r['state']),
            r1c_metric=old[key(r)]['metric'],r1c_state=old[key(r)]['admissibility'],admissibility=r['state'],
            nature=sorted({p['relation'] for p in r['proofs']}),object_reached=sorted({p['object_reached'] for p in r['proofs']}),
            evidence_ids=sorted({e for p in r['proofs'] for e in p['evidence_ids']}),candidate_retrieval=r['retrieved'],
            evidence_availability=r['evidence_availability'],editorial_score=r['editorial_score'],final_selection=None,
            proof_digest=digest(r['proofs']),annotation_status=r['annotation_status']))
    by={key(r):r for r in rows}; groups={}
    for name,items in ledger['groups'].items():
        cases=[]
        for m in items:
            r=by[key(m)]
            cases.append(dict(case_id=m['case_id'],device_id=r['device_id'],work_id=r['work_id'],state=r['admissibility'],
                rotulo_historico=m['rotulo_historico'],rotulo_adjudicado_v1=m['rotulo_adjudicado_v1'],
                metric=metric(m['rotulo_adjudicado_v1'],r['admissibility']),historical_metric=metric(m['rotulo_historico'],r['admissibility'])))
        groups[name]=dict(total=len(cases),counts=matrix(cases),historical_counts=matrix(cases,'historical_metric'),cases=cases)
    report=dict(schema='REGRESSAO_COMPLETA_EXPANSION_R1D_ADJUDICADA',at=now(),input_hash=inp.hash,
        label_sha256=file_hash(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1.json'),
        proof_sha256=file_hash(ROOT/'06_BENCHMARKS/PROVAS_EXPANSAO_R1D.json'),freeze_sha256=file_hash(ROOT/'00_CHECKPOINTS/R1D_ADJUDICADA_FREEZE.json'),
        runs=1,total=len(rows),matrix=matrix(rows),historical_label_matrix=matrix(rows,'historical_metric'),
        state_counts=dict(Counter(r['admissibility'] for r in rows)),groups=groups,cases=rows,
        excluded=[r for r in rows if r['metric']=='NAO_AVALIAVEL'],
        new_admissions=[r for r in rows if r['admissibility']=='ADMISSIVEL' and r['r1c_state']!='ADMISSIVEL'],
        lost_admissions=[r for r in rows if r['admissibility']!='ADMISSIVEL' and r['r1c_state']=='ADMISSIVEL'],
        caveats=['Benchmark de desenvolvimento conhecido; não estimativa de generalização.',
                 'Abstenção não é incompatibilidade. Insuficientes e pendentes adjudicados excluídos da matriz binária.',
                 'Matriz histórica paralela conserva denominadores originais e explicita perdas de TP.',
                 'Grupos se sobrepõem e conservam rótulos de origem para diagnóstico histórico.'])
    write('06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D.json',report)
    write('00_CHECKPOINTS/R1D_REGRESSION_COMPLETE.json',dict(at=now(),input_hash=inp.hash,runs=1,
        matrix=report['matrix'],historical_label_matrix=report['historical_label_matrix']))
    print(report['matrix']);print('Historical sensitivity',report['historical_label_matrix'])
    print({k:v['counts'] for k,v in groups.items()})


if __name__=='__main__':run()
