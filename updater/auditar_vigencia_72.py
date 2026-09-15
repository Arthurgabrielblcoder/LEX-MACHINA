from datetime import datetime
from pathlib import Path
import argparse
import copy
import json
import re
import sys
import time
import unicodedata

import requests
from bs4 import BeautifulSoup


# ============================================================
# LEX MACHINA - AUDITORIA DE VIGÊNCIA DAS 72 NORMAS
#
# OBJETIVO:
# - NÃO ALTERAR NENHUM ARQUIVO DO CARTÃO;
# - comparar cada norma local com o TEXTO OFICIAL VIGENTE;
# - separar texto histórico/revogado do texto vigente;
# - detectar omissões de blocos vigentes;
# - detectar quando a própria página oficial foi extraída de
#   forma incompleta e NÃO transformar isso em falso "OK";
# - gerar relatório TXT + JSON no PC.
#
# CLASSIFICAÇÕES:
# - APROVADA_VIGENTE
# - REVISAR
# - SUSPEITA_OMISSAO_VIGENTE
# - FONTE_OFICIAL_INCONCLUSIVA
#
# IMPORTANTE:
# ESTE SCRIPT É SOMENTE LEITURA NO CARTÃO.
# ============================================================


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO = Path(
    "catalogo_mestre_vademecum.json"
)

REL_DIR = Path(
    "saida/99_INDICES"
)

REL_TXT = (
    REL_DIR
    / "AUDITORIA_VIGENCIA_72_NORMAS.txt"
)

REL_JSON = (
    REL_DIR
    / "AUDITORIA_VIGENCIA_72_NORMAS.json"
)

CACHE_DIR = Path(
    "cache_auditoria_vigencia_72"
)

TIMEOUT = 45

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


# ============================================================
# ALIASES DOS 20 ITENS BASE
# ============================================================

ALIASES = {
    "CF88": [
        "1- CONSTITUIÇÃO FEDERAL/cf.txt",
    ],
    "CC2002": [
        "2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt",
    ],
    "CPC2015": [
        "3-CÓDIGO PROCESSO CIVIL/codigo_processo_civil.txt",
    ],
    "CP1940": [
        "4-CÓDIGO PENAL/codigo_penal.txt",
    ],
    "CPP1941": [
        "5-CÓDIGO PROCESSO PENAL/Código_de_Processo_Penal.txt",
    ],
    "CTN1966": [
        "6-CÓDIGO TRIBUTARIO NACIONAL/Código Tributário Nacional.txt",
    ],
    "CE1965": [
        "7-CÓDIGO ELEITORAL/Código Eleitoral.txt",
    ],
    "CLT1943": [
        "8-CLT CONSOLIDAÇÃO DAS LEIS DO TRABALHO/CLT.txt",
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
# ARGUMENTOS
# ============================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - auditoria do texto vigente "
            "das 72 normas"
        )
    )

    parser.add_argument(
        "origem",
        help=(
            "Raiz do cartão. Exemplo: D:\\"
        ),
    )

    parser.add_argument(
        "--sem-cache",
        action="store_true",
        help=(
            "Ignora o cache local e consulta novamente "
            "todas as fontes oficiais."
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


def limpar_texto(texto):
    texto = str(
        texto or ""
    )

    texto = (
        texto
        .replace("\xa0", " ")
        .replace("\u2002", " ")
        .replace("\u2003", " ")
        .replace("\u2009", " ")
        .replace("\ufeff", "")
    )

    texto = re.sub(
        r"[ \t]+",
        " ",
        texto,
    )

    texto = re.sub(
        r"\n{3,}",
        "\n\n",
        texto,
    )

    return texto.strip()


def normalizar(texto):
    texto = remover_acentos(
        texto
    ).casefold()

    texto = re.sub(
        r"[^a-z0-9§º°]+",
        " ",
        texto,
    )

    return re.sub(
        r"\s+",
        " ",
        texto,
    ).strip()


def compactar(texto):
    return re.sub(
        r"[^a-z0-9]+",
        "",
        normalizar(
            texto
        ),
    )


def nome_cache(
    identificador
):
    seguro = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        identificador,
    )

    return (
        CACHE_DIR
        / f"{seguro}.json"
    )


# ============================================================
# CATÁLOGO
# ============================================================

def carregar_catalogo():
    if not CATALOGO.exists():
        raise FileNotFoundError(
            f"Catálogo não encontrado: {CATALOGO}"
        )

    dados = json.loads(
        CATALOGO.read_text(
            encoding="utf-8"
        )
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
            "precisa ser uma lista."
        )

    if len(
        itens
    ) != 72:
        print(
            (
                "AVISO: o catálogo possui "
                f"{len(itens)} itens, não 72."
            )
        )

    return dados, itens


# ============================================================
# INVENTÁRIO / LOCALIZAÇÃO
# ============================================================

def inventariar(origem):
    arquivos = []

    for caminho in origem.rglob(
        "*"
    ):
        if not caminho.is_file():
            continue

        try:
            relativo = caminho.relative_to(
                origem
            )

        except ValueError:
            continue

        arquivos.append(
            {
                "path": caminho,
                "rel": relativo,
                "nome_compacto": compactar(
                    caminho.name
                ),
                "caminho_norm": normalizar(
                    str(
                        relativo
                    )
                ),
            }
        )

    return arquivos


def localizar_item(
    item,
    origem,
    arquivos,
):
    identificador = str(
        item.get(
            "id",
            ""
        )
    ).strip()

    for relativo in ALIASES.get(
        identificador,
        [],
    ):
        caminho = (
            origem
            / Path(
                relativo
            )
        )

        if caminho.exists():
            return caminho

    pasta = normalizar(
        item.get(
            "pasta_destino",
            ""
        )
    )

    nome = compactar(
        item.get(
            "arquivo_sugerido",
            ""
        )
    )

    candidatos = []

    for arquivo in arquivos:
        if (
            arquivo[
                "nome_compacto"
            ]
            != nome
        ):
            continue

        if (
            pasta
            not in arquivo[
                "caminho_norm"
            ]
        ):
            continue

        candidatos.append(
            arquivo[
                "path"
            ]
        )

    if candidatos:
        return candidatos[
            0
        ]

    return None


# ============================================================
# LEITURA LOCAL
# ============================================================

def ler_local(caminho):
    dados = caminho.read_bytes()

    for codificacao in (
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            texto = dados.decode(
                codificacao
            )

            return {
                "bytes": len(
                    dados
                ),
                "linhas": len(
                    texto.splitlines()
                ),
                "caracteres": len(
                    texto
                ),
                "encoding": codificacao,
                "texto": limpar_texto(
                    texto
                ),
            }

        except UnicodeDecodeError:
            continue

    texto = dados.decode(
        "utf-8",
        errors="replace",
    )

    return {
        "bytes": len(
            dados
        ),
        "linhas": len(
            texto.splitlines()
        ),
        "caracteres": len(
            texto
        ),
        "encoding": "utf-8-replace",
        "texto": limpar_texto(
            texto
        ),
    }


# ============================================================
# ARTIGOS APARENTES
# Usado apenas para avaliar a qualidade da extração oficial.
# ============================================================

PADRAO_ARTIGO = re.compile(
    r"(?im)"
    r"(?:^|\n)\s*"
    r"Art(?:igo)?"
    r"\s*\.?\s*"
    r"(?:\.\s*)?"
    r"(\d{1,3}(?:\.\d{3})+|\d{1,4})"
)


def metricas_artigos(
    texto
):
    bases = []

    for match in PADRAO_ARTIGO.finditer(
        texto
    ):
        bruto = match.group(
            1
        )

        try:
            base = int(
                bruto.replace(
                    ".",
                    "",
                )
            )

        except ValueError:
            continue

        if 1 <= base <= 9999:
            bases.append(
                base
            )

    return {
        "ocorrencias": len(
            bases
        ),
        "max": (
            max(
                bases
            )
            if bases
            else 0
        ),
    }


# ============================================================
# FONTE OFICIAL
# ============================================================

def decodificar_html(dados):
    candidatos = []

    for codificacao in (
        "utf-8",
        "cp1252",
        "iso-8859-1",
    ):
        try:
            html = dados.decode(
                codificacao
            )

            candidatos.append(
                (
                    html.count(
                        "Art"
                    ),
                    codificacao,
                    html,
                )
            )

        except UnicodeDecodeError:
            continue

    if candidatos:
        candidatos.sort(
            key=lambda item: item[
                0
            ],
            reverse=True,
        )

        return (
            candidatos[
                0
            ][
                2
            ],
            candidatos[
                0
            ][
                1
            ],
        )

    return (
        dados.decode(
            "cp1252",
            errors="replace",
        ),
        "cp1252-replace",
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

    estilo = str(
        attrs.get(
            "style",
            ""
        )
    ).lower()

    estilo = re.sub(
        r"\s+",
        "",
        estilo,
    )

    return (
        "line-through"
        in estilo
    )


def remover_nao_textuais(soup):
    for nome in (
        "script",
        "style",
        "noscript",
        "iframe",
        "svg",
        "canvas",
    ):
        for tag in soup.find_all(
            nome
        ):
            try:
                tag.decompose()

            except AttributeError:
                pass


def extrair_oficial_html(
    html,
    bytes_html,
    status_http,
    codificacao,
):
    soup_completo = BeautifulSoup(
        html,
        "lxml",
    )

    remover_nao_textuais(
        soup_completo
    )

    soup_vigente = copy.deepcopy(
        soup_completo
    )

    tags = list(
        soup_vigente.find_all(
            True
        )
    )

    for tag in reversed(
        tags
    ):
        try:
            if elemento_riscado(
                tag
            ):
                tag.decompose()

        except (
            AttributeError,
            TypeError,
        ):
            pass

    corpo_completo = (
        soup_completo.body
        or soup_completo
    )

    corpo_vigente = (
        soup_vigente.body
        or soup_vigente
    )

    texto_completo = limpar_texto(
        corpo_completo.get_text(
            separator="\n",
            strip=True,
        )
    )

    texto_vigente = limpar_texto(
        corpo_vigente.get_text(
            separator="\n",
            strip=True,
        )
    )

    return {
        "status_http": (
            status_http
        ),
        "encoding_html": (
            codificacao
        ),
        "bytes_html": (
            bytes_html
        ),
        "completo": {
            "texto": texto_completo,
            "linhas": len(
                texto_completo.splitlines()
            ),
            "caracteres": len(
                texto_completo
            ),
            "artigos": metricas_artigos(
                texto_completo
            ),
        },
        "vigente": {
            "texto": texto_vigente,
            "linhas": len(
                texto_vigente.splitlines()
            ),
            "caracteres": len(
                texto_vigente
            ),
            "artigos": metricas_artigos(
                texto_vigente
            ),
        },
    }


def baixar_oficial(
    item,
    usar_cache=True,
):
    identificador = str(
        item.get(
            "id",
            ""
        )
    ).strip()

    cache = nome_cache(
        identificador
    )

    if (
        usar_cache
        and cache.exists()
    ):
        try:
            dados_cache = json.loads(
                cache.read_text(
                    encoding="utf-8"
                )
            )

            if (
                dados_cache.get(
                    "url"
                )
                == item.get(
                    "fonte_oficial"
                )
            ):
                return (
                    dados_cache[
                        "resultado"
                    ]
                )

        except Exception:
            pass

    resposta = requests.get(
        item[
            "fonte_oficial"
        ],
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    resposta.raise_for_status()

    html, codificacao = (
        decodificar_html(
            resposta.content
        )
    )

    resultado = extrair_oficial_html(
        html,
        len(
            resposta.content
        ),
        resposta.status_code,
        codificacao,
    )

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cache.write_text(
        json.dumps(
            {
                "url": item[
                    "fonte_oficial"
                ],
                "gerado_em": agora(),
                "resultado": (
                    resultado
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return resultado


# ============================================================
# SHINGLES / COBERTURA
# ============================================================

def shingles(
    texto,
    n=7,
):
    palavras = normalizar(
        texto
    ).split()

    if len(
        palavras
    ) < n:
        return set()

    return {
        " ".join(
            palavras[
                indice:
                indice + n
            ]
        )
        for indice in range(
            len(
                palavras
            )
            - n
            + 1
        )
    }


def cobertura(
    referencia,
    candidato,
):
    ref = shingles(
        referencia
    )

    cand = shingles(
        candidato
    )

    if not ref:
        return 0.0

    return len(
        ref
        & cand
    ) / len(
        ref
    )


# ============================================================
# BLOCOS
# ============================================================

def blocos(
    texto,
    min_chars=100,
):
    linhas = [
        limpar_texto(
            linha
        )
        for linha in texto.splitlines()
    ]

    saida = []

    atual = []

    tamanho = 0

    for linha in linhas:
        if not linha:
            if atual:
                bloco = " ".join(
                    atual
                ).strip()

                if len(
                    bloco
                ) >= min_chars:
                    saida.append(
                        bloco
                    )

                atual = []
                tamanho = 0

            continue

        atual.append(
            linha
        )

        tamanho += len(
            linha
        )

        if tamanho >= 450:
            bloco = " ".join(
                atual
            ).strip()

            if len(
                bloco
            ) >= min_chars:
                saida.append(
                    bloco
                )

            atual = []
            tamanho = 0

    if atual:
        bloco = " ".join(
            atual
        ).strip()

        if len(
            bloco
        ) >= min_chars:
            saida.append(
                bloco
            )

    return saida


def bloco_presente(
    bloco,
    local_norm,
):
    bloco_norm = normalizar(
        bloco
    )

    if not bloco_norm:
        return True

    if bloco_norm in local_norm:
        return True

    palavras = bloco_norm.split()

    if len(
        palavras
    ) < 10:
        return False

    janela = min(
        14,
        len(
            palavras
        ),
    )

    inicio = " ".join(
        palavras[
            :janela
        ]
    )

    fim = " ".join(
        palavras[
            -janela:
        ]
    )

    meio_indice = (
        len(
            palavras
        )
        // 2
    )

    meio = " ".join(
        palavras[
            max(
                0,
                meio_indice
                - janela // 2
            ):
            meio_indice
            + janela // 2
        ]
    )

    presentes = sum(
        1
        for assinatura in (
            inicio,
            meio,
            fim,
        )
        if (
            assinatura
            and assinatura
            in local_norm
        )
    )

    return presentes >= 2


def encontrar_ausentes(
    texto_vigente,
    texto_local,
    limite=25,
):
    lista = blocos(
        texto_vigente
    )

    local_norm = normalizar(
        texto_local
    )

    exemplos = []

    total_ausentes = 0

    for bloco in lista:
        if bloco_presente(
            bloco,
            local_norm,
        ):
            continue

        total_ausentes += 1

        if len(
            exemplos
        ) < limite:
            exemplos.append(
                re.sub(
                    r"\s+",
                    " ",
                    bloco,
                ).strip()[
                    :800
                ]
            )

    return {
        "total_blocos": len(
            lista
        ),
        "total_ausentes": (
            total_ausentes
        ),
        "exemplos": exemplos,
    }


# ============================================================
# QUALIDADE DA FONTE OFICIAL
# ============================================================

def avaliar_fonte_oficial(
    local,
    oficial,
):
    vigente = oficial[
        "vigente"
    ]

    motivos = []

    local_chars = local[
        "caracteres"
    ]

    oficial_chars = vigente[
        "caracteres"
    ]

    local_art = metricas_artigos(
        local[
            "texto"
        ]
    )

    oficial_art = vigente[
        "artigos"
    ]

    # A fonte extraída ser MUITO menor que o arquivo local
    # é forte indício de página/HTML problemático.
    if (
        local_chars >= 5000
        and oficial_chars
        < local_chars * 0.35
    ):
        motivos.append(
            (
                "texto oficial extraído tem menos de 35% "
                "do tamanho do arquivo local"
            )
        )

    if (
        local_art[
            "ocorrencias"
        ] >= 20
        and oficial_art[
            "ocorrencias"
        ]
        < local_art[
            "ocorrencias"
        ] * 0.35
    ):
        motivos.append(
            (
                "fonte oficial extraída contém muito menos "
                "artigos aparentes que o arquivo local"
            )
        )

    if (
        oficial_chars < 500
        and local_chars > 5000
    ):
        motivos.append(
            (
                "texto oficial extraído é pequeno demais "
                "para uma norma extensa"
            )
        )

    return {
        "confiavel": not bool(
            motivos
        ),
        "motivos": motivos,
        "local_artigos": local_art,
        "oficial_artigos": oficial_art,
    }


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar(
    local,
    oficial,
):
    qualidade = avaliar_fonte_oficial(
        local,
        oficial,
    )

    if not qualidade[
        "confiavel"
    ]:
        return {
            "status": (
                "FONTE_OFICIAL_INCONCLUSIVA"
            ),
            "motivos": qualidade[
                "motivos"
            ],
            "cobertura_vigente_no_local": None,
            "cobertura_local_no_vigente": None,
            "blocos_vigentes": 0,
            "blocos_vigentes_ausentes": 0,
            "proporcao_blocos_ausentes": 0.0,
            "exemplos_ausentes": [],
            "qualidade_fonte": qualidade,
        }

    cobertura_vigente = cobertura(
        oficial[
            "vigente"
        ][
            "texto"
        ],
        local[
            "texto"
        ],
    )

    cobertura_local_no_vigente = (
        cobertura(
            local[
                "texto"
            ],
            oficial[
                "vigente"
            ][
                "texto"
            ],
        )
    )

    ausentes = encontrar_ausentes(
        oficial[
            "vigente"
        ][
            "texto"
        ],
        local[
            "texto"
        ],
    )

    proporcao_ausentes = (
        ausentes[
            "total_ausentes"
        ]
        / ausentes[
            "total_blocos"
        ]
        if ausentes[
            "total_blocos"
        ]
        else 0.0
    )

    motivos = []

    if cobertura_vigente < 0.85:
        motivos.append(
            (
                "cobertura do texto vigente oficial "
                "no arquivo local abaixo de 85%"
            )
        )

    if (
        oficial[
            "vigente"
        ][
            "caracteres"
        ]
        >= 5000
        and local[
            "caracteres"
        ]
        < oficial[
            "vigente"
        ][
            "caracteres"
        ]
        * 0.75
    ):
        motivos.append(
            (
                "arquivo local tem menos de 75% "
                "do tamanho do texto oficial vigente"
            )
        )

    if proporcao_ausentes > 0.12:
        motivos.append(
            (
                "mais de 12% dos blocos vigentes "
                "não foram localizados no arquivo local"
            )
        )

    if motivos:
        status = (
            "SUSPEITA_OMISSAO_VIGENTE"
        )

    elif (
        cobertura_vigente < 0.95
        or proporcao_ausentes > 0.04
    ):
        status = "REVISAR"

    else:
        status = (
            "APROVADA_VIGENTE"
        )

    return {
        "status": status,
        "motivos": motivos,
        "cobertura_vigente_no_local": (
            cobertura_vigente
        ),
        "cobertura_local_no_vigente": (
            cobertura_local_no_vigente
        ),
        "blocos_vigentes": (
            ausentes[
                "total_blocos"
            ]
        ),
        "blocos_vigentes_ausentes": (
            ausentes[
                "total_ausentes"
            ]
        ),
        "proporcao_blocos_ausentes": (
            proporcao_ausentes
        ),
        "exemplos_ausentes": (
            ausentes[
                "exemplos"
            ]
        ),
        "qualidade_fonte": (
            qualidade
        ),
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

    catalogo, itens = (
        carregar_catalogo()
    )

    arquivos = inventariar(
        origem
    )

    usar_cache = not args.sem_cache

    print()
    print(
        "LEX MACHINA - "
        "AUDITORIA DE VIGÊNCIA DAS 72 NORMAS"
    )

    print(
        "=" * 72
    )

    print(
        f"Origem: {origem}"
    )

    print(
        f"Normas: {len(itens)}"
    )

    print(
        "Modo: SOMENTE LEITURA NO CARTÃO"
    )

    print(
        "Cache da fonte oficial: "
        + (
            "ATIVO"
            if usar_cache
            else "IGNORADO"
        )
    )

    print()

    resultados = []

    total = len(
        itens
    )

    for indice, item in enumerate(
        itens,
        start=1,
    ):
        identificador = str(
            item.get(
                "id",
                ""
            )
        ).strip()

        nome = item.get(
            "nome",
            "",
        )

        print(
            f"[{indice}/{total}] "
            f"{identificador} - {nome}"
        )

        caminho = localizar_item(
            item,
            origem,
            arquivos,
        )

        if caminho is None:
            resultados.append(
                {
                    "id": identificador,
                    "nome": nome,
                    "status": (
                        "SUSPEITA_OMISSAO_VIGENTE"
                    ),
                    "erro": (
                        "Arquivo local não encontrado."
                    ),
                }
            )

            print(
                "  SUSPEITA: arquivo local "
                "não encontrado."
            )

            continue

        try:
            local = ler_local(
                caminho
            )

            oficial = baixar_oficial(
                item,
                usar_cache=(
                    usar_cache
                ),
            )

            analise = classificar(
                local,
                oficial,
            )

            resultado = {
                "id": identificador,
                "nome": nome,
                "prioridade": item.get(
                    "prioridade",
                    "",
                ),
                "arquivo": str(
                    caminho
                ),
                "fonte_oficial": item.get(
                    "fonte_oficial",
                    "",
                ),
                "status": analise[
                    "status"
                ],
                "motivos": analise[
                    "motivos"
                ],
                "local": {
                    "bytes": local[
                        "bytes"
                    ],
                    "linhas": local[
                        "linhas"
                    ],
                    "caracteres": local[
                        "caracteres"
                    ],
                    "artigos": (
                        analise[
                            "qualidade_fonte"
                        ][
                            "local_artigos"
                        ]
                    ),
                },
                "oficial_vigente": {
                    "linhas": oficial[
                        "vigente"
                    ][
                        "linhas"
                    ],
                    "caracteres": oficial[
                        "vigente"
                    ][
                        "caracteres"
                    ],
                    "artigos": oficial[
                        "vigente"
                    ][
                        "artigos"
                    ],
                },
                "cobertura_vigente_no_local": (
                    analise[
                        "cobertura_vigente_no_local"
                    ]
                ),
                "cobertura_local_no_vigente": (
                    analise[
                        "cobertura_local_no_vigente"
                    ]
                ),
                "blocos_vigentes": (
                    analise[
                        "blocos_vigentes"
                    ]
                ),
                "blocos_vigentes_ausentes": (
                    analise[
                        "blocos_vigentes_ausentes"
                    ]
                ),
                "proporcao_blocos_ausentes": (
                    analise[
                        "proporcao_blocos_ausentes"
                    ]
                ),
                "exemplos_ausentes": (
                    analise[
                        "exemplos_ausentes"
                    ]
                ),
            }

            resultados.append(
                resultado
            )

            if (
                resultado[
                    "cobertura_vigente_no_local"
                ]
                is not None
            ):
                print(
                    (
                        f"  {resultado['status']} "
                        "| vigente→local="
                        f"{resultado['cobertura_vigente_no_local']:.4f} "
                        "| ausentes="
                        f"{resultado['blocos_vigentes_ausentes']}/"
                        f"{resultado['blocos_vigentes']}"
                    )
                )

            else:
                print(
                    (
                        f"  {resultado['status']}: "
                        + "; ".join(
                            resultado[
                                "motivos"
                            ]
                        )
                    )
                )

        except Exception as erro:
            resultados.append(
                {
                    "id": identificador,
                    "nome": nome,
                    "arquivo": str(
                        caminho
                    ),
                    "status": (
                        "FONTE_OFICIAL_INCONCLUSIVA"
                    ),
                    "erro": str(
                        erro
                    ),
                }
            )

            print(
                f"  INCONCLUSIVO: {erro}"
            )

        # pequena pausa para não agredir o servidor
        time.sleep(
            0.15
        )

    # --------------------------------------------------------
    # RESUMO
    # --------------------------------------------------------

    aprovadas = [
        item
        for item in resultados
        if item.get(
            "status"
        )
        == "APROVADA_VIGENTE"
    ]

    revisar = [
        item
        for item in resultados
        if item.get(
            "status"
        )
        == "REVISAR"
    ]

    suspeitas = [
        item
        for item in resultados
        if item.get(
            "status"
        )
        == "SUSPEITA_OMISSAO_VIGENTE"
    ]

    inconclusivas = [
        item
        for item in resultados
        if item.get(
            "status"
        )
        == "FONTE_OFICIAL_INCONCLUSIVA"
    ]

    # --------------------------------------------------------
    # RELATÓRIO
    # --------------------------------------------------------

    REL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas = [
        "LEX MACHINA",
        "AUDITORIA DO TEXTO VIGENTE - 72 NORMAS",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        f"ORIGEM: {origem}",
        (
            "VERSÃO DO CATÁLOGO: "
            f"{catalogo.get('versao', '')}"
        ),
        "",
        (
            "A auditoria não altera nenhum "
            "arquivo do cartão."
        ),
        (
            "Quando a extração da fonte oficial "
            "é pequena ou suspeita, a norma é "
            "marcada como FONTE_OFICIAL_INCONCLUSIVA "
            "em vez de receber falso OK."
        ),
        "",
        f"TOTAL: {len(resultados)}",
        (
            "APROVADAS PARA TEXTO VIGENTE: "
            f"{len(aprovadas)}"
        ),
        f"REVISAR: {len(revisar)}",
        (
            "SUSPEITA DE OMISSÃO VIGENTE: "
            f"{len(suspeitas)}"
        ),
        (
            "FONTE OFICIAL INCONCLUSIVA: "
            f"{len(inconclusivas)}"
        ),
        "",
        "=" * 78,
        "RESULTADOS",
        "=" * 78,
        "",
    ]

    for item in resultados:
        linhas.append(
            (
                f"[{item.get('status', '')}] "
                f"{item.get('id', '')} - "
                f"{item.get('nome', '')}"
            )
        )

        linhas.append(
            (
                "  Arquivo: "
                f"{item.get('arquivo', '')}"
            )
        )

        if item.get(
            "erro"
        ):
            linhas.append(
                (
                    "  ERRO: "
                    f"{item['erro']}"
                )
            )

        for motivo in item.get(
            "motivos",
            [],
        ):
            linhas.append(
                (
                    "  MOTIVO: "
                    f"{motivo}"
                )
            )

        if item.get(
            "local"
        ):
            linhas.append(
                (
                    "  Local: "
                    f"{item['local']['caracteres']} caracteres "
                    f"| artigos_aparentes="
                    f"{item['local']['artigos']['ocorrencias']} "
                    f"| maior_artigo="
                    f"{item['local']['artigos']['max']}"
                )
            )

        if item.get(
            "oficial_vigente"
        ):
            linhas.append(
                (
                    "  Oficial vigente: "
                    f"{item['oficial_vigente']['caracteres']} caracteres "
                    f"| artigos_aparentes="
                    f"{item['oficial_vigente']['artigos']['ocorrencias']} "
                    f"| maior_artigo="
                    f"{item['oficial_vigente']['artigos']['max']}"
                )
            )

        if (
            item.get(
                "cobertura_vigente_no_local"
            )
            is not None
        ):
            linhas.append(
                (
                    "  Cobertura vigente -> local: "
                    f"{item['cobertura_vigente_no_local']:.4f}"
                )
            )

            linhas.append(
                (
                    "  Blocos vigentes ausentes: "
                    f"{item['blocos_vigentes_ausentes']}/"
                    f"{item['blocos_vigentes']}"
                )
            )

        if item.get(
            "exemplos_ausentes"
        ):
            linhas.append(
                "  Exemplos de possíveis omissões vigentes:"
            )

            for exemplo in item[
                "exemplos_ausentes"
            ][
                :10
            ]:
                linhas.append(
                    (
                        "    - "
                        f"{exemplo}"
                    )
                )

        linhas.append("")

    linhas.extend(
        [
            "=" * 78,
            "CONCLUSÃO",
            "=" * 78,
            "",
        ]
    )

    if suspeitas:
        linhas.append(
            (
                "NÃO APROVADO: há indício de ausência "
                "de texto vigente em pelo menos uma norma."
            )
        )

    elif revisar:
        linhas.append(
            (
                "AINDA NÃO APROVADO: existem normas "
                "que exigem revisão."
            )
        )

    elif inconclusivas:
        linhas.append(
            (
                "AINDA NÃO APROVADO: o acervo não apresentou "
                "omissão vigente automática nas fontes confiáveis, "
                "mas há fontes oficiais cuja extração foi "
                "considerada inconclusiva."
            )
        )

    else:
        linhas.append(
            (
                "AUDITORIA APROVADA: TODAS AS NORMAS "
                "PASSARAM NA AUDITORIA DO TEXTO VIGENTE."
            )
        )

    REL_TXT.write_text(
        "\n".join(
            linhas
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    REL_JSON.write_text(
        json.dumps(
            {
                "gerado_em": agora(),
                "origem": str(
                    origem
                ),
                "versao_catalogo": (
                    catalogo.get(
                        "versao",
                        "",
                    )
                ),
                "resumo": {
                    "total": len(
                        resultados
                    ),
                    "aprovadas_vigente": len(
                        aprovadas
                    ),
                    "revisar": len(
                        revisar
                    ),
                    "suspeita_omissao_vigente": len(
                        suspeitas
                    ),
                    "fonte_oficial_inconclusiva": len(
                        inconclusivas
                    ),
                },
                "resultados": resultados,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print()
    print(
        "=" * 72
    )

    print(
        "AUDITORIA DE VIGÊNCIA FINALIZADA"
    )

    print(
        "APROVADAS PARA TEXTO VIGENTE: "
        f"{len(aprovadas)}"
    )

    print(
        f"REVISAR: {len(revisar)}"
    )

    print(
        "SUSPEITA DE OMISSÃO VIGENTE: "
        f"{len(suspeitas)}"
    )

    print(
        "FONTE OFICIAL INCONCLUSIVA: "
        f"{len(inconclusivas)}"
    )

    print(
        f"Relatório TXT: {REL_TXT}"
    )

    print(
        f"Relatório JSON: {REL_JSON}"
    )

    print()

    print(
        "Nenhum arquivo do cartão foi alterado."
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
