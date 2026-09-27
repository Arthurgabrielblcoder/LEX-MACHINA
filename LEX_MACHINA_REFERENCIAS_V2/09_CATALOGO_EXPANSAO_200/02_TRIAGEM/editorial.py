"""Standalone editorial dossier builder. Does not import or execute the engine."""
import json,hashlib,datetime,re,unicodedata
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes((json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8'))
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower())
def process(batch,rows):
 candidates=load(ROOT/'00_ENTRADA/CANDIDATAS_200.json');base=load(ROOT/'00_ENTRADA/REFERENCIA_CATALOGO_69.json')['obras']
 assert {r['number'] for r in rows}==set(range((batch-1)*25+1,batch*25+1))
 out=[];paths=[]
 for entry in rows:
  c=candidates[entry['number']-1];wid=c['work_id'];e=dict(c,**{k:v for k,v in entry.items() if k!='number'})
  e.setdefault('titulo_canonico',c['titulo_informado'].split(' — ')[0]);e.setdefault('titulo_original',e['titulo_canonico']);e.setdefault('titulo_ptbr',None)
  e.setdefault('pais_origem',None);e.setdefault('franquia',None)
  e.setdefault('metadata_pendente',[])
  if e['pais_origem'] is None:e['metadata_pendente'].append('País de produção não confirmado na fonte consultada; não inferido do cenário ou nacionalidade do autor.')
  if e['titulo_ptbr'] is None:e['metadata_pendente'].append('Título de edição brasileira não confirmado; null não significa inexistência.')
  aliases=set(norm(v) for v in [e['titulo_canonico'],e['titulo_original'],e['titulo_ptbr'],c['titulo_informado']] if v)
  comparisons=[]
  for w in base:
   titles=[w['titulo'],w.get('titulo_original','')]
   comparisons.append(dict(existing_id=w['id'],title=w['titulo'],same_medium=w['tipo']==e['tipo'],exact_normalized=bool(aliases&{norm(t) for t in titles if t})))
  e['comparacao_69']=comparisons;e['comparacoes_realizadas']=69
  e['status_catalogo']='CANDIDATO_NAO_INTEGRADO';e['not_targeted_to_device']=True
  e.setdefault('transposition_limits',['A evidência descreve a obra; não demonstra um instituto ou regra brasileira.'])
  e.setdefault('riscos',[]);e.setdefault('fontes',[])
  if e['status_triagem'] in ['APTA','APTA_COM_RESSALVA']:
   assert e.get('facts') and e['fontes'] and e.get('criador_principal') and e.get('ano'),e
   cards=[]
   for j,f in enumerate(e.pop('facts')):
    cards.append(dict(evidence_id=f'{wid}-E{j+1:02}',work_id=wid,centrality=f.get('centrality','CENTRAL'),content_type=f['content_type'],not_targeted_to_device=True,
      claim=dict(predicate=f.get('predicate','ANALISAR' if 'ARGUMENTO' in f['content_type'] else 'CONTROLAR' if f['content_type']=='MECANICA_INTERATIVA' else 'VIVENCIAR'),objects=f.get('objects',[]),participants=f.get('participants',[]),subjects=[],context=[],effects=[],factual_description=f['text']),
      ONTOLOGY_GAP=dict(status='REVISAO_SEMANTICA_PRE_INGESTAO',description='Descrição factual preservada. Objetos, participantes e qualificadores não preenchidos não devem ser inferidos; mapear explicitamente na ontologia congelada antes da ingestão.'),
      source=dict(e['fontes'][f.get('source_index',0)],paraphrase=f['text']),state='DOCUMENTADA_PRELIMINAR',provenance=dict(collection='EXPANSAO_200',candidate_id=c['candidate_id'],engine_executed=False,source_basis='Fonte concreta consultada; paráfrase editorial'),transposition_limits=e['transposition_limits']))
   e['evidencias']=cards;e['resumo_factual_curto']=' '.join(x['claim']['factual_description'] for x in cards)
   dossier=dict(e,titulo=e['titulo_canonico'],pais=e['pais_origem'],criadores=e['criador_principal'],provenance=dict(candidate_id=c['candidate_id'],batch=batch,ontology_changed=False,ingestion_ready=False))
   p=ROOT/'04_DOSSIERS'/f'{wid}.json';write(p,dossier);paths.append(p)
  else:e['evidencias']=[]
  p=ROOT/'03_FONTES'/f'{wid}.json';write(p,e['fontes']);paths.append(p);out.append(e)
 p=ROOT/'02_TRIAGEM'/f'LOTE_{batch:02}.json';write(p,out);paths.append(p)
 p=ROOT/'01_IDENTIDADE'/f'LOTE_{batch:02}.json';write(p,[{k:v for k,v in e.items() if k not in ['evidencias','resumo_factual_curto','facts']} for e in out]);paths.append(p)
 count=Counter(e['status_triagem'] for e in out)
 cp=ROOT/'06_RELATORIOS/CHECKPOINT_LOTES.json';checkpoints=load(cp) if cp.exists() else []
 assert not any(x['lote']==batch for x in checkpoints),'Batch already frozen'
 checkpoints.append(dict(lote=batch,intervalo=[(batch-1)*25+1,batch*25],processadas=25,aptas=count['APTA'],ressalva=count['APTA_COM_RESSALVA'],rejeitadas=sum(n for s,n in count.items() if s.startswith('REJEITADA')),fontes_em_revisao=count['FONTE_EM_REVISAO'],timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),hashes=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(paths)]))
 write(cp,checkpoints);print('LOTE',batch,dict(count),flush=True)
