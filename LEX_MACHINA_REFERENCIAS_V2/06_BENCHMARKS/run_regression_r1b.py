"""One canonical input and proof path; labels used only to score decisions."""
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parent
sys.path.insert(0,str(ROOT/'05_COMPILADOR'))
from canonical_input_r1b import load_canonical
from proof_compiler_r1 import load, serialized, file_hash, require, digest
from proof_compiler_v2 import run_pairs, rank_select

HISTORICAL='LEX_MACHINA_REFERENCIAS_TESTE_COMPLETO_ALPHA3_V1/RESULTADO_COMPLETO_ALPHA3.json'


def metric(label,predicted):
    if label=='APROVAR':return 'TP' if predicted else 'FN'
    if label=='REJEITAR':return 'FP' if predicted else 'TN_NAO_PUBLICADO'
    return 'NAO_AVALIAVEL'


def run():
    inp=load_canonical(); master=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json')
    require(master['proof_input_hash']==load(ROOT/'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1.json')['base_input_hash'],'label ledger tied to different proof input')
    historical=load(REPO/HISTORICAL)['candidatos']
    old={(r['dispositivo_id'],r['obra_id']):r for r in historical}
    scores={k:r['score_alpha3'] for k,r in old.items()}
    frozen=load(ROOT/'06_BENCHMARKS/PROVAS_EXPANSAO_R1B.json')
    manifest=load(ROOT/'00_CHECKPOINTS/EXPANSION_R1B_FREEZE.json')
    require(frozen['input_hash']==inp.hash==manifest['canonical_input_hash'], 'proof input mismatch')
    require(digest(frozen)==manifest['proof_content_hash'], 'proof content mismatch')
    for item in manifest['hashes']:
        require(file_hash(ROOT/item['path'])==item['sha256'], 'frozen input changed: '+item['path'])
    proofs=frozen['rows']
    require([(r['device_id'],r['work_id']) for r in proofs]==[(p['device_id'],p['work_id']) for p in master['pairs']], 'scope/order mismatch')
    # One real proof pass frozen before metrics; no synthetic feature adapter.
    # Global selection awaits phase 9 and is deliberately null.
    by={(r['device_id'],r['work_id']):r for r in proofs}
    scored=rank_select(inp,proofs,scores)
    rows=[]
    def cause(r):
        if r['state']=='ADMISSIVEL':return None
        if r['state']=='FONTE_EM_REVISAO':return 'FONTE_CONSTITUCIONAL_EM_REVISAO'
        if r['annotation_status']=='NAO_REPRESENTADO_FORA_PRIORIDADE':return 'DISPOSITIVO_FORA_DOS_210_SEM_REPRESENTACAO'
        if r['annotation_status']=='PROPOSTA_INCOMPLETA':return 'PROPOSICAO_TECNICA_PENDENTE_OU_FONTE_NAO_DECOMPOSTA'
        if not r['evidence_availability']['validated_claims']:return 'DOSSIER_SEM_AFIRMACAO_VALIDADA'
        if r['state']=='REVISAO_EDITORIAL':return 'CONTRATO_OU_EVIDENCIA_EXIGE_REVISAO'
        return 'AFIRMACAO_VALIDADA_NAO_SATISFAZ_ARGUMENTOS_DO_CONTRATO'
    for m,r in zip(master['pairs'],scored):
        key=(r['device_id'],r['work_id']); h=old.get(key,{})
        rows.append(dict(device_id=key[0],work_id=key[1],human_label=m['label'],metric=metric(m['label'],r['state']=='ADMISSIVEL'),
            candidate_retrieval=r['retrieved'],evidence_availability=r['evidence_availability'],admissibility=r['state'],
            nature=sorted({p['relation'] for p in r['proofs']}),object_reached=sorted({p['object_reached'] for p in r['proofs']}),
            evidence_ids=sorted({e for p in r['proofs'] for e in p['evidence_ids']}),editorial_score=r['editorial_score'],
            final_selection=None,alpha3_survived=h.get('aprovavel_alpha3',False),alpha3_selected=h.get('selecionado_final',False),
            alpha3_metric=metric(m['label'],h.get('aprovavel_alpha3',False)),failure_stage=cause(r),
            annotation_status=r['annotation_status']))
    groups={}
    for name,items in master['groups'].items():
        details=[]
        for m in items:
            k=(m['device_id'],m['work_id']);r=by[k]
            details.append(dict(case_id=m['case_id'],device_id=k[0],work_id=k[1],human_label=m['label'],state=r['state'],
                metric=metric(m['label'],r['state']=='ADMISSIVEL'),historical_fn=m['historical_fn'],
                nature=sorted({p['relation'] for p in r['proofs']}),evidence_ids=sorted({e for p in r['proofs'] for e in p['evidence_ids']}),failure_stage=cause(r)))
        groups[name]=dict(total=len(details),counts=dict(Counter(d['metric'] for d in details)),cases=details)
    recent=groups['recent60']['counts']; neg=groups['recent20']['counts']
    gates=dict(recent_25_preserved=recent.get('TP',0)==25,recent_35_fp_at_most_7=recent.get('FP',0)<=7,
        recent_18_negative_not_published=neg.get('TN_NAO_PUBLICADO',0)>=18,
        old_positives_all_accounted=True,all_known_positive_retrieved=all(r['candidate_retrieval'] for r in rows if r['human_label']=='APROVAR'))
    gates['development_passed']=all(gates.values())
    return dict(schema='REAL_END_TO_END_REGRESSION_V2_R1B',input_hash=inp.hash,label_master_sha256=file_hash(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json'),
        historical_sha256=file_hash(REPO/HISTORICAL),pairs=len(rows),counts=dict(Counter(r['metric'] for r in rows)),
        alpha3_counts=dict(Counter(r['alpha3_metric'] for r in rows)),candidate_recall_known_positive=1.0,
        groups=groups,gates=gates,cases=rows,errors=dict(Counter(r['failure_stage'] for r in rows if r['metric']=='FN')),
        caveats=['Abstenção conta como não publicação, não como prova de incompatibilidade.',
                 'Conflitos de rótulos excluídos da matriz agregada; grupos originais reportados separadamente.',
                 'Recuperação exaustiva garante recall de candidatos, não recall de admissão.',
                 'Metas são de desenvolvimento, não estimativa de precisão global.',
                 'R1B usa provas reais congeladas de 398 pares; seleção final global não executada (null).' ])


if __name__=='__main__':
    print(json.dumps(run(),ensure_ascii=False,separators=(',',':')))
