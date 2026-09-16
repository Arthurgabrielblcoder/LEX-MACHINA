from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import argparse
import hashlib
import json
import os
import re
import shutil
import time

import requests
from bs4 import BeautifulSoup
from importar_stf_repercussao_geral import atualizar_catalogo_precedentes
from importar_stf_controle_concentrado import atualizar_controle_concentrado
from importar_stf_sumulas_vinculantes import atualizar_sumulas_vinculantes


# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================

PASTA_SAIDA = Path("saida")

ARQUIVO_CATALOGO_NORMAS = Path(
    "catalogo_normas.json"
)

ARQUIVO_CATALOGO_JURISPRUDENCIA = Path(
    "catalogo_jurisprudencia.json"
)

# Catálogos separados para as novas camadas da interface jurídica.
# Eles começam vazios e podem ser alimentados por importadores oficiais
# sem misturar acórdãos avulsos com precedentes qualificados.
ARQUIVO_CATALOGO_ACORDAOS = Path(
    "catalogo_acordaos.json"
)

ARQUIVO_CATALOGO_PRECEDENTES = Path(
    "catalogo_precedentes.json"
)

ARQUIVO_CATALOGO_MESTRE = Path(
    "catalogo_mestre_vademecum.json"
)

# RAIZ_VADEMECUM:
#   raiz geral do acervo. Ex.: D:\
#
# PASTA_SAIDA:
#   mantém compatibilidade com o comportamento antigo.
#   Sem destino externo: saida/
#   Com destino externo: <destino>/9-CÓDIGO DE DEFESA DO CONSUMIDOR/
#
# PASTA_RELATORIOS_GERAIS:
#   índices e relatórios do Vade Mecum completo.
RAIZ_VADEMECUM = Path("saida")
PASTA_RELATORIOS_GERAIS = (
    RAIZ_VADEMECUM
    / "99_INDICES"
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


# ============================================================
# SEGURANÇA DO UPDATER DO CATÁLOGO MESTRE - V2
# ============================================================

# Constituição, Código Civil e ECA não usam mais o scraping HTML
# legado do Planalto. Para esses três diplomas o updater resolve,
# no portal oficial do Senado Federal, a "Compilação Monovigente"
# e só aceita a fonte se ela atravessar testes estruturais fortes.
FONTES_ESPECIAIS_MESTRE = {
    "CF88": {
        "norma_url": "https://legis.senado.leg.br/norma/579494",
        "titulo_inicio": (
            "CONSTITUIÇÃO DA REPÚBLICA FEDERATIVA DO BRASIL"
        ),
        "min_caracteres": 180000,
        "min_linhas": 2000,
        "min_artigos": 235,
        "artigo_final": "250",
        "artigos_ancora": [
            "1", "5", "18", "31", "37", "60", "75", "93",
            "102", "127", "134", "144", "150", "170",
            "194", "196", "205", "225", "226", "227",
            "230", "250",
        ],
        "frases_recentes": [
            "vedada sua extinção, criação ou instalação",
            "os tribunais de contas são instituições permanentes",
        ],
    },
    "CC2002": {
        "norma_url": "https://legis.senado.leg.br/norma/552282",
        "titulo_inicio": (
            "LEI Nº 10.406, DE 10 DE JANEIRO DE 2002"
        ),
        "min_caracteres": 400000,
        "min_linhas": 5000,
        "min_artigos": 1900,
        "artigo_final": "2046",
        "artigos_ancora": [
            "1", "40", "44", "104", "186", "233", "404",
            "406", "421", "927", "966", "1045", "1225",
            "1421", "1511", "1784", "1829", "2002", "2046",
        ],
        "frases_recentes": [
            "empreendimentos de economia solidária",
            "lei nº 14.905",
        ],
    },
    "ECA1990": {
        "norma_url": "https://legis.senado.leg.br/norma/549945",
        "titulo_inicio": (
            "LEI Nº 8.069, DE 13 DE JULHO DE 1990"
        ),
        "min_caracteres": 120000,
        "min_linhas": 1500,
        "min_artigos": 250,
        "artigo_final": "267",
        "artigos_ancora": [
            "1", "7", "11-A", "53", "70", "101", "112",
            "131", "136", "149", "171", "190-F", "201",
            "208", "227-C", "240", "241-E", "267",
        ],
        "frases_recentes": [
            "lei nº 15.487",
            "art. 190-f",
            "art. 227-c",
        ],
    },
}


# Caminhos canônicos dos 20 arquivos BASE já existentes no cartão.
#
# Isto evita um erro importante do localizador antigo: ele procurava os
# termos de detecção no CAMINHO INTEIRO. Como o nome da pasta
# "9-CÓDIGO DE DEFESA DO CONSUMIDOR" aparece no caminho de todos os
# arquivos internos, um relatório como RELATORIO_ATUALIZACAO.txt podia
# ser confundido com o próprio CDC.
#
# A partir desta versão:
#   1) tenta primeiro o caminho canônico;
#   2) depois o nome exato sugerido;
#   3) só então usa termos no NOME DO ARQUIVO, nunca na pasta inteira.
ARQUIVOS_BASE_CANONICOS = {
    "CF88": (
        "1- CONSTITUIÇÃO FEDERAL/cf.txt"
    ),
    "CC2002": (
        "2- CÓDIGO CIVIL/"
        "codigo_civil_ lei10.406 2002.txt"
    ),
    "CPC2015": (
        "3-CÓDIGO PROCESSO CIVIL/"
        "codigo_processo_civil.txt"
    ),
    "CP1940": (
        "4-CÓDIGO PENAL/codigo_penal.txt"
    ),
    "CPP1941": (
        "5-CÓDIGO PROCESSO PENAL/"
        "Código_de_Processo_Penal.txt"
    ),
    "CTN1966": (
        "6-CÓDIGO TRIBUTARIO NACIONAL/"
        "Código Tributário Nacional.txt"
    ),
    "CE1965": (
        "7-CÓDIGO ELEITORAL/"
        "Código Eleitoral.txt"
    ),
    "CLT1943": (
        "8-CLT CONSOLIDAÇÃO DAS LEIS DO TRABALHO/"
        "CLT.txt"
    ),
    "CDC1990": (
        "9-CÓDIGO DE DEFESA DO CONSUMIDOR/"
        "01_CDC/cdc_lei_8078_1990.txt"
    ),
    "ECA1990": (
        "10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE/"
        "Estatuto da Criança e do Adolescente "
        "(Lei nº 8.069 1990).txt"
    ),
    "IDOSO2003": (
        "11- ESTATUTO DA PESSOA IDOSA/"
        "Estatuto da pessoa idosa.txt"
    ),
    "LBI2015": (
        "12-LEI BRASILEIRA DE INCLUSÃO DA PESSOA COM DEFICIÊNCIA/"
        "Lei Brasileira de Inclusão da Pessoa com Deficiência.txt"
    ),
    "LEP1984": (
        "13- LEI DA EXECUÇÃO PENAL/"
        "Lei de Execução Penal.txt"
    ),
    "DROGAS2006": (
        "14- LEI DE DROGAS/"
        "Lei de Drogas.txt"
    ),
    "MARIA2006": (
        "15-LEI MARIA DA PENHA/"
        "Lei Maria da Penha.txt"
    ),
    "HEDIONDOS1990": (
        "16- LEI DE CRIMES HEDIONDOS/"
        "Lei de Crimes Hediondos.txt"
    ),
    "LIC2021": (
        "17- LEI DE LICITAÇÕES E CONTRATOS/"
        "Lei de Licitações e Contratos Administrativos.txt"
    ),
    "MCI2014": (
        "18- MARCO CIVIL DA INTERNET/"
        "Marco Civil da Internet.txt"
    ),
    "LGPD2018": (
        "19-LGPD LEI GERAL DA PROTEÇÃO DE DADOS/"
        "LGPD Lei Geral da Proteção de Dados.txt"
    ),
    "LAI2011": (
        "20- LEI DE ACESSO A INFORMAÇÃO/"
        "Lei de Acesso a Informação.txt"
    ),
}

# Cabeçalho de artigo: somente início de linha. Isso impede que
# referências como "nos termos do art. 827" sejam contadas como
# artigos do diploma.
PADRAO_ARTIGO_CABECALHO = re.compile(
    r"(?im)"
    r"^\s*"
    r"Art(?:igo)?"
    r"\s*\.?\s*"
    r"(\d{1,3}(?:\.\d{3})+|\d{1,4})"
    r"\s*"
    r"(?:º|°|o)?"
    r"\s*"
    r"(?:[-–—]\s*([A-Za-z]{1,5}(?:-[A-Za-z]{1,5})*))?"
    r"(?:\s*[\.\-–—])?"
)

TIMEOUT_UPDATER = 60
MAX_TENTATIVAS_UPDATER = 4


def _hash_bytes(dados):
    return hashlib.sha256(
        dados
    ).hexdigest()


def _hash_texto(texto):
    return _hash_bytes(
        texto.encode(
            "utf-8"
        )
    )


def _canonizar_artigo(
    numero_bruto,
    sufixo=None,
):
    numero = str(
        int(
            str(
                numero_bruto
            ).replace(
                ".",
                "",
            )
        )
    )

    if sufixo:
        return (
            numero
            + "-"
            + str(
                sufixo
            ).upper()
        )

    return numero


def _artigos_cabecalho(
    texto,
):
    artigos = []

    for match in (
        PADRAO_ARTIGO_CABECALHO.finditer(
            texto
        )
    ):
        try:
            artigos.append(
                _canonizar_artigo(
                    match.group(
                        1
                    ),
                    match.group(
                        2
                    ),
                )
            )

        except (
            ValueError,
            TypeError,
        ):
            continue

    return artigos


def _requisitar_com_retry(
    url,
):
    ultimo_erro = None

    for tentativa in range(
        1,
        MAX_TENTATIVAS_UPDATER + 1,
    ):
        try:
            resposta = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT_UPDATER,
                allow_redirects=True,
            )

            if resposta.status_code in {
                429,
                500,
                502,
                503,
                504,
            }:
                ultimo_erro = RuntimeError(
                    (
                        f"HTTP {resposta.status_code} "
                        f"em {resposta.url}"
                    )
                )

                if (
                    tentativa
                    < MAX_TENTATIVAS_UPDATER
                ):
                    time.sleep(
                        min(
                            2 ** tentativa,
                            12,
                        )
                    )

                continue

            resposta.raise_for_status()

            if len(
                resposta.content
            ) < 100:
                ultimo_erro = RuntimeError(
                    (
                        "Resposta pequena demais "
                        f"({len(resposta.content)} bytes)."
                    )
                )

                if (
                    tentativa
                    < MAX_TENTATIVAS_UPDATER
                ):
                    time.sleep(
                        tentativa
                    )

                continue

            return resposta

        except requests.RequestException as erro:
            ultimo_erro = erro

            if (
                tentativa
                < MAX_TENTATIVAS_UPDATER
            ):
                time.sleep(
                    min(
                        2 ** tentativa,
                        12,
                    )
                )

    raise RuntimeError(
        (
            f"Falha ao consultar {url}: "
            f"{ultimo_erro}"
        )
    )


def _resolver_publicacoes_monovigentes(
    norma_url,
):
    """
    Retorna URLs /publicacao/ ligadas à linha
    "Compilação Monovigente" no portal oficial do Senado.

    Falha de resolução é tratada como falha de segurança:
    o updater NÃO volta automaticamente ao HTML legado.
    """

    resposta = _requisitar_com_retry(
        norma_url
    )

    soup = BeautifulSoup(
        resposta.content,
        "html.parser",
    )

    candidatos = []

    # Estratégia principal: linha da tabela.
    for linha in soup.find_all(
        "tr"
    ):
        texto_linha = (
            normalizar_identificador(
                linha.get_text(
                    " ",
                    strip=True,
                )
            )
        )

        if (
            "compilacao monovigente"
            not in texto_linha
        ):
            continue

        for link in linha.find_all(
            "a",
            href=True,
        ):
            href = str(
                link.get(
                    "href",
                    "",
                )
            ).strip()

            if (
                "/publicacao/"
                in href
            ):
                candidatos.append(
                    urljoin(
                        str(
                            resposta.url
                        ),
                        href,
                    )
                )

    # Estratégia secundária: sobe na árvore a partir do texto.
    if not candidatos:
        for no_texto in soup.find_all(
            string=True
        ):
            if (
                "compilacao monovigente"
                not in normalizar_identificador(
                    str(
                        no_texto
                    )
                )
            ):
                continue

            atual = getattr(
                no_texto,
                "parent",
                None,
            )

            for _ in range(
                8
            ):
                if atual is None:
                    break

                for link in atual.find_all(
                    "a",
                    href=True,
                ):
                    href = str(
                        link.get(
                            "href",
                            "",
                        )
                    ).strip()

                    if (
                        "/publicacao/"
                        in href
                    ):
                        candidatos.append(
                            urljoin(
                                str(
                                    resposta.url
                                ),
                                href,
                            )
                        )

                if candidatos:
                    break

                atual = getattr(
                    atual,
                    "parent",
                    None,
                )

            if candidatos:
                break

    unicos = []
    vistos = set()

    for candidato in candidatos:
        if candidato in vistos:
            continue

        vistos.add(
            candidato
        )

        unicos.append(
            candidato
        )

    if not unicos:
        raise RuntimeError(
            (
                "Não foi possível resolver a "
                "Compilação Monovigente no Senado."
            )
        )

    return unicos


def _extrair_corpo_senado(
    conteudo,
    titulo_inicio,
):
    """
    Extrai somente o corpo legal da publicação monovigente
    oficial do Senado. Não tenta interpretar revogações:
    a consolidação já é publicada pelo órgão oficial.
    """

    soup = BeautifulSoup(
        conteudo,
        "html.parser",
    )

    for nome in (
        "script",
        "style",
        "noscript",
        "iframe",
        "svg",
        "canvas",
        "form",
    ):
        for tag in soup.find_all(
            nome
        ):
            try:
                tag.decompose()

            except AttributeError:
                continue

    texto_total = soup.get_text(
        "\n",
        strip=False,
    )

    linhas = [
        linha.strip()
        for linha in (
            texto_total
            .replace(
                "\xa0",
                " ",
            )
            .splitlines()
        )
    ]

    titulo_norm = (
        normalizar_identificador(
            titulo_inicio
        )
    )

    inicio = None

    for indice, linha in enumerate(
        linhas
    ):
        if (
            titulo_norm
            in normalizar_identificador(
                linha
            )
        ):
            inicio = indice
            break

    if inicio is None:
        raise RuntimeError(
            (
                "Título jurídico não localizado "
                "na publicação monovigente."
            )
        )

    marcadores_fim = (
        "english",
        "espanol",
        "francais",
        "intranet",
        "servidor efetivo",
        "fale com o senado",
        "senado federal praca dos tres poderes",
    )

    fim = len(
        linhas
    )

    for indice in range(
        inicio + 1,
        len(
            linhas
        ),
    ):
        linha_norm = (
            normalizar_identificador(
                linhas[
                    indice
                ]
            )
        )

        # IMPORTANTE:
        # não use "marcador in linha_norm" aqui.
        #
        # O ECA possui no art. 194 a expressão
        # "servidor efetivo ou voluntário credenciado".
        # A versão anterior confundia isso com o link de rodapé
        # "Servidor efetivo" e cortava a lei nesse ponto.
        #
        # Marcadores curtos de rodapé só valem se a linha inteira
        # for exatamente o marcador.
        if (
            linha_norm
            in marcadores_fim
            or linha_norm.startswith(
                "senado federal praca dos tres poderes"
            )
        ):
            fim = indice
            break

    corpo = "\n".join(
        linhas[
            inicio:fim
        ]
    )

    return normalizar_texto(
        corpo
    )


def _validar_especial_mestre(
    identificador,
    texto,
):
    config = (
        FONTES_ESPECIAIS_MESTRE[
            identificador
        ]
    )

    artigos = _artigos_cabecalho(
        texto
    )

    conjunto = set(
        artigos
    )

    problemas = []

    if (
        len(
            texto
        )
        < config[
            "min_caracteres"
        ]
    ):
        problemas.append(
            (
                "Texto oficial menor que o "
                "mínimo de segurança: "
                f"{len(texto)} < "
                f"{config['min_caracteres']}."
            )
        )

    if (
        len(
            texto.splitlines()
        )
        < config[
            "min_linhas"
        ]
    ):
        problemas.append(
            (
                "Texto oficial com linhas abaixo "
                "do mínimo de segurança."
            )
        )

    if (
        len(
            artigos
        )
        < config[
            "min_artigos"
        ]
    ):
        problemas.append(
            (
                "Quantidade de cabeçalhos de artigos "
                "abaixo do mínimo de segurança: "
                f"{len(artigos)} < "
                f"{config['min_artigos']}."
            )
        )

    faltantes = [
        artigo
        for artigo in config[
            "artigos_ancora"
        ]
        if artigo
        not in conjunto
    ]

    if faltantes:
        problemas.append(
            (
                "Artigos-âncora ausentes: "
                + ", ".join(
                    faltantes
                )
            )
        )

    if (
        config[
            "artigo_final"
        ]
        not in conjunto
    ):
        problemas.append(
            (
                "Artigo final obrigatório ausente: "
                f"{config['artigo_final']}."
            )
        )

    if (
        artigos
        and artigos[
            0
        ]
        != "1"
    ):
        problemas.append(
            (
                "O primeiro cabeçalho detectado "
                f"não é Art. 1: {artigos[0]}."
            )
        )

    # Além da estrutura, exigimos marcas de atualização recente
    # previamente confirmadas nas compilações monovigentes oficiais.
    # Isso ajuda a impedir que uma publicação histórica antiga seja
    # aceita apenas por possuir todos os números de artigo.
    texto_norm = (
        normalizar_identificador(
            texto
        )
    )

    frases_ausentes = [
        frase
        for frase in config.get(
            "frases_recentes",
            []
        )
        if (
            normalizar_identificador(
                frase
            )
            not in texto_norm
        )
    ]

    if frases_ausentes:
        problemas.append(
            (
                "Marcas de atualização recente ausentes: "
                + " | ".join(
                    frases_ausentes
                )
            )
        )

    return problemas


def _obter_fonte_especial_mestre(
    item,
):
    identificador = str(
        item.get(
            "id",
            ""
        )
    ).strip()

    config = (
        FONTES_ESPECIAIS_MESTRE[
            identificador
        ]
    )

    publicacoes = (
        _resolver_publicacoes_monovigentes(
            config[
                "norma_url"
            ]
        )
    )

    erros = []

    for url in publicacoes:
        try:
            resposta = (
                _requisitar_com_retry(
                    url
                )
            )

            texto = (
                _extrair_corpo_senado(
                    resposta.content,
                    config[
                        "titulo_inicio"
                    ],
                )
            )

            problemas = (
                _validar_especial_mestre(
                    identificador,
                    texto,
                )
            )

            if problemas:
                erros.append(
                    (
                        f"{url}: "
                        + "; ".join(
                            problemas
                        )
                    )
                )

                continue

            return {
                "texto": texto,
                "codificacao": "portal-oficial-senado",
                "fonte_nome": (
                    "Senado Federal - "
                    "Compilação Monovigente"
                ),
                "url_fonte": str(
                    resposta.url
                ),
                "metodo": (
                    "COMPILACAO_MONOVIGENTE_SENADO"
                ),
            }

        except (
            requests.RequestException,
            RuntimeError,
            ValueError,
        ) as erro:
            erros.append(
                (
                    f"{url}: {erro}"
                )
            )

    raise RuntimeError(
        (
            "Nenhuma Compilação Monovigente "
            "passou na validação forte. "
            + " | ".join(
                erros
            )
        )
    )


def _validar_candidato_generico(
    texto_novo,
    texto_atual=None,
):
    """
    Validação fail-closed para as demais normas.

    Não tenta "provar" juridicamente a vigência; apenas impede
    que uma resposta obviamente truncada/aberrante substitua
    um arquivo local já validado.
    """

    problemas = list(
        verificar_texto(
            texto_novo
        )
    )

    tamanho_novo = len(
        texto_novo
    )

    if (
        tamanho_novo
        < 500
    ):
        problemas.append(
            (
                "Candidato menor que 500 caracteres; "
                "substituição bloqueada."
            )
        )

    artigos_novos = (
        _artigos_cabecalho(
            texto_novo
        )
    )

    if texto_atual is None:
        if not artigos_novos:
            problemas.append(
                (
                    "Arquivo ausente e a fonte nova "
                    "não apresenta cabeçalhos de artigo "
                    "detectáveis; download automático "
                    "bloqueado por segurança."
                )
            )

        return problemas

    corpo_atual = corpo_arquivo_lex(
        texto_atual
    )

    tamanho_atual = len(
        corpo_atual
    )

    if (
        tamanho_atual
        >= 2000
        and tamanho_novo
        < tamanho_atual
        * 0.65
    ):
        problemas.append(
            (
                "Redução estrutural anormal: "
                f"{tamanho_atual} -> "
                f"{tamanho_novo} caracteres "
                "(menos de 65% do arquivo atual)."
            )
        )

    if (
        tamanho_atual
        >= 5000
        and tamanho_novo
        > tamanho_atual
        * 3.0
    ):
        problemas.append(
            (
                "Crescimento estrutural anormal: "
                f"{tamanho_atual} -> "
                f"{tamanho_novo} caracteres "
                "(mais de 3x o arquivo atual)."
            )
        )

    artigos_atuais = (
        _artigos_cabecalho(
            corpo_atual
        )
    )

    if (
        len(
            artigos_atuais
        )
        >= 10
        and len(
            artigos_novos
        )
        < len(
            artigos_atuais
        )
        * 0.60
    ):
        problemas.append(
            (
                "Perda anormal de cabeçalhos de artigo: "
                f"{len(artigos_atuais)} -> "
                f"{len(artigos_novos)}."
            )
        )

    conjunto_atual = set(
        artigos_atuais
    )

    conjunto_novo = set(
        artigos_novos
    )

    if (
        len(
            conjunto_atual
        )
        >= 20
    ):
        cobertura = (
            len(
                conjunto_atual
                & conjunto_novo
            )
            / len(
                conjunto_atual
            )
        )

        if cobertura < 0.65:
            problemas.append(
                (
                    "A nova fonte preserva menos de "
                    "65% dos cabeçalhos de artigos "
                    "do arquivo atual."
                )
            )

    return problemas


def _obter_candidato_mestre(
    item,
    texto_local=None,
):
    identificador = str(
        item.get(
            "id",
            ""
        )
    ).strip()

    if (
        identificador
        in FONTES_ESPECIAIS_MESTRE
    ):
        return (
            _obter_fonte_especial_mestre(
                item
            )
        )

    pagina = baixar_pagina(
        item[
            "fonte_oficial"
        ]
    )

    texto, codificacao = (
        extrair_texto(
            pagina
        )
    )

    problemas = (
        _validar_candidato_generico(
            texto,
            texto_atual=(
                texto_local
            ),
        )
    )

    if problemas:
        raise RuntimeError(
            (
                "ATUALIZAÇÃO BLOQUEADA POR INTEGRIDADE: "
                + " | ".join(
                    problemas
                )
            )
        )

    return {
        "texto": texto,
        "codificacao": codificacao,
        "fonte_nome": (
            "Presidência da República - Planalto"
        ),
        "url_fonte": item[
            "fonte_oficial"
        ],
        "metodo": (
            "HTML_PLANALTO_COM_GUARDRAILS"
        ),
    }


def _ler_texto_local_seguro(
    caminho,
):
    try:
        return caminho.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        return caminho.read_text(
            encoding="cp1252",
            errors="replace",
        )


def _montar_conteudo_mestre(
    item,
    texto,
    codificacao,
    fonte_nome,
    url_fonte,
    metodo,
):
    return (
        criar_cabecalho_mestre(
            item,
            codificacao,
            fonte_nome=(
                fonte_nome
            ),
            url_fonte=(
                url_fonte
            ),
            metodo=(
                metodo
            ),
        )
        + texto
        + "\n"
    )


def _validar_conteudo_gravado_mestre(
    item,
    conteudo,
):
    corpo = corpo_arquivo_lex(
        conteudo
    )

    identificador = str(
        item.get(
            "id",
            ""
        )
    ).strip()

    if (
        identificador
        in FONTES_ESPECIAIS_MESTRE
    ):
        return (
            _validar_especial_mestre(
                identificador,
                corpo,
            )
        )

    return verificar_texto(
        corpo
    )


def _gravar_item_mestre_transacional(
    item,
    candidato,
    caminho,
):
    """
    Grava primeiro em arquivo temporário na MESMA pasta,
    reabre, valida, cria backup do arquivo atual, usa
    os.replace() e revalida o arquivo final.

    Em qualquer falha posterior ao backup, tenta rollback.
    """

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conteudo = (
        _montar_conteudo_mestre(
            item,
            candidato[
                "texto"
            ],
            candidato[
                "codificacao"
            ],
            candidato[
                "fonte_nome"
            ],
            candidato[
                "url_fonte"
            ],
            candidato[
                "metodo"
            ],
        )
    )

    temporario = caminho.with_name(
        caminho.name
        + ".novo_lex_machina"
    )

    backup = None
    existia_antes = caminho.exists()

    try:
        temporario.write_text(
            conteudo,
            encoding="utf-8",
            newline="\n",
        )

        dados_temp = (
            temporario.read_bytes()
        )

        if (
            _hash_bytes(
                dados_temp
            )
            != _hash_bytes(
                conteudo.encode(
                    "utf-8"
                )
            )
        ):
            raise RuntimeError(
                "Hash do arquivo temporário divergente."
            )

        texto_temp = (
            dados_temp.decode(
                "utf-8"
            )
        )

        problemas_temp = (
            _validar_conteudo_gravado_mestre(
                item,
                texto_temp,
            )
        )

        if problemas_temp:
            raise RuntimeError(
                (
                    "Temporário falhou na revalidação: "
                    + " | ".join(
                        problemas_temp
                    )
                )
            )

        if caminho.exists():
            backup = (
                backup_arquivo_mestre(
                    caminho
                )
            )

        os.replace(
            temporario,
            caminho,
        )

        dados_final = (
            caminho.read_bytes()
        )

        if (
            _hash_bytes(
                dados_final
            )
            != _hash_bytes(
                conteudo.encode(
                    "utf-8"
                )
            )
        ):
            raise RuntimeError(
                "Hash final divergente após substituição."
            )

        texto_final = (
            dados_final.decode(
                "utf-8"
            )
        )

        problemas_final = (
            _validar_conteudo_gravado_mestre(
                item,
                texto_final,
            )
        )

        if problemas_final:
            raise RuntimeError(
                (
                    "Arquivo final falhou na revalidação: "
                    + " | ".join(
                        problemas_final
                    )
                )
            )

        return backup

    except Exception:
        if (
            backup is not None
            and backup.exists()
        ):
            try:
                shutil.copy2(
                    backup,
                    caminho,
                )

            except OSError:
                pass

        elif (
            not existia_antes
            and caminho.exists()
        ):
            try:
                caminho.unlink()
            except OSError:
                pass

        try:
            if temporario.exists():
                temporario.unlink()

        except OSError:
            pass

        raise


# ============================================================
# UTILITÁRIOS JSON
# ============================================================

def carregar_json(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    texto = caminho.read_text(
        encoding="utf-8"
    )

    dados = json.loads(texto)

    if not isinstance(dados, list):
        raise ValueError(
            f"{caminho} precisa conter uma lista JSON."
        )

    return dados



# ============================================================
# CATÁLOGO MESTRE / DESTINO UNIFICADO
# ============================================================

def configurar_destino(destino=None):
    """
    Configura o layout sem quebrar o modo antigo.

    Sem argumento:
        RAIZ_VADEMECUM = saida
        PASTA_SAIDA = saida

    Com argumento, por exemplo D:\\:
        RAIZ_VADEMECUM = D:\\
        PASTA_SAIDA =
            D:\\9-CÓDIGO DE DEFESA DO CONSUMIDOR
    """

    global RAIZ_VADEMECUM
    global PASTA_SAIDA
    global PASTA_RELATORIOS_GERAIS

    if destino:
        RAIZ_VADEMECUM = Path(
            destino
        )

        PASTA_SAIDA = (
            RAIZ_VADEMECUM
            / (
                "9-CÓDIGO DE DEFESA "
                "DO CONSUMIDOR"
            )
        )

    else:
        RAIZ_VADEMECUM = Path(
            "saida"
        )

        PASTA_SAIDA = Path(
            "saida"
        )

    PASTA_RELATORIOS_GERAIS = (
        RAIZ_VADEMECUM
        / "99_INDICES"
    )


def carregar_catalogo_mestre():
    if not ARQUIVO_CATALOGO_MESTRE.exists():
        raise FileNotFoundError(
            "Arquivo não encontrado: "
            f"{ARQUIVO_CATALOGO_MESTRE}"
        )

    dados = json.loads(
        ARQUIVO_CATALOGO_MESTRE.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        dados,
        dict,
    ):
        raise ValueError(
            "catalogo_mestre_vademecum.json "
            "precisa conter um objeto JSON."
        )

    itens = dados.get(
        "itens",
        []
    )

    if not isinstance(
        itens,
        list,
    ):
        raise ValueError(
            "O campo 'itens' do catálogo mestre "
            "precisa conter uma lista."
        )

    return dados, itens


def validar_catalogo_mestre(
    itens
):
    obrigatorios = {
        "id",
        "ramo",
        "nome",
        "prioridade",
        "fonte_oficial",
        "pasta_destino",
        "arquivo_sugerido",
    }

    ids = set()

    for indice, item in enumerate(
        itens,
        start=1,
    ):
        if not isinstance(
            item,
            dict,
        ):
            raise ValueError(
                "Registro mestre "
                f"{indice} inválido."
            )

        faltando = (
            obrigatorios
            - set(
                item.keys()
            )
        )

        if faltando:
            raise ValueError(
                "Registro mestre "
                f"{indice} sem campos: "
                + ", ".join(
                    sorted(
                        faltando
                    )
                )
            )

        identificador = str(
            item[
                "id"
            ]
        ).strip()

        if not identificador:
            raise ValueError(
                "Registro mestre "
                f"{indice} com ID vazio."
            )

        if identificador in ids:
            raise ValueError(
                "ID duplicado no catálogo mestre: "
                f"{identificador}"
            )

        ids.add(
            identificador
        )


def normalizar_identificador(
    texto
):
    texto = str(
        texto or ""
    ).casefold()

    substituicoes = {
        "á": "a",
        "à": "a",
        "â": "a",
        "ã": "a",
        "ä": "a",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "í": "i",
        "ì": "i",
        "î": "i",
        "ï": "i",
        "ó": "o",
        "ò": "o",
        "ô": "o",
        "õ": "o",
        "ö": "o",
        "ú": "u",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
    }

    for origem, destino in (
        substituicoes.items()
    ):
        texto = texto.replace(
            origem,
            destino,
        )

    texto = re.sub(
        r"[^a-z0-9]+",
        " ",
        texto,
    )

    return re.sub(
        r"\s+",
        " ",
        texto,
    ).strip()


def compactar_identificador(
    texto
):
    return re.sub(
        r"[^a-z0-9]+",
        "",
        normalizar_identificador(
            texto
        ),
    )


def inventariar_vademecum():
    arquivos = []

    if not RAIZ_VADEMECUM.exists():
        return arquivos

    for caminho in (
        RAIZ_VADEMECUM.rglob(
            "*"
        )
    ):
        if not caminho.is_file():
            continue

        try:
            relativo = (
                caminho.relative_to(
                    RAIZ_VADEMECUM
                )
            )

        except ValueError:
            relativo = caminho

        arquivos.append(
            {
                "absoluto": caminho,
                "relativo": str(
                    relativo
                ),
                "nome_compacto": (
                    compactar_identificador(
                        caminho.name
                    )
                ),
                "caminho_normalizado": (
                    normalizar_identificador(
                        str(
                            relativo
                        )
                    )
                ),
            }
        )

    return arquivos


def localizar_item_mestre(
    item,
    arquivos
):
    """
    Localiza de forma conservadora o arquivo correspondente
    a um item do Catálogo Mestre.

    REGRAS:

    BASE:
        1) usa o caminho canônico conhecido, quando existir;
        2) tenta o nome exato sugerido dentro da pasta esperada;
        3) tenta termos de detecção SOMENTE no nome do arquivo;
        4) nunca usa nomes de relatórios/índices como legislação;
        5) não escolhe arbitrariamente o primeiro arquivo em caso
           de ambiguidade.

    A/B/C:
        exige nome exato do arquivo sugerido dentro da pasta
        esperada.
    """

    prioridade = str(
        item.get(
            "prioridade",
            ""
        )
    ).strip().upper()

    identificador = str(
        item.get(
            "id",
            ""
        )
    ).strip()

    pasta_esperada = (
        normalizar_identificador(
            item.get(
                "pasta_destino",
                ""
            )
        )
    )

    nome_esperado = (
        compactar_identificador(
            item.get(
                "arquivo_sugerido",
                ""
            )
        )
    )

    # --------------------------------------------------------
    # PRIORIDADES A/B/C:
    # nome exato + pasta esperada.
    # --------------------------------------------------------

    if prioridade != "BASE":
        candidatos = []

        for arquivo in arquivos:
            if (
                arquivo[
                    "nome_compacto"
                ]
                != nome_esperado
            ):
                continue

            if (
                pasta_esperada
                and pasta_esperada
                not in arquivo[
                    "caminho_normalizado"
                ]
            ):
                continue

            candidatos.append(
                arquivo[
                    "absoluto"
                ]
            )

        return candidatos

    # --------------------------------------------------------
    # BASE - 1) caminho canônico.
    # --------------------------------------------------------

    relativo_canonico = (
        ARQUIVOS_BASE_CANONICOS.get(
            identificador
        )
    )

    if relativo_canonico:
        caminho_canonico = (
            RAIZ_VADEMECUM
            / Path(
                relativo_canonico
            )
        )

        if (
            caminho_canonico.exists()
            and caminho_canonico.is_file()
        ):
            return [
                caminho_canonico
            ]

    # --------------------------------------------------------
    # BASE - 2) nome exato sugerido dentro da pasta.
    # Isso também permite futuras migrações para o nome novo
    # do catálogo sem depender dos nomes históricos.
    # --------------------------------------------------------

    exatos = []

    for arquivo in arquivos:
        if (
            arquivo[
                "nome_compacto"
            ]
            != nome_esperado
        ):
            continue

        if (
            pasta_esperada
            and pasta_esperada
            not in arquivo[
                "caminho_normalizado"
            ]
        ):
            continue

        exatos.append(
            arquivo[
                "absoluto"
            ]
        )

    if len(
        exatos
    ) == 1:
        return exatos

    if len(
        exatos
    ) > 1:
        # Ambiguidade é mais segura que escolher o arquivo errado.
        return []

    # --------------------------------------------------------
    # BASE - 3) termos apenas no NOME DO ARQUIVO.
    #
    # Nunca procure no caminho inteiro: o nome da pasta
    # "CÓDIGO DE DEFESA DO CONSUMIDOR", por exemplo, faria
    # RELATORIO_ATUALIZACAO.txt parecer um CDC válido.
    # --------------------------------------------------------

    termos = [
        normalizar_identificador(
            termo
        )
        for termo in item.get(
            "detectar_por",
            []
        )
        if str(
            termo
        ).strip()
    ]

    candidatos = []

    nomes_proibidos = (
        "relatorio",
        "indice",
        "auditoria",
        "backup",
        "meta",
    )

    for arquivo in arquivos:
        if (
            pasta_esperada
            and pasta_esperada
            not in arquivo[
                "caminho_normalizado"
            ]
        ):
            continue

        caminho = arquivo[
            "absoluto"
        ]

        if (
            caminho.suffix.lower()
            != ".txt"
        ):
            continue

        nome_norm = (
            normalizar_identificador(
                caminho.name
            )
        )

        if any(
            proibido
            in nome_norm
            for proibido in nomes_proibidos
        ):
            continue

        if any(
            termo
            and termo
            in nome_norm
            for termo in termos
        ):
            candidatos.append(
                caminho
            )

    # Só aceitamos detecção heurística se o resultado for único.
    if len(
        candidatos
    ) == 1:
        return candidatos

    # --------------------------------------------------------
    # BASE - 4) fallback de arquivo único, também excluindo
    # relatórios/índices. Nunca escolhe "o primeiro".
    # --------------------------------------------------------

    txts_validos = []

    for arquivo in arquivos:
        if (
            pasta_esperada
            and pasta_esperada
            not in arquivo[
                "caminho_normalizado"
            ]
        ):
            continue

        caminho = arquivo[
            "absoluto"
        ]

        if (
            caminho.suffix.lower()
            != ".txt"
        ):
            continue

        nome_norm = (
            normalizar_identificador(
                caminho.name
            )
        )

        if any(
            proibido
            in nome_norm
            for proibido in nomes_proibidos
        ):
            continue

        txts_validos.append(
            caminho
        )

    if len(
        txts_validos
    ) == 1:
        return txts_validos

    return []


def criar_cabecalho_mestre(
    item,
    codificacao_origem,
    fonte_nome=None,
    url_fonte=None,
    metodo=None,
):
    data = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    if not fonte_nome:
        fonte_nome = (
            "Presidência da República - Planalto"
        )

    if not url_fonte:
        url_fonte = item[
            "fonte_oficial"
        ]

    if not metodo:
        metodo = (
            "HTML_PLANALTO"
        )

    return (
        "LEX MACHINA\n"
        "========================================\n"
        f"NORMA: {item['nome']}\n"
        f"RAMO: {item['ramo']}\n"
        f"PRIORIDADE: {item['prioridade']}\n"
        "TIPO_REGISTRO: LEGISLAÇÃO - CATÁLOGO MESTRE\n"
        f"FONTE: {fonte_nome}\n"
        f"URL_FONTE: {url_fonte}\n"
        f"METODO_ATUALIZACAO: {metodo}\n"
        "VALIDACAO_INTEGRIDADE: APROVADA\n"
        f"PASTA_DESTINO: {item['pasta_destino']}\n"
        f"CODIFICACAO_ORIGEM: {codificacao_origem}\n"
        "CODIFICACAO_ARQUIVO: UTF-8\n"
        f"ATUALIZADO_EM: {data}\n"
        "========================================\n\n"
    )


def caminho_novo_item_mestre(
    item
):
    pasta = (
        RAIZ_VADEMECUM
        / item[
            "pasta_destino"
        ]
    )

    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        pasta
        / item[
            "arquivo_sugerido"
        ]
    )


def corpo_arquivo_lex(
    texto
):
    """
    Remove apenas o cabeçalho gerado pelo LEX MACHINA
    quando ele existir. Arquivos antigos, sem cabeçalho,
    são preservados integralmente para comparação.
    """

    if not texto.startswith(
        "LEX MACHINA"
    ):
        return normalizar_texto(
            texto
        )

    marcador = (
        "========================================"
    )

    posicoes = [
        m.end()
        for m in re.finditer(
            re.escape(
                marcador
            ),
            texto,
        )
    ]

    if len(
        posicoes
    ) >= 2:
        texto = texto[
            posicoes[
                1
            ]:
        ]

    return normalizar_texto(
        texto
    )


def backup_arquivo_mestre(
    caminho
):
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    raiz_backup = (
        Path(
            "backup_catalogos"
        )
        / (
            "catalogo_mestre_"
            + timestamp
        )
    )

    try:
        relativo = caminho.relative_to(
            RAIZ_VADEMECUM
        )

    except ValueError:
        relativo = Path(
            caminho.name
        )

    destino = (
        raiz_backup
        / relativo
    )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        caminho,
        destino,
    )

    return destino



def salvar_item_mestre(
    item,
    texto,
    codificacao,
    caminho=None,
    fonte_nome=None,
    url_fonte=None,
    metodo=None,
):
    """
    Compatibilidade com chamadas antigas, agora usando a mesma
    gravação transacional do updater seguro.
    """

    if caminho is None:
        caminho = (
            caminho_novo_item_mestre(
                item
            )
        )

    candidato = {
        "texto": texto,
        "codificacao": codificacao,
        "fonte_nome": (
            fonte_nome
            or "Presidência da República - Planalto"
        ),
        "url_fonte": (
            url_fonte
            or item[
                "fonte_oficial"
            ]
        ),
        "metodo": (
            metodo
            or "HTML_PLANALTO_COM_GUARDRAILS"
        ),
    }

    _gravar_item_mestre_transacional(
        item,
        candidato,
        caminho,
    )

    return caminho



def processar_catalogo_mestre(
    itens,
    atualizar=False,
    simular=False,
):
    """
    Processamento seguro do Catálogo Mestre.

    Sem --atualizar-mestre:
        - verifica existência local;
        - baixa somente itens ausentes, mas apenas se a fonte
          passar na validação de integridade.

    Com --atualizar-mestre:
        - consulta a fonte oficial;
        - valida ANTES de qualquer gravação;
        - compara com o arquivo local;
        - cria backup;
        - grava temporário;
        - revalida;
        - substitui atomicamente;
        - revalida após a substituição;
        - em falha, preserva/restaura o arquivo anterior.

    Com --simular-mestre:
        - executa consulta, validação e comparação;
        - NÃO cria backup;
        - NÃO altera o cartão.
    """

    arquivos = inventariar_vademecum()

    resultados = []

    baixados = 0
    atualizados = 0
    presentes = 0
    erros = 0
    alertas = 0
    bloqueados = 0
    simulados = 0

    total = len(
        itens
    )

    for indice, item in enumerate(
        itens,
        start=1,
    ):
        print(
            (
                f"[MESTRE {indice}/{total}] "
                f"{item['nome']}"
            )
        )

        encontrados = localizar_item_mestre(
            item,
            arquivos,
        )

        caminho_existente = (
            encontrados[
                0
            ]
            if encontrados
            else None
        )

        if (
            caminho_existente
            and not atualizar
            and not simular
        ):
            presentes += 1

            resultados.append(
                {
                    "id": item[
                        "id"
                    ],
                    "nome": item[
                        "nome"
                    ],
                    "status": "PRESENTE",
                    "arquivo": str(
                        caminho_existente
                    ),
                    "observacao": (
                        "Arquivo já existente. "
                        "Verificação online não solicitada."
                    ),
                }
            )

            print(
                f"  ✓ Presente: {caminho_existente}"
            )

            continue

        texto_local = None

        if caminho_existente:
            texto_local = (
                _ler_texto_local_seguro(
                    caminho_existente
                )
            )

        try:
            if (
                str(
                    item.get(
                        "id",
                        "",
                    )
                ).strip()
                in FONTES_ESPECIAIS_MESTRE
            ):
                print(
                    (
                        "  Consultando Compilação "
                        "Monovigente oficial do Senado..."
                    )
                )
            else:
                print(
                    "  Consultando fonte oficial..."
                )

            candidato = (
                _obter_candidato_mestre(
                    item,
                    texto_local=(
                        texto_local
                    ),
                )
            )

            corpo_oficial = normalizar_texto(
                candidato[
                    "texto"
                ]
            )

            if caminho_existente:
                corpo_local = corpo_arquivo_lex(
                    texto_local
                )

                if (
                    corpo_local
                    == corpo_oficial
                ):
                    presentes += 1

                    resultados.append(
                        {
                            "id": item[
                                "id"
                            ],
                            "nome": item[
                                "nome"
                            ],
                            "status": "ATUAL",
                            "arquivo": str(
                                caminho_existente
                            ),
                            "fonte": candidato[
                                "fonte_nome"
                            ],
                            "url_fonte": candidato[
                                "url_fonte"
                            ],
                            "observacao": (
                                "Conteúdo local igual "
                                "à fonte oficial validada."
                            ),
                        }
                    )

                    print(
                        "  ✓ Já está atualizado e validado."
                    )

                    continue

                if simular:
                    simulados += 1

                    resultados.append(
                        {
                            "id": item[
                                "id"
                            ],
                            "nome": item[
                                "nome"
                            ],
                            "status": (
                                "SIMULADO_ATUALIZAR"
                            ),
                            "arquivo": str(
                                caminho_existente
                            ),
                            "fonte": candidato[
                                "fonte_nome"
                            ],
                            "url_fonte": candidato[
                                "url_fonte"
                            ],
                            "observacao": (
                                "A fonte validada difere "
                                "do arquivo local. "
                                "Nenhuma alteração foi feita."
                            ),
                        }
                    )

                    print(
                        (
                            "  ◇ SIMULAÇÃO: fonte íntegra "
                            "e conteúdo diferente. "
                            "Arquivo preservado."
                        )
                    )

                    continue

                backup = (
                    _gravar_item_mestre_transacional(
                        item,
                        candidato,
                        caminho_existente,
                    )
                )

                atualizados += 1

                resultados.append(
                    {
                        "id": item[
                            "id"
                        ],
                        "nome": item[
                            "nome"
                        ],
                        "status": "ATUALIZADO",
                        "arquivo": str(
                            caminho_existente
                        ),
                        "backup": (
                            str(
                                backup
                            )
                            if backup
                            else ""
                        ),
                        "fonte": candidato[
                            "fonte_nome"
                        ],
                        "url_fonte": candidato[
                            "url_fonte"
                        ],
                        "observacao": (
                            "Fonte validada. Backup criado, "
                            "gravação transacional concluída "
                            "e arquivo final revalidado."
                        ),
                    }
                )

                print(
                    (
                        "  ↻ Atualizado com validação "
                        f"transacional: {caminho_existente}"
                    )
                )

            else:
                caminho = (
                    caminho_novo_item_mestre(
                        item
                    )
                )

                if simular:
                    simulados += 1

                    resultados.append(
                        {
                            "id": item[
                                "id"
                            ],
                            "nome": item[
                                "nome"
                            ],
                            "status": (
                                "SIMULADO_BAIXAR"
                            ),
                            "arquivo": str(
                                caminho
                            ),
                            "fonte": candidato[
                                "fonte_nome"
                            ],
                            "url_fonte": candidato[
                                "url_fonte"
                            ],
                            "observacao": (
                                "Item ausente e fonte validada. "
                                "Nenhum arquivo foi criado "
                                "por estar em modo simulação."
                            ),
                        }
                    )

                    print(
                        (
                            "  ◇ SIMULAÇÃO: item ausente, "
                            "fonte íntegra, nenhuma gravação."
                        )
                    )

                    continue

                _gravar_item_mestre_transacional(
                    item,
                    candidato,
                    caminho,
                )

                baixados += 1

                resultados.append(
                    {
                        "id": item[
                            "id"
                        ],
                        "nome": item[
                            "nome"
                        ],
                        "status": "BAIXADO",
                        "arquivo": str(
                            caminho
                        ),
                        "fonte": candidato[
                            "fonte_nome"
                        ],
                        "url_fonte": candidato[
                            "url_fonte"
                        ],
                        "observacao": (
                            "Item ausente foi criado somente "
                            "após validação e revalidação "
                            "da fonte oficial."
                        ),
                    }
                )

                arquivos.append(
                    {
                        "absoluto": caminho,
                        "relativo": str(
                            caminho.relative_to(
                                RAIZ_VADEMECUM
                            )
                        ),
                        "nome_compacto": (
                            compactar_identificador(
                                caminho.name
                            )
                        ),
                        "caminho_normalizado": (
                            normalizar_identificador(
                                str(
                                    caminho.relative_to(
                                        RAIZ_VADEMECUM
                                    )
                                )
                            )
                        ),
                    }
                )

                print(
                    (
                        "  ↓ Baixado com validação "
                        f"transacional: {caminho}"
                    )
                )

        except RuntimeError as erro:
            bloqueados += 1
            alertas += 1

            resultados.append(
                {
                    "id": item.get(
                        "id",
                        "",
                    ),
                    "nome": item.get(
                        "nome",
                        "",
                    ),
                    "status": (
                        "BLOQUEADO_INTEGRIDADE"
                    ),
                    "arquivo": (
                        str(
                            caminho_existente
                        )
                        if caminho_existente
                        else ""
                    ),
                    "observacao": str(
                        erro
                    ),
                }
            )

            print(
                (
                    "  ⛔ BLOQUEADO: "
                    f"{erro}"
                )
            )

            if caminho_existente:
                print(
                    "  ✓ Arquivo local preservado."
                )

        except (
            requests.RequestException,
            OSError,
            ValueError,
        ) as erro:
            erros += 1

            resultados.append(
                {
                    "id": item.get(
                        "id",
                        "",
                    ),
                    "nome": item.get(
                        "nome",
                        "",
                    ),
                    "status": "ERRO",
                    "arquivo": (
                        str(
                            caminho_existente
                        )
                        if caminho_existente
                        else ""
                    ),
                    "observacao": str(
                        erro
                    ),
                }
            )

            print(
                f"  ✗ ERRO: {erro}"
            )

    return {
        "total": total,
        "presentes": presentes,
        "baixados": baixados,
        "atualizados": atualizados,
        "erros": erros,
        "alertas": alertas,
        "bloqueados": bloqueados,
        "simulados": simulados,
        "resultados": resultados,
    }


def gerar_indice_mestre_unificado(
    itens_mestre,
    registros_normas,
    registros_juris,
):
    PASTA_RELATORIOS_GERAIS.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        PASTA_RELATORIOS_GERAIS
        / "INDICE_MESTRE_UNIFICADO.txt"
    )

    linhas = [
        "LEX MACHINA",
        "ÍNDICE MESTRE UNIFICADO",
        "=" * 90,
        "",
        (
            "GERADO EM: "
            + datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )
        ),
        "",
        "CATÁLOGO MESTRE",
        "-" * 90,
    ]

    for item in itens_mestre:
        linhas.append(
            (
                f"{item.get('prioridade', '')}"
                f"|{item.get('ramo', '')}"
                f"|{item.get('nome', '')}"
                f"|{item.get('pasta_destino', '')}"
                f"|{item.get('arquivo_sugerido', '')}"
            )
        )

    linhas.extend(
        [
            "",
            "LEGISLAÇÃO CONSUMERISTA ESPECIALIZADA",
            "-" * 90,
        ]
    )

    for item in registros_normas:
        if (
            item.get(
                "tipo_registro",
                "norma",
            )
            == "referencia"
        ):
            continue

        linhas.append(
            (
                f"CONSUMIDOR"
                f"|{item.get('nome', '')}"
                f"|{item.get('pasta_destino', '')}"
                f"|{item.get('arquivo', '')}"
            )
        )

    linhas.extend(
        [
            "",
            "JURISPRUDÊNCIA",
            "-" * 90,
        ]
    )

    for item in registros_juris:
        linhas.append(
            (
                f"{item.get('tribunal', '')}"
                f"|{item.get('tipo', '')}"
                f"|{item.get('numero', '')}"
                f"|{item.get('status', '')}"
                f"|{item.get('arquivo', '')}"
            )
        )

    caminho.write_text(
        "\n".join(
            linhas
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return caminho




def gerar_relatorio_unificado(
    versao_catalogo,
    resultado_mestre,
    normas_processadas,
    referencias_processadas,
    jurisprudencias_processadas,
    erros_consumidor,
    alertas_consumidor,
):
    PASTA_RELATORIOS_GERAIS.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        PASTA_RELATORIOS_GERAIS
        / "RELATORIO_UPDATER_UNIFICADO.txt"
    )

    linhas = [
        "LEX MACHINA",
        "RELATÓRIO DO UPDATER UNIFICADO",
        "=" * 78,
        "",
        (
            "GERADO EM: "
            + datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )
        ),
        (
            "VERSÃO DO CATÁLOGO MESTRE: "
            f"{versao_catalogo}"
        ),
        f"RAIZ DO VADE MECUM: {RAIZ_VADEMECUM}",
        f"MÓDULO CONSUMIDOR: {PASTA_SAIDA}",
        "",
        "CATÁLOGO MESTRE",
        "-" * 78,
        (
            "Itens: "
            f"{resultado_mestre['total']}"
        ),
        (
            "Já presentes/atuais: "
            f"{resultado_mestre['presentes']}"
        ),
        (
            "Baixados: "
            f"{resultado_mestre['baixados']}"
        ),
        (
            "Atualizados: "
            f"{resultado_mestre['atualizados']}"
        ),
        (
            "Simulados sem gravação: "
            f"{resultado_mestre.get('simulados', 0)}"
        ),
        (
            "Bloqueados por integridade: "
            f"{resultado_mestre.get('bloqueados', 0)}"
        ),
        (
            "Erros: "
            f"{resultado_mestre['erros']}"
        ),
        (
            "Alertas: "
            f"{resultado_mestre['alertas']}"
        ),
        "",
        "DETALHES DO CATÁLOGO MESTRE",
        "-" * 78,
    ]

    resultados_mestre = (
        resultado_mestre.get(
            "resultados",
            [],
        )
    )

    if not resultados_mestre:
        linhas.append(
            "Nenhum item do Catálogo Mestre foi processado."
        )

    for registro in resultados_mestre:
        linhas.append(
            (
                f"[{registro.get('status', '')}] "
                f"{registro.get('id', '')} - "
                f"{registro.get('nome', '')}"
            )
        )

        if registro.get(
            "arquivo"
        ):
            linhas.append(
                (
                    "  Arquivo: "
                    f"{registro.get('arquivo', '')}"
                )
            )

        if registro.get(
            "fonte"
        ):
            linhas.append(
                (
                    "  Fonte: "
                    f"{registro.get('fonte', '')}"
                )
            )

        if registro.get(
            "url_fonte"
        ):
            linhas.append(
                (
                    "  URL: "
                    f"{registro.get('url_fonte', '')}"
                )
            )

        if registro.get(
            "backup"
        ):
            linhas.append(
                (
                    "  Backup: "
                    f"{registro.get('backup', '')}"
                )
            )

        if registro.get(
            "observacao"
        ):
            linhas.append(
                (
                    "  Observação: "
                    f"{registro.get('observacao', '')}"
                )
            )

        linhas.append("")

    linhas.extend(
        [
            "MÓDULO CONSUMIDOR",
            "-" * 78,
            (
                "Normas processadas: "
                f"{normas_processadas}"
            ),
            (
                "Referências cruzadas: "
                f"{referencias_processadas}"
            ),
            (
                "Jurisprudências processadas: "
                f"{jurisprudencias_processadas}"
            ),
            (
                "Erros: "
                f"{erros_consumidor}"
            ),
            (
                "Alertas: "
                f"{alertas_consumidor}"
            ),
            "",
            "RESULTADO GERAL",
            "-" * 78,
            (
                "Erros totais: "
                f"{resultado_mestre['erros'] + erros_consumidor}"
            ),
            (
                "Alertas totais: "
                f"{resultado_mestre['alertas'] + alertas_consumidor}"
            ),
            (
                "Regra de segurança: uma fonte nova só substitui "
                "o arquivo local após validação, backup, gravação "
                "temporária, substituição atômica e revalidação."
            ),
        ]
    )

    caminho.write_text(
        "\n".join(
            linhas
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return caminho


def argumentos_main():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA Updater Unificado"
        )
    )

    parser.add_argument(
        "destino",
        nargs="?",
        default=None,
        help=(
            "Raiz do Vade Mecum. "
            "Exemplo: D:\\ "
            "Se omitido, mantém o modo antigo em saida/."
        ),
    )

    parser.add_argument(
        "--atualizar-mestre",
        action="store_true",
        help=(
            "Compara as 72 normas do Catálogo Mestre "
            "com as fontes oficiais. Só atualiza uma norma "
            "depois que a nova fonte passa nas travas de "
            "integridade e na gravação transacional."
        ),
    )

    parser.add_argument(
        "--simular-mestre",
        action="store_true",
        help=(
            "Consulta, valida e compara as fontes do Catálogo "
            "Mestre, mas NÃO cria backup e NÃO altera o cartão. "
            "Use este modo antes de uma atualização real."
        ),
    )

    parser.add_argument(
        "--somente-mestre",
        action="store_true",
        help=(
            "Processa somente o Catálogo Mestre, "
            "sem regenerar o módulo consumerista."
        ),
    )

    parser.add_argument(
        "--sem-mestre",
        action="store_true",
        help=(
            "Ignora o Catálogo Mestre e executa somente "
            "o módulo consumerista/jurisprudencial."
        ),
    )

    parser.add_argument(
        "--sem-stf",
        action="store_true",
        help=(
            "Não consulta o STF (Repercussão Geral e controle concentrado). O catálogo local de "
            "precedentes é mantido como está."
        ),
    )

    parser.add_argument(
        "--sem-stf-controle",
        action="store_true",
        help="Não atualiza ADI/ADC/ADPF/ADO; mantém a consulta de Repercussão Geral.",
    )

    args = parser.parse_args()

    if (
        args.simular_mestre
        and args.sem_mestre
    ):
        parser.error(
            "--simular-mestre não pode ser usado com --sem-mestre."
        )

    if (
        args.simular_mestre
        and args.atualizar_mestre
    ):
        parser.error(
            "Use --simular-mestre OU --atualizar-mestre, não os dois."
        )

    # Segurança: simulação do Catálogo Mestre nunca deve cair
    # acidentalmente no módulo consumidor e alterar outros arquivos.
    if args.simular_mestre:
        args.somente_mestre = True

    return args


def validar_catalogo_normas(registros):
    campos_norma = {
        "nome",
        "arquivo",
        "pasta_destino",
        "url",
    }

    campos_referencia = {
        "tipo_registro",
        "nome",
        "arquivo",
        "destino_ref",
        "relacao",
    }

    for indice, registro in enumerate(
        registros,
        start=1,
    ):
        if not isinstance(registro, dict):
            raise ValueError(
                f"Registro {indice} inválido "
                "em catalogo_normas.json."
            )

        tipo = registro.get(
            "tipo_registro",
            "norma",
        )

        if tipo == "referencia":
            faltando = (
                campos_referencia
                - set(registro.keys())
            )
        else:
            faltando = (
                campos_norma
                - set(registro.keys())
            )

        if faltando:
            raise ValueError(
                f"Registro {indice} sem campos: "
                + ", ".join(
                    sorted(faltando)
                )
            )


# ============================================================
# VALIDAÇÃO DO CATÁLOGO DE JURISPRUDÊNCIA
# ============================================================

def validar_catalogo_jurisprudencia(registros):
    obrigatorios = {
        "tribunal",
        "tipo",
        "numero",
        "tema",
        "arquivo",
        "pasta_destino",
        "texto",
        "relacionado_a",
        "fonte",
    }

    for indice, registro in enumerate(
        registros,
        start=1,
    ):
        if not isinstance(registro, dict):
            raise ValueError(
                f"Registro {indice} inválido "
                "em catalogo_jurisprudencia.json."
            )

        faltando = (
            obrigatorios
            - set(registro.keys())
        )

        if faltando:
            raise ValueError(
                f"Jurisprudência {indice} sem campos: "
                + ", ".join(
                    sorted(faltando)
                )
            )

        if not isinstance(
            registro["relacionado_a"],
            list,
        ):
            raise ValueError(
                f"'relacionado_a' da jurisprudência "
                f"{indice} precisa ser uma lista."
            )


# ============================================================
# DOWNLOAD DE LEGISLAÇÃO
# ============================================================

def baixar_pagina(url):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=40,
    )

    resposta.raise_for_status()

    return resposta.content


# ============================================================
# DECODIFICAÇÃO
# ============================================================

def pontuar_texto(texto):
    suspeitos = [
        "ę",
        "ş",
        "Ă",
        "Ţ",
        "ŕ",
        "ő",
        "ű",
        "Ã§",
        "Ã£",
        "Ã¡",
        "Ã©",
        "Ã³",
        "Ãº",
        "Âº",
        "Â§",
        "�",
    ]

    pontos = 0

    for caractere in suspeitos:
        pontos += (
            texto.count(caractere)
            * 10
        )

    naturais = [
        "ção",
        "ções",
        "ência",
        "ública",
        "não",
        "Art.",
        "Lei",
    ]

    for trecho in naturais:
        pontos -= texto.count(
            trecho
        )

    return pontos


def decodificar_html(conteudo):
    candidatos = []

    for codificacao in (
        "utf-8",
        "cp1252",
        "iso-8859-1",
    ):
        try:
            texto = conteudo.decode(
                codificacao,
                errors="strict",
            )

            candidatos.append(
                (
                    pontuar_texto(texto),
                    codificacao,
                    texto,
                )
            )

        except UnicodeDecodeError:
            continue

    if not candidatos:
        return (
            conteudo.decode(
                "cp1252",
                errors="replace",
            ),
            "cp1252",
        )

    candidatos.sort(
        key=lambda item: item[0]
    )

    _, codificacao, texto = (
        candidatos[0]
    )

    return texto, codificacao


# ============================================================
# DETECÇÃO DE TEXTO RISCADO
# ============================================================

def normalizar_css(valor):
    if not valor:
        return ""

    return (
        str(valor)
        .lower()
        .replace(" ", "")
        .replace("\n", "")
        .replace("\t", "")
    )


def elemento_riscado(tag):
    if tag is None:
        return False

    nome = getattr(
        tag,
        "name",
        None,
    )

    if nome in {
        "strike",
        "s",
        "del",
    }:
        return True

    attrs = getattr(
        tag,
        "attrs",
        None,
    )

    if not attrs:
        return False

    estilo = normalizar_css(
        attrs.get("style")
    )

    return (
        "line-through"
        in estilo
    )


def remover_texto_riscado(soup):
    tags = list(
        soup.find_all(True)
    )

    for tag in reversed(tags):
        try:
            if elemento_riscado(tag):
                tag.decompose()

        except (
            AttributeError,
            TypeError,
        ):
            continue


# ============================================================
# REMOÇÃO DE ELEMENTOS NÃO JURÍDICOS
# ============================================================

def remover_elementos_nao_juridicos(
    soup
):
    tipos = [
        "script",
        "style",
        "noscript",
        "iframe",
        "svg",
        "canvas",
    ]

    for nome in tipos:
        for tag in soup.find_all(nome):
            try:
                tag.decompose()

            except AttributeError:
                continue


# ============================================================
# NORMALIZAÇÃO DO TEXTO
# ============================================================

def compactar_linhas(texto):
    linhas = []
    anterior_vazia = False

    for linha in texto.splitlines():
        linha = linha.strip()

        if not linha:
            if not anterior_vazia:
                linhas.append("")

            anterior_vazia = True
            continue

        linhas.append(linha)
        anterior_vazia = False

    return "\n".join(
        linhas
    ).strip()


def normalizar_texto(texto):
    texto = texto.replace(
        "\xa0",
        " ",
    )

    texto = texto.replace(
        "\u2002",
        " ",
    )

    texto = texto.replace(
        "\u2003",
        " ",
    )

    texto = texto.replace(
        "\u2009",
        " ",
    )

    texto = re.sub(
        r"[ \t]+",
        " ",
        texto,
    )

    return compactar_linhas(
        texto
    )


# ============================================================
# EXTRAÇÃO DE LEGISLAÇÃO
# ============================================================

def extrair_texto(conteudo_bytes):
    html, codificacao = (
        decodificar_html(
            conteudo_bytes
        )
    )

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    remover_elementos_nao_juridicos(
        soup
    )

    remover_texto_riscado(
        soup
    )

    corpo = (
        soup.body
        or soup
    )

    texto = corpo.get_text(
        separator="\n",
        strip=True,
    )

    texto = normalizar_texto(
        texto
    )

    return (
        texto,
        codificacao,
    )


# ============================================================
# VALIDAÇÃO DE TEXTO
# ============================================================

CARACTERES_SUSPEITOS = (
    "ę",
    "ş",
    "Ă",
    "Ţ",
    "ŕ",
    "ő",
    "ű",
    "Ã§",
    "Ã£",
    "Ã¡",
    "Ã©",
    "Ã³",
    "Ãº",
    "Âº",
    "Â§",
    "�",
)


def verificar_texto(texto):
    problemas = []

    if len(texto) < 100:
        problemas.append(
            "Texto extraído pequeno demais."
        )

    ruins = [
        item
        for item
        in CARACTERES_SUSPEITOS
        if item in texto
    ]

    if ruins:
        problemas.append(
            "Possível problema de codificação: "
            + ", ".join(
                repr(x)
                for x in ruins
            )
        )

    return problemas


# ============================================================
# CABEÇALHO DA LEGISLAÇÃO
# ============================================================

def criar_cabecalho_norma(
    norma,
    codificacao_origem,
):
    data = datetime.now().strftime(
        "%d/%m/%Y"
    )

    return (
        "LEX MACHINA\n"
        "========================================\n"
        f"NORMA: {norma['nome']}\n"
        "TIPO_REGISTRO: LEGISLAÇÃO\n"
        "FONTE: Presidência da República - Planalto\n"
        f"URL_FONTE: {norma['url']}\n"
        f"PASTA_DESTINO: {norma['pasta_destino']}\n"
        f"CODIFICACAO_ORIGEM: {codificacao_origem}\n"
        "CODIFICACAO_ARQUIVO: UTF-8\n"
        f"BAIXADO_EM: {data}\n"
        "STATUS_DE_REVISAO: AUTOMÁTICO - AGUARDANDO VALIDAÇÃO\n"
        "REGRA_REVOGADOS: SOMENTE MARCAÇÃO HTML RISCADA\n"
        "========================================\n\n"
    )


# ============================================================
# SALVAR LEGISLAÇÃO
# ============================================================


def salvar_norma(
    norma,
    texto,
    codificacao,
):
    """
    Salva a legislação consumerista de forma transacional.

    O conteúdo já precisa ter sido validado por processar_norma().
    Se o arquivo existir, uma cópia é guardada em backup_saida/
    antes da substituição.
    """

    pasta = (
        PASTA_SAIDA
        / norma[
            "pasta_destino"
        ]
    )

    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        pasta
        / norma["arquivo"]
    )

    conteudo = (
        criar_cabecalho_norma(
            norma,
            codificacao,
        )
        + texto
        + "\n"
    )

    temporario = caminho.with_name(
        caminho.name
        + ".novo_lex_machina"
    )

    backup = None
    existia_antes = caminho.exists()

    try:
        temporario.write_text(
            conteudo,
            encoding="utf-8",
            newline="\n",
        )

        dados_temp = temporario.read_bytes()

        if (
            _hash_bytes(
                dados_temp
            )
            != _hash_bytes(
                conteudo.encode(
                    "utf-8"
                )
            )
        ):
            raise RuntimeError(
                "Hash temporário divergente "
                "no módulo consumidor."
            )

        if caminho.exists():
            stamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            raiz_backup = (
                Path(
                    "backup_saida"
                )
                / (
                    "modulo_consumidor_"
                    + stamp
                )
            )

            try:
                relativo = caminho.relative_to(
                    PASTA_SAIDA
                )

            except ValueError:
                relativo = Path(
                    caminho.name
                )

            backup = (
                raiz_backup
                / relativo
            )

            backup.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                caminho,
                backup,
            )

        os.replace(
            temporario,
            caminho,
        )

        dados_final = caminho.read_bytes()

        if (
            _hash_bytes(
                dados_final
            )
            != _hash_bytes(
                conteudo.encode(
                    "utf-8"
                )
            )
        ):
            raise RuntimeError(
                "Hash final divergente "
                "no módulo consumidor."
            )

        return caminho

    except Exception:
        if (
            backup is not None
            and backup.exists()
        ):
            try:
                shutil.copy2(
                    backup,
                    caminho,
                )

            except OSError:
                pass

        elif (
            not existia_antes
            and caminho.exists()
        ):
            try:
                caminho.unlink()
            except OSError:
                pass

        try:
            if temporario.exists():
                temporario.unlink()

        except OSError:
            pass

        raise


def salvar_referencia(registro):
    pasta = (
        PASTA_SAIDA
        / "90_REFERENCIAS_CRUZADAS"
    )

    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        pasta
        / registro["arquivo"]
    )

    conteudo = (
        "LEX MACHINA\n"
        "========================================\n"
        "TIPO_REGISTRO: REFERÊNCIA CRUZADA\n"
        f"NOME: {registro['nome']}\n"
        f"DESTINO: {registro['destino_ref']}\n"
        f"RELAÇÃO: {registro['relacao']}\n"
        "========================================\n"
    )

    caminho.write_text(
        conteudo,
        encoding="utf-8",
        newline="\n",
    )

    return caminho


# ============================================================
# NOMES DOS TIPOS DE JURISPRUDÊNCIA
# ============================================================

def normalizar_tipo_jurisprudencia(
    tipo
):
    mapa = {
        "sumula": "SÚMULA",
        "sumula_vinculante": (
            "SÚMULA VINCULANTE"
        ),
        "repetitivo": (
            "RECURSO REPETITIVO"
        ),
        "repercussao_geral": (
            "REPERCUSSÃO GERAL"
        ),
        "acordao": "ACÓRDÃO",
        "precedente": "PRECEDENTE QUALIFICADO",
        "irdr": "IRDR",
        "iac": "IAC",
        "irr": "IRR",
        "adi": "ADI",
        "adc": "ADC",
        "adpf": "ADPF",
        "ado": "ADO",
    }

    return mapa.get(
        tipo,
        tipo.upper(),
    )


# ============================================================
# STATUS INTERNO DA JURISPRUDÊNCIA
# ============================================================

def normalizar_status_pasta(
    registro
):
    status = registro.get(
        "status",
        "julgado",
    )

    status = str(
        status
    ).strip().lower()

    mapa = {
        "julgado": "JULGADOS",
        "pendente": "PENDENTES",
        "sobrestado": "SOBRESTADOS",
        "cancelado": "CANCELADOS",
        "superado": "SUPERADOS",
    }

    return mapa.get(
        status,
        status.upper(),
    )


# ============================================================
# SALVAR JURISPRUDÊNCIA
# ============================================================

def salvar_jurisprudencia(
    registro
):
    pasta = (
        PASTA_SAIDA
        / registro[
            "pasta_destino"
        ]
    )

    if (
        registro.get("tipo")
        == "repetitivo"
    ):
        pasta = (
            pasta
            / normalizar_status_pasta(
                registro
            )
        )

    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        pasta
        / registro["arquivo"]
    )

    tipo_formatado = (
        normalizar_tipo_jurisprudencia(
            registro["tipo"]
        )
    )

    relacionados = "\n".join(
        f"- {item}"
        for item
        in registro.get(
            "relacionado_a",
            []
        )
    )

    # --------------------------------------------------------
    # STATUS INTERNO
    # --------------------------------------------------------

    status_interno = str(
        registro.get(
            "status",
            "julgado",
        )
    ).strip().lower()

    # --------------------------------------------------------
    # TEXTO ORIGINAL DO CATÁLOGO
    # --------------------------------------------------------

    texto_original = str(
        registro.get(
            "texto",
            "",
        )
    ).strip()

    # --------------------------------------------------------
    # TESE OFICIAL ENCONTRADA PELO VERIFICADOR STJ
    # --------------------------------------------------------

    texto_oficial = str(
        registro.get(
            "texto_oficial_verificado",
            "",
        )
    ).strip()

    # --------------------------------------------------------
    # QUESTÃO OFICIAL
    # --------------------------------------------------------

    questao_oficial = str(
        registro.get(
            "questao_oficial_verificada",
            "",
        )
    ).strip()

    # --------------------------------------------------------
    # REGRA DE PREFERÊNCIA DA FONTE
    # --------------------------------------------------------

    usar_tese_oficial = bool(
        registro.get(
            "usar_tese_oficial",
            False,
        )
    )

    fonte_preferencial = str(
        registro.get(
            "fonte_texto_preferencial",
            "",
        )
    ).strip()

    if (
        fonte_preferencial
        == "texto_oficial_verificado"
    ):
        usar_tese_oficial = True

    # --------------------------------------------------------
    # ESCOLHA DO CONTEÚDO PRINCIPAL
    #
    # Julgado:
    #   usa a tese oficial quando ela existe.
    #
    # Pendente / sobrestado:
    #   usa a questão submetida, pois ainda não deve ser
    #   apresentado ao usuário como se houvesse tese final.
    #
    # Cancelado / superado:
    #   preserva o conteúdo histórico, com aviso explícito.
    # --------------------------------------------------------

    titulo_conteudo = (
        "TESE / ENUNCIADO PRINCIPAL:"
    )

    aviso_status = ""

    if status_interno == "pendente":
        aviso_status = (
            "ATENÇÃO: TEMA PENDENTE. "
            "Ainda não há tese definitiva aplicável "
            "como julgamento final."
        )

        if questao_oficial:
            texto_principal = (
                questao_oficial
            )

            origem_texto = (
                "QUESTÃO OFICIAL SUBMETIDA "
                "A JULGAMENTO"
            )

            titulo_conteudo = (
                "QUESTÃO EM JULGAMENTO:"
            )

        elif texto_original:
            texto_principal = (
                texto_original
            )

            origem_texto = (
                "TEXTO DO CATÁLOGO - "
                "TEMA AINDA PENDENTE"
            )

            titulo_conteudo = (
                "CONTEÚDO DO TEMA PENDENTE:"
            )

        else:
            texto_principal = (
                "Tema pendente de julgamento."
            )

            origem_texto = (
                "STATUS OFICIAL"
            )

            titulo_conteudo = (
                "SITUAÇÃO:"
            )

    elif status_interno == "sobrestado":
        aviso_status = (
            "ATENÇÃO: TEMA SOBRESTADO. "
            "O andamento está suspenso/sobrestado "
            "conforme a situação oficial registrada."
        )

        if questao_oficial:
            texto_principal = (
                questao_oficial
            )

            origem_texto = (
                "QUESTÃO OFICIAL DO TEMA SOBRESTADO"
            )

            titulo_conteudo = (
                "QUESTÃO SUBMETIDA:"
            )

        elif texto_original:
            texto_principal = (
                texto_original
            )

            origem_texto = (
                "TEXTO DO CATÁLOGO - "
                "TEMA SOBRESTADO"
            )

            titulo_conteudo = (
                "CONTEÚDO DO TEMA SOBRESTADO:"
            )

        else:
            texto_principal = (
                "Tema sobrestado."
            )

            origem_texto = (
                "STATUS OFICIAL"
            )

            titulo_conteudo = (
                "SITUAÇÃO:"
            )

    elif status_interno == "cancelado":
        aviso_status = (
            "ATENÇÃO: TEMA CANCELADO. "
            "Este registro é mantido apenas para "
            "consulta histórica e não deve ser tratado "
            "como precedente vigente."
        )

        if texto_oficial:
            texto_principal = (
                texto_oficial
            )

            origem_texto = (
                "TEXTO OFICIAL HISTÓRICO "
                "DO TEMA CANCELADO"
            )

        elif texto_original:
            texto_principal = (
                texto_original
            )

            origem_texto = (
                "TEXTO HISTÓRICO DO CATÁLOGO"
            )

        elif questao_oficial:
            texto_principal = (
                questao_oficial
            )

            origem_texto = (
                "QUESTÃO OFICIAL HISTÓRICA"
            )

        else:
            texto_principal = (
                "Tema cancelado."
            )

            origem_texto = (
                "STATUS OFICIAL"
            )

        titulo_conteudo = (
            "CONTEÚDO HISTÓRICO:"
        )

    elif status_interno == "superado":
        aviso_status = (
            "ATENÇÃO: TEMA SUPERADO. "
            "Este registro é mantido para consulta "
            "histórica e não deve ser usado como "
            "entendimento atual sem nova conferência."
        )

        if texto_oficial:
            texto_principal = (
                texto_oficial
            )

            origem_texto = (
                "TEXTO OFICIAL HISTÓRICO "
                "DO TEMA SUPERADO"
            )

        elif texto_original:
            texto_principal = (
                texto_original
            )

            origem_texto = (
                "TEXTO HISTÓRICO DO CATÁLOGO"
            )

        elif questao_oficial:
            texto_principal = (
                questao_oficial
            )

            origem_texto = (
                "QUESTÃO OFICIAL HISTÓRICA"
            )

        else:
            texto_principal = (
                "Tema superado."
            )

            origem_texto = (
                "STATUS OFICIAL"
            )

        titulo_conteudo = (
            "CONTEÚDO HISTÓRICO:"
        )

    else:
        if (
            texto_oficial
            and (
                usar_tese_oficial
                or status_interno == "julgado"
            )
        ):
            texto_principal = (
                texto_oficial
            )

            origem_texto = (
                "TESE OFICIAL VERIFICADA "
                "NA FONTE OFICIAL"
            )

        elif texto_oficial:
            texto_principal = (
                texto_oficial
            )

            origem_texto = (
                "TEXTO OFICIAL VERIFICADO "
                "NA FONTE OFICIAL"
            )

        elif texto_original:
            texto_principal = (
                texto_original
            )

            origem_texto = (
                "TEXTO CADASTRADO "
                "AINDA NÃO VERIFICADO "
                "COMO TESE OFICIAL"
            )

        elif questao_oficial:
            texto_principal = (
                questao_oficial
            )

            origem_texto = (
                "QUESTÃO OFICIAL SUBMETIDA "
                "A JULGAMENTO"
            )

            titulo_conteudo = (
                "QUESTÃO SUBMETIDA:"
            )

        else:
            texto_principal = (
                "Conteúdo não disponível."
            )

            origem_texto = (
                "SEM CONTEÚDO TEXTUAL DISPONÍVEL"
            )

    # --------------------------------------------------------
    # Registros de controle concentrado não são teses de Repercussão Geral.
    # Preserva a natureza do texto e a cronologia publicada pelo STF.
    if registro.get("natureza_texto_oficial") == "registro_de_decisao_final_no_corte_aberta":
        titulo_conteudo = "DECISÃO DE MÉRITO E ANDAMENTOS POSTERIORES:"
        origem_texto = "REGISTROS OFICIAIS DO CORTE ABERTA / STF"
        aviso_status = (
            "Julgamento de mérito acompanhado dos andamentos posteriores disponíveis na base. "
            "A ordenação não interpreta os efeitos de embargos, modulação ou revisão."
        )

    # STATUS OFICIAL DO STJ
    # --------------------------------------------------------

    status_oficial = str(
        registro.get(
            "status_oficial_stj",
            "",
        )
    ).strip()

    if not status_oficial:
        status_oficial = str(
            registro.get(
                "status",
                "não informado",
            )
        )

    # --------------------------------------------------------
    # ÚLTIMA VERIFICAÇÃO
    # --------------------------------------------------------

    ultima_verificacao = str(
        registro.get(
            "ultima_verificacao",
            "",
        )
    ).strip()

    if not ultima_verificacao:
        ultima_verificacao = (
            "não verificado"
        )

    # --------------------------------------------------------
    # URL DA VERIFICAÇÃO
    # --------------------------------------------------------

    url_verificacao = str(
        registro.get(
            "url_verificacao",
            "",
        )
    ).strip()

    # --------------------------------------------------------
    # DATAS E PROCESSOS, CASO EXISTAM
    # --------------------------------------------------------

    data_afetacao = str(
        registro.get(
            "data_afetacao",
            "",
        )
    ).strip()

    data_julgamento = str(
        registro.get(
            "data_julgamento",
            "",
        )
    ).strip()

    data_publicacao = str(
        registro.get(
            "data_publicacao",
            "",
        )
    ).strip()

    processos = registro.get(
        "processos",
        [],
    )

    if not isinstance(
        processos,
        list,
    ):
        processos = []

    # --------------------------------------------------------
    # CONSTRUÇÃO DO ARQUIVO
    # --------------------------------------------------------

    linhas = [
        "LEX MACHINA - JURISPRUDÊNCIA",
        "========================================",
        f"TRIBUNAL: {registro['tribunal']}",
        f"TIPO: {tipo_formatado}",
        f"NÚMERO: {registro['numero']}",
        f"TEMA: {registro['tema']}",
        f"STATUS INTERNO: {status_interno.upper()}",
        f"STATUS OFICIAL: {status_oficial}",
        f"ÚLTIMA VERIFICAÇÃO: {ultima_verificacao}",
        f"ORIGEM DO TEXTO: {origem_texto}",
        "",
    ]

    # --------------------------------------------------------
    # AVISO DE STATUS
    # --------------------------------------------------------

    if aviso_status:
        linhas.extend(
            [
                "========================================",
                aviso_status,
                "========================================",
                "",
            ]
        )

    # --------------------------------------------------------
    # DATAS
    # --------------------------------------------------------

    if data_afetacao:
        linhas.append(
            f"DATA DE AFETAÇÃO: {data_afetacao}"
        )

    if data_julgamento:
        linhas.append(
            f"DATA DE JULGAMENTO: {data_julgamento}"
        )

    if data_publicacao:
        linhas.append(
            f"DATA DE PUBLICAÇÃO: {data_publicacao}"
        )

    if (
        data_afetacao
        or data_julgamento
        or data_publicacao
    ):
        linhas.append("")

    # --------------------------------------------------------
    # PROCESSOS PARADIGMA
    # --------------------------------------------------------

    if processos:
        linhas.append(
            "PROCESSOS PARADIGMA:"
        )

        for processo in processos:
            linhas.append(
                f"- {processo}"
            )

        linhas.append("")

    # --------------------------------------------------------
    # ARTIGOS RELACIONADOS
    # --------------------------------------------------------

    if relacionados:
        linhas.extend(
            [
                "RELACIONADO A:",
                relacionados,
                "",
            ]
        )

    # --------------------------------------------------------
    # QUESTÃO SUBMETIDA
    #
    # Para pendente/sobrestado ela já pode ser o conteúdo
    # principal. Evitamos repeti-la duas vezes.
    # --------------------------------------------------------

    if (
        questao_oficial
        and texto_principal
        != questao_oficial
    ):
        linhas.extend(
            [
                "QUESTÃO SUBMETIDA A JULGAMENTO:",
                questao_oficial,
                "",
            ]
        )

    # --------------------------------------------------------
    # CONTEÚDO PRINCIPAL
    # --------------------------------------------------------

    linhas.extend(
        [
            titulo_conteudo,
            texto_principal,
            "",
        ]
    )

    # --------------------------------------------------------
    # TESE OFICIAL ADICIONAL
    #
    # Em pendentes ou sobrestados, se houver algum texto
    # oficial previamente armazenado, ele é exibido separado
    # e nunca apresentado como se fosse automaticamente uma
    # tese final vigente.
    # --------------------------------------------------------

    if (
        status_interno
        in {
            "pendente",
            "sobrestado",
        }
        and texto_oficial
        and texto_oficial
        != texto_principal
    ):
        linhas.extend(
            [
                "TEXTO OFICIAL ARMAZENADO:",
                texto_oficial,
                "",
            ]
        )

    # --------------------------------------------------------
    # RESUMO ORIGINAL
    # --------------------------------------------------------

    if (
        texto_original
        and texto_original
        != texto_principal
    ):
        normalizado_principal = (
            normalizar_texto(
                texto_principal
            )
        )

        normalizado_original = (
            normalizar_texto(
                texto_original
            )
        )

        if (
            normalizado_principal
            != normalizado_original
        ):
            linhas.extend(
                [
                    "TEXTO CADASTRADO ORIGINALMENTE:",
                    texto_original,
                    "",
                ]
            )

    # --------------------------------------------------------
    # OBSERVAÇÕES DE AUDITORIA
    # --------------------------------------------------------

    observacao = str(
        registro.get(
            "observacao_verificacao",
            "",
        )
    ).strip()

    resolucao = str(
        registro.get(
            "resolucao_auditoria",
            "",
        )
    ).strip()

    if observacao:
        linhas.extend(
            [
                "OBSERVAÇÃO DE VERIFICAÇÃO:",
                observacao,
                "",
            ]
        )

    if resolucao:
        linhas.extend(
            [
                "RESOLUÇÃO DE AUDITORIA:",
                resolucao,
                "",
            ]
        )

    # --------------------------------------------------------
    # FONTE
    # --------------------------------------------------------

    linhas.extend(
        [
            "FONTE:",
            registro.get(
                "fonte",
                "",
            ),
        ]
    )

    if url_verificacao:
        linhas.extend(
            [
                "",
                "URL DE VERIFICAÇÃO:",
                url_verificacao,
            ]
        )

    linhas.append(
        "========================================"
    )

    conteudo = (
        "\n".join(
            linhas
        )
        + "\n"
    )

    caminho.write_text(
        conteudo,
        encoding="utf-8",
        newline="\n",
    )

    return caminho


# ============================================================
# ÍNDICE DE JURISPRUDÊNCIA
# ============================================================

def gerar_indice_jurisprudencia(
    registros
):
    pasta = (
        PASTA_SAIDA
        / "99_INDICES"
    )

    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        pasta
        / "INDICE_JURISPRUDENCIA_CDC.txt"
    )

    linhas = []

    for registro in registros:
        status = registro.get(
            "status_oficial_stj",
            registro.get(
                "status",
                "",
            ),
        )

        for relacao in registro.get(
            "relacionado_a",
            [],
        ):
            linha = (
                f"{relacao}"
                f"|{registro['tribunal']}"
                f"|{registro['tipo']}"
                f"|{registro['numero']}"
                f"|{status}"
                f"|{registro['arquivo']}"
            )

            linhas.append(
                linha
            )

    linhas.sort()

    conteudo = (
        "LEX MACHINA - ÍNDICE DE JURISPRUDÊNCIA\n"
        "======================================================================\n"
        "FORMATO:\n"
        "REFERÊNCIA|TRIBUNAL|TIPO|NÚMERO|STATUS|ARQUIVO\n"
        "======================================================================\n\n"
        + "\n".join(
            linhas
        )
        + "\n"
    )

    caminho.write_text(
        conteudo,
        encoding="utf-8",
        newline="\n",
    )

    return caminho


# ============================================================
# ÍNDICES REVERSOS DA CAMADA JURÍDICA V2
# ============================================================

def _eh_acordao_registro(registro):
    return str(registro.get("tipo", "")).strip().lower() == "acordao"


def _eh_precedente_registro(registro):
    tipo = str(registro.get("tipo", "")).strip().lower()
    return tipo in {
        "precedente", "repercussao_geral", "irdr", "iac",
        "irr", "adi", "adc", "adpf", "ado",
    }


def gerar_indice_relacoes_especializado(registros, categoria):
    """Gera um índice reverso artigo -> item com caminho explícito.

    Mantém o índice antigo intacto e cria os novos arquivos em
    99_RELATIONS_V1, compatíveis com a futura tela 3/4 do firmware.
    """
    if categoria == "acordaos":
        selecionados = [r for r in registros if _eh_acordao_registro(r)]
        pasta = PASTA_SAIDA / "99_RELATIONS_V1" / "02_ACORDAOS"
        arquivo = "INDICE_ACORDAOS.txt"
        titulo = "ACÓRDÃOS"
    elif categoria == "precedentes":
        selecionados = [r for r in registros if _eh_precedente_registro(r)]
        pasta = PASTA_SAIDA / "99_RELATIONS_V1" / "03_PRECEDENTES"
        arquivo = "INDICE_PRECEDENTES.txt"
        titulo = "PRECEDENTES QUALIFICADOS"
    else:
        raise ValueError(f"Categoria de relação desconhecida: {categoria}")

    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / arquivo
    linhas = []

    for registro in selecionados:
        status = registro.get(
            "status_oficial_stj",
            registro.get("status", ""),
        )
        pasta_destino = str(registro.get("pasta_destino", "")).strip()
        for relacao in registro.get("relacionado_a", []):
            linhas.append(
                f"{relacao}|{registro['tribunal']}|{registro['tipo']}|"
                f"{registro['numero']}|{status}|{registro['arquivo']}|"
                f"{pasta_destino}"
            )

    linhas.sort()
    conteudo = (
        f"LEX MACHINA - ÍNDICE DE {titulo}\n"
        + "=" * 90 + "\n"
        + "FORMATO:\n"
        + "REFERÊNCIA|TRIBUNAL|TIPO|NÚMERO|STATUS|ARQUIVO|PASTA_DESTINO\n"
        + "=" * 90 + "\n\n"
        + "\n".join(linhas)
        + ("\n" if linhas else "")
    )
    caminho.write_text(conteudo, encoding="utf-8", newline="\n")
    return caminho


def gerar_indice_sumulas_vinculantes(registros):
    """Lista própria para a futura opção SÚMULAS VINCULANTES do firmware."""
    selecionados = [
        r for r in registros
        if str(r.get("tipo", "")).strip().lower() == "sumula_vinculante"
    ]
    pasta = PASTA_SAIDA / "99_RELATIONS_V1" / "02_SUMULAS_VINCULANTES"
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / "INDICE_SUMULAS_VINCULANTES.txt"
    linhas = [
        f"{r['numero']}|{r.get('status', '')}|{r['arquivo']}|{r['pasta_destino']}"
        for r in sorted(selecionados, key=lambda x: int(x["numero"]))
    ]
    conteudo = (
        f"SÚMULAS VINCULANTES ({len(selecionados)})\n"
        + "=" * 72 + "\n"
        + "FORMATO: NÚMERO|STATUS|ARQUIVO|PASTA_DESTINO\n"
        + "=" * 72 + "\n\n"
        + "\n".join(linhas)
        + ("\n" if linhas else "")
    )
    caminho.write_text(conteudo, encoding="utf-8", newline="\n")
    return caminho


def gerar_manifesto_camadas_juridicas(registros):
    pasta = PASTA_SAIDA / "99_RELATIONS_V1"
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / "LEIA-ME_CAMADAS_JURIDICAS.txt"

    qtd_sumulas = sum(1 for r in registros if str(r.get("tipo", "")).lower() == "sumula")
    qtd_sumulas_vinculantes = sum(
        1 for r in registros
        if str(r.get("tipo", "")).lower() == "sumula_vinculante"
    )
    qtd_repetitivos = sum(1 for r in registros if str(r.get("tipo", "")).lower() == "repetitivo")
    qtd_acordaos = sum(1 for r in registros if _eh_acordao_registro(r))
    qtd_precedentes = sum(1 for r in registros if _eh_precedente_registro(r))

    conteudo = (
        "LEX MACHINA - CAMADAS JURÍDICAS\n"
        + "=" * 72 + "\n"
        + "1 = SÚMULAS\n"
        + "2 = SÚMULAS VINCULANTES\n"
        + "3 = ACÓRDÃOS\n"
        + "4 = TEMAS DE REPERCUSSÃO GERAL\n"
        + "5 = RECURSOS REPETITIVOS\n"
        + "6 = PRECEDENTES RELEVANTES\n\n"
        + f"Súmulas cadastradas: {qtd_sumulas}\n"
        + f"SÚMULAS VINCULANTES ({qtd_sumulas_vinculantes})\n"
        + f"Repetitivos cadastrados: {qtd_repetitivos}\n"
        + f"Acórdãos cadastrados: {qtd_acordaos}\n"
        + f"Precedentes cadastrados: {qtd_precedentes}\n\n"
        + "Subtipos aceitos em PRECEDENTES: repercussao_geral, irdr, iac, "
          "irr, adi, adc, adpf e ado.\n"
        + "Os índices 02_ACORDAOS e 03_PRECEDENTES possuem o caminho "
          "de destino explícito para o firmware.\n"
    )
    caminho.write_text(conteudo, encoding="utf-8", newline="\n")
    return caminho


# ============================================================
# ÍNDICE POR ARTIGO
# ============================================================

def gerar_indice_artigos(
    registros
):
    pasta = (
        PASTA_SAIDA
        / "99_INDICES"
    )

    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        pasta
        / "INDICE_ARTIGOS_CDC.txt"
    )

    mapa = {}

    for registro in registros:
        for referencia in registro.get(
            "relacionado_a",
            [],
        ):
            mapa.setdefault(
                referencia,
                [],
            )

            mapa[
                referencia
            ].append(
                (
                    registro[
                        "tribunal"
                    ],
                    registro[
                        "tipo"
                    ],
                    registro[
                        "numero"
                    ],
                    registro[
                        "arquivo"
                    ],
                )
            )

    linhas = [
        "LEX MACHINA",
        "ÍNDICE DE ARTIGOS DO CDC",
        "=" * 70,
        "",
    ]

    for referencia in sorted(
        mapa.keys()
    ):
        linhas.append(
            referencia
        )

        for item in mapa[
            referencia
        ]:
            tribunal = item[0]
            tipo = item[1]
            numero = item[2]
            arquivo = item[3]

            linhas.append(
                (
                    f"  -> {tribunal} "
                    f"{tipo} {numero} "
                    f"| {arquivo}"
                )
            )

        linhas.append("")

    caminho.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )

    return caminho


# ============================================================
# RELATÓRIO DE JURISPRUDÊNCIA
# ============================================================

def gerar_relatorio_jurisprudencia(
    registros
):
    pasta = (
        PASTA_SAIDA
        / "99_INDICES"
    )

    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        pasta
        / "RELATORIO_JURISPRUDENCIA.txt"
    )

    total = len(
        registros
    )

    oficiais = 0
    nao_verificados = 0

    contagem_status = {
        "julgado": 0,
        "pendente": 0,
        "sobrestado": 0,
        "cancelado": 0,
        "superado": 0,
        "outro": 0,
    }

    linhas = [
        "LEX MACHINA",
        "RELATÓRIO DE JURISPRUDÊNCIA",
        "=" * 70,
        "",
        (
            "GERADO EM: "
            + datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )
        ),
        "",
    ]

    for registro in registros:
        texto_oficial = str(
            registro.get(
                "texto_oficial_verificado",
                "",
            )
        ).strip()

        if texto_oficial:
            oficiais += 1
            estado = (
                "OFICIAL VERIFICADO"
            )
        else:
            nao_verificados += 1
            estado = (
                "SEM TESE OFICIAL VERIFICADA"
            )

        status = str(
            registro.get(
                "status",
                "",
            )
        ).strip().lower()

        if status in contagem_status:
            contagem_status[
                status
            ] += 1
        else:
            contagem_status[
                "outro"
            ] += 1

        linhas.append(
            (
                f"{registro['tribunal']} "
                f"{registro['tipo']} "
                f"{registro['numero']} "
                f"| STATUS: {status or 'não informado'} "
                f"| {estado}"
            )
        )

    linhas.extend(
        [
            "",
            "=" * 70,
            f"TOTAL: {total}",
            (
                "COM TEXTO OFICIAL VERIFICADO: "
                f"{oficiais}"
            ),
            (
                "SEM TESE OFICIAL VERIFICADA: "
                f"{nao_verificados}"
            ),
            "",
            "STATUS INTERNOS:",
            (
                "JULGADOS: "
                f"{contagem_status['julgado']}"
            ),
            (
                "PENDENTES: "
                f"{contagem_status['pendente']}"
            ),
            (
                "SOBRESTADOS: "
                f"{contagem_status['sobrestado']}"
            ),
            (
                "CANCELADOS: "
                f"{contagem_status['cancelado']}"
            ),
            (
                "SUPERADOS: "
                f"{contagem_status['superado']}"
            ),
            (
                "OUTROS: "
                f"{contagem_status['outro']}"
            ),
            "",
        ]
    )

    caminho.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )

    return caminho


# ============================================================
# PROCESSAR NORMA
# ============================================================


def processar_norma(
    registro
):
    print(
        f"Baixando norma: "
        f"{registro['nome']}"
    )

    pagina = baixar_pagina(
        registro["url"]
    )

    texto, codificacao = (
        extrair_texto(
            pagina
        )
    )

    pasta = (
        PASTA_SAIDA
        / registro[
            "pasta_destino"
        ]
    )

    caminho_existente = (
        pasta
        / registro[
            "arquivo"
        ]
    )

    texto_local = None

    if caminho_existente.exists():
        texto_local = (
            _ler_texto_local_seguro(
                caminho_existente
            )
        )

    problemas = (
        _validar_candidato_generico(
            texto,
            texto_atual=(
                texto_local
            ),
        )
    )

    if problemas:
        raise RuntimeError(
            (
                "ATUALIZAÇÃO CONSUMERISTA "
                "BLOQUEADA POR INTEGRIDADE: "
                + " | ".join(
                    problemas
                )
            )
        )

    if texto_local is not None:
        corpo_local = corpo_arquivo_lex(
            texto_local
        )

        corpo_novo = normalizar_texto(
            texto
        )

        if (
            corpo_local
            == corpo_novo
        ):
            print(
                (
                    "OK: arquivo já está atualizado "
                    "e passou na validação de integridade."
                )
            )

            return (
                caminho_existente,
                [],
            )

    caminho = salvar_norma(
        registro,
        texto,
        codificacao,
    )

    print(
        f"OK: {caminho}"
    )

    return (
        caminho,
        [],
    )


def gerar_relatorio(
    resultados,
    normas_processadas,
    referencias_processadas,
    jurisprudencias_processadas,
    erros,
    alertas,
):
    caminho = (
        PASTA_SAIDA
        / "RELATORIO_ATUALIZACAO.txt"
    )

    data = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    linhas = [
        "LEX MACHINA - RELATÓRIO DE ATUALIZAÇÃO",
        "========================================",
        "",
        f"DATA: {data}",
        "",
        (
            "NORMAS PROCESSADAS: "
            f"{normas_processadas}"
        ),
        (
            "REFERÊNCIAS CRUZADAS: "
            f"{referencias_processadas}"
        ),
        (
            "JURISPRUDÊNCIAS: "
            f"{jurisprudencias_processadas}"
        ),
        f"ERROS: {erros}",
        f"ALERTAS: {alertas}",
        "",
        "RESULTADOS:",
        "----------------------------------------",
    ]

    linhas.extend(
        resultados
    )

    caminho.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )

    return caminho


# ============================================================
# MAIN
# ============================================================

def main():
    args = argumentos_main()

    configurar_destino(
        args.destino
    )

    print()
    print(
        "LEX MACHINA UPDATER UNIFICADO"
    )
    print(
        "============================"
    )
    print()

    print(
        f"Raiz do Vade Mecum: "
        f"{RAIZ_VADEMECUM}"
    )

    print(
        f"Módulo consumidor: "
        f"{PASTA_SAIDA}"
    )

    print()

    # --------------------------------------------------------
    # CATÁLOGO MESTRE
    # --------------------------------------------------------

    catalogo_mestre = {
        "versao": "",
    }

    itens_mestre = []

    resultado_mestre = {
        "total": 0,
        "presentes": 0,
        "baixados": 0,
        "atualizados": 0,
        "erros": 0,
        "alertas": 0,
        "bloqueados": 0,
        "simulados": 0,
        "resultados": [],
    }

    if not args.sem_mestre:
        catalogo_mestre, itens_mestre = (
            carregar_catalogo_mestre()
        )

        validar_catalogo_mestre(
            itens_mestre
        )

        RAIZ_VADEMECUM.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            "CATÁLOGO MESTRE"
        )
        print(
            "-" * 70
        )

        print(
            f"Versão: "
            f"{catalogo_mestre.get('versao', '')}"
        )

        print(
            f"Itens: {len(itens_mestre)}"
        )

        print(
            "Verificação online: "
            + (
                "SIMULAÇÃO SEGURA"
                if args.simular_mestre
                else (
                    "SIM - ATUALIZAÇÃO SEGURA"
                    if args.atualizar_mestre
                    else "NÃO"
                )
            )
        )

        print()

        resultado_mestre = (
            processar_catalogo_mestre(
                itens_mestre,
                atualizar=(
                    args.atualizar_mestre
                    or args.simular_mestre
                ),
                simular=(
                    args.simular_mestre
                ),
            )
        )

        print()
        print(
            "Resumo do Catálogo Mestre:"
        )

        print(
            "  Presentes/atuais: "
            f"{resultado_mestre['presentes']}"
        )

        print(
            "  Baixados: "
            f"{resultado_mestre['baixados']}"
        )

        print(
            "  Atualizados: "
            f"{resultado_mestre['atualizados']}"
        )

        print(
            "  Erros: "
            f"{resultado_mestre['erros']}"
        )

        print(
            "  Alertas: "
            f"{resultado_mestre['alertas']}"
        )

        print(
            "  Bloqueados por integridade: "
            f"{resultado_mestre.get('bloqueados', 0)}"
        )

        print(
            "  Simulados sem gravação: "
            f"{resultado_mestre.get('simulados', 0)}"
        )

        print()

    if args.somente_mestre:
        relatorio_unificado = (
            gerar_relatorio_unificado(
                catalogo_mestre.get(
                    "versao",
                    "",
                ),
                resultado_mestre,
                0,
                0,
                0,
                0,
                0,
            )
        )

        print(
            "=" * 70
        )

        print(
            "PROCESSAMENTO FINALIZADO"
        )

        print(
            f"Relatório: "
            f"{relatorio_unificado}"
        )

        return

    # --------------------------------------------------------
    # CATÁLOGOS DO MÓDULO CONSUMIDOR
    # --------------------------------------------------------

    registros_normas = carregar_json(
        ARQUIVO_CATALOGO_NORMAS
    )

    registros_juris = carregar_json(
        ARQUIVO_CATALOGO_JURISPRUDENCIA
    )

    # Acórdãos e precedentes são catálogos opcionais e separados.
    # Se ainda não houver itens, os arquivos permanecem como listas vazias.
    registros_acordaos = (
        carregar_json(ARQUIVO_CATALOGO_ACORDAOS)
        if ARQUIVO_CATALOGO_ACORDAOS.exists()
        else []
    )
    # Atualiza primeiro a fatia oficial de Repercussão Geral do STF.
    # Em caso de indisponibilidade do portal ou mudança de layout, o
    # importador preserva integralmente o catálogo local anterior.
    if not args.sem_stf:
        print("STF - REPERCUSSÃO GERAL")
        print("-" * 70)
        resultado_stf = atualizar_catalogo_precedentes(
            ARQUIVO_CATALOGO_PRECEDENTES,
            verbose=True,
        )
        if resultado_stf.get("ok"):
            print(
                "STF RG: "
                f"{resultado_stf.get('importados', 0)} precedentes consumeristas; "
                f"{resultado_stf.get('com_relacao_cdc', 0)} com artigo do CDC explícito."
            )
        print()

    if not args.sem_stf and not args.sem_stf_controle:
        print("STF - CONTROLE CONCENTRADO (ADI, ADC, ADPF, ADO)")
        print("-" * 70)
        resultado_controle = atualizar_controle_concentrado(
            ARQUIVO_CATALOGO_PRECEDENTES,
            verbose=True,
            outros_registros=registros_juris + registros_acordaos,
        )
        PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
        (PASTA_SAIDA / "relatorio_stf_controle_concentrado.json").write_text(
            json.dumps(resultado_controle, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print()

    if not args.sem_stf:
        print("STF - SÚMULAS VINCULANTES")
        print("-" * 70)
        resultado_sv = atualizar_sumulas_vinculantes(
            ARQUIVO_CATALOGO_PRECEDENTES,
            verbose=True,
            outros_registros=registros_juris + registros_acordaos,
        )
        PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
        (PASTA_SAIDA / "relatorio_stf_sumulas_vinculantes.json").write_text(
            json.dumps(resultado_sv, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print()

    registros_precedentes = (
        carregar_json(ARQUIVO_CATALOGO_PRECEDENTES)
        if ARQUIVO_CATALOGO_PRECEDENTES.exists()
        else []
    )

    validar_catalogo_normas(
        registros_normas
    )

    validar_catalogo_jurisprudencia(
        registros_juris
    )
    validar_catalogo_jurisprudencia(
        registros_acordaos
    )
    validar_catalogo_jurisprudencia(
        registros_precedentes
    )

    # Uma lista única alimenta o processamento e os índices, mantendo
    # os catálogos físicos separados para facilitar auditoria e importação.
    registros_juris_todos = (
        registros_juris
        + registros_acordaos
        + registros_precedentes
    )

    PASTA_SAIDA.mkdir(
        parents=True,
        exist_ok=True,
    )

    normas_processadas = 0
    referencias_processadas = 0
    jurisprudencias_processadas = 0

    erros = 0
    alertas = 0

    resultados = []

    total_normas = len(
        registros_normas
    )

    print(
        "MÓDULO CONSUMIDOR"
    )
    print(
        "-" * 70
    )

    print(
        f"Registros legislativos: "
        f"{total_normas}"
    )

    print(
        "Registros jurisprudenciais: "
        f"{len(registros_juris_todos)} "
        f"(base={len(registros_juris)}, "
        f"acórdãos={len(registros_acordaos)}, "
        f"precedentes={len(registros_precedentes)})"
    )

    print()

    # --------------------------------------------------------
    # LEGISLAÇÃO + REFERÊNCIAS
    # --------------------------------------------------------

    for indice, registro in enumerate(
        registros_normas,
        start=1,
    ):
        tipo_registro = registro.get(
            "tipo_registro",
            "norma",
        )

        print(
            f"[LEG {indice}/{total_normas}]"
        )

        try:
            if (
                tipo_registro
                == "referencia"
            ):
                print(
                    f"Criando referência: "
                    f"{registro['nome']}"
                )

                caminho = salvar_referencia(
                    registro
                )

                referencias_processadas += 1

                resultados.append(
                    (
                        "✓ REFERÊNCIA: "
                        f"{registro['nome']}"
                    )
                )

                print(
                    f"OK: {caminho}"
                )

            else:
                _, problemas = (
                    processar_norma(
                        registro
                    )
                )

                normas_processadas += 1

                if problemas:
                    alertas += 1

                    resultados.append(
                        (
                            "! NORMA COM ALERTA: "
                            f"{registro['nome']}"
                        )
                    )

                else:
                    resultados.append(
                        (
                            "✓ NORMA: "
                            f"{registro['nome']}"
                        )
                    )

        except (
            requests.RequestException,
            OSError,
            RuntimeError,
            ValueError,
        ) as erro:
            erros += 1

            resultados.append(
                (
                    "✗ ERRO: "
                    f"{registro.get('nome', 'registro')} "
                    f"- {erro}"
                )
            )

            print(
                f"ERRO: {erro}"
            )

        print()

    # --------------------------------------------------------
    # JURISPRUDÊNCIA
    # --------------------------------------------------------

    total_juris = len(
        registros_juris_todos
    )

    for indice, registro in enumerate(
        registros_juris_todos,
        start=1,
    ):
        print(
            f"[JURIS {indice}/{total_juris}]"
        )

        try:
            oficial = bool(
                str(
                    registro.get(
                        "texto_oficial_verificado",
                        "",
                    )
                ).strip()
            )

            origem = (
                "OFICIAL"
                if oficial
                else "CATÁLOGO"
            )

            print(
                (
                    "Criando jurisprudência: "
                    f"{registro['tribunal']} "
                    f"{registro['tipo']} "
                    f"{registro['numero']} "
                    f"[{origem}]"
                )
            )

            caminho = (
                salvar_jurisprudencia(
                    registro
                )
            )

            jurisprudencias_processadas += 1

            resultados.append(
                (
                    "✓ JURISPRUDÊNCIA: "
                    f"{registro['tribunal']} "
                    f"{registro['tipo']} "
                    f"{registro['numero']} "
                    f"[{origem}]"
                )
            )

            print(
                f"OK: {caminho}"
            )

        except (
            OSError,
            RuntimeError,
            ValueError,
        ) as erro:
            erros += 1

            resultados.append(
                (
                    "✗ ERRO JURISPRUDÊNCIA: "
                    f"{registro.get('numero', '?')} "
                    f"- {erro}"
                )
            )

            print(
                f"ERRO: {erro}"
            )

        print()

    # --------------------------------------------------------
    # ÍNDICES DO MÓDULO CONSUMIDOR
    # --------------------------------------------------------

    try:
        indice_juris = (
            gerar_indice_jurisprudencia(
                registros_juris_todos
            )
        )

        print(
            "Índice de jurisprudência: "
            f"{indice_juris}"
        )

    except OSError as erro:
        erros += 1

        print(
            "ERRO ao gerar índice "
            f"de jurisprudência: {erro}"
        )

    try:
        indice_artigos = (
            gerar_indice_artigos(
                registros_juris_todos
            )
        )

        print(
            "Índice por artigo: "
            f"{indice_artigos}"
        )

        indice_acordaos = gerar_indice_relacoes_especializado(
            registros_juris_todos,
            "acordaos",
        )
        indice_precedentes = gerar_indice_relacoes_especializado(
            registros_juris_todos,
            "precedentes",
        )
        indice_sumulas_vinculantes = gerar_indice_sumulas_vinculantes(
            registros_juris_todos
        )
        manifesto_camadas = gerar_manifesto_camadas_juridicas(
            registros_juris_todos
        )
        print(f"Índice de acórdãos: {indice_acordaos}")
        print(f"Índice de precedentes: {indice_precedentes}")
        print(f"Índice de Súmulas Vinculantes: {indice_sumulas_vinculantes}")
        print(f"Manifesto das camadas: {manifesto_camadas}")

    except OSError as erro:
        erros += 1

        print(
            "ERRO ao gerar índice "
            f"por artigo: {erro}"
        )

    try:
        relatorio_juris = (
            gerar_relatorio_jurisprudencia(
                registros_juris
            )
        )

        print(
            "Relatório jurisprudencial: "
            f"{relatorio_juris}"
        )

    except OSError as erro:
        erros += 1

        print(
            "ERRO ao gerar relatório "
            f"jurisprudencial: {erro}"
        )

    relatorio_consumidor = gerar_relatorio(
        resultados,
        normas_processadas,
        referencias_processadas,
        jurisprudencias_processadas,
        erros,
        alertas,
    )

    # --------------------------------------------------------
    # ÍNDICE E RELATÓRIO UNIFICADOS
    # --------------------------------------------------------

    try:
        indice_unificado = (
            gerar_indice_mestre_unificado(
                itens_mestre,
                registros_normas,
                registros_juris,
            )
        )

    except OSError as erro:
        erros += 1
        indice_unificado = ""

        print(
            "ERRO ao gerar índice mestre "
            f"unificado: {erro}"
        )

    relatorio_unificado = (
        gerar_relatorio_unificado(
            catalogo_mestre.get(
                "versao",
                "",
            ),
            resultado_mestre,
            normas_processadas,
            referencias_processadas,
            jurisprudencias_processadas,
            erros,
            alertas,
        )
    )

    # --------------------------------------------------------
    # RESUMO FINAL
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "PROCESSAMENTO FINALIZADO"
    )

    if not args.sem_mestre:
        print(
            "Catálogo Mestre: "
            f"{resultado_mestre['total']} itens"
        )

        print(
            "  Presentes/atuais: "
            f"{resultado_mestre['presentes']}"
        )

        print(
            "  Baixados: "
            f"{resultado_mestre['baixados']}"
        )

        print(
            "  Atualizados: "
            f"{resultado_mestre['atualizados']}"
        )

    print(
        "Normas consumeristas processadas: "
        f"{normas_processadas}"
    )

    print(
        "Referências cruzadas: "
        f"{referencias_processadas}"
    )

    print(
        "Jurisprudências: "
        f"{jurisprudencias_processadas}"
    )

    erros_totais = (
        erros
        + resultado_mestre[
            "erros"
        ]
    )

    alertas_totais = (
        alertas
        + resultado_mestre[
            "alertas"
        ]
    )

    print(
        f"Erros totais: {erros_totais}"
    )

    print(
        f"Alertas totais: {alertas_totais}"
    )

    print()

    print(
        "Relatório consumidor: "
        f"{relatorio_consumidor}"
    )

    if indice_unificado:
        print(
            "Índice mestre unificado: "
            f"{indice_unificado}"
        )

    print(
        "Relatório unificado: "
        f"{relatorio_unificado}"
    )


if __name__ == "__main__":
    main()
