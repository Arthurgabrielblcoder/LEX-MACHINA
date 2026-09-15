from datetime import datetime
from pathlib import Path
import argparse
import copy
import json
import re
import sys
import unicodedata

import requests
from bs4 import BeautifulSoup


# ============================================================
# LEX MACHINA - AUDITORIA DA VIGÊNCIA
#
# OBJETIVO:
# Confirmar se o TEXTO VIGENTE das 5 normas ainda duvidosas
# está completo no cartão, separando:
#
# 1) texto oficial completo (inclui histórico/revogado)
# 2) texto oficial vigente (remove apenas marcações HTML
#    explicitamente riscadas: strike/s/del/line-through)
#
# O SCRIPT NÃO ALTERA NENHUM ARQUIVO DO CARTÃO.
# ============================================================


CATALOGO = Path(
    "catalogo_mestre_vademecum.json"
)

REL_DIR = Path(
    "saida/99_INDICES"
)

REL_TXT = (
    REL_DIR
    / "AUDITORIA_VIGENCIA_5_NORMAS.txt"
)

REL_JSON = (
    REL_DIR
    / "AUDITORIA_VIGENCIA_5_NORMAS.json"
)


# ============================================================
# ALVOS
# ============================================================

ALVOS = {
    "DROGAS2006",
    "LIA1992",
    "LRP1973",
    "SFI1997",
    "ALIMENTOS1968",
}


# ============================================================
# ALIASES CONHECIDOS
# ============================================================

ALIASES = {
    "DROGAS2006": [
        (
            "14- LEI DE DROGAS/"
            "Lei de Drogas.txt"
        ),
    ],
}


# ============================================================
# REDE
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

TIMEOUT = 45


# ============================================================
# ARGUMENTOS
# ============================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - auditoria do texto vigente "
            "das 5 normas ainda duvidosas"
        )
    )

    parser.add_argument(
        "origem",
        help=(
            "Raiz do cartão. Exemplo: D:\\"
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

    selecionados = [
        item
        for item in itens
        if str(
            item.get(
                "id",
                ""
            )
        ).strip()
        in ALVOS
    ]

    ids = {
        str(
            item.get(
                "id",
                ""
            )
        ).strip()
        for item in selecionados
    }

    faltantes = (
        ALVOS
        - ids
    )

    if faltantes:
        raise ValueError(
            "IDs ausentes do catálogo: "
            + ", ".join(
                sorted(
                    faltantes
                )
            )
        )

    return dados, selecionados


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

    # Alias conhecido primeiro.
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


def remover_nao_textuais(
    soup
):
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


def baixar_oficial(
    url
):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    resposta.raise_for_status()

    html, codificacao = (
        decodificar_html(
            resposta.content
        )
    )

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

    # Remove apenas elementos HTML explicitamente riscados.
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
            resposta.status_code
        ),
        "encoding_html": codificacao,
        "bytes_html": len(
            resposta.content
        ),
        "completo": {
            "texto": texto_completo,
            "linhas": len(
                texto_completo.splitlines()
            ),
            "caracteres": len(
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
        },
    }


# ============================================================
# COMPARAÇÃO POR SHINGLES
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
# BLOCOS VIGENTES AUSENTES
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
    local_norm
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


def encontrar_ausentes_vigentes(
    texto_vigente,
    texto_local,
    limite=30,
):
    lista = blocos(
        texto_vigente
    )

    local_norm = normalizar(
        texto_local
    )

    ausentes = []

    total_ausentes = 0

    for bloco in lista:
        if bloco_presente(
            bloco,
            local_norm,
        ):
            continue

        total_ausentes += 1

        if len(
            ausentes
        ) < limite:
            ausentes.append(
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
        "exemplos": ausentes,
    }


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar(
    local,
    oficial
):
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

    cobertura_completa = cobertura(
        oficial[
            "completo"
        ][
            "texto"
        ],
        local[
            "texto"
        ],
    )

    ausentes = (
        encontrar_ausentes_vigentes(
            oficial[
                "vigente"
            ][
                "texto"
            ],
            local[
                "texto"
            ],
        )
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
        status = "APROVADA_VIGENTE"

    return {
        "status": status,
        "motivos": motivos,
        "cobertura_vigente_no_local": (
            cobertura_vigente
        ),
        "cobertura_local_no_vigente": (
            cobertura_local_no_vigente
        ),
        "cobertura_completo_no_local": (
            cobertura_completa
        ),
        "blocos_vigentes": ausentes[
            "total_blocos"
        ],
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

    print()
    print(
        "LEX MACHINA - "
        "AUDITORIA DE VIGÊNCIA"
    )

    print(
        "=" * 68
    )

    print(
        "Analisando somente o TEXTO VIGENTE "
        "das 5 normas ainda duvidosas."
    )

    print(
        "Nenhum arquivo do cartão será alterado."
    )

    print()

    resultados = []

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
            f"[{indice}/5] "
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
                "  ERRO: arquivo local "
                "não encontrado."
            )

            continue

        try:
            local = ler_local(
                caminho
            )

            oficial = baixar_oficial(
                item[
                    "fonte_oficial"
                ]
            )

            analise = classificar(
                local,
                oficial,
            )

            resultado = {
                "id": identificador,
                "nome": nome,
                "arquivo": str(
                    caminho
                ),
                "fonte_oficial": (
                    item[
                        "fonte_oficial"
                    ]
                ),
                "status": (
                    analise[
                        "status"
                    ]
                ),
                "motivos": (
                    analise[
                        "motivos"
                    ]
                ),
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
                },
                "oficial_completo": {
                    "linhas": oficial[
                        "completo"
                    ][
                        "linhas"
                    ],
                    "caracteres": oficial[
                        "completo"
                    ][
                        "caracteres"
                    ],
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
                "cobertura_completo_no_local": (
                    analise[
                        "cobertura_completo_no_local"
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

            print(
                (
                    f"  {resultado['status']} "
                    "| vigente→local="
                    f"{resultado['cobertura_vigente_no_local']:.4f} "
                    "| blocos ausentes="
                    f"{resultado['blocos_vigentes_ausentes']}/"
                    f"{resultado['blocos_vigentes']}"
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
                    "status": "REVISAR",
                    "erro": str(
                        erro
                    ),
                }
            )

            print(
                f"  ERRO: {erro}"
            )

    # --------------------------------------------------------
    # RELATÓRIO
    # --------------------------------------------------------

    REL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

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

    linhas = [
        "LEX MACHINA",
        "AUDITORIA DO TEXTO VIGENTE - 5 NORMAS",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        f"ORIGEM: {origem}",
        (
            "VERSÃO DO CATÁLOGO: "
            f"{catalogo.get('versao', '')}"
        ),
        "",
        "CRITÉRIO:",
        (
            "O texto oficial completo é separado do "
            "texto explicitamente riscado/revogado no HTML."
        ),
        (
            "A classificação principal considera somente "
            "o texto oficial vigente."
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

            linhas.append("")
            continue

        linhas.append(
            (
                "  Cobertura VIGENTE -> local: "
                f"{item['cobertura_vigente_no_local']:.4f}"
            )
        )

        linhas.append(
            (
                "  Cobertura local -> VIGENTE: "
                f"{item['cobertura_local_no_vigente']:.4f}"
            )
        )

        linhas.append(
            (
                "  Cobertura COMPLETO -> local: "
                f"{item['cobertura_completo_no_local']:.4f}"
            )
        )

        linhas.append(
            (
                "  Local: "
                f"{item['local']['caracteres']} caracteres"
            )
        )

        linhas.append(
            (
                "  Oficial completo: "
                f"{item['oficial_completo']['caracteres']} caracteres"
            )
        )

        linhas.append(
            (
                "  Oficial vigente: "
                f"{item['oficial_vigente']['caracteres']} caracteres"
            )
        )

        linhas.append(
            (
                "  Blocos vigentes ausentes: "
                f"{item['blocos_vigentes_ausentes']}/"
                f"{item['blocos_vigentes']}"
            )
        )

        for motivo in item[
            "motivos"
        ]:
            linhas.append(
                (
                    "  MOTIVO: "
                    f"{motivo}"
                )
            )

        if item[
            "exemplos_ausentes"
        ]:
            linhas.append(
                "  Exemplos de possíveis omissões VIGENTES:"
            )

            for exemplo in (
                item[
                    "exemplos_ausentes"
                ][
                    :12
                ]
            ):
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
                "AINDA NÃO APROVADO: não há omissão "
                "vigente grave automática, mas há itens "
                "para revisão."
            )
        )

    else:
        linhas.append(
            (
                "AS 5 NORMAS PASSARAM NA AUDITORIA "
                "DO TEXTO VIGENTE."
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
        "=" * 68
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
