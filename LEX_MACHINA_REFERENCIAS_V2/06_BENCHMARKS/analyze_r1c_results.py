"""Post-freeze diagnosis of existing results only; never invokes evaluation."""
import json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'05_COMPILADOR'))
from canonical_input_r1c import load_canonical
from proof_compiler_r1 import load,serialized,file_hash

def prepare():
    inp=load_canonical()
    reg=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1C.json')
    inv=load(ROOT/'06_BENCHMARKS/INVENTARIO_OPERACIONAL_105_R1C.json')['rows']
    index={(r['dispositivo'],r['work_id']):r for r in inv}
    proofs={(r['device_id'],r['work_id']):r for r in load(ROOT/'06_BENCHMARKS/PROVAS_EXPANSAO_R1C.json')['rows']}
    a3={(r['dispositivo'],r['work_id']):r for r in load(ROOT/'06_BENCHMARKS/AUDITORIA_17_FONTES_R1C.json')['rows']}
    causes=[]
    for r in reg['cases']:
        if r['metric']!='FN':continue
        key=(r['device_id'],r['work_id']);old=index[key]; p=proofs[key];d=inp.devices[key[0]];w=inp.works[key[1]]
        primary='AUSENCIA_REAL_DE_EVIDENCIA'
        reason='As fontes auditadas não documentam conjuntamente predicado, objeto e participantes específicos da rota. Ausência no conjunto consultado, não prova de inexistência na obra.'
        if old['causa_principal']=='CONTRATO_DE_NATUREZA_INADEQUADO':
            primary='CONTRATO_REQUER_ADJUDICACAO';reason=old['dimensao_ausente']
        elif key in a3:
            primary=a3[key]['causa_se_nao_recuperado'];reason=a3[key]['conclusao']
        elif old['causa_principal']=='REPRESENTACAO_DISPOSITIVO_INCOMPLETA':
            if key[0] in ['CF88:ART.170','CF88:ART.3:INC.IV','CF88:ART.5']:
                primary='REPRESENTACAO_AINDA_INCOMPLETA';reason='A anotação literal explicita o objeto amplo, mas os núcleos/rotas existentes não o cobrem. Completar uma rota de admissão requer autorização além da curadoria factual congelada.'
            elif key[0] in ['CF88:ART.19:INC.I','CF88:ART.55:PAR.3','CF88:ART.5:INC.XII']:
                primary='CONTRATO_REQUER_ADJUDICACAO';reason='A fonte da obra descreve outra modalidade/regime: coação religiosa não é proibição estatal de aliança; defesa penal não é regime parlamentar; tratamento de dados não é interceptação. Não corrigir por equivalência artificial.'
        elif old['causa_principal']=='EVIDENCIA_OBRA_PROPOSTA_NAO_VALIDADA':
            if key[1]=='REF-FIL-0002' and key[0] in ['CF88:ART.5:INC.IV','CF88:ART.5:INC.IX']:
                primary='FONTE_INSUFICIENTE';reason='A pesquisa oficial não localizou evento concreto de repressão; proposta não validada.'
            elif (key[1]=='REF-FIL-0008' and key[0]=='CF88:ART.1:INC.III') or (key[1]=='REF-JOG-0002') or key[1]=='REF-DOC-0003' or (key[1]=='REF-SER-0003' and key[0] in ['CF88:ART.220:PAR.1','CF88:ART.5:INC.XIV']):
                primary='CONTRATO_REQUER_ADJUDICACAO';reason='Fonte validada, mas modalidade diferente: proteger vida/buscar sobrevivência não é negar alimento; documentar impeachment não é defender separação de Poderes; ocultar informação de risco não é publicar informação jornalística.'
            elif r['admissibility']=='REVISAO_EDITORIAL':
                primary='CONTRATO_REQUER_ADJUDICACAO';reason='Há prova alimentar completa, mas o contrato já exigia revisão editorial. A R1C preserva essa exigência; não trata prova disponível como aprovação humana.'
        if not r['candidate_retrieval']:primary='CANDIDATO_NAO_RECUPERADO'
        if r['admissibility']=='FONTE_EM_REVISAO':primary='FONTE_JURIDICA_EM_REVISAO'
        secondary=[]
        if old['causa_principal']=='REPRESENTACAO_DISPOSITIVO_INCOMPLETA':secondary.append('REPRESENTACAO_LITERAL_COMPLEMENTADA_MAS_PROVA_PARCIAL')
        if any(e['state']!='VALIDADA' for e in w['evidences']):secondary.append('HA_EVIDENCIA_NAO_VALIDADA_NO_DOSSIE')
        causes.append(dict(device_id=key[0],work_id=key[1],obra=w['nome'],pair_id=old['pair_id'],primary_cause=primary,secondary_causes=secondary,reason=reason,baseline_cause=old['causa_principal'],state=r['admissibility'],existing_claims=[dict(id=e['evidence_id'],state=e['state'],claim=e['claim'],source_hash=e['source']['hash']) for e in w['evidences']],unmet_contracts=p['unmet_contracts'],proofs=p['proofs'],action='Manter abstenção/revisão; não pesquisar indefinidamente nem alterar a entrada R1C congelada.'))
    categories=['AUSENCIA_REAL_DE_EVIDENCIA','REPRESENTACAO_AINDA_INCOMPLETA','FONTE_INSUFICIENTE','CONTRATO_REQUER_ADJUDICACAO','CANDIDATO_NAO_RECUPERADO','FONTE_JURIDICA_EM_REVISAO','OUTRO']
    counts={k:sum(r['primary_cause']==k for r in causes) for k in categories}
    comparison={}
    for version in ['R1','R1B','R1C']:
        result=load(ROOT/f'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_{version}.json')
        c=result['counts']; tp,fp,tn,fn=[c.get(k,0) for k in ('TP','FP','TN_NAO_PUBLICADO','FN')]
        comparison[version]=dict(TP=tp,FP=fp,TN=tn,FN=fn,valid=tp+fp+tn+fn,total=result['pairs'],excluded=c.get('NAO_AVALIAVEL',0),precision=tp/(tp+fp),recall=tp/(tp+fn),specificity=tn/(tn+fp),accuracy=(tp+tn)/(tp+fp+tn+fn),states=dict(Counter(r['admissibility'] for r in result['cases'])),result_sha256=file_hash(ROOT/f'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_{version}.json'))
    baseline=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1B.json')
    index_c={(r['device_id'],r['work_id']):r for r in reg['cases']}
    transitions=[]
    for r in baseline['groups']['recent60']['cases']:
        if r['metric']=='FN':
            k=(r['device_id'],r['work_id']);new=index_c[k];cause=next((c for c in causes if (c['device_id'],c['work_id'])==k),None)
            transitions.append(dict(device_id=k[0],work_id=k[1],baseline=r['state'],r1c=new['admissibility'],metric=new['metric'],cause=cause['primary_cause'] if cause else 'DADO_FALTANTE_CORRIGIDO',reason=cause['reason'] if cause else 'Nova afirmação documental supriu a rota sem alterar contrato.'))
    mechanisms=[]
    for r in baseline['groups']['mechanisms15']['cases']:
        if r['metric']=='FN':
            k=(r['device_id'],r['work_id']);n=index_c[k];cause=next((c for c in causes if (c['device_id'],c['work_id'])==k),None)
            mechanisms.append(dict(device_id=k[0],work_id=k[1],r1b=r['state'],r1c=n['admissibility'],metric=n['metric'],reason=cause['reason'] if cause else 'Condenação injusta documentada em fonte oficial.'))
    return {'06_BENCHMARKS/DECOMPOSICAO_CAUSAL_FN_R1C.json':serialized(dict(total=len(causes),counts=counts,cases=causes,policy='Diagnóstico pós-freeze; não importado pelo compilador. Ausência real significa ausência de suporte nas fontes auditadas, não inexistência demonstrada na obra.')),'06_BENCHMARKS/COMPARACAO_R1_R1B_R1C.json':serialized(comparison),'06_BENCHMARKS/AUDITORIA_RECENTES_10_E_MECANISMOS_4_R1C.json':serialized(dict(recent10=transitions,mechanisms4=mechanisms))}

if __name__=='__main__':print(json.dumps({'files':prepare()},ensure_ascii=False))
