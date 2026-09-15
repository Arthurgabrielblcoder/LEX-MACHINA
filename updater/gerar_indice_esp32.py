from datetime import datetime
from pathlib import Path
import argparse
import bisect
import json
import re
import sys
import unicodedata


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
ARQ_RELATORIO = "RELATORIO_INDICE_ESP32.txt"


# ============================================================
# CAMINHOS HISTÓRICOS DOS 20 ITENS BASE
# ============================================================

BASE_ALIASES = {
    "CF88": [
        "1- CONSTITUIÇÃO FEDERAL/cf.txt",
    ],
    "CC2002": [
        "2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt",
        "2- CÓDIGO CIVIL/codigo_civil_2002.txt",
    ],
    "CPC2015": [
        "3-CÓDIGO PROCESSO CIVIL/codigo_processo_civil.txt",
        "3-CÓDIGO PROCESSO CIVIL/codigo_processo_civil_2015.txt",
    ],
    "CP1940": [
        "4-CÓDIGO PENAL/codigo_penal.txt",
    ],
    "CPP1941": [
        "5-CÓDIGO PROCESSO PENAL/Código_de_Processo_Penal.txt",
        "5-CÓDIGO PROCESSO PENAL/codigo_processo_penal.txt",
    ],
    "CTN1966": [
        "6-CÓDIGO TRIBUTARIO NACIONAL/Código Tributário Nacional.txt",
        "6-CÓDIGO TRIBUTARIO NACIONAL/codigo_tributario_nacional.txt",
    ],
    "CE1965": [
        "7-CÓDIGO ELEITORAL/Código Eleitoral.txt",
        "7-CÓDIGO ELEITORAL/codigo_eleitoral.txt",
    ],
    "CLT1943": [
        "8-CLT CONSOLIDAÇÃO DAS LEIS DO TRABALHO/CLT.txt",
        "8-CLT CONSOLIDAÇÃO DAS LEIS DO TRABALHO/clt.txt",
    ],
    "CDC1990": [
        "9-CÓDIGO DE DEFESA DO CONSUMIDOR/01_CDC/cdc_lei_8078_1990.txt",
    ],
    "ECA1990": [
        "10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE/Estatuto da Criança e do Adolescente (Lei nº 8.069 1990).txt",
        "10- ECA ESTATUTO DA CRIANÇA E DO ADOLESCENTE/eca_lei_8069_1990.txt",
    ],
    "IDOSO2003": [
        "11- ESTATUTO DA PESSOA IDOSA/Estatuto da pessoa idosa.txt",
        "11- ESTATUTO DA PESSOA IDOSA/estatuto_pessoa_idosa.txt",
    ],
    "LBI2015": [
        "12-LEI BRASILEIRA DE INCLUSÃO DA PESSOA COM DEFICIÊNCIA/Lei Brasileira de Inclusão da Pessoa com Deficiência.txt",
        "12-LEI BRASILEIRA DE INCLUSÃO DA PESSOA COM DEFICIÊNCIA/lei_brasileira_inclusao.txt",
    ],
    "LEP1984": [
        "13- LEI DA EXECUÇÃO PENAL/Lei de Execução Penal.txt",
        "13- LEI DA EXECUÇÃO PENAL/lei_execucao_penal.txt",
    ],
    "DROGAS2006": [
        "14- LEI DE DROGAS/Lei de Drogas.txt",
        "14- LEI DE DROGAS/lei_drogas.txt",
    ],
    "MARIA2006": [
        "15-LEI MARIA DA PENHA/Lei Maria da Penha.txt",
        "15-LEI MARIA DA PENHA/lei_maria_da_penha.txt",
    ],
    "HEDIONDOS1990": [
        "16- LEI DE CRIMES HEDIONDOS/Lei de Crimes Hediondos.txt",
        "16- LEI DE CRIMES HEDIONDOS/lei_crimes_hediondos.txt",
    ],
    "LIC2021": [
        "17- LEI DE LICITAÇÕES E CONTRATOS/Lei de Licitações e Contratos Administrativos.txt",
        "17- LEI DE LICITAÇÕES E CONTRATOS/lei_licitacoes_contratos_14133.txt",
    ],
    "MCI2014": [
        "18- MARCO CIVIL DA INTERNET/Marco Civil da Internet.txt",
        "18- MARCO CIVIL DA INTERNET/marco_civil_internet.txt",
    ],
    "LGPD2018": [
        "19-LGPD LEI GERAL DA PROTEÇÃO DE DADOS/LGPD Lei Geral da Proteção de Dados.txt",
        "19-LGPD LEI GERAL DA PROTEÇÃO DE DADOS/lgpd.txt",
    ],
    "LAI2011": [
        "20- LEI DE ACESSO A INFORMAÇÃO/Lei de Acesso a Informação.txt",
        "20- LEI DE ACESSO A INFORMAÇÃO/lei_acesso_informacao.txt",
    ],
}


# ============================================================
# ARGUMENTOS
# ============================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - Gerador de índices ESP32 v2 "
            "com seleção monotônica de artigos"
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
# LOCALIZAÇÃO EXATA DAS NORMAS
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

    # BASE: usa aliases históricos conhecidos.
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
                return [
                    caminho
                ]

    # A/B/C e fallback BASE:
    # pasta_destino + arquivo_sugerido exatos.
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
            return [
                caminho
            ]

    return []


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
# EXTRAÇÃO DOS CANDIDATOS DE ARTIGO
# ============================================================

PADRAO_ARTIGO = re.compile(
    rb"(?im)"
    rb"^[ \t]*"
    rb"(?:art\.?|artigo)"
    rb"[ \t]+"
    rb"(\d+)"
    rb"(?:"
        rb"\xc2\xba"
        rb"|\xc2\xb0"
        rb"|o"
    rb")?"
    rb"(?:"
        rb"[ \t]*-[ \t]*"
        rb"([A-Za-z]+)"
    rb")?"
)


def valor_sufixo(
    sufixo
):
    """
    Converte:
        ""  -> 0
        A   -> 1
        B   -> 2
        AA  -> 27
    """

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


def listar_candidatos_artigo(
    dados
):
    candidatos = []

    for match in PADRAO_ARTIGO.finditer(
        dados
    ):
        numero = match.group(
            1
        ).decode(
            "ascii",
            errors="ignore",
        )

        sufixo = ""

        if match.group(
            2
        ):
            sufixo = match.group(
                2
            ).decode(
                "ascii",
                errors="ignore",
            ).upper()

        artigo = numero

        if sufixo:
            artigo += (
                "-"
                + sufixo
            )

        candidatos.append(
            {
                "artigo": artigo,
                "numero": numero,
                "sufixo": sufixo,
                "chave": chave_artigo(
                    numero,
                    sufixo,
                ),
                "offset": match.start(),
            }
        )

    return candidatos


# ============================================================
# MAIOR SUBSEQUÊNCIA CRESCENTE
# ============================================================

def selecionar_sequencia_principal(
    candidatos
):
    """
    O corpo principal de uma lei percorre artigos em ordem
    crescente: 1, 2, 3... ou 5, 5-A, 5-B, 6...

    Referências legislativas e notas de alteração podem começar
    uma linha com "Art. 63", "Art. 5" etc. e confundiam a versão
    anterior do índice.

    Aqui selecionamos a maior subsequência estritamente crescente
    pelas chaves (número, sufixo). O corpo real da lei é muito mais
    longo e ordenado do que as referências esparsas.
    """

    if not candidatos:
        return []

    tails = []
    tails_indices = []
    anteriores = [
        -1
    ] * len(
        candidatos
    )

    for indice, candidato in enumerate(
        candidatos
    ):
        chave = candidato[
            "chave"
        ]

        pos = bisect.bisect_left(
            tails,
            chave,
        )

        if (
            pos
            == len(
                tails
            )
        ):
            tails.append(
                chave
            )

            tails_indices.append(
                indice
            )

        else:
            tails[
                pos
            ] = chave

            tails_indices[
                pos
            ] = indice

        if pos > 0:
            anteriores[
                indice
            ] = tails_indices[
                pos
                - 1
            ]

    atual = tails_indices[
        -1
    ]

    selecionados = []

    while atual >= 0:
        selecionados.append(
            candidatos[
                atual
            ]
        )

        atual = anteriores[
            atual
        ]

    selecionados.reverse()

    return selecionados


# ============================================================
# OFFSETS E TAMANHOS
# ============================================================

def extrair_artigos_bytes(
    caminho
):
    dados = caminho.read_bytes()

    candidatos = listar_candidatos_artigo(
        dados
    )

    selecionados = selecionar_sequencia_principal(
        candidatos
    )

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
            fim = selecionados[
                indice
                + 1
            ][
                "offset"
            ]

        else:
            fim = len(
                dados
            )

        artigos.append(
            {
                "artigo": item[
                    "artigo"
                ],
                "offset": inicio,
                "tamanho": max(
                    0,
                    fim - inicio,
                ),
            }
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

    return (
        artigos,
        len(
            candidatos
        ),
        descartados,
        qualidade,
        len(
            dados
        ),
    )


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
        "#LEXMACHINA|NORMAS|2",
        "#ID|SIGLA|PRIORIDADE|RAMO|NOME|CAMINHO|ARTIGOS|BYTES",
    ]

    linhas_artigos = [
        "#LEXMACHINA|ARTIGOS|2",
        "#ID|ARTIGO|OFFSET|TAMANHO",
    ]

    linhas_menu = [
        "#LEXMACHINA|MENU|2",
        "#ORDEM|ID|SIGLA|RAMO|NOME",
    ]

    linhas_juris = [
        "#LEXMACHINA|JURIS|2",
        "#TRIBUNAL|TIPO|NUMERO|STATUS|ARQUIVO|RELACIONADO_A",
    ]

    relatorio = [
        "LEX MACHINA",
        "GERAÇÃO DE ÍNDICES PARA ESP32 - VERSÃO 2",
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
    total_juris = 0
    total_candidatos = 0
    total_descartados = 0

    erros = []
    alertas = []

    detalhes = []

    # --------------------------------------------------------
    # NORMAS
    # --------------------------------------------------------

    for ordem, item in enumerate(
        itens_mestre,
        start=1,
    ):
        encontrados = localizar_norma(
            item,
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
            (
                artigos,
                candidatos,
                descartados,
                qualidade,
                tamanho_bytes,
            ) = extrair_artigos_bytes(
                caminho
            )

        except OSError as erro:
            erros.append(
                (
                    f"Falha ao ler {caminho}: "
                    f"{erro}"
                )
            )

            continue

        nome = limpar_campo(
            item.get(
                "nome",
                "",
            )
        )

        if not artigos:
            alertas.append(
                (
                    f"{nome}: nenhum artigo foi "
                    "identificado."
                )
            )

        # Qualidade baixa indica que há muitas referências
        # ou estrutura atípica e merece revisão.
        if (
            candidatos >= 20
            and qualidade < 0.45
        ):
            alertas.append(
                (
                    f"{nome}: somente "
                    f"{len(artigos)}/{candidatos} "
                    "candidatos compõem a sequência "
                    "principal."
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
                        tamanho_bytes
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

        detalhes.append(
            {
                "id": identificador,
                "nome": nome,
                "arquivo": caminho_sd,
                "candidatos": candidatos,
                "artigos_indexados": len(
                    artigos
                ),
                "ruidos_descartados": descartados,
                "qualidade": round(
                    qualidade,
                    4,
                ),
            }
        )

        total_normas += 1
        total_artigos += len(
            artigos
        )
        total_candidatos += candidatos
        total_descartados += descartados

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
        "formato_indice": 2,
        "gerado_em": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "versao_catalogo": catalogo_mestre.get(
            "versao",
            ""
        ),
        "normas": total_normas,
        "artigos": total_artigos,
        "candidatos_artigo": total_candidatos,
        "ruidos_descartados": total_descartados,
        "jurisprudencias": total_juris,
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

    relatorio.extend(
        [
            f"NORMAS INDEXADAS: {total_normas}",
            f"ARTIGOS INDEXADOS: {total_artigos}",
            (
                "CANDIDATOS DE ARTIGO ENCONTRADOS: "
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
            f"ALERTAS REAIS: {len(alertas)}",
            "",
            "ARQUIVOS GERADOS:",
            f"- {pasta_saida / ARQ_NORMAS}",
            f"- {pasta_saida / ARQ_ARTIGOS}",
            f"- {pasta_saida / ARQ_JURIS}",
            f"- {pasta_saida / ARQ_MENU}",
            f"- {pasta_saida / ARQ_META}",
            "",
            "=" * 78,
            "DIAGNÓSTICO POR NORMA",
            "=" * 78,
            "",
        ]
    )

    for detalhe in detalhes:
        relatorio.append(
            (
                f"- {detalhe['id']} | "
                f"artigos={detalhe['artigos_indexados']} | "
                f"candidatos={detalhe['candidatos']} | "
                f"descartados={detalhe['ruidos_descartados']} | "
                f"qualidade={detalhe['qualidade']:.4f} | "
                f"{detalhe['nome']}"
            )
        )

    relatorio.append("")

    if erros:
        relatorio.extend(
            [
                "ERROS",
                "-" * 78,
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
                "ALERTAS REAIS",
                "-" * 78,
            ]
        )

        for alerta in alertas:
            relatorio.append(
                f"- {alerta}"
            )

        relatorio.append("")

    (
        pasta_saida
        / ARQ_RELATORIO
    ).write_text(
        "\n".join(
            relatorio
        ),
        encoding="utf-8",
        newline="\n",
    )

    return {
        "pasta": pasta_saida,
        "normas": total_normas,
        "artigos": total_artigos,
        "candidatos": total_candidatos,
        "descartados": total_descartados,
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

    catalogo_mestre, itens_mestre = (
        carregar_catalogo_mestre()
    )

    registros_juris = (
        carregar_catalogo_juris()
    )

    print()
    print(
        "LEX MACHINA - "
        "GERADOR DE ÍNDICES ESP32 V2"
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
        "ÍNDICES GERADOS"
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
        "Ruídos/referências descartados: "
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
        "Alertas reais: "
        f"{len(resultado['alertas'])}"
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
            "✓ ÍNDICE ESP32 V2 GERADO "
            "SEM PENDÊNCIAS"
        )

    elif not resultado[
        "erros"
    ]:
        print(
            "✓ ÍNDICE GERADO, "
            "COM ALERTAS PARA REVISÃO"
        )

    else:
        print(
            "⚠ EXISTEM ERROS. "
            "REVISE O RELATÓRIO."
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
