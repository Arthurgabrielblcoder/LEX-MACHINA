from datetime import datetime
from pathlib import Path
import argparse
import bisect
import json
import re
import sys
import unicodedata


# ============================================================
# LEX MACHINA - GERADOR DE ÍNDICES ESP32 V3
#
# OBJETIVO:
# - indexar as 72 normas;
# - localizar artigos mesmo quando "Art." e número estão
#   separados por quebras de linha;
# - evitar referências internas como "art. 5º da Lei...";
# - gerar offsets de BYTE compatíveis com File.seek() no ESP32;
# - preservar o formato dos índices já usado pelo projeto.
#
# ESTE SCRIPT NÃO ALTERA NENHUMA LEI DO CARTÃO.
# ============================================================


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO_MESTRE = Path(
    "catalogo_mestre_vademecum.json"
)

CATALOGO_JURIS = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_INDICES_NOME = "99_INDICES_ESP32"

ARQ_NORMAS = "NORMAS.IDX"
ARQ_ARTIGOS = "ARTIGOS.IDX"
ARQ_JURIS = "JURIS.IDX"
ARQ_MENU = "MENU.IDX"
ARQ_META = "META.JSON"

ARQ_RELATORIO = (
    "RELATORIO_INDICE_ESP32.txt"
)


# ============================================================
# CAMINHOS CANÔNICOS DOS 20 ITENS BASE
#
# Evita que o índice escolha, por engano, relatório,
# referência ou cópia secundária dentro de outra pasta.
# ============================================================

BASE_RELATIVOS = {
    "CF88": (
        "1- CONSTITUIÇÃO FEDERAL/"
        "cf.txt"
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
        "4-CÓDIGO PENAL/"
        "codigo_penal.txt"
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
        "01_CDC/"
        "cdc_lei_8078_1990.txt"
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
        "12-LEI BRASILEIRA DE INCLUSÃO "
        "DA PESSOA COM DEFICIÊNCIA/"
        "Lei Brasileira de Inclusão "
        "da Pessoa com Deficiência.txt"
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
        "Lei de Licitações e Contratos "
        "Administrativos.txt"
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


# ============================================================
# REGEX V3
#
# DIFERENÇA PRINCIPAL:
# - NÃO depende do início da linha;
# - aceita quebra de linha entre "Art." e o número;
# - aceita "Art. . 154";
# - aceita Art. 1º-A, Art. 22A, Art. 359-M-B;
# - aceita Art. 1.072.
#
# Somente "Art"/"ART" com A maiúsculo entra como candidato
# principal. Isso elimina a maior parte das referências
# internas escritas como "art. 5º".
# ============================================================

PADRAO_CANDIDATO = re.compile(
    r"(?<![A-Za-zÀ-ÿ])"
    r"(?P<token>"
        r"Art(?:igo)?"
        r"|"
        r"ART(?:IGO)?"
    r")"
    r"(?:\s*\.){0,2}"
    r"\s*"
    r"(?P<numero>"
        r"\d{1,3}(?:\.\d{3})+"
        r"|"
        r"\d{1,4}"
    r")"
)


# ============================================================
# ARGUMENTOS
# ============================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - Gerador de índices "
            "ESP32 V3"
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


def compactar(texto):
    texto = remover_acentos(
        texto
    ).casefold()

    return re.sub(
        r"[^a-z0-9]+",
        "",
        texto,
    )


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
# INVENTÁRIO
# ============================================================

def inventariar(
    origem
):
    arquivos = []

    for caminho in origem.rglob(
        "*"
    ):
        if not caminho.is_file():
            continue

        if (
            PASTA_INDICES_NOME
            in caminho.parts
        ):
            continue

        try:
            relativo = caminho.relative_to(
                origem
            )

        except ValueError:
            continue

        arquivos.append(
            {
                "absoluto": caminho,
                "relativo": relativo,
                "nome_compacto": compactar(
                    caminho.name
                ),
                "caminho_normalizado": normalizar(
                    str(
                        relativo
                    )
                ),
            }
        )

    return arquivos


# ============================================================
# LOCALIZAÇÃO DA NORMA
# ============================================================

def localizar_norma(
    item,
    arquivos,
    origem,
):
    identificador = str(
        item.get(
            "id",
            ""
        )
    ).strip()

    # --------------------------------------------------------
    # 1. Caminho canônico BASE
    # --------------------------------------------------------

    relativo_canonico = BASE_RELATIVOS.get(
        identificador
    )

    if relativo_canonico:
        caminho = (
            origem
            / Path(
                relativo_canonico
            )
        )

        if caminho.exists():
            return [
                caminho
            ]

    prioridade = str(
        item.get(
            "prioridade",
            ""
        )
    ).strip().upper()

    pasta_esperada = normalizar(
        item.get(
            "pasta_destino",
            ""
        )
    )

    nome_esperado = compactar(
        item.get(
            "arquivo_sugerido",
            ""
        )
    )

    # --------------------------------------------------------
    # 2. A / B / C:
    #    nome exato + pasta esperada
    # --------------------------------------------------------

    if prioridade != "BASE":
        encontrados = []

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
                not in arquivo[
                    "caminho_normalizado"
                ]
            ):
                continue

            encontrados.append(
                arquivo[
                    "absoluto"
                ]
            )

        return encontrados

    # --------------------------------------------------------
    # 3. Fallback BASE
    # --------------------------------------------------------

    termos = [
        normalizar(
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

    dentro_pasta = []

    encontrados = []

    for arquivo in arquivos:
        if (
            pasta_esperada
            and pasta_esperada
            not in arquivo[
                "caminho_normalizado"
            ]
        ):
            continue

        if (
            arquivo[
                "absoluto"
            ].suffix.lower()
            != ".txt"
        ):
            continue

        dentro_pasta.append(
            arquivo[
                "absoluto"
            ]
        )

        caminho_norm = arquivo[
            "caminho_normalizado"
        ]

        if any(
            termo
            and termo in caminho_norm
            for termo in termos
        ):
            encontrados.append(
                arquivo[
                    "absoluto"
                ]
            )

    if encontrados:
        return encontrados

    if len(
        dentro_pasta
    ) == 1:
        return dentro_pasta

    return []


# ============================================================
# SIGLA
# ============================================================

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

    ignoradas = {
        "LEI",
        "DECRETO",
        "DECRETO-LEI",
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

    palavras = re.findall(
        r"[A-Z]+",
        nome,
    )

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

    if filtradas:
        sigla = "".join(
            palavra[
                0
            ]
            for palavra in filtradas[
                :4
            ]
        )

        if sigla:
            return sigla[
                :8
            ]

    return identificador[
        :8
    ].upper()


# ============================================================
# LEITURA PRESERVANDO BYTES
# ============================================================

def ler_texto_e_bytes(
    caminho
):
    dados = caminho.read_bytes()

    for codificacao in (
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            texto = dados.decode(
                codificacao,
                errors="strict",
            )

            return (
                dados,
                texto,
                codificacao,
            )

        except UnicodeDecodeError:
            continue

    raise UnicodeError(
        "Não foi possível decodificar "
        f"{caminho}"
    )


# ============================================================
# SUFIXOS
# ============================================================

def parsear_sufixo(
    texto,
    fim_numero,
):
    """
    Interpreta:
        Art. 3º-A
        Art. 22A
        Art. 359-M-B
        Art. 61A.
        Art. 1 o
    """

    pos = fim_numero
    tamanho = len(
        texto
    )

    sufixos = []

    # --------------------------------------------------------
    # Sufixo grudado:
    # 22A, 61A
    # --------------------------------------------------------

    if (
        pos < tamanho
        and "A" <= texto[
            pos
        ] <= "Z"
    ):
        sufixos.append(
            texto[
                pos
            ]
        )

        return tuple(
            sufixos
        )

    # --------------------------------------------------------
    # Espaços
    # --------------------------------------------------------

    cursor = pos

    while (
        cursor < tamanho
        and texto[
            cursor
        ].isspace()
    ):
        cursor += 1

    # --------------------------------------------------------
    # Ordinal º / ° / o
    # --------------------------------------------------------

    if (
        cursor < tamanho
        and texto[
            cursor
        ] in (
            "º",
            "°",
        )
    ):
        cursor += 1

    elif (
        cursor < tamanho
        and texto[
            cursor
        ] == "o"
    ):
        proximo = (
            texto[
                cursor + 1
            ]
            if (
                cursor + 1
                < tamanho
            )
            else ""
        )

        if (
            not proximo
            or proximo.isspace()
            or proximo
            in ".-–—,;:"
        ):
            cursor += 1

    # --------------------------------------------------------
    # Ponto após o ordinal/número
    # --------------------------------------------------------

    while (
        cursor < tamanho
        and texto[
            cursor
        ].isspace()
    ):
        cursor += 1

    if (
        cursor < tamanho
        and texto[
            cursor
        ] == "."
    ):
        cursor += 1

    while (
        cursor < tamanho
        and texto[
            cursor
        ].isspace()
    ):
        cursor += 1

    # --------------------------------------------------------
    # -A / -M-B
    # --------------------------------------------------------

    if (
        cursor < tamanho
        and texto[
            cursor
        ] in "-–—"
    ):
        cursor += 1

        while cursor < tamanho:
            while (
                cursor < tamanho
                and texto[
                    cursor
                ].isspace()
            ):
                cursor += 1

            if (
                cursor < tamanho
                and "A" <= texto[
                    cursor
                ] <= "Z"
            ):
                sufixos.append(
                    texto[
                        cursor
                    ]
                )

                cursor += 1

            else:
                break

            while (
                cursor < tamanho
                and texto[
                    cursor
                ].isspace()
            ):
                cursor += 1

            if (
                cursor < tamanho
                and texto[
                    cursor
                ] in "-–—"
            ):
                cursor += 1
                continue

            break

    return tuple(
        sufixos
    )


def artigo_texto(
    base,
    sufixo
):
    resultado = str(
        base
    )

    if sufixo:
        resultado += (
            "-"
            + "-".join(
                sufixo
            )
        )

    return resultado


# ============================================================
# CANDIDATOS V3
# ============================================================

def encontrar_candidatos(
    texto
):
    candidatos = []

    for match in (
        PADRAO_CANDIDATO.finditer(
            texto
        )
    ):
        numero_bruto = match.group(
            "numero"
        )

        try:
            base = int(
                numero_bruto.replace(
                    ".",
                    "",
                )
            )

        except ValueError:
            continue

        if (
            base < 1
            or base > 9999
        ):
            continue

        sufixo = parsear_sufixo(
            texto,
            match.end(
                "numero"
            ),
        )

        inicio = match.start()

        # ----------------------------------------------------
        # Bônus estrutural:
        # começa no início físico da linha.
        # ----------------------------------------------------

        inicio_linha = (
            texto.rfind(
                "\n",
                0,
                inicio,
            )
            + 1
        )

        antes_na_linha = texto[
            inicio_linha:
            inicio
        ]

        estrutural = (
            3
            if not antes_na_linha.strip()
            else 0
        )

        candidatos.append(
            {
                "base": base,
                "sufixo": sufixo,
                "chave": (
                    base,
                    sufixo,
                ),
                "artigo": artigo_texto(
                    base,
                    sufixo,
                ),
                "inicio_char": inicio,
                "fim_match_char": (
                    match.end()
                ),
                "estrutural": estrutural,
                "texto_match": (
                    match.group(
                        0
                    )
                ),
            }
        )

    return candidatos


# ============================================================
# CADEIA JURÍDICA PRINCIPAL
#
# Dynamic Programming:
# privilegia 1 -> 2 -> 3 -> ...
# e artigos inseridos 3-A, 3-B etc.
#
# Referências internas podem até ter "Art." maiúsculo,
# mas normalmente quebram a progressão principal.
# ============================================================

def pontuacao_transicao(
    anterior,
    atual
):
    gap = (
        atual[
            "base"
        ]
        - anterior[
            "base"
        ]
    )

    if gap < 0:
        return None

    if not (
        anterior[
            "chave"
        ]
        < atual[
            "chave"
        ]
    ):
        return None

    # Mesmo número, novo sufixo:
    # 3 -> 3-A -> 3-B
    if gap == 0:
        return 10

    # Sequência natural
    if gap == 1:
        return 12

    # Pequenos saltos por revogação/omissão
    if gap <= 3:
        return 6 - gap

    if gap <= 10:
        return 1

    if gap <= 50:
        return -4

    return -14


def selecionar_cadeia_principal(
    candidatos
):
    if not candidatos:
        return []

    total = len(
        candidatos
    )

    pontuacoes = [
        -10**9
        for _ in range(
            total
        )
    ]

    anteriores = [
        -1
        for _ in range(
            total
        )
    ]

    for i, atual in enumerate(
        candidatos
    ):
        base = atual[
            "base"
        ]

        # Começar pelo art. 1 é fortemente preferido.
        if base == 1:
            inicio = 25

        else:
            inicio = (
                -25
                - min(
                    base,
                    60,
                )
            )

        pontuacoes[
            i
        ] = (
            inicio
            + atual[
                "estrutural"
            ]
        )

        for j in range(
            i
        ):
            anterior = candidatos[
                j
            ]

            transicao = (
                pontuacao_transicao(
                    anterior,
                    atual,
                )
            )

            if transicao is None:
                continue

            proposta = (
                pontuacoes[
                    j
                ]
                + transicao
                + atual[
                    "estrutural"
                ]
            )

            if (
                proposta
                > pontuacoes[
                    i
                ]
            ):
                pontuacoes[
                    i
                ] = proposta

                anteriores[
                    i
                ] = j

    # Pequeno bônus para cadeias que chegam mais longe
    melhor = max(
        range(
            total
        ),
        key=lambda indice: (
            pontuacoes[
                indice
            ]
            + min(
                candidatos[
                    indice
                ][
                    "base"
                ],
                4000,
            )
            * 0.001
        ),
    )

    cadeia = []

    while melhor != -1:
        cadeia.append(
            candidatos[
                melhor
            ]
        )

        melhor = anteriores[
            melhor
        ]

    cadeia.reverse()

    return cadeia


# ============================================================
# CHAR OFFSET -> BYTE OFFSET
# ============================================================

def converter_offsets_bytes(
    texto,
    codificacao,
    cadeia,
    tamanho_bytes,
):
    if not cadeia:
        return []

    resultados = []

    char_anterior = 0
    byte_anterior = 0

    for item in cadeia:
        inicio_char = item[
            "inicio_char"
        ]

        trecho = texto[
            char_anterior:
            inicio_char
        ]

        byte_anterior += len(
            trecho.encode(
                codificacao
            )
        )

        novo = dict(
            item
        )

        novo[
            "offset"
        ] = byte_anterior

        resultados.append(
            novo
        )

        char_anterior = (
            inicio_char
        )

    for indice, item in enumerate(
        resultados
    ):
        if (
            indice + 1
            < len(
                resultados
            )
        ):
            fim = resultados[
                indice + 1
            ][
                "offset"
            ]

        else:
            fim = tamanho_bytes

        item[
            "tamanho"
        ] = max(
            0,
            fim
            - item[
                "offset"
            ],
        )

    return resultados


# ============================================================
# EXTRAÇÃO V3
# ============================================================

def extrair_artigos_v3(
    caminho
):
    (
        dados,
        texto,
        codificacao,
    ) = ler_texto_e_bytes(
        caminho
    )

    candidatos = encontrar_candidatos(
        texto
    )

    cadeia = selecionar_cadeia_principal(
        candidatos
    )

    artigos = converter_offsets_bytes(
        texto,
        codificacao,
        cadeia,
        len(
            dados
        ),
    )

    bases = {
        item[
            "base"
        ]
        for item in artigos
    }

    max_base = (
        max(
            bases
        )
        if bases
        else 0
    )

    cobertura = (
        len(
            bases
        )
        / max_base
        if max_base
        else 0.0
    )

    return {
        "artigos": artigos,
        "candidatos": len(
            candidatos
        ),
        "selecionados": len(
            artigos
        ),
        "descartados": (
            len(
                candidatos
            )
            - len(
                artigos
            )
        ),
        "bases_unicas": len(
            bases
        ),
        "max_base": max_base,
        "cobertura": cobertura,
        "bytes": len(
            dados
        ),
        "codificacao": codificacao,
    }


# ============================================================
# VALIDAÇÃO DA NORMA
# ============================================================

def validar_extracao(
    item,
    diagnostico
):
    alertas = []

    artigos = diagnostico[
        "artigos"
    ]

    if not artigos:
        return [
            (
                "nenhum artigo foi identificado"
            )
        ]

    primeiro = artigos[
        0
    ][
        "base"
    ]

    if primeiro != 1:
        alertas.append(
            (
                "cadeia não começa no art. 1 "
                f"(começa no art. {primeiro})"
            )
        )

    max_base = diagnostico[
        "max_base"
    ]

    cobertura = diagnostico[
        "cobertura"
    ]

    # Para normas minimamente extensas,
    # uma cobertura muito baixa é suspeita.
    if (
        max_base >= 20
        and cobertura < 0.60
    ):
        alertas.append(
            (
                "cobertura numérica baixa: "
                f"{cobertura:.3f}"
            )
        )

    if (
        diagnostico[
            "bytes"
        ] > 20000
        and diagnostico[
            "selecionados"
        ] < 10
    ):
        alertas.append(
            (
                "arquivo grande com poucos "
                "artigos selecionados"
            )
        )

    return alertas


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
        return []

    raiz = (
        origem
        / "9-CÓDIGO DE DEFESA DO CONSUMIDOR"
        / "19_JURISPRUDENCIA"
    )

    if not raiz.exists():
        raiz = (
            origem
            / "19_JURISPRUDENCIA"
        )

    if not raiz.exists():
        return []

    return [
        caminho
        for caminho in raiz.rglob(
            arquivo
        )
        if caminho.is_file()
    ]


# ============================================================
# GERAR ÍNDICES
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

    arquivos = inventariar(
        origem
    )

    linhas_normas = [
        "#LEXMACHINA|NORMAS|3",
        (
            "#ID|SIGLA|PRIORIDADE|RAMO|NOME|"
            "CAMINHO|ARTIGOS|BYTES"
        ),
    ]

    linhas_artigos = [
        "#LEXMACHINA|ARTIGOS|3",
        "#ID|ARTIGO|OFFSET|TAMANHO",
    ]

    linhas_menu = [
        "#LEXMACHINA|MENU|3",
        "#ORDEM|ID|SIGLA|RAMO|NOME",
    ]

    linhas_juris = [
        "#LEXMACHINA|JURIS|3",
        (
            "#TRIBUNAL|TIPO|NUMERO|STATUS|"
            "ARQUIVO|RELACIONADO_A"
        ),
    ]

    relatorio = [
        "LEX MACHINA",
        (
            "GERAÇÃO DE ÍNDICES PARA "
            "ESP32 - VERSÃO 3"
        ),
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        f"ORIGEM: {origem}",
        (
            "VERSÃO DO CATÁLOGO: "
            f"{catalogo_mestre.get('versao', '')}"
        ),
        "",
    ]

    total_normas = 0
    total_artigos = 0
    total_candidatos = 0
    total_descartados = 0
    total_juris = 0

    erros = []
    alertas = []

    diagnosticos = []

    # --------------------------------------------------------
    # NORMAS
    # --------------------------------------------------------

    for ordem, item in enumerate(
        itens_mestre,
        start=1,
    ):
        encontrados = localizar_norma(
            item,
            arquivos,
            origem,
        )

        if not encontrados:
            erros.append(
                (
                    "Norma não encontrada: "
                    f"{item.get('nome', '')}"
                )
            )
            continue

        caminho = encontrados[
            0
        ]

        try:
            diagnostico = (
                extrair_artigos_v3(
                    caminho
                )
            )

        except Exception as erro:
            erros.append(
                (
                    f"{item.get('nome', '')}: "
                    f"{erro}"
                )
            )
            continue

        alertas_norma = validar_extracao(
            item,
            diagnostico,
        )

        for alerta in alertas_norma:
            alertas.append(
                (
                    f"{item.get('nome', '')}: "
                    f"{alerta}"
                )
            )

        identificador = limpar_campo(
            item.get(
                "id",
                "",
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

        nome = limpar_campo(
            item.get(
                "nome",
                "",
            )
        )

        caminho_sd = caminho_esp32(
            caminho,
            origem,
        )

        artigos = diagnostico[
            "artigos"
        ]

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
                        diagnostico[
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

        diagnosticos.append(
            {
                "id": identificador,
                "nome": nome,
                "arquivo": caminho_sd,
                "artigos": (
                    diagnostico[
                        "selecionados"
                    ]
                ),
                "candidatos": (
                    diagnostico[
                        "candidatos"
                    ]
                ),
                "descartados": (
                    diagnostico[
                        "descartados"
                    ]
                ),
                "bases_unicas": (
                    diagnostico[
                        "bases_unicas"
                    ]
                ),
                "max_base": (
                    diagnostico[
                        "max_base"
                    ]
                ),
                "cobertura": (
                    diagnostico[
                        "cobertura"
                    ]
                ),
                "codificacao": (
                    diagnostico[
                        "codificacao"
                    ]
                ),
                "alertas": (
                    alertas_norma
                ),
            }
        )

        total_normas += 1
        total_artigos += len(
            artigos
        )

        total_candidatos += (
            diagnostico[
                "candidatos"
            ]
        )

        total_descartados += (
            diagnostico[
                "descartados"
            ]
        )

    # --------------------------------------------------------
    # JURISPRUDÊNCIA
    # --------------------------------------------------------

    for registro in registros_juris:
        encontrados = localizar_jurisprudencia(
            registro,
            origem,
        )

        if not encontrados:
            erros.append(
                (
                    "Jurisprudência não encontrada: "
                    f"{registro.get('tribunal', '')} "
                    f"{registro.get('tipo', '')} "
                    f"{registro.get('numero', '')}"
                )
            )
            continue

        caminho = encontrados[
            0
        ]

        relacionados = ",".join(
            limpar_campo(
                valor
            )
            for valor in registro.get(
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
    # SALVAR ÍNDICES
    # --------------------------------------------------------

    arquivos_saida = {
        ARQ_NORMAS: linhas_normas,
        ARQ_ARTIGOS: linhas_artigos,
        ARQ_JURIS: linhas_juris,
        ARQ_MENU: linhas_menu,
    }

    for nome_arquivo, linhas in (
        arquivos_saida.items()
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
        "formato_indice": 3,
        "gerado_em": (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ),
        "versao_catalogo": (
            catalogo_mestre.get(
                "versao",
                "",
            )
        ),
        "normas": total_normas,
        "artigos": total_artigos,
        "candidatos": (
            total_candidatos
        ),
        "descartados": (
            total_descartados
        ),
        "jurisprudencias": (
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
        },
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

    # --------------------------------------------------------
    # RELATÓRIO
    # --------------------------------------------------------

    relatorio.extend(
        [
            (
                f"NORMAS INDEXADAS: "
                f"{total_normas}"
            ),
            (
                f"ARTIGOS INDEXADOS: "
                f"{total_artigos}"
            ),
            (
                "CANDIDATOS ENCONTRADOS: "
                f"{total_candidatos}"
            ),
            (
                "CANDIDATOS DESCARTADOS: "
                f"{total_descartados}"
            ),
            (
                "JURISPRUDÊNCIAS INDEXADAS: "
                f"{total_juris}"
            ),
            f"ERROS: {len(erros)}",
            f"ALERTAS: {len(alertas)}",
            "",
            "=" * 78,
            "DIAGNÓSTICO POR NORMA",
            "=" * 78,
            "",
        ]
    )

    for item in diagnosticos:
        relatorio.append(
            (
                f"- {item['id']} "
                f"| artigos={item['artigos']} "
                f"| candidatos={item['candidatos']} "
                f"| descartados={item['descartados']} "
                f"| max={item['max_base']} "
                f"| cobertura="
                f"{item['cobertura']:.4f} "
                f"| {item['nome']}"
            )
        )

    if erros:
        relatorio.extend(
            [
                "",
                "ERROS",
                "-" * 78,
            ]
        )

        for erro in erros:
            relatorio.append(
                f"- {erro}"
            )

    if alertas:
        relatorio.extend(
            [
                "",
                "ALERTAS",
                "-" * 78,
            ]
        )

        for alerta in alertas:
            relatorio.append(
                f"- {alerta}"
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
        "normas": total_normas,
        "artigos": total_artigos,
        "candidatos": (
            total_candidatos
        ),
        "descartados": (
            total_descartados
        ),
        "juris": total_juris,
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

    (
        catalogo_mestre,
        itens_mestre,
    ) = carregar_catalogo_mestre()

    registros_juris = (
        carregar_catalogo_juris()
    )

    print()
    print(
        "LEX MACHINA - "
        "GERADOR DE ÍNDICES ESP32 V3"
    )

    print(
        "=" * 60
    )

    print(
        f"Origem: {origem}"
    )

    print(
        "Normas no catálogo: "
        f"{len(itens_mestre)}"
    )

    print(
        "Jurisprudências no catálogo: "
        f"{len(registros_juris)}"
    )

    print()

    resultado = gerar_indices(
        origem,
        catalogo_mestre,
        itens_mestre,
        registros_juris,
    )

    print(
        "=" * 60
    )

    print(
        "ÍNDICES V3 GERADOS"
    )

    print(
        f"Normas: {resultado['normas']}"
    )

    print(
        f"Artigos: {resultado['artigos']}"
    )

    print(
        "Candidatos encontrados: "
        f"{resultado['candidatos']}"
    )

    print(
        "Candidatos descartados: "
        f"{resultado['descartados']}"
    )

    print(
        "Jurisprudências: "
        f"{resultado['juris']}"
    )

    print(
        f"Erros: {len(resultado['erros'])}"
    )

    print(
        f"Alertas: {len(resultado['alertas'])}"
    )

    print()

    print(
        f"Pasta: {resultado['pasta']}"
    )

    print()

    if (
        not resultado[
            "erros"
        ]
        and not resultado[
            "alertas"
        ]
    ):
        print(
            "✓ ÍNDICE V3 GERADO "
            "SEM PENDÊNCIAS"
        )

    elif not resultado[
        "erros"
    ]:
        print(
            "✓ ÍNDICE V3 GERADO, "
            "COM ALERTAS PARA REVISÃO"
        )

    else:
        print(
            "⚠ ÍNDICE V3 GERADO, "
            "MAS EXISTEM ERROS"
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
