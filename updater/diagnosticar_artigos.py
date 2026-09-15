from datetime import datetime
from pathlib import Path
import argparse
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

PASTA_RELATORIOS = Path(
    "saida/99_INDICES"
)

RELATORIO_TXT = (
    PASTA_RELATORIOS
    / "DIAGNOSTICO_ARTIGOS_ESP32.txt"
)

RELATORIO_JSON = (
    PASTA_RELATORIOS
    / "DIAGNOSTICO_ARTIGOS_ESP32.json"
)


# ============================================================
# ARGUMENTOS
# ============================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - diagnóstico dos formatos "
            "de artigos nas 72 normas do Catálogo Mestre"
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


def limpar_linha(texto):
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

    return texto.strip()


# ============================================================
# CATÁLOGO
# ============================================================

def carregar_catalogo_mestre():
    if not CATALOGO_MESTRE.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: "
            f"{CATALOGO_MESTRE}"
        )

    dados = json.loads(
        CATALOGO_MESTRE.read_text(
            encoding="utf-8"
        )
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
# LOCALIZAÇÃO DAS NORMAS
# ============================================================

def localizar_norma(
    item,
    arquivos,
):
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
    # A / B / C:
    # nome exato + pasta esperada
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
    # BASE:
    # aceita nomes históricos
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
# LEITURA DE TEXTO
# ============================================================

def ler_texto(
    caminho
):
    for codificacao in (
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            return (
                caminho.read_text(
                    encoding=codificacao
                ),
                codificacao,
            )

        except UnicodeDecodeError:
            continue

    return (
        caminho.read_text(
            encoding="utf-8",
            errors="replace",
        ),
        "utf-8-replace",
    )


# ============================================================
# PADRÕES DE ARTIGO
# ============================================================

PADROES = {
    "P1_classico": re.compile(
        r"(?i)^\s*Art\.\s*(\d+)"
        r"(?:\s*[º°o])?"
        r"(?:\s*[-–—]\s*([A-Za-z0-9]+))?"
        r"(?=\s|\.|,|;|:|$)"
    ),

    "P2_sem_ponto": re.compile(
        r"(?i)^\s*Art\s+(\d+)"
        r"(?:\s*[º°o])?"
        r"(?:\s*[-–—]\s*([A-Za-z0-9]+))?"
        r"(?=\s|\.|,|;|:|$)"
    ),

    "P3_artigo_extenso": re.compile(
        r"(?i)^\s*Artigo\s+(\d+)"
        r"(?:\s*[º°o])?"
        r"(?:\s*[-–—]\s*([A-Za-z0-9]+))?"
        r"(?=\s|\.|,|;|:|$)"
    ),

    "P4_ponto_ordinal": re.compile(
        r"(?i)^\s*Art\.\s*(\d+)"
        r"\s*\.\s*[º°o]"
        r"(?:\s*[-–—]\s*([A-Za-z0-9]+))?"
        r"(?=\s|\.|,|;|:|$)"
    ),

    "P5_numero_com_ponto_milhar": re.compile(
        r"(?i)^\s*Art\.\s*"
        r"(\d{1,3}(?:\.\d{3})+)"
        r"(?:\s*[º°o])?"
        r"(?:\s*[-–—]\s*([A-Za-z0-9]+))?"
        r"(?=\s|\.|,|;|:|$)"
    ),

    "P6_flexivel": re.compile(
        r"(?i)^\s*Art(?:igo)?\.?\s*"
        r"(\d+(?:\.\d{3})*)"
        r"(?:\s*\.\s*)?"
        r"(?:[º°o])?"
        r"(?:\s*[-–—]\s*([A-Za-z0-9]+))?"
        r"(?=\s|\.|,|;|:|$)"
    ),
}


PADRAO_PARECE_ARTIGO = re.compile(
    r"(?i)"
    r"^\s*"
    r"(?:Art(?:igo)?\.?)"
)


# ============================================================
# DIAGNÓSTICO DE UMA NORMA
# ============================================================

def diagnosticar_norma(
    item,
    caminho,
):
    texto, codificacao = ler_texto(
        caminho
    )

    linhas = texto.splitlines()

    linhas_art = []

    resultados_padrao = {
        nome: []
        for nome in PADROES
    }

    rejeitadas = []

    for numero_linha, linha_original in enumerate(
        linhas,
        start=1,
    ):
        linha = limpar_linha(
            linha_original
        )

        if not linha:
            continue

        parece = bool(
            PADRAO_PARECE_ARTIGO.search(
                linha
            )
        )

        if parece:
            linhas_art.append(
                {
                    "linha": numero_linha,
                    "texto": linha,
                }
            )

        casou_algum = False

        for nome, padrao in PADROES.items():
            match = padrao.search(
                linha
            )

            if not match:
                continue

            casou_algum = True

            numero = match.group(
                1
            )

            sufixo = (
                match.group(
                    2
                )
                if (
                    match.lastindex
                    and match.lastindex >= 2
                )
                else None
            )

            resultados_padrao[
                nome
            ].append(
                {
                    "linha": numero_linha,
                    "numero": numero,
                    "sufixo": sufixo,
                    "texto": linha,
                }
            )

        if (
            parece
            and not casou_algum
        ):
            rejeitadas.append(
                {
                    "linha": numero_linha,
                    "texto": linha,
                }
            )

    # --------------------------------------------------------
    # Exemplos
    # --------------------------------------------------------

    exemplos_inicio = linhas_art[
        :10
    ]

    exemplos_fim = (
        linhas_art[
            -10:
        ]
        if len(
            linhas_art
        ) > 10
        else linhas_art
    )

    rejeitadas_exemplo = rejeitadas[
        :30
    ]

    # --------------------------------------------------------
    # Estatísticas de números únicos
    # --------------------------------------------------------

    numeros_unicos = {}

    for nome, ocorrencias in (
        resultados_padrao.items()
    ):
        chaves = set()

        for ocorrencia in ocorrencias:
            chave = str(
                ocorrencia[
                    "numero"
                ]
            )

            sufixo = ocorrencia[
                "sufixo"
            ]

            if sufixo:
                chave += (
                    "-"
                    + str(
                        sufixo
                    ).upper()
                )

            chaves.add(
                chave
            )

        numeros_unicos[
            nome
        ] = len(
            chaves
        )

    return {
        "id": item.get(
            "id",
            "",
        ),
        "nome": item.get(
            "nome",
            "",
        ),
        "arquivo": str(
            caminho
        ),
        "codificacao": codificacao,
        "linhas_totais": len(
            linhas
        ),
        "linhas_que_parecem_artigo": len(
            linhas_art
        ),
        "rejeitadas": len(
            rejeitadas
        ),
        "padroes": {
            nome: {
                "ocorrencias": len(
                    ocorrencias
                ),
                "numeros_unicos": (
                    numeros_unicos[
                        nome
                    ]
                ),
            }
            for nome, ocorrencias in (
                resultados_padrao.items()
            )
        },
        "exemplos_inicio": (
            exemplos_inicio
        ),
        "exemplos_fim": (
            exemplos_fim
        ),
        "rejeitadas_exemplo": (
            rejeitadas_exemplo
        ),
    }


# ============================================================
# RELATÓRIOS
# ============================================================

def gerar_relatorios(
    catalogo,
    resultados,
    erros,
):
    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas = [
        "LEX MACHINA",
        "DIAGNÓSTICO DOS FORMATOS DE ARTIGO",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        (
            "VERSÃO DO CATÁLOGO: "
            f"{catalogo.get('versao', '')}"
        ),
        "",
        (
            "NORMAS DIAGNOSTICADAS: "
            f"{len(resultados)}"
        ),
        (
            "ERROS: "
            f"{len(erros)}"
        ),
        "",
        "=" * 78,
        "RESUMO",
        "=" * 78,
        "",
    ]

    for item in resultados:
        linhas.append(
            (
                f"- {item['id']} | "
                f"linhas_art={item['linhas_que_parecem_artigo']} "
                f"| rejeitadas={item['rejeitadas']} "
                f"| {item['nome']}"
            )
        )

        for nome_padrao, dados in (
            item[
                "padroes"
            ].items()
        ):
            linhas.append(
                (
                    f"    {nome_padrao}: "
                    f"ocorrencias={dados['ocorrencias']} "
                    f"| unicos={dados['numeros_unicos']}"
                )
            )

    linhas.extend(
        [
            "",
            "=" * 78,
            "DIAGNÓSTICO DETALHADO",
            "=" * 78,
            "",
        ]
    )

    for item in resultados:
        linhas.extend(
            [
                (
                    f"{item['id']} - "
                    f"{item['nome']}"
                ),
                "-" * 78,
                (
                    f"Arquivo: "
                    f"{item['arquivo']}"
                ),
                (
                    f"Codificação: "
                    f"{item['codificacao']}"
                ),
                (
                    f"Linhas totais: "
                    f"{item['linhas_totais']}"
                ),
                (
                    "Linhas que parecem artigo: "
                    f"{item['linhas_que_parecem_artigo']}"
                ),
                (
                    "Linhas rejeitadas por todos "
                    f"os padrões: {item['rejeitadas']}"
                ),
                "",
                "PADRÕES:",
            ]
        )

        for nome_padrao, dados in (
            item[
                "padroes"
            ].items()
        ):
            linhas.append(
                (
                    f"- {nome_padrao}: "
                    f"ocorrencias={dados['ocorrencias']} "
                    f"| unicos={dados['numeros_unicos']}"
                )
            )

        linhas.extend(
            [
                "",
                "PRIMEIROS EXEMPLOS:",
            ]
        )

        if item[
            "exemplos_inicio"
        ]:
            for exemplo in item[
                "exemplos_inicio"
            ]:
                linhas.append(
                    (
                        f"  L{exemplo['linha']}: "
                        f"{exemplo['texto']}"
                    )
                )

        else:
            linhas.append(
                "  [nenhum]"
            )

        linhas.extend(
            [
                "",
                "ÚLTIMOS EXEMPLOS:",
            ]
        )

        if item[
            "exemplos_fim"
        ]:
            for exemplo in item[
                "exemplos_fim"
            ]:
                linhas.append(
                    (
                        f"  L{exemplo['linha']}: "
                        f"{exemplo['texto']}"
                    )
                )

        else:
            linhas.append(
                "  [nenhum]"
            )

        linhas.extend(
            [
                "",
                "PARECEM ARTIGOS, MAS FORAM "
                "REJEITADOS POR TODOS OS PADRÕES:",
            ]
        )

        if item[
            "rejeitadas_exemplo"
        ]:
            for exemplo in item[
                "rejeitadas_exemplo"
            ]:
                linhas.append(
                    (
                        f"  L{exemplo['linha']}: "
                        f"{exemplo['texto']}"
                    )
                )

        else:
            linhas.append(
                "  [nenhum]"
            )

        linhas.append("")
        linhas.append(
            "=" * 78
        )
        linhas.append("")

    if erros:
        linhas.extend(
            [
                "ERROS",
                "=" * 78,
                "",
            ]
        )

        for erro in erros:
            linhas.append(
                f"- {erro}"
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
            "versao",
            ""
        ),
        "normas_diagnosticadas": len(
            resultados
        ),
        "erros": erros,
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
        carregar_catalogo_mestre()
    )

    arquivos = inventariar(
        origem
    )

    print()
    print(
        "LEX MACHINA - "
        "DIAGNÓSTICO DE ARTIGOS"
    )

    print(
        "=" * 60
    )

    print(
        f"Origem: {origem}"
    )

    print(
        f"Normas no catálogo: {len(itens)}"
    )

    print()

    resultados = []

    erros = []

    for indice, item in enumerate(
        itens,
        start=1,
    ):
        encontrados = localizar_norma(
            item,
            arquivos,
        )

        print(
            (
                f"[{indice}/{len(itens)}] "
                f"{item.get('nome', '')}"
            )
        )

        if not encontrados:
            mensagem = (
                "Norma não encontrada: "
                f"{item.get('nome', '')}"
            )

            erros.append(
                mensagem
            )

            print(
                f"  ✗ {mensagem}"
            )

            continue

        caminho = encontrados[
            0
        ]

        try:
            resultado = diagnosticar_norma(
                item,
                caminho,
            )

            resultados.append(
                resultado
            )

            print(
                (
                    "  linhas_art="
                    f"{resultado['linhas_que_parecem_artigo']} "
                    "| rejeitadas="
                    f"{resultado['rejeitadas']}"
                )
            )

        except Exception as erro:
            mensagem = (
                f"{item.get('nome', '')}: "
                f"{erro}"
            )

            erros.append(
                mensagem
            )

            print(
                f"  ✗ {erro}"
            )

    gerar_relatorios(
        catalogo,
        resultados,
        erros,
    )

    print()
    print(
        "=" * 60
    )

    print(
        "DIAGNÓSTICO FINALIZADO"
    )

    print(
        "Normas diagnosticadas: "
        f"{len(resultados)}"
    )

    print(
        f"Erros: {len(erros)}"
    )

    print()

    print(
        f"Relatório TXT: "
        f"{RELATORIO_TXT}"
    )

    print(
        f"Relatório JSON: "
        f"{RELATORIO_JSON}"
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
