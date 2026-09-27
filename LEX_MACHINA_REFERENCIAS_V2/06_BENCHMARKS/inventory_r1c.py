"""Evaluation-only operational ledger; never imported by proof compilation."""
import json
import hashlib
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'05_COMPILADOR'))
from canonical_input_r1b import load_canonical
from proof_compiler_r1 import load


def inventory():
    inp=load_canonical()
    causal=load(ROOT/'06_BENCHMARKS/DECOMPOSICAO_CAUSAL_FN_R1B.json')['cases']
    baseline=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1B.json')
    decisions={(r['device_id'],r['work_id']):r for r in baseline['cases']}
    rows=[]
    for c in causal:
        did,wid=c['device_id'],c['work_id']; d,w=inp.devices[did],inp.works[wid]
        decision=decisions[(did,wid)]
        rows.append(dict(pair_id=hashlib.sha256((did+'|'+wid).encode()).hexdigest()[:20],
            obra=w['nome'],work_id=wid,dispositivo=did,rotulo_humano=decision['human_label'],decisao_R1B=decision['admissibility'],
            causa_principal=c['category'],causas_secundarias=c['secondary_categories'],
            nucleo_esperado=[dict(id=n['nucleus_id'],proposicao=n['proposition'],papel=n['role'],dependencias=n['depends_on']) for n in d['nuclei']],
            natureza_pedagogica_existente=sorted({r['relation'] for n in d['nuclei'] for r in n['contracts_by_relation']}),
            contratos_existentes=[dict(nucleo=n['nucleus_id'],contratos=n['contracts_by_relation']) for n in d['nuclei']],
            evidencias_existentes=w['evidences'],estado_evidencias={e['evidence_id']:e['state'] for e in w['evidences']},
            dimensao_ausente=c['reason'],fonte_disponivel=[e['source'] for e in w['evidences']],
            fonte_constitucional=dict(texto=d['text'],pais=d['hierarchical_context'],hash=d['source_hash']),
            acao_recomendada='ADJUDICACAO_SEM_ALTERACAO' if c['category']=='CONTRATO_DE_NATUREZA_INADEQUADO' else 'CONFERIR_FATOS_E_FONTES_SEM_ALTERAR_CONTRATOS',
            nota='Rótulo apenas prioriza investigação e mede regressão; não comprova o fato ou a natureza pedagógica.'))
    assert len(rows)==105 and len({r['pair_id'] for r in rows})==105
    return dict(version='INVENTARIO_OPERACIONAL_R1C_1',baseline_input_hash=inp.hash,total=105,rows=rows)


if __name__=='__main__': print(json.dumps(inventory(),ensure_ascii=False,separators=(',',':')))
