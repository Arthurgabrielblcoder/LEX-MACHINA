from collections import Counter
from datetime import datetime
from pathlib import Path
import argparse
import json
import os
import re
import sys


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PASTA_RELATORIOS = Path(
    "saida/99_INDICES"
)

RELATORIO_TXT = (
    PASTA_RELATORIOS
    / "INVENTARIO_VADE_MECUM_COMPLETO.txt"
)

RELATORIO_JSON = (
    PASTA_RELATORIOS
    / "INVENTARIO_VADE_MECUM_COMPLETO.json"
)


# ============================================================
# ARGUMENTOS
# ============================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - Auditoria geral "
            "do Vade Mecum completo"
        )
    )

    parser.add_argument(
        "origem",
        help=(
            "Pasta ou unidade a ser auditada. "
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


def limpar(texto):
    return re.sub(
        r"\s+",
        " ",
        str(texto or ""),
    ).strip()


def formatar_bytes(
    quantidade
):
    valor = float(
        quantidade
    )

    unidade = "B"

    for unidade in (
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
    ):
        if valor < 1024:
            break

        valor /= 1024

    return (
        f"{valor:.2f} {unidade}"
    )


# ============================================================
# LEITURA DE TXT
# ============================================================

def analisar_txt(
    caminho
):
    resultado = {
        "legivel": False,
        "codificacao": "",
        "caracteres": 0,
        "linhas": 0,
        "vazio": False,
        "erro": "",
    }

    codificacoes = [
        "utf-8",
        "cp1252",
        "latin-1",
    ]

    texto = None

    for codificacao in codificacoes:

        try:
            texto = caminho.read_text(
                encoding=codificacao
            )

            resultado[
                "legivel"
            ] = True

            resultado[
                "codificacao"
            ] = codificacao

            break

        except UnicodeDecodeError:
            continue

        except Exception as erro:
            resultado[
                "erro"
            ] = str(
                erro
            )

            return resultado

    if texto is None:
        resultado[
            "erro"
        ] = (
            "Não foi possível decodificar "
            "o arquivo."
        )

        return resultado

    resultado[
        "caracteres"
    ] = len(
        texto
    )

    resultado[
        "linhas"
    ] = len(
        texto.splitlines()
    )

    resultado[
        "vazio"
    ] = not bool(
        texto.strip()
    )

    return resultado


# ============================================================
# INVENTÁRIO
# ============================================================

def inventariar(
    origem
):
    pastas = []

    arquivos = []

    problemas = []

    if not origem.exists():

        raise FileNotFoundError(
            f"A origem não existe: {origem}"
        )

    if not origem.is_dir():

        raise ValueError(
            "A origem precisa ser uma pasta "
            "ou unidade."
        )

    for raiz, diretorios, nomes in os.walk(
        origem
    ):

        raiz_path = Path(
            raiz
        )

        for diretorio in diretorios:

            pasta = (
                raiz_path
                / diretorio
            )

            try:
                relativo = pasta.relative_to(
                    origem
                )

            except ValueError:
                relativo = pasta

            pastas.append(
                {
                    "nome": diretorio,
                    "caminho": str(
                        relativo
                    ),
                }
            )

        for nome in nomes:

            caminho = (
                raiz_path
                / nome
            )

            try:

                relativo = caminho.relative_to(
                    origem
                )

            except ValueError:

                relativo = caminho

            try:

                tamanho = (
                    caminho.stat().st_size
                )

            except OSError as erro:

                tamanho = 0

                problemas.append(
                    {
                        "tipo": (
                            "erro_leitura_metadados"
                        ),
                        "arquivo": str(
                            relativo
                        ),
                        "erro": str(
                            erro
                        ),
                    }
                )

            item = {
                "nome": nome,
                "caminho": str(
                    relativo
                ),
                "extensao": (
                    caminho.suffix.lower()
                ),
                "tamanho_bytes": tamanho,
            }

            if (
                caminho.suffix.lower()
                == ".txt"
            ):

                analise = analisar_txt(
                    caminho
                )

                item[
                    "txt"
                ] = analise

                if not analise[
                    "legivel"
                ]:

                    problemas.append(
                        {
                            "tipo": (
                                "txt_nao_legivel"
                            ),
                            "arquivo": str(
                                relativo
                            ),
                            "erro": analise[
                                "erro"
                            ],
                        }
                    )

                elif analise[
                    "vazio"
                ]:

                    problemas.append(
                        {
                            "tipo": (
                                "txt_vazio"
                            ),
                            "arquivo": str(
                                relativo
                            ),
                        }
                    )

            arquivos.append(
                item
            )

    return (
        pastas,
        arquivos,
        problemas,
    )


# ============================================================
# PASTAS PRINCIPAIS
# ============================================================

def pastas_principais(
    origem
):
    resultado = []

    for item in sorted(
        origem.iterdir(),
        key=lambda x: x.name.casefold(),
    ):

        if item.is_dir():

            resultado.append(
                item.name
            )

    return resultado


# ============================================================
# ARQUIVOS POR PASTA RAIZ
# ============================================================

def arquivos_por_area(
    arquivos
):
    contador = Counter()

    for item in arquivos:

        partes = Path(
            item[
                "caminho"
            ]
        ).parts

        if partes:

            contador[
                partes[0]
            ] += 1

    return contador


# ============================================================
# EXTENSÕES
# ============================================================

def extensoes(
    arquivos
):
    contador = Counter()

    for item in arquivos:

        extensao = (
            item[
                "extensao"
            ]
            or "[sem extensão]"
        )

        contador[
            extensao
        ] += 1

    return contador


# ============================================================
# NOMES DUPLICADOS
# ============================================================

def nomes_duplicados(
    arquivos
):
    mapa = {}

    for item in arquivos:

        chave = (
            item[
                "nome"
            ].casefold()
        )

        mapa.setdefault(
            chave,
            []
        ).append(
            item[
                "caminho"
            ]
        )

    return {
        nome: caminhos
        for nome, caminhos
        in mapa.items()
        if len(
            caminhos
        ) > 1
    }


# ============================================================
# RELATÓRIO TXT
# ============================================================

def gerar_txt(
    origem,
    pastas,
    arquivos,
    problemas,
):
    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    principais = (
        pastas_principais(
            origem
        )
    )

    por_area = (
        arquivos_por_area(
            arquivos
        )
    )

    por_extensao = (
        extensoes(
            arquivos
        )
    )

    duplicados = (
        nomes_duplicados(
            arquivos
        )
    )

    tamanho_total = sum(
        item[
            "tamanho_bytes"
        ]
        for item in arquivos
    )

    txts = [
        item
        for item in arquivos
        if item[
            "extensao"
        ] == ".txt"
    ]

    linhas = [
        "LEX MACHINA",
        "INVENTÁRIO DO VADE MECUM COMPLETO",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        f"ORIGEM: {origem}",
        "",
        "RESUMO",
        "-" * 78,
        (
            "Pastas encontradas: "
            f"{len(pastas)}"
        ),
        (
            "Arquivos encontrados: "
            f"{len(arquivos)}"
        ),
        (
            "Arquivos TXT: "
            f"{len(txts)}"
        ),
        (
            "Tamanho total: "
            f"{formatar_bytes(tamanho_total)}"
        ),
        (
            "Problemas detectados: "
            f"{len(problemas)}"
        ),
        (
            "Nomes de arquivo duplicados: "
            f"{len(duplicados)}"
        ),
        "",
        "=" * 78,
        "PASTAS PRINCIPAIS",
        "=" * 78,
        "",
    ]

    for pasta in principais:

        linhas.append(
            (
                f"- {pasta}: "
                f"{por_area[pasta]} "
                "arquivo(s)"
            )
        )

    linhas.extend(
        [
            "",
            "=" * 78,
            "TIPOS DE ARQUIVO",
            "=" * 78,
            "",
        ]
    )

    for extensao, quantidade in sorted(
        por_extensao.items()
    ):

        linhas.append(
            f"- {extensao}: "
            f"{quantidade}"
        )

    linhas.extend(
        [
            "",
            "=" * 78,
            "ESTRUTURA COMPLETA",
            "=" * 78,
            "",
        ]
    )

    for pasta in sorted(
        pastas,
        key=lambda x: (
            x[
                "caminho"
            ].casefold()
        ),
    ):

        linhas.append(
            "[PASTA] "
            + pasta[
                "caminho"
            ]
        )

    linhas.extend(
        [
            "",
            "=" * 78,
            "ARQUIVOS",
            "=" * 78,
            "",
        ]
    )

    for item in sorted(
        arquivos,
        key=lambda x: (
            x[
                "caminho"
            ].casefold()
        ),
    ):

        linhas.append(
            (
                f"[ARQUIVO] "
                f"{item['caminho']}"
            )
        )

        linhas.append(
            (
                "          tamanho: "
                f"{formatar_bytes(item['tamanho_bytes'])}"
            )
        )

        if "txt" in item:

            analise = item[
                "txt"
            ]

            linhas.append(
                (
                    "          codificação: "
                    f"{analise['codificacao']}"
                )
            )

            linhas.append(
                (
                    "          caracteres: "
                    f"{analise['caracteres']}"
                )
            )

            linhas.append(
                (
                    "          linhas: "
                    f"{analise['linhas']}"
                )
            )

        linhas.append("")

    linhas.extend(
        [
            "=" * 78,
            "NOMES DUPLICADOS",
            "=" * 78,
            "",
        ]
    )

    if not duplicados:

        linhas.append(
            "Nenhum nome duplicado."
        )

    else:

        for nome, caminhos in sorted(
            duplicados.items()
        ):

            linhas.append(
                f"{nome}"
            )

            for caminho in caminhos:

                linhas.append(
                    f"  - {caminho}"
                )

            linhas.append("")

    linhas.extend(
        [
            "",
            "=" * 78,
            "PROBLEMAS",
            "=" * 78,
            "",
        ]
    )

    if not problemas:

        linhas.append(
            "Nenhum problema estrutural "
            "básico detectado."
        )

    else:

        for problema in problemas:

            linhas.append(
                json.dumps(
                    problema,
                    ensure_ascii=False,
                )
            )

    RELATORIO_TXT.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )

    return RELATORIO_TXT


# ============================================================
# RELATÓRIO JSON
# ============================================================

def gerar_json(
    origem,
    pastas,
    arquivos,
    problemas,
):
    duplicados = (
        nomes_duplicados(
            arquivos
        )
    )

    tamanho_total = sum(
        item[
            "tamanho_bytes"
        ]
        for item in arquivos
    )

    estrutura = {
        "gerado_em": (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ),

        "origem": str(
            origem
        ),

        "resumo": {
            "pastas": len(
                pastas
            ),
            "arquivos": len(
                arquivos
            ),
            "txt": sum(
                1
                for item in arquivos
                if item[
                    "extensao"
                ] == ".txt"
            ),
            "tamanho_total_bytes": (
                tamanho_total
            ),
            "problemas": len(
                problemas
            ),
            "nomes_duplicados": len(
                duplicados
            ),
        },

        "pastas_principais": (
            pastas_principais(
                origem
            )
        ),

        "arquivos_por_area": dict(
            arquivos_por_area(
                arquivos
            )
        ),

        "extensoes": dict(
            extensoes(
                arquivos
            )
        ),

        "pastas": pastas,

        "arquivos": arquivos,

        "duplicados": duplicados,

        "problemas": problemas,
    }

    RELATORIO_JSON.write_text(
        json.dumps(
            estrutura,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return RELATORIO_JSON


# ============================================================
# MAIN
# ============================================================

def main():
    args = argumentos()

    origem = Path(
        args.origem
    )

    print()
    print(
        "LEX MACHINA - "
        "AUDITORIA DO VADE MECUM COMPLETO"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Origem: {origem}"
    )

    print()

    print(
        "Lendo todo o acervo..."
    )

    (
        pastas,
        arquivos,
        problemas,
    ) = inventariar(
        origem
    )

    tamanho_total = sum(
        item[
            "tamanho_bytes"
        ]
        for item in arquivos
    )

    print()
    print(
        "INVENTÁRIO CONCLUÍDO"
    )

    print(
        "-" * 60
    )

    print(
        f"Pastas: "
        f"{len(pastas)}"
    )

    print(
        f"Arquivos: "
        f"{len(arquivos)}"
    )

    print(
        "Arquivos TXT: "
        f"{sum(1 for x in arquivos if x['extensao'] == '.txt')}"
    )

    print(
        "Tamanho total: "
        f"{formatar_bytes(tamanho_total)}"
    )

    print(
        "Problemas: "
        f"{len(problemas)}"
    )

    print()

    relatorio_txt = gerar_txt(
        origem,
        pastas,
        arquivos,
        problemas,
    )

    relatorio_json = gerar_json(
        origem,
        pastas,
        arquivos,
        problemas,
    )

    print(
        "=" * 60
    )

    print(
        "AUDITORIA FINALIZADA"
    )

    print()

    print(
        f"Relatório TXT: "
        f"{relatorio_txt}"
    )

    print(
        f"Relatório JSON: "
        f"{relatorio_json}"
    )

    print()

    print(
        "Nenhum arquivo do Vade Mecum "
        "foi alterado."
    )


if __name__ == "__main__":

    try:
        main()

    except Exception as erro:

        print()
        print(
            "ERRO:"
        )

        print(
            erro
        )

        sys.exit(
            1
        )