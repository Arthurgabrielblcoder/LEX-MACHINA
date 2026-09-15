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
# GERADOR DE ÍNDICES ESP32 V4 - MODO TESTE SEGURO
#
# OBJETIVO
# -------
# Gerar índices de acesso direto por byte para o ESP32-S3,
# SEM alterar nenhum arquivo jurídico do cartão e SEM
# sobrescrever os índices antigos.
#
# Saída:
#   D:\99_INDICES_ESP32_V4_TESTE\
#
# Arquivos:
#   NORMAS.IDX
#   ARTIGOS.IDX
#   JURIS.IDX
#   MENU.IDX
#   META.JSON
#   RELATORIO_INDICE_ESP32_V4.txt
#   AMOSTRAS_OFFSETS_V4.txt
#
# MELHORIAS SOBRE AS VERSÕES ANTERIORES
# -------------------------------------
# 1) aceita artigos com milhares:
#       Art. 1.001  -> artigo 1001
#       Art. 2.046  -> artigo 2046
#
# 2) aceita artigos com letras:
#       Art. 11-A
#       Art. 190-F
#       Art. 227-C
#
# 3) só considera candidatos que começam uma linha;
#
# 4) seleciona a sequência jurídica principal por programação
#    dinâmica, favorecendo 1, 2, 3... e artigos inseridos;
#
# 5) referências soltas a artigos de outras leis recebem
#    penalidade e tendem a ser descartadas;
#
# 6) CF, Código Civil e ECA possuem testes estruturais
#    obrigatórios, baseados nos arquivos já validados;
#
# 7) cada offset é reaberto no arquivo bruto e revalidado;
#
# 8) os índices são gravados em pasta de TESTE.
# ============================================================


CATALOGO_MESTRE = Path(
    "catalogo_mestre_vademecum.json"
)

CATALOGO_JURIS = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_INDICES_NOME = (
    "99_INDICES_ESP32_V4_TESTE"
)

ARQ_NORMAS = "NORMAS.IDX"
ARQ_ARTIGOS = "ARTIGOS.IDX"
ARQ_JURIS = "JURIS.IDX"
ARQ_MENU = "MENU.IDX"
ARQ_META = "META.JSON"

ARQ_RELATORIO = (
    "RELATORIO_INDICE_ESP32_V4.txt"
)

ARQ_AMOSTRAS = (
    "AMOSTRAS_OFFSETS_V4.txt"
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
    "ECA1990": [
        "1",
        "53",
        "101",
        "190-F",
        "227-C",
        "240",
        "267",
    ],
    "CDC1990": [
        "1",
        "6",
        "14",
        "39",
        "51",
        "119",
    ],
    "MARIA2006": [
        "1",
        "7",
        "10-A",
        "12-C",
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
# REGEX DE CABEÇALHO DE ARTIGO EM BYTES
#
# Exemplos aceitos:
#   Art. 1º
#   Art. 10-A.
#   Art 190-F
#   Art. 1.001.
#   Art. 2.046
#
# A palavra Art./Artigo precisa estar no começo da linha.
# ============================================================

PADRAO_ARTIGO_BYTES = re.compile(
    rb"(?im)"
    rb"^[ \t]*"
    rb"(?:art\.?|artigo)"
    rb"[ \t]*"
    rb"("
        rb"\d{1,3}(?:\.\d{3})+"
        rb"|"
        rb"\d{1,4}"
    rb")"
    rb"[ \t]*"
    rb"(?:"
        rb"\xc2\xba"
        rb"|"
        rb"\xc2\xb0"
        rb"|"
        rb"\xba"
        rb"|"
        rb"\xb0"
        rb"|"
        rb"o"
    rb")?"
    rb"[ \t]*"
    rb"(?:"
        rb"-"
        rb"[ \t]*"
        rb"([A-Za-z]{1,5})"
    rb")?"
    rb"[ \t]*"
    rb"(?:[.]|:|-)?"
)


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


def extrair_linha_bytes(
    dados,
    inicio,
):
    fim = dados.find(
        b"\n",
        inicio,
    )

    if fim < 0:
        fim = len(
            dados
        )

    return dados[
        inicio:fim
    ]


def decodificar_trecho(
    dados
):
    for encoding in (
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            return dados.decode(
                encoding
            )
        except UnicodeDecodeError:
            continue

    return dados.decode(
        "utf-8",
        errors="replace",
    )


def pontuar_candidato(
    dados,
    match,
    numero,
    sufixo,
):
    """
    Pontuação local do candidato.

    O corpo real de um artigo normalmente possui texto depois
    do cabeçalho. Referências soltas, links ou linhas muito
    curtas recebem menos pontos.
    """

    linha = extrair_linha_bytes(
        dados,
        match.start(),
    )

    linha_texto = decodificar_trecho(
        linha
    )

    resto_bytes = linha[
        match.end()
        - match.start():
    ]

    resto = decodificar_trecho(
        resto_bytes
    ).strip()

    pontos = 3.0

    if len(
        resto
    ) >= 20:
        pontos += 2.0

    elif len(
        resto
    ) >= 5:
        pontos += 1.0

    else:
        pontos -= 1.0

    resto_norm = normalizar(
        resto
    )

    referencias_suspeitas = (
        "da lei ",
        "do codigo ",
        "da constituicao ",
        "do decreto ",
        "da lei complementar ",
    )

    if any(
        resto_norm.startswith(
            trecho
        )
        for trecho in referencias_suspeitas
    ):
        pontos -= 3.0

    if int(
        numero
    ) == 1:
        pontos += 1.0

    if sufixo:
        pontos += 0.25

    return (
        pontos,
        linha_texto,
    )


def listar_candidatos_artigo(
    dados
):
    candidatos = []

    for match in (
        PADRAO_ARTIGO_BYTES.finditer(
            dados
        )
    ):
        bruto = (
            match.group(
                1
            )
            .decode(
                "ascii",
                errors="ignore",
            )
        )

        numero = bruto.replace(
            ".",
            "",
        )

        try:
            numero_int = int(
                numero
            )
        except ValueError:
            continue

        if not (
            1
            <= numero_int
            <= 9999
        ):
            continue

        sufixo = ""

        if match.group(
            2
        ):
            sufixo = (
                match.group(
                    2
                )
                .decode(
                    "ascii",
                    errors="ignore",
                )
                .upper()
            )

        (
            pontos,
            linha,
        ) = pontuar_candidato(
            dados,
            match,
            numero,
            sufixo,
        )

        candidatos.append(
            {
                "artigo": formatar_artigo(
                    numero,
                    sufixo,
                ),
                "numero": numero_int,
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
                "offset": match.start(),
                "fim_cabecalho": (
                    match.end()
                ),
                "pontos_local": pontos,
                "linha": linha[
                    :500
                ],
            }
        )

    return candidatos


# ============================================================
# SEQUÊNCIA JURÍDICA PRINCIPAL
# ============================================================

def pontuar_transicao(
    anterior,
    atual,
):
    num_a = anterior[
        "numero"
    ]

    num_b = atual[
        "numero"
    ]

    suf_a = anterior[
        "sufixo_valor"
    ]

    suf_b = atual[
        "sufixo_valor"
    ]

    if atual[
        "chave"
    ] <= anterior[
        "chave"
    ]:
        return None

    distancia_bytes = (
        atual[
            "offset"
        ]
        - anterior[
            "offset"
        ]
    )

    # Mesmo artigo-base, com letra inserida:
    # 10 -> 10-A -> 10-B
    if num_b == num_a:
        delta_suf = (
            suf_b
            - suf_a
        )

        if delta_suf == 1:
            pontos = 14.0

        elif (
            delta_suf > 1
            and delta_suf <= 4
        ):
            pontos = 7.0

        else:
            pontos = 1.0

    else:
        delta = (
            num_b
            - num_a
        )

        if delta == 1:
            pontos = 16.0

        elif delta == 2:
            pontos = 8.0

        elif delta <= 5:
            pontos = 4.0

        elif delta <= 20:
            pontos = 0.0

        elif delta <= 100:
            pontos = -6.0

        else:
            pontos = -18.0

    # Uma distância enorme entre "artigos consecutivos"
    # é indício de referência externa ou rodapé.
    if distancia_bytes > 100_000:
        pontos -= 10.0

    elif distancia_bytes > 50_000:
        pontos -= 5.0

    return pontos


def selecionar_sequencia_principal(
    candidatos
):
    """
    Programação dinâmica.

    Diferente da simples LIS, esta função valoriza fortemente
    transições jurídicas naturais (1->2, 10->10-A, 10-A->11)
    e penaliza grandes saltos que normalmente são referências
    a outras normas.
    """

    if not candidatos:
        return []

    n = len(
        candidatos
    )

    score = [
        -10**18
    ] * n

    anterior_idx = [
        -1
    ] * n

    comprimento = [
        1
    ] * n

    for i, candidato in enumerate(
        candidatos
    ):
        numero = candidato[
            "numero"
        ]

        # O corpo principal quase sempre começa em Art. 1.
        # Permite outros inícios, mas com forte desvantagem.
        if numero == 1:
            score[
                i
            ] = (
                50.0
                + candidato[
                    "pontos_local"
                ]
            )

        else:
            score[
                i
            ] = (
                candidato[
                    "pontos_local"
                ]
                - min(
                    40.0,
                    float(
                        numero
                    )
                    / 4.0,
                )
            )

        for j in range(
            i
        ):
            transicao = pontuar_transicao(
                candidatos[
                    j
                ],
                candidato,
            )

            if transicao is None:
                continue

            novo_score = (
                score[
                    j
                ]
                + transicao
                + candidato[
                    "pontos_local"
                ]
                + 1.5
            )

            novo_comprimento = (
                comprimento[
                    j
                ]
                + 1
            )

            if (
                novo_score
                > score[
                    i
                ]
                + 1e-9
            ):
                score[
                    i
                ] = novo_score

                anterior_idx[
                    i
                ] = j

                comprimento[
                    i
                ] = novo_comprimento

            elif (
                abs(
                    novo_score
                    - score[
                        i
                    ]
                )
                <= 1e-9
                and novo_comprimento
                > comprimento[
                    i
                ]
            ):
                anterior_idx[
                    i
                ] = j

                comprimento[
                    i
                ] = novo_comprimento

    # Escolha do final:
    # favorece score e, em empate aproximado, a cadeia maior.
    melhor = max(
        range(
            n
        ),
        key=lambda indice: (
            score[
                indice
            ],
            comprimento[
                indice
            ],
        ),
    )

    selecionados = []

    atual = melhor

    while atual >= 0:
        selecionados.append(
            candidatos[
                atual
            ]
        )

        atual = anterior_idx[
            atual
        ]

    selecionados.reverse()

    return selecionados


# ============================================================
# CORTE ESPECIAL DE FINAL PARA AS 3 NORMAS VALIDADA
# ============================================================

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

    indice_final = None

    for indice, item in enumerate(
        selecionados
    ):
        if item[
            "artigo"
        ] == final:
            indice_final = indice

    if indice_final is None:
        return selecionados

    return selecionados[
        :indice_final + 1
    ]


# ============================================================
# OFFSETS / TAMANHOS
# ============================================================

def montar_artigos(
    dados,
    selecionados,
):
    artigos = []

    for indice, item in enumerate(
        selecionados
    ):
        inicio = item[
            "offset"
        ]

        if (
            indice
            + 1
            < len(
                selecionados
            )
        ):
            fim = (
                selecionados[
                    indice
                    + 1
                ][
                    "offset"
                ]
            )

        else:
            fim = len(
                dados
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
            }
        )

    return artigos


def extrair_artigos_bytes(
    caminho,
    identificador,
):
    dados = caminho.read_bytes()

    candidatos = (
        listar_candidatos_artigo(
            dados
        )
    )

    selecionados = (
        selecionar_sequencia_principal(
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
        "artigos": artigos,
        "candidatos_lista": candidatos,
        "selecionados_lista": selecionados,
        "candidatos": len(
            candidatos
        ),
        "descartados": descartados,
        "qualidade": qualidade,
        "bytes": len(
            dados
        ),
    }


# ============================================================
# VALIDAÇÃO DE OFFSETS
# ============================================================

def cabecalho_no_offset(
    dados,
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

    match = (
        PADRAO_ARTIGO_BYTES.match(
            dados,
            offset,
        )
    )

    if not match:
        return None

    bruto = (
        match.group(
            1
        )
        .decode(
            "ascii",
            errors="ignore",
        )
        .replace(
            ".",
            "",
        )
    )

    sufixo = ""

    if match.group(
        2
    ):
        sufixo = (
            match.group(
                2
            )
            .decode(
                "ascii",
                errors="ignore",
            )
            .upper()
        )

    return formatar_artigo(
        bruto,
        sufixo,
    )


def validar_offsets(
    dados,
    artigos,
):
    erros = []

    offset_anterior = -1

    for artigo in artigos:
        offset = artigo[
            "offset"
        ]

        tamanho = artigo[
            "tamanho"
        ]

        if offset <= offset_anterior:
            erros.append(
                (
                    f"Offsets fora de ordem em "
                    f"Art. {artigo['artigo']}."
                )
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

        offset_anterior = offset

    return erros


# ============================================================
# VALIDAÇÃO ESTRUTURAL POR NORMA
# ============================================================

def validar_norma_indexada(
    identificador,
    artigos,
    candidatos,
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

    if not artigos:
        erros.append(
            "Nenhum artigo indexado."
        )

        return (
            erros,
            alertas,
        )

    if (
        artigos[
            0
        ][
            "artigo"
        ]
        != "1"
    ):
        alertas.append(
            (
                "Sequência não começa em Art. 1 "
                f"(começa em {artigos[0]['artigo']})."
            )
        )

    if (
        candidatos >= 20
        and qualidade < 0.35
    ):
        alertas.append(
            (
                "Baixa razão entre sequência principal "
                f"e candidatos: {len(artigos)}/{candidatos} "
                f"({qualidade:.4f})."
            )
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
        "#LEXMACHINA|NORMAS|4",
        (
            "#ID|SIGLA|PRIORIDADE|RAMO|"
            "NOME|CAMINHO|ARTIGOS|BYTES"
        ),
    ]

    linhas_artigos = [
        "#LEXMACHINA|ARTIGOS|4",
        "#ID|ARTIGO|OFFSET|TAMANHO",
    ]

    linhas_menu = [
        "#LEXMACHINA|MENU|4",
        "#ORDEM|ID|SIGLA|RAMO|NOME",
    ]

    linhas_juris = [
        "#LEXMACHINA|JURIS|4",
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
            artigos,
        )

        (
            erros_norma,
            alertas_norma,
        ) = validar_norma_indexada(
            identificador,
            artigos,
            candidatos,
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
        "formato_indice": 4,
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
        "ruidos_descartados": (
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
            "AMOSTRAS REAIS LIDAS PELOS OFFSETS V4\n"
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
        "GERAÇÃO DE ÍNDICES PARA ESP32 - VERSÃO 4",
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
            "RUÍDOS/REFERÊNCIAS DESCARTADOS: "
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
        "GERADOR DE ÍNDICES ESP32 V4"
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
            "✓ ÍNDICE V4 APROVADO AUTOMATICAMENTE"
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
