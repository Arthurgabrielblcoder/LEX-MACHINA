from datetime import datetime
from pathlib import Path
import json
import re


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CATALOGO = Path(
    "catalogo_jurisprudencia.json"
)

PASTA_SAIDA = Path(
    "saida/99_INDICES"
)

RELATORIO_TXT = (
    PASTA_SAIDA
    / "RELATORIO_AUDITORIA_RESULTADO_STJ.txt"
)

RELATORIO_JSON = (
    PASTA_SAIDA
    / "RELATORIO_AUDITORIA_RESULTADO_STJ.json"
)


# ============================================================
# UTILITÁRIOS
# ============================================================

def limpar_texto(texto):
    texto = str(
        texto or ""
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


def agora():
    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


# ============================================================
# CARREGAR CATÁLOGO
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


# ============================================================
# FILTRAR TEMAS REPETITIVOS
# ============================================================

def obter_temas_repetitivos(
    catalogo
):
    return [
        item
        for item in catalogo
        if (
            item.get(
                "tribunal"
            ) == "STJ"
            and item.get(
                "tipo"
            ) == "repetitivo"
        )
    ]


# ============================================================
# CLASSIFICAÇÃO DO RESULTADO
# ============================================================

def classificar_resultado(
    registro
):
    resultado = limpar_texto(
        registro.get(
            "resultado_ultima_verificacao_stj",
            "",
        )
    ).casefold()

    status = limpar_texto(
        registro.get(
            "status",
            "",
        )
    ).casefold()

    status_oficial = limpar_texto(
        registro.get(
            "status_oficial_stj",
            "",
        )
    ).casefold()

    # --------------------------------------------------------
    # RESULTADO SALVO PELO VERIFICADOR
    # --------------------------------------------------------

    if resultado == "verificado":
        return "confirmado"

    if resultado == "pendente":
        return "pendente"

    if resultado == "divergencia":
        return "divergencia"

    if resultado == "cancelado":
        return "cancelado"

    if resultado == "superado":
        return "superado"

    if resultado == "inconclusivo":
        return "inconclusivo"

    # --------------------------------------------------------
    # FALLBACK PELO STATUS INTERNO
    # --------------------------------------------------------

    if status == "cancelado":
        return "cancelado"

    if status == "superado":
        return "superado"

    if status == "pendente":
        return "pendente"

    # --------------------------------------------------------
    # FALLBACK PELO STATUS OFICIAL
    # --------------------------------------------------------

    if (
        "cancelad"
        in status_oficial
    ):
        return "cancelado"

    if (
        "superad"
        in status_oficial
    ):
        return "superado"

    if (
        "afetad"
        in status_oficial
        or "pendente"
        in status_oficial
        or "aguardando julgamento"
        in status_oficial
    ):
        return "pendente"

    return "nao_classificado"


# ============================================================
# RESUMO DO REGISTRO
# ============================================================

def montar_resumo(
    registro
):
    return {
        "numero": registro.get(
            "numero"
        ),

        "tema": limpar_texto(
            registro.get(
                "tema",
                "",
            )
        ),

        "status_interno": limpar_texto(
            registro.get(
                "status",
                "",
            )
        ),

        "status_oficial_stj": limpar_texto(
            registro.get(
                "status_oficial_stj",
                "",
            )
        ),

        "resultado_ultima_verificacao_stj": limpar_texto(
            registro.get(
                "resultado_ultima_verificacao_stj",
                "",
            )
        ),

        "ultima_verificacao": limpar_texto(
            registro.get(
                "ultima_verificacao",
                "",
            )
        ),

        "texto_original": limpar_texto(
            registro.get(
                "texto",
                "",
            )
        ),

        "texto_oficial_verificado": limpar_texto(
            registro.get(
                "texto_oficial_verificado",
                "",
            )
        ),

        "questao_oficial_verificada": limpar_texto(
            registro.get(
                "questao_oficial_verificada",
                "",
            )
        ),

        "url_verificacao": limpar_texto(
            registro.get(
                "url_verificacao",
                "",
            )
        ),

        "processos": registro.get(
            "processos",
            [],
        ),

        "arquivo": limpar_texto(
            registro.get(
                "arquivo",
                "",
            )
        ),
    }


# ============================================================
# AUDITORIA
# ============================================================

def auditar(
    temas
):
    grupos = {
        "confirmados": [],
        "pendentes": [],
        "divergencias": [],
        "cancelados": [],
        "superados": [],
        "inconclusivos": [],
        "nao_classificados": [],
    }

    for registro in temas:
        categoria = (
            classificar_resultado(
                registro
            )
        )

        resumo = montar_resumo(
            registro
        )

        if categoria == "confirmado":
            grupos[
                "confirmados"
            ].append(
                resumo
            )

        elif categoria == "pendente":
            grupos[
                "pendentes"
            ].append(
                resumo
            )

        elif categoria == "divergencia":
            grupos[
                "divergencias"
            ].append(
                resumo
            )

        elif categoria == "cancelado":
            grupos[
                "cancelados"
            ].append(
                resumo
            )

        elif categoria == "superado":
            grupos[
                "superados"
            ].append(
                resumo
            )

        elif categoria == "inconclusivo":
            grupos[
                "inconclusivos"
            ].append(
                resumo
            )

        else:
            grupos[
                "nao_classificados"
            ].append(
                resumo
            )

    for lista in grupos.values():
        lista.sort(
            key=lambda item: (
                int(
                    item.get(
                        "numero",
                        0,
                    )
                    or 0
                )
            )
        )

    return grupos


# ============================================================
# RESUMIR TEXTO
# ============================================================

def resumo_texto(
    texto,
    limite=420,
):
    texto = limpar_texto(
        texto
    )

    if len(
        texto
    ) <= limite:
        return texto

    return (
        texto[
            : limite - 3
        ].rstrip()
        + "..."
    )


# ============================================================
# BLOCO DE DETALHE
# ============================================================

def adicionar_detalhe(
    linhas,
    item,
    mostrar_textos=True,
):
    linhas.append(
        f"TEMA {item['numero']}"
    )

    linhas.append(
        f"Título: {item['tema']}"
    )

    linhas.append(
        (
            "Status interno: "
            f"{item['status_interno']}"
        )
    )

    linhas.append(
        (
            "Status oficial STJ: "
            f"{item['status_oficial_stj']}"
        )
    )

    linhas.append(
        (
            "Resultado da última verificação: "
            f"{item['resultado_ultima_verificacao_stj']}"
        )
    )

    linhas.append(
        (
            "Última verificação: "
            f"{item['ultima_verificacao']}"
        )
    )

    if item[
        "processos"
    ]:
        linhas.append(
            "Processos: "
            + ", ".join(
                str(x)
                for x
                in item[
                    "processos"
                ]
            )
        )

    if mostrar_textos:
        if item[
            "questao_oficial_verificada"
        ]:
            linhas.append(
                "Questão oficial:"
            )

            linhas.append(
                resumo_texto(
                    item[
                        "questao_oficial_verificada"
                    ]
                )
            )

        if item[
            "texto_original"
        ]:
            linhas.append(
                "Texto original:"
            )

            linhas.append(
                resumo_texto(
                    item[
                        "texto_original"
                    ]
                )
            )

        if item[
            "texto_oficial_verificado"
        ]:
            linhas.append(
                "Tese oficial verificada:"
            )

            linhas.append(
                resumo_texto(
                    item[
                        "texto_oficial_verificado"
                    ]
                )
            )

    if item[
        "url_verificacao"
    ]:
        linhas.append(
            "URL:"
        )

        linhas.append(
            item[
                "url_verificacao"
            ]
        )

    linhas.append(
        "-" * 78
    )

    linhas.append("")


# ============================================================
# GERAR RELATÓRIO TXT
# ============================================================

def gerar_relatorio_txt(
    grupos,
    total
):
    PASTA_SAIDA.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas = [
        "LEX MACHINA",
        "AUDITORIA DO RESULTADO FINAL - STJ",
        "=" * 78,
        "",
        f"GERADO EM: {agora()}",
        "",
        f"TEMAS REPETITIVOS AUDITADOS: {total}",
        "",
        (
            "CONFIRMADOS: "
            f"{len(grupos['confirmados'])}"
        ),
        (
            "PENDENTES / AFETADOS: "
            f"{len(grupos['pendentes'])}"
        ),
        (
            "DIVERGÊNCIAS: "
            f"{len(grupos['divergencias'])}"
        ),
        (
            "CANCELADOS: "
            f"{len(grupos['cancelados'])}"
        ),
        (
            "SUPERADOS: "
            f"{len(grupos['superados'])}"
        ),
        (
            "INCONCLUSIVOS: "
            f"{len(grupos['inconclusivos'])}"
        ),
        (
            "NÃO CLASSIFICADOS: "
            f"{len(grupos['nao_classificados'])}"
        ),
        "",
        "=" * 78,
        "DECISÃO RECOMENDADA",
        "=" * 78,
        "",
        (
            "CONFIRMADOS -> manter normalmente "
            "e gerar no LEX MACHINA."
        ),
        (
            "PENDENTES -> manter no catálogo, "
            "marcados como pendentes e sem tese "
            "firmada quando ainda inexistente."
        ),
        (
            "CANCELADOS -> manter no catálogo "
            "para histórico, claramente marcados "
            "como cancelados."
        ),
        (
            "SUPERADOS -> manter para histórico, "
            "claramente marcados como superados."
        ),
        (
            "DIVERGÊNCIAS -> revisar antes de considerar "
            "a tese local como equivalente à oficial."
        ),
        (
            "INCONCLUSIVOS -> revisar a extração ou "
            "consultar novamente a fonte oficial."
        ),
        "",
    ]

    # ========================================================
    # DIVERGÊNCIAS
    # ========================================================

    linhas.extend(
        [
            "=" * 78,
            "DIVERGÊNCIAS",
            "=" * 78,
            "",
        ]
    )

    if not grupos[
        "divergencias"
    ]:
        linhas.append(
            "Nenhuma divergência."
        )

        linhas.append("")

    for item in grupos[
        "divergencias"
    ]:
        adicionar_detalhe(
            linhas,
            item,
            mostrar_textos=True,
        )

    # ========================================================
    # INCONCLUSIVOS
    # ========================================================

    linhas.extend(
        [
            "=" * 78,
            "INCONCLUSIVOS",
            "=" * 78,
            "",
        ]
    )

    if not grupos[
        "inconclusivos"
    ]:
        linhas.append(
            "Nenhum inconclusivo."
        )

        linhas.append("")

    for item in grupos[
        "inconclusivos"
    ]:
        adicionar_detalhe(
            linhas,
            item,
            mostrar_textos=True,
        )

    # ========================================================
    # CANCELADOS
    # ========================================================

    linhas.extend(
        [
            "=" * 78,
            "CANCELADOS",
            "=" * 78,
            "",
        ]
    )

    if not grupos[
        "cancelados"
    ]:
        linhas.append(
            "Nenhum cancelado."
        )

        linhas.append("")

    for item in grupos[
        "cancelados"
    ]:
        adicionar_detalhe(
            linhas,
            item,
            mostrar_textos=False,
        )

    # ========================================================
    # PENDENTES
    # ========================================================

    linhas.extend(
        [
            "=" * 78,
            "PENDENTES / AFETADOS",
            "=" * 78,
            "",
        ]
    )

    if not grupos[
        "pendentes"
    ]:
        linhas.append(
            "Nenhum pendente."
        )

        linhas.append("")

    for item in grupos[
        "pendentes"
    ]:
        adicionar_detalhe(
            linhas,
            item,
            mostrar_textos=False,
        )

    # ========================================================
    # SUPERADOS
    # ========================================================

    linhas.extend(
        [
            "=" * 78,
            "SUPERADOS",
            "=" * 78,
            "",
        ]
    )

    if not grupos[
        "superados"
    ]:
        linhas.append(
            "Nenhum superado."
        )

        linhas.append("")

    for item in grupos[
        "superados"
    ]:
        adicionar_detalhe(
            linhas,
            item,
            mostrar_textos=False,
        )

    # ========================================================
    # NÃO CLASSIFICADOS
    # ========================================================

    linhas.extend(
        [
            "=" * 78,
            "NÃO CLASSIFICADOS",
            "=" * 78,
            "",
        ]
    )

    if not grupos[
        "nao_classificados"
    ]:
        linhas.append(
            "Nenhum registro não classificado."
        )

        linhas.append("")

    for item in grupos[
        "nao_classificados"
    ]:
        adicionar_detalhe(
            linhas,
            item,
            mostrar_textos=True,
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
# GERAR RELATÓRIO JSON
# ============================================================

def gerar_relatorio_json(
    grupos,
    total
):
    estrutura = {
        "gerado_em": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "total_temas_repetitivos": total,

        "resumo": {
            "confirmados": len(
                grupos[
                    "confirmados"
                ]
            ),

            "pendentes": len(
                grupos[
                    "pendentes"
                ]
            ),

            "divergencias": len(
                grupos[
                    "divergencias"
                ]
            ),

            "cancelados": len(
                grupos[
                    "cancelados"
                ]
            ),

            "superados": len(
                grupos[
                    "superados"
                ]
            ),

            "inconclusivos": len(
                grupos[
                    "inconclusivos"
                ]
            ),

            "nao_classificados": len(
                grupos[
                    "nao_classificados"
                ]
            ),
        },

        "grupos": grupos,
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
# EXIBIÇÃO RESUMIDA
# ============================================================

def imprimir_lista(
    titulo,
    itens
):
    print(
        titulo
        + ": "
        + str(
            len(
                itens
            )
        )
    )

    for item in itens:
        print(
            f"  - Tema {item['numero']} "
            f"| {item['status_oficial_stj']}"
        )


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print(
        "LEX MACHINA - "
        "AUDITORIA FINAL STJ"
    )
    print(
        "=" * 60
    )
    print()

    catalogo = carregar_catalogo()

    temas = obter_temas_repetitivos(
        catalogo
    )

    print(
        "Temas repetitivos encontrados: "
        f"{len(temas)}"
    )

    grupos = auditar(
        temas
    )

    print()
    print(
        "RESUMO DA AUDITORIA"
    )
    print(
        "=" * 60
    )

    print(
        "Confirmados: "
        f"{len(grupos['confirmados'])}"
    )

    print(
        "Pendentes / afetados: "
        f"{len(grupos['pendentes'])}"
    )

    print(
        "Divergências: "
        f"{len(grupos['divergencias'])}"
    )

    print(
        "Cancelados: "
        f"{len(grupos['cancelados'])}"
    )

    print(
        "Superados: "
        f"{len(grupos['superados'])}"
    )

    print(
        "Inconclusivos: "
        f"{len(grupos['inconclusivos'])}"
    )

    print(
        "Não classificados: "
        f"{len(grupos['nao_classificados'])}"
    )

    print()
    print(
        "=" * 60
    )

    imprimir_lista(
        "DIVERGÊNCIAS",
        grupos[
            "divergencias"
        ],
    )

    print()

    imprimir_lista(
        "INCONCLUSIVOS",
        grupos[
            "inconclusivos"
        ],
    )

    print()

    imprimir_lista(
        "CANCELADOS",
        grupos[
            "cancelados"
        ],
    )

    print()

    imprimir_lista(
        "PENDENTES",
        grupos[
            "pendentes"
        ],
    )

    relatorio_txt = (
        gerar_relatorio_txt(
            grupos,
            len(temas),
        )
    )

    relatorio_json = (
        gerar_relatorio_json(
            grupos,
            len(temas),
        )
    )

    print()
    print(
        "=" * 60
    )

    print(
        "AUDITORIA FINALIZADA"
    )

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
        "Nenhuma alteração foi feita "
        "no catálogo."
    )


if __name__ == "__main__":
    main()