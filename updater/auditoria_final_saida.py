from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict
import json
import re


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_SAIDA = Path(
    "saida"
)

PASTA_JURISPRUDENCIA = (
    PASTA_SAIDA
    / "19_JURISPRUDENCIA"
)

PASTA_INDICES = (
    PASTA_SAIDA
    / "99_INDICES"
)

RELATORIO_TXT = (
    PASTA_INDICES
    / "RELATORIO_AUDITORIA_FINAL_LEX_MACHINA.txt"
)

RELATORIO_JSON = (
    PASTA_INDICES
    / "RELATORIO_AUDITORIA_FINAL_LEX_MACHINA.json"
)


# ============================================================
# UTILITÁRIOS
# ============================================================

def agora():
    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def limpar_texto(
    texto
):
    texto = str(
        texto or ""
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


def caminho_normalizado(
    caminho
):
    return str(
        caminho
    ).replace(
        "\\",
        "/",
    ).casefold()


# ============================================================
# CARREGAR CATÁLOGO
# ============================================================

def carregar_catalogo():
    if not CATALOGO.exists():
        raise FileNotFoundError(
            "catalogo_jurisprudencia.json "
            "não foi encontrado."
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


# ============================================================
# IDENTIFICAR JURISPRUDÊNCIAS
# ============================================================

def eh_jurisprudencia(
    item
):
    tribunal = limpar_texto(
        item.get(
            "tribunal",
            ""
        )
    )

    tipo = limpar_texto(
        item.get(
            "tipo",
            ""
        )
    )

    return bool(
        tribunal
        and tipo
    )


# ============================================================
# STATUS
# ============================================================

def status_normalizado(
    item
):
    status = limpar_texto(
        item.get(
            "status",
            ""
        )
    ).casefold()

    oficial = limpar_texto(
        item.get(
            "status_oficial_stj",
            ""
        )
    ).casefold()

    resultado = limpar_texto(
        item.get(
            "resultado_ultima_verificacao_stj",
            ""
        )
    ).casefold()

    # --------------------------------------------------------
    # STATUS DIRETO
    # --------------------------------------------------------

    if status in {
        "julgado",
        "pendente",
        "sobrestado",
        "cancelado",
        "superado",
    }:
        return status

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if "cancelad" in oficial:
        return "cancelado"

    if "superad" in oficial:
        return "superado"

    if "sobrestad" in oficial:
        return "sobrestado"

    if (
        "afetad" in oficial
        or "em julgamento" in oficial
        or resultado == "pendente"
    ):
        return "pendente"

    if (
        "transito em julgado" in oficial
        or "trânsito em julgado" in oficial
        or "acordao publicado" in oficial
        or "acórdão publicado" in oficial
        or resultado == "verificado"
    ):
        return "julgado"

    return status or "desconhecido"


# ============================================================
# PASTA ESPERADA
# ============================================================

def pasta_status_esperada(
    item
):
    tipo = limpar_texto(
        item.get(
            "tipo",
            ""
        )
    ).casefold()

    if tipo == "sumula":
        return "SUMULAS"

    if tipo == "súmula":
        return "SUMULAS"

    status = status_normalizado(
        item
    )

    mapa = {
        "julgado": "JULGADOS",
        "pendente": "PENDENTES",
        "sobrestado": "SOBRESTADOS",
        "cancelado": "CANCELADOS",
        "superado": "SUPERADOS",
    }

    return mapa.get(
        status,
        ""
    )


# ============================================================
# LOCALIZAR ARQUIVO GERADO
# ============================================================

def localizar_arquivo(
    nome_arquivo
):
    if not nome_arquivo:
        return []

    encontrados = []

    for caminho in (
        PASTA_JURISPRUDENCIA.rglob(
            nome_arquivo
        )
    ):
        if caminho.is_file():
            encontrados.append(
                caminho
            )

    return encontrados


# ============================================================
# VALIDAR CONTEÚDO TXT
# ============================================================

def validar_txt(
    caminho
):
    problemas = []

    try:
        texto = caminho.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        try:
            texto = caminho.read_text(
                encoding="cp1252"
            )

            problemas.append(
                "Arquivo não está em UTF-8."
            )

        except Exception as erro:
            return [
                "Não foi possível ler o arquivo: "
                f"{erro}"
            ]

    if not texto.strip():
        problemas.append(
            "Arquivo vazio."
        )

    if len(
        texto.strip()
    ) < 20:
        problemas.append(
            "Conteúdo muito curto."
        )

    return problemas


# ============================================================
# AUDITORIA DO CATÁLOGO
# ============================================================

def auditar_catalogo(
    jurisprudencias
):
    problemas = []

    chaves = []

    for item in jurisprudencias:

        tribunal = limpar_texto(
            item.get(
                "tribunal",
                ""
            )
        )

        tipo = limpar_texto(
            item.get(
                "tipo",
                ""
            )
        )

        numero = item.get(
            "numero"
        )

        chave = (
            tribunal.casefold(),
            tipo.casefold(),
            str(
                numero
            ),
        )

        chaves.append(
            chave
        )

    contagem = Counter(
        chaves
    )

    duplicados = [
        chave
        for chave, quantidade
        in contagem.items()
        if quantidade > 1
    ]

    for chave in duplicados:
        problemas.append(
            {
                "tipo": "duplicidade_catalogo",
                "detalhe": (
                    "Registro duplicado: "
                    f"{chave}"
                ),
            }
        )

    return problemas


# ============================================================
# AUDITORIA DOS ARQUIVOS
# ============================================================

def auditar_arquivos(
    jurisprudencias
):
    problemas = []

    arquivos_referenciados = set()

    estatisticas = defaultdict(
        int
    )

    for item in jurisprudencias:

        tribunal = limpar_texto(
            item.get(
                "tribunal",
                ""
            )
        )

        tipo = limpar_texto(
            item.get(
                "tipo",
                ""
            )
        )

        numero = item.get(
            "numero"
        )

        arquivo = limpar_texto(
            item.get(
                "arquivo",
                ""
            )
        )

        identificador = (
            f"{tribunal} "
            f"{tipo} "
            f"{numero}"
        )

        if not arquivo:
            problemas.append(
                {
                    "tipo": "arquivo_nao_definido",
                    "detalhe": (
                        f"{identificador}: "
                        "campo 'arquivo' vazio."
                    ),
                }
            )

            continue

        encontrados = localizar_arquivo(
            arquivo
        )

        if not encontrados:
            problemas.append(
                {
                    "tipo": "arquivo_ausente",
                    "detalhe": (
                        f"{identificador}: "
                        f"{arquivo} não foi encontrado."
                    ),
                }
            )

            continue

        if len(
            encontrados
        ) > 1:
            problemas.append(
                {
                    "tipo": "arquivo_duplicado",
                    "detalhe": (
                        f"{identificador}: "
                        f"{arquivo} aparece "
                        f"{len(encontrados)} vezes."
                    ),
                }
            )

        caminho = encontrados[
            0
        ]

        arquivos_referenciados.add(
            caminho.resolve()
        )

        # ----------------------------------------------------
        # CONTEÚDO
        # ----------------------------------------------------

        problemas_txt = validar_txt(
            caminho
        )

        for problema in problemas_txt:
            problemas.append(
                {
                    "tipo": "conteudo_txt",
                    "detalhe": (
                        f"{identificador}: "
                        f"{problema}"
                    ),
                }
            )

        # ----------------------------------------------------
        # STATUS X PASTA
        # ----------------------------------------------------

        pasta_esperada = (
            pasta_status_esperada(
                item
            )
        )

        if pasta_esperada:

            partes = [
                parte.casefold()
                for parte
                in caminho.parts
            ]

            if (
                pasta_esperada.casefold()
                not in partes
            ):
                problemas.append(
                    {
                        "tipo": "pasta_status_incorreta",
                        "detalhe": (
                            f"{identificador}: "
                            f"status exige pasta "
                            f"{pasta_esperada}, "
                            f"mas arquivo está em "
                            f"{caminho}."
                        ),
                    }
                )

        # ----------------------------------------------------
        # ESTATÍSTICAS
        # ----------------------------------------------------

        status = status_normalizado(
            item
        )

        estatisticas[
            f"status_{status}"
        ] += 1

        estatisticas[
            f"tipo_{tipo.casefold()}"
        ] += 1

    return (
        problemas,
        arquivos_referenciados,
        estatisticas,
    )


# ============================================================
# ARQUIVOS ÓRFÃOS
# ============================================================

def auditar_orfaos(
    arquivos_referenciados
):
    problemas = []

    if not PASTA_JURISPRUDENCIA.exists():
        return [
            {
                "tipo": "pasta_ausente",
                "detalhe": (
                    "A pasta 19_JURISPRUDENCIA "
                    "não existe."
                ),
            }
        ]

    todos_txt = {
        caminho.resolve()
        for caminho
        in PASTA_JURISPRUDENCIA.rglob(
            "*.txt"
        )
        if caminho.is_file()
    }

    orfaos = (
        todos_txt
        - arquivos_referenciados
    )

    for caminho in sorted(
        orfaos,
        key=lambda item: str(
            item
        )
    ):
        problemas.append(
            {
                "tipo": "arquivo_orfao",
                "detalhe": (
                    "Arquivo sem registro correspondente "
                    f"no catálogo: {caminho}"
                ),
            }
        )

    return problemas


# ============================================================
# AUDITORIA DOS ÍNDICES
# ============================================================

def auditar_indices():
    esperados = [
        PASTA_INDICES
        / "INDICE_JURISPRUDENCIA_CDC.txt",

        PASTA_INDICES
        / "INDICE_ARTIGOS_CDC.txt",

        PASTA_INDICES
        / "RELATORIO_JURISPRUDENCIA.txt",
    ]

    problemas = []

    existentes = []

    for caminho in esperados:

        if not caminho.exists():
            problemas.append(
                {
                    "tipo": "indice_ausente",
                    "detalhe": (
                        f"Arquivo obrigatório ausente: "
                        f"{caminho}"
                    ),
                }
            )

            continue

        existentes.append(
            str(
                caminho
            )
        )

        if caminho.stat().st_size == 0:
            problemas.append(
                {
                    "tipo": "indice_vazio",
                    "detalhe": (
                        f"Arquivo vazio: "
                        f"{caminho}"
                    ),
                }
            )

    return (
        problemas,
        existentes,
    )


# ============================================================
# AUDITORIA DO RELATÓRIO GERAL
# ============================================================

def auditar_relatorio_geral():
    caminho = (
        PASTA_SAIDA
        / "RELATORIO_ATUALIZACAO.txt"
    )

    if not caminho.exists():
        return [
            {
                "tipo": "relatorio_geral_ausente",
                "detalhe": (
                    "saida/RELATORIO_ATUALIZACAO.txt "
                    "não foi encontrado."
                ),
            }
        ]

    if caminho.stat().st_size == 0:
        return [
            {
                "tipo": "relatorio_geral_vazio",
                "detalhe": (
                    "RELATORIO_ATUALIZACAO.txt "
                    "está vazio."
                ),
            }
        ]

    return []


# ============================================================
# RELATÓRIO TXT
# ============================================================

def gerar_relatorio_txt(
    total_catalogo,
    jurisprudencias,
    estatisticas,
    problemas,
    indices,
):
    PASTA_INDICES.mkdir(
        parents=True,
        exist_ok=True,
    )

    por_tipo = Counter(
        limpar_texto(
            item.get(
                "tipo",
                ""
            )
        ).casefold()
        for item
        in jurisprudencias
    )

    por_status = Counter(
        status_normalizado(
            item
        )
        for item
        in jurisprudencias
        if limpar_texto(
            item.get(
                "tipo",
                ""
            )
        ).casefold()
        not in {
            "sumula",
            "súmula",
        }
    )

    linhas = [
        "LEX MACHINA",
        "AUDITORIA FINAL DA SAÍDA",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        "",
        f"REGISTROS TOTAIS NO CATÁLOGO: {total_catalogo}",
        (
            "JURISPRUDÊNCIAS NO CATÁLOGO: "
            f"{len(jurisprudencias)}"
        ),
        "",
        "TIPOS:",
    ]

    for tipo, quantidade in sorted(
        por_tipo.items()
    ):
        linhas.append(
            f"- {tipo}: {quantidade}"
        )

    linhas.extend(
        [
            "",
            "STATUS DOS PRECEDENTES:",
        ]
    )

    for status, quantidade in sorted(
        por_status.items()
    ):
        linhas.append(
            f"- {status}: {quantidade}"
        )

    linhas.extend(
        [
            "",
            "ÍNDICES CONFIRMADOS:",
        ]
    )

    for indice in indices:
        linhas.append(
            f"- {indice}"
        )

    linhas.extend(
        [
            "",
            "=" * 78,
            "RESULTADO",
            "=" * 78,
            "",
            (
                "PROBLEMAS ENCONTRADOS: "
                f"{len(problemas)}"
            ),
            "",
        ]
    )

    if not problemas:
        linhas.extend(
            [
                "AUDITORIA APROVADA.",
                "",
                (
                    "Nenhum arquivo ausente, "
                    "duplicado, órfão ou em pasta "
                    "incompatível foi identificado."
                ),
                "",
            ]
        )

    else:

        agrupados = defaultdict(
            list
        )

        for problema in problemas:
            agrupados[
                problema[
                    "tipo"
                ]
            ].append(
                problema[
                    "detalhe"
                ]
            )

        for tipo in sorted(
            agrupados
        ):

            linhas.append(
                tipo.upper()
            )

            linhas.append(
                "-" * 78
            )

            for detalhe in (
                agrupados[
                    tipo
                ]
            ):
                linhas.append(
                    f"- {detalhe}"
                )

            linhas.append("")

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

def gerar_relatorio_json(
    total_catalogo,
    jurisprudencias,
    estatisticas,
    problemas,
):
    estrutura = {
        "gerado_em": (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ),

        "total_catalogo": (
            total_catalogo
        ),

        "total_jurisprudencias": (
            len(
                jurisprudencias
            )
        ),

        "estatisticas": dict(
            estatisticas
        ),

        "problemas_encontrados": (
            len(
                problemas
            )
        ),

        "aprovado": (
            len(
                problemas
            )
            == 0
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
        "AUDITORIA FINAL DA SAÍDA"
    )

    print(
        "=" * 60
    )

    print()

    catalogo = carregar_catalogo()

    jurisprudencias = [
        item
        for item
        in catalogo
        if eh_jurisprudencia(
            item
        )
    ]

    print(
        f"Registros no catálogo: "
        f"{len(catalogo)}"
    )

    print(
        f"Jurisprudências: "
        f"{len(jurisprudencias)}"
    )

    problemas = []

    # --------------------------------------------------------
    # CATÁLOGO
    # --------------------------------------------------------

    print()
    print(
        "1/5 - Auditando catálogo..."
    )

    problemas.extend(
        auditar_catalogo(
            jurisprudencias
        )
    )

    # --------------------------------------------------------
    # ARQUIVOS
    # --------------------------------------------------------

    print(
        "2/5 - Auditando arquivos..."
    )

    (
        problemas_arquivos,
        arquivos_referenciados,
        estatisticas,
    ) = auditar_arquivos(
        jurisprudencias
    )

    problemas.extend(
        problemas_arquivos
    )

    # --------------------------------------------------------
    # ÓRFÃOS
    # --------------------------------------------------------

    print(
        "3/5 - Procurando arquivos órfãos..."
    )

    problemas.extend(
        auditar_orfaos(
            arquivos_referenciados
        )
    )

    # --------------------------------------------------------
    # ÍNDICES
    # --------------------------------------------------------

    print(
        "4/5 - Auditando índices..."
    )

    (
        problemas_indices,
        indices_confirmados,
    ) = auditar_indices()

    problemas.extend(
        problemas_indices
    )

    # --------------------------------------------------------
    # RELATÓRIO GERAL
    # --------------------------------------------------------

    print(
        "5/5 - Auditando relatório geral..."
    )

    problemas.extend(
        auditar_relatorio_geral()
    )

    # --------------------------------------------------------
    # RELATÓRIOS
    # --------------------------------------------------------

    relatorio_txt = gerar_relatorio_txt(
        len(catalogo),
        jurisprudencias,
        estatisticas,
        problemas,
        indices_confirmados,
    )

    relatorio_json = gerar_relatorio_json(
        len(catalogo),
        jurisprudencias,
        estatisticas,
        problemas,
    )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    print()

    print(
        "=" * 60
    )

    print(
        "AUDITORIA FINALIZADA"
    )

    print()

    print(
        f"Jurisprudências auditadas: "
        f"{len(jurisprudencias)}"
    )

    print(
        f"Problemas encontrados: "
        f"{len(problemas)}"
    )

    print()

    if not problemas:

        print(
            "✓ AUDITORIA APROVADA"
        )

        print()

        print(
            "A estrutura jurisprudencial "
            "gerada está íntegra."
        )

    else:

        print(
            "⚠ AUDITORIA REQUER ATENÇÃO"
        )

        print()

        contagem_problemas = Counter(
            problema[
                "tipo"
            ]
            for problema
            in problemas
        )

        for tipo, quantidade in sorted(
            contagem_problemas.items()
        ):
            print(
                f"- {tipo}: "
                f"{quantidade}"
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
        "Nenhum arquivo foi alterado "
        "por esta auditoria."
    )


if __name__ == "__main__":
    main()