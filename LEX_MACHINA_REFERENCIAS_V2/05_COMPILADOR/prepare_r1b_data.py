"""One factual patch set; no labels, scores, benchmark or decision code is read."""
import copy
import json
from canonical_input_r1 import load_canonical, ROOT
from proof_compiler_r1 import serialized, digest, file_hash, CanonicalInput


def prepare():
    inp=load_canonical()
    works=[]; changes=[]
    # Existing, independently checked source cards remain byte-identical.
    for wid,obj,why in (
        ('REF-LIV-0001','PRIVACIDADE','A ficha documenta observação de Winston dentro de casa; não apenas transmissão de comunicação.'),
        ('REF-SER-0002','AUTONOMIA_REPRODUTIVA','A ficha documenta servidão reprodutiva; dimensão factual omitida da anotação de igualdade de gênero.')):
        w=copy.deepcopy(inp.works[wid]); e=w['evidences'][0]
        assert e['state']=='VALIDADA' and obj not in e['claim']['objects']
        e['claim']['objects'].append(obj)
        e['provenance']['r1b_completion']=dict(reason=why,source_card_reused=e['source']['hash'],human_validated=False)
        works.append(w); changes.append(dict(work_id=wid,evidence_id=e['evidence_id'],field='claim.objects',added=obj,reason=why,source=e['source']))
    w=copy.deepcopy(inp.works['EXP-LIV-008']); prior=w['evidences'][0]; e=copy.deepcopy(prior)
    e['evidence_id']=w['work_id']+'#E02'
    e['content_type']='PRATICA_INSTITUCIONAL'
    e['claim']=dict(predicate='DISCRIMINAR',subjects=['ESTADO'],objects=['MORADIA'],
                    context=['EUA','SEGREGACAO_RESIDENCIAL'],effects=[],participants=[dict(concept='ESTADO',role='ACTOR')])
    e['provenance']['r1b_completion']=dict(reason='A descrição editorial já atribui segregação residencial a políticas públicas; explicita-se a prática na moradia, sem equivalência entre moradia e raça.',
                                          source_card_reused=e['source']['hash'],human_validated=False)
    e['transposition_limits'].append('Prática histórica descrita na fonte bibliográfica; não representa administração pública brasileira nem competência legislativa.')
    w['evidences'].append(e); works.append(w)
    changes.append(dict(work_id=w['work_id'],evidence_id=e['evidence_id'],field='evidences',added='prática de discriminação na moradia',source=e['source'],reason=e['provenance']['r1b_completion']['reason']))
    d=copy.deepcopy(inp.devices['CF88:ART.5:INC.XV'])
    assert not d['nuclei']
    span='podendo qualquer pessoa, nos termos da lei, nele entrar, permanecer ou dele sair com seus bens'
    start=d['text'].index(span)
    d['annotation_status']='CURADA_PARCIAL_R1B'
    d['nuclei']=[dict(nucleus_id=d['device_id']+'#N1',template='GARANTIA',state='CURADA_EXPERIMENTAL',role='AUTONOMO',depends_on=[],
        source_spans=[dict(device_id=d['device_id'],start=start,end=start+len(span),text=span)],
        proposition=dict(modalidade='DIREITO',sujeitos=['PESSOA'],predicado='ASSEGURAR',objetos=['INGRESSO_TERRITORIO'],
                         condicoes=['território nacional; tempo de paz; nos termos da lei'],excecoes=[],finalidades=[]),
        contracts_by_relation=[dict(relation='ANALOGIA_CONTROLADA',object_reached='GARANTIA',editorial_review=False,
            requires=dict(predicates=['CONTROLAR'],objects_all=['INGRESSO_TERRITORIO'],subjects_any=[],context_all=[],participant_role='ACTOR'),
            forbidden_inferences=['identidade_de_regime','recusa_automaticamente_ilegal','controle_como_violacao','circulacao_interna_automaticamente_provada'],
            scope_policy='Analogia limitada à tensão entre ingresso no território e controle de entrada. Não afirma que cada recusa seja ilegal, que a regra estrangeira reproduza a CF ou que todo o inciso seja representado.')],
        residual_text_policy='Locomoção interna, permanência, saída e bens não são implicitamente provados pelo núcleo de ingresso.',
        provenance=dict(method='anotacao_do_segmento_literal_da_fotografia_congelada',version='EXPANSAO_R1B',human_validated=False))]
    changes.append(dict(device_id=d['device_id'],field='nuclei',added='núcleo de ingresso no território',reason='O dispositivo existia, mas tinha zero núcleos. Segmento literal da fotografia; arquitetura, ontologia e contratos já existentes não foram alterados.',source_hash=d['source_hash'],source_span=span))
    overlay=dict(version='EXPANSAO_R1B_DADOS_1',base_r1_hash=inp.hash,works=works,devices=[d],changes=changes,
                 policy='Completude de anotação apoiada em fontes já verificadas. Nenhuma nova pesquisa, promoção de PROPOSTA, equivalência ou alteração de contrato preexistente.')
    path='01_SCHEMA/COMPLETUDE_FACTUAL_R1B.json'
    manifest=dict(version='CANONICAL_EVALUATION_INPUT_V2_R1B_MANIFEST',base_manifest='01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1.json',
                  base_input_hash=inp.hash,overlay=path,overlay_sha256=digest(overlay),revision_phase7=1,factual_pass=1)
    return {path:serialized(overlay),'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1B.json':serialized(manifest)}


if __name__=='__main__':
    print(json.dumps({'files':prepare()},ensure_ascii=False))
