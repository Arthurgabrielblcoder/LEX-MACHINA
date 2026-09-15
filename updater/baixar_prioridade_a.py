from datetime import datetime
from pathlib import Path
import argparse
import json
import re
import sys
import unicodedata

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO = Path("catalogo_mestre_vademecum.json")

PASTA_RELATORIOS = Path(
    "saida/99_INDICES"
)

RELATORIO_TXT = (
    PASTA_RELATORIOS
    / "RELATORIO_DOWNLOAD_PRIORIDADE_A.txt"
)

RELATORIO_JSON = (
    PASTA_RELATORIOS
    / "RELATORIO_DOWNLOAD_PRIORIDADE_A.json"
)

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
            "LEX MACHINA - Baixa automaticamente "
            "as normas ausentes de Prioridade A."
        )
    )

    parser.add_argument(
        "destino",
        help=(
            "Unidade ou pasta do Vade Mecum. "
            "Exemplo: D:\\"
        ),
    )

    parser.add_argument(
        "--forcar",
        action="store_true",
        help=(
            "Permite substituir arquivo já existente. "
            "Use somente quando necessário."
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


def normalizar_nome(texto):
    texto = unicodedata.normalize(
        "NFKD",
        str(texto or ""),
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(
            caractere
        )
    )

    texto = texto.casefold()

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


def compactar_linhas(texto):
    linhas = []
    anterior_vazia = False

    for linha in texto.splitlines():
        linha = linha.strip()

        if not linha:
            if not anterior_vazia:
                linhas.append("")

            anterior_vazia = True
            continue

        linhas.append(linha)
        anterior_vazia = False

    return "\n".join(
        linhas
    ).strip()


def normalizar_texto(texto):
    texto = (
        texto
        .replace("\xa0", " ")
        .replace("\u2002", " ")
        .replace("\u2003", " ")
        .replace("\u2009", " ")
    )

    texto = re.sub(
        r"[ \t]+",
        " ",
        texto,
    )

    return compactar_linhas(
        texto
    )


# ============================================================
# CATÁLOGO
# ============================================================

def carregar_catalogo():
    if not CATALOGO.exists():
        raise FileNotFoundError(
            f"Catálogo mestre não encontrado: {CATALOGO}"
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
        list
    ):
        raise ValueError(
            "O campo 'itens' do catálogo "
            "mestre precisa ser uma lista."
        )

    return dados, itens


# ============================================================
# INVENTÁRIO DO DESTINO
# ============================================================

def inventariar(destino):
    arquivos = []

    for caminho in destino.rglob("*"):
        if caminho.is_file():

            try:
                relativo = caminho.relative_to(
                    destino
                )

            except ValueError:
                relativo = caminho

            arquivos.append(
                {
                    "caminho": caminho,
                    "relativo": str(
                        relativo
                    ),
                    "normalizado": normalizar_nome(
                        str(
                            relativo
                        )
                    ),
                }
            )

    return arquivos


def detectar_existencia(
    item,
    arquivos,
):
    termos = [
        normalizar_nome(
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

    encontrados = []

    for arquivo in arquivos:
        texto = arquivo[
            "normalizado"
        ]

        if any(
            termo
            and termo in texto
            for termo in termos
        ):
            encontrados.append(
                arquivo[
                    "relativo"
                ]
            )

    return encontrados


# ============================================================
# DOWNLOAD
# ============================================================

def baixar_html(url):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    resposta.raise_for_status()

    return resposta.content


# ============================================================
# DECODIFICAÇÃO
# ============================================================

def pontuar_texto(texto):
    suspeitos = [
        "Ã§",
        "Ã£",
        "Ã¡",
        "Ã©",
        "Ã³",
        "Ãº",
        "Âº",
        "Â§",
        "�",
        "Ă",
        "Ţ",
    ]

    pontos = 0

    for item in suspeitos:
        pontos += (
            texto.count(
                item
            )
            * 10
        )

    naturais = [
        "ção",
        "ções",
        "Art.",
        "Lei",
        "não",
        "República",
    ]

    for item in naturais:
        pontos -= texto.count(
            item
        )

    return pontos


def decodificar_html(conteudo):
    candidatos = []

    for codificacao in (
        "utf-8",
        "cp1252",
        "iso-8859-1",
    ):
        try:
            texto = conteudo.decode(
                codificacao,
                errors="strict",
            )

            candidatos.append(
                (
                    pontuar_texto(
                        texto
                    ),
                    codificacao,
                    texto,
                )
            )

        except UnicodeDecodeError:
            continue

    if not candidatos:
        return (
            conteudo.decode(
                "cp1252",
                errors="replace",
            ),
            "cp1252",
        )

    candidatos.sort(
        key=lambda item: item[0]
    )

    _, codificacao, texto = (
        candidatos[0]
    )

    return texto, codificacao


# ============================================================
# LIMPEZA HTML
# ============================================================

def normalizar_css(valor):
    if not valor:
        return ""

    return (
        str(
            valor
        )
        .lower()
        .replace(" ", "")
        .replace("\n", "")
        .replace("\t", "")
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

    estilo = normalizar_css(
        attrs.get(
            "style"
        )
    )

    return (
        "line-through"
        in estilo
    )


def remover_texto_riscado(soup):
    tags = list(
        soup.find_all(
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
            continue


def remover_elementos_nao_juridicos(
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
                continue


# ============================================================
# EXTRAÇÃO
# ============================================================

def extrair_texto(
    conteudo_bytes
):
    html, codificacao = (
        decodificar_html(
            conteudo_bytes
        )
    )

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    remover_elementos_nao_juridicos(
        soup
    )

    remover_texto_riscado(
        soup
    )

    corpo = (
        soup.body
        or soup
    )

    texto = corpo.get_text(
        separator="\n",
        strip=True,
    )

    texto = normalizar_texto(
        texto
    )

    return (
        texto,
        codificacao,
    )


# ============================================================
# VALIDAÇÃO
# ============================================================

def validar_texto(
    texto
):
    problemas = []

    if len(
        texto
    ) < 300:
        problemas.append(
            "Texto extraído pequeno demais."
        )

    if not re.search(
        r"\bArt\.?\s*1",
        texto,
        flags=re.IGNORECASE,
    ):
        problemas.append(
            "Não foi localizado o início "
            "típico de articulado (Art. 1)."
        )

    suspeitos = [
        "Ã§",
        "Ã£",
        "Ã¡",
        "Ã©",
        "Ã³",
        "Ãº",
        "Â§",
        "�",
    ]

    encontrados = [
        item
        for item in suspeitos
        if item in texto
    ]

    if encontrados:
        problemas.append(
            "Possível problema de codificação: "
            + ", ".join(
                repr(
                    item
                )
                for item in encontrados
            )
        )

    return problemas


# ============================================================
# CABEÇALHO
# ============================================================

def criar_cabecalho(
    item,
    codificacao,
):
    return (
        "LEX MACHINA\n"
        "========================================\n"
        f"NORMA: {item['nome']}\n"
        f"RAMO: {item['ramo']}\n"
        f"PRIORIDADE: {item['prioridade']}\n"
        "TIPO_REGISTRO: LEGISLAÇÃO\n"
        "FONTE: Presidência da República - Planalto\n"
        f"URL_FONTE: {item['fonte_oficial']}\n"
        f"PASTA_DESTINO: {item['pasta_destino']}\n"
        f"CODIFICACAO_ORIGEM: {codificacao}\n"
        "CODIFICACAO_ARQUIVO: UTF-8\n"
        f"BAIXADO_EM: {agora()}\n"
        "STATUS_DE_REVISAO: AUTOMÁTICO - AGUARDANDO VALIDAÇÃO\n"
        "REGRA_REVOGADOS: SOMENTE MARCAÇÃO HTML RISCADA\n"
        "========================================\n\n"
    )


# ============================================================
# SALVAR
# ============================================================

def salvar_norma(
    destino_raiz,
    item,
    texto,
    codificacao,
    forcar=False,
):
    pasta = (
        destino_raiz
        / item[
            "pasta_destino"
        ]
    )

    pasta.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho = (
        pasta
        / item[
            "arquivo_sugerido"
        ]
    )

    if (
        caminho.exists()
        and not forcar
    ):
        raise FileExistsError(
            f"O arquivo já existe: {caminho}"
        )

    conteudo = (
        criar_cabecalho(
            item,
            codificacao,
        )
        + texto
        + "\n"
    )

    caminho.write_text(
        conteudo,
        encoding="utf-8",
        newline="\n",
    )

    return caminho


# ============================================================
# RELATÓRIO
# ============================================================

def gerar_relatorio(
    destino,
    resultados,
):
    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    baixados = [
        item
        for item in resultados
        if item[
            "resultado"
        ] == "baixado"
    ]

    ja_existiam = [
        item
        for item in resultados
        if item[
            "resultado"
        ] == "ja_existia"
    ]

    erros = [
        item
        for item in resultados
        if item[
            "resultado"
        ] == "erro"
    ]

    alertas = [
        item
        for item in resultados
        if item[
            "alertas"
        ]
    ]

    linhas = [
        "LEX MACHINA",
        "DOWNLOAD AUTOMÁTICO - PRIORIDADE A",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        f"DESTINO: {destino}",
        "",
        f"ITENS ANALISADOS: {len(resultados)}",
        f"BAIXADOS: {len(baixados)}",
        f"JÁ EXISTIAM: {len(ja_existiam)}",
        f"ERROS: {len(erros)}",
        f"COM ALERTAS: {len(alertas)}",
        "",
        "=" * 78,
        "RESULTADOS",
        "=" * 78,
        "",
    ]

    for item in resultados:
        simbolo = {
            "baixado": "✓",
            "ja_existia": "=",
            "erro": "✗",
        }.get(
            item[
                "resultado"
            ],
            "?",
        )

        linhas.append(
            (
                f"{simbolo} "
                f"{item['nome']}"
            )
        )

        linhas.append(
            (
                "   Resultado: "
                f"{item['resultado']}"
            )
        )

        if item.get(
            "arquivo"
        ):
            linhas.append(
                (
                    "   Arquivo: "
                    f"{item['arquivo']}"
                )
            )

        if item.get(
            "fonte"
        ):
            linhas.append(
                (
                    "   Fonte: "
                    f"{item['fonte']}"
                )
            )

        if item.get(
            "encontrados"
        ):
            for achado in item[
                "encontrados"
            ]:
                linhas.append(
                    (
                        "   Já encontrado em: "
                        f"{achado}"
                    )
                )

        if item[
            "alertas"
        ]:
            for alerta in item[
                "alertas"
            ]:
                linhas.append(
                    (
                        "   ALERTA: "
                        f"{alerta}"
                    )
                )

        if item.get(
            "erro"
        ):
            linhas.append(
                (
                    "   ERRO: "
                    f"{item['erro']}"
                )
            )

        linhas.append("")

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
        "destino": str(
            destino
        ),
        "resumo": {
            "itens_analisados": len(
                resultados
            ),
            "baixados": len(
                baixados
            ),
            "ja_existiam": len(
                ja_existiam
            ),
            "erros": len(
                erros
            ),
            "com_alertas": len(
                alertas
            ),
        },
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
        RELATORIO_TXT,
        RELATORIO_JSON,
    )


# ============================================================
# MAIN
# ============================================================

def main():
    args = argumentos()

    destino = Path(
        args.destino
    )

    if (
        not destino.exists()
        or not destino.is_dir()
    ):
        raise FileNotFoundError(
            f"Destino inválido: {destino}"
        )

    _, itens = carregar_catalogo()

    prioridade_a = [
        item
        for item in itens
        if str(
            item.get(
                "prioridade",
                ""
            )
        ).strip().upper()
        == "A"
    ]

    arquivos_existentes = (
        inventariar(
            destino
        )
    )

    print()
    print(
        "LEX MACHINA - "
        "DOWNLOAD PRIORIDADE A"
    )

    print(
        "=" * 60
    )

    print(
        f"Destino: {destino}"
    )

    print(
        "Itens de Prioridade A: "
        f"{len(prioridade_a)}"
    )

    print()

    resultados = []

    for indice, item in enumerate(
        prioridade_a,
        start=1,
    ):
        nome = item.get(
            "nome",
            "SEM NOME",
        )

        print(
            f"[{indice}/{len(prioridade_a)}] "
            f"{nome}"
        )

        encontrados = (
            detectar_existencia(
                item,
                arquivos_existentes,
            )
        )

        if (
            encontrados
            and not args.forcar
        ):
            print(
                "  = Já existe no cartão. "
                "Ignorado."
            )

            resultados.append(
                {
                    "id": item.get(
                        "id"
                    ),
                    "nome": nome,
                    "resultado": (
                        "ja_existia"
                    ),
                    "arquivo": "",
                    "fonte": item.get(
                        "fonte_oficial",
                        "",
                    ),
                    "encontrados": (
                        encontrados
                    ),
                    "alertas": [],
                    "erro": "",
                }
            )

            print()
            continue

        try:
            url = item[
                "fonte_oficial"
            ]

            print(
                f"  Baixando: {url}"
            )

            conteudo = baixar_html(
                url
            )

            texto, codificacao = (
                extrair_texto(
                    conteudo
                )
            )

            alertas = validar_texto(
                texto
            )

            caminho = salvar_norma(
                destino,
                item,
                texto,
                codificacao,
                forcar=args.forcar,
            )

            print(
                f"  ✓ Salvo em: {caminho}"
            )

            if alertas:
                print(
                    "  ⚠ Arquivo salvo, "
                    "mas requer revisão:"
                )

                for alerta in alertas:
                    print(
                        f"    - {alerta}"
                    )

            resultados.append(
                {
                    "id": item.get(
                        "id"
                    ),
                    "nome": nome,
                    "resultado": (
                        "baixado"
                    ),
                    "arquivo": str(
                        caminho
                    ),
                    "fonte": url,
                    "encontrados": [],
                    "alertas": alertas,
                    "erro": "",
                }
            )

            arquivos_existentes.append(
                {
                    "caminho": caminho,
                    "relativo": str(
                        caminho.relative_to(
                            destino
                        )
                    ),
                    "normalizado": (
                        normalizar_nome(
                            str(
                                caminho.relative_to(
                                    destino
                                )
                            )
                        )
                    ),
                }
            )

        except Exception as erro:
            print(
                f"  ✗ ERRO: {erro}"
            )

            resultados.append(
                {
                    "id": item.get(
                        "id"
                    ),
                    "nome": nome,
                    "resultado": (
                        "erro"
                    ),
                    "arquivo": "",
                    "fonte": item.get(
                        "fonte_oficial",
                        "",
                    ),
                    "encontrados": [],
                    "alertas": [],
                    "erro": str(
                        erro
                    ),
                }
            )

        print()

    relatorio_txt, relatorio_json = (
        gerar_relatorio(
            destino,
            resultados,
        )
    )

    baixados = sum(
        1
        for item in resultados
        if item[
            "resultado"
        ] == "baixado"
    )

    ja_existiam = sum(
        1
        for item in resultados
        if item[
            "resultado"
        ] == "ja_existia"
    )

    erros = sum(
        1
        for item in resultados
        if item[
            "resultado"
        ] == "erro"
    )

    alertas = sum(
        1
        for item in resultados
        if item[
            "alertas"
        ]
    )

    print()
    print(
        "=" * 60
    )

    print(
        "DOWNLOAD PRIORIDADE A FINALIZADO"
    )

    print()

    print(
        f"Baixados: {baixados}"
    )

    print(
        f"Já existiam: {ja_existiam}"
    )

    print(
        f"Erros: {erros}"
    )

    print(
        f"Com alertas: {alertas}"
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
