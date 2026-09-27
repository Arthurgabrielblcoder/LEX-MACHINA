"""Audit full output, compare persisted baselines, package evidence-backed RC1.

This never invokes a matcher, consolidates labels, or opens a holdout dataset.
"""
import collections
import gzip
import json
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'05_COMPILADOR'))
from canonical_input_r1d1 import load_canonical
from proof_compiler_r1 import load,digest,file_hash,require,match_claim
from r1d_support import ROOT,now,write,key,metric
from r1d1_pipeline import integrity,freeze_verify,matrix,LABELS,HISTORICAL


def concentration(rows):
    counts=collections.Counter(r['work_id'] for r in rows)
    ordered=sorted(counts.items(),key=lambda x:(-x[1],x[0]));total=sum(counts.values())
    hhi=sum((n/total)**2 for _,n in ordered) if total else None
    return dict(unit='vínculos únicos obra-dispositivo',total=total,works_used=len(counts),
        devices_covered=len({r['device_id'] for r in rows}),top1=sum(n for _,n in ordered[:1])/total if total else None,
        top5=sum(n for _,n in ordered[:5])/total if total else None,top10=sum(n for _,n in ordered[:10])/total if total else None,
        HHI=hhi,HHI_10000=hhi*10000 if hhi else None,effective_works=1/hhi if hhi else None,counts_by_work=dict(ordered))


def distributions(inp,rows):
    media=collections.Counter();families=collections.Counter();scores=collections.Counter();nature=collections.Counter();objects=collections.Counter();content=collections.Counter();quality=collections.Counter();evidence_states=collections.Counter()
    for r in rows:
        w=inp.works[r['work_id']];d=inp.devices[r['device_id']]
        media[w['tipo']]+=1;families[d['family']]+=1
        scores['SEM_SCORE_HISTORICO' if r.get('editorial_score') is None else str(r['editorial_score'])]+=1
        for n in {p['relation'] for p in r.get('proofs',[])}:nature[n]+=1
        for o in {p['object_reached'] for p in r.get('proofs',[])}:objects[o]+=1
        ids={e for p in r.get('proofs',[]) for e in p['evidence_ids']}
        ev=[e for e in w['evidences'] if e['evidence_id'] in ids]
        for t in {e['content_type'] for e in ev}:content[t]+=1
        for q in {e['source']['tier'] for e in ev}:quality[q]+=1
        for s in {e['state'] for e in ev}:evidence_states[s]+=1
    return dict(media=dict(media),legal_family=dict(families),editorial_score=dict(scores),pedagogical_nature=dict(nature),
        object_reached=dict(objects),evidence_content_type=dict(content),source_quality_tier=dict(quality),evidence_state=dict(evidence_states),
        counting='Mídia/família/score exclusivos por vínculo; natureza/objeto/tipo/qualidade inclusivos (um vínculo pode ter mais de um). Sem nota de qualidade nova.')


def sample_diverse(rows,limit=25):
    rows=sorted(rows,key=lambda r:(r['device_id'],r['work_id']))
    out=[];used=set();remaining=[]
    for r in rows:
        if r['work_id'] not in used and len(out)<limit:out.append(r);used.add(r['work_id'])
        else:remaining.append(r)
    return out+remaining[:max(0,limit-len(out))]


def main():
    freeze_verify();inp=load_canonical();integ=integrity();require(integ['passed'],'Integrity failure')
    gate=load(ROOT/'00_CHECKPOINTS/R1D1_GATE_DECISION.json');det=load(ROOT/'00_CHECKPOINTS/DETERMINISMO_R1D1.json')
    require(gate['passed'] and det['passed'],'Release requires gate and two deterministic full runs')
    full=load(ROOT/'07_EXECUCAO_COMPLETA/R1D1_RUN1_SUMMARY.json')
    require(full==load(ROOT/'07_EXECUCAO_COMPLETA/R1D1_RUN2_SUMMARY.json'),'Full summaries differ')
    admitted=load(ROOT/'07_EXECUCAO_COMPLETA/R1D1_RUN1_ADMISSIVEIS.json')['rows']
    review=load(ROOT/'07_EXECUCAO_COMPLETA/R1D1_RUN1_REVISAO.json')['rows']
    reg=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D1.json')
    ledger=load(ROOT/LABELS);labels={key(p):p for p in ledger['pairs']}
    alpha=load(HISTORICAL);arows=alpha['candidatos'];aby={(r['dispositivo_id'],r['obra_id']):r for r in arows}
    selected=[r for r in admitted if r['selected']]
    # Validate every release proof and its dependencies; this is audit of output,
    # not another regression or integral evaluation pass.
    problems=[];verified=0
    for r in admitted+review:
        d=inp.devices[r['device_id']];w=inp.works[r['work_id']]
        es={e['evidence_id']:e for e in w['evidences']};ns={n['nucleus_id']:n for n in d['nuclei']};proven={p['nucleus_id'] for p in r['proofs']}
        if d['text_identity_status']=='FONTE_EM_REVISAO':problems.append(dict(pair=key(r),issue='source under review published'))
        for p in r['proofs']:
            verified+=1;n=ns[p['nucleus_id']];c=n['contracts_by_relation'][p['contract_index']]
            if not set(n['depends_on'])<=proven:problems.append(dict(pair=key(r),issue='missing anchor'))
            if not p['evidence_ids']:problems.append(dict(pair=key(r),issue='empty proof'))
            for eid in p['evidence_ids']:
                e=es[eid]
                if not (e['state']=='VALIDADA' and e['polarity']=='AFIRMADA' and match_claim(inp,e['claim'],c['requires'])):problems.append(dict(pair=key(r),issue='invalid supporting assertion',evidence_id=eid))
    write('00_CHECKPOINTS/R1D1_FULL_STRUCTURAL_AUDIT.json',dict(at=now(),proof_routes_checked=verified,problems=problems,passed=not problems,
        method='Auditoria das provas persistidas: fontes, afirmações, argumentos tipados e dependências. Não cria rótulos humanos.',
        semantic_limit='Integridade de prova tipada não estima precisão semântica de vínculos inéditos. A revisão humana permanece necessária.'))
    require(not problems,'Severe full structural failure; no RC')
    metrics=dict(full=full,admissible=concentration(admitted),selected=concentration(selected),
        distributions=distributions(inp,admitted),selection_distributions=distributions(inp,selected),
        editorial_queue=dict(proof_review=len(review),admissible_without_historical_score=full['admissible_unscored'],
            nonbinary_known=len(reg['cases'])-reg['matrix']['binary_total'],do_not_sum='Categorias podem se sobrepor; não são um novo estado de admissibilidade.'),
        coverage=dict(admissible_devices=len({r['device_id'] for r in admitted}),total_devices=3461,works_used=len({r['work_id'] for r in admitted}),total_works=69,
            devices_with_any_nucleus=full['represented_devices']),
        caveat='Execução exaustiva com representações parciais; precisão de 100% pertence ao benchmark conhecido/adjudicado, não ao universo sem rótulos.')
    write('07_EXECUCAO_COMPLETA/METRICAS_COMPLETAS_R1D1.json',metrics)
    comparison={}
    for name,path in [('R1C','06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1C.json'),('R1D','06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D.json'),('R1D1','06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D1.json')]:
        j=load(ROOT/path);known={key(r):r for r in j['cases']}
        common=[]
        for p in ledger['pairs']:
            s=known[key(p)]['admissibility'];common.append(dict(metric=metric(p['label'],s),historical_metric=metric(p['rotulo_historico'],s)))
        hits=[r for r in j['cases'] if r['admissibility']=='ADMISSIVEL']
        comparison[name]=dict(scope='398 pares conhecidos',common_adjudicated_labels=matrix(common),historical_labels=matrix(common,'historical_metric'),
            states=dict(collections.Counter(r['admissibility'] for r in j['cases'])),known_coverage_concentration=concentration(hits),
            full_execution=None if name in ['R1C','R1D'] else metrics['admissible'],
            auditability='Provas tipadas, fontes, escopos e hashes rastreáveis.',notes='R1C/R1D globais não executadas; cobertura/concentração conhecidas não comparáveis a totais globais.')
    common=[]
    for p in ledger['pairs']:
        predicted=aby.get(key(p),{}).get('aprovavel_alpha3',False)
        state='ADMISSIVEL' if predicted else 'EVIDENCIA_INSUFICIENTE'
        common.append(dict(metric=metric(p['label'],state),historical_metric=metric(p['rotulo_historico'],state)))
    ahits=[dict(work_id=r['obra_id'],device_id=r['dispositivo_id']) for r in arows if r['aprovavel_alpha3']]
    aselected=[dict(work_id=r['obra_id'],device_id=r['dispositivo_id']) for r in arows if r['selecionado_final']]
    comparison['Alpha3']=dict(scope='Resultado persistido de 238809 pares; métricas conhecidas calculadas sobre os mesmos 398 IDs, sem reexecutar engine.',
        common_adjudicated_labels=matrix(common),historical_labels=matrix(common,'historical_metric'),
        full=dict(possible_pairs=alpha['total_pares'],pre_filter=alpha['total_pre_filtro'],post_filter=alpha['total_pos_filtro'],selected=alpha['links_selecionados']),
        admissible=concentration(ahits),selected=concentration(aselected),states=dict(collections.Counter(r['status_alpha3'] for r in arows)),
        auditability='Scores, temas e gates legados persistidos; não possui o mesmo contrato de prova tipada do V2.',
        editorial_queue='Estados legados não equivalem automaticamente a REVISAO_EDITORIAL V2.')
    comparison['FULL_R1D1']=dict(scope='69 x 3461 integral, duas execuções determinísticas',known_quality=reg['matrix'],
        full=full,coverage_concentration=metrics['admissible'],editorial_queue=metrics['editorial_queue'],
        auditability='Cada rota de prova possui núcleo, evidências, fontes, escopo afirmado/não afirmado e versões/hashes.',global_precision=None,
        global_precision_reason='Sem rótulos independentes para todo o universo; holdout fechado.')
    write('09_RELATORIOS/COMPARACAO_ALPHA3_R1C_R1D_R1D1.json',comparison)
    md=['# Comparação de versões','', 'Mesmos 398 pares e ledger adjudicado congelado para a coluna principal. Engines antigas não reexecutadas.','',
        '| Versão | TP | FP | TN | FN | Precision | Recall | Escopo |','|---|---:|---:|---:|---:|---:|---:|---|']
    for name in ['Alpha3','R1C','R1D','R1D1']:
        m=comparison[name]['common_adjudicated_labels'];md.append(f"| {name} | {m['TP']} | {m['FP']} | {m['TN']} | {m['FN']} | {m['precision']:.4%} | {m['recall']:.4%} | 375 binários / 398 conhecidos |")
    md += ['', 'R1C e R1D não possuem execução global; não inventar volume, fila, cobertura ou concentração globais. O JSON acompanha suas métricas de cobertura/concentração apenas no subconjunto conhecido e a matriz histórica separada.','',
        f"Alpha3: {len(ahits)} aprováveis, {len(aselected)} selecionados. R1D1 global: {len(admitted)} admissíveis, {len(review)} em revisão probatória, {len(selected)} selecionados pela mesma regra de score histórico.",
        '',f"Concentração Alpha3 aprováveis: {comparison['Alpha3']['admissible']}",'',f"Concentração R1D1 admissíveis: {metrics['admissible']}",'',
        'Volume, evidência e auditabilidade são distintos: admissíveis V2 têm prova tipada; links novos sem score histórico são preservados com null, sem inventar score ou usar score para admitir. A validação conhecida não comprova precisão global.']
    write('09_RELATORIOS/COMPARACAO_ALPHA3_R1C_R1D_R1D1.md','\n'.join(md)+'\n')

    # One reference per proof route; link metrics use unique work-device pairs.
    refs=[]
    compiler_hashes={p:file_hash(ROOT/'05_COMPILADOR'/p) for p in ['proof_compiler_r1.py','proof_compiler_v2.py','canonical_input_r1d1.py']}
    for r in sorted(admitted,key=key):
        w=inp.works[r['work_id']];d=inp.devices[r['device_id']];ev={e['evidence_id']:e for e in w['evidences']}
        for p in r['proofs']:
            # Some rows have mixed review and approved routes. Publish only an
            # admissible proof; never treat the existence of another proof as approval.
            if p['requires_editorial_review']:continue
            es=[ev[eid] for eid in p['evidence_ids']]
            ref_id=digest(dict(device=r['device_id'],work=r['work_id'],nucleus=p['nucleus_id'],contract=p['contract_index']))[:24]
            explanation=' '.join(e['source']['paraphrase'] for e in es)
            explanation+=f" Essa evidência sustenta {p['relation']} do objeto {', '.join(p['legal_proposition']['objetos'])} no núcleo indicado, dentro do escopo descrito."
            refs.append(dict(reference_id=ref_id,obra=w['nome'],work_id=w['work_id'],tipo=w['tipo'],ano=w['ano'],
                dispositivo=r['device_id'],device_id=r['device_id'],texto_dispositivo=d['text'],nucleo_id=p['nucleus_id'],relacao_pedagogica=p['relation'],
                objeto_alcancado=p['object_reached'],POR_QUE_ESTA_OBRA_SE_RELACIONA=explanation,score_editorial=r['editorial_score'],
                score_provenance='Score Alpha3 congelado; ausente permanece null. Não participa da admissibilidade.',selected_legacy_ranking=r['selected'],
                evidencias=es,fontes=[e['source'] for e in es],escopo_afirmado=dict(proposicao=p['legal_proposition'],contrato=p['affirmed_scope'],limite=p['scope_policy'],ancoras=p['anchors']),
                escopo_nao_afirmado=p['not_affirmed'],proveniencia=dict(status='CANDIDATO_PARA_REVISAO_HUMANA',pipeline='R1D1',
                    evidence_provenance=[e['provenance'] for e in es],legal_provenance=next(n['provenance'] for n in d['nuclei'] if n['nucleus_id']==p['nucleus_id'])),
                versions_hashes=dict(input_hash=inp.hash,device_source_version=d['source_version'],device_source_hash=d['source_hash'],
                    evidence_hashes={e['evidence_id']:digest(e) for e in es},source_hashes=p['source_hashes'],proof_hash=digest(p),compiler_hashes=compiler_hashes,
                    label_ledger_sha256=file_hash(ROOT/LABELS),patch_sha256=file_hash(ROOT/'02_DISPOSITIVOS/PATCH_ART205_R1D1.json'))))
    require(len({r['reference_id'] for r in refs})==len(refs),'Duplicate reference IDs')
    require({(r['device_id'],r['work_id']) for r in refs}=={key(r) for r in admitted},'Release lost an admissible pair')
    rc='08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1/'
    write(rc+'REFERENCIAS_RC1.json',dict(schema='CF_REFERENCIAS_V2_RC1',input_hash=inp.hash,reference_unit='uma rota de prova admissível por núcleo/contrato; várias referências podem pertencer ao mesmo vínculo',
        total_references=len(refs),unique_links=len(admitted),references=refs))

    known_proofs={key(r):r for r in load(ROOT/'06_BENCHMARKS/PROVAS_EXPANSAO_R1D1.json')['rows']}
    insuff=[];hard=[]
    for k,p in known_proofs.items():
        if p['state']!='EVIDENCIA_INSUFICIENTE':continue
        label=labels[k]
        if label['label'] in ['APROVAR','EVIDENCIA_INSUFICIENTE','PENDENTE_HUMANO']:insuff.append(p)
        if label['label']=='REJEITAR':hard.append(p)
    new=[r for r in admitted if not aby.get(key(r),{}).get('aprovavel_alpha3',False)]
    novel_candidate=[r for r in admitted if key(r) not in aby]
    groups={'APROVADOS_RC1':admitted,'REVISAO_EDITORIAL':review,'EVIDENCIA_INSUFICIENTE_ALTO_POTENCIAL':insuff,
        'NOVOS_VINCULOS_NAO_ALPHA3':new,'REJEITADOS_DIFICEIS':hard}
    sample_counts={}
    for name,pool in groups.items():
        sample=sample_diverse(pool);items=[]
        for r in sample:
            w=inp.works[r['work_id']];ids={e for p in r['proofs'] for e in p['evidence_ids']}
            items.append(dict(device_id=r['device_id'],work_id=r['work_id'],obra=w['nome'],tipo=w['tipo'],ano=w['ano'],
                state_pipeline=r['state'],review_status='PENDENTE_REVISAO_HUMANA',new_human_label=None,
                known_label=labels.get(key(r),{}).get('label'),proofs=r['proofs'],unmet_contracts=r['unmet_contracts'],
                evidence_dossier=w['evidences'],constitutional_text=inp.devices[r['device_id']]['text'],
                alpha3_candidate=key(r) in aby,alpha3_approved=aby.get(key(r),{}).get('aprovavel_alpha3',False)))
        sample_counts[name]=dict(pool=len(pool),sample=len(items))
        write(rc+'AMOSTRAS/'+name+'.json',dict(group=name,selection='Até 25 pares, primeiro diversidade por obra e depois ordem de dispositivo/obra; não é amostra aleatória nem novo gold label.',
            semantic_definition='Alto potencial usa rótulos já existentes; REJEITADOS_DIFICEIS usa rejeição adjudicada, não afirma INCOMPATIVEL factual.',input_hash=inp.hash,pool_size=len(pool),items=items))
        lines=[f'# {name}','',f'{len(items)} pares para revisão humana, universo do grupo: {len(pool)}. Nenhum novo rótulo atribuído.','', '| Obra | Dispositivo | Estado do pipeline | Revisão |','|---|---|---|---|']
        lines += [f"| {r['obra']} | {r['device_id']} | {r['state_pipeline']} | PENDENTE |" for r in items]
        write(rc+'AMOSTRAS/'+name+'.md','\n'.join(lines)+'\n')
    write(rc+'NOVOS_VINCULOS_RESUMO.json',dict(new_vs_alpha3_approved=len(new),absent_from_alpha3_589_candidates=len(novel_candidate),
        distinction='Não aprovável em Alpha3 inclui candidato recusado; ausente dos 589 é novidade de recuperação.',
        new_pairs=[dict(device_id=r['device_id'],work_id=r['work_id']) for r in new],sample_counts=sample_counts))
    write(rc+'METADADOS_RC1.json',dict(at=now(),status='RC1_OFFLINE_PARA_REVISAO',input_hash=inp.hash,unique_links=len(admitted),references=len(refs),
        known_matrix=reg['matrix'],global_quality='NÃO ESTIMADA; holdout fechado',full_summary=full,metrics=metrics,samples=sample_counts,
        no_firmware=True,no_idx=True,no_sd=True,no_official_catalog_change=True,no_official_dna_change=True,new_scores=0,new_thresholds=0,
        pending='Revisão humana de vínculos inéditos, oito pendências adjudicadas preservadas e admissíveis sem score histórico; não ajustar o freeze.',
        next_step='Revisar as cinco amostras RC1 e registrar decisões humanas versionadas sem alterar os rótulos congelados nem abrir o holdout.'))
    write(rc+'README.md','# CF_REFERENCIAS_V2_RC1 — R1D1\n\n'+
        f"{len(admitted)} vínculos únicos, {len(refs)} referências por rota de prova admissível, {len({r['device_id'] for r in admitted})} dispositivos cobertos, {len({r['work_id'] for r in admitted})} obras utilizadas.\n\n"+
        'REFERENCIAS_RC1.json inclui obra/tipo/ano, dispositivo/núcleo, natureza, objeto, explicação baseada na prova, score histórico ou null, evidências/fontes, escopos e proveniência/hashes. Uma referência é uma rota de prova; métricas de concentração contam vínculos únicos, sem duplicar rotas.\n\n'+
        'Duas execuções canônicas de 238.809 pares produziram hashes idênticos. O score não admite vínculos. A seleção histórica permanece em campo separado; admissíveis sem score não recebem nota inventada.\n\n'+
        'A precisão conhecida não é precisão global. As amostras são para revisão humana e não acrescentam rótulos. A cobertura de representações segue parcial; FONTE_EM_REVISAO e provas que exigem revisão não são publicadas como referências admissíveis. Holdout fechado. Nenhuma integração em firmware, IDX ou SD.\n')
    report=['# Encerramento R1D1','',
        'A rota histórica do art.205 foi deslocada de N3 para N1, já autônomo no texto. Requisitos EDUCACAO+CIDADANIA e HISTORIAR/ANALISAR preservados. N2 e dependências dos núcleos finalísticos permanecem intactos.','',
        'Impacto: quatro pares conhecidos e 69 pares potenciais do art.205. Somente Cidadania foi recuperado; onze controles sintéticos bloquearam temas isolados e finalidades sem âncora.','',
        f"Regressão única: {reg['matrix']}. Comparação histórica: {reg['historical_label_matrix']}.",'',
        '35 negativos recentes e 10 pareados preservados; grupo recente de 20 conserva 2 TP + 18 TN; mecanismos conservam 12/15; 25 positivos recentes conservam 15/25. A política D não foi revertida nem seus cinco TP históricos recuperados artificialmente.','',
        f"Execução integral: {full['evaluated_pairs']} pares, {full['candidates']} candidatos, {full['proof_attempted_pairs']} provas por par tentadas, {full['contract_routes_attempted']} rotas contratuais tentadas. Estados: {full['states']}.",'',
        f"Cobertura e concentração: {metrics['admissible']}",'',
        f"Distribuições: {metrics['distributions']}",'',
        f"RC1: {len(refs)} referências de prova / {len(admitted)} vínculos. Seleção histórica: {len(selected)}. Admissíveis sem score: {full['admissible_unscored']}. Novos versus aprováveis Alpha3: {len(new)}; fora dos antigos 589: {len(novel_candidate)}.",'',
        'Determinismo: duas execuções integrais; bytes gzip, conteúdo, estados, provas e ranking coincidem. Paridade 398/398 com regressão em cada execução.','',
        f"Integridade: {integ}",'',
        'Principal pendência: revisão humana da qualidade semântica dos vínculos novos, das oito pendências adjudicadas e dos admissíveis sem score. Nenhuma precisão global inferida.','',
        'Próximo passo: revisar as cinco amostras em 08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1/AMOSTRAS, registrando decisões em ledger separado. Preservar o holdout fechado; não integrar firmware/SD/IDX.','']
    write('09_RELATORIOS/RELATORIO_FINAL_R1D1.md','\n'.join(report))
    write('09_RELATORIOS/RESULTADO_FINAL_R1D1.json',dict(at=now(),status='CF_REFERENCIAS_V2_RC1',correction=True,regression=reg['matrix'],historical=reg['historical_label_matrix'],
        gate=True,full_execution=True,full=full,metrics=metrics,rc1=True,references=len(refs),unique_links=len(admitted),samples=sample_counts,
        determinism=det,integrity=integ,next_step='Revisar cinco amostras RC1; registrar decisões humanas separadas; preservar holdout fechado e não integrar firmware/IDX/SD.'))
    write('00_CHECKPOINTS/INTEGRITY_R1D1_FINAL.json',integ)
    write('00_CHECKPOINTS/RESUME_STATE_R1D1.json',dict(at=now(),status='CF_REFERENCIAS_V2_RC1',input_hash=inp.hash,regression_runs=1,full_runs=2,holdout_opened=False,
        next_step='Revisão humana das cinco amostras RC1, com novo ledger separado; nenhum novo ajuste automático.'))
    files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=file_hash(p),bytes=p.stat().st_size) for p in sorted(ROOT.rglob('*')) if p.is_file() and ('R1D1' in p.name or 'r1d1' in p.name or 'CF_REFERENCIAS_V2_RC1' in p.parts)]
    write(rc+'MANIFEST.json',dict(at=now(),input_hash=inp.hash,self_excluded=True,files=files,total=len(files)))
    print('RC1',len(refs),'references',len(admitted),'links',metrics['admissible'],flush=True)


if __name__=='__main__':main()
