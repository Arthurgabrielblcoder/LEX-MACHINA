from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import json
import re
import ssl

import requests
from bs4 import BeautifulSoup


class _AdaptadorTLSNativo(requests.adapters.HTTPAdapter):
    """Trust store do sistema, restrito à sessão do importador (Python 3.10+)."""

    def __init__(self):
        import truststore

        self.contexto = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        super().__init__()

    def build_connection_pool_key_attributes(self, request, verify, cert=None):
        if verify is False:
            raise ValueError("a sessão STF exige validação TLS")
        host, kwargs = super().build_connection_pool_key_attributes(request, verify, cert)
        kwargs["ssl_context"] = self.contexto
        return host, kwargs

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        if proxy.lower().startswith("https://"):
            proxy_kwargs["proxy_ssl_context"] = self.contexto
        return super().proxy_manager_for(proxy, **proxy_kwargs)


def _criar_session() -> requests.Session:
    adaptador = _AdaptadorTLSNativo()
    session = requests.Session()
    session.mount("https://", adaptador)
    return session

URL_TESES = "https://portal.stf.jus.br/jurisprudenciaRepercussao/tesesJulgamento.asp"
URL_TODOS_TEMAS = URL_TESES  # Compatibilidade com os testes e consumidores anteriores.
URL_BANCO_TESES = "https://portal.stf.jus.br/repercussaogeral/teses.asp"
URL_TESES_JSON = "https://portal.stf.jus.br/repercussaogeral/retornartesesrepercussaogeral.asp"
URL_TEMA = "https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num={numero}"
HEADERS_STF = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

# Filtro de descoberta. O índice do Lex Machina é por artigo do CDC; por isso
# buscamos temas com forte sinal consumerista e só criamos relação automática
# quando o próprio texto oficial menciona o CDC/Lei 8.078 e um artigo.
PALAVRAS_CONSUMIDOR = (
    "consumidor", "consumo", "código de defesa do consumidor", "codigo de defesa do consumidor",
    "lei 8.078", "lei nº 8.078", "lei n. 8.078", "cdc", "fornecedor", "plano de saúde",
    "plano de saude", "instituição financeira", "instituicao financeira", "contrato bancário",
    "contrato bancario", "telefonia", "serviço público", "servico publico", "tarifa bancária",
    "tarifa bancaria", "cadastro de inadimplentes", "dano moral", "produto defeituoso",
)


def _limpar(texto: str) -> str:
    return re.sub(r"\s+", " ", str(texto or "")).strip()


def _texto_soup(soup: BeautifulSoup) -> str:
    return "\n".join(_limpar(x) for x in soup.stripped_strings if _limpar(x))


def _url_oficial(url: str) -> str:
    partes = urlparse(url)
    if partes.scheme != "https" or partes.hostname != "portal.stf.jus.br":
        raise RuntimeError(f"URL fora da fonte oficial HTTPS: {url}")
    return url


def _validar_resposta(r: requests.Response) -> None:
    r.raise_for_status()
    if r.status_code != 200 or not r.content:
        raise RuntimeError(f"resposta oficial incompleta: HTTP {r.status_code}")
    if isinstance(r.url, str):
        _url_oficial(r.url)
    soup = BeautifulSoup(r.content, "html.parser")
    texto = _limpar(soup.get_text(" ", strip=True)).lower()
    if any(m in texto for m in (
        "não encontramos o que você está procurando", "página não encontrada",
        "pagina nao encontrada", "404 not found", "access denied",
        "acesso negado", "serviço indisponível", "site em manutenção",
    )):
        raise RuntimeError("portal retornou página de erro, mesmo com HTTP 200")


def _obter_html(session: requests.Session, url: str) -> BeautifulSoup:
    r = session.get(_url_oficial(url), headers=HEADERS_STF, timeout=60,
                    allow_redirects=False)
    _validar_resposta(r)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def _extrair_entre(texto: str, inicio: str, finais: tuple[str, ...]) -> str:
    p = texto.lower().find(inicio.lower())
    if p < 0:
        return ""
    p += len(inicio)
    fim = len(texto)
    trecho_lower = texto.lower()
    for marcador in finais:
        q = trecho_lower.find(marcador.lower(), p)
        if q >= 0:
            fim = min(fim, q)
    return _limpar(texto[p:fim].replace("\n", " "))


def _status_interno(situacao: str) -> str:
    s = situacao.lower()
    if "cancel" in s:
        return "cancelado"
    if "trânsito" in s or "transito" in s or "mérito julgado" in s or "merito julgado" in s:
        return "julgado"
    return "pendente"


def _relacoes_cdc(texto: str) -> list[str]:
    """Extrai somente vínculos explícitos entre artigo(s) e o CDC.

    A função não usa janela semântica ampla: o número precisa estar na mesma
    expressão que identifica o CDC/Lei 8.078. Isso evita capturar, por exemplo,
    um artigo da Constituição citado na mesma frase.
    """
    bruto = _limpar(texto)
    artigos: set[int] = set()

    lei = r"(?:Lei\s*(?:n[ºo\.]?\s*)?8[\.]?078(?:/1990)?|Código\s+de\s+Defesa\s+do\s+Consumidor|CDC)"
    art = r"art(?:igo)?s?\.?(?:\s+|\s*º\s*)"
    # Aceita apenas enumerações de artigos/incisos, nunca palavras livres
    # que poderiam atravessar uma referência à Constituição ou a outra lei.
    numero = r"\d{1,3}[º°]?(?:\s*,\s*[IVXLCDM]+)?"
    lista = rf"{numero}(?:\s*(?:,|e)\s*{numero})*"

    # Ex.: "arts. 6º, III, 14 e 51 da Lei 8.078/1990"
    padrao_antes = re.compile(
        rf"\b{art}({lista})(?:\s*,?\s+d[aoe]\s+|\s*,\s*){lei}\b",
        re.I,
    )
    # Ex.: "Lei 8.078/1990, arts. 6º e 14"
    padrao_depois = re.compile(
        rf"\b{lei}\s*[,;:\-]\s*{art}({lista})(?=\s*(?:\.|;|\)|$))",
        re.I,
    )
    # Ex.: "CDC art. 43" / "CDC arts. 42 e 43"
    padrao_direto = re.compile(
        rf"\bCDC\s+{art}({lista})(?=\s*(?:\.|;|\)|$))",
        re.I,
    )

    def colher(trecho: str):
        # Números de incisos/anos podem aparecer no mesmo trecho. Para reduzir
        # falsos positivos, aceitamos apenas 1..119 (faixa de artigos do CDC)
        # e descartamos números precedidos por '/' ou quatro dígitos.
        for m in re.finditer(r"(?<![/\d])(\d{1,3})(?!\d)", trecho):
            n = int(m.group(1))
            if 1 <= n <= 119:
                artigos.add(n)

    for padrao in (padrao_antes, padrao_depois, padrao_direto):
        for m in padrao.finditer(bruto):
            colher(m.group(1))

    return [f"CDC art. {n}" for n in sorted(artigos)]


def _descobrir_temas(session: requests.Session) -> list[dict]:
    """Banco oficial completo de teses COM RG; paginação é apenas no cliente.

    Contrato publicado em /scripts/tesesrepercussaogeral.js, usado pela página
    /repercussaogeral/teses.asp. Não usa o recorte de sessões em julgamento.
    """
    r = session.post(URL_TESES_JSON, data={"tipo": "com"},
                     headers=HEADERS_STF, timeout=60, allow_redirects=False)
    _validar_resposta(r)
    try:
        dados = json.loads(r.content)
    except (ValueError, UnicodeError) as exc:
        raise RuntimeError("o banco de teses não retornou JSON oficial válido") from exc
    if not isinstance(dados, list) or not dados:
        raise RuntimeError("o banco de teses retornou estrutura inesperada ou vazia")
    encontrados = {}
    campos = ("numeroTema", "incidente", "siglaClasse", "numeroProcesso",
              "descricaoTese", "dataAndamento")
    for item in dados:
        if not isinstance(item, dict) or any(
            not isinstance(item.get(c), str) or not item[c].strip() for c in campos
        ):
            raise RuntimeError("registro incompleto no banco oficial de teses")
        if any(not re.fullmatch(r"[0-9]+", item[c]) or int(item[c]) <= 0
               for c in ("numeroTema", "incidente", "numeroProcesso")):
            raise RuntimeError("identificador inválido no banco oficial de teses")
        datetime.strptime(item["dataAndamento"], "%d/%m/%Y")
        numero = int(item["numeroTema"])
        if numero in encontrados:
            raise RuntimeError(f"Tema {numero} duplicado no banco oficial")
        tese = _limpar(BeautifulSoup(item["descricaoTese"], "html.parser").get_text(" ", strip=True))
        if not tese:
            raise RuntimeError(f"Tema {numero} sem texto de tese")
        encontrados[numero] = {
            "numero": numero, "texto_linha": tese, "tese_oficial": tese,
            "data_tese": item["dataAndamento"],
            "processo_oficial": _limpar(item["siglaClasse"] + " " + item["numeroProcesso"]),
            "url": URL_TEMA.format(numero=numero),
            "url_tese": URL_BANCO_TESES,
        }
    return [encontrados[k] for k in sorted(encontrados)]


def _eh_candidato_consumidor(texto: str) -> bool:
    t = texto.lower()
    return any(p in t for p in PALAVRAS_CONSUMIDOR)


def _carregar_detalhe(session: requests.Session, tema: dict) -> dict | None:
    numero = tema["numero"]
    url = URL_TEMA.format(numero=numero)
    soup = _obter_html(session, url)
    texto = _texto_soup(soup.select_one("#conteudo") or soup)
    identidade = re.search(r"Tema:\s*0*(\d+)\b", texto)
    if identidade is None or int(identidade.group(1)) != numero:
        raise RuntimeError(f"Tema {numero}: identidade da página não confere")

    titulo = _extrair_entre(texto, "Título:", ("Descrição:", "Ver assuntos:"))
    descricao = _extrair_entre(texto, "Descrição:", ("Ver assuntos:", "Informações gerais"))
    leading = _extrair_entre(texto, "Leading Case:", ("Manifestação", "Ministro:"))
    ministro = _extrair_entre(texto, "Ministro:", ("Plenário Virtual", "Situação atual"))
    repercussao = _extrair_entre(texto, "Repercussão geral:", ("Data da Repercussão geral:", "Situação:"))
    data_rg = _extrair_entre(texto, "Data da Repercussão geral:", ("Situação:", "Tese:"))
    situacao = _extrair_entre(texto, "Situação:", ("Tese:", "Mapa do Site", "Praça dos Três Poderes"))
    if not titulo or not descricao or not repercussao or not situacao:
        raise RuntimeError(f"Tema {numero}: estrutura oficial não reconhecida")

    # O link de andamento costuma trazer a tese de maneira estruturada.
    tese = tema.get("tese_oficial", "")
    url_andamento = tema.get("url_tese", "")
    for a in soup.find_all("a", href=True) if not tese else []:
        href = a.get("href", "")
        if "verAndamentoProcesso.asp" in href:
            url_andamento = urljoin(url, href)
            break
    if url_andamento and not tese:
        try:
            ta = _texto_soup(_obter_html(session, url_andamento))
            tese = _extrair_entre(ta, "Tese:", ("Data Andamento", "Data | Andamento", "Número do Protocolo:"))
            if not descricao:
                descricao = _extrair_entre(ta, "Descrição:", ("Tese:",))
            if not leading:
                leading = _extrair_entre(ta, "Leading Case:", ("Descrição:",))
            if "Tese:" not in ta:
                raise RuntimeError(f"Tema {numero}: estrutura do andamento não reconhecida")
        except requests.RequestException as exc:
            raise RuntimeError(f"Tema {numero}: falha ao consultar andamento") from exc

    combinado = " ".join([titulo, descricao, tese])
    if tema.get("processo_oficial") and _limpar(leading) != tema["processo_oficial"]:
        raise RuntimeError(f"Tema {numero}: leading case diverge do banco oficial")
    # Só aceitamos temas com repercussão geral reconhecida. Não transformar
    # temas negados em "precedentes qualificados" no Lex Machina.
    rep_low = repercussao.lower()
    texto_low = texto.lower()
    if ("não há repercussão" in rep_low or "nao ha repercussao" in rep_low or
            "não há repercussão" in texto_low or "nao ha repercussao" in texto_low):
        return None
    if repercussao and "há repercussão" not in rep_low and "ha repercussao" not in rep_low:
        return None

    # Após abrir a página oficial, exige de novo um sinal consumerista.
    if not _eh_candidato_consumidor(combinado):
        return None

    relacoes = sorted({rel for campo in (titulo, descricao, tese)
                       for rel in _relacoes_cdc(campo)},
                      key=lambda rel: int(rel.rsplit(" ", 1)[1]))
    processo = re.sub(r"\s+", " ", leading).strip()
    texto_principal = tese or descricao or titulo
    if not texto_principal:
        return None

    return {
        "tribunal": "STF",
        "tipo": "repercussao_geral",
        "numero": numero,
        "status": _status_interno(situacao),
        "tema": titulo or f"Tema {numero} de Repercussão Geral",
        "arquivo": f"stf_tema_rg_{numero}.txt",
        "pasta_destino": "19_JURISPRUDENCIA/STF/PRECEDENTES/REPERCUSSAO_GERAL",
        "texto": texto_principal,
        "texto_oficial_verificado": tese,
        "questao_oficial_verificada": descricao,
        "relacionado_a": relacoes,
        "fonte": f"Supremo Tribunal Federal - Tema de Repercussão Geral {numero}",
        "url_fonte": url,
        "url_verificacao": url_andamento or url,
        "ultima_verificacao": datetime.now().strftime("%Y-%m-%d"),
        "processos": [processo] if processo else [],
        "relator": ministro,
        "situacao_oficial_stf": situacao,
        "repercussao_geral_stf": repercussao,
        "data_repercussao_geral": data_rg,
        "data_tese": tema.get("data_tese", ""),
        "url_descoberta": URL_TESES_JSON,
        "usar_tese_oficial": bool(tese),
        "fonte_texto_preferencial": "texto_oficial_verificado" if tese else "texto",
        "origem_importacao": "STF_OFICIAL_REPERCUSSAO_GERAL",
    }


def atualizar_catalogo_precedentes(caminho_catalogo: Path, verbose: bool = True) -> dict:
    """Atualiza a fatia STF/Repercussão Geral do catálogo de precedentes.

    Em falha de rede ou mudança de layout, o catálogo existente é preservado.
    """
    caminho_catalogo = Path(caminho_catalogo)
    session = None
    temas = []
    candidatos = []
    try:
        existentes = []
        if caminho_catalogo.exists():
            existentes = json.loads(caminho_catalogo.read_text(encoding="utf-8"))
            if not isinstance(existentes, list):
                raise ValueError("o catálogo existente não é uma lista")
        session = _criar_session()
        temas = _descobrir_temas(session)
        if not temas:
            raise RuntimeError("o portal oficial não retornou temas reconhecíveis")
        candidatos = [t for t in temas if _eh_candidato_consumidor(t.get("texto_linha", ""))]
        if verbose:
            print(f"STF RG: {len(temas)} temas descobertos; {len(candidatos)} candidatos consumeristas.")

        importados = []
        erros = 0
        for i, tema in enumerate(candidatos, 1):
            try:
                reg = _carregar_detalhe(session, tema)
                if reg:
                    importados.append(reg)
                    if verbose:
                        rel = ", ".join(reg["relacionado_a"]) or "sem artigo CDC explícito"
                        print(f"  [STF RG {i}/{len(candidatos)}] Tema {reg['numero']} -> {rel}")
            except Exception as exc:
                erros += 1
                if verbose:
                    print(f"  [AVISO STF RG] Tema {tema['numero']}: {exc}")

        if erros or not candidatos or not importados:
            raise RuntimeError(
                f"importação incompleta ou vazia: {erros} erros, "
                f"{len(candidatos)} candidatos, {len(importados)} importados"
            )

        numeros_consultados = {t["numero"] for t in candidatos}
        numeros_anteriores = {
            int(r["numero"]) for r in existentes if isinstance(r, dict)
            and r.get("origem_importacao") == "STF_OFICIAL_REPERCUSSAO_GERAL"
            and r.get("tribunal") == "STF" and r.get("tipo") == "repercussao_geral"
        }
        if not numeros_anteriores.issubset(numeros_consultados):
            raise RuntimeError("temas do catálogo anterior ficaram fora da consulta de detalhes")

        # Só substitui a fatia automática do STF; entradas manuais e outros
        # subtipos (ADI/ADC/ADPF/IRDR/IAC...) são preservados.
        preservados = [
            r for r in existentes
            if not (
                isinstance(r, dict)
                and r.get("tribunal") == "STF"
                and r.get("tipo") == "repercussao_geral"
                and r.get("origem_importacao") == "STF_OFICIAL_REPERCUSSAO_GERAL"
            )
        ]
        novo = preservados + sorted(importados, key=lambda r: int(r.get("numero", 0)))
        tmp = caminho_catalogo.with_suffix(caminho_catalogo.suffix + ".tmp")
        tmp.write_text(json.dumps(novo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(caminho_catalogo)
        return {
            "ok": True,
            "temas_descobertos": len(temas),
            "candidatos": len(candidatos),
            "importados": len(importados),
            "com_relacao_cdc": sum(bool(r.get("relacionado_a")) for r in importados),
            "erros": erros,
        }
    except Exception as exc:
        if verbose:
            print(f"[AVISO] STF Repercussão Geral não atualizado: {exc}")
            print("        Catálogo anterior preservado.")
        return {"ok": False, "erro": str(exc), "temas_descobertos": len(temas),
                "candidatos": len(candidatos), "importados": 0, "com_relacao_cdc": 0}
    finally:
        if session is not None:
            session.close()


if __name__ == "__main__":
    resultado = atualizar_catalogo_precedentes(Path("catalogo_precedentes.json"), verbose=True)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
