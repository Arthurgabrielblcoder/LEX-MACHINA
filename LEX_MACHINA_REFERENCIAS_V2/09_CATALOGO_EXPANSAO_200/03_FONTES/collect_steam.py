"""Read-only collection from the official Steam store; never runs a game or engine."""
import concurrent.futures,datetime,hashlib,html,json,re,sys,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'CatalogResearch/1.0'})
 with urllib.request.urlopen(req,timeout=35) as r:return json.load(r)
def clean(s):return html.unescape(re.sub('<[^>]+>',' ',s or ''))
def collect(c):
 n=c['number'];out=ROOT/'03_FONTES'/f'STEAM_{n:03}.json'
 if out.exists():
  cached=json.loads(out.read_text(encoding='utf-8'))
  if not cached.get('error'):return cached
 title=c['titulo_informado'];q='https://store.steampowered.com/api/storesearch/?'+urllib.parse.urlencode(dict(term=title,l='english',cc='US'))
 try:
  search=fetch(q);items=search.get('items',[])
  match=next((i for i in items if i['name'].casefold()==title.casefold()),None)
  if not match and items:match=items[0]
  if not match:raise ValueError('No store result')
  appid=match['id'];url=f'https://store.steampowered.com/api/appdetails?appids={appid}&l=english&cc=US'
  response=fetch(url)
  data=next(v for v in response.values() if v.get('success') and v.get('data',{}).get('steam_appid')==appid)
  assert data['success'];d=data['data']
  result=dict(number=n,input_title=title,matched_title=d['name'],app_id=appid,source_url=f'https://store.steampowered.com/app/{appid}/',api_url=url,query_url=q,tier='A',source_kind='Descrição oficial fornecida pelo publisher à plataforma',accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),developers=d.get('developers'),publishers=d.get('publishers'),release_date=d.get('release_date'),website=d.get('website'),type=d.get('type'),short_description=clean(d.get('short_description')),about=clean(d.get('about_the_game')),search_titles=[i['name'] for i in items],identity_requires_manual_confirmation=True)
 except Exception as e:result=dict(number=n,input_title=title,query_url=q,error=str(e),accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
 out.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'));return result
if __name__=='__main__':
 lo,hi=map(int,sys.argv[1:]);c=json.loads((ROOT/'00_ENTRADA/CANDIDATAS_200.json').read_text(encoding='utf-8'))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for r in pool.map(collect,[x for x in c if lo<=x['number']<=hi]):
   print(json.dumps({k:r.get(k) for k in ['number','matched_title','developers','publishers','release_date','short_description','error']},ensure_ascii=False),flush=True)
