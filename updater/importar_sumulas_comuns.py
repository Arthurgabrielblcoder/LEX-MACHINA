"""Súmulas comuns do STF e STJ, a partir das coleções oficiais."""
from __future__ import annotations
from datetime import datetime
import json, re
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from importar_stf_repercussao_geral import HEADERS_STF, _criar_session, _limpar, _relacoes_cdc

ORIGEM = "SUMULAS_COMUNS_OFICIAIS"
STF_LISTA = "https://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp?base=30"
STF_API = "https://portal.stf.jus.br/jurisprudencia/aplicacaosumulapesquisa.asp"
STF_DETALHE = STF_LISTA + "&sumula={id_stf}"
STF_CONSULTA_COMPLETA = "consumidor ou consumo ou fornecedor ou banco ou bancário ou seguro ou telefonia"
STJ_BUSCA = "https://processo.stj.jus.br/SCON/pesquisar.jsp?b=SUMU&tipo=sumula&ordenacao=%40NUM&l=100&i={inicio}"
STJ_ITEM = "https://processo.stj.jus.br/SCON/sumstj/toc.jsp?sumula={numero}.num."
STJ_CANCELADAS = "https://processo.stj.jus.br/SCON/pesquisar.jsp?b=SUMU&inde=%28sumula+adj+cancelada%29.emen%2Cinde.&l=100&i=1"
SINAIS_CONSUMERISTAS = (
    "consumidor", "código de defesa do consumidor", "lei 8.078", "lei nº 8.078",
    "cdc", "fornecedor", "plano de saúde", "instituição financeira",
    "instituições financeiras", "contrato bancário", "contratos bancários",
    "tarifa bancária", "cadastro de inadimplentes", "proteção ao crédito",
    "telefonia", "seguro saúde", "cobertura securitária", "contrato de seguro",
    "sistema financeiro nacional", "cartão de crédito", "dano moral",
)

def _oficial(url, tribunal):
    p=urlparse(url); host="portal.stf.jus.br" if tribunal=="STF" else "processo.stj.jus.br"
    if p.scheme!="https" or p.hostname!=host or p.port not in (None,443) or p.username or p.password or p.fragment:
        raise ValueError("URL fora da fonte oficial")
    return url

def _resposta(r,url,tribunal,json_esperado=False):
    _oficial(url,tribunal); r.raise_for_status()
    if r.status_code!=200 or not r.content or r.url!=url: raise ValueError("resposta vazia, redirecionada ou incompleta")
    texto=_limpar(BeautifulSoup(r.content,"html.parser").get_text(" ",strip=True)).lower()
    if any(x in texto for x in ("404 not found","página não encontrada","pagina nao encontrada","access denied","acesso negado","serviço indisponível")):
        raise ValueError("falso HTTP 200")
    if json_esperado:
        try: dados=json.loads(r.content)
        except (ValueError,UnicodeError) as e: raise ValueError("JSON oficial inválido") from e
        if not isinstance(dados,list) or not dados: raise ValueError("JSON oficial vazio")
        return dados
    return BeautifulSoup(r.content,"html.parser")

def _get(s,url,tribunal):
    return _resposta(s.get(url,headers=HEADERS_STF,timeout=60,allow_redirects=False),url,tribunal)

def _status(texto):
    t=texto.lower().replace("\u200b","")
    if "cancelada" in t: return "cancelado"
    if "superada" in t or "revogada" in t: return "superado"
    if "alterada" in t: return "alterado"
    return "vigente"

def _stf(s):
    soup=_get(s,STF_LISTA,"STF"); bloco=soup.select_one(".sumarioSumulas")
    if bloco is None: raise ValueError("lista STF não reconhecida")
    lista={}
    for a in bloco.select(".sumula-item > a[href]"):
        rot=_limpar(a.get_text(" ",strip=True)).replace("\u200b",""); m=re.match(r"Súmula\s+(\d+)",rot,re.I)
        href=a.get("href",""); q=re.search(r"[?&]sumula=(\d+)",href)
        if not m or not q: raise ValueError("item STF inválido")
        n=int(m.group(1)); lista[n]={"numero":n,"id_stf":int(q.group(1)),"situacao":_status(rot)}
    if len(lista)<700: raise ValueError("lista STF truncada")
    h={**HEADERS_STF,"X-Requested-With":"XMLHttpRequest","Referer":"https://portal.stf.jus.br/jurisprudencia/aplicacaosumula.asp"}
    r=s.post(STF_API,data={"base":"30","texto":STF_CONSULTA_COMPLETA,"numero":"","ramo":""},headers=h,timeout=60,allow_redirects=False)
    dados=_resposta(r,STF_API,"STF",True); encontrados={}
    for x in dados:
        if isinstance(x,dict) and "num" not in x:
            if x: raise ValueError("marcador STF inesperado")
            continue
        if not isinstance(x,dict) or set(("num","link","comentario"))-set(x): raise ValueError("registro STF incompleto")
        nome=_limpar(BeautifulSoup(str(x["num"]),"html.parser").get_text(" ")); m=re.fullmatch(r"Súmula\s+(\d+)(?:\s+\((?:cancelada|superada|revogada|alterada)\))?",nome,re.I)
        if not m or not str(x["link"]).isdigit() or not _limpar(BeautifulSoup(str(x["comentario"]),"html.parser").get_text(" ")): raise ValueError("registro STF inválido")
        n=int(m.group(1)); encontrados[n]={**lista.get(n,{}),"numero":n,"id_stf":int(x["link"]),"texto":_limpar(BeautifulSoup(str(x["comentario"]),"html.parser").get_text(" "))}
    if set(encontrados)!=set(lista) or any(encontrados[n]["id_stf"]!=lista[n]["id_stf"] for n in lista): raise ValueError("JSON STF não corresponde à lista oficial")
    return [encontrados[n] for n in sorted(encontrados)]

def _detalhe_stf(s,item):
    url=STF_DETALHE.format(id_stf=item["id_stf"]); soup=_get(s,url,"STF")
    tit=soup.select("section.conteudo .container div.titulo"); primeiro=tit[0] if tit else None
    p=primeiro.find_next_sibling("div",class_="parCOM") if primeiro else None
    nome=_limpar(primeiro.get_text(" ",strip=True) if primeiro else "").replace("\u200b","")
    texto=_limpar(p.get_text(" ",strip=True) if p else "")
    if not re.fullmatch(rf"Súmula\s+{item['numero']}(?:\s+\([^)]*\))?",nome,re.I) or texto!=item["texto"]: raise ValueError("detalhe STF divergente")
    obs=""
    for t in tit[1:]:
        if _limpar(t.get_text(" ")).lower() in {"observação","observações"}:
            p=t.find_next_sibling("div",class_="parCOM"); obs=_limpar(p.get_text(" ",strip=True) if p else ""); break
    ds=re.findall(r"Data (?:de publicação|de aprovação) do enunciado:\s*(?:Sessão Plenária de |(?:DJE|DJ)\s+(?:de\s+)?)?(\d{1,2}(?:º)?-\d{1,2}-\d{4})",obs,re.I)
    data=ds[0].replace("º","") if ds else ""
    if data: datetime.strptime(data,"%d-%m-%Y")
    return {**item,"url":url,"data":data,"observacao":obs}

def _stj(s):
    todos=[]; total=None
    for inicio in range(1,1000,100):
        url=STJ_BUSCA.format(inicio=inicio); soup=_get(s,url,"STJ")
        cab=_limpar((soup.select_one(".numDocs") or soup).get_text(" ",strip=True)); m=re.search(r"(\d+)\s+súmulas",cab,re.I)
        if total is None:
            if not m: raise ValueError("total STJ ausente")
            total=int(m.group(1))
        grades=soup.select("#listaSumulas .gridSumula")
        if not grades: raise ValueError("página STJ vazia")
        for g in grades:
            n=_limpar((g.select_one(".numeroSumula") or g).get_text())
            bloco=g.select_one(".blocoVerbete")
            if bloco:
                bloco=BeautifulSoup(str(bloco),"html.parser")
                for ramo in bloco.select(".ramoSumula"): ramo.decompose()
            corpo=_limpar((bloco or g).get_text(" ",strip=True))
            if not n.isdigit() or not corpo: raise ValueError("registro STJ incompleto")
            mi=re.match(r"(.+?)\s+\(([^()]*(?:julgado|SÚMULA CANCELADA)[^()]*)\)\s*$",corpo,re.I)
            texto=_limpar(mi.group(1) if mi else corpo); meta=mi.group(2) if mi else ""
            datas=re.findall(r"(?:julgado em|DJe? de?)\s*(\d{1,2}/\d{1,2}/\d{4})",meta,re.I)
            todos.append({"numero":int(n),"texto":texto,"situacao":"vigente","data":datas[-1] if datas else "","url":STJ_ITEM.format(numero=n)})
        if len(todos)>=total: break
    if total is None or len(todos)!=total or len({x["numero"] for x in todos})!=total: raise ValueError("coleção STJ truncada ou duplicada")
    canceladas=_get(s,STJ_CANCELADAS,"STJ")
    total_canceladas=_limpar((canceladas.select_one(".numDocs") or canceladas).get_text(" ",strip=True))
    nums_cancelados={int(_limpar(x.get_text())) for x in canceladas.select("#listaSumulas .numeroSumula")}
    mc=re.search(r"(\d+)\s+súmulas",total_canceladas,re.I)
    if not mc or int(mc.group(1))!=len(nums_cancelados) or not nums_cancelados.issubset({x["numero"] for x in todos}):
        raise ValueError("lista oficial de cancelamentos STJ inválida")
    for x in todos:
        if x["numero"] in nums_cancelados: x["situacao"]="cancelado"
    return sorted(todos,key=lambda x:x["numero"])

def _consumidor(x): return any(p in x["texto"].lower() for p in SINAIS_CONSUMERISTAS)

def _novo(x,tribunal,hoje):
    rel=_relacoes_cdc(x["texto"]+" "+x.get("observacao",""))
    return {"tribunal":tribunal,"tipo":"sumula","numero":x["numero"],"tema":f"Súmula {x['numero']} — {tribunal}","arquivo":f"{tribunal.lower()}_sumula_{x['numero']}.txt","pasta_destino":f"19_JURISPRUDENCIA/{tribunal}/SUMULAS","texto":x["texto"],"texto_oficial_verificado":x["texto"],"relacionado_a":rel,"fonte":f"{tribunal} — Súmula {x['numero']}","status":x["situacao"],"data_publicacao":x["data"],"url_fonte":x["url"],"ultima_verificacao":hoje,"origem_importacao":ORIGEM}

def atualizar_sumulas_comuns(caminho:Path,verbose=True,outros_registros=()):
    res={"ok":False,"STF":{},"STJ":{}}; s=None
    try:
        bruto=caminho.read_bytes(); cat=json.loads(bruto.decode("utf8"))
        if not isinstance(cat,list) or any(not isinstance(x,dict) for x in cat): raise ValueError("catálogo inválido")
        base=[x for x in cat if x.get("origem_importacao")!=ORIGEM]
        antigos=[x for x in base if x.get("tipo")=="sumula" and x.get("tribunal")=="STJ"]
        s=_criar_session(); stf=_stf(s); stj=_stj(s)
        cstf=[x for x in stf if _consumidor(x)]; cstj=[x for x in stj if _consumidor(x)]
        cstf=[_detalhe_stf(s,x) for x in cstf]
        hoje=datetime.now().astimezone().date().isoformat()
        existentes={(x.get("tribunal"),x.get("tipo"),x.get("numero")):x for x in base}
        novos=[]
        for fonte,trib in ((cstf,"STF"),(cstj,"STJ")):
            for x in fonte:
                chave=(trib,"sumula",x["numero"])
                if chave in existentes:
                    atual=existentes[chave]
                    if trib=="STJ" and atual not in antigos: raise ValueError("ID STJ duplicado")
                    atual.setdefault("texto_oficial_verificado",x["texto"]); atual.setdefault("url_fonte",x["url"])
                    atual.setdefault("data_publicacao",x["data"]); atual.setdefault("situacao_oficial",x["situacao"])
                    atual.setdefault("relacoes_automaticas_cdc",_relacoes_cdc(x["texto"]))
                elif x["situacao"]=="vigente": novos.append(_novo(x,trib,hoje))
        final=base+novos
        chaves=set()
        for x in [*final,*outros_registros]:
            k=(x.get("tribunal"),x.get("tipo"),x.get("numero"))
            if k in chaves: raise ValueError("registro jurisprudencial duplicado")
            chaves.add(k)
        tmp=caminho.with_suffix(caminho.suffix+".tmp"); tmp.write_text(json.dumps(final,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n"); tmp.replace(caminho)
        for nome,dados,cands in (("STF",stf,cstf),("STJ",stj,cstj)):
            imp=[x for x in final if x.get("tribunal")==nome and x.get("tipo")=="sumula"]
            auto=[(x["numero"],_relacoes_cdc(x["texto"]+" "+x.get("observacao",""))) for x in cands]; auto=[x for x in auto if x[1]]
            res[nome]={"encontrados":len(dados),"vigentes":sum(x["situacao"]=="vigente" for x in dados),"consumeristas":len(cands),"importados":len(imp),"ja_existiam":len(antigos) if nome=="STJ" else 0,"vinculos_explicitos":auto}
        res["ok"]=True
        if verbose: print("Súmulas comuns:",json.dumps(res,ensure_ascii=False))
    except Exception as e:
        res["erro"]=str(e)
        if verbose: print("Súmulas comuns: catálogo anterior preservado:",e)
    finally:
        if s is not None:s.close()
    return res
