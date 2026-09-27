"""Evaluation-only human-label ledger, loaded strictly after the proof freeze.

Never sends justifications, supplied features, decisions or grades to the compiler.
Repeated derived files are provenance, not independent human votes.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parent
sys.path.insert(0,str(ROOT/'05_COMPILADOR'))
from canonical_input import load_canonical
from proof_compiler_r1 import load, serialized, file_hash, require

NORMAL={'APROVAR':'APROVAR','APROVADO':'APROVAR','REJEITAR':'REJEITAR','REJEITADO':'REJEITAR'}


def walk(value, locator='$'):
    if isinstance(value,dict):
        yield locator,value
        for k,v in value.items():
            if k!='features_simulacao': yield from walk(v,locator+'.'+k)
    elif isinstance(value,list):
        for i,v in enumerate(value): yield from walk(v,locator+f'[{i}]')


def device_id(row):
    value=row.get('dispositivo_id',row.get('device_id',row.get('dispositivo')))
    if isinstance(value,str): return value if re.fullmatch(r'(?:CF88|ADCT):ART\.[^ ]+',value) else None
    if isinstance(value,dict):
        if value.get('chave_dispositivo'): return value['chave_dispositivo']
        if value.get('norma') and value.get('artigo'):
            s=f"{value['norma']}:ART.{value['artigo']}"
            for k,prefix in [('paragrafo','PAR'),('inciso','INC'),('alinea','AL')]:
                if value.get(k): s+=':'+prefix+'.'+str(value[k])
            return s
    return None


def build():
    inp=load_canonical(); freeze=load(ROOT/'00_CHECKPOINTS/EXPANSION_PROOFS_FREEZE.json')
    require(inp.hash==freeze['canonical_input_hash'],'proof/input mismatch before labels')
    for item in freeze['hashes']: require(file_hash(ROOT/item['path'])==item['sha256'],'compiler changed before labels')
    names=defaultdict(list)
    for w in inp.works.values(): names[w['nome']].append(w['work_id'])
    ledger=defaultdict(list); sources=[]; unresolved=[]; non_pair_files=[]
    def wid(row):
        value=row.get('obra_id',row.get('work_id'))
        if value in inp.works: return value
        opts=names.get(row.get('obra',row.get('nome','')),[])
        if len(opts)==1:return opts[0]
        opts=[w for w in opts if inp.works[w]['tipo']==row.get('tipo')]
        return opts[0] if len(opts)==1 else None
    # Exact frozen trees only. No compiler or current V2 output is scanned.
    paths=sorted(p for folder in REPO.glob('LEX_MACHINA_REFERENCIAS*') if folder.is_dir() and folder!=ROOT for p in folder.rglob('*.json'))
    for path in paths:
        raw=path.read_text(encoding='utf-8-sig')
        if not any('"'+k+'"' in raw for k in ('decisao_humana','decisao_humana_informada','status_humano')): continue
        data=json.loads(raw); entries=[]
        sid='SRC'+str(len(sources)+1).zfill(3)
        for loc,row in walk(data):
            decision=row.get('decisao_humana_informada',row.get('decisao_humana',row.get('status_humano')))
            if not isinstance(decision,str):continue
            did=device_id(row); work=wid(row)
            if did and work:
                entries.append((did,work,dict(source=sid,locator=loc,decision_raw=decision,
                    decision=NORMAL.get(decision,'PENDENTE'),case_id=row.get('benchmark_id',row.get('mecanismo_id',row.get('par_id',row.get('id_origem',row.get('id',row.get('numero')))))))))
            elif did or row.get('obra_id') and 'dispositivo' in row:
                unresolved.append(dict(file=path.relative_to(REPO).as_posix(),locator=loc,device_id=did,work_id=work,decision=decision,
                                       reason='Identidade não resolvida inequivocamente; não inferida por proximidade de nomes.'))
        if entries:
            sources.append(dict(id=sid,path=path.relative_to(REPO).as_posix(),sha256=file_hash(path),occurrences=len(entries)))
            for did,work,entry in entries: ledger[(did,work)].append(entry)
        else: non_pair_files.append(path.relative_to(REPO).as_posix())
    pairs=[]
    for (did,work), provenance in sorted(ledger.items()):
        decisions={p['decision'] for p in provenance if p['decision']!='PENDENTE'}
        label=next(iter(decisions)) if len(decisions)==1 else 'CONFLITO' if len(decisions)>1 else 'PENDENTE'
        pairs.append(dict(device_id=did,work_id=work,label=label,in_canonical_input=did in inp.devices,provenance=provenance))
    groups={}
    groupdefs=[('human134','LEX_MACHINA_REFERENCIAS_BENCHMARK_69_HUMANO_V1/BENCHMARK_HUMANO_134.json','casos'),
        ('external36','LEX_MACHINA_REFERENCIAS_VALIDACAO_V14_ALPHA3/RESULTADO_EXTERNO_ALPHA3.json','casos'),
        ('old176','LEX_MACHINA_REFERENCIAS_BENCHMARK_CF_V2/BENCHMARK_HUMANO_REFERENCIAS_CF_TOTAL.json','casos'),
        ('mechanisms15','LEX_MACHINA_REFERENCIAS_PREPARACAO_V14_ALPHA2/BENCHMARK_MECANISMO_POSITIVO_V1.json','casos'),
        ('negatives10','LEX_MACHINA_REFERENCIAS_PREPARACAO_V14_ALPHA2/NEGATIVOS_PAREADOS_MECANISMO.json','casos'),
        ('protected20','LEX_MACHINA_REFERENCIAS_VALIDACAO_V14_ALPHA3/REGRESSAO_TP_ALPHA3.json','casos')]
    def group_row(r,file):
        return dict(device_id=device_id(r),work_id=wid(r),label=NORMAL.get(r.get('decisao_humana_informada',r.get('decisao_humana',r.get('status_humano'))),'PENDENTE'),
                    source_file=file,case_id=r.get('benchmark_id',r.get('mecanismo_id',r.get('par_id',r.get('id',r.get('numero'))))),
                    historical_fn=bool(r.get('FN_conhecido_pendente_contexto_historico',False)))
    for name,file,key in groupdefs: groups[name]=[group_row(r,file) for r in load(REPO/file)[key]]
    file='LEX_MACHINA_REFERENCIAS_AUDITORIA_ASTRA_V1/TAXONOMIA_ERROS_589.json'
    recent=load(REPO/file)['resultados_humanos_80']
    groups['recent60']=[group_row(r,file) for r in recent['amostra_sobreviventes']]
    groups['recent20']=[group_row(r,file) for r in recent['amostra_rejeitados']]
    return dict(schema='HUMAN_LABELS_MASTER_V2', proof_input_hash=inp.hash, proof_stream_hash=freeze['proof_stream_sha256'],
        unique_pairs=len(pairs),counts=dict(Counter(p['label'] for p in pairs)),sources=sources,pairs=pairs,groups=groups,
        unresolved=unresolved,non_pair_files_excluded=non_pair_files,
        policy='Consenso por par, não voto por repetição. Divergências preservadas como CONFLITO. Grades de obras não são rótulos de pares. Nenhum campo entra como feature.')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--emit',action='store_true');args=p.parse_args();data=build()
    print(json.dumps({'files':{'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json':serialized(data)}} if args.emit else {
        'pairs':data['unique_pairs'],'counts':data['counts'],'sources':len(data['sources']),'unresolved':data['unresolved'],
        'groups':{k:len(v) for k,v in data['groups'].items()}},ensure_ascii=False))
