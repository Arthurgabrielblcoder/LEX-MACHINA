from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import json
import os


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO_NORMAS = Path(
    "catalogo_normas.json"
)

CATALOGO_JURIS = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_SAIDA = Path(
    "saida"
)

PASTA_INDICES = (
    PASTA_SAIDA
    / "99_INDICES"
)

RELATORIO_TXT = (
    PASTA_INDICES
    / "AUDITORIA_GERAL_ACERVO.txt"
)

RELATORIO_JSON = (
    PASTA_INDICES
    / "AUDITORIA_GERAL_ACERVO.json"
)


# ============================================================
# UTILITÁRIOS
# ============================================================

def agora():
    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def limpar(texto):
    return str(
        texto or ""
    ).strip()


def carregar_json(
    caminho
):
    if not caminho.exists():
        return []

    try:
        dados = json.loads(
            caminho.read_text(
                encoding="utf-8"
            )
        )

    except Exception as erro:
        raise RuntimeError(
            f"Erro ao carregar {caminho}: {erro}"
        )

    if not isinstance(
        dados,
        list
    ):
        raise ValueError(
            f"{caminho} não contém uma lista JSON."
        )

    return dados


# ============================================================
# ÁRVORE DA SAÍDA
# ============================================================

def inventariar_saida():

    pastas = []
    arquivos = []

    if not PASTA_SAIDA.exists():
        return pastas, arquivos

    for raiz, diretorios, nomes in os.walk(
        PASTA_SAIDA
    ):

        raiz_path = Path(
            raiz
        )

        for diretorio in diretorios:

            caminho = (
                raiz_path
                / diretorio
            )

            pastas.append(
                caminho
            )

        for nome in nomes:

            caminho = (
                raiz_path
                / nome
            )

            try:
                tamanho = (
                    caminho.stat().st_size
                )

            except OSError:
                tamanho = 0

            arquivos.append(
                {
                    "caminho": str(
                        caminho
                    ),
                    "nome": nome,
                    "extensao": (
                        caminho.suffix.lower()
                    ),
                    "tamanho_bytes": tamanho,
                }
            )

    return pastas, arquivos


# ============================================================
# CATÁLOGO DE NORMAS
# ============================================================

def analisar_normas(
    registros
):

    normas = []
    referencias = []

    por_pasta = Counter()

    for item in registros:

        tipo = limpar(
            item.get(
                "tipo_registro",
                "norma",
            )
        )

        if tipo == "referencia":

            referencias.append(
                item
            )

            destino = limpar(
                item.get(
                    "destino_ref",
                    ""
                )
            )

            if destino:
                por_pasta[
                    destino
                ] += 1

        else:

            normas.append(
                item
            )

            destino = limpar(
                item.get(
                    "pasta_destino",
                    ""
                )
            )

            if destino:
                por_pasta[
                    destino
                ] += 1

    return {
        "normas": normas,
        "referencias": referencias,
        "por_pasta": por_pasta,
    }


# ============================================================
# CATÁLOGO DE JURISPRUDÊNCIA
# ============================================================

def analisar_jurisprudencia(
    registros
):

    por_tribunal = Counter()
    por_tipo = Counter()
    por_status = Counter()

    for item in registros:

        tribunal = limpar(
            item.get(
                "tribunal",
                "NÃO INFORMADO",
            )
        )

        tipo = limpar(
            item.get(
                "tipo",
                "NÃO INFORMADO",
            )
        )

        status = limpar(
            item.get(
                "status",
                "NÃO INFORMADO",
            )
        )

        por_tribunal[
            tribunal
        ] += 1

        por_tipo[
            tipo
        ] += 1

        por_status[
            status
        ] += 1

    return {
        "por_tribunal": por_tribunal,
        "por_tipo": por_tipo,
        "por_status": por_status,
    }


# ============================================================
# TAMANHOS
# ============================================================

def tamanho_total(
    arquivos
):

    return sum(
        item[
            "tamanho_bytes"
        ]
        for item
        in arquivos
    )


def formatar_bytes(
    quantidade
):

    unidade = "B"
    valor = float(
        quantidade
    )

    for unidade in [
        "B",
        "KB",
        "MB",
        "GB",
    ]:

        if valor < 1024:
            break

        valor /= 1024

    return (
        f"{valor:.2f} {unidade}"
    )


# ============================================================
# PASTAS DE PRIMEIRO NÍVEL
# ============================================================

def pastas_raiz():

    resultado = []

    if not PASTA_SAIDA.exists():
        return resultado

    for item in sorted(
        PASTA_SAIDA.iterdir(),
        key=lambda x: x.name.casefold(),
    ):

        if item.is_dir():

            resultado.append(
                item.name
            )

    return resultado


# ============================================================
# CONTAGEM POR ÁREA
# ============================================================

def arquivos_por_pasta_raiz(
    arquivos
):

    contador = Counter()

    for item in arquivos:

        caminho = Path(
            item[
                "caminho"
            ]
        )

        try:
            relativo = (
                caminho.relative_to(
                    PASTA_SAIDA
                )
            )

        except ValueError:
            continue

        if not relativo.parts:
            continue

        contador[
            relativo.parts[0]
        ] += 1

    return contador


# ============================================================
# VERIFICAÇÃO BÁSICA DE ARQUIVOS
# ============================================================

def encontrar_problemas(
    arquivos
):

    problemas = []

    for item in arquivos:

        caminho = Path(
            item[
                "caminho"
            ]
        )

        tamanho = item[
            "tamanho_bytes"
        ]

        if tamanho == 0:

            problemas.append(
                {
                    "tipo": "arquivo_vazio",
                    "arquivo": str(
                        caminho
                    ),
                }
            )

        if (
            caminho.suffix.lower()
            == ".txt"
            and tamanho < 10
        ):

            problemas.append(
                {
                    "tipo": "txt_muito_pequeno",
                    "arquivo": str(
                        caminho
                    ),
                }
            )

    return problemas


# ============================================================
# RELATÓRIO TXT
# ============================================================

def gerar_txt(
    normas,
    juris,
    pastas,
    arquivos,
    problemas,
):

    PASTA_INDICES.mkdir(
        parents=True,
        exist_ok=True,
    )

    analise_normas = (
        analisar_normas(
            normas
        )
    )

    analise_juris = (
        analisar_jurisprudencia(
            juris
        )
    )

    raiz = pastas_raiz()

    contagem_raiz = (
        arquivos_por_pasta_raiz(
            arquivos
        )
    )

    linhas = [
        "LEX MACHINA",
        "AUDITORIA GERAL DO ACERVO",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        "",
        "RESUMO GERAL",
        "-" * 78,
        (
            "Registros no catálogo de normas: "
            f"{len(normas)}"
        ),
        (
            "Normas propriamente ditas: "
            f"{len(analise_normas['normas'])}"
        ),
        (
            "Referências cruzadas: "
            f"{len(analise_normas['referencias'])}"
        ),
        (
            "Registros jurisprudenciais: "
            f"{len(juris)}"
        ),
        (
            "Pastas encontradas em saida: "
            f"{len(pastas)}"
        ),
        (
            "Arquivos físicos encontrados: "
            f"{len(arquivos)}"
        ),
        (
            "Tamanho total do acervo: "
            f"{formatar_bytes(tamanho_total(arquivos))}"
        ),
        (
            "Problemas estruturais básicos: "
            f"{len(problemas)}"
        ),
        "",
        "=" * 78,
        "PASTAS PRINCIPAIS DO ACERVO",
        "=" * 78,
        "",
    ]

    for pasta in raiz:

        quantidade = (
            contagem_raiz[
                pasta
            ]
        )

        linhas.append(
            f"- {pasta}: "
            f"{quantidade} arquivo(s)"
        )

    linhas.extend(
        [
            "",
            "=" * 78,
            "NORMAS POR PASTA / ÁREA",
            "=" * 78,
            "",
        ]
    )

    for pasta, quantidade in sorted(
        analise_normas[
            "por_pasta"
        ].items(),
        key=lambda x: x[0].casefold(),
    ):

        linhas.append(
            f"- {pasta}: "
            f"{quantidade}"
        )

    linhas.extend(
        [
            "",
            "=" * 78,
            "LISTA DE NORMAS CADASTRADAS",
            "=" * 78,
            "",
        ]
    )

    for indice, item in enumerate(
        analise_normas[
            "normas"
        ],
        start=1,
    ):

        nome = limpar(
            item.get(
                "nome",
                "SEM NOME",
            )
        )

        destino = limpar(
            item.get(
                "pasta_destino",
                "",
            )
        )

        url = limpar(
            item.get(
                "url",
                "",
            )
        )

        linhas.extend(
            [
                (
                    f"{indice:03d}. "
                    f"{nome}"
                ),
                (
                    f"     Pasta: "
                    f"{destino}"
                ),
                (
                    f"     Fonte: "
                    f"{url}"
                ),
                "",
            ]
        )

    linhas.extend(
        [
            "=" * 78,
            "REFERÊNCIAS CRUZADAS",
            "=" * 78,
            "",
        ]
    )

    for indice, item in enumerate(
        analise_normas[
            "referencias"
        ],
        start=1,
    ):

        linhas.append(
            (
                f"{indice:03d}. "
                f"{limpar(item.get('nome', ''))}"
            )
        )

        linhas.append(
            (
                "     Destino: "
                f"{limpar(item.get('destino_ref', ''))}"
            )
        )

        linhas.append(
            (
                "     Relação: "
                f"{limpar(item.get('relacao', ''))}"
            )
        )

        linhas.append("")

    linhas.extend(
        [
            "=" * 78,
            "JURISPRUDÊNCIA POR TRIBUNAL",
            "=" * 78,
            "",
        ]
    )

    for tribunal, quantidade in sorted(
        analise_juris[
            "por_tribunal"
        ].items()
    ):

        linhas.append(
            f"- {tribunal}: "
            f"{quantidade}"
        )

    linhas.extend(
        [
            "",
            "JURISPRUDÊNCIA POR TIPO",
            "-" * 78,
        ]
    )

    for tipo, quantidade in sorted(
        analise_juris[
            "por_tipo"
        ].items()
    ):

        linhas.append(
            f"- {tipo}: "
            f"{quantidade}"
        )

    linhas.extend(
        [
            "",
            "JURISPRUDÊNCIA POR STATUS",
            "-" * 78,
        ]
    )

    for status, quantidade in sorted(
        analise_juris[
            "por_status"
        ].items()
    ):

        linhas.append(
            f"- {status}: "
            f"{quantidade}"
        )

    linhas.extend(
        [
            "",
            "=" * 78,
            "PROBLEMAS BÁSICOS ENCONTRADOS",
            "=" * 78,
            "",
        ]
    )

    if not problemas:

        linhas.append(
            "Nenhum problema estrutural básico encontrado."
        )

    else:

        for problema in problemas:

            linhas.append(
                (
                    f"- {problema['tipo']}: "
                    f"{problema['arquivo']}"
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
    normas,
    juris,
    pastas,
    arquivos,
    problemas,
):

    analise_normas = (
        analisar_normas(
            normas
        )
    )

    analise_juris = (
        analisar_jurisprudencia(
            juris
        )
    )

    estrutura = {
        "gerado_em": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "resumo": {
            "registros_catalogo_normas": (
                len(normas)
            ),
            "normas": (
                len(
                    analise_normas[
                        "normas"
                    ]
                )
            ),
            "referencias": (
                len(
                    analise_normas[
                        "referencias"
                    ]
                )
            ),
            "jurisprudencias": (
                len(juris)
            ),
            "pastas_saida": (
                len(pastas)
            ),
            "arquivos_saida": (
                len(arquivos)
            ),
            "tamanho_total_bytes": (
                tamanho_total(
                    arquivos
                )
            ),
            "problemas": (
                len(problemas)
            ),
        },

        "pastas_principais": (
            pastas_raiz()
        ),

        "normas_por_pasta": dict(
            analise_normas[
                "por_pasta"
            ]
        ),

        "jurisprudencia": {
            "por_tribunal": dict(
                analise_juris[
                    "por_tribunal"
                ]
            ),
            "por_tipo": dict(
                analise_juris[
                    "por_tipo"
                ]
            ),
            "por_status": dict(
                analise_juris[
                    "por_status"
                ]
            ),
        },

        "normas": (
            analise_normas[
                "normas"
            ]
        ),

        "referencias": (
            analise_normas[
                "referencias"
            ]
        ),

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

    print()
    print(
        "LEX MACHINA - "
        "AUDITORIA GERAL DO ACERVO"
    )

    print(
        "=" * 60
    )

    print()

    normas = carregar_json(
        CATALOGO_NORMAS
    )

    juris = carregar_json(
        CATALOGO_JURIS
    )

    print(
        "Lendo estrutura física..."
    )

    pastas, arquivos = (
        inventariar_saida()
    )

    problemas = (
        encontrar_problemas(
            arquivos
        )
    )

    analise_normas = (
        analisar_normas(
            normas
        )
    )

    print()
    print(
        "ACERVO ATUAL"
    )

    print(
        "-" * 60
    )

    print(
        "Normas: "
        f"{len(analise_normas['normas'])}"
    )

    print(
        "Referências cruzadas: "
        f"{len(analise_normas['referencias'])}"
    )

    print(
        "Jurisprudências: "
        f"{len(juris)}"
    )

    print(
        "Arquivos físicos: "
        f"{len(arquivos)}"
    )

    print(
        "Pastas: "
        f"{len(pastas)}"
    )

    print(
        "Tamanho total: "
        f"{formatar_bytes(tamanho_total(arquivos))}"
    )

    print(
        "Problemas básicos: "
        f"{len(problemas)}"
    )

    relatorio_txt = gerar_txt(
        normas,
        juris,
        pastas,
        arquivos,
        problemas,
    )

    relatorio_json = gerar_json(
        normas,
        juris,
        pastas,
        arquivos,
        problemas,
    )

    print()
    print(
        "=" * 60
    )

    print(
        "AUDITORIA GERAL CONCLUÍDA"
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
        "Nenhum arquivo do acervo "
        "foi alterado."
    )


if __name__ == "__main__":
    main()