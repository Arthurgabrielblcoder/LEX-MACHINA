from __future__ import annotations

"""
LEX MACHINA
PIPELINE OFICIAL V2 - PREFLIGHT + CORPUS CANÔNICO

POR QUE ESTA VERSÃO EXISTE
==========================
A versão anterior tinha dois erros arquiteturais:

1) Tentava baixar https://normas.leg.br/impressao com requests.
   Essa rota é uma aplicação web que, para um cliente HTTP simples,
   devolve o shell "Please enable JavaScript...". Resultado: 0 artigos
   em praticamente todas as normas convencionais.

2) Tratava dois nós JSON-LD com o mesmo rótulo de artigo como erro fatal.
   O modelo do normas.leg.br trabalha com Work/Expression/Version e
   workExample; repetições de nós/sufixos podem existir na árvore.
   O correto é endereçar o dispositivo pelo legislationIdentifier/suffix
   e extrair o texto da versão atual (workExample), não abortar porque o
   rótulo visível apareceu duas vezes.

A V2 NÃO usa /impressao.

FONTES
======
- Senado Dados Abertos: resolve a URN Lex oficial.
- normas.leg.br /api/public/normas:
    * normas estruturadas: usa a árvore JSON-LD e os nós de artigo;
    * normas convencionais: usa os contentUrl de LegislationObject
      presentes na própria resposta JSON-LD, normalmente URLs do tipo:
      /api/public/binario/<uuid>/texto

SEGURANÇA
=========
- Por padrão roda apenas PREFLIGHT em normas sentinela.
- Não escreve nada no microSD no preflight.
- --full roda o mesmo preflight primeiro.
- O modo completo só publica a pasta no microSD se 72/72 normas e
  80/80 jurisprudências passarem.
- Nenhum TXT jurídico existente no cartão é alterado.
- Offsets são calculados apenas nos novos arquivos canônicos UTF-8.
- Todos os offsets são reabertos e verificados por SHA-256.

USO
===
1) Primeiro:
   python construir_lexdata_oficial_v2.py D:\\

2) Somente se o preflight terminar APROVADO:
   python construir_lexdata_oficial_v2.py D:\\ --full
"""

from bisect import bisect_left
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
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
    "cache_lexdata_v2"
)

PREFLIGHT_DIR = (
    Path("saida")
    / "PREFLIGHT_LEXDATA_V2"
)

FULL_BUILD_DIR = (
    Path("saida")
    / "LEXDATA_V2_BUILD"
)

PASTA_PUBLICADA = (
    "99_LEXDATA_ESP32_OFICIAL_V2_TESTE"
)

TIMEOUT = 70
MAX_TENTATIVAS = 4
PAUSA_REDE = 0.22

HEADERS_JSON = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36 "
        "LEX-MACHINA/2.0"
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

# Conjunto escolhido para cobrir os dois caminhos:
# - estruturado com duplicatas/out-of-order anteriores;
# - convencional anterior a 2017;
# - decreto;
# - casos que falharam repetidamente.
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
# ÂNCORAS DE SEGURANÇA
# =============================================================================

ANCORAS = {
    "CF88": {
        "minimo": 250,
        "artigos": [
            "1", "5", "37", "60", "250",
        ],
    },
    "CC2002": {
        "minimo": 1900,
        "artigos": [
            "1", "421", "927", "1784", "2046",
        ],
    },
    "CPC2015": {
        "minimo": 1000,
        "artigos": [
            "1", "100", "300", "500", "1000", "1072",
        ],
    },
    "CTN1966": {
        "minimo": 200,
        "artigos": [
            "1", "5", "100", "218",
        ],
    },
    "ECA1990": {
        "minimo": 250,
        "artigos": [
            "1",
            "53",
            "101",
            "190-F",
            "227-C",
            "240",
            "267",
        ],
    },
    "LEP1984": {
        "minimo": 190,
        "artigos": [
            "1", "9-A", "82", "138", "204",
        ],
    },
    "MARIA2006": {
        "minimo": 45,
        "artigos": [
            "1",
            "7",
            "10-A",
            "12-C",
            "17-A",
            "46",
        ],
    },
    "LIC2021": {
        "minimo": 180,
        "artigos": [
            "1", "50", "100", "150", "194",
        ],
    },
    "CUSTEIO1991": {
        "minimo": 95,
        "artigos": [
            "1", "20", "55", "105",
        ],
    },
    "TORTURA1997": {
        "minimo": 4,
        "artigos": [
            "1", "2", "3", "4",
        ],
    },
    "LIQFIN1974": {
        "minimo": 50,
        "artigos": [
            "1", "10", "19", "36", "50", "57",
        ],
    },
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
# ARTIGOS
# =============================================================================

PADRAO_ARTIGO_NOME = re.compile(
    r"(?i)"
    r"\bArt(?:igo)?"
    r"\s*\.?\s*"
    r"("
        r"\d{1,3}(?:\.\d{3})+"
        r"|"
        r"\d{1,4}"
    r")"
    r"\s*"
    r"(?:º|°|o)?"
    r"(-[A-Za-z]{1,4})?"
)

# Parser do binário convencional.
# É deliberadamente CASE-SENSITIVE: só "Art." / "Artigo" no início da linha.
# Referências internas "art. 50" não entram.
PADRAO_ARTIGO_BINARIO = re.compile(
    r"(?m)"
    r"^[ \t\u00a0\u2000-\u200b\u202f\u2060\ufeff]*"
    r"(?:"
        r"A\s*r\s*t"
        r"(?:\s*i\s*g\s*o)?"
    r")"
    r"\s*\.?\s*"
    r"("
        r"\d{1,3}(?:\.\d{3})+"
        r"|"
        r"\d{1,4}"
    r")"
    r"\s*"
    r"(?:º|°|o)?"
    # Sufixo deve estar colado ao número/ordinal.
    r"(-[A-Z]{1,4})?"
    r"(?=$|[\s\.,;:\)\]–—-])"
)


# =============================================================================
# UTILITÁRIOS
# =============================================================================

def agora() -> str:
    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def timestamp() -> str:
    return datetime.now().strftime(
        "%Y%m%d_%H%M%S"
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
    decomposicao = unicodedata.normalize(
        "NFKD",
        str(texto or ""),
    )

    return "".join(
        c
        for c in decomposicao
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
    )

    texto = texto.replace(
        "\r",
        "\n",
    )

    saida = []

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
                saida.append(
                    ""
                )

            vazio_anterior = True

            continue

        saida.append(
            linha
        )

        vazio_anterior = False

    return (
        "\n".join(
            saida
        ).strip()
    )


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
        sufixo = (
            sufixo_bruto
            .lstrip(
                "-"
            )
            .upper()
        )

        rotulo += (
            "-"
            + sufixo
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

    sufixo_valor = 0

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
                sufixo_valor = (
                    sufixo_valor
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
        + sufixo_valor
    )


def rotulo_apresentacao(
    rotulo: str,
) -> str:
    base = int(
        rotulo.split(
            "-",
            1,
        )[
            0
        ]
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


def extrair_rotulo_nome(
    texto: str,
) -> str | None:
    match = (
        PADRAO_ARTIGO_NOME.search(
            str(
                texto
                or ""
            )
        )
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


# =============================================================================
# CATÁLOGOS
# =============================================================================

def carregar_json(
    caminho: Path,
):
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
                "O maior catálogo disponível não possui 72 itens: "
                f"{caminho} tem {quantidade}."
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
            "tipo_lex": (
                "constituicao"
            ),
            "tipo_senado": (
                "CON"
            ),
            "numero": 1988,
            "ano": 1988,
            "urn_inicial": (
                URN_FIXOS[
                    "CF88"
                ]
            ),
        }

    match = (
        PADRAO_IDENTIFICACAO.search(
            nome
        )
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

    tipo_lex = TIPOS_LEX[
        tipo
    ]

    tipo_senado = (
        TIPOS_SENADO[
            tipo
        ]
    )

    return {
        "tipo_lex": tipo_lex,
        "tipo_senado": (
            tipo_senado
        ),
        "numero": numero,
        "ano": ano,
        "urn_inicial": (
            "urn:lex:br:federal:"
            f"{tipo_lex}:{ano};{numero}"
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
        for match in (
            PADRAO_URN.finditer(
                html_mod.unescape(
                    texto
                )
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

    if (
        f":{info['tipo_lex']}:"
        not in low
    ):
        return False

    if (
        f";{info['numero']}"
        not in low
    ):
        return False

    if (
        f":{info['ano']}"
        not in low
    ):
        return False

    return True


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

    # URN com data completa primeiro.
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


def iter_nodes(
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
            yield from iter_nodes(
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
        identificador = (
            identificador.rsplit(
                ":",
                1,
            )[
                -1
            ]
        )

    return (
        identificador
        .casefold()
        .strip()
    )


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
    suffix = str(
        suffix
        or ""
    ).strip()

    match = re.fullmatch(
        r"art"
        r"(\d+)"
        r"(?:[-_]?([A-Za-z]{1,4}))?",
        suffix,
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


def texto_atual_subarvore(
    node: dict,
) -> str:
    partes = []

    for atual in iter_nodes(
        node
    ):
        exemplo = (
            first_work_example(
                atual
            )
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


def extrair_estruturado(
    tree: dict,
) -> list[dict]:
    """
    Implementa a semântica que o cliente público br-eli-mcp
    usa para o normas.leg.br:
        - legislationIdentifier -> suffix endereçável;
        - workExample -> versão atualmente exibida;
        - artigo -> container;
        - caput/parágrafo/inciso/alínea/item -> texto descendente.

    Diferentemente da V1, repetição do mesmo suffix não é erro fatal.
    Agrupamos pelo suffix e escolhemos a ocorrência com texto atual
    mais completo.
    """

    grupos = {}

    for node in iter_nodes(
        tree
    ):
        if (
            tipo_node(
                node
            )
            != "artigo"
        ):
            continue

        suffix = suffix_identificador(
            node.get(
                "legislationIdentifier",
                "",
            )
        )

        rotulo = artigo_do_suffix(
            suffix
        )

        if rotulo is None:
            exemplo = (
                first_work_example(
                    node
                )
            )

            rotulo = (
                extrair_rotulo_nome(
                    exemplo.get(
                        "name",
                        "",
                    )
                )
            )

        if rotulo is None:
            continue

        texto = texto_atual_subarvore(
            node
        )

        if not texto:
            continue

        grupos.setdefault(
            rotulo,
            [],
        ).append(
            {
                "artigo": rotulo,
                "texto": texto,
                "suffix": suffix,
            }
        )

    artigos = []

    for rotulo, opcoes in (
        grupos.items()
    ):
        # Mesma chave jurídica aparecendo mais de uma vez na árvore:
        # preferimos o bloco com mais conteúdo textual da workExample atual.
        escolhido = max(
            opcoes,
            key=lambda item: len(
                item[
                    "texto"
                ]
            ),
        )

        artigos.append(
            {
                "artigo": rotulo,
                "texto": (
                    escolhido[
                        "texto"
                    ]
                ),
                "origem": (
                    "ESTRUTURADO"
                ),
            }
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
# contentUrl DA VERSÃO ATUAL
# =============================================================================

def url_binario_valida(
    url: str,
) -> bool:
    try:
        parsed = urlparse(
            url
        )

    except Exception:
        return False

    host = (
        parsed.netloc
        .casefold()
    )

    if not (
        host == "normas.leg.br"
        or host.endswith(
            ".normas.leg.br"
        )
    ):
        return False

    return (
        "/binario/"
        in parsed.path
        and parsed.path.endswith(
            "/texto"
        )
    )


def coletar_content_urls(
    objeto,
    prioridade: int,
    origem: str,
    saida: list[dict],
):
    if isinstance(
        objeto,
        dict,
    ):
        content_url = objeto.get(
            "contentUrl"
        )

        if (
            isinstance(
                content_url,
                str,
            )
            and url_binario_valida(
                content_url
            )
        ):
            saida.append(
                {
                    "url": content_url,
                    "prioridade": (
                        prioridade
                    ),
                    "origem": origem,
                    "name": limpar_campo(
                        objeto.get(
                            "name",
                            "",
                        )
                    ),
                    "version": limpar_campo(
                        objeto.get(
                            "version",
                            "",
                        )
                    ),
                    "encodingFormat": (
                        limpar_campo(
                            objeto.get(
                                "encodingFormat",
                                "",
                            )
                        )
                    ),
                    "legalValue": limpar_campo(
                        objeto.get(
                            "legislationLegalValue",
                            "",
                        )
                    ),
                }
            )

        # Alguns objetos usam @id diretamente para a manifestação.
        at_id = objeto.get(
            "@id"
        )

        if (
            isinstance(
                at_id,
                str,
            )
            and url_binario_valida(
                at_id
            )
        ):
            saida.append(
                {
                    "url": at_id,
                    "prioridade": (
                        prioridade - 1
                    ),
                    "origem": (
                        origem
                        + ":@id"
                    ),
                    "name": limpar_campo(
                        objeto.get(
                            "name",
                            "",
                        )
                    ),
                    "version": limpar_campo(
                        objeto.get(
                            "version",
                            "",
                        )
                    ),
                    "encodingFormat": (
                        limpar_campo(
                            objeto.get(
                                "encodingFormat",
                                "",
                            )
                        )
                    ),
                    "legalValue": limpar_campo(
                        objeto.get(
                            "legislationLegalValue",
                            "",
                        )
                    ),
                }
            )

        for chave, valor in (
            objeto.items()
        ):
            if chave in {
                "contentUrl",
                "@id",
            }:
                continue

            coletar_content_urls(
                valor,
                prioridade,
                origem,
                saida,
            )

    elif isinstance(
        objeto,
        list,
    ):
        for valor in objeto:
            coletar_content_urls(
                valor,
                prioridade,
                origem,
                saida,
            )


def candidatos_binarios_atuais(
    tree: dict,
) -> list[dict]:
    """
    Ordem de confiança:
    1) first workExample do ato consultado (versão atual)
    2) encoding do ato raiz
    3) fallback recursivo na resposta toda

    A V1 ignorava esses contentUrl e tentava fazer scraping de /impressao.
    """

    saida = []

    atual = (
        first_work_example(
            tree
        )
    )

    if atual:
        coletar_content_urls(
            atual,
            300,
            "workExample_atual",
            saida,
        )

    if "encoding" in tree:
        coletar_content_urls(
            tree.get(
                "encoding"
            ),
            200,
            "encoding_raiz",
            saida,
        )

    # Fallback: se a estrutura do JSON variar.
    coletar_content_urls(
        tree,
        100,
        "fallback_tree",
        saida,
    )

    # Dedup por URL, mantendo a maior prioridade.
    mapa = {}

    for item in saida:
        url = item[
            "url"
        ]

        anterior = mapa.get(
            url
        )

        if (
            anterior is None
            or item[
                "prioridade"
            ]
            > anterior[
                "prioridade"
            ]
        ):
            mapa[
                url
            ] = item

    candidatos = list(
        mapa.values()
    )

    # Bônus semântico para manifestações atuais/compiladas.
    for item in candidatos:
        texto_meta = normalizar_busca(
            (
                item.get(
                    "name",
                    "",
                )
                + " "
                + item.get(
                    "version",
                    "",
                )
            )
        )

        bonus = 0

        if "compil" in texto_meta:
            bonus += 80

        if "atual" in texto_meta:
            bonus += 80

        if "vigente" in texto_meta:
            bonus += 80

        item[
            "prioridade"
        ] += bonus

    candidatos.sort(
        key=lambda item: (
            item[
                "prioridade"
            ],
            item[
                "url"
            ],
        ),
        reverse=True,
    )

    return candidatos


# =============================================================================
# BINÁRIO OFICIAL
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


def bytes_para_texto_legal(
    dados: bytes,
    content_type: str,
) -> str:
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
            texto,
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


def candidatos_artigos_binario(
    texto: str,
) -> list[dict]:
    candidatos = []

    for match in (
        PADRAO_ARTIGO_BINARIO.finditer(
            texto
        )
    ):
        rotulo = canonicalizar_artigo(
            match.group(
                1
            ),
            match.group(
                2
            ),
        )

        candidatos.append(
            {
                "artigo": rotulo,
                "chave": (
                    chave_artigo(
                        rotulo
                    )
                ),
                "inicio": match.start(),
            }
        )

    return candidatos


def lis_artigos(
    candidatos: list[dict],
) -> list[dict]:
    """
    LIS O(n log n), obrigatoriamente a partir da primeira ocorrência de Art. 1.
    Em um texto legal limpo, referências internas quebradas em linha própria
    tendem a criar saltos que são descartados pela subsequência máxima.
    """

    if not candidatos:
        return []

    inicio_idx = None

    for i, item in enumerate(
        candidatos
    ):
        if item[
            "artigo"
        ] == "1":
            inicio_idx = i

            break

    if inicio_idx is None:
        return []

    base = candidatos[
        inicio_idx:
    ]

    # Art. 1 fica fixo.
    primeiro = base[
        0
    ]

    restantes = [
        item
        for item in base[
            1:
        ]
        if item[
            "chave"
        ]
        > primeiro[
            "chave"
        ]
    ]

    tails = []
    tails_idx = []
    anterior = [
        -1
    ] * len(
        restantes
    )

    for i, item in enumerate(
        restantes
    ):
        chave = item[
            "chave"
        ]

        pos = bisect_left(
            tails,
            chave,
        )

        # Strictly increasing: mesma chave substitui,
        # não aumenta comprimento.
        if pos == len(
            tails
        ):
            tails.append(
                chave
            )

            tails_idx.append(
                i
            )

        else:
            tails[
                pos
            ] = chave

            tails_idx[
                pos
            ] = i

        if pos > 0:
            anterior[
                i
            ] = tails_idx[
                pos - 1
            ]

    selecionados = [
        primeiro
    ]

    if not tails_idx:
        return selecionados

    indice = tails_idx[
        -1
    ]

    cadeia = []

    while indice >= 0:
        cadeia.append(
            restantes[
                indice
            ]
        )

        indice = anterior[
            indice
        ]

    cadeia.reverse()

    selecionados.extend(
        cadeia
    )

    return selecionados


def artigos_do_binario(
    texto: str,
) -> list[dict]:
    candidatos = (
        candidatos_artigos_binario(
            texto
        )
    )

    selecionados = lis_artigos(
        candidatos
    )

    if not selecionados:
        return []

    artigos = []

    for i, item in enumerate(
        selecionados
    ):
        inicio = item[
            "inicio"
        ]

        if (
            i
            + 1
            < len(
                selecionados
            )
        ):
            fim = (
                selecionados[
                    i + 1
                ][
                    "inicio"
                ]
            )

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
                "texto": corpo,
                "origem": "BINARIO",
            }
        )

    # Segurança final: dedup.
    unicos = {}

    for artigo in artigos:
        rotulo = artigo[
            "artigo"
        ]

        if rotulo not in unicos:
            unicos[
                rotulo
            ] = artigo

    saida = list(
        unicos.values()
    )

    saida.sort(
        key=lambda item: (
            chave_artigo(
                item[
                    "artigo"
                ]
            )
        )
    )

    return saida


# =============================================================================
# VALIDAÇÃO
# =============================================================================

def validar_lista(
    identificador: str,
    artigos: list[dict],
) -> list[str]:
    problemas = []

    if not artigos:
        return [
            "lista de artigos vazia"
        ]

    conjunto = {
        item[
            "artigo"
        ]
        for item in artigos
    }

    if "1" not in conjunto:
        problemas.append(
            "Art. 1 ausente"
        )

    if len(
        conjunto
    ) != len(
        artigos
    ):
        problemas.append(
            "artigos duplicados"
        )

    config = ANCORAS.get(
        identificador
    )

    if config:
        if len(
            artigos
        ) < config[
            "minimo"
        ]:
            problemas.append(
                (
                    "quantidade abaixo do piso: "
                    f"{len(artigos)} < "
                    f"{config['minimo']}"
                )
            )

        faltantes = [
            rotulo
            for rotulo in config[
                "artigos"
            ]
            if rotulo not in conjunto
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


def normalizar_artigos_canonicos(
    artigos: list[dict],
) -> list[dict]:
    saida = []

    for artigo in artigos:
        rotulo = artigo[
            "artigo"
        ]

        texto = normalizar_texto(
            artigo[
                "texto"
            ]
        )

        inicio_rotulo = (
            extrair_rotulo_nome(
                texto[
                    :250
                ]
            )
        )

        if (
            inicio_rotulo
            != rotulo
        ):
            texto = (
                rotulo_apresentacao(
                    rotulo
                )
                + "\n"
                + texto
            )

        saida.append(
            {
                "artigo": rotulo,
                "texto": (
                    texto.strip()
                    + "\n"
                ),
                "origem": artigo.get(
                    "origem",
                    "",
                ),
            }
        )

    saida.sort(
        key=lambda item: (
            chave_artigo(
                item[
                    "artigo"
                ]
            )
        )
    )

    return saida


# =============================================================================
# OBTER NORMA
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
        # 1) ESTRUTURADO
        # ---------------------------------------------------------------------

        try:
            artigos = (
                extrair_estruturado(
                    tree
                )
            )

            artigos = (
                normalizar_artigos_canonicos(
                    artigos
                )
            )

            problemas = validar_lista(
                identificador,
                artigos,
            )

            tentativas.append(
                {
                    "urn": urn,
                    "metodo": "ESTRUTURADO",
                    "artigos": len(
                        artigos
                    ),
                    "problemas": (
                        problemas
                    ),
                }
            )

            if not problemas:
                return {
                    "ok": True,
                    "id": identificador,
                    "urn": urn,
                    "metodo": "ESTRUTURADO",
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
                    "metodo": "ESTRUTURADO",
                    "erro": str(
                        erro
                    ),
                }
            )

        # ---------------------------------------------------------------------
        # 2) BINÁRIOS contentUrl DA PRÓPRIA API
        # ---------------------------------------------------------------------

        candidatos_bin = (
            candidatos_binarios_atuais(
                tree
            )
        )

        if not candidatos_bin:
            tentativas.append(
                {
                    "urn": urn,
                    "metodo": "BINARIO",
                    "erro": (
                        "Nenhum contentUrl /binario/.../texto "
                        "encontrado no JSON-LD."
                    ),
                }
            )

        melhor = None

        for candidato in (
            candidatos_bin
        ):
            url = candidato[
                "url"
            ]

            try:
                (
                    dados,
                    content_type,
                    url_final,
                ) = cliente.bytes(
                    url
                )

                texto = (
                    bytes_para_texto_legal(
                        dados,
                        content_type,
                    )
                )

                artigos = (
                    artigos_do_binario(
                        texto
                    )
                )

                artigos = (
                    normalizar_artigos_canonicos(
                        artigos
                    )
                )

                problemas = validar_lista(
                    identificador,
                    artigos,
                )

                registro = {
                    "urn": urn,
                    "metodo": "BINARIO",
                    "url": url_final,
                    "prioridade": (
                        candidato[
                            "prioridade"
                        ]
                    ),
                    "origem_contentUrl": (
                        candidato[
                            "origem"
                        ]
                    ),
                    "name": candidato.get(
                        "name",
                        "",
                    ),
                    "version": candidato.get(
                        "version",
                        "",
                    ),
                    "artigos": len(
                        artigos
                    ),
                    "bytes": len(
                        dados
                    ),
                    "problemas": (
                        problemas
                    ),
                }

                tentativas.append(
                    registro
                )

                if problemas:
                    continue

                # Escolha objetiva:
                # 1) prioridade do current workExample/compilação;
                # 2) maior quantidade de artigos.
                score = (
                    candidato[
                        "prioridade"
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
                        "url": (
                            url_final
                        ),
                        "registro": registro,
                    }

            except Exception as erro:
                tentativas.append(
                    {
                        "urn": urn,
                        "metodo": "BINARIO",
                        "url": url,
                        "erro": str(
                            erro
                        ),
                    }
                )

        if melhor is not None:
            return {
                "ok": True,
                "id": identificador,
                "urn": urn,
                "metodo": "BINARIO",
                "fonte": melhor[
                    "url"
                ],
                "artigos": melhor[
                    "artigos"
                ],
                "tentativas": tentativas,
            }

    return {
        "ok": False,
        "id": identificador,
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
):
    PREFLIGHT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    ok = sum(
        1
        for r in resultados
        if r[
            "ok"
        ]
    )

    linhas = [
        "LEX MACHINA",
        "PREFLIGHT DA FONTE OFICIAL V2",
        "=" * 86,
        "",
        f"GERADO EM: {agora()}",
        f"CATÁLOGO: {catalogo_path}",
        "",
        (
            "Este teste NÃO escreve no microSD."
        ),
        (
            "Ele valida o acesso correto ao JSON-LD do normas.leg.br "
            "e aos contentUrl binários oficiais."
        ),
        "",
        f"APROVADAS: {ok}/{len(resultados)}",
        "",
        "=" * 86,
        "RESULTADOS",
        "=" * 86,
        "",
    ]

    for r in resultados:
        linhas.append(
            (
                f"[{'OK' if r['ok'] else 'FALHA'}] "
                f"{r['id']} - {r['nome']}"
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
                    "  Fonte: "
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

        for t in r.get(
            "tentativas",
            []
        ):
            linhas.append(
                (
                    "    "
                    + json.dumps(
                        t,
                        ensure_ascii=False,
                    )
                )
            )

        linhas.append("")

    linhas.extend(
        [
            "=" * 86,
            "CONCLUSÃO",
            "=" * 86,
            "",
        ]
    )

    if ok == len(
        resultados
    ):
        linhas.append(
            (
                "PREFLIGHT APROVADO. O caminho de aquisição oficial "
                "funcionou para todos os casos sentinela."
            )
        )

        linhas.append(
            (
                "Agora é seguro executar o MESMO arquivo com --full."
            )
        )

    else:
        linhas.append(
            (
                "PREFLIGHT REPROVADO. NÃO executar --full."
            )
        )

        linhas.append(
            (
                "O relatório já contém URLs, métodos, contagens e "
                "problemas suficientes para diagnosticar sem testar 72 normas."
            )
        )

    caminho = (
        PREFLIGHT_DIR
        / "RELATORIO_PREFLIGHT_V2.txt"
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
        / "RELATORIO_PREFLIGHT_V2.json"
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
        "LEX MACHINA - PREFLIGHT OFICIAL V2"
    )

    print(
        "=" * 72
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
                    "primeiro": (
                        primeiro
                    ),
                    "ultimo": ultimo,
                    "tentativas": (
                        resultado[
                            "tentativas"
                        ]
                    ),
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
                    "tentativas": (
                        resultado[
                            "tentativas"
                        ]
                    ),
                }
            )

            print(
                "  FALHA"
            )

    relatorio = (
        escrever_relatorio_preflight(
            resultados,
            catalogo_path,
        )
    )

    aprovado = all(
        r[
            "ok"
        ]
        for r in resultados
    )

    print()
    print(
        "=" * 72
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
                "sha256": (
                    sha256_bytes(
                        dados
                    )
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
    r"(-[A-Za-z]{1,4})?"
)


def rotulo_no_inicio(
    texto: str,
) -> str | None:
    match = (
        PADRAO_INICIO_CANONICO.match(
            texto.lstrip()
        )
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

            if (
                lido
                != registro[
                    "artigo"
                ]
            ):
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
# FULL
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

    if (
        bytes_origem
        != bytes_destino
    ):
        shutil.rmtree(
            temporario,
            ignore_errors=True,
        )

        raise RuntimeError(
            (
                "Cópia para SD divergente: "
                f"{bytes_origem} != "
                f"{bytes_destino}"
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
        "#LEXMACHINA|NORMAS|OFICIAL2",
        (
            "#ID|SIGLA|PRIORIDADE|RAMO|NOME|"
            "CAMINHO|ARTIGOS|BYTES|METODO"
        ),
    ]

    linhas_artigos = [
        "#LEXMACHINA|ARTIGOS|OFICIAL2",
        "#ID|ARTIGO|OFFSET|TAMANHO",
    ]

    linhas_menu = [
        "#LEXMACHINA|MENU|OFICIAL2",
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
                    "tentativas": (
                        resultado[
                            "tentativas"
                        ]
                    ),
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

        erros_offset = (
            validar_offsets_canonicos(
                escrito[
                    "caminho"
                ],
                escrito[
                    "registros"
                ],
            )
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
                    "tentativas": (
                        resultado[
                            "tentativas"
                        ]
                    ),
                    "offset_erros": (
                        erros_offset
                    ),
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
                "registros reabertos e verificados."
            )
        )

        print(
            (
                f"  OK | {resultado['metodo']} "
                f"| artigos="
                f"{len(resultado['artigos'])}"
            )
        )

    # Jurisprudência
    registros_juris = carregar_json(
        CATALOGO_JURIS
    )

    linhas_juris = [
        "#LEXMACHINA|JURIS|OFICIAL2",
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

    # Grava índices no staging.
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
            "VALIDAÇÃO TOTAL DE OFFSETS - OFICIAL2\n"
            + "=" * 78
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

    relatorio = [
        "LEX MACHINA",
        "CORPUS OFICIAL V2 - RESULTADO COMPLETO",
        "=" * 86,
        "",
        f"GERADO EM: {agora()}",
        "",
        f"NORMAS: {normas_ok}/{len(itens)}",
        f"ARTIGOS: {artigos_total}",
        (
            f"JURISPRUDÊNCIAS: "
            f"{juris_ok}/{len(registros_juris)}"
        ),
        f"ERROS: {len(erros)}",
        "",
        "=" * 86,
        "NORMAS",
        "=" * 86,
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

            for t in r.get(
                "tentativas",
                [],
            ):
                relatorio.append(
                    (
                        "     "
                        + json.dumps(
                            t,
                            ensure_ascii=False,
                        )
                    )
                )

    if erros:
        relatorio.extend(
            [
                "",
                "=" * 86,
                "ERROS",
                "=" * 86,
                "",
            ]
        )

        for erro in erros:
            relatorio.append(
                f"- {erro}"
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

    relatorio.extend(
        [
            "",
            "=" * 86,
            "CONCLUSÃO",
            "=" * 86,
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
        / "RELATORIO_LEXDATA_V2.txt"
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
        "formato": "OFICIAL2",
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
            "LEX MACHINA - fonte oficial V2 "
            "com preflight e corpus canônico."
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
            "Depois de repetir e aprovar o preflight, "
            "processa as 72 normas."
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

    aprovado_preflight, _ = (
        executar_preflight(
            cliente,
            itens,
            catalogo_path,
        )
    )

    if not aprovado_preflight:
        print()
        print(
            "FULL BLOQUEADO."
        )

        print(
            "Corrija a fonte antes de testar 72 normas."
        )

        return

    if not args.full:
        print()
        print(
            "Nenhum arquivo do microSD foi alterado."
        )

        print(
            (
                "Se o relatório confirmar 9/9, "
                "execute o MESMO arquivo com --full."
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
        "=" * 72
    )

    print(
        (
            f"Normas: "
            f"{resultado['normas_ok']}/"
            f"{resultado['normas_total']}"
        )
    )

    print(
        (
            f"Artigos: "
            f"{resultado['artigos_total']}"
        )
    )

    print(
        (
            f"Jurisprudências: "
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
            "✓ CORPUS V2 APROVADO"
        )

        print(
            (
                "Publicado em: "
                f"{resultado['destino']}"
            )
        )

    else:
        print(
            "⚠ CORPUS V2 NÃO PUBLICADO"
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
