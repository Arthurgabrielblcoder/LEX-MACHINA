from datetime import datetime
from pathlib import Path
import argparse
import json
import re
import shutil
import time
import unicodedata

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_BACKUP = Path(
    "backup_catalogos"
)

PASTA_CACHE = Path(
    "cache_stj"
)

PASTA_INDICES = Path(
    "saida/99_INDICES"
)

RELATORIO = (
    PASTA_INDICES
    / "RELATORIO_VERIFICACAO_STJ_LOTE.txt"
)


PAUSA_ENTRE_TEMAS = 0.8


# ============================================================
# ARGUMENTOS
# ============================================================

def ler_argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "LEX MACHINA - "
            "Verificador em lote de Temas Repetitivos do STJ"
        )
    )

    parser.add_argument(
        "--forcar",
        action="store_true",
        help=(
            "Reprocessa todos os Temas Repetitivos, "
            "mesmo os já verificados hoje."
        ),
    )

    return parser.parse_args()


# ============================================================
# UTILITÁRIOS
# ============================================================

def hoje():
    return datetime.now().strftime(
        "%Y-%m-%d"
    )


def agora():
    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def limpar_texto(texto):
    texto = str(
        texto or ""
    )

    texto = texto.replace(
        "\xa0",
        " ",
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


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
        limpar_texto(
            texto
        )
    )

    texto = texto.casefold()

    texto = re.sub(
        r"[^\w\s]",
        " ",
        texto,
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


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

    if not isinstance(
        dados,
        list,
    ):
        raise ValueError(
            "catalogo_jurisprudencia.json "
            "precisa conter uma lista."
        )

    return dados


def salvar_catalogo(
    catalogo
):
    CATALOGO.write_text(
        json.dumps(
            catalogo,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


# ============================================================
# BACKUP
# ============================================================

def criar_backup():
    PASTA_BACKUP.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    caminho = (
        PASTA_BACKUP
        / (
            "catalogo_jurisprudencia_"
            f"antes_verificacao_{timestamp}.json"
        )
    )

    shutil.copy2(
        CATALOGO,
        caminho,
    )

    return caminho


# ============================================================
# URL OFICIAL
# ============================================================

def url_tema(
    numero
):
    return (
        "https://processo.stj.jus.br/"
        "repetitivos/temas_repetitivos/"
        "pesquisa.jsp"
        f"?cod_tema_inicial={numero}"
        f"&cod_tema_final={numero}"
        "&novaConsulta=true"
        "&tipo_pesquisa=T"
    )


# ============================================================
# NAVEGADOR
# ============================================================

def abrir_navegador(
    playwright
):
    navegador = (
        playwright.chromium.launch(
            headless=True,
        )
    )

    contexto = (
        navegador.new_context(
            locale="pt-BR",
            viewport={
                "width": 1440,
                "height": 1200,
            },
            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131 Safari/537.36"
            ),
        )
    )

    return (
        navegador,
        contexto,
    )


# ============================================================
# CARREGAMENTO DA PÁGINA
# ============================================================

def carregar_tema(
    contexto,
    numero,
):
    pagina = contexto.new_page()

    url = url_tema(
        numero
    )

    try:
        pagina.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        try:
            pagina.wait_for_load_state(
                "networkidle",
                timeout=15000,
            )

        except PlaywrightTimeoutError:
            pass

        pagina.wait_for_timeout(
            1500
        )

        html = pagina.content()

        texto = pagina.locator(
            "body"
        ).inner_text(
            timeout=15000
        )

        PASTA_CACHE.mkdir(
            parents=True,
            exist_ok=True,
        )

        (
            PASTA_CACHE
            / f"tema_{numero}_browser.html"
        ).write_text(
            html,
            encoding="utf-8",
        )

        (
            PASTA_CACHE
            / f"tema_{numero}_browser.txt"
        ).write_text(
            texto,
            encoding="utf-8",
        )

        return {
            "url": url,
            "html": html,
            "texto": texto,
        }

    finally:
        pagina.close()


# ============================================================
# LINHAS
# ============================================================

def obter_linhas(
    texto
):
    linhas = []

    for linha in str(
        texto
    ).splitlines():

        linha = limpar_texto(
            linha
        )

        if linha:
            linhas.append(
                linha
            )

    return linhas


def localizar_rotulo(
    linhas,
    rotulos
):
    if isinstance(
        rotulos,
        str,
    ):
        rotulos = [
            rotulos
        ]

    rotulos = [
        normalizar(
            rotulo
        )
        for rotulo in rotulos
    ]

    for indice, linha in enumerate(
        linhas
    ):
        linha_normalizada = (
            normalizar(
                linha
            )
        )

        for rotulo in rotulos:
            if (
                linha_normalizada
                == rotulo
            ):
                return indice

    return None


def valor_depois(
    linhas,
    rotulos
):
    indice = localizar_rotulo(
        linhas,
        rotulos
    )

    if indice is None:
        return ""

    if (
        indice + 1
        >= len(linhas)
    ):
        return ""

    return linhas[
        indice + 1
    ]


# ============================================================
# BLOCO DE TEXTO
# ============================================================

def extrair_bloco(
    linhas,
    rotulos_inicio,
    rotulos_fim
):
    inicio = localizar_rotulo(
        linhas,
        rotulos_inicio
    )

    if inicio is None:
        return ""

    finais = {
        normalizar(
            item
        )
        for item
        in rotulos_fim
    }

    resultado = []

    for linha in linhas[
        inicio + 1:
    ]:

        if (
            normalizar(
                linha
            )
            in finais
        ):
            break

        resultado.append(
            linha
        )

    return limpar_texto(
        " ".join(
            resultado
        )
    )


# ============================================================
# IDENTIFICAÇÃO DO TEMA
# ============================================================

def tema_presente(
    numero,
    texto
):
    texto_n = normalizar(
        texto
    )

    padroes = [
        f"tema repetitivo {numero}",
        f"tema {numero}",
        f"tema repetitivo n {numero}",
        f"tema repetitivo numero {numero}",
    ]

    return any(
        normalizar(
            padrao
        )
        in texto_n
        for padrao
        in padroes
    )


# ============================================================
# EXTRAÇÃO OFICIAL
# ============================================================

def extrair_dados(
    numero,
    texto
):
    if not tema_presente(
        numero,
        texto
    ):
        return None

    linhas = obter_linhas(
        texto
    )

    situacao = valor_depois(
        linhas,
        [
            "Situação",
            "Situação do Tema",
        ],
    )

    questao = extrair_bloco(
        linhas,
        [
            "Questão submetida a julgamento",
            "Questão submetida",
        ],
        {
            "Tese Firmada",
            "Tese firmada",
            "Anotações NUGEPNAC",
            "Informações Complementares",
            "Processos",
            "Processos Paradigma",
            "Afetação",
            "Julgamento",
        },
    )

    tese = extrair_bloco(
        linhas,
        [
            "Tese Firmada",
            "Tese firmada",
        ],
        {
            "Anotações NUGEPNAC",
            "Informações Complementares",
            "Processos",
            "Processos Paradigma",
            "Afetação",
            "Julgamento",
            "Última atualização",
            "Última atualização:",
        },
    )

    return {
        "situacao": limpar_texto(
            situacao
        ),
        "questao": limpar_texto(
            questao
        ),
        "tese": limpar_texto(
            tese
        ),
    }


# ============================================================
# CLASSIFICAÇÃO DO STATUS OFICIAL
# ============================================================

def classificar_status_stj(
    situacao
):
    situacao_n = normalizar(
        situacao
    )

    if (
        "cancelado"
        in situacao_n
        or "cancelada"
        in situacao_n
    ):
        return {
            "categoria": "cancelado",
            "status_interno": "cancelado",
            "descricao": "CANCELADO",
        }

    if (
        "superado"
        in situacao_n
        or "superada"
        in situacao_n
    ):
        return {
            "categoria": "superado",
            "status_interno": "superado",
            "descricao": "SUPERADO",
        }

    termos_pendentes = [
        "afetado",
        "afetada",
        "aguardando julgamento",
        "pendente de julgamento",
        "em julgamento",
    ]

    if any(
        termo
        in situacao_n
        for termo
        in termos_pendentes
    ):
        return {
            "categoria": "pendente",
            "status_interno": "pendente",
            "descricao": (
                "AFETADO / "
                "PENDENTE DE JULGAMENTO"
            ),
        }

    termos_julgados = [
        "transito em julgado",
        "acordao publicado",
        "julgado",
        "re pendente",
    ]

    if any(
        termo
        in situacao_n
        for termo
        in termos_julgados
    ):
        return {
            "categoria": "julgado",
            "status_interno": "julgado",
            "descricao": "JULGADO",
        }

    return {
        "categoria": "desconhecido",
        "status_interno": None,
        "descricao": (
            "STATUS NÃO CLASSIFICADO"
        ),
    }


# ============================================================
# COMPARAÇÃO DE TESES
# ============================================================

def comparar_teses(
    texto_local,
    tese_oficial
):
    oficial = normalizar(
        tese_oficial
    )

    local = normalizar(
        texto_local
    )

    if not oficial:
        return "sem_tese"

    if not local:
        return "inconclusivo"

    if local == oficial:
        return "igual"

    if (
        local in oficial
        or oficial in local
    ):
        return "semelhante"

    palavras_local = set(
        local.split()
    )

    palavras_oficial = set(
        oficial.split()
    )

    if not palavras_local:
        return "inconclusivo"

    intersecao = (
        palavras_local
        & palavras_oficial
    )

    proporcao = (
        len(intersecao)
        / len(palavras_local)
    )

    if proporcao >= 0.70:
        return "semelhante"

    return "divergente"


# ============================================================
# RESULTADO JURÍDICO/TÉCNICO
# ============================================================

def interpretar_resultado(
    registro,
    dados
):
    status = (
        classificar_status_stj(
            dados[
                "situacao"
            ]
        )
    )

    tese = dados[
        "tese"
    ]

    comparacao = comparar_teses(
        registro.get(
            "texto",
            "",
        ),
        tese,
    )

    categoria = status[
        "categoria"
    ]

    if categoria == "pendente":
        return {
            "resultado": "pendente",
            "comparacao": (
                "sem_tese"
                if not tese
                else comparacao
            ),
            "descricao": (
                "AFETADO / "
                "PENDENTE DE JULGAMENTO"
            ),
            "status": status,
        }

    if categoria == "cancelado":
        return {
            "resultado": "cancelado",
            "comparacao": comparacao,
            "descricao": "CANCELADO",
            "status": status,
        }

    if categoria == "superado":
        return {
            "resultado": "superado",
            "comparacao": comparacao,
            "descricao": "SUPERADO",
            "status": status,
        }

    if categoria == "julgado":

        if not tese:
            return {
                "resultado": (
                    "inconclusivo"
                ),
                "comparacao": (
                    "sem_tese"
                ),
                "descricao": (
                    "JULGADO, MAS TESE "
                    "NÃO EXTRAÍDA"
                ),
                "status": status,
            }

        if (
            comparacao
            == "divergente"
        ):
            return {
                "resultado": (
                    "divergencia"
                ),
                "comparacao": (
                    comparacao
                ),
                "descricao": (
                    "DIVERGÊNCIA DE TESE"
                ),
                "status": status,
            }

        return {
            "resultado": (
                "verificado"
            ),
            "comparacao": (
                comparacao
            ),
            "descricao": (
                "JULGADO / "
                "TESE CONFIRMADA"
            ),
            "status": status,
        }

    return {
        "resultado": (
            "inconclusivo"
        ),
        "comparacao": (
            comparacao
        ),
        "descricao": (
            "SITUAÇÃO NÃO CLASSIFICADA"
        ),
        "status": status,
    }


# ============================================================
# ATUALIZAÇÃO DO REGISTRO
# ============================================================

def atualizar_registro(
    registro,
    pagina,
    dados,
    interpretacao
):
    registro[
        "status_oficial_stj"
    ] = dados[
        "situacao"
    ]

    registro[
        "ultima_verificacao"
    ] = hoje()

    registro[
        "url_verificacao"
    ] = pagina[
        "url"
    ]

    if dados[
        "questao"
    ]:
        registro[
            "questao_oficial_verificada"
        ] = dados[
            "questao"
        ]

    if dados[
        "tese"
    ]:
        registro[
            "texto_oficial_verificado"
        ] = dados[
            "tese"
        ]

    status_interno = (
        interpretacao[
            "status"
        ][
            "status_interno"
        ]
    )

    if status_interno:
        registro[
            "status"
        ] = status_interno

    registro[
        "resultado_ultima_verificacao_stj"
    ] = interpretacao[
        "resultado"
    ]


# ============================================================
# TEMAS REPETITIVOS
# ============================================================

def obter_repetitivos(
    catalogo
):
    return [
        registro
        for registro
        in catalogo
        if (
            registro.get(
                "tribunal"
            ) == "STJ"
            and registro.get(
                "tipo"
            ) == "repetitivo"
        )
    ]


# ============================================================
# RELATÓRIO
# ============================================================

def gerar_relatorio(
    backup,
    total_catalogo,
    pulados,
    resultados,
    contadores,
    modo_forcado,
):
    PASTA_INDICES.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas = [
        "LEX MACHINA",
        "VERIFICAÇÃO EM LOTE - STJ",
        "=" * 78,
        "",
        f"DATA: {agora()}",
        (
            "MODO: "
            + (
                "FORÇADO"
                if modo_forcado
                else "NORMAL"
            )
        ),
        (
            "BACKUP: "
            f"{backup}"
        ),
        "",
        (
            "TEMAS REPETITIVOS NO CATÁLOGO: "
            f"{total_catalogo}"
        ),
        (
            "PULADOS POR JÁ ESTAREM "
            "VERIFICADOS HOJE: "
            f"{pulados}"
        ),
        (
            "CONSULTADOS AGORA: "
            f"{len(resultados)}"
        ),
        "",
        (
            "JULGADOS VERIFICADOS: "
            f"{contadores['verificados']}"
        ),
        (
            "PENDENTES / AFETADOS: "
            f"{contadores['pendentes']}"
        ),
        (
            "DIVERGÊNCIAS: "
            f"{contadores['divergencias']}"
        ),
        (
            "CANCELADOS: "
            f"{contadores['cancelados']}"
        ),
        (
            "SUPERADOS: "
            f"{contadores['superados']}"
        ),
        (
            "INCONCLUSIVOS REAIS: "
            f"{contadores['inconclusivos']}"
        ),
        (
            "ERROS: "
            f"{contadores['erros']}"
        ),
        "",
        "=" * 78,
        "DETALHES",
        "=" * 78,
        "",
    ]

    for item in resultados:

        linhas.extend(
            [
                (
                    f"TEMA "
                    f"{item['numero']}"
                ),
                (
                    "RESULTADO: "
                    f"{item['resultado'].upper()}"
                ),
                (
                    "SITUAÇÃO STJ: "
                    f"{item['situacao']}"
                ),
                (
                    "COMPARAÇÃO: "
                    f"{item['comparacao']}"
                ),
                (
                    "URL: "
                    f"{item['url']}"
                ),
                "",
                "-" * 78,
                "",
            ]
        )

    RELATORIO.write_text(
        "\n".join(
            linhas
        ),
        encoding="utf-8",
        newline="\n",
    )

    return RELATORIO


# ============================================================
# EXIBIÇÃO
# ============================================================

def imprimir_resultado(
    interpretacao,
    dados
):
    resultado = interpretacao[
        "resultado"
    ]

    if resultado == "verificado":
        print(
            "✓ JULGADO / TESE CONFIRMADA"
        )

    elif resultado == "pendente":
        print(
            "⏳ AFETADO / "
            "PENDENTE DE JULGAMENTO"
        )

    elif resultado == "divergencia":
        print(
            "⚠ DIVERGÊNCIA DE TESE"
        )

    elif resultado == "cancelado":
        print(
            "⚠ TEMA CANCELADO"
        )

    elif resultado == "superado":
        print(
            "⚠ TEMA SUPERADO"
        )

    else:
        print(
            "△ INCONCLUSIVO"
        )

    print(
        "Situação STJ: "
        f"{dados['situacao']}"
    )

    if dados[
        "tese"
    ]:
        print(
            "Tese oficial: encontrada"
        )

    else:
        print(
            "Tese oficial: "
            "ainda inexistente/não encontrada"
        )

    print(
        "Comparação: "
        f"{interpretacao['comparacao']}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    args = ler_argumentos()

    modo_forcado = (
        args.forcar
    )

    print()
    print(
        "LEX MACHINA - "
        "VERIFICAÇÃO STJ EM LOTE"
    )
    print(
        "=" * 60
    )
    print()

    if modo_forcado:
        print(
            "MODO FORÇADO ATIVADO"
        )

        print(
            "Todos os Temas Repetitivos "
            "serão consultados novamente."
        )

        print()

    else:
        print(
            "MODO NORMAL"
        )

        print(
            "Temas já verificados hoje "
            "serão ignorados."
        )

        print()

    catalogo = carregar_catalogo()

    repetitivos = obter_repetitivos(
        catalogo
    )

    print(
        "Temas repetitivos no catálogo: "
        f"{len(repetitivos)}"
    )

    backup = criar_backup()

    print(
        f"Backup: {backup}"
    )

    print()

    verificar = []
    pulados = 0

    for registro in repetitivos:

        if (
            not modo_forcado
            and registro.get(
                "ultima_verificacao"
            ) == hoje()
        ):
            pulados += 1

            continue

        verificar.append(
            registro
        )

    print(
        "Já verificados hoje e pulados: "
        f"{pulados}"
    )

    print(
        "Serão consultados agora: "
        f"{len(verificar)}"
    )

    print()

    contadores = {
        "verificados": 0,
        "pendentes": 0,
        "divergencias": 0,
        "cancelados": 0,
        "superados": 0,
        "inconclusivos": 0,
        "erros": 0,
    }

    resultados = []

    if verificar:

        with sync_playwright() as p:

            navegador, contexto = (
                abrir_navegador(
                    p
                )
            )

            try:

                for indice, registro in enumerate(
                    verificar,
                    start=1,
                ):

                    numero = int(
                        registro[
                            "numero"
                        ]
                    )

                    print(
                        f"[{indice}/{len(verificar)}] "
                        f"Tema {numero}"
                    )

                    try:

                        pagina = carregar_tema(
                            contexto,
                            numero,
                        )

                        dados = extrair_dados(
                            numero,
                            pagina[
                                "texto"
                            ],
                        )

                        if dados is None:

                            print(
                                "△ INCONCLUSIVO"
                            )

                            print(
                                "O Tema não pôde ser "
                                "identificado no conteúdo."
                            )

                            contadores[
                                "inconclusivos"
                            ] += 1

                            resultados.append(
                                {
                                    "numero": numero,
                                    "resultado": (
                                        "inconclusivo"
                                    ),
                                    "situacao": "",
                                    "comparacao": (
                                        "não realizada"
                                    ),
                                    "url": pagina[
                                        "url"
                                    ],
                                }
                            )

                            print()

                            time.sleep(
                                PAUSA_ENTRE_TEMAS
                            )

                            continue

                        interpretacao = (
                            interpretar_resultado(
                                registro,
                                dados,
                            )
                        )

                        atualizar_registro(
                            registro,
                            pagina,
                            dados,
                            interpretacao,
                        )

                        resultado = (
                            interpretacao[
                                "resultado"
                            ]
                        )

                        if resultado == "verificado":
                            contadores[
                                "verificados"
                            ] += 1

                        elif resultado == "pendente":
                            contadores[
                                "pendentes"
                            ] += 1

                        elif resultado == "divergencia":
                            contadores[
                                "divergencias"
                            ] += 1

                        elif resultado == "cancelado":
                            contadores[
                                "cancelados"
                            ] += 1

                        elif resultado == "superado":
                            contadores[
                                "superados"
                            ] += 1

                        else:
                            contadores[
                                "inconclusivos"
                            ] += 1

                        imprimir_resultado(
                            interpretacao,
                            dados,
                        )

                        resultados.append(
                            {
                                "numero": numero,
                                "resultado": resultado,
                                "situacao": (
                                    dados[
                                        "situacao"
                                    ]
                                ),
                                "comparacao": (
                                    interpretacao[
                                        "comparacao"
                                    ]
                                ),
                                "url": pagina[
                                    "url"
                                ],
                            }
                        )

                    except (
                        PlaywrightTimeoutError,
                        OSError,
                        RuntimeError,
                        ValueError,
                        KeyError,
                    ) as erro:

                        contadores[
                            "erros"
                        ] += 1

                        print(
                            "✗ ERRO"
                        )

                        print(
                            erro
                        )

                        resultados.append(
                            {
                                "numero": numero,
                                "resultado": "erro",
                                "situacao": "",
                                "comparacao": "",
                                "url": url_tema(
                                    numero
                                ),
                            }
                        )

                    print()

                    time.sleep(
                        PAUSA_ENTRE_TEMAS
                    )

            finally:

                contexto.close()
                navegador.close()

    # ========================================================
    # SALVAR CATÁLOGO
    # ========================================================

    salvar_catalogo(
        catalogo
    )

    # ========================================================
    # RELATÓRIO
    # ========================================================

    relatorio = gerar_relatorio(
        backup,
        len(repetitivos),
        pulados,
        resultados,
        contadores,
        modo_forcado,
    )

    # ========================================================
    # RESUMO FINAL
    # ========================================================

    print()
    print(
        "=" * 60
    )

    print(
        "VERIFICAÇÃO EM LOTE FINALIZADA"
    )

    print(
        "Modo: "
        + (
            "FORÇADO"
            if modo_forcado
            else "NORMAL"
        )
    )

    print(
        "Temas repetitivos no catálogo: "
        f"{len(repetitivos)}"
    )

    print(
        "Pulados por já estarem "
        "verificados hoje: "
        f"{pulados}"
    )

    print(
        "Consultados agora: "
        f"{len(resultados)}"
    )

    print()

    print(
        "✓ Julgados / teses confirmadas: "
        f"{contadores['verificados']}"
    )

    print(
        "⏳ Afetados / pendentes: "
        f"{contadores['pendentes']}"
    )

    print(
        "⚠ Divergências: "
        f"{contadores['divergencias']}"
    )

    print(
        "⚠ Cancelados: "
        f"{contadores['cancelados']}"
    )

    print(
        "⚠ Superados: "
        f"{contadores['superados']}"
    )

    print(
        "△ Inconclusivos reais: "
        f"{contadores['inconclusivos']}"
    )

    print(
        "✗ Erros: "
        f"{contadores['erros']}"
    )

    print()

    print(
        f"Relatório: "
        f"{relatorio}"
    )

    print()

    print(
        "O campo 'texto' original "
        "não foi sobrescrito."
    )

    print(
        "Quando existente, a tese oficial "
        "permanece em "
        "'texto_oficial_verificado'."
    )


if __name__ == "__main__":
    main()