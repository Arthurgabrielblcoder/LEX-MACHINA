"""Importa uma amostra pequena e auditável de acórdãos consumeristas do STJ."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from importar_stf_repercussao_geral import _criar_session, _limpar


API_CKAN = "https://dadosabertos.web.stj.jus.br/api/3/action/package_show"
DATA_AMOSTRA = "20260831.json"
DATASETS = (
    "espelhos-de-acordaos-segunda-secao",
    "espelhos-de-acordaos-terceira-turma",
    "espelhos-de-acordaos-quarta-turma",
)
ORIGEM = "STJ_DADOS_ABERTOS_ESPELHOS_ACORDAOS_AMOSTRA_20260831"
LIMITE_IMPORTACAO = 20
COLUNAS = {
    "id", "numeroProcesso", "numeroRegistro", "siglaClasse",
    "nomeOrgaoJulgador", "ministroRelator", "dataPublicacao", "ementa",
    "tipoDeDecisao", "dataDecisao", "decisao", "referenciasLegislativas",
}
CLASSES_QUALIFICADAS = {"IAC", "SIRDR", "ADI", "ADC", "ADPF", "ADO"}
CDC = re.compile(
    r"\b(?:CDC|C[oó]digo de Defesa do Consumidor|Lei\s*(?:n[ºo.]?\s*)?8[.]?078(?:/1990)?)\b",
    re.I,
)


def _get_json(session, url, *, params=None):
    resposta = session.get(url, params=params, timeout=90)
    resposta.raise_for_status()
    tipo = resposta.headers.get("Content-Type", "").lower()
    if "json" not in tipo:
        raise ValueError("fonte oficial retornou conteúdo que não é JSON")
    try:
        dados = resposta.json()
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError("JSON oficial inválido") from exc
    return dados


def _descobrir_recursos(session):
    recursos = []
    for dataset in DATASETS:
        pacote = _get_json(session, API_CKAN, params={"id": dataset})
        if pacote.get("success") is not True or not isinstance(pacote.get("result"), dict):
            raise ValueError("resposta CKAN inesperada")
        encontrados = [
            r for r in pacote["result"].get("resources", [])
            if r.get("name") == DATA_AMOSTRA
            and str(r.get("format", "")).upper() == "JSON"
            and str(r.get("url", "")).startswith("https://dadosabertos.web.stj.jus.br/")
        ]
        if len(encontrados) != 1:
            raise ValueError(f"recurso oficial {DATA_AMOSTRA} ausente ou ambíguo em {dataset}")
        recursos.append({"dataset": dataset, "url": encontrados[0]["url"]})
    return recursos


def _validar_colecao(dados, *, validar_volume=True):
    if not isinstance(dados, list) or not dados:
        raise ValueError("coleção oficial vazia")
    if validar_volume and len(dados) < 100:
        raise ValueError("coleção oficial aparentemente truncada")
    for item in dados:
        if not isinstance(item, dict) or not COLUNAS.issubset(item):
            raise ValueError("estrutura oficial de acórdãos alterada")
        if not str(item["id"]).isdigit():
            raise ValueError("identificador oficial de acórdão inválido")
    return dados


def _texto_oficial(item):
    referencias = item.get("referenciasLegislativas") or []
    if not isinstance(referencias, list):
        raise ValueError("referências legislativas em formato inesperado")
    return "\n".join(
        [str(item.get("ementa") or ""), str(item.get("decisao") or "")]
        + [str(x) for x in referencias]
    )


def _menciona_cdc(item):
    return bool(CDC.search(_texto_oficial(item)))


def _relacoes_e_evidencias_cdc(item):
    texto = _texto_oficial(item)
    evidencias = {}
    def registrar(numero, evidencia):
        numero = int(numero)
        if 1 <= numero <= 119:
            relacao = f"CDC art. {numero}"
            evidencias.setdefault(relacao, [])
            trecho = _limpar(evidencia)
            if trecho and trecho not in evidencias[relacao]:
                evidencias[relacao].append(trecho)
    # Formato estruturado dos Espelhos: a lei e seus artigos estão no mesmo bloco.
    for referencia in item.get("referenciasLegislativas") or []:
        referencia = str(referencia)
        if re.search(r"LEI:0*8078\s+ANO:1990", referencia, re.I) or CDC.search(referencia):
            for numero in re.findall(r"\bART:0*(\d{1,3})\b", referencia, re.I):
                registrar(numero, referencia)
    lei = r"(?:CDC|C[oó]digo de Defesa do Consumidor|Lei\s*(?:n[ºo.]?\s*)?8[.]?078(?:/1990)?)"
    padroes = (
        rf"\bart(?:igo)?s?\.?\s*(\d{{1,3}})(?:\s*,[^.;:]{{0,35}})?\s+d[ao]\s+{lei}\b",
        rf"\b{lei}\s*,?\s*art(?:igo)?s?\.?\s*(\d{{1,3}})\b",
    )
    for padrao in padroes:
        for achado in re.finditer(padrao, texto, re.I):
            inicio = max(0, achado.start() - 100)
            fim = min(len(texto), achado.end() + 100)
            registrar(achado.group(1), texto[inicio:fim])
    evidencias = dict(sorted(evidencias.items(), key=lambda par: int(par[0].rsplit(" ", 1)[1])))
    return list(evidencias), evidencias


def _relacoes_cdc(item):
    return _relacoes_e_evidencias_cdc(item)[0]


def _normalizar_processo(valor):
    texto = re.sub(r"[^A-Z0-9]", "", str(valor or "").upper())
    return texto if len(texto) >= 6 else ""


def _processos_qualificados(registros):
    processos = set()
    def visitar(chave, valor):
        if isinstance(valor, dict):
            for k, v in valor.items():
                visitar(k, v)
        elif isinstance(valor, list):
            for v in valor:
                visitar(chave, v)
        elif "process" in str(chave).casefold():
            normalizado = _normalizar_processo(valor)
            if normalizado:
                processos.add(normalizado)
            for classe, numero in re.findall(r"\b([A-Za-z]+)\s*(\d[\d.\-/]*)", str(valor)):
                n = _normalizar_processo(classe + numero)
                if n:
                    processos.add(n)
    for registro in registros:
        visitar("registro", registro)
    return processos


def _chave(item):
    return (
        "STJ", _normalizar_processo(item["siglaClasse"] + item["numeroProcesso"]),
        str(item["dataDecisao"]), str(item["id"]),
    )


def _data_publicacao(valor):
    achado = re.search(r"DATA:(\d{2})/(\d{2})/(\d{4})", str(valor))
    return f"{achado.group(3)}-{achado.group(2)}-{achado.group(1)}" if achado else ""


def _riqueza_documental(item):
    campos = (
        "ementa", "decisao", "jurisprudenciaCitada", "notas", "termosAuxiliares",
        "referenciasLegislativas",
    )
    preenchidos = sum(bool(item.get(campo)) for campo in campos)
    tamanho = min(sum(len(str(item.get(campo) or "")) for campo in campos) // 500, 20)
    return preenchidos, tamanho


def _riqueza_estruturada(item):
    return (
        bool(item.get("teseJuridica")),
        bool(item.get("informacoesComplementares")),
        len(item.get("referenciasLegislativas") or []),
    )


def _selecionar_editorialmente(elegiveis, limite=LIMITE_IMPORTACAO):
    """Escolhe registros sem depender da ordem recebida dos recursos oficiais."""
    restantes = list(elegiveis)
    selecionados = []
    frequencia_artigos = {}
    while restantes and len(selecionados) < limite:
        def prioridade(par):
            item, relacoes = par
            novos = sum(frequencia_artigos.get(r, 0) == 0 for r in relacoes)
            concentracao = -sum(frequencia_artigos.get(r, 0) for r in relacoes)
            return (
                _riqueza_documental(item),
                _riqueza_estruturada(item),
                (novos, concentracao, len(relacoes)),
                str(item["dataDecisao"]),
                int(item["id"]),
            )
        escolhido = max(restantes, key=prioridade)
        restantes.remove(escolhido)
        selecionados.append(escolhido)
        for relacao in escolhido[1]:
            frequencia_artigos[relacao] = frequencia_artigos.get(relacao, 0) + 1
    return selecionados


def _registro(item, relacoes, evidencias, hoje):
    classe = _limpar(item["siglaClasse"])
    numero = _limpar(item["numeroProcesso"])
    ementa = _limpar(item["ementa"])
    data_julgamento = str(item["dataDecisao"])
    data_julgamento = (f"{data_julgamento[:4]}-{data_julgamento[4:6]}-{data_julgamento[6:8]}"
                       if re.fullmatch(r"\d{8}", data_julgamento) else "")
    return {
        "tribunal": "STJ", "tipo": "acordao", "classe": classe,
        "numero": numero, "numero_processo": f"{classe} {numero}",
        "tema": f"{classe} {numero}/STJ",
        "numero_registro_stj": _limpar(item["numeroRegistro"]),
        "decisao_id_stj": str(item["id"]),
        "orgao_julgador": _limpar(item["nomeOrgaoJulgador"]),
        "relator": _limpar(item["ministroRelator"]),
        "data_julgamento": data_julgamento,
        "data_publicacao": _data_publicacao(item["dataPublicacao"]),
        "ementa": ementa, "texto": ementa,
        "trecho_relevante": next((p.strip() for p in re.split(r"\n|(?<=\.)\s+", ementa)
                                  if CDC.search(p) or any(r.rsplit(" ", 1)[1] in p for r in relacoes)), ementa[:500]),
        "url_fonte": (
            "https://scon.stj.jus.br/SCON/GetInteiroTeorDoAcordao?"
            f"num_registro={item['numeroRegistro']}&dt_publicacao="
            f"{_data_publicacao(item['dataPublicacao'])[8:10]}/"
            f"{_data_publicacao(item['dataPublicacao'])[5:7]}/"
            f"{_data_publicacao(item['dataPublicacao'])[:4]}"
        ),
        "fonte": "STJ - Dados Abertos - Espelho do Acórdão",
        "status": "julgado", "relacionado_a": relacoes,
        "relacoes_automaticas_cdc": relacoes,
        "evidencias_relacoes_cdc": evidencias,
        "arquivo": f"stj_{re.sub(r'[^a-z0-9]+', '_', classe.casefold()).strip('_')}_{numero}_{item['id']}.txt",
        "pasta_destino": "19_JURISPRUDENCIA/STJ/ACORDAOS",
        "amostra_oficial": DATA_AMOSTRA, "origem_importacao": ORIGEM,
        "criterio_selecao": "CDC e artigo explícitos; priorização por tratamento documental e mérito",
        "ultima_verificacao": hoje,
    }


def atualizar_acordaos(caminho: Path, verbose=True, registros_qualificados=()):
    resultado = {"ok": False}
    session = None
    try:
        bruto = caminho.read_bytes()
        anteriores = json.loads(bruto.decode("utf-8"))
        if not isinstance(anteriores, list) or any(not isinstance(x, dict) for x in anteriores):
            raise ValueError("catálogo anterior de acórdãos inválido")
        session = _criar_session()
        recursos = _descobrir_recursos(session)
        itens = []
        for recurso in recursos:
            itens.extend(_validar_colecao(_get_json(session, recurso["url"])))

        unicos = {}
        ids_oficiais = {}
        for item in itens:
            chave = _chave(item)
            anterior = unicos.get(chave)
            if anterior is not None and anterior != item:
                raise ValueError("acórdão duplicado com conteúdo divergente")
            unicos[chave] = item
            id_oficial = str(item["id"])
            anterior_id = ids_oficiais.get(id_oficial)
            if anterior_id is not None and anterior_id != item:
                raise ValueError("identificador oficial duplicado com conteúdo divergente")
            ids_oficiais[id_oficial] = item
        amostra = list(unicos.values())
        candidatos = [
            x for x in amostra
            if _limpar(x["tipoDeDecisao"]).upper() == "ACÓRDÃO"
            and _menciona_cdc(x)
            and len(_limpar(x["ementa"])) >= 200
        ]
        consumeristas = []
        for item in candidatos:
            relacoes, evidencias = _relacoes_e_evidencias_cdc(item)
            if relacoes:
                consumeristas.append((item, relacoes, evidencias))
        qualificados = _processos_qualificados(registros_qualificados)
        elegiveis, excluidos = [], []
        for item, relacoes, evidencias in consumeristas:
            classe = _limpar(item["siglaClasse"]).upper()
            ids = {
                _normalizar_processo(item["numeroProcesso"]),
                _normalizar_processo(item["numeroRegistro"]),
                _normalizar_processo(item["siglaClasse"] + item["numeroProcesso"]),
            }
            texto = _texto_oficial(item).upper()
            if classe in CLASSES_QUALIFICADAS or ids & qualificados or re.search(r"\bTEMA\s+\d+[.]?\d*/STJ\b", texto):
                excluidos.append(item)
            else:
                elegiveis.append((item, relacoes, evidencias))
        pares_selecao = [(item, relacoes) for item, relacoes, _ in elegiveis]
        pares_escolhidos = _selecionar_editorialmente(pares_selecao)
        por_id = {str(item["id"]): (item, relacoes, evidencias)
                  for item, relacoes, evidencias in elegiveis}
        selecionados = [por_id[str(item["id"])] for item, _ in pares_escolhidos]
        hoje = datetime.now().astimezone().date().isoformat()
        novos = [_registro(item, relacoes, evidencias, hoje)
                 for item, relacoes, evidencias in selecionados]
        chaves = set()
        for item in novos:
            chave = (item["tribunal"], _normalizar_processo(item["numero_processo"]),
                     item["data_julgamento"], item["decisao_id_stj"])
            if chave in chaves:
                raise ValueError("duplicação interna de acórdão")
            chaves.add(chave)

        preservados = [x for x in anteriores if x.get("origem_importacao") != ORIGEM]
        final = preservados + novos
        tmp = caminho.with_suffix(caminho.suffix + ".acordaos.tmp")
        try:
            tmp.write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            tmp.replace(caminho)
        finally:
            tmp.unlink(missing_ok=True)
        resultado.update({
            "ok": True, "amostra_total": len(amostra),
            "candidatos_encontrados": len(candidatos),
            "consumeristas": len(consumeristas), "importados": len(novos),
            "excluidos_qualificados": len(excluidos),
            "elegiveis": len(elegiveis),
            "elegiveis_fora_limite": max(0, len(elegiveis) - len(selecionados)),
            "limite_editorial": LIMITE_IMPORTACAO,
            "regra_selecao": (
                "riqueza documental; tese/informações estruturadas; diversidade de artigos; "
                "data mais recente; maior ID oficial"
            ),
            "com_vinculo_explicito_cdc": len(novos),
            "vinculos_explicitos_cdc": [
                {"processo": x["numero_processo"], "relacoes": x["relacionado_a"]} for x in novos
            ],
            "total_final_categoria": sum(x.get("tipo") == "acordao" for x in final),
            "fontes": [x["url"] for x in recursos],
        })
        if verbose:
            print("Acórdãos:", json.dumps(resultado, ensure_ascii=False))
    except Exception as exc:
        resultado["erro"] = str(exc)
        if verbose:
            print("Acórdãos: catálogo anterior preservado:", exc)
    finally:
        if session is not None:
            session.close()
    return resultado
