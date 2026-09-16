"""Temas repetitivos do STJ a partir do catálogo oficial de Dados Abertos."""
from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from importar_stf_repercussao_geral import HEADERS_STF, _criar_session, _limpar, _relacoes_cdc

ORIGEM = "STJ_DADOS_ABERTOS_REPETITIVOS"
URL_TEMAS = (
    "https://dadosabertos.web.stj.jus.br/dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/"
    "resource/df29da13-7d6b-41ba-ad96-cd1a5bbd191c/download/temas.csv"
)
URL_PROCESSOS = (
    "https://dadosabertos.web.stj.jus.br/dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/"
    "resource/7ed21202-0049-4fcb-aa7c-48d810d3c499/download/processos.csv"
)
URL_TEMA = (
    "https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?"
    "cod_tema_inicial={numero}&cod_tema_final={numero}&novaConsulta=true&tipo_pesquisa=T"
)

COLUNAS_TEMAS = {
    "sequencialPrecedente", "tipoPrecedente", "numeroPrecedente",
    "dataPrimeiraAfetacao", "dataJulgamento", "dataPublicacaoAcordao",
    "situacao", "informacoesComplementares", "questaoSubmetidaAJulgamento",
    "teseFirmada", "anotacoesNUGEPNAC", "delimitacaoJulgado",
    "referenciaLegislativa", "referenciaSumular", "orgaoJulgador", "Assuntos",
}
COLUNAS_PROCESSOS = {
    "sequencialPrecedente", "tipoPrecedente", "numeroPrecedente", "Processo",
    "ministroRelator", "leadingCase", "dataAfetacao", "dataJulgamento", "Desafetação",
}
SITUACOES_OFICIAIS = {
    "Trânsito em Julgado", "Cancelado", "Afetado", "Acórdão Publicado",
    "Acórdão Publicado - RE Pendente", "Em Julgamento", "Revisado", "Sobrestado",
    "Mérito Julgado", "Sem Processo Vinculado", "Afetado - Possível Revisão de Tese",
}
SITUACOES_JULGADAS = {
    "Trânsito em Julgado", "Acórdão Publicado", "Acórdão Publicado - RE Pendente",
    "Mérito Julgado", "Revisado",
}
SITUACOES_PENDENTES = {"Afetado", "Em Julgamento", "Afetado - Possível Revisão de Tese"}
SINAIS_CONSUMERISTAS = (
    "direito do consumidor", "consumidor", "consumo", "fornecedor",
    "código de defesa do consumidor", "lei 8.078", "lei nº 8.078", "cdc",
    "plano de saúde", "instituição financeira", "instituições financeiras",
    "contrato bancário", "contratos bancários", "tarifa bancária",
    "cadastro de inadimplentes", "cadastro de proteção ao crédito",
    "seguro saúde", "contrato de seguro", "telefonia", "energia elétrica",
)


def _url_oficial(url: str) -> str:
    p = urlparse(url)
    if (p.scheme != "https" or p.hostname != "dadosabertos.web.stj.jus.br"
            or p.port not in (None, 443) or p.username or p.password or p.fragment):
        raise ValueError("URL fora da fonte oficial de Dados Abertos do STJ")
    return url


def _ler_csv_resposta(resposta, url: str, colunas: set[str]) -> list[dict[str, str]]:
    _url_oficial(url)
    resposta.raise_for_status()
    if resposta.status_code != 200 or not resposta.content or resposta.url != url:
        raise ValueError("resposta oficial vazia, redirecionada ou incompleta")
    try:
        texto = resposta.content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV oficial não está em UTF-8") from exc
    amostra = texto[:1000].lower()
    if any(x in amostra for x in ("<!doctype html", "<html", "404 not found", "access denied", "acesso negado")):
        raise ValueError("falso HTTP 200 na fonte oficial")
    leitor = csv.DictReader(io.StringIO(texto, newline=""))
    if not leitor.fieldnames or not colunas.issubset(set(leitor.fieldnames)):
        raise ValueError("estrutura do CSV oficial alterada")
    linhas = list(leitor)
    if not linhas or any(None in linha for linha in linhas):
        raise ValueError("CSV oficial vazio ou estruturalmente inválido")
    return linhas


def _baixar_csv(session, url: str, colunas: set[str]) -> list[dict[str, str]]:
    resposta = session.get(url, headers=HEADERS_STF, timeout=90, allow_redirects=False)
    return _ler_csv_resposta(resposta, url, colunas)


def _data(valor: str) -> str:
    valor = _limpar(valor)
    if not valor:
        return ""
    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(valor, formato).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"data oficial inválida: {valor}")


def _deduplicar_temas(linhas: list[dict[str, str]], validar_colecao: bool = True) -> list[dict[str, str]]:
    temas: dict[int, dict[str, str]] = {}
    for linha in linhas:
        if _limpar(linha["tipoPrecedente"]) != "Tema":
            continue
        numero_txt = _limpar(linha["numeroPrecedente"])
        sequencial = _limpar(linha["sequencialPrecedente"])
        situacao = _limpar(linha["situacao"])
        if not numero_txt.isdigit() or int(numero_txt) < 1 or not sequencial.isdigit():
            raise ValueError("identificação oficial de tema inválida")
        if situacao not in SITUACOES_OFICIAIS:
            raise ValueError(f"situação oficial desconhecida: {situacao}")
        normalizada = {k: _limpar(v) for k, v in linha.items()}
        numero = int(numero_txt)
        anterior = temas.get(numero)
        if anterior is not None:
            for campo, valor in normalizada.items():
                antigo = anterior.get(campo, "")
                if antigo and valor and antigo != valor:
                    if campo in {"numeroRepercussaoGeralSTF", "descricaoRepercussaoGeral"}:
                        valores = antigo.split(" | ")
                        if valor not in valores:
                            anterior[campo] = antigo + " | " + valor
                        continue
                    raise ValueError(f"Tema {numero} duplicado com conteúdo divergente")
                if valor:
                    anterior[campo] = valor
        else:
            temas[numero] = normalizada
    if validar_colecao:
        numeros = sorted(temas)
        if len(numeros) < 1400 or numeros != list(range(1, numeros[-1] + 1)):
            raise ValueError("coleção oficial de Temas Repetitivos truncada")
    if not temas:
        raise ValueError("nenhum Tema Repetitivo no CSV oficial")
    return [temas[n] for n in sorted(temas)]


def _agrupar_processos(
    linhas: list[dict[str, str]], tipos=("Tema",)
) -> dict[str, list[dict[str, str]]]:
    grupos: dict[str, list[dict[str, str]]] = {}
    vistos: set[tuple[str, ...]] = set()
    for linha in linhas:
        if _limpar(linha["tipoPrecedente"]) not in set(tipos):
            continue
        seq = _limpar(linha["sequencialPrecedente"])
        numero = _limpar(linha["numeroPrecedente"])
        processo = _limpar(linha["Processo"])
        if numero.isdigit() and not seq and not processo:
            # O próprio dataset usa uma linha vazia para "Sem Processo Vinculado".
            continue
        if not seq.isdigit() or not numero.isdigit() or not processo:
            raise ValueError("processo representativo oficial inválido")
        item = {
            "processo": processo,
            "relator": _limpar(linha["ministroRelator"]),
            "leading_case": _limpar(linha["leadingCase"]),
            "data_afetacao": _data(linha["dataAfetacao"]),
            "data_julgamento": _data(linha["dataJulgamento"]),
            "desafetacao": _limpar(linha["Desafetação"]),
        }
        chave = (seq, numero, *item.values())
        if chave in vistos:
            continue
        vistos.add(chave)
        grupos.setdefault(seq, []).append(item)
    return grupos


def _status_interno(situacao: str) -> str:
    if situacao == "Cancelado":
        return "cancelado"
    if situacao == "Sem Processo Vinculado":
        return "sem_tese_aplicavel"
    if situacao == "Sobrestado":
        return "sobrestado"
    if situacao in SITUACOES_PENDENTES:
        return "pendente"
    if situacao in SITUACOES_JULGADAS:
        return "julgado"
    raise ValueError(f"situação não mapeada: {situacao}")


def _relacoes_explicitas(item: dict[str, str]) -> list[str]:
    campos = " ".join(item.get(k, "") for k in (
        "questaoSubmetidaAJulgamento", "teseFirmada", "informacoesComplementares",
        "delimitacaoJulgado", "referenciaLegislativa", "Assuntos",
    ))
    return _relacoes_cdc(campos)


def _eh_consumerista(item: dict[str, str]) -> bool:
    # Toda citação inequívoca ao CDC já é, por si, sinal consumerista. Isso
    # também cobre grafias oficiais como "Lei n.8.078/90" sem relaxar a regra
    # usada para criar relações normativas.
    if _relacoes_explicitas(item):
        return True
    texto = " ".join(item.get(k, "") for k in (
        "questaoSubmetidaAJulgamento", "teseFirmada", "informacoesComplementares",
        "delimitacaoJulgado", "referenciaLegislativa", "Assuntos",
    )).casefold()
    return any(sinal in texto for sinal in SINAIS_CONSUMERISTAS)


def _montar_oficial(item: dict[str, str], processos: list[dict[str, str]]) -> dict:
    numero = int(item["numeroPrecedente"])
    situacao = item["situacao"]
    desafetado = bool(processos) and all(p["desafetacao"] for p in processos)
    vigente = situacao not in {"Cancelado", "Sem Processo Vinculado"} and not desafetado
    if desafetado and situacao not in {"Cancelado", "Sem Processo Vinculado"}:
        raise ValueError(f"Tema {numero}: desafetação integral incompatível com a situação oficial")
    relacoes = _relacoes_explicitas(item)
    return {
        "numero": numero,
        "sequencial_precedente_stj": item["sequencialPrecedente"],
        "situacao_oficial_stj": situacao,
        "status": _status_interno(situacao),
        "vigente_aplicavel": vigente,
        "tema_cancelado": situacao == "Cancelado",
        "tema_desafetado": desafetado,
        "sem_tese_aplicavel": situacao == "Sem Processo Vinculado",
        "questao_oficial_verificada": item["questaoSubmetidaAJulgamento"],
        "texto_oficial_verificado": item["teseFirmada"],
        "processos": [p["processo"] for p in processos],
        "processos_representativos_detalhes": processos,
        "orgao_julgador": item["orgaoJulgador"],
        "data_afetacao": _data(item["dataPrimeiraAfetacao"]),
        "data_julgamento": _data(item["dataJulgamento"]),
        "data_publicacao": _data(item["dataPublicacaoAcordao"]),
        "data_transito_julgado": "",
        "assuntos_stj": item["Assuntos"],
        "referencia_legislativa_stj": item["referenciaLegislativa"],
        "referencia_sumular_stj": item["referenciaSumular"],
        "informacoes_complementares_stj": item["informacoesComplementares"],
        "anotacoes_nugepnac_stj": item["anotacoesNUGEPNAC"],
        "delimitacao_julgado_stj": item["delimitacaoJulgado"],
        "relacoes_automaticas_cdc": relacoes,
        "consumerista": _eh_consumerista(item),
        "url_fonte": URL_TEMA.format(numero=numero),
    }


def _registro_novo(oficial: dict, hoje: str) -> dict:
    numero = oficial["numero"]
    texto = oficial["texto_oficial_verificado"] or oficial["questao_oficial_verificada"]
    return {
        "tribunal": "STJ", "tipo": "repetitivo", "numero": numero,
        "tema": oficial["assuntos_stj"] or f"Tema Repetitivo {numero}",
        "arquivo": f"stj_tema_{numero}.txt",
        "pasta_destino": "19_JURISPRUDENCIA/STJ/REPETITIVOS",
        "texto": texto, "relacionado_a": list(oficial["relacoes_automaticas_cdc"]),
        "fonte": f"Superior Tribunal de Justiça - Tema Repetitivo {numero}",
        "ultima_verificacao": hoje, "origem_importacao": ORIGEM,
        **oficial,
    }


def _mesclar_historico(registro: dict, oficial: dict, hoje: str) -> None:
    # ID, arquivo, tema editorial e relações legadas são deliberadamente preservados.
    registro.update({k: v for k, v in oficial.items() if k not in {"numero"}})
    registro["ultima_verificacao"] = hoje
    registro["resultado_ultima_verificacao_stj"] = "verificado_dados_abertos"
    registro.setdefault("fonte", f"Superior Tribunal de Justiça - Tema Repetitivo {oficial['numero']}")
    registro.setdefault("texto", oficial["texto_oficial_verificado"] or oficial["questao_oficial_verificada"])
    registro.setdefault("relacionado_a", [])


def _validar_duplicacoes(final: list[dict], outros: list[dict]) -> None:
    chaves = set()
    urls = {}
    for registro in [*final, *outros]:
        tipo = registro.get("tipo")
        classe = registro.get("subtipo") if tipo == "precedente_relevante" else tipo
        chave = (registro.get("tribunal"), classe, registro.get("numero"))
        if chave in chaves:
            raise ValueError("registro jurisprudencial duplicado")
        chaves.add(chave)
        url = str(registro.get("url_fonte", "")).strip()
        if url and url in urls and urls[url] != chave:
            raise ValueError("Tema Repetitivo duplicado em outra categoria")
        if url:
            urls[url] = chave


def atualizar_repetitivos_stj(caminho: Path, verbose: bool = True, outros_registros=()) -> dict:
    resultado = {"ok": False}
    session = None
    try:
        bruto = caminho.read_bytes()
        catalogo = json.loads(bruto.decode("utf-8"))
        if not isinstance(catalogo, list) or any(not isinstance(x, dict) for x in catalogo):
            raise ValueError("catálogo jurisprudencial inválido")
        antigos = [x for x in catalogo if x.get("tribunal") == "STJ" and x.get("tipo") == "repetitivo"]
        chaves_antigas = {(x.get("tribunal"), x.get("tipo"), x.get("numero")) for x in antigos}
        if len(chaves_antigas) != len(antigos):
            raise ValueError("Temas Repetitivos históricos duplicados")

        session = _criar_session()
        linhas_temas = _baixar_csv(session, URL_TEMAS, COLUNAS_TEMAS)
        linhas_processos = _baixar_csv(session, URL_PROCESSOS, COLUNAS_PROCESSOS)
        temas = _deduplicar_temas(linhas_temas)
        processos = _agrupar_processos(linhas_processos)
        oficiais = [_montar_oficial(x, processos.get(x["sequencialPrecedente"], [])) for x in temas]
        oficiais_por_numero = {x["numero"]: x for x in oficiais}
        hoje = datetime.now().astimezone().date().isoformat()

        existentes = {(x.get("tribunal"), x.get("tipo"), x.get("numero")): x for x in catalogo}
        for antigo in antigos:
            oficial = oficiais_por_numero.get(int(antigo["numero"]))
            if oficial:
                _mesclar_historico(antigo, oficial, hoje)

        novos = []
        for oficial in oficiais:
            chave = ("STJ", "repetitivo", oficial["numero"])
            if oficial["consumerista"] and oficial["vigente_aplicavel"] and chave not in existentes:
                novos.append(_registro_novo(oficial, hoje))
        final = catalogo + novos
        _validar_duplicacoes(final, list(outros_registros))

        temporario = caminho.with_suffix(caminho.suffix + ".tmp")
        temporario.write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        temporario.replace(caminho)

        finais = [x for x in final if x.get("tribunal") == "STJ" and x.get("tipo") == "repetitivo"]
        vinculos = [
            {"tema": x["numero"], "relacoes": x["relacoes_automaticas_cdc"]}
            for x in oficiais if x["relacoes_automaticas_cdc"]
        ]
        resultado.update({
            "ok": True,
            "oficiais_encontrados": len(oficiais),
            "vigentes_aplicaveis": sum(x["vigente_aplicavel"] for x in oficiais),
            "consumeristas": sum(x["consumerista"] for x in oficiais),
            "importados": len(finais),
            "ja_existiam": len(antigos),
            "novos": len(novos),
            "cancelados_ou_desafetados_fora_indice": sum(
                x["tema_cancelado"] or x["tema_desafetado"] for x in oficiais
            ),
            "total_fora_indice_vigente": sum(not x["vigente_aplicavel"] for x in oficiais),
            "cancelados": sum(x["tema_cancelado"] for x in oficiais),
            "desafetados": sum(x["tema_desafetado"] for x in oficiais),
            "sem_tese_aplicavel": sum(x["sem_tese_aplicavel"] for x in oficiais),
            "com_vinculo_explicito_cdc": len(vinculos),
            "vinculos_explicitos_cdc": vinculos,
            "fonte_temas": URL_TEMAS,
            "fonte_processos": URL_PROCESSOS,
            "total_final_categoria": len(finais),
        })
        if verbose:
            print("STJ Repetitivos:", json.dumps(resultado, ensure_ascii=False))
    except Exception as exc:
        resultado["erro"] = str(exc)
        if verbose:
            print("STJ Repetitivos: catálogo anterior preservado:", exc)
    finally:
        if session is not None:
            session.close()
    return resultado
