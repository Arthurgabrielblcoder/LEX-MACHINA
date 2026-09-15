from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import json
import math
import re
import sys
import unicodedata


# ============================================================
# LEX MACHINA
# GERADOR DE ÍNDICES ESP32 V5 - MODO TESTE SEGURO
#
# OBJETIVO
# -------
# Gerar índices de acesso direto por byte para o ESP32-S3,
# SEM alterar nenhum arquivo jurídico do cartão e SEM
# sobrescrever os índices antigos.
#
# Saída:
#   D:\99_INDICES_ESP32_V5_TESTE\
#
# Arquivos:
#   NORMAS.IDX
#   ARTIGOS.IDX
#   JURIS.IDX
#   MENU.IDX
#   META.JSON
#   RELATORIO_INDICE_ESP32_V5.txt
#   AMOSTRAS_OFFSETS_V5.txt
#
# MELHORIAS SOBRE AS VERSÕES ANTERIORES
# -------------------------------------
# 1) parser Unicode por LINHAS DECODIFICADAS, preservando
#    offsets exatos em bytes;
#
# 2) reconhece espaços especiais, BOM, caracteres invisíveis
#    e cabeçalhos quebrados em duas linhas:
#
#       Art.
#       1º Esta Lei...
#
#    Esse formato ocorria em CF88 e Maria da Penha;
#
# 3) aceita artigos com milhares:
#       Art. 1.001  -> artigo 1001
#       Art. 2.046  -> artigo 2046
#
# 4) aceita artigos com letras:
#       Art. 11-A
#       Art. 190-F
#       Art. 227-C
#
# 5) NÃO confunde mais:
#       Art. 361 - Este Decreto...
#    com um inexistente "Art. 361-ESTE";
#
# 6) abandona a programação dinâmica da V4.
#    A V4 descartava artigos válidos em normas como CTN,
#    Licitações, Custeio e Liquidação Financeira;
#
# 7) quando o mesmo artigo aparece várias vezes, escolhe a
#    ocorrência com maior probabilidade de ser o cabeçalho
#    jurídico real e, em empate, a ocorrência mais recente;
#
# 8) CF, Código Civil e ECA continuam com testes estruturais
#    obrigatórios;
#
# 9) adiciona guardas contra regressão para normas que a V4
#    subindexou de forma evidente;
#
# 10) cada offset é reaberto no arquivo bruto e revalidado;
#
# 11) os índices são gravados em pasta V5 de TESTE.
# ============================================================# ============================================================


CATALOGO_MESTRE = Path(
    "catalogo_mestre_vademecum.json"
)

CATALOGO_JURIS = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_INDICES_NOME = (
    "99_INDICES_ESP32_V5_TESTE"
)

ARQ_NORMAS = "NORMAS.IDX"
ARQ_ARTIGOS = "ARTIGOS.IDX"
ARQ_JURIS = "JURIS.IDX"
ARQ_MENU = "MENU.IDX"
ARQ_META = "META.JSON"

ARQ_RELATORIO = (
    "RELATORIO_INDICE_ESP32_V5.txt"
)

ARQ_AMOSTRAS = (
    "AMOSTRAS_OFFSETS_V5.txt"
)


# ============================================================
# CAMINHOS CANÔNICOS DOS 20 ITENS BASE
# ============================================================

BASE_ALIASES = {
    "CF88": [
        "1- CONSTITUIÇÃO FEDERAL/cf.txt",
    ],
    "CC2002": [
        (
            "2- CÓDIGO CIVIL/"
            "codigo_civil_ lei10.406 2002.txt"
        ),
        (
            "2- CÓDIGO CIVIL/"
            "codigo_civil_2002.txt"
        ),
    ],
    "CPC2015": [
        (
            "3-CÓDIGO PROCESSO CIVIL/"
            "codigo_processo_civil.txt"
        ),
    ],
    "CP1940": [
        "4-CÓDIGO PENAL/codigo_penal.txt",
    ],
    "CPP1941": [
        (
            "5-CÓDIGO PROCESSO PENAL/"
            "Código_de_Processo_Penal.txt"
        ),
        (
            "5-CÓDIGO PROCESSO PENAL/"
            "codigo_processo_penal.txt"
        ),
    ],
    "CTN1966": [
        (
            "6-CÓDIGO TRIBUTARIO NACIONAL/"
            "Código Tributário Nacional.txt"
        ),
    ],
    "CE1965": [
        (
            "7-CÓDIGO ELEITORAL/"
            "Código Eleitoral.txt"
        ),
    ],
    "CLT1943": [
        (
            "8-CLT CONSOLIDAÇÃO DAS LEIS DO TRABALHO/"
            "CLT.txt"
        ),
    ],
    "CDC1990": [
        (
            "9-CÓDIGO DE DEFESA DO CONSUMIDOR/"
            "01_CDC/cdc_lei_8078_1990.txt"
        ),
    ],
    "ECA1990": [
        (
            "10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE/"
            "Estatuto da Criança e do Adolescente "
            "(Lei nº 8.069 1990).txt"
        ),
    ],
    "IDOSO2003": [
        (
            "11- ESTATUTO DA PESSOA IDOSA/"
            "Estatuto da pessoa idosa.txt"
        ),
    ],
    "LBI2015": [
        (
            "12-LEI BRASILEIRA DE INCLUSÃO "
            "DA PESSOA COM DEFICIÊNCIA/"
            "Lei Brasileira de Inclusão "
            "da Pessoa com Deficiência.txt"
        ),
    ],
    "LEP1984": [
        (
            "13- LEI DA EXECUÇÃO PENAL/"
            "Lei de Execução Penal.txt"
        ),
    ],
    "DROGAS2006": [
        (
            "14- LEI DE DROGAS/"
            "Lei de Drogas.txt"
        ),
    ],
    "MARIA2006": [
        (
            "15-LEI MARIA DA PENHA/"
            "Lei Maria da Penha.txt"
        ),
    ],
    "HEDIONDOS1990": [
        (
            "16- LEI DE CRIMES HEDIONDOS/"
            "Lei de Crimes Hediondos.txt"
        ),
    ],
    "LIC2021": [
        (
            "17- LEI DE LICITAÇÕES E CONTRATOS/"
            "Lei de Licitações e Contratos "
            "Administrativos.txt"
        ),
    ],
    "MCI2014": [
        (
            "18- MARCO CIVIL DA INTERNET/"
            "Marco Civil da Internet.txt"
        ),
    ],
    "LGPD2018": [
        (
            "19-LGPD LEI GERAL DA PROTEÇÃO DE DADOS/"
            "LGPD Lei Geral da Proteção de Dados.txt"
        ),
    ],
    "LAI2011": [
        (
            "20- LEI DE ACESSO A INFORMAÇÃO/"
            "Lei de Acesso a Informação.txt"
        ),
    ],
}


# ============================================================
# TESTES ESTRUTURAIS FORTES DAS 3 NORMAS RECUPERADAS
# ============================================================

VALIDACOES_ESPECIAIS = {
    "CF88": {
        "min_artigos": 270,
        "artigo_final": "250",
        "ancoras": [
            "1",
            "5",
            "18",
            "31",
            "37",
            "60",
            "75",
            "93",
            "102",
            "127",
            "134",
            "144",
            "150",
            "170",
            "194",
            "196",
            "205",
            "225",
            "226",
            "227",
            "230",
            "250",
        ],
    },
    "CC2002": {
        "min_artigos": 2050,
        "artigo_final": "2046",
        "ancoras": [
            "1",
            "40",
            "44",
            "104",
            "186",
            "233",
            "404",
            "406",
            "421",
            "927",
            "966",
            "1045",
            "1225",
            "1421",
            "1511",
            "1784",
            "1829",
            "2002",
            "2046",
        ],
    },
    "ECA1990": {
        "min_artigos": 320,
        "artigo_final": "267",
        "ancoras": [
            "1",
            "7",
            "11-A",
            "53",
            "70",
            "101",
            "112",
            "131",
            "136",
            "149",
            "171",
            "190-F",
            "201",
            "208",
            "227-C",
            "240",
            "241-E",
            "267",
        ],
    },
}


# ============================================================
# AMOSTRAS QUE SERÃO LIDAS DE VOLTA PELOS OFFSETS
# ============================================================

AMOSTRAS_OBRIGATORIAS = {
    "CF88": [
        "1",
        "5",
        "37",
        "60",
        "250",
    ],
    "CC2002": [
        "1",
        "421",
        "927",
        "1784",
        "2046",
    ],
    "CTN1966": [
        "1",
        "5",
        "100",
        "218",
    ],
    "LEP1984": [
        "1",
        "1-A",
        "9-A",
        "204",
    ],
    "CDC1990": [
        "1",
        "6",
        "14",
        "39",
        "51",
        "119",
    ],
    "ECA1990": [
        "1",
        "53",
        "101",
        "190-F",
        "227-C",
        "240",
        "267",
    ],
    "MARIA2006": [
        "1",
        "7",
        "10-A",
        "12-C",
        "46",
    ],
    "LIC2021": [
        "1",
        "50",
        "100",
        "150",
        "194",
    ],
    "CUSTEIO1991": [
        "1",
        "20",
        "55",
        "105",
    ],
    "LIQFIN1974": [
        "1",
        "19",
        "36",
        "57",
    ],
}


# ============================================================
# ARGUMENTOS
# ============================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - Gerador de índices ESP32 V4 "
            "em pasta de teste"
        )
    )

    parser.add_argument(
        "origem",
        help=(
            "Raiz do cartão microSD. "
            "Exemplo: D:\\"
        ),
    )

    return parser.parse_args()


# ============================================================
# UTILITÁRIOS
# ============================================================

def agora():
    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def remover_acentos(texto):
    texto = unicodedata.normalize(
        "NFKD",
        str(texto or ""),
    )

    return "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(
            caractere
        )
    )


def normalizar(texto):
    texto = remover_acentos(
        texto
    ).casefold()

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


def limpar_campo(texto):
    texto = str(
        texto or ""
    )

    texto = texto.replace(
        "|",
        "/",
    )

    texto = texto.replace(
        "\r",
        " ",
    )

    texto = texto.replace(
        "\n",
        " ",
    )

    return re.sub(
        r"\s+",
        " ",
        texto,
    ).strip()


def caminho_esp32(
    caminho,
    origem,
):
    relativo = caminho.relative_to(
        origem
    )

    return (
        "/"
        + "/".join(
            relativo.parts
        )
    )


def tamanho_arquivo(
    caminho
):
    return caminho.stat().st_size


# ============================================================
# JSON
# ============================================================

def carregar_json(
    caminho
):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    return json.loads(
        caminho.read_text(
            encoding="utf-8"
        )
    )


def carregar_catalogo_mestre():
    dados = carregar_json(
        CATALOGO_MESTRE
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
            "O campo 'itens' precisa ser uma lista."
        )

    return dados, itens


def carregar_catalogo_juris():
    dados = carregar_json(
        CATALOGO_JURIS
    )

    if not isinstance(
        dados,
        list,
    ):
        raise ValueError(
            "catalogo_jurisprudencia.json "
            "precisa conter uma lista."
        )

    return dados


# ============================================================
# LOCALIZAÇÃO DAS NORMAS
# ============================================================

def localizar_norma(
    item,
    origem,
):
    identificador = str(
        item.get(
            "id",
            ""
        )
    ).strip()

    prioridade = str(
        item.get(
            "prioridade",
            ""
        )
    ).strip().upper()

    if prioridade == "BASE":
        for relativo in BASE_ALIASES.get(
            identificador,
            [],
        ):
            caminho = (
                origem
                / Path(
                    relativo
                )
            )

            if caminho.is_file():
                return caminho

    pasta = str(
        item.get(
            "pasta_destino",
            ""
        )
    ).strip()

    arquivo = str(
        item.get(
            "arquivo_sugerido",
            ""
        )
    ).strip()

    if (
        pasta
        and arquivo
    ):
        caminho = (
            origem
            / pasta
            / arquivo
        )

        if caminho.is_file():
            return caminho

    return None


# ============================================================
# SIGLAS
# ============================================================

SIGLAS_FIXAS = {
    "CF88": "CF",
    "CC2002": "CC",
    "CPC2015": "CPC",
    "CP1940": "CP",
    "CPP1941": "CPP",
    "CTN1966": "CTN",
    "CE1965": "CE",
    "CLT1943": "CLT",
    "CDC1990": "CDC",
    "ECA1990": "ECA",
    "IDOSO2003": "IDOSO",
    "LBI2015": "LBI",
    "LEP1984": "LEP",
    "DROGAS2006": "DROGAS",
    "MARIA2006": "LMP",
    "HEDIONDOS1990": "HED",
    "LIC2021": "LIC",
    "MCI2014": "MCI",
    "LGPD2018": "LGPD",
    "LAI2011": "LAI",
}


def gerar_sigla(
    item
):
    identificador = str(
        item.get(
            "id",
            ""
        )
    ).strip()

    if identificador in SIGLAS_FIXAS:
        return SIGLAS_FIXAS[
            identificador
        ]

    nome = remover_acentos(
        item.get(
            "nome",
            "",
        )
    ).upper()

    palavras = re.findall(
        r"[A-Z]+",
        nome,
    )

    ignoradas = {
        "LEI",
        "DECRETO",
        "COMPLEMENTAR",
        "DA",
        "DE",
        "DO",
        "DAS",
        "DOS",
        "E",
        "A",
        "O",
        "PARA",
    }

    filtradas = [
        palavra
        for palavra in palavras
        if (
            palavra not in ignoradas
            and len(
                palavra
            ) > 1
        )
    ]

    sigla = "".join(
        palavra[
            0
        ]
        for palavra in filtradas[
            :4
        ]
    )

    return (
        sigla[
            :8
        ]
        or identificador[
            :8
        ].upper()
    )


# ============================================================
# PARSER DE CABEÇALHOS DE ARTIGO V5
#
# A V4 operava diretamente com regex em bytes e aceitava
# somente espaço ASCII / tabulação. Isso falhava quando o
# arquivo trazia NBSP, BOM, caracteres invisíveis ou quando
# "Art." e o número estavam em linhas separadas.
#
# A V5:
#   - detecta a codificação;
#   - percorre linha por linha mantendo o offset bruto;
#   - faz a regex no texto Unicode;
#   - converte a posição do "Art." de volta para bytes.
# ============================================================


PREFIXO_INVISIVEL = (
    "\u00a0"
    "\u1680"
    "\u2000"
    "\u2001"
    "\u2002"
    "\u2003"
    "\u2004"
    "\u2005"
    "\u2006"
    "\u2007"
    "\u2008"
    "\u2009"
    "\u200a"
    "\u200b"
    "\u200c"
    "\u200d"
    "\u200e"
    "\u200f"
    "\u202f"
    "\u205f"
    "\u2060"
    "\u3000"
    "\ufeff"
)


PADRAO_ARTIGO_DIRETO = re.compile(
    r"^[\s"
    + re.escape(
        PREFIXO_INVISIVEL
    )
    + r"]*"
    r"(?P<art>Art(?:igo)?\.?)"
    r"\s*"
    r"(?P<num>"
        r"\d{1,3}(?:\.\d{3})+"
        r"|"
        r"\d{1,4}"
    r")"
    r"\s*"
    r"(?P<ord>º|°|o)?"
    # Sufixo só é aceito quando o hífen está COLADO
    # ao número/ordinal. Assim:
    #   Art. 10-A  -> 10-A
    #   Art. 361 - Este... -> 361
    r"(?P<suf>-[A-Za-z]{1,2})?"
    r"(?=$|[\s\.,;:\)\]\-–—])",
    re.IGNORECASE,
)


PADRAO_ART_SOZINHO = re.compile(
    r"^[\s"
    + re.escape(
        PREFIXO_INVISIVEL
    )
    + r"]*"
    r"(?P<art>Art(?:igo)?\.?)"
    r"[\s"
    + re.escape(
        PREFIXO_INVISIVEL
    )
    + r"]*$",
    re.IGNORECASE,
)


PADRAO_CONTINUACAO_NUMERO = re.compile(
    r"^[\s"
    + re.escape(
        PREFIXO_INVISIVEL
    )
    + r"]*"
    r"(?P<num>"
        r"\d{1,3}(?:\.\d{3})+"
        r"|"
        r"\d{1,4}"
    r")"
    r"\s*"
    r"(?P<ord>º|°|o)?"
    r"(?P<suf>-[A-Za-z]{1,2})?"
    r"(?=$|[\s\.,;:\)\]\-–—])",
    re.IGNORECASE,
)


# Guardas conservadoras baseadas nas contagens já obtidas
# antes da regressão introduzida pela V4.
#
# Não tentam definir o número "jurídico perfeito" de artigos;
# servem somente para impedir regressões grosseiras, como:
#   LIC: 196 -> 27
#   CUSTEIO: 115 -> 35
#   LIQFIN: 57 -> 2
REGRESSION_GUARDS = {
    "CF88": 270,
    "CC2002": 2050,
    "CPC2015": 1000,
    "CP1940": 350,
    "CPP1941": 700,
    "CTN1966": 200,
    "CLT1943": 900,
    "ECA1990": 320,
    "LEP1984": 190,
    "MARIA2006": 50,
    "LIC2021": 180,
    "CUSTEIO1991": 100,
    "BENEF1991": 140,
    "RPEM1994": 60,
    "COND1964": 70,
    "EXECFISC1980": 38,
    "LIQFIN1974": 50,
    "RPS1999": 400,
}


# ============================================================
# ARTIGOS
# ============================================================

def valor_sufixo(
    sufixo
):
    if not sufixo:
        return 0

    valor = 0

    for caractere in sufixo.upper():
        if not (
            "A"
            <= caractere
            <= "Z"
        ):
            continue

        valor = (
            valor
            * 26
            + (
                ord(
                    caractere
                )
                - ord(
                    "A"
                )
                + 1
            )
        )

    return valor


def chave_artigo(
    numero,
    sufixo,
):
    return (
        int(
            numero
        ),
        valor_sufixo(
            sufixo
        ),
    )


def formatar_artigo(
    numero,
    sufixo,
):
    artigo = str(
        int(
            numero
        )
    )

    if sufixo:
        artigo += (
            "-"
            + sufixo.upper()
        )

    return artigo


def detectar_codificacao(
    dados
):
    for encoding in (
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            dados.decode(
                encoding,
                errors="strict",
            )

            return encoding

        except UnicodeDecodeError:
            continue

    return "utf-8"


def decodificar_trecho(
    dados,
    encoding=None,
):
    if encoding:
        try:
            return dados.decode(
                encoding,
                errors="strict",
            )

        except UnicodeDecodeError:
            pass

    for tentativa in (
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            return dados.decode(
                tentativa,
                errors="strict",
            )

        except UnicodeDecodeError:
            continue

    return dados.decode(
        "utf-8",
        errors="replace",
    )


def linhas_com_offsets(
    dados,
    encoding,
):
    linhas = []

    offset = 0

    for raw in dados.splitlines(
        keepends=True
    ):
        texto = raw.decode(
            encoding,
            errors="strict",
        )

        texto_sem_quebra = texto.rstrip(
            "\r\n"
        )

        linhas.append(
            {
                "offset": offset,
                "raw": raw,
                "texto": texto_sem_quebra,
            }
        )

        offset += len(
            raw
        )

    # Caso raríssimo de arquivo sem terminador final e splitlines
    # não ter coberto todos os bytes.
    if (
        offset
        < len(
            dados
        )
    ):
        raw = dados[
            offset:
        ]

        linhas.append(
            {
                "offset": offset,
                "raw": raw,
                "texto": raw.decode(
                    encoding,
                    errors="strict",
                ),
            }
        )

    return linhas


def sufixo_do_match(
    match
):
    bruto = (
        match.group(
            "suf"
        )
        or ""
    )

    return bruto.lstrip(
        "-"
    ).upper()


def numero_do_match(
    match
):
    bruto = match.group(
        "num"
    )

    return int(
        bruto.replace(
            ".",
            "",
        )
    )


def pontuar_contexto_artigo(
    resto,
    origem,
):
    """
    Diferencia cabeçalho real de referências que, por causa
    da diagramação HTML, eventualmente começam uma linha.
    """

    resto = str(
        resto or ""
    ).strip()

    resto_norm = normalizar(
        resto
    )

    pontos = 10.0

    if origem == "DIRETO":
        pontos += 1.0

    if len(
        resto
    ) >= 20:
        pontos += 2.0

    elif len(
        resto
    ) >= 5:
        pontos += 1.0

    # Referências típicas que podem ter sido quebradas para
    # o começo de uma linha durante a extração HTML.
    suspeitos = (
        "da lei n",
        "da lei complementar n",
        "do codigo civil",
        "do codigo penal",
        "do codigo de processo",
        "da constituicao federal",
        "do decreto n",
        "do decreto lei n",
        "da medida provisoria n",
        "desta lei n",
    )

    if any(
        resto_norm.startswith(
            termo
        )
        for termo in suspeitos
    ):
        pontos -= 15.0

    return pontos


def criar_candidato_direto(
    linha,
    match,
    encoding,
):
    numero = numero_do_match(
        match
    )

    if not (
        1
        <= numero
        <= 9999
    ):
        return None

    sufixo = sufixo_do_match(
        match
    )

    inicio_art_char = match.start(
        "art"
    )

    prefixo = linha[
        "texto"
    ][
        :inicio_art_char
    ]

    offset_artigo = (
        linha[
            "offset"
        ]
        + len(
            prefixo.encode(
                encoding
            )
        )
    )

    resto = linha[
        "texto"
    ][
        match.end():
    ].strip()

    return {
        "artigo": formatar_artigo(
            numero,
            sufixo,
        ),
        "numero": numero,
        "sufixo": sufixo,
        "sufixo_valor": (
            valor_sufixo(
                sufixo
            )
        ),
        "chave": chave_artigo(
            numero,
            sufixo,
        ),
        "offset": offset_artigo,
        "pontos_local": (
            pontuar_contexto_artigo(
                resto,
                "DIRETO",
            )
        ),
        "linha": linha[
            "texto"
        ][
            :500
        ],
        "origem": "DIRETO",
    }


def criar_candidato_quebrado(
    linhas,
    indice_art,
    indice_numero,
    match_art,
    match_numero,
    encoding,
):
    numero = numero_do_match(
        match_numero
    )

    if not (
        1
        <= numero
        <= 9999
    ):
        return None

    sufixo = sufixo_do_match(
        match_numero
    )

    linha_art = linhas[
        indice_art
    ]

    inicio_art_char = match_art.start(
        "art"
    )

    prefixo = linha_art[
        "texto"
    ][
        :inicio_art_char
    ]

    offset_artigo = (
        linha_art[
            "offset"
        ]
        + len(
            prefixo.encode(
                encoding
            )
        )
    )

    linha_numero = linhas[
        indice_numero
    ][
        "texto"
    ]

    resto = linha_numero[
        match_numero.end():
    ].strip()

    combinado = (
        linha_art[
            "texto"
        ].strip()
        + " "
        + linha_numero.strip()
    )

    return {
        "artigo": formatar_artigo(
            numero,
            sufixo,
        ),
        "numero": numero,
        "sufixo": sufixo,
        "sufixo_valor": (
            valor_sufixo(
                sufixo
            )
        ),
        "chave": chave_artigo(
            numero,
            sufixo,
        ),
        "offset": offset_artigo,
        "pontos_local": (
            pontuar_contexto_artigo(
                resto,
                "QUEBRADO",
            )
        ),
        "linha": combinado[
            :500
        ],
        "origem": "QUEBRADO",
    }


def listar_candidatos_artigo(
    dados
):
    encoding = detectar_codificacao(
        dados
    )

    linhas = linhas_com_offsets(
        dados,
        encoding,
    )

    candidatos = []

    total_linhas = len(
        linhas
    )

    for indice, linha in enumerate(
        linhas
    ):
        texto = linha[
            "texto"
        ]

        direto = PADRAO_ARTIGO_DIRETO.match(
            texto
        )

        if direto:
            candidato = criar_candidato_direto(
                linha,
                direto,
                encoding,
            )

            if candidato:
                candidatos.append(
                    candidato
                )

            continue

        art_sozinho = (
            PADRAO_ART_SOZINHO.match(
                texto
            )
        )

        if not art_sozinho:
            continue

        # Procura o número nas próximas 3 linhas não vazias.
        # Isso cobre HTMLs em que spans diferentes foram
        # transformados em quebras de linha.
        nao_vazias = 0

        limite = min(
            total_linhas,
            indice + 8,
        )

        for proximo in range(
            indice + 1,
            limite,
        ):
            texto_proximo = linhas[
                proximo
            ][
                "texto"
            ]

            if not texto_proximo.strip():
                continue

            nao_vazias += 1

            numero_match = (
                PADRAO_CONTINUACAO_NUMERO.match(
                    texto_proximo
                )
            )

            if numero_match:
                candidato = (
                    criar_candidato_quebrado(
                        linhas,
                        indice,
                        proximo,
                        art_sozinho,
                        numero_match,
                        encoding,
                    )
                )

                if candidato:
                    candidatos.append(
                        candidato
                    )

                break

            # Se a primeira ou segunda linha não vazia depois
            # de "Art." não começa por número, provavelmente
            # não é um cabeçalho dividido.
            if nao_vazias >= 2:
                break

    candidatos.sort(
        key=lambda item: item[
            "offset"
        ]
    )

    return (
        candidatos,
        encoding,
    )


# ============================================================
# SELEÇÃO V5
#
# A programação dinâmica da V4 foi removida.
#
# Como os candidatos já precisam começar uma linha (ou formar
# o padrão explícito "Art." + número na linha seguinte), o
# principal problema restante são DUPLICATAS históricas.
#
# Para cada chave de artigo:
#   - escolhemos a maior pontuação local;
#   - em empate, escolhemos a ocorrência mais tardia.
#
# Isso tende a preferir a redação consolidada mais recente.
# ============================================================

def selecionar_candidatos_unicos(
    candidatos
):
    grupos = {}

    for candidato in candidatos:
        grupos.setdefault(
            candidato[
                "artigo"
            ],
            [],
        ).append(
            candidato
        )

    selecionados = []

    for artigo, grupo in (
        grupos.items()
    ):
        melhor = max(
            grupo,
            key=lambda item: (
                item[
                    "pontos_local"
                ],
                item[
                    "offset"
                ],
            ),
        )

        selecionados.append(
            melhor
        )

    selecionados.sort(
        key=lambda item: item[
            "offset"
        ]
    )

    return selecionados


def cortar_no_artigo_final(
    identificador,
    selecionados,
):
    config = VALIDACOES_ESPECIAIS.get(
        identificador
    )

    if not config:
        return selecionados

    final = config[
        "artigo_final"
    ]

    finais = [
        item
        for item in selecionados
        if item[
            "artigo"
        ] == final
    ]

    if not finais:
        return selecionados

    # Como já deduplicamos, deverá existir apenas um.
    offset_final = finais[
        -1
    ][
        "offset"
    ]

    return [
        item
        for item in selecionados
        if item[
            "offset"
        ]
        <= offset_final
    ]


# ============================================================
# OFFSETS / TAMANHOS
# ============================================================

def proximo_offset_candidato(
    candidatos,
    offset_atual,
):
    for candidato in candidatos:
        if (
            candidato[
                "offset"
            ]
            > offset_atual
        ):
            return candidato[
                "offset"
            ]

    return None


def montar_artigos(
    dados,
    selecionados,
    candidatos,
):
    artigos = []

    candidatos_ordenados = sorted(
        candidatos,
        key=lambda item: item[
            "offset"
        ],
    )

    for item in selecionados:
        inicio = item[
            "offset"
        ]

        # O tamanho termina no PRÓXIMO cabeçalho candidato,
        # mesmo que ele seja uma redação histórica não escolhida.
        # Assim um artigo nunca "engole" outro cabeçalho.
        proximo = proximo_offset_candidato(
            candidatos_ordenados,
            inicio,
        )

        fim = (
            proximo
            if proximo is not None
            else len(
                dados
            )
        )

        artigos.append(
            {
                "artigo": item[
                    "artigo"
                ],
                "numero": item[
                    "numero"
                ],
                "sufixo": item[
                    "sufixo"
                ],
                "offset": inicio,
                "tamanho": max(
                    0,
                    fim
                    - inicio,
                ),
                "linha": item[
                    "linha"
                ],
                "origem": item[
                    "origem"
                ],
            }
        )

    return artigos


def extrair_artigos_bytes(
    caminho,
    identificador,
):
    dados = caminho.read_bytes()

    (
        candidatos,
        encoding,
    ) = listar_candidatos_artigo(
        dados
    )

    selecionados = (
        selecionar_candidatos_unicos(
            candidatos
        )
    )

    selecionados = (
        cortar_no_artigo_final(
            identificador,
            selecionados,
        )
    )

    artigos = montar_artigos(
        dados,
        selecionados,
        candidatos,
    )

    descartados = (
        len(
            candidatos
        )
        - len(
            selecionados
        )
    )

    qualidade = (
        (
            len(
                selecionados
            )
            / len(
                candidatos
            )
        )
        if candidatos
        else 0.0
    )

    return {
        "dados": dados,
        "encoding": encoding,
        "artigos": artigos,
        "candidatos_lista": candidatos,
        "selecionados_lista": selecionados,
        "candidatos": len(
            candidatos
        ),
        "unicos": len(
            {
                item[
                    "artigo"
                ]
                for item in candidatos
            }
        ),
        "descartados": descartados,
        "qualidade": qualidade,
        "bytes": len(
            dados
        ),
    }


# ============================================================
# REVALIDAÇÃO DO CABEÇALHO NO OFFSET
# ============================================================

def cabecalho_no_offset(
    dados,
    encoding,
    offset,
):
    if not (
        0
        <= offset
        < len(
            dados
        )
    ):
        return None

    trecho = dados[
        offset:
        min(
            len(
                dados
            ),
            offset + 2048,
        )
    ]

    texto = decodificar_trecho(
        trecho,
        encoding,
    )

    linhas = texto.splitlines()

    if not linhas:
        return None

    direto = (
        PADRAO_ARTIGO_DIRETO.match(
            linhas[
                0
            ]
        )
    )

    if direto:
        return formatar_artigo(
            numero_do_match(
                direto
            ),
            sufixo_do_match(
                direto
            ),
        )

    art_sozinho = (
        PADRAO_ART_SOZINHO.match(
            linhas[
                0
            ]
        )
    )

    if not art_sozinho:
        return None

    nao_vazias = 0

    for linha in linhas[
        1:8
    ]:
        if not linha.strip():
            continue

        nao_vazias += 1

        numero_match = (
            PADRAO_CONTINUACAO_NUMERO.match(
                linha
            )
        )

        if numero_match:
            return formatar_artigo(
                numero_do_match(
                    numero_match
                ),
                sufixo_do_match(
                    numero_match
                ),
            )

        if nao_vazias >= 2:
            break

    return None


def validar_offsets(
    dados,
    encoding,
    artigos,
):
    erros = []

    offsets = set()

    for artigo in artigos:
        offset = artigo[
            "offset"
        ]

        tamanho = artigo[
            "tamanho"
        ]

        if offset in offsets:
            erros.append(
                (
                    "Offset duplicado em "
                    f"Art. {artigo['artigo']}: {offset}."
                )
            )

        offsets.add(
            offset
        )

        if tamanho <= 0:
            erros.append(
                (
                    f"Tamanho inválido em "
                    f"Art. {artigo['artigo']}."
                )
            )

        if (
            offset
            + tamanho
            > len(
                dados
            )
        ):
            erros.append(
                (
                    f"Faixa ultrapassa arquivo em "
                    f"Art. {artigo['artigo']}."
                )
            )

        lido = cabecalho_no_offset(
            dados,
            encoding,
            offset,
        )

        if (
            lido
            != artigo[
                "artigo"
            ]
        ):
            erros.append(
                (
                    "Offset não aponta para o artigo "
                    f"esperado: índice={artigo['artigo']} "
                    f"lido={lido} offset={offset}."
                )
            )

    return erros


# ============================================================
# VALIDAÇÃO ESTRUTURAL POR NORMA
# ============================================================

def validar_norma_indexada(
    identificador,
    artigos,
    candidatos_lista,
    qualidade,
):
    erros = []
    alertas = []

    chaves = [
        item[
            "artigo"
        ]
        for item in artigos
    ]

    conjunto = set(
        chaves
    )

    candidatos_chaves = {
        item[
            "artigo"
        ]
        for item in candidatos_lista
    }

    if not artigos:
        erros.append(
            "Nenhum artigo indexado."
        )

        return (
            erros,
            alertas,
        )

    # Se a própria fonte contém Art. 1, ele deve obrigatoriamente
    # sobreviver à deduplicação.
    if (
        "1"
        in candidatos_chaves
        and "1"
        not in conjunto
    ):
        erros.append(
            (
                "Art. 1 foi encontrado como candidato, "
                "mas desapareceu do índice final."
            )
        )

    # Se há muitos artigos e nem sequer aparece Art. 1 como
    # candidato, algo no parser/formatação ainda está suspeito.
    if (
        len(
            candidatos_lista
        )
        >= 20
        and "1"
        not in candidatos_chaves
    ):
        alertas.append(
            "Art. 1 não foi encontrado no texto como cabeçalho."
        )

    # Duplicatas nunca podem existir no índice final.
    duplicados = sorted(
        {
            artigo
            for artigo in chaves
            if chaves.count(
                artigo
            )
            > 1
        }
    )

    if duplicados:
        erros.append(
            (
                "Artigos duplicados no índice final: "
                + ", ".join(
                    duplicados[
                        :30
                    ]
                )
            )
        )

    config = (
        VALIDACOES_ESPECIAIS.get(
            identificador
        )
    )

    if config:
        if (
            len(
                artigos
            )
            < config[
                "min_artigos"
            ]
        ):
            erros.append(
                (
                    "Quantidade abaixo do mínimo "
                    f"validado: {len(artigos)} < "
                    f"{config['min_artigos']}."
                )
            )

        final = config[
            "artigo_final"
        ]

        if final not in conjunto:
            erros.append(
                (
                    "Artigo final obrigatório ausente: "
                    f"{final}."
                )
            )

        faltantes = [
            ancora
            for ancora in config[
                "ancoras"
            ]
            if ancora not in conjunto
        ]

        if faltantes:
            erros.append(
                (
                    "Artigos-âncora ausentes: "
                    + ", ".join(
                        faltantes
                    )
                )
            )

    minimo_regressao = (
        REGRESSION_GUARDS.get(
            identificador
        )
    )

    if (
        minimo_regressao is not None
        and len(
            artigos
        )
        < minimo_regressao
    ):
        erros.append(
            (
                "Regressão de indexação detectada: "
                f"{len(artigos)} artigos < "
                f"piso de segurança {minimo_regressao}."
            )
        )

    # Sufixos com palavras inteiras foram um bug explícito da V4.
    # Na V5 só 1-2 letras são permitidas e mesmo assim fazemos
    # uma conferência defensiva.
    sufixos_invalidos = [
        artigo
        for artigo in chaves
        if (
            "-"
            in artigo
            and len(
                artigo.split(
                    "-",
                    1,
                )[
                    1
                ]
            )
            > 2
        )
    ]

    if sufixos_invalidos:
        erros.append(
            (
                "Sufixos impossíveis detectados: "
                + ", ".join(
                    sufixos_invalidos[
                        :20
                    ]
                )
            )
        )

    return (
        erros,
        alertas,
    )


# ============================================================
# AMOSTRAS DE LEITURA REAL PELOS OFFSETS
# ============================================================

def criar_amostras(
    identificador,
    nome,
    dados,
    artigos,
):
    mapa = {
        item[
            "artigo"
        ]: item
        for item in artigos
    }

    pedidos = (
        AMOSTRAS_OBRIGATORIAS.get(
            identificador,
            []
        )
    )

    linhas = []

    for artigo in pedidos:
        item = mapa.get(
            artigo
        )

        if not item:
            linhas.append(
                (
                    f"[FALHA] {identificador} "
                    f"Art. {artigo}: não indexado."
                )
            )

            continue

        inicio = item[
            "offset"
        ]

        tamanho_amostra = min(
            item[
                "tamanho"
            ],
            500,
        )

        trecho = dados[
            inicio:
            inicio + tamanho_amostra
        ]

        texto = decodificar_trecho(
            trecho
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto,
        ).strip()

        linhas.append(
            (
                f"[OK] {identificador} "
                f"Art. {artigo} "
                f"| offset={inicio} "
                f"| tamanho={item['tamanho']} "
                f"| {nome}"
            )
        )

        linhas.append(
            (
                "    "
                + texto[
                    :420
                ]
            )
        )

    return linhas


# ============================================================
# JURISPRUDÊNCIA
# ============================================================

def localizar_jurisprudencia(
    registro,
    origem,
):
    arquivo = str(
        registro.get(
            "arquivo",
            ""
        )
    ).strip()

    if not arquivo:
        return None

    raiz = (
        origem
        / (
            "9-CÓDIGO DE DEFESA "
            "DO CONSUMIDOR"
        )
        / "19_JURISPRUDENCIA"
    )

    if not raiz.exists():
        raiz = (
            origem
            / "19_JURISPRUDENCIA"
        )

    if not raiz.exists():
        return None

    encontrados = [
        caminho
        for caminho in raiz.rglob(
            arquivo
        )
        if caminho.is_file()
    ]

    if len(
        encontrados
    ) == 1:
        return encontrados[
            0
        ]

    if not encontrados:
        return None

    # Se houver duplicatas físicas com o mesmo nome,
    # não escolhemos arbitrariamente.
    return None


# ============================================================
# GERAÇÃO
# ============================================================

def gerar_indices(
    origem,
    catalogo_mestre,
    itens_mestre,
    registros_juris,
):
    pasta_saida = (
        origem
        / PASTA_INDICES_NOME
    )

    pasta_saida.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas_normas = [
        "#LEXMACHINA|NORMAS|5",
        (
            "#ID|SIGLA|PRIORIDADE|RAMO|"
            "NOME|CAMINHO|ARTIGOS|BYTES"
        ),
    ]

    linhas_artigos = [
        "#LEXMACHINA|ARTIGOS|5",
        "#ID|ARTIGO|OFFSET|TAMANHO",
    ]

    linhas_menu = [
        "#LEXMACHINA|MENU|5",
        "#ORDEM|ID|SIGLA|RAMO|NOME",
    ]

    linhas_juris = [
        "#LEXMACHINA|JURIS|5",
        (
            "#TRIBUNAL|TIPO|NUMERO|STATUS|"
            "ARQUIVO|RELACIONADO_A"
        ),
    ]

    erros = []
    alertas = []
    detalhes = []
    amostras = []

    total_normas = 0
    total_artigos = 0
    total_candidatos = 0
    total_descartados = 0
    total_juris = 0

    # --------------------------------------------------------
    # NORMAS
    # --------------------------------------------------------

    total_catalogo = len(
        itens_mestre
    )

    for ordem, item in enumerate(
        itens_mestre,
        start=1,
    ):
        identificador = limpar_campo(
            item.get(
                "id",
                "",
            )
        )

        nome = limpar_campo(
            item.get(
                "nome",
                "",
            )
        )

        print(
            (
                f"[NORMA {ordem}/{total_catalogo}] "
                f"{identificador} - {nome}"
            )
        )

        caminho = localizar_norma(
            item,
            origem,
        )

        if caminho is None:
            mensagem = (
                "Norma não encontrada: "
                f"{identificador} - {nome}"
            )

            erros.append(
                mensagem
            )

            print(
                "  ERRO: arquivo não encontrado."
            )

            continue

        try:
            resultado = (
                extrair_artigos_bytes(
                    caminho,
                    identificador,
                )
            )

        except OSError as erro:
            mensagem = (
                f"{identificador}: falha ao ler "
                f"{caminho}: {erro}"
            )

            erros.append(
                mensagem
            )

            print(
                f"  ERRO: {erro}"
            )

            continue

        artigos = resultado[
            "artigos"
        ]

        candidatos = resultado[
            "candidatos"
        ]

        descartados = resultado[
            "descartados"
        ]

        qualidade = resultado[
            "qualidade"
        ]

        dados = resultado[
            "dados"
        ]

        erros_offset = validar_offsets(
            dados,
            resultado[
                "encoding"
            ],
            artigos,
        )

        (
            erros_norma,
            alertas_norma,
        ) = validar_norma_indexada(
            identificador,
            artigos,
            resultado[
                "candidatos_lista"
            ],
            qualidade,
        )

        for erro_item in erros_offset:
            erros.append(
                (
                    f"{identificador}: "
                    f"{erro_item}"
                )
            )

        for erro_item in erros_norma:
            erros.append(
                (
                    f"{identificador}: "
                    f"{erro_item}"
                )
            )

        for alerta_item in alertas_norma:
            alertas.append(
                (
                    f"{identificador}: "
                    f"{alerta_item}"
                )
            )

        sigla = limpar_campo(
            gerar_sigla(
                item
            )
        )

        prioridade = limpar_campo(
            item.get(
                "prioridade",
                "",
            )
        )

        ramo = limpar_campo(
            item.get(
                "ramo",
                "",
            )
        )

        caminho_sd = caminho_esp32(
            caminho,
            origem,
        )

        linhas_normas.append(
            "|".join(
                [
                    identificador,
                    sigla,
                    prioridade,
                    ramo,
                    nome,
                    caminho_sd,
                    str(
                        len(
                            artigos
                        )
                    ),
                    str(
                        resultado[
                            "bytes"
                        ]
                    ),
                ]
            )
        )

        linhas_menu.append(
            "|".join(
                [
                    str(
                        ordem
                    ),
                    identificador,
                    sigla,
                    ramo,
                    nome,
                ]
            )
        )

        for artigo in artigos:
            linhas_artigos.append(
                "|".join(
                    [
                        identificador,
                        artigo[
                            "artigo"
                        ],
                        str(
                            artigo[
                                "offset"
                            ]
                        ),
                        str(
                            artigo[
                                "tamanho"
                            ]
                        ),
                    ]
                )
            )

        primeiro = (
            artigos[
                0
            ][
                "artigo"
            ]
            if artigos
            else ""
        )

        ultimo = (
            artigos[
                -1
            ][
                "artigo"
            ]
            if artigos
            else ""
        )

        detalhes.append(
            {
                "id": identificador,
                "nome": nome,
                "arquivo": caminho_sd,
                "bytes": resultado[
                    "bytes"
                ],
                "candidatos": candidatos,
                "artigos_indexados": len(
                    artigos
                ),
                "descartados": descartados,
                "qualidade": round(
                    qualidade,
                    4,
                ),
                "primeiro": primeiro,
                "ultimo": ultimo,
                "erros_offset": len(
                    erros_offset
                ),
                "erros_estruturais": len(
                    erros_norma
                ),
                "alertas": len(
                    alertas_norma
                ),
            }
        )

        amostras.extend(
            criar_amostras(
                identificador,
                nome,
                dados,
                artigos,
            )
        )

        total_normas += 1
        total_artigos += len(
            artigos
        )

        total_candidatos += candidatos

        total_descartados += (
            descartados
        )

        print(
            (
                f"  artigos={len(artigos)} "
                f"| candidatos={candidatos} "
                f"| descartados={descartados} "
                f"| primeiro={primeiro} "
                f"| último={ultimo}"
            )
        )

    # --------------------------------------------------------
    # JURISPRUDÊNCIA
    # --------------------------------------------------------

    for registro in registros_juris:
        caminho = localizar_jurisprudencia(
            registro,
            origem,
        )

        if caminho is None:
            erros.append(
                (
                    "Jurisprudência não encontrada "
                    "ou ambígua: "
                    f"{registro.get('tribunal', '')} "
                    f"{registro.get('tipo', '')} "
                    f"{registro.get('numero', '')}"
                )
            )

            continue

        relacionados = ",".join(
            limpar_campo(
                item
            )
            for item in registro.get(
                "relacionado_a",
                []
            )
        )

        linhas_juris.append(
            "|".join(
                [
                    limpar_campo(
                        registro.get(
                            "tribunal",
                            "",
                        )
                    ),
                    limpar_campo(
                        registro.get(
                            "tipo",
                            "",
                        )
                    ),
                    limpar_campo(
                        registro.get(
                            "numero",
                            "",
                        )
                    ),
                    limpar_campo(
                        registro.get(
                            "status",
                            "",
                        )
                    ),
                    caminho_esp32(
                        caminho,
                        origem,
                    ),
                    relacionados,
                ]
            )
        )

        total_juris += 1

    # --------------------------------------------------------
    # GRAVAÇÃO
    # --------------------------------------------------------

    saidas = {
        ARQ_NORMAS: linhas_normas,
        ARQ_ARTIGOS: linhas_artigos,
        ARQ_JURIS: linhas_juris,
        ARQ_MENU: linhas_menu,
    }

    for nome_arquivo, linhas in (
        saidas.items()
    ):
        (
            pasta_saida
            / nome_arquivo
        ).write_text(
            "\n".join(
                linhas
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

    meta = {
        "lex_machina": True,
        "formato_indice": 5,
        "modo": "TESTE_SEGURO",
        "gerado_em": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "versao_catalogo": (
            catalogo_mestre.get(
                "versao",
                "",
            )
        ),
        "normas_catalogo": len(
            itens_mestre
        ),
        "normas_indexadas": (
            total_normas
        ),
        "artigos_indexados": (
            total_artigos
        ),
        "candidatos_artigo": (
            total_candidatos
        ),
        "duplicatas_referencias_descartadas": (
            total_descartados
        ),
        "jurisprudencias_indexadas": (
            total_juris
        ),
        "erros": len(
            erros
        ),
        "alertas": len(
            alertas
        ),
        "arquivos": {
            "normas": ARQ_NORMAS,
            "artigos": ARQ_ARTIGOS,
            "jurisprudencia": ARQ_JURIS,
            "menu": ARQ_MENU,
            "relatorio": ARQ_RELATORIO,
            "amostras": ARQ_AMOSTRAS,
        },
        "detalhes_normas": detalhes,
    }

    (
        pasta_saida
        / ARQ_META
    ).write_text(
        json.dumps(
            meta,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    (
        pasta_saida
        / ARQ_AMOSTRAS
    ).write_text(
        (
            "LEX MACHINA\n"
            "AMOSTRAS REAIS LIDAS PELOS OFFSETS V5\n"
            + "=" * 78
            + "\n\n"
            + "\n".join(
                amostras
            )
            + "\n"
        ),
        encoding="utf-8",
        newline="\n",
    )

    # --------------------------------------------------------
    # RELATÓRIO
    # --------------------------------------------------------

    relatorio = [
        "LEX MACHINA",
        "GERAÇÃO DE ÍNDICES PARA ESP32 - VERSÃO 5",
        "MODO TESTE SEGURO",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        f"ORIGEM: {origem}",
        (
            "VERSÃO DO CATÁLOGO: "
            f"{catalogo_mestre.get('versao', '')}"
        ),
        "",
        (
            "NORMAS NO CATÁLOGO: "
            f"{len(itens_mestre)}"
        ),
        (
            "NORMAS INDEXADAS: "
            f"{total_normas}"
        ),
        (
            "ARTIGOS INDEXADOS: "
            f"{total_artigos}"
        ),
        (
            "CANDIDATOS ENCONTRADOS: "
            f"{total_candidatos}"
        ),
        (
            "DUPLICATAS/REFERÊNCIAS DESCARTADAS: "
            f"{total_descartados}"
        ),
        (
            "JURISPRUDÊNCIAS INDEXADAS: "
            f"{total_juris}"
        ),
        f"ERROS: {len(erros)}",
        f"ALERTAS: {len(alertas)}",
        "",
        "PASTA DE TESTE:",
        str(
            pasta_saida
        ),
        "",
        "=" * 78,
        "DIAGNÓSTICO POR NORMA",
        "=" * 78,
        "",
    ]

    for detalhe in detalhes:
        relatorio.append(
            (
                f"{detalhe['id']} "
                f"| artigos={detalhe['artigos_indexados']} "
                f"| candidatos={detalhe['candidatos']} "
                f"| descartados={detalhe['descartados']} "
                f"| qualidade={detalhe['qualidade']:.4f} "
                f"| primeiro={detalhe['primeiro']} "
                f"| ultimo={detalhe['ultimo']} "
                f"| offset_errors={detalhe['erros_offset']} "
                f"| structural_errors="
                f"{detalhe['erros_estruturais']} "
                f"| alerts={detalhe['alertas']} "
                f"| {detalhe['nome']}"
            )
        )

    relatorio.append("")

    if erros:
        relatorio.extend(
            [
                "=" * 78,
                "ERROS",
                "=" * 78,
                "",
            ]
        )

        for erro in erros:
            relatorio.append(
                f"- {erro}"
            )

        relatorio.append("")

    if alertas:
        relatorio.extend(
            [
                "=" * 78,
                "ALERTAS",
                "=" * 78,
                "",
            ]
        )

        for alerta in alertas:
            relatorio.append(
                f"- {alerta}"
            )

        relatorio.append("")

    relatorio.extend(
        [
            "=" * 78,
            "CONCLUSÃO",
            "=" * 78,
            "",
        ]
    )

    if (
        total_normas
        == len(
            itens_mestre
        )
        and total_juris
        == len(
            registros_juris
        )
        and not erros
        and not alertas
    ):
        relatorio.append(
            (
                "APROVADO AUTOMATICAMENTE: "
                "72 normas e toda a jurisprudência foram "
                "indexadas sem erros ou alertas."
            )
        )

    elif not erros:
        relatorio.append(
            (
                "ÍNDICE GERADO EM MODO TESTE, "
                "MAS EXISTEM ALERTAS PARA REVISÃO."
            )
        )

    else:
        relatorio.append(
            (
                "ÍNDICE NÃO APROVADO: "
                "existem erros que precisam ser corrigidos "
                "antes de promover os arquivos para produção."
            )
        )

    (
        pasta_saida
        / ARQ_RELATORIO
    ).write_text(
        "\n".join(
            relatorio
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return {
        "pasta": pasta_saida,
        "normas_catalogo": len(
            itens_mestre
        ),
        "normas": total_normas,
        "artigos": total_artigos,
        "candidatos": total_candidatos,
        "descartados": total_descartados,
        "juris": total_juris,
        "juris_catalogo": len(
            registros_juris
        ),
        "erros": erros,
        "alertas": alertas,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    args = argumentos()

    origem = Path(
        args.origem
    )

    if (
        not origem.exists()
        or not origem.is_dir()
    ):
        raise FileNotFoundError(
            f"Origem inválida: {origem}"
        )

    catalogo_mestre, itens_mestre = (
        carregar_catalogo_mestre()
    )

    registros_juris = (
        carregar_catalogo_juris()
    )

    print()
    print(
        "LEX MACHINA"
    )

    print(
        "GERADOR DE ÍNDICES ESP32 V5"
    )

    print(
        "MODO TESTE SEGURO"
    )

    print(
        "=" * 64
    )

    print(
        f"Origem: {origem}"
    )

    print(
        (
            "Normas no catálogo: "
            f"{len(itens_mestre)}"
        )
    )

    print(
        (
            "Jurisprudências no catálogo: "
            f"{len(registros_juris)}"
        )
    )

    print()

    resultado = gerar_indices(
        origem,
        catalogo_mestre,
        itens_mestre,
        registros_juris,
    )

    print()
    print(
        "=" * 64
    )

    print(
        "GERAÇÃO FINALIZADA"
    )

    print(
        (
            "Normas: "
            f"{resultado['normas']}/"
            f"{resultado['normas_catalogo']}"
        )
    )

    print(
        f"Artigos: {resultado['artigos']}"
    )

    print(
        (
            "Candidatos: "
            f"{resultado['candidatos']}"
        )
    )

    print(
        (
            "Descartados: "
            f"{resultado['descartados']}"
        )
    )

    print(
        (
            "Jurisprudências: "
            f"{resultado['juris']}/"
            f"{resultado['juris_catalogo']}"
        )
    )

    print(
        f"Erros: {len(resultado['erros'])}"
    )

    print(
        f"Alertas: {len(resultado['alertas'])}"
    )

    print()

    print(
        (
            "Pasta de teste: "
            f"{resultado['pasta']}"
        )
    )

    print()

    if (
        resultado[
            "normas"
        ]
        == resultado[
            "normas_catalogo"
        ]
        and resultado[
            "juris"
        ]
        == resultado[
            "juris_catalogo"
        ]
        and not resultado[
            "erros"
        ]
        and not resultado[
            "alertas"
        ]
    ):
        print(
            "✓ ÍNDICE V5 APROVADO AUTOMATICAMENTE"
        )

    elif not resultado[
        "erros"
    ]:
        print(
            (
                "✓ Índice criado em modo teste, "
                "com alertas para revisão."
            )
        )

    else:
        print(
            (
                "⚠ Índice NÃO aprovado. "
                "Revise o relatório."
            )
        )


if __name__ == "__main__":
    try:
        main()

    except Exception as erro:
        print()
        print(
            "ERRO FATAL:"
        )
        print(
            erro
        )
        sys.exit(
            1
        )
