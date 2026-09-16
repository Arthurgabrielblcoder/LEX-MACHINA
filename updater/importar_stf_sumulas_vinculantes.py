"""Importa Súmulas Vinculantes da coleção oficial do STF."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup
from importar_stf_repercussao_geral import (
    HEADERS_STF, PALAVRAS_CONSUMIDOR, _criar_session, _limpar, _relacoes_cdc,
)

TIPO = "sumula_vinculante"
ORIGEM = "STF_OFICIAL_SUMULA_VINCULANTE"
URL_LISTA = "https://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp?base=26"
URL_DETALHE = URL_LISTA + "&sumula={id_stf}"


def _url_oficial(url, detalhe=False):
    p, q = urlparse(url), parse_qs(urlparse(url).query)
    campos = {"base", "sumula"} if detalhe else {"base"}
    if (p.scheme != "https" or p.hostname != "portal.stf.jus.br" or p.port not in (None, 443)
            or p.username or p.password or p.fragment
            or p.path != "/jurisprudencia/sumariosumulas.asp"
            or set(q) != campos or q.get("base") != ["26"]):
        raise ValueError("URL fora da fonte oficial de Súmulas Vinculantes")
    if detalhe and not re.fullmatch(r"[1-9][0-9]*", (q.get("sumula") or [""])[0]):
        raise ValueError("identificador oficial inválido")
    return url


def _validar_resposta(r, url):
    _url_oficial(url, "sumula=" in url)
    r.raise_for_status()
    if r.status_code != 200 or not r.content or r.url != url:
        raise ValueError("resposta oficial vazia, redirecionada ou incompleta")
    soup = BeautifulSoup(r.content, "html.parser")
    texto = _limpar(soup.get_text(" ", strip=True)).lower()
    if any(x in texto for x in ("404 not found", "página não encontrada", "pagina nao encontrada",
           "não encontramos o que você", "access denied", "acesso negado",
           "serviço indisponível", "site em manutenção")):
        raise ValueError("página de erro com falso HTTP 200")
    return soup


def _obter(session, url):
    return _validar_resposta(session.get(url, headers=HEADERS_STF, timeout=60,
                                         allow_redirects=False), url)


def _descobrir(session):
    bloco = _obter(session, URL_LISTA).select_one(".sumarioSumulas")
    if bloco is None or _limpar((bloco.select_one("h3") or bloco).get_text()).lower() != "súmulas vinculantes":
        raise ValueError("estrutura da lista oficial não reconhecida")
    itens = []
    for a in bloco.select(".sumula-item > a[href]"):
        titulo = _limpar(a.get_text(" ", strip=True)).replace("\u200b", "")
        url = urljoin(URL_LISTA, a["href"])
        m = re.fullmatch(r"Súmula Vinculante\s+(\d+)(?:\s+\(cancelada\))?", titulo, re.I)
        _url_oficial(url, True)
        if not m:
            raise ValueError("item inesperado na lista oficial")
        itens.append({"numero": int(m.group(1)), "id_stf": int(parse_qs(urlparse(url).query)["sumula"][0]),
                      "url": url, "situacao_lista": "cancelada" if "cancelada" in titulo.lower() else "vigente"})
    nums = [x["numero"] for x in itens]
    if not nums or nums != list(range(1, max(nums) + 1)) or len({x["id_stf"] for x in itens}) != len(itens):
        raise ValueError("lista oficial vazia, duplicada ou incompleta")
    return itens


def _parsear_detalhe(soup, item):
    conteudo = soup.select_one("section.conteudo .container")
    titulos = conteudo.select("div.titulo") if conteudo else []
    if not titulos:
        raise ValueError("estrutura individual não reconhecida")
    titulo = _limpar(titulos[0].get_text(" ", strip=True)).replace("\u200b", "")
    m = re.fullmatch(r"Súmula Vinculante\s+(\d+)(?:\s+\(cancelada\))?", titulo, re.I)
    p = titulos[0].find_next_sibling("div", class_="parCOM")
    texto = _limpar(p.get_text(" ", strip=True) if p else "")
    situacao = ("cancelada" if "cancelada" in titulo.lower() else
                "pendente" if "pendente de publicação" in texto.lower() else "vigente")
    if (not m or int(m.group(1)) != item["numero"] or not texto
            or (situacao != item["situacao_lista"] and situacao != "pendente")):
        raise ValueError("identidade, texto ou situação oficial não confere")
    observacao = ""
    for t in titulos[1:]:
        if _limpar(t.get_text(" ", strip=True)).lower() in {"observação", "observações"}:
            p = t.find_next_sibling("div", class_="parCOM")
            observacao = _limpar(p.get_text(" ", strip=True) if p else "")
            break
    datas = re.findall(r"Data de publicação do enunciado:\s*(?:DJE|DJ)\s+(?:s/n\s+)?(?:de\s+)?(\d{1,2}(?:º)?-\d{1,2}-\d{4})", observacao, re.I)
    if len(datas) != 1 and situacao != "pendente":
        raise ValueError("data oficial ausente ou ambígua")
    data = datas[0].replace("º", "") if datas else ""
    if data:
        datetime.strptime(data, "%d-%m-%Y")
    return {**item, "texto": texto, "situacao": situacao,
            "data_publicacao": data, "observacao": observacao}


def _eh_consumerista(item):
    texto = (item["texto"] + " " + item["observacao"]).lower()
    return any(p.lower() in texto for p in PALAVRAS_CONSUMIDOR)


def _registro(item, hoje):
    relacoes = _relacoes_cdc(item["texto"] + " " + item["observacao"])
    return {"tribunal":"STF", "tipo":TIPO, "numero":item["numero"], "status":item["situacao"],
            "tema":f"Súmula Vinculante {item['numero']}",
            "arquivo":f"stf_sumula_vinculante_{item['numero']}.txt",
            "pasta_destino":"19_JURISPRUDENCIA/STF/SUMULAS_VINCULANTES",
            "texto":item["texto"], "texto_oficial_verificado":item["texto"],
            "relacionado_a":relacoes,
            "fonte":f"Supremo Tribunal Federal — Súmula Vinculante {item['numero']}",
            "url_fonte":item["url"], "url_verificacao":URL_LISTA, "url_descoberta":URL_LISTA,
            "situacao_oficial_stf":item["situacao"], "data_publicacao":item["data_publicacao"],
            "ultima_verificacao":hoje, "usar_tese_oficial":True,
            "fonte_texto_preferencial":"texto_oficial_verificado", "origem_importacao":ORIGEM}


def atualizar_sumulas_vinculantes(caminho_catalogo: Path, verbose=True, outros_registros=()):
    res = {"ok":False, "encontrados":0, "consumeristas":0, "importados":0,
           "com_relacao_cdc":0, "vinculos":[], "fonte":URL_LISTA}
    session = None
    try:
        bruto = caminho_catalogo.read_bytes() if caminho_catalogo.exists() else b"[]"
        catalogo = json.loads(bruto.decode("utf-8"))
        if not isinstance(catalogo, list) or any(not isinstance(x, dict) for x in catalogo):
            raise ValueError("catálogo anterior inválido")
        session = _criar_session()
        descobertos = _descobrir(session); res["encontrados"] = len(descobertos)
        detalhes = [_parsear_detalhe(_obter(session, x["url"]), x) for x in descobertos]
        candidatos = [x for x in detalhes if _eh_consumerista(x)]
        novos = [_registro(x, datetime.now().astimezone().date().isoformat()) for x in candidatos]
        preservados = [x for x in catalogo if x.get("origem_importacao") != ORIGEM]
        vistos = set()
        for x in [*preservados, *outros_registros, *novos]:
            tipo = str(x.get("tipo", "")).lower()
            classe = str(x.get("subtipo", tipo)).lower() if tipo == "precedente_relevante" else tipo
            chave = (str(x.get("tribunal", "")).upper(), classe, x.get("numero"))
            if chave in vistos:
                raise ValueError("duplicação entre categorias jurisprudenciais")
            vistos.add(chave)
        tmp = caminho_catalogo.with_suffix(caminho_catalogo.suffix + ".tmp")
        tmp.write_text(json.dumps(preservados + novos, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8", newline="\n")
        tmp.replace(caminho_catalogo)
        vinculos = [{"numero":x["numero"], "relacionado_a":x["relacionado_a"]}
                    for x in novos if x["relacionado_a"]]
        res.update(ok=True, consumeristas=len(candidatos), importados=len(novos),
                   com_relacao_cdc=len(vinculos), vinculos=vinculos)
        if verbose:
            print(f"STF SV: {len(descobertos)} oficiais; {len(candidatos)} consumeristas; "
                  f"{len(novos)} importadas; {len(vinculos)} com artigo do CDC explícito.")
    except Exception as exc:
        res["erro"] = str(exc)
        if verbose: print(f"STF SV: catálogo anterior preservado: {exc}")
    finally:
        if session is not None: session.close()
    return res
