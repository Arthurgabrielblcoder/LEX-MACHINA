"""Append-only enrichment support. Never imports or executes the engine."""
import copy, datetime, hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent
REPORT = ROOT / '06_RELATORIOS'
OVER = ROOT / '04_DOSSIERS' / 'ENRIQUECIMENTO_V1'
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)+'\n', encoding='utf-8')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def queue():
    rows=load(REPORT/'ESTIMATIVA_ENRIQUECIMENTO.json')['obras']
    return sorted((x for x in rows if x['estimativa']!='COMPLETA_PROVAVEL'), key=lambda x:(0 if x['estimativa']=='+2_OU_MAIS' else 1 if x['tipo']=='JOGO' else 2,x['candidate_number']))
def dossier(n):
    w=next(x for x in queue() if x['candidate_number']==n)
    return load(ROOT/'04_DOSSIERS'/f"{w['work_id']}.json")
def baseline():
    p=REPORT/'BASELINE_ENRIQUECIMENTO_V1.json'
    assert not p.exists(), 'Baseline already exists'
    files=[x for x in ROOT.rglob('*') if x.is_file() and '__pycache__' not in x.parts]
    frozen=load(ROOT/'08_MANIFEST/INTEGRIDADE_ANTES.json')['files']
    checks=[dict(path=f['path'], expected=f['sha256'], actual=sha(ROOT.parent/f['path'])) for f in frozen]
    assert all(x['expected']==x['actual'] for x in checks)
    protected=[REPO/'firmware/LEX_MACHINA.ino/LEX_MACHINA.ino.ino']
    protected += sorted(x for x in REPO.rglob('*.IDX') if '.git' not in x.parts)
    protected += [Path(load(ROOT/'00_ENTRADA/REFERENCIA_CATALOGO_69.json')['path'])]
    catalogs={p.name:sha(p) for p in (ROOT/'07_CATALOGO_CANDIDATO').glob('CATALOGO_*.json')}
    assert catalogs['CATALOGO_EXPANSAO_200.json']=='5764d749f83d5c1ce99a84ff521178c048d922f40591dc9a598f2af543ec5c43'
    assert catalogs['CATALOGO_TOTAL_69_MAIS_APTAS.json']=='6bf04fec443416d0b9fd92b65a4254960a3b37691d171942fc5950e0ca14abb6'
    dump(p,dict(at=now(), cards=221, obras=199, candidatas=200, catalogos=catalogs, arquivos_expansao=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in sorted(files)], congelados=checks, externos=[dict(path=str(x),sha256=sha(x)) for x in protected]))
    dump(REPORT/'CORRECOES_DURANTE_ENRIQUECIMENTO.json',dict(correcoes=[],nota='Cards anteriores preservados integralmente; acréscimos em overlay versionado.'))
    dump(REPORT/'CHECKPOINT_ENRIQUECIMENTO.json',dict(estado='EM_ANDAMENTO', baseline_sha256=sha(p), fila=queue(), checkpoints=[]))
def inspect(ns):
    for n in ns:
        d=dossier(n)
        print(json.dumps(dict(number=n,title=d['titulo'],old=[dict(id=c['evidence_id'],type=c['content_type'],fact=c['claim']['factual_description']) for c in d['evidencias']],sources=d['fontes']),ensure_ascii=False))
        s=ROOT/'03_FONTES'/f'STEAM_{n:03}.json'
        if n<=50 and s.exists():
            data=load(s); print('STEAM:',data.get('about',data))
def checkpoint(decisions):
    assert 0<len(decisions)<=10
    p=REPORT/'CHECKPOINT_ENRIQUECIMENTO.json'; state=load(p)
    done=[n for cp in state['checkpoints'] for n in cp['obras_examinadas']]
    expected=[x['candidate_number'] for x in queue() if x['candidate_number'] not in done][:len(decisions)]
    assert [x['number'] for x in decisions]==expected, expected
    touched=[]; added=[]
    for dec in decisions:
        d=dossier(dec['number']); wid=d['work_id']; cards=[]
        for i, item in enumerate(dec.pop('new',[]),len(d['evidencias'])+1):
            source=copy.deepcopy(item['source']); assert source['verificacao']=='PAGINA_CONSULTADA'
            card=dict(evidence_id=f'{wid}-E{i:02}',work_id=wid,centrality=item.get('centrality','FORTE'),content_type=item['type'],not_targeted_to_device=True,
                claim=dict(predicate=item.get('predicate','ANALISAR'),objects=[],participants=[],subjects=[],context=[],effects=[],factual_description=item['fact']),
                ONTOLOGY_GAP=copy.deepcopy(d['evidencias'][0]['ONTOLOGY_GAP']), source=dict(source,paraphrase=item['fact'],supports=['fato_independente']),state='DOCUMENTADA_PRELIMINAR',
                provenance=dict(candidate_id=d['candidate_id'],collection='ENRIQUECIMENTO_V1',engine_executed=False,source_basis='Fonte consultada; paráfrase editorial; sem mapeamento ontológico final'),
                transposition_limits=['Não equivale a procedimento ou instituição brasileira.','A mecânica descreve possibilidades do jogo, sem afirmar ocorrência em toda partida.' if item['type']=='MECANICA_INTERATIVA' else 'O card descreve somente a representação ou argumento documentado na fonte; não formula conclusão jurídica.'],
                independencia_editorial=item['independence'])
            for k in ['modo_discursivo','unidade_documental','escopo_centralidade']:
                if k in item: card[k]=item[k]
            cards.append(card)
        dec.update(work_id=wid,titulo=d['titulo'],cards_antes=len(d['evidencias']),cards_adicionados=len(cards),evidence_ids=[x['evidence_id'] for x in cards],estado='ENRIQUECIDA' if cards else 'SEM_CARD_ADICIONAL_JUSTIFICADO',dossier_original_sha256=sha(ROOT/'04_DOSSIERS'/f'{wid}.json'))
        file=OVER/f'{wid}.json'; assert not file.exists()
        dump(file,dict(decisao=dec,evidencias_adicionais=cards)); touched.append(dict(path=file.relative_to(ROOT).as_posix(),sha256=sha(file))); added+=cards
    cp=dict(numero=len(state['checkpoints'])+1,at=now(),obras_examinadas=[x['number'] for x in decisions],cards_adicionados=len(added),cards_recusados=sum(len(d.get('rejeitados',[])) for d in decisions),fontes_novas=[s for d in decisions for s in d.get('fontes_novas',[])],arquivos=touched)
    state['checkpoints'].append(cp); state['obras_examinadas']=len(done)+len(decisions);state['cards_adicionados']=sum(x['cards_adicionados'] for x in state['checkpoints'])
    dump(REPORT/'CHECKPOINTS_ENRIQUECIMENTO'/f"CP_{cp['numero']:02}.json",cp); dump(p,state)
    print(json.dumps(cp,ensure_ascii=False))
if __name__=='__main__':
    if sys.argv[1]=='baseline': baseline()
    elif sys.argv[1]=='inspect': inspect(list(map(int,sys.argv[2:])))
    elif sys.argv[1]=='checkpoint': checkpoint(load(Path(sys.argv[2])))
