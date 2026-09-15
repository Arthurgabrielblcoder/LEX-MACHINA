from __future__ import annotations

r"""
LEX MACHINA
PIPELINE OFICIAL V4 - PREFLIGHT CONFIÁVEL + CORPUS CANÔNICO

Esta versão corrige duas falhas comprovadas da V2:

1) O JSON-LD do normas.leg.br publica contentUrl como:
       https://normas.leg.br/api/binario/<UUID>/texto
   Mas a rota pública acessível externamente é:
       https://normas.leg.br/api/public/binario/<UUID>/texto

   A V2 seguia literalmente /api/binario e recebia HTTP 404.
   A V3 preserva a URL declarada para auditoria, mas faz a requisição
   pela forma pública /api/public/binario.

2) A árvore estruturada pode conter, dentro de um artigo da norma A,
   dispositivos da norma B que A está alterando. Exemplo clássico:
   Lei 14.133/2021 art. 177 contém a redação do CPC art. 1.048.
   A V2 indexava o art. 1.048 como se fosse artigo da Lei 14.133.

   A V3 só aceita um nó estruturado se o legislationIdentifier do nó,
   antes de "!", pertencer EXATAMENTE à URN da norma-alvo.

Arquitetura da V4
=================
- A fonte principal continua sendo a manifestação "Current" /
  "Compilação Monovigente" informada no campo encoding do JSON-LD.
- Se o normas.leg.br não publicar uma manifestação Current para a norma,
  a V4 usa COMO FALLBACK a URL oficial do Planalto já cadastrada em
  fonte_oficial no Catálogo Mestre.
- Esse fallback não é uma URL adivinhada: é a mesma fonte oficial já
  auditada e usada pelo updater do LEX MACHINA.
- O texto atual é baixado da rota pública /api/public/binario/.../texto.
- Os artigos são extraídos do texto oficial atual.
- Um mapa fail-closed de artigo final esperado impede que citações de
  outras leis virem "artigos" da norma consultada.
- A sequência é reconstruída por LIS estritamente crescente, sempre
  iniciando no Art. 1 e terminando no artigo final esperado.
- A árvore estruturada é fallback e também é filtrada pela URN-alvo.
- Offsets são calculados apenas em novos arquivos canônicos UTF-8 criados
  pelo próprio LEX MACHINA.
- 100% dos offsets são reabertos e verificados por SHA-256.

IMPORTANTE
==========
Por padrão o programa roda APENAS o PREFLIGHT de 9 normas.
NÃO escreve nada no microSD.

Uso:
    python construir_lexdata_oficial_v4.py D:\\

Somente depois de obter PREFLIGHT 9/9:
    python construir_lexdata_oficial_v4.py D:\\ --full
"""

from bisect import bisect_left
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
import argparse
import hashlib
import html as html_mod
import json
import os
import re
import shutil
import sys
import time
import unicodedata

import requests
from bs4 import BeautifulSoup


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

CATALOGOS_CANDIDATOS = [
    Path("catalogo_mestre_vademecum.json"),
    Path("catalogo_mestre_vademecum_v1_1.json"),
]

CATALOGO_JURIS = Path(
    "catalogo_jurisprudencia.json"
)

SENADO_BASE = (
    "https://legis.senado.leg.br/dadosabertos"
)

NORMAS_API = (
    "https://normas.leg.br/api/public"
)

NORMAS_SITE = (
    "https://normas.leg.br"
)

CACHE_DIR = Path(
    "cache_lexdata_v4"
)

PREFLIGHT_DIR = (
    Path("saida")
    / "PREFLIGHT_LEXDATA_V4"
)

FULL_BUILD_DIR = (
    Path("saida")
    / "LEXDATA_V4_BUILD"
)

PASTA_PUBLICADA = (
    "99_LEXDATA_ESP32_OFICIAL_V4_TESTE"
)

TIMEOUT = 70
MAX_TENTATIVAS = 4
PAUSA_REDE = 0.20

HEADERS_JSON = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36 "
        "LEX-MACHINA/4.0"
    ),
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.5",
    "Cache-Control": "no-cache",
}

HEADERS_TEXT = {
    "User-Agent": HEADERS_JSON["User-Agent"],
    "Accept": (
        "text/html,text/plain,application/xhtml+xml,"
        "application/octet-stream;q=0.8,*/*;q=0.5"
    ),
    "Accept-Language": HEADERS_JSON["Accept-Language"],
    "Cache-Control": "no-cache",
}


# =============================================================================
# PREFLIGHT
# =============================================================================

PREFLIGHT_IDS = [
    "CF88",
    "CC2002",
    "CPC2015",
    "LAI2011",
    "ECA1990",
    "MARIA2006",
    "LIC2021",
    "LIQFIN1974",
    "RPS1999",
]


# =============================================================================
# ARTIGO FINAL ESPERADO
#
# Estes limites são "fail-closed".
# Se uma futura alteração legislativa criar artigo além do limite atual,
# o pipeline para e exige revisão do catálogo, em vez de indexar silenciosamente
# uma referência pertencente a outra lei.
# =============================================================================

ARTIGO_FINAL = {
    "CF88": 250,
    "CC2002": 2046,
    "CPC2015": 1072,
    "CP1940": 361,
    "CPP1941": 811,
    "CTN1966": 218,
    "CE1965": 383,
    "CLT1943": 922,
    "CDC1990": 119,
    "ECA1990": 267,
    "IDOSO2003": 118,
    "LBI2015": 127,
    "LEP1984": 204,
    "DROGAS2006": 60,
    "MARIA2006": 46,
    "HEDIONDOS1990": 13,
    "LIC2021": 194,
    "MCI2014": 32,
    "LGPD2018": 65,
    "LAI2011": 47,
    "PAF1999": 70,
    "LIA1992": 25,
    "RJU1990": 253,
    "CUSTEIO1991": 105,
    "BENEF1991": 156,
    "FALENCIA2005": 201,
    "SA1976": 300,
    "RPEM1994": 67,
    "LRP1973": 299,
    "CIDADE2001": 58,
    "PNMA1981": 21,
    "CRIMAMB1998": 82,
    "JEC1995": 97,
    "ELEICOES1997": 107,
    "PARTIDOS1995": 63,
    "INELEG1990": 28,
    "ACAOPOP1965": 22,
    "MS2009": 29,
    "ARBIT1996": 44,
    "MED2015": 48,
    "JEF2001": 27,
    "JEFAZ2009": 28,
    "ABUSO2019": 45,
    "ORCRIM2013": 27,
    "LAVAGEM1998": 18,
    "ARMAS2003": 37,
    "TORTURA1997": 4,
    "COND1964": 70,
    "EXECFISC1980": 42,
    "FINPUB1964": 115,
    "LRF2000": 75,
    "LPI1996": 244,
    "LDA1998": 115,
    "COOP1971": 117,
    "TERRA1964": 128,
    "REFAGR1993": 28,
    "MINER1967": 98,
    "CBA1986": 324,
    "CVM1976": 35,
    "SEGUROS1966": 153,
    "LIQFIN1974": 57,
    "CONSORCIO2008": 49,
    "INQUIL1991": 90,
    "SFI1997": 42,
    "TEMP1974": 20,
    "GREVE1989": 19,
    "FGTS1990": 32,
    "RPS1999": 382,
    "ALIMENTOS1968": 29,
    "PATERN1992": 10,
    "ALIMGRAV2008": 12,
    "ALIENPAR2010": 11,
}


# =============================================================================
# CONTAGENS HISTÓRICAS DE REFERÊNCIA
#
# Não são usadas como verdade jurídica absoluta.
# Viram apenas um piso conservador para detectar regressões grosseiras.
# =============================================================================

CONTAGEM_REFERENCIA = {
    "CF88": 276,
    "CC2002": 2077,
    "CPC2015": 1073,
    "CP1940": 417,
    "CPP1941": 847,
    "CTN1966": 230,
    "CE1965": 384,
    "CLT1943": 999,
    "CDC1990": 130,
    "ECA1990": 329,
    "IDOSO2003": 118,
    "LBI2015": 130,
    "LEP1984": 215,
    "DROGAS2006": 76,
    "MARIA2006": 57,
    "HEDIONDOS1990": 13,
    "LIC2021": 196,
    "MCI2014": 32,
    "LGPD2018": 79,
    "LAI2011": 49,
    "PAF1999": 80,
    "LIA1992": 31,
    "RJU1990": 262,
    "CUSTEIO1991": 115,
    "BENEF1991": 178,
    "FALENCIA2005": 261,
    "SA1976": 313,
    "RPEM1994": 71,
    "LRP1973": 314,
    "CIDADE2001": 61,
    "PNMA1981": 39,
    "CRIMAMB1998": 87,
    "JEC1995": 99,
    "ELEICOES1997": 152,
    "PARTIDOS1995": 76,
    "INELEG1990": 33,
    "ACAOPOP1965": 22,
    "MS2009": 29,
    "ARBIT1996": 46,
    "MED2015": 48,
    "JEF2001": 27,
    "JEFAZ2009": 28,
    "ABUSO2019": 46,
    "ORCRIM2013": 36,
    "LAVAGEM1998": 28,
    "ARMAS2003": 41,
    "TORTURA1997": 4,
    "COND1964": 80,
    "EXECFISC1980": 42,
    "FINPUB1964": 116,
    "LRF2000": 83,
    "LPI1996": 247,
    "LDA1998": 122,
    "COOP1971": 118,
    "TERRA1964": 128,
    "REFAGR1993": 36,
    "MINER1967": 102,
    "CBA1986": 326,
    "CVM1976": 44,
    "SEGUROS1966": 159,
    "LIQFIN1974": 57,
    "CONSORCIO2008": 47,
    "INQUIL1991": 91,
    "SFI1997": 43,
    "TEMP1974": 29,
    "GREVE1989": 19,
    "FGTS1990": 49,
    "RPS1999": 470,
    "ALIMENTOS1968": 26,
    "PATERN1992": 11,
    "ALIMGRAV2008": 12,
    "ALIENPAR2010": 12,
}


# =============================================================================
# ÂNCORAS CRÍTICAS
# =============================================================================

ANCORAS = {
    "CF88": [
        "1", "5", "37", "60", "250",
    ],
    "CC2002": [
        "1", "421", "927", "1784", "2046",
    ],
    "CPC2015": [
        "1", "100", "300", "500", "1000", "1072",
    ],
    "CTN1966": [
        "1", "5", "100", "218",
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
    "LEP1984": [
        "1", "9-A", "82", "138", "204",
    ],
    "MARIA2006": [
        "1",
        "7",
        "10-A",
        "12-C",
        "17-A",
        "46",
    ],
    "LIC2021": [
        "1", "50", "100", "150", "194",
    ],
    "CUSTEIO1991": [
        "1", "20", "55", "105",
    ],
    "TORTURA1997": [
        "1", "2", "3", "4",
    ],
    "LIQFIN1974": [
        "1", "10", "19", "36", "50", "57",
    ],
    "RPS1999": [
        "1", "100", "200", "300", "382",
    ],
}


# =============================================================================
# SIGLAS
# =============================================================================

SIGLAS = {
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


# =============================================================================
# URN
# =============================================================================

URN_FIXOS = {
    "CF88": (
        "urn:lex:br:federal:constituicao:"
        "1988-10-05;1988"
    ),
}

TIPOS_LEX = {
    "LEI": "lei",
    "LEI COMPLEMENTAR": "lei.complementar",
    "DECRETO-LEI": "decreto.lei",
    "DECRETO LEI": "decreto.lei",
    "DECRETO": "decreto",
}

TIPOS_SENADO = {
    "LEI": "LEI",
    "LEI COMPLEMENTAR": "LCP",
    "DECRETO-LEI": "DEL",
    "DECRETO LEI": "DEL",
    "DECRETO": "DEC",
}

PADRAO_IDENTIFICACAO = re.compile(
    r"^\s*"
    r"(Lei\s+Complementar|Decreto[\s-]*Lei|Decreto|Lei)"
    r"\s+"
    r"([\d.]+)"
    r"/"
    r"(\d{4})",
    re.IGNORECASE,
)

PADRAO_URN = re.compile(
    r"urn:lex:"
    r"[A-Za-z0-9_\-.:;\[\],@!]+"
)


# =============================================================================
# REGEX DE ARTIGO DO BINÁRIO OFICIAL
# =============================================================================

# Primeira letra obrigatoriamente maiúscula:
# "Art. 20" entra; referência comum "art. 20" não entra.
#
# Suporta:
#   Art. 1º
#   Art . 1º
#   A r t . 1º
#   Art.
#   1º ...
#   Art. 10-A
#   Art. 1.784
#
# Não aceita aspas antes do A, então blocos citados como
# “Art. 1.048...” não viram artigo da norma principal.
PADRAO_ARTIGO_BINARIO = re.compile(
    r"(?m)"
    r"^[ \t\u00a0\u2000-\u200b\u202f\u2060\ufeff]*"
    r"A[ \t]*[rR][ \t]*[tT]"
    r"(?:[ \t]*[iI][ \t]*[gG][ \t]*[oO])?"
    r"[ \t]*\.?"
    r"[ \t]*"
    r"(?:\n[ \t]*)?"
    r"("
        r"\d{1,3}(?:\.\d{3})+"
        r"|"
        r"\d{1,4}"
    r")"
    r"[ \t]*"
    r"(?:º|°|o)?"
    r"(?:"
        r"[ \t]*-[ \t]*"
        r"([A-Z]{1,4})"
        r"(?=$|[\s\.,;:\)\]–—-])"
    r")?"
    r"(?=$|[\s\.,;:\)\]–—-])"
)


# =============================================================================
# UTILITÁRIOS
# =============================================================================

def agora() -> str:
    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def sha256_bytes(
    dados: bytes,
) -> str:
    return hashlib.sha256(
        dados
    ).hexdigest()


def remover_acentos(
    texto: str,
) -> str:
    decomp = unicodedata.normalize(
        "NFKD",
        str(texto or ""),
    )

    return "".join(
        c
        for c in decomp
        if not unicodedata.combining(
            c
        )
    )


def normalizar_busca(
    texto: str,
) -> str:
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


def limpar_campo(
    texto,
) -> str:
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


def texto_localizado(
    valor,
) -> str:
    if isinstance(
        valor,
        str,
    ):
        return valor

    if isinstance(
        valor,
        dict,
    ):
        for chave in (
            "@value",
            "name",
            "value",
        ):
            if isinstance(
                valor.get(
                    chave
                ),
                str,
            ):
                return valor[
                    chave
                ]

        return ""

    if isinstance(
        valor,
        list,
    ):
        partes = [
            texto_localizado(
                item
            )
            for item in valor
        ]

        return " ".join(
            parte
            for parte in partes
            if parte
        )

    return ""


def normalizar_texto(
    texto: str,
) -> str:
    texto = html_mod.unescape(
        str(texto or "")
    )

    substituicoes = {
        "\xa0": " ",
        "\u1680": " ",
        "\u2000": " ",
        "\u2001": " ",
        "\u2002": " ",
        "\u2003": " ",
        "\u2004": " ",
        "\u2005": " ",
        "\u2006": " ",
        "\u2007": " ",
        "\u2008": " ",
        "\u2009": " ",
        "\u200a": " ",
        "\u202f": " ",
        "\u205f": " ",
        "\u3000": " ",
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\u2060": "",
        "\ufeff": "",
    }

    for origem, destino in (
        substituicoes.items()
    ):
        texto = texto.replace(
            origem,
            destino,
        )

    texto = texto.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )

    linhas = []

    vazio_anterior = False

    for linha in texto.split(
        "\n"
    ):
        linha = re.sub(
            r"[ \t]+",
            " ",
            linha,
        ).strip()

        if not linha:
            if not vazio_anterior:
                linhas.append(
                    ""
                )

            vazio_anterior = True

            continue

        linhas.append(
            linha
        )

        vazio_anterior = False

    return "\n".join(
        linhas
    ).strip()


def canonicalizar_artigo(
    numero_bruto: str,
    sufixo_bruto: str | None = None,
) -> str:
    numero = int(
        numero_bruto.replace(
            ".",
            "",
        )
    )

    rotulo = str(
        numero
    )

    if sufixo_bruto:
        rotulo += (
            "-"
            + sufixo_bruto
            .lstrip(
                "-"
            )
            .strip()
            .upper()
        )

    return rotulo


def chave_artigo(
    rotulo: str,
) -> int:
    partes = rotulo.split(
        "-",
        1,
    )

    base = int(
        partes[
            0
        ]
    )

    valor_sufixo = 0

    if len(
        partes
    ) == 2:
        for c in partes[
            1
        ]:
            if (
                "A"
                <= c
                <= "Z"
            ):
                valor_sufixo = (
                    valor_sufixo
                    * 27
                    + (
                        ord(
                            c
                        )
                        - ord(
                            "A"
                        )
                        + 1
                    )
                )

    return (
        base
        * 100000
        + valor_sufixo
    )


def base_artigo(
    rotulo: str,
) -> int:
    return int(
        rotulo.split(
            "-",
            1,
        )[
            0
        ]
    )


def rotulo_apresentacao(
    rotulo: str,
) -> str:
    base = base_artigo(
        rotulo
    )

    sufixo = ""

    if "-" in rotulo:
        sufixo = (
            "-"
            + rotulo.split(
                "-",
                1,
            )[
                1
            ]
        )

    if base <= 9:
        return (
            f"Art. {base}º{sufixo}"
        )

    return (
        f"Art. {base}{sufixo}."
    )


def piso_contagem(
    identificador: str,
) -> int:
    referencia = CONTAGEM_REFERENCIA.get(
        identificador,
        0,
    )

    # Conservador: tolera diferença de formatação/insertos,
    # mas bloqueia regressões grotescas.
    return max(
        1,
        int(
            referencia
            * 0.60
        ),
    )


# =============================================================================
# CATÁLOGOS
# =============================================================================

def carregar_json(
    caminho: Path,
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
    candidatos = []

    for caminho in (
        CATALOGOS_CANDIDATOS
    ):
        if not caminho.exists():
            continue

        dados = carregar_json(
            caminho
        )

        itens = dados.get(
            "itens",
            []
        )

        if isinstance(
            itens,
            list,
        ):
            candidatos.append(
                (
                    len(
                        itens
                    ),
                    caminho,
                    dados,
                )
            )

    if not candidatos:
        raise FileNotFoundError(
            "Nenhum catálogo mestre foi encontrado."
        )

    candidatos.sort(
        key=lambda item: item[
            0
        ],
        reverse=True,
    )

    quantidade, caminho, dados = (
        candidatos[
            0
        ]
    )

    if quantidade != 72:
        raise ValueError(
            (
                "O catálogo mestre selecionado não possui "
                f"72 itens: {caminho} possui {quantidade}."
            )
        )

    ids = {
        str(
            item.get(
                "id",
                "",
            )
        ).strip()
        for item in dados[
            "itens"
        ]
    }

    faltantes_finais = sorted(
        ids
        - set(
            ARTIGO_FINAL
        )
    )

    if faltantes_finais:
        raise ValueError(
            (
                "ARTIGO_FINAL não cobre: "
                + ", ".join(
                    faltantes_finais
                )
            )
        )

    return (
        caminho,
        dados,
        dados[
            "itens"
        ],
    )


# =============================================================================
# HTTP / CACHE
# =============================================================================

def chave_cache(
    url: str,
    params: dict | None,
) -> str:
    serial = json.dumps(
        {
            "url": url,
            "params": params or {},
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    return hashlib.sha256(
        serial.encode(
            "utf-8"
        )
    ).hexdigest()


class ClienteHTTP:
    def __init__(self):
        self.sessao = requests.Session()

        CACHE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    def request(
        self,
        url: str,
        params: dict | None,
        headers: dict,
    ) -> requests.Response:
        ultimo = None

        for tentativa in range(
            1,
            MAX_TENTATIVAS + 1,
        ):
            try:
                resposta = (
                    self.sessao.get(
                        url,
                        params=params,
                        headers=headers,
                        timeout=TIMEOUT,
                        allow_redirects=True,
                    )
                )

                if (
                    resposta.status_code
                    in {
                        429,
                        500,
                        502,
                        503,
                        504,
                    }
                ):
                    ultimo = RuntimeError(
                        (
                            "HTTP "
                            f"{resposta.status_code} "
                            f"em {resposta.url}"
                        )
                    )

                    if (
                        tentativa
                        < MAX_TENTATIVAS
                    ):
                        time.sleep(
                            min(
                                2 ** tentativa,
                                12,
                            )
                        )

                        continue

                resposta.raise_for_status()

                time.sleep(
                    PAUSA_REDE
                )

                return resposta

            except Exception as erro:
                ultimo = erro

                if (
                    tentativa
                    < MAX_TENTATIVAS
                ):
                    time.sleep(
                        min(
                            2 ** tentativa,
                            12,
                        )
                    )

        raise RuntimeError(
            (
                f"Falha HTTP em {url}: "
                f"{ultimo}"
            )
        )

    def json(
        self,
        url: str,
        params: dict | None = None,
    ):
        chave = chave_cache(
            url,
            params,
        )

        cache = (
            CACHE_DIR
            / (
                chave
                + ".json"
            )
        )

        if cache.exists():
            return json.loads(
                cache.read_text(
                    encoding="utf-8"
                )
            )

        resposta = self.request(
            url,
            params,
            HEADERS_JSON,
        )

        dados = resposta.json()

        cache.write_text(
            json.dumps(
                dados,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

        return dados

    def bytes(
        self,
        url: str,
    ) -> tuple[
        bytes,
        str,
        str,
    ]:
        chave = chave_cache(
            url,
            None,
        )

        cache = (
            CACHE_DIR
            / (
                chave
                + ".bin"
            )
        )

        meta = (
            CACHE_DIR
            / (
                chave
                + ".meta.json"
            )
        )

        if cache.exists():
            content_type = ""
            url_final = url

            if meta.exists():
                try:
                    info = json.loads(
                        meta.read_text(
                            encoding="utf-8"
                        )
                    )

                    content_type = str(
                        info.get(
                            "content_type",
                            "",
                        )
                    )

                    url_final = str(
                        info.get(
                            "url_final",
                            url,
                        )
                    )

                except Exception:
                    pass

            return (
                cache.read_bytes(),
                content_type,
                url_final,
            )

        resposta = self.request(
            url,
            None,
            HEADERS_TEXT,
        )

        dados = resposta.content

        cache.write_bytes(
            dados
        )

        meta.write_text(
            json.dumps(
                {
                    "url_final": str(
                        resposta.url
                    ),
                    "content_type": (
                        resposta.headers.get(
                            "Content-Type",
                            "",
                        )
                    ),
                    "bytes": len(
                        dados
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

        return (
            dados,
            resposta.headers.get(
                "Content-Type",
                "",
            ),
            str(
                resposta.url
            ),
        )


# =============================================================================
# IDENTIFICAÇÃO / URN
# =============================================================================

def identificar_item(
    item: dict,
) -> dict:
    identificador = str(
        item.get(
            "id",
            "",
        )
    ).strip()

    nome = str(
        item.get(
            "nome",
            "",
        )
    ).strip()

    if identificador == "CF88":
        return {
            "tipo_lex": "constituicao",
            "tipo_senado": "CON",
            "numero": 1988,
            "ano": 1988,
            "urn_inicial": (
                URN_FIXOS[
                    "CF88"
                ]
            ),
        }

    match = PADRAO_IDENTIFICACAO.search(
        nome
    )

    if not match:
        raise ValueError(
            (
                "Não foi possível identificar "
                f"tipo/número/ano: {nome}"
            )
        )

    tipo = (
        match.group(
            1
        )
        .upper()
    )

    tipo = re.sub(
        r"\s*-\s*",
        "-",
        tipo,
    )

    tipo = re.sub(
        r"\s+",
        " ",
        tipo,
    )

    if tipo == "DECRETO LEI":
        tipo = "DECRETO-LEI"

    numero = int(
        re.sub(
            r"\D+",
            "",
            match.group(
                2
            ),
        )
    )

    ano = int(
        match.group(
            3
        )
    )

    return {
        "tipo_lex": TIPOS_LEX[
            tipo
        ],
        "tipo_senado": (
            TIPOS_SENADO[
                tipo
            ]
        ),
        "numero": numero,
        "ano": ano,
        "urn_inicial": (
            "urn:lex:br:federal:"
            f"{TIPOS_LEX[tipo]}:{ano};{numero}"
        ),
    }


def coletar_strings(
    objeto,
):
    if isinstance(
        objeto,
        str,
    ):
        yield objeto
        return

    if isinstance(
        objeto,
        dict,
    ):
        for chave, valor in (
            objeto.items()
        ):
            yield from coletar_strings(
                chave
            )

            yield from coletar_strings(
                valor
            )

        return

    if isinstance(
        objeto,
        list,
    ):
        for valor in objeto:
            yield from coletar_strings(
                valor
            )


def coletar_urns(
    objeto,
) -> list[str]:
    encontrados = []

    for texto in coletar_strings(
        objeto
    ):
        for match in PADRAO_URN.finditer(
            html_mod.unescape(
                texto
            )
        ):
            urn = match.group(
                0
            )

            urn = urn.split(
                "@",
                1,
            )[
                0
            ]

            urn = urn.split(
                "!",
                1,
            )[
                0
            ]

            urn = urn.rstrip(
                ".,);]}"
            )

            encontrados.append(
                urn
            )

    unicos = []

    vistos = set()

    for urn in encontrados:
        if urn in vistos:
            continue

        vistos.add(
            urn
        )

        unicos.append(
            urn
        )

    return unicos


def urn_compativel(
    urn: str,
    info: dict,
) -> bool:
    low = urn.casefold()

    return (
        f":{info['tipo_lex']}:"
        in low
        and f";{info['numero']}"
        in low
        and f":{info['ano']}"
        in low
    )


def resolver_urns(
    cliente: ClienteHTTP,
    item: dict,
) -> list[str]:
    identificador = str(
        item.get(
            "id",
            "",
        )
    ).strip()

    info = identificar_item(
        item
    )

    if identificador == "CF88":
        return [
            info[
                "urn_inicial"
            ]
        ]

    candidatos = []

    try:
        dados = cliente.json(
            (
                SENADO_BASE
                + "/legislacao/lista"
            ),
            params={
                "numero": (
                    info[
                        "numero"
                    ]
                ),
                "ano": info[
                    "ano"
                ],
                "v": 3,
            },
        )

        candidatos.extend(
            coletar_urns(
                dados
            )
        )

    except Exception:
        pass

    try:
        dados = cliente.json(
            (
                SENADO_BASE
                + "/legislacao/"
                + info[
                    "tipo_senado"
                ]
                + "/"
                + str(
                    info[
                        "numero"
                    ]
                )
                + "/"
                + str(
                    info[
                        "ano"
                    ]
                )
            ),
            params={
                "v": 3,
            },
        )

        candidatos.extend(
            coletar_urns(
                dados
            )
        )

    except Exception:
        pass

    candidatos.append(
        info[
            "urn_inicial"
        ]
    )

    candidatos = [
        urn
        for urn in candidatos
        if urn_compativel(
            urn,
            info,
        )
    ]

    unicos = []

    vistos = set()

    for urn in candidatos:
        if urn in vistos:
            continue

        vistos.add(
            urn
        )

        unicos.append(
            urn
        )

    unicos.sort(
        key=lambda urn: (
            1
            if re.search(
                rf":{info['ano']}-\d{{2}}-\d{{2}};",
                urn,
            )
            else 0,
            len(
                urn
            ),
        ),
        reverse=True,
    )

    return unicos


# =============================================================================
# JSON-LD
# =============================================================================

def como_lista(
    valor,
) -> list:
    if valor is None:
        return []

    if isinstance(
        valor,
        list,
    ):
        return valor

    return [
        valor
    ]


def urn_base(
    identificador: str,
) -> str:
    valor = str(
        identificador
        or ""
    ).strip()

    if "!" in valor:
        valor = valor.split(
            "!",
            1,
        )[
            0
        ]

    if "@" in valor:
        valor = valor.split(
            "@",
            1,
        )[
            0
        ]

    return valor


def iter_objetos(
    objeto,
):
    if isinstance(
        objeto,
        dict,
    ):
        yield objeto

        for valor in objeto.values():
            yield from iter_objetos(
                valor
            )

    elif isinstance(
        objeto,
        list,
    ):
        for valor in objeto:
            yield from iter_objetos(
                valor
            )


def encontrar_raiz_alvo(
    tree,
    urn: str,
) -> dict | None:
    alvo = urn_base(
        urn
    )

    candidatos = []

    for objeto in iter_objetos(
        tree
    ):
        ident = urn_base(
            objeto.get(
                "legislationIdentifier",
                "",
            )
        )

        if ident != alvo:
            continue

        score = 0

        if objeto.get(
            "encoding"
        ):
            score += 100

        if objeto.get(
            "hasPart"
        ):
            score += 50

        if (
            objeto.get(
                "legislationIdentifier"
            )
            == alvo
        ):
            score += 20

        candidatos.append(
            (
                score,
                objeto,
            )
        )

    if not candidatos:
        return None

    candidatos.sort(
        key=lambda item: item[
            0
        ],
        reverse=True,
    )

    return candidatos[
        0
    ][
        1
    ]


def iter_nodes_haspart(
    node,
):
    if not isinstance(
        node,
        dict,
    ):
        return

    yield node

    for filho in como_lista(
        node.get(
            "hasPart"
        )
    ):
        if isinstance(
            filho,
            dict,
        ):
            yield from iter_nodes_haspart(
                filho
            )


def first_work_example(
    node: dict,
) -> dict:
    for exemplo in como_lista(
        node.get(
            "workExample"
        )
    ):
        if isinstance(
            exemplo,
            dict,
        ):
            return exemplo

    return {}


def tipo_node(
    node: dict,
) -> str:
    tipo = node.get(
        "legislationType"
    )

    if isinstance(
        tipo,
        dict,
    ):
        identificador = str(
            tipo.get(
                "@id",
                "",
            )
        )

    else:
        identificador = str(
            tipo
            or ""
        )

    if ":" in identificador:
        identificador = identificador.rsplit(
            ":",
            1,
        )[
            -1
        ]

    return identificador.casefold().strip()


def suffix_identificador(
    texto: str,
) -> str:
    texto = str(
        texto
        or ""
    )

    if "!" not in texto:
        return ""

    return texto.rsplit(
        "!",
        1,
    )[
        -1
    ]


def artigo_do_suffix(
    suffix: str,
) -> str | None:
    match = re.fullmatch(
        r"art"
        r"(\d+)"
        r"(?:[-_]?([A-Za-z]{1,4}))?",
        str(
            suffix
            or ""
        ).strip(),
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    sufixo = (
        "-"
        + match.group(
            2
        )
        if match.group(
            2
        )
        else None
    )

    return canonicalizar_artigo(
        match.group(
            1
        ),
        sufixo,
    )


def texto_subarvore(
    node: dict,
) -> str:
    partes = []

    for atual in iter_nodes_haspart(
        node
    ):
        exemplo = first_work_example(
            atual
        )

        texto = exemplo.get(
            "text"
        )

        if (
            isinstance(
                texto,
                str,
            )
            and texto.strip()
        ):
            partes.append(
                texto.strip()
            )

    return normalizar_texto(
        "\n".join(
            partes
        )
    )


def extrair_estruturado_filtrado(
    tree,
    urn: str,
) -> list[dict]:
    """
    SOMENTE artigos cujo legislationIdentifier pertence à norma-alvo.

    Isso impede que, por exemplo, o CPC art. 1.048 citado dentro da
    Lei 14.133/2021 seja indexado como se fosse um artigo da Lei 14.133.
    """

    raiz = encontrar_raiz_alvo(
        tree,
        urn,
    )

    if raiz is None:
        return []

    alvo = urn_base(
        raiz.get(
            "legislationIdentifier",
            urn,
        )
    )

    por_rotulo = {}

    for node in iter_nodes_haspart(
        raiz
    ):
        if tipo_node(
            node
        ) != "artigo":
            continue

        identificador = str(
            node.get(
                "legislationIdentifier",
                "",
            )
        )

        if urn_base(
            identificador
        ) != alvo:
            continue

        rotulo = artigo_do_suffix(
            suffix_identificador(
                identificador
            )
        )

        if rotulo is None:
            continue

        if rotulo in por_rotulo:
            # Mesma semântica de extract_text do cliente testado:
            # primeira ocorrência em ordem documental vence.
            continue

        texto = texto_subarvore(
            node
        )

        if not texto:
            continue

        if (
            rotulo_apresentacao(
                rotulo
            )
            not in texto[
                :250
            ]
        ):
            texto = (
                rotulo_apresentacao(
                    rotulo
                )
                + "\n"
                + texto
            )

        por_rotulo[
            rotulo
        ] = {
            "artigo": rotulo,
            "texto": (
                texto.strip()
                + "\n"
            ),
            "origem": "ESTRUTURADO",
        }

    artigos = list(
        por_rotulo.values()
    )

    artigos.sort(
        key=lambda item: (
            chave_artigo(
                item[
                    "artigo"
                ]
            )
        )
    )

    return artigos


def obter_tree(
    cliente: ClienteHTTP,
    urn: str,
):
    return cliente.json(
        (
            NORMAS_API
            + "/normas"
        ),
        params={
            "urn": urn,
            "tipo_documento": (
                "maior-detalhe"
            ),
        },
    )


# =============================================================================
# ENCODING "CURRENT" / CONTENT URL
# =============================================================================

def linguagem_pt(
    valor,
) -> bool:
    texto = texto_localizado(
        valor
    ).casefold().strip()

    if not texto:
        return True

    return (
        texto == "pt"
        or texto.startswith(
            "pt-"
        )
        or texto.startswith(
            "pt_"
        )
        or "portugu" in texto
    )


def canonicalizar_url_publica(
    url: str,
) -> str:
    """
    O JSON-LD publica /api/binario/<uuid>/texto.
    A rota pública externa é /api/public/binario/<uuid>/texto.
    """

    url = str(
        url
        or ""
    ).strip()

    if not url:
        return ""

    url = urljoin(
        NORMAS_SITE + "/",
        url,
    )

    parsed = urlparse(
        url
    )

    host = parsed.netloc.casefold()

    if not (
        host == "normas.leg.br"
        or host.endswith(
            ".normas.leg.br"
        )
    ):
        return ""

    path = parsed.path

    if path.startswith(
        "/api/binario/"
    ):
        path = (
            "/api/public/binario/"
            + path[
                len(
                    "/api/binario/"
                ):
            ]
        )

    if not path.startswith(
        "/api/public/binario/"
    ):
        return ""

    if not path.endswith(
        "/texto"
    ):
        return ""

    return urlunparse(
        (
            "https",
            "normas.leg.br",
            path,
            "",
            parsed.query,
            "",
        )
    )


def coletar_encodings(
    valor,
) -> list[dict]:
    saida = []

    for objeto in iter_objetos(
        valor
    ):
        content_url = objeto.get(
            "contentUrl"
        )

        if not isinstance(
            content_url,
            str,
        ):
            continue

        bruto = content_url.strip()

        publica = (
            canonicalizar_url_publica(
                bruto
            )
        )

        if not publica:
            continue

        versao = texto_localizado(
            objeto.get(
                "version",
                "",
            )
        )

        nome = texto_localizado(
            objeto.get(
                "name",
                "",
            )
        )

        lingua = texto_localizado(
            objeto.get(
                "inLanguage",
                "",
            )
        )

        formato = texto_localizado(
            objeto.get(
                "encodingFormat",
                "",
            )
        )

        if not linguagem_pt(
            objeto.get(
                "inLanguage"
            )
        ):
            continue

        versao_norm = normalizar_busca(
            versao
        )

        nome_norm = normalizar_busca(
            nome
        )

        atual = (
            versao_norm == "current"
            or "compilacao monovigente"
            in nome_norm
            or "texto atual"
            in nome_norm
        )

        if not atual:
            continue

        score = 0

        if (
            versao_norm
            == "current"
        ):
            score += 1000

        if (
            "compilacao monovigente"
            in nome_norm
        ):
            score += 600

        if (
            "text/html"
            in formato.casefold()
        ):
            score += 200

        if publica.startswith(
            "https://normas.leg.br/api/public/binario/"
        ):
            score += 100

        saida.append(
            {
                "url_jsonld": bruto,
                "url_publica": publica,
                "version": versao,
                "name": nome,
                "inLanguage": lingua,
                "encodingFormat": formato,
                "score": score,
            }
        )

    # Dedup pela URL pública.
    mapa = {}

    for item in saida:
        url = item[
            "url_publica"
        ]

        anterior = mapa.get(
            url
        )

        if (
            anterior is None
            or item[
                "score"
            ]
            > anterior[
                "score"
            ]
        ):
            mapa[
                url
            ] = item

    resultado = list(
        mapa.values()
    )

    resultado.sort(
        key=lambda item: (
            item[
                "score"
            ],
            item[
                "url_publica"
            ],
        ),
        reverse=True,
    )

    return resultado


def candidatos_current(
    tree,
    urn: str,
) -> list[dict]:
    raiz = encontrar_raiz_alvo(
        tree,
        urn,
    )

    if raiz is None:
        return []

    # Fonte principal: encoding da própria norma-alvo.
    candidatos = coletar_encodings(
        raiz.get(
            "encoding"
        )
    )

    if candidatos:
        return candidatos

    # Fallback limitado ao workExample da própria raiz.
    candidatos = coletar_encodings(
        raiz.get(
            "workExample"
        )
    )

    return candidatos


# =============================================================================
# BINÁRIO CURRENT
# =============================================================================

def decodificar_bytes(
    dados: bytes,
) -> str:
    candidatos = []

    for encoding in (
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            texto = dados.decode(
                encoding,
                errors="strict",
            )

        except UnicodeDecodeError:
            continue

        penalidade = (
            texto.count(
                "�"
            )
            * 100
            + texto.count(
                "Ã"
            )
            * 3
            + texto.count(
                "Â"
            )
            * 2
        )

        candidatos.append(
            (
                penalidade,
                -len(
                    texto
                ),
                texto,
            )
        )

    if not candidatos:
        return dados.decode(
            "utf-8",
            errors="replace",
        )

    candidatos.sort(
        key=lambda item: (
            item[
                0
            ],
            item[
                1
            ],
        )
    )

    return candidatos[
        0
    ][
        2
    ]


def bytes_para_texto(
    dados: bytes,
    content_type: str,
) -> str:
    if dados.startswith(
        b"%PDF"
    ):
        raise RuntimeError(
            "A manifestação Current retornou PDF; HTML era esperado."
        )

    texto = decodificar_bytes(
        dados
    )

    low = texto[
        :5000
    ].casefold()

    parece_html = (
        "<html"
        in low
        or "<body"
        in low
        or "<p"
        in low
        or "<div"
        in low
        or "<span"
        in low
    )

    if parece_html:
        soup = BeautifulSoup(
            dados,
            "html.parser",
        )

        for nome in (
            "script",
            "style",
            "noscript",
            "svg",
            "canvas",
            "iframe",
            "form",
            "nav",
        ):
            for tag in soup.find_all(
                nome
            ):
                try:
                    tag.decompose()

                except Exception:
                    pass

        texto = (
            (
                soup.body
                or soup
            )
            .get_text(
                "\n",
                strip=False,
            )
        )

    return normalizar_texto(
        texto
    )



# =============================================================================
# FALLBACK OFICIAL DO PLANALTO
#
# Algumas normas oficiais não possuem manifestação "Current" no
# normas.leg.br. O Decreto 3.048/1999 é um caso comprovado.
#
# Para essas normas usamos SOMENTE item["fonte_oficial"] do Catálogo Mestre,
# e somente se a URL pertencer ao domínio oficial planalto.gov.br.
#
# O extrator remove elementos não textuais e redações explicitamente
# riscadas (<strike>, <s>, <del> ou CSS line-through), reproduzindo a
# estratégia que já passou na auditoria de vigência das 72 normas.
# =============================================================================

def url_planalto_oficial(
    url: str,
) -> bool:
    try:
        parsed = urlparse(
            str(
                url
                or ""
            )
        )

    except Exception:
        return False

    host = (
        parsed.netloc
        .casefold()
        .split(
            ":",
            1,
        )[
            0
        ]
    )

    return (
        host == "planalto.gov.br"
        or host == "www.planalto.gov.br"
    )


def elemento_riscado_planalto(
    tag,
) -> bool:
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

    estilo = str(
        attrs.get(
            "style",
            "",
        )
    ).casefold()

    estilo = re.sub(
        r"\s+",
        "",
        estilo,
    )

    return (
        "line-through"
        in estilo
    )


def bytes_planalto_para_texto_vigente(
    dados: bytes,
) -> str:
    if dados.startswith(
        b"%PDF"
    ):
        raise RuntimeError(
            "A fonte oficial do Planalto retornou PDF; HTML era esperado."
        )

    html = decodificar_bytes(
        dados
    )

    soup = BeautifulSoup(
        html,
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
        "nav",
    ):
        for tag in soup.find_all(
            nome
        ):
            try:
                tag.decompose()

            except Exception:
                pass

    # Percurso reverso evita tentar decompor filhos depois do pai.
    tags = list(
        soup.find_all(
            True
        )
    )

    for tag in reversed(
        tags
    ):
        try:
            if elemento_riscado_planalto(
                tag
            ):
                tag.decompose()

        except (
            AttributeError,
            TypeError,
        ):
            pass

    corpo = (
        soup.body
        or soup
    )

    texto = corpo.get_text(
        separator="\n",
        strip=False,
    )

    return normalizar_texto(
        texto
    )


def tentar_planalto_fallback(
    cliente: ClienteHTTP,
    item: dict,
    tentativas: list[dict],
    urn_preferida: str,
) -> dict | None:
    identificador = str(
        item.get(
            "id",
            "",
        )
    ).strip()

    url = str(
        item.get(
            "fonte_oficial",
            "",
        )
    ).strip()

    if not url:
        tentativas.append(
            {
                "urn": urn_preferida,
                "metodo": "PLANALTO_VIGENTE_FALLBACK",
                "erro": "Catálogo sem fonte_oficial.",
            }
        )

        return None

    if not url_planalto_oficial(
        url
    ):
        tentativas.append(
            {
                "urn": urn_preferida,
                "metodo": "PLANALTO_VIGENTE_FALLBACK",
                "url": url,
                "erro": (
                    "fonte_oficial não pertence ao domínio "
                    "oficial planalto.gov.br."
                ),
            }
        )

        return None

    try:
        (
            dados,
            content_type,
            url_final,
        ) = cliente.bytes(
            url
        )

        if not url_planalto_oficial(
            url_final
        ):
            raise RuntimeError(
                (
                    "Redirecionamento saiu do domínio oficial "
                    f"do Planalto: {url_final}"
                )
            )

        texto = bytes_planalto_para_texto_vigente(
            dados
        )

        (
            artigos,
            diagnostico,
        ) = montar_artigos_binario(
            texto,
            identificador,
        )

        problemas = validar_artigos(
            identificador,
            artigos,
        )

        tentativas.append(
            {
                "urn": urn_preferida,
                "metodo": "PLANALTO_VIGENTE_FALLBACK",
                "url_catalogo": url,
                "url_final": url_final,
                "content_type": content_type,
                "bytes": len(
                    dados
                ),
                "caracteres_texto": len(
                    texto
                ),
                "diagnostico": diagnostico,
                "problemas": problemas,
            }
        )

        if problemas:
            return None

        return {
            "ok": True,
            "urn": urn_preferida,
            "metodo": "PLANALTO_VIGENTE_FALLBACK",
            "fonte": url_final,
            "artigos": artigos,
            "tentativas": tentativas,
        }

    except Exception as erro:
        tentativas.append(
            {
                "urn": urn_preferida,
                "metodo": "PLANALTO_VIGENTE_FALLBACK",
                "url_catalogo": url,
                "erro": str(
                    erro
                ),
            }
        )

        return None


def listar_candidatos_artigos(
    texto: str,
    identificador: str,
) -> list[dict]:
    limite = ARTIGO_FINAL[
        identificador
    ]

    chave_limite = chave_artigo(
        str(
            limite
        )
    )

    candidatos = []

    for match in PADRAO_ARTIGO_BINARIO.finditer(
        texto
    ):
        rotulo = canonicalizar_artigo(
            match.group(
                1
            ),
            match.group(
                2
            ),
        )

        chave = chave_artigo(
            rotulo
        )

        if chave > chave_limite:
            # Ex.: CPC art. 2.027 citado dentro do CPC;
            #      Lei 14.133 art. 1.048 do CPC.
            continue

        candidatos.append(
            {
                "artigo": rotulo,
                "chave": chave,
                "inicio": match.start(),
                "fim_cabecalho": match.end(),
                "linha": (
                    texto[
                        match.start():
                        texto.find(
                            "\n",
                            match.start(),
                        )
                        if texto.find(
                            "\n",
                            match.start(),
                        )
                        >= 0
                        else len(
                            texto
                        )
                    ][
                        :300
                    ]
                ),
            }
        )

    return candidatos


def lis_forcada(
    candidatos: list[dict],
    inicio_idx: int,
    fim_idx: int,
) -> list[int]:
    """
    Retorna índices da maior subsequência estritamente crescente,
    fixando:
      candidatos[inicio_idx] == Art. 1
      candidatos[fim_idx]    == artigo final esperado

    Empates de mesma chave mantêm a ocorrência MAIS ANTIGA.
    Isso reduz o risco de uma citação posterior substituir o
    cabeçalho real.
    """

    inicio = candidatos[
        inicio_idx
    ]

    fim = candidatos[
        fim_idx
    ]

    itens = []

    for idx in range(
        inicio_idx + 1,
        fim_idx,
    ):
        chave = candidatos[
            idx
        ][
            "chave"
        ]

        if (
            chave
            <= inicio[
                "chave"
            ]
            or chave
            >= fim[
                "chave"
            ]
        ):
            continue

        itens.append(
            idx
        )

    if not itens:
        return [
            inicio_idx,
            fim_idx,
        ]

    tails_chaves = []
    tails_pos = []
    anterior = {
        idx: -1
        for idx in itens
    }

    for idx in itens:
        chave = candidatos[
            idx
        ][
            "chave"
        ]

        pos = bisect_left(
            tails_chaves,
            chave,
        )

        if (
            pos
            < len(
                tails_chaves
            )
            and tails_chaves[
                pos
            ]
            == chave
        ):
            # Mesma chave: preserva a ocorrência anterior.
            continue

        if pos == len(
            tails_chaves
        ):
            tails_chaves.append(
                chave
            )

            tails_pos.append(
                idx
            )

        else:
            tails_chaves[
                pos
            ] = chave

            tails_pos[
                pos
            ] = idx

        if pos > 0:
            anterior[
                idx
            ] = tails_pos[
                pos - 1
            ]

    cadeia = []

    if tails_pos:
        atual = tails_pos[
            -1
        ]

        while atual >= 0:
            cadeia.append(
                atual
            )

            atual = anterior.get(
                atual,
                -1,
            )

        cadeia.reverse()

    return (
        [
            inicio_idx
        ]
        + cadeia
        + [
            fim_idx
        ]
    )


def selecionar_sequencia(
    candidatos: list[dict],
    identificador: str,
) -> list[dict]:
    final_label = str(
        ARTIGO_FINAL[
            identificador
        ]
    )

    inicios = [
        i
        for i, item in enumerate(
            candidatos
        )
        if item[
            "artigo"
        ]
        == "1"
    ]

    finais = [
        i
        for i, item in enumerate(
            candidatos
        )
        if item[
            "artigo"
        ]
        == final_label
    ]

    if not inicios:
        raise RuntimeError(
            "Art. 1 não encontrado no texto Current."
        )

    if not finais:
        raise RuntimeError(
            (
                "Artigo final esperado não encontrado: "
                f"{final_label}."
            )
        )

    melhor = None

    for inicio_idx in inicios:
        for fim_idx in finais:
            if fim_idx <= inicio_idx:
                continue

            indices = lis_forcada(
                candidatos,
                inicio_idx,
                fim_idx,
            )

            # Critério:
            # 1) maior quantidade de artigos;
            # 2) em empate, início mais tardio
            #    (resolve preâmbulo Art.1/Art.2 + código que reinicia Art.1);
            # 3) final mais tardio.
            score = (
                len(
                    indices
                ),
                inicio_idx,
                fim_idx,
            )

            if (
                melhor is None
                or score
                > melhor[
                    "score"
                ]
            ):
                melhor = {
                    "score": score,
                    "indices": indices,
                }

    if melhor is None:
        raise RuntimeError(
            "Não foi possível conectar Art. 1 ao artigo final."
        )

    return [
        candidatos[
            idx
        ]
        for idx in melhor[
            "indices"
        ]
    ]


def montar_artigos_binario(
    texto: str,
    identificador: str,
) -> tuple[
    list[dict],
    dict,
]:
    candidatos = listar_candidatos_artigos(
        texto,
        identificador,
    )

    selecionados = selecionar_sequencia(
        candidatos,
        identificador,
    )

    artigos = []

    for i, item in enumerate(
        selecionados
    ):
        inicio = item[
            "inicio"
        ]

        if (
            i + 1
            < len(
                selecionados
            )
        ):
            fim = selecionados[
                i + 1
            ][
                "inicio"
            ]

        else:
            fim = len(
                texto
            )

        corpo = texto[
            inicio:fim
        ].strip()

        if not corpo:
            continue

        artigos.append(
            {
                "artigo": item[
                    "artigo"
                ],
                "texto": (
                    corpo
                    + "\n"
                ),
                "origem": "CURRENT_BINARIO",
            }
        )

    diagnostico = {
        "candidatos": len(
            candidatos
        ),
        "selecionados": len(
            selecionados
        ),
        "descartados": (
            len(
                candidatos
            )
            - len(
                selecionados
            )
        ),
        "primeiro": (
            artigos[
                0
            ][
                "artigo"
            ]
            if artigos
            else ""
        ),
        "ultimo": (
            artigos[
                -1
            ][
                "artigo"
            ]
            if artigos
            else ""
        ),
    }

    return (
        artigos,
        diagnostico,
    )


# =============================================================================
# VALIDAÇÃO
# =============================================================================

def validar_artigos(
    identificador: str,
    artigos: list[dict],
) -> list[str]:
    problemas = []

    if not artigos:
        return [
            "lista de artigos vazia"
        ]

    labels = [
        item[
            "artigo"
        ]
        for item in artigos
    ]

    conjunto = set(
        labels
    )

    if labels[
        0
    ] != "1":
        problemas.append(
            (
                "primeiro artigo não é 1: "
                f"{labels[0]}"
            )
        )

    final = str(
        ARTIGO_FINAL[
            identificador
        ]
    )

    if labels[
        -1
    ] != final:
        problemas.append(
            (
                "último artigo selecionado não é o final esperado: "
                f"{labels[-1]} != {final}"
            )
        )

    if final not in conjunto:
        problemas.append(
            (
                "artigo final ausente: "
                f"{final}"
            )
        )

    if len(
        conjunto
    ) != len(
        labels
    ):
        problemas.append(
            "artigos duplicados na sequência final"
        )

    anterior = -1

    for rotulo in labels:
        chave = chave_artigo(
            rotulo
        )

        if chave <= anterior:
            problemas.append(
                (
                    "ordem não crescente em "
                    f"{rotulo}"
                )
            )

            break

        anterior = chave

    piso = piso_contagem(
        identificador
    )

    if len(
        artigos
    ) < piso:
        problemas.append(
            (
                "quantidade abaixo do piso conservador: "
                f"{len(artigos)} < {piso}"
            )
        )

    faltantes = [
        ancora
        for ancora in ANCORAS.get(
            identificador,
            [],
        )
        if ancora not in conjunto
    ]

    if faltantes:
        problemas.append(
            (
                "âncoras ausentes: "
                + ", ".join(
                    faltantes
                )
            )
        )

    return problemas


# =============================================================================
# OBTENÇÃO DA NORMA
# =============================================================================

def obter_norma(
    cliente: ClienteHTTP,
    item: dict,
) -> dict:
    identificador = str(
        item.get(
            "id",
            "",
        )
    ).strip()

    urns = resolver_urns(
        cliente,
        item,
    )

    tentativas = []

    for urn in urns:
        try:
            tree = obter_tree(
                cliente,
                urn,
            )

        except Exception as erro:
            tentativas.append(
                {
                    "urn": urn,
                    "metodo": "API_TREE",
                    "erro": str(
                        erro
                    ),
                }
            )

            continue

        # ---------------------------------------------------------------------
        # 1) FONTE PRINCIPAL: encoding Current / Compilação Monovigente
        # ---------------------------------------------------------------------

        current = candidatos_current(
            tree,
            urn,
        )

        if not current:
            tentativas.append(
                {
                    "urn": urn,
                    "metodo": "CURRENT_BINARIO",
                    "erro": (
                        "Nenhum encoding Current/Compilação Monovigente "
                        "em português foi localizado na raiz da norma."
                    ),
                }
            )

        melhor = None

        for candidato in current:
            try:
                (
                    dados,
                    content_type,
                    url_final,
                ) = cliente.bytes(
                    candidato[
                        "url_publica"
                    ]
                )

                texto = bytes_para_texto(
                    dados,
                    content_type,
                )

                (
                    artigos,
                    diagnostico,
                ) = montar_artigos_binario(
                    texto,
                    identificador,
                )

                problemas = validar_artigos(
                    identificador,
                    artigos,
                )

                registro = {
                    "urn": urn,
                    "metodo": "CURRENT_BINARIO",
                    "url_jsonld": candidato[
                        "url_jsonld"
                    ],
                    "url_publica": candidato[
                        "url_publica"
                    ],
                    "url_final": url_final,
                    "version": candidato[
                        "version"
                    ],
                    "name": candidato[
                        "name"
                    ],
                    "inLanguage": candidato[
                        "inLanguage"
                    ],
                    "encodingFormat": candidato[
                        "encodingFormat"
                    ],
                    "bytes": len(
                        dados
                    ),
                    "caracteres_texto": len(
                        texto
                    ),
                    "diagnostico": diagnostico,
                    "problemas": problemas,
                }

                tentativas.append(
                    registro
                )

                if problemas:
                    continue

                score = (
                    candidato[
                        "score"
                    ],
                    len(
                        artigos
                    ),
                    len(
                        dados
                    ),
                )

                if (
                    melhor is None
                    or score
                    > melhor[
                        "score"
                    ]
                ):
                    melhor = {
                        "score": score,
                        "artigos": artigos,
                        "fonte": url_final,
                        "registro": registro,
                    }

            except Exception as erro:
                tentativas.append(
                    {
                        "urn": urn,
                        "metodo": "CURRENT_BINARIO",
                        "url_jsonld": candidato[
                            "url_jsonld"
                        ],
                        "url_publica": candidato[
                            "url_publica"
                        ],
                        "version": candidato[
                            "version"
                        ],
                        "name": candidato[
                            "name"
                        ],
                        "erro": str(
                            erro
                        ),
                    }
                )

        if melhor is not None:
            return {
                "ok": True,
                "urn": urn,
                "metodo": "CURRENT_BINARIO",
                "fonte": melhor[
                    "fonte"
                ],
                "artigos": melhor[
                    "artigos"
                ],
                "tentativas": tentativas,
            }

        # ---------------------------------------------------------------------
        # 2) FALLBACK: árvore estruturada, FILTRADA pela URN da norma-alvo.
        # ---------------------------------------------------------------------

        try:
            artigos = extrair_estruturado_filtrado(
                tree,
                urn,
            )

            problemas = validar_artigos(
                identificador,
                artigos,
            )

            tentativas.append(
                {
                    "urn": urn,
                    "metodo": "ESTRUTURADO_FILTRADO",
                    "artigos": len(
                        artigos
                    ),
                    "primeiro": (
                        artigos[
                            0
                        ][
                            "artigo"
                        ]
                        if artigos
                        else ""
                    ),
                    "ultimo": (
                        artigos[
                            -1
                        ][
                            "artigo"
                        ]
                        if artigos
                        else ""
                    ),
                    "problemas": problemas,
                }
            )

            if not problemas:
                return {
                    "ok": True,
                    "urn": urn,
                    "metodo": "ESTRUTURADO_FILTRADO",
                    "fonte": (
                        NORMAS_SITE
                        + "/?urn="
                        + urn
                    ),
                    "artigos": artigos,
                    "tentativas": tentativas,
                }

        except Exception as erro:
            tentativas.append(
                {
                    "urn": urn,
                    "metodo": "ESTRUTURADO_FILTRADO",
                    "erro": str(
                        erro
                    ),
                }
            )

    # -------------------------------------------------------------------------
    # 3) FALLBACK OFICIAL: fonte_oficial do Catálogo Mestre (Planalto)
    #
    # É propositalmente executado APENAS depois de esgotar:
    #   - Current/Compilação Monovigente do normas.leg.br;
    #   - árvore estruturada filtrada por URN.
    #
    # Assim CF, CC, CPC, ECA etc. continuam usando as fontes mais estruturadas,
    # enquanto normas como o Decreto 3.048/1999 não ficam sem corpus só porque
    # o normas.leg.br não publica um encoding Current para elas.
    # -------------------------------------------------------------------------

    urn_preferida = (
        urns[
            0
        ]
        if urns
        else ""
    )

    fallback = tentar_planalto_fallback(
        cliente,
        item,
        tentativas,
        urn_preferida,
    )

    if fallback is not None:
        return fallback

    return {
        "ok": False,
        "urn": "",
        "metodo": "",
        "fonte": "",
        "artigos": [],
        "tentativas": tentativas,
    }


# =============================================================================
# PREFLIGHT
# =============================================================================

def escrever_relatorio_preflight(
    resultados: list[dict],
    catalogo_path: Path,
) -> Path:
    if PREFLIGHT_DIR.exists():
        shutil.rmtree(
            PREFLIGHT_DIR
        )

    PREFLIGHT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    aprovadas = sum(
        1
        for r in resultados
        if r[
            "ok"
        ]
    )

    linhas = [
        "LEX MACHINA",
        "PREFLIGHT DA FONTE OFICIAL V4",
        "=" * 92,
        "",
        f"GERADO EM: {agora()}",
        f"CATÁLOGO: {catalogo_path}",
        "",
        "MODO: SOMENTE TESTE DE FONTE; O MICROSD NÃO É ALTERADO.",
        "",
        (
            "CORREÇÕES V4:"
        ),
        (
            "- /api/binario/... é convertido para "
            "/api/public/binario/... antes do download."
        ),
        (
            "- artigos estruturados de outras leis são excluídos "
            "pela URN-base do legislationIdentifier."
        ),
        (
            "- cada norma precisa terminar no seu artigo final esperado."
        ),
        (
            "- a fonte principal é Current/Compilação Monovigente;"
        ),
        (
            "- se ela não existir, usa-se fonte_oficial do Catálogo Mestre "
            "somente quando ela for do domínio oficial planalto.gov.br."
        ),
        "",
        f"APROVADAS: {aprovadas}/{len(resultados)}",
        "",
        "=" * 92,
        "RESULTADOS",
        "=" * 92,
        "",
    ]

    for r in resultados:
        linhas.append(
            (
                f"[{'OK' if r['ok'] else 'FALHA'}] "
                f"{r['id']} - {r['nome']}"
            )
        )

        linhas.append(
            (
                "  Artigo final esperado: "
                f"{ARTIGO_FINAL[r['id']]}"
            )
        )

        linhas.append(
            (
                "  Piso conservador de artigos: "
                f"{piso_contagem(r['id'])}"
            )
        )

        if r[
            "ok"
        ]:
            linhas.append(
                (
                    "  Método: "
                    f"{r['metodo']}"
                )
            )

            linhas.append(
                (
                    "  URN: "
                    f"{r['urn']}"
                )
            )

            linhas.append(
                (
                    "  Fonte efetivamente baixada: "
                    f"{r['fonte']}"
                )
            )

            linhas.append(
                (
                    "  Artigos: "
                    f"{r['artigos']}"
                )
            )

            linhas.append(
                (
                    "  Primeiro: "
                    f"{r['primeiro']}"
                )
            )

            linhas.append(
                (
                    "  Último: "
                    f"{r['ultimo']}"
                )
            )

        linhas.append(
            "  Tentativas:"
        )

        for tentativa in r.get(
            "tentativas",
            [],
        ):
            linhas.append(
                (
                    "    "
                    + json.dumps(
                        tentativa,
                        ensure_ascii=False,
                    )
                )
            )

        linhas.append("")

    linhas.extend(
        [
            "=" * 92,
            "CONCLUSÃO",
            "=" * 92,
            "",
        ]
    )

    if aprovadas == len(
        resultados
    ):
        linhas.append(
            "PREFLIGHT APROVADO 9/9."
        )

        linhas.append(
            (
                "As nove normas sentinela passaram pela fonte Current, "
                "limite de artigo final, âncoras e sequência jurídica."
            )
        )

        linhas.append(
            (
                "Somente agora o mesmo arquivo pode ser executado com --full."
            )
        )

    else:
        linhas.append(
            "PREFLIGHT REPROVADO. NÃO EXECUTAR --full."
        )

    caminho = (
        PREFLIGHT_DIR
        / "RELATORIO_PREFLIGHT_V4.txt"
    )

    caminho.write_text(
        "\n".join(
            linhas
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    (
        PREFLIGHT_DIR
        / "RELATORIO_PREFLIGHT_V4.json"
    ).write_text(
        json.dumps(
            resultados,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return caminho


def executar_preflight(
    cliente: ClienteHTTP,
    itens: list[dict],
    catalogo_path: Path,
):
    mapa = {
        str(
            item.get(
                "id",
                "",
            )
        ).strip(): item
        for item in itens
    }

    resultados = []

    print()
    print(
        "LEX MACHINA - PREFLIGHT OFICIAL V3"
    )

    print(
        "=" * 78
    )

    print(
        "Nenhum arquivo do microSD será alterado."
    )

    print()

    for indice, identificador in enumerate(
        PREFLIGHT_IDS,
        start=1,
    ):
        item = mapa.get(
            identificador
        )

        if item is None:
            resultados.append(
                {
                    "ok": False,
                    "id": identificador,
                    "nome": "",
                    "tentativas": [
                        {
                            "erro": (
                                "ID ausente no catálogo."
                            )
                        }
                    ],
                }
            )

            continue

        nome = str(
            item.get(
                "nome",
                "",
            )
        )

        print(
            (
                f"[{indice}/{len(PREFLIGHT_IDS)}] "
                f"{identificador} - {nome}"
            )
        )

        resultado = obter_norma(
            cliente,
            item,
        )

        if resultado[
            "ok"
        ]:
            artigos = resultado[
                "artigos"
            ]

            primeiro = artigos[
                0
            ][
                "artigo"
            ]

            ultimo = artigos[
                -1
            ][
                "artigo"
            ]

            resultados.append(
                {
                    "ok": True,
                    "id": identificador,
                    "nome": nome,
                    "metodo": resultado[
                        "metodo"
                    ],
                    "urn": resultado[
                        "urn"
                    ],
                    "fonte": resultado[
                        "fonte"
                    ],
                    "artigos": len(
                        artigos
                    ),
                    "primeiro": primeiro,
                    "ultimo": ultimo,
                    "tentativas": resultado[
                        "tentativas"
                    ],
                }
            )

            print(
                (
                    f"  OK | {resultado['metodo']} "
                    f"| artigos={len(artigos)} "
                    f"| {primeiro} -> {ultimo}"
                )
            )

        else:
            resultados.append(
                {
                    "ok": False,
                    "id": identificador,
                    "nome": nome,
                    "tentativas": resultado[
                        "tentativas"
                    ],
                }
            )

            print(
                "  FALHA"
            )

    relatorio = escrever_relatorio_preflight(
        resultados,
        catalogo_path,
    )

    aprovado = all(
        r[
            "ok"
        ]
        for r in resultados
    )

    print()
    print(
        "=" * 78
    )

    print(
        (
            f"PREFLIGHT: "
            f"{sum(r['ok'] for r in resultados)}/"
            f"{len(resultados)}"
        )
    )

    print(
        f"Relatório: {relatorio}"
    )

    if aprovado:
        print(
            "✓ PREFLIGHT APROVADO"
        )

    else:
        print(
            "⚠ PREFLIGHT REPROVADO"
        )

    return (
        aprovado,
        resultados,
    )


# =============================================================================
# CORPUS CANÔNICO
# =============================================================================

def escrever_lei(
    pasta_leis: Path,
    identificador: str,
    artigos: list[dict],
) -> dict:
    pasta_leis.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        pasta_leis
        / f"{identificador}.TXT"
    )

    buffer = bytearray()

    registros = []

    for artigo in artigos:
        texto = (
            artigo[
                "texto"
            ].rstrip()
            + "\n\n"
        )

        dados = texto.encode(
            "utf-8"
        )

        offset = len(
            buffer
        )

        buffer.extend(
            dados
        )

        registros.append(
            {
                "artigo": artigo[
                    "artigo"
                ],
                "offset": offset,
                "tamanho": len(
                    dados
                ),
                "sha256": sha256_bytes(
                    dados
                ),
            }
        )

    caminho.write_bytes(
        bytes(
            buffer
        )
    )

    return {
        "caminho": caminho,
        "registros": registros,
        "bytes": len(
            buffer
        ),
        "sha256": sha256_bytes(
            bytes(
                buffer
            )
        ),
    }


PADRAO_INICIO_CANONICO = re.compile(
    r"^"
    r"Art(?:igo)?"
    r"\s*\.?\s*"
    r"("
        r"\d{1,3}(?:\.\d{3})+"
        r"|"
        r"\d{1,4}"
    r")"
    r"\s*"
    r"(?:º|°|o)?"
    r"(?:\s*-\s*([A-Za-z]{1,4}))?"
)


def rotulo_no_inicio(
    texto: str,
) -> str | None:
    match = PADRAO_INICIO_CANONICO.match(
        texto.lstrip()
    )

    if not match:
        return None

    return canonicalizar_artigo(
        match.group(
            1
        ),
        match.group(
            2
        ),
    )


def validar_offsets_canonicos(
    caminho: Path,
    registros: list[dict],
) -> list[str]:
    erros = []

    total = caminho.stat().st_size

    fim_anterior = 0

    with caminho.open(
        "rb"
    ) as arquivo:
        for registro in registros:
            offset = registro[
                "offset"
            ]

            tamanho = registro[
                "tamanho"
            ]

            if offset != fim_anterior:
                erros.append(
                    (
                        f"{caminho.name}: quebra de continuidade "
                        f"em {registro['artigo']}."
                    )
                )

            if (
                offset < 0
                or tamanho <= 0
                or offset
                + tamanho
                > total
            ):
                erros.append(
                    (
                        f"{caminho.name}: faixa inválida "
                        f"em {registro['artigo']}."
                    )
                )

                continue

            arquivo.seek(
                offset
            )

            dados = arquivo.read(
                tamanho
            )

            if (
                sha256_bytes(
                    dados
                )
                != registro[
                    "sha256"
                ]
            ):
                erros.append(
                    (
                        f"{caminho.name}: SHA divergente "
                        f"em {registro['artigo']}."
                    )
                )

            try:
                texto = dados.decode(
                    "utf-8",
                    errors="strict",
                )

            except UnicodeDecodeError:
                erros.append(
                    (
                        f"{caminho.name}: UTF-8 inválido "
                        f"em {registro['artigo']}."
                    )
                )

                continue

            lido = rotulo_no_inicio(
                texto
            )

            if lido != registro[
                "artigo"
            ]:
                erros.append(
                    (
                        f"{caminho.name}: esperado "
                        f"{registro['artigo']}, lido {lido}."
                    )
                )

            fim_anterior = (
                offset
                + tamanho
            )

    if (
        registros
        and fim_anterior
        != total
    ):
        erros.append(
            (
                f"{caminho.name}: índice termina em "
                f"{fim_anterior}, arquivo possui {total}."
            )
        )

    return erros


# =============================================================================
# JURISPRUDÊNCIA
# =============================================================================

def localizar_jurisprudencia(
    registro: dict,
    origem: Path,
) -> Path | None:
    arquivo = str(
        registro.get(
            "arquivo",
            "",
        )
    ).strip()

    if not arquivo:
        return None

    raizes = [
        (
            origem
            / (
                "9-CÓDIGO DE DEFESA "
                "DO CONSUMIDOR"
            )
            / "19_JURISPRUDENCIA"
        ),
        (
            origem
            / "19_JURISPRUDENCIA"
        ),
    ]

    encontrados = []

    for raiz in raizes:
        if not raiz.exists():
            continue

        encontrados.extend(
            p
            for p in raiz.rglob(
                arquivo
            )
            if p.is_file()
        )

    unicos = []

    vistos = set()

    for p in encontrados:
        chave = str(
            p.resolve()
        ).casefold()

        if chave in vistos:
            continue

        vistos.add(
            chave
        )

        unicos.append(
            p
        )

    if len(
        unicos
    ) == 1:
        return unicos[
            0
        ]

    return None


def caminho_sd(
    caminho: Path,
    origem: Path,
) -> str:
    rel = caminho.relative_to(
        origem
    )

    return (
        "/"
        + "/".join(
            rel.parts
        )
    )


# =============================================================================
# PUBLICAÇÃO FULL
# =============================================================================

def publicar_build(
    build_dir: Path,
    origem: Path,
) -> Path:
    destino = (
        origem
        / PASTA_PUBLICADA
    )

    temporario = (
        origem
        / (
            PASTA_PUBLICADA
            + "_NOVO"
        )
    )

    anterior = (
        origem
        / (
            PASTA_PUBLICADA
            + "_ANTERIOR"
        )
    )

    if temporario.exists():
        shutil.rmtree(
            temporario
        )

    shutil.copytree(
        build_dir,
        temporario,
    )

    bytes_origem = sum(
        p.stat().st_size
        for p in build_dir.rglob(
            "*"
        )
        if p.is_file()
    )

    bytes_destino = sum(
        p.stat().st_size
        for p in temporario.rglob(
            "*"
        )
        if p.is_file()
    )

    if bytes_origem != bytes_destino:
        shutil.rmtree(
            temporario,
            ignore_errors=True,
        )

        raise RuntimeError(
            (
                "Cópia para SD divergente: "
                f"{bytes_origem} != {bytes_destino}"
            )
        )

    if anterior.exists():
        shutil.rmtree(
            anterior
        )

    if destino.exists():
        os.replace(
            destino,
            anterior,
        )

    try:
        os.replace(
            temporario,
            destino,
        )

    except Exception:
        if (
            anterior.exists()
            and not destino.exists()
        ):
            os.replace(
                anterior,
                destino,
            )

        raise

    if anterior.exists():
        shutil.rmtree(
            anterior,
            ignore_errors=True,
        )

    return destino


def executar_full(
    cliente: ClienteHTTP,
    itens: list[dict],
    catalogo: dict,
    origem: Path,
):
    if FULL_BUILD_DIR.exists():
        shutil.rmtree(
            FULL_BUILD_DIR
        )

    pasta_leis = (
        FULL_BUILD_DIR
        / "LEIS"
    )

    pasta_leis.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas_normas = [
        "#LEXMACHINA|NORMAS|OFICIAL4",
        (
            "#ID|SIGLA|PRIORIDADE|RAMO|NOME|"
            "CAMINHO|ARTIGOS|BYTES|METODO"
        ),
    ]

    linhas_artigos = [
        "#LEXMACHINA|ARTIGOS|OFICIAL4",
        "#ID|ARTIGO|OFFSET|TAMANHO",
    ]

    linhas_menu = [
        "#LEXMACHINA|MENU|OFICIAL4",
        "#ORDEM|ID|SIGLA|RAMO|NOME",
    ]

    fontes = []
    resultados = []
    erros = []
    validacao_offsets = []

    total = len(
        itens
    )

    for ordem, item in enumerate(
        itens,
        start=1,
    ):
        identificador = str(
            item.get(
                "id",
                "",
            )
        ).strip()

        nome = str(
            item.get(
                "nome",
                "",
            )
        ).strip()

        print(
            (
                f"[FULL {ordem}/{total}] "
                f"{identificador} - {nome}"
            )
        )

        resultado = obter_norma(
            cliente,
            item,
        )

        if not resultado[
            "ok"
        ]:
            erros.append(
                (
                    f"{identificador}: "
                    "fonte oficial não aprovada."
                )
            )

            resultados.append(
                {
                    "ok": False,
                    "id": identificador,
                    "nome": nome,
                    "tentativas": resultado[
                        "tentativas"
                    ],
                }
            )

            print(
                "  FALHA"
            )

            continue

        escrito = escrever_lei(
            pasta_leis,
            identificador,
            resultado[
                "artigos"
            ],
        )

        erros_offset = validar_offsets_canonicos(
            escrito[
                "caminho"
            ],
            escrito[
                "registros"
            ],
        )

        if erros_offset:
            erros.extend(
                erros_offset
            )

            resultados.append(
                {
                    "ok": False,
                    "id": identificador,
                    "nome": nome,
                    "offset_erros": erros_offset,
                    "tentativas": resultado[
                        "tentativas"
                    ],
                }
            )

            print(
                "  FALHA OFFSET"
            )

            continue

        for reg in escrito[
            "registros"
        ]:
            linhas_artigos.append(
                "|".join(
                    [
                        identificador,
                        reg[
                            "artigo"
                        ],
                        str(
                            reg[
                                "offset"
                            ]
                        ),
                        str(
                            reg[
                                "tamanho"
                            ]
                        ),
                    ]
                )
            )

        sigla = SIGLAS.get(
            identificador,
            identificador[
                :8
            ].upper(),
        )

        caminho_runtime = (
            "/"
            + PASTA_PUBLICADA
            + "/LEIS/"
            + identificador
            + ".TXT"
        )

        linhas_normas.append(
            "|".join(
                [
                    identificador,
                    limpar_campo(
                        sigla
                    ),
                    limpar_campo(
                        item.get(
                            "prioridade",
                            "",
                        )
                    ),
                    limpar_campo(
                        item.get(
                            "ramo",
                            "",
                        )
                    ),
                    limpar_campo(
                        nome
                    ),
                    caminho_runtime,
                    str(
                        len(
                            resultado[
                                "artigos"
                            ]
                        )
                    ),
                    str(
                        escrito[
                            "bytes"
                        ]
                    ),
                    resultado[
                        "metodo"
                    ],
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
                    limpar_campo(
                        sigla
                    ),
                    limpar_campo(
                        item.get(
                            "ramo",
                            "",
                        )
                    ),
                    limpar_campo(
                        nome
                    ),
                ]
            )
        )

        fontes.append(
            {
                "id": identificador,
                "nome": nome,
                "urn": resultado[
                    "urn"
                ],
                "metodo": resultado[
                    "metodo"
                ],
                "fonte": resultado[
                    "fonte"
                ],
                "artigos": len(
                    resultado[
                        "artigos"
                    ]
                ),
                "artigo_final": (
                    ARTIGO_FINAL[
                        identificador
                    ]
                ),
                "sha256": escrito[
                    "sha256"
                ],
            }
        )

        resultados.append(
            {
                "ok": True,
                "id": identificador,
                "nome": nome,
                "urn": resultado[
                    "urn"
                ],
                "metodo": resultado[
                    "metodo"
                ],
                "fonte": resultado[
                    "fonte"
                ],
                "artigos": len(
                    resultado[
                        "artigos"
                    ]
                ),
                "bytes": escrito[
                    "bytes"
                ],
            }
        )

        validacao_offsets.append(
            (
                f"[OK] {identificador}: "
                f"{len(escrito['registros'])} "
                "artigos reabertos; offset, tamanho, UTF-8, "
                "rótulo e SHA-256 conferidos."
            )
        )

        print(
            (
                f"  OK | {resultado['metodo']} "
                f"| artigos={len(resultado['artigos'])}"
            )
        )

    # Jurisprudência
    registros_juris = carregar_json(
        CATALOGO_JURIS
    )

    linhas_juris = [
        "#LEXMACHINA|JURIS|OFICIAL4",
        (
            "#TRIBUNAL|TIPO|NUMERO|STATUS|"
            "ARQUIVO|RELACIONADO_A"
        ),
    ]

    juris_ok = 0

    for registro in registros_juris:
        caminho = localizar_jurisprudencia(
            registro,
            origem,
        )

        if caminho is None:
            erros.append(
                (
                    "Jurisprudência ausente/ambígua: "
                    f"{registro.get('tribunal', '')} "
                    f"{registro.get('tipo', '')} "
                    f"{registro.get('numero', '')}"
                )
            )

            continue

        relacionados = ",".join(
            limpar_campo(
                valor
            )
            for valor in registro.get(
                "relacionado_a",
                [],
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
                    caminho_sd(
                        caminho,
                        origem,
                    ),
                    relacionados,
                ]
            )
        )

        juris_ok += 1

    (
        FULL_BUILD_DIR
        / "NORMAS.IDX"
    ).write_text(
        "\n".join(
            linhas_normas
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    (
        FULL_BUILD_DIR
        / "ARTIGOS.IDX"
    ).write_text(
        "\n".join(
            linhas_artigos
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    (
        FULL_BUILD_DIR
        / "MENU.IDX"
    ).write_text(
        "\n".join(
            linhas_menu
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    (
        FULL_BUILD_DIR
        / "JURIS.IDX"
    ).write_text(
        "\n".join(
            linhas_juris
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    (
        FULL_BUILD_DIR
        / "FONTES.JSON"
    ).write_text(
        json.dumps(
            fontes,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    (
        FULL_BUILD_DIR
        / "VALIDACAO_OFFSETS.txt"
    ).write_text(
        (
            "LEX MACHINA\n"
            "VALIDAÇÃO TOTAL DE OFFSETS - OFICIAL4\n"
            + "=" * 84
            + "\n\n"
            + "\n".join(
                validacao_offsets
            )
            + "\n"
        ),
        encoding="utf-8",
        newline="\n",
    )

    normas_ok = sum(
        1
        for r in resultados
        if r[
            "ok"
        ]
    )

    artigos_total = sum(
        r.get(
            "artigos",
            0,
        )
        for r in resultados
        if r[
            "ok"
        ]
    )

    aprovado = (
        normas_ok
        == len(
            itens
        )
        and juris_ok
        == len(
            registros_juris
        )
        and not erros
    )

    relatorio = [
        "LEX MACHINA",
        "CORPUS OFICIAL V4 - RESULTADO COMPLETO",
        "=" * 92,
        "",
        f"GERADO EM: {agora()}",
        "",
        f"NORMAS: {normas_ok}/{len(itens)}",
        f"ARTIGOS: {artigos_total}",
        (
            "JURISPRUDÊNCIAS: "
            f"{juris_ok}/{len(registros_juris)}"
        ),
        f"ERROS: {len(erros)}",
        "",
        "=" * 92,
        "NORMAS",
        "=" * 92,
        "",
    ]

    for r in resultados:
        if r[
            "ok"
        ]:
            relatorio.append(
                (
                    f"[OK] {r['id']} "
                    f"| artigos={r['artigos']} "
                    f"| metodo={r['metodo']} "
                    f"| urn={r['urn']}"
                )
            )

            relatorio.append(
                (
                    f"     fonte={r['fonte']}"
                )
            )

        else:
            relatorio.append(
                (
                    f"[FALHA] {r['id']} - "
                    f"{r['nome']}"
                )
            )

            for tentativa in r.get(
                "tentativas",
                [],
            ):
                relatorio.append(
                    (
                        "     "
                        + json.dumps(
                            tentativa,
                            ensure_ascii=False,
                        )
                    )
                )

    if erros:
        relatorio.extend(
            [
                "",
                "=" * 92,
                "ERROS",
                "=" * 92,
                "",
            ]
        )

        for erro in erros:
            relatorio.append(
                f"- {erro}"
            )

    relatorio.extend(
        [
            "",
            "=" * 92,
            "CONCLUSÃO",
            "=" * 92,
            "",
            (
                "APROVADO PARA PUBLICAÇÃO."
                if aprovado
                else (
                    "NÃO APROVADO. "
                    "Nada foi publicado no microSD."
                )
            ),
        ]
    )

    (
        FULL_BUILD_DIR
        / "RELATORIO_LEXDATA_V4.txt"
    ).write_text(
        "\n".join(
            relatorio
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    meta = {
        "lex_machina": True,
        "formato": "OFICIAL4",
        "gerado_em": agora(),
        "normas_ok": normas_ok,
        "normas_total": len(
            itens
        ),
        "artigos_total": artigos_total,
        "juris_ok": juris_ok,
        "juris_total": len(
            registros_juris
        ),
        "erros": len(
            erros
        ),
    }

    (
        FULL_BUILD_DIR
        / "META.JSON"
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

    destino = None

    if aprovado:
        destino = publicar_build(
            FULL_BUILD_DIR,
            origem,
        )

    return {
        "aprovado": aprovado,
        "normas_ok": normas_ok,
        "normas_total": len(
            itens
        ),
        "artigos_total": artigos_total,
        "juris_ok": juris_ok,
        "juris_total": len(
            registros_juris
        ),
        "erros": erros,
        "destino": destino,
    }


# =============================================================================
# MAIN
# =============================================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - pipeline oficial V4."
        )
    )

    parser.add_argument(
        "origem",
        help=(
            "Raiz do microSD. Ex.: D:\\"
        ),
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help=(
            "Repete o preflight e, se 9/9, processa as 72 normas."
        ),
    )

    return parser.parse_args()


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

    (
        catalogo_path,
        catalogo,
        itens,
    ) = carregar_catalogo_mestre()

    cliente = ClienteHTTP()

    aprovado_preflight, _ = executar_preflight(
        cliente,
        itens,
        catalogo_path,
    )

    if not aprovado_preflight:
        print()
        print(
            "FULL BLOQUEADO."
        )

        print(
            "Não execute --full enquanto o preflight não estiver 9/9."
        )

        return

    if not args.full:
        print()
        print(
            "Nenhum arquivo do microSD foi alterado."
        )

        print(
            (
                "Se o RELATORIO_PREFLIGHT_V4.txt confirmar 9/9, "
                "o mesmo arquivo poderá ser executado com --full."
            )
        )

        return

    print()
    print(
        "PREFLIGHT 9/9 APROVADO."
    )

    print(
        "Iniciando processamento completo..."
    )

    print()

    resultado = executar_full(
        cliente,
        itens,
        catalogo,
        origem,
    )

    print()
    print(
        "=" * 78
    )

    print(
        (
            "Normas: "
            f"{resultado['normas_ok']}/"
            f"{resultado['normas_total']}"
        )
    )

    print(
        (
            "Artigos: "
            f"{resultado['artigos_total']}"
        )
    )

    print(
        (
            "Jurisprudências: "
            f"{resultado['juris_ok']}/"
            f"{resultado['juris_total']}"
        )
    )

    print(
        f"Erros: {len(resultado['erros'])}"
    )

    if resultado[
        "aprovado"
    ]:
        print(
            "✓ CORPUS V4 APROVADO"
        )

        print(
            (
                "Publicado em: "
                f"{resultado['destino']}"
            )
        )

    else:
        print(
            "⚠ CORPUS V3 NÃO PUBLICADO"
        )

        print(
            (
                "Diagnóstico: "
                f"{FULL_BUILD_DIR}"
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
