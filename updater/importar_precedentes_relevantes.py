"""Consolida precedentes relevantes e importa IAC/SIRDR oficiais do STJ."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from importar_stf_repercussao_geral import _criar_session, _limpar
from importar_stf_repercussao_geral import _relacoes_cdc
from importar_stj_repetitivos import (
    COLUNAS_PROCESSOS, COLUNAS_TEMAS, URL_PROCESSOS, URL_TEMAS,
    _agrupar_processos, _baixar_csv, _data,
)

ORIGEM = "STJ_DADOS_ABERTOS_PRECEDENTES_RELEVANTES"
SUBTIPOS_CONTROLE = {"adi", "adc", "adpf", "ado"}
SUBTIPOS = SUBTIPOS_CONTROLE | {"iac", "irdr", "sirdr"}
SITUACOES_IAC = {
    "Trânsito em Julgado", "Acórdão Publicado", "Admitido",
    "Em Julgamento", "Cancelado",
}
SITUACOES_SIRDR = {
    "Suspensão indeferida", "Suspensão deferida", "Prejudicada",
    "Vinculada a tema repetitivo", "Finalizada determinação de suspensão",
}
SINAIS_FORTES = (
    "direito do consumidor", "consumidor", "fornecedor",
    "código de defesa do consumidor", "plano de saúde", "planos de saúde",
    "contrato de seguro", "segurado e segurador", "contratos bancários",
    "contrato bancário", "conta bancária", "cadastro de inadimplentes",
    "proteção ao crédito", "construtora", "falha na prestação do serviço",
    "falha na prestação dos serviços", "dados pessoais", "direito de imagem",
)


def _deduplicar(linhas: list[dict[str, str]], tipo: str, validar_colecao=True):
    esperadas = SITUACOES_IAC if tipo == "IAC" else SITUACOES_SIRDR
    itens = {}
    for linha in linhas:
        if _limpar(linha["tipoPrecedente"]) != tipo:
            continue
        numero = _limpar(linha["numeroPrecedente"])
        seq = _limpar(linha["sequencialPrecedente"])
        situacao = _limpar(linha["situacao"])
        if not numero.isdigit() or not seq.isdigit() or situacao not in esperadas:
            raise ValueError(f"registro oficial {tipo} inválido")
        atual = {k: _limpar(v) for k, v in linha.items()}
        n = int(numero)
        if n in itens:
            anterior = itens[n]
            for campo, valor in atual.items():
                antigo = anterior.get(campo, "")
                if antigo and valor and antigo != valor:
                    if campo in {"numeroRepercussaoGeralSTF", "descricaoRepercussaoGeral"}:
                        if valor not in antigo.split(" | "):
                            anterior[campo] = antigo + " | " + valor
                        continue
                    raise ValueError(f"{tipo} {n} duplicado com conteúdo divergente")
                if valor:
                    anterior[campo] = valor
        else:
            itens[n] = atual
    minimo = 20 if tipo == "IAC" else 10
    if not itens or (validar_colecao and len(itens) < minimo):
        raise ValueError(f"coleção oficial {tipo} vazia ou truncada")
    return [itens[n] for n in sorted(itens)]


def _relacoes_cdc_oficiais(item):
    texto = " ".join(item.get(k, "") for k in (
        "questaoSubmetidaAJulgamento", "teseFirmada", "informacoesComplementares",
        "delimitacaoJulgado", "referenciaLegislativa", "Assuntos",
    ))
    relacoes = set(_relacoes_cdc(texto))
    lei = r"(?:CDC|C[oó]digo de Defesa do Consumidor|Lei\s*(?:n[ºo\.]?\s*)?8[\.]?078(?:/1990)?)"
    for achado in re.finditer(
        rf"\bart(?:igo)?s?\.?\s*(\d{{1,3}})(?:\s*,\s*[IVXLCDM]+(?:\s+e\s+[IVXLCDM]+)*)?\s*,?\s+d[ao]\s+{lei}\b",
        texto, re.I,
    ):
        numero = int(achado.group(1))
        if 1 <= numero <= 119:
            relacoes.add(f"CDC art. {numero}")
    return sorted(relacoes, key=lambda x: int(x.rsplit(" ", 1)[1]))


def _consumerista(item):
    if _relacoes_cdc_oficiais(item):
        return True
    texto = " ".join(item.get(k, "") for k in (
        "questaoSubmetidaAJulgamento", "teseFirmada", "informacoesComplementares",
        "delimitacaoJulgado", "referenciaLegislativa", "Assuntos",
    )).casefold()
    return any(sinal in texto for sinal in SINAIS_FORTES)


def _status(tipo, situacao):
    if tipo == "IAC":
        if situacao == "Cancelado":
            return "cancelado"
        if situacao in {"Admitido", "Em Julgamento"}:
            return "pendente"
        return "julgado"
    if situacao in {"Prejudicada", "Vinculada a tema repetitivo"}:
        return "superado"
    if situacao == "Suspensão deferida":
        return "sobrestado"
    return "julgado"


def _origem_irdr(item):
    texto = item.get("anotacoesNUGEPNAC", "")
    tribunais = sorted(set(re.findall(r"\b(?:TJ[A-Z]{2,4}|TRF[1-6])\b", texto)))
    numeros = re.findall(
        r"\bIRDR(?:\s+n\.)?\s*([0-9][0-9.\-]*(?:/[0-9A-Z]{2,5})*)",
        texto,
        re.I,
    )
    processos = re.findall(r"\(([0-9][0-9.\-]{3,})\)", texto)
    identificacoes = list(dict.fromkeys(_limpar(x) for x in [*numeros, *processos]))
    return tribunais, identificacoes


def _registro(item, processos, subtipo, hoje):
    numero = int(item["numeroPrecedente"])
    situacao = item["situacao"]
    relacoes = _relacoes_cdc_oficiais(item)
    tribunais_origem, irdrs = _origem_irdr(item) if subtipo == "sirdr" else ([], [])
    url_tipo = "I" if subtipo == "iac" else "S"
    tese = item["teseFirmada"]
    questao = item["questaoSubmetidaAJulgamento"]
    return {
        "tribunal": "STJ", "tipo": "precedente_relevante", "subtipo": subtipo,
        "classe": "IAC" if subtipo == "iac" else "SIRDR",
        "numero": numero, "tema": f"{'IAC' if subtipo == 'iac' else 'SIRDR'} {numero}/STJ",
        "arquivo": f"stj_{'iac' if subtipo == 'iac' else 'sirdr'}_{numero}.txt",
        "pasta_destino": f"19_JURISPRUDENCIA/STJ/PRECEDENTES_RELEVANTES/{subtipo.upper()}",
        "texto": tese or questao, "texto_oficial_verificado": tese,
        "questao_oficial_verificada": questao, "relacionado_a": relacoes,
        "relacoes_automaticas_cdc": relacoes,
        "fonte": f"Superior Tribunal de Justiça - {'IAC' if subtipo == 'iac' else 'SIRDR'} {numero}",
        "url_fonte": "https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?"
                     f"cod_tema_inicial={numero}&cod_tema_final={numero}&novaConsulta=true&tipo_pesquisa={url_tipo}",
        "status": _status("IAC" if subtipo == "iac" else "SIRDR", situacao),
        "situacao_oficial_stj": situacao,
        "sequencial_precedente_stj": item["sequencialPrecedente"],
        "numero_sirdr_stj": numero if subtipo == "sirdr" else None,
        "processos": list(dict.fromkeys(p["processo"] for p in processos)),
        "processos_representativos_detalhes": processos,
        "relator": next((p["relator"] for p in processos if p["relator"]), ""),
        "orgao_julgador": item["orgaoJulgador"],
        "data_afetacao": _data(item["dataPrimeiraAfetacao"]),
        "data_julgamento": _data(item["dataJulgamento"]),
        "data_publicacao": _data(item["dataPublicacaoAcordao"]),
        "assuntos_stj": item["Assuntos"],
        "referencia_legislativa_stj": item["referenciaLegislativa"],
        "informacoes_complementares_stj": item["informacoesComplementares"],
        "anotacoes_nugepnac_stj": item["anotacoesNUGEPNAC"],
        "tribunais_origem_irdr": tribunais_origem,
        "identificacoes_irdr_origem": irdrs,
        "irdr_origem_texto_oficial": item["anotacoesNUGEPNAC"] if subtipo == "sirdr" else "",
        "cobertura_irdr": "IRDR de origem relacionado a SIRDR registrado no STJ" if subtipo == "sirdr" else "",
        "ultima_verificacao": hoje, "origem_importacao": ORIGEM,
    }


def _consolidar_controle(registro):
    tipo = str(registro.get("tipo", "")).lower()
    if tipo in SUBTIPOS_CONTROLE:
        registro["tipo_original"] = tipo
        registro["tipo"] = "precedente_relevante"
        registro["subtipo"] = tipo
        registro["classe"] = tipo.upper()
        registro["categoria_interface"] = "precedente_relevante"
    elif tipo == "precedente_relevante":
        subtipo = str(registro.get("subtipo", "")).lower()
        if subtipo not in SUBTIPOS:
            raise ValueError("precedente_relevante com subtipo inválido")


def _validar_duplicacoes(registros, outros):
    identidades, urls = set(), set()
    for r in [*registros, *outros]:
        tipo = str(r.get("tipo", "")).lower()
        subtipo = str(r.get("subtipo", tipo)).lower()
        chave = (str(r.get("tribunal", "")).upper(), subtipo, str(r.get("numero", "")))
        if chave in identidades:
            raise ValueError("precedente duplicado entre categorias")
        identidades.add(chave)
        url = str(r.get("url_fonte", ""))
        if url and url in urls:
            raise ValueError("URL oficial duplicada entre categorias")
        if url:
            urls.add(url)


def atualizar_precedentes_relevantes(caminho: Path, verbose=True, outros_registros=()):
    resultado = {"ok": False}
    session = None
    try:
        bruto = caminho.read_bytes()
        catalogo = json.loads(bruto.decode("utf-8"))
        if not isinstance(catalogo, list) or any(not isinstance(x, dict) for x in catalogo):
            raise ValueError("catálogo de precedentes inválido")
        anteriores_controle = [
            x for x in catalogo
            if str(x.get("tipo", "")).lower() in SUBTIPOS_CONTROLE
            or (
                str(x.get("tipo", "")).lower() == "precedente_relevante"
                and str(x.get("subtipo", "")).lower() in SUBTIPOS_CONTROLE
            )
        ]
        base = [x for x in catalogo if x.get("origem_importacao") != ORIGEM]
        for registro in base:
            _consolidar_controle(registro)

        session = _criar_session()
        linhas_temas = _baixar_csv(session, URL_TEMAS, COLUNAS_TEMAS)
        linhas_processos = _baixar_csv(session, URL_PROCESSOS, COLUNAS_PROCESSOS)
        iacs = _deduplicar(linhas_temas, "IAC")
        sirdrs = _deduplicar(linhas_temas, "SIRDR")
        processos = _agrupar_processos(linhas_processos, tipos=("IAC", "SIRDR"))
        hoje = datetime.now().astimezone().date().isoformat()

        candidatos_iac = [x for x in iacs if _consumerista(x) and x["situacao"] != "Cancelado"]
        # SIRDR vinculada a repetitivo fica na categoria principal já existente.
        candidatos_sirdr = [x for x in sirdrs if _consumerista(x) and x["situacao"] != "Vinculada a tema repetitivo"]
        novos = [
            _registro(x, processos.get(x["sequencialPrecedente"], []), subtipo, hoje)
            for subtipo, itens in (("iac", candidatos_iac), ("sirdr", candidatos_sirdr))
            for x in itens
        ]
        final = base + novos
        _validar_duplicacoes(final, list(outros_registros))
        preservados = [x for x in final if x.get("subtipo") in SUBTIPOS_CONTROLE]
        if len(preservados) != len(anteriores_controle):
            raise ValueError("controle concentrado não foi preservado integralmente")

        tmp = caminho.with_suffix(caminho.suffix + ".relevantes.tmp")
        try:
            tmp.write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            tmp.replace(caminho)
        finally:
            tmp.unlink(missing_ok=True)
        rels = [{"subtipo": x["subtipo"], "numero": x["numero"], "relacoes": x["relacionado_a"]}
                for x in novos if x["relacionado_a"]]
        resultado.update({
            "ok": True,
            "controle_preservado": {t: sum(x.get("subtipo") == t for x in final) for t in sorted(SUBTIPOS_CONTROLE)},
            "iac_oficiais": len(iacs), "iac_consumeristas": len(candidatos_iac),
            "iac_importados": sum(x["subtipo"] == "iac" for x in novos),
            "sirdr_cobertura": "SIRDRs oficiais do STJ relacionados a IRDRs de origem; sem cobertura nacional direta de IRDR",
            "sirdr_oficiais_encontrados": len(sirdrs), "sirdr_consumeristas": len(candidatos_sirdr),
            "sirdr_importados": sum(x["subtipo"] == "sirdr" for x in novos),
            "tribunais_origem_irdr_referenciados": sorted({
                tribunal
                for item in sirdrs
                for tribunal in _origem_irdr(item)[0]
            }),
            "vinculos_explicitos_cdc": rels,
            "total_final": sum(x.get("tipo") == "precedente_relevante" for x in final),
            "fonte_temas": URL_TEMAS, "fonte_processos": URL_PROCESSOS,
        })
        if verbose:
            print("Precedentes Relevantes:", json.dumps(resultado, ensure_ascii=False))
    except Exception as exc:
        resultado["erro"] = str(exc)
        if verbose:
            print("Precedentes Relevantes: catálogo anterior preservado:", exc)
    finally:
        if session is not None:
            session.close()
    return resultado
