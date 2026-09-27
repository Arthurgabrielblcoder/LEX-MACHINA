"""Assemble curated data only. Does not import evaluation or read human labels."""
import copy, json
from canonical_input_r1b import load_canonical, ROOT
from proof_compiler_r1 import load, digest, serialized, source_hash, CanonicalInput, require

def assemble(base, overlay):
    data=copy.deepcopy(base.data)
    ds={d['device_id']:d for d in data['devices']}
    ws={w['work_id']:w for w in data['works']}
    for d in overlay['devices']: ds[d['device_id']]=copy.deepcopy(d)
    for w in overlay['works']: ws[w['work_id']]=copy.deepcopy(w)
    data['devices']=[ds[k] for k in sorted(ds)]
    data['works']=[ws[k] for k in sorted(ws)]
    data['scope']+='__FACTUAL_R1C'
    return CanonicalInput(data)

def contracts(inp):
    return {d['device_id']:[{k:n[k] for k in ('nucleus_id','template','role','depends_on','contracts_by_relation','state','source_spans')} for n in d['nuclei']] for d in inp.devices.values()}

def invariants(base, new):
    require(base.devices.keys()==new.devices.keys(),'device IDs changed')
    require(base.works.keys()==new.works.keys(),'work IDs changed')
    require(base.data['ontology']==new.data['ontology'],'ontology changed')
    require(contracts(base)==contracts(new),'contract/template/nature/anchor/state changed')
    for did,d in base.devices.items():
        require(all(d[k]==new.devices[did][k] for k in ('text','hierarchical_context','source_version','source_hash','text_identity_status')),'legal source changed')
    for wid,w in base.works.items():
        require({k:v for k,v in w.items() if k!='evidences'}=={k:v for k,v in new.works[wid].items() if k!='evidences'},'catalog metadata changed')
        current={e['evidence_id']:e for e in new.works[wid]['evidences']}
        for e in w['evidences']:
            require(e['evidence_id'] in current,'evidence deleted')
            if e['state']=='VALIDADA':require(e==current[e['evidence_id']],'old validated evidence changed')

def prepare():
    base=load_canonical()
    plan=load(ROOT/'03_OBRAS/CURADORIA_EVIDENCIAS_R1C.json')
    source_data=load(ROOT/'03_OBRAS/FONTES_DOCUMENTAIS_R1C.json')
    cards={r['source_id']:r for r in source_data['cards']}
    legal=load(ROOT/'02_DISPOSITIVOS/COMPLEMENTOS_JURIDICOS_R1C.json')['rows']
    works={}; changes=[]
    def source(sid):
        c=cards[sid]
        s={k:c[k] for k in ('identifier','locator','paraphrase','tier','consulted_at','hash_scope')}
        s['hash']=source_hash(s)
        return s
    def work(wid):
        if wid not in works: works[wid]=copy.deepcopy(base.works[wid])
        return works[wid]
    for u in plan['updates']:
        w=work(u['work_id']); e=next(e for e in w['evidences'] if e['evidence_id']==u['evidence_id'])
        require(e['state']=='PROPOSTA','only proposed evidence may change')
        prior=copy.deepcopy(e)
        e['state']=u['state']
        if u['source_id']:
            e['source']=source(u['source_id'])
            e['transposition_limits']=cards[u['source_id']]['transposition_limits']
        if u['claim_patch']: e['claim'].update(copy.deepcopy(u['claim_patch']))
        e['provenance']['r1c']=dict(method='curadoria_documental_factual',human_validated=False,source_card_verified=u['state']=='VALIDADA',reason=u['reason'],prior_evidence_hash=digest(prior))
        changes.append(dict(work_id=w['work_id'],evidence_id=e['evidence_id'],operation='REVIEW_PROPOSAL',before_hash=digest(prior),after_hash=digest(e),reason=u['reason']))
    for r in plan['new_evidences']:
        w=work(r['work_id']); card=cards[r['source_id']]
        e=dict(evidence_id=r['evidence_id'],work_id=r['work_id'],content_type=r['content_type'],centrality='PONTUAL',claim=r['claim'],state='VALIDADA',polarity='AFIRMADA',source=source(r['source_id']),transposition_limits=card['transposition_limits'],provenance=dict(method='curadoria_documental_factual',human_validated=False,version='EXPANSAO_R1C',annotation_note=r['annotation_note'],not_targeted_to_device=True))
        w['evidences'].append(e)
        changes.append(dict(work_id=w['work_id'],evidence_id=e['evidence_id'],operation='ADD_FACTUAL_ASSERTION',source_id=r['source_id']))
    devices=[]
    for r in legal:
        d=copy.deepcopy(base.devices[r['device_id']])
        related=[]
        for did in r['relacionados_ids']:
            require(did in base.devices,'invalid related device')
            related.append(dict(device_id=did,text=base.devices[did]['text']))
        d['literal_curation_r1c']={k:v for k,v in r.items() if k not in ('fonte','nucleos_atuais')}
        d['literal_curation_r1c']['related_context']=related
        d['literal_curation_r1c']['proof_effect']='NONE: literal metadata does not add contractual routes'
        # Only factual qualifier fields; typed subjects/objects/predicate and proof routing stay frozen.
        for n in d['nuclei']:
            p=n['proposition']
            for dest, src in [('condicoes','condicoes_qualificadores'),('excecoes','excecoes'),('finalidades','finalidades')]:
                p[dest]=list(dict.fromkeys(p[dest]+r[src]))
            n['provenance']['r1c_literal_completion']=dict(source_hash=d['source_hash'],human_validated=False,scope='Qualificadores textuais; não adiciona rota, não promove estado de curadoria.')
        devices.append(d)
    overlay=dict(version='EXPANSAO_R1C_DADOS_E_EVIDENCIAS_1',base_input_hash=base.hash,devices=devices,works=[works[k] for k in sorted(works)],changes=changes,policy='Sem novos contratos, núcleos, templates, naturezas, equivalências, exceções por par ou alterações de código de decisão.')
    inp=assemble(base,overlay);invariants(base,inp)
    desc=dict(version='CANONICAL_EVALUATION_INPUT_V2_R1C_MANIFEST',base_manifest='01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1B.json',base_input_hash=base.hash,overlay='01_SCHEMA/COMPLETUDE_FACTUAL_R1C.json',overlay_sha256=digest(overlay),canonical_input_hash=inp.hash,contracts_sha256=digest(contracts(base)),ontology_sha256=digest(base.data['ontology']))
    return {'01_SCHEMA/COMPLETUDE_FACTUAL_R1C.json':serialized(overlay),'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1C.json':serialized(desc)}

if __name__=='__main__':print(json.dumps({'files':prepare()},ensure_ascii=False))
