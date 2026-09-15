from datetime import datetime
from pathlib import Path
import argparse
import json
import re
import unicodedata


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO = Path("catalogo_mestre_vademecum.json")

PASTA_RELATORIOS = Path("saida/99_INDICES")

RELATORIO_TXT = (
    PASTA_RELATORIOS
    / "MAPA_MESTRE_VADE_MECUM.txt"
)

RELATORIO_JSON = (
    PASTA_RELATORIOS
    / "MAPA_MESTRE_VADE_MECUM.json"
)


# ============================================================
# ARGUMENTOS
# ============================================================

def argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - comparação segura do cartão "
            "com o catálogo mestre"
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
# NORMALIZAÇÃO
# ============================================================

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
        list,
    ):
        raise ValueError(
            "O campo 'itens' do catálogo mestre "
            "precisa ser uma lista."
        )

    return dados, itens


# ============================================================
# INVENTÁRIO
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

        texto_relativo = str(
            relativo
        )

        arquivos.append(
            {
                "caminho": texto_relativo,
                "nome": caminho.name,
                "normalizado": normalizar(
                    texto_relativo
                ),
                "compacto": compactar(
                    texto_relativo
                ),
                "nome_normalizado": normalizar(
                    caminho.name
                ),
                "nome_compacto": compactar(
                    caminho.name
                ),
            }
        )

    return arquivos


# ============================================================
# IDENTIFICAÇÃO DA NORMA
# ============================================================

def extrair_numero_ano(nome):
    """
    Extrai o número principal da norma e o ano.

    Exemplos:
        Lei 9.504/1997 -> ("9504", "1997")
        Lei 12.016/2009 -> ("12016", "2009")
        Lei Complementar 64/1990 -> ("64", "1990")
        Decreto-Lei 2.848/1940 -> ("2848", "1940")
    """

    padrao = re.compile(
        r"\b(?:lei\s+complementar|lei|decreto-lei|decreto)\s+"
        r"([\d.]+)\s*/\s*(\d{4})",
        flags=re.IGNORECASE,
    )

    resultado = padrao.search(
        str(
            nome or ""
        )
    )

    if not resultado:
        return (
            "",
            "",
        )

    numero = re.sub(
        r"\D+",
        "",
        resultado.group(
            1
        ),
    )

    ano = resultado.group(
        2
    )

    return (
        numero,
        ano,
    )


# ============================================================
# TERMOS FORTES
# ============================================================

def termos_fortes(item):
    """
    Retorna apenas termos textuais suficientemente específicos.

    Evita considerar como evidência expressões muito genéricas
    ou apenas fragmentos numéricos.
    """

    termos = []

    for termo in item.get(
        "detectar_por",
        [],
    ):
        normal = normalizar(
            termo
        )

        if not normal:
            continue

        possui_letras = bool(
            re.search(
                r"[a-z]",
                normal,
            )
        )

        palavras = [
            p
            for p in normal.split()
            if p
        ]

        if (
            possui_letras
            and len(
                " ".join(
                    palavras
                )
            ) >= 5
        ):
            termos.append(
                normal
            )

    return termos


# ============================================================
# DETECÇÃO SEGURA
# ============================================================

def detectar_item(
    item,
    arquivos,
):
    """
    Ordem de confiança:

    1. Nome de arquivo sugerido EXATO.
    2. Número da norma + ano presentes no caminho.
    3. Termo textual forte do catálogo.

    Não usa mais combinação genérica de fragmentos numéricos.
    Isso elimina falsos positivos como:
      Lei 12.016/2009 -> dec_8771_2016_regulamento_mci.txt
    """

    candidatos = []

    arquivo_sugerido = str(
        item.get(
            "arquivo_sugerido",
            ""
        )
    ).strip()

    sugerido_compacto = (
        compactar(
            arquivo_sugerido
        )
        if arquivo_sugerido
        else ""
    )

    numero, ano = (
        extrair_numero_ano(
            item.get(
                "nome",
                "",
            )
        )
    )

    termos = termos_fortes(
        item
    )

    for arquivo in arquivos:
        encontrou = False

        # ----------------------------------------------------
        # 1. NOME EXATO DO ARQUIVO SUGERIDO
        # ----------------------------------------------------

        if (
            sugerido_compacto
            and arquivo[
                "nome_compacto"
            ]
            == sugerido_compacto
        ):
            encontrou = True

        # ----------------------------------------------------
        # 2. NÚMERO DA NORMA + ANO
        # ----------------------------------------------------

        if (
            not encontrou
            and numero
            and ano
        ):
            texto = arquivo[
                "compacto"
            ]

            # Para números curtos, exigimos marcador textual
            # adicional; para números maiores, número+ano basta.
            if (
                numero in texto
                and ano in texto
            ):
                if len(
                    numero
                ) >= 4:
                    encontrou = True

                else:
                    nome_norm = arquivo[
                        "normalizado"
                    ]

                    prefixos = (
                        "lei",
                        "lc",
                        "lcp",
                        "decreto",
                    )

                    if any(
                        prefixo
                        in nome_norm
                        for prefixo
                        in prefixos
                    ):
                        encontrou = True

        # ----------------------------------------------------
        # 3. TERMO TEXTUAL FORTE
        # ----------------------------------------------------

        if not encontrou:
            texto = arquivo[
                "normalizado"
            ]

            for termo in termos:
                if termo in texto:
                    encontrou = True
                    break

        if encontrou:
            candidatos.append(
                arquivo[
                    "caminho"
                ]
            )

    # Remove duplicados preservando ordem
    vistos = set()
    unicos = []

    for caminho in candidatos:
        chave = caminho.casefold()

        if chave in vistos:
            continue

        vistos.add(
            chave
        )

        unicos.append(
            caminho
        )

    return unicos


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar(
    encontrados
):
    if encontrados:
        return "PRESENTE"

    return "AUSENTE"


# ============================================================
# RELATÓRIOS
# ============================================================

def gerar_relatorios(
    catalogo,
    resultados,
):
    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    prioridades = [
        "BASE",
        "A",
        "B",
        "C",
    ]

    resumo = {}

    for prioridade in prioridades:
        grupo = [
            item
            for item in resultados
            if item[
                "prioridade"
            ] == prioridade
        ]

        if not grupo:
            continue

        resumo[
            prioridade
        ] = {
            "total": len(
                grupo
            ),
            "presentes": sum(
                1
                for item in grupo
                if item[
                    "status"
                ]
                == "PRESENTE"
            ),
            "ausentes": sum(
                1
                for item in grupo
                if item[
                    "status"
                ]
                == "AUSENTE"
            ),
        }

    ramos = {}

    for item in resultados:
        ramo = item[
            "ramo"
        ]

        ramos.setdefault(
            ramo,
            {
                "total": 0,
                "presentes": 0,
                "ausentes": 0,
            },
        )

        ramos[
            ramo
        ][
            "total"
        ] += 1

        if (
            item[
                "status"
            ]
            == "PRESENTE"
        ):
            ramos[
                ramo
            ][
                "presentes"
            ] += 1

        else:
            ramos[
                ramo
            ][
                "ausentes"
            ] += 1

    linhas = [
        "LEX MACHINA",
        "MAPA MESTRE DO VADE MECUM",
        "=" * 78,
        "",
        (
            "GERADO EM: "
            + datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        ),
        (
            "VERSÃO DO CATÁLOGO: "
            f"{catalogo.get('versao', '')}"
        ),
        "",
        "RESUMO POR PRIORIDADE",
        "-" * 78,
    ]

    for prioridade, dados in resumo.items():
        linhas.append(
            (
                f"{prioridade}: "
                f"total={dados['total']} "
                f"| presentes={dados['presentes']} "
                f"| ausentes={dados['ausentes']}"
            )
        )

    linhas.extend(
        [
            "",
            "COBERTURA POR RAMO",
            "-" * 78,
        ]
    )

    for ramo in sorted(
        ramos,
        key=str.casefold,
    ):
        dados = ramos[
            ramo
        ]

        if (
            dados[
                "ausentes"
            ]
            == 0
        ):
            simbolo = "✓"
            estado = (
                "COBERTO NO CATÁLOGO MESTRE"
            )

        elif (
            dados[
                "presentes"
            ]
            == 0
        ):
            simbolo = "○"
            estado = "AUSENTE"

        else:
            simbolo = "◐"
            estado = "PARCIAL"

        linhas.append(
            (
                f"{simbolo} {ramo}: "
                f"{dados['presentes']}/"
                f"{dados['total']} presentes "
                f"- {estado}"
            )
        )

    for prioridade in prioridades:
        grupo = [
            item
            for item in resultados
            if item[
                "prioridade"
            ]
            == prioridade
        ]

        if not grupo:
            continue

        linhas.extend(
            [
                "",
                "=" * 78,
                f"PRIORIDADE {prioridade}",
                "=" * 78,
                "",
            ]
        )

        for item in grupo:
            simbolo = (
                "✓"
                if item[
                    "status"
                ]
                == "PRESENTE"
                else "↓"
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
                    "   Ramo: "
                    f"{item['ramo']}"
                )
            )

            linhas.append(
                (
                    "   Destino: "
                    f"{item['pasta_destino']}"
                )
            )

            linhas.append(
                (
                    "   Fonte: "
                    f"{item['fonte_oficial']}"
                )
            )

            if item[
                "encontrados"
            ]:
                for achado in item[
                    "encontrados"
                ]:
                    linhas.append(
                        (
                            "   Encontrado em: "
                            f"{achado}"
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
        "versao_catalogo": catalogo.get(
            "versao"
        ),
        "resumo_por_prioridade": resumo,
        "cobertura_por_ramo": ramos,
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
        carregar_catalogo()
    )

    arquivos = inventariar(
        origem
    )

    print()
    print(
        "LEX MACHINA - MAPA MESTRE"
    )

    print(
        "=" * 60
    )

    print(
        f"Origem: {origem}"
    )

    print(
        "Itens no catálogo mestre: "
        f"{len(itens)}"
    )

    print(
        "Arquivos analisados: "
        f"{len(arquivos)}"
    )

    print()

    resultados = []

    for indice, item in enumerate(
        itens,
        start=1,
    ):
        encontrados = detectar_item(
            item,
            arquivos,
        )

        status = classificar(
            encontrados
        )

        resultado = {
            "id": item.get(
                "id"
            ),
            "ramo": item.get(
                "ramo"
            ),
            "nome": item.get(
                "nome"
            ),
            "prioridade": item.get(
                "prioridade"
            ),
            "status": status,
            "fonte_oficial": item.get(
                "fonte_oficial"
            ),
            "pasta_destino": item.get(
                "pasta_destino"
            ),
            "arquivo_sugerido": item.get(
                "arquivo_sugerido"
            ),
            "encontrados": encontrados,
        }

        resultados.append(
            resultado
        )

        marca = (
            "✓"
            if status == "PRESENTE"
            else "↓"
        )

        print(
            (
                f"[{indice}/{len(itens)}] "
                f"{marca} "
                f"{item.get('nome')}"
            )
        )

    gerar_relatorios(
        catalogo,
        resultados,
    )

    presentes = sum(
        1
        for item in resultados
        if item[
            "status"
        ]
        == "PRESENTE"
    )

    ausentes = (
        len(
            resultados
        )
        - presentes
    )

    print()
    print(
        "=" * 60
    )

    print(
        "MAPA MESTRE CONCLUÍDO"
    )

    print(
        f"Presentes: {presentes}"
    )

    print(
        f"Ausentes: {ausentes}"
    )

    print(
        f"Relatório TXT: {RELATORIO_TXT}"
    )

    print(
        f"Relatório JSON: {RELATORIO_JSON}"
    )

    print()

    print(
        "Nenhum arquivo do cartão foi alterado."
    )


if __name__ == "__main__":
    main()
