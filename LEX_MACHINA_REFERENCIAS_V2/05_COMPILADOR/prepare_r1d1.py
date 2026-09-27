"""Pre-implementation impact analysis, scoped simulation, then data patch.

Does not evaluate any old version or consolidate labels. Old known states are
read from persisted R1D. New simulations are restricted to article 205.
"""
import copy
from collections import Counter
from canonical_input_r1d import load_canonical as load_base
from canonical_input_r1d1 import assemble
from proof_compiler_r1 import load,digest,file_hash,require,CanonicalInput
from proof_compiler_v2 import run_pairs,evaluate_pair
from r1d_support import ROOT,now,write,key


def prepare():
    base=load_base();before=copy.deepcopy(base.devices['CF88:ART.205'])
    ledger=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1.json')
    prior={key(r):r for r in load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D.json')['cases']}
    pairs=[p for p in ledger['pairs'] if p['device_id']=='CF88:ART.205']
    impact=dict(at=now(),article='CF88:ART.205',known_pairs=[dict(device_id=p['device_id'],work_id=p['work_id'],obra=base.works[p['work_id']]['nome'],label=p['label'],state_r1d=prior[key(p)]['admissibility']) for p in pairs],
        global_potential_pairs=[dict(device_id='CF88:ART.205',work_id=w,obra=base.works[w]['nome']) for w in sorted(base.works)],
        known_count=len(pairs),potential_count=len(base.works),other_articles_affected=0,
        risk_analysis={'TRABALHO':'Objeto isolado ou qualificação sem educação não satisfaz a rota histórica. N2 permanece dependente e conserva context_all EDUCACAO.',
          'CIDADANIA':'Exige EDUCACAO e CIDADANIA conjuntamente e predicado HISTORIAR/ANALISAR; tema isolado não basta.',
          'EDUCACAO':'A rota só cobre contextualização documentada; não autoriza automaticamente N2/N3 nem todas as finalidades.',
          'DESENVOLVIMENTO':'Nenhum núcleo autônomo de desenvolvimento criado; N3 permanece dependente.',
          'DIREITOS_SOCIAIS':'Não existe propagação por ancestralidade para EDUCACAO.'},
        structure_confirmation=dict(primary_nucleus='CF88:ART.205#N1',role=before['nuclei'][0]['role'],span=before['nuclei'][0]['source_spans'],
            legal_reason='A oração principal qualifica educação como direito de todos e dever do Estado/família. A oração introduzida por visando estabelece finalidades. A contextualização do direito principal não exige provar simultaneamente todas as finalidades. Texto constitucional local congelado, sem nova pesquisa.'),
        methodology='Análise estática antes da implementação; somente simulação da proposta abaixo. Sem leitura do holdout.')
    write('06_BENCHMARKS/IMPACTO_ART205_R1D1.json',impact)
    write('06_BENCHMARKS/IMPACTO_ART205_R1D1.md','# Impacto art.205 antes da implementação\n\n'+impact['structure_confirmation']['legal_reason']+'\n\nQuatro pares conhecidos; 69 pares potenciais no universo integral.\n\n'+'\n'.join(f"- {p['obra']}: {p['label']}; R1D {p['state_r1d']}" for p in impact['known_pairs'])+'\n\n'+'\n'.join(f'- {k}: {v}' for k,v in impact['risk_analysis'].items())+'\n')
    after=copy.deepcopy(before)
    n1,n2,n3=after['nuclei']
    routes=[(i,c) for i,c in enumerate(n3['contracts_by_relation']) if c['relation']=='CONTEXTUALIZACAO_HISTORICA']
    require(len(routes)==1 and n1['role']=='AUTONOMO' and not n1['depends_on'],'Hypothesis not supported')
    index,route=routes[0]
    require(route['requires']['objects_all']==['EDUCACAO','CIDADANIA'],'Unexpected contract')
    moved=copy.deepcopy(route)
    moved['scope_policy']='Contextualiza historicamente o direito à educação e sua relação documentada com cidadania, no núcleo principal N1. Não afirma realização de qualificação para trabalho, pleno desenvolvimento ou preparo efetivo para cidadania; essas finalidades conservam provas e dependências próprias.'
    moved['revision']='R1D1_ART205_RELOCATION'
    n3['contracts_by_relation'].pop(index)
    n1['contracts_by_relation'].append(moved)
    require(n2==before['nuclei'][1],'Labor purpose changed')
    for a,b in zip(before['nuclei'],after['nuclei']):
        require({k:v for k,v in a.items() if k!='contracts_by_relation'}=={k:v for k,v in b.items() if k!='contracts_by_relation'},'Nucleus/dependency/qualifier changed')
    patch=dict(schema='R1D1_ART205_ONLY_PATCH',at=now(),base_input_hash=base.hash,device_id='CF88:ART.205',before=before,after=after,
        before_sha256=digest(before),after_sha256=digest(after),
        operation='MOVE_ONE_CONTRACT_N3_TO_N1_NO_REQUIREMENTS_CHANGE',
        justification=impact['structure_confirmation']['legal_reason'],expected_effect='Admissão de contextualização histórica apenas no N1; N2/N3 não provados automaticamente.',
        known_affected_pairs=impact['known_pairs'],potential_count=69,new_matcher=False,new_score=False,new_threshold=False,new_evidence=False,new_nucleus=False)
    simulated=assemble(base,patch)
    results=run_pairs(simulated,[dict(device_id='CF88:ART.205',work_id=w) for w in sorted(base.works)])
    by={key(r):r for r in results}
    known=[]
    for p in pairs:
        r=by[key(p)];known.append(dict(**impact['known_pairs'][next(i for i,q in enumerate(pairs) if key(q)==key(p))],state_simulated=r['state'],proofs=r['proofs']))
    # Synthetic assertions are explicitly not factual additions nor benchmark labels.
    checks=[]
    cases=[('trabalho_isolado','HISTORIAR',['TRABALHO'],[],False),
      ('cidadania_isolada','HISTORIAR',['CIDADANIA'],[],False),
      ('educacao_isolada','HISTORIAR',['EDUCACAO'],[],False),
      ('direito_social_ancestral','ANALISAR',['ORDEM_SOCIAL'],[],False),
      ('desenvolvimento_tema','ANALISAR',['DIGNIDADE'],[],False),
      ('labor_sem_educacao','QUALIFICAR',['TRABALHO'],[],False),
      ('labor_finalidade_sem_n1','QUALIFICAR',['TRABALHO'],['EDUCACAO'],False),
      ('cidadania_finalidade_sem_n1','EDUCAR',['CIDADANIA'],[],False),
      ('coocorrencia_sem_predicado','DOCUMENTAR',['EDUCACAO','CIDADANIA'],[],False),
      ('historia_documentada','HISTORIAR',['EDUCACAO','CIDADANIA'],[],True),
      ('analise_documentada','ANALISAR',['EDUCACAO','CIDADANIA'],[],True)]
    for name,predicate,objects,context,expected in cases:
        data=copy.deepcopy(simulated.data)
        w=next(w for w in data['works'] if w['work_id']=='EXP-LIV-004')
        e=copy.deepcopy(w['evidences'][1]);e['claim'].update(predicate=predicate,objects=objects,context=context)
        w['evidences']=[e]
        result=evaluate_pair(CanonicalInput(data),'CF88:ART.205','EXP-LIV-004')
        passed=(result['state']=='ADMISSIVEL')==expected
        if expected:passed=passed and {p['nucleus_id'] for p in result['proofs']}=={'CF88:ART.205#N1'}
        checks.append(dict(name=name,synthetic=True,expected_admission=expected,state=result['state'],nuclei=[p['nucleus_id'] for p in result['proofs']],passed=passed))
    target=by[('CF88:ART.205','EXP-LIV-004')]
    safe=all(c['passed'] for c in checks) and target['state']=='ADMISSIVEL' and all(c['state_simulated']!='ADMISSIVEL' for c in known if c['label']=='REJEITAR')
    # All 69 dossiers inspected; no other assertion even names education/citizenship.
    require({r['work_id'] for r in results if r['state']=='ADMISSIVEL'}=={'EXP-LIV-004'},'Unexpected global impact; stop for diagnosis')
    simulation=dict(at=now(),scope='69 obras x art.205; não é regressão completa',input_hash=simulated.hash,safe=safe,
        states=dict(Counter(r['state'] for r in results)),known_cases=known,rows=results,synthetic_checks=checks,old_versions_executed=False)
    write('06_BENCHMARKS/SIMULACAO_ART205_R1D1.json',simulation)
    write('06_BENCHMARKS/SIMULACAO_ART205_R1D1.md','# Simulação art.205 R1D1\n\n'+f"Segura: {safe}. 69 pares: {simulation['states']}. Onze controles sintéticos: {sum(c['passed'] for c in checks)}/11.\n\n"+
          'Somente Cidadania no Brasil passa a ADMISSIVEL, com prova N1. Os três negativos conhecidos continuam insuficientes. Trabalho/cidadania isolados e finalidades sem N1 não admitem. Os testes sintéticos não são novas evidências nem rótulos.\n')
    require(safe,'Unsafe simulation; patch not persisted')
    write('02_DISPOSITIVOS/PATCH_ART205_R1D1.json',patch)
    write('01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1D1.json',dict(schema='R1D1_DESCRIPTOR',base_input_hash=base.hash,canonical_input_hash=simulated.hash,
        patch='02_DISPOSITIVOS/PATCH_ART205_R1D1.json',patch_sha256=file_hash(ROOT/'02_DISPOSITIVOS/PATCH_ART205_R1D1.json'),works=69,devices=3461,
        label_path='06_BENCHMARKS/HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1.json',label_sha256=file_hash(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1.json')))
    write('09_RELATORIOS/CORRECAO_ART205_R1D1.md','# Correção art.205 R1D1\n\n'+patch['justification']+'\n\nAntes: rota histórica em N3 dependia de N1, cujo único contrato era NEGAR_ACESSO EDUCACAO. Depois: a mesma rota, com HISTORIAR/ANALISAR e EDUCACAO+CIDADANIA, pertence a N1. Removida de N3 para não atribuir automaticamente a finalidade.\n\nNenhum núcleo, predicado, objeto, qualificador, dependência, evidência, matcher, score ou threshold foi criado ou enfraquecido. N2 permanece idêntico; N3 mantém a rota EDUCAR CIDADANIA e sua dependência N1. A regra se aplica a qualquer obra com afirmação validada que satisfaça o contrato, sem teste de título ou ID.\n\nEfeito esperado: somente o vínculo adjudicado se recupera entre os 69 pares do artigo. Pares e testes constam dos relatórios de impacto e simulação.\n')
    print('Safe simulation; R1D1 patch created',simulated.hash)


if __name__=='__main__':prepare()
