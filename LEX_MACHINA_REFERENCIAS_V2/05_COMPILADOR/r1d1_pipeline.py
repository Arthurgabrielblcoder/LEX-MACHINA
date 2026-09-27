"""Frozen R1D1 workflow. Same interpreter and ranker; labels score output only.

Stages are exclusive and resumable by artifact, not repeatable evaluations.
No old regression is invoked; no holdout JSON is parsed.
"""
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from canonical_input_r1d import load_canonical as load_base
from canonical_input_r1d1 import load_canonical
from proof_compiler_r1 import load, file_hash, digest, require
from proof_compiler_v2 import run_pairs, iter_exhaustive, rank_select
from r1d_support import ROOT, now, write, key, metric, integrity as r1d_integrity

LABELS='06_BENCHMARKS/HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1.json'
TARGET=('CF88:ART.205','EXP-LIV-004')
HISTORICAL=ROOT.parent/'LEX_MACHINA_REFERENCIAS_TESTE_COMPLETO_ALPHA3_V1/RESULTADO_COMPLETO_ALPHA3.json'


def check_manifest(path):
    manifest=load(ROOT/path)
    changed=[r['path'] for r in manifest['files'] if not (ROOT/r['path']).exists() or file_hash(ROOT/r['path'])!=r['sha256']]
    return dict(total=len(manifest['files']),changed=changed,passed=not changed)


def integrity():
    old=r1d_integrity()
    frozen=check_manifest('00_CHECKPOINTS/R1D_ADJUDICADA_FREEZE.json')
    before=check_manifest('00_CHECKPOINTS/R1D1_INTEGRITY_BEFORE.json')
    return dict(at=now(),protected545=dict(total=old['protected_checked'],changed=old['protected_changed']),
        previous162=dict(total=old['preexisting_v2_checked'],changed=old['preexisting_v2_changed']),r1d_freeze187=frozen,
        all_preexisting_r1d=before,holdout_sha256=old['holdout_sha256'],holdout_content_opened=False,
        passed=old['passed'] and frozen['passed'] and before['passed'])


def freeze_verify():
    result=check_manifest('00_CHECKPOINTS/R1D1_INPUT_FREEZE.json')
    require(result['passed'],'R1D1 frozen input/code changed')
    return load(ROOT/'00_CHECKPOINTS/R1D1_INPUT_FREEZE.json')


def matrix(rows,field='metric'):
    counts=Counter(r[field] for r in rows)
    out={k:counts[k] for k in ['TP','FP','TN','FN','NAO_AVALIAVEL']}
    out.update(precision=counts['TP']/(counts['TP']+counts['FP']) if counts['TP']+counts['FP'] else None,
        recall=counts['TP']/(counts['TP']+counts['FN']) if counts['TP']+counts['FN'] else None,
        binary_total=sum(counts[k] for k in ['TP','FP','TN','FN']))
    return out


def freeze():
    inp=load_canonical();base=load_base();integ=integrity()
    require(integ['passed'],'Integrity failed')
    sim=load(ROOT/'06_BENCHMARKS/SIMULACAO_ART205_R1D1.json')
    require(sim['safe'] and sim['input_hash']==inp.hash,'Unsafe simulation')
    d0=base.devices['CF88:ART.205'];d1=inp.devices['CF88:ART.205']
    structural=dict(only_art205_changed=all(base.devices[d]==inp.devices[d] for d in base.devices if d!='CF88:ART.205'),
        works_unchanged=base.data['works']==inp.data['works'],ontology_unchanged=base.data['ontology']==inp.data['ontology'],
        no_new_nucleus=len(d0['nuclei'])==len(d1['nuclei']),work_finality_identical=d0['nuclei'][1]==d1['nuclei'][1],
        dependencies_unchanged=all(a['depends_on']==b['depends_on'] and a['role']==b['role'] and a['proposition']==b['proposition'] for a,b in zip(d0['nuclei'],d1['nuclei'])),
        historical_contract_requirements_identical=d0['nuclei'][2]['contracts_by_relation'][1]['requires']==d1['nuclei'][0]['contracts_by_relation'][1]['requires'],
        independent_education_literal=d1['nuclei'][0]['role']=='AUTONOMO' and 'EDUCACAO' in d1['nuclei'][0]['proposition']['objetos'],
        dependent_guarantees_identical=all(d==inp.devices[d['device_id']] for d in base.devices.values() if any(n['role']=='GARANTIA_TRANSVERSAL' for n in d['nuclei'])),
        label_ledger_unchanged=file_hash(ROOT/LABELS)==load(ROOT/'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1D1.json')['label_sha256'])
    require(all(structural.values()) and all(c['passed'] for c in sim['synthetic_checks']),'Structural tests failed')
    write('00_CHECKPOINTS/TEST_RESULTS_R1D1.json',dict(at=now(),structural_checks=structural,synthetic_checks=sim['synthetic_checks'],
        tests_run=len(structural)+len(sim['synthetic_checks']),passed=True,scope='Testes de dados e controles sintéticos da simulação; nenhuma regressão histórica.'))
    files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=file_hash(p),bytes=p.stat().st_size) for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    write('00_CHECKPOINTS/R1D1_INPUT_FREEZE.json',dict(at=now(),input_hash=inp.hash,files=files,total=len(files),self_excluded=True,
        scope='Representação, evidências, código, política e ledger antes da prova/regressão; não avalia holdout.',
        gate_criteria=['Cidadania com prova N1','FP zero','garantia dependente idêntica','nenhuma transição fora do art.205',
          '35 negativos recentes e 10 pareados protegidos','demais controles preservados de R1D','integridade e paridade válidas']))
    print('INPUT FROZEN',len(files),inp.hash,flush=True)


def proofs():
    freeze=freeze_verify();inp=load_canonical()
    require(freeze['input_hash']==inp.hash,'Wrong input')
    ledger=load(ROOT/LABELS)
    # Scope projection deliberately excludes labels and annotations.
    pairs=[dict(device_id=p['device_id'],work_id=p['work_id']) for p in ledger['pairs']]
    write('00_CHECKPOINTS/R1D1_PROOF_PASS_STARTED.json',dict(at=now(),input_hash=inp.hash,pairs=len(pairs),max_runs=1))
    rows=run_pairs(inp,pairs)
    result=dict(schema='R1D1_PRE_REGRESSION_PROOFS',input_hash=inp.hash,rows=rows)
    write('06_BENCHMARKS/PROVAS_EXPANSAO_R1D1.json',result)
    write('00_CHECKPOINTS/R1D1_PROOFS_FREEZE.json',dict(at=now(),input_hash=inp.hash,pairs=len(rows),
        proof_sha256=file_hash(ROOT/'06_BENCHMARKS/PROVAS_EXPANSAO_R1D1.json'),proof_digest=digest(result),
        input_freeze_sha256=file_hash(ROOT/'00_CHECKPOINTS/R1D1_INPUT_FREEZE.json'),label_sha256=file_hash(ROOT/LABELS),regression_executed=False))
    print('PROOFS FROZEN',len(rows),flush=True)


def regression():
    freeze_verify();inp=load_canonical();pf=load(ROOT/'00_CHECKPOINTS/R1D1_PROOFS_FREEZE.json')
    p=load(ROOT/'06_BENCHMARKS/PROVAS_EXPANSAO_R1D1.json')
    require(pf['input_hash']==p['input_hash']==inp.hash and digest(p)==pf['proof_digest'],'Frozen proof mismatch')
    require(file_hash(ROOT/LABELS)==pf['label_sha256'],'Labels changed')
    ledger=load(ROOT/LABELS);prior=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D.json')
    old={key(r):r for r in prior['cases']}
    require([key(r) for r in p['rows']]==[key(r) for r in ledger['pairs']],'Scope mismatch')
    write('00_CHECKPOINTS/R1D1_REGRESSION_STARTED.json',dict(at=now(),max_runs=1,input_hash=inp.hash))
    hist=load(HISTORICAL)['candidatos'];scores={(r['dispositivo_id'],r['obra_id']):r['score_alpha3'] for r in hist}
    scored=rank_select(inp,p['rows'],scores);rows=[]
    for m,r in zip(ledger['pairs'],scored):
        rows.append(dict(device_id=r['device_id'],work_id=r['work_id'],obra=inp.works[r['work_id']]['nome'],admissibility=r['state'],
            rotulo_adjudicado_v1=m['label'],rotulo_historico=m['rotulo_historico'],metric=metric(m['label'],r['state']),
            historical_metric=metric(m['rotulo_historico'],r['state']),r1d_state=old[key(r)]['admissibility'],
            nature=sorted({p['relation'] for p in r['proofs']}),evidence_ids=sorted({e for p in r['proofs'] for e in p['evidence_ids']}),
            nucleus_ids=sorted({p['nucleus_id'] for p in r['proofs']}),proof_digest=digest(r['proofs']),editorial_score=r['editorial_score'],final_selection=None))
    by={key(r):r for r in rows};groups={}
    for name,items in ledger['groups'].items():
        cases=[dict(device_id=m['device_id'],work_id=m['work_id'],case_id=m['case_id'],state=by[key(m)]['admissibility'],
            rotulo_adjudicado_v1=m['label'],rotulo_historico=m['rotulo_historico'],metric=metric(m['label'],by[key(m)]['admissibility']),
            historical_metric=metric(m['rotulo_historico'],by[key(m)]['admissibility'])) for m in items]
        groups[name]=dict(total=len(cases),counts=matrix(cases),historical_counts=matrix(cases,'historical_metric'),cases=cases)
    report=dict(schema='R1D1_ADJUDICATED_REGRESSION',at=now(),input_hash=inp.hash,runs=1,pairs=len(rows),matrix=matrix(rows),historical_label_matrix=matrix(rows,'historical_metric'),
        groups=groups,cases=rows,states=dict(Counter(r['admissibility'] for r in rows)),
        transitions=[r for r in rows if r['admissibility']!=r['r1d_state']],label_master_sha256=file_hash(ROOT/LABELS),
        caveats=['Conhecido/adjudicado, não cego. 23 não binários explicitamente excluídos.','Rótulos históricos somente comparação, sem reconsolidação.','Grupos se sobrepõem.'])
    write('06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D1.json',report)
    write('00_CHECKPOINTS/R1D1_REGRESSION_COMPLETE.json',dict(at=now(),input_hash=inp.hash,runs=1,matrix=report['matrix'],historical_label_matrix=report['historical_label_matrix']))
    print('REGRESSION',report['matrix'],'historical',report['historical_label_matrix'],flush=True)


def gate():
    freeze_verify();inp=load_canonical();base=load_base();integ=integrity()
    r=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D1.json');old=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D.json')
    by={key(x):x for x in r['cases']};g=r['groups'];target=by[TARGET]
    approved=load(ROOT/'06_BENCHMARKS/ADJUDICACAO_HUMANA_R1C_V1.json')['cases']+load(ROOT/'06_BENCHMARKS/CONTRATOS_ADICIONAIS_14_POS_POLITICA.json')['cases']
    checks=dict(cidadania_approved_with_main_nucleus=target['admissibility']=='ADMISSIVEL' and target['nucleus_ids']==['CF88:ART.205#N1'],
        zero_fp=r['matrix']['FP']==0,all_adjudicated_approvals_have_proof=all(by[key(a)]['admissibility']=='ADMISSIVEL' for a in approved if a['rotulo_adjudicado_v1']=='APROVAR'),
        no_unexpected_transition=all(key(x)==TARGET for x in r['transitions']),
        dependent_guarantees_unchanged=all(d==inp.devices[d['device_id']] for d in base.devices.values() if any(n['role']=='GARANTIA_TRANSVERSAL' for n in d['nuclei'])),
        scoped_simulation_safe=load(ROOT/'06_BENCHMARKS/SIMULACAO_ART205_R1D1.json')['safe'],
        recent35_protected=all(c['state']!='ADMISSIVEL' for c in g['recent60']['cases'] if c['rotulo_historico']=='REJEITAR'),
        paired10_protected=g['negatives10']['historical_counts']['TN']==10,
        recent20_preserved=g['recent20']['historical_counts']==old['groups']['recent20']['historical_counts'],
        mechanisms15_preserved=g['mechanisms15']['historical_counts']==old['groups']['mechanisms15']['historical_counts'],
        recent25_no_unexplained_loss=g['recent60']['historical_counts']==old['groups']['recent60']['historical_counts'],
        frozen_label_ledger=file_hash(ROOT/LABELS)==load(ROOT/'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1D1.json')['label_sha256'],
        integrity=integ['passed'],structural_tests=load(ROOT/'00_CHECKPOINTS/TEST_RESULTS_R1D1.json')['passed'])
    passed=all(checks.values())
    write('00_CHECKPOINTS/R1D1_GATE_DECISION.json',dict(at=now(),passed=passed,input_hash=inp.hash,checks=checks,
        decision='EXECUCAO_COMPLETA_R1D1' if passed else 'R1D1_GATE_FAILED',
        parity='Os 397 pares não alvo mantêm seus estados; paridade integral será conferida em cada execução completa.',
        recent25_policy='15/25 permanece como R1D adjudicada; não restaurar os cinco TP retirados pela política D.'))
    print('GATE',passed,checks,flush=True)


def full(run_id):
    require(run_id in [1,2],'Only two full runs authorized')
    freeze_verify();inp=load_canonical();gate=load(ROOT/'00_CHECKPOINTS/R1D1_GATE_DECISION.json')
    require(gate['passed'] and gate['input_hash']==inp.hash,'Full gate not passed')
    require(integrity()['passed'],'Historical integrity failed')
    if run_id==2:require((ROOT/'07_EXECUCAO_COMPLETA/R1D1_RUN1_SUMMARY.json').exists(),'Run1 must finish first')
    reg=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D1.json');known={key(r):r for r in reg['cases']}
    prefix=f'07_EXECUCAO_COMPLETA/R1D1_RUN{run_id}'
    write(f'00_CHECKPOINTS/R1D1_FULL_RUN{run_id}_STARTED.json',dict(at=now(),input_hash=inp.hash,expected_pairs=69*3461))
    path=ROOT/(prefix+'.jsonl.gz');require(not path.exists(),'Full output exists')
    counts=Counter();admitted=[];review=[];parity=[];total=0;retrieved=0;contracts=0;proof_count=0
    pairs_digest=hashlib.sha256();results_digest=hashlib.sha256()
    with path.open('xb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as output:
            for row in iter_exhaustive(inp):
                total+=1;retrieved+=int(row['retrieved']);counts[row['state']]+=1;proof_count+=len(row['proofs'])
                d=inp.devices[row['device_id']]
                if d['text_identity_status']!='FONTE_EM_REVISAO':contracts+=sum(len(n['contracts_by_relation']) for n in d['nuclei'])
                pairs_digest.update((row['device_id']+'\t'+row['work_id']+'\n').encode())
                line=(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
                output.write(line);results_digest.update(line)
                if row['state']=='ADMISSIVEL':admitted.append(row)
                elif row['state']=='REVISAO_EDITORIAL':review.append(row)
                if key(row) in known:
                    k=known[key(row)];parity.append(row['state']==k['admissibility'] and digest(row['proofs'])==k['proof_digest'])
                if total%50000==0:print(f'FULL RUN {run_id}: {total}/238809',flush=True)
    require(total==238809 and retrieved==total,'Incomplete Cartesian evaluation')
    require(len(parity)==398 and all(parity),'Full/known proof parity failed')
    hist=load(HISTORICAL)['candidatos'];scores={(r['dispositivo_id'],r['obra_id']):r['score_alpha3'] for r in hist}
    ranked=rank_select(inp,admitted,scores)
    write(prefix+'_ADMISSIVEIS.json',dict(input_hash=inp.hash,rows=ranked))
    write(prefix+'_REVISAO.json',dict(input_hash=inp.hash,rows=review))
    # Validate actual serialized output without executing the interpreter again.
    seen=set();stored=Counter();replay_hash=hashlib.sha256()
    with gzip.open(path,'rb') as src:
        for line in src:
            replay_hash.update(line);row=json.loads(line);k=key(row)
            require(k not in seen,'Duplicate persisted pair');seen.add(k);stored[row['state']]+=1
    require(len(seen)==total and stored==counts and replay_hash.hexdigest()==results_digest.hexdigest(),'Stored full output failed validation')
    summary=dict(schema='R1D1_FULL_CANONICAL_PASS',input_hash=inp.hash,possible_pairs=238809,evaluated_pairs=total,candidates=retrieved,
        proof_attempted_pairs=total,contract_routes_attempted=contracts,proof_routes_generated=proof_count,
        states={s:counts[s] for s in ['ADMISSIVEL','REVISAO_EDITORIAL','EVIDENCIA_INSUFICIENTE','INCOMPATIVEL','FONTE_EM_REVISAO']},
        candidate_definition='Cada combinação de obra e dispositivo foi recuperada; somente prova tipada admite.',
        attempted_definition='Uma chamada canônica por par; rotas contratuais contam contratos de núcleos em dispositivos com fonte liberada.',
        known_pair_parity=dict(total=398,equal=sum(parity)),unique_pairs=len(seen),
        pair_order_sha256=pairs_digest.hexdigest(),result_content_sha256=results_digest.hexdigest(),compressed_sha256=file_hash(path),
        admissible_sha256=file_hash(ROOT/(prefix+'_ADMISSIVEIS.json')),review_sha256=file_hash(ROOT/(prefix+'_REVISAO.json')),
        editorial_selection=sum(r['selected'] for r in ranked),admissible_unscored=sum(r['editorial_score'] is None for r in ranked),
        represented_devices=sum(bool(d['nuclei']) for d in inp.devices.values()),total_devices=3461,total_works=69)
    write(prefix+'_SUMMARY.json',summary)
    write(f'00_CHECKPOINTS/R1D1_FULL_RUN{run_id}_COMPLETE.json',dict(at=now(),summary_sha256=file_hash(ROOT/(prefix+'_SUMMARY.json')),input_hash=inp.hash))
    print('FULL COMPLETE',run_id,summary['states'],flush=True)
    if run_id==2:
        first=load(ROOT/'07_EXECUCAO_COMPLETA/R1D1_RUN1_SUMMARY.json')
        require(first==summary,'Non-deterministic full output')
        write('00_CHECKPOINTS/DETERMINISMO_R1D1.json',dict(at=now(),passed=True,full_runs=2,possible_pairs_per_run=238809,
            checks=dict(summary_equal=True,full_gzip_sha256_equal=True,uncompressed_results_sha256_equal=True,proofs_and_ranking_sha256_equal=True),
            input_hash=inp.hash,results_sha256=summary['result_content_sha256'],gzip_sha256=summary['compressed_sha256']))


if __name__=='__main__':
    command=sys.argv[1]
    if command=='full':full(int(sys.argv[2]))
    else:globals()[command]()
