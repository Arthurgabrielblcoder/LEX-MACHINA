"""Read public source URLs and keep retrieval metadata only, not page contents."""
import concurrent.futures, gzip, hashlib, html, json, re, sys, urllib.request, zlib
from pathlib import Path
from enriquecer_v1 import ROOT, REPORT, dossier, dump, load, now
from html.parser import HTMLParser
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','svg','noscript'): self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style','svg','noscript') and self.skip: self.skip-=1
    def handle_data(self,data):
        if not self.skip and data.strip(): self.parts.append(data.strip())
def fetch(job):
    n,url,tier=job
    meta=dict(number=n,url=url,tier=tier,accessed_on=now()[:10],consulted_at=now())
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(request,timeout=25) as response:
            raw=response.read();meta.update(final_url=response.url,http_status=response.status,snapshot_sha256=hashlib.sha256(raw).hexdigest(),verificacao='PAGINA_CONSULTADA')
            encoding=response.headers.get('Content-Encoding','')
            if encoding=='gzip' or raw[:2]==b'\x1f\x8b': raw=gzip.decompress(raw)
            elif encoding=='deflate': raw=zlib.decompress(raw)
        content=raw.decode('utf-8',errors='replace')
        if content.count('\ufffd') > max(5,len(content)//100):
            raise ValueError('Resposta não decodificada como texto legível; requer leitor alternativo')
        if '/api/appdetails' in url:
            data=json.loads(content); app=next(v['data'] for v in data.values() if v.get('success'))
            content=app.get('about_the_game','')
        parser=Text();parser.feed(content); txt=' '.join(parser.parts)
        meta['caracteres_texto']=len(txt)
        paragraphs='\n'.join(p for p in parser.parts if len(p)>100)
        return meta,paragraphs if len(paragraphs)>400 else txt
    except Exception as e:
        meta.update(verificacao='FALHA_DE_ACESSO',erro=str(e));return meta,''
def run(ns, custom=None):
    jobs=[]
    for n in ns:
        d=dossier(n); s=ROOT/'03_FONTES'/f'STEAM_{n:03}.json'
        if n<=50 and s.exists() and load(s).get('api_url'): jobs.append((n,load(s)['api_url'],'A'))
        else: jobs.extend((n,x['url'],x['tier']) for x in d['fontes'][:2])
    if custom: jobs=custom
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for meta,txt in pool.map(fetch,jobs):
            path=ROOT/'03_FONTES/ENRIQUECIMENTO_V1'/f"{meta['number']:03}_{hashlib.sha256(meta['url'].encode()).hexdigest()[:12]}.json"
            dump(path,meta)
            print(json.dumps(meta,ensure_ascii=False),flush=True)
            if txt:
                if meta['number']<=50 and '/api/appdetails' in meta['url']: txt='[Descrição Steam consultada; conteúdo prévio disponível em STEAM_NNN.json]'
                else:
                    patterns={164:'Americans of all ages',165:'3. Arendt',167:'About Why Nations Fail',169:'Description',179:'Description'}
                    pos=txt.find(patterns.get(meta['number'],'\x00'));txt=txt[max(0,pos):]
                print(txt[:7500],flush=True)
if __name__=='__main__':
    if sys.argv[1]=='custom': run([],load(Path(sys.argv[2])))
    else: run(list(map(int,sys.argv[1:])))
