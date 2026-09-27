"""Prepare evidence/representations without labels, scores or historical verdicts.

Emit one requested artifact on stdout. Files are persisted by the caller using
apply_patch, never by this module. Grammatical frames remain PROPOSTA.
"""
import argparse
import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from proof_compiler_r1 import load, digest, serialized, source_hash, CanonicalInput

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
CF = REPO / 'CF_SEGMENTADA_V2/CF_DISPOSITIVOS_LIMPOS.json'
VERSION = 'V2_EXPANSION_1'


def families(d):
    if d['norma'] == 'ADCT': return 'REGRA_TRANSITORIA'
    a = int(re.match(r'\d+', d['artigo']).group())
    if a <= 4: return 'PRINCIPIO_FUNDAMENTAL'
    if a == 5: return 'GARANTIA'
    if a <= 11: return 'DIREITO_SOCIAL'
    if a <= 17 or a in (28, 29, 32, 77, 121): return 'REGRA_ELEITORAL'
    if a == 22 or a == 24: return 'COMPETENCIA_LEGISLATIVA'
    if a == 23: return 'COMPETENCIA_ADMINISTRATIVA'
    if 37 <= a <= 41 or a == 247: return 'REGIME_FUNCIONAL'
    if a == 42 or a == 142: return 'REGIME_MILITAR'
    if 93 <= a <= 135: return 'ORGANIZACAO_INSTITUCIONAL'
    if 136 <= a <= 144: return 'DEFESA_ESTADO_SEGURANCA'
    if 145 <= a <= 169 or a in (195, 239, 240): return 'TRIBUTACAO_FINANCIAMENTO'
    if 170 <= a <= 181: return 'ORDEM_ECONOMICA'
    if 182 <= a <= 191 or a == 243: return 'REGIME_PROPRIEDADE'
    if a in (201, 202): return 'BENEFICIO_PREVIDENCIARIO'
    if a in (203, 204): return 'ASSISTENCIA_SOCIAL'
    if 196 <= a <= 200: return 'POLITICA_SAUDE'
    if 205 <= a <= 219: return 'EDUCACAO_CULTURA_CIENCIA'
    if 220 <= a <= 224: return 'COMUNICACAO_SOCIAL'
    if a == 225: return 'PROTECAO_AMBIENTAL'
    if a in (226, 227): return 'PROTECAO_FAMILIA_INFANCIA'
    return 'ORGANIZACAO_ORDEM_SOCIAL'


def source_alerts(d):
    text = d['text']
    alerts = []
    if re.search(r'\brevogad[oa]', text, re.I): alerts.append('REVOGACAO_NA_FOTOGRAFIA')
    if re.match(r'\s*-[A-Z]\.', text): alerts.append('SUFIXO_DE_PARAGRAFO_SEM_IDENTIDADE')
    if re.search(r'\)\s+[IVXLCDM]+\s+[a-záéíóúãõç]', text): alerts.append('INCISO_APOS_NOTA_EDITORIAL')
    if re.search(r'\.\s+[IVXLCDM]+\s+[a-záéíóúãõç]', text): alerts.append('INCISO_CONCATENADO')
    return alerts


def device_shell(d, by_id, sha):
    did = d['chave_dispositivo']
    parts = did.split(':')
    parents = [':'.join(parts[:i]) for i in range(2, len(parts))]
    result = dict(device_id=did, text=d['texto'], source_version='CF_SEGMENTADA_V2', source_hash=sha,
                  text_identity_status='CONSISTENTE_NA_FOTOGRAFIA', family=families(d), nuclei=[],
                  hierarchical_context=[dict(device_id=p, text=by_id[p]['texto']) for p in parents if p in by_id])
    alerts = source_alerts(result)
    if alerts: result.update(text_identity_status='FONTE_EM_REVISAO', source_alerts=alerts)
    return result


def proposal_frame(d):
    """Lossless grammatical draft, no contracts; not a completed diagnosis.

    Specific wording is retained in a literal frame. No invented subject/object
    IDs stand in for an unresolved legal proposition.
    """
    t = d['text']
    m = re.search(r'\b(será|serão|poderá|poderão|deverá|deverão|compreende|compete|estabelecerá|assegurará|é vedad[oa]|são|é|fica)\b', t, re.I)
    p = dict(modalidade='A_CONFIRMAR', sujeitos=[], predicado='PROPOSICAO_PENDENTE', objetos=[],
             condicoes=[], excecoes=[], finalidades=[])
    literal = dict(sujeito_textual=t[:m.start()].strip() if m else None,
                   predicado_textual=m.group() if m else None,
                   complemento_textual=t[m.end():].strip() if m else t,
                   contexto_herdado=d['hierarchical_context'])
    return dict(nucleus_id=d['device_id']+'#PROPOSTA',
                source_spans=[dict(device_id=d['device_id'], start=0, end=len(t), text=t)],
                template=d['family'], proposition=p, role='AUTONOMO', depends_on=[], contracts_by_relation=[],
                state='PROPOSTA', literal_frame=literal,
                unresolved=['decomposição semântica dos sujeitos, predicados, condições, exceções e dependências'],
                provenance=dict(method='segmentacao_gramatical_conservadora_sem_admissao', version=VERSION, human_validated=False))


def curated_nucleus(d, a):
    start = d['text'].index(a['span'])
    contracts = []
    for c in a.get('contracts', []):
        contracts.append(dict(relation=c['relation'], object_reached=c['object_reached'],
            requires=dict(predicates=c['predicates'], objects_all=c['objects'], subjects_any=c.get('subjects_any', []),
                          context_all=c.get('context_all', []), participant_role=c.get('participant_role', 'ACTOR')),
            editorial_review=c.get('editorial_review', False),
            scope_policy='Alcance parcial indicado pelo span e pelos argumentos da prova; não demonstra os demais requisitos.',
            forbidden_inferences=['ancestral_como_especie', 'tema_como_prova', 'contexto_como_competencia']))
    return dict(nucleus_id=d['device_id']+'#N'+str(len(d['nuclei'])+1),
        source_spans=[dict(device_id=d['device_id'], start=start, end=start+len(a['span']), text=a['span'])],
        template=a['family'], proposition=dict(modalidade=a.get('modalidade', 'DEVER_OU_GARANTIA'), sujeitos=a['subjects'],
            predicado=a['predicate'], objetos=a['objects'], condicoes=a.get('conditions', []),
            excecoes=a.get('exceptions', []), finalidades=a.get('purposes', [])),
        role=a.get('role', 'AUTONOMO'), depends_on=[], contracts_by_relation=contracts, state='CURADA_EXPERIMENTAL',
        residual_text_policy='Texto integral preservado; núcleos adicionais não modelados não são implicitamente provados.',
        provenance=dict(method='anotacao_manual_do_texto_e_pais', version=VERSION, human_validated=False))


def build():
    pilot = load(ROOT/'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_PILOTO_R1.json')
    cf = load(CF)['dispositivos']
    by_id = {d['chave_dispositivo']: d for d in cf}
    sha = hashlib.sha256(CF.read_bytes()).hexdigest()
    priority = load(ROOT/'02_DISPOSITIVOS/UNIVERSO_PRIORITARIO_V2.json')
    # Supports the persisted universe contract, never historical outcomes.
    ids = priority['ids'] if 'ids' in priority else [d['chave_dispositivo'] for d in priority['devices']]
    devices = {d['device_id']: copy.deepcopy(d) for d in pilot['devices']}
    for did in ids:
        if did not in devices: devices[did] = device_shell(by_id[did], by_id, sha)
    for a in load(ROOT/'02_DISPOSITIVOS/ANOTACOES_CURADAS_EXPANSAO_V2.json')['annotations']:
        d = devices[a['device_id']]
        d['family'] = a['family']
        d['nuclei'].append(curated_nucleus(d, a))
    technical = load(ROOT/'02_DISPOSITIVOS/ANOTACOES_TECNICAS_PROPOSTAS_V2.json')
    for a in technical['annotations']:
        d = devices[a['device_id']]
        a = dict(a, family=d['family'])
        n = curated_nucleus(d, a)
        n['state'] = 'PROPOSTA'
        n['provenance']['method'] = 'proposicao_tecnica_manual_pendente_revisao'
        n['contracts_by_relation'] = [dict(relation='REPRESENTACAO', object_reached='INSTITUTO',
            requires=dict(predicates=[a['predicate']], objects_all=a['objects'], subjects_any=a['subjects'],
                          context_all=[], participant_role='ACTOR'), editorial_review=True,
            scope_policy='Exige conferência de todos os qualificadores literais antes de qualquer publicação.',
            forbidden_inferences=['finalidade_sem_ancora','dominio_como_competencia'])]
        d['nuclei'].append(n)
    for d in devices.values():
        if not d['nuclei']: d['nuclei'] = [proposal_frame(d)]
        d['annotation_status'] = 'CURADA_PARCIAL' if any(n['state']=='CURADA_EXPERIMENTAL' for n in d['nuclei']) else 'PROPOSTA_INCOMPLETA'
        d['source_alerts'] = source_alerts(d)
        if d['source_alerts']: d['text_identity_status'] = 'FONTE_EM_REVISAO'
    for q in technical['quarantine']:
        devices[q['device_id']]['source_alerts'].append(q['reason'])
        devices[q['device_id']]['text_identity_status'] = 'FONTE_EM_REVISAO'
    works = load(ROOT/'03_OBRAS/WORK_EVIDENCE_V2_DRAFT.json')['works']
    by_work = {w['work_id']: w for w in works}
    for f in load(ROOT/'03_OBRAS/FONTES_COMPLEMENTARES_V2.json')['facts']:
        e = by_work[f['work_id']]['evidences'][0]
        e['source'] = dict(identifier=f['url'], locator=f['locator'], paraphrase=f['paraphrase'], hash=None,
            hash_scope='SHA256 da ficha documental, não bytes remotos', consulted_at='2026-09-24', tier=f.get('tier','PRIMARIA_OFICIAL'))
        e['state'] = f.get('state', 'VALIDADA')
        if 'objects' in f: e['claim']['objects'] = f['objects']
        e['transposition_limits'] = f.get('limits', ['Não afirma identidade institucional brasileira nem cobertura de requisitos ausentes.'])
        e['provenance'].update(method='curadoria_documental_experimental', source_checked=True)
    for w in works:
        for e in w['evidences']: e['source']['hash'] = source_hash(e['source'])
    ontology = copy.deepcopy(pilot['ontology'])
    concepts = {c['id']:c for c in ontology['concepts']}
    predicates = set(ontology['predicates'])
    def concept_list(values):
        for v in values: concepts.setdefault(v, dict(id=v, label=v.replace('_',' ').lower(), state='CURADA_EXPERIMENTAL'))
    for d in devices.values():
        for n in d['nuclei']:
            p=n['proposition']; concept_list(p['sujeitos']+p['objetos']); predicates.add(p['predicado'])
            for c in n['contracts_by_relation']:
                r=c['requires']; concept_list(r['objects_all']+r['subjects_any']+r['context_all']); predicates.update(r['predicates'])
    for w in works:
        for e in w['evidences']:
            cl=e['claim']; predicates.add(cl['predicate'])
            for k in ('subjects','objects','context','effects'): concept_list(cl[k])
            concept_list([p['concept'] for p in cl['participants']])
    ontology.update(version='CONCEPTS_V2_EXPANSION_1', concepts=[concepts[k] for k in sorted(concepts)], predicates=sorted(predicates),
                     roles=['ACTOR','AFFECTED','CONTEXT'], qualifier_policy='Preservados literalmente; ausentes nunca inferidos por ancestralidade.')
    ordered_d = [devices[k] for k in sorted(devices)]
    ordered_w = sorted(works, key=lambda w:w['work_id'])
    files = {}
    for i in range(0,len(ordered_d),30): files[f'02_DISPOSITIVOS/DISPOSITIVOS_V2_{i//30+1:02}.json'] = dict(version=VERSION, devices=ordered_d[i:i+30])
    for i in range(0,len(ordered_w),18): files[f'03_OBRAS/WORK_EVIDENCE_V2_{i//18+1:02}.json'] = dict(version=VERSION, works=ordered_w[i:i+18])
    files['04_CONCEITOS/CONCEITOS_V2.json'] = ontology
    files['01_SCHEMA/FAMILIAS_TEMPLATES_V2.json'] = dict(version=VERSION, families=sorted({d['family'] for d in ordered_d}),
        templates=[dict(id=f, required_proposition_fields=['modalidade','sujeitos','predicado','objetos','condicoes','excecoes','finalidades'],
                        proof_policy='Argumentos conjuntivos na mesma afirmação validada, sem herança conceitual; depende da instância.',
                        unresolved_policy='PROPOSTA sem contrato até curadoria; não diagnóstico concluído.') for f in sorted({d['family'] for d in ordered_d})])
    canonical = dict(schema_version='CANONICAL_EVALUATION_INPUT_V2', scope='FULL_69_BY_3461_PRIORITY_210_PARTIALLY_CURATED',
                     devices=ordered_d, works=ordered_w, ontology=ontology, source_policy=pilot['source_policy'])
    CanonicalInput(canonical)
    manifest = dict(version='CANONICAL_EVALUATION_INPUT_V2_MANIFEST_1', representation_version=VERSION,
        parts=[dict(path=k,sha256=digest(v)) for k,v in sorted(files.items()) if not k.endswith('FAMILIAS_TEMPLATES_V2.json')],
        constitutional_source=dict(path=CF.relative_to(REPO).as_posix(),sha256=sha),
        policy='Mesmo loader resolve 3461 textos: 210 representações prioritárias; demais sem núcleo, nunca herdando alpha3.',
        priority_count=len(devices), work_count=len(works), schema_version=canonical['schema_version'], source_policy=canonical['source_policy'],
        scope=canonical['scope'])
    files['01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2.json'] = manifest
    stats = dict(devices=len(devices),curated_devices=sum(d['annotation_status']=='CURADA_PARCIAL' for d in ordered_d),
        proposed_devices=sum(d['annotation_status']=='PROPOSTA_INCOMPLETA' for d in ordered_d), nuclei=sum(len(d['nuclei']) for d in ordered_d),
        works=len(works),evidence_states=dict(Counter(e['state'] for w in works for e in w['evidences'])),
        source_alerts=[dict(device_id=d['device_id'],alerts=d['source_alerts']) for d in ordered_d if d['source_alerts']],
        concepts=len(concepts),predicates=len(predicates),families=len(files['01_SCHEMA/FAMILIAS_TEMPLATES_V2.json']['families']))
    files['00_CHECKPOINTS/EXPANSION_REPRESENTATIONS_FREEZE.json'] = dict(logical_timestamp='V2-P02-REPRESENTATIONS-0007',
        manifest_hash=digest(manifest), artifacts=[dict(path=k,sha256=digest(v)) for k,v in sorted(files.items())],
        statistics=stats, blind_protocol='Dados não consomem rótulos ou scores; preexposição ao piloto/auditoria já declarada.',
        semantic_completion=False, reason='Rascunhos gramaticais propostos ainda exigem anotação semântica; não são 210 diagnósticos curados.')
    return files


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--artifact'); args=parser.parse_args()
    files=build()
    print(json.dumps({'files':{args.artifact:serialized(files[args.artifact])}} if args.artifact else {'artifacts':list(files), 'statistics':files['00_CHECKPOINTS/EXPANSION_REPRESENTATIONS_FREEZE.json']['statistics']},ensure_ascii=False))
