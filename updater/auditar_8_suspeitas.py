from datetime import datetime
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import re
import sys
import unicodedata

import requests
from bs4 import BeautifulSoup


# ============================================================
# LEX MACHINA - AUDITORIA PROFUNDA DAS 8 NORMAS SUSPEITAS
#
# OBJETIVO:
# - NÃO ALTERAR NADA NO CARTÃO;
# - comparar texto atual x fonte oficial x backup;
# - detectar omissões internas, não apenas tamanho ou número
#   máximo de artigo;
# - mostrar blocos presentes na fonte oficial e ausentes
#   no arquivo local;
# - classificar cada norma como:
#     APROVADA
#     REVISAR
#     SUSPEITA_DE_OMISSAO
#
# ESTE SCRIPT É SOMENTE LEITURA NO CARTÃO.
# ============================================================


CATALOGO = Path("catalogo_mestre_vademecum.json")
BACKUP_ROOT = Path("backup_catalogos")

REL_DIR = Path("saida/99_INDICES")

REL_TXT = (
    REL_DIR
    / "AUDITORIA_PROFUNDA_8_NORMAS.txt"
)

REL_JSON = (
    REL_DIR
    / "AUDITORIA_PROFUNDA_8_NORMAS.json"
)


# ============================================================
# 8 ALVOS
# ============================================================

ALVOS = {
    "DROGAS2006",
    "MARIA2006",
    "LIA1992",
    "LRP1973",
    "INELEG1990",
    "ARBIT1996",
    "SFI1997",
    "ALIMENTOS1968",
}


# ============================================================
# HEADERS / REDE
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
            "LEX MACHINA - Auditoria profunda "
            "das 8 normas suspeitas"
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


def normalizar_basico(texto):
    texto = (
        str(
            texto or ""
        )
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


def normalizar_comparacao(texto):
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
        normalizar_comparacao(
            texto
        ),
    )


def sha256_bytes(data):
    return hashlib.sha256(
        data
    ).hexdigest()


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

    encontrados = {
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
        - encontrados
    )

    if faltantes:
        raise ValueError(
            "IDs não encontrados no catálogo: "
            + ", ".join(
                sorted(
                    faltantes
                )
            )
        )

    return dados, selecionados


# ============================================================
# INVENTÁRIO
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
                "caminho_norm": (
                    normalizar_comparacao(
                        str(
                            relativo
                        )
                    )
                ),
            }
        )

    return arquivos


def localizar_item(
    item,
    arquivos
):
    pasta = normalizar_comparacao(
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

    if len(
        candidatos
    ) == 1:
        return candidatos[
            0
        ]

    if len(
        candidatos
    ) > 1:
        return candidatos[
            0
        ]

    return None


# ============================================================
# BACKUP
# ============================================================

def localizar_backups(
    relativo
):
    encontrados = []

    if not BACKUP_ROOT.exists():
        return encontrados

    for pasta in BACKUP_ROOT.glob(
        "catalogo_mestre_*"
    ):
        candidato = (
            pasta
            / relativo
        )

        if (
            candidato.exists()
            and candidato.is_file()
        ):
            encontrados.append(
                candidato
            )

    if not encontrados:
        nome = relativo.name.casefold()

        for candidato in (
            BACKUP_ROOT.rglob(
                "*"
            )
        ):
            if (
                candidato.is_file()
                and candidato.name.casefold()
                == nome
            ):
                encontrados.append(
                    candidato
                )

    return encontrados


def escolher_backup(
    relativo
):
    candidatos = localizar_backups(
        relativo
    )

    if not candidatos:
        return None

    # Preferimos o maior backup disponível.
    return max(
        candidatos,
        key=lambda caminho: (
            caminho.stat().st_size
        ),
    )


# ============================================================
# LEITURA LOCAL
# ============================================================

def ler_arquivo(
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
                "encoding": (
                    codificacao
                ),
                "texto": normalizar_basico(
                    texto
                ),
                "sha256": sha256_bytes(
                    dados
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
        "encoding": (
            "utf-8-replace"
        ),
        "texto": normalizar_basico(
            texto
        ),
        "sha256": sha256_bytes(
            dados
        ),
    }


# ============================================================
# FONTE OFICIAL
#
# IMPORTANTE:
# NÃO remove strike/del/s/line-through.
# Nesta auditoria queremos enxergar tudo que a página oficial
# expõe, inclusive trechos revogados/alterados.
# ============================================================

def baixar_oficial(
    url
):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    resposta.raise_for_status()

    dados = resposta.content

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
                    html.count("Art"),
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

        _, codificacao, html = (
            candidatos[
                0
            ]
        )

    else:
        codificacao = (
            "cp1252-replace"
        )

        html = dados.decode(
            "cp1252",
            errors="replace",
        )

    soup = BeautifulSoup(
        html,
        "lxml",
    )

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

    corpo = (
        soup.body
        or soup
    )

    texto = corpo.get_text(
        separator="\n",
        strip=True,
    )

    texto = normalizar_basico(
        texto
    )

    return {
        "url": url,
        "status_http": (
            resposta.status_code
        ),
        "bytes_html": len(
            dados
        ),
        "encoding_html": (
            codificacao
        ),
        "linhas": len(
            texto.splitlines()
        ),
        "caracteres": len(
            texto
        ),
        "texto": texto,
    }


# ============================================================
# BLOCOS
# ============================================================

def blocos_textuais(
    texto,
    min_chars=80,
):
    linhas = [
        normalizar_basico(
            linha
        )
        for linha in texto.splitlines()
    ]

    blocos = []

    acumulado = []

    tamanho = 0

    for linha in linhas:
        if not linha:
            if acumulado:
                bloco = " ".join(
                    acumulado
                ).strip()

                if len(
                    bloco
                ) >= min_chars:
                    blocos.append(
                        bloco
                    )

                acumulado = []
                tamanho = 0

            continue

        acumulado.append(
            linha
        )

        tamanho += len(
            linha
        )

        if tamanho >= 400:
            bloco = " ".join(
                acumulado
            ).strip()

            if len(
                bloco
            ) >= min_chars:
                blocos.append(
                    bloco
                )

            acumulado = []
            tamanho = 0

    if acumulado:
        bloco = " ".join(
            acumulado
        ).strip()

        if len(
            bloco
        ) >= min_chars:
            blocos.append(
                bloco
            )

    return blocos


# ============================================================
# SHINGLES
#
# Mede cobertura textual sem depender de formatação/linhas.
# ============================================================

def shingles(
    texto,
    n=7,
):
    palavras = (
        normalizar_comparacao(
            texto
        ).split()
    )

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


def cobertura_shingles(
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
# SIMILARIDADE DE BLOCOS
# ============================================================

def melhor_similaridade(
    bloco,
    texto_local_normalizado,
):
    bloco_norm = normalizar_comparacao(
        bloco
    )

    if not bloco_norm:
        return 1.0

    if bloco_norm in (
        texto_local_normalizado
    ):
        return 1.0

    palavras = bloco_norm.split()

    if len(
        palavras
    ) < 8:
        return 0.0

    # Assinaturas curtas do bloco:
    # início, meio e fim.
    pedacos = []

    janela = min(
        12,
        len(
            palavras
        ),
    )

    pedacos.append(
        " ".join(
            palavras[
                :janela
            ]
        )
    )

    if len(
        palavras
    ) > janela * 2:
        meio = (
            len(
                palavras
            )
            // 2
        )

        pedacos.append(
            " ".join(
                palavras[
                    meio - janela // 2:
                    meio + janela // 2
                ]
            )
        )

    pedacos.append(
        " ".join(
            palavras[
                -janela:
            ]
        )
    )

    presentes = sum(
        1
        for pedaco in pedacos
        if pedaco
        in texto_local_normalizado
    )

    if presentes == len(
        pedacos
    ):
        return 0.98

    if presentes >= 2:
        return 0.85

    if presentes == 1:
        return 0.60

    return 0.0


def encontrar_blocos_ausentes(
    oficial,
    local,
    limite=25,
):
    blocos = blocos_textuais(
        oficial
    )

    local_norm = (
        normalizar_comparacao(
            local
        )
    )

    ausentes = []

    for bloco in blocos:
        similaridade = (
            melhor_similaridade(
                bloco,
                local_norm,
            )
        )

        if similaridade < 0.60:
            resumo = re.sub(
                r"\s+",
                " ",
                bloco,
            ).strip()

            ausentes.append(
                {
                    "similaridade": (
                        similaridade
                    ),
                    "trecho": resumo[
                        :700
                    ],
                }
            )

            if len(
                ausentes
            ) >= limite:
                break

    return (
        len(
            blocos
        ),
        ausentes,
    )


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar(
    atual,
    oficial,
    backup,
):
    cobertura_oficial_local = (
        cobertura_shingles(
            oficial[
                "texto"
            ],
            atual[
                "texto"
            ],
        )
    )

    cobertura_local_oficial = (
        cobertura_shingles(
            atual[
                "texto"
            ],
            oficial[
                "texto"
            ],
        )
    )

    cobertura_backup_local = None
    cobertura_local_backup = None

    if backup:
        cobertura_backup_local = (
            cobertura_shingles(
                backup[
                    "texto"
                ],
                atual[
                    "texto"
                ],
            )
        )

        cobertura_local_backup = (
            cobertura_shingles(
                atual[
                    "texto"
                ],
                backup[
                    "texto"
                ],
            )
        )

    (
        total_blocos,
        blocos_ausentes,
    ) = encontrar_blocos_ausentes(
        oficial[
            "texto"
        ],
        atual[
            "texto"
        ],
    )

    proporcao_blocos_ausentes = (
        len(
            blocos_ausentes
        )
        / total_blocos
        if total_blocos
        else 0.0
    )

    motivos = []

    # Forte sinal de omissão:
    # grande parte da fonte oficial não existe localmente.
    if (
        cobertura_oficial_local
        < 0.70
    ):
        motivos.append(
            (
                "cobertura da fonte oficial no "
                "arquivo local abaixo de 70%"
            )
        )

    # Texto local significativamente menor.
    if (
        oficial[
            "caracteres"
        ] >= 5000
        and atual[
            "caracteres"
        ]
        < oficial[
            "caracteres"
        ]
        * 0.65
    ):
        motivos.append(
            (
                "arquivo local tem menos de 65% "
                "do tamanho textual da fonte oficial"
            )
        )

    # Backup muito mais completo que o atual.
    if (
        backup
        and backup[
            "bytes"
        ] >= 5000
        and atual[
            "bytes"
        ]
        < backup[
            "bytes"
        ]
        * 0.65
    ):
        motivos.append(
            (
                "arquivo local tem menos de 65% "
                "do tamanho do backup"
            )
        )

    if motivos:
        status = (
            "SUSPEITA_DE_OMISSAO"
        )

    elif (
        cobertura_oficial_local
        < 0.88
        or proporcao_blocos_ausentes
        > 0.08
    ):
        status = "REVISAR"

    else:
        status = "APROVADA"

    return {
        "status": status,
        "motivos": motivos,
        "cobertura_oficial_no_local": (
            cobertura_oficial_local
        ),
        "cobertura_local_no_oficial": (
            cobertura_local_oficial
        ),
        "cobertura_backup_no_local": (
            cobertura_backup_local
        ),
        "cobertura_local_no_backup": (
            cobertura_local_backup
        ),
        "blocos_oficiais": (
            total_blocos
        ),
        "blocos_ausentes_amostrados": (
            len(
                blocos_ausentes
            )
        ),
        "proporcao_ausentes_amostrada": (
            proporcao_blocos_ausentes
        ),
        "blocos_ausentes": (
            blocos_ausentes
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
        "AUDITORIA PROFUNDA DAS 8 NORMAS"
    )

    print(
        "=" * 68
    )

    print(
        f"Origem: {origem}"
    )

    print(
        "Modo: SOMENTE LEITURA NO CARTÃO"
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
            f"[{indice}/8] "
            f"{identificador} - {nome}"
        )

        atual_path = localizar_item(
            item,
            arquivos,
        )

        if atual_path is None:
            resultados.append(
                {
                    "id": identificador,
                    "nome": nome,
                    "status": (
                        "SUSPEITA_DE_OMISSAO"
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

        relativo = atual_path.relative_to(
            origem
        )

        backup_path = escolher_backup(
            relativo
        )

        try:
            atual = ler_arquivo(
                atual_path
            )

            oficial = baixar_oficial(
                item[
                    "fonte_oficial"
                ]
            )

            backup = (
                ler_arquivo(
                    backup_path
                )
                if backup_path
                else None
            )

            analise = classificar(
                atual,
                oficial,
                backup,
            )

            resultado = {
                "id": identificador,
                "nome": nome,
                "arquivo": str(
                    atual_path
                ),
                "fonte_oficial": item[
                    "fonte_oficial"
                ],
                "backup": (
                    str(
                        backup_path
                    )
                    if backup_path
                    else ""
                ),
                "status": analise[
                    "status"
                ],
                "motivos": analise[
                    "motivos"
                ],
                "local": {
                    "bytes": atual[
                        "bytes"
                    ],
                    "linhas": atual[
                        "linhas"
                    ],
                    "caracteres": atual[
                        "caracteres"
                    ],
                    "sha256": atual[
                        "sha256"
                    ],
                },
                "oficial": {
                    "bytes_html": oficial[
                        "bytes_html"
                    ],
                    "linhas": oficial[
                        "linhas"
                    ],
                    "caracteres": oficial[
                        "caracteres"
                    ],
                },
                "backup_info": (
                    {
                        "bytes": backup[
                            "bytes"
                        ],
                        "linhas": backup[
                            "linhas"
                        ],
                        "caracteres": backup[
                            "caracteres"
                        ],
                        "sha256": backup[
                            "sha256"
                        ],
                    }
                    if backup
                    else None
                ),
                "cobertura_oficial_no_local": (
                    analise[
                        "cobertura_oficial_no_local"
                    ]
                ),
                "cobertura_local_no_oficial": (
                    analise[
                        "cobertura_local_no_oficial"
                    ]
                ),
                "cobertura_backup_no_local": (
                    analise[
                        "cobertura_backup_no_local"
                    ]
                ),
                "cobertura_local_no_backup": (
                    analise[
                        "cobertura_local_no_backup"
                    ]
                ),
                "blocos_oficiais": (
                    analise[
                        "blocos_oficiais"
                    ]
                ),
                "blocos_ausentes_amostrados": (
                    analise[
                        "blocos_ausentes_amostrados"
                    ]
                ),
                "proporcao_ausentes_amostrada": (
                    analise[
                        "proporcao_ausentes_amostrada"
                    ]
                ),
                "blocos_ausentes": (
                    analise[
                        "blocos_ausentes"
                    ]
                ),
            }

            resultados.append(
                resultado
            )

            print(
                (
                    f"  {resultado['status']} "
                    "| cobertura oficial→local="
                    f"{resultado['cobertura_oficial_no_local']:.3f} "
                    "| local→oficial="
                    f"{resultado['cobertura_local_no_oficial']:.3f}"
                )
            )

        except Exception as erro:
            resultados.append(
                {
                    "id": identificador,
                    "nome": nome,
                    "arquivo": str(
                        atual_path
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
    # RELATÓRIOS
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
        == "APROVADA"
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
        == "SUSPEITA_DE_OMISSAO"
    ]

    linhas = [
        "LEX MACHINA",
        "AUDITORIA PROFUNDA DAS 8 NORMAS SUSPEITAS",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        f"ORIGEM: {origem}",
        (
            "VERSÃO DO CATÁLOGO: "
            f"{catalogo.get('versao', '')}"
        ),
        "MODO: SOMENTE LEITURA NO CARTÃO",
        "",
        f"TOTAL: {len(resultados)}",
        f"APROVADAS: {len(aprovadas)}",
        f"REVISAR: {len(revisar)}",
        (
            "SUSPEITA DE OMISSÃO: "
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
                "  Cobertura oficial -> local: "
                f"{item['cobertura_oficial_no_local']:.4f}"
            )
        )

        linhas.append(
            (
                "  Cobertura local -> oficial: "
                f"{item['cobertura_local_no_oficial']:.4f}"
            )
        )

        if (
            item[
                "cobertura_backup_no_local"
            ]
            is not None
        ):
            linhas.append(
                (
                    "  Cobertura backup -> local: "
                    f"{item['cobertura_backup_no_local']:.4f}"
                )
            )

            linhas.append(
                (
                    "  Cobertura local -> backup: "
                    f"{item['cobertura_local_no_backup']:.4f}"
                )
            )

        linhas.append(
            (
                "  Local: "
                f"{item['local']['bytes']} bytes "
                f"| {item['local']['linhas']} linhas "
                f"| {item['local']['caracteres']} caracteres"
            )
        )

        linhas.append(
            (
                "  Oficial: "
                f"{item['oficial']['linhas']} linhas "
                f"| {item['oficial']['caracteres']} caracteres"
            )
        )

        if item[
            "backup_info"
        ]:
            linhas.append(
                (
                    "  Backup: "
                    f"{item['backup_info']['bytes']} bytes "
                    f"| {item['backup_info']['linhas']} linhas "
                    f"| {item['backup_info']['caracteres']} caracteres"
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

        linhas.append(
            (
                "  Blocos oficiais analisados: "
                f"{item['blocos_oficiais']}"
            )
        )

        linhas.append(
            (
                "  Blocos ausentes amostrados: "
                f"{item['blocos_ausentes_amostrados']}"
            )
        )

        if item[
            "blocos_ausentes"
        ]:
            linhas.append(
                "  Exemplos de possíveis omissões:"
            )

            for bloco in (
                item[
                    "blocos_ausentes"
                ][
                    :10
                ]
            ):
                linhas.append(
                    (
                        "    - "
                        f"{bloco['trecho']}"
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
                "NÃO APROVADO: existem normas com "
                "forte suspeita de omissão textual."
            )
        )

    elif revisar:
        linhas.append(
            (
                "AINDA NÃO APROVADO: não foi detectada "
                "omissão grave automática, mas existem "
                "normas que exigem revisão."
            )
        )

    else:
        linhas.append(
            (
                "AS 8 NORMAS PASSARAM NESTA AUDITORIA "
                "TEXTUAL PROFUNDA."
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
                    "aprovadas": len(
                        aprovadas
                    ),
                    "revisar": len(
                        revisar
                    ),
                    "suspeita_omissao": len(
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
        "AUDITORIA PROFUNDA FINALIZADA"
    )

    print(
        f"APROVADAS: {len(aprovadas)}"
    )

    print(
        f"REVISAR: {len(revisar)}"
    )

    print(
        "SUSPEITA DE OMISSÃO: "
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
