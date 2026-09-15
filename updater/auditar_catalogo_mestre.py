from datetime import datetime
from pathlib import Path
from collections import Counter
import argparse
import json
import re
import sys
import unicodedata


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO = Path(
    "catalogo_mestre_vademecum.json"
)

PASTA_RELATORIOS = Path(
    "saida/99_INDICES"
)

RELATORIO_TXT = (
    PASTA_RELATORIOS
    / "AUDITORIA_CATALOGO_MESTRE.txt"
)

RELATORIO_JSON = (
    PASTA_RELATORIOS
    / "AUDITORIA_CATALOGO_MESTRE.json"
)


# ============================================================
# ARGUMENTOS
# ============================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - Auditoria final do "
            "Catálogo Mestre do Vade Mecum"
        )
    )

    parser.add_argument(
        "origem",
        help=(
            "Unidade ou pasta do Vade Mecum. "
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


# ============================================================
# CATÁLOGO
# ============================================================

def carregar_catalogo():
    if not CATALOGO.exists():
        raise FileNotFoundError(
            f"Catálogo mestre não encontrado: "
            f"{CATALOGO}"
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

    return dados, itens


# ============================================================
# INVENTÁRIO DO CARTÃO
# ============================================================

def inventariar(origem):
    arquivos = []

    for caminho in origem.rglob("*"):
        if not caminho.is_file():
            continue

        try:
            relativo = caminho.relative_to(
                origem
            )

        except ValueError:
            relativo = caminho

        arquivos.append(
            {
                "absoluto": caminho,
                "relativo": relativo,
                "nome": caminho.name,
                "nome_normalizado": normalizar(
                    caminho.name
                ),
                "nome_compacto": compactar(
                    caminho.name
                ),
                "caminho_normalizado": normalizar(
                    str(
                        relativo
                    )
                ),
                "caminho_compacto": compactar(
                    str(
                        relativo
                    )
                ),
            }
        )

    return arquivos


# ============================================================
# DETECÇÃO DO ARQUIVO
# ============================================================

def localizar_item(
    item,
    arquivos,
):
    arquivo_sugerido = str(
        item.get(
            "arquivo_sugerido",
            ""
        )
    ).strip()

    sugerido_compacto = compactar(
        arquivo_sugerido
    )

    pasta_destino = str(
        item.get(
            "pasta_destino",
            ""
        )
    ).strip()

    pasta_destino_normalizada = (
        normalizar(
            pasta_destino
        )
    )

    candidatos = []

    # --------------------------------------------------------
    # 1. NOME EXATO DO ARQUIVO
    # --------------------------------------------------------

    for arquivo in arquivos:
        if (
            sugerido_compacto
            and arquivo[
                "nome_compacto"
            ] == sugerido_compacto
        ):
            candidatos.append(
                arquivo
            )

    # --------------------------------------------------------
    # 2. FALLBACK POR PASTA + TERMOS
    # --------------------------------------------------------

    if not candidatos:
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

        for arquivo in arquivos:
            caminho_norm = arquivo[
                "caminho_normalizado"
            ]

            dentro_pasta = (
                not pasta_destino_normalizada
                or pasta_destino_normalizada
                in caminho_norm
            )

            if not dentro_pasta:
                continue

            for termo in termos:
                if (
                    termo
                    and termo in caminho_norm
                ):
                    candidatos.append(
                        arquivo
                    )
                    break

    return candidatos


# ============================================================
# LEITURA TXT
# ============================================================

def analisar_txt(caminho):
    resultado = {
        "legivel": False,
        "codificacao": "",
        "caracteres": 0,
        "linhas": 0,
        "vazio": False,
        "erro": "",
    }

    for codificacao in (
        "utf-8",
        "cp1252",
        "latin-1",
    ):
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

        except UnicodeDecodeError:
            continue

        except Exception as erro:
            resultado[
                "erro"
            ] = str(
                erro
            )

            return resultado

    resultado[
        "erro"
    ] = (
        "Não foi possível decodificar o arquivo."
    )

    return resultado


# ============================================================
# AUDITORIA DE UM ITEM
# ============================================================

def auditar_item(
    item,
    arquivos,
):
    encontrados = localizar_item(
        item,
        arquivos,
    )

    problemas = []

    if not encontrados:
        problemas.append(
            "arquivo_ausente"
        )

        return {
            "id": item.get(
                "id"
            ),
            "nome": item.get(
                "nome"
            ),
            "prioridade": item.get(
                "prioridade"
            ),
            "ramo": item.get(
                "ramo"
            ),
            "pasta_destino": item.get(
                "pasta_destino"
            ),
            "arquivo_sugerido": item.get(
                "arquivo_sugerido"
            ),
            "status": "PROBLEMA",
            "problemas": problemas,
            "encontrados": [],
            "analise_txt": [],
        }

    if len(
        encontrados
    ) > 1:
        problemas.append(
            "arquivo_duplicado"
        )

    analises = []

    pasta_esperada = normalizar(
        item.get(
            "pasta_destino",
            ""
        )
    )

    for arquivo in encontrados:
        relativo = str(
            arquivo[
                "relativo"
            ]
        )

        # ----------------------------------------------------
        # PASTA ESPERADA
        # ----------------------------------------------------

        if (
            pasta_esperada
            and pasta_esperada
            not in arquivo[
                "caminho_normalizado"
            ]
        ):
            problemas.append(
                "pasta_incorreta"
            )

        # ----------------------------------------------------
        # EXTENSÃO
        # ----------------------------------------------------

        if (
            arquivo[
                "absoluto"
            ].suffix.lower()
            != ".txt"
        ):
            problemas.append(
                "extensao_inesperada"
            )

            analises.append(
                {
                    "arquivo": relativo,
                    "legivel": False,
                    "codificacao": "",
                    "caracteres": 0,
                    "linhas": 0,
                    "vazio": False,
                    "erro": (
                        "Arquivo não é .txt"
                    ),
                }
            )

            continue

        analise = analisar_txt(
            arquivo[
                "absoluto"
            ]
        )

        analise[
            "arquivo"
        ] = relativo

        analises.append(
            analise
        )

        if not analise[
            "legivel"
        ]:
            problemas.append(
                "txt_nao_legivel"
            )

        if analise[
            "vazio"
        ]:
            problemas.append(
                "txt_vazio"
            )

        if (
            analise[
                "caracteres"
            ] > 0
            and analise[
                "caracteres"
            ] < 300
        ):
            problemas.append(
                "txt_muito_pequeno"
            )

    # Remove duplicidades de rótulos de problema
    problemas = list(
        dict.fromkeys(
            problemas
        )
    )

    status = (
        "OK"
        if not problemas
        else "PROBLEMA"
    )

    return {
        "id": item.get(
            "id"
        ),
        "nome": item.get(
            "nome"
        ),
        "prioridade": item.get(
            "prioridade"
        ),
        "ramo": item.get(
            "ramo"
        ),
        "pasta_destino": item.get(
            "pasta_destino"
        ),
        "arquivo_sugerido": item.get(
            "arquivo_sugerido"
        ),
        "status": status,
        "problemas": problemas,
        "encontrados": [
            str(
                arquivo[
                    "relativo"
                ]
            )
            for arquivo in encontrados
        ],
        "analise_txt": analises,
    }


# ============================================================
# DUPLICIDADE ENTRE ITENS DO CATÁLOGO
# ============================================================

def auditar_catalogo_interno(
    itens
):
    problemas = []

    ids = Counter(
        str(
            item.get(
                "id",
                ""
            )
        ).strip()
        for item in itens
    )

    for identificador, qtd in ids.items():
        if (
            identificador
            and qtd > 1
        ):
            problemas.append(
                {
                    "tipo": "id_duplicado",
                    "detalhe": (
                        f"ID duplicado no catálogo: "
                        f"{identificador}"
                    ),
                }
            )

    nomes_arquivo = Counter(
        str(
            item.get(
                "arquivo_sugerido",
                ""
            )
        ).strip().casefold()
        for item in itens
    )

    for nome, qtd in nomes_arquivo.items():
        if (
            nome
            and qtd > 1
        ):
            problemas.append(
                {
                    "tipo": (
                        "arquivo_sugerido_duplicado"
                    ),
                    "detalhe": (
                        f"Arquivo sugerido duplicado "
                        f"no catálogo: {nome}"
                    ),
                }
            )

    return problemas


# ============================================================
# RELATÓRIO
# ============================================================

def gerar_relatorios(
    catalogo,
    resultados,
    problemas_catalogo,
):
    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    ok = [
        item
        for item in resultados
        if item[
            "status"
        ] == "OK"
    ]

    com_problema = [
        item
        for item in resultados
        if item[
            "status"
        ] == "PROBLEMA"
    ]

    contador_problemas = Counter()

    for item in com_problema:
        for problema in item[
            "problemas"
        ]:
            contador_problemas[
                problema
            ] += 1

    for problema in problemas_catalogo:
        contador_problemas[
            problema[
                "tipo"
            ]
        ] += 1

    linhas = [
        "LEX MACHINA",
        "AUDITORIA FINAL DO CATÁLOGO MESTRE",
        "=" * 78,
        "",
        (
            "GERADO EM: "
            + agora()
        ),
        (
            "VERSÃO DO CATÁLOGO: "
            f"{catalogo.get('versao', '')}"
        ),
        "",
        f"ITENS AUDITADOS: {len(resultados)}",
        f"ITENS OK: {len(ok)}",
        (
            "ITENS COM PROBLEMA: "
            f"{len(com_problema)}"
        ),
        (
            "PROBLEMAS INTERNOS DO CATÁLOGO: "
            f"{len(problemas_catalogo)}"
        ),
        "",
        "=" * 78,
        "RESUMO DE PROBLEMAS",
        "=" * 78,
        "",
    ]

    if not contador_problemas:
        linhas.append(
            "Nenhum problema encontrado."
        )

    else:
        for tipo, qtd in sorted(
            contador_problemas.items()
        ):
            linhas.append(
                f"- {tipo}: {qtd}"
            )

    linhas.extend(
        [
            "",
            "=" * 78,
            "RESULTADO POR ITEM",
            "=" * 78,
            "",
        ]
    )

    for item in resultados:
        simbolo = (
            "✓"
            if item[
                "status"
            ] == "OK"
            else "⚠"
        )

        linhas.append(
            (
                f"{simbolo} "
                f"[{item['status']}] "
                f"{item['nome']}"
            )
        )

        linhas.append(
            (
                "   Prioridade: "
                f"{item['prioridade']}"
            )
        )

        linhas.append(
            (
                "   Ramo: "
                f"{item['ramo']}"
            )
        )

        linhas.append(
            (
                "   Pasta esperada: "
                f"{item['pasta_destino']}"
            )
        )

        linhas.append(
            (
                "   Arquivo esperado: "
                f"{item['arquivo_sugerido']}"
            )
        )

        if item[
            "encontrados"
        ]:
            for caminho in item[
                "encontrados"
            ]:
                linhas.append(
                    (
                        "   Encontrado em: "
                        f"{caminho}"
                    )
                )

        if item[
            "problemas"
        ]:
            for problema in item[
                "problemas"
            ]:
                linhas.append(
                    (
                        "   PROBLEMA: "
                        f"{problema}"
                    )
                )

        for analise in item[
            "analise_txt"
        ]:
            linhas.append(
                (
                    "   TXT: "
                    f"{analise['arquivo']} "
                    f"| codificação="
                    f"{analise['codificacao']} "
                    f"| caracteres="
                    f"{analise['caracteres']} "
                    f"| linhas="
                    f"{analise['linhas']}"
                )
            )

        linhas.append("")

    if problemas_catalogo:
        linhas.extend(
            [
                "=" * 78,
                "PROBLEMAS INTERNOS DO CATÁLOGO",
                "=" * 78,
                "",
            ]
        )

        for problema in problemas_catalogo:
            linhas.append(
                (
                    f"- {problema['tipo']}: "
                    f"{problema['detalhe']}"
                )
            )

    aprovado = (
        not com_problema
        and not problemas_catalogo
    )

    linhas.extend(
        [
            "",
            "=" * 78,
            "CONCLUSÃO",
            "=" * 78,
            "",
        ]
    )

    if aprovado:
        linhas.extend(
            [
                "AUDITORIA APROVADA.",
                "",
                (
                    "Todos os itens do Catálogo Mestre "
                    "foram encontrados e passaram nas "
                    "verificações básicas."
                ),
            ]
        )

    else:
        linhas.extend(
            [
                "AUDITORIA REQUER ATENÇÃO.",
                "",
                (
                    "Há itens ou registros do catálogo "
                    "que precisam ser corrigidos antes "
                    "de encerrar esta fase."
                ),
            ]
        )

    RELATORIO_TXT.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )

    estrutura = {
        "gerado_em": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "versao_catalogo": catalogo.get(
            "versao"
        ),
        "resumo": {
            "itens_auditados": len(
                resultados
            ),
            "itens_ok": len(
                ok
            ),
            "itens_com_problema": len(
                com_problema
            ),
            "problemas_catalogo": len(
                problemas_catalogo
            ),
            "aprovado": aprovado,
        },
        "problemas_por_tipo": dict(
            contador_problemas
        ),
        "problemas_catalogo": (
            problemas_catalogo
        ),
        "resultados": resultados,
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

    return (
        aprovado,
        RELATORIO_TXT,
        RELATORIO_JSON,
    )


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
        "AUDITORIA FINAL DO CATÁLOGO MESTRE"
    )

    print(
        "=" * 60
    )

    print(
        f"Origem: {origem}"
    )

    print(
        f"Itens no catálogo: {len(itens)}"
    )

    print(
        f"Arquivos no cartão: {len(arquivos)}"
    )

    print()

    problemas_catalogo = (
        auditar_catalogo_interno(
            itens
        )
    )

    resultados = []

    for indice, item in enumerate(
        itens,
        start=1,
    ):
        resultado = auditar_item(
            item,
            arquivos,
        )

        resultados.append(
            resultado
        )

        marca = (
            "✓"
            if resultado[
                "status"
            ] == "OK"
            else "⚠"
        )

        print(
            (
                f"[{indice}/{len(itens)}] "
                f"{marca} "
                f"{item.get('nome')}"
            )
        )

    (
        aprovado,
        relatorio_txt,
        relatorio_json,
    ) = gerar_relatorios(
        catalogo,
        resultados,
        problemas_catalogo,
    )

    itens_ok = sum(
        1
        for item in resultados
        if item[
            "status"
        ] == "OK"
    )

    itens_problema = (
        len(
            resultados
        )
        - itens_ok
    )

    print()
    print(
        "=" * 60
    )

    print(
        "AUDITORIA FINALIZADA"
    )

    print(
        f"Itens OK: {itens_ok}"
    )

    print(
        "Itens com problema: "
        f"{itens_problema}"
    )

    print(
        "Problemas internos do catálogo: "
        f"{len(problemas_catalogo)}"
    )

    print()

    if aprovado:
        print(
            "✓ AUDITORIA APROVADA"
        )

    else:
        print(
            "⚠ AUDITORIA REQUER ATENÇÃO"
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
        "Nenhum arquivo do cartão "
        "foi alterado."
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
